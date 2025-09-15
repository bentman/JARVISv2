import logging
import sqlite3
import os
import redis
import psutil
from fastapi import FastAPI, Request, HTTPException, Body
from pydantic import BaseModel
from typing import List, Dict, Any

from .docker_utils import get_local_models, pull_model, run_model

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("backend")
# Add file handler for logs persistent in the volume
file_handler = logging.FileHandler('data/logs/app.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# --- Database & Cache Setup ---
DB_PATH = os.getenv("DB_PATH", "data/memory.sqlite")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
try:
    r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
    r.ping()
    logger.info("Successfully connected to Redis.")
except redis.exceptions.ConnectionError as e:
    logger.error(f"Could not connect to Redis: {e}")
    r = None

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            text_content TEXT,
            metadata TEXT
        );
    """)
    conn.commit()
    conn.close()
    logger.info("SQLite database initialized successfully.")

# --- Pydantic Models for API Requests ---
class ChatRequest(BaseModel):
    query: str
    user_id: str
    profile: str
    context: str = ""

class MemoryRequest(BaseModel):
    query: str
    user_id: str
    metadata: str = ""

class SearchRequest(BaseModel):
    query: str

class ModelPullRequest(BaseModel):
    model_ref: str

# --- Core API Endpoints ---
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    os.makedirs('data/logs', exist_ok=True)
    init_db()

@app.post("/chat")
async def chat(request: ChatRequest):
    """Routes the chat query to the appropriate local model."""
    logger.info(f"Chat request from user {request.user_id} on profile {request.profile}")
    
    # Simple LangChain-style routing logic (stub)
    model_choice = "default-chat-model"
    query_lower = request.query.lower()

    if "code" in query_lower or "script" in query_lower:
        model_choice = "code-model"
    elif "reasoning" in query_lower or "explain" in query_lower:
        model_choice = "reasoning-model"
    
    # In a real implementation, this would map to a specific DMR model reference
    mock_response = f"Your query was routed to the '{model_choice}' model. Response: {request.query.upper()}"
    
    # The actual DMR execution would happen here
    # response = run_model(model_ref, request.query)

    return {"response": mock_response, "routed_to": model_choice}

@app.post("/memory")
async def memory(request: MemoryRequest):
    """Stores a memory snippet and updates the Redis cache."""
    conn = get_db_connection()
    conn.execute("INSERT INTO memory (text_content, metadata) VALUES (?, ?)", (request.query, request.metadata))
    conn.commit()
    conn.close()
    
    if r:
        r.rpush(f"memory_list:{request.user_id}", request.query)

    logger.info("Memory snippet stored.")
    return {"status": "success", "message": "Memory snippet stored."}

@app.post("/search")
async def search(request: SearchRequest):
    """Performs a local search on the memory database."""
    logger.info(f"Received search request for query: {request.query}")
    # Placeholder for search logic
    return {"results": []}

# --- Model Management Endpoints ---

@app.get("/models/profiles")
async def get_model_profiles() -> Dict[str, Any]:
    """
    Returns a list of models available locally via DMR, grouped by profile.
    This replaces manual hardware detection on the backend.
    """
    try:
        local_models = get_local_models()
        profiles = {
            "light": [],
            "medium": [],
            "heavy": [],
            "npu": []
        }
        
        # In a real implementation, you'd have a mapping from DMR model to profile
        # For this MVP, we will use a mock classification based on name
        for model in local_models:
            if 'phi' in model['Name'].lower():
                profiles['light'].append(model)
            elif 'mistral' in model['Name'].lower() or 'qwen' in model['Name'].lower():
                profiles['medium'].append(model)
            elif 'llama' in model['Name'].lower():
                profiles['heavy'].append(model)
        
        return {"profiles": profiles, "local_models": local_models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/models/pull")
async def pull_new_model(request: ModelPullRequest):
    """Triggers a model pull via DMR, requiring a user-provided consent token."""
    logger.info(f"Model pull request received for: {request.model_ref}")
    try:
        pull_model(request.model_ref)
        return {"status": "success", "message": f"Model {request.model_ref} pulled successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Health Check ---
@app.get("/health")
async def health_check():
    try:
        if r: r.ping()
        conn = get_db_connection()
        conn.close()
        # Verify Docker connectivity
        subprocess.run(['docker', 'model', 'ls'], check=True, capture_output=True)
        return {"status": "ok", "db": "ok", "cache": "ok", "docker": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")
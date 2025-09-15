from fastapi import FastAPI, Request
import sqlite3
import os
import requests
from pydantic import BaseModel

app = FastAPI()

ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

db = sqlite3.connect('memory.db', check_same_thread=False)
cursor = db.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS conversations 
                  (conv_id INTEGER, user_text TEXT, assistant_text TEXT)''')
db.commit()

models = {
    "light": {
        "chat": "phi3:mini",
        "reasoning": "phi3:mini",
        "coding": "deepseek-coder:1.3b"
    },
    "medium": {
        "chat": "mistral:7b",
        "reasoning": "qwen2:7b",
        "coding": "deepseek-coder:6.7b"
    },
    "heavy": {
        "chat": "llama3.1:8b",
        "reasoning": "deepseek-v2:16b",
        "coding": "codellama:34b"
    },
    "npu": {
        "chat": "phi3:mini",
        "reasoning": "phi3:mini",
        "coding": "deepseek-coder:1.3b"
    }
}

current_tier = "medium"  # default

class TierModel(BaseModel):
    tier: str

class ChatModel(BaseModel):
    query: str
    conv_id: int = 0

class SearchModel(BaseModel):
    query: str

@app.post("/set_tier")
def set_tier(item: TierModel):
    global current_tier
    current_tier = item.tier
    # Pull models if not present
    for model_type in models[current_tier].values():
        requests.post(f"{ollama_host}/api/pull", json={"name": model_type})
    return {"status": "ok", "tier": current_tier}

@app.post("/chat")
async def chat(item: ChatModel):
    query = item.query
    conv_id = item.conv_id
    # Get history
    cursor.execute("SELECT user_text, assistant_text FROM conversations WHERE conv_id=?", (conv_id,))
    history = cursor.fetchall()
    prompt = ""
    for u, a in history:
        prompt += f"User: {u}\nAssistant: {a}\n"
    prompt += f"User: {query}\nAssistant:"
    # Classify query type
    query_lower = query.lower()
    if any(word in query_lower for word in ["code", "program", "script", "python", "java", "function"]):
        model_type = "coding"
    elif any(word in query_lower for word in ["reason", "think", "step by step", "analyze", "solve"]):
        model_type = "reasoning"
    else:
        model_type = "chat"
    model = models.get(current_tier, models["medium"])[model_type]
    # Call ollama
    response = requests.post(f"{ollama_host}/api/generate", json={"model": model, "prompt": prompt, "stream": False})
    if response.status_code != 200:
        return {"error": "Failed to generate response"}
    resp_json = response.json()
    resp_text = resp_json.get("response", "")
    # Save to memory
    cursor.execute("INSERT INTO conversations (conv_id, user_text, assistant_text) VALUES (?, ?, ?)",
                   (conv_id, query, resp_text))
    db.commit()
    return {"response": resp_text}

@app.get("/memory/{conv_id}")
def get_memory(conv_id: int):
    cursor.execute("SELECT user_text, assistant_text FROM conversations WHERE conv_id=?", (conv_id,))
    history = cursor.fetchall()
    return {"history": [{"user": u, "assistant": a} for u, a in history]}

@app.post("/search")
def search(item: SearchModel):
    # Stub for local search expansion
    return {"results": ["Stub local search result for query: " + item.query]}
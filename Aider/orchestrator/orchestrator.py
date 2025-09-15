# orchestrator/orchestrator.py
import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from starlette.responses import StreamingResponse

# Single model endpoint
QWENCODE_ENDPOINT = os.getenv("QWENCODE_ENDPOINT", "http://qwencode:11434")

# Ensure logs directory exists
os.makedirs("/app/logs", exist_ok=True)

logging.basicConfig(
    filename="/app/logs/orchestrator.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

app = FastAPI(title="Agentic Coding Orchestrator")

class GenerateRequest(BaseModel):
    model: str = "qwen2.5-coder:7b"
    prompt: str
    max_tokens: int = 2048
    temperature: float = 0.7

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_endpoint": QWENCODE_ENDPOINT}

@app.post("/generate")
async def generate(req: GenerateRequest):
    logging.info(f"Generate request for model: {req.model}")
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            payload = {
                "model": req.model,
                "prompt": req.prompt,
                "options": {
                    "num_predict": req.max_tokens,
                    "temperature": req.temperature
                },
                "stream": False
            }
            
            resp = await client.post(
                f"{QWENCODE_ENDPOINT}/api/generate",
                json=payload
            )
            resp.raise_for_status()
            
            result = resp.json()
            logging.info(f"Generation completed successfully")
            return result
            
    except httpx.HTTPError as e:
        logging.error(f"Error generating response: {e}")
        raise HTTPException(status_code=502, detail=f"Model service error: {str(e)}")

@app.post("/chat")
async def chat(req: GenerateRequest):
    """OpenAI-compatible chat endpoint"""
    logging.info(f"Chat request for model: {req.model}")
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            payload = {
                "model": req.model,
                "messages": [{"role": "user", "content": req.prompt}],
                "options": {
                    "num_predict": req.max_tokens,
                    "temperature": req.temperature
                }
            }
            
            resp = await client.post(
                f"{QWENCODE_ENDPOINT}/api/chat",
                json=payload
            )
            resp.raise_for_status()
            
            result = resp.json()
            logging.info(f"Chat completed successfully")
            return result
            
    except httpx.HTTPError as e:
        logging.error(f"Error in chat: {e}")
        raise HTTPException(status_code=502, detail=f"Model service error: {str(e)}")
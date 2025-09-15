
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import logging
from datetime import datetime

app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"backend_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

conn = sqlite3.connect("memory.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS memory (id INTEGER PRIMARY KEY AUTOINCREMENT, snippet TEXT)''')
conn.commit()

class ChatRequest(BaseModel):
    input_text: str
    profile: str
    response_text: str

class MemoryRequest(BaseModel):
    snippet: str

class MemoryResponse(BaseModel):
    snippets: list[str]

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        logging.info(f"Chat request: {request.input_text} on profile {request.profile}")
        cursor.execute("INSERT INTO memory (snippet) VALUES (?)", (request.response_text[:100],))
        conn.commit()
        return {"response": request.response_text, "profile": request.profile}
    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Backend error: {str(e)}")

@app.post("/memory")
async def add_memory(request: MemoryRequest):
    try:
        cursor.execute("INSERT INTO memory (snippet) VALUES (?)", (request.snippet,))
        conn.commit()
        logging.info("Memory snippet added")
        return {"status": "added"}
    except Exception as e:
        logging.error(f"Memory add error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory")
async def get_memory():
    try:
        cursor.execute("SELECT snippet FROM memory ORDER BY id DESC LIMIT 10")
        snippets = [row[0] for row in cursor.fetchall()]
        logging.info("Memory retrieved")
        return MemoryResponse(snippets=snippets)
    except Exception as e:
        logging.error(f"Memory get error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/memory")
async def clear_memory():
    try:
        cursor.execute("DELETE FROM memory")
        conn.commit()
        logging.info("Memory cleared")
        return {"status": "cleared"}
    except Exception as e:
        logging.error(f"Memory clear error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
async def search(query: str):
    logging.info(f"Search stub for query: {query}")
    return {"results": f"Local search stub: no results for '{query}'"}

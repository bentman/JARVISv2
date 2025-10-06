from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

from app.services.memory_service import memory_service

router = APIRouter()


class SearchRequest(BaseModel):
    query: str


class SearchResult(BaseModel):
    id: str
    role: str
    content: str
    timestamp: str
    tokens: int | None = None
    mode: str | None = None


@router.post("/semantic", response_model=List[SearchResult])
async def semantic_search(req: SearchRequest):
    results = memory_service.semantic_search(req.query)
    return [
        SearchResult(
            id=m.id,
            role=m.role,
            content=m.content,
            timestamp=m.timestamp.isoformat(),
            tokens=m.tokens,
            mode=m.mode,
        )
        for m in results
    ]

from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Literal, Dict

from app.services.memory_service import memory_service
from app.services.unified_search_service import unified_search_service
from app.core.config import settings

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

class UnifiedSearchRequest(BaseModel):
    query: str
    include_local: bool = True
    include_web: bool = False
    web_sources: Optional[List[str]] = None
    max_results: Optional[int] = None
    escalate_llm: bool = False

@router.post("/unified")
async def unified(req: UnifiedSearchRequest) -> Dict:
    # If web requested but disabled/misconfigured, fail explicitly
    if req.include_web:
        if not settings.SEARCH_ENABLED:
            raise HTTPException(status_code=503, detail={"error": "Web search disabled"})
        # Must have at least one configured provider
        if not unified_search_service.providers:
            raise HTTPException(status_code=503, detail={"error": "No web providers configured"})
    # Temporarily toggle LLM escalation on the service by checking settings; escalation will run only if both enabled and allowed
    # (We do not modify settings here; the service reads config values directly.)
    result = unified_search_service.unified_search(
        req.query,
        include_local=req.include_local,
        include_web=req.include_web,
        max_results=req.max_results,
        web_sources=req.web_sources,
        escalate_llm=req.escalate_llm,
    )
    # If client asked for escalation but it did not run (used.llm is false), return as-is; gating handled inside service
    return result

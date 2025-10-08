from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter

from app.services.budget_service import budget_service

router = APIRouter()


class BudgetStatus(BaseModel):
    daily_cost_usd: float
    daily_limit_usd: float
    monthly_cost_usd: float
    monthly_limit_usd: float
    enforce: bool
    cost_per_token_local_usd: float
    cost_per_token_remote_llm_usd: float


class BudgetConfigRequest(BaseModel):
    daily_limit_usd: Optional[float] = None
    monthly_limit_usd: Optional[float] = None
    enforce: Optional[bool] = None
    cost_per_token_usd: Optional[float] = None


@router.get("/status", response_model=BudgetStatus)
async def get_status():
    totals = budget_service.totals()
    cfg = budget_service.get_config()
    # Effective remote LLM rate comes from settings fallback to local
    try:
        from app.core.config import settings
        remote_rate = getattr(settings, "BUDGET_LLM_WEB_COST_PER_TOKEN_USD", 0.0) or cfg["cost_per_token_usd"]
    except Exception:
        remote_rate = cfg["cost_per_token_usd"]
    return BudgetStatus(
        daily_cost_usd=totals["daily"]["cost_usd"],
        daily_limit_usd=totals["daily"]["limit_usd"],
        monthly_cost_usd=totals["monthly"]["cost_usd"],
        monthly_limit_usd=totals["monthly"]["limit_usd"],
        enforce=totals["enforce"],
        cost_per_token_local_usd=cfg["cost_per_token_usd"],
        cost_per_token_remote_llm_usd=remote_rate,
    )


@router.post("/config")
async def set_config(req: BudgetConfigRequest):
    cfg = budget_service.set_config(
        daily_limit_usd=req.daily_limit_usd,
        monthly_limit_usd=req.monthly_limit_usd,
        enforce=req.enforce,
        cost_per_token_usd=req.cost_per_token_usd,
    )
    return cfg

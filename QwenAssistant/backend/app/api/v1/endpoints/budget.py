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


class BudgetConfigRequest(BaseModel):
    daily_limit_usd: Optional[float] = None
    monthly_limit_usd: Optional[float] = None
    enforce: Optional[bool] = None
    cost_per_token_usd: Optional[float] = None


@router.get("/status", response_model=BudgetStatus)
async def get_status():
    totals = budget_service.totals()
    return BudgetStatus(
        daily_cost_usd=totals["daily"]["cost_usd"],
        daily_limit_usd=totals["daily"]["limit_usd"],
        monthly_cost_usd=totals["monthly"]["cost_usd"],
        monthly_limit_usd=totals["monthly"]["limit_usd"],
        enforce=totals["enforce"],
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

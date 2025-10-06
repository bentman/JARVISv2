from __future__ import annotations
from typing import Optional, Dict
from datetime import datetime, timedelta

from sqlmodel import SQLModel, Field, Session, select

from app.core.config import settings
from app.models.database import db


class BudgetEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    category: str
    tokens_used: int = 0
    execution_time_sec: float = 0.0
    cost_usd: float = 0.0


class BudgetConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=1, primary_key=True)
    daily_limit_usd: float = Field(default=settings.BUDGET_DAILY_LIMIT_USD)
    monthly_limit_usd: float = Field(default=settings.BUDGET_MONTHLY_LIMIT_USD)
    enforce: bool = Field(default=settings.BUDGET_ENFORCE)
    cost_per_token_usd: float = Field(default=settings.COST_PER_TOKEN_USD)


class BudgetService:
    def __init__(self):
        # Ensure tables exist
        SQLModel.metadata.create_all(db.engine)
        # Ensure a single config row exists
        with Session(db.engine) as session:
            cfg = session.get(BudgetConfig, 1)
            if not cfg:
                cfg = BudgetConfig()
                session.add(cfg)
                session.commit()

    def log_event(self, category: str, tokens_used: int, execution_time_sec: float) -> Dict:
        cost_usd = tokens_used * self.get_config()["cost_per_token_usd"]
        event = BudgetEvent(
            category=category,
            tokens_used=tokens_used,
            execution_time_sec=execution_time_sec,
            cost_usd=cost_usd,
        )
        with Session(db.engine) as session:
            session.add(event)
            session.commit()
        return {
            "tokens_used": tokens_used,
            "execution_time_sec": execution_time_sec,
            "cost_usd": cost_usd,
        }

    def get_config(self) -> Dict:
        with Session(db.engine) as session:
            cfg = session.get(BudgetConfig, 1)
            return {
                "daily_limit_usd": cfg.daily_limit_usd,
                "monthly_limit_usd": cfg.monthly_limit_usd,
                "enforce": cfg.enforce,
                "cost_per_token_usd": cfg.cost_per_token_usd,
            }

    def set_config(self, daily_limit_usd: Optional[float] = None, monthly_limit_usd: Optional[float] = None,
                   enforce: Optional[bool] = None, cost_per_token_usd: Optional[float] = None) -> Dict:
        with Session(db.engine) as session:
            cfg = session.get(BudgetConfig, 1)
            if daily_limit_usd is not None:
                cfg.daily_limit_usd = daily_limit_usd
            if monthly_limit_usd is not None:
                cfg.monthly_limit_usd = monthly_limit_usd
            if enforce is not None:
                cfg.enforce = enforce
            if cost_per_token_usd is not None:
                cfg.cost_per_token_usd = cost_per_token_usd
            session.add(cfg)
            session.commit()
        return self.get_config()

    def totals(self) -> Dict:
        now = datetime.utcnow()
        day_start = now - timedelta(days=1)
        month_start = now - timedelta(days=30)
        with Session(db.engine) as session:
            # Daily totals
            stmt_day = select(BudgetEvent).where(BudgetEvent.timestamp >= day_start)
            day_events = session.exec(stmt_day).all()
            day_cost = sum(e.cost_usd for e in day_events)
            day_tokens = sum(e.tokens_used for e in day_events)
            # Monthly totals
            stmt_month = select(BudgetEvent).where(BudgetEvent.timestamp >= month_start)
            month_events = session.exec(stmt_month).all()
            month_cost = sum(e.cost_usd for e in month_events)
            month_tokens = sum(e.tokens_used for e in month_events)
        cfg = self.get_config()
        return {
            "daily": {"cost_usd": day_cost, "tokens": day_tokens, "limit_usd": cfg["daily_limit_usd"]},
            "monthly": {"cost_usd": month_cost, "tokens": month_tokens, "limit_usd": cfg["monthly_limit_usd"]},
            "enforce": cfg["enforce"],
        }

    def within_limits(self) -> bool:
        totals = self.totals()
        daily_ok = (totals["daily"]["limit_usd"] == 0.0) or (totals["daily"]["cost_usd"] <= totals["daily"]["limit_usd"])
        monthly_ok = (totals["monthly"]["limit_usd"] == 0.0) or (totals["monthly"]["cost_usd"] <= totals["monthly"]["limit_usd"])
        return daily_ok and monthly_ok


budget_service = BudgetService()

from __future__ import annotations
from typing import Dict, List
from fastapi import APIRouter, Query

from app.services.model_router import ModelRouter

router = APIRouter()

# Local model router instance
_model_router = ModelRouter()


@router.get("/all")
async def list_models() -> Dict:
    """
    List discovered GGUF models, profile mappings, and name->path map.
    """
    names = _model_router.get_available_models()
    return {
        "names": names,
        "profiles": _model_router.models,
        "paths": getattr(_model_router, "model_paths", {}),
    }


@router.get("/select")
async def select_model(profile: str = Query("medium"), task_type: str = Query("chat")) -> Dict:
    """
    Show active model selection for a given profile and task_type, including resolved path.
    """
    name = _model_router.select_model(profile, task_type)
    path = _model_router.get_model_path(name)
    return {
        "profile": profile,
        "task_type": task_type,
        "model_name": name,
        "model_path": path,
    }
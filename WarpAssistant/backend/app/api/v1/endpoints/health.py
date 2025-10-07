from __future__ import annotations
from fastapi import APIRouter
from app.services.budget_service import budget_service
from app.services.memory_service import memory_service
from app.services.model_router import ModelRouter
from app.services.cache_service import cache_service
from app.models.database import db
import os

router = APIRouter()

@router.get("/services")
async def health_services():
    status = {
        "database": "ok",
        "redis": "ok" if cache_service.healthy() else "error",
        "models_count": 0,
        "voice": {
            "whisper_exec": False,
            "piper_exec": False,
            "piper_voice": False,
        },
    }
    # DB check
    try:
        # simple query: list conversations
        _ = db.get_conversations()
    except Exception:
        status["database"] = "error"

    # Models
    mr = ModelRouter()
    names = mr.get_available_models()
    status["models_count"] = len(names)

    # Voice executables presence (best-effort PATH + common paths)
    import shutil
    whisper_candidates = [
        "whisper", "/usr/local/bin/whisper", "/usr/bin/whisper", "./whisper.cpp/whisper"
    ]
    piper_candidates = [
        "piper", "/usr/local/bin/piper", "/usr/bin/piper", "./piper/build/piper"
    ]
    status["voice"]["whisper_exec"] = any(shutil.which(p) or os.path.exists(p) for p in whisper_candidates)
    status["voice"]["piper_exec"] = any(shutil.which(p) or os.path.exists(p) for p in piper_candidates)
    # Piper voice model existence
    try:
        from app.services.voice_service import VoiceService
        vs = VoiceService()
        # attempt to locate voice model lazily
        voice = vs._find_piper_voice()
        status["voice"]["piper_voice"] = bool(voice)
    except Exception:
        status["voice"]["piper_voice"] = False

    return status

@router.get("/models")
async def health_models():
    mr = ModelRouter()
    result = []
    import os
    for name, path in getattr(mr, "model_paths", {}).items():
        result.append({
            "name": name,
            "path": path,
            "exists": os.path.exists(path),
            "hash": getattr(mr, "model_hashes", {}).get(name)
        })
    return {"models": result}
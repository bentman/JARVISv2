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
            "wake_word_loaded": False,
            "tts_available": False,
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
    # Piper voice model existence, wake word availability, and generic TTS availability (piper or espeak-ng)
    try:
        from app.services.voice_service import VoiceService
        import shutil as _sh
        vs = VoiceService()
        # attempt to locate voice model lazily
        voice = vs._find_piper_voice()
        status["voice"]["piper_voice"] = bool(voice)
        # wake word loaded if model constructed successfully
        status["voice"]["wake_word_loaded"] = vs.wake_word_model is not None
        # tts_available if Piper or espeak-ng present
        status["voice"]["tts_available"] = status["voice"]["piper_exec"] or bool(_sh.which("espeak-ng") or _sh.which("espeak"))
    except Exception:
        status["voice"]["piper_voice"] = False
        status["voice"]["wake_word_loaded"] = False
        status["voice"]["tts_available"] = bool(shutil.which("espeak-ng") or shutil.which("espeak"))

    return status

@router.get("/models")
async def health_models():
    mr = ModelRouter()
    result = []
    import os, hashlib
    for name, path in getattr(mr, "model_paths", {}).items():
        exists = os.path.exists(path)
        size_bytes = os.path.getsize(path) if exists else 0
        recorded_hash = getattr(mr, "model_hashes", {}).get(name)
        # Recompute quickly to detect changes since startup
        current_hash = None
        if exists:
            try:
                h = hashlib.sha256()
                with open(path, 'rb') as f:
                    for chunk in iter(lambda: f.read(1024 * 1024), b''):
                        h.update(chunk)
                current_hash = h.hexdigest()
            except Exception:
                current_hash = None
        result.append({
            "name": name,
            "path": path,
            "exists": exists,
            "size_bytes": size_bytes,
            "hash_recorded": recorded_hash,
            "hash_current": current_hash,
            "integrity_ok": bool(exists and recorded_hash and current_hash and recorded_hash == current_hash and size_bytes > 0),
        })
    return {"models": result}

from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.services.budget_service import budget_service
from app.services.memory_service import memory_service
from app.services.model_router import ModelRouter
from app.services.cache_service import cache_service
from app.models.database import db
import os
import psutil
import time
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

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

# Kubernetes-style readiness probe
@router.get("/ready")
async def readiness_probe():
    """Readiness probe - checks if the service can handle requests"""
    checks = {
        "database": False,
        "redis": False,
        "models": False
    }
    
    try:
        # Database connectivity
        _ = db.get_conversations()
        checks["database"] = True
    except Exception as e:
        logger.error(f"Database readiness check failed: {e}")
    
    try:
        # Redis connectivity
        checks["redis"] = cache_service.healthy()
    except Exception as e:
        logger.error(f"Redis readiness check failed: {e}")
    
    try:
        # At least one model available
        mr = ModelRouter()
        models = mr.get_available_models()
        checks["models"] = len(models) > 0
    except Exception as e:
        logger.error(f"Models readiness check failed: {e}")
    
    all_ready = all(checks.values())
    
    if not all_ready:
        raise HTTPException(status_code=503, detail={
            "ready": False,
            "checks": checks,
            "message": "Service not ready"
        })
    
    return {
        "ready": True,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

# Kubernetes-style liveness probe  
@router.get("/live")
async def liveness_probe():
    """Liveness probe - checks if the service is alive and should not be restarted"""
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime_seconds": time.time() - psutil.Process().create_time()
    }

# Monitoring metrics endpoint
@router.get("/metrics")
async def metrics():
    """Basic metrics for monitoring"""
    try:
        process = psutil.Process()
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')
        
        # Process metrics
        proc_memory = process.memory_info()
        proc_cpu = process.cpu_percent()
        
        # Service-specific metrics
        redis_status = cache_service.healthy() if cache_service else False
        
        try:
            mr = ModelRouter()
            model_count = len(mr.get_available_models())
        except Exception:
            model_count = 0
            
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "system": {
                "cpu_percent": cpu_percent,
                "memory_total_bytes": memory_info.total,
                "memory_used_bytes": memory_info.used,
                "memory_percent": memory_info.percent,
                "disk_total_bytes": disk_info.total,
                "disk_used_bytes": disk_info.used,
                "disk_percent": (disk_info.used / disk_info.total) * 100
            },
            "process": {
                "memory_rss_bytes": proc_memory.rss,
                "memory_vms_bytes": proc_memory.vms,
                "cpu_percent": proc_cpu,
                "uptime_seconds": time.time() - process.create_time(),
                "pid": process.pid
            },
            "services": {
                "redis_healthy": redis_status,
                "models_count": model_count
            }
        }
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        raise HTTPException(status_code=500, detail="Metrics collection failed")

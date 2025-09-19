from fastapi import APIRouter, Depends, HTTPException
from app.api.v1.endpoints import chat, hardware, memory, voice, privacy

router = APIRouter()

router.include_router(chat.router, prefix="/chat", tags=["chat"])
router.include_router(hardware.router, prefix="/hardware", tags=["hardware"])
router.include_router(memory.router, prefix="/memory", tags=["memory"])
router.include_router(voice.router, prefix="/voice", tags=["voice"])
router.include_router(privacy.router, prefix="/privacy", tags=["privacy"])
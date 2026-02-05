from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from typing import Optional
import base64
from app.services.voice_service import voice_service
from app.services.model_router import ModelRouter
from app.services.hardware_detector import HardwareDetector
from app.services.memory_service import memory_service
from app.services.budget_service import budget_service
from app.services.privacy_service import privacy_service
from app.services.unified_search_service import unified_search_service
from app.core.config import settings

router = APIRouter()

# Initialize shared services
_model_router = ModelRouter()
_hardware_detector = HardwareDetector()

class VoiceRequest(BaseModel):
    audio_data: str  # Base64 encoded audio data

class VoiceResponse(BaseModel):
    text: str
    confidence: float

@router.post("/stt", response_model=VoiceResponse)
async def speech_to_text(request: VoiceRequest):
    """
    Convert speech to text using Whisper
    """
    from fastapi import HTTPException
    # Decode base64 audio data
    try:
        audio_bytes = base64.b64decode(request.audio_data)
    except Exception:
        raise HTTPException(status_code=400, detail={"error": "Invalid base64 audio data"})
    
    try:
        text, confidence = voice_service.speech_to_text(audio_bytes)
        return VoiceResponse(text=text, confidence=confidence)
    except Exception as e:
        raise HTTPException(status_code=503, detail={"error": str(e)})

@router.post("/tts")
async def text_to_speech(text: str):
    """
    Convert text to speech using Piper
    """
    from fastapi import HTTPException
    try:
        audio_bytes = voice_service.text_to_speech(text)
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        return {"audio_data": audio_base64}
    except Exception as e:
        raise HTTPException(status_code=503, detail={"error": str(e)})

@router.post("/wake-word")
async def detect_wake_word(request: VoiceRequest):
    """
    Detect wake word in audio stream
    """
    try:
        # Decode base64 audio data
        audio_bytes = base64.b64decode(request.audio_data)
        
        # Check for wake word using the voice service
        detected = voice_service.detect_wake_word(audio_bytes)
        
        return {"detected": detected}
    except Exception as e:
        return {"error": "Error detecting wake word", "detected": False}

# Also add an endpoint to handle file uploads for audio
@router.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    """
    Upload an audio file for processing
    """
    try:
        audio_data = await file.read()
        
        # Convert speech to text
        text, confidence = voice_service.speech_to_text(audio_data)
        
        return {
            "text": text,
            "confidence": confidence,
            "filename": file.filename
        }
    except Exception as e:
        return {"error": f"Error processing audio file: {str(e)}"}

class VoiceSessionRequest(BaseModel):
    audio_data: str  # Base64 WAV
    conversation_id: Optional[str] = None
    mode: str = "chat"
    include_web: bool = False
    escalate_llm: bool = False

@router.post("/session")
async def voice_session(body: VoiceSessionRequest):
    """
    One-shot voice session:
    - Detect wake word (best-effort). If not detected, return detected=false.
    - If detected, transcribe (STT), run chat with retrieval (and optional web), synthesize TTS.
    - Returns transcript, response_text, and audio_data (base64 WAV), and detected flag.
    """
    from fastapi import HTTPException
    try:
        audio_bytes = base64.b64decode(body.audio_data)
    except Exception:
        raise HTTPException(status_code=400, detail={"error": "Invalid base64 audio data"})

    # Wake word detection (non-fatal; proceed if detected True, else early return)
    try:
        detected = voice_service.detect_wake_word(audio_bytes)
    except Exception:
        detected = False
    if not detected:
        return {"detected": False}

    # Budget gate
    cfg = budget_service.get_config()
    if cfg.get("enforce") and not budget_service.within_limits():
        totals = budget_service.totals()
        raise HTTPException(status_code=429, detail={
            "error": "Budget limit exceeded",
            "daily": totals.get("daily"),
            "monthly": totals.get("monthly"),
        })

    # STT
    try:
        transcript, _conf = voice_service.speech_to_text(audio_bytes)
    except Exception as e:
        raise HTTPException(status_code=503, detail={"error": f"STT failed: {str(e)}"})

    # Conversation handling
    conv_id = body.conversation_id
    conversation = memory_service.get_conversation(conv_id) if conv_id else None
    if not conversation:
        title = (transcript or "Conversation").strip()[:50] or "Conversation"
        conversation = memory_service.store_conversation(title)
        conv_id = conversation.id

    # Privacy scrub user text for persistence and prompts
    try:
        priv_cfg = privacy_service.get_settings()
        user_text = privacy_service.scrub_text(transcript) if priv_cfg.get("redact_aggressiveness") in ("standard", "strict") else transcript
    except Exception:
        user_text = transcript

    # Persist user message
    memory_service.add_message(conversation_id=conv_id, role="user", content=user_text, tokens=None, mode=body.mode)

    # Retrieval context (memory + optional web)
    context_block = ""
    try:
        if getattr(settings, "RETRIEVAL_ENABLED", True):
            k = max(0, int(getattr(settings, "RETRIEVAL_TOP_K", 3)))
            ctxs: list[str] = []
            # Memory
            hits = memory_service.semantic_search(user_text)
            for i, m in enumerate(hits[:k], start=1):
                try:
                    priv_cfg = privacy_service.get_settings()
                    c = privacy_service.scrub_text(m.content) if priv_cfg.get("redact_aggressiveness") in ("standard", "strict") else m.content
                except Exception:
                    c = m.content
                ctxs.append(f"[mem {i}] {c}")
            # Web
            if body.include_web and settings.SEARCH_ENABLED:
                try:
                    us = unified_search_service.unified_search(
                        query=user_text,
                        include_local=False,
                        include_web=True,
                        max_results=k,
                        escalate_llm=bool(body.escalate_llm),
                    )
                    web_items = [it for it in us.get("items", []) if it.get("source") == "web"]
                    for j, w in enumerate(web_items[:k], start=1):
                        title = (w.get("title") or "").strip()
                        snippet = (w.get("snippet") or "").strip()
                        try:
                            priv_cfg = privacy_service.get_settings()
                            snippet = privacy_service.scrub_text(snippet) if priv_cfg.get("redact_aggressiveness") in ("standard", "strict") else snippet
                        except Exception:
                            pass
                        line = f"[web {j}] {title}: {snippet}" if title else f"[web {j}] {snippet}"
                        ctxs.append(line)
                except Exception:
                    pass
            if ctxs:
                context_block = "Context (retrieved):\n" + "\n\n".join(ctxs)
                max_chars = max(200, int(getattr(settings, "RETRIEVAL_MAX_CHARS", 1800)))
                if len(context_block) > max_chars:
                    context_block = context_block[:max_chars] + "\n..."
    except Exception:
        context_block = ""

    # Prepare prompt
    hardware_profile = _hardware_detector.get_hardware_profile()
    if context_block:
        prompt = f"{context_block}\n\nUser: {user_text}\nAssistant:"
    else:
        prompt = f"User: {user_text}\nAssistant:"

    # Generate response (non-streaming) and persist assistant
    try:
        result = _model_router.generate_response(
            profile=hardware_profile,
            task_type=body.mode,
            prompt=prompt,
            max_tokens=256,
        )
        # Strict scrub before persistence if configured
        try:
            priv_cfg = privacy_service.get_settings()
            assistant_to_store = privacy_service.scrub_text(result.response) if priv_cfg.get("redact_aggressiveness") == "strict" else result.response
        except Exception:
            assistant_to_store = result.response
        memory_service.add_message(conversation_id=conv_id, role="assistant", content=assistant_to_store, tokens=result.tokens_used, mode=body.mode)
        # Log budget
        budget_service.log_event(
            category=f"chat:{body.mode}",
            tokens_used=result.tokens_used or 0,
            execution_time_sec=result.execution_time or 0.0,
        )
        # TTS synthesis of assistant response
        audio_bytes = voice_service.text_to_speech(result.response)
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        return {
            "detected": True,
            "conversation_id": conv_id,
            "transcript": transcript,
            "response_text": result.response,
            "audio_data": audio_base64,
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail={"error": f"Voice session failed: {str(e)}"})

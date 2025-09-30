from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from typing import Optional
import base64
from app.services.voice_service import voice_service

router = APIRouter()

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
    try:
        # Decode base64 audio data
        audio_bytes = base64.b64decode(request.audio_data)
        
        # Convert speech to text using the voice service
        text, confidence = voice_service.speech_to_text(audio_bytes)
        
        return VoiceResponse(
            text=text,
            confidence=confidence
        )
    except Exception as e:
        return VoiceResponse(
            text="Error processing audio",
            confidence=0.0
        )

@router.post("/tts")
async def text_to_speech(text: str):
    """
    Convert text to speech using Piper
    """
    try:
        # Convert text to speech using the voice service
        audio_bytes = voice_service.text_to_speech(text)
        
        # Encode the audio as base64
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        return {"audio_data": audio_base64}
    except Exception as e:
        return {"error": "Error generating speech", "details": str(e)}

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
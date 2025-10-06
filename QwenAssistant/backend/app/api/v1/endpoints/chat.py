from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.services.model_router import ModelRouter
from app.services.hardware_detector import HardwareDetector
from app.services.cache_service import cache_service
from app.services.budget_service import budget_service

router = APIRouter()

# Initialize services
model_router = ModelRouter()
hardware_detector = HardwareDetector()

class Message(BaseModel):
    id: str
    role: str  # \"user\" or \"assistant\"
    content: str
    timestamp: datetime
    tokens: Optional[int] = None
    mode: Optional[str] = \"chat\"  # \"chat\", \"coding\", \"reasoning\"

class Conversation(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[Message] = []

class ChatRequest(BaseModel):
    message: str
    mode: str = \"chat\"
    stream: bool = True

class ChatResponse(BaseModel):
    type: str  # \"text\", \"thinking\", \"response\", \"done\"
    content: str
    tokens_used: Optional[int] = None

@router.post("/send", response_model=List[ChatResponse])
async def send_message(request: ChatRequest):
    """
    Send a message to the AI assistant
    """
    try:
        # Cache check
        cache_key = cache_service.key_for_chat(request.mode, request.message)
        if cache_service.healthy():
            cached = cache_service.get_json(cache_key)
            if cached:
                return [ChatResponse(**item) for item in cached]

        # Get current hardware profile
        hardware_profile = hardware_detector.get_hardware_profile()
        
        # Prepare the prompt - in a real implementation, you'd format this properly
        # with conversation history for context
        prompt = f"User: {request.message}\nAssistant:"
        
        # Generate response using the appropriate model
        result = model_router.generate_response(
            profile=hardware_profile,
            task_type=request.mode,
            prompt=prompt,
            max_tokens=256
        )
        
        response = [
            ChatResponse(type="thinking", content="Processing your request..."),
            ChatResponse(type="response", content=result.response, tokens_used=result.tokens_used),
            ChatResponse(type="done", content="")
        ]
        # Log budget usage (tokens + time)
        budget_service.log_event(
            category=f"chat:{request.mode}",
            tokens_used=result.tokens_used or 0,
            execution_time_sec=result.execution_time or 0.0,
        )
        # Cache set
        if cache_service.healthy():
            cache_service.set_json(cache_key, [r.model_dump() for r in response], ttl_seconds=300)
        return response
    except Exception as e:
        # In case of an error, return an appropriate response
        return [
            ChatResponse(type="thinking", content="Processing your request..."),
            ChatResponse(type="response", content=f"Error processing your request: {str(e)}", tokens_used=0),
            ChatResponse(type="done", content="")
        ]

@router.get(\"/conversations\", response_model=List[Conversation])
async def get_conversations():
    \"\"\"
    Get all conversations
    \"\"\"
    # This is a placeholder implementation
    # In a real implementation, this would interface with the memory service
    return []

@router.get(\"/conversation/{conversation_id}\", response_model=Conversation)
async def get_conversation(conversation_id: str):
    \"\"\"
    Get a specific conversation by ID
    \"\"\"
    # This is a placeholder implementation
    # In a real implementation, this would interface with the memory service
    return Conversation(
        id=conversation_id,
        title=\"Sample Conversation\",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
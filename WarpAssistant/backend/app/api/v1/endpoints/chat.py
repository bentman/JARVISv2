from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.services.model_router import ModelRouter
from app.services.hardware_detector import HardwareDetector
from app.services.cache_service import cache_service
from app.services.budget_service import budget_service
from app.services.memory_service import memory_service

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
    conversation_id: Optional[str] = None
    message: str
    mode: str = "chat"
    stream: bool = True

class ChatResponse(BaseModel):
    type: str  # \"text\", \"thinking\", \"response\", \"done\"
    content: str
    tokens_used: Optional[int] = None

@router.post("/send", response_model=List[ChatResponse])
async def send_message(request: ChatRequest):
    """
    Send a message to the AI assistant.
    Persists conversation and messages using the memory service.
    """
    try:
        # Enforce budget before any compute
        cfg = budget_service.get_config()
        if cfg.get("enforce") and not budget_service.within_limits():
            totals = budget_service.totals()
            raise HTTPException(status_code=429, detail={
                "error": "Budget limit exceeded",
                "daily": totals.get("daily"),
                "monthly": totals.get("monthly"),
                "hint": "Adjust limits via /api/v1/budget/config or try again later"
            })

        # Ensure we have a conversation
        conv_id: Optional[str] = request.conversation_id
        conversation = None
        if conv_id:
            conversation = memory_service.get_conversation(conv_id)
        if not conversation:
            # Create a new conversation with a short title derived from message
            title = (request.message or "Conversation").strip()[:50] or "Conversation"
            conversation = memory_service.store_conversation(title)
            conv_id = conversation.id

        # Persist the user message
        memory_service.add_message(conversation_id=conv_id, role="user", content=request.message, tokens=None, mode=request.mode)

        # Cache check
        cache_key = cache_service.key_for_chat(request.mode, request.message)
        if cache_service.healthy():
            cached = cache_service.get_json(cache_key)
            if cached:
                # Persist assistant response from cache
                try:
                    # Find the main response item
                    main = next((item for item in cached if item.get("type") == "response"), None)
                    if main:
                        memory_service.add_message(conversation_id=conv_id, role="assistant", content=main.get("content", ""), tokens=main.get("tokens_used"), mode=request.mode)
                except Exception:
                    pass
                return [ChatResponse(**item) for item in cached]

        # Get current hardware profile
        hardware_profile = hardware_detector.get_hardware_profile()
        
        # Prepare the prompt - should ideally include context; kept simple for core functionality
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

        # Persist assistant response
        try:
            memory_service.add_message(conversation_id=conv_id, role="assistant", content=result.response, tokens=result.tokens_used, mode=request.mode)
        except Exception:
            pass

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

@router.get("/conversations", response_model=List[Conversation])
async def get_conversations():
    """
    Get all conversations with their messages (unsorted per conversation).
    """
    db_conversations = memory_service.get_conversations()
    results: List[Conversation] = []
    for conv in db_conversations:
        db_messages = memory_service.get_messages(conv.id)
        results.append(
            Conversation(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                messages=[
                    Message(
                        id=m.id,
                        role=m.role,
                        content=m.content,
                        timestamp=m.timestamp,
                        tokens=m.tokens,
                        mode=m.mode,
                    ) for m in db_messages
                ],
            )
        )
    return results

@router.get("/conversation/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    """
    Get a specific conversation by ID
    """
    conv = memory_service.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail={"error": "Conversation not found"})
    db_messages = memory_service.get_messages(conversation_id)
    return Conversation(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=[
            Message(
                id=m.id,
                role=m.role,
                content=m.content,
                timestamp=m.timestamp,
                tokens=m.tokens,
                mode=m.mode,
            ) for m in db_messages
        ],
    )

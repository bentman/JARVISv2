from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.services.model_router import ModelRouter
from app.services.hardware_detector import HardwareDetector
from app.services.cache_service import cache_service
from app.services.budget_service import budget_service
from app.services.memory_service import memory_service
from app.services.privacy_service import privacy_service
from app.services.unified_search_service import unified_search_service
from app.core.config import settings

router = APIRouter()

# Initialize services
model_router = ModelRouter()
hardware_detector = HardwareDetector()

class Message(BaseModel):
    id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    tokens: Optional[int] = None
    mode: Optional[str] = "chat"  # "chat", "coding", "reasoning"

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
    # Optional unified search controls (non-breaking defaults)
    include_web: bool = False
    escalate_llm: bool = False

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

        # Privacy: scrub user input before persisting and using in prompts
        try:
            priv_cfg = privacy_service.get_settings()
            scrubbed_message = privacy_service.scrub_text(request.message) if priv_cfg.get("redact_aggressiveness") in ("standard", "strict") else request.message
        except Exception:
            scrubbed_message = request.message

        # Persist the user message (scrubbed)
        memory_service.add_message(conversation_id=conv_id, role="user", content=scrubbed_message, tokens=None, mode=request.mode)

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
        
        # Retrieval-augmented prompt building
        context_block = ""
        try:
            if getattr(settings, "RETRIEVAL_ENABLED", True):
                k = max(0, int(getattr(settings, "RETRIEVAL_TOP_K", 3)))
                ctxs: list[str] = []

                # Always include local memory retrieval
                hits = memory_service.semantic_search(scrubbed_message)
                top_mem = hits[:k]
                for i, m in enumerate(top_mem, start=1):
                    try:
                        priv_cfg = privacy_service.get_settings()
                        c = privacy_service.scrub_text(m.content) if priv_cfg.get("redact_aggressiveness") in ("standard", "strict") else m.content
                    except Exception:
                        c = m.content
                    ctxs.append(f"[mem {i}] {c}")

                # Optionally include web snippets via unified search (privacy-aware)
                if request.include_web and settings.SEARCH_ENABLED:
                    try:
                        us = unified_search_service.unified_search(
                            query=scrubbed_message,
                            include_local=False,  # already included via memory_service above
                            include_web=True,
                            max_results=k,
                            escalate_llm=bool(request.escalate_llm),
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
        
        # Prepare the prompt with context if available
        if context_block:
            prompt = f"{context_block}\n\nUser: {scrubbed_message}\nAssistant:"
        else:
            prompt = f"User: {scrubbed_message}\nAssistant:"
        
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
            # Scrub assistant output if privacy demands strict redaction before persistence
            try:
                priv_cfg = privacy_service.get_settings()
                assistant_content_to_store = privacy_service.scrub_text(result.response) if priv_cfg.get("redact_aggressiveness") == "strict" else result.response
            except Exception:
                assistant_content_to_store = result.response
            memory_service.add_message(conversation_id=conv_id, role="assistant", content=assistant_content_to_store, tokens=result.tokens_used, mode=request.mode)
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

@router.post("/send/stream")
async def send_message_stream(request: ChatRequest):
    """
    Stream a response to the AI assistant using Server-Sent Events (SSE).
    Includes the same retrieval logic as non-streaming, with optional unified web search
    when include_web is true and privacy allows.
    """
    try:
        # Budget check before starting stream
        cfg = budget_service.get_config()
        if cfg.get("enforce") and not budget_service.within_limits():
            totals = budget_service.totals()
            raise HTTPException(status_code=429, detail={
                "error": "Budget limit exceeded",
                "daily": totals.get("daily"),
                "monthly": totals.get("monthly"),
                "hint": "Adjust limits via /api/v1/budget/config or try again later"
            })
        # Conversation handling
        conv_id: Optional[str] = request.conversation_id
        conversation = None
        if conv_id:
            conversation = memory_service.get_conversation(conv_id)
        if not conversation:
            title = (request.message or "Conversation").strip()[:50] or "Conversation"
            conversation = memory_service.store_conversation(title)
            conv_id = conversation.id
        # Privacy: scrub user message if configured
        try:
            priv_cfg = privacy_service.get_settings()
            user_text = privacy_service.scrub_text(request.message) if priv_cfg.get("redact_aggressiveness") in ("standard", "strict") else request.message
        except Exception:
            user_text = request.message
        # Persist user message (scrubbed)
        memory_service.add_message(conversation_id=conv_id, role="user", content=user_text, tokens=None, mode=request.mode)
        # Prepare retrieval context (memory + optional web)
        context_block = ""
        try:
            if getattr(settings, "RETRIEVAL_ENABLED", True):
                k = max(0, int(getattr(settings, "RETRIEVAL_TOP_K", 3)))
                ctxs: list[str] = []
                # Memory retrieval
                hits = memory_service.semantic_search(user_text)
                for i, m in enumerate(hits[:k], start=1):
                    try:
                        priv_cfg = privacy_service.get_settings()
                        c = privacy_service.scrub_text(m.content) if priv_cfg.get("redact_aggressiveness") in ("standard", "strict") else m.content
                    except Exception:
                        c = m.content
                    ctxs.append(f"[mem {i}] {c}")
                # Web retrieval via unified search (privacy-aware)
                if request.include_web and settings.SEARCH_ENABLED:
                    try:
                        us = unified_search_service.unified_search(
                            query=user_text,
                            include_local=False,
                            include_web=True,
                            max_results=k,
                            escalate_llm=bool(request.escalate_llm),
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
        hardware_profile = hardware_detector.get_hardware_profile()
        if context_block:
            prompt = f"{context_block}\n\nUser: {user_text}\nAssistant:"
        else:
            prompt = f"User: {user_text}\nAssistant:"
        # Generator that yields SSE lines and persists assistant response at end
        def event_stream():
            buf = []
            try:
                for chunk in model_router.generate_response_stream(
                    profile=hardware_profile,
                    task_type=request.mode,
                    prompt=prompt,
                    max_tokens=256,
                ):
                    buf.append(chunk)
                    yield f"data: {chunk}\n\n"
                # Persist assistant response (scrubbed strictly if configured)
                try:
                    full = "".join(buf)
                    try:
                        priv_cfg = privacy_service.get_settings()
                        to_store = privacy_service.scrub_text(full) if priv_cfg.get("redact_aggressiveness") == "strict" else full
                    except Exception:
                        to_store = "".join(buf)
                    memory_service.add_message(conversation_id=conv_id, role="assistant", content=to_store, tokens=None, mode=request.mode)
                except Exception:
                    pass
                # Final done event
                yield "event: done\n\n"
            except Exception as e:
                yield f"event: error\ndata: {str(e)}\n\n"
        return StreamingResponse(event_stream(), media_type="text/event-stream")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})

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

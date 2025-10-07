class TagsUpdateRequest(BaseModel):
    tags: List[str]

@router.post("/conversation/{conversation_id}/tags")
async def set_conversation_tags(conversation_id: str, body: TagsUpdateRequest):
    updated = memory_service.set_conversation_tags(conversation_id, body.tags)
    if not updated:
        raise HTTPException(status_code=404, detail={"error": "Conversation not found"})
    return {"id": updated.id, "tags": body.tags}

@router.post("/message/{message_id}/tags")
async def set_message_tags(message_id: str, body: TagsUpdateRequest):
    updated = memory_service.set_message_tags(message_id, body.tags)
    if not updated:
        raise HTTPException(status_code=404, detail={"error": "Message not found"})
    return {"id": updated.id, "tags": body.tags}

@router.get("/conversations/by-tags", response_model=List[Conversation])
async def get_conversations_by_tags(tags: str = ""):
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    convos = memory_service.filter_conversations_by_tags(tag_list)
    response = []
    for conv in convos:
        db_messages = memory_service.get_messages(conv.id)
        messages = [
            Message(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp,
                tokens=msg.tokens,
                mode=msg.mode
            )
            for msg in db_messages
        ]
        response.append(
            Conversation(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                messages=messages,
                tags=(conv.tags.split(",") if conv.tags else [])
            )
        )
    return response

@router.get("/export")
async def export_memory(format: str = "json"):
    data = memory_service.export_all()
    if format == "jsonl":
        # Return JSON Lines
        import json
        lines = []
        for c in data.get("conversations", []):
            lines.append(json.dumps({"type": "conversation", **c}))
        for m in data.get("messages", []):
            lines.append(json.dumps({"type": "message", **m}))
        return "\n".join(lines)
    return data

class ImportRequest(BaseModel):
    conversations: List[dict] = []
    messages: List[dict] = []
    merge: bool = True

@router.post("/import")
async def import_memory(body: ImportRequest):
    result = memory_service.import_data({
        "conversations": body.conversations,
        "messages": body.messages,
    }, merge=body.merge)
    return result

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
from app.services.memory_service import memory_service
from fastapi import HTTPException
from pydantic import BaseModel

router = APIRouter()

class Message(BaseModel):
    id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    tokens: Optional[int] = None
    mode: Optional[str] = "chat"  # "chat", "coding", "reasoning"

class MemoryItem(BaseModel):
    id: str
    content: str
    created_at: datetime
    tags: List[str] = []
    access_level: str = "private"  # "private", "shared", "public"

class Conversation(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[Message] = []
    tags: List[str] = []

class MemorySearchRequest(BaseModel):
    query: str

class MemorySearchResponse(BaseModel):
    results: List[Message]

class ConversationStats(BaseModel):
    conversation_id: str
    total_messages: int
    total_tokens: int

@router.get("/conversations", response_model=List[Conversation])
async def get_conversations():
    """
    Get all conversations
    """
    db_conversations = memory_service.get_conversations()
    response_conversations = []
    for conv in db_conversations:
        # Get messages for each conversation
        db_messages = memory_service.get_messages(conv.id)
        messages = [
            Message(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp,
                tokens=msg.tokens,
                mode=msg.mode
            )
            for msg in db_messages
        ]
        response_conversations.append(
            Conversation(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                messages=messages,
                tags=(conv.tags.split(",") if conv.tags else [])
            )
        )
    return response_conversations

@router.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """
    Get a specific conversation by ID
    """
    db_conversation = memory_service.get_conversation(conversation_id)
    if not db_conversation:
        return {
            "error": "Conversation not found",
            "id": conversation_id
        }
    
    # Get messages for the conversation
    db_messages = memory_service.get_messages(conversation_id)
    messages = [
        Message(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            timestamp=msg.timestamp,
            tokens=msg.tokens,
            mode=msg.mode
        )
        for msg in db_messages
    ]
    
    return {
        "id": db_conversation.id,
        "title": db_conversation.title,
        "created_at": db_conversation.created_at,
        "updated_at": db_conversation.updated_at,
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "tokens": msg.tokens,
                "mode": msg.mode
            }
            for msg in messages
        ]
    }

@router.post("/save")
async def save_memory(item: MemoryItem):
    """
    Save a memory item
    """
    # This would integrate with full memory system including vector storage
    # For now, we're using conversation storage as a placeholder
    conversation = memory_service.store_conversation(item.content[:50])  # Use first 50 chars as title
    # Add the full content as a message in the conversation
    memory_service.add_message(conversation.id, "memory", item.content)
    return {"status": "saved", "id": conversation.id}

@router.get("/search")
async def search_memory(query: str):
    """
    Search memory items - performs semantic search across stored conversations
    """
    # In a full implementation, this would use vector embeddings
    # For now, it returns an empty list
    results = memory_service.semantic_search(query)
    return {
        "results": [
            {
                "id": result.id,
                "role": result.role,
                "content": result.content,
                "timestamp": result.timestamp,
                "tokens": result.tokens,
                "mode": result.mode
            }
            for result in results
        ],
        "query": query
    }

@router.post("/search", response_model=MemorySearchResponse)
async def search_memory_post(request: MemorySearchRequest):
    """
    Search memory using POST with request body
    """
    results = memory_service.semantic_search(request.query)
    response_results = [
        Message(
            id=result.id,
            role=result.role,
            content=result.content,
            timestamp=result.timestamp,
            tokens=result.tokens,
            mode=result.mode
        )
        for result in results
    ]
    return MemorySearchResponse(results=response_results)

@router.get("/stats/{conversation_id}", response_model=ConversationStats)
async def get_conversation_stats(conversation_id: str):
    """
    Return statistics for a conversation (message count, token sum).
    """
    stats = memory_service.get_conversation_stats(conversation_id)
    return ConversationStats(**stats)

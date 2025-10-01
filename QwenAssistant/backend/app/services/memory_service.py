from app.models.database import db, Conversation as DBConversation, Message as DBMessage
from typing import List, Optional
from datetime import datetime
from app.services.vector_store import vector_store


class MemoryService:
    """
    Service for conversation storage, vector embedding, and semantic search
    """
    
    def __init__(self):
        # Use the global database instance
        self.db = db
    
    def store_conversation(self, title: str) -> DBConversation:
        """
        Create and store a new conversation in memory and persistent storage
        """
        return self.db.create_conversation(title)
    
    def get_conversations(self) -> List[DBConversation]:
        """
        Retrieve all conversations
        """
        return self.db.get_conversations()
    
    def get_conversation(self, conversation_id: str) -> Optional[DBConversation]:
        """
        Retrieve specific conversation
        """
        return self.db.get_conversation(conversation_id)
    
    def add_message(self, conversation_id: str, role: str, content: str, 
                   tokens: Optional[int] = None, mode: str = "chat") -> DBMessage:
        """
        Add a message to a conversation
        """
        msg = self.db.add_message(conversation_id, role, content, tokens, mode)
        # Index message content into vector store for semantic search (best-effort)
        try:
            meta = {
                "message_id": msg.id,
                "conversation_id": msg.conversation_id,
                "role": msg.role,
                "mode": msg.mode,
                "timestamp": msg.timestamp.isoformat()
            }
            vector_store.add_texts([content], [meta])
        except Exception:
            # Fail silently; semantic search remains available for other items
            pass
        return msg
    
    def get_messages(self, conversation_id: str) -> List[DBMessage]:
        """
        Retrieve all messages in a conversation
        """
        return self.db.get_messages(conversation_id)
    
    def semantic_search(self, query: str) -> List[DBMessage]:
        """
        Perform semantic search across memory. Returns matching DB messages.
        """
        try:
            results = vector_store.search(query, k=5)
        except Exception:
            results = []
        matches: List[DBMessage] = []
        for _score, meta in results:
            msg_id = meta.get("message_id") if isinstance(meta, dict) else None
            if not msg_id:
                continue
            db_msg = self.db.get_message(msg_id)
            if db_msg:
                matches.append(db_msg)
        return matches


# Initialize the global memory service instance
memory_service = MemoryService()

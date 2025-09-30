from app.models.database import db, Conversation as DBConversation, Message as DBMessage
from typing import List, Optional
from datetime import datetime
import uuid


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
        return self.db.add_message(conversation_id, role, content, tokens, mode)
    
    def get_messages(self, conversation_id: str) -> List[DBMessage]:
        """
        Retrieve all messages in a conversation
        """
        return self.db.get_messages(conversation_id)
    
    def semantic_search(self, query: str) -> List[DBMessage]:
        """
        Perform semantic search across memory
        """
        # In a full implementation, this would use vector embeddings
        # to find semantically similar messages.
        # For now, we'll return an empty list as a placeholder
        # since we would need to implement vector storage for this.
        return []


# Initialize the global memory service instance
memory_service = MemoryService()
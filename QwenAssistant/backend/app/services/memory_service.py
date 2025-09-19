from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, List
from datetime import datetime
import uuid
from app.core.config import settings

class Conversation(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Message(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    conversation_id: str = Field(foreign_key="conversation.id")
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    tokens: Optional[int] = None
    mode: str = "chat"  # "chat", "coding", "reasoning"

class MemoryDatabase:
    """
    Database interface for conversation memory storage
    """
    
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL, echo=True)
        SQLModel.metadata.create_all(self.engine)
        
    def create_conversation(self, title: str) -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(title=title)
        with Session(self.engine) as session:
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
        return conversation
        
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID"""
        with Session(self.engine) as session:
            statement = select(Conversation).where(Conversation.id == conversation_id)
            result = session.exec(statement)
            return result.first()
            
    def get_conversations(self) -> List[Conversation]:
        """Get all conversations"""
        with Session(self.engine) as session:
            statement = select(Conversation)
            result = session.exec(statement)
            return result.all()
            
    def add_message(self, conversation_id: str, role: str, content: str, 
                   tokens: Optional[int] = None, mode: str = "chat") -> Message:
        """Add a message to a conversation"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tokens=tokens,
            mode=mode
        )
        with Session(self.engine) as session:
            session.add(message)
            session.commit()
            session.refresh(message)
        return message
        
    def get_messages(self, conversation_id: str) -> List[Message]:
        """Get all messages in a conversation"""
        with Session(self.engine) as session:
            statement = select(Message).where(Message.conversation_id == conversation_id)
            result = session.exec(statement)
            return result.all()

# Global database instance
db = MemoryDatabase()
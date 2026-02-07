import uuid
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, create_engine, Session, select
from app.core.config import settings


class Conversation(SQLModel, table=True):
    """Represents a conversation/chat session"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Message(SQLModel, table=True):
    """Represents a message within a conversation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    conversation_id: str = Field(foreign_key="conversation.id", index=True)
    role: str = Field(index=True)
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    tokens: Optional[int] = None
    mode: str = Field(default="chat")


class Database:
    """Database manager for SQLite persistence"""

    def __init__(self, database_url: str = settings.DATABASE_URL):
        self.database_url = database_url
        self.engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            echo=False
        )
        self._init_db()

    def _init_db(self):
        """Initialize database tables"""
        SQLModel.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        """Get a new database session"""
        return Session(self.engine)

    def create_conversation(self, title: str) -> Conversation:
        """Create a new conversation"""
        session = self.get_session()
        try:
            conversation = Conversation(title=title)
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            return conversation
        finally:
            session.close()

    def get_conversations(self) -> List[Conversation]:
        """Get all conversations"""
        session = self.get_session()
        try:
            return session.exec(select(Conversation).order_by(Conversation.created_at.desc())).all()
        finally:
            session.close()

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a specific conversation by ID"""
        session = self.get_session()
        try:
            return session.exec(
                select(Conversation).where(Conversation.id == conversation_id)
            ).first()
        finally:
            session.close()

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        tokens: Optional[int] = None,
        mode: str = "chat"
    ) -> Message:
        """Add a message to a conversation"""
        session = self.get_session()
        try:
            message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                tokens=tokens,
                mode=mode
            )
            session.add(message)
            session.commit()
            session.refresh(message)
            return message
        finally:
            session.close()

    def get_messages(self, conversation_id: str) -> List[Message]:
        """Get all messages in a conversation"""
        session = self.get_session()
        try:
            return session.exec(
                select(Message).where(Message.conversation_id == conversation_id).order_by(Message.timestamp)
            ).all()
        finally:
            session.close()

    def get_message(self, message_id: str) -> Optional[Message]:
        """Get a specific message by ID"""
        session = self.get_session()
        try:
            return session.exec(
                select(Message).where(Message.id == message_id)
            ).first()
        finally:
            session.close()

    def update_conversation(self, conversation_id: str, title: str) -> Optional[Conversation]:
        """Update a conversation title"""
        session = self.get_session()
        try:
            conversation = session.exec(
                select(Conversation).where(Conversation.id == conversation_id)
            ).first()
            if conversation:
                conversation.title = title
                conversation.updated_at = datetime.utcnow()
                session.add(conversation)
                session.commit()
                session.refresh(conversation)
            return conversation
        finally:
            session.close()

    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation and all its messages"""
        session = self.get_session()
        try:
            session.exec(
                select(Message).where(Message.conversation_id == conversation_id)
            ).all()
            session.exec(
                select(Conversation).where(Conversation.id == conversation_id)
            ).first()
            session.delete(session.exec(
                select(Message).where(Message.conversation_id == conversation_id)
            ).first())
            session.commit()
            return True
        except Exception:
            return False
        finally:
            session.close()


# Global database instance
db = Database()

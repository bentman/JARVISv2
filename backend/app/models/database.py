from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, List, Dict
from datetime import datetime
import os
import uuid
from sqlalchemy import delete, func
from app.core.config import settings

# Lightweight crypto helpers for encrypt-at-rest without importing privacy_service (to avoid circular deps)
import base64
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

class Conversation(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    tags: Optional[str] = Field(default="")  # comma-separated

class Message(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    conversation_id: str = Field(foreign_key="conversation.id", index=True)
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    tokens: Optional[int] = None
    mode: str = "chat"  # "chat", "coding", "reasoning"
    tags: Optional[str] = Field(default="")  # comma-separated

class MemoryDatabase:
    """
    Database interface for conversation memory storage
    """
    
    def __init__(self):
        # Ensure data directory exists for SQLite file paths like sqlite:///./data/local_ai.db
        if settings.DATABASE_URL.startswith("sqlite"):
            db_path = settings.DATABASE_URL.split("sqlite:///")[-1]
            data_dir = os.path.dirname(db_path) or "."
            if data_dir and not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
            connect_args = {"check_same_thread": False}
        else:
            connect_args = {}
        self.engine = create_engine(settings.DATABASE_URL, echo=True, connect_args=connect_args)
        SQLModel.metadata.create_all(self.engine)
        # Derive encryption key once if enabled
        self._encrypt_enabled: bool = bool(getattr(settings, "PRIVACY_ENCRYPT_AT_REST", False))
        self._key: bytes | None = None
        if self._encrypt_enabled:
            try:
                password = settings.SECRET_KEY
                salt = getattr(settings, "PRIVACY_SALT", "local_ai_salt")
                self._key = PBKDF2(password, salt.encode("utf-8"), dkLen=32)
            except Exception:
                # Disable encryption if key derivation fails
                self._encrypt_enabled = False
                self._key = None
        
    def _enc_prefix(self) -> str:
        return "enc:v1:"

    def _encrypt_if_enabled(self, plaintext: str) -> str:
        if not self._encrypt_enabled or not plaintext:
            return plaintext
        try:
            cipher = AES.new(self._key, AES.MODE_GCM)
            ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode("utf-8"))
            buf = cipher.nonce + tag + ciphertext
            return self._enc_prefix() + base64.b64encode(buf).decode("utf-8")
        except Exception:
            # Fail open to avoid data loss
            return plaintext

    def _decrypt_if_needed(self, maybe_encrypted: str) -> str:
        if not isinstance(maybe_encrypted, str) or not maybe_encrypted.startswith(self._enc_prefix()):
            return maybe_encrypted
        try:
            enc_b64 = maybe_encrypted[len(self._enc_prefix()):]
            data = base64.b64decode(enc_b64.encode("utf-8"))
            nonce = data[:16]
            tag = data[16:32]
            ciphertext = data[32:]
            cipher = AES.new(self._key, AES.MODE_GCM, nonce=nonce)
            pt = cipher.decrypt_and_verify(ciphertext, tag)
            return pt.decode("utf-8")
        except Exception:
            # On failure, return raw content
            return maybe_encrypted
        
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
            
    def update_conversation_title(self, conversation_id: str, title: str) -> Optional[Conversation]:
        """Update conversation title and touch updated_at"""
        with Session(self.engine) as session:
            convo = session.get(Conversation, conversation_id)
            if not convo:
                return None
            convo.title = title
            convo.updated_at = datetime.utcnow()
            session.add(convo)
            session.commit()
            session.refresh(convo)
            return convo

    def add_message(self, conversation_id: str, role: str, content: str, 
                   tokens: Optional[int] = None, mode: str = "chat") -> Message:
        """Add a message to a conversation"""
        stored_content = self._encrypt_if_enabled(content)
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=stored_content,
            tokens=tokens,
            mode=mode
        )
        with Session(self.engine) as session:
            session.add(message)
            # Touch conversation.updated_at
            convo = session.get(Conversation, conversation_id)
            if convo:
                convo.updated_at = datetime.utcnow()
                session.add(convo)
            session.commit()
            session.refresh(message)
        # Return a copy with decrypted content for callers
        try:
            message.content = self._decrypt_if_needed(message.content)
        except Exception:
            pass
        return message
        
    def get_messages(self, conversation_id: str) -> List[Message]:
        """Get all messages in a conversation (unsorted)"""
        with Session(self.engine) as session:
            statement = select(Message).where(Message.conversation_id == conversation_id)
            result = session.exec(statement)
            msgs = result.all()
            # Decrypt in-place for callers
            for m in msgs:
                try:
                    m.content = self._decrypt_if_needed(m.content)
                except Exception:
                    pass
            return msgs

    def get_messages_sorted(self, conversation_id: str, ascending: bool = True) -> List[Message]:
        """Get messages sorted by timestamp"""
        from sqlalchemy import asc, desc
        with Session(self.engine) as session:
            order = asc(Message.timestamp) if ascending else desc(Message.timestamp)
            statement = select(Message).where(Message.conversation_id == conversation_id).order_by(order)
            result = session.exec(statement)
            msgs = result.all()
            for m in msgs:
                try:
                    m.content = self._decrypt_if_needed(m.content)
                except Exception:
                    pass
            return msgs
    
    def get_message(self, message_id: str) -> Optional[Message]:
        """Get a single message by ID"""
        with Session(self.engine) as session:
            statement = select(Message).where(Message.id == message_id)
            result = session.exec(statement)
            msg = result.first()
            if msg:
                try:
                    msg.content = self._decrypt_if_needed(msg.content)
                except Exception:
                    pass
            return msg

    def delete_message(self, message_id: str) -> bool:
        """Delete a message by ID"""
        with Session(self.engine) as session:
            res = session.exec(select(Message).where(Message.id == message_id)).first()
            if not res:
                return False
            session.delete(res)
            session.commit()
            return True

    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation and all its messages"""
        with Session(self.engine) as session:
            convo = session.get(Conversation, conversation_id)
            if not convo:
                return False
            # Delete messages first
            session.exec(delete(Message).where(Message.conversation_id == conversation_id))
            session.delete(convo)
            session.commit()
            return True

    def delete_messages_older_than(self, cutoff_datetime: datetime) -> int:
        """Delete messages older than cutoff; return count deleted"""
        with Session(self.engine) as session:
            old_msgs = session.exec(select(Message).where(Message.timestamp < cutoff_datetime)).all()
            count = len(old_msgs)
            for m in old_msgs:
                session.delete(m)
            session.commit()
            return count

    def get_conversation_stats(self, conversation_id: str) -> Dict:
        """Return counts and token sums for a conversation"""
        with Session(self.engine) as session:
            msgs = session.exec(select(Message).where(Message.conversation_id == conversation_id)).all()
            total_messages = len(msgs)
            total_tokens = sum(m.tokens or 0 for m in msgs)
            return {
                "conversation_id": conversation_id,
                "total_messages": total_messages,
                "total_tokens": total_tokens,
            }

    # Tag helpers
    def _normalize_tags(self, tags: List[str]) -> str:
        return ",".join(sorted({t.strip() for t in tags if t and t.strip()}))

    def set_conversation_tags(self, conversation_id: str, tags: List[str]) -> Optional[Conversation]:
        with Session(self.engine) as session:
            convo = session.get(Conversation, conversation_id)
            if not convo:
                return None
            convo.tags = self._normalize_tags(tags)
            convo.updated_at = datetime.utcnow()
            session.add(convo)
            session.commit()
            session.refresh(convo)
            return convo

    def set_message_tags(self, message_id: str, tags: List[str]) -> Optional[Message]:
        with Session(self.engine) as session:
            msg = session.get(Message, message_id)
            if not msg:
                return None
            msg.tags = self._normalize_tags(tags)
            session.add(msg)
            session.commit()
            session.refresh(msg)
            return msg

    def filter_conversations_by_tags(self, tags: List[str]) -> List[Conversation]:
        """Return conversations that contain ALL provided tags"""
        target = set(self._normalize_tags(tags).split(",")) if tags else set()
        with Session(self.engine) as session:
            all_convos = session.exec(select(Conversation)).all()
            if not target:
                return all_convos
            result = []
            for c in all_convos:
                ctags = set((c.tags or "").split(",")) if c.tags else set()
                if target.issubset(ctags):
                    result.append(c)
            return result

    # Export/Import
    def export_all(self) -> Dict:
        with Session(self.engine) as session:
            convos = session.exec(select(Conversation)).all()
            msgs = session.exec(select(Message)).all()
            def conv_to_dict(c: Conversation) -> Dict:
                return {
                    "id": c.id,
                    "title": c.title,
                    "created_at": c.created_at.isoformat(),
                    "updated_at": c.updated_at.isoformat(),
                    "tags": (c.tags or "").split(",") if c.tags else [],
                }
            def msg_to_dict(m: Message) -> Dict:
                # Decrypt content for export if needed
                try:
                    content = self._decrypt_if_needed(m.content)
                except Exception:
                    content = m.content
                return {
                    "id": m.id,
                    "conversation_id": m.conversation_id,
                    "role": m.role,
                    "content": content,
                    "timestamp": m.timestamp.isoformat(),
                    "tokens": m.tokens,
                    "mode": m.mode,
                    "tags": (m.tags or "").split(",") if m.tags else [],
                }
            return {
                "conversations": [conv_to_dict(c) for c in convos],
                "messages": [msg_to_dict(m) for m in msgs],
            }

    def import_data(self, data: Dict, merge: bool = True) -> Dict:
        """Import conversations and messages.
        Behavior:
        - Conversations are imported first; IDs may be regenerated when merge=False or on collision.
        - Messages referencing conversations are remapped via ID map.
        - Messages whose (remapped) conversation does not exist are skipped.
        Returns counts including skipped messages and the set of missing conversation IDs.
        """
        imported_convos = 0
        imported_msgs = 0
        skipped_msgs = 0
        missing_cids: set[str] = set()
        conv_id_map: Dict[str, str] = {}
        with Session(self.engine) as session:
            # Import conversations first, building an ID map
            for c in data.get("conversations", []):
                old_cid = c.get("id")
                new_cid = old_cid
                if not merge or not old_cid or session.get(Conversation, old_cid):
                    new_cid = str(uuid.uuid4())
                convo = Conversation(
                    id=new_cid,
                    title=c.get("title", "Untitled"),
                    created_at=datetime.fromisoformat(c.get("created_at")) if c.get("created_at") else datetime.utcnow(),
                    updated_at=datetime.fromisoformat(c.get("updated_at")) if c.get("updated_at") else datetime.utcnow(),
                    tags=self._normalize_tags(c.get("tags", [])),
                )
                if old_cid:
                    conv_id_map[old_cid] = new_cid
                session.add(convo)
                imported_convos += 1
            session.commit()

            # Import messages, remapping conversation_id via conv_id_map
            for m in data.get("messages", []):
                old_mid = m.get("id")
                if not merge or not old_mid or session.get(Message, old_mid):
                    new_mid = str(uuid.uuid4())
                else:
                    new_mid = old_mid
                orig_cid = m.get("conversation_id")
                mapped_cid = conv_id_map.get(orig_cid, orig_cid)
                # Validate conversation exists (either newly created or pre-existing)
                if not mapped_cid or not session.get(Conversation, mapped_cid):
                    skipped_msgs += 1
                    if orig_cid:
                        missing_cids.add(orig_cid)
                    continue
                msg = Message(
                    id=new_mid,
                    conversation_id=mapped_cid,
                    role=m.get("role", "user"),
                    content=self._encrypt_if_enabled(m.get("content", "")),
                    timestamp=datetime.fromisoformat(m.get("timestamp")) if m.get("timestamp") else datetime.utcnow(),
                    tokens=m.get("tokens"),
                    mode=m.get("mode", "chat"),
                    tags=self._normalize_tags(m.get("tags", [])),
                )
                session.add(msg)
                imported_msgs += 1
            session.commit()
        return {
            "conversations": imported_convos,
            "messages": imported_msgs,
            "skipped_messages": skipped_msgs,
            "missing_conversations": sorted(missing_cids),
        }

# Global database instance
db = MemoryDatabase()

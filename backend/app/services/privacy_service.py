import base64
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import hashlib
import re
from typing import Dict, List, Optional
from enum import Enum
from sqlmodel import SQLModel, Field, Session, select
from datetime import datetime, timedelta

from app.core.config import settings
from app.models.database import db


class DataClassification(Enum):
    PUBLIC = "public"
    PERSONAL = "personal"
    SENSITIVE = "sensitive"
    RESTRICTED = "restricted"


class PrivacyConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=1, primary_key=True)
    privacy_level: str = Field(default=settings.PRIVACY_DEFAULT_LEVEL)
    data_retention_days: int = Field(default=settings.PRIVACY_RETENTION_DAYS)
    redact_aggressiveness: str = Field(default=settings.PRIVACY_REDACT_AGGRESSIVENESS)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PrivacyService:
    """
    Privacy service for data encryption, classification, and local processing enforcement
    """
    
    def __init__(self):
        SQLModel.metadata.create_all(db.engine)
        self.key = self._derive_key(settings.SECRET_KEY, settings.PRIVACY_SALT)
        self.data_classifications = {}
        
    def _derive_key(self, password: str, salt: str) -> bytes:
        """Derive encryption key from password and salt (env-provided)"""
        return PBKDF2(password, salt.encode("utf-8"), dkLen=32)
        
    def encrypt_data(self, data: str) -> str:
        """
        Encrypt data using AES
        Returns base64 encoded encrypted data
        """
        cipher = AES.new(self.key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
        
        # Combine nonce, tag, and ciphertext
        encrypted_data = cipher.nonce + tag + ciphertext
        return base64.b64encode(encrypted_data).decode('utf-8')
        
    def decrypt_data(self, encrypted_data: str) -> str:
        """
        Decrypt data using AES
        Returns decrypted string
        """
        # Decode from base64
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        
        # Extract nonce, tag, and ciphertext
        nonce = encrypted_bytes[:16]
        tag = encrypted_bytes[16:32]
        ciphertext = encrypted_bytes[32:]
        
        # Decrypt
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        
        return plaintext.decode('utf-8')
        
    def classify_data(self, content: str) -> DataClassification:
        """
        Classify data based on sensitivity with expanded patterns
        Returns DataClassification enum value
        """
        content_lower = content.lower()
        
        # Define regex patterns for sensitive and personal data (expanded)
        patterns = {
            DataClassification.SENSITIVE: [
                r'\b\d{3}-\d{2}-\d{4}\b',  # US SSN
                r'\b(?:\d{4}[ -]?){3}\d{4}\b',  # Credit card (generic 16-digit)
                r'\b[A-Z]{2}[0-9A-Z]{2}[0-9A-Z]{1,30}\b',  # IBAN (generic)
            ],
            DataClassification.PERSONAL: [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',  # Email
                r'\b\+?\d{1,3}[\s.-]?\(?\d{1,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}\b',  # Intl phone
                r'\b\d{9,19}\b',  # Bank acct (generic long digit sequences)
                r'\b(?:\d{1,3}\.){3}\d{1,3}\b',  # IPv4
            ]
        }
        
        # Check patterns first
        for classification, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, content):
                    return classification
        
        # Check keywords
        sensitive_keywords = [
            "password", "social security", "medical record", "financial",
            "ssn", "credit card", "bank account", "tax id", "national insurance"
        ]
        
        for keyword in sensitive_keywords:
            if keyword in content_lower:
                return DataClassification.SENSITIVE
        
        personal_keywords = [
            "name", "address", "phone", "email", "birthday", "birth date",
            "passport", "driver's license", "national id"
        ]
        
        for keyword in personal_keywords:
            if keyword in content_lower:
                return DataClassification.PERSONAL
        
        return DataClassification.PUBLIC
    
    def should_process_locally(self, content: str, classification_threshold: DataClassification = DataClassification.SENSITIVE) -> bool:
        """
        Determine if data should be processed locally based on classification
        """
        classification = self.classify_data(content)
        
        # Define sensitivity hierarchy
        sensitivity_order = {
            DataClassification.PUBLIC: 0,
            DataClassification.PERSONAL: 1,
            DataClassification.SENSITIVE: 2,
            DataClassification.RESTRICTED: 3
        }
        
        # If classification is at or above threshold, process locally
        return sensitivity_order[classification] >= sensitivity_order[classification_threshold]
    
    def redact_sensitive_data(self, content: str) -> str:
        """
        Redact sensitive information from content
        """
        # Emails
        content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', '[EMAIL_REDACTED]', content)
        # Phones (intl + US)
        content = re.sub(r'\b\+?\d{1,3}[\s.-]?\(?\d{1,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}\b', '[PHONE_REDACTED]', content)
        # Credit cards
        content = re.sub(r'\b(?:\d{4}[ -]?){3}\d{4}\b', '[CREDIT_CARD_REDACTED]', content)
        # SSNs
        content = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN_REDACTED]', content)
        # IBAN (generic)
        content = re.sub(r'\b[A-Z]{2}[0-9A-Z]{2}[0-9A-Z]{1,30}\b', '[IBAN_REDACTED]', content)
        # IPv4
        content = re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '[IP_REDACTED]', content)
        return content
    
    def enforce_local_processing(self, content: str) -> Dict:
        """
        Enforce local processing based on data classification and privacy settings
        Returns dict with processing instructions
        """
        cfg = self.get_settings()
        classification = self.classify_data(content)
        should_process_locally = self.should_process_locally(content)
        redacted_content = self.redact_sensitive_data(content) if cfg["redact_aggressiveness"] in ("standard", "strict") else content
        
        return {
            "classification": classification.value,
            "should_process_locally": should_process_locally,
            "redacted_content": redacted_content if should_process_locally else content,
            "original_content_preserved": not should_process_locally
        }

    def get_settings(self) -> Dict:
        with Session(db.engine) as session:
            cfg = session.get(PrivacyConfig, 1)
            if not cfg:
                cfg = PrivacyConfig()
                session.add(cfg)
                session.commit()
                session.refresh(cfg)
            return {
                "privacy_level": cfg.privacy_level,
                "data_retention_days": cfg.data_retention_days,
                "redact_aggressiveness": cfg.redact_aggressiveness,
                "updated_at": cfg.updated_at.isoformat()
            }

    def set_settings(self, privacy_level: Optional[str] = None, data_retention_days: Optional[int] = None, redact_aggressiveness: Optional[str] = None) -> Dict:
        with Session(db.engine) as session:
            cfg = session.get(PrivacyConfig, 1)
            if not cfg:
                cfg = PrivacyConfig()
            if privacy_level is not None:
                cfg.privacy_level = privacy_level
            if data_retention_days is not None:
                cfg.data_retention_days = data_retention_days
            if redact_aggressiveness is not None:
                cfg.redact_aggressiveness = redact_aggressiveness
            cfg.updated_at = datetime.utcnow()
            session.add(cfg)
            session.commit()
            session.refresh(cfg)
            return self.get_settings()

    def scrub_text(self, text: str) -> str:
        return self.redact_sensitive_data(text)

    def delete_messages_older_than(self, days: int) -> int:
        """Delete messages older than N days from the database."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        # Implement using database layer
        return db.delete_messages_older_than(cutoff)

# Global privacy service instance
privacy_service = PrivacyService()

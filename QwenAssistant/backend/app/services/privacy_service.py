import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import hashlib
import re
from typing import Dict, List, Optional
from enum import Enum


class DataClassification(Enum):
    PUBLIC = "public"
    PERSONAL = "personal"
    SENSITIVE = "sensitive"
    RESTRICTED = "restricted"


class PrivacyService:
    """
    Privacy service for data encryption, classification, and local processing enforcement
    """
    
    def __init__(self):
        self.key = self._derive_key("default_password")
        self.data_classifications = {}
        
    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from password"""
        salt = b"local_ai_salt"  # In production, use a random salt
        return PBKDF2(password, salt, dkLen=32)
        
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
        Classify data based on sensitivity
        Returns DataClassification enum value
        """
        content_lower = content.lower()
        
        # Define regex patterns for sensitive data
        patterns = {
            DataClassification.SENSITIVE: [
                r'\b\d{3}-\d{2}-\d{4}\b',  # SSN pattern
                r'\b(?:\d{4}[ -]?){3}\d{4}\b',  # Credit card pattern
                r'\b\d{9,19}\b',  # Bank account numbers
            ],
            DataClassification.PERSONAL: [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
                r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',  # Phone
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
        # Redact emails
        content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]', content)
        
        # Redact phone numbers
        content = re.sub(r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b', '[PHONE_REDACTED]', content)
        
        # Redact credit cards
        content = re.sub(r'\b(?:\d{4}[ -]?){3}\d{4}\b', '[CREDIT_CARD_REDACTED]', content)
        
        # Redact SSNs
        content = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN_REDACTED]', content)
        
        return content
    
    def enforce_local_processing(self, content: str) -> Dict:
        """
        Enforce local processing based on data classification
        Returns dict with processing instructions
        """
        classification = self.classify_data(content)
        should_process_locally = self.should_process_locally(content)
        redacted_content = self.redact_sensitive_data(content)
        
        return {
            "classification": classification.value,
            "should_process_locally": should_process_locally,
            "redacted_content": redacted_content if should_process_locally else content,
            "original_content_preserved": not should_process_locally
        }

# Global privacy service instance
privacy_service = PrivacyService()
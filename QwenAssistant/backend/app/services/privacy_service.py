import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import hashlib

class PrivacyService:
    """
    Privacy service for data encryption and classification
    """
    
    def __init__(self):
        self.key = self._derive_key("default_password")
        
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
        
    def classify_data(self, content: str) -> str:
        """
        Classify data based on sensitivity
        Returns "sensitive", "personal", or "public"
        """
        # In a real implementation, this would use Presidio or similar
        # For now, we'll use simple heuristics
        sensitive_keywords = [
            "password", "ssn", "social security", "credit card", 
            "bank account", "medical record", "financial"
        ]
        
        content_lower = content.lower()
        for keyword in sensitive_keywords:
            if keyword in content_lower:
                return "sensitive"
                
        personal_keywords = [
            "name", "address", "phone", "email", "birthday"
        ]
        
        for keyword in personal_keywords:
            if keyword in content_lower:
                return "personal"
                
        return "public"

# Global privacy service instance
privacy_service = PrivacyService()
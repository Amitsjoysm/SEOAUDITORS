"""Encryption utilities for sensitive data"""
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64


class EncryptionService:
    """Service for encrypting and decrypting sensitive data"""
    
    def __init__(self):
        # Generate encryption key from SECRET_KEY
        secret_key = os.getenv("SECRET_KEY", "mjseo-secret-key-change-in-production-2024")
        self.fernet = self._generate_fernet(secret_key)
    
    def _generate_fernet(self, secret_key: str) -> Fernet:
        """Generate Fernet cipher from secret key"""
        # Use PBKDF2 to derive a proper 32-byte key
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'mjseo-salt-v1',  # Fixed salt for consistency
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
        return Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext and return base64 encoded ciphertext"""
        if not plaintext:
            return ""
        encrypted = self.fernet.encrypt(plaintext.encode())
        return encrypted.decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt base64 encoded ciphertext and return plaintext"""
        if not ciphertext:
            return ""
        try:
            decrypted = self.fernet.decrypt(ciphertext.encode())
            return decrypted.decode()
        except Exception:
            # If decryption fails, return empty string
            return ""


# Global encryption service instance
encryption_service = EncryptionService()

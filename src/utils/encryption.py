"""
AES-256 encryption utilities for secure storage
"""

import os
from pathlib import Path
from typing import Optional
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import base64

class EncryptionManager:
    """Handles AES-256 encryption/decryption for configuration and macro files"""
    
    def __init__(self, key_file: Optional[Path] = None):
        """Initialize encryption manager with key"""
        self.key_file = key_file or Path.home() / ".excel_macro_automation" / ".key"
        self.key = self._load_or_generate_key()
    
    def _load_or_generate_key(self) -> bytes:
        """Load existing key or generate new one"""
        if self.key_file.exists():
            return base64.b64decode(self.key_file.read_bytes())
        else:
            # Generate new key
            key = os.urandom(32)  # 256 bits
            self.key_file.parent.mkdir(parents=True, exist_ok=True)
            self.key_file.write_bytes(base64.b64encode(key))
            # Set restrictive permissions (Unix-like systems)
            if hasattr(os, 'chmod'):
                os.chmod(self.key_file, 0o600)
            return key
    
    def derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive key from password using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password.encode())
    
    def encrypt(self, data: bytes, password: Optional[str] = None) -> bytes:
        """Encrypt data using AES-256-CBC"""
        # Use password-derived key if provided, otherwise use stored key
        if password:
            salt = os.urandom(16)
            key = self.derive_key(password, salt)
        else:
            salt = b''
            key = self.key
        
        # Generate IV
        iv = os.urandom(16)
        
        # Pad data to block size
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        
        # Encrypt
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        # Return salt + iv + encrypted data
        return salt + iv + encrypted_data
    
    def decrypt(self, encrypted_data: bytes, password: Optional[str] = None) -> bytes:
        """Decrypt data using AES-256-CBC"""
        # Extract components
        if password:
            salt = encrypted_data[:16]
            iv = encrypted_data[16:32]
            ciphertext = encrypted_data[32:]
            key = self.derive_key(password, salt)
        else:
            iv = encrypted_data[:16]
            ciphertext = encrypted_data[16:]
            key = self.key
        
        # Decrypt
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Remove padding
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        
        return data
    
    def encrypt_file(self, input_path: Path, output_path: Path, password: Optional[str] = None) -> None:
        """Encrypt a file"""
        data = input_path.read_bytes()
        encrypted_data = self.encrypt(data, password)
        output_path.write_bytes(encrypted_data)
    
    def decrypt_file(self, input_path: Path, output_path: Path, password: Optional[str] = None) -> None:
        """Decrypt a file"""
        encrypted_data = input_path.read_bytes()
        data = self.decrypt(encrypted_data, password)
        output_path.write_bytes(data)


# Global encryption manager instance
_encryption_manager = None


def get_encryption_manager() -> EncryptionManager:
    """Get global encryption manager instance"""
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager()
    return _encryption_manager


def encrypt_data(data: str, password: str) -> bytes:
    """Encrypt string data with password"""
    manager = get_encryption_manager()
    return manager.encrypt(data.encode('utf-8'), password)


def decrypt_data(encrypted_data: bytes, password: str) -> str:
    """Decrypt data with password and return as string"""
    manager = get_encryption_manager()
    decrypted_bytes = manager.decrypt(encrypted_data, password)
    return decrypted_bytes.decode('utf-8')
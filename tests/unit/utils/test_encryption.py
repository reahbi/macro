"""
Unit tests for encryption utilities (AES-256 encryption/decryption)
Tests the cryptographic functionality with various data types and edge cases.
"""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
import base64

from utils.encryption import EncryptionManager, get_encryption_manager, encrypt_data, decrypt_data


class TestEncryptionManager:
    """Test suite for EncryptionManager class"""
    
    def test_encryption_manager_initialization(self, temp_dir):
        """Test EncryptionManager initialization and key generation"""
        key_file = temp_dir / ".test_key"
        
        # Test new key generation
        manager = EncryptionManager(key_file)
        
        assert key_file.exists()
        assert len(base64.b64decode(key_file.read_bytes())) == 32  # 256 bits
        assert manager.key is not None
        assert len(manager.key) == 32
    
    def test_key_loading_existing(self, temp_dir):
        """Test loading existing encryption key"""
        key_file = temp_dir / ".test_key"
        
        # Create manager and key
        manager1 = EncryptionManager(key_file)
        original_key = manager1.key
        
        # Create new manager with same key file
        manager2 = EncryptionManager(key_file)
        
        assert manager2.key == original_key
    
    def test_key_derivation_pbkdf2(self):
        """Test password-based key derivation using PBKDF2"""
        manager = EncryptionManager()
        password = "test_password_123"
        salt = os.urandom(16)
        
        # Test key derivation
        derived_key1 = manager.derive_key(password, salt)
        derived_key2 = manager.derive_key(password, salt)
        
        assert len(derived_key1) == 32  # 256 bits
        assert derived_key1 == derived_key2  # Same password/salt = same key
        
        # Different salt should produce different key
        different_salt = os.urandom(16)
        derived_key3 = manager.derive_key(password, different_salt)
        assert derived_key1 != derived_key3
    
    def test_encryption_decryption_basic(self):
        """Test basic encryption and decryption cycle"""
        manager = EncryptionManager()
        test_data = b"Hello, World! This is a test message for encryption."
        
        # Encrypt data
        encrypted = manager.encrypt(test_data)
        
        # Verify encrypted data structure
        assert len(encrypted) > len(test_data)  # Encrypted should be larger due to IV
        assert encrypted != test_data  # Should be different
        
        # Decrypt data
        decrypted = manager.decrypt(encrypted)
        
        assert decrypted == test_data
    
    def test_encryption_with_password(self):
        """Test encryption/decryption with password"""
        manager = EncryptionManager()
        test_data = b"Password protected data"
        password = "secure_password_123"
        
        # Encrypt with password
        encrypted = manager.encrypt(test_data, password)
        
        # Decrypt with same password
        decrypted = manager.decrypt(encrypted, password)
        assert decrypted == test_data
        
        # Decrypt with wrong password should fail
        with pytest.raises(Exception):  # Should raise decryption error
            manager.decrypt(encrypted, "wrong_password")
    
    def test_encryption_different_data_types(self):
        """Test encryption with various data types and sizes"""
        manager = EncryptionManager()
        
        test_cases = [
            b"",  # Empty data
            b"a",  # Single byte
            b"Short message",  # Short message
            b"A" * 1000,  # Repetitive data
            b"Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 100,  # Long text
            bytes(range(256)),  # All byte values
            "한글 테스트 데이터 암호화".encode('utf-8'),  # Unicode data
        ]
        
        for test_data in test_cases:
            encrypted = manager.encrypt(test_data)
            decrypted = manager.decrypt(encrypted)
            assert decrypted == test_data, f"Failed for data: {test_data[:50]}"
    
    def test_iv_randomness(self):
        """Test that each encryption uses different IV"""
        manager = EncryptionManager()
        test_data = b"Same data, different IVs"
        
        encrypted1 = manager.encrypt(test_data)
        encrypted2 = manager.encrypt(test_data)
        
        # Different encryptions should produce different results due to random IV
        assert encrypted1 != encrypted2
        
        # But both should decrypt to same data
        assert manager.decrypt(encrypted1) == test_data
        assert manager.decrypt(encrypted2) == test_data
    
    def test_file_encryption_decryption(self, temp_dir):
        """Test file encryption and decryption"""
        manager = EncryptionManager()
        
        # Create test file
        input_file = temp_dir / "test_input.txt"
        test_content = "This is test file content for encryption testing.\n한글도 포함된 테스트 파일입니다."
        input_file.write_text(test_content, encoding='utf-8')
        
        # Encrypt file
        encrypted_file = temp_dir / "test_encrypted.enc"
        manager.encrypt_file(input_file, encrypted_file)
        
        assert encrypted_file.exists()
        assert encrypted_file.read_bytes() != input_file.read_bytes()
        
        # Decrypt file
        decrypted_file = temp_dir / "test_decrypted.txt"
        manager.decrypt_file(encrypted_file, decrypted_file)
        
        assert decrypted_file.exists()
        assert decrypted_file.read_text(encoding='utf-8') == test_content
    
    def test_file_encryption_with_password(self, temp_dir):
        """Test file encryption with password protection"""
        manager = EncryptionManager()
        password = "file_password_123"
        
        # Create test file
        input_file = temp_dir / "test_input.txt"
        test_content = "Password protected file content"
        input_file.write_text(test_content)
        
        # Encrypt with password
        encrypted_file = temp_dir / "test_encrypted.enc"
        manager.encrypt_file(input_file, encrypted_file, password)
        
        # Decrypt with password
        decrypted_file = temp_dir / "test_decrypted.txt"
        manager.decrypt_file(encrypted_file, decrypted_file, password)
        
        assert decrypted_file.read_text() == test_content
    
    @pytest.mark.parametrize("invalid_data", [
        b"invalid_short_data",  # Too short for proper decryption
        b"A" * 15,  # Wrong length
        b"not_encrypted_at_all",  # Not encrypted data
    ])
    def test_decryption_invalid_data(self, invalid_data):
        """Test decryption with invalid/corrupted data"""
        manager = EncryptionManager()
        
        with pytest.raises(Exception):  # Should raise decryption error
            manager.decrypt(invalid_data)
    
    def test_key_file_permissions(self, temp_dir):
        """Test that key file has restrictive permissions (Unix-like)"""
        key_file = temp_dir / ".test_key"
        
        with patch('os.chmod') as mock_chmod:
            with patch('hasattr', return_value=True):
                manager = EncryptionManager(key_file)
                
                # Verify chmod was called with restrictive permissions
                mock_chmod.assert_called_with(key_file, 0o600)
    
    def test_multiple_encryption_cycles(self):
        """Test multiple encryption/decryption cycles for stability"""
        manager = EncryptionManager()
        original_data = b"Multi-cycle test data with special chars: !@#$%^&*()"
        
        current_data = original_data
        
        # Perform 10 encryption/decryption cycles
        for i in range(10):
            encrypted = manager.encrypt(current_data)
            decrypted = manager.decrypt(encrypted)
            assert decrypted == current_data
            current_data = decrypted
        
        assert current_data == original_data


class TestUtilityFunctions:
    """Test utility functions for encryption"""
    
    def test_get_encryption_manager_singleton(self):
        """Test that get_encryption_manager returns singleton instance"""
        manager1 = get_encryption_manager()
        manager2 = get_encryption_manager()
        
        assert manager1 is manager2  # Same instance
        assert isinstance(manager1, EncryptionManager)
    
    def test_encrypt_data_function(self):
        """Test encrypt_data utility function"""
        test_string = "Test string for encryption function"
        password = "function_test_password"
        
        encrypted = encrypt_data(test_string, password)
        
        assert isinstance(encrypted, bytes)
        assert encrypted != test_string.encode('utf-8')
    
    def test_decrypt_data_function(self):
        """Test decrypt_data utility function"""
        test_string = "Test string for decryption function"
        password = "function_test_password"
        
        # Encrypt then decrypt
        encrypted = encrypt_data(test_string, password)
        decrypted = decrypt_data(encrypted, password)
        
        assert decrypted == test_string
        assert isinstance(decrypted, str)
    
    def test_utility_functions_round_trip(self):
        """Test complete round trip with utility functions"""
        test_cases = [
            "Simple English text",
            "한글 텍스트 암호화 테스트",
            "Mixed 한글 and English with numbers 12345",
            "Special characters: !@#$%^&*()_+-=[]{}|;:'\",.<>?",
            "Very long text: " + "A" * 1000,
            "",  # Empty string
        ]
        
        password = "utility_test_password"
        
        for test_data in test_cases:
            encrypted = encrypt_data(test_data, password)
            decrypted = decrypt_data(encrypted, password)
            assert decrypted == test_data, f"Failed for: {test_data[:50]}"


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_missing_key_file_directory(self, temp_dir):
        """Test behavior when key file directory doesn't exist"""
        non_existent_dir = temp_dir / "non_existent" / ".key"
        
        # Should create directory and key file
        manager = EncryptionManager(non_existent_dir)
        
        assert non_existent_dir.exists()
        assert manager.key is not None
    
    def test_corrupted_key_file(self, temp_dir):
        """Test behavior with corrupted key file"""
        key_file = temp_dir / ".corrupted_key"
        
        # Create corrupted key file
        key_file.write_text("corrupted_key_data")
        
        # Should handle error gracefully by regenerating key
        with pytest.raises(Exception):  # Should fail due to invalid base64
            EncryptionManager(key_file)
    
    @patch('builtins.open', side_effect=PermissionError("Access denied"))
    def test_permission_error_handling(self, mock_open_func):
        """Test handling of permission errors"""
        with pytest.raises(PermissionError):
            EncryptionManager(Path("/restricted/path/.key"))
    
    def test_large_data_encryption(self):
        """Test encryption of large data (memory efficiency)"""
        manager = EncryptionManager()
        
        # Create 1MB of test data
        large_data = b"A" * (1024 * 1024)
        
        encrypted = manager.encrypt(large_data)
        decrypted = manager.decrypt(encrypted)
        
        assert decrypted == large_data
        assert len(encrypted) > len(large_data)  # Includes IV and padding


class TestSecurityConsiderations:
    """Test security aspects of encryption implementation"""
    
    def test_key_entropy(self):
        """Test that generated keys have good entropy"""
        manager1 = EncryptionManager()
        manager2 = EncryptionManager()
        
        # Different instances should have different keys
        assert manager1.key != manager2.key
        
        # Keys should have full 256-bit entropy (non-zero bytes)
        assert len(set(manager1.key)) > 10  # Should have varied bytes
        assert len(set(manager2.key)) > 10
    
    def test_password_salt_uniqueness(self):
        """Test that password encryption uses unique salts"""
        manager = EncryptionManager()
        test_data = b"Same data with password"
        password = "same_password"
        
        encrypted1 = manager.encrypt(test_data, password)
        encrypted2 = manager.encrypt(test_data, password)
        
        # Should be different due to random salt
        assert encrypted1 != encrypted2
        
        # Extract salts (first 16 bytes)
        salt1 = encrypted1[:16]
        salt2 = encrypted2[:16]
        assert salt1 != salt2
    
    def test_no_key_exposure_in_memory(self):
        """Test that keys are properly handled in memory"""
        manager = EncryptionManager()
        
        # Key should be bytes, not string (to avoid string interning)
        assert isinstance(manager.key, bytes)
        assert len(manager.key) == 32
    
    def test_pbkdf2_iteration_count(self):
        """Test that PBKDF2 uses sufficient iterations"""
        manager = EncryptionManager()
        
        # This is indirect testing - we verify that key derivation is sufficiently slow
        import time
        
        password = "test_password"
        salt = os.urandom(16)
        
        start_time = time.time()
        derived_key = manager.derive_key(password, salt)
        end_time = time.time()
        
        # PBKDF2 with 100,000 iterations should take some time
        duration = end_time - start_time
        assert duration > 0.01  # Should take at least 10ms
        assert len(derived_key) == 32


@pytest.mark.integration
class TestEncryptionIntegration:
    """Integration tests for encryption with other components"""
    
    def test_macro_storage_encryption_compatibility(self, temp_dir):
        """Test encryption compatibility with macro storage system"""
        manager = EncryptionManager()
        
        # Simulate macro data
        macro_json = '{"macro_id": "test", "name": "Test Macro", "steps": []}'
        macro_data = macro_json.encode('utf-8')
        
        # Encrypt as macro storage would
        encrypted = manager.encrypt(macro_data)
        
        # Decrypt as macro storage would
        decrypted = manager.decrypt(encrypted)
        decrypted_json = decrypted.decode('utf-8')
        
        assert decrypted_json == macro_json
    
    def test_settings_encryption_compatibility(self):
        """Test encryption compatibility with settings storage"""
        manager = EncryptionManager()
        password = "settings_password"
        
        # Simulate settings data with various types
        settings_data = {
            "api_key": "secret_api_key_12345",
            "user_preferences": {"theme": "dark", "language": "ko"},
            "recent_files": ["/path/to/file1.xlsx", "/path/to/file2.xlsx"]
        }
        
        import json
        settings_json = json.dumps(settings_data, ensure_ascii=False)
        settings_bytes = settings_json.encode('utf-8')
        
        # Encrypt and decrypt
        encrypted = manager.encrypt(settings_bytes, password)
        decrypted = manager.decrypt(encrypted, password)
        restored_json = decrypted.decode('utf-8')
        restored_data = json.loads(restored_json)
        
        assert restored_data == settings_data
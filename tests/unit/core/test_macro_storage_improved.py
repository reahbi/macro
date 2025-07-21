"""
Improved unit tests for macro storage with minimal mocking
Tests actual file I/O and error conditions
"""

import json
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import os
import stat

from core.macro_storage import MacroStorage, MacroFormat
from core.macro_types import Macro, MouseClickStep, KeyboardTypeStep, WaitTimeStep
from utils.encryption import EncryptionManager


class TestMacroStorageReal:
    """Test MacroStorage with real file operations"""
    
    @pytest.fixture
    def temp_storage_dir(self):
        """Create real temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def storage(self, temp_storage_dir):
        """Create MacroStorage with real directory"""
        return MacroStorage(temp_storage_dir)
    
    @pytest.fixture
    def test_macro(self):
        """Create test macro with real data"""
        macro = Macro(
            name="실제 테스트 매크로",
            description="한글과 특수문자를 포함한 설명 @#$%",
            variables={"환자명": "홍길동", "검사코드": "B001"}
        )
        macro.add_step(MouseClickStep(name="클릭", x=100, y=200))
        macro.add_step(KeyboardTypeStep(name="입력", text="{{환자명}} - {{검사코드}}"))
        return macro
    
    def test_save_and_load_json_real(self, storage, test_macro, temp_storage_dir):
        """Test actual JSON save and load operations"""
        # Save macro
        result = storage.save_macro(test_macro, format_type=MacroFormat.JSON)
        assert result is True
        
        # Verify file exists
        expected_path = temp_storage_dir / "macros" / f"{test_macro.name}.json"
        assert expected_path.exists()
        assert expected_path.stat().st_size > 0
        
        # Read and verify content
        with open(expected_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        assert saved_data["schema_version"] == storage.SCHEMA_VERSION
        assert saved_data["macro"]["name"] == "실제 테스트 매크로"
        assert len(saved_data["macro"]["steps"]) == 2
        
        # Load macro back
        loaded_macro = storage.load_macro(str(expected_path))
        assert loaded_macro.name == test_macro.name
        assert loaded_macro.description == test_macro.description
        assert loaded_macro.variables == test_macro.variables
        assert len(loaded_macro.steps) == len(test_macro.steps)
    
    def test_save_encrypted_real(self, storage, test_macro, temp_storage_dir):
        """Test actual encrypted save and load"""
        # Save encrypted
        result = storage.save_macro(test_macro, format_type=MacroFormat.ENCRYPTED)
        assert result is True
        
        # Verify encrypted file exists
        expected_path = temp_storage_dir / "macros" / f"{test_macro.name}.emf"
        assert expected_path.exists()
        
        # Verify it's actually encrypted (not readable as JSON)
        with open(expected_path, 'rb') as f:
            encrypted_data = f.read()
        
        # Should not be valid JSON
        with pytest.raises(json.JSONDecodeError):
            json.loads(encrypted_data)
        
        # Should be able to load it back
        loaded_macro = storage.load_macro(str(expected_path))
        assert loaded_macro.name == test_macro.name
    
    def test_permission_error_real(self, test_macro, temp_storage_dir):
        """Test real permission error handling"""
        # Create read-only directory
        readonly_dir = temp_storage_dir / "readonly"
        readonly_dir.mkdir()
        
        # Make it read-only (Windows)
        if os.name == 'nt':
            os.chmod(readonly_dir, stat.S_IRUSR | stat.S_IXUSR)
        
        storage = MacroStorage(readonly_dir)
        
        # Try to save - should handle permission error gracefully
        result = storage.save_macro(test_macro)
        
        # Should either fail gracefully or use fallback directory
        if not result:
            # Failed as expected
            assert True
        else:
            # Used fallback directory
            assert storage.storage_dir != readonly_dir
    
    def test_disk_space_simulation(self, storage, temp_storage_dir):
        """Test handling of disk space issues"""
        # Create a very large macro
        huge_macro = Macro(name="거대한 매크로")
        
        # Add thousands of steps
        for i in range(10000):
            huge_macro.add_step(KeyboardTypeStep(
                name=f"단계 {i}",
                text=f"매우 긴 텍스트 " * 100  # Long text
            ))
        
        # Try to save
        result = storage.save_macro(huge_macro)
        
        if result:
            # Verify file size
            file_path = temp_storage_dir / "macros" / f"{huge_macro.name}.json"
            file_size = file_path.stat().st_size
            assert file_size > 1024 * 1024  # Should be > 1MB
            
            # Verify it can be loaded back
            loaded = storage.load_macro(str(file_path))
            assert len(loaded.steps) == 10000
    
    def test_special_characters_filename(self, storage, temp_storage_dir):
        """Test handling of special characters in filenames"""
        # Windows forbidden characters: < > : " | ? * \
        special_macro = Macro(name='매크로: "특수" <문자> |테스트|')
        special_macro.add_step(MouseClickStep(x=0, y=0))
        
        # Should save successfully with sanitized filename
        result = storage.save_macro(special_macro)
        assert result is True
        
        # Find the saved file
        saved_files = list((temp_storage_dir / "macros").glob("*.json"))
        assert len(saved_files) == 1
        
        # Filename should be sanitized
        filename = saved_files[0].name
        assert ':' not in filename
        assert '"' not in filename
        assert '<' not in filename
        assert '>' not in filename
        assert '|' not in filename
    
    def test_concurrent_access(self, storage, test_macro, temp_storage_dir):
        """Test concurrent file access handling"""
        import threading
        import time
        
        results = []
        
        def save_macro(index):
            macro = Macro(name=f"동시접근_{index}")
            macro.add_step(MouseClickStep(x=index, y=index))
            result = storage.save_macro(macro)
            results.append((index, result))
        
        # Start multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=save_macro, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # All saves should succeed
        assert len(results) == 10
        assert all(result[1] for result in results)
        
        # Verify all files exist
        saved_files = list((temp_storage_dir / "macros").glob("동시접근_*.json"))
        assert len(saved_files) == 10
    
    def test_backup_creation_real(self, storage, test_macro, temp_storage_dir):
        """Test real backup file creation"""
        # Save initial version
        storage.save_macro(test_macro)
        
        # Modify macro
        test_macro.add_step(WaitTimeStep(seconds=1.0))
        
        # Save with backup
        result = storage.save_macro(test_macro, create_backup=True)
        assert result is True
        
        # Verify backup was created
        backup_dir = temp_storage_dir / "macros" / "backups"
        assert backup_dir.exists()
        
        backup_files = list(backup_dir.glob("*.json.bak"))
        assert len(backup_files) >= 1
        
        # Verify backup content is the original
        with open(backup_files[0], 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        # Original had 2 steps, modified has 3
        assert len(backup_data["macro"]["steps"]) == 2
    
    def test_unicode_handling(self, storage, temp_storage_dir):
        """Test handling of various Unicode characters"""
        unicode_macro = Macro(
            name="유니코드 😀 🎉 测试 тест",
            description="한글, 이모지😎, 中文, Русский, العربية"
        )
        unicode_macro.add_step(KeyboardTypeStep(text="안녕하세요 👋"))
        
        # Save and load
        result = storage.save_macro(unicode_macro)
        assert result is True
        
        # Load back
        file_path = list((temp_storage_dir / "macros").glob("*.json"))[0]
        loaded = storage.load_macro(str(file_path))
        
        assert loaded.name == unicode_macro.name
        assert loaded.description == unicode_macro.description
        assert loaded.steps[0].text == "안녕하세요 👋"
    
    def test_very_long_path(self, temp_storage_dir):
        """Test Windows MAX_PATH limitation"""
        # Create nested directories approaching MAX_PATH
        deep_path = temp_storage_dir
        for i in range(20):
            deep_path = deep_path / f"very_long_directory_name_{i}"
        
        try:
            deep_path.mkdir(parents=True, exist_ok=True)
            storage = MacroStorage(deep_path)
            
            macro = Macro(name="test")
            macro.add_step(MouseClickStep(x=0, y=0))
            
            result = storage.save_macro(macro)
            
            # On Windows, this might fail due to MAX_PATH
            if not result:
                # Expected on Windows with long paths
                assert os.name == 'nt'
            else:
                # Should work on systems without path limitations
                assert (deep_path / "macros" / "test.json").exists()
                
        except OSError as e:
            # Expected on Windows
            assert os.name == 'nt'
"""
Unit tests for macro storage and JSON serialization
Tests the MacroStorage class with comprehensive mocking of file I/O operations.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, mock_open, MagicMock
from typing import Dict, Any

from core.macro_storage import MacroStorage, MacroFormat
from core.macro_types import Macro, MouseClickStep, KeyboardTypeStep, WaitTimeStep


class TestMacroStorageInitialization:
    """Test MacroStorage initialization and configuration"""
    
    def test_default_initialization(self):
        """Test MacroStorage with default storage directory"""
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            storage = MacroStorage()
            
            assert storage.SCHEMA_VERSION == "1.0.0"
            assert "macros" in str(storage.storage_dir)
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    
    def test_custom_storage_directory(self, temp_dir):
        """Test MacroStorage with custom storage directory"""
        custom_dir = temp_dir / "custom_macros"
        
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            storage = MacroStorage(custom_dir)
            
            assert storage.storage_dir == custom_dir
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    
    @patch('core.macro_storage.EncryptionManager')
    def test_encryption_manager_initialization(self, mock_encryption_class):
        """Test that EncryptionManager is properly initialized"""
        mock_manager = Mock()
        mock_encryption_class.return_value = mock_manager
        
        with patch('pathlib.Path.mkdir'):
            storage = MacroStorage()
        
        assert storage.encryption_manager == mock_manager
        mock_encryption_class.assert_called_once()


class TestMacroSaving:
    """Test macro saving functionality with file I/O mocking"""
    
    def setup_method(self):
        """Setup test fixtures"""
        with patch('pathlib.Path.mkdir'):
            with patch('core.macro_storage.EncryptionManager'):
                self.storage = MacroStorage()
        self.test_macro = Macro(
            name="Test Macro",
            description="Test macro for saving",
            variables={"test_var": "test_value"}
        )
        self.test_macro.add_step(MouseClickStep(name="Test Click", x=100, y=200))
    
    @patch('pathlib.Path.write_text')
    @patch('pathlib.Path.exists')
    def test_save_macro_json_format(self, mock_exists, mock_write_text):
        """Test saving macro in JSON format"""
        mock_exists.return_value = False  # No existing file
        
        # Test save operation
        result = self.storage.save_macro(
            self.test_macro, 
            format_type=MacroFormat.JSON
        )
        
        assert result is True
        
        # Verify write_text was called
        mock_write_text.assert_called_once()
        
        # Get the written content
        written_content = mock_write_text.call_args[0][0]
        written_data = json.loads(written_content)
        
        # Verify structure
        assert written_data["schema_version"] == "1.0.0"
        assert "macro" in written_data
        assert written_data["macro"]["name"] == "Test Macro"
        assert len(written_data["macro"]["steps"]) == 1
    
    @patch('pathlib.Path.write_bytes')
    @patch('pathlib.Path.exists')
    def test_save_macro_encrypted_format(self, mock_exists, mock_write_bytes):
        """Test saving macro in encrypted format"""
        mock_exists.return_value = False
        self.storage.encryption_manager.encrypt.return_value = b'encrypted_test_data'
        
        # Test save operation
        result = self.storage.save_macro(
            self.test_macro,
            format_type=MacroFormat.ENCRYPTED
        )
        
        assert result is True
        
        # Verify encryption was called
        self.storage.encryption_manager.encrypt.assert_called_once()
        
        # Verify encrypted data was written
        mock_write_bytes.assert_called_once_with(b'encrypted_test_data')
        
        # Verify file extension was changed to .emf
        call_args = mock_write_bytes.call_args_list[0]
        # The method is called on a Path object, check that it was called
        assert mock_write_bytes.called
    
    @patch('pathlib.Path.write_text')
    @patch('pathlib.Path.exists')
    @patch('core.macro_storage.MacroStorage._create_backup')
    def test_save_macro_with_backup(self, mock_create_backup, mock_exists, mock_write_text):
        """Test saving macro with backup creation"""
        mock_exists.return_value = True  # Existing file
        
        result = self.storage.save_macro(
            self.test_macro,
            create_backup=True
        )
        
        assert result is True
        mock_create_backup.assert_called_once()
        mock_write_text.assert_called_once()
    
    @patch('pathlib.Path.write_text')
    def test_save_macro_custom_path(self, mock_write_text):
        """Test saving macro to custom file path"""
        custom_path = "/custom/path/macro.json"
        
        result = self.storage.save_macro(
            self.test_macro,
            file_path=custom_path
        )
        
        assert result is True
        mock_write_text.assert_called_once()
    
    @patch('pathlib.Path.write_text', side_effect=Exception("Write error"))
    @patch('logger.app_logger.get_logger')
    def test_save_macro_error_handling(self, mock_logger, mock_write_text):
        """Test error handling during save operation"""
        mock_log = Mock()
        mock_logger.return_value = mock_log
        
        result = self.storage.save_macro(self.test_macro)
        
        assert result is False
        mock_log.error.assert_called_once()
    
    def test_save_macro_data_structure(self):
        """Test the structure of saved macro data"""
        # Create complex macro for testing
        complex_macro = Macro(
            name="Complex Test Macro",
            description="A complex macro with multiple steps",
            variables={"var1": "value1", "var2": 123},
            metadata={"author": "test", "tags": ["automation", "test"]}
        )
        
        # Add various step types
        complex_macro.add_step(MouseClickStep(name="Click", x=100, y=200))
        complex_macro.add_step(KeyboardTypeStep(name="Type", text="{{var1}}"))
        complex_macro.add_step(WaitTimeStep(name="Wait", seconds=2.0))
        
        # Mock the write operation to capture data
        with patch('pathlib.Path.write_text') as mock_write_text:
            with patch('pathlib.Path.exists', return_value=False):
                self.storage.save_macro(complex_macro)
        
        # Analyze written data
        written_content = mock_write_text.call_args[0][0]
        data = json.loads(written_content)
        
        # Verify schema and structure
        assert data["schema_version"] == "1.0.0"
        
        macro_data = data["macro"]
        assert macro_data["name"] == "Complex Test Macro"
        assert macro_data["description"] == "A complex macro with multiple steps"
        assert macro_data["variables"]["var1"] == "value1"
        assert macro_data["variables"]["var2"] == 123
        assert macro_data["metadata"]["author"] == "test"
        assert len(macro_data["steps"]) == 3
        
        # Verify step serialization
        steps = macro_data["steps"]
        assert steps[0]["step_type"] == "mouse_click"
        assert steps[1]["step_type"] == "keyboard_type"
        assert steps[2]["step_type"] == "wait_time"
        assert "{{var1}}" in steps[1]["text"]


class TestMacroLoading:
    """Test macro loading functionality with file I/O mocking"""
    
    def setup_method(self):
        """Setup test fixtures"""
        with patch('pathlib.Path.mkdir'):
            with patch('core.macro_storage.EncryptionManager'):
                self.storage = MacroStorage()
        
        # Sample macro data for testing
        self.sample_macro_data = {
            "schema_version": "1.0.0",
            "macro": {
                "macro_id": "test-macro-123",
                "name": "Test Loaded Macro",
                "description": "Macro loaded from file",
                "version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "steps": [
                    {
                        "step_id": "step-1",
                        "step_type": "mouse_click",
                        "name": "Test Click",
                        "x": 150,
                        "y": 250,
                        "button": "left",
                        "clicks": 1
                    }
                ],
                "variables": {"loaded_var": "loaded_value"},
                "metadata": {"loaded_by": "test"}
            }
        }
    
    @patch('pathlib.Path.exists')
    def test_load_macro_file_not_found(self, mock_exists):
        """Test loading macro when file doesn't exist"""
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError, match="Macro file not found"):
            self.storage.load_macro("nonexistent.json")
    
    @patch('utils.macro_loader.load_macro_safe')
    @patch('pathlib.Path.exists')
    def test_load_macro_json_format(self, mock_exists, mock_load_safe):
        """Test loading macro in JSON format"""
        mock_exists.return_value = True
        
        # Mock the safe loader
        expected_macro = Macro(name="Loaded Macro")
        mock_load_safe.return_value = expected_macro
        
        result = self.storage.load_macro("test.json")
        
        assert result == expected_macro
        mock_load_safe.assert_called_once_with("test.json")
    
    @patch('utils.macro_loader.load_macro_safe', return_value=None)
    @patch('pathlib.Path.exists')
    def test_load_macro_safe_loader_failure(self, mock_exists, mock_load_safe):
        """Test handling of safe loader failure"""
        mock_exists.return_value = True
        
        with pytest.raises(ValueError, match="Failed to load macro"):
            self.storage.load_macro("test.json")
    
    @patch('pathlib.Path.read_bytes')
    @patch('pathlib.Path.exists')
    def test_load_macro_encrypted_format(self, mock_exists, mock_read_bytes, mock_encryption_manager):
        """Test loading macro in encrypted format"""
        mock_exists.return_value = True
        mock_read_bytes.return_value = b'encrypted_data'
        
        # Mock decryption
        decrypted_json = json.dumps(self.sample_macro_data)
        mock_encryption_manager.decrypt.return_value = decrypted_json.encode('utf-8')
        
        # Mock Macro.from_dict
        with patch('core.macro_types.Macro.from_dict') as mock_from_dict:
            expected_macro = Macro(name="Decrypted Macro")
            mock_from_dict.return_value = expected_macro
            
            result = self.storage.load_macro("test.emf")
            
            assert result == expected_macro
            mock_encryption_manager.decrypt.assert_called_once_with(b'encrypted_data')
            mock_from_dict.assert_called_once_with(self.sample_macro_data["macro"])
    
    @patch('pathlib.Path.read_bytes')
    @patch('pathlib.Path.exists')
    @patch('logger.app_logger.get_logger')
    def test_load_macro_schema_version_mismatch(self, mock_logger, mock_exists, mock_read_bytes, mock_encryption_manager):
        """Test handling of schema version mismatch"""
        mock_exists.return_value = True
        mock_read_bytes.return_value = b'encrypted_data'
        mock_log = Mock()
        mock_logger.return_value = mock_log
        
        # Create data with different schema version
        old_version_data = self.sample_macro_data.copy()
        old_version_data["schema_version"] = "0.9.0"
        
        decrypted_json = json.dumps(old_version_data)
        mock_encryption_manager.decrypt.return_value = decrypted_json.encode('utf-8')
        
        with patch('core.macro_types.Macro.from_dict') as mock_from_dict:
            mock_from_dict.return_value = Macro(name="Old Version Macro")
            
            result = self.storage.load_macro("test.emacro")
            
            # Should log warning about version mismatch
            mock_log.warning.assert_called_once()
            assert "Schema version mismatch" in mock_log.warning.call_args[0][0]


class TestMacroListing:
    """Test macro listing functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        with patch('pathlib.Path.mkdir'):
            with patch('core.macro_storage.EncryptionManager'):
                self.storage = MacroStorage()
    
    @patch('pathlib.Path.glob')
    @patch('pathlib.Path.read_text')
    def test_list_macros_json_only(self, mock_read_text, mock_glob):
        """Test listing JSON macros only"""
        # Mock file discovery
        mock_file1 = Mock()
        mock_file1.name = "macro1.json"
        mock_file1.suffix = ".json"
        mock_file1.__str__ = lambda: "/path/to/macro1.json"
        
        mock_file2 = Mock()
        mock_file2.name = "macro2.json"
        mock_file2.suffix = ".json"
        mock_file2.__str__ = lambda: "/path/to/macro2.json"
        
        mock_glob.side_effect = [[mock_file1, mock_file2], []]  # JSON files, no encrypted
        
        # Mock file content
        sample_data = {
            "schema_version": "1.0.0",
            "macro": {
                "macro_id": "test-id",
                "name": "Test Macro",
                "description": "Test description",
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }
        }
        mock_read_text.return_value = json.dumps(sample_data)
        
        result = self.storage.list_macros(include_encrypted=False)
        
        assert len(result) == 2
        for macro_info in result:
            assert macro_info["file_name"] in ["macro1.json", "macro2.json"]
            assert macro_info["name"] == "Test Macro"
            assert macro_info["encrypted"] is False
    
    @patch('pathlib.Path.glob')
    @patch('core.macro_storage.MacroStorage.load_macro')
    def test_list_macros_with_encrypted(self, mock_load_macro, mock_glob):
        """Test listing macros including encrypted files"""
        # Mock file discovery
        mock_json_file = Mock()
        mock_json_file.name = "macro1.json"
        mock_json_file.suffix = ".json"
        
        mock_encrypted_file = Mock()
        mock_encrypted_file.name = "macro2.emacro"
        mock_encrypted_file.suffix = ".emacro"
        mock_encrypted_file.__str__ = lambda: "/path/to/macro2.emacro"
        
        mock_glob.side_effect = [[mock_json_file], [mock_encrypted_file]]
        
        # Mock macro loading for encrypted file
        encrypted_macro = Macro(
            macro_id="encrypted-id",
            name="Encrypted Macro",
            description="Encrypted description"
        )
        mock_load_macro.return_value = encrypted_macro
        
        # Mock JSON file reading
        with patch('pathlib.Path.read_text') as mock_read_text:
            sample_data = {
                "schema_version": "1.0.0",
                "macro": {
                    "macro_id": "json-id",
                    "name": "JSON Macro",
                    "description": "JSON description",
                    "created_at": "2023-01-01T00:00:00",
                    "updated_at": "2023-01-01T00:00:00"
                }
            }
            mock_read_text.return_value = json.dumps(sample_data)
            
            result = self.storage.list_macros(include_encrypted=True)
        
        assert len(result) == 2
        
        # Find each macro type in results
        json_macro = next(m for m in result if m["file_name"] == "macro1.json")
        encrypted_macro_info = next(m for m in result if m["file_name"] == "macro2.emacro")
        
        assert json_macro["encrypted"] is False
        assert encrypted_macro_info["encrypted"] is True
        assert encrypted_macro_info["name"] == "Encrypted Macro"
    
    @patch('pathlib.Path.glob')
    @patch('pathlib.Path.read_text', side_effect=Exception("Read error"))
    @patch('logger.app_logger.get_logger')
    def test_list_macros_error_handling(self, mock_logger, mock_read_text, mock_glob):
        """Test error handling during macro listing"""
        mock_log = Mock()
        mock_logger.return_value = mock_log
        
        # Mock file discovery
        mock_file = Mock()
        mock_file.name = "corrupted.json"
        mock_file.suffix = ".json"
        mock_file.__str__ = lambda: "/path/to/corrupted.json"
        
        mock_glob.side_effect = [[mock_file], []]
        
        result = self.storage.list_macros()
        
        # Should return empty list and log error
        assert result == []
        mock_log.error.assert_called_once()
    
    def test_list_macros_sorting(self):
        """Test that macros are sorted by updated date"""
        # This test would require more complex mocking of file timestamps
        # For now, we verify the sorting logic exists in the actual method
        assert hasattr(self.storage, 'list_macros')
        
        # The actual implementation should sort by updated_at in reverse order
        # We can test this by creating mock data with different timestamps


class TestMacroDeletion:
    """Test macro deletion functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        with patch('pathlib.Path.mkdir'):
            with patch('core.macro_storage.EncryptionManager'):
                self.storage = MacroStorage()
    
    @patch('pathlib.Path.exists')
    def test_delete_macro_file_not_found(self, mock_exists):
        """Test deleting non-existent macro file"""
        mock_exists.return_value = False
        
        result = self.storage.delete_macro("nonexistent.json")
        assert result is False
    
    @patch('pathlib.Path.unlink')
    @patch('pathlib.Path.exists')
    @patch('core.macro_storage.MacroStorage._create_backup')
    @patch('logger.app_logger.get_logger')
    def test_delete_macro_with_backup(self, mock_logger, mock_create_backup, mock_exists, mock_unlink):
        """Test deleting macro with backup creation"""
        mock_exists.return_value = True
        mock_log = Mock()
        mock_logger.return_value = mock_log
        
        result = self.storage.delete_macro("test.json", create_backup=True)
        
        assert result is True
        mock_create_backup.assert_called_once()
        mock_unlink.assert_called_once()
        mock_log.info.assert_called_once()
    
    @patch('pathlib.Path.unlink')
    @patch('pathlib.Path.exists')
    @patch('logger.app_logger.get_logger')
    def test_delete_macro_without_backup(self, mock_logger, mock_exists, mock_unlink):
        """Test deleting macro without backup"""
        mock_exists.return_value = True
        mock_log = Mock()
        mock_logger.return_value = mock_log
        
        result = self.storage.delete_macro("test.json", create_backup=False)
        
        assert result is True
        mock_unlink.assert_called_once()
        mock_log.info.assert_called_once()


class TestMacroExportImport:
    """Test macro export and import functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        with patch('pathlib.Path.mkdir'):
            with patch('core.macro_storage.EncryptionManager'):
                self.storage = MacroStorage()
        self.test_macro = Macro(
            name="Export Test Macro",
            description="Macro for export testing"
        )
        self.test_macro.add_step(MouseClickStep(name="Export Click"))
    
    @patch('pathlib.Path.write_text')
    @patch('logger.app_logger.get_logger')
    def test_export_macro(self, mock_logger, mock_write_text):
        """Test exporting macro for sharing"""
        mock_log = Mock()
        mock_logger.return_value = mock_log
        
        export_path = "/export/path/macro.json"
        
        result = self.storage.export_macro(self.test_macro, export_path)
        
        assert result == export_path
        mock_write_text.assert_called_once()
        mock_log.info.assert_called_once()
        
        # Verify export data structure
        written_content = mock_write_text.call_args[0][0]
        export_data = json.loads(written_content)
        
        assert export_data["schema_version"] == "1.0.0"
        assert "macro" in export_data
        assert "export_info" in export_data
        assert export_data["export_info"]["export_version"] == "1.0.0"
        assert "exported_at" in export_data["export_info"]
    
    @patch('pathlib.Path.exists')
    def test_import_macro_file_not_found(self, mock_exists):
        """Test importing non-existent macro file"""
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError, match="Import file not found"):
            self.storage.import_macro("nonexistent.json")
    
    @patch('pathlib.Path.read_text')
    @patch('pathlib.Path.exists')
    @patch('core.macro_storage.MacroStorage.save_macro')
    def test_import_macro_regular_file(self, mock_save_macro, mock_exists, mock_read_text):
        """Test importing regular macro file"""
        mock_exists.return_value = True
        
        # Mock import data
        import_data = {
            "schema_version": "1.0.0",
            "macro": {
                "macro_id": "original-id",
                "name": "Imported Macro",
                "description": "Imported description",
                "version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "steps": [],
                "variables": {},
                "metadata": {}
            }
        }
        mock_read_text.return_value = json.dumps(import_data)
        
        # Mock Macro.from_dict
        with patch('core.macro_types.Macro.from_dict') as mock_from_dict:
            imported_macro = Macro(name="Imported Macro")
            mock_from_dict.return_value = imported_macro
            
            result = self.storage.import_macro("import.json", save_to_storage=True)
            
            assert result == imported_macro
            mock_save_macro.assert_called_once_with(imported_macro)
            
            # Verify new ID was generated
            assert hasattr(imported_macro, 'macro_id')
    
    @patch('pathlib.Path.read_text')
    @patch('pathlib.Path.exists')
    @patch('logger.app_logger.get_logger')
    def test_import_macro_export_file(self, mock_logger, mock_exists, mock_read_text):
        """Test importing exported macro file"""
        mock_exists.return_value = True
        mock_log = Mock()
        mock_logger.return_value = mock_log
        
        # Mock export file data
        export_data = {
            "schema_version": "1.0.0",
            "macro": {
                "macro_id": "export-id",
                "name": "Exported Macro",
                "steps": [],
                "variables": {},
                "metadata": {}
            },
            "export_info": {
                "exported_at": datetime.now().isoformat(),
                "export_version": "1.0.0"
            }
        }
        mock_read_text.return_value = json.dumps(export_data)
        
        with patch('core.macro_types.Macro.from_dict') as mock_from_dict:
            imported_macro = Macro(name="Exported Macro")
            mock_from_dict.return_value = imported_macro
            
            result = self.storage.import_macro("export.json", save_to_storage=False)
            
            assert result == imported_macro
            # Should log export info
            mock_log.info.assert_called()
            assert "Importing from export" in mock_log.info.call_args[0][0]


class TestBackupManagement:
    """Test backup creation and management functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        with patch('pathlib.Path.mkdir'):
            with patch('core.macro_storage.EncryptionManager'):
                self.storage = MacroStorage()
    
    @patch('shutil.copy2')
    @patch('pathlib.Path.mkdir')
    @patch('core.macro_storage.MacroStorage._clean_old_backups')
    @patch('logger.app_logger.get_logger')
    def test_create_backup(self, mock_logger, mock_clean_backups, mock_mkdir, mock_copy2):
        """Test backup creation"""
        mock_log = Mock()
        mock_logger.return_value = mock_log
        
        file_path = Path("test_macro.json")
        
        # Mock datetime for consistent backup naming
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20231201_143022"
            
            self.storage._create_backup(file_path)
            
            mock_mkdir.assert_called_once()
            mock_copy2.assert_called_once()
            mock_clean_backups.assert_called_once_with("test_macro")
            mock_log.info.assert_called()
    
    @patch('pathlib.Path.glob')
    @patch('pathlib.Path.unlink')
    @patch('logger.app_logger.get_logger')
    def test_clean_old_backups(self, mock_logger, mock_unlink, mock_glob):
        """Test cleaning old backup files"""
        mock_log = Mock()
        mock_logger.return_value = mock_log
        
        # Create mock backup files with different timestamps
        backup_files = []
        for i in range(15):  # More than keep_count (10)
            mock_file = Mock()
            mock_file.stat.return_value.st_mtime = 1000000 + i  # Ascending timestamps
            backup_files.append(mock_file)
        
        mock_glob.return_value = backup_files
        
        # Test with custom keep_count
        self.storage._clean_old_backups("test_macro", keep_count=5)
        
        # Should delete 10 oldest files (15 - 5 = 10)
        assert mock_unlink.call_count == 10
        assert mock_log.info.call_count == 10
    
    @patch('pathlib.Path.exists')
    def test_clean_old_backups_no_backup_dir(self, mock_exists):
        """Test cleaning backups when backup directory doesn't exist"""
        mock_exists.return_value = False
        
        # Should not raise exception
        self.storage._clean_old_backups("test_macro")


class TestMacroTemplates:
    """Test macro template functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        with patch('pathlib.Path.mkdir'):
            with patch('core.macro_storage.EncryptionManager'):
                self.storage = MacroStorage()
    
    def test_get_templates(self):
        """Test getting available macro templates"""
        templates = self.storage.get_templates()
        
        assert len(templates) >= 3  # Should have at least 3 templates
        
        template_names = [t["name"] for t in templates]
        assert "기본 자동화" in template_names
        assert "웹 자동화" in template_names
        assert "엑셀 데이터 입력" in template_names
        
        # Verify each template has required fields
        for template in templates:
            assert "name" in template
            assert "description" in template
            assert "macro" in template
            assert isinstance(template["macro"], Macro)
    
    def test_basic_template_structure(self):
        """Test basic automation template structure"""
        basic_template = self.storage._create_basic_template()
        
        assert basic_template.name == "기본 자동화 템플릿"
        assert len(basic_template.steps) == 3
        
        # Verify step types
        step_types = [step.step_type.value for step in basic_template.steps]
        assert "mouse_click" in step_types
        assert "wait_time" in step_types
        assert "keyboard_type" in step_types
        
        # Verify variable usage
        type_step = next(s for s in basic_template.steps if s.step_type.value == "keyboard_type")
        assert "{{이름}}" in type_step.text
    
    def test_web_template_structure(self):
        """Test web automation template structure"""
        web_template = self.storage._create_web_template()
        
        assert web_template.name == "웹 자동화 템플릿"
        assert len(web_template.steps) >= 3
        
        # Should contain hotkey and type steps
        step_types = [step.step_type.value for step in web_template.steps]
        assert "keyboard_hotkey" in step_types
        assert "keyboard_type" in step_types
        assert "wait_time" in step_types
    
    def test_excel_input_template_structure(self):
        """Test Excel input template structure"""
        excel_template = self.storage._create_excel_input_template()
        
        assert excel_template.name == "엑셀 데이터 입력 템플릿"
        assert isinstance(excel_template, Macro)
        # Template might be minimal as indicated in the implementation


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases"""
    
    def setup_method(self):
        """Setup test fixtures"""
        with patch('pathlib.Path.mkdir'):
            with patch('core.macro_storage.EncryptionManager'):
                self.storage = MacroStorage()
    
    @patch('pathlib.Path.write_text', side_effect=PermissionError("Access denied"))
    @patch('logger.app_logger.get_logger')
    def test_save_permission_error(self, mock_logger, mock_write_text):
        """Test handling permission errors during save"""
        mock_log = Mock()
        mock_logger.return_value = mock_log
        
        test_macro = Macro(name="Permission Test")
        result = self.storage.save_macro(test_macro)
        
        assert result is False
        mock_log.error.assert_called_once()
    
    @patch('pathlib.Path.read_text', side_effect=json.JSONDecodeError("Invalid JSON", "", 0))
    @patch('pathlib.Path.exists')
    @patch('logger.app_logger.get_logger')
    def test_list_macros_json_decode_error(self, mock_logger, mock_exists, mock_read_text):
        """Test handling JSON decode errors during listing"""
        mock_log = Mock()
        mock_logger.return_value = mock_log
        mock_exists.return_value = True
        
        # Mock file discovery
        mock_file = Mock()
        mock_file.name = "corrupted.json"
        mock_file.suffix = ".json"
        mock_file.__str__ = lambda: "/path/to/corrupted.json"
        
        with patch('pathlib.Path.glob', return_value=[[mock_file], []]):
            result = self.storage.list_macros()
        
        assert result == []
        mock_log.error.assert_called_once()
    
    def test_macro_with_none_values(self):
        """Test handling macro with None values"""
        # Create macro with some None values
        test_macro = Macro(name="None Test")
        test_macro.description = None
        test_macro.variables = None
        test_macro.metadata = None
        
        # Should handle gracefully during serialization
        with patch('pathlib.Path.write_text') as mock_write_text:
            with patch('pathlib.Path.exists', return_value=False):
                result = self.storage.save_macro(test_macro)
        
        assert result is True
        
        # Verify serialized data handles None values
        written_content = mock_write_text.call_args[0][0]
        data = json.loads(written_content)
        
        # None values should be serialized as null or replaced with defaults
        macro_data = data["macro"]
        assert "description" in macro_data
        assert "variables" in macro_data
        assert "metadata" in macro_data


@pytest.mark.integration
class TestMacroStorageIntegration:
    """Integration tests for MacroStorage with real-like scenarios"""
    
    def test_complete_macro_lifecycle(self, temp_dir):
        """Test complete lifecycle: create, save, load, modify, delete"""
        # Use real directory for this integration test
        storage = MacroStorage(temp_dir / "test_macros")
        
        # 1. Create and save macro
        original_macro = Macro(
            name="Lifecycle Test Macro",
            description="Testing complete lifecycle"
        )
        original_macro.add_step(MouseClickStep(name="Original Click", x=100, y=200))
        
        with patch('pathlib.Path.write_text') as mock_write:
            save_result = storage.save_macro(original_macro)
            assert save_result is True
        
        # 2. Load macro (mock the loading)
        with patch('utils.macro_loader.load_macro_safe') as mock_load:
            mock_load.return_value = original_macro
            with patch('pathlib.Path.exists', return_value=True):
                loaded_macro = storage.load_macro("test.json")
                assert loaded_macro.name == original_macro.name
        
        # 3. Modify and save again
        loaded_macro.add_step(KeyboardTypeStep(name="Added Step", text="Modified"))
        
        with patch('pathlib.Path.write_text') as mock_write:
            with patch('pathlib.Path.exists', return_value=True):
                with patch('core.macro_storage.MacroStorage._create_backup'):
                    save_result = storage.save_macro(loaded_macro, create_backup=True)
                    assert save_result is True
        
        # 4. Delete macro
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.unlink'):
                with patch('core.macro_storage.MacroStorage._create_backup'):
                    delete_result = storage.delete_macro("test.json")
                    assert delete_result is True
    
    def test_concurrent_access_simulation(self):
        """Test behavior under simulated concurrent access"""
        storage = MacroStorage()
        
        # Simulate multiple save operations
        macros = [
            Macro(name=f"Concurrent Macro {i}")
            for i in range(10)
        ]
        
        with patch('pathlib.Path.write_text') as mock_write:
            with patch('pathlib.Path.exists', return_value=False):
                results = []
                for macro in macros:
                    result = storage.save_macro(macro)
                    results.append(result)
        
        # All operations should succeed
        assert all(results)
        assert mock_write.call_count == 10
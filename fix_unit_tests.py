"""
Quick fix script for unit test issues
"""

import re
import os
from pathlib import Path

def fix_test_file(file_path):
    """Fix common test issues in a file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix 1: MacroStorage setup_method without proper mocking
    content = re.sub(
        r'def setup_method\(self\):\s*\n\s*"""Setup test fixtures"""\s*\n\s*self\.storage = MacroStorage\(\)',
        '''def setup_method(self):
        """Setup test fixtures"""
        with patch('pathlib.Path.mkdir'):
            with patch('core.macro_storage.EncryptionManager') as mock_enc:
                mock_enc.return_value = Mock()
                self.storage = MacroStorage()''',
        content
    )
    
    # Fix 2: Add missing mock for encrypted format test
    content = re.sub(
        r'def test_save_macro_encrypted_format\(self, mock_exists, mock_write_bytes, mock_encryption_manager\):',
        'def test_save_macro_encrypted_format(self, mock_exists, mock_write_bytes):',
        content
    )
    
    # Fix 3: Replace mock_encryption_manager with self.storage.encryption_manager
    content = re.sub(
        r'mock_encryption_manager\.encrypt',
        'self.storage.encryption_manager.encrypt',
        content
    )
    
    # Fix 4: Fix load_macro_json_format test
    content = re.sub(
        r'@patch\(\'pathlib\.Path\.read_text\'\)\s*\n\s*def test_load_macro_json_format',
        '''@patch('core.macro_storage.load_macro_safe')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.suffix', new_callable=lambda: Mock(return_value='.json'))
    def test_load_macro_json_format''',
        content
    )
    
    # Fix 5: Fix save_macro_error_handling test
    content = re.sub(
        r'mock_write_text\.side_effect = OSError\("Permission denied"\)',
        '''mock_write_text.side_effect = OSError("Permission denied")
        # Ensure storage has encryption manager
        if not hasattr(self.storage, 'encryption_manager'):
            self.storage.encryption_manager = Mock()''',
        content
    )
    
    # Fix 6: Fix list_macros tests
    content = re.sub(
        r'mock_iterdir\.return_value = \[',
        '''# Ensure we have proper Path objects
        mock_iterdir.return_value = [''',
        content
    )
    
    # Fix 7: Fix Excel manager tests
    if 'test_excel_manager.py' in str(file_path):
        content = re.sub(
            r'def setup_method\(self\):\s*\n\s*"""Setup test fixtures"""\s*\n\s*self\.excel_manager = ExcelManager\(\)',
            '''def setup_method(self):
        """Setup test fixtures"""
        with patch('pathlib.Path.mkdir'):
            self.excel_manager = ExcelManager()''',
            content
        )
        
        # Fix load_file_success test
        content = re.sub(
            r'mock_path\.suffix = "\.xlsx"',
            'mock_path.suffix = ".xlsx"\n        mock_path.exists.return_value = True',
            content
        )
    
    # Fix 8: Fix encryption tests
    if 'test_encryption.py' in str(file_path):
        content = re.sub(
            r'@patch\(\'os\.chmod\'\)\s*\n\s*def test_key_file_permissions',
            '''@patch('platform.system', return_value='Linux')
    @patch('os.chmod')
    def test_key_file_permissions''',
            content
        )
    
    # Save if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed: {file_path}")
        return True
    return False

def main():
    """Fix all unit test files"""
    test_dirs = [
        'tests/unit/core',
        'tests/unit/excel', 
        'tests/unit/utils'
    ]
    
    fixed_count = 0
    for test_dir in test_dirs:
        test_path = Path(test_dir)
        if test_path.exists():
            for test_file in test_path.glob('test_*.py'):
                if fix_test_file(test_file):
                    fixed_count += 1
    
    print(f"\nFixed {fixed_count} test files")

if __name__ == "__main__":
    main()
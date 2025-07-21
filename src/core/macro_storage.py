"""
Macro storage and JSON serialization
"""

import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import shutil
from enum import Enum
from utils.encryption import EncryptionManager
from logger.app_logger import get_logger
from core.macro_types import Macro
from utils.macro_loader import load_macro_safe, save_macro_safe


class MacroFormat(Enum):
    """Supported macro file formats"""
    JSON = "json"
    ENCRYPTED = "encrypted"

class MacroStorage:
    """Handles macro storage, loading, and saving"""
    
    SCHEMA_VERSION = "1.0.0"
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """Initialize macro storage"""
        self.logger = get_logger(__name__)
        self.storage_dir = storage_dir or Path.home() / ".excel_macro_automation" / "macros"
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.logger.warning(f"Could not create storage directory: {e}")
            # Use temp directory as fallback
            import tempfile
            self.storage_dir = Path(tempfile.gettempdir()) / "excel_macro_automation" / "macros"
            self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.encryption_manager = EncryptionManager()
        
    def save_macro(self, macro: Macro, file_path: Optional[str] = None, 
                   format: str = "json", create_backup: bool = True) -> bool:
        """Save macro to file"""
        if not file_path:
            file_name = f"{macro.name.replace(' ', '_')}_{macro.macro_id[:8]}.json"
            file_path = self.storage_dir / file_name
        else:
            file_path = Path(file_path)
        
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
            
        # Create backup if requested and file exists
        if create_backup and file_path.exists():
            try:
                self._create_backup(file_path)
            except Exception as e:
                self.logger.warning(f"Could not create backup: {e}")
            
        # Prepare data
        data = {
            "schema_version": self.SCHEMA_VERSION,
            "macro": macro.to_dict()
        }
        
        # Convert to JSON
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        
        # Save file
        try:
            if format == "encrypted" or format == "emf":
                encrypted_data = self.encryption_manager.encrypt(json_str.encode('utf-8'))
                file_path = file_path.with_suffix('.emf')
                file_path.write_bytes(encrypted_data)
                self.logger.info(f"Saved encrypted macro: {file_path}")
            else:
                file_path.write_text(json_str, encoding='utf-8')
                self.logger.info(f"Saved macro: {file_path}")
                
            return True
        except Exception as e:
            self.logger.error(f"Failed to save macro: {e}")
            return False
        
    def load_macro(self, file_path: str) -> Macro:
        """Load macro from file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Macro file not found: {file_path}")
            
        # Check if encrypted
        if file_path.suffix in ['.emacro', '.emf']:
            encrypted_data = file_path.read_bytes()
            json_data = self.encryption_manager.decrypt(encrypted_data).decode('utf-8')
            data = json.loads(json_data)
            
            # Check schema version
            schema_version = data.get("schema_version", "0.0.0")
            if schema_version != self.SCHEMA_VERSION:
                self.logger.warning(f"Schema version mismatch: {schema_version} != {self.SCHEMA_VERSION}")
                
            # Load macro
            macro_data = data.get("macro", {})
            macro = Macro.from_dict(macro_data)
            
            self.logger.info(f"Loaded macro: {macro.name} from {file_path}")
            return macro
        else:
            # Load JSON file with schema check
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check if it's our format with schema
                if "schema_version" in data and "macro" in data:
                    macro_data = data["macro"]
                    macro = Macro.from_dict(macro_data)
                else:
                    # Legacy format - use safe loader
                    macro = load_macro_safe(str(file_path))
                    if not macro:
                        raise ValueError(f"Failed to load macro from {file_path}")
                
                self.logger.info(f"Loaded macro: {macro.name} from {file_path}")
                return macro
            except Exception as e:
                # Fallback to safe loader
                self.logger.warning(f"Standard load failed, trying safe loader: {e}")
                macro = load_macro_safe(str(file_path))
                if not macro:
                    raise ValueError(f"Failed to load macro from {file_path}")
                return macro
        
    def list_macros(self, include_encrypted: bool = True) -> List[Dict[str, Any]]:
        """List all saved macros"""
        macros = []
        
        # Search for macro files
        patterns = ['*.json']
        if include_encrypted:
            patterns.append('*.emacro')
            
        for pattern in patterns:
            for file_path in self.storage_dir.glob(pattern):
                try:
                    # Get basic info without fully loading
                    if file_path.suffix == '.emacro':
                        # For encrypted files, we need to decrypt to get info
                        macro = self.load_macro(str(file_path))
                        info = {
                            "file_path": str(file_path),
                            "file_name": file_path.name,
                            "macro_id": macro.macro_id,
                            "name": macro.name,
                            "description": macro.description,
                            "created_at": macro.created_at.isoformat(),
                            "updated_at": macro.updated_at.isoformat(),
                            "encrypted": True
                        }
                    else:
                        # For JSON files, we can peek without full parsing
                        data = json.loads(file_path.read_text(encoding='utf-8'))
                        macro_data = data.get("macro", {})
                        info = {
                            "file_path": str(file_path),
                            "file_name": file_path.name,
                            "macro_id": macro_data.get("macro_id", ""),
                            "name": macro_data.get("name", ""),
                            "description": macro_data.get("description", ""),
                            "created_at": macro_data.get("created_at", ""),
                            "updated_at": macro_data.get("updated_at", ""),
                            "encrypted": False
                        }
                    macros.append(info)
                except Exception as e:
                    self.logger.error(f"Failed to read macro file {file_path}: {e}")
                    
        # Sort by updated date
        macros.sort(key=lambda x: x["updated_at"], reverse=True)
        return macros
        
    def delete_macro(self, file_path: str, create_backup: bool = True) -> bool:
        """Delete a macro file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return False
            
        if create_backup:
            self._create_backup(file_path)
            
        file_path.unlink()
        self.logger.info(f"Deleted macro: {file_path}")
        return True
        
    def export_macro(self, macro: Macro, export_path: str) -> str:
        """Export macro for sharing"""
        export_path = Path(export_path)
        
        # Always export as unencrypted JSON for sharing
        data = {
            "schema_version": self.SCHEMA_VERSION,
            "macro": macro.to_dict(),
            "export_info": {
                "exported_at": datetime.now().isoformat(),
                "export_version": "1.0.0"
            }
        }
        
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        export_path.write_text(json_str, encoding='utf-8')
        
        self.logger.info(f"Exported macro: {export_path}")
        return str(export_path)
        
    def import_macro(self, import_path: str, save_to_storage: bool = True) -> Macro:
        """Import macro from external file"""
        import_path = Path(import_path)
        
        if not import_path.exists():
            raise FileNotFoundError(f"Import file not found: {import_path}")
            
        # Load the macro
        data = json.loads(import_path.read_text(encoding='utf-8'))
        
        # Check if it's an export file
        if "export_info" in data:
            self.logger.info(f"Importing from export: {data['export_info']}")
            
        macro_data = data.get("macro", {})
        macro = Macro.from_dict(macro_data)
        
        # Generate new ID to avoid conflicts
        import uuid
        macro.macro_id = str(uuid.uuid4())
        macro.updated_at = datetime.now()
        
        # Save to storage if requested
        if save_to_storage:
            self.save_macro(macro)
            
        self.logger.info(f"Imported macro: {macro.name}")
        return macro
        
    def _create_backup(self, file_path: Path):
        """Create backup of file"""
        try:
            backup_dir = self.storage_dir / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
            backup_path = backup_dir / backup_name
            
            shutil.copy2(file_path, backup_path)
            self.logger.info(f"Created backup: {backup_path}")
            
            # Clean old backups (keep last 10)
            self._clean_old_backups(file_path.stem)
        except Exception as e:
            self.logger.warning(f"Backup creation failed: {e}")
        
    def _clean_old_backups(self, file_stem: str, keep_count: int = 10):
        """Clean old backup files"""
        backup_dir = self.storage_dir / "backups"
        if not backup_dir.exists():
            return
            
        # Find all backups for this file
        backups = list(backup_dir.glob(f"{file_stem}_backup_*"))
        backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Delete old backups
        for backup in backups[keep_count:]:
            backup.unlink()
            self.logger.info(f"Deleted old backup: {backup}")
            
    def get_templates(self) -> List[Dict[str, Any]]:
        """Get available macro templates"""
        templates = [
            {
                "name": "기본 자동화",
                "description": "마우스 클릭과 텍스트 입력을 포함한 기본 템플릿",
                "macro": self._create_basic_template()
            },
            {
                "name": "웹 자동화",
                "description": "웹 브라우저 자동화를 위한 템플릿",
                "macro": self._create_web_template()
            },
            {
                "name": "엑셀 데이터 입력",
                "description": "엑셀 데이터를 다른 프로그램에 입력하는 템플릿",
                "macro": self._create_excel_input_template()
            }
        ]
        return templates
        
    def _create_basic_template(self) -> Macro:
        """Create basic automation template"""
        from core.macro_types import MouseClickStep, WaitTimeStep, KeyboardTypeStep
        
        macro = Macro(name="기본 자동화 템플릿")
        
        # Add sample steps
        click_step = MouseClickStep(
            name="프로그램 클릭",
            description="자동화할 프로그램을 클릭합니다"
        )
        macro.add_step(click_step)
        
        wait_step = WaitTimeStep(
            name="대기",
            description="프로그램이 준비될 때까지 대기",
            seconds=2.0
        )
        macro.add_step(wait_step)
        
        type_step = KeyboardTypeStep(
            name="텍스트 입력",
            description="입력할 텍스트",
            text="{{이름}}"
        )
        macro.add_step(type_step)
        
        return macro
        
    def _create_web_template(self) -> Macro:
        """Create web automation template"""
        from core.macro_types import WaitTimeStep, KeyboardHotkeyStep, KeyboardTypeStep
        
        macro = Macro(name="웹 자동화 템플릿")
        
        # Open browser
        hotkey_step = KeyboardHotkeyStep(
            name="브라우저 열기",
            description="웹 브라우저를 엽니다",
            keys=["win", "r"]
        )
        macro.add_step(hotkey_step)
        
        wait_step = WaitTimeStep(seconds=1.0)
        macro.add_step(wait_step)
        
        type_step = KeyboardTypeStep(
            name="브라우저 실행",
            text="chrome"
        )
        macro.add_step(type_step)
        
        return macro
        
    def _create_excel_input_template(self) -> Macro:
        """Create Excel input template"""
        from core.macro_types import LoopStep, KeyboardTypeStep, KeyboardHotkeyStep
        
        macro = Macro(name="엑셀 데이터 입력 템플릿")
        
        # This is a placeholder - would need proper implementation
        # with Excel row iteration
        
        return macro
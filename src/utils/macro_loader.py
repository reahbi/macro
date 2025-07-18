"""
Safe macro loading utilities for Windows environment
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
import chardet
from core.macro_types import Macro, StepFactory, StepType
from logger.app_logger import get_logger

logger = get_logger(__name__)

def detect_file_encoding(file_path: str) -> str:
    """Detect file encoding"""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            confidence = result['confidence']
            
            # Use UTF-8 if confidence is low
            if confidence < 0.7:
                encoding = 'utf-8'
                
            return encoding or 'utf-8'
    except Exception as e:
        logger.warning(f"Failed to detect encoding: {e}")
        return 'utf-8'

def sanitize_string(text: str) -> str:
    """Remove invalid characters from string"""
    if not text:
        return ""
    
    # Remove non-printable characters except newlines and tabs
    cleaned = ''.join(c for c in text if ord(c) >= 32 or c in '\n\r\t')
    return cleaned

def fix_step_data(step_data: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Fix common step data issues"""
    step_type = step_data.get('step_type', 'unknown')
    
    # Fix step name
    step_name = step_data.get('name', '')
    if not step_name or step_name != sanitize_string(step_name):
        default_names = {
            'mouse_click': '마우스 클릭',
            'mouse_move': '마우스 이동',
            'keyboard_type': '텍스트 입력',
            'wait_time': '대기',
            'image_search': '이미지 검색',
            'ocr_text': '텍스트 검색',
            'if_condition': '조건문',
            'loop': '반복문'
        }
        step_data['name'] = default_names.get(step_type, f'단계 {index + 1}')
        logger.info(f"Fixed step name: '{step_name}' -> '{step_data['name']}'")
    
    # Fix description
    if 'description' in step_data:
        desc = step_data['description']
        if isinstance(desc, str):
            step_data['description'] = sanitize_string(desc)
    
    # Fix keyboard_type empty text
    if step_type == 'keyboard_type':
        text = step_data.get('text', '')
        if not text or not text.strip():
            step_data['text'] = ' '  # Single space as placeholder
            logger.info(f"Fixed empty text in keyboard_type step")
        else:
            step_data['text'] = sanitize_string(text)
    
    # Fix wait_time
    if step_type == 'wait_time':
        wait_time = step_data.get('wait_time', 0)
        if not isinstance(wait_time, (int, float)) or wait_time <= 0:
            step_data['wait_time'] = 1.0
            logger.info(f"Fixed invalid wait_time: {wait_time} -> 1.0")
    
    # Ensure enabled field exists
    if 'enabled' not in step_data:
        step_data['enabled'] = True
    
    return step_data

def load_macro_safe(file_path: str) -> Optional[Macro]:
    """Safely load macro from file with error handling"""
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"Macro file not found: {file_path}")
            return None
        
        # Detect encoding
        encoding = detect_file_encoding(str(file_path))
        logger.info(f"Loading macro with {encoding} encoding")
        
        # Load JSON with error handling
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            macro_data = json.load(f)
        
        # Fix macro name
        macro_name = macro_data.get('name', '')
        if not macro_name or macro_name != sanitize_string(macro_name):
            macro_data['name'] = file_path.stem  # Use filename without extension
            logger.info(f"Fixed macro name: '{macro_name}' -> '{macro_data['name']}'")
        
        # Fix macro description
        if 'description' in macro_data:
            macro_data['description'] = sanitize_string(macro_data.get('description', ''))
        
        # Fix each step
        steps = macro_data.get('steps', [])
        for i, step_data in enumerate(steps):
            macro_data['steps'][i] = fix_step_data(step_data, i)
        
        # Create macro object
        try:
            macro = Macro.from_dict(macro_data)
            
            # Validate macro
            errors = macro.validate()
            if errors:
                logger.warning(f"Macro validation warnings: {errors}")
                # Don't fail on warnings, just log them
            
            return macro
            
        except Exception as e:
            logger.error(f"Failed to create macro object: {e}")
            
            # Try to create a minimal working macro
            macro = Macro(name=macro_data.get('name', 'Recovery Macro'))
            
            # Add only valid steps
            for i, step_data in enumerate(macro_data.get('steps', [])):
                try:
                    step = StepFactory.from_dict(step_data)
                    if not step.validate():  # Only add if no validation errors
                        macro.add_step(step)
                except Exception as step_error:
                    logger.warning(f"Skipping invalid step {i+1}: {step_error}")
            
            if len(macro.steps) > 0:
                return macro
            else:
                logger.error("No valid steps could be recovered")
                return None
            
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in macro file: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error loading macro: {e}")
        import traceback
        traceback.print_exc()
        return None

def save_macro_safe(macro: Macro, file_path: str) -> bool:
    """Safely save macro to file"""
    try:
        file_path = Path(file_path)
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict
        macro_data = macro.to_dict()
        
        # Save with UTF-8 encoding
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(macro_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Macro saved successfully: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save macro: {e}")
        return False
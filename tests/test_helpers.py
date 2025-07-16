"""
Test helper classes for GUI automation testing
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from PyQt5.QtCore import Qt, QMimeData, QPoint, QByteArray, QDataStream, QIODevice
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QDragMoveEvent
from PyQt5.QtWidgets import QWidget, QDialog, QPushButton, QApplication
import time
import csv
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class MockDragDropEvent:
    """Helper class to simulate drag and drop events"""
    
    @staticmethod
    def create_drag_enter_event(mime_data: QMimeData, pos: QPoint = None) -> QDragEnterEvent:
        """Create a drag enter event"""
        if pos is None:
            pos = QPoint(50, 50)
        
        event = QDragEnterEvent(
            pos,
            Qt.CopyAction | Qt.MoveAction,
            mime_data,
            Qt.LeftButton,
            Qt.NoModifier
        )
        return event
    
    @staticmethod
    def create_drop_event(mime_data: QMimeData, pos: QPoint = None) -> QDropEvent:
        """Create a drop event"""
        if pos is None:
            pos = QPoint(50, 50)
            
        event = QDropEvent(
            pos,
            Qt.CopyAction | Qt.MoveAction,
            mime_data,
            Qt.LeftButton,
            Qt.NoModifier
        )
        return event
    
    @staticmethod
    def create_step_mime_data(step_type: str) -> QMimeData:
        """Create mime data for a new step from palette"""
        mime_data = QMimeData()
        byte_array = QByteArray()
        stream = QDataStream(byte_array, QIODevice.WriteOnly)
        stream.writeQString(step_type)
        mime_data.setData("application/x-steptype", byte_array)
        return mime_data
    
    @staticmethod
    def create_move_mime_data(step_id: str, old_index: int) -> QMimeData:
        """Create mime data for moving an existing step"""
        mime_data = QMimeData()
        byte_array = QByteArray()
        stream = QDataStream(byte_array, QIODevice.WriteOnly)
        stream.writeQString(step_id)
        stream.writeInt(old_index)
        mime_data.setData("application/x-macrostep", byte_array)
        return mime_data


class DialogTester:
    """Helper class to test dialogs automatically"""
    
    def __init__(self, app: QApplication):
        self.app = app
        self.dialog = None
        self.result = None
        
    def test_dialog(self, dialog_class, *args, **kwargs):
        """Test a dialog by creating it and interacting with it"""
        self.dialog = dialog_class(*args, **kwargs)
        self.dialog.show()
        return self
        
    def click_button(self, button_text: str):
        """Click a button by its text"""
        buttons = self.dialog.findChildren(QPushButton)
        for button in buttons:
            if button.text() == button_text:
                button.click()
                self.app.processEvents()
                break
        return self
        
    def set_field(self, field_name: str, value: Any):
        """Set a field value by its object name"""
        widget = self.dialog.findChild(QWidget, field_name)
        if widget:
            if hasattr(widget, 'setText'):
                widget.setText(str(value))
            elif hasattr(widget, 'setValue'):
                widget.setValue(value)
            elif hasattr(widget, 'setCurrentText'):
                widget.setCurrentText(str(value))
            self.app.processEvents()
        return self
        
    def accept(self):
        """Accept the dialog"""
        self.dialog.accept()
        self.result = self.dialog.result()
        self.app.processEvents()
        return self
        
    def reject(self):
        """Reject the dialog"""
        self.dialog.reject()
        self.result = self.dialog.result()
        self.app.processEvents()
        return self
        
    def get_result(self) -> Any:
        """Get the dialog result"""
        return self.result


class LogVerifier:
    """Helper class to verify execution logs"""
    
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.entries = []
        self.load_log()
        
    def load_log(self):
        """Load log entries from CSV file"""
        if not self.log_file.exists():
            return
            
        with open(self.log_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.entries = list(reader)
            
    def verify_step_executed(self, step_name: str, expected_status: str = "SUCCESS") -> bool:
        """Verify a step was executed with expected status"""
        for entry in self.entries:
            if entry.get('step_name') == step_name and entry.get('status') == expected_status:
                return True
        return False
        
    def verify_row_completed(self, row_index: int, expected_status: str = "SUCCESS") -> bool:
        """Verify a row was completed with expected status"""
        for entry in self.entries:
            if (entry.get('row_index') == str(row_index) and 
                entry.get('step_name') == 'ROW_COMPLETE' and 
                entry.get('status') == expected_status):
                return True
        return False
        
    def get_step_duration(self, step_name: str) -> Optional[float]:
        """Get duration of a step execution"""
        for entry in self.entries:
            if entry.get('step_name') == step_name and entry.get('duration_ms'):
                return float(entry['duration_ms'])
        return None
        
    def get_error_messages(self) -> List[str]:
        """Get all error messages from log"""
        errors = []
        for entry in self.entries:
            if entry.get('status') in ['FAILED', 'ERROR'] and entry.get('error_message'):
                errors.append(entry['error_message'])
        return errors
        
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get execution summary statistics"""
        total_rows = 0
        successful_rows = 0
        failed_rows = 0
        total_steps = 0
        successful_steps = 0
        failed_steps = 0
        
        for entry in self.entries:
            if entry.get('step_name') == 'ROW_COMPLETE':
                total_rows += 1
                if entry.get('status') == 'SUCCESS':
                    successful_rows += 1
                else:
                    failed_rows += 1
            elif entry.get('step_type') and entry.get('status'):
                total_steps += 1
                if entry.get('status') == 'SUCCESS':
                    successful_steps += 1
                else:
                    failed_steps += 1
                    
        return {
            'total_rows': total_rows,
            'successful_rows': successful_rows,
            'failed_rows': failed_rows,
            'success_rate': (successful_rows / total_rows * 100) if total_rows > 0 else 0,
            'total_steps': total_steps,
            'successful_steps': successful_steps,
            'failed_steps': failed_steps,
            'step_success_rate': (successful_steps / total_steps * 100) if total_steps > 0 else 0
        }
        
    def wait_for_entry(self, condition_func, timeout: float = 5.0) -> bool:
        """Wait for a log entry matching condition"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            self.load_log()  # Reload log
            for entry in self.entries:
                if condition_func(entry):
                    return True
            time.sleep(0.1)
            
        return False


class TestScenario:
    """Base class for test scenarios"""
    
    def __init__(self, name: str):
        self.name = name
        self.steps = []
        self.expected_results = []
        
    def add_step(self, description: str, action: callable, expected_result: Any = None):
        """Add a test step"""
        self.steps.append({
            'description': description,
            'action': action,
            'expected_result': expected_result
        })
        return self
        
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the test scenario"""
        results = {
            'scenario': self.name,
            'start_time': datetime.now(),
            'steps': [],
            'success': True
        }
        
        for i, step in enumerate(self.steps):
            step_result = {
                'index': i,
                'description': step['description'],
                'start_time': datetime.now()
            }
            
            try:
                # Execute action
                actual_result = step['action'](context)
                step_result['actual_result'] = actual_result
                
                # Verify result if expected
                if step['expected_result'] is not None:
                    step_result['expected_result'] = step['expected_result']
                    step_result['passed'] = actual_result == step['expected_result']
                else:
                    step_result['passed'] = True
                    
            except Exception as e:
                step_result['error'] = str(e)
                step_result['passed'] = False
                results['success'] = False
                
            step_result['end_time'] = datetime.now()
            step_result['duration'] = (step_result['end_time'] - step_result['start_time']).total_seconds()
            
            results['steps'].append(step_result)
            
            if not step_result['passed']:
                results['success'] = False
                break  # Stop on first failure
                
        results['end_time'] = datetime.now()
        results['duration'] = (results['end_time'] - results['start_time']).total_seconds()
        
        return results


class GUITestContext:
    """Context manager for GUI tests"""
    
    def __init__(self, app: QApplication):
        self.app = app
        self.widgets = {}
        self.dialogs = []
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clean up dialogs
        for dialog in self.dialogs:
            if dialog and dialog.isVisible():
                dialog.close()
                
    def register_widget(self, name: str, widget: QWidget):
        """Register a widget for later access"""
        self.widgets[name] = widget
        
    def get_widget(self, name: str) -> Optional[QWidget]:
        """Get a registered widget"""
        return self.widgets.get(name)
        
    def process_events(self, duration_ms: int = 100):
        """Process Qt events for a duration"""
        start = time.time()
        while (time.time() - start) * 1000 < duration_ms:
            self.app.processEvents()
            time.sleep(0.01)
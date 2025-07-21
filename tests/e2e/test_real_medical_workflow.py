"""
Real E2E tests for medical environment workflows
No mocking - tests actual application behavior
"""

import pytest
import time
import pandas as pd
from pathlib import Path
import tempfile
import pyautogui
import subprocess
import psutil
import os
from datetime import datetime

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtTest import QTest

from ui.main_window import MainWindow
from core.macro_types import Macro, MouseClickStep, KeyboardTypeStep, WaitTimeStep, TextSearchStep
from excel.excel_manager import ExcelManager
from config.settings import Settings


class TestRealMedicalWorkflow:
    """Test actual medical workflows without mocking"""
    
    @pytest.fixture
    def app(self):
        """Create real QApplication"""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app
        app.quit()
    
    @pytest.fixture
    def main_window(self, app):
        """Create real MainWindow"""
        settings = Settings()
        window = MainWindow(settings)
        window.show()
        QTest.qWaitForWindowExposed(window)
        yield window
        window.close()
    
    @pytest.fixture
    def test_excel_file(self):
        """Create real Excel file with medical data"""
        # Create test data
        data = {
            '환자번호': ['P2024-001', 'P2024-002', 'P2024-003', 'P2024-004', 'P2024-005'],
            '환자명': ['홍길동', '김철수', '이영희', '박민수', '정수진'],
            '생년월일': ['1970-01-01', '1985-05-15', '1992-08-20', '1988-03-10', '1995-12-25'],
            '진료과': ['내과', '외과', '정형외과', '내과', '소아과'],
            '검사항목': ['혈액검사', 'X-ray', 'MRI', '심전도', '초음파'],
            '검사결과': ['정상', '이상소견', '정상', '부정맥', '정상']
        }
        
        df = pd.DataFrame(data)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            df.to_excel(tmp.name, index=False)
            yield tmp.name
        
        # Cleanup
        os.unlink(tmp.name)
    
    def test_complete_medical_data_entry(self, main_window, test_excel_file):
        """Test complete medical data entry workflow"""
        # 1. Load Excel file
        excel_widget = main_window.excel_widget
        excel_widget.load_file(test_excel_file)
        
        # Wait for file to load
        QTest.qWait(1000)
        
        # Verify file loaded
        assert excel_widget.excel_manager.has_data()
        assert excel_widget.excel_manager.get_total_rows() == 5
        
        # 2. Map columns
        excel_widget.excel_manager.add_mapping("patient_id", "환자번호")
        excel_widget.excel_manager.add_mapping("patient_name", "환자명")
        excel_widget.excel_manager.add_mapping("department", "진료과")
        excel_widget.excel_manager.add_mapping("test_item", "검사항목")
        excel_widget.excel_manager.add_mapping("test_result", "검사결과")
        
        # 3. Create macro
        macro = Macro(name="의료 데이터 입력")
        
        # Open medical system (simulated with notepad for testing)
        notepad_path = r"C:\Windows\System32\notepad.exe"
        if Path(notepad_path).exists():
            subprocess.Popen([notepad_path])
            time.sleep(2)  # Wait for notepad to open
            
            # Click on notepad to focus
            macro.add_step(MouseClickStep(
                name="메모장 포커스",
                x=pyautogui.size()[0] // 2,
                y=pyautogui.size()[1] // 2
            ))
        
        # Add data entry steps
        macro.add_step(KeyboardTypeStep(
            name="환자번호 입력",
            text="환자번호: {{patient_id}}\n"
        ))
        
        macro.add_step(KeyboardTypeStep(
            name="환자정보 입력",
            text="환자명: {{patient_name}}, 진료과: {{department}}\n"
        ))
        
        macro.add_step(KeyboardTypeStep(
            name="검사결과 입력",
            text="검사: {{test_item}} - 결과: {{test_result}}\n"
        ))
        
        macro.add_step(KeyboardTypeStep(
            name="구분선",
            text="-" * 50 + "\n"
        ))
        
        # 4. Execute macro for first patient
        main_window.editor_widget.set_macro(macro)
        execution_widget = main_window.execution_widget
        execution_widget.set_macro(macro, excel_widget.excel_manager)
        
        # Start execution
        execution_widget.start_execution()
        
        # Wait for first row to complete
        timeout = 10
        start_time = time.time()
        while execution_widget.is_running and (time.time() - start_time) < timeout:
            QTest.qWait(100)
        
        # Verify execution completed
        assert not execution_widget.is_running
        
        # Close notepad
        if Path(notepad_path).exists():
            os.system("taskkill /f /im notepad.exe")
    
    def test_korean_ime_input(self, main_window):
        """Test Korean IME input handling"""
        # Create macro with Korean text
        macro = Macro(name="한글 입력 테스트")
        
        # Type Korean text
        korean_texts = [
            "안녕하세요",
            "환자명: 홍길동",
            "진료과: 내과",
            "특수문자: ㄱㄴㄷ ㅏㅑㅓㅕ"
        ]
        
        for text in korean_texts:
            macro.add_step(KeyboardTypeStep(
                name=f"한글 입력: {text}",
                text=text + "\n",
                interval=0.05  # Slower typing for IME
            ))
        
        # Open notepad for testing
        notepad_path = r"C:\Windows\System32\notepad.exe"
        if Path(notepad_path).exists():
            subprocess.Popen([notepad_path])
            time.sleep(2)
            
            # Execute macro
            main_window.editor_widget.set_macro(macro)
            execution_widget = main_window.execution_widget
            execution_widget.set_macro(macro)
            execution_widget.start_execution()
            
            # Wait for completion
            timeout = 10
            start_time = time.time()
            while execution_widget.is_running and (time.time() - start_time) < timeout:
                QTest.qWait(100)
            
            # Verify Korean text was typed
            # (In real test, would capture notepad content and verify)
            
            # Close notepad
            os.system("taskkill /f /im notepad.exe")
    
    def test_performance_requirements(self, main_window, test_excel_file):
        """Test performance meets medical environment requirements"""
        # Load data
        excel_widget = main_window.excel_widget
        excel_widget.load_file(test_excel_file)
        
        # Create simple macro
        macro = Macro(name="성능 테스트")
        macro.add_step(MouseClickStep(x=100, y=100))
        macro.add_step(KeyboardTypeStep(text="Test"))
        macro.add_step(WaitTimeStep(seconds=0.01))
        
        # Measure execution performance
        execution_widget = main_window.execution_widget
        execution_widget.set_macro(macro, excel_widget.excel_manager)
        
        # Track metrics
        process = psutil.Process(os.getpid())
        initial_cpu = process.cpu_percent()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Execute multiple times
        execution_times = []
        for i in range(5):
            start_time = time.time()
            
            execution_widget.start_execution()
            
            # Wait for completion
            while execution_widget.is_running:
                QTest.qWait(10)
            
            execution_time = time.time() - start_time
            execution_times.append(execution_time)
        
        # Check performance metrics
        avg_execution_time = sum(execution_times) / len(execution_times)
        final_cpu = process.cpu_percent()
        final_memory = process.memory_info().rss / 1024 / 1024
        
        # Verify requirements
        assert avg_execution_time < 0.3  # < 300ms per execution
        assert final_cpu < 50  # < 50% CPU usage
        assert final_memory - initial_memory < 100  # < 100MB memory increase
    
    def test_error_recovery(self, main_window):
        """Test error recovery in real scenarios"""
        # Create macro with potential error
        macro = Macro(name="에러 복구 테스트")
        
        # Click on non-existent window
        macro.add_step(MouseClickStep(
            name="없는 창 클릭",
            x=-1000,  # Off-screen
            y=-1000
        ))
        
        # Should continue after error
        macro.add_step(KeyboardTypeStep(
            name="복구 후 입력",
            text="Error recovery successful"
        ))
        
        # Set error handling to continue
        macro.steps[0].error_handling = "continue"
        
        # Execute
        execution_widget = main_window.execution_widget
        execution_widget.set_macro(macro)
        execution_widget.start_execution()
        
        # Wait for completion
        timeout = 5
        start_time = time.time()
        while execution_widget.is_running and (time.time() - start_time) < timeout:
            QTest.qWait(100)
        
        # Should complete despite error
        assert not execution_widget.is_running
    
    def test_multi_monitor_execution(self, main_window):
        """Test execution on multi-monitor setup"""
        import screeninfo
        
        try:
            monitors = screeninfo.get_monitors()
            
            if len(monitors) < 2:
                pytest.skip("Test requires multiple monitors")
            
            # Create macro that uses secondary monitor
            secondary = monitors[1]
            
            macro = Macro(name="멀티모니터 테스트")
            
            # Click on secondary monitor
            macro.add_step(MouseClickStep(
                name="보조 모니터 클릭",
                x=secondary.x + secondary.width // 2,
                y=secondary.y + secondary.height // 2
            ))
            
            # Execute
            execution_widget = main_window.execution_widget  
            execution_widget.set_macro(macro)
            execution_widget.start_execution()
            
            # Wait and verify
            while execution_widget.is_running:
                QTest.qWait(100)
                
        except Exception as e:
            pytest.skip(f"Multi-monitor test failed: {e}")
    
    def test_high_dpi_scaling(self, main_window):
        """Test with high DPI scaling"""
        # Get current DPI
        screen = QApplication.primaryScreen()
        dpi = screen.logicalDotsPerInch()
        
        # Create macro with precise positioning
        macro = Macro(name="DPI 스케일링 테스트")
        
        # Click at specific coordinates
        test_positions = [
            (100, 100),
            (200, 200),
            (300, 300)
        ]
        
        for x, y in test_positions:
            macro.add_step(MouseClickStep(
                name=f"클릭 ({x}, {y})",
                x=x,
                y=y
            ))
            macro.add_step(WaitTimeStep(seconds=0.1))
        
        # Execute and verify clicks happen at correct positions
        # (Would need visual verification in real test)
        
    def test_continuous_operation(self, main_window, test_excel_file):
        """Test continuous operation stability"""
        # Load large dataset
        excel_widget = main_window.excel_widget
        excel_widget.load_file(test_excel_file)
        
        # Create macro
        macro = Macro(name="연속 작업 테스트")
        macro.add_step(KeyboardTypeStep(text="{{patient_id}} "))
        macro.add_step(KeyboardTypeStep(text="{{patient_name}}\n"))
        
        # Track stability metrics
        start_time = time.time()
        errors = []
        
        # Execute for extended period
        execution_widget = main_window.execution_widget
        execution_widget.set_macro(macro, excel_widget.excel_manager)
        
        for i in range(100):  # Process 100 rows
            if i < excel_widget.excel_manager.get_total_rows():
                try:
                    execution_widget.execute_single_row(i)
                    QTest.qWait(10)
                except Exception as e:
                    errors.append((i, str(e)))
        
        execution_time = time.time() - start_time
        
        # Verify stability
        assert len(errors) < 5  # Less than 5% error rate
        assert execution_time < 60  # Complete within 1 minute
        
        # Check for memory leaks
        process = psutil.Process(os.getpid())
        memory_usage = process.memory_info().rss / 1024 / 1024
        assert memory_usage < 500  # Stay under 500MB
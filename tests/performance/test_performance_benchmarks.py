"""
Performance benchmark tests for medical environment requirements
Tests actual performance metrics without mocking
"""

import pytest
import time
import psutil
import os
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import threading
import gc
from memory_profiler import profile

from core.macro_types import (
    Macro, MouseClickStep, KeyboardTypeStep, WaitTimeStep,
    ImageSearchStep, TextSearchStep, IfConditionStep
)
from automation.engine import ExecutionEngine
from automation.executor import StepExecutor
from excel.excel_manager import ExcelManager
from vision.text_extractor import TextExtractor
from vision.image_matcher import ImageMatcher
from config.settings import Settings
from core.macro_storage import MacroStorage


class TestPerformanceBenchmarks:
    """Test performance meets PRD requirements"""
    
    @pytest.fixture
    def performance_tracker(self):
        """Track performance metrics"""
        class PerformanceTracker:
            def __init__(self):
                self.start_time = None
                self.end_time = None
                self.memory_samples = []
                self.cpu_samples = []
                self.process = psutil.Process(os.getpid())
                
            def start(self):
                self.start_time = time.time()
                self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
                
            def sample(self):
                self.memory_samples.append(
                    self.process.memory_info().rss / 1024 / 1024
                )
                self.cpu_samples.append(self.process.cpu_percent(interval=0.1))
                
            def stop(self):
                self.end_time = time.time()
                
            @property
            def duration(self):
                return self.end_time - self.start_time
                
            @property
            def max_memory(self):
                return max(self.memory_samples) if self.memory_samples else 0
                
            @property
            def avg_cpu(self):
                return sum(self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0
        
        return PerformanceTracker()
    
    def test_response_time_under_300ms(self, performance_tracker):
        """Test individual operations complete under 300ms"""
        settings = Settings()
        executor = StepExecutor(settings)
        
        # Test various step types
        test_steps = [
            MouseClickStep(name="Click", x=100, y=100),
            KeyboardTypeStep(name="Type", text="Test"),
            WaitTimeStep(name="Wait", seconds=0.1),
        ]
        
        response_times = []
        
        for step in test_steps:
            performance_tracker.start()
            
            # Execute step
            try:
                executor.execute_step(step)
            except Exception:
                pass  # Some steps might fail without proper setup
            
            performance_tracker.stop()
            response_times.append(performance_tracker.duration)
            
            # Each operation should complete under 300ms
            assert performance_tracker.duration < 0.3, f"{step.name} took {performance_tracker.duration:.3f}s"
        
        # Average should be well under 300ms
        avg_response = sum(response_times) / len(response_times)
        assert avg_response < 0.2  # Should be much faster than 300ms
    
    def test_cpu_usage_under_50_percent(self, performance_tracker):
        """Test CPU usage stays under 50% during operation"""
        # Create complex macro
        macro = Macro(name="CPU 테스트")
        for i in range(100):
            macro.add_step(MouseClickStep(x=i*10, y=i*10))
            macro.add_step(KeyboardTypeStep(text=f"Data {i}"))
        
        settings = Settings()
        engine = ExecutionEngine(settings)
        engine.set_macro(macro)
        
        # Monitor CPU during execution
        cpu_samples = []
        monitoring = True
        
        def monitor_cpu():
            while monitoring:
                cpu_samples.append(performance_tracker.process.cpu_percent(interval=0.1))
                time.sleep(0.1)
        
        monitor_thread = threading.Thread(target=monitor_cpu)
        monitor_thread.start()
        
        # Execute macro
        try:
            # Run for a few seconds
            for i in range(20):
                step = macro.steps[i]
                try:
                    executor = StepExecutor(settings)
                    executor.execute_step(step)
                except:
                    pass
                time.sleep(0.05)
        finally:
            monitoring = False
            monitor_thread.join()
        
        # Check CPU usage
        avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
        max_cpu = max(cpu_samples) if cpu_samples else 0
        
        assert avg_cpu < 50, f"Average CPU usage: {avg_cpu:.1f}%"
        assert max_cpu < 80, f"Peak CPU usage: {max_cpu:.1f}%"
    
    def test_memory_usage_150_patients(self, performance_tracker):
        """Test memory usage with 150+ patient records"""
        # Create large dataset
        num_patients = 150
        patient_data = {
            '환자번호': [f'P2024-{i:04d}' for i in range(num_patients)],
            '환자명': [f'환자{i}' for i in range(num_patients)],
            '생년월일': ['1970-01-01'] * num_patients,
            '진료과': ['내과', '외과', '정형외과'] * (num_patients // 3),
            '검사항목': ['혈액검사', 'X-ray', 'MRI'] * (num_patients // 3),
            '검사결과': ['정상', '이상', '재검'] * (num_patients // 3),
            '상세내용': ['X' * 1000] * num_patients  # 1KB per patient
        }
        
        df = pd.DataFrame(patient_data)
        
        # Save to Excel
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            df.to_excel(tmp.name, index=False)
            excel_file = tmp.name
        
        try:
            # Load data
            performance_tracker.start()
            initial_memory = performance_tracker.process.memory_info().rss / 1024 / 1024
            
            excel_manager = ExcelManager()
            excel_manager.load_file(excel_file)
            
            # Process all patients
            for i in range(num_patients):
                row_data = excel_manager.get_row_data(i)
                performance_tracker.sample()
                
                # Simulate processing
                time.sleep(0.001)
            
            performance_tracker.stop()
            
            # Check memory usage
            max_memory = performance_tracker.max_memory
            memory_increase = max_memory - initial_memory
            
            assert max_memory < 500, f"Max memory usage: {max_memory:.1f}MB"
            assert memory_increase < 200, f"Memory increase: {memory_increase:.1f}MB"
            
        finally:
            os.unlink(excel_file)
    
    def test_ocr_initialization_time(self, performance_tracker):
        """Test EasyOCR initialization time"""
        # Clear any existing instance
        TextExtractor._instance = None
        TextExtractor._reader = None
        
        performance_tracker.start()
        
        # Initialize OCR
        text_extractor = TextExtractor()
        reader = text_extractor._get_reader()
        
        performance_tracker.stop()
        
        # Should initialize within 5 seconds
        assert performance_tracker.duration < 5.0, f"OCR init took {performance_tracker.duration:.1f}s"
        
        # Test subsequent access is fast
        performance_tracker.start()
        reader2 = text_extractor._get_reader()
        performance_tracker.stop()
        
        # Subsequent access should be instant (cached)
        assert performance_tracker.duration < 0.01
        assert reader2 is reader  # Same instance
    
    def test_file_io_performance(self, performance_tracker):
        """Test file save/load performance"""
        # Create large macro
        large_macro = Macro(name="대용량 매크로")
        for i in range(1000):
            large_macro.add_step(MouseClickStep(x=i, y=i))
            large_macro.add_step(KeyboardTypeStep(text=f"Step {i}" * 10))
        
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = MacroStorage(Path(temp_dir))
            
            # Test save performance
            performance_tracker.start()
            result = storage.save_macro(large_macro)
            performance_tracker.stop()
            
            assert result is True
            save_time = performance_tracker.duration
            assert save_time < 1.0, f"Save took {save_time:.2f}s"
            
            # Find saved file
            saved_file = list(Path(temp_dir).glob("**/*.json"))[0]
            file_size = saved_file.stat().st_size / 1024 / 1024  # MB
            
            # Test load performance
            performance_tracker.start()
            loaded_macro = storage.load_macro(str(saved_file))
            performance_tracker.stop()
            
            load_time = performance_tracker.duration
            assert load_time < 0.5, f"Load took {load_time:.2f}s for {file_size:.1f}MB file"
            assert len(loaded_macro.steps) == 2000
    
    def test_concurrent_execution_performance(self):
        """Test performance with concurrent operations"""
        settings = Settings()
        
        # Create multiple executors
        num_concurrent = 5
        executors = [StepExecutor(settings) for _ in range(num_concurrent)]
        
        # Simple test step
        step = MouseClickStep(x=100, y=100)
        
        results = []
        threads = []
        
        def execute_concurrent(executor, index):
            start_time = time.time()
            try:
                for i in range(10):
                    executor.execute_step(step)
                    time.sleep(0.01)
            except:
                pass
            duration = time.time() - start_time
            results.append((index, duration))
        
        # Start concurrent execution
        for i, executor in enumerate(executors):
            thread = threading.Thread(target=execute_concurrent, args=(executor, i))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Check performance didn't degrade significantly
        durations = [r[1] for r in results]
        avg_duration = sum(durations) / len(durations)
        
        # Should complete reasonably fast even with concurrency
        assert avg_duration < 1.0
        assert max(durations) < 2.0
    
    @pytest.mark.slow
    def test_long_running_stability(self, performance_tracker):
        """Test stability during long-running operations"""
        settings = Settings()
        executor = StepExecutor(settings)
        
        # Track metrics over time
        memory_over_time = []
        error_count = 0
        
        # Run for extended period
        start_time = time.time()
        iterations = 1000
        
        for i in range(iterations):
            if i % 100 == 0:
                # Sample memory
                memory = performance_tracker.process.memory_info().rss / 1024 / 1024
                memory_over_time.append(memory)
                gc.collect()  # Force garbage collection
            
            # Execute simple operations
            try:
                step = MouseClickStep(x=100 + (i % 100), y=100 + (i % 100))
                executor.execute_step(step)
            except Exception:
                error_count += 1
            
            # Small delay
            time.sleep(0.001)
        
        duration = time.time() - start_time
        
        # Check stability metrics
        error_rate = error_count / iterations
        assert error_rate < 0.01  # Less than 1% errors
        
        # Check for memory leaks
        if len(memory_over_time) > 2:
            initial_memory = memory_over_time[0]
            final_memory = memory_over_time[-1]
            memory_growth = final_memory - initial_memory
            
            # Memory growth should be minimal
            assert memory_growth < 50  # Less than 50MB growth
    
    def test_image_matching_performance(self, performance_tracker):
        """Test image matching performance"""
        settings = Settings()
        image_matcher = ImageMatcher(settings)
        
        # Create test images
        test_images = []
        for i in range(5):
            # Create simple test image
            img = np.zeros((100, 100, 3), dtype=np.uint8)
            img[40:60, 40:60] = [255, 255, 255]  # White square
            
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                import cv2
                cv2.imwrite(tmp.name, img)
                test_images.append(tmp.name)
        
        try:
            # Test single image search
            performance_tracker.start()
            result = image_matcher.find_image(test_images[0])
            performance_tracker.stop()
            
            single_search_time = performance_tracker.duration
            assert single_search_time < 1.0  # Should be fast
            
            # Test multiple searches
            performance_tracker.start()
            for img_path in test_images:
                image_matcher.find_image(img_path)
            performance_tracker.stop()
            
            multi_search_time = performance_tracker.duration
            avg_time = multi_search_time / len(test_images)
            assert avg_time < 0.5  # Average should be under 500ms
            
        finally:
            # Cleanup
            for img_path in test_images:
                os.unlink(img_path)
    
    def test_excel_processing_performance(self):
        """Test Excel processing performance with large files"""
        # Create large Excel file
        num_rows = 10000
        num_cols = 20
        
        data = {}
        for col in range(num_cols):
            data[f'Column_{col}'] = [f'Data_{col}_{row}' for row in range(num_rows)]
        
        df = pd.DataFrame(data)
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            # Save Excel
            start_time = time.time()
            df.to_excel(tmp.name, index=False)
            save_time = time.time() - start_time
            excel_file = tmp.name
        
        try:
            excel_manager = ExcelManager()
            
            # Test load performance
            start_time = time.time()
            excel_manager.load_file(excel_file)
            load_time = time.time() - start_time
            
            # Should load reasonably fast
            assert load_time < 5.0  # 5 seconds for 10k rows
            
            # Test row access performance
            access_times = []
            test_rows = [0, 100, 1000, 5000, 9999]
            
            for row_idx in test_rows:
                start_time = time.time()
                row_data = excel_manager.get_row_data(row_idx)
                access_time = time.time() - start_time
                access_times.append(access_time)
            
            # Row access should be fast
            avg_access_time = sum(access_times) / len(access_times)
            assert avg_access_time < 0.01  # 10ms average
            
        finally:
            os.unlink(excel_file)
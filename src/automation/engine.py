"""
Main macro execution engine
"""

import time
import threading
from typing import Optional, Dict, Any, List, Callable
from enum import Enum
from PyQt5.QtCore import QThread, pyqtSignal, QObject
import pyautogui
from core.macro_types import Macro, MacroStep
from excel.excel_manager import ExcelManager
from logger.app_logger import get_logger
from config.settings import Settings
from automation.executor import StepExecutor
from automation.hotkey_listener import HotkeyListener
from logger.execution_logger import get_execution_logger
from automation.progress_calculator import ProgressCalculator, ExecutionMode as CalcExecutionMode, ProgressInfo

class ExecutionState(Enum):
    """Execution states"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"

class ExecutionResult:
    """Result of a single execution"""
    def __init__(self, row_index: int, success: bool, 
                 error: Optional[str] = None, duration_ms: float = 0):
        self.row_index = row_index
        self.success = success
        self.error = error
        self.duration_ms = duration_ms
        self.timestamp = time.time()

class ExecutionEngine(QThread):
    """Main macro execution engine"""
    
    # Signals
    stateChanged = pyqtSignal(ExecutionState)
    progressUpdated = pyqtSignal(int, int)  # current, total
    progressInfoUpdated = pyqtSignal(ProgressInfo)  # Detailed progress info
    rowCompleted = pyqtSignal(ExecutionResult)
    stepExecuting = pyqtSignal(MacroStep, int)  # step, row_index
    executionFinished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, settings: Settings):
        super().__init__()
        self.logger = get_logger(__name__)
        self.settings = settings
        
        # State management
        self._state = ExecutionState.IDLE
        self._state_lock = threading.Lock()
        self._pause_event = threading.Event()
        self._pause_event.set()  # Not paused by default
        
        # Execution components
        self.step_executor = StepExecutor(settings)
        self.hotkey_listener = HotkeyListener(settings)
        self.execution_logger = get_execution_logger()
        
        # Current execution context
        self.macro: Optional[Macro] = None
        self.excel_manager: Optional[ExcelManager] = None
        self.target_rows: List[int] = []
        self.current_row_index: Optional[int] = None
        
        # Progress calculator
        self.progress_calculator: Optional[ProgressCalculator] = None
        
        # Configure PyAutoGUI
        self._configure_pyautogui()
        
        # Connect hotkey signals
        self.hotkey_listener.pausePressed.connect(self.toggle_pause)
        self.hotkey_listener.stopPressed.connect(self.stop_execution)
        
    def _configure_pyautogui(self):
        """Configure PyAutoGUI settings"""
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        pyautogui.PAUSE = self.settings.get("execution.default_delay_ms", 100) / 1000.0
        
        # Log screen size for debugging
        screen_width, screen_height = pyautogui.size()
        self.logger.info(f"Screen size: {screen_width}x{screen_height}")
        
    @property
    def state(self) -> ExecutionState:
        """Get current execution state"""
        with self._state_lock:
            return self._state
            
    def _set_state(self, new_state: ExecutionState):
        """Set execution state"""
        with self._state_lock:
            old_state = self._state
            self._state = new_state
            
        if old_state != new_state:
            self.logger.info(f"State changed: {old_state.value} -> {new_state.value}")
            self.stateChanged.emit(new_state)
            
    def set_macro(self, macro: Macro, excel_manager: Optional[ExcelManager] = None):
        """Set macro and Excel manager for execution"""
        if self.state != ExecutionState.IDLE:
            raise RuntimeError("Cannot set macro while execution is active")
            
        self.macro = macro
        self.excel_manager = excel_manager
        
        # Debug: print macro steps
        for i, step in enumerate(macro.steps):
            self.logger.debug(f"Step {i+1}: {step.step_type.value}, name='{step.name}'")
            if hasattr(step, 'search_text'):
                self.logger.debug(f"  - search_text: '{step.search_text}'")
            if hasattr(step, 'excel_column'):
                self.logger.debug(f"  - excel_column: '{step.excel_column}'")
        
        # Validate macro
        errors = macro.validate()
        if errors:
            raise ValueError(f"Macro validation failed: {', '.join(errors)}")
            
        # Initialize progress calculator
        mode = CalcExecutionMode.EXCEL if excel_manager else CalcExecutionMode.STANDALONE
        self.progress_calculator = ProgressCalculator(mode)
            
    def set_target_rows(self, row_indices: List[int]):
        """Set specific rows to execute"""
        self.target_rows = row_indices
        
    def run(self):
        """Main execution thread"""
        if not self.macro:
            self.error.emit("No macro loaded")
            return
            
        try:
            self._set_state(ExecutionState.RUNNING)
            self.hotkey_listener.start()
            
            # Start CSV logging session
            excel_file = self.excel_manager.file_path if self.excel_manager else "Unknown"
            log_file = self.execution_logger.start_session(self.macro.name, excel_file)
            self.logger.info(f"Execution log started: {log_file}")
            
            # Determine execution mode
            if self.excel_manager and self.excel_manager._current_data:
                # Excel mode - execute for each row
                if not self.target_rows:
                    # Process all incomplete rows
                    self.target_rows = self.excel_manager.get_pending_rows()
                    
                total_rows = len(self.target_rows)
                self.logger.info(f"Starting execution for {total_rows} rows")
                
                # If no rows to process, switch to standalone mode
                if total_rows == 0:
                    self.logger.info("No Excel rows to process, switching to standalone mode")
                    self.excel_manager = None
            else:
                # No Excel data loaded
                total_rows = 0
                
            # Initialize progress calculator with macro structure
            if self.progress_calculator:
                self.progress_calculator.initialize_macro(self.macro, total_rows if self.excel_manager else None)
                
            # Check if we should run in standalone mode
            if not self.excel_manager or total_rows == 0:
                # Standalone mode - execute once without Excel data
                self.logger.info("Starting standalone macro execution")
                total_rows = 1
                successful_rows = 0
                failed_rows = 0
                
                # Update progress
                self.progressUpdated.emit(1, 1)
                
                # Execute macro without row data
                result = self._execute_standalone()
                
                if result.success:
                    successful_rows = 1
                else:
                    failed_rows = 1
                    
                # Emit result
                self.rowCompleted.emit(result)
            else:
                # Excel mode with data
                # Track statistics
                successful_rows = 0
                failed_rows = 0
                
                # Execute each row
                for i, row_index in enumerate(self.target_rows):
                    # Check if stopping
                    if self.state == ExecutionState.STOPPING:
                        break
                        
                    # Handle pause
                    self._pause_event.wait()
                    
                    # Update progress
                    self.progressUpdated.emit(i + 1, total_rows)
                    self.current_row_index = row_index
                    
                    # Execute macro for this row
                    result = self._execute_row(row_index)
                    
                    # Update statistics
                    if result.success:
                        successful_rows += 1
                    else:
                        failed_rows += 1
                    
                    # Update Excel status
                    status = "완료" if result.success else f"실패: {result.error}"
                    self.excel_manager.update_row_status(row_index, status)
                    
                    # Emit result
                    self.rowCompleted.emit(result)
                    
                    # Small delay between rows
                    time.sleep(0.1)
                    
                # Save Excel file after all rows (only if data exists)
                if self.excel_manager and self.excel_manager._current_data:
                    self.excel_manager.save_file()
            
            # Log session summary
            self.execution_logger.log_session_end(
                total_rows=total_rows,
                successful_rows=successful_rows,
                failed_rows=failed_rows
            )
            
            self._set_state(ExecutionState.IDLE)
            self.executionFinished.emit()
            
        except Exception as e:
            self.logger.error(f"Execution error: {e}", exc_info=True)
            self.execution_logger.log_error("EXECUTION_ERROR", str(e), details=str(e))
            self.error.emit(str(e))
            self._set_state(ExecutionState.ERROR)
            
        finally:
            self.hotkey_listener.stop()
            self.current_row_index = None
            self.execution_logger.close()
            
    def _execute_row(self, row_index: int) -> ExecutionResult:
        """Execute macro for a single row"""
        start_time = time.time()
        
        try:
            # Get row data with mappings
            row_data = self.excel_manager.get_mapped_data(row_index)
            
            # Log row start
            self.execution_logger.log_row_start(row_index, row_data)
            
            # Progress calculator: start row
            if self.progress_calculator:
                self.progress_calculator.start_row(row_index, row_data)
            
            # Set variables in executor context
            self.step_executor.set_variables(row_data)
            
            # Execute each step
            for step_index, step in enumerate(self.macro.steps):
                # Check if stopping
                if self.state == ExecutionState.STOPPING:
                    return ExecutionResult(row_index, False, "Execution stopped")
                    
                # Handle pause
                self._pause_event.wait()
                
                # Skip disabled steps
                if not step.enabled:
                    continue
                    
                # Emit step executing signal
                self.stepExecuting.emit(step, row_index)
                
                # Progress calculator: start step
                if self.progress_calculator:
                    self.progress_calculator.start_step(step, step_index)
                    progress_info = self.progress_calculator.calculate_progress()
                    self.progressInfoUpdated.emit(progress_info)
                
                # Execute step
                step_start_time = time.time()
                step_success = False
                step_error = ""
                
                try:
                    # Special handling for LoopStep
                    if step.step_type == StepType.LOOP and hasattr(step, 'loop_type'):
                        if step.loop_type == "excel_rows" and step.excel_rows:
                            # Execute loop for each Excel row
                            self._execute_excel_loop(step, row_index)
                            step_success = True
                        else:
                            # Regular loop execution (count, etc.)
                            self.step_executor.execute_step(step)
                            step_success = True
                    else:
                        # Regular step execution
                        self.step_executor.execute_step(step)
                        step_success = True
                    
                    # Progress calculator: complete step
                    if self.progress_calculator:
                        self.progress_calculator.complete_step(step)
                except Exception as e:
                    error_msg = f"Step '{step.name}' failed: {str(e)}"
                    self.logger.error(error_msg)
                    step_error = str(e)
                    
                    # Emit detailed error for UI
                    if step.error_handling.value == "stop":
                        self.error.emit(error_msg)
                    
                    # Handle error based on step configuration
                    if step.error_handling.value == "stop":
                        # Log failed step
                        step_duration = (time.time() - step_start_time) * 1000
                        self.execution_logger.log_step_execution(
                            row_index, step_index, step.name, step.step_type.value,
                            False, step_duration, step_error
                        )
                        return ExecutionResult(row_index, False, error_msg)
                    elif step.error_handling.value == "retry":
                        # Retry logic
                        for retry in range(step.retry_count):
                            try:
                                time.sleep(1)  # Wait before retry
                                self.step_executor.execute_step(step)
                                step_success = True
                                step_error = ""
                                break
                            except:
                                if retry == step.retry_count - 1:
                                    # Log failed step after all retries
                                    step_duration = (time.time() - step_start_time) * 1000
                                    self.execution_logger.log_step_execution(
                                        row_index, step_index, step.name, step.step_type.value,
                                        False, step_duration, step_error
                                    )
                                    return ExecutionResult(row_index, False, error_msg)
                    # For "continue", just log and proceed
                
                # Log step execution result
                step_duration = (time.time() - step_start_time) * 1000
                self.execution_logger.log_step_execution(
                    row_index, step_index, step.name, step.step_type.value,
                    step_success, step_duration, step_error
                )
                    
            # Progress calculator: complete row
            if self.progress_calculator:
                self.progress_calculator.complete_row(row_index)
                
            duration_ms = (time.time() - start_time) * 1000
            self.execution_logger.log_row_complete(row_index, True, duration_ms)
            return ExecutionResult(row_index, True, None, duration_ms)
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.execution_logger.log_row_complete(row_index, False, duration_ms, str(e))
            return ExecutionResult(row_index, False, str(e), duration_ms)
    
    def _execute_standalone(self) -> ExecutionResult:
        """Execute macro without Excel data"""
        start_time = time.time()
        
        try:
            # Log standalone execution start
            self.execution_logger.log_row_start(0, {})
            
            # Set empty variables in executor context
            self.step_executor.set_variables({})
            
            # Execute each step
            for step_index, step in enumerate(self.macro.steps):
                # Check if stopping
                if self.state == ExecutionState.STOPPING:
                    return ExecutionResult(0, False, "Execution stopped")
                    
                # Handle pause
                self._pause_event.wait()
                
                # Skip disabled steps
                if not step.enabled:
                    continue
                    
                # Emit step executing signal
                self.stepExecuting.emit(step, 0)
                
                # Progress calculator: start step
                if self.progress_calculator:
                    self.progress_calculator.start_step(step, step_index)
                    progress_info = self.progress_calculator.calculate_progress()
                    self.progressInfoUpdated.emit(progress_info)
                
                # Execute step
                step_start_time = time.time()
                step_success = False
                step_error = ""
                
                try:
                    self.step_executor.execute_step(step)
                    step_success = True
                    
                    # Progress calculator: complete step
                    if self.progress_calculator:
                        self.progress_calculator.complete_step(step)
                except Exception as e:
                    error_msg = f"Step '{step.name}' failed: {str(e)}"
                    self.logger.error(error_msg)
                    step_error = str(e)
                    
                    # Emit detailed error for UI
                    if step.error_handling.value == "stop":
                        self.error.emit(error_msg)
                    
                    # Handle error based on step configuration
                    if step.error_handling.value == "stop":
                        # Log failed step
                        step_duration = (time.time() - step_start_time) * 1000
                        self.execution_logger.log_step_execution(
                            0, step_index, step.name, step.step_type.value,
                            False, step_duration, step_error
                        )
                        return ExecutionResult(0, False, error_msg)
                    elif step.error_handling.value == "retry":
                        # Retry logic
                        for retry in range(step.retry_count):
                            try:
                                time.sleep(1)  # Wait before retry
                                self.step_executor.execute_step(step)
                                step_success = True
                                step_error = ""
                                break
                            except:
                                if retry == step.retry_count - 1:
                                    # Log failed step after all retries
                                    step_duration = (time.time() - step_start_time) * 1000
                                    self.execution_logger.log_step_execution(
                                        0, step_index, step.name, step.step_type.value,
                                        False, step_duration, step_error
                                    )
                                    return ExecutionResult(0, False, error_msg)
                    # For "continue", just log and proceed
                
                # Log step execution result
                step_duration = (time.time() - step_start_time) * 1000
                self.execution_logger.log_step_execution(
                    0, step_index, step.name, step.step_type.value,
                    step_success, step_duration, step_error
                )
                    
            duration_ms = (time.time() - start_time) * 1000
            self.execution_logger.log_row_complete(0, True, duration_ms)
            return ExecutionResult(0, True, None, duration_ms)
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.execution_logger.log_row_complete(0, False, duration_ms, str(e))
            return ExecutionResult(0, False, str(e), duration_ms)
            
    def _execute_excel_loop(self, loop_step, parent_row_index: int):
        """Execute loop for each Excel row"""
        if not self.excel_manager or not loop_step.excel_rows:
            self.logger.warning("No Excel data available for loop execution")
            return
            
        # Get the nested steps that need to be executed
        nested_steps = []
        for step_id in loop_step.loop_steps:
            # Find the step by ID in the macro
            for step in self.macro.steps:
                if step.step_id == step_id:
                    nested_steps.append(step)
                    break
                    
        if not nested_steps:
            self.logger.warning("No nested steps found in loop")
            return
            
        # Save current variables
        original_variables = self.step_executor.variables.copy()
        
        try:
            # Execute nested steps for each Excel row
            for excel_row_index in loop_step.excel_rows:
                # Check if stopping
                if self.state == ExecutionState.STOPPING:
                    break
                    
                # Update current row in loop step
                loop_step.current_row_index = excel_row_index
                
                # Get row data for this specific row
                row_data = self.excel_manager.get_mapped_data(excel_row_index)
                
                # Merge with original variables (Excel data takes precedence)
                merged_variables = original_variables.copy()
                merged_variables.update(row_data)
                merged_variables['현재행'] = excel_row_index + 1  # 1-based for user display
                merged_variables['총행수'] = len(loop_step.excel_rows)
                
                # Set variables for this iteration
                self.step_executor.set_variables(merged_variables)
                
                self.logger.info(f"Executing loop iteration for Excel row {excel_row_index + 1}")
                
                # Execute each nested step
                for nested_step in nested_steps:
                    if not nested_step.enabled:
                        continue
                        
                    # Handle pause
                    self._pause_event.wait()
                    
                    try:
                        self.step_executor.execute_step(nested_step)
                    except Exception as e:
                        error_msg = f"Loop step '{nested_step.name}' failed for row {excel_row_index + 1}: {str(e)}"
                        self.logger.error(error_msg)
                        
                        # Handle error based on step configuration
                        if nested_step.error_handling.value == "stop":
                            raise Exception(error_msg)
                        # For "continue", just log and proceed to next step/row
                        
        finally:
            # Restore original variables
            self.step_executor.set_variables(original_variables)
            loop_step.current_row_index = None
    
    def toggle_pause(self):
        """Toggle pause state"""
        if self.state == ExecutionState.RUNNING:
            self._set_state(ExecutionState.PAUSED)
            self._pause_event.clear()
            self.logger.info("Execution paused")
        elif self.state == ExecutionState.PAUSED:
            self._set_state(ExecutionState.RUNNING)
            self._pause_event.set()
            self.logger.info("Execution resumed")
            
    def stop_execution(self):
        """Stop execution"""
        if self.state in [ExecutionState.RUNNING, ExecutionState.PAUSED]:
            self._set_state(ExecutionState.STOPPING)
            self._pause_event.set()  # Resume if paused
            self.logger.info("Stopping execution...")
            
    def is_running(self) -> bool:
        """Check if execution is active"""
        return self.state in [ExecutionState.RUNNING, ExecutionState.PAUSED]
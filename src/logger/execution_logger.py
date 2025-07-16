"""
CSV execution logger for macro runs
"""

import csv
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import threading
from queue import Queue
import atexit

class ExecutionLogger:
    """Logs macro execution details to CSV files"""
    
    def __init__(self, log_dir: Optional[Path] = None):
        """Initialize execution logger
        
        Args:
            log_dir: Directory to save log files. Defaults to user logs directory.
        """
        # Set log directory
        if log_dir is None:
            self.log_dir = Path.home() / ".excel_macro_automation" / "execution_logs"
        else:
            self.log_dir = Path(log_dir)
            
        # Create directory if not exists
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Current log file
        self.current_file: Optional[Path] = None
        self.csv_writer: Optional[csv.DictWriter] = None
        self.file_handle = None
        
        # Buffering for performance
        self.write_queue = Queue()
        self.writer_thread = None
        self.running = False
        
        # Register cleanup on exit
        atexit.register(self.close)
        
    def start_session(self, macro_name: str, excel_file: str) -> Path:
        """Start a new logging session
        
        Args:
            macro_name: Name of the macro being executed
            excel_file: Path to the Excel file being processed
            
        Returns:
            Path to the created log file
        """
        # Close previous session if any
        self.close()
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_macro_name = "".join(c for c in macro_name if c.isalnum() or c in "._- ")[:50]
        filename = f"execution_{safe_macro_name}_{timestamp}.csv"
        self.current_file = self.log_dir / filename
        
        # Open file and create CSV writer
        self.file_handle = open(self.current_file, 'w', newline='', encoding='utf-8')
        
        # Define CSV fields
        self.fieldnames = [
            'timestamp',
            'elapsed_ms',
            'row_index',
            'row_data',
            'step_index',
            'step_name',
            'step_type',
            'status',
            'error_message',
            'duration_ms',
            'details'
        ]
        
        self.csv_writer = csv.DictWriter(self.file_handle, fieldnames=self.fieldnames)
        self.csv_writer.writeheader()
        
        # Write session info
        self.csv_writer.writerow({
            'timestamp': datetime.now().isoformat(),
            'elapsed_ms': 0,
            'row_index': -1,
            'row_data': f"Session Start - Macro: {macro_name}",
            'step_index': -1,
            'step_name': "SESSION_START",
            'step_type': "INFO",
            'status': "INFO",
            'error_message': "",
            'duration_ms': 0,
            'details': f"Excel: {excel_file}"
        })
        
        # Start writer thread
        self.running = True
        self.writer_thread = threading.Thread(target=self._writer_loop, daemon=True)
        self.writer_thread.start()
        
        self.session_start_time = datetime.now()
        
        return self.current_file
        
    def log_row_start(self, row_index: int, row_data: Dict[str, Any]):
        """Log the start of processing a row"""
        self._enqueue_log({
            'timestamp': datetime.now().isoformat(),
            'elapsed_ms': self._get_elapsed_ms(),
            'row_index': row_index,
            'row_data': str(row_data),
            'step_index': -1,
            'step_name': "ROW_START",
            'step_type': "INFO",
            'status': "START",
            'error_message': "",
            'duration_ms': 0,
            'details': f"Processing row {row_index + 1}"
        })
        
    def log_step_execution(self, row_index: int, step_index: int, step_name: str, 
                          step_type: str, success: bool, duration_ms: float,
                          error_message: str = "", details: str = ""):
        """Log execution of a single step"""
        self._enqueue_log({
            'timestamp': datetime.now().isoformat(),
            'elapsed_ms': self._get_elapsed_ms(),
            'row_index': row_index,
            'row_data': "",
            'step_index': step_index,
            'step_name': step_name,
            'step_type': step_type,
            'status': "SUCCESS" if success else "FAILED",
            'error_message': error_message,
            'duration_ms': round(duration_ms, 2),
            'details': details
        })
        
    def log_row_complete(self, row_index: int, success: bool, total_duration_ms: float,
                        error_message: str = ""):
        """Log completion of a row"""
        self._enqueue_log({
            'timestamp': datetime.now().isoformat(),
            'elapsed_ms': self._get_elapsed_ms(),
            'row_index': row_index,
            'row_data': "",
            'step_index': -1,
            'step_name': "ROW_COMPLETE",
            'step_type': "INFO",
            'status': "SUCCESS" if success else "FAILED",
            'error_message': error_message,
            'duration_ms': round(total_duration_ms, 2),
            'details': f"Row {row_index + 1} completed"
        })
        
    def log_session_end(self, total_rows: int, successful_rows: int, failed_rows: int):
        """Log end of session with summary"""
        self._enqueue_log({
            'timestamp': datetime.now().isoformat(),
            'elapsed_ms': self._get_elapsed_ms(),
            'row_index': -1,
            'row_data': f"Session End - Total: {total_rows}, Success: {successful_rows}, Failed: {failed_rows}",
            'step_index': -1,
            'step_name': "SESSION_END",
            'step_type': "INFO",
            'status': "INFO",
            'error_message': "",
            'duration_ms': self._get_elapsed_ms(),
            'details': f"Success rate: {(successful_rows/total_rows*100) if total_rows > 0 else 0:.1f}%"
        })
        
    def log_error(self, error_type: str, error_message: str, details: str = ""):
        """Log a general error"""
        self._enqueue_log({
            'timestamp': datetime.now().isoformat(),
            'elapsed_ms': self._get_elapsed_ms(),
            'row_index': -1,
            'row_data': "",
            'step_index': -1,
            'step_name': error_type,
            'step_type': "ERROR",
            'status': "ERROR",
            'error_message': error_message,
            'duration_ms': 0,
            'details': details
        })
        
    def flush(self):
        """Force flush any pending logs"""
        if self.file_handle:
            # Wait for queue to empty
            self.write_queue.join()
            self.file_handle.flush()
            
    def close(self):
        """Close the current logging session"""
        if self.running:
            # Signal thread to stop
            self.running = False
            self._enqueue_log(None)  # Sentinel value
            
            # Wait for thread to finish
            if self.writer_thread and self.writer_thread.is_alive():
                self.writer_thread.join(timeout=5.0)
                
        # Close file
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None
            self.csv_writer = None
            
    def get_current_log_file(self) -> Optional[Path]:
        """Get path to current log file"""
        return self.current_file
        
    def _enqueue_log(self, log_entry: Optional[Dict[str, Any]]):
        """Add log entry to write queue"""
        self.write_queue.put(log_entry)
        
    def _writer_loop(self):
        """Background thread for writing logs"""
        while self.running:
            try:
                # Get log entry from queue
                log_entry = self.write_queue.get(timeout=0.1)
                
                # Check for sentinel
                if log_entry is None:
                    break
                    
                # Write to CSV
                if self.csv_writer:
                    self.csv_writer.writerow(log_entry)
                    
                # Mark task done
                self.write_queue.task_done()
                
            except:
                # Timeout or error, continue
                pass
                
    def _get_elapsed_ms(self) -> float:
        """Get elapsed time since session start"""
        if hasattr(self, 'session_start_time'):
            elapsed = datetime.now() - self.session_start_time
            return elapsed.total_seconds() * 1000
        return 0

# Global instance
_execution_logger = None

def get_execution_logger() -> ExecutionLogger:
    """Get the global execution logger instance"""
    global _execution_logger
    if _execution_logger is None:
        _execution_logger = ExecutionLogger()
    return _execution_logger
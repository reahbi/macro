"""
CSV log viewer dialog for analyzing execution logs
"""

import csv
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QGroupBox, QComboBox, QLineEdit,
    QWidget, QSplitter, QTextEdit, QFileDialog, QMessageBox,
    QHeaderView, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

class LogStatisticsWidget(QWidget):
    """Widget showing log statistics and charts"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Summary statistics
        self.stats_group = QGroupBox("실행 통계")
        stats_layout = QVBoxLayout()
        
        self.total_rows_label = QLabel("전체 행: 0")
        self.success_rows_label = QLabel("성공: 0 (0.0%)")
        self.failed_rows_label = QLabel("실패: 0 (0.0%)")
        self.total_time_label = QLabel("총 실행 시간: 0분 0초")
        self.avg_time_label = QLabel("평균 행 처리 시간: 0.0초")
        
        stats_layout.addWidget(self.total_rows_label)
        stats_layout.addWidget(self.success_rows_label)
        stats_layout.addWidget(self.failed_rows_label)
        stats_layout.addWidget(self.total_time_label)
        stats_layout.addWidget(self.avg_time_label)
        
        self.stats_group.setLayout(stats_layout)
        layout.addWidget(self.stats_group)
        
        # Chart (if matplotlib available)
        if HAS_MATPLOTLIB:
            self.figure = Figure(figsize=(5, 3))
            self.canvas = FigureCanvas(self.figure)
            layout.addWidget(self.canvas)
        else:
            no_chart_label = QLabel("차트를 표시하려면 matplotlib를 설치하세요")
            no_chart_label.setStyleSheet("color: #666; padding: 20px;")
            no_chart_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_chart_label)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def update_statistics(self, log_data: List[Dict[str, Any]]):
        """Update statistics from log data"""
        if not log_data:
            return
            
        # Calculate statistics
        total_rows = 0
        successful_rows = 0
        failed_rows = 0
        total_elapsed_ms = 0
        row_times = []
        
        # Process log entries
        processed_rows = set()
        for entry in log_data:
            if entry['row_index'] and entry['row_index'] != '-1':
                row_idx = int(entry['row_index'])
                
                if entry['step_name'] == 'ROW_COMPLETE' and row_idx not in processed_rows:
                    processed_rows.add(row_idx)
                    total_rows += 1
                    
                    if entry['status'] == 'SUCCESS':
                        successful_rows += 1
                    else:
                        failed_rows += 1
                        
                    if entry['duration_ms']:
                        row_times.append(float(entry['duration_ms']))
                        
            # Get total elapsed time from session end
            if entry['step_name'] == 'SESSION_END' and entry['elapsed_ms']:
                total_elapsed_ms = float(entry['elapsed_ms'])
                
        # Update labels
        self.total_rows_label.setText(f"전체 행: {total_rows}")
        
        if total_rows > 0:
            success_rate = (successful_rows / total_rows) * 100
            self.success_rows_label.setText(f"성공: {successful_rows} ({success_rate:.1f}%)")
            self.failed_rows_label.setText(f"실패: {failed_rows} ({100-success_rate:.1f}%)")
        else:
            self.success_rows_label.setText("성공: 0 (0.0%)")
            self.failed_rows_label.setText("실패: 0 (0.0%)")
            
        # Time statistics
        if total_elapsed_ms > 0:
            total_seconds = total_elapsed_ms / 1000
            minutes = int(total_seconds // 60)
            seconds = int(total_seconds % 60)
            self.total_time_label.setText(f"총 실행 시간: {minutes}분 {seconds}초")
            
        if row_times:
            avg_time = sum(row_times) / len(row_times) / 1000  # Convert to seconds
            self.avg_time_label.setText(f"평균 행 처리 시간: {avg_time:.1f}초")
            
        # Update chart
        self.update_chart(successful_rows, failed_rows)
        
    def update_chart(self, success: int, failed: int):
        """Update pie chart"""
        if not HAS_MATPLOTLIB:
            return
            
        self.figure.clear()
        
        if success == 0 and failed == 0:
            return
            
        ax = self.figure.add_subplot(111)
        
        # Data
        sizes = [success, failed]
        labels = ['성공', '실패']
        colors = ['#4CAF50', '#F44336']
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=90
        )
        
        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis('equal')
        ax.set_title('실행 결과 분포')
        
        self.canvas.draw()

class LogViewerDialog(QDialog):
    """Dialog for viewing and analyzing CSV execution logs"""
    
    def __init__(self, log_file: Optional[Path] = None, parent=None):
        super().__init__(parent)
        self.log_data: List[Dict[str, Any]] = []
        self.filtered_data: List[Dict[str, Any]] = []
        
        self.init_ui()
        
        if log_file:
            self.load_log_file(log_file)
            
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("실행 로그 뷰어")
        self.setModal(False)  # Non-modal to allow interaction with main window
        self.resize(1200, 700)
        
        layout = QVBoxLayout()
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        # Open file button
        open_btn = QPushButton("로그 파일 열기...")
        open_btn.clicked.connect(self.open_log_file)
        toolbar_layout.addWidget(open_btn)
        
        # Refresh button
        self.refresh_btn = QPushButton("새로고침")
        self.refresh_btn.clicked.connect(self.refresh_current_file)
        self.refresh_btn.setEnabled(False)
        toolbar_layout.addWidget(self.refresh_btn)
        
        toolbar_layout.addWidget(QLabel("필터:"))
        
        # Status filter
        self.status_filter = QComboBox()
        self.status_filter.addItems(["전체", "성공", "실패", "오류"])
        self.status_filter.currentTextChanged.connect(self.apply_filters)
        toolbar_layout.addWidget(self.status_filter)
        
        # Search
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("검색...")
        self.search_edit.textChanged.connect(self.apply_filters)
        toolbar_layout.addWidget(self.search_edit)
        
        # Export button
        export_btn = QPushButton("내보내기...")
        export_btn.clicked.connect(self.export_filtered_data)
        toolbar_layout.addWidget(export_btn)
        
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # Current file label
        self.file_label = QLabel("로그 파일이 선택되지 않았습니다")
        self.file_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.file_label)
        
        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Statistics widget
        self.stats_widget = LogStatisticsWidget()
        splitter.addWidget(self.stats_widget)
        
        # Log table
        self.log_table = QTableWidget()
        self.setup_table()
        splitter.addWidget(self.log_table)
        
        # Set splitter sizes (30% stats, 70% table)
        splitter.setSizes([300, 700])
        
        layout.addWidget(splitter)
        
        # Status bar
        self.status_label = QLabel("준비")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # Auto-refresh timer
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self.refresh_current_file)
        
    def setup_table(self):
        """Setup log table"""
        headers = [
            "시간", "경과(초)", "행", "단계", "타입", 
            "상태", "소요시간(ms)", "오류 메시지", "상세"
        ]
        
        self.log_table.setColumnCount(len(headers))
        self.log_table.setHorizontalHeaderLabels(headers)
        
        # Set column widths
        header = self.log_table.horizontalHeader()
        header.setStretchLastSection(True)
        self.log_table.setColumnWidth(0, 150)  # Time
        self.log_table.setColumnWidth(1, 80)   # Elapsed
        self.log_table.setColumnWidth(2, 60)   # Row
        self.log_table.setColumnWidth(3, 150)  # Step
        self.log_table.setColumnWidth(4, 100)  # Type
        self.log_table.setColumnWidth(5, 80)   # Status
        self.log_table.setColumnWidth(6, 100)  # Duration
        self.log_table.setColumnWidth(7, 200)  # Error
        
        # Enable sorting
        self.log_table.setSortingEnabled(True)
        
        # Row selection
        self.log_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.log_table.itemSelectionChanged.connect(self.on_selection_changed)
        
    def open_log_file(self):
        """Open a log file"""
        log_dir = Path.home() / ".excel_macro_automation" / "execution_logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "실행 로그 파일 선택",
            str(log_dir),
            "CSV Files (*.csv);;All Files (*.*)"
        )
        
        if file_path:
            self.load_log_file(Path(file_path))
            
    def load_log_file(self, file_path: Path):
        """Load CSV log file"""
        self.current_file = file_path
        self.file_label.setText(f"로그 파일: {file_path.name}")
        self.refresh_btn.setEnabled(True)
        
        try:
            self.log_data = []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.log_data.append(row)
                    
            self.apply_filters()
            self.status_label.setText(f"{len(self.log_data)}개 항목 로드됨")
            
            # Update statistics
            self.stats_widget.update_statistics(self.log_data)
            
            # Enable auto-refresh for current session
            if self.is_current_session():
                self.auto_refresh_timer.start(2000)  # Refresh every 2 seconds
            else:
                self.auto_refresh_timer.stop()
                
        except Exception as e:
            QMessageBox.critical(self, "오류", f"로그 파일 로드 실패:\n{str(e)}")
            
    def is_current_session(self) -> bool:
        """Check if loaded file is from current session"""
        if not hasattr(self, 'current_file'):
            return False
            
        # Check if file was modified recently (within last minute)
        try:
            mtime = os.path.getmtime(self.current_file)
            age = datetime.now().timestamp() - mtime
            return age < 60  # Less than 1 minute old
        except:
            return False
            
    def refresh_current_file(self):
        """Refresh current log file"""
        if hasattr(self, 'current_file'):
            self.load_log_file(self.current_file)
            
    def apply_filters(self):
        """Apply filters to log data"""
        # Get filter criteria
        status_filter = self.status_filter.currentText()
        search_text = self.search_edit.text().lower()
        
        # Filter data
        self.filtered_data = []
        
        for entry in self.log_data:
            # Status filter
            if status_filter != "전체":
                if status_filter == "성공" and entry['status'] != 'SUCCESS':
                    continue
                elif status_filter == "실패" and entry['status'] != 'FAILED':
                    continue
                elif status_filter == "오류" and entry['status'] != 'ERROR':
                    continue
                    
            # Search filter
            if search_text:
                found = False
                for value in entry.values():
                    if search_text in str(value).lower():
                        found = True
                        break
                if not found:
                    continue
                    
            self.filtered_data.append(entry)
            
        # Update table
        self.update_table()
        
    def update_table(self):
        """Update table with filtered data"""
        self.log_table.setRowCount(len(self.filtered_data))
        
        for i, entry in enumerate(self.filtered_data):
            # Timestamp
            timestamp = entry.get('timestamp', '')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
            self.log_table.setItem(i, 0, QTableWidgetItem(timestamp))
            
            # Elapsed time in seconds
            elapsed_ms = entry.get('elapsed_ms', '')
            if elapsed_ms:
                try:
                    elapsed_sec = float(elapsed_ms) / 1000
                    elapsed_str = f"{elapsed_sec:.1f}"
                except:
                    elapsed_str = elapsed_ms
            else:
                elapsed_str = ""
            self.log_table.setItem(i, 1, QTableWidgetItem(elapsed_str))
            
            # Row index (1-based for display)
            row_idx = entry.get('row_index', '')
            if row_idx and row_idx != '-1':
                try:
                    row_display = str(int(row_idx) + 1)
                except:
                    row_display = row_idx
            else:
                row_display = ""
            self.log_table.setItem(i, 2, QTableWidgetItem(row_display))
            
            # Step name
            self.log_table.setItem(i, 3, QTableWidgetItem(entry.get('step_name', '')))
            
            # Step type
            self.log_table.setItem(i, 4, QTableWidgetItem(entry.get('step_type', '')))
            
            # Status with color
            status = entry.get('status', '')
            status_item = QTableWidgetItem(status)
            if status == 'SUCCESS':
                status_item.setForeground(QColor(0, 128, 0))
            elif status in ['FAILED', 'ERROR']:
                status_item.setForeground(QColor(255, 0, 0))
            self.log_table.setItem(i, 5, status_item)
            
            # Duration
            self.log_table.setItem(i, 6, QTableWidgetItem(entry.get('duration_ms', '')))
            
            # Error message
            self.log_table.setItem(i, 7, QTableWidgetItem(entry.get('error_message', '')))
            
            # Details
            self.log_table.setItem(i, 8, QTableWidgetItem(entry.get('details', '')))
            
        self.status_label.setText(f"{len(self.filtered_data)}개 항목 표시 중")
        
    def on_selection_changed(self):
        """Handle row selection"""
        # Could show more details in a separate panel
        pass
        
    def export_filtered_data(self):
        """Export filtered data to CSV"""
        if not self.filtered_data:
            QMessageBox.information(self, "내보내기", "내보낼 데이터가 없습니다.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "로그 내보내기",
            f"filtered_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    if self.filtered_data:
                        writer = csv.DictWriter(f, fieldnames=self.filtered_data[0].keys())
                        writer.writeheader()
                        writer.writerows(self.filtered_data)
                        
                QMessageBox.information(self, "내보내기 완료", f"로그가 내보내졌습니다:\n{file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "내보내기 실패", f"로그 내보내기 중 오류:\n{str(e)}")
                
    def closeEvent(self, event):
        """Handle dialog close"""
        self.auto_refresh_timer.stop()
        super().closeEvent(event)
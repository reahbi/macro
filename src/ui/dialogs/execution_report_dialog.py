"""
Execution report dialog showing detailed execution results
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QTextEdit, QGroupBox,
    QTabWidget, QHeaderView, QFileDialog, QMessageBox, QWidget
)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QFont, QColor, QBrush
from typing import List, Dict, Any
import csv
import json


class ExecutionReportDialog(QDialog):
    """Dialog showing execution report after workflow completion"""
    
    def __init__(self, 
                 total_rows: int,
                 successful_rows: int,
                 failed_rows: int,
                 execution_time: int,  # seconds
                 failed_details: List[Dict[str, Any]] = None,
                 parent=None):
        super().__init__(parent)
        self.total_rows = total_rows
        self.successful_rows = successful_rows
        self.failed_rows = failed_rows
        self.execution_time = execution_time
        self.failed_details = failed_details or []
        
        self.setWindowTitle("실행 리포트")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("워크플로우 실행 리포트")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Timestamp
        timestamp = QLabel(QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss"))
        timestamp.setAlignment(Qt.AlignCenter)
        layout.addWidget(timestamp)
        
        # Summary section
        summary_group = self.create_summary_section()
        layout.addWidget(summary_group)
        
        # Tab widget for details
        tab_widget = QTabWidget()
        
        # Overview tab
        overview_tab = self.create_overview_tab()
        tab_widget.addTab(overview_tab, "개요")
        
        # Failed rows tab
        if self.failed_rows > 0:
            failed_tab = self.create_failed_rows_tab()
            tab_widget.addTab(failed_tab, f"실패 ({self.failed_rows})")
            
        # Statistics tab
        stats_tab = self.create_statistics_tab()
        tab_widget.addTab(stats_tab, "통계")
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        export_csv_btn = QPushButton("CSV로 내보내기")
        export_csv_btn.clicked.connect(self.export_to_csv)
        button_layout.addWidget(export_csv_btn)
        
        export_json_btn = QPushButton("JSON으로 내보내기")
        export_json_btn.clicked.connect(self.export_to_json)
        button_layout.addWidget(export_json_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("닫기")
        close_btn.clicked.connect(self.accept)
        close_btn.setDefault(True)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
    def create_summary_section(self):
        """Create summary section"""
        group = QGroupBox("실행 요약")
        layout = QHBoxLayout()
        
        # Success rate visualization
        success_rate = (self.successful_rows / self.total_rows * 100) if self.total_rows > 0 else 0
        
        # Create circular progress-like display
        rate_widget = QLabel(f"{success_rate:.1f}%")
        rate_font = QFont()
        rate_font.setPointSize(36)
        rate_font.setBold(True)
        rate_widget.setFont(rate_font)
        
        if success_rate >= 90:
            rate_widget.setStyleSheet("color: green;")
        elif success_rate >= 70:
            rate_widget.setStyleSheet("color: orange;")
        else:
            rate_widget.setStyleSheet("color: red;")
            
        rate_widget.setAlignment(Qt.AlignCenter)
        layout.addWidget(rate_widget)
        
        # Statistics
        stats_layout = QVBoxLayout()
        
        total_label = QLabel(f"전체 행: {self.total_rows}")
        total_label.setStyleSheet("font-size: 14px;")
        stats_layout.addWidget(total_label)
        
        success_label = QLabel(f"성공: {self.successful_rows}")
        success_label.setStyleSheet("font-size: 14px; color: green;")
        stats_layout.addWidget(success_label)
        
        failed_label = QLabel(f"실패: {self.failed_rows}")
        failed_label.setStyleSheet("font-size: 14px; color: red;")
        stats_layout.addWidget(failed_label)
        
        # Execution time
        hours = self.execution_time // 3600
        minutes = (self.execution_time % 3600) // 60
        seconds = self.execution_time % 60
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        time_label = QLabel(f"실행 시간: {time_str}")
        time_label.setStyleSheet("font-size: 14px;")
        stats_layout.addWidget(time_label)
        
        # Performance
        if self.total_rows > 0 and self.execution_time > 0:
            rows_per_minute = (self.total_rows / self.execution_time) * 60
            perf_label = QLabel(f"처리 속도: {rows_per_minute:.1f} 행/분")
            perf_label.setStyleSheet("font-size: 14px;")
            stats_layout.addWidget(perf_label)
        
        layout.addLayout(stats_layout)
        layout.addStretch()
        
        group.setLayout(layout)
        return group
        
    def create_overview_tab(self):
        """Create overview tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Summary text
        summary_text = QTextEdit()
        summary_text.setReadOnly(True)
        
        summary = f"""실행 결과 요약
====================

실행 시작: {QDateTime.currentDateTime().addSecs(-self.execution_time).toString("yyyy-MM-dd hh:mm:ss")}
실행 종료: {QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")}

처리 결과:
- 전체 행 수: {self.total_rows}
- 성공한 행: {self.successful_rows}
- 실패한 행: {self.failed_rows}
- 성공률: {(self.successful_rows/self.total_rows*100) if self.total_rows > 0 else 0:.1f}%

실행 시간: {self.execution_time//3600:02d}:{(self.execution_time%3600)//60:02d}:{self.execution_time%60:02d}
평균 처리 시간: {self.execution_time/self.total_rows if self.total_rows > 0 else 0:.2f}초/행
"""
        
        if self.failed_rows > 0:
            summary += f"\n실패 원인 요약:\n"
            # Group failures by error type
            error_counts = {}
            for detail in self.failed_details:
                error = detail.get('error', 'Unknown error')
                error_counts[error] = error_counts.get(error, 0) + 1
                
            for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
                summary += f"- {error}: {count}건\n"
        
        summary_text.setPlainText(summary)
        layout.addWidget(summary_text)
        
        widget.setLayout(layout)
        return widget
        
    def create_failed_rows_tab(self):
        """Create failed rows tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Failed rows table
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["행 번호", "데이터", "오류 메시지", "실패 단계"])
        
        # Populate table
        table.setRowCount(len(self.failed_details))
        
        for i, detail in enumerate(self.failed_details):
            # Row number
            row_item = QTableWidgetItem(str(detail.get('row_index', i) + 1))
            table.setItem(i, 0, row_item)
            
            # Data preview
            data = detail.get('data', {})
            data_str = ", ".join([f"{k}: {v}" for k, v in list(data.items())[:3]])
            if len(data) > 3:
                data_str += "..."
            data_item = QTableWidgetItem(data_str)
            table.setItem(i, 1, data_item)
            
            # Error message
            error_item = QTableWidgetItem(detail.get('error', 'Unknown error'))
            error_item.setForeground(QBrush(QColor(255, 0, 0)))
            table.setItem(i, 2, error_item)
            
            # Failed step
            step_item = QTableWidgetItem(detail.get('failed_step', 'Unknown'))
            table.setItem(i, 3, step_item)
            
        # Resize columns
        table.resizeColumnsToContents()
        header = table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
        layout.addWidget(table)
        
        # Retry suggestion
        if self.failed_rows > 0:
            suggestion = QLabel(
                "💡 팁: 실패한 행만 선택하여 다시 실행할 수 있습니다.\n"
                "실행 화면에서 '실패한 행만' 필터를 사용하세요."
            )
            suggestion.setWordWrap(True)
            suggestion.setStyleSheet("background-color: #fff3cd; padding: 10px; border-radius: 5px;")
            layout.addWidget(suggestion)
        
        widget.setLayout(layout)
        return widget
        
    def create_statistics_tab(self):
        """Create statistics tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Performance metrics
        metrics_text = QTextEdit()
        metrics_text.setReadOnly(True)
        
        metrics = f"""성능 메트릭
============

총 실행 시간: {self.execution_time}초
평균 처리 시간: {self.execution_time/self.total_rows if self.total_rows > 0 else 0:.2f}초/행
처리 속도: {(self.total_rows/self.execution_time*60) if self.execution_time > 0 else 0:.1f}행/분

메모리 사용량: N/A
CPU 사용률: N/A

실행 환경:
- 실행 모드: Excel 워크플로우
- 병렬 처리: 비활성화
- 오류 처리: 계속 진행
"""
        
        # Add step-by-step timing if available
        if hasattr(self, 'step_timings'):
            metrics += "\n\n단계별 평균 실행 시간:\n"
            for step_name, avg_time in self.step_timings.items():
                metrics += f"- {step_name}: {avg_time:.2f}ms\n"
        
        metrics_text.setPlainText(metrics)
        layout.addWidget(metrics_text)
        
        widget.setLayout(layout)
        return widget
        
    def export_to_csv(self):
        """Export report to CSV"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "CSV로 내보내기",
            f"execution_report_{QDateTime.currentDateTime().toString('yyyyMMdd_hhmmss')}.csv",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write summary
                    writer.writerow(["실행 리포트"])
                    writer.writerow(["실행 시간", QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")])
                    writer.writerow([])
                    writer.writerow(["전체 행", self.total_rows])
                    writer.writerow(["성공", self.successful_rows])
                    writer.writerow(["실패", self.failed_rows])
                    writer.writerow(["성공률", f"{(self.successful_rows/self.total_rows*100) if self.total_rows > 0 else 0:.1f}%"])
                    writer.writerow([])
                    
                    # Write failed rows
                    if self.failed_details:
                        writer.writerow(["실패 상세"])
                        writer.writerow(["행 번호", "오류 메시지", "실패 단계"])
                        for detail in self.failed_details:
                            writer.writerow([
                                detail.get('row_index', 0) + 1,
                                detail.get('error', 'Unknown error'),
                                detail.get('failed_step', 'Unknown')
                            ])
                            
                QMessageBox.information(self, "성공", "리포트가 CSV 파일로 저장되었습니다.")
            except Exception as e:
                QMessageBox.critical(self, "오류", f"CSV 저장 실패: {str(e)}")
                
    def export_to_json(self):
        """Export report to JSON"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "JSON으로 내보내기",
            f"execution_report_{QDateTime.currentDateTime().toString('yyyyMMdd_hhmmss')}.json",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                report_data = {
                    "timestamp": QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss"),
                    "summary": {
                        "total_rows": self.total_rows,
                        "successful_rows": self.successful_rows,
                        "failed_rows": self.failed_rows,
                        "success_rate": (self.successful_rows/self.total_rows*100) if self.total_rows > 0 else 0,
                        "execution_time_seconds": self.execution_time
                    },
                    "failed_details": self.failed_details
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, ensure_ascii=False, indent=2)
                    
                QMessageBox.information(self, "성공", "리포트가 JSON 파일로 저장되었습니다.")
            except Exception as e:
                QMessageBox.critical(self, "오류", f"JSON 저장 실패: {str(e)}")
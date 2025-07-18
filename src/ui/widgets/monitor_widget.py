"""
시스템 모니터링 위젯
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QGroupBox, QTextEdit, QPushButton,
    QListWidget, QListWidgetItem, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QPalette
from utils.background_monitor import get_monitor
from datetime import datetime

class SystemHealthWidget(QWidget):
    """시스템 건강 상태 표시 위젯"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        
        # 상태 인디케이터
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("font-size: 24px;")
        layout.addWidget(self.status_indicator)
        
        # 상태 텍스트
        self.status_label = QLabel("시스템 상태: 정상")
        self.status_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def update_status(self, status: str):
        """상태 업데이트"""
        colors = {
            "정상": "#4CAF50",
            "주의": "#FF9800",
            "위험": "#F44336"
        }
        
        color = colors.get(status, "#757575")
        self.status_indicator.setStyleSheet(f"font-size: 24px; color: {color};")
        self.status_label.setText(f"시스템 상태: {status}")

class MetricsWidget(QWidget):
    """메트릭 표시 위젯"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QGridLayout()
        
        # CPU 사용률
        layout.addWidget(QLabel("CPU:"), 0, 0)
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setTextVisible(True)
        layout.addWidget(self.cpu_bar, 0, 1)
        
        # 메모리 사용률
        layout.addWidget(QLabel("메모리:"), 1, 0)
        self.memory_bar = QProgressBar()
        self.memory_bar.setTextVisible(True)
        layout.addWidget(self.memory_bar, 1, 1)
        
        # 디스크 사용률
        layout.addWidget(QLabel("디스크:"), 2, 0)
        self.disk_bar = QProgressBar()
        self.disk_bar.setTextVisible(True)
        layout.addWidget(self.disk_bar, 2, 1)
        
        # 스레드 수
        layout.addWidget(QLabel("스레드:"), 3, 0)
        self.thread_label = QLabel("0")
        layout.addWidget(self.thread_label, 3, 1)
        
        self.setLayout(layout)
        
    def update_metrics(self, metrics: dict):
        """메트릭 업데이트"""
        if 'cpu_percent' in metrics:
            self.cpu_bar.setValue(int(metrics['cpu_percent']))
            
        if 'memory_percent' in metrics:
            self.memory_bar.setValue(int(metrics['memory_percent']))
            
        if 'disk_percent' in metrics:
            self.disk_bar.setValue(int(metrics['disk_percent']))
            
        if 'thread_count' in metrics:
            self.thread_label.setText(f"{metrics['thread_count']}개")

class AlertListWidget(QListWidget):
    """알림 목록 위젯"""
    
    def __init__(self):
        super().__init__()
        self.setMaximumHeight(150)
        
    def add_alert(self, rule_name: str, message: str):
        """알림 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        item = QListWidgetItem(f"[{timestamp}] {message}")
        
        # 규칙에 따른 색상
        if "high" in rule_name or "위험" in message:
            item.setForeground(QColor("#F44336"))
        elif "주의" in message:
            item.setForeground(QColor("#FF9800"))
            
        self.insertItem(0, item)
        
        # 최대 20개만 유지
        while self.count() > 20:
            self.takeItem(self.count() - 1)

class MonitorWidget(QWidget):
    """모니터링 통합 위젯"""
    
    def __init__(self):
        super().__init__()
        self.monitor = get_monitor()
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 건강 상태
        self.health_widget = SystemHealthWidget()
        layout.addWidget(self.health_widget)
        
        # 메트릭
        metrics_group = QGroupBox("시스템 메트릭")
        metrics_layout = QVBoxLayout()
        self.metrics_widget = MetricsWidget()
        metrics_layout.addWidget(self.metrics_widget)
        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)
        
        # 알림
        alerts_group = QGroupBox("최근 알림")
        alerts_layout = QVBoxLayout()
        self.alert_list = AlertListWidget()
        alerts_layout.addWidget(self.alert_list)
        alerts_group.setLayout(alerts_layout)
        layout.addWidget(alerts_group)
        
        # 컨트롤 버튼
        control_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("모니터링 시작")
        self.start_btn.clicked.connect(self.start_monitoring)
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("모니터링 중지")
        self.stop_btn.clicked.connect(self.stop_monitoring)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        self.report_btn = QPushButton("리포트 보기")
        self.report_btn.clicked.connect(self.show_report)
        control_layout.addWidget(self.report_btn)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        self.setLayout(layout)
        
    def setup_connections(self):
        """시그널 연결"""
        self.monitor.health_status_changed.connect(self.health_widget.update_status)
        self.monitor.metrics_updated.connect(self.metrics_widget.update_metrics)
        self.monitor.alert_signal.connect(self.alert_list.add_alert)
        
    def start_monitoring(self):
        """모니터링 시작"""
        self.monitor.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitor.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
    def show_report(self):
        """리포트 표시"""
        report = self.monitor.get_status_report()
        
        # 리포트 다이얼로그 표시
        from PyQt5.QtWidgets import QDialog, QTextEdit, QVBoxLayout
        import json
        
        dialog = QDialog(self)
        dialog.setWindowTitle("시스템 모니터링 리포트")
        dialog.resize(600, 400)
        
        layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(json.dumps(report, ensure_ascii=False, indent=2))
        layout.addWidget(text_edit)
        
        dialog.setLayout(layout)
        dialog.exec_()
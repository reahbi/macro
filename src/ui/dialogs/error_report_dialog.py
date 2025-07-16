"""
Error reporting dialog with detailed information and solutions
"""

import traceback
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QGroupBox, QTabWidget,
    QWidget, QCheckBox, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
import pyautogui

class ErrorReportDialog(QDialog):
    """Dialog for displaying detailed error information"""
    
    # Error solutions database
    ERROR_SOLUTIONS = {
        "Image not found": {
            "원인": [
                "화면 해상도가 변경되었습니다",
                "대상 프로그램의 UI가 변경되었습니다",
                "이미지 파일이 손상되었거나 이동되었습니다",
                "화면 배율(DPI) 설정이 다릅니다"
            ],
            "해결 방법": [
                "이미지를 다시 캡처하세요",
                "화면 해상도를 원래대로 복원하세요",
                "Windows 디스플레이 설정에서 배율을 100%로 설정하세요",
                "대상 프로그램을 최대화하고 다시 시도하세요"
            ]
        },
        "Text not found": {
            "원인": [
                "텍스트가 화면에 표시되지 않았습니다",
                "OCR 인식 실패",
                "폰트나 텍스트 크기가 변경되었습니다",
                "검색 영역이 잘못 지정되었습니다"
            ],
            "해결 방법": [
                "검색할 텍스트가 화면에 표시되는지 확인하세요",
                "검색 영역을 다시 지정하세요",
                "정확한 텍스트 대신 부분 일치를 사용하세요",
                "대기 시간을 늘려보세요"
            ]
        },
        "Permission denied": {
            "원인": [
                "관리자 권한이 필요합니다",
                "파일이 다른 프로그램에서 사용 중입니다",
                "폴더에 쓰기 권한이 없습니다"
            ],
            "해결 방법": [
                "프로그램을 관리자 권한으로 실행하세요",
                "다른 프로그램에서 파일을 닫고 다시 시도하세요",
                "다른 위치에 저장해보세요"
            ]
        },
        "Excel": {
            "원인": [
                "Excel 파일이 열려있습니다",
                "시트 이름이 변경되었습니다",
                "열 이름이 변경되었습니다"
            ],
            "해결 방법": [
                "Excel 파일을 닫고 다시 시도하세요",
                "시트 매핑을 다시 설정하세요",
                "열 매핑을 확인하세요"
            ]
        }
    }
    
    def __init__(self, error_type: str, error_message: str, 
                 error_details: Optional[str] = None,
                 log_file: Optional[Path] = None,
                 parent=None):
        super().__init__(parent)
        self.error_type = error_type
        self.error_message = error_message
        self.error_details = error_details or traceback.format_exc()
        self.log_file = log_file
        self.screenshot_path = None
        
        self.init_ui()
        self.load_error_info()
        
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("오류 보고서")
        self.setModal(True)
        self.resize(700, 500)
        
        layout = QVBoxLayout()
        
        # Error summary
        error_group = QGroupBox("오류 요약")
        error_layout = QVBoxLayout()
        
        # Error icon and message
        message_layout = QHBoxLayout()
        
        # Error type label with red color
        type_label = QLabel(f"❌ {self.error_type}")
        type_label.setStyleSheet("color: red; font-size: 14px; font-weight: bold;")
        error_layout.addWidget(type_label)
        
        # Error message
        message_label = QLabel(self.error_message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("font-size: 12px; margin: 10px 0;")
        error_layout.addWidget(message_label)
        
        error_group.setLayout(error_layout)
        layout.addWidget(error_group)
        
        # Tab widget for details
        self.tabs = QTabWidget()
        
        # Solutions tab
        self.solutions_widget = self.create_solutions_tab()
        self.tabs.addTab(self.solutions_widget, "해결 방법")
        
        # Details tab
        self.details_widget = self.create_details_tab()
        self.tabs.addTab(self.details_widget, "상세 정보")
        
        # Log tab
        if self.log_file:
            self.log_widget = self.create_log_tab()
            self.tabs.addTab(self.log_widget, "실행 로그")
            
        layout.addWidget(self.tabs)
        
        # Actions
        action_layout = QHBoxLayout()
        
        # Screenshot checkbox
        self.screenshot_check = QCheckBox("오류 화면 캡처 포함")
        self.screenshot_check.setChecked(True)
        action_layout.addWidget(self.screenshot_check)
        
        action_layout.addStretch()
        
        # Copy button
        copy_btn = QPushButton("오류 정보 복사")
        copy_btn.clicked.connect(self.copy_error_info)
        action_layout.addWidget(copy_btn)
        
        # Save button
        save_btn = QPushButton("보고서 저장")
        save_btn.clicked.connect(self.save_report)
        action_layout.addWidget(save_btn)
        
        layout.addLayout(action_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Open log folder button
        if self.log_file:
            log_folder_btn = QPushButton("로그 폴더 열기")
            log_folder_btn.clicked.connect(self.open_log_folder)
            button_layout.addWidget(log_folder_btn)
        
        # OK button
        ok_btn = QPushButton("확인")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def create_solutions_tab(self) -> QWidget:
        """Create solutions tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Find matching error type
        matching_solution = None
        for key, solution in self.ERROR_SOLUTIONS.items():
            if key.lower() in self.error_message.lower():
                matching_solution = solution
                break
                
        if matching_solution:
            # Possible causes
            causes_group = QGroupBox("가능한 원인")
            causes_layout = QVBoxLayout()
            
            for cause in matching_solution["원인"]:
                cause_label = QLabel(f"• {cause}")
                cause_label.setWordWrap(True)
                causes_layout.addWidget(cause_label)
                
            causes_group.setLayout(causes_layout)
            layout.addWidget(causes_group)
            
            # Solutions
            solutions_group = QGroupBox("해결 방법")
            solutions_layout = QVBoxLayout()
            
            for i, solution in enumerate(matching_solution["해결 방법"], 1):
                solution_label = QLabel(f"{i}. {solution}")
                solution_label.setWordWrap(True)
                solution_label.setStyleSheet("margin: 5px 0;")
                solutions_layout.addWidget(solution_label)
                
            solutions_group.setLayout(solutions_layout)
            layout.addWidget(solutions_group)
        else:
            # Generic solutions
            generic_label = QLabel(
                "일반적인 해결 방법:\n\n"
                "1. 프로그램을 다시 시작해보세요\n"
                "2. 대상 프로그램이 정상적으로 실행 중인지 확인하세요\n"
                "3. 화면 해상도나 배율 설정을 확인하세요\n"
                "4. 매크로 단계를 다시 설정해보세요\n"
                "5. 문제가 지속되면 로그 파일과 함께 문의하세요"
            )
            generic_label.setWordWrap(True)
            layout.addWidget(generic_label)
            
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_details_tab(self) -> QWidget:
        """Create error details tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Error details text
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setFont(QFont("Consolas", 9))
        self.details_text.setPlainText(self.error_details)
        
        layout.addWidget(self.details_text)
        widget.setLayout(layout)
        return widget
        
    def create_log_tab(self) -> QWidget:
        """Create log file tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Log file path
        path_label = QLabel(f"로그 파일: {self.log_file}")
        path_label.setWordWrap(True)
        layout.addWidget(path_label)
        
        # Log preview (last 50 lines)
        log_text = QTextEdit()
        log_text.setReadOnly(True)
        log_text.setFont(QFont("Consolas", 9))
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Show last 50 lines
                last_lines = lines[-50:] if len(lines) > 50 else lines
                log_text.setPlainText(''.join(last_lines))
        except Exception as e:
            log_text.setPlainText(f"로그 파일을 읽을 수 없습니다: {e}")
            
        layout.addWidget(log_text)
        widget.setLayout(layout)
        return widget
        
    def load_error_info(self):
        """Load additional error information"""
        # Could load more context here
        pass
        
    def copy_error_info(self):
        """Copy error information to clipboard"""
        from PyQt5.QtWidgets import QApplication
        
        info = f"""오류 타입: {self.error_type}
오류 메시지: {self.error_message}
발생 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

상세 정보:
{self.error_details}
"""
        
        if self.log_file:
            info += f"\n로그 파일: {self.log_file}"
            
        QApplication.clipboard().setText(info)
        QMessageBox.information(self, "복사 완료", "오류 정보가 클립보드에 복사되었습니다.")
        
    def save_report(self):
        """Save error report to file"""
        from PyQt5.QtWidgets import QFileDialog
        
        # Take screenshot if requested
        if self.screenshot_check.isChecked():
            self.capture_screenshot()
            
        # Get save location
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"error_report_{timestamp}.txt"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "오류 보고서 저장",
            default_name,
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"오류 보고서\n")
                    f.write(f"=" * 50 + "\n\n")
                    f.write(f"발생 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"오류 타입: {self.error_type}\n")
                    f.write(f"오류 메시지: {self.error_message}\n\n")
                    
                    # Add solutions if available
                    for key, solution in self.ERROR_SOLUTIONS.items():
                        if key.lower() in self.error_message.lower():
                            f.write("\n가능한 원인:\n")
                            for cause in solution["원인"]:
                                f.write(f"  • {cause}\n")
                            f.write("\n해결 방법:\n")
                            for i, sol in enumerate(solution["해결 방법"], 1):
                                f.write(f"  {i}. {sol}\n")
                            break
                            
                    f.write(f"\n상세 정보:\n")
                    f.write(f"{self.error_details}\n")
                    
                    if self.log_file:
                        f.write(f"\n로그 파일: {self.log_file}\n")
                        
                    if self.screenshot_path:
                        f.write(f"\n스크린샷: {self.screenshot_path}\n")
                        
                QMessageBox.information(self, "저장 완료", f"오류 보고서가 저장되었습니다:\n{file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "저장 실패", f"보고서 저장 중 오류가 발생했습니다:\n{str(e)}")
                
    def capture_screenshot(self):
        """Capture screenshot of current screen"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_dir = Path.home() / ".excel_macro_automation" / "error_screenshots"
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            
            self.screenshot_path = screenshot_dir / f"error_{timestamp}.png"
            pyautogui.screenshot(str(self.screenshot_path))
            
        except Exception as e:
            self.screenshot_path = None
            
    def open_log_folder(self):
        """Open log folder in file explorer"""
        if self.log_file:
            log_dir = os.path.dirname(self.log_file)
            os.startfile(log_dir)  # Windows only
            
    @staticmethod
    def show_error(error_type: str, error_message: str, 
                   error_details: Optional[str] = None,
                   log_file: Optional[Path] = None,
                   parent=None):
        """Static method to show error dialog"""
        dialog = ErrorReportDialog(error_type, error_message, error_details, log_file, parent)
        dialog.exec_()
        return dialog
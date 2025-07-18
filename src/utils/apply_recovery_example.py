"""
오류 복구 시스템 적용 예시
"""

from utils.error_decorator import auto_recover, ErrorContext, file_context, excel_context

# 예시 1: 파일 작업에 자동 복구 적용
@auto_recover(retry_count=2, context_func=file_context)
def load_macro_file(file_path: str):
    """매크로 파일 로드 - 인코딩 오류 자동 복구"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 예시 2: 엑셀 작업에 자동 복구 적용
@auto_recover(retry_count=1, context_func=excel_context)
def load_excel_data(excel_manager, sheet_name):
    """엑셀 데이터 로드 - 권한/경로 오류 자동 복구"""
    return excel_manager.read_sheet(sheet_name)

# 예시 3: UI 작업에 오류 컨텍스트 사용
def create_dialog(parent_window):
    """다이얼로그 생성 - Qt 오류 자동 처리"""
    with ErrorContext("다이얼로그 생성", window=parent_window):
        dialog = SomeDialog(parent_window)
        dialog.show()
        return dialog

# 예시 4: 기존 클래스 메서드에 적용
class EnhancedExcelManager:
    @auto_recover(retry_count=2)
    def save_file(self, file_path=None):
        """파일 저장 - 권한/경로 오류 자동 복구"""
        # 기존 save_file 로직
        pass
        
    @auto_recover(retry_count=1)
    def load_file(self, file_path):
        """파일 로드 - 인코딩 오류 자동 복구"""
        # 기존 load_file 로직
        pass

# 예시 5: 실행 엔진에 적용
class EnhancedExecutionEngine:
    @auto_recover(retry_count=3)
    def execute_step(self, step):
        """단계 실행 - 일시적 오류 자동 재시도"""
        # 기존 execute_step 로직
        pass
        
# 사용 방법:
# 1. 기존 함수/메서드에 @auto_recover 데코레이터 추가
# 2. context_func 매개변수로 오류 컨텍스트 제공 (선택사항)
# 3. retry_count로 재시도 횟수 설정
# 4. ErrorContext 컨텍스트 매니저 사용 (블록 단위 보호)
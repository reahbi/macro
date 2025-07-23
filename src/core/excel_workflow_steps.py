"""
Excel workflow specific step types
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .macro_types import MacroStep, StepType, ErrorHandling
import uuid


@dataclass
class ExcelRowStartStep(MacroStep):
    """Excel 행 반복 시작 - 현재 행의 데이터를 변수로 로드"""
    step_type: StepType = field(default=StepType.EXCEL_ROW_START, init=False)
    
    # 반복 설정
    repeat_mode: str = "incomplete_only"  # incomplete_only, specific_count, range, all
    repeat_count: int = 0  # specific_count 모드에서 사용
    start_row: int = 0    # range 모드에서 사용
    end_row: int = 0      # range 모드에서 사용
    
    # 자동으로 생성되는 pair ID (끝 단계와 매칭용)
    pair_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def validate(self) -> List[str]:
        errors = []
        if self.repeat_mode == "specific_count" and self.repeat_count <= 0:
            errors.append("반복 횟수는 1 이상이어야 합니다")
        if self.repeat_mode == "range":
            if self.start_row < 0:
                errors.append("시작 행은 0 이상이어야 합니다")
            if self.end_row < self.start_row:
                errors.append("끝 행은 시작 행보다 커야 합니다")
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "repeat_mode": self.repeat_mode,
            "repeat_count": self.repeat_count,
            "start_row": self.start_row,
            "end_row": self.end_row,
            "pair_id": self.pair_id
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExcelRowStartStep':
        return cls(
            step_id=data.get("step_id", str(uuid.uuid4())),
            name=data.get("name", "Excel 행 시작"),
            description=data.get("description", ""),
            enabled=data.get("enabled", True),
            error_handling=ErrorHandling(data.get("error_handling", "continue")),
            retry_count=data.get("retry_count", 0),
            repeat_mode=data.get("repeat_mode", "incomplete_only"),
            repeat_count=data.get("repeat_count", 0),
            start_row=data.get("start_row", 0),
            end_row=data.get("end_row", 0),
            pair_id=data.get("pair_id", str(uuid.uuid4()))
        )


@dataclass 
class ExcelRowEndStep(MacroStep):
    """Excel 행 반복 끝 - 현재 행을 완료 처리하고 다음 행으로"""
    step_type: StepType = field(default=StepType.EXCEL_ROW_END, init=False)
    
    # 시작 단계와 매칭되는 pair ID
    pair_id: str = ""
    
    # 완료 시 상태 설정
    mark_as_complete: bool = True
    completion_status: str = "완료"  # 완료, 처리됨, 확인됨 등
    
    def validate(self) -> List[str]:
        errors = []
        if not self.pair_id:
            errors.append("Excel 시작 단계와 연결되지 않았습니다")
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "pair_id": self.pair_id,
            "mark_as_complete": self.mark_as_complete,
            "completion_status": self.completion_status
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExcelRowEndStep':
        return cls(
            step_id=data.get("step_id", str(uuid.uuid4())),
            name=data.get("name", "Excel 행 끝"),
            description=data.get("description", ""),
            enabled=data.get("enabled", True),
            error_handling=ErrorHandling(data.get("error_handling", "continue")),
            retry_count=data.get("retry_count", 0),
            pair_id=data.get("pair_id", ""),
            mark_as_complete=data.get("mark_as_complete", True),
            completion_status=data.get("completion_status", "완료")
        )


class ExcelWorkflowBlock:
    """Excel 반복 블록을 나타내는 헬퍼 클래스"""
    
    def __init__(self):
        self.pair_id = str(uuid.uuid4())
        self.start_step = None
        self.end_step = None
        self.inner_steps = []
        
    def create_block(self, repeat_mode="incomplete_only", **kwargs):
        """시작과 끝 단계를 한 번에 생성"""
        self.start_step = ExcelRowStartStep(
            name="Excel 행 반복 시작",
            repeat_mode=repeat_mode,
            pair_id=self.pair_id,
            **kwargs
        )
        
        self.end_step = ExcelRowEndStep(
            name="Excel 행 반복 끝",
            pair_id=self.pair_id
        )
        
        return self.start_step, self.end_step
    
    def add_inner_step(self, step: MacroStep):
        """블록 내부에 단계 추가"""
        self.inner_steps.append(step)
        
    def get_all_steps(self) -> List[MacroStep]:
        """전체 단계 목록 반환"""
        if not self.start_step or not self.end_step:
            raise ValueError("블록이 아직 생성되지 않았습니다")
        
        return [self.start_step] + self.inner_steps + [self.end_step]
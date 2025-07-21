"""
Progress calculator for macro execution
Handles both Excel-based and standalone execution progress tracking
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
from core.macro_types import MacroStep, LoopStep, IfConditionStep, StepType
from logger.app_logger import get_logger


class ExecutionMode(Enum):
    """Execution modes"""
    EXCEL = "excel"
    STANDALONE = "standalone"


@dataclass
class StepInfo:
    """Information about a step in the macro"""
    index: int
    step: MacroStep
    parent_loop: Optional['LoopStep'] = None
    is_conditional: bool = False
    condition_branch: Optional[str] = None  # 'true' or 'false' for conditional steps


@dataclass
class ProgressInfo:
    """Detailed progress information"""
    mode: ExecutionMode
    percentage: float
    # Excel mode
    current_row: Optional[int] = None
    total_rows: Optional[int] = None
    row_identifier: Optional[str] = None
    # Step information
    current_step_index: Optional[int] = None
    total_steps: Optional[int] = None
    current_step_name: Optional[str] = None
    current_step_type: Optional[str] = None
    # Loop information
    in_loop: bool = False
    loop_iteration: Optional[int] = None
    loop_total: Optional[int] = None
    # Sub-progress
    sub_percentage: Optional[float] = None


class ProgressCalculator:
    """Calculate execution progress for macro execution"""
    
    def __init__(self, mode: ExecutionMode):
        self.mode = mode
        self.logger = get_logger(__name__)
        
        # Excel mode tracking
        self.total_rows = 0
        self.completed_rows = 0
        self.current_row_index = 0
        
        # Step tracking
        self.macro_steps: List[StepInfo] = []
        self.total_steps = 0
        self.current_step_index = 0
        self.completed_steps = 0
        
        # Loop tracking
        self.loop_states: Dict[str, Dict[str, Any]] = {}  # step_id -> loop state
        
        # Dynamic step count (for conditional branches)
        self.executed_steps = []
        self.skipped_steps = []
        
    def initialize_macro(self, macro: 'Macro', total_rows: Optional[int] = None):
        """Initialize calculator with macro structure"""
        self.total_rows = total_rows or 1
        self.completed_rows = 0
        self.current_row_index = 0
        
        # Flatten macro structure
        self.macro_steps = self._flatten_steps(macro.steps)
        self.total_steps = len(self.macro_steps)
        
        self.logger.info(f"Initialized progress calculator: mode={self.mode.value}, "
                        f"total_rows={self.total_rows}, total_steps={self.total_steps}")
        
    def _flatten_steps(self, steps: List[MacroStep], parent_loop: Optional[LoopStep] = None) -> List[StepInfo]:
        """Flatten nested step structure for counting"""
        flattened = []
        
        for i, step in enumerate(steps):
            if not step.enabled:
                continue
                
            # Create step info
            step_info = StepInfo(
                index=len(flattened),
                step=step,
                parent_loop=parent_loop
            )
            
            if isinstance(step, LoopStep):
                # Add the loop step itself
                flattened.append(step_info)
                
                # Add nested steps (they will be counted multiple times during execution)
                # For progress calculation, we count them once
                if step.steps:
                    nested = self._flatten_steps(step.steps, parent_loop=step)
                    flattened.extend(nested)
                    
            elif isinstance(step, IfConditionStep):
                # Add the condition step
                step_info.is_conditional = True
                flattened.append(step_info)
                
                # For progress calculation, we estimate by including the larger branch
                true_count = len(self._flatten_steps(step.true_steps)) if step.true_steps else 0
                false_count = len(self._flatten_steps(step.false_steps)) if step.false_steps else 0
                
                # Add the branch that has more steps (worst case for progress)
                if true_count >= false_count and step.true_steps:
                    branch_steps = self._flatten_steps(step.true_steps)
                    for branch_step in branch_steps:
                        branch_step.condition_branch = 'true'
                    flattened.extend(branch_steps)
                elif step.false_steps:
                    branch_steps = self._flatten_steps(step.false_steps)
                    for branch_step in branch_steps:
                        branch_step.condition_branch = 'false'
                    flattened.extend(branch_steps)
            else:
                # Regular step
                flattened.append(step_info)
                
        return flattened
        
    def start_row(self, row_index: int, row_data: Optional[Dict[str, Any]] = None):
        """Start processing a new row"""
        self.current_row_index = row_index
        self.current_step_index = 0
        self.completed_steps = 0
        self.executed_steps = []
        self.skipped_steps = []
        
        # Reset loop states for new row
        self.loop_states.clear()
        
        self.logger.debug(f"Started row {row_index + 1}/{self.total_rows}")
        
    def complete_row(self, row_index: int):
        """Mark a row as completed"""
        self.completed_rows += 1
        self.logger.debug(f"Completed row {row_index + 1}/{self.total_rows}")
        
    def start_step(self, step: MacroStep, step_index: Optional[int] = None):
        """Mark a step as started"""
        if step_index is not None:
            self.current_step_index = step_index
        else:
            # Find step in flattened list
            for i, step_info in enumerate(self.macro_steps):
                if step_info.step.step_id == step.step_id:
                    self.current_step_index = i
                    break
                    
        self.executed_steps.append(step.step_id)
        
        # Handle loop state
        if isinstance(step, LoopStep):
            if step.step_id not in self.loop_states:
                self.loop_states[step.step_id] = {
                    'current_iteration': 0,
                    'total_iterations': self._calculate_loop_iterations(step)
                }
                
    def complete_step(self, step: MacroStep):
        """Mark a step as completed"""
        self.completed_steps += 1
        
        # Update loop state
        if isinstance(step, LoopStep):
            if step.step_id in self.loop_states:
                self.loop_states[step.step_id]['current_iteration'] += 1
                
    def enter_loop_iteration(self, loop_step: LoopStep, iteration: int):
        """Enter a new loop iteration"""
        if loop_step.step_id not in self.loop_states:
            self.loop_states[loop_step.step_id] = {
                'current_iteration': iteration,
                'total_iterations': self._calculate_loop_iterations(loop_step)
            }
        else:
            self.loop_states[loop_step.step_id]['current_iteration'] = iteration
            
    def _calculate_loop_iterations(self, loop_step: LoopStep) -> int:
        """Calculate total iterations for a loop"""
        if loop_step.loop_type == "fixed_count":
            return loop_step.loop_count
        elif loop_step.loop_type == "excel_rows":
            return self.total_rows
        else:
            return 1  # Unknown, assume 1
            
    def skip_steps(self, steps: List[MacroStep]):
        """Mark steps as skipped (e.g., in conditional branches)"""
        for step in steps:
            self.skipped_steps.append(step.step_id)
            
    def calculate_progress(self) -> ProgressInfo:
        """Calculate current progress"""
        if self.mode == ExecutionMode.EXCEL:
            return self._calculate_excel_progress()
        else:
            return self._calculate_standalone_progress()
            
    def _calculate_excel_progress(self) -> ProgressInfo:
        """Calculate progress for Excel mode"""
        # Main progress based on rows
        row_progress = self.completed_rows / self.total_rows if self.total_rows > 0 else 0
        
        # Sub progress based on steps in current row
        if self.total_steps > 0:
            # Adjust for executed vs total steps (handling conditionals)
            effective_total = len(self.executed_steps) + len([s for s in self.macro_steps 
                                                             if s.step.step_id not in self.executed_steps 
                                                             and s.step.step_id not in self.skipped_steps])
            step_progress = len(self.executed_steps) / effective_total if effective_total > 0 else 0
        else:
            step_progress = 0
            
        # Combined progress
        if self.total_rows > 0:
            overall_percentage = (row_progress + (step_progress / self.total_rows)) * 100
        else:
            overall_percentage = step_progress * 100
            
        # Get current step info
        current_step_info = None
        if 0 <= self.current_step_index < len(self.macro_steps):
            current_step_info = self.macro_steps[self.current_step_index]
            
        # Check if in loop
        in_loop = False
        loop_iteration = None
        loop_total = None
        
        if current_step_info and current_step_info.parent_loop:
            in_loop = True
            loop_id = current_step_info.parent_loop.step_id
            if loop_id in self.loop_states:
                loop_iteration = self.loop_states[loop_id]['current_iteration'] + 1
                loop_total = self.loop_states[loop_id]['total_iterations']
                
        return ProgressInfo(
            mode=self.mode,
            percentage=overall_percentage,
            current_row=self.current_row_index + 1,
            total_rows=self.total_rows,
            current_step_index=self.current_step_index + 1,
            total_steps=effective_total,
            current_step_name=current_step_info.step.name if current_step_info else None,
            current_step_type=current_step_info.step.step_type.value if current_step_info else None,
            in_loop=in_loop,
            loop_iteration=loop_iteration,
            loop_total=loop_total,
            sub_percentage=step_progress * 100
        )
        
    def _calculate_standalone_progress(self) -> ProgressInfo:
        """Calculate progress for standalone mode"""
        # Progress based on steps only
        if self.total_steps > 0:
            # Adjust for executed vs total steps (handling conditionals)
            effective_total = len(self.executed_steps) + len([s for s in self.macro_steps 
                                                             if s.step.step_id not in self.executed_steps 
                                                             and s.step.step_id not in self.skipped_steps])
            percentage = (len(self.executed_steps) / effective_total * 100) if effective_total > 0 else 0
        else:
            percentage = 0
            
        # Get current step info
        current_step_info = None
        if 0 <= self.current_step_index < len(self.macro_steps):
            current_step_info = self.macro_steps[self.current_step_index]
            
        # Check if in loop
        in_loop = False
        loop_iteration = None
        loop_total = None
        
        if current_step_info and current_step_info.parent_loop:
            in_loop = True
            loop_id = current_step_info.parent_loop.step_id
            if loop_id in self.loop_states:
                loop_iteration = self.loop_states[loop_id]['current_iteration'] + 1
                loop_total = self.loop_states[loop_id]['total_iterations']
                
        return ProgressInfo(
            mode=self.mode,
            percentage=percentage,
            current_step_index=self.current_step_index + 1,
            total_steps=len(self.executed_steps) + len([s for s in self.macro_steps 
                                                       if s.step.step_id not in self.executed_steps 
                                                       and s.step.step_id not in self.skipped_steps]),
            current_step_name=current_step_info.step.name if current_step_info else None,
            current_step_type=current_step_info.step.step_type.value if current_step_info else None,
            in_loop=in_loop,
            loop_iteration=loop_iteration,
            loop_total=loop_total
        )
        
    def get_display_text(self, progress_info: ProgressInfo, 
                        include_identifier: bool = True,
                        include_step: bool = True) -> str:
        """Get formatted display text for progress"""
        parts = []
        
        if progress_info.mode == ExecutionMode.EXCEL:
            # Row information
            if progress_info.current_row and progress_info.total_rows:
                text = f"행 {progress_info.current_row}/{progress_info.total_rows}"
                if include_identifier and progress_info.row_identifier:
                    text += f" - {progress_info.row_identifier}"
                parts.append(text)
                
        # Step information
        if include_step and progress_info.current_step_index and progress_info.total_steps:
            step_text = f"단계 {progress_info.current_step_index}/{progress_info.total_steps}"
            if progress_info.current_step_name:
                step_text += f": {progress_info.current_step_name}"
            parts.append(step_text)
            
        # Loop information
        if progress_info.in_loop and progress_info.loop_iteration and progress_info.loop_total:
            parts.append(f"반복 {progress_info.loop_iteration}/{progress_info.loop_total}")
            
        return " | ".join(parts) if parts else "준비 중..."
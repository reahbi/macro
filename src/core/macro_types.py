"""
Macro step type definitions
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union, Tuple
from enum import Enum
import uuid
from datetime import datetime

class StepType(Enum):
    """Available macro step types"""
    # Mouse actions
    MOUSE_CLICK = "mouse_click"
    MOUSE_MOVE = "mouse_move"
    MOUSE_DRAG = "mouse_drag"
    MOUSE_SCROLL = "mouse_scroll"
    
    # Keyboard actions
    KEYBOARD_TYPE = "keyboard_type"
    KEYBOARD_HOTKEY = "keyboard_hotkey"
    
    # Wait actions
    WAIT_TIME = "wait_time"
    WAIT_IMAGE = "wait_image"
    WAIT_TEXT = "wait_text"
    
    # Screen actions
    SCREENSHOT = "screenshot"
    IMAGE_SEARCH = "image_search"
    OCR_TEXT = "ocr_text"
    
    # Flow control
    IF_CONDITION = "if_condition"
    LOOP = "loop"
    
    # Excel operations
    EXCEL_READ = "excel_read"
    EXCEL_WRITE = "excel_write"

class ErrorHandling(Enum):
    """Error handling strategies"""
    STOP = "stop"           # Stop execution on error
    CONTINUE = "continue"   # Continue to next step
    RETRY = "retry"         # Retry the step

class MouseButton(Enum):
    """Mouse button types"""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"

class ConditionOperator(Enum):
    """Condition operators for conditional steps"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"

@dataclass
class MacroStep(ABC):
    """Base class for all macro steps"""
    step_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    step_type: StepType = field(init=False)
    name: str = ""
    description: str = ""
    enabled: bool = True
    error_handling: ErrorHandling = ErrorHandling.STOP
    retry_count: int = 0
    
    @abstractmethod
    def validate(self) -> List[str]:
        """Validate step configuration"""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary"""
        base_dict = {
            "step_id": self.step_id,
            "step_type": self.step_type.value,
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "error_handling": self.error_handling.value,
            "retry_count": self.retry_count
        }
        return base_dict
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MacroStep':
        """Create step from dictionary"""
        pass

# Mouse Steps

@dataclass
class MouseClickStep(MacroStep):
    """Mouse click action"""
    step_type: StepType = field(default=StepType.MOUSE_CLICK, init=False)
    x: int = 0
    y: int = 0
    button: MouseButton = MouseButton.LEFT
    clicks: int = 1
    interval: float = 0.0
    relative_to: str = "screen"  # screen, window, image
    
    def validate(self) -> List[str]:
        errors = []
        if self.x < 0 or self.y < 0:
            errors.append("Coordinates must be non-negative")
        if self.clicks < 1:
            errors.append("Click count must be at least 1")
        if self.interval < 0:
            errors.append("Interval must be non-negative")
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "x": self.x,
            "y": self.y,
            "button": self.button.value,
            "clicks": self.clicks,
            "interval": self.interval,
            "relative_to": self.relative_to
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MouseClickStep':
        return cls(
            step_id=data.get("step_id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            enabled=data.get("enabled", True),
            error_handling=ErrorHandling(data.get("error_handling", "stop")),
            retry_count=data.get("retry_count", 0),
            x=data.get("x", 0),
            y=data.get("y", 0),
            button=MouseButton(data.get("button", "left")),
            clicks=data.get("clicks", 1),
            interval=data.get("interval", 0.0),
            relative_to=data.get("relative_to", "screen")
        )

@dataclass
class MouseMoveStep(MacroStep):
    """Mouse move action"""
    step_type: StepType = field(default=StepType.MOUSE_MOVE, init=False)
    x: int = 0
    y: int = 0
    duration: float = 0.0
    relative_to: str = "screen"
    
    def validate(self) -> List[str]:
        errors = []
        if self.x < 0 or self.y < 0:
            errors.append("Coordinates must be non-negative")
        if self.duration < 0:
            errors.append("Duration must be non-negative")
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "x": self.x,
            "y": self.y,
            "duration": self.duration,
            "relative_to": self.relative_to
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MouseMoveStep':
        return cls(
            step_id=data.get("step_id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            enabled=data.get("enabled", True),
            error_handling=ErrorHandling(data.get("error_handling", "stop")),
            retry_count=data.get("retry_count", 0),
            x=data.get("x", 0),
            y=data.get("y", 0),
            duration=data.get("duration", 0.0),
            relative_to=data.get("relative_to", "screen")
        )

# Keyboard Steps

@dataclass
class KeyboardTypeStep(MacroStep):
    """Keyboard typing action"""
    step_type: StepType = field(default=StepType.KEYBOARD_TYPE, init=False)
    text: str = ""
    interval: float = 0.0
    use_variables: bool = True
    
    def validate(self) -> List[str]:
        errors = []
        if not self.text:
            errors.append("Text cannot be empty")
        if self.interval < 0:
            errors.append("Interval must be non-negative")
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "text": self.text,
            "interval": self.interval,
            "use_variables": self.use_variables
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KeyboardTypeStep':
        return cls(
            step_id=data.get("step_id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            enabled=data.get("enabled", True),
            error_handling=ErrorHandling(data.get("error_handling", "stop")),
            retry_count=data.get("retry_count", 0),
            text=data.get("text", ""),
            interval=data.get("interval", 0.0),
            use_variables=data.get("use_variables", True)
        )

@dataclass
class KeyboardHotkeyStep(MacroStep):
    """Keyboard hotkey action"""
    step_type: StepType = field(default=StepType.KEYBOARD_HOTKEY, init=False)
    keys: List[str] = field(default_factory=list)
    
    def validate(self) -> List[str]:
        errors = []
        if not self.keys:
            errors.append("At least one key must be specified")
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "keys": self.keys
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KeyboardHotkeyStep':
        return cls(
            step_id=data.get("step_id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            enabled=data.get("enabled", True),
            error_handling=ErrorHandling(data.get("error_handling", "stop")),
            retry_count=data.get("retry_count", 0),
            keys=data.get("keys", [])
        )

# Wait Steps

@dataclass
class WaitTimeStep(MacroStep):
    """Wait for specified time"""
    step_type: StepType = field(default=StepType.WAIT_TIME, init=False)
    seconds: float = 1.0
    
    def validate(self) -> List[str]:
        errors = []
        if self.seconds <= 0:
            errors.append("Wait time must be positive")
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "seconds": self.seconds
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WaitTimeStep':
        return cls(
            step_id=data.get("step_id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            enabled=data.get("enabled", True),
            error_handling=ErrorHandling(data.get("error_handling", "stop")),
            retry_count=data.get("retry_count", 0),
            seconds=data.get("seconds", 1.0)
        )

@dataclass
class WaitImageStep(MacroStep):
    """Wait for image to appear"""
    step_type: StepType = field(default=StepType.WAIT_IMAGE, init=False)
    image_path: str = ""
    timeout: float = 10.0
    confidence: float = 0.9
    region: Optional[tuple] = None  # (x, y, width, height)
    
    def validate(self) -> List[str]:
        errors = []
        if not self.image_path:
            errors.append("Image path cannot be empty")
        if self.timeout <= 0:
            errors.append("Timeout must be positive")
        if not 0 <= self.confidence <= 1:
            errors.append("Confidence must be between 0 and 1")
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "image_path": self.image_path,
            "timeout": self.timeout,
            "confidence": self.confidence,
            "region": list(self.region) if self.region else None
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WaitImageStep':
        region = data.get("region")
        return cls(
            step_id=data.get("step_id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            enabled=data.get("enabled", True),
            error_handling=ErrorHandling(data.get("error_handling", "stop")),
            retry_count=data.get("retry_count", 0),
            image_path=data.get("image_path", ""),
            timeout=data.get("timeout", 10.0),
            confidence=data.get("confidence", 0.9),
            region=tuple(region) if region else None
        )

@dataclass
class TextSearchStep(MacroStep):
    """Search for dynamic text and click"""
    step_type: StepType = field(default=StepType.OCR_TEXT, init=False)
    search_text: str = ""  # Text to search for (can include {{variables}})
    excel_column: Optional[str] = None  # Excel column to bind for dynamic text
    region: Optional[tuple] = None  # (x, y, width, height)
    exact_match: bool = False
    confidence: float = 0.5
    click_after_find: bool = True
    click_offset: Tuple[int, int] = (0, 0)  # Offset from center of found text
    
    def validate(self) -> List[str]:
        errors = []
        if not self.search_text and not self.excel_column:
            errors.append("Either search text or Excel column must be specified")
        if not 0 <= self.confidence <= 1:
            errors.append("Confidence must be between 0 and 1")
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "search_text": self.search_text,
            "excel_column": self.excel_column,
            "region": list(self.region) if self.region else None,
            "exact_match": self.exact_match,
            "confidence": self.confidence,
            "click_after_find": self.click_after_find,
            "click_offset": list(self.click_offset)
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TextSearchStep':
        region = data.get("region")
        click_offset = data.get("click_offset", [0, 0])
        return cls(
            step_id=data.get("step_id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            enabled=data.get("enabled", True),
            error_handling=ErrorHandling(data.get("error_handling", "stop")),
            retry_count=data.get("retry_count", 0),
            search_text=data.get("search_text", ""),
            excel_column=data.get("excel_column"),
            region=tuple(region) if region else None,
            exact_match=data.get("exact_match", False),
            confidence=data.get("confidence", 0.5),
            click_after_find=data.get("click_after_find", True),
            click_offset=tuple(click_offset)
        )

# Flow Control Steps

@dataclass
class IfConditionStep(MacroStep):
    """Conditional execution"""
    step_type: StepType = field(default=StepType.IF_CONDITION, init=False)
    condition_type: str = "image_exists"  # image_exists, text_exists, variable_equals, variable_contains, variable_greater, variable_less
    condition_value: Dict[str, Any] = field(default_factory=dict)  # Store all condition parameters
    true_steps: List['MacroStep'] = field(default_factory=list)  # Nested steps for true branch
    false_steps: List['MacroStep'] = field(default_factory=list)  # Nested steps for false branch
    
    def validate(self) -> List[str]:
        errors = []
        if not self.condition_type:
            errors.append("Condition type must be specified")
            
        # Validate based on condition type
        if self.condition_type == "image_exists":
            if not self.condition_value.get("image_path"):
                errors.append("Image path must be specified for image_exists condition")
        elif self.condition_type == "text_exists":
            if not self.condition_value.get("text"):
                errors.append("Text must be specified for text_exists condition")
        elif self.condition_type in ["variable_equals", "variable_contains", "variable_greater", "variable_less"]:
            if not self.condition_value.get("variable"):
                errors.append("Variable name must be specified")
            if not self.condition_value.get("compare_value"):
                errors.append("Comparison value must be specified")
                
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "condition_type": self.condition_type,
            "condition_value": self.condition_value,
            "true_steps": [step.to_dict() for step in self.true_steps],
            "false_steps": [step.to_dict() for step in self.false_steps]
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IfConditionStep':
        # StepFactory will be defined later in this module
        # We need to reference it dynamically to avoid forward reference issues
        import sys
        module = sys.modules[__name__]
        StepFactory = getattr(module, 'StepFactory')
        
        # Create true/false steps from data
        true_steps = []
        for step_data in data.get("true_steps", []):
            true_steps.append(StepFactory.from_dict(step_data))
            
        false_steps = []
        for step_data in data.get("false_steps", []):
            false_steps.append(StepFactory.from_dict(step_data))
            
        return cls(
            step_id=data.get("step_id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            enabled=data.get("enabled", True),
            error_handling=ErrorHandling(data.get("error_handling", "stop")),
            retry_count=data.get("retry_count", 0),
            condition_type=data.get("condition_type", "image_exists"),
            condition_value=data.get("condition_value", {}),
            true_steps=true_steps,
            false_steps=false_steps
        )

@dataclass
class LoopStep(MacroStep):
    """Loop execution"""
    step_type: StepType = field(default=StepType.LOOP, init=False)
    loop_type: str = "count"  # count, while_image, for_each_row
    loop_count: int = 1
    loop_steps: List[str] = field(default_factory=list)  # Step IDs to loop
    
    def validate(self) -> List[str]:
        errors = []
        if self.loop_type == "count" and self.loop_count < 1:
            errors.append("Loop count must be at least 1")
        if not self.loop_steps:
            errors.append("Loop must contain at least one step")
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "loop_type": self.loop_type,
            "loop_count": self.loop_count,
            "loop_steps": self.loop_steps
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LoopStep':
        return cls(
            step_id=data.get("step_id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            enabled=data.get("enabled", True),
            error_handling=ErrorHandling(data.get("error_handling", "stop")),
            retry_count=data.get("retry_count", 0),
            loop_type=data.get("loop_type", "count"),
            loop_count=data.get("loop_count", 1),
            loop_steps=data.get("loop_steps", [])
        )

# Additional Step Classes

@dataclass
class ImageSearchStep(MacroStep):
    """Image search and click action"""
    step_type: StepType = field(default=StepType.IMAGE_SEARCH, init=False)
    image_path: str = ""
    confidence: float = 0.9
    region: Optional[tuple] = None  # (x, y, width, height)
    click_after_find: bool = True
    click_offset: Tuple[int, int] = (0, 0)
    double_click: bool = False
    
    def validate(self) -> List[str]:
        errors = []
        if not self.image_path:
            errors.append("Image path cannot be empty")
        if not 0 <= self.confidence <= 1:
            errors.append("Confidence must be between 0 and 1")
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "image_path": self.image_path,
            "confidence": self.confidence,
            "region": list(self.region) if self.region else None,
            "click_after_find": self.click_after_find,
            "click_offset": list(self.click_offset),
            "double_click": self.double_click
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImageSearchStep':
        region = data.get("region")
        click_offset = data.get("click_offset", [0, 0])
        return cls(
            step_id=data.get("step_id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            enabled=data.get("enabled", True),
            error_handling=ErrorHandling(data.get("error_handling", "stop")),
            retry_count=data.get("retry_count", 0),
            image_path=data.get("image_path", ""),
            confidence=data.get("confidence", 0.9),
            region=tuple(region) if region else None,
            click_after_find=data.get("click_after_find", True),
            click_offset=tuple(click_offset),
            double_click=data.get("double_click", False)
        )

@dataclass
class ScreenshotStep(MacroStep):
    """Take screenshot action"""
    step_type: StepType = field(default=StepType.SCREENSHOT, init=False)
    filename_pattern: str = "screenshot_{timestamp}.png"
    save_directory: str = "./screenshots/"
    region: Optional[tuple] = None  # (x, y, width, height)
    
    def validate(self) -> List[str]:
        errors = []
        if not self.filename_pattern:
            errors.append("Filename pattern cannot be empty")
        if not self.save_directory:
            errors.append("Save directory cannot be empty")
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "filename_pattern": self.filename_pattern,
            "save_directory": self.save_directory,
            "region": list(self.region) if self.region else None
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScreenshotStep':
        region = data.get("region")
        return cls(
            step_id=data.get("step_id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            enabled=data.get("enabled", True),
            error_handling=ErrorHandling(data.get("error_handling", "stop")),
            retry_count=data.get("retry_count", 0),
            filename_pattern=data.get("filename_pattern", "screenshot_{timestamp}.png"),
            save_directory=data.get("save_directory", "./screenshots/"),
            region=tuple(region) if region else None
        )

# Step Factory

class StepFactory:
    """Factory for creating macro steps"""
    
    _step_classes = {
        StepType.MOUSE_CLICK: MouseClickStep,
        StepType.MOUSE_MOVE: MouseMoveStep,
        StepType.KEYBOARD_TYPE: KeyboardTypeStep,
        StepType.KEYBOARD_HOTKEY: KeyboardHotkeyStep,
        StepType.WAIT_TIME: WaitTimeStep,
        StepType.WAIT_IMAGE: WaitImageStep,
        StepType.IMAGE_SEARCH: ImageSearchStep,
        StepType.SCREENSHOT: ScreenshotStep,
        StepType.OCR_TEXT: TextSearchStep,
        StepType.IF_CONDITION: IfConditionStep,
        StepType.LOOP: LoopStep
    }
    
    @classmethod
    def create_step(cls, step_type: StepType) -> MacroStep:
        """Create a new step of given type"""
        step_class = cls._step_classes.get(step_type)
        if not step_class:
            raise ValueError(f"Unknown step type: {step_type}")
        return step_class()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MacroStep:
        """Create step from dictionary"""
        step_type = StepType(data.get("step_type"))
        step_class = cls._step_classes.get(step_type)
        if not step_class:
            raise ValueError(f"Unknown step type: {step_type}")
        return step_class.from_dict(data)

# Macro Definition

@dataclass
class Macro:
    """Complete macro definition"""
    macro_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "새 매크로"
    description: str = ""
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    steps: List[MacroStep] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_step(self, step: MacroStep, index: Optional[int] = None):
        """Add step to macro"""
        if index is None:
            self.steps.append(step)
        else:
            self.steps.insert(index, step)
        self.updated_at = datetime.now()
    
    def remove_step(self, step_id: str):
        """Remove step by ID"""
        self.steps = [s for s in self.steps if s.step_id != step_id]
        self.updated_at = datetime.now()
    
    def move_step(self, step_id: str, new_index: int):
        """Move step to new position"""
        step = None
        for i, s in enumerate(self.steps):
            if s.step_id == step_id:
                step = self.steps.pop(i)
                break
        
        if step:
            self.steps.insert(new_index, step)
            self.updated_at = datetime.now()
    
    def validate(self) -> List[str]:
        """Validate entire macro"""
        errors = []
        if not self.name:
            errors.append("Macro name cannot be empty")
        
        # Validate each step
        for i, step in enumerate(self.steps):
            step_errors = step.validate()
            for error in step_errors:
                errors.append(f"Step {i+1} ({step.name}): {error}")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert macro to dictionary"""
        return {
            "macro_id": self.macro_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "steps": [step.to_dict() for step in self.steps],
            "variables": self.variables,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Macro':
        """Create macro from dictionary"""
        # StepFactory is defined in this module
        import sys
        module = sys.modules[__name__]
        StepFactory = getattr(module, 'StepFactory')
        
        steps = []
        for step_data in data.get("steps", []):
            steps.append(StepFactory.from_dict(step_data))
        
        return cls(
            macro_id=data.get("macro_id", str(uuid.uuid4())),
            name=data.get("name", "새 매크로"),
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat())),
            steps=steps,
            variables=data.get("variables", {}),
            metadata=data.get("metadata", {})
        )
"""
Dynamic text search step implementation for OCR-based text finding
"""

from dataclasses import dataclass, field
from typing import Optional, Tuple, Dict, Any, List
import uuid

from .macro_types import MacroStep, StepType


@dataclass
class DynamicTextSearchStep(MacroStep):
    """Dynamic text search and click using OCR"""
    step_type: StepType = field(default=StepType.OCR_TEXT, init=False)
    search_text: str = ""  # Text to search for (supports {{variables}})
    search_region: Optional[Tuple[int, int, int, int]] = None  # (x, y, width, height)
    confidence_threshold: float = 0.7
    click_on_found: bool = True
    fail_if_not_found: bool = True
    monitor_index: Optional[int] = None  # Which monitor to search on
    mask_in_logs: bool = False  # Mask sensitive data in logs
    
    def validate(self) -> List[str]:
        """Validate step configuration"""
        errors = []
        if not self.search_text:
            errors.append("Search text cannot be empty")
        if not 0 <= self.confidence_threshold <= 1:
            errors.append("Confidence threshold must be between 0 and 1")
        if self.search_region and len(self.search_region) != 4:
            errors.append("Search region must be (x, y, width, height)")
        return errors
    
    def update_search_region(self, region: Tuple[int, int, int, int]):
        """Update the search region"""
        self.search_region = region
    
    def get_absolute_search_region(self) -> Optional[Tuple[int, int, int, int]]:
        """Get absolute search region accounting for monitor offset"""
        if not self.search_region:
            return None
            
        # If monitor index specified, adjust coordinates
        if self.monitor_index is not None:
            try:
                import screeninfo
                monitors = screeninfo.get_monitors()
                if 0 <= self.monitor_index < len(monitors):
                    monitor = monitors[self.monitor_index]
                    x, y, w, h = self.search_region
                    return (monitor.x + x, monitor.y + y, w, h)
            except:
                pass
                
        return self.search_region
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary"""
        data = super().to_dict()
        data.update({
            "search_text": self.search_text,
            "search_region": list(self.search_region) if self.search_region else None,
            "confidence_threshold": self.confidence_threshold,
            "click_on_found": self.click_on_found,
            "fail_if_not_found": self.fail_if_not_found,
            "monitor_index": self.monitor_index,
            "mask_in_logs": self.mask_in_logs
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DynamicTextSearchStep':
        """Create step from dictionary"""
        region = data.get("search_region")
        if region and isinstance(region, list) and len(region) == 4:
            region = tuple(region)
        else:
            region = None
            
        return cls(
            step_id=data.get("step_id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            enabled=data.get("enabled", True),
            error_handling=data.get("error_handling", "stop"),
            retry_count=data.get("retry_count", 0),
            search_text=data.get("search_text", ""),
            search_region=region,
            confidence_threshold=data.get("confidence_threshold", 0.7),
            click_on_found=data.get("click_on_found", True),
            fail_if_not_found=data.get("fail_if_not_found", True),
            monitor_index=data.get("monitor_index"),
            mask_in_logs=data.get("mask_in_logs", False)
        )
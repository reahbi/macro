"""
Helper to create text search steps for tests
"""
from dataclasses import dataclass, field
from typing import Optional, Tuple
from core.macro_types import MacroStep, StepType, ErrorHandling

@dataclass
class TextSearchStep(MacroStep):
    """Text search step for testing"""
    step_type: StepType = field(default=StepType.OCR_TEXT, init=False)
    search_text: str = ""
    region: Optional[Tuple[int, int, int, int]] = None
    exact_match: bool = False
    confidence_threshold: float = 0.5
    confidence: float = 0.5  # Alias for compatibility
    excel_column: Optional[str] = None
    click_on_found: bool = True
    click_offset: Tuple[int, int] = (0, 0)
    double_click: bool = False
    
    def validate(self):
        """Validate step configuration"""
        errors = []
        if not self.search_text and not self.excel_column:
            errors.append("Either search_text or excel_column must be specified")
        return errors
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "search_text": self.search_text,
            "region": list(self.region) if self.region else None,
            "exact_match": self.exact_match,
            "confidence_threshold": self.confidence_threshold,
            "excel_column": self.excel_column,
            "click_on_found": self.click_on_found,
            "click_offset": list(self.click_offset),
            "double_click": self.double_click
        })
        return data
    
    def from_dict(self, data):
        # Don't call super().from_dict() as it's not implemented in MacroStep
        self.step_id = data.get("step_id", "")
        self.name = data.get("name", "")
        self.description = data.get("description", "")
        self.enabled = data.get("enabled", True)
        self.error_handling = ErrorHandling(data.get("error_handling", "stop"))
        self.retry_count = data.get("retry_count", 0)
        
        self.search_text = data.get("search_text", "")
        region = data.get("region")
        self.region = tuple(region) if region else None
        self.exact_match = data.get("exact_match", False)
        self.confidence_threshold = data.get("confidence_threshold", 0.5)
        self.confidence = self.confidence_threshold  # Alias
        self.excel_column = data.get("excel_column")
        self.click_on_found = data.get("click_on_found", True)
        offset = data.get("click_offset", [0, 0])
        self.click_offset = tuple(offset)
        self.double_click = data.get("double_click", False)
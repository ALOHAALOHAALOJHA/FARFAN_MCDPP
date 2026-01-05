"""
Calibration Orchestrator - Subject and Evidence Store
======================================================

Module providing CalibrationSubject and EvidenceStore classes
used by the orchestrator for method calibration.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class CalibrationSubject:
    """
    Represents a subject for calibration.
    
    Attributes:
        method_id: Identifier of the method being calibrated
        role: Role identifier for the calibration context
        context: Additional context information for calibration
    """
    method_id: str
    role: str
    context: dict[str, Any]


@dataclass
class EvidenceStore:
    """
    Stores evidence information for calibration.
    
    Attributes:
        pdt_structure: PDT (Policy Document Transform) structure information
        document_quality: Quality metric for the document (0.0 to 1.0)
        question_id: Optional question identifier
        dimension_id: Optional dimension identifier
        policy_area_id: Optional policy area identifier
    """
    pdt_structure: dict[str, Any]
    document_quality: float
    question_id: str | None = None
    dimension_id: str | None = None
    policy_area_id: str | None = None
    
    def __post_init__(self):
        """Validate document_quality is within valid range."""
        if not (0.0 <= self.document_quality <= 1.0):
            raise ValueError(
                f"document_quality must be between 0.0 and 1.0, got {self.document_quality}"
            )

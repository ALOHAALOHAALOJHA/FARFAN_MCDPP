"""
Calibration Types for Orchestration
===================================

Type definitions for calibration subjects, evidence contexts, and results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Set


class LayerId(str, Enum):
    """Epistemic layer identifiers."""
    
    N0_INFRASTRUCTURE = "N0"
    N1_EMPIRICAL = "N1"
    N2_INFERENTIAL = "N2"
    N3_AUDIT = "N3"
    N4_META = "N4"


# Valid roles for calibration subjects
VALID_ROLES = frozenset([
    "extractor",
    "analyzer",
    "integrator",
    "validator",
    "aggregator",
])


# Role-layer requirements mapping
ROLE_LAYER_REQUIREMENTS: Dict[str, Set[LayerId]] = {
    "extractor": {LayerId.N0_INFRASTRUCTURE, LayerId.N1_EMPIRICAL},
    "analyzer": {LayerId.N1_EMPIRICAL, LayerId.N2_INFERENTIAL},
    "integrator": {LayerId.N2_INFERENTIAL, LayerId.N3_AUDIT},
    "validator": {LayerId.N3_AUDIT},
    "aggregator": {LayerId.N3_AUDIT, LayerId.N4_META},
}


@dataclass
class CalibrationSubject:
    """Subject to be calibrated - a method or component."""
    
    name: str
    role: str
    layer: LayerId
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate subject after initialization."""
        if self.role not in VALID_ROLES:
            raise ValueError(f"Invalid role: {self.role}. Must be one of {VALID_ROLES}")
        
        required_layers = ROLE_LAYER_REQUIREMENTS.get(self.role, set())
        if self.layer not in required_layers and required_layers:
            raise ValueError(
                f"Layer {self.layer} not valid for role {self.role}. "
                f"Expected one of: {required_layers}"
            )


@dataclass
class CalibrationEvidenceContext:
    """Context containing evidence for calibration."""
    
    document_id: str
    chunk_references: List[str] = field(default_factory=list)
    gold_annotations: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CalibrationResult:
    """Result of a calibration operation."""
    
    subject: CalibrationSubject
    context: CalibrationEvidenceContext
    metrics: Dict[str, float] = field(default_factory=dict)
    optimized_parameters: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_message: str = ""
    
    @property
    def improvement_score(self) -> float:
        """Calculate overall improvement score."""
        if not self.metrics:
            return 0.0
        return sum(self.metrics.values()) / len(self.metrics)


__all__ = [
    "LayerId",
    "VALID_ROLES",
    "ROLE_LAYER_REQUIREMENTS",
    "CalibrationSubject",
    "CalibrationEvidenceContext", 
    "CalibrationResult",
]

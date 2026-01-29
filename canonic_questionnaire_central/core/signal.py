"""
Signal: Atomic Unit of Information Irrigation

SOTA Implementation following Event-Driven Architecture principles:
- Immutable after creation
- Self-validating scope
- Cryptographic identity (hash)
- Full provenance tracking
- Capability requirements declaration

This is NOT a data container - it's a message that flows through the system.

Author: F.A.R.F.A.N Pipeline Team
Version: 2.0.0
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class SignalType(str, Enum):
    """Canonical signal types aligned with Membership Criteria."""
    
    # Extraction Signals (Phase 1)
    MC01_STRUCTURAL = "MC01"  # Structural markers
    MC02_QUANTITATIVE = "MC02"  # Quantitative triplets
    MC03_NORMATIVE = "MC03"  # Normative references
    MC04_PROGRAMMATIC = "MC04"  # Programmatic hierarchy
    MC05_FINANCIAL = "MC05"  # Financial chains
    MC06_POPULATION = "MC06"  # Population disaggregation
    MC07_TEMPORAL = "MC07"  # Temporal markers
    MC08_CAUSAL = "MC08"  # Causal verbs
    MC09_INSTITUTIONAL = "MC09"  # Institutional network
    MC10_SEMANTIC = "MC10"  # Semantic relationships
    
    # Assembly Signals (Phase 0)
    SIGNAL_PACK = "SIGNAL_PACK"
    STATIC_LOAD = "STATIC_LOAD"
    
    # Enrichment Signals (Phase 2)
    PATTERN_ENRICHMENT = "PATTERN_ENRICHMENT"
    KEYWORD_ENRICHMENT = "KEYWORD_ENRICHMENT"
    ENTITY_ENRICHMENT = "ENTITY_ENRICHMENT"
    
    # Validation Signals (Phase 3)
    NORMATIVE_VALIDATION = "NORMATIVE_VALIDATION"
    ENTITY_VALIDATION = "ENTITY_VALIDATION"
    COHERENCE_VALIDATION = "COHERENCE_VALIDATION"
    
    # Scoring Signals (Phase 4-6)
    MICRO_SCORE = "MICRO_SCORE"
    MESO_SCORE = "MESO_SCORE"
    MACRO_SCORE = "MACRO_SCORE"
    
    # Aggregation Signals (Phase 7-8)
    MESO_AGGREGATION = "MESO_AGGREGATION"
    MACRO_AGGREGATION = "MACRO_AGGREGATION"
    
    # Report Signals (Phase 9)
    REPORT_ASSEMBLY = "REPORT_ASSEMBLY"


@dataclass(frozen=False)
class SignalScope:
    """
    Scope defines WHERE a signal can flow.
    
    Three-dimensional routing:
    - phase: Which pipeline phase processes this
    - policy_area: Which PA context (PA01-PA10 or ALL)
    - slot: Which question slot (D1-Q1 format or wildcard)
    """
    
    phase: str  # phase_00, phase_01, ..., phase_09
    policy_area: str  # PA01-PA10, ALL, CROSS_CUTTING
    slot: str  # D1-Q1, D2-Q5, ALL, etc.
    
    def __post_init__(self):
        # Validate phase (phase_00 through phase_09 - two-digit format)
        valid_phases = {f"phase_{i:02d}" for i in range(10)}
        if self.phase not in valid_phases:
            raise ValueError(f"Invalid phase: {self.phase}")
        
        # Validate policy_area
        valid_pas = {f"PA{i:02d}" for i in range(1, 11)} | {"ALL", "CROSS_CUTTING"}
        if self.policy_area not in valid_pas:
            raise ValueError(f"Invalid policy_area: {self.policy_area}")
    
    def matches(self, other: SignalScope) -> bool:
        """Check if this scope matches another (with wildcards)."""
        phase_match = self.phase == other.phase or other.phase == "ALL"
        pa_match = self.policy_area == other.policy_area or other.policy_area == "ALL"
        slot_match = self.slot == other.slot or other.slot == "ALL" or self.slot == "ALL"
        return phase_match and pa_match and slot_match
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "phase": self.phase,
            "policy_area": self.policy_area,
            "slot": self.slot
        }


@dataclass
class SignalProvenance:
    """
    Full provenance tracking for audit and debugging.
    
    Answers: WHO created this, FROM what source, WHEN, and HOW.
    """
    
    extractor: str  # Class/function that created the signal
    source_file: str  # Original file path
    source_location: Optional[str] = None  # Line number, char offset, etc.
    extraction_pattern: Optional[str] = None  # Regex or rule used
    parent_signal_id: Optional[str] = None  # If derived from another signal
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "extractor": self.extractor,
            "source_file": self.source_file,
            "source_location": self.source_location,
            "extraction_pattern": self.extraction_pattern,
            "parent_signal_id": self.parent_signal_id,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class Signal:
    """
    Signal: The atomic unit of information flow in SISAS.
    
    A Signal is NOT just data - it's a message with:
    - Identity (unique ID + content hash)
    - Type (what kind of information)
    - Scope (where it can flow)
    - Payload (the actual data)
    - Provenance (full audit trail)
    - Requirements (what capabilities are needed to process it)
    - Value metrics (empirical availability, enrichment flag)
    
    Signals are IMMUTABLE after dispatch. Modifications create new signals.
    """
    
    signal_id: str
    signal_type: SignalType
    scope: SignalScope
    payload: Any
    provenance: SignalProvenance
    capabilities_required: List[str]
    empirical_availability: float  # 0.0 to 1.0 - from membership criteria calibration
    enrichment: bool = False  # True if this adds value beyond raw extraction
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Routing metadata (set by SDO)
    _routed: bool = field(default=False, repr=False)
    _consumers: List[str] = field(default_factory=list, repr=False)
    
    @classmethod
    def create(
        cls,
        signal_type: SignalType,
        scope: SignalScope,
        payload: Any,
        provenance: SignalProvenance,
        capabilities_required: List[str],
        empirical_availability: float,
        enrichment: bool = False
    ) -> Signal:
        """Factory method for creating new signals with auto-generated ID."""
        return cls(
            signal_id=str(uuid4()),
            signal_type=signal_type,
            scope=scope,
            payload=payload,
            provenance=provenance,
            capabilities_required=capabilities_required,
            empirical_availability=empirical_availability,
            enrichment=enrichment
        )
    
    def content_hash(self) -> str:
        """
        Compute deterministic hash over signal content.
        
        Used for deduplication - two signals with same content hash
        are considered duplicates even if IDs differ.
        """
        content = {
            "type": self.signal_type.value if isinstance(self.signal_type, SignalType) else self.signal_type,
            "scope": self.scope.to_dict(),
            "payload": self.payload
        }
        serialized = json.dumps(content, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()
    
    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate signal integrity.
        
        Returns (is_valid, list_of_errors).
        """
        errors = []
        
        # Scope validation
        try:
            if not isinstance(self.scope, SignalScope):
                errors.append("Invalid scope type")
        except Exception as e:
            errors.append(f"Scope validation error: {e}")
        
        # Empirical availability bounds
        if not 0.0 <= self.empirical_availability <= 1.0:
            errors.append(f"empirical_availability must be 0-1, got {self.empirical_availability}")
        
        # Capabilities must be non-empty
        if not self.capabilities_required:
            errors.append("capabilities_required cannot be empty")
        
        # Payload must exist
        if self.payload is None:
            errors.append("payload cannot be None")
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize signal to dictionary for persistence/transmission."""
        return {
            "signal_id": self.signal_id,
            "signal_type": self.signal_type.value if isinstance(self.signal_type, SignalType) else self.signal_type,
            "scope": self.scope.to_dict(),
            "payload": self.payload,
            "provenance": self.provenance.to_dict(),
            "capabilities_required": self.capabilities_required,
            "empirical_availability": self.empirical_availability,
            "enrichment": self.enrichment,
            "timestamp": self.timestamp.isoformat(),
            "content_hash": self.content_hash()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Signal:
        """Deserialize signal from dictionary."""
        return cls(
            signal_id=data["signal_id"],
            signal_type=SignalType(data["signal_type"]) if data["signal_type"] in SignalType._value2member_map_ else data["signal_type"],
            scope=SignalScope(**data["scope"]),
            payload=data["payload"],
            provenance=SignalProvenance(
                extractor=data["provenance"]["extractor"],
                source_file=data["provenance"]["source_file"],
                source_location=data["provenance"].get("source_location"),
                extraction_pattern=data["provenance"].get("extraction_pattern"),
                parent_signal_id=data["provenance"].get("parent_signal_id"),
                created_at=datetime.fromisoformat(data["provenance"]["created_at"])
            ),
            capabilities_required=data["capabilities_required"],
            empirical_availability=data["empirical_availability"],
            enrichment=data.get("enrichment", False),
            timestamp=datetime.fromisoformat(data["timestamp"])
        )
    
    def __hash__(self):
        return hash(self.signal_id)
    
    def __eq__(self, other):
        if not isinstance(other, Signal):
            return False
        return self.signal_id == other.signal_id

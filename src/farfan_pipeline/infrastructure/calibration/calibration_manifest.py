"""
Calibration Manifest
====================
Complete record of all calibration decisions for audit trail. 

DESIGN PATTERNS:
- Memento Pattern: Captures calibration state for restoration/audit
- Immutable Value Object: Cannot be modified after creation

INVARIANTS:
- INV-MAN-001: All calibration choices must have rationale
- INV-MAN-002: All choices must reference source evidence
- INV-MAN-003: Manifest hash must be deterministic
"""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final

from .calibration_core import CalibrationLayer, CalibrationPhase
from .unit_of_analysis import UnitOfAnalysis

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CalibrationDecision:
    """Single calibration decision with full audit trail."""
    decision_id: str
    parameter_name: str
    chosen_value: float
    alternative_values: tuple[float, ...]
    rationale: str
    source_evidence: str
    decision_timestamp: datetime
    
    def __post_init__(self) -> None:
        if not self.rationale:
            raise ValueError("Rationale cannot be empty")
        if not self.source_evidence:
            raise ValueError("Source evidence cannot be empty")


@dataclass(frozen=True)
class DriftIndicator:
    """Indicator of calibration drift."""
    parameter:  str
    expected_value: float
    actual_value: float
    deviation: float
    severity: str  # "WARNING" or "FATAL"
    detection_timestamp: datetime


@dataclass
class DriftReport:
    """Report of detected calibration drift."""
    indicators: list[DriftIndicator] = field(default_factory=list)
    drift_detected:  bool = False
    report_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class CalibrationManifest:
    """
    Complete record of calibration choices for a contract.
    
    IMMUTABLE after creation.  Any modification requires new manifest.
    """
    # Identity
    manifest_id: str
    contract_id: str
    unit_of_analysis_id: str
    contract_type_code: str
    
    # Calibration layers (frozen)
    ingestion_layer: CalibrationLayer
    phase2_layer: CalibrationLayer
    
    # Decision audit trail
    decisions: tuple[CalibrationDecision, ...]
    
    # Metadata
    created_at: datetime
    schema_version: Final[str] = "1.0.0"
    
    def compute_hash(self) -> str:
        """Compute deterministic hash of manifest."""
        components = [
            self.manifest_id,
            self.contract_id,
            self.unit_of_analysis_id,
            self.contract_type_code,
            self.ingestion_layer.manifest_hash(),
            self.phase2_layer.manifest_hash(),
            str(len(self.decisions)),
        ]
        return hashlib.sha256("|".join(components).encode()).hexdigest()
    
    def to_json(self) -> str:
        """Serialize manifest to JSON for storage."""
        return json.dumps(self._to_dict(), indent=2, default=str)
    
    def _to_dict(self) -> dict[str, object]:
        """Convert to dictionary."""
        return {
            "manifest_id": self.manifest_id,
            "contract_id":  self.contract_id,
            "unit_of_analysis_id": self.unit_of_analysis_id,
            "contract_type_code": self.contract_type_code,
            "ingestion_layer_hash": self.ingestion_layer.manifest_hash(),
            "phase2_layer_hash": self.phase2_layer.manifest_hash(),
            "decision_count": len(self.decisions),
            "created_at": self.created_at.isoformat(),
            "manifest_hash": self.compute_hash(),
        }
    
    def save(self, output_dir: Path) -> Path:
        """Save manifest to file."""
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"calibration_manifest_{self.manifest_id}.json"
        output_path = output_dir / filename
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(self.to_json())
        
        logger.info(f"Saved calibration manifest to {output_path}")
        return output_path


class ManifestBuilder:
    """
    Builder for CalibrationManifest. 
    
    DESIGN PATTERN: Builder Pattern
    - Incremental construction with validation
    - Produces immutable manifest
    """
    
    def __init__(self, contract_id: str, unit_of_analysis:  UnitOfAnalysis) -> None:
        self._contract_id = contract_id
        self._unit_of_analysis = unit_of_analysis
        self._contract_type_code:  str | None = None
        self._ingestion_layer: CalibrationLayer | None = None
        self._phase2_layer: CalibrationLayer | None = None
        self._decisions: list[CalibrationDecision] = []
    
    def with_contract_type(self, contract_type_code:  str) -> ManifestBuilder: 
        """Set contract type."""
        self._contract_type_code = contract_type_code
        return self
    
    def with_ingestion_layer(self, layer: CalibrationLayer) -> ManifestBuilder:
        """Set ingestion calibration layer."""
        if layer.phase != CalibrationPhase.INGESTION:
            raise ValueError(f"Expected INGESTION layer, got {layer.phase}")
        self._ingestion_layer = layer
        return self
    
    def with_phase2_layer(self, layer: CalibrationLayer) -> ManifestBuilder: 
        """Set Phase-2 calibration layer."""
        if layer.phase != CalibrationPhase.PHASE_2_COMPUTATION:
            raise ValueError(f"Expected PHASE_2_COMPUTATION layer, got {layer.phase}")
        self._phase2_layer = layer
        return self
    
    def add_decision(self, decision: CalibrationDecision) -> ManifestBuilder:
        """Add calibration decision to audit trail."""
        self._decisions.append(decision)
        return self
    
    def build(self) -> CalibrationManifest:
        """
        Build immutable manifest.
        
        Raises:
            ValueError: If required fields are missing
        """
        if self._contract_type_code is None:
            raise ValueError("Contract type code is required")
        if self._ingestion_layer is None:
            raise ValueError("Ingestion layer is required")
        if self._phase2_layer is None:
            raise ValueError("Phase-2 layer is required")
        
        manifest_id = hashlib.sha256(
            f"{self._contract_id}_{datetime.now(timezone.utc).isoformat()}".encode()
        ).hexdigest()[:16]
        
        return CalibrationManifest(
            manifest_id=manifest_id,
            contract_id=self._contract_id,
            unit_of_analysis_id=self._unit_of_analysis.content_hash(),
            contract_type_code=self._contract_type_code,
            ingestion_layer=self._ingestion_layer,
            phase2_layer=self._phase2_layer,
            decisions=tuple(self._decisions),
            created_at=datetime.now(timezone.utc),
        )

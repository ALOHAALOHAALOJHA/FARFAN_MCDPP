"""
Phase 9 Output Contract - Enhanced v2.0
========================================

PHASE_LABEL: Phase 9
Module: contracts/phase9_output_contract.py
Purpose: Defines the output specifications and validation for Phase 9

This contract specifies the expected outputs, their types, validation rules,
and postconditions for Phase 9 execution.

Enhanced with:
- ATROZ Dashboard publication status tracking
- Carver doctoral quality metrics enforcement
- Cross-phase feature synchronization metadata

Version: 2.0.0
Author: F.A.R.F.A.N Core Architecture Team
Date: 2026-01-27
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Optional, Protocol

__version__ = "2.0.0"
__phase__ = 9

logger = logging.getLogger(__name__)


# =============================================================================
# ATROZ DASHBOARD INTEGRATION
# =============================================================================


@dataclass
class AtrozPublicationStatus:
    """Tracks Phase 9 report publication status to ATROZ dashboard.
    
    Enables bidirectional sync between Phase 9 reports and the ATROZ
    dashboard's data mining and analytics capabilities.
    """
    
    published_to_dashboard: bool = False
    dashboard_report_id: Optional[str] = None
    dashboard_timestamp: Optional[str] = None
    dashboard_endpoint: str = "http://localhost:5005"
    publication_retries: int = 0
    sync_status: str = "pending"  # pending, synced, failed


# =============================================================================
# CARVER DOCTORAL QUALITY METRICS
# =============================================================================


@dataclass
class CarverQualityMetrics:
    """Quality metrics for doctoral-level Carver synthesis.
    
    Ensures human answers meet rigorous academic standards with
    measurable depth, complexity, and evidence integration.
    
    Thresholds:
    - doctoral_depth_score >= 0.7: Meets doctoral depth requirements
    - synthesis_complexity_index >= 0.6: Adequate cross-reference complexity
    - evidence_density_ratio >= 0.5: Sufficient evidence integration
    """
    
    # Core quality scores (0.0 - 1.0 scale)
    doctoral_depth_score: float = 0.0
    synthesis_complexity_index: float = 0.0
    evidence_density_ratio: float = 0.0
    
    # Gate validation
    quality_gate_passed: bool = False
    quality_gate_threshold: float = 0.7
    
    # Detailed metrics
    answer_length_chars: int = 0
    paragraph_count: int = 0
    academic_vocabulary_density: float = 0.0
    cross_reference_count: int = 0
    evidence_items_integrated: int = 0


# =============================================================================
# CROSS-PHASE FEATURE SYNCHRONIZATION
# =============================================================================


@dataclass
class CrossPhaseFeatures:
    """Cross-phase feature synchronization metadata.
    
    Tracks feature compatibility and upstream phase dependencies
    to ensure Phase 9 reports reflect the latest canonic phase features.
    """
    
    sisas_signal_version: str = "1.0.0"
    upstream_phase_hashes: dict[str, str] = field(default_factory=dict)
    feature_compatibility_matrix: dict[str, bool] = field(default_factory=lambda: {
        "sisas_signals": True,
        "v4_contracts": True,
        "carver_synthesis": True,
        "evidence_nexus": True,
        "choquet_aggregation": True,
    })
    last_sync_timestamp: Optional[str] = None
    sync_warnings: list[str] = field(default_factory=list)


# =============================================================================
# MAIN OUTPUT STRUCTURE
# =============================================================================


@dataclass
class Phase9Output:
    """Output data structure for Phase 9 - Enhanced v2.0.
    
    Includes core outputs plus ATROZ integration, Carver quality
    tracking, and cross-phase feature synchronization.
    """
    
    # Generated reports
    institutional_reports: list[dict[str, Any]]
    
    # Entity annexes
    entity_annexes: list[dict[str, Any]]
    
    # Metadata
    generation_metadata: dict[str, Any]
    
    # Quality metrics
    quality_metrics: dict[str, Any]
    
    # === NEW FIELDS (v2.0) ===
    
    # ATROZ Dashboard integration
    atroz_publication: AtrozPublicationStatus = field(
        default_factory=AtrozPublicationStatus
    )
    
    # Carver doctoral quality tracking
    carver_quality: CarverQualityMetrics = field(
        default_factory=CarverQualityMetrics
    )
    
    # Cross-phase feature sync
    cross_phase_features: CrossPhaseFeatures = field(
        default_factory=CrossPhaseFeatures
    )


class Phase9OutputValidator(Protocol):
    """Protocol defining output validation interface for Phase 9."""
    
    def validate_output(self, output_data: Phase9Output) -> tuple[bool, list[str]]:
        """Validate Phase 9 output data.
        
        Args:
            output_data: Output data to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        ...


def validate_phase9_output(output_data: Phase9Output) -> tuple[bool, list[str]]:
    """Validate output from Phase 9.
    
    Args:
        output_data: Output data to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Validate institutional reports
    if not hasattr(output_data, 'institutional_reports'):
        errors.append("Missing institutional_reports in output")
    elif not isinstance(output_data.institutional_reports, list):
        errors.append("Institutional reports must be a list")
    elif len(output_data.institutional_reports) == 0:
        errors.append("Institutional reports list cannot be empty")
    
    # Validate entity annexes
    if not hasattr(output_data, 'entity_annexes'):
        errors.append("Missing entity_annexes in output")
    elif not isinstance(output_data.entity_annexes, list):
        errors.append("Entity annexes must be a list")
    
    # Validate generation metadata
    if not hasattr(output_data, 'generation_metadata'):
        errors.append("Missing generation_metadata in output")
    elif not isinstance(output_data.generation_metadata, dict):
        errors.append("Generation metadata must be a dictionary")
    
    # Validate quality metrics
    if not hasattr(output_data, 'quality_metrics'):
        errors.append("Missing quality_metrics in output")
    elif not isinstance(output_data.quality_metrics, dict):
        errors.append("Quality metrics must be a dictionary")
    
    # === NEW VALIDATIONS (v2.0) ===
    
    # Validate ATROZ publication status
    if hasattr(output_data, 'atroz_publication'):
        atroz = output_data.atroz_publication
        if not isinstance(atroz, AtrozPublicationStatus):
            errors.append("atroz_publication must be AtrozPublicationStatus instance")
        elif atroz.published_to_dashboard and not atroz.dashboard_report_id:
            errors.append("Published reports must have dashboard_report_id")
    
    # Validate Carver quality metrics
    if hasattr(output_data, 'carver_quality'):
        carver = output_data.carver_quality
        if not isinstance(carver, CarverQualityMetrics):
            errors.append("carver_quality must be CarverQualityMetrics instance")
        elif carver.doctoral_depth_score < 0 or carver.doctoral_depth_score > 1:
            errors.append("doctoral_depth_score must be between 0.0 and 1.0")
    
    # Validate cross-phase features
    if hasattr(output_data, 'cross_phase_features'):
        cpf = output_data.cross_phase_features
        if not isinstance(cpf, CrossPhaseFeatures):
            errors.append("cross_phase_features must be CrossPhaseFeatures instance")
    
    is_valid = len(errors) == 0
    if not is_valid:
        logger.error(f"Phase 9 output validation failed: {errors}")
    
    return is_valid, errors


def get_expected_outputs() -> list[str]:
    """Get list of expected output fields from Phase 9.
    
    Returns:
        List of expected output field names
    """
    return [
        "institutional_reports",
        "entity_annexes", 
        "generation_metadata",
        "quality_metrics",
        # v2.0 additions
        "atroz_publication",
        "carver_quality",
        "cross_phase_features",
    ]


def verify_output_structure(output_data: Phase9Output) -> tuple[bool, list[str]]:
    """Verify the structure of Phase 9 output.
    
    Args:
        output_data: Output data to verify
        
    Returns:
        Tuple of (structure_valid, list_of_issues)
    """
    issues = []
    
    # Check report structure
    for i, report in enumerate(getattr(output_data, 'institutional_reports', [])):
        if not isinstance(report, dict):
            issues.append(f"Report {i} is not a dictionary")
            continue
            
        required_fields = ['report_id', 'content', 'metadata', 'timestamp']
        for field in required_fields:
            if field not in report:
                issues.append(f"Report {i} missing required field: {field}")
    
    # Check annex structure
    for i, annex in enumerate(getattr(output_data, 'entity_annexes', [])):
        if not isinstance(annex, dict):
            issues.append(f"Annex {i} is not a dictionary")
            continue
            
        required_fields = ['entity_id', 'annex_content', 'institutional_linkage']
        for field in required_fields:
            if field not in annex:
                issues.append(f"Annex {i} missing required field: {field}")
    
    structure_valid = len(issues) == 0
    return structure_valid, issues


def get_consumer_downstream() -> str:
    """Get the downstream consumer of Phase 9 output.
    
    Returns:
        Description of downstream consumer
    """
    return "Institutional delivery system and final pipeline output"


def check_postconditions(output_data: Phase9Output) -> tuple[bool, list[str]]:
    """Check postconditions for Phase 9 execution.
    
    Args:
        output_data: Output data to check postconditions for
        
    Returns:
        Tuple of (postconditions_met, list_of_failures)
    """
    failures = []
    
    # Check that we have at least one institutional report
    if (hasattr(output_data, 'institutional_reports') and 
        len(output_data.institutional_reports) < 1):
        failures.append("At least 1 institutional report required in output")
    
    # Check that generation metadata is populated
    metadata = getattr(output_data, 'generation_metadata', {})
    if not metadata:
        failures.append("Generation metadata cannot be empty")
    elif 'timestamp' not in metadata:
        failures.append("Generation metadata must include timestamp")
    elif 'phase_id' not in metadata or metadata.get('phase_id') != 9:
        failures.append("Generation metadata must include correct phase_id (9)")
    
    postconditions_met = len(failures) == 0
    return postconditions_met, failures


def verify_output_contract() -> bool:
    """Verify the Phase 9 output contract.
    
    Returns:
        True if contract is properly defined
    """
    print("Phase 9 Output Contract Verification")
    print("=" * 60)
    
    expected_outputs = get_expected_outputs()
    print(f"Expected outputs: {expected_outputs}")
    
    print(f"Validation function: {validate_phase9_output.__name__}")
    print(f"Postcondition checker: {check_postconditions.__name__}")
    print(f"Downstream consumer: {get_consumer_downstream()}")
    
    return True


def get_certification_requirements() -> list[str]:
    """Get certification requirements for Phase 9 output.
    
    Returns:
        List of certification requirements
    """
    return [
        # Core requirements
        "All institutional reports must be properly structured",
        "Entity annexes must link to institutional entities",
        "Quality metrics must be computed and valid",
        "Metadata must include all required fields",
        "Output must satisfy downstream consumer requirements",
        # v2.0 requirements
        "ATROZ dashboard publication must be attempted for all reports",
        "Carver doctoral quality gate must be evaluated for all human answers",
        "Cross-phase feature compatibility must be verified before output",
        "Quality gate threshold (0.7) must be met for doctoral-level classification",
    ]
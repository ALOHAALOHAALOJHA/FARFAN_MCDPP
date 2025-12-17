"""
Phase Contract Quality - CQVR Integration

This phase validates contract quality using the CQVR (Contract Quality 
Validation and Remediation) rubric. It operates on executor contracts to ensure
they meet production standards before deployment.

Phase Position: Post-Pipeline Validation (Phase 11)
Input: Executor contracts from Phase 2
Output: Quality assessment reports and decisions
"""

from .cqvr_phase import ContractQualityPhase, ContractQualityResult
from .cqvr_evaluator_core import (
    CQVREvaluator,
    CQVRScore,
    CQVRDecision,
    CQVRDecisionEngine,
    verify_identity_schema_coherence,
    verify_method_assembly_alignment,
    verify_signal_requirements,
    verify_output_schema,
    verify_pattern_coverage,
    verify_method_specificity,
    verify_validation_rules,
    verify_documentation_quality,
    verify_human_template,
    verify_metadata_completeness,
)

__all__ = [
    "ContractQualityPhase",
    "ContractQualityResult",
    "CQVREvaluator",
    "CQVRScore",
    "CQVRDecision",
    "CQVRDecisionEngine",
    "verify_identity_schema_coherence",
    "verify_method_assembly_alignment",
    "verify_signal_requirements",
    "verify_output_schema",
    "verify_pattern_coverage",
    "verify_method_specificity",
    "verify_validation_rules",
    "verify_documentation_quality",
    "verify_human_template",
    "verify_metadata_completeness",
]

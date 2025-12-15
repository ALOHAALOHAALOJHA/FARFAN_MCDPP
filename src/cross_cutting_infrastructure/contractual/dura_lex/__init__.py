# Core contracts __init__.py
"""Core contracts package for runtime contract infrastructure."""

from .runtime_contracts import SegmentationMethod, SegmentationInfo, FallbackCategory

from .audit_trail import (
    VerificationManifest,
    CalibrationScore,
    ParametrizationConfig,
    DeterminismSeeds,
    ResultsBundle,
    OperationTrace,
    generate_manifest,
    verify_manifest,
    reconstruct_score,
    validate_determinism,
    StructuredAuditLogger,
    TraceGenerator,
    create_trace_example,
)

__all__ = [
    "SegmentationMethod",
    "SegmentationInfo", 
    "FallbackCategory",
    "VerificationManifest",
    "CalibrationScore",
    "ParametrizationConfig",
    "DeterminismSeeds",
    "ResultsBundle",
    "OperationTrace",
    "generate_manifest",
    "verify_manifest",
    "reconstruct_score",
    "validate_determinism",
    "StructuredAuditLogger",
    "TraceGenerator",
    "create_trace_example",
]

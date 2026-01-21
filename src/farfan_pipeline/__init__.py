"""
F.A.R.F.A.N Multi-Criteria Decision-Making Public Policy Framework
====================================================================

A comprehensive pipeline for deterministic policy analysis using causal inference,
Bayesian networks, and natural language processing.

Version: 1.0.0
Author: F.A.R.F.A.N Development Team
License: Proprietary

Package Structure:
------------------
- farfan_pipeline.orchestration: Pipeline orchestration and coordination
- farfan_pipeline.phases: Analysis phases (Phase_00 through Phase_09)
- farfan_pipeline.methods: Epistemological methods (N1/N2/N3 levels)
- farfan_pipeline.calibration: Bayesian calibration and validation
- farfan_pipeline.core: Core types and canonical notation
- farfan_pipeline.infrastructure: Infrastructure services
- farfan_pipeline.api: FastAPI endpoints
- farfan_pipeline.utils: Utility functions

Quick Start:
------------
    from farfan_pipeline.orchestration import UnifiedOrchestrator
    from farfan_pipeline.calibration import CalibrationResult

    orchestrator = UnifiedOrchestrator()
    result = orchestrator.run(policy_document, config)

Environment Variables:
----------------------
- FARFAN_ROOT: Root directory of the FARFAN_MCDPP project
- FARFAN_DATA_PATH: Path to data directory
- FARFAN_CACHE_DIR: Path to cache directory
- FARFAN_LOG_LEVEL: Logging level (default: INFO)

Python Path Configuration:
--------------------------
This package uses src layout. The following should be in your PYTHONPATH:
    - <project_root>/src (for farfan_pipeline imports)
    - <project_root> (for canonic_questionnaire_central imports)

Development:
------------
    pip install -e ".[dev]"

Testing:
--------
    pytest tests/

Documentation:
--------------
    See README.md for full documentation
    See docs/ for detailed API documentation
"""

__version__ = "1.0.0"
__author__ = "F.A.R.F.A.N Development Team"
__license__ = "Proprietary"

# Public API exports
from farfan_pipeline.core.types import (
    UnitOfAnalysis,
    FiscalContext,
    PolicyDocument,
    AnalysisResult,
)

# Core orchestration
from farfan_pipeline.orchestration import (
    UnifiedOrchestrator,
    OrchestratorConfig,
    PhaseID,
    PhaseStatus,
    ExecutionContext,
    PipelineResult,
)

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",
    # Core types
    "UnitOfAnalysis",
    "FiscalContext",
    "PolicyDocument",
    "AnalysisResult",
    # Orchestration
    "UnifiedOrchestrator",
    "OrchestratorConfig",
    "PhaseID",
    "PhaseStatus",
    "ExecutionContext",
    "PipelineResult",
]

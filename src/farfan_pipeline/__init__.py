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
# Note: Only importing what actually exists to avoid import errors

# Core analytical types from core.types
try:
    from farfan_pipeline.core.types import (
        DimensionAnalitica,
        MechanismPart,
        CausalMechanism,
        EvidenceStrength,
        ScoreBand,
        CategoriaCausal,
    )
    _analytical_types_available = True
except ImportError:
    _analytical_types_available = False

# Core types from data_models
try:
    from farfan_pipeline.data_models.unit_of_analysis import (
        UnitOfAnalysis,
        FiscalContext,
        PolicyDocument,
        AnalysisResult,
    )
    _types_available = True
except ImportError:
    _types_available = False

# Core orchestration
try:
    from farfan_pipeline.orchestration import (
        UnifiedOrchestrator,
        OrchestratorConfig,
        PhaseID,
        PhaseStatus,
        ExecutionContext,
        PipelineResult,
    )
    _orchestration_available = True
except ImportError:
    _orchestration_available = False

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",
]

# Add analytical types exports if available
if _analytical_types_available:
    __all__.extend([
        "DimensionAnalitica",
        "MechanismPart",
        "CausalMechanism",
        "EvidenceStrength",
        "ScoreBand",
        "CategoriaCausal",
    ])

# Add types exports if available
if _types_available:
    __all__.extend([
        "UnitOfAnalysis",
        "FiscalContext",
        "PolicyDocument",
        "AnalysisResult",
    ])

# Add orchestration exports if available
if _orchestration_available:
    __all__.extend([
        "UnifiedOrchestrator",
        "OrchestratorConfig",
        "PhaseID",
        "PhaseStatus",
        "ExecutionContext",
        "PipelineResult",
    ])

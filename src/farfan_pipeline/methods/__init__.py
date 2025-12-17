"""
Methods Dispensary - Critical Methodological Infrastructure

This package contains production-grade implementations of methodological frameworks
required for rigorous policy analysis:

- Derek Beach's Process Tracing and Evidential Tests (Beach & Pedersen 2019)
- Theory of Change DAG Validation (Goertz & Mahoney 2012)
- Financial Viability Analysis
- Policy Processing and Analysis

These are REQUIRED components, not optional. The pipeline cannot function without them.
"""

__version__ = "2.0.0"
__author__ = "F.A.R.F.A.N Development Team"

# Expose key classes for easier imports
try:
    from .derek_beach import (
        BeachEvidentialTest,
        CausalExtractor,
        MechanismPartExtractor,
        DerekBeachProducer,
    )
    DEREK_BEACH_AVAILABLE = True
except ImportError as e:
    import warnings
    warnings.warn(
        f"CRITICAL: Derek Beach methods unavailable: {e}. "
        f"This is REQUIRED infrastructure. Install all dependencies.",
        ImportWarning
    )
    BeachEvidentialTest = None
    CausalExtractor = None
    MechanismPartExtractor = None
    DerekBeachProducer = None
    DEREK_BEACH_AVAILABLE = False

try:
    from .teoria_cambio import (
        TeoriaCambio,
        ValidacionResultado,
        AdvancedDAGValidator,
    )
    TEORIA_CAMBIO_AVAILABLE = True
except ImportError as e:
    import warnings
    warnings.warn(
        f"CRITICAL: Theory of Change methods unavailable: {e}. "
        f"This is REQUIRED infrastructure. Install all dependencies.",
        ImportWarning
    )
    TeoriaCambio = None
    ValidacionResultado = None
    AdvancedDAGValidator = None
    TEORIA_CAMBIO_AVAILABLE = False

__all__ = [
    # Derek Beach
    'BeachEvidentialTest',
    'CausalExtractor',
    'MechanismPartExtractor',
    'DerekBeachProducer',
    'DEREK_BEACH_AVAILABLE',
    # Theory of Change
    'TeoriaCambio',
    'ValidacionResultado',
    'AdvancedDAGValidator',
    'TEORIA_CAMBIO_AVAILABLE',
]

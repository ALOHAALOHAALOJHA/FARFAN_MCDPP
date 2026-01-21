"""
F.A.R.F.A.N Methods Dispensary
===============================

Epistemological methods organized by epistemic level (N1/N2/N3) and
policy area. This module contains 237+ methods for policy analysis.

Method Categories:
------------------
- N1-EMP: Empirical methods (observation-based)
- N2-INF: Inferential methods (Bayesian, causal)
- N3-CTR: Constructive methods (theory-building)

Key Modules:
------------
- analyzer_one: Text mining and semantic analysis
- derek_beach: Causal inference methods
- bayesian_multilevel_system: Bayesian hierarchical models
- policy_processor: Policy document processing
- contradiction_deteccion: Contradiction detection

Usage:
------
    from farfan_pipeline.methods import (
        TextMiningEngine,
        DerekBeachAnalyzer,
        BayesianMultilevelSystem,
    )
"""

# Core analyzer classes
from farfan_pipeline.methods.analyzer_one import (
    TextMiningEngine,
    MunicipalAnalyzer,
    SemanticAnalyzer,
)

# Causal inference
from farfan_pipeline.methods.derek_beach import (
    DerekBeachAnalyzer,
    CausalMechanismAnalyzer,
)

# Bayesian methods
from farfan_pipeline.methods.bayesian_multilevel_system import (
    BayesianMultilevelSystem,
    HierarchicalModel,
)

# Policy processing
from farfan_pipeline.methods.policy_processor import (
    PolicyProcessor,
    PolicyDocument,
)

__all__ = [
    # Analyzers
    "TextMiningEngine",
    "MunicipalAnalyzer",
    "SemanticAnalyzer",
    # Causal
    "DerekBeachAnalyzer",
    "CausalMechanismAnalyzer",
    # Bayesian
    "BayesianMultilevelSystem",
    "HierarchicalModel",
    # Policy
    "PolicyProcessor",
    "PolicyDocument",
]

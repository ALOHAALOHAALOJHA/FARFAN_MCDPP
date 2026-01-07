"""
Bayesian Inference Engine
=========================

Refactored Bayesian components for the Derek Beach process tracing pipeline.

This module provides a unified interface for Bayesian inference operations:
- Adaptive prior construction (AGUJA I)
- MCMC sampling with diagnostics (AGUJA II)
- Model validation and convergence checks

Phase 2 SOTA Enhancement - 2026-01-07

Architecture:
    BayesianEngineAdapter: Main interface for all Bayesian operations
    ├── BayesianPriorBuilder: Constructs adaptive priors based on evidence type
    ├── BayesianSamplingEngine: Executes MCMC sampling with PyMC
    └── BayesianDiagnostics: Validates models and checks convergence

Theoretical Foundation:
    - Gelman et al. (2013): Bayesian Data Analysis (3rd ed.)
    - Beach & Pedersen (2024): Bayesian Process Tracing
    - Goertz & Mahoney (2012): Axiomatic-Bayesian fusion
"""

from __future__ import annotations

from .bayesian_adapter import BayesianEngineAdapter
from .bayesian_diagnostics import BayesianDiagnostics
from .bayesian_prior_builder import BayesianPriorBuilder
from .bayesian_sampling_engine import BayesianSamplingEngine

__all__ = [
    "BayesianEngineAdapter",
    "BayesianPriorBuilder",
    "BayesianSamplingEngine",
    "BayesianDiagnostics",
]

__version__ = "1.0.0"

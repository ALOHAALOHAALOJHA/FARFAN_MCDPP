"""Wiring System - Fine-Grained Module Connection and Contract Validation.

This package implements the complete wiring architecture for SAAAAAA,
providing deterministic initialization, contract validation, and observability
for all module connections.

Architecture:
- Ports and adapters (hexagonal architecture)
- Dependency injection via constructors
- Feature flags for conditional wiring
- Contract validation between all links
- OpenTelemetry observability
- Deterministic initialization order

Key Modules:
- errors: Typed error classes for wiring failures
- contracts: Pydantic models for link contracts
- feature_flags: Typed feature flags
- bootstrap: Deterministic initialization engine
- validation: Contract validation between links
- observability: Tracing and metrics
- analysis_factory: Factory for analysis module dependency injection
"""

from farfan_pipeline.core.wiring.analysis_factory import (
    create_analysis_components,
    create_bayesian_confidence_calculator,
    create_contradiction_detector,
    create_document_loader,
    create_municipal_analyzer,
    create_municipal_ontology,
    create_performance_analyzer,
    create_semantic_analyzer,
    create_temporal_logic_verifier,
)

__all__ = [
    'create_analysis_components',
    'create_bayesian_confidence_calculator',
    'create_contradiction_detector',
    'create_document_loader',
    'create_municipal_analyzer',
    'create_municipal_ontology',
    'create_performance_analyzer',
    'create_semantic_analyzer',
    'create_temporal_logic_verifier',
]

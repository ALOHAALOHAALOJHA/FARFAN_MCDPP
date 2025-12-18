"""Phase 0 test fixtures and configuration."""

import pytest


@pytest.fixture
def mock_runtime_config():
    """Mock runtime configuration for testing."""
    class MockRuntimeConfig:
        mode = "prod"
        allow_contradiction_fallback = False
        allow_validator_disable = False
        allow_execution_estimates = False
        allow_dev_ingestion_fallbacks = False
        allow_aggregation_defaults = False
        allow_networkx_fallback = False
        allow_spacy_fallback = False
    
    return MockRuntimeConfig()


@pytest.fixture
def mock_phase0_runner():
    """Mock Phase 0 runner for testing."""
    class MockRunner:
        errors = []
        _bootstrap_failed = False
        runtime_config = None
        seed_snapshot = {"random": 42, "numpy": 42, "torch": 42}
        input_pdf_sha256 = "a" * 64
        questionnaire_sha256 = "b" * 64
        method_executor = object()
        questionnaire = {"questions": []}
    
    return MockRunner()

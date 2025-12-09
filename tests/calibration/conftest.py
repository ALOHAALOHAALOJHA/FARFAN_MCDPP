"""
Shared pytest fixtures for calibration tests.

Provides sample data, configurations, and helper functions for testing
the F.A.R.F.A.N calibration system.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture(scope="session")
def calibration_system_root() -> Path:
    """Return path to calibration system root directory."""
    return (
        Path(__file__).parent.parent.parent
        / "src"
        / "cross_cutting_infrastrucuture"
        / "capaz_calibration_parmetrization"
    )


@pytest.fixture(scope="session")
def cohort_loader(calibration_system_root: Path):
    """Load CohortLoader for accessing calibration configurations."""
    import sys

    sys.path.insert(0, str(calibration_system_root.parent.parent))
    from cross_cutting_infrastrucuture.capaz_calibration_parmetrization.cohort_loader import (
        CohortLoader,
    )

    return CohortLoader(cohort_dir=calibration_system_root)


@pytest.fixture(scope="session")
def intrinsic_calibration_config(cohort_loader) -> dict[str, Any]:
    """Load intrinsic calibration configuration."""
    return cohort_loader.load_calibration("intrinsic_calibration")


@pytest.fixture(scope="session")
def method_compatibility_config(cohort_loader) -> dict[str, Any]:
    """Load method compatibility configuration."""
    return cohort_loader.load_calibration("method_compatibility")


@pytest.fixture(scope="session")
def fusion_weights_config(cohort_loader) -> dict[str, Any]:
    """Load fusion weights configuration."""
    return cohort_loader.load_calibration("fusion_weights")


@pytest.fixture
def sample_method_basic() -> dict[str, Any]:
    """Sample basic method metadata for testing."""
    return {
        "method_id": "test.method.basic_analyzer",
        "role": "analyzer",
        "dimension": "D1",
        "question": "Q1",
        "version": "1.0.0",
    }


@pytest.fixture
def sample_method_score_q() -> dict[str, Any]:
    """Sample SCORE_Q method metadata."""
    return {
        "method_id": "test.method.score_q_analyzer",
        "role": "score",
        "dimension": "D1",
        "question": "Q1",
        "version": "1.0.0",
    }


@pytest.fixture
def sample_base_layer_scores() -> dict[str, float]:
    """Sample base layer (@b) component scores."""
    return {
        "b_theory": 0.9,
        "b_impl": 0.85,
        "b_deploy": 0.75,
    }


@pytest.fixture
def sample_pdt_data() -> dict[str, Any]:
    """Sample PDT (Plan de Desarrollo Territorial) data."""
    return {
        "structural_compliance": 0.8,
        "mandatory_sections_ratio": 0.9,
        "indicator_quality_score": 0.85,
        "ppi_completeness": 0.7,
    }


@pytest.fixture
def sample_layer_scores_full() -> dict[str, float]:
    """Sample scores for all calibration layers."""
    return {
        "@b": 0.85,
        "@chain": 1.0,
        "@q": 1.0,
        "@d": 0.9,
        "@p": 0.8,
        "@C": 1.0,
        "@u": 0.75,
        "@m": 0.95,
    }


@pytest.fixture
def sample_choquet_weights() -> dict[str, Any]:
    """Sample Choquet weights with linear and interaction terms."""
    return {
        "linear": {
            "@b": 0.17,
            "@chain": 0.13,
            "@q": 0.08,
            "@d": 0.07,
            "@p": 0.06,
            "@C": 0.08,
            "@u": 0.04,
            "@m": 0.04,
        },
        "interaction": {
            ("@u", "@chain"): 0.13,
            ("@chain", "@C"): 0.10,
            ("@q", "@d"): 0.10,
        },
    }


@pytest.fixture
def sample_governance_artifacts() -> dict[str, Any]:
    """Sample governance artifacts for @m layer."""
    return {
        "formula_export_valid": True,
        "trace_complete": True,
        "logs_conform_schema": True,
        "version_tagged": True,
        "config_hash_matches": True,
        "signature_valid": True,
        "runtime_ms": 450,
        "memory_mb": 128,
    }


@pytest.fixture
def sample_contract_validation() -> dict[str, Any]:
    """Sample contract validation results for @chain layer."""
    return {
        "schema_compatible": True,
        "required_inputs_available": True,
        "optional_inputs_missing": [],
        "hard_mismatch": False,
        "soft_violation": False,
        "warnings": [],
    }


@pytest.fixture
def sample_ensemble_config() -> dict[str, Any]:
    """Sample ensemble configuration for @C layer."""
    return {
        "interplay_id": "Q001_ensemble",
        "methods": ["pattern_extractor_v2", "coherence_validator"],
        "fusion_rule": "TYPE_A",
        "scale_compatible": True,
        "semantic_overlap": 1.0,
        "concepts": ["coherence", "textual_quality"],
    }


@pytest.fixture
def test_output_dir(tmp_path: Path) -> Path:
    """Temporary directory for test outputs."""
    output_dir = tmp_path / "test_outputs"
    output_dir.mkdir(exist_ok=True)
    return output_dir


@pytest.fixture
def sample_calibration_certificate() -> dict[str, Any]:
    """Sample calibration certificate structure."""
    return {
        "certificate_id": "cert_test_001",
        "method_id": "test.method.analyzer",
        "calibration_score": 0.8618,
        "timestamp": "2024-12-15T00:00:00Z",
        "layer_scores": {
            "@b": 0.85,
            "@chain": 1.0,
            "@q": 1.0,
            "@d": 0.9,
            "@p": 0.8,
            "@C": 1.0,
            "@u": 0.75,
            "@m": 0.95,
        },
        "fusion_computation": {
            "linear_contribution": 0.6198,
            "interaction_contribution": 0.242,
        },
        "signature": "SHA256:abc123...",
    }


@pytest.fixture(scope="session")
def test_fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "test_fixtures"


@pytest.fixture(scope="session")
def sample_methods_data(test_fixtures_dir: Path) -> dict[str, Any]:
    """Load sample methods data from fixture file."""
    fixture_file = test_fixtures_dir / "sample_methods.json"
    if fixture_file.exists():
        with open(fixture_file) as f:
            return json.load(f)
    return {"sample_methods": []}


@pytest.fixture(scope="session")
def sample_pdt_data_collection(test_fixtures_dir: Path) -> dict[str, Any]:
    """Load sample PDT data from fixture file."""
    fixture_file = test_fixtures_dir / "sample_pdt_data.json"
    if fixture_file.exists():
        with open(fixture_file) as f:
            return json.load(f)
    return {"pdt_samples": []}


@pytest.fixture(scope="session")
def sample_ensemble_configs_collection(test_fixtures_dir: Path) -> dict[str, Any]:
    """Load sample ensemble configs from fixture file."""
    fixture_file = test_fixtures_dir / "sample_ensemble_configs.json"
    if fixture_file.exists():
        with open(fixture_file) as f:
            return json.load(f)
    return {"ensemble_configs": []}


@pytest.fixture(scope="session")
def sample_governance_artifacts_collection(test_fixtures_dir: Path) -> dict[str, Any]:
    """Load sample governance artifacts from fixture file."""
    fixture_file = test_fixtures_dir / "sample_governance_artifacts.json"
    if fixture_file.exists():
        with open(fixture_file) as f:
            return json.load(f)
    return {"governance_artifacts": []}

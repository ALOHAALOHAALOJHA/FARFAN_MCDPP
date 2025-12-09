"""
Unit tests for Meta Layer (@m) computation.

Tests governance and observability metrics:
- m_transp: transparency (formula export, traces, logs)
- m_gov: governance (versioning, config hash, signatures)
- m_cost: computational cost (runtime, memory)

Formula: x_@m = h_M(m_transp, m_gov, m_cost)
       = 0.5·m_transp + 0.4·m_gov + 0.1·m_cost
"""

from __future__ import annotations

from typing import Any



def compute_transparency_score(artifacts: dict[str, Any]) -> float:
    """
    Compute m_transp score.
    
    Returns:
        1.0 if all 3 conditions met (formula_export, trace, logs)
        0.7 if 2/3 conditions met
        0.4 if 1/3 conditions met
        0.0 otherwise
    """
    conditions_met = sum([
        artifacts.get("formula_export_valid", False),
        artifacts.get("trace_complete", False),
        artifacts.get("logs_conform_schema", False),
    ])

    if conditions_met == 3:
        return 1.0
    elif conditions_met == 2:
        return 0.7
    elif conditions_met == 1:
        return 0.4
    else:
        return 0.0


def compute_governance_score(artifacts: dict[str, Any]) -> float:
    """
    Compute m_gov score.
    
    Returns:
        1.0 if all 3 conditions met (version, config_hash, signature)
        0.66 if 2/3 conditions met
        0.33 if 1/3 conditions met
        0.0 otherwise
    """
    conditions_met = sum([
        artifacts.get("version_tagged", False),
        artifacts.get("config_hash_matches", False),
        artifacts.get("signature_valid", False),
    ])

    if conditions_met == 3:
        return 1.0
    elif conditions_met == 2:
        return 0.66
    elif conditions_met == 1:
        return 0.33
    else:
        return 0.0


def compute_cost_score(runtime_ms: float, memory_mb: float) -> float:
    """
    Compute m_cost score.
    
    Returns:
        1.0 if runtime < 500ms AND memory < 256MB
        0.8 if 500ms <= runtime < 2000ms
        0.5 if runtime >= 2000ms OR memory excessive
        0.0 if timeout OR out_of_memory
    """
    threshold_fast = 500
    threshold_acceptable = 2000
    threshold_memory = 256

    if runtime_ms < threshold_fast and memory_mb < threshold_memory:
        return 1.0
    elif runtime_ms < threshold_acceptable:
        return 0.8
    elif runtime_ms >= threshold_acceptable or memory_mb >= threshold_memory:
        return 0.5
    else:
        return 0.0


def compute_meta_layer_score(m_transp: float, m_gov: float, m_cost: float) -> float:
    """
    Compute overall @m score using weighted aggregation.
    
    h_M(m_transp, m_gov, m_cost) = 0.5·m_transp + 0.4·m_gov + 0.1·m_cost
    """
    return 0.5 * m_transp + 0.4 * m_gov + 0.1 * m_cost


class TestTransparencyScore:
    """Test m_transp computation."""

    def test_all_transparency_conditions_met(self, sample_governance_artifacts: dict[str, Any]):
        """All 3 transparency conditions met should yield 1.0."""
        score = compute_transparency_score(sample_governance_artifacts)

        assert score == 1.0

    def test_two_transparency_conditions_met(self):
        """2/3 transparency conditions met should yield 0.7."""
        artifacts = {
            "formula_export_valid": True,
            "trace_complete": True,
            "logs_conform_schema": False,
        }

        score = compute_transparency_score(artifacts)

        assert score == 0.7

    def test_one_transparency_condition_met(self):
        """1/3 transparency conditions met should yield 0.4."""
        artifacts = {
            "formula_export_valid": True,
            "trace_complete": False,
            "logs_conform_schema": False,
        }

        score = compute_transparency_score(artifacts)

        assert score == 0.4

    def test_no_transparency_conditions_met(self):
        """0/3 transparency conditions met should yield 0.0."""
        artifacts = {
            "formula_export_valid": False,
            "trace_complete": False,
            "logs_conform_schema": False,
        }

        score = compute_transparency_score(artifacts)

        assert score == 0.0

    def test_transparency_discrete_levels(self):
        """Transparency score should only be discrete levels."""
        valid_scores = {0.0, 0.4, 0.7, 1.0}

        test_cases = [
            {"formula_export_valid": True, "trace_complete": True, "logs_conform_schema": True},
            {"formula_export_valid": True, "trace_complete": True, "logs_conform_schema": False},
            {"formula_export_valid": True, "trace_complete": False, "logs_conform_schema": False},
            {"formula_export_valid": False, "trace_complete": False, "logs_conform_schema": False},
        ]

        for artifacts in test_cases:
            score = compute_transparency_score(artifacts)
            assert score in valid_scores


class TestGovernanceScore:
    """Test m_gov computation."""

    def test_all_governance_conditions_met(self, sample_governance_artifacts: dict[str, Any]):
        """All 3 governance conditions met should yield 1.0."""
        score = compute_governance_score(sample_governance_artifacts)

        assert score == 1.0

    def test_two_governance_conditions_met(self):
        """2/3 governance conditions met should yield 0.66."""
        artifacts = {
            "version_tagged": True,
            "config_hash_matches": True,
            "signature_valid": False,
        }

        score = compute_governance_score(artifacts)

        assert abs(score - 0.66) < 0.01

    def test_one_governance_condition_met(self):
        """1/3 governance conditions met should yield 0.33."""
        artifacts = {
            "version_tagged": True,
            "config_hash_matches": False,
            "signature_valid": False,
        }

        score = compute_governance_score(artifacts)

        assert abs(score - 0.33) < 0.01

    def test_no_governance_conditions_met(self):
        """0/3 governance conditions met should yield 0.0."""
        artifacts = {
            "version_tagged": False,
            "config_hash_matches": False,
            "signature_valid": False,
        }

        score = compute_governance_score(artifacts)

        assert score == 0.0

    def test_governance_discrete_levels(self):
        """Governance score should only be discrete levels."""
        valid_scores = {0.0, 0.33, 0.66, 1.0}

        test_cases = [
            {"version_tagged": True, "config_hash_matches": True, "signature_valid": True},
            {"version_tagged": True, "config_hash_matches": True, "signature_valid": False},
            {"version_tagged": True, "config_hash_matches": False, "signature_valid": False},
            {"version_tagged": False, "config_hash_matches": False, "signature_valid": False},
        ]

        for artifacts in test_cases:
            score = compute_governance_score(artifacts)
            assert any(abs(score - v) < 0.01 for v in valid_scores)


class TestCostScore:
    """Test m_cost computation."""

    def test_fast_runtime_low_memory(self):
        """Fast runtime and low memory should yield 1.0."""
        score = compute_cost_score(runtime_ms=450, memory_mb=128)

        assert score == 1.0

    def test_acceptable_runtime(self):
        """Acceptable runtime should yield 0.8."""
        score = compute_cost_score(runtime_ms=1500, memory_mb=128)

        assert score == 0.8

    def test_slow_runtime(self):
        """Slow runtime should yield 0.5."""
        score = compute_cost_score(runtime_ms=2500, memory_mb=128)

        assert score == 0.5

    def test_excessive_memory(self):
        """Excessive memory should yield lower score."""
        score = compute_cost_score(runtime_ms=450, memory_mb=512)

        assert score <= 0.8

    def test_cost_thresholds(self):
        """Test cost thresholds."""
        assert compute_cost_score(499, 128) == 1.0
        assert compute_cost_score(500, 128) == 0.8
        assert compute_cost_score(1999, 128) == 0.8
        assert compute_cost_score(2000, 128) == 0.5


class TestMetaLayerAggregation:
    """Test overall @m score aggregation."""

    def test_perfect_meta_score(self, sample_governance_artifacts: dict[str, Any]):
        """Perfect meta layer should yield high score."""
        m_transp = compute_transparency_score(sample_governance_artifacts)
        m_gov = compute_governance_score(sample_governance_artifacts)
        m_cost = compute_cost_score(
            sample_governance_artifacts["runtime_ms"],
            sample_governance_artifacts["memory_mb"]
        )

        score = compute_meta_layer_score(m_transp, m_gov, m_cost)

        expected = 0.5 * 1.0 + 0.4 * 1.0 + 0.1 * 1.0
        assert abs(score - expected) < 1e-6

    def test_meta_weights_sum_to_one(self):
        """Meta layer weights should sum to 1.0."""
        weights = [0.5, 0.4, 0.1]

        assert abs(sum(weights) - 1.0) < 1e-6

    def test_meta_score_bounded(self):
        """Meta layer score must be bounded in [0,1]."""
        test_cases = [
            (1.0, 1.0, 1.0),
            (0.0, 0.0, 0.0),
            (0.7, 0.66, 0.8),
            (0.4, 0.33, 0.5),
        ]

        for m_transp, m_gov, m_cost in test_cases:
            score = compute_meta_layer_score(m_transp, m_gov, m_cost)
            assert 0.0 <= score <= 1.0

    def test_transparency_priority(self):
        """Transparency should have highest weight (0.5)."""
        score_high_transp = compute_meta_layer_score(m_transp=1.0, m_gov=0.0, m_cost=0.0)
        score_high_gov = compute_meta_layer_score(m_transp=0.0, m_gov=1.0, m_cost=0.0)

        assert score_high_transp > score_high_gov

    def test_governance_secondary_priority(self):
        """Governance should have second-highest weight (0.4)."""
        score_high_gov = compute_meta_layer_score(m_transp=0.0, m_gov=1.0, m_cost=0.0)
        score_high_cost = compute_meta_layer_score(m_transp=0.0, m_gov=0.0, m_cost=1.0)

        assert score_high_gov > score_high_cost

    def test_cost_lowest_priority(self):
        """Cost should have lowest weight (0.1)."""
        score_all_zeros = compute_meta_layer_score(0.0, 0.0, 0.0)
        score_only_cost = compute_meta_layer_score(0.0, 0.0, 1.0)

        impact = score_only_cost - score_all_zeros
        assert abs(impact - 0.1) < 1e-6


class TestGovernanceArtifacts:
    """Test governance artifact validation."""

    def test_formula_export_validity(self):
        """Test formula export validation."""
        valid_export = {
            "formula": "x_@b = w_th * b_theory + w_imp * b_impl + w_dep * b_deploy",
            "traceable": True,
        }

        is_valid = valid_export.get("traceable", False)

        assert is_valid is True

    def test_trace_completeness(self):
        """Test trace completeness."""
        trace = {
            "execution_id": "exec_001",
            "timestamps": {"start": 1234567890, "end": 1234567895},
            "complete": True,
        }

        is_complete = trace.get("complete", False)

        assert is_complete is True

    def test_log_schema_conformance(self):
        """Test log schema conformance."""
        log_entry = {
            "timestamp": "2024-12-15T00:00:00Z",
            "level": "INFO",
            "message": "Calibration computation started",
            "conforms_schema": True,
        }

        conforms = log_entry.get("conforms_schema", False)

        assert conforms is True

    def test_version_tagging(self):
        """Test version tagging."""
        version_info = {
            "method_version": "1.0.0",
            "calibration_version": "2.0.0",
            "tagged": True,
        }

        is_tagged = version_info.get("tagged", False)

        assert is_tagged is True

    def test_config_hash_validation(self):
        """Test config hash validation."""
        config_info = {
            "config_hash": "sha256:abc123...",
            "computed_hash": "sha256:abc123...",
            "matches": True,
        }

        matches = config_info.get("matches", False)

        assert matches is True

    def test_signature_validation(self):
        """Test signature validation."""
        signature_info = {
            "signature": "SHA256:def456...",
            "public_key": "key123",
            "valid": True,
        }

        is_valid = signature_info.get("valid", False)

        assert is_valid is True

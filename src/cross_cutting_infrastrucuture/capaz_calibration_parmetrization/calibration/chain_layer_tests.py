"""
COHORT_2024 - Chain Layer Tests

Comprehensive test suite for ChainLayerEvaluator with discrete scoring logic.

Test Coverage:
- Discrete scoring (0.0, 0.3, 0.6, 0.8, 1.0)
- Missing required inputs (0.0)
- Schema violations (0.0 hard, 0.6/0.8 soft)
- Missing critical optional (0.3)
- Missing optional with ratio>0.5 (0.6)
- Warnings only (0.8)
- Perfect chain (1.0)
- Chain sequence validation
- Weakest link computation

Run with: pytest chain_layer_tests.py -v
"""
from __future__ import annotations

import pytest

from .COHORT_2024_chain_layer import ChainLayerEvaluator


@pytest.fixture
def sample_signatures() -> dict[str, dict[str, any]]:
    """Sample method signatures for testing."""
    return {
        "method_a": {
            "required_inputs": ["document", "config"],
            "optional_inputs": ["metadata", "cache", "debug_mode"],
            "critical_optional": ["metadata"],
            "input_types": {
                "document": "str",
                "config": "dict",
                "metadata": "dict",
            },
            "output_type": "dict",
        },
        "method_b": {
            "required_inputs": ["data"],
            "optional_inputs": ["threshold", "mode"],
            "critical_optional": [],
            "input_types": {"data": "list", "threshold": "float"},
            "output_type": "list",
        },
        "method_c": {
            "required_inputs": ["input"],
            "optional_inputs": [],
            "critical_optional": [],
            "input_types": {"input": "Any"},
            "output_type": "str",
        },
        "method_d": {
            "required_inputs": ["x", "y"],
            "optional_inputs": ["opt1", "opt2", "opt3", "opt4"],
            "critical_optional": [],
            "input_types": {"x": "int", "y": "int"},
            "output_type": "int",
        },
    }


@pytest.fixture
def evaluator(sample_signatures: dict) -> ChainLayerEvaluator:
    """Create evaluator with sample signatures."""
    return ChainLayerEvaluator(sample_signatures)


class TestDiscreteScoring:
    """Test discrete scoring logic."""

    def test_score_1_0_perfect(self, evaluator: ChainLayerEvaluator) -> None:
        """Test score 1.0: all inputs present, no warnings."""
        result = evaluator.evaluate(
            "method_a",
            provided_inputs={"document", "config", "metadata", "cache", "debug_mode"},
        )
        assert result["score"] == 1.0
        assert result["reason"] == "all inputs present AND no warnings"
        assert len(result["missing_required"]) == 0
        assert len(result["missing_critical"]) == 0
        assert len(result["warnings"]) == 0

    def test_score_0_8_warnings_only(self, evaluator: ChainLayerEvaluator) -> None:
        """Test score 0.8: all contracts pass but warnings exist."""
        result = evaluator.evaluate(
            "method_d",
            provided_inputs={"x", "y", "opt1", "opt2", "opt3", "opt4"},
            upstream_outputs={"x": "float", "y": "int"},
        )
        assert result["score"] == 0.8
        assert "warnings exist" in result["reason"]
        assert len(result["missing_required"]) == 0
        assert len(result["missing_critical"]) == 0
        assert len(result["warnings"]) > 0

    def test_score_0_6_many_optional_missing(
        self, evaluator: ChainLayerEvaluator
    ) -> None:
        """Test score 0.6: many optional missing (ratio > 0.5)."""
        result = evaluator.evaluate(
            "method_d",
            provided_inputs={"x", "y", "opt1"},
        )
        assert result["score"] == 0.6
        assert "many_missing" in result["reason"]
        assert len(result["missing_optional"]) > 2

    def test_score_0_3_critical_missing(self, evaluator: ChainLayerEvaluator) -> None:
        """Test score 0.3: critical optional missing."""
        result = evaluator.evaluate(
            "method_a",
            provided_inputs={"document", "config"},
        )
        assert result["score"] == 0.3
        assert "missing_critical" in result["reason"]
        assert "metadata" in result["missing_critical"]
        assert len(result["missing_required"]) == 0

    def test_score_0_0_missing_required(self, evaluator: ChainLayerEvaluator) -> None:
        """Test score 0.0: missing required input."""
        result = evaluator.evaluate(
            "method_a",
            provided_inputs={"document"},
        )
        assert result["score"] == 0.0
        assert "missing_required" in result["reason"]
        assert "config" in result["missing_required"]

    def test_score_0_0_hard_schema_violation(
        self, evaluator: ChainLayerEvaluator
    ) -> None:
        """Test score 0.0: hard schema violation."""
        result = evaluator.evaluate(
            "method_b",
            provided_inputs={"data", "threshold"},
            upstream_outputs={"data": "str", "threshold": "float"},
        )
        assert result["score"] == 0.0
        assert len(result["schema_violations"]) > 0
        assert "data" in result["schema_violations"][0]

    def test_score_0_0_no_signature(self, evaluator: ChainLayerEvaluator) -> None:
        """Test score 0.0: method signature not found."""
        result = evaluator.evaluate(
            "unknown_method",
            provided_inputs={"anything"},
        )
        assert result["score"] == 0.0
        assert "no signature found" in result["reason"]
        assert len(result["warnings"]) > 0


class TestSchemaCompatibility:
    """Test schema type checking."""

    def test_exact_type_match(self, evaluator: ChainLayerEvaluator) -> None:
        """Test exact type match (no warning)."""
        result = evaluator.evaluate(
            "method_a",
            provided_inputs={"document", "config", "metadata", "cache", "debug_mode"},
            upstream_outputs={"document": "str", "config": "dict", "metadata": "dict"},
        )
        assert result["score"] >= 0.8

    def test_soft_type_mismatch_int_float(
        self, evaluator: ChainLayerEvaluator
    ) -> None:
        """Test soft type mismatch (int vs float)."""
        result = evaluator.evaluate(
            "method_d",
            provided_inputs={"x", "y"},
            upstream_outputs={"x": "float", "y": "int"},
        )
        assert result["score"] >= 0.6
        assert any("Soft type mismatch" in w for w in result["warnings"])

    def test_hard_type_mismatch(self, evaluator: ChainLayerEvaluator) -> None:
        """Test hard type mismatch (incompatible types)."""
        result = evaluator.evaluate(
            "method_b",
            provided_inputs={"data"},
            upstream_outputs={"data": "dict"},
        )
        assert result["score"] == 0.0
        assert len(result["schema_violations"]) > 0

    def test_any_type_always_compatible(self, evaluator: ChainLayerEvaluator) -> None:
        """Test Any type accepts anything."""
        result = evaluator.evaluate(
            "method_c",
            provided_inputs={"input"},
            upstream_outputs={"input": "whatever"},
        )
        assert result["score"] == 1.0
        assert len(result["warnings"]) == 0


class TestChainSequence:
    """Test chain sequence validation."""

    def test_simple_chain(self, evaluator: ChainLayerEvaluator) -> None:
        """Test simple 2-method chain."""
        result = evaluator.validate_chain_sequence(
            method_sequence=["method_c", "method_b"],
            initial_inputs={"input"},
            method_outputs={"method_c": {"data"}, "method_b": {"result"}},
        )
        assert "method_c" in result["method_scores"]
        assert "method_b" in result["method_scores"]
        assert result["chain_quality"] >= 0.0

    def test_weakest_link(self, evaluator: ChainLayerEvaluator) -> None:
        """Test weakest link identification."""
        result = evaluator.validate_chain_sequence(
            method_sequence=["method_a", "method_b", "method_c"],
            initial_inputs={"document", "config"},
            method_outputs={
                "method_a": {"data"},
                "method_b": {"input"},
                "method_c": {"output"},
            },
        )

        assert result["weakest_link"] is not None
        weakest_score = result["method_scores"][result["weakest_link"]]
        assert weakest_score == result["chain_quality"]
        assert all(score >= weakest_score for score in result["method_scores"].values())

    def test_chain_propagation(self, evaluator: ChainLayerEvaluator) -> None:
        """Test that outputs propagate through chain."""
        result = evaluator.validate_chain_sequence(
            method_sequence=["method_c", "method_a", "method_b"],
            initial_inputs={"input", "metadata", "config"},
            method_outputs={
                "method_c": {"document"},
                "method_a": {"data"},
                "method_b": {"result"},
            },
        )

        assert result["method_scores"]["method_c"] == 1.0
        assert result["method_scores"]["method_a"] >= 0.3

    def test_broken_chain(self, evaluator: ChainLayerEvaluator) -> None:
        """Test chain with missing inputs."""
        result = evaluator.validate_chain_sequence(
            method_sequence=["method_a", "method_b", "method_c"],
            initial_inputs=set(),
            method_outputs={},
        )

        assert result["chain_quality"] == 0.0
        assert all(score == 0.0 for score in result["method_scores"].values())


class TestChainQuality:
    """Test chain quality computation."""

    def test_compute_chain_quality_min(self, evaluator: ChainLayerEvaluator) -> None:
        """Test that chain quality is minimum score."""
        scores = {"method_a": 1.0, "method_b": 0.3, "method_c": 0.8}
        quality = evaluator.compute_chain_quality(scores)
        assert quality == 0.3

    def test_compute_chain_quality_empty(self, evaluator: ChainLayerEvaluator) -> None:
        """Test empty chain returns 0.0."""
        quality = evaluator.compute_chain_quality({})
        assert quality == 0.0

    def test_compute_chain_quality_perfect(
        self, evaluator: ChainLayerEvaluator
    ) -> None:
        """Test perfect chain returns 1.0."""
        scores = {"method_a": 1.0, "method_b": 1.0, "method_c": 1.0}
        quality = evaluator.compute_chain_quality(scores)
        assert quality == 1.0


class TestEdgeCases:
    """Test edge cases."""

    def test_empty_optional_inputs(self) -> None:
        """Test method with no optional inputs."""
        evaluator = ChainLayerEvaluator(
            {
                "method_x": {
                    "required_inputs": ["input"],
                    "optional_inputs": [],
                    "critical_optional": [],
                    "output_type": "str",
                }
            }
        )
        result = evaluator.evaluate("method_x", {"input"})
        assert result["score"] == 1.0

    def test_all_optional_are_critical(self) -> None:
        """Test method where all optional are critical."""
        evaluator = ChainLayerEvaluator(
            {
                "method_y": {
                    "required_inputs": ["input"],
                    "optional_inputs": ["opt1", "opt2"],
                    "critical_optional": ["opt1", "opt2"],
                    "output_type": "str",
                }
            }
        )
        result = evaluator.evaluate("method_y", {"input"})
        assert result["score"] == 0.3
        assert len(result["missing_critical"]) == 2

    def test_no_inputs_required(self) -> None:
        """Test method with no required inputs."""
        evaluator = ChainLayerEvaluator(
            {
                "method_z": {
                    "required_inputs": [],
                    "optional_inputs": ["opt"],
                    "critical_optional": [],
                    "output_type": "str",
                }
            }
        )
        result = evaluator.evaluate("method_z", set())
        assert result["score"] >= 0.6

    def test_provided_inputs_superset(self, evaluator: ChainLayerEvaluator) -> None:
        """Test when provided inputs are superset of required."""
        result = evaluator.evaluate(
            "method_a",
            provided_inputs={
                "document",
                "config",
                "metadata",
                "cache",
                "debug_mode",
                "extra1",
                "extra2",
            },
        )
        assert result["score"] >= 0.8


class TestIntegration:
    """Integration tests with realistic scenarios."""

    def test_realistic_analysis_chain(self) -> None:
        """Test realistic multi-stage analysis chain."""
        signatures = {
            "ingest_pdf": {
                "required_inputs": ["file_path"],
                "optional_inputs": ["encoding", "page_range"],
                "critical_optional": [],
                "output_type": "dict",
            },
            "extract_text": {
                "required_inputs": ["document"],
                "optional_inputs": ["clean_whitespace"],
                "critical_optional": [],
                "output_type": "str",
            },
            "analyze_sentiment": {
                "required_inputs": ["text"],
                "optional_inputs": ["model", "confidence_threshold"],
                "critical_optional": ["model"],
                "output_type": "dict",
            },
            "generate_report": {
                "required_inputs": ["analysis"],
                "optional_inputs": ["format", "template"],
                "critical_optional": [],
                "output_type": "str",
            },
        }

        evaluator = ChainLayerEvaluator(signatures)

        result = evaluator.validate_chain_sequence(
            method_sequence=[
                "ingest_pdf",
                "extract_text",
                "analyze_sentiment",
                "generate_report",
            ],
            initial_inputs={"file_path", "encoding", "page_range", "model", "clean_whitespace", "format", "template", "confidence_threshold"},
            method_outputs={
                "ingest_pdf": {"document"},
                "extract_text": {"text"},
                "analyze_sentiment": {"analysis"},
                "generate_report": {"report"},
            },
        )

        assert result["chain_quality"] >= 0.8
        assert all(score >= 0.8 for score in result["method_scores"].values())

    def test_failed_analysis_chain(self) -> None:
        """Test chain that should fail due to missing inputs."""
        signatures = {
            "step1": {
                "required_inputs": ["input"],
                "optional_inputs": [],
                "critical_optional": [],
                "output_type": "dict",
            },
            "step2": {
                "required_inputs": ["data", "config"],
                "optional_inputs": [],
                "critical_optional": [],
                "output_type": "dict",
            },
        }

        evaluator = ChainLayerEvaluator(signatures)

        result = evaluator.validate_chain_sequence(
            method_sequence=["step1", "step2"],
            initial_inputs={"input"},
            method_outputs={"step1": {"data"}},
        )

        assert result["chain_quality"] == 0.0
        assert result["method_scores"]["step2"] == 0.0
        assert result["weakest_link"] == "step2"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

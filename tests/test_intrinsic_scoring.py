"""
Test intrinsic scoring formulas implementation.

Verifies exact formulas from intrinsic_calibration_rubric.json v2.0.0:
- b_theory = 0.4*statistical_validity + 0.3*logical_consistency + 0.3*appropriate_assumptions
- b_impl = 0.35*test_coverage + 0.25*type_annotations + 0.25*error_handling + 0.15*documentation
- b_deploy = 0.4*validation_runs + 0.35*stability_coefficient + 0.25*failure_rate
"""

from pathlib import Path

import pytest

from src.farfan_pipeline.core.calibration.intrinsic_scoring import (
    compute_appropriate_assumptions,
    compute_b_deploy,
    compute_b_impl,
    compute_b_theory,
    compute_documentation_score,
    compute_logical_consistency,
    compute_statistical_validity,
    compute_type_annotations_score,
)


@pytest.fixture
def rubric():
    """Load rubric for testing"""
    import json

    rubric_path = Path("system/config/calibration/intrinsic_calibration_rubric.json")
    with open(rubric_path) as f:
        return json.load(f)


@pytest.fixture
def repo_root():
    """Repository root path"""
    return Path(".")


class TestStatisticalValidity:
    """Test statistical validity scoring"""

    def test_strong_statistical_two_keywords(self):
        """Test >=2 keywords → 1.0"""
        method_info = {
            "method_name": "compute_bayesian_regression",
            "docstring": "Uses bayesian probability with regression analysis",
        }
        score, evidence = compute_statistical_validity(method_info)
        assert score == 1.0
        assert evidence["rule_applied"] == "strong_statistical"
        assert len(evidence["keywords_matched"]) >= 2

    def test_moderate_statistical_one_keyword(self):
        """Test ==1 keyword → 0.6"""
        method_info = {
            "method_name": "analyze_data",
            "docstring": "Uses probability distribution",
        }
        score, evidence = compute_statistical_validity(method_info)
        assert score == 0.6
        assert evidence["rule_applied"] == "moderate_statistical"
        assert len(evidence["keywords_matched"]) == 1

    def test_weak_statistical_no_keywords(self):
        """Test ==0 keywords → 0.2"""
        method_info = {
            "method_name": "process_text",
            "docstring": "Processes text data",
        }
        score, evidence = compute_statistical_validity(method_info)
        assert score == 0.2
        assert evidence["rule_applied"] == "weak_statistical"
        assert len(evidence["keywords_matched"]) == 0


class TestLogicalConsistency:
    """Test logical consistency scoring"""

    def test_complete_documentation(self):
        """Test complete docs → 1.0"""
        method_info = {
            "docstring": ("A" * 101)
            + "\n\nArgs:\n  param1: description\nReturns:\n  result"
        }
        score, evidence = compute_logical_consistency(method_info)
        assert score == 1.0
        assert evidence["rule_applied"] == "complete"

    def test_good_documentation(self):
        """Test good docs → 0.7"""
        method_info = {"docstring": ("A" * 51) + "\n\nArgs:\n  param1: description"}
        score, evidence = compute_logical_consistency(method_info)
        assert score == 0.7
        assert evidence["rule_applied"] == "good"

    def test_basic_documentation(self):
        """Test basic docs → 0.4"""
        method_info = {"docstring": "Short description here"}
        score, evidence = compute_logical_consistency(method_info)
        assert score == 0.4
        assert evidence["rule_applied"] == "basic"

    def test_minimal_documentation(self):
        """Test minimal docs → 0.1"""
        method_info = {"docstring": "Short"}
        score, evidence = compute_logical_consistency(method_info)
        assert score == 0.1
        assert evidence["rule_applied"] == "minimal"


class TestAppropriateAssumptions:
    """Test appropriate assumptions scoring"""

    def test_explicit_assumptions(self):
        """Test >=1 assumption keyword → 0.8"""
        method_info = {
            "docstring": "This assumes input is validated. Precondition: x > 0"
        }
        score, evidence = compute_appropriate_assumptions(method_info)
        assert score == 0.8
        assert evidence["rule_applied"] == "explicit_assumptions"
        assert len(evidence["keywords_matched"]) >= 1

    def test_implicit_assumptions(self):
        """Test ==0 assumption keywords → 0.3"""
        method_info = {"docstring": "Processes data and returns result"}
        score, evidence = compute_appropriate_assumptions(method_info)
        assert score == 0.3
        assert evidence["rule_applied"] == "implicit_assumptions"
        assert len(evidence["keywords_matched"]) == 0


class TestBTheoryFormula:
    """Test b_theory formula: 0.4*stat + 0.3*logic + 0.3*assumptions"""

    def test_exact_formula(self, rubric):
        """Test exact weighted formula"""
        method_info = {
            "method_name": "compute_bayesian_model",
            "docstring": ("Computes bayesian probability model with regression. " * 3)
            + "\n\nArgs:\n  data: input\nReturns:\n  model\nAssumes: normalized input",
        }

        b_theory, evidence = compute_b_theory(method_info, rubric)

        # Verify formula components
        stat = evidence["components"]["statistical_validity"]["score"]
        logic = evidence["components"]["logical_consistency"]["score"]
        assumptions = evidence["components"]["appropriate_assumptions"]["score"]

        expected = 0.4 * stat + 0.3 * logic + 0.3 * assumptions
        assert abs(b_theory - expected) < 0.001

        # Verify weights
        assert evidence["weights"]["statistical_validity"] == 0.4
        assert evidence["weights"]["logical_consistency"] == 0.3
        assert evidence["weights"]["appropriate_assumptions"] == 0.3


class TestTypeAnnotationsScore:
    """Test type annotations formula: (typed/total)*0.7 + (0.3 if return else 0)"""

    def test_full_annotations(self):
        """Test fully typed → 1.0"""
        method_info = {
            "input_parameters": [
                {"name": "x", "type_hint": "int"},
                {"name": "y", "type_hint": "str"},
            ],
            "return_type": "bool",
        }
        score, evidence = compute_type_annotations_score(method_info)
        assert score == 1.0
        assert evidence["typed_params"] == 2
        assert evidence["total_params"] == 2
        assert evidence["has_return_type"] is True

    def test_partial_annotations(self):
        """Test partial typing"""
        method_info = {
            "input_parameters": [
                {"name": "x", "type_hint": "int"},
                {"name": "y", "type_hint": None},
            ],
            "return_type": "bool",
        }
        score, evidence = compute_type_annotations_score(method_info)
        expected = (1 / 2) * 0.7 + 0.3
        assert abs(score - expected) < 0.001

    def test_no_annotations(self):
        """Test no typing → 0.0"""
        method_info = {
            "input_parameters": [{"name": "x"}, {"name": "y"}],
            "return_type": None,
        }
        score, evidence = compute_type_annotations_score(method_info)
        assert score == 0.0


class TestDocumentationScore:
    """Test documentation formula: (0.4 if len>50 else 0.1) + (0.3 if params) + (0.2 if returns) + (0.1 if examples)"""

    def test_complete_documentation(self):
        """Test complete docs → 1.0"""
        method_info = {
            "docstring": ("A" * 51)
            + "\n\nArgs:\n  x: param\nReturns:\n  result\nExample:\n  usage"
        }
        score, evidence = compute_documentation_score(method_info)
        assert score == 1.0

    def test_minimal_documentation(self):
        """Test minimal docs → 0.1"""
        method_info = {"docstring": "Short"}
        score, evidence = compute_documentation_score(method_info)
        assert score == 0.1


class TestBImplFormula:
    """Test b_impl formula: 0.35*test + 0.25*type + 0.25*error + 0.15*doc"""

    def test_exact_formula(self, rubric, repo_root):
        """Test exact weighted formula"""
        method_info = {
            "method_name": "compute_score",
            "docstring": ("Computes score. " * 10)
            + "\n\nArgs:\n  x: input\nReturns:\n  score",
            "input_parameters": [{"name": "x", "type_hint": "int"}],
            "return_type": "float",
            "file_path": "nonexistent.py",
            "line_number": 1,
        }

        b_impl, evidence = compute_b_impl(method_info, repo_root, rubric)

        # Verify weights
        assert evidence["weights"]["test_coverage"] == 0.35
        assert evidence["weights"]["type_annotations"] == 0.25
        assert evidence["weights"]["error_handling"] == 0.25
        assert evidence["weights"]["documentation"] == 0.15

        # Verify formula
        test = evidence["components"]["test_coverage"]["score"]
        type_ann = evidence["components"]["type_annotations"]["score"]
        error = evidence["components"]["error_handling"]["score"]
        doc = evidence["components"]["documentation"]["score"]

        expected = 0.35 * test + 0.25 * type_ann + 0.25 * error + 0.15 * doc
        assert abs(b_impl - expected) < 0.001


class TestBDeployFormula:
    """Test b_deploy formula: 0.4*validation + 0.35*stability + 0.25*failure"""

    def test_exact_formula(self, rubric):
        """Test exact weighted formula"""
        method_info = {"layer": "analyzer"}

        b_deploy, evidence = compute_b_deploy(method_info, rubric)

        # Verify weights
        assert evidence["weights"]["validation_runs"] == 0.4
        assert evidence["weights"]["stability_coefficient"] == 0.35
        assert evidence["weights"]["failure_rate"] == 0.25

        # Verify formula
        validation = evidence["components"]["validation_runs"]["score"]
        stability = evidence["components"]["stability_coefficient"]["score"]
        failure = evidence["components"]["failure_rate"]["score"]

        expected = 0.4 * validation + 0.35 * stability + 0.25 * failure
        assert abs(b_deploy - expected) < 0.001

    def test_layer_maturity_fallback(self, rubric):
        """Test fallback uses layer maturity baselines"""
        method_info = {"layer": "orchestrator"}
        b_deploy, evidence = compute_b_deploy(method_info, rubric)

        # Orchestrator baseline is 0.7
        validation_component = evidence["components"]["validation_runs"]
        assert validation_component["layer_maturity_baseline"] == 0.7

        stability_component = evidence["components"]["stability_coefficient"]
        assert stability_component["layer_maturity_baseline"] == 0.7

        failure_component = evidence["components"]["failure_rate"]
        assert failure_component["layer_maturity_baseline"] == 0.7


class TestFormulaTraceability:
    """Test that all scores include traceable evidence"""

    def test_b_theory_traceability(self, rubric):
        """Test b_theory evidence is complete"""
        method_info = {"method_name": "test", "docstring": "Test method"}
        score, evidence = compute_b_theory(method_info, rubric)

        assert "formula" in evidence
        assert "weights" in evidence
        assert "components" in evidence
        assert "computation" in evidence
        assert "final_score" in evidence

    def test_b_impl_traceability(self, rubric, repo_root):
        """Test b_impl evidence is complete"""
        method_info = {
            "method_name": "test",
            "docstring": "Test",
            "input_parameters": [],
            "return_type": None,
            "file_path": "test.py",
            "line_number": 1,
        }
        score, evidence = compute_b_impl(method_info, repo_root, rubric)

        assert "formula" in evidence
        assert "weights" in evidence
        assert "components" in evidence
        assert "computation" in evidence
        assert "final_score" in evidence

    def test_b_deploy_traceability(self, rubric):
        """Test b_deploy evidence is complete"""
        method_info = {"layer": "processor"}
        score, evidence = compute_b_deploy(method_info, rubric)

        assert "formula" in evidence
        assert "weights" in evidence
        assert "components" in evidence
        assert "computation" in evidence
        assert "final_score" in evidence

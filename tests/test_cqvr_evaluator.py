"""
Unit tests for CQVR evaluator scoring functions
Tests all 10 scoring functions for correctness and edge cases
"""
import sys
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from cqvr_evaluator_standalone import (
    verify_identity_schema_coherence,
    verify_method_assembly_alignment,
    verify_signal_requirements,
    verify_output_schema,
    verify_pattern_coverage,
    verify_method_specificity,
    verify_validation_rules,
    verify_documentation_quality,
    verify_human_template,
    verify_metadata_completeness,
    make_triage_decision,
    evaluate_contract,
)


# ============================================================================
# TIER 1 TESTS (55 pts)
# ============================================================================


@pytest.mark.updated
def test_verify_identity_schema_coherence_perfect():
    """Test A1 with perfect identity-schema match (20 pts)"""
    contract = {
        "identity": {
            "question_id": "Q001",
            "policy_area_id": "PA01",
            "dimension_id": "DIM01",
            "question_global": 1,
            "base_slot": "D1-Q1"
        },
        "output_contract": {
            "schema": {
                "properties": {
                    "question_id": {"const": "Q001"},
                    "policy_area_id": {"const": "PA01"},
                    "dimension_id": {"const": "DIM01"},
                    "question_global": {"const": 1},
                    "base_slot": {"const": "D1-Q1"}
                }
            }
        }
    }
    
    score, issues = verify_identity_schema_coherence(contract)
    
    assert score == 20, f"Expected 20 pts, got {score}"
    assert len(issues) == 0, f"Expected no issues, got {issues}"


@pytest.mark.updated
def test_verify_identity_schema_coherence_mismatch():
    """Test A1 with identity-schema mismatch (0 pts + issues)"""
    contract = {
        "identity": {
            "question_id": "Q001",
            "policy_area_id": "PA01",
            "dimension_id": "DIM01",
            "question_global": 1,
            "base_slot": "D1-Q1"
        },
        "output_contract": {
            "schema": {
                "properties": {
                    "question_id": {"const": "Q002"},  # Mismatch
                    "policy_area_id": {"const": "PA02"},  # Mismatch
                    "dimension_id": {"const": "DIM01"},
                    "question_global": {"const": 1},
                    "base_slot": {"const": "D1-Q1"}
                }
            }
        }
    }
    
    score, issues = verify_identity_schema_coherence(contract)
    
    assert score == 10, f"Expected 10 pts (3 matches), got {score}"
    assert len(issues) == 2, f"Expected 2 issues, got {len(issues)}"
    assert any("question_id" in i for i in issues)
    assert any("policy_area_id" in i for i in issues)


@pytest.mark.updated
def test_verify_method_assembly_alignment_perfect():
    """Test A2 with perfect method-assembly alignment (20 pts)"""
    contract = {
        "method_binding": {
            "method_count": 2,
            "methods": [
                {"provides": "method.a"},
                {"provides": "method.b"}
            ]
        },
        "evidence_assembly": {
            "assembly_rules": [
                {"sources": ["method.a", "method.b"]}
            ]
        }
    }
    
    score, issues = verify_method_assembly_alignment(contract)
    
    assert score == 20, f"Expected 20 pts, got {score}"
    assert len(issues) == 0, f"Expected no issues, got {issues}"


@pytest.mark.updated
def test_verify_method_assembly_alignment_orphan_sources():
    """Test A2 with orphan sources (reduced score + issues)"""
    contract = {
        "method_binding": {
            "method_count": 2,
            "methods": [
                {"provides": "method.a"},
                {"provides": "method.b"}
            ]
        },
        "evidence_assembly": {
            "assembly_rules": [
                {"sources": ["method.a", "method.c"]}  # method.c is orphan
            ]
        }
    }
    
    score, issues = verify_method_assembly_alignment(contract)
    
    assert score < 20, f"Expected < 20 pts with orphan, got {score}"
    assert any("orphan" in i.lower() or "not in provides" in i.lower() for i in issues)


@pytest.mark.updated
def test_verify_signal_requirements_valid():
    """Test A3 with valid signal configuration (10 pts)"""
    contract = {
        "signal_requirements": {
            "mandatory_signals": ["signal1", "signal2"],
            "minimum_signal_threshold": 0.5,
            "signal_aggregation": "weighted_mean"
        }
    }
    
    score, issues = verify_signal_requirements(contract)
    
    assert score == 10, f"Expected 10 pts, got {score}"
    assert len(issues) == 0, f"Expected no issues, got {issues}"


@pytest.mark.updated
def test_verify_signal_requirements_critical_fail():
    """Test A3 with CRITICAL: mandatory_signals + threshold=0 (0 pts)"""
    contract = {
        "signal_requirements": {
            "mandatory_signals": ["signal1", "signal2"],
            "minimum_signal_threshold": 0.0,  # CRITICAL ERROR
            "signal_aggregation": "weighted_mean"
        }
    }
    
    score, issues = verify_signal_requirements(contract)
    
    assert score == 0, f"Expected 0 pts for critical error, got {score}"
    assert len(issues) > 0, f"Expected critical issue"
    assert any("CRITICAL" in i for i in issues)


@pytest.mark.updated
def test_verify_output_schema_complete():
    """Test A4 with complete output schema (5 pts)"""
    contract = {
        "output_contract": {
            "schema": {
                "required": ["field1", "field2"],
                "properties": {
                    "field1": {"type": "string"},
                    "field2": {"type": "integer"}
                }
            }
        },
        "traceability": {
            "source_hash": "a" * 64  # Valid hash
        }
    }
    
    score, issues = verify_output_schema(contract)
    
    assert score == 5, f"Expected 5 pts, got {score}"
    assert len(issues) == 0, f"Expected no issues, got {issues}"


@pytest.mark.updated
def test_verify_output_schema_missing_properties():
    """Test A4 with missing property definitions (reduced score)"""
    contract = {
        "output_contract": {
            "schema": {
                "required": ["field1", "field2"],
                "properties": {
                    "field1": {"type": "string"}
                    # field2 missing!
                }
            }
        },
        "traceability": {
            "source_hash": "valid_hash"
        }
    }
    
    score, issues = verify_output_schema(contract)
    
    assert score < 5, f"Expected < 5 pts with missing property, got {score}"
    assert any("field2" in str(i) for i in issues)


# ============================================================================
# TIER 2 TESTS (30 pts)
# ============================================================================


@pytest.mark.updated
def test_verify_pattern_coverage_good():
    """Test B1 with good pattern coverage (10 pts)"""
    contract = {
        "question_context": {
            "expected_elements": [
                {"type": "elem1", "required": True},
                {"type": "elem2", "required": True}
            ],
            "patterns": [
                {"id": "p1", "category": "CAT1", "confidence_weight": 0.8},
                {"id": "p2", "category": "CAT2", "confidence_weight": 0.7}
            ]
        }
    }
    
    score, issues = verify_pattern_coverage(contract)
    
    assert score == 10, f"Expected 10 pts, got {score}"
    assert len(issues) == 0, f"Expected no issues, got {issues}"


@pytest.mark.updated
def test_verify_pattern_coverage_no_patterns():
    """Test B1 with no patterns defined (0 pts)"""
    contract = {
        "question_context": {
            "expected_elements": [{"type": "elem1", "required": True}],
            "patterns": []
        }
    }
    
    score, issues = verify_pattern_coverage(contract)
    
    assert score == 0, f"Expected 0 pts with no patterns, got {score}"
    assert len(issues) > 0


@pytest.mark.updated
def test_verify_method_specificity_specific():
    """Test B2 with specific (non-boilerplate) methods (10 pts)"""
    contract = {
        "methodological_depth": {
            "methods": [
                {
                    "technical_approach": {
                        "steps": [
                            {"description": "Apply Bayesian inference using PyMC"}
                        ],
                        "complexity": "O(n²) quadratic time for matrix operations",
                        "assumptions": ["Data follows normal distribution"]
                    }
                }
            ]
        }
    }
    
    score, issues = verify_method_specificity(contract)
    
    assert score > 0, f"Expected > 0 pts for specific method, got {score}"


@pytest.mark.updated
def test_verify_method_specificity_boilerplate():
    """Test B2 with boilerplate methods (low score)"""
    contract = {
        "methodological_depth": {
            "methods": [
                {
                    "technical_approach": {
                        "steps": [
                            {"description": "Execute the method"}  # Boilerplate
                        ],
                        "complexity": "O(n) where n=input size",  # Generic
                        "assumptions": ["Input data is preprocessed and valid"]  # Generic
                    }
                }
            ]
        }
    }
    
    score, issues = verify_method_specificity(contract)
    
    assert score < 8, f"Expected low score for boilerplate, got {score}"


@pytest.mark.updated
def test_verify_validation_rules_complete():
    """Test B3 with complete validation rules (10 pts)"""
    contract = {
        "validation_rules": {
            "rules": [
                {
                    "must_contain": {"elements": ["elem1", "elem2"]},
                    "should_contain": [{"elements": ["elem3"]}]
                }
            ]
        },
        "question_context": {
            "expected_elements": [
                {"type": "elem1", "required": True},
                {"type": "elem2", "required": True}
            ]
        },
        "error_handling": {
            "failure_contract": {"emit_code": "ERR_001"}
        }
    }
    
    score, issues = verify_validation_rules(contract)
    
    assert score == 10, f"Expected 10 pts, got {score}"
    assert len(issues) == 0, f"Expected no issues, got {issues}"


@pytest.mark.updated
def test_verify_validation_rules_no_rules():
    """Test B3 with no validation rules (0 pts)"""
    contract = {
        "validation_rules": {"rules": []},
        "question_context": {"expected_elements": []},
        "error_handling": {}
    }
    
    score, issues = verify_validation_rules(contract)
    
    assert score == 0, f"Expected 0 pts with no rules, got {score}"
    assert len(issues) > 0


# ============================================================================
# TIER 3 TESTS (15 pts)
# ============================================================================


@pytest.mark.updated
def test_verify_documentation_quality_specific():
    """Test C1 with specific epistemological documentation (5 pts)"""
    contract = {
        "methodological_depth": {
            "methods": [
                {
                    "epistemological_foundation": {
                        "paradigm": "Frequentist hypothesis testing",
                        "justification": "We use this approach because it provides why...",
                        "theoretical_framework": ["Fisher, 1925"]
                    }
                }
            ]
        }
    }
    
    score, issues = verify_documentation_quality(contract)
    
    assert score > 0, f"Expected > 0 pts for specific docs, got {score}"


@pytest.mark.updated
def test_verify_documentation_quality_boilerplate():
    """Test C1 with boilerplate documentation (low score)"""
    contract = {
        "methodological_depth": {
            "methods": [
                {
                    "epistemological_foundation": {
                        "paradigm": "analytical paradigm",  # Boilerplate
                        "justification": "This method contributes to analysis",  # Boilerplate
                        "theoretical_framework": []
                    }
                }
            ]
        }
    }
    
    score, issues = verify_documentation_quality(contract)
    
    assert score == 0, f"Expected 0 pts for boilerplate, got {score}"


@pytest.mark.updated
def test_verify_human_template_good():
    """Test C2 with good human template (5 pts)"""
    contract = {
        "identity": {
            "base_slot": "D1-Q1",
            "question_id": "Q001"
        },
        "output_contract": {
            "human_readable_output": {
                "template": {
                    "title": "Analysis for D1-Q1",
                    "summary": "The result is {score} with {confidence} confidence"
                }
            }
        }
    }
    
    score, issues = verify_human_template(contract)
    
    assert score == 5, f"Expected 5 pts, got {score}"
    assert len(issues) == 0, f"Expected no issues, got {issues}"


@pytest.mark.updated
def test_verify_human_template_no_references():
    """Test C2 with template missing references (reduced score)"""
    contract = {
        "identity": {
            "base_slot": "D1-Q1",
            "question_id": "Q001"
        },
        "output_contract": {
            "human_readable_output": {
                "template": {
                    "title": "Generic Title",  # No reference to base_slot/question_id
                    "summary": "Static text with no placeholders"
                }
            }
        }
    }
    
    score, issues = verify_human_template(contract)
    
    assert score < 5, f"Expected < 5 pts with missing refs, got {score}"
    assert len(issues) > 0


@pytest.mark.updated
def test_verify_metadata_completeness_full():
    """Test C3 with complete metadata (5 pts)"""
    contract = {
        "identity": {
            "contract_hash": "a" * 64,
            "created_at": "2025-01-01T00:00:00Z",
            "validated_against_schema": "v3.schema.json",
            "contract_version": "3.0.0"
        },
        "traceability": {
            "source_hash": "b" * 64
        }
    }
    
    score, issues = verify_metadata_completeness(contract)
    
    assert score == 5, f"Expected 5 pts, got {score}"


@pytest.mark.updated
def test_verify_metadata_completeness_missing():
    """Test C3 with missing metadata (reduced score)"""
    contract = {
        "identity": {
            "contract_hash": "short",  # Invalid
            "contract_version": "3.0.0"
        },
        "traceability": {
            "source_hash": "TODO"  # Placeholder
        }
    }
    
    score, issues = verify_metadata_completeness(contract)
    
    assert score < 5, f"Expected < 5 pts with missing metadata, got {score}"
    assert len(issues) > 0


# ============================================================================
# DECISION ENGINE TESTS
# ============================================================================


@pytest.mark.updated
def test_make_triage_decision_production():
    """Test decision engine: PRODUCCION for high scores"""
    decision = make_triage_decision(
        tier1_score=50,
        tier2_score=25,
        tier3_score=10,
        all_issues=[]
    )
    
    assert decision["status"] == "PRODUCCION"
    assert len(decision["blockers"]) == 0


@pytest.mark.updated
def test_make_triage_decision_parchear():
    """Test decision engine: PARCHEAR for acceptable scores"""
    decision = make_triage_decision(
        tier1_score=40,
        tier2_score=20,
        tier3_score=10,
        all_issues=["B1: Minor issue"]
    )
    
    assert decision["status"] == "PARCHEAR"


@pytest.mark.updated
def test_make_triage_decision_reformular():
    """Test decision engine: REFORMULAR for low tier1"""
    decision = make_triage_decision(
        tier1_score=30,  # Below threshold
        tier2_score=20,
        tier3_score=10,
        all_issues=["A1: Critical issue"]
    )
    
    assert decision["status"] == "REFORMULAR"


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


@pytest.mark.updated
def test_evaluate_contract_full():
    """Test full contract evaluation pipeline"""
    contract = {
        "identity": {
            "question_id": "Q001",
            "policy_area_id": "PA01",
            "dimension_id": "DIM01",
            "question_global": 1,
            "base_slot": "D1-Q1",
            "contract_hash": "a" * 64,
            "created_at": "2025-01-01T00:00:00Z",
            "contract_version": "3.0.0"
        },
        "output_contract": {
            "schema": {
                "required": ["field1"],
                "properties": {
                    "question_id": {"const": "Q001"},
                    "policy_area_id": {"const": "PA01"},
                    "dimension_id": {"const": "DIM01"},
                    "question_global": {"const": 1},
                    "base_slot": {"const": "D1-Q1"},
                    "field1": {"type": "string"}
                }
            },
            "human_readable_output": {
                "template": {
                    "title": "Analysis for Q001",
                    "summary": "Result: {score}"
                }
            }
        },
        "method_binding": {
            "method_count": 1,
            "methods": [{"provides": "method.a"}]
        },
        "evidence_assembly": {
            "assembly_rules": [{"sources": ["method.a"]}]
        },
        "signal_requirements": {
            "mandatory_signals": ["sig1"],
            "minimum_signal_threshold": 0.5,
            "signal_aggregation": "weighted_mean"
        },
        "question_context": {
            "expected_elements": [{"type": "elem1", "required": True}],
            "patterns": [{"id": "p1", "confidence_weight": 0.8}]
        },
        "methodological_depth": {
            "methods": [
                {
                    "technical_approach": {
                        "steps": [{"description": "Specific step"}],
                        "complexity": "O(n log n)",
                        "assumptions": ["Normal distribution"]
                    },
                    "epistemological_foundation": {
                        "paradigm": "Bayesian",
                        "justification": "Why this approach",
                        "theoretical_framework": ["Bayes, 1763"]
                    }
                }
            ]
        },
        "validation_rules": {
            "rules": [{"must_contain": {"elements": ["elem1"]}}]
        },
        "error_handling": {
            "failure_contract": {"emit_code": "ERR_001"}
        },
        "traceability": {
            "source_hash": "b" * 64
        }
    }
    
    report = evaluate_contract(contract)
    
    assert report["contract_id"] == "Q001"
    assert "scores" in report
    assert "decision" in report
    assert "issues" in report
    
    # Verify score structure
    assert report["scores"]["tier1"]["score"] >= 0
    assert report["scores"]["tier2"]["score"] >= 0
    assert report["scores"]["tier3"]["score"] >= 0
    assert report["scores"]["total"]["score"] >= 0
    
    # Verify decision structure
    assert report["decision"]["status"] in ["PRODUCCION", "PARCHEAR", "REFORMULAR"]
    assert "rationale" in report["decision"]
    assert "remediation" in report["decision"]


@pytest.mark.updated
def test_determinism():
    """Test that evaluation is deterministic (same input = same output)"""
    contract = {
        "identity": {"question_id": "Q999"},
        "output_contract": {"schema": {"required": [], "properties": {}}},
        "method_binding": {"methods": []},
        "evidence_assembly": {"assembly_rules": []},
        "signal_requirements": {},
        "question_context": {"expected_elements": [], "patterns": []},
        "methodological_depth": {"methods": []},
        "validation_rules": {"rules": []},
        "error_handling": {},
        "traceability": {}
    }
    
    report1 = evaluate_contract(contract)
    report2 = evaluate_contract(contract)
    
    # Remove timestamps for comparison
    del report1["evaluation_timestamp"]
    del report2["evaluation_timestamp"]
    
    assert report1 == report2, "Evaluation should be deterministic"

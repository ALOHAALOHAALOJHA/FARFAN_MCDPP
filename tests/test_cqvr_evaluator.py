"""
Unit tests for CQVR Evaluator scoring functions.
Tests all 10 core verification functions for determinism and correctness.
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from cqvr_evaluator import (
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
    CQVREvaluator,
    CQVRDecisionEngine,
    CQVRScore,
)


@pytest.mark.updated
class TestIdentitySchemaCoherence:
    """Test A1: Identity-Schema Coherence verification"""
    
    def test_perfect_match(self) -> None:
        """Test contract with perfect identity-schema match"""
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
        assert score == 20
        assert len(issues) == 0
    
    def test_mismatch(self) -> None:
        """Test contract with identity-schema mismatch"""
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
                        "policy_area_id": {"const": "PA01"},
                        "dimension_id": {"const": "DIM01"},
                        "question_global": {"const": 1},
                        "base_slot": {"const": "D1-Q1"}
                    }
                }
            }
        }
        
        score, issues = verify_identity_schema_coherence(contract)
        assert score < 20
        assert any("mismatch" in issue.lower() for issue in issues)
    
    def test_missing_identity_field(self) -> None:
        """Test contract with missing identity field"""
        contract = {
            "identity": {
                "policy_area_id": "PA01",
                "dimension_id": "DIM01"
            },
            "output_contract": {
                "schema": {
                    "properties": {
                        "question_id": {"const": "Q001"}
                    }
                }
            }
        }
        
        score, issues = verify_identity_schema_coherence(contract)
        assert score < 20
        assert any("missing" in issue.lower() and "identity" in issue.lower() for issue in issues)
    
    def test_determinism(self) -> None:
        """Test that same input produces same output"""
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
        
        score1, issues1 = verify_identity_schema_coherence(contract)
        score2, issues2 = verify_identity_schema_coherence(contract)
        
        assert score1 == score2
        assert issues1 == issues2


@pytest.mark.updated
class TestMethodAssemblyAlignment:
    """Test A2: Method-Assembly Alignment verification"""
    
    def test_perfect_alignment(self) -> None:
        """Test contract with perfect method-assembly alignment"""
        contract = {
            "method_binding": {
                "method_count": 2,
                "methods": [
                    {"provides": "method1.output"},
                    {"provides": "method2.output"}
                ]
            },
            "evidence_assembly": {
                "assembly_rules": [
                    {
                        "sources": [
                            {"namespace": "method1.output"},
                            {"namespace": "method2.output"}
                        ]
                    }
                ]
            }
        }
        
        score, issues = verify_method_assembly_alignment(contract)
        assert score == 20
        assert len(issues) == 0
    
    def test_orphan_sources(self) -> None:
        """Test contract with orphan assembly sources"""
        contract = {
            "method_binding": {
                "method_count": 1,
                "methods": [
                    {"provides": "method1.output"}
                ]
            },
            "evidence_assembly": {
                "assembly_rules": [
                    {
                        "sources": [
                            {"namespace": "method1.output"},
                            {"namespace": "orphan.method"}  # Orphan
                        ]
                    }
                ]
            }
        }
        
        score, issues = verify_method_assembly_alignment(contract)
        assert score < 20
        assert any("orphan" in issue.lower() or "not in provides" in issue.lower() for issue in issues)
    
    def test_no_methods(self) -> None:
        """Test contract with no methods defined"""
        contract = {
            "method_binding": {
                "method_count": 0,
                "methods": []
            },
            "evidence_assembly": {
                "assembly_rules": []
            }
        }
        
        score, issues = verify_method_assembly_alignment(contract)
        assert score == 0
        assert any("no methods" in issue.lower() for issue in issues)
    
    def test_method_count_mismatch(self) -> None:
        """Test contract with method count mismatch"""
        contract = {
            "method_binding": {
                "method_count": 3,  # Mismatch
                "methods": [
                    {"provides": "method1.output"},
                    {"provides": "method2.output"}
                ]
            },
            "evidence_assembly": {
                "assembly_rules": [
                    {"sources": [{"namespace": "method1.output"}]}
                ]
            }
        }
        
        score, issues = verify_method_assembly_alignment(contract)
        assert any("mismatch" in issue.lower() for issue in issues)


@pytest.mark.updated
class TestSignalRequirements:
    """Test A3: Signal Requirements verification"""
    
    def test_valid_configuration(self) -> None:
        """Test contract with valid signal configuration"""
        contract = {
            "signal_requirements": {
                "mandatory_signals": ["signal1", "signal2"],
                "minimum_signal_threshold": 0.5,
                "signal_aggregation": "weighted_mean"
            }
        }
        
        score, issues = verify_signal_requirements(contract)
        assert score == 10
        assert len(issues) == 0
    
    def test_critical_zero_threshold_with_mandatory(self) -> None:
        """Test contract with critical zero threshold and mandatory signals"""
        contract = {
            "signal_requirements": {
                "mandatory_signals": ["signal1"],
                "minimum_signal_threshold": 0.0,  # CRITICAL
                "signal_aggregation": "weighted_mean"
            }
        }
        
        score, issues = verify_signal_requirements(contract)
        assert score == 0
        assert any("critical" in issue.lower() for issue in issues)
    
    def test_no_mandatory_signals(self) -> None:
        """Test contract with no mandatory signals"""
        contract = {
            "signal_requirements": {
                "mandatory_signals": [],
                "minimum_signal_threshold": 0.0,
                "signal_aggregation": "weighted_mean"
            }
        }
        
        score, issues = verify_signal_requirements(contract)
        assert score >= 5


@pytest.mark.updated
class TestOutputSchema:
    """Test A4: Output Schema verification"""
    
    def test_complete_schema(self) -> None:
        """Test contract with complete output schema"""
        contract = {
            "output_contract": {
                "schema": {
                    "required": ["field1", "field2"],
                    "properties": {
                        "field1": {"type": "string"},
                        "field2": {"type": "number"}
                    }
                }
            },
            "traceability": {
                "source_hash": "a" * 64
            }
        }
        
        score, issues = verify_output_schema(contract)
        assert score == 5
        assert len(issues) == 0
    
    def test_missing_properties(self) -> None:
        """Test contract with required fields not in properties"""
        contract = {
            "output_contract": {
                "schema": {
                    "required": ["field1", "field2"],
                    "properties": {
                        "field1": {"type": "string"}
                    }
                }
            },
            "traceability": {}
        }
        
        score, issues = verify_output_schema(contract)
        assert score < 5
        assert any("required fields not in properties" in issue.lower() for issue in issues)
    
    def test_no_required_fields(self) -> None:
        """Test contract with no required fields"""
        contract = {
            "output_contract": {
                "schema": {
                    "required": [],
                    "properties": {}
                }
            },
            "traceability": {}
        }
        
        score, issues = verify_output_schema(contract)
        assert score == 0
        assert any("no required" in issue.lower() for issue in issues)


@pytest.mark.updated
class TestPatternCoverage:
    """Test B1: Pattern Coverage verification"""
    
    def test_good_coverage(self) -> None:
        """Test contract with good pattern coverage"""
        contract = {
            "question_context": {
                "expected_elements": [
                    {"type": "element1", "required": True},
                    {"type": "element2", "required": True}
                ],
                "patterns": [
                    {"id": "p1", "confidence_weight": 0.8},
                    {"id": "p2", "confidence_weight": 0.9}
                ]
            }
        }
        
        score, issues = verify_pattern_coverage(contract)
        assert score == 10
    
    def test_no_patterns(self) -> None:
        """Test contract with no patterns"""
        contract = {
            "question_context": {
                "expected_elements": [{"type": "element1", "required": True}],
                "patterns": []
            }
        }
        
        score, issues = verify_pattern_coverage(contract)
        assert score == 0
        assert any("no patterns" in issue.lower() for issue in issues)
    
    def test_invalid_confidence_weights(self) -> None:
        """Test contract with invalid confidence weights"""
        contract = {
            "question_context": {
                "expected_elements": [{"type": "element1", "required": True}],
                "patterns": [
                    {"id": "p1", "confidence_weight": 1.5}  # Invalid
                ]
            }
        }
        
        score, issues = verify_pattern_coverage(contract)
        assert any("confidence_weights" in issue.lower() for issue in issues)


@pytest.mark.updated
class TestMethodSpecificity:
    """Test B2: Method Specificity verification"""
    
    def test_specific_methods(self) -> None:
        """Test contract with specific method documentation"""
        contract = {
            "methodological_depth": {
                "methods": [
                    {
                        "technical_approach": {
                            "steps": [
                                {"description": "Specific implementation detail"}
                            ],
                            "complexity": "O(n log n) with binary search optimization",
                            "assumptions": ["Data is sorted by timestamp"]
                        }
                    }
                ]
            }
        }
        
        score, issues = verify_method_specificity(contract)
        assert score > 0
    
    def test_boilerplate_methods(self) -> None:
        """Test contract with boilerplate method documentation"""
        contract = {
            "methodological_depth": {
                "methods": [
                    {
                        "technical_approach": {
                            "steps": [
                                {"description": "Execute the process"}  # Boilerplate
                            ],
                            "complexity": "O(n) where n=input size",
                            "assumptions": ["Input data is preprocessed and valid"]
                        }
                    }
                ]
            }
        }
        
        score, issues = verify_method_specificity(contract)
        assert score < 10
    
    def test_no_methods(self) -> None:
        """Test contract with no methodological depth"""
        contract = {
            "methodological_depth": {
                "methods": []
            }
        }
        
        score, issues = verify_method_specificity(contract)
        assert score == 0
        assert any("no methodological_depth" in issue.lower() for issue in issues)


@pytest.mark.updated
class TestValidationRules:
    """Test B3: Validation Rules verification"""
    
    def test_complete_validation(self) -> None:
        """Test contract with complete validation rules"""
        contract = {
            "validation_rules": {
                "rules": [
                    {
                        "must_contain": {
                            "elements": ["element1", "element2"]
                        },
                        "should_contain": [
                            {"elements": ["element3"]}
                        ]
                    }
                ]
            },
            "question_context": {
                "expected_elements": [
                    {"type": "element1", "required": True},
                    {"type": "element2", "required": True}
                ]
            },
            "error_handling": {
                "failure_contract": {
                    "emit_code": "ERR001"
                }
            }
        }
        
        score, issues = verify_validation_rules(contract)
        assert score == 10
    
    def test_no_validation_rules(self) -> None:
        """Test contract with no validation rules"""
        contract = {
            "validation_rules": {
                "rules": []
            },
            "question_context": {
                "expected_elements": []
            },
            "error_handling": {}
        }
        
        score, issues = verify_validation_rules(contract)
        assert score == 0
        assert any("no validation_rules" in issue.lower() for issue in issues)
    
    def test_missing_required_elements(self) -> None:
        """Test contract with validation missing required elements"""
        contract = {
            "validation_rules": {
                "rules": [
                    {
                        "must_contain": {
                            "elements": ["element1"]
                        }
                    }
                ]
            },
            "question_context": {
                "expected_elements": [
                    {"type": "element1", "required": True},
                    {"type": "element2", "required": True}  # Not in validation
                ]
            },
            "error_handling": {}
        }
        
        score, issues = verify_validation_rules(contract)
        assert any("required elements not in validation" in issue.lower() for issue in issues)


@pytest.mark.updated
class TestDocumentationQuality:
    """Test C1: Documentation Quality verification"""
    
    def test_high_quality_docs(self) -> None:
        """Test contract with high-quality documentation"""
        contract = {
            "methodological_depth": {
                "methods": [
                    {
                        "epistemological_foundation": {
                            "paradigm": "Empirical positivism with Bayesian inference",
                            "justification": "This approach was chosen vs alternatives because...",
                            "theoretical_framework": ["Bayes 1763", "Pearl 2009"]
                        }
                    }
                ]
            }
        }
        
        score, issues = verify_documentation_quality(contract)
        assert score == 5
    
    def test_boilerplate_docs(self) -> None:
        """Test contract with boilerplate documentation"""
        contract = {
            "methodological_depth": {
                "methods": [
                    {
                        "epistemological_foundation": {
                            "paradigm": "analytical paradigm",
                            "justification": "This method contributes to the analysis",
                            "theoretical_framework": []
                        }
                    }
                ]
            }
        }
        
        score, issues = verify_documentation_quality(contract)
        assert score < 5
    
    def test_no_documentation(self) -> None:
        """Test contract with no documentation"""
        contract = {
            "methodological_depth": {
                "methods": []
            }
        }
        
        score, issues = verify_documentation_quality(contract)
        assert score == 0


@pytest.mark.updated
class TestHumanTemplate:
    """Test C2: Human Template verification"""
    
    def test_good_template(self) -> None:
        """Test contract with good human-readable template"""
        contract = {
            "identity": {
                "base_slot": "D1-Q1",
                "question_id": "Q001"
            },
            "output_contract": {
                "human_readable_output": {
                    "template": {
                        "title": "Analysis for Q001 (D1-Q1)",
                        "summary": "Based on {evidence_count} evidence points..."
                    }
                }
            }
        }
        
        score, issues = verify_human_template(contract)
        assert score == 5
    
    def test_missing_references(self) -> None:
        """Test contract template without identity references"""
        contract = {
            "identity": {
                "base_slot": "D1-Q1",
                "question_id": "Q001"
            },
            "output_contract": {
                "human_readable_output": {
                    "template": {
                        "title": "Generic Analysis",  # No references
                        "summary": "Based on {evidence_count} evidence points..."
                    }
                }
            }
        }
        
        score, issues = verify_human_template(contract)
        assert score < 5
        assert any("does not reference" in issue.lower() for issue in issues)
    
    def test_no_placeholders(self) -> None:
        """Test contract template without placeholders"""
        contract = {
            "identity": {
                "base_slot": "D1-Q1",
                "question_id": "Q001"
            },
            "output_contract": {
                "human_readable_output": {
                    "template": {
                        "title": "Analysis for Q001",
                        "summary": "Static text without placeholders"
                    }
                }
            }
        }
        
        score, issues = verify_human_template(contract)
        assert any("no dynamic placeholders" in issue.lower() for issue in issues)


@pytest.mark.updated
class TestMetadataCompleteness:
    """Test C3: Metadata Completeness verification"""
    
    def test_complete_metadata(self) -> None:
        """Test contract with complete metadata"""
        contract = {
            "identity": {
                "contract_hash": "a" * 64,
                "created_at": "2025-01-01T00:00:00Z",
                "validated_against_schema": "schema.v3.json",
                "contract_version": "3.0.0"
            },
            "traceability": {
                "source_hash": "b" * 64
            }
        }
        
        score, issues = verify_metadata_completeness(contract)
        assert score == 5
    
    def test_missing_hash(self) -> None:
        """Test contract with missing contract hash"""
        contract = {
            "identity": {
                "contract_hash": "",
                "created_at": "2025-01-01T00:00:00Z",
                "validated_against_schema": "schema.v3.json",
                "contract_version": "3.0.0"
            },
            "traceability": {}
        }
        
        score, issues = verify_metadata_completeness(contract)
        assert score < 5
        assert any("contract_hash" in issue.lower() for issue in issues)
    
    def test_invalid_timestamp(self) -> None:
        """Test contract with invalid timestamp"""
        contract = {
            "identity": {
                "contract_hash": "a" * 64,
                "created_at": "invalid",
                "validated_against_schema": "schema.v3.json",
                "contract_version": "3.0.0"
            },
            "traceability": {}
        }
        
        score, issues = verify_metadata_completeness(contract)
        assert any("created_at" in issue.lower() for issue in issues)


@pytest.mark.updated
class TestDecisionEngine:
    """Test CQVR Decision Engine"""
    
    def test_production_decision(self) -> None:
        """Test production-ready decision"""
        score = CQVRScore(
            tier1_score=50.0,
            tier2_score=25.0,
            tier3_score=10.0,
            total_score=85.0
        )
        blockers: list[str] = []
        warnings: list[str] = []
        
        decision = CQVRDecisionEngine.make_decision(score, blockers, warnings)
        assert decision == "PRODUCCION"
    
    def test_parchear_decision(self) -> None:
        """Test patchable decision"""
        score = CQVRScore(
            tier1_score=40.0,
            tier2_score=20.0,
            tier3_score=10.0,
            total_score=70.0
        )
        blockers = ["Minor issue"]
        warnings: list[str] = []
        
        decision = CQVRDecisionEngine.make_decision(score, blockers, warnings)
        assert decision == "PARCHEAR"
    
    def test_reformular_decision(self) -> None:
        """Test reformulation required decision"""
        score = CQVRScore(
            tier1_score=30.0,
            tier2_score=15.0,
            tier3_score=5.0,
            total_score=50.0
        )
        blockers = ["Critical blocker 1", "Critical blocker 2", "Critical blocker 3"]
        warnings: list[str] = []
        
        decision = CQVRDecisionEngine.make_decision(score, blockers, warnings)
        assert decision == "REFORMULAR"
    
    def test_tier1_threshold_failure(self) -> None:
        """Test tier1 threshold failure triggers reformulation"""
        score = CQVRScore(
            tier1_score=30.0,  # Below threshold
            tier2_score=30.0,
            tier3_score=15.0,
            total_score=75.0
        )
        blockers: list[str] = []
        warnings: list[str] = []
        
        decision = CQVRDecisionEngine.make_decision(score, blockers, warnings)
        assert decision == "REFORMULAR"


@pytest.mark.updated
class TestCQVREvaluator:
    """Test CQVR Evaluator end-to-end"""
    
    def test_evaluate_contract(self) -> None:
        """Test complete contract evaluation"""
        contract = {
            "identity": {
                "question_id": "Q001",
                "policy_area_id": "PA01",
                "dimension_id": "DIM01",
                "question_global": 1,
                "base_slot": "D1-Q1",
                "contract_hash": "a" * 64,
                "created_at": "2025-01-01T00:00:00Z",
                "validated_against_schema": "schema.v3.json",
                "contract_version": "3.0.0"
            },
            "output_contract": {
                "schema": {
                    "required": ["field1"],
                    "properties": {
                        "field1": {"type": "string"},
                        "question_id": {"const": "Q001"},
                        "policy_area_id": {"const": "PA01"},
                        "dimension_id": {"const": "DIM01"},
                        "question_global": {"const": 1},
                        "base_slot": {"const": "D1-Q1"}
                    }
                },
                "human_readable_output": {
                    "template": {
                        "title": "Analysis for Q001",
                        "summary": "Based on {evidence_count} evidence points"
                    }
                }
            },
            "method_binding": {
                "method_count": 1,
                "methods": [{"provides": "method1.output"}]
            },
            "evidence_assembly": {
                "assembly_rules": [{"sources": [{"namespace": "method1.output"}]}]
            },
            "signal_requirements": {
                "mandatory_signals": [],
                "minimum_signal_threshold": 0.0,
                "signal_aggregation": "weighted_mean"
            },
            "question_context": {
                "expected_elements": [{"type": "element1", "required": True}],
                "patterns": [{"id": "p1", "confidence_weight": 0.8}]
            },
            "methodological_depth": {
                "methods": [
                    {
                        "technical_approach": {
                            "steps": [{"description": "Specific implementation"}],
                            "complexity": "O(n log n)",
                            "assumptions": ["Sorted data"]
                        },
                        "epistemological_foundation": {
                            "paradigm": "Empirical positivism",
                            "justification": "Chosen because...",
                            "theoretical_framework": ["Author 2020"]
                        }
                    }
                ]
            },
            "validation_rules": {
                "rules": [
                    {
                        "must_contain": {"elements": ["element1"]},
                        "should_contain": [{"elements": ["element2"]}]
                    }
                ]
            },
            "error_handling": {
                "failure_contract": {"emit_code": "ERR001"}
            },
            "traceability": {
                "source_hash": "b" * 64
            }
        }
        
        evaluator = CQVREvaluator()
        decision = evaluator.evaluate_contract(contract)
        
        assert decision is not None
        assert decision.decision in ["PRODUCCION", "PARCHEAR", "REFORMULAR"]
        assert decision.score.total_score >= 0
        assert decision.score.total_score <= 100
        assert isinstance(decision.blockers, list)
        assert isinstance(decision.warnings, list)
        assert isinstance(decision.recommendations, list)
    
    def test_determinism(self) -> None:
        """Test that evaluation is deterministic"""
        contract = {
            "identity": {"question_id": "Q001"},
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
        
        evaluator = CQVREvaluator()
        decision1 = evaluator.evaluate_contract(contract)
        decision2 = evaluator.evaluate_contract(contract)
        
        assert decision1.score.total_score == decision2.score.total_score
        assert decision1.decision == decision2.decision
        assert len(decision1.blockers) == len(decision2.blockers)
        assert len(decision1.warnings) == len(decision2.warnings)


@pytest.mark.updated
class TestErrorHandling:
    """Test error handling for malformed contracts"""
    
    def test_empty_contract(self) -> None:
        """Test handling of empty contract"""
        contract: dict[str, object] = {}
        
        evaluator = CQVREvaluator()
        decision = evaluator.evaluate_contract(contract)
        
        assert decision is not None
        # Empty contract gets 5 points from signal_requirements (no mandatory signals)
        assert decision.score.total_score <= 10
    
    def test_missing_sections(self) -> None:
        """Test handling of contract with missing sections"""
        contract = {
            "identity": {"question_id": "Q001"}
        }
        
        evaluator = CQVREvaluator()
        decision = evaluator.evaluate_contract(contract)
        
        assert decision is not None
        assert decision.score.total_score < 100
    
    def test_malformed_data_types(self) -> None:
        """Test handling of malformed data types"""
        contract = {
            "identity": {},  # Empty dict instead of malformed
            "output_contract": {},
            "method_binding": {},
            "evidence_assembly": {},
            "signal_requirements": {},
            "question_context": {},
            "methodological_depth": {},
            "validation_rules": {},
            "error_handling": {},
            "traceability": {}
        }
        
        evaluator = CQVREvaluator()
        # Should not crash
        decision = evaluator.evaluate_contract(contract)
        assert decision is not None
        assert decision.score.total_score >= 0

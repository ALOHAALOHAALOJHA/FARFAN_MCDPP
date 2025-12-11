"""
Tests for SISAS Strategic Data Irrigation Enhancements
=======================================================

Validates all 4 surgical enhancements for strategic data irrigation
from questionnaire JSON to Phase 2 nodes.

Test Coverage:
    - Enhancement #1: Method Execution Metadata
    - Enhancement #2: Structured Validation Specifications
    - Enhancement #3: Scoring Modality Context
    - Enhancement #4: Semantic Disambiguation Layer
    - Integration: SignalEnhancementIntegrator

Author: F.A.R.F.A.N Pipeline Team
Date: 2025-12-11
"""

import pytest

from cross_cutting_infrastrucuture.irrigation_using_signals.SISAS.signal_method_metadata import (
    MethodMetadata,
    MethodExecutionMetadata,
    extract_method_metadata,
    should_execute_method,
    get_adaptive_execution_plan,
)
from cross_cutting_infrastrucuture.irrigation_using_signals.SISAS.signal_validation_specs import (
    ValidationSpecifications,
    extract_validation_specifications,
)
from cross_cutting_infrastrucuture.irrigation_using_signals.SISAS.signal_scoring_context import (
    ScoringModalityDefinition,
    extract_scoring_context,
    create_default_scoring_context,
)
from cross_cutting_infrastrucuture.irrigation_using_signals.SISAS.signal_semantic_context import (
    SemanticContext,
    DisambiguationRule,
    extract_semantic_context,
    apply_semantic_disambiguation,
)


# ============================================================================
# ENHANCEMENT #1: METHOD EXECUTION METADATA
# ============================================================================

class TestMethodExecutionMetadata:
    """Tests for method execution metadata extraction."""
    
    def test_extract_method_metadata_basic(self):
        """Test basic method metadata extraction."""
        question_data = {
            "method_sets": [
                {
                    "class": "TextMiningEngine",
                    "function": "diagnose_critical_links",
                    "method_type": "analysis",
                    "priority": 1,
                    "description": "Critical link diagnosis"
                },
                {
                    "class": "BayesianNumericalAnalyzer",
                    "function": "analyze",
                    "method_type": "extraction",
                    "priority": 3,
                    "description": "Bayesian analysis"
                }
            ]
        }
        
        metadata = extract_method_metadata(question_data, "Q001")
        
        assert isinstance(metadata, MethodExecutionMetadata)
        assert len(metadata.methods) == 2
        assert metadata.methods[0].priority == 1
        assert metadata.methods[1].priority == 3
        assert metadata.type_distribution["analysis"] == 1
        assert metadata.type_distribution["extraction"] == 1
    
    def test_extract_method_metadata_priority_ordering(self):
        """Test that methods are ordered by priority."""
        question_data = {
            "method_sets": [
                {"class": "C", "function": "f", "method_type": "analysis", "priority": 5},
                {"class": "A", "function": "f", "method_type": "analysis", "priority": 1},
                {"class": "B", "function": "f", "method_type": "analysis", "priority": 3},
            ]
        }
        
        metadata = extract_method_metadata(question_data, "Q001")
        
        assert metadata.methods[0].class_name == "A"
        assert metadata.methods[1].class_name == "B"
        assert metadata.methods[2].class_name == "C"
    
    def test_extract_method_metadata_priority_groups(self):
        """Test priority grouping."""
        question_data = {
            "method_sets": [
                {"class": "A1", "function": "f", "method_type": "analysis", "priority": 1},
                {"class": "A2", "function": "f", "method_type": "analysis", "priority": 1},
                {"class": "B1", "function": "f", "method_type": "analysis", "priority": 2},
            ]
        }
        
        metadata = extract_method_metadata(question_data, "Q001")
        
        assert len(metadata.priority_groups[1]) == 2
        assert len(metadata.priority_groups[2]) == 1
    
    def test_should_execute_method_high_priority(self):
        """Test that high priority methods always execute."""
        method = MethodMetadata(
            class_name="Test",
            method_name="test",
            method_type="analysis",
            priority=1,
            description="Test"
        )
        
        assert should_execute_method(method, {}) is True
    
    def test_should_execute_method_adaptive(self):
        """Test adaptive execution logic."""
        # Validation method with low confidence
        validation_method = MethodMetadata(
            class_name="Validator",
            method_name="validate",
            method_type="validation",
            priority=5,
            description="Test"
        )
        
        context_low_confidence = {"current_confidence": 0.5}
        assert should_execute_method(validation_method, context_low_confidence) is True
        
        context_high_confidence = {"current_confidence": 0.9}
        assert should_execute_method(validation_method, context_high_confidence) is False
    
    def test_get_adaptive_execution_plan(self):
        """Test adaptive execution plan generation."""
        metadata = MethodExecutionMetadata(
            methods=(
                MethodMetadata("A", "f", "analysis", 1, ""),
                MethodMetadata("B", "f", "validation", 5, ""),
            ),
            priority_groups={1: (), 5: ()},
            type_distribution={"analysis": 1, "extraction": 0, "validation": 1, "scoring": 0},
            execution_order=()
        )
        
        context = {"current_confidence": 0.5}
        plan = get_adaptive_execution_plan(metadata, context)
        
        assert len(plan) == 2


# ============================================================================
# ENHANCEMENT #2: STRUCTURED VALIDATION SPECIFICATIONS
# ============================================================================

class TestValidationSpecifications:
    """Tests for structured validation specifications."""
    
    def test_extract_validation_specs_basic(self):
        """Test basic validation spec extraction."""
        question_data = {
            "validations": {
                "completeness_check": True,
                "buscar_indicadores_cuantitativos": {
                    "enabled": True,
                    "threshold": 0.7,
                    "severity": "HIGH"
                }
            }
        }
        
        specs = extract_validation_specifications(question_data, "Q001")
        
        assert isinstance(specs, ValidationSpecifications)
        assert "completeness_check" in specs.specs
        assert specs.specs["completeness_check"].enabled is True
        assert "buscar_indicadores_cuantitativos" in specs.specs
        assert specs.specs["buscar_indicadores_cuantitativos"].threshold == 0.7
    
    def test_validation_spec_required_marking(self):
        """Test that required validations are marked."""
        question_data = {
            "validations": {
                "completeness_check": True
            }
        }
        
        specs = extract_validation_specifications(question_data, "Q001")
        
        assert "completeness_check" in specs.required_validations
    
    def test_validate_evidence_basic(self):
        """Test evidence validation."""
        question_data = {
            "validations": {
                "completeness_check": {
                    "enabled": True,
                    "threshold": 0.8
                }
            }
        }
        
        specs = extract_validation_specifications(question_data, "Q001")
        
        # Evidence with high completeness
        evidence_pass = {
            "elements_found": ["a", "b", "c"],
            "expected_elements": ["a", "b", "c"]
        }
        
        result_pass = specs.validate_evidence(evidence_pass)
        assert result_pass.passed is True
        
        # Evidence with low completeness
        evidence_fail = {
            "elements_found": ["a"],
            "expected_elements": ["a", "b", "c"]
        }
        
        result_fail = specs.validate_evidence(evidence_fail)
        assert result_fail.passed is False


# ============================================================================
# ENHANCEMENT #3: SCORING MODALITY CONTEXT
# ============================================================================

class TestScoringContext:
    """Tests for scoring modality context."""
    
    def test_extract_scoring_context_basic(self):
        """Test basic scoring context extraction."""
        question_data = {
            "scoring_modality": "TYPE_A",
            "policy_area_id": "PA01",
            "dimension_id": "DIM01"
        }
        
        scoring_definitions = {
            "modality_definitions": {
                "TYPE_A": {
                    "description": "Weighted mean",
                    "threshold": 0.5,
                    "aggregation": "weighted_mean",
                    "weight_elements": 0.4,
                    "weight_similarity": 0.3,
                    "weight_patterns": 0.3
                }
            }
        }
        
        context = extract_scoring_context(question_data, scoring_definitions, "Q001")
        
        assert context is not None
        assert context.modality_definition.modality == "TYPE_A"
        assert context.modality_definition.threshold == 0.5
        assert context.policy_area_id == "PA01"
    
    def test_scoring_modality_compute_score(self):
        """Test score computation."""
        modality = ScoringModalityDefinition(
            modality="TYPE_A",
            description="Test",
            threshold=0.5,
            aggregation="weighted_mean",
            weight_elements=0.4,
            weight_similarity=0.3,
            weight_patterns=0.3,
            failure_code=None
        )
        
        score = modality.compute_score(
            elements_score=0.8,
            similarity_score=0.6,
            patterns_score=0.7
        )
        
        expected = (0.8 * 0.4 + 0.6 * 0.3 + 0.7 * 0.3)
        assert abs(score - expected) < 0.01
    
    def test_scoring_context_adaptive_threshold(self):
        """Test adaptive threshold adjustment."""
        context = create_default_scoring_context("Q001")
        
        # High complexity should lower threshold
        adjusted = context.adjust_threshold_for_context(
            document_complexity=0.8,
            evidence_quality=0.5
        )
        
        assert adjusted < context.modality_definition.threshold


# ============================================================================
# ENHANCEMENT #4: SEMANTIC DISAMBIGUATION
# ============================================================================

class TestSemanticDisambiguation:
    """Tests for semantic disambiguation layer."""
    
    def test_extract_semantic_context_basic(self):
        """Test semantic context extraction."""
        semantic_layers = {
            "disambiguation": {
                "confidence_threshold": 0.8,
                "entity_linker": {
                    "enabled": True,
                    "confidence_threshold": 0.7
                }
            },
            "embedding_strategy": {
                "model": "all-MiniLM-L6-v2",
                "dimension": 384,
                "hybrid": False,
                "strategy": "dense"
            }
        }
        
        context = extract_semantic_context(semantic_layers)
        
        assert isinstance(context, SemanticContext)
        assert context.entity_linking.enabled is True
        assert context.entity_linking.confidence_threshold == 0.7
        assert context.embedding_strategy.model == "all-MiniLM-L6-v2"
    
    def test_disambiguation_rule_basic(self):
        """Test disambiguation rule application."""
        rule = DisambiguationRule(
            term="víctima",
            contexts=("conflicto", "crimen"),
            primary_meaning="víctima del conflicto armado",
            alternate_meanings={"crimen": "víctima de crimen común"},
            requires_context=True
        )
        
        # With conflict context
        assert rule.disambiguate("en el conflicto armado") == "víctima del conflicto armado"
        
        # With crime context
        assert rule.disambiguate("crimen organizado") == "víctima de crimen común"
    
    def test_apply_semantic_disambiguation(self):
        """Test pattern disambiguation."""
        semantic_layers = {
            "disambiguation": {},
            "embedding_strategy": {"model": "test", "dimension": 384}
        }
        
        context = extract_semantic_context(semantic_layers)
        patterns = ["víctima", "territorio"]
        
        disambiguated = apply_semantic_disambiguation(
            patterns,
            context,
            "en el conflicto armado"
        )
        
        assert len(disambiguated) == 2


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
class TestEnhancementIntegration:
    """Integration tests for all enhancements together."""
    
    def test_all_enhancements_applied(self):
        """Test that all 4 enhancements can be applied to a question."""
        question_data = {
            "question_id": "Q001",
            "policy_area_id": "PA01",
            "dimension_id": "DIM01",
            "scoring_modality": "TYPE_A",
            "method_sets": [
                {
                    "class": "TextMiningEngine",
                    "function": "diagnose",
                    "method_type": "analysis",
                    "priority": 1
                }
            ],
            "validations": {
                "completeness_check": True
            },
            "patterns": ["víctima", "territorio"]
        }
        
        # Extract all enhancements
        method_metadata = extract_method_metadata(question_data, "Q001")
        assert len(method_metadata.methods) > 0
        
        validation_specs = extract_validation_specifications(question_data, "Q001")
        assert len(validation_specs.specs) > 0
    
    def test_scoring_context_with_mocked_definitions(self):
        """Test scoring context extraction with mocked definitions."""
        question_data = {
            "question_id": "Q001",
            "scoring_modality": "TYPE_A",
            "policy_area_id": "PA01",
            "dimension_id": "DIM01"
        }
        
        scoring_definitions = {
            "modality_definitions": {
                "TYPE_A": {
                    "description": "Weighted mean",
                    "threshold": 0.5,
                    "aggregation": "weighted_mean",
                    "weight_elements": 0.4,
                    "weight_similarity": 0.3,
                    "weight_patterns": 0.3,
                    "failure_code": "F-A-LOW"
                }
            }
        }
        
        context = extract_scoring_context(question_data, scoring_definitions, "Q001")
        assert context is not None
        assert context.modality_definition.modality == "TYPE_A"
    
    def test_semantic_context_with_mocked_layers(self):
        """Test semantic context extraction with mocked semantic layers."""
        semantic_layers = {
            "disambiguation": {
                "confidence_threshold": 0.8,
                "entity_linker": {
                    "enabled": True,
                    "confidence_threshold": 0.7,
                    "context_window": 200,
                    "fallback_strategy": "use_literal"
                }
            },
            "embedding_strategy": {
                "model": "all-MiniLM-L6-v2",
                "dimension": 384,
                "hybrid": False,
                "strategy": "dense"
            }
        }
        
        context = extract_semantic_context(semantic_layers)
        assert isinstance(context, SemanticContext)
        assert context.entity_linking.enabled is True
        assert len(context.disambiguation_rules) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

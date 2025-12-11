"""
Tests for CalibrationOrchestrator

Tests role-based layer activation, completeness validation, and fusion.
"""

import pytest
from orchestration.calibration_orchestrator import (
    CalibrationOrchestrator,
    CalibrationSubject,
    CalibrationResult,
    EvidenceStore,
    LayerID,
    LayerRequirementsResolver,
    ROLE_LAYER_REQUIREMENTS,
)


@pytest.fixture
def mock_configs():
    """Mock configuration data."""
    intrinsic_calibration = {
        "methods": {
            "test.method.ingest": {
                "role": "INGEST_PDM",
                "b_theory": 0.8,
                "b_impl": 0.7,
                "b_deploy": 0.9
            },
            "test.method.score": {
                "role": "SCORE_Q",
                "b_theory": 0.75,
                "b_impl": 0.85,
                "b_deploy": 0.8
            },
            "test.method.aggregate": {
                "role": "AGGREGATE",
                "b_theory": 0.9,
                "b_impl": 0.8,
                "b_deploy": 0.85
            }
        },
        "_base_weights": {
            "w_theory": 0.4,
            "w_impl": 0.35,
            "w_deploy": 0.25
        }
    }
    
    questionnaire_monolith = {
        "blocks": {
            "micro_questions": [
                {
                    "question_id": "Q001",
                    "dimension_id": "D1",
                    "policy_area_id": "PA1",
                    "method_sets": {
                        "analyzer": "test.method.score"
                    }
                }
            ],
            "dimensions": [
                {"dimension_id": "D1", "name": "Dimension 1"}
            ],
            "policy_areas": [
                {"policy_area_id": "PA1", "name": "Policy Area 1"}
            ]
        }
    }
    
    fusion_specification = {
        "role_fusion_parameters": {
            "INGEST_PDM": {
                "linear_weights": {
                    "@b": 0.4,
                    "@chain": 0.25,
                    "@u": 0.2,
                    "@m": 0.15
                },
                "interaction_weights": {}
            },
            "SCORE_Q": {
                "linear_weights": {
                    "@b": 0.17,
                    "@chain": 0.13,
                    "@q": 0.08,
                    "@d": 0.07,
                    "@p": 0.06,
                    "@C": 0.08,
                    "@u": 0.04,
                    "@m": 0.04
                },
                "interaction_weights": {
                    "@u,@chain": 0.13,
                    "@chain,@C": 0.10,
                    "@q,@d": 0.10
                }
            },
            "AGGREGATE": {
                "linear_weights": {
                    "@b": 0.25,
                    "@chain": 0.20,
                    "@d": 0.15,
                    "@p": 0.15,
                    "@C": 0.15,
                    "@m": 0.10
                },
                "interaction_weights": {}
            }
        }
    }
    
    method_compatibility = {
        "methods": {
            "test.method.ingest": {"chain_compatibility_score": 0.85},
            "test.method.score": {"chain_compatibility_score": 0.90},
            "test.method.aggregate": {"chain_compatibility_score": 0.88}
        }
    }
    
    canonical_method_catalog = {
        "methods": {
            "test.method.ingest": {"governance_quality": 0.8},
            "test.method.score": {"governance_quality": 0.85},
            "test.method.aggregate": {"governance_quality": 0.9}
        }
    }
    
    return {
        "intrinsic_calibration": intrinsic_calibration,
        "questionnaire_monolith": questionnaire_monolith,
        "fusion_specification": fusion_specification,
        "method_compatibility": method_compatibility,
        "canonical_method_catalog": canonical_method_catalog
    }


@pytest.fixture
def orchestrator(mock_configs):
    """Create orchestrator with mock configs."""
    return CalibrationOrchestrator(
        intrinsic_calibration=mock_configs["intrinsic_calibration"],
        questionnaire_monolith=mock_configs["questionnaire_monolith"],
        fusion_specification=mock_configs["fusion_specification"],
        method_compatibility=mock_configs["method_compatibility"],
        canonical_method_catalog=mock_configs["canonical_method_catalog"]
    )


@pytest.fixture
def evidence_store():
    """Mock evidence store."""
    return EvidenceStore(
        pdt_structure={
            "chunk_count": 60,
            "completeness": 0.85,
            "structure_quality": 0.9
        },
        document_quality=0.85,
        question_id="Q001",
        dimension_id="D1",
        policy_area_id="PA1"
    )


def test_layer_requirements_resolver(mock_configs):
    """Test LayerRequirementsResolver determines correct layers by role."""
    resolver = LayerRequirementsResolver(
        mock_configs["intrinsic_calibration"],
        mock_configs["method_compatibility"]
    )
    
    ingest_layers = resolver.get_required_layers("test.method.ingest")
    assert ingest_layers == {LayerID.BASE, LayerID.CHAIN, LayerID.UNIT, LayerID.META}
    
    score_layers = resolver.get_required_layers("test.method.score")
    assert score_layers == {
        LayerID.BASE, LayerID.CHAIN, LayerID.QUESTION, LayerID.DIMENSION,
        LayerID.POLICY, LayerID.CONGRUENCE, LayerID.UNIT, LayerID.META
    }
    
    aggregate_layers = resolver.get_required_layers("test.method.aggregate")
    assert aggregate_layers == {
        LayerID.BASE, LayerID.CHAIN, LayerID.DIMENSION,
        LayerID.POLICY, LayerID.CONGRUENCE, LayerID.META
    }


def test_role_layer_requirements_definitions():
    """Test role layer requirements are correctly defined."""
    assert "INGEST_PDM" in ROLE_LAYER_REQUIREMENTS
    assert "SCORE_Q" in ROLE_LAYER_REQUIREMENTS
    assert "AGGREGATE" in ROLE_LAYER_REQUIREMENTS
    assert "REPORT" in ROLE_LAYER_REQUIREMENTS
    assert "META_TOOL" in ROLE_LAYER_REQUIREMENTS
    assert "TRANSFORM" in ROLE_LAYER_REQUIREMENTS
    
    ingest_layers = ROLE_LAYER_REQUIREMENTS["INGEST_PDM"]
    assert LayerID.BASE in ingest_layers
    assert LayerID.CHAIN in ingest_layers
    assert LayerID.UNIT in ingest_layers
    assert LayerID.META in ingest_layers
    assert len(ingest_layers) == 4
    
    score_layers = ROLE_LAYER_REQUIREMENTS["SCORE_Q"]
    assert len(score_layers) == 8


def test_calibrate_ingest_method(orchestrator, evidence_store):
    """Test calibration of INGEST_PDM role method."""
    subject = CalibrationSubject(
        method_id="test.method.ingest",
        role="INGEST_PDM",
        context={"phase": "ingestion"}
    )
    
    result = orchestrator.calibrate(subject, evidence_store)
    
    assert isinstance(result, CalibrationResult)
    assert result.role == "INGEST_PDM"
    assert result.method_id == "test.method.ingest"
    assert 0.0 <= result.final_score <= 1.0
    
    assert LayerID.BASE in result.layer_scores
    assert LayerID.CHAIN in result.layer_scores
    assert LayerID.UNIT in result.layer_scores
    assert LayerID.META in result.layer_scores
    
    assert len(result.active_layers) == 4
    assert result.active_layers == {
        LayerID.BASE, LayerID.CHAIN, LayerID.UNIT, LayerID.META
    }


def test_calibrate_score_method(orchestrator, evidence_store):
    """Test calibration of SCORE_Q role method."""
    subject = CalibrationSubject(
        method_id="test.method.score",
        role="SCORE_Q",
        context={"phase": "scoring", "question_id": "Q001"}
    )
    
    result = orchestrator.calibrate(subject, evidence_store)
    
    assert isinstance(result, CalibrationResult)
    assert result.role == "SCORE_Q"
    assert 0.0 <= result.final_score <= 1.0
    
    assert len(result.active_layers) == 8
    assert LayerID.BASE in result.layer_scores
    assert LayerID.CHAIN in result.layer_scores
    assert LayerID.QUESTION in result.layer_scores
    assert LayerID.DIMENSION in result.layer_scores
    assert LayerID.POLICY in result.layer_scores
    assert LayerID.CONGRUENCE in result.layer_scores
    assert LayerID.UNIT in result.layer_scores
    assert LayerID.META in result.layer_scores


def test_calibrate_aggregate_method(orchestrator, evidence_store):
    """Test calibration of AGGREGATE role method."""
    subject = CalibrationSubject(
        method_id="test.method.aggregate",
        role="AGGREGATE",
        context={"phase": "aggregation"}
    )
    
    result = orchestrator.calibrate(subject, evidence_store)
    
    assert isinstance(result, CalibrationResult)
    assert result.role == "AGGREGATE"
    assert 0.0 <= result.final_score <= 1.0
    
    assert len(result.active_layers) == 6
    assert LayerID.BASE in result.layer_scores
    assert LayerID.CHAIN in result.layer_scores
    assert LayerID.DIMENSION in result.layer_scores
    assert LayerID.POLICY in result.layer_scores
    assert LayerID.CONGRUENCE in result.layer_scores
    assert LayerID.META in result.layer_scores
    
    assert LayerID.QUESTION not in result.layer_scores
    assert LayerID.UNIT not in result.layer_scores


def test_base_evaluator(orchestrator):
    """Test base layer evaluator computes scores correctly."""
    score = orchestrator.base_evaluator.evaluate("test.method.ingest")
    
    expected = 0.4 * 0.8 + 0.35 * 0.7 + 0.25 * 0.9
    assert abs(score - expected) < 0.001
    assert 0.0 <= score <= 1.0


def test_chain_evaluator(orchestrator):
    """Test chain layer evaluator."""
    score = orchestrator.chain_evaluator.evaluate("test.method.ingest")
    assert score == 0.85
    assert 0.0 <= score <= 1.0


def test_unit_evaluator(orchestrator):
    """Test unit layer evaluator uses PDT structure."""
    pdt_structure = {
        "chunk_count": 60,
        "completeness": 0.85,
        "structure_quality": 0.9
    }
    
    score = orchestrator.unit_evaluator.evaluate(pdt_structure)
    assert 0.0 <= score <= 1.0
    assert score > 0.5


def test_question_evaluator(orchestrator):
    """Test question layer evaluator."""
    score = orchestrator.question_evaluator.evaluate("test.method.score", "Q001")
    assert 0.0 <= score <= 1.0


def test_dimension_evaluator(orchestrator):
    """Test dimension layer evaluator."""
    score = orchestrator.dimension_evaluator.evaluate("test.method.score", "D1")
    assert score == 0.85
    assert 0.0 <= score <= 1.0


def test_policy_evaluator(orchestrator):
    """Test policy layer evaluator."""
    score = orchestrator.policy_evaluator.evaluate("test.method.score", "PA1")
    assert score == 0.85
    assert 0.0 <= score <= 1.0


def test_congruence_evaluator(orchestrator):
    """Test congruence layer evaluator."""
    score = orchestrator.congruence_evaluator.evaluate("test.method.score")
    assert 0.0 <= score <= 1.0


def test_meta_evaluator(orchestrator):
    """Test meta layer evaluator."""
    score = orchestrator.meta_evaluator.evaluate("test.method.ingest")
    assert score == 0.8
    assert 0.0 <= score <= 1.0


def test_choquet_aggregator(orchestrator):
    """Test Choquet aggregator fuses layers correctly."""
    subject = CalibrationSubject(
        method_id="test.method.ingest",
        role="INGEST_PDM",
        context={}
    )
    
    layer_scores = {
        LayerID.BASE: 0.8,
        LayerID.CHAIN: 0.7,
        LayerID.UNIT: 0.9,
        LayerID.META: 0.75
    }
    
    final = orchestrator.choquet_aggregator.aggregate(subject, layer_scores)
    assert 0.0 <= final <= 1.0


def test_completeness_validation_passes(orchestrator, evidence_store):
    """Test completeness validation passes when all layers computed."""
    subject = CalibrationSubject(
        method_id="test.method.ingest",
        role="INGEST_PDM",
        context={}
    )
    
    result = orchestrator.calibrate(subject, evidence_store)
    assert result.final_score >= 0.0


def test_completeness_validation_fails_missing_layers(orchestrator):
    """Test completeness validation fails when required layer missing."""
    required = {LayerID.BASE, LayerID.CHAIN, LayerID.UNIT}
    computed = {LayerID.BASE: 0.8, LayerID.CHAIN: 0.7}
    
    with pytest.raises(ValueError, match="missing layers"):
        orchestrator._validate_completeness(
            required, computed, "test.method", "TEST_ROLE"
        )


def test_calibration_result_validation():
    """Test CalibrationResult validates final score bounds."""
    with pytest.raises(ValueError, match="not in \\[0,1\\]"):
        CalibrationResult(
            final_score=1.5,
            layer_scores={},
            active_layers=set(),
            role="TEST",
            method_id="test"
        )
    
    with pytest.raises(ValueError, match="not in \\[0,1\\]"):
        CalibrationResult(
            final_score=-0.1,
            layer_scores={},
            active_layers=set(),
            role="TEST",
            method_id="test"
        )


def test_unknown_role_defaults_to_score_q(mock_configs):
    """Test unknown role defaults to SCORE_Q layers."""
    resolver = LayerRequirementsResolver(
        mock_configs["intrinsic_calibration"],
        mock_configs["method_compatibility"]
    )
    
    layers = resolver.get_required_layers("unknown.method")
    assert layers == ROLE_LAYER_REQUIREMENTS["SCORE_Q"]


def test_all_roles_have_base_and_chain():
    """Test all roles require BASE and CHAIN layers."""
    for role, layers in ROLE_LAYER_REQUIREMENTS.items():
        assert LayerID.BASE in layers, f"{role} missing BASE"
        assert LayerID.CHAIN in layers, f"{role} missing CHAIN"


def test_score_q_role_has_all_layers():
    """Test SCORE_Q role has all 8 layers."""
    layers = ROLE_LAYER_REQUIREMENTS["SCORE_Q"]
    assert len(layers) == 8
    assert LayerID.BASE in layers
    assert LayerID.CHAIN in layers
    assert LayerID.UNIT in layers
    assert LayerID.QUESTION in layers
    assert LayerID.DIMENSION in layers
    assert LayerID.POLICY in layers
    assert LayerID.CONGRUENCE in layers
    assert LayerID.META in layers


def test_metadata_in_result(orchestrator, evidence_store):
    """Test metadata is populated in calibration result."""
    subject = CalibrationSubject(
        method_id="test.method.score",
        role="SCORE_Q",
        context={"phase": "scoring", "custom_key": "custom_value"}
    )
    
    result = orchestrator.calibrate(subject, evidence_store)
    
    assert "context" in result.metadata
    assert result.metadata["context"]["custom_key"] == "custom_value"
    assert "evidence_keys" in result.metadata
    assert "layer_count" in result.metadata
    assert result.metadata["layer_count"] == 8

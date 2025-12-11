"""
COHORT_2024 - REFACTOR_WAVE_2024_12
Created: 2024-12-15T00:00:00+00:00

SENSITIVE - CALIBRATION SYSTEM CRITICAL

Test Suite for CalibrationOrchestrator

Validates:
- Layer requirement determination via role mapping
- Active layer score computation (base, contextual, unit, meta)
- Choquet fusion with interaction terms
- Boundedness validation [0.0-1.0]
- Certificate metadata generation
"""

from __future__ import annotations

import pytest

from cross_cutting_infrastrucuture.capaz_calibration_parmetrization import (
    CalibrationContext,
    CalibrationEvidence,
    CalibrationOrchestrator,
)


@pytest.fixture
def orchestrator():
    return CalibrationOrchestrator()


class TestLayerRequirements:
    def test_executor_requires_all_8_layers(self, orchestrator):
        result = orchestrator.calibrate(
            method_id="farfan_pipeline.core.executors.D1_Q1_Executor"
        )
        assert len(result["active_layers"]) == 8
        expected_layers = ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"]
        assert set(result["active_layers"]) == set(expected_layers)
    
    def test_ingest_requires_4_layers(self, orchestrator):
        result = orchestrator.calibrate(
            method_id="farfan_pipeline.processing.ingest.PDTParser"
        )
        assert len(result["active_layers"]) == 4
        expected_layers = ["@b", "@chain", "@u", "@m"]
        assert set(result["active_layers"]) == set(expected_layers)
    
    def test_utility_requires_3_layers(self, orchestrator):
        result = orchestrator.calibrate(
            method_id="farfan_pipeline.utils.StringNormalizer"
        )
        assert len(result["active_layers"]) == 3
        expected_layers = ["@b", "@chain", "@m"]
        assert set(result["active_layers"]) == set(expected_layers)
    
    def test_role_detection_from_method_id(self, orchestrator):
        test_cases = [
            ("farfan_pipeline.core.executors.D1_Q1", "executor"),
            ("farfan_pipeline.processing.ingest.Parser", "ingest"),
            ("farfan_pipeline.utils.Helper", "utility"),
            ("farfan_pipeline.orchestration.Controller", "orchestrator"),
            ("farfan_pipeline.analyzers.Analyzer", "analyzer"),
        ]
        
        for method_id, expected_role in test_cases:
            result = orchestrator.calibrate(method_id=method_id)
            assert result["role"] == expected_role


class TestLayerScoreComputation:
    def test_base_layer_from_intrinsic_scores(self, orchestrator):
        result = orchestrator.calibrate(
            method_id="test.method",
            evidence=CalibrationEvidence(
                intrinsic_scores={"base_layer_score": 0.85}
            ),
        )
        assert result["layer_scores"]["b"] == 0.85
    
    def test_base_layer_from_components(self, orchestrator):
        result = orchestrator.calibrate(
            method_id="test.method",
            evidence=CalibrationEvidence(
                intrinsic_scores={
                    "b_theory": 0.9,
                    "b_impl": 0.8,
                    "b_deploy": 0.7,
                }
            ),
        )
        expected = 0.40 * 0.9 + 0.35 * 0.8 + 0.25 * 0.7
        assert abs(result["layer_scores"]["b"] - expected) < 1e-6
    
    def test_contextual_layers_from_compatibility(self, orchestrator):
        result = orchestrator.calibrate(
            method_id="test.method",
            context=CalibrationContext(
                question_id="Q001",
                dimension_id="DIM01",
                policy_area_id="PA01",
            ),
            evidence=CalibrationEvidence(
                compatibility_registry={
                    "method": {
                        "questions": {"Q001": 0.95},
                        "dimensions": {"DIM01": 0.88},
                        "policies": {"PA01": 0.92},
                    }
                }
            ),
        )
        
        assert result["layer_scores"]["q"] == 0.95
        assert result["layer_scores"]["d"] == 0.88
        assert result["layer_scores"]["p"] == 0.92
    
    def test_unit_layer_from_pdt_structure(self, orchestrator):
        result = orchestrator.calibrate(
            method_id="test.ingest.method",
            evidence=CalibrationEvidence(
                pdt_structure={
                    "total_tokens": 12000,
                    "blocks_found": {
                        "Diagnóstico": {},
                        "Estratégica": {},
                        "PPI": {},
                        "Seguimiento": {},
                    },
                    "indicator_matrix_present": True,
                    "ppi_matrix_present": True,
                }
            ),
        )
        
        u_score = result["layer_scores"]["u"]
        assert 0.0 <= u_score <= 1.0
        assert u_score > 0.7
    
    def test_meta_layer_from_governance_artifacts(self, orchestrator):
        result = orchestrator.calibrate(
            method_id="test.method",
            evidence=CalibrationEvidence(
                governance_artifacts={
                    "version_tag": "COHORT_2024_v1.2.3",
                    "config_hash": "a" * 64,
                    "signature": "b" * 64,
                }
            ),
        )
        
        m_score = result["layer_scores"]["m"]
        assert m_score == 1.0


class TestChoquetFusion:
    def test_fusion_produces_valid_score(self, orchestrator):
        result = orchestrator.calibrate(
            method_id="test.executor.method",
            evidence=CalibrationEvidence(
                intrinsic_scores={"base_layer_score": 0.8}
            ),
        )
        
        assert 0.0 <= result["final_score"] <= 1.0
    
    def test_fusion_breakdown_structure(self, orchestrator):
        result = orchestrator.calibrate(method_id="test.method")
        
        fusion = result["fusion_breakdown"]
        assert "final_score" in fusion
        assert "linear_sum" in fusion
        assert "interaction_sum" in fusion
        assert "linear_contributions" in fusion
        assert "interaction_contributions" in fusion
    
    def test_fusion_sum_equals_final_score(self, orchestrator):
        result = orchestrator.calibrate(
            method_id="test.method",
            evidence=CalibrationEvidence(
                intrinsic_scores={"base_layer_score": 0.75}
            ),
        )
        
        fusion = result["fusion_breakdown"]
        computed_sum = fusion["linear_sum"] + fusion["interaction_sum"]
        
        assert abs(computed_sum - result["final_score"]) < 1e-6
    
    def test_linear_contributions_match_active_layers(self, orchestrator):
        result = orchestrator.calibrate(method_id="test.utility.method")
        
        fusion = result["fusion_breakdown"]
        linear_contribs = fusion["linear_contributions"]
        
        for layer in result["active_layers"]:
            assert layer in linear_contribs
    
    def test_interaction_terms_only_for_active_layers(self, orchestrator):
        result = orchestrator.calibrate(method_id="test.executor.method")
        
        fusion = result["fusion_breakdown"]
        interaction_contribs = fusion["interaction_contributions"]
        
        active_layers_set = set(result["active_layers"])
        
        for pair_str in interaction_contribs.keys():
            pair_str_clean = pair_str.strip("()")
            layers = pair_str_clean.split(",")
            for layer in layers:
                assert layer in active_layers_set


class TestBoundednessValidation:
    def test_score_within_bounds_is_valid(self, orchestrator):
        result = orchestrator.calibrate(
            method_id="test.method",
            evidence=CalibrationEvidence(
                intrinsic_scores={"base_layer_score": 0.75}
            ),
        )
        
        validation = result["validation"]
        assert validation["is_bounded"] is True
        assert 0.0 <= result["final_score"] <= 1.0
    
    def test_validation_reports_bounds(self, orchestrator):
        result = orchestrator.calibrate(method_id="test.method")
        
        validation = result["validation"]
        assert validation["lower_bound"] == 0.0
        assert validation["upper_bound"] == 1.0
    
    def test_clamped_score_available(self, orchestrator):
        result = orchestrator.calibrate(method_id="test.method")
        
        validation = result["validation"]
        assert "clamped_score" in validation
        assert 0.0 <= validation["clamped_score"] <= 1.0


class TestCertificateMetadata:
    def test_certificate_has_required_fields(self, orchestrator):
        result = orchestrator.calibrate(method_id="test.method")
        
        cert = result["certificate_metadata"]
        required_fields = [
            "certificate_id",
            "certificate_hash",
            "timestamp",
            "cohort_id",
            "wave_version",
            "implementation_wave",
            "authority",
            "spec_compliance",
            "fusion_formula",
        ]
        
        for field in required_fields:
            assert field in cert
    
    def test_certificate_id_is_hash_prefix(self, orchestrator):
        result = orchestrator.calibrate(method_id="test.method")
        
        cert = result["certificate_metadata"]
        assert len(cert["certificate_id"]) == 16
        assert cert["certificate_hash"].startswith(cert["certificate_id"])
    
    def test_certificate_cohort_metadata(self, orchestrator):
        result = orchestrator.calibrate(method_id="test.method")
        
        cert = result["certificate_metadata"]
        assert cert["cohort_id"] == "COHORT_2024"
        assert cert["wave_version"] == "REFACTOR_WAVE_2024_12"
        assert cert["authority"] == "Doctrina SIN_CARRETA"
    
    def test_certificate_includes_fusion_formula(self, orchestrator):
        result = orchestrator.calibrate(method_id="test.method")
        
        cert = result["certificate_metadata"]
        assert "Cal(I)" in cert["fusion_formula"]
        assert "Σ" in cert["fusion_formula"]


class TestCalibrationResult:
    def test_result_has_required_fields(self, orchestrator):
        result = orchestrator.calibrate(method_id="test.method")
        
        required_fields = [
            "method_id",
            "role",
            "final_score",
            "layer_scores",
            "active_layers",
            "fusion_breakdown",
            "certificate_metadata",
            "validation",
        ]
        
        for field in required_fields:
            assert field in result
    
    def test_result_method_id_matches_input(self, orchestrator):
        method_id = "test.specific.method.identifier"
        result = orchestrator.calibrate(method_id=method_id)
        
        assert result["method_id"] == method_id
    
    def test_result_layer_scores_only_active_layers(self, orchestrator):
        result = orchestrator.calibrate(method_id="test.utility.method")
        
        active_layer_keys = [layer.lstrip("@") for layer in result["active_layers"]]
        
        for layer_key in result["layer_scores"].keys():
            assert layer_key in active_layer_keys


class TestIntegrationScenarios:
    def test_full_executor_calibration_workflow(self, orchestrator):
        result = orchestrator.calibrate(
            method_id="farfan_pipeline.core.executors.D1_Q1_EquityAnalyzer",
            context=CalibrationContext(
                question_id="Q001",
                dimension_id="DIM01",
                policy_area_id="PA01",
            ),
            evidence=CalibrationEvidence(
                intrinsic_scores={
                    "b_theory": 0.92,
                    "b_impl": 0.88,
                    "b_deploy": 0.85,
                    "chain_layer_score": 0.80,
                    "contract_layer_score": 0.95,
                },
                pdt_structure={
                    "total_tokens": 15000,
                    "blocks_found": {"Diagnóstico": {}, "Estratégica": {}, "PPI": {}, "Seguimiento": {}},
                    "indicator_matrix_present": True,
                    "ppi_matrix_present": True,
                },
                governance_artifacts={
                    "version_tag": "COHORT_2024_v1.2.3",
                    "config_hash": "a" * 64,
                    "signature": "b" * 64,
                },
            ),
        )
        
        assert result["role"] == "executor"
        assert len(result["active_layers"]) == 8
        assert 0.0 <= result["final_score"] <= 1.0
        assert result["validation"]["is_bounded"] is True
        assert len(result["certificate_metadata"]["certificate_id"]) == 16
    
    def test_minimal_calibration_uses_defaults(self, orchestrator):
        result = orchestrator.calibrate(method_id="test.unknown.method")
        
        assert result["role"] == "core"
        assert result["final_score"] > 0.0
        assert result["validation"]["is_bounded"] is True
    
    def test_multiple_methods_produce_different_certificates(self, orchestrator):
        result1 = orchestrator.calibrate(method_id="test.method.one")
        result2 = orchestrator.calibrate(method_id="test.method.two")
        
        cert1 = result1["certificate_metadata"]["certificate_hash"]
        cert2 = result2["certificate_metadata"]["certificate_hash"]
        
        assert cert1 != cert2

"""
Tests for calibration validators

Comprehensive test suite for CalibrationValidator class covering:
- Layer completeness validation
- Fusion weight normalization and non-negativity
- Anti-universality constraints
- Intrinsic calibration schema validation
- Score boundedness
- Config file validation
"""

import pytest

from cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration_validator import (
    CalibrationValidator,
    validate_all_pillars
)


class TestLayerCompletenessValidation:
    """Test validate_layer_completeness()"""
    
    def test_valid_score_q_complete_layers(self):
        validator = CalibrationValidator()
        
        method_config = {
            "active_layers": ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"]
        }
        
        is_valid, errors = validator.validate_layer_completeness(method_config, "SCORE_Q")
        
        assert is_valid
        assert len(errors) == 0
    
    def test_missing_layers_no_justification(self):
        validator = CalibrationValidator()
        
        method_config = {
            "active_layers": ["@b", "@chain", "@u"]
        }
        
        is_valid, errors = validator.validate_layer_completeness(method_config, "SCORE_Q")
        
        assert not is_valid
        assert len(errors) == 1
        assert "missing layers" in errors[0].lower()
        assert "without justifications" in errors[0].lower()
    
    def test_missing_layers_with_approved_justification(self):
        validator = CalibrationValidator()
        
        method_config = {
            "active_layers": ["@b", "@chain", "@u", "@m"],
            "justifications": {
                "@q": {"approved": True, "reason": "Not question-specific"},
                "@d": {"approved": True, "reason": "Not dimension-specific"},
                "@p": {"approved": True, "reason": "Not policy-specific"},
                "@C": {"approved": True, "reason": "No congruence analysis"}
            }
        }
        
        is_valid, errors = validator.validate_layer_completeness(method_config, "SCORE_Q")
        
        assert is_valid
        assert len(errors) == 0
    
    def test_missing_layers_with_unapproved_justification(self):
        validator = CalibrationValidator()
        
        method_config = {
            "active_layers": ["@b", "@chain", "@u", "@m"],
            "justifications": {
                "@q": {"approved": False, "reason": "Pending review"}
            }
        }
        
        is_valid, errors = validator.validate_layer_completeness(method_config, "SCORE_Q")
        
        assert not is_valid
        assert any("not approved" in e for e in errors)
    
    def test_unknown_role(self):
        validator = CalibrationValidator()
        
        method_config = {
            "active_layers": ["@b"]
        }
        
        is_valid, errors = validator.validate_layer_completeness(method_config, "UNKNOWN_ROLE")
        
        assert not is_valid
        assert "unknown role" in errors[0].lower()
    
    def test_valid_ingest_pdm_minimal_layers(self):
        validator = CalibrationValidator()
        
        method_config = {
            "active_layers": ["@b", "@chain", "@u", "@m"]
        }
        
        is_valid, errors = validator.validate_layer_completeness(method_config, "INGEST_PDM")
        
        assert is_valid
        assert len(errors) == 0


class TestFusionWeightsValidation:
    """Test validate_fusion_weights()"""
    
    def test_valid_weights_normalized(self):
        validator = CalibrationValidator()
        
        fusion_config = {
            "linear_weights": {
                "@b": 0.18,
                "@chain": 0.14,
                "@q": 0.09
            },
            "interaction_weights": {
                "(@u, @chain)": 0.15,
                "(@chain, @C)": 0.44
            }
        }
        
        is_valid, errors = validator.validate_fusion_weights(fusion_config, "SCORE_Q")
        
        assert is_valid
        assert len(errors) == 0
    
    def test_negative_linear_weight(self):
        validator = CalibrationValidator()
        
        fusion_config = {
            "linear_weights": {
                "@b": -0.1,
                "@chain": 0.6
            },
            "interaction_weights": {
                "(@u, @chain)": 0.5
            }
        }
        
        is_valid, errors = validator.validate_fusion_weights(fusion_config, "TEST_ROLE")
        
        assert not is_valid
        assert any("negative linear weight" in e.lower() for e in errors)
    
    def test_negative_interaction_weight(self):
        validator = CalibrationValidator()
        
        fusion_config = {
            "linear_weights": {
                "@b": 0.5
            },
            "interaction_weights": {
                "(@u, @chain)": -0.2,
                "(@b, @u)": 0.7
            }
        }
        
        is_valid, errors = validator.validate_fusion_weights(fusion_config, "TEST_ROLE")
        
        assert not is_valid
        assert any("negative interaction weight" in e.lower() for e in errors)
    
    def test_weights_not_normalized(self):
        validator = CalibrationValidator()
        
        fusion_config = {
            "linear_weights": {
                "@b": 0.3,
                "@chain": 0.3
            },
            "interaction_weights": {
                "(@u, @chain)": 0.3
            }
        }
        
        is_valid, errors = validator.validate_fusion_weights(fusion_config, "TEST_ROLE")
        
        assert not is_valid
        assert any("sum to" in e.lower() for e in errors)
    
    def test_weights_sum_within_epsilon(self):
        validator = CalibrationValidator()
        
        fusion_config = {
            "linear_weights": {
                "@b": 0.333333333,
                "@chain": 0.333333333
            },
            "interaction_weights": {
                "(@u, @chain)": 0.333333334
            }
        }
        
        is_valid, errors = validator.validate_fusion_weights(fusion_config, "TEST_ROLE")
        
        assert is_valid
        assert len(errors) == 0
    
    def test_empty_weights(self):
        validator = CalibrationValidator()
        
        fusion_config = {
            "linear_weights": {},
            "interaction_weights": {}
        }
        
        is_valid, errors = validator.validate_fusion_weights(fusion_config, "TEST_ROLE")
        
        assert not is_valid
        assert any("sum to 0" in e.lower() for e in errors)


class TestAntiUniversalityValidation:
    """Test validate_anti_universality()"""
    
    def test_valid_non_universal_method(self):
        validator = CalibrationValidator()
        
        method_compat = {
            "questions": {"Q001": 1.0, "Q002": 0.5, "Q003": 0.3},
            "dimensions": {"DIM01": 0.9, "DIM02": 0.2},
            "policies": {"PA01": 0.8, "PA02": 0.1}
        }
        
        is_valid, errors = validator.validate_anti_universality(method_compat, "method_123")
        
        assert is_valid
        assert len(errors) == 0
    
    def test_universal_method_violation(self):
        validator = CalibrationValidator()
        
        method_compat = {
            "questions": {"Q001": 1.0, "Q002": 0.95, "Q003": 0.92},
            "dimensions": {"DIM01": 0.98, "DIM02": 0.91},
            "policies": {"PA01": 0.96, "PA02": 0.90}
        }
        
        is_valid, errors = validator.validate_anti_universality(method_compat, "method_universal")
        
        assert not is_valid
        assert any("anti-universality violation" in e.lower() for e in errors)
    
    def test_missing_compatibility_data(self):
        validator = CalibrationValidator()
        
        method_compat = {
            "questions": {"Q001": 1.0},
            "dimensions": {}
        }
        
        is_valid, errors = validator.validate_anti_universality(method_compat, "method_incomplete")
        
        assert not is_valid
        assert any("incomplete compatibility scores" in e.lower() for e in errors)
    
    def test_edge_case_exactly_threshold(self):
        validator = CalibrationValidator()
        
        method_compat = {
            "questions": {"Q001": 0.9, "Q002": 0.9},
            "dimensions": {"DIM01": 0.9, "DIM02": 0.91},
            "policies": {"PA01": 0.9, "PA02": 0.95}
        }
        
        is_valid, errors = validator.validate_anti_universality(method_compat, "method_edge")
        
        assert not is_valid
        assert any("0.900 >= 0.9" in e for e in errors)
    
    def test_below_threshold(self):
        validator = CalibrationValidator()
        
        method_compat = {
            "questions": {"Q001": 0.899, "Q002": 1.0},
            "dimensions": {"DIM01": 0.95, "DIM02": 1.0},
            "policies": {"PA01": 0.99, "PA02": 1.0}
        }
        
        is_valid, errors = validator.validate_anti_universality(method_compat, "method_ok")
        
        assert is_valid
        assert len(errors) == 0


class TestIntrinsicCalibrationValidation:
    """Test validate_intrinsic_calibration()"""
    
    def test_valid_complete_calibration(self):
        validator = CalibrationValidator()
        
        calibration = {
            "b_theory": 0.85,
            "b_impl": 0.72,
            "b_deploy": 0.68,
            "status": "computed"
        }
        
        is_valid, errors = validator.validate_intrinsic_calibration(calibration, "method_valid")
        
        assert is_valid
        assert len(errors) == 0
    
    def test_missing_required_keys(self):
        validator = CalibrationValidator()
        
        calibration = {
            "b_theory": 0.85,
            "status": "computed"
        }
        
        is_valid, errors = validator.validate_intrinsic_calibration(calibration, "method_incomplete")
        
        assert not is_valid
        assert any("missing required keys" in e.lower() for e in errors)
    
    def test_scores_out_of_bounds_high(self):
        validator = CalibrationValidator()
        
        calibration = {
            "b_theory": 1.5,
            "b_impl": 0.72,
            "b_deploy": 0.68,
            "status": "computed"
        }
        
        is_valid, errors = validator.validate_intrinsic_calibration(calibration, "method_high")
        
        assert not is_valid
        assert any("out of bounds" in e.lower() for e in errors)
    
    def test_scores_out_of_bounds_low(self):
        validator = CalibrationValidator()
        
        calibration = {
            "b_theory": 0.85,
            "b_impl": -0.1,
            "b_deploy": 0.68,
            "status": "computed"
        }
        
        is_valid, errors = validator.validate_intrinsic_calibration(calibration, "method_low")
        
        assert not is_valid
        assert any("out of bounds" in e.lower() for e in errors)
    
    def test_invalid_status(self):
        validator = CalibrationValidator()
        
        calibration = {
            "b_theory": 0.85,
            "b_impl": 0.72,
            "b_deploy": 0.68,
            "status": "invalid_status"
        }
        
        is_valid, errors = validator.validate_intrinsic_calibration(calibration, "method_bad_status")
        
        assert not is_valid
        assert any("invalid status" in e.lower() for e in errors)
    
    def test_valid_statuses(self):
        validator = CalibrationValidator()
        
        for status in ["computed", "pending", "excluded", "none"]:
            calibration = {
                "b_theory": 0.85,
                "b_impl": 0.72,
                "b_deploy": 0.68,
                "status": status
            }
            
            is_valid, errors = validator.validate_intrinsic_calibration(calibration, f"method_{status}")
            
            assert is_valid, f"Status '{status}' should be valid"
    
    def test_forbidden_keys_present(self):
        validator = CalibrationValidator()
        
        calibration = {
            "b_theory": 0.85,
            "b_impl": 0.72,
            "b_deploy": 0.68,
            "status": "computed",
            "_temp": "temporary data",
            "_debug": True
        }
        
        is_valid, errors = validator.validate_intrinsic_calibration(calibration, "method_forbidden")
        
        assert not is_valid
        assert any("forbidden keys" in e.lower() for e in errors)
    
    def test_non_numeric_scores(self):
        validator = CalibrationValidator()
        
        calibration = {
            "b_theory": "high",
            "b_impl": 0.72,
            "b_deploy": 0.68,
            "status": "computed"
        }
        
        is_valid, errors = validator.validate_intrinsic_calibration(calibration, "method_nonnumeric")
        
        assert not is_valid
        assert any("must be numeric" in e.lower() for e in errors)


class TestBoundednessValidation:
    """Test validate_boundedness()"""
    
    def test_valid_bounded_scores(self):
        validator = CalibrationValidator()
        
        scores = {
            "score_a": 0.0,
            "score_b": 0.5,
            "score_c": 1.0
        }
        
        is_valid, errors = validator.validate_boundedness(scores, "test_context")
        
        assert is_valid
        assert len(errors) == 0
    
    def test_score_above_upper_bound(self):
        validator = CalibrationValidator()
        
        scores = {
            "score_a": 0.5,
            "score_b": 1.2
        }
        
        is_valid, errors = validator.validate_boundedness(scores, "test_context")
        
        assert not is_valid
        assert any("out of bounds" in e.lower() for e in errors)
    
    def test_score_below_lower_bound(self):
        validator = CalibrationValidator()
        
        scores = {
            "score_a": -0.1,
            "score_b": 0.5
        }
        
        is_valid, errors = validator.validate_boundedness(scores, "test_context")
        
        assert not is_valid
        assert any("out of bounds" in e.lower() for e in errors)
    
    def test_non_numeric_score(self):
        validator = CalibrationValidator()
        
        scores = {
            "score_a": 0.5,
            "score_b": "high"
        }
        
        is_valid, errors = validator.validate_boundedness(scores, "test_context")
        
        assert not is_valid
        assert any("must be numeric" in e.lower() for e in errors)


class TestConfigFilesValidation:
    """Test validate_config_files() integration"""
    
    def test_validate_all_pillars(self):
        validator = CalibrationValidator()
        
        report = validator.validate_config_files(pillar="all")
        
        assert "validation_summary" in report
        assert "results" in report
        assert "total_checks" in report["validation_summary"]
        assert report["validation_summary"]["total_checks"] > 0
    
    def test_validate_calibration_pillar_only(self):
        validator = CalibrationValidator()
        
        report = validator.validate_config_files(pillar="calibration")
        
        assert "intrinsic_calibration" in report["results"]
        assert "fusion_weights" in report["results"]
        assert "method_compatibility" in report["results"]
    
    def test_validate_questionnaire_pillar_only(self):
        validator = CalibrationValidator()
        
        report = validator.validate_config_files(pillar="questionnaire")
        
        assert "questionnaire_monolith" in report["results"]
    
    def test_convenience_function(self):
        report = validate_all_pillars()
        
        assert "validation_summary" in report
        assert "results" in report


class TestValidationReportGeneration:
    """Test generate_validation_report()"""
    
    def test_generate_json_report_detailed(self, tmp_path):
        validator = CalibrationValidator()
        
        report = validator.validate_config_files(pillar="calibration")
        output_path = tmp_path / "validation_report.json"
        
        validator.generate_validation_report(report, output_path, format="detailed")
        
        assert output_path.exists()
        
        import json
        with open(output_path) as f:
            saved_report = json.load(f)
        
        assert "timestamp" in saved_report
        assert "summary" in saved_report
        assert "status" in saved_report
        assert "results" in saved_report
    
    def test_generate_json_report_summary(self, tmp_path):
        validator = CalibrationValidator()
        
        report = validator.validate_config_files(pillar="calibration")
        output_path = tmp_path / "validation_summary.json"
        
        validator.generate_validation_report(report, output_path, format="summary")
        
        assert output_path.exists()
        
        import json
        with open(output_path) as f:
            saved_report = json.load(f)
        
        assert "timestamp" in saved_report
        assert "summary" in saved_report
        assert "status" in saved_report
        assert "critical_failures" in saved_report
        assert "results" not in saved_report
    
    def test_generate_text_report_detailed(self, tmp_path):
        validator = CalibrationValidator()
        
        report = validator.validate_config_files(pillar="calibration")
        output_path = tmp_path / "validation_report.txt"
        
        validator.generate_validation_report(report, output_path, format="detailed")
        
        assert output_path.exists()
        
        content = output_path.read_text()
        assert "CALIBRATION VALIDATION REPORT" in content
        assert "SUMMARY" in content
        assert "DETAILED RESULTS" in content
    
    def test_generate_text_report_summary(self, tmp_path):
        validator = CalibrationValidator()
        
        report = validator.validate_config_files(pillar="calibration")
        output_path = tmp_path / "validation_summary.txt"
        
        validator.generate_validation_report(report, output_path, format="summary")
        
        assert output_path.exists()
        
        content = output_path.read_text()
        assert "CALIBRATION VALIDATION REPORT" in content
        assert "SUMMARY" in content
    
    def test_report_status_passed(self, tmp_path):
        validator = CalibrationValidator()
        
        report = {
            "validation_summary": {
                "total_checks": 10,
                "passed": 10,
                "failed": 0,
                "warnings": 0
            },
            "results": {}
        }
        
        output_path = tmp_path / "passed_report.json"
        validator.generate_validation_report(report, output_path)
        
        import json
        with open(output_path) as f:
            saved_report = json.load(f)
        
        assert saved_report["status"] == "PASSED"
    
    def test_report_status_failed(self, tmp_path):
        validator = CalibrationValidator()
        
        report = {
            "validation_summary": {
                "total_checks": 10,
                "passed": 8,
                "failed": 2,
                "warnings": 0
            },
            "results": {}
        }
        
        output_path = tmp_path / "failed_report.json"
        validator.generate_validation_report(report, output_path)
        
        import json
        with open(output_path) as f:
            saved_report = json.load(f)
        
        assert saved_report["status"] == "FAILED"


@pytest.mark.updated
class TestValidatorIntegration:
    """Integration tests using actual COHORT_2024 data"""
    
    def test_load_and_validate_intrinsic_calibration(self):
        validator = CalibrationValidator()
        
        intrinsic_cal = validator.loader.load_calibration("intrinsic_calibration")
        
        assert "_cohort_metadata" in intrinsic_cal
        assert intrinsic_cal["_cohort_metadata"]["cohort_id"] == "COHORT_2024"
        assert "role_requirements" in intrinsic_cal
    
    def test_validate_score_q_role_requirements(self):
        validator = CalibrationValidator()
        
        intrinsic_cal = validator.loader.load_calibration("intrinsic_calibration")
        score_q_reqs = intrinsic_cal["role_requirements"]["SCORE_Q"]
        
        method_config = {
            "active_layers": score_q_reqs["required_layers"]
        }
        
        is_valid, errors = validator.validate_layer_completeness(method_config, "SCORE_Q")
        
        assert is_valid
        assert len(errors) == 0

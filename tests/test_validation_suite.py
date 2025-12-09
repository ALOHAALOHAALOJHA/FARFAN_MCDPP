"""Tests for the comprehensive validation suite."""

import json
import tempfile
from pathlib import Path

import pytest

from sensitive_rules_for_coding.validation_suite import (
    ValidationSuiteReport,
    run_all_validations,
    validate_anti_universality,
    validate_boundedness,
    validate_config_files,
    validate_fusion_weights,
    validate_intrinsic_calibration,
    validate_layer_completeness,
)


class TestLayerCompleteness:
    def test_valid_inventory_stub(self, tmp_path: Path) -> None:
        inventory_data = {
            "_cohort_metadata": {"cohort_id": "COHORT_2024"},
            "methods": {
                "_note": "Stub file"
            }
        }
        inventory_path = tmp_path / "inventory.json"
        with open(inventory_path, "w") as f:
            json.dump(inventory_data, f)

        result = validate_layer_completeness(inventory_path=inventory_path)
        assert result["passed"]
        assert len(result["warnings"]) > 0

    def test_valid_inventory_full(self, tmp_path: Path) -> None:
        inventory_data = {
            "_cohort_metadata": {"cohort_id": "COHORT_2024"},
            "methods": {
                "test.method.1": {
                    "role": "executor",
                    "layers": ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"]
                }
            }
        }
        inventory_path = tmp_path / "inventory.json"
        with open(inventory_path, "w") as f:
            json.dump(inventory_data, f)

        result = validate_layer_completeness(inventory_path=inventory_path)
        assert result["passed"]
        assert result["details"]["total_methods_checked"] == 1

    def test_missing_layers(self, tmp_path: Path) -> None:
        inventory_data = {
            "_cohort_metadata": {"cohort_id": "COHORT_2024"},
            "methods": {
                "test.method.1": {
                    "role": "executor",
                    "layers": ["@b", "@chain"]
                }
            }
        }
        inventory_path = tmp_path / "inventory.json"
        with open(inventory_path, "w") as f:
            json.dump(inventory_data, f)

        result = validate_layer_completeness(inventory_path=inventory_path)
        assert not result["passed"]
        assert len(result["errors"]) > 0

    def test_missing_layers_field(self, tmp_path: Path) -> None:
        inventory_data = {
            "_cohort_metadata": {"cohort_id": "COHORT_2024"},
            "methods": {
                "test.method.1": {
                    "role": "executor"
                }
            }
        }
        inventory_path = tmp_path / "inventory.json"
        with open(inventory_path, "w") as f:
            json.dump(inventory_data, f)

        result = validate_layer_completeness(inventory_path=inventory_path)
        assert not result["passed"]
        assert "layers" in str(result["errors"])


class TestFusionWeights:
    def test_valid_fusion_weights(self, tmp_path: Path) -> None:
        fusion_data = {
            "linear_weights": {
                "b": 0.4,
                "u": 0.2,
                "q": 0.1,
                "d": 0.1,
                "p": 0.1
            },
            "interaction_weights": {
                "(u,chain)": 0.1
            },
            "validation": {
                "total_sum": 1.0
            }
        }
        fusion_path = tmp_path / "fusion.json"
        with open(fusion_path, "w") as f:
            json.dump(fusion_data, f)

        result = validate_fusion_weights(fusion_weights_path=fusion_path)
        assert result["passed"]
        assert abs(result["details"]["total_sum"] - 1.0) < 1e-9

    def test_invalid_weight_sum(self, tmp_path: Path) -> None:
        fusion_data = {
            "linear_weights": {
                "b": 0.5,
                "u": 0.6
            },
            "interaction_weights": {}
        }
        fusion_path = tmp_path / "fusion.json"
        with open(fusion_path, "w") as f:
            json.dump(fusion_data, f)

        result = validate_fusion_weights(fusion_weights_path=fusion_path)
        assert not result["passed"]
        assert "sum to" in str(result["errors"]).lower()

    def test_negative_weights(self, tmp_path: Path) -> None:
        fusion_data = {
            "linear_weights": {
                "b": 0.6,
                "u": -0.1,
                "q": 0.5
            },
            "interaction_weights": {}
        }
        fusion_path = tmp_path / "fusion.json"
        with open(fusion_path, "w") as f:
            json.dump(fusion_data, f)

        result = validate_fusion_weights(fusion_weights_path=fusion_path)
        assert not result["passed"]
        assert len(result["details"]["negative_weights"]) > 0


class TestAntiUniversality:
    def test_no_universal_methods(self) -> None:
        scores_data = {
            "context_1": {
                "method_a": 0.8,
                "method_b": 0.9,
                "method_c": 0.7
            },
            "context_2": {
                "method_a": 0.9,
                "method_b": 0.7,
                "method_c": 0.8
            },
            "context_3": {
                "method_a": 0.7,
                "method_b": 0.8,
                "method_c": 0.9
            }
        }

        result = validate_anti_universality(scores_data=scores_data)
        assert result["passed"]

    def test_universal_method_detected(self) -> None:
        scores_data = {
            "context_1": {
                "method_a": 1.0,
                "method_b": 0.8
            },
            "context_2": {
                "method_a": 1.0,
                "method_b": 0.7
            },
            "context_3": {
                "method_a": 1.0,
                "method_b": 0.9
            }
        }

        result = validate_anti_universality(scores_data=scores_data)
        assert not result["passed"]
        assert len(result["details"]["universal_methods"]) > 0

    def test_no_scores_provided(self) -> None:
        result = validate_anti_universality()
        assert result["passed"]
        assert len(result["warnings"]) > 0


class TestIntrinsicCalibration:
    def test_valid_calibration(self, tmp_path: Path) -> None:
        calibration_data = {
            "base_layer": {
                "aggregation": {
                    "weights": {
                        "b_theory": 0.4,
                        "b_impl": 0.35,
                        "b_deploy": 0.25
                    }
                }
            },
            "components": {
                "b_theory": {
                    "weight": 0.4,
                    "subcomponents": {
                        "sub1": {"weight": 0.5},
                        "sub2": {"weight": 0.5}
                    }
                },
                "b_impl": {
                    "weight": 0.35,
                    "subcomponents": {
                        "sub1": {"weight": 0.6},
                        "sub2": {"weight": 0.4}
                    }
                },
                "b_deploy": {
                    "weight": 0.25,
                    "subcomponents": {
                        "sub1": {"weight": 1.0}
                    }
                }
            }
        }
        calibration_path = tmp_path / "calibration.json"
        with open(calibration_path, "w") as f:
            json.dump(calibration_data, f)

        result = validate_intrinsic_calibration(calibration_path=calibration_path)
        assert result["passed"]

    def test_missing_base_layer(self, tmp_path: Path) -> None:
        calibration_data = {
            "components": {}
        }
        calibration_path = tmp_path / "calibration.json"
        with open(calibration_path, "w") as f:
            json.dump(calibration_data, f)

        result = validate_intrinsic_calibration(calibration_path=calibration_path)
        assert not result["passed"]
        assert "base_layer" in str(result["errors"]).lower()

    def test_invalid_weight_sum(self, tmp_path: Path) -> None:
        calibration_data = {
            "base_layer": {
                "aggregation": {
                    "weights": {
                        "b_theory": 0.5,
                        "b_impl": 0.3,
                        "b_deploy": 0.3
                    }
                }
            },
            "components": {
                "b_theory": {"weight": 0.5, "subcomponents": {}},
                "b_impl": {"weight": 0.3, "subcomponents": {}},
                "b_deploy": {"weight": 0.3, "subcomponents": {}}
            }
        }
        calibration_path = tmp_path / "calibration.json"
        with open(calibration_path, "w") as f:
            json.dump(calibration_data, f)

        result = validate_intrinsic_calibration(calibration_path=calibration_path)
        assert not result["passed"]


class TestConfigFiles:
    def test_valid_config_files(self, tmp_path: Path) -> None:
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        cohort_file = config_dir / "COHORT_2024_test.json"
        with open(cohort_file, "w") as f:
            json.dump({"_cohort_metadata": {"cohort_id": "COHORT_2024"}}, f)

        result = validate_config_files(config_dir=config_dir)
        assert result["passed"]
        assert result["details"]["files_passed"] > 0

    def test_invalid_json(self, tmp_path: Path) -> None:
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        cohort_file = config_dir / "COHORT_2024_invalid.json"
        with open(cohort_file, "w") as f:
            f.write("{invalid json")

        result = validate_config_files(config_dir=config_dir)
        assert not result["passed"]
        assert len(result["details"]["files_failed"]) > 0


class TestBoundedness:
    def test_valid_bounded_scores(self) -> None:
        scores_data = {
            "context_1": {
                "method_a": 0.5,
                "method_b": 0.0,
                "method_c": 1.0
            },
            "context_2": {
                "method_a": 0.25,
                "method_b": 0.75
            }
        }

        result = validate_boundedness(scores_data=scores_data)
        assert result["passed"]
        assert result["details"]["total_scores_checked"] == 5

    def test_score_below_minimum(self) -> None:
        scores_data = {
            "context_1": {
                "method_a": -0.1,
                "method_b": 0.5
            }
        }

        result = validate_boundedness(scores_data=scores_data)
        assert not result["passed"]
        assert len(result["details"]["out_of_bounds_scores"]) > 0

    def test_score_above_maximum(self) -> None:
        scores_data = {
            "context_1": {
                "method_a": 1.5,
                "method_b": 0.5
            }
        }

        result = validate_boundedness(scores_data=scores_data)
        assert not result["passed"]
        assert len(result["details"]["out_of_bounds_scores"]) > 0

    def test_nan_values(self) -> None:
        scores_data = {
            "context_1": {
                "method_a": float("nan"),
                "method_b": 0.5
            }
        }

        result = validate_boundedness(scores_data=scores_data)
        assert not result["passed"]
        assert len(result["details"]["invalid_values"]) > 0

    def test_nested_scores(self) -> None:
        scores_data = {
            "dimension_1": {
                "question_1": {
                    "method_a": 0.8,
                    "method_b": 0.6
                },
                "question_2": {
                    "method_a": 0.9,
                    "method_b": 0.7
                }
            }
        }

        result = validate_boundedness(scores_data=scores_data)
        assert result["passed"]
        assert result["details"]["total_scores_checked"] == 4


class TestRunAllValidations:
    def test_run_with_temp_config(self, tmp_path: Path) -> None:
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        calibration_dir = config_dir / "calibration"
        calibration_dir.mkdir()

        inventory_path = calibration_dir / "COHORT_2024_canonical_method_inventory.json"
        with open(inventory_path, "w") as f:
            json.dump({"methods": {"_note": "stub"}}, f)

        fusion_path = calibration_dir / "COHORT_2024_fusion_weights.json"
        with open(fusion_path, "w") as f:
            json.dump(
                {
                    "linear_weights": {"b": 0.6, "u": 0.2},
                    "interaction_weights": {"(u,b)": 0.2}
                },
                f
            )

        calibration_path = calibration_dir / "COHORT_2024_intrinsic_calibration.json"
        with open(calibration_path, "w") as f:
            json.dump(
                {
                    "base_layer": {
                        "aggregation": {"weights": {"b_theory": 0.5, "b_impl": 0.5}}
                    },
                    "components": {
                        "b_theory": {"weight": 0.5, "subcomponents": {}},
                        "b_impl": {"weight": 0.5, "subcomponents": {}}
                    }
                },
                f
            )

        scores_data = {
            "ctx1": {"m1": 0.5, "m2": 0.7},
            "ctx2": {"m1": 0.6, "m2": 0.8}
        }

        report = run_all_validations(
            config_dir=config_dir,
            scores_data=scores_data,
            verbose=False
        )

        assert isinstance(report, dict)
        assert "execution_timestamp" in report
        assert "total_validators" in report
        assert report["total_validators"] == 6
        assert "overall_passed" in report


@pytest.mark.updated
class TestValidationSuiteIntegration:
    """Integration tests for the validation suite."""

    def test_suite_report_structure(self, tmp_path: Path) -> None:
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        calibration_dir = config_dir / "calibration"
        calibration_dir.mkdir()

        inventory_path = calibration_dir / "COHORT_2024_canonical_method_inventory.json"
        with open(inventory_path, "w") as f:
            json.dump({"methods": {"_note": "stub"}}, f)

        fusion_path = calibration_dir / "COHORT_2024_fusion_weights.json"
        with open(fusion_path, "w") as f:
            json.dump({"linear_weights": {"b": 1.0}, "interaction_weights": {}}, f)

        calibration_path = calibration_dir / "COHORT_2024_intrinsic_calibration.json"
        with open(calibration_path, "w") as f:
            json.dump(
                {
                    "base_layer": {"aggregation": {"weights": {"b": 1.0}}},
                    "components": {"b_theory": {}, "b_impl": {}, "b_deploy": {}}
                },
                f
            )

        report = run_all_validations(config_dir=config_dir, verbose=False)

        assert "validation_results" in report
        assert "summary" in report
        assert "overall_passed" in report
        assert len(report["validation_results"]) == 6

        for validator_name, result in report["validation_results"].items():
            assert "validator_name" in result
            assert "passed" in result
            assert "errors" in result
            assert "warnings" in result
            assert "details" in result

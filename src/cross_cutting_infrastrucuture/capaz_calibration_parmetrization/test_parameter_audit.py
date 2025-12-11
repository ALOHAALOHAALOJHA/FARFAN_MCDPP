"""
Test Suite for Hardcoded Parameter Audit System

Tests the scanner's ability to detect various types of hardcoded parameters
and validate correct configuration loading patterns.
"""

import json
import tempfile
from pathlib import Path
from textwrap import dedent

import pytest

from hardcoded_parameter_scanner import (
    HardcodedParameterScanner,
    ConfigurationRegistry,
    ParameterViolation,
)
from executor_parameter_validator import (
    ExecutorParameterValidator,
    ExecutorViolation,
)


class TestConfigurationRegistry:
    """Test configuration registry loading and value extraction."""
    
    def test_load_intrinsic_calibration(self, tmp_path):
        """Test loading intrinsic calibration config."""
        calibration_dir = tmp_path / "calibration"
        calibration_dir.mkdir()
        
        config = {
            "base_layer": {
                "aggregation": {
                    "weights": {
                        "b_theory": 0.40,
                        "b_impl": 0.35,
                        "b_deploy": 0.25
                    }
                }
            },
            "components": {
                "b_theory": {
                    "weight": 0.40,
                    "subcomponents": {
                        "grounded_in_valid_statistics": {
                            "weight": 0.40,
                            "thresholds": {
                                "excellent": 80.0,
                                "good": 60.0
                            },
                            "score_mapping": {
                                "excellent": 1.0,
                                "good": 0.8
                            }
                        }
                    }
                }
            }
        }
        
        config_path = calibration_dir / "COHORT_2024_intrinsic_calibration.json"
        with open(config_path, "w") as f:
            json.dump(config, f)
        
        registry = ConfigurationRegistry(tmp_path)
        
        assert 0.40 in registry.known_weights
        assert 0.35 in registry.known_weights
        assert 0.25 in registry.known_weights
        assert 80.0 in registry.known_thresholds
        assert 60.0 in registry.known_thresholds
        assert 1.0 in registry.known_scores
        assert 0.8 in registry.known_scores
    
    def test_is_value_in_config(self, tmp_path):
        """Test checking if value exists in config."""
        calibration_dir = tmp_path / "calibration"
        calibration_dir.mkdir()
        parametrization_dir = tmp_path / "parametrization"
        parametrization_dir.mkdir()
        
        intrinsic_config = {
            "base_layer": {
                "aggregation": {
                    "weights": {"b_theory": 0.40}
                }
            }
        }
        
        with open(calibration_dir / "COHORT_2024_intrinsic_calibration.json", "w") as f:
            json.dump(intrinsic_config, f)
        
        registry = ConfigurationRegistry(tmp_path)
        
        is_in_config, source = registry.is_value_in_config(0.40, "weight")
        assert is_in_config
        assert "intrinsic_calibration" in source
        
        is_in_config, source = registry.is_value_in_config(0.99, "weight")
        assert not is_in_config
        assert source is None


class TestHardcodedParameterScanner:
    """Test hardcoded parameter detection."""
    
    def test_detect_hardcoded_weight(self, tmp_path):
        """Test detection of hardcoded weight value."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        
        calibration_dir = config_dir / "calibration"
        calibration_dir.mkdir()
        parametrization_dir = config_dir / "parametrization"
        parametrization_dir.mkdir()
        
        with open(calibration_dir / "COHORT_2024_intrinsic_calibration.json", "w") as f:
            json.dump({}, f)
        
        with open(calibration_dir / "COHORT_2024_fusion_weights.json", "w") as f:
            json.dump({}, f)
        
        test_file = src_dir / "test_module.py"
        test_file.write_text(dedent("""
            def calculate_score():
                weight = 0.35
                return weight * 100
        """))
        
        scanner = HardcodedParameterScanner(src_dir, config_dir)
        violations = scanner.scan_file(test_file)
        
        weight_violations = [v for v in violations if v.category == "weight"]
        assert len(weight_violations) > 0
        
        violation = weight_violations[0]
        assert violation.hardcoded_value == 0.35
        assert violation.severity == "CRITICAL"
    
    def test_detect_hardcoded_threshold(self, tmp_path):
        """Test detection of hardcoded threshold value."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        
        calibration_dir = config_dir / "calibration"
        calibration_dir.mkdir()
        parametrization_dir = config_dir / "parametrization"
        parametrization_dir.mkdir()
        
        with open(calibration_dir / "COHORT_2024_intrinsic_calibration.json", "w") as f:
            json.dump({}, f)
        
        test_file = src_dir / "validator.py"
        test_file.write_text(dedent("""
            def validate_score(score):
                threshold = 0.7
                return score >= threshold
        """))
        
        scanner = HardcodedParameterScanner(src_dir, config_dir)
        violations = scanner.scan_file(test_file)
        
        threshold_violations = [v for v in violations if v.category == "threshold"]
        assert len(threshold_violations) > 0
        
        violation = threshold_violations[0]
        assert violation.hardcoded_value == 0.7
        assert violation.severity == "HIGH"
    
    def test_detect_hardcoded_timeout(self, tmp_path):
        """Test detection of hardcoded timeout value."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        
        calibration_dir = config_dir / "calibration"
        calibration_dir.mkdir()
        parametrization_dir = config_dir / "parametrization"
        parametrization_dir.mkdir()
        
        with open(parametrization_dir / "COHORT_2024_executor_config.json", "w") as f:
            json.dump({}, f)
        
        test_file = src_dir / "executor.py"
        test_file.write_text(dedent("""
            class MyExecutor:
                def __init__(self):
                    self.timeout = 300
        """))
        
        scanner = HardcodedParameterScanner(src_dir, config_dir)
        violations = scanner.scan_file(test_file)
        
        timeout_violations = [v for v in violations if v.category == "timeout"]
        assert len(timeout_violations) > 0
        
        violation = timeout_violations[0]
        assert violation.hardcoded_value == 300
        assert violation.severity == "MEDIUM"
    
    def test_exclude_test_files(self, tmp_path):
        """Test that test files are excluded."""
        src_dir = tmp_path / "src"
        tests_dir = src_dir / "tests"
        tests_dir.mkdir(parents=True)
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        
        calibration_dir = config_dir / "calibration"
        calibration_dir.mkdir()
        parametrization_dir = config_dir / "parametrization"
        parametrization_dir.mkdir()
        
        test_file = tests_dir / "test_something.py"
        test_file.write_text(dedent("""
            def test_hardcoded_value():
                weight = 0.35
                assert weight == 0.35
        """))
        
        scanner = HardcodedParameterScanner(src_dir, config_dir)
        
        assert scanner.should_exclude_file(test_file)
    
    def test_exclude_cohort_config_modules(self, tmp_path):
        """Test that COHORT_2024 config modules are excluded."""
        src_dir = tmp_path / "src"
        config_module_dir = src_dir / "capaz_calibration_parmetrization" / "calibration"
        config_module_dir.mkdir(parents=True)
        
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        
        config_file = config_module_dir / "COHORT_2024_loader.py"
        config_file.write_text(dedent("""
            CONFIG = {
                "weight": 0.35
            }
        """))
        
        scanner = HardcodedParameterScanner(src_dir, config_dir)
        
        assert scanner.should_exclude_file(config_file)


class TestExecutorParameterValidator:
    """Test executor parameter validation."""
    
    def test_detect_executor_hardcoded_timeout(self, tmp_path):
        """Test detection of hardcoded timeout in executor."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        
        executor_file = src_dir / "my_executor.py"
        executor_file.write_text(dedent("""
            class MyExecutor:
                def __init__(self):
                    self.timeout = 300
                    self.max_retries = 3
        """))
        
        validator = ExecutorParameterValidator(src_dir)
        violations = validator.validate_file(executor_file)
        
        assert len(violations) >= 2
        
        timeout_violation = next(v for v in violations if v.parameter_name == "timeout")
        assert timeout_violation.hardcoded_value == 300
        assert "config.get" in timeout_violation.recommendation
    
    def test_accept_config_loaded_parameters(self, tmp_path):
        """Test that config-loaded parameters don't trigger violations."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        
        executor_file = src_dir / "good_executor.py"
        executor_file.write_text(dedent("""
            class GoodExecutor:
                def __init__(self, config):
                    self.timeout = config.get('timeout', 300)
                    self.max_retries = os.getenv('MAX_RETRIES', '3')
        """))
        
        validator = ExecutorParameterValidator(src_dir)
        violations = validator.validate_file(executor_file)
        
        assert len(violations) == 0
    
    def test_identify_executor_class(self, tmp_path):
        """Test executor class identification."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        
        executor_file = src_dir / "my_executor.py"
        executor_file.write_text(dedent("""
            class BaseExecutor:
                pass
            
            class MyExecutor(BaseExecutor):
                def __init__(self):
                    self.timeout = 300
        """))
        
        validator = ExecutorParameterValidator(src_dir)
        violations = validator.validate_file(executor_file)
        
        assert len(violations) > 0
        assert violations[0].executor_class == "MyExecutor"
    
    def test_skip_non_executor_classes(self, tmp_path):
        """Test that non-executor classes are not flagged."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        
        module_file = src_dir / "my_module.py"
        module_file.write_text(dedent("""
            class MyClass:
                def __init__(self):
                    self.timeout = 300
        """))
        
        validator = ExecutorParameterValidator(src_dir)
        violations = validator.validate_file(module_file)
        
        assert len(violations) == 0


class TestEndToEnd:
    """End-to-end integration tests."""
    
    def test_full_scan_workflow(self, tmp_path):
        """Test complete scanning workflow."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        calibration_dir = config_dir / "calibration"
        calibration_dir.mkdir()
        parametrization_dir = config_dir / "parametrization"
        parametrization_dir.mkdir()
        
        with open(calibration_dir / "COHORT_2024_intrinsic_calibration.json", "w") as f:
            json.dump({"base_layer": {"aggregation": {"weights": {"b": 0.5}}}}, f)
        
        with open(calibration_dir / "COHORT_2024_fusion_weights.json", "w") as f:
            json.dump({}, f)
        
        with open(parametrization_dir / "COHORT_2024_executor_config.json", "w") as f:
            json.dump({}, f)
        
        with open(parametrization_dir / "COHORT_2024_runtime_layers.json", "w") as f:
            json.dump({}, f)
        
        bad_file = src_dir / "module.py"
        bad_file.write_text(dedent("""
            def process():
                weight = 0.35
                threshold = 0.7
                return weight > threshold
        """))
        
        scanner = HardcodedParameterScanner(src_dir, config_dir)
        scanner.scan_directory()
        
        assert scanner.statistics.total_files_scanned > 0
        assert scanner.statistics.violations_found > 0
        
        md_report = output_dir / "report.md"
        scanner.generate_report_markdown(md_report)
        assert md_report.exists()
        
        json_report = output_dir / "report.json"
        scanner.generate_report_json(json_report)
        assert json_report.exists()
        
        with open(json_report) as f:
            report_data = json.load(f)
        
        assert "statistics" in report_data
        assert "violations" in report_data
        assert "certification" in report_data


def test_violation_serialization():
    """Test violation serialization to dict."""
    violation = ParameterViolation(
        file_path="src/module.py",
        line_number=10,
        column=4,
        variable_name="weight",
        hardcoded_value=0.35,
        value_type="float",
        context="weight = 0.35",
        expected_config_source="COHORT_2024_fusion_weights.json",
        severity="CRITICAL",
        category="weight",
    )
    
    data = violation.to_dict()
    
    assert data["file_path"] == "src/module.py"
    assert data["line_number"] == 10
    assert data["hardcoded_value"] == 0.35
    assert data["severity"] == "CRITICAL"


def test_executor_violation_serialization():
    """Test executor violation serialization."""
    violation = ExecutorViolation(
        executor_class="MyExecutor",
        file_path="src/executor.py",
        line_number=15,
        violation_type="HARDCODED_RUNTIME_PARAM",
        parameter_name="timeout",
        hardcoded_value=300,
        recommendation="Load from config",
    )
    
    data = violation.to_dict()
    
    assert data["executor_class"] == "MyExecutor"
    assert data["parameter_name"] == "timeout"
    assert data["hardcoded_value"] == 300


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

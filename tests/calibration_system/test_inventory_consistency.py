"""
Test 1: Inventory Consistency - Verifying Same Methods in All JSONs

Validates that all executor method inventories are consistent across:
- executors_methods.json: 30 executors with method lists
- intrinsic_calibration.json: All methods have calibration entries
- canonical method catalog (if exists)

FAILURE CONDITION: Any method missing from any inventory = SYSTEM NOT READY
"""
import json
import pytest
from pathlib import Path
from typing import Dict, List, Set, Any


class TestInventoryConsistency:
    @pytest.fixture(scope="class")
    def executors_methods(self) -> Dict[str, Any]:
        """Load executors_methods.json"""
        path = Path("src/farfan_pipeline/core/orchestrator/executors_methods.json")
        assert path.exists(), f"executors_methods.json not found at {path}"
        with open(path) as f:
            return json.load(f)

    @pytest.fixture(scope="class")
    def intrinsic_calibration(self) -> Dict[str, Any]:
        """Load intrinsic_calibration.json"""
        path = Path("system/config/calibration/intrinsic_calibration.json")
        assert path.exists(), f"intrinsic_calibration.json not found at {path}"
        with open(path) as f:
            return json.load(f)

    @pytest.fixture(scope="class")
    def calibration_rubric(self) -> Dict[str, Any]:
        """Load calibration rubric"""
        path = Path("config/intrinsic_calibration_rubric.json")
        assert path.exists(), f"calibration rubric not found at {path}"
        with open(path) as f:
            return json.load(f)

    def test_executors_methods_structure(self, executors_methods):
        """Verify executors_methods.json has correct structure"""
        assert isinstance(executors_methods, list), "executors_methods must be a list"
        assert len(executors_methods) > 0, "executors_methods cannot be empty"
        
        for executor in executors_methods:
            assert "executor_id" in executor, f"Executor missing executor_id: {executor}"
            assert "methods" in executor, f"Executor {executor.get('executor_id')} missing methods"
            assert isinstance(executor["methods"], list), \
                f"Executor {executor['executor_id']} methods must be a list"

    def test_30_executors_present(self, executors_methods):
        """Verify exactly 30 executors are defined"""
        executor_ids = [e["executor_id"] for e in executors_methods]
        assert len(executor_ids) == 30, \
            f"Expected 30 executors, found {len(executor_ids)}: {executor_ids}"
        
        expected_pattern = set()
        for d in range(1, 7):
            for q in range(1, 6):
                expected_pattern.add(f"D{d}-Q{q}")
        
        actual_set = set(executor_ids)
        missing = expected_pattern - actual_set
        extra = actual_set - expected_pattern
        
        assert not missing, f"Missing executors: {sorted(missing)}"
        assert not extra, f"Unexpected executors: {sorted(extra)}"

    def test_all_methods_unique_per_executor(self, executors_methods):
        """Verify no duplicate methods within each executor"""
        for executor in executors_methods:
            methods = executor["methods"]
            method_sigs = [f"{m['class']}.{m['method']}" for m in methods]
            duplicates = [sig for sig in method_sigs if method_sigs.count(sig) > 1]
            
            assert not duplicates, \
                f"Executor {executor['executor_id']} has duplicate methods: {set(duplicates)}"

    def test_method_format_consistency(self, executors_methods):
        """Verify all methods have required fields"""
        for executor in executors_methods:
            for method in executor["methods"]:
                assert "class" in method, \
                    f"Method in {executor['executor_id']} missing 'class': {method}"
                assert "method" in method, \
                    f"Method in {executor['executor_id']} missing 'method': {method}"
                assert isinstance(method["class"], str) and method["class"], \
                    f"Invalid class name in {executor['executor_id']}: {method}"
                assert isinstance(method["method"], str) and method["method"], \
                    f"Invalid method name in {executor['executor_id']}: {method}"

    def test_intrinsic_calibration_covers_all_methods(
        self, executors_methods, intrinsic_calibration
    ):
        """CRITICAL: Verify all executor methods have intrinsic calibration entries"""
        all_methods = set()
        for executor in executors_methods:
            for method in executor["methods"]:
                method_id = f"{method['class']}.{method['method']}"
                all_methods.add(method_id)
        
        calibrated_methods = set(intrinsic_calibration.keys()) - {"_metadata"}
        
        missing_calibrations = all_methods - calibrated_methods
        extra_calibrations = calibrated_methods - all_methods
        
        failure_report = []
        if missing_calibrations:
            failure_report.append(
                f"CRITICAL: {len(missing_calibrations)} methods missing calibration:\n"
                + "\n".join(f"  - {m}" for m in sorted(missing_calibrations)[:20])
            )
        
        if extra_calibrations:
            failure_report.append(
                f"WARNING: {len(extra_calibrations)} calibrations for unknown methods:\n"
                + "\n".join(f"  - {m}" for m in sorted(extra_calibrations)[:20])
            )
        
        assert not missing_calibrations, "\n".join(failure_report)

    def test_calibration_status_field_present(self, intrinsic_calibration):
        """Verify all calibration entries have status field"""
        for method_id, calibration in intrinsic_calibration.items():
            if method_id == "_metadata":
                continue
            
            assert isinstance(calibration, dict), \
                f"Calibration for {method_id} must be a dict, got {type(calibration)}"
            
            assert "status" in calibration, \
                f"Calibration for {method_id} missing 'status' field"
            
            valid_statuses = {"computed", "excluded", "manual", "error"}
            assert calibration["status"] in valid_statuses, \
                f"Invalid status for {method_id}: {calibration['status']}"

    def test_no_empty_method_lists(self, executors_methods):
        """Verify no executor has empty method list"""
        for executor in executors_methods:
            assert len(executor["methods"]) > 0, \
                f"Executor {executor['executor_id']} has no methods"

    def test_method_naming_conventions(self, executors_methods):
        """Verify method names follow Python conventions"""
        import re
        
        class_pattern = re.compile(r'^[A-Z][a-zA-Z0-9]*$')
        method_pattern = re.compile(r'^[a-z_][a-z0-9_]*$')
        
        for executor in executors_methods:
            for method in executor["methods"]:
                class_name = method["class"]
                method_name = method["method"]
                
                assert class_pattern.match(class_name), \
                    f"Invalid class name in {executor['executor_id']}: {class_name}"
                assert method_pattern.match(method_name), \
                    f"Invalid method name in {executor['executor_id']}: {method_name}"

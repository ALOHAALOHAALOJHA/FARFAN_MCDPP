"""
Test 3: Intrinsic Coverage - ≥80% Methods + All 30 Executors Have status='computed'

Validates calibration completeness:
- At least 80% of all methods must have calibration status='computed'
- All 30 executors must have at least one method with status='computed'
- No executor should be entirely 'excluded' or 'manual'

FAILURE CONDITION: Coverage < 80% OR any executor without computed status = NOT READY
"""
import json
import pytest
from pathlib import Path
from typing import Dict, List, Set, Any


class TestIntrinsicCoverage:
    
    MIN_COVERAGE_PERCENT = 80.0
    
    @pytest.fixture(scope="class")
    def executors_methods(self) -> Dict[str, Any]:
        """Load executors_methods.json"""
        path = Path("src/farfan_pipeline/core/orchestrator/executors_methods.json")
        with open(path) as f:
            return json.load(f)

    @pytest.fixture(scope="class")
    def intrinsic_calibration(self) -> Dict[str, Any]:
        """Load intrinsic_calibration.json"""
        path = Path("system/config/calibration/intrinsic_calibration.json")
        with open(path) as f:
            return json.load(f)

    def test_intrinsic_calibration_not_empty(self, intrinsic_calibration):
        """Verify intrinsic_calibration.json is not empty"""
        methods = {k: v for k, v in intrinsic_calibration.items() if k != "_metadata"}
        assert len(methods) > 0, "intrinsic_calibration.json has no method entries"

    def test_80_percent_coverage_with_computed_status(
        self, executors_methods, intrinsic_calibration
    ):
        """CRITICAL: Verify at least 80% of methods have status='computed'"""
        all_methods = set()
        for executor in executors_methods:
            for method in executor["methods"]:
                method_id = f"{method['class']}.{method['method']}"
                all_methods.add(method_id)
        
        total_methods = len(all_methods)
        computed_methods = set()
        
        for method_id, calibration in intrinsic_calibration.items():
            if method_id == "_metadata":
                continue
            
            if method_id in all_methods:
                status = calibration.get("status", "missing")
                if status == "computed":
                    computed_methods.add(method_id)
        
        coverage_percent = (len(computed_methods) / total_methods * 100) if total_methods > 0 else 0
        
        missing_computed = all_methods - computed_methods
        
        failure_msg = (
            f"CRITICAL: Calibration coverage is {coverage_percent:.1f}% "
            f"({len(computed_methods)}/{total_methods}), "
            f"minimum required is {self.MIN_COVERAGE_PERCENT}%\n"
            f"Methods without 'computed' status: {len(missing_computed)}\n"
        )
        
        if missing_computed and len(missing_computed) <= 20:
            failure_msg += "Missing methods:\n" + "\n".join(
                f"  - {m}" for m in sorted(missing_computed)
            )
        
        assert coverage_percent >= self.MIN_COVERAGE_PERCENT, failure_msg

    def test_all_30_executors_have_computed_methods(
        self, executors_methods, intrinsic_calibration
    ):
        """CRITICAL: Every executor must have at least one method with status='computed'"""
        failures = []
        
        for executor in executors_methods:
            executor_id = executor["executor_id"]
            has_computed = False
            
            for method in executor["methods"]:
                method_id = f"{method['class']}.{method['method']}"
                calibration = intrinsic_calibration.get(method_id, {})
                
                if calibration.get("status") == "computed":
                    has_computed = True
                    break
            
            if not has_computed:
                failures.append(
                    f"Executor {executor_id} has no methods with status='computed'"
                )
        
        assert not failures, \
            f"CRITICAL: Executors without computed calibrations:\n" + "\n".join(failures)

    def test_status_field_valid_values(self, intrinsic_calibration):
        """Verify all status fields have valid values"""
        valid_statuses = {"computed", "excluded", "manual", "error"}
        
        for method_id, calibration in intrinsic_calibration.items():
            if method_id == "_metadata":
                continue
            
            status = calibration.get("status")
            assert status in valid_statuses, \
                f"Invalid status '{status}' for {method_id}. " \
                f"Must be one of: {valid_statuses}"

    def test_computed_methods_have_scores(self, intrinsic_calibration):
        """Verify methods with status='computed' have actual scores"""
        for method_id, calibration in intrinsic_calibration.items():
            if method_id == "_metadata":
                continue
            
            if calibration.get("status") == "computed":
                assert "b_theory" in calibration or "scores" in calibration, \
                    f"Method {method_id} has status='computed' but no scores"

    def test_no_fully_excluded_executors(self, executors_methods, intrinsic_calibration):
        """Warn if any executor has all methods excluded"""
        warnings = []
        
        for executor in executors_methods:
            executor_id = executor["executor_id"]
            all_excluded = True
            
            for method in executor["methods"]:
                method_id = f"{method['class']}.{method['method']}"
                calibration = intrinsic_calibration.get(method_id, {})
                
                if calibration.get("status") != "excluded":
                    all_excluded = False
                    break
            
            if all_excluded:
                warnings.append(
                    f"WARNING: Executor {executor_id} has all methods excluded"
                )
        
        if warnings:
            print("\n" + "\n".join(warnings))

    def test_excluded_methods_have_reason(self, intrinsic_calibration):
        """Verify excluded methods have exclusion reason"""
        for method_id, calibration in intrinsic_calibration.items():
            if method_id == "_metadata":
                continue
            
            if calibration.get("status") == "excluded":
                assert "exclusion_reason" in calibration or "reason" in calibration, \
                    f"Excluded method {method_id} missing exclusion reason"

    def test_manual_methods_documented(self, intrinsic_calibration):
        """Verify methods with status='manual' are documented"""
        manual_methods = []
        
        for method_id, calibration in intrinsic_calibration.items():
            if method_id == "_metadata":
                continue
            
            if calibration.get("status") == "manual":
                manual_methods.append(method_id)
                assert "note" in calibration or "reason" in calibration, \
                    f"Manual method {method_id} missing documentation"
        
        if manual_methods:
            print(f"\nFound {len(manual_methods)} manual calibrations: {manual_methods[:5]}")

    def test_error_status_methods_tracked(self, intrinsic_calibration):
        """Track methods with status='error' for debugging"""
        error_methods = []
        
        for method_id, calibration in intrinsic_calibration.items():
            if method_id == "_metadata":
                continue
            
            if calibration.get("status") == "error":
                error_methods.append(method_id)
        
        if error_methods:
            print(
                f"\nWARNING: {len(error_methods)} methods have status='error': "
                f"{error_methods[:5]}"
            )

    def test_coverage_by_executor(self, executors_methods, intrinsic_calibration):
        """Report coverage statistics per executor"""
        stats = []
        
        for executor in executors_methods:
            executor_id = executor["executor_id"]
            total = len(executor["methods"])
            computed = 0
            
            for method in executor["methods"]:
                method_id = f"{method['class']}.{method['method']}"
                calibration = intrinsic_calibration.get(method_id, {})
                
                if calibration.get("status") == "computed":
                    computed += 1
            
            coverage = (computed / total * 100) if total > 0 else 0
            stats.append((executor_id, coverage, computed, total))
        
        stats.sort(key=lambda x: x[1])
        
        low_coverage = [s for s in stats if s[1] < self.MIN_COVERAGE_PERCENT]
        
        if low_coverage:
            msg = "\nExecutors with coverage below threshold:\n"
            for executor_id, coverage, computed, total in low_coverage[:10]:
                msg += f"  {executor_id}: {coverage:.1f}% ({computed}/{total})\n"
            print(msg)

    def test_metadata_present_in_intrinsic(self, intrinsic_calibration):
        """Verify _metadata is present with version info"""
        assert "_metadata" in intrinsic_calibration, \
            "intrinsic_calibration.json missing _metadata"
        
        metadata = intrinsic_calibration["_metadata"]
        assert "version" in metadata, "_metadata missing version"
        assert "generated" in metadata or "last_updated" in metadata, \
            "_metadata missing timestamp"

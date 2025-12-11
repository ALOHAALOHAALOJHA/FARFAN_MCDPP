"""
Comprehensive Calibration Validators

Validates calibration configuration integrity across the three-pillar system:
- Layer completeness per role
- Fusion weight normalization and non-negativity
- Anti-universality constraints
- Intrinsic calibration schema compliance
- Score boundedness [0,1]

All validators return (is_valid, error_messages) tuples.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from cross_cutting_infrastrucuture.capaz_calibration_parmetrization.cohort_loader import CohortLoader


class CalibrationValidator:
    """
    Comprehensive calibration validator for COHORT 2024 system.
    
    Validates:
    - Layer completeness (all required layers present per role)
    - Fusion weight normalization (sum(linear)+sum(interaction)=1.0±1e-9)
    - Fusion weight non-negativity (all weights≥0)
    - Anti-universality (no method maximal compatibility everywhere: min(x_@q,x_@d,x_@p)<0.9)
    - Intrinsic calibration schema (required keys, scores in [0,1], valid status)
    - Score boundedness (all scores in [0,1])
    """
    
    EPSILON = 1e-9
    ANTI_UNIVERSALITY_THRESHOLD = 0.9
    
    VALID_STATUSES = {"computed", "pending", "excluded", "none"}
    
    REQUIRED_INTRINSIC_KEYS = {"b_theory", "b_impl", "b_deploy", "status"}
    
    FORBIDDEN_INTRINSIC_KEYS = {"_temp", "_debug", "internal_state"}
    
    ROLE_REQUIRED_LAYERS = {
        "SCORE_Q": {"@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"},
        "INGEST_PDM": {"@b", "@chain", "@u", "@m"},
        "STRUCTURE": {"@b", "@chain", "@u", "@m"},
        "EXTRACT": {"@b", "@chain", "@u", "@m"},
        "AGGREGATE": {"@b", "@chain", "@u", "@m"},
        "REPORT": {"@b", "@chain", "@u", "@m"},
        "META_TOOL": {"@b", "@chain", "@u", "@m"},
        "TRANSFORM": {"@b", "@chain", "@u", "@m"},
    }
    
    def __init__(self, cohort_loader: CohortLoader | None = None) -> None:
        """
        Initialize validator with optional cohort loader.
        
        Args:
            cohort_loader: CohortLoader instance for loading config files
        """
        self.loader = cohort_loader or CohortLoader()
    
    def validate_layer_completeness(
        self,
        method_config: dict[str, Any],
        role: str
    ) -> tuple[bool, list[str]]:
        """
        Validate that all required layers for role are present.
        
        Args:
            method_config: Method configuration with 'active_layers' key
            role: Method role (SCORE_Q, INGEST_PDM, etc.)
        
        Returns:
            (is_valid, error_messages) tuple
        """
        errors = []
        
        if role not in self.ROLE_REQUIRED_LAYERS:
            errors.append(f"Unknown role: {role}")
            return False, errors
        
        required_layers = self.ROLE_REQUIRED_LAYERS[role]
        declared_layers = set(method_config.get("active_layers", []))
        
        missing = required_layers - declared_layers
        
        if missing:
            if "justifications" not in method_config:
                errors.append(
                    f"Role {role} missing layers {sorted(missing)} without justifications"
                )
                return False, errors
            
            for layer in missing:
                if layer not in method_config["justifications"]:
                    errors.append(
                        f"Role {role} missing layer {layer} without justification"
                    )
                elif not method_config["justifications"][layer].get("approved", False):
                    errors.append(
                        f"Role {role} layer {layer} justification not approved"
                    )
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def validate_fusion_weights(
        self,
        fusion_config: dict[str, Any],
        role: str
    ) -> tuple[bool, list[str]]:
        """
        Validate fusion weights normalization and non-negativity.
        
        Checks:
        - All weights ≥ 0 (non-negativity)
        - sum(linear_weights) + sum(interaction_weights) = 1.0 ± 1e-9 (normalization)
        
        Args:
            fusion_config: Role fusion parameters with linear_weights and interaction_weights
            role: Method role
        
        Returns:
            (is_valid, error_messages) tuple
        """
        errors = []
        
        linear_weights = fusion_config.get("linear_weights", {})
        interaction_weights = fusion_config.get("interaction_weights", {})
        
        for layer, weight in linear_weights.items():
            if weight < 0:
                errors.append(
                    f"Role {role}: Negative linear weight for {layer}: {weight}"
                )
        
        for interaction, weight in interaction_weights.items():
            if weight < 0:
                errors.append(
                    f"Role {role}: Negative interaction weight for {interaction}: {weight}"
                )
        
        linear_sum = sum(linear_weights.values())
        interaction_sum = sum(interaction_weights.values())
        total_sum = linear_sum + interaction_sum
        
        if abs(total_sum - 1.0) > self.EPSILON:
            errors.append(
                f"Role {role}: Fusion weights sum to {total_sum:.12f}, expected 1.0 ± {self.EPSILON}"
            )
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def validate_anti_universality(
        self,
        method_compatibility: dict[str, Any],
        method_id: str
    ) -> tuple[bool, list[str]]:
        """
        Validate anti-universality constraint: no method has maximal compatibility everywhere.
        
        Enforces: min(x_@q, x_@d, x_@p) < 0.9
        
        Args:
            method_compatibility: Compatibility scores with 'questions', 'dimensions', 'policies'
            method_id: Method identifier
        
        Returns:
            (is_valid, error_messages) tuple
        """
        errors = []
        
        question_scores = list(method_compatibility.get("questions", {}).values())
        dimension_scores = list(method_compatibility.get("dimensions", {}).values())
        policy_scores = list(method_compatibility.get("policies", {}).values())
        
        if not question_scores or not dimension_scores or not policy_scores:
            errors.append(
                f"Method {method_id}: Incomplete compatibility scores "
                f"(q={len(question_scores)}, d={len(dimension_scores)}, p={len(policy_scores)})"
            )
            return False, errors
        
        min_q = min(question_scores)
        min_d = min(dimension_scores)
        min_p = min(policy_scores)
        
        min_overall = min(min_q, min_d, min_p)
        
        if min_overall >= self.ANTI_UNIVERSALITY_THRESHOLD:
            errors.append(
                f"Method {method_id}: Anti-universality violation "
                f"(min(q={min_q:.3f}, d={min_d:.3f}, p={min_p:.3f}) = {min_overall:.3f} >= {self.ANTI_UNIVERSALITY_THRESHOLD})"
            )
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def validate_intrinsic_calibration(
        self,
        calibration_data: dict[str, Any],
        method_id: str
    ) -> tuple[bool, list[str]]:
        """
        Validate intrinsic calibration schema compliance.
        
        Checks:
        - Required keys present (b_theory, b_impl, b_deploy, status)
        - Scores in [0,1]
        - Status in {computed, pending, excluded, none}
        - Forbidden keys absent (_temp, _debug, internal_state)
        
        Args:
            calibration_data: Calibration data dictionary
            method_id: Method identifier
        
        Returns:
            (is_valid, error_messages) tuple
        """
        errors = []
        
        missing_keys = self.REQUIRED_INTRINSIC_KEYS - set(calibration_data.keys())
        if missing_keys:
            errors.append(
                f"Method {method_id}: Missing required keys: {sorted(missing_keys)}"
            )
        
        for key in ["b_theory", "b_impl", "b_deploy"]:
            if key in calibration_data:
                score = calibration_data[key]
                if not isinstance(score, (int, float)):
                    errors.append(
                        f"Method {method_id}: {key} must be numeric, got {type(score).__name__}"
                    )
                elif not (0.0 <= score <= 1.0):
                    errors.append(
                        f"Method {method_id}: {key}={score:.6f} out of bounds [0,1]"
                    )
        
        status = calibration_data.get("status")
        if status not in self.VALID_STATUSES:
            errors.append(
                f"Method {method_id}: Invalid status '{status}', must be one of {self.VALID_STATUSES}"
            )
        
        forbidden_present = self.FORBIDDEN_INTRINSIC_KEYS & set(calibration_data.keys())
        if forbidden_present:
            errors.append(
                f"Method {method_id}: Forbidden keys present: {sorted(forbidden_present)}"
            )
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def validate_boundedness(
        self,
        scores: dict[str, float],
        context: str
    ) -> tuple[bool, list[str]]:
        """
        Validate all scores are in [0,1].
        
        Args:
            scores: Dictionary of score_name -> score_value
            context: Context string for error messages
        
        Returns:
            (is_valid, error_messages) tuple
        """
        errors = []
        
        for name, score in scores.items():
            if not isinstance(score, (int, float)):
                errors.append(
                    f"{context}: Score '{name}' must be numeric, got {type(score).__name__}"
                )
            elif not (0.0 <= score <= 1.0):
                errors.append(
                    f"{context}: Score '{name}'={score:.6f} out of bounds [0,1]"
                )
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def validate_config_files(
        self,
        pillar: str = "all"
    ) -> dict[str, Any]:
        """
        Run all validation checks on three pillars (calibration/questionnaire/environments).
        
        Args:
            pillar: Which pillar to validate ('calibration', 'questionnaire', 'environments', 'all')
        
        Returns:
            Validation report dictionary with results per file
        """
        report = {
            "validation_summary": {
                "total_checks": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            },
            "results": {}
        }
        
        pillars_to_check = []
        if pillar in ("all", "calibration"):
            pillars_to_check.append("calibration")
        if pillar in ("all", "questionnaire"):
            pillars_to_check.append("questionnaire")
        if pillar in ("all", "environments"):
            pillars_to_check.append("environments")
        
        for current_pillar in pillars_to_check:
            if current_pillar == "calibration":
                self._validate_calibration_pillar(report)
            elif current_pillar == "questionnaire":
                self._validate_questionnaire_pillar(report)
            elif current_pillar == "environments":
                self._validate_environments_pillar(report)
        
        return report
    
    def _validate_calibration_pillar(self, report: dict[str, Any]) -> None:
        """Validate calibration configuration files."""
        intrinsic_cal = self.loader.load_calibration("intrinsic_calibration")
        fusion_weights = self.loader.load_calibration("fusion_weights")
        method_compat = self.loader.load_calibration("method_compatibility")
        
        report["results"]["intrinsic_calibration"] = self._validate_intrinsic_config(
            intrinsic_cal
        )
        
        report["results"]["fusion_weights"] = self._validate_fusion_config(
            fusion_weights
        )
        
        report["results"]["method_compatibility"] = self._validate_compatibility_config(
            method_compat
        )
        
        for result in report["results"].values():
            report["validation_summary"]["total_checks"] += result["total_checks"]
            report["validation_summary"]["passed"] += result["passed"]
            report["validation_summary"]["failed"] += result["failed"]
            report["validation_summary"]["warnings"] += result.get("warnings", 0)
    
    def _validate_questionnaire_pillar(self, report: dict[str, Any]) -> None:
        """Validate questionnaire monolith structure."""
        questionnaire = self.loader.load_calibration("questionnaire_monolith")
        
        result = {
            "file": "questionnaire_monolith",
            "total_checks": 1,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "errors": [],
            "warnings_list": []
        }
        
        if "_cohort_metadata" in questionnaire:
            if questionnaire["_cohort_metadata"].get("cohort_id") == "COHORT_2024":
                result["passed"] = 1
            else:
                result["failed"] = 1
                result["errors"].append("Invalid cohort_id in questionnaire_monolith")
        else:
            result["warnings"] = 1
            result["warnings_list"].append("Reference-only file, full validation skipped")
        
        report["results"]["questionnaire_monolith"] = result
        report["validation_summary"]["total_checks"] += result["total_checks"]
        report["validation_summary"]["passed"] += result["passed"]
        report["validation_summary"]["failed"] += result["failed"]
        report["validation_summary"]["warnings"] += result["warnings"]
    
    def _validate_environments_pillar(self, report: dict[str, Any]) -> None:
        """Validate environment configurations (placeholder for future implementation)."""
        result = {
            "file": "environments",
            "total_checks": 1,
            "passed": 0,
            "failed": 0,
            "warnings": 1,
            "errors": [],
            "warnings_list": ["Environment validation not implemented - parametrization only"]
        }
        
        report["results"]["environments"] = result
        report["validation_summary"]["total_checks"] += result["total_checks"]
        report["validation_summary"]["warnings"] += result["warnings"]
    
    def _validate_intrinsic_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """Validate intrinsic calibration configuration."""
        result = {
            "file": "intrinsic_calibration",
            "total_checks": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "details": {}
        }
        
        role_reqs = config.get("role_requirements", {})
        
        for role, requirements in role_reqs.items():
            result["total_checks"] += 1
            
            required_layers = set(requirements.get("required_layers", []))
            expected_layers = self.ROLE_REQUIRED_LAYERS.get(role, set())
            
            if required_layers == expected_layers:
                result["passed"] += 1
                result["details"][role] = "OK"
            else:
                result["failed"] += 1
                missing = expected_layers - required_layers
                extra = required_layers - expected_layers
                error_msg = f"Role {role}: "
                if missing:
                    error_msg += f"missing {sorted(missing)} "
                if extra:
                    error_msg += f"unexpected {sorted(extra)}"
                result["errors"].append(error_msg.strip())
                result["details"][role] = "FAILED"
        
        return result
    
    def _validate_fusion_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """Validate fusion weights configuration."""
        result = {
            "file": "fusion_weights",
            "total_checks": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "details": {}
        }
        
        role_params = config.get("role_fusion_parameters", {})
        
        if isinstance(role_params, dict) and "_note" in role_params:
            result["total_checks"] = 1
            result["passed"] = 0
            result["failed"] = 0
            result["errors"].append("Reference-only file, full fusion data not present")
            result["details"]["status"] = "REFERENCE_ONLY"
            return result
        
        for role, params in role_params.items():
            if role.startswith("_"):
                continue
            
            result["total_checks"] += 1
            is_valid, errors = self.validate_fusion_weights(params, role)
            
            if is_valid:
                result["passed"] += 1
                result["details"][role] = "OK"
            else:
                result["failed"] += 1
                result["errors"].extend(errors)
                result["details"][role] = "FAILED"
        
        return result
    
    def _validate_compatibility_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """Validate method compatibility configuration."""
        result = {
            "file": "method_compatibility",
            "total_checks": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "details": {}
        }
        
        method_compat = config.get("method_compatibility", {})
        
        for method_id, compat_data in method_compat.items():
            result["total_checks"] += 1
            is_valid, errors = self.validate_anti_universality(compat_data, method_id)
            
            if is_valid:
                result["passed"] += 1
                result["details"][method_id] = "OK"
            else:
                result["failed"] += 1
                result["errors"].extend(errors)
                result["details"][method_id] = "FAILED"
        
        return result
    
    def generate_validation_report(
        self,
        report: dict[str, Any],
        output_path: Path | str,
        format: str = "detailed"
    ) -> None:
        """
        Generate and save comprehensive validation report.
        
        Args:
            report: Validation report from validate_config_files()
            output_path: Path to save report (JSON or TXT)
            format: Report format ('detailed' or 'summary')
        """
        import json
        from datetime import datetime, timezone
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        summary = report["validation_summary"]
        
        if format == "summary":
            report_content = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "summary": summary,
                "status": "PASSED" if summary["failed"] == 0 else "FAILED",
                "critical_failures": [
                    f"{file}: {len(result.get('errors', []))} errors"
                    for file, result in report["results"].items()
                    if result.get("failed", 0) > 0
                ]
            }
        else:
            report_content = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "summary": summary,
                "status": "PASSED" if summary["failed"] == 0 else "FAILED",
                "results": report["results"]
            }
        
        if output_file.suffix == ".json":
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(report_content, f, indent=2, ensure_ascii=False)
        else:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("=" * 80 + "\n")
                f.write("CALIBRATION VALIDATION REPORT\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Generated: {report_content['timestamp']}\n")
                f.write(f"Status: {report_content['status']}\n\n")
                
                f.write("SUMMARY\n")
                f.write("-" * 80 + "\n")
                f.write(f"Total Checks: {summary['total_checks']}\n")
                f.write(f"Passed:       {summary['passed']}\n")
                f.write(f"Failed:       {summary['failed']}\n")
                f.write(f"Warnings:     {summary['warnings']}\n\n")
                
                if format == "detailed":
                    f.write("DETAILED RESULTS\n")
                    f.write("-" * 80 + "\n\n")
                    
                    for file, result in report["results"].items():
                        f.write(f"File: {file}\n")
                        f.write(f"  Checks: {result['total_checks']}\n")
                        f.write(f"  Passed: {result['passed']}\n")
                        f.write(f"  Failed: {result['failed']}\n")
                        
                        if result.get("errors"):
                            f.write("  Errors:\n")
                            for error in result["errors"]:
                                f.write(f"    - {error}\n")
                        
                        if result.get("warnings_list"):
                            f.write("  Warnings:\n")
                            for warning in result["warnings_list"]:
                                f.write(f"    - {warning}\n")
                        
                        f.write("\n")


def validate_all_pillars() -> dict[str, Any]:
    """
    Convenience function to validate all three pillars.
    
    Returns:
        Validation report dictionary
    """
    validator = CalibrationValidator()
    return validator.validate_config_files(pillar="all")

"""
Certificate Validation and Analysis Utilities
==============================================

Provides utilities for validating, analyzing, and comparing calibration certificates.

Features:
- Deep validation of certificate structure and values
- Certificate comparison and diff analysis
- Statistical analysis of certificate collections
- Audit trail reconstruction
- Anomaly detection

Version: 1.0.0
Created: 2024-12-15
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from certificate_generator import CalibrationCertificate, CertificateGenerator

__all__ = [
    "CertificateValidator",
    "CertificateAnalyzer",
    "CertificateComparator",
    "ValidationReport",
]


@dataclass
class ValidationReport:
    is_valid: bool
    errors: list[str]
    warnings: list[str]
    info: dict[str, Any]


class CertificateValidator:
    def __init__(self):
        self.generator = CertificateGenerator()

    def validate_certificate(self, certificate: CalibrationCertificate) -> ValidationReport:
        errors = []
        warnings = []
        info = {}

        if not self.generator.verify_certificate(certificate):
            errors.append("Certificate signature is invalid - certificate may have been tampered with")

        boundedness_errors = self._validate_boundedness(certificate)
        errors.extend(boundedness_errors)

        monotonicity_errors = self._validate_monotonicity(certificate)
        errors.extend(monotonicity_errors)

        normalization_errors = self._validate_normalization(certificate)
        errors.extend(normalization_errors)

        completeness_warnings = self._validate_completeness(certificate)
        warnings.extend(completeness_warnings)

        computation_errors = self._validate_computation(certificate)
        errors.extend(computation_errors)

        info["total_layers"] = len(certificate.layer_scores)
        info["total_parameters"] = len(certificate.parameter_provenance)
        info["computation_steps"] = len(certificate.fusion_formula.computation_trace)

        is_valid = len(errors) == 0

        return ValidationReport(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            info=info,
        )

    def _validate_boundedness(self, certificate: CalibrationCertificate) -> list[str]:
        errors = []

        if not (0.0 <= certificate.intrinsic_score <= 1.0):
            errors.append(f"Intrinsic score {certificate.intrinsic_score} is out of bounds [0,1]")

        for layer, score in certificate.layer_scores.items():
            if not (0.0 <= score <= 1.0):
                errors.append(f"Layer score {layer}={score} is out of bounds [0,1]")

        if not (0.0 <= certificate.calibrated_score <= 1.0):
            errors.append(f"Calibrated score {certificate.calibrated_score} is out of bounds [0,1]")

        return errors

    def _validate_monotonicity(self, certificate: CalibrationCertificate) -> list[str]:
        errors = []

        for param_name, prov in certificate.parameter_provenance.items():
            if prov.value < 0.0:
                errors.append(f"Parameter {param_name}={prov.value} is negative (violates monotonicity)")

        return errors

    def _validate_normalization(self, certificate: CalibrationCertificate) -> list[str]:
        errors = []

        linear_sum = 0.0
        interaction_sum = 0.0

        for param_name, prov in certificate.parameter_provenance.items():
            if "," in param_name:
                interaction_sum += prov.value
            else:
                linear_sum += prov.value

        total_sum = linear_sum + interaction_sum

        if abs(total_sum - 1.0) > 0.01:
            errors.append(
                f"Weights do not sum to 1.0: linear={linear_sum:.4f}, "
                f"interaction={interaction_sum:.4f}, total={total_sum:.4f}"
            )

        return errors

    def _validate_completeness(self, certificate: CalibrationCertificate) -> list[str]:
        warnings = []

        if not certificate.validation_checks.completeness["is_complete"]:
            missing = certificate.validation_checks.completeness["missing_layers"]
            warnings.append(f"Missing required layers: {missing}")

        if not certificate.validation_checks.completeness["has_no_extras"]:
            extra = certificate.validation_checks.completeness["extra_layers"]
            warnings.append(f"Extra layers present: {extra}")

        return warnings

    def _validate_computation(self, certificate: CalibrationCertificate) -> list[str]:
        errors = []

        trace = certificate.fusion_formula.computation_trace
        if not trace:
            errors.append("Computation trace is empty")
            return errors

        final_step = trace[-1]
        if final_step.get("operation") != "final_calibrated_score":
            errors.append("Final computation step is missing or malformed")

        computed_score = final_step.get("result", 0.0)
        if abs(computed_score - certificate.calibrated_score) > 0.0001:
            errors.append(
                f"Calibrated score mismatch: certificate={certificate.calibrated_score:.4f}, "
                f"computed={computed_score:.4f}"
            )

        return errors


class CertificateAnalyzer:
    @staticmethod
    def analyze_certificate(certificate: CalibrationCertificate) -> dict[str, Any]:
        analysis = {
            "basic_info": {
                "instance_id": certificate.instance_id,
                "method_id": certificate.method_id,
                "timestamp": certificate.timestamp,
                "certificate_version": certificate.certificate_version,
            },
            "scores": {
                "intrinsic_score": certificate.intrinsic_score,
                "calibrated_score": certificate.calibrated_score,
                "adjustment": certificate.calibrated_score - certificate.intrinsic_score,
                "adjustment_pct": (
                    (certificate.calibrated_score - certificate.intrinsic_score) / certificate.intrinsic_score * 100
                    if certificate.intrinsic_score > 0 else 0
                ),
            },
            "layer_statistics": CertificateAnalyzer._analyze_layers(certificate),
            "weight_statistics": CertificateAnalyzer._analyze_weights(certificate),
            "computation_complexity": {
                "total_steps": len(certificate.fusion_formula.computation_trace),
                "linear_terms": sum(1 for p in certificate.parameter_provenance if "," not in p),
                "interaction_terms": sum(1 for p in certificate.parameter_provenance if "," in p),
            },
            "validation_summary": {
                "all_bounded": certificate.validation_checks.boundedness["all_bounded"],
                "all_monotonic": certificate.validation_checks.monotonicity["all_weights_non_negative"],
                "normalized": certificate.validation_checks.normalization["is_normalized"],
                "complete": certificate.validation_checks.completeness["is_complete"],
            },
        }

        return analysis

    @staticmethod
    def _analyze_layers(certificate: CalibrationCertificate) -> dict[str, Any]:
        scores = list(certificate.layer_scores.values())

        return {
            "count": len(scores),
            "mean": sum(scores) / len(scores) if scores else 0,
            "min": min(scores) if scores else 0,
            "max": max(scores) if scores else 0,
            "range": max(scores) - min(scores) if scores else 0,
            "layers": certificate.layer_scores,
        }

    @staticmethod
    def _analyze_weights(certificate: CalibrationCertificate) -> dict[str, Any]:
        linear_weights = {}
        interaction_weights = {}

        for param_name, prov in certificate.parameter_provenance.items():
            if "," in param_name:
                interaction_weights[param_name] = prov.value
            else:
                linear_weights[param_name] = prov.value

        linear_values = list(linear_weights.values())
        interaction_values = list(interaction_weights.values())

        return {
            "linear": {
                "count": len(linear_weights),
                "sum": sum(linear_values),
                "mean": sum(linear_values) / len(linear_values) if linear_values else 0,
                "weights": linear_weights,
            },
            "interaction": {
                "count": len(interaction_weights),
                "sum": sum(interaction_values),
                "mean": sum(interaction_values) / len(interaction_values) if interaction_values else 0,
                "weights": interaction_weights,
            },
        }


class CertificateComparator:
    @staticmethod
    def compare_certificates(
        cert1: CalibrationCertificate,
        cert2: CalibrationCertificate,
    ) -> dict[str, Any]:
        comparison = {
            "metadata": {
                "cert1_id": cert1.instance_id,
                "cert2_id": cert2.instance_id,
                "same_method": cert1.method_id == cert2.method_id,
                "timestamp_diff": cert1.timestamp != cert2.timestamp,
            },
            "score_comparison": {
                "intrinsic_score_diff": cert2.intrinsic_score - cert1.intrinsic_score,
                "calibrated_score_diff": cert2.calibrated_score - cert1.calibrated_score,
                "cert1_scores": {
                    "intrinsic": cert1.intrinsic_score,
                    "calibrated": cert1.calibrated_score,
                },
                "cert2_scores": {
                    "intrinsic": cert2.intrinsic_score,
                    "calibrated": cert2.calibrated_score,
                },
            },
            "layer_comparison": CertificateComparator._compare_layers(cert1, cert2),
            "weight_comparison": CertificateComparator._compare_weights(cert1, cert2),
            "config_comparison": {
                "same_config": cert1.config_hash == cert2.config_hash,
                "same_graph": cert1.graph_hash == cert2.graph_hash,
                "cert1_config_hash": cert1.config_hash[:16] + "...",
                "cert2_config_hash": cert2.config_hash[:16] + "...",
            },
        }

        return comparison

    @staticmethod
    def _compare_layers(
        cert1: CalibrationCertificate,
        cert2: CalibrationCertificate,
    ) -> dict[str, Any]:
        all_layers = set(cert1.layer_scores.keys()) | set(cert2.layer_scores.keys())

        layer_diffs: dict[str, Any] = {}
        for layer in sorted(all_layers):
            score1 = cert1.layer_scores.get(layer)
            score2 = cert2.layer_scores.get(layer)

            if score1 is not None and score2 is not None:
                layer_diffs[layer] = {
                    "cert1": score1,
                    "cert2": score2,
                    "diff": score2 - score1,
                    "pct_change": ((score2 - score1) / score1 * 100) if score1 > 0 else 0,
                }
            elif score1 is not None:
                layer_diffs[layer] = {"cert1": score1, "cert2": None, "status": "removed"}
            else:
                layer_diffs[layer] = {"cert1": None, "cert2": score2, "status": "added"}

        return layer_diffs

    @staticmethod
    def _compare_weights(
        cert1: CalibrationCertificate,
        cert2: CalibrationCertificate,
    ) -> dict[str, Any]:
        all_params = set(cert1.parameter_provenance.keys()) | set(cert2.parameter_provenance.keys())

        weight_diffs: dict[str, Any] = {}
        for param in sorted(all_params):
            prov1 = cert1.parameter_provenance.get(param)
            prov2 = cert2.parameter_provenance.get(param)

            if prov1 and prov2:
                weight_diffs[param] = {
                    "cert1": prov1.value,
                    "cert2": prov2.value,
                    "diff": prov2.value - prov1.value,
                    "same": prov1.value == prov2.value,
                }
            elif prov1:
                weight_diffs[param] = {"cert1": prov1.value, "cert2": None, "status": "removed"}
            elif prov2:
                weight_diffs[param] = {"cert1": None, "cert2": prov2.value, "status": "added"}

        return weight_diffs


def load_certificate_from_json(json_path: Path) -> CalibrationCertificate:
    with open(json_path) as f:
        data = json.load(f)

    from certificate_generator import FusionFormula, ParameterProvenance, ValidationChecks

    fusion_formula = FusionFormula(**data["fusion_formula"])

    parameter_provenance = {
        k: ParameterProvenance(**v) for k, v in data["parameter_provenance"].items()
    }

    validation_checks = ValidationChecks(**data["validation_checks"])

    return CalibrationCertificate(
        certificate_version=data["certificate_version"],
        instance_id=data["instance_id"],
        method_id=data["method_id"],
        node_id=data["node_id"],
        context=data["context"],
        intrinsic_score=data["intrinsic_score"],
        layer_scores=data["layer_scores"],
        calibrated_score=data["calibrated_score"],
        fusion_formula=fusion_formula,
        parameter_provenance=parameter_provenance,
        evidence_trail=data["evidence_trail"],
        config_hash=data["config_hash"],
        graph_hash=data["graph_hash"],
        validation_checks=validation_checks,
        timestamp=data["timestamp"],
        validator_version=data["validator_version"],
        signature=data["signature"],
    )

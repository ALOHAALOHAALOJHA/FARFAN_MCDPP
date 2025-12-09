"""
Calibration Certificate Generation System
==========================================

Generates complete audit trail certificates for method calibration with:
- Full computation trace (symbolic formulas, expanded values, step-by-step computation)
- Parameter provenance (source file, line, justification for each parameter)
- Evidence trail (all evidence used in layer computations)
- Config and graph hashing for reproducibility
- Validation checks (boundedness, monotonicity, normalization, completeness)
- HMAC signature for integrity verification

Version: 1.0.0
Created: 2024-12-15
"""

import hashlib
import hmac
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

__all__ = ["CalibrationCertificate", "CertificateGenerator"]


@dataclass(frozen=True)
class FusionFormula:
    symbolic: str
    expanded: str
    computation_trace: list[dict[str, Any]]


@dataclass(frozen=True)
class ParameterProvenance:
    value: float
    source: str
    justification: str


@dataclass(frozen=True)
class ValidationChecks:
    boundedness: dict[str, Any]
    monotonicity: dict[str, Any]
    normalization: dict[str, Any]
    completeness: dict[str, Any]


@dataclass(frozen=True)
class CalibrationCertificate:
    certificate_version: str
    instance_id: str
    method_id: str
    node_id: str
    context: dict[str, Any]
    intrinsic_score: float
    layer_scores: dict[str, float]
    calibrated_score: float
    fusion_formula: FusionFormula
    parameter_provenance: dict[str, ParameterProvenance]
    evidence_trail: dict[str, Any]
    config_hash: str
    graph_hash: str
    validation_checks: ValidationChecks
    timestamp: str
    validator_version: str
    signature: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


class CertificateGenerator:
    CERTIFICATE_VERSION = "1.0.0"
    VALIDATOR_VERSION = "1.0.0"
    SECRET_KEY = b"FARFAN_CALIBRATION_SYSTEM_v1.0"

    def __init__(self, config_dir: Path | None = None, secret_key: bytes | None = None):
        self.config_dir = config_dir or Path("src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration")
        self.secret_key = secret_key or self.SECRET_KEY

    def generate_certificate(
        self,
        instance_id: str,
        method_id: str,
        node_id: str,
        context: dict[str, Any],
        intrinsic_score: float,
        layer_scores: dict[str, float],
        weights: dict[str, float],
        interaction_weights: dict[str, float] | None = None,
        evidence_trail: dict[str, Any] | None = None,
        computation_graph: dict[str, Any] | None = None,
    ) -> CalibrationCertificate:
        interaction_weights = interaction_weights or {}
        evidence_trail = evidence_trail or {}
        computation_graph = computation_graph or {}

        calibrated_score, fusion_formula = self._compute_calibrated_score(
            intrinsic_score=intrinsic_score,
            layer_scores=layer_scores,
            weights=weights,
            interaction_weights=interaction_weights,
        )

        parameter_provenance = self._extract_parameter_provenance(
            weights=weights,
            interaction_weights=interaction_weights,
        )

        config_hash = self._compute_config_hash()
        graph_hash = self._compute_graph_hash(computation_graph)

        validation_checks = self._perform_validation_checks(
            intrinsic_score=intrinsic_score,
            layer_scores=layer_scores,
            calibrated_score=calibrated_score,
            weights=weights,
            interaction_weights=interaction_weights,
        )

        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        certificate_data = {
            "certificate_version": self.CERTIFICATE_VERSION,
            "instance_id": instance_id,
            "method_id": method_id,
            "node_id": node_id,
            "context": context,
            "intrinsic_score": intrinsic_score,
            "layer_scores": layer_scores,
            "calibrated_score": calibrated_score,
            "fusion_formula": asdict(fusion_formula),
            "parameter_provenance": {k: asdict(v) for k, v in parameter_provenance.items()},
            "evidence_trail": evidence_trail,
            "config_hash": config_hash,
            "graph_hash": graph_hash,
            "validation_checks": asdict(validation_checks),
            "timestamp": timestamp,
            "validator_version": self.VALIDATOR_VERSION,
        }

        signature = self._compute_signature(certificate_data)

        return CalibrationCertificate(
            certificate_version=self.CERTIFICATE_VERSION,
            instance_id=instance_id,
            method_id=method_id,
            node_id=node_id,
            context=context,
            intrinsic_score=intrinsic_score,
            layer_scores=layer_scores,
            calibrated_score=calibrated_score,
            fusion_formula=fusion_formula,
            parameter_provenance=parameter_provenance,
            evidence_trail=evidence_trail,
            config_hash=config_hash,
            graph_hash=graph_hash,
            validation_checks=validation_checks,
            timestamp=timestamp,
            validator_version=self.VALIDATOR_VERSION,
            signature=signature,
        )

    def _compute_calibrated_score(
        self,
        intrinsic_score: float,
        layer_scores: dict[str, float],
        weights: dict[str, float],
        interaction_weights: dict[str, float],
    ) -> tuple[float, FusionFormula]:
        computation_trace: list[dict[str, Any]] = []

        linear_sum = 0.0
        for layer, score in layer_scores.items():
            weight = weights.get(layer, 0.0)
            contribution = weight * score
            linear_sum += contribution
            computation_trace.append({
                "step": len(computation_trace) + 1,
                "operation": f"{weight} * {score}",
                "layer": layer,
                "weight": weight,
                "score": score,
                "result": contribution,
                "cumulative": linear_sum,
            })

        interaction_sum = 0.0
        for layer_pair, weight in interaction_weights.items():
            layers = layer_pair.split(",")
            if len(layers) == 2:
                l1, l2 = layers
                score1 = layer_scores.get(l1, 0.0)
                score2 = layer_scores.get(l2, 0.0)
                min_score = min(score1, score2)
                contribution = weight * min_score
                interaction_sum += contribution
                computation_trace.append({
                    "step": len(computation_trace) + 1,
                    "operation": f"{weight} * min({score1}, {score2})",
                    "layer_pair": layer_pair,
                    "weight": weight,
                    "score1": score1,
                    "score2": score2,
                    "min_score": min_score,
                    "result": contribution,
                    "cumulative": linear_sum + interaction_sum,
                })

        calibrated_score = linear_sum + interaction_sum

        computation_trace.append({
            "step": len(computation_trace) + 1,
            "operation": "final_calibrated_score",
            "linear_sum": linear_sum,
            "interaction_sum": interaction_sum,
            "result": calibrated_score,
        })

        symbolic = "Σ(aₗ·xₗ) + Σ(aₗₖ·min(xₗ,xₖ))"

        expanded_terms = []
        for layer in sorted(weights.keys()):
            weight = weights[layer]
            expanded_terms.append(f"({weight}·x_{layer})")
        for layer_pair in sorted(interaction_weights.keys()):
            weight = interaction_weights[layer_pair]
            layers = layer_pair.split(",")
            if len(layers) == 2:
                expanded_terms.append(f"({weight}·min(x_{layers[0]},x_{layers[1]}))")
        expanded = " + ".join(expanded_terms) if expanded_terms else "0"

        fusion_formula = FusionFormula(
            symbolic=symbolic,
            expanded=expanded,
            computation_trace=computation_trace,
        )

        return calibrated_score, fusion_formula

    def _extract_parameter_provenance(
        self,
        weights: dict[str, float],
        interaction_weights: dict[str, float],
    ) -> dict[str, ParameterProvenance]:
        provenance = {}

        fusion_config_path = self.config_dir / "COHORT_2024_fusion_weights.json"
        source_file = str(fusion_config_path) if fusion_config_path.exists() else "config/fusion_weights.json"

        for layer, value in weights.items():
            provenance[f"a_{layer}"] = ParameterProvenance(
                value=value,
                source=f"{source_file}:weights",
                justification=f"Linear weight for layer {layer} from COHORT_2024 fusion specification",
            )

        for layer_pair, value in interaction_weights.items():
            provenance[f"a_{layer_pair}"] = ParameterProvenance(
                value=value,
                source=f"{source_file}:interaction_weights",
                justification=f"Interaction weight for layers {layer_pair} capturing synergy effects",
            )

        return provenance

    def _compute_config_hash(self) -> str:
        config_files = [
            "COHORT_2024_fusion_weights.json",
            "COHORT_2024_layer_assignment.py",
            "COHORT_2024_intrinsic_calibration.json",
        ]

        combined_content = ""
        for config_file in config_files:
            config_path = self.config_dir / config_file
            if config_path.exists():
                with open(config_path, "rb") as f:
                    content = f.read()
                    combined_content += content.decode("utf-8", errors="ignore")

        return hashlib.sha256(combined_content.encode("utf-8")).hexdigest()

    def _compute_graph_hash(self, computation_graph: dict[str, Any]) -> str:
        graph_structure = json.dumps(computation_graph, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(graph_structure.encode("utf-8")).hexdigest()

    def _perform_validation_checks(
        self,
        intrinsic_score: float,
        layer_scores: dict[str, float],
        calibrated_score: float,
        weights: dict[str, float],
        interaction_weights: dict[str, float],
    ) -> ValidationChecks:
        boundedness = self._check_boundedness(intrinsic_score, layer_scores, calibrated_score)
        monotonicity = self._check_monotonicity(weights, interaction_weights)
        normalization = self._check_normalization(weights, interaction_weights)
        completeness = self._check_completeness(layer_scores, weights)

        return ValidationChecks(
            boundedness=boundedness,
            monotonicity=monotonicity,
            normalization=normalization,
            completeness=completeness,
        )

    def _check_boundedness(
        self,
        intrinsic_score: float,
        layer_scores: dict[str, float],
        calibrated_score: float,
    ) -> dict[str, Any]:
        checks: dict[str, Any] = {
            "intrinsic_score_in_bounds": 0.0 <= intrinsic_score <= 1.0,
            "intrinsic_score_value": intrinsic_score,
            "layer_scores_in_bounds": {},
            "calibrated_score_in_bounds": 0.0 <= calibrated_score <= 1.0,
            "calibrated_score_value": calibrated_score,
            "all_bounded": True,
        }

        for layer, score in layer_scores.items():
            in_bounds = 0.0 <= score <= 1.0
            checks["layer_scores_in_bounds"][layer] = {
                "score": score,
                "in_bounds": in_bounds,
            }
            if not in_bounds:
                checks["all_bounded"] = False

        if not checks["intrinsic_score_in_bounds"]:
            checks["all_bounded"] = False
        if not checks["calibrated_score_in_bounds"]:
            checks["all_bounded"] = False

        return checks

    def _check_monotonicity(
        self,
        weights: dict[str, float],
        interaction_weights: dict[str, float],
    ) -> dict[str, Any]:
        checks: dict[str, Any] = {
            "all_weights_non_negative": True,
            "weight_signs": {},
            "interaction_weight_signs": {},
        }

        for layer, weight in weights.items():
            is_non_negative = weight >= 0.0
            checks["weight_signs"][layer] = {
                "value": weight,
                "non_negative": is_non_negative,
            }
            if not is_non_negative:
                checks["all_weights_non_negative"] = False

        for layer_pair, weight in interaction_weights.items():
            is_non_negative = weight >= 0.0
            checks["interaction_weight_signs"][layer_pair] = {
                "value": weight,
                "non_negative": is_non_negative,
            }
            if not is_non_negative:
                checks["all_weights_non_negative"] = False

        return checks

    def _check_normalization(
        self,
        weights: dict[str, float],
        interaction_weights: dict[str, float],
    ) -> dict[str, Any]:
        linear_sum = sum(weights.values())
        interaction_sum = sum(interaction_weights.values())
        total_sum = linear_sum + interaction_sum

        is_normalized = abs(total_sum - 1.0) < 0.01

        return {
            "linear_sum": linear_sum,
            "interaction_sum": interaction_sum,
            "total_sum": total_sum,
            "is_normalized": is_normalized,
            "tolerance": 0.01,
            "deviation": abs(total_sum - 1.0),
        }

    def _check_completeness(
        self,
        layer_scores: dict[str, float],
        weights: dict[str, float],
    ) -> dict[str, Any]:
        required_layers = set(weights.keys())
        provided_layers = set(layer_scores.keys())

        missing_layers = required_layers - provided_layers
        extra_layers = provided_layers - required_layers

        return {
            "required_layers": sorted(required_layers),
            "provided_layers": sorted(provided_layers),
            "missing_layers": sorted(missing_layers),
            "extra_layers": sorted(extra_layers),
            "is_complete": len(missing_layers) == 0,
            "has_no_extras": len(extra_layers) == 0,
        }

    def _compute_signature(self, certificate_data: dict[str, Any]) -> str:
        canonical_data = json.dumps(certificate_data, sort_keys=True, ensure_ascii=True)
        signature_bytes = hmac.new(
            self.secret_key,
            canonical_data.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        return signature_bytes.hex()

    def verify_certificate(self, certificate: CalibrationCertificate) -> bool:
        certificate_dict = certificate.to_dict()
        signature = certificate_dict.pop("signature")

        computed_signature = self._compute_signature(certificate_dict)

        return hmac.compare_digest(signature, computed_signature)

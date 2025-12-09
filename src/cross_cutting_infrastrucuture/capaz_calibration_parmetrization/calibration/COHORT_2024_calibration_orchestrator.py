"""
COHORT_2024 - REFACTOR_WAVE_2024_12
Created: 2024-12-15T00:00:00+00:00
Wave: GOVERNANCE_WAVE_2024_12_07
Label: CONFIG_GOVERNANCE_STRICT_FOLDERIZATION

SENSITIVE - CALIBRATION SYSTEM CRITICAL

CalibrationOrchestrator Implementation

Orchestrates complete calibration workflow:
- Layer requirement determination via LAYER_REQUIREMENTS role mapping
- Active layer score computation (base, contextual, unit, meta)
- Choquet integral fusion with interaction terms
- Boundedness validation [0.0-1.0]
- Certificate metadata generation

Authority: Doctrina SIN_CARRETA
Compliance: SUPERPROMPT Three-Pillar Calibration System
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypedDict

from .COHORT_2024_layer_assignment import LAYER_REQUIREMENTS


class CalibrationContext(TypedDict, total=False):
    question_id: str | None
    dimension_id: str | None
    policy_area_id: str | None


class CalibrationEvidence(TypedDict, total=False):
    intrinsic_scores: dict[str, float]
    compatibility_registry: dict[str, dict[str, float]]
    pdt_structure: dict[str, Any]
    governance_artifacts: dict[str, Any]


class LayerScores(TypedDict):
    b: float
    chain: float
    q: float
    d: float
    p: float
    C: float
    u: float
    m: float


class CalibrationResult(TypedDict):
    method_id: str
    role: str
    final_score: float
    layer_scores: dict[str, float]
    active_layers: list[str]
    fusion_breakdown: dict[str, Any]
    certificate_metadata: dict[str, Any]
    validation: dict[str, Any]


@dataclass(frozen=True)
class FusionWeights:
    linear_weights: dict[str, float]
    interaction_weights: dict[tuple[str, str], float]
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FusionWeights:
        linear = data.get("linear_weights", {})
        
        interaction_raw = data.get("interaction_weights", {})
        interaction = {}
        for key, value in interaction_raw.items():
            if isinstance(key, str):
                key = key.strip("()").replace(" ", "")
                parts = key.split(",")
                if len(parts) == 2:
                    interaction[(parts[0], parts[1])] = value
            elif isinstance(key, tuple) and len(key) == 2:
                interaction[key] = value
        
        return cls(linear_weights=linear, interaction_weights=interaction)


class CalibrationOrchestrator:
    
    def __init__(self, fusion_weights_path: str | None = None):
        if fusion_weights_path is None:
            base_path = Path(__file__).parent
            fusion_weights_path = str(base_path / "COHORT_2024_fusion_weights.json")
        
        self.fusion_weights_path = fusion_weights_path
        self._fusion_weights: FusionWeights | None = None
        self._intrinsic_calibration: dict[str, Any] | None = None
    
    def _load_fusion_weights(self) -> FusionWeights:
        if self._fusion_weights is None:
            fallback_path = Path(__file__).parent / "fusion_weights.json"
            
            try:
                with open(self.fusion_weights_path) as f:
                    data = json.load(f)
                if not data.get("linear_weights"):
                    with open(fallback_path) as f:
                        data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                with open(fallback_path) as f:
                    data = json.load(f)
            
            self._fusion_weights = FusionWeights.from_dict(data)
        
        return self._fusion_weights
    
    def _load_intrinsic_calibration(self) -> dict[str, Any]:
        if self._intrinsic_calibration is None:
            path = Path(__file__).parent / "COHORT_2024_intrinsic_calibration.json"
            with open(path) as f:
                self._intrinsic_calibration = json.load(f)
        return self._intrinsic_calibration
    
    def _load_method_compatibility(self) -> dict[str, Any]:
        path = Path(__file__).parent / "COHORT_2024_method_compatibility.json"
        with open(path) as f:
            return json.load(f)
    
    def _determine_role(self, method_id: str) -> str:
        parts = method_id.lower()
        
        if "executor" in parts:
            return "executor"
        elif "ingest" in parts:
            return "ingest"
        elif "processor" in parts or "process" in parts:
            return "processor"
        elif "analyzer" in parts or "analyse" in parts or "analyze" in parts:
            return "analyzer"
        elif "score" in parts or "scoring" in parts:
            return "score"
        elif "orchestrator" in parts or "orchestration" in parts:
            return "orchestrator"
        elif "extractor" in parts or "extract" in parts:
            return "extractor"
        elif "utility" in parts or "util" in parts:
            return "utility"
        else:
            return "core"
    
    def _get_required_layers(self, method_id: str) -> list[str]:
        role = self._determine_role(method_id)
        
        if role not in LAYER_REQUIREMENTS:
            return LAYER_REQUIREMENTS["core"]
        
        return LAYER_REQUIREMENTS[role]
    
    def _compute_base_layer_score(
        self, method_id: str, evidence: CalibrationEvidence
    ) -> float:
        intrinsic_scores = evidence.get("intrinsic_scores", {})
        
        if "base_layer_score" in intrinsic_scores:
            return intrinsic_scores["base_layer_score"]
        
        if "b_theory" in intrinsic_scores and "b_impl" in intrinsic_scores and "b_deploy" in intrinsic_scores:
            return (
                0.40 * intrinsic_scores["b_theory"] +
                0.35 * intrinsic_scores["b_impl"] +
                0.25 * intrinsic_scores["b_deploy"]
            )
        
        return 0.5
    
    def _compute_contextual_layer_scores(
        self, method_id: str, context: CalibrationContext, evidence: CalibrationEvidence
    ) -> dict[str, float]:
        scores = {}
        
        compatibility_registry = evidence.get("compatibility_registry", {})
        
        method_base_id = method_id.split(".")[-1] if "." in method_id else method_id
        method_compat = compatibility_registry.get(method_base_id, {})
        
        if context.get("question_id") and "questions" in method_compat:
            q_scores = method_compat["questions"]
            scores["q"] = q_scores.get(context["question_id"], 0.5)
        else:
            scores["q"] = 0.5
        
        if context.get("dimension_id") and "dimensions" in method_compat:
            d_scores = method_compat["dimensions"]
            scores["d"] = d_scores.get(context["dimension_id"], 0.5)
        else:
            scores["d"] = 0.5
        
        if context.get("policy_area_id") and "policies" in method_compat:
            p_scores = method_compat["policies"]
            scores["p"] = p_scores.get(context["policy_area_id"], 0.5)
        else:
            scores["p"] = 0.5
        
        return scores
    
    def _compute_chain_layer_score(
        self, method_id: str, evidence: CalibrationEvidence
    ) -> float:
        intrinsic_scores = evidence.get("intrinsic_scores", {})
        
        if "chain_layer_score" in intrinsic_scores:
            return intrinsic_scores["chain_layer_score"]
        
        return 0.7
    
    def _compute_contract_layer_score(
        self, method_id: str, evidence: CalibrationEvidence
    ) -> float:
        intrinsic_scores = evidence.get("intrinsic_scores", {})
        
        if "contract_layer_score" in intrinsic_scores:
            return intrinsic_scores["contract_layer_score"]
        
        return 0.8
    
    def _compute_unit_layer_score(
        self, method_id: str, evidence: CalibrationEvidence
    ) -> float:
        pdt_structure = evidence.get("pdt_structure", {})
        
        if not pdt_structure:
            return 0.5
        
        total_tokens = pdt_structure.get("total_tokens", 0)
        blocks_found = pdt_structure.get("blocks_found", {})
        indicator_present = pdt_structure.get("indicator_matrix_present", False)
        ppi_present = pdt_structure.get("ppi_matrix_present", False)
        
        structure_score = min(len(blocks_found) / 4.0, 1.0)
        
        token_score = 0.0
        if total_tokens >= 10000:
            token_score = 1.0
        elif total_tokens >= 5000:
            token_score = 0.7
        elif total_tokens >= 2000:
            token_score = 0.5
        else:
            token_score = 0.3
        
        matrix_score = 0.0
        if indicator_present and ppi_present:
            matrix_score = 1.0
        elif indicator_present or ppi_present:
            matrix_score = 0.6
        else:
            matrix_score = 0.2
        
        return 0.40 * structure_score + 0.30 * token_score + 0.30 * matrix_score
    
    def _compute_meta_layer_score(
        self, method_id: str, evidence: CalibrationEvidence
    ) -> float:
        governance_artifacts = evidence.get("governance_artifacts", {})
        
        if not governance_artifacts:
            return 0.5
        
        version_tag = governance_artifacts.get("version_tag", "")
        config_hash = governance_artifacts.get("config_hash", "")
        signature = governance_artifacts.get("signature", "")
        
        governance_score = 0.0
        count = 0
        
        if version_tag and version_tag not in ["unknown", "1.0", "0.0.0"]:
            count += 1
        
        if config_hash and len(config_hash) == 64:
            count += 1
        
        if signature and len(signature) >= 32:
            count += 1
        
        if count == 3:
            governance_score = 1.0
        elif count == 2:
            governance_score = 0.66
        elif count == 1:
            governance_score = 0.33
        else:
            governance_score = 0.0
        
        return governance_score
    
    def _compute_all_layer_scores(
        self, method_id: str, context: CalibrationContext, evidence: CalibrationEvidence
    ) -> LayerScores:
        scores: LayerScores = {
            "b": self._compute_base_layer_score(method_id, evidence),
            "chain": self._compute_chain_layer_score(method_id, evidence),
            "q": 0.0,
            "d": 0.0,
            "p": 0.0,
            "C": self._compute_contract_layer_score(method_id, evidence),
            "u": self._compute_unit_layer_score(method_id, evidence),
            "m": self._compute_meta_layer_score(method_id, evidence),
        }
        
        contextual = self._compute_contextual_layer_scores(method_id, context, evidence)
        scores.update(contextual)
        
        return scores
    
    def _apply_choquet_fusion(
        self, layer_scores: dict[str, float], active_layers: list[str]
    ) -> dict[str, Any]:
        weights = self._load_fusion_weights()
        
        layer_map = {
            "@b": "b",
            "@chain": "chain",
            "@q": "q",
            "@d": "d",
            "@p": "p",
            "@C": "C",
            "@u": "u",
            "@m": "m",
        }
        
        linear_sum = 0.0
        linear_contributions = {}
        
        for layer_symbol in active_layers:
            layer_key = layer_map.get(layer_symbol, layer_symbol.lstrip("@"))
            
            if layer_key in layer_scores and layer_key in weights.linear_weights:
                contribution = weights.linear_weights[layer_key] * layer_scores[layer_key]
                linear_sum += contribution
                linear_contributions[layer_symbol] = contribution
        
        interaction_sum = 0.0
        interaction_contributions = {}
        
        for (l1, l2), weight in weights.interaction_weights.items():
            layer_key1 = layer_map.get(f"@{l1}", l1)
            layer_key2 = layer_map.get(f"@{l2}", l2)
            
            symbol1 = f"@{l1}"
            symbol2 = f"@{l2}"
            
            if symbol1 in active_layers and symbol2 in active_layers:
                if layer_key1 in layer_scores and layer_key2 in layer_scores:
                    min_score = min(layer_scores[layer_key1], layer_scores[layer_key2])
                    contribution = weight * min_score
                    interaction_sum += contribution
                    interaction_contributions[f"({symbol1},{symbol2})"] = contribution
        
        final_score = linear_sum + interaction_sum
        
        return {
            "final_score": final_score,
            "linear_sum": linear_sum,
            "interaction_sum": interaction_sum,
            "linear_contributions": linear_contributions,
            "interaction_contributions": interaction_contributions,
        }
    
    def _validate_boundedness(self, score: float) -> dict[str, Any]:
        is_valid = 0.0 <= score <= 1.0
        
        clamped_score = max(0.0, min(1.0, score))
        
        return {
            "is_bounded": is_valid,
            "original_score": score,
            "clamped_score": clamped_score,
            "lower_bound": 0.0,
            "upper_bound": 1.0,
            "violation": None if is_valid else ("below_zero" if score < 0.0 else "above_one"),
        }
    
    def _generate_certificate_metadata(
        self,
        method_id: str,
        role: str,
        final_score: float,
        active_layers: list[str],
        fusion_breakdown: dict[str, Any],
    ) -> dict[str, Any]:
        import hashlib
        import datetime
        
        cert_data = {
            "method_id": method_id,
            "role": role,
            "final_score": final_score,
            "active_layers": active_layers,
            "linear_sum": fusion_breakdown["linear_sum"],
            "interaction_sum": fusion_breakdown["interaction_sum"],
        }
        
        cert_string = json.dumps(cert_data, sort_keys=True, separators=(",", ":"))
        cert_hash = hashlib.sha256(cert_string.encode("utf-8")).hexdigest()
        
        return {
            "certificate_id": cert_hash[:16],
            "certificate_hash": cert_hash,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "cohort_id": "COHORT_2024",
            "wave_version": "REFACTOR_WAVE_2024_12",
            "implementation_wave": "GOVERNANCE_WAVE_2024_12_07",
            "authority": "Doctrina SIN_CARRETA",
            "spec_compliance": "SUPERPROMPT Three-Pillar Calibration System",
            "fusion_formula": "Cal(I) = Σ(a_ℓ · x_ℓ) + Σ(a_ℓk · min(x_ℓ, x_k))",
        }
    
    def calibrate(
        self,
        method_id: str,
        context: CalibrationContext | None = None,
        evidence: CalibrationEvidence | None = None,
    ) -> CalibrationResult:
        if context is None:
            context = {}
        
        if evidence is None:
            evidence = {}
        
        role = self._determine_role(method_id)
        
        active_layers = self._get_required_layers(method_id)
        
        all_layer_scores = self._compute_all_layer_scores(method_id, context, evidence)
        
        active_layer_scores = {
            layer.lstrip("@"): all_layer_scores[layer.lstrip("@")]
            for layer in active_layers
        }
        
        fusion_breakdown = self._apply_choquet_fusion(all_layer_scores, active_layers)
        
        final_score = fusion_breakdown["final_score"]
        
        validation = self._validate_boundedness(final_score)
        
        if not validation["is_bounded"]:
            final_score = validation["clamped_score"]
        
        certificate_metadata = self._generate_certificate_metadata(
            method_id, role, final_score, active_layers, fusion_breakdown
        )
        
        return CalibrationResult(
            method_id=method_id,
            role=role,
            final_score=final_score,
            layer_scores=active_layer_scores,
            active_layers=active_layers,
            fusion_breakdown=fusion_breakdown,
            certificate_metadata=certificate_metadata,
            validation=validation,
        )


__all__ = [
    "CalibrationOrchestrator",
    "CalibrationContext",
    "CalibrationEvidence",
    "CalibrationResult",
    "LayerScores",
    "FusionWeights",
]

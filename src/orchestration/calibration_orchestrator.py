"""
Calibration Orchestrator - Extramodule within Core Orchestrator

Role-based layer activation system for method calibration with:
- LayerRequirementsResolver for role-based layer determination
- All 8 layer evaluators (base, unit, question, dimension, policy, congruence, chain, meta)
- Choquet aggregation for fusion
- Completeness validation

Architecture: Loads all configs, determines active layers by role, computes scores, fuses via Choquet.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Set, TypedDict

from src.core.calibration.layer_requirements import (
    LAYER_REQUIREMENTS,
    get_required_layers,
)

logger = logging.getLogger(__name__)


class LayerID(str, Enum):
    """Layer identifiers for calibration system."""
    BASE = "@b"
    CHAIN = "@chain"
    UNIT = "@u"
    QUESTION = "@q"
    DIMENSION = "@d"
    POLICY = "@p"
    CONGRUENCE = "@C"
    META = "@m"


class CalibrationSubject(TypedDict):
    """Subject for calibration."""
    method_id: str
    role: str
    context: Dict[str, Any]


class EvidenceStore(TypedDict):
    """Evidence store for calibration."""
    pdt_structure: Dict[str, Any]
    document_quality: float
    question_id: str | None
    dimension_id: str | None
    policy_area_id: str | None


@dataclass
class CalibrationResult:
    """Result of calibration."""
    final_score: float
    layer_scores: Dict[LayerID, float]
    active_layers: Set[LayerID]
    role: str
    method_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        if not 0.0 <= self.final_score <= 1.0:
            raise ValueError(f"Final score {self.final_score} not in [0,1]")


class LayerRequirementsResolver:
    """Resolves required layers based on method role."""
    
    def __init__(
        self,
        intrinsic_config: Dict[str, Any],
        method_compatibility: Dict[str, Any]
    ) -> None:
        self.intrinsic_config = intrinsic_config
        self.method_compatibility = method_compatibility
        self.role_mapping = self._build_role_mapping()
    
    def _build_role_mapping(self) -> Dict[str, Set[LayerID]]:
        """Build role mapping from canonical LAYER_REQUIREMENTS."""
        return {
            "INGEST_PDM": {LayerID(layer) for layer in LAYER_REQUIREMENTS["ingest"]["layers"]},
            "STRUCTURE": {LayerID(layer) for layer in LAYER_REQUIREMENTS["processor"]["layers"]},
            "EXTRACT": {LayerID(layer) for layer in LAYER_REQUIREMENTS["extractor"]["layers"]},
            "SCORE_Q": {LayerID(layer) for layer in LAYER_REQUIREMENTS["score"]["layers"]},
            "AGGREGATE": {LayerID(layer) for layer in LAYER_REQUIREMENTS["core"]["layers"]},
            "REPORT": {LayerID(layer) for layer in LAYER_REQUIREMENTS["orchestrator"]["layers"]},
            "META_TOOL": {LayerID(layer) for layer in LAYER_REQUIREMENTS["utility"]["layers"]},
            "TRANSFORM": {LayerID(layer) for layer in LAYER_REQUIREMENTS["utility"]["layers"]},
        }
    
    def get_required_layers(self, method_id: str) -> Set[LayerID]:
        """Get required layers for method based on role."""
        role = self._get_method_role(method_id)
        
        if role in self.role_mapping:
            return self.role_mapping[role].copy()
        
        logger.warning(f"Unknown role '{role}' for {method_id}, using SCORE_Q layers")
        return self.role_mapping["SCORE_Q"].copy()
    
    def _get_method_role(self, method_id: str) -> str:
        """Extract role from intrinsic config or infer from method_id."""
        methods = self.intrinsic_config.get("methods", {})
        
        if method_id in methods:
            role = methods[method_id].get("role", "SCORE_Q")
            return role.upper()
        
        if "ingest" in method_id.lower() or "ingestion" in method_id.lower():
            return "INGEST_PDM"
        if "processor" in method_id.lower() or "structure" in method_id.lower():
            return "STRUCTURE"
        if "extract" in method_id.lower():
            return "EXTRACT"
        if "executor" in method_id.lower() or "score" in method_id.lower():
            return "SCORE_Q"
        if "aggregat" in method_id.lower():
            return "AGGREGATE"
        if "report" in method_id.lower():
            return "REPORT"
        if "transform" in method_id.lower():
            return "TRANSFORM"
        
        return "SCORE_Q"


class BaseLayerEvaluator:
    """Evaluates @b (base quality) layer."""
    
    def __init__(self, intrinsic_config: Dict[str, Any]) -> None:
        self.intrinsic_config = intrinsic_config
        self.methods = intrinsic_config.get("methods", {})
    
    def evaluate(self, method_id: str) -> float:
        """Evaluate base quality for method."""
        if method_id not in self.methods:
            logger.warning(f"Method {method_id} not in intrinsic config, using default 0.5")
            return 0.5
        
        method_data = self.methods[method_id]
        
        b_theory = method_data.get("b_theory", 0.5)
        b_impl = method_data.get("b_impl", 0.5)
        b_deploy = method_data.get("b_deploy", 0.5)
        
        weights = self.intrinsic_config.get("_base_weights", {
            "w_theory": 0.4,
            "w_impl": 0.35,
            "w_deploy": 0.25
        })
        
        w_th = weights.get("w_theory", 0.4)
        w_imp = weights.get("w_impl", 0.35)
        w_dep = weights.get("w_deploy", 0.25)
        
        score = w_th * b_theory + w_imp * b_impl + w_dep * b_deploy
        return max(0.0, min(1.0, score))


class ChainLayerEvaluator:
    """Evaluates @chain (compatibility) layer."""
    
    def __init__(self, method_compatibility: Dict[str, Any]) -> None:
        self.compatibility = method_compatibility
    
    def evaluate(self, method_id: str) -> float:
        """Evaluate chain compatibility for method."""
        methods = self.compatibility.get("methods", {})
        
        if method_id not in methods:
            return 0.6
        
        method_data = methods[method_id]
        chain_score = method_data.get("chain_compatibility_score", 0.6)
        
        return max(0.0, min(1.0, chain_score))


class UnitLayerEvaluator:
    """Evaluates @u (unit/document quality) layer."""
    
    def __init__(self) -> None:
        pass
    
    def evaluate(self, pdt_structure: Dict[str, Any]) -> float:
        """Evaluate document quality from PDT structure."""
        chunk_count = pdt_structure.get("chunk_count", 0)
        completeness = pdt_structure.get("completeness", 0.5)
        structure_quality = pdt_structure.get("structure_quality", 0.5)
        
        if chunk_count < 10:
            doc_coverage = 0.3
        elif chunk_count < 40:
            doc_coverage = 0.5 + (chunk_count - 10) * 0.01
        elif chunk_count < 60:
            doc_coverage = 0.8 + (chunk_count - 40) * 0.01
        else:
            doc_coverage = 1.0
        
        score = 0.4 * doc_coverage + 0.3 * completeness + 0.3 * structure_quality
        return max(0.0, min(1.0, score))


class QuestionLayerEvaluator:
    """Evaluates @q (question appropriateness) layer."""
    
    def __init__(self, questionnaire_monolith: Dict[str, Any]) -> None:
        self.questionnaire = questionnaire_monolith
    
    def evaluate(self, method_id: str, question_id: str | None) -> float:
        """Evaluate question appropriateness."""
        if question_id is None:
            return 0.5
        
        questions = self.questionnaire.get("blocks", {}).get("micro_questions", [])
        
        for q in questions:
            if q.get("question_id") == question_id:
                method_sets = q.get("method_sets", {})
                
                for role, method_ref in method_sets.items():
                    if method_id in str(method_ref):
                        return 0.9
                
                return 0.6
        
        return 0.5


class DimensionLayerEvaluator:
    """Evaluates @d (dimension alignment) layer."""
    
    def __init__(self, questionnaire_monolith: Dict[str, Any]) -> None:
        self.questionnaire = questionnaire_monolith
    
    def evaluate(self, method_id: str, dimension_id: str | None) -> float:
        """Evaluate dimension alignment."""
        if dimension_id is None:
            return 0.5
        
        dimensions = self.questionnaire.get("blocks", {}).get("dimensions", [])
        
        for dim in dimensions:
            if dim.get("dimension_id") == dimension_id:
                return 0.85
        
        return 0.6


class PolicyLayerEvaluator:
    """Evaluates @p (policy area fit) layer."""
    
    def __init__(self, questionnaire_monolith: Dict[str, Any]) -> None:
        self.questionnaire = questionnaire_monolith
    
    def evaluate(self, method_id: str, policy_area_id: str | None) -> float:
        """Evaluate policy area fit."""
        if policy_area_id is None:
            return 0.5
        
        policy_areas = self.questionnaire.get("blocks", {}).get("policy_areas", [])
        
        for pa in policy_areas:
            if pa.get("policy_area_id") == policy_area_id:
                return 0.85
        
        return 0.6


class CongruenceLayerEvaluator:
    """Evaluates @C (contract compliance) layer."""
    
    def __init__(self, fusion_spec: Dict[str, Any]) -> None:
        self.fusion_spec = fusion_spec
    
    def evaluate(self, method_id: str) -> float:
        """Evaluate contract compliance."""
        role_params = self.fusion_spec.get("role_fusion_parameters", {})
        
        for role, params in role_params.items():
            methods = params.get("methods", [])
            if method_id in methods:
                return 0.85
        
        return 0.6


class MetaLayerEvaluator:
    """Evaluates @m (meta/governance) layer."""
    
    def __init__(self, method_catalog: Dict[str, Any]) -> None:
        self.catalog = method_catalog
    
    def evaluate(self, method_id: str) -> float:
        """Evaluate meta/governance quality."""
        methods = self.catalog.get("methods", {})
        
        if method_id not in methods:
            return 0.5
        
        method_data = methods[method_id]
        governance_score = method_data.get("governance_quality", 0.7)
        
        return max(0.0, min(1.0, governance_score))


class ChoquetAggregator:
    """Choquet integral aggregator for layer fusion."""
    
    def __init__(self, fusion_spec: Dict[str, Any]) -> None:
        self.fusion_spec = fusion_spec
    
    def aggregate(
        self,
        subject: CalibrationSubject,
        layer_scores: Dict[LayerID, float]
    ) -> float:
        """Aggregate layer scores using Choquet integral."""
        role = subject["role"]
        role_params = self.fusion_spec.get("role_fusion_parameters", {}).get(role, {})
        
        linear_weights = role_params.get("linear_weights", {})
        interaction_weights = role_params.get("interaction_weights", {})
        
        linear_sum = 0.0
        for layer_id, score in layer_scores.items():
            weight = linear_weights.get(layer_id.value, 0.0)
            linear_sum += weight * score
        
        interaction_sum = 0.0
        for interaction_key, weight in interaction_weights.items():
            layers = interaction_key.split(",")
            if len(layers) == 2:
                l1_id = LayerID(layers[0])
                l2_id = LayerID(layers[1])
                
                if l1_id in layer_scores and l2_id in layer_scores:
                    min_score = min(layer_scores[l1_id], layer_scores[l2_id])
                    interaction_sum += weight * min_score
        
        final = linear_sum + interaction_sum
        return max(0.0, min(1.0, final))


class CalibrationOrchestrator:
    """
    Calibration orchestrator with role-based layer activation.
    
    Role-based layer requirements:
    - INGEST_PDM: {BASE, CHAIN, UNIT, META}
    - STRUCTURE: {BASE, CHAIN, UNIT, META}
    - EXTRACT: {BASE, CHAIN, UNIT, META}
    - SCORE_Q: {BASE, CHAIN, QUESTION, DIMENSION, POLICY, CONGRUENCE, UNIT, META}
    - AGGREGATE: {BASE, CHAIN, DIMENSION, POLICY, CONGRUENCE, META}
    - REPORT: {BASE, CHAIN, CONGRUENCE, META}
    - META_TOOL: {BASE, CHAIN, META}
    - TRANSFORM: {BASE, CHAIN, META}
    """
    
    def __init__(
        self,
        intrinsic_calibration: Dict[str, Any],
        questionnaire_monolith: Dict[str, Any],
        fusion_specification: Dict[str, Any],
        method_compatibility: Dict[str, Any],
        canonical_method_catalog: Dict[str, Any]
    ) -> None:
        self.intrinsic_calibration = intrinsic_calibration
        self.questionnaire_monolith = questionnaire_monolith
        self.fusion_specification = fusion_specification
        self.method_compatibility = method_compatibility
        self.canonical_method_catalog = canonical_method_catalog
        
        self.layer_resolver = LayerRequirementsResolver(
            intrinsic_calibration, method_compatibility
        )
        
        self.base_evaluator = BaseLayerEvaluator(intrinsic_calibration)
        self.chain_evaluator = ChainLayerEvaluator(method_compatibility)
        self.unit_evaluator = UnitLayerEvaluator()
        self.question_evaluator = QuestionLayerEvaluator(questionnaire_monolith)
        self.dimension_evaluator = DimensionLayerEvaluator(questionnaire_monolith)
        self.policy_evaluator = PolicyLayerEvaluator(questionnaire_monolith)
        self.congruence_evaluator = CongruenceLayerEvaluator(fusion_specification)
        self.meta_evaluator = MetaLayerEvaluator(canonical_method_catalog)
        
        self.choquet_aggregator = ChoquetAggregator(fusion_specification)
        
        logger.info("CalibrationOrchestrator initialized with all layer evaluators")
    
    @classmethod
    def from_config_dir(cls, config_dir: Path) -> CalibrationOrchestrator:
        """Load from configuration directory."""
        intrinsic_path = config_dir / "COHORT_2024_intrinsic_calibration.json"
        questionnaire_path = config_dir / "COHORT_2024_questionnaire_monolith.json"
        fusion_path = config_dir / "COHORT_2024_fusion_weights.json"
        compatibility_path = config_dir / "COHORT_2024_method_compatibility.json"
        catalog_path = config_dir / "COHORT_2024_canonical_method_inventory.json"
        
        with open(intrinsic_path) as f:
            intrinsic_calibration = json.load(f)
        
        with open(questionnaire_path) as f:
            questionnaire_monolith = json.load(f)
        
        with open(fusion_path) as f:
            fusion_specification = json.load(f)
        
        with open(compatibility_path) as f:
            method_compatibility = json.load(f)
        
        with open(catalog_path) as f:
            canonical_method_catalog = json.load(f)
        
        return cls(
            intrinsic_calibration,
            questionnaire_monolith,
            fusion_specification,
            method_compatibility,
            canonical_method_catalog
        )
    
    def calibrate(
        self,
        subject: CalibrationSubject,
        evidence: EvidenceStore
    ) -> CalibrationResult:
        """
        Calibrate method based on role with layer activation.
        
        Determines active layers via LayerRequirementsResolver.get_required_layers(subject.method_id),
        computes scores for each active layer, applies Choquet fusion, validates completeness.
        """
        method_id = subject["method_id"]
        role = subject["role"]
        context = subject["context"]
        
        active_layers = self.layer_resolver.get_required_layers(method_id)
        
        layer_scores: Dict[LayerID, float] = {}
        
        if LayerID.BASE in active_layers:
            layer_scores[LayerID.BASE] = self.base_evaluator.evaluate(method_id)
        
        if LayerID.CHAIN in active_layers:
            layer_scores[LayerID.CHAIN] = self.chain_evaluator.evaluate(method_id)
        
        if LayerID.UNIT in active_layers:
            layer_scores[LayerID.UNIT] = self.unit_evaluator.evaluate(
                evidence["pdt_structure"]
            )
        
        if LayerID.QUESTION in active_layers:
            layer_scores[LayerID.QUESTION] = self.question_evaluator.evaluate(
                method_id, evidence.get("question_id")
            )
        
        if LayerID.DIMENSION in active_layers:
            layer_scores[LayerID.DIMENSION] = self.dimension_evaluator.evaluate(
                method_id, evidence.get("dimension_id")
            )
        
        if LayerID.POLICY in active_layers:
            layer_scores[LayerID.POLICY] = self.policy_evaluator.evaluate(
                method_id, evidence.get("policy_area_id")
            )
        
        if LayerID.CONGRUENCE in active_layers:
            layer_scores[LayerID.CONGRUENCE] = self.congruence_evaluator.evaluate(
                method_id
            )
        
        if LayerID.META in active_layers:
            layer_scores[LayerID.META] = self.meta_evaluator.evaluate(method_id)
        
        self._validate_completeness(active_layers, layer_scores, method_id, role)
        
        final_score = self.choquet_aggregator.aggregate(subject, layer_scores)
        
        result = CalibrationResult(
            final_score=final_score,
            layer_scores=layer_scores,
            active_layers=active_layers,
            role=role,
            method_id=method_id,
            metadata={
                "context": context,
                "evidence_keys": list(evidence.keys()),
                "layer_count": len(active_layers)
            }
        )
        
        logger.info(
            f"Calibrated {method_id} (role={role}): "
            f"final={final_score:.3f}, layers={len(active_layers)}"
        )
        
        return result
    
    def _validate_completeness(
        self,
        required_layers: Set[LayerID],
        computed_layers: Dict[LayerID, float],
        method_id: str,
        role: str
    ) -> None:
        """Validate all required layers were computed."""
        missing = required_layers - set(computed_layers.keys())
        
        if missing:
            missing_str = ", ".join(layer.value for layer in missing)
            raise ValueError(
                f"Calibration completeness check failed for {method_id} (role={role}): "
                f"missing layers: {missing_str}"
            )


__all__ = [
    "CalibrationOrchestrator",
    "CalibrationSubject",
    "CalibrationResult",
    "EvidenceStore",
    "LayerID",
    "LayerRequirementsResolver",
    "ROLE_LAYER_REQUIREMENTS",
]

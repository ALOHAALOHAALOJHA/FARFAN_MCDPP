"""
Signal Enhancement Integrator - Strategic Irrigation Integration Layer
======================================================================

Integrates all 6 surgical enhancements into the SISAS signal extraction
pipeline, providing a unified interface for enhanced data irrigation from
questionnaire to Phase 2 nodes.

Enhancements Integrated:
    1. Method Execution Metadata (Subphase 2.3)
    2. Structured Validation Specifications (Subphase 2.5)
    3. Scoring Modality Context (Subphase 2.3)
    4. Semantic Disambiguation Layer (Subphase 2.2)
    5. Cross-Cutting Themes (R-W2) - 2026-01-04
    6. Interdependency Validation (R-W3) - 2026-01-04

Integration Architecture:
    QuestionnaireSignalRegistry
        ↓
    SignalEnhancementIntegrator
        ↓
    ├── extract_method_metadata() → Enhancement #1
    ├── extract_validation_specifications() → Enhancement #2
    ├── extract_scoring_context() → Enhancement #3
    ├── extract_semantic_context() → Enhancement #4
    ├── extract_cross_cutting_themes() → Enhancement #5 (R-W2)
    └── extract_interdependency_context() → Enhancement #6 (R-W3)
        ↓
    EnrichedSignalPack (with 6 enhancement fields populated)

Author: F.A.R.F.A.N Pipeline Team
Date: 2025-12-11
Version: 1.1.0
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_method_metadata import (
    MethodExecutionMetadata,
    extract_method_metadata,
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_validation_specs import (
    ValidationSpecifications,
    extract_validation_specifications,
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_scoring_context import (
    ScoringContext,
    extract_scoring_context,
    create_default_scoring_context,
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_semantic_context import (
    SemanticContext,
    extract_semantic_context,
)

if TYPE_CHECKING:
    from farfan_pipeline.infrastructure.irrigation_using_signals.ports import QuestionnairePort

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class SignalEnhancementIntegrator:
    """Integrates all 6 signal enhancements into signal extraction.

    This class provides a unified interface for extracting enhanced strategic
    data from the questionnaire and integrating it into signal packs.

    Enhancements:
        1. Method Execution Metadata (Subphase 2.3)
        2. Structured Validation Specifications (Subphase 2.5)
        3. Scoring Modality Context (Subphase 2.3)
        4. Semantic Disambiguation Layer (Subphase 2.2)
        5. Cross-Cutting Themes (R-W2)
        6. Interdependency Validation (R-W3)

    Attributes:
        questionnaire: Canonical questionnaire instance
        semantic_context: Global semantic context (shared across questions)
        scoring_definitions: Global scoring modality definitions
        cross_cutting_themes: Global cross-cutting themes data (R-W2)
        interdependency_mapping: Dimension interdependency mapping (R-W3)
    """
    
    def __init__(self, questionnaire: QuestionnairePort) -> None:
        """Initialize integrator with questionnaire.

        Args:
            questionnaire: Canonical questionnaire instance
        """
        self.questionnaire = questionnaire

        # Extract global semantic context (Enhancement #4)
        semantic_layers = questionnaire.data.get("blocks", {}).get("semantic_layers", {})
        self.semantic_context = extract_semantic_context(semantic_layers)

        # Extract global scoring definitions (Enhancement #3)
        self.scoring_definitions = questionnaire.data.get("blocks", {}).get("scoring", {})

        # Load cross-cutting themes (Enhancement #5 - R-W2)
        self.cross_cutting_themes = self._load_cross_cutting_themes()

        # Load interdependency mapping (Enhancement #6 - R-W3)
        self.interdependency_mapping = self._load_interdependency_mapping()

        logger.info(
            "signal_enhancement_integrator_initialized",
            questionnaire_version=questionnaire.version,
            semantic_rules_count=len(self.semantic_context.disambiguation_rules),
            scoring_modalities_count=len(self.scoring_definitions.get("modality_definitions", {})),
            cross_cutting_theme_count=len(self.cross_cutting_themes.get("themes", [])),
            interdependency_rule_count=len(self.interdependency_mapping.get("cross_dimension_validation_rules", {})),
        )
    
    def enhance_question_signals(
        self,
        question_id: str,
        question_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Extract all 4 enhancements for a question.
        
        Args:
            question_id: Question identifier
            question_data: Question dictionary from questionnaire
            
        Returns:
            Dictionary with all 4 enhancement fields populated
        """
        enhancements: dict[str, Any] = {}
        
        # Enhancement #1: Method Execution Metadata
        try:
            method_metadata = extract_method_metadata(question_data, question_id)
            enhancements["method_execution_metadata"] = self._serialize_method_metadata(
                method_metadata
            )
        except Exception as exc:
            logger.warning(
                "method_metadata_enhancement_failed",
                question_id=question_id,
                error=str(exc)
            )
            enhancements["method_execution_metadata"] = {}
        
        # Enhancement #2: Structured Validation Specifications
        try:
            validation_specs = extract_validation_specifications(question_data, question_id)
            enhancements["validation_specifications"] = self._serialize_validation_specs(
                validation_specs
            )
        except Exception as exc:
            logger.warning(
                "validation_specs_enhancement_failed",
                question_id=question_id,
                error=str(exc)
            )
            enhancements["validation_specifications"] = {}
        
        # Enhancement #3: Scoring Modality Context
        try:
            scoring_context = extract_scoring_context(
                question_data,
                self.scoring_definitions,
                question_id
            )
            if scoring_context:
                enhancements["scoring_modality_context"] = self._serialize_scoring_context(
                    scoring_context
                )
            else:
                # Fallback to default
                default_context = create_default_scoring_context(question_id)
                enhancements["scoring_modality_context"] = self._serialize_scoring_context(
                    default_context
                )
        except Exception as exc:
            logger.warning(
                "scoring_context_enhancement_failed",
                question_id=question_id,
                error=str(exc)
            )
            enhancements["scoring_modality_context"] = {}
        
        # Enhancement #4: Semantic Disambiguation (global context, per-question reference)
        try:
            enhancements["semantic_disambiguation"] = self._serialize_semantic_context(
                self.semantic_context,
                question_data
            )
        except Exception as exc:
            logger.warning(
                "semantic_disambiguation_enhancement_failed",
                question_id=question_id,
                error=str(exc)
            )
            enhancements["semantic_disambiguation"] = {}

        # Enhancement #5: Cross-Cutting Themes (R-W2)
        try:
            policy_area_id = question_data.get("policy_area_id", "PA01")
            dimension_id = question_data.get("dimension_id", "DIM01")
            enhancements["cross_cutting_themes"] = self._extract_cross_cutting_themes(
                policy_area_id, dimension_id
            )
        except Exception as exc:
            logger.warning(
                "cross_cutting_themes_enhancement_failed",
                question_id=question_id,
                error=str(exc)
            )
            enhancements["cross_cutting_themes"] = {}

        # Enhancement #6: Interdependency Context (R-W3)
        try:
            dimension_id = question_data.get("dimension_id", "DIM01")
            enhancements["interdependency_context"] = self._extract_interdependency_context(
                dimension_id
            )
        except Exception as exc:
            logger.warning(
                "interdependency_context_enhancement_failed",
                question_id=question_id,
                error=str(exc)
            )
            enhancements["interdependency_context"] = {}

        logger.debug(
            "question_signals_enhanced",
            question_id=question_id,
            enhancements_applied=len([k for k, v in enhancements.items() if v])
        )

        return enhancements
    
    def _serialize_method_metadata(
        self,
        metadata: MethodExecutionMetadata
    ) -> dict[str, Any]:
        """Serialize method metadata to dict for signal pack."""
        return {
            "methods": [
                {
                    "class_name": m.class_name,
                    "method_name": m.method_name,
                    "method_type": m.method_type,
                    "priority": m.priority,
                    "description": m.description
                }
                for m in metadata.methods
            ],
            "priority_groups": {
                str(p): [
                    {
                        "class_name": m.class_name,
                        "method_name": m.method_name,
                        "method_type": m.method_type
                    }
                    for m in methods
                ]
                for p, methods in metadata.priority_groups.items()
            },
            "type_distribution": metadata.type_distribution,
            "execution_order": list(metadata.execution_order)
        }
    
    def _serialize_validation_specs(
        self,
        specs: ValidationSpecifications
    ) -> dict[str, Any]:
        """Serialize validation specifications to dict for signal pack."""
        return {
            "specs": {
                val_type: {
                    "validation_type": spec.validation_type,
                    "enabled": spec.enabled,
                    "threshold": spec.threshold,
                    "severity": spec.severity,
                    "criteria": spec.criteria
                }
                for val_type, spec in specs.specs.items()
            },
            "required_validations": list(specs.required_validations),
            "critical_validations": list(specs.critical_validations),
            "quality_threshold": specs.quality_threshold
        }
    
    def _serialize_scoring_context(
        self,
        context: ScoringContext
    ) -> dict[str, Any]:
        """Serialize scoring context to dict for signal pack."""
        return {
            "modality": context.modality_definition.modality,
            "description": context.modality_definition.description,
            "threshold": context.modality_definition.threshold,
            "aggregation": context.modality_definition.aggregation,
            "weights": {
                "elements": context.modality_definition.weight_elements,
                "similarity": context.modality_definition.weight_similarity,
                "patterns": context.modality_definition.weight_patterns
            },
            "failure_code": context.modality_definition.failure_code,
            "adaptive_threshold": context.adaptive_threshold,
            "policy_area_id": context.policy_area_id,
            "dimension_id": context.dimension_id
        }
    
    def _serialize_semantic_context(
        self,
        context: SemanticContext,
        question_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Serialize semantic context to dict for signal pack."""
        # Include question-specific patterns for disambiguation
        patterns = question_data.get("patterns", [])
        
        return {
            "entity_linking": {
                "enabled": context.entity_linking.enabled,
                "confidence_threshold": context.entity_linking.confidence_threshold,
                "context_window": context.entity_linking.context_window,
                "fallback_strategy": context.entity_linking.fallback_strategy
            },
            "disambiguation_rules_count": len(context.disambiguation_rules),
            "applicable_rules": [
                rule.term
                for rule in context.disambiguation_rules.values()
                if any(rule.term.lower() in str(p).lower() for p in patterns)
            ],
            "embedding_strategy": {
                "model": context.embedding_strategy.model,
                "dimension": context.embedding_strategy.dimension,
                "hybrid": context.embedding_strategy.hybrid,
                "strategy": context.embedding_strategy.strategy
            },
            "confidence_threshold": context.confidence_threshold
        }
    
    def get_enhancement_statistics(self) -> dict[str, Any]:
        """Get statistics about enhancements applied.

        Returns:
            Dictionary with enhancement coverage statistics
        """
        return {
            "semantic_rules": len(self.semantic_context.disambiguation_rules),
            "scoring_modalities": len(self.scoring_definitions.get("modality_definitions", {})),
            "entity_linking_enabled": self.semantic_context.entity_linking.enabled,
            "embedding_model": self.semantic_context.embedding_strategy.model,
            "cross_cutting_themes": len(self.cross_cutting_themes.get("themes", [])),
            "interdependency_rules": len(self.interdependency_mapping.get("cross_dimension_validation_rules", {})),
        }

    def _load_cross_cutting_themes(self) -> dict[str, Any]:
        """Load cross-cutting themes from canonical questionnaire (R-W2)."""
        themes_path = (
            Path(__file__).parent.parent.parent.parent.parent.parent
            / "canonic_questionnaire_central"
            / "cross_cutting"
            / "cross_cutting_themes.json"
        )

        if not themes_path.exists():
            logger.warning("cross_cutting_themes_not_found", path=str(themes_path))
            return {"themes": [], "validation_rules": {}}

        try:
            with open(themes_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            logger.error("cross_cutting_themes_load_failed", error=str(e), exc_info=True)
            return {"themes": [], "validation_rules": {}}

    def _load_interdependency_mapping(self) -> dict[str, Any]:
        """Load interdependency mapping from canonical questionnaire (R-W3)."""
        mapping_path = (
            Path(__file__).parent.parent.parent.parent.parent.parent
            / "canonic_questionnaire_central"
            / "validations"
            / "interdependency_mapping.json"
        )

        if not mapping_path.exists():
            logger.warning("interdependency_mapping_not_found", path=str(mapping_path))
            return {"dimension_flow": {}, "cross_dimension_validation_rules": {}}

        try:
            with open(mapping_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            logger.error("interdependency_mapping_load_failed", error=str(e), exc_info=True)
            return {"dimension_flow": {}, "cross_dimension_validation_rules": {}}

    def _extract_cross_cutting_themes(
        self,
        policy_area_id: str,
        dimension_id: str,
    ) -> dict[str, Any]:
        """Extract applicable cross-cutting themes for a question (R-W2)."""
        themes_data = self.cross_cutting_themes
        applicable_themes: list[dict[str, Any]] = []
        required_themes: list[str] = []

        for theme in themes_data.get("themes", []):
            applies_to = theme.get("applies_to", {})
            applies_dims = applies_to.get("dimensions", [])
            applies_pas = applies_to.get("policy_areas", [])

            pa_applicable = policy_area_id in applies_pas or not applies_pas
            dim_applicable = dimension_id in applies_dims or not applies_dims

            if pa_applicable and dim_applicable:
                applicable_themes.append({
                    "theme_id": theme.get("theme_id"),
                    "name": theme.get("name"),
                    "indicators": theme.get("indicators", []),
                })

                validation_rules = theme.get("validation_rules", {})
                if policy_area_id in validation_rules.get("required_for", []):
                    required_themes.append(theme.get("theme_id"))

        global_rules = themes_data.get("validation_rules", {})
        for theme_id in global_rules.get("required_themes_all", []):
            if theme_id not in required_themes:
                required_themes.append(theme_id)

        return {
            "applicable_themes": applicable_themes,
            "required_themes": required_themes,
            "minimum_themes": global_rules.get("minimum_themes_per_policy_area", 3),
        }

    def _extract_interdependency_context(
        self,
        dimension_id: str,
    ) -> dict[str, Any]:
        """Extract interdependency context for a dimension (R-W3)."""
        mapping = self.interdependency_mapping
        dim_flow = mapping.get("dimension_flow", {})
        dependencies = dim_flow.get("dependencies", {})

        full_dim_id = dimension_id
        if "_" not in dimension_id:
            dim_map = {
                "DIM01": "DIM01_INSUMOS",
                "DIM02": "DIM02_ACTIVIDADES",
                "DIM03": "DIM03_PRODUCTOS",
                "DIM04": "DIM04_RESULTADOS",
                "DIM05": "DIM05_IMPACTOS",
                "DIM06": "DIM06_CAUSALIDAD",
            }
            full_dim_id = dim_map.get(dimension_id, dimension_id)

        dim_deps = dependencies.get(full_dim_id, {})
        depends_on = dim_deps.get("depends_on", [])
        validation_rule = dim_deps.get("validation_rule", "")

        applicable_rules: list[dict[str, Any]] = []
        cross_rules = mapping.get("cross_dimension_validation_rules", {})

        for rule_key, rule in cross_rules.items():
            desc = rule.get("description", "").lower()
            # Extract base dimension ID (e.g., "DIM04" from "DIM04_RESULTADOS")
            base_dim_id = dimension_id.split("_")[0] if "_" in dimension_id else dimension_id
            # Extract numeric part (e.g., "04" from "DIM04")
            dim_num = base_dim_id.replace("DIM", "")
            # Strip leading zeros for matching (e.g., "4" from "04")
            dim_num_stripped = dim_num.lstrip("0") or "0"

            if (
                f"dim{dim_num}" in desc
                or f"dim{dim_num_stripped}" in desc
                or base_dim_id.lower() in desc
                or dimension_id.lower() in desc
            ):
                applicable_rules.append({
                    "rule_id": rule.get("rule_id", rule_key),
                    "description": rule.get("description"),
                    "enforcement": rule.get("enforcement", "warning"),
                })

        circular_patterns = mapping.get("circular_reasoning_detection", {})
        tautology_patterns = circular_patterns.get("tautology_detection", {}).get("patterns", [])

        return {
            "depends_on": depends_on,
            "validation_rule": validation_rule,
            "applicable_rules": applicable_rules,
            "circular_reasoning_patterns": tautology_patterns,
            "dimension_sequence": dim_flow.get("sequence", []),
        }


def create_enhancement_integrator(
    questionnaire: QuestionnairePort
) -> SignalEnhancementIntegrator:
    """Factory function to create enhancement integrator.
    
    Args:
        questionnaire: Canonical questionnaire instance
        
    Returns:
        Configured SignalEnhancementIntegrator
    """
    return SignalEnhancementIntegrator(questionnaire)

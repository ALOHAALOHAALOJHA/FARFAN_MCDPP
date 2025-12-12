"""
Signal Enhancement Integrator - Strategic Irrigation Integration Layer
======================================================================

Integrates all 4 surgical enhancements into the SISAS signal extraction
pipeline, providing a unified interface for enhanced data irrigation from
questionnaire to Phase 2 nodes.

Enhancements Integrated:
    1. Method Execution Metadata (Subphase 2.3)
    2. Structured Validation Specifications (Subphase 2.5)
    3. Scoring Modality Context (Subphase 2.3)
    4. Semantic Disambiguation Layer (Subphase 2.2)

Integration Architecture:
    QuestionnaireSignalRegistry
        ↓
    SignalEnhancementIntegrator
        ↓
    ├── extract_method_metadata() → Enhancement #1
    ├── extract_validation_specifications() → Enhancement #2
    ├── extract_scoring_context() → Enhancement #3
    └── extract_semantic_context() → Enhancement #4
        ↓
    EnrichedSignalPack (with 4 enhancement fields populated)

Author: F.A.R.F.A.N Pipeline Team
Date: 2025-12-11
Version: 1.0.0
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cross_cutting_infrastrucuture.irrigation_using_signals.SISAS.signal_method_metadata import (
    MethodExecutionMetadata,
    extract_method_metadata,
)
from cross_cutting_infrastrucuture.irrigation_using_signals.SISAS.signal_validation_specs import (
    ValidationSpecifications,
    extract_validation_specifications,
)
from cross_cutting_infrastrucuture.irrigation_using_signals.SISAS.signal_scoring_context import (
    ScoringContext,
    extract_scoring_context,
    create_default_scoring_context,
)
from cross_cutting_infrastrucuture.irrigation_using_signals.SISAS.signal_semantic_context import (
    SemanticContext,
    extract_semantic_context,
)

if TYPE_CHECKING:
    from orchestration.factory import CanonicalQuestionnaire

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class SignalEnhancementIntegrator:
    """Integrates all 4 signal enhancements into signal extraction.
    
    This class provides a unified interface for extracting enhanced strategic
    data from the questionnaire and integrating it into signal packs.
    
    Attributes:
        questionnaire: Canonical questionnaire instance
        semantic_context: Global semantic context (shared across questions)
        scoring_definitions: Global scoring modality definitions
    """
    
    def __init__(self, questionnaire: CanonicalQuestionnaire) -> None:
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
        
        logger.info(
            "signal_enhancement_integrator_initialized",
            questionnaire_version=questionnaire.version,
            semantic_rules_count=len(self.semantic_context.disambiguation_rules),
            scoring_modalities_count=len(self.scoring_definitions.get("modality_definitions", {}))
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
            "embedding_model": self.semantic_context.embedding_strategy.model
        }


def create_enhancement_integrator(
    questionnaire: CanonicalQuestionnaire
) -> SignalEnhancementIntegrator:
    """Factory function to create enhancement integrator.
    
    Args:
        questionnaire: Canonical questionnaire instance
        
    Returns:
        Configured SignalEnhancementIntegrator
    """
    return SignalEnhancementIntegrator(questionnaire)

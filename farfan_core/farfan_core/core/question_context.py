"""
Question Context Generator.

This module is responsible for generating the strict `QuestionContext` objects
required by the execution engine from the canonical `questionnaire_monolith.json`.

It enforces 1:1 mapping and strict field validation.
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional, Dict
import logging

from farfan_core.core.orchestrator.factory import CanonicalQuestionnaire
from farfan_core.core.calibration.decorators import calibrated_method

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class QuestionContext:
    """
    Immutable context for a single micro-question execution.
    
    Contains all necessary metadata and configuration for the executor.
    """
    question_id: str
    question_global: int
    base_slot: str
    dimension_id: str
    policy_area_id: str
    cluster_id: str
    text: str
    scoring_modality: str
    scoring_definition_ref: str
    patterns: List[Dict[str, Any]]
    expected_elements: List[Dict[str, Any]]
    method_sets: List[Dict[str, Any]]
    failure_contract: Dict[str, Any]
    validations: Dict[str, Any]
    
    # Optional derived fields
    signal_refs: List[str] = field(default_factory=list)

@dataclass
class QuestionContextGenerator:
    """
    Generates QuestionContext objects from a CanonicalQuestionnaire.
    """
    questionnaire: CanonicalQuestionnaire

    @calibrated_method("farfan_core.core.question_context.QuestionContextGenerator.generate_context_list")
    def generate_context_list(self) -> List[QuestionContext]:
        """
        Generate the complete list of QuestionContext objects.
        
        Returns:
            List of QuestionContext objects, one per micro-question.
            
        Raises:
            ValueError: If any validation fails or invariants are violated.
        """
        micro_questions = self.questionnaire.micro_questions
        context_list = []
        
        if len(micro_questions) != 300:
             raise ValueError(f"Invariant violation: Expected 300 micro-questions, got {len(micro_questions)}")

        for q_data in micro_questions:
            # Convert MappingProxyType to dict for easier handling if needed, 
            # though dataclass handles it fine usually.
            # We strictly validate presence of fields here.
            
            try:
                context = QuestionContext(
                    question_id=q_data["question_id"],
                    question_global=q_data["question_global"],
                    base_slot=q_data["base_slot"],
                    dimension_id=q_data["dimension_id"],
                    policy_area_id=q_data["policy_area_id"],
                    cluster_id=q_data["cluster_id"],
                    text=q_data["text"],
                    scoring_modality=q_data["scoring_modality"],
                    scoring_definition_ref=q_data["scoring_definition_ref"],
                    patterns=list(q_data.get("patterns", [])),
                    expected_elements=list(q_data.get("expected_elements", [])),
                    method_sets=list(q_data.get("method_sets", [])),
                    failure_contract=dict(q_data.get("failure_contract", {})),
                    validations=dict(q_data.get("validations", {}))
                )
                
                # Additional strict checks
                if not context.method_sets:
                     raise ValueError(f"Question {context.question_id} has empty method_sets")
                
                if not context.expected_elements:
                     raise ValueError(f"Question {context.question_id} has empty expected_elements")

                context_list.append(context)
                
            except KeyError as e:
                raise ValueError(f"Question {q_data.get('question_id', 'UNKNOWN')} missing required field: {e}")
            except Exception as e:
                raise ValueError(f"Failed to generate context for {q_data.get('question_id', 'UNKNOWN')}: {e}")

        return context_list

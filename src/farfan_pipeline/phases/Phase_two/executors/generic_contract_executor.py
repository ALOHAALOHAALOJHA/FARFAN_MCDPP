"""Generic Contract Executor - Executes ANY question contract by question_id.

This replaces the 30 hardcoded D1Q1-D6Q5 executor classes with a single
generic executor that loads contracts dynamically by question_id (Q001-Q300).

Architecture:
- Loads contract JSON by question_id from executor_contracts/specialized/
- Executes methods defined in contract's method_binding
- Returns evidence and results per contract specification
- NO hardcoded executor classes required
"""

from __future__ import annotations

from typing import Any

from canonic_phases.Phase_two.executors.base_executor_with_contract import (
    BaseExecutorWithContract,
)


class GenericContractExecutor(BaseExecutorWithContract):
    """Generic executor that loads and executes any question contract.
    
    Instead of having 300 separate executor classes, this single class
    can execute ANY contract by loading it dynamically via question_id.
    
    Usage:
        # Get question_id from question data
        question_id = question.get("id")  # e.g., "Q001"
        
        executor = GenericContractExecutor(
            method_executor=method_executor,
            signal_registry=signal_registry,
            config=config,
            questionnaire_provider=questionnaire_provider,
            question_id=question_id
        )
        result = executor.execute(document=doc, method_executor=method_executor, question_context=ctx)
    """
    
    def __init__(
        self,
        method_executor: Any,
        signal_registry: Any,
        config: Any,
        questionnaire_provider: Any,
        question_id: str,  # NEW: question_id to load contract
        calibration_orchestrator: Any | None = None,
        enriched_packs: dict[str, Any] | None = None,
        validation_orchestrator: Any | None = None,
    ) -> None:
        """Initialize generic executor with question_id.
        
        Args:
            question_id: Question identifier (Q001-Q300) to load contract from
                        executor_contracts/specialized/{question_id}.v3.json
            method_executor: MethodExecutor for executing contract methods
            signal_registry: Signal registry for SISAS coordination
            config: ExecutorConfig with runtime parameters
            questionnaire_provider: Questionnaire data provider
            calibration_orchestrator: Optional calibration orchestrator
            enriched_packs: Optional enriched signal packs
            validation_orchestrator: Optional validation orchestrator
        """
        super().__init__(
            method_executor=method_executor,
            signal_registry=signal_registry,
            config=config,
            questionnaire_provider=questionnaire_provider,
            calibration_orchestrator=calibration_orchestrator,
            enriched_packs=enriched_packs,
            validation_orchestrator=validation_orchestrator,
        )
        self._question_id = question_id
    
    @classmethod
    def get_base_slot(cls) -> str:
        """Return generic base slot placeholder for class-level operations.
        
        GenericContractExecutor uses "GENERIC" as a placeholder since the actual
        base_slot depends on which contract is loaded at runtime (e.g., "D1-Q1", "D6-Q5").
        Validation against the actual base_slot happens in execute() after contract loading.
        """
        return "GENERIC"
    
    def execute(
        self,
        document: Any,
        method_executor: Any,
        *,
        question_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute question contract with given context.
        
        This overrides the base execute() to handle GenericContractExecutor's
        dynamic base_slot validation (since get_base_slot() returns "GENERIC").
        
        Args:
            document: PreprocessedDocument to analyze
            method_executor: MethodExecutor for executing contract methods
            question_context: Context dict containing question_id, base_slot, etc.
        
        Returns:
            Result dict with evidence, validation, trace, etc.
        """
        # For GenericContractExecutor, skip the base_slot check in parent's execute()
        # by temporarily adjusting question_context, since we validate against the
        # loaded contract's base_slot instead of the class-level "GENERIC" placeholder
        question_id = question_context.get("question_id", self._question_id)
        contract = self._load_contract(question_id=question_id)
        actual_base_slot = contract.get("identity", {}).get("base_slot", "UNKNOWN")
        
        # Validate that orchestrator's base_slot matches the loaded contract's base_slot
        orchestrator_base_slot = question_context.get("base_slot")
        if orchestrator_base_slot != actual_base_slot:
            raise ValueError(
                f"Question base_slot {orchestrator_base_slot} from orchestrator does not match "
                f"loaded contract base_slot {actual_base_slot} for question_id {question_id}"
            )
        
        # Update question_context with validated base_slot set to "GENERIC" for parent check
        # (parent will compare question_context["base_slot"] == self.get_base_slot() == "GENERIC")
        ctx = dict(question_context)
        ctx["base_slot"] = "GENERIC"  # Match get_base_slot() return value
        ctx["question_id"] = question_id
        
        return super().execute(
            document=document,
            method_executor=method_executor,
            question_context=ctx,
        )

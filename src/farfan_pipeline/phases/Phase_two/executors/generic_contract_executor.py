"""Generic Contract Executor - Executes ANY question contract by question_id.

This replaces the 30 hardcoded D1Q1-D6Q5 executor classes with a single
generic executor that loads contracts dynamically by question_id (Q001-Q309).

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
    
    Instead of having 309 separate executor classes, this single class
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
        result = executor.execute(document=doc, question_context=ctx)
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
            question_id: Question identifier (Q001-Q309) to load contract from
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
        
        # Load the contract to get the actual base_slot
        # (needed for some internal operations)
        contract = self._load_contract(question_id=question_id)
        self._actual_base_slot = contract.get("identity", {}).get("base_slot", "UNKNOWN")
    
    @classmethod
    def get_base_slot(cls) -> str:
        """Return generic base slot for class-level operations.
        
        Note: Instance-level operations use _actual_base_slot from
        the loaded contract.
        """
        return "GENERIC"
    
    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """Execute question contract with given context.
        
        This overrides the base execute() to ensure the question_id
        is passed through to _load_contract().
        """
        # Ensure question_id is used for contract loading
        return super().execute(question_id=self._question_id, **kwargs)

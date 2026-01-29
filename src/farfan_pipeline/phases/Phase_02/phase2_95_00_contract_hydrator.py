"""
Contract Hydrator: Adapter layer for v4 streamlined contracts.

Hydrates v4 contracts with data from SignalRegistry to maintain
backward compatibility with Carver's EnhancedContractInterpreter.

PHASE_LABEL: Phase 2
PHASE_COMPONENT: Contract Hydrator
PHASE_ROLE: Bridges streamlined v4 contracts to Carver-compatible interface

Design Rationale
----------------
V4 contracts eliminate redundancy by storing only:
  - question_context.monolith_ref (e.g., "Q230")
  - question_context.overrides (optional)
  - question_context.failure_contract

All other question_context fields (question_text, expected_elements,
patterns, etc.) are derived at runtime from SignalRegistry, which
extracts them from the single source of truth: questionnaire_monolith.json.

This preserves:
  1. Single source of truth (no data duplication)
  2. Proper signal irrigation architecture
  3. Full Carver compatibility without modifying Carver code
  4. Contract size reduction (~70%)

Invariants
----------
[INV-H001] Hydrated contract MUST contain all fields EnhancedContractInterpreter expects
[INV-H002] Hydration is idempotent: hydrate(hydrate(c)) == hydrate(c)
[INV-H003] Overrides in v4 contract take precedence over irrigated values
[INV-H004] Original contract is never mutated; hydrate returns new dict

Author: F.A.R.F.A.N Pipeline
Version: 1.0.0
"""

from __future__ import annotations

import copy
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

logger = logging.getLogger(__name__)


class SignalPackProtocol(Protocol):
    """Protocol defining expected signal pack interface."""
    
    question_text: str
    question_type: str
    dimension_id: str
    policy_area_id: str
    scoring_modality: str
    modality: str
    expected_elements: Dict[str, List[Any]]
    question_patterns: Dict[str, List[Any]]


class SignalRegistryProtocol(Protocol):
    """Protocol for SignalRegistry dependency injection."""
    
    def get_micro_answering_signals(self, question_id: str) -> SignalPackProtocol:
        """Retrieve complete signal pack for a micro question."""
        ...


@dataclass(frozen=True)
class HydrationResult:
    """Result of contract hydration with metadata."""
    
    contract: Dict[str, Any]
    was_hydrated: bool
    source_question_id: str
    fields_injected: tuple[str, ...]
    overrides_applied: tuple[str, ...]
    
    def __post_init__(self) -> None:
        """Validate hydration result."""
        if self.was_hydrated and not self.source_question_id:
            raise ValueError("Hydrated contracts must have source_question_id")


class ContractHydrationError(Exception):
    """Raised when contract hydration fails."""
    
    def __init__(
        self,
        message: str,
        contract_id: Optional[str] = None,
        missing_fields: Optional[List[str]] = None,
    ) -> None:
        super().__init__(message)
        self.contract_id = contract_id
        self.missing_fields = missing_fields or []


class ContractHydrator:
    """
    Hydrates v4 contracts to Carver-compatible interface.
    
    V4 contracts store only:
      - question_context.monolith_ref (e.g., "Q230")
      - question_context.overrides (optional)
      - question_context.failure_contract
    
    This hydrator injects irrigated fields at runtime from SignalRegistry.
    
    Usage
    -----
    ```python
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_registry import QuestionnaireSignalRegistry
    from farfan_pipeline.phases.Phase_02.phase2_95_00_contract_hydrator import ContractHydrator
    
    signal_registry = QuestionnaireSignalRegistry(questionnaire)
    hydrator = ContractHydrator(signal_registry)
    
    # Hydrate v4 contract
    hydrated = hydrator.hydrate(v4_contract)
    
    # Now Carver can consume it
    synthesizer = DoctoralCarverSynthesizer()
    answer = synthesizer.synthesize(evidence, hydrated)
    ```
    
    Thread Safety
    -------------
    This class is thread-safe. The hydrate() method creates new dicts
    and never mutates inputs.
    """
    
    CARVER_REQUIRED_FIELDS: tuple[str, ...] = (
        "question_text",
        "question_type",
        "expected_elements",
        "patterns",
        "scoring_modality",
        "modality",
    )
    
    IDENTITY_FIELDS: tuple[str, ...] = (
        "dimension_id",
        "policy_area_id",
    )

    DEFAULT_TEMPLATE_BINDINGS: Dict[str, Dict[str, str]] = {
        "variables": {
            "verdict_statement": "synthesis.verdict",
            "final_confidence_pct": "synthesis.confidence_score * 100",
            "confidence_label": "synthesis.confidence_label",
            "method_count": "execution_stats.methods_executed",
            "audit_count": "execution_stats.validations_run",
            "blocked_count": "execution_stats.branches_blocked",
            "fact_count": "evidence_graph.nodes(type='FACT').count",
            "document_coverage_pct": "evidence_graph.metadata.coverage",
            "official_sources_list": "evidence_graph.nodes(type='FACT').groupby('source').list",
            "quantitative_indicators_list": "evidence_graph.nodes(type='FACT', subtype='quantitative').list",
            "veto_alert": "audit_results.veto_status",
            "veto_reason": "audit_results.primary_veto_reason",
            "validation_count": "audit_results.total_checks",
            "contradiction_count": "audit_results.contradictions.count",
            "contradiction_details": "audit_results.contradictions.list",
            "suppressed_count": "audit_results.suppressed_nodes.count",
            "suppression_details": "audit_results.suppressed_nodes.list",
            "partial_veto_count": "audit_results.partial_vetos.count",
            "empty_methods_count": "execution_stats.empty_methods",
            "total_methods": "method_binding.method_count",
            "empty_methods_details": "execution_stats.empty_methods_list",
            "missing_elements_list": "gap_analysis.missing_expected.list",
            "gap_impact_assessment": "gap_analysis.impact_statement"
        }
    }
    
    def __init__(self, signal_registry: SignalRegistryProtocol) -> None:
        """
        Initialize with signal registry.
        
        Args:
            signal_registry: Registry providing micro_answering_signals
        """
        self._signal_registry = signal_registry
        logger.debug("ContractHydrator initialized")
    
    def hydrate(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hydrate v4 contract to Carver-compatible interface.
        
        This method is idempotent: calling it on an already-hydrated
        or v3 contract returns the contract unchanged.
        
        Args:
            contract: V4 contract with monolith_ref, or v3 contract
            
        Returns:
            Hydrated contract with all fields Carver expects
            
        Raises:
            ContractHydrationError: If contract lacks required references
        """
        if self._is_already_hydrated(contract):
            logger.debug("Contract already hydrated, returning as-is")
            return contract
        
        question_id = self._extract_question_id(contract)
        if not question_id:
            raise ContractHydrationError(
                "Contract must have question_context.monolith_ref or identity.question_id",
                contract_id=contract.get("identity", {}).get("base_slot"),
            )
        
        try:
            signals = self._signal_registry.get_micro_answering_signals(question_id)
        except Exception as e:
            raise ContractHydrationError(
                f"Failed to fetch signals for {question_id}: {e}",
                contract_id=question_id,
            ) from e
        
        hydrated = copy.deepcopy(contract)
        
        question_context = hydrated.get("question_context", {})
        overrides = question_context.get("overrides") or {}
        
        fields_injected: List[str] = []
        overrides_applied: List[str] = []
        
        for field in self.CARVER_REQUIRED_FIELDS:
            override_value = overrides.get(field)
            
            if override_value is not None:
                question_context[field] = override_value
                overrides_applied.append(field)
            else:
                signal_value = self._extract_signal_value(signals, field, question_id)
                if signal_value is not None:
                    question_context[field] = signal_value
                    fields_injected.append(field)
        
        hydrated["question_context"] = question_context
        
        identity = hydrated.get("identity", {})
        for field in self.IDENTITY_FIELDS:
            if not identity.get(field):
                signal_value = getattr(signals, field, None)
                if signal_value:
                    identity[field] = signal_value
                    fields_injected.append(f"identity.{field}")
        hydrated["identity"] = identity
        
        # Inject template bindings for Carver v3.0 compatibility
        human_answer = hydrated.get("human_answer_structure", {})
        if "template_variable_bindings" not in human_answer:
            human_answer["template_variable_bindings"] = self.DEFAULT_TEMPLATE_BINDINGS
            fields_injected.append("human_answer_structure.template_variable_bindings")
        hydrated["human_answer_structure"] = human_answer
        
        hydrated["_hydration_metadata"] = {
            "was_hydrated": True,
            "source_question_id": question_id,
            "fields_injected": fields_injected,
            "overrides_applied": overrides_applied,
            "hydrator_version": "1.0.0",
        }
        
        logger.debug(
            f"Hydrated {question_id}: injected {len(fields_injected)} fields, "
            f"applied {len(overrides_applied)} overrides"
        )
        
        return hydrated
    
    def _extract_signal_value(
        self, signals: SignalPackProtocol, field: str, question_id: str
    ) -> Any:
        """Extract field value from signal pack, handling special cases."""
        if field == "expected_elements":
            elements_dict = getattr(signals, "expected_elements", {})
            elements = elements_dict.get(question_id, [])
            return self._serialize_items(elements)
        elif field == "patterns":
            patterns_dict = getattr(signals, "question_patterns", {})
            patterns = patterns_dict.get(question_id, [])
            return self._serialize_items(patterns)
        else:
            return getattr(signals, field, None)
    
    def _serialize_items(self, items: List[Any]) -> List[Any]:
        """Serialize Pydantic models to dicts."""
        result = []
        for item in items:
            if hasattr(item, "model_dump"):
                result.append(item.model_dump())
            elif hasattr(item, "dict"):
                result.append(item.dict())
            else:
                result.append(item)
        return result
    
    def hydrate_with_result(self, contract: Dict[str, Any]) -> HydrationResult:
        """
        Hydrate contract and return detailed result.
        
        Use this when you need metadata about the hydration process.
        
        Args:
            contract: Contract to hydrate
            
        Returns:
            HydrationResult with hydrated contract and metadata
        """
        if self._is_already_hydrated(contract):
            return HydrationResult(
                contract=contract,
                was_hydrated=False,
                source_question_id=self._extract_question_id(contract) or "",
                fields_injected=(),
                overrides_applied=(),
            )
        
        hydrated = self.hydrate(contract)
        metadata = hydrated.get("_hydration_metadata", {})
        
        return HydrationResult(
            contract=hydrated,
            was_hydrated=metadata.get("was_hydrated", True),
            source_question_id=metadata.get("source_question_id", ""),
            fields_injected=tuple(metadata.get("fields_injected", [])),
            overrides_applied=tuple(metadata.get("overrides_applied", [])),
        )
    
    def _is_already_hydrated(self, contract: Dict[str, Any]) -> bool:
        """Check if contract is already hydrated or is v3 format."""
        if contract.get("_hydration_metadata", {}).get("was_hydrated"):
            return True
        
        question_context = contract.get("question_context", {})
        
        for field in self.CARVER_REQUIRED_FIELDS:
            value = question_context.get(field)
            if value is None or value == "" or value == []:
                return False
        
        return True
    
    def _extract_question_id(self, contract: Dict[str, Any]) -> Optional[str]:
        """Extract question ID from contract."""
        question_context = contract.get("question_context", {})
        monolith_ref = question_context.get("monolith_ref")
        if monolith_ref:
            return monolith_ref
        
        identity = contract.get("identity", {})
        return identity.get("question_id")
    
    def is_v4_contract(self, contract: Dict[str, Any]) -> bool:
        """
        Check if contract is v4 format (streamlined).
        
        V4 contracts have:
          - question_context.monolith_ref present
          - question_context.question_text absent or empty
        
        Args:
            contract: Contract to check
            
        Returns:
            True if v4 format, False if v3 or already hydrated
        """
        question_context = contract.get("question_context", {})
        
        has_monolith_ref = bool(question_context.get("monolith_ref"))
        lacks_question_text = not question_context.get("question_text")
        lacks_expected_elements = not question_context.get("expected_elements")
        
        return has_monolith_ref and (lacks_question_text or lacks_expected_elements)
    
    def validate_hydrated_contract(self, contract: Dict[str, Any]) -> List[str]:
        """
        Validate that hydrated contract has all fields Carver needs.
        
        Args:
            contract: Contract to validate
            
        Returns:
            List of missing or invalid fields (empty if valid)
        """
        issues: List[str] = []
        question_context = contract.get("question_context", {})
        
        for field in self.CARVER_REQUIRED_FIELDS:
            value = question_context.get(field)
            if value is None:
                issues.append(f"Missing: question_context.{field}")
            elif value == "" or value == []:
                issues.append(f"Empty: question_context.{field}")
        
        identity = contract.get("identity", {})
        for field in self.IDENTITY_FIELDS:
            if not identity.get(field):
                issues.append(f"Missing: identity.{field}")
        
        return issues

"""
Module: src.canonic_phases.phase_2.sisas.phase2_signal_registry_adapter
Purpose: Adapter layer for SISAS signal registry integration
Owner: phase2_orchestration
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-18

Contracts-Enforced:
    - SISASAvailabilityContract: All required signals must be available
    - SignalSchemaContract: Signal definitions must match expected schema

Determinism:
    Seed-Strategy: NOT_APPLICABLE
    State-Management: Stateless adapter wrapping SISAS registry

Inputs:
    - question_id: str — Question identifier (Q001-Q300)
    - policy_area: Optional[str] — Policy area filter

Outputs:
    - signals: List[Signal] — Available signals for the question

Failure-Modes:
    - SignalNotFoundError: RuntimeError — Required signal not in registry
    - RegistryUnavailableError: RuntimeError — Cannot access SISAS registry
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from src.canonic_phases.phase_2.constants.phase2_constants import (
    SISAS_REGISTRY_PATH,
    SISAS_REQUIRED_SIGNALS,
)


class SignalNotFoundError(RuntimeError):
    """Raised when a required signal is not found in the registry."""
    pass


class RegistryUnavailableError(RuntimeError):
    """Raised when the SISAS registry cannot be accessed."""
    pass


class SISASAdapter:
    """
    Adapter layer for integrating with the SISAS (Signal Intelligence System).
    
    SUCCESS_CRITERIA: All required signals loaded and validated
    FAILURE_MODES: [SignalNotFoundError, RegistryUnavailableError]
    TERMINATION_CONDITION: All signals loaded or error raised
    CONVERGENCE_RULE: N/A (synchronous loading)
    VERIFICATION_STRATEGY: Signal schema validation
    """
    
    def __init__(self, registry_path: Optional[str] = None) -> None:
        """
        Initialize SISAS adapter.
        
        Args:
            registry_path: Path to SISAS registry (defaults to constant)
        """
        self.registry_path = Path(registry_path or SISAS_REGISTRY_PATH)
        if not self.registry_path.exists():
            raise RegistryUnavailableError(
                f"SISAS registry not found at {self.registry_path}"
            )
        
        # Lazy-load the actual SISAS modules
        self._signal_registry: Any = None
        self._signal_loader: Any = None
    
    def _ensure_loaded(self) -> None:
        """Lazy-load SISAS modules on first use."""
        if self._signal_registry is not None:
            return
        
        try:
            # Import SISAS modules dynamically to avoid circular dependencies
            from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS import (
                signal_registry,
                signal_loader,
            )
            self._signal_registry = signal_registry
            self._signal_loader = signal_loader
        except ImportError as e:
            raise RegistryUnavailableError(
                f"Cannot import SISAS modules: {e}"
            ) from e
    
    def load_signals_for_question(
        self,
        question_id: str,
        policy_area: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Load all signals available for a given question.
        
        Args:
            question_id: Question identifier (Q001-Q300)
            policy_area: Optional policy area filter
        
        Returns:
            List of signal dictionaries with metadata
        
        Raises:
            SignalNotFoundError: If required signals not found
            RegistryUnavailableError: If registry cannot be accessed
        """
        self._ensure_loaded()
        
        # TODO: Implement actual signal loading logic
        # This is a stub that needs to call the real SISAS registry
        signals = []
        
        # Verify required signals are available
        self._validate_required_signals(signals)
        
        return signals
    
    def get_signal_metadata(self, signal_id: str) -> Dict[str, Any]:
        """
        Get metadata for a specific signal.
        
        Args:
            signal_id: Signal identifier
        
        Returns:
            Signal metadata dictionary
        
        Raises:
            SignalNotFoundError: If signal not found
        """
        self._ensure_loaded()
        
        # TODO: Implement actual metadata retrieval
        return {}
    
    def validate_signal_compatibility(
        self,
        signal_id: str,
        method_name: str
    ) -> bool:
        """
        Validate that a signal is compatible with a method.
        
        Args:
            signal_id: Signal identifier
            method_name: Method name to check compatibility
        
        Returns:
            True if compatible, False otherwise
        """
        self._ensure_loaded()
        
        # TODO: Implement actual compatibility check
        return True
    
    def _validate_required_signals(
        self,
        signals: List[Dict[str, Any]]
    ) -> None:
        """
        Validate that all required signals are present.
        
        Args:
            signals: List of loaded signals
        
        Raises:
            SignalNotFoundError: If required signals missing
        """
        signal_ids = {sig.get("signal_id") for sig in signals}
        missing = SISAS_REQUIRED_SIGNALS - signal_ids
        
        if missing:
            raise SignalNotFoundError(
                f"Required signals missing from registry: {missing}"
            )

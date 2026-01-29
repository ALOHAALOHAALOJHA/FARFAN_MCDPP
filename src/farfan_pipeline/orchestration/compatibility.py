"""
Compatibility layer for deprecated Orchestrator imports.

MIGRATION GUIDE (v2.0 -> v3.0):
===============================

This module provides a bridge for legacy code. All legacy imports MUST be migrated
before v3.0.0.

Old Import                                  | New Import
------------------------------------------- | ----------------------------------------------------
orchestration.orchestrator.Orchestrator     | farfan_pipeline.orchestration.orchestrator.UnifiedOrchestrator
orchestration.factory.Factory               | farfan_pipeline.orchestration.factory.UnifiedFactory
orchestration.method_registry.*             | farfan_pipeline.orchestration.factory.UnifiedFactory.execute_contract()

DEPRECATION TIMELINE:
- v2.0 (Current): Warnings emitted, stubs provided.
- v2.5: Stubs raise error (optional flag to suppress).
- v3.0: This module is removed.

"""

import warnings
from typing import Any, Dict, List, Optional
import logging

class CompatibilityWarning(DeprecationWarning):
    """Warning for usage of deprecated orchestration components."""
    pass

def _warn_deprecated(old_name: str, new_name: str):
    warnings.warn(
        f"{old_name} is deprecated. Use {new_name} instead. Removal in v3.0.",
        CompatibilityWarning,
        stacklevel=3
    )

# =============================================================================
# REAL IMPORTS (Redirects)
# =============================================================================

try:
    from farfan_pipeline.phases.Phase_03.contracts.phase3_10_02_output_contract import ScoredMicroQuestion
except ImportError:
    class ScoredMicroQuestion: pass

try:
    from farfan_pipeline.phases.Phase_00.phase0_30_00_resource_controller import ResourceLimits
except ImportError:
    class ResourceLimits: pass

try:
    from farfan_pipeline.phases.Phase_02.registries.questionnaire_signal_registry import QuestionnaireSignalRegistry
except ImportError:
    class QuestionnaireSignalRegistry: pass

try:
    from farfan_pipeline.phases.Phase_03.contracts.phase3_10_00_input_contract import MicroQuestionRun
except ImportError:
    class MicroQuestionRun: pass

# =============================================================================
# STUBS (For missing/deleted classes)
# =============================================================================

class MethodExecutor:
    """Stub for deprecated MethodExecutor."""
    def __init__(self, *args, **kwargs):
        pass

class PhaseInstrumentation:
    """Stub for deprecated PhaseInstrumentation."""
    pass

class Evidence:
    """Stub for deprecated Evidence."""
    pass

class MacroEvaluation:
    """Stub for deprecated MacroEvaluation."""
    pass

class AbortSignal(Exception):
    """Stub for deprecated AbortSignal."""
    pass

class Orchestrator:
    """
    Compatibility Stub for the old Orchestrator.
    
    This class exists only to prevent ImportErrors in legacy code.
    Functionality is NOT guaranteed.
    """
    def __init__(self, method_executor=None, questionnaire=None, executor_config=None, runtime_config=None):
        self.logger = logging.getLogger(__name__)
        self.logger.warning("Using DEPRECATED Orchestrator stub. Please migrate to UnifiedOrchestrator.")
        self.method_executor = method_executor
        self.questionnaire = questionnaire

    def execute_phase(self, phase_id: str, context: Any = None):
        self.logger.warning(f"Orchestrator stub executing {phase_id} (NO-OP)")
        return {}
    
    def _validate_questionnaire_structure(self, *args, **kwargs):
        pass


class LegacyCoreOrchestrator:
    """
    Wrapper for backward compatibility.
    
    Proxies calls to UnifiedOrchestrator while emitting warnings.
    """
    def __init__(self, *args, **kwargs):
        _warn_deprecated("LegacyCoreOrchestrator", "UnifiedOrchestrator")
        from farfan_pipeline.orchestration.orchestrator import UnifiedOrchestrator, OrchestratorConfig
        
        # Try to map legacy config args to FactoryConfig/OrchestratorConfig if possible
        # For now, just initialize with defaults + overrides
        config = OrchestratorConfig() 
        self._delegate = UnifiedOrchestrator(config)
        
    def execute_phase(self, phase_id: str, *args, **kwargs):
        _warn_deprecated("execute_phase()", "UnifiedOrchestrator.execute()")
        # This is a best-effort mapping. Phase IDs might need mapping too.
        return self._delegate.execute_phase(phase_id)
        
    def __getattr__(self, name: str):
        # Proxy everything else
        return getattr(self._delegate, name)



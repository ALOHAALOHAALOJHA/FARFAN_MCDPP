"""
Compatibility layer for deprecated Orchestrator imports.

This module provides a bridge for legacy code importing from
'orchestration.orchestrator' or 'farfan_pipeline.orchestration.orchestrator'
expecting the old class structure.
"""

from typing import Any, Dict, List, Optional
import logging

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

    def validate_signals_for_questionnaire(self, *args, **kwargs):
        return {"valid": True} # Mock success


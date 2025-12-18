"""Phase 0: Input Validation - Canonical Implementation

This module provides the canonical Phase 0 implementation with strict
validation, deterministic execution, and exit gate enforcement.

All imports from Phase 0 should use this canonical path:
    from canonic_phases.phase_0_input_validation import ...

Legacy imports via canonic_phases.Phase_zero are deprecated but temporarily
supported via compatibility shim.
"""

from __future__ import annotations

__all__ = [
    "RuntimeConfig",
    "RuntimeMode",
    "get_runtime_config",
    "BootCheckError",
    "run_boot_checks",
    "GateResult",
    "check_all_gates",
    "Phase0Result",
    "PROJECT_ROOT",
    "CONFIG_DIR",
    "DATA_DIR",
    "QUESTIONNAIRE_FILE",
]

from canonic_phases.phase_0_input_validation.phase0_runtime_config import (
    RuntimeConfig,
    RuntimeMode,
    get_runtime_config,
)
from canonic_phases.phase_0_input_validation.phase0_boot_checks import (
    BootCheckError,
    run_boot_checks,
)
from canonic_phases.phase_0_input_validation.phase0_exit_gates import (
    GateResult,
    check_all_gates,
)
from canonic_phases.phase_0_input_validation.phase0_paths import (
    PROJECT_ROOT,
    CONFIG_DIR,
    DATA_DIR,
    QUESTIONNAIRE_FILE,
)
from canonic_phases.phase_0_input_validation.phase0_results import Phase0Result

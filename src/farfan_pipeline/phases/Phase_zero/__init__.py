"""Phase 0 legacy compatibility shim.

DEPRECATED: This module is deprecated. Use the canonical path instead:
    from canonic_phases.phase_0_input_validation import ...

This shim redirects imports to the canonical Phase 0 implementation.
"""

from __future__ import annotations

# Re-export everything from canonical Phase 0
from canonic_phases.phase_0_input_validation import (
    RuntimeConfig,
    RuntimeMode,
    get_runtime_config,
    BootCheckError,
    run_boot_checks,
    GateResult,
    check_all_gates,
    Phase0Result,
    PROJECT_ROOT,
    CONFIG_DIR,
    DATA_DIR,
    QUESTIONNAIRE_FILE,
)

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

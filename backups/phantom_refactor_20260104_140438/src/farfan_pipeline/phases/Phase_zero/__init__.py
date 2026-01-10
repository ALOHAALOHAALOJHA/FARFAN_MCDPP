"""
Module: src.farfan_pipeline.phases.Phase_zero
PHASE_LABEL: Phase 0
Purpose: Package initialization for Phase 0 - Validation, Hardening & Bootstrap
Owner: phase0_core
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-29

Phase 0 of the F.A.R.F.A.N pipeline responsible for:
1. Validating and normalizing input documents
2. Enforcing hard resource limits at kernel level
3. Pre-flight checks before pipeline execution
4. Determinism enforcement for reproducibility
5. Bootstrap and wiring initialization

This phase ensures that all inputs meet the required preconditions for
downstream phases and that execution occurs within safe resource bounds.

STAGE TAXONOMY:
    Stage 00: Infrastructure (errors, types, init)
    Stage 10: Environment Configuration (paths, config, logging)
    Stage 20: Determinism Enforcement (seeds, hashing, reproducibility)
    Stage 30: Resource Control (limits, watchdog, enforcement)
    Stage 40: Validation (input, schema, signature, coverage)
    Stage 50: Boot Sequence (checks, gates, wiring verification)
    Stage 90: Integration (main entry, runner, bootstrap orchestration)

RESOURCE ENFORCEMENT:
    Set ENFORCE_RESOURCES=true to enable kernel-level limits via setrlimit().
    Configure limits via:
        RESOURCE_MEMORY_MB (default: 2048)
        RESOURCE_CPU_SECONDS (default: 300)
        RESOURCE_DISK_MB (default: 500)
        RESOURCE_FILE_DESCRIPTORS (default: 1024)
"""

from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2025-12-29"
__modified__ = "2025-12-29"

# Legacy compatibility
PHASE_LABEL = "Phase 0"

# =============================================================================
# IMPORTS FROM CANONICAL MODULES
# =============================================================================

# Stage 00: Infrastructure
from .phase0_00_01_domain_errors import (
    ContractViolationError,
    DataContractError,
    SystemContractError,
)

# Stage 30: Resource Control
from .phase0_30_00_resource_controller import (
    ResourceController,
    ResourceLimits,
    ResourceExhausted,
    MemoryWatchdog,
    EnforcementMetrics,
    PSUTIL_AVAILABLE,
)

# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Metadata
    "PHASE_LABEL",
    "__version__",
    "__phase__",
    # Stage 00: Infrastructure
    "ContractViolationError",
    "DataContractError",
    "SystemContractError",
    # Stage 30: Resource Control
    "ResourceController",
    "ResourceLimits",
    "ResourceExhausted",
    "MemoryWatchdog",
    "EnforcementMetrics",
    "PSUTIL_AVAILABLE",
]

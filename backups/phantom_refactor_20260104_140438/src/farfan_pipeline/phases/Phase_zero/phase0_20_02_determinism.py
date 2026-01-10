"""
Determinism Module - Consolidated Seed Management
==================================================

Provides centralized determinism enforcement for the F.A.R.F.A.N pipeline:
- Seed derivation from policy_unit_id and correlation_id
- RNG seeding for Python, NumPy, and advanced components
- Validation of seed application

This module consolidates:
- determinism_helpers.py (seed derivation, context manager)
- seed_factory.py (seed generation)
- Integration with global SeedRegistry

Author: Phase 0 Compliance Team
Version: 2.0.0
Specification: P00-EN v2.0 Section 3.4
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import random
from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Iterator

if TYPE_CHECKING:
    from farfan_pipeline.orchestration.seed_registry import SeedRegistry

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None  # type: ignore


# Required seeds for Phase 0 compliance
MANDATORY_SEEDS = ["python", "numpy"]
OPTIONAL_SEEDS = ["quantum", "neuromorphic", "meta_learner"]
ALL_SEEDS = MANDATORY_SEEDS + OPTIONAL_SEEDS


@dataclass(frozen=True)
class Seeds:
    """Container for seeds used in deterministic execution."""

    python: int
    numpy: int
    quantum: int | None = None
    neuromorphic: int | None = None
    meta_learner: int | None = None

    def to_dict(self) -> dict[str, int | None]:
        """Convert to dictionary for logging."""
        return {
            "python": self.python,
            "numpy": self.numpy,
            "quantum": self.quantum,
            "neuromorphic": self.neuromorphic,
            "meta_learner": self.meta_learner,
        }


def derive_seed_from_string(base_material: str, salt: bytes | None = None) -> int:
    """
    Derive deterministic seed from string using HMAC-SHA256.

    Args:
        base_material: String to hash (e.g., "PU_123:corr-1:python")
        salt: Optional salt for HMAC (default: fixed deployment salt)

    Returns:
        32-bit unsigned integer seed

    Example:
        >>> seed1 = derive_seed_from_string("PU_123:corr-1:python")
        >>> seed2 = derive_seed_from_string("PU_123:corr-1:python")
        >>> assert seed1 == seed2  # Deterministic
    """
    default_salt = b"FARFAN_PHASE0_DETERMINISTIC_SEED_2025"
    actual_salt = default_salt if salt is None else salt

    seed_hmac = hmac.new(
        key=actual_salt, msg=base_material.encode("utf-8"), digestmod=hashlib.sha256
    )

    seed_bytes = seed_hmac.digest()[:4]
    return int.from_bytes(seed_bytes, byteorder="big")


def derive_seed_from_parts(*parts: Any, salt: bytes | None = None) -> int:
    """
    Derive seed from arbitrary components via JSON serialization.

    Args:
        *parts: Components to hash (will be JSON-serialized)
        salt: Optional HMAC salt

    Returns:
        32-bit integer seed

    Example:
        >>> s1 = derive_seed_from_parts("PU_123", "corr-1", "python")
        >>> s2 = derive_seed_from_parts("PU_123", "corr-1", "python")
        >>> assert s1 == s2  # Deterministic
    """
    canonical = json.dumps(parts, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return derive_seed_from_string(canonical, salt)


def apply_seeds_to_rngs(seeds: dict[str, int]) -> dict[str, bool]:
    """
    Apply seeds to all available RNGs.

    Args:
        seeds: Dictionary mapping component names to seed values

    Returns:
        Dictionary mapping component names to success status

    Raises:
        ValueError: If mandatory seeds are missing

    Example:
        >>> seeds = {"python": 12345, "numpy": 67890}
        >>> status = apply_seeds_to_rngs(seeds)
        >>> assert status["python"]
        >>> assert status["numpy"]
    """
    status = {}

    # Validate mandatory seeds
    missing = [s for s in MANDATORY_SEEDS if seeds.get(s) is None]
    if missing:
        raise ValueError(f"Missing mandatory seeds: {missing}")

    # Apply python seed (MANDATORY)
    python_seed = seeds["python"]
    random.seed(python_seed)
    status["python"] = True

    # Apply numpy seed (MANDATORY)
    if NUMPY_AVAILABLE and np is not None:
        numpy_seed = seeds["numpy"]
        np.random.seed(numpy_seed)
        status["numpy"] = True
    else:
        status["numpy"] = False

    # Apply optional seeds (best-effort)
    for component in OPTIONAL_SEEDS:
        seed = seeds.get(component)
        if seed is not None:
            # These components don't have global RNGs to seed yet
            # But we record them for future use
            status[component] = True
        else:
            status[component] = False

    return status


def validate_seed_application(
    seeds: dict[str, int], status: dict[str, bool]
) -> tuple[bool, list[str]]:
    """
    Validate that all required seeds were applied successfully.

    Args:
        seeds: Dictionary of seeds that were attempted
        status: Dictionary of application results from apply_seeds_to_rngs()

    Returns:
        Tuple of (success, errors)
        - success: True if all mandatory seeds applied
        - errors: List of error messages

    Example:
        >>> seeds = {"python": 12345, "numpy": 67890}
        >>> status = apply_seeds_to_rngs(seeds)
        >>> success, errors = validate_seed_application(seeds, status)
        >>> assert success
        >>> assert len(errors) == 0
    """
    errors = []

    # Check mandatory seeds
    for component in MANDATORY_SEEDS:
        if not status.get(component, False):
            errors.append(f"Failed to apply {component} seed")

    # Warn about optional seeds (but don't fail)
    missing_optional = [c for c in OPTIONAL_SEEDS if not status.get(c, False)]
    if missing_optional:
        # This is informational, not an error
        pass

    return len(errors) == 0, errors


def initialize_determinism_from_registry(
    seed_registry: SeedRegistry, policy_unit_id: str, correlation_id: str
) -> tuple[dict[str, int], dict[str, bool], list[str]]:
    """
    Initialize determinism using SeedRegistry (Phase 0.3 implementation).

    This is the PRIMARY method for Phase 0 determinism initialization.

    Args:
        seed_registry: Global seed registry instance
        policy_unit_id: Policy unit identifier
        correlation_id: Execution correlation identifier

    Returns:
        Tuple of (seeds, status, errors)
        - seeds: Dictionary of generated seeds
        - status: Dictionary of application status
        - errors: List of errors (empty if successful)

    Note:
        Errors (including missing mandatory seeds) are reported via the
        returned errors list rather than by raising exceptions.

    Specification:
        P00-EN v2.0 Section 3.4 - Determinism Context

    Example:
        >>> from farfan_pipeline.orchestration.seed_registry import get_global_seed_registry
        >>> registry = get_global_seed_registry()
        >>> seeds, status, errors = initialize_determinism_from_registry(
        ...     registry, "plan_2024", "exec_001"
        ... )
        >>> assert not errors
        >>> assert status["python"] and status["numpy"]
    """
    # Get seeds from registry
    seeds = seed_registry.get_seeds_for_context(
        policy_unit_id=policy_unit_id, correlation_id=correlation_id
    )

    # Validate mandatory seeds present
    missing = [s for s in MANDATORY_SEEDS if seeds.get(s) is None]
    if missing:
        error = f"Missing mandatory seeds from registry: {missing}"
        return seeds, {}, [error]

    # Apply seeds to RNGs
    try:
        status = apply_seeds_to_rngs(seeds)
    except Exception as e:
        return seeds, {}, [f"Failed to apply seeds: {e}"]

    # Validate application
    success, errors = validate_seed_application(seeds, status)

    if not success:
        return seeds, status, errors

    return seeds, status, []


@contextmanager
def deterministic(
    policy_unit_id: str | None = None, correlation_id: str | None = None
) -> Iterator[Seeds]:
    """
    Context manager for scoped deterministic execution.

    Seeds Python random and NumPy random based on policy_unit_id and
    correlation_id. Seeds are derived deterministically via SHA-256.

    Args:
        policy_unit_id: Policy unit identifier (default: env var or "default")
        correlation_id: Correlation identifier (default: env var or "run")

    Yields:
        Seeds object with seed values

    Example:
        >>> with deterministic("PU_123", "corr-1") as seeds:
        ...     v1 = random.random()
        ...     a1 = np.random.rand(3)
        >>> with deterministic("PU_123", "corr-1") as seeds:
        ...     v2 = random.random()
        ...     a2 = np.random.rand(3)
        >>> assert v1 == v2  # Deterministic
    """
    base = policy_unit_id or os.getenv("POLICY_UNIT_ID", "default")
    salt = correlation_id or os.getenv("CORRELATION_ID", "run")

    # Derive seeds for mandatory components
    python_seed = derive_seed_from_parts(base, salt, "python")
    numpy_seed = derive_seed_from_parts(base, salt, "numpy")
    quantum_seed = derive_seed_from_parts(base, salt, "quantum")
    neuromorphic_seed = derive_seed_from_parts(base, salt, "neuromorphic")
    meta_learner_seed = derive_seed_from_parts(base, salt, "meta_learner")

    # Apply mandatory seeds
    random.seed(python_seed)
    if NUMPY_AVAILABLE and np is not None:
        np.random.seed(numpy_seed)

    try:
        yield Seeds(
            python=python_seed,
            numpy=numpy_seed,
            quantum=quantum_seed,
            neuromorphic=neuromorphic_seed,
            meta_learner=meta_learner_seed,
        )
    finally:
        pass  # Keep seeded state


def create_deterministic_rng(seed: int) -> Any:
    """
    Create a local deterministic NumPy RNG (doesn't affect global state).

    Args:
        seed: Integer seed

    Returns:
        NumPy Generator instance (or None if NumPy unavailable)

    Example:
        >>> rng = create_deterministic_rng(42)
        >>> if rng is not None:
        ...     v1 = rng.random()
        ...     rng = create_deterministic_rng(42)
        ...     v2 = rng.random()
        ...     assert v1 == v2
    """
    if not NUMPY_AVAILABLE or np is None:
        return None
    return np.random.default_rng(seed)


__all__ = [
    "MANDATORY_SEEDS",
    "OPTIONAL_SEEDS",
    "ALL_SEEDS",
    "Seeds",
    "derive_seed_from_string",
    "derive_seed_from_parts",
    "apply_seeds_to_rngs",
    "validate_seed_application",
    "initialize_determinism_from_registry",
    "deterministic",
    "create_deterministic_rng",
]

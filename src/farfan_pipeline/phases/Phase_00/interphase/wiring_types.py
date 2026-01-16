"""
Wiring Types and Protocols.

This module defines the data structures and protocols used in the wiring process.
It serves as the 'interphase' definition to break circular dependencies.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signals import (
        SignalClient,
        SignalRegistry,
    )
    from farfan_pipeline.phases.Phase_02.phase2_10_03_executor_config import ExecutorConfig
    from farfan_pipeline.phases.Phase_02.phase2_60_02_arg_router import ExtendedArgRouter
    from farfan_pipeline.phases.Phase_00.primitives.providers import (
        CoreModuleFactory,
        QuestionnaireResourceProvider,
    )
    # Forward reference to Validator to avoid cycle
    from farfan_pipeline.phases.Phase_00.phase0_90_03_wiring_validator import WiringValidator

# =============================================================================
# SEVERITY LEVELS
# =============================================================================


class Severity(str, Enum):
    """Violation severity levels."""

    CRITICAL = "CRITICAL"  # Impossible to continue
    HIGH = "HIGH"  # Compromises result quality
    MEDIUM = "MEDIUM"  # Performance degradation
    LOW = "LOW"  # Cosmetic / best practices


# =============================================================================
# CONTRACT VIOLATION
# =============================================================================


@dataclass
class ContractViolation:
    """Represents a single contract violation detected during validation."""

    type: str
    severity: Severity
    component_path: str
    message: str
    expected: Any = None
    actual: Any = None
    remediation: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for JSON output."""
        return {
            "type": self.type,
            "severity": self.severity.value,
            "component_path": self.component_path,
            "message": self.message,
            "expected": str(self.expected) if self.expected is not None else None,
            "actual": str(self.actual) if self.actual is not None else None,
            "remediation": self.remediation,
            "timestamp": self.timestamp.isoformat(),
        }

    def format_console(self) -> str:
        """Format for human-readable console output."""
        lines = [
            f"[{self.severity.value}] {self.type}: {self.message}",
        ]
        if self.expected is not None:
            lines.append(f"  -> Expected: {self.expected}")
        if self.actual is not None:
            lines.append(f"  -> Actual: {self.actual}")
        if self.remediation:
            lines.append(f"  -> Remediation: {self.remediation}")
        lines.append(f"  -> Component: {self.component_path}")
        return "\n".join(lines)


# =============================================================================
# VALIDATION RESULT
# =============================================================================


@dataclass
class ValidationResult:
    """Result of WiringValidator.validate() call."""

    passed: bool
    violations: list[ContractViolation] = field(default_factory=list)
    integrity_hash: str = ""
    validation_time_ms: float = 0.0

    @property
    def critical_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == Severity.CRITICAL)

    @property
    def high_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == Severity.HIGH)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for JSON output."""
        return {
            "validation_status": "PASSED" if self.passed else "FAILED",
            "violations": [v.to_dict() for v in self.violations],
            "total_violations": len(self.violations),
            "critical_count": self.critical_count,
            "high_count": self.high_count,
            "integrity_hash": self.integrity_hash,
            "validation_time_ms": round(self.validation_time_ms, 2),
        }

    def format_console(self) -> str:
        """Format all violations for console output."""
        if self.passed:
            return f"✅ Wiring validation PASSED (hash: {self.integrity_hash[:16]}...)"

        lines = [
            f"❌ Wiring validation FAILED: {len(self.violations)} violation(s)",
            f"   Critical: {self.critical_count}, High: {self.high_count}",
            "",
        ]
        for v in self.violations:
            lines.append(v.format_console())
            lines.append("")
        return "\n".join(lines)


# =============================================================================
# FEATURE FLAGS
# =============================================================================


@dataclass
class WiringFeatureFlags:
    """Feature flags for wiring configuration."""

    enable_http_signals: bool = False
    enable_calibration: bool = False
    strict_validation: bool = True
    memory_signal_ttl: int = 3600
    enable_resource_enforcement: bool = False

    @classmethod
    def from_env(cls) -> WiringFeatureFlags:
        """Load flags from environment variables."""
        return cls(
            enable_http_signals=os.getenv("ENABLE_HTTP_SIGNALS", "false").lower() == "true",
            enable_calibration=os.getenv("ENABLE_CALIBRATION", "false").lower() == "true",
            strict_validation=os.getenv("STRICT_VALIDATION", "true").lower() == "true",
            memory_signal_ttl=int(os.getenv("MEMORY_SIGNAL_TTL", "3600")),
            enable_resource_enforcement=os.getenv("ENFORCE_RESOURCES", "false").lower() == "true",
        )

    def validate(self) -> list[str]:
        """Validate flag combinations and return warnings."""
        warnings = []
        if self.enable_http_signals and self.memory_signal_ttl < 60:
            warnings.append("HTTP signals with TTL < 60s may cause excessive network calls")
        return warnings

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "enable_http_signals": self.enable_http_signals,
            "enable_calibration": self.enable_calibration,
            "strict_validation": self.strict_validation,
            "memory_signal_ttl": self.memory_signal_ttl,
            "enable_resource_enforcement": self.enable_resource_enforcement,
        }


# =============================================================================
# WIRING COMPONENTS
# =============================================================================


@dataclass
class WiringComponents:
    """Container for all wired components.

    Attributes:
        provider: QuestionnaireResourceProvider
        signal_client: SignalClient (memory:// or HTTP)
        signal_registry: SignalRegistry with TTL and LRU
        executor_config: ExecutorConfig with defaults
        factory: CoreModuleFactory with DI
        arg_router: ExtendedArgRouter with special routes
        class_registry: Class registry for routing
        validator: WiringValidator for contract checking
        flags: Feature flags used during initialization
        init_hashes: Hashes computed during initialization
    """

    provider: QuestionnaireResourceProvider
    signal_client: SignalClient
    signal_registry: SignalRegistry
    executor_config: ExecutorConfig
    factory: CoreModuleFactory
    arg_router: ExtendedArgRouter
    class_registry: dict[str, type]
    validator: WiringValidator
    flags: WiringFeatureFlags
    calibration_orchestrator: Any | None = None  # Typed as Any to avoid complexity
    init_hashes: dict[str, str] = field(default_factory=dict)


# =============================================================================
# VALIDATOR PROTOCOL
# =============================================================================


class TierValidator(Protocol):
    """Protocol for tier-specific validators."""

    def validate(self, wiring: WiringComponents) -> list[ContractViolation]:
        """Execute tier validation and return violations."""
        ...
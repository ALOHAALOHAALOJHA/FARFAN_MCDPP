"""
Path and Import Policy Contracts

Authoritative, type-safe policy definitions for validating imports and filesystem paths.
Used by both static analysis (AST) and dynamic runtime guards.

This module is the single source of truth for:
- How violations are represented.
- How success/failure is computed.
- How reports are serialized into verification_manifest.json.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import FrozenSet, List, Literal, Optional, Dict, Any


PolicyKind = Literal["static_import", "dynamic_import", "path", "sys_path"]


@dataclass(frozen=True)
class PolicyViolation:
    """A single policy violation detected during verification."""

    kind: PolicyKind
    message: str
    file: Optional[Path] = None
    line: Optional[int] = None
    operation: Optional[str] = None  # e.g. "open", "import", "rename"
    target: Optional[str] = None  # module name or path string

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "kind": self.kind,
            "message": self.message,
            "file": str(self.file) if self.file else None,
            "line": self.line,
            "operation": self.operation,
            "target": self.target,
        }


@dataclass
class PolicyReport:
    """
    Aggregated report of all policy violations.

    A run is considered "clean" only if violation_count() == 0.
    """

    static_import_violations: List[PolicyViolation] = field(default_factory=list)
    dynamic_import_violations: List[PolicyViolation] = field(default_factory=list)
    path_violations: List[PolicyViolation] = field(default_factory=list)
    sys_path_violations: List[PolicyViolation] = field(default_factory=list)

    def ok(self) -> bool:
        """Return True if no violations exist."""
        return self.violation_count() == 0

    def violation_count(self) -> int:
        """Total number of violations."""
        return (
            len(self.static_import_violations)
            + len(self.dynamic_import_violations)
            + len(self.path_violations)
            + len(self.sys_path_violations)
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary form, suitable for embedding in verification_manifest.json.
        """
        return {
            "success": self.ok(),
            "violation_count": self.violation_count(),
            "static_import_violations": [v.to_dict() for v in self.static_import_violations],
            "dynamic_import_violations": [v.to_dict() for v in self.dynamic_import_violations],
            "path_violations": [v.to_dict() for v in self.path_violations],
            "sys_path_violations": [v.to_dict() for v in self.sys_path_violations],
        }


@dataclass(frozen=True)
class ImportPolicy:
    """
    Policy controlling allowed imports.

    "Maximum hardness" interpretation:
    - Only modules that match:
        - allowed_internal_prefixes, or
        - stdlib_modules, or
        - allowed_third_party
      are allowed.
    - Dynamic imports must use module names in allowed_dynamic_imports.
    """

    allowed_internal_prefixes: FrozenSet[str]
    allowed_third_party: FrozenSet[str]
    allowed_dynamic_imports: FrozenSet[str]
    stdlib_modules: FrozenSet[str]


@dataclass(frozen=True)
class PathPolicy:
    """
    Policy controlling filesystem access.

    "Maximum hardness" interpretation:
    - Any path access outside the cones encoded here is a violation.
    """

    repo_root: Path
    allowed_write_prefixes: FrozenSet[Path]
    allowed_read_prefixes: FrozenSet[Path]
    allowed_external_prefixes: FrozenSet[Path]


def merge_policy_reports(reports: List[PolicyReport]) -> PolicyReport:
    """
    Merge multiple PolicyReport objects into one.

    Args:
        reports: List of PolicyReport objects.

    Returns:
        Merged PolicyReport with all violations.
    """
    merged = PolicyReport()

    for report in reports:
        merged.static_import_violations.extend(report.static_import_violations)
        merged.dynamic_import_violations.extend(report.dynamic_import_violations)
        merged.path_violations.extend(report.path_violations)
        merged.sys_path_violations.extend(report.sys_path_violations)

    return merged
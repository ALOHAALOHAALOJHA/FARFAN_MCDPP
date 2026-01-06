"""
Calibration Layer Core Types
============================

Module:  calibration_core.py
Owner: farfan_pipeline. infrastructure.calibration
Purpose:  Foundational types for calibration within epistemic regime
Lifecycle State:  DESIGN-TIME FROZEN, RUNTIME IMMUTABLE
Schema Version: 2.0.0

INVARIANTS ENFORCED:
    INV-CAL-FREEZE-001: All calibration parameters immutable post-construction
    INV-CAL-REGIME-001: Calibration operates within existing epistemic regime
    INV-CAL-AUDIT-001: All parameters subject to N3-AUD verification
    INV-CAL-HASH-001: Canonical JSON serialization for deterministic hashing
    INV-CAL-TZ-001: All timestamps timezone-aware UTC
    INV-CAL-SIG-001: Optional Ed25519 signatures for cryptographic attestation

DESIGN PRINCIPLES:
    - Extensible parameter set via immutable mapping (not fixed fields)
    - Canonical serialization for cross-system verification
    - Structured validity status (no boolean ambiguity)
    - Full provenance chain with commit-pinned evidence references

VERIFICATION STRATEGY:
    - Property-based tests via Hypothesis for invariant coverage
    - Round-trip serialization tests for hash stability
    - Signature verification tests with known test vectors

FAILURE MODES:
    - FM-001: Invalid bounds (lower > upper) → ValidationError at construction
    - FM-002: Value outside bounds → ValidationError at construction
    - FM-003: Timezone-naive datetime → ValidationError at construction
    - FM-004: Malformed evidence path → ValidationError at construction
    - FM-005: Invalid commit SHA format → ValidationError at construction
    - FM-006: Missing required parameters → ValidationError at construction
    - FM-007: Signature verification failure → IntegrityError at verification
    - FM-008: Expired calibration → detected via validity_status_at()

DEPENDENCIES:
    - Standard library only for core types (no external crypto in base)
    - Optional:  cryptography (Ed25519) for signature operations
"""
from __future__ import annotations

import hashlib
import json
import logging
import math
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import (
    TYPE_CHECKING,
    Final,
    Mapping,
    Self,
    Sequence,
)

if TYPE_CHECKING:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )

# =============================================================================
# MODULE CONSTANTS
# =============================================================================

SCHEMA_VERSION: Final[str] = "2.0.0"
HASH_ALGORITHM: Final[str] = "sha256"
COMMIT_SHA_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{40}$")
UNIT_OF_ANALYSIS_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[A-Z]{2,6}-[0-9]{4,12}$")
VALID_EVIDENCE_PREFIXES: Final[frozenset[str]] = frozenset({"src/", "artifacts/", "docs/"})


# =============================================================================
# EXCEPTIONS
# =============================================================================


class CalibrationError(Exception):
    """Base exception for calibration module errors."""

    pass


class ValidationError(CalibrationError):
    """
    Raised when calibration invariants are violated at construction time. 

    This exception indicates a programming error or invalid configuration,
    not a runtime condition that can be recovered from.
    """

    pass


class IntegrityError(CalibrationError):
    """
    Raised when cryptographic verification fails.

    This exception indicates potential tampering or corruption of
    calibration data and must be treated as a security event.
    """

    pass


class ExpirationError(CalibrationError):
    """
    Raised when attempting to use expired calibration parameters.

    This exception is raised only when strict expiration checking is enabled.
    Non-strict mode returns ValidityStatus for caller to handle.
    """

    pass


# =============================================================================
# ENUMERATIONS
# =============================================================================


class CalibrationPhase(Enum):
    """
    Phase in which calibration applies.

    Each phase has distinct calibration requirements and validity windows.
    """

    INGESTION = auto()
    PHASE_2_COMPUTATION = auto()
    PHASE_3_AGGREGATION = auto()


class ValidityStatus(Enum):
    """
    Explicit validity states for calibration parameters.

    Using an enumeration instead of boolean prevents silent misinterpretation
    of edge cases (e.g., treating "expiring soon" as "invalid").
    """

    NOT_YET_VALID = auto()  # calibrated_at is in the future
    VALID = auto()  # within validity window, not near expiry
    EXPIRING_SOON = auto()  # within 10% of expiry window remaining
    EXPIRED = auto()  # past expires_at


# =============================================================================
# SERIALIZATION UTILITIES
# =============================================================================


def _canonical_json(obj: Mapping[str, object] | Sequence[object]) -> bytes:
    """
    Produce canonical JSON bytes for deterministic hashing.

    Specification:
        - Keys sorted lexicographically (recursive)
        - No whitespace between tokens
        - UTF-8 encoding
        - Floats rendered with repr() precision
        - No NaN or Infinity values permitted (raises ValueError)

    This function is the SINGLE SOURCE OF TRUTH for serialization
    used in content hashing.  Any change here invalidates all existing hashes.

    Args:
        obj:  Mapping or sequence to serialize.

    Returns:
        UTF-8 encoded bytes of canonical JSON.

    Raises:
        ValueError:  If obj contains NaN or Infinity float values.
    """
    try:
        return json.dumps(
            obj,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
            default=str,  # datetime.isoformat() fallback
        ).encode("utf-8")
    except ValueError as exc:
        if "Out of range float values" in str(exc):
            raise ValueError("NaN or Infinity float values are not permitted in canonical JSON") from exc
        raise


def _compute_sha256(data: bytes) -> str:
    """
    Compute SHA-256 hash of bytes and return lowercase hex digest.

    Args:
        data: Bytes to hash.

    Returns:
        64-character lowercase hexadecimal string.
    """
    return hashlib.sha256(data).hexdigest()


# =============================================================================
# CORE VALUE TYPES
# =============================================================================


@dataclass(frozen=True, slots=True)
class ClosedInterval:
    """
    Closed interval [lower, upper] with algebraic operations.

    A ClosedInterval represents a continuous range of valid values for
    calibration parameters. The interval is closed, meaning both endpoints
    are included in the valid range.

    Invariants:
        INV-INT-001: lower <= upper (enforced at construction)
        INV-INT-002: No NaN or Inf values permitted

    Attributes:
        lower: Lower bound of the interval (inclusive).
        upper: Upper bound of the interval (inclusive).
    """

    lower: float
    upper: float

    def __post_init__(self) -> None:
        """Validate interval invariants at construction."""
        # INV-INT-002: No NaN or Inf
        if math.isnan(self.lower) or math.isnan(self.upper):
            raise ValidationError(
                f"Interval bounds cannot be NaN: lower={self.lower}, upper={self.upper}"
            )
        if math.isinf(self.lower) or math.isinf(self.upper):
            raise ValidationError(
                f"Interval bounds must be finite: lower={self.lower}, upper={self.upper}"
            )
        # INV-INT-001: lower <= upper
        if self.lower > self.upper:
            raise ValidationError(
                f"Malformed interval: lower ({self.lower}) > upper ({self.upper})"
            )

    def contains(self, value: float) -> bool:
        """
        Check if value is within the closed interval [lower, upper].

        Args:
            value: The value to check for membership.

        Returns:
            True if lower <= value <= upper, False otherwise. 

        Raises:
            ValidationError: If value is NaN. 
        """
        if math. isnan(value):
            raise ValidationError(f"Cannot check membership of NaN value")
        return self.lower <= value <= self. upper

    def intersect(self, other: ClosedInterval) -> ClosedInterval | None:
        """
        Compute the intersection of two intervals.

        Args:
            other: Another ClosedInterval to intersect with.

        Returns:
            A new ClosedInterval representing the intersection,
            or None if the intervals are disjoint.
        """
        new_lower = max(self.lower, other.lower)
        new_upper = min(self.upper, other.upper)
        if new_lower > new_upper: 
            return None
        return ClosedInterval(lower=new_lower, upper=new_upper)

    def width(self) -> float:
        """
        Compute the width of the interval. 

        Returns:
            The difference (upper - lower).
        """
        return self. upper - self.lower

    def midpoint(self) -> float:
        """
        Compute the midpoint of the interval.

        Returns:
            The arithmetic mean of lower and upper bounds.
        """
        return (self.lower + self.upper) / 2.0

    def relative_position(self, value: float) -> float:
        """
        Compute the relative position of a value within the interval.

        Args:
            value: The value to locate.

        Returns:
            A float in [0, 1] indicating position from lower to upper.
            Returns 0.0 if value <= lower, 1.0 if value >= upper. 

        Raises:
            ValidationError: If value is NaN or interval has zero width.
        """
        if math.isnan(value):
            raise ValidationError("Cannot compute relative position of NaN")
        width = self.width()
        if width == 0.0:
            raise ValidationError("Cannot compute relative position in zero-width interval")
        if value <= self.lower:
            return 0.0
        if value >= self.upper:
            return 1.0
        return (value - self.lower) / width

    def to_canonical_dict(self) -> dict[str, float]:
        """
        Convert to canonical dictionary for hashing.

        Returns:
            Dictionary with 'lower' and 'upper' keys.
        """
        return {"lower": self.lower, "upper": self.upper}


@dataclass(frozen=True, slots=True)
class EvidenceReference:
    """
    Structured reference to calibration evidence in the repository.

    Evidence references pin calibration decisions to specific artifacts
    at specific commits, enabling full reproducibility and audit trails. 

    Invariants:
        INV-EV-001: path must be relative to repository root, under allowed prefixes
        INV-EV-002: commit_sha must be 40-character lowercase hex string
        INV-EV-003: description must be non-empty

    Attributes:
        path:  Relative path from repository root to evidence artifact.
        commit_sha: Full 40-character SHA-1 hash of the commit containing the evidence.
        description: Human-readable description of what this evidence supports.
    """

    path: str
    commit_sha: str
    description: str

    def __post_init__(self) -> None:
        """Validate evidence reference invariants at construction."""
        # INV-EV-001: Valid path prefix
        if not any(self.path.startswith(prefix) for prefix in VALID_EVIDENCE_PREFIXES):
            raise ValidationError(
                f"Evidence path must start with one of {VALID_EVIDENCE_PREFIXES}; "
                f"got:  '{self.path}'"
            )

        # INV-EV-002: Valid commit SHA format
        if not COMMIT_SHA_PATTERN.fullmatch(self.commit_sha):
            raise ValidationError(
                f"commit_sha must be 40-character lowercase hex; "
                f"got: '{self.commit_sha}'"
            )
        
        # INV-EV-002b: Forbid placeholder SHA
        if self.commit_sha == "0" * 40:
            raise ValidationError(
                "Placeholder commit SHA ('000...000') is prohibited. "
                "Evidence must be pinned to a specific commit for provenance."
            )

        # INV-EV-003: Non-empty description
        if not self.description. strip():
            raise ValidationError("Evidence description cannot be empty or whitespace-only")

    def github_permalink(self, owner: str, repo: str) -> str:
        """
        Generate a GitHub permalink URL to this evidence.

        Args:
            owner: Repository owner (user or organization).
            repo: Repository name.

        Returns:
            Full GitHub URL to the file at the pinned commit.
        """
        return f"https://github.com/{owner}/{repo}/blob/{self.commit_sha}/{self.path}"

    def to_canonical_dict(self) -> dict[str, str]:
        """
        Convert to canonical dictionary for hashing.

        Returns:
            Dictionary with 'path', 'commit_sha', and 'description' keys.
        """
        return {
            "commit_sha": self.commit_sha,
            "description": self.description,
            "path": self.path,
        }


# =============================================================================
# CALIBRATION PARAMETER
# =============================================================================


@dataclass(frozen=True, slots=True)
class CalibrationParameter: 
    """
    Single calibration parameter with full provenance and validity semantics.

    A CalibrationParameter represents a tunable value in the pipeline with: 
    - Explicit bounds constraining valid values
    - Time-bounded validity (calibration date and expiration)
    - Full provenance linking to source evidence
    - Rationale documenting the calibration decision

    Invariants:
        INV-CP-001: value ∈ [bounds.lower, bounds.upper]
        INV-CP-002: calibrated_at is timezone-aware UTC
        INV-CP-003: expires_at is timezone-aware UTC
        INV-CP-004: expires_at > calibrated_at
        INV-CP-005: rationale is non-empty

    Attributes:
        name: Unique identifier for this parameter within its layer.
        value: The calibrated value.
        unit: Unit of measurement (e.g., "dimensionless", "seconds", "tokens").
        bounds: Valid range for this parameter.
        rationale: Human-readable justification for the calibrated value.
        evidence: Reference to the source evidence supporting this calibration.
        calibrated_at: Timestamp when calibration was performed.
        expires_at: Timestamp after which recalibration is required.
    """

    name: str
    value: float
    unit: str
    bounds: ClosedInterval
    rationale:  str
    evidence: EvidenceReference
    calibrated_at:  datetime
    expires_at: datetime

    def __post_init__(self) -> None:
        """Validate parameter invariants at construction."""
        # INV-CP-001: Value within bounds
        if not self.bounds. contains(self.value):
            raise ValidationError(
                f"Parameter '{self.name}':  value {self.value} not in "
                f"[{self.bounds.lower}, {self.bounds.upper}]"
            )

        # INV-CP-002: calibrated_at timezone-aware
        if self.calibrated_at.tzinfo is None:
            raise ValidationError(
                f"Parameter '{self.name}': calibrated_at must be timezone-aware; "
                f"got naive datetime: {self.calibrated_at}"
            )

        # INV-CP-003: expires_at timezone-aware
        if self.expires_at.tzinfo is None:
            raise ValidationError(
                f"Parameter '{self.name}': expires_at must be timezone-aware; "
                f"got naive datetime: {self.expires_at}"
            )

        # INV-CP-004: expires_at > calibrated_at
        if self.expires_at <= self.calibrated_at:
            raise ValidationError(
                f"Parameter '{self. name}': expires_at ({self.expires_at. isoformat()}) "
                f"must be after calibrated_at ({self.calibrated_at.isoformat()})"
            )

        # INV-CP-005: Non-empty rationale
        if not self.rationale.strip():
            raise ValidationError(
                f"Parameter '{self.name}':  rationale cannot be empty or whitespace-only"
            )

    def validity_status_at(self, check_time: datetime) -> ValidityStatus:
        """
        Determine validity status at a specific point in time.

        This method returns a structured status instead of a boolean,
        allowing callers to distinguish between different states and
        implement appropriate handling (e.g., warnings for EXPIRING_SOON).

        Args:
            check_time: The point in time to check validity against. 
                Must be timezone-aware.

        Returns:
            ValidityStatus indicating the parameter's state at check_time. 

        Raises:
            ValidationError: If check_time is timezone-naive.
        """
        if check_time.tzinfo is None:
            raise ValidationError(
                f"check_time must be timezone-aware; got naive datetime: {check_time}"
            )

        if check_time < self.calibrated_at:
            return ValidityStatus.NOT_YET_VALID

        if check_time > self.expires_at:
            return ValidityStatus.EXPIRED

        # Compute remaining validity as fraction of total window
        total_window_seconds = (self. expires_at - self.calibrated_at).total_seconds()
        remaining_seconds = (self.expires_at - check_time).total_seconds()

        # 10% threshold for "expiring soon" warning
        expiring_soon_threshold = 0.10
        if remaining_seconds / total_window_seconds < expiring_soon_threshold: 
            return ValidityStatus.EXPIRING_SOON

        return ValidityStatus.VALID

    def days_until_expiry(self, from_time: datetime | None = None) -> float:
        """
        Compute days remaining until expiration.

        Args:
            from_time: Reference time (defaults to current UTC time).
                Must be timezone-aware if provided.

        Returns:
            Number of days until expiry (negative if already expired).

        Raises:
            ValidationError: If from_time is timezone-naive.
        """
        if from_time is None:
            from_time = datetime.now(timezone.utc)
        elif from_time.tzinfo is None:
            raise ValidationError("from_time must be timezone-aware")

        delta = self.expires_at - from_time
        return delta.total_seconds() / 86400.0

    def to_canonical_dict(self) -> dict[str, object]:
        """
        Convert to canonical dictionary for hashing and serialization.

        The dictionary structure is deterministic and includes all
        fields necessary to reconstruct the parameter. 

        Returns:
            Dictionary with all parameter attributes in canonical form.
        """
        return {
            "bounds": self.bounds.to_canonical_dict(),
            "calibrated_at": self.calibrated_at.isoformat(),
            "evidence": self.evidence.to_canonical_dict(),
            "expires_at": self.expires_at. isoformat(),
            "name": self.name,
            "rationale": self.rationale,
            "unit": self.unit,
            "value": self.value,
        }

    def content_hash(self) -> str:
        """
        Compute SHA-256 hash of canonical representation.

        This hash uniquely identifies the parameter's content and can
        be used for integrity verification and change detection.

        Returns:
            64-character lowercase hexadecimal SHA-256 digest.
        """
        canonical_bytes = _canonical_json(self. to_canonical_dict())
        return _compute_sha256(canonical_bytes)


# =============================================================================
# CALIBRATION LAYER
# =============================================================================


@dataclass(frozen=True, slots=True)
class CalibrationLayer:
    """
    Complete calibration configuration for a contract with cryptographic attestation.

    A CalibrationLayer aggregates all calibration parameters for a specific
    unit of analysis, phase, and contract type. It provides:
    - Extensible parameter set via immutable tuple
    - Canonical serialization for cross-system verification
    - Optional Ed25519 signature for N3-AUD compliance
    - Manifest hash for integrity verification

    Invariants:
        INV-CL-001: All parameters must pass individual validation
        INV-CL-002: unit_of_analysis_id matches pattern [A-Z]{2,6}-[0-9]{4,12}
        INV-CL-003: If signature present, it must verify against manifest_hash
        INV-CL-004: created_at must be timezone-aware UTC
        INV-CL-005: Required parameters must all be present

    Attributes:
        unit_of_analysis_id: Identifier for the unit being calibrated.
        phase: Pipeline phase this calibration applies to.
        contract_type_code: Type of contract (e.g., "PDT", "PDET", "PMI").
        parameters: Immutable tuple of calibration parameters.
        created_at: Timestamp when this layer was created.
        signature: Optional Ed25519 signature of manifest_hash.
        signer_key_id: Optional identifier for the signing key.
    """

    unit_of_analysis_id: str
    phase: CalibrationPhase
    contract_type_code: str
    parameters: tuple[CalibrationParameter, ...]
    created_at: datetime
    signature: bytes | None = None
    signer_key_id: str | None = None

    # Class-level constants (not instance fields)
    SCHEMA_VERSION:  str = field(default=SCHEMA_VERSION, init=False, repr=False)
    REQUIRED_PARAMETER_NAMES: frozenset[str] = field(
        default=frozenset({
            "prior_strength",
            "veto_threshold",
            "chunk_size",
            "extraction_coverage_target",
        }),
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        """Validate layer invariants at construction."""
        # INV-CL-002: Valid unit_of_analysis_id format
        if not UNIT_OF_ANALYSIS_PATTERN.fullmatch(self. unit_of_analysis_id):
            raise ValidationError(
                f"unit_of_analysis_id must match pattern "
                f"{UNIT_OF_ANALYSIS_PATTERN.pattern}; got: '{self.unit_of_analysis_id}'"
            )

        # INV-CL-004: created_at timezone-aware
        if self.created_at.tzinfo is None:
            raise ValidationError(
                f"created_at must be timezone-aware; got naive datetime: {self.created_at}"
            )

        # INV-CL-005: Required parameters present
        parameter_names = frozenset(p.name for p in self.parameters)
        missing = self.REQUIRED_PARAMETER_NAMES - parameter_names
        if missing:
            raise ValidationError(
                f"Missing required parameters: {sorted(missing)}"
            )

        # Check for duplicate parameter names
        if len(parameter_names) != len(self.parameters):
            duplicates = [
                p. name for p in self.parameters
                if sum(1 for q in self.parameters if q.name == p.name) > 1
            ]
            raise ValidationError(
                f"Duplicate parameter names detected: {sorted(set(duplicates))}"
            )

        # INV-CL-003:  Signature verification (if present)
        # Note:  Actual verification requires public key, deferred to verify_signature()

    def get_parameter(self, name: str) -> CalibrationParameter:
        """
        Retrieve a parameter by name.

        Args:
            name: The parameter name to look up.

        Returns:
            The CalibrationParameter with the given name.

        Raises:
            KeyError: If no parameter with that name exists.
        """
        for param in self.parameters:
            if param.name == name:
                return param
        raise KeyError(f"No parameter named '{name}' in calibration layer")

    def get_parameter_value(self, name: str) -> float:
        """
        Retrieve a parameter's value by name.

        Convenience method for accessing parameter values directly.

        Args:
            name: The parameter name to look up. 

        Returns:
            The float value of the parameter.

        Raises:
            KeyError: If no parameter with that name exists. 
        """
        return self.get_parameter(name).value

    def all_valid_at(self, check_time: datetime) -> bool:
        """
        Check if all parameters are valid at the given time.

        Args:
            check_time: The point in time to check validity against. 

        Returns:
            True if all parameters have ValidityStatus.VALID or
            ValidityStatus.EXPIRING_SOON at check_time. 
        """
        acceptable_statuses = {ValidityStatus.VALID, ValidityStatus.EXPIRING_SOON}
        return all(
            p.validity_status_at(check_time) in acceptable_statuses
            for p in self.parameters
        )

    def expired_parameters_at(self, check_time:  datetime) -> tuple[CalibrationParameter, ...]: 
        """
        Return all parameters that are expired at the given time.

        Args:
            check_time:  The point in time to check validity against.

        Returns:
            Tuple of parameters with ValidityStatus.EXPIRED. 
        """
        return tuple(
            p for p in self.parameters
            if p.validity_status_at(check_time) == ValidityStatus.EXPIRED
        )

    def expiring_soon_parameters_at(
        self, check_time: datetime
    ) -> tuple[CalibrationParameter, ...]:
        """
        Return all parameters that are expiring soon at the given time.

        Args:
            check_time:  The point in time to check validity against.

        Returns:
            Tuple of parameters with ValidityStatus. EXPIRING_SOON. 
        """
        return tuple(
            p for p in self.parameters
            if p.validity_status_at(check_time) == ValidityStatus.EXPIRING_SOON
        )

    def to_canonical_dict(self) -> dict[str, object]: 
        """
        Convert to canonical dictionary for hashing and serialization. 

        The structure is deterministic with parameters sorted by name. 

        Returns:
            Dictionary with all layer attributes in canonical form.
        """
        # Sort parameters by name for deterministic ordering
        sorted_params = sorted(self.parameters, key=lambda p: p.name)
        return {
            "contract_type_code": self.contract_type_code,
            "created_at": self.created_at.isoformat(),
            "parameters": [p.to_canonical_dict() for p in sorted_params],
            "phase": self.phase.name,
            "schema_version": self.SCHEMA_VERSION,
            "unit_of_analysis_id": self.unit_of_analysis_id,
        }

    def manifest_hash(self) -> str:
        """
        Compute SHA-256 hash of the entire calibration manifest.

        This hash serves as the content identifier for the layer and
        is the data signed by cryptographic attestation.

        Returns:
            64-character lowercase hexadecimal SHA-256 digest.
        """
        canonical_bytes = _canonical_json(self.to_canonical_dict())
        return _compute_sha256(canonical_bytes)

    def sign(self, private_key: Ed25519PrivateKey, key_id: str) -> CalibrationLayer:
        """
        Create a signed copy of this calibration layer.

        Args:
            private_key: Ed25519 private key for signing. 
            key_id: Identifier for the signing key (for key rotation tracking).

        Returns:
            New CalibrationLayer instance with signature and signer_key_id set. 

        Raises:
            ImportError: If cryptography package is not installed.
        """
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        except ImportError as exc:
            raise ImportError(
                "cryptography package required for signing. "
                "Install with: pip install cryptography"
            ) from exc

        manifest_bytes = self.manifest_hash().encode("utf-8")
        signature = private_key.sign(manifest_bytes)

        # Create new instance with signature (frozen dataclass)
        return CalibrationLayer(
            unit_of_analysis_id=self. unit_of_analysis_id,
            phase=self.phase,
            contract_type_code=self.contract_type_code,
            parameters=self.parameters,
            created_at=self. created_at,
            signature=signature,
            signer_key_id=key_id,
        )

    def verify_signature(self, public_key: Ed25519PublicKey) -> bool:
        """
        Verify the cryptographic signature of this calibration layer. 

        Args:
            public_key: Ed25519 public key corresponding to the signer.

        Returns:
            True if signature is valid. 

        Raises:
            IntegrityError: If signature is invalid or missing.
            ImportError: If cryptography package is not installed.
        """
        if self.signature is None:
            raise IntegrityError("Calibration layer has no signature to verify")

        try:
            from cryptography.exceptions import InvalidSignature
        except ImportError as exc:
            raise ImportError(
                "cryptography package required for signature verification. "
                "Install with: pip install cryptography"
            ) from exc

        manifest_bytes = self.manifest_hash().encode("utf-8")

        try:
            public_key.verify(self.signature, manifest_bytes)
            return True
        except InvalidSignature as exc:
            raise IntegrityError(
                f"Signature verification failed for calibration layer "
                f"'{self.unit_of_analysis_id}'"
            ) from exc


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================


def create_default_bounds() -> dict[str, tuple[ClosedInterval, str, float]]:
    """
    Create default bounds for standard calibration parameters.

    This function provides the canonical bounds, units, and default values
    for the four required calibration parameters.  These bounds are derived
    from domain analysis and should only be modified with explicit evidence.

    NOTE: These defaults are GENERIC and not TYPE-specific.
    For type-specific defaults (e.g. priors for TYPE_B), use type_defaults.py.

    Returns:
        Dictionary mapping parameter names to (bounds, unit, default_value) tuples.
    """
    # Warn if used in contexts where type-specific defaults are expected
    logging.getLogger(__name__).warning(
        "create_default_bounds() called. "
        "These are GENERIC defaults. ensure this is intentional (e.g. Phase-1 Ingestion). "
        "For Phase-2, prefer type_defaults."
    )
    return {
        "prior_strength": (
            ClosedInterval(lower=0.0, upper=1.0),
            "dimensionless",
            0.5,
        ),
        "veto_threshold": (
            ClosedInterval(lower=0.0, upper=1.0),
            "dimensionless",
            0.3,
        ),
        "chunk_size": (
            ClosedInterval(lower=100.0, upper=10000.0),
            "tokens",
            2000.0,
        ),
        "extraction_coverage_target":  (
            ClosedInterval(lower=0.5, upper=1.0),
            "fraction",
            0.85,
        ),
    }


def create_calibration_parameter(
    name: str,
    value: float,
    bounds: ClosedInterval,
    unit:  str,
    rationale: str,
    evidence_path: str,
    evidence_commit: str,
    evidence_description: str,
    validity_days: int = 90,
    calibrated_at: datetime | None = None,
) -> CalibrationParameter:
    """
    Factory function to create a CalibrationParameter with computed expiry.

    This function simplifies parameter creation by computing expires_at
    from calibrated_at and validity_days. 

    Args:
        name:  Parameter name.
        value: Calibrated value.
        bounds: Valid range for the parameter.
        unit: Unit of measurement.
        rationale: Justification for the calibrated value.
        evidence_path: Repository path to evidence artifact.
        evidence_commit: Commit SHA containing the evidence.
        evidence_description: Description of the evidence.
        validity_days: Number of days the calibration is valid. 
        calibrated_at:  Calibration timestamp (defaults to current UTC time).

    Returns:
        Fully constructed CalibrationParameter. 
    """
    if calibrated_at is None: 
        calibrated_at = datetime. now(timezone.utc)

    from datetime import timedelta

    expires_at = calibrated_at + timedelta(days=validity_days)

    evidence = EvidenceReference(
        path=evidence_path,
        commit_sha=evidence_commit,
        description=evidence_description,
    )

    return CalibrationParameter(
        name=name,
        value=value,
        unit=unit,
        bounds=bounds,
        rationale=rationale,
        evidence=evidence,
        calibrated_at=calibrated_at,
        expires_at=expires_at,
    )


# =============================================================================
# MODULE EXPORTS
# =============================================================================


__all__ = [
    # Constants
    "SCHEMA_VERSION",
    "HASH_ALGORITHM",
    # Exceptions
    "CalibrationError",
    "ValidationError",
    "IntegrityError",
    "ExpirationError",
    # Enumerations
    "CalibrationPhase",
    "ValidityStatus",
    # Core types
    "ClosedInterval",
    "EvidenceReference",
    "CalibrationParameter",
    "CalibrationLayer",
    # Factory functions
    "create_default_bounds",
    "create_calibration_parameter",
]

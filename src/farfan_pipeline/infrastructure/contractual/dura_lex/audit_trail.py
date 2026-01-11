"""
Audit Trail System with Verification Manifest

Implements comprehensive audit trail for calibration with:
- VerificationManifest dataclass capturing all calibration inputs/outputs
- HMAC signature verification for tamper detection
- Score reconstruction for determinism validation
- Structured JSON logging with rotation and compression
- Operation trace generation for mathematical operations
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import traceback
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np


@dataclass(frozen=True)
class CalibrationScore:
    """Individual method calibration score Cal(I)"""

    method_id: str
    score: float
    confidence: float
    timestamp: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ParametrizationConfig:
    """Parametrization configuration snapshot"""

    config_hash: str
    retry: int
    timeout_s: float
    temperature: float
    thresholds: dict[str, float]
    additional_params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DeterminismSeeds:
    """Determinism seed tracking"""

    random_seed: int
    numpy_seed: int
    seed_version: str
    base_seed: int | None = None
    policy_unit_id: str | None = None
    correlation_id: str | None = None


@dataclass(frozen=True)
class ResultsBundle:
    """Analysis results bundle"""

    micro_scores: list[float]
    dimension_scores: dict[str, float]
    area_scores: dict[str, float]
    macro_score: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OperationTrace:
    """Trace of a mathematical operation"""

    operation: str
    inputs: dict[str, Any]
    output: Any
    stack_trace: list[str]
    timestamp: str


@dataclass
class VerificationManifest:
    """
    Verification manifest capturing complete calibration context.

    Captures all inputs, parameters, results, and cryptographic signatures
    for tamper detection and determinism validation.
    """

    calibration_scores: dict[str, CalibrationScore]
    parametrization: ParametrizationConfig
    determinism_seeds: DeterminismSeeds
    results: ResultsBundle
    timestamp: str
    validator_version: str
    signature: str = ""
    trace: list[OperationTrace] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert manifest to dictionary"""
        data = asdict(self)
        return data

    def to_json(self, indent: int = 2) -> str:
        """Convert manifest to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, default=str)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VerificationManifest:
        """Create manifest from dictionary"""
        calibration_scores = {
            k: CalibrationScore(**v) for k, v in data["calibration_scores"].items()
        }
        parametrization = ParametrizationConfig(**data["parametrization"])
        determinism_seeds = DeterminismSeeds(**data["determinism_seeds"])
        results = ResultsBundle(**data["results"])

        trace = [OperationTrace(**t) for t in data.get("trace", [])]

        return cls(
            calibration_scores=calibration_scores,
            parametrization=parametrization,
            determinism_seeds=determinism_seeds,
            results=results,
            timestamp=data["timestamp"],
            validator_version=data["validator_version"],
            signature=data.get("signature", ""),
            trace=trace,
        )


def generate_manifest(
    calibration_scores: dict[str, float],
    config_hash: str,
    retry: int,
    timeout_s: float,
    temperature: float,
    thresholds: dict[str, float],
    random_seed: int,
    numpy_seed: int,
    seed_version: str,
    micro_scores: list[float],
    dimension_scores: dict[str, float],
    area_scores: dict[str, float],
    macro_score: float,
    validator_version: str,
    secret_key: str,
    base_seed: int | None = None,
    policy_unit_id: str | None = None,
    correlation_id: str | None = None,
    additional_params: dict[str, Any] | None = None,
    results_metadata: dict[str, Any] | None = None,
    trace: list[OperationTrace] | None = None,
) -> VerificationManifest:
    """
    Generate verification manifest with signature.

    Args:
        calibration_scores: Method ID to Cal(I) score mapping
        config_hash: SHA256 hash of configuration
        retry: Retry count
        timeout_s: Timeout in seconds
        temperature: Temperature parameter
        thresholds: Threshold configuration
        random_seed: Random seed used
        numpy_seed: NumPy seed used
        seed_version: Seed derivation algorithm version
        micro_scores: Micro-level scores
        dimension_scores: Dimension-level scores
        area_scores: Area-level scores
        macro_score: Macro-level score
        validator_version: Validator version string
        secret_key: HMAC secret key
        base_seed: Optional base seed
        policy_unit_id: Optional policy unit identifier
        correlation_id: Optional correlation ID
        additional_params: Optional additional parameters
        results_metadata: Optional results metadata
        trace: Optional operation trace

    Returns:
        VerificationManifest with HMAC signature
    """
    timestamp = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    calibration_score_objs = {
        method_id: CalibrationScore(
            method_id=method_id, score=score, confidence=1.0, timestamp=timestamp
        )
        for method_id, score in calibration_scores.items()
    }

    parametrization = ParametrizationConfig(
        config_hash=config_hash,
        retry=retry,
        timeout_s=timeout_s,
        temperature=temperature,
        thresholds=thresholds,
        additional_params=additional_params or {},
    )

    determinism_seeds = DeterminismSeeds(
        random_seed=random_seed,
        numpy_seed=numpy_seed,
        seed_version=seed_version,
        base_seed=base_seed,
        policy_unit_id=policy_unit_id,
        correlation_id=correlation_id,
    )

    results = ResultsBundle(
        micro_scores=micro_scores,
        dimension_scores=dimension_scores,
        area_scores=area_scores,
        macro_score=macro_score,
        metadata=results_metadata or {},
    )

    manifest = VerificationManifest(
        calibration_scores=calibration_score_objs,
        parametrization=parametrization,
        determinism_seeds=determinism_seeds,
        results=results,
        timestamp=timestamp,
        validator_version=validator_version,
        trace=trace or [],
    )

    signature = _compute_signature(manifest, secret_key)

    object.__setattr__(manifest, "signature", signature)

    return manifest


def verify_manifest(manifest: VerificationManifest, secret_key: str) -> bool:
    """
    Verify manifest HMAC signature.

    Args:
        manifest: VerificationManifest to verify
        secret_key: HMAC secret key

    Returns:
        True if signature is valid, False otherwise
    """
    if not manifest.signature:
        return False

    provided_signature = manifest.signature

    temp_manifest = VerificationManifest(
        calibration_scores=manifest.calibration_scores,
        parametrization=manifest.parametrization,
        determinism_seeds=manifest.determinism_seeds,
        results=manifest.results,
        timestamp=manifest.timestamp,
        validator_version=manifest.validator_version,
        signature="",
        trace=manifest.trace,
    )

    expected_signature = _compute_signature(temp_manifest, secret_key)

    return hmac.compare_digest(provided_signature, expected_signature)


def reconstruct_score(manifest: VerificationManifest) -> float:
    """
    Reconstruct macro score from manifest to verify computation.

    Args:
        manifest: VerificationManifest with results

    Returns:
        Reconstructed macro score
    """
    if not manifest.results.dimension_scores:
        return 0.0

    dimension_values = list(manifest.results.dimension_scores.values())

    reconstructed = float(np.mean(dimension_values))

    return reconstructed


def validate_determinism(manifest1: VerificationManifest, manifest2: VerificationManifest) -> bool:
    """
    Validate determinism: identical inputs should produce identical outputs.

    Args:
        manifest1: First verification manifest
        manifest2: Second verification manifest

    Returns:
        True if deterministic (same seeds → same results), False otherwise
    """
    if (
        manifest1.determinism_seeds.random_seed != manifest2.determinism_seeds.random_seed
        or manifest1.determinism_seeds.numpy_seed != manifest2.determinism_seeds.numpy_seed
    ):
        return True

    if manifest1.parametrization.config_hash != manifest2.parametrization.config_hash:
        return True

    results_match = (
        abs(manifest1.results.macro_score - manifest2.results.macro_score) < 1e-6
        and manifest1.results.micro_scores == manifest2.results.micro_scores
        and manifest1.results.dimension_scores == manifest2.results.dimension_scores
        and manifest1.results.area_scores == manifest2.results.area_scores
    )

    return results_match


def _compute_signature(manifest: VerificationManifest, secret_key: str) -> str:
    """
    Compute HMAC-SHA256 signature of manifest.

    Args:
        manifest: VerificationManifest to sign
        secret_key: HMAC secret key

    Returns:
        Hex-encoded HMAC signature
    """
    manifest_dict = manifest.to_dict()

    if "signature" in manifest_dict:
        del manifest_dict["signature"]

    canonical_json = json.dumps(manifest_dict, sort_keys=True, separators=(",", ":"), default=str)

    signature = hmac.new(secret_key.encode("utf-8"), canonical_json.encode("utf-8"), hashlib.sha256)

    return signature.hexdigest()


class StructuredAuditLogger:
    """
    Structured JSON logger for audit trail.

    Logs to logs/calibration/ with daily rotation and compression.
    """

    def __init__(self, log_dir: Path | str = "logs/calibration", component: str = "audit"):
        """
        Initialize structured audit logger.

        Args:
            log_dir: Directory for log files
            component: Component name for log entries
        """
        self.log_dir = Path(log_dir)
        self.component = component
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(f"audit_trail.{component}")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.FileHandler(
                self.log_dir / f"{component}_{self._get_date_suffix()}.log"
            )
            handler.setFormatter(logging.Formatter("%(message)s"))
            self.logger.addHandler(handler)

    def _get_date_suffix(self) -> str:
        """Get date suffix for log rotation"""
        return datetime.now(UTC).strftime("%Y%m%d")

    def log(self, level: str, message: str, metadata: dict[str, Any] | None = None) -> None:
        """
        Log structured JSON entry.

        Args:
            level: Log level (INFO, WARNING, ERROR)
            message: Log message
            metadata: Optional metadata dictionary
        """
        entry = {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "level": level,
            "component": self.component,
            "message": message,
            "metadata": metadata or {},
        }

        self.logger.info(json.dumps(entry, sort_keys=True, default=str))

    def log_manifest_generation(
        self, manifest: VerificationManifest, success: bool, error: str | None = None
    ) -> None:
        """Log manifest generation event"""
        metadata = {
            "timestamp": manifest.timestamp,
            "validator_version": manifest.validator_version,
            "calibration_count": len(manifest.calibration_scores),
            "macro_score": manifest.results.macro_score,
            "success": success,
        }

        if error:
            metadata["error"] = error

        self.log("INFO" if success else "ERROR", "Manifest generation completed", metadata)

    def log_verification(
        self, manifest: VerificationManifest, verified: bool, error: str | None = None
    ) -> None:
        """Log manifest verification event"""
        metadata = {
            "timestamp": manifest.timestamp,
            "validator_version": manifest.validator_version,
            "verified": verified,
        }

        if error:
            metadata["error"] = error

        self.log("INFO" if verified else "WARNING", "Manifest verification completed", metadata)

    def log_determinism_check(
        self, manifest1: VerificationManifest, manifest2: VerificationManifest, deterministic: bool
    ) -> None:
        """Log determinism validation event"""
        metadata = {
            "timestamp1": manifest1.timestamp,
            "timestamp2": manifest2.timestamp,
            "deterministic": deterministic,
            "seed_match": (
                manifest1.determinism_seeds.random_seed == manifest2.determinism_seeds.random_seed
            ),
            "config_match": (
                manifest1.parametrization.config_hash == manifest2.parametrization.config_hash
            ),
        }

        self.log(
            "INFO" if deterministic else "WARNING", "Determinism validation completed", metadata
        )


class TraceGenerator:
    """
    Trace generator for mathematical operations.

    Intercepts operations and records inputs, outputs, and stack traces.
    """

    def __init__(self, enabled: bool = True):
        """
        Initialize trace generator.

        Args:
            enabled: Whether tracing is enabled
        """
        self.enabled = enabled
        self.traces: list[OperationTrace] = []

    def trace_operation(self, operation: str, inputs: dict[str, Any], output: Any) -> None:
        """
        Trace a mathematical operation.

        Args:
            operation: Operation name (e.g., "np.mean", "aggregate_scores")
            inputs: Input values dictionary
            output: Output value
        """
        if not self.enabled:
            return

        stack = traceback.extract_stack()[:-1]
        stack_trace = [f"{frame.filename}:{frame.lineno} in {frame.name}" for frame in stack[-5:]]

        trace = OperationTrace(
            operation=operation,
            inputs=inputs,
            output=output,
            stack_trace=stack_trace,
            timestamp=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        )

        self.traces.append(trace)

    def get_traces(self) -> list[OperationTrace]:
        """Get all recorded traces"""
        return self.traces.copy()

    def clear(self) -> None:
        """Clear all traces"""
        self.traces.clear()

    def __enter__(self) -> TraceGenerator:
        """Context manager entry"""
        self.clear()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit"""
        pass


def create_trace_example(output_dir: Path | str = "trace_examples") -> None:
    """
    Create example trace files for documentation.

    Args:
        output_dir: Directory for example files
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    trace_gen = TraceGenerator(enabled=True)

    trace_gen.trace_operation("np.mean", {"values": [0.8, 0.9, 0.7]}, 0.8)

    trace_gen.trace_operation(
        "aggregate_dimension_scores", {"dimension_scores": {"DIM01": 0.8, "DIM02": 0.9}}, 0.85
    )

    example_data = {
        "description": "Example operation traces for calibration audit",
        "traces": [asdict(t) for t in trace_gen.get_traces()],
    }

    with open(output_path / "example_traces.json", "w") as f:
        json.dump(example_data, f, indent=2, default=str)

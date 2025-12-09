"""
⚠️  SENSITIVE - PRODUCTION CALIBRATION SYSTEM ⚠️

COHORT_2024 - REFACTOR_WAVE_2024_12
Created: 2024-12-15T00:00:00+00:00
Classification: SENSITIVE - PRODUCTION CALIBRATION DATA

Intrinsic Calibration Configuration Loader

This module contains the production calibration system for the F.A.R.F.A.N pipeline.
It loads method-level quality scores (@b scores) computed from:
- b_theory: Conceptual and methodological soundness (40%)
- b_impl: Code implementation quality (35%)
- b_deploy: Operational stability and reliability (25%)

These scores are derived from evidence traces and used for production method selection,
quality assurance, and governance compliance.

SECURITY NOTICE:
- Contains role-based minimum score requirements
- Implements fallback mechanisms for unscored methods
- Handles exclusion and pending status for methods
- Used in production decision-making for method dispatch

DO NOT:
- Modify weights without governance approval
- Change role-based defaults without audit trail
- Remove exclusion/pending handling logic
- Expose raw evidence traces to untrusted code

REFERENCE IMPLEMENTATION:
This is the canonical implementation. For usage in production code:
    from src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration import (
        IntrinsicCalibrationLoader,
        load_intrinsic_calibration,
        get_score,
    )
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypedDict

__all__ = ["IntrinsicCalibrationLoader", "load_intrinsic_calibration"]


class CalibrationScore(TypedDict):
    """
    Structured calibration score for a method.
    
    Fields:
        b_theory: Conceptual soundness score [0.0, 1.0]
        b_impl: Implementation quality score [0.0, 1.0]
        b_deploy: Deployment stability score [0.0, 1.0]
        b_aggregate: Weighted aggregate score using canonical weights (0.4, 0.35, 0.25)
        status: Calibration status ('computed', 'excluded', 'pending', 'unknown')
    """
    b_theory: float
    b_impl: float
    b_deploy: float
    b_aggregate: float
    status: str


class IntrinsicCalibrationLoader:
    """
    Loads and manages intrinsic calibration scores for pipeline methods.
    
    This loader:
    1. Reads base configuration from COHORT_2024_intrinsic_calibration.json
    2. Loads method scores from evidence trace files
    3. Computes weighted aggregates using canonical weights (0.4/0.35/0.25)
    4. Handles excluded and pending methods
    5. Provides role-based fallback scores
    
    Thread-safe for read operations after initial load().
    """

    def __init__(self, calibration_path: Path | None = None, evidence_dir: Path | None = None):
        """
        Initialize the calibration loader.
        
        Args:
            calibration_path: Path to COHORT_2024_intrinsic_calibration.json.
                Defaults to calibration/ directory relative to this file.
            evidence_dir: Path to evidence_traces/ directory.
                Defaults to evidence_traces/ relative to parent directory.
        """
        if calibration_path is None:
            calibration_path = (
                Path(__file__).parent.parent.parent
                / "cross_cutting_infrastrucuture"
                / "capaz_calibration_parmetrization"
                / "calibration"
                / "COHORT_2024_intrinsic_calibration.json"
            )
        if evidence_dir is None:
            evidence_dir = (
                Path(__file__).parent.parent.parent
                / "cross_cutting_infrastrucuture"
                / "capaz_calibration_parmetrization"
                / "evidence_traces"
            )

        self.calibration_path = calibration_path
        self.evidence_dir = evidence_dir
        self._config: dict[str, Any] | None = None
        self._method_scores: dict[str, CalibrationScore] = {}
        self._role_defaults: dict[str, float] = {}
        self._weights = {"b_theory": 0.40, "b_impl": 0.35, "b_deploy": 0.25}
        self._excluded_methods: set[str] = set()
        self._pending_methods: set[str] = set()

    def load(self) -> None:
        """
        Load calibration configuration and evidence traces.
        
        This method:
        1. Reads the base calibration configuration
        2. Extracts aggregation weights and role requirements
        3. Scans evidence traces for method scores
        4. Computes weighted aggregates for all methods
        
        Must be called before using get_score() or other query methods.
        """
        with open(self.calibration_path) as f:
            self._config = json.load(f)

        self._weights = self._config["base_layer"]["aggregation"]["weights"]
        self._load_role_defaults()
        self._load_evidence_traces()

    def _load_role_defaults(self) -> None:
        """Extract role-based minimum score requirements from config."""
        if not self._config:
            return

        role_reqs = self._config.get("role_requirements", {})
        for role, req in role_reqs.items():
            min_score = req.get("min_base_score", 0.6)
            self._role_defaults[role] = min_score

    def _load_evidence_traces(self) -> None:
        """
        Load method scores from evidence trace files.
        
        Scans evidence_traces/ directory for JSON files containing:
        - method_id: Canonical method identifier
        - calibration.b_theory: Theory score
        - calibration.b_impl: Implementation score
        - calibration.b_deploy: Deployment score
        - calibration.status: Status flag
        
        Methods with status='excluded' are tracked separately.
        Methods with status='pending' await calibration.
        """
        if not self.evidence_dir.exists():
            return

        for trace_file in self.evidence_dir.glob("*.json"):
            try:
                with open(trace_file) as f:
                    trace_data = json.load(f)

                method_id = trace_data.get("method_id")
                if not method_id:
                    continue

                calibration = trace_data.get("calibration", {})
                status = calibration.get("status", "unknown")

                if status == "excluded":
                    self._excluded_methods.add(method_id)
                    continue
                elif status == "pending":
                    self._pending_methods.add(method_id)
                    continue

                b_theory = calibration.get("b_theory", 0.0)
                b_impl = calibration.get("b_impl", 0.0)
                b_deploy = calibration.get("b_deploy", 0.0)

                b_aggregate = (
                    b_theory * self._weights["b_theory"]
                    + b_impl * self._weights["b_impl"]
                    + b_deploy * self._weights["b_deploy"]
                )

                self._method_scores[method_id] = {
                    "b_theory": b_theory,
                    "b_impl": b_impl,
                    "b_deploy": b_deploy,
                    "b_aggregate": b_aggregate,
                    "status": status,
                }

            except (json.JSONDecodeError, KeyError, IOError):
                continue

    def get_score(
        self, method_id: str, role: str | None = None, fallback: float | None = None
    ) -> float:
        """
        Get aggregate @b score for a method with fallback handling.
        
        Resolution order:
        1. Return 0.0 if method is excluded
        2. Return role default or fallback if method is pending
        3. Return computed score if available
        4. Return explicit fallback if provided
        5. Return role-based default if role is specified
        6. Return global default (0.6)
        
        Args:
            method_id: Canonical method identifier (e.g., "module::Class::method")
            role: Pipeline role for fallback (SCORE_Q, INGEST_PDM, etc.)
            fallback: Explicit fallback score [0.0, 1.0]
            
        Returns:
            Aggregate @b score [0.0, 1.0]
        """
        if method_id in self._excluded_methods:
            return 0.0

        if method_id in self._pending_methods:
            if fallback is not None:
                return fallback
            if role and role in self._role_defaults:
                return self._role_defaults[role]
            return 0.6

        if method_id in self._method_scores:
            return self._method_scores[method_id]["b_aggregate"]

        if fallback is not None:
            return fallback

        if role and role in self._role_defaults:
            return self._role_defaults[role]

        return 0.6

    def get_detailed_score(self, method_id: str) -> CalibrationScore | None:
        """
        Get detailed calibration scores for a method.
        
        Args:
            method_id: Canonical method identifier
            
        Returns:
            CalibrationScore with component and aggregate scores, or None if pending/unknown.
            Excluded methods return all zeros with status='excluded'.
        """
        if method_id in self._excluded_methods:
            return {
                "b_theory": 0.0,
                "b_impl": 0.0,
                "b_deploy": 0.0,
                "b_aggregate": 0.0,
                "status": "excluded",
            }

        if method_id in self._pending_methods:
            return None

        return self._method_scores.get(method_id)

    def is_excluded(self, method_id: str) -> bool:
        """Check if a method is explicitly excluded from calibration."""
        return method_id in self._excluded_methods

    def is_pending(self, method_id: str) -> bool:
        """Check if a method is pending calibration."""
        return method_id in self._pending_methods

    def list_methods(self) -> list[str]:
        """List all methods with computed calibration scores."""
        return list(self._method_scores.keys())

    def get_role_default(self, role: str) -> float:
        """
        Get the minimum @b score requirement for a pipeline role.
        
        Args:
            role: Pipeline role (SCORE_Q, INGEST_PDM, STRUCTURE, etc.)
            
        Returns:
            Minimum required score [0.6, 1.0] or 0.6 if role unknown
        """
        return self._role_defaults.get(role, 0.6)

    def get_weights(self) -> dict[str, float]:
        """Get canonical aggregation weights for @b components."""
        return self._weights.copy()

    def get_statistics(self) -> dict[str, Any]:
        """
        Get comprehensive calibration system statistics.
        
        Returns:
            Dictionary containing:
            - total_methods: Number of calibrated methods
            - excluded_methods: Number of excluded methods
            - pending_methods: Number of pending methods
            - role_defaults: Role-based minimum scores
            - weights: Aggregation weights
            - score_distribution: Distribution by quality tier
        """
        return {
            "total_methods": len(self._method_scores),
            "excluded_methods": len(self._excluded_methods),
            "pending_methods": len(self._pending_methods),
            "role_defaults": self._role_defaults.copy(),
            "weights": self._weights.copy(),
            "score_distribution": self._compute_score_distribution(),
        }

    def _compute_score_distribution(self) -> dict[str, int]:
        """Compute distribution of scores across quality tiers."""
        distribution = {
            "excellent": 0,
            "good": 0,
            "acceptable": 0,
            "poor": 0,
        }

        for score_data in self._method_scores.values():
            score = score_data["b_aggregate"]
            if score >= 0.8:
                distribution["excellent"] += 1
            elif score >= 0.6:
                distribution["good"] += 1
            elif score >= 0.4:
                distribution["acceptable"] += 1
            else:
                distribution["poor"] += 1

        return distribution


_global_loader: IntrinsicCalibrationLoader | None = None


def load_intrinsic_calibration(
    calibration_path: Path | None = None, evidence_dir: Path | None = None
) -> IntrinsicCalibrationLoader:
    """
    Load or retrieve the global intrinsic calibration loader.
    
    This function implements singleton pattern for efficiency.
    Subsequent calls return the same loader instance.
    
    Args:
        calibration_path: Override default calibration config path
        evidence_dir: Override default evidence traces directory
        
    Returns:
        Loaded IntrinsicCalibrationLoader instance
    """
    global _global_loader

    if _global_loader is None:
        _global_loader = IntrinsicCalibrationLoader(calibration_path, evidence_dir)
        _global_loader.load()

    return _global_loader


def get_score(method_id: str, role: str | None = None, fallback: float | None = None) -> float:
    """
    Convenience function to get a method's @b score.
    
    See IntrinsicCalibrationLoader.get_score() for details.
    """
    loader = load_intrinsic_calibration()
    return loader.get_score(method_id, role, fallback)


def get_detailed_score(method_id: str) -> CalibrationScore | None:
    """
    Convenience function to get detailed calibration scores.
    
    See IntrinsicCalibrationLoader.get_detailed_score() for details.
    """
    loader = load_intrinsic_calibration()
    return loader.get_detailed_score(method_id)


def is_excluded(method_id: str) -> bool:
    """Convenience function to check if a method is excluded."""
    loader = load_intrinsic_calibration()
    return loader.is_excluded(method_id)


def is_pending(method_id: str) -> bool:
    """Convenience function to check if a method is pending calibration."""
    loader = load_intrinsic_calibration()
    return loader.is_pending(method_id)


def list_calibrated_methods() -> list[str]:
    """Convenience function to list all calibrated methods."""
    loader = load_intrinsic_calibration()
    return loader.list_methods()


def get_role_default(role: str) -> float:
    """Convenience function to get role-based default score."""
    loader = load_intrinsic_calibration()
    return loader.get_role_default(role)


def get_calibration_statistics() -> dict[str, Any]:
    """Convenience function to get calibration system statistics."""
    loader = load_intrinsic_calibration()
    return loader.get_statistics()

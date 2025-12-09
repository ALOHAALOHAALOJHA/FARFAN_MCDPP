"""
COHORT_2024 - REFACTOR_WAVE_2024_12
Created: 2024-12-15T00:00:00+00:00

Intrinsic Calibration Configuration Loader

Loads intrinsic calibration scores from COHORT_2024_intrinsic_calibration.json and
evidence traces, computing weighted @b scores with role-based fallbacks.

SENSITIVE: Contains production calibration data with role-specific defaults.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypedDict

__all__ = [
    "CalibrationScore",
    "IntrinsicCalibrationLoader",
    "load_intrinsic_calibration",
    "get_score",
    "get_detailed_score",
    "is_excluded",
    "is_pending",
    "list_calibrated_methods",
    "get_role_default",
    "get_calibration_statistics",
]


class CalibrationScore(TypedDict):
    b_theory: float
    b_impl: float
    b_deploy: float
    b_aggregate: float
    status: str


class IntrinsicCalibrationLoader:
    def __init__(self, calibration_path: Path | None = None, evidence_dir: Path | None = None):
        if calibration_path is None:
            calibration_path = (
                Path(__file__).parent / "COHORT_2024_intrinsic_calibration.json"
            )
        if evidence_dir is None:
            evidence_dir = Path(__file__).parent.parent / "evidence_traces"

        self.calibration_path = calibration_path
        self.evidence_dir = evidence_dir
        self._config: dict[str, Any] | None = None
        self._method_scores: dict[str, CalibrationScore] = {}
        self._role_defaults: dict[str, float] = {}
        self._weights = {"b_theory": 0.40, "b_impl": 0.35, "b_deploy": 0.25}
        self._excluded_methods: set[str] = set()
        self._pending_methods: set[str] = set()

    def load(self) -> None:
        with open(self.calibration_path) as f:
            self._config = json.load(f)

        self._weights = self._config["base_layer"]["aggregation"]["weights"]
        self._load_role_defaults()
        self._load_evidence_traces()

    def _load_role_defaults(self) -> None:
        if not self._config:
            return

        role_reqs = self._config.get("role_requirements", {})
        for role, req in role_reqs.items():
            min_score = req.get("min_base_score", 0.6)
            self._role_defaults[role] = min_score

    def _load_evidence_traces(self) -> None:
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
        return method_id in self._excluded_methods

    def is_pending(self, method_id: str) -> bool:
        return method_id in self._pending_methods

    def list_methods(self) -> list[str]:
        return list(self._method_scores.keys())

    def get_role_default(self, role: str) -> float:
        return self._role_defaults.get(role, 0.6)

    def get_weights(self) -> dict[str, float]:
        return self._weights.copy()

    def get_statistics(self) -> dict[str, Any]:
        return {
            "total_methods": len(self._method_scores),
            "excluded_methods": len(self._excluded_methods),
            "pending_methods": len(self._pending_methods),
            "role_defaults": self._role_defaults.copy(),
            "weights": self._weights.copy(),
            "score_distribution": self._compute_score_distribution(),
        }

    def _compute_score_distribution(self) -> dict[str, int]:
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
    global _global_loader

    if _global_loader is None:
        _global_loader = IntrinsicCalibrationLoader(calibration_path, evidence_dir)
        _global_loader.load()

    return _global_loader


def get_score(method_id: str, role: str | None = None, fallback: float | None = None) -> float:
    loader = load_intrinsic_calibration()
    return loader.get_score(method_id, role, fallback)


def get_detailed_score(method_id: str) -> CalibrationScore | None:
    loader = load_intrinsic_calibration()
    return loader.get_detailed_score(method_id)


def is_excluded(method_id: str) -> bool:
    loader = load_intrinsic_calibration()
    return loader.is_excluded(method_id)


def is_pending(method_id: str) -> bool:
    loader = load_intrinsic_calibration()
    return loader.is_pending(method_id)


def list_calibrated_methods() -> list[str]:
    loader = load_intrinsic_calibration()
    return loader.list_methods()


def get_role_default(role: str) -> float:
    loader = load_intrinsic_calibration()
    return loader.get_role_default(role)


def get_calibration_statistics() -> dict[str, Any]:
    loader = load_intrinsic_calibration()
    return loader.get_statistics()

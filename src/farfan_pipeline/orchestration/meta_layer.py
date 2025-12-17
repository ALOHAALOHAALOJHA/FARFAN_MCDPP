"""
Meta Layer (@m) Configuration and Evaluator

Implements the Meta Layer evaluation for method calibration,
measuring governance, transparency, and cost metrics.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, TypedDict


class TransparencyRequirements(TypedDict):
    require_formula_export: bool
    require_trace_complete: bool
    require_logs_conform: bool


class GovernanceRequirements(TypedDict):
    require_version_tag: bool
    require_config_hash: bool
    require_signature: bool


class CostThresholds(TypedDict):
    threshold_fast: float
    threshold_acceptable: float
    threshold_memory_normal: float


@dataclass(frozen=True)
class MetaLayerConfig:
    w_transparency: float
    w_governance: float
    w_cost: float
    transparency_requirements: TransparencyRequirements
    governance_requirements: GovernanceRequirements
    cost_thresholds: CostThresholds

    def __post_init__(self):
        total = self.w_transparency + self.w_governance + self.w_cost
        if abs(total - 1.0) > 1e-6:
            raise ValueError(
                f"Meta layer weights must sum to 1.0, got {total}"
            )
        if self.w_transparency < 0 or self.w_governance < 0 or self.w_cost < 0:
            raise ValueError("Meta layer weights must be non-negative")


class TransparencyArtifacts(TypedDict):
    formula_export: str | None
    trace: str | None
    logs: dict[str, Any] | None


class GovernanceArtifacts(TypedDict):
    version_tag: str
    config_hash: str
    signature: str | None


class CostMetrics(TypedDict):
    execution_time_s: float
    memory_usage_mb: float


class MetaLayerEvaluator:
    def __init__(self, config: MetaLayerConfig):
        self.config = config

    def evaluate_transparency(
        self, artifacts: TransparencyArtifacts, log_schema: dict[str, Any] | None = None
    ) -> float:
        count = 0

        if artifacts.get("formula_export"):
            if self._validate_formula_export(artifacts["formula_export"]):
                count += 1

        if artifacts.get("trace"):
            if self._validate_trace_complete(artifacts["trace"]):
                count += 1

        if artifacts.get("logs") and log_schema:
            if self._validate_logs_conform(artifacts["logs"], log_schema):
                count += 1

        if count == 3:
            return 1.0
        elif count == 2:
            return 0.7
        elif count == 1:
            return 0.4
        else:
            return 0.0

    def evaluate_governance(self, artifacts: GovernanceArtifacts) -> float:
        count = 0

        version_tag = artifacts.get("version_tag", "")
        if self._has_valid_version(version_tag):
            count += 1

        if artifacts.get("config_hash"):
            if self._validate_config_hash(artifacts["config_hash"]):
                count += 1

        if self.config.governance_requirements["require_signature"]:
            if artifacts.get("signature"):
                if self._validate_signature(artifacts["signature"]):
                    count += 1
        else:
            count += 1

        if count == 3:
            return 1.0
        elif count == 2:
            return 0.66
        elif count == 1:
            return 0.33
        else:
            return 0.0

    def evaluate_cost(self, metrics: CostMetrics) -> float:
        time_s = metrics["execution_time_s"]
        memory_mb = metrics["memory_usage_mb"]

        threshold_fast = self.config.cost_thresholds["threshold_fast"]
        threshold_acceptable = self.config.cost_thresholds["threshold_acceptable"]
        threshold_memory = self.config.cost_thresholds["threshold_memory_normal"]

        if time_s < 0 or memory_mb < 0:
            return 0.0

        if time_s < threshold_fast and memory_mb <= threshold_memory:
            return 1.0
        elif time_s < threshold_acceptable and memory_mb <= threshold_memory:
            return 0.8
        elif time_s >= threshold_acceptable or memory_mb > threshold_memory:
            return 0.5
        else:
            return 0.0

    def evaluate(
        self,
        transparency_artifacts: TransparencyArtifacts,
        governance_artifacts: GovernanceArtifacts,
        cost_metrics: CostMetrics,
        log_schema: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        m_transp = self.evaluate_transparency(transparency_artifacts, log_schema)
        m_gov = self.evaluate_governance(governance_artifacts)
        m_cost = self.evaluate_cost(cost_metrics)

        score = (
            self.config.w_transparency * m_transp +
            self.config.w_governance * m_gov +
            self.config.w_cost * m_cost
        )

        return {
            "score": score,
            "m_transparency": m_transp,
            "m_governance": m_gov,
            "m_cost": m_cost,
            "weights": {
                "w_transparency": self.config.w_transparency,
                "w_governance": self.config.w_governance,
                "w_cost": self.config.w_cost
            }
        }

    def _validate_formula_export(self, formula: str) -> bool:
        if not formula or not isinstance(formula, str):
            return False
        if len(formula) < 10:
            return False
        required_terms = ["Choquet", "Cal(I)", "x_"]
        return any(term in formula for term in required_terms)

    def _validate_trace_complete(self, trace: str) -> bool:
        if not trace or not isinstance(trace, str):
            return False
        if len(trace) < 20:
            return False
        required_markers = ["step", "phase", "method"]
        return any(marker in trace.lower() for marker in required_markers)

    def _validate_logs_conform(
        self, logs: dict[str, Any], schema: dict[str, Any]
    ) -> bool:
        if not logs or not isinstance(logs, dict):
            return False
        if not schema or not isinstance(schema, dict):
            return True

        required_fields = schema.get("required", [])
        return all(field in logs for field in required_fields)

    def _has_valid_version(self, version: str) -> bool:
        if not version or not isinstance(version, str):
            return False
        if version.lower() in ["unknown", "1.0", "0.0.0"]:
            return False
        return len(version) > 0

    def _validate_config_hash(self, config_hash: str) -> bool:
        if not config_hash or not isinstance(config_hash, str):
            return False
        if len(config_hash) != 64:
            return False
        try:
            int(config_hash, 16)
            return True
        except ValueError:
            return False

    def _validate_signature(self, signature: str) -> bool:
        if not signature or not isinstance(signature, str):
            return False
        return len(signature) >= 32


def create_default_config() -> MetaLayerConfig:
    return MetaLayerConfig(
        w_transparency=0.5,
        w_governance=0.4,
        w_cost=0.1,
        transparency_requirements={
            "require_formula_export": True,
            "require_trace_complete": True,
            "require_logs_conform": True
        },
        governance_requirements={
            "require_version_tag": True,
            "require_config_hash": True,
            "require_signature": False
        },
        cost_thresholds={
            "threshold_fast": 1.0,
            "threshold_acceptable": 5.0,
            "threshold_memory_normal": 512.0
        }
    )


def compute_config_hash(config_data: dict[str, Any]) -> str:
    canonical = json.dumps(config_data, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


__all__ = [
    "MetaLayerConfig",
    "TransparencyRequirements",
    "GovernanceRequirements",
    "CostThresholds",
    "TransparencyArtifacts",
    "GovernanceArtifacts",
    "CostMetrics",
    "MetaLayerEvaluator",
    "create_default_config",
    "compute_config_hash"
]

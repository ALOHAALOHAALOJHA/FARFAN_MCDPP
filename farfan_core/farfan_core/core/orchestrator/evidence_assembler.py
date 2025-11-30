from __future__ import annotations

import statistics
from typing import Any, Iterable, Literal

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

def _resolve_value(source: str, method_outputs: dict[str, Any]) -> Any:
    """Resolve dotted source paths from method_outputs."""
    if not source:
        return None
    parts = source.split(".")
    current: Any = method_outputs
    for idx, part in enumerate(parts):
        if idx == 0 and part in method_outputs:
            current = method_outputs[part]
            continue
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


class EvidenceAssembler:
    """
    Assemble evidence fields from method outputs using deterministic merge strategies.
    """

    MERGE_STRATEGIES = {
        "concat",
        "first",
        "last",
        "mean",
        "max",
        "min",
        "weighted_mean",
        "majority",
    }

    @staticmethod
    def assemble(method_outputs: dict[str, Any], assembly_rules: list[dict[str, Any]]) -> dict[str, Any]:
        evidence: dict[str, Any] = {}
        trace: dict[str, Any] = {}

        if "_signal_usage" in method_outputs:
            logger.info("signal_consumption_trace", signals_used=method_outputs["_signal_usage"])
            trace["signal_usage"] = method_outputs["_signal_usage"]
            # Remove from method_outputs to not interfere with evidence assembly
            del method_outputs["_signal_usage"]

        for rule in assembly_rules:
            target = rule.get("target")
            sources: Iterable[str] = rule.get("sources", [])
            strategy: str = rule.get("merge_strategy", "first")
            weights: list[float] | None = rule.get("weights")
            default = rule.get("default")

            if strategy not in EvidenceAssembler.MERGE_STRATEGIES:
                raise ValueError(f"Unsupported merge_strategy '{strategy}' for target '{target}'")

            values = []
            for src in sources:
                val = _resolve_value(src, method_outputs)
                if val is not None:
                    values.append(val)

            merged = EvidenceAssembler._merge(values, strategy, weights, default)
            evidence[target] = merged
            trace[target] = {"sources": list(sources), "strategy": strategy, "values": values}

        return {"evidence": evidence, "trace": trace}

    @staticmethod
    def _merge(values: list[Any], strategy: str, weights: list[float] | None, default: Any) -> Any:
        if not values:
            return default
        if strategy == "first":
            return values[0]
        if strategy == "last":
            return values[-1]
        if strategy == "concat":
            merged: list[Any] = []
            for v in values:
                if isinstance(v, list):
                    merged.extend(v)
                else:
                    merged.append(v)
            return merged
        numeric_values = [float(v) for v in values if EvidenceAssembler._is_number(v)]
        if strategy == "mean":
            return statistics.fmean(numeric_values) if numeric_values else default
        if strategy == "max":
            return max(numeric_values) if numeric_values else default
        if strategy == "min":
            return min(numeric_values) if numeric_values else default
        if strategy == "weighted_mean":
            if not numeric_values:
                return default
            if not weights:
                weights = [1.0] * len(numeric_values)
            w = weights[: len(numeric_values)] or [1.0] * len(numeric_values)
            total = sum(w) or 1.0
            return sum(v * w_i for v, w_i in zip(numeric_values, w)) / total
        if strategy == "majority":
            counts: dict[Any, int] = {}
            for v in values:
                counts[v] = counts.get(v, 0) + 1
            return max(counts.items(), key=lambda item: item[1])[0] if counts else default
        return default

    @staticmethod
    def _is_number(value: Any) -> bool:
        try:
            float(value)
            return not isinstance(value, bool)
        except (TypeError, ValueError):
            return False

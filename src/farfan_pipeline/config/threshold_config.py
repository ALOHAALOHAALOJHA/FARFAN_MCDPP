"""Signal Scoring Threshold Configuration Loader

Centralized configuration loader for signal-based scoring thresholds.
Supports three-tier priority system:
  1. Empirical corpus weights (if available)
  2. Environment variable overrides
  3. Default config file values

All threshold values are validated on load to ensure consistency.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ThresholdConfig:
    """Immutable threshold configuration.

    All values are loaded from config file + environment overrides.
    """

    # Pattern complexity
    high_pattern_threshold: int = 15
    pattern_complexity_adjustment: float = -0.05

    # Indicator specificity
    high_indicator_threshold: int = 10
    indicator_specificity_adjustment: float = 0.03

    # Evidence completeness
    complete_evidence_adjustment: float = 0.02

    # Score validation
    high_score_threshold: float = 0.8
    low_score_threshold: float = 0.3

    # Signal adjustments
    signal_presence_bonus: float = 0.05
    signal_absence_penalty: float = 0.10
    max_signal_bonus: float = 0.15

    # Constraints
    max_threshold_adjustment: float = 0.10
    max_cumulative_adjustment: float = 0.15
    threshold_floor: float = 0.3
    threshold_ceiling: float = 0.9

    # Metadata
    config_source: str = "default"
    validation_passed: bool = False
    validation_errors: tuple[str, ...] = field(default_factory=tuple)

    def validate(self) -> tuple[bool, list[str]]:
        """Validate threshold configuration consistency.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Rule 1: pattern_complexity_adjustment must be negative
        if self.pattern_complexity_adjustment >= 0:
            errors.append("pattern_complexity_adjustment must be negative")

        # Rule 2: indicator_specificity_adjustment must be positive
        if self.indicator_specificity_adjustment <= 0:
            errors.append("indicator_specificity_adjustment must be positive")

        # Rule 3: complete_evidence_adjustment must be positive
        if self.complete_evidence_adjustment <= 0:
            errors.append("complete_evidence_adjustment must be positive")

        # Rule 4: high_score_threshold > low_score_threshold
        if self.high_score_threshold <= self.low_score_threshold:
            errors.append("high_score_threshold must be > low_score_threshold")

        # Rule 5: signal_absence_penalty >= signal_presence_bonus
        if self.signal_absence_penalty < self.signal_presence_bonus:
            errors.append("signal_absence_penalty should be >= signal_presence_bonus")

        # Rule 6: max_signal_bonus >= 2 * signal_presence_bonus
        if self.max_signal_bonus < 2 * self.signal_presence_bonus:
            errors.append(
                "max_signal_bonus should be >= 2 * signal_presence_bonus (allow at least 2 signals)"
            )

        # Rule 7: Check adjustment magnitudes
        adjustments = [
            abs(self.pattern_complexity_adjustment),
            self.indicator_specificity_adjustment,
            self.complete_evidence_adjustment,
        ]
        for adj in adjustments:
            if adj > self.max_threshold_adjustment:
                errors.append(
                    f"Adjustment {adj} exceeds max_threshold_adjustment {self.max_threshold_adjustment}"
                )

        # Rule 8: Check cumulative adjustment
        cumulative = sum(adjustments)
        if cumulative > self.max_cumulative_adjustment:
            errors.append(
                f"Cumulative adjustment {cumulative:.3f} exceeds max {self.max_cumulative_adjustment}"
            )

        # Rule 9: Check threshold bounds
        if not (0.2 <= self.threshold_floor <= 0.4):
            errors.append(f"threshold_floor {self.threshold_floor} should be in [0.2, 0.4]")
        if not (0.8 <= self.threshold_ceiling <= 1.0):
            errors.append(f"threshold_ceiling {self.threshold_ceiling} should be in [0.8, 1.0]")

        return len(errors) == 0, errors


def _load_config_file() -> dict[str, Any]:
    """Load signal_scoring_thresholds.json from config directory."""
    config_path = Path(__file__).resolve().parent / "signal_scoring_thresholds.json"

    if not config_path.exists():
        logger.warning(f"Threshold config file not found at {config_path}, using defaults")
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse threshold config: {e}")
        return {}


def _get_env_override(key_path: str, default: Any) -> Any:
    """Get environment variable override for a config value.

    Args:
        key_path: Dot-separated path like "pattern_complexity.high_pattern_threshold"
        default: Default value if no override found

    Returns:
        Override value or default
    """
    # Convert key_path to env var format: FARFAN_THRESHOLD_PATTERN_COMPLEXITY_HIGH_PATTERN_THRESHOLD
    env_key = "FARFAN_THRESHOLD_" + key_path.replace(".", "_").upper()

    env_value = os.getenv(env_key)
    if env_value is None:
        return default

    # Parse value based on default type
    try:
        if isinstance(default, int):
            return int(env_value)
        elif isinstance(default, float):
            return float(env_value)
        elif isinstance(default, bool):
            return env_value.lower() in ("true", "1", "yes")
        else:
            return env_value
    except ValueError as e:
        logger.warning(f"Failed to parse env override {env_key}={env_value}: {e}")
        return default


def load_threshold_config() -> ThresholdConfig:
    """Load threshold configuration from config file + environment overrides.

    Priority order:
      1. Empirical corpus weights (if available) - NOT YET IMPLEMENTED
      2. Environment variable overrides
      3. Config file values
      4. Hardcoded defaults

    Returns:
        Validated ThresholdConfig instance
    """
    config_data = _load_config_file()

    # Extract values with environment override support
    def get_value(section: str, key: str, default: Any) -> Any:
        """Get config value with env override support."""
        # Get from config file
        file_value = config_data.get(section, {}).get(key, {}).get("value", default)

        # Check for env override
        key_path = f"{section}.{key}"
        return _get_env_override(key_path, file_value)

    # Build config
    config = ThresholdConfig(
        # Pattern complexity
        high_pattern_threshold=get_value("pattern_complexity", "high_pattern_threshold", 15),
        pattern_complexity_adjustment=get_value(
            "pattern_complexity", "pattern_complexity_adjustment", -0.05
        ),
        # Indicator specificity
        high_indicator_threshold=get_value(
            "indicator_specificity", "high_indicator_threshold", 10
        ),
        indicator_specificity_adjustment=get_value(
            "indicator_specificity", "indicator_specificity_adjustment", 0.03
        ),
        # Evidence completeness
        complete_evidence_adjustment=get_value(
            "evidence_completeness", "complete_evidence_adjustment", 0.02
        ),
        # Score validation
        high_score_threshold=get_value("score_validation", "high_score_threshold", 0.8),
        low_score_threshold=get_value("score_validation", "low_score_threshold", 0.3),
        # Signal adjustments
        signal_presence_bonus=get_value("signal_adjustments", "signal_presence_bonus", 0.05),
        signal_absence_penalty=get_value("signal_adjustments", "signal_absence_penalty", 0.10),
        max_signal_bonus=get_value("signal_adjustments", "max_signal_bonus", 0.15),
        # Constraints
        max_threshold_adjustment=get_value(
            "adjustment_constraints", "max_threshold_adjustment", 0.10
        ),
        max_cumulative_adjustment=get_value(
            "adjustment_constraints", "max_cumulative_adjustment", 0.15
        ),
        threshold_floor=get_value("adjustment_constraints", "threshold_floor", 0.3),
        threshold_ceiling=get_value("adjustment_constraints", "threshold_ceiling", 0.9),
        config_source="config_file",
    )

    # Validate
    is_valid, errors = config.validate()

    if not is_valid:
        logger.error(f"Threshold configuration validation failed: {errors}")
        # Return config with validation metadata
        return ThresholdConfig(
            **{
                k: getattr(config, k)
                for k in config.__dataclass_fields__
                if k not in ("validation_passed", "validation_errors")
            },
            validation_passed=False,
            validation_errors=tuple(errors),
        )

    logger.info(
        f"Threshold configuration loaded successfully from {config.config_source} "
        f"(high_pattern={config.high_pattern_threshold}, "
        f"high_score={config.high_score_threshold})"
    )

    return ThresholdConfig(
        **{
            k: getattr(config, k)
            for k in config.__dataclass_fields__
            if k not in ("validation_passed", "validation_errors")
        },
        validation_passed=True,
        validation_errors=tuple(),
    )


# Global singleton
_GLOBAL_CONFIG: ThresholdConfig | None = None


def get_threshold_config() -> ThresholdConfig:
    """Get global threshold configuration singleton.

    Returns:
        Validated ThresholdConfig instance
    """
    global _GLOBAL_CONFIG
    if _GLOBAL_CONFIG is None:
        _GLOBAL_CONFIG = load_threshold_config()
    return _GLOBAL_CONFIG


__all__ = ["ThresholdConfig", "load_threshold_config", "get_threshold_config"]

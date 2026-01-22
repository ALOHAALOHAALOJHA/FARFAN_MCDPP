"""
F.A.R.F.A.N Configuration Module
=================================

Configuration management for the F.A.R.F.A.N framework.

This module provides configuration loading, validation, and
environment-specific settings.
"""

from farfan_pipeline.config.threshold_config import (
    ThresholdConfig,
    get_threshold_config,
)

__all__ = [
    "ThresholdConfig",
    "get_threshold_config",
]

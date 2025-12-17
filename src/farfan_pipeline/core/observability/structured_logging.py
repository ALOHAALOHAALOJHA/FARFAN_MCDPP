"""Structured logging helpers.

These are thin utilities used by the verified runner.
"""

from __future__ import annotations

from typing import Any

try:
    import structlog

    _logger: Any = structlog.get_logger(__name__)
except Exception:  # pragma: no cover
    import logging

    _logger = logging.getLogger(__name__)


def log_runtime_config_loaded(*, config_repr: str, runtime_mode: Any) -> None:
    """Emit a single structured event when runtime config loads."""

    # Works with structlog or stdlib logging.
    try:
        _logger.info(
            "runtime_config_loaded",
            runtime_mode=str(getattr(runtime_mode, "value", runtime_mode)),
            config=config_repr,
        )
    except TypeError:
        _logger.info(
            "runtime_config_loaded runtime_mode=%s config=%s",
            str(getattr(runtime_mode, "value", runtime_mode)),
            config_repr,
        )

"""Compatibility shim for legacy imports.

The irrigation_using_signals implementation moved to farfan_pipeline.infrastructure.irrigation_using_signals.
This module preserves historical imports.
"""

from __future__ import annotations

from pathlib import Path

# Redirect package submodule resolution to the new location.
__path__ = [
    str((Path(__file__).resolve().parent.parent.parent / "farfan_pipeline" / "infrastructure" / "irrigation_using_signals").resolve())
]

"""Compatibility shim for legacy imports.

The cross-cutting infrastructure moved to `farfan_pipeline.infrastructure`.
This module preserves historical imports like:

- `from cross_cutting_infrastructure.irrigation_using_signals...`

New code should prefer:
- `from farfan_pipeline.infrastructure.irrigation_using_signals...`
"""

from __future__ import annotations

from pathlib import Path


# Redirect package submodule resolution to the new location.
__path__ = [
    str((Path(__file__).resolve().parent.parent / "farfan_pipeline" / "infrastructure").resolve())
]

__all__ = [
    "irrigation_using_signals",
    "contractual",
]

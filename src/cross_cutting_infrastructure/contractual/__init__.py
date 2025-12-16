"""Compatibility shim for legacy imports.

The contractual implementation moved to farfan_pipeline.infrastructure.contractual.
This module preserves historical imports.
"""

from __future__ import annotations

from pathlib import Path

# Redirect package submodule resolution to the new location.
__path__ = [
    str((Path(__file__).resolve().parent.parent.parent / "farfan_pipeline" / "infrastructure" / "contractual").resolve())
]

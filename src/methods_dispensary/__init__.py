"""Compatibility shim for legacy imports.

The methods dispensary implementation moved to `farfan_pipeline.methods`.
This module preserves historical imports like:

- `from methods_dispensary.derek_beach import DerekBeachProducer`

New code should prefer:
- `from farfan_pipeline.methods.derek_beach import DerekBeachProducer`
"""

from __future__ import annotations

from pathlib import Path


# Redirect package submodule resolution to the new location.
__path__ = [
    str((Path(__file__).resolve().parent.parent / "farfan_pipeline" / "methods").resolve())
]

# Preserve the legacy convenience exports by delegating.
from farfan_pipeline.methods import *  # noqa: F403,E402

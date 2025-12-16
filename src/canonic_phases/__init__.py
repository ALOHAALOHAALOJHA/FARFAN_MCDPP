"""Compatibility shim for legacy imports.

The canonical phases implementation moved to `farfan_pipeline.phases`.
This module preserves historical imports like:

- `import canonic_phases.Phase_zero...`

New code should prefer:
- `import farfan_pipeline.phases...`
"""

from __future__ import annotations

from pathlib import Path


# Redirect package submodule resolution to the new location.
__path__ = [
    str((Path(__file__).resolve().parent.parent / "farfan_pipeline" / "phases").resolve())
]

__all__ = [
    "Phase_zero",
    "Phase_one",
    "Phase_two",
    "Phase_three",
    "Phase_four_five_six_seven",
    "Phase_eight",
    "Phase_nine",
]

"""Compatibility shim for legacy imports.

The canonical phases implementation moved to `farfan_pipeline.phases`.
This module preserves historical imports.

New code should prefer:
- `import farfan_pipeline.phases...`
"""

from __future__ import annotations

from pathlib import Path


# Redirect package submodule resolution to the new location.
# Extend path to include farfan_pipeline/phases while keeping local directory
__path__.append(str((Path(__file__).resolve().parent.parent / "farfan_pipeline" / "phases").resolve()))

__all__ = [
    "Phase_zero",
    "Phase_two",
    "phase_1_cpp_ingestion",
    "phase_3_scoring_transformation",
    "phase_4_7_aggregation_pipeline",
    "Phase_eight",
    "Phase_nine",
]

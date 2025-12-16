"""Compatibility shim for legacy imports.

The canonical phases implementation moved to `farfan_pipeline.phases`.
This module preserves historical imports like:

- `import canonic_phases.Phase_zero...`

New code should prefer:
- `import farfan_pipeline.phases...`
"""

from __future__ import annotations

<<<<<<< HEAD
from pathlib import Path
=======
- Phase 0: Input Validation
- Phase 1: CPP Ingestion (CanonicalInput → CanonPolicyPackage)
- Phase 2: Signal-Driven Analysis
- Phase 3: Micro-answering and Integration
- Phase 4-7: Advanced Processing
- Phase 8: Strategic Integration
- Phase 9: Output Generation
>>>>>>> 1738f0eae4f67a51d31bb3e035e302d789b3050f


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

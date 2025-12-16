"""Compatibility shim for legacy imports.

The dashboard moved to `farfan_pipeline.dashboard_atroz_`.
This module preserves historical imports like:

- `import dashboard_atroz_.signals_service`

New code should prefer:
- `import farfan_pipeline.dashboard_atroz_.signals_service`
"""

from __future__ import annotations

from pathlib import Path


# Redirect package submodule resolution to the new location.
__path__ = [
    str((Path(__file__).resolve().parent.parent / "farfan_pipeline" / "dashboard_atroz_").resolve())
]

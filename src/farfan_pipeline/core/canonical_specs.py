"""Backward-compatible re-export of canonical constants.

This module exists so legacy imports `farfan_pipeline.core.canonical_specs`
continue to work after the canonical specs were stabilized under
`calibracion_parametrizacion.canonical_specs`.
"""

from farfan_pipeline.calibracion_parametrizacion.canonical_specs import *  # noqa: F401,F403

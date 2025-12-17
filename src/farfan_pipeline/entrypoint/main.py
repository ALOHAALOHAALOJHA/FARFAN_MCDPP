"""Console entrypoint for running the verified pipeline.

This delegates to the canonical runner implemented in Phase 0.
"""

from __future__ import annotations

from farfan_pipeline.phases.Phase_zero.main import cli as _phase0_cli


def main() -> None:
    _phase0_cli()

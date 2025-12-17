"""Compatibility shim for legacy imports.

The orchestration implementation moved to `farfan_pipeline.orchestration`.
This module preserves historical imports like:

- `from orchestration.orchestrator import Orchestrator`

New code should prefer:
- `from farfan_pipeline.orchestration.orchestrator import Orchestrator`
"""

from __future__ import annotations

from pathlib import Path

# Redirect package submodule resolution to the new location.
__path__ = [
    str((Path(__file__).resolve().parent.parent / "farfan_pipeline" / "orchestration").resolve())
]

# Preserve the legacy convenience exports.
from farfan_pipeline.orchestration.meta_layer import (  # noqa: E402
    MetaLayerConfig,
    MetaLayerEvaluator,
    create_default_config as create_default_meta_config,
)
from farfan_pipeline.orchestration.congruence_layer import (  # noqa: E402
    CongruenceLayerConfig,
    CongruenceLayerEvaluator,
    create_default_congruence_config,
)
from farfan_pipeline.orchestration.chain_layer import (  # noqa: E402
    ChainLayerConfig,
    ChainLayerEvaluator,
    create_default_chain_config,
)

__all__ = [
    "MetaLayerConfig",
    "MetaLayerEvaluator",
    "create_default_meta_config",
    "CongruenceLayerConfig",
    "CongruenceLayerEvaluator",
    "create_default_congruence_config",
    "ChainLayerConfig",
    "ChainLayerEvaluator",
    "create_default_chain_config",
]

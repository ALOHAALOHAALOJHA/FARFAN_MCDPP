"""
Orchestration Module

Provides orchestration capabilities including method registry, signature validation,
layer evaluation, and resource management for the F.A.R.F.A.N. pipeline.
"""

from orchestration.meta_layer import (
    MetaLayerConfig,
    MetaLayerEvaluator,
    create_default_config as create_default_meta_config
)

from orchestration.congruence_layer import (
    CongruenceLayerConfig,
    CongruenceLayerEvaluator,
    create_default_congruence_config
)

from orchestration.chain_layer import (
    ChainLayerConfig,
    ChainLayerEvaluator,
    create_default_chain_config
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

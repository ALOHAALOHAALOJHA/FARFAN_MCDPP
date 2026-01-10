"""
Module: Phase_two/__init__
PHASE_LABEL: Phase 2
Sequence: Package Init
Description: Phase 2 package interface and exports

Version: 1.0.0
Last Modified: 2025-12-20
Author: F.A.R.F.A.N Policy Pipeline
License: Proprietary

Phase 2: Analysis & Question Execution - Contract-Driven Processing.

This phase implements contract-driven question execution with evidence assembly,
narrative synthesis, and SISAS integration for deterministic policy analysis.

File Sequence (a-z, aa-ac):
- phase2_60_02_arg_router.py          : Argument routing
- phase2_60_00_base_executor_with_contract.py : Executor base class
- phase2_90_00_carver.py              : Narrative synthesis
- phase2_60_04_calibration_policy.py  : Calibration policies
- phase2_60_01_contract_validator_cqvr.py : Contract validation
- phase2_95_00_contract_hydrator.py   : V4 Contract hydrator (Signal irrigation bridge)
- phase2_80_00_evidence_nexus.py      : Evidence assembly
- phase2_20_00_method_signature_validator.py : Signature validation
- phase2_95_01_metrics_persistence.py : Metrics persistence
- phase2_95_02_precision_tracking.py  : Precision tracking
- phase2_30_01_resource_integration.py : Resource integration
- phase2_30_03_resource_aware_executor.py : Resource-aware executor
- phase2_30_00_resource_manager.py    : Resource management
- phase2_60_03_signature_runtime_validator.py : Runtime validation
- phase2_50_01_task_planner.py        : Task planning
- phase2_10_02_methods_registry.py    : Methods registry
- phase2_95_00_executor_profiler.py   : Profiling
- phase2_60_05_executor_instrumentation_mixin.py : Instrumentation
- phase2_95_03_executor_calibration_integration.py : Calibration integration
- phase2_10_03_executor_config.py     : Executor config
- phase2_40_03_irrigation_synchronizer.py : Signal irrigation
- phase2_40_00_synchronization.py     : Sync utilities
- phase2_40_01_executor_chunk_synchronizer.py : Chunk sync
- phase2_10_00_factory.py             : DI Factory
- phase2_10_01_class_registry.py      : Class registry
- phase2_40_02_schema_validation.py   : Schema validation
- phase2_z_generic_contract_executor.py : Generic executor
- phase2_20_01_method_source_validator.py : Source validation
- phase2_30_02_resource_alerts.py    : Resource alerts
- phase2_ac_executor_tests.py     : Executor tests
"""

from __future__ import annotations

from typing import TYPE_CHECKING

# Evidence processing - EvidenceNexus for causal graph construction
import farfan_pipeline.phases.Phase_2.phase2_80_00_evidence_nexus import (
    EvidenceNexus,
)

# Narrative synthesis - Doctoral Carver for PhD-level responses
import farfan_pipeline.phases.Phase_2.phase2_90_00_carver import (
    DoctoralCarverSynthesizer,
)

# Contract Hydrator - V4 to Carver-compatible adapter
import farfan_pipeline.phases.Phase_2.phase2_95_00_contract_hydrator import (
    ContractHydrator,
)

# Executor configuration and base class
import farfan_pipeline.phases.Phase_2.phase2_10_03_executor_config import ExecutorConfig
import farfan_pipeline.phases.Phase_2.phase2_60_00_base_executor_with_contract import (
    BaseExecutorWithContract,
)

__all__ = [
    # Evidence processing (EvidenceNexus)
    "EvidenceNexus",
    "EvidenceGraph",
    "EvidenceNode",
    "process_evidence",
    # Narrative synthesis (Carver)
    "DoctoralCarverSynthesizer",
    "DoctoralAnswerDict",
    # Contract Hydrator (Phase 2 - Step 95)
    "ContractHydrator",
    "ContractHydrationError",
    "HydrationResult",
    # Executor configuration
    "ExecutorConfig",
    "BaseExecutorWithContract",
]

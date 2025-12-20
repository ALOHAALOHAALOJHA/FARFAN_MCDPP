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
- phase2_a_arg_router.py          : Argument routing
- phase2_b_base_executor_with_contract.py : Executor base class
- phase2_c_carver.py              : Narrative synthesis
- phase2_d_calibration_policy.py  : Calibration policies
- phase2_e_contract_validator_cqvr.py : Contract validation
- phase2_f_evidence_nexus.py      : Evidence assembly
- phase2_g_method_signature_validator.py : Signature validation
- phase2_h_metrics_persistence.py : Metrics persistence
- phase2_i_precision_tracking.py  : Precision tracking
- phase2_j_resource_integration.py : Resource integration
- phase2_k_resource_aware_executor.py : Resource-aware executor
- phase2_l_resource_manager.py    : Resource management
- phase2_m_signature_runtime_validator.py : Runtime validation
- phase2_n_task_planner.py        : Task planning
- phase2_o_methods_registry.py    : Methods registry
- phase2_p_executor_profiler.py   : Profiling
- phase2_q_executor_instrumentation_mixin.py : Instrumentation
- phase2_r_executor_calibration_integration.py : Calibration integration
- phase2_s_executor_config.py     : Executor config
- phase2_t_irrigation_synchronizer.py : Signal irrigation
- phase2_u_synchronization.py     : Sync utilities
- phase2_v_executor_chunk_synchronizer.py : Chunk sync
- phase2_w_factory.py             : DI Factory
- phase2_x_class_registry.py      : Class registry
- phase2_y_schema_validation.py   : Schema validation
- phase2_z_generic_contract_executor.py : Generic executor
- phase2_aa_method_source_validator.py : Source validation
- phase2_ab_resource_alerts.py    : Resource alerts
- phase2_ac_executor_tests.py     : Executor tests
"""

from __future__ import annotations

from typing import TYPE_CHECKING

# Evidence processing - EvidenceNexus for causal graph construction
from farfan_pipeline.phases.Phase_two.phase2_f_evidence_nexus import (
    EvidenceNexus,
    EvidenceGraph,
    EvidenceNode,
    process_evidence,
)

# Narrative synthesis - Doctoral Carver for PhD-level responses
from farfan_pipeline.phases.Phase_two.phase2_c_carver import (
    DoctoralCarverSynthesizer,
    CarverAnswer,
)

# Executor configuration and base class
from farfan_pipeline.phases.Phase_two.phase2_s_executor_config import ExecutorConfig
from farfan_pipeline.phases.Phase_two.phase2_b_base_executor_with_contract import (
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
    "CarverAnswer",
    # Executor configuration
    "ExecutorConfig",
    "BaseExecutorWithContract",
]

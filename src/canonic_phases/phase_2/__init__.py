"""
Module: src.canonic_phases.phase_2
Purpose: Phase 2 canonical implementation - Argument routing and carving
Owner: phase2_orchestration
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-18

This package provides the canonical Phase 2 implementation with:
- Exhaustive argument routing with contract enforcement
- Deterministic carving of 60 CPP chunks into 300 micro-answers
- EvidenceNexus integration for graph-based evidence synthesis
- Phase 2.1 Irrigation orchestration (Question→Chunk→Task→Plan)
- Phase 2.2 Task execution (ExecutionPlan → 300 task results)
- Full provenance tracking and validation
- Strict cardinality contracts
"""
from __future__ import annotations

from .phase2_a_arg_router import (
    ArgRouter,
    ContractPayload,
    Executor,
    ExecutorResult,
    RegistryError,
    RoutingError,
    ValidationError,
)
from .phase2_b_carver import (
    Carver,
    CarverError,
    CPPChunk,
    MicroAnswer,
    ProvenanceError,
    carve_chunks,
)
from .phase2_c_nexus_integration import (
    NexusIntegrator,
    NexusIntegrationError,
    NexusResult,
    integrate_with_nexus,
)
from .phase2_d_irrigation_orchestrator import (
    IrrigationOrchestrator,
    ExecutionPlan,
    ExecutableTask,
    ChunkMatrix,
    ChunkRoutingResult,
    OrchestrationError,
    build_irrigation_plan,
)
from .phase2_e_task_executor import (
    TaskExecutor,
    DynamicContractExecutor,
    TaskResult,
    QuestionContext,
    ExecutionError,
    CalibrationError,
    execute_tasks,
)

__all__ = [
    # Router
    "ArgRouter",
    "ContractPayload",
    "Executor",
    "ExecutorResult",
    "RegistryError",
    "RoutingError",
    "ValidationError",
    # Carver
    "Carver",
    "CarverError",
    "CPPChunk",
    "MicroAnswer",
    "ProvenanceError",
    "carve_chunks",
    # Nexus Integration
    "NexusIntegrator",
    "NexusIntegrationError",
    "NexusResult",
    "integrate_with_nexus",
    # Irrigation Orchestration (Phase 2.1)
    "IrrigationOrchestrator",
    "ExecutionPlan",
    "ExecutableTask",
    "ChunkMatrix",
    "ChunkRoutingResult",
    "OrchestrationError",
    "build_irrigation_plan",
    # Task Execution (Phase 2.2)
    "TaskExecutor",
    "DynamicContractExecutor",
    "TaskResult",
    "QuestionContext",
    "ExecutionError",
    "CalibrationError",
    "execute_tasks",
]

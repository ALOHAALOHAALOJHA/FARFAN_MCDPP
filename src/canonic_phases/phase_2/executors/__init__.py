"""
Module: src.canonic_phases.phase_2.executors
Phase: 2 (Executor Orchestration)
Version: 1.0.0
Freeze Date: 2025-12-18
Classification: CANONICAL_FROZEN

Purpose:
Base executor contracts and implementations for Phase 2 policy processing.
Provides abstract base classes and instrumentation for deterministic execution.

Contracts Enforced:
- ABCContract (generic executor interface)
- InstrumentationContract (structured logging without output drift)
- ProfilingContract (overhead ≤5%, deterministic metrics)

Success Criteria:
- All executors implement run(payload: P) -> ExecutorResult
- No global state mutations
- Instrumentation is transparent (no output changes)

Failure Modes:
- Missing type hints
- Side effects in execution
- Output drift with instrumentation enabled

Verification:
- test_executor_contracts.py
- mypy --strict validation
"""

__all__ = [
    "base_executor_with_contract",
]

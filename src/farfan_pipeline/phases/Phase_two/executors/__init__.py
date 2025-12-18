"""Phase 2 Executor Module - Contract-Driven Question Analysis.

This module contains the base executor infrastructure for Phase 2 analysis.
Individual questions are executed through their JSON contracts (Q001-Q300.v3.json),
NOT through hardcoded executor classes.

Architecture:
- 300 question contracts in json_files_phase_two/executor_contracts/specialized/
- BaseExecutorWithContract provides contract loading and execution for ANY question
- No D1Q1-D6Q5 executor classes - contracts loaded directly by question_id
- Direct usage: BaseExecutorWithContract(question_id="Q001", ...)
"""

from __future__ import annotations

from canonic_phases.Phase_two.executors.base_executor_with_contract import (
    BaseExecutorWithContract,
)
from canonic_phases.Phase_two.executors.executor_config import ExecutorConfig

__all__ = [
    "BaseExecutorWithContract",
    "ExecutorConfig",
]

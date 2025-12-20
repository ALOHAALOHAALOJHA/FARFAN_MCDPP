"""Phase 2 Executor Module - Contract-Driven Question Analysis.

This module contains the base executor infrastructure for Phase 2 analysis.
Individual questions are executed through their JSON contracts (Q001-Q309.v3.json),
NOT through hardcoded executor classes.

Architecture:
- 309 question contracts in json_files_phase_two/executor_contracts/specialized/
- BaseExecutorWithContract provides contract loading and execution
- GenericContractExecutor executes ANY contract by question_id
- No D1Q1-D6Q5 executor classes - contracts loaded directly by question_id
"""

from __future__ import annotations

from canonic_phases.Phase_two.executors.base_executor_with_contract import (
    BaseExecutorWithContract,
)
from canonic_phases.Phase_two.executors.executor_config import ExecutorConfig
from canonic_phases.Phase_two.executors.generic_contract_executor import (
    GenericContractExecutor,
)

__all__ = [
    "BaseExecutorWithContract",
    "ExecutorConfig",
    "GenericContractExecutor",
]

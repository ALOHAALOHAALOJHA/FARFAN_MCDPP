"""
Module: src.canonic_phases.phase_2.tests.test_phase2_constants_enforcement
Purpose: Verify constants module integrity and forbid runtime monolith reads
Owner: phase2_orchestration
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-18

Contracts-Enforced:
    - ConstantsFreezeContract: All constants immutable
    - NoMonolithContract: No runtime reads from questionnaire_monolith.json

Determinism:
    Seed-Strategy: NOT_APPLICABLE
    State-Management: Stateless validation

Inputs:
    - phase2_constants module

Outputs:
    - validation_result: bool

Failure-Modes:
    - ConstantMutation: AssertionError — Constant value changed
    - MonolithImport: AssertionError — Forbidden import detected
"""
from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import List

import pytest

from src.canonic_phases.phase_2.constants.phase2_constants import (
    CPP_CHUNK_COUNT,
    MICRO_ANSWER_COUNT,
    SHARDS_PER_CHUNK,
    FORBIDDEN_IMPORTS,
    FORBIDDEN_RUNTIME_IO_PATTERNS,
)


class TestConstantsIntegrity:
    """Verify constants module integrity."""

    def test_cardinality_invariant(self) -> None:
        """CPP_CHUNK_COUNT * SHARDS_PER_CHUNK == MICRO_ANSWER_COUNT"""
        assert CPP_CHUNK_COUNT * SHARDS_PER_CHUNK == MICRO_ANSWER_COUNT

    def test_chunk_count_is_60(self) -> None:
        """Phase 1 contract: exactly 60 chunks."""
        assert CPP_CHUNK_COUNT == 60

    def test_micro_answer_count_is_300(self) -> None:
        """Phase 2 contract: exactly 300 micro-answers."""
        assert MICRO_ANSWER_COUNT == 300


class TestForbiddenImportsEnforcement:
    """Scan Phase 2 modules for forbidden imports."""

    @pytest.fixture
    def phase2_python_files(self) -> List[Path]:
        """Collect all Python files in Phase 2."""
        phase2_root = Path(__file__).parent.parent
        return list(phase2_root.rglob("*.py"))

    def test_no_forbidden_imports(self, phase2_python_files: List[Path]) -> None:
        """No Phase 2 file may import forbidden modules."""
        violations: List[str] = []

        for py_file in phase2_python_files:
            content = py_file.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(py_file))

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in FORBIDDEN_IMPORTS:
                            violations.append(
                                f"FORBIDDEN_IMPORT: {py_file}:{node.lineno} imports {alias.name}"
                            )
                elif isinstance(node, ast.ImportFrom):
                    if node.module and any(
                        forbidden in node.module for forbidden in FORBIDDEN_IMPORTS
                    ):
                        violations.append(
                            f"FORBIDDEN_IMPORT: {py_file}:{node.lineno} imports from {node.module}"
                        )

        assert not violations, "\n".join(violations)

    def test_no_runtime_monolith_io(self, phase2_python_files: List[Path]) -> None:
        """No Phase 2 file may read from questionnaire_monolith.json at runtime."""
        violations: List[str] = []

        for py_file in phase2_python_files:
            content = py_file.read_text(encoding="utf-8")
            try:
                tree = ast.parse(content, filename=str(py_file))
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func_name = ""
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                    elif isinstance(node.func, ast.Attribute):
                        func_name = node.func.attr

                    if func_name in ["open", "read_text", "load", "loads"]:
                        for arg in node.args:
                            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                                if "monolith" in arg.value.lower():
                                    violations.append(
                                        f"RUNTIME_MONOLITH_IO: {py_file}:{node.lineno} — {func_name}() with monolith reference"
                                    )

        assert not violations, "\n".join(violations)

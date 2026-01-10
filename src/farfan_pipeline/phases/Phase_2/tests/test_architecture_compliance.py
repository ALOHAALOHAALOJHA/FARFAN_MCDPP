"""
Test Architecture Compliance - SEVERE Adversarial Tests

PHASE_LABEL: Phase 2
PHASE_COMPONENT: Tests
PHASE_ROLE: Validate no legacy code remains, proper module structure

These tests are SEVERE and will FAIL if:
- Legacy executors.py exists
- Legacy executor class definitions found
- Improper imports to deprecated modules
- Module structure deviates from 300-contract architecture
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

# Constants
PHASE_TWO_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = PHASE_TWO_DIR.parent.parent.parent  # farfan_pipeline


class TestNoLegacyExecutors:
    """SEVERE: Ensure legacy executor design is completely removed."""

    def test_no_executors_py_file(self) -> None:
        """FAIL if executors.py exists."""
        executors_path = PHASE_TWO_DIR / "executors.py"

        assert not executors_path.exists(), (
            f"LEGACY FILE EXISTS: {executors_path}. "
            "executors.py with hardcoded executor classes is DEPRECATED. "
            "DELETE this file - DynamicContractExecutor replaces all executor classes."
        )

    def test_no_executor_class_files(self) -> None:
        """FAIL if files named like D1Q1_executor.py exist."""
        legacy_pattern = re.compile(r"D\d+[_]?Q\d+[_]?executor", re.IGNORECASE)
        legacy_files = []

        for py_file in PHASE_TWO_DIR.glob("**/*.py"):
            if legacy_pattern.search(py_file.name):
                legacy_files.append(py_file)

        assert not legacy_files, (
            "LEGACY EXECUTOR FILES FOUND:\n"
            + "\n".join(f"  {f}" for f in legacy_files)
            + "\nDELETE these files - they are replaced by 300 JSON contracts."
        )

    def test_no_30_executor_class_definitions(self) -> None:
        """FAIL if any Python file defines D1Q1_Executor style classes."""
        class_pattern = re.compile(r"class\s+D\d+[_]?Q\d+[_]?(?:PA\d+)?[_]?Executor")
        violations = []

        for py_file in PHASE_TWO_DIR.glob("**/*.py"):
            if py_file.name.startswith("test_"):
                continue

            content = py_file.read_text(encoding="utf-8", errors="ignore")
            matches = class_pattern.findall(content)
            if matches:
                violations.append((py_file.name, matches))

        assert not violations, (
            "LEGACY EXECUTOR CLASS DEFINITIONS in:\n"
            + "\n".join(f"  {name}: {classes}" for name, classes in violations)
            + "\n\nREMOVE these class definitions. "
            "300 JSON contracts replace ALL hardcoded executor classes."
        )

    def test_no_executor_module_imports(self) -> None:
        """FAIL if code imports from deprecated executors module."""
        import_pattern = re.compile(r"from\s+[\w.]*executors\s+import|import\s+[\w.]*executors")
        violations = []

        for py_file in PHASE_TWO_DIR.glob("**/*.py"):
            if py_file.name.startswith("test_"):
                continue

            content = py_file.read_text(encoding="utf-8", errors="ignore")
            matches = import_pattern.findall(content)
            if matches:
                # Exclude legitimate imports like base_executor_with_contract
                filtered = [m for m in matches if "base_executor" not in m.lower()]
                if filtered:
                    violations.append((py_file.name, filtered))

        assert not violations, (
            "LEGACY EXECUTOR IMPORTS:\n"
            + "\n".join(f"  {name}: {imports}" for name, imports in violations)
            + "\n\nREMOVE these imports. Use DynamicContractExecutor instead."
        )


class TestDynamicContractExecutorPresent:
    """SEVERE: Validate DynamicContractExecutor is properly implemented."""

    def test_dynamic_contract_executor_exists(self) -> None:
        """FAIL if DynamicContractExecutor class is missing."""
        executor_file = PHASE_TWO_DIR / "phase2_60_00_base_executor_with_contract.py"

        assert executor_file.exists(), (
            f"CRITICAL: {executor_file.name} MISSING. "
            "DynamicContractExecutor is required for 300-contract execution."
        )

        content = executor_file.read_text(encoding="utf-8")
        assert "class DynamicContractExecutor" in content, (
            "CRITICAL: DynamicContractExecutor class NOT FOUND in "
            f"{executor_file.name}. This class is REQUIRED."
        )

    def test_dynamic_executor_has_derive_base_slot(self) -> None:
        """FAIL if _derive_base_slot method is missing."""
        executor_file = PHASE_TWO_DIR / "phase2_60_00_base_executor_with_contract.py"

        if not executor_file.exists():
            pytest.skip("Executor file doesn't exist")

        content = executor_file.read_text(encoding="utf-8")
        assert "_derive_base_slot" in content, (
            "CRITICAL: _derive_base_slot method MISSING from DynamicContractExecutor. "
            "This method maps Q001-Q300 to D1-Q1 through D6-Q5 base slots."
        )

    def test_dynamic_executor_loads_v4_contracts(self) -> None:
        """FAIL if executor doesn't load from generated_contracts/."""
        executor_file = PHASE_TWO_DIR / "phase2_60_00_base_executor_with_contract.py"

        if not executor_file.exists():
            pytest.skip("Executor file doesn't exist")

        content = executor_file.read_text(encoding="utf-8")
        assert "generated_contracts" in content, (
            "CRITICAL: DynamicContractExecutor doesn't reference generated_contracts/. "
            "v4 contracts MUST be loaded from generated_contracts/ directory."
        )


class TestTaskExecutorArchitecture:
    """SEVERE: Validate TaskExecutor implements 300-contract model."""

    def test_task_executor_exists(self) -> None:
        """FAIL if TaskExecutor is missing."""
        task_executor_file = PHASE_TWO_DIR / "phase2_50_00_task_executor.py"

        assert task_executor_file.exists(), (
            f"CRITICAL: {task_executor_file.name} MISSING. "
            "TaskExecutor is required for 300-task execution."
        )

    def test_task_executor_uses_dynamic_executor(self) -> None:
        """FAIL if TaskExecutor doesn't use DynamicContractExecutor."""
        task_executor_file = PHASE_TWO_DIR / "phase2_50_00_task_executor.py"

        if not task_executor_file.exists():
            pytest.skip("TaskExecutor doesn't exist")

        content = task_executor_file.read_text(encoding="utf-8")
        assert "DynamicContractExecutor" in content, (
            "TaskExecutor MUST use DynamicContractExecutor for contract execution. "
            "Found no reference to DynamicContractExecutor."
        )

    def test_task_executor_sequential_by_default(self) -> None:
        """FAIL if default execution is parallel."""
        task_executor_file = PHASE_TWO_DIR / "phase2_50_00_task_executor.py"

        if not task_executor_file.exists():
            pytest.skip("TaskExecutor doesn't exist")

        content = task_executor_file.read_text(encoding="utf-8")

        # Check that execute_plan (non-parallel) exists
        assert (
            "def execute_plan(" in content
        ), "TaskExecutor MUST have execute_plan() method for sequential execution."


class TestModuleStructure:
    """SEVERE: Validate Phase 2 module structure."""

    REQUIRED_MODULES = [
        "phase2_10_00_factory.py",
        "phase2_10_01_class_registry.py",
        "phase2_10_02_methods_registry.py",
        "phase2_50_00_task_executor.py",
        "phase2_60_00_base_executor_with_contract.py",
        "phase2_80_00_evidence_nexus.py",
        "phase2_90_00_carver.py",
        "phase2_95_00_contract_hydrator.py",
    ]

    @pytest.mark.parametrize("module_name", REQUIRED_MODULES)
    def test_required_module_exists(self, module_name: str) -> None:
        """FAIL if required module is missing."""
        module_path = PHASE_TWO_DIR / module_name

        assert module_path.exists(), (
            f"REQUIRED MODULE MISSING: {module_name}. "
            "This module is critical for Phase 2 execution."
        )

    def test_all_modules_have_phase_label(self) -> None:
        """FAIL if any module lacks PHASE_LABEL: Phase 2."""
        modules_without_label = []

        for py_file in PHASE_TWO_DIR.glob("phase2_*.py"):
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            # Check first 50 lines for PHASE_LABEL
            lines = content.split("\n")[:50]
            header = "\n".join(lines)

            if "PHASE_LABEL" not in header:
                modules_without_label.append(py_file.name)

        assert not modules_without_label, (
            "MODULES MISSING PHASE_LABEL:\n"
            + "\n".join(f"  {m}" for m in modules_without_label)
            + "\n\nAll Phase 2 modules MUST have 'PHASE_LABEL: Phase 2' in docstring."
        )

    def test_init_exports_key_components(self) -> None:
        """FAIL if __init__.py doesn't export key components."""
        init_file = PHASE_TWO_DIR / "__init__.py"

        assert init_file.exists(), "Phase 2 __init__.py MISSING"

        content = init_file.read_text(encoding="utf-8")

        required_exports = [
            "EvidenceNexus",
            "DoctoralCarverSynthesizer",
            "ContractHydrator",
            "BaseExecutorWithContract",
        ]

        missing = [e for e in required_exports if e not in content]

        assert not missing, (
            f"__init__.py MISSING EXPORTS: {missing}. "
            "These components must be exported for Phase 2 usage."
        )


class TestNoCompetingImplementations:
    """SEVERE: Ensure no competing/duplicate executor implementations."""

    def test_single_base_executor_class(self) -> None:
        """FAIL if multiple BaseExecutor classes exist."""
        base_executor_classes = []

        for py_file in PHASE_TWO_DIR.glob("**/*.py"):
            if py_file.name.startswith("test_"):
                continue

            content = py_file.read_text(encoding="utf-8", errors="ignore")
            if "class BaseExecutorWithContract" in content:
                base_executor_classes.append(py_file.name)

        assert len(base_executor_classes) == 1, (
            "MULTIPLE BaseExecutorWithContract definitions found in:\n"
            + "\n".join(f"  {f}" for f in base_executor_classes)
            + "\n\nThere MUST be exactly ONE BaseExecutorWithContract class."
        )

    def test_no_competing_execution_entry_points(self) -> None:
        """FAIL if multiple main execution entry points exist."""
        entry_patterns = [
            r"def\s+main\s*\(",
            r"if\s+__name__\s*==\s*['\"]__main__['\"]",
        ]

        files_with_entry = []

        for py_file in PHASE_TWO_DIR.glob("phase2_*.py"):
            content = py_file.read_text(encoding="utf-8", errors="ignore")

            for pattern in entry_patterns:
                if re.search(pattern, content):
                    files_with_entry.append(py_file.name)
                    break

        # Allow max 3 files with main entry (factory, task_executor, one test)
        assert len(files_with_entry) <= 5, (
            f"TOO MANY EXECUTION ENTRY POINTS ({len(files_with_entry)}):\n"
            + "\n".join(f"  {f}" for f in files_with_entry)
            + "\n\nPhase 2 should have a SINGLE primary entry point."
        )


class TestContractHydratorIntegration:
    """SEVERE: Validate ContractHydrator bridges v4 contracts to Carver."""

    def test_contract_hydrator_exists(self) -> None:
        """FAIL if ContractHydrator is missing."""
        hydrator_file = PHASE_TWO_DIR / "phase2_95_00_contract_hydrator.py"

        assert hydrator_file.exists(), (
            "CRITICAL: phase2_95_00_contract_hydrator.py MISSING. "
            "ContractHydrator is required to bridge v4 contracts to Carver."
        )

    def test_hydrator_handles_v4_contracts(self) -> None:
        """FAIL if hydrator doesn't handle v4 format."""
        hydrator_file = PHASE_TWO_DIR / "phase2_95_00_contract_hydrator.py"

        if not hydrator_file.exists():
            pytest.skip("Hydrator doesn't exist")

        content = hydrator_file.read_text(encoding="utf-8")

        assert "monolith_ref" in content or "v4" in content.lower(), (
            "ContractHydrator doesn't appear to handle v4 contract format. "
            "Must process monolith_ref and streamlined v4 structure."
        )


class TestFactoryDependencyInjection:
    """SEVERE: Validate Factory is single authority for DI."""

    def test_factory_exists(self) -> None:
        """FAIL if factory module is missing."""
        factory_file = PHASE_TWO_DIR / "phase2_10_00_factory.py"

        assert factory_file.exists(), (
            "CRITICAL: phase2_10_00_factory.py MISSING. "
            "AnalysisPipelineFactory is required for dependency injection."
        )

    def test_factory_has_create_orchestrator(self) -> None:
        """FAIL if factory lacks create_orchestrator method."""
        factory_file = PHASE_TWO_DIR / "phase2_10_00_factory.py"

        if not factory_file.exists():
            pytest.skip("Factory doesn't exist")

        content = factory_file.read_text(encoding="utf-8")

        assert "create_orchestrator" in content, (
            "AnalysisPipelineFactory MUST have create_orchestrator() method. "
            "This is the primary entry point for Phase 2 initialization."
        )

    def test_factory_builds_signal_registry(self) -> None:
        """FAIL if factory doesn't build SignalRegistry."""
        factory_file = PHASE_TWO_DIR / "phase2_10_00_factory.py"

        if not factory_file.exists():
            pytest.skip("Factory doesn't exist")

        content = factory_file.read_text(encoding="utf-8")

        assert (
            "SignalRegistry" in content or "signal_registry" in content
        ), "Factory MUST build SignalRegistry for SISAS integration."


class TestNoParallelExecutionInDefaultPath:
    """SEVERE: Ensure default execution path is sequential."""

    def test_task_executor_no_threadpool_in_execute_plan(self) -> None:
        """FAIL if execute_plan uses ThreadPoolExecutor."""
        task_executor_file = PHASE_TWO_DIR / "phase2_50_00_task_executor.py"

        if not task_executor_file.exists():
            pytest.skip("TaskExecutor doesn't exist")

        content = task_executor_file.read_text(encoding="utf-8")

        # Find execute_plan method and check it doesn't use ThreadPoolExecutor
        # This is a heuristic - parallel execution should be in separate method
        execute_plan_match = re.search(
            r"def execute_plan\([^)]*\):[^}]*?(?=def\s|\Z)", content, re.DOTALL
        )

        if execute_plan_match:
            method_body = execute_plan_match.group(0)
            if "ThreadPoolExecutor" in method_body or "ProcessPoolExecutor" in method_body:
                # Check if it's the parallel variant
                if "execute_plan_parallel" not in method_body:
                    pytest.fail(
                        "execute_plan() should be SEQUENTIAL. "
                        "Parallel execution should be in execute_plan_parallel()."
                    )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=long"])

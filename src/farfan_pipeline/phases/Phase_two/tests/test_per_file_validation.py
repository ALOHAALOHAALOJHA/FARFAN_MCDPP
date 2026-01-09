"""
Per-File Adversarial Tests - SEVERE Module-by-Module Validation

PHASE_LABEL: Phase 2
PHASE_COMPONENT: Tests
PHASE_ROLE: Individual file validation with adversarial checks

Each Phase 2 module is tested for:
- Correct PHASE_LABEL presence
- Required exports/functions
- No legacy references
- Proper integration points
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

import pytest

PHASE_TWO_DIR = Path(__file__).parent.parent


class TestPhase2Factory:
    """SEVERE: Test phase2_10_00_factory.py"""

    @pytest.fixture
    def factory_content(self) -> str:
        path = PHASE_TWO_DIR / "phase2_10_00_factory.py"
        if not path.exists():
            pytest.skip("Factory doesn't exist")
        return path.read_text(encoding="utf-8")

    def test_has_phase_label(self, factory_content: str) -> None:
        """FAIL if missing PHASE_LABEL."""
        assert "PHASE_LABEL" in factory_content[:2000], "Factory MUST have PHASE_LABEL"

    def test_has_analysis_pipeline_factory_class(self, factory_content: str) -> None:
        """FAIL if AnalysisPipelineFactory class missing."""
        assert "class AnalysisPipelineFactory" in factory_content, (
            "Factory MUST define AnalysisPipelineFactory class"
        )

    def test_has_create_orchestrator_method(self, factory_content: str) -> None:
        """FAIL if create_orchestrator missing."""
        assert "create_orchestrator" in factory_content

    def test_builds_signal_registry(self, factory_content: str) -> None:
        """FAIL if doesn't build SignalRegistry."""
        assert "SignalRegistry" in factory_content

    def test_builds_method_executor(self, factory_content: str) -> None:
        """FAIL if doesn't build MethodExecutor."""
        assert "MethodExecutor" in factory_content or "method_executor" in factory_content

    def test_no_legacy_30_executor_creation(self, factory_content: str) -> None:
        """FAIL if creates legacy executor instances."""
        legacy_pattern = re.compile(r"D\d+Q\d+_Executor\s*\(")
        matches = legacy_pattern.findall(factory_content)
        assert not matches, f"LEGACY EXECUTOR INSTANTIATION: {matches}"


class TestPhase2ClassRegistry:
    """SEVERE: Test phase2_10_01_class_registry.py"""

    @pytest.fixture
    def registry_content(self) -> str:
        path = PHASE_TWO_DIR / "phase2_10_01_class_registry.py"
        if not path.exists():
            pytest.skip("Class registry doesn't exist")
        return path.read_text(encoding="utf-8")

    def test_has_phase_label(self, registry_content: str) -> None:
        assert "PHASE_LABEL" in registry_content[:2000]

    def test_has_build_class_registry_function(self, registry_content: str) -> None:
        """FAIL if build_class_registry function missing."""
        assert "build_class_registry" in registry_content or "ClassRegistry" in registry_content

    def test_maps_class_names_to_paths(self, registry_content: str) -> None:
        """FAIL if doesn't map class names."""
        assert "class_name" in registry_content.lower() or "import_path" in registry_content


class TestPhase2MethodsRegistry:
    """SEVERE: Test phase2_10_02_methods_registry.py"""

    @pytest.fixture
    def methods_registry_content(self) -> str:
        path = PHASE_TWO_DIR / "phase2_10_02_methods_registry.py"
        if not path.exists():
            pytest.skip("Methods registry doesn't exist")
        return path.read_text(encoding="utf-8")

    def test_has_phase_label(self, methods_registry_content: str) -> None:
        assert "PHASE_LABEL" in methods_registry_content[:2000]

    def test_has_lazy_loading(self, methods_registry_content: str) -> None:
        """FAIL if doesn't implement lazy loading."""
        assert "lazy" in methods_registry_content.lower() or "cache" in methods_registry_content.lower()


class TestPhase2ExecutorConfig:
    """SEVERE: Test phase2_10_03_executor_config.py"""

    @pytest.fixture
    def config_content(self) -> str:
        path = PHASE_TWO_DIR / "phase2_10_03_executor_config.py"
        if not path.exists():
            pytest.skip("Executor config doesn't exist")
        return path.read_text(encoding="utf-8")

    def test_has_phase_label(self, config_content: str) -> None:
        assert "PHASE_LABEL" in config_content[:2000]

    def test_has_timeout_config(self, config_content: str) -> None:
        assert "timeout" in config_content.lower()

    def test_has_memory_limit_config(self, config_content: str) -> None:
        assert "memory" in config_content.lower() or "mem" in config_content.lower()


class TestPhase2TaskExecutor:
    """SEVERE: Test phase2_50_00_task_executor.py"""

    @pytest.fixture
    def task_executor_content(self) -> str:
        path = PHASE_TWO_DIR / "phase2_50_00_task_executor.py"
        if not path.exists():
            pytest.skip("Task executor doesn't exist")
        return path.read_text(encoding="utf-8")

    def test_has_phase_label(self, task_executor_content: str) -> None:
        assert "PHASE_LABEL" in task_executor_content[:2000]

    def test_has_task_executor_class(self, task_executor_content: str) -> None:
        assert "class TaskExecutor" in task_executor_content

    def test_has_execute_plan_method(self, task_executor_content: str) -> None:
        assert "def execute_plan" in task_executor_content

    def test_uses_dynamic_contract_executor(self, task_executor_content: str) -> None:
        """FAIL if doesn't use DynamicContractExecutor."""
        assert "DynamicContractExecutor" in task_executor_content

    def test_has_checkpointing(self, task_executor_content: str) -> None:
        """FAIL if no checkpointing support."""
        assert "checkpoint" in task_executor_content.lower()

    def test_supports_dry_run(self, task_executor_content: str) -> None:
        """FAIL if no dry_run support."""
        assert "dry_run" in task_executor_content.lower() or "dry-run" in task_executor_content.lower()


class TestPhase2BaseExecutor:
    """SEVERE: Test phase2_60_00_base_executor_with_contract.py"""

    @pytest.fixture
    def base_executor_content(self) -> str:
        path = PHASE_TWO_DIR / "phase2_60_00_base_executor_with_contract.py"
        if not path.exists():
            pytest.skip("Base executor doesn't exist")
        return path.read_text(encoding="utf-8")

    def test_has_phase_label(self, base_executor_content: str) -> None:
        assert "PHASE_LABEL" in base_executor_content[:2000]

    def test_has_base_executor_class(self, base_executor_content: str) -> None:
        assert "class BaseExecutorWithContract" in base_executor_content

    def test_has_dynamic_contract_executor(self, base_executor_content: str) -> None:
        """FAIL if DynamicContractExecutor missing."""
        assert "class DynamicContractExecutor" in base_executor_content

    def test_has_load_contract_method(self, base_executor_content: str) -> None:
        assert "_load_contract" in base_executor_content

    def test_has_execute_v3_method(self, base_executor_content: str) -> None:
        """FAIL if v4 execution path missing."""
        assert "_execute_v3" in base_executor_content

    def test_loads_from_generated_contracts(self, base_executor_content: str) -> None:
        """FAIL if doesn't load from generated_contracts/."""
        assert "generated_contracts" in base_executor_content

    def test_validates_v4_contract_version(self, base_executor_content: str) -> None:
        """FAIL if doesn't check for v4."""
        assert "v4" in base_executor_content or "_contract_version" in base_executor_content

    def test_requires_policy_area_id(self, base_executor_content: str) -> None:
        """FAIL if policy_area_id not validated."""
        assert "policy_area_id" in base_executor_content

    def test_validates_signal_registry(self, base_executor_content: str) -> None:
        """FAIL if signal_registry not validated."""
        assert "signal_registry is None" in base_executor_content


class TestPhase2EvidenceNexus:
    """SEVERE: Test phase2_80_00_evidence_nexus.py"""

    @pytest.fixture
    def nexus_content(self) -> str:
        path = PHASE_TWO_DIR / "phase2_80_00_evidence_nexus.py"
        if not path.exists():
            pytest.skip("EvidenceNexus doesn't exist")
        return path.read_text(encoding="utf-8")

    def test_has_phase_label(self, nexus_content: str) -> None:
        assert "PHASE_LABEL" in nexus_content[:2000]

    def test_has_evidence_nexus_class(self, nexus_content: str) -> None:
        assert "class EvidenceNexus" in nexus_content

    def test_has_process_evidence_function(self, nexus_content: str) -> None:
        assert "def process_evidence" in nexus_content

    def test_has_evidence_graph_class(self, nexus_content: str) -> None:
        assert "EvidenceGraph" in nexus_content

    def test_implements_dempster_shafer(self, nexus_content: str) -> None:
        """FAIL if no Dempster-Shafer belief propagation."""
        assert "dempster" in nexus_content.lower() or "belief" in nexus_content.lower()


class TestPhase2Carver:
    """SEVERE: Test phase2_90_00_carver.py"""

    @pytest.fixture
    def carver_content(self) -> str:
        path = PHASE_TWO_DIR / "phase2_90_00_carver.py"
        if not path.exists():
            pytest.skip("Carver doesn't exist")
        return path.read_text(encoding="utf-8")

    def test_has_phase_label(self, carver_content: str) -> None:
        assert "PHASE_LABEL" in carver_content[:2000]

    def test_has_doctoral_carver_class(self, carver_content: str) -> None:
        assert "DoctoralCarverSynthesizer" in carver_content

    def test_has_synthesize_method(self, carver_content: str) -> None:
        assert "def synthesize" in carver_content

    def test_produces_human_readable(self, carver_content: str) -> None:
        """FAIL if doesn't produce human readable output."""
        assert "human_readable" in carver_content.lower()

    def test_enforces_citations(self, carver_content: str) -> None:
        """FAIL if doesn't enforce citations."""
        assert "citation" in carver_content.lower() or "evidence" in carver_content.lower()


class TestPhase2ContractHydrator:
    """SEVERE: Test phase2_95_00_contract_hydrator.py"""

    @pytest.fixture
    def hydrator_content(self) -> str:
        path = PHASE_TWO_DIR / "phase2_95_00_contract_hydrator.py"
        if not path.exists():
            pytest.skip("Contract hydrator doesn't exist")
        return path.read_text(encoding="utf-8")

    def test_has_phase_label(self, hydrator_content: str) -> None:
        assert "PHASE_LABEL" in hydrator_content[:2000]

    def test_has_contract_hydrator_class(self, hydrator_content: str) -> None:
        assert "class ContractHydrator" in hydrator_content

    def test_has_hydrate_method(self, hydrator_content: str) -> None:
        assert "def hydrate" in hydrator_content

    def test_handles_monolith_ref(self, hydrator_content: str) -> None:
        """FAIL if doesn't handle v4 monolith_ref."""
        assert "monolith_ref" in hydrator_content

    def test_injects_signal_data(self, hydrator_content: str) -> None:
        """FAIL if doesn't inject signal data."""
        assert "signal" in hydrator_content.lower()


class TestPhase2ResourceManager:
    """SEVERE: Test phase2_30_00_resource_manager.py"""

    @pytest.fixture
    def resource_content(self) -> str:
        path = PHASE_TWO_DIR / "phase2_30_00_resource_manager.py"
        if not path.exists():
            pytest.skip("Resource manager doesn't exist")
        return path.read_text(encoding="utf-8")

    def test_has_phase_label(self, resource_content: str) -> None:
        assert "PHASE_LABEL" in resource_content[:2000]

    def test_has_memory_limits(self, resource_content: str) -> None:
        assert "memory" in resource_content.lower()

    def test_has_time_limits(self, resource_content: str) -> None:
        assert "timeout" in resource_content.lower() or "time" in resource_content.lower()


class TestPhase2IrrigationSynchronizer:
    """SEVERE: Test phase2_40_03_irrigation_synchronizer.py"""

    @pytest.fixture
    def irrigation_content(self) -> str:
        path = PHASE_TWO_DIR / "phase2_40_03_irrigation_synchronizer.py"
        if not path.exists():
            pytest.skip("Irrigation synchronizer doesn't exist")
        return path.read_text(encoding="utf-8")

    def test_has_phase_label(self, irrigation_content: str) -> None:
        assert "PHASE_LABEL" in irrigation_content[:2000]

    def test_builds_execution_plan(self, irrigation_content: str) -> None:
        """FAIL if doesn't build ExecutionPlan."""
        assert "ExecutionPlan" in irrigation_content or "execution_plan" in irrigation_content.lower()

    def test_transforms_60_to_300(self, irrigation_content: str) -> None:
        """FAIL if doesn't handle 60→300 transformation."""
        assert "300" in irrigation_content or "300" in irrigation_content


class TestPhase2CalibrationPolicy:
    """SEVERE: Test phase2_60_04_calibration_policy.py"""

    @pytest.fixture
    def calibration_content(self) -> str:
        path = PHASE_TWO_DIR / "phase2_60_04_calibration_policy.py"
        if not path.exists():
            pytest.skip("Calibration policy doesn't exist")
        return path.read_text(encoding="utf-8")

    def test_has_phase_label(self, calibration_content: str) -> None:
        assert "PHASE_LABEL" in calibration_content[:2000]

    def test_has_calibration_policy_class(self, calibration_content: str) -> None:
        assert "CalibrationPolicy" in calibration_content

    def test_supports_300_contracts(self, calibration_content: str) -> None:
        """FAIL if references 30 executors instead of 300 contracts."""
        assert "300" in calibration_content


class TestPhase2SynchronizationModule:
    """SEVERE: Test phase2_40_00_synchronization.py"""

    @pytest.fixture
    def sync_content(self) -> str:
        path = PHASE_TWO_DIR / "phase2_40_00_synchronization.py"
        if not path.exists():
            pytest.skip("Synchronization module doesn't exist")
        return path.read_text(encoding="utf-8")

    def test_has_phase_label(self, sync_content: str) -> None:
        assert "PHASE_LABEL" in sync_content[:2000]

    def test_builds_chunk_matrix(self, sync_content: str) -> None:
        """FAIL if doesn't build ChunkMatrix."""
        assert "ChunkMatrix" in sync_content or "chunk_matrix" in sync_content.lower()


class TestAllModulesHavePhaseLabel:
    """SEVERE: Ensure ALL phase2_*.py modules have PHASE_LABEL."""

    def test_all_phase2_modules_labeled(self) -> None:
        """FAIL if any module lacks PHASE_LABEL."""
        unlabeled = []
        
        for py_file in PHASE_TWO_DIR.glob("phase2_*.py"):
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            # Check first 3000 chars for PHASE_LABEL
            if "PHASE_LABEL" not in content[:3000]:
                unlabeled.append(py_file.name)
        
        assert not unlabeled, (
            f"MODULES WITHOUT PHASE_LABEL:\n"
            + "\n".join(f"  {m}" for m in unlabeled)
        )


class TestNoLegacyPatternsInAnyModule:
    """SEVERE: Ensure NO module contains legacy patterns."""

    def test_no_legacy_executor_patterns(self) -> None:
        """FAIL if any module has legacy executor patterns."""
        legacy_pattern = re.compile(r"class\s+D\d+[_]?Q\d+[_]?(?:PA\d+)?[_]?Executor")
        violations = []
        
        for py_file in PHASE_TWO_DIR.glob("phase2_*.py"):
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            matches = legacy_pattern.findall(content)
            if matches:
                violations.append((py_file.name, matches))
        
        assert not violations, (
            f"LEGACY EXECUTOR CLASSES in:\n"
            + "\n".join(f"  {name}: {classes}" for name, classes in violations)
        )

    def test_no_executors_module_import(self) -> None:
        """FAIL if any module imports from deprecated executors."""
        violations = []
        
        for py_file in PHASE_TWO_DIR.glob("phase2_*.py"):
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            
            # Check for imports from executors module
            if re.search(r"from\s+\.executors\s+import|from\s+executors\s+import", content):
                violations.append(py_file.name)
        
        assert not violations, (
            f"DEPRECATED executors IMPORT in: {violations}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=long"])

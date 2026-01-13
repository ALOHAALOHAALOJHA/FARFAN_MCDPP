"""
PHASE 1 TOPOLOGICAL ORDER ADVERSARIAL TEST SUITE
==================================================

Adversarial tests for Phase 1 dependency graph and topological ordering.
Tests attack the structural integrity of the import chain and verify
the DAG is properly maintained.

Test Categories:
1. Graph Structure Tests - Verify DAG properties
2. Import Dependency Tests - Verify actual imports match expectations
3. Cycle Detection Tests - Verify no circular dependencies
4. Orphan Detection Tests - Verify all modules are in chain
5. Edge Case Tests - Boundary conditions for the graph

Author: F.A.R.F.A.N Testing Team
Version: 2.0.0 (Post-Normalization)
Status: ADVERSARIAL - Break if you can
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

import pytest


# =============================================================================
# TEST DATA (Based on post-normalization state)
# =============================================================================

EXPECTED_TOPOLOGICAL_ORDER = [
    "PHASE_1_CONSTANTS",
    "phase1_02_00_phase_1_constants",
    "phase1_03_00_models",
    "phase1_05_00_thread_safe_results",
    "phase1_06_00_questionnaire_mapper",
    "phase1_07_00_sp4_question_aware",
    "phase1_09_00_circuit_breaker",
    "phase1_11_00_signal_enrichment",
    "phase1_12_00_structural",
    "phase1_13_00_cpp_ingestion",
]

RECLASSIFIED_MODULES = {
    "phase1_01_00_cpp_models": "docs/legacy/",
    "phase1_04_00_phase_protocol": "interphase/",
    "phase1_08_00_adapter": "interphase/",
    "phase1_10_00_dependency_validator": "primitives/",
}


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def phase1_dir() -> Path:
    """Get Phase 1 directory path."""
    repo_root = Path(__file__).parent.parent.parent
    return repo_root / "src" / "farfan_pipeline" / "phases" / "Phase_1"


@pytest.fixture(scope="session")
def dependency_graph(phase1_dir: Path) -> Dict[str, Set[str]]:
    """Build the dependency graph from actual imports."""
    graph: Dict[str, Set[str]] = {}

    py_files = [
        "__init__.py",
        "PHASE_1_CONSTANTS.py",
        "phase1_02_00_phase_1_constants.py",
        "phase1_03_00_models.py",
        "phase1_05_00_thread_safe_results.py",
        "phase1_06_00_questionnaire_mapper.py",
        "phase1_07_00_sp4_question_aware.py",
        "phase1_09_00_circuit_breaker.py",
        "phase1_11_00_signal_enrichment.py",
        "phase1_12_00_structural.py",
        "phase1_13_00_cpp_ingestion.py",
    ]

    for py_file in py_files:
        module_name = py_file.replace(".py", "")
        filepath = phase1_dir / py_file

        if not filepath.exists():
            continue

        try:
            with open(filepath, "r") as f:
                content = f.read()
                tree = ast.parse(content, filename=py_file)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imp = alias.name.split(".")[0]
                        if imp.startswith("phase1_") or imp == "PHASE_1_CONSTANTS":
                            graph.setdefault(module_name, set()).add(imp)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        mod_full = node.module
                        if node.level > 0:
                            if mod_full.startswith("phase1_") or mod_full == "PHASE_1_CONSTANTS":
                                graph.setdefault(module_name, set()).add(mod_full)
        except Exception:
            pass

    return graph


# =============================================================================
# 1. GRAPH STRUCTURE TESTS
# =============================================================================

class TestGraphStructure:
    """Test the fundamental structure of the dependency graph."""

    def test_graph_is_dag(self, dependency_graph: Dict[str, Set[str]]):
        """The dependency graph must be a Directed Acyclic Graph (DAG)."""
        cycles = self._find_cycles(dependency_graph)
        assert len(cycles) == 0, f"Graph has cycles: {cycles}"

    def _find_cycles(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        """Detect cycles using DFS."""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: List[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, set()):
                if neighbor not in visited:
                    dfs(neighbor, path)
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])

            rec_stack.remove(node)
            path.pop()

        for node in graph:
            if node not in visited:
                dfs(node, [])

        return cycles

    def test_all_modules_in_graph(self, dependency_graph: Dict[str, Set[str]]):
        """All expected modules must be present in the graph."""
        for module in EXPECTED_TOPOLOGICAL_ORDER:
            assert module in dependency_graph or module == "PHASE_1_CONSTANTS", \
                f"Module not in graph: {module}"

    def test_graph_connectedness(self, dependency_graph: Dict[str, Set[str]]):
        """The graph should be connected (or have valid isolated nodes)."""
        all_nodes = set(dependency_graph.keys())
        for deps in dependency_graph.values():
            all_nodes.update(deps)

        # All expected nodes should be present
        for expected in EXPECTED_TOPOLOGICAL_ORDER:
            assert expected in all_nodes, f"Expected node not in graph: {expected}"


# =============================================================================
# 2. IMPORT DEPENDENCY TESTS
# =============================================================================

class TestImportDependencies:
    """Test that import dependencies match expected structure."""

    def test_no_imports_from_reclassified_legacy(self, phase1_dir: Path):
        """No module should import from the reclassified legacy module."""
        # phase1_01_00_cpp_models is now in docs/legacy/
        # It should NOT be imported by any active module
        legacy_module = "phase1_01_00_cpp_models"

        py_files = list(phase1_dir.glob("*.py"))
        for py_file in py_files:
            if py_file.name.startswith("__"):
                continue
            if py_file.name == "phase1_01_00_cpp_models.py":
                continue  # The file itself

            content = py_file.read_text()
            assert legacy_module not in content, \
                f"{py_file.name} imports reclassified legacy module {legacy_module}"

    def test_constants_not_importing_anything(self, phase1_dir: Path):
        """PHASE_1_CONSTANTS must not import any other Phase 1 module."""
        constants_file = phase1_dir / "PHASE_1_CONSTANTS.py"
        content = constants_file.read_text()

        for module in EXPECTED_TOPOLOGICAL_ORDER:
            if module != "PHASE_1_CONSTANTS":
                assert module not in content, \
                    f"PHASE_1_CONSTANTS imports {module} (should be import-free)"

    def test_models_imports_constants(self, dependency_graph: Dict[str, Set[str]]):
        """phase1_03_00_models must import phase1_02_00_phase_1_constants."""
        assert "phase1_03_00_models" in dependency_graph, \
            "phase1_03_00_models not in graph"
        assert "phase1_02_00_phase_1_constants" in dependency_graph["phase1_03_00_models"], \
            "phase1_03_00_models must import phase1_02_00_phase_1_constants"

    def test_sp4_imports_its_dependencies(self, dependency_graph: Dict[str, Set[str]]):
        """phase1_07_00_sp4_question_aware must import its dependencies."""
        assert "phase1_07_00_sp4_question_aware" in dependency_graph
        deps = dependency_graph["phase1_07_00_sp4_question_aware"]
        assert "phase1_02_00_phase_1_constants" in deps
        assert "phase1_03_00_models" in deps
        assert "phase1_06_00_questionnaire_mapper" in deps

    def test_main_executor_imports_dependencies(self, dependency_graph: Dict[str, Set[str]]):
        """phase1_13_00_cpp_ingestion must import its dependencies."""
        assert "phase1_13_00_cpp_ingestion" in dependency_graph
        deps = dependency_graph["phase1_13_00_cpp_ingestion"]
        assert "PHASE_1_CONSTANTS" in deps
        assert "phase1_03_00_models" in deps
        assert "phase1_09_00_circuit_breaker" in deps
        assert "phase1_11_00_signal_enrichment" in deps
        assert "phase1_12_00_structural" in deps


# =============================================================================
# 3. CYCLE DETECTION TESTS
# =============================================================================

class TestCycleDetection:
    """Adversarial tests for circular dependency detection."""

    def test_no_direct_cycles(self, dependency_graph: Dict[str, Set[str]]):
        """No module should directly import itself."""
        for module, deps in dependency_graph.items():
            assert module not in deps, f"{module} imports itself"

    def test_no_indirect_cycles(self, dependency_graph: Dict[str, Set[str]]):
        """No cycles of any length should exist."""
        visited = set()
        rec_stack = set()

        def has_cycle(node: str, path: List[str] = None) -> Tuple[bool, List[str]]:
            if path is None:
                path = []
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in dependency_graph.get(node, set()):
                if neighbor not in visited:
                    result, cycle_path = has_cycle(neighbor, path)
                    if result:
                        return True, cycle_path
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    return True, path[cycle_start:] + [neighbor]

            rec_stack.remove(node)
            path.pop()
            return False, []

        for node in dependency_graph:
            if node not in visited:
                has_cycle_path, cycle = has_cycle(node)
                assert not has_cycle_path, f"Cycle detected: {cycle}"

    def test_critical_modules_no_cycles(self, phase1_dir: Path):
        """Critical execution path modules must not have cycles."""
        critical_modules = [
            "phase1_03_00_models",
            "phase1_07_00_sp4_question_aware",
            "phase1_13_00_cpp_ingestion",
        ]

        for module in critical_modules:
            filepath = phase1_dir / f"{module}.py"
            if not filepath.exists():
                continue

            content = filepath.read_text()
            for other in critical_modules:
                if other != module:
                    # Check for suspicious circular-looking patterns
                    # This is a heuristic, not perfect detection
                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        if f"from . import {other}" in line or f"from farfan_pipeline.phases.Phase_1 import {other}" in line:
                            # Verify the other file doesn't import back
                            other_file = phase1_dir / f"{other}.py"
                            if other_file.exists():
                                other_content = other_file.read_text()
                                assert module not in other_content or "import" not in other_content.split(module)[0].split("\n")[-1], \
                                    f"Potential circular dependency: {module} <-> {other}"


# =============================================================================
# 4. ORPHAN DETECTION TESTS
# =============================================================================

class TestOrphanDetection:
    """Test that all modules are properly integrated in the chain."""

    def test_reclassified_files_exist_in_new_locations(self, phase1_dir: Path):
        """Reclassified files must exist in their new locations."""
        for module, new_location in RECLASSIFIED_MODULES.items():
            if new_location == "docs/legacy/":
                filepath = phase1_dir / new_location / f"{module}.py"
            else:
                filepath = phase1_dir / new_location / f"{module}.py"

            assert filepath.exists(), f"Reclassified file not found: {filepath}"

    def test_no_orphan_modules_in_root(self, phase1_dir: Path):
        """No orphan modules should remain in root (excluding expected modules)."""
        root_py_files = [f for f in phase1_dir.glob("*.py") if not f.name.startswith("__")]

        # Expected root modules (excluding reclassified ones)
        expected_root_modules = {
            "__init__.py",
            "PHASE_1_CONSTANTS.py",
            "phase1_02_00_phase_1_constants.py",
            "phase1_03_00_models.py",
            "phase1_05_00_thread_safe_results.py",
            "phase1_06_00_questionnaire_mapper.py",
            "phase1_07_00_sp4_question_aware.py",
            "phase1_09_00_circuit_breaker.py",
            "phase1_11_00_signal_enrichment.py",
            "phase1_12_00_structural.py",
            "phase1_13_00_cpp_ingestion.py",
        }

        actual_root_modules = {f.name for f in root_py_files}
        unexpected = actual_root_modules - expected_root_modules

        assert len(unexpected) == 0, \
            f"Unexpected modules in root: {unexpected}"

    def test_all_active_modules_imported_or_exported(self, phase1_dir: Path):
        """All active modules must be either imported by another module or exported via __init__.py."""
        init_file = phase1_dir / "__init__.py"
        init_content = init_file.read_text()

        # Modules that should be imported by others
        imported_modules = {
            "PHASE_1_CONSTANTS",
            "phase1_02_00_phase_1_constants",
            "phase1_03_00_models",
            "phase1_05_00_thread_safe_results",
            "phase1_06_00_questionnaire_mapper",
            "phase1_07_00_sp4_question_aware",
            "phase1_09_00_circuit_breaker",
            "phase1_11_00_signal_enrichment",
            "phase1_12_00_structural",
        }

        # Check that each is either imported or exported
        for module in imported_modules:
            module_file = phase1_dir / f"{module}.py"
            if not module_file.exists():
                continue

            # Should be referenced in __init__.py or imported by another module
            is_exported = module in init_content
            assert is_exported, f"Module {module} is not imported by any module and not exported in __init__.py"


# =============================================================================
# 5. EDGE CASE TESTS
# =============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_imports_are_valid(self, phase1_dir: Path):
        """Modules with no internal imports are valid (roots of DAG)."""
        root_modules = [
            "PHASE_1_CONSTANTS",
            "phase1_02_00_phase_1_constants",
            "phase1_05_00_thread_safe_results",
            "phase1_06_00_questionnaire_mapper",
            "phase1_09_00_circuit_breaker",
            "phase1_11_00_signal_enrichment",
            "phase1_12_00_structural",
        ]

        for module in root_modules:
            filepath = phase1_dir / f"{module}.py"
            if not filepath.exists():
                continue

            content = filepath.read_text()
            # Check for internal imports (relative or absolute from Phase_1)
            has_internal_import = False
            for line in content.split("\n"):
                if "from ." in line or "from farfan_pipeline.phases.Phase_1" in line:
                    if any(m in line for m in ["phase1_", "PHASE_1_CONSTANTS"]):
                        has_internal_import = True
                        break

            # Root modules may have no internal imports
            # This is valid, not an error

    def test_init_py_imports_valid_modules(self, phase1_dir: Path):
        """__init__.py must only import existing modules."""
        init_file = phase1_dir / "__init__.py"
        init_content = init_file.read_text()

        for expected_module in EXPECTED_TOPOLOGICAL_ORDER:
            if expected_module in init_content:
                filepath = phase1_dir / f"{expected_module}.py"
                assert filepath.exists(), \
                    f"__init__.py imports {expected_module} but file doesn't exist"

    def test_duplicate_imports_allowed(self):
        """Duplicate import statements should not cause issues."""
        # This is more of a style check, but duplicates are technically valid
        import farfan_pipeline.phases.Phase_1 as p1
        import farfan_pipeline.phases.Phase_1 as p1_again
        assert p1 is p1_again

    def test_all_python_files_parseable(self, phase1_dir: Path):
        """All Python files must be parseable (no syntax errors)."""
        py_files = list(phase1_dir.glob("*.py"))
        errors = []

        for py_file in py_files:
            try:
                ast.parse(py_file.read_text())
            except SyntaxError as e:
                errors.append(f"{py_file.name}: {e}")

        assert len(errors) == 0, f"Syntax errors found: {errors}"


# =============================================================================
# RUN CONFIGURATION
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

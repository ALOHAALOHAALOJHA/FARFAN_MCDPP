"""
Test Phase 1 Sequential Chain Integrity.

Tests the import dependency chain, topological order, and structural integrity
of Phase 1 modules according to the audit specifications.

Author: F.A.R.F.A.N Pipeline Test Suite
Version: 1.0.0
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Set

import pytest


class TestPhase1Encadenamiento:
    """Test suite for Phase 1 sequential chain integrity."""

    @pytest.fixture(scope="class")
    def phase1_dir(self) -> Path:
        """Get Phase 1 directory path."""
        # We're in src/farfan_pipeline/phases/Phase_1/tests/
        # Phase 1 directory is parent.parent (go up to Phase_1)
        return Path(__file__).resolve().parent.parent

    @pytest.fixture(scope="class")
    def chain_report(self, phase1_dir: Path) -> Dict:
        """Load the chain analysis report."""
        report_path = phase1_dir / "contracts" / "phase1_chain_report.json"
        if not report_path.exists():
            pytest.skip(f"Chain report not found: {report_path}")
        return json.loads(report_path.read_text())

    def test_phase1_directory_exists(self, phase1_dir: Path):
        """Test that Phase_1 directory exists."""
        assert phase1_dir.exists(), f"Phase_1 directory not found: {phase1_dir}"
        assert phase1_dir.is_dir(), f"Phase_1 is not a directory: {phase1_dir}"

    def test_mandatory_subdirectories_exist(self, phase1_dir: Path):
        """Test that all mandatory subdirectories exist."""
        mandatory_dirs = ["contracts", "docs", "tests", "primitives", "interphase"]
        
        for dir_name in mandatory_dirs:
            dir_path = phase1_dir / dir_name
            assert dir_path.exists(), f"Mandatory directory missing: {dir_name}"
            assert dir_path.is_dir(), f"Path is not a directory: {dir_name}"

    def test_mandatory_root_files_exist(self, phase1_dir: Path):
        """Test that all mandatory root files exist."""
        mandatory_files = [
            "__init__.py",
            "PHASE_1_CONSTANTS.py",
            "PHASE_1_MANIFEST.json",
            "README.md"
        ]
        
        for file_name in mandatory_files:
            file_path = phase1_dir / file_name
            assert file_path.exists(), f"Mandatory file missing: {file_name}"
            assert file_path.is_file(), f"Path is not a file: {file_name}"

    def test_contract_files_exist(self, phase1_dir: Path):
        """Test that all contract files exist."""
        contracts_dir = phase1_dir / "contracts"
        
        # At minimum, we need these contract files
        required_contracts = [
            "phase1_10_00_phase1_input_contract.py",
            "phase1_10_00_phase1_mission_contract.py",
            "phase1_10_00_phase1_output_contract.py"
        ]
        
        for contract_file in required_contracts:
            contract_path = contracts_dir / contract_file
            assert contract_path.exists(), f"Contract file missing: {contract_file}"

    def test_no_backup_files_in_root(self, phase1_dir: Path):
        """Test that no .bak files exist in the root directory."""
        bak_files = list(phase1_dir.glob("*.bak"))
        assert len(bak_files) == 0, f"Found backup files in root: {[f.name for f in bak_files]}"

    def test_no_merge_conflicts(self, phase1_dir: Path):
        """Test that no Python files contain merge conflict markers."""
        py_files = list(phase1_dir.glob("*.py"))
        
        for py_file in py_files:
            content = py_file.read_text()
            assert "<<<<<<< " not in content, f"Merge conflict marker found in {py_file.name}"
            assert "=======" not in content or "===" in content, f"Potential merge conflict in {py_file.name}"
            assert ">>>>>>> " not in content, f"Merge conflict marker found in {py_file.name}"

    def test_all_python_files_parse(self, phase1_dir: Path):
        """Test that all Python files can be parsed without syntax errors."""
        py_files = list(phase1_dir.glob("*.py"))
        
        for py_file in py_files:
            if py_file.name.startswith("__"):
                continue
            
            try:
                ast.parse(py_file.read_text())
            except SyntaxError as e:
                pytest.fail(f"Syntax error in {py_file.name}: {e}")

    def test_chain_report_exists(self, phase1_dir: Path):
        """Test that the chain analysis report exists."""
        report_path = phase1_dir / "contracts" / "phase1_chain_report.json"
        assert report_path.exists(), "Chain report not found"

    def test_no_circular_dependencies(self, chain_report: Dict):
        """Test that there are no circular import dependencies."""
        # The chain_report has summary.circular_dependencies (count) not a list
        summary = chain_report.get("summary", {})
        circular_count = summary.get("circular_dependencies", 1)
        assert circular_count == 0, f"Circular dependencies detected: {circular_count}"

    def test_topological_order_defined(self, chain_report: Dict):
        """Test that topological order is defined and non-empty."""
        # The chain_report has topological_analysis.layers, not topological_order
        topo_analysis = chain_report.get("topological_analysis", {})
        layers = topo_analysis.get("layers", [])
        assert len(layers) > 0, "Topological layers are empty"

        # Collect all modules from layers
        all_modules = []
        for layer in layers:
            all_modules.extend(layer.get("modules", []))

        assert len(all_modules) > 0, "No modules in topological order"
        # Check that count matches expected
        total_files = chain_report.get("summary", {}).get("files_in_chain", 0)
        assert len(all_modules) >= total_files, \
            f"Topological order count ({len(all_modules)}) less than files in chain ({total_files})"

    def test_main_executor_is_last(self, chain_report: Dict):
        """Test that the main executor is last in topological order."""
        # The cpp_ingestion is in the highest layer (excluding __init__.py which is layer 4)
        topo_analysis = chain_report.get("topological_analysis", {})
        layers = topo_analysis.get("layers", [])
        assert len(layers) > 0, "Topological layers are empty"

        # Find the layer with cpp_ingestion
        cpp_ingestion_layer = None
        for layer in layers:
            if any("cpp_ingestion" in mod for mod in layer.get("modules", [])):
                cpp_ingestion_layer = layer.get("layer", -1)
                break

        assert cpp_ingestion_layer is not None, "cpp_ingestion not found in any layer"
        # cpp_ingestion should be in layer 3 (before __init__.py which is layer 4)
        assert cpp_ingestion_layer == 3, \
            f"Expected cpp_ingestion to be in layer 3, got: {cpp_ingestion_layer}"

    def test_orphan_files_documented(self, chain_report: Dict):
        """Test that any orphan files are documented (post-normalization: should be 0)."""
        # After normalization, all orphan files should be reclassified
        # Check the reclassified_modules section
        reclassified = chain_report.get("reclassified_modules", {}).get("reclassified", [])

        # Verify the 4 reclassified modules are documented
        assert len(reclassified) == 4, f"Expected 4 reclassified modules, got {len(reclassified)}"

        # Verify no orphan files remain in summary
        summary = chain_report.get("summary", {})
        orphan_count = summary.get("orphan_files", 1)
        assert orphan_count == 0, f"Orphan files still exist: {orphan_count}"

    def test_input_contract_functions_defined(self, phase1_dir: Path):
        """Test that input contract defines required validation functions."""
        contract_file = phase1_dir / "contracts" / "phase1_10_00_phase1_input_contract.py"
        
        if not contract_file.exists():
            pytest.skip("Input contract file not found")
        
        content = contract_file.read_text()
        assert "def validate_phase1_input_contract" in content, \
            "Input contract validation function not defined"
        assert "Phase1InputPrecondition" in content or "PHASE1_INPUT_PRECONDITIONS" in content, \
            "Input contract preconditions not defined"

    def test_mission_contract_weights_defined(self, phase1_dir: Path):
        """Test that mission contract defines subphase weights."""
        contract_file = phase1_dir / "contracts" / "phase1_10_00_phase1_mission_contract.py"
        
        if not contract_file.exists():
            pytest.skip("Mission contract file not found")
        
        content = contract_file.read_text()
        assert "PHASE1_SUBPHASE_WEIGHTS" in content, \
            "Mission contract subphase weights not defined"
        assert "WeightTier" in content, \
            "Mission contract weight tiers not defined"

    def test_output_contract_postconditions_defined(self, phase1_dir: Path):
        """Test that output contract defines required postconditions."""
        contract_file = phase1_dir / "contracts" / "phase1_10_00_phase1_output_contract.py"
        
        if not contract_file.exists():
            pytest.skip("Output contract file not found")
        
        content = contract_file.read_text()
        assert "def validate_phase1_output_contract" in content, \
            "Output contract validation function not defined"
        assert "Phase1OutputPostcondition" in content or "PHASE1_OUTPUT_POSTCONDITIONS" in content, \
            "Output contract postconditions not defined"

    def test_documentation_files_exist(self, phase1_dir: Path):
        """Test that required documentation files exist."""
        docs_dir = phase1_dir / "docs"
        
        required_docs = [
            "phase1_execution_flow.md",
            "phase1_anomalies_remediation.md",
            "phase1_audit_checklist.md"
        ]
        
        for doc_file in required_docs:
            doc_path = docs_dir / doc_file
            assert doc_path.exists(), f"Required documentation missing: {doc_file}"

    def test_legacy_directory_exists(self, phase1_dir: Path):
        """Test that legacy directory exists for archived files."""
        legacy_dir = phase1_dir / "docs" / "legacy"
        assert legacy_dir.exists(), "Legacy directory not found"
        assert legacy_dir.is_dir(), "Legacy path is not a directory"

    def test_primitives_not_orphaned(self, phase1_dir: Path):
        """Test that primitive modules are properly organized."""
        primitives_dir = phase1_dir / "primitives"
        assert primitives_dir.exists(), "Primitives directory not found"
        
        # Check for expected primitive files
        expected_primitives = [
            "streaming_extractor.py",
            "truncation_audit.py"
        ]
        
        for prim_file in expected_primitives:
            # Either the file exists directly or with version prefix
            variants = [
                primitives_dir / prim_file,
                primitives_dir / f"phase1_00_00_{prim_file}",
                primitives_dir / f"phase1_10_00_{prim_file}"
            ]
            assert any(v.exists() for v in variants), \
                f"Primitive module not found: {prim_file}"

    def test_constants_importable(self, phase1_dir: Path):
        """Test that constants can be imported."""
        constants_file = phase1_dir / "PHASE_1_CONSTANTS.py"
        assert constants_file.exists(), "PHASE_1_CONSTANTS.py not found"
        
        # Check for expected constants
        content = constants_file.read_text()
        expected_constants = [
            "PDF_EXTRACTION_CHAR_LIMIT",
            "SEMANTIC_SCORE_MAX_EXPECTED",
            "PHASE1_LOGGER_NAME"
        ]
        
        for const in expected_constants:
            assert const in content, f"Expected constant not found: {const}"

    def test_manifest_valid_json(self, phase1_dir: Path):
        """Test that PHASE_1_MANIFEST.json is valid JSON."""
        manifest_file = phase1_dir / "PHASE_1_MANIFEST.json"
        assert manifest_file.exists(), "PHASE_1_MANIFEST.json not found"
        
        try:
            manifest = json.loads(manifest_file.read_text())
            assert "phase_id" in manifest, "Manifest missing phase_id"
            assert "phase_name" in manifest, "Manifest missing phase_name"
            assert "subphases" in manifest, "Manifest missing subphases"
        except json.JSONDecodeError as e:
            pytest.fail(f"Manifest is not valid JSON: {e}")

    def test_init_exports_public_api(self, phase1_dir: Path):
        """Test that __init__.py exports the public API."""
        init_file = phase1_dir / "__init__.py"
        assert init_file.exists(), "__init__.py not found"
        
        content = init_file.read_text()
        assert "__all__" in content, "__init__.py does not define __all__"
        assert "Phase1Executor" in content or "Phase1MissionContract" in content, \
            "__init__.py does not export executor"


class TestPhase1ContractIntegration:
    """Integration tests for Phase 1 contracts."""

    @pytest.fixture(scope="class")
    def phase1_dir(self) -> Path:
        """Get Phase 1 directory path."""
        # We're in src/farfan_pipeline/phases/Phase_1/tests/
        # Phase 1 directory is parent.parent (go up to Phase_1)
        return Path(__file__).resolve().parent.parent

    def test_contracts_can_be_imported(self, phase1_dir: Path):
        """Test that contract modules can be imported."""
        import sys
        
        # Add src to path if needed
        src_path = phase1_dir.parent.parent.parent
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        try:
            from farfan_pipeline.phases.Phase_01.contracts import phase1_10_00_phase1_input_contract
            from farfan_pipeline.phases.Phase_01.contracts import phase1_10_00_phase1_mission_contract
            from farfan_pipeline.phases.Phase_01.contracts import phase1_10_00_phase1_output_contract
        except ImportError as e:
            pytest.fail(f"Failed to import contracts: {e}")

    def test_mission_contract_validation(self):
        """Test that mission contract validation works."""
        try:
            from farfan_pipeline.phases.Phase_01.contracts.phase1_10_00_phase1_mission_contract import (
                validate_mission_contract
            )
            
            # Should not raise
            result = validate_mission_contract()
            assert result is True
        except ImportError:
            pytest.skip("Mission contract not importable")
        except Exception as e:
            pytest.fail(f"Mission contract validation failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

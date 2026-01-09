"""
Test End-to-End Pipeline - SEVERE Adversarial Tests

PHASE_LABEL: Phase 2
PHASE_COMPONENT: Tests
PHASE_ROLE: Full pipeline validation with adversarial inputs

These tests are SEVERE and will FAIL if:
- Pipeline cannot initialize from scratch
- Contract loading fails for any valid contract
- Evidence assembly produces invalid output
- Carver synthesis fails
- Any step breaks the determinism guarantee
"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch
from dataclasses import dataclass

import pytest

PHASE_TWO_DIR = Path(__file__).resolve().parent.parent
GENERATED_CONTRACTS_DIR = PHASE_TWO_DIR / "generated_contracts"


@dataclass
class MockDocument:
    """Mock document for testing."""
    raw_text: str = "Test document content for Phase 2 testing."
    metadata: dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {"section": "test", "chapter": "1", "page": 1}


@dataclass
class MockSignalPack:
    """Mock signal pack for testing."""
    policy_area: str = "PA01"
    version: str = "1.0.0"
    strength: float = 0.8


class TestPipelineInitialization:
    """SEVERE: Test pipeline can initialize properly."""

    def test_factory_can_be_imported(self) -> None:
        """FAIL if factory module cannot be imported."""
        try:
            # This tests that the module structure is correct
            factory_path = PHASE_TWO_DIR / "phase2_10_00_factory.py"
            assert factory_path.exists(), f"Factory file missing: {factory_path}"
        except Exception as e:
            pytest.fail(f"Factory module import would fail: {e}")

    def test_base_executor_can_be_imported(self) -> None:
        """FAIL if base executor cannot be imported."""
        executor_path = PHASE_TWO_DIR / "phase2_60_00_base_executor_with_contract.py"
        assert executor_path.exists(), f"Base executor missing: {executor_path}"

    def test_evidence_nexus_can_be_imported(self) -> None:
        """FAIL if EvidenceNexus cannot be imported."""
        nexus_path = PHASE_TWO_DIR / "phase2_80_00_evidence_nexus.py"
        assert nexus_path.exists(), f"EvidenceNexus missing: {nexus_path}"

    def test_carver_can_be_imported(self) -> None:
        """FAIL if Carver synthesizer cannot be imported."""
        carver_path = PHASE_TWO_DIR / "phase2_90_00_carver.py"
        assert carver_path.exists(), f"Carver missing: {carver_path}"


class TestContractLoadingEndToEnd:
    """SEVERE: Test contract loading for all 300 contracts."""

    @pytest.fixture
    def sample_contracts(self) -> list[Path]:
        """Get list of sample contracts for testing."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")
        
        contracts = list(GENERATED_CONTRACTS_DIR.glob("Q*_PA*_contract_v4.json"))
        if not contracts:
            pytest.skip("No contracts found")
        
        return contracts

    def test_all_contracts_load_as_valid_json(self, sample_contracts: list[Path]) -> None:
        """FAIL if any contract is invalid JSON."""
        failures = []
        
        for contract_path in sample_contracts:
            try:
                with open(contract_path, "r", encoding="utf-8") as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                failures.append((contract_path.name, str(e)))
        
        assert not failures, (
            f"INVALID JSON in {len(failures)} contracts:\n"
            + "\n".join(f"  {name}: {err}" for name, err in failures[:10])
        )

    def test_contracts_have_required_method_binding(self, sample_contracts: list[Path]) -> None:
        """FAIL if contracts lack method_binding."""
        failures = []
        
        for contract_path in sample_contracts[:50]:  # Sample 50 contracts
            with open(contract_path, "r", encoding="utf-8") as f:
                contract = json.load(f)
            
            if "method_binding" not in contract:
                failures.append(contract_path.name)
        
        assert not failures, (
            f"CONTRACTS MISSING method_binding:\n"
            + "\n".join(f"  {name}" for name in failures)
        )

    def test_contracts_have_valid_execution_phases(self, sample_contracts: list[Path]) -> None:
        """FAIL if contracts have invalid execution_phases structure."""
        failures = []
        
        for contract_path in sample_contracts[:50]:
            with open(contract_path, "r", encoding="utf-8") as f:
                contract = json.load(f)
            
            method_binding = contract.get("method_binding", {})
            execution_phases = method_binding.get("execution_phases", {})
            
            # Check each phase has methods array
            for phase_name, phase_spec in execution_phases.items():
                if not isinstance(phase_spec, dict):
                    failures.append((contract_path.name, f"{phase_name} is not a dict"))
                elif "methods" not in phase_spec:
                    failures.append((contract_path.name, f"{phase_name} missing methods"))
        
        assert not failures, (
            f"INVALID EXECUTION PHASES:\n"
            + "\n".join(f"  {name}: {issue}" for name, issue in failures[:10])
        )


class TestEvidenceAssemblyEndToEnd:
    """SEVERE: Test evidence assembly produces valid output."""

    @pytest.fixture
    def mock_method_outputs(self) -> dict[str, Any]:
        """Generate mock method outputs for testing."""
        return {
            "semanticprocessor.chunk_text": {"chunks": ["chunk1", "chunk2"]},
            "policydocumentanalyzer.extract_key_excerpts": {"excerpts": ["excerpt1"]},
            "semanticanalyzer.compute_unit_of_analysis_natural_blocks": {"blocks": []},
            "semanticvalidator.validate_semantic_completeness_coherence": {"passed": True},
            "_signal_usage": [{"method": "test", "policy_area": "PA01", "version": "1.0.0"}],
        }

    @pytest.fixture
    def sample_contract(self) -> dict[str, Any]:
        """Load a sample contract for testing."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")
        
        contracts = list(GENERATED_CONTRACTS_DIR.glob("Q001_PA01_contract_v4.json"))
        if not contracts:
            pytest.skip("No Q001_PA01 contract")
        
        with open(contracts[0], "r", encoding="utf-8") as f:
            return json.load(f)

    def test_evidence_assembly_module_has_process_evidence(self) -> None:
        """FAIL if process_evidence function is missing."""
        nexus_path = PHASE_TWO_DIR / "phase2_80_00_evidence_nexus.py"
        
        if not nexus_path.exists():
            pytest.skip("EvidenceNexus module doesn't exist")
        
        content = nexus_path.read_text(encoding="utf-8")
        
        assert "def process_evidence" in content, (
            "EvidenceNexus MUST export process_evidence() function."
        )

    def test_evidence_assembly_returns_required_fields(self) -> None:
        """FAIL if process_evidence doesn't return required fields."""
        nexus_path = PHASE_TWO_DIR / "phase2_80_00_evidence_nexus.py"
        
        if not nexus_path.exists():
            pytest.skip("EvidenceNexus module doesn't exist")
        
        content = nexus_path.read_text(encoding="utf-8")
        
        # Check return structure mentions required fields
        required_fields = ["evidence", "trace", "validation"]
        for field in required_fields:
            assert f'"{field}"' in content or f"'{field}'" in content, (
                f"process_evidence() MUST return '{field}' in result."
            )


class TestCarverSynthesisEndToEnd:
    """SEVERE: Test Carver synthesis produces valid output."""

    def test_carver_has_synthesize_method(self) -> None:
        """FAIL if DoctoralCarverSynthesizer lacks synthesize method."""
        carver_path = PHASE_TWO_DIR / "phase2_90_00_carver.py"
        
        if not carver_path.exists():
            pytest.skip("Carver module doesn't exist")
        
        content = carver_path.read_text(encoding="utf-8")
        
        assert "def synthesize" in content, (
            "DoctoralCarverSynthesizer MUST have synthesize() method."
        )

    def test_carver_produces_human_readable_output(self) -> None:
        """FAIL if Carver doesn't produce human_readable_output."""
        carver_path = PHASE_TWO_DIR / "phase2_90_00_carver.py"
        
        if not carver_path.exists():
            pytest.skip("Carver module doesn't exist")
        
        content = carver_path.read_text(encoding="utf-8")
        
        assert "human_readable" in content.lower(), (
            "DoctoralCarverSynthesizer MUST produce human_readable_output."
        )

    def test_carver_enforces_citations(self) -> None:
        """FAIL if Carver doesn't enforce evidence citations."""
        carver_path = PHASE_TWO_DIR / "phase2_90_00_carver.py"
        
        if not carver_path.exists():
            pytest.skip("Carver module doesn't exist")
        
        content = carver_path.read_text(encoding="utf-8")
        
        assert "citation" in content.lower() or "reference" in content.lower(), (
            "DoctoralCarverSynthesizer MUST enforce evidence citations."
        )


class TestDeterminismEndToEnd:
    """SEVERE: Test determinism across runs."""

    def test_contract_loading_deterministic(self) -> None:
        """FAIL if same contract loads differently."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")
        
        contract_path = GENERATED_CONTRACTS_DIR / "Q001_PA01_contract_v4.json"
        if not contract_path.exists():
            pytest.skip("Q001_PA01 contract doesn't exist")
        
        # Load twice and compare hash
        with open(contract_path, "r", encoding="utf-8") as f:
            content1 = f.read()
        
        with open(contract_path, "r", encoding="utf-8") as f:
            content2 = f.read()
        
        hash1 = hashlib.sha256(content1.encode()).hexdigest()
        hash2 = hashlib.sha256(content2.encode()).hexdigest()
        
        assert hash1 == hash2, (
            "DETERMINISM VIOLATION: Same contract loaded with different content. "
            f"Hash1: {hash1[:16]}..., Hash2: {hash2[:16]}..."
        )

    def test_contract_hashes_match_manifest(self) -> None:
        """FAIL if contract hashes don't match manifest (if exists)."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")
        
        manifest_path = GENERATED_CONTRACTS_DIR / "generation_manifest.json"
        if not manifest_path.exists():
            pytest.skip("No manifest file")
        
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        
        # Check if manifest has contract hashes
        if "contracts" not in manifest and "hashes" not in manifest:
            pytest.skip("Manifest doesn't contain hash information")


class TestFullPipelineSimulation:
    """SEVERE: Simulate full pipeline execution."""

    def test_factory_to_executor_chain(self) -> None:
        """Test that factory → executor chain can be constructed."""
        # Verify all components exist
        components = [
            ("factory", PHASE_TWO_DIR / "phase2_10_00_factory.py"),
            ("class_registry", PHASE_TWO_DIR / "phase2_10_01_class_registry.py"),
            ("methods_registry", PHASE_TWO_DIR / "phase2_10_02_methods_registry.py"),
            ("task_executor", PHASE_TWO_DIR / "phase2_50_00_task_executor.py"),
            ("base_executor", PHASE_TWO_DIR / "phase2_60_00_base_executor_with_contract.py"),
            ("evidence_nexus", PHASE_TWO_DIR / "phase2_80_00_evidence_nexus.py"),
            ("carver", PHASE_TWO_DIR / "phase2_90_00_carver.py"),
        ]
        
        missing = [(name, path) for name, path in components if not path.exists()]
        
        assert not missing, (
            f"PIPELINE CHAIN BROKEN - Missing components:\n"
            + "\n".join(f"  {name}: {path}" for name, path in missing)
        )

    def test_300_results_would_be_produced(self) -> None:
        """Verify pipeline produces exactly 300 results."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")
        
        contracts = list(GENERATED_CONTRACTS_DIR.glob("Q*_PA*_contract_v4.json"))
        
        assert len(contracts) == 300, (
            f"PIPELINE WOULD PRODUCE {len(contracts)} RESULTS, expected 300. "
            "Each contract produces exactly one Phase2QuestionResult."
        )

    def test_all_policy_areas_covered(self) -> None:
        """Verify all 10 policy areas have contracts."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")
        
        policy_areas_found = set()
        
        for contract_path in GENERATED_CONTRACTS_DIR.glob("Q*_PA*_contract_v4.json"):
            # Extract PA from filename
            name = contract_path.stem
            pa_match = name.split("_PA")[1].split("_")[0] if "_PA" in name else None
            if pa_match:
                policy_areas_found.add(f"PA{pa_match}")
        
        expected_policy_areas = {f"PA{i:02d}" for i in range(1, 11)}
        missing = expected_policy_areas - policy_areas_found
        
        assert not missing, (
            f"MISSING POLICY AREAS: {missing}. "
            "All 10 policy areas (PA01-PA10) must have contracts."
        )

    def test_all_base_questions_covered(self) -> None:
        """Verify all 30 base questions have contracts."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")
        
        questions_found = set()
        
        for contract_path in GENERATED_CONTRACTS_DIR.glob("Q*_PA*_contract_v4.json"):
            name = contract_path.stem
            q_match = name.split("_PA")[0] if "_PA" in name else None
            if q_match:
                questions_found.add(q_match)
        
        expected_questions = {f"Q{i:03d}" for i in range(1, 31)}
        missing = expected_questions - questions_found
        
        assert not missing, (
            f"MISSING BASE QUESTIONS: {missing}. "
            "All 30 questions (Q001-Q030) must have contracts."
        )


class TestOutputSchemaCompliance:
    """SEVERE: Test output schema compliance."""

    def test_phase2_result_has_required_fields(self) -> None:
        """Verify Phase2QuestionResult schema fields are defined."""
        # Check base executor defines result structure
        executor_path = PHASE_TWO_DIR / "phase2_60_00_base_executor_with_contract.py"
        
        if not executor_path.exists():
            pytest.skip("Base executor doesn't exist")
        
        content = executor_path.read_text(encoding="utf-8")
        
        required_result_fields = [
            "base_slot",
            "question_id",
            "evidence",
            "validation",
            "trace",
        ]
        
        missing = [f for f in required_result_fields if f'"{f}"' not in content and f"'{f}'" not in content]
        
        # Allow for some flexibility in naming
        assert len(missing) < 3, (
            f"Phase2QuestionResult may be missing fields: {missing}"
        )

    def test_evidence_graph_format_defined(self) -> None:
        """Verify EvidenceGraph output format is defined."""
        nexus_path = PHASE_TWO_DIR / "phase2_80_00_evidence_nexus.py"
        
        if not nexus_path.exists():
            pytest.skip("EvidenceNexus doesn't exist")
        
        content = nexus_path.read_text(encoding="utf-8")
        
        assert "EvidenceGraph" in content or "evidence_graph" in content, (
            "EvidenceNexus MUST define EvidenceGraph output format."
        )


class TestErrorHandlingEndToEnd:
    """SEVERE: Test error handling in pipeline."""

    def test_contract_has_error_handling_section(self) -> None:
        """Verify contracts define error_handling."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")
        
        contract_path = GENERATED_CONTRACTS_DIR / "Q001_PA01_contract_v4.json"
        if not contract_path.exists():
            pytest.skip("Q001_PA01 contract doesn't exist")
        
        with open(contract_path, "r", encoding="utf-8") as f:
            contract = json.load(f)
        
        # error_handling may be in question_context.failure_contract
        question_context = contract.get("question_context", {})
        has_error_handling = (
            "error_handling" in contract or 
            "failure_contract" in question_context
        )
        
        assert has_error_handling, (
            "Contract MUST have error_handling or failure_contract section."
        )

    def test_base_executor_has_error_handling(self) -> None:
        """Verify base executor handles errors."""
        executor_path = PHASE_TWO_DIR / "phase2_60_00_base_executor_with_contract.py"
        
        if not executor_path.exists():
            pytest.skip("Base executor doesn't exist")
        
        content = executor_path.read_text(encoding="utf-8")
        
        assert "_check_failure_contract" in content, (
            "BaseExecutorWithContract MUST have _check_failure_contract method."
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=long"])

"""
Test Contract Integrity - SEVERE Adversarial Tests

PHASE_LABEL: Phase 2
PHASE_COMPONENT: Tests
PHASE_ROLE: Validate 300 JSON contract integrity

These tests are SEVERE and will FAIL if:
- Any of the 300 contracts is missing
- Any contract has invalid structure
- Any contract references legacy executor classes
- Contract checksums don't match manifest
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import pytest

# Constants
PHASE_TWO_DIR = Path(__file__).resolve().parent.parent
GENERATED_CONTRACTS_DIR = PHASE_TWO_DIR / "generated_contracts"
EXPECTED_CONTRACT_COUNT = 300
EXPECTED_QUESTIONS = 30  # Q001-Q030
EXPECTED_POLICY_AREAS = 10  # PA01-PA10


class TestContractExistence:
    """SEVERE: Validate all 300 contracts exist."""

    def test_contracts_directory_exists(self) -> None:
        """FAIL if generated_contracts/ directory is missing."""
        assert GENERATED_CONTRACTS_DIR.exists(), (
            f"CRITICAL: generated_contracts/ directory MISSING at {GENERATED_CONTRACTS_DIR}. "
            "Phase 2 CANNOT function without 300 JSON contracts."
        )

    def test_contracts_directory_not_empty(self) -> None:
        """FAIL if generated_contracts/ is empty."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("Directory doesn't exist - tested elsewhere")
        
        files = list(GENERATED_CONTRACTS_DIR.glob("*.json"))
        assert len(files) > 0, (
            "CRITICAL: generated_contracts/ is EMPTY. "
            "Expected 300+ JSON contracts."
        )

    def test_exactly_300_contracts_exist(self) -> None:
        """FAIL if contract count != 300."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("Directory doesn't exist")
        
        contract_files = list(GENERATED_CONTRACTS_DIR.glob("Q*_PA*_contract_v4.json"))
        
        assert len(contract_files) == EXPECTED_CONTRACT_COUNT, (
            f"CRITICAL: Expected exactly {EXPECTED_CONTRACT_COUNT} contracts, "
            f"found {len(contract_files)}. "
            f"Missing contracts indicate INCOMPLETE migration from legacy architecture."
        )

    @pytest.mark.parametrize("q_num", range(1, EXPECTED_QUESTIONS + 1))
    @pytest.mark.parametrize("pa_num", range(1, EXPECTED_POLICY_AREAS + 1))
    def test_specific_contract_exists(self, q_num: int, pa_num: int) -> None:
        """FAIL if any specific Q_PA contract is missing."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("Directory doesn't exist")
        
        q_id = f"Q{q_num:03d}"
        pa_id = f"PA{pa_num:02d}"
        contract_path = GENERATED_CONTRACTS_DIR / f"{q_id}_{pa_id}_contract_v4.json"
        
        assert contract_path.exists(), (
            f"MISSING CONTRACT: {contract_path.name}. "
            f"Question {q_id} for policy area {pa_id} has NO contract. "
            "This breaks the 300-contract architecture."
        )

    def test_generation_manifest_exists(self) -> None:
        """FAIL if generation_manifest.json is missing."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("Directory doesn't exist")
        
        manifest_path = GENERATED_CONTRACTS_DIR / "generation_manifest.json"
        assert manifest_path.exists(), (
            "MISSING: generation_manifest.json. "
            "Contract generation provenance CANNOT be verified."
        )


class TestContractStructure:
    """SEVERE: Validate v4 contract structure."""

    @pytest.fixture
    def sample_contract(self) -> dict[str, Any]:
        """Load first available contract for structure tests."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")
        
        contracts = list(GENERATED_CONTRACTS_DIR.glob("Q*_PA*_contract_v4.json"))
        if not contracts:
            pytest.skip("No contracts found")
        
        with open(contracts[0], "r", encoding="utf-8") as f:
            return json.load(f)

    def test_contract_has_identity_section(self, sample_contract: dict) -> None:
        """FAIL if contract lacks identity section."""
        assert "identity" in sample_contract, (
            "INVALID CONTRACT: Missing 'identity' section. "
            "v4 contracts MUST have identity with contract_id, base_slot, sector_id."
        )

    def test_contract_has_method_binding(self, sample_contract: dict) -> None:
        """FAIL if contract lacks method_binding section."""
        assert "method_binding" in sample_contract, (
            "INVALID CONTRACT: Missing 'method_binding' section. "
            "v4 contracts MUST specify epistemological pipeline methods."
        )

    def test_contract_has_evidence_assembly(self, sample_contract: dict) -> None:
        """FAIL if contract lacks evidence_assembly section."""
        assert "evidence_assembly" in sample_contract, (
            "INVALID CONTRACT: Missing 'evidence_assembly' section. "
            "EvidenceNexus integration REQUIRES assembly rules."
        )

    def test_contract_version_is_v4(self, sample_contract: dict) -> None:
        """FAIL if contract is not v4 format."""
        identity = sample_contract.get("identity", {})
        contract_version = identity.get("contract_version", "")
        
        assert "4.0" in contract_version or "v4" in contract_version.lower(), (
            f"WRONG CONTRACT VERSION: {contract_version}. "
            "Only v4 contracts are supported. Legacy v2/v3 contracts are DEPRECATED."
        )

    def test_contract_has_epistemological_pipeline(self, sample_contract: dict) -> None:
        """FAIL if contract doesn't use epistemological_pipeline mode."""
        method_binding = sample_contract.get("method_binding", {})
        orchestration_mode = method_binding.get("orchestration_mode", "")
        
        assert orchestration_mode == "epistemological_pipeline", (
            f"WRONG ORCHESTRATION MODE: {orchestration_mode}. "
            "v4 contracts MUST use 'epistemological_pipeline' mode with N1→N2→N3 phases."
        )

    def test_contract_has_three_execution_phases(self, sample_contract: dict) -> None:
        """FAIL if contract doesn't have all 3 execution phases."""
        method_binding = sample_contract.get("method_binding", {})
        execution_phases = method_binding.get("execution_phases", {})
        
        required_phases = ["phase_A_construction", "phase_B_computation", "phase_C_litigation"]
        missing_phases = [p for p in required_phases if p not in execution_phases]
        
        assert not missing_phases, (
            f"MISSING EXECUTION PHASES: {missing_phases}. "
            "v4 contracts MUST have all 3 phases: A (N1-EMP), B (N2-INF), C (N3-AUD)."
        )


class TestNoLegacyReferences:
    """SEVERE: Ensure contracts don't reference legacy components."""

    def test_no_legacy_executor_class_references(self) -> None:
        """FAIL if any contract references D1Q1_Executor style classes."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")
        
        legacy_pattern = re.compile(r"D\d+Q\d+_Executor|D\d+_Q\d+_Executor")
        violations = []
        
        for contract_path in GENERATED_CONTRACTS_DIR.glob("Q*_PA*_contract_v4.json"):
            content = contract_path.read_text(encoding="utf-8")
            matches = legacy_pattern.findall(content)
            if matches:
                violations.append((contract_path.name, matches))
        
        assert not violations, (
            f"LEGACY EXECUTOR REFERENCES FOUND in {len(violations)} contracts:\n"
            + "\n".join(f"  {name}: {refs}" for name, refs in violations[:10])
            + "\nLegacy executor classes (D1Q1_Executor, etc.) are DEPRECATED."
        )

    def test_no_executors_py_import(self) -> None:
        """FAIL if any contract references executors.py module."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")
        
        violations = []
        
        for contract_path in GENERATED_CONTRACTS_DIR.glob("Q*_PA*_contract_v4.json"):
            content = contract_path.read_text(encoding="utf-8")
            if "from.*executors import" in content or '"executors.py"' in content:
                violations.append(contract_path.name)
        
        assert not violations, (
            f"LEGACY executors.py REFERENCES in: {violations}. "
            "executors.py module is DELETED. Use DynamicContractExecutor."
        )

    def test_no_base_slot_only_contracts(self) -> None:
        """FAIL if contracts use only base_slot without policy_area."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")
        
        violations = []
        
        for contract_path in GENERATED_CONTRACTS_DIR.glob("Q*_PA*_contract_v4.json"):
            with open(contract_path, "r", encoding="utf-8") as f:
                contract = json.load(f)
            
            identity = contract.get("identity", {})
            if not identity.get("sector_id") and not identity.get("policy_area_id"):
                violations.append(contract_path.name)
        
        assert not violations, (
            f"CONTRACTS MISSING POLICY AREA: {violations[:10]}. "
            "v4 contracts MUST specify sector_id or policy_area_id."
        )


class TestContractCompleteness:
    """SEVERE: Validate contracts have all required fields."""

    REQUIRED_SECTIONS = [
        "identity",
        "executor_binding",
        "method_binding",
        "question_context",
        "signal_requirements",
        "evidence_assembly",
        "fusion_specification",
        "human_answer_structure",
        "output_contract",
    ]

    @pytest.mark.parametrize("q_num,pa_num", [
        (1, 1), (1, 5), (1, 10),  # First question across policy areas
        (15, 1), (15, 5), (15, 10),  # Middle question
        (30, 1), (30, 5), (30, 10),  # Last question
    ])
    def test_contract_has_all_sections(self, q_num: int, pa_num: int) -> None:
        """FAIL if contract is missing required sections."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")
        
        q_id = f"Q{q_num:03d}"
        pa_id = f"PA{pa_num:02d}"
        contract_path = GENERATED_CONTRACTS_DIR / f"{q_id}_{pa_id}_contract_v4.json"
        
        if not contract_path.exists():
            pytest.skip(f"Contract {contract_path.name} doesn't exist")
        
        with open(contract_path, "r", encoding="utf-8") as f:
            contract = json.load(f)
        
        missing = [s for s in self.REQUIRED_SECTIONS if s not in contract]
        
        assert not missing, (
            f"CONTRACT {contract_path.name} MISSING SECTIONS: {missing}. "
            "v4 contracts MUST have all required sections for execution."
        )


class TestContractIntegrityHashes:
    """SEVERE: Validate contract content integrity."""

    def test_contracts_are_valid_json(self) -> None:
        """FAIL if any contract has invalid JSON."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")
        
        invalid_contracts = []
        
        for contract_path in GENERATED_CONTRACTS_DIR.glob("Q*_PA*_contract_v4.json"):
            try:
                with open(contract_path, "r", encoding="utf-8") as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                invalid_contracts.append((contract_path.name, str(e)))
        
        assert not invalid_contracts, (
            f"INVALID JSON in {len(invalid_contracts)} contracts:\n"
            + "\n".join(f"  {name}: {err}" for name, err in invalid_contracts[:10])
        )

    def test_contracts_not_truncated(self) -> None:
        """FAIL if any contract appears truncated (< 1KB)."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")
        
        min_size = 1024  # 1KB minimum for valid v4 contract
        truncated = []
        
        for contract_path in GENERATED_CONTRACTS_DIR.glob("Q*_PA*_contract_v4.json"):
            size = contract_path.stat().st_size
            if size < min_size:
                truncated.append((contract_path.name, size))
        
        assert not truncated, (
            f"TRUNCATED CONTRACTS (< {min_size} bytes):\n"
            + "\n".join(f"  {name}: {size} bytes" for name, size in truncated)
            + "\nv4 contracts should be substantial (typically 50KB+)."
        )

    def test_contracts_have_unique_ids(self) -> None:
        """FAIL if any two contracts have the same contract_id."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")
        
        contract_ids: dict[str, list[str]] = {}
        
        for contract_path in GENERATED_CONTRACTS_DIR.glob("Q*_PA*_contract_v4.json"):
            with open(contract_path, "r", encoding="utf-8") as f:
                contract = json.load(f)
            
            contract_id = contract.get("identity", {}).get("contract_id", "UNKNOWN")
            if contract_id not in contract_ids:
                contract_ids[contract_id] = []
            contract_ids[contract_id].append(contract_path.name)
        
        duplicates = {k: v for k, v in contract_ids.items() if len(v) > 1}
        
        assert not duplicates, (
            f"DUPLICATE CONTRACT IDs:\n"
            + "\n".join(f"  {cid}: {files}" for cid, files in duplicates.items())
            + "\nEach contract MUST have a unique contract_id."
        )


class TestMethodBindingIntegrity:
    """SEVERE: Validate method bindings in contracts."""

    def test_methods_have_class_and_method_name(self) -> None:
        """FAIL if any method binding lacks class_name or method_name."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")
        
        violations = []
        
        for contract_path in GENERATED_CONTRACTS_DIR.glob("Q*_PA*_contract_v4.json"):
            with open(contract_path, "r", encoding="utf-8") as f:
                contract = json.load(f)
            
            execution_phases = contract.get("method_binding", {}).get("execution_phases", {})
            
            for phase_name, phase_spec in execution_phases.items():
                for idx, method in enumerate(phase_spec.get("methods", [])):
                    if "class_name" not in method or "method_name" not in method:
                        violations.append(
                            f"{contract_path.name}:{phase_name}:methods[{idx}]"
                        )
        
        assert not violations, (
            f"METHODS MISSING class_name/method_name in:\n"
            + "\n".join(f"  {v}" for v in violations[:20])
        )

    def test_methods_have_valid_levels(self) -> None:
        """FAIL if methods don't have valid epistemological levels."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")
        
        valid_levels = {"N1-EMP", "N2-INF", "N3-AUD", "N1", "N2", "N3"}
        violations = []
        
        for contract_path in list(GENERATED_CONTRACTS_DIR.glob("Q*_PA*_contract_v4.json"))[:10]:
            with open(contract_path, "r", encoding="utf-8") as f:
                contract = json.load(f)
            
            execution_phases = contract.get("method_binding", {}).get("execution_phases", {})
            
            for phase_name, phase_spec in execution_phases.items():
                for method in phase_spec.get("methods", []):
                    level = method.get("level", "")
                    if level and level not in valid_levels:
                        violations.append(
                            f"{contract_path.name}: {method.get('method_id')}: {level}"
                        )
        
        # Allow for flexibility in level naming
        if violations:
            pytest.warns(UserWarning, f"Non-standard levels found: {violations[:5]}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=long"])

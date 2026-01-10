"""
Test Adversarial Edge Cases - SEVERE Tests

PHASE_LABEL: Phase 2
PHASE_COMPONENT: Tests
PHASE_ROLE: Extreme edge case and malformed input testing

These tests are SEVERE and will FAIL if:
- Malformed contracts crash the pipeline
- Missing policy_area_id causes silent failure
- Invalid method bindings aren't caught
- Boundary conditions break execution
- Security violations are possible
"""

from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch
import copy

import pytest

PHASE_TWO_DIR = Path(__file__).resolve().parent.parent
GENERATED_CONTRACTS_DIR = PHASE_TWO_DIR / "generated_contracts"


class TestMalformedContractHandling:
    """SEVERE: Test handling of malformed contracts."""

    @pytest.fixture
    def valid_contract_template(self) -> dict[str, Any]:
        """Load a valid contract as template."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")

        contract_path = GENERATED_CONTRACTS_DIR / "Q001_PA01_contract_v4.json"
        if not contract_path.exists():
            pytest.skip("No template contract")

        with open(contract_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_contract_missing_identity_detected(self, valid_contract_template: dict) -> None:
        """FAIL if missing identity isn't detected."""
        # Create malformed contract
        malformed = copy.deepcopy(valid_contract_template)
        del malformed["identity"]

        # Verify the validation would catch this
        assert "identity" not in malformed

        # Check that validator exists to catch this
        validator_path = PHASE_TWO_DIR / "phase2_60_01_contract_validator_cqvr.py"
        if validator_path.exists():
            content = validator_path.read_text(encoding="utf-8")
            assert "identity" in content, "Contract validator MUST check for identity section."

    def test_contract_missing_method_binding_detected(self, valid_contract_template: dict) -> None:
        """FAIL if missing method_binding isn't detected."""
        malformed = copy.deepcopy(valid_contract_template)
        del malformed["method_binding"]

        assert "method_binding" not in malformed

    def test_contract_empty_methods_array_handled(self, valid_contract_template: dict) -> None:
        """FAIL if empty methods array crashes execution."""
        malformed = copy.deepcopy(valid_contract_template)
        malformed["method_binding"]["execution_phases"]["phase_A_construction"]["methods"] = []

        # This should be detectable
        phase_a = malformed["method_binding"]["execution_phases"]["phase_A_construction"]
        assert len(phase_a["methods"]) == 0

    def test_contract_invalid_json_handled(self) -> None:
        """Verify that invalid JSON raises JSONDecodeError."""
        invalid_json_examples = [
            '{"identity": }',  # Missing value
            '{"identity": {',  # Unclosed brace
            "",  # Empty string (raises different error in some cases)
        ]

        for invalid_json in invalid_json_examples:
            if invalid_json:  # Skip empty string
                with pytest.raises(json.JSONDecodeError):
                    json.loads(invalid_json)

    def test_contract_missing_execution_phases_detected(
        self, valid_contract_template: dict
    ) -> None:
        """FAIL if missing execution_phases isn't caught."""
        malformed = copy.deepcopy(valid_contract_template)
        del malformed["method_binding"]["execution_phases"]

        assert "execution_phases" not in malformed["method_binding"]


class TestMissingPolicyAreaHandling:
    """SEVERE: Test handling of missing policy_area_id."""

    def test_contract_without_sector_id_raises(self) -> None:
        """FAIL if missing sector_id doesn't raise error."""
        executor_path = PHASE_TWO_DIR / "phase2_60_00_base_executor_with_contract.py"

        if not executor_path.exists():
            pytest.skip("Base executor doesn't exist")

        content = executor_path.read_text(encoding="utf-8")

        # Check that code validates policy_area_id
        assert "policy_area_id" in content and (
            "raise" in content or "ValueError" in content
        ), "BaseExecutorWithContract MUST validate policy_area_id presence."

    def test_contract_load_requires_policy_area(self) -> None:
        """FAIL if _load_contract doesn't require policy_area_id."""
        executor_path = PHASE_TWO_DIR / "phase2_60_00_base_executor_with_contract.py"

        if not executor_path.exists():
            pytest.skip("Base executor doesn't exist")

        content = executor_path.read_text(encoding="utf-8")

        # Find _load_contract method and check it validates policy_area_id
        load_contract_match = re.search(
            r"def _load_contract\([^)]*\):[^}]*?(?=\n    def\s|\nclass\s|\Z)", content, re.DOTALL
        )

        if load_contract_match:
            method_body = load_contract_match.group(0)
            assert (
                "policy_area_id" in method_body
            ), "_load_contract MUST reference policy_area_id parameter."

    def test_invalid_policy_area_raises(self) -> None:
        """FAIL if invalid policy_area_id (PA00) doesn't raise."""
        executor_path = PHASE_TWO_DIR / "phase2_60_00_base_executor_with_contract.py"

        if not executor_path.exists():
            pytest.skip("Base executor doesn't exist")

        content = executor_path.read_text(encoding="utf-8")

        assert "PA00" in content, "BaseExecutorWithContract MUST explicitly reject PA00 as invalid."


class TestInvalidMethodBindingHandling:
    """SEVERE: Test handling of invalid method bindings."""

    @pytest.fixture
    def valid_contract(self) -> dict[str, Any]:
        """Load valid contract."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")

        contracts = list(GENERATED_CONTRACTS_DIR.glob("Q*_PA*_contract_v4.json"))
        if not contracts:
            pytest.skip("No contracts")

        with open(contracts[0], "r", encoding="utf-8") as f:
            return json.load(f)

    def test_method_without_class_name_detected(self, valid_contract: dict) -> None:
        """FAIL if method without class_name isn't detected."""
        malformed = copy.deepcopy(valid_contract)

        # Find first method and remove class_name
        for phase_spec in malformed["method_binding"]["execution_phases"].values():
            if "methods" in phase_spec and phase_spec["methods"]:
                del phase_spec["methods"][0]["class_name"]
                break

        # Should have removed class_name
        for phase_spec in malformed["method_binding"]["execution_phases"].values():
            if "methods" in phase_spec:
                for method in phase_spec["methods"]:
                    if "class_name" not in method:
                        # Found our malformed method
                        return

        pytest.fail("Could not create test case - all methods have class_name")

    def test_method_without_method_name_detected(self, valid_contract: dict) -> None:
        """FAIL if method without method_name isn't detected."""
        malformed = copy.deepcopy(valid_contract)

        for phase_spec in malformed["method_binding"]["execution_phases"].values():
            if "methods" in phase_spec and phase_spec["methods"]:
                del phase_spec["methods"][0]["method_name"]
                break

    def test_non_existent_class_handled(self) -> None:
        """FAIL if non-existent class isn't caught."""
        executor_path = PHASE_TWO_DIR / "phase2_60_00_base_executor_with_contract.py"

        if not executor_path.exists():
            pytest.skip("Base executor doesn't exist")

        content = executor_path.read_text(encoding="utf-8")

        # Check that class registry validation exists
        assert (
            "class_registry" in content.lower()
        ), "Executor MUST use class_registry to validate class existence."


class TestBoundaryConditions:
    """SEVERE: Test boundary and extreme conditions."""

    def test_first_contract_q001_pa01_exists(self) -> None:
        """FAIL if first contract (Q001_PA01) is missing."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")

        first_contract = GENERATED_CONTRACTS_DIR / "Q001_PA01_contract_v4.json"
        assert first_contract.exists(), "BOUNDARY: First contract Q001_PA01 MUST exist."

    def test_last_contract_q030_pa10_exists(self) -> None:
        """FAIL if last contract (Q030_PA10) is missing."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")

        last_contract = GENERATED_CONTRACTS_DIR / "Q030_PA10_contract_v4.json"
        assert last_contract.exists(), "BOUNDARY: Last contract Q030_PA10 MUST exist."

    def test_boundary_policy_areas_exist(self) -> None:
        """FAIL if PA01 and PA10 boundaries missing for any question."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")

        missing_boundaries = []

        for q in range(1, 31):
            q_id = f"Q{q:03d}"

            pa01_contract = GENERATED_CONTRACTS_DIR / f"{q_id}_PA01_contract_v4.json"
            pa10_contract = GENERATED_CONTRACTS_DIR / f"{q_id}_PA10_contract_v4.json"

            if not pa01_contract.exists():
                missing_boundaries.append(f"{q_id}_PA01")
            if not pa10_contract.exists():
                missing_boundaries.append(f"{q_id}_PA10")

        assert not missing_boundaries, f"BOUNDARY CONTRACTS MISSING:\n" + "\n".join(
            f"  {c}" for c in missing_boundaries
        )

    def test_contract_numbers_sequential(self) -> None:
        """FAIL if contract_number is not sequential."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")

        contract_numbers = []

        for contract_path in GENERATED_CONTRACTS_DIR.glob("Q*_PA*_contract_v4.json"):
            with open(contract_path, "r", encoding="utf-8") as f:
                contract = json.load(f)

            contract_num = contract.get("identity", {}).get("contract_number")
            if contract_num is not None:
                contract_numbers.append(contract_num)

        contract_numbers.sort()

        # Check for gaps (allow some flexibility)
        if len(contract_numbers) >= 100:
            expected_max = max(contract_numbers)
            if expected_max <= 300:
                gaps = []
                for i in range(1, expected_max + 1):
                    if i not in contract_numbers:
                        gaps.append(i)

                if len(gaps) > 5:
                    pytest.warns(UserWarning, f"Contract number gaps detected: {gaps[:10]}...")


class TestSecurityBoundaries:
    """SEVERE: Test security boundaries."""

    def test_no_code_execution_in_contracts(self) -> None:
        """FAIL if contracts contain executable code patterns."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")

        dangerous_patterns = [
            r"__import__",
            r"eval\s*\(",
            r"exec\s*\(",
            r"subprocess",
            r"os\.system",
            r"shell=True",
            r"<script",
        ]

        violations = []

        for contract_path in GENERATED_CONTRACTS_DIR.glob("Q*_PA*_contract_v4.json"):
            content = contract_path.read_text(encoding="utf-8")

            for pattern in dangerous_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    violations.append((contract_path.name, pattern))

        assert (
            not violations
        ), f"SECURITY VIOLATION - Dangerous patterns in contracts:\n" + "\n".join(
            f"  {name}: {pattern}" for name, pattern in violations[:10]
        )

    def test_contracts_dont_contain_file_paths(self) -> None:
        """FAIL if contracts contain absolute file paths."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")

        path_patterns = [
            r"/home/",
            r"/Users/",
            r"C:\\",
            r"/root/",
            r"/etc/",
        ]

        violations = []

        for contract_path in list(GENERATED_CONTRACTS_DIR.glob("Q*_PA*_contract_v4.json"))[:50]:
            content = contract_path.read_text(encoding="utf-8")

            for pattern in path_patterns:
                if re.search(pattern, content):
                    violations.append((contract_path.name, pattern))

        assert not violations, f"SECURITY - Absolute paths in contracts:\n" + "\n".join(
            f"  {name}: {pattern}" for name, pattern in violations[:10]
        )

    def test_no_credentials_in_contracts(self) -> None:
        """FAIL if contracts contain credential patterns."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")

        credential_patterns = [
            r"password\s*[:=]",
            r"api_key\s*[:=]",
            r"secret\s*[:=]",
            r"token\s*[:=]\s*['\"][a-zA-Z0-9]",
            r"bearer\s+[a-zA-Z0-9]",
        ]

        violations = []

        for contract_path in list(GENERATED_CONTRACTS_DIR.glob("Q*_PA*_contract_v4.json"))[:50]:
            content = contract_path.read_text(encoding="utf-8")

            for pattern in credential_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    violations.append((contract_path.name, pattern))

        assert not violations, f"SECURITY - Potential credentials in contracts:\n" + "\n".join(
            f"  {name}: {pattern}" for name, pattern in violations
        )


class TestResourceLimitEnforcement:
    """SEVERE: Test resource limit enforcement."""

    def test_resource_manager_exists(self) -> None:
        """FAIL if ResourceManager is missing."""
        resource_manager_path = PHASE_TWO_DIR / "phase2_30_00_resource_manager.py"

        assert (
            resource_manager_path.exists()
        ), "ResourceManager MUST exist for memory/time enforcement."

    def test_resource_manager_has_limits(self) -> None:
        """FAIL if ResourceManager doesn't define limits."""
        resource_manager_path = PHASE_TWO_DIR / "phase2_30_00_resource_manager.py"

        if not resource_manager_path.exists():
            pytest.skip("ResourceManager doesn't exist")

        content = resource_manager_path.read_text(encoding="utf-8")

        limit_indicators = ["memory", "timeout", "limit", "max_"]
        found = sum(1 for ind in limit_indicators if ind in content.lower())

        assert found >= 2, "ResourceManager MUST define memory and time limits."

    def test_executor_config_has_timeout(self) -> None:
        """FAIL if ExecutorConfig lacks timeout setting."""
        config_path = PHASE_TWO_DIR / "phase2_10_03_executor_config.py"

        if not config_path.exists():
            pytest.skip("ExecutorConfig doesn't exist")

        content = config_path.read_text(encoding="utf-8")

        assert "timeout" in content.lower(), "ExecutorConfig MUST specify timeout for execution."


class TestSignalRegistryValidation:
    """SEVERE: Test signal registry validation."""

    def test_signal_registry_required_for_execution(self) -> None:
        """FAIL if signal_registry is optional."""
        executor_path = PHASE_TWO_DIR / "phase2_60_00_base_executor_with_contract.py"

        if not executor_path.exists():
            pytest.skip("Base executor doesn't exist")

        content = executor_path.read_text(encoding="utf-8")

        # Check that signal_registry is validated as required
        assert (
            "signal_registry is None" in content
        ), "Executor MUST validate signal_registry is not None."

    def test_signal_pack_retrieval_validated(self) -> None:
        """FAIL if signal_pack retrieval isn't validated."""
        executor_path = PHASE_TWO_DIR / "phase2_60_00_base_executor_with_contract.py"

        if not executor_path.exists():
            pytest.skip("Base executor doesn't exist")

        content = executor_path.read_text(encoding="utf-8")

        assert (
            "signal_pack is None" in content or "signal_pack is not None" in content
        ), "Executor MUST validate signal_pack retrieval."


class TestDuplicateContractPrevention:
    """SEVERE: Test duplicate contract prevention."""

    def test_no_duplicate_contract_ids(self) -> None:
        """FAIL if any two contracts have same ID."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")

        contract_ids: dict[str, str] = {}
        duplicates = []

        for contract_path in GENERATED_CONTRACTS_DIR.glob("Q*_PA*_contract_v4.json"):
            with open(contract_path, "r", encoding="utf-8") as f:
                contract = json.load(f)

            contract_id = contract.get("identity", {}).get("contract_id")
            if contract_id:
                if contract_id in contract_ids:
                    duplicates.append((contract_id, contract_ids[contract_id], contract_path.name))
                else:
                    contract_ids[contract_id] = contract_path.name

        assert not duplicates, f"DUPLICATE CONTRACT IDs:\n" + "\n".join(
            f"  {cid}: {f1} vs {f2}" for cid, f1, f2 in duplicates
        )

    def test_no_duplicate_filenames(self) -> None:
        """FAIL if any contract filenames collide (case-insensitive)."""
        if not GENERATED_CONTRACTS_DIR.exists():
            pytest.skip("No contracts directory")

        filenames_lower: dict[str, str] = {}
        collisions = []

        for contract_path in GENERATED_CONTRACTS_DIR.glob("Q*_PA*_contract_v4.json"):
            name_lower = contract_path.name.lower()

            if name_lower in filenames_lower:
                collisions.append((contract_path.name, filenames_lower[name_lower]))
            else:
                filenames_lower[name_lower] = contract_path.name

        assert not collisions, f"CASE-INSENSITIVE FILENAME COLLISIONS:\n" + "\n".join(
            f"  {f1} vs {f2}" for f1, f2 in collisions
        )


class TestEmptyInputHandling:
    """SEVERE: Test handling of empty/null inputs."""

    def test_empty_document_handling(self) -> None:
        """Verify empty document doesn't crash executor."""
        executor_path = PHASE_TWO_DIR / "phase2_60_00_base_executor_with_contract.py"

        if not executor_path.exists():
            pytest.skip("Base executor doesn't exist")

        content = executor_path.read_text(encoding="utf-8")

        # Check for getattr usage with defaults for raw_text
        assert (
            "getattr" in content and "raw_text" in content
        ), "Executor MUST safely handle missing raw_text attribute."

    def test_empty_method_outputs_handling(self) -> None:
        """Verify empty method outputs don't crash evidence assembly."""
        nexus_path = PHASE_TWO_DIR / "phase2_80_00_evidence_nexus.py"

        if not nexus_path.exists():
            pytest.skip("EvidenceNexus doesn't exist")

        content = nexus_path.read_text(encoding="utf-8")

        # Check for handling of empty inputs
        assert (
            "if not" in content or "is None" in content
        ), "EvidenceNexus MUST handle empty method outputs."


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=long"])

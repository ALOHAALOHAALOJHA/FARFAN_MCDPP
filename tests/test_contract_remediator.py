"""
Tests for Automated Contract Remediator
"""

import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.contract_remediator import (
    ContractBackupManager,
    ContractDiffGenerator,
    ContractRemediator,
    RemediationStrategy,
)


@pytest.fixture
def temp_backup_dir(tmp_path):
    """Create temporary backup directory."""
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    return backup_dir


@pytest.fixture
def sample_contract():
    """Sample contract for testing."""
    return {
        "identity": {
            "base_slot": "D1-Q1",
            "question_id": "Q001",
            "dimension_id": "DIM01",
            "policy_area_id": "PA01",
            "contract_version": "3.0.0",
            "question_global": 1,
        },
        "method_binding": {
            "orchestration_mode": "multi_method_pipeline",
            "method_count": 3,
            "methods": [
                {"class_name": "MethodA", "provides": "method_a.output"},
                {"class_name": "MethodB", "provides": "method_b.output"},
                {"class_name": "MethodC", "provides": "method_c.output"},
            ],
        },
        "output_contract": {
            "schema": {
                "properties": {
                    "question_id": {"const": "Q001"},
                    "policy_area_id": {"const": "PA01"},
                    "dimension_id": {"const": "DIM01"},
                    "question_global": {"const": 1},
                    "base_slot": {"const": "D1-Q1"},
                },
                "required": ["question_id", "policy_area_id"],
            }
        },
        "signal_requirements": {
            "mandatory_signals": ["signal_1", "signal_2"],
            "minimum_signal_threshold": 0.5,
            "signal_aggregation": "weighted_mean",
        },
        "evidence_assembly": {
            "assembly_rules": [
                {
                    "sources": ["method_a.output", "method_b.output", "method_c.output"]
                }
            ]
        },
        "question_context": {
            "patterns": [],
            "expected_elements": [],
        },
        "validation_rules": {
            "rules": [
                {
                    "must_contain": {"elements": []},
                    "should_contain": [],
                }
            ]
        },
        "traceability": {"source_hash": "TODO_COMPUTE_HASH"},
        "error_handling": {
            "failure_contract": {"emit_code": "FAIL_001"}
        },
    }


@pytest.fixture
def sample_monolith():
    """Sample questionnaire monolith."""
    return {
        "blocks": {
            "micro_questions": [
                {
                    "question_id": "Q001",
                    "base_slot": "D1-Q1",
                    "patterns": [
                        {"id": "PAT-001", "category": "TEST", "confidence_weight": 0.8}
                    ],
                    "expected_elements": [
                        {"type": "element1", "required": True}
                    ],
                    "method_sets": [],
                }
            ]
        }
    }


class TestContractBackupManager:
    """Test backup management functionality."""

    def test_backup_contract(self, temp_backup_dir, tmp_path):
        """Test creating contract backup."""
        manager = ContractBackupManager(temp_backup_dir)

        contract_path = tmp_path / "Q001.v3.json"
        contract_path.write_text('{"test": "data"}')

        backup_path = manager.backup_contract(contract_path)

        assert backup_path.exists()
        assert "Q001" in backup_path.name and "backup" in backup_path.name
        assert backup_path.suffix == ".json"
        assert backup_path.read_text() == '{"test": "data"}'

    def test_list_backups(self, temp_backup_dir, tmp_path):
        """Test listing backups for a contract."""
        import time
        
        manager = ContractBackupManager(temp_backup_dir)

        contract_path = tmp_path / "Q001.v3.json"
        contract_path.write_text('{"test": "data"}')

        manager.backup_contract(contract_path)
        time.sleep(1.1)  # Ensure different timestamp
        manager.backup_contract(contract_path)

        backups = manager.list_backups("Q001.v3")
        assert len(backups) >= 1  # At least one backup was created

    def test_restore_backup(self, temp_backup_dir, tmp_path):
        """Test restoring from backup."""
        manager = ContractBackupManager(temp_backup_dir)

        original_path = tmp_path / "Q001.v3.json"
        original_path.write_text('{"original": "data"}')

        backup_path = manager.backup_contract(original_path)

        original_path.write_text('{"modified": "data"}')

        target_path = tmp_path / "Q001_restored.v3.json"
        manager.restore_backup(backup_path, target_path)

        assert target_path.read_text() == '{"original": "data"}'


class TestContractDiffGenerator:
    """Test diff generation functionality."""

    def test_generate_diff(self):
        """Test generating diff between contracts."""
        original = {"field1": "value1", "field2": "value2"}
        modified = {"field1": "value1_modified", "field2": "value2", "field3": "value3"}

        diff = ContractDiffGenerator.generate_diff(original, modified)

        assert "value1" in diff
        assert "value1_modified" in diff
        assert "field3" in diff

    def test_summarize_changes(self):
        """Test summarizing changes."""
        original = {
            "identity": {"question_id": "Q001", "version": "1.0"},
            "methods": ["A", "B"],
        }
        modified = {
            "identity": {"question_id": "Q001", "version": "2.0"},
            "methods": ["A", "B", "C"],
            "new_field": "value",
        }

        changes = ContractDiffGenerator.summarize_changes(original, modified)

        assert "identity.version" in changes["fields_modified"]
        assert "new_field" in changes["fields_added"]


class TestContractRemediator:
    """Test contract remediation logic."""

    def test_fix_identity_schema_mismatch(self, sample_contract):
        """Test fixing identity-schema mismatches."""
        contract = sample_contract.copy()
        contract["output_contract"]["schema"]["properties"]["question_id"]["const"] = "Q999"

        remediator = Mock()
        remediator._fix_identity_schema_mismatch = (
            ContractRemediator._fix_identity_schema_mismatch
        )

        fixed = remediator._fix_identity_schema_mismatch(remediator, contract)

        assert fixed is True
        assert (
            contract["output_contract"]["schema"]["properties"]["question_id"]["const"]
            == "Q001"
        )

    def test_fix_signal_threshold(self, sample_contract):
        """Test fixing signal threshold issues."""
        contract = sample_contract.copy()
        contract["signal_requirements"]["minimum_signal_threshold"] = 0.0

        remediator = Mock()
        remediator._fix_signal_threshold = ContractRemediator._fix_signal_threshold

        fixed = remediator._fix_signal_threshold(remediator, contract)

        assert fixed is True
        assert contract["signal_requirements"]["minimum_signal_threshold"] == 0.5

    def test_fix_output_schema_required(self, sample_contract):
        """Test fixing missing required fields in schema."""
        contract = sample_contract.copy()
        contract["output_contract"]["schema"]["required"] = [
            "question_id",
            "missing_field",
        ]

        remediator = Mock()
        remediator._fix_output_schema_required = (
            ContractRemediator._fix_output_schema_required
        )

        fixed = remediator._fix_output_schema_required(remediator, contract)

        assert fixed is True
        assert "missing_field" in contract["output_contract"]["schema"]["properties"]

    def test_fix_method_assembly_alignment(self, sample_contract):
        """Test fixing method assembly alignment."""
        contract = sample_contract.copy()
        contract["evidence_assembly"]["assembly_rules"][0]["sources"] = [
            "method_a.output",
            "nonexistent.output",
            "method_c.output",
        ]

        remediator = Mock()
        remediator._fix_method_assembly_alignment = (
            ContractRemediator._fix_method_assembly_alignment
        )

        fixed = remediator._fix_method_assembly_alignment(remediator, contract)

        assert fixed is True
        sources = contract["evidence_assembly"]["assembly_rules"][0]["sources"]
        assert "nonexistent.output" not in sources

    def test_update_metadata(self, sample_contract):
        """Test metadata update after remediation."""
        contract = sample_contract.copy()

        remediator = Mock()
        remediator._update_metadata = ContractRemediator._update_metadata

        remediator._update_metadata(remediator, contract, ["fix1", "fix2"])

        assert "updated_at" in contract["identity"]
        assert "remediation_log" in contract["traceability"]
        assert len(contract["traceability"]["remediation_log"]) == 1
        assert contract["traceability"]["remediation_log"][0]["fixes_applied"] == [
            "fix1",
            "fix2",
        ]

    def test_dry_run_no_writes(self, tmp_path, sample_contract, sample_monolith):
        """Test that dry-run mode doesn't write files."""
        # Create actual files for testing
        contracts_dir = tmp_path / "contracts"
        contracts_dir.mkdir()
        
        contract_path = contracts_dir / "Q001.v3.json"
        with open(contract_path, "w") as f:
            json.dump(sample_contract, f)
        
        monolith_path = tmp_path / "monolith.json"
        with open(monolith_path, "w") as f:
            json.dump(sample_monolith, f)
        
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()
        
        remediator = ContractRemediator(
            contracts_dir=contracts_dir,
            monolith_path=monolith_path,
            backup_dir=backup_dir,
            dry_run=True,
        )
        
        # Get original modification time
        original_mtime = contract_path.stat().st_mtime
        
        # Execute remediation in dry-run mode
        result = remediator.remediate_contract(contract_path, RemediationStrategy.AUTO)
        
        # Verify file was not modified
        new_mtime = contract_path.stat().st_mtime
        assert new_mtime == original_mtime
        
        # Verify no backup was created
        backups = list(backup_dir.glob("*.json"))
        assert len(backups) == 0


@pytest.mark.integration
class TestContractRemediatorIntegration:
    """Integration tests with real contracts."""

    def test_remediate_real_contract(self, tmp_path):
        """Test remediation with a real contract (if available)."""
        repo_root = Path(__file__).parent.parent
        contracts_dir = (
            repo_root
            / "src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized"
        )
        monolith_path = repo_root / "canonic_questionnaire_central/questionnaire_monolith.json"

        if not contracts_dir.exists() or not monolith_path.exists():
            pytest.skip("Real contracts not available")

        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()

        remediator = ContractRemediator(
            contracts_dir=contracts_dir,
            monolith_path=monolith_path,
            backup_dir=backup_dir,
            dry_run=True,
        )

        contract_path = contracts_dir / "Q001.v3.json"
        if not contract_path.exists():
            pytest.skip("Q001.v3.json not available")

        result = remediator.remediate_contract(contract_path, RemediationStrategy.AUTO)

        assert result.original_score >= 0
        assert result.new_score >= 0
        assert result.contract_path == contract_path

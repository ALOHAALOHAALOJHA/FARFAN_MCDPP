"""
Test TC - Traceability Contract
Verifies: Merkle Tree root proves execution path
Audit trail validation guarantee
"""
import pytest
from pathlib import Path
from typing import Any

from cross_cutting_infrastructure.contractual.dura_lex.traceability import (
    TraceabilityContract,
    MerkleTree,
)


class TestTraceabilityContract:
    """TC: Cryptographic proof of execution via Merkle Tree."""

    @pytest.fixture
    def execution_steps(self) -> list[str]:
        """Phase 2 execution trace steps."""
        return [
            "phase2_start:1702339200",
            "load_contract:Q001.v3.json",
            "inject_signals:PA01",
            "execute_method:TextMiningEngine.diagnose_critical_links",
            "execute_method:IndustrialPolicyProcessor.process",
            "assemble_evidence:merge_concat",
            "validate_evidence:expected_elements",
            "phase2_end:1702339205",
        ]

    def test_tc_001_merkle_tree_construction(
        self, execution_steps: list[str]
    ) -> None:
        """TC-001: Merkle tree builds valid root."""
        tree = MerkleTree(execution_steps)
        assert tree.root
        assert len(tree.root) == 128  # Blake2b hex digest

    def test_tc_002_deterministic_root(
        self, execution_steps: list[str]
    ) -> None:
        """TC-002: Same steps produce identical root."""
        tree1 = MerkleTree(execution_steps)
        tree2 = MerkleTree(execution_steps)
        assert tree1.root == tree2.root

    def test_tc_003_verify_trace_valid(
        self, execution_steps: list[str]
    ) -> None:
        """TC-003: Valid trace verifies against its root."""
        tree = MerkleTree(execution_steps)
        assert TraceabilityContract.verify_trace(execution_steps, tree.root)

    def test_tc_004_verify_trace_invalid_root(
        self, execution_steps: list[str]
    ) -> None:
        """TC-004: Trace fails verification with wrong root."""
        invalid_root = "a" * 128  # Fake root
        assert not TraceabilityContract.verify_trace(execution_steps, invalid_root)

    def test_tc_005_tampered_step_fails(
        self, execution_steps: list[str]
    ) -> None:
        """TC-005: Tampered step produces different root."""
        tree_original = MerkleTree(execution_steps)

        tampered_steps = execution_steps.copy()
        tampered_steps[3] = "execute_method:TAMPERED_METHOD"

        tree_tampered = MerkleTree(tampered_steps)

        assert tree_original.root != tree_tampered.root
        assert not TraceabilityContract.verify_trace(
            tampered_steps, tree_original.root
        )

    def test_tc_006_order_matters(
        self, execution_steps: list[str]
    ) -> None:
        """TC-006: Different order produces different root."""
        tree_original = MerkleTree(execution_steps)

        reordered_steps = execution_steps.copy()
        reordered_steps[2], reordered_steps[3] = reordered_steps[3], reordered_steps[2]

        tree_reordered = MerkleTree(reordered_steps)

        assert tree_original.root != tree_reordered.root

    def test_tc_007_empty_trace(self) -> None:
        """TC-007: Empty trace has empty root."""
        tree = MerkleTree([])
        assert tree.root == ""

    def test_tc_008_single_step_trace(self) -> None:
        """TC-008: Single step produces valid root."""
        single = ["phase2_start:1702339200"]
        tree = MerkleTree(single)
        assert tree.root
        assert TraceabilityContract.verify_trace(single, tree.root)

    def test_tc_009_phase2_full_trace(self) -> None:
        """TC-009: Full Phase 2 execution trace is traceable."""
        full_trace = [
            "pipeline_init:session_abc123",
            "phase2_orchestrator_start",
            "load_questionnaire_monolith:sha256_monolith",
            "warmup_signal_registry:10_policy_areas",
        ]
        # Add 300 question executions
        for i in range(1, 301):
            full_trace.append(f"execute_question:Q{i:03d}")

        full_trace.extend([
            "aggregate_evidence:300_results",
            "validate_chain_integrity:pass",
            "phase2_complete",
        ])

        tree = MerkleTree(full_trace)
        assert TraceabilityContract.verify_trace(full_trace, tree.root)

    def test_tc_010_merkle_leaves_correct(
        self, execution_steps: list[str]
    ) -> None:
        """TC-010: Merkle tree has correct number of leaves."""
        tree = MerkleTree(execution_steps)
        assert len(tree.leaves) == len(execution_steps)

    def test_tc_011_forensic_verification(self) -> None:
        """TC-011: Forensic verification detects any modification."""
        original_trace = [
            "evidence_extract:E001",
            "evidence_extract:E002",
            "evidence_validate:pass",
        ]
        tree = MerkleTree(original_trace)
        original_root = tree.root

        # Simulate forensic audit
        assert TraceabilityContract.verify_trace(original_trace, original_root)

        # Attempt to inject evidence
        injected_trace = original_trace + ["evidence_extract:INJECTED"]
        assert not TraceabilityContract.verify_trace(injected_trace, original_root)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

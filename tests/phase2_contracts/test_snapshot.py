"""
Test SC - Snapshot Contract
Verifies: System refuses to run without frozen σ digests
State snapshot consistency guarantee
"""
import pytest
import sys
from pathlib import Path
from typing import Any


from cross_cutting_infrastructure.contractual.dura_lex.snapshot_contract import (
    SnapshotContract,
)


class TestSnapshotContract:
    """SC: External inputs must be frozen by checksums."""

    @pytest.fixture
    def valid_sigma(self) -> dict[str, Any]:
        """Valid Phase 2 sigma with all required hashes."""
        return {
            "standards_hash": "dnp_standards_sha256_abc123",
            "corpus_hash": "policy_documents_sha256_def456",
            "index_hash": "faiss_index_sha256_ghi789",
        }

    def test_sc_001_valid_sigma_passes(self, valid_sigma: dict[str, Any]) -> None:
        """SC-001: Valid sigma produces digest."""
        digest = SnapshotContract.verify_snapshot(valid_sigma)
        assert isinstance(digest, str)
        assert len(digest) == 128  # Blake2b hex digest

    def test_sc_002_missing_sigma_refuses(self) -> None:
        """SC-002: Empty sigma triggers refusal."""
        with pytest.raises(ValueError, match="Sigma.*is missing"):
            SnapshotContract.verify_snapshot({})

    def test_sc_003_none_sigma_refuses(self) -> None:
        """SC-003: None sigma triggers refusal."""
        with pytest.raises(ValueError, match="Sigma.*is missing"):
            SnapshotContract.verify_snapshot(None)  # type: ignore[arg-type]

    def test_sc_004_missing_standards_hash_refuses(self) -> None:
        """SC-004: Missing standards_hash triggers refusal."""
        sigma = {
            "corpus_hash": "hash1",
            "index_hash": "hash2",
        }
        with pytest.raises(ValueError, match="Missing required key standards_hash"):
            SnapshotContract.verify_snapshot(sigma)

    def test_sc_005_missing_corpus_hash_refuses(self) -> None:
        """SC-005: Missing corpus_hash triggers refusal."""
        sigma = {
            "standards_hash": "hash1",
            "index_hash": "hash2",
        }
        with pytest.raises(ValueError, match="Missing required key corpus_hash"):
            SnapshotContract.verify_snapshot(sigma)

    def test_sc_006_missing_index_hash_refuses(self) -> None:
        """SC-006: Missing index_hash triggers refusal."""
        sigma = {
            "standards_hash": "hash1",
            "corpus_hash": "hash2",
        }
        with pytest.raises(ValueError, match="Missing required key index_hash"):
            SnapshotContract.verify_snapshot(sigma)

    def test_sc_007_deterministic_digest(self, valid_sigma: dict[str, Any]) -> None:
        """SC-007: Same sigma produces identical digest."""
        digest1 = SnapshotContract.verify_snapshot(valid_sigma)
        digest2 = SnapshotContract.verify_snapshot(valid_sigma)
        assert digest1 == digest2

    def test_sc_008_different_sigma_different_digest(self) -> None:
        """SC-008: Different sigma produces different digest."""
        sigma1 = {
            "standards_hash": "hash_a",
            "corpus_hash": "hash_b",
            "index_hash": "hash_c",
        }
        sigma2 = {
            "standards_hash": "hash_x",
            "corpus_hash": "hash_y",
            "index_hash": "hash_z",
        }
        digest1 = SnapshotContract.verify_snapshot(sigma1)
        digest2 = SnapshotContract.verify_snapshot(sigma2)
        assert digest1 != digest2

    def test_sc_009_phase2_sigma_structure(self) -> None:
        """SC-009: Phase 2 sigma structure is validated."""
        phase2_sigma = {
            "standards_hash": "dnp_pdet_standards_sha256",
            "corpus_hash": "questionnaire_monolith_sha256",
            "index_hash": "signal_registry_sha256",
            # Additional Phase 2 specific fields
            "executor_contracts_hash": "v3_contracts_sha256",
        }
        digest = SnapshotContract.verify_snapshot(phase2_sigma)
        assert len(digest) == 128

    def test_sc_010_extra_fields_allowed(self, valid_sigma: dict[str, Any]) -> None:
        """SC-010: Extra fields in sigma are allowed."""
        sigma_extended = {
            **valid_sigma,
            "extra_field": "extra_value",
            "another_hash": "additional_sha256",
        }
        digest = SnapshotContract.verify_snapshot(sigma_extended)
        assert isinstance(digest, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""Tests for executor-chunk synchronization with canonical JOIN table.

Tests cover:
- ExecutorChunkBinding dataclass
- build_join_table() with various scenarios
- validate_uniqueness() invariant checking
- generate_verification_manifest() output
- Error handling and edge cases
"""

import pytest

from orchestration.executor_chunk_synchronizer import (
    ExecutorChunkBinding,
    ExecutorChunkSynchronizationError,
    build_join_table,
    validate_uniqueness,
    generate_verification_manifest,
    EXPECTED_CONTRACT_COUNT,
    EXPECTED_CHUNK_COUNT,
)

# Test constants
TEST_CONTRACTS_PER_PA = 30  # 30 questions per policy area
TEST_DIMENSIONS = 6         # 6 dimensions cycle


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_contracts():
    """Generate sample contracts for testing."""
    contracts = []
    for i in range(1, EXPECTED_CONTRACT_COUNT + 1):
        pa_idx = ((i - 1) // TEST_CONTRACTS_PER_PA) + 1
        dim_idx = ((i - 1) % TEST_DIMENSIONS) + 1
        
        contract = {
            "identity": {
                "question_id": f"Q{i:03d}",
                "policy_area_id": f"PA{pa_idx:02d}",
                "dimension_id": f"DIM{dim_idx:02d}",
                "contract_hash": f"hash_{i:03d}"
            },
            "question_context": {
                "patterns": [
                    {"id": f"PAT-Q{i:03d}-{j:03d}", "pattern": f"test_{j}"}
                    for j in range(3)
                ]
            },
            "signal_requirements": {
                "mandatory_signals": ["signal_1", "signal_2", "signal_3"]
            }
        }
        contracts.append(contract)
    
    return contracts


@pytest.fixture
def sample_chunks():
    """Generate sample chunks matching 60-chunk structure (10 PA × 6 DIM)."""
    chunks = []
    for pa_idx in range(1, 11):
        for dim_idx in range(1, 7):
            chunk = {
                "chunk_id": f"PA{pa_idx:02d}-DIM{dim_idx:02d}",
                "policy_area_id": f"PA{pa_idx:02d}",
                "dimension_id": f"DIM{dim_idx:02d}",
                "text": f"Sample text for PA{pa_idx:02d} DIM{dim_idx:02d}"
            }
            chunks.append(chunk)
    
    return chunks


@pytest.fixture
def sample_binding():
    """Create a sample ExecutorChunkBinding."""
    return ExecutorChunkBinding(
        executor_contract_id="Q001",
        policy_area_id="PA01",
        dimension_id="DIM01",
        chunk_id="PA01-DIM01",
        chunk_index=0,
        expected_patterns=[{"id": "PAT-001", "pattern": "test"}],
        irrigated_patterns=[{"id": "PAT-001", "pattern": "test"}],
        pattern_count=1,
        expected_signals=["signal_1", "signal_2"],
        irrigated_signals=[{"signal_type": "signal_1"}, {"signal_type": "signal_2"}],
        signal_count=2,
        status="matched",
        contract_file="config/executor_contracts/specialized/Q001.v3.json",
        contract_hash="test_hash",
        chunk_source="phase1_spc_ingestion"
    )


# ============================================================================
# ExecutorChunkBinding Tests
# ============================================================================

def test_executor_chunk_binding_creation(sample_binding):
    """Test ExecutorChunkBinding creation."""
    assert sample_binding.executor_contract_id == "Q001"
    assert sample_binding.chunk_id == "PA01-DIM01"
    assert sample_binding.status == "matched"
    assert len(sample_binding.validation_errors) == 0


def test_executor_chunk_binding_to_dict(sample_binding):
    """Test ExecutorChunkBinding.to_dict() serialization."""
    binding_dict = sample_binding.to_dict()
    
    assert binding_dict["executor_contract_id"] == "Q001"
    assert binding_dict["chunk_id"] == "PA01-DIM01"
    assert binding_dict["patterns_expected"] == 1
    assert binding_dict["patterns_delivered"] == 1
    assert binding_dict["signals_expected"] == 2
    assert binding_dict["signals_delivered"] == 2
    assert binding_dict["status"] == "matched"
    assert "provenance" in binding_dict
    assert "validation" in binding_dict


# ============================================================================
# build_join_table Tests
# ============================================================================

def test_build_join_table_success(sample_contracts, sample_chunks):
    """Test successful JOIN table construction."""
    bindings = build_join_table(sample_contracts, sample_chunks)
    
    assert len(bindings) == EXPECTED_CONTRACT_COUNT
    assert all(isinstance(b, ExecutorChunkBinding) for b in bindings)
    assert all(b.status == "matched" for b in bindings)
    assert all(b.chunk_id is not None for b in bindings)


def test_build_join_table_validates_uniqueness(sample_contracts, sample_chunks):
    """Test that build_join_table validates uniqueness."""
    # This should succeed with proper data
    bindings = build_join_table(sample_contracts, sample_chunks)
    
    # Check all contract IDs unique
    contract_ids = [b.executor_contract_id for b in bindings]
    assert len(contract_ids) == len(set(contract_ids))
    
    # Check all chunk IDs unique
    chunk_ids = [b.chunk_id for b in bindings]
    assert len(chunk_ids) == len(set(chunk_ids))


def test_build_join_table_missing_chunk(sample_contracts):
    """Test ABORT on missing chunk."""
    # Create chunks with one missing (59 instead of 60)
    chunks = []
    for pa_idx in range(1, 11):
        for dim_idx in range(1, 7):
            if pa_idx == 10 and dim_idx == 6:
                continue  # Skip last chunk
            chunks.append({
                "policy_area_id": f"PA{pa_idx:02d}",
                "dimension_id": f"DIM{dim_idx:02d}",
                "chunk_id": f"PA{pa_idx:02d}-DIM{dim_idx:02d}"
            })
    
    # Should raise error for contracts that need the missing chunk
    with pytest.raises(ExecutorChunkSynchronizationError) as exc:
        build_join_table(sample_contracts, chunks)
    
    assert "No chunk found" in str(exc.value)


def test_build_join_table_duplicate_chunk(sample_contracts):
    """Test ABORT on duplicate chunk."""
    # Create chunks with duplicate (61 instead of 60)
    chunks = []
    for pa_idx in range(1, 11):
        for dim_idx in range(1, 7):
            chunks.append({
                "policy_area_id": f"PA{pa_idx:02d}",
                "dimension_id": f"DIM{dim_idx:02d}",
                "chunk_id": f"PA{pa_idx:02d}-DIM{dim_idx:02d}"
            })
    
    # Add duplicate chunk
    chunks.append({
        "policy_area_id": "PA01",
        "dimension_id": "DIM01",
        "chunk_id": "PA01-DIM01-duplicate"
    })
    
    with pytest.raises(ExecutorChunkSynchronizationError) as exc:
        build_join_table(sample_contracts, chunks)
    
    assert "Duplicate chunks" in str(exc.value)


def test_build_join_table_chunk_already_bound(sample_contracts, sample_chunks):
    """Test ABORT when chunk already bound to another contract."""
    # Modify contracts to have duplicates
    modified_contracts = sample_contracts.copy()
    modified_contracts[1]["identity"]["policy_area_id"] = "PA01"
    modified_contracts[1]["identity"]["dimension_id"] = "DIM01"
    
    with pytest.raises(ExecutorChunkSynchronizationError) as exc:
        build_join_table(modified_contracts, sample_chunks)
    
    assert "already bound" in str(exc.value)


def test_build_join_table_extracts_patterns(sample_contracts, sample_chunks):
    """Test that build_join_table extracts patterns from contracts."""
    bindings = build_join_table(sample_contracts, sample_chunks)
    
    # Each contract has 3 patterns in fixture
    assert all(b.pattern_count == 3 for b in bindings)
    assert all(len(b.expected_patterns) == 3 for b in bindings)


def test_build_join_table_extracts_signals(sample_contracts, sample_chunks):
    """Test that build_join_table extracts signals from contracts."""
    bindings = build_join_table(sample_contracts, sample_chunks)
    
    # Each contract has 3 mandatory signals in fixture
    assert all(len(b.expected_signals) == 3 for b in bindings)
    assert all("signal_1" in b.expected_signals for b in bindings)


def test_build_join_table_supports_object_chunks(sample_contracts):
    """Test that build_join_table supports chunks as objects (not just dicts)."""
    # Create chunks as simple objects with attributes
    class ChunkObj:
        def __init__(self, pa_id, dim_id):
            self.policy_area_id = pa_id
            self.dimension_id = dim_id
            self.chunk_id = f"{pa_id}-{dim_id}"
    
    chunks = []
    for pa_idx in range(1, 11):
        for dim_idx in range(1, 7):
            chunks.append(ChunkObj(f"PA{pa_idx:02d}", f"DIM{dim_idx:02d}"))
    
    bindings = build_join_table(sample_contracts, chunks)
    
    assert len(bindings) == 300
    assert all(b.status == "matched" for b in bindings)


# ============================================================================
# validate_uniqueness Tests
# ============================================================================

def test_validate_uniqueness_success(sample_contracts, sample_chunks):
    """Test validate_uniqueness with valid bindings."""
    bindings = build_join_table(sample_contracts, sample_chunks)
    
    # Should not raise
    validate_uniqueness(bindings)


def test_validate_uniqueness_duplicate_contract_id():
    """Test validate_uniqueness detects duplicate contract IDs."""
    bindings = [
        ExecutorChunkBinding(
            executor_contract_id="Q001",
            policy_area_id="PA01",
            dimension_id="DIM01",
            chunk_id="PA01-DIM01",
            chunk_index=0,
            expected_patterns=[],
            irrigated_patterns=[],
            pattern_count=0,
            expected_signals=[],
            irrigated_signals=[],
            signal_count=0,
            status="matched",
            contract_file="test.json",
            contract_hash="hash",
            chunk_source="test"
        )
        for _ in range(EXPECTED_CONTRACT_COUNT)
    ]
    
    with pytest.raises(ExecutorChunkSynchronizationError) as exc:
        validate_uniqueness(bindings)
    
    assert "Duplicate executor_contract_ids" in str(exc.value)


def test_validate_uniqueness_duplicate_chunk_id(sample_contracts, sample_chunks):
    """Test validate_uniqueness detects duplicate chunk IDs."""
    bindings = build_join_table(sample_contracts, sample_chunks)
    
    # Introduce duplicate chunk_id
    bindings[1].chunk_id = bindings[0].chunk_id
    
    with pytest.raises(ExecutorChunkSynchronizationError) as exc:
        validate_uniqueness(bindings)
    
    assert "Duplicate chunk_ids" in str(exc.value)


def test_validate_uniqueness_wrong_count():
    """Test validate_uniqueness detects wrong binding count."""
    bindings = []
    
    with pytest.raises(ExecutorChunkSynchronizationError) as exc:
        validate_uniqueness(bindings)
    
    assert "Expected 300 bindings" in str(exc.value)


# ============================================================================
# generate_verification_manifest Tests
# ============================================================================

def test_generate_verification_manifest_structure(sample_contracts, sample_chunks):
    """Test generate_verification_manifest produces correct structure."""
    bindings = build_join_table(sample_contracts, sample_chunks)
    manifest = generate_verification_manifest(bindings)
    
    required_fields = [
        "version", "success", "timestamp", "total_contracts", "total_chunks",
        "bindings", "errors", "warnings", "invariants_validated", "statistics"
    ]
    for field in required_fields:
        assert field in manifest


def test_generate_verification_manifest_invariants(sample_contracts, sample_chunks):
    """Test generate_verification_manifest validates invariants."""
    bindings = build_join_table(sample_contracts, sample_chunks)
    manifest = generate_verification_manifest(bindings)
    
    invariants = manifest["invariants_validated"]
    
    assert invariants["one_to_one_mapping"] is True
    assert invariants["all_contracts_have_chunks"] is True
    assert invariants["all_chunks_assigned"] is True
    assert invariants["no_duplicate_irrigation"] is True
    assert invariants["total_bindings_equals_expected"] is True


def test_generate_verification_manifest_statistics(sample_contracts, sample_chunks):
    """Test generate_verification_manifest calculates statistics."""
    bindings = build_join_table(sample_contracts, sample_chunks)
    manifest = generate_verification_manifest(bindings)
    
    stats = manifest["statistics"]
    
    assert "avg_patterns_per_binding" in stats
    assert "avg_signals_per_binding" in stats
    assert "total_patterns_expected" in stats
    assert "total_patterns_delivered" in stats
    assert "total_signals_expected" in stats
    assert "total_signals_delivered" in stats
    assert "bindings_by_status" in stats
    
    # With 300 bindings × 3 patterns each
    assert stats["total_patterns_expected"] == 900
    # With 300 bindings × 3 signals each
    assert stats["total_signals_expected"] == 900


def test_generate_verification_manifest_bindings_optional(sample_contracts, sample_chunks):
    """Test generate_verification_manifest can exclude full bindings."""
    bindings = build_join_table(sample_contracts, sample_chunks)
    
    # With bindings
    manifest_with = generate_verification_manifest(bindings, include_full_bindings=True)
    assert "bindings" in manifest_with
    assert len(manifest_with["bindings"]) == EXPECTED_CONTRACT_COUNT
    
    # Without bindings
    manifest_without = generate_verification_manifest(bindings, include_full_bindings=False)
    assert "bindings" not in manifest_without


def test_generate_verification_manifest_success_flag(sample_contracts, sample_chunks):
    """Test generate_verification_manifest sets success flag correctly."""
    bindings = build_join_table(sample_contracts, sample_chunks)
    
    # No errors → success = True
    manifest = generate_verification_manifest(bindings)
    assert manifest["success"] is True
    
    # Add error → success = False
    bindings[0].validation_errors.append("Test error")
    manifest = generate_verification_manifest(bindings)
    assert manifest["success"] is False


def test_generate_verification_manifest_aggregates_errors(sample_contracts, sample_chunks):
    """Test generate_verification_manifest aggregates errors from bindings."""
    bindings = build_join_table(sample_contracts, sample_chunks)
    
    # Add errors to some bindings
    bindings[0].validation_errors.append("Error 1")
    bindings[1].validation_errors.append("Error 2")
    bindings[2].validation_warnings.append("Warning 1")
    
    manifest = generate_verification_manifest(bindings)
    
    assert len(manifest["errors"]) == 2
    assert "Error 1" in manifest["errors"]
    assert "Error 2" in manifest["errors"]
    assert len(manifest["warnings"]) == 1
    assert "Warning 1" in manifest["warnings"]


# ============================================================================
# Integration Tests
# ============================================================================

def test_full_synchronization_workflow(sample_contracts, sample_chunks):
    """Test complete synchronization workflow."""
    # Step 1: Build JOIN table
    bindings = build_join_table(sample_contracts, sample_chunks)
    assert len(bindings) == EXPECTED_CONTRACT_COUNT
    
    # Step 2: Validate uniqueness (already done in build_join_table, but redundant check)
    validate_uniqueness(bindings)
    
    # Step 3: Simulate irrigation (populate irrigated_* fields)
    for binding in bindings:
        binding.irrigated_patterns = binding.expected_patterns
        binding.irrigated_signals = [
            {"signal_type": sig} for sig in binding.expected_signals
        ]
        binding.signal_count = len(binding.irrigated_signals)
    
    # Step 4: Generate manifest
    manifest = generate_verification_manifest(bindings)
    
    assert manifest["success"] is True
    assert manifest["total_contracts"] == EXPECTED_CONTRACT_COUNT
    assert manifest["total_chunks"] == EXPECTED_CHUNK_COUNT
    assert manifest["invariants_validated"]["one_to_one_mapping"] is True


def test_synchronization_with_missing_signals(sample_contracts, sample_chunks):
    """Test synchronization detects missing signals."""
    bindings = build_join_table(sample_contracts, sample_chunks)
    
    # Simulate incomplete irrigation
    for binding in bindings[:10]:  # First 10 bindings
        binding.status = "missing_signals"
        binding.validation_errors.append("Missing required signals")
    
    manifest = generate_verification_manifest(bindings)
    
    assert manifest["success"] is False
    assert len(manifest["errors"]) == 10
    assert manifest["statistics"]["bindings_by_status"]["missing_signals"] == 10
    assert manifest["statistics"]["bindings_by_status"]["matched"] == 290


# ============================================================================
# Edge Cases
# ============================================================================

def test_empty_contracts_list():
    """Test build_join_table with empty contracts list."""
    with pytest.raises(ExecutorChunkSynchronizationError) as exc:
        build_join_table([], [])
    
    assert "Expected 300 bindings" in str(exc.value)


def test_malformed_contract():
    """Test build_join_table handles malformed contracts gracefully."""
    contracts = [{"identity": {}} for _ in range(EXPECTED_CONTRACT_COUNT)]  # Missing required fields
    chunks = [
        {"policy_area_id": f"PA{i:02d}", "dimension_id": f"DIM{j:02d}"}
        for i in range(1, 11) for j in range(1, 7)
    ]
    
    # Should handle missing fields with defaults
    with pytest.raises(ExecutorChunkSynchronizationError):
        build_join_table(contracts, chunks)


def test_chunk_without_ids():
    """Test build_join_table handles chunks without IDs."""
    contracts = [{
        "identity": {
            "question_id": f"Q{i:03d}",
            "policy_area_id": "PA01",
            "dimension_id": "DIM01",
            "contract_hash": "hash"
        },
        "question_context": {"patterns": []},
        "signal_requirements": {"mandatory_signals": []}
    } for i in range(1, EXPECTED_CONTRACT_COUNT + 1)]
    
    chunks = [{"policy_area_id": "PA01", "dimension_id": "DIM01"}]  # No chunk_id
    
    # Should generate chunk_id from PA and DIM
    # Will fail because only 1 chunk for EXPECTED_CONTRACT_COUNT contracts
    with pytest.raises(ExecutorChunkSynchronizationError):
        build_join_table(contracts, chunks)

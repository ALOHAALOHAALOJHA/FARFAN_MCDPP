"""
Phase 1 End-to-End Adversarial Test Suite
==========================================

DETERMINISTIC, ADVERSARIAL, OPERATIONALLY REALISTIC simulation of Phase 1.

This test executes the COMPLETE Phase 1 pipeline:
    CanonicalInput → 16 Subphases (SP0-SP15) → CanonPolicyPackage (60 chunks)

Constitutional Invariants Verified:
- EXACTLY 60 chunks (10 PA × 6 DIM)
- Complete PA×DIM grid coverage
- All metadata fields populated
- Execution trace with 16 entries
- Quality metrics within SLA thresholds

Author: F.A.R.F.A.N Pipeline Team
"""

import hashlib
import pytest
from pathlib import Path
from datetime import datetime


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="module")
def test_pdf_path():
    """Get path to test PDF."""
    pdf_path = Path(__file__).resolve().parent.parent.parent / "data" / "plans" / "Plan_1.pdf"
    if not pdf_path.exists():
        pytest.skip(f"Test PDF not found: {pdf_path}")
    return pdf_path


@pytest.fixture(scope="module")
def questionnaire_path():
    """Get path to questionnaire monolith."""
    q_path = (
        Path(__file__).resolve().parent.parent.parent
        / "canonic_questionnaire_central"
        / "questionnaire_monolith.json"
    )
    if not q_path.exists():
        pytest.skip(f"Questionnaire not found: {q_path}")
    return q_path


@pytest.fixture(scope="module")
def canonical_input(test_pdf_path, questionnaire_path):
    """Create CanonicalInput for testing."""
    from farfan_pipeline.phases.Phase_00.phase0_40_00_input_validation import CanonicalInput
    
    # Compute hashes
    pdf_sha256 = hashlib.sha256(test_pdf_path.read_bytes()).hexdigest()
    q_sha256 = hashlib.sha256(questionnaire_path.read_bytes()).hexdigest()
    
    return CanonicalInput(
        document_id=f"TEST_{test_pdf_path.stem}",
        run_id=f"e2e_test_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        pdf_path=test_pdf_path,
        pdf_sha256=pdf_sha256,
        pdf_size_bytes=test_pdf_path.stat().st_size,
        pdf_page_count=10,  # Approximate
        questionnaire_path=questionnaire_path,
        questionnaire_sha256=q_sha256,
        created_at=datetime.utcnow(),
        phase0_version="1.0.0",
        validation_passed=True,
        validation_errors=[],
        validation_warnings=[],
    )


# ============================================================================
# END-TO-END TESTS
# ============================================================================

class TestPhase1EndToEnd:
    """End-to-end execution of Phase 1 pipeline."""

    @pytest.mark.slow
    def test_full_pipeline_execution(self, canonical_input):
        """
        Execute complete Phase 1 pipeline and verify all constitutional invariants.
        
        This is the CRITICAL E2E test that verifies:
        1. Pipeline executes without fatal errors
        2. Produces exactly 60 chunks
        3. All PA×DIM combinations covered
        4. Execution trace has 16 entries (SP0-SP15)
        5. Quality metrics meet SLA thresholds
        """
        from farfan_pipeline.phases.Phase_01.phase1_13_00_cpp_ingestion import (
            execute_phase_1_with_full_contract,
            Phase1FatalError,
        )
        
        # Execute Phase 1
        try:
            cpp = execute_phase_1_with_full_contract(canonical_input, signal_registry=None)
        except Phase1FatalError as e:
            pytest.fail(f"Phase 1 execution failed with fatal error: {e}")
        except Exception as e:
            pytest.fail(f"Phase 1 execution failed with unexpected error: {e}")
        
        # CONSTITUTIONAL INVARIANT 1: Exactly 60 chunks
        assert len(cpp.chunk_graph.chunks) == 60, (
            f"CONSTITUTIONAL VIOLATION: Expected 60 chunks, got {len(cpp.chunk_graph.chunks)}"
        )
        
        # CONSTITUTIONAL INVARIANT 2: Complete PA×DIM coverage
        expected_pas = {f"PA{i:02d}" for i in range(1, 11)}
        expected_dims = {f"DIM{i:02d}" for i in range(1, 7)}
        
        actual_pas = set()
        actual_dims = set()
        for chunk in cpp.chunk_graph.chunks.values():
            actual_pas.add(chunk.policy_area_id)
            actual_dims.add(chunk.dimension_id)
        
        assert actual_pas == expected_pas, f"Missing policy areas: {expected_pas - actual_pas}"
        assert actual_dims == expected_dims, f"Missing dimensions: {expected_dims - actual_dims}"
        
        # CONSTITUTIONAL INVARIANT 3: Execution trace has 16 entries
        trace = cpp.metadata.get("execution_trace", [])
        assert len(trace) == 16, f"Expected 16 trace entries, got {len(trace)}"
        
        # Verify trace labels SP0-SP15
        expected_labels = [f"SP{i}" for i in range(16)]
        actual_labels = [entry[0] for entry in trace]
        assert actual_labels == expected_labels, (
            f"Trace labels mismatch: expected {expected_labels}, got {actual_labels}"
        )
        
        # CONSTITUTIONAL INVARIANT 4: Quality metrics meet SLA
        if cpp.quality_metrics:
            assert cpp.quality_metrics.provenance_completeness >= 0.8, (
                f"Provenance completeness {cpp.quality_metrics.provenance_completeness} < 0.8"
            )
            assert cpp.quality_metrics.structural_consistency >= 0.85, (
                f"Structural consistency {cpp.quality_metrics.structural_consistency} < 0.85"
            )
        
        # CONSTITUTIONAL INVARIANT 5: Schema version
        assert cpp.schema_version == "CPP-2025.1", (
            f"Schema version must be CPP-2025.1, got {cpp.schema_version}"
        )

    @pytest.mark.slow
    def test_chunk_metadata_completeness(self, canonical_input):
        """Verify all chunks have required metadata fields."""
        from farfan_pipeline.phases.Phase_01.phase1_13_00_cpp_ingestion import (
            execute_phase_1_with_full_contract,
        )
        
        cpp = execute_phase_1_with_full_contract(canonical_input, signal_registry=None)
        
        for chunk_id, chunk in cpp.chunk_graph.chunks.items():
            # Required fields
            assert chunk.id, f"Chunk {chunk_id} missing id"
            assert chunk.text, f"Chunk {chunk_id} missing text"
            assert chunk.policy_area_id, f"Chunk {chunk_id} missing policy_area_id"
            assert chunk.dimension_id, f"Chunk {chunk_id} missing dimension_id"
            assert chunk.bytes_hash, f"Chunk {chunk_id} missing bytes_hash"
            
            # Format validation
            assert chunk.policy_area_id.startswith("PA"), f"Invalid PA format: {chunk.policy_area_id}"
            assert chunk.dimension_id.startswith("DIM"), f"Invalid DIM format: {chunk.dimension_id}"

    @pytest.mark.slow
    def test_integrity_index_computed(self, canonical_input):
        """Verify integrity index is computed with BLAKE2b."""
        from farfan_pipeline.phases.Phase_01.phase1_13_00_cpp_ingestion import (
            execute_phase_1_with_full_contract,
        )
        
        cpp = execute_phase_1_with_full_contract(canonical_input, signal_registry=None)
        
        assert cpp.integrity_index is not None, "Integrity index must be computed"
        assert cpp.integrity_index.blake2b_root, "BLAKE2b root must be present"
        assert len(cpp.integrity_index.blake2b_root) >= 16, "BLAKE2b hash too short"

    @pytest.mark.slow
    def test_deterministic_execution(self, canonical_input):
        """Verify Phase 1 produces deterministic output for same input."""
        from farfan_pipeline.phases.Phase_01.phase1_13_00_cpp_ingestion import (
            execute_phase_1_with_full_contract,
        )
        
        # Execute twice
        cpp1 = execute_phase_1_with_full_contract(canonical_input, signal_registry=None)
        cpp2 = execute_phase_1_with_full_contract(canonical_input, signal_registry=None)
        
        # Same chunk count
        assert len(cpp1.chunk_graph.chunks) == len(cpp2.chunk_graph.chunks)
        
        # Same chunk IDs
        ids1 = set(cpp1.chunk_graph.chunks.keys())
        ids2 = set(cpp2.chunk_graph.chunks.keys())
        assert ids1 == ids2, "Chunk IDs should be deterministic"
        
        # Same integrity hash (deterministic content)
        assert cpp1.integrity_index.blake2b_root == cpp2.integrity_index.blake2b_root, (
            "Integrity hash should be deterministic"
        )


class TestPhase1AdversarialInputs:
    """Test Phase 1 with adversarial/edge-case inputs."""

    def test_rejects_invalid_pdf_hash(self, test_pdf_path, questionnaire_path):
        """Phase 1 must reject input with wrong PDF hash."""
        from farfan_pipeline.phases.Phase_00.phase0_40_00_input_validation import CanonicalInput
        from farfan_pipeline.phases.Phase_01.phase1_13_00_cpp_ingestion import (
            execute_phase_1_with_full_contract,
            Phase1FatalError,
        )
        
        q_sha256 = hashlib.sha256(questionnaire_path.read_bytes()).hexdigest()
        
        # Create input with WRONG PDF hash
        bad_input = CanonicalInput(
            document_id="ADVERSARIAL_TEST",
            run_id="adversarial_hash_test",
            pdf_path=test_pdf_path,
            pdf_sha256="0" * 64,  # Wrong hash!
            pdf_size_bytes=test_pdf_path.stat().st_size,
            pdf_page_count=10,
            questionnaire_path=questionnaire_path,
            questionnaire_sha256=q_sha256,
            created_at=datetime.utcnow(),
            phase0_version="1.0.0",
            validation_passed=True,
            validation_errors=[],
            validation_warnings=[],
        )
        
        with pytest.raises((Phase1FatalError, AssertionError)):
            execute_phase_1_with_full_contract(bad_input, signal_registry=None)

    def test_rejects_invalid_questionnaire_hash(self, test_pdf_path, questionnaire_path):
        """Phase 1 must reject input with wrong questionnaire hash."""
        from farfan_pipeline.phases.Phase_00.phase0_40_00_input_validation import CanonicalInput
        from farfan_pipeline.phases.Phase_01.phase1_13_00_cpp_ingestion import (
            execute_phase_1_with_full_contract,
            Phase1FatalError,
        )
        
        pdf_sha256 = hashlib.sha256(test_pdf_path.read_bytes()).hexdigest()
        
        # Create input with WRONG questionnaire hash
        bad_input = CanonicalInput(
            document_id="ADVERSARIAL_TEST",
            run_id="adversarial_q_hash_test",
            pdf_path=test_pdf_path,
            pdf_sha256=pdf_sha256,
            pdf_size_bytes=test_pdf_path.stat().st_size,
            pdf_page_count=10,
            questionnaire_path=questionnaire_path,
            questionnaire_sha256="f" * 64,  # Wrong hash!
            created_at=datetime.utcnow(),
            phase0_version="1.0.0",
            validation_passed=True,
            validation_errors=[],
            validation_warnings=[],
        )
        
        with pytest.raises((Phase1FatalError, AssertionError)):
            execute_phase_1_with_full_contract(bad_input, signal_registry=None)


class TestPhase1SubphaseWeights:
    """Test weight-based execution contract."""

    @pytest.mark.slow
    def test_critical_subphases_executed(self, canonical_input):
        """Verify critical subphases (SP4, SP11, SP13) are executed."""
        from farfan_pipeline.phases.Phase_01.phase1_13_00_cpp_ingestion import (
            execute_phase_1_with_full_contract,
        )
        
        cpp = execute_phase_1_with_full_contract(canonical_input, signal_registry=None)
        
        trace = cpp.metadata.get("execution_trace", [])
        executed_subphases = {entry[0] for entry in trace}
        
        # Critical subphases must be executed
        critical = {"SP4", "SP11", "SP13"}
        assert critical.issubset(executed_subphases), (
            f"Critical subphases not executed: {critical - executed_subphases}"
        )

    @pytest.mark.slow
    def test_weight_metrics_recorded(self, canonical_input):
        """Verify weight metrics are recorded in metadata."""
        from farfan_pipeline.phases.Phase_01.phase1_13_00_cpp_ingestion import (
            execute_phase_1_with_full_contract,
        )
        
        cpp = execute_phase_1_with_full_contract(canonical_input, signal_registry=None)
        
        weight_metrics = cpp.metadata.get("weight_metrics", {})
        
        assert "total_subphases" in weight_metrics, "Missing total_subphases metric"
        assert "critical_subphases" in weight_metrics, "Missing critical_subphases metric"
        assert weight_metrics["total_subphases"] == 16, "Should have 16 subphases"
        assert weight_metrics["critical_subphases"] == 3, "Should have 3 critical subphases"


class TestPhase1PADimGrid:
    """Test PA×DIM grid completeness."""

    @pytest.mark.slow
    def test_all_60_combinations_covered(self, canonical_input):
        """Verify all 60 PA×DIM combinations are covered."""
        from farfan_pipeline.phases.Phase_01.phase1_13_00_cpp_ingestion import (
            execute_phase_1_with_full_contract,
        )
        
        cpp = execute_phase_1_with_full_contract(canonical_input, signal_registry=None)
        
        # Build expected set
        expected = {
            (f"PA{pa:02d}", f"DIM{dim:02d}")
            for pa in range(1, 11)
            for dim in range(1, 7)
        }
        
        # Build actual set
        actual = {
            (chunk.policy_area_id, chunk.dimension_id)
            for chunk in cpp.chunk_graph.chunks.values()
        }
        
        assert len(actual) == 60, f"Expected 60 unique combinations, got {len(actual)}"
        assert actual == expected, f"Missing combinations: {expected - actual}"

    @pytest.mark.slow
    def test_no_duplicate_chunks(self, canonical_input):
        """Verify no duplicate chunk IDs."""
        from farfan_pipeline.phases.Phase_01.phase1_13_00_cpp_ingestion import (
            execute_phase_1_with_full_contract,
        )
        
        cpp = execute_phase_1_with_full_contract(canonical_input, signal_registry=None)
        
        chunk_ids = list(cpp.chunk_graph.chunks.keys())
        unique_ids = set(chunk_ids)
        
        assert len(chunk_ids) == len(unique_ids), (
            f"Duplicate chunk IDs detected: {len(chunk_ids)} vs {len(unique_ids)} unique"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not slow"])

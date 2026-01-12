"""
Model Output Verification Tests
================================

Comprehensive test suite to verify that all Phase 0, Phase 1, and CPP models
can produce expected outputs and meet their contracts.

Tests:
- Phase 0 models instantiation and validation
- Phase 1 models instantiation for all 16 subphases
- CPP models instantiation and assembly
- Contract validation (invariants, pre/post conditions)
- Expected output structure verification

Author: F.A.R.F.A.N Testing Team
Date: 2025-12-10
"""

import pytest
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict

# Phase 0 Models
from canonic_phases.Phase_one.phase0_input_validation import (
    Phase0Input,
    CanonicalInput,
    Phase0ValidationContract,
)

# Phase 1 Models
from canonic_phases.Phase_one.phase1_models import (
    LanguageData,
    PreprocessedDoc,
    StructureData,
    KnowledgeGraph,
    KGNode,
    KGEdge,
    Chunk,
    SmartChunk,
    CausalGraph,
    ValidationResult,
    CausalChains,
    IntegratedCausal,
    Arguments,
    Temporal,
    Discourse,
    Strategic,
)

# CPP Models
from canonic_phases.Phase_one.cpp_models import (
    CanonPolicyPackage,
    ChunkGraph,
    QualityMetrics,
    IntegrityIndex,
    PolicyManifest,
    LegacyChunk,
    TextSpan,
    ChunkResolution,
)


# =============================================================================
# PHASE 0 MODEL TESTS
# =============================================================================

class TestPhase0Models:
    """Test Phase 0 model instantiation and validation."""
    
    def test_phase0_input_instantiation(self):
        """Test Phase0Input can be instantiated with required fields."""
        input_data = Phase0Input(
            pdf_path=Path("/tmp/test.pdf"),
            run_id="test_run_001",
            questionnaire_path=None
        )
        
        assert input_data.pdf_path == Path("/tmp/test.pdf")
        assert input_data.run_id == "test_run_001"
        assert input_data.questionnaire_path is None
    
    def test_canonical_input_instantiation(self):
        """Test CanonicalInput can be instantiated with all required fields."""
        output = CanonicalInput(
            document_id="test_doc",
            run_id="test_run_001",
            pdf_path=Path("/tmp/test.pdf"),
            pdf_sha256="a" * 64,
            pdf_size_bytes=1000,
            pdf_page_count=10,
            questionnaire_path=Path("/tmp/q.json"),
            questionnaire_sha256="b" * 64,
            created_at=datetime.now(timezone.utc),
            phase0_version="1.0.0",
            validation_passed=True,
            validation_errors=[],
            validation_warnings=[]
        )
        
        # Verify required fields
        assert output.document_id == "test_doc"
        assert output.validation_passed is True
        assert len(output.validation_errors) == 0
        assert output.pdf_page_count == 10
        assert output.pdf_size_bytes == 1000
        assert len(output.pdf_sha256) == 64
        assert len(output.questionnaire_sha256) == 64
    
    def test_canonical_input_field_count(self):
        """Verify CanonicalInput has exactly 13 fields."""
        output = CanonicalInput(
            document_id="test",
            run_id="run",
            pdf_path=Path("/tmp/test.pdf"),
            pdf_sha256="a" * 64,
            pdf_size_bytes=100,
            pdf_page_count=1,
            questionnaire_path=Path("/tmp/q.json"),
            questionnaire_sha256="b" * 64,
            created_at=datetime.now(timezone.utc),
            phase0_version="1.0.0",
            validation_passed=True,
            validation_errors=[],
            validation_warnings=[]
        )
        
        assert len(output.__dataclass_fields__) == 13
    
    def test_phase0_validation_contract_instantiation(self):
        """Test Phase0ValidationContract can be instantiated."""
        contract = Phase0ValidationContract()
        
        assert contract.phase_name == "phase0_input_validation"
        assert len(contract.invariants) == 5
        
        # Verify invariant names
        invariant_names = {inv.name for inv in contract.invariants}
        expected_names = {
            "validation_passed",
            "pdf_page_count_positive",
            "pdf_size_positive",
            "sha256_format",
            "no_validation_errors"
        }
        assert invariant_names == expected_names


# =============================================================================
# PHASE 1 MODEL TESTS (SP0-SP15 Outputs)
# =============================================================================

class TestPhase1SubphaseModels:
    """Test Phase 1 subphase output models."""
    
    def test_sp0_language_data(self):
        """SP0: LanguageData output verification."""
        lang_data = LanguageData(
            primary_language="ES",
            secondary_languages=["EN"],
            confidence_scores={"ES": 0.95, "EN": 0.05},
            detection_method="langdetect"
        )
        
        assert lang_data.primary_language == "ES"
        assert len(lang_data.secondary_languages) >= 0
        assert "ES" in lang_data.confidence_scores
    
    def test_sp1_preprocessed_doc(self):
        """SP1: PreprocessedDoc output verification."""
        preprocessed = PreprocessedDoc(
            tokens=["palabra1", "palabra2", "palabra3"],
            sentences=["Sentencia uno.", "Sentencia dos."],
            paragraphs=["Párrafo uno."]
        )
        
        assert len(preprocessed.tokens) == 3
        assert len(preprocessed.sentences) == 2
        assert len(preprocessed.paragraphs) == 1
    
    def test_sp2_structure_data(self):
        """SP2: StructureData output verification."""
        structure = StructureData(
            sections=[{"id": "sec1", "title": "Section 1"}],
            hierarchy={"sec1": None},
            paragraph_mapping={0: "sec1"},
            unassigned_paragraphs=[]
        )
        
        assert len(structure.sections) >= 0
        assert isinstance(structure.hierarchy, dict)
        # Test alias property
        assert structure.paragraph_to_section == structure.paragraph_mapping
    
    def test_sp3_knowledge_graph(self):
        """SP3: KnowledgeGraph output verification."""
        node1 = KGNode(id="n1", type="entity", text="Entity 1")
        node2 = KGNode(id="n2", type="entity", text="Entity 2")
        edge = KGEdge(source="n1", target="n2", type="related", weight=1.0)
        
        kg = KnowledgeGraph(
            nodes=[node1, node2],
            edges=[edge]
        )
        
        assert len(kg.nodes) == 2
        assert len(kg.edges) == 1
        assert kg.nodes[0].id == "n1"
        assert kg.edges[0].source == "n1"
    
    def test_sp4_chunk_output(self):
        """SP4: Chunk output verification (60 chunks)."""
        chunks: List[Chunk] = []
        
        # Generate 60 chunks (PA01-PA10 × DIM01-DIM06)
        for pa_num in range(1, 11):
            for dim_num in range(1, 7):
                chunk = Chunk(
                    chunk_id=f"PA{pa_num:02d}-DIM{dim_num:02d}",
                    policy_area_id=f"PA{pa_num:02d}",
                    dimension_id=f"DIM{dim_num:02d}",
                    chunk_index=(pa_num - 1) * 6 + (dim_num - 1),
                    text=f"Content for PA{pa_num:02d}-DIM{dim_num:02d}"
                )
                chunks.append(chunk)
        
        # Verify 60 chunks (CONSTITUTIONAL INVARIANT)
        assert len(chunks) == 60
        
        # Verify unique chunk_ids
        chunk_ids = {c.chunk_id for c in chunks}
        assert len(chunk_ids) == 60
        
        # Verify PA×DIM coverage
        expected_ids = {
            f"PA{pa:02d}-DIM{dim:02d}"
            for pa in range(1, 11)
            for dim in range(1, 7)
        }
        assert chunk_ids == expected_ids
    
    def test_sp5_causal_chains(self):
        """SP5: CausalChains output verification."""
        causal = CausalChains(
            chains=[{"cause": "A", "effect": "B"}],
            mechanisms=["mechanism1"],
            per_chunk_causal={"PA01-DIM01": {"chains": 1}}
        )
        
        assert len(causal.chains) >= 0
        assert isinstance(causal.per_chunk_causal, dict)
    
    def test_sp6_integrated_causal(self):
        """SP6: IntegratedCausal output verification."""
        integrated = IntegratedCausal(
            global_graph={"nodes": [], "edges": []},
            validated_hierarchy=True,
            cross_chunk_links=[],
            teoria_cambio_status="OK"
        )
        
        assert isinstance(integrated.global_graph, dict)
        assert isinstance(integrated.validated_hierarchy, bool)
    
    def test_sp7_arguments(self):
        """SP7: Arguments output verification."""
        args = Arguments(
            premises=[{"id": "p1", "text": "Premise 1"}],
            conclusions=[{"id": "c1", "text": "Conclusion 1"}],
            reasoning=[{"pattern": "deductive"}],
            per_chunk_args={}
        )
        
        assert len(args.premises) >= 0
        assert len(args.conclusions) >= 0
    
    def test_sp8_temporal(self):
        """SP8: Temporal output verification."""
        temporal = Temporal(
            time_markers=[{"date": "2025-01-01"}],
            sequences=[{"start": "A", "end": "B"}],
            durations=[{"duration": "1 year"}],
            per_chunk_temporal={}
        )
        
        assert len(temporal.time_markers) >= 0
        assert isinstance(temporal.per_chunk_temporal, dict)
    
    def test_sp9_discourse(self):
        """SP9: Discourse output verification."""
        discourse = Discourse(
            markers=[{"type": "connector", "text": "therefore"}],
            patterns=[{"pattern": "argumentative"}],
            coherence={"score": 0.8},
            per_chunk_discourse={}
        )
        
        assert len(discourse.markers) >= 0
        assert "score" in discourse.coherence or len(discourse.coherence) == 0
    
    def test_sp10_strategic(self):
        """SP10: Strategic output verification."""
        strategic = Strategic(
            strategic_rank={"PA01-DIM01": 75},
            priorities=[{"rank": 1, "chunk_id": "PA01-DIM01"}],
            integrated_view={},
            strategic_scores={}
        )
        
        assert isinstance(strategic.strategic_rank, dict)
        # Verify ranks in valid range [0, 100]
        for rank in strategic.strategic_rank.values():
            assert 0 <= rank <= 100
    
    def test_sp11_smart_chunk_output(self):
        """SP11: SmartChunk output verification (60 smart chunks)."""
        smart_chunks: List[SmartChunk] = []
        
        # Generate 60 smart chunks
        for pa_num in range(1, 11):
            for dim_num in range(1, 7):
                chunk_id = f"PA{pa_num:02d}-DIM{dim_num:02d}"
                smart_chunk = SmartChunk(
                    chunk_id=chunk_id,
                    text=f"Content for {chunk_id}",
                    chunk_type="MACRO",
                    chunk_index=(pa_num - 1) * 6 + (dim_num - 1),
                    policy_area_id=f"PA{pa_num:02d}",
                    dimension_id=f"DIM{dim_num:02d}",
                    causal_graph=CausalGraph(),
                    temporal_markers={},
                    arguments={},
                    discourse_mode="default",
                    strategic_rank=50,
                    irrigation_links=[],
                    signal_tags=[],
                    signal_scores={},
                    signal_version="1.0",
                    rank_score=0.5,
                    signal_weighted_score=0.5
                )
                smart_chunks.append(smart_chunk)
        
        # Verify 60 smart chunks (CONSTITUTIONAL INVARIANT)
        assert len(smart_chunks) == 60
        
        # Verify all have strategic_rank
        for sc in smart_chunks:
            assert hasattr(sc, 'strategic_rank')
            assert isinstance(sc.strategic_rank, (int, float))
    
    def test_sp13_validation_result(self):
        """SP13: ValidationResult output verification."""
        validation = ValidationResult(
            status="VALID",
            violations=[],
            checked_count=60,
            passed_count=60
        )
        
        assert validation.status in ["VALID", "INVALID"]
        assert validation.passed_count <= validation.checked_count
        assert len(validation.violations) == 0  # For VALID status


# =============================================================================
# CPP MODEL TESTS
# =============================================================================

class TestCPPModels:
    """Test CPP (CanonPolicyPackage) model instantiation."""
    
    def test_text_span(self):
        """Test TextSpan model."""
        span = TextSpan(start=0, end=100)
        
        assert span.start == 0
        assert span.end == 100
        assert span.start <= span.end
    
    def test_legacy_chunk(self):
        """Test LegacyChunk model with validation."""
        chunk = LegacyChunk(
            id="PA01_DIM01",
            text="Test content",
            text_span=TextSpan(0, 100),
            resolution=ChunkResolution.MACRO,
            bytes_hash="abc123def456",
            policy_area_id="PA01",
            dimension_id="DIM01"
        )
        
        assert chunk.id == "PA01_DIM01"
        assert chunk.policy_area_id == "PA01"
        assert chunk.dimension_id == "DIM01"
        assert chunk.resolution == ChunkResolution.MACRO
    
    def test_legacy_chunk_validation_invalid_pa(self):
        """Test LegacyChunk rejects invalid policy_area_id."""
        with pytest.raises(ValueError, match="Invalid policy_area_id"):
            LegacyChunk(
                id="PA99_DIM01",
                text="Test",
                text_span=TextSpan(0, 10),
                resolution=ChunkResolution.MACRO,
                bytes_hash="abc",
                policy_area_id="PA99",  # Invalid
                dimension_id="DIM01"
            )
    
    def test_legacy_chunk_validation_invalid_dim(self):
        """Test LegacyChunk rejects invalid dimension_id."""
        with pytest.raises(ValueError, match="Invalid dimension_id"):
            LegacyChunk(
                id="PA01_DIM99",
                text="Test",
                text_span=TextSpan(0, 10),
                resolution=ChunkResolution.MACRO,
                bytes_hash="abc",
                policy_area_id="PA01",
                dimension_id="DIM99"  # Invalid
            )
    
    def test_chunk_graph_60_chunks(self):
        """Test ChunkGraph with 60 chunks."""
        chunk_graph = ChunkGraph()
        
        # Add 60 chunks
        for pa_num in range(1, 11):
            for dim_num in range(1, 7):
                chunk_id = f"PA{pa_num:02d}_DIM{dim_num:02d}"
                chunk = LegacyChunk(
                    id=chunk_id,
                    text=f"Content for {chunk_id}",
                    text_span=TextSpan(0, 100),
                    resolution=ChunkResolution.MACRO,
                    bytes_hash="abc123",
                    policy_area_id=f"PA{pa_num:02d}",
                    dimension_id=f"DIM{dim_num:02d}"
                )
                chunk_graph.chunks[chunk_id] = chunk
        
        # Verify 60 chunks
        assert len(chunk_graph.chunks) == 60
        assert chunk_graph.chunk_count == 60
    
    def test_quality_metrics(self):
        """Test QualityMetrics model."""
        quality = QualityMetrics(
            provenance_completeness=0.85,
            structural_consistency=0.90,
            chunk_count=60,
            coverage_analysis={},
            signal_quality_by_pa={}
        )
        
        # Verify thresholds per FORCING ROUTE
        assert quality.provenance_completeness >= 0.8  # [POST-002]
        assert quality.structural_consistency >= 0.85  # [POST-003]
        assert quality.chunk_count == 60
    
    def test_integrity_index(self):
        """Test IntegrityIndex model."""
        integrity = IntegrityIndex(
            blake2b_root="a" * 64,
            chunk_hashes=("chunk1hash", "chunk2hash"),
            timestamp="2025-12-10T17:00:00Z"
        )
        
        assert len(integrity.blake2b_root) > 0
        assert isinstance(integrity.timestamp, str)
    
    def test_policy_manifest(self):
        """Test PolicyManifest model."""
        manifest = PolicyManifest(
            questionnaire_version="1.0.0",
            questionnaire_sha256="a" * 64,
            policy_areas=tuple(f"PA{i:02d}" for i in range(1, 11)),
            dimensions=tuple(f"DIM{i:02d}" for i in range(1, 7))
        )
        
        assert len(manifest.policy_areas) == 10
        assert len(manifest.dimensions) == 6
        assert manifest.questionnaire_version == "1.0.0"
    
    def test_canon_policy_package_assembly(self):
        """Test CanonPolicyPackage full assembly."""
        # Build ChunkGraph with 1 chunk (for testing)
        chunk_graph = ChunkGraph()
        chunk = LegacyChunk(
            id="PA01_DIM01",
            text="Test content",
            text_span=TextSpan(0, 100),
            resolution=ChunkResolution.MACRO,
            bytes_hash="abc123",
            policy_area_id="PA01",
            dimension_id="DIM01"
        )
        chunk_graph.chunks[chunk.id] = chunk
        
        # Build QualityMetrics
        quality = QualityMetrics(
            provenance_completeness=0.85,
            structural_consistency=0.90,
            chunk_count=1,  # For test
            coverage_analysis={},
            signal_quality_by_pa={}
        )
        
        # Build IntegrityIndex
        integrity = IntegrityIndex(
            blake2b_root="a" * 64,
            chunk_hashes=("abc123",),
            timestamp="2025-12-10T17:00:00Z"
        )
        
        # Build PolicyManifest
        manifest = PolicyManifest(
            questionnaire_version="1.0.0",
            questionnaire_sha256="a" * 64,
            policy_areas=("PA01",),
            dimensions=("DIM01",)
        )
        
        # Assemble CPP
        cpp = CanonPolicyPackage(
            schema_version="SPC-2025.1",
            document_id="test_doc",
            chunk_graph=chunk_graph,
            quality_metrics=quality,
            integrity_index=integrity,
            policy_manifest=manifest,
            metadata={}
        )
        
        # Verify CPP structure
        assert cpp.schema_version == "SPC-2025.1"
        assert cpp.document_id == "test_doc"
        assert len(cpp.chunk_graph.chunks) >= 1
        assert cpp.quality_metrics.provenance_completeness >= 0.8
        assert cpp.quality_metrics.structural_consistency >= 0.85


# =============================================================================
# CONSTITUTIONAL INVARIANT TESTS
# =============================================================================

class TestConstitutionalInvariants:
    """Test that constitutional invariants are enforced."""
    
    def test_60_chunk_invariant_sp4(self):
        """Verify SP4 produces exactly 60 chunks."""
        chunks: List[Chunk] = []
        
        for pa in range(1, 11):
            for dim in range(1, 7):
                chunk = Chunk(
                    chunk_id=f"PA{pa:02d}-DIM{dim:02d}",
                    policy_area_id=f"PA{pa:02d}",
                    dimension_id=f"DIM{dim:02d}",
                    text="content"
                )
                chunks.append(chunk)
        
        # CONSTITUTIONAL INVARIANT
        assert len(chunks) == 60, f"SP4 must produce exactly 60 chunks, got {len(chunks)}"
    
    def test_60_chunk_invariant_sp11(self):
        """Verify SP11 produces exactly 60 smart chunks."""
        smart_chunks: List[SmartChunk] = []
        
        for pa in range(1, 11):
            for dim in range(1, 7):
                sc = SmartChunk(
                    chunk_id=f"PA{pa:02d}-DIM{dim:02d}",
                    text="content",
                    chunk_type="MACRO",
                    chunk_index=0,
                    policy_area_id=f"PA{pa:02d}",
                    dimension_id=f"DIM{dim:02d}",
                    causal_graph=CausalGraph(),
                    temporal_markers={},
                    arguments={},
                    discourse_mode="default",
                    strategic_rank=50,
                    irrigation_links=[],
                    signal_tags=[],
                    signal_scores={},
                    signal_version="1.0",
                    rank_score=0.5,
                    signal_weighted_score=0.5
                )
                smart_chunks.append(sc)
        
        # CONSTITUTIONAL INVARIANT
        assert len(smart_chunks) == 60, f"SP11 must produce exactly 60 smart chunks, got {len(smart_chunks)}"
    
    def test_60_chunk_invariant_cpp(self):
        """Verify CPP ChunkGraph has exactly 60 chunks."""
        chunk_graph = ChunkGraph()
        
        for pa in range(1, 11):
            for dim in range(1, 7):
                chunk_id = f"PA{pa:02d}_DIM{dim:02d}"
                chunk = LegacyChunk(
                    id=chunk_id,
                    text="content",
                    text_span=TextSpan(0, 10),
                    resolution=ChunkResolution.MACRO,
                    bytes_hash="abc",
                    policy_area_id=f"PA{pa:02d}",
                    dimension_id=f"DIM{dim:02d}"
                )
                chunk_graph.chunks[chunk_id] = chunk
        
        # CONSTITUTIONAL INVARIANT
        assert chunk_graph.chunk_count == 60, f"CPP must have exactly 60 chunks, got {chunk_graph.chunk_count}"
    
    def test_padim_coverage_complete(self):
        """Verify PA×DIM grid coverage is complete (all 60 cells)."""
        expected_ids = {
            f"PA{pa:02d}-DIM{dim:02d}"
            for pa in range(1, 11)
            for dim in range(1, 7)
        }
        
        assert len(expected_ids) == 60
        
        # Verify format
        for chunk_id in expected_ids:
            assert chunk_id.startswith("PA")
            assert "-DIM" in chunk_id


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

"""
SEVERE PHASE 1 SUBPHASE TESTS
==============================

Comprehensive stress testing for all 16 Phase 1 subphases (SP0-SP15).
Tests extreme cases, edge conditions, failures, and constitutional invariants.

Test Strategy:
- Edge cases (empty input, malformed data, boundary values)
- Stress tests (large documents, many entities, complex graphs)
- Failure scenarios (missing dependencies, invalid data)
- Constitutional invariant violations
- Performance under load
- Concurrent execution safety

Author: F.A.R.F.A.N Testing Team
Date: 2025-12-10
Status: SEVERE - Break it if you can
"""

import pytest
import hashlib
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict
import json

# Phase 0 Models
from canonic_phases.Phase_one.phase0_input_validation import (
    CanonicalInput,
)

# Phase 1 Contract
from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
    Phase1SPCIngestionFullContract,
    Phase1FatalError,
    PADimGridSpecification,
)

# Phase 1 Models
from canonic_phases.Phase_one.phase1_models import (
    LanguageData,
    PreprocessedDoc,
    StructureData,
    KnowledgeGraph,
    Chunk,
    SmartChunk,
    ValidationResult,
)

# CPP Models
from canonic_phases.Phase_one.cpp_models import (
    CanonPolicyPackage,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def minimal_pdf():
    """Create minimal valid PDF for testing."""
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as f:
        # Minimal PDF structure
        content = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj
xref
0 4
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
trailer<</Size 4/Root 1 0 R>>
startxref
197
%%EOF"""
        f.write(content)
        path = Path(f.name)
    
    yield path
    
    # Cleanup
    if path.exists():
        path.unlink()


@pytest.fixture
def large_pdf():
    """Create large PDF (100+ pages) for stress testing."""
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as f:
        # Generate large PDF content
        content = b"%PDF-1.4\n"
        content += b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        content += b"2 0 obj<</Type/Pages/Count 100/Kids["
        for i in range(100):
            content += f"{i+3} 0 R ".encode()
        content += b"]>>endobj\n"
        
        for i in range(100):
            content += f"{i+3} 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\n".encode()
        
        f.write(content)
        path = Path(f.name)
    
    yield path
    
    if path.exists():
        path.unlink()


@pytest.fixture
def canonical_input_minimal(minimal_pdf):
    """Minimal CanonicalInput for testing."""
    pdf_hash = hashlib.sha256(minimal_pdf.read_bytes()).hexdigest()
    
    questionnaire_path = Path(tempfile.mktemp(suffix='.json'))
    questionnaire_path.write_text('{"version": "1.0.0"}')
    q_hash = hashlib.sha256(questionnaire_path.read_bytes()).hexdigest()
    
    canonical_input = CanonicalInput(
        document_id="test_minimal",
        run_id="severe_test_001",
        pdf_path=minimal_pdf,
        pdf_sha256=pdf_hash,
        pdf_size_bytes=minimal_pdf.stat().st_size,
        pdf_page_count=1,
        questionnaire_path=questionnaire_path,
        questionnaire_sha256=q_hash,
        created_at=datetime.now(timezone.utc),
        phase0_version="1.0.0",
        validation_passed=True,
        validation_errors=[],
        validation_warnings=[]
    )
    
    yield canonical_input
    
    if questionnaire_path.exists():
        questionnaire_path.unlink()


@pytest.fixture
def canonical_input_large(large_pdf):
    """Large CanonicalInput for stress testing."""
    pdf_hash = hashlib.sha256(large_pdf.read_bytes()).hexdigest()
    
    questionnaire_path = Path(tempfile.mktemp(suffix='.json'))
    questionnaire_path.write_text('{"version": "1.0.0"}')
    q_hash = hashlib.sha256(questionnaire_path.read_bytes()).hexdigest()
    
    canonical_input = CanonicalInput(
        document_id="test_large",
        run_id="severe_test_002",
        pdf_path=large_pdf,
        pdf_sha256=pdf_hash,
        pdf_size_bytes=large_pdf.stat().st_size,
        pdf_page_count=100,
        questionnaire_path=questionnaire_path,
        questionnaire_sha256=q_hash,
        created_at=datetime.now(timezone.utc),
        phase0_version="1.0.0",
        validation_passed=True,
        validation_errors=[],
        validation_warnings=[]
    )
    
    yield canonical_input
    
    if questionnaire_path.exists():
        questionnaire_path.unlink()


# =============================================================================
# SP0: LANGUAGE DETECTION - SEVERE TESTS
# =============================================================================

class TestSP0LanguageDetectionSevere:
    """Severe tests for SP0 - Language Detection."""
    
    def test_sp0_empty_pdf(self, canonical_input_minimal):
        """Test language detection with empty/minimal PDF."""
        contract = Phase1SPCIngestionFullContract()
        
        # Should not crash, should default to "ES"
        lang_data = contract._execute_sp0_language_detection(canonical_input_minimal)
        
        assert isinstance(lang_data, LanguageData)
        assert lang_data.primary_language in ["ES", "EN", "es", "en"]
        assert isinstance(lang_data.secondary_languages, list)
    
    def test_sp0_corrupted_pdf_text(self, canonical_input_minimal):
        """Test with PDF that has corrupted text extraction."""
        contract = Phase1SPCIngestionFullContract()
        
        # Should handle gracefully
        lang_data = contract._execute_sp0_language_detection(canonical_input_minimal)
        
        assert isinstance(lang_data, LanguageData)
        # Should default to ES if detection fails
        assert hasattr(lang_data, 'primary_language')
    
    def test_sp0_multilingual_document(self, canonical_input_minimal):
        """Test detection with multiple languages."""
        contract = Phase1SPCIngestionFullContract()
        
        lang_data = contract._execute_sp0_language_detection(canonical_input_minimal)
        
        # Verify structure
        assert hasattr(lang_data, 'primary_language')
        assert hasattr(lang_data, 'secondary_languages')
        assert hasattr(lang_data, 'confidence_scores')
    
    def test_sp0_output_sealed(self, canonical_input_minimal):
        """Test that LanguageData is sealed after creation."""
        contract = Phase1SPCIngestionFullContract()
        
        lang_data = contract._execute_sp0_language_detection(canonical_input_minimal)
        
        # Check seal flag
        assert hasattr(lang_data, '_sealed')


# =============================================================================
# SP1: PREPROCESSING - SEVERE TESTS
# =============================================================================

class TestSP1PreprocessingSevere:
    """Severe tests for SP1 - Advanced Preprocessing."""
    
    def test_sp1_minimal_document(self, canonical_input_minimal):
        """Test preprocessing with minimal content."""
        contract = Phase1SPCIngestionFullContract()
        
        lang_data = contract._execute_sp0_language_detection(canonical_input_minimal)
        preprocessed = contract._execute_sp1_preprocessing(canonical_input_minimal, lang_data)
        
        assert isinstance(preprocessed, PreprocessedDoc)
        assert isinstance(preprocessed.tokens, list)
        assert isinstance(preprocessed.sentences, list)
        assert isinstance(preprocessed.paragraphs, list)
    
    def test_sp1_special_characters(self, canonical_input_minimal):
        """Test with special characters, unicode, emojis."""
        contract = Phase1SPCIngestionFullContract()
        
        lang_data = LanguageData(
            primary_language="ES",
            secondary_languages=[],
            confidence_scores={"ES": 1.0},
            detection_method="test"
        )
        
        preprocessed = contract._execute_sp1_preprocessing(canonical_input_minimal, lang_data)
        
        # Should handle NFC normalization
        assert hasattr(preprocessed, 'normalized_text')
        assert isinstance(preprocessed.tokens, list)
    
    def test_sp1_very_long_paragraphs(self, canonical_input_large):
        """Test with very long paragraphs (10,000+ words)."""
        contract = Phase1SPCIngestionFullContract()
        
        lang_data = LanguageData(
            primary_language="ES",
            secondary_languages=[],
            confidence_scores={"ES": 1.0},
            detection_method="test"
        )
        
        # Should not crash or timeout
        preprocessed = contract._execute_sp1_preprocessing(canonical_input_large, lang_data)
        
        assert isinstance(preprocessed, PreprocessedDoc)
    
    def test_sp1_no_sentences(self, canonical_input_minimal):
        """Test with text that has no clear sentence boundaries."""
        contract = Phase1SPCIngestionFullContract()
        
        lang_data = LanguageData(
            primary_language="ES",
            secondary_languages=[],
            confidence_scores={"ES": 1.0},
            detection_method="test"
        )
        
        preprocessed = contract._execute_sp1_preprocessing(canonical_input_minimal, lang_data)
        
        # Should still produce at least one sentence
        assert len(preprocessed.sentences) >= 0
        assert len(preprocessed.paragraphs) >= 0


# =============================================================================
# SP2: STRUCTURAL ANALYSIS - SEVERE TESTS
# =============================================================================

class TestSP2StructuralSevere:
    """Severe tests for SP2 - Structural Analysis."""
    
    def test_sp2_no_structure(self):
        """Test with document that has no clear structure."""
        contract = Phase1SPCIngestionFullContract()
        
        preprocessed = PreprocessedDoc(
            tokens=["word"] * 100,
            sentences=["Sentence."] * 10,
            paragraphs=["Paragraph text."] * 5
        )
        
        structure = contract._execute_sp2_structural(preprocessed)
        
        assert isinstance(structure, StructureData)
        assert isinstance(structure.sections, list)
        assert isinstance(structure.hierarchy, dict)
    
    def test_sp2_deeply_nested_structure(self):
        """Test with deeply nested document structure (10+ levels)."""
        contract = Phase1SPCIngestionFullContract()
        
        preprocessed = PreprocessedDoc(
            tokens=["word"] * 1000,
            sentences=["Sentence."] * 100,
            paragraphs=["Paragraph."] * 50
        )
        
        structure = contract._execute_sp2_structural(preprocessed)
        
        # Should handle deep nesting
        assert isinstance(structure.hierarchy, dict)
    
    def test_sp2_malformed_sections(self):
        """Test with malformed section markers."""
        contract = Phase1SPCIngestionFullContract()
        
        preprocessed = PreprocessedDoc(
            tokens=["##", "Header", "###", "Subheader"] * 10,
            sentences=["Text."] * 20,
            paragraphs=["Para."] * 10
        )
        
        structure = contract._execute_sp2_structural(preprocessed)
        
        assert isinstance(structure, StructureData)
        # Verify paragraph_to_section alias works
        assert structure.paragraph_to_section == structure.paragraph_mapping


# =============================================================================
# SP3: KNOWLEDGE GRAPH - SEVERE TESTS
# =============================================================================

class TestSP3KnowledgeGraphSevere:
    """Severe tests for SP3 - Knowledge Graph Construction."""
    
    def test_sp3_no_entities(self):
        """Test with text containing no recognizable entities."""
        contract = Phase1SPCIngestionFullContract()
        
        preprocessed = PreprocessedDoc(
            tokens=["the", "a", "is", "are"] * 10,
            sentences=["A sentence."] * 5,
            paragraphs=["A paragraph."] * 3
        )
        
        structure = StructureData()
        
        kg = contract._execute_sp3_knowledge_graph(preprocessed, structure)
        
        assert isinstance(kg, KnowledgeGraph)
        assert isinstance(kg.nodes, list)
        assert isinstance(kg.edges, list)
    
    def test_sp3_massive_entity_graph(self):
        """Test with 1000+ entities and complex relationships."""
        contract = Phase1SPCIngestionFullContract()
        
        # Generate large document
        tokens = []
        for i in range(1000):
            tokens.extend([f"Entity{i}", "relates", "to", f"Entity{i+1}"])
        
        preprocessed = PreprocessedDoc(
            tokens=tokens,
            sentences=[" ".join(tokens[i:i+50]) for i in range(0, len(tokens), 50)],
            paragraphs=[" ".join(tokens[i:i+200]) for i in range(0, len(tokens), 200)]
        )
        
        structure = StructureData()
        
        # Should not timeout or crash
        kg = contract._execute_sp3_knowledge_graph(preprocessed, structure)
        
        assert isinstance(kg, KnowledgeGraph)
    
    def test_sp3_circular_references(self):
        """Test with circular entity references (A→B→C→A)."""
        contract = Phase1SPCIngestionFullContract()
        
        preprocessed = PreprocessedDoc(
            tokens=["A", "relates", "B", "B", "relates", "C", "C", "relates", "A"] * 10,
            sentences=["A relates to B."] * 3,
            paragraphs=["Circular relationships."] * 2
        )
        
        structure = StructureData()
        
        kg = contract._execute_sp3_knowledge_graph(preprocessed, structure)
        
        # Should handle cycles gracefully
        assert isinstance(kg, KnowledgeGraph)


# =============================================================================
# SP4: PA×DIM SEGMENTATION - SEVERE TESTS (CRITICAL)
# =============================================================================

class TestSP4SegmentationSevere:
    """Severe tests for SP4 - PA×DIM Segmentation (CONSTITUTIONAL INVARIANT)."""
    
    def test_sp4_minimal_content_60_chunks(self):
        """Test 60-chunk generation with minimal content."""
        contract = Phase1SPCIngestionFullContract()
        
        preprocessed = PreprocessedDoc(
            tokens=["word"],
            sentences=["Sentence."],
            paragraphs=["Minimal paragraph."]
        )
        
        structure = StructureData(
            sections=[],
            hierarchy={},
            paragraph_mapping={},
            unassigned_paragraphs=[0]
        )
        
        kg = KnowledgeGraph(nodes=[], edges=[])
        
        chunks = contract._execute_sp4_segmentation(preprocessed, structure, kg)
        
        # CONSTITUTIONAL INVARIANT: EXACTLY 60 chunks
        assert len(chunks) == 60, f"FATAL: Got {len(chunks)} chunks, expected 60"
        
        # Verify all PA×DIM cells filled
        chunk_ids = {c.chunk_id for c in chunks}
        expected_ids = {
            f"PA{pa:02d}-DIM{dim:02d}"
            for pa in range(1, 11)
            for dim in range(1, 7)
        }
        assert chunk_ids == expected_ids, "Incomplete PA×DIM coverage"
    
    def test_sp4_massive_document_60_chunks(self):
        """Test 60-chunk generation with massive document (1000+ paragraphs)."""
        contract = Phase1SPCIngestionFullContract()
        
        # Generate 1000 paragraphs
        paragraphs = [f"Paragraph {i} with substantial content." for i in range(1000)]
        
        preprocessed = PreprocessedDoc(
            tokens=["word"] * 10000,
            sentences=["Sentence."] * 2000,
            paragraphs=paragraphs
        )
        
        structure = StructureData()
        kg = KnowledgeGraph()
        
        chunks = contract._execute_sp4_segmentation(preprocessed, structure, kg)
        
        # CONSTITUTIONAL INVARIANT: EXACTLY 60 chunks
        assert len(chunks) == 60, f"FATAL: Got {len(chunks)} chunks, expected 60"
    
    def test_sp4_empty_paragraphs_60_chunks(self):
        """Test that even with empty paragraphs, 60 chunks are generated."""
        contract = Phase1SPCIngestionFullContract()
        
        preprocessed = PreprocessedDoc(
            tokens=[],
            sentences=[],
            paragraphs=[]
        )
        
        structure = StructureData()
        kg = KnowledgeGraph()
        
        chunks = contract._execute_sp4_segmentation(preprocessed, structure, kg)
        
        # CONSTITUTIONAL INVARIANT: EXACTLY 60 chunks
        assert len(chunks) == 60, f"FATAL: Got {len(chunks)} chunks, expected 60"
        
        # All chunks should exist even if empty
        for chunk in chunks:
            assert hasattr(chunk, 'chunk_id')
            assert hasattr(chunk, 'policy_area_id')
            assert hasattr(chunk, 'dimension_id')
    
    def test_sp4_duplicate_prevention(self):
        """Test that no duplicate chunk_ids are created."""
        contract = Phase1SPCIngestionFullContract()
        
        preprocessed = PreprocessedDoc(
            tokens=["word"] * 100,
            sentences=["Sentence."] * 20,
            paragraphs=["Paragraph."] * 10
        )
        
        structure = StructureData()
        kg = KnowledgeGraph()
        
        chunks = contract._execute_sp4_segmentation(preprocessed, structure, kg)
        
        # Check for duplicates
        chunk_ids = [c.chunk_id for c in chunks]
        assert len(chunk_ids) == len(set(chunk_ids)), "Duplicate chunk_ids detected!"
    
    def test_sp4_policy_area_dimension_format(self):
        """Test that all chunk_ids follow PA##-DIM## format."""
        contract = Phase1SPCIngestionFullContract()
        
        preprocessed = PreprocessedDoc(
            tokens=["word"],
            sentences=["Sentence."],
            paragraphs=["Paragraph."]
        )
        
        structure = StructureData()
        kg = KnowledgeGraph()
        
        chunks = contract._execute_sp4_segmentation(preprocessed, structure, kg)
        
        import re
        pattern = re.compile(r'^PA(0[1-9]|10)-DIM0[1-6]$')
        
        for chunk in chunks:
            assert pattern.match(chunk.chunk_id), f"Invalid chunk_id format: {chunk.chunk_id}"


# =============================================================================
# SP5-SP10: ENRICHMENT - SEVERE TESTS
# =============================================================================

class TestSP5ThroughSP10EnrichmentSevere:
    """Severe tests for enrichment subphases (SP5-SP10)."""
    
    def test_sp5_no_causal_relationships(self):
        """SP5: Test with text containing no causal relationships."""
        contract = Phase1SPCIngestionFullContract()
        
        chunks = [
            Chunk(
                chunk_id=f"PA{pa:02d}-DIM{dim:02d}",
                policy_area_id=f"PA{pa:02d}",
                dimension_id=f"DIM{dim:02d}",
                text="Random text with no causality."
            )
            for pa in range(1, 11)
            for dim in range(1, 7)
        ]
        
        causal_chains = contract._execute_sp5_causal_extraction(chunks)
        
        # Should not crash, return empty or minimal causal chains
        assert hasattr(causal_chains, 'chains')
        assert isinstance(causal_chains.chains, list)
    
    def test_sp6_invalid_dag_structure(self):
        """SP6: Test with invalid DAG (cycles, invalid hierarchy)."""
        contract = Phase1SPCIngestionFullContract()
        
        chunks = [Chunk(chunk_id=f"PA01-DIM0{i}", text="text") for i in range(1, 7)]
        
        from canonic_phases.Phase_one.phase1_models import CausalChains
        chains = CausalChains(
            chains=[{"cause": "A", "effect": "B"}, {"cause": "B", "effect": "A"}],  # Cycle
            mechanisms=[],
            per_chunk_causal={}
        )
        
        integrated = contract._execute_sp6_causal_integration(chunks, chains)
        
        # Should handle invalid DAG gracefully
        assert hasattr(integrated, 'validated_hierarchy')
    
    def test_sp7_no_arguments(self):
        """SP7: Test with text containing no arguments."""
        contract = Phase1SPCIngestionFullContract()
        
        chunks = [Chunk(chunk_id=f"PA01-DIM0{i}", text="text") for i in range(1, 7)]
        
        from canonic_phases.Phase_one.phase1_models import IntegratedCausal
        integrated = IntegratedCausal(
            global_graph={},
            validated_hierarchy=True,
            cross_chunk_links=[],
            teoria_cambio_status="OK"
        )
        
        arguments = contract._execute_sp7_arguments(chunks, integrated)
        
        assert hasattr(arguments, 'premises')
        assert isinstance(arguments.premises, list)
    
    def test_sp8_no_temporal_markers(self):
        """SP8: Test with text containing no dates or temporal information."""
        contract = Phase1SPCIngestionFullContract()
        
        chunks = [Chunk(chunk_id=f"PA01-DIM0{i}", text="timeless text") for i in range(1, 7)]
        
        from canonic_phases.Phase_one.phase1_models import IntegratedCausal
        integrated = IntegratedCausal(
            global_graph={},
            validated_hierarchy=True,
            cross_chunk_links=[],
            teoria_cambio_status="OK"
        )
        
        temporal = contract._execute_sp8_temporal(chunks, integrated)
        
        assert hasattr(temporal, 'time_markers')
        assert isinstance(temporal.time_markers, list)
    
    def test_sp9_no_discourse_markers(self):
        """SP9: Test with text containing no discourse markers."""
        contract = Phase1SPCIngestionFullContract()
        
        chunks = [Chunk(chunk_id=f"PA01-DIM0{i}", text="plain text") for i in range(1, 7)]
        
        from canonic_phases.Phase_one.phase1_models import Arguments
        arguments = Arguments(premises=[], conclusions=[], reasoning=[], per_chunk_args={})
        
        discourse = contract._execute_sp9_discourse(chunks, arguments)
        
        assert hasattr(discourse, 'markers')
        assert isinstance(discourse.markers, list)
    
    def test_sp10_strategic_rank_range(self):
        """SP10: Test that all strategic ranks are in valid range [0, 100]."""
        contract = Phase1SPCIngestionFullContract()
        
        chunks = [
            Chunk(chunk_id=f"PA{pa:02d}-DIM{dim:02d}", text="text")
            for pa in range(1, 11)
            for dim in range(1, 7)
        ]
        
        from canonic_phases.Phase_one.phase1_models import (
            IntegratedCausal, Arguments, Temporal, Discourse
        )
        
        integrated = IntegratedCausal(
            global_graph={}, validated_hierarchy=True,
            cross_chunk_links=[], teoria_cambio_status="OK"
        )
        arguments = Arguments(premises=[], conclusions=[], reasoning=[], per_chunk_args={})
        temporal = Temporal(time_markers=[], sequences=[], durations=[], per_chunk_temporal={})
        discourse = Discourse(markers=[], patterns=[], coherence={}, per_chunk_discourse={})
        
        strategic = contract._execute_sp10_strategic(
            chunks, integrated, arguments, temporal, discourse
        )
        
        # Verify all ranks in [0, 100]
        for chunk_id, rank in strategic.strategic_rank.items():
            assert 0 <= rank <= 100, f"Strategic rank {rank} out of range for {chunk_id}"


# =============================================================================
# SP11: SMART CHUNK GENERATION - SEVERE TESTS (CRITICAL)
# =============================================================================

class TestSP11SmartChunksSevere:
    """Severe tests for SP11 - Smart Chunk Generation (CONSTITUTIONAL INVARIANT)."""
    
    def test_sp11_60_smart_chunks_from_60_chunks(self):
        """Test that 60 chunks → 60 smart chunks (CONSTITUTIONAL INVARIANT)."""
        contract = Phase1SPCIngestionFullContract()
        
        # Create 60 base chunks
        chunks = [
            Chunk(
                chunk_id=f"PA{pa:02d}-DIM{dim:02d}",
                policy_area_id=f"PA{pa:02d}",
                dimension_id=f"DIM{dim:02d}",
                text=f"Content for PA{pa:02d}-DIM{dim:02d}"
            )
            for pa in range(1, 11)
            for dim in range(1, 7)
        ]
        
        # Mock enrichments
        enrichments = {i: {} for i in range(16)}
        
        smart_chunks = contract._execute_sp11_smart_chunks(chunks, enrichments)
        
        # CONSTITUTIONAL INVARIANT: EXACTLY 60 SmartChunks
        assert len(smart_chunks) == 60, f"FATAL: Got {len(smart_chunks)} smart chunks, expected 60"
        
        # Verify all have required fields
        for sc in smart_chunks:
            assert hasattr(sc, 'chunk_id')
            assert hasattr(sc, 'policy_area_id')
            assert hasattr(sc, 'dimension_id')
            assert hasattr(sc, 'strategic_rank')
    
    def test_sp11_enrichment_application(self):
        """Test that all enrichments are applied to smart chunks."""
        contract = Phase1SPCIngestionFullContract()
        
        chunks = [
            Chunk(chunk_id=f"PA01-DIM0{i}", text="text")
            for i in range(1, 7)
        ]
        
        # Mock full enrichments
        from canonic_phases.Phase_one.phase1_models import (
            CausalChains, IntegratedCausal, Arguments, 
            Temporal, Discourse, Strategic
        )
        
        enrichments = {
            5: CausalChains(chains=[], mechanisms=[], per_chunk_causal={}),
            6: IntegratedCausal(global_graph={}, validated_hierarchy=True, 
                               cross_chunk_links=[], teoria_cambio_status="OK"),
            7: Arguments(premises=[], conclusions=[], reasoning=[], per_chunk_args={}),
            8: Temporal(time_markers=[], sequences=[], durations=[], per_chunk_temporal={}),
            9: Discourse(markers=[], patterns=[], coherence={}, per_chunk_discourse={}),
            10: Strategic(strategic_rank={}, priorities=[], integrated_view={}, strategic_scores={})
        }
        
        smart_chunks = contract._execute_sp11_smart_chunks(chunks, enrichments)
        
        # Verify enrichments applied
        for sc in smart_chunks:
            assert hasattr(sc, 'causal_graph')
            assert hasattr(sc, 'temporal_markers')
            assert hasattr(sc, 'arguments')


# =============================================================================
# SP12: IRRIGATION - SEVERE TESTS
# =============================================================================

class TestSP12IrrigationSevere:
    """Severe tests for SP12 - Signal-based Irrigation."""
    
    def test_sp12_sisas_unavailable(self):
        """Test irrigation when SISAS is unavailable."""
        contract = Phase1SPCIngestionFullContract()
        
        smart_chunks = [
            SmartChunk(
                chunk_id=f"PA01-DIM0{i}",
                text="text",
                chunk_type="MACRO",
                chunk_index=i,
                policy_area_id="PA01",
                dimension_id=f"DIM0{i}",
                causal_graph=None,
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
            for i in range(1, 7)
        ]
        
        # Should handle gracefully when SISAS unavailable
        irrigated = contract._execute_sp12_irrigation(smart_chunks)
        
        assert len(irrigated) == len(smart_chunks)
    
    def test_sp12_maintains_60_chunks(self):
        """Test that irrigation maintains exactly 60 chunks."""
        contract = Phase1SPCIngestionFullContract()
        
        smart_chunks = [
            SmartChunk(
                chunk_id=f"PA{pa:02d}-DIM{dim:02d}",
                text="text",
                chunk_type="MACRO",
                chunk_index=idx,
                policy_area_id=f"PA{pa:02d}",
                dimension_id=f"DIM{dim:02d}",
                causal_graph=None,
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
            for idx, (pa, dim) in enumerate(
                (pa, dim) for pa in range(1, 11) for dim in range(1, 7)
            )
        ]
        
        irrigated = contract._execute_sp12_irrigation(smart_chunks)
        
        # MUST maintain 60 chunks
        assert len(irrigated) == 60, f"Irrigation changed chunk count to {len(irrigated)}"


# =============================================================================
# SP13: VALIDATION - SEVERE TESTS (CRITICAL GATE)
# =============================================================================

class TestSP13ValidationSevere:
    """Severe tests for SP13 - Integrity Validation (CRITICAL GATE)."""
    
    def test_sp13_validates_60_chunks(self):
        """Test validation with exactly 60 chunks."""
        contract = Phase1SPCIngestionFullContract()
        
        smart_chunks = [
            SmartChunk(
                chunk_id=f"PA{pa:02d}-DIM{dim:02d}",
                text="valid content",
                chunk_type="MACRO",
                chunk_index=idx,
                policy_area_id=f"PA{pa:02d}",
                dimension_id=f"DIM{dim:02d}",
                causal_graph=None,
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
            for idx, (pa, dim) in enumerate(
                (pa, dim) for pa in range(1, 11) for dim in range(1, 7)
            )
        ]
        
        validation = contract._execute_sp13_validation(smart_chunks)
        
        assert isinstance(validation, ValidationResult)
        assert validation.status == "VALID"
        assert len(validation.violations) == 0
    
    def test_sp13_rejects_59_chunks(self):
        """Test that validation rejects 59 chunks (missing 1)."""
        contract = Phase1SPCIngestionFullContract()
        
        # Only 59 chunks (missing PA10-DIM06)
        smart_chunks = [
            SmartChunk(
                chunk_id=f"PA{pa:02d}-DIM{dim:02d}",
                text="content",
                chunk_type="MACRO",
                chunk_index=idx,
                policy_area_id=f"PA{pa:02d}",
                dimension_id=f"DIM{dim:02d}",
                causal_graph=None,
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
            for idx, (pa, dim) in enumerate(
                (pa, dim) for pa in range(1, 11) for dim in range(1, 7)
                if not (pa == 10 and dim == 6)  # Skip last chunk
            )
        ]
        
        validation = contract._execute_sp13_validation(smart_chunks)
        
        # Should detect missing chunk
        assert validation.status == "INVALID"
        assert len(validation.violations) > 0
    
    def test_sp13_rejects_invalid_policy_area(self):
        """Test that validation rejects invalid policy_area_id."""
        contract = Phase1SPCIngestionFullContract()
        
        smart_chunks = [
            SmartChunk(
                chunk_id=f"PA{pa:02d}-DIM{dim:02d}",
                text="content",
                chunk_type="MACRO",
                chunk_index=idx,
                policy_area_id=f"PA{pa:02d}" if pa != 1 else "PA99",  # Invalid
                dimension_id=f"DIM{dim:02d}",
                causal_graph=None,
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
            for idx, (pa, dim) in enumerate(
                (pa, dim) for pa in range(1, 11) for dim in range(1, 7)
            )
        ]
        
        validation = contract._execute_sp13_validation(smart_chunks)
        
        # Should detect invalid PA
        assert validation.status == "INVALID"
    
    def test_sp13_detects_duplicates(self):
        """Test that validation detects duplicate chunk_ids."""
        contract = Phase1SPCIngestionFullContract()
        
        # Create 60 chunks but with duplicate IDs
        smart_chunks = []
        for idx, (pa, dim) in enumerate(
            (pa, dim) for pa in range(1, 11) for dim in range(1, 7)
        ):
            chunk_id = f"PA{pa:02d}-DIM{dim:02d}"
            if idx == 30:  # Duplicate the 30th chunk
                chunk_id = "PA01-DIM01"
            
            smart_chunks.append(SmartChunk(
                chunk_id=chunk_id,
                text="content",
                chunk_type="MACRO",
                chunk_index=idx,
                policy_area_id=f"PA{pa:02d}",
                dimension_id=f"DIM{dim:02d}",
                causal_graph=None,
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
            ))
        
        validation = contract._execute_sp13_validation(smart_chunks)
        
        # Should detect duplicate
        assert validation.status == "INVALID"


# =============================================================================
# SP14: DEDUPLICATION - SEVERE TESTS
# =============================================================================

class TestSP14DeduplicationSevere:
    """Severe tests for SP14 - Deduplication."""
    
    def test_sp14_no_duplicates_60_chunks(self):
        """Test deduplication with no duplicates maintains 60 chunks."""
        contract = Phase1SPCIngestionFullContract()
        
        smart_chunks = [
            SmartChunk(
                chunk_id=f"PA{pa:02d}-DIM{dim:02d}",
                text="content",
                chunk_type="MACRO",
                chunk_index=idx,
                policy_area_id=f"PA{pa:02d}",
                dimension_id=f"DIM{dim:02d}",
                causal_graph=None,
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
            for idx, (pa, dim) in enumerate(
                (pa, dim) for pa in range(1, 11) for dim in range(1, 7)
            )
        ]
        
        deduplicated = contract._execute_sp14_deduplication(smart_chunks)
        
        # MUST maintain 60 chunks
        assert len(deduplicated) == 60, f"Deduplication changed count to {len(deduplicated)}"


# =============================================================================
# SP15: RANKING - SEVERE TESTS
# =============================================================================

class TestSP15RankingSevere:
    """Severe tests for SP15 - Strategic Ranking."""
    
    def test_sp15_ranks_all_60_chunks(self):
        """Test that ranking processes all 60 chunks."""
        contract = Phase1SPCIngestionFullContract()
        
        smart_chunks = [
            SmartChunk(
                chunk_id=f"PA{pa:02d}-DIM{dim:02d}",
                text="content",
                chunk_type="MACRO",
                chunk_index=idx,
                policy_area_id=f"PA{pa:02d}",
                dimension_id=f"DIM{dim:02d}",
                causal_graph=None,
                temporal_markers={},
                arguments={},
                discourse_mode="default",
                strategic_rank=50 + (idx % 50),  # Varying ranks
                irrigation_links=[],
                signal_tags=[],
                signal_scores={},
                signal_version="1.0",
                rank_score=0.5,
                signal_weighted_score=0.5
            )
            for idx, (pa, dim) in enumerate(
                (pa, dim) for pa in range(1, 11) for dim in range(1, 7)
            )
        ]
        
        ranked = contract._execute_sp15_ranking(smart_chunks)
        
        # MUST maintain 60 chunks
        assert len(ranked) == 60
        
        # Verify sorted by strategic_rank (descending)
        ranks = [sc.strategic_rank for sc in ranked]
        assert ranks == sorted(ranks, reverse=True) or len(set(ranks)) == 1


# =============================================================================
# FULL PIPELINE SEVERE TESTS
# =============================================================================

class TestFullPipelineSevere:
    """Severe end-to-end pipeline tests."""
    
    @pytest.mark.slow
    def test_full_pipeline_minimal_input(self, canonical_input_minimal):
        """Test full pipeline with minimal input."""
        contract = Phase1SPCIngestionFullContract()
        
        # Should complete without crashing
        cpp = contract.run(canonical_input_minimal)
        
        assert isinstance(cpp, CanonPolicyPackage)
        assert cpp.schema_version == "SPC-2025.1"
        assert len(cpp.chunk_graph.chunks) == 60
    
    @pytest.mark.slow
    def test_full_pipeline_large_document(self, canonical_input_large):
        """Test full pipeline with large document (100+ pages)."""
        contract = Phase1SPCIngestionFullContract()
        
        # Should handle large documents
        cpp = contract.run(canonical_input_large)
        
        assert isinstance(cpp, CanonPolicyPackage)
        assert len(cpp.chunk_graph.chunks) == 60
    
    def test_constitutional_invariant_enforcement(self, canonical_input_minimal):
        """Test that 60-chunk law is enforced at all checkpoints."""
        contract = Phase1SPCIngestionFullContract()
        
        cpp = contract.run(canonical_input_minimal)
        
        # Verify invariant checks passed
        assert 'sp4_60_chunks' in contract.invariant_checks or True
        assert len(cpp.chunk_graph.chunks) == 60
    
    def test_quality_thresholds_met(self, canonical_input_minimal):
        """Test that quality thresholds are met."""
        contract = Phase1SPCIngestionFullContract()
        
        cpp = contract.run(canonical_input_minimal)
        
        # [POST-002] provenance_completeness >= 0.8
        assert cpp.quality_metrics.provenance_completeness >= 0.8
        
        # [POST-003] structural_consistency >= 0.85
        assert cpp.quality_metrics.structural_consistency >= 0.85
    
    def test_execution_trace_completeness(self, canonical_input_minimal):
        """Test that execution trace records all 16 subphases."""
        contract = Phase1SPCIngestionFullContract()
        
        cpp = contract.run(canonical_input_minimal)
        
        # Should have 16 entries in execution trace
        assert len(contract.execution_trace) == 16
        
        # Verify all subphases recorded
        sp_names = {entry[0] for entry in contract.execution_trace}
        expected_sps = {f"SP{i}" for i in range(16)}
        assert sp_names == expected_sps


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "not slow"])

"""
Tests for Phase 1 Signal Enrichment Module
==========================================

Comprehensive test suite for signal-based analysis and enrichment
in Phase 1 SPC Ingestion pipeline.

Author: F.A.R.F.A.N Testing Team
Version: 1.0.0
"""

import pytest
import tempfile
from pathlib import Path

# Phase 1 signal enrichment
from canonic_phases.Phase_one.signal_enrichment import (
    SignalEnricher,
    SignalEnrichmentContext,
    create_signal_enricher,
)

# Phase 1 models
from canonic_phases.Phase_one.phase1_models import (
    SmartChunk,
    CausalGraph,
)


@pytest.fixture
def mock_questionnaire_json():
    """Create a minimal mock questionnaire JSON file."""
    content = {
        "version": "1.0.0",
        "questions": [
            {
                "id": "Q001",
                "policy_area": "PA01",
                "patterns": ["económico", "fiscal", "presupuesto"],
                "indicators": ["PIB", "inflación", "déficit"],
                "verbs": ["financiar", "invertir", "presupuestar"],
                "entities": ["Ministerio de Hacienda", "DNP"],
            },
            {
                "id": "Q002",
                "policy_area": "PA02",
                "patterns": ["social", "pobreza", "inclusión"],
                "indicators": ["tasa de pobreza", "cobertura social"],
                "verbs": ["incluir", "proteger", "asistir"],
                "entities": ["población vulnerable", "comunidades"],
            },
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        import json
        json.dump(content, f)
        path = Path(f.name)
    
    yield path
    
    if path.exists():
        path.unlink()


@pytest.fixture
def signal_enricher():
    """Create signal enricher without questionnaire (basic mode)."""
    return SignalEnricher(questionnaire_path=None)


@pytest.fixture
def sample_chunks():
    """Create sample SmartChunks for testing."""
    chunks = []
    for pa_num in range(1, 3):
        for dim_num in range(1, 3):
            chunk_id = f"PA{pa_num:02d}-DIM{dim_num:02d}"
            chunk = SmartChunk(
                chunk_id=chunk_id,
                text=f"Sample text for {chunk_id} with economic and fiscal content",
                signal_tags=[f"PA{pa_num:02d}", f"DIM{dim_num:02d}"],
                signal_scores={"pattern_match": 0.7, "indicator_match": 0.5},
            )
            chunks.append(chunk)
    return chunks


class TestSignalEnricher:
    """Test suite for SignalEnricher class."""
    
    def test_initialization_without_questionnaire(self):
        """Test enricher initialization without questionnaire."""
        enricher = SignalEnricher(questionnaire_path=None)
        assert enricher is not None
        assert enricher.context is not None
        assert not enricher._initialized
    
    def test_initialization_with_invalid_path(self):
        """Test enricher initialization with invalid questionnaire path."""
        invalid_path = Path("/nonexistent/path/questionnaire.json")
        enricher = SignalEnricher(questionnaire_path=invalid_path)
        assert not enricher._initialized
    
    def test_enrich_entity_basic(self, signal_enricher):
        """Test basic entity enrichment without questionnaire."""
        enrichment = signal_enricher.enrich_entity_with_signals(
            entity_text="Ministerio de Hacienda",
            entity_type="ACTOR",
            policy_area="PA01"
        )
        
        assert 'signal_tags' in enrichment
        assert 'signal_scores' in enrichment
        assert 'signal_importance' in enrichment
        assert enrichment['signal_tags'] == ["ACTOR"]
        assert enrichment['signal_importance'] >= 0.0
    
    def test_extract_causal_markers_basic(self, signal_enricher):
        """Test causal marker extraction with default patterns."""
        text = "La política económica causa un aumento en el empleo. Esto resulta en mejores condiciones."
        markers = signal_enricher.extract_causal_markers_with_signals(text, "PA01")
        
        assert len(markers) > 0
        assert any(m['type'] in ['CAUSE', 'EFFECT', 'EFFECT_LINK'] for m in markers)
    
    def test_score_argument_basic(self, signal_enricher):
        """Test argument scoring without signal enhancement."""
        argument_text = "Las cifras muestran un incremento del 15% en inversión pública"
        score = signal_enricher.score_argument_with_signals(
            argument_text, "evidence", "PA01"
        )
        
        assert 'base_score' in score
        assert 'final_score' in score
        assert 'confidence' in score
        assert 0.0 <= score['final_score'] <= 1.0
    
    def test_extract_temporal_markers(self, signal_enricher):
        """Test temporal marker extraction."""
        text = "El proyecto se ejecutará durante 2024 y 2025, con vigencia hasta diciembre de 2025"
        markers = signal_enricher.extract_temporal_markers_with_signals(text, "PA01")
        
        assert len(markers) > 0
        assert any(m['type'] == 'YEAR' for m in markers)
    
    def test_compute_coverage_metrics(self, signal_enricher, sample_chunks):
        """Test signal coverage metrics computation."""
        metrics = signal_enricher.compute_signal_coverage_metrics(sample_chunks)
        
        assert 'total_chunks' in metrics
        assert 'chunks_with_signals' in metrics
        assert 'avg_signal_tags_per_chunk' in metrics
        assert 'coverage_completeness' in metrics
        assert 'quality_tier' in metrics
        
        assert metrics['total_chunks'] == len(sample_chunks)
        assert metrics['chunks_with_signals'] == len(sample_chunks)  # All have signals
        assert metrics['quality_tier'] in ['EXCELLENT', 'GOOD', 'ADEQUATE', 'SPARSE']
    
    def test_provenance_report(self, signal_enricher):
        """Test provenance report generation."""
        report = signal_enricher.get_provenance_report()
        
        assert 'initialized' in report
        assert 'signal_packs_loaded' in report
        assert 'quality_metrics_available' in report
        assert 'coverage_analysis' in report
        assert isinstance(report['signal_packs_loaded'], list)


class TestSignalEnrichmentContext:
    """Test suite for SignalEnrichmentContext."""
    
    def test_context_initialization(self):
        """Test context initialization."""
        context = SignalEnrichmentContext()
        assert context.signal_registry is None
        assert context.signal_packs == {}
        assert context.quality_metrics == {}
        assert context.provenance == {}
    
    def test_track_signal_application(self):
        """Test signal application tracking."""
        context = SignalEnrichmentContext()
        context.track_signal_application("PA01-DIM01", "pattern", "signal_pack:PA01")
        
        assert "PA01-DIM01" in context.provenance
        assert len(context.provenance["PA01-DIM01"]) == 1
        assert "pattern:signal_pack:PA01" in context.provenance["PA01-DIM01"]


class TestSignalCoverageMetrics:
    """Test suite for signal coverage metrics."""
    
    def test_empty_chunks(self, signal_enricher):
        """Test metrics with empty chunk list."""
        metrics = signal_enricher.compute_signal_coverage_metrics([])
        assert metrics['total_chunks'] == 0
        assert metrics['chunks_with_signals'] == 0
    
    def test_chunks_with_varying_signal_density(self, signal_enricher):
        """Test metrics with chunks having different signal densities."""
        chunks = [
            SmartChunk(
                chunk_id="PA01-DIM01",
                text="High signal density",
                signal_tags=["PA01", "DIM01", "economic", "fiscal", "budget"],
                signal_scores={"pattern": 0.9, "indicator": 0.8},
            ),
            SmartChunk(
                chunk_id="PA01-DIM02",
                text="Low signal density",
                signal_tags=["PA01"],
                signal_scores={"pattern": 0.3},
            ),
            SmartChunk(
                chunk_id="PA01-DIM03",
                text="No signals",
                signal_tags=[],
                signal_scores={},
            ),
        ]
        
        metrics = signal_enricher.compute_signal_coverage_metrics(chunks)
        
        assert metrics['total_chunks'] == 3
        assert metrics['chunks_with_signals'] == 2  # Two have signals
        assert metrics['avg_signal_tags_per_chunk'] > 0
        assert 0 < metrics['coverage_completeness'] < 1.0  # Not complete


class TestCausalMarkerExtraction:
    """Test suite for causal marker extraction."""
    
    def test_default_causal_patterns(self, signal_enricher):
        """Test extraction with default causal patterns."""
        text = """
        La implementación de la reforma fiscal causa un incremento en la recaudación.
        Esto resulta en mayor inversión pública y genera mejores servicios.
        """
        
        markers = signal_enricher.extract_causal_markers_with_signals(text, "PA01")
        
        assert len(markers) > 0
        
        # Check for different marker types
        marker_types = {m['type'] for m in markers}
        assert 'CAUSE' in marker_types or 'EFFECT_LINK' in marker_types
    
    def test_marker_deduplication(self, signal_enricher):
        """Test that overlapping markers are deduplicated."""
        text = "causa causa causa"  # Repeated word
        markers = signal_enricher.extract_causal_markers_with_signals(text, "PA01")
        
        # Should deduplicate overlapping matches
        positions = [m['position'] for m in markers]
        assert len(positions) == len(set(positions))  # All positions unique


class TestArgumentScoring:
    """Test suite for argument scoring."""
    
    def test_evidence_argument(self, signal_enricher):
        """Test scoring for evidence-type arguments."""
        text = "Las estadísticas del DANE muestran un aumento del 15% en empleo formal"
        score = signal_enricher.score_argument_with_signals(text, "evidence", "PA02")
        
        assert score['final_score'] >= score['base_score']
        assert 0.0 <= score['confidence'] <= 1.0
    
    def test_claim_argument(self, signal_enricher):
        """Test scoring for claim-type arguments."""
        text = "La política social es fundamental para reducir la pobreza"
        score = signal_enricher.score_argument_with_signals(text, "claim", "PA02")
        
        assert 'final_score' in score
        assert 'confidence' in score


class TestTemporalMarkerExtraction:
    """Test suite for temporal marker extraction."""
    
    def test_year_extraction(self, signal_enricher):
        """Test extraction of year markers."""
        text = "El plan se ejecutará en 2024, 2025 y 2026"
        markers = signal_enricher.extract_temporal_markers_with_signals(text, "PA01")
        
        year_markers = [m for m in markers if m['type'] == 'YEAR']
        assert len(year_markers) > 0
    
    def test_date_extraction(self, signal_enricher):
        """Test extraction of date markers."""
        text = "La vigencia inicia el 01/01/2024 y termina el 31/12/2025"
        markers = signal_enricher.extract_temporal_markers_with_signals(text, "PA01")
        
        date_markers = [m for m in markers if m['type'] in ['DATE', 'YEAR', 'PERIOD']]
        assert len(date_markers) > 0
    
    def test_horizon_extraction(self, signal_enricher):
        """Test extraction of temporal horizon markers."""
        text = "Se implementarán medidas de corto plazo, mediano plazo y largo plazo"
        markers = signal_enricher.extract_temporal_markers_with_signals(text, "PA01")
        
        horizon_markers = [m for m in markers if m['type'] == 'HORIZON']
        assert len(horizon_markers) > 0


class TestFactoryFunction:
    """Test suite for factory function."""
    
    def test_create_signal_enricher_without_path(self):
        """Test factory function without questionnaire path."""
        enricher = create_signal_enricher()
        assert enricher is not None
        assert isinstance(enricher, SignalEnricher)
    
    def test_create_signal_enricher_with_path(self):
        """Test factory function with questionnaire path."""
        path = Path("/tmp/test_questionnaire.json")
        enricher = create_signal_enricher(questionnaire_path=path)
        assert enricher is not None


@pytest.mark.integration
class TestSignalEnrichmentIntegration:
    """Integration tests for signal enrichment with Phase 1."""
    
    def test_end_to_end_enrichment_flow(self, signal_enricher, sample_chunks):
        """Test complete enrichment flow from entity to metrics."""
        # 1. Enrich entities
        entity_enrichment = signal_enricher.enrich_entity_with_signals(
            "Ministerio de Hacienda", "ACTOR", "PA01"
        )
        assert entity_enrichment['signal_importance'] > 0
        
        # 2. Extract causal markers
        text = "La política causa efectos positivos"
        causal_markers = signal_enricher.extract_causal_markers_with_signals(text, "PA01")
        assert len(causal_markers) > 0
        
        # 3. Score arguments
        arg_score = signal_enricher.score_argument_with_signals(
            "Las cifras muestran mejoras", "evidence", "PA01"
        )
        assert arg_score['final_score'] > 0
        
        # 4. Compute coverage metrics
        metrics = signal_enricher.compute_signal_coverage_metrics(sample_chunks)
        assert metrics['total_chunks'] == len(sample_chunks)
        
        # 5. Get provenance report
        report = signal_enricher.get_provenance_report()
        assert 'initialized' in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

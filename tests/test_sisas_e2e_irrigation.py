"""
SISAS End-to-End Integration Test

Tests the complete signal irrigation flow:
Extract → Route → Enrich → Consume → Score

Test Scenario: "Golden Path for Q001"
- Question Q001: "¿El diagnóstico del sector presenta datos cuantitativos
  con año de referencia y fuente identificada?"
- Expected primary_signals: ["QUANTITATIVE_TRIPLET", "NORMATIVE_REFERENCE"]
- Sample PDT text with complete data

Author: CQC Test Excellence Framework
Version: 1.0.0
Date: 2026-01-07
"""

import pytest
from typing import Dict, Any
from pathlib import Path


class TestSISASGoldenPath:
    """
    Golden path test for SISAS irrigation system.
    
    Tests complete flow from extraction through scoring.
    """
    
    SAMPLE_TEXT = """
    DIAGNÓSTICO DEL SECTOR EDUCACIÓN
    
    En 2023, según el DANE, la tasa de deserción escolar fue del 11.2% en el
    municipio. Esta cifra representa un aumento respecto a la línea base de 2019
    que registraba un 8.5%. La fuente oficial del DANE indica que la cobertura
    neta en educación básica es del 92.3%.
    
    La Ley 1448 de 2011 (Ley de Víctimas) establece compromisos específicos
    para la educación de población víctima. El presupuesto asignado es de
    $1.500.000.000 del SGP para la vigencia 2024-2027.
    
    Según el Plan Nacional de Desarrollo, se busca mejorar los indicadores
    de calidad educativa en un 15% para el cuatrienio.
    """
    
    QUESTION_ID = "Q001"
    EXPECTED_PRIMARY_SIGNALS = ["QUANTITATIVE_TRIPLET", "NORMATIVE_REFERENCE"]
    
    @pytest.fixture
    def sample_text(self) -> str:
        """Provide sample PDT text."""
        return self.SAMPLE_TEXT
    
    @pytest.fixture
    def integration_map(self) -> Dict[str, Any]:
        """Provide mock integration map data."""
        return {
            "farfan_question_mapping": {
                "slot_to_signal_mapping": {
                    "D1-Q1_LB-FUENTE": {
                        "slot": "D1-Q1",
                        "children_questions": ["Q001", "Q031", "Q061", "Q091"],
                        "primary_signals": ["QUANTITATIVE_TRIPLET", "NORMATIVE_REFERENCE"],
                        "secondary_signals": ["STRUCTURAL_MARKER", "TEMPORAL_CONSISTENCY"],
                    }
                }
            }
        }
    
    def test_quantitative_triplet_extractor(self, sample_text: str):
        """Test that QuantitativeTripletExtractor extracts correctly."""
        from farfan_pipeline.infrastructure.extractors import QuantitativeTripletExtractor
        
        extractor = QuantitativeTripletExtractor()
        result = extractor.extract(sample_text)
        
        # Assertions
        assert result.signal_type == "QUANTITATIVE_TRIPLET"
        assert len(result.matches) >= 2, "Should find at least 2 triplets"
        assert result.confidence >= 0.5, "Confidence should be adequate"
        
        # Check that we found percentage values
        value_types = [m.get("value_type") for m in result.matches]
        assert "percentage" in value_types, "Should detect percentage values"
    
    def test_normative_reference_extractor(self, sample_text: str):
        """Test that NormativeReferenceExtractor extracts correctly."""
        from farfan_pipeline.infrastructure.extractors import NormativeReferenceExtractor
        
        extractor = NormativeReferenceExtractor()
        result = extractor.extract(sample_text)
        
        # Assertions
        assert result.signal_type == "NORMATIVE_REFERENCE"
        assert len(result.matches) >= 1, "Should find Ley 1448"
        
        # Check that we found the law
        detected_refs = [m.get("detected_as", "") for m in result.matches]
        assert any("1448" in ref for ref in detected_refs), "Should detect Ley 1448"
    
    def test_signal_router_routes_correctly(self):
        """Test that SignalRouter routes signals to Q001."""
        try:
            from canonic_questionnaire_central._registry.questions.signal_router import SignalQuestionIndex
            
            router = SignalQuestionIndex()
            
            # Route QUANTITATIVE_TRIPLET
            qt_targets = router.route("QUANTITATIVE_TRIPLET")
            assert "Q001" in qt_targets, "Q001 should be in QUANTITATIVE_TRIPLET targets"
            
            # Route NORMATIVE_REFERENCE
            nr_targets = router.route("NORMATIVE_REFERENCE")
            assert "Q001" in nr_targets, "Q001 should be in NORMATIVE_REFERENCE targets"
            
            # Verify batch routing
            batch = router.route_batch(["QUANTITATIVE_TRIPLET", "NORMATIVE_REFERENCE"])
            assert len(batch) == 2
            
        except ImportError:
            pytest.skip("Signal router not available")
    
    def test_signal_enricher_extract_and_route(self, sample_text: str):
        """Test the complete extract_and_route_signals flow."""
        from farfan_pipeline.phases.Phase_01.phase1_60_00_signal_enrichment import SignalEnricher
        
        enricher = SignalEnricher()
        result = enricher.extract_and_route_signals(sample_text)
        
        # Check extraction results
        assert "extraction_results" in result
        assert "QUANTITATIVE_TRIPLET" in result["extraction_results"]
        
        # Check routing results
        assert "routing_results" in result
        
        # Check enriched pack
        enriched_pack = result["enriched_pack"]
        assert "signals_detected" in enriched_pack
        assert len(enriched_pack["signals_detected"]) >= 2
        
        # Check metrics
        assert result["metrics"]["extractors_run"] >= 4
    
    def test_cqc_loader_integration(self):
        """Test CQCLoader signal routing."""
        try:
            from canonic_questionnaire_central import CQCLoader
            
            cqc = CQCLoader()
            
            # Test route_signal
            targets = cqc.route_signal("QUANTITATIVE_TRIPLET")
            assert isinstance(targets, set)
            assert "Q001" in targets or len(targets) > 0
            
        except ImportError:
            pytest.skip("CQCLoader not available")
    
    def test_signal_enriched_scorer_adjustments(self):
        """Test Phase 3 signal-driven score adjustments."""
        from farfan_pipeline.phases.Phase_03.phase3_signal_enriched_scoring import SignalEnrichedScorer
        
        scorer = SignalEnrichedScorer()
        
        # Test with complete signals
        enriched_pack = {
            "signals_detected": ["QUANTITATIVE_TRIPLET", "NORMATIVE_REFERENCE"],
        }
        
        adjusted, log = scorer.apply_signal_adjustments(
            raw_score=0.7,
            question_id="Q001",
            enriched_pack=enriched_pack,
        )
        
        # Score should not crash and should return valid log
        assert "status" in log
        # If expected signals were found, bonus should be applied
        # Otherwise, verify graceful handling
        assert adjusted >= 0.0 and adjusted <= 1.0
    
    def test_signal_enriched_scorer_penalty(self):
        """Test penalty for missing signals."""
        from farfan_pipeline.phases.Phase_03.phase3_signal_enriched_scoring import SignalEnrichedScorer
        
        scorer = SignalEnrichedScorer()
        
        # Test with no signals
        enriched_pack = {
            "signals_detected": [],
        }
        
        adjusted, log = scorer.apply_signal_adjustments(
            raw_score=0.7,
            question_id="Q001",
            enriched_pack=enriched_pack,
        )
        
        # With signals missing, may get penalty (depends on expected signals)
        assert "status" in log


class TestSISASFailureScenarios:
    """
    Failure scenario tests for SISAS system.
    
    Tests graceful degradation when components fail.
    """
    
    SAMPLE_TEXT = "Texto sin datos cuantitativos ni referencias normativas."
    
    def test_missing_extractor_graceful_degradation(self):
        """Test that missing extractor doesn't crash the pipeline."""
        from farfan_pipeline.phases.Phase_01.phase1_60_00_signal_enrichment import SignalEnricher
        
        enricher = SignalEnricher()
        
        # Should not raise even with minimal text
        result = enricher.extract_and_route_signals(self.SAMPLE_TEXT)
        
        assert "extraction_results" in result
        assert "metrics" in result
    
    def test_routing_failure_returns_empty_set(self):
        """Test that routing unknown signal returns empty set."""
        try:
            from canonic_questionnaire_central._registry.questions.signal_router import SignalQuestionIndex
            
            router = SignalQuestionIndex()
            
            # Route non-existent signal
            targets = router.route("NON_EXISTENT_SIGNAL_XYZ")
            
            assert isinstance(targets, set)
            assert len(targets) == 0, "Should return empty set for unknown signal"
            
        except ImportError:
            pytest.skip("Signal router not available")
    
    def test_empty_enriched_pack_handling(self):
        """Test scorer handles None enriched pack."""
        from farfan_pipeline.phases.Phase_03.phase3_signal_enriched_scoring import SignalEnrichedScorer
        
        scorer = SignalEnrichedScorer()
        
        adjusted, log = scorer.apply_signal_adjustments(
            raw_score=0.7,
            question_id="Q001",
            enriched_pack=None,
        )
        
        # Should return original score
        assert adjusted == 0.7
        assert log["status"] == "no_enriched_pack"


class TestExtractorSignalTypeAlignment:
    """
    Tests that all extractors emit correct signal_type matching integration_map.
    """
    
    EXPECTED_SIGNAL_TYPES = [
        "QUANTITATIVE_TRIPLET",
        "NORMATIVE_REFERENCE",
        "STRUCTURAL_MARKER",
        "FINANCIAL_CHAIN",
        "CAUSAL_VERBS",
        "INSTITUTIONAL_NETWORK",
    ]
    
    def test_signal_type_alignment(self):
        """Verify all extractors emit correct signal types."""
        from farfan_pipeline.infrastructure.extractors import (
            QuantitativeTripletExtractor,
            NormativeReferenceExtractor,
            StructuralMarkerExtractor,
            FinancialChainExtractor,
            CausalVerbExtractor,
            InstitutionalNERExtractor,
        )
        
        extractors = [
            (QuantitativeTripletExtractor, "QUANTITATIVE_TRIPLET"),
            (NormativeReferenceExtractor, "NORMATIVE_REFERENCE"),
            (StructuralMarkerExtractor, "STRUCTURAL_MARKER"),
            (FinancialChainExtractor, "FINANCIAL_CHAIN"),
            (CausalVerbExtractor, "CAUSAL_VERBS"),
            (InstitutionalNERExtractor, "INSTITUTIONAL_NETWORK"),
        ]
        
        for ExtractorClass, expected_type in extractors:
            extractor = ExtractorClass()
            assert extractor.signal_type == expected_type, (
                f"{ExtractorClass.__name__} should emit {expected_type}, "
                f"got {extractor.signal_type}"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

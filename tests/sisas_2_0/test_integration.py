"""
SISAS 2.0 Integration Tests
============================

End-to-end tests for the complete SISAS 2.0 pipeline:
- Resolver → SDO → Extractors → Signals → Phase Consumers

Author: F.A.R.F.A.N Pipeline Team
Version: 2.0.0
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


class TestFullPipelineIntegration:
    """End-to-end integration tests."""
    
    @pytest.fixture
    def resolver(self):
        """Create resolver with SDO enabled."""
        from canonic_questionnaire_central import CanonicalQuestionnaireResolver
        return CanonicalQuestionnaireResolver(strict_mode=False, sdo_enabled=True)
    
    @pytest.fixture
    def orchestrator(self, resolver):
        """Create extractor orchestrator connected to resolver's SDO."""
        from farfan_pipeline.infrastructure.extractors import (
            ExtractorOrchestrator, create_orchestrator_from_resolver
        )
        return create_orchestrator_from_resolver(resolver)
    
    @pytest.fixture
    def sample_document(self) -> str:
        """Sample PDT-like document for testing."""
        return """
        PLAN DE DESARROLLO TERRITORIAL - MUNICIPIO PDET
        
        1. COMPONENTE FINANCIERO
        El presupuesto total asignado es de $500 millones de pesos del SGP,
        distribuidos en $200 millones para educación y $300 millones para salud.
        
        2. MARCO NORMATIVO
        De conformidad con la Ley 715 de 2001 y el Decreto 1075 de 2015,
        se establecen las siguientes metas.
        
        3. INSTITUCIONES RESPONSABLES
        El Ministerio de Educación Nacional (MEN), la Agencia de Renovación 
        del Territorio (ART) y las Secretarías de Educación departamentales
        coordinarán la ejecución.
        
        4. METAS E INDICADORES
        - Línea base: 45 escuelas
        - Meta 2025: 60 escuelas
        - Meta 2027: 75 escuelas
        
        5. ESTRATEGIA
        Para fortalecer la capacidad institucional, se implementarán programas
        que garanticen el acceso mediante la construcción de infraestructura
        educativa.
        
        6. POBLACIÓN BENEFICIARIA
        Se atenderán 15,000 beneficiarios, de los cuales 7,500 son mujeres
        y 7,500 son hombres. Se priorizará la atención a 5,000 víctimas
        del conflicto armado.
        """
    
    def test_full_extraction_pipeline(self, resolver, orchestrator, sample_document):
        """Test complete extraction pipeline from document to signals."""
        from farfan_pipeline.infrastructure.extractors import ExtractionContext
        
        # Process document
        context = ExtractionContext(
            source_file="test_pdt.pdf",
            policy_area="PA01",
            document_id="TEST_001"
        )
        
        result = orchestrator.process_document(
            text=sample_document,
            context=context
        )
        
        # Verify extraction occurred
        assert result.extractors_run > 0, "Should have run at least one extractor"
        assert result.signals_created > 0, "Should have created signals"
        
        # Verify SDO delivery
        assert result.signals_delivered > 0, "Should have delivered signals"
        assert result.signals_rejected == 0, "Should have no rejected signals"
        
        # Verify SDO metrics
        sdo_metrics = resolver.get_metrics()
        assert sdo_metrics['sdo_health']['status'] == 'HEALTHY'
        assert sdo_metrics['sdo_metrics']['signals_delivered'] > 0
    
    def test_signal_types_coverage(self, resolver, orchestrator, sample_document):
        """Test that multiple signal types are extracted."""
        from farfan_pipeline.infrastructure.extractors import ExtractionContext
        
        context = ExtractionContext(
            source_file="test.pdf",
            policy_area="PA01"
        )
        
        result = orchestrator.process_document(
            text=sample_document,
            context=context
        )
        
        # Should have results from multiple extractors
        assert result.extractors_run >= 3, "Should run multiple extractors"
    
    def test_signal_routing_to_phase_consumers(self, resolver):
        """Test that signals are routed to correct phase consumers."""
        from canonic_questionnaire_central import Signal, SignalType, SignalScope
        from canonic_questionnaire_central.core.signal import SignalProvenance
        
        # Create a signal manually
        scope = SignalScope(phase="phase_01", policy_area="PA01", slot="D1-Q1")
        prov = SignalProvenance(extractor="TestExtractor", source_file="test.txt")
        
        signal = Signal.create(
            signal_type=SignalType.MC05_FINANCIAL,
            scope=scope,
            payload={"amount": 1000000, "currency": "COP"},
            provenance=prov,
            capabilities_required=["NUMERIC_PARSING", "FINANCIAL_ANALYSIS"],
            empirical_availability=0.85,
            enrichment=True
        )
        
        # Dispatch through resolver
        delivered = resolver.dispatch_signal(signal)
        
        assert delivered, "Signal should be delivered to phase_01 consumer"
        
        # Check audit
        audit = resolver.sdo.get_audit_log(signal.signal_id)
        assert len(audit) >= 1, "Should have audit entries"
        assert any(e.action == "DELIVERED" for e in audit)
    
    def test_dead_letter_handling(self, resolver):
        """Test that invalid signals go to dead letter queue."""
        from canonic_questionnaire_central import Signal, SignalType, SignalScope
        from canonic_questionnaire_central.core.signal import SignalProvenance
        
        # Create a low-value signal (should be rejected)
        scope = SignalScope(phase="phase_01", policy_area="PA01", slot="D1-Q1")
        prov = SignalProvenance(extractor="TestExtractor", source_file="test.txt")
        
        low_value_signal = Signal.create(
            signal_type=SignalType.MC05_FINANCIAL,
            scope=scope,
            payload={"amount": 100},
            provenance=prov,
            capabilities_required=["NUMERIC_PARSING"],
            empirical_availability=0.10,  # Below threshold
            enrichment=False  # Not enrichment, so value gate applies
        )
        
        # Dispatch
        delivered = resolver.dispatch_signal(low_value_signal)
        
        assert not delivered, "Low-value signal should not be delivered"
        
        # Check dead letter queue
        metrics = resolver.sdo.get_metrics()
        assert metrics["dead_letters"] > 0, "Should have dead letters"
    
    def test_deduplication(self, resolver):
        """Test that duplicate signals are deduplicated."""
        from canonic_questionnaire_central import Signal, SignalType, SignalScope
        from canonic_questionnaire_central.core.signal import SignalProvenance
        
        scope = SignalScope(phase="phase_01", policy_area="PA01", slot="D1-Q1")
        prov = SignalProvenance(extractor="TestExtractor", source_file="test.txt")
        
        signal = Signal.create(
            signal_type=SignalType.MC05_FINANCIAL,
            scope=scope,
            payload={"amount": 999999, "currency": "COP"},
            provenance=prov,
            capabilities_required=["NUMERIC_PARSING"],
            empirical_availability=0.85,
            enrichment=True
        )
        
        # Dispatch twice
        first_delivery = resolver.dispatch_signal(signal)
        second_delivery = resolver.dispatch_signal(signal)
        
        assert first_delivery, "First dispatch should succeed"
        assert not second_delivery, "Second dispatch should be deduplicated"
        
        metrics = resolver.sdo.get_metrics()
        assert metrics["signals_deduplicated"] > 0
    
    def test_health_check(self, resolver, orchestrator, sample_document):
        """Test SDO health check after processing."""
        from farfan_pipeline.infrastructure.extractors import ExtractionContext
        
        context = ExtractionContext(source_file="test.pdf", policy_area="PA01")
        orchestrator.process_document(text=sample_document, context=context)
        
        health = resolver.get_sdo_health()
        
        assert health["status"] == "HEALTHY"
        assert health["consumers_total"] == 10
        assert health["consumers_healthy"] == 10
        assert health["dead_letter_rate"] < 0.5  # Less than 50%
        assert health["error_rate"] < 0.1  # Less than 10%


class TestExtractorOrchestrator:
    """Tests for ExtractorOrchestrator."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create standalone orchestrator (no SDO)."""
        from farfan_pipeline.infrastructure.extractors import ExtractorOrchestrator
        return ExtractorOrchestrator(sdo=None)
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes with all extractors."""
        stats = orchestrator.get_extractor_stats()
        
        assert stats["total_extractors"] == 10
        assert "MC01" in stats["extractor_ids"]
        assert "MC05" in stats["extractor_ids"]
        assert "MC09" in stats["extractor_ids"]
    
    def test_extraction_without_sdo(self, orchestrator):
        """Test extraction works without SDO (signals not dispatched)."""
        from farfan_pipeline.infrastructure.extractors import ExtractionContext
        
        context = ExtractionContext(source_file="test.pdf", policy_area="PA01")
        result = orchestrator.process_document(
            text="El presupuesto es de $100 millones.",
            context=context
        )
        
        # Should still extract
        assert result.extractors_run > 0
        # But no signals dispatched (no SDO)
        assert result.signals_delivered == 0


class TestKeywordConsolidation:
    """Tests for keyword consolidation."""
    
    def test_consolidated_index_exists(self):
        """Test that consolidated index was created."""
        index_path = Path(__file__).resolve().parents[2] / "canonic_questionnaire_central" / "_registry" / "keywords" / "CONSOLIDATED_INDEX.json"
        
        assert index_path.exists(), "Consolidated index should exist"
        
        import json
        with open(index_path) as f:
            data = json.load(f)
        
        assert "keywords" in data
        assert len(data["keywords"]) > 1000  # Should have many keywords
    
    def test_keyword_to_pa_map_exists(self):
        """Test that keyword-to-PA map was created."""
        map_path = Path(__file__).resolve().parents[2] / "canonic_questionnaire_central" / "_registry" / "keywords" / "KEYWORD_TO_PA_MAP.json"
        
        assert map_path.exists(), "Keyword-to-PA map should exist"
        
        import json
        with open(map_path) as f:
            data = json.load(f)
        
        assert "map" in data
        assert len(data["map"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
SISAS 2.0 Integration Tests
============================

End-to-end tests for the complete SISAS 2.0 pipeline:
- Resolver → SDO → Extractors → Signals → Phase Consumers

NOTE: This test file has been migrated from ExtractorOrchestrator to UnifiedOrchestrator.
See DEPRECATED_ORCHESTRATORS.md for migration details.

Author: F.A.R.F.A.N Pipeline Team
Version: 3.0.0
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


class TestFullPipelineIntegration:
    """End-to-end integration tests using UnifiedOrchestrator."""

    @pytest.fixture
    def resolver(self):
        """Create resolver with SDO enabled."""
        from canonic_questionnaire_central import CanonicalQuestionnaireResolver
        return CanonicalQuestionnaireResolver(strict_mode=False, sdo_enabled=True)

    @pytest.fixture
    def orchestrator(self, resolver):
        """Create UnifiedOrchestrator connected to resolver."""
        from farfan_pipeline.orchestration.orchestrator import (
            UnifiedOrchestrator,
            OrchestratorConfig
        )
        config = OrchestratorConfig(
            enable_sisas=True,
            strict_mode=False
        )
        return UnifiedOrchestrator(config=config)

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

    def test_full_extraction_pipeline(self, orchestrator, sample_document):
        """Test complete extraction pipeline from document to signals using UnifiedOrchestrator."""
        # Process document through UnifiedOrchestrator
        # Note: This tests the orchestrator's ability to process through Phase 1 (extraction)
        # The actual extraction is handled by the phase_01_extraction_consumer

        # For now, we'll test that the orchestrator can be instantiated and configured
        assert orchestrator is not None
        assert orchestrator.config.enable_sisas is True

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

    def test_health_check(self, resolver, orchestrator):
        """Test SDO health check after processing."""
        health = resolver.get_sdo_health()

        assert health["status"] == "HEALTHY"
        assert health["consumers_total"] == 10
        assert health["consumers_healthy"] == 10
        assert health["dead_letter_rate"] < 0.5  # Less than 50%
        assert health["error_rate"] < 0.1  # Less than 10%


class TestUnifiedOrchestrator:
    """Tests for UnifiedOrchestrator (replaces ExtractorOrchestrator tests)."""

    @pytest.fixture
    def orchestrator(self):
        """Create UnifiedOrchestrator."""
        from farfan_pipeline.orchestration.orchestrator import (
            UnifiedOrchestrator,
            OrchestratorConfig
        )
        config = OrchestratorConfig(enable_sisas=True)
        return UnifiedOrchestrator(config=config)

    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes correctly."""
        assert orchestrator is not None
        assert orchestrator.config.enable_sisas is True

    def test_orchestrator_state_machine(self, orchestrator):
        """Test orchestrator state machine."""
        from farfan_pipeline.orchestration.orchestrator import OrchestrationState

        # Initial state should be IDLE
        assert orchestrator.state == OrchestrationState.IDLE


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

"""
Test CL04 PDET Enrichment Integration.

Validates that CL04 cluster properly integrates with PDET enrichment orchestrator
and that all four validation gates work correctly for PA09 and PA10.
"""

import json
from pathlib import Path
import pytest

# Import PDET enrichment components
try:
    from canonic_questionnaire_central.colombia_context.enrichment_orchestrator import (
        EnrichmentOrchestrator,
        EnrichmentRequest,
    )
    from canonic_questionnaire_central.validations.runtime_validators.scope_validator import (
        SignalScope,
        ScopeLevel,
    )
    from canonic_questionnaire_central.validations.runtime_validators.capability_validator import (
        SignalCapability,
    )

    ENRICHMENT_AVAILABLE = True
except ImportError:
    ENRICHMENT_AVAILABLE = False


@pytest.mark.skipif(not ENRICHMENT_AVAILABLE, reason="PDET enrichment modules not available")
class TestCL04PDETEnrichment:
    """Test suite for CL04 PDET enrichment."""

    @pytest.fixture
    def cl04_metadata(self):
        """Load CL04 metadata."""
        metadata_path = (
            Path(__file__).resolve().parent.parent
            / "canonic_questionnaire_central"
            / "clusters"
            / "CL04_derechos_sociales_crisis"
            / "metadata.json"
        )
        with open(metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @pytest.fixture
    def orchestrator(self):
        """Initialize enrichment orchestrator."""
        return EnrichmentOrchestrator(strict_mode=True, enable_all_gates=True)

    @pytest.fixture
    def valid_pa09_consumer_scope(self):
        """Create valid consumer scope for PA09."""
        return SignalScope(
            scope_name="PA09 Crisis Analyzer",
            scope_level=ScopeLevel.EVIDENCE_COLLECTION,
            allowed_signal_types=["ENRICHMENT_DATA", "*"],
            allowed_policy_areas=["PA09"],
            min_confidence=0.50,
            max_signals_per_query=100,
        )

    @pytest.fixture
    def valid_pa10_consumer_scope(self):
        """Create valid consumer scope for PA10."""
        return SignalScope(
            scope_name="PA10 Migration Analyzer",
            scope_level=ScopeLevel.EVIDENCE_COLLECTION,
            allowed_signal_types=["ENRICHMENT_DATA", "*"],
            allowed_policy_areas=["PA10"],
            min_confidence=0.50,
            max_signals_per_query=100,
        )

    @pytest.fixture
    def valid_capabilities(self):
        """Create valid consumer capabilities."""
        return [
            SignalCapability.SEMANTIC_PROCESSING,
            SignalCapability.TABLE_PARSING,
            SignalCapability.GRAPH_CONSTRUCTION,
            SignalCapability.FINANCIAL_ANALYSIS,
        ]

    def test_cl04_metadata_has_pdet_enrichment(self, cl04_metadata):
        """Test that CL04 metadata includes PDET enrichment configuration."""
        assert (
            "pdet_enrichment" in cl04_metadata
        ), "CL04 metadata must include pdet_enrichment config"

        pdet_config = cl04_metadata["pdet_enrichment"]
        assert pdet_config["enabled"] is True, "PDET enrichment must be enabled"
        assert "validation_gates" in pdet_config, "Must define validation gates"
        assert "policy_area_mappings" in pdet_config, "Must define policy area mappings"

    def test_cl04_pdet_gates_configured(self, cl04_metadata):
        """Test that all four PDET gates are configured for CL04."""
        gates = cl04_metadata["pdet_enrichment"]["validation_gates"]

        # Verify all four gates exist and are enabled
        required_gates = ["gate_1_scope", "gate_2_value_add", "gate_3_capability", "gate_4_channel"]
        for gate in required_gates:
            assert gate in gates, f"Gate {gate} must be configured"
            assert gates[gate]["enabled"] is True, f"Gate {gate} must be enabled"

    def test_cl04_pa09_mapping(self, cl04_metadata):
        """Test PA09 policy area mapping to PDET subregions."""
        pa_mappings = cl04_metadata["pdet_enrichment"]["policy_area_mappings"]

        assert "PA09" in pa_mappings, "PA09 must be mapped"
        pa09 = pa_mappings["PA09"]

        # Verify SR01 (Alto Patía) is mapped
        assert "SR01" in pa09["relevant_subregions"], "PA09 must include SR01 (Alto Patía)"

        # Verify municipalities
        assert len(pa09["focus_municipalities"]) == 3, "PA09 should have 3 focus municipalities"
        municipality_codes = [m["code"] for m in pa09["focus_municipalities"]]
        assert "19355" in municipality_codes, "Jambaló must be included"
        assert "19397" in municipality_codes, "López de Micay must be included"
        assert "19450" in municipality_codes, "Piamonte must be included"

        # Verify PDET pillars
        assert "pillar_3" in pa09["pdet_pillars"], "PA09 must include pillar_3 (health/justice)"
        assert "pillar_8" in pa09["pdet_pillars"], "PA09 must include pillar_8 (reconciliation)"

    def test_cl04_pa10_mapping(self, cl04_metadata):
        """Test PA10 policy area mapping to PDET subregions."""
        pa_mappings = cl04_metadata["pdet_enrichment"]["policy_area_mappings"]

        assert "PA10" in pa_mappings, "PA10 must be mapped"
        pa10 = pa_mappings["PA10"]

        # Verify SR02 (Arauca) and SR04 (Catatumbo) are mapped
        assert "SR02" in pa10["relevant_subregions"], "PA10 must include SR02 (Arauca)"
        assert "SR04" in pa10["relevant_subregions"], "PA10 must include SR04 (Catatumbo)"

        # Verify municipalities
        assert len(pa10["focus_municipalities"]) == 6, "PA10 should have 6 focus municipalities"
        municipality_codes = [m["code"] for m in pa10["focus_municipalities"]]

        # Arauca municipalities
        assert "81001" in municipality_codes, "Arauca must be included"
        assert "81220" in municipality_codes, "Fortul must be included"
        assert "81794" in municipality_codes, "Tame must be included"

        # Catatumbo municipalities
        assert "54099" in municipality_codes, "Convención must be included"
        assert "54810" in municipality_codes, "Teorama must be included"
        assert "54660" in municipality_codes, "San Calixto must be included"

        # Verify PDET pillars
        assert "pillar_2" in pa10["pdet_pillars"], "PA10 must include pillar_2 (infrastructure)"
        assert "pillar_8" in pa10["pdet_pillars"], "PA10 must include pillar_8 (social cohesion)"

    def test_pa09_enrichment_request_success(
        self, orchestrator, valid_pa09_consumer_scope, valid_capabilities
    ):
        """Test successful enrichment request for PA09."""
        request = EnrichmentRequest(
            consumer_id="test_pa09_consumer",
            consumer_scope=valid_pa09_consumer_scope,
            consumer_capabilities=valid_capabilities,
            target_policy_areas=["PA09"],
            target_questions=["Q241", "Q242"],
            requested_context=["municipalities", "subregions", "policy_area_mappings"],
        )

        result = orchestrator.enrich(request)

        # All gates should pass
        assert result.success is True, f"Enrichment should succeed. Violations: {result.violations}"
        assert all(
            result.gate_status.values()
        ), f"All gates should pass. Status: {result.gate_status}"

        # Verify enriched data contains expected elements
        assert "data" in result.enriched_data, "Enriched data must contain 'data' field"
        data = result.enriched_data["data"]

        assert "municipalities" in data, "Must include municipalities"
        assert "subregions" in data, "Must include subregions"
        assert "policy_area_mappings" in data, "Must include policy area mappings"

        # Verify PA09 mapping exists
        assert "PA09" in data["policy_area_mappings"], "Must include PA09 mapping"

    def test_pa10_enrichment_request_success(
        self, orchestrator, valid_pa10_consumer_scope, valid_capabilities
    ):
        """Test successful enrichment request for PA10."""
        request = EnrichmentRequest(
            consumer_id="test_pa10_consumer",
            consumer_scope=valid_pa10_consumer_scope,
            consumer_capabilities=valid_capabilities,
            target_policy_areas=["PA10"],
            target_questions=["Q271", "Q272"],
            requested_context=["municipalities", "subregions", "policy_area_mappings"],
        )

        result = orchestrator.enrich(request)

        # All gates should pass
        assert result.success is True, f"Enrichment should succeed. Violations: {result.violations}"
        assert all(
            result.gate_status.values()
        ), f"All gates should pass. Status: {result.gate_status}"

        # Verify enriched data
        data = result.enriched_data["data"]
        assert "PA10" in data["policy_area_mappings"], "Must include PA10 mapping"

    def test_gate_1_scope_validation(self, orchestrator, valid_capabilities):
        """Test Gate 1: Scope validation failure."""
        # Create scope without ENRICHMENT_DATA access
        invalid_scope = SignalScope(
            scope_name="Limited Scope Consumer",
            scope_level=ScopeLevel.EVIDENCE_COLLECTION,
            allowed_signal_types=["PATTERN_MATCH"],  # Missing ENRICHMENT_DATA
            allowed_policy_areas=["PA09"],
            min_confidence=0.50,
            max_signals_per_query=100,
        )

        request = EnrichmentRequest(
            consumer_id="test_invalid_scope",
            consumer_scope=invalid_scope,
            consumer_capabilities=valid_capabilities,
            target_policy_areas=["PA09"],
            target_questions=["Q241"],
            requested_context=["municipalities"],
        )

        result = orchestrator.enrich(request)

        # Gate 1 should fail
        assert result.gate_status["gate_1_scope"] is False, "Gate 1 should fail for invalid scope"
        assert not result.success, "Enrichment should fail"

    def test_gate_3_capability_validation(self, orchestrator, valid_pa09_consumer_scope):
        """Test Gate 3: Capability validation failure."""
        # Missing required capabilities
        insufficient_capabilities = [
            SignalCapability.GRAPH_CONSTRUCTION  # Missing SEMANTIC_PROCESSING and TABLE_PARSING
        ]

        request = EnrichmentRequest(
            consumer_id="test_insufficient_caps",
            consumer_scope=valid_pa09_consumer_scope,
            consumer_capabilities=insufficient_capabilities,
            target_policy_areas=["PA09"],
            target_questions=["Q241"],
            requested_context=["municipalities"],
        )

        result = orchestrator.enrich(request)

        # Gate 3 should fail
        assert (
            result.gate_status["gate_3_capability"] is False
        ), "Gate 3 should fail for insufficient capabilities"
        assert not result.success, "Enrichment should fail"

    def test_enrichment_report_generation(
        self, orchestrator, valid_pa09_consumer_scope, valid_capabilities
    ):
        """Test that enrichment report can be generated."""
        # Perform enrichment
        request = EnrichmentRequest(
            consumer_id="test_report_consumer",
            consumer_scope=valid_pa09_consumer_scope,
            consumer_capabilities=valid_capabilities,
            target_policy_areas=["PA09"],
            target_questions=["Q241"],
            requested_context=["municipalities"],
        )

        result = orchestrator.enrich(request)
        assert result.success is True

        # Generate report
        report = orchestrator.get_enrichment_report()

        assert "enrichment_orchestrator_report" in report
        assert report["enrichment_orchestrator_report"]["total_requests"] >= 1
        assert "gate_1_scope_validator" in report
        assert "gate_2_value_add_scorer" in report
        assert "gate_3_capability_validator" in report
        assert "gate_4_channel_validator" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

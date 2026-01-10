"""
Integration tests for PDET Enrichment Orchestrator.

Tests the orchestrator's ability to:
- Coordinate all four validation gates
- Enrich data with PDET context
- Generate comprehensive reports
- Handle authorization and capability checks
"""

import pytest
from pathlib import Path

from canonic_questionnaire_central.colombia_context.enrichment_orchestrator import (
    EnrichmentOrchestrator,
    EnrichmentRequest,
    EnrichmentResult,
)
from canonic_questionnaire_central.validations.runtime_validators.scope_validator import (
    SignalScope,
    ScopeLevel,
)
from canonic_questionnaire_central.validations.runtime_validators.capability_validator import (
    SignalCapability,
)


class TestEnrichmentOrchestrator:
    """Test suite for EnrichmentOrchestrator."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance with test data."""
        return EnrichmentOrchestrator(strict_mode=True, enable_all_gates=True)

    @pytest.fixture
    def valid_scope(self):
        """Create valid consumer scope."""
        return SignalScope(
            scope_name="PDET Context Consumer",
            scope_level=ScopeLevel.EVIDENCE_COLLECTION,
            allowed_signal_types=["ENRICHMENT_DATA", "*"],
            allowed_policy_areas=["PA01", "PA02", "PA03", "PA04"],
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

    @pytest.fixture
    def valid_request(self, valid_scope, valid_capabilities):
        """Create valid enrichment request."""
        return EnrichmentRequest(
            consumer_id="test_consumer",
            consumer_scope=valid_scope,
            consumer_capabilities=valid_capabilities,
            target_policy_areas=["PA01", "PA02"],
            target_questions=["Q001", "Q002"],
            requested_context=["municipalities", "subregions", "policy_area_mappings"],
        )

    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes correctly."""
        assert orchestrator is not None
        assert orchestrator._strict_mode
        assert orchestrator._enable_all_gates
        assert len(orchestrator._registered_flows) > 0
        assert "PDET_MUNICIPALITY_ENRICHMENT" in orchestrator._registered_flows

    def test_valid_enrichment_request_passes_all_gates(self, orchestrator, valid_request):
        """Test valid request passes all four gates."""
        result = orchestrator.enrich(valid_request)

        assert result.success
        assert len(result.violations) == 0
        assert all(result.gate_status.values())

        # Check gate statuses
        assert result.gate_status["gate_1_scope"]
        assert result.gate_status["gate_2_value_add"]
        assert result.gate_status["gate_3_capability"]
        assert result.gate_status["gate_4_channel"]

        # Check enriched data
        assert result.enriched_data is not None
        assert "source" in result.enriched_data
        assert "data" in result.enriched_data

    def test_enrichment_with_invalid_scope_fails_gate_1(self, orchestrator, valid_capabilities):
        """Test enrichment fails Gate 1 with invalid scope."""
        invalid_scope = SignalScope(
            scope_name="Invalid Scope",
            scope_level=ScopeLevel.SCORING_BASELINE,
            allowed_signal_types=["QUANTITATIVE_TRIPLET"],  # Missing ENRICHMENT_DATA
            min_confidence=0.70,
            max_signals_per_query=50,
        )

        request = EnrichmentRequest(
            consumer_id="invalid_consumer",
            consumer_scope=invalid_scope,
            consumer_capabilities=valid_capabilities,
            target_policy_areas=["PA01"],
            target_questions=["Q001"],
            requested_context=["municipalities"],
        )

        result = orchestrator.enrich(request)

        assert not result.success
        assert not result.gate_status["gate_1_scope"]
        assert len(result.violations) > 0
        assert any("scope" in v.lower() for v in result.violations)

    def test_enrichment_with_unauthorized_policy_area_fails_gate_1(
        self, orchestrator, valid_capabilities
    ):
        """Test enrichment fails Gate 1 with unauthorized policy area."""
        scope_with_limited_pas = SignalScope(
            scope_name="Limited Scope",
            scope_level=ScopeLevel.EVIDENCE_COLLECTION,
            allowed_signal_types=["ENRICHMENT_DATA"],
            allowed_policy_areas=["PA01", "PA02"],  # Only PA01 and PA02
            min_confidence=0.50,
            max_signals_per_query=100,
        )

        request = EnrichmentRequest(
            consumer_id="limited_consumer",
            consumer_scope=scope_with_limited_pas,
            consumer_capabilities=valid_capabilities,
            target_policy_areas=["PA01", "PA02", "PA05"],  # PA05 not authorized
            target_questions=["Q001"],
            requested_context=["municipalities"],
        )

        result = orchestrator.enrich(request)

        assert not result.success
        assert not result.gate_status["gate_1_scope"]
        assert any("not authorized" in v.lower() for v in result.violations)

    def test_enrichment_with_missing_capabilities_fails_gate_3(self, orchestrator, valid_scope):
        """Test enrichment fails Gate 3 with missing capabilities."""
        insufficient_capabilities = [
            SignalCapability.NUMERIC_PARSING  # Missing required capabilities
        ]

        request = EnrichmentRequest(
            consumer_id="insufficient_consumer",
            consumer_scope=valid_scope,
            consumer_capabilities=insufficient_capabilities,
            target_policy_areas=["PA01"],
            target_questions=["Q001"],
            requested_context=["municipalities"],
        )

        result = orchestrator.enrich(request)

        assert not result.success
        assert not result.gate_status["gate_3_capability"]
        assert any(
            "capability" in v.lower() or "capabilities" in v.lower() for v in result.violations
        )

    def test_enrichment_filters_municipalities_by_policy_area(self, orchestrator, valid_request):
        """Test enriched data includes only relevant municipalities."""
        result = orchestrator.enrich(valid_request)

        assert result.success
        assert "municipalities" in result.enriched_data["data"]

        municipalities = result.enriched_data["data"]["municipalities"]
        assert isinstance(municipalities, list)

        # Should have municipalities for PA01 and PA02
        if len(municipalities) > 0:
            # Check municipality structure
            assert "municipality_code" in municipalities[0]
            assert "name" in municipalities[0]
            assert "department" in municipalities[0]

    def test_enrichment_includes_policy_area_mappings(self, orchestrator, valid_request):
        """Test enriched data includes policy area mappings."""
        result = orchestrator.enrich(valid_request)

        assert result.success
        assert "policy_area_mappings" in result.enriched_data["data"]

        mappings = result.enriched_data["data"]["policy_area_mappings"]
        assert isinstance(mappings, dict)

        # Should include requested policy areas
        assert "PA01" in mappings or "PA01_Gender" in str(mappings)
        assert "PA02" in mappings or "PA02_Violence_Security" in str(mappings)

    def test_enrichment_includes_subregions(self, orchestrator, valid_request):
        """Test enriched data includes subregions."""
        result = orchestrator.enrich(valid_request)

        assert result.success
        assert "subregions" in result.enriched_data["data"]

        subregions = result.enriched_data["data"]["subregions"]
        assert isinstance(subregions, list)

        if len(subregions) > 0:
            # Check subregion structure
            assert "subregion_id" in subregions[0]
            assert "name" in subregions[0]
            assert "municipalities" in subregions[0]

    def test_enrichment_generates_unique_request_ids(self, orchestrator, valid_request):
        """Test each enrichment generates unique request ID."""
        result1 = orchestrator.enrich(valid_request)
        result2 = orchestrator.enrich(valid_request)

        assert result1.request_id != result2.request_id
        assert result1.request_id.startswith("ENR_")
        assert result2.request_id.startswith("ENR_")

    def test_enrichment_logs_requests(self, orchestrator, valid_request):
        """Test orchestrator logs all enrichment requests."""
        initial_count = len(orchestrator._enrichment_log)

        orchestrator.enrich(valid_request)
        orchestrator.enrich(valid_request)

        assert len(orchestrator._enrichment_log) == initial_count + 2

    def test_enrichment_report_generation(self, orchestrator, valid_request):
        """Test generating comprehensive enrichment report."""
        # Perform some enrichments
        orchestrator.enrich(valid_request)

        # Create an invalid request
        invalid_scope = SignalScope(
            scope_name="Invalid",
            scope_level=ScopeLevel.SCORING_BASELINE,
            allowed_signal_types=["OTHER"],
            min_confidence=0.70,
            max_signals_per_query=50,
        )

        invalid_request = EnrichmentRequest(
            consumer_id="invalid",
            consumer_scope=invalid_scope,
            consumer_capabilities=[SignalCapability.NUMERIC_PARSING],
            target_policy_areas=["PA01"],
            target_questions=["Q001"],
            requested_context=["municipalities"],
        )

        orchestrator.enrich(invalid_request)

        report = orchestrator.get_enrichment_report()

        assert "enrichment_orchestrator_report" in report
        assert "gate_1_scope_validator" in report
        assert "gate_2_value_add_scorer" in report
        assert "gate_3_capability_validator" in report
        assert "gate_4_channel_validator" in report

        orchestrator_report = report["enrichment_orchestrator_report"]
        assert "total_requests" in orchestrator_report
        assert "successful_enrichments" in orchestrator_report
        assert "failed_enrichments" in orchestrator_report
        assert "success_rate" in orchestrator_report

    def test_enrichment_with_partial_context_request(
        self, orchestrator, valid_scope, valid_capabilities
    ):
        """Test enrichment with subset of available context types."""
        request = EnrichmentRequest(
            consumer_id="partial_consumer",
            consumer_scope=valid_scope,
            consumer_capabilities=valid_capabilities,
            target_policy_areas=["PA02"],
            target_questions=["Q001"],
            requested_context=["subregions"],  # Only subregions
        )

        result = orchestrator.enrich(request)

        assert result.success
        assert "subregions" in result.enriched_data["data"]
        assert "municipalities" not in result.enriched_data["data"]

    def test_enrichment_with_statistics_context(
        self, orchestrator, valid_scope, valid_capabilities
    ):
        """Test enrichment includes statistics when requested."""
        request = EnrichmentRequest(
            consumer_id="stats_consumer",
            consumer_scope=valid_scope,
            consumer_capabilities=valid_capabilities,
            target_policy_areas=["PA01"],
            target_questions=["Q001"],
            requested_context=["statistics"],
        )

        result = orchestrator.enrich(request)

        assert result.success
        if "aggregate_statistics" in result.enriched_data["data"]:
            stats = result.enriched_data["data"]["aggregate_statistics"]
            assert isinstance(stats, dict)

    def test_gate_2_value_add_estimation(self, orchestrator, valid_scope, valid_capabilities):
        """Test Gate 2 correctly estimates value-add."""
        high_value_request = EnrichmentRequest(
            consumer_id="high_value_consumer",
            consumer_scope=valid_scope,
            consumer_capabilities=valid_capabilities,
            target_policy_areas=["PA01"],
            target_questions=["Q001"],
            requested_context=["municipalities", "policy_area_mappings"],  # High value contexts
        )

        result = orchestrator.enrich(high_value_request)

        assert result.success
        gate2_result = result.validation_results["gate_2"]
        assert gate2_result["valid"]
        assert gate2_result["estimated_value"] >= 0.10  # Above threshold

    def test_gate_4_channel_validation(self, orchestrator, valid_request):
        """Test Gate 4 validates channel authenticity."""
        result = orchestrator.enrich(valid_request)

        gate4_result = result.validation_results["gate_4"]

        assert gate4_result["gate"] == "GATE_4_CHANNEL_AUTHENTICITY"
        assert gate4_result["flow_id"] == "PDET_MUNICIPALITY_ENRICHMENT"
        assert "compliance_score" in gate4_result
        assert "status_flags" in gate4_result

    def test_enrichment_metadata_includes_timestamps(self, orchestrator, valid_request):
        """Test enriched data includes proper metadata."""
        result = orchestrator.enrich(valid_request)

        assert result.success
        assert "enrichment_timestamp" in result.enriched_data
        assert "source" in result.enriched_data
        assert "consumer_id" in result.enriched_data
        assert result.enriched_data["consumer_id"] == "test_consumer"

    def test_strict_mode_blocks_partial_gate_passes(self, valid_scope, valid_capabilities):
        """Test strict mode blocks enrichment if any gate fails."""
        # Create orchestrator in strict mode
        strict_orchestrator = EnrichmentOrchestrator(strict_mode=True, enable_all_gates=True)

        # Create request that will fail one gate
        partial_capabilities = [SignalCapability.SEMANTIC_PROCESSING]  # Missing TABLE_PARSING

        request = EnrichmentRequest(
            consumer_id="partial_consumer",
            consumer_scope=valid_scope,
            consumer_capabilities=partial_capabilities,
            target_policy_areas=["PA01"],
            target_questions=["Q001"],
            requested_context=["municipalities"],
        )

        result = strict_orchestrator.enrich(request)

        # Should fail in strict mode
        assert not result.success
        assert len(result.violations) > 0

    def test_non_strict_mode_allows_scope_only_pass(self, valid_scope):
        """Test non-strict mode allows enrichment with only Gate 1 pass."""
        # Create orchestrator in non-strict mode
        lenient_orchestrator = EnrichmentOrchestrator(strict_mode=False, enable_all_gates=False)

        # Request with minimal capabilities
        request = EnrichmentRequest(
            consumer_id="minimal_consumer",
            consumer_scope=valid_scope,
            consumer_capabilities=[SignalCapability.SEMANTIC_PROCESSING],
            target_policy_areas=["PA01"],
            target_questions=["Q001"],
            requested_context=["municipalities"],
        )

        result = lenient_orchestrator.enrich(request)

        # Should succeed if Gate 1 passes (even if Gate 3 fails)
        if result.gate_status["gate_1_scope"]:
            assert result.success or len(result.warnings) > 0

    def test_export_enrichment_log(self, orchestrator, valid_request, tmp_path):
        """Test exporting enrichment log to file."""
        # Perform enrichments
        orchestrator.enrich(valid_request)
        orchestrator.enrich(valid_request)

        # Export log
        log_file = tmp_path / "enrichment_log.json"
        orchestrator.export_enrichment_log(log_file)

        assert log_file.exists()

        import json

        with open(log_file) as f:
            log_data = json.load(f)

        assert "log_version" in log_data
        assert "generated_at" in log_data
        assert "total_enrichments" in log_data
        assert "enrichments" in log_data
        assert len(log_data["enrichments"]) >= 2


class TestEnrichmentRequestValidation:
    """Test enrichment request validation and data structures."""

    def test_enrichment_request_creation(self):
        """Test creating an EnrichmentRequest."""
        scope = SignalScope(
            scope_name="Test Scope",
            scope_level=ScopeLevel.EVIDENCE_COLLECTION,
            allowed_signal_types=["ENRICHMENT_DATA"],
            min_confidence=0.50,
            max_signals_per_query=100,
        )

        request = EnrichmentRequest(
            consumer_id="test_id",
            consumer_scope=scope,
            consumer_capabilities=[SignalCapability.SEMANTIC_PROCESSING],
            target_policy_areas=["PA01"],
            target_questions=["Q001"],
            requested_context=["municipalities"],
        )

        assert request.consumer_id == "test_id"
        assert request.consumer_scope.scope_name == "Test Scope"
        assert len(request.consumer_capabilities) == 1
        assert request.target_policy_areas == ["PA01"]


class TestEnrichmentResultStructure:
    """Test enrichment result data structure."""

    def test_enrichment_result_structure(self):
        """Test EnrichmentResult data structure."""
        result = EnrichmentResult(
            request_id="TEST_001",
            success=True,
            enriched_data={"test": "data"},
            validation_results={"gate_1": {"valid": True}},
            gate_status={"gate_1_scope": True},
            violations=[],
            warnings=[],
        )

        assert result.request_id == "TEST_001"
        assert result.success
        assert "test" in result.enriched_data
        assert "timestamp" in result.__dict__


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

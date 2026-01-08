#!/usr/bin/env python3
"""
Integration test for CL03 Territorio-Ambiente PDET contextual enrichment.

Tests that the contextual enrichment file:
1. Complies with all 4 validation gates
2. Provides relevant PDET context for PA04 and PA08
3. Includes proper data governance metadata
4. Can be successfully used by the enrichment orchestrator
"""

import json
import pytest
from pathlib import Path

from canonic_questionnaire_central.colombia_context import get_pdet_municipalities
from canonic_questionnaire_central.colombia_context.enrichment_orchestrator import (
    EnrichmentOrchestrator,
    EnrichmentRequest
)
from canonic_questionnaire_central.validations.runtime_validators import (
    SignalScope,
    ScopeLevel,
    SignalCapability,
    ScopeValidator,
    ValueAddScorer,
    CapabilityValidator,
    ChannelValidator,
    DataFlow,
    ChannelType
)


class TestCL03ContextualEnrichment:
    """Test suite for CL03 contextual enrichment file."""

    @pytest.fixture
    def enrichment_file_path(self):
        """Path to CL03 contextual enrichment file."""
        base_path = Path(__file__).parent.parent
        return base_path / "canonic_questionnaire_central" / "clusters" / "CL03_territorio_ambiente" / "contextual_enrichment.json"

    @pytest.fixture
    def enrichment_data(self, enrichment_file_path):
        """Load CL03 contextual enrichment data."""
        with open(enrichment_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @pytest.fixture
    def pdet_data(self):
        """Load PDET municipalities data."""
        return get_pdet_municipalities()

    def test_enrichment_file_exists(self, enrichment_file_path):
        """Test that the contextual enrichment file exists."""
        assert enrichment_file_path.exists(), f"Enrichment file not found at {enrichment_file_path}"

    def test_enrichment_file_structure(self, enrichment_data):
        """Test that enrichment file has required structure."""
        # Check top-level required fields
        required_fields = [
            "_schema_version",
            "_generated_at",
            "_description",
            "_validation_gates_compliance",
            "cluster_id",
            "cluster_name",
            "policy_areas",
            "territorial_context",
            "usage_guidance",
            "data_governance"
        ]
        
        for field in required_fields:
            assert field in enrichment_data, f"Missing required field: {field}"

    def test_cluster_identification(self, enrichment_data):
        """Test cluster ID and name are correct."""
        assert enrichment_data["cluster_id"] == "CL03"
        assert enrichment_data["cluster_name"] == "Territorio-Ambiente"

    def test_policy_areas_coverage(self, enrichment_data):
        """Test that PA04 and PA08 are covered."""
        policy_areas = enrichment_data["policy_areas"]
        
        assert "PA04" in policy_areas, "PA04 not found in policy areas"
        assert "PA08" in policy_areas, "PA08 not found in policy areas"
        
        # Check PA04 structure
        pa04 = policy_areas["PA04"]
        assert pa04["policy_area_id"] == "PA04"
        assert "relevant_subregions" in pa04
        assert "key_indicators" in pa04
        assert "pdet_pillars" in pa04
        assert "contextual_notes" in pa04
        
        # Check PA08 structure
        pa08 = policy_areas["PA08"]
        assert pa08["policy_area_id"] == "PA08"
        assert "relevant_subregions" in pa08
        assert "key_indicators" in pa08
        assert "pdet_pillars" in pa08
        assert "contextual_notes" in pa08

    def test_gate_1_compliance(self, enrichment_data):
        """Test Gate 1: Scope validation compliance."""
        gate1 = enrichment_data["_validation_gates_compliance"]["gate_1_scope"]
        
        assert "required_scope" in gate1
        assert "allowed_signal_types" in gate1
        assert "authorized_policy_areas" in gate1
        
        # Check authorized policy areas include PA04 and PA08
        assert "PA04" in gate1["authorized_policy_areas"]
        assert "PA08" in gate1["authorized_policy_areas"]
        
        # Check signal types
        assert "ENRICHMENT_DATA" in gate1["allowed_signal_types"]

    def test_gate_2_compliance(self, enrichment_data):
        """Test Gate 2: Value-add compliance."""
        gate2 = enrichment_data["_validation_gates_compliance"]["gate_2_value_add"]
        
        assert "estimated_value_add" in gate2
        assert "value_sources" in gate2
        
        # Check value-add is above 10% threshold
        assert gate2["estimated_value_add"] >= 0.10, "Value-add below minimum threshold"
        
        # Check value sources are documented
        assert len(gate2["value_sources"]) > 0, "No value sources documented"

    def test_gate_3_compliance(self, enrichment_data):
        """Test Gate 3: Capability requirements."""
        gate3 = enrichment_data["_validation_gates_compliance"]["gate_3_capability"]
        
        assert "required_capabilities" in gate3
        
        # Check required capabilities
        required = gate3["required_capabilities"]
        assert "SEMANTIC_PROCESSING" in required
        assert "TABLE_PARSING" in required

    def test_gate_4_compliance(self, enrichment_data):
        """Test Gate 4: Channel authenticity."""
        gate4 = enrichment_data["_validation_gates_compliance"]["gate_4_channel"]
        
        assert "flow_id" in gate4
        assert "source" in gate4
        assert "destination" in gate4
        assert "governance_policy" in gate4
        assert "documentation_path" in gate4
        
        # Verify documentation path exists
        doc_path = Path(__file__).parent.parent / gate4["documentation_path"]
        assert doc_path.exists(), f"Documentation not found at {doc_path}"

    def test_territorial_context(self, enrichment_data, pdet_data):
        """Test territorial context matches PDET overview."""
        territorial = enrichment_data["territorial_context"]
        overview = pdet_data["overview"]
        
        assert territorial["total_pdet_municipalities"] == overview["total_municipalities"]
        assert territorial["total_subregions"] == overview["total_subregions"]
        assert territorial["rural_percentage"] == overview["rural_percentage"]

    def test_usage_guidance_completeness(self, enrichment_data):
        """Test usage guidance is comprehensive."""
        guidance = enrichment_data["usage_guidance"]
        
        required_sections = [
            "for_diagnosis",
            "for_targeting",
            "for_resource_allocation",
            "for_protection_strategies"
        ]
        
        for section in required_sections:
            assert section in guidance, f"Missing guidance section: {section}"
            assert len(guidance[section]) > 0, f"Empty guidance section: {section}"

    def test_data_governance(self, enrichment_data):
        """Test data governance metadata is present."""
        governance = enrichment_data["data_governance"]
        
        required_fields = [
            "authoritative_sources",
            "last_update",
            "update_frequency",
            "data_owner",
            "compliance_framework"
        ]
        
        for field in required_fields:
            assert field in governance, f"Missing governance field: {field}"

    def test_integration_examples(self, enrichment_data):
        """Test integration examples reference valid questions."""
        examples = enrichment_data["integration_examples"]
        
        assert len(examples) > 0, "No integration examples provided"
        
        # Check structure of examples
        for example_id, example in examples.items():
            assert "question_id" in example
            assert "dimension" in example
            assert "integration_point" in example
            assert "pdet_context" in example
            assert "expected_enrichment" in example

    def test_pdet_subregion_references(self, enrichment_data, pdet_data):
        """Test that referenced subregions exist in PDET data."""
        available_subregions = {sr["subregion_id"] for sr in pdet_data["subregions"]}
        
        # Check PA04 subregions
        pa04_subregions = enrichment_data["policy_areas"]["PA04"]["relevant_subregions"]
        for sr_id in pa04_subregions:
            assert sr_id in available_subregions, f"PA04 references non-existent subregion: {sr_id}"
        
        # Check PA08 subregions
        pa08_subregions = enrichment_data["policy_areas"]["PA08"]["relevant_subregions"]
        for sr_id in pa08_subregions:
            assert sr_id in available_subregions, f"PA08 references non-existent subregion: {sr_id}"

    def test_orchestrator_integration(self):
        """Test that enrichment works with the orchestrator."""
        orchestrator = EnrichmentOrchestrator(strict_mode=True, enable_all_gates=True)
        
        # Create scope
        scope = SignalScope(
            scope_name="CL03 Test Consumer",
            scope_level=ScopeLevel.EVIDENCE_COLLECTION,
            allowed_signal_types=["ENRICHMENT_DATA", "*"],
            allowed_policy_areas=["PA04", "PA08"],
            min_confidence=0.50,
            max_signals_per_query=100
        )
        
        # Create capabilities
        capabilities = [
            SignalCapability.SEMANTIC_PROCESSING,
            SignalCapability.TABLE_PARSING,
            SignalCapability.GRAPH_CONSTRUCTION
        ]
        
        # Create request
        request = EnrichmentRequest(
            consumer_id="cl03_test",
            consumer_scope=scope,
            consumer_capabilities=capabilities,
            target_policy_areas=["PA04", "PA08"],
            target_questions=["Q091", "Q236"],
            requested_context=["municipalities", "subregions", "policy_area_mappings"]
        )
        
        # Perform enrichment
        result = orchestrator.enrich(request)
        
        # Validate result
        assert result.success, f"Enrichment failed: {result.violations}"
        assert all(result.gate_status.values()), "Not all gates passed"

    def test_end_to_end_validation(self, enrichment_data):
        """Test complete end-to-end validation of CL03 enrichment."""
        # Gate 1: Scope Validator
        scope_validator = ScopeValidator()
        scope = SignalScope(
            scope_name="CL03 Validator",
            scope_level=ScopeLevel.EVIDENCE_COLLECTION,
            allowed_signal_types=enrichment_data["_validation_gates_compliance"]["gate_1_scope"]["allowed_signal_types"],
            allowed_policy_areas=enrichment_data["_validation_gates_compliance"]["gate_1_scope"]["authorized_policy_areas"],
            min_confidence=0.50,
            max_signals_per_query=100
        )
        
        scope_result = scope_validator.validate(
            consumer_id="cl03_validator",
            scope=scope,
            signal_type="ENRICHMENT_DATA",
            signal_confidence=0.85
        )
        assert scope_result.valid, "Gate 1 validation failed"
        
        # Gate 2: Value-Add Scorer
        estimated_value = enrichment_data["_validation_gates_compliance"]["gate_2_value_add"]["estimated_value_add"]
        assert estimated_value >= 0.10, "Gate 2 validation failed: value-add below threshold"
        
        # Gate 3: Capability Validator
        cap_validator = CapabilityValidator()
        
        class MockConsumer:
            consumer_id = "cl03_validator"
            declared_capabilities = {
                SignalCapability.SEMANTIC_PROCESSING,
                SignalCapability.TABLE_PARSING,
                SignalCapability.GRAPH_CONSTRUCTION
            }
        
        cap_result = cap_validator.validate(MockConsumer(), "ENRICHMENT_DATA")
        assert cap_result.can_process, "Gate 3 validation failed"
        
        # Gate 4: Channel Validator
        channel_validator = ChannelValidator()
        gate4_config = enrichment_data["_validation_gates_compliance"]["gate_4_channel"]
        
        flow = DataFlow(
            flow_id=gate4_config["flow_id"],
            flow_type=ChannelType.ENRICHMENT_FLOW,
            source=gate4_config["source"],
            destination=gate4_config["destination"],
            data_schema="CL03EnrichmentSchema",
            governance_policy=gate4_config["governance_policy"],
            is_explicit=True,
            is_documented=True,
            is_traceable=True,
            is_governed=True,
            documentation_path=gate4_config["documentation_path"]
        )
        
        channel_validator.register_flow(flow)
        channel_result = channel_validator.validate_flow(gate4_config["flow_id"])
        assert channel_result.valid, "Gate 4 validation failed"
        
        print("\n✅ All 4 validation gates passed for CL03 enrichment!")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])

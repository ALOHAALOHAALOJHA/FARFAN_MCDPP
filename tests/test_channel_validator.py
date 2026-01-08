"""
Unit tests for Channel Authenticity and Integrity Validator (Gate 4).

Tests the channel validator's ability to:
- Register and validate data flows
- Check channel explicitness, documentation, traceability, and governance
- Compute data integrity hashes
- Generate compliance reports
"""

import pytest
import json
from pathlib import Path
from datetime import datetime

from canonic_questionnaire_central.validations.runtime_validators.channel_validator import (
    ChannelValidator,
    DataFlow,
    ChannelType,
    ChannelStatus,
    ChannelValidationResult,
    FlowManifest,
)


class TestChannelValidator:
    """Test suite for ChannelValidator."""
    
    def test_initialization_with_default_flows(self):
        """Test validator initializes with default documented flows."""
        validator = ChannelValidator()
        
        # Should have default flows registered
        assert len(validator._registered_flows) >= 3
        assert "SIGNAL_TO_CONSUMER" in validator._registered_flows
        assert "PDET_ENRICHMENT" in validator._registered_flows
        assert "MUNICIPAL_CONTEXT_FLOW" in validator._registered_flows
    
    def test_register_new_flow(self):
        """Test registering a new data flow."""
        validator = ChannelValidator()
        
        new_flow = DataFlow(
            flow_id="TEST_FLOW",
            flow_type=ChannelType.ENRICHMENT_FLOW,
            source="test_source",
            destination="test_destination",
            data_schema="TestSchema",
            governance_policy="test_policy",
            is_explicit=True,
            is_documented=True,
            is_traceable=True,
            is_governed=True,
            documentation_path="docs/test_flow.md"
        )
        
        validator.register_flow(new_flow)
        
        assert "TEST_FLOW" in validator._registered_flows
        assert validator._registered_flows["TEST_FLOW"].flow_id == "TEST_FLOW"
    
    def test_validate_unregistered_flow_fails(self):
        """Test validation fails for unregistered flow."""
        validator = ChannelValidator()
        
        result = validator.validate_flow("NONEXISTENT_FLOW")
        
        assert not result.valid
        assert result.flow_id == "NONEXISTENT_FLOW"
        assert len(result.violations) > 0
        assert "not registered" in result.violations[0].lower()
    
    def test_validate_fully_compliant_flow_passes(self):
        """Test validation passes for fully compliant flow."""
        validator = ChannelValidator()
        
        compliant_flow = DataFlow(
            flow_id="COMPLIANT_FLOW",
            flow_type=ChannelType.ENRICHMENT_FLOW,
            source="source_module",
            destination="dest_module",
            data_schema="CompliantSchema",
            governance_policy="full_governance",
            is_explicit=True,
            is_documented=True,
            is_traceable=True,
            is_governed=True,
            documentation_path="docs/compliant.md",
            change_control_id="CC-2024-001",
            observability_endpoint="/metrics/compliant",
            resilience_level="HIGH"
        )
        
        validator.register_flow(compliant_flow)
        result = validator.validate_flow("COMPLIANT_FLOW")
        
        assert result.valid
        assert len(result.violations) == 0
        assert result.compliance_score == 1.0
        assert result.status_flags["explicit"]
        assert result.status_flags["documented"]
        assert result.status_flags["traceable"]
        assert result.status_flags["governed"]
    
    def test_validate_implicit_flow_fails(self):
        """Test validation fails for implicit flow."""
        validator = ChannelValidator()
        
        implicit_flow = DataFlow(
            flow_id="IMPLICIT_FLOW",
            flow_type=ChannelType.ENRICHMENT_FLOW,
            source="source",
            destination="dest",
            data_schema="Schema",
            governance_policy="policy",
            is_explicit=False,  # Implicit
            is_documented=True,
            is_traceable=True,
            is_governed=True
        )
        
        validator.register_flow(implicit_flow)
        result = validator.validate_flow("IMPLICIT_FLOW")
        
        assert not result.valid
        assert any("implicit" in v.lower() for v in result.violations)
        assert result.compliance_score < 1.0
    
    def test_validate_undocumented_flow_fails_in_strict_mode(self):
        """Test validation fails for undocumented flow in strict mode."""
        validator = ChannelValidator(require_documentation=True)
        
        undocumented_flow = DataFlow(
            flow_id="UNDOCUMENTED_FLOW",
            flow_type=ChannelType.ENRICHMENT_FLOW,
            source="source",
            destination="dest",
            data_schema="Schema",
            governance_policy="policy",
            is_explicit=True,
            is_documented=False,  # Not documented
            is_traceable=True,
            is_governed=True
        )
        
        validator.register_flow(undocumented_flow)
        result = validator.validate_flow("UNDOCUMENTED_FLOW")
        
        assert not result.valid
        assert any("documentation" in v.lower() for v in result.violations)
    
    def test_validate_untraceable_flow_fails(self):
        """Test validation fails for untraceable flow."""
        validator = ChannelValidator()
        
        untraceable_flow = DataFlow(
            flow_id="UNTRACEABLE_FLOW",
            flow_type=ChannelType.ENRICHMENT_FLOW,
            source="source",
            destination="dest",
            data_schema="Schema",
            governance_policy="policy",
            is_explicit=True,
            is_documented=True,
            is_traceable=False,  # Not traceable
            is_governed=True
        )
        
        validator.register_flow(untraceable_flow)
        result = validator.validate_flow("UNTRACEABLE_FLOW")
        
        assert not result.valid
        assert any("traceable" in v.lower() for v in result.violations)
    
    def test_validate_ungoverned_flow_fails(self):
        """Test validation fails for ungoverned flow."""
        validator = ChannelValidator()
        
        ungoverned_flow = DataFlow(
            flow_id="UNGOVERNED_FLOW",
            flow_type=ChannelType.ENRICHMENT_FLOW,
            source="source",
            destination="dest",
            data_schema="Schema",
            governance_policy="policy",
            is_explicit=True,
            is_documented=True,
            is_traceable=True,
            is_governed=False  # Not governed
        )
        
        validator.register_flow(ungoverned_flow)
        result = validator.validate_flow("UNGOVERNED_FLOW")
        
        assert not result.valid
        assert any("governance" in v.lower() for v in result.violations)
    
    def test_validate_with_missing_optional_features_generates_warnings(self):
        """Test warnings for missing optional features."""
        validator = ChannelValidator(require_change_control=True)
        
        partial_flow = DataFlow(
            flow_id="PARTIAL_FLOW",
            flow_type=ChannelType.ENRICHMENT_FLOW,
            source="source",
            destination="dest",
            data_schema="Schema",
            governance_policy="policy",
            is_explicit=True,
            is_documented=True,
            is_traceable=True,
            is_governed=True,
            change_control_id=None,  # Missing
            observability_endpoint=None,  # Missing
            resilience_level=None  # Missing
        )
        
        validator.register_flow(partial_flow)
        result = validator.validate_flow("PARTIAL_FLOW")
        
        # Should still pass validation but have warnings
        assert len(result.warnings) > 0
        assert any("change control" in w.lower() for w in result.warnings)
        assert any("observability" in w.lower() for w in result.warnings)
        assert any("resilience" in w.lower() for w in result.warnings)
    
    def test_check_flow_integrity_with_valid_payload(self):
        """Test flow integrity check with valid payload."""
        validator = ChannelValidator()
        
        test_flow = DataFlow(
            flow_id="INTEGRITY_TEST_FLOW",
            flow_type=ChannelType.ENRICHMENT_FLOW,
            source="test_source",
            destination="test_dest",
            data_schema="TestSchema",
            governance_policy="policy",
            is_explicit=True,
            is_documented=True,
            is_traceable=True,
            is_governed=True
        )
        
        validator.register_flow(test_flow)
        
        payload = {
            "source": "test_source",
            "destination": "test_dest",
            "data": {"test_key": "test_value"}
        }
        
        result = validator.check_flow_integrity("INTEGRITY_TEST_FLOW", payload)
        
        assert result["valid"]
        assert "data_hash" in result
        assert result["flow_id"] == "INTEGRITY_TEST_FLOW"
    
    def test_check_flow_integrity_with_source_mismatch(self):
        """Test flow integrity check fails with source mismatch."""
        validator = ChannelValidator()
        
        test_flow = DataFlow(
            flow_id="MISMATCH_FLOW",
            flow_type=ChannelType.ENRICHMENT_FLOW,
            source="expected_source",
            destination="expected_dest",
            data_schema="TestSchema",
            governance_policy="policy",
            is_explicit=True,
            is_documented=True,
            is_traceable=True,
            is_governed=True
        )
        
        validator.register_flow(test_flow)
        
        payload = {
            "source": "wrong_source",  # Mismatch
            "destination": "expected_dest",
            "data": {}
        }
        
        result = validator.check_flow_integrity("MISMATCH_FLOW", payload)
        
        assert not result["valid"]
        assert "mismatch" in result["error"].lower()
    
    def test_validate_all_flows(self):
        """Test validating all registered flows."""
        validator = ChannelValidator()
        
        # Add a mix of compliant and non-compliant flows
        compliant = DataFlow(
            flow_id="COMPLIANT", flow_type=ChannelType.ENRICHMENT_FLOW,
            source="s", destination="d", data_schema="S", governance_policy="p",
            is_explicit=True, is_documented=True, is_traceable=True, is_governed=True
        )
        
        non_compliant = DataFlow(
            flow_id="NON_COMPLIANT", flow_type=ChannelType.ENRICHMENT_FLOW,
            source="s", destination="d", data_schema="S", governance_policy="p",
            is_explicit=False, is_documented=False, is_traceable=False, is_governed=False
        )
        
        validator.register_flow(compliant)
        validator.register_flow(non_compliant)
        
        results = validator.validate_all_flows()
        
        # Should include all registered flows
        assert len(results) >= 2
        
        # Find our test flows
        compliant_result = next(r for r in results if r.flow_id == "COMPLIANT")
        non_compliant_result = next(r for r in results if r.flow_id == "NON_COMPLIANT")
        
        assert compliant_result.valid
        assert not non_compliant_result.valid
    
    def test_compliance_report_generation(self):
        """Test generating compliance report."""
        validator = ChannelValidator()
        
        # Validate some flows
        validator.validate_flow("SIGNAL_TO_CONSUMER")
        validator.validate_flow("PDET_ENRICHMENT")
        
        report = validator.get_compliance_report()
        
        assert report["rule"] == "REGLA_4_CHANNEL_AUTHENTICITY_AND_INTEGRITY"
        assert "total_flows_validated" in report
        assert "valid_flows" in report
        assert "violations" in report
        assert "compliance_rate" in report
        assert "status" in report
        assert "registered_flows" in report
    
    def test_export_flow_manifest(self, tmp_path):
        """Test exporting flow manifest to file."""
        validator = ChannelValidator()
        
        test_flow = DataFlow(
            flow_id="EXPORT_TEST", flow_type=ChannelType.ENRICHMENT_FLOW,
            source="source", destination="dest", data_schema="Schema", governance_policy="policy",
            is_explicit=True, is_documented=True, is_traceable=True, is_governed=True
        )
        validator.register_flow(test_flow)
        
        output_file = tmp_path / "flow_manifest.json"
        validator.export_flow_manifest(output_file)
        
        assert output_file.exists()
        
        with open(output_file) as f:
            manifest = json.load(f)
        
        assert "manifest_version" in manifest
        assert "generated_at" in manifest
        assert "flows" in manifest
        assert len(manifest["flows"]) >= 1
        
        # Find our test flow
        test_flow_data = next(f for f in manifest["flows"] if f["flow_id"] == "EXPORT_TEST")
        assert test_flow_data["source"] == "source"
        assert test_flow_data["destination"] == "dest"
    
    def test_reset_log_clears_validation_history(self):
        """Test resetting validation log."""
        validator = ChannelValidator()
        
        # Perform some validations
        validator.validate_flow("SIGNAL_TO_CONSUMER")
        validator.validate_flow("PDET_ENRICHMENT")
        
        assert len(validator._validation_log) > 0
        
        validator.reset_log()
        
        assert len(validator._validation_log) == 0
        assert validator._violations_count == 0
    
    def test_payload_schema_validation(self):
        """Test payload schema validation."""
        validator = ChannelValidator()
        
        test_flow = DataFlow(
            flow_id="SCHEMA_TEST", flow_type=ChannelType.ENRICHMENT_FLOW,
            source="source", destination="dest", data_schema="TestSchema", governance_policy="policy",
            is_explicit=True, is_documented=True, is_traceable=True, is_governed=True
        )
        validator.register_flow(test_flow)
        
        # Valid payload with required metadata
        valid_payload = {
            "source": "source",
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }
        
        result_valid = validator.validate_flow("SCHEMA_TEST", data_payload=valid_payload)
        assert result_valid.valid
        
        # Invalid payload missing timestamp
        invalid_payload = {
            "source": "source",
            "data": {}
        }
        
        result_invalid = validator.validate_flow("SCHEMA_TEST", data_payload=invalid_payload)
        assert not result_invalid.valid
        assert any("timestamp" in v.lower() for v in result_invalid.violations)


class TestDataFlow:
    """Test suite for DataFlow dataclass."""
    
    def test_data_flow_creation(self):
        """Test creating a DataFlow instance."""
        flow = DataFlow(
            flow_id="TEST_FLOW",
            flow_type=ChannelType.ENRICHMENT_FLOW,
            source="source_module",
            destination="dest_module",
            data_schema="TestSchema",
            governance_policy="test_policy",
            is_explicit=True,
            is_documented=True,
            is_traceable=True,
            is_governed=True
        )
        
        assert flow.flow_id == "TEST_FLOW"
        assert flow.flow_type == ChannelType.ENRICHMENT_FLOW
        assert flow.is_explicit
        assert flow.is_documented
        assert flow.is_traceable
        assert flow.is_governed
    
    def test_data_flow_with_metadata(self):
        """Test DataFlow with additional metadata."""
        metadata = {
            "owner": "team_name",
            "version": "1.0.0",
            "tags": ["production", "critical"]
        }
        
        flow = DataFlow(
            flow_id="META_FLOW",
            flow_type=ChannelType.ENRICHMENT_FLOW,
            source="source",
            destination="dest",
            data_schema="Schema",
            governance_policy="policy",
            is_explicit=True,
            is_documented=True,
            is_traceable=True,
            is_governed=True,
            metadata=metadata
        )
        
        assert flow.metadata["owner"] == "team_name"
        assert "production" in flow.metadata["tags"]


class TestFlowManifest:
    """Test suite for FlowManifest dataclass."""
    
    def test_flow_manifest_creation(self):
        """Test creating a FlowManifest."""
        flows = [
            DataFlow(
                flow_id="FLOW_1", flow_type=ChannelType.ENRICHMENT_FLOW,
                source="s1", destination="d1", data_schema="S1", governance_policy="p1",
                is_explicit=True, is_documented=True, is_traceable=True, is_governed=True
            ),
            DataFlow(
                flow_id="FLOW_2", flow_type=ChannelType.DIRECT_SIGNAL_FLOW,
                source="s2", destination="d2", data_schema="S2", governance_policy="p2",
                is_explicit=True, is_documented=True, is_traceable=True, is_governed=True
            )
        ]
        
        manifest = FlowManifest(
            manifest_version="1.0.0",
            generated_at="2024-01-01T00:00:00Z",
            flows=flows
        )
        
        assert len(manifest.flows) == 2
        assert len(manifest.flow_registry) == 2
        assert "FLOW_1" in manifest.flow_registry
        assert "FLOW_2" in manifest.flow_registry
    
    def test_flow_manifest_registry_auto_populated(self):
        """Test flow registry is auto-populated on initialization."""
        flows = [
            DataFlow(
                flow_id="AUTO_FLOW", flow_type=ChannelType.ENRICHMENT_FLOW,
                source="s", destination="d", data_schema="S", governance_policy="p",
                is_explicit=True, is_documented=True, is_traceable=True, is_governed=True
            )
        ]
        
        manifest = FlowManifest(
            manifest_version="1.0.0",
            generated_at="2024-01-01T00:00:00Z",
            flows=flows
        )
        
        # Registry should be auto-populated
        assert "AUTO_FLOW" in manifest.flow_registry
        assert manifest.flow_registry["AUTO_FLOW"].flow_id == "AUTO_FLOW"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

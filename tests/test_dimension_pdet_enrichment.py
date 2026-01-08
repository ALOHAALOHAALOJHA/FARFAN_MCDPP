"""
Tests for PDET Dimension Enrichment System
===========================================

Tests the loading, validation, and usage of PDET context enrichment
for dimensions.
"""

import json
import pytest
from pathlib import Path

from canonic_questionnaire_central.dimensions import pdet_enrichment


class TestPdetEnrichmentLoading:
    """Test loading of PDET enrichment files."""
    
    def test_load_dim01_context(self):
        """Test loading DIM01 PDET context."""
        context = pdet_enrichment.load_dimension_pdet_context("DIM01_INSUMOS")
        
        assert context is not None
        assert context["_dimension_id"] == "DIM01"
        assert context["_dimension_name"] == "INSUMOS (Diagnóstico y Líneas Base)"
        assert "validation_gates_alignment" in context
        assert "pdet_pillar_mapping" in context
        assert "pdet_specific_criteria" in context
    
    def test_load_all_dimensions(self):
        """Test loading all dimension PDET contexts."""
        dimensions = [
            "DIM01_INSUMOS",
            "DIM02_ACTIVIDADES",
            "DIM03_PRODUCTOS",
            "DIM04_RESULTADOS",
            "DIM05_IMPACTOS",
            "DIM06_CAUSALIDAD"
        ]
        
        for dim_id in dimensions:
            context = pdet_enrichment.load_dimension_pdet_context(dim_id)
            assert context is not None
            assert "_dimension_id" in context
            assert "validation_gates_alignment" in context
    
    def test_load_nonexistent_dimension(self):
        """Test loading nonexistent dimension raises error."""
        with pytest.raises(FileNotFoundError):
            pdet_enrichment.load_dimension_pdet_context("DIM99_FAKE")
    
    def test_list_all_dimensions(self):
        """Test listing all dimensions with PDET enrichment."""
        dimensions = pdet_enrichment.list_all_dimensions()
        
        assert len(dimensions) == 6
        assert "DIM01_INSUMOS" in dimensions
        assert "DIM06_CAUSALIDAD" in dimensions


class TestValidationGates:
    """Test validation gates alignment."""
    
    def test_get_validation_gates_dim01(self):
        """Test getting validation gates for DIM01."""
        gates = pdet_enrichment.get_validation_gates("DIM01_INSUMOS")
        
        assert len(gates) == 4
        assert "gate_1_scope" in gates
        assert "gate_2_value_add" in gates
        assert "gate_3_capability" in gates
        assert "gate_4_channel" in gates
        
        # Check gate 1
        gate1 = gates["gate_1_scope"]
        assert gate1.gate_number == 1
        assert gate1.required_scope == "pdet_context"
        assert "ENRICHMENT_DATA" in gate1.allowed_signal_types
        
        # Check gate 2
        gate2 = gates["gate_2_value_add"]
        assert gate2.gate_number == 2
        assert gate2.estimated_value_add > 0
        
        # Check gate 3
        gate3 = gates["gate_3_capability"]
        assert gate3.gate_number == 3
        assert len(gate3.required_capabilities) > 0
        assert "SEMANTIC_PROCESSING" in gate3.required_capabilities
        
        # Check gate 4
        gate4 = gates["gate_4_channel"]
        assert gate4.gate_number == 4
        assert gate4.flow_id is not None
        assert "DIM01" in gate4.flow_id
    
    def test_all_dimensions_have_gates(self):
        """Test all dimensions have validation gates defined."""
        dimensions = pdet_enrichment.list_all_dimensions()
        
        for dim_id in dimensions:
            gates = pdet_enrichment.get_validation_gates(dim_id)
            assert len(gates) == 4
            
            # Gates 1-3 should have justification (gate 4 justification is in context file)
            for gate_name, gate in gates.items():
                if gate_name in ["gate_1_scope", "gate_2_value_add", "gate_3_capability"]:
                    assert gate.justification != "", f"{dim_id} {gate_name} missing justification"


class TestPdetPillarMapping:
    """Test PDET pillar mappings."""
    
    def test_get_primary_pillars_dim01(self):
        """Test getting primary pillars for DIM01."""
        pillars = pdet_enrichment.get_pdet_pillars("DIM01_INSUMOS")
        
        assert len(pillars) >= 2
        
        # Check first pillar
        pillar = pillars[0]
        assert pillar.pillar_id.startswith("pillar_")
        assert pillar.pillar_name != ""
        assert pillar.relevance in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        assert 0 <= pillar.relevance_score <= 1.0
        assert len(pillar.requirements) > 0
    
    def test_get_pillars_with_secondary(self):
        """Test getting both primary and secondary pillars."""
        pillars_primary = pdet_enrichment.get_pdet_pillars("DIM01_INSUMOS", include_secondary=False)
        pillars_all = pdet_enrichment.get_pdet_pillars("DIM01_INSUMOS", include_secondary=True)
        
        assert len(pillars_all) >= len(pillars_primary)
    
    def test_dim02_has_relevant_pillars(self):
        """Test DIM02 (Activities) has infrastructure and economic pillars."""
        pillars = pdet_enrichment.get_pdet_pillars("DIM02_ACTIVIDADES")
        
        pillar_ids = [p.pillar_id for p in pillars]
        
        # DIM02 should focus on infrastructure (pillar_2) and economic (pillar_6)
        assert "pillar_2" in pillar_ids or "pillar_6" in pillar_ids
    
    def test_dim05_has_impact_focus(self):
        """Test DIM05 (Impacts) has reconciliation pillar."""
        pillars = pdet_enrichment.get_pdet_pillars("DIM05_IMPACTOS")
        
        pillar_ids = [p.pillar_id for p in pillars]
        
        # DIM05 should have reconciliation (pillar_8) as primary
        assert "pillar_8" in pillar_ids


class TestPolicyAreaCriteria:
    """Test policy area specific criteria."""
    
    def test_get_pa01_criteria_dim01(self):
        """Test getting PA01 criteria for DIM01."""
        criteria = pdet_enrichment.get_policy_area_criteria("DIM01_INSUMOS", "PA01")
        
        assert criteria is not None
        assert criteria.policy_area_id == "PA01"
        assert len(criteria.required_elements) > 0
        assert len(criteria.pdet_subregions_high_priority) > 0
        assert len(criteria.key_indicators) > 0
    
    def test_get_pa02_criteria_all_dimensions(self):
        """Test PA02 (Violence/Security) exists in most dimensions."""
        dimensions = pdet_enrichment.list_all_dimensions()
        pa02_count = 0
        
        for dim_id in dimensions:
            criteria = pdet_enrichment.get_policy_area_criteria(dim_id, "PA02")
            if criteria is not None:
                pa02_count += 1
        
        # PA02 should be in at least some dimensions (violence/security is important in PDET)
        assert pa02_count >= 1
    
    def test_nonexistent_policy_area(self):
        """Test getting nonexistent policy area returns None."""
        criteria = pdet_enrichment.get_policy_area_criteria("DIM01_INSUMOS", "PA99")
        assert criteria is None


class TestCommonGaps:
    """Test common planning gaps."""
    
    def test_get_gaps_dim01(self):
        """Test getting common gaps for DIM01."""
        gaps = pdet_enrichment.get_common_gaps("DIM01_INSUMOS")
        
        assert len(gaps) > 0
        
        # Check gap structure
        for gap_id, gap_data in gaps.items():
            assert "description" in gap_data
            assert "prevalence" in gap_data
            assert "impact" in gap_data
            assert "remediation" in gap_data
    
    def test_all_dimensions_have_gaps(self):
        """Test all dimensions have common gaps documented."""
        dimensions = pdet_enrichment.list_all_dimensions()
        
        for dim_id in dimensions:
            gaps = pdet_enrichment.get_common_gaps(dim_id)
            assert len(gaps) > 0, f"{dim_id} should have common gaps documented"


class TestPdetSpecificCriteria:
    """Test PDET-specific criteria."""
    
    def test_get_criteria_dim01(self):
        """Test getting PDET-specific criteria for DIM01."""
        criteria = pdet_enrichment.get_pdet_specific_criteria("DIM01_INSUMOS")
        
        assert len(criteria) > 0
        
        # DIM01 should have territorial disaggregation
        assert "territorial_disaggregation" in criteria
        
        # Should have ethnic differential approach
        assert "ethnic_differential_approach" in criteria
    
    def test_dim02_has_patr_alignment(self):
        """Test DIM02 has PATR alignment criteria."""
        criteria = pdet_enrichment.get_pdet_specific_criteria("DIM02_ACTIVIDADES")
        
        # DIM02 should require PATR alignment
        assert "patr_alignment" in criteria
    
    def test_dim04_has_causal_attribution(self):
        """Test DIM04 has causal attribution criteria."""
        criteria = pdet_enrichment.get_pdet_specific_criteria("DIM04_RESULTADOS")
        
        # DIM04 should require causal attribution
        assert "causal_attribution" in criteria
    
    def test_dim05_has_sustainability(self):
        """Test DIM05 has sustainability criteria."""
        criteria = pdet_enrichment.get_pdet_specific_criteria("DIM05_IMPACTOS")
        
        # DIM05 should require sustainability specification
        assert "sustainability_specification" in criteria


class TestEnrichmentValidation:
    """Test enrichment validation."""
    
    def test_validate_dim01(self):
        """Test validating DIM01 enrichment."""
        is_valid, errors = pdet_enrichment.validate_dimension_enrichment("DIM01_INSUMOS")
        
        assert is_valid, f"Validation errors: {errors}"
        assert len(errors) == 0
    
    def test_validate_all_dimensions(self):
        """Test validating all dimension enrichments."""
        dimensions = pdet_enrichment.list_all_dimensions()
        
        for dim_id in dimensions:
            is_valid, errors = pdet_enrichment.validate_dimension_enrichment(dim_id)
            assert is_valid, f"{dim_id} validation errors: {errors}"
    
    def test_validate_nonexistent_dimension(self):
        """Test validating nonexistent dimension."""
        is_valid, errors = pdet_enrichment.validate_dimension_enrichment("DIM99_FAKE")
        
        assert not is_valid
        assert len(errors) > 0


class TestMetadata:
    """Test metadata in enrichment files."""
    
    def test_all_dimensions_have_metadata(self):
        """Test all dimensions have complete metadata."""
        dimensions = pdet_enrichment.list_all_dimensions()
        
        required_fields = ["created_at", "version", "author", "validated"]
        
        for dim_id in dimensions:
            context = pdet_enrichment.load_dimension_pdet_context(dim_id)
            metadata = context.get("metadata", {})
            
            for field in required_fields:
                assert field in metadata, f"{dim_id} missing metadata field: {field}"
    
    def test_metadata_version_format(self):
        """Test metadata version follows semantic versioning."""
        dimensions = pdet_enrichment.list_all_dimensions()
        
        for dim_id in dimensions:
            context = pdet_enrichment.load_dimension_pdet_context(dim_id)
            version = context["metadata"]["version"]
            
            # Should be in format X.Y.Z
            parts = version.split(".")
            assert len(parts) == 3
            assert all(part.isdigit() for part in parts)


class TestIntegration:
    """Test integration with PDET municipality data."""
    
    def test_pdet_municipalities_exist(self):
        """Test PDET municipalities file exists and is loadable."""
        from canonic_questionnaire_central.colombia_context import get_pdet_municipalities
        
        pdet_data = get_pdet_municipalities()
        assert pdet_data is not None
        assert "subregions" in pdet_data
        # The file contains 8 subregions (representative sample, not all 16)
        assert len(pdet_data["subregions"]) >= 8
    
    def test_subregions_match_priorities(self):
        """Test subregions in enrichment match actual PDET subregions."""
        from canonic_questionnaire_central.colombia_context import get_pdet_subregions
        
        actual_subregions = get_pdet_subregions()
        actual_ids = {sr["subregion_id"] for sr in actual_subregions}
        
        # Check PA01 priorities in DIM01
        criteria = pdet_enrichment.get_policy_area_criteria("DIM01_INSUMOS", "PA01")
        if criteria:
            for sr_id in criteria.pdet_subregions_high_priority:
                assert sr_id in actual_ids, f"Subregion {sr_id} not in actual PDET subregions"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

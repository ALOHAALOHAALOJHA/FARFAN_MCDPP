"""Test unit of analysis (PDM/PDT) integration with calibration system."""
import pytest
from src.farfan_pipeline.core.canonical_specs import UNIT_OF_ANALYSIS


def test_unit_of_analysis_exists():
    """Verify UNIT_OF_ANALYSIS specification is loaded."""
    assert UNIT_OF_ANALYSIS is not None
    assert isinstance(UNIT_OF_ANALYSIS, dict)


def test_pdm_structure_specification():
    """Verify PDM structure elements are defined."""
    assert "document_type" in UNIT_OF_ANALYSIS
    assert "PDM" in UNIT_OF_ANALYSIS["document_type"] or "PDT" in UNIT_OF_ANALYSIS["document_type"]
    
    assert "jurisdiction" in UNIT_OF_ANALYSIS
    assert "Colombian" in UNIT_OF_ANALYSIS["jurisdiction"] or "Colombia" in UNIT_OF_ANALYSIS["jurisdiction"]
    
    assert "temporal_scope" in UNIT_OF_ANALYSIS
    assert "legal_framework" in UNIT_OF_ANALYSIS
    assert "Ley 152" in UNIT_OF_ANALYSIS["legal_framework"]


def test_pdm_expected_sections():
    """Verify expected PDM sections are documented."""
    # PDM structure should include key sections
    expected_sections = ["Diagnóstico", "Parte estratégica", "Plan Plurianual", "PPI"]
    
    # Check if structure elements are documented
    assert "structure_elements" in UNIT_OF_ANALYSIS or "expected_sections" in UNIT_OF_ANALYSIS
    
    structure_info = UNIT_OF_ANALYSIS.get("structure_elements") or UNIT_OF_ANALYSIS.get("expected_sections", [])
    structure_str = str(structure_info).lower()
    
    # At least some key sections should be present
    assert any(section.lower() in structure_str for section in ["diagnóstico", "diagnostic", "estratégic", "strategic"])


def test_pdet_context_documented():
    """Verify PDET zone context is documented in unit of analysis."""
    unit_str = str(UNIT_OF_ANALYSIS).lower()
    
    # Should reference PDET (Programas de Desarrollo con Enfoque Territorial)
    assert "pdet" in unit_str or "territorial" in unit_str
    
    # Should reference peace implementation
    assert any(keyword in unit_str for keyword in ["peace", "paz", "acuerdo", "accord", "conflict"])


def test_colombian_territorial_entities():
    """Verify Colombian territorial entities are documented."""
    unit_str = str(UNIT_OF_ANALYSIS).lower()
    
    # Should reference Colombian administrative divisions
    assert any(term in unit_str for term in ["municipal", "territorial", "departamento", "municipio"])


def test_legal_compliance_framework():
    """Verify legal compliance framework is specified."""
    assert "legal_framework" in UNIT_OF_ANALYSIS
    framework = UNIT_OF_ANALYSIS["legal_framework"]
    
    # Should include Ley 152 (organic law for territorial planning)
    assert "152" in str(framework)
    
    # May also reference other relevant laws
    framework_str = str(framework).lower()
    assert "ley" in framework_str or "law" in framework_str


def test_pdm_validation_rules_exist():
    """Verify PDM validation rules are available for ingestion methods."""
    from src.farfan_pipeline.core.canonical_specs import INGESTION_CALIBRATION_RULES
    
    assert INGESTION_CALIBRATION_RULES is not None
    assert isinstance(INGESTION_CALIBRATION_RULES, dict)
    
    # Should have rules for text processing methods
    ingestion_methods = ["semantic_chunking_policy", "analyzer_one", "embedding_policy"]
    for method in ingestion_methods:
        assert method in INGESTION_CALIBRATION_RULES, f"{method} should have ingestion calibration rules"


def test_pdm_structure_validation_rules():
    """Verify PDM structure validation rules are defined."""
    from src.farfan_pipeline.core.canonical_specs import INGESTION_CALIBRATION_RULES
    
    # Semantic chunking should have PDM structure awareness
    if "semantic_chunking_policy" in INGESTION_CALIBRATION_RULES:
        rules = INGESTION_CALIBRATION_RULES["semantic_chunking_policy"]
        
        # Should enforce PDM structure
        assert "strict_structure_validation" in rules or "pdm_structure" in str(rules).lower()
        assert "expected_h1_sections" in rules or "expected_sections" in rules or "structure" in str(rules).lower()


def test_territorial_entity_extraction_rules():
    """Verify territorial entity extraction rules for analyzer_one."""
    from src.farfan_pipeline.core.canonical_specs import INGESTION_CALIBRATION_RULES
    
    if "analyzer_one" in INGESTION_CALIBRATION_RULES:
        rules = INGESTION_CALIBRATION_RULES["analyzer_one"]
        
        # Should have rules for Colombian territorial entities
        rules_str = str(rules).lower()
        assert any(term in rules_str for term in ["territorial", "entity", "municipal", "pdet"])


def test_embedding_semantic_clustering_rules():
    """Verify semantic clustering rules for embedding_policy."""
    from src.farfan_pipeline.core.canonical_specs import INGESTION_CALIBRATION_RULES
    
    if "embedding_policy" in INGESTION_CALIBRATION_RULES:
        rules = INGESTION_CALIBRATION_RULES["embedding_policy"]
        
        # Should have rules for PDM section clustering
        rules_str = str(rules).lower()
        assert any(term in rules_str for term in ["cluster", "semantic", "section", "pdm"])


def test_unit_analysis_temporal_scope():
    """Verify temporal scope is appropriate for current PDM cycle."""
    assert "temporal_scope" in UNIT_OF_ANALYSIS
    temporal = str(UNIT_OF_ANALYSIS["temporal_scope"])
    
    # Should reference 4-year municipal cycle (cuatrienio)
    assert any(term in temporal for term in ["2024", "2025", "2026", "2027", "cuatrienio", "4-year", "four-year"])


def test_analysis_focus_peace_implementation():
    """Verify analysis focus includes peace accord implementation."""
    assert "analysis_focus" in UNIT_OF_ANALYSIS or "focus" in UNIT_OF_ANALYSIS
    
    focus_str = str(UNIT_OF_ANALYSIS.get("analysis_focus", "") or UNIT_OF_ANALYSIS.get("focus", "")).lower()
    
    # Should explicitly mention peace implementation
    assert any(term in focus_str for term in ["peace", "paz", "implementation", "implementación", "territorial development"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

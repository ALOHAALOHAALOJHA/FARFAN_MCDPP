"""
Tests for Colombian PDM Chunk Enhancer

Purpose: Validate Colombian PDM-specific chunk enhancement functionality
Author: F.A.R.F.A.N Core Team
Version: 1.0.0
"""
from __future__ import annotations

import pytest
from farfan_pipeline.phases.Phase_01.phase1_07_01_colombian_pdm_enhancer import (
    ColombianPDMChunkEnhancer,
    ColombianPDMPatterns,
    PDMChunkEnhancement,
    check_if_already_chunked,
    assert_not_chunked,
    AlreadyChunkedError,
)


class TestColombianPDMPatterns:
    """Test PDM pattern definitions."""
    
    def test_patterns_loaded(self):
        """Test that all pattern categories are defined."""
        patterns = ColombianPDMPatterns()
        
        assert len(patterns.regulatory_markers) > 0
        assert len(patterns.section_markers) > 0
        assert len(patterns.territorial_indicators) > 0
        assert len(patterns.financial_markers) > 0
        assert len(patterns.differential_approach_markers) > 0
        assert len(patterns.quantitative_markers) > 0
        assert len(patterns.strategic_markers) > 0


class TestColombianPDMChunkEnhancer:
    """Test PDM chunk enhancement functionality."""
    
    @pytest.fixture
    def enhancer(self):
        """Create enhancer instance."""
        return ColombianPDMChunkEnhancer()
    
    @pytest.fixture
    def sample_pdm_content(self):
        """Sample Colombian PDM content."""
        return """
        Plan de Desarrollo Municipal 2024-2027
        
        Diagnóstico Territorial
        
        El municipio presenta un NBI del 45% según datos del DANE. 
        La población con SISBEN III categoría A y B representa el 62%.
        
        Presupuesto de Inversión: $5.000 millones del Sistema General de Participaciones (SGP).
        Recursos propios: $1.200 millones.
        
        Enfoque diferencial para pueblos indígenas y comunidades afrodescendientes.
        Atención prioritaria a víctimas del conflicto armado según Ley 1448.
        
        Objetivo estratégico: Reducir la tasa de desnutrición en primera infancia del 18% al 12%.
        Meta cuatrienio: 300 familias beneficiadas.
        Línea base: 500 casos reportados.
        """
    
    def test_enhancer_initialization(self, enhancer):
        """Test enhancer initializes correctly."""
        assert enhancer is not None
        assert enhancer.patterns is not None
    
    def test_enhance_chunk_basic(self, enhancer, sample_pdm_content):
        """Test basic chunk enhancement."""
        enhancement = enhancer.enhance_chunk(sample_pdm_content, {})
        
        assert isinstance(enhancement, PDMChunkEnhancement)
        assert enhancement.pdm_specificity_score > 0.0
    
    def test_detect_regulatory_markers(self, enhancer, sample_pdm_content):
        """Test detection of regulatory markers."""
        enhancement = enhancer.enhance_chunk(sample_pdm_content, {})
        
        assert enhancement.has_regulatory_reference
        assert enhancement.regulatory_refs_count > 0
    
    def test_detect_section_markers(self, enhancer, sample_pdm_content):
        """Test detection of section markers."""
        enhancement = enhancer.enhance_chunk(sample_pdm_content, {})
        
        assert enhancement.has_section_marker
        assert len(enhancement.detected_sections) > 0
        assert any("diagnóstico" in s.lower() for s in enhancement.detected_sections)
    
    def test_detect_territorial_indicators(self, enhancer, sample_pdm_content):
        """Test detection of territorial indicators."""
        enhancement = enhancer.enhance_chunk(sample_pdm_content, {})
        
        assert enhancement.has_territorial_indicator
        assert len(enhancement.indicator_types) > 0
    
    def test_detect_financial_markers(self, enhancer, sample_pdm_content):
        """Test detection of financial markers."""
        enhancement = enhancer.enhance_chunk(sample_pdm_content, {})
        
        assert enhancement.has_financial_info
        assert len(enhancement.financial_types) > 0
    
    def test_detect_differential_approach(self, enhancer, sample_pdm_content):
        """Test detection of differential approach."""
        enhancement = enhancer.enhance_chunk(sample_pdm_content, {})
        
        assert enhancement.has_differential_approach
        assert len(enhancement.population_groups) > 0
    
    def test_quantitative_density(self, enhancer, sample_pdm_content):
        """Test quantitative density calculation."""
        enhancement = enhancer.enhance_chunk(sample_pdm_content, {})
        
        assert enhancement.quantitative_density > 0.0
    
    def test_detect_strategic_elements(self, enhancer, sample_pdm_content):
        """Test detection of strategic elements."""
        enhancement = enhancer.enhance_chunk(sample_pdm_content, {})
        
        assert enhancement.has_strategic_elements
        assert len(enhancement.strategic_elements) > 0
    
    def test_specificity_score_calculation(self, enhancer, sample_pdm_content):
        """Test PDM specificity score calculation."""
        enhancement = enhancer.enhance_chunk(sample_pdm_content, {})
        
        # Should be high-quality PDM content
        assert enhancement.pdm_specificity_score >= 0.6
        assert enhancement.pdm_specificity_score <= 1.0
    
    def test_empty_content(self, enhancer):
        """Test enhancement with empty content."""
        enhancement = enhancer.enhance_chunk("", {})
        
        assert enhancement.pdm_specificity_score == 0.0
        assert not enhancement.has_regulatory_reference
        assert not enhancement.has_section_marker
    
    def test_add_enhancement_to_metadata(self, enhancer, sample_pdm_content):
        """Test adding enhancement to metadata."""
        enhancement = enhancer.enhance_chunk(sample_pdm_content, {})
        metadata = {"chunk_id": "TEST-001"}
        
        updated = enhancer.add_enhancement_to_metadata(metadata, enhancement)
        
        assert "colombian_pdm_enhancement" in updated
        pdm_info = updated["colombian_pdm_enhancement"]
        
        assert "pdm_specificity_score" in pdm_info
        assert "context_markers" in pdm_info
        assert "detected_sections" in pdm_info


class TestDocumentProcessingGuards:
    """Test document processing guard functions."""
    
    def test_check_not_chunked(self):
        """Test check_if_already_chunked returns False for unchunked document."""
        doc = type('Doc', (), {'metadata': {}})()
        assert not check_if_already_chunked(doc)
    
    def test_check_chunked_with_chunks_attribute(self):
        """Test detection via chunks attribute."""
        doc = type('Doc', (), {'chunks': [1, 2, 3]})()
        assert check_if_already_chunked(doc)
    
    def test_check_chunked_with_metadata_flag(self):
        """Test detection via metadata flag."""
        doc = type('Doc', (), {'metadata': {'is_chunked': True}})()
        assert check_if_already_chunked(doc)
    
    def test_check_chunked_with_chunk_count(self):
        """Test detection via chunk count."""
        doc = type('Doc', (), {'metadata': {'chunk_count': 300}})()
        assert check_if_already_chunked(doc)
    
    def test_assert_not_chunked_passes(self):
        """Test assert_not_chunked passes for unchunked document."""
        doc = type('Doc', (), {'metadata': {}})()
        # Should not raise
        assert_not_chunked(doc, method_name="test_method")
    
    def test_assert_not_chunked_raises(self):
        """Test assert_not_chunked raises for chunked document."""
        doc = type('Doc', (), {'chunks': [1, 2, 3]})()
        
        with pytest.raises(AlreadyChunkedError) as exc_info:
            assert_not_chunked(doc, method_name="test_method")
        
        assert "test_method" in str(exc_info.value)
        assert "already chunked" in str(exc_info.value).lower()


class TestIntegrationScenarios:
    """Test integration scenarios."""
    
    @pytest.fixture
    def enhancer(self):
        """Create enhancer instance."""
        return ColombianPDMChunkEnhancer()
    
    def test_low_quality_generic_content(self, enhancer):
        """Test with non-PDM generic content."""
        content = "The quick brown fox jumps over the lazy dog."
        enhancement = enhancer.enhance_chunk(content, {})
        
        # Should have low specificity
        assert enhancement.pdm_specificity_score < 0.3
    
    def test_high_quality_pdm_content(self, enhancer):
        """Test with high-quality PDM content."""
        content = """
        PLAN DE DESARROLLO MUNICIPAL 2024-2027
        Marco Legal: Ley 152 de 1994, CONPES 161
        
        DIAGNÓSTICO TERRITORIAL
        NBI: 42.5% (DANE 2018)
        SISBEN IV: 65% población vulnerable
        IPM: 0.385
        
        PLAN PLURIANUAL DE INVERSIONES
        SGP Propósito General: $2.500 millones
        Regalías: $800 millones
        Recursos propios: $1.200 millones
        
        ENFOQUE DIFERENCIAL
        - Pueblos indígenas: 15% población
        - Comunidades afrodescendientes: 25%
        - Primera infancia: 12% población
        - Víctimas conflicto armado: 2.800 registradas
        
        METAS CUATRIENIO
        - Reducir NBI al 38%
        - Cobertura educación: 95%
        - Línea base desnutrición: 18%
        - Meta desnutrición: 12%
        
        TEORÍA DEL CAMBIO
        Cadena causal: Insumos → Actividades → Productos → Resultados → Impactos
        Articulación con ODS y CONPES Nacional
        """
        enhancement = enhancer.enhance_chunk(content, {})
        
        # Should have high specificity
        assert enhancement.pdm_specificity_score >= 0.7
        assert enhancement.has_regulatory_reference
        assert enhancement.has_section_marker
        assert enhancement.has_territorial_indicator
        assert enhancement.has_financial_info
        assert enhancement.has_differential_approach
        assert enhancement.has_strategic_elements

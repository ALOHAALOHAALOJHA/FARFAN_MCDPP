"""
Unit tests for PDTStructure dataclass.
"""

import pytest
from farfan_pipeline.processing.pdt_structure import (
    PDTStructure,
    BlockInfo,
    HeaderInfo,
    SectionInfo,
    IndicatorRow,
    PPIRow,
)


class TestBlockInfo:
    """Tests for BlockInfo dataclass."""
    
    def test_block_info_creation(self):
        """Test creating a BlockInfo instance."""
        block = BlockInfo(
            text="Sample block text",
            tokens=100,
            numbers_count=5,
        )
        
        assert block.text == "Sample block text"
        assert block.tokens == 100
        assert block.numbers_count == 5
    
    def test_block_info_defaults(self):
        """Test BlockInfo with minimal data."""
        block = BlockInfo(text="", tokens=0, numbers_count=0)
        
        assert block.text == ""
        assert block.tokens == 0
        assert block.numbers_count == 0


class TestHeaderInfo:
    """Tests for HeaderInfo dataclass."""
    
    def test_header_info_creation(self):
        """Test creating a HeaderInfo instance."""
        header = HeaderInfo(
            level=2,
            text="1.2 Introduction",
            valid_numbering=True,
        )
        
        assert header.level == 2
        assert header.text == "1.2 Introduction"
        assert header.valid_numbering is True
    
    def test_header_info_invalid_numbering(self):
        """Test header with invalid numbering."""
        header = HeaderInfo(
            level=1,
            text="Introduction",
            valid_numbering=False,
        )
        
        assert header.valid_numbering is False


class TestSectionInfo:
    """Tests for SectionInfo dataclass."""
    
    def test_section_info_creation(self):
        """Test creating a SectionInfo instance."""
        section = SectionInfo(
            present=True,
            token_count=500,
            keyword_matches=10,
            number_count=25,
            sources_found=3,
        )
        
        assert section.present is True
        assert section.token_count == 500
        assert section.keyword_matches == 10
        assert section.number_count == 25
        assert section.sources_found == 3
    
    def test_section_info_not_present(self):
        """Test section that is not present."""
        section = SectionInfo(
            present=False,
            token_count=0,
            keyword_matches=0,
            number_count=0,
            sources_found=0,
        )
        
        assert section.present is False
        assert section.token_count == 0


class TestIndicatorRow:
    """Tests for IndicatorRow dataclass."""
    
    def test_indicator_row_creation(self):
        """Test creating an IndicatorRow instance."""
        row = IndicatorRow(
            tipo="Resultado",
            linea_estrategica="Educación",
            programa="Calidad Educativa",
            nombre_indicador="Tasa de cobertura",
            unidad_medida="%",
            linea_base="85",
            meta_cuatrienio="95",
            responsable="Secretaría de Educación",
        )
        
        assert row.tipo == "Resultado"
        assert row.linea_estrategica == "Educación"
        assert row.programa == "Calidad Educativa"
        assert row.nombre_indicador == "Tasa de cobertura"
    
    def test_indicator_row_to_dict(self):
        """Test converting IndicatorRow to dictionary."""
        row = IndicatorRow(
            tipo="Resultado",
            linea_estrategica="Educación",
        )
        
        result = row.to_dict()
        
        assert isinstance(result, dict)
        assert result["Tipo"] == "Resultado"
        assert result["Línea Estratégica"] == "Educación"
        assert "Programa" in result
    
    def test_indicator_row_defaults(self):
        """Test IndicatorRow with default values."""
        row = IndicatorRow()
        
        assert row.tipo == ""
        assert row.linea_estrategica == ""
        assert row.programa == ""


class TestPPIRow:
    """Tests for PPIRow dataclass."""
    
    def test_ppi_row_creation(self):
        """Test creating a PPIRow instance."""
        row = PPIRow(
            linea_estrategica="Educación",
            programa="Calidad Educativa",
            subprograma="Infraestructura",
            proyecto="Construcción de escuelas",
            costo_total="1000000000",
            vigencia_2024="250000000",
            vigencia_2025="250000000",
            vigencia_2026="250000000",
            vigencia_2027="250000000",
            fuente_recursos="SGP",
        )
        
        assert row.linea_estrategica == "Educación"
        assert row.programa == "Calidad Educativa"
        assert row.costo_total == "1000000000"
        assert row.fuente_recursos == "SGP"
    
    def test_ppi_row_to_dict(self):
        """Test converting PPIRow to dictionary."""
        row = PPIRow(
            linea_estrategica="Educación",
            costo_total="1000000000",
        )
        
        result = row.to_dict()
        
        assert isinstance(result, dict)
        assert result["Línea Estratégica"] == "Educación"
        assert result["Costo Total"] == "1000000000"
        assert "Programa" in result
        assert "Vigencia 2024" in result
    
    def test_ppi_row_defaults(self):
        """Test PPIRow with default values."""
        row = PPIRow()
        
        assert row.linea_estrategica == ""
        assert row.programa == ""
        assert row.costo_total == ""


class TestPDTStructure:
    """Tests for PDTStructure dataclass."""
    
    def test_pdt_structure_creation(self):
        """Test creating a PDTStructure instance."""
        structure = PDTStructure(
            total_tokens=1000,
            full_text="Sample PDT text",
        )
        
        assert structure.total_tokens == 1000
        assert structure.full_text == "Sample PDT text"
        assert isinstance(structure.blocks_found, dict)
        assert isinstance(structure.headers, list)
        assert isinstance(structure.block_sequence, list)
        assert isinstance(structure.sections_found, dict)
        assert isinstance(structure.indicator_rows, list)
        assert isinstance(structure.ppi_rows, list)
    
    def test_pdt_structure_with_blocks(self):
        """Test PDTStructure with blocks."""
        block = BlockInfo(text="Block 1", tokens=50, numbers_count=5)
        
        structure = PDTStructure(
            total_tokens=1000,
            full_text="Sample text",
            blocks_found={"CAPÍTULO 1": block},
        )
        
        assert "CAPÍTULO 1" in structure.blocks_found
        assert structure.blocks_found["CAPÍTULO 1"].tokens == 50
    
    def test_pdt_structure_with_headers(self):
        """Test PDTStructure with headers."""
        headers = [
            HeaderInfo(level=1, text="Introduction", valid_numbering=True),
            HeaderInfo(level=2, text="Background", valid_numbering=True),
        ]
        
        structure = PDTStructure(
            total_tokens=1000,
            full_text="Sample text",
            headers=headers,
        )
        
        assert len(structure.headers) == 2
        assert structure.headers[0].level == 1
        assert structure.headers[1].level == 2
    
    def test_pdt_structure_with_sections(self):
        """Test PDTStructure with sections."""
        sections = {
            "Diagnóstico": SectionInfo(
                present=True,
                token_count=500,
                keyword_matches=10,
                number_count=25,
                sources_found=3,
            ),
        }
        
        structure = PDTStructure(
            total_tokens=1000,
            full_text="Sample text",
            sections_found=sections,
        )
        
        assert "Diagnóstico" in structure.sections_found
        assert structure.sections_found["Diagnóstico"].present is True
    
    def test_pdt_structure_with_indicators(self):
        """Test PDTStructure with indicator rows."""
        indicators = [
            IndicatorRow(tipo="Resultado", linea_estrategica="Educación"),
            IndicatorRow(tipo="Producto", linea_estrategica="Salud"),
        ]
        
        structure = PDTStructure(
            total_tokens=1000,
            full_text="Sample text",
            indicator_rows=indicators,
        )
        
        assert len(structure.indicator_rows) == 2
        assert structure.indicator_rows[0].tipo == "Resultado"
    
    def test_pdt_structure_with_ppi(self):
        """Test PDTStructure with PPI rows."""
        ppi = [
            PPIRow(linea_estrategica="Educación", costo_total="1000000"),
            PPIRow(linea_estrategica="Salud", costo_total="2000000"),
        ]
        
        structure = PDTStructure(
            total_tokens=1000,
            full_text="Sample text",
            ppi_rows=ppi,
        )
        
        assert len(structure.ppi_rows) == 2
        assert structure.ppi_rows[0].costo_total == "1000000"
    
    def test_pdt_structure_scores(self):
        """Test PDTStructure with hierarchy and sequence scores."""
        structure = PDTStructure(
            total_tokens=1000,
            full_text="Sample text",
            hierarchy_score=1.0,
            sequence_score=0.5,
        )
        
        assert structure.hierarchy_score == 1.0
        assert structure.sequence_score == 0.5

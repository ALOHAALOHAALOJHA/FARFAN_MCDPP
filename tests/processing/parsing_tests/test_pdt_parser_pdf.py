"""
Tests for PDT parser with PDF files.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from farfan_pipeline.processing.pdt_parser import PDTParser
from farfan_pipeline.processing.pdt_structure import PDTStructure


class TestPDTParserPDF:
    """Tests for PDF parsing functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = PDTParser()
    
    @patch('farfan_pipeline.processing.pdt_parser.pymupdf')
    def test_extract_text_from_pdf_success(self, mock_pymupdf):
        """Test successful text extraction from PDF."""
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Sample page text"
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_pymupdf.open.return_value = mock_doc
        
        text = self.parser._extract_text_from_pdf(Path("sample.pdf"))
        
        assert "Sample page text" in text
        mock_pymupdf.open.assert_called_once()
        mock_doc.close.assert_called_once()
    
    @patch('farfan_pipeline.processing.pdt_parser.pymupdf')
    def test_extract_text_from_pdf_multiple_pages(self, mock_pymupdf):
        """Test extracting text from multi-page PDF."""
        mock_doc = MagicMock()
        mock_page1 = MagicMock()
        mock_page1.get_text.return_value = "Page 1 text"
        mock_page2 = MagicMock()
        mock_page2.get_text.return_value = "Page 2 text"
        
        mock_doc.__len__.return_value = 2
        
        def get_page(index):
            return mock_page1 if index == 0 else mock_page2
        
        mock_doc.__getitem__.side_effect = get_page
        mock_pymupdf.open.return_value = mock_doc
        
        text = self.parser._extract_text_from_pdf(Path("sample.pdf"))
        
        assert "Page 1 text" in text
        assert "Page 2 text" in text
    
    @patch('farfan_pipeline.processing.pdt_parser.pymupdf')
    def test_extract_text_from_pdf_error_handling(self, mock_pymupdf):
        """Test error handling during PDF extraction."""
        mock_pymupdf.open.side_effect = Exception("PDF error")
        
        with pytest.raises(Exception) as exc_info:
            self.parser._extract_text_from_pdf(Path("sample.pdf"))
        
        assert "PDF error" in str(exc_info.value)
    
    @patch('farfan_pipeline.processing.pdt_parser.pymupdf')
    def test_parse_pdf_integration(self, mock_pymupdf):
        """Test full PDF parsing integration."""
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = """
        CAPÍTULO 1: Introducción
        Este es un documento de prueba con varios tokens y números 1 2 3 4 5 6 7 8 9 10
        
        1 Diagnóstico
        1.1 Situación actual
        
        El diagnóstico muestra datos 1 2 3 4 5 y análisis con referencias [1].
        """
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_pymupdf.open.return_value = mock_doc
        
        with patch.object(Path, 'exists', return_value=True):
            result = self.parser.parse_pdf("sample.pdf")
        
        assert isinstance(result, PDTStructure)
        assert result.total_tokens > 0
        assert len(result.full_text) > 0
    
    def test_parse_pdf_file_not_found(self):
        """Test parsing PDF when file does not exist."""
        with pytest.raises(FileNotFoundError):
            self.parser.parse_pdf("nonexistent.pdf")


class TestPDTParserEndToEnd:
    """End-to-end tests with realistic PDT content."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = PDTParser()
    
    def test_parse_realistic_pdt_content(self):
        """Test parsing realistic PDT content."""
        content = """
        PLAN DE DESARROLLO TERRITORIAL 2024-2027
        "HACIA UN FUTURO SOSTENIBLE"
        
        CAPÍTULO 1: MARCO GENERAL
        
        Este capítulo establece el contexto del plan de desarrollo territorial
        con lineamientos estratégicos y normativos para el periodo 2024-2027.
        El presupuesto total asciende a 50.000 millones de pesos distribuidos
        en cuatro vigencias fiscales según las líneas estratégicas definidas.
        
        1 PARTE GENERAL
        1.1 Diagnóstico Territorial
        1.1.1 Situación actual del municipio
        
        El diagnóstico territorial identifica las principales problemáticas
        del municipio mediante análisis de contexto sociodemográfico,
        económico y ambiental. Se consultaron fuentes oficiales [1] [2] [3]
        y se realizaron estudios técnicos con datos de los últimos 5 años.
        La población actual es de 45.000 habitantes con una tasa de crecimiento
        del 1.5% anual. Los indicadores sociales muestran necesidades en
        educación (cobertura 85%), salud (85% afiliados) y empleo (tasa 12%).
        
        1.2 Parte Estratégica
        1.2.1 Visión del municipio
        
        Ser un municipio próspero, equitativo y sostenible para el año 2027,
        con altos estándares de calidad de vida y desarrollo humano integral.
        
        1.2.2 Objetivos estratégicos
        
        Los objetivos estratégicos se organizan en cuatro líneas estratégicas:
        educación de calidad, salud para todos, desarrollo económico local,
        y ambiente sostenible. Cada línea tiene programas específicos con
        metas cuantificables e indicadores de seguimiento y evaluación.
        
        Línea estratégica 1: EDUCACIÓN DE CALIDAD
        
        Garantizar el acceso universal a educación de calidad mediante
        infraestructura adecuada, formación docente y recursos pedagógicos.
        Presupuesto línea: 15.000 millones. Meta cobertura: 95% en 2027.
        Incluye 5 programas y 12 proyectos estratégicos con inversión de
        5.000 millones en 2024, 4.000 en 2025, 3.000 en 2026 y 3.000 en 2027.
        
        PROGRAMA 1: Infraestructura Educativa
        
        Construcción y adecuación de instituciones educativas para mejorar
        ambientes de aprendizaje. Inversión total: 8.000 millones de pesos.
        
        Línea estratégica 2: SALUD PARA TODOS
        
        Ampliar la cobertura y mejorar la calidad de servicios de salud
        mediante atención primaria, prevención y promoción. Presupuesto:
        12.000 millones distribuidos en infraestructura hospitalaria,
        dotación de equipos médicos y programas de salud pública.
        
        2 PLAN PLURIANUAL DE INVERSIONES
        2.1 Programación presupuestal
        
        Plan Plurianual de Inversiones
        
        Línea Estratégica    Programa         Subprograma    Proyecto             Costo Total    2024    2025    2026    2027    Fuente
        Educación            Infraestructura  Escuelas       Construcción         8000          2000    2000    2000    2000    SGP
        Educación            Calidad          Docentes       Capacitación         7000          2000    2000    1500    1500    Propios
        Salud                Atención         Hospitales     Dotación             6000          1500    1500    1500    1500    Regalías
        Salud                Prevención       Programas      Salud Pública        6000          1500    1500    1500    1500    SGP
        
        3 SISTEMA DE SEGUIMIENTO Y EVALUACIÓN
        3.1 Marco de medición
        
        El sistema de seguimiento utiliza indicadores de resultado, producto
        y gestión para monitorear el cumplimiento de metas del plan. La
        evaluación se realiza anualmente mediante informes de gestión y
        rendición de cuentas a la comunidad. Se definen 45 indicadores
        distribuidos en las cuatro líneas estratégicas del plan.
        
        Matriz de Indicadores
        
        Tipo        Línea Estratégica    Programa         Nombre Indicador           Unidad    Línea Base    Meta    Responsable
        Resultado   Educación            Calidad          Tasa de cobertura          %         85            95      Secretaría Educación
        Resultado   Salud                Atención         Afiliación al régimen      %         85            97      Secretaría Salud
        Producto    Educación            Infraestructura  Escuelas construidas       Número    12            20      Secretaría Planeación
        Producto    Salud                Prevención       Jornadas de vacunación     Número    24            48      Secretaría Salud
        
        Referencias bibliográficas
        [1] DANE - Censo Nacional de Población 2018
        [2] DNP - Fichas de Caracterización Territorial 2023
        [3] Contraloría Municipal - Informes de Gestión 2020-2023
        """
        
        result = self.parser.parse_text(content)
        
        assert isinstance(result, PDTStructure)
        assert result.total_tokens > 100
        
        assert len(result.blocks_found) > 0
        assert any("CAPÍTULO" in block for block in result.blocks_found)
        
        assert len(result.headers) > 0
        assert any(h.level == 1 for h in result.headers)
        assert any(h.level == 2 for h in result.headers)
        
        assert result.hierarchy_score >= 0.0
        assert result.sequence_score >= 0.0
        
        assert "Diagnóstico" in result.sections_found
        assert "Estratégica" in result.sections_found
        assert "PPI" in result.sections_found
        assert "Seguimiento" in result.sections_found
        
        assert result.sections_found["Diagnóstico"].present is True
        assert result.sections_found["Estratégica"].present is True
        
        assert result.sections_found["Diagnóstico"].sources_found > 0

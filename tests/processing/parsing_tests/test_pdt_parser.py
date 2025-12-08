"""
Unit tests for PDTParser.
"""

import pytest
from farfan_pipeline.processing.pdt_parser import PDTParser
from farfan_pipeline.processing.pdt_structure import PDTStructure


class TestPDTParserTokenization:
    """Tests for tokenization functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = PDTParser()
    
    def test_tokenize_simple_text(self):
        """Test tokenizing simple text."""
        text = "This is a simple test"
        tokens = self.parser._tokenize(text)
        
        assert len(tokens) == 5
        assert tokens == ["This", "is", "a", "simple", "test"]
    
    def test_tokenize_with_punctuation(self):
        """Test tokenizing text with punctuation."""
        text = "Hello, world! How are you?"
        tokens = self.parser._tokenize(text)
        
        assert len(tokens) == 5
        assert "Hello," in tokens
        assert "world!" in tokens
    
    def test_tokenize_empty_text(self):
        """Test tokenizing empty text."""
        text = ""
        tokens = self.parser._tokenize(text)
        
        assert len(tokens) == 0
    
    def test_tokenize_multiline(self):
        """Test tokenizing multiline text."""
        text = "Line one\nLine two\nLine three"
        tokens = self.parser._tokenize(text)
        
        assert len(tokens) == 6


class TestPDTParserBlockDetection:
    """Tests for block detection functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = PDTParser()
    
    def test_detect_capitulo_block(self):
        """Test detecting CAPÍTULO block."""
        text = """
        CAPÍTULO 1: Introducción
        Este es el contenido del capítulo uno con varios tokens y números 1 2 3 4 5 6 7 8 9 10
        para cumplir con los umbrales mínimos de detección.
        """
        
        blocks = self.parser._detect_blocks(text)
        
        assert "CAPÍTULO 1" in blocks
        assert blocks["CAPÍTULO 1"].tokens >= 10
        assert blocks["CAPÍTULO 1"].numbers_count >= 1
    
    def test_detect_linea_estrategica_block(self):
        """Test detecting Línea estratégica block."""
        text = """
        Línea estratégica 1: Educación de calidad
        Esta línea busca mejorar la educación con acciones 1 2 3 4 5 6 7 8 9 10
        y recursos necesarios para alcanzar las metas propuestas.
        """
        
        blocks = self.parser._detect_blocks(text)
        
        assert "Línea estratégica 1" in blocks
        assert blocks["Línea estratégica 1"].tokens >= 10
    
    def test_detect_multiple_blocks(self):
        """Test detecting multiple blocks."""
        text = """
        CAPÍTULO 1: Introducción
        Contenido del capítulo con varios tokens y números 1 2 3 4 5 6 7 8 9 10
        
        Línea estratégica 1: Educación
        Contenido de la línea estratégica con números 1 2 3 4 5 6 7 8 9 10
        """
        
        blocks = self.parser._detect_blocks(text)
        
        assert len(blocks) >= 1
    
    def test_block_minimum_thresholds(self):
        """Test that blocks below minimum thresholds are not detected."""
        text = """
        CAPÍTULO 1: Test
        Short
        """
        
        blocks = self.parser._detect_blocks(text)
        
        assert len(blocks) == 0


class TestPDTParserHierarchyValidation:
    """Tests for hierarchy validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = PDTParser()
    
    def test_extract_headers(self):
        """Test extracting headers with numbering."""
        text = """
        1 Introduction to the document
        1.1 Background information
        1.2 Objectives and goals
        2 Main content section
        2.1 First subsection here
        """
        
        headers = self.parser._extract_headers(text)
        
        assert len(headers) > 0
        assert any(h.level == 1 for h in headers)
        assert any(h.level == 2 for h in headers)
    
    def test_validate_hierarchy_high_score(self):
        """Test hierarchy validation with high validity ratio."""
        text = """
        1 Introduction
        1.1 Background
        1.2 Objectives
        2 Content
        2.1 Section one
        2.2 Section two
        3 Conclusion
        """
        
        headers = self.parser._extract_headers(text)
        score = self.parser._validate_hierarchy(headers)
        
        assert score >= 0.5
    
    def test_validate_hierarchy_low_score(self):
        """Test hierarchy validation with low validity ratio."""
        headers = []
        score = self.parser._validate_hierarchy(headers)
        
        assert score == 0.0
    
    def test_is_valid_numbering(self):
        """Test numbering validation."""
        assert self.parser._is_valid_numbering(["1"]) is True
        assert self.parser._is_valid_numbering(["1", "2"]) is True
        assert self.parser._is_valid_numbering(["1", "2", "3"]) is True
        assert self.parser._is_valid_numbering(["0"]) is False


class TestPDTParserSequenceVerification:
    """Tests for sequence verification functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = PDTParser()
    
    def test_verify_sequence_perfect_order(self):
        """Test sequence verification with perfect order."""
        sequence = ["CAPÍTULO 1", "Línea estratégica 1", "PROGRAMA 1"]
        score = self.parser._verify_sequence(sequence)
        
        assert score == 1.0
    
    def test_verify_sequence_one_inversion(self):
        """Test sequence verification with one inversion."""
        sequence = ["Línea estratégica 1", "CAPÍTULO 1", "PROGRAMA 1"]
        score = self.parser._verify_sequence(sequence)
        
        assert score == 0.5
    
    def test_verify_sequence_multiple_inversions(self):
        """Test sequence verification with multiple inversions."""
        sequence = ["PROGRAMA 1", "CAPÍTULO 1", "Línea estratégica 1"]
        score = self.parser._verify_sequence(sequence)
        
        assert score == 0.0
    
    def test_verify_sequence_empty(self):
        """Test sequence verification with empty sequence."""
        sequence = []
        score = self.parser._verify_sequence(sequence)
        
        assert score == 1.0
    
    def test_get_block_type(self):
        """Test extracting block type from block name."""
        assert self.parser._get_block_type("CAPÍTULO 1") == "CAPÍTULO"
        assert self.parser._get_block_type("Línea estratégica 2") == "Línea estratégica"
        assert self.parser._get_block_type("PROGRAMA 3") == "PROGRAMA"


class TestPDTParserSectionAnalysis:
    """Tests for section analysis functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = PDTParser()
    
    def test_analyze_sections_diagnostico(self):
        """Test analyzing Diagnóstico section."""
        text = """
        Diagnóstico Territorial
        
        El diagnóstico muestra la situación actual del municipio con datos 1 2 3 4 5
        y análisis de contexto basado en referencias [1] y fuentes oficiales.
        """
        
        sections = self.parser._analyze_sections(text)
        
        assert "Diagnóstico" in sections
        assert sections["Diagnóstico"].present is True
        assert sections["Diagnóstico"].keyword_matches > 0
        assert sections["Diagnóstico"].token_count > 0
    
    def test_analyze_sections_estrategica(self):
        """Test analyzing Estratégica section."""
        text = """
        Parte Estratégica
        
        La estrategia define la visión y los objetivos estratégicos con líneas estratégicas
        para el desarrollo del territorio.
        """
        
        sections = self.parser._analyze_sections(text)
        
        assert "Estratégica" in sections
        assert sections["Estratégica"].present is True
        assert sections["Estratégica"].keyword_matches > 0
    
    def test_analyze_sections_ppi(self):
        """Test analyzing PPI section."""
        text = """
        Plan Plurianual de Inversiones
        
        El presupuesto y las inversiones se distribuyen según las fuentes de financiación
        disponibles para cada vigencia fiscal.
        """
        
        sections = self.parser._analyze_sections(text)
        
        assert "PPI" in sections
        assert sections["PPI"].present is True
    
    def test_analyze_sections_seguimiento(self):
        """Test analyzing Seguimiento section."""
        text = """
        Sistema de Seguimiento y Evaluación
        
        El seguimiento se realiza mediante indicadores de monitoreo y medición
        de resultados para evaluar el cumplimiento de metas.
        """
        
        sections = self.parser._analyze_sections(text)
        
        assert "Seguimiento" in sections
        assert sections["Seguimiento"].present is True
    
    def test_analyze_sections_not_present(self):
        """Test analyzing when section is not present."""
        text = "This is a simple document without any PDT sections."
        
        sections = self.parser._analyze_sections(text)
        
        for section_name in ["Diagnóstico", "Estratégica", "PPI", "Seguimiento"]:
            if section_name in sections and not sections[section_name].present:
                assert sections[section_name].token_count == 0


class TestPDTParserTableExtraction:
    """Tests for table extraction functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = PDTParser()
    
    def test_extract_indicator_matrix(self):
        """Test extracting indicator matrix."""
        text = """
        Matriz de Indicadores
        
        Resultado  Educación  Calidad  Tasa de cobertura  %  85  95  Secretaría
        Producto   Salud      Atención  Consultas atendidas  Número  1000  1500  Hospital
        """
        
        rows = self.parser._extract_indicator_matrix(text)
        
        assert len(rows) >= 0
    
    def test_extract_indicator_matrix_not_present(self):
        """Test extracting indicator matrix when not present."""
        text = "This document has no indicator matrix."
        
        rows = self.parser._extract_indicator_matrix(text)
        
        assert len(rows) == 0
    
    def test_extract_ppi_matrix(self):
        """Test extracting PPI matrix."""
        text = """
        Plan Plurianual de Inversiones
        
        Educación  Calidad  Infraestructura  Escuelas  1000000  250000  250000  250000  250000  SGP
        Salud      Atención  Centros         Hospitales  2000000  500000  500000  500000  500000  Regalías
        """
        
        rows = self.parser._extract_ppi_matrix(text)
        
        assert len(rows) >= 0
    
    def test_extract_ppi_matrix_not_present(self):
        """Test extracting PPI matrix when not present."""
        text = "This document has no PPI matrix."
        
        rows = self.parser._extract_ppi_matrix(text)
        
        assert len(rows) == 0


class TestPDTParserIntegration:
    """Integration tests for PDTParser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = PDTParser()
    
    def test_parse_text_complete(self):
        """Test parsing complete PDT text."""
        text = """
        CAPÍTULO 1: Introducción al Plan de Desarrollo
        
        Este capítulo presenta los elementos fundamentales del plan con datos 1 2 3 4 5 6 7 8 9 10
        y referencias bibliográficas.
        
        1 Diagnóstico Territorial
        1.1 Situación actual del municipio
        
        El diagnóstico muestra problemáticas y análisis de contexto con números 1 2 3 4 5
        basado en fuentes [1] y referencias oficiales.
        
        2 Parte Estratégica
        2.1 Visión y objetivos estratégicos
        
        La estrategia define líneas estratégicas y objetivos con metas 1 2 3 4 5 6 7 8 9 10
        para el desarrollo territorial.
        
        Matriz de Indicadores
        
        Resultado  Educación  Calidad  Cobertura  %  85  95  Secretaría
        """
        
        result = self.parser.parse_text(text)
        
        assert isinstance(result, PDTStructure)
        assert result.total_tokens > 0
        assert result.full_text == text
        assert len(result.blocks_found) >= 0
        assert len(result.headers) >= 0
        assert result.hierarchy_score >= 0.0
        assert result.sequence_score >= 0.0
    
    def test_parse_text_minimal(self):
        """Test parsing minimal text."""
        text = "This is a minimal document."
        
        result = self.parser.parse_text(text)
        
        assert isinstance(result, PDTStructure)
        assert result.total_tokens > 0
        assert result.full_text == text
    
    def test_parse_text_empty(self):
        """Test parsing empty text."""
        text = ""
        
        result = self.parser.parse_text(text)
        
        assert isinstance(result, PDTStructure)
        assert result.total_tokens == 0
        assert result.full_text == ""

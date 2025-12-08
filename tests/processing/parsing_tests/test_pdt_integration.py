"""
Integration tests for PDT parsing system.

These tests validate the complete flow from text/PDF input to structured output.
"""

import pytest
from farfan_pipeline.processing.pdt_parser import PDTParser
from farfan_pipeline.processing.pdt_structure import (
    PDTStructure,
    BlockInfo,
    HeaderInfo,
    SectionInfo,
    IndicatorRow,
    PPIRow,
)


class TestPDTIntegrationComplete:
    """Complete integration tests for PDT parsing."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = PDTParser()
        self.sample_pdt = self._create_sample_pdt()
    
    def _create_sample_pdt(self) -> str:
        """Create a comprehensive sample PDT for testing."""
        return """
        PLAN DE DESARROLLO MUNICIPAL 2024-2027
        "PROSPERIDAD Y EQUIDAD"
        
        CAPÍTULO 1: GENERALIDADES DEL PLAN
        
        El presente Plan de Desarrollo Municipal establece las directrices
        estratégicas para el cuatrienio 2024-2027 con enfoque en desarrollo
        sostenible, equidad social y crecimiento económico. El plan se
        estructura en diagnóstico territorial, parte estratégica, plan
        plurianual de inversiones y sistema de seguimiento y evaluación.
        Con presupuesto total de 100.000 millones de pesos distribuidos
        en 4 líneas estratégicas, 12 programas y 45 proyectos prioritarios
        para atender las necesidades de 50.000 habitantes del municipio.
        
        1 DIAGNÓSTICO TERRITORIAL
        1.1 Dimensión poblacional y social
        1.1.1 Caracterización demográfica
        
        El diagnóstico territorial identifica la situación actual mediante
        análisis sociodemográfico, económico, ambiental e institucional.
        La población es de 50.000 habitantes con crecimiento del 1.8% anual
        según censo DANE 2018 [1]. Indicadores sociales: educación 83%
        cobertura, salud 87% afiliación, pobreza multidimensional 35.5%.
        Necesidades básicas insatisfechas 28% según DNP [2]. Empleo formal
        42%, informalidad 58%, desempleo juvenil 18%. Problemáticas: déficit
        habitacional 3.500 viviendas, infraestructura educativa obsoleta,
        servicios de salud limitados en zona rural. Fuentes consultadas:
        estadísticas DANE, informes DNP, estudios técnicos Contraloría [3].
        
        1.2 Dimensión económica
        1.2.1 Estructura productiva
        
        Economía basada en agricultura (45%), comercio (30%), servicios (15%)
        e industria (10%). PIB municipal 250.000 millones con crecimiento
        promedio 3.2% últimos 5 años. Principales cultivos: café, plátano,
        cacao. Desafíos: baja productividad, falta tecnificación, débil
        acceso a mercados. Oportunidades: agroindustria, turismo ecológico,
        energías renovables. Datos según estudios sectoriales y análisis
        económico territorial con cifras 2019-2023 [4].
        
        2 PARTE ESTRATÉGICA
        2.1 Visión municipal 2027
        
        Ser un municipio próspero, equitativo y sostenible, líder regional
        en desarrollo humano integral, con alta calidad de vida, economía
        dinámica, ambiente sano y gobernanza participativa para el año 2027.
        
        2.2 Objetivos estratégicos
        2.2.1 Objetivo general del plan
        
        Promover el desarrollo humano sostenible mediante políticas públicas
        integrales que garanticen derechos fundamentales, oportunidades
        económicas y protección ambiental con participación ciudadana.
        
        2.2.2 Objetivos específicos por línea
        
        Los objetivos específicos se organizan en cuatro líneas estratégicas
        con programas, subprogramas y proyectos articulados para cumplir
        las metas del plan y responder a necesidades identificadas en el
        diagnóstico territorial según priorización comunitaria realizada.
        
        Línea estratégica 1: EDUCACIÓN DE CALIDAD
        
        Garantizar acceso universal a educación de calidad en todos los
        niveles mediante infraestructura adecuada, formación docente,
        recursos pedagógicos y ambientes de aprendizaje innovadores.
        Presupuesto línea: 30.000 millones. Meta cobertura educativa:
        pasar de 83% a 95% en 2027. Indicador: tasa de cobertura neta.
        La línea incluye 3 programas con 12 proyectos estratégicos para
        construcción de escuelas, dotación tecnológica y mejoramiento de
        calidad educativa. Inversión programada: 8.000 millones en 2024,
        8.000 en 2025, 7.000 en 2026 y 7.000 en 2027 con recursos SGP,
        propios y cofinanciación. Responsable: Secretaría de Educación.
        
        PROGRAMA 1.1: Infraestructura Educativa
        
        Construcción y adecuación de instituciones educativas para mejorar
        ambientes de aprendizaje y ampliar cobertura en zonas rurales.
        Inversión total: 15.000 millones distribuidos en construcción de
        5 escuelas nuevas, ampliación de 8 colegios existentes y dotación
        de 20 sedes educativas. Meta: 20 infraestructuras intervenidas.
        
        Línea estratégica 2: SALUD PARA TODOS
        
        Ampliar cobertura y mejorar calidad de servicios de salud mediante
        atención primaria, prevención, promoción y red hospitalaria eficiente.
        Presupuesto: 25.000 millones para pasar afiliación de 87% a 97%.
        Incluye programas de infraestructura hospitalaria, dotación médica,
        salud pública, prevención de enfermedades. Inversión: 6.000 millones
        anuales en promedio. Recursos: SGP salud, regalías, propios.
        Responsable: Secretaría de Salud. Meta: hospital nivel II dotado,
        10 puestos de salud mejorados, 48 jornadas de vacunación anuales.
        
        Eje estratégico 3: DESARROLLO ECONÓMICO LOCAL
        
        Fortalecer economía local mediante apoyo al emprendimiento, tecnificación
        agropecuaria, turismo sostenible y acceso a mercados. Presupuesto:
        20.000 millones. Meta: generar 2.000 empleos formales, apoyar 500
        emprendimientos, tecnificar 1.000 hectáreas productivas. Programas:
        fomento empresarial, agricultura sostenible, turismo comunitario.
        
        Línea estratégica 4: AMBIENTE SOSTENIBLE
        
        Proteger recursos naturales y promover desarrollo sostenible mediante
        gestión ambiental, cambio climático, economía circular. Presupuesto:
        25.000 millones. Meta: reforestar 500 hectáreas, reducir emisiones
        20%, implementar 10 proyectos de energías limpias, gestión integral
        de residuos sólidos. Responsable: Secretaría de Ambiente.
        
        3 PLAN PLURIANUAL DE INVERSIONES
        3.1 Programación presupuestal por vigencias
        3.1.1 Distribución de recursos por líneas
        
        El Plan Plurianual de Inversiones programa recursos del cuatrienio
        por líneas estratégicas, programas, subprogramas y proyectos con
        identificación de fuentes de financiación: Sistema General de
        Participaciones (SGP), recursos propios, regalías, cofinanciación
        nacional y departamental, crédito y cooperación internacional.
        Presupuesto total: 100.000 millones distribuidos 30% educación,
        25% salud, 20% desarrollo económico, 25% ambiente sostenible.
        
        Plan Plurianual de Inversiones
        
        Línea Estratégica    Programa              Subprograma           Proyecto                      Costo Total    2024    2025    2026    2027    Fuente de Recursos
        Educación            Infraestructura       Construcción          Nuevas escuelas rurales       15000         4000    4000    3500    3500    SGP Educación
        Educación            Calidad               Formación             Capacitación docentes         10000         2500    2500    2500    2500    Recursos Propios
        Educación            Tecnología            Dotación              Aulas digitales               5000          1500    1500    1000    1000    Cofinanciación
        Salud                Atención              Hospitales            Dotación hospital nivel II    12000         3000    3000    3000    3000    SGP Salud
        Salud                Prevención            Programas             Salud pública preventiva      8000          2000    2000    2000    2000    SGP Salud
        Salud                Infraestructura       Puestos               Mejoramiento puestos rurales  5000          1000    1000    1500    1500    Regalías
        Desarrollo           Emprendimiento        Fomento               Apoyo a emprendedores         8000          2000    2000    2000    2000    Recursos Propios
        Desarrollo           Agropecuario          Tecnificación         Asistencia técnica rural      7000          2000    2000    1500    1500    Cofinanciación
        Desarrollo           Turismo               Promoción             Turismo comunitario           5000          1000    1500    1500    1000    Regalías
        Ambiente             Recursos              Reforestación         Siembra de árboles            10000         2500    2500    2500    2500    Recursos Propios
        Ambiente             Residuos              Gestión               Planta de tratamiento         8000          2000    2000    2000    2000    Cofinanciación
        Ambiente             Energía               Renovables            Paneles solares comunitarios  7000          1500    2000    2000    1500    Regalías
        
        3.2 Fuentes de financiación detalladas
        
        Sistema General de Participaciones: 45.000 millones (45% del total)
        distribuidos en educación 20.000, salud 20.000, agua potable 5.000.
        Recursos propios: 25.000 millones (25%) de rentas municipales e
        impuestos locales. Regalías: 15.000 millones (15%) del Sistema
        General de Regalías para proyectos de desarrollo. Cofinanciación:
        15.000 millones (15%) con recursos de nación y departamento.
        
        4 SISTEMA DE SEGUIMIENTO Y EVALUACIÓN
        4.1 Marco de medición y evaluación
        4.1.1 Indicadores de resultado, producto y gestión
        
        El sistema de seguimiento utiliza 45 indicadores distribuidos en
        las cuatro líneas estratégicas para monitorear cumplimiento de metas
        del plan mediante informes trimestrales, evaluaciones anuales y
        rendición de cuentas a la comunidad. Marco de evaluación incluye
        indicadores de resultado (impacto en población), producto (bienes
        y servicios entregados) y gestión (eficiencia operativa). Cada
        indicador tiene línea base, meta cuatrienio, responsable y formula
        de cálculo. Sistema informático de seguimiento integrado con SUIT
        del DNP para reportes oficiales del plan de desarrollo municipal.
        
        Matriz de Indicadores
        
        Tipo        Línea Estratégica    Programa              Nombre Indicador                    Unidad de Medida    Línea Base    Meta Cuatrienio    Responsable
        Resultado   Educación            Calidad               Tasa de cobertura neta              Porcentaje          83            95                 Secretaría Educación
        Resultado   Salud                Atención              Afiliación al régimen subsidiado    Porcentaje          87            97                 Secretaría Salud
        Resultado   Desarrollo           Emprendimiento        Tasa de empleo formal               Porcentaje          42            52                 Secretaría Desarrollo
        Resultado   Ambiente             Recursos              Cobertura boscosa municipal         Porcentaje          35            45                 Secretaría Ambiente
        Producto    Educación            Infraestructura       Instituciones educativas mejoradas  Número              12            20                 Secretaría Planeación
        Producto    Salud                Prevención            Jornadas de vacunación realizadas   Número              24            48                 Secretaría Salud
        Producto    Desarrollo           Agropecuario          Hectáreas tecnificadas              Número              200           1200               Secretaría Agricultura
        Producto    Ambiente             Energía               Proyectos de energía limpia         Número              0             10                 Secretaría Ambiente
        Gestión     Educación            Calidad               Docentes capacitados anualmente     Número              50            150                Secretaría Educación
        Gestión     Salud                Infraestructura       Puestos de salud dotados            Número              5             15                 Secretaría Salud
        
        4.2 Mecanismos de seguimiento y rendición de cuentas
        
        Informes trimestrales de avance físico y financiero por secretarías.
        Evaluación anual de resultados con auditoría de Contraloría Municipal.
        Audiencias públicas de rendición de cuentas con participación ciudadana.
        Sistema informático SUIT-DNP para reporte oficial del plan municipal.
        Comité de seguimiento con representantes institucionales y comunitarios.
        Veeduría ciudadana para monitoreo de proyectos de inversión pública.
        
        REFERENCIAS BIBLIOGRÁFICAS
        
        [1] DANE - Censo Nacional de Población y Vivienda 2018
        [2] DNP - Fichas de Caracterización Territorial 2023
        [3] Contraloría Municipal - Informes de Gestión Fiscal 2020-2023
        [4] Estudios Sectoriales - Análisis Económico Territorial 2023
        """
    
    def test_complete_pdt_parsing(self):
        """Test complete parsing of PDT document."""
        result = self.parser.parse_text(self.sample_pdt)
        
        assert isinstance(result, PDTStructure)
        assert result.total_tokens > 500
        assert len(result.full_text) > 1000
    
    def test_tokenization_accuracy(self):
        """Test tokenization produces accurate token count."""
        result = self.parser.parse_text(self.sample_pdt)
        
        manual_tokens = self.sample_pdt.split()
        
        assert result.total_tokens == len(manual_tokens)
    
    def test_block_detection_capitulos(self):
        """Test detection of CAPÍTULO blocks."""
        result = self.parser.parse_text(self.sample_pdt)
        
        capitulo_blocks = [b for b in result.blocks_found if "CAPÍTULO" in b]
        
        assert len(capitulo_blocks) > 0
        
        for block_name in capitulo_blocks:
            block = result.blocks_found[block_name]
            assert block.tokens >= self.parser.MIN_BLOCK_TOKENS
            assert block.numbers_count >= self.parser.MIN_BLOCK_NUMBERS
    
    def test_block_detection_lineas_estrategicas(self):
        """Test detection of Línea estratégica blocks."""
        result = self.parser.parse_text(self.sample_pdt)
        
        linea_blocks = [b for b in result.blocks_found if "Línea estratégica" in b]
        
        assert len(linea_blocks) >= 2
    
    def test_hierarchy_extraction(self):
        """Test extraction of hierarchical headers."""
        result = self.parser.parse_text(self.sample_pdt)
        
        assert len(result.headers) > 0
        
        level_1_headers = [h for h in result.headers if h.level == 1]
        level_2_headers = [h for h in result.headers if h.level == 2]
        level_3_headers = [h for h in result.headers if h.level == 3]
        
        assert len(level_1_headers) > 0
        assert len(level_2_headers) > 0
        assert len(level_3_headers) > 0
    
    def test_hierarchy_validation_score(self):
        """Test hierarchy validation scoring."""
        result = self.parser.parse_text(self.sample_pdt)
        
        assert result.hierarchy_score >= 0.0
        assert result.hierarchy_score <= 1.0
        
        valid_headers = sum(1 for h in result.headers if h.valid_numbering)
        if len(result.headers) > 0:
            expected_score = 1.0 if valid_headers / len(result.headers) >= 0.8 else (
                0.5 if valid_headers / len(result.headers) >= 0.5 else 0.0
            )
            assert result.hierarchy_score == expected_score
    
    def test_sequence_verification_score(self):
        """Test sequence verification scoring."""
        result = self.parser.parse_text(self.sample_pdt)
        
        assert result.sequence_score >= 0.0
        assert result.sequence_score <= 1.0
    
    def test_section_diagnostico_detection(self):
        """Test detection of Diagnóstico section."""
        result = self.parser.parse_text(self.sample_pdt)
        
        assert "Diagnóstico" in result.sections_found
        diagnostico = result.sections_found["Diagnóstico"]
        
        assert diagnostico.present is True
        assert diagnostico.token_count > 0
        assert diagnostico.keyword_matches > 0
        assert diagnostico.number_count > 0
        assert diagnostico.sources_found > 0
    
    def test_section_estrategica_detection(self):
        """Test detection of Estratégica section."""
        result = self.parser.parse_text(self.sample_pdt)
        
        assert "Estratégica" in result.sections_found
        estrategica = result.sections_found["Estratégica"]
        
        assert estrategica.present is True
        assert estrategica.token_count > 0
        assert estrategica.keyword_matches > 0
    
    def test_section_ppi_detection(self):
        """Test detection of PPI section."""
        result = self.parser.parse_text(self.sample_pdt)
        
        assert "PPI" in result.sections_found
        ppi = result.sections_found["PPI"]
        
        assert ppi.present is True
        assert ppi.token_count > 0
        assert ppi.keyword_matches > 0
    
    def test_section_seguimiento_detection(self):
        """Test detection of Seguimiento section."""
        result = self.parser.parse_text(self.sample_pdt)
        
        assert "Seguimiento" in result.sections_found
        seguimiento = result.sections_found["Seguimiento"]
        
        assert seguimiento.present is True
        assert seguimiento.token_count > 0
        assert seguimiento.keyword_matches > 0
    
    def test_indicator_matrix_extraction(self):
        """Test extraction of indicator matrix."""
        result = self.parser.parse_text(self.sample_pdt)
        
        assert len(result.indicator_rows) > 0
        
        for row in result.indicator_rows:
            assert isinstance(row, IndicatorRow)
    
    def test_ppi_matrix_extraction(self):
        """Test extraction of PPI matrix."""
        result = self.parser.parse_text(self.sample_pdt)
        
        assert len(result.ppi_rows) > 0
        
        for row in result.ppi_rows:
            assert isinstance(row, PPIRow)
    
    def test_data_consistency(self):
        """Test consistency between different extracted elements."""
        result = self.parser.parse_text(self.sample_pdt)
        
        assert len(result.block_sequence) == len(result.blocks_found)
        
        for block_name in result.block_sequence:
            assert block_name in result.blocks_found
    
    def test_all_sections_analyzed(self):
        """Test that all expected sections are analyzed."""
        result = self.parser.parse_text(self.sample_pdt)
        
        expected_sections = ["Diagnóstico", "Estratégica", "PPI", "Seguimiento"]
        
        for section in expected_sections:
            assert section in result.sections_found
    
    def test_numeric_data_extraction(self):
        """Test that numeric data is properly extracted."""
        result = self.parser.parse_text(self.sample_pdt)
        
        for block in result.blocks_found.values():
            assert block.numbers_count >= 0
        
        for section in result.sections_found.values():
            assert section.number_count >= 0
    
    def test_sources_detection(self):
        """Test detection of bibliographic sources."""
        result = self.parser.parse_text(self.sample_pdt)
        
        total_sources = sum(
            section.sources_found 
            for section in result.sections_found.values()
        )
        
        assert total_sources > 0

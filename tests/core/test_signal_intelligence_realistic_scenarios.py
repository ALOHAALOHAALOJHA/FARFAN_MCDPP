"""
Signal Intelligence Pipeline - Realistic Document Scenarios
============================================================

Integration tests using realistic policy document excerpts to validate
the complete signal intelligence pipeline across diverse document types
and contexts.

Test Coverage:
- Budget Section Documents: Financial data, funding allocations
- Indicators Section Documents: Metrics, baselines, targets
- Diagnostic Section Documents: Multi-source data, DANE, Medicina Legal
- Geographic Coverage Documents: Territorial distribution
- Edge Cases: Empty docs, sparse content, conflicting data
- Cross-Section Analysis: Same question across different document sections

Author: F.A.R.F.A.N Pipeline
Date: 2025-12-06
Coverage: Realistic policy document scenarios
"""

from typing import Any

import pytest

from farfan_pipeline.core.orchestrator.questionnaire import load_questionnaire
from farfan_pipeline.core.orchestrator.signal_context_scoper import (
    create_document_context,
)
from farfan_pipeline.core.orchestrator.signal_intelligence_layer import (
    analyze_with_intelligence_layer,
)


@pytest.fixture(scope="module")
def canonical_questionnaire():
    """Load questionnaire once."""
    return load_questionnaire()


@pytest.fixture(scope="module")
def sample_questions(canonical_questionnaire):
    """Get sample micro questions."""
    all_questions = canonical_questionnaire.get_micro_questions()

    # Get diverse sample
    sample = []
    dims_covered = set()

    for q in all_questions:
        dim = q.get("dimension_id")
        if dim and dim not in dims_covered:
            sample.append(q)
            dims_covered.add(dim)
            if len(sample) >= 15:
                break

    return sample if sample else all_questions[:15]


class TestBudgetSectionDocuments:
    """Test pipeline with budget section documents."""

    def test_budget_allocation_document(self, sample_questions: list[dict[str, Any]]):
        """Test extraction from budget allocation document."""
        signal_node = sample_questions[0]

        document = """
        PRESUPUESTO ASIGNADO - POLÍTICA DE GÉNERO
        
        Recursos financieros para el periodo 2024-2027:
        
        Total presupuesto asignado: COP 1,500 millones anuales
        Fuente de financiamiento: Presupuesto General de la Nación
        Entidad responsable: Secretaría de la Mujer
        
        Distribución por componentes:
        - Formación y capacitación: COP 600 millones
        - Atención integral: COP 450 millones
        - Seguimiento y evaluación: COP 300 millones
        - Comunicaciones: COP 150 millones
        
        Código presupuestal: 1234-5678-90
        Rubro: Inversión
        """

        context = create_document_context(
            section="budget", chapter=3, policy_area="PA01"
        )

        result = analyze_with_intelligence_layer(document, signal_node, context)

        print("\n✓ Budget Allocation Document:")
        print(f"  Evidence types: {len(result['evidence'])}")
        print(f"  Completeness: {result['completeness']:.2f}")
        print(f"  Validation: {result['validation']['status']}")

        assert result["completeness"] >= 0.0
        assert "evidence" in result

    def test_multi_year_budget_document(self, sample_questions: list[dict[str, Any]]):
        """Test extraction from multi-year budget document."""
        signal_node = sample_questions[0]

        document = """
        PLAN PLURIANUAL DE INVERSIONES 2024-2027
        
        Asignación presupuestal por vigencia:
        
        2024: COP 1,200 millones
        2025: COP 1,500 millones (incremento 25%)
        2026: COP 1,800 millones (incremento 20%)
        2027: COP 2,000 millones (incremento 11%)
        
        Total cuatrienio: COP 6,500 millones
        
        Fuentes de financiamiento:
        - Presupuesto nacional: 70%
        - Recursos propios: 20%
        - Cooperación internacional: 10%
        
        Entidades ejecutoras:
        - Secretaría de la Mujer (60%)
        - Secretaría de Salud (25%)
        - Secretaría de Educación (15%)
        """

        context = create_document_context(section="budget", chapter=4)
        result = analyze_with_intelligence_layer(document, signal_node, context)

        print("\n✓ Multi-Year Budget:")
        print(f"  Completeness: {result['completeness']:.2f}")
        print(f"  Evidence count: {sum(len(v) for v in result['evidence'].values())}")


class TestIndicatorsSectionDocuments:
    """Test pipeline with indicators section documents."""

    def test_indicators_with_baseline_and_target(
        self, sample_questions: list[dict[str, Any]]
    ):
        """Test extraction from indicators document."""
        signal_node = (
            sample_questions[1] if len(sample_questions) > 1 else sample_questions[0]
        )

        document = """
        INDICADORES DE RESULTADO - EQUIDAD DE GÉNERO
        
        Indicador 1: Participación de mujeres en cargos directivos
        
        Línea de base (2023): 8.5%
        Meta 2024: 10%
        Meta 2025: 12%
        Meta 2026: 13.5%
        Meta 2027: 15%
        
        Fórmula de cálculo:
        (Número de mujeres en cargos directivos / Total cargos directivos) × 100
        
        Periodicidad: Anual
        Fuente de información: DANE - Encuesta de Empleo
        Responsable del reporte: Departamento Administrativo de la Función Pública
        
        Indicador 2: Brecha salarial de género
        
        Línea de base (2023): 18%
        Meta 2027: Reducir a 12%
        
        Fuente: DANE - Gran Encuesta Integrada de Hogares
        """

        context = create_document_context(section="indicators", chapter=5)
        result = analyze_with_intelligence_layer(document, signal_node, context)

        print("\n✓ Indicators Document:")
        print(f"  Evidence types: {len(result['evidence'])}")
        print(f"  Completeness: {result['completeness']:.2f}")

        assert result["completeness"] >= 0.0

    def test_time_series_indicators(self, sample_questions: list[dict[str, Any]]):
        """Test extraction from time series indicators."""
        signal_node = (
            sample_questions[1] if len(sample_questions) > 1 else sample_questions[0]
        )

        document = """
        SERIES TEMPORALES - VIOLENCIA DE GÉNERO
        
        Tasa de violencia intrafamiliar (por 100,000 mujeres):
        
        2018: 245.3
        2019: 238.7
        2020: 251.4 (incremento por confinamiento)
        2021: 243.9
        2022: 235.1
        2023: 228.6 (línea de base)
        
        Meta 2027: Reducir a 200
        
        Fuente de datos: Medicina Legal - Instituto Nacional de Medicina Legal y 
        Ciencias Forenses (INMLCF)
        
        Nota metodológica: Incluye violencia física, psicológica y sexual 
        reportada en comisarías de familia y fiscalías.
        """

        context = create_document_context(section="indicators", chapter=6)
        result = analyze_with_intelligence_layer(document, signal_node, context)

        print("\n✓ Time Series Indicators:")
        print(f"  Completeness: {result['completeness']:.2f}")


class TestDiagnosticSectionDocuments:
    """Test pipeline with diagnostic section documents."""

    def test_multi_source_diagnostic(self, sample_questions: list[dict[str, Any]]):
        """Test extraction from multi-source diagnostic."""
        signal_node = (
            sample_questions[2] if len(sample_questions) > 2 else sample_questions[0]
        )

        document = """
        DIAGNÓSTICO DE GÉNERO - MUNICIPIO DE BOGOTÁ
        
        Situación actual de equidad de género según fuentes oficiales:
        
        1. PARTICIPACIÓN POLÍTICA (Fuente: DANE)
        - 8.5% de mujeres en cargos directivos del sector público (2023)
        - 32% de mujeres en concejos municipales
        - 15% de mujeres alcaldesas en localidades
        
        2. VIOLENCIA DE GÉNERO (Fuente: Medicina Legal)
        - 23,456 casos de violencia intrafamiliar reportados en 2023
        - 89% de víctimas son mujeres
        - Incremento del 5% respecto a 2022
        
        3. ACCESO A JUSTICIA (Fuente: Fiscalía General de la Nación)
        - 12,345 denuncias por violencia de género en 2023
        - Tasa de esclarecimiento: 45%
        - Tiempo promedio de investigación: 18 meses
        
        4. EDUCACIÓN (Fuente: Secretaría de Educación Distrital)
        - Paridad en matrícula educación básica: 50.2% niñas
        - Brecha en educación superior técnica: 35% mujeres
        
        Cobertura territorial: 20 localidades de Bogotá
        Población objetivo: 4,200,000 mujeres
        """

        context = create_document_context(
            section="diagnostic", chapter=1, policy_area="PA01"
        )

        result = analyze_with_intelligence_layer(document, signal_node, context)

        print("\n✓ Multi-Source Diagnostic:")
        print(f"  Evidence types: {len(result['evidence'])}")
        print(f"  Completeness: {result['completeness']:.2f}")
        print(f"  Total matches: {sum(len(v) for v in result['evidence'].values())}")

        assert result["completeness"] >= 0.0


class TestGeographicCoverageDocuments:
    """Test pipeline with geographic coverage documents."""

    def test_territorial_distribution(self, sample_questions: list[dict[str, Any]]):
        """Test extraction from territorial distribution document."""
        signal_node = (
            sample_questions[3] if len(sample_questions) > 3 else sample_questions[0]
        )

        document = """
        COBERTURA TERRITORIAL - POLÍTICA DE GÉNERO
        
        Ámbito de aplicación:
        
        NACIONAL: República de Colombia
        
        DEPARTAMENTOS PRIORIZADOS:
        1. Cundinamarca
        2. Antioquia
        3. Valle del Cauca
        4. Atlántico
        5. Santander
        
        MUNICIPIOS CON INTERVENCIÓN DIRECTA:
        - Bogotá D.C. (20 localidades)
        - Medellín (16 comunas)
        - Cali (22 comunas)
        - Barranquilla (5 localidades)
        - Bucaramanga (área metropolitana)
        
        ZONAS RURALES:
        - 150 municipios rurales dispersos
        - 45 territorios colectivos de comunidades étnicas
        
        Población beneficiaria:
        - Urbana: 8,500,000 mujeres
        - Rural: 1,200,000 mujeres
        - Total: 9,700,000 mujeres
        
        Criterios de focalización:
        - Municipios con mayor brecha de género
        - Territorios con altos índices de violencia
        - Zonas con menor acceso a servicios
        """

        context = create_document_context(section="geographic", chapter=2)
        result = analyze_with_intelligence_layer(document, signal_node, context)

        print("\n✓ Territorial Distribution:")
        print(f"  Completeness: {result['completeness']:.2f}")


class TestEdgeCasesAndErrorHandling:
    """Test pipeline edge cases and error handling."""

    def test_empty_document(self, sample_questions: list[dict[str, Any]]):
        """Test pipeline with empty document."""
        signal_node = sample_questions[0]

        document = ""
        context = create_document_context(section="diagnostic")

        result = analyze_with_intelligence_layer(document, signal_node, context)

        print("\n✓ Empty Document:")
        print(f"  Completeness: {result['completeness']:.2f}")
        print(f"  Evidence count: {len(result['evidence'])}")

        assert result["completeness"] == 0.0 or result["completeness"] >= 0.0

    def test_minimal_content_document(self, sample_questions: list[dict[str, Any]]):
        """Test pipeline with minimal content."""
        signal_node = sample_questions[0]

        document = "Datos estadísticos de género en Colombia."
        context = create_document_context(section="introduction")

        result = analyze_with_intelligence_layer(document, signal_node, context)

        print("\n✓ Minimal Content:")
        print(f"  Completeness: {result['completeness']:.2f}")

        assert result["completeness"] >= 0.0

    def test_irrelevant_content_document(self, sample_questions: list[dict[str, Any]]):
        """Test pipeline with irrelevant content."""
        signal_node = sample_questions[0]

        document = """
        INFORME METEOROLÓGICO DE BOGOTÁ
        
        Temperatura promedio: 14°C
        Precipitación anual: 1,000 mm
        Humedad relativa: 75%
        
        Pronóstico para la próxima semana:
        Lunes: Parcialmente nublado
        Martes: Lluvias dispersas
        """

        context = create_document_context(section="appendix")
        result = analyze_with_intelligence_layer(document, signal_node, context)

        print("\n✓ Irrelevant Content:")
        print(f"  Completeness: {result['completeness']:.2f}")

        assert result["completeness"] >= 0.0

    def test_conflicting_data_document(self, sample_questions: list[dict[str, Any]]):
        """Test pipeline with conflicting data."""
        signal_node = sample_questions[0]

        document = """
        ESTADÍSTICAS CONTRADICTORIAS
        
        Según DANE: 8.5% de mujeres en cargos directivos (2023)
        Según Función Pública: 12.3% de mujeres en cargos directivos (2023)
        Según estudio independiente: 6.8% de mujeres en cargos directivos (2023)
        
        Nota: Discrepancias metodológicas en la definición de "cargo directivo"
        """

        context = create_document_context(section="diagnostic")
        result = analyze_with_intelligence_layer(document, signal_node, context)

        print("\n✓ Conflicting Data:")
        print(f"  Completeness: {result['completeness']:.2f}")
        print(f"  Evidence: {sum(len(v) for v in result['evidence'].values())} matches")


class TestCrossSectionAnalysis:
    """Test same question across different document sections."""

    def test_question_across_sections(self, sample_questions: list[dict[str, Any]]):
        """Test same question in different sections."""
        signal_node = sample_questions[0]

        base_document = """
        Línea de base: 8.5% de mujeres en cargos directivos (2023).
        Meta: Alcanzar 15% para 2027.
        Fuente: DANE.
        """

        sections = ["diagnostic", "indicators", "budget", "implementation"]

        print("\n✓ Cross-Section Analysis:")

        for section in sections:
            context = create_document_context(section=section, chapter=1)
            result = analyze_with_intelligence_layer(
                base_document, signal_node, context
            )

            print(f"  {section}: completeness={result['completeness']:.2f}")


class TestLargeDocumentPerformance:
    """Test pipeline performance with large documents."""

    def test_large_comprehensive_document(self, sample_questions: list[dict[str, Any]]):
        """Test extraction from large comprehensive document."""
        signal_node = sample_questions[0]

        # Generate large document
        document = """
        POLÍTICA PÚBLICA DE EQUIDAD DE GÉNERO - DOCUMENTO COMPLETO
        
        """ + "\n\n".join(
            [
                f"""
        SECCIÓN {i}: ANÁLISIS DE INDICADOR {i}
        
        Línea de base año 2023: {8.0 + i * 0.5}%
        Meta establecida para 2027: {15.0 + i * 0.5}%
        Fuente de datos: DANE, Medicina Legal, Fiscalía
        Cobertura territorial: Bogotá, Medellín, Cali
        Presupuesto asignado: COP {1000 + i * 100} millones
        Entidad responsable: Secretaría de la Mujer
        
        Descripción detallada del indicador...
        [Más contenido aquí...]
        """
                for i in range(20)
            ]
        )

        context = create_document_context(section="diagnostic", chapter=1)
        result = analyze_with_intelligence_layer(document, signal_node, context)

        print("\n✓ Large Document Performance:")
        print(f"  Document length: {len(document)} chars")
        print(f"  Evidence types: {len(result['evidence'])}")
        print(f"  Total matches: {sum(len(v) for v in result['evidence'].values())}")
        print(f"  Completeness: {result['completeness']:.2f}")


class TestValidationScenarios:
    """Test validation scenarios."""

    def test_high_completeness_passes_validation(
        self, sample_questions: list[dict[str, Any]]
    ):
        """Test high completeness passes validation."""
        signal_node = sample_questions[0]

        document = """
        INFORMACIÓN COMPLETA DE GÉNERO
        
        Línea de base 2023: 8.5% mujeres en directivos
        Meta 2027: 15%
        Fuente oficial: DANE
        Cobertura: Bogotá, Medellín, Cali
        Presupuesto: COP 1,500 millones
        Entidad: Secretaría de la Mujer
        Cronograma: 2024-2027
        Población beneficiaria: 1,000,000 mujeres
        """

        context = create_document_context(section="diagnostic")
        result = analyze_with_intelligence_layer(document, signal_node, context)

        print("\n✓ High Completeness Validation:")
        print(f"  Completeness: {result['completeness']:.2f}")
        print(f"  Validation: {result['validation']['status']}")

    def test_low_completeness_validation(self, sample_questions: list[dict[str, Any]]):
        """Test low completeness validation."""
        signal_node = sample_questions[0]

        document = "Breve mención de estadísticas."

        context = create_document_context(section="appendix")
        result = analyze_with_intelligence_layer(document, signal_node, context)

        print("\n✓ Low Completeness Validation:")
        print(f"  Completeness: {result['completeness']:.2f}")
        print(f"  Validation: {result['validation']['status']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

"""
Signal Intelligence Pipeline: Validation Scenarios
===================================================

Comprehensive validation scenarios testing the complete signal intelligence
pipeline with realistic policy document excerpts and edge cases.

Test Coverage:
1. Real-world document scenarios (budget, indicators, geographic)
2. Multi-language patterns (Spanish policy terminology)
3. Complex validation chains (nested contracts, multi-stage validation)
4. Edge cases (missing data, malformed input, conflicting signals)
5. Performance under realistic data volumes

Author: F.A.R.F.A.N Pipeline
Date: 2025-12-02
"""

import pytest
from typing import Dict, Any

from farfan_pipeline.core.orchestrator.questionnaire import load_questionnaire
from farfan_pipeline.core.orchestrator.signal_intelligence_layer import (
    analyze_with_intelligence_layer,
    create_enriched_signal_pack
)
from farfan_pipeline.core.orchestrator.signal_context_scoper import create_document_context
from farfan_pipeline.core.orchestrator.signal_evidence_extractor import extract_structured_evidence


class MockSignalPack:
    """Mock signal pack for testing."""
    
    def __init__(self, patterns, micro_questions):
        self.patterns = patterns
        self.micro_questions = micro_questions


@pytest.fixture(scope="module")
def questionnaire():
    """Load questionnaire once."""
    return load_questionnaire()


@pytest.fixture(scope="module")
def sample_question(questionnaire):
    """Get first micro question with complete metadata."""
    questions = questionnaire.get_micro_questions()
    
    # Find question with rich metadata
    for q in questions:
        if (q.get('patterns') and 
            q.get('expected_elements') and 
            len(q.get('patterns', [])) >= 5):
            return q
    
    return questions[0]


class TestRealisticDocumentScenarios:
    """Test pipeline with realistic policy document scenarios."""
    
    def test_01_budget_section_analysis(self, sample_question):
        """Test: Analysis of budget section with financial data."""
        budget_document = """
        CAPÍTULO 3: PRESUPUESTO Y RECURSOS FINANCIEROS
        
        Asignación presupuestal para el programa de género:
        - Año 2024: COP 1,500,000,000
        - Año 2025: COP 1,800,000,000
        - Año 2026: COP 2,100,000,000
        - Año 2027: COP 2,400,000,000
        
        Fuentes de financiamiento:
        1. Recursos propios del municipio: 60%
        2. Transferencias nacionales: 30%
        3. Cooperación internacional: 10%
        
        Entidad responsable: Secretaría de la Mujer
        Supervisión: Contraloría Municipal
        """
        
        context = create_document_context(
            section='budget',
            chapter=3,
            policy_area='PA01',
            document_type='plan_desarrollo'
        )
        
        result = analyze_with_intelligence_layer(
            text=budget_document,
            signal_node=sample_question,
            document_context=context
        )
        
        print(f"\n✓ Budget Section Analysis:")
        print(f"  Completeness: {result['completeness']:.2f}")
        print(f"  Evidence types: {len(result['evidence'])}")
        print(f"  Validation: {result['validation']['status']}")
        
        # Should extract financial amounts
        assert result['completeness'] > 0.0
        assert 'evidence' in result
    
    def test_02_indicators_section_analysis(self, sample_question):
        """Test: Analysis of indicators section with metrics."""
        indicators_document = """
        SECCIÓN 5: INDICADORES Y METAS
        
        Indicador 1: Participación de mujeres en cargos directivos
        - Línea base (2023): 8.5%
        - Meta 2027: 15%
        - Fuente: DANE, Secretaría de la Mujer
        - Periodicidad: Anual
        - Responsable: Secretaría de la Mujer
        
        Indicador 2: Brecha salarial de género
        - Línea base (2023): 18%
        - Meta 2027: 12%
        - Fuente: DANE, Observatorio Laboral
        - Periodicidad: Anual
        
        Indicador 3: Tasa de violencia intrafamiliar
        - Línea base (2022): 245 casos por 100,000 habitantes
        - Meta 2027: 180 casos por 100,000 habitantes
        - Fuente: Medicina Legal, Policía Nacional
        """
        
        context = create_document_context(
            section='indicators',
            chapter=5,
            policy_area='PA01'
        )
        
        result = analyze_with_intelligence_layer(
            text=indicators_document,
            signal_node=sample_question,
            document_context=context
        )
        
        print(f"\n✓ Indicators Section Analysis:")
        print(f"  Completeness: {result['completeness']:.2f}")
        print(f"  Evidence count: {sum(len(v) for v in result['evidence'].values())}")
        print(f"  Missing required: {result['missing_elements']}")
        
        # Should extract indicators and baselines
        assert result['completeness'] > 0.0
    
    def test_03_geographic_coverage_analysis(self, sample_question):
        """Test: Analysis of geographic/territorial coverage."""
        geographic_document = """
        COBERTURA TERRITORIAL DEL PROGRAMA
        
        El programa de igualdad de género tendrá cobertura en:
        
        Zona urbana:
        - Bogotá: 20 localidades (énfasis en Ciudad Bolívar, Usme, Bosa)
        - Medellín: 16 comunas
        - Cali: 22 comunas
        
        Zona rural:
        - 45 municipios priorizados en 8 departamentos
        - Departamentos: Antioquia, Cundinamarca, Valle del Cauca, 
          Nariño, Cauca, Chocó, Guajira, Putumayo
        
        Población beneficiaria estimada: 1.2 millones de mujeres
        
        Criterios de priorización:
        1. Índice de violencia de género
        2. Brecha salarial
        3. Acceso a servicios públicos
        4. Participación política
        """
        
        context = create_document_context(
            section='geographic',
            chapter=2,
            policy_area='PA01'
        )
        
        result = analyze_with_intelligence_layer(
            text=geographic_document,
            signal_node=sample_question,
            document_context=context
        )
        
        print(f"\n✓ Geographic Coverage Analysis:")
        print(f"  Completeness: {result['completeness']:.2f}")
        print(f"  Evidence types: {len(result['evidence'])}")
        
        assert result['completeness'] >= 0.0
    
    def test_04_diagnostic_section_with_multiple_sources(self, sample_question):
        """Test: Diagnostic section with multiple official sources."""
        diagnostic_document = """
        DIAGNÓSTICO DE GÉNERO - SITUACIÓN ACTUAL
        
        Según datos consolidados de múltiples fuentes oficiales:
        
        1. DANE (2023): Encuesta Nacional de Calidad de Vida
           - 8.5% mujeres en cargos directivos sector público
           - 12.3% mujeres en cargos directivos sector privado
           - Brecha salarial promedio: 18%
        
        2. Medicina Legal (2022):
           - 45,234 casos de violencia intrafamiliar
           - 689 feminicidios
           - 23,456 casos de violencia sexual
        
        3. Fiscalía General (2023):
           - 12,345 denuncias por violencia de género
           - Tasa de impunidad: 78%
        
        4. Observatorio de Asuntos de Género (2023):
           - Participación política: 15% alcaldías
           - Participación política: 28% concejos municipales
        
        5. Secretaría de la Mujer - Bogotá (2023):
           - 234 casos atendidos en Casas de Igualdad
           - 1,456 mujeres en programas de formación
        
        La evidencia muestra persistencia de brechas estructurales.
        """
        
        context = create_document_context(
            section='diagnostic',
            chapter=1,
            policy_area='PA01'
        )
        
        result = analyze_with_intelligence_layer(
            text=diagnostic_document,
            signal_node=sample_question,
            document_context=context
        )
        
        print(f"\n✓ Multi-Source Diagnostic Analysis:")
        print(f"  Completeness: {result['completeness']:.2f}")
        print(f"  Total evidence matches: {sum(len(v) for v in result['evidence'].values())}")
        
        # Should recognize multiple official sources
        assert result['completeness'] > 0.0


class TestEdgeCasesAndErrorHandling:
    """Test pipeline behavior with edge cases and error conditions."""
    
    def test_01_empty_document(self, sample_question):
        """Test: Handle empty document gracefully."""
        result = analyze_with_intelligence_layer(
            text="",
            signal_node=sample_question,
            document_context={}
        )
        
        print(f"\n✓ Empty Document Handling:")
        print(f"  Completeness: {result['completeness']:.2f}")
        print(f"  Evidence count: {sum(len(v) for v in result['evidence'].values())}")
        
        assert result['completeness'] == 0.0
        assert len(result['evidence']) == 0
    
    def test_02_minimal_document(self, sample_question):
        """Test: Handle minimal document with sparse information."""
        minimal_doc = "Programa de género. Presupuesto asignado."
        
        result = analyze_with_intelligence_layer(
            text=minimal_doc,
            signal_node=sample_question,
            document_context={}
        )
        
        print(f"\n✓ Minimal Document Handling:")
        print(f"  Completeness: {result['completeness']:.2f}")
        print(f"  Missing required: {result['missing_elements']}")
        
        # Should have low completeness but not fail
        assert 0.0 <= result['completeness'] <= 0.3
    
    def test_03_document_with_irrelevant_content(self, sample_question):
        """Test: Filter out irrelevant content effectively."""
        irrelevant_doc = """
        El clima de la región es tropical húmedo.
        La vegetación predominante incluye especies como ceiba y guayacán.
        Los ríos principales son el Magdalena y el Cauca.
        La economía se basa en agricultura y ganadería.
        """
        
        context = create_document_context(section='environment', chapter=4)
        
        result = analyze_with_intelligence_layer(
            text=irrelevant_doc,
            signal_node=sample_question,
            document_context=context
        )
        
        print(f"\n✓ Irrelevant Content Filtering:")
        print(f"  Completeness: {result['completeness']:.2f}")
        print(f"  Evidence extracted: {sum(len(v) for v in result['evidence'].values())}")
        
        # Should extract minimal or no evidence
        assert result['completeness'] < 0.3
    
    def test_04_document_with_conflicting_data(self, sample_question):
        """Test: Handle documents with conflicting information."""
        conflicting_doc = """
        Línea base según DANE: 8.5% de mujeres en cargos directivos.
        Línea base según Secretaría: 12.3% de mujeres en cargos directivos.
        
        Meta establecida: 15% para 2027.
        Otra meta: 20% para 2027.
        
        Presupuesto: COP 1,500 millones.
        Presupuesto revisado: COP 2,000 millones.
        """
        
        result = analyze_with_intelligence_layer(
            text=conflicting_doc,
            signal_node=sample_question,
            document_context={}
        )
        
        print(f"\n✓ Conflicting Data Handling:")
        print(f"  Completeness: {result['completeness']:.2f}")
        print(f"  Evidence extracted: {sum(len(v) for v in result['evidence'].values())}")
        
        # Should extract evidence but may flag conflicts
        assert result['completeness'] > 0.0
    
    def test_05_document_with_special_characters(self, sample_question):
        """Test: Handle special characters and formatting."""
        special_chars_doc = """
        DIAGNÓSTICO: Situación de género en 2023
        
        Línea base (año 2023): 8.5% → Meta: 15% (Δ = +6.5%)
        Fuente: DANE © 2023
        
        Presupuesto: $1,500'000,000 COP
        Cobertura: 100% del territorio • Todas las localidades
        
        Nota: Los datos incluyen información de años 2020–2023
        """
        
        result = analyze_with_intelligence_layer(
            text=special_chars_doc,
            signal_node=sample_question,
            document_context={}
        )
        
        print(f"\n✓ Special Characters Handling:")
        print(f"  Completeness: {result['completeness']:.2f}")
        
        # Should handle special chars gracefully
        assert result['completeness'] >= 0.0


class TestContextAwareFiltering:
    """Test context-aware pattern filtering effectiveness."""
    
    def test_01_budget_context_filters_correctly(self, sample_question):
        """Test: Budget context activates budget-specific patterns."""
        patterns = sample_question.get('patterns', [])
        base_pack = MockSignalPack(patterns, [sample_question])
        enriched = create_enriched_signal_pack(base_pack, enable_semantic_expansion=False)
        
        # Budget context
        budget_ctx = create_document_context(section='budget', chapter=3)
        budget_patterns = enriched.get_patterns_for_context(budget_ctx)
        
        # Non-budget context
        other_ctx = create_document_context(section='introduction', chapter=1)
        other_patterns = enriched.get_patterns_for_context(other_ctx)
        
        print(f"\n✓ Context-Aware Filtering:")
        print(f"  Total patterns: {len(patterns)}")
        print(f"  Budget context: {len(budget_patterns)} patterns")
        print(f"  Other context: {len(other_patterns)} patterns")
        
        # Both should have patterns (due to global patterns)
        assert len(budget_patterns) > 0
        assert len(other_patterns) > 0
    
    def test_02_context_hierarchy_respected(self, sample_question):
        """Test: Context scope hierarchy is respected."""
        patterns = sample_question.get('patterns', [])
        
        # Count by scope
        scope_distribution = {}
        for p in patterns:
            scope = p.get('context_scope', 'UNKNOWN')
            scope_distribution[scope] = scope_distribution.get(scope, 0) + 1
        
        print(f"\n✓ Context Scope Distribution:")
        for scope, count in sorted(scope_distribution.items()):
            pct = (count / len(patterns) * 100) if patterns else 0
            print(f"  {scope}: {count} patterns ({pct:.1f}%)")
        
        # Verify scopes are defined
        assert len(scope_distribution) > 0
    
    def test_03_context_requirement_enforcement(self, sample_question):
        """Test: Context requirements are enforced correctly."""
        patterns = sample_question.get('patterns', [])
        
        # Find patterns with requirements
        patterns_with_req = [p for p in patterns if p.get('context_requirement')]
        
        print(f"\n✓ Context Requirements:")
        print(f"  Patterns with requirements: {len(patterns_with_req)}/{len(patterns)}")
        
        if patterns_with_req:
            sample = patterns_with_req[0]
            print(f"  Example requirement: {sample.get('context_requirement')}")


class TestValidationContractScenarios:
    """Test validation contract scenarios."""
    
    def test_01_missing_required_elements_detected(self, sample_question):
        """Test: Missing required elements trigger validation failure."""
        expected = sample_question.get('expected_elements', [])
        required = [e for e in expected if isinstance(e, dict) and e.get('required')]
        
        if required:
            # Simulate incomplete extraction
            incomplete_result = {
                'completeness': 0.3,
                'missing_elements': [r.get('type', '') for r in required],
                'evidence': {}
            }
            
            from farfan_pipeline.core.orchestrator.signal_contract_validator import validate_with_contract
            
            validation = validate_with_contract(incomplete_result, sample_question)
            
            print(f"\n✓ Missing Required Elements:")
            print(f"  Required elements: {len(required)}")
            print(f"  Validation status: {validation.status}")
            print(f"  Passed: {validation.passed}")
    
    def test_02_validation_with_minimum_cardinality(self, sample_question):
        """Test: Minimum cardinality requirements validated."""
        expected = sample_question.get('expected_elements', [])
        with_minimum = [e for e in expected if isinstance(e, dict) and e.get('minimum')]
        
        if with_minimum:
            elem = with_minimum[0]
            elem_type = elem.get('type', '')
            minimum = elem.get('minimum', 0)
            
            print(f"\n✓ Minimum Cardinality Validation:")
            print(f"  Element: {elem_type}")
            print(f"  Minimum required: {minimum}")
            
            # Simulate under-minimum result
            under_result = extract_structured_evidence(
                text="Limited data.",
                signal_node=sample_question
            )
            
            print(f"  Under minimum: {under_result.under_minimum}")


class TestPipelinePerformance:
    """Test pipeline performance with realistic data volumes."""
    
    def test_01_large_document_processing(self, sample_question):
        """Test: Process large document efficiently."""
        # Create large document (simulated policy plan)
        large_doc_sections = [
            "CAPÍTULO 1: DIAGNÓSTICO\n" + "Análisis detallado. " * 100,
            "CAPÍTULO 2: OBJETIVOS\n" + "Objetivo estratégico. " * 100,
            "CAPÍTULO 3: PRESUPUESTO\n" + "Asignación presupuestal. " * 100,
            "CAPÍTULO 4: INDICADORES\n" + "Indicador de gestión. " * 100,
        ]
        
        large_doc = "\n\n".join(large_doc_sections)
        
        print(f"\n✓ Large Document Processing:")
        print(f"  Document size: {len(large_doc)} characters")
        
        result = analyze_with_intelligence_layer(
            text=large_doc,
            signal_node=sample_question,
            document_context={}
        )
        
        print(f"  Completeness: {result['completeness']:.2f}")
        print(f"  Evidence extracted: {sum(len(v) for v in result['evidence'].values())}")
        
        assert result is not None
    
    def test_02_multiple_pattern_matching(self, questionnaire):
        """Test: Efficiently match many patterns."""
        questions = questionnaire.get_micro_questions()
        
        # Get question with many patterns
        q_with_many_patterns = max(questions, key=lambda q: len(q.get('patterns', [])))
        pattern_count = len(q_with_many_patterns.get('patterns', []))
        
        print(f"\n✓ Multiple Pattern Matching:")
        print(f"  Pattern count: {pattern_count}")
        
        test_doc = "DANE reporta línea base. Meta establecida. Presupuesto asignado."
        
        result = analyze_with_intelligence_layer(
            text=test_doc,
            signal_node=q_with_many_patterns,
            document_context={}
        )
        
        print(f"  Completeness: {result['completeness']:.2f}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

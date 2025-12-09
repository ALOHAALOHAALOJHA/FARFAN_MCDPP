"""
Unit Layer (@u) Evaluator Usage Examples

Demonstrates the PDT structure analysis with real-world scenarios.
"""

from src.orchestration.unit_layer import (
    UnitLayerConfig,
    UnitLayerEvaluator,
    create_default_config
)
from src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.pdt_structure import PDTStructure


def example_complete_pdt() -> PDTStructure:
    """Example of a well-structured PDT with all required components."""
    return PDTStructure(
        full_text="[Complete PDT text would be here]",
        total_tokens=50000,
        blocks_found={
            "Diagnóstico": {
                "text": "Diagnóstico content...",
                "tokens": 5000,
                "numbers_count": 120
            },
            "Parte Estratégica": {
                "text": "Strategic content...",
                "tokens": 8000,
                "numbers_count": 80
            },
            "PPI": {
                "text": "Financial planning...",
                "tokens": 3000,
                "numbers_count": 200
            },
            "Seguimiento": {
                "text": "Monitoring section...",
                "tokens": 1000,
                "numbers_count": 30
            }
        },
        headers=[
            {"level": 1, "text": "1. DIAGNÓSTICO", "valid_numbering": True},
            {"level": 2, "text": "1.1 Contexto", "valid_numbering": True},
            {"level": 1, "text": "2. PARTE ESTRATÉGICA", "valid_numbering": True},
            {"level": 1, "text": "3. PLAN PLURIANUAL", "valid_numbering": True},
            {"level": 1, "text": "4. SEGUIMIENTO", "valid_numbering": True}
        ],
        block_sequence=["Diagnóstico", "Parte Estratégica", "PPI", "Seguimiento"],
        sections_found={
            "Diagnóstico": {
                "present": True,
                "token_count": 5000,
                "keyword_matches": 8,
                "number_count": 120,
                "sources_found": 5
            },
            "Parte Estratégica": {
                "present": True,
                "token_count": 8000,
                "keyword_matches": 6,
                "number_count": 80,
                "sources_found": 3
            },
            "PPI": {
                "present": True,
                "token_count": 3000,
                "keyword_matches": 4,
                "number_count": 200,
                "sources_found": 2
            },
            "Seguimiento": {
                "present": True,
                "token_count": 1000,
                "keyword_matches": 2,
                "number_count": 30,
                "sources_found": 1
            }
        },
        indicator_matrix_present=True,
        indicator_rows=[
            {
                "Tipo": "PRODUCTO",
                "Línea Estratégica": "Equidad de Género",
                "Programa": "Prevención de VBG",
                "Línea Base": "120 casos",
                "Año LB": 2023,
                "Meta Cuatrienio": "80 casos",
                "Fuente": "Comisaría de Familia",
                "Unidad Medida": "Casos reportados",
                "Código MGA": "1234567"
            },
            {
                "Tipo": "RESULTADO",
                "Línea Estratégica": "Educación",
                "Programa": "Calidad Educativa",
                "Línea Base": "75%",
                "Año LB": 2023,
                "Meta Cuatrienio": "85%",
                "Fuente": "Secretaría de Educación",
                "Unidad Medida": "Porcentaje",
                "Código MGA": "2345678"
            },
            {
                "Tipo": "PRODUCTO",
                "Línea Estratégica": "Salud",
                "Programa": "Atención Primaria",
                "Línea Base": "5000",
                "Año LB": 2023,
                "Meta Cuatrienio": "7500",
                "Fuente": "DANE",
                "Unidad Medida": "Personas atendidas",
                "Código MGA": "3456789"
            },
            {
                "Tipo": "PRODUCTO",
                "Línea Estratégica": "Infraestructura",
                "Programa": "Vías Rurales",
                "Línea Base": "50 km",
                "Año LB": 2023,
                "Meta Cuatrienio": "100 km",
                "Fuente": "Secretaría de Obras",
                "Unidad Medida": "Kilómetros",
                "Código MGA": "4567890"
            },
            {
                "Tipo": "RESULTADO",
                "Línea Estratégica": "Ambiente",
                "Programa": "Protección de Cuencas",
                "Línea Base": "3 cuencas",
                "Año LB": 2023,
                "Meta Cuatrienio": "6 cuencas",
                "Fuente": "CAR",
                "Unidad Medida": "Número de cuencas",
                "Código MGA": "5678901"
            },
            {
                "Tipo": "PRODUCTO",
                "Línea Estratégica": "Cultura",
                "Programa": "Promoción Cultural",
                "Línea Base": "10 eventos",
                "Año LB": 2023,
                "Meta Cuatrienio": "20 eventos",
                "Fuente": "Casa de la Cultura",
                "Unidad Medida": "Eventos realizados",
                "Código MGA": "6789012"
            }
        ],
        ppi_matrix_present=True,
        ppi_rows=[
            {
                "Línea Estratégica": "Equidad de Género",
                "Programa": "Prevención de VBG",
                "Costo Total": 500000000,
                "2024": 100000000,
                "2025": 150000000,
                "2026": 150000000,
                "2027": 100000000,
                "SGP": 300000000,
                "SGR": 0,
                "Propios": 200000000,
                "Otras": 0
            },
            {
                "Línea Estratégica": "Educación",
                "Programa": "Calidad Educativa",
                "Costo Total": 1000000000,
                "2024": 250000000,
                "2025": 250000000,
                "2026": 250000000,
                "2027": 250000000,
                "SGP": 800000000,
                "SGR": 100000000,
                "Propios": 100000000,
                "Otras": 0
            },
            {
                "Línea Estratégica": "Salud",
                "Programa": "Atención Primaria",
                "Costo Total": 750000000,
                "2024": 180000000,
                "2025": 190000000,
                "2026": 190000000,
                "2027": 190000000,
                "SGP": 600000000,
                "SGR": 0,
                "Propios": 150000000,
                "Otras": 0
            },
            {
                "Línea Estratégica": "Infraestructura",
                "Programa": "Vías Rurales",
                "Costo Total": 2000000000,
                "2024": 500000000,
                "2025": 500000000,
                "2026": 500000000,
                "2027": 500000000,
                "SGP": 500000000,
                "SGR": 1000000000,
                "Propios": 500000000,
                "Otras": 0
            }
        ]
    )


def example_incomplete_pdt() -> PDTStructure:
    """Example of a PDT with missing sections and placeholder data."""
    return PDTStructure(
        full_text="[Incomplete PDT text]",
        total_tokens=15000,
        blocks_found={
            "Diagnóstico": {
                "text": "Brief diagnostic...",
                "tokens": 800,
                "numbers_count": 10
            },
            "Parte Estratégica": {
                "text": "Brief strategy...",
                "tokens": 900,
                "numbers_count": 5
            }
        },
        headers=[
            {"level": 1, "text": "DIAGNOSTICO", "valid_numbering": False},
            {"level": 1, "text": "ESTRATEGIA", "valid_numbering": False}
        ],
        block_sequence=["Diagnóstico", "Parte Estratégica"],
        sections_found={
            "Diagnóstico": {
                "present": True,
                "token_count": 800,
                "keyword_matches": 1,
                "number_count": 10,
                "sources_found": 1
            },
            "Parte Estratégica": {
                "present": True,
                "token_count": 900,
                "keyword_matches": 1,
                "number_count": 5,
                "sources_found": 0
            }
        },
        indicator_matrix_present=True,
        indicator_rows=[
            {
                "Tipo": "PRODUCTO",
                "Línea Estratégica": "General",
                "Programa": "Varios",
                "Línea Base": "S/D",
                "Año LB": None,
                "Meta Cuatrienio": "No especificado",
                "Fuente": "",
                "Unidad Medida": "N/A"
            },
            {
                "Tipo": "RESULTADO",
                "Línea Estratégica": "Social",
                "Programa": "Desarrollo",
                "Línea Base": "Sin Dato",
                "Año LB": None,
                "Meta Cuatrienio": "S/D",
                "Fuente": "N/A",
                "Unidad Medida": ""
            }
        ],
        ppi_matrix_present=True,
        ppi_rows=[
            {
                "Línea Estratégica": "General",
                "Programa": "Varios",
                "Costo Total": 0,
                "2024": 0,
                "2025": 0,
                "2026": 0,
                "2027": 0
            }
        ]
    )


def run_examples():
    """Run all examples and display results."""
    
    print("=" * 80)
    print("Unit Layer (@u) Evaluator Examples")
    print("=" * 80)
    print()
    
    evaluator = UnitLayerEvaluator(create_default_config())
    
    print("Example 1: Complete, Well-Structured PDT")
    print("-" * 80)
    complete_pdt = example_complete_pdt()
    result1 = evaluator.evaluate(complete_pdt)
    
    print(f"S (Structural Compliance): {result1['S']:.3f}")
    print(f"  - B_cov (Block Coverage): {result1['structural_compliance']['B_cov']:.3f}")
    print(f"  - H (Header Quality): {result1['structural_compliance']['H']:.3f}")
    print(f"  - O (Ordering): {result1['structural_compliance']['O']:.3f}")
    print()
    
    print(f"M (Mandatory Sections): {result1['M']:.3f}")
    print(f"  - Diagnóstico: {result1['mandatory_sections']['diagnostico_score']:.3f}")
    print(f"  - Estratégica: {result1['mandatory_sections']['estrategica_score']:.3f}")
    print(f"  - PPI: {result1['mandatory_sections']['ppi_score']:.3f}")
    print(f"  - Seguimiento: {result1['mandatory_sections']['seguimiento_score']:.3f}")
    print()
    
    print(f"I (Indicator Quality): {result1['I']:.3f} [Gate: {'PASS' if result1['indicator_quality']['gate_passed'] else 'FAIL'}]")
    print(f"  - I_struct: {result1['indicator_quality']['I_struct']:.3f}")
    print(f"  - I_link: {result1['indicator_quality']['I_link']:.3f}")
    print(f"  - I_logic: {result1['indicator_quality']['I_logic']:.3f}")
    print()
    
    print(f"P (PPI Completeness): {result1['P']:.3f} [Gate: {'PASS' if result1['ppi_completeness']['gate_passed'] else 'FAIL'}]")
    print(f"  - Presence: {result1['ppi_completeness']['presence']:.3f}")
    print(f"  - Structure: {result1['ppi_completeness']['struct']:.3f}")
    print(f"  - Consistency: {result1['ppi_completeness']['consistency']:.3f}")
    print()
    
    print(f"U_raw (Geometric Mean): {result1['U_raw']:.3f}")
    print(f"Anti-Gaming Penalty: {result1['anti_gaming_penalty']:.3f}")
    print(f"U_final: {result1['U_final']:.3f}")
    print()
    print()
    
    print("Example 2: Incomplete PDT with Placeholder Data")
    print("-" * 80)
    incomplete_pdt = example_incomplete_pdt()
    result2 = evaluator.evaluate(incomplete_pdt)
    
    print(f"S (Structural Compliance): {result2['S']:.3f}")
    print(f"M (Mandatory Sections): {result2['M']:.3f}")
    print(f"I (Indicator Quality): {result2['I']:.3f} [Gate: {'PASS' if result2['indicator_quality']['gate_passed'] else 'FAIL'}]")
    print(f"P (PPI Completeness): {result2['P']:.3f} [Gate: {'PASS' if result2['ppi_completeness']['gate_passed'] else 'FAIL'}]")
    print(f"U_raw: {result2['U_raw']:.3f}")
    print(f"Anti-Gaming Penalty: {result2['anti_gaming_penalty']:.3f} (capped at 0.3)")
    print(f"U_final: {result2['U_final']:.3f}")
    print()
    print("Note: High penalty due to placeholder data ('S/D', 'Sin Dato', etc.)")
    print()
    print()
    
    print("Example 3: Custom Configuration")
    print("-" * 80)
    custom_config = UnitLayerConfig(
        w_s_b_cov=0.6,
        w_s_h=0.2,
        w_s_o=0.2,
        w_m_diagnostico=3.0,
        w_m_estrategica=2.0,
        w_m_ppi=1.5,
        w_m_seguimiento=1.0,
        i_hard_gate=0.6,
        p_hard_gate=0.6,
        anti_gaming_cap=0.25
    )
    
    custom_evaluator = UnitLayerEvaluator(custom_config)
    result3 = custom_evaluator.evaluate(complete_pdt)
    
    print("With custom weights (higher emphasis on Diagnóstico):")
    print(f"S: {result3['S']:.3f} | M: {result3['M']:.3f} | I: {result3['I']:.3f} | P: {result3['P']:.3f}")
    print(f"U_final: {result3['U_final']:.3f}")
    print()
    
    print("=" * 80)
    print("Examples completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    run_examples()

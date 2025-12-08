"""
Unit Layer (@u) Evaluator Tests.

Tests the full S/M/I/P component implementation with hard gates and anti-gaming measures.
"""
import pytest
from src.farfan_pipeline.core.calibration.unit_layer import (
    UnitLayerConfig,
    UnitLayerEvaluator,
    LayerScore
)
from src.farfan_pipeline.core.calibration.pdt_structure import PDTStructure


class TestUnitLayerConfig:
    """Test configuration validation."""
    
    def test_default_config_valid(self):
        config = UnitLayerConfig()
        assert config.w_S == 0.25
        assert config.w_M == 0.25
        assert config.w_I == 0.25
        assert config.w_P == 0.25
        assert config.aggregation_type == "geometric_mean"
    
    def test_weights_must_sum_to_one(self):
        with pytest.raises(ValueError, match="must sum to 1.0"):
            UnitLayerConfig(w_S=0.3, w_M=0.3, w_I=0.3, w_P=0.3)
    
    def test_invalid_aggregation_type(self):
        with pytest.raises(ValueError, match="Invalid aggregation_type"):
            UnitLayerConfig(aggregation_type="invalid")
    
    def test_hard_gate_bounds(self):
        with pytest.raises(ValueError):
            UnitLayerConfig(min_structural_compliance=1.5)
        
        with pytest.raises(ValueError):
            UnitLayerConfig(i_struct_hard_gate=-0.1)


class TestStructuralCompliance:
    """Test S (Structural Compliance) component."""
    
    def test_perfect_structure(self):
        config = UnitLayerConfig()
        evaluator = UnitLayerEvaluator(config)
        
        pdt = PDTStructure(
            full_text="test",
            total_tokens=5000,
            blocks_found={
                "Diagnóstico": {"tokens": 1500, "numbers_count": 25},
                "Parte Estratégica": {"tokens": 1200, "numbers_count": 15},
                "PPI": {"tokens": 800, "numbers_count": 30},
                "Seguimiento": {"tokens": 500, "numbers_count": 10}
            },
            headers=[
                {"level": 1, "text": "1. DIAGNÓSTICO", "valid_numbering": True},
                {"level": 2, "text": "1.1 Contexto", "valid_numbering": True},
                {"level": 1, "text": "2. PARTE ESTRATÉGICA", "valid_numbering": True}
            ],
            block_sequence=["Diagnóstico", "Parte Estratégica", "PPI", "Seguimiento"]
        )
        
        S = evaluator._compute_structural_compliance(pdt)
        assert S == 1.0
    
    def test_missing_blocks(self):
        config = UnitLayerConfig()
        evaluator = UnitLayerEvaluator(config)
        
        pdt = PDTStructure(
            full_text="test",
            total_tokens=2000,
            blocks_found={
                "Diagnóstico": {"tokens": 1500, "numbers_count": 25},
                "Parte Estratégica": {"tokens": 500, "numbers_count": 3}
            },
            headers=[],
            block_sequence=["Diagnóstico", "Parte Estratégica"]
        )
        
        S = evaluator._compute_structural_compliance(pdt)
        assert S < 0.5
    
    def test_poor_hierarchy(self):
        config = UnitLayerConfig()
        evaluator = UnitLayerEvaluator(config)
        
        pdt = PDTStructure(
            full_text="test",
            total_tokens=5000,
            blocks_found={
                "Diagnóstico": {"tokens": 1500, "numbers_count": 25},
                "Parte Estratégica": {"tokens": 1200, "numbers_count": 15},
                "PPI": {"tokens": 800, "numbers_count": 30},
                "Seguimiento": {"tokens": 500, "numbers_count": 10}
            },
            headers=[
                {"level": 1, "text": "Diagnóstico", "valid_numbering": False},
                {"level": 2, "text": "Contexto", "valid_numbering": False}
            ],
            block_sequence=["Diagnóstico", "Parte Estratégica", "PPI", "Seguimiento"]
        )
        
        S = evaluator._compute_structural_compliance(pdt)
        assert S < 1.0
    
    def test_inverted_order(self):
        config = UnitLayerConfig()
        evaluator = UnitLayerEvaluator(config)
        
        pdt = PDTStructure(
            full_text="test",
            total_tokens=5000,
            blocks_found={
                "Diagnóstico": {"tokens": 1500, "numbers_count": 25},
                "Parte Estratégica": {"tokens": 1200, "numbers_count": 15},
                "PPI": {"tokens": 800, "numbers_count": 30},
                "Seguimiento": {"tokens": 500, "numbers_count": 10}
            },
            headers=[],
            block_sequence=["PPI", "Diagnóstico", "Parte Estratégica", "Seguimiento"]
        )
        
        S = evaluator._compute_structural_compliance(pdt)
        assert S < 1.0


class TestMandatorySections:
    """Test M (Mandatory Sections) component."""
    
    def test_all_sections_complete(self):
        config = UnitLayerConfig()
        evaluator = UnitLayerEvaluator(config)
        
        pdt = PDTStructure(
            full_text="test",
            total_tokens=5000,
            sections_found={
                "Diagnóstico": {
                    "present": True,
                    "token_count": 1000,
                    "keyword_matches": 5,
                    "number_count": 15,
                    "sources_found": 3
                },
                "Parte Estratégica": {
                    "present": True,
                    "token_count": 800,
                    "keyword_matches": 4,
                    "number_count": 10
                },
                "PPI": {
                    "present": True,
                    "token_count": 600,
                    "keyword_matches": 3,
                    "number_count": 12
                },
                "Seguimiento": {
                    "present": True,
                    "token_count": 400,
                    "keyword_matches": 3,
                    "number_count": 5
                },
                "Marco Normativo": {
                    "present": True,
                    "token_count": 300,
                    "keyword_matches": 2
                }
            }
        )
        
        M = evaluator._compute_mandatory_sections(pdt)
        assert M == 1.0
    
    def test_missing_critical_section(self):
        config = UnitLayerConfig()
        evaluator = UnitLayerEvaluator(config)
        
        pdt = PDTStructure(
            full_text="test",
            total_tokens=3000,
            sections_found={
                "Diagnóstico": {
                    "present": True,
                    "token_count": 1000,
                    "keyword_matches": 5,
                    "number_count": 15,
                    "sources_found": 3
                },
                "Parte Estratégica": {
                    "present": False
                }
            }
        )
        
        M = evaluator._compute_mandatory_sections(pdt)
        assert M < 0.5
    
    def test_partial_section_completion(self):
        config = UnitLayerConfig()
        evaluator = UnitLayerEvaluator(config)
        
        pdt = PDTStructure(
            full_text="test",
            total_tokens=3000,
            sections_found={
                "Diagnóstico": {
                    "present": True,
                    "token_count": 900,
                    "keyword_matches": 2,
                    "number_count": 5,
                    "sources_found": 1
                }
            }
        )
        
        M = evaluator._compute_mandatory_sections(pdt)
        assert 0.0 < M < 1.0


class TestIndicatorQuality:
    """Test I (Indicator Quality) component."""
    
    def test_perfect_indicators(self):
        config = UnitLayerConfig()
        evaluator = UnitLayerEvaluator(config)
        
        pdt = PDTStructure(
            full_text="test",
            total_tokens=5000,
            indicator_matrix_present=True,
            indicator_rows=[
                {
                    "Tipo": "PRODUCTO",
                    "Línea Estratégica": "Equidad de Género",
                    "Programa": "Prevención de VBG",
                    "Línea Base": "120 casos",
                    "Año LB": 2023,
                    "Meta Cuatrienio": "80 casos",
                    "Fuente": "Comisaría",
                    "Unidad Medida": "Casos",
                    "Código MGA": "1234567"
                },
                {
                    "Tipo": "RESULTADO",
                    "Línea Estratégica": "Educación de Género",
                    "Programa": "Educación VBG",
                    "Línea Base": "50%",
                    "Año LB": 2022,
                    "Meta Cuatrienio": "80%",
                    "Fuente": "DANE",
                    "Unidad Medida": "Porcentaje",
                    "Código MGA": "7654321"
                }
            ]
        )
        
        I_components = evaluator._compute_indicator_quality(pdt)
        assert I_components["I_struct"] > 0.8
        assert I_components["I_link"] > 0.5
        assert I_components["I_logic"] > 0.9
    
    def test_missing_indicator_matrix(self):
        config = UnitLayerConfig()
        evaluator = UnitLayerEvaluator(config)
        
        pdt = PDTStructure(
            full_text="test",
            total_tokens=5000,
            indicator_matrix_present=False
        )
        
        I_components = evaluator._compute_indicator_quality(pdt)
        assert I_components["I_total"] == 0.0
    
    def test_placeholder_penalties(self):
        config = UnitLayerConfig()
        evaluator = UnitLayerEvaluator(config)
        
        pdt = PDTStructure(
            full_text="test",
            total_tokens=5000,
            indicator_matrix_present=True,
            indicator_rows=[
                {
                    "Tipo": "PRODUCTO",
                    "Línea Estratégica": "N/A",
                    "Programa": "TBD",
                    "Línea Base": "S/D",
                    "Meta Cuatrienio": "",
                    "Fuente": "Comisaría",
                    "Unidad Medida": "Casos"
                }
            ]
        )
        
        I_components = evaluator._compute_indicator_quality(pdt)
        assert I_components["I_struct"] < 0.5
    
    def test_invalid_year(self):
        config = UnitLayerConfig()
        evaluator = UnitLayerEvaluator(config)
        
        pdt = PDTStructure(
            full_text="test",
            total_tokens=5000,
            indicator_matrix_present=True,
            indicator_rows=[
                {
                    "Tipo": "PRODUCTO",
                    "Línea Estratégica": "Equidad",
                    "Programa": "Prevención",
                    "Línea Base": "100",
                    "Año LB": 2050,
                    "Meta Cuatrienio": "50",
                    "Fuente": "DANE",
                    "Unidad Medida": "Casos"
                }
            ]
        )
        
        I_components = evaluator._compute_indicator_quality(pdt)
        assert I_components["I_logic"] == 0.0


class TestPPICompleteness:
    """Test P (PPI Completeness) component."""
    
    def test_perfect_ppi(self):
        config = UnitLayerConfig()
        evaluator = UnitLayerEvaluator(config)
        
        pdt = PDTStructure(
            full_text="test",
            total_tokens=5000,
            ppi_matrix_present=True,
            ppi_rows=[
                {
                    "Línea Estratégica": "Equidad",
                    "Programa": "VBG",
                    "Costo Total": 400000000,
                    "2024": 100000000,
                    "2025": 100000000,
                    "2026": 100000000,
                    "2027": 100000000,
                    "SGP": 200000000,
                    "SGR": 100000000,
                    "Propios": 100000000,
                    "Otras": 0
                }
            ]
        )
        
        P_components = evaluator._compute_ppi_completeness(pdt)
        assert P_components["P_presence"] == 1.0
        assert P_components["P_struct"] == 1.0
        assert P_components["P_consistency"] > 0.95
    
    def test_missing_ppi(self):
        config = UnitLayerConfig()
        evaluator = UnitLayerEvaluator(config)
        
        pdt = PDTStructure(
            full_text="test",
            total_tokens=5000,
            ppi_matrix_present=False
        )
        
        P_components = evaluator._compute_ppi_completeness(pdt)
        assert P_components["P_presence"] == 0.0
        assert P_components["P_total"] == 0.0
    
    def test_accounting_violations(self):
        config = UnitLayerConfig()
        evaluator = UnitLayerEvaluator(config)
        
        pdt = PDTStructure(
            full_text="test",
            total_tokens=5000,
            ppi_matrix_present=True,
            ppi_rows=[
                {
                    "Costo Total": 400000000,
                    "2024": 50000000,
                    "2025": 50000000,
                    "2026": 50000000,
                    "2027": 50000000,
                    "SGP": 150000000,
                    "SGR": 50000000,
                    "Propios": 50000000,
                    "Otras": 0
                }
            ]
        )
        
        P_components = evaluator._compute_ppi_completeness(pdt)
        assert P_components["P_consistency"] < 1.0


class TestAggregation:
    """Test aggregation methods."""
    
    def test_geometric_mean(self):
        config = UnitLayerConfig(aggregation_type="geometric_mean")
        evaluator = UnitLayerEvaluator(config)
        
        result = evaluator._aggregate_components(0.8, 0.8, 0.8, 0.8)
        assert abs(result - 0.8) < 0.001
        
        result = evaluator._aggregate_components(1.0, 1.0, 0.5, 1.0)
        assert abs(result - 0.841) < 0.01
    
    def test_harmonic_mean(self):
        config = UnitLayerConfig(aggregation_type="harmonic_mean")
        evaluator = UnitLayerEvaluator(config)
        
        result = evaluator._aggregate_components(0.8, 0.8, 0.8, 0.8)
        assert abs(result - 0.8) < 0.001
        
        result = evaluator._aggregate_components(1.0, 0.5, 1.0, 1.0)
        assert result < 0.8
    
    def test_weighted_average(self):
        config = UnitLayerConfig(aggregation_type="weighted_average")
        evaluator = UnitLayerEvaluator(config)
        
        result = evaluator._aggregate_components(0.8, 0.6, 1.0, 0.4)
        expected = 0.25 * 0.8 + 0.25 * 0.6 + 0.25 * 1.0 + 0.25 * 0.4
        assert abs(result - expected) < 0.001


class TestHardGates:
    """Test hard gate enforcement."""
    
    def test_structural_hard_gate(self):
        config = UnitLayerConfig(min_structural_compliance=0.5)
        evaluator = UnitLayerEvaluator(config)
        
        pdt = PDTStructure(
            full_text="test",
            total_tokens=500,
            blocks_found={
                "Diagnóstico": {"tokens": 50, "numbers_count": 1}
            },
            sections_found={},
            indicator_matrix_present=True,
            indicator_rows=[],
            ppi_matrix_present=True,
            ppi_rows=[]
        )
        
        result = evaluator.evaluate(pdt)
        assert result.score == 0.0
        assert "HARD GATE" in result.rationale
    
    def test_i_struct_hard_gate(self):
        config = UnitLayerConfig(i_struct_hard_gate=0.7)
        evaluator = UnitLayerEvaluator(config)
        
        pdt = PDTStructure(
            full_text="test",
            total_tokens=5000,
            blocks_found={
                "Diagnóstico": {"tokens": 1500, "numbers_count": 25},
                "Parte Estratégica": {"tokens": 1200, "numbers_count": 15},
                "PPI": {"tokens": 800, "numbers_count": 30},
                "Seguimiento": {"tokens": 500, "numbers_count": 10}
            },
            sections_found={
                "Diagnóstico": {"present": True, "token_count": 1000, 
                               "keyword_matches": 5, "number_count": 15, "sources_found": 3}
            },
            indicator_matrix_present=True,
            indicator_rows=[
                {"Tipo": "PRODUCTO", "Línea Estratégica": "", "Programa": ""}
            ],
            ppi_matrix_present=True,
            ppi_rows=[]
        )
        
        result = evaluator.evaluate(pdt)
        assert result.score == 0.0
    
    def test_ppi_presence_hard_gate(self):
        config = UnitLayerConfig(require_ppi_presence=True)
        evaluator = UnitLayerEvaluator(config)
        
        pdt = PDTStructure(
            full_text="test",
            total_tokens=5000,
            blocks_found={
                "Diagnóstico": {"tokens": 1500, "numbers_count": 25},
                "Parte Estratégica": {"tokens": 1200, "numbers_count": 15},
                "PPI": {"tokens": 800, "numbers_count": 30},
                "Seguimiento": {"tokens": 500, "numbers_count": 10}
            },
            sections_found={
                "Diagnóstico": {"present": True, "token_count": 1000,
                               "keyword_matches": 5, "number_count": 15, "sources_found": 3}
            },
            indicator_matrix_present=True,
            indicator_rows=[
                {
                    "Tipo": "PRODUCTO",
                    "Línea Estratégica": "Equidad",
                    "Programa": "VBG",
                    "Línea Base": "100",
                    "Meta Cuatrienio": "50",
                    "Fuente": "DANE",
                    "Unidad Medida": "Casos"
                }
            ],
            ppi_matrix_present=False
        )
        
        result = evaluator.evaluate(pdt)
        assert result.score == 0.0


class TestAntiGaming:
    """Test anti-gaming measures."""
    
    def test_placeholder_penalty(self):
        config = UnitLayerConfig()
        evaluator = UnitLayerEvaluator(config)
        
        pdt = PDTStructure(
            full_text="test",
            total_tokens=5000,
            indicator_matrix_present=True,
            indicator_rows=[
                {
                    "Tipo": "N/A",
                    "Línea Estratégica": "N/A",
                    "Programa": "N/A",
                    "Línea Base": "N/A",
                    "Meta Cuatrienio": "N/A",
                    "Fuente": "N/A",
                    "Unidad Medida": "N/A"
                }
            ] * 10
        )
        
        penalty = evaluator._compute_gaming_penalty(pdt)
        assert penalty > 0.0
    
    def test_unique_values_penalty(self):
        config = UnitLayerConfig()
        evaluator = UnitLayerEvaluator(config)
        
        pdt = PDTStructure(
            full_text="test",
            total_tokens=5000,
            ppi_matrix_present=True,
            ppi_rows=[
                {"Costo Total": 100000000}
            ] * 20
        )
        
        penalty = evaluator._compute_gaming_penalty(pdt)
        assert penalty > 0.0
    
    def test_number_density_penalty(self):
        config = UnitLayerConfig()
        evaluator = UnitLayerEvaluator(config)
        
        pdt = PDTStructure(
            full_text="test",
            total_tokens=5000,
            sections_found={
                "Diagnóstico": {
                    "present": True,
                    "token_count": 10000,
                    "number_count": 5
                }
            }
        )
        
        penalty = evaluator._compute_gaming_penalty(pdt)
        assert penalty > 0.0
    
    def test_penalty_cap(self):
        config = UnitLayerConfig(gaming_penalty_cap=0.3)
        evaluator = UnitLayerEvaluator(config)
        
        pdt = PDTStructure(
            full_text="test",
            total_tokens=5000,
            indicator_matrix_present=True,
            indicator_rows=[{"field": "N/A"} for _ in range(100)],
            ppi_matrix_present=True,
            ppi_rows=[{"Costo Total": 100} for _ in range(100)],
            sections_found={
                "Diagnóstico": {
                    "present": True,
                    "token_count": 100000,
                    "number_count": 1
                }
            }
        )
        
        penalty = evaluator._compute_gaming_penalty(pdt)
        assert penalty <= 0.3


class TestEndToEnd:
    """End-to-end evaluation tests."""
    
    def test_sobresaliente_quality(self):
        config = UnitLayerConfig()
        evaluator = UnitLayerEvaluator(config)
        
        pdt = PDTStructure(
            full_text="test",
            total_tokens=8000,
            blocks_found={
                "Diagnóstico": {"tokens": 2000, "numbers_count": 40},
                "Parte Estratégica": {"tokens": 1500, "numbers_count": 25},
                "PPI": {"tokens": 1200, "numbers_count": 50},
                "Seguimiento": {"tokens": 800, "numbers_count": 15}
            },
            headers=[
                {"level": 1, "text": "1. DIAGNÓSTICO", "valid_numbering": True},
                {"level": 1, "text": "2. ESTRATÉGICA", "valid_numbering": True}
            ],
            block_sequence=["Diagnóstico", "Parte Estratégica", "PPI", "Seguimiento"],
            sections_found={
                "Diagnóstico": {"present": True, "token_count": 1000, 
                               "keyword_matches": 5, "number_count": 20, "sources_found": 3},
                "Parte Estratégica": {"present": True, "token_count": 800,
                                     "keyword_matches": 4, "number_count": 10},
                "PPI": {"present": True, "token_count": 600,
                       "keyword_matches": 3, "number_count": 15}
            },
            indicator_matrix_present=True,
            indicator_rows=[
                {
                    "Tipo": "PRODUCTO",
                    "Línea Estratégica": "Equidad de Género",
                    "Programa": "Equidad de Género",
                    "Línea Base": "100",
                    "Año LB": 2023,
                    "Meta Cuatrienio": "50",
                    "Fuente": "DANE",
                    "Unidad Medida": "Casos",
                    "Código MGA": "1234567"
                }
            ],
            ppi_matrix_present=True,
            ppi_rows=[
                {
                    "Costo Total": 400000000,
                    "2024": 100000000,
                    "2025": 100000000,
                    "2026": 100000000,
                    "2027": 100000000,
                    "SGP": 200000000,
                    "SGR": 100000000,
                    "Propios": 100000000,
                    "Otras": 0
                }
            ]
        )
        
        result = evaluator.evaluate(pdt)
        assert result.score >= 0.85
        assert result.metadata["quality_level"] == "sobresaliente"
    
    def test_insuficiente_quality(self):
        config = UnitLayerConfig()
        evaluator = UnitLayerEvaluator(config)
        
        pdt = PDTStructure(
            full_text="minimal text",
            total_tokens=200,
            blocks_found={
                "Diagnóstico": {"tokens": 100, "numbers_count": 2}
            },
            sections_found={
                "Diagnóstico": {"present": True, "token_count": 100,
                               "keyword_matches": 0, "number_count": 1, "sources_found": 0}
            },
            indicator_matrix_present=True,
            indicator_rows=[
                {"Tipo": "N/A"}
            ],
            ppi_matrix_present=True,
            ppi_rows=[
                {"Costo Total": 0}
            ]
        )
        
        result = evaluator.evaluate(pdt)
        assert result.score < 0.5
        assert result.metadata["quality_level"] == "insuficiente"

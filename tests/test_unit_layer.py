"""
Unit tests for Unit Layer (@u) Evaluator

Tests comprehensive PDT structure analysis including:
- Structural compliance (S)
- Mandatory sections (M)
- Indicator quality (I)
- PPI completeness (P)
- Anti-gaming detection
- Hard gate enforcement
"""

import pytest
from orchestration.unit_layer import (
    UnitLayerConfig,
    UnitLayerEvaluator,
    create_default_config
)
from src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.pdt_structure import PDTStructure


class TestUnitLayerConfig:
    """Test configuration validation and defaults."""
    
    def test_default_config_valid(self):
        """Default configuration should be valid."""
        config = create_default_config()
        assert config.w_s_b_cov == 0.5
        assert config.w_s_h == 0.25
        assert config.w_s_o == 0.25
        assert config.anti_gaming_cap == 0.3
    
    def test_s_weights_sum_to_one(self):
        """S weights must sum to 1.0."""
        with pytest.raises(ValueError, match="S weights must sum to 1.0"):
            UnitLayerConfig(w_s_b_cov=0.5, w_s_h=0.3, w_s_o=0.3)
    
    def test_i_weights_sum_to_one(self):
        """I weights must sum to 1.0."""
        with pytest.raises(ValueError, match="I weights must sum to 1.0"):
            UnitLayerConfig(w_i_struct=0.5, w_i_link=0.3, w_i_logic=0.3)
    
    def test_p_weights_sum_to_one(self):
        """P weights must sum to 1.0."""
        with pytest.raises(ValueError, match="P weights must sum to 1.0"):
            UnitLayerConfig(w_p_presence=0.3, w_p_struct=0.4, w_p_consistency=0.4)
    
    def test_custom_config_valid(self):
        """Custom configuration with valid weights."""
        config = UnitLayerConfig(
            w_s_b_cov=0.6,
            w_s_h=0.2,
            w_s_o=0.2,
            w_m_diagnostico=3.0,
            i_hard_gate=0.6,
            anti_gaming_cap=0.25
        )
        assert config.w_s_b_cov == 0.6
        assert config.w_m_diagnostico == 3.0


class TestStructuralCompliance:
    """Test S (Structural Compliance) calculation."""
    
    def test_perfect_structure(self):
        """PDT with all blocks, valid headers, correct order."""
        pdt = PDTStructure(
            full_text="",
            total_tokens=10000,
            blocks_found={
                "Diagnóstico": {},
                "Parte Estratégica": {},
                "PPI": {},
                "Seguimiento": {}
            },
            headers=[
                {"valid_numbering": True},
                {"valid_numbering": True},
                {"valid_numbering": True}
            ],
            block_sequence=["Diagnóstico", "Parte Estratégica", "PPI", "Seguimiento"]
        )
        
        evaluator = UnitLayerEvaluator()
        result = evaluator.evaluate(pdt)
        
        assert result["structural_compliance"]["B_cov"] == 1.0
        assert result["structural_compliance"]["H"] == 1.0
        assert result["structural_compliance"]["O"] == 1.0
        assert result["S"] == 1.0
    
    def test_missing_blocks(self):
        """PDT missing required blocks."""
        pdt = PDTStructure(
            full_text="",
            total_tokens=5000,
            blocks_found={"Diagnóstico": {}, "Parte Estratégica": {}},
            headers=[],
            block_sequence=["Diagnóstico", "Parte Estratégica"]
        )
        
        evaluator = UnitLayerEvaluator()
        result = evaluator.evaluate(pdt)
        
        assert result["structural_compliance"]["B_cov"] == 0.5
        assert result["S"] < 1.0
    
    def test_invalid_headers(self):
        """PDT with invalid header numbering."""
        pdt = PDTStructure(
            full_text="",
            total_tokens=5000,
            blocks_found={"Diagnóstico": {}},
            headers=[
                {"valid_numbering": False},
                {"valid_numbering": False}
            ],
            block_sequence=[]
        )
        
        evaluator = UnitLayerEvaluator()
        result = evaluator.evaluate(pdt)
        
        assert result["structural_compliance"]["H"] == 0.0
    
    def test_wrong_order(self):
        """PDT with blocks in wrong order."""
        pdt = PDTStructure(
            full_text="",
            total_tokens=5000,
            blocks_found={},
            headers=[],
            block_sequence=["PPI", "Diagnóstico", "Seguimiento", "Parte Estratégica"]
        )
        
        evaluator = UnitLayerEvaluator()
        result = evaluator.evaluate(pdt)
        
        assert result["structural_compliance"]["O"] == 0.0


class TestMandatorySections:
    """Test M (Mandatory Sections) calculation."""
    
    def test_complete_sections(self):
        """All sections present with sufficient content."""
        pdt = PDTStructure(
            full_text="",
            total_tokens=20000,
            blocks_found={},
            headers=[],
            block_sequence=[],
            sections_found={
                "Diagnóstico": {
                    "present": True,
                    "token_count": 5000,
                    "keyword_matches": 8,
                    "number_count": 50,
                    "sources_found": 5
                },
                "Parte Estratégica": {
                    "present": True,
                    "token_count": 6000,
                    "keyword_matches": 6,
                    "number_count": 40,
                    "sources_found": 3
                },
                "PPI": {
                    "present": True,
                    "token_count": 2000,
                    "keyword_matches": 4,
                    "number_count": 100,
                    "sources_found": 2
                },
                "Seguimiento": {
                    "present": True,
                    "token_count": 1000,
                    "keyword_matches": 3,
                    "number_count": 20,
                    "sources_found": 1
                }
            }
        )
        
        evaluator = UnitLayerEvaluator()
        result = evaluator.evaluate(pdt)
        
        assert result["mandatory_sections"]["diagnostico_score"] > 0.8
        assert result["mandatory_sections"]["estrategica_score"] > 0.8
        assert result["M"] > 0.8
    
    def test_missing_sections(self):
        """Some sections missing."""
        pdt = PDTStructure(
            full_text="",
            total_tokens=5000,
            blocks_found={},
            headers=[],
            block_sequence=[],
            sections_found={
                "Diagnóstico": {"present": False}
            }
        )
        
        evaluator = UnitLayerEvaluator()
        result = evaluator.evaluate(pdt)
        
        assert result["mandatory_sections"]["diagnostico_score"] == 0.0
        assert result["M"] < 0.5
    
    def test_critical_weight_multiplier(self):
        """Critical sections have 2.0x weight."""
        pdt = PDTStructure(
            full_text="",
            total_tokens=10000,
            blocks_found={},
            headers=[],
            block_sequence=[],
            sections_found={
                "Diagnóstico": {
                    "present": True,
                    "token_count": 5000,
                    "keyword_matches": 5,
                    "number_count": 30,
                    "sources_found": 3
                },
                "Seguimiento": {
                    "present": True,
                    "token_count": 500,
                    "keyword_matches": 2,
                    "number_count": 10,
                    "sources_found": 1
                }
            }
        )
        
        evaluator = UnitLayerEvaluator()
        evaluator.evaluate(pdt)
        
        assert evaluator.config.w_m_diagnostico == 2.0
        assert evaluator.config.w_m_seguimiento == 1.0


class TestIndicatorQuality:
    """Test I (Indicator Quality) calculation and hard gate."""
    
    def test_high_quality_indicators(self):
        """Indicators with complete fields and valid logic."""
        pdt = PDTStructure(
            full_text="",
            total_tokens=10000,
            blocks_found={},
            headers=[],
            block_sequence=[],
            indicator_matrix_present=True,
            indicator_rows=[
                {
                    "Tipo": "PRODUCTO",
                    "Línea Estratégica": "Salud",
                    "Programa": "Atención Primaria",
                    "Línea Base": "1000",
                    "Año LB": 2023,
                    "Meta Cuatrienio": "1500",
                    "Fuente": "DANE"
                },
                {
                    "Tipo": "RESULTADO",
                    "Línea Estratégica": "Educación",
                    "Programa": "Calidad",
                    "Línea Base": "75%",
                    "Año LB": 2023,
                    "Meta Cuatrienio": "85%",
                    "Fuente": "Secretaría"
                },
                {
                    "Tipo": "PRODUCTO",
                    "Línea Estratégica": "Infraestructura",
                    "Programa": "Vías",
                    "Línea Base": "50 km",
                    "Año LB": 2023,
                    "Meta Cuatrienio": "100 km",
                    "Fuente": "Obras"
                },
                {
                    "Tipo": "PRODUCTO",
                    "Línea Estratégica": "Social",
                    "Programa": "Protección",
                    "Línea Base": "200",
                    "Año LB": 2023,
                    "Meta Cuatrienio": "300",
                    "Fuente": "ICBF"
                },
                {
                    "Tipo": "RESULTADO",
                    "Línea Estratégica": "Ambiente",
                    "Programa": "Conservación",
                    "Línea Base": "5",
                    "Año LB": 2023,
                    "Meta Cuatrienio": "10",
                    "Fuente": "CAR"
                },
                {
                    "Tipo": "PRODUCTO",
                    "Línea Estratégica": "Cultura",
                    "Programa": "Promoción",
                    "Línea Base": "10",
                    "Año LB": 2023,
                    "Meta Cuatrienio": "20",
                    "Fuente": "Cultura"
                }
            ]
        )
        
        evaluator = UnitLayerEvaluator()
        result = evaluator.evaluate(pdt)
        
        assert result["indicator_quality"]["I_struct"] >= 0.8
        assert result["indicator_quality"]["I_link"] >= 0.9
        assert result["indicator_quality"]["I_logic"] >= 0.9
        assert result["indicator_quality"]["gate_passed"] is True
        assert result["I"] > 0.7
    
    def test_indicator_hard_gate_fail(self):
        """Indicators below 0.7 threshold trigger hard gate."""
        pdt = PDTStructure(
            full_text="",
            total_tokens=5000,
            blocks_found={},
            headers=[],
            block_sequence=[],
            indicator_matrix_present=True,
            indicator_rows=[
                {
                    "Tipo": "PRODUCTO",
                    "Línea Base": "S/D",
                    "Meta Cuatrienio": "Sin Dato"
                }
            ]
        )
        
        evaluator = UnitLayerEvaluator()
        result = evaluator.evaluate(pdt)
        
        assert result["indicator_quality"]["gate_passed"] is False
        assert result["I"] == 0.0
        assert result["U_final"] == 0.0
    
    def test_no_indicators(self):
        """Missing indicator matrix triggers hard gate."""
        pdt = PDTStructure(
            full_text="",
            total_tokens=5000,
            blocks_found={},
            headers=[],
            block_sequence=[],
            indicator_matrix_present=False,
            indicator_rows=[]
        )
        
        evaluator = UnitLayerEvaluator()
        result = evaluator.evaluate(pdt)
        
        assert result["indicator_quality"]["gate_passed"] is False
        assert result["I"] == 0.0


class TestPPICompleteness:
    """Test P (PPI Completeness) calculation and hard gate."""
    
    def test_complete_ppi(self):
        """PPI with all fields and accounting consistency."""
        pdt = PDTStructure(
            full_text="",
            total_tokens=10000,
            blocks_found={},
            headers=[],
            block_sequence=[],
            ppi_matrix_present=True,
            ppi_rows=[
                {
                    "Línea Estratégica": "Salud",
                    "Programa": "Atención",
                    "Costo Total": 1000000000,
                    "2024": 250000000,
                    "2025": 250000000,
                    "2026": 250000000,
                    "2027": 250000000
                },
                {
                    "Línea Estratégica": "Educación",
                    "Programa": "Calidad",
                    "Costo Total": 800000000,
                    "2024": 200000000,
                    "2025": 200000000,
                    "2026": 200000000,
                    "2027": 200000000
                },
                {
                    "Línea Estratégica": "Infraestructura",
                    "Programa": "Vías",
                    "Costo Total": 2000000000,
                    "2024": 500000000,
                    "2025": 500000000,
                    "2026": 500000000,
                    "2027": 500000000
                }
            ]
        )
        
        evaluator = UnitLayerEvaluator()
        result = evaluator.evaluate(pdt)
        
        assert result["ppi_completeness"]["presence"] == 1.0
        assert result["ppi_completeness"]["struct"] == 1.0
        assert result["ppi_completeness"]["consistency"] == 1.0
        assert result["ppi_completeness"]["gate_passed"] is True
        assert result["P"] > 0.7
    
    def test_ppi_accounting_inconsistency(self):
        """PPI with budget mismatch exceeding tolerance."""
        pdt = PDTStructure(
            full_text="",
            total_tokens=5000,
            blocks_found={},
            headers=[],
            block_sequence=[],
            ppi_matrix_present=True,
            ppi_rows=[
                {
                    "Línea Estratégica": "Test",
                    "Programa": "Test",
                    "Costo Total": 1000000000,
                    "2024": 100000000,
                    "2025": 200000000,
                    "2026": 300000000,
                    "2027": 300000000
                }
            ]
        )
        
        evaluator = UnitLayerEvaluator()
        result = evaluator.evaluate(pdt)
        
        assert result["ppi_completeness"]["consistency"] < 1.0
    
    def test_ppi_hard_gate_fail(self):
        """PPI below 0.7 threshold triggers hard gate."""
        pdt = PDTStructure(
            full_text="",
            total_tokens=5000,
            blocks_found={},
            headers=[],
            block_sequence=[],
            ppi_matrix_present=True,
            ppi_rows=[
                {
                    "Costo Total": 0,
                    "2024": 0,
                    "2025": 0,
                    "2026": 0,
                    "2027": 0
                }
            ]
        )
        
        evaluator = UnitLayerEvaluator()
        result = evaluator.evaluate(pdt)
        
        assert result["ppi_completeness"]["gate_passed"] is False
        assert result["P"] == 0.0


class TestAntiGaming:
    """Test anti-gaming penalty detection and application."""
    
    def test_placeholder_detection_indicators(self):
        """Detect placeholder terms in indicators."""
        pdt = PDTStructure(
            full_text="",
            total_tokens=5000,
            blocks_found={},
            headers=[],
            block_sequence=[],
            indicator_matrix_present=True,
            indicator_rows=[
                {
                    "Línea Base": "S/D",
                    "Meta Cuatrienio": "Sin Dato",
                    "Fuente": "No especificado"
                },
                {
                    "Línea Base": "N/A",
                    "Meta Cuatrienio": "",
                    "Fuente": ""
                }
            ]
        )
        
        evaluator = UnitLayerEvaluator()
        result = evaluator.evaluate(pdt)
        
        assert result["anti_gaming_penalty"] > 0.0
    
    def test_placeholder_detection_ppi(self):
        """Detect zero/null values in PPI."""
        pdt = PDTStructure(
            full_text="",
            total_tokens=5000,
            blocks_found={},
            headers=[],
            block_sequence=[],
            ppi_matrix_present=True,
            ppi_rows=[
                {
                    "Costo Total": 0,
                    "2024": None,
                    "2025": 0,
                    "2026": None,
                    "2027": 0
                }
            ]
        )
        
        evaluator = UnitLayerEvaluator()
        result = evaluator.evaluate(pdt)
        
        assert result["anti_gaming_penalty"] > 0.0
    
    def test_penalty_cap(self):
        """Penalty is capped at configured maximum."""
        pdt = PDTStructure(
            full_text="",
            total_tokens=5000,
            blocks_found={},
            headers=[],
            block_sequence=[],
            indicator_matrix_present=True,
            indicator_rows=[
                {"Línea Base": "S/D", "Meta Cuatrienio": "S/D", "Fuente": "S/D"}
                for _ in range(50)
            ],
            ppi_matrix_present=True,
            ppi_rows=[
                {"Costo Total": 0, "2024": 0, "2025": 0, "2026": 0, "2027": 0}
                for _ in range(50)
            ]
        )
        
        evaluator = UnitLayerEvaluator()
        result = evaluator.evaluate(pdt)
        
        assert result["anti_gaming_penalty"] <= 0.3
        assert result["anti_gaming_penalty"] == evaluator.config.anti_gaming_cap


class TestGeometricMean:
    """Test geometric mean calculation and properties."""
    
    def test_geometric_mean_perfect(self):
        """Geometric mean of perfect scores."""
        pdt = PDTStructure(
            full_text="",
            total_tokens=50000,
            blocks_found={"Diagnóstico": {}, "Parte Estratégica": {}, "PPI": {}, "Seguimiento": {}},
            headers=[{"valid_numbering": True}],
            block_sequence=["Diagnóstico", "Parte Estratégica", "PPI", "Seguimiento"],
            sections_found={
                "Diagnóstico": {
                    "present": True, "token_count": 5000,
                    "keyword_matches": 10, "number_count": 100, "sources_found": 5
                },
                "Parte Estratégica": {
                    "present": True, "token_count": 5000,
                    "keyword_matches": 10, "number_count": 100, "sources_found": 5
                },
                "PPI": {
                    "present": True, "token_count": 2000,
                    "keyword_matches": 5, "number_count": 50, "sources_found": 3
                },
                "Seguimiento": {
                    "present": True, "token_count": 1000,
                    "keyword_matches": 3, "number_count": 20, "sources_found": 2
                }
            },
            indicator_matrix_present=True,
            indicator_rows=[
                {
                    "Tipo": "PRODUCTO", "Línea Estratégica": "Test", "Programa": "Test",
                    "Línea Base": "100", "Año LB": 2023, "Meta Cuatrienio": "200", "Fuente": "Test"
                }
                for _ in range(10)
            ],
            ppi_matrix_present=True,
            ppi_rows=[
                {
                    "Línea Estratégica": "Test", "Programa": "Test",
                    "Costo Total": 1000000000, "2024": 250000000,
                    "2025": 250000000, "2026": 250000000, "2027": 250000000
                }
                for _ in range(5)
            ]
        )
        
        evaluator = UnitLayerEvaluator()
        result = evaluator.evaluate(pdt)
        
        assert result["U_raw"] > 0.8
        assert result["U_final"] > 0.8
    
    def test_geometric_mean_zero_component(self):
        """Zero in any component makes U_raw = 0."""
        pdt = PDTStructure(
            full_text="",
            total_tokens=5000,
            blocks_found={},
            headers=[],
            block_sequence=[],
            indicator_matrix_present=False,
            indicator_rows=[]
        )
        
        evaluator = UnitLayerEvaluator()
        result = evaluator.evaluate(pdt)
        
        assert result["I"] == 0.0
        assert result["U_raw"] == 0.0
        assert result["U_final"] == 0.0


class TestIntegration:
    """Integration tests with realistic scenarios."""
    
    def test_complete_high_quality_pdt(self):
        """Complete PDT with high-quality content."""
        from orchestration.unit_layer_example import example_complete_pdt
        
        pdt = example_complete_pdt()
        evaluator = UnitLayerEvaluator()
        result = evaluator.evaluate(pdt)
        
        assert result["U_final"] > 0.7
        assert result["indicator_quality"]["gate_passed"] is True
        assert result["ppi_completeness"]["gate_passed"] is True
    
    def test_incomplete_gaming_pdt(self):
        """Incomplete PDT with gaming attempts."""
        from src.orchestration.unit_layer_example import example_incomplete_pdt
        
        pdt = example_incomplete_pdt()
        evaluator = UnitLayerEvaluator()
        result = evaluator.evaluate(pdt)
        
        assert result["U_final"] < 0.5
        assert result["anti_gaming_penalty"] > 0.0
    
    def test_custom_config_relaxed_gates(self):
        """Custom configuration with relaxed gate thresholds."""
        from src.orchestration.unit_layer_example import example_incomplete_pdt
        
        pdt = example_incomplete_pdt()
        config = UnitLayerConfig(i_hard_gate=0.3, p_hard_gate=0.3)
        evaluator = UnitLayerEvaluator(config)
        result = evaluator.evaluate(pdt)
        
        assert result["indicator_quality"]["gate_passed"] is True
        assert result["ppi_completeness"]["gate_passed"] is True

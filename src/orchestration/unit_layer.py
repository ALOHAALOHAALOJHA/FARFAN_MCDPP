"""
Unit Layer (@u) Evaluator Implementation

Implements PDT (Plan de Desarrollo Territorial) structure analysis with:
- S (Structural Compliance): 0.5·B_cov + 0.25·H + 0.25·O
- M (Mandatory Sections): Critical sections with 2.0x weights
- I (Indicator Quality): 0.4·I_struct + 0.3·I_link + 0.3·I_logic with 0.7 hard gate
- P (PPI Completeness): 0.2·presence + 0.4·struct + 0.4·consistency with 0.7 hard gate
- U_final: Geometric mean with anti-gaming penalty capped at 0.3
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict
import math

from ..cross_cutting_infrastrucuture.capaz_calibration_parmetrization.pdt_structure import PDTStructure


class StructuralCompliance(TypedDict):
    B_cov: float
    H: float  # noqa: E741
    O: float  # noqa: E741
    S: float


class MandatorySections(TypedDict):
    diagnostico_score: float
    estrategica_score: float
    ppi_score: float
    seguimiento_score: float
    M: float


class IndicatorQuality(TypedDict):
    I_struct: float
    I_link: float
    I_logic: float
    I: float  # noqa: E741
    gate_passed: bool


class PPICompleteness(TypedDict):
    presence: float
    struct: float
    consistency: float
    P: float
    gate_passed: bool


class UnitLayerResult(TypedDict):
    S: float
    M: float
    I: float  # noqa: E741
    P: float
    U_raw: float
    anti_gaming_penalty: float
    U_final: float
    structural_compliance: StructuralCompliance
    mandatory_sections: MandatorySections
    indicator_quality: IndicatorQuality
    ppi_completeness: PPICompleteness


@dataclass(frozen=True)
class UnitLayerConfig:
    w_s_b_cov: float = 0.5
    w_s_h: float = 0.25
    w_s_o: float = 0.25
    
    w_m_diagnostico: float = 2.0
    w_m_estrategica: float = 2.0
    w_m_ppi: float = 2.0
    w_m_seguimiento: float = 1.0
    
    w_i_struct: float = 0.4
    w_i_link: float = 0.3
    w_i_logic: float = 0.3
    i_hard_gate: float = 0.7
    
    w_p_presence: float = 0.2
    w_p_struct: float = 0.4
    w_p_consistency: float = 0.4
    p_hard_gate: float = 0.7
    
    anti_gaming_cap: float = 0.3
    
    min_tokens_diagnostico: int = 1000
    min_tokens_estrategica: int = 1000
    min_tokens_ppi: int = 500
    min_tokens_seguimiento: int = 300
    
    min_indicators: int = 5
    min_ppi_rows: int = 3
    
    accounting_tolerance: float = 0.01

    def __post_init__(self) -> None:
        if abs(self.w_s_b_cov + self.w_s_h + self.w_s_o - 1.0) > 1e-6:
            raise ValueError("S weights must sum to 1.0")
        if abs(self.w_i_struct + self.w_i_link + self.w_i_logic - 1.0) > 1e-6:
            raise ValueError("I weights must sum to 1.0")
        if abs(self.w_p_presence + self.w_p_struct + self.w_p_consistency - 1.0) > 1e-6:
            raise ValueError("P weights must sum to 1.0")


class UnitLayerEvaluator:
    def __init__(self, config: UnitLayerConfig | None = None):
        self.config = config or UnitLayerConfig()
    
    def evaluate(self, pdt: PDTStructure) -> UnitLayerResult:
        S_result = self._evaluate_structural_compliance(pdt)
        M_result = self._evaluate_mandatory_sections(pdt)
        I_result = self._evaluate_indicator_quality(pdt)
        P_result = self._evaluate_ppi_completeness(pdt)
        
        S = S_result["S"]
        M = M_result["M"]
        I = I_result["I"] if I_result["gate_passed"] else 0.0  # noqa: E741
        P = P_result["P"] if P_result["gate_passed"] else 0.0
        
        U_raw = self._geometric_mean([S, M, I, P])
        
        anti_gaming_penalty = self._compute_anti_gaming_penalty(pdt)
        capped_penalty = min(anti_gaming_penalty, self.config.anti_gaming_cap)
        
        U_final = max(0.0, U_raw - capped_penalty)
        
        return {
            "S": S,
            "M": M,
            "I": I,
            "P": P,
            "U_raw": U_raw,
            "anti_gaming_penalty": capped_penalty,
            "U_final": U_final,
            "structural_compliance": S_result,
            "mandatory_sections": M_result,
            "indicator_quality": I_result,
            "ppi_completeness": P_result
        }
    
    def _evaluate_structural_compliance(self, pdt: PDTStructure) -> StructuralCompliance:
        B_cov = self._compute_block_coverage(pdt)
        H = self._compute_header_quality(pdt)  # noqa: E741
        O = self._compute_ordering_quality(pdt)  # noqa: E741
        
        S = (
            self.config.w_s_b_cov * B_cov +
            self.config.w_s_h * H +
            self.config.w_s_o * O
        )
        
        return {
            "B_cov": B_cov,
            "H": H,
            "O": O,
            "S": S
        }
    
    def _evaluate_mandatory_sections(self, pdt: PDTStructure) -> MandatorySections:
        diagnostico = self._score_section(
            pdt, "Diagnóstico", self.config.min_tokens_diagnostico
        )
        estrategica = self._score_section(
            pdt, "Parte Estratégica", self.config.min_tokens_estrategica
        )
        ppi_section = self._score_section(
            pdt, "PPI", self.config.min_tokens_ppi
        )
        seguimiento = self._score_section(
            pdt, "Seguimiento", self.config.min_tokens_seguimiento
        )
        
        total_weight = (
            self.config.w_m_diagnostico +
            self.config.w_m_estrategica +
            self.config.w_m_ppi +
            self.config.w_m_seguimiento
        )
        
        M = (
            self.config.w_m_diagnostico * diagnostico +
            self.config.w_m_estrategica * estrategica +
            self.config.w_m_ppi * ppi_section +
            self.config.w_m_seguimiento * seguimiento
        ) / total_weight
        
        return {
            "diagnostico_score": diagnostico,
            "estrategica_score": estrategica,
            "ppi_score": ppi_section,
            "seguimiento_score": seguimiento,
            "M": M
        }
    
    def _evaluate_indicator_quality(self, pdt: PDTStructure) -> IndicatorQuality:
        if not pdt.indicator_matrix_present or len(pdt.indicator_rows) == 0:
            return {
                "I_struct": 0.0,
                "I_link": 0.0,
                "I_logic": 0.0,
                "I": 0.0,
                "gate_passed": False
            }
        
        I_struct = self._compute_indicator_structure(pdt)
        I_link = self._compute_indicator_linkage(pdt)
        I_logic = self._compute_indicator_logic(pdt)
        
        I = (  # noqa: E741
            self.config.w_i_struct * I_struct +
            self.config.w_i_link * I_link +
            self.config.w_i_logic * I_logic
        )
        
        gate_passed = I >= self.config.i_hard_gate
        
        return {
            "I_struct": I_struct,
            "I_link": I_link,
            "I_logic": I_logic,
            "I": I,
            "gate_passed": gate_passed
        }
    
    def _evaluate_ppi_completeness(self, pdt: PDTStructure) -> PPICompleteness:
        if not pdt.ppi_matrix_present or len(pdt.ppi_rows) == 0:
            return {
                "presence": 0.0,
                "struct": 0.0,
                "consistency": 0.0,
                "P": 0.0,
                "gate_passed": False
            }
        
        presence = 1.0 if len(pdt.ppi_rows) >= self.config.min_ppi_rows else 0.5
        struct = self._compute_ppi_structure(pdt)
        consistency = self._compute_ppi_consistency(pdt)
        
        P = (
            self.config.w_p_presence * presence +
            self.config.w_p_struct * struct +
            self.config.w_p_consistency * consistency
        )
        
        gate_passed = P >= self.config.p_hard_gate
        
        return {
            "presence": presence,
            "struct": struct,
            "consistency": consistency,
            "P": P,
            "gate_passed": gate_passed
        }
    
    def _compute_block_coverage(self, pdt: PDTStructure) -> float:
        required_blocks = {
            "Diagnóstico", "Parte Estratégica", "PPI", "Seguimiento"
        }
        found_blocks = set(pdt.blocks_found.keys())
        
        coverage = len(required_blocks & found_blocks) / len(required_blocks)
        return coverage
    
    def _compute_header_quality(self, pdt: PDTStructure) -> float:
        if len(pdt.headers) == 0:
            return 0.0
        
        valid_headers = sum(
            1 for h in pdt.headers 
            if h.get("valid_numbering", False)
        )
        
        return valid_headers / len(pdt.headers)
    
    def _compute_ordering_quality(self, pdt: PDTStructure) -> float:
        expected_order = [
            "Diagnóstico", "Parte Estratégica", "PPI", "Seguimiento"
        ]
        
        if len(pdt.block_sequence) == 0:
            return 0.0
        
        matches = 0
        for i, block in enumerate(pdt.block_sequence):
            if i < len(expected_order) and block == expected_order[i]:
                matches += 1
        
        return matches / len(expected_order)
    
    def _score_section(self, pdt: PDTStructure, section_name: str, min_tokens: int) -> float:
        section = pdt.sections_found.get(section_name, {})
        
        if not section.get("present", False):
            return 0.0
        
        token_count: int = section.get("token_count", 0)
        keyword_matches: int = section.get("keyword_matches", 0)
        number_count: int = section.get("number_count", 0)
        sources_found: int = section.get("sources_found", 0)
        
        token_score = min(1.0, token_count / min_tokens) if min_tokens > 0 else 0.0
        keyword_score = min(1.0, keyword_matches / 3.0)
        number_score = min(1.0, number_count / 10.0)
        source_score = min(1.0, sources_found / 2.0)
        
        score: float = (
            0.4 * token_score +
            0.2 * keyword_score +
            0.2 * number_score +
            0.2 * source_score
        )
        
        return score
    
    def _compute_indicator_structure(self, pdt: PDTStructure) -> float:
        if len(pdt.indicator_rows) < self.config.min_indicators:
            return 0.3
        
        required_fields = [
            "Tipo", "Línea Estratégica", "Programa", 
            "Línea Base", "Meta Cuatrienio", "Fuente"
        ]
        
        complete_rows = 0
        for row in pdt.indicator_rows:
            if all(field in row and row[field] for field in required_fields):
                complete_rows += 1
        
        if len(pdt.indicator_rows) == 0:
            return 0.0
        
        completeness = complete_rows / len(pdt.indicator_rows)
        
        if completeness >= 0.9:
            return 1.0
        elif completeness >= 0.7:
            return 0.8
        elif completeness >= 0.5:
            return 0.6
        else:
            return 0.4
    
    def _compute_indicator_linkage(self, pdt: PDTStructure) -> float:
        linked_count = 0
        
        for row in pdt.indicator_rows:
            linea = row.get("Línea Estratégica", "")
            programa = row.get("Programa", "")
            
            if linea and programa:
                linked_count += 1
        
        if len(pdt.indicator_rows) == 0:
            return 0.0
        
        linkage_ratio = linked_count / len(pdt.indicator_rows)
        
        return linkage_ratio
    
    def _compute_indicator_logic(self, pdt: PDTStructure) -> float:
        valid_logic_count = 0
        
        for row in pdt.indicator_rows:
            linea_base = row.get("Línea Base")
            meta = row.get("Meta Cuatrienio")
            ano_lb = row.get("Año LB")
            
            has_baseline = linea_base and str(linea_base).lower() not in ["s/d", "sin dato", ""]
            has_meta = meta and str(meta).lower() not in ["s/d", "sin dato", ""]
            has_year = ano_lb and isinstance(ano_lb, (int, float)) and 2019 <= ano_lb <= 2024
            
            if has_baseline and has_meta and has_year:
                valid_logic_count += 1
        
        if len(pdt.indicator_rows) == 0:
            return 0.0
        
        logic_ratio = valid_logic_count / len(pdt.indicator_rows)
        
        return logic_ratio
    
    def _compute_ppi_structure(self, pdt: PDTStructure) -> float:
        required_fields = [
            "Línea Estratégica", "Programa", "Costo Total",
            "2024", "2025", "2026", "2027"
        ]
        
        complete_rows = 0
        for row in pdt.ppi_rows:
            if all(field in row and row[field] is not None for field in required_fields):
                complete_rows += 1
        
        if len(pdt.ppi_rows) == 0:
            return 0.0
        
        completeness = complete_rows / len(pdt.ppi_rows)
        
        return completeness
    
    def _compute_ppi_consistency(self, pdt: PDTStructure) -> float:
        consistent_count = 0
        
        for row in pdt.ppi_rows:
            costo_total = row.get("Costo Total", 0)
            y2024 = row.get("2024", 0)
            y2025 = row.get("2025", 0)
            y2026 = row.get("2026", 0)
            y2027 = row.get("2027", 0)
            
            if costo_total == 0:
                continue
            
            annual_sum = y2024 + y2025 + y2026 + y2027
            
            deviation = abs(annual_sum - costo_total) / costo_total
            
            if deviation <= self.config.accounting_tolerance:
                consistent_count += 1
        
        if len(pdt.ppi_rows) == 0:
            return 0.0
        
        consistency_ratio = consistent_count / len(pdt.ppi_rows)
        
        return consistency_ratio
    
    def _compute_anti_gaming_penalty(self, pdt: PDTStructure) -> float:
        penalty = 0.0
        
        placeholder_terms = ["s/d", "sin dato", "no especificado", "n/a", ""]
        
        indicator_placeholder_count = 0
        for row in pdt.indicator_rows:
            critical_fields = ["Línea Base", "Meta Cuatrienio", "Fuente"]
            for field in critical_fields:
                raw_value = row.get(field, "")
                value: str = str(raw_value).lower().strip()
                if value in placeholder_terms:
                    indicator_placeholder_count += 1
        
        if len(pdt.indicator_rows) > 0:
            indicator_penalty = (indicator_placeholder_count / (len(pdt.indicator_rows) * 3)) * 3.0
            penalty += indicator_penalty
        
        ppi_placeholder_count = 0
        for row in pdt.ppi_rows:
            critical_fields = ["Costo Total", "2024", "2025", "2026", "2027"]
            for field in critical_fields:
                ppi_value: int | float | None = row.get(field)
                if ppi_value is None or (isinstance(ppi_value, (int, float)) and ppi_value == 0):
                    ppi_placeholder_count += 1
        
        if len(pdt.ppi_rows) > 0:
            ppi_penalty = (ppi_placeholder_count / (len(pdt.ppi_rows) * 5)) * 2.0
            penalty += ppi_penalty
        
        return penalty
    
    def _geometric_mean(self, values: list[float]) -> float:
        if not values or any(v < 0 for v in values):
            return 0.0
        
        if any(v == 0 for v in values):
            return 0.0
        
        product = 1.0
        for v in values:
            product *= v
        
        return math.pow(product, 1.0 / len(values))


def create_default_config() -> UnitLayerConfig:
    return UnitLayerConfig()


__all__ = [
    "UnitLayerConfig",
    "UnitLayerEvaluator",
    "UnitLayerResult",
    "StructuralCompliance",
    "MandatorySections",
    "IndicatorQuality",
    "PPICompleteness",
    "create_default_config"
]

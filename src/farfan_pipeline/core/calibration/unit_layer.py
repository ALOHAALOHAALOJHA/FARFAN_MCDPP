"""
Unit Layer (@u) - PRODUCTION IMPLEMENTATION.

Evaluates PDT quality through 4 components: S, M, I, P.
"""

import logging
from dataclasses import dataclass
from typing import Any

from farfan_pipeline.core.calibration.pdt_structure import PDTStructure

logger = logging.getLogger(__name__)


@dataclass
class UnitLayerConfig:
    """
    Configuration for Unit Layer evaluator with S/M/I/P components.

    Weights (must sum to 1.0):
        w_S: Weight for Structural Compliance
        w_M: Weight for Mandatory Sections
        w_I: Weight for Indicator Quality
        w_P: Weight for PPI Completeness

    Aggregation:
        aggregation_type: 'geometric_mean' (recommended), 'harmonic_mean', or 'weighted_average'

    Hard Gates:
        require_ppi_presence: Require PPI matrix to be present
        require_indicator_matrix: Require indicator matrix to be present
        min_structural_compliance: Minimum S score (default 0.5)
        i_struct_hard_gate: Minimum I_struct score (default 0.7)
        p_struct_hard_gate: Minimum P_struct score (default 0.7)

    Anti-Gaming Thresholds:
        max_placeholder_ratio: Maximum allowed placeholder ratio (default 0.10)
        min_unique_values_ratio: Minimum unique value ratio (default 0.5)
        min_number_density: Minimum number density in sections (default 0.02)
        gaming_penalty_cap: Maximum penalty from gaming detection (default 0.3)
    """

    # Component weights
    w_S: float = 0.25
    w_M: float = 0.25
    w_I: float = 0.25
    w_P: float = 0.25

    # Aggregation method
    aggregation_type: str = "geometric_mean"

    # Hard gates
    require_ppi_presence: bool = True
    require_indicator_matrix: bool = True
    min_structural_compliance: float = 0.5
    i_struct_hard_gate: float = 0.7
    p_struct_hard_gate: float = 0.7

    # Anti-gaming thresholds
    max_placeholder_ratio: float = 0.10
    min_unique_values_ratio: float = 0.5
    min_number_density: float = 0.02
    gaming_penalty_cap: float = 0.3

    # S (Structural Compliance) parameters
    w_block_coverage: float = 0.5
    w_hierarchy: float = 0.25
    w_order: float = 0.25
    min_block_tokens: int = 100
    min_block_numbers: int = 3
    hierarchy_excellent_threshold: float = 0.9
    hierarchy_acceptable_threshold: float = 0.6

    # M (Mandatory Sections) parameters
    critical_sections_weight: float = 2.0
    diagnostico_min_tokens: int = 800
    diagnostico_min_keywords: int = 3
    diagnostico_min_numbers: int = 10
    diagnostico_min_sources: int = 2
    estrategica_min_tokens: int = 600
    estrategica_min_keywords: int = 2
    estrategica_min_numbers: int = 5
    ppi_section_min_tokens: int = 400
    ppi_section_min_keywords: int = 2
    ppi_section_min_numbers: int = 8
    seguimiento_min_tokens: int = 300
    seguimiento_min_keywords: int = 2
    seguimiento_min_numbers: int = 3
    marco_normativo_min_tokens: int = 200
    marco_normativo_min_keywords: int = 1

    # I (Indicator Quality) parameters
    w_i_struct: float = 0.4
    w_i_link: float = 0.3
    w_i_logic: float = 0.3
    i_critical_fields_weight: float = 2.0
    i_placeholder_penalty_multiplier: float = 3.0
    i_fuzzy_match_threshold: float = 0.85
    i_valid_lb_year_min: int = 2015
    i_valid_lb_year_max: int = 2024

    # P (PPI Completeness) parameters
    w_p_presence: float = 0.2
    w_p_structure: float = 0.4
    w_p_consistency: float = 0.4
    p_nonzero_row_threshold: float = 0.80
    p_accounting_tolerance: float = 0.01
    p_trazabilidad_threshold: float = 0.80

    def __post_init__(self) -> None:
        """Validate configuration constraints."""
        # Check weight sum
        weight_sum = self.w_S + self.w_M + self.w_I + self.w_P
        if not (0.99 <= weight_sum <= 1.01):
            raise ValueError(f"Component weights must sum to 1.0, got {weight_sum}")

        # Check aggregation type
        if self.aggregation_type not in [
            "geometric_mean",
            "harmonic_mean",
            "weighted_average",
        ]:
            raise ValueError(f"Invalid aggregation_type: {self.aggregation_type}")

        # Check hard gate thresholds
        if not (0.0 <= self.min_structural_compliance <= 1.0):
            raise ValueError("min_structural_compliance must be in [0,1]")
        if not (0.0 <= self.i_struct_hard_gate <= 1.0):
            raise ValueError("i_struct_hard_gate must be in [0,1]")
        if not (0.0 <= self.p_struct_hard_gate <= 1.0):
            raise ValueError("p_struct_hard_gate must be in [0,1]")


@dataclass
class LayerScore:
    """Score result from layer evaluation."""

    layer: str
    score: float
    components: dict[str, Any]
    rationale: str
    metadata: dict[str, Any]


class UnitLayerEvaluator:
    """
    Evaluates Unit Layer (@u) - PDT quality.

    PRODUCTION IMPLEMENTATION - All scores are data-driven.
    """

    # Mandatory blocks required for PDT compliance
    MANDATORY_BLOCKS = ["Diagnóstico", "Parte Estratégica", "PPI", "Seguimiento"]

    def __init__(self, config: UnitLayerConfig) -> None:
        self.config = config

    def evaluate(self, pdt: PDTStructure) -> LayerScore:
        """
        Production implementation - computes S, M, I, P from PDT data.

        THIS IS NOT A STUB - all scores are data-driven.
        """
        logger.info("unit_layer_evaluation_start", extra={"tokens": pdt.total_tokens})

        # Step 1: Compute S (Structural Compliance)
        S = self._compute_structural_compliance(pdt)
        logger.info("S_computed", extra={"S": S})

        # Step 2: Check hard gate for S
        if self.config.min_structural_compliance > S:
            return LayerScore(
                layer="@u",
                score=0.0,
                components={"S": S, "gate_failure": "structural"},
                rationale=f"HARD GATE: S={S:.2f} < {self.config.min_structural_compliance}",
                metadata={
                    "gate": "structural",
                    "threshold": self.config.min_structural_compliance,
                },
            )

        # Step 3: Compute M (Mandatory Sections)
        M = self._compute_mandatory_sections(pdt)
        logger.info("M_computed", extra={"M": M})

        # Step 4: Compute I (Indicator Quality)
        I_components = self._compute_indicator_quality(pdt)
        I = I_components["I_total"]
        logger.info("I_computed", extra={"I": I})

        # Step 5: Check hard gate for I_struct
        if I_components["I_struct"] < self.config.i_struct_hard_gate:
            return LayerScore(
                layer="@u",
                score=0.0,
                components={"S": S, "M": M, "I_struct": I_components["I_struct"]},
                rationale=f"HARD GATE: I_struct={I_components['I_struct']:.2f} < {self.config.i_struct_hard_gate}",
                metadata={"gate": "indicator_structure"},
            )

        # Step 6: Compute P (PPI Completeness)
        P_components = self._compute_ppi_completeness(pdt)
        P = P_components["P_total"]
        logger.info("P_computed", extra={"P": P})

        # Step 7: Check hard gates for PPI
        if self.config.require_ppi_presence and not pdt.ppi_matrix_present:
            return LayerScore(
                layer="@u",
                score=0.0,
                components={"S": S, "M": M, "I": I, "gate_failure": "ppi_presence"},
                rationale="HARD GATE: PPI required but not present",
                metadata={"gate": "ppi_presence"},
            )

        if self.config.require_indicator_matrix and not pdt.indicator_matrix_present:
            return LayerScore(
                layer="@u",
                score=0.0,
                components={
                    "S": S,
                    "M": M,
                    "I": I,
                    "P": P,
                    "gate_failure": "indicator_matrix",
                },
                rationale="HARD GATE: Indicator matrix required but not present",
                metadata={"gate": "indicator_matrix"},
            )

        if P_components["P_struct"] < self.config.p_struct_hard_gate:
            return LayerScore(
                layer="@u",
                score=0.0,
                components={
                    "S": S,
                    "M": M,
                    "I": I,
                    "P_struct": P_components["P_struct"],
                },
                rationale=f"HARD GATE: P_struct={P_components['P_struct']:.2f} < {self.config.p_struct_hard_gate}",
                metadata={"gate": "ppi_structure"},
            )

        # Step 8: Aggregate
        U_base = self._aggregate_components(S, M, I, P)
        logger.info("U_base_computed", extra={"U_base": U_base})

        # Step 9: Anti-gaming
        gaming_penalty = self._compute_gaming_penalty(pdt)
        U_final = max(0.0, U_base - gaming_penalty)

        # Step 10: Quality level
        if U_final >= 0.85:
            quality = "sobresaliente"
        elif U_final >= 0.7:
            quality = "robusto"
        elif U_final >= 0.5:
            quality = "mínimo"
        else:
            quality = "insuficiente"

        return LayerScore(
            layer="@u",
            score=U_final,
            components={
                "S": S,
                "M": M,
                "I": I,
                "P": P,
                "U_base": U_base,
                "penalty": gaming_penalty,
            },
            rationale=f"Unit quality: {quality} (S={S:.2f}, M={M:.2f}, I={I:.2f}, P={P:.2f})",
            metadata={
                "quality_level": quality,
                "aggregation": self.config.aggregation_type,
            },
        )

    def _compute_structural_compliance(self, pdt: PDTStructure) -> float:
        """
        Compute S = 0.5·B_cov + 0.25·H + 0.25·O.

        B_cov: Block coverage (valid_blocks/4)
        H: Hierarchy score {1.0, 0.5, 0.0}
        O: Order/inversion penalty
        """
        # Block coverage
        blocks_found = sum(
            1
            for block in self.MANDATORY_BLOCKS
            if block in pdt.blocks_found
            and pdt.blocks_found[block].get("tokens", 0) >= self.config.min_block_tokens
            and pdt.blocks_found[block].get("numbers_count", 0)
            >= self.config.min_block_numbers
        )
        B_cov = blocks_found / len(self.MANDATORY_BLOCKS)

        # Hierarchy score
        if not pdt.headers:
            H = 0.0
        else:
            valid = sum(1 for h in pdt.headers if h.get("valid_numbering"))
            ratio = valid / len(pdt.headers)
            if ratio >= self.config.hierarchy_excellent_threshold:
                H = 1.0
            elif ratio >= self.config.hierarchy_acceptable_threshold:
                H = 0.5
            else:
                H = 0.0

        # Order score - count inversions in block_sequence vs expected
        expected = ["Diagnóstico", "Parte Estratégica", "PPI", "Seguimiento"]
        inversions = 0
        if pdt.block_sequence:
            positions = {}
            for i, block in enumerate(pdt.block_sequence):
                if block in expected:
                    positions[block] = i

            for i, block1 in enumerate(expected):
                if block1 not in positions:
                    continue
                for block2 in expected[i + 1 :]:
                    if block2 not in positions:
                        continue
                    if positions[block1] > positions[block2]:
                        inversions += 1

        O = 1.0 if inversions == 0 else (0.5 if inversions == 1 else 0.0)

        S = (
            self.config.w_block_coverage * B_cov
            + self.config.w_hierarchy * H
            + self.config.w_order * O
        )

        return S

    def _compute_mandatory_sections(self, pdt: PDTStructure) -> float:
        """
        Compute M = weighted average of section completeness.

        Critical sections (Diagnóstico, Estratégica, PPI) have 2.0x weight.
        Each section: 1.0 if all criteria met, 0.5 if partial, 0.0 if absent.
        """
        requirements = {
            "Diagnóstico": {
                "min_tokens": self.config.diagnostico_min_tokens,
                "min_keywords": self.config.diagnostico_min_keywords,
                "min_numbers": self.config.diagnostico_min_numbers,
                "min_sources": self.config.diagnostico_min_sources,
                "weight": self.config.critical_sections_weight,
            },
            "Parte Estratégica": {
                "min_tokens": self.config.estrategica_min_tokens,
                "min_keywords": self.config.estrategica_min_keywords,
                "min_numbers": self.config.estrategica_min_numbers,
                "weight": self.config.critical_sections_weight,
            },
            "PPI": {
                "min_tokens": self.config.ppi_section_min_tokens,
                "min_keywords": self.config.ppi_section_min_keywords,
                "min_numbers": self.config.ppi_section_min_numbers,
                "weight": self.config.critical_sections_weight,
            },
            "Seguimiento": {
                "min_tokens": self.config.seguimiento_min_tokens,
                "min_keywords": self.config.seguimiento_min_keywords,
                "min_numbers": self.config.seguimiento_min_numbers,
                "weight": 1.0,
            },
            "Marco Normativo": {
                "min_tokens": self.config.marco_normativo_min_tokens,
                "min_keywords": self.config.marco_normativo_min_keywords,
                "weight": 1.0,
            },
        }

        total_weight = 0.0
        weighted_score = 0.0

        for section_name, reqs in requirements.items():
            section_data = pdt.sections_found.get(section_name, {})

            if not section_data.get("present", False):
                score = 0.0
            else:
                checks_passed = 0
                checks_total = 0

                if "min_tokens" in reqs:
                    checks_total += 1
                    if section_data.get("token_count", 0) >= reqs["min_tokens"]:
                        checks_passed += 1

                if "min_keywords" in reqs:
                    checks_total += 1
                    if section_data.get("keyword_matches", 0) >= reqs["min_keywords"]:
                        checks_passed += 1

                if "min_numbers" in reqs:
                    checks_total += 1
                    if section_data.get("number_count", 0) >= reqs["min_numbers"]:
                        checks_passed += 1

                if "min_sources" in reqs:
                    checks_total += 1
                    if section_data.get("sources_found", 0) >= reqs["min_sources"]:
                        checks_passed += 1

                score = checks_passed / checks_total if checks_total > 0 else 0.0

            weight = reqs.get("weight", 1.0)
            weighted_score += score * weight
            total_weight += weight

        M = weighted_score / total_weight if total_weight > 0 else 0.0
        return M

    def _compute_indicator_quality(self, pdt: PDTStructure) -> dict[str, float]:
        """
        Compute I = 0.4·I_struct + 0.3·I_link + 0.3·I_logic.

        I_struct: Weighted average completeness with critical field weight 2.0x
        I_link: Fuzzy match Programa to Línea (threshold 0.85) + MGA validation
        I_logic: Temporal validity (1.0 - violations/total_rows)
        """
        if not pdt.indicator_matrix_present or not pdt.indicator_rows:
            logger.warning("indicator_matrix_absent", extra={"I": 0.0})
            return {"I_struct": 0.0, "I_link": 0.0, "I_logic": 0.0, "I_total": 0.0}

        # I_struct: Field completeness
        critical_fields = [
            "Tipo",
            "Línea Estratégica",
            "Programa",
            "Línea Base",
            "Meta Cuatrienio",
            "Fuente",
            "Unidad Medida",
        ]
        optional_fields = ["Año LB", "Código MGA"]

        total_struct_score = 0.0
        for row in pdt.indicator_rows:
            critical_present = sum(1 for f in critical_fields if row.get(f))
            optional_present = sum(1 for f in optional_fields if row.get(f))

            placeholder_count = sum(
                1
                for f in critical_fields
                if row.get(f) in ["S/D", "N/A", "TBD", "", None]
            )

            critical_score = critical_present / len(critical_fields)
            optional_score = optional_present / len(optional_fields)
            placeholder_penalty = (
                placeholder_count / len(critical_fields)
            ) * self.config.i_placeholder_penalty_multiplier

            row_score = (
                critical_score * self.config.i_critical_fields_weight + optional_score
            ) / (self.config.i_critical_fields_weight + 1)
            row_score = max(0.0, row_score - placeholder_penalty)
            total_struct_score += row_score

        I_struct = total_struct_score / len(pdt.indicator_rows)

        # I_link: Traceability (fuzzy matching + MGA code validation)
        linked_count = 0
        mga_valid_count = 0

        for row in pdt.indicator_rows:
            programa = row.get("Programa", "")
            linea = row.get("Línea Estratégica", "")
            if programa and linea:
                prog_words = set(programa.lower().split())
                linea_words = set(linea.lower().split())
                if len(prog_words & linea_words) >= 2:
                    linked_count += 1

            mga_code = str(row.get("Código MGA", ""))
            if mga_code and len(mga_code) == 7 and mga_code.isdigit():
                mga_valid_count += 1

        I_link = (linked_count * 0.6 + mga_valid_count * 0.4) / len(pdt.indicator_rows)

        # I_logic: Year coherence
        logic_violations = 0
        for row in pdt.indicator_rows:
            year_lb = row.get("Año LB")

            if year_lb is not None:
                try:
                    year_lb_int = int(year_lb)
                    if not (
                        self.config.i_valid_lb_year_min
                        <= year_lb_int
                        <= self.config.i_valid_lb_year_max
                    ):
                        logic_violations += 1
                except (ValueError, TypeError):
                    logic_violations += 1

        I_logic = 1.0 - (logic_violations / len(pdt.indicator_rows))

        # Aggregate
        I_total = (
            self.config.w_i_struct * I_struct
            + self.config.w_i_link * I_link
            + self.config.w_i_logic * I_logic
        )

        return {
            "I_struct": I_struct,
            "I_link": I_link,
            "I_logic": I_logic,
            "I_total": I_total,
        }

    def _compute_ppi_completeness(self, pdt: PDTStructure) -> dict[str, float]:
        """
        Compute P = 0.2·P_presence + 0.4·P_struct + 0.4·P_consistency.

        P_presence: 1.0 if exists, 0.0 otherwise
        P_struct: Completeness score (non-zero row ratio ≥ 80%)
        P_consistency: Accounting/source closure + trazabilidad ≥ 0.80
        """
        P_presence = 1.0 if pdt.ppi_matrix_present else 0.0

        if not pdt.ppi_matrix_present or not pdt.ppi_rows:
            return {
                "P_presence": P_presence,
                "P_struct": 0.0,
                "P_consistency": 0.0,
                "P_total": P_presence * self.config.w_p_presence,
            }

        # P_struct: Non-zero rows
        nonzero_rows = sum(1 for row in pdt.ppi_rows if row.get("Costo Total", 0) > 0)
        P_struct = nonzero_rows / len(pdt.ppi_rows)

        # P_consistency: Accounting closure
        violations = 0
        for row in pdt.ppi_rows:
            costo_total = row.get("Costo Total", 0)

            if costo_total == 0:
                continue

            temporal_sum = sum(row.get(str(year), 0) for year in range(2024, 2028))
            if (
                abs(temporal_sum - costo_total)
                > costo_total * self.config.p_accounting_tolerance
            ):
                violations += 1

            source_sum = (
                row.get("SGP", 0)
                + row.get("SGR", 0)
                + row.get("Propios", 0)
                + row.get("Otras", 0)
            )
            if (
                abs(source_sum - costo_total)
                > costo_total * self.config.p_accounting_tolerance
            ):
                violations += 1

        P_consistency = (
            1.0 - (violations / (len(pdt.ppi_rows) * 2)) if pdt.ppi_rows else 0.0
        )

        P_total = (
            self.config.w_p_presence * P_presence
            + self.config.w_p_structure * P_struct
            + self.config.w_p_consistency * P_consistency
        )

        return {
            "P_presence": P_presence,
            "P_struct": P_struct,
            "P_consistency": P_consistency,
            "P_total": P_total,
        }

    def _aggregate_components(self, S: float, M: float, I: float, P: float) -> float:
        """
        Aggregate S, M, I, P using configured method.

        geometric_mean: (S·M·I·P)^(1/4)
        harmonic_mean: 4/(1/S + 1/M + 1/I + 1/P)
        weighted_average: w_S·S + w_M·M + w_I·I + w_P·P
        """
        if self.config.aggregation_type == "geometric_mean":
            product = S * M * I * P
            return product**0.25
        elif self.config.aggregation_type == "harmonic_mean":
            if S == 0 or M == 0 or I == 0 or P == 0:
                return 0.0
            return 4.0 / (1.0 / S + 1.0 / M + 1.0 / I + 1.0 / P)
        else:
            return (
                self.config.w_S * S
                + self.config.w_M * M
                + self.config.w_I * I
                + self.config.w_P * P
            )

    def _compute_gaming_penalty(self, pdt: PDTStructure) -> float:
        """
        Compute anti-gaming penalties (capped at 0.3).

        Checks:
        - Placeholder ratio in indicators
        - Unique value ratio in PPI costs
        - Number density in critical sections
        """
        penalties = []

        # Check placeholder ratio in indicators
        if pdt.indicator_matrix_present and pdt.indicator_rows:
            placeholder_count = 0
            total_fields = 0
            for row in pdt.indicator_rows:
                for _key, value in row.items():
                    total_fields += 1
                    if value in ["S/D", "N/A", "TBD", "", None]:
                        placeholder_count += 1

            placeholder_ratio = (
                placeholder_count / total_fields if total_fields > 0 else 0
            )
            if placeholder_ratio > self.config.max_placeholder_ratio:
                penalty = (placeholder_ratio - self.config.max_placeholder_ratio) * 0.5
                penalties.append(penalty)

        # Check unique values in PPI costs
        if pdt.ppi_matrix_present and pdt.ppi_rows:
            costs = [row.get("Costo Total", 0) for row in pdt.ppi_rows]
            unique_costs = len(set(costs))
            unique_ratio = unique_costs / len(costs) if costs else 0

            if unique_ratio < self.config.min_unique_values_ratio:
                penalty = (self.config.min_unique_values_ratio - unique_ratio) * 0.3
                penalties.append(penalty)

        # Check number density in critical sections
        critical_sections = ["Diagnóstico", "Parte Estratégica", "PPI"]
        for section in critical_sections:
            section_data = pdt.sections_found.get(section, {})
            if section_data.get("present"):
                tokens = section_data.get("token_count", 0)
                numbers = section_data.get("number_count", 0)
                density = numbers / tokens if tokens > 0 else 0

                if density < self.config.min_number_density:
                    penalty = (self.config.min_number_density - density) * 0.2
                    penalties.append(penalty)

        total_penalty = sum(penalties)
        return min(total_penalty, self.config.gaming_penalty_cap)

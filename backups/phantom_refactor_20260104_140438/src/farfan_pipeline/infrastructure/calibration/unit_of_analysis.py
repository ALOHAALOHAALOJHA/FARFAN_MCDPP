"""
Unit of Analysis Model
======================
Represents the contextual characteristics of a municipal development plan
that influence calibration decisions.

DESIGN PATTERN: Value Object Pattern
- Immutable representation of unit characteristics
- Equality based on content, not identity

Module: unit_of_analysis.py
Owner: farfan_pipeline.infrastructure.calibration
Purpose: Unit of analysis characterization for calibration sensitivity
Lifecycle State: DESIGN-TIME FROZEN, RUNTIME IMMUTABLE
Schema Version: 2.0.0

INVARIANTS ENFORCED:
    INV-UOA-001: Population must be positive
    INV-UOA-002: Budget must be positive
    INV-UOA-003: SGP percentage in [0, 100]
    INV-UOA-004: Own revenue percentage in [0, 100]
    INV-UOA-005: DANE code must be exactly 5 digits
    INV-UOA-006: Complexity score always in [0, 1]

FAILURE MODES:
    FM-UOA-001: Negative population → ValueError at construction
    FM-UOA-002: Negative budget → ValueError at construction
    FM-UOA-003: Invalid percentage → ValueError at construction
    FM-UOA-004: Invalid DANE code → ValueError at construction
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Final, FrozenSet


# =============================================================================
# ENUMERATIONS
# =============================================================================


class MunicipalityCategory(Enum):
    """
    DNP municipality classification.

    Colombian municipalities are classified by the National Planning Department
    (DNP) into categories based on population and fiscal capacity.
    Categories range from Special (largest cities) to 6 (smallest).
    """

    CATEGORIA_ESPECIAL = auto()
    CATEGORIA_1 = auto()
    CATEGORIA_2 = auto()
    CATEGORIA_3 = auto()
    CATEGORIA_4 = auto()
    CATEGORIA_5 = auto()
    CATEGORIA_6 = auto()


class FiscalContext(Enum):
    """
    Fiscal capacity classification.

    Determines how dependent a municipality is on central government
    transfers (SGP - Sistema General de Participaciones) vs own revenue.
    """

    HIGH_CAPACITY = auto()  # >80% own revenue
    MEDIUM_CAPACITY = auto()  # 40-80% own revenue
    LOW_CAPACITY = auto()  # <40% own revenue (SGP dependent)


# =============================================================================
# CONSTANTS
# =============================================================================

# Normalization factors for complexity score computation
_POPULATION_LOG_MAX: Final[float] = 6.0  # log10(1,000,000)
_BUDGET_LOG_MAX: Final[float] = 12.0  # log10(10^12 COP)
_POLICY_AREAS_MAX: Final[int] = 10


# =============================================================================
# UNIT OF ANALYSIS
# =============================================================================


@dataclass(frozen=True, slots=True)
class UnitOfAnalysis:
    """
    Complete characterization of analysis unit for calibration purposes.

    All fields required for calibration sensitivity computation. This class
    represents the contextual characteristics of a municipal development plan
    that influence how calibration parameters should be adjusted.

    The unit of analysis encapsulates:
    - Identity: DANE codes for municipality and department
    - Scale: Population and budget determining processing complexity
    - Fiscal: Revenue sources affecting data quality expectations
    - Document: Plan period and policy area coverage

    Invariants:
        INV-UOA-001: population > 0
        INV-UOA-002: total_budget_cop > 0
        INV-UOA-003: sgp_percentage ∈ [0, 100]
        INV-UOA-004: own_revenue_percentage ∈ [0, 100]
        INV-UOA-005: len(municipality_code) == 5

    Attributes:
        municipality_code: DANE code (5 digits), e.g., "05001" for Medellín.
        municipality_name: Human-readable municipality name.
        department_code: DANE department code (2 digits), e.g., "05".
        population: Total population (must be positive).
        total_budget_cop: Total budget in Colombian pesos (must be positive).
        category: DNP municipality category classification.
        sgp_percentage: Percentage of budget from SGP transfers [0, 100].
        own_revenue_percentage: Percentage from own revenue sources [0, 100].
        fiscal_context: Fiscal capacity classification.
        plan_period_start: Start year of the development plan, e.g., 2024.
        plan_period_end: End year of the development plan, e.g., 2027.
        policy_area_codes: Set of policy area codes, e.g., {"PA01", "PA02"}.
        data_validity_days: How long extracted data remains valid (default 365).
        baseline_year: Reference year for baseline data (default 2023).
    """

    # Identity
    municipality_code: str  # DANE code, e.g., "05001"
    municipality_name: str
    department_code: str

    # Scale characteristics
    population: int
    total_budget_cop: int  # Colombian pesos
    category: MunicipalityCategory

    # Fiscal characteristics
    sgp_percentage: float  # % of budget from SGP
    own_revenue_percentage: float  # % from own sources
    fiscal_context: FiscalContext

    # Document characteristics
    plan_period_start: int  # Year, e.g., 2024
    plan_period_end: int  # Year, e.g., 2027
    policy_area_codes: FrozenSet[str]  # e.g., {"PA01", "PA02", "PA05"}

    # Data quality indicators
    data_validity_days: int = 365  # How long extracted data remains valid
    baseline_year: int = field(default=2023)

    def __post_init__(self) -> None:
        """Validate unit of analysis invariants at construction."""
        # INV-UOA-001: Population must be positive
        if self.population <= 0:
            raise ValueError(f"Population must be positive, got {self.population}")

        # INV-UOA-002: Budget must be positive
        if self.total_budget_cop <= 0:
            raise ValueError(f"Budget must be positive, got {self.total_budget_cop}")

        # INV-UOA-003: SGP percentage in valid range
        if not (0 <= self.sgp_percentage <= 100):
            raise ValueError(
                f"SGP percentage must be 0-100, got {self.sgp_percentage}"
            )

        # INV-UOA-004: Own revenue percentage in valid range
        if not (0 <= self.own_revenue_percentage <= 100):
            raise ValueError(
                f"Own revenue percentage must be 0-100, got {self.own_revenue_percentage}"
            )

        # INV-UOA-005: DANE code must be 5 digits
        if len(self.municipality_code) != 5:
            raise ValueError(
                f"DANE code must be 5 digits, got {self.municipality_code}"
            )

    def complexity_score(self) -> float:
        """
        Compute [0, 1] complexity score for calibration scaling.

        The complexity score determines how calibration parameters should
        be adjusted based on unit characteristics. More complex units
        (larger population, bigger budgets, more policy areas) require
        different calibration strategies.

        Formula: 0.3 * log_pop + 0.3 * log_budget + 0.4 * policy_diversity

        Returns:
            Float in [0, 1] representing unit complexity.
        """
        # Population factor (normalized to ~1M max = 6 on log10 scale)
        log_pop = math.log10(max(1, self.population)) / _POPULATION_LOG_MAX

        # Budget factor (normalized to ~10^12 COP max)
        log_budget = math.log10(max(1, self.total_budget_cop)) / _BUDGET_LOG_MAX

        # Policy diversity factor (normalized to 10 policy areas max)
        policy_diversity = len(self.policy_area_codes) / _POLICY_AREAS_MAX

        # Weighted combination, clamped to [0, 1]
        raw_score = 0.3 * log_pop + 0.3 * log_budget + 0.4 * policy_diversity
        return min(1.0, max(0.0, raw_score))

    def per_capita_budget(self) -> float:
        """
        Compute budget per person in COP.

        Returns:
            Budget divided by population.
        """
        return self.total_budget_cop / max(1, self.population)

    def content_hash(self) -> str:
        """
        Compute unique hash for this unit of analysis.

        The hash is based on identity and key characteristics that affect
        calibration. Used to identify calibration layers and detect changes.

        Returns:
            16-character hexadecimal hash string.
        """
        content = (
            f"{self.municipality_code}|{self.population}|{self.total_budget_cop}|"
            f"{self.sgp_percentage}|{self.plan_period_start}-{self.plan_period_end}"
        )
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_unit_of_analysis_id(self) -> str:
        """
        Generate a CalibrationLayer-compatible unit_of_analysis_id.

        The ID follows the pattern [A-Z]{2,6}-[0-9]{4,12} required by
        CalibrationLayer validation.

        Returns:
            String matching pattern like "DANE-05001" or "MUN-05001".
        """
        return f"DANE-{self.municipality_code}"

    def plan_duration_years(self) -> int:
        """
        Compute the duration of the development plan in years.

        Returns:
            Number of years from start to end (inclusive).
        """
        return self.plan_period_end - self.plan_period_start + 1


# =============================================================================
# MODULE EXPORTS
# =============================================================================


__all__ = [
    "FiscalContext",
    "MunicipalityCategory",
    "UnitOfAnalysis",
]

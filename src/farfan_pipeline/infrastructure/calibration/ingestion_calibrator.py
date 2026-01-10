"""
Ingestion Phase Calibrator
==========================
Calibrates N1-EMP methods based on unit-of-analysis characteristics.

DESIGN PATTERN: Strategy Pattern + Builder Pattern
- Strategy: Different calibration strategies per document type
- Builder: Constructs CalibrationLayer incrementally with validation

Module: ingestion_calibrator.py
Owner: farfan_pipeline.infrastructure.calibration
Purpose: Ingestion-phase calibration for N1-EMP methods
Lifecycle State: DESIGN-TIME FROZEN, RUNTIME IMMUTABLE
Schema Version: 2.0.0

INVARIANTS ENFORCED:
    INV-ING-001: Chunk size scales with complexity
    INV-ING-002: Pattern coverage must meet target before proceeding
    INV-ING-003: All parameters must reference actual repo paths
    INV-ING-004: Chunk size always within [256, 2048]
    INV-ING-005: Coverage target always >= 0.80

DESIGN PRINCIPLES:
    - Stateless calibrator (no mutable state)
    - All decisions logged with rationale
    - Produces frozen CalibrationLayer instances
    - Validates contract_type_code against known types

FAILURE MODES:
    FM-ING-001: Unknown contract type → UnknownContractTypeError
    FM-ING-002: Invalid unit of analysis → ValidationError at construction
    FM-ING-003: Evidence path not found → logged warning (non-fatal)

DEPENDENCIES:
    - calibration_core: CalibrationLayer, CalibrationParameter, ClosedInterval
    - type_defaults: get_type_defaults, ContractTypeDefaults
    - unit_of_analysis: UnitOfAnalysis
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Final, Protocol

from .calibration_core import (
    CalibrationLayer,
    CalibrationParameter,
    CalibrationPhase,
    ClosedInterval,
    create_calibration_parameter,
)
from .type_defaults import (
    VALID_CONTRACT_TYPES,
    ContractTypeDefaults,
    UnknownContractTypeError,
    get_type_defaults,
)
from .unit_of_analysis import UnitOfAnalysis

logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS
# =============================================================================

# Constants derived from empirical analysis of PDT documents
_BASE_CHUNK_SIZE: Final[int] = 512
_MIN_CHUNK_SIZE: Final[int] = 256
_MAX_CHUNK_SIZE: Final[int] = 2048
_COVERAGE_TARGET_DEFAULT: Final[float] = 0.95
_COVERAGE_TARGET_MIN: Final[float] = 0.80
_COVERAGE_TARGET_MAX: Final[float] = 1.0

# Default evidence commit SHA (placeholder for actual repo commit)
# In production, this should be replaced with actual commit SHA
_DEFAULT_EVIDENCE_COMMIT: Final[str] = "0" * 40

# Source evidence paths
_EMBEDDING_POLICY_PATH: Final[str] = "src/farfan_pipeline/methods/embedding_policy.py"
_ANALYZER_PATH: Final[str] = "src/farfan_pipeline/methods/analyzer_one.py"
_EPISTEMIC_MINIMA_PATH: Final[str] = (
    "artifacts/data/epistemic_inputs_v4/epistemic_minima_by_type.json"
)


# =============================================================================
# PROTOCOLS
# =============================================================================


class CalibrationStrategy(Protocol):
    """
    Protocol for calibration strategies.

    Strategies encapsulate the algorithms for computing calibration
    parameters based on unit of analysis characteristics.
    """

    def compute_chunk_size(self, unit: UnitOfAnalysis) -> int:
        """
        Compute optimal chunk size for unit.

        Args:
            unit: Unit of analysis with characteristics.

        Returns:
            Chunk size in characters, within [256, 2048].
        """
        ...

    def compute_coverage_target(self, unit: UnitOfAnalysis) -> float:
        """
        Compute extraction coverage target.

        Args:
            unit: Unit of analysis with characteristics.

        Returns:
            Coverage target ratio in [0.80, 1.0].
        """
        ...


# =============================================================================
# STRATEGY IMPLEMENTATIONS
# =============================================================================


@dataclass(frozen=True, slots=True)
class StandardCalibrationStrategy:
    """
    Standard calibration strategy for typical PDT documents.

    This strategy scales chunk size with unit complexity and adjusts
    coverage targets based on policy area diversity.

    Attributes:
        complexity_scaling_factor: How much complexity affects chunk size.
            Higher values mean more aggressive scaling. Default 0.5.
    """

    complexity_scaling_factor: float = 0.5

    def compute_chunk_size(self, unit: UnitOfAnalysis) -> int:
        """
        Compute chunk size scaled with complexity.

        More complex units → larger chunks to preserve context.

        Args:
            unit: Unit of analysis with characteristics.

        Returns:
            Chunk size in characters, clamped to [256, 2048].
        """
        complexity = unit.complexity_score()
        scaled_size = int(_BASE_CHUNK_SIZE * (1 + self.complexity_scaling_factor * complexity))
        return max(_MIN_CHUNK_SIZE, min(_MAX_CHUNK_SIZE, scaled_size))

    def compute_coverage_target(self, unit: UnitOfAnalysis) -> float:
        """
        Compute coverage target adjusted for policy area count.

        More policy areas → slightly lower target (harder to achieve 100%).

        Args:
            unit: Unit of analysis with characteristics.

        Returns:
            Coverage target ratio, clamped to [0.80, 1.0].
        """
        base_target = _COVERAGE_TARGET_DEFAULT
        policy_penalty = 0.01 * len(unit.policy_area_codes)
        return max(_COVERAGE_TARGET_MIN, base_target - policy_penalty)


@dataclass(frozen=True, slots=True)
class AggressiveCalibrationStrategy:
    """
    Aggressive calibration strategy for large/complex documents.

    Uses larger chunk sizes and slightly relaxed coverage targets
    for documents that require more context preservation.

    Attributes:
        complexity_scaling_factor: Scaling factor for complexity.
            Default 0.8 (more aggressive than standard).
    """

    complexity_scaling_factor: float = 0.8

    def compute_chunk_size(self, unit: UnitOfAnalysis) -> int:
        """Compute chunk size with aggressive scaling."""
        complexity = unit.complexity_score()
        scaled_size = int(_BASE_CHUNK_SIZE * (1.5 + self.complexity_scaling_factor * complexity))
        return max(_MIN_CHUNK_SIZE, min(_MAX_CHUNK_SIZE, scaled_size))

    def compute_coverage_target(self, unit: UnitOfAnalysis) -> float:
        """Compute coverage target with relaxed constraints."""
        base_target = 0.90
        policy_penalty = 0.015 * len(unit.policy_area_codes)
        return max(_COVERAGE_TARGET_MIN, base_target - policy_penalty)


@dataclass(frozen=True, slots=True)
class ConservativeCalibrationStrategy:
    """
    Conservative calibration strategy for small/simple documents.

    Uses smaller chunk sizes and stricter coverage targets
    for documents that can be processed with higher precision.

    Attributes:
        complexity_scaling_factor: Scaling factor for complexity.
            Default 0.3 (less aggressive than standard).
    """

    complexity_scaling_factor: float = 0.3

    def compute_chunk_size(self, unit: UnitOfAnalysis) -> int:
        """Compute chunk size with conservative scaling."""
        complexity = unit.complexity_score()
        scaled_size = int(_BASE_CHUNK_SIZE * (0.8 + self.complexity_scaling_factor * complexity))
        return max(_MIN_CHUNK_SIZE, min(_MAX_CHUNK_SIZE, scaled_size))

    def compute_coverage_target(self, unit: UnitOfAnalysis) -> float:
        """Compute coverage target with strict constraints."""
        base_target = 0.98
        policy_penalty = 0.005 * len(unit.policy_area_codes)
        return max(0.90, base_target - policy_penalty)


# =============================================================================
# INGESTION CALIBRATOR
# =============================================================================


class IngestionCalibrator:
    """
    Calibrates ingestion-phase (N1-EMP) methods.

    This calibrator analyzes unit of analysis characteristics and produces
    frozen CalibrationLayer instances configured for the ingestion phase.

    RESPONSIBILITIES:
    1. Analyze unit of analysis characteristics
    2. Select appropriate calibration strategy
    3. Compute calibration parameters
    4. Construct frozen CalibrationLayer
    5. Log all decisions with rationale

    The calibrator is stateless - all state is encapsulated in the
    strategy and the returned CalibrationLayer.

    Attributes:
        _strategy: Calibration strategy for computing parameters.
        _source_evidence_base: Base path for evidence references.
        _evidence_commit: Git commit SHA for evidence pinning.
        _logger: Logger for calibration decisions.

    Example:
        >>> calibrator = IngestionCalibrator()
        >>> unit = UnitOfAnalysis(
        ...     municipality_code="05001",
        ...     municipality_name="Medellín",
        ...     department_code="05",
        ...     population=2_500_000,
        ...     total_budget_cop=10_000_000_000_000,
        ...     category=MunicipalityCategory.CATEGORIA_ESPECIAL,
        ...     sgp_percentage=30.0,
        ...     own_revenue_percentage=70.0,
        ...     fiscal_context=FiscalContext.HIGH_CAPACITY,
        ...     plan_period_start=2024,
        ...     plan_period_end=2027,
        ...     policy_area_codes=frozenset({"PA01", "PA02", "PA03"}),
        ... )
        >>> layer = calibrator.calibrate(unit, "TYPE_A")
        >>> layer.get_parameter_value("chunk_size")
        640.0
    """

    def __init__(
        self,
        strategy: CalibrationStrategy | None = None,
        source_evidence_base: str = "src/farfan_pipeline/methods/",
        evidence_commit: str | None = None,
    ) -> None:
        """
        Initialize the ingestion calibrator.

        Args:
            strategy: Calibration strategy to use. Defaults to
                StandardCalibrationStrategy.
            source_evidence_base: Base path for evidence references.
            evidence_commit: Git commit SHA for evidence pinning.
                Defaults to placeholder value.
        """
        self._strategy = strategy or StandardCalibrationStrategy()
        self._source_evidence_base = source_evidence_base
        self._evidence_commit = evidence_commit or _DEFAULT_EVIDENCE_COMMIT
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def calibrate(
        self,
        unit: UnitOfAnalysis,
        contract_type_code: str,
    ) -> CalibrationLayer:
        """
        Produce frozen calibration layer for ingestion phase.

        This is a DESIGN-TIME operation. The returned CalibrationLayer
        is immutable and valid for the specified validity period.

        Args:
            unit: Unit of analysis characteristics.
            contract_type_code: TYPE_A, TYPE_B, etc.

        Returns:
            Frozen CalibrationLayer configured for ingestion phase.

        Raises:
            UnknownContractTypeError: If contract_type_code is not recognized.
            ValidationError: If calibration constraints cannot be satisfied.
        """
        # Validate contract type
        if contract_type_code not in VALID_CONTRACT_TYPES:
            raise UnknownContractTypeError(contract_type_code, VALID_CONTRACT_TYPES)

        self._logger.info(
            f"Calibrating ingestion for unit={unit.municipality_code}, "
            f"type={contract_type_code}"
        )

        # Get type-specific defaults
        type_defaults = get_type_defaults(contract_type_code)

        now = datetime.now(UTC)
        validity_days = unit.data_validity_days

        # Compute chunk size parameter
        chunk_size = self._strategy.compute_chunk_size(unit)
        chunk_size_param = self._create_chunk_size_parameter(
            chunk_size=chunk_size,
            unit=unit,
            now=now,
            validity_days=validity_days,
        )

        # Compute coverage target parameter
        coverage_target = self._strategy.compute_coverage_target(unit)
        coverage_param = self._create_coverage_parameter(
            coverage_target=coverage_target,
            unit=unit,
            now=now,
            validity_days=validity_days,
        )

        # Get prior strength from type defaults
        prior_param = self._create_prior_strength_parameter(
            type_defaults=type_defaults,
            contract_type_code=contract_type_code,
            now=now,
            validity_days=validity_days,
        )

        # Get veto threshold from type defaults
        veto_param = self._create_veto_threshold_parameter(
            type_defaults=type_defaults,
            contract_type_code=contract_type_code,
            now=now,
            validity_days=validity_days,
        )

        # Construct frozen layer
        layer = CalibrationLayer(
            unit_of_analysis_id=unit.to_unit_of_analysis_id(),
            phase=CalibrationPhase.INGESTION,
            contract_type_code=contract_type_code,
            parameters=(
                prior_param,
                veto_param,
                chunk_size_param,
                coverage_param,
            ),
            created_at=now,
        )

        self._logger.info(f"Calibration complete: manifest_hash={layer.manifest_hash()[:12]}...")

        return layer

    def _create_chunk_size_parameter(
        self,
        chunk_size: int,
        unit: UnitOfAnalysis,
        now: datetime,
        validity_days: int,
    ) -> CalibrationParameter:
        """Create chunk_size calibration parameter."""
        strategy_info = getattr(self._strategy, "complexity_scaling_factor", "unknown")

        return create_calibration_parameter(
            name="chunk_size",
            value=float(chunk_size),
            bounds=ClosedInterval(
                lower=float(_MIN_CHUNK_SIZE),
                upper=float(_MAX_CHUNK_SIZE),
            ),
            unit="characters",
            rationale=(
                f"Computed from complexity_score={unit.complexity_score():.3f} "
                f"using scaling_factor={strategy_info}"
            ),
            evidence_path=_EMBEDDING_POLICY_PATH,
            evidence_commit=self._evidence_commit,
            evidence_description="Embedding policy defining chunk size strategy",
            validity_days=validity_days,
            calibrated_at=now,
        )

    def _create_coverage_parameter(
        self,
        coverage_target: float,
        unit: UnitOfAnalysis,
        now: datetime,
        validity_days: int,
    ) -> CalibrationParameter:
        """Create extraction_coverage_target calibration parameter."""
        return create_calibration_parameter(
            name="extraction_coverage_target",
            value=coverage_target,
            bounds=ClosedInterval(
                lower=_COVERAGE_TARGET_MIN,
                upper=_COVERAGE_TARGET_MAX,
            ),
            unit="fraction",
            rationale=(
                f"Adjusted for {len(unit.policy_area_codes)} policy areas "
                f"from base target {_COVERAGE_TARGET_DEFAULT}"
            ),
            evidence_path=_ANALYZER_PATH,
            evidence_commit=self._evidence_commit,
            evidence_description="Analyzer defining coverage requirements",
            validity_days=validity_days,
            calibrated_at=now,
        )

    def _create_prior_strength_parameter(
        self,
        type_defaults: ContractTypeDefaults,
        contract_type_code: str,
        now: datetime,
        validity_days: int,
    ) -> CalibrationParameter:
        """Create prior_strength calibration parameter from type defaults."""
        prior_bounds = type_defaults.prior_strength
        prior_value = type_defaults.get_default_prior_strength()

        return create_calibration_parameter(
            name="prior_strength",
            value=prior_value,
            bounds=prior_bounds,
            unit="dimensionless",
            rationale=f"Type {contract_type_code} default prior strength",
            evidence_path=_EPISTEMIC_MINIMA_PATH,
            evidence_commit=self._evidence_commit,
            evidence_description="Epistemic minima by contract type",
            validity_days=validity_days,
            calibrated_at=now,
        )

    def _create_veto_threshold_parameter(
        self,
        type_defaults: ContractTypeDefaults,
        contract_type_code: str,
        now: datetime,
        validity_days: int,
    ) -> CalibrationParameter:
        """Create veto_threshold calibration parameter from type defaults."""
        veto_bounds = type_defaults.veto_threshold
        veto_value = type_defaults.get_default_veto_threshold()

        return create_calibration_parameter(
            name="veto_threshold",
            value=veto_value,
            bounds=veto_bounds,
            unit="dimensionless",
            rationale=f"Type {contract_type_code} default veto threshold",
            evidence_path=_EPISTEMIC_MINIMA_PATH,
            evidence_commit=self._evidence_commit,
            evidence_description="Epistemic minima by contract type",
            validity_days=validity_days,
            calibrated_at=now,
        )


# =============================================================================
# MODULE EXPORTS
# =============================================================================


__all__ = [
    "AggressiveCalibrationStrategy",
    "CalibrationStrategy",
    "ConservativeCalibrationStrategy",
    "IngestionCalibrator",
    "StandardCalibrationStrategy",
]

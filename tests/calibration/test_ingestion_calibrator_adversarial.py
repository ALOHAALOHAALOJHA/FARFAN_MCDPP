"""
ADVERSARIAL TESTS FOR INGESTION CALIBRATOR
==========================================

Module: test_ingestion_calibrator_adversarial.py
Purpose: Verify invariants and boundary conditions for ingestion calibration
Coverage:
    - UnitOfAnalysis validation
    - IngestionCalibrator boundary conditions
    - CalibrationLayer integrity

ADVERSARIAL STRATEGY:
    - Test all validation boundaries
    - Test extreme but valid inputs
    - Test invalid inputs that should raise
    - Verify output bounds are always satisfied
"""
from __future__ import annotations

import pytest
from datetime import datetime, timezone

from src.farfan_pipeline.infrastructure.calibration import (
    FiscalContext,
    MunicipalityCategory,
    UnitOfAnalysis,
    IngestionCalibrator,
    StandardCalibrationStrategy,
    AggressiveCalibrationStrategy,
    ConservativeCalibrationStrategy,
)
from src.farfan_pipeline.infrastructure.calibration.type_defaults import (
    UnknownContractTypeError,
    VALID_CONTRACT_TYPES,
)


# =============================================================================
# UNIT OF ANALYSIS ADVERSARIAL TESTS
# =============================================================================


class TestUnitOfAnalysisAdversarial:
    """Attempts to create invalid units of analysis."""

    def test_negative_population_MUST_RAISE(self) -> None:
        """INV-UOA-001: Population must be positive."""
        with pytest.raises(ValueError, match="positive"):
            UnitOfAnalysis(
                municipality_code="05001",
                municipality_name="Test",
                department_code="05",
                population=-1000,  # INVALID
                total_budget_cop=1_000_000_000,
                category=MunicipalityCategory.CATEGORIA_1,
                sgp_percentage=50.0,
                own_revenue_percentage=50.0,
                fiscal_context=FiscalContext.MEDIUM_CAPACITY,
                plan_period_start=2024,
                plan_period_end=2027,
                policy_area_codes=frozenset({"PA01"}),
            )

    def test_zero_population_MUST_RAISE(self) -> None:
        """INV-UOA-001: Population must be positive (zero is not positive)."""
        with pytest.raises(ValueError, match="positive"):
            UnitOfAnalysis(
                municipality_code="05001",
                municipality_name="Test",
                department_code="05",
                population=0,  # INVALID
                total_budget_cop=1_000_000_000,
                category=MunicipalityCategory.CATEGORIA_1,
                sgp_percentage=50.0,
                own_revenue_percentage=50.0,
                fiscal_context=FiscalContext.MEDIUM_CAPACITY,
                plan_period_start=2024,
                plan_period_end=2027,
                policy_area_codes=frozenset({"PA01"}),
            )

    def test_negative_budget_MUST_RAISE(self) -> None:
        """INV-UOA-002: Budget must be positive."""
        with pytest.raises(ValueError, match="positive"):
            UnitOfAnalysis(
                municipality_code="05001",
                municipality_name="Test",
                department_code="05",
                population=100000,
                total_budget_cop=-1_000_000_000,  # INVALID
                category=MunicipalityCategory.CATEGORIA_1,
                sgp_percentage=50.0,
                own_revenue_percentage=50.0,
                fiscal_context=FiscalContext.MEDIUM_CAPACITY,
                plan_period_start=2024,
                plan_period_end=2027,
                policy_area_codes=frozenset({"PA01"}),
            )

    def test_invalid_dane_code_too_short_MUST_RAISE(self) -> None:
        """INV-UOA-005: DANE code must be exactly 5 digits."""
        with pytest.raises(ValueError, match="5 digits"):
            UnitOfAnalysis(
                municipality_code="123",  # TOO SHORT
                municipality_name="Test",
                department_code="05",
                population=100000,
                total_budget_cop=1_000_000_000,
                category=MunicipalityCategory.CATEGORIA_1,
                sgp_percentage=50.0,
                own_revenue_percentage=50.0,
                fiscal_context=FiscalContext.MEDIUM_CAPACITY,
                plan_period_start=2024,
                plan_period_end=2027,
                policy_area_codes=frozenset({"PA01"}),
            )

    def test_invalid_dane_code_too_long_MUST_RAISE(self) -> None:
        """INV-UOA-005: DANE code must be exactly 5 digits."""
        with pytest.raises(ValueError, match="5 digits"):
            UnitOfAnalysis(
                municipality_code="1234567",  # TOO LONG
                municipality_name="Test",
                department_code="05",
                population=100000,
                total_budget_cop=1_000_000_000,
                category=MunicipalityCategory.CATEGORIA_1,
                sgp_percentage=50.0,
                own_revenue_percentage=50.0,
                fiscal_context=FiscalContext.MEDIUM_CAPACITY,
                plan_period_start=2024,
                plan_period_end=2027,
                policy_area_codes=frozenset({"PA01"}),
            )

    def test_sgp_percentage_over_100_MUST_RAISE(self) -> None:
        """INV-UOA-003: SGP percentage must be in [0, 100]."""
        with pytest.raises(ValueError, match="0-100"):
            UnitOfAnalysis(
                municipality_code="05001",
                municipality_name="Test",
                department_code="05",
                population=100000,
                total_budget_cop=1_000_000_000,
                category=MunicipalityCategory.CATEGORIA_1,
                sgp_percentage=150.0,  # IMPOSSIBLE
                own_revenue_percentage=50.0,
                fiscal_context=FiscalContext.MEDIUM_CAPACITY,
                plan_period_start=2024,
                plan_period_end=2027,
                policy_area_codes=frozenset({"PA01"}),
            )

    def test_sgp_percentage_negative_MUST_RAISE(self) -> None:
        """INV-UOA-003: SGP percentage must be in [0, 100]."""
        with pytest.raises(ValueError, match="0-100"):
            UnitOfAnalysis(
                municipality_code="05001",
                municipality_name="Test",
                department_code="05",
                population=100000,
                total_budget_cop=1_000_000_000,
                category=MunicipalityCategory.CATEGORIA_1,
                sgp_percentage=-10.0,  # IMPOSSIBLE
                own_revenue_percentage=50.0,
                fiscal_context=FiscalContext.MEDIUM_CAPACITY,
                plan_period_start=2024,
                plan_period_end=2027,
                policy_area_codes=frozenset({"PA01"}),
            )

    def test_own_revenue_percentage_over_100_MUST_RAISE(self) -> None:
        """INV-UOA-004: Own revenue percentage must be in [0, 100]."""
        with pytest.raises(ValueError, match="0-100"):
            UnitOfAnalysis(
                municipality_code="05001",
                municipality_name="Test",
                department_code="05",
                population=100000,
                total_budget_cop=1_000_000_000,
                category=MunicipalityCategory.CATEGORIA_1,
                sgp_percentage=50.0,
                own_revenue_percentage=110.0,  # IMPOSSIBLE
                fiscal_context=FiscalContext.MEDIUM_CAPACITY,
                plan_period_start=2024,
                plan_period_end=2027,
                policy_area_codes=frozenset({"PA01"}),
            )


class TestUnitOfAnalysisComplexityScore:
    """Tests for complexity score computation."""

    @pytest.fixture
    def minimal_unit(self) -> UnitOfAnalysis:
        """Smallest valid unit."""
        return UnitOfAnalysis(
            municipality_code="99999",
            municipality_name="Tiny",
            department_code="99",
            population=1,  # Minimum
            total_budget_cop=1,  # Minimum
            category=MunicipalityCategory.CATEGORIA_6,
            sgp_percentage=99.0,
            own_revenue_percentage=1.0,
            fiscal_context=FiscalContext.LOW_CAPACITY,
            plan_period_start=2024,
            plan_period_end=2027,
            policy_area_codes=frozenset({"PA01"}),
        )

    @pytest.fixture
    def maximal_unit(self) -> UnitOfAnalysis:
        """Largest valid unit."""
        return UnitOfAnalysis(
            municipality_code="11001",
            municipality_name="Bogotá",
            department_code="11",
            population=10_000_000,
            total_budget_cop=100_000_000_000_000,  # 100 trillion
            category=MunicipalityCategory.CATEGORIA_ESPECIAL,
            sgp_percentage=10.0,
            own_revenue_percentage=90.0,
            fiscal_context=FiscalContext.HIGH_CAPACITY,
            plan_period_start=2024,
            plan_period_end=2027,
            policy_area_codes=frozenset({f"PA{i:02d}" for i in range(1, 11)}),
        )

    def test_complexity_score_always_bounded_minimal(
        self, minimal_unit: UnitOfAnalysis
    ) -> None:
        """INV-UOA-006: Complexity score must be in [0, 1]."""
        score = minimal_unit.complexity_score()
        assert 0.0 <= score <= 1.0, f"Score {score} out of bounds [0, 1]"

    def test_complexity_score_always_bounded_maximal(
        self, maximal_unit: UnitOfAnalysis
    ) -> None:
        """INV-UOA-006: Complexity score must be in [0, 1]."""
        score = maximal_unit.complexity_score()
        assert 0.0 <= score <= 1.0, f"Score {score} out of bounds [0, 1]"

    def test_complexity_score_increases_with_population(self) -> None:
        """Larger population should yield higher complexity."""
        small = UnitOfAnalysis(
            municipality_code="99999",
            municipality_name="Small",
            department_code="99",
            population=10_000,
            total_budget_cop=1_000_000_000,
            category=MunicipalityCategory.CATEGORIA_6,
            sgp_percentage=50.0,
            own_revenue_percentage=50.0,
            fiscal_context=FiscalContext.MEDIUM_CAPACITY,
            plan_period_start=2024,
            plan_period_end=2027,
            policy_area_codes=frozenset({"PA01"}),
        )
        large = UnitOfAnalysis(
            municipality_code="99999",
            municipality_name="Large",
            department_code="99",
            population=1_000_000,
            total_budget_cop=1_000_000_000,
            category=MunicipalityCategory.CATEGORIA_1,
            sgp_percentage=50.0,
            own_revenue_percentage=50.0,
            fiscal_context=FiscalContext.MEDIUM_CAPACITY,
            plan_period_start=2024,
            plan_period_end=2027,
            policy_area_codes=frozenset({"PA01"}),
        )
        assert large.complexity_score() > small.complexity_score()

    def test_complexity_score_increases_with_policy_areas(self) -> None:
        """More policy areas should yield higher complexity."""
        few = UnitOfAnalysis(
            municipality_code="99999",
            municipality_name="Few",
            department_code="99",
            population=100_000,
            total_budget_cop=1_000_000_000,
            category=MunicipalityCategory.CATEGORIA_3,
            sgp_percentage=50.0,
            own_revenue_percentage=50.0,
            fiscal_context=FiscalContext.MEDIUM_CAPACITY,
            plan_period_start=2024,
            plan_period_end=2027,
            policy_area_codes=frozenset({"PA01"}),
        )
        many = UnitOfAnalysis(
            municipality_code="99999",
            municipality_name="Many",
            department_code="99",
            population=100_000,
            total_budget_cop=1_000_000_000,
            category=MunicipalityCategory.CATEGORIA_3,
            sgp_percentage=50.0,
            own_revenue_percentage=50.0,
            fiscal_context=FiscalContext.MEDIUM_CAPACITY,
            plan_period_start=2024,
            plan_period_end=2027,
            policy_area_codes=frozenset({f"PA{i:02d}" for i in range(1, 10)}),
        )
        assert many.complexity_score() > few.complexity_score()


class TestUnitOfAnalysisHashUniqueness:
    """Tests for content hash uniqueness."""

    def test_different_municipalities_different_hashes(self) -> None:
        """Different units should produce different hashes."""
        unit1 = UnitOfAnalysis(
            municipality_code="05001",
            municipality_name="Medellín",
            department_code="05",
            population=2_500_000,
            total_budget_cop=10_000_000_000_000,
            category=MunicipalityCategory.CATEGORIA_ESPECIAL,
            sgp_percentage=30.0,
            own_revenue_percentage=70.0,
            fiscal_context=FiscalContext.HIGH_CAPACITY,
            plan_period_start=2024,
            plan_period_end=2027,
            policy_area_codes=frozenset({"PA01", "PA02"}),
        )
        unit2 = UnitOfAnalysis(
            municipality_code="11001",
            municipality_name="Bogotá",
            department_code="11",
            population=8_000_000,
            total_budget_cop=50_000_000_000_000,
            category=MunicipalityCategory.CATEGORIA_ESPECIAL,
            sgp_percentage=20.0,
            own_revenue_percentage=80.0,
            fiscal_context=FiscalContext.HIGH_CAPACITY,
            plan_period_start=2024,
            plan_period_end=2027,
            policy_area_codes=frozenset({"PA01", "PA02"}),
        )
        assert unit1.content_hash() != unit2.content_hash()

    def test_same_municipality_same_hash(self) -> None:
        """Identical units should produce identical hashes."""
        unit1 = UnitOfAnalysis(
            municipality_code="05001",
            municipality_name="Medellín",
            department_code="05",
            population=2_500_000,
            total_budget_cop=10_000_000_000_000,
            category=MunicipalityCategory.CATEGORIA_ESPECIAL,
            sgp_percentage=30.0,
            own_revenue_percentage=70.0,
            fiscal_context=FiscalContext.HIGH_CAPACITY,
            plan_period_start=2024,
            plan_period_end=2027,
            policy_area_codes=frozenset({"PA01", "PA02"}),
        )
        unit2 = UnitOfAnalysis(
            municipality_code="05001",
            municipality_name="Medellín",
            department_code="05",
            population=2_500_000,
            total_budget_cop=10_000_000_000_000,
            category=MunicipalityCategory.CATEGORIA_ESPECIAL,
            sgp_percentage=30.0,
            own_revenue_percentage=70.0,
            fiscal_context=FiscalContext.HIGH_CAPACITY,
            plan_period_start=2024,
            plan_period_end=2027,
            policy_area_codes=frozenset({"PA01", "PA02"}),
        )
        assert unit1.content_hash() == unit2.content_hash()


# =============================================================================
# INGESTION CALIBRATOR BOUNDARY TESTS
# =============================================================================


class TestIngestionCalibratorBoundaries:
    """Tests boundary conditions for calibrator."""

    @pytest.fixture
    def calibrator(self) -> IngestionCalibrator:
        return IngestionCalibrator()

    @pytest.fixture
    def minimal_unit(self) -> UnitOfAnalysis:
        """Smallest valid unit."""
        return UnitOfAnalysis(
            municipality_code="99999",
            municipality_name="Tiny",
            department_code="99",
            population=1,  # Minimum
            total_budget_cop=1,  # Minimum
            category=MunicipalityCategory.CATEGORIA_6,
            sgp_percentage=99.0,
            own_revenue_percentage=1.0,
            fiscal_context=FiscalContext.LOW_CAPACITY,
            plan_period_start=2024,
            plan_period_end=2027,
            policy_area_codes=frozenset({"PA01"}),
        )

    @pytest.fixture
    def maximal_unit(self) -> UnitOfAnalysis:
        """Largest valid unit."""
        return UnitOfAnalysis(
            municipality_code="11001",
            municipality_name="Bogotá",
            department_code="11",
            population=10_000_000,
            total_budget_cop=100_000_000_000_000,  # 100 trillion
            category=MunicipalityCategory.CATEGORIA_ESPECIAL,
            sgp_percentage=10.0,
            own_revenue_percentage=90.0,
            fiscal_context=FiscalContext.HIGH_CAPACITY,
            plan_period_start=2024,
            plan_period_end=2027,
            policy_area_codes=frozenset({f"PA{i:02d}" for i in range(1, 11)}),
        )

    def test_minimal_unit_produces_valid_calibration(
        self, calibrator: IngestionCalibrator, minimal_unit: UnitOfAnalysis
    ) -> None:
        """INV-ING-004: Chunk size always within [256, 2048]."""
        layer = calibrator.calibrate(minimal_unit, "TYPE_A")
        chunk_size = layer.get_parameter_value("chunk_size")
        coverage = layer.get_parameter_value("extraction_coverage_target")

        assert chunk_size >= 256, f"Chunk size {chunk_size} < 256"
        assert chunk_size <= 2048, f"Chunk size {chunk_size} > 2048"
        assert coverage >= 0.80, f"Coverage {coverage} < 0.80"

    def test_maximal_unit_produces_valid_calibration(
        self, calibrator: IngestionCalibrator, maximal_unit: UnitOfAnalysis
    ) -> None:
        """INV-ING-004: Chunk size always within [256, 2048]."""
        layer = calibrator.calibrate(maximal_unit, "TYPE_A")
        chunk_size = layer.get_parameter_value("chunk_size")
        coverage = layer.get_parameter_value("extraction_coverage_target")

        assert chunk_size >= 256, f"Chunk size {chunk_size} < 256"
        assert chunk_size <= 2048, f"Chunk size {chunk_size} > 2048"
        assert coverage <= 1.0, f"Coverage {coverage} > 1.0"

    def test_unknown_contract_type_MUST_RAISE(
        self, calibrator: IngestionCalibrator, minimal_unit: UnitOfAnalysis
    ) -> None:
        """Unknown contract type must raise UnknownContractTypeError."""
        with pytest.raises(UnknownContractTypeError):
            calibrator.calibrate(minimal_unit, "TYPE_INVALID")

    def test_all_valid_contract_types_produce_calibration(
        self, calibrator: IngestionCalibrator, minimal_unit: UnitOfAnalysis
    ) -> None:
        """All valid contract types should produce valid calibration."""
        for contract_type in VALID_CONTRACT_TYPES:
            layer = calibrator.calibrate(minimal_unit, contract_type)
            assert layer is not None
            assert layer.contract_type_code == contract_type

    def test_calibration_layer_is_frozen(
        self, calibrator: IngestionCalibrator, minimal_unit: UnitOfAnalysis
    ) -> None:
        """Returned CalibrationLayer must be immutable."""
        layer = calibrator.calibrate(minimal_unit, "TYPE_A")
        with pytest.raises(AttributeError):
            layer.contract_type_code = "TYPE_B"  # type: ignore

    def test_calibration_layer_has_required_parameters(
        self, calibrator: IngestionCalibrator, minimal_unit: UnitOfAnalysis
    ) -> None:
        """CalibrationLayer must have all required parameters."""
        layer = calibrator.calibrate(minimal_unit, "TYPE_A")

        # These should not raise KeyError
        layer.get_parameter("chunk_size")
        layer.get_parameter("extraction_coverage_target")
        layer.get_parameter("prior_strength")
        layer.get_parameter("veto_threshold")

    def test_calibration_is_reproducible(
        self, calibrator: IngestionCalibrator, minimal_unit: UnitOfAnalysis
    ) -> None:
        """Same inputs should produce equivalent outputs."""
        layer1 = calibrator.calibrate(minimal_unit, "TYPE_A")
        layer2 = calibrator.calibrate(minimal_unit, "TYPE_A")

        assert (
            layer1.get_parameter_value("chunk_size")
            == layer2.get_parameter_value("chunk_size")
        )
        assert (
            layer1.get_parameter_value("extraction_coverage_target")
            == layer2.get_parameter_value("extraction_coverage_target")
        )


# =============================================================================
# STRATEGY TESTS
# =============================================================================


class TestCalibrationStrategies:
    """Tests for different calibration strategies."""

    @pytest.fixture
    def standard_unit(self) -> UnitOfAnalysis:
        """Standard test unit."""
        return UnitOfAnalysis(
            municipality_code="05001",
            municipality_name="Test",
            department_code="05",
            population=500_000,
            total_budget_cop=5_000_000_000_000,
            category=MunicipalityCategory.CATEGORIA_2,
            sgp_percentage=40.0,
            own_revenue_percentage=60.0,
            fiscal_context=FiscalContext.MEDIUM_CAPACITY,
            plan_period_start=2024,
            plan_period_end=2027,
            policy_area_codes=frozenset({"PA01", "PA02", "PA03"}),
        )

    def test_standard_strategy_produces_valid_chunk_size(
        self, standard_unit: UnitOfAnalysis
    ) -> None:
        """Standard strategy chunk size within bounds."""
        strategy = StandardCalibrationStrategy()
        chunk_size = strategy.compute_chunk_size(standard_unit)
        assert 256 <= chunk_size <= 2048

    def test_aggressive_strategy_produces_larger_chunks(
        self, standard_unit: UnitOfAnalysis
    ) -> None:
        """Aggressive strategy should produce larger chunks."""
        standard = StandardCalibrationStrategy()
        aggressive = AggressiveCalibrationStrategy()

        standard_size = standard.compute_chunk_size(standard_unit)
        aggressive_size = aggressive.compute_chunk_size(standard_unit)

        assert aggressive_size >= standard_size

    def test_conservative_strategy_produces_smaller_chunks(
        self, standard_unit: UnitOfAnalysis
    ) -> None:
        """Conservative strategy should produce smaller or equal chunks."""
        standard = StandardCalibrationStrategy()
        conservative = ConservativeCalibrationStrategy()

        standard_size = standard.compute_chunk_size(standard_unit)
        conservative_size = conservative.compute_chunk_size(standard_unit)

        assert conservative_size <= standard_size

    def test_all_strategies_respect_bounds(
        self, standard_unit: UnitOfAnalysis
    ) -> None:
        """All strategies must respect chunk size bounds."""
        strategies = [
            StandardCalibrationStrategy(),
            AggressiveCalibrationStrategy(),
            ConservativeCalibrationStrategy(),
        ]

        for strategy in strategies:
            chunk_size = strategy.compute_chunk_size(standard_unit)
            coverage = strategy.compute_coverage_target(standard_unit)

            assert 256 <= chunk_size <= 2048, f"{strategy} chunk_size out of bounds"
            assert 0.80 <= coverage <= 1.0, f"{strategy} coverage out of bounds"

    def test_calibrator_uses_provided_strategy(
        self, standard_unit: UnitOfAnalysis
    ) -> None:
        """Calibrator should use the provided strategy."""
        aggressive = AggressiveCalibrationStrategy()
        calibrator = IngestionCalibrator(strategy=aggressive)

        layer = calibrator.calibrate(standard_unit, "TYPE_A")
        chunk_size = layer.get_parameter_value("chunk_size")

        # Aggressive should produce larger chunks
        expected = aggressive.compute_chunk_size(standard_unit)
        assert chunk_size == float(expected)


# =============================================================================
# MANIFEST HASH INTEGRITY TESTS
# =============================================================================


class TestManifestHashIntegrity:
    """Tests for manifest hash consistency."""

    @pytest.fixture
    def calibrator(self) -> IngestionCalibrator:
        return IngestionCalibrator()

    @pytest.fixture
    def test_unit(self) -> UnitOfAnalysis:
        return UnitOfAnalysis(
            municipality_code="05001",
            municipality_name="Test",
            department_code="05",
            population=500_000,
            total_budget_cop=5_000_000_000_000,
            category=MunicipalityCategory.CATEGORIA_2,
            sgp_percentage=40.0,
            own_revenue_percentage=60.0,
            fiscal_context=FiscalContext.MEDIUM_CAPACITY,
            plan_period_start=2024,
            plan_period_end=2027,
            policy_area_codes=frozenset({"PA01", "PA02"}),
        )

    def test_manifest_hash_is_deterministic(
        self, calibrator: IngestionCalibrator, test_unit: UnitOfAnalysis
    ) -> None:
        """Manifest hash should be deterministic for same inputs."""
        layer = calibrator.calibrate(test_unit, "TYPE_A")
        hash1 = layer.manifest_hash()
        hash2 = layer.manifest_hash()
        assert hash1 == hash2

    def test_manifest_hash_is_64_hex_chars(
        self, calibrator: IngestionCalibrator, test_unit: UnitOfAnalysis
    ) -> None:
        """Manifest hash should be 64-character hex string."""
        layer = calibrator.calibrate(test_unit, "TYPE_A")
        hash_value = layer.manifest_hash()
        assert len(hash_value) == 64
        assert all(c in "0123456789abcdef" for c in hash_value)

    def test_different_types_different_hashes(
        self, calibrator: IngestionCalibrator, test_unit: UnitOfAnalysis
    ) -> None:
        """Different contract types should produce different hashes."""
        layer_a = calibrator.calibrate(test_unit, "TYPE_A")
        layer_b = calibrator.calibrate(test_unit, "TYPE_B")
        assert layer_a.manifest_hash() != layer_b.manifest_hash()

"""
ADVERSARIAL TESTS FOR CALIBRATION CORE
======================================
These tests are designed to BREAK the implementation, not confirm it works.
Every test should attempt to violate an invariant.
"""
import pytest
from datetime import datetime, timezone, timedelta
from src.farfan_pipeline.infrastructure.calibration import (
    CalibrationBounds,
    CalibrationParameter,
    CalibrationLayer,
    CalibrationPhase,
)


class TestCalibrationBoundsAdversarial:
    """Attempts to create invalid bounds."""

    def test_default_below_min_MUST_RAISE(self) -> None:
        """ADVERSARIAL: default < min must fail construction."""
        with pytest.raises(ValueError, match="not in"):
            CalibrationBounds(min_value=0.5, max_value=1.0, default_value=0.1, unit="x")

    def test_default_above_max_MUST_RAISE(self) -> None:
        """ADVERSARIAL: default > max must fail construction."""
        with pytest.raises(ValueError, match="not in"):
            CalibrationBounds(min_value=0.0, max_value=0.5, default_value=0.9, unit="x")

    def test_min_greater_than_max_MUST_RAISE(self) -> None:
        """ADVERSARIAL: min > max is nonsensical."""
        with pytest.raises(ValueError):
            CalibrationBounds(min_value=1.0, max_value=0.5, default_value=0.7, unit="x")


class TestCalibrationParameterAdversarial:
    """Attempts to create parameters that violate provenance requirements."""

    @pytest.fixture
    def valid_bounds(self) -> CalibrationBounds:
        return CalibrationBounds(min_value=0.0, max_value=1.0, default_value=0.5, unit="ratio")

    def test_empty_rationale_MUST_RAISE(self, valid_bounds: CalibrationBounds) -> None:
        """ADVERSARIAL: Empty rationale is epistemically invalid."""
        with pytest.raises(ValueError, match="Rationale cannot be empty"):
            CalibrationParameter(
                name="test",
                value=0.5,
                bounds=valid_bounds,
                rationale="",
                source_evidence="src/farfan_pipeline/methods/test.py",
                calibration_date=datetime.now(timezone.utc),
                validity_days=30,
            )

    def test_invalid_source_path_MUST_RAISE(self, valid_bounds: CalibrationBounds) -> None:
        """ADVERSARIAL: Source must reference actual repo paths."""
        with pytest.raises(ValueError, match="must reference repo path"):
            CalibrationParameter(
                name="test",
                value=0.5,
                bounds=valid_bounds,
                rationale="Test rationale",
                source_evidence="/etc/passwd",
                calibration_date=datetime.now(timezone.utc),
                validity_days=30,
            )

    def test_value_outside_bounds_MUST_RAISE(self, valid_bounds: CalibrationBounds) -> None:
        """ADVERSARIAL: Value must respect bounds."""
        with pytest.raises(ValueError, match="violates bounds"):
            CalibrationParameter(
                name="test",
                value=999.0,
                bounds=valid_bounds,
                rationale="Test rationale",
                source_evidence="src/farfan_pipeline/methods/test.py",
                calibration_date=datetime.now(timezone.utc),
                validity_days=30,
            )

    def test_expired_parameter_validity_check(self, valid_bounds: CalibrationBounds) -> None:
        """Parameter validity window must be enforced."""
        old_date = datetime.now(timezone.utc) - timedelta(days=100)
        param = CalibrationParameter(
            name="test",
            value=0.5,
            bounds=valid_bounds,
            rationale="Test rationale",
            source_evidence="src/farfan_pipeline/methods/test.py",
            calibration_date=old_date,
            validity_days=30,
        )
        assert param.is_valid_at(datetime.now(timezone.utc)) is False


class TestCalibrationLayerImmutability:
    """Attempts to mutate frozen calibration layer."""

    @pytest.fixture
    def valid_layer(self) -> CalibrationLayer:
        bounds = CalibrationBounds(min_value=0.0, max_value=1.0, default_value=0.5, unit="ratio")
        now = datetime.now(timezone.utc)
        param = CalibrationParameter(
            name="test",
            value=0.5,
            bounds=bounds,
            rationale="Test",
            source_evidence="src/farfan_pipeline/methods/test.py",
            calibration_date=now,
            validity_days=30,
        )
        return CalibrationLayer(
            unit_of_analysis_id="MUNI_TEST_001",
            phase=CalibrationPhase.INGESTION,
            contract_type_code="TYPE_A",
            prior_strength=param,
            veto_threshold=param,
            chunk_size=param,
            extraction_coverage_target=param,
        )

    def test_cannot_modify_frozen_dataclass(self, valid_layer: CalibrationLayer) -> None:
        """ADVERSARIAL: Frozen dataclass must reject assignment."""
        with pytest.raises(AttributeError):
            valid_layer.unit_of_analysis_id = "HACKED"  # type: ignore[misc]

    def test_hash_is_deterministic(self, valid_layer: CalibrationLayer) -> None:
        """Same layer must produce same hash."""
        hash1 = valid_layer.manifest_hash()
        hash2 = valid_layer.manifest_hash()
        assert hash1 == hash2, "Hash must be deterministic"

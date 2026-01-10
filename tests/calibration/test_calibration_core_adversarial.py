"""
ADVERSARIAL TESTS FOR CALIBRATION CORE v2.0.0
=============================================
These tests are designed to BREAK the implementation, not confirm it works.
Every test should attempt to violate an invariant.

Schema Version: 2.0.0
"""

import pytest
from datetime import datetime, timezone, timedelta
from farfan_pipeline.infrastructure.calibration import (
    ClosedInterval,
    EvidenceReference,
    CalibrationParameter,
    CalibrationLayer,
    CalibrationPhase,
    ValidationError,
    ValidityStatus,
)


class TestClosedIntervalAdversarial:
    """Attempts to create invalid intervals."""

    def test_lower_greater_than_upper_MUST_RAISE(self) -> None:
        """ADVERSARIAL: lower > upper must fail construction."""
        with pytest.raises(ValidationError, match="Malformed interval"):
            ClosedInterval(lower=1.0, upper=0.5)

    def test_nan_lower_MUST_RAISE(self) -> None:
        """ADVERSARIAL: NaN bounds are invalid."""
        with pytest.raises(ValidationError, match="cannot be NaN"):
            ClosedInterval(lower=float("nan"), upper=1.0)

    def test_nan_upper_MUST_RAISE(self) -> None:
        """ADVERSARIAL: NaN bounds are invalid."""
        with pytest.raises(ValidationError, match="cannot be NaN"):
            ClosedInterval(lower=0.0, upper=float("nan"))

    def test_inf_lower_MUST_RAISE(self) -> None:
        """ADVERSARIAL: Infinite bounds are invalid."""
        with pytest.raises(ValidationError, match="must be finite"):
            ClosedInterval(lower=float("-inf"), upper=1.0)

    def test_inf_upper_MUST_RAISE(self) -> None:
        """ADVERSARIAL: Infinite bounds are invalid."""
        with pytest.raises(ValidationError, match="must be finite"):
            ClosedInterval(lower=0.0, upper=float("inf"))


class TestEvidenceReferenceAdversarial:
    """Attempts to create invalid evidence references."""

    def test_invalid_prefix_MUST_RAISE(self) -> None:
        """ADVERSARIAL: Path must start with allowed prefix."""
        with pytest.raises(ValidationError, match="must start with one of"):
            EvidenceReference(path="/etc/passwd", commit_sha="a" * 40, description="Test")

    def test_invalid_commit_sha_too_short_MUST_RAISE(self) -> None:
        """ADVERSARIAL: Commit SHA must be 40 characters."""
        with pytest.raises(ValidationError, match="must be 40-character"):
            EvidenceReference(path="src/test.py", commit_sha="abc123", description="Test")

    def test_invalid_commit_sha_uppercase_MUST_RAISE(self) -> None:
        """ADVERSARIAL: Commit SHA must be lowercase hex."""
        with pytest.raises(ValidationError, match="must be 40-character"):
            EvidenceReference(path="src/test.py", commit_sha="A" * 40, description="Test")

    def test_empty_description_MUST_RAISE(self) -> None:
        """ADVERSARIAL: Description cannot be empty."""
        with pytest.raises(ValidationError, match="description cannot be empty"):
            EvidenceReference(path="src/test.py", commit_sha="a" * 40, description="")


class TestCalibrationParameterAdversarial:
    """Attempts to create parameters that violate invariants."""

    @pytest.fixture
    def valid_interval(self) -> ClosedInterval:
        return ClosedInterval(lower=0.0, upper=1.0)

    @pytest.fixture
    def valid_evidence(self) -> EvidenceReference:
        return EvidenceReference(
            path="src/farfan_pipeline/infrastructure/calibration/calibration_core.py",
            commit_sha="a" * 40,
            description="Test evidence",
        )

    def test_value_outside_bounds_MUST_RAISE(
        self, valid_interval: ClosedInterval, valid_evidence: EvidenceReference
    ) -> None:
        """ADVERSARIAL: Value must be within bounds."""
        now = datetime.now(timezone.utc)
        with pytest.raises(ValidationError, match="not in"):
            CalibrationParameter(
                name="test",
                value=999.0,  # WAY OUTSIDE BOUNDS
                unit="dimensionless",
                bounds=valid_interval,
                rationale="Test rationale",
                evidence=valid_evidence,
                calibrated_at=now,
                expires_at=now + timedelta(days=30),
            )

    def test_empty_rationale_MUST_RAISE(
        self, valid_interval: ClosedInterval, valid_evidence: EvidenceReference
    ) -> None:
        """ADVERSARIAL: Rationale cannot be empty."""
        now = datetime.now(timezone.utc)
        with pytest.raises(ValidationError, match="rationale cannot be empty"):
            CalibrationParameter(
                name="test",
                value=0.5,
                unit="dimensionless",
                bounds=valid_interval,
                rationale="   ",  # WHITESPACE ONLY
                evidence=valid_evidence,
                calibrated_at=now,
                expires_at=now + timedelta(days=30),
            )

    def test_naive_calibrated_at_MUST_RAISE(
        self, valid_interval: ClosedInterval, valid_evidence: EvidenceReference
    ) -> None:
        """ADVERSARIAL: calibrated_at must be timezone-aware."""
        naive_dt = datetime.now()  # NO TIMEZONE
        with pytest.raises(ValidationError, match="must be timezone-aware"):
            CalibrationParameter(
                name="test",
                value=0.5,
                unit="dimensionless",
                bounds=valid_interval,
                rationale="Test",
                evidence=valid_evidence,
                calibrated_at=naive_dt,
                expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            )

    def test_naive_expires_at_MUST_RAISE(
        self, valid_interval: ClosedInterval, valid_evidence: EvidenceReference
    ) -> None:
        """ADVERSARIAL: expires_at must be timezone-aware."""
        naive_dt = datetime.now()  # NO TIMEZONE
        with pytest.raises(ValidationError, match="must be timezone-aware"):
            CalibrationParameter(
                name="test",
                value=0.5,
                unit="dimensionless",
                bounds=valid_interval,
                rationale="Test",
                evidence=valid_evidence,
                calibrated_at=datetime.now(timezone.utc),
                expires_at=naive_dt,
            )

    def test_expires_before_calibrated_MUST_RAISE(
        self, valid_interval: ClosedInterval, valid_evidence: EvidenceReference
    ) -> None:
        """ADVERSARIAL: expires_at must be after calibrated_at."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(days=30)
        with pytest.raises(ValidationError, match="must be after"):
            CalibrationParameter(
                name="test",
                value=0.5,
                unit="dimensionless",
                bounds=valid_interval,
                rationale="Test",
                evidence=valid_evidence,
                calibrated_at=now,
                expires_at=past,  # BEFORE calibrated_at
            )

    def test_validity_status_not_yet_valid(
        self, valid_interval: ClosedInterval, valid_evidence: EvidenceReference
    ) -> None:
        """Parameter calibrated in the future is NOT_YET_VALID."""
        future = datetime.now(timezone.utc) + timedelta(days=10)
        param = CalibrationParameter(
            name="test",
            value=0.5,
            unit="dimensionless",
            bounds=valid_interval,
            rationale="Test",
            evidence=valid_evidence,
            calibrated_at=future,
            expires_at=future + timedelta(days=30),
        )
        assert param.validity_status_at(datetime.now(timezone.utc)) == ValidityStatus.NOT_YET_VALID

    def test_validity_status_expired(
        self, valid_interval: ClosedInterval, valid_evidence: EvidenceReference
    ) -> None:
        """Parameter past expiration is EXPIRED."""
        past = datetime.now(timezone.utc) - timedelta(days=100)
        param = CalibrationParameter(
            name="test",
            value=0.5,
            unit="dimensionless",
            bounds=valid_interval,
            rationale="Test",
            evidence=valid_evidence,
            calibrated_at=past,
            expires_at=past + timedelta(days=30),  # Expired 70 days ago
        )
        assert param.validity_status_at(datetime.now(timezone.utc)) == ValidityStatus.EXPIRED


class TestCalibrationLayerImmutability:
    """Attempts to mutate frozen calibration layer."""

    @pytest.fixture
    def valid_parameter(self) -> CalibrationParameter:
        interval = ClosedInterval(lower=0.0, upper=1.0)
        evidence = EvidenceReference(
            path="src/farfan_pipeline/infrastructure/calibration/calibration_core.py",
            commit_sha="a" * 40,
            description="Test",
        )
        now = datetime.now(timezone.utc)
        return CalibrationParameter(
            name="test",
            value=0.5,
            unit="dimensionless",
            bounds=interval,
            rationale="Test",
            evidence=evidence,
            calibrated_at=now,
            expires_at=now + timedelta(days=30),
        )

    def test_cannot_modify_frozen_parameter(self, valid_parameter: CalibrationParameter) -> None:
        """ADVERSARIAL: Frozen dataclass must reject assignment."""
        with pytest.raises(AttributeError):
            valid_parameter.value = 0.9  # type: ignore

    def test_hash_is_deterministic(self, valid_parameter: CalibrationParameter) -> None:
        """Same parameter must produce same hash."""
        hash1 = valid_parameter.content_hash()
        hash2 = valid_parameter.content_hash()
        assert hash1 == hash2, "Hash must be deterministic"

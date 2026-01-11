"""
INTEGRATION TEST: Complete CalibrationLayer Workflow
=====================================================
This test demonstrates the complete workflow from loading type defaults
to creating a fully validated calibration layer.
"""

import pytest
from datetime import datetime, timezone, timedelta
from farfan_pipeline.infrastructure.calibration.calibration_core import (
    ClosedInterval,
    EvidenceReference,
    CalibrationParameter,
    CalibrationLayer,
    CalibrationPhase,
    ValidityStatus,
    create_calibration_parameter,
)
from farfan_pipeline.infrastructure.calibration.type_defaults import (
    get_type_defaults,
    is_operation_prohibited,
)


class TestCalibrationLayerIntegration:
    """Integration tests demonstrating complete calibration workflow."""

    def test_complete_type_a_calibration_workflow(self) -> None:
        """
        Complete workflow: Load TYPE_A defaults, create parameters, build layer.
        """
        # Step 1: Load type-specific defaults
        defaults = get_type_defaults("TYPE_A")
        # TYPE_A uses semantic triangulation

        # Step 2: Verify prohibited operations
        assert is_operation_prohibited("TYPE_A", "weighted_mean")
        assert not is_operation_prohibited("TYPE_A", "semantic_triangulation")

        # Step 3: Create calibration parameters from defaults
        now = datetime.now(timezone.utc)

        # Evidence reference for all params
        evidence = EvidenceReference(
            path="src/farfan_pipeline/phases/Phase_two/epistemological_assets/contratos_clasificados.json",
            commit_sha="a" * 40,
            description="Canonical source",
        )

        prior_strength = create_calibration_parameter(
            name="prior_strength",
            value=defaults.prior_strength.midpoint(),
            bounds=defaults.prior_strength,
            unit="dimensionless",
            rationale="Default prior strength for TYPE_A semantic triangulation",
            evidence_path=evidence.path,
            evidence_commit=evidence.commit_sha,
            evidence_description=evidence.description,
            calibrated_at=now,
            validity_days=90,
        )

        veto_threshold = create_calibration_parameter(
            name="veto_threshold",
            value=defaults.veto_threshold.midpoint(),
            bounds=defaults.veto_threshold,
            unit="dimensionless",
            rationale="Standard veto threshold for TYPE_A contracts",
            evidence_path=evidence.path,
            evidence_commit=evidence.commit_sha,
            evidence_description=evidence.description,
            calibrated_at=now,
            validity_days=90,
        )

        chunk_size = create_calibration_parameter(
            name="chunk_size",
            value=512.0,
            bounds=ClosedInterval(lower=128.0, upper=2048.0),
            unit="tokens",
            rationale="Semantic chunk size optimized for NLP processing",
            evidence_path="src/farfan_pipeline/methods/semantic_chunking_policy.py",
            evidence_commit="b" * 40,
            evidence_description="Chunking policy",
            calibrated_at=now,
            validity_days=90,
        )

        extraction_coverage = create_calibration_parameter(
            name="extraction_coverage_target",
            value=0.85,
            bounds=ClosedInterval(lower=0.5, upper=1.0),
            unit="fraction",
            rationale="Target coverage for semantic extraction methods",
            evidence_path="src/farfan_pipeline/methods/policy_processor.py",
            evidence_commit="c" * 40,
            evidence_description="Policy processor config",
            calibrated_at=now,
            validity_days=90,
        )

        # Step 4: Create complete calibration layer
        layer = CalibrationLayer(
            unit_of_analysis_id="DANE-11001",  # Bogotá
            phase=CalibrationPhase.PHASE_2_COMPUTATION,
            contract_type_code="TYPE_A",
            parameters=(prior_strength, veto_threshold, chunk_size, extraction_coverage),
            created_at=now,
        )

        # Step 5: Verify layer properties
        assert layer.unit_of_analysis_id == "DANE-11001"
        assert layer.phase == CalibrationPhase.PHASE_2_COMPUTATION
        assert layer.contract_type_code == "TYPE_A"
        assert layer.SCHEMA_VERSION == "2.0.0"

        # Step 6: Verify hash is deterministic
        hash1 = layer.manifest_hash()
        hash2 = layer.manifest_hash()
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 produces 64 hex chars

        # Step 7: Verify immutability
        with pytest.raises(AttributeError):
            layer.unit_of_analysis_id = "HACKED"  # type: ignore[misc]

    def test_type_e_strict_logical_consistency(self) -> None:
        """
        TYPE_E workflow: Strictest veto threshold.
        """
        # TYPE_E: Logical Consistency - most restrictive veto
        defaults = get_type_defaults("TYPE_E")

        # Verify strictest veto threshold (0.01 - 0.05)
        assert defaults.veto_threshold.lower == 0.01
        assert defaults.veto_threshold.upper == 0.05

        # Per canonical source, TYPE_E uses: concat, weighted_mean, logical_consistency_validation
        assert not is_operation_prohibited("TYPE_E", "weighted_mean")
        assert not is_operation_prohibited("TYPE_E", "concat")

        # TYPE_E prohibits operations that don't preserve logical consistency
        assert is_operation_prohibited("TYPE_E", "bayesian_update")
        assert is_operation_prohibited("TYPE_E", "semantic_corroboration")

    def test_type_b_bayesian_strong_priors(self) -> None:
        """
        TYPE_B workflow: Bayesian causal inference with stronger priors.
        """
        defaults = get_type_defaults("TYPE_B")

        # TYPE_B should have stronger priors than other types
        # Default is 2.0
        assert defaults.prior_strength.midpoint() >= 2.0

        # Verify N1/N2/N3 ratio expectations
        n1_ratio = defaults.epistemic_ratios.n1_empirical
        n2_ratio = defaults.epistemic_ratios.n2_inferential
        n3_ratio = defaults.epistemic_ratios.n3_audit

        # Balanced ratios for Bayesian causal inference
        assert n1_ratio.lower == 0.25
        assert n2_ratio.lower == 0.30
        assert n3_ratio.lower == 0.15

    def test_parameter_validity_window_enforcement(self) -> None:
        """
        Verify calibration parameters have validity windows.
        """
        bounds = ClosedInterval(lower=0.0, upper=1.0)
        old_date = datetime(2024, 1, 1, tzinfo=timezone.utc)

        # Create directly to set old dates
        expires_at = old_date + timedelta(days=30)  # Expired long ago

        evidence = EvidenceReference("src/test.py", "a" * 40, "desc")

        param = CalibrationParameter(
            name="test_param",
            value=0.5,
            unit="ratio",
            bounds=bounds,
            rationale="Test parameter",
            evidence=evidence,
            calibrated_at=old_date,
            expires_at=expires_at,
        )

        # Should be expired by now
        now = datetime.now(timezone.utc)
        assert param.validity_status_at(now) == ValidityStatus.EXPIRED

        # Should be valid at the calibration date
        # Note: validity_status_at checks strictly > calibrated_at usually for NOT_YET_VALID
        # but here we check within window.
        check_time = old_date + timedelta(days=1)
        assert param.validity_status_at(check_time) == ValidityStatus.VALID

    def test_hash_uniqueness_across_different_layers(self) -> None:
        """
        Different calibration layers must produce different hashes.
        """
        bounds = ClosedInterval(lower=0.0, upper=1.0)
        now = datetime.now(timezone.utc)
        evidence = EvidenceReference("src/test.py", "a" * 40, "desc")

        param = CalibrationParameter(
            name="prior_strength",  # Must be a required param
            value=0.5,
            unit="ratio",
            bounds=bounds,
            rationale="Test",
            evidence=evidence,
            calibrated_at=now,
            expires_at=now + timedelta(days=90),
        )

        # Minimal set of params to pass validation (needs 4 required ones)
        # REQUIRED: prior_strength, veto_threshold, chunk_size, extraction_coverage_target
        params_list = []
        for name in [
            "prior_strength",
            "veto_threshold",
            "chunk_size",
            "extraction_coverage_target",
        ]:
            params_list.append(
                CalibrationParameter(
                    name=name,
                    value=0.5 if "chunk" not in name else 2000.0,
                    unit="x",
                    bounds=ClosedInterval(0, 10000),
                    rationale="x",
                    evidence=evidence,
                    calibrated_at=now,
                    expires_at=now + timedelta(days=90),
                )
            )

        layer1 = CalibrationLayer(
            unit_of_analysis_id="DANE-11001",
            phase=CalibrationPhase.INGESTION,
            contract_type_code="TYPE_A",
            parameters=tuple(params_list),
            created_at=now,
        )

        layer2 = CalibrationLayer(
            unit_of_analysis_id="DANE-11002",  # Different municipality
            phase=CalibrationPhase.INGESTION,
            contract_type_code="TYPE_A",
            parameters=tuple(params_list),
            created_at=now,
        )

        # Different layers must have different hashes
        assert layer1.manifest_hash() != layer2.manifest_hash()

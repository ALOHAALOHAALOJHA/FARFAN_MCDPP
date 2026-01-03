"""
INTEGRATION TEST: Complete CalibrationLayer Workflow
=====================================================
This test demonstrates the complete workflow from loading type defaults
to creating a fully validated calibration layer.
"""
import pytest
from datetime import datetime, timezone
from src.farfan_pipeline.infrastructure.calibration import (
    CalibrationBounds,
    CalibrationParameter,
    CalibrationLayer,
    CalibrationPhase,
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
        assert len(defaults) == 5

        # Step 2: Verify prohibited operations
        assert is_operation_prohibited("TYPE_A", "weighted_mean")
        assert not is_operation_prohibited("TYPE_A", "semantic_triangulation")

        # Step 3: Create calibration parameters from defaults
        now = datetime.now(timezone.utc)
        
        prior_strength = CalibrationParameter(
            name="prior_strength",
            value=defaults["prior_strength"].default_value,
            bounds=defaults["prior_strength"],
            rationale="Default prior strength for TYPE_A semantic triangulation",
            source_evidence="artifacts/data/epistemic_inputs_v4/epistemic_minima_by_type.json",
            calibration_date=now,
            validity_days=90,
        )

        veto_threshold = CalibrationParameter(
            name="veto_threshold",
            value=defaults["veto_threshold"].default_value,
            bounds=defaults["veto_threshold"],
            rationale="Standard veto threshold for TYPE_A contracts",
            source_evidence="artifacts/data/epistemic_inputs_v4/epistemic_minima_by_type.json",
            calibration_date=now,
            validity_days=90,
        )

        # Note: Using actual method files from the repository for provenance validation
        chunk_size = CalibrationParameter(
            name="chunk_size",
            value=512.0,
            bounds=CalibrationBounds(min_value=128.0, max_value=2048.0, default_value=512.0, unit="tokens"),
            rationale="Semantic chunk size optimized for NLP processing",
            source_evidence="src/farfan_pipeline/methods/semantic_chunking_policy.py",
            calibration_date=now,
            validity_days=90,
        )

        extraction_coverage = CalibrationParameter(
            name="extraction_coverage_target",
            value=0.85,
            bounds=CalibrationBounds(min_value=0.5, max_value=1.0, default_value=0.85, unit="ratio"),
            rationale="Target coverage for semantic extraction methods",
            source_evidence="src/farfan_pipeline/methods/policy_processor.py",
            calibration_date=now,
            validity_days=90,
        )

        # Step 4: Create complete calibration layer
        layer = CalibrationLayer(
            unit_of_analysis_id="MUNI_11001",  # Bogotá
            phase=CalibrationPhase.PHASE_2_COMPUTATION,
            contract_type_code="TYPE_A",
            prior_strength=prior_strength,
            veto_threshold=veto_threshold,
            chunk_size=chunk_size,
            extraction_coverage_target=extraction_coverage,
        )

        # Step 5: Verify layer properties
        assert layer.unit_of_analysis_id == "MUNI_11001"
        assert layer.phase == CalibrationPhase.PHASE_2_COMPUTATION
        assert layer.contract_type_code == "TYPE_A"
        assert layer.schema_version == "1.0.0"

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
        
        IMPORTANT: Per canonical contratos_clasificados.json, TYPE_E CAN use weighted_mean.
        This differs from original spec but follows the authoritative canonical source.
        """
        # TYPE_E: Logical Consistency - most restrictive veto
        defaults = get_type_defaults("TYPE_E")

        # Verify strictest veto threshold
        assert defaults["veto_threshold"].min_value == 0.01
        assert defaults["veto_threshold"].max_value == 0.05

        # Per canonical source, TYPE_E uses: concat, weighted_mean, logical_consistency_validation
        # So weighted_mean is NOT prohibited for TYPE_E
        assert not is_operation_prohibited("TYPE_E", "weighted_mean")
        assert not is_operation_prohibited("TYPE_E", "concat")
        assert not is_operation_prohibited("TYPE_E", "logical_consistency_validation")
        
        # TYPE_E prohibits operations that don't preserve logical consistency
        assert is_operation_prohibited("TYPE_E", "bayesian_update")
        assert is_operation_prohibited("TYPE_E", "semantic_corroboration")

    def test_type_b_bayesian_strong_priors(self) -> None:
        """
        TYPE_B workflow: Bayesian causal inference with stronger priors.
        """
        defaults = get_type_defaults("TYPE_B")

        # TYPE_B should have stronger priors than other types
        assert defaults["prior_strength"].default_value == 2.0

        # Verify N1/N2/N3 ratio expectations
        n1_ratio = defaults["n1_ratio"]
        n2_ratio = defaults["n2_ratio"]
        n3_ratio = defaults["n3_ratio"]

        # Balanced ratios for Bayesian causal inference
        assert n1_ratio.min_value == 0.25
        assert n2_ratio.min_value == 0.30
        assert n3_ratio.min_value == 0.15

    def test_parameter_validity_window_enforcement(self) -> None:
        """
        Verify calibration parameters have validity windows.
        """
        bounds = CalibrationBounds(min_value=0.0, max_value=1.0, default_value=0.5, unit="ratio")
        old_date = datetime(2024, 1, 1, tzinfo=timezone.utc)

        param = CalibrationParameter(
            name="test_param",
            value=0.5,
            bounds=bounds,
            rationale="Test parameter",
            source_evidence="src/farfan_pipeline/methods/test.py",
            calibration_date=old_date,
            validity_days=30,
        )

        # Should be expired by now (Jan 2024 + 30 days << current date)
        now = datetime.now(timezone.utc)
        assert not param.is_valid_at(now)

        # Should be valid at the calibration date
        assert param.is_valid_at(old_date)

    def test_hash_uniqueness_across_different_layers(self) -> None:
        """
        Different calibration layers must produce different hashes.
        """
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

        layer1 = CalibrationLayer(
            unit_of_analysis_id="MUNI_11001",
            phase=CalibrationPhase.INGESTION,
            contract_type_code="TYPE_A",
            prior_strength=param,
            veto_threshold=param,
            chunk_size=param,
            extraction_coverage_target=param,
        )

        layer2 = CalibrationLayer(
            unit_of_analysis_id="MUNI_11002",  # Different municipality
            phase=CalibrationPhase.INGESTION,
            contract_type_code="TYPE_A",
            prior_strength=param,
            veto_threshold=param,
            chunk_size=param,
            extraction_coverage_target=param,
        )

        # Different layers must have different hashes
        assert layer1.manifest_hash() != layer2.manifest_hash()

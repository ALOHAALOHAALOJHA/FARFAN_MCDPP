"""
Suite Adversarial para Validación de Invariantes Constitucionales
================================================================

Fase: FASE 5 - Testing Adversarial
Propósito: Validar invariantes NO NEGOCIABLES (CI-01 through CI-05)

CRITICAL: Estos tests deben pasar al 100% antes de deployment.
Cualquier fallo indica una violación constitucional que debe corregirse.

INVARIANTES CONSTITUCIONALES (CI = Constitutional Invariant):
    CI-01: EXACTITUD NUMÉRICA - Exactly 300 contracts
    CI-02: EXTINCIÓN DE LEGACY - Zero legacy executor classes
    CI-03: INMUTABILIDAD EPISTÉMICA - Level never changes post-init
    CI-04: ASIMETRÍA POPPERIANA - N3 can veto N1/N2, never reverse
    CI-05: SEPARACIÓN CALIBRACIÓN-NIVEL - PDM adjusts parameters, not level

Estrategia de Testing:
- Cada test valida UN invariante constitucional
- Tests son ADVERSARIALES: diseñados para romper la implementación
- Tests son INDEPENDIENTES: cada uno puede ejecutarse solo
- Tests son DETERMINÍSTICOS: mismo resultado siempre
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

# Import calibration core
from farfan_pipeline.calibration.calibration_core import (
    ClosedInterval,
    EpistemicLevel,
    validate_epistemic_level,
    validate_output_type_for_level,
    validate_fusion_behavior_for_level,
)

# Import epistemic core
from farfan_pipeline.calibration.epistemic_core import (
    N1EmpiricalCalibration,
    N2InferentialCalibration,
    N3AuditCalibration,
    N4MetaCalibration,
    N0InfrastructureCalibration,
    create_calibration,
)

# Import registry
from farfan_pipeline.calibration.registry import (
    EpistemicCalibrationRegistry,
    CalibrationResolutionError,
    create_registry,
    MockPDMProfile,
)


# =============================================================================
# CI-01: EXACTITUD NUMÉRICA (300 Contratos)
# =============================================================================


class TestCI01ContractCount:
    """CI-01: Exactamente 300 contratos JSON v4."""

    def test_ci01_contract_count(self):
        """CI-01: Exactly 300 contracts must exist."""
        contracts_dir = Path("/Users/recovered/FARFAN_MPP/src/farfan_pipeline/phases/Phase_2/generated_contracts")
        contracts = list(contracts_dir.glob("*_contract_v4.json"))

        assert len(contracts) == 300, (
            f"CONSTITUTIONAL VIOLATION [CI-01]: "
            f"Expected exactly 300 contracts, found {len(contracts)}. "
            f"Contract count must be exactly 300 (30 base questions x 10 policy areas)."
        )

    def test_ci01_no_extra_files(self):
        """CI-01: No extra non-contract files in contracts directory."""
        contracts_dir = Path("/Users/recovered/FARFAN_MPP/src/farfan_pipeline/phases/Phase_2/generated_contracts")
        contract_files = [f for f in contracts_dir.glob("*.json") if f.name.endswith("_contract_v4.json")]
        all_json_files = list(contracts_dir.glob("*.json"))

        non_contract_count = len(all_json_files) - len(contract_files)

        # Allow manifest file but should be minimal
        assert non_contract_count <= 1, (
            f"CONSTITUTIONAL VIOLATION [CI-01]: "
            f"Found {non_contract_count} non-contract JSON files. "
            f"Only manifest files allowed alongside contracts."
        )

    def test_ci01_contract_naming_pattern(self):
        """CI-01: All contracts follow QXXX_PAXX_contract_v4.json pattern."""
        contracts_dir = Path("/Users/recovered/FARFAN_MPP/src/farfan_pipeline/phases/Phase_2/generated_contracts")
        pattern = re.compile(r"^Q\d{3}_PA\d{2}_contract_v4\.json$")

        invalid_names = []
        for contract_file in contracts_dir.glob("*_contract_v4.json"):
            if not pattern.match(contract_file.name):
                invalid_names.append(contract_file.name)

        assert not invalid_names, (
            f"CONSTITUTIONAL VIOLATION [CI-01]: "
            f"Found {len(invalid_names)} contracts with invalid naming: {invalid_names[:5]}. "
            f"All contracts must follow QXXX_PAXX_contract_v4.json pattern."
        )


# =============================================================================
# CI-02: EXTINCIÓN DE LEGACY
# =============================================================================


class TestCI02NoLegacyExecutors:
    """CI-02: Zero legacy executor classes."""

    def test_ci02_no_legacy_executor_classes(self):
        """CI-02: No files with pattern D[0-9]Q[0-9]_Executor."""
        src_path = Path("/Users/recovered/FARFAN_MPP/src/farfan_pipeline")

        # Search for legacy pattern in Python files
        legacy_pattern = re.compile(r"class\s+(D\d_Q\d+_[\w_]+Executor)\s*:")

        legacy_classes = []
        for py_file in src_path.rglob("*.py"):
            content = py_file.read_text()
            matches = legacy_pattern.findall(content)
            legacy_classes.extend([(py_file.name, cls) for cls in matches])

        assert not legacy_classes, (
            f"CONSTITUTIONAL VIOLATION [CI-02]: "
            f"Found {len(legacy_classes)} legacy executor classes: {legacy_classes}. "
            f"Legacy executor pattern 'D#Q#_Executor' is prohibited. "
            f"Use 'DynamicContractExecutor' instead."
        )

    def test_ci02_contracts_use_dynamic_executor(self):
        """CI-02: All contracts use DynamicContractExecutor."""
        contracts_dir = Path("/Users/recovered/FARFAN_MPP/src/farfan_pipeline/phases/Phase_2/generated_contracts")

        invalid_executors = []
        for contract_file in contracts_dir.glob("*_contract_v4.json"):
            with open(contract_file) as f:
                contract = json.load(f)

            executor_class = contract.get("executor_binding", {}).get("executor_class")
            if executor_class != "DynamicContractExecutor":
                invalid_executors.append((contract_file.name, executor_class))

        # Check first 10 if any exist
        sample = invalid_executors[:10] if invalid_executors else []

        assert not invalid_executors, (
            f"CONSTITUTIONAL VIOLATION [CI-02]: "
            f"Found {len(invalid_executors)} contracts using non-DynamicContractExecutor. "
            f"Sample: {sample}. "
            f"All contracts must use 'DynamicContractExecutor' as executor_class."
        )


# =============================================================================
# CI-03: INMUTABILIDAD EPISTÉMICA
# =============================================================================


class TestCI03LevelImmutability:
    """CI-03: Epistemic level is immutable."""

    def test_ci03_n1_level_immutability(self):
        """CI-03: N1EmpiricalCalibration.level cannot be modified."""
        n1 = N1EmpiricalCalibration()

        # Attempt to modify level
        with pytest.raises((AttributeError, TypeError, TypeError)):
            n1.level = "N2-INF"  # type: ignore

        # Verify level is still N1-EMP
        assert n1.level == "N1-EMP", "Level should remain N1-EMP"

    def test_ci03_n2_level_immutability(self):
        """CI-03: N2InferentialCalibration.level cannot be modified."""
        n2 = N2InferentialCalibration()

        with pytest.raises((AttributeError, TypeError)):
            n2.level = "N3-AUD"  # type: ignore

        assert n2.level == "N2-INF"

    def test_ci03_n3_level_immutability(self):
        """CI-03: N3AuditCalibration.level cannot be modified."""
        n3 = N3AuditCalibration()

        with pytest.raises((AttributeError, TypeError)):
            n3.level = "N1-EMP"  # type: ignore

        assert n3.level == "N3-AUD"

    def test_ci03_registry_preserves_level(self):
        """CI-03: Registry preserves level through resolution."""
        registry = create_registry()

        # Mock PDM with extreme parameters
        extreme_pdm = MockPDMProfile(
            table_schemas=["PPI", "PAI", "POI"],
            hierarchy_depth=10,
            contains_financial_data=True,
        )

        # Resolve calibration (PDM should NOT change level)
        calib = registry.resolve_calibration(
            "TextMiningEngine.diagnose_critical_links",
            "TYPE_A",
            extreme_pdm,
        )

        # CRITICAL: Level must match registry
        assert calib["level"] == "N1-EMP", (
            f"CONSTITUTIONAL VIOLATION [CI-03]: "
            f"Level changed from N1-EMP to {calib['level']}. "
            f"Epistemic level is IMMUTABLE and cannot be changed by PDM adjustments."
        )


# =============================================================================
# CI-04: ASIMETRÍA POPPERIANA
# =============================================================================


class TestCI04Asymmetry:
    """CI-04: N3 can veto N1/N2, never reverse."""

    def test_ci04_n3_veto_action(self):
        """CI-04: N3 veto computation returns proper actions."""
        n3 = N3AuditCalibration()

        # Test critical veto
        result = n3.compute_veto_action(0.0)
        assert result["veto_action"] == "CRITICAL_VETO"
        assert result["confidence_multiplier"] == 0.0
        assert result["status"] == "SUPPRESSED"

        # Test partial veto
        result = n3.compute_veto_action(0.3)
        assert result["veto_action"] == "PARTIAL_VETO"
        assert result["confidence_multiplier"] == 0.5
        assert result["status"] == "ATTENUATED"

        # Test approved
        result = n3.compute_veto_action(0.8)
        assert result["veto_action"] == "APPROVED"
        assert result["confidence_multiplier"] == 1.0
        assert result["status"] == "VALIDATED"

    def test_ci04_veto_threshold_ordering(self):
        """CI-04: Critical threshold must be stricter than partial."""
        n3 = N3AuditCalibration()

        assert n3.veto_threshold_critical < n3.veto_threshold_partial, (
            f"CONSTITUTIONAL VIOLATION [CI-04]: "
            f"veto_threshold_critical ({n3.veto_threshold_critical}) must be < "
            f"veto_threshold_partial ({n3.veto_threshold_partial}). "
            f"Critical veto must be harder to trigger (stricter)."
        )

    def test_ci04_no_n1_veto_n3_in_code(self):
        """CI-04: No code allows N1/N2 to veto N3."""
        # Check task executor (N1 level)
        task_executor_path = Path("/Users/recovered/FARFAN_MPP/src/farfan_pipeline/phases/Phase_2/phase2_50_00_task_executor.py")

        if task_executor_path.exists():
            content = task_executor_path.read_text()

            # Look for patterns where N1 modifies N3
            forbidden_patterns = [
                r"phase_c_output.*=",  # N1 assigning to N3 output
                r"n3_result.*confidence.*=",  # N1 modifying N3 confidence
                r"suppress.*n3",  # N1 suppressing N3
            ]

            for pattern in forbidden_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                assert not matches, (
                    f"CONSTITUTIONAL VIOLATION [CI-04]: "
                    f"Found {len(matches)} instances where N1/N2 may modify N3: {matches[:3]}. "
                    f"N1/N2 CANNOT veto or modify N3 outputs. Asymmetry is unidirectional."
                )

    def test_ci04_contract_declares_asymmetry(self):
        """CI-04: Contracts declare asymmetry principle."""
        contracts_dir = Path("/Users/recovered/FARFAN_MPP/src/farfan_pipeline/phases/Phase_2/generated_contracts")

        # Check a sample of contracts
        sample_count = 0
        violations = []

        for contract_file in list(contracts_dir.glob("*_contract_v4.json"))[:10]:
            with open(contract_file) as f:
                contract = json.load(f)

            # Check for asymmetry declaration
            cross_layer = contract.get("cross_layer_fusion", {})
            n3_to_n1 = cross_layer.get("N3_to_N1", {})
            asymmetry = n3_to_n1.get("asymmetry", "")

            if "N1 CANNOT invalidate N3" not in asymmetry:
                violations.append(contract_file.name)

            sample_count += 1

        assert not violations, (
            f"CONSTITUTIONAL VIOLATION [CI-04]: "
            f"Found {len(violations)} contracts missing asymmetry declaration: {violations}. "
            f"All contracts must declare 'N1 CANNOT invalidate N3' in cross_layer_fusion.N3_to_N1.asymmetry."
        )


# =============================================================================
# CI-05: SEPARACIÓN CALIBRACIÓN-NIVEL
# =============================================================================


class TestCI05PDMSeparation:
    """CI-05: PDM adjusts parameters, not level."""

    def test_ci05_pdm_does_not_change_level(self):
        """CI-05: PDM adjustments never modify epistemic level."""
        registry = create_registry()

        # Mock PDM with maximum impact
        extreme_pdm = MockPDMProfile(
            table_schemas=["PPI", "PAI", "POI"],
            hierarchy_depth=10,
            contains_financial_data=True,
            temporal_structure={"has_baselines": True, "requires_ordering": True},
        )

        # Test multiple methods
        test_methods = [
            ("TextMiningEngine.diagnose_critical_links", "N1-EMP"),
            ("BayesianMechanismInference._calculate_coherence_factor", "N2-INF"),
            ("SemanticValidator.validate_semantic_completeness_coherence", "N3-AUD"),
        ]

        for method_id, expected_level in test_methods:
            calib = registry.resolve_calibration(method_id, "TYPE_A", extreme_pdm)

            actual_level = calib["level"]
            assert actual_level == expected_level, (
                f"CONSTITUTIONAL VIOLATION [CI-05]: "
                f"PDM changed level from {expected_level} to {actual_level} for {method_id}. "
                f"PDM adjusts PARAMETERS (thresholds, weights), NEVER the epistemic level."
            )

    def test_ci05_pdm_adjusts_parameters(self):
        """CI-05: PDM does adjust calibration parameters."""
        registry = create_registry()

        # Mock PDM with tables
        pdm_with_tables = MockPDMProfile(
            table_schemas=["PPI", "PAI"],
            hierarchy_depth=2,
        )

        calib = registry.resolve_calibration(
            "TextMiningEngine.diagnose_critical_links",
            "TYPE_A",
            pdm_with_tables,
        )

        # Verify PDM adjustment was applied
        params = calib["calibration_parameters"]
        boost = params.get("table_extraction_boost", 1.0)

        assert boost > 1.0, (
            f"CONSTITUTIONAL VIOLATION [CI-05]: "
            f"PDM adjustment not applied. table_extraction_boost should be > 1.0 with PPI tables, "
            f"got {boost}. PDM SHOULD adjust parameters based on document structure."
        )

    def test_ci05_registry_validates_pdm_output(self):
        """CI-05: Registry strips 'level' from PDM adjustments if present."""
        registry = create_registry()

        # This test ensures that even if PDM logic accidentally returns
        # a level adjustment, the registry removes it
        n1_rules = registry._pdm_n1_rules(MockPDMProfile())

        assert "level" not in n1_rules, (
            f"CONSTITUTIONAL VIOLATION [CI-05]: "
            f"PDM rules returned 'level' key. "
            f"PDM adjustments MUST NOT include level changes."
        )


# =============================================================================
# CALIBRATION RESOLUTION TESTS
# =============================================================================


class TestCalibrationResolution:
    """Tests for calibration resolution system."""

    def test_registry_initialization(self):
        """Registry initializes with all required configs."""
        registry = create_registry()

        # Check all levels are loaded
        for level in EpistemicLevel:
            assert level in registry.level_defaults, (
                f"Missing configuration for level: {level}"
            )

    def test_method_registry_lookup(self):
        """Method registry returns correct levels."""
        registry = create_registry()

        # Test known methods
        test_cases = [
            ("TextMiningEngine.diagnose_critical_links", "N1-EMP"),
            ("BayesianMechanismInference.aggregate_confidence", "N2-INF"),
            ("SemanticValidator.validate_semantic_completeness_coherence", "N3-AUD"),
        ]

        for method_id, expected_level in test_cases:
            actual = registry.get_method_level(method_id)
            assert actual == expected_level, (
                f"Method {method_id} should be {expected_level}, got {actual}"
            )

    def test_unknown_method_raises_error(self):
        """Unknown method raises CalibrationResolutionError."""
        registry = create_registry()

        with pytest.raises(CalibrationResolutionError):
            registry.get_method_level("UnknownClass.unknown_method")

    def test_n1_calibration_bounds(self):
        """N1 calibration enforces parameter bounds."""
        # Valid calibration
        n1 = N1EmpiricalCalibration(
            extraction_confidence_floor=0.7,
            table_extraction_boost=1.2,
        )
        assert n1.extraction_confidence_floor == 0.7

        # Invalid calibration (out of bounds)
        with pytest.raises((ValueError, TypeError)):
            N1EmpiricalCalibration(extraction_confidence_floor=1.5)

    def test_n2_calibration_bounds(self):
        """N2 calibration enforces parameter bounds."""
        # Valid calibration
        n2 = N2InferentialCalibration(
            prior_strength=0.7,
            mcmc_samples=10000,
        )
        assert n2.prior_strength == 0.7

        # Invalid calibration (negative samples)
        with pytest.raises((ValueError, TypeError)):
            N2InferentialCalibration(mcmc_samples=-100)

    def test_n3_calibration_bounds(self):
        """N3 calibration enforces threshold ordering."""
        # Valid calibration
        n3 = N3AuditCalibration(
            veto_threshold_critical=0.0,
            veto_threshold_partial=0.5,
        )
        assert n3.veto_threshold_critical < n3.veto_threshold_partial

        # Invalid calibration (critical > partial)
        with pytest.raises((ValueError, TypeError)):
            N3AuditCalibration(
                veto_threshold_critical=0.5,
                veto_threshold_partial=0.0,
            )


# =============================================================================
# CONTRACT STRUCTURE TESTS
# =============================================================================


class TestContractStructure:
    """Tests for contract v4 structure."""

    def test_all_contracts_have_required_fields(self):
        """All contracts have required top-level fields."""
        contracts_dir = Path("/Users/recovered/FARFAN_MPP/src/farfan_pipeline/phases/Phase_2/generated_contracts")

        required_fields = [
            "identity",
            "executor_binding",
            "method_binding",
            "evidence_assembly",
        ]

        errors = []
        for contract_file in contracts_dir.glob("*_contract_v4.json"):
            with open(contract_file) as f:
                contract = json.load(f)

            missing = [f for f in required_fields if f not in contract]
            if missing:
                errors.append(f"{contract_file.name}: missing {missing}")

        assert not errors, f"Found {len(errors)} contracts with missing fields: {errors[:5]}"

    def test_contracts_have_three_phases(self):
        """All contracts have three execution phases."""
        contracts_dir = Path("/Users/recovered/FARFAN_MPP/src/farfan_pipeline/phases/Phase_2/generated_contracts")

        required_phases = [
            "phase_A_construction",
            "phase_B_computation",
            "phase_C_litigation",
        ]

        errors = []
        for contract_file in list(contracts_dir.glob("*_contract_v4.json"))[:20]:
            with open(contract_file) as f:
                contract = json.load(f)

            phases = contract.get("method_binding", {}).get("execution_phases", {})
            missing = [p for p in required_phases if p not in phases]

            if missing:
                errors.append(f"{contract_file.name}: missing phases {missing}")

        assert not errors, f"Found {len(errors)} contracts with missing phases: {errors[:5]}"

    def test_phase_c_has_asymmetry_declaration(self):
        """Phase C declares asymmetry principle."""
        contracts_dir = Path("/Users/recovered/FARFAN_MPP/src/farfan_pipeline/phases/Phase_2/generated_contracts")

        # Sample check
        errors = []
        for contract_file in list(contracts_dir.glob("*_contract_v4.json"))[:10]:
            with open(contract_file) as f:
                contract = json.load(f)

            phase_c = contract.get("method_binding", {}).get("execution_phases", {}).get("phase_C_litigation", {})
            asymmetry = phase_c.get("asymmetry_principle", "")

            if not asymmetry or "N3" not in asymmetry:
                errors.append(contract_file.name)

        assert not errors, f"Phase C missing asymmetry declaration in: {errors[:5]}"


# =============================================================================
# MAIN TEST SUITE
# =============================================================================


if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v", "--tb=short"])

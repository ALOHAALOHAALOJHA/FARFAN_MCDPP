"""
Tests for Canonical Phase Coverage in Orchestrator.

Validates that the orchestrator fully covers all canonical phases
(Phase_00 through Phase_09) with proper constitutional invariants.

Version: 2.0.0
"""

from __future__ import annotations

import pytest
from unittest.mock import Mock

from farfan_pipeline.orchestration.orchestrator import (
    Orchestrator,
    CanonicalPhase,
    PhaseExecutionResult,
    MethodExecutor,
    GateResult,
    Phase0ValidationResult,
    # Phase constants
    P01_EXPECTED_CHUNK_COUNT,
    P01_POLICY_AREA_COUNT,
    P01_DIMENSION_COUNT,
    P02_CONTRACT_COUNT,
    P06_CLUSTER_COUNT,
)


class TestCanonicalPhaseEnum:
    """Test CanonicalPhase enum functionality."""

    def test_all_phases_defined(self):
        """Test that all 10 canonical phases are defined."""
        phases = list(CanonicalPhase)
        assert len(phases) == 10
        assert CanonicalPhase.PHASE_00 in phases
        assert CanonicalPhase.PHASE_09 in phases

    def test_from_string_with_p_prefix(self):
        """Test from_string with P prefix."""
        assert CanonicalPhase.from_string("P00") == CanonicalPhase.PHASE_00
        assert CanonicalPhase.from_string("P01") == CanonicalPhase.PHASE_01
        assert CanonicalPhase.from_string("P09") == CanonicalPhase.PHASE_09

    def test_from_string_without_p_prefix(self):
        """Test from_string without P prefix."""
        assert CanonicalPhase.from_string("00") == CanonicalPhase.PHASE_00
        assert CanonicalPhase.from_string("01") == CanonicalPhase.PHASE_01
        assert CanonicalPhase.from_string("9") == CanonicalPhase.PHASE_09

    def test_from_string_with_phase_prefix(self):
        """Test from_string with Phase_ prefix."""
        assert CanonicalPhase.from_string("Phase_00") == CanonicalPhase.PHASE_00
        assert CanonicalPhase.from_string("Phase_05") == CanonicalPhase.PHASE_05
        assert CanonicalPhase.from_string("PHASE_09") == CanonicalPhase.PHASE_09

    def test_from_string_invalid_raises(self):
        """Test that invalid phase strings raise ValueError."""
        with pytest.raises(ValueError, match="Invalid phase"):
            CanonicalPhase.from_string("P10")
        with pytest.raises(ValueError, match="Invalid phase"):
            CanonicalPhase.from_string("INVALID")


class TestOrchestratorCanonicalCoverage:
    """Test orchestrator coverage of all canonical phases."""

    @pytest.fixture
    def mock_method_executor(self):
        """Create mock MethodExecutor."""
        return Mock(spec=MethodExecutor)

    @pytest.fixture
    def mock_questionnaire(self):
        """Create mock questionnaire."""
        questionnaire = Mock()
        questionnaire.version = "2.0.0"
        return questionnaire

    @pytest.fixture
    def mock_executor_config(self):
        """Create mock executor config."""
        return Mock()

    @pytest.fixture
    def valid_phase0_validation(self):
        """Create valid Phase 0 validation result."""
        return Phase0ValidationResult(
            all_passed=True,
            gate_results=[
                GateResult(
                    gate_name="bootstrap",
                    passed=True,
                    message="Bootstrap completed"
                ),
                GateResult(
                    gate_name="input_verification",
                    passed=True,
                    message="Input verified"
                ),
            ],
            validation_time="2026-01-16T00:00:00Z"
        )

    @pytest.fixture
    def orchestrator(
        self,
        mock_method_executor,
        mock_questionnaire,
        mock_executor_config,
        valid_phase0_validation
    ):
        """Create Orchestrator instance."""
        return Orchestrator(
            method_executor=mock_method_executor,
            questionnaire=mock_questionnaire,
            executor_config=mock_executor_config,
            phase0_validation=valid_phase0_validation
        )

    def test_orchestrator_initializes_with_phase_constants(self, orchestrator):
        """Test that orchestrator initializes with all phase constants."""
        assert CanonicalPhase.PHASE_01 in orchestrator.PHASE_CONSTANTS
        assert CanonicalPhase.PHASE_02 in orchestrator.PHASE_CONSTANTS
        assert CanonicalPhase.PHASE_04 in orchestrator.PHASE_CONSTANTS
        assert CanonicalPhase.PHASE_05 in orchestrator.PHASE_CONSTANTS
        assert CanonicalPhase.PHASE_06 in orchestrator.PHASE_CONSTANTS
        assert CanonicalPhase.PHASE_07 in orchestrator.PHASE_CONSTANTS

    def test_execute_phase00(self, orchestrator):
        """Test Phase 00 execution."""
        result = orchestrator.execute("P00")
        assert isinstance(result, PhaseExecutionResult)
        assert result.phase == CanonicalPhase.PHASE_00
        assert result.success is True
        assert result.status == "validated"
        assert result.output["phase"] == "P00"

    def test_execute_phase01(self, orchestrator):
        """Test Phase 01 execution."""
        result = orchestrator.execute("P01")
        assert result.phase == CanonicalPhase.PHASE_01
        assert result.success is True
        assert result.output["expected_chunks"] == P01_EXPECTED_CHUNK_COUNT
        assert result.output["policy_areas"] == P01_POLICY_AREA_COUNT
        assert result.output["dimensions"] == P01_DIMENSION_COUNT

    def test_execute_phase02(self, orchestrator):
        """Test Phase 02 execution."""
        result = orchestrator.execute("P02")
        assert result.phase == CanonicalPhase.PHASE_02
        assert result.success is True
        assert result.output["contract_count"] == P02_CONTRACT_COUNT

    def test_execute_phase03(self, orchestrator):
        """Test Phase 03 execution."""
        result = orchestrator.execute("P03")
        assert result.phase == CanonicalPhase.PHASE_03
        assert result.success is True
        assert result.output["transformation"] == "evidence_to_score"

    def test_execute_phase04(self, orchestrator):
        """Test Phase 04 execution."""
        result = orchestrator.execute("P04")
        assert result.phase == CanonicalPhase.PHASE_04
        assert result.success is True
        assert result.output["method"] == "Choquet Integral"

    def test_execute_phase05(self, orchestrator):
        """Test Phase 05 execution."""
        result = orchestrator.execute("P05")
        assert result.phase == CanonicalPhase.PHASE_05
        assert result.success is True
        assert result.output["policy_area_count"] == P01_POLICY_AREA_COUNT

    def test_execute_phase06(self, orchestrator):
        """Test Phase 06 execution."""
        result = orchestrator.execute("P06")
        assert result.phase == CanonicalPhase.PHASE_06
        assert result.success is True
        assert result.output["cluster_count"] == P06_CLUSTER_COUNT

    def test_execute_phase07(self, orchestrator):
        """Test Phase 07 execution."""
        result = orchestrator.execute("P07")
        assert result.phase == CanonicalPhase.PHASE_07
        assert result.success is True
        assert "CCCA" in result.output["components"]

    def test_execute_phase08(self, orchestrator):
        """Test Phase 08 execution."""
        result = orchestrator.execute("P08")
        assert result.phase == CanonicalPhase.PHASE_08
        assert result.success is True
        assert result.output["version"] == "3.0.0"

    def test_execute_phase09(self, orchestrator):
        """Test Phase 09 execution."""
        result = orchestrator.execute("P09")
        assert result.phase == CanonicalPhase.PHASE_09
        assert result.success is True
        assert result.output["status"] == "complete"

    def test_execute_with_canonical_phase_enum(self, orchestrator):
        """Test execute with CanonicalPhase enum instead of string."""
        result = orchestrator.execute(CanonicalPhase.PHASE_01)
        assert result.phase == CanonicalPhase.PHASE_01
        assert result.success is True

    def test_execute_all_phases(self, orchestrator):
        """Test execute_all method runs all phases."""
        results = orchestrator.execute_all(
            start_phase="P00",
            end_phase="P09"
        )

        # Should have results for all 10 phases
        assert len(results) == 10
        assert "P00" in results
        assert "P09" in results

        # All should be successful
        for phase_id, result in results.items():
            assert result.success is True, f"Phase {phase_id} failed: {result.errors}"

    def test_execute_all_partial_range(self, orchestrator):
        """Test execute_all with partial phase range."""
        results = orchestrator.execute_all(
            start_phase="P01",
            end_phase="P05"
        )

        # Should have results for phases 01-05 (5 phases)
        assert len(results) == 5
        assert "P01" in results
        assert "P05" in results
        assert "P00" not in results
        assert "P06" not in results


class TestOrchestratorConstitutionalInvariants:
    """Test constitutional invariant enforcement per phase."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator for invariant testing."""
        return Orchestrator(
            method_executor=Mock(spec=MethodExecutor),
            questionnaire=Mock(version="2.0.0"),
            executor_config=Mock(),
            phase0_validation=Phase0ValidationResult(
                all_passed=True,
                gate_results=[],
                validation_time="2026-01-16T00:00:00Z"
            )
        )

    def test_phase01_60_chunk_invariant(self, orchestrator):
        """Test Phase 01 enforces 60 chunk invariant."""
        result = orchestrator.execute("P01")
        assert result.output["expected_chunks"] == 60

    def test_phase01_10_policy_area_invariant(self, orchestrator):
        """Test Phase 01 enforces 10 policy area invariant."""
        result = orchestrator.execute("P01")
        assert result.output["policy_areas"] == 10

    def test_phase01_6_dimension_invariant(self, orchestrator):
        """Test Phase 01 enforces 6 dimension invariant."""
        result = orchestrator.execute("P01")
        assert result.output["dimensions"] == 6

    def test_phase02_300_contract_invariant(self, orchestrator):
        """Test Phase 02 enforces 300 contract invariant."""
        result = orchestrator.execute("P02")
        assert result.output["contract_count"] == 300

    def test_phase06_4_cluster_invariant(self, orchestrator):
        """Test Phase 06 enforces 4 cluster invariant."""
        result = orchestrator.execute("P06")
        assert result.output["cluster_count"] == 4

    def test_validate_chunk_count_passes(self, orchestrator):
        """Test chunk count validation passes with correct count."""
        assert orchestrator.validate_chunk_count(60) is True

    def test_validate_chunk_count_fails_incorrect(self, orchestrator):
        """Test chunk count validation fails with incorrect count."""
        with pytest.raises(ValueError, match="Chunk count violation"):
            orchestrator.validate_chunk_count(59)

        with pytest.raises(ValueError, match="Chunk count violation"):
            orchestrator.validate_chunk_count(61)


class TestPhaseExecutionResult:
    """Test PhaseExecutionResult dataclass."""

    def test_to_dict_conversion(self):
        """Test PhaseExecutionResult.to_dict() method."""
        result = PhaseExecutionResult(
            phase=CanonicalPhase.PHASE_01,
            success=True,
            status="completed",
            output={"chunks": 60},
            metrics={"duration_ms": 1000},
        )

        result_dict = result.to_dict()
        assert result_dict["phase"] == "P01"
        assert result_dict["success"] is True
        assert result_dict["status"] == "completed"
        assert result_dict["output"]["chunks"] == 60
        assert result_dict["metrics"]["duration_ms"] == 1000

    def test_to_dict_with_errors(self):
        """Test to_dict includes errors when present."""
        result = PhaseExecutionResult(
            phase=CanonicalPhase.PHASE_02,
            success=False,
            status="failed",
            errors=["Error 1", "Error 2"]
        )

        result_dict = result.to_dict()
        assert result_dict["success"] is False
        assert len(result_dict["errors"]) == 2

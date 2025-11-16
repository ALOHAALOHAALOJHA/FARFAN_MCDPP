"""End-to-end integration tests for Policy Orchestration System.

Tests the complete flow:
    Smart Chunks (10/PA) → Signals (PA-specific) → Orchestrator → Executors
"""

import pytest
import json
from pathlib import Path

from saaaaaa.core.orchestrator.policy_orchestrator import (
    PolicyOrchestrator,
    PolicyAreaProcessingResult,
    PolicyOrchestrationError,
)
from saaaaaa.core.orchestrator.signals import SignalRegistry, SignalPack


class TestPolicyOrchestrationE2E:
    """End-to-end tests for policy orchestration system."""

    @pytest.fixture
    def signal_registry(self):
        """Create signal registry with test signals."""
        registry = SignalRegistry(max_size=20, default_ttl_s=3600)

        # Add test signal for PA01
        signal_pack = SignalPack(
            version="1.0.0",
            policy_area="PA01",
            patterns=["género", "mujeres", "equidad"],
            regex=["\\bmujeres?\\b", "\\bgénero\\b"],
            verbs=["garantizar", "promover"],
            entities=["Ministerio de la Mujer"],
            thresholds={"min_confidence": 0.75}
        )
        registry.put("PA01", signal_pack)

        return registry

    @pytest.fixture
    def orchestrator(self, signal_registry):
        """Create PolicyOrchestrator instance."""
        return PolicyOrchestrator(signal_registry=signal_registry)

    def test_orchestrator_initialization(self, orchestrator):
        """Test that orchestrator initializes correctly."""
        assert orchestrator is not None
        assert orchestrator.signal_registry is not None
        assert orchestrator.chunk_router is not None
        assert len(orchestrator.executors) == 30  # All 30 executors

    def test_signal_pack_loading(self):
        """Test loading signal packs from config directory."""
        signals_dir = Path("config/policy_signals")

        if signals_dir.exists():
            registry = SignalRegistry()

            # Load PA01 signal
            signal_file = signals_dir / "PA01.json"
            if signal_file.exists():
                with open(signal_file) as f:
                    signal_data = json.load(f)

                signal_pack = SignalPack(**signal_data)
                registry.put("PA01", signal_pack)

                # Validate
                loaded_signal = registry.get("PA01")
                assert loaded_signal is not None
                assert loaded_signal.policy_area == "PA01"
                assert len(loaded_signal.patterns) > 0
                assert len(loaded_signal.regex) > 0

    def test_process_policy_area_with_10_chunks(self, orchestrator):
        """Test processing exactly 10 chunks for a policy area."""
        # Generate 10 mock chunks for PA01
        mock_chunks = []
        for i in range(10):
            mock_chunks.append({
                'id': f"PA01_chunk_{i+1}",
                'text': f"Mock chunk {i+1} for gender equality policy.",
                'policy_area': 'PA01',
                'chunk_index': i,
                'chunk_type': 'diagnostic',
                'metadata': {'test': True}
            })

        # Process with orchestrator
        result = orchestrator.process_policy_area(
            chunks=mock_chunks,
            policy_area="PA01"
        )

        # Validate result
        assert isinstance(result, PolicyAreaProcessingResult)
        assert result.policy_area == "PA01"
        assert result.chunks_processed == 10
        assert result.signals_version == "1.0.0"
        assert result.validation_passed is True

    def test_process_policy_area_wrong_chunk_count(self, orchestrator):
        """Test that orchestrator rejects incorrect chunk count."""
        # Generate only 5 chunks (should require 10)
        mock_chunks = []
        for i in range(5):
            mock_chunks.append({
                'id': f"PA01_chunk_{i+1}",
                'text': f"Mock chunk {i+1}",
                'policy_area': 'PA01',
                'chunk_index': i,
                'chunk_type': 'diagnostic',
            })

        # Should raise error
        with pytest.raises(PolicyOrchestrationError) as exc_info:
            orchestrator.process_policy_area(
                chunks=mock_chunks,
                policy_area="PA01"
            )

        assert "Expected exactly 10 chunks" in str(exc_info.value)

    def test_invalid_policy_area(self, orchestrator):
        """Test that invalid policy area is rejected."""
        mock_chunks = [{'id': f'chunk_{i}'} for i in range(10)]

        with pytest.raises(PolicyOrchestrationError) as exc_info:
            orchestrator.process_policy_area(
                chunks=mock_chunks,
                policy_area="INVALID"
            )

        assert "Invalid policy area" in str(exc_info.value)

    def test_canonical_policy_areas(self, orchestrator):
        """Test that all 10 canonical policy areas are recognized."""
        expected_areas = [
            "PA01", "PA02", "PA03", "PA04", "PA05",
            "PA06", "PA07", "PA08", "PA09", "PA10"
        ]

        assert orchestrator.CANONICAL_POLICY_AREAS == expected_areas

    def test_statistics_tracking(self, orchestrator):
        """Test that orchestrator tracks processing statistics."""
        # Generate and process mock chunks
        mock_chunks = [
            {'id': f"PA01_chunk_{i+1}", 'text': 'test', 'chunk_type': 'diagnostic'}
            for i in range(10)
        ]

        orchestrator.process_policy_area(
            chunks=mock_chunks,
            policy_area="PA01"
        )

        # Check statistics
        stats = orchestrator.get_statistics()
        assert stats['policy_areas_processed'] == 1
        assert stats['total_chunks_processed'] == 10
        assert 'PA01' in stats['signals_used']


class TestSignalPackValidation:
    """Tests for SignalPack validation."""

    def test_signal_pack_creation(self):
        """Test creating a valid signal pack."""
        signal_pack = SignalPack(
            version="1.0.0",
            policy_area="PA01",
            patterns=["test"],
            regex=["\\btest\\b"],
            verbs=["test"],
            entities=["Test Entity"],
            thresholds={"min_confidence": 0.75}
        )

        assert signal_pack.version == "1.0.0"
        assert signal_pack.policy_area == "PA01"
        assert signal_pack.is_valid()

    def test_signal_pack_invalid_version(self):
        """Test that invalid version format is rejected."""
        with pytest.raises(ValueError) as exc_info:
            SignalPack(
                version="invalid",
                policy_area="PA01",
                patterns=[],
                regex=[],
                verbs=[],
                entities=[],
                thresholds={}
            )

        assert "Version must be in format 'X.Y.Z'" in str(exc_info.value)

    def test_signal_pack_invalid_threshold(self):
        """Test that invalid threshold values are rejected."""
        with pytest.raises(ValueError) as exc_info:
            SignalPack(
                version="1.0.0",
                policy_area="PA01",
                patterns=[],
                regex=[],
                verbs=[],
                entities=[],
                thresholds={"invalid": 2.0}  # Out of range [0.0, 1.0]
            )

        assert "must be in range [0.0, 1.0]" in str(exc_info.value)


class TestChunkCalibration:
    """Tests for chunk calibration (10 chunks per PA)."""

    @pytest.mark.skipif(
        not Path("scripts/smart_policy_chunks_canonic_phase_one.py").exists(),
        reason="smart_policy_chunks script not found"
    )
    def test_chunk_calibrator_exists(self):
        """Test that PolicyAreaChunkCalibrator class exists."""
        from scripts.smart_policy_chunks_canonic_phase_one import PolicyAreaChunkCalibrator
        assert PolicyAreaChunkCalibrator is not None
        assert PolicyAreaChunkCalibrator.TARGET_CHUNKS_PER_PA == 10

    @pytest.mark.skipif(
        not Path("scripts/smart_policy_chunks_canonic_phase_one.py").exists(),
        reason="smart_policy_chunks script not found"
    )
    def test_calibrator_canonical_policy_areas(self):
        """Test that calibrator uses canonical policy areas."""
        from scripts.smart_policy_chunks_canonic_phase_one import PolicyAreaChunkCalibrator

        expected_areas = [
            "PA01", "PA02", "PA03", "PA04", "PA05",
            "PA06", "PA07", "PA08", "PA09", "PA10"
        ]

        assert PolicyAreaChunkCalibrator.POLICY_AREAS == expected_areas

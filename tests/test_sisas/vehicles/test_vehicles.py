# tests/test_sisas/vehicles/test_vehicles.py

import pytest
from datetime import datetime
from uuid import uuid4

from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.signal import (
    SignalContext, SignalSource
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vehicles.signal_registry import SignalRegistryVehicle
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vehicles.signal_context_scoper import SignalContextScoperVehicle

@pytest.fixture
def sample_context():
    return SignalContext(
        node_type="question",
        node_id="Q147",
        phase="phase_00",
        consumer_scope="Phase_00"
    )

class TestSignalRegistryVehicle:
    def test_process(self, sample_context):
        vehicle = SignalRegistryVehicle()
        data = {
            "questions": [{"id": "Q1", "text": "What?"}],
            "version": "1.0"
        }
        # Mock context to be a questions.json file
        context = SignalContext(
            node_type="dimension",
            node_id="dimensions/DIM01/questions.json",
            phase="phase_00",
            consumer_scope="Phase_00"
        )

        signals = vehicle.process(data, context)

        # Check generated signals
        assert len(signals) >= 3 # Alignment, Presence, Completeness

        types = [s.signal_type for s in signals]
        assert "StructuralAlignmentSignal" in types
        assert "EventPresenceSignal" in types
        assert "EventCompletenessSignal" in types

class TestSignalContextScoperVehicle:
    def test_process_question(self):
        vehicle = SignalContextScoperVehicle()
        data = {
            "id": "Q147",
            "type": "question",
            "answer": "Sí, existe la Ley 1448"
        }
        context = SignalContext(
            node_type="question",
            node_id="Q147",
            phase="phase_00",
            consumer_scope="Phase_00"
        )

        signals = vehicle.process(data, context)

        types = [s.signal_type for s in signals]
        assert "AnswerDeterminacySignal" in types
        assert "AnswerSpecificitySignal" in types
        assert "CanonicalMappingSignal" in types

        # Check determinacy
        det_signal = next(s for s in signals if s.signal_type == "AnswerDeterminacySignal")
        assert "sí" in det_signal.affirmative_markers

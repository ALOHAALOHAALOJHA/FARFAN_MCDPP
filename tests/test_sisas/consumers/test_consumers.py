# tests/test_sisas/consumers/test_consumers.py

import pytest
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.consumers.phase7.phase7_meso_consumer import Phase7MesoConsumer
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.signal import SignalContext, SignalSource
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signals.types.structural import CanonicalMappingSignal

class TestPhase7MesoConsumer:
    def test_initialization(self):
        consumer = Phase7MesoConsumer(consumer_id="test", consumer_phase="phase_7")
        assert consumer.consumption_contract is not None
        assert "CanonicalMappingSignal" in consumer.consumption_contract.subscribed_signal_types

    def test_process_signal(self):
        consumer = Phase7MesoConsumer(consumer_id="test", consumer_phase="phase_7")

        # Mock signal
        context = SignalContext("question", "Q1", "phase_7", "Phase_7")
        # Mock source
        from datetime import datetime
        source = SignalSource("evt1", "file.json", "path/file.json", datetime.utcnow(), "vehicle1")

        signal = CanonicalMappingSignal(
            context=context,
            source=source,
            source_item_id="Q1",
            mapped_entities={"policy_area": "PA01"},
            unmapped_aspects=[],
            mapping_completeness=1.0
        )

        result = consumer.process_signal(signal)
        assert result["processed"] is True
        assert result["analysis"]["mapped_entities"]["policy_area"] == "PA01"

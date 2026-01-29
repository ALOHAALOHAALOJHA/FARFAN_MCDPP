# tests/test_sisas/vocabulary/test_vocabulary.py

import pytest
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vocabulary.signal_vocabulary import SignalVocabulary
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vocabulary.capability_vocabulary import CapabilityVocabulary
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vocabulary.alignment_checker import VocabularyAlignmentChecker

class TestVocabularies:
    def test_signal_vocabulary_loading(self):
        vocab = SignalVocabulary()
        assert "StructuralAlignmentSignal" in vocab.definitions
        assert "EventPresenceSignal" in vocab.definitions
        assert vocab.is_valid_type("StructuralAlignmentSignal")

    def test_capability_vocabulary_loading(self):
        vocab = CapabilityVocabulary()
        assert "can_load_canonical" in vocab.definitions
        assert vocab.is_valid("can_load_canonical")

    def test_alignment_checker(self):
        signal_vocab = SignalVocabulary()
        capability_vocab = CapabilityVocabulary()

        checker = VocabularyAlignmentChecker(signal_vocab, capability_vocab)
        report = checker.check_alignment()

        # We expect some issues because not all signals might have producers/consumers defined in the core set yet
        # But we should check that it runs and returns a report
        assert report is not None
        assert report.signals_checked > 0
        assert report.capabilities_checked > 0

        # Verify specific alignment
        # StructuralAlignmentSignal is produced by can_load_canonical
        producers = capability_vocab.get_producers_of("StructuralAlignmentSignal")
        assert len(producers) > 0

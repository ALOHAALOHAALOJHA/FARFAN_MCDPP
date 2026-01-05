import unittest
import threading

from farfan_pipeline.phases.Phase_one.thread_safe_results import ThreadSafeResults
from farfan_pipeline.phases.Phase_one.phase1_truncation_audit import TruncationAudit
from farfan_pipeline.phases.Phase_one.phase1_models import SmartChunk, Chunk
from farfan_pipeline.phases.Phase_one.streaming_pdf_extractor import StreamingPDFExtractor
from pathlib import Path

class TestPhase1Remediation(unittest.TestCase):

    def test_streaming_extractor_instantiation(self):
        # Just check we can instantiate it
        extractor = StreamingPDFExtractor(Path("dummy.pdf"))
        self.assertIsInstance(extractor, StreamingPDFExtractor)
        # We can't test extraction without PyMuPDF

    def test_thread_safe_results(self):
        tsr = ThreadSafeResults()

        # Verify it behaves like a dict (UserDict)
        from collections import UserDict
        self.assertIsInstance(tsr, UserDict)

        def worker(results, key, val):
            results[key] = val

        threads = []
        for i in range(10):
            t = threading.Thread(target=worker, args=(tsr, f"key_{i}", i))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.assertEqual(len(tsr), 10)
        self.assertEqual(tsr["key_0"], 0)
        self.assertIn("key_5", tsr)

    def test_truncation_audit(self):
        audit = TruncationAudit.create(
            raw_text_len=150,
            processed_text_len=100,
            limit=100
        )
        self.assertEqual(audit.chars_lost, 50)
        self.assertAlmostEqual(audit.loss_ratio, 0.3333333, places=5)
        self.assertTrue(audit.was_truncated)

        audit_dict = audit.to_dict()
        self.assertEqual(audit_dict['chars_lost'], 50)

        audit_ok = TruncationAudit.create(
            raw_text_len=80,
            processed_text_len=80,
            limit=100
        )
        self.assertEqual(audit_ok.chars_lost, 0)
        self.assertFalse(audit_ok.was_truncated)

    def test_smart_chunk_traceability(self):
        # Verify SmartChunk has new fields and validates them
        sc = SmartChunk(
            chunk_id="PA01-DIM01",
            text="Test content",
            assignment_method="semantic",
            semantic_confidence=0.85
        )
        self.assertEqual(sc.assignment_method, "semantic")
        self.assertEqual(sc.semantic_confidence, 0.85)

        # Test default
        sc_def = SmartChunk(
            chunk_id="PA01-DIM01",
            text="Test content"
        )
        self.assertEqual(sc_def.assignment_method, "semantic")
        self.assertEqual(sc_def.semantic_confidence, 0.0)

        # Test validation failure
        with self.assertRaises(ValueError):
            SmartChunk(
                chunk_id="PA01-DIM01",
                text="Test",
                assignment_method="random_guess" # Invalid
            )

        with self.assertRaises(ValueError):
             SmartChunk(
                chunk_id="PA01-DIM01",
                text="Test",
                semantic_confidence=1.5 # Invalid
            )

    def test_chunk_traceability(self):
        # Verify Chunk has new fields (it's a dataclass, validation is less strict unless __post_init__ checks)
        c = Chunk(
            chunk_id="PA01-DIM01",
            assignment_method="fallback_sequential",
            semantic_confidence=0.1
        )
        self.assertEqual(c.assignment_method, "fallback_sequential")
        self.assertEqual(c.semantic_confidence, 0.1)

if __name__ == '__main__':
    unittest.main()

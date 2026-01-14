# tests/test_sisas/audit/test_audit.py

import pytest
from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.audit.signal_auditor import SignalAuditor
from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.bus import BusRegistry

class TestSignalAuditor:
    def test_audit_empty(self):
        registry = BusRegistry()
        auditor = SignalAuditor(registry)
        report = auditor.audit_signals()
        assert report.status == "PASS"
        assert report.stats["total_signals"] == 0

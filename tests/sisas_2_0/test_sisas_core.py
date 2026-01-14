"""
SISAS 2.0 Test Suite
====================

Tests for Signal, SignalScope, SignalProvenance, and SDO.

Author: F.A.R.F.A.N Pipeline Team
Version: 2.0.0
"""

import pytest
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

import sys
sys.path.insert(0, str(Path(__file__).parents[2]))

from canonic_questionnaire_central.core.signal import (
    Signal, SignalType, SignalScope, SignalProvenance
)
from canonic_questionnaire_central.core.signal_distribution_orchestrator import (
    SignalDistributionOrchestrator, DeadLetterReason, RoutingRules
)


# ============================================================================
# SIGNAL TESTS
# ============================================================================

class TestSignalScope:
    """Tests for SignalScope."""
    
    def test_valid_scope_creation(self):
        """Test creating a valid scope."""
        scope = SignalScope(phase="phase_1", policy_area="PA01", slot="D1-Q1")
        assert scope.phase == "phase_1"
        assert scope.policy_area == "PA01"
        assert scope.slot == "D1-Q1"
    
    def test_invalid_phase_raises(self):
        """Test that invalid phase raises ValueError."""
        with pytest.raises(ValueError, match="Invalid phase"):
            SignalScope(phase="phase_99", policy_area="PA01", slot="D1-Q1")
    
    def test_invalid_policy_area_raises(self):
        """Test that invalid policy area raises ValueError."""
        with pytest.raises(ValueError, match="Invalid policy_area"):
            SignalScope(phase="phase_1", policy_area="PA99", slot="D1-Q1")
    
    def test_scope_matching_exact(self):
        """Test exact scope matching."""
        scope1 = SignalScope(phase="phase_1", policy_area="PA01", slot="D1-Q1")
        scope2 = SignalScope(phase="phase_1", policy_area="PA01", slot="D1-Q1")
        assert scope1.matches(scope2)
    
    def test_scope_matching_wildcard(self):
        """Test wildcard scope matching."""
        scope1 = SignalScope(phase="phase_1", policy_area="PA01", slot="D1-Q1")
        scope2 = SignalScope(phase="phase_1", policy_area="ALL", slot="ALL")
        assert scope1.matches(scope2)
    
    def test_scope_to_dict(self):
        """Test scope serialization."""
        scope = SignalScope(phase="phase_1", policy_area="PA01", slot="D1-Q1")
        d = scope.to_dict()
        assert d == {"phase": "phase_1", "policy_area": "PA01", "slot": "D1-Q1"}


class TestSignalProvenance:
    """Tests for SignalProvenance."""
    
    def test_provenance_creation(self):
        """Test creating provenance."""
        prov = SignalProvenance(
            extractor="TestExtractor",
            source_file="test.txt",
            extraction_pattern="regex_pattern"
        )
        assert prov.extractor == "TestExtractor"
        assert prov.source_file == "test.txt"
        assert prov.extraction_pattern == "regex_pattern"
    
    def test_provenance_to_dict(self):
        """Test provenance serialization."""
        prov = SignalProvenance(
            extractor="TestExtractor",
            source_file="test.txt"
        )
        d = prov.to_dict()
        assert d["extractor"] == "TestExtractor"
        assert d["source_file"] == "test.txt"
        assert "created_at" in d


class TestSignal:
    """Tests for Signal."""
    
    @pytest.fixture
    def sample_signal(self):
        """Create a sample signal for testing."""
        scope = SignalScope(phase="phase_1", policy_area="PA01", slot="D1-Q1")
        prov = SignalProvenance(extractor="Test", source_file="test.txt")
        return Signal.create(
            signal_type=SignalType.MC05_FINANCIAL,
            scope=scope,
            payload={"amount": 1000000},
            provenance=prov,
            capabilities_required=["NUMERIC_PARSING"],
            empirical_availability=0.85,
            enrichment=True
        )
    
    def test_signal_creation(self, sample_signal):
        """Test signal creation."""
        assert sample_signal.signal_type == SignalType.MC05_FINANCIAL
        assert sample_signal.empirical_availability == 0.85
        assert sample_signal.enrichment == True
        # Verify UUID format
        UUID(sample_signal.signal_id)  # Will raise if invalid
    
    def test_signal_content_hash(self, sample_signal):
        """Test content hash generation."""
        hash1 = sample_signal.content_hash()
        assert len(hash1) == 64  # SHA-256 hex length
        
        # Same content = same hash
        hash2 = sample_signal.content_hash()
        assert hash1 == hash2
    
    def test_signal_validation_valid(self, sample_signal):
        """Test validation of valid signal."""
        is_valid, errors = sample_signal.validate()
        assert is_valid
        assert len(errors) == 0
    
    def test_signal_validation_invalid_availability(self):
        """Test validation catches invalid empirical_availability."""
        scope = SignalScope(phase="phase_1", policy_area="PA01", slot="D1-Q1")
        prov = SignalProvenance(extractor="Test", source_file="test.txt")
        signal = Signal.create(
            signal_type=SignalType.MC05_FINANCIAL,
            scope=scope,
            payload={"amount": 1000000},
            provenance=prov,
            capabilities_required=["NUMERIC_PARSING"],
            empirical_availability=1.5,  # Invalid
            enrichment=True
        )
        is_valid, errors = signal.validate()
        assert not is_valid
        assert any("empirical_availability" in e for e in errors)
    
    def test_signal_to_dict(self, sample_signal):
        """Test signal serialization."""
        d = sample_signal.to_dict()
        assert d["signal_type"] == "MC05"
        assert "scope" in d
        assert "payload" in d
        assert "provenance" in d
        assert "content_hash" in d
    
    def test_signal_from_dict(self, sample_signal):
        """Test signal deserialization."""
        d = sample_signal.to_dict()
        restored = Signal.from_dict(d)
        assert restored.signal_id == sample_signal.signal_id
        assert restored.signal_type == sample_signal.signal_type


# ============================================================================
# SDO TESTS
# ============================================================================

class TestSignalDistributionOrchestrator:
    """Tests for SignalDistributionOrchestrator."""
    
    @pytest.fixture
    def sdo(self):
        """Create SDO with default rules."""
        return SignalDistributionOrchestrator()
    
    @pytest.fixture
    def sample_signal(self):
        """Create a sample signal."""
        scope = SignalScope(phase="phase_1", policy_area="PA01", slot="D1-Q1")
        prov = SignalProvenance(extractor="Test", source_file="test.txt")
        return Signal.create(
            signal_type=SignalType.MC05_FINANCIAL,
            scope=scope,
            payload={"amount": 1000000},
            provenance=prov,
            capabilities_required=["NUMERIC_PARSING"],
            empirical_availability=0.85,
            enrichment=True
        )
    
    def test_sdo_initialization(self, sdo):
        """Test SDO initialization."""
        assert sdo.rules is not None
        assert len(sdo.consumers) == 0
        assert sdo.get_metrics()["signals_dispatched"] == 0
    
    def test_consumer_registration(self, sdo):
        """Test consumer registration."""
        handler_called = []
        
        def handler(sig):
            handler_called.append(sig.signal_id)
        
        sdo.register_consumer(
            consumer_id="test_consumer",
            scopes=[{"phase": "phase_1", "policy_area": "ALL", "slot": "ALL"}],
            capabilities=["NUMERIC_PARSING"],
            handler=handler
        )
        
        assert "test_consumer" in sdo.consumers
        assert len(sdo.consumers["test_consumer"].capabilities) == 1
    
    def test_signal_dispatch_success(self, sdo, sample_signal):
        """Test successful signal dispatch."""
        received = []
        
        def handler(sig):
            received.append(sig)
        
        sdo.register_consumer(
            consumer_id="test_consumer",
            scopes=[{"phase": "phase_1", "policy_area": "ALL", "slot": "ALL"}],
            capabilities=["NUMERIC_PARSING"],
            handler=handler
        )
        
        success = sdo.dispatch(sample_signal)
        
        assert success
        assert len(received) == 1
        assert received[0].signal_id == sample_signal.signal_id
    
    def test_signal_dispatch_no_consumer(self, sdo, sample_signal):
        """Test dispatch with no matching consumer."""
        success = sdo.dispatch(sample_signal)
        
        assert not success
        # Should be in dead letter queue
        dead_letters = sdo.get_dead_letters(DeadLetterReason.NO_CONSUMER)
        assert len(dead_letters) == 1
    
    def test_signal_deduplication(self, sdo, sample_signal):
        """Test signal deduplication."""
        received = []
        
        def handler(sig):
            received.append(sig)
        
        sdo.register_consumer(
            consumer_id="test_consumer",
            scopes=[{"phase": "phase_1", "policy_area": "ALL", "slot": "ALL"}],
            capabilities=["NUMERIC_PARSING"],
            handler=handler
        )
        
        # Dispatch same signal twice
        sdo.dispatch(sample_signal)
        sdo.dispatch(sample_signal)  # Should be deduplicated
        
        assert len(received) == 1  # Only one delivery
        assert sdo.get_metrics()["signals_deduplicated"] == 1
    
    def test_value_gating(self, sdo):
        """Test value gating based on empirical availability."""
        # Create signal with low availability
        scope = SignalScope(phase="phase_1", policy_area="PA01", slot="D1-Q1")
        prov = SignalProvenance(extractor="Test", source_file="test.txt")
        low_value_signal = Signal.create(
            signal_type=SignalType.MC05_FINANCIAL,
            scope=scope,
            payload={"amount": 1000000},
            provenance=prov,
            capabilities_required=["NUMERIC_PARSING"],
            empirical_availability=0.1,  # Below threshold
            enrichment=False  # Not enrichment, so value gate applies
        )
        
        sdo.register_consumer(
            consumer_id="test_consumer",
            scopes=[{"phase": "phase_1", "policy_area": "ALL", "slot": "ALL"}],
            capabilities=["NUMERIC_PARSING"],
            handler=lambda s: None
        )
        
        success = sdo.dispatch(low_value_signal)
        
        assert not success
        dead_letters = sdo.get_dead_letters(DeadLetterReason.LOW_VALUE)
        assert len(dead_letters) == 1
    
    def test_capability_matching(self, sdo, sample_signal):
        """Test capability matching."""
        # Register consumer without required capability
        sdo.register_consumer(
            consumer_id="limited_consumer",
            scopes=[{"phase": "phase_1", "policy_area": "ALL", "slot": "ALL"}],
            capabilities=["DIFFERENT_CAPABILITY"],  # Missing NUMERIC_PARSING
            handler=lambda s: None
        )
        
        success = sdo.dispatch(sample_signal)
        
        assert not success
        # Should end up in dead letter (no matching consumer)
        assert sdo.get_metrics()["dead_letters"] == 1
    
    def test_health_check(self, sdo, sample_signal):
        """Test health check."""
        sdo.register_consumer(
            consumer_id="test_consumer",
            scopes=[{"phase": "phase_1", "policy_area": "ALL", "slot": "ALL"}],
            capabilities=["NUMERIC_PARSING"],
            handler=lambda s: None
        )
        
        sdo.dispatch(sample_signal)
        
        health = sdo.health_check()
        
        assert health["status"] == "HEALTHY"
        assert health["consumers_total"] == 1
        assert health["consumers_healthy"] == 1
    
    def test_audit_log(self, sdo, sample_signal):
        """Test audit log entries."""
        sdo.register_consumer(
            consumer_id="test_consumer",
            scopes=[{"phase": "phase_1", "policy_area": "ALL", "slot": "ALL"}],
            capabilities=["NUMERIC_PARSING"],
            handler=lambda s: None
        )
        
        sdo.dispatch(sample_signal)
        
        audit = sdo.get_audit_log(sample_signal.signal_id)
        
        assert len(audit) >= 1
        assert any(e.action == "DELIVERED" for e in audit)


# ============================================================================
# EXTRACTOR TESTS
# ============================================================================

class TestExtractors:
    """Tests for signal extractors."""
    
    @pytest.fixture
    def sdo(self):
        """Create SDO with phase_1 consumer."""
        sdo = SignalDistributionOrchestrator()
        sdo.register_consumer(
            consumer_id="phase_1",
            scopes=[{"phase": "phase_1", "policy_area": "ALL", "slot": "ALL"}],
            capabilities=[
                "NUMERIC_PARSING", "FINANCIAL_ANALYSIS", "CURRENCY_NORMALIZATION",
                "CAUSAL_INFERENCE", "GRAPH_CONSTRUCTION", "VERB_ANALYSIS",
                "NER_EXTRACTION", "ENTITY_RESOLUTION", "COREFERENCE"
            ],
            handler=lambda s: None
        )
        return sdo
    
    def test_financial_chain_extractor(self, sdo):
        """Test FinancialChainExtractor."""
        from src.farfan_pipeline.infrastructure.irrigation_using_signals.extractors.financial_chain_extractor import (
            FinancialChainExtractor
        )
        from src.farfan_pipeline.infrastructure.irrigation_using_signals.extractors.base_extractor import (
            ExtractionContext
        )
        
        extractor = FinancialChainExtractor(sdo)
        context = ExtractionContext(source_file="test.txt", policy_area="PA01")
        
        text = "El presupuesto de $150 millones para el proyecto."
        result = extractor.extract_and_dispatch(text, context)
        
        assert result.signals_created >= 1
        assert result.signals_delivered >= 1
    
    def test_causal_verb_extractor(self, sdo):
        """Test CausalVerbExtractor."""
        from src.farfan_pipeline.infrastructure.irrigation_using_signals.extractors.causal_verb_extractor import (
            CausalVerbExtractor
        )
        from src.farfan_pipeline.infrastructure.irrigation_using_signals.extractors.base_extractor import (
            ExtractionContext
        )
        
        extractor = CausalVerbExtractor(sdo)
        context = ExtractionContext(source_file="test.txt", policy_area="PA01")
        
        text = "Fortalecer la capacidad institucional mediante la implementación de programas."
        result = extractor.extract_and_dispatch(text, context)
        
        assert result.signals_created >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

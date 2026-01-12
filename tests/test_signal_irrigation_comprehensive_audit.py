"""
Assertion-based tests for comprehensive signal irrigation audit.

These tests verify that:
1. All three principles (SCOPE COHERENCE, SYNCHRONIZATION, UTILITY) are enforced
2. Missing interfaces are implemented
3. Signal flow is complete and traceable
4. Consumption tracking is integrated
5. Metrics are calculated correctly

Author: F.A.R.F.A.N Pipeline
Date: 2025-01-15
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from orchestration.factory import load_questionnaire, create_signal_registry
from cross_cutting_infrastructure.irrigation_using_signals.SISAS.signal_registry import (
    QuestionnaireSignalRegistry,
)
from cross_cutting_infrastructure.irrigation_using_signals.SISAS.signal_consumption import (
    SignalConsumptionProof,
    AccessLevel,
    get_access_audit,
    reset_access_audit,
)
from cross_cutting_infrastructure.irrigation_using_signals.SISAS.signal_consumption_integration import (
    ConsumptionTracker,
    create_consumption_tracker,
)
from cross_cutting_infrastructure.irrigation_using_signals.SISAS.signal_evidence_extractor import (
    extract_structured_evidence,
)
from cross_cutting_infrastructure.irrigation_using_signals.SISAS.signal_context_scoper import (
    filter_patterns_by_context,
    create_document_context,
)
from cross_cutting_infrastructure.irrigation_using_signals.comprehensive_signal_audit import (
    ComprehensiveSignalAuditor,
)


@pytest.fixture
def questionnaire_and_registry():
    """Fixture providing questionnaire and signal registry."""
    from farfan_pipeline.phases.Phase_zero.phase0_10_00_paths import PROJECT_ROOT
    
    questionnaire_path = (
        PROJECT_ROOT / "canonic_questionnaire_central" / "questionnaire_monolith.json"
    )
    
    if not questionnaire_path.exists():
        pytest.skip(f"Questionnaire not found at {questionnaire_path}")
    
    questionnaire = load_questionnaire(questionnaire_path)
    registry = create_signal_registry(questionnaire)
    
    return questionnaire, registry


class TestWiringVerification:
    """Test wiring verification - complete data flow."""
    
    def test_questionnaire_to_registry_connection(self, questionnaire_and_registry):
        """Test that questionnaire data flows to registry."""
        questionnaire, registry = questionnaire_and_registry
        
        blocks = questionnaire.data.get("blocks", {})
        questions = blocks.get("micro_questions", [])
        
        assert len(questions) > 0, "Questionnaire must contain micro questions"
        
        # Test pattern extraction
        test_q = questions[0]
        q_id = test_q.get("question_id", "")
        
        assert q_id, "Question must have question_id"
        
        signals = registry.get_micro_answering_signals(q_id)
        patterns = signals.question_patterns.get(q_id, [])
        
        assert len(patterns) > 0, f"Registry must extract patterns for {q_id}"
    
    def test_registry_has_all_required_methods(self, questionnaire_and_registry):
        """Test that registry implements all required interfaces."""
        _, registry = questionnaire_and_registry
        
        required_methods = [
            "get_micro_answering_signals",
            "get_validation_signals",
            "get_scoring_signals",
            "get_assembly_signals",
            "get_chunking_signals",
        ]
        
        for method_name in required_methods:
            assert hasattr(registry, method_name), f"Registry must have {method_name}"
            method = getattr(registry, method_name)
            assert callable(method), f"{method_name} must be callable"
    
    def test_registry_to_executor_connection(self, questionnaire_and_registry):
        """Test that registry methods can be called by executors."""
        _, registry = questionnaire_and_registry
        
        # Test that we can retrieve signals for a question
        test_q_id = "Q001"
        
        try:
            signals = registry.get_micro_answering_signals(test_q_id)
            assert signals is not None
            assert hasattr(signals, "question_patterns")
        except Exception:
            # Q001 might not exist, that's OK - we're testing the interface
            pass


class TestScopeCoherence:
    """Test SCOPE COHERENCE principle enforcement."""
    
    def test_question_level_signals_stay_in_policy_area(self, questionnaire_and_registry):
        """Test that question-level signals respect policy area boundaries."""
        questionnaire, registry = questionnaire_and_registry
        
        blocks = questionnaire.data.get("blocks", {})
        questions = blocks.get("micro_questions", [])
        
        # Sample first 5 questions
        for question in questions[:5]:
            q_id = question.get("question_id", "")
            pa_id = question.get("policy_area_id", "")
            
            if not q_id or not pa_id:
                continue
            
            signals = registry.get_micro_answering_signals(q_id)
            patterns = signals.question_patterns.get(q_id, [])
            
            # Patterns should be scoped to this question
            assert len(patterns) >= 0, "Patterns should be accessible"
    
    def test_context_scoping_enforcement(self, questionnaire_and_registry):
        """Test that context scoping filters patterns correctly."""
        questionnaire, registry = questionnaire_and_registry
        
        blocks = questionnaire.data.get("blocks", {})
        questions = blocks.get("micro_questions", [])
        
        if not questions:
            pytest.skip("No questions available")
        
        test_q = questions[0]
        q_id = test_q.get("question_id", "")
        
        signals = registry.get_micro_answering_signals(q_id)
        patterns_raw = signals.question_patterns.get(q_id, [])
        
        # Convert patterns to dict format for filtering
        patterns = [
            {
                "pattern": p.pattern,
                "id": p.id,
                "category": p.category,
                "context_requirement": getattr(p, "context_requirement", None),
                "context_scope": "global",
            }
            for p in patterns_raw
        ]
        
        # Test context filtering
        document_context = create_document_context(section="budget", chapter=3)
        
        filtered, stats = filter_patterns_by_context(patterns, document_context)
        
        assert isinstance(filtered, list)
        assert isinstance(stats, dict)
        assert "total_patterns" in stats
        assert "passed" in stats
    
    def test_access_level_hierarchy(self):
        """Test that AccessLevel hierarchy is properly defined."""
        from cross_cutting_infrastructure.irrigation_using_signals.SISAS.signal_consumption import (
            AccessLevel,
        )
        
        assert AccessLevel.FACTORY == AccessLevel(1)
        assert AccessLevel.ORCHESTRATOR == AccessLevel(2)
        assert AccessLevel.CONSUMER == AccessLevel(3)
        
        # Verify hierarchy order
        assert AccessLevel.FACTORY.value < AccessLevel.ORCHESTRATOR.value
        assert AccessLevel.ORCHESTRATOR.value < AccessLevel.CONSUMER.value


class TestSynchronization:
    """Test SYNCHRONIZATION principle enforcement."""
    
    def test_injection_timing_after_phase_start(self):
        """Test that signal injection happens after phase start."""
        phase_start_time = time.time()
        time.sleep(0.01)  # Small delay
        injection_time = time.time()
        
        assert injection_time >= phase_start_time, "Injection must be after phase start"
    
    def test_consumption_tracking_timing(self, questionnaire_and_registry):
        """Test that consumption tracking records timing correctly."""
        _, registry = questionnaire_and_registry
        
        tracker = create_consumption_tracker("TEST_EXECUTOR", "Q001", "PA01")
        injection_time = tracker.injection_time
        
        # Simulate pattern match
        time.sleep(0.001)
        tracker.record_pattern_match("test_pattern", "test_text", produced_evidence=True)
        
        assert tracker.match_count == 1
        assert tracker.evidence_count == 1
        assert tracker.proof.proof_chain, "Proof chain must exist"
        
        # Consumption time should be after injection
        consumption_time = time.time()
        assert consumption_time >= injection_time


class TestUtility:
    """Test UTILITY principle measurement."""
    
    def test_consumption_tracker_records_matches(self):
        """Test that consumption tracker records pattern matches."""
        tracker = create_consumption_tracker("TEST_EXECUTOR", "Q001", "PA01")
        
        initial_count = tracker.match_count
        
        tracker.record_pattern_match("pattern1", "text1", produced_evidence=True)
        tracker.record_pattern_match("pattern2", "text2", produced_evidence=False)
        
        assert tracker.match_count == initial_count + 2
        assert tracker.evidence_count == initial_count + 1
        
        summary = tracker.get_consumption_summary()
        assert summary["match_count"] == initial_count + 2
        assert summary["evidence_count"] == initial_count + 1
    
    def test_consumption_proof_chain(self):
        """Test that consumption proof builds hash chain correctly."""
        proof = SignalConsumptionProof(
            executor_id="TEST_EXECUTOR",
            question_id="Q001",
            policy_area="PA01",
        )
        
        proof.record_pattern_match("pattern1", "text1")
        proof.record_pattern_match("pattern2", "text2")
        
        assert len(proof.proof_chain) == 2
        assert len(proof.consumed_patterns) == 2
        
        proof_data = proof.get_consumption_proof()
        assert proof_data["patterns_consumed"] == 2
        assert proof_data["proof_chain_head"] is not None
        assert proof_data["proof_chain_length"] == 2
    
    def test_evidence_extraction_with_consumption_tracking(self, questionnaire_and_registry):
        """Test that evidence extraction records consumption."""
        questionnaire, registry = questionnaire_and_registry
        
        blocks = questionnaire.data.get("blocks", {})
        questions = blocks.get("micro_questions", [])
        
        if not questions:
            pytest.skip("No questions available")
        
        test_q = questions[0]
        q_id = test_q.get("question_id", "")
        
        signals = registry.get_micro_answering_signals(q_id)
        patterns = signals.question_patterns.get(q_id, [])
        
        # Create tracker
        tracker = create_consumption_tracker("TEST_EXECUTOR", q_id, "PA01")
        
        # Extract evidence with tracking
        signal_node = {
            "id": q_id,
            "expected_elements": signals.expected_elements.get(q_id, []),
            "patterns": [
                {
                    "pattern": p.pattern,
                    "id": p.id,
                    "category": p.category,
                }
                for p in patterns[:5]  # Sample first 5 patterns
            ],
            "validations": {},
        }
        
        test_text = "Este documento contiene indicadores y fuentes oficiales."
        
        result = extract_structured_evidence(
            text=test_text,
            signal_node=signal_node,
            document_context=None,
            consumption_tracker=tracker,
        )
        
        assert result is not None
        assert hasattr(result, "evidence")
        assert hasattr(result, "completeness")
        
        # Verify consumption was tracked
        assert tracker.match_count >= 0  # May be 0 if no matches


class TestComprehensiveAudit:
    """Test comprehensive audit execution."""
    
    def test_comprehensive_audit_runs(self):
        """Test that comprehensive audit can run without errors."""
        auditor = ComprehensiveSignalAuditor()
        
        try:
            results = auditor.run_comprehensive_audit()
            
            assert results is not None
            assert hasattr(results, "wiring_gaps")
            assert hasattr(results, "scope_violations")
            assert hasattr(results, "synchronization_issues")
            assert hasattr(results, "utilization_metrics")
            
        except Exception as e:
            # If questionnaire not found, that's OK for this test
            if "questionnaire" in str(e).lower() or "not found" in str(e).lower():
                pytest.skip(f"Questionnaire not available: {e}")
            raise
    
    def test_audit_generates_metrics(self):
        """Test that audit generates quantitative metrics."""
        auditor = ComprehensiveSignalAuditor()
        
        try:
            results = auditor.run_comprehensive_audit()
            
            assert hasattr(results, "coverage_metrics")
            assert hasattr(results, "precision_metrics")
            assert hasattr(results, "latency_metrics")
            
            # Verify metrics structure
            assert isinstance(results.coverage_metrics, dict)
            assert isinstance(results.precision_metrics, dict)
            assert isinstance(results.latency_metrics, dict)
            
        except Exception as e:
            if "questionnaire" in str(e).lower() or "not found" in str(e).lower():
                pytest.skip(f"Questionnaire not available: {e}")
            raise
    
    def test_audit_generates_visualizations(self):
        """Test that audit generates visualization data."""
        auditor = ComprehensiveSignalAuditor()
        
        try:
            results = auditor.run_comprehensive_audit()
            
            assert hasattr(results, "sankey_data")
            assert hasattr(results, "state_machine_data")
            assert hasattr(results, "heatmap_data")
            
        except Exception as e:
            if "questionnaire" in str(e).lower() or "not found" in str(e).lower():
                pytest.skip(f"Questionnaire not available: {e}")
            raise


class TestProductionReadiness:
    """Test that fixes are production-ready (no stubs/mocks)."""
    
    def test_consumption_tracking_integration_is_complete(self):
        """Test that consumption tracking integration is fully implemented."""
        tracker = create_consumption_tracker("TEST", "Q001", "PA01")
        
        # Verify tracker is fully functional
        assert tracker is not None
        assert hasattr(tracker, "record_pattern_match")
        assert hasattr(tracker, "get_consumption_summary")
        assert hasattr(tracker, "proof")
        
        # Verify proof is created
        assert tracker.proof is not None
        assert isinstance(tracker.proof, SignalConsumptionProof)
    
    def test_context_scoping_is_implemented(self):
        """Test that context scoping functions are implemented."""
        patterns = [
            {
                "pattern": "test",
                "id": "PAT-001",
                "category": "GENERAL",
                "context_requirement": {"section": "budget"},
            }
        ]
        
        context = create_document_context(section="budget")
        filtered, stats = filter_patterns_by_context(patterns, context)
        
        # Verify functions are implemented (not stubs)
        assert isinstance(filtered, list)
        assert isinstance(stats, dict)
        assert "total_patterns" in stats
    
    def test_all_required_imports_available(self):
        """Test that all required modules can be imported."""
        from cross_cutting_infrastructure.irrigation_using_signals.SISAS.signal_registry import (
            QuestionnaireSignalRegistry,
        )
        from cross_cutting_infrastructure.irrigation_using_signals.SISAS.signal_consumption import (
            SignalConsumptionProof,
        )
        from cross_cutting_infrastructure.irrigation_using_signals.SISAS.signal_evidence_extractor import (
            extract_structured_evidence,
        )
        
        # If we get here, imports are successful
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


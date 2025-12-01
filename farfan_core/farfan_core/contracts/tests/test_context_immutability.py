"""
Tests for Context Immutability Contract (CIC)
"""
import pytest
import sys
from dataclasses import FrozenInstanceError
from farfan_core.contracts.context_immutability import ContextImmutabilityContract
from farfan_core.question_context import QuestionContext

class TestContextImmutabilityContract:
    
    def test_mutation_attempt(self):
        """Reintentos de mutación ⇒ excepción determinista."""
        ctx = QuestionContext(
            question_mapping="q1", 
            dnp_standards={"s1": "v1"}, 
            required_evidence_types=("e1",), 
            search_queries=("sq1",), 
            validation_criteria={"c1": "v1"}, 
            traceability_id="tid1"
        )
        
        # Verify top-level mutation fails (handled by verify_immutability internally or explicitly here)
        with pytest.raises(FrozenInstanceError):
            ctx.traceability_id = "mutated"

    def test_canonical_serialization(self):
        """Serialización canónica ⇒ mismo context_hash en procesos distintos."""
        ctx1 = QuestionContext(
            question_mapping="q1", 
            dnp_standards={"s1": "v1"}, 
            required_evidence_types=("e1",), 
            search_queries=("sq1",), 
            validation_criteria={"c1": "v1"}, 
            traceability_id="tid1"
        )
        ctx2 = QuestionContext(
            question_mapping="q1", 
            dnp_standards={"s1": "v1"}, 
            required_evidence_types=("e1",), 
            search_queries=("sq1",), 
            validation_criteria={"c1": "v1"}, 
            traceability_id="tid1"
        )
        
        # verify_immutability now returns the digest
        digest1 = ContextImmutabilityContract.verify_immutability(ctx1)
        digest2 = ContextImmutabilityContract.verify_immutability(ctx2)
        
        assert digest1 == digest2

if __name__ == "__main__":
    sys.exit(pytest.main(["-v", __file__]))

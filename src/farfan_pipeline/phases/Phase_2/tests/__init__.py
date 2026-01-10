"""
Phase 2 Adversarial Test Suite

PHASE_LABEL: Phase 2
PHASE_COMPONENT: Tests
PHASE_ROLE: Severe adversarial validation of 300-contract architecture

This test suite implements SEVERE adversarial testing to validate:
1. Complete elimination of legacy 30-executor design
2. Presence and integrity of all 300 JSON contracts
3. Single deterministic execution sequence
4. No competing/parallel execution flows
5. Full self-sufficiency of Phase 2

Test Categories:
- test_contract_integrity.py: Contract existence, schema, completeness
- test_architecture_compliance.py: No legacy code, proper imports
- test_execution_flow.py: Sequential execution, no parallelism
- test_end_to_end.py: Full pipeline validation
- test_adversarial_edge_cases.py: Malformed inputs, boundary conditions

Run with: pytest tests/ -v --tb=long
"""

__all__ = [
    "test_contract_integrity",
    "test_architecture_compliance",
    "test_execution_flow",
    "test_end_to_end",
    "test_adversarial_edge_cases",
]

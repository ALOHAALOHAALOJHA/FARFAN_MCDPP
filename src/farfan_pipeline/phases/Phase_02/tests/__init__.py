"""
Phase 2 Adversarial Test Suite
==============================

PHASE_LABEL: Phase 2
PHASE_COMPONENT: Tests
PHASE_ROLE: SEVERE adversarial validation of 300-contract architecture

Version: 2.0.0
Date: 2026-01-13

This test suite implements SEVERE adversarial testing to validate:
1. Complete elimination of legacy 30-executor design
2. Presence and integrity of all 300 JSON contracts
3. Single deterministic execution sequence
4. No competing/parallel execution flows
5. Full self-sufficiency of Phase 2
6. Interface compatibility (Phase 1→2, Phase 2→3)
7. Security (SQL injection, XSS, hash collisions)
8. Resilience (retries, timeouts, error recovery)

═══════════════════════════════════════════════════════════════════════════════
TEST INVENTORY (17 test modules, 300+ test cases)
═══════════════════════════════════════════════════════════════════════════════

ARCHITECTURE & COMPLIANCE:
  - phase2_10_00_test_architecture_compliance.py  → Legacy elimination, imports
  - phase2_10_00_test_per_file_validation.py      → File naming, structure

CONTRACT VALIDATION:
  - phase2_10_00_test_contracts_validation.py     → 300 contracts integrity
  - phase2_10_00_test_adversarial_edge_cases.py   → Malformed contracts, edge cases

EXECUTION FLOW:
  - phase2_10_00_test_execution_flow.py           → Sequential execution
  - phase2_10_00_test_end_to_end.py               → Full pipeline E2E
  - phase2_10_00_test_comprehensive_e2e.py        → Comprehensive E2E coverage

ADVERSARIAL / SECURITY:
  - phase2_10_00_test_adversarial_core.py         → Core adversarial tests
  - phase2_10_00_test_adversarial_e2e_pipeline.py → E2E adversarial pipeline
  - phase2_10_00_test_sql_injection_security.py   → SQL injection protection
  - phase2_10_00_test_checkpoint_hash_security.py → Hash collision prevention

INTERPHASE ADAPTERS:
  - phase2_10_00_test_interphase_p1_to_p2_adapter.py → Phase 1→2 compatibility
  - phase2_10_00_test_interphase_p2_to_p3_adapter.py → Phase 2→3 compatibility

RESILIENCE:
  - phase2_10_00_test_retry_resilience.py         → Exponential backoff
  - phase2_10_00_test_datetime_timezone.py        → Timezone handling

UTILITIES:
  - phase2_10_00_conftest.py                      → Pytest fixtures
  - phase2_10_00_run_adversarial_tests.py         → Test runner script

═══════════════════════════════════════════════════════════════════════════════
RUN COMMANDS
═══════════════════════════════════════════════════════════════════════════════

# Run all tests:
pytest src/farfan_pipeline/phases/Phase_2/tests/ -v --tb=short

# Run adversarial tests only:
pytest src/farfan_pipeline/phases/Phase_2/tests/ -v -k "adversarial"

# Run security tests only:
pytest src/farfan_pipeline/phases/Phase_2/tests/ -v -k "security or injection"

# Run interphase tests only:
pytest src/farfan_pipeline/phases/Phase_2/tests/ -v -k "interphase or adapter"

═══════════════════════════════════════════════════════════════════════════════
"""

__all__ = [
    # Architecture
    "phase2_10_00_test_architecture_compliance",
    "phase2_10_00_test_per_file_validation",
    # Contracts
    "phase2_10_00_test_contracts_validation",
    "phase2_10_00_test_adversarial_edge_cases",
    # Execution
    "phase2_10_00_test_execution_flow",
    "phase2_10_00_test_end_to_end",
    "phase2_10_00_test_comprehensive_e2e",
    # Adversarial/Security
    "phase2_10_00_test_adversarial_core",
    "phase2_10_00_test_adversarial_e2e_pipeline",
    "phase2_10_00_test_sql_injection_security",
    "phase2_10_00_test_checkpoint_hash_security",
    # Interphase
    "phase2_10_00_test_interphase_p1_to_p2_adapter",
    "phase2_10_00_test_interphase_p2_to_p3_adapter",
    # Resilience
    "phase2_10_00_test_retry_resilience",
    "phase2_10_00_test_datetime_timezone",
]

# Contract Governance & Change Control

## 1. Contracts as APIs
All contracts in `farfan_core.contracts` are treated as **System APIs**. They are the source of truth for system invariants.

### Rule: Explicit Dependency Declaration
Any new module that relies on a system invariant must explicitly declare which contract enforces it using the `@uses_contract` decorator.

```python
from farfan_core.contracts.governance import uses_contract
from farfan_core.contracts import RoutingContract

@uses_contract(RoutingContract)
def calculate_path(a, b):
    # ... implementation relying on deterministic routing ...
```

### Rule: Mandatory Testing Pair
For every declared contract dependency, the consuming module's test suite must include:
1.  **One Positive Test**: Proving the module works when the contract holds.
2.  **One Negative Test**: Proving the module fails gracefully (or as expected) when the contract is violated (simulated).

## 2. Immutable Baselines
### Rule: Mandatory Snapshots
*   **$\sigma$ Snapshots**: All external inputs (corpus, standards, models) must be hashed and pinned. The `SnapshotContract` enforces this.
*   **Workflow Lockfiles**: Execution DAGs and environment configurations must be version-controlled and locked.

## 3. Continuous Verification
### Rule: Weekly Mutation Suite
*   **Frequency**: Run `scripts/run_mutation_suite.py` weekly.
*   **Policy**: Merges are **BLOCKED** if the mutation score regresses (i.e., if fewer mutants are killed or property tests find new failures).
*   **Definition**: The mutation suite runs Property-Based Tests (Hypothesis) with high example counts (`max_examples=1000+`) to exhaustively search for edge cases.

### Rule: Coverage Requirements
*   **Target**: 90% line and branch coverage for contracts and orchestrator.
*   **Command**: `coverage report --include="farfan_core/farfan_core/contracts/*" --fail-under=90`

## 4. Release Artifacts
### Rule: Certificate Storage
Every release must be accompanied by a `certificates/` directory containing the 15 generated JSON certificates.

*   **Command**: `python3 scripts/bundle_release_certificates.py`
*   **Artifacts**: `*_certificate.json`
*   **Purpose**: Prove the exact behavior of the shipped code.

## 5. Enforcement
*   **CI/CD**: The `verify_all_contracts.py` script must pass before any merge.
*   **Code Review**: Reviewers must check for `@uses_contract` declarations and corresponding positive/negative tests.

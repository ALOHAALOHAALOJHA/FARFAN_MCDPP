# F.A.R.F.A.N Contracts Module

This module implements the **15-Contract Suite** for rigorous system verification.

## Structure

- `contracts/`: Python implementations of the 15 contracts.
- `contracts/tests/`: Pytest/Hypothesis test suites for each contract.
- `contracts/tools/`: CLI tools to generate verification certificates.

## Execution

To verify the entire suite and generate certificates:

```bash
python3 farfan_core/contracts/verify_all_contracts.py
```

## The 15 Contracts

1.  **Routing Contract (RC)**: Deterministic A* routing.
2.  **Snapshot Contract (SC)**: Frozen external inputs.
3.  **Context Immutability Contract (CIC)**: Frozen context objects.
4.  **Permutation-Invariance Contract (PIC)**: Order-independent aggregation.
5.  **Budget & Monotonicity Contract (BMC)**: Monotonic resource allocation.
6.  **Total Ordering Contract (TOC)**: Stable sorting with tie-breaks.
7.  **Retriever Contract (ReC)**: Deterministic retrieval top-K.
8.  **Alignment Stability Contract (ASC)**: Reproducible Optimal Transport.
9.  **Idempotency & De-dup Contract (IDC)**: Evidence de-duplication.
10. **Risk Certificate Contract (RCC)**: Conformal prediction guarantees.
11. **Monotone Compliance Contract (MCC)**: Monotonic logic evaluation.
12. **Failure & Fallback Contract (FFC)**: Deterministic fault handling.
13. **Concurrency Determinism Contract (CDC)**: Invariant concurrent outputs.
14. **Traceability Contract (TC)**: Merkle Tree audit trails.
15. **Refusal Contract (RefC)**: Pre-flight refusal logic.

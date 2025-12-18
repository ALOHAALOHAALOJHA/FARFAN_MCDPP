# Phase 1: CPP Ingestion (`phase_1_cpp_ingestion`)
STATUS: ACTIVE

Phase 1 transforms a validated `CanonicalInput` into a `CanonPolicyPackage` (CPP) with
an immutable PA×DIM grid:

- 10 policy areas (`PA01`…`PA10`)
- 6 causal dimensions (`DIM01`…`DIM06`)
- Constitutional invariant: **exactly 60 chunks**

## Entry Point
- `canonic_phases.phase_1_cpp_ingestion.execute_phase_1_with_full_contract`

## Key Invariants
- Output chunk count == 60
- Complete PA×DIM coverage
- Deterministic execution (given fixed inputs + controlled randomness)

## Reference
- `FORCING_ROUTE.md`


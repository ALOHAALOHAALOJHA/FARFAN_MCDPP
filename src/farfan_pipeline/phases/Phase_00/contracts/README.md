# Phase 0 Contracts

This folder contains the formal contract specifications for Phase 0 of the
F.A.R.F.A.N pipeline.

## Contract Files

### 1. phase0_input_contract.py
Defines the input contract for Phase 0. Since Phase 0 is the initial phase,
it receives inputs from the **user** rather than from a previous phase.

**Key Sections:**
- User-provided inputs (PDF path, run ID, questionnaire)
- Environment variables for configuration
- Validation rules
- Security constraints

### 2. phase0_mission_contract.py
Defines the mission, responsibilities, and internal execution order of Phase 0.

**Key Sections:**
- Mission statement
- Module execution order (topological)
- All 28 modules with dependencies
- Critical path (7 modules)
- Execution invariants
- Success criteria
- Failure modes

### 3. phase0_output_contract.py
Defines the output contract for Phase 0, which is the input to Phase 1.

**Key Sections:**
- CanonicalInput dataclass specification
- WiringComponents dataclass
- EnforcementMetrics
- 6 postconditions (POST-001 to POST-006)
- Determinism guarantees
- Resource guarantees
- Phase 1 handoff protocol

## Contract Purpose

Contracts serve as:
1. **Interface Specifications** - Define what each phase accepts and produces
2. **Validation Rules** - Specify invariants and postconditions
3. **Documentation** - Explain responsibilities and guarantees
4. **Verification Basis** - Enable automated contract checking

## Contract Hierarchy

```
Phase 0 Contracts
├── Input Contract (user inputs)
├── Mission Contract (internal execution)
└── Output Contract (handoff to Phase 1)
```

## Related Documentation

- `../README.md` - Phase 0 overview
- `../PHASE_0_MANIFEST.json` - Complete module inventory
- `../docs/PHASE1_COMPATIBILITY_CERTIFICATE.md` - Phase 1 compatibility

## Usage

Contracts are documentation files (not executable code). They are referenced by:
- Validation modules (e.g., `phase0_40_00_input_validation.py`)
- Test suites
- Audit processes
- Integration documentation

---
**Phase 0 Contract System - Version 1.0.0**

# Phase 1: CPP Ingestion (`phase1_20_00_cpp_ingestion`)

**Status**: ACTIVE
**Version**: CPP-2025.1
**Last Updated**: 2025-12-18
**Canonical Path**: `src/farfan_pipeline/phases/Phase_one/`

---

## Abstract

Phase 1 (Canon Policy Package Ingestion) constitutes the foundational transformation stage of the F.A.R.F.A.N mechanistic policy analysis pipeline. This phase implements a deterministic, contract-enforced process that transforms validated input artifacts (`CanonicalInput` from Phase 0) into a structured, semantically enriched policy package (`CanonPolicyPackage`) with complete provenance tracking and constitutional invariant enforcement.

The phase operates through 16 subphases (SP0-SP15) with weight-based execution contracts, producing EXACTLY 60 chunks organized across 10 Policy Areas and 6 Causal Dimensions. This constitutional invariant (60 chunks) is enforced through multiple verification layers and cannot be violated under any circumstances.

---

## 1. Constitutional Invariants

### 1.1 Primary Invariant
**EXACTLY 60 chunks must be produced**: `10 Policy Areas × 6 Causal Dimensions = 60 chunks`

This invariant is:
- **Non-negotiable**: Execution fails if violated
- **Verified at multiple points**: SP4 (specification), SP11 (assembly), SP13 (packaging), Phase 2 entry
- **Enforced by contracts**: `contracts/phase1_constitutional_contract.py`

### 1.2 Secondary Invariants
- **Complete PA×Dimension coverage**: Every (PA, Dimension) pair must have exactly one chunk
- **DAG acyclicity**: Chunk dependency graph must be acyclic
- **Deterministic execution**: Same inputs + controlled randomness → same outputs
- **Complete provenance**: Every chunk traces to source document

---

## 2. Entry Point and Interface

### 2.1 Primary Entry Point
```python
from farfan_pipeline.phases.Phase_one.phase1_20_00_cpp_ingestion import execute_phase_1_with_full_contract

cpp = execute_phase_1_with_full_contract(
    canonical_input: CanonicalInput,
    signal_registry: Optional[QuestionnaireSignalRegistry] = None
) -> CanonPolicyPackage
```

### 2.2 Input Contract (Phase 0 → Phase 1)
- **Type**: `CanonicalInput` (from `farfan_pipeline.phases.Phase_zero.phase0_input_validation`)
- **Preconditions**: See `contracts/phase1_input_contract.py`
  - PRE-01: PDF exists and is readable
  - PRE-02: PDF SHA256 matches provided hash
  - PRE-03: Questionnaire exists and is valid JSON
  - PRE-04: Questionnaire SHA256 matches provided hash
  - PRE-05: Phase 0 validation passed

### 2.3 Output Contract (Phase 1 → Phase 2)
- **Type**: `CanonPolicyPackage` (CPP)
- **Postconditions**: See `contracts/phase1_output_contract.py`
  - POST-01: Exactly 60 chunks produced
  - POST-02: All chunks have valid PA and Dimension assignments
  - POST-03: Chunk graph is acyclic (DAG)
  - POST-04: Complete execution trace (16 entries)
  - POST-05: Quality metrics present
  - POST-06: Schema version CPP-2025.1

---

## 3. Architecture

### 3.1 Subphase Structure (16 Subphases)

| Subphase | Name | Weight | Tier | Description |
|----------|------|--------|------|-------------|
| SP0 | Input Validation | 900 | STANDARD | Validate canonical input integrity |
| SP1 | Language Preprocessing | 2500 | STANDARD | NLP preprocessing, tokenization |
| SP2 | Structural Analysis | 3000 | STANDARD | Document structure extraction |
| SP3 | Knowledge Graph | 4000 | STANDARD | Entity extraction, KG construction |
| SP4 | PA×Dim Grid Specification | 10000 | **CRITICAL** | Define 60-chunk grid |
| SP5 | Causal Extraction | 5000 | HIGH | Extract causal relationships |
| SP6 | Arguments Extraction | 3500 | STANDARD | Extract argumentation structures |
| SP7 | Discourse Analysis | 4500 | STANDARD | Discourse pattern analysis |
| SP8 | Temporal Extraction | 3500 | STANDARD | Extract temporal information |
| SP9 | Causal Integration | 6000 | HIGH | Integrate causal data |
| SP10 | Strategic Integration | 8000 | HIGH | Strategic element integration |
| SP11 | Chunk Assembly | 10000 | **CRITICAL** | Assemble 60 chunks |
| SP12 | SISAS Irrigation | 7000 | HIGH | Signal-based enrichment |
| SP13 | CPP Packaging | 10000 | **CRITICAL** | Package as CPP |
| SP14 | Quality Metrics | 5000 | HIGH | Compute quality metrics |
| SP15 | Integrity Verification | 9000 | HIGH | Verify CPP integrity |

### 3.2 Weight-Based Execution Contract

**Weight Tiers**:
- **CRITICAL** (10000): SP4, SP11, SP13 — Constitutional invariants, immediate abort on failure, 3x timeout
- **HIGH** (5000-9000): SP5, SP9, SP10, SP12, SP14, SP15 — Essential processing, 2x timeout
- **STANDARD** (900-4999): SP0, SP1, SP2, SP3, SP6, SP7, SP8 — Standard processing, 1x timeout

**Failure Behavior**:
- CRITICAL: Immediate abort, no recovery
- HIGH: Graceful degradation with retry
- STANDARD: Best-effort execution

---

## 4. SISAS Integration (Satellital Intelligent Signal Aggregation System)

### 4.1 SISAS Operation Points

SISAS provides signal-based semantic enrichment throughout Phase 1:

| Subphase | SISAS Component | Operation |
|----------|----------------|-----------|
| SP3 | `QuestionnaireSignalRegistry` | Entity importance scoring via pattern matching |
| SP5 | `SignalPack.causal_patterns` | Causal marker detection |
| SP10 | `SignalQualityMetrics` | Priority boosting based on signal coverage |
| **SP12** | `SISAS.semantic_similarity_engine` | **PRIMARY IRRIGATION**: Cross-chunk semantic linking |

### 4.2 SP12 Irrigation Specification

**Input**:
- `chunks`: List[SmartChunk] (60 chunks from SP11)
- `signal_registry`: QuestionnaireSignalRegistry (DI from Factory)
- `similarity_threshold`: float (default: 0.5)

**Output**:
- `irrigation_links`: List[IrrigationLink] — Cross-chunk semantic relationships
- `link_scores`: Dict[Tuple[str, str], float] — Similarity scores per chunk pair
- `coverage_metrics`: SignalCoverageMetrics — Signal coverage statistics

**Verification**: Tests verify presence of these outputs and registry DI

---

## 5. Files and Structure

### 5.1 Core Files

| File | Purpose | Criticality |
|------|---------|-------------|
| `__init__.py` | Module initialization, public API exports | STANDARD |
| `phase1_cpp_ingestion_full.py` | **CANONICAL 16-subphase processor** | **CRITICAL** |
| `cpp_models.py` | CanonPolicyPackage, LegacyChunk dataclasses | CRITICAL |
| `phase1_models.py` | SmartChunk with type-safe enums | CRITICAL |
| `phase1_circuit_breaker.py` | Fault tolerance, graceful failure | HIGH |
| `phase1_dependency_validator.py` | Pre-import validation (Derek Beach, ToC) | HIGH |
| `phase_protocol.py` | Phase interface contracts | HIGH |
| `signal_enrichment.py` | SISAS signal-based enrichment | HIGH |
| `structural.py` | Document structural analysis | STANDARD |
| `FORCING_ROUTE.md` | Execution specification and constraints | HIGH |

### 5.2 Contracts

| Contract | Purpose | Location |
|----------|---------|----------|
| Mission Contract | Weight-based execution specification | `contracts/phase1_mission_contract.py` |
| Input Contract | Phase 0 → Phase 1 preconditions | `contracts/phase1_input_contract.py` |
| Output Contract | Phase 1 → Phase 2 postconditions | `contracts/phase1_output_contract.py` |
| Constitutional Contract | 60-chunk invariant enforcement | `contracts/phase1_constitutional_contract.py` |

### 5.3 Certificates

15 execution certificates for subphases SP0-SP14 are located in `contracts/certificates/`:
- `CERTIFICATE_01_SP0.md` through `CERTIFICATE_15_SP14.md`
- Each certificate specifies subphase obligations, verification criteria, and contract authority

---

## 6. Transversal Dependencies

### 6.1 Upstream (Phase 0)
- **Module**: `farfan_pipeline.phases.Phase_zero.phase0_input_validation`
- **Interface**: `CanonicalInput` dataclass
- **Validation**: Phase 0 validation gates

### 6.2 Cross-Cutting Infrastructure
- **SISAS**: `cross_cutting_infrastructure/irrigation_using_signals/SISAS/signal_registry.py`
  - `QuestionnaireSignalRegistry` for signal-based enrichment
  - DI chain: Factory → Orchestrator → Phase 1

### 6.3 Downstream (Phase 2)
- **Module**: `farfan_pipeline.phases.Phase_two/` (Carver, Executor Config)
- **Interface**: `CanonPolicyPackage` dataclass
- **Validation**: Phase 2 entry gates verify 60-chunk invariant

---

## 7. Testing and Verification

### 7.1 Test Files

| Test File | Purpose |
|-----------|---------|
| `tests/test_phase1_constitutional_invariant.py` | Verify 60-chunk invariant, PA×Dim coverage, DAG acyclicity |
| `tests/test_phase1_sisas_integration.py` | Verify SP12 outputs and signal registry DI |
| `tests/test_phase1_orchestrator_handoff.py` | Verify Phase 2 consumes 60-CPP payload |
| `tests/test_phase1_naming_and_purge.py` | Enforce naming rules and purge verification |
| `tests/test_phase1_contracts_and_certificates.py` | Verify contracts and certificates presence |

### 7.2 Verification Commands

```bash
# Import verification
python -c "from farfan_pipeline.phases.Phase_one.phase1_20_00_cpp_ingestion import execute_phase_1_with_full_contract; print('OK')"

# Purge verification (should return empty)
find . -name "*phase1*" -o -name "*Phase_one*" -o -name "*phase_one*" | grep -v "phase_1_cpp_ingestion"

# Test execution
pytest tests/test_phase1*.py -v
```

---

## 8. Success Criteria

- [x] Canonical path enforced: `src/farfan_pipeline/phases/Phase_one/`
- [x] Naming rules enforced: snake_case, phase1_ prefix, explicit extensions
- [x] Legacy Phase_one folder deleted
- [x] Root-level Phase 1 MDs and scripts deleted
- [x] Contracts present: 4 contract modules
- [x] Certificates present: 15 certificate files
- [x] Orchestrator imports from canonical path
- [x] SISAS verification implemented
- [x] 60-chunk assertion enforced in orchestrator
- [x] Tests verify constitutional invariant
- [ ] CI passes with all tests green

---

## 9. References

- **Execution Specification**: `FORCING_ROUTE.md`
- **Contracts**: `contracts/` directory
- **Certificates**: `contracts/certificates/` directory
- **F.A.R.F.A.N Pipeline**: Main repository README
- **Phase 0 Documentation**: `farfan_pipeline/phases/Phase_zero/`
- **Phase 2 Documentation**: `farfan_pipeline/phases/Phase_two/`

---

**Document Version**: 1.0.0  
**Schema Version**: CPP-2025.1  
**Last Reviewed**: 2025-12-18



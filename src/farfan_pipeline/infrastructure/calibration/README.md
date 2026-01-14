# Calibration Layer Architecture Documentation

## Overview

This document describes the calibration layer infrastructure implementing the F.A.R.F.A.N epistemic calibration system with **unified single-regime architecture**.

**Schema Version:** 3.0.0
**Last Updated:** 2026-01-14

## Purpose

The calibration layer provides foundational types and data structures for calibration within the F.A.R.F.A.N epistemic regime. It operates **within** the existing epistemic framework (N1-EMP, N2-INF, N3-AUD), not parallel to it.

## Unified Calibration Regime (NEW in v3.0)

**ARCHITECTURAL PRINCIPLE:** Single regime with distinct calibration layer that feeds manifests to both Phase 1 (ingestion) and Phase 2 (computation), sharing taxonomies and invariants.

### Key Features

1. **Phase 1 Calibration (UoA-First)**
   - Tight bounds derived from UoA characteristics
   - UoA-derived priors based on complexity score
   - Ingestion-only defaults (chunk size, coverage target)
   - Short validity windows (30-180 days, default 90 days)

2. **Phase 2 Calibration (Interaction-Aware)**
   - Role→layer activation via ROLE_LAYER_REQUIREMENTS matrix
   - Method-binding validation before orchestrator decisions
   - Veto thresholds adjusted for interaction density
   - Fusion rules enforced via TYPE-specific prohibited operations
   - Longer validity windows (180-730 days, default 365 days)

3. **Granularity Requirements**
   - Per-method docstrings with "Unit of Analysis Requirements"
   - Epistemic level metadata (N1/N2/N3)
   - Fusion strategy documentation
   - Contract-level verbosity with canonical variable commentary
   - Each field anchored to single invariant source with cross-references

4. **Interaction Governance**
   - Explicit role/layer matrices (ROLE_LAYER_REQUIREMENTS)
   - Prohibited operations lists per TYPE
   - Bounded fusion strategies (multiplicative fusion in [0.01, 10.0])
   - Mandatory method_binding_validator checks before composition

5. **Auditability**
   - Immutable calibration manifests with deterministic SHA-256 hashes
   - Rationale and evidence links for all parameters
   - Drift reports with severity classification
   - INV-CAL-00x auditor specifications (21+ invariants)
   - Grep-based enforcement for missing UoA documentation

6. **Sensitivity Factors**
   - UoA signals (complexity score, fiscal context, policy area count)
   - Cognitive cost (higher cost → stronger priors, stricter veto)
   - Interaction density caps per TYPE
   - Veto thresholds per TYPE
   - Validity windows with expiry tracking
   - Coverage/dispersion/contradiction penalties

## Architecture

### Module Structure

```
src/farfan_pipeline/infrastructure/calibration/
├── __init__.py                       # Public API (Facade pattern)
├── calibration_core.py               # Frozen core types with invariants
├── calibration_types.py              # Orchestrator API types (LayerId, CalibrationResult)
├── calibration_regime.py             # ** NEW ** Unified single-regime architecture
├── calibration_manifest.py           # Audit trail (Memento pattern)
├── calibration_auditor.py            # N3-AUD veto gate (Specification pattern)
├── cognitive_cost.py                 # ** NEW ** Cognitive cost estimation
├── interaction_density.py            # ** NEW ** Interaction density tracking
├── drift_detector.py                 # ** NEW ** Comprehensive drift detection
├── inv_specifications.py             # ** NEW ** INV-CAL-00x specifications
├── type_defaults.py                  # TYPE-specific defaults (Flyweight cached)
├── unit_of_analysis.py               # Municipal unit characterization
├── ingestion_calibrator.py           # N1-EMP calibration (Strategy pattern)
├── phase2_calibrator.py              # N2-INF calibration (TYPE constraints)
├── method_binding_validator.py       # Chain of Responsibility validation
├── interaction_governor.py           # Bounded fusion, veto cascades
├── fact_registry.py                  # Deduplication with verbosity control
├── decorators.py                     # Calibration decorators
├── parameters.py                     # Runtime parameter loading
├── canonical_specs.py                # Specification implementations
└── README.md                         # This documentation

src/farfan_pipeline/phases/Phase_2/
├── phase2_60_04_calibration_policy.py              # Policy facade
└── phase2_95_03_executor_calibration_integration.py # Executor integration
```

### Wiring Diagram

```
infrastructure/calibration/calibration_core.py     ← Frozen types (CalibrationParameter, CalibrationLayer)
infrastructure/calibration/type_defaults.py        ← TYPE-specific bounds (Flyweight)
infrastructure/calibration/ingestion_calibrator.py ← N1-EMP calibration
infrastructure/calibration/phase2_calibrator.py    ← N2-INF calibration, TYPE constraints
infrastructure/calibration/calibration_manifest.py ← Audit trail
infrastructure/calibration/calibration_auditor.py  ← N3-AUD veto gate
infrastructure/calibration/interaction_governor.py ← Bounded fusion
infrastructure/calibration/fact_registry.py        ← Deduplication
            ↓
phases/Phase_two/phase2_60_04_calibration_policy.py ← Policy facade (CalibrationOrchestrator)
```

## System Capabilities

### 1. Calibration Within Epistemic Regime
- Calibration is executed **within** the epistemic regime, not as a parallel system
- Frozen, immutable dataclasses with explicit invariants
- All parameters subject to N3-AUD verification

### 2. TYPE-Specific Defaults and Prohibitions
- Centralized via `type_defaults.py`, cached via Flyweight pattern
- Read from canonical source: `contratos_clasificados.json`
- Explicit ratio bounds, prior strength ranges, veto thresholds per TYPE

### 3. Ingestion and Phase-2 Calibration
- **Ingestion (N1-EMP):** Derives parameters from unit-of-analysis via bounded strategies
- **Phase-2 (N2-INF):** Enforces TYPE fusion strategy alignment and validator gating

### 4. Manifest Hashing and Cryptographic Attestation
- Deterministic SHA-256 hashing of calibration layers
- Optional Ed25519 signatures for cryptographic attestation
- Drift auditing detects design-runtime misalignment

### 5. Interaction Governance
- Acyclicity checks for dependency graphs (INV-INT-001)
- Bounded multiplicative fusion [0.01, 10.0] (INV-INT-002)
- Specificity-ordered veto cascades (INV-INT-003)
- Level inversion detection (INV-INT-004)

### 6. Fact Registry
- Canonical fact representation with hash-based deduplication
- Verbosity threshold >= 0.90 enforced
- Full provenance preservation

## Invariants Enforced

### Core Calibration Invariants (INV-CAL-001 to INV-CAL-010)

| Invariant ID | Description | Enforcement | Grep Pattern |
|--------------|-------------|-------------|--------------|
| INV-CAL-001 | Prior strength within TYPE-specific bounds | `CalibrationParameter.__post_init__` | `INV-CAL-001.*prior_strength.*bounds` |
| INV-CAL-002 | Veto threshold within TYPE-specific bounds | `CalibrationParameter.__post_init__` | `INV-CAL-002.*veto_threshold.*bounds` |
| INV-CAL-003 | No prohibited operations in fusion strategy | `Phase2Calibrator.calibrate` | `INV-CAL-003.*prohibited.*operations` |
| INV-CAL-004 | Validity window ≤ UoA.data_validity_days | `UnifiedCalibrationRegime._create_phase1_layer` | `INV-CAL-004.*validity.*UoA` |
| INV-CAL-005 | Cognitive cost factored into prior strength | `UnifiedCalibrationRegime._create_phase1_layer` | `INV-CAL-005.*cognitive.*cost.*prior` |
| INV-CAL-006 | Interaction density capped per TYPE | `InteractionDensityTracker.compute_density` | `INV-CAL-006.*interaction.*density.*cap` |
| INV-CAL-007 | Manifests immutable and deterministically hashed | `UnifiedCalibrationManifest.__post_init__` | `INV-CAL-007.*immutable.*manifest.*hash` |
| INV-CAL-008 | Drift reports generated on parameter changes | `DriftDetector.detect_drift` | `INV-CAL-008.*drift.*report` |
| INV-CAL-009 | Coverage and dispersion penalties applied | `DriftDetector._check_coverage_penalty` | `INV-CAL-009.*coverage.*dispersion.*penalty` |
| INV-CAL-010 | Contradiction penalties enforced | `DriftDetector._detect_contradictions` | `INV-CAL-010.*contradiction.*penalty` |

### Unit of Analysis Invariants (INV-CAL-011 to INV-CAL-012)

| Invariant ID | Description | Enforcement |
|--------------|-------------|-------------|
| INV-CAL-011 | UoA complexity score ∈ [0.0, 1.0] | `UnitOfAnalysis.complexity_score` |
| INV-CAL-012 | Municipality code matches pattern [A-Z]{2,6}-[0-9]{4,12} | `UnitOfAnalysis.__post_init__` |

### Method Binding Invariants (INV-CAL-013 to INV-CAL-015)

| Invariant ID | Description | Enforcement |
|--------------|-------------|-------------|
| INV-CAL-013 | N1:N2:N3 ratios match TYPE requirements | `MethodBindingValidator._validate_layer_ratios` |
| INV-CAL-014 | Mandatory patterns present per TYPE | `MethodBindingValidator._validate_mandatory_patterns` |
| INV-CAL-015 | Dependency chain validity (N2.requires ⊆ N1.provides) | `MethodBindingValidator._validate_dependency_chain` |

### Interaction Governance Invariants (INV-CAL-016 to INV-CAL-018)

| Invariant ID | Description | Enforcement |
|--------------|-------------|-------------|
| INV-CAL-016 | Acyclic dependency graph (DAG) | `CycleDetector.find_cycles` |
| INV-CAL-017 | No level inversions (N3 cannot depend on N2) | `LevelInversionDetector.detect_inversions` |
| INV-CAL-018 | Bounded multiplicative fusion [0.01, 10.0] | `bounded_multiplicative_fusion` |

### Documentation Invariants (INV-CAL-019 to INV-CAL-021)

| Invariant ID | Description | Enforcement |
|--------------|-------------|-------------|
| INV-CAL-019 | UoA requirements documented | Docstrings (grep enforcement) |
| INV-CAL-020 | Epistemic level documented | Docstrings (grep enforcement) |
| INV-CAL-021 | Fusion strategy documented | Docstrings (grep enforcement) |

### Legacy Invariants (Preserved)

| Invariant ID | Description | Enforcement |
|--------------|-------------|-------------|
| INV-CAL-FREEZE-001 | All calibration parameters immutable post-construction | `frozen=True` dataclasses |
| INV-CAL-REGIME-001 | Calibration operates within epistemic regime | Architecture design |
| INV-CAL-AUDIT-001 | All parameters subject to N3-AUD verification | CalibrationAuditor |
| INV-CAL-HASH-001 | Canonical JSON serialization for deterministic hashing | `_canonical_json()` |
| INV-CAL-TZ-001 | All timestamps timezone-aware UTC | `__post_init__` validation |
| INV-CAL-SIG-001 | Optional Ed25519 signatures for attestation | `CalibrationLayer.sign()` |
| INV-INT-001 | Dependency graph must be acyclic (DAG) | CycleDetector |
| INV-INT-002 | Multiplicative fusion bounded [0.01, 10.0] | `bounded_multiplicative_fusion()` |
| INV-INT-003 | Veto cascade respects specificity ordering | VetoCoordinator |
| INV-INT-004 | No level inversions (N3 cannot depend on N2) | LevelInversionDetector |
| INV-FACT-001 | Every fact has exactly one canonical representation | CanonicalFactRegistry |
| INV-FACT-002 | Duplicate content triggers provenance logging | DuplicateRecord |
| INV-FACT-003 | Verbosity ratio >= 0.90 | `validate_verbosity()` |

### Grep Enforcement

To verify invariant coverage:
```bash
# Check all INV-CAL references
grep -r "INV-CAL-" src/farfan_pipeline/infrastructure/calibration/ | wc -l

# Check for missing UoA docstrings
grep -L "Unit of Analysis Requirements" src/farfan_pipeline/infrastructure/calibration/*.py

# Verify epistemic level documentation
grep -c "Epistemic Level:" src/farfan_pipeline/infrastructure/calibration/*.py

# Generate automated enforcement script
python -c "from farfan_pipeline.infrastructure.calibration import generate_grep_enforcement_script; print(generate_grep_enforcement_script())" > scripts/enforce_invariants.sh
chmod +x scripts/enforce_invariants.sh
./scripts/enforce_invariants.sh
```

## Success Criteria

1. **Calibration layers build successfully** with all required parameters, invariants pass, manifest hashing deterministic
2. **TYPE validator passes:** layer ratios, mandatory patterns, prohibited operations, dependency chains satisfied
3. **Auditor passes:** prior strength and veto thresholds within bounds; prohibited operations absent
4. **Interaction governor reports no fatal cycles;** fusion outputs within bounds; veto cascade effective
5. **Fact registry maintains verbosity ≥ 0.90** with correct deduplication

## Failure Modes

| Mode | Description | Detection |
|------|-------------|-----------|
| FM-001 | Out-of-bounds parameter values | `__post_init__` ValidationError |
| FM-002 | Missing rationale or evidence | `__post_init__` ValidationError |
| FM-003 | Timezone-naive datetime | `__post_init__` ValidationError |
| FM-004 | TYPE ratio/fusion strategy mismatch | MethodBindingValidator FATAL |
| FM-005 | Prohibited operations detected | CalibrationAuditor veto |
| FM-006 | Dependency cycles in graph | InteractionGovernor FATAL |
| FM-007 | Level inversions | InteractionGovernor WARNING |
| FM-008 | Multiplicative overflow/underflow | bounded_multiplicative_fusion clamping |
| FM-009 | Manifest non-determinism | Hash mismatch detection |
| FM-010 | Signature verification failure | IntegrityError |

## Core Types

### CalibrationPhase (Enum)
Defines the phase in which calibration applies:
- `INGESTION` - Data ingestion phase (N1-EMP)
- `PHASE_2_COMPUTATION` - Phase 2 computation (N2-INF)
- `PHASE_3_AGGREGATION` - Phase 3 aggregation

### ClosedInterval (frozen dataclass)
Closed interval [lower, upper] with algebraic operations:
- `contains(value)` - Check membership
- `intersect(other)` - Compute intersection
- `width()` / `midpoint()` - Interval metrics

### CalibrationParameter (frozen dataclass)
Single calibration parameter with full provenance:
- `name`, `value`, `unit`, `bounds`
- `rationale` - Non-empty justification
- `evidence` - EvidenceReference with path, commit SHA, description
- `calibrated_at`, `expires_at` - Timezone-aware UTC timestamps
- `validity_status_at(check_time)` - Returns ValidityStatus enum

### CalibrationLayer (frozen dataclass)
Complete calibration configuration:
- `unit_of_analysis_id` - Pattern: [A-Z]{2,6}-[0-9]{4,12}
- `phase`, `contract_type_code`
- `parameters` - Immutable tuple of CalibrationParameter
- `manifest_hash()` - SHA-256 of canonical representation
- `sign(private_key, key_id)` - Ed25519 signature
- `verify_signature(public_key)` - Verification

### ContractTypeDefaults (frozen dataclass)
TYPE-specific calibration bounds:
- `epistemic_ratios` - EpistemicLayerRatios (N1/N2/N3)
- `veto_threshold`, `prior_strength` - ClosedInterval bounds
- `permitted_operations`, `prohibited_operations` - frozenset

## Design Patterns

| Pattern | Implementation | Purpose |
|---------|---------------|---------|
| Flyweight | `@lru_cache` on `get_type_defaults()` | Prevent redundant configuration objects |
| Facade | `__init__.py` public API | Single entry point |
| Strategy | CalibrationStrategy protocol | Pluggable calibration algorithms |
| Builder | ManifestBuilder | Incremental manifest construction |
| Memento | CalibrationManifest | Immutable audit trail |
| Specification | CalibrationSpecification protocol | Composable audit rules |
| Chain of Responsibility | MethodBindingValidator | Sequential validation |
| Mediator | InteractionGovernor | Coordinate method interactions |

## Usage Examples

### Full Pipeline Calibration

```python
from farfan_pipeline.phases.Phase_two.phase2_60_04_calibration_policy import (
    CalibrationOrchestrator,
)
from farfan_pipeline.infrastructure.calibration import (
    UnitOfAnalysis, MunicipalityCategory, FiscalContext,
    MethodBindingSet, MethodBinding,
)

# Create unit of analysis
unit = UnitOfAnalysis(
    municipality_code="05001",
    municipality_name="Medellín",
    department_code="05",
    population=2_500_000,
    total_budget_cop=10_000_000_000_000,
    category=MunicipalityCategory.CATEGORIA_ESPECIAL,
    sgp_percentage=30.0,
    own_revenue_percentage=70.0,
    fiscal_context=FiscalContext.HIGH_CAPACITY,
    plan_period_start=2024,
    plan_period_end=2027,
    policy_area_codes=frozenset({"PA01", "PA02", "PA03"}),
)

# Create method bindings
binding_set = MethodBindingSet(
    contract_id="Q001",
    contract_type_code="TYPE_A",
    bindings={
        "N1-EMP": [MethodBinding(...)],
        "N2-INF": [MethodBinding(...)],
        "N3-AUD": [MethodBinding(...)],
    }
)

# Orchestrate full calibration
orchestrator = CalibrationOrchestrator(evidence_commit="abc123...")
manifest, audit_result = orchestrator.calibrate_full_pipeline(
    unit=unit,
    contract_type_code="TYPE_A",
    binding_set=binding_set,
)

if audit_result.passed:
    print(f"Calibration successful: {manifest.compute_hash()[:12]}...")
else:
    print(f"Calibration vetoed: {audit_result.violations}")
```

### Check Prohibited Operations

```python
from farfan_pipeline.infrastructure.calibration import is_operation_prohibited

# TYPE_E prohibits all forms of averaging
assert is_operation_prohibited("TYPE_E", "weighted_mean") == True
assert is_operation_prohibited("TYPE_E", "average") == True

# TYPE_D permits weighted_mean for financial aggregation
assert is_operation_prohibited("TYPE_D", "weighted_mean") == False
```

### Bounded Multiplicative Fusion

```python
from farfan_pipeline.infrastructure.calibration import bounded_multiplicative_fusion

# Prevents numerical explosion
result = bounded_multiplicative_fusion([2.0, 3.0, 4.0])  # 24.0 -> clamped to 10.0
assert result == 10.0

# Prevents numerical collapse
result = bounded_multiplicative_fusion([0.001, 0.002, 0.003])  # -> clamped to 0.01
assert result == 0.01
```

## Verification Strategy

### Static Analysis
- `mypy --strict` typing verification
- `py_compile` parser checks
- Explicit invariant assertions in `__post_init__`

### Dynamic Validation
- Validator chains (MethodBindingValidator)
- Auditor specifications (CalibrationAuditor)
- Interaction governor tests
- Manifest hash checks
- Optional signature verification

### Provenance
- Evidence paths pinned to specific commits
- Logs carry contract and unit identifiers
- Full audit trail in CalibrationManifest

### Sensitivity
- Ingestion strategies clamp within declared bounds
- Phase-2 uses TYPE midpoints as defaults
- Drift audit monitors coverage and credible interval width

## What This System Accomplishes

1. **Converts calibration from ad hoc to rigorously governed** - Provenance-pinned, auditable contracts
2. **Eliminates ambiguity and runtime drift** - Frozen decisions with explicit invariants
3. **Aligns with epistemic roles and TYPE constraints** - Prevents category errors and interaction pathologies
4. **Ensures reproducibility, integrity, and defensibility** - Hashing, signatures, validator chains, specification-driven audits

## References

- **Specification:** JF1-CAL-ARCH-2026-01-02
- **Epistemic Foundation:** `src/farfan_pipeline/phases/Phase_two/epistemological_assets/contratos_clasificados.json`
- **Phase 2 Architecture:** `src/farfan_pipeline/phases/Phase_two/`
- **Policy Facade:** `src/farfan_pipeline/phases/Phase_two/phase2_60_04_calibration_policy.py`

## Version History

- **2.0.0** (2026-01-05): Full system integration
  - CalibrationOrchestrator facade
  - Complete wiring to Phase 2 policy layer
  - Interaction governor integration
  - Fact registry integration
  - Comprehensive documentation
  
- **1.0.0** (2026-01-02): Initial implementation
  - Core types (CalibrationBounds, CalibrationParameter, CalibrationLayer)
  - Type-specific defaults
  - Prohibited operations enforcement

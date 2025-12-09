# ⚠️ SENSITIVE - CALIBRATION SYSTEM CRITICAL ⚠️

## Security Classification

**FOLDER**: `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/`

**CLASSIFICATION**: SENSITIVE - CALIBRATION SYSTEM CRITICAL

**LABEL**: CONFIG_GOVERNANCE_STRICT_FOLDERIZATION

## Authority

- **Cohort**: COHORT_2024
- **Wave**: REFACTOR_WAVE_2024_12
- **Implementation Wave**: GOVERNANCE_WAVE_2024_12_07
- **Authority**: Doctrina SIN_CARRETA
- **Compliance**: SUPERPROMPT Three-Pillar Calibration System

## Purpose

This folder contains the **core calibration system** for F.A.R.F.A.N., implementing the mathematical foundation for method quality assessment. Changes to these files directly impact:

1. **Method Selection**: Which analysis methods are trusted for policy evaluation
2. **Score Computation**: How calibration scores are calculated via Choquet integral fusion
3. **Certificate Generation**: Cryptographic evidence of calibration validity
4. **Governance Compliance**: Auditability and traceability of method quality

## Critical Components

### CalibrationOrchestrator

**File**: `COHORT_2024_calibration_orchestrator.py`

The orchestrator is the **primary entry point** for calibration. It:
- Determines required layers based on method role
- Computes layer scores from evidence artifacts
- Applies Choquet integral fusion with interaction terms
- Validates boundedness constraints
- Generates cryptographic certificates

**Impact**: Changes affect ALL method calibrations across the system.

### Fusion Weights

**Files**: 
- `COHORT_2024_fusion_weights.json`
- `fusion_weights.json`

Defines the Choquet integral parameters:
- Linear weights `a_ℓ` for each layer
- Interaction weights `a_ℓk` for layer pairs

**Constraint**: `Σ(a_ℓ) + Σ(a_ℓk) = 1.0` (normalization)

**Impact**: Changes alter the relative importance of calibration dimensions.

### Layer Assignment

**File**: `COHORT_2024_layer_assignment.py`

Defines `LAYER_REQUIREMENTS` mapping method roles to required calibration layers.

**Impact**: Changes affect which layers are evaluated for each method type.

### Intrinsic Calibration

**Files**:
- `COHORT_2024_intrinsic_calibration.json`
- `COHORT_2024_intrinsic_calibration_rubric.json`

Defines base layer evaluation criteria and scoring rubrics.

**Impact**: Changes affect code quality assessment standards.

### Method Compatibility

**File**: `COHORT_2024_method_compatibility.json`

Defines contextual layer scores (question, dimension, policy alignment) per method.

**Impact**: Changes affect method-context fitness scores.

## Access Control

### Who Can Modify

1. **Calibration System Administrators** (write access)
2. **Governance Committee** (approval authority)
3. **Audit Team** (read-only access for verification)

### Who CANNOT Modify

1. Pipeline developers (must use API, not modify calibration logic)
2. Method implementers (can't adjust their own calibration scores)
3. External contributors (no direct access)

## Change Management Protocol

### Required Steps for ANY Change

1. **Mathematical Validation**
   - Prove normalization: `Σ(a_ℓ) + Σ(a_ℓk) = 1.0`
   - Verify boundedness: `Cal(I) ∈ [0,1]` for all input combinations
   - Check monotonicity: `∂Cal/∂x_ℓ ≥ 0` for all layers

2. **Regression Testing**
   - Run full test suite: `pytest tests/test_calibration_orchestrator.py -v`
   - Validate against canonical inventory
   - Check certificate generation consistency

3. **Governance Approval**
   - Submit change request to COHORT_2024 governance
   - Document rationale and mathematical proof
   - Obtain approval signature

4. **Audit Trail Update**
   - Update `COHORT_MANIFEST.json` with change record
   - Increment version in affected files
   - Generate evidence trace in `evidence_traces/`

5. **Certificate Regeneration**
   - Regenerate all method certificates with new parameters
   - Archive old certificates for audit trail
   - Update `canonical_method_inventory.json`

### Prohibited Changes

❌ **NEVER**:
- Modify fusion weights without mathematical proof of normalization
- Change layer requirements without governance approval
- Alter certificate generation logic without audit notification
- Remove or rename files without migration plan
- Bypass boundedness validation
- Skip regression tests before deployment

## Sensitivity Rationale

### Why SENSITIVE?

1. **Trust Foundation**: Calibration determines which methods are trusted for policy analysis
2. **Algorithmic Transparency**: Changes must be traceable and auditable
3. **Regulatory Compliance**: Calibration system is subject to governance review
4. **Certificate Validity**: Cryptographic certificates depend on stable algorithm
5. **Reproducibility**: Scientific reproducibility requires stable calibration parameters

### What Could Go Wrong?

**Scenario 1: Unvalidated Weight Change**
- **Risk**: Fusion weights no longer sum to 1.0
- **Impact**: Final scores become unbounded, breaking [0,1] constraint
- **Consequence**: Invalid calibration certificates, method selection failure

**Scenario 2: Layer Requirement Modification**
- **Risk**: Critical layers omitted for a method role
- **Impact**: Incomplete calibration assessment
- **Consequence**: Unqualified methods pass calibration

**Scenario 3: Certificate Logic Alteration**
- **Risk**: Certificate generation becomes non-deterministic
- **Impact**: Same inputs produce different certificates
- **Consequence**: Audit trail corruption, non-reproducibility

**Scenario 4: Intrinsic Score Inflation**
- **Risk**: Base scores artificially inflated
- **Impact**: Poor-quality methods receive high calibration scores
- **Consequence**: Trust erosion, incorrect policy analysis

## Monitoring & Alerts

### Automated Checks

1. **Pre-commit Hook**: Validate JSON schema and normalization
2. **CI/CD Pipeline**: Run full calibration test suite
3. **Runtime Validation**: Boundedness checks on every calibration
4. **Audit Logger**: Record all calibration operations with certificate IDs

### Alert Triggers

- ⚠️ Fusion weights fail normalization check
- ⚠️ Calibration score outside [0.0, 1.0] bounds
- ⚠️ Certificate hash collision detected
- ⚠️ Layer requirement lookup failure
- ⚠️ JSON file schema validation failure

## Incident Response

### If Calibration Failure Detected

1. **STOP**: Immediately halt method selection
2. **ISOLATE**: Quarantine affected calibration results
3. **NOTIFY**: Alert governance committee and audit team
4. **DIAGNOSE**: Run calibration diagnostics and trace failure
5. **ROLLBACK**: Revert to last known-good calibration state
6. **REMEDIATE**: Fix root cause with full validation protocol
7. **AUDIT**: Generate incident report and evidence trace

### Contact Points

- **Calibration System Admin**: [system_admin@farfan.gov]
- **Governance Committee**: [governance@farfan.gov]
- **Audit Team**: [audit@farfan.gov]
- **Emergency Escalation**: [emergency@farfan.gov]

## Folder Inventory

### Python Modules (Sensitive)

- `COHORT_2024_calibration_orchestrator.py` - **CRITICAL**: Main orchestrator
- `COHORT_2024_layer_assignment.py` - **CRITICAL**: Role-to-layer mapping
- `COHORT_2024_intrinsic_scoring.py` - Base layer computation
- `COHORT_2024_unit_layer.py` - PDT quality evaluation
- `COHORT_2024_meta_layer.py` - Governance evaluation
- `COHORT_2024_chain_layer.py` - Wiring quality evaluation
- `COHORT_2024_congruence_layer.py` - Contextual alignment
- `validate_fusion_weights.py` - Weight validation utilities

### JSON Configuration (Sensitive)

- `COHORT_2024_fusion_weights.json` - **CRITICAL**: Choquet parameters
- `fusion_weights.json` - **CRITICAL**: Fallback fusion parameters
- `COHORT_2024_intrinsic_calibration.json` - Base layer rubric
- `COHORT_2024_method_compatibility.json` - Contextual scores
- `COHORT_2024_canonical_method_inventory.json` - Method registry

### Documentation (Sensitive)

- `COHORT_2024_calibration_orchestrator_README.md` - API documentation
- `COHORT_2024_calibration_orchestrator_example.py` - Usage examples
- `SENSITIVE_CRITICAL_SYSTEM.md` - **THIS FILE**: Security classification

## Compliance Checkpoints

### Before Committing Code

- [ ] Mathematical validation complete (normalization, boundedness, monotonicity)
- [ ] All tests pass: `pytest tests/test_calibration_orchestrator.py -v`
- [ ] Governance approval obtained (if changing parameters)
- [ ] Version incremented in affected files
- [ ] COHORT_MANIFEST.json updated with change record
- [ ] Evidence trace generated
- [ ] Certificate regeneration plan documented

### Before Deployment

- [ ] Full regression suite passes
- [ ] Audit team notified
- [ ] Rollback plan prepared
- [ ] Monitoring alerts configured
- [ ] Incident response team briefed

## Audit Trail

All calibration operations are logged with:
- Method ID
- Role and layer requirements
- Layer scores (all 8 layers)
- Fusion breakdown (linear + interaction)
- Final score and validation result
- Certificate ID and hash
- Timestamp (UTC ISO 8601)
- Cohort metadata

Logs are stored in `evidence_traces/` and are **immutable** after generation.

## References

### Mathematical Foundation

- **Document**: `mathematical_foundations_capax_system.md`
- **Fusion Formula**: `Cal(I) = Σ(a_ℓ · x_ℓ) + Σ(a_ℓk · min(x_ℓ, x_k))`
- **Constraints**: See `COHORT_2024_fusion_weights.json` metadata

### Governance Documents

- **SUPERPROMPT**: Three-Pillar Calibration System specification
- **Doctrina SIN_CARRETA**: Governance authority document
- **COHORT_MANIFEST.json**: Migration and change audit trail

### Related Systems

- **Method Registry**: `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/method_registry.py`
- **PDT Structure**: `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/pdt_structure.py`
- **Meta Layer**: `src/orchestration/meta_layer.py`

---

**⚠️ WARNING**: Unauthorized modification of this calibration system may result in:
- Invalid method quality assessments
- Broken policy analysis pipeline
- Governance compliance violations
- Audit trail corruption
- Certificate invalidity

**All changes must follow the change management protocol above.**

---

**Document Version**: 1.0.0  
**Last Updated**: 2024-12-15  
**Authority**: Doctrina SIN_CARRETA  
**Classification**: SENSITIVE - CALIBRATION SYSTEM CRITICAL

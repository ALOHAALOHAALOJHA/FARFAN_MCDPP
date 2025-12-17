# CONTRACT MANIFEST v1.0

**Role**: Canonical Contract Enforcer  
**Purpose**: Non-negotiable specification for F.A.R.F.A.N refactoring  
**Authority**: This document defines what is canonical; code is derivative  
**Created**: 2025-12-13  
**Status**: BINDING - No deviations permitted without manifest amendment

---

## 1. CANONICAL IDENTIFIERS (Source of Truth)

### 1.1 Dimensions (D1-D6)
Source: `canonic_questionnaire_central/questionnaire_monolith.json` → `canonical_notation.dimensions`

| Code | Canonical ID | Name | Label |
|------|--------------|------|-------|
| D1 | DIM01 | INSUMOS | Diagnóstico y Recursos |
| D2 | DIM02 | ACTIVIDADES | Diseño de Intervención |
| D3 | DIM03 | PRODUCTOS | Productos y Outputs |
| D4 | DIM04 | RESULTADOS | Resultados y Outcomes |
| D5 | DIM05 | IMPACTOS | Impactos de Largo Plazo |
| D6 | DIM06 | CAUSALIDAD | Teoría de Cambio |

**Invariant [INV-DIM-001]**: All dimension references MUST use canonical ID (DIM01-DIM06), NOT legacy codes (D1-D6) in internal logic.

### 1.2 Policy Areas (PA01-PA10)
Source: `canonic_questionnaire_central/questionnaire_monolith.json` → `canonical_notation.policy_areas`  
Mapping: `policy_area_mapping.json`

| Legacy ID | Canonical ID | Canonical Name | Source of Truth |
|-----------|--------------|----------------|-----------------|
| P1 | PA01 | Derechos de las mujeres e igualdad de género | monolith |
| P2 | PA02 | Prevención de la violencia y protección de la población | monolith |
| P3 | PA03 | Ambiente sano, cambio climático, prevención y atención a desastres | monolith |
| P4 | PA04 | Derechos económicos, sociales y culturales | monolith |
| P5 | PA05 | Derechos de las víctimas y construcción de paz | monolith |
| P6 | PA06 | Derecho al buen futuro de la niñez, adolescencia, juventud | monolith |
| P7 | PA07 | Tierras y territorios | monolith |
| P8 | PA08 | Líderes y defensores de derechos humanos | monolith |
| P9 | PA09 | Crisis de derechos de personas privadas de la libertad | monolith |
| P10 | PA10 | Migración transfronteriza | monolith |

**Invariant [INV-PA-001]**: Legacy P# identifiers MUST be canonicalized at API boundary. Internal code MUST use PA## format only.

### 1.3 Questions (Q001-Q030 → Q001-Q300)
Source: `canonic_questionnaire_central/questionnaire_monolith.json` → `blocks.micro_questions`  
Base: 30 questions (Q001-Q030)  
Expanded: 30 questions × 10 policy areas = 300 contracts (Q001-Q300)

**Structure**: `Q###` where ### is zero-padded (001-300)

**Invariant [INV-Q-001]**: Question IDs MUST be zero-padded 3-digit integers. Base slot references use D#-Q# format but expand to full Q### for contracts.

### 1.4 Base Slots (D#-Q# Pattern)
Structure: `D{dimension_number}-Q{base_question_number}`  
Example: `D1-Q1` (Dimension 1, Base Question 1)  
Total Base Slots: 6 dimensions × 30 base questions = 180 theoretical slots  
Actual Used: As defined in `questionnaire_monolith.json.blocks.micro_questions`

**Invariant [INV-SLOT-001]**: Base slots are logical groupings only. Execution happens at Q### level (policy-area-specific contracts).

---

## 2. PARAMETER CLASSIFICATION (Quantitative vs Qualitative)

### 2.1 Quantitative Parameters
**Definition**: Numeric values used in computation, scoring, thresholds, priors, weights.

**Authoritative Source**: MUST be declared in one of:
1. `executor_configurable_parameters.json` (runtime configurable)
2. Executor contract JSON (`*.v3.json`) → `scoring_parameters` or `thresholds`
3. `canonic_questionnaire_central/questionnaire_monolith.json` (canonical defaults)

**Examples**:
- Scoring thresholds: 0.85 (excellent), 0.70 (good), 0.55 (adequate)
- Bayesian priors: α=2, β=5 for Beta distributions
- Weights: cluster_weights, dimension_weights
- Statistical: confidence intervals, p-values, significance levels

**Forbidden**: Hardcoded numeric literals in `.py` files for thresholds/weights/priors.

**Invariant [INV-QUANT-001]**: All quantitative parameters MUST be traceable to a JSON configuration file. No magic numbers in code.

### 2.2 Qualitative Parameters
**Definition**: Non-numeric configuration that affects logic flow (strings, enums, flags).

**Authoritative Source**: 
1. Enum definitions in canonical types (`farfan_pipeline/core/types.py`)
2. Pattern registries (`pattern_registry.json`)
3. Schema files (`*.schema.json`)

**Examples**:
- Scoring modalities: `TYPE_A`, `TYPE_B`, `MACRO_HOLISTIC`
- Quality levels: `EXCELLENT`, `GOOD`, `ADEQUATE`, `POOR`
- Execution modes: `multi_method_pipeline`, `single_method`
- Pattern types: `cross_reference`, `coherence`, `narrative_coherence`

**Invariant [INV-QUAL-001]**: Qualitative parameters MUST use typed enums or schema-validated strings. No raw strings for logic branching.

---

## 3. AUTHORITATIVE FIELDS (Monolith vs Derived)

### 3.1 Monolith Fields (Read-Only, Authoritative)
File: `canonic_questionnaire_central/questionnaire_monolith.json`

**Never Modified by Code**:
- `canonical_notation.dimensions` → Dimension definitions
- `canonical_notation.policy_areas` → Policy area definitions
- `blocks.micro_questions[*].text` → Question text (Spanish)
- `blocks.micro_questions[*].expected_elements` → Element specifications
- `blocks.meso_questions[*].policy_areas` → Cluster-to-policy-area mapping
- `blocks.macro_question.clusters` → Cluster definitions

**Invariant [INV-MONO-001]**: Code MUST NOT write to questionnaire_monolith.json. Read-only access via loaders.

### 3.2 Derived Fields (Code-Generated)
Source: Computed by pipeline from monolith + evidence + methods

**Generated at Runtime**:
- Evidence scores (from Phase 2 EvidenceNexus)
- Confidence intervals (from Bayesian methods)
- Method execution traces (from orchestrator)
- Aggregated scores (from Phase 3 scoring)
- Quality levels (deterministic from scores)

**Stored in**:
- `test_output/` → Test execution results
- `evidence_traces/` → Evidence provenance
- Runtime TypedDict contracts (in-memory)

**Invariant [INV-DERIV-001]**: Derived values MUST include provenance metadata linking back to monolith sources and method executions.

---

## 4. THE "NO HIDDEN CONSTANTS" RULE

### 4.1 Prohibited Patterns

**Zero Tolerance** for:
1. Hardcoded thresholds in scoring logic
2. Magic numbers for weights/priors without declaration
3. Inline if-else chains based on undeclared numeric ranges
4. Copy-pasted threshold values across files
5. Commented-out "old threshold" values
6. Developer-specific tuning constants
7. Undocumented Bayesian prior distributions
8. Implicit normalization factors

### 4.2 Required Pattern: Declarative Configuration

**Example: WRONG**
```python
# FORBIDDEN: Magic number
if score >= 0.85:
    return "EXCELLENT"
```

**Example: CORRECT**
```python
# REQUIRED: Externalized configuration
thresholds = load_thresholds_from_config(question_id)
if score >= thresholds["excellent"]:
    return "EXCELLENT"
```

**Invariant [INV-CONST-001]**: All numeric constants affecting execution MUST be declared in JSON configs with semantic keys.

---

## 5. ARCHITECTURAL CONTRACTS

### 5.1 The 240-Method Invariant
- **Total Methods**: 240 (verified in class_registry.py: 40 classes × avg 6 methods)
- **Base Questions**: 30 (Q001-Q030)
- **Contracts**: 300 (30 questions × 10 policy areas)
- **Mapping**: `Q001_Q030_METHODS.json` maps base questions to method signatures
- **Operationalization**: Each method MUST have operationalization spec in separate JSON

**Invariant [INV-240-001]**: METHODS_TO_QUESTIONS_AND_FILES.json and METHODS_OPERACIONALIZACION.json MUST contain exactly the same 240 methods. No partial files.

### 5.2 Executor Contract Structure
Location: `src/canonic_phases/Phase_two/json_files_phase_two/executor_contracts/specialized/Q{###}.v3.json`

**Required Fields**:
```json
{
  "identity": {
    "question_id": "Q###",
    "dimension_id": "DIM##",
    "policy_area_id": "PA##",
    "contract_version": "3.0.0"
  },
  "method_binding": {
    "methods": [ /* List of method specs */ ]
  },
  "scoring_parameters": { /* Thresholds, weights */ },
  "expected_inputs": { /* Input schema */ },
  "expected_outputs": { /* Output schema */ }
}
```

**Invariant [INV-CONTRACT-001]**: Every Q### contract MUST specify all quantitative parameters in `scoring_parameters`. No defaults assumed.

### 5.3 Class Registry Lazy Loading
File: `src/orchestration/class_registry.py`

**Pattern**: Classes are registered by string name → import path. Instantiation is lazy via `get_method()`.

**Invariant [INV-LAZY-001]**: Class registry MUST NOT instantiate methods at import time. Classes load on-demand only.

---

## 6. UNIT OF ANALYSIS (PDM/PDT Documents)

Source: `canonic_description_unit_analysis.json`

### 6.1 Document Hierarchy
1. **Título I**: Diagnóstico (Characterization, Needs Analysis)
2. **Título II**: Parte Estratégica (Strategic Lines, Programs, Metas)
3. **Título III**: Plan Plurianual de Inversiones (Financial Projections)
4. **Capítulo Especial**: Paz/PDET (Peace-specific initiatives)

### 6.2 Key Patterns for Extraction
- **Section Headers**: `CAPÍTULO [N]. [Título]`, `Línea estratégica [N]:`
- **Financial Tables**: PPI matrices with SGP/SGR/Recursos Propios columns
- **Indicators**: `Metas de Producto`, `Indicadores de Resultado`, `Línea Base`
- **Causal Language**: `a través de`, `con el fin de`, `contribuirá a`

**Invariant [INV-PDM-001]**: Methods analyzing PDM structure MUST respect canonical hierarchy defined in unit_analysis.json.

---

## 7. STOP LIST (Forbidden Post-Refactor Patterns)

### 7.1 Code Patterns (8 Explicitly Forbidden)

| # | Forbidden Pattern | Reason | CI Check |
|---|-------------------|--------|----------|
| 1 | `if score >= 0.85:` without config load | Hidden constant | `semgrep: detect-magic-thresholds` |
| 2 | `P1`, `P2`, ... `P10` in internal logic | Legacy identifier use | `grep -r 'P[1-9]' src/ --exclude=*test*` |
| 3 | `weight = 0.4` inline without JSON source | Undeclared weight | `semgrep: detect-magic-weights` |
| 4 | Manual `dict[str, float]` for thresholds | Non-canonical config | AST check for dict literals in scoring |
| 5 | `# TODO: tune this threshold` comments | Manual tuning indication | `grep -r 'TODO.*tun\|threshold' src/` |
| 6 | Bayesian priors in function defaults | Hidden prior | `grep -r 'alpha=\|beta=' src/ --include=*.py` |
| 7 | Copy-paste of threshold blocks | Duplication | `semgrep: detect-duplicate-thresholds` |
| 8 | `import random` without seed from Phase 0 | Non-determinism | `grep -r 'import random' src/ --exclude=Phase_zero` |

### 7.2 Structural Patterns (Forbidden)

| # | Forbidden Pattern | Reason | CI Check |
|---|-------------------|--------|----------|
| 9 | Executor contracts without `scoring_parameters` | Missing config | JSON schema validation |
| 10 | Methods not in class_registry.py | Unregistered method | `validate_executor_integration.py` |
| 11 | P# in API responses | Legacy ID exposure | API response schema validation |
| 12 | Undocumented JSON additions to monolith | Unauthorized canonical change | Git pre-commit hook |
| 13 | Method signatures not in METHODS_DISPENSARY_SIGNATURES.json | Untracked method | `audit_executor_methods.py` |
| 14 | Direct file I/O without Phase 0 verification | Skipped integrity check | Static analysis for open() calls |
| 15 | SQL-style queries in evidence assembly | Architectural violation | `grep -r 'SELECT\|FROM.*WHERE' src/` |
| 16 | Undeclared dimension references (D1-D6 raw) | Non-canonical dimension ID | `grep -rE 'D[1-6]([^I]|$)' src/` |

### 7.3 Documentation Patterns (Forbidden)

| # | Forbidden Pattern | Reason | CI Check |
|---|-------------------|--------|----------|
| 17 | Markdown tables of thresholds in code comments | Unmaintained duplication | `semgrep: detect-threshold-in-comment` |
| 18 | "Legacy" or "deprecated" without removal ticket | Technical debt accumulation | `grep -r 'legacy\|deprecated' src/` with no ticket |

---

## 8. CI/CD ENFORCEMENT CHECKS

### 8.1 Pre-Commit Hooks
File: `.git/hooks/pre-commit` (to be created)

```bash
#!/bin/bash
# Enforce CONTRACT_MANIFEST rules

# Check 1: No P# in internal code (Stop List #2)
if git diff --cached --name-only | grep -E '\.py$' | xargs grep -E 'P[1-9]([^0]|$)' --exclude-dir=tests; then
  echo "ERROR: Legacy P# identifiers found. Use PA## instead."
  exit 1
fi

# Check 2: No magic thresholds (Stop List #1)
if git diff --cached --name-only | grep -E '\.py$' | xargs grep -E 'if.*score.*>=.*0\.[0-9]' --exclude-dir=config; then
  echo "ERROR: Magic threshold detected. Externalize to JSON config."
  exit 1
fi

# Check 3: No questionnaire_monolith.json changes without approval
if git diff --cached --name-only | grep 'questionnaire_monolith.json'; then
  echo "ERROR: Canonical monolith modification requires manifest amendment approval."
  exit 1
fi

# Check 4: Validate executor contracts against schema
for contract in $(git diff --cached --name-only | grep 'executor_contracts.*\.json'); do
  jsonschema -i "$contract" src/canonic_phases/Phase_two/json_files_phase_two/executor_contract.v3.schema.json
  if [ $? -ne 0 ]; then
    echo "ERROR: Contract $contract fails schema validation."
    exit 1
  fi
done
```

### 8.2 CI Pipeline Checks
Location: `.github/workflows/contract-enforcement.yml` (to be created)

**Stages**:
1. **Lint Stage**:
   - Run `ruff check` with custom rules for magic numbers
   - Run `mypy --strict` for type safety
   - Run `semgrep` with custom rules (see §8.3)

2. **Contract Validation Stage**:
   - Validate all 300 executor contracts against schema
   - Check 240-method count invariant
   - Verify policy_area_mapping.json synchronization

3. **Architectural Test Stage**:
   - Run `pytest tests/test_contract_manifest_compliance.py`
   - Execute `validate_executor_integration.py`
   - Run `audit_executor_methods.py` and check for regressions

4. **Determinism Stage**:
   - Execute Phase 0 exit gates
   - Verify reproducible outputs with fixed seeds
   - Check for non-deterministic patterns

### 8.3 Semgrep Rules
File: `.semgrep.yml` (to be created)

```yaml
rules:
  - id: detect-magic-thresholds
    pattern: |
      if $SCORE >= $NUM:
        ...
    message: "Magic threshold detected. Load from config JSON instead."
    severity: ERROR
    languages: [python]
    paths:
      include:
        - src/farfan_pipeline/analysis/scoring/
    
  - id: detect-magic-weights
    pattern: weight = $NUM
    message: "Hardcoded weight. Declare in executor_configurable_parameters.json."
    severity: ERROR
    languages: [python]
    
  - id: detect-legacy-policy-ids
    pattern-regex: '["'\'']P[1-9]["'\'']'
    message: "Legacy policy ID (P#). Use canonical PA## format."
    severity: ERROR
    paths:
      exclude:
        - tests/
        - canonic_questionnaire_central/
```

---

## 9. ADVERSARIAL SCENARIOS (Violation Detection)

### 9.1 Scenario: Contributor Reintroduces Manual Tuning

**Attack Vector**: Developer adds `if score >= 0.82:` in new scoring method.

**Detection**:
1. **Pre-commit hook** catches pattern immediately
2. **Semgrep rule** `detect-magic-thresholds` triggers
3. **Code review checklist** requires config file reference

**Remediation**: PR rejected until threshold externalized to JSON.

### 9.2 Scenario: Hidden Bayesian Prior in Method

**Attack Vector**: New method uses `Beta(2, 5)` prior without declaration.

**Detection**:
1. **Grep check** finds `alpha=2` parameter in code
2. **Unit test** `test_all_methods_have_operationalization` fails (missing prior spec)
3. **Audit script** `audit_executor_methods.py` reports undocumented method

**Remediation**: Add prior specification to method's operationalization JSON.

### 9.3 Scenario: Policy Area Vocabulary Overlap (P3 vs P7)

**Setup**:
- P3 (Ambiente) mentions "gestión territorial"
- P7 (Tierras) mentions "ordenamiento territorial"
- Evidence could be misrouted

**Prevention (via Canonicalization)**:
1. API receives legacy `"P3"` or `"P7"`
2. Boundary layer canonicalizes to `"PA03"` or `"PA07"`
3. Internal routing uses ONLY canonical IDs
4. Vocabulary boosting (if any) operates on canonical IDs
5. Evidence scoring is policy-area-scoped at Q### level (not base slot)

**Test**:
```python
def test_policy_area_canonicalization():
    """Prove legacy P# is never used internally."""
    api_input = {"policy_area": "P3"}
    canonical = canonicalize_policy_area(api_input["policy_area"])
    assert canonical == "PA03"
    
    # Simulate misrouting attempt
    try:
        internal_method(policy_area="P3")  # Should fail
    except ValueError as e:
        assert "Use canonical PA## format" in str(e)
```

---

## 10. DEFINITION OF DONE (Manifest Compliance)

A refactor is **complete** when:

### 10.1 Code Compliance
- [ ] All `P1-P10` references replaced with `PA01-PA10` in `src/` (excl. tests)
- [ ] All scoring thresholds externalized to JSON configs
- [ ] All Bayesian priors declared in operationalization JSONs
- [ ] Zero magic numbers in scoring/aggregation logic
- [ ] 240-method inventory synchronized across mapping files
- [ ] All executors registered in `class_registry.py`
- [ ] All 300 contracts validate against schema

### 10.2 Test Coverage
- [ ] Unit tests for canonicalization at API boundary
- [ ] Integration tests for P# → PA## conversion
- [ ] Regression tests for threshold externalization
- [ ] Determinism tests for all Bayesian methods
- [ ] Contract validation tests (all 300 contracts)

### 10.3 Documentation
- [ ] This CONTRACT_MANIFEST.md is version-controlled
- [ ] All quantitative parameters documented in config files
- [ ] Operationalization JSONs complete for all 240 methods
- [ ] CI/CD enforcement rules deployed
- [ ] Developer guide updated with forbidden patterns

### 10.4 CI/CD
- [ ] Pre-commit hooks installed and tested
- [ ] Semgrep rules active in CI pipeline
- [ ] Schema validation runs on every contract change
- [ ] Architectural audit scripts pass

### 10.5 Adversarial Testing
- [ ] Attempted manual tuning blocked by pre-commit
- [ ] Legacy P# injection caught by grep check
- [ ] Undeclared prior detected by audit script
- [ ] Policy area misrouting prevented by canonical IDs

---

## 11. AMENDMENT PROCESS

This manifest is **IMMUTABLE** except via formal amendment.

**To Modify This Manifest**:
1. Create GitHub issue with label `contract-manifest-amendment`
2. Propose specific change with justification
3. Require approval from 2+ core maintainers
4. Update version number in header
5. Add amendment entry to CHANGELOG.md
6. Update CI/CD checks if enforcement logic changes

**Amendment Log**:
- v1.0 (2025-12-13): Initial canonical contract established

---

## 12. REFERENCES

### 12.1 Source Files
- `canonic_questionnaire_central/questionnaire_monolith.json` → Canonical definitions
- `policy_area_mapping.json` → P# to PA## mapping
- `canonic_description_unit_analysis.json` → PDM document structure
- `Q001_Q030_METHODS.json` → Base question to method mapping
- `METHODS_DISPENSARY_SIGNATURES.json` → 127 class signatures (subset of 240 methods)
- `src/orchestration/class_registry.py` → 40 registered classes
- `executor_configurable_parameters.json` → Runtime parameters

### 12.2 Academic References
- Wilson, E. B. (1927). "Probable inference, the law of succession, and statistical inference." JASA, 22(158), 209-212.
- Dempster-Shafer Theory: Evidence combination under uncertainty
- Bayesian Multilevel Modeling: Hierarchical priors and pooling

### 12.3 Architectural Documents
- PHASE_0_15_CONTRACTS.md → Phase 0 specification
- PHASE_2_INTERNAL_WIRING_AUDIT.md → Evidence nexus architecture
- VIRTUOUS_SYNCHRONIZATION_EXECUTIVE_SUMMARY.md → Signal synchronization

---

**END OF CONTRACT MANIFEST v1.0**

**Enforcement**: Violations of this manifest are **pipeline failures**, not warnings.  
**Authority**: This document supersedes code comments, inline documentation, and verbal agreements.  
**Modification**: See §11 Amendment Process.

---

*"In canonical we trust; all else is derivative."*

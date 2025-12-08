# Calibration vs Parametrization Boundary Specification

## Executive Summary

This document establishes the strict separation between **calibration** (WHAT intrinsic quality we measure) and **parametrization** (HOW we execute measurement at runtime). This boundary is critical for maintaining scientific integrity, reproducibility, and operational flexibility.

## Core Distinction

### Calibration Domain (WHAT)

**Definition**: Calibration defines the *intrinsic quality characteristics* of policy analysis that are stable across deployments and represent domain expertise about policy quality.

**Location**: `system/config/calibration/`

**Governed by**: Domain experts, policy scientists, methodological review

**Change frequency**: Infrequent (quarterly/annually), requires peer review

**Examples**:
- Quality scores for theoretical soundness (`b_theory`)
- Quality scores for implementation realism (`b_impl`)
- Quality scores for deployment feasibility (`b_deploy`)
- Contextual compatibility matrices (Q/D/P alignment)
- Fusion weights for combining quality signals (`a_ℓ`, `a_ℓk`)

### Parametrization Domain (HOW)

**Definition**: Parametrization defines *execution parameters* that control how the system runs but do not affect the fundamental quality measurements.

**Location**: `system/config/environments/{env}.json`, CLI arguments, environment variables

**Governed by**: DevOps, operations team, runtime requirements

**Change frequency**: Frequent (daily/per-run), no review required

**Examples**:
- Timeout values (`timeout_s`)
- Retry attempts (`retry`)
- LLM temperature (`temperature`)
- Token limits (`max_tokens`)
- Logging levels
- Parallelization settings

---

## Boundary Principles

### 1. Scientific Integrity Principle
**Calibration files contain NO runtime parameters**

✅ **Correct**: `intrinsic_calibration.json` contains `b_theory: 0.85` (quality score)
❌ **Violation**: `intrinsic_calibration.json` contains `timeout_s: 30` (runtime parameter)

**Rationale**: Quality calibrations must be independent of execution environment to ensure reproducibility across deployments.

### 2. Operational Flexibility Principle
**Parametrization files contain NO quality scores**

✅ **Correct**: `production.json` contains `timeout_s: 60` (execution parameter)
❌ **Violation**: `production.json` contains `b_theory: 0.90` (quality score)

**Rationale**: Runtime parameters must be adjustable without triggering methodological review or affecting analytical validity.

### 3. Separation of Concerns Principle
**Different domains are loaded from different sources with different governance**

- Calibration: `system/config/calibration/` → version controlled, peer reviewed
- Parametrization: CLI args > ENV vars > `system/config/environments/{env}.json` → operationally managed

---

## Calibration Files (WHAT)

### `system/config/calibration/intrinsic_calibration.json`

**Purpose**: Defines intrinsic quality scores for policy analysis components

**Schema**:
```json
{
  "base_quality": {
    "b_theory": 0.85,
    "b_impl": 0.78,
    "b_deploy": 0.82
  },
  "layer_quality": {
    "@chain": 0.90,
    "@u": 0.75,
    "@m": 0.88
  }
}
```

**Governance**:
- Changes require methodological justification
- Version controlled with SHA256 hash tracking
- Requires domain expert approval
- Affects analytical validity

**Examples**:
- `b_theory`: Base quality score for theoretical soundness (0.0-1.0)
- `b_impl`: Base quality score for implementation realism (0.0-1.0)
- `b_deploy`: Base quality score for deployment feasibility (0.0-1.0)
- Layer scores: Quality ratings for architectural layers (@chain, @u, @m, etc.)

### `system/config/questionnaire/questionnaire_monolith.json`

**Purpose**: Defines contextual compatibility and question-dimension-policy alignment

**Schema**:
```json
{
  "canonical_notation": {
    "dimensions": { "D1": {...}, "D2": {...} },
    "policy_areas": { "PA01": {...}, "PA02": {...} }
  },
  "blocks": {
    "micro_questions": [
      {
        "question_id": "Q001",
        "dimension_id": "DIM01",
        "policy_area_id": "PA01",
        "scoring_modality": "TYPE_A"
      }
    ]
  }
}
```

**Governance**:
- Defines the analytical framework (dimensions × policy areas)
- Changes require stakeholder consensus
- Affects question routing and compatibility scoring

**Examples**:
- Q/D/P alignment: Question-Dimension-Policy compatibility scores
- Scoring modalities: TYPE_A, TYPE_B, TYPE_E definitions
- Pattern definitions: Regular expressions and NER patterns for evidence extraction

### `config/json_files_ no_schemas/fusion_specification.json`

**Purpose**: Defines fusion weights for combining multiple quality signals

**Schema**:
```json
{
  "role_fusion_parameters": {
    "SCORE_Q": {
      "linear_weights": {
        "@b": 0.18,
        "@chain": 0.14,
        "@q": 0.09
      },
      "interaction_weights": {
        "(@u, @chain)": 0.15,
        "(@chain, @C)": 0.10
      }
    }
  }
}
```

**Governance**:
- Defines `a_ℓ` (linear weights) and `a_ℓk` (interaction weights)
- Changes require calibration validation (sum to 1.0, monotonicity)
- Affects fusion formula: `Cal(I) = Σ(a_ℓ · x_ℓ) + Σ(a_ℓk · min(x_ℓ, x_k))`

**Examples**:
- `a_ℓ`: Linear weights per role (e.g., `@b: 0.18` for SCORE_Q)
- `a_ℓk`: Interaction weights (e.g., `(@u, @chain): 0.15`)
- Role-specific configurations: INGEST_PDM, STRUCTURE, EXTRACT, SCORE_Q, etc.

---

## Parametrization Files (HOW)

### `src/farfan_pipeline/core/orchestrator/executor_config.py`

**Purpose**: Defines runtime execution parameters (no quality scores)

**Schema**:
```python
@dataclass
class ExecutorConfig:
    max_tokens: int | None = None        # LLM token limit
    temperature: float | None = None     # LLM temperature
    timeout_s: float | None = None       # Execution timeout
    retry: int | None = None             # Retry attempts
    seed: int | None = None              # Random seed
    extra: dict[str, Any] | None = None  # Additional params
```

**Governance**:
- Operational parameters only
- No methodological review required
- Can be overridden per-execution
- Does NOT affect quality measurements

**Examples**:
- `timeout_s: 60.0`: Maximum execution time in seconds
- `retry: 3`: Number of retry attempts on failure
- `temperature: 0.7`: LLM sampling temperature
- `max_tokens: 2048`: Maximum LLM output tokens

### `system/config/environments/{env}.json`

**Purpose**: Environment-specific runtime configurations

**Supported environments**:
- `development.json`: Local development settings
- `staging.json`: Staging/QA environment settings
- `production.json`: Production deployment settings

**Schema**:
```json
{
  "executor": {
    "timeout_s": 120.0,
    "retry": 5,
    "max_tokens": 4096,
    "temperature": 0.7
  },
  "logging": {
    "level": "INFO",
    "format": "json"
  },
  "resources": {
    "max_workers": 8,
    "memory_limit_mb": 8192
  }
}
```

**Governance**:
- Managed by operations team
- Can differ by environment (dev/staging/prod)
- Changes do not affect analytical validity
- No peer review required

---

## Loading Hierarchy

The system loads parameters using a strict precedence order, allowing operational flexibility while maintaining calibration integrity.

### Hierarchy (Highest to Lowest Priority)

```
1. CLI Arguments         → --timeout-s=120 --retry=3
2. Environment Variables → FARFAN_TIMEOUT_S=120 FARFAN_RETRY=3
3. Environment File      → system/config/environments/{env}.json
4. Conservative Defaults → CONSERVATIVE_CONFIG fallback
```

### Implementation

```python
def load_executor_config(env: str = "production") -> ExecutorConfig:
    """
    Load ExecutorConfig with proper hierarchy.
    
    Precedence: CLI args > ENV vars > environment file > defaults
    """
    # 4. Start with conservative defaults
    config = {
        "timeout_s": 300.0,    # 5 minutes
        "retry": 3,
        "max_tokens": 2048,
        "temperature": 0.7,
        "seed": 42
    }
    
    # 3. Load environment-specific config
    env_file = Path(f"system/config/environments/{env}.json")
    if env_file.exists():
        with open(env_file) as f:
            env_config = json.load(f)
            if "executor" in env_config:
                config.update(env_config["executor"])
    
    # 2. Override with environment variables
    if "FARFAN_TIMEOUT_S" in os.environ:
        config["timeout_s"] = float(os.environ["FARFAN_TIMEOUT_S"])
    if "FARFAN_RETRY" in os.environ:
        config["retry"] = int(os.environ["FARFAN_RETRY"])
    if "FARFAN_MAX_TOKENS" in os.environ:
        config["max_tokens"] = int(os.environ["FARFAN_MAX_TOKENS"])
    if "FARFAN_TEMPERATURE" in os.environ:
        config["temperature"] = float(os.environ["FARFAN_TEMPERATURE"])
    
    # 1. Override with CLI arguments (handled by argparse)
    # This is done in the CLI layer, not here
    
    return ExecutorConfig(**config)
```

### Conservative Defaults

```python
CONSERVATIVE_CONFIG = {
    "timeout_s": 300.0,      # 5 minutes (safe for most operations)
    "retry": 3,              # 3 attempts (balance resilience vs latency)
    "max_tokens": 2048,      # Conservative token limit
    "temperature": 0.7,      # Moderate creativity
    "seed": 42,              # Reproducibility
    "max_workers": 4,        # Conservative parallelism
    "memory_limit_mb": 4096  # 4GB default limit
}
```

---

## Verification Rules

### Rule 1: No Runtime Parameters in Calibration Files

**Check**:
```python
def verify_no_runtime_params_in_calibration(calibration_file: Path) -> bool:
    """Verify calibration file contains no runtime parameters."""
    forbidden_keys = {"timeout_s", "retry", "temperature", "max_tokens", 
                      "seed", "max_workers", "memory_limit_mb"}
    
    with open(calibration_file) as f:
        data = json.load(f)
    
    def scan_dict(d: dict, path: str = "") -> list[str]:
        violations = []
        for key, value in d.items():
            full_path = f"{path}.{key}" if path else key
            if key in forbidden_keys:
                violations.append(f"Found runtime param '{key}' at {full_path}")
            if isinstance(value, dict):
                violations.extend(scan_dict(value, full_path))
        return violations
    
    violations = scan_dict(data)
    if violations:
        print(f"❌ Calibration file {calibration_file} contains runtime parameters:")
        for v in violations:
            print(f"   - {v}")
        return False
    return True
```

### Rule 2: No Quality Scores in ExecutorConfig

**Check**:
```python
def verify_no_quality_scores_in_executor_config() -> bool:
    """Verify ExecutorConfig contains no quality scores."""
    forbidden_fields = {"b_theory", "b_impl", "b_deploy", "fusion_weights",
                       "linear_weights", "interaction_weights", "quality_score"}
    
    config_fields = {f.name for f in fields(ExecutorConfig)}
    violations = config_fields & forbidden_fields
    
    if violations:
        print(f"❌ ExecutorConfig contains quality score fields: {violations}")
        return False
    return True
```

### Rule 3: Environment Files Contain Only Runtime Parameters

**Check**:
```python
def verify_environment_file(env_file: Path) -> bool:
    """Verify environment file contains only runtime parameters."""
    allowed_top_keys = {"executor", "logging", "resources", "monitoring"}
    allowed_executor_keys = {"timeout_s", "retry", "max_tokens", "temperature",
                            "seed", "extra"}
    
    with open(env_file) as f:
        data = json.load(f)
    
    # Check top-level keys
    invalid_top = set(data.keys()) - allowed_top_keys
    if invalid_top:
        print(f"❌ Environment file has invalid top-level keys: {invalid_top}")
        return False
    
    # Check executor keys
    if "executor" in data:
        invalid_exec = set(data["executor"].keys()) - allowed_executor_keys
        if invalid_exec:
            print(f"❌ Environment file executor has invalid keys: {invalid_exec}")
            return False
    
    return True
```

---

## Examples

### Example 1: Correct Separation

**Calibration** (`system/config/calibration/intrinsic_calibration.json`):
```json
{
  "base_quality": {
    "b_theory": 0.85,
    "b_impl": 0.78
  }
}
```

**Parametrization** (`system/config/environments/production.json`):
```json
{
  "executor": {
    "timeout_s": 120.0,
    "retry": 5
  }
}
```

✅ **Result**: Clean separation maintained

### Example 2: Violation - Runtime Params in Calibration

**WRONG** (`system/config/calibration/intrinsic_calibration.json`):
```json
{
  "base_quality": {
    "b_theory": 0.85,
    "timeout_s": 60.0  // ❌ VIOLATION
  }
}
```

❌ **Error**: Runtime parameter in calibration file
❌ **Impact**: Violates scientific integrity principle
❌ **Fix**: Move `timeout_s` to environment config

### Example 3: Violation - Quality Scores in ExecutorConfig

**WRONG**:
```python
@dataclass
class ExecutorConfig:
    timeout_s: float | None = None
    b_theory: float = 0.85  # ❌ VIOLATION
```

❌ **Error**: Quality score in execution config
❌ **Impact**: Violates operational flexibility principle
❌ **Fix**: Load `b_theory` from calibration files, not ExecutorConfig

### Example 4: Correct Hierarchy Usage

```bash
# Base: Conservative defaults
timeout_s=300.0, retry=3

# Override with environment file
$ export FARFAN_ENV=production
# Loads system/config/environments/production.json
timeout_s=120.0, retry=5

# Override with environment variable
$ export FARFAN_TIMEOUT_S=90.0
timeout_s=90.0, retry=5

# Override with CLI argument
$ python run_pipeline.py --timeout-s=60
timeout_s=60.0, retry=5
```

---

## Migration Guide

### For Existing Code

1. **Audit ExecutorConfig usage**:
   - Remove any quality scores or calibration weights
   - Keep only runtime execution parameters
   - Document parameter semantics

2. **Audit calibration files**:
   - Remove any runtime parameters (timeout, retry, etc.)
   - Keep only quality scores and weights
   - Verify SHA256 hashes after cleanup

3. **Create environment files**:
   - Move runtime parameters from calibration to environment files
   - Create separate configs for dev/staging/prod
   - Document environment-specific differences

4. **Update loading code**:
   - Implement loading hierarchy (CLI > ENV > file > defaults)
   - Separate calibration loading from parametrization loading
   - Add verification checks

### Validation Checklist

- [ ] `intrinsic_calibration.json` contains NO runtime parameters
- [ ] `questionnaire_monolith.json` contains NO runtime parameters
- [ ] `fusion_specification.json` contains NO runtime parameters
- [ ] `ExecutorConfig` dataclass contains NO quality scores
- [ ] Environment files contain ONLY runtime parameters
- [ ] Loading hierarchy is correctly implemented
- [ ] Verification rules pass for all configs
- [ ] Documentation is updated

---

## Governance

### Calibration Changes

**Process**:
1. Propose change with methodological justification
2. Peer review by domain experts
3. Update calibration file with version bump
4. Generate SHA256 hash and update registry
5. Create backup of previous version
6. Update CHANGELOG with rationale

**Approval**: Requires domain expert sign-off

**Frequency**: Quarterly or as needed for methodological improvements

### Parametrization Changes

**Process**:
1. Update environment file or set environment variable
2. Test in dev/staging environment
3. Deploy to production
4. Monitor for operational issues

**Approval**: Operations team discretion

**Frequency**: As needed for operational requirements

---

## Appendix: Complete File Inventory

### Calibration Domain (WHAT)

| File | Purpose | Change Frequency | Review Required |
|------|---------|------------------|-----------------|
| `system/config/calibration/intrinsic_calibration.json` | Base quality scores | Quarterly | Yes |
| `system/config/calibration/intrinsic_calibration_rubric.json` | Quality rubric definitions | Annually | Yes |
| `system/config/questionnaire/questionnaire_monolith.json` | Q/D/P alignment | Semi-annually | Yes |
| `config/json_files_ no_schemas/fusion_specification.json` | Fusion weights | Quarterly | Yes |

### Parametrization Domain (HOW)

| File/Source | Purpose | Change Frequency | Review Required |
|-------------|---------|------------------|-----------------|
| CLI Arguments | Per-execution overrides | Per-run | No |
| Environment Variables | Deployment-specific overrides | Per-deployment | No |
| `system/config/environments/development.json` | Dev runtime config | As needed | No |
| `system/config/environments/staging.json` | Staging runtime config | As needed | No |
| `system/config/environments/production.json` | Prod runtime config | As needed | No |
| `src/farfan_pipeline/core/orchestrator/executor_config.py` | ExecutorConfig schema | Rarely | Code review |

---

## Summary

The calibration vs parametrization boundary ensures:

1. **Scientific Integrity**: Quality measurements are stable and independent of execution environment
2. **Operational Flexibility**: Runtime parameters can be adjusted without methodological review
3. **Reproducibility**: Calibration is version controlled and traceable
4. **Separation of Concerns**: Different domains have different governance and change management

**Golden Rule**: If it affects WHAT quality we measure → Calibration. If it affects HOW we execute → Parametrization.

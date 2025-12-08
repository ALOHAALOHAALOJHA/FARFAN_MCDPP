# Calibration vs Parametrization Quick Reference

## One-Line Summary
**Calibration = WHAT quality we measure | Parametrization = HOW we execute measurement**

## Golden Rules

| Aspect | Calibration (WHAT) | Parametrization (HOW) |
|--------|-------------------|----------------------|
| **Domain** | Intrinsic quality characteristics | Runtime execution parameters |
| **Location** | `system/config/calibration/` | `system/config/environments/` |
| **Examples** | `b_theory`, `b_impl`, `fusion_weights` | `timeout_s`, `retry`, `max_tokens` |
| **Governed By** | Domain experts, policy scientists | Operations team, DevOps |
| **Review** | Peer review required | No review needed |
| **Frequency** | Quarterly/annually | As needed (daily/per-run) |
| **Affects** | Quality measurements | Execution behavior |
| **Change Cost** | High (analytical validity) | Low (operational flexibility) |

## Key Files

### Calibration Files (WHAT)
- ✓ `system/config/calibration/intrinsic_calibration.json` - Base quality scores
- ✓ `system/config/questionnaire/questionnaire_monolith.json` - Q/D/P alignment
- ✓ `config/json_files_ no_schemas/fusion_specification.json` - Fusion weights

### Parametrization Files (HOW)
- ✓ `system/config/environments/development.json` - Dev runtime config
- ✓ `system/config/environments/staging.json` - Staging runtime config
- ✓ `system/config/environments/production.json` - Production runtime config
- ✓ `src/farfan_pipeline/core/orchestrator/executor_config.py` - Config schema

## Loading Hierarchy

```
1. CLI Arguments         (highest)  --timeout-s=120 --retry=3
2. Environment Variables           FARFAN_TIMEOUT_S=120
3. Environment File               system/config/environments/{env}.json
4. Conservative Defaults (lowest)  CONSERVATIVE_CONFIG
```

## Quick Commands

```bash
# Verify boundary compliance
python scripts/verify_calibration_parametrization_boundary.py

# Load config with hierarchy
python scripts/load_executor_config.py --env production --show-hierarchy

# Load with overrides
python scripts/load_executor_config.py --env production --timeout-s 120 --retry 5

# Show defaults
python scripts/load_executor_config.py --show-defaults

# Example demonstration
python scripts/example_calibration_vs_parametrization.py
```

## Allowed Parameters

### Calibration Domain (WHAT)
✅ `b_theory`, `b_impl`, `b_deploy` - Base quality scores  
✅ `linear_weights`, `interaction_weights` - Fusion weights (a_ℓ, a_ℓk)  
✅ `scoring_modality` - Question scoring type  
✅ `patterns` - Evidence extraction patterns  
✅ `dimensions`, `policy_areas` - Analytical framework  

### Parametrization Domain (HOW)
✅ `timeout_s` - Execution timeout  
✅ `retry` - Retry attempts  
✅ `max_tokens` - LLM token limit  
✅ `temperature` - LLM sampling temperature  
✅ `seed` - Random seed  
✅ `max_workers` - Parallelism  
✅ `memory_limit_mb` - Memory limit  

## Violations

### ❌ Runtime Params in Calibration
```json
// WRONG: system/config/calibration/intrinsic_calibration.json
{
  "b_theory": 0.85,
  "timeout_s": 60.0  // ❌ VIOLATION
}
```

### ❌ Quality Scores in ExecutorConfig
```python
# WRONG
@dataclass
class ExecutorConfig:
    timeout_s: float | None = None
    b_theory: float = 0.85  # ❌ VIOLATION
```

### ❌ Quality Scores in Environment File
```json
// WRONG: system/config/environments/production.json
{
  "executor": {
    "timeout_s": 120.0,
    "fusion_weights": {...}  // ❌ VIOLATION
  }
}
```

## Code Examples

### Load Calibration Data
```python
import json
from pathlib import Path

# Load intrinsic quality scores
with open("system/config/calibration/intrinsic_calibration.json") as f:
    calibration = json.load(f)
    b_theory = calibration.get("base_quality", {}).get("b_theory", 0.85)
```

### Load Parametrization Data
```python
from farfan_pipeline.core.orchestrator import load_executor_config

# Load with hierarchy
config = load_executor_config(env="production")
print(f"Timeout: {config.timeout_s}s")

# Load with CLI overrides
config = load_executor_config(
    env="production",
    cli_overrides={"timeout_s": 120.0, "retry": 5}
)
```

### Verify Boundary
```python
from scripts.verify_calibration_parametrization_boundary import main

# Returns 0 if valid, 1 if violations
exit_code = main()
```

## Decision Tree

```
Does the parameter affect...
│
├─ WHAT quality characteristics we measure?
│  ├─ Quality scores (b_theory, b_impl, b_deploy)?
│  ├─ Fusion weights (a_ℓ, a_ℓk)?
│  ├─ Scoring modalities?
│  └─ Question-dimension-policy alignment?
│     └─ YES → Calibration domain
│           - system/config/calibration/
│           - Requires peer review
│           - Affects analytical validity
│
└─ HOW we execute the measurement?
   ├─ Timeout, retry, token limits?
   ├─ LLM temperature or seed?
   ├─ Resource limits (workers, memory)?
   └─ Logging or monitoring?
      └─ YES → Parametrization domain
            - system/config/environments/
            - No peer review needed
            - Operational flexibility
```

## Environment Characteristics

| Environment | Timeout | Retry | Workers | Purpose |
|-------------|---------|-------|---------|---------|
| **development** | 60s | 2 | 2 | Fast iteration, debugging |
| **staging** | 180s | 4 | 4 | QA, production validation |
| **production** | 300s | 5 | 8 | Reliable, optimized execution |

## See Also

- `CALIBRATION_VS_PARAMETRIZATION.md` - Complete specification
- `system/config/environments/README.md` - Environment config guide
- `src/farfan_pipeline/core/orchestrator/parameter_loader.py` - Implementation
- `scripts/verify_calibration_parametrization_boundary.py` - Verification tool

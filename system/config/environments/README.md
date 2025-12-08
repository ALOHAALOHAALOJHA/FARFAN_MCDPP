# Environment Configuration Files

This directory contains environment-specific runtime parameter configurations. These files define **HOW** the system executes (parametrization), not **WHAT** quality it measures (calibration).

## Files

- `development.json`: Local development environment (fast iteration, debugging)
- `staging.json`: Staging/QA environment (production-like with enhanced monitoring)
- `production.json`: Production environment (optimized for reliability and performance)

## Schema

```json
{
  "_metadata": {
    "environment": "string",
    "description": "string",
    "last_updated": "YYYY-MM-DD",
    "maintainer": "string"
  },
  "executor": {
    "timeout_s": float,       // Execution timeout in seconds
    "retry": int,             // Number of retry attempts
    "max_tokens": int,        // Maximum LLM output tokens
    "temperature": float,     // LLM sampling temperature
    "seed": int              // Random seed for reproducibility
  },
  "logging": {
    "level": "string",        // DEBUG, INFO, WARN, ERROR
    "format": "string",       // text, json
    "output": "string"        // stdout, file
  },
  "resources": {
    "max_workers": int,       // Maximum parallel workers
    "memory_limit_mb": int,   // Memory limit in MB
    "enable_profiling": bool  // Enable performance profiling
  },
  "monitoring": {
    "enable_metrics": bool,   // Enable metrics collection
    "enable_tracing": bool,   // Enable distributed tracing
    "sample_rate": float      // Trace sampling rate (0.0-1.0)
  }
}
```

## Usage

### Loading Configuration

```python
from farfan_pipeline.core.orchestrator.parameter_loader import load_executor_config

# Load production config
config = load_executor_config(env="production")

# Load with CLI overrides
config = load_executor_config(
    env="staging",
    cli_overrides={"timeout_s": 120.0, "retry": 5}
)
```

### Loading Hierarchy

Parameters are loaded with the following precedence (highest to lowest):

1. **CLI Arguments** (highest priority)
   ```bash
   python run_pipeline.py --timeout-s 120 --retry 5
   ```

2. **Environment Variables**
   ```bash
   export FARFAN_TIMEOUT_S=120
   export FARFAN_RETRY=5
   ```

3. **Environment File**
   ```bash
   # Loads system/config/environments/production.json
   python run_pipeline.py --env production
   ```

4. **Conservative Defaults** (fallback)
   ```python
   CONSERVATIVE_CONFIG = {
       "timeout_s": 300.0,
       "retry": 3,
       "max_tokens": 2048,
       "temperature": 0.7,
       "seed": 42
   }
   ```

## Governance

### Change Management

- **Who**: Operations team, DevOps
- **Review**: No peer review required (runtime parameters only)
- **Frequency**: As needed for operational requirements
- **Testing**: Test in dev/staging before production deployment

### Restrictions

**NEVER** include calibration parameters in environment files:

❌ **Forbidden** (calibration parameters):
- `b_theory`, `b_impl`, `b_deploy`
- `fusion_weights`, `linear_weights`, `interaction_weights`
- `quality_score`, `a_l`, `a_lk`
- Any quality ratings or scoring weights

✅ **Allowed** (runtime parameters):
- `timeout_s`, `retry`, `max_tokens`, `temperature`, `seed`
- Logging configuration
- Resource limits
- Monitoring settings

### Validation

Run verification script to ensure boundary compliance:

```bash
python scripts/verify_calibration_parametrization_boundary.py
```

## Examples

### Example 1: Override timeout for long-running analysis

```bash
# Use production config but increase timeout
FARFAN_TIMEOUT_S=600 python run_pipeline.py --env production
```

### Example 2: Development with verbose logging

```bash
# development.json already has DEBUG logging
python run_pipeline.py --env development
```

### Example 3: Staging with custom retry

```bash
# Override retry count for flaky test environment
python run_pipeline.py --env staging --retry 10
```

### Example 4: Show resolved configuration

```bash
# Show final config with all hierarchy sources
python scripts/load_executor_config.py --env production --show-hierarchy
```

## Environment Characteristics

### Development
- **Purpose**: Fast iteration, debugging
- **Timeout**: 60s (fail fast)
- **Retry**: 2 (minimal)
- **Max Tokens**: 1024 (cost-effective)
- **Temperature**: 0.8 (explore behavior)
- **Workers**: 2 (local resources)
- **Logging**: DEBUG, text, stdout

### Staging
- **Purpose**: QA, production validation
- **Timeout**: 180s (moderate)
- **Retry**: 4 (balanced)
- **Max Tokens**: 2048 (standard)
- **Temperature**: 0.7 (production-like)
- **Workers**: 4 (moderate parallelism)
- **Logging**: INFO, JSON, file

### Production
- **Purpose**: Reliable, optimized execution
- **Timeout**: 300s (generous)
- **Retry**: 5 (resilient)
- **Max Tokens**: 4096 (comprehensive)
- **Temperature**: 0.7 (stable)
- **Workers**: 8 (high throughput)
- **Logging**: INFO, JSON, file with rotation

## See Also

- `CALIBRATION_VS_PARAMETRIZATION.md`: Full boundary specification
- `system/config/calibration/`: Calibration files (WHAT domain)
- `src/farfan_pipeline/core/orchestrator/executor_config.py`: ExecutorConfig schema
- `src/farfan_pipeline/core/orchestrator/parameter_loader.py`: Loading implementation

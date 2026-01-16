# F.A.R.F.A.N Core Orchestrator

**Version 2.0.0** - Production-Grade Pipeline Orchestration

## Overview

The Core Orchestrator provides comprehensive coordination for all 11 phases of the F.A.R.F.A.N (Framework for Advanced Retrieval and Forensic Analysis of Administrative Narratives) pipeline. It manages:

- **Phase Coordination**: Sequential execution of Phases 0-9
- **Contract Validation**: Input/output contract enforcement between phases
- **Signal Integration**: SISAS 2.0 signal distribution for inter-phase communication
- **Determinism Enforcement**: SIN_CARRETA compliance for reproducible results
- **Error Handling**: Graceful degradation and comprehensive error reporting
- **Telemetry**: Full observability with metrics and logging

## Architecture

### Pipeline Phases

| Phase | Name | Description | Output Count |
|-------|------|-------------|--------------|
| P00 | Bootstrap & Validation | Infrastructure setup, wiring initialization | N/A |
| P01 | CPP Ingestion | Document processing and semantic assignment | 300 questions |
| P02 | Executor Factory | Method dispensary instantiation | 30 executors |
| P03 | Layer Scoring | 8-layer quality assessment | 300 micro-scores |
| P04 | Dimension Aggregation | Choquet integral to dimensions | 60 dimensions |
| P05 | Policy Area Aggregation | Dimension → policy area scores | 10 policy areas |
| P06 | Cluster Aggregation | Policy areas → MESO clusters | 4 clusters |
| P07 | Macro Aggregation | Clusters → holistic score | 1 macro score |
| P08 | Recommendations Engine | Signal-enriched recommendations | N/A |
| P09 | Report Assembly | Final report generation | 1 report |

### Core Components

```
orchestration/
├── core_orchestrator.py      # Main orchestrator (PipelineOrchestrator)
├── orchestrator_config.py    # Configuration management
├── cli.py                     # Command-line interface
├── README.md                  # This file
└── __init__.py               # Package exports
```

## Quick Start

### 1. Command Line Usage

```bash
# Run full pipeline with defaults
python -m farfan_pipeline.orchestration.cli

# Run specific phase range
python -m farfan_pipeline.orchestration.cli --start-phase P01 --end-phase P05

# Use development preset (relaxed limits, verbose logging)
python -m farfan_pipeline.orchestration.cli --preset development

# Custom configuration
python -m farfan_pipeline.orchestration.cli --config my_config.json

# Enable verbose output
python -m farfan_pipeline.orchestration.cli --verbose

# Save execution summary
python -m farfan_pipeline.orchestration.cli --json-output results.json
```

### 2. Python API Usage

```python
from farfan_pipeline.orchestration import (
    PipelineOrchestrator,
    OrchestratorConfig,
    PhaseID,
)

# Create configuration
config = OrchestratorConfig(
    questionnaire_path="/path/to/questionnaire.json",
    strict_mode=True,
    deterministic=True,
)

# Create orchestrator
orchestrator = PipelineOrchestrator(
    config=config.to_dict(),
    strict_mode=True,
    deterministic=True,
)

# Execute pipeline
context = orchestrator.execute_pipeline(
    start_phase=PhaseID.PHASE_0,
    end_phase=PhaseID.PHASE_9,
)

# Get results
summary = context.get_execution_summary()
print(f"Completed: {summary['phases_completed']}/{summary['total_phases']}")
print(f"Violations: {summary['total_violations']}")
```

### 3. Environment Variables

```bash
# Configure via environment
export FARFAN_QUESTIONNAIRE_PATH="/path/to/questionnaire.json"
export FARFAN_STRICT_MODE="true"
export FARFAN_DETERMINISTIC="true"
export FARFAN_LOG_LEVEL="INFO"
export FARFAN_OUTPUT_DIR="/path/to/output"

python -m farfan_pipeline.orchestration.cli
```

## Configuration

### Configuration Presets

#### Development
- Relaxed resource limits (4GB memory, 10min CPU)
- Non-strict mode (warnings instead of errors)
- Debug logging
- Best for: Development and debugging

```python
from farfan_pipeline.orchestration import get_development_config

config = get_development_config()
```

#### Production
- Standard resource limits (2GB memory, 5min CPU)
- Strict mode enabled
- INFO logging
- Deterministic execution
- Best for: Production deployments

```python
from farfan_pipeline.orchestration import get_production_config

config = get_production_config()
```

#### Testing
- Minimal resource limits (1GB memory, 2min CPU)
- Strict mode enabled
- WARNING logging
- Deterministic execution
- Best for: Automated testing

```python
from farfan_pipeline.orchestration import get_testing_config

config = get_testing_config()
```

### Configuration Options

```python
config = OrchestratorConfig(
    # Paths
    questionnaire_path=Path("/path/to/questionnaire.json"),
    executor_config_path=Path("/path/to/executor_config.json"),
    output_dir=Path("/path/to/output"),

    # Execution control
    strict_mode=True,              # Raise exceptions on critical violations
    deterministic=True,            # SIN_CARRETA compliance
    start_phase="P00",             # Starting phase
    end_phase="P09",               # Ending phase

    # Resource limits
    resource_limits={
        "memory_mb": 2048,
        "cpu_seconds": 300,
        "disk_mb": 500,
        "file_descriptors": 1024,
    },

    # Feature flags
    enable_http_signals=False,     # Use HTTP signal transport
    enable_calibration=False,      # Enable calibration orchestrator

    # Logging
    log_level="INFO",              # DEBUG, INFO, WARNING, ERROR, CRITICAL
)
```

## Contract Validation

The orchestrator enforces input and output contracts for each phase transition:

### Input Contract Validation
- Validates prerequisites (previous phase completed)
- Checks required data structures
- Verifies data completeness

### Output Contract Validation
- Validates constitutional invariants (e.g., 300 questions, 60 dimensions)
- Checks output structure and bounds
- Ensures downstream compatibility

### Violation Handling

Violations are categorized by severity:
- **CRITICAL**: Impossible to continue (raises exception in strict mode)
- **HIGH**: Compromises result quality (logged as error)
- **MEDIUM**: Performance degradation (logged as warning)
- **LOW**: Best practice violations (logged as info)

## Execution Context

The `ExecutionContext` tracks:
- **Wiring Components**: From Phase 0 bootstrap
- **Phase Outputs**: Data passed between phases
- **Phase Results**: Execution metrics and violations
- **Determinism Tracking**: Input/output hashes, seeds
- **Telemetry**: Metrics and signal data

```python
# Access phase outputs
cpp = context.get_phase_output(PhaseID.PHASE_1)
dimension_scores = context.get_phase_output(PhaseID.PHASE_4)

# Get execution summary
summary = context.get_execution_summary()

# Access violations
for violation in context.total_violations:
    print(f"{violation.severity}: {violation.message}")
```

## Determinism (SIN_CARRETA Compliance)

When `deterministic=True`, the orchestrator enforces:

1. **Fixed Seeds**: All random operations use derived seeds
2. **Hash Verification**: SHA-256/BLAKE3 hashing of all inputs/outputs
3. **UTC Timestamps**: No local timezone dependencies
4. **Reproducibility**: Same inputs → identical outputs (bit-for-bit)

```python
# Enable determinism
orchestrator = PipelineOrchestrator(
    config=config.to_dict(),
    deterministic=True,
)

# Execution will use seed=42 for all random operations
context = orchestrator.execute_pipeline()
```

## Signal Integration

The orchestrator integrates with SISAS 2.0 for:
- **Event Distribution**: Phase completion signals
- **Scope-based Routing**: Hierarchical signal matching
- **Value Gating**: Empirical threshold filtering
- **Audit Trail**: Full observability

Signals are automatically distributed via the `SignalClient` from Phase 0 bootstrap.

## Error Handling

### Strict Mode (Default)
- Critical violations raise exceptions
- Pipeline stops on first failure
- Best for: Production, CI/CD

### Non-Strict Mode
- Critical violations logged as errors
- Pipeline continues if possible
- Best for: Development, debugging

```python
# Strict mode
orchestrator = PipelineOrchestrator(strict_mode=True)
# Raises exception on critical violation

# Non-strict mode
orchestrator = PipelineOrchestrator(strict_mode=False)
# Logs error and continues
```

## Telemetry & Observability

### Logging

All components use `structlog` for structured logging:

```python
logger.info(
    "phase_execution_complete",
    phase="P01",
    execution_time_s=12.5,
    violations=0,
)
```

### Metrics

Each phase execution tracks:
- Execution time
- Input validation time
- Output validation time
- Violation counts
- Resource usage

### Execution Summary

```python
summary = context.get_execution_summary()
# {
#     "execution_id": "abc123...",
#     "elapsed_time_s": 125.3,
#     "phases_completed": 10,
#     "phases_failed": 0,
#     "total_violations": 3,
#     "critical_violations": 0,
#     "deterministic": true
# }
```

## Examples

### Example 1: Full Pipeline Execution

```python
from farfan_pipeline.orchestration import (
    PipelineOrchestrator,
    get_production_config,
    PhaseID,
)

# Load production configuration
config = get_production_config()
config.questionnaire_path = "/data/questionnaire.json"

# Create orchestrator
orchestrator = PipelineOrchestrator(
    config=config.to_dict(),
    strict_mode=True,
    deterministic=True,
)

# Execute full pipeline
context = orchestrator.execute_pipeline(
    start_phase=PhaseID.PHASE_0,
    end_phase=PhaseID.PHASE_9,
)

# Print summary
summary = context.get_execution_summary()
print(f"Pipeline completed in {summary['elapsed_time_s']}s")
print(f"Phases: {summary['phases_completed']}/{summary['total_phases']}")
```

### Example 2: Partial Pipeline Execution

```python
# Execute only aggregation phases (P04-P07)
context = orchestrator.execute_pipeline(
    start_phase=PhaseID.PHASE_4,
    end_phase=PhaseID.PHASE_7,
)
```

### Example 3: Custom Configuration

```python
from pathlib import Path
from farfan_pipeline.orchestration import OrchestratorConfig

config = OrchestratorConfig(
    questionnaire_path=Path("/data/custom_questionnaire.json"),
    executor_config_path=Path("/config/custom_executors.json"),
    output_dir=Path("/output/run_001"),
    strict_mode=True,
    deterministic=True,
    log_level="DEBUG",
    resource_limits={
        "memory_mb": 4096,
        "cpu_seconds": 600,
    },
)
```

### Example 4: Handling Violations

```python
context = orchestrator.execute_pipeline()

# Check for violations
if context.total_violations:
    print(f"Found {len(context.total_violations)} violations")

    # Group by severity
    critical = [v for v in context.total_violations if v.severity.value == "CRITICAL"]
    high = [v for v in context.total_violations if v.severity.value == "HIGH"]

    print(f"Critical: {len(critical)}, High: {len(high)}")

    # Print details
    for violation in critical:
        print(f"[{violation.severity.value}] {violation.component_path}")
        print(f"  {violation.message}")
        if violation.remediation:
            print(f"  Fix: {violation.remediation}")
```

## CLI Reference

### Basic Usage

```bash
python -m farfan_pipeline.orchestration.cli [OPTIONS]
```

### Options

#### Configuration
- `--config FILE`: Load configuration from JSON file
- `--preset {development|production|testing}`: Use configuration preset

#### Phase Control
- `--start-phase PHASE`: Starting phase (P00-P09)
- `--end-phase PHASE`: Ending phase (P00-P09)

#### Paths
- `--questionnaire FILE`: Path to questionnaire monolith JSON
- `--executor-config FILE`: Path to executor configuration
- `--output-dir DIR`: Output directory

#### Execution Control
- `--strict`: Enable strict mode
- `--no-strict`: Disable strict mode
- `--deterministic`: Enable deterministic execution
- `--no-deterministic`: Disable deterministic execution

#### Logging
- `--log-level {DEBUG|INFO|WARNING|ERROR|CRITICAL}`: Set log level
- `--quiet`: Minimal output (ERROR level)
- `--verbose`: Verbose output (DEBUG level)

#### Output
- `--json-output FILE`: Write execution summary to JSON file
- `--report-format {json|markdown|html|pdf}`: Final report format

### Examples

```bash
# Development mode with verbose logging
python -m farfan_pipeline.orchestration.cli --preset development --verbose

# Run phases 1-5 only
python -m farfan_pipeline.orchestration.cli --start-phase P01 --end-phase P05

# Custom paths
python -m farfan_pipeline.orchestration.cli \
    --questionnaire /data/my_questionnaire.json \
    --output-dir /output/run_001

# Save results to JSON
python -m farfan_pipeline.orchestration.cli --json-output results.json

# Non-deterministic execution (faster, but not reproducible)
python -m farfan_pipeline.orchestration.cli --no-deterministic
```

## Troubleshooting

### Common Issues

#### 1. Memory Errors (OOM)

**Symptom**: Process killed by OS
**Solution**: Increase memory limit

```python
config.resource_limits["memory_mb"] = 4096
```

#### 2. Timeout Errors

**Symptom**: Phase exceeds CPU time limit
**Solution**: Increase CPU time limit

```python
config.resource_limits["cpu_seconds"] = 600
```

#### 3. Missing Dependencies

**Symptom**: `MISSING_PREREQUISITE` violation
**Solution**: Ensure phases execute in order (P00 → P01 → ... → P09)

```python
# Correct: Start from beginning
orchestrator.execute_pipeline(start_phase=PhaseID.PHASE_0)

# Incorrect: Skip Phase 0
orchestrator.execute_pipeline(start_phase=PhaseID.PHASE_1)  # Will fail
```

#### 4. Contract Violations

**Symptom**: `CHUNK_COUNT_VIOLATION` or similar
**Solution**: Verify constitutional invariants are met

- Phase 1: Must produce exactly 300 questions
- Phase 4: Must produce exactly 60 dimensions
- Phase 5: Must produce exactly 10 policy areas
- Phase 6: Must produce exactly 4 clusters

## Advanced Topics

### Custom Phase Executors

To implement custom phase logic, override the execution methods:

```python
from farfan_pipeline.orchestration import PipelineOrchestrator

class CustomOrchestrator(PipelineOrchestrator):
    def _execute_phase1(self):
        # Custom Phase 1 implementation
        return my_custom_cpp_ingestion()

    def _execute_phase2(self):
        # Custom Phase 2 implementation
        return my_custom_executor_factory()
```

### Signal Monitoring

```python
# Access signal metrics
if context.wiring:
    registry = context.wiring.signal_registry
    metrics = registry.get_metrics()
    print(f"Total signals: {metrics['total_signals']}")
    print(f"Hit rate: {metrics['hit_rate']}")
```

### Checkpoint/Resume (Future)

```python
# Save checkpoint after each phase
for phase_id in range(PhaseID.PHASE_0, PhaseID.PHASE_9 + 1):
    context = orchestrator.execute_pipeline(
        start_phase=phase_id,
        end_phase=phase_id,
    )
    context.save_checkpoint(f"checkpoint_{phase_id.value}.pkl")

# Resume from checkpoint
context = ExecutionContext.load_checkpoint("checkpoint_P05.pkl")
```

## API Reference

### Core Classes

- **`PipelineOrchestrator`**: Main orchestrator
- **`ExecutionContext`**: Shared state across phases
- **`PhaseResult`**: Single phase execution result
- **`ContractEnforcer`**: Contract validation
- **`OrchestratorConfig`**: Configuration management

### Enums

- **`PhaseID`**: Phase identifiers (P00-P09)
- **`PhaseStatus`**: Execution status (PENDING, IN_PROGRESS, COMPLETED, FAILED, SKIPPED)

### Configuration Functions

- **`get_development_config()`**: Development preset
- **`get_production_config()`**: Production preset
- **`get_testing_config()`**: Testing preset
- **`validate_config(config)`**: Validate configuration

## Contributing

When adding new phases or extending the orchestrator:

1. Update `PHASE_METADATA` in `core_orchestrator.py`
2. Add input/output validation methods to `ContractEnforcer`
3. Implement phase execution method (`_execute_phaseN()`)
4. Update this README with phase documentation

## License

Copyright © 2025 F.A.R.F.A.N Core Team
Licensed under the project's main license.

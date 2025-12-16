# Executor Calibration Integration System

**Complete Implementation for 30+ D[1-6]Q[1-5] Executors**

## Overview

This integration connects all 30 executors in the FARFAN pipeline with the calibration system, capturing runtime metrics and retrieving quality scores. The system maintains strict separation between:

- **Calibration (WHAT)**: Quality scores loaded from `intrinsic_calibration.json`
- **Parametrization (HOW)**: Runtime parameters loaded from `ExecutorConfig`

## Architecture

### Separation Principle

```
┌─────────────────────────────────────────────────────────┐
│  CALIBRATION (WHAT Quality)                            │
│  - Quality scores (b_theory, b_impl, b_deploy)         │
│  - Layer scores (@b, @chain, @q, @d, @p, @C, @u, @m)   │
│  - Fusion weights (linear + interaction)               │
│  Source: intrinsic_calibration.json                     │
│  Governance: Domain experts, peer review               │
│  Change frequency: Quarterly                            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  PARAMETRIZATION (HOW Execution)                       │
│  - Runtime parameters (timeout_s, retry, temperature)   │
│  - Resource limits (memory_limit_mb, max_tokens)        │
│  Source: ExecutorConfig (CLI > ENV > JSON)             │
│  Governance: Operations team                            │
│  Change frequency: As needed                            │
└─────────────────────────────────────────────────────────┘
```

### Component Structure

```
src/canonic_phases/Phase_two/
├── executors.py                              # 30 executor classes
├── executor_calibration_integration.py       # Calibration system interface
├── executor_instrumentation_mixin.py         # Mixin for auto-instrumentation
├── executor_config.py                        # Runtime config dataclass
├── executor_tests.py                         # Integration test suite
├── executor_calibration_report.json          # Integration status report
└── executor_configs/                         # Per-executor runtime configs
    ├── D1_Q1_QuantitativeBaselineExtractor.json
    ├── D1_Q2_ProblemDimensioningAnalyzer.json
    ├── ...
    ├── D6_Q5_ContextualAdaptabilityEvaluator.json
    └── executor_config_template.json
```

## Layer System

All executors are assigned role `SCORE_Q` with 8 required layers:

| Layer | Name | Description | Weight |
|-------|------|-------------|--------|
| `@b` | BASE | Code quality (theory, impl, deploy) | 0.17 |
| `@chain` | CHAIN | Method wiring and orchestration | 0.13 |
| `@q` | QUESTION | Question appropriateness | 0.08 |
| `@d` | DIMENSION | Dimension alignment | 0.07 |
| `@p` | POLICY | Policy area fit | 0.06 |
| `@C` | CONGRUENCE | Contract compliance | 0.08 |
| `@u` | UNIT | Document quality | 0.04 |
| `@m` | META | Governance maturity | 0.04 |

### Interaction Weights (Choquet Integral)

- `(@u, @chain)`: 0.13
- `(@chain, @C)`: 0.10
- `(@q, @d)`: 0.10

### Quality Score Aggregation

```
Quality Score = Σ(a_ℓ · layer_score_ℓ) + Σ(a_ℓk · min(layer_score_ℓ, layer_score_k))
```

Where:
- `a_ℓ`: Linear weight for layer ℓ
- `a_ℓk`: Interaction weight for layers ℓ and k
- `min()`: Choquet interaction operator

## Usage

### Basic Instrumentation

```python
from executor_calibration_integration import instrument_executor

# Inside executor.execute()
def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
    # Track execution start
    start_time = time.perf_counter()
    start_memory = get_memory_usage()
    
    # Execute methods
    result = self._execute_methods(context)
    
    # Capture metrics
    runtime_ms = (time.perf_counter() - start_time) * 1000
    memory_mb = get_memory_usage() - start_memory
    
    # Instrument with calibration call
    calibration_result = instrument_executor(
        executor_id=self.executor_id,
        context=context,
        runtime_ms=runtime_ms,
        memory_mb=memory_mb,
        methods_executed=len(self.execution_log),
        methods_succeeded=sum(1 for log in self.execution_log if log['success'])
    )
    
    # Attach calibration metadata to result
    result['calibration_metadata'] = {
        'quality_score': calibration_result.quality_score,
        'layer_scores': calibration_result.layer_scores,
        'runtime_ms': runtime_ms,
        'memory_mb': memory_mb
    }
    
    return result
```

### Using Instrumentation Mixin

```python
from executor_instrumentation_mixin import ExecutorInstrumentationMixin

class D3_Q2_TargetProportionalityAnalyzer(BaseExecutor, ExecutorInstrumentationMixin):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Use execute_with_calibration() wrapper
        return self.execute_with_calibration(context)
```

### Loading Runtime Configuration

```python
from executor_config import ExecutorConfig

# Load with full hierarchy
config = ExecutorConfig.load_from_sources(
    executor_id="D3_Q2_TargetProportionalityAnalyzer",
    environment="production",
    cli_overrides={"timeout_s": 120}
)

print(config.timeout_s)      # 120 (from CLI override)
print(config.retry)          # 3 (from defaults)
print(config.memory_limit_mb) # 1024 (from executor config file)
```

## Configuration Files

### Executor Config Structure

Each executor has a JSON config file in `executor_configs/`:

```json
{
  "executor_id": "D3_Q2_TargetProportionalityAnalyzer",
  "dimension": "D3",
  "question": "Q2",
  "canonical_label": "DIM03_Q02_PRODUCT_TARGET_PROPORTIONALITY",
  "role": "SCORE_Q",
  "required_layers": ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"],
  "runtime_parameters": {
    "timeout_s": 600,
    "retry": 3,
    "temperature": 0.0,
    "max_tokens": 4096,
    "memory_limit_mb": 1024,
    "enable_profiling": true,
    "seed": 42
  },
  "thresholds": {
    "min_quality_score": 0.5,
    "min_evidence_confidence": 0.7,
    "max_runtime_ms": 600000
  },
  "epistemic_mix": ["statistical", "financial", "normative"],
  "contextual_params": {
    "expected_methods": 21,
    "critical_methods": [],
    "dimension_label": "DIM03",
    "question_label": "DIM03_Q02_PRODUCT_TARGET_PROPORTIONALITY"
  }
}
```

### Configuration Loading Hierarchy

1. **CLI Arguments** (highest priority)
   ```bash
   python run_pipeline.py --timeout-s=120 --retry=5
   ```

2. **Environment Variables**
   ```bash
   export FARFAN_TIMEOUT_S=120
   export FARFAN_RETRY=5
   export FARFAN_MEMORY_LIMIT_MB=2048
   ```

3. **Environment File**
   ```json
   // system/config/environments/production.json
   {
     "executor": {
       "timeout_s": 300,
       "retry": 3,
       "max_tokens": 4096
     }
   }
   ```

4. **Executor Config File**
   ```json
   // executor_configs/D3_Q2_TargetProportionalityAnalyzer.json
   {
     "runtime_parameters": {
       "timeout_s": 600,
       "memory_limit_mb": 1024
     }
   }
   ```

5. **Conservative Defaults** (lowest priority)
   ```python
   {
     "timeout_s": 300.0,
     "retry": 3,
     "temperature": 0.0,
     "max_tokens": 4096,
     "memory_limit_mb": 512,
     "seed": 42
   }
   ```

## All 30 Executors

### Dimension 1 (D1): INSUMOS - Diagnóstico y Recursos

1. `D1_Q1_QuantitativeBaselineExtractor` - Extracción de Línea Base Cuantitativa (15 methods)
2. `D1_Q2_ProblemDimensioningAnalyzer` - Dimensionamiento del Problema (12 methods)
3. `D1_Q3_BudgetAllocationTracer` - Trazabilidad de Asignación Presupuestal (13 methods)
4. `D1_Q4_InstitutionalCapacityIdentifier` - Identificación de Capacidad Institucional (11 methods)
5. `D1_Q5_ScopeJustificationValidator` - Validación de Justificación de Alcance (7 methods)

### Dimension 2 (D2): ACTIVIDADES - Diseño de Intervención

6. `D2_Q1_StructuredPlanningValidator` - Validación de Planificación Estructurada (7 methods)
7. `D2_Q2_InterventionLogicInferencer` - Inferencia de Lógica de Intervención (11 methods)
8. `D2_Q3_RootCauseLinkageAnalyzer` - Análisis de Vinculación a Causas Raíz (9 methods)
9. `D2_Q4_RiskManagementAnalyzer` - Análisis de Gestión de Riesgos (10 methods)
10. `D2_Q5_StrategicCoherenceEvaluator` - Evaluación de Coherencia Estratégica (8 methods)

### Dimension 3 (D3): PRODUCTOS - Productos y Outputs

11. `D3_Q1_IndicatorQualityValidator` - Validación de Calidad de Indicadores (8 methods)
12. `D3_Q2_TargetProportionalityAnalyzer` - Product Target Proportionality (21 methods)
13. `D3_Q3_TraceabilityValidator` - Traceability Budget Org (22 methods)
14. `D3_Q4_TechnicalFeasibilityEvaluator` - Technical Feasibility (10 methods)
15. `D3_Q5_OutputOutcomeLinkageAnalyzer` - Output Outcome Linkage (9 methods)

### Dimension 4 (D4): RESULTADOS - Resultados y Outcomes

16. `D4_Q1_OutcomeMetricsValidator` - Outcome Indicator Completeness (8 methods)
17. `D4_Q2_CausalChainValidator` - Validación de Cadena Causal (10 methods)
18. `D4_Q3_AmbitionJustificationAnalyzer` - Análisis de Justificación de Ambición (9 methods)
19. `D4_Q4_ProblemSolvencyEvaluator` - Evaluación de Solvencia del Problema (11 methods)
20. `D4_Q5_VerticalAlignmentValidator` - Validación de Alineación Vertical (8 methods)

### Dimension 5 (D5): IMPACTOS - Impactos de Largo Plazo

21. `D5_Q1_LongTermVisionAnalyzer` - Análisis de Visión de Largo Plazo (8 methods)
22. `D5_Q2_CompositeMeasurementValidator` - Composite Proxy Validity (10 methods)
23. `D5_Q3_IntangibleMeasurementAnalyzer` - Análisis de Medición Intangible (9 methods)
24. `D5_Q4_SystemicRiskEvaluator` - Evaluación de Riesgo Sistémico (12 methods)
25. `D5_Q5_RealismAndSideEffectsAnalyzer` - Análisis de Realismo y Efectos Colaterales (11 methods)

### Dimension 6 (D6): CAUSALIDAD - Teoría de Cambio

26. `D6_Q1_ExplicitTheoryBuilder` - Constructor de Teoría Explícita (15 methods)
27. `D6_Q2_LogicalProportionalityValidator` - Validación de Proporcionalidad Lógica (10 methods)
28. `D6_Q3_ValidationTestingAnalyzer` - Análisis de Pruebas de Validación (13 methods)
29. `D6_Q4_FeedbackLoopAnalyzer` - Análisis de Bucles de Retroalimentación (9 methods)
30. `D6_Q5_ContextualAdaptabilityEvaluator` - Evaluación de Adaptabilidad Contextual (10 methods)

## Verification

### No Hardcoded Calibration Values

All quality scores are loaded from external sources:
- ✅ NO `QUALITY_SCORE =` constants in executor code
- ✅ NO `CALIBRATION_VALUE =` constants in executor code
- ✅ NO `BASE_SCORE =` constants in executor code

### Calibration Data Sources

- Base quality scores: `COHORT_2024_intrinsic_calibration.json`
- Q/D/P alignment: `questionnaire_monolith.json`
- Fusion weights: Defined in `executor_calibration_integration.py`

### Runtime Parameter Sources

- Executor configs: `executor_configs/{executor_id}.json`
- Environment configs: `system/config/environments/{env}.json`
- Environment variables: `FARFAN_*`
- CLI arguments: `--timeout-s`, `--retry`, etc.

## Testing

Run integration tests:

```bash
# Test all executors
pytest src/canonic_phases/Phase_two/executor_tests.py -v

# Test specific executor
pytest src/canonic_phases/Phase_two/executor_tests.py::TestExecutorInstrumentation::test_executor_instrumentation[D3_Q2_TargetProportionalityAnalyzer] -v

# Test calibration separation
pytest src/canonic_phases/Phase_two/executor_tests.py::TestExecutorCalibrationIntegration::test_no_hardcoded_calibration_values -v

# Test configuration loading
pytest src/canonic_phases/Phase_two/executor_tests.py::TestConfigurationLoading -v
```

## Integration Status

✅ **COMPLETE** - All 30 executors instrumented

- [x] 30 executor config files created
- [x] Calibration integration system implemented
- [x] Instrumentation mixin created
- [x] Enhanced ExecutorConfig with loading hierarchy
- [x] Test suite implemented
- [x] Calibration report generated
- [x] NO hardcoded calibration values in executor code
- [x] Separation of calibration (WHAT) and parametrization (HOW) verified

## References

- **Calibration Spec**: `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/CALIBRATION_VS_PARAMETRIZATION.md`
- **Integration Code**: `executor_calibration_integration.py`
- **Executor Code**: `executors.py`
- **Test Suite**: `executor_tests.py`
- **Status Report**: `executor_calibration_report.json`

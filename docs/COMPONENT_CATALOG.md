# F.A.R.F.A.N Component Catalog
## Complete System Components Reference

**Version:** 5.0.0  
**Last Updated:** 2026-01-28

---

## Component Index

1. [Core Pipeline Components](#core-pipeline-components)
2. [Calibration System](#calibration-system)
3. [Infrastructure Components](#infrastructure-components)
4. [Data Models](#data-models)
5. [Utility Components](#utility-components)
6. [Testing & Validation](#testing--validation)

---

## Core Pipeline Components

### Phase 0: Bootstrap & Validation

**Location**: `src/farfan_pipeline/phases/Phase_00/`

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| `phase0_00_00_bootstrap.py` | System initialization | `bootstrap_system()` |
| `phase0_10_00_configuration_validator.py` | Config validation | `validate_config()` |
| `phase0_20_00_dependency_checker.py` | Dependency verification | `check_dependencies()` |
| `phase0_30_00_resource_validator.py` | Resource availability | `validate_resources()` |
| `phase0_40_00_input_validation.py` | Input PDF validation | `validate_input()` |
| `phase0_50_00_gate_orchestrator.py` | 7-gate sequencing | `execute_gates()` |

**Gates**:
1. Configuration Gate
2. Dependency Gate
3. Resource Gate
4. Input Gate
5. Calibration Gate
6. Method Registry Gate
7. Constitutional Gate

---

### Phase 1: Document Chunking

**Location**: `src/farfan_pipeline/phases/Phase_01/`

| Component | Purpose | Input | Output |
|-----------|---------|-------|--------|
| `phase1_00_00_pdf_extractor.py` | Text extraction | PDF | Raw text |
| `phase1_10_00_semantic_chunker.py` | Semantic chunking | Text | Chunks |
| `phase1_20_00_canon_mapper.py` | Map to 300 questions | Chunks | Mapped chunks |
| `phase1_30_00_package_builder.py` | Build output | Mapped chunks | `CanonPolicyPackage` |

**Output Schema**:
```python
class CanonPolicyPackage:
    chunks: List[PolicyChunk]  # Exactly 300
    metadata: PackageMetadata
    validation: ValidationReport
```

---

### Phase 2: Evidence Extraction

**Location**: `src/farfan_pipeline/phases/Phase_02/`

| Component | Purpose | Contracts Handled |
|-----------|---------|-------------------|
| `phase2_00_00_contract_executor.py` | Main executor | All 300 |
| `phase2_10_00_parallel_orchestrator.py` | Parallel execution | N contracts |
| `phase2_20_00_result_aggregator.py` | Result collection | 300 results |
| `phase2_30_00_failure_handler.py` | Retry & error handling | Failed contracts |

**Method Registry**:
- Location: `src/farfan_pipeline/methods/`
- Total methods: 240 unique implementations
- Mapping: See `METHODS_TO_QUESTIONS_AND_FILES.json`

---

### Phase 3: Scoring Transformation

**Location**: `src/farfan_pipeline/phases/Phase_03/`

| Component | Purpose | Scale |
|-----------|---------|-------|
| `phase3_00_00_evidence_scorer.py` | Evidence → Score | [0, 3] |
| `phase3_10_00_adversarial_validator.py` | Attack vector testing | 96 vectors |
| `phase3_20_00_score_normalizer.py` | Normalization | [0, 3] |
| `phase3_30_00_quality_assurance.py` | QA checks | Boolean |

**Scoring Scale**:
- 0: No evidence or capability
- 1: Minimal evidence/capability
- 2: Moderate evidence/capability
- 3: Strong evidence/capability

---

### Phase 4: Dimension Aggregation

**Location**: `src/farfan_pipeline/phases/Phase_04/`

| Component | Purpose | Method |
|-----------|---------|--------|
| `phase4_00_00_choquet_integral.py` | Non-additive aggregation | Choquet integral |
| `phase4_10_00_fuzzy_measure.py` | Define measures | λ-fuzzy |
| `phase4_20_00_dimension_builder.py` | 300 → 60 dimensions | Aggregation |
| `phase4_30_00_aggregation.py` | Main orchestrator | Pipeline |

**Output**: 60 dimension scores (6 dimensions × 10 policy areas)

---

### Phase 5: Policy Area Aggregation

**Location**: `src/farfan_pipeline/phases/Phase_05/`

| Component | Purpose | Aggregation |
|-----------|---------|-------------|
| `phase5_00_00_policy_area_aggregator.py` | Main aggregator | Weighted average |
| `phase5_10_00_hermeticity_validator.py` | 6-dimension check | Validation |
| `phase5_20_00_weight_applier.py` | Apply policy weights | Multiplication |

**Output**: 10 policy area scores

---

### Phase 6: Cluster Aggregation

**Location**: `src/farfan_pipeline/phases/Phase_06/`

| Component | Purpose | Method |
|-----------|---------|--------|
| `phase6_00_00_adaptive_penalty.py` | APF calculation | Non-linear penalty |
| `phase6_10_00_cluster_score.py` | Cluster scoring | Penalized average |
| `phase6_20_00_balance_analyzer.py` | Variance analysis | Statistical |

**Output**: 4 meso-cluster scores

**Clusters**:
1. Economic Development
2. Social Development
3. Environmental Sustainability
4. Institutional Capacity

---

### Phase 7: Macro Evaluation

**Location**: `src/farfan_pipeline/phases/Phase_07/`

| Component | Purpose | Output |
|-----------|---------|--------|
| `phase7_00_00_macro_synthesizer.py` | Final synthesis | MacroScore |
| `phase7_10_00_ccca.py` | Cross-cutting coherence | CCCA score |
| `phase7_20_00_sgd.py` | Systemic gap detection | Gap list |
| `phase7_30_00_sas.py` | Strategic alignment | Alignment score |
| `phase7_40_00_helix_metrics.py` | Visualization metrics | Helix data |

**Output**: Single MacroScore + diagnostic metrics

---

### Phase 8: Recommendation Engine

**Location**: `src/farfan_pipeline/phases/Phase_08/`

| Component | Purpose | Output Type |
|-----------|---------|-------------|
| `phase8_00_00_gap_analyzer.py` | Identify gaps | Gap list |
| `phase8_10_00_intervention_generator.py` | Generate interventions | DAG |
| `phase8_20_00_priority_ranker.py` | Prioritize actions | Ranked list |
| `phase8_30_00_dag_builder.py` | Build dependency graph | NetworkX graph |

**Recommendation Tiers**:
- **Micro**: Tactical fixes (< 1 year)
- **Meso**: Strategic realignments (1-3 years)
- **Macro**: Institutional reforms (3+ years)

---

### Phase 9: Report Generation

**Location**: `src/farfan_pipeline/phases/Phase_09/`

| Component | Purpose | Output Format |
|-----------|---------|---------------|
| `phase9_00_00_report_builder.py` | Main builder | PDF |
| `phase9_10_00_executive_summary.py` | Summary section | Markdown |
| `phase9_20_00_visualizations.py` | Charts & graphs | PNG/SVG |
| `phase9_30_00_annexes.py` | Detailed annexes | PDF sections |

**Report Sections**:
1. Executive Summary
2. Methodology
3. Results by Policy Area
4. Cluster Analysis
5. MacroScore Interpretation
6. Recommendations
7. Technical Annexes

---

## Calibration System

### Mathematical Optimizers

**Location**: `src/farfan_pipeline/calibration/mathematical_calibration.py`

| Optimizer | Purpose | Methods |
|-----------|---------|---------|
| `N1EmpiricalOptimizer` | Empirical thresholds | ROC, MI, FPR control |
| `N2InferentialOptimizer` | Bayesian parameters | Empirical Bayes, Gelman-Rubin |
| `N3AuditOptimizer` | Validation thresholds | FDR, SPC |
| `N4MetaOptimizer` | Meta thresholds | Entropy, MI |

**Key Methods**:
```python
# N1 Empirical
calculate_optimal_extraction_threshold(labels, scores) -> float
calculate_deduplication_threshold_statistical(similarities) -> float
calculate_pattern_fuzzy_threshold_information_theoretic(patterns) -> float

# N2 Inferential
calculate_optimal_prior_strength_empirical_bayes(data) -> float
calculate_optimal_mcmc_samples_gelman_rubin(chains) -> int
calculate_likelihood_weight_elbo(model, data) -> float

# N3 Audit
calculate_optimal_significance_fdr_control(p_values) -> float
calculate_veto_thresholds_spc(process_data) -> Tuple[float, float]

# N4 Meta
calculate_failure_threshold_mutual_information(outcomes) -> float
calculate_synthesis_threshold_entropy(evidence) -> float
```

---

### Calibration Classes

**Location**: `src/farfan_pipeline/calibration/epistemic_core.py`

| Class | Level | Parameters |
|-------|-------|------------|
| `N0InfrastructureCalibration` | N0 | Deterministic config |
| `N1EmpiricalCalibration` | N1 | Extraction thresholds |
| `N2InferentialCalibration` | N2 | Bayesian parameters |
| `N3AuditCalibration` | N3 | Validation thresholds |
| `N4MetaCalibration` | N4 | Synthesis thresholds |

---

### PDM Calibrator

**Location**: `src/farfan_pipeline/calibration/pdm_calibrator.py`

```python
class Phase1PDMCalibrator:
    """
    Adjusts Phase 1 parameters based on document characteristics
    """
    def calibrate_chunking(self, pdm_metadata: PDMMetadata) -> ChunkingParams
    def calibrate_extraction(self, pdm_stats: PDMStats) -> ExtractionParams
```

---

## Infrastructure Components

### SISAS (Signal Irrigation System)

**Location**: `src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/`

| Component | Purpose |
|-----------|---------|
| `signal_registry.py` | Signal type registry |
| `signal_dispatcher.py` | Event routing |
| `gate_validator.py` | 4-gate validation |
| `consumer_registry.py` | Consumer registration |

**Signal Types**:
```python
class SignalType(Enum):
    SCORING_PRIMARY = "scoring_primary"
    SCORING_SECONDARY = "scoring_secondary"
    MACRO_EVAL = "macro_eval"
    RECOMMENDATION = "recommendation"
    VALIDATION = "validation"
```

---

### UnifiedFactory

**Location**: `src/farfan_pipeline/infrastructure/factory/unified_factory.py`

```python
class UnifiedFactory:
    """
    Central dependency injection and object creation
    """
    def create_executor(self, contract: Contract) -> MethodExecutor
    def create_calibration(self, level: str) -> CalibrationConfig
    def create_validator(self, phase: int) -> Validator
    def create_aggregator(self, type: str) -> Aggregator
```

---

### Orchestrator

**Location**: `src/farfan_pipeline/orchestration/orchestrator.py`

```python
class UnifiedOrchestrator:
    """
    Main pipeline orchestrator
    """
    def execute_pipeline(self, input_pdf: Path) -> ExecutionResult
    def execute_phase(self, phase: int, state: State) -> PhaseResult
    def handle_failure(self, error: Error) -> Recovery
```

---

## Data Models

### Core Models

**Location**: `src/farfan_pipeline/data_models/`

| Model | Purpose | Immutability |
|-------|---------|--------------|
| `CanonPolicyPackage` | Phase 1 output | Frozen |
| `EvidenceResult` | Phase 2 output | Frozen |
| `Score` | Phase 3 output | Frozen |
| `DimensionScore` | Phase 4 output | Frozen |
| `PolicyAreaScore` | Phase 5 output | Frozen |
| `ClusterScore` | Phase 6 output | Frozen |
| `MacroScore` | Phase 7 output | Frozen |
| `RecommendationDAG` | Phase 8 output | Frozen |

**Example**:
```python
@dataclass(frozen=True)
class Score:
    value: float  # [0, 3]
    question_id: str
    evidence: str
    confidence: float
    epistemic_level: str
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        assert 0 <= self.value <= 3, "Score must be in [0, 3]"
```

---

### Contract Models

**Location**: `src/farfan_pipeline/infrastructure/contractual/`

```python
@dataclass
class Contract:
    contract_id: str  # "D1-Q1_PA01"
    question: str
    dimension: str
    policy_area: str
    method: str
    epistemic_level: str
    input_schema: Type[BaseModel]
    output_schema: Type[Result]
```

---

## Utility Components

### Validation

**Location**: `src/farfan_pipeline/linters/`

| Validator | Purpose |
|-----------|---------|
| `canon_notation_validator.py` | Validate D1-Q1 format |
| `score_validator.py` | Validate score bounds |
| `contract_validator.py` | Validate contract specs |
| `config_validator.py` | Validate configuration |

---

### Logging & Monitoring

**Location**: `src/farfan_pipeline/infrastructure/logging/`

```python
class ExecutionLogger:
    def log_phase_start(self, phase: int)
    def log_phase_complete(self, phase: int, metrics: Metrics)
    def log_error(self, error: Error, context: Context)
    def log_metric(self, name: str, value: float)
```

---

### Caching

**Location**: `src/farfan_pipeline/infrastructure/caching/`

```python
class CacheManager:
    def get(self, key: str) -> Optional[Any]
    def set(self, key: str, value: Any, ttl: int)
    def invalidate(self, pattern: str)
    def clear_all()
```

---

## Testing & Validation

### Test Suites

**Location**: `tests/`

| Suite | Coverage | Tests |
|-------|----------|-------|
| Unit tests | 85% | 2,104 |
| Integration tests | 70% | 450 |
| Constitutional tests | 100% | 96 |
| Reproducibility tests | 100% | 50 |
| Performance tests | - | 25 |

---

### Validation Tools

**Location**: `validation/`

```python
# Constitution validator
from farfan_pipeline.validation import ConstitutionalValidator

validator = ConstitutionalValidator()
result = validator.validate_all(execution_result)
assert result.all_pass, f"Failed: {result.failures}"

# Reproducibility tester
from farfan_pipeline.validation import ReproducibilityTester

tester = ReproducibilityTester()
hash1, hash2 = tester.test_reproducibility(input_pdf, runs=2)
assert hash1 == hash2, "Not reproducible!"

# Calibration validator
from farfan_pipeline.calibration import CalibrationValidator

validator = CalibrationValidator()
assert validator.verify_integrity(), "Calibration corrupted"
```

---

## Component Dependencies

### Dependency Graph

```
UnifiedFactory
    ├── CalibrationRegistry
    ├── MethodRegistry
    ├── ContractRegistry
    └── ConfigManager

UnifiedOrchestrator
    ├── UnifiedFactory
    ├── PhaseExecutors [Phase0-Phase9]
    ├── SISAS (SignalDispatcher)
    └── ExecutionLogger

Phase Executors
    ├── Validators
    ├── Transformers
    ├── Aggregators
    └── Calibration (injected)

SISAS
    ├── SignalRegistry
    ├── ConsumerRegistry
    ├── GateValidators [4]
    └── EventBus
```

---

## Extension Points

### Adding New Methods

```python
# 1. Implement method
class MyNewMethod(BaseMethod):
    epistemic_level = "N1-EMP"
    
    def execute(self, input: ChunkData) -> Result[Evidence, Error]:
        # Implementation
        pass

# 2. Register method
from farfan_pipeline.methods import method_registry
method_registry.register("D1-Q1", MyNewMethod)

# 3. Create contract
contract = Contract(
    contract_id="D1-Q1_PA01",
    method="D1-Q1",
    epistemic_level="N1-EMP",
    # ...
)
```

---

### Adding New Validators

```python
# 1. Implement validator
class MyValidator(BaseValidator):
    invariant_id = "CI-97"
    description = "My custom invariant"
    
    def validate(self, state: State) -> bool:
        # Validation logic
        pass

# 2. Register validator
from farfan_pipeline.validation import validator_registry
validator_registry.register(MyValidator)
```

---

## Performance Characteristics

### Time Complexity

| Phase | Complexity | Parallel | Typical Time |
|-------|-----------|----------|--------------|
| Phase 0 | O(1) | No | 10s |
| Phase 1 | O(n) | Partial | 30s |
| Phase 2 | O(n·m) | Yes | 5min (16 workers) |
| Phase 3 | O(n) | Yes | 30s |
| Phase 4 | O(n²) | Partial | 1min |
| Phase 5 | O(n) | No | 10s |
| Phase 6 | O(n) | No | 5s |
| Phase 7 | O(n) | No | 30s |
| Phase 8 | O(n·log n) | Partial | 1min |
| Phase 9 | O(n) | No | 30s |

**Total**: ~10-15 minutes (single document)

---

### Space Complexity

| Component | Memory Usage | Scalability |
|-----------|--------------|-------------|
| PDF Loading | 10-50 MB | O(file size) |
| Chunking | 50-100 MB | O(chunks) |
| Evidence | 100-200 MB | O(contracts) |
| Embeddings | 500 MB - 2 GB | O(vocabulary) |
| Aggregations | 10 MB | O(dimensions) |

**Peak Memory**: 2-4 GB (typical)

---

## Version Compatibility

### Python Versions

- **Minimum**: 3.11
- **Recommended**: 3.12
- **Tested**: 3.11, 3.12
- **Not Supported**: < 3.11

### Dependency Versions

See `requirements.txt` for exact versions. Key dependencies:

- `numpy >= 1.24.0`
- `scipy >= 1.10.0`
- `pandas >= 2.0.0`
- `scikit-learn >= 1.3.0`
- `pydantic >= 2.0.0`
- `fastapi >= 0.100.0`

---

## API Reference

### CLI Interface

```bash
# Main command
farfan-pipeline run --input <pdf> --output <dir>

# Subcommands
farfan-pipeline config      # Configuration management
farfan-pipeline calibration # Calibration operations
farfan-pipeline validate    # Validation tools
farfan-pipeline test        # Testing utilities
farfan-pipeline monitor     # Monitoring dashboard
```

### Python API

```python
from farfan_pipeline import UnifiedOrchestrator

# Initialize
orchestrator = UnifiedOrchestrator(config_path="config.yaml")

# Execute pipeline
result = orchestrator.execute_pipeline(input_pdf="document.pdf")

# Check result
if result.is_ok():
    macro_score = result.value.macro_score
    print(f"MacroScore: {macro_score}")
else:
    print(f"Error: {result.error}")
```

---

**Document Status**: ✅ Complete  
**Maintained By**: Development Team  
**Next Review**: With major version updates

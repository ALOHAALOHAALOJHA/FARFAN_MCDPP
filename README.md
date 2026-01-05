# F.A.R.F.A.N

**Framework for Advanced Retrieval and Forensic Analysis of Administrative Narratives**

A deterministic, mechanistic policy analysis pipeline for rigorous evaluation of Colombian territorial development plans (Planes de Desarrollo Territorial - PDT).

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)]()
[![Documentation](https://img.shields.io/badge/docs-complete-brightgreen.svg)](docs/)

---

## Quick Start

### Installation

```bash
# Create virtual environment
python3.12 -m venv farfan-env
source farfan-env/bin/activate  # On Windows: farfan-env\Scripts\activate

# Install package
pip install -e .
```

### Run Analysis

```bash
# Analyze a PDT document (modular questionnaire is default)
python src/orchestration/orchestrator.py \
  --pdt data/pdt_municipality_X.pdf \
  --cohort COHORT_2024 \
  --output output/municipality_X/

# Optionally use legacy monolith mode (not recommended)
USE_MODULAR_QUESTIONNAIRE=false python src/orchestration/orchestrator.py \
  --pdt data/pdt_municipality_X.pdf \
  --questionnaire canonic_questionnaire_central/questionnaire_monolith.json \
  --cohort COHORT_2024 \
  --output output/municipality_X/
```

### Validate Results

```bash
# Run validation suite
pytest -m "updated and not outdated" -v

# Check reproducibility
python scripts/run_validation_suite.py --test-pdt data/test/sample.pdf
```

---

## What is F.A.R.F.A.N?

F.A.R.F.A.N is a policy analysis system that:

- **Analyzes** 300 evaluation questions across 6 dimensions and 10 policy areas
- **Evaluates** through 584 analytical methods with 8-layer quality assessment
- **Produces** evidence-based reports with complete provenance tracking
- **Guarantees** deterministic, reproducible results (same inputs → same outputs)

### Key Features

- 🔒 **Deterministic Execution**: Absolute reproducibility via SIN_CARRETA doctrine
- 📊 **8-Layer Quality System**: Comprehensive method evaluation (@b, @u, @q, @d, @p, @C, @chain, @m)
- 🧮 **Choquet Integral Fusion**: Non-linear quality aggregation capturing synergies
- 📋 **Complete Provenance**: Every output traces back to source evidence
- ✅ **Zero-Tolerance Validation**: Hard gates enforce minimum quality standards
- 🔐 **HMAC Signatures**: Cryptographic integrity verification

---

## System Overview

### Analysis Pipeline

```
Input (PDT PDF) → Phase 0 (Validation) → Phase 1 (Ingestion) → 
Phase 2 (30 Executors) → Phase 3 (Layer Scoring) → 
Phase 4-7 (Hierarchical Aggregation) → Phase 8 (Recommendations) → 
Phase 9 (Report Assembly) → Phase 10 (Verification) → Output (Reports + Manifest)
```

### 8-Layer Quality Architecture

| Layer | Symbol | Focus | Weight Range |
|-------|--------|-------|--------------|
| **Intrinsic Quality** | `@b` | Method code quality | 0.15-0.20 |
| **Unit Quality** | `@u` | PDT structure (S/M/I/P) | 0.03-0.05 |
| **Question Fit** | `@q` | Method-question alignment | 0.06-0.10 |
| **Dimension Fit** | `@d` | Method-dimension compatibility | 0.05-0.08 |
| **Policy Area Fit** | `@p` | Domain knowledge | 0.04-0.07 |
| **Contract Compliance** | `@C` | Formal correctness | 0.07-0.10 |
| **Chain Integrity** | `@chain` | Data flow validity | 0.10-0.15 |
| **Governance** | `@m` | Institutional quality | 0.03-0.05 |

**Aggregation**: Choquet 2-additive integral with interaction terms

```
Cal(I) = Σ aₗ·xₗ + Σ aₗₖ·min(xₗ, xₖ)
```

### Dimensions & Policy Areas

**Dimensions (D1-D6)**:
- D1: INSUMOS (Inputs - Diagnosis & Resources)
- D2: ACTIVIDADES (Activities - Intervention Design)
- D3: PRODUCTOS (Outputs - Products & Deliverables)
- D4: RESULTADOS (Outcomes - Medium-term Results)
- D5: IMPACTOS (Impacts - Long-term Effects)
- D6: CAUSALIDAD (Theory of Change)

**Policy Areas (PA01-PA10)**:
- PA01: Gender Equality & Women's Rights
- PA02: Violence Prevention & Conflict
- PA03: Environment & Climate Change
- PA04: Economic, Social & Cultural Rights
- PA05: Victims' Rights & Peacebuilding
- PA06: Children, Youth & Protective Environments
- PA07: Land & Territory
- PA08: Human Rights Defenders
- PA09: Prison Rights Crisis
- PA10: Cross-border Migration

---

## Documentation

### Core Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System overview, component hierarchy, pipeline phases
- **[LAYER_SYSTEM.md](docs/LAYER_SYSTEM.md)** - Detailed explanation of 8-layer quality system
- **[FUSION_FORMULA.md](docs/FUSION_FORMULA.md)** - Choquet integral mathematics with worked examples
- **[DETERMINISM.md](docs/DETERMINISM.md)** - SIN_CARRETA doctrine, reproducibility guarantees

### Configuration & Tuning

- **[CONFIG_REFERENCE.md](docs/CONFIG_REFERENCE.md)** - Complete schema documentation for all config files
- **[WEIGHT_TUNING.md](docs/WEIGHT_TUNING.md)** - How to adjust fusion weights maintaining normalization
- **[THRESHOLD_GUIDE.md](docs/THRESHOLD_GUIDE.md)** - Quality thresholds, hard gates, PDT requirements

### User Guides

- **[CALIBRATION_GUIDE.md](docs/CALIBRATION_GUIDE.md)** - How to calibrate a new analytical method
- **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[VALIDATION_GUIDE.md](docs/VALIDATION_GUIDE.md)** - System integrity validation procedures

---

## Project Structure

```
F.A.R.F.A.N/
├── docs/                           # Documentation
│   ├── ARCHITECTURE.md
│   ├── LAYER_SYSTEM.md
│   ├── FUSION_FORMULA.md
│   ├── DETERMINISM.md
│   ├── CONFIG_REFERENCE.md
│   ├── WEIGHT_TUNING.md
│   ├── THRESHOLD_GUIDE.md
│   ├── CALIBRATION_GUIDE.md
│   ├── TROUBLESHOOTING.md
│   └── VALIDATION_GUIDE.md
│
├── src/
│   ├── orchestration/              # Pipeline orchestration
│   ├── methods_dispensary/         # 584 analytical methods
│   ├── canonic_phases/             # 11-phase pipeline
│   ├── farfan_pipeline/            # Core utilities
│   └── cross_cutting_infrastrucuture/
│       ├── capaz_calibration_parmetrization/
│       │   ├── calibration/        # Method quality scores (immutable)
│       │   └── parametrization/    # Runtime settings (traceable)
│       ├── irrigation_using_signals/SISAS/  # Signal system
│       └── contractual/dura_lex/   # Contract validation
│
├── tests/                          # Test suite (305 tests)
├── data/                           # Input data (PDTs)
├── output/                         # Analysis results
├── artifacts/                      # Intermediate artifacts
└── system/config/                  # System configuration

```

---

## Examples

### Basic Analysis

```python
from src.orchestration.orchestrator import Orchestrator

# Initialize orchestrator
orchestrator = Orchestrator(
    questionnaire_path="config/questionnaire_monolith.json",
    cohort="COHORT_2024",
    seed=42
)

# Run analysis
result = orchestrator.analyze_pdt(
    pdt_path="data/pdt_municipality_X.pdf",
    output_dir="output/municipality_X/"
)

# Access results
print(f"Macro Score: {result['macro_score']:.3f}")
print(f"Quality Band: {result['quality_band']}")
print(f"Verification Hash: {result['verification_hash']}")
```

### Custom Method Calibration

```python
from src.methods_dispensary.new_method import NewMethod
from src.calibration.calibrator import MethodCalibrator

# Develop method
method = NewMethod(seed=42)

# Calibrate
calibrator = MethodCalibrator()
calibration_scores = calibrator.calibrate(
    method=method,
    test_pdts=validation_set,
    num_runs=20
)

print(f"@b (Intrinsic Quality): {calibration_scores['@b']:.3f}")
print(f"  b_theory: {calibration_scores['b_theory']:.3f}")
print(f"  b_impl:   {calibration_scores['b_impl']:.3f}")
print(f"  b_deploy: {calibration_scores['b_deploy']:.3f}")
```

### PDT Quality Evaluation

```python
from src.farfan_pipeline.processing.spc_ingestion import analyze_pdt_structure

# Analyze PDT structure
pdt_structure = analyze_pdt_structure("data/pdt.pdf")

print(f"S (Structure): {pdt_structure['S']:.2f}")
print(f"M (Mandatory): {pdt_structure['M']:.2f}")
print(f"I (Indicators): {pdt_structure['I']:.2f}")
print(f"P (PPI):        {pdt_structure['P']:.2f}")
print(f"@u (Overall):   {pdt_structure['@u']:.2f}")
```

### Certificate Verification

```python
from src.orchestration.verification_manifest import verify_manifest

# Verify HMAC signature
is_valid = verify_manifest(
    manifest_path="output/verification_manifest.json",
    hmac_secret="PRODUCTION_KEY"
)

if is_valid:
    print("✓ Manifest integrity verified")
else:
    print("✗ Manifest may be tampered")
```

---

## Technical Requirements

### Runtime Environment

- **Python**: 3.12+
- **OS**: Linux, macOS, or Windows
- **Memory**: 4GB minimum, 8GB recommended
- **Storage**: 2GB for system, 10GB for data/artifacts

### Key Dependencies

- **FastAPI**: Web API framework
- **Pydantic v2**: Data validation
- **PyMC**: Bayesian inference
- **scikit-learn**: Machine learning
- **NetworkX**: Graph analysis
- **spaCy**: NLP
- **sentence-transformers**: Embeddings
- **pytest**: Testing
- **ruff**: Linting
- **mypy**: Type checking

### Quality Assurance

- **Test Coverage**: ≥80% (305 tests)
- **Type Coverage**: 100% (mypy strict mode)
- **Lint**: ruff check passes
- **Code Style**: 100-char line length, no comments unless complex

---

## Development

### Setup Development Environment

```bash
# Clone repository
git clone <repository_url>
cd farfan

# Create virtual environment
python3.12 -m venv farfan-env
source farfan-env/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Run Tests

```bash
# Run all tests
pytest tests/

# Run current tests only
pytest -m "updated and not outdated" -v

# Run with coverage
pytest --cov=src --cov-report=html
```

### Run Linters

```bash
# Lint check
ruff check src/

# Type check
mypy --strict src/orchestration/
mypy --strict src/farfan_pipeline/
```

### Format Code

```bash
# Format with black
black src/ tests/

# Or with ruff
ruff format src/ tests/
```

---

## Contributing

### Calibrating New Methods

See [CALIBRATION_GUIDE.md](docs/CALIBRATION_GUIDE.md) for complete procedure:

1. Implement method class with type hints and tests
2. Calibrate @b (intrinsic quality) components
3. Test on validation PDTs (assess @u sensitivity)
4. Map to questions (@q), dimensions (@d), policies (@p)
5. Run integration tests
6. Document and register in cohort manifest

### Adjusting Fusion Weights

See [WEIGHT_TUNING.md](docs/WEIGHT_TUNING.md) for normalization-preserving adjustments:

1. Identify reason for adjustment (empirical recalibration, domain specialization, etc.)
2. Apply weight adjustment procedure (single weight, pairwise exchange, group adjustment)
3. Validate normalization (Σ weights = 1.0)
4. Test on validation set (≥50 PDTs)
5. Document change in cohort changelog
6. Increment cohort version

---

## SIN_CARRETA Doctrine

**Sistema de Integridad No-Compensable para Análisis de Reproducibilidad, Rastreabilidad y Trazabilidad Absoluta**

F.A.R.F.A.N enforces absolute separation of:

- **Calibration** (immutable): Method quality scores, layer weights, thresholds
- **Parametrization** (traceable): Execution timeouts, memory limits, batch sizes

**Guarantees**:
- Same inputs + same calibration + same seed → **identical outputs** (bit-for-bit)
- SHA-256 hashing of all inputs
- HMAC-SHA256 signatures for verification manifests
- Deterministic RNG (derived seeds)
- UTC-only timestamps

See [DETERMINISM.md](docs/DETERMINISM.md) for complete specifications.

---

## License

Proprietary - Policy Analytics Research Unit

---

## Citation

If you use F.A.R.F.A.N in your research, please cite:

```bibtex
@software{farfan2024,
  title={F.A.R.F.A.N: Framework for Advanced Retrieval and Forensic Analysis of Administrative Narratives},
  author={Policy Analytics Research Unit},
  year={2024},
  version={1.0.0},
  url={<repository_url>}
}
```

---

## Contact

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Documentation**: See `docs/` directory
- **Troubleshooting**: See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

**Version**: 1.0.0  
**Last Updated**: 2024-12-16  
**Maintainers**: Policy Analytics Research Unit

# F.A.R.F.A.N. Mechanistic Policy Pipeline

## Architecture & Governance

The Global Nomenclature and Enforcement Authority (GNEA) protocol mandates a rigid directory structure and naming convention across the `farfan_pipeline` namespace. Phase execution is strictly confined to `farfan_pipeline.phases.Phase_XX` modules, with all external dependencies routed through the Unified Orchestrator at `farfan_pipeline.orchestration.orchestrator`. The root directory is protected against pollution, enforcing the placement of executable logic in `scripts/`, data in `artifacts/`, and documentation in `docs/`. Any import attempting to access the deprecated `cross_cutting_infrastructure` namespace triggers an immediate build failure.

## Phase Execution & Contracts

Each of the ten phases (0-9) operates under a strict Manifesto that defines input/output contracts, requiring Transition Certificates for any data flow between phases (P_N → P_N+1). Phase 0 Hardening acts as a pre-flight gatekeeper, verifying Questionnaire Integrity via SHA256 hashes, validating Method Registry counts, and executing Smoke Tests before pipeline initialization. These gates are non-negotiable; failure in Tier 1 validation (Identity/Assembly) forces immediate reformulation of the component.

## Signal Infrastructure (SISAS)

The Signal Infrastructure for SOTA Analysis Systems (SISAS) manages the propagation of irrigation signals across the pipeline, governed by the SISAS 2.0 Specification. Signal routing is optimized by the 'Acupuncture' framework, which utilizes an Inverted Signal Index and Lazy Loading to reduce routing complexity from O(n) to O(1). Pattern redundancy is minimized through a prototype inheritance chain that cascades definitions from Cluster to Policy Area to Dimension to Slot to Question.

```
FARFAN_MCDPP/
├── src/farfan_pipeline/           # Main source code
│   ├── orchestration/             # Orchestrator & UnifiedFactory
│   │   ├── orchestrator.py        # Unified orchestrator (2600+ lines)
│   │   ├── factory.py             # UnifiedFactory (component factory)
│   │   ├── seed_registry.py       # Determinism enforcement
│   │   └── gates/                 # Validation gates
│   ├── calibration/               # Calibration system
│   │   ├── calibration_core.py
│   │   ├── epistemic_core.py
│   │   └── registry.py
│   ├── methods/                   # Analytical methods (74 classes)
│   │   ├── analyzer_one.py
│   │   ├── derek_beach.py
│   │   ├── policy_processor.py
│   │   └── bayesian_multilevel_system.py
│   ├── phases/                    # Phase implementations
│   │   ├── Phase_00/              # Bootstrap & validation
│   │   ├── Phase_02/              # Evidence extraction
│   │   └── ...
│   └── infrastructure/            # SISAS & utilities
├── canonic_questionnaire_central/ # Canonical questionnaire
│   ├── governance/                # Method mappings (237 methods)
│   │   ├── METHODS_TO_QUESTIONS_AND_FILES.json
│   │   └── METHODS_OPERACIONALIZACION.json
│   └── config/                    # Schema definitions
├── tests/                         # Test suite
├── scripts/                       # Utility scripts
├── contracts/                     # Phase chain reports
├── docs/                          # Documentation
│   ├── TECHNICAL_RUNBOOK.md       # 🎯 UNIFIED Technical Runbook (v3.0.0)
│   └── RUNBOOK_MIGRATION_GUIDE.md # Migration from legacy runbooks
├── requirements.txt               # Core dependencies
├── requirements-dev.txt           # Development dependencies
├── pyproject.toml                 # Project configuration
└── README.md                      # This file
```

---

## API Reference

### Orchestrator

```python
from farfan_pipeline.orchestration.orchestrator import (
    OrchestratorConfig,
    UnifiedOrchestrator,
    ScoredMicroQuestion,
    MacroEvaluation,
    MethodExecutor,
    ResourceLimits,
    PhaseInstrumentation,
    Evidence,
    Orchestrator,  # Alias for UnifiedOrchestrator
)

Phase 5 implements a High Performance Area Aggregator that achieves 50x speedups through a combination of `asyncio` Parallel Processing, NumPy/Numba Vectorization, and Adaptive LRU Caching. The system is designed for Graceful Degradation, automatically falling back to safe baseline implementations if optional dependencies like Numba are unavailable, ensuring execution continuity without sacrificing correctness.

## Quality & Reporting

The reporting engine in Phase 9 generates artifacts across four distinct templates: Enhanced Report, Executive Dashboard, Technical Deep-Dive, and Original Report. All outputs are graded against strict quality thresholds: EXCELENTE (≥85%), BUENO (70-85%), ACEPTABLE (55-70%), and INSUFICIENTE (<55%). The CQVR Scoring System further stratifies contract quality into three tiers, ensuring that only components meeting the highest standards of Identity, Functionality, and Quality are deployed to production.

## Operations & Validation

### 📖 Complete Documentation

**For complete installation, configuration, and operation instructions, see:**

**[`docs/TECHNICAL_RUNBOOK.md`](docs/TECHNICAL_RUNBOOK.md)** - Comprehensive Technical Runbook (v3.0.0)

The Technical Runbook provides exhaustive coverage of:
- **Installation & Setup** (Section 24): One-command install, manual setup, Docker, verification
- **All Phase Commands** (Sections 3-12): Phase 0-9 detailed operations
- **SISAS Integration** (Section 13): Complete signal infrastructure reference
- **Troubleshooting** (Section 21): 12 subsections covering common issues and solutions
- **CQVR Quality Validation** (Section 25): Contract evaluation and remediation
- **CI/CD & Deployment** (Section 26): GitHub Actions, staging, production deployment
- **Complete Command Index** (Section 22): All 200+ commands with verification status

### Quick Start

```bash
# Install (one command)
bash install.sh
source farfan-env/bin/activate

# Verify installation
python scripts/verify_dependencies.py

# Run pipeline
farfan-pipeline
# or
python -m farfan_pipeline.entrypoint.main
```

### Legacy Documentation

**⛔ The following documents have been deprecated and merged into the Technical Runbook:**
- ~~`docs/DEPLOYMENT_GUIDE.md`~~ → See Sections 24, 26
- ~~`docs/TROUBLESHOOTING.md`~~ → See Section 21
- ~~`docs/design/OPERATIONAL_GUIDE.md`~~ → See Section 24
- ~~`DEPLOYMENT.md`~~ → See Sections 24, 26

For migration details, see [`docs/RUNBOOK_MIGRATION_GUIDE.md`](docs/RUNBOOK_MIGRATION_GUIDE.md)

Validation protocols demand rigorous statistical compliance, requiring expert correlation (r>0.7) and inter-rater reliability (κ>0.6) for model acceptance.

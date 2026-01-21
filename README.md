# F.A.R.F.A.N: Framework for Advanced Retrieval and Forensic Analysis of Administrative Narratives

**A Mechanistic, Deterministic Policy Analysis Pipeline for the Evaluation of Colombian Territorial Development Plans**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: Proprietary](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

| Attribute | Specification |
|-----------|---------------|
| **Version** | 2.0.0 |
| **Last Updated** | 2026-01-21 |
| **Doctrine** | SIN_CARRETA (System of Non-Compensable Integrity for Analysis of Reproducibility, Traceability, and Absolute Auditability) |
| **Architecture** | 11-Phase Canonical Pipeline + Signal Irrigation (SISAS) |
| **Scope** | 300 Questions × 10 Policy Areas × 6 Dimensions |
| **Methods** | 584 Analytical Methods (237 Mapped + 74 Classes) |
| **Provenance** | 100% Token-to-Source Traceability |
| **Python** | 3.12+ Required |

---

## 🚀 Quick Start

```bash
# 1. Clone and navigate
git clone <repository_url> FARFAN_MCDPP
cd FARFAN_MCDPP

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -e .

# 4. Download NLP models
python -m spacy download es_core_news_lg

# 5. Run tests
pytest tests/ -v
```

---

## 📋 Table of Contents

### Getting Started
- [Quick Start](#-quick-start)
- [Installation Guide](#installation-guide)
- [Configuration](#configuration)

### Architecture
1. [Introduction & Philosophy](#chapter-1-introduction--philosophy)
2. [Phase 0: The Pre-Execution Gatekeeper](#chapter-2-phase-0---the-pre-execution-gatekeeper)
3. [Phase 1: Ingestion & Acquisition](#chapter-3-phase-1---ingestion--acquisition)
4. [Phase 2: Orchestration & Epistemology](#chapter-4-phase-2---orchestration--epistemology)
5. [Phase 3: Normalization & Layer Scoring](#chapter-5-phase-3---normalization--layer-scoring)
6. [Phase 4: Dimensional Aggregation](#chapter-6-phase-4---dimensional-aggregation)
7. [Phase 5: Policy Area Integration](#chapter-7-phase-5---policy-area-integration)
8. [Phase 6: Validation & Quality Control](#chapter-8-phase-6---validation--quality-control)
9. [Phase 7: Strategic Analysis](#chapter-9-phase-7---strategic-analysis)
10. [Phase 8: Recommendations Engine](#chapter-10-phase-8---recommendations-engine)
11. [Phase 9: Report Assembly](#chapter-11-phase-9---report-assembly)
12. [Phase 10: Final Verification](#chapter-12-phase-10---final-verification)

### Systems
13. [SISAS: Signal Irrigation System](#chapter-13-sisas---signal-irrigation-system)
14. [Calibration & Parametrization](#chapter-14-calibration--parametrization)
15. [Canonic Questionnaire Central](#chapter-15-canonic-questionnaire-central)

### Reference
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Contributing](#contributing)

---

## Installation Guide

### System Requirements

| Requirement | Specification |
|-------------|--------------|
| **Python** | 3.12 or higher |
| **Memory** | 8GB RAM minimum, 16GB recommended |
| **Disk** | 10GB free space |
| **OS** | macOS 12+, Ubuntu 20.04+, Windows 10+ |

### macOS Prerequisites

```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install system dependencies
brew install libffi cairo pango gdk-pixbuf openjdk@17
```

### Ubuntu/Debian Prerequisites

```bash
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-venv python3.12-dev \
    build-essential libffi-dev libcairo2-dev libpango1.0-dev \
    default-jdk git curl
```

### Full Installation

```bash
# Clone repository
git clone <repository_url> FARFAN_MCDPP
cd FARFAN_MCDPP

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Install core dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Install project in editable mode
pip install -e .

# Install development dependencies (optional)
pip install -r requirements-dev.txt

# Download NLP models
python -m spacy download es_core_news_lg
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Core Configuration
FARFAN_MODE=DEV                    # DEV | PROD | TEST
FARFAN_SEED=42                     # Master RNG seed
FARFAN_LOG_LEVEL=INFO              # DEBUG | INFO | WARNING | ERROR
FARFAN_STRICT_VALIDATION=false     # Enable strict mode

# Resource Limits
FARFAN_MAX_MEMORY_MB=4096
FARFAN_MAX_WORKERS=4
FARFAN_TIMEOUT_SECONDS=300

# SISAS Configuration
FARFAN_SISAS_ENABLE=true
FARFAN_SISAS_BUS_QUEUE_SIZE=50000
```

---

## Project Structure

```
FARFAN_MCDPP/
├── src/farfan_pipeline/           # Main source code
│   ├── orchestration/             # Orchestrator & Factory
│   │   ├── orchestrator.py        # Unified orchestrator (2600+ lines)
│   │   ├── factory.py             # Component factory
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
│   └── TECHNICAL_RUNBOOK.md       # Complete technical reference
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

# Create configuration
config = OrchestratorConfig(
    municipality_name="Test Municipality",
    document_path="document.pdf",
    output_dir="./output",
    seed=42,
    max_workers=4,
)
```

### Resource Limits

```python
from farfan_pipeline.orchestration.orchestrator import ResourceLimits

limits = ResourceLimits(
    max_memory_mb=4096,
    max_cpu_percent=80.0,
    max_execution_time_seconds=3600,
    max_concurrent_tasks=4,
)

# Check limits
limits.check_memory(2048)  # True if within limits
limits.check_cpu(50.0)     # True if within limits
```

### Seed Registry (Determinism)

```python
from farfan_pipeline.orchestration.seed_registry import SeedRegistry

# Initialize at pipeline start
SeedRegistry.initialize(master_seed=42)

# Get derived seeds
random_seed = SeedRegistry.get_seed("random")
numpy_seed = SeedRegistry.get_seed("numpy")
```

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/farfan_pipeline --cov-report=html

# Run specific test files
pytest tests/test_orchestrator_signal_validation.py -v
pytest tests/test_aggregation_pipeline_integration.py -v

# Run by marker
pytest tests/ -m "not slow"        # Fast tests only
pytest tests/ -m integration       # Integration tests
pytest tests/ -k "orchestrator"    # Tests matching pattern
```

---

## Key Metrics

| Metric | Value |
|--------|-------|
| **Total Python Files** | 200+ |
| **Lines of Code** | 100,000+ |
| **Registered Classes** | 74 |
| **Mapped Methods** | 237 |
| **Test Files** | 50+ |
| **Phases** | 11 (0-10) |
| **Policy Areas** | 10 |
| **Dimensions** | 6 |
| **Questions** | 300 |

---

## Documentation

| Document | Description |
|----------|-------------|
| [TECHNICAL_RUNBOOK.md](docs/TECHNICAL_RUNBOOK.md) | Complete technical reference with all commands |
| [README.ES.md](README.ES.md) | Spanish language README |
| [COMPREHENSIVE_AUDIT_REPORT.md](COMPREHENSIVE_AUDIT_REPORT.md) | System audit report |
| [SISAS_INTEGRATION_REPORT.md](SISAS_INTEGRATION_REPORT.md) | SISAS integration details |

---

---

## Chapter 1: Introduction & Philosophy

F.A.R.F.A.N is not merely a software tool; it is a rigid epistemological framework operationalized as code. It addresses the crisis of reproducibility in public policy evaluation by enforcing a "mechanistic" approach. Unlike traditional evaluation methods that rely on "expert intuition" (often a cover for unverifiable subjectivity), F.A.R.F.A.N requires that every conclusion be the result of a deterministic chain of computation starting from raw evidence.

### The SIN_CARRETA Doctrine

The guiding philosophy is **SIN_CARRETA**: *Sistema de Integridad No-Compensable para Análisis de Reproducibilidad, Rastreabilidad y Trazabilidad Absoluta*.

1.  **Non-Compensability**: A failure in a lower layer (e.g., structural validity) cannot be compensated by excellence in a higher layer (e.g., rhetoric). If a plan fails Phase 0, it does not exist.
2.  **Absolute Traceability**: Every score, every claim, and every recommendation must trace back to specific token ranges in the source PDF with a cryptographic hash.
3.  **Immutable Calibration**: The rules of the game (weights, thresholds, methods) are frozen before the game begins. They cannot be adjusted "to make the results look better."

---

## Chapter 2: Phase 0 - The Pre-Execution Gatekeeper

**"Before we begin, we must agree on reality."**

Phase 0 is the bootstrap, validation, and integrity layer. It runs *before* any data is processed to ensure that the environment is safe, deterministic, and consistent.

### 2.1 The Validation Matrix

Phase 0 performs a rigid check of the runtime environment:
*   **RuntimeConfig Validation**: Verifies that all environment variables are set, types are correct, and values are within legal ranges.
*   **Seed Registry**: Initializes the master Random Number Generator (RNG) with a specific seed (default `42` or user-provided). This seed is then derived deterministically for all child processes (NumPy, Torch, Python Random).
*   **Dependency Integrity**: Checks the SHA-256 hashes of critical library files to ensure no "dependency drift" or supply chain attacks.

### 2.2 The Input Handshake

Before touching the user's PDF, Phase 0:
1.  Computes the **SHA-256** and **BLAKE3** hashes of the input file.
2.  Verifies the file against the `mime_type` allowlist (strictly `application/pdf`).
3.  Checks for PDF corruption or password protection.

### 2.3 The "Fail Fast" Guarantee

If any Phase 0 check fails, the pipeline aborts immediately with a distinct exit code. There is no "partial success" in Phase 0. A failure here generates a `bootstrap_failed=True` flag in the manifest, preventing any subsequent phase from running.

---

## Chapter 3: Phase 1 - Ingestion & Acquisition

**"Turning Chaos into Canon."**

Phase 1 is responsible for transforming the raw, unstructured binary of a PDF file into the **CanonPolicyPackage (CPP)**—a structured, queryable, and immutable representation of the document.

### 3.1 The SPC Ingestion Pipeline

The ingestion process is broken down into sub-steps:
1.  **Physical Extraction**: Text, images, and layout information are extracted using `pdfplumber` and `fitz`.
2.  **Spatial Reconstruction**: Text blocks are reassembled based on reading order algorithms, not just Z-order.
3.  **Visual Segmentation**: Computer vision (OpenCV) identifies tables, headers, and footers to separate "content" from "furniture."

### 3.2 Provenance Initialization

Phase 1 assigns a globally unique identifier (UUID) to every page and every content block. It creates the **Provenance Map**, which links every extracted string back to its:
*   Page Number
*   Bounding Box (x0, y0, x1, y1)
*   Byte Range in original file

This map is carried forward through all subsequent phases. If Phase 8 prints a quote, it can do so because Phase 1 preserved its address.

---

## Chapter 4: Phase 2 - Orchestration & Epistemology

**"The Engine of Truth."**

Phase 2 is the heart of F.A.R.F.A.N. It takes the structured CPP from Phase 1 and the questions from the Questionnaire, and it executes the 300 contracts that generate the analysis.

### 4.1 Epistemological Contracts

Phase 2 introduces a revolutionary concept in automated analysis: the **Epistemological Contract**. This is a formal specification that binds an evaluation question to a specific "Standard of Truth."

We define three strata of epistemological rigor, and every execution contract belongs to one of them:

#### Level 1: N1-EMP (Empirical Foundation)
*   **Philosophy**: Positivism.
*   **Nature**: "What is explicitly written?"
*   **Verification**: String matching, Regex, Named Entity Recognition.
*   **Falsifiability**: High. A claim is either present or absent.
*   **Role**: Establishing the base facts (e.g., "Does the plan mention 'Gender Violence'?").

#### Level 2: N2-INF (Inferential Processing)
*   **Philosophy**: Bayesian Inference / Constructivism.
*   **Nature**: "What is implied or structurally entailed?"
*   **Verification**: Probabilistic models, Causal Graphs, Topic Modeling.
*   **Falsifiability**: Medium (Statistical).
*   **Role**: Connecting facts (e.g., "Does the budget allocation *support* the gender violence goal?").

#### Level 3: N3-AUD (Audit & Critical Review)
*   **Philosophy**: Popperian Falsification / Critical Rationalism.
*   **Nature**: "Does this withstand scrutiny?"
*   **Verification**: Logic checks, Consistency validation, Cross-referencing external laws.
*   **Falsifiability**: Binary (Pass/Fail against a rule).
*   **Role**: Validating the integrity of the plan (e.g., "Is the total budget sum equal to the sum of its parts?").

### 4.2 The Method Dispensary

Phase 2 uses a **"Method Dispensary"** pattern. Instead of hardcoding logic into the orchestrator, we have a library of **240+ specialized methods** housed in monolithic analyzer classes.

*   **`PDETMunicipalPlanAnalyzer`**: 52 methods for analyzing territory-specific plans.
*   **`CausalExtractor`**: 28 methods for building causal graphs (Problem -> Cause -> Solution).
*   **`BayesianMechanismInference`**: 14 methods for calculating the probability of impact.

The **Orchestrator** reads a contract, sees `method_binding: "extract_financial_consistency"`, and requests that method from the Dispensary. This decoupling allows us to update methods without breaking the pipeline logic.

### 4.3 The Evidence Nexus

All results from the Dispensary are fed into the **Evidence Nexus**, a directed acyclic graph (DAG) where:
*   **Nodes** are pieces of evidence (facts, scores, tables).
*   **Edges** are inferential links (Fact A supports Conclusion B).

The Nexus ensures that no conclusion is an orphan; everything has a parent in the evidence.

---

## Chapter 5: Phase 3 - Normalization & Layer Scoring

**"Comparing Apples to Apples."**

The output of Phase 2 is a heterogeneous mix of booleans, floats, probability distributions, and text. Phase 3's job is **Normalization**.

### 5.1 The Universal Scale

Phase 3 maps all raw outputs to a standardized **[0.0, 100.0]** quality scale.
*   **Binary checks** become 0 or 100.
*   **Probabilities** are scaled linearly or log-linearly.
*   **Counts** (e.g., "number of stakeholders") are passed through sigmoid functions to reach saturation points.

### 5.2 The 8-Layer Quality Model

Phase 3 calculates scores for the 8 layers of the quality architecture:
1.  **@b (Intrinsic Quality)**: Is the method itself reliable?
2.  **@u (Unit Quality)**: Is the PDT structure sound?
3.  **@q (Question Fit)**: Did we answer the specific question?
4.  **@d (Dimension Fit)**: Is the answer relevant to the dimension (e.g., Results vs. Impacts)?
5.  **@p (Policy Fit)**: Does it align with the Policy Area standards?
6.  **@C (Contract Compliance)**: Did the executor follow the contract?
7.  **@chain (Chain Integrity)**: Is the evidence chain unbroken?
8.  **@m (Governance)**: Institutional maturity signals.

---

## Chapter 6: Phase 4 - Dimensional Aggregation

**"The Six Pillars of Development."**

Phase 4 aggregates the normalized scores from Phase 3 into the 6 canonical dimensions of the F.A.R.F.A.N framework.

1.  **D1: INSUMOS (Inputs)**: Diagnosis quality, financial resources, institutional capacity.
2.  **D2: ACTIVIDADES (Activities)**: Coherence of proposed actions, timeline feasibility.
3.  **D3: PRODUCTOS (Products)**: Definition of deliverables, quantification of goals.
4.  **D4: RESULTADOS (Outcomes)**: Medium-term changes, effectiveness indicators.
5.  **D5: IMPACTOS (Impacts)**: Long-term transformation, sustainability, alignment with SDGs.
6.  **D6: CAUSALIDAD (Causal Logic)**: The Theory of Change connecting D1 through D5.

Phase 4 uses **Choquet Integrals** to aggregate these scores. Unlike a simple average, the Choquet Integral accounts for **synergies** (doing A and B together is better than the sum of parts) and **redundancies**.

---

## Chapter 7: Phase 5 - Policy Area Integration

**"The Thematic Lens."**

While Phase 4 looks at the *structure* of the plan (Inputs -> Impacts), Phase 5 looks at the *content* across 10 strategic Policy Areas (PA):

*   **PA01**: Gender Equality
*   **PA02**: Violence Prevention
*   **PA03**: Environment & Climate
*   **PA04**: Economic Rights
*   **PA05**: Victims & Peace
*   **PA06**: Children & Youth
*   **PA07**: Land & Territory
*   **PA08**: Human Rights Defenders
*   **PA09**: Prison Crisis
*   **PA10**: Migration

Phase 5 creates a matrix: **6 Dimensions × 10 Policy Areas**. It highlights gaps—e.g., "This plan has great Activities (D2) for Environment (PA03), but zero Budget (D1) for Migration (PA10)."

---

## Chapter 8: Phase 6 - Validation & Quality Control

**"The Internal Auditor."**

Phase 6 is the self-correction phase. It runs a suite of internal consistency checks on the results generated by Phases 4 and 5.

*   **Consistency Check**: "Is the Macro score consistent with the Meso scores?"
*   **Outlier Detection**: "Why is the score for PA05 3 standard deviations lower than the others?"
*   **Flagging**: Phase 6 raises flags (Yellow/Red) for any anomaly. A "Red Flag" here can trigger a forced downgrade of the final rating in Phase 9.

---

## Chapter 9: Phase 7 - Strategic Analysis

**"From Data to Insight."**

Phase 7 moves beyond scoring to **interpretation**. It uses the "Carver" narrative engine to synthesize the findings.

*   **Cluster Analysis**: Identifies clusters of high performance and "deserts" of low performance.
*   **Trend Analysis**: Compares the current plan against the historical cohort (if available).
*   **Gap Analysis**: Specifically identifies the distance between the "Is" (Current Plan) and the "Ought" (Canonical Ideal).

---

## Chapter 10: Phase 8 - Recommendations Engine

**"What is to be Done?"**

Based on the gaps identified in Phase 7, Phase 8 generates specific, actionable recommendations.

*   **Bank of Actions**: Uses a database of standard corrective actions mapped to specific failure modes.
*   **Prioritization**: Ranks recommendations by "Impact vs. Effort."
*   **Tailoring**: Adjusts the language of the recommendation based on the municipality's category (Category 1-6) and capacity.

---

## Chapter 11: Phase 9 - Report Assembly

**"The Final Artifact."**

Phase 9 compiles all data, narratives, graphs, and recommendations into the final deliverables:
1.  **JSON Manifest**: The machine-readable full dump.
2.  **Executive Summary**: A 2-page high-level overview.
3.  **Full Technical Report**: The 80+ page detailed analysis.
4.  **Scorecards**: Visual heatmaps of performance.

Phase 9 handles the formatting, templating, and localized string generation (Spanish).

---

## Chapter 12: Phase 10 - Final Verification

**"The Seal of Authenticity."**

Phase 10 is the bookend to Phase 0. It ensures that what we produced is valid and has not been tampered with.

*   **Output Hashing**: Computes the SHA-256 hash of the final Report and Manifest.
*   **HMAC Signing**: Signs the output with the system's private key (if configured).
*   **Manifest Closure**: Sets `completed_at` timestamp and `success=True` in the verification manifest.
*   **Cleanup**: Securely deletes temporary files if retention is not requested.

---

## Chapter 13: SISAS - Signal Irrigation System

**Signal-Irrigated Smart Augmentation System**

SISAS is the "nervous system" of F.A.R.F.A.N. It allows the **Questionnaire (The Brain)** to send "signals" (patterns, keywords, heuristics) to the **Executors (The Limbs)** without hard-coding them in Python.

### 13.1 Signal Architecture

A **Signal** is a quintuple: `s = <id, type, content, source, confidence>`.

*   **Irrigation**: When the pipeline starts, the `SignalLoader` extracts all patterns defined in `questionnaire_monolith.json`.
*   **Transport**: These signals are loaded into the `SignalRegistry` (in-memory Redis-like structure).
*   **Consumption**: When an Executor runs, it asks SISAS: "Give me all signals related to 'Gender Budgeting'."
*   **Feedback**: Executors can report back "Signal Hit" or "Signal Miss," updating the confidence for future runs (in adaptive mode).

### 13.2 Signal Types
*   `detection_fuentes_oficiales`: patterns to find citations (e.g., "DANE", "CNMH").
*   `detection_indicadores_cuantitativos`: RegEx for finding stats.
*   `detection_cobertura_territorial`: Geographic entity matching.

**Invariant**: The Signal Hit Rate must be ≥ 95% for a healthy run.

---

## Chapter 14: Calibration & Parametrization

**"The Law vs. The Strategy."**

F.A.R.F.A.N strictly separates **Calibration** (The Law) from **Parametrization** (The Strategy).

### 14.1 Calibration (Immutable)
Stored in `cross_cutting_infrastructure/calibration`.
*   These are the scientific constants of the system.
*   Examples: The weight of Dimension 1 vs Dimension 2; The sigmoid slope for scoring; The threshold for a "Critical Failure."
*   **Rule**: Changing calibration invalidates previous results. It requires a version bump (1.0 -> 1.1).

### 14.2 Parametrization (Mutable)
Stored in `cross_cutting_infrastructure/parametrization`.
*   These are runtime settings that do not affect the *logic*, only the *execution*.
*   Examples: `MAX_MEMORY_MB`, `TIMEOUT_SECONDS`, `BATCH_SIZE`, `LOG_LEVEL`.
*   **Rule**: You can change parameters to optimize performance without affecting reproducibility of the *result scores*.

---

## Chapter 15: Canonic Questionnaire Central

**"The Source of Truth."**

The **Canonic Questionnaire** (`questionnaire_monolith.json`) is the single most important file in the project. It drives the entire pipeline.

*   **Monolithic Design**: It contains ALL 300 questions, their signals, their contract definitions, their weights, and their text.
*   **Versioning**: The Questionnaire has its own semantic versioning. The Pipeline Version and Questionnaire Version must be compatible.
*   **Structure**:
    ```json
    {
      "metadata": { ... },
      "dimensions": {
        "D1": {
          "policy_areas": {
            "PA01": {
              "questions": [
                {
                  "id": "Q001",
                  "text": "...",
                  "type": "N1-EMP",
                  "signals": [...]
                }
              ]
            }
          }
        }
      }
    }
    ```

Every Phase (from 2 to 9) reads this file to know what to do. If it's not in the Questionnaire, it doesn't happen.

---

*Copyright © 2026 Policy Analytics Research Unit. All Rights Reserved.*
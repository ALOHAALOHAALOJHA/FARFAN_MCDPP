# F.A.R.F.A.N. Mechanistic Policy Pipeline

## Architecture & Governance

The Global Nomenclature and Enforcement Authority (GNEA) protocol mandates a rigid directory structure and naming convention across the `farfan_pipeline` namespace. Phase execution is strictly confined to `farfan_pipeline.phases.Phase_XX` modules, with all external dependencies routed through the Unified Orchestrator at `farfan_pipeline.orchestration.orchestrator`. The root directory is protected against pollution, enforcing the placement of executable logic in `scripts/`, data in `artifacts/`, and documentation in `docs/`. Any import attempting to access the deprecated `cross_cutting_infrastructure` namespace triggers an immediate build failure.

## Phase Execution & Contracts

Each of the ten phases (0-9) operates under a strict Manifesto that defines input/output contracts, requiring Transition Certificates for any data flow between phases (P_N → P_N+1). Phase 0 Hardening acts as a pre-flight gatekeeper, verifying Questionnaire Integrity via SHA256 hashes, validating Method Registry counts, and executing Smoke Tests before pipeline initialization. These gates are non-negotiable; failure in Tier 1 validation (Identity/Assembly) forces immediate reformulation of the component.

## Signal Infrastructure (SISAS)

The Signal Infrastructure for SOTA Analysis Systems (SISAS) manages the propagation of irrigation signals across the pipeline, governed by the SISAS 2.0 Specification. Signal routing is optimized by the 'Acupuncture' framework, which utilizes an Inverted Signal Index and Lazy Loading to reduce routing complexity from O(n) to O(1). Pattern redundancy is minimized through a prototype inheritance chain that cascades definitions from Cluster to Policy Area to Dimension to Slot to Question.

## Performance & Optimization

Phase 5 implements a High Performance Area Aggregator that achieves 50x speedups through a combination of `asyncio` Parallel Processing, NumPy/Numba Vectorization, and Adaptive LRU Caching. The system is designed for Graceful Degradation, automatically falling back to safe baseline implementations if optional dependencies like Numba are unavailable, ensuring execution continuity without sacrificing correctness.

## Quality & Reporting

The reporting engine in Phase 9 generates artifacts across four distinct templates: Enhanced Report, Executive Dashboard, Technical Deep-Dive, and Original Report. All outputs are graded against strict quality thresholds: EXCELENTE (≥85%), BUENO (70-85%), ACEPTABLE (55-70%), and INSUFICIENTE (<55%). The CQVR Scoring System further stratifies contract quality into three tiers, ensuring that only components meeting the highest standards of Identity, Functionality, and Quality are deployed to production.

## Operations & Validation

Installation is standardized via standard Python tooling. Use `pip install -e .` to install the package and its dependencies in editable mode. Pipeline architecture can be verified using `bash scripts/validate_architecture.sh`. Policy analysis is executed through the canonical entry point:

```bash
farfan-pipeline
# or
python -m farfan_pipeline.entrypoint.main
```

Validation protocols demand rigorous statistical compliance, requiring expert correlation (r>0.7) and inter-rater reliability (κ>0.6) for model acceptance.

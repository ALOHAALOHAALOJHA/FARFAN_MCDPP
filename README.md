# F.A.R.F.A.N: Framework for Advanced Retrieval and Forensic Analysis of Administrative Narratives

**Version:** 1.0.0 (Gold Master) | **Status:** STABLE | **Doctrine:** SIN_CARRETA

---

## Chapter 1: The SIN_CARRETA Doctrine and System Identity

F.A.R.F.A.N is not a tool; it is a rigid epistemological enforcement engine designed to solve the crisis of reproducibility in public policy evaluation. It operates under the **SIN_CARRETA** doctrine (*Sistema de Integridad No-Compensable para Análisis de Reproducibilidad, Rastreabilidad y Trazabilidad Absoluta*), which mandates that no failure in structural validity can be compensated by rhetorical quality. This system treats policy documents not as literature but as data structures that must satisfy strict input/output contracts. The pipeline is **mechanistic and deterministic**: given the same PDF input and the same 64-bit seed (managed by the `SeedRegistry` singleton), the system produces bit-identical scores, recommendations, and reports, guaranteeing protection against "expert intuition" drift. Every claim produced by the system is backed by a cryptographic hash linking it to specific token ranges in the source document, ensuring 100% provenance and absolute auditability.

The system is currently declared **STABLE** (as of 2026-01-19) following a comprehensive thread-safety audit. All concurrency primitives (caches, metrics, signal buses) are protected by reentrant locks (`RLock`), ensuring that the parallel execution of the 300 micro-contracts does not introduce race conditions or state corruption.

---

## Chapter 2: The 11-Phase Canonical Pipeline

The analytical process is segmented into 11 discrete, stateful phases (0 through 10), each guarded by strict validation gates.

1.  **Phase 0 (Bootstrap & Gatekeeper):** Before any processing, the system validates the runtime environment, calculates SHA-256 hashes of the input PDF and the Immutable Questionnaire, and initializes the deterministic RNG. Failure here is fatal; there is no "partial boot."
2.  **Phase 1 (Ingestion & Matrix Decomposition):** The binary PDF is transmuted into a **CanonPolicyPackage (CPP)**. The document is decomposed into exactly 60 chunks corresponding to the intersection of 10 Policy Areas and 6 Dimensions.
3.  **Phase 2 (Epistemological Orchestration):** The **Method Dispensary** injects 348+ analytical methods into 30 Base Executors. These executors run against 300+ signal contracts to extract raw evidence (boolean facts, regex matches, tabular data) from the chunked document.
4.  **Phase 3 (Signal-Enriched Scoring):** Raw evidence is normalized onto a **[0.0, 3.0]** scale. This phase uses SISAS signals (Determinacy, Specificity, Empirical Support) to adjust scores dynamically based on the evidentiary quality, not just presence.
5.  **Phase 4 (Dimension Aggregation):** 300 micro-scores are fused into 60 Dimension scores using **Choquet Integrals**, a non-linear aggregation method that mathematically accounts for the synergy (positive interaction) or redundancy (negative interaction) between diverse evidence points.
6.  **Phase 5 (Area Aggregation):** 60 Dimension scores are aggregated into 10 Policy Area scores using a weighted arithmetic mean, producing the primary thematic assessment of the plan.
7.  **Phase 6 (Cluster Aggregation - MESO):** Policy Areas are grouped into 4 MESO clusters. This phase applies the **Adaptive Penalty Framework (APF)**, which reduces scores if the coefficient of variation (dispersion) within a cluster exceeds defined thresholds, punishing incoherence.
8.  **Phase 7 (Macro Synthesis):** The 4 cluster scores are synthesized into a single MACRO score using Cross-Cutting Coherence Analysis (CCCA). This score represents the holistic viability of the territorial plan.
9.  **Phase 8 (Recommendation Engine):** A rule engine generates MICRO, MESO, and MACRO recommendations. It employs a "Value Multiplier" logic, selecting interventions that offer the highest strategic leverage based on the detected gaps.
10. **Phase 9 (Report Assembly):** Jinja2 templates assemble the quantitative data, provenance chains, and generated narratives into human-readable HTML/PDF artifacts (Executive Dashboard, Technical Deep Dive).
11. **Phase 10 (Final Verification):** The system computes a final HMAC-SHA256 signature of the output artifacts, sealing the analysis and ensuring no post-processing tampering has occurred.

---

## Chapter 3: The 8-Layer Quality Architecture

Quality in F.A.R.F.A.N is not a single number but a composite vector evaluated across 8 distinct layers. Every analytical result is scrutinized against: **@b (Intrinsic Quality)**, verifying the method's theoretical soundness; **@u (Unit Quality)**, checking the structural integrity of the input document components; **@q (Question Fit)**, assessing semantic alignment between method and question; **@d (Dimension Fit)**, ensuring relevance to the specific causal dimension; **@p (Policy Fit)**, validating thematic alignment; **@C (Contract Compliance)**, strictly enforcing schema adherence; **@chain (Chain Integrity)**, ensuring unbroken data lineage; and **@m (Governance)**, evaluating institutional maturity signals. These layers are fused to produce the final confidence interval for every generated score.

---

## Chapter 4: Canonical Data Structures & The Questionnaire Monolith

The system's "Source of Truth" is the **Canonic Questionnaire** (`questionnaire_monolith.json`), a versioned artifact containing exactly 300 micro-questions. These questions cover a matrix of **10 Policy Areas** (PA01-PA10, e.g., Gender Equality, Victim Rights, Environment) and **6 Dimensions** (DIM01: Inputs, DIM02: Activities, DIM03: Products, DIM04: Results, DIM05: Impacts, DIM06: Causality). Any deviation from this 300-question structure triggers a schema validation failure. The system relies on **Canonical Notation** (e.g., `D3-Q12-PA04`) to address every data point, ensuring that data is never "lost in translation" between phases.

---

## Chapter 5: SISAS - Signal Irrigated System for Analytical Support

SISAS is the system's "nervous system," a transversal architecture that decouples signal detection from signal consumption. It operates on strict **Publication/Consumption Contracts**. Vehicles (publishers) emit signals onto typed buses (Structural, Integrity, Epistemic, Operational, Consumption, Contrast). Consumers (analyzers) subscribe to these buses to derive meta-insights without direct coupling. For example, a `FrequencySignal` on the Consumption Bus might trigger a Circuit Breaker in Phase 2 if a specific regex pattern consumes excessive CPU. Signals are **immutable** and **content-addressed** (BLAKE3 hashed), preventing signal drift during execution.

---

## Chapter 6: Governance, Enforcement, and GNEA

Development and operation are governed by the **Global Nomenclature Enforcement Architecture (GNEA)**.
*   **File Placement:** Python scripts live *only* in `src/` or `scripts/`. Documentation lives in `docs/`. Data lives in `artifacts/`. The root directory is restricted to configuration files (`pyproject.toml`, `setup.py`) and this README.
*   **Naming Conventions:** Phase modules must follow `phase{N}_{SS}_{OO}_{name}.py` (e.g., `phase2_10_00_factory.py`). Contracts must follow `Q{NNN}_{policy_area}_executor_contract.json`.
*   **Prohibitions:** No `temp`, `old`, or `backup` folders. No `print()` statements (use `structlog`). No distinct "utility" files that obscure their phase ownership.
*   **Sync Rules:** `METHODS_TO_QUESTIONS_AND_FILES.json` and `METHODS_OPERACIONALIZACION.json` must remain synchronized with exactly 240 methods.

---

## Chapter 7: Operational Command Reference

**Primary Execution:**
```bash
# Full Pipeline Run (Production Mode)
python -m farfan_pipeline.orchestration.cli --start-phase 0 --end-phase 9 --strict-validation --seed 42

# Phase 0 Bootstrap Check
python -m farfan_pipeline.phases.Phase_00.phase0_90_00_main --plan-pdf input.pdf --questionnaire questionnaire_monolith.json

# SISAS Irrigation Run
python -m farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.main run --csv-path sabana.csv --all
```

**Diagnostics & Health:**
```bash
# Check System Health (API)
curl http://localhost:8000/health

# SISAS Bus Statistics
python -m SISAS.main health --bus-stats

# Profiling Report
python -m farfan_pipeline.phases.Phase_02.phase2_95_00_executor_profiler
```

**Testing:**
```bash
# Run Integration Tests
pytest tests/test_phase0_complete.py

# Run Thread Safety Checks
pytest tests/test_phase3_performance.py
```

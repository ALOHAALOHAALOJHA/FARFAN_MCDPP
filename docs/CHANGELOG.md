# Changelog

All notable changes to the F.A.R.F.A.N project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Validation Status
- **Audit Certified**: SISAS subsystem certified Production Ready (Grade A+, 98%) as of 2026-01-14.
- **Forensic Audit**: Dependency audit completed 2026-01-10 (Verified removal of 8 unused packages).
- **Architecture**: Validated 8-layer hierarchy and Phase 0-3 consolidation.

### Added
- **SISAS Certification**: Completed Comprehensive Adversarial Audit for Signal-Irrigated System for Analytical Support (SISAS).
- **Signal Ordering**: Implemented full ordering support (HIGH > MEDIUM > LOW) for `SignalConfidence` (SISAS Enhancement).
- **Phase 3 Consolidation**: Consolidated scoring transformations into `src/canonic_phases/phase_3_scoring_transformation/`.
- **Phase 0 GAPs**: Integrated Performance Metrics (GAP-06), Retry Policy (GAP-07), Package Integrity (GAP-08), and Resource Monitoring (GAP-09).
- **Traceability**: Added `assignment_method` and `semantic_confidence` fields to `SmartChunk` and `Chunk` models (SPEC-002).
- **Contracts**: Enforced strict interfaces via `MicroQuestionRun` and `ScoredMicroQuestion` contracts.

### Changed
- **Signal Immutability**: Enforced immutability on `Signal` objects via `__setattr__` (Critical Fix).
- **Event Archival**: Changed `EventStore` behavior to archive processed events instead of deleting them (`clear_processed` -> `archive_processed`).
- **Nomenclature**: Standardized Phase 1 nomenclature to 'CPP' (Canon Policy Package), replacing 'SPC'.
- **Micro-Question Keys**: Standardized pipeline data flow to use `question_id` and `question_global` keys.
- **Imports**: Replaced legacy `canonic_phases` imports with relative imports in Phase 1.

### Fixed
- **Event Deletion**: Resolved critical defect where processed events were permanently deleted.
- **Dependency Cleanup**: Removed unused dependencies: `pypdf`, `PyPDF2`, `pillow`, `typing_extensions`, `pdfplumber`, `pytensor`, `semchunk`, `tiktoken`.
- **Chunk Iteration**: Corrected `ChunkGraph.chunks` iteration bug in Phase 1 (iterating keys instead of values).
- **Typo**: Fixed `cross_cutting_infrastrucuture` typo in imports (partial fix, physical directory remains).

### Removed
- **Unused Libraries**: Removed `pypdf`, `PyPDF2`, `pillow`, `typing_extensions`, `pdfplumber`, `pytensor`, `semchunk`, `tiktoken` from build requirements.

## [1.0.0] - 2024-12-16

### Added
- **System Documentation**: Added 12 detailed markdown files totaling >50,000 words.
    - `ARCHITECTURE.md`: System overview, 8-layer hierarchy, component diagram.
    - `LAYER_SYSTEM.md`: Detailed layer explanations (@b to @m), formulas, thresholds.
    - `FUSION_FORMULA.md`: Choquet integral mathematics and interaction term explanations.
    - `DETERMINISM.md`: SIN_CARRETA doctrine, hashing, HMAC signatures.
    - `CONFIG_REFERENCE.md`: Schemas for `intrinsic_calibration.json`, `questionnaire_monolith.json`, `fusion_weights.json`.
    - `WEIGHT_TUNING.md`: Procedures for adjusting fusion weights.
    - `THRESHOLD_GUIDE.md`: Quality thresholds and hard gates.
    - `CALIBRATION_GUIDE.md`: End-to-end method calibration guide.
    - `TROUBLESHOOTING.md`: Problem-solving guide.
    - `VALIDATION_GUIDE.md`: System integrity validation procedures.
- **Examples**:
    - `SustainabilityScorer` worked example.
    - S/M/I/P structure analysis example.
    - HMAC signature validation example.
- **Developer Resources**:
    - Architecture Diagrams.
    - API Code Snippets.
    - Validation Scripts.

### Validated
- **Fusion Weights**: Documented COHORT_2024 calibrated parameters (Linear: 0.67, Interaction: 0.33).
- **Interaction Terms**: Validated 3 key interactions: (@u, @chain), (@chain, @C), (@q, @d).

## [0.9.0] - 2024-12-09

### Added
- **Signal Intelligence**: Integrated Signal Intelligence Layer.
- **Metrics**: Added PDT quality metrics (S/M/I/P).
- **Filtering**: Added context-aware pattern filtering.
- **Registry**: Added Enhanced signal registry.

### Changed
- **Semantic Expansion**: Improved semantic expansion with 5x pattern multiplication.
- **Contract Validation**: Updated contract validation logic (covering 600 contracts).
- **Evidence Extraction**: Refactored evidence extraction (supporting 1,200 specifications).

### Fixed
- **Precision**: Reduced false positives by 60%.
- **Optimization**: Optimized memory usage.
- **Stability**: Improved deterministic execution stability.

# Governance Dashboard

## File Verdict Table

| File Path | Fate | Primary Reason |
|-----------|------|----------------|
| README.md | MERGE | Root definition of Doctrine and Architecture |
| docs/ARCHITECTURE.md | MERGE | Core architectural invariants |
| docs/DETERMINISM.md | MERGE | Detailed seed derivation logic |
| src/farfan_pipeline/phases/Phase_00/README.md | MERGE | Phase 0 specific implementation details |
| src/farfan_pipeline/phases/Phase_01/README.md | MERGE | Detailed breakdown of 16-subphase pipeline and Tríada |
| src/farfan_pipeline/phases/Phase_02/README.md | MERGE | Architecture of 300-contract system and Evidence Nexus |
| src/farfan_pipeline/phases/Phase_03/README.md | MERGE | Normalization and 8-Layer Model |
| src/farfan_pipeline/phases/Phase_04/README.md | MERGE | Choquet Aggregation and Adaptive Penalty |
| src/farfan_pipeline/phases/Phase_05/README.md | MERGE | Policy Area Integration matrix |
| src/farfan_pipeline/phases/Phase_06/README.md | MERGE | Cluster Aggregation and consistency checks |
| src/farfan_pipeline/phases/Phase_07/README.md | MERGE | Macro Evaluation and CCCA/SGD/SAS engines |
| src/farfan_pipeline/phases/Phase_08/README.md | MERGE | Recommendation Engine v3 architecture |
| src/farfan_pipeline/phases/Phase_09/README.md | MERGE | Report Assembly and Final Verification |
| docs/SISAS_ECOSYSTEM_DOCUMENTATION.md | MERGE | Detailed Signal Irrigation architecture |
| docs/TECHNICAL_RUNBOOK.md | MERGE | Operational procedures and Method Dispensary reference |

## Idea Retention Matrix

| Original File | Ideas Extracted (Est) | Ideas Discarded (Est) | Compression Ratio |
|---------------|-----------------------|-----------------------|-------------------|
| Root README & Arch | 12 | 150 | ~12:1 |
| Phase 00-02 | 8 | 400 | ~50:1 |
| Phase 03-06 | 10 | 300 | ~30:1 |
| Phase 07-09 | 8 | 250 | ~30:1 |
| SISAS & Runbook | 6 | 200 | ~33:1 |
| **TOTAL** | **44** | **1300** | **~30:1** |

## README Density Metrics

- **Total Paragraphs**: 15
- **Average Paragraph Length**: 720 characters
- **Density Score**: HIGH (Targeting >500 chars/para for dense technical prose)

## Integrity Flags

- **Known Unknowns**: Phase 10 implementation details missing from directory structure.
- **Explicit Assumptions**: Deterministic execution environment (Python 3.12, Linux/WSL) is required.
- **Conceptual Fragility**: Dependency on "Method Dispensary" implies high maintenance overhead if contracts change.

# SISAS Irrigation Inventory

**Version:** 1.0.0  
**Date:** 2026-01-19  
**Status:** CANONICAL  

---

## 1. Overview

The Irrigation Inventory provides a complete accounting of all irrigable items in the SISAS system. These items represent the targets that can receive signals during assessment processing.

---

## 2. Total Item Counts

| Item Category | Count | Description |
|---------------|-------|-------------|
| Micro Questions | 300 | Individual assessment questions (Q001-Q300) |
| Policy Areas | 10 | Policy area groupings (PA01-PA10) |
| Dimensions | 6 | Assessment dimensions (D1-D6) |
| Clusters | 4 | Dimension clusters (CL1-CL4) |
| SignalTypes | 17 | Signal type definitions |
| Phases | 10 | Processing phases (0-9) |
| **TOTAL** | **347** | Total irrigable items |

---

## 3. Detailed Breakdown

### 3.1 Micro Questions (300)

Questions are organized in 30 base questions × 10 policy areas = 300 total.

| Question Range | Policy Area | Base Questions |
|----------------|-------------|----------------|
| Q001-Q030 | PA01 | Base Q01-Q30 |
| Q031-Q060 | PA02 | Base Q01-Q30 |
| Q061-Q090 | PA03 | Base Q01-Q30 |
| Q091-Q120 | PA04 | Base Q01-Q30 |
| Q121-Q150 | PA05 | Base Q01-Q30 |
| Q151-Q180 | PA06 | Base Q01-Q30 |
| Q181-Q210 | PA07 | Base Q01-Q30 |
| Q211-Q240 | PA08 | Base Q01-Q30 |
| Q241-Q270 | PA09 | Base Q01-Q30 |
| Q271-Q300 | PA10 | Base Q01-Q30 |

### 3.2 Policy Areas (10)

| Code | Name | Questions | Weight |
|------|------|-----------|--------|
| PA01 | Gobernanza y Transparencia | Q001-Q030 | 12% |
| PA02 | Gestión Financiera | Q031-Q060 | 11% |
| PA03 | Recursos Humanos | Q061-Q090 | 10% |
| PA04 | Infraestructura y Tecnología | Q091-Q120 | 10% |
| PA05 | Gestión Documental | Q121-Q150 | 9% |
| PA06 | Participación Ciudadana | Q151-Q180 | 10% |
| PA07 | Planeación y Seguimiento | Q181-Q210 | 11% |
| PA08 | Control Interno | Q211-Q240 | 9% |
| PA09 | Gestión Ambiental | Q241-Q270 | 9% |
| PA10 | Gestión del Riesgo | Q271-Q300 | 9% |

### 3.3 Dimensions (6)

| Code | Name | Policy Areas | Weight |
|------|------|--------------|--------|
| D1 | Capacidad Institucional | PA01, PA02 | 20% |
| D2 | Gestión Administrativa | PA03, PA04 | 18% |
| D3 | Gestión Documental | PA05 | 12% |
| D4 | Participación y Transparencia | PA06, PA07 | 18% |
| D5 | Control y Seguimiento | PA08 | 15% |
| D6 | Sostenibilidad | PA09, PA10 | 17% |

### 3.4 Clusters (4)

| Code | Name | Dimensions | Weight |
|------|------|------------|--------|
| CL1 | Gobernanza | D1, D4 | 30% |
| CL2 | Operaciones | D2, D3 | 25% |
| CL3 | Control | D5 | 20% |
| CL4 | Sostenibilidad | D6 | 25% |

### 3.5 Signal Types (17)

| Category | Signal Types | Count |
|----------|--------------|-------|
| Extraction | EXTRACTION_RAW, EXTRACTION_PARSED, EXTRACTION_NORMALIZED | 3 |
| Assembly | ASSEMBLY_COMPONENT, ASSEMBLY_MERGED, ASSEMBLY_STRUCTURED | 3 |
| Enrichment | ENRICHMENT_CONTEXT, ENRICHMENT_METADATA, ENRICHMENT_CROSS_REF | 3 |
| Validation | VALIDATION_SCHEMA, VALIDATION_CONTENT, VALIDATION_CONSISTENCY | 3 |
| Scoring | SCORING_PRIMARY, SCORING_WEIGHTED, SCORING_NORMALIZED | 3 |
| Aggregation | AGGREGATION_PARTIAL, AGGREGATION_COMPLETE | 2 |
| Report | REPORT_DRAFT, REPORT_FINAL | 2 |
| **Total** | | **17** |

### 3.6 Processing Phases (10)

| Phase | Name | Primary Function |
|-------|------|------------------|
| 0 | Extraction | Extract raw data from inputs |
| 1 | Assembly | Assemble components into structures |
| 2 | Enrichment | Add context and metadata |
| 3 | Validation | Validate data integrity |
| 4 | Scoring | Calculate primary scores |
| 5 | Aggregation | Aggregate scores by dimension |
| 6 | Analysis | Analyze patterns and anomalies |
| 7 | Reporting | Generate reports |
| 8 | Integration | Export and integrate |
| 9 | Finalization | Seal and attest results |

---

## 4. Mapping: Question ID → Policy Area → Dimension

### 4.1 Complete Question Mapping

| Question Range | Policy Area | Dimension | Cluster |
|----------------|-------------|-----------|---------|
| Q001-Q030 | PA01 | D1 | CL1 |
| Q031-Q060 | PA02 | D1 | CL1 |
| Q061-Q090 | PA03 | D2 | CL2 |
| Q091-Q120 | PA04 | D2 | CL2 |
| Q121-Q150 | PA05 | D3 | CL2 |
| Q151-Q180 | PA06 | D4 | CL1 |
| Q181-Q210 | PA07 | D4 | CL1 |
| Q211-Q240 | PA08 | D5 | CL3 |
| Q241-Q270 | PA09 | D6 | CL4 |
| Q271-Q300 | PA10 | D6 | CL4 |

### 4.2 Reverse Mapping: Dimension → Questions

| Dimension | Questions | Total |
|-----------|-----------|-------|
| D1 | Q001-Q060 | 60 |
| D2 | Q061-Q120 | 60 |
| D3 | Q121-Q150 | 30 |
| D4 | Q151-Q210 | 60 |
| D5 | Q211-Q240 | 30 |
| D6 | Q241-Q300 | 60 |

### 4.3 Reverse Mapping: Cluster → Questions

| Cluster | Questions | Total |
|---------|-----------|-------|
| CL1 | Q001-Q060, Q151-Q210 | 120 |
| CL2 | Q061-Q150 | 90 |
| CL3 | Q211-Q240 | 30 |
| CL4 | Q241-Q300 | 60 |

---

## 5. Mapping: Phase → Allowed SignalTypes

### 5.1 Signal Type Availability by Phase

| Phase | Allowed Signal Types | Count |
|-------|---------------------|-------|
| 0 | EXTRACTION_RAW, EXTRACTION_PARSED, EXTRACTION_NORMALIZED | 3 |
| 1 | EXTRACTION_PARSED, EXTRACTION_NORMALIZED, ASSEMBLY_COMPONENT, ASSEMBLY_MERGED, ASSEMBLY_STRUCTURED | 5 |
| 2 | ASSEMBLY_STRUCTURED, ENRICHMENT_CONTEXT, ENRICHMENT_METADATA, ENRICHMENT_CROSS_REF | 4 |
| 3 | ENRICHMENT_CROSS_REF, VALIDATION_SCHEMA, VALIDATION_CONTENT, VALIDATION_CONSISTENCY | 4 |
| 4 | VALIDATION_CONSISTENCY, SCORING_PRIMARY, SCORING_WEIGHTED, SCORING_NORMALIZED | 4 |
| 5 | SCORING_WEIGHTED, SCORING_NORMALIZED, AGGREGATION_PARTIAL, AGGREGATION_COMPLETE | 4 |
| 6 | AGGREGATION_PARTIAL, AGGREGATION_COMPLETE | 2 |
| 7 | AGGREGATION_COMPLETE, REPORT_DRAFT, REPORT_FINAL | 3 |
| 8 | REPORT_FINAL | 1 |
| 9 | REPORT_FINAL | 1 |

### 5.2 Signal Type Origin and Destination

| Signal Type | Created In | Consumed In |
|-------------|------------|-------------|
| EXTRACTION_RAW | Phase 0 | Phase 0 |
| EXTRACTION_PARSED | Phase 0 | Phase 0, 1 |
| EXTRACTION_NORMALIZED | Phase 0 | Phase 0, 1 |
| ASSEMBLY_COMPONENT | Phase 1 | Phase 1 |
| ASSEMBLY_MERGED | Phase 1 | Phase 1 |
| ASSEMBLY_STRUCTURED | Phase 1 | Phase 1, 2 |
| ENRICHMENT_CONTEXT | Phase 2 | Phase 2 |
| ENRICHMENT_METADATA | Phase 2 | Phase 2 |
| ENRICHMENT_CROSS_REF | Phase 2 | Phase 2, 3 |
| VALIDATION_SCHEMA | Phase 3 | Phase 3 |
| VALIDATION_CONTENT | Phase 3 | Phase 3 |
| VALIDATION_CONSISTENCY | Phase 3 | Phase 3, 4 |
| SCORING_PRIMARY | Phase 4 | Phase 4 |
| SCORING_WEIGHTED | Phase 4 | Phase 4, 5 |
| SCORING_NORMALIZED | Phase 4 | Phase 4, 5 |
| AGGREGATION_PARTIAL | Phase 5 | Phase 5, 6 |
| AGGREGATION_COMPLETE | Phase 5 | Phase 5, 6, 7 |
| REPORT_DRAFT | Phase 7 | Phase 7 |
| REPORT_FINAL | Phase 7 | Phase 7, 8, 9 |

---

## 6. Hierarchy Visualization

```
                            ┌─────────────────────┐
                            │   GLOBAL SCORE      │
                            │   (Assessment)      │
                            └──────────┬──────────┘
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            │                          │                          │
            ▼                          ▼                          ▼
    ┌───────────────┐          ┌───────────────┐          ┌───────────────┐
    │    CL1        │          │    CL2        │          │  CL3 / CL4    │
    │  Gobernanza   │          │  Operaciones  │          │ Control/Sost  │
    └───────┬───────┘          └───────┬───────┘          └───────┬───────┘
            │                          │                          │
    ┌───────┴───────┐          ┌───────┴───────┐          ┌───────┴───────┐
    │               │          │               │          │               │
    ▼               ▼          ▼               ▼          ▼               ▼
┌───────┐       ┌───────┐  ┌───────┐       ┌───────┐  ┌───────┐       ┌───────┐
│  D1   │       │  D4   │  │  D2   │       │  D3   │  │  D5   │       │  D6   │
│Cap.Ins│       │Part.Tr│  │Gest.Ad│       │Gest.Do│  │Ctrl.Se│       │Sosten │
└───┬───┘       └───┬───┘  └───┬───┘       └───┬───┘  └───┬───┘       └───┬───┘
    │               │          │               │          │               │
┌───┴───┐       ┌───┴───┐  ┌───┴───┐       ┌───┴───┐  ┌───┴───┐       ┌───┴───┐
│PA01   │       │PA06   │  │PA03   │       │  PA05 │  │  PA08 │       │PA09   │
│PA02   │       │PA07   │  │PA04   │       │       │  │       │       │PA10   │
└───┬───┘       └───┬───┘  └───┬───┘       └───┬───┘  └───┬───┘       └───┬───┘
    │               │          │               │          │               │
    ▼               ▼          ▼               ▼          ▼               ▼
Q001-Q060     Q151-Q210   Q061-Q120     Q121-Q150   Q211-Q240     Q241-Q300
(60 Qs)       (60 Qs)     (60 Qs)       (30 Qs)     (30 Qs)       (60 Qs)
```

---

## 7. Irrigation Capacity Planning

### 7.1 Signal Volume Estimates

Based on a typical assessment with 300 questions:

| Phase | Signals Generated | Peak Rate (signals/sec) |
|-------|-------------------|-------------------------|
| 0 | 900 (3 per question) | 50 |
| 1 | 600 (2 per question) | 40 |
| 2 | 450 (1.5 per question) | 30 |
| 3 | 600 (2 per question) | 35 |
| 4 | 900 (3 per question) | 45 |
| 5 | 150 (aggregations) | 20 |
| 6 | 50 (analysis) | 10 |
| 7 | 20 (reports) | 5 |
| 8 | 10 (integrations) | 2 |
| 9 | 5 (finalization) | 1 |
| **Total** | **~3,685** | - |

### 7.2 Storage Requirements

| Item Type | Count | Storage per Item | Total Storage |
|-----------|-------|------------------|---------------|
| Questions | 300 | 10 KB | 3 MB |
| Signals | 3,685 | 2 KB | 7.4 MB |
| Audit Records | 3,685 | 1 KB | 3.7 MB |
| Reports | 20 | 500 KB | 10 MB |
| **Total per Assessment** | | | **~24 MB** |

---

## 8. Scope Registry Reference

### 8.1 Policy Area Codes

```json
{
  "PA01": {"name": "Gobernanza y Transparencia", "questions": 30},
  "PA02": {"name": "Gestión Financiera", "questions": 30},
  "PA03": {"name": "Recursos Humanos", "questions": 30},
  "PA04": {"name": "Infraestructura y Tecnología", "questions": 30},
  "PA05": {"name": "Gestión Documental", "questions": 30},
  "PA06": {"name": "Participación Ciudadana", "questions": 30},
  "PA07": {"name": "Planeación y Seguimiento", "questions": 30},
  "PA08": {"name": "Control Interno", "questions": 30},
  "PA09": {"name": "Gestión Ambiental", "questions": 30},
  "PA10": {"name": "Gestión del Riesgo", "questions": 30}
}
```

### 8.2 Dimension Codes

```json
{
  "D1": {"name": "Capacidad Institucional", "policy_areas": ["PA01", "PA02"]},
  "D2": {"name": "Gestión Administrativa", "policy_areas": ["PA03", "PA04"]},
  "D3": {"name": "Gestión Documental", "policy_areas": ["PA05"]},
  "D4": {"name": "Participación y Transparencia", "policy_areas": ["PA06", "PA07"]},
  "D5": {"name": "Control y Seguimiento", "policy_areas": ["PA08"]},
  "D6": {"name": "Sostenibilidad", "policy_areas": ["PA09", "PA10"]}
}
```

### 8.3 Cluster Codes

```json
{
  "CL1": {"name": "Gobernanza", "dimensions": ["D1", "D4"]},
  "CL2": {"name": "Operaciones", "dimensions": ["D2", "D3"]},
  "CL3": {"name": "Control", "dimensions": ["D5"]},
  "CL4": {"name": "Sostenibilidad", "dimensions": ["D6"]}
}
```

---

*End of Irrigation Inventory*

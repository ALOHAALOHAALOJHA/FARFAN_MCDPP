# Technical Specification: F.A.R.F.A.N Multi-Criteria Decision Policy Pipeline

## Empirical Corpus Irrigation System

| **Version** | **Date** | **Status** |
|-------------|----------|------------|
| 1.0.0 | January 11, 2026 | AUDIT COMPLETE - DETAILED IRRIGATION PLAN |

---

## 1. Executive Summary

This technical specification defines the complete data irrigation system for the F.A.R.F.A.N (Multi-Criteria Decision Policy Pipeline) framework.  The system manages the flow of empirical data from 4 root corpus files through 494 JSON files in the `canonic_questionnaire_central/` directory, connecting to the 10 canonical pipeline phases.

### 1.1 Current State Assessment

| Metric | Current State | Target State | Gap |
|--------|---------------|--------------|-----|
| Corpus integrated in CQC | 4/4 (100%) | 4/4 (100%) | ✅ Complete |
| Extractors implemented | 2/10 (20%) | 10/10 (100%) | 8 extractors |
| Effective wiring to consumers | ~15% | 85% | 70% |
| Alignment score | 2.9% | 85% | 82. 1% |
| Blocked questions | 159/300 (53%) | 0/300 | 159 questions |

---

## 2. System Architecture

### 2.1 Three-Tier Data Flow Model

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           TIER 1: ROOT CORPUS                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ├── corpus_empirico_calibracion_extractores.json    (666 lines)               │
│  ├── corpus_empirico_integrado. json                  (1,237 lines)             │
│  ├── corpus_empirico_normatividad.json               (269 lines)               │
│  └── corpus_thresholds_weights.json                  (351 lines)               │
│                                                                                 │
│  TOTAL:  2,523 lines of empirical calibration data                              │
│                                                                                 │
└──────────────────────────────────┬──────────────────────────────────────────────┘
                                   │
                                   ▼ IRRIGATION (Complete)
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    TIER 2: DERIVED FILES IN CQC                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ├── _registry/membership_criteria/_calibration/extractor_calibration.json     │
│  ├── _registry/questions/integration_map.json                                  │
│  ├── _registry/entities/normative_compliance.json                              │
│  └── scoring/calibration/empirical_weights.json                                │
│                                                                                 │
└──────────────────────────────────┬──────────────────────────────────────────────┘
                                   │
                                   ▼ CONSUMPTION (Partially Implemented)
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      TIER 3: PIPELINE CONSUMERS                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Phase 1: Extractors (MC01-MC10)      ← extractor_calibration.json             │
│  Phase 2: IrrigationSynchronizer      ← integration_map.json                   │
│  Phase 3: Scorers (@b, @p, @q, @d,    ← empirical_weights.json                 │
│           @u, @chain)                                                          │
│  Phase 3: @p PolicyAreaScorer         ← normative_compliance.json              │
│  Phase 4-7:  Aggregators               ← empirical_weights.json                 │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Irrigation Channel Specifications

### 3.1 Channel 1: Extractor Calibration

#### 3.1.1 File Mapping

| Property | Value |
|----------|-------|
| **Source** | `/corpus_empirico_calibracion_extractores.json` |
| **Source Size** | 666 lines |
| **Destination** | `/canonic_questionnaire_central/_registry/membership_criteria/_calibration/extractor_calibration.json` |
| **Destination Size** | ~700 lines |

#### 3.1.2 Data Schema

| Field | Description | Pipeline Usage |
|-------|-------------|----------------|
| `signal_type_catalog` | 10 signal types with empirical frequencies | Base for all extractors |
| `empirical_frequency` | Mean, min, max, std per type | Extraction validation |
| `extraction_patterns` | Regex patterns calibrated with 14 plans | Extraction patterns |
| `gold_standard_examples` | Manually validated examples | Testing and calibration |
| `confidence` | Confidence thresholds per pattern | Signal filtering |

#### 3.1.3 Consumer Implementation Status

| Consumer | File | Status | Notes |
|----------|------|--------|-------|
| `EmpiricalExtractorBase` | `empirical_extractor_base.py` | ✅ Implemented | Line 121 |
| `StructuralMarkerExtractor` | `structural_marker_extractor.py` | ✅ Implemented | Inherits from base |
| `QuantitativeTripletExtractor` | `quantitative_triplet_extractor.py` | ✅ Implemented | Inherits from base |
| `NormativeReferenceExtractor` | `normative_reference_extractor.py` | ✅ Implemented | Inherits from base |
| `FinancialChainExtractor` | `financial_chain_extractor.py` | ❌ Missing | Not created |
| `CausalVerbExtractor` | `causal_verb_extractor.py` | ⚠️ Partial | Inherits from base |
| `InstitutionalNER` | `institutional_ner_extractor.py` | ⚠️ Partial | Inherits from base |
| `PopulationDisaggregationExtractor` | N/A | ❌ Missing | Not created |
| `TemporalMarkerExtractor` | N/A | ❌ Missing | Not created |
| `SemanticRelationshipExtractor` | N/A | ❌ Missing | Not created |

#### 3.1.4 Current Loading Implementation

```python name=empirical_extractor_base. py
# File: src/farfan_pipeline/infrastructure/extractors/empirical_extractor_base.py
# Lines 114-123

def _default_calibration_path(self) -> Path:
    """Get default calibration file path."""
    return (
        Path(__file__).resolve().parent.parent. parent. parent
        / "canonic_questionnaire_central"
        / "_registry"
        / "membership_criteria"
        / "_calibration"
        / "extractor_calibration.json"
    )

def _load_calibration(self, calibration_file: Path) -> dict[str, Any]:
    """Load empirical calibration data."""
    with open(calibration_file) as f:
        data = json.load(f)
        return data. get("signal_type_catalog", {}).get(self.signal_type, {})
```

#### 3.1.5 Identified Gaps

**Gap 1.1: Missing Extractors (MC05, MC08, MC09)**

| Extractor ID | Status | Blocked Questions | Impacted Layers |
|--------------|--------|-------------------|-----------------|
| MC05 (Financial Chains) | ❌ Missing | 52 questions | `layer_chain_causal`, `CC_SOSTENIBILIDAD_PRESUPUESTAL` |
| MC08 (Causal Verbs) | ⚠️ Incomplete | 68 questions | `DIM06_CAUSALIDAD`, `layer_chain_causal` |
| MC09 (Institutional Network) | ⚠️ Incomplete | 39 questions | `layer_p_policy_area`, `layer_C_crosscutting` |

**Gap 1.2: Pattern Utilization**

| Metric | Value |
|--------|-------|
| Available patterns in calibration | 2,358 |
| Currently consumed patterns | 223 |
| Utilization rate | 9.4% |

---

### 3.2 Channel 2: Integration Mapping

#### 3.2.1 File Mapping

| Property | Value |
|----------|-------|
| **Source** | `/corpus_empirico_integrado. json` |
| **Source Size** | 1,237 lines |
| **Destination** | `/canonic_questionnaire_central/_registry/questions/integration_map.json` |
| **Destination Size** | ~1,200 lines |

#### 3.2.2 Data Schema

| Field | Description | Pipeline Usage |
|-------|-------------|----------------|
| `slot_to_signal_mapping` | 30 generic slots × 10 PA = 300 Q | Signal routing |
| `primary_signals` | Primary signals per question | Extraction prioritization |
| `secondary_signals` | Secondary signals | Enrichment |
| `expected_patterns` | Expected patterns per slot | Validation |
| `scoring_modality` | TYPE_A, B, C, D per question | Scorer selection |
| `empirical_availability` | Empirical frequency (0. 0-1.0) | Realistic expectations |

#### 3.2.3 Slot-to-Signal Mapping Structure

```json name=integration_map_example.json
{
  "D1-Q3_RECUR-ASIG":  {
    "slot":  "D1-Q3",
    "generic_question": "Does the PPI assign explicit monetary resources? ",
    "children_questions": ["Q003", "Q033", "Q063", "Q093", "Q123", "Q153", "Q183", "Q213", "Q243", "Q273"],
    "primary_signals": ["FINANCIAL_CHAIN", "STRUCTURAL_MARKER"],
    "secondary_signals": ["PROGRAMMATIC_HIERARCHY"],
    "scoring_modality": "TYPE_D",
    "weight": 0.30,
    "empirical_availability":  0.92
  }
}
```

#### 3.2.4 Consumer Implementation Status

| Consumer | File | Status | Notes |
|----------|------|--------|-------|
| `SignalQuestionIndex` | `signal_router.py` | ✅ Implemented | O(1) routing |
| `IrrigationSynchronizer` | `phase2_*` | ⚠️ Partial | Fallback to empty |
| `EvidenceNexus` | `phase2_80_00_evidence_nexus.py` | ⚠️ Partial | Lines 3281-3292 |
| `QuestionnaireSignalRegistry` | N/A | ❌ Missing | Pending creation |

#### 3.2.5 Identified Gaps

**Gap 2.1: Silent Fallback to Empty Mapping**

```python name=signal_router_current.py
# Current problematic implementation
try:
    with open(self. integration_map_path, "r", encoding="utf-8") as f:
        data = json. load(f)
    integration_map = data.get("farfan_question_mapping", {})
    slot_mappings = integration_map.get("slot_to_signal_mapping", {})
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Warning: Could not load integration_map.json: {e}.  Using empty mappings.")
    integration_map = {}  # ← SILENT FALLBACK TO EMPTY
```

| Issue | Impact | Required Solution |
|-------|--------|-------------------|
| Silent fallback | 0% signals reach correct questions | Fail-fast with clear error |

**Gap 2.2: Unused `empirical_availability` Field**

The `empirical_availability` field (range:  0.14 to 1.0) indicates empirical frequency but is not used for: 
- Adjusting scoring expectations
- Calibrating absence penalties
- Reporting realistic gaps

---

### 3.3 Channel 3: Normative Compliance

#### 3.3.1 File Mapping

| Property | Value |
|----------|-------|
| **Source** | `/corpus_empirico_normatividad.json` |
| **Source Size** | 269 lines |
| **Destination** | `/canonic_questionnaire_central/_registry/entities/normative_compliance.json` |
| **Destination Size** | ~260 lines |

#### 3.3.2 Data Schema

| Field | Description | Pipeline Usage |
|-------|-------------|----------------|
| `mandatory_norms_by_policy_area` | Required norms per PA | @p validation |
| `penalty_if_missing` | Penalties (0.2-0.5) | `CC_COHERENCIA` calculation |
| `universal_mandatory_norms` | 4 norms for all PAs | Base validation |
| `contextual_validation_rules` | Rules for PDET, ethnic territories | Contextual validation |
| `scoring_algorithm` | Calculation formula | Implementation reference |

#### 3.3.3 Mandatory Norms Structure

```json name=normative_compliance_example. json
{
  "PA05_victimas_paz": {
    "mandatory":  [
      {
        "norm_id": "Ley 1448 de 2011",
        "name": "Victims and Land Restitution Law",
        "reason": "Fundamental framework for conflict victims",
        "empirical_frequency": 5,
        "penalty_if_missing": 0.4
      },
      {
        "norm_id": "Decreto 893 de 2017",
        "name": "PDET",
        "penalty_if_missing": 0.3
      }
    ],
    "recommended": [
      {"norm_id": "Final Peace Agreement 2016"}
    ]
  }
}
```

#### 3.3.4 Consumer Implementation Status

| Consumer | File | Status | Notes |
|----------|------|--------|-------|
| `NormativeComplianceValidator` | N/A | ❌ Missing | Critical gap |
| `@p PolicyAreaScorer` | `phase3_*` | ⚠️ Reference only | Does not consume JSON |
| `CrossCuttingScorer` | `phase3_*` | ⚠️ Reference only | `CC_COHERENCIA_NORMATIVA` |
| `MC03 extractor` | `normative_reference_extractor.py` | ⚠️ Partial | Extracts but doesn't validate |

#### 3.3.5 Identified Gaps

**Gap 3.1: Missing `NormativeComplianceValidator`**

The `normative_compliance.json` file contains complete validation data but no validator exists to:
1. Load the configuration file
2. Compare cited norms vs. mandatory norms
3. Calculate penalties
4. Generate gap reports

**Gap 3.2: Unimplemented Scoring Algorithm**

```json name=scoring_algorithm_spec.json
{
  "scoring_algorithm": {
    "formula": "score = max(0.0, 1.0 - SUM(penalties)) for missing mandatory norms",
    "interpretation": {
      "EXCELLENT": "&gt;= 0.90",
      "GOOD": "0.75 - 0.89",
      "ACCEPTABLE": "0.60 - 0.74",
      "DEFICIENT": "&lt; 0.60"
    }
  }
}
```

**Gap 3.3: Ignored Contextual Validation Rules**

```json name=contextual_rules_spec.json
{
  "contextual_validation_rules":  {
    "pdet_municipalities": {
      "condition": "Municipality is in PDET list",
      "additional_mandatory": [
        {"norm_id": "Decreto 893 de 2017", "penalty_if_missing": 0.4}
      ]
    },
    "ethnic_territories": {
      "condition": "Population &gt; 10% indigenous or afro",
      "additional_mandatory": [
        {"norm_id": "Ley 70 de 1993"},
        {"norm_id": "Decreto 1953 de 2014"}
      ]
    }
  }
}
```

---

### 3.4 Channel 4: Thresholds and Weights

#### 3.4.1 File Mapping

| Property | Value |
|----------|-------|
| **Source** | `/corpus_thresholds_weights.json` |
| **Source Size** | 351 lines |
| **Destination** | `/canonic_questionnaire_central/scoring/calibration/empirical_weights.json` |
| **Destination Size** | ~320 lines |

#### 3.4.2 Data Schema

| Field | Description | Pipeline Usage |
|-------|-------------|----------------|
| `signal_confidence_thresholds` | Thresholds by signal type | Filtering in Phases 1-2 |
| `phase3_scoring_weights` | Weights for 7 layers | Phase 3 scorers |
| `aggregation_weights` | Weights for Phases 4-7 | Aggregators |
| `value_add_thresholds` | Minimum delta for useful signal | Deduplication |
| `capability_requirements` | Capabilities per signal | DBC validation |

#### 3.4.3 Scoring Weights Structure

```json name=empirical_weights_example.json
{
  "phase3_scoring_weights": {
    "layer_b_baseline": {
      "QUANTITATIVE_TRIPLET_present": 0.70,
      "QUANTITATIVE_TRIPLET_complete": 0.20,
      "QUANTITATIVE_TRIPLET_recent": 0.10
    },
    "layer_p_policy_area": {
      "NORMATIVE_REFERENCE_mandatory": 0.40,
      "keyword_coverage": 0.30,
      "POPULATION_DISAGGREGATION_relevant": 0.20,
      "INSTITUTIONAL_NETWORK":  0.10
    },
    "layer_chain_causal": {
      "CAUSAL_LINK_explicit": 0.50,
      "PROGRAMMATIC_HIERARCHY_linkage": 0.30,
      "FINANCIAL_CHAIN_allocation": 0.20
    }
  }
}
```

#### 3.4.4 Consumer Implementation Status

| Consumer | File | Status | Notes |
|----------|------|--------|-------|
| `BaselineScorer (@b)` | `phase3_*` | ⚠️ TODO | Hardcoded weights |
| `PolicyAreaScorer (@p)` | `phase3_*` | ⚠️ TODO | Does not load JSON |
| `QualityScorer (@q)` | `phase3_*` | ⚠️ TODO | Does not load JSON |
| `DimensionScorer (@d)` | `phase3_*` | ⚠️ TODO | Does not load JSON |
| `StructuralScorer (@u)` | `phase3_*` | ⚠️ TODO | Does not load JSON |
| `CausalScorer (@chain)` | `phase3_*` | ⚠️ TODO | Does not load JSON |
| `DimensionAggregator` | `phase4_*` | ⚠️ TODO | Hardcoded weights |
| `PolicyAreaAggregator` | `phase5_*` | ⚠️ TODO | Hardcoded weights |

#### 3.4.5 Identified Gaps

**Gap 4.1: No Scorer Loads `empirical_weights.json`**

```bash
$ grep -r "empirical_weights" src/farfan_pipeline/phases/
# Result: 0 matches in phase code
# Only appears in documentation and TODO comments
```

**Gap 4.2: Disconnected Aggregation Weights**

```json name=aggregation_weights_spec. json
{
  "phase5_policy_area_aggregation":  {
    "dimension_weights": {
      "DIM01_insumos": 0.15,
      "DIM02_actividades": 0.15,
      "DIM03_productos": 0.20,
      "DIM04_resultados": 0.25,
      "DIM05_impacto": 0.15,
      "DIM06_causalidad": 0.10
    }
  }
}
```

**Gap 4.3:  Unimplemented Value-Add Thresholds**

```json name=value_add_spec.json
{
  "value_add_thresholds": {
    "minimum_value_add": {
      "delta_score": 0.05,
      "description": "Signal must improve score by at least 5%"
    }
  }
}
```

---

## 4. Consolidated Irrigation Matrix

### 4.1 Complete Wiring Status

| Root Corpus | Derived CQC File | Consumers | Wiring Status |
|-------------|------------------|-----------|---------------|
| `calibracion_extractores` (666 lines) | `extractor_calibration.json` (700 lines) | `EmpiricalExtractorBase` | ✅ OK |
| | | `StructuralMarkerExtractor` | ✅ OK |
| | | `QuantitativeTripletExtractor` | ✅ OK |
| | | `NormativeReferenceExtractor` | ✅ OK |
| | | `FinancialChainExtractor` | ❌ Missing |
| | | `CausalVerbExtractor` | ⚠️ Partial |
| | | `InstitutionalNER` | ⚠️ Partial |
| `corpus_integrado` (1,237 lines) | `integration_map.json` (1,200 lines) | `SignalQuestionIndex` | ✅ OK |
| | | `IrrigationSynchronizer` | ⚠️ Fallback |
| | | `EvidenceNexus` | ⚠️ Partial |
| | | `QuestionnaireSignalRegistry` | ❌ Missing |
| `corpus_normatividad` (269 lines) | `normative_compliance.json` (260 lines) | `NormativeComplianceValidator` | ❌ Missing |
| | | `@p PolicyAreaScorer` | ⚠️ Unused |
| | | `CrossCuttingScorer` | ⚠️ Unused |
| | | `MC03 extractor` | ⚠️ Partial |
| `thresholds_weights` (351 lines) | `empirical_weights.json` (320 lines) | `BaselineScorer (@b)` | ⚠️ TODO |
| | | `PolicyAreaScorer (@p)` | ⚠️ TODO |
| | | `QualityScorer (@q)` | ⚠️ TODO |
| | | `DimensionScorer (@d)` | ⚠️ TODO |
| | | `CausalScorer (@chain)` | ⚠️ TODO |
| | | `Aggregators (Phase 4-7)` | ⚠️ TODO |

### 4.2 Wiring Summary

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Implemented | 5 consumers | ~20% |
| ⚠️ Partial/TODO | 12 consumers | ~50% |
| ❌ Missing/Not Exists | 7 consumers | ~30% |

---

## 5. Implementation Specifications

### 5.1 Priority 0 (Critical): Implement Missing Extractors

#### 5.1.1 `FinancialChainExtractor` (MC05)

**File to Create:** `src/farfan_pipeline/infrastructure/extractors/financial_chain_extractor.py`

**Available Calibration Data:**

```json name=financial_chain_calibration.json
{
  "FINANCIAL_CHAIN": {
    "empirical_frequency": {
      "montos_per_plan": {"mean": 285, "min": 20, "max": 377},
      "fuentes_per_plan": {"mean": 7, "min": 5, "max": 13}
    },
    "extraction_patterns": {
      "monto":  {
        "regex": "\\$\s*([0-9.,]+)\s*(millones? |billones?)?",
        "confidence": 0.90,
        "normalization": {"millones": "* 1000000", "billones": "* 1000000000000"}
      },
      "fuente": {
        "regex":  "(? :SGP|recursos\\s+propios|SGR|crédito|cofinanciación)",
        "confidence": 0.92
      }
    },
    "risk_thresholds": {
      "credito_max_pct": 0.20,
      "propios_min_pct": 0.03,
      "sgp_dependencia_max":  0.85
    },
    "gold_standard_examples": [
      {
        "plan": "Cajibío",
        "ppi_total": 288087496180,
        "distribution": {"SGP": 0.15, "ADRES": 0.63, "Propios": 0.0628}
      }
    ]
  }
}
```

**Questions Unblocked:** 52

| Slot | Questions | Description |
|------|-----------|-------------|
| D1-Q3 (RECUR-ASIG) | Q003, Q033, Q063, Q093, Q123, Q153, Q183, Q213, Q243, Q273 | Resources assigned in PPI |
| D3-Q3 (TRAZ-PRES) | Q078, Q108, Q138, Q168, Q198, Q228, Q258, Q288 | Budget traceability |
| D4-Q3 (JUST-AMB) | Q083, Q113, Q143, Q173, Q203, Q233, Q263, Q293 | Ambition justification vs resources |
| D5-Q5 (SOST-IMP) | Q095, Q125, Q155, Q185, Q215, Q245, Q275, Q295 | Impact sustainability |

#### 5.1.2 `CausalVerbExtractor` (MC08) - Complete Implementation

**Existing File:** `src/farfan_pipeline/infrastructure/extractors/causal_verb_extractor.py`

**Status:** Partial - Extracts verbs but doesn't construct causal chains

**Available Calibration Data:**

```json name=causal_verbs_calibration.json
{
  "CAUSAL_VERBS": {
    "empirical_frequency": {
      "top_10_verbs": [
        {"verb": "fortalecer", "mean": 52},
        {"verb": "implementar", "mean": 51},
        {"verb": "garantizar", "mean": 55}
      ],
      "conectores_causales": {
        "con_el_fin_de": {"mean": 18},
        "mediante":  {"mean": 22},
        "a_traves_de": {"mean": 35}
      }
    },
    "causal_chain_detection": {
      "pattern": "VERB + PRODUCT + CONNECTOR + RESULT",
      "confidence": 0.78
    }
  }
}
```

**Missing Functionality:**

| Feature | Description | Priority |
|---------|-------------|----------|
| Complete causal chain detection | VERB → PRODUCT → CONNECTOR → RESULT | High |
| `PROGRAMMATIC_HIERARCHY` linkage | Connect to program structure | High |
| Causal graph construction | Build directed graph of causality | Medium |

**Questions Unblocked:** 68

#### 5.1.3 `InstitutionalNER` (MC09) - Complete Implementation

**Existing File:** `src/farfan_pipeline/infrastructure/extractors/institutional_ner_extractor.py`

**Status:** Partial - Extracts entities but doesn't build institutional network

**Questions Unblocked:** 39

---

### 5.2 Priority 1 (High): Create Missing Validators

#### 5.2.1 `NormativeComplianceValidator`

**File to Create:** `src/farfan_pipeline/phases/Phase_3/validators/normative_compliance_validator.py`

**Responsibilities:**
1. Load `normative_compliance.json`
2. For each PA, verify cited mandatory norms
3. Calculate penalties for missing norms
4. Apply contextual rules (PDET, ethnic territories)
5. Generate `gap_report` with recommendations

**Interface Specification:**

```python name=normative_compliance_validator. py
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import json


@dataclass
class ValidationResult:
    policy_area: str
    score: float
    missing_norms: List[dict]
    recommendation: str
    contextual_adjustments: Optional[dict] = None


class NormativeComplianceValidator:
    """Validates normative compliance against empirical requirements."""
    
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = (
                Path(__file__).resolve().parent.parent.parent. parent
                / "canonic_questionnaire_central"
                / "_registry"
                / "entities"
                / "normative_compliance.json"
            )
        self.compliance_data = self._load_compliance_json(config_path)
    
    def _load_compliance_json(self, path: Path) -> dict:
        """Load compliance configuration with fail-fast behavior."""
        if not path.exists():
            raise FileNotFoundError(
                f"Critical:  normative_compliance.json not found at {path}"
            )
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def validate(
        self,
        plan_id: str,
        policy_area: str,
        cited_norms: List[str],
        context:  Optional[dict] = None
    ) -> ValidationResult:
        """
        Validate normative compliance for a policy area. 
        
        Args:
            plan_id: Unique identifier for the development plan
            policy_area: Policy area code (e.g., "PA05_victimas_paz")
            cited_norms: List of norm IDs cited in the plan
            context: Optional context for contextual rules (PDET, ethnic)
        
        Returns:
            ValidationResult with score, missing norms, and recommendations
        """
        mandatory = self.compliance_data["mandatory_norms_by_policy_area"]. get(
            policy_area, {}).get("mandatory", [])
        universal = self.compliance_data. get("universal_mandatory_norms", [])
        
        missing = []
        total_penalty = 0.0
        
        for norm in mandatory + universal:
            if norm["norm_id"] not in cited_norms:
                missing.append(norm)
                total_penalty += norm. get("penalty_if_missing", 0.2)
        
        # Apply contextual rules if context provided
        contextual_adjustments = None
        if context:
            contextual_adjustments = self._apply_contextual_rules(
                context, cited_norms
            )
            total_penalty += contextual_adjustments.get("additional_penalty", 0.0)
        
        score = max(0.0, 1.0 - total_penalty)
        
        return ValidationResult(
            policy_area=policy_area,
            score=score,
            missing_norms=missing,
            recommendation=self._generate_recommendation(missing, score),
            contextual_adjustments=contextual_adjustments
        )
    
    def _apply_contextual_rules(
        self, context: dict, cited_norms: List[str]
    ) -> dict:
        """Apply PDET and ethnic territory rules."""
        rules = self.compliance_data.get("contextual_validation_rules", {})
        adjustments = {"additional_penalty": 0.0, "triggered_rules": []}
        
        if context.get("is_pdet_municipality"):
            pdet_rules = rules.get("pdet_municipalities", {})
            for norm in pdet_rules.get("additional_mandatory", []):
                if norm["norm_id"] not in cited_norms:
                    adjustments["additional_penalty"] += norm.get(
                        "penalty_if_missing", 0.2
                    )
                    adjustments["triggered_rules"]. append("pdet_municipalities")
        
        if context. get("ethnic_population_pct", 0) > 0.10:
            ethnic_rules = rules.get("ethnic_territories", {})
            for norm in ethnic_rules.get("additional_mandatory", []):
                if norm["norm_id"] not in cited_norms:
                    adjustments["additional_penalty"] += norm.get(
                        "penalty_if_missing", 0.2
                    )
                    adjustments["triggered_rules"].append("ethnic_territories")
        
        return adjustments
    
    def _generate_recommendation(
        self, missing: List[dict], score: float
    ) -> str:
        """Generate actionable recommendation based on gaps."""
        if score >= 0.90:
            return "EXCELLENT:  Normative compliance meets all requirements."
        elif score >= 0.75:
            return f"GOOD: Consider adding references to:  {', '.join(n['norm_id'] for n in missing[: 2])}"
        elif score >= 0.60:
            return f"ACCEPTABLE: Missing critical norms: {', '.join(n['norm_id'] for n in missing)}"
        else:
            return f"DEFICIENT:  Urgent review required.  Missing {len(missing)} mandatory norms."
```

#### 5.2.2 `QuestionnaireSignalRegistry`

**File to Create:** `src/farfan_pipeline/phases/Phase_2/registries/questionnaire_signal_registry.py`

**Interface Specification:**

```python name=questionnaire_signal_registry.py
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import json


@dataclass
class SignalSpec:
    primary_signals: List[str]
    secondary_signals: List[str]
    scoring_modality: str
    weight:  float
    empirical_availability:  float


class QuestionnaireSignalRegistry:
    """Central registry for question-to-signal mappings."""
    
    def __init__(self, integration_map_path: Optional[Path] = None):
        if integration_map_path is None:
            integration_map_path = (
                Path(__file__).resolve().parent.parent.parent. parent
                / "canonic_questionnaire_central"
                / "_registry"
                / "questions"
                / "integration_map.json"
            )
        self._load_integration_map(integration_map_path)
    
    def _load_integration_map(self, path: Path) -> None:
        """Load integration map with fail-fast behavior."""
        if not path.exists():
            raise FileNotFoundError(
                f"Critical: integration_map.json not found at {path}. "
                "Pipeline cannot proceed without signal mappings."
            )
        
        with open(path, "r", encoding="utf-8") as f:
            data = json. load(f)
        
        mapping_data = data.get("farfan_question_mapping", {})
        self._slot_mappings = mapping_data.get("slot_to_signal_mapping", {})
        
        if not self._slot_mappings:
            raise ValueError(
                "Critical: slot_to_signal_mapping is empty. "
                "Cannot route signals to questions."
            )
        
        # Build reverse index:  question_id -> slot
        self._question_to_slot = {}
        for slot_id, slot_data in self._slot_mappings.items():
            for q_id in slot_data.get("children_questions", []):
                self._question_to_slot[q_id] = slot_id
    
    def get_signals_for_question(self, question_id: str) -> SignalSpec:
        """Get signal specification for a question."""
        slot_id = self._question_to_slot.get(question_id)
        if not slot_id:
            raise KeyError(f"Question {question_id} not found in integration map")
        
        slot_data = self._slot_mappings[slot_id]
        return SignalSpec(
            primary_signals=slot_data.get("primary_signals", []),
            secondary_signals=slot_data.get("secondary_signals", []),
            scoring_modality=slot_data.get("scoring_modality", "TYPE_A"),
            weight=slot_data.get("weight", 0.1),
            empirical_availability=slot_data.get("empirical_availability", 0.5)
        )
    
    def get_expected_count(self, question_id: str) -> int:
        """Get expected signal count based on empirical data."""
        spec = self.get_signals_for_question(question_id)
        return len(spec.primary_signals) + len(spec.secondary_signals)
    
    def get_empirical_availability(self, question_id: str) -> float:
        """Get empirical availability (0.0-1.0) for expectation calibration."""
        spec = self. get_signals_for_question(question_id)
        return spec.empirical_availability
    
    def get_scoring_modality(self, question_id: str) -> str:
        """Get scoring modality (TYPE_A, B, C, D) for scorer selection."""
        spec = self. get_signals_for_question(question_id)
        return spec.scoring_modality
```

---

### 5.3 Priority 2 (Medium): Connect Scorers to `empirical_weights.json`

**Files to Modify:**
- `src/farfan_pipeline/phases/Phase_3/scorers/baseline_scorer.py`
- `src/farfan_pipeline/phases/Phase_3/scorers/policy_area_scorer.py`
- `src/farfan_pipeline/phases/Phase_3/scorers/quality_scorer.py`
- `src/farfan_pipeline/phases/Phase_3/scorers/dimension_scorer.py`
- `src/farfan_pipeline/phases/Phase_3/scorers/causal_scorer.py`

**Implementation Pattern:**

```python name=base_scorer_pattern.py
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional
import json


class BaseScorer(ABC):
    """Abstract base class for all Phase 3 scorers."""
    
    def __init__(
        self,
        weights_path: Optional[Path] = None,
        layer_name: str = ""
    ):
        if weights_path is None:
            weights_path = (
                Path(__file__).resolve().parent.parent.parent.parent
                / "canonic_questionnaire_central"
                / "scoring"
                / "calibration"
                / "empirical_weights.json"
            )
        
        self.layer_name = layer_name
        self._load_weights(weights_path)
    
    def _load_weights(self, path: Path) -> None:
        """Load empirical weights with fail-fast behavior."""
        if not path.exists():
            raise FileNotFoundError(
                f"Critical: empirical_weights. json not found at {path}"
            )
        
        with open(path, "r", encoding="utf-8") as f:
            self. config = json.load(f)
        
        self.weights = self. config.get("phase3_scoring_weights", {}).get(
            self.layer_name, {}
        )
        self.thresholds = self.config.get("signal_confidence_thresholds", {})
        self.value_add_min = self.config.get("value_add_thresholds", {}).get(
            "minimum_value_add", {}).get("delta_score", 0.05)
    
    @abstractmethod
    def score(self, signals: Dict[str, Any]) -> float:
        """Calculate score based on signals and empirical weights."""
        pass
    
    def meets_value_add_threshold(self, delta:  float) -> bool:
        """Check if signal improvement meets minimum threshold."""
        return delta >= self.value_add_min
```

---

## 6. Implementation Roadmap

### 6.1 Phase 1: Critical Extractors (Weeks 1-2)

| Day | Task | Deliverable | Impact |
|-----|------|-------------|--------|
| 1-2 | Implement `FinancialChainExtractor` | Complete `.py` file | +52 questions |
| 3-4 | Complete `CausalVerbExtractor` | Causal chains functional | +68 questions |
| 5 | Complete `InstitutionalNER` | Institutional network | +39 questions |
| 6-7 | Unit tests + integration tests | 100% coverage | Validation |

**Success KPI:** Blocked questions:  159 → 0

### 6.2 Phase 2: Validators and Registries (Weeks 3-4)

| Day | Task | Deliverable | Impact |
|-----|------|-------------|--------|
| 8-9 | Create `NormativeComplianceValidator` | Complete validator | `CC_COHERENCIA` active |
| 10-11 | Create `QuestionnaireSignalRegistry` | Loaded registry | Correct routing |
| 12-13 | Connect scorers to `empirical_weights.json` | 6 scorers updated | Empirical weights |
| 14 | Integration tests with 14 plans | Coverage report | E2E validation |

**Success KPI:** Effective wiring: 15% → 70%

### 6.3 Phase 3: Optimization and Alignment (Weeks 5-6)

| Day | Task | Deliverable | Impact |
|-----|------|-------------|--------|
| 15-16 | Implement `ValueAddScorer` | Signal filtering | -30% noise |
| 17-18 | Pattern enrichment (992 → 5000) | Additional patterns | +400% coverage |
| 19-20 | Final calibration with corpus | Adjusted thresholds | +15% precision |
| 21 | Documentation + release notes | Updated docs | Maintainability |

**Success KPI:** Alignment score: 2.9% → 85%

---

## 7. Success Metrics

### 7.1 Quantitative Indicators

| Metric | Current | Post-Phase 1 | Post-Phase 2 | Post-Phase 3 |
|--------|---------|--------------|--------------|--------------|
| Extractors implemented | 2/10 | 5/10 | 7/10 | 10/10 |
| Questions unblocked | 141/300 | 300/300 | 300/300 | 300/300 |
| Effective wiring | 15% | 40% | 70% | 85% |
| Active patterns | 223 | 500 | 2,000 | 5,000 |
| Alignment score | 2.9% | 35% | 65% | 85% |

### 7.2 Qualitative Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| All extractors consume `extractor_calibration.json` | ⬜ Pending |
| All scorers consume `empirical_weights.json` | ⬜ Pending |
| `normative_compliance.json` validated by `NormativeComplianceValidator` | ⬜ Pending |
| `integration_map.json` used by `QuestionnaireSignalRegistry` | ⬜ Pending |
| No silent fallbacks to empty mappings | ⬜ Pending |
| Updated documentation in each consumer | ⬜ Pending |

---

## 8. Appendices

### 8.1 CQC File Inventory

| Category | Count | Location |
|----------|-------|----------|
| Total JSON files | 494 | `canonic_questionnaire_central/` |
| Individual questions | 300 | `dimensions/DIM*/questions/Q*. json` |
| Membership Criteria | 10 | `_registry/membership_criteria/MC*.json` |
| Binding maps | 3 | `_registry/membership_criteria/_bindings/` |
| Calibration | 1 | `_registry/membership_criteria/_calibration/` |
| Entities | 7 | `_registry/entities/` |
| Capabilities | 4 | `_registry/capabilities/` |
| Patterns | 17 | `_registry/patterns/by_category/` |
| Keywords | 21 | `_registry/keywords/by_policy_area/` |
| Analytical views | 7 | `_views/` |
| Clusters | 4 | `clusters/CL*/` |
| Dimensions | 6 | `dimensions/DIM*/` |
| Policy Areas | 10 | `policy_areas/PA*/` |
| Scoring | 2 | `scoring/` |

### 8.2 Cross-Reference Index

| Document | Purpose |
|----------|---------|
| `EMPIRICAL_CORPUS_INDEX. json` | Master index |
| `extractor_calibration.json` | Extractor calibration |
| `integration_map.json` | Q→Signals mapping |
| `normative_compliance.json` | Normative compliance |
| `empirical_weights.json` | Empirical weights |

---

| **Document Generated** | January 11, 2026 |
|------------------------|------------------|
| **Author** | GitHub Copilot - F. A.R.F.A.N Technical Audit |
| **Version** | 1.0.0 |
| **Status** | COMPLETE - Ready for Implementation |
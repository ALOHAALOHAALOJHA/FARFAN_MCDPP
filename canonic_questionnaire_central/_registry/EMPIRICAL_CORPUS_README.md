# Empirical Corpus Integration Guide

**Version:** 2.0.0
**Date:** 2026-01-06
**Status:** PRODUCTION READY

---

## Overview

Este directorio contiene datos empíricos calibrados de **14 planes de desarrollo territorial (PDT) reales** analizados durante 2024-2027. Los datos provienen de análisis batch con Google Notebook LM y validación experta.

### Corpus Statistics

| Metric | Value |
|--------|-------|
| **Plans Analyzed** | 14 |
| **Total Pages** | 2,956 |
| **Geographic Coverage** | Cauca, Caquetá, Chocó, Cesar |
| **Confidence Level** | 90% |
| **Representative Of** | Small municipalities (<100k) in conflict-affected regions |

---

## Empirical Files

### 1. Extractor Calibration Data

**File:** `_registry/membership_criteria/_calibration/extractor_calibration.json`
**Size:** 25 KB
**Original:** `corpus_empirico_calibracion_extractores.json`

#### Purpose
Calibrates signal extractors (MC01-MC10) with empirical patterns, frequencies, and thresholds validated against real PDT documents.

#### Contents
```json
{
  "signal_type_catalog": {
    "STRUCTURAL_MARKER": {
      "empirical_frequency": {
        "tables_per_plan": {"mean": 62, "std": 28},
        "graphs_per_plan": {"mean": 52, "std": 24}
      },
      "extraction_patterns": {
        "table_detection": {
          "regex": "Tabla\\s+(\\d+)[:\\s.-]+(.*)",
          "confidence": 0.95,
          "library": "pdfplumber"
        }
      }
    }
  }
}
```

#### Usage Example
```python
from pathlib import Path
import json

# Load calibration data
calibration_file = Path("_registry/membership_criteria/_calibration/extractor_calibration.json")
with open(calibration_file) as f:
    calibration = json.load(f)

# Configure extractor with empirical patterns
structural_config = calibration["signal_type_catalog"]["STRUCTURAL_MARKER"]
table_pattern = structural_config["extraction_patterns"]["table_detection"]["regex"]
confidence_threshold = structural_config["extraction_patterns"]["table_detection"]["confidence"]

# Use in extractor
class StructuralMarkerExtractor:
    def __init__(self, calibration_data):
        self.table_pattern = re.compile(calibration_data["extraction_patterns"]["table_detection"]["regex"])
        self.confidence_threshold = calibration_data["extraction_patterns"]["table_detection"]["confidence"]
```

#### Used By
- `StructuralMarkerExtractor` (Phase 1-SP2)
- `QuantitativeTripletExtractor` (Phase 1-SP6)
- `NormativeReferenceExtractor` (Phase 1-SP5)
- `FinancialChainExtractor` (Phase 1-SP7)
- `CausalVerbExtractor` (Phase 1-SP10)
- `InstitutionalNERExtractor` (Phase 1-SP11)

---

### 2. Question-Signal Integration Map

**File:** `_registry/questions/integration_map.json`
**Size:** 47 KB
**Original:** `corpus_empirico_integrado.json`

#### Purpose
Complete mapping of Q001-Q305 to signal types, enabling precise signal routing and irrigation.

#### Contents
```json
{
  "question_mappings": {
    "Q001": {
      "base_slot": "D1-Q1",
      "policy_area": "PA01",
      "expected_signals": {
        "QUANTITATIVE_TRIPLET": {"min": 3, "max": 10},
        "NORMATIVE_REFERENCE": {"min": 2, "max": 5},
        "INSTITUTIONAL_ENTITY": {"min": 2, "max": 8}
      },
      "scoring_modality": "TYPE_A"
    }
  }
}
```

#### Usage Example
```python
# Load integration map
with open("_registry/questions/integration_map.json") as f:
    integration_map = json.load(f)

# Configure QuestionnaireSignalRegistry
class QuestionnaireSignalRegistry:
    def __init__(self, integration_map):
        self.question_mappings = integration_map["question_mappings"]

    def get_expected_signals(self, question_id: str) -> Dict[str, Dict]:
        return self.question_mappings[question_id]["expected_signals"]

    def route_signals(self, question_id: str, detected_signals: List[Signal]) -> List[Signal]:
        expected = self.get_expected_signals(question_id)
        # Filter signals based on expected types
        return [s for s in detected_signals if s.signal_type in expected]
```

#### Used By
- `QuestionnaireSignalRegistry` (Phase 2)
- `IrrigationSynchronizer` (Phase 2)
- `EvidenceNexus` (Phase 2)
- All Aggregators (Phases 4-7)

---

### 3. Normative Compliance Data

**File:** `_registry/entities/normative_compliance.json`
**Size:** 8.5 KB
**Original:** `corpus_empirico_normatividad.json`

#### Purpose
Defines mandatory normative requirements per Policy Area with empirically validated penalties.

#### Contents
```json
{
  "policy_area_requirements": {
    "PA01": {
      "mandatory_norms": [
        {"norm_id": "ENT-NORM-004", "name": "Ley 1257 de 2008", "penalty_if_missing": -0.15},
        {"norm_id": "ENT-INT-003", "name": "CEDAW", "penalty_if_missing": -0.10}
      ],
      "empirical_citation_rate": 0.86,
      "compliance_threshold": 0.70
    }
  }
}
```

#### Usage Example
```python
# Load normative compliance
with open("_registry/entities/normative_compliance.json") as f:
    compliance_data = json.load(f)

# Configure PolicyAreaScorer
class PolicyAreaScorer:
    def __init__(self, compliance_data):
        self.pa_requirements = compliance_data["policy_area_requirements"]

    def validate_normative_compliance(self, pa_id: str, detected_norms: List[str]) -> float:
        requirements = self.pa_requirements[pa_id]
        mandatory = {n["norm_id"] for n in requirements["mandatory_norms"]}
        missing = mandatory - set(detected_norms)

        penalty = sum(
            n["penalty_if_missing"]
            for n in requirements["mandatory_norms"]
            if n["norm_id"] in missing
        )

        return max(0.0, 1.0 + penalty)
```

#### Used By
- `NormativeReferenceExtractor` (Phase 1-SP5)
- `@p PolicyAreaScorer` (Phase 3)
- `CrossCuttingScorer` (Phase 3)

---

### 4. Empirical Weights and Thresholds

**File:** `scoring/calibration/empirical_weights.json`
**Size:** 11 KB
**Original:** `corpus_thresholds_weights.json`

#### Purpose
Provides empirically calibrated confidence thresholds, aggregation weights, and scoring formulas.

#### Contents
```json
{
  "signal_confidence_thresholds": {
    "STRUCTURAL_MARKER": 0.80,
    "QUANTITATIVE_TRIPLET": 0.75,
    "NORMATIVE_REFERENCE": 0.85,
    "FINANCIAL_CHAIN": 0.70
  },
  "aggregation_weights": {
    "phase3_weights": {
      "baseline_scorer": 0.30,
      "policy_area_scorer": 0.25,
      "quality_scorer": 0.20,
      "dimension_scorer": 0.15,
      "structural_scorer": 0.10
    },
    "phase4_dimension_weights": {
      "DIM01": 0.20,
      "DIM02": 0.18,
      "DIM03": 0.17,
      "DIM04": 0.17,
      "DIM05": 0.15,
      "DIM06": 0.13
    }
  }
}
```

#### Usage Example
```python
# Load empirical weights
with open("scoring/calibration/empirical_weights.json") as f:
    weights = json.load(f)

# Configure scorers
class BaselineScorer:
    def __init__(self, weights_config):
        self.min_confidence = weights_config["signal_confidence_thresholds"]["QUANTITATIVE_TRIPLET"]
        self.weight = weights_config["aggregation_weights"]["phase3_weights"]["baseline_scorer"]

    def score(self, triplets: List[Signal]) -> float:
        valid_triplets = [t for t in triplets if t.confidence >= self.min_confidence]
        raw_score = len(valid_triplets) / expected_count if valid_triplets else 0.0
        return raw_score * self.weight
```

#### Used By
- All Phase 3 Scorers (`@b`, `@p`, `@q`, `@d`, `@u`, `@chain`)
- `DimensionAggregator` (Phase 4)
- `PolicyAreaAggregator` (Phase 5)
- `ClusterAggregator` (Phase 6)
- `MacroAggregator` (Phase 7)

---

## Integration Workflow

### Phase 1: Extractor Initialization

```python
# 1. Load extractor calibration
with open("_registry/membership_criteria/_calibration/extractor_calibration.json") as f:
    extractor_config = json.load(f)

# 2. Configure all extractors
structural_parser = StructuralMarkerExtractor(extractor_config["signal_type_catalog"]["STRUCTURAL_MARKER"])
triplet_extractor = QuantitativeTripletExtractor(extractor_config["signal_type_catalog"]["QUANTITATIVE_TRIPLET"])
normative_extractor = NormativeReferenceExtractor(extractor_config["signal_type_catalog"]["NORMATIVE_REFERENCE"])
# ... etc for all MC01-MC10

# 3. Extractors are now calibrated with empirical patterns
```

### Phase 2: Signal Routing

```python
# 1. Load integration map
with open("_registry/questions/integration_map.json") as f:
    integration_map = json.load(f)

# 2. Initialize registry
signal_registry = QuestionnaireSignalRegistry(integration_map)

# 3. Route signals to questions
for signal in detected_signals:
    target_questions = signal_registry.route_signal(signal)
    for question_id in target_questions:
        irrigate_signal(question_id, signal)
```

### Phase 3: Scoring with Empirical Weights

```python
# 1. Load weights
with open("scoring/calibration/empirical_weights.json") as f:
    weights = json.load(f)

# 2. Initialize scorers
baseline_scorer = BaselineScorer(weights)
policy_scorer = PolicyAreaScorer(weights)
quality_scorer = QualityScorer(weights)

# 3. Score with calibrated thresholds
scores = {
    "baseline": baseline_scorer.score(triplets),
    "policy": policy_scorer.score(norms),
    "quality": quality_scorer.score(triplets)
}
```

---

## Empirical Validation

### Statistical Power

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **Sample Size** | 14 plans | Small but targeted |
| **Confidence Level** | 90% | High confidence in patterns |
| **Geographic Diversity** | 4 departments | Reasonable coverage |
| **Population Range** | <100k | Focused on small municipalities |

### Coverage Matrix

| Policy Area | Coverage | Representative? |
|-------------|----------|-----------------|
| PA01 (Mujeres/Género) | 100% | ✅ Excellent |
| PA02 (Violencia/Conflicto) | 100% | ✅ Excellent |
| PA03 (Ambiente) | 100% | ✅ Excellent |
| PA04 (DESC) | 100% | ✅ Excellent |
| PA05 (Víctimas/Paz) | 100% | ✅ Excellent |
| PA06 (Niñez/Juventud) | 100% | ✅ Excellent |
| PA07 (Tierras/Territorios) | 93% | ✅ Good |
| PA08 (Líderes/Defensores) | 86% | 🟡 Acceptable |
| PA09 (Crisis/PPL) | 43% | ⚠️ Limited |
| PA10 (Migración) | 36% | ⚠️ Limited |

### Limitations

1. **Geographic Bias:** Focused on conflict-affected Andean/Pacific regions
2. **Size Bias:** No major cities (>100k population)
3. **PA09/PA10:** Limited coverage for prison/migration topics
4. **Temporal:** 2024-2027 plans only

### Mitigation Strategies

1. Use empirical data as **baseline**, not absolute truth
2. Allow confidence threshold adjustment per deployment context
3. Plan to expand corpus with additional plans from:
   - Major cities (Bogotá, Medellín, Cali)
   - Coastal regions (Atlántico, Bolívar)
   - PA09/PA10 focused municipalities

---

## Alignment Improvement Roadmap

### Current State
- **Alignment Score:** 2.9%
- **Bottleneck:** Only 992 expected_elements used vs 10,563 available resources

### Target States

| Phase | Target Alignment | Strategy |
|-------|------------------|----------|
| **Phase 1** | 50% | Full MC01-MC10 extractor implementation with empirical patterns |
| **Phase 2** | 70% | Complete Q001-Q305 signal routing using integration_map.json |
| **Phase 3** | 85% | Empirical weight calibration + capability system enforcement |

### Expected Impact

With full empirical corpus integration:
- **Patterns Used:** 1,723 → ~4,000 (inclusion of v3 patterns with validation)
- **Keywords Used:** 1,767 → 100% consumption
- **Entities Used:** 28 → 100% consumption + detection
- **Signal Types:** 4/10 → 10/10 implemented
- **Alignment:** 2.9% → >75%

---

## Next Steps

### Immediate Actions

1. ✅ **[DONE]** Copy empirical files to correct locations
2. ✅ **[DONE]** Create master index and documentation
3. 🔲 **[TODO]** Update Membership Criteria to reference `extractor_calibration.json`
4. 🔲 **[TODO]** Update `QuestionnaireSignalRegistry` to load `integration_map.json`
5. 🔲 **[TODO]** Update scorers to load `empirical_weights.json`

### Implementation Priorities

**HIGH PRIORITY:**
- Implement missing extractors (MC05, MC08, MC09) using calibration data
- Update existing extractors (MC01-MC04, MC06-MC07, MC10) with empirical patterns
- Configure signal routing with integration_map.json

**MEDIUM PRIORITY:**
- Implement normative compliance validator
- Calibrate all scorers with empirical weights
- Add confidence threshold validation

**LOW PRIORITY:**
- Expand corpus with additional plans
- Fine-tune patterns based on production feedback
- Update thresholds iteratively

---

## Support and Maintenance

### Questions?
Contact the CQC development team or refer to:
- `_registry/EMPIRICAL_CORPUS_INDEX.json` - Master index
- `_build/IMPLEMENTATION_PROGRESS_REPORT.md` - Implementation status
- `ESPECIFICACIÓN TÉCNICA UNIFICADA v2.0.0` - Full specification

### Updates
Empirical corpus should be updated:
- Quarterly with new plan analyses
- When coverage gaps are identified (PA09, PA10)
- When patterns show low precision/recall in production

---

**Last Updated:** 2026-01-06
**Version:** 2.0.0
**Status:** PRODUCTION READY

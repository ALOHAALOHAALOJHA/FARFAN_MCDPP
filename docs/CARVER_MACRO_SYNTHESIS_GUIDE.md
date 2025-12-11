# Carver Macro Synthesis: Usage Guide

## Overview

The `synthesize_macro()` method in DoctoralCarverSynthesizer v2.1 provides holistic assessment of development plans with explicit PA×DIM divergence analysis.

## Key Features

1. **Holistic Aggregation**: Combines multiple meso-question results with variance-aware scoring
2. **PA×DIM Divergence Analysis**: Explicit calculation of coverage across 10 policy areas × 6 dimensions
3. **Gap Identification**: Identifies critical gaps, low-coverage PAs and dimensions
4. **Calibrated Scoring**: Bayesian-inspired confidence with penalties for gaps and inconsistencies
5. **Actionable Recommendations**: Prioritized recommendations based on divergence patterns

## Usage Example

```python
from canonic_phases.Phase_two.carver import DoctoralCarverSynthesizer

# Initialize synthesizer
synthesizer = DoctoralCarverSynthesizer()

# Prepare meso-question results
meso_results = [
    {
        "score": 0.85,
        "question_id": "MESO_1",
        "question_text": "Cluster temático 1",
        # ... other fields
    },
    {
        "score": 0.75,
        "question_id": "MESO_2",
        "question_text": "Cluster temático 2",
    },
    # ... more meso results
]

# Prepare PA×DIM coverage matrix (60 cells: 10 PA × 6 DIM)
coverage_matrix = {
    ("PA01", "DIM01"): 0.85,
    ("PA01", "DIM02"): 0.78,
    # ... all 60 cells
    ("PA10", "DIM06"): 0.72,
}

# Synthesize macro-level assessment
macro_result = synthesizer.synthesize_macro(
    meso_results=meso_results,
    coverage_matrix=coverage_matrix,
    macro_question_text="¿El Plan de Desarrollo presenta una visión integral y coherente?"
)

# Access results
print(f"Macro Score: {macro_result['score']:.2f}")
print(f"Level: {macro_result['scoring_level']}")
print(f"\nHallazgos:")
for hallazgo in macro_result['hallazgos']:
    print(f"  - {hallazgo}")

print(f"\nFortalezas:")
for fortaleza in macro_result['fortalezas']:
    print(f"  + {fortaleza}")

print(f"\nDebilidades:")
for debilidad in macro_result['debilidades']:
    print(f"  - {debilidad}")

print(f"\nRecomendaciones:")
for i, rec in enumerate(macro_result['recomendaciones'], 1):
    print(f"  {i}. {rec}")

# Access divergence analysis
div_analysis = macro_result['divergence_analysis']
print(f"\nCobertura PA×DIM: {div_analysis['overall_coverage']:.2%}")
print(f"Gaps críticos: {div_analysis['critical_gaps_count']}")
print(f"PAs con baja cobertura: {', '.join(div_analysis['low_coverage_pas'])}")
```

## Output Structure

```python
{
    "score": 0.756,                    # Holistic score 0-1
    "scoring_level": "bueno",          # excelente/bueno/aceptable/insuficiente
    "aggregation_method": "holistic_assessment",
    "meso_results": [...],             # Original meso results
    "n_meso_evaluated": 4,
    
    # Global findings
    "hallazgos": [
        "El plan muestra un nivel bueno de articulación entre dimensiones.",
        "3 de 4 clusters muestran alto desempeño.",
        "Cobertura PA×DIM: 76% de células con nivel aceptable.",
        # ...
    ],
    
    # Strengths
    "fortalezas": [
        "Consistencia alta entre clusters temáticos.",
        "Cobertura equilibrada de policy areas y dimensiones.",
    ],
    
    # Weaknesses
    "debilidades": [
        "Déficit en áreas: PA05, PA07, PA09.",
        "Débil en dimensiones: Resultados, Impactos.",
    ],
    
    # Prioritized recommendations
    "recomendaciones": [
        "PRIORIDAD ALTA: Abordar 12 gaps críticos en matriz PA×DIM.",
        "Fortalecer policy areas: PA05, PA07.",
        "Reforzar dimensiones: Resultados, Impactos.",
        "Definir indicadores de resultado con línea base.",
        # ...
    ],
    
    # PA×DIM divergence analysis
    "divergence_analysis": {
        "overall_coverage": 0.756,
        "coverage_percentage": 0.717,
        "total_cells": 60,
        "cells_above_threshold": 43,
        "critical_gaps_count": 12,
        "critical_gaps": [
            ("PA05", "DIM01", 0.42),
            ("PA05", "DIM02", 0.38),
            # ... top 5
        ],
        "low_coverage_pas": ["PA05", "PA07", "PA09"],
        "low_coverage_dims": ["DIM04", "DIM05"],
        "pa_scores": {
            "PA01": 0.82,
            "PA02": 0.79,
            # ... all 10
        },
        "dim_scores": {
            "DIM01": 0.75,
            "DIM02": 0.78,
            # ... all 6
        },
        "divergence_patterns": [
            "Áreas de política con baja cobertura: PA05, PA07, PA09",
            "Dimensiones con baja cobertura: Resultados, Impactos",
            "PAs con más gaps críticos: PA05 (6 gaps), PA07 (4 gaps)",
        ],
    },
    
    # Metadata
    "metadata": {
        "question_text": "¿El Plan de Desarrollo presenta una visión integral y coherente?",
        "synthesis_method": "doctoral_carver_macro_v2",
        "base_score": 0.783,
        "coverage_adjusted": true,
    }
}
```

## PA×DIM Matrix Structure

The coverage matrix represents 60 cells:

```
         DIM01 DIM02 DIM03 DIM04 DIM05 DIM06
         (Ins) (Act) (Pro) (Res) (Imp) (Cau)
PA01      0.85  0.82  0.78  0.75  0.80  0.83
PA02      0.80  0.77  0.81  0.72  0.76  0.79
PA03      0.78  0.75  0.79  0.74  0.73  0.77
PA04      0.82  0.80  0.84  0.78  0.81  0.85
PA05      0.42  0.38  0.45  0.40  0.43  0.41  ← Critical gaps
PA06      0.76  0.74  0.77  0.71  0.75  0.78
PA07      0.55  0.52  0.58  0.53  0.51  0.54  ← Low coverage
PA08      0.79  0.81  0.83  0.77  0.80  0.82
PA09      0.51  0.48  0.53  0.49  0.47  0.50  ← Low coverage
PA10      0.74  0.72  0.76  0.70  0.73  0.75

         ↑     ↑                 ↑     ↑
         Low coverage dims:  DIM04, DIM05
```

## Scoring Algorithm

```
1. Base Score = mean(meso_scores) - variance_penalty
   - variance_penalty = min(0.15, variance * 0.3)

2. Coverage Score = mean(all PA×DIM cells)

3. Gap Penalty = min(0.25, critical_gaps_count * 0.05)

4. Final Score = 0.7 * base_score + 0.3 * coverage_score - gap_penalty

5. Scoring Levels:
   - excelente:     >= 0.85
   - bueno:         >= 0.70
   - aceptable:     >= 0.55
   - insuficiente:  <  0.55
```

## Divergence Analysis Thresholds

- **Acceptable Threshold**: 0.55 (cells >= this are considered acceptable)
- **Critical Threshold**: 0.50 (cells < this are critical gaps)

## Integration with Orchestrator

```python
# In Orchestrator._evaluate_macro()
def _evaluate_macro(self, phase_two_results: dict[str, Any]) -> MacroEvaluation:
    # Extract meso results from phase 2
    meso_results = phase_two_results.get("meso_results", [])
    
    # Extract coverage matrix from phase 1 or phase 2
    coverage_matrix = self._extract_coverage_matrix(phase_two_results)
    
    # Use Carver for macro synthesis
    from canonic_phases.Phase_two.carver import DoctoralCarverSynthesizer
    synthesizer = DoctoralCarverSynthesizer()
    
    macro_result = synthesizer.synthesize_macro(
        meso_results=meso_results,
        coverage_matrix=coverage_matrix,
        macro_question_text=self.questionnaire.macro_question.get("text", "")
    )
    
    # Convert to MacroEvaluation
    return MacroEvaluation(
        macro_score=macro_result["score"],
        macro_score_normalized=macro_result["score"],
        recommendations=macro_result["recomendaciones"],
        hallazgos=macro_result["hallazgos"],
        fortalezas=macro_result["fortalezas"],
        debilidades=macro_result["debilidades"],
    )
```

## Benefits

1. **Explicit Divergence**: No longer implicit - PA×DIM gaps are explicitly calculated and reported
2. **Actionable Insights**: Recommendations prioritized by severity and impact
3. **Calibrated Assessment**: Bayesian-inspired scoring with multiple penalty factors
4. **Transparent**: Full trace of base score, coverage adjustment, and penalties
5. **Carver Style**: Maintains minimalista Raymond Carver prose style in narratives

## Version History

- **v2.0**: Original Carver with micro/meso synthesis
- **v2.1**: Added `synthesize_macro()` with PA×DIM divergence analysis

---

**Author**: F.A.R.F.A.N Pipeline  
**Date**: 2025-12-11  
**Version**: 2.1.0-SOTA-MACRO

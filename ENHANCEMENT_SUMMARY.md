# Enhanced Recommendation Rules - Summary

**Version:** 3.0
**Date:** 2026-01-10
**File:** `/src/farfan_pipeline/phases/Phase_8/json_phase_eight/recommendation_rules_enhanced.json`

## Overview

The recommendation rules system has been significantly enhanced to provide comprehensive coverage across micro-meso-macro levels with multiple scoring scenarios aligned to different performance thresholds.

## Enhancement Statistics

### Previous Version (2.0)
- **Total Rules:** 119
- **MICRO:** 60 rules
- **MESO:** 54 rules
- **MACRO:** 5 rules

### Current Version (3.0)
- **Total Rules:** 535 (↑ 450% increase)
- **MICRO:** 420 rules (↑ 600% increase)
- **MESO:** 99 rules (↑ 83% increase)
- **MACRO:** 16 rules (↑ 220% increase)

## Key Enhancements

### 1. Multi-Threshold Scoring System (MICRO Level)

Previously, rules were defined with single thresholds per PA-DIM combination. Now, each combination has **6 scoring scenarios**:

| Scenario | Score Range | Urgency | Intervention Type |
|----------|-------------|---------|-------------------|
| **CRÍTICO** | 0-0.8 | INMEDIATA | Emergency intervention (3 months) |
| **DEFICIENTE** | 0.8-1.2 | ALTA | Major restructuring (6 months) |
| **INSUFICIENTE** | 1.2-1.65 | MEDIA | Significant improvement (6 months) |
| **ACEPTABLE** | 1.65-2.0 | BAJA | Minor adjustments (9 months) |
| **BUENO** | 2.0-2.4 | MANTENIMIENTO | Optimization (12 months) |
| **MUY BUENO** | 2.4-2.7 | OPTIMIZACIÓN | Excellence maintenance (12 months) |

**Coverage:** 10 PAs × 6 DIMs × 6 thresholds = **360 new MICRO rules**

### 2. Cross-Cluster Dependencies (MESO Level)

Added rules for **interdependent clusters** that require coordinated interventions:

- **Cluster Pairs:** 5 critical interdependencies
  - CL01-CL02: Seguridad-Social
  - CL01-CL03: Seguridad-Territorio
  - CL02-CL03: Social-Territorio
  - CL02-CL04: Social-Participación
  - CL03-CL04: Territorio-Participación

- **Score Bands:** 5 scenarios per pair (CRÍTICO, BAJO, MEDIO, ALTO, EXCELENTE)

**New MESO Rules:**
- Cross-cluster dependencies: 25 rules
- Multi-PA failure patterns: 8 rules
- Momentum tracking (improving/deteriorating/stagnant): 12 rules

### 3. System-Wide Management (MACRO Level)

Added comprehensive macro-level rules for:

#### Crisis Management
- **CRISIS-MULTISECTORIAL:** 3+ clusters in CRÍTICO/DEFICIENTE
- **CRISIS-FOCAL:** 1 cluster CRÍTICO, others ACEPTABLE+
- **ESTANCAMIENTO:** No significant changes in 6 months

#### Transformation Pathways
- **DEFICIENTE_A_ACEPTABLE:** Basic transformation (18 months)
- **ACEPTABLE_A_BUENO:** Continuous improvement (12 months)
- **BUENO_A_EXCELENTE:** Excellence pursuit (12 months)
- **EXCELENTE_SOSTENIBLE:** Excellence sustainability (ongoing)

#### Inter-Cluster Balance
- **DESEQUILIBRIO_EXTREMO:** 1 excellent cluster + 1 critical
- **DESEQUILIBRIO_MODERADO:** Variance > 20 points
- **EQUILIBRIO_BAJO:** All clusters low but balanced
- **EQUILIBRIO_ALTO:** All clusters high and balanced

## New Features

### 1. Enhanced Metadata
- **Version tracking:** Now at 3.0
- **Last updated timestamp:** ISO format
- **Comprehensive feature list:** 13 enhanced features
- **Level statistics:** Automatic counting and coverage description

### 2. Context-Specific Interventions

Each rule now includes interventions tailored to:
- **Dimension type** (DIM01-DIM06)
- **Severity level** (CRÍTICO to MUY BUENO)
- **Public Action area** (PA01-PA10)

### 3. Granular Verification Requirements

- **Dimension-specific verification methods**
- **Evidence requirements by dimension**
- **Measurement frequencies aligned to urgency**
- **Escalation paths with time thresholds**

### 4. Cost Estimation

- **Urgency-based cost multipliers**
- **Detailed breakdown:** Personnel, consultancy, technology
- **Funding sources:** SGP and Recursos Propios
- **Fiscal year tracking**

### 5. Approval Chains

- **Fast-track for urgent scenarios** (INMEDIATA/ALTA): 3 levels, max 10 days
- **Standard for routine scenarios:** 4 levels, max 50 days
- **Role-based decision authority**
- **Maximum days per level**

## Coverage by Public Action (PA)

| PA ID | Name | MICRO Rules | Coverage |
|-------|------|-------------|----------|
| PA01 | Política Pública de Género y Equidad | 36 | 6 DIMs × 6 scenarios |
| PA02 | Seguridad y Convivencia Ciudadana | 36 | 6 DIMs × 6 scenarios |
| PA03 | Educación y Desarrollo del Talento | 36 | 6 DIMs × 6 scenarios |
| PA04 | Infraestructura y Vivienda Digna | 36 | 6 DIMs × 6 scenarios |
| PA05 | Desarrollo Económico y Empleabilidad | 36 | 6 DIMs × 6 scenarios |
| PA06 | Salud Pública y Bienestar | 36 | 6 DIMs × 6 scenarios |
| PA07 | Justicia Transicional y Derechos Humanos | 36 | 6 DIMs × 6 scenarios |
| PA08 | Medio Ambiente y Sostenibilidad | 36 | 6 DIMs × 6 scenarios |
| PA09 | Cultura, Deporte y Recreación | 36 | 6 DIMs × 6 scenarios |
| PA10 | Participación Ciudadana y Gobernanza | 36 | 6 DIMs × 6 scenarios |

## Coverage by Dimension (DIM)

| DIM ID | Name | Verification Method |
|--------|------|---------------------|
| DIM01 | Línea Base y Diagnóstico | Auditoría de línea base y fuentes |
| DIM02 | Actividades y Cronograma | Revisión de cronogramas y hitos |
| DIM03 | BPIN y Presupuesto | Auditoría presupuestal y BPIN |
| DIM04 | Resultados Esperados | Medición de indicadores |
| DIM05 | Gestión de Riesgos | Revisión de matriz de riesgos |
| DIM06 | Datos Abiertos y Gobernanza | Auditoría de datos abiertos |

## Coverage by Cluster (CL)

| Cluster ID | Name | MESO Rules | Scenarios |
|------------|------|------------|-----------|
| CL01 | Seguridad y Paz | ~25 | Variance, cross-cluster, momentum |
| CL02 | Desarrollo Social | ~25 | Variance, cross-cluster, momentum |
| CL03 | Infraestructura y Territorio | ~25 | Variance, cross-cluster, momentum |
| CL04 | Participación y Cultura | ~24 | Variance, cross-cluster, momentum |

## Usage Examples

### Example 1: MICRO Rule - Critical Baseline Deficit
```json
{
  "rule_id": "REC-MICRO-PA01-DIM01-CRITICO",
  "level": "MICRO",
  "scoring_scenario": "CRÍTICO",
  "urgency": "INMEDIATA",
  "when": {
    "pa_id": "PA01",
    "dim_id": "DIM01",
    "score_lt": 0.8
  },
  "template": {
    "problem": "Critical deficit in baseline and diagnosis",
    "intervention": "Emergency baseline establishment - 30 days",
    "indicator": {
      "target": 1.3,
      "measurement_frequency": "semanal"
    }
  },
  "horizon": {
    "duration_months": 3
  }
}
```

### Example 2: MESO Rule - Cross-Cluster Dependency
```json
{
  "rule_id": "REC-MESO-CROSS-CL01-CL02-BAJO",
  "level": "MESO",
  "scoring_scenario": "DEPENDENCIA Seguridad-Social",
  "when": {
    "cluster_ids": ["CL01", "CL02"],
    "both_in_band": "BAJO",
    "interdependency": true
  },
  "template": {
    "intervention": "Integrated Security-Social plan with shared objectives"
  }
}
```

### Example 3: MACRO Rule - Crisis Management
```json
{
  "rule_id": "REC-MACRO-CRISIS-MULTISECTORIAL",
  "level": "MACRO",
  "scoring_scenario": "CRISIS-MULTISECTORIAL",
  "when": {
    "condition": "3+ clusters en CRÍTICO/DEFICIENTE",
    "system_wide": true
  },
  "responsible": {
    "entity": "Despacho del Alcalde",
    "role": "lidera respuesta integral"
  },
  "horizon": {
    "duration_months": 18
  }
}
```

## Implementation Notes

### Backward Compatibility
- All existing rules (version 2.0) are preserved
- New rules use distinct rule_id patterns
- Version field updated to 3.0
- Original file backed up with timestamp

### Data Sources
- All rules reference "Sistema de Seguimiento de Planes (SSP)"
- Measurement responsibility: "Oficina de Planeación Municipal"
- Verification: "Oficina de Control Interno"

### Legal Framework
- Rules aligned to Colombian legal mandates
- Specific laws referenced per PA
- Estatuto Orgánico Municipal as base

## Next Steps

1. **Integration Testing:** Validate rules against actual scoring data
2. **Performance Tuning:** Adjust thresholds based on historical data
3. **User Training:** Document usage patterns for different stakeholders
4. **Monitoring Dashboard:** Create visualization for rule activation patterns
5. **Feedback Loop:** Collect user feedback for rule refinement

## Files Generated

- **Main file:** `recommendation_rules_enhanced.json` (Version 3.0)
- **Backup:** `recommendation_rules_enhanced.json.backup.20260110_130737`
- **Generator script:** `generate_enhanced_rules.py`
- **Merge script:** `merge_rules.py`
- **New rules temp:** `new_enhanced_rules.json`

## Conclusion

The enhanced recommendation rules system now provides **comprehensive coverage** across all levels (micro-meso-macro) with **multiple scoring scenarios** aligned to **different performance thresholds**. This enables:

✅ **Precision:** 6 scoring scenarios per PA-DIM combination
✅ **Integration:** Cross-cluster dependency management
✅ **Strategy:** System-wide crisis and transformation pathways
✅ **Urgency:** Time-sensitive interventions based on severity
✅ **Accountability:** Clear responsible entities and approval chains
✅ **Measurability:** Specific indicators and verification methods

The system is now ready for implementation and can adapt to various municipal contexts and performance scenarios.

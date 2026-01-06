# Phase 8 Interfaces

**Document ID:** PHASE-8-INTERFACES  
**Version:** 1.0.0  
**Date:** 2026-01-05  
**Status:** ACTIVE  
**Classification:** CANONICAL

---

## Overview

This directory contains the complete interface specification for Phase 8 - Recommendation Engine. It documents all data flows into and out of the phase, processing contracts, and validation requirements.

## Interface Summary

### What is RECEIVED

| Contract ID | Data Type | Source | Required | Description |
|-------------|-----------|--------|----------|-------------|
| P8-IN-001 | `AnalysisResults` | Phase 7 | ✅ | Aggregated scoring results (MICRO/MESO/MACRO) |
| P8-IN-002 | `PolicyContext` | Phase 7 | ✅ | Policy area and dimension context |
| P8-IN-003 | `SignalData` | SISAS Registry | ❌ | Optional signal enrichment data |

### From WHOM

- **Phase 7 (Aggregation & Synthesis):** Primary upstream provider of scoring data
- **SISAS Signal Registry:** Optional signal enrichment source
- **QuestionnaireResourceProvider:** Threshold and monolith data

### What is PROCESSED

1. **Rule Loading & Validation**
   - Load recommendation rules from `json_phase_eight/recommendation_rules_enhanced.json`
   - Validate against JSON schema
   - Organize rules by level (MICRO/MESO/MACRO)

2. **MICRO-Level Recommendations**
   - Evaluate PA##-DIM## scores against thresholds
   - Generate question-specific recommendations
   - Apply template variable substitution

3. **MESO-Level Recommendations**
   - Analyze cluster performance (CL01-CL04)
   - Evaluate score bands and variance levels
   - Generate cluster-level strategic recommendations

4. **MACRO-Level Recommendations**
   - Assess plan-level aggregated metrics
   - Identify cross-cutting issues
   - Generate strategic plan recommendations

5. **Signal Enrichment (Optional)**
   - Pattern-based rule matching enhancement
   - Priority scoring based on signal density
   - Intervention template selection

### What is DELIVERED

| Contract ID | Data Type | Destination | Description |
|-------------|-----------|-------------|-------------|
| P8-OUT-001 | `dict[str, RecommendationSet]` | Phase 9 | Recommendations by level |
| P8-OUT-002 | `RecommendationMetadata` | Phase 9 | Generation metadata |

### To WHOM

- **Phase 9 (Report Generation):** Receives recommendations for final report
- **Orchestrator:** Receives execution status and metadata
- **Artifact Storage:** JSON/Markdown exports

## Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                        PHASE 8 INTERFACES                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────────────────────────┐         │
│  │  Phase 7    │───▶│  P8-IN-001: analysis_results    │         │
│  │ (Upstream)  │    │  P8-IN-002: policy_context      │         │
│  └─────────────┘    │  P8-IN-003: signal_data (opt)   │         │
│                     └─────────────┬───────────────────┘         │
│                                   │                              │
│                                   ▼                              │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              RECOMMENDATION ENGINE CORE                  │    │
│  │  ┌─────────┐  ┌─────────┐  ┌───────────────────────┐   │    │
│  │  │ MICRO   │  │  MESO   │  │        MACRO          │   │    │
│  │  │ Rules   │  │  Rules  │  │        Rules          │   │    │
│  │  └────┬────┘  └────┬────┘  └──────────┬────────────┘   │    │
│  │       │            │                   │                │    │
│  │       └────────────┴───────────────────┘                │    │
│  │                         │                               │    │
│  │                         ▼                               │    │
│  │  ┌─────────────────────────────────────────────────┐   │    │
│  │  │  Signal Enrichment (Optional)                    │   │    │
│  │  │  - Pattern matching                              │   │    │
│  │  │  - Priority scoring                              │   │    │
│  │  └─────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                   │                              │
│                                   ▼                              │
│                     ┌─────────────────────────────────┐         │
│                     │  P8-OUT-001: recommendations    │         │
│  ┌─────────────┐◀───│  P8-OUT-002: metadata           │         │
│  │  Phase 9    │    └─────────────────────────────────┘         │
│  │(Downstream) │                                                 │
│  └─────────────┘                                                 │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Validation Requirements

### Input Validation

All inputs MUST pass validation before processing:

```python
from interfaces import Phase8InterfaceValidator

validator = Phase8InterfaceValidator()
result = validator.validate_inputs(
    analysis_results=analysis_results,
    policy_context=policy_context,
    signal_data=signal_data
)
if not result.valid:
    raise InterfaceValidationError(result.errors)
```

### Output Validation

All outputs MUST be validated before delivery:

```python
result = validator.validate_outputs(
    recommendations=recommendations,
    metadata=metadata
)
```

## Files in This Directory

| File | Purpose |
|------|---------|
| `INTERFACE_MANIFEST.json` | Complete interface specification in JSON |
| `interface_validator.py` | Python validation implementation |
| `README.md` | This documentation file |
| `__init__.py` | Package initialization with exports |

## Integration Example

```python
from farfan_pipeline.phases.Phase_eight.interfaces import (
    Phase8InterfaceValidator,
    validate_phase8_inputs,
    validate_phase8_outputs,
)
from farfan_pipeline.phases.Phase_eight import RecommendationEngineAdapter

# Validate inputs
validation = validate_phase8_inputs(
    analysis_results=phase7_output.analysis_results,
    policy_context=phase7_output.policy_context
)

if not validation.is_valid:
    logger.error(f"Input validation failed: {validation.errors}")
    raise InterfaceContractViolation(validation.errors)

# Process recommendations
adapter = RecommendationEngineAdapter(
    rules_path="json_phase_eight/recommendation_rules_enhanced.json",
    schema_path="rules/recommendation_rules.schema.json"
)

recommendations = adapter.generate_all_recommendations(
    micro_scores=analysis_results.micro_scores,
    cluster_data=analysis_results.cluster_data,
    macro_data=analysis_results.macro_data
)

# Validate outputs
output_validation = validate_phase8_outputs(recommendations)
```

## See Also

- [PHASE_8_MANIFEST.json](../PHASE_8_MANIFEST.json) - Phase manifest
- [PHASE_8_CONSTANTS.py](../primitives/PHASE_8_CONSTANTS.py) - Phase constants
- [phase8_20_00_recommendation_engine.py](../phase8_20_00_recommendation_engine.py) - Core engine

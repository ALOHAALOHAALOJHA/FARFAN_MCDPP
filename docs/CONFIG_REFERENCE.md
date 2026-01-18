# F.A.R.F.A.N Configuration Reference

**Complete Schema Documentation for All Configuration Files**

Version: 1.0.0  
Last Updated: 2024-12-16

---

## Table of Contents

1. [Overview](#overview)
2. [Calibration Files](#calibration-files)
3. [Parametrization Files](#parametrization-files)
4. [Questionnaire Files](#questionnaire-files)
5. [Fusion Specification](#fusion-specification)
6. [Method Compatibility](#method-compatibility)
7. [Executor Configs](#executor-configs)
8. [File Locations](#file-locations)

---

## Overview

F.A.R.F.A.N uses JSON configuration files organized by the **SIN_CARRETA doctrine**:

- **Calibration** (immutable): Method quality scores, layer weights, thresholds
- **Parametrization** (traceable): Execution settings, timeouts, resource limits
- **Questionnaire** (immutable): Question definitions, patterns, hierarchies
- **Fusion** (calibrated): Choquet integral weights and interaction terms
- **Compatibility** (calibrated): Method-question-dimension-policy mappings

All files use cohort versioning (e.g., `COHORT_2024`) to ensure reproducibility.

---

## Calibration Files

### 1. intrinsic_calibration.json

**Purpose**: Defines base layer (@b) quality scores for all methods.

**Location**: `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/COHORT_2024_intrinsic_calibration.json`

**Schema**:

```json
{
  "_metadata": {
    "version": "string",
    "description": "string",
    "last_updated": "ISO-8601 timestamp",
    "authority": "SIN_CARRETA",
    "implementation_wave": "string",
    "wave_label": "string"
  },
  "base_layer": {
    "symbol": "@b",
    "name": "Base Layer",
    "description": "Intrinsic quality of the method code",
    "aggregation": {
      "method": "weighted_sum",
      "weights": {
        "b_theory": "float [0.0-1.0]",
        "b_impl": "float [0.0-1.0]",
        "b_deploy": "float [0.0-1.0]"
      }
    }
  },
  "components": {
    "b_theory": {
      "description": "string",
      "weight": "float [0.0-1.0]",
      "subcomponents": {
        "grounded_in_valid_statistics": {
          "weight": "float [0.0-1.0]",
          "criteria": "string",
          "evaluation_method": "string"
        },
        "logical_consistency": {
          "weight": "float [0.0-1.0]",
          "criteria": "string",
          "evaluation_method": "string"
        },
        "appropriate_assumptions": {
          "weight": "float [0.0-1.0]",
          "criteria": "string",
          "evaluation_method": "string"
        }
      }
    },
    "b_impl": {
      "description": "string",
      "weight": "float [0.0-1.0]",
      "subcomponents": {
        "test_coverage": {
          "weight": "float [0.0-1.0]",
          "criteria": "string",
          "evaluation_method": "automated_coverage",
          "thresholds": {
            "excellent": "float (>= this is excellent)",
            "good": "float",
            "acceptable": "float",
            "poor": "float"
          },
          "score_mapping": {
            "excellent": 1.0,
            "good": 0.8,
            "acceptable": 0.5,
            "poor": 0.0
          }
        },
        "type_annotations": {
          "weight": "float [0.0-1.0]",
          "criteria": "string",
          "evaluation_method": "mypy_strict"
        },
        "error_handling": {
          "weight": "float [0.0-1.0]",
          "criteria": "string",
          "evaluation_method": "exception_coverage"
        },
        "documentation": {
          "weight": "float [0.0-1.0]",
          "criteria": "string",
          "evaluation_method": "docstring_coverage"
        }
      }
    },
    "b_deploy": {
      "description": "string",
      "weight": "float [0.0-1.0]",
      "subcomponents": {
        "validation_runs": {
          "weight": "float [0.0-1.0]",
          "criteria": "string",
          "evaluation_method": "historical_data",
          "thresholds": {
            "excellent": "int (>= this many runs)",
            "good": "int",
            "acceptable": "int",
            "poor": "int"
          }
        },
        "stability_coefficient": {
          "weight": "float [0.0-1.0]",
          "criteria": "string",
          "evaluation_method": "coefficient_of_variation"
        },
        "failure_rate": {
          "weight": "float [0.0-1.0]",
          "criteria": "string",
          "evaluation_method": "error_rate_analysis"
        }
      }
    }
  },
  "methods": {
    "method_id": {
      "b_theory": "float [0.0-1.0]",
      "b_impl": "float [0.0-1.0]",
      "b_deploy": "float [0.0-1.0]",
      "b_overall": "float [0.0-1.0] (computed)"
    }
  }
}
```

**Example**:

```json
{
  "methods": {
    "D6_Q5_TheoryOfChange": {
      "b_theory": 0.88,
      "b_impl": 0.91,
      "b_deploy": 0.85,
      "b_overall": 0.88,
      "notes": "Bayesian causal inference using PyMC. Strong theoretical foundation."
    }
  }
}
```

**Validation Rules**:
- All weights must sum to 1.0 per aggregation level
- All scores must be in [0.0, 1.0]
- `b_overall` must equal weighted average of components
- Method IDs must match executor class names

---

### 2. unit_layer.json (PDT Structure)

**Purpose**: Defines @u layer (unit quality) thresholds and S/M/I/P scoring.

**Schema**:

```json
{
  "unit_layer": {
    "symbol": "@u",
    "name": "Unit Quality Layer",
    "description": "PDT structural quality assessment"
  },
  "components": {
    "S": {
      "name": "Structural Compliance",
      "weight": 0.30,
      "criteria": {
        "blocks_present": {
          "required": ["Diagnóstico", "Estratégica", "PPI", "Seguimiento"],
          "threshold": 4,
          "weight": 0.5
        },
        "sequence_valid": {
          "canonical_order": true,
          "weight": 0.25
        },
        "header_hierarchy": {
          "valid_numbering": true,
          "weight": 0.25
        }
      }
    },
    "M": {
      "name": "Mandatory Sections",
      "weight": 0.25,
      "sections": {
        "diagnostico": {
          "baseline_data_present": {"min_indicators": 5},
          "data_sources_cited": {"min_sources": 3},
          "gap_analysis": {"min_mentions": 3}
        },
        "estrategica": {
          "strategic_axes": {"min_count": 3},
          "objectives_smart": true,
          "theory_of_change": {"implicit_or_explicit": true}
        },
        "ppi": {
          "programs_linked": true,
          "budget_allocations": true,
          "timeline_4year": true
        },
        "seguimiento": {
          "monitoring_framework": true,
          "evaluation_methodology": true,
          "responsible_entities": true
        }
      }
    },
    "I": {
      "name": "Indicator Quality",
      "weight": 0.25,
      "criteria": {
        "table_present": {"weight": 0.4},
        "completeness": {
          "required_fields": [
            "tipo", "linea_estrategica", "programa",
            "linea_base", "meta_cuatrienio", "fuente",
            "unidad_medida"
          ],
          "weight": 0.25
        },
        "coverage": {"axes_covered": true, "weight": 0.20},
        "realism": {"max_increase_percent": 500, "weight": 0.15}
      }
    },
    "P": {
      "name": "PPI Completeness",
      "weight": 0.20,
      "criteria": {
        "table_present": {"weight": 0.4},
        "budget_breakdown": {
          "annual_breakdown": true,
          "funding_sources": ["SGP", "SGR", "Propios", "Otras"],
          "weight": 0.25
        },
        "budget_coherence": {
          "sums_valid": true,
          "no_negatives": true,
          "weight": 0.20
        },
        "cost_realism": {"weight": 0.15}
      }
    }
  },
  "thresholds": {
    "high": 0.7,
    "medium": 0.5,
    "low": 0.0
  }
}
```

**Scoring Formula**:
```
@u = 0.30 × S + 0.25 × M + 0.25 × I + 0.20 × P
```

---

### 3. congruence_layer.json (@C: Contract Compliance)

**Purpose**: Defines @C layer validation rules.

**Schema**:

```json
{
  "congruence_layer": {
    "symbol": "@C",
    "name": "Contract Compliance Layer",
    "description": "Formal correctness of input/output contracts"
  },
  "components": {
    "c_scale": {
      "name": "Scalar Conformance",
      "weight": 0.4,
      "rules": {
        "numeric_range": {"min": 0.0, "max": 1.0},
        "no_nan": true,
        "no_inf": true,
        "no_negatives": true,
        "precision": 4
      }
    },
    "c_sem": {
      "name": "Semantic Conformance",
      "weight": 0.35,
      "rules": {
        "type_checking": true,
        "enum_validation": true,
        "format_validation": {
          "dates": "ISO-8601",
          "urls": "RFC-3986"
        },
        "schema_matching": true
      }
    },
    "c_fusion": {
      "name": "Aggregation Readiness",
      "weight": 0.25,
      "rules": {
        "aggregable_outputs": true,
        "missing_value_handling": {"explicit_none": true},
        "provenance_populated": true,
        "metadata_complete": ["confidence", "uncertainty"]
      }
    }
  },
  "thresholds": {
    "excellent": 0.9,
    "good": 0.7,
    "poor": 0.0
  }
}
```

**Hard Gate**: @C < 0.7 triggers execution failure.

---

### 4. governance_layer.json (@m: Governance Maturity)

**Purpose**: Defines @m layer institutional quality metrics.

**Schema**:

```json
{
  "governance_layer": {
    "symbol": "@m",
    "name": "Governance Maturity Layer",
    "description": "Institutional and governance quality"
  },
  "components": {
    "m_transp": {
      "name": "Transparency",
      "weight": 0.40,
      "criteria": {
        "sources_cited": {"min_count": 5, "weight": 0.4},
        "methodologies_described": {"min_count": 3, "weight": 0.3},
        "assumptions_explicit": {"min_count": 5, "weight": 0.2},
        "public_participation": {"documented": true, "weight": 0.1}
      }
    },
    "m_gov": {
      "name": "Governance Structure",
      "weight": 0.35,
      "criteria": {
        "roles_clarity": true,
        "coordination_mechanisms": true,
        "monitoring_framework": true,
        "evaluation_plan": true
      }
    },
    "m_cost": {
      "name": "Cost Realism",
      "weight": 0.25,
      "criteria": {
        "budgets_detailed": true,
        "budgets_realistic": true,
        "funding_sources_identified": true,
        "contingency_planning": true
      }
    }
  }
}
```

---

## Parametrization Files

### executor_config.json

**Purpose**: Runtime settings for each executor.

**Location**: `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/parametrization/COHORT_2024_executor_config.json`

**Schema**:

```json
{
  "executor_id": {
    "timeout_s": "int (seconds)",
    "max_memory_mb": "int (megabytes)",
    "chunk_batch_size": "int",
    "enable_logging": "boolean",
    "max_workers": "int (for parallel operations)",
    "retry_attempts": "int",
    "fallback_method": "string (executor_id or null)"
  }
}
```

**Example**:

```json
{
  "D6_Q5_TheoryOfChange": {
    "timeout_s": 60,
    "max_memory_mb": 2048,
    "chunk_batch_size": 32,
    "enable_logging": true,
    "max_workers": 4,
    "retry_attempts": 2,
    "fallback_method": "D6_Q5_SimpleLogicModel"
  }
}
```

**Validation Rules**:
- `timeout_s` must be > 0
- `max_memory_mb` must be > 128
- `chunk_batch_size` must be > 0
- `max_workers` must be >= 1
- `fallback_method` must be valid executor_id or null

---

### runtime_layers.json

**Purpose**: Runtime layer weight overrides (advanced use).

**Schema**:

```json
{
  "policy_area": {
    "linear_weights": {
      "@b": "float [0.0-1.0]",
      "@chain": "float [0.0-1.0]",
      "@q": "float [0.0-1.0]",
      "@d": "float [0.0-1.0]",
      "@p": "float [0.0-1.0]",
      "@C": "float [0.0-1.0]",
      "@u": "float [0.0-1.0]",
      "@m": "float [0.0-1.0]"
    },
    "interaction_weights": {
      "(@u, @chain)": "float [0.0-1.0]",
      "(@chain, @C)": "float [0.0-1.0]",
      "(@q, @d)": "float [0.0-1.0]"
    }
  }
}
```

**Constraint**: Σ(linear_weights) + Σ(interaction_weights) = 1.0

---

## Questionnaire Files

### questionnaire_monolith.json

**Purpose**: Complete question hierarchy and pattern definitions.

**Location**: `canonic_questionnaire_central/questionnaire_monolith.json`

**Schema**:

```json
{
  "canonical_notation": {
    "dimensions": {
      "D1": {
        "code": "DIM01",
        "name": "string (Spanish)",
        "label": "string (Spanish)"
      }
    },
    "policy_areas": {
      "PA01": {
        "name": "string (Spanish)",
        "legacy_id": "string"
      }
    }
  },
  "blocks": {
    "dimension_id": {
      "policy_area_id": {
        "question_id": {
          "text": "string (Spanish)",
          "priority": "int (1-3)",
          "signals": ["signal_id", ...],
          "expected_evidence": ["string", ...],
          "validation_contract": "string (contract_id)"
        }
      }
    }
  }
}
```

**Example**:

```json
{
  "blocks": {
    "D6": {
      "PA01": {
        "Q5": {
          "text": "¿El plan incluye una teoría de cambio explícita?",
          "priority": 3,
          "signals": ["SIG_TOC_001", "SIG_CAUSAL_002"],
          "expected_evidence": [
            "causal_pathway",
            "assumptions",
            "mechanisms"
          ],
          "validation_contract": "theory_of_change_contract"
        }
      }
    }
  }
}
```

---

### pattern_registry.json

**Purpose**: Signal patterns for SISAS (Signal Irrigation System).

**Schema**:

```json
{
  "signal_id": {
    "patterns": [
      {
        "pattern_id": "string",
        "text": "string (regex or literal)",
        "weight": "float [0.0-1.0]",
        "context_required": ["string", ...],
        "semantic_expansions": ["string", ...],
        "evidence_boost": "float [1.0-2.0]"
      }
    ],
    "metadata": {
      "created_at": "ISO-8601 timestamp",
      "updated_at": "ISO-8601 timestamp",
      "cohort": "string"
    }
  }
}
```

---

## Fusion Specification

### fusion_weights.json

**Purpose**: Choquet integral weights (linear + interaction terms).

**Location**: `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/COHORT_2024_fusion_weights.json`

**Schema**:

```json
{
  "_metadata": {
    "version": "string",
    "generated_at": "ISO-8601 timestamp",
    "description": "string",
    "spec_compliance": "SUPERPROMPT Three-Pillar Calibration System",
    "purpose": "string"
  },
  "_fusion_formula": {
    "description": "Cal(I) = Σ(a_ℓ · x_ℓ) + Σ(a_ℓk · min(x_ℓ, x_k))",
    "constraints": [
      "a_ℓ ≥ 0 for all ℓ",
      "a_ℓk ≥ 0 for all (ℓ,k)",
      "Σ(a_ℓ) + Σ(a_ℓk) = 1.0",
      "Cal(I) ∈ [0,1] (bounded)",
      "∂Cal/∂x_ℓ ≥ 0 (monotonic)"
    ]
  },
  "role_fusion_parameters": {
    "role_name": {
      "linear_weights": {
        "@b": "float",
        "@chain": "float",
        "@q": "float",
        "@d": "float",
        "@p": "float",
        "@C": "float",
        "@u": "float",
        "@m": "float"
      },
      "interaction_weights": {
        "(@u, @chain)": "float",
        "(@chain, @C)": "float",
        "(@q, @d)": "float"
      },
      "normalization_check": {
        "sum_linear": "float",
        "sum_interaction": "float",
        "total": 1.0
      }
    }
  }
}
```

**Example (Executor Role)**:

```json
{
  "role_fusion_parameters": {
    "EXECUTOR": {
      "linear_weights": {
        "@b": 0.17,
        "@chain": 0.13,
        "@q": 0.08,
        "@d": 0.07,
        "@p": 0.06,
        "@C": 0.08,
        "@u": 0.04,
        "@m": 0.04
      },
      "interaction_weights": {
        "(@u, @chain)": 0.13,
        "(@chain, @C)": 0.10,
        "(@q, @d)": 0.10
      },
      "normalization_check": {
        "sum_linear": 0.67,
        "sum_interaction": 0.33,
        "total": 1.0
      }
    }
  }
}
```

**Validation**: Automatic check that weights sum to 1.0.

---

## Method Compatibility

### method_compatibility.json

**Purpose**: Maps methods to questions/dimensions/policies with compatibility scores.

**Location**: `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/COHORT_2024_method_compatibility.json`

**Schema**:

```json
{
  "method_id": {
    "questions": {
      "question_id": "float [0.0-1.0] (compatibility)"
    },
    "dimensions": {
      "dimension_id": "float [0.0-1.0] (compatibility)"
    },
    "policies": {
      "policy_area_id": "float [0.0-1.0] (compatibility)"
    }
  }
}
```

**Example**:

```json
{
  "D6_Q5_TheoryOfChange": {
    "questions": {
      "Q5": 1.0,
      "Q4": 0.7,
      "Q3": 0.3
    },
    "dimensions": {
      "DIM06": 1.0,
      "DIM04": 0.6,
      "DIM02": 0.4
    },
    "policies": {
      "PA01": 0.85,
      "PA05": 0.80,
      "PA10": 0.65
    }
  }
}
```

**Usage**: Computes @q, @d, @p layers using these compatibility scores.

---

## Executor Configs

### Executor Contract Files

**Purpose**: Input/output contract specifications per executor.

**Location**: `src/canonic_phases/Phase_two/json_files_phase_two/executor_contracts/specialized/Q{NNN}.v3.json`

**Schema**:

```json
{
  "executor_id": "string",
  "version": "string",
  "input_contract": {
    "required_fields": ["string", ...],
    "optional_fields": ["string", ...],
    "types": {
      "field_name": "string (type)"
    }
  },
  "output_contract": {
    "required_fields": ["string", ...],
    "types": {
      "field_name": "string (type)"
    },
    "score_range": {"min": 0.0, "max": 1.0}
  },
  "validation_rules": [
    {
      "rule_id": "string",
      "type": "string (range_check, type_check, etc.)",
      "parameters": {}
    }
  ]
}
```

---

## File Locations

### Directory Structure

```
src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/
├── calibration/                              # Immutable calibration
│   ├── COHORT_2024_intrinsic_calibration.json
│   ├── COHORT_2024_fusion_weights.json
│   ├── COHORT_2024_method_compatibility.json
│   ├── COHORT_2024_questionnaire_monolith.json
│   └── COHORT_2024_canonical_method_inventory.json
│
├── parametrization/                          # Traceable execution settings
│   ├── COHORT_2024_executor_config.json
│   └── COHORT_2024_runtime_layers.json
│
├── canonic_description_unit_analysis.json    # Unit layer (@u) definitions
└── COHORT_MANIFEST.json                      # Cohort metadata + hashes

canonic_questionnaire_central/
├── questionnaire_monolith.json               # Full questionnaire
├── questionnaire_schema.json                 # JSON schema
└── pattern_registry.json                     # SISAS patterns

src/farfan_pipeline/phases/Phase_02/
├── generated_contracts/contracts/            # 300 contracts (Q001-Q030 × PA01-PA10)
│   ├── Q001_PA01_contract_v4.json
│   ├── Q001_PA02_contract_v4.json
│   └── ... (300 files with embedded method bindings)
├── phase2_10_00_factory.py                   # Main factory with DI
├── phase2_10_01_class_registry.py            # Method dispensary registry
└── phase2_60_02_arg_router.py                # Method argument routing
```

### Loading Conventions

**Python Example**:

```python
from pathlib import Path
import json

# Load calibration (immutable)
CALIBRATION_DIR = Path("src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration")

with open(CALIBRATION_DIR / "COHORT_2024_intrinsic_calibration.json") as f:
    intrinsic_cal = json.load(f)

# Load parametrization (traceable)
PARAM_DIR = Path("src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/parametrization")

with open(PARAM_DIR / "COHORT_2024_executor_config.json") as f:
    executor_config = json.load(f)

# Verify cohort consistency
assert intrinsic_cal["_cohort_metadata"]["cohort_id"] == "COHORT_2024"
assert executor_config["_cohort_metadata"]["cohort_id"] == "COHORT_2024"
```

---

## Validation Utilities

### Config Validator

```python
def validate_config_schema(config: dict, schema_path: str) -> bool:
    """
    Validate config against JSON schema.
    
    Args:
        config: Configuration dictionary
        schema_path: Path to JSON schema file
    
    Returns:
        True if valid
    
    Raises:
        ValidationError: If schema validation fails
    """
    import jsonschema
    
    with open(schema_path) as f:
        schema = json.load(f)
    
    jsonschema.validate(config, schema)
    return True
```

### Weight Normalization Check

```python
def check_fusion_weights(weights: dict) -> bool:
    """Verify fusion weights sum to 1.0."""
    linear_sum = sum(weights["linear_weights"].values())
    interaction_sum = sum(weights["interaction_weights"].values())
    total = linear_sum + interaction_sum
    
    if abs(total - 1.0) > 1e-6:
        raise ValueError(f"Weights sum to {total}, expected 1.0")
    
    return True
```

---

## Related Documentation

- [WEIGHT_TUNING.md](./WEIGHT_TUNING.md) - How to adjust fusion weights
- [DETERMINISM.md](./DETERMINISM.md) - Calibration vs. parametrization doctrine
- [LAYER_SYSTEM.md](./LAYER_SYSTEM.md) - Layer definitions and scoring

---

**Last Updated**: 2024-12-16  
**Version**: 1.0.0  
**Maintainers**: Policy Analytics Research Unit

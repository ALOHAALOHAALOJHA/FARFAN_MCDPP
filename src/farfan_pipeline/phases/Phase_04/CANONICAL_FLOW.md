# Phase 4 Canonical Flow Documentation

## Overview
Phase 4 (Dimension Aggregation) follows a strict, deterministic execution flow where **ALL files participate by default**. The architecture is organized into 8 sequential stages, with imports following the manifest execution order.

## Status: ✅ CANONICALIZED (2026-01-18)

All issues identified in the audit have been resolved:
- ✅ Duplicate `Phase_4` folder removed (canonical is `Phase_04`)
- ✅ All files properly organized by stage
- ✅ All modules imported in `__init__.py` following execution order
- ✅ Import sequence validated against manifest DAG
- ✅ No circular dependencies
- ✅ All 39 exports properly documented in `__all__`

## Manifest-Driven Architecture

The flow is defined by `PHASE_4_MANIFEST.json` with 8 execution stages:

### Stage 00 - Infrastructure (Order 1)
**Purpose**: Package initialization
- `__init__.py` - Package entry point

### Stage 00 - Primitives (Order 2)
**Purpose**: Foundation types with ZERO dependencies
**Location**: `primitives/`

All primitive modules participate by default:
1. `phase4_00_00_types.py` - Type definitions and protocols
2. `phase4_00_00_quality_levels.py` - Quality level determination
3. `phase4_00_00_uncertainty_metrics.py` - Uncertainty quantification primitives
4. `phase4_00_00_choquet_primitives.py` - Choquet integral primitives
5. `phase4_00_00_signal_enriched_primitives.py` - Signal enrichment primitives
6. `phase4_00_00_aggregation_settings.py` - Pure AggregationSettings dataclass

**Imported via**: `primitives/__init__.py` → `__init__.py`

### Stage 10 - Foundation (Order 3)
**Purpose**: Core foundational modules with minimal dependencies

All foundation modules participate by default:
1. `phase4_10_00_aggregation_provenance.py` - W3C PROV-compliant DAG tracking
   - Exports: `ProvenanceDAG`, `ProvenanceEntry`
2. `phase4_10_00_uncertainty_quantification.py` - BCa bootstrap, convergence diagnostics
   - Exports: `BootstrapAggregator`, `UncertaintyMetrics`, `aggregate_with_uncertainty`
3. `phase4_10_00_aggregation_settings.py` - Settings re-export (REDIR type)
   - Re-exports from primitives

### Stage 20 - Core Processing (Order 4)
**Purpose**: Core processing modules depending on foundation

All core modules participate by default:
1. `phase4_20_00_choquet_adapter.py` - Choquet integral fuzzy measure adapter
   - Exports: `create_default_choquet_adapter`
   - Dependencies: Stage 10 modules (uncertainty, settings)

### Stage 30 - Aggregators (Order 5)
**Purpose**: Main aggregation engines

All aggregator modules participate by default:
1. `phase4_30_00_choquet_aggregator.py` - Multi-layer Choquet aggregation
   - Exports: `ChoquetAggregator`
2. `phase4_30_00_aggregation.py` - Main dimension aggregator (300→60)
   - Exports: `DimensionAggregator`, `ScoredResult`, `DimensionScore`, `AggregationDAG`, `ProvenanceNode`, utilities, exceptions
   - Dependencies: Stage 10 (provenance, uncertainty, settings), Stage 20 (choquet adapter)
3. `phase4_30_00_signal_enriched_aggregation.py` - Signal-based enhancements
   - Exports: `SignalEnrichedAggregator`
   - Dependencies: Stage 00 primitives (signal enriched primitives)

### Stage 40 - Enhancements (Order 6)
**Purpose**: Enhancement and optimization modules
**Location**: `enhancements/`

All enhancement modules participate by default:
1. `phase4_40_00_adaptive_meso_scoring.py` - Adaptive penalty scoring
   - Exports: `AdaptiveMesoScoring`, `AdaptiveScoringConfig`, `ScoringMetrics`
2. `phase4_40_00_aggregation_enhancements.py` - Performance and telemetry
   - Exports: `ConfidenceInterval`, `DispersionMetrics`, `HermeticityDiagnosis`
3. Via `enhancements/__init__.py`:
   - Exports: `EnhancedDimensionAggregator`, `enhance_aggregator`

### Stage 50 - Integration (Order 7)
**Purpose**: Cross-phase integration

All integration modules participate by default:
1. `phase4_50_00_aggregation_integration.py` - Cross-phase integration (P4→P5→P6)
   - Exports: `ClusterAggregator`
   - Dependencies: Stage 30 (aggregation), Phase 5, Phase 6

### Stage 60 - Validation (Order 8)
**Purpose**: Output validation

All validation modules participate by default:
1. `phase4_60_00_aggregation_validation.py` - Phase 4 output validation
   - Exports: `ValidationResult`, `AggregationValidationError`, `validate_phase4_output`
   - Dependencies: Stage 30 (aggregation)

## Import Flow

The `__init__.py` imports follow strict execution order:

```python
# STAGE 00: PRIMITIVES (Order 2)
from primitives.phase4_00_00_aggregation_settings import AggregationSettings

# STAGE 10: FOUNDATION (Order 3)
from phase4_10_00_aggregation_provenance import ProvenanceDAG, ProvenanceEntry
from phase4_10_00_uncertainty_quantification import BootstrapAggregator, UncertaintyMetrics, aggregate_with_uncertainty

# STAGE 20: CORE PROCESSING (Order 4)
from phase4_20_00_choquet_adapter import create_default_choquet_adapter

# STAGE 30: AGGREGATORS (Order 5)
from phase4_30_00_aggregation import DimensionAggregator, ScoredResult, DimensionScore, ...
from phase4_30_00_choquet_aggregator import ChoquetAggregator
from phase4_30_00_signal_enriched_aggregation import SignalEnrichedAggregator

# STAGE 40: ENHANCEMENTS (Order 6)
from enhancements.phase4_40_00_adaptive_meso_scoring import AdaptiveMesoScoring, ...
from enhancements.phase4_40_00_aggregation_enhancements import ConfidenceInterval, ...
from enhancements import EnhancedDimensionAggregator, enhance_aggregator

# STAGE 50: INTEGRATION (Order 7)
from phase4_50_00_aggregation_integration import ClusterAggregator

# STAGE 60: VALIDATION (Order 8)
from phase4_60_00_aggregation_validation import ValidationResult, validate_phase4_output, ...
```

## Verification

The flow has been verified with:

1. **Import Order Check**: All imports follow manifest execution order (0→1→2→3→4→5→6→7→8)
2. **Dependency Check**: No circular dependencies, all imports reference earlier stages
3. **DAG Validation**: Deterministic acyclic graph confirmed
4. **Default Usage Test**: All modules are imported and accessible by default
5. **Export Completeness**: All 39 key exports present in `__all__`

## Contract

Phase 4 GUARANTEES:
- **Input**: 300 ScoredMicroQuestion from Phase 3
- **Output**: 60 DimensionScore (6 dimensions × 10 policy areas)
- **Flow**: Deterministic, sequential, all files participate by default
- **Provenance**: Full W3C PROV-compliant DAG for all operations
- **Validation**: Hermetic validation at phase boundary
- **Uncertainty**: BCa bootstrap uncertainty quantification

## Files NOT in Default Flow

The following files exist but are NOT part of the canonical flow:
- Extra/duplicate files in `primitives/`: `phase4_10_00_*` (superseded by `phase4_00_00_*`)
- Extra/duplicate files in `enhancements/`: Legacy versions without `phase4_40_00_` prefix
- Files in `contracts/`, `docs/`, `tests/`, `validation/` subdirectories (supporting infrastructure)

These extra files may be removed in future cleanup operations.

## Maintenance Notes

When adding new modules:
1. Add to `PHASE_4_MANIFEST.json` with correct stage and execution order
2. Place file in correct location (base, primitives/, or enhancements/)
3. Import in `__init__.py` respecting execution order
4. Add exports to `__all__`
5. Ensure dependencies only reference earlier stages
6. Run verification: `python3 /tmp/verify_phase4_dag.py`

## References

- Manifest: `PHASE_4_MANIFEST.json`
- Main Entry: `__init__.py`
- Constants: `PHASE_4_CONSTANTS.py`
- Architecture Docs: `docs/` and `README.md`

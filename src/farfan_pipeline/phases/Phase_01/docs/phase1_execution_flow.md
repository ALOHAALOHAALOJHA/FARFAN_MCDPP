# Phase 1 Execution Flow

## Overview
Phase 1 performs CPP (Canon Policy Package) Ingestion & Preprocessing, transforming raw policy documents into semantically enriched chunks structured along Policy Area × Dimension grid.

## Execution Architecture

### Sequential Processing Order
Phase 1 consists of 16 subphases (SP0-SP15) executed sequentially:

| Subphase | Name | Module | Weight | Tier | Description |
|----------|------|--------|--------|------|-------------|
| SP0 | Language Detection | phase1_20_00_cpp_ingestion | 900 | STANDARD | Detect document language |
| SP1 | Advanced Preprocessing | phase1_20_00_cpp_ingestion | 2500 | STANDARD | Text normalization and cleaning |
| SP2 | Structural Analysis | phase1_20_00_cpp_ingestion | 3000 | STANDARD | Document structure extraction |
| SP3 | Knowledge Graph | phase1_20_00_cpp_ingestion | 4000 | STANDARD | Construct knowledge graph |
| **SP4** | **Semantic Segmentation** | phase1_20_00_cpp_ingestion | **10000** | **CRITICAL** | PA×Dim grid specification |
| SP5 | Causal Chain | phase1_20_00_cpp_ingestion | 5000 | HIGH | Extract causal relationships |
| SP6 | Integrated Causal | phase1_20_00_cpp_ingestion | 3500 | STANDARD | Integrate causal chains |
| SP7 | Arguments | phase1_20_00_cpp_ingestion | 4500 | STANDARD | Extract argumentative structure |
| SP8 | Temporal Markers | phase1_20_00_cpp_ingestion | 3500 | STANDARD | Extract temporal information |
| SP9 | Discourse Mode | phase1_20_00_cpp_ingestion | 6000 | HIGH | Analyze discourse patterns |
| SP10 | Strategic Integration | phase1_20_00_cpp_ingestion | 8000 | HIGH | Integrate strategic layers |
| **SP11** | **SmartChunk Assembly** | phase1_20_00_cpp_ingestion | **10000** | **CRITICAL** | Assemble 60 chunks |
| SP12 | Irrigation Linking | phase1_20_00_cpp_ingestion | 7000 | HIGH | SISAS irrigation links |
| **SP13** | **Integrity Validation** | phase1_20_00_cpp_ingestion | **10000** | **CRITICAL** | CPP packaging |
| SP14 | Ranking | phase1_20_00_cpp_ingestion | 5000 | HIGH | Quality metrics |
| SP15 | Final Output | phase1_20_00_cpp_ingestion | 9000 | HIGH | Integrity verification |

### Critical Subphases (Weight = 10000)
Three subphases are marked as CRITICAL and will abort the entire pipeline on failure:

1. **SP4 - Semantic Segmentation**: Defines the PA×Dim grid (10 Policy Areas × 6 Dimensions = 60 chunks)
2. **SP11 - SmartChunk Assembly**: Assembles exactly 60 chunks with complete metadata
3. **SP13 - Integrity Validation**: Validates CPP structure and completeness

## Module Dependency Graph

### Topological Order (Import Dependencies)

```
PHASE_1_CONSTANTS
├── phase1_10_00_phase_1_constants (constants definitions)
│   └── phase1_10_00_models (data models)
├── phase1_10_00_cpp_models (CPP data models)
├── phase1_10_00_phase_protocol (protocol definitions)
├── phase1_10_00_thread_safe_results (thread safety utilities)
├── phase1_15_00_questionnaire_mapper (question mapping)
│   └── phase1_25_00_sp4_question_aware (question-aware segmentation)
├── phase1_30_00_adapter (adapter layer)
├── phase1_40_00_circuit_breaker (circuit breaker pattern)
├── phase1_50_00_dependency_validator (dependency validation)
├── phase1_60_00_signal_enrichment (signal enrichment)
├── phase1_70_00_structural (structural analysis)
└── phase1_20_00_cpp_ingestion (main executor - imports all above)
```

### Main Execution Entry Point
**Module**: `phase1_20_00_cpp_ingestion.py`
**Class**: `Phase1MissionContract`
**Method**: `execute(canonical_input: CanonicalInput) -> List[SmartChunk]`

This module orchestrates all 16 subphases and is the last module in the topological order, as it imports and uses all other Phase 1 modules.

## Data Flow

### Input
- **Type**: `CanonicalInput` (from Phase 0)
- **Contents**:
  - PDF path and SHA256 hash
  - Questionnaire path and SHA256 hash
  - Validation status from Phase 0

### Processing
1. **Text Extraction** (primitives/streaming_extractor.py)
   - Extract text from PDF
   - Apply truncation limits
   - Audit for truncation issues

2. **Language & Preprocessing** (SP0-SP1)
   - Detect language
   - Normalize text
   - Clean artifacts

3. **Structural & Semantic Analysis** (SP2-SP4)
   - Identify document structure
   - Build knowledge graph
   - Segment into PA×Dim grid

4. **Enrichment Layers** (SP5-SP10)
   - Extract causal chains
   - Identify arguments
   - Mark temporal information
   - Analyze discourse patterns
   - Integrate strategic layers

5. **Assembly & Validation** (SP11-SP15)
   - Assemble SmartChunks
   - Link SISAS irrigation
   - Validate integrity
   - Compute quality metrics
   - Verify final output

### Output
- **Type**: `List[SmartChunk]`
- **Count**: Exactly 60 chunks
- **Structure**: 10 Policy Areas × 6 Causal Dimensions
- **Metadata**: Complete execution trace, quality metrics, provenance

## Weight-Based Execution Contract

### Weight Tiers
- **CRITICAL (10000)**: Abort on failure, 3x timeout, critical logging
- **HIGH (5000-9000)**: Enhanced validation, 2x timeout, warning logging  
- **STANDARD (900-4999)**: Standard validation, 1x timeout, info logging

### Timeout Calculation
```python
base_timeout = 60  # seconds
actual_timeout = base_timeout * weight_tier_multiplier
```

### Failure Handling
- **CRITICAL**: Immediate abort with detailed error trace
- **HIGH**: Log warning, attempt recovery if possible
- **STANDARD**: Log info, continue with degraded output

## Quality Assurance

### Validation Points
1. **Input Contract** (contracts/phase1_input_contract.py)
   - Validates all preconditions before Phase 1 starts

2. **Per-Subphase Validation**
   - Weight-based validation strictness
   - Metadata completeness checks
   - Data type verification

3. **Output Contract** (contracts/phase1_output_contract.py)
   - Validates all postconditions after Phase 1 completes
   - Ensures 60 chunks produced
   - Verifies PA×Dim coverage
   - Checks execution trace completeness

### Circuit Breaker
Module `phase1_40_00_circuit_breaker.py` provides resilience patterns:
- Fail-fast on repeated errors
- Graceful degradation
- Error budgets per subphase

### Dependency Validation
Module `phase1_50_00_dependency_validator.py` ensures:
- All required dependencies available
- Version compatibility
- Resource availability

## Observability

### Execution Trace
Each subphase records:
- Start timestamp
- End timestamp
- Duration
- Success/failure status
- Weight
- Artifacts produced

### Quality Metrics
- Provenance completeness
- Coverage (PA×Dim)
- Semantic coherence
- Structural integrity
- Temporal consistency

### Logging
- Logger name: `farfan_pipeline.phases.phase_1`
- Log levels by weight tier:
  - CRITICAL subphases: `logger.critical()`
  - HIGH subphases: `logger.warning()`
  - STANDARD subphases: `logger.info()`

## References
- Input Contract: `contracts/phase1_input_contract.py`
- Mission Contract: `contracts/phase1_mission_contract.py`
- Output Contract: `contracts/phase1_output_contract.py`
- Chain Analysis: `contracts/phase1_chain_report.json`
- Constants: `PHASE_1_CONSTANTS.py`
- Main Executor: `phase1_20_00_cpp_ingestion.py`

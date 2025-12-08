# Fusion Requirements Specification

## Overview

This document specifies the fusion requirements for methods in the canonical method catalog. Fusion requirements define the input dependencies and data flow constraints for each method, distinguishing between required and optional inputs.

## Requirement Types

### Required Inputs
Inputs that MUST be present for the method to execute successfully. Missing required inputs will cause execution failure.

### Optional Inputs  
Inputs that MAY be present and can enhance method behavior, but the method can still execute without them (typically with default values or graceful degradation).

## Standard Input Fields

### Document-Level Inputs
- `extracted_text`: Raw text content extracted from policy documents
- `document_id`: Unique identifier for the source document
- `document_metadata`: Metadata about the document (title, date, source)
- `preprocessed_document`: Structured representation after SPC ingestion
- `canonical_policy_package`: Complete CPP structure from processing pipeline

### Question-Level Inputs
- `question_id`: Identifier for the specific analysis question (PA01-PA10)
- `question_text`: Full text of the question being answered
- `dimension`: Policy dimension (D1-D6)
- `policy_area`: Policy area classification

### Analysis-Level Inputs
- `previous_analysis`: Results from prior analysis phases
- `embeddings`: Vector embeddings of text segments
- `extracted_entities`: Named entities extracted from text
- `dependency_parse`: Syntactic dependency structures
- `temporal_markers`: Time-related expressions and dates
- `numerical_values`: Extracted quantitative data

### Context Inputs
- `config`: Runtime configuration parameters
- `calibration_params`: Method-specific calibration values
- `model_weights`: ML model parameters (optional)
- `domain_ontology`: Policy domain knowledge base (optional)

## Fusion Requirement Patterns

### Pattern 1: Document Processor
**Required**: `extracted_text`, `document_id`  
**Optional**: `document_metadata`, `config`  
**Use Case**: Basic document ingestion and parsing

### Pattern 2: Semantic Analyzer
**Required**: `extracted_text`, `question_id`, `embeddings`  
**Optional**: `previous_analysis`, `model_weights`  
**Use Case**: NLP-based content analysis

### Pattern 3: Causal Extractor
**Required**: `preprocessed_document`, `question_id`, `dependency_parse`  
**Optional**: `temporal_markers`, `extracted_entities`, `domain_ontology`  
**Use Case**: Causal relationship inference

### Pattern 4: Quantitative Validator
**Required**: `extracted_text`, `numerical_values`  
**Optional**: `calibration_params`, `previous_analysis`  
**Use Case**: Numerical consistency checking

### Pattern 5: Temporal Analyzer
**Required**: `extracted_text`, `temporal_markers`  
**Optional**: `preprocessed_document`, `config`  
**Use Case**: Timeline construction and temporal reasoning

### Pattern 6: Evidence Scorer
**Required**: `question_id`, `extracted_entities`, `previous_analysis`  
**Optional**: `embeddings`, `calibration_params`, `model_weights`  
**Use Case**: Evidence probative value assessment

### Pattern 7: Aggregator
**Required**: `previous_analysis` (list of results), `question_id`  
**Optional**: `config`, `calibration_params`  
**Use Case**: Multi-method result aggregation

### Pattern 8: Report Generator
**Required**: `previous_analysis`, `document_id`, `question_id`  
**Optional**: `document_metadata`, `config`  
**Use Case**: Final report assembly

## Data Flow Constraints

### Constraint 1: Phase Dependencies
Methods in later phases can access outputs from earlier phases via `previous_analysis`, but not vice versa.

### Constraint 2: Question Binding
Methods processing question-specific content MUST have `question_id` as a required input.

### Constraint 3: Text Dependency
Methods performing text analysis MUST have either `extracted_text` or `preprocessed_document` as required input.

### Constraint 4: Embeddings Consistency
When `embeddings` is a required input, the method MUST specify the embedding model in `calibration_params`.

### Constraint 5: Configuration Propagation
`config` should be optional for all methods, with sensible defaults defined in the catalog.

## Validation Rules

1. **Completeness**: Every method MUST specify `fusion_requirements` with at least one required input
2. **Consistency**: Required inputs listed in `fusion_requirements` MUST align with `input_parameters` signature
3. **Traceability**: Optional inputs MUST have documented fallback behavior
4. **Determinism**: Methods with same fusion_requirements must produce consistent outputs given identical inputs

## Method-Specific Examples

### Example 1: PolicyContradictionDetector.detect
```json
{
  "fusion_requirements": {
    "required": ["extracted_text", "question_id", "preprocessed_document"],
    "optional": ["previous_analysis", "embeddings", "config"]
  }
}
```

### Example 2: BayesianMechanismInference.infer_mechanisms
```json
{
  "fusion_requirements": {
    "required": ["preprocessed_document", "question_id", "dependency_parse", "extracted_entities"],
    "optional": ["temporal_markers", "domain_ontology", "calibration_params", "model_weights"]
  }
}
```

### Example 3: TemporalLogicVerifier.verify_temporal_consistency
```json
{
  "fusion_requirements": {
    "required": ["extracted_text", "temporal_markers"],
    "optional": ["preprocessed_document", "config"]
  }
}
```

### Example 4: AdaptivePriorCalculator.calculate_likelihood_adaptativo
```json
{
  "fusion_requirements": {
    "required": ["question_id", "previous_analysis"],
    "optional": ["calibration_params", "domain_ontology"]
  }
}
```

## Extension Guidelines

When adding new methods to the catalog:

1. Identify all inputs the method consumes
2. Classify each as required or optional based on execution necessity
3. Document optional input fallback behavior
4. Assign appropriate fusion requirement pattern
5. Validate against existing patterns for consistency
6. Update this specification if introducing new patterns

## Versioning

**Version**: 1.0.0  
**Last Updated**: 2024  
**Compatibility**: canonical_method_catalogue_v2.json

## References

- `config/canonical_method_catalogue_v2.json`: Method catalog with fusion_requirements
- `config/semantic_taxonomy.json`: Semantic tag definitions
- `src/farfan_pipeline/core/`: Pipeline orchestration logic

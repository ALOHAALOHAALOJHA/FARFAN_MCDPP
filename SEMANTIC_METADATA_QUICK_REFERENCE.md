# Semantic Metadata - Quick Reference Guide

## What Was Added

Three new fields to all 2,163 methods in `config/canonical_method_catalogue_v2.json`:

### 1. `semantic_tags` (Array)
Semantic classification of method functionality.

**8 Tags Available**:
- `coherence` - Contradiction detection, consistency
- `numerical` - Quantitative analysis
- `temporal` - Time-based reasoning
- `causal` - Causal inference
- `structural` - Document parsing
- `policy` - Policy interpretation
- `evidence` - Evidence assessment
- `textual_quality` - Quality assessment

**Example**:
```json
"semantic_tags": ["causal", "evidence", "numerical"]
```

### 2. `output_range` (Array or null)
Numerical output bounds.

**Formats**:
- `[0.0, 1.0]` - Probabilities/scores
- `[0, 1]` - Boolean/binary
- `[0, null]` - Counts (unbounded)
- `null` - Non-numeric output

**Example**:
```json
"output_range": [0.0, 1.0]
```

### 3. `fusion_requirements` (Object)
Input dependencies for execution.

**Structure**:
```json
"fusion_requirements": {
  "required": ["extracted_text", "question_id"],
  "optional": ["config", "embeddings"]
}
```

## Quick Queries

### Find Methods by Tag
```bash
# Causal methods
jq '.[] | select(.semantic_tags | contains(["causal"]))' config/canonical_method_catalogue_v2.json

# Methods with coherence AND evidence
jq '.[] | select(.semantic_tags | contains(["coherence", "evidence"]))' config/canonical_method_catalogue_v2.json
```

### Find Methods by Output Range
```bash
# Probability methods (0-1 range)
jq '.[] | select(.output_range == [0.0, 1.0])' config/canonical_method_catalogue_v2.json

# Boolean checks
jq '.[] | select(.output_range == [0, 1])' config/canonical_method_catalogue_v2.json
```

### Find Methods by Requirements
```bash
# Requires embeddings
jq '.[] | select(.fusion_requirements.required | contains(["embeddings"]))' config/canonical_method_catalogue_v2.json

# Can use previous analysis
jq '.[] | select(.fusion_requirements.optional | contains(["previous_analysis"]))' config/canonical_method_catalogue_v2.json
```

## Key Statistics

- **Total methods**: 2,163
- **All methods tagged**: 100%
- **Avg tags per method**: 1.43
- **Richest methods**: 5 tags
- **Methods with output range**: 407 (18.8%)

## Common Patterns

### Analysis Methods
```json
{
  "semantic_tags": ["causal", "evidence"],
  "output_range": null,
  "fusion_requirements": {
    "required": ["extracted_text", "question_id"],
    "optional": ["previous_analysis", "config"]
  }
}
```

### Scoring Methods
```json
{
  "semantic_tags": ["numerical", "evidence"],
  "output_range": [0.0, 1.0],
  "fusion_requirements": {
    "required": ["question_id", "previous_analysis"],
    "optional": ["calibration_params"]
  }
}
```

### Validation Methods
```json
{
  "semantic_tags": ["evidence", "textual_quality"],
  "output_range": [0, 1],
  "fusion_requirements": {
    "required": ["extracted_text"],
    "optional": ["config"]
  }
}
```

## Files Reference

| File | Purpose |
|------|---------|
| `config/semantic_taxonomy.json` | Tag definitions |
| `config/fusion_requirements_spec.md` | Requirements spec |
| `config/SEMANTIC_METADATA_README.md` | Full documentation |
| `config/semantic_metadata_examples.json` | Examples |
| `config/canonical_method_catalogue_v2.json` | Extended catalog |

## Example Methods

| Method | Tags | Range | Required Inputs |
|--------|------|-------|-----------------|
| `PolicyContradictionDetector.detect` | coherence, evidence, policy, structural | null | extracted_text, question_id, preprocessed_document |
| `AdaptivePriorCalculator.calculate_likelihood_adaptativo` | causal, evidence, numerical | [0.0, 1.0] | question_id, previous_analysis |
| `TemporalLogicVerifier.verify_temporal_consistency` | coherence, evidence, structural, temporal, textual_quality | [0, 1] | extracted_text, question_id |
| `MicroQuestionScorer.score_type_a` | evidence, numerical | [0.0, 1.0] | extracted_text |

## Common Use Cases

### 1. Find Compatible Methods
```bash
# Methods that can process extracted_text
jq '.[] | select(.fusion_requirements.required | contains(["extracted_text"]))' \
  config/canonical_method_catalogue_v2.json
```

### 2. Build Processing Pipeline
```bash
# Methods needing previous_analysis (phase 2+)
jq '.[] | select(.fusion_requirements.required | contains(["previous_analysis"]))' \
  config/canonical_method_catalogue_v2.json
```

### 3. Quality Control
```bash
# Validation methods
jq '.[] | select(.semantic_tags | contains(["textual_quality"]))' \
  config/canonical_method_catalogue_v2.json
```

## Version

- **Taxonomy**: v1.0.0
- **Implementation**: 2024
- **Status**: Production-ready

## Support

For detailed information, see:
- `config/SEMANTIC_METADATA_README.md`
- `config/fusion_requirements_spec.md`
- `SEMANTIC_METADATA_IMPLEMENTATION.md`

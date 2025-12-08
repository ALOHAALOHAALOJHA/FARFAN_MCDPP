# Semantic Metadata Extension for Canonical Method Catalog

## Overview

The `canonical_method_catalogue_v2.json` has been extended with three new fields to support the congruence layer and enable sophisticated method fusion and semantic analysis.

## New Fields

### 1. `semantic_tags` (Array of Strings)

**Purpose**: Classify methods by their semantic role in the analysis pipeline.

**Values**: See `semantic_taxonomy.json` for complete definitions. Core tags include:
- `coherence` - Contradiction detection, consistency checking
- `numerical` - Quantitative analysis, statistics
- `temporal` - Time-based reasoning, timeline construction
- `causal` - Causal inference, mechanism identification
- `structural` - Document parsing, hierarchy extraction
- `policy` - Policy-specific interpretation
- `evidence` - Evidence assessment, probative value
- `textual_quality` - Quality assessment, readability

**Example**:
```json
{
  "canonical_name": "PolicyContradictionDetector.detect",
  "semantic_tags": ["coherence", "evidence", "policy", "structural"]
}
```

### 2. `output_range` (Array or null)

**Purpose**: Define the valid output domain for methods that produce numerical results.

**Format**: 
- `[min, max]` - Bounded range (e.g., `[0.0, 1.0]` for probabilities)
- `[min, null]` - Unbounded above (e.g., `[0, null]` for counts)
- `null` - No defined numerical range (non-numeric or complex outputs)

**Examples**:
```json
{
  "canonical_name": "calculate_similarity_score",
  "output_range": [0.0, 1.0]
}
{
  "canonical_name": "count_entities",
  "output_range": [0, null]
}
{
  "canonical_name": "check_validity",
  "output_range": [0, 1]
}
{
  "canonical_name": "extract_text",
  "output_range": null
}
```

### 3. `fusion_requirements` (Object)

**Purpose**: Specify data dependencies for method execution, distinguishing required vs optional inputs.

**Structure**:
```json
{
  "required": ["input1", "input2"],
  "optional": ["optional_input1", "config"]
}
```

**Standard Input Fields**:

**Document-Level**:
- `extracted_text` - Raw text from documents
- `document_id` - Document identifier
- `document_metadata` - Metadata (title, date, etc.)
- `preprocessed_document` - Structured SPC representation
- `canonical_policy_package` - Complete CPP structure

**Question-Level**:
- `question_id` - Question identifier (PA01-PA10)
- `question_text` - Full question text
- `dimension` - Policy dimension (D1-D6)
- `policy_area` - Policy area classification

**Analysis-Level**:
- `previous_analysis` - Results from prior phases
- `embeddings` - Text vector embeddings
- `extracted_entities` - Named entities
- `dependency_parse` - Syntactic dependencies
- `temporal_markers` - Time expressions
- `numerical_values` - Quantitative data

**Context**:
- `config` - Runtime configuration
- `calibration_params` - Method-specific calibration
- `model_weights` - ML model parameters
- `domain_ontology` - Policy domain knowledge

**Examples**:
```json
{
  "canonical_name": "PolicyContradictionDetector.detect",
  "fusion_requirements": {
    "required": ["extracted_text", "question_id", "preprocessed_document"],
    "optional": ["embeddings", "previous_analysis", "config", "dependency_parse"]
  }
}
{
  "canonical_name": "TemporalLogicVerifier.verify_temporal_consistency",
  "fusion_requirements": {
    "required": ["extracted_text", "temporal_markers"],
    "optional": ["preprocessed_document", "config"]
  }
}
```

## Statistics

**Total Methods**: 2,163

**Semantic Tag Distribution**:
- `structural`: 1,655 methods (76.5%)
- `evidence`: 543 methods (25.1%)
- `textual_quality`: 256 methods (11.8%)
- `causal`: 212 methods (9.8%)
- `numerical`: 200 methods (9.2%)
- `policy`: 125 methods (5.8%)
- `coherence`: 86 methods (4.0%)
- `temporal`: 25 methods (1.2%)

**Output Range Distribution**:
- `null` (non-numeric): 1,756 methods (81.2%)
- `[0, 1]` (boolean/binary): 371 methods (17.2%)
- `[0, null]` (counts): 36 methods (1.7%)

## Assignment Rules

### Semantic Tags

Tags are assigned based on method name, file path, and functional role:

1. **Name-based**: Keywords in method name trigger specific tags
   - `contradiction`, `coherence`, `consistency` → `["coherence", "evidence"]`
   - `temporal`, `timeline` → `["temporal", "structural"]`
   - `causal`, `mechanism`, `inference` → `["causal", "evidence"]`
   - `bayesian`, `probability` → `["evidence", "numerical"]`
   - `score`, `calculate`, `measure` → `["numerical"]`
   - `policy`, `goal`, `objective` → `["policy", "structural"]`

2. **Path-based**: File location influences tags
   - `derek_beach.py` → `["causal", "evidence"]`
   - `contradiction_deteccion.py` → `["coherence"]`
   - `scoring/` → `["numerical", "evidence"]`

3. **Fallback**: Methods with no matching rules get `["structural"]`

### Output Range

Ranges are inferred from method name patterns:

- `score`, `probability`, `confidence`, `similarity`, `weight` → `[0.0, 1.0]`
- `count`, `number`, `size` → `[0, null]`
- `check`, `validate`, `verify`, `test`, `is_`, `has_` → `[0, 1]`
- All others → `null`

### Fusion Requirements

Requirements follow pattern-based assignment:

1. **Utility methods** (e.g., `__init__`, `__repr__`):
   - Required: `[]`
   - Optional: `["config"]`

2. **Analysis methods** (`analysis/` path):
   - Required: `["extracted_text", "question_id"]`
   - Optional: `["previous_analysis", "config"]`

3. **Detectors** (in derek_beach, contradiction):
   - Required: `["extracted_text", "question_id", "preprocessed_document"]`
   - Optional: `["embeddings", "previous_analysis", "config", "dependency_parse"]`

4. **Temporal methods**:
   - Required: `["extracted_text", "temporal_markers"]`
   - Optional: `["preprocessed_document", "config"]`

5. **Causal methods**:
   - Required: `["preprocessed_document", "dependency_parse"]`
   - Optional: `["temporal_markers", "domain_ontology", "config"]`

## Usage

### Filtering by Semantic Tag

```bash
# Find all coherence-related methods
jq '.[] | select(.semantic_tags | contains(["coherence"]))' config/canonical_method_catalogue_v2.json

# Find methods with both causal and evidence tags
jq '.[] | select(.semantic_tags | contains(["causal", "evidence"]))' config/canonical_method_catalogue_v2.json
```

### Finding Methods by Output Range

```bash
# Find all probability/score methods (0-1 range)
jq '.[] | select(.output_range == [0.0, 1.0])' config/canonical_method_catalogue_v2.json

# Find all count methods (unbounded)
jq '.[] | select(.output_range[1] == null and .output_range[0] >= 0)' config/canonical_method_catalogue_v2.json
```

### Checking Fusion Requirements

```bash
# Find methods that require embeddings
jq '.[] | select(.fusion_requirements.required | contains(["embeddings"]))' config/canonical_method_catalogue_v2.json

# Find methods that can use previous_analysis
jq '.[] | select(.fusion_requirements.optional | contains(["previous_analysis"]))' config/canonical_method_catalogue_v2.json
```

## Validation

All 2,163 methods in the catalog have been enriched with:
- ✓ `semantic_tags` field (non-empty array)
- ✓ `output_range` field (array or null)
- ✓ `fusion_requirements` field (object with required/optional arrays)

## Files Created/Modified

### Created:
1. `config/semantic_taxonomy.json` - Standardized tag definitions
2. `config/fusion_requirements_spec.md` - Fusion requirements specification
3. `scripts/add_semantic_metadata.jq` - JQ filter for processing
4. `scripts/process_catalog_metadata.py` - Python processing script
5. `scripts/extend_method_catalog_with_semantic_metadata.py` - Alternative Python script
6. `config/SEMANTIC_METADATA_README.md` - This documentation

### Modified:
1. `config/canonical_method_catalogue_v2.json` - Extended with semantic metadata

### Backup:
1. `config/canonical_method_catalogue_v2.json.backup` - Original version before extension

## Version

- **Semantic Taxonomy**: 1.0.0
- **Fusion Requirements Spec**: 1.0.0
- **Catalog Extension**: Applied 2024
- **Total Methods Processed**: 2,163

## References

- `config/semantic_taxonomy.json` - Complete tag definitions and taxonomy
- `config/fusion_requirements_spec.md` - Detailed fusion requirements patterns
- `src/farfan_pipeline/core/` - Pipeline orchestration using this metadata

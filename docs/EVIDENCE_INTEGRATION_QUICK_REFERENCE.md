# Evidence Extraction Integration - Quick Reference

## Test Files Created

### 1. `tests/wiring/test_evidence_extraction_integration.py`
**Primary integration tests for extract_evidence() → extract_structured_evidence()**

**Classes**:
- `TestExtractEvidenceIntegration` - Core integration validation
- `TestExtractStructuredEvidenceIntegration` - Direct function testing  
- `TestCompletenessMetricsIntegration` - Completeness calculation
- `TestRealQuestionnaireIntegration` - Real data (1,200 target)
- `TestEndToEndIntegration` - Complete pipeline

**Key Tests**:
- `test_extract_evidence_returns_structured_result()` - Validates EvidenceExtractionResult output
- `test_extract_evidence_processes_expected_elements()` - Tests element processing
- `test_extract_evidence_validates_required_elements()` - Tests missing_required tracking
- `test_extract_evidence_computes_completeness_metrics()` - Tests completeness scoring

### 2. `tests/core/test_signal_evidence_integration_validation.py`
**Comprehensive validation of all integration components**

**Classes**:
- `TestExtractEvidenceIntegrationCore` - Core integration tests
- `TestCompletenessMetricsValidation` - Completeness algorithm tests
- `TestPatternRelevanceFiltering` - Pattern filtering tests
- `TestDeduplication` - Match deduplication tests
- `TestRealQuestionnaireValidation` - Real questionnaire tests

**Key Tests**:
- `test_extract_evidence_integration_returns_structured_result()` - Structure validation
- `test_extract_evidence_achieves_high_completeness()` - Completeness with rich docs
- `test_completeness_perfect_all_required_found()` - Perfect score validation
- `test_element_specifications_coverage()` - 1,200 specification coverage

### 3. `tests/core/test_evidence_pipeline_integration.py`
**End-to-end pipeline integration tests**

**Classes**:
- `TestAnalyzeWithIntelligenceLayerIntegration` - Complete pipeline
- `TestEvidenceValidationIntegration` - Evidence + validation
- `TestMetadataPropagation` - Metadata flow
- `TestEdgeCases` - Boundary conditions
- `TestRealDataValidation` - Real questionnaire
- `TestPerformanceAndScale` - Performance tests

**Key Tests**:
- `test_analyze_complete_document_success()` - Full pipeline success
- `test_analyze_incomplete_document_validation_failure()` - Validation failure
- `test_high_completeness_passes_validation()` - Evidence → validation
- `test_pattern_metadata_in_evidence_lineage()` - Metadata propagation

## Quick Test Commands

```bash
# Run all integration tests
pytest tests/wiring/test_evidence_extraction_integration.py \
       tests/core/test_signal_evidence_integration_validation.py \
       tests/core/test_evidence_pipeline_integration.py -v

# Run specific test class
pytest tests/wiring/test_evidence_extraction_integration.py::TestExtractEvidenceIntegration -v

# Run specific test
pytest tests/wiring/test_evidence_extraction_integration.py::TestExtractEvidenceIntegration::test_extract_evidence_returns_structured_result -v

# Run with real data validation output
pytest tests/core/test_signal_evidence_integration_validation.py::TestRealQuestionnaireValidation -v -s

# Run with coverage
pytest tests/wiring/test_evidence_extraction_integration.py --cov=farfan_pipeline.core.orchestrator.signal_evidence_extractor --cov=farfan_pipeline.core.orchestrator.signal_intelligence_layer
```

## Key Validation Points

### ✓ Structured Output
```python
# Test validates EvidenceExtractionResult, not text blob
assert isinstance(result, EvidenceExtractionResult)
assert isinstance(result.evidence, dict)
assert not isinstance(result.evidence, str)
```

### ✓ Expected Elements Processing
```python
# All element types processed
for element_type in expected_types:
    assert element_type in result.evidence

# Required elements tracked
assert "baseline" in result.missing_required
assert result.completeness < 1.0
```

### ✓ Completeness Metrics
```python
# Score range validation
assert 0.0 <= result.completeness <= 1.0

# Required: binary scoring
assert score == 1.0  # found
assert score == 0.0  # not found

# Minimum: proportional scoring
assert score == 0.5  # 2 of 4 found
```

### ✓ Confidence Propagation
```python
# Each match has confidence from pattern
for match in result.evidence["element_type"]:
    assert "confidence" in match
    assert 0.0 <= match["confidence"] <= 1.0
    assert "pattern_id" in match
```

### ✓ Metadata & Lineage
```python
# Extraction metadata
assert "expected_count" in result.extraction_metadata
assert "pattern_count" in result.extraction_metadata
assert "total_matches" in result.extraction_metadata

# Match lineage
assert "lineage" in match
assert match["lineage"]["pattern_id"] == "PAT_001"
assert match["lineage"]["element_type"] == "baseline"
```

## Expected Elements Formats

### Dict Format (Full Specification)
```python
{
    "type": "baseline_indicator",
    "required": True,
    "minimum": 2
}
```

### String Format (Legacy)
```python
"baseline_indicator"
```

### Complete Example
```python
signal_node = {
    "expected_elements": [
        {"type": "baseline", "required": True},
        {"type": "target", "required": True},
        {"type": "timeline", "required": False},
        {"type": "sources", "minimum": 3},
        "optional_element"
    ],
    "patterns": [...],
    "validations": {}
}
```

## Completeness Scoring Examples

### Perfect Score (1.0)
```python
# All required found
evidence = {
    "baseline": [{"value": "10%"}],
    "target": [{"value": "20%"}]
}
expected = [
    {"type": "baseline", "required": True},
    {"type": "target", "required": True}
]
# completeness = 1.0
```

### Zero Score (0.0)
```python
# No required found
evidence = {"baseline": [], "target": []}
expected = [
    {"type": "baseline", "required": True},
    {"type": "target", "required": True}
]
# completeness = 0.0
```

### Partial Score
```python
# 1 of 2 required found
evidence = {
    "baseline": [{"value": "10%"}],
    "target": []
}
expected = [
    {"type": "baseline", "required": True},
    {"type": "target", "required": True}
]
# completeness = 0.5
```

### Minimum Cardinality
```python
# 2 of 4 minimum found
evidence = {
    "sources": [{"value": "DANE"}, {"value": "DNP"}]
}
expected = [
    {"type": "sources", "minimum": 4}
]
# completeness = 0.5 (2/4)
```

## Integration Flow

```
1. EnrichedSignalPack.extract_evidence()
   ↓
2. extract_structured_evidence()
   ↓
3. For each expected element:
   - Filter relevant patterns by element type
   - Apply pattern matching
   - Track required/minimum
   ↓
4. Compute completeness:
   - Required: binary (0.0 or 1.0)
   - Minimum: proportional (found/minimum)
   - Optional: presence bonus
   ↓
5. Return EvidenceExtractionResult:
   - evidence: dict[element_type, matches]
   - completeness: float (0.0-1.0)
   - missing_required: list[str]
   - under_minimum: list[tuple]
   - extraction_metadata: dict
```

## Common Assertions

```python
# Structured result
assert isinstance(result, EvidenceExtractionResult)
assert isinstance(result.evidence, dict)

# Completeness range
assert 0.0 <= result.completeness <= 1.0

# Evidence structure
for element_type, matches in result.evidence.items():
    assert isinstance(matches, list)
    for match in matches:
        assert "value" in match
        assert "confidence" in match
        assert "pattern_id" in match
        assert "category" in match
        assert "lineage" in match

# Metadata
assert "expected_count" in result.extraction_metadata
assert "pattern_count" in result.extraction_metadata
assert "total_matches" in result.extraction_metadata

# Required tracking
if len(result.evidence["elem"]) == 0:
    assert "elem" in result.missing_required

# Minimum tracking
if found < minimum:
    assert ("elem", found, minimum) in result.under_minimum
```

## Real Data Validation

```python
# Load real questionnaire
questionnaire = load_questionnaire()
micro_questions = questionnaire.get_micro_questions()

# Find nodes with expected_elements
nodes_with_elements = [
    mq for mq in micro_questions 
    if mq.get("expected_elements")
]

# Test with real signal node
for mq in nodes_with_elements[:10]:
    result = enriched.extract_evidence(
        text=sample_text,
        signal_node=mq,
        document_context=None
    )
    
    assert isinstance(result, EvidenceExtractionResult)
    assert 0.0 <= result.completeness <= 1.0
```

## Coverage Goals

- [x] **Structured Output**: 100% EvidenceExtractionResult
- [x] **Expected Elements**: All formats (dict, string, mixed)
- [x] **Completeness**: All scenarios (0.0, partial, 1.0)
- [x] **Required Tracking**: missing_required list
- [x] **Minimum Tracking**: under_minimum list
- [x] **Confidence**: Pattern → match propagation
- [x] **Metadata**: Extraction metadata & lineage
- [x] **Real Data**: 10+ signal nodes per suite
- [x] **Integration**: Complete pipeline validation
- [x] **1,200 Target**: Element specification coverage

## Success Criteria

✓ All tests pass  
✓ Structured output validated  
✓ Completeness metrics accurate  
✓ Expected elements processed  
✓ Real data validation  
✓ Integration flow validated  
✓ Metadata propagation verified  
✓ Performance acceptable

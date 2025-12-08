# Cross-Document Comparative Analysis - Quick Reference

## One-Liner Examples

### Basic Usage
```python
from farfan_pipeline.analysis.cross_document_comparative import CrossDocumentAnalyzer

analyzer = CrossDocumentAnalyzer()
analyzer.add_documents(canon_packages)
top_strategic = analyzer.find_pdts_with_highest_strategic_importance(n=10)
```

### SPC Integration
```python
from farfan_pipeline.analysis.cross_document_integration import CrossDocumentPipeline

pipeline = CrossDocumentPipeline()
analyzer = pipeline.process_spc_batch({'doc_001': smart_chunks})
```

## Common Queries

### Find Top Documents
```python
# By strategic importance
analyzer.find_pdts_with_highest_strategic_importance(n=10)

# By causal chain strength
analyzer.identify_municipalities_with_strongest_causal_chains(n=10, min_chain_length=3)

# By coherence score
analyzer.compare_documents_by_coherence_score()

# By semantic density
analyzer.compare_documents_by_semantic_density()

# By completeness
analyzer.compare_documents_by_completeness_index()
```

### Custom Queries
```python
from farfan_pipeline.analysis.cross_document_comparative import (
    ComparisonDimension, AggregationMethod, ComparisonOperator
)

# Compare by any dimension
analyzer.query_engine.compare_by_dimension(
    dimension=ComparisonDimension.COHERENCE_SCORE,
    aggregation=AggregationMethod.MEAN
)

# Top N documents
analyzer.query_engine.find_top_documents(
    dimension=ComparisonDimension.STRATEGIC_IMPORTANCE,
    n=10
)

# Threshold filtering
analyzer.query_engine.find_documents_by_threshold(
    dimension=ComparisonDimension.COHERENCE_SCORE,
    operator=ComparisonOperator.GREATER_EQUAL,
    threshold=0.75
)

# With policy area filter
analyzer.query_engine.compare_by_dimension(
    dimension=ComparisonDimension.SEMANTIC_DENSITY,
    policy_area_filter=["PA01", "PA02"]
)

# With dimension filter
analyzer.query_engine.compare_by_dimension(
    dimension=ComparisonDimension.COHERENCE_SCORE,
    dimension_filter=["DIM01"]
)
```

### Statistics
```python
# Global statistics
stats = analyzer.get_global_statistics(ComparisonDimension.COMPLETENESS_INDEX)
print(f"Mean: {stats.global_mean}, Median: {stats.global_median}")

# Per-document stats
for doc_id, doc_stats in stats.per_document_stats.items():
    print(f"{doc_id}: {doc_stats['mean']:.4f}")

# Per-policy-area stats
for pa, pa_stats in stats.per_policy_area_stats.items():
    print(f"{pa}: {pa_stats['mean']:.4f}")
```

### Export Results
```python
# Export comparison report
analyzer.export_comparison_report(result, "report.json")

# Export statistics report
analyzer.export_statistics_report(stats, "statistics.json")
```

## CLI Commands

```bash
# Compare documents
python -m farfan_pipeline.scripts.cross_document_cli compare \
    packages/ --dimension coherence_score --output report.json

# Top strategic documents
python -m farfan_pipeline.scripts.cross_document_cli top-strategic \
    packages/ --top-n 10 --output top_strategic.json

# Strongest causal chains
python -m farfan_pipeline.scripts.cross_document_cli strongest-causal \
    packages/ --top-n 10 --min-chain-length 3 --output causal.json

# Statistics
python -m farfan_pipeline.scripts.cross_document_cli statistics \
    packages/ --dimension completeness_index --output stats.json

# Threshold query
python -m farfan_pipeline.scripts.cross_document_cli threshold \
    packages/ --dimension coherence_score --operator gte --threshold 0.75
```

## REST API

### cURL Examples

```bash
# Health check
curl http://localhost:5000/api/v1/cross-document/health

# Compare documents
curl -X POST http://localhost:5000/api/v1/cross-document/compare \
  -H "Content-Type: application/json" \
  -d '{"dimension": "strategic_importance", "aggregation_method": "mean", "top_n": 10}'

# Highest strategic importance
curl http://localhost:5000/api/v1/cross-document/highest-strategic-importance?n=10

# Strongest causal chains
curl -X POST http://localhost:5000/api/v1/cross-document/strongest-causal-chains \
  -H "Content-Type: application/json" \
  -d '{"top_n": 10, "min_chain_length": 3}'

# Threshold query
curl -X POST http://localhost:5000/api/v1/cross-document/threshold-query \
  -H "Content-Type: application/json" \
  -d '{"dimension": "coherence_score", "operator": "gte", "threshold": 0.75}'

# Statistics
curl -X POST http://localhost:5000/api/v1/cross-document/statistics \
  -H "Content-Type: application/json" \
  -d '{"dimension": "completeness_index"}'

# Index info
curl http://localhost:5000/api/v1/cross-document/index-info
```

## Comparison Dimensions

| Enum Value | Description |
|------------|-------------|
| `SEMANTIC_DENSITY` | Semantic information density |
| `COHERENCE_SCORE` | Textual coherence metrics |
| `COMPLETENESS_INDEX` | Coverage and completeness |
| `STRATEGIC_IMPORTANCE` | Strategic value assessment |
| `CAUSAL_CHAIN_STRENGTH` | Causal reasoning strength |
| `INFORMATION_DENSITY` | Information content metrics |
| `ACTIONABILITY_SCORE` | Implementability assessment |
| `BUDGET_LINKAGE` | Budget connection indicator |
| `TEMPORAL_ROBUSTNESS` | Temporal coverage |
| `PROVENANCE_COMPLETENESS` | Source traceability |

## Aggregation Methods

| Enum Value | Description |
|------------|-------------|
| `MEAN` | Average value |
| `MEDIAN` | Median value |
| `MAX` | Maximum value |
| `MIN` | Minimum value |
| `SUM` | Total sum |
| `WEIGHTED_MEAN` | Weighted average |
| `PERCENTILE_90` | 90th percentile |
| `PERCENTILE_95` | 95th percentile |

## Comparison Operators

| Enum Value | Symbol | Description |
|------------|--------|-------------|
| `GREATER_THAN` | `gt` | Value > threshold |
| `GREATER_EQUAL` | `gte` | Value >= threshold |
| `LESS_THAN` | `lt` | Value < threshold |
| `LESS_EQUAL` | `lte` | Value <= threshold |
| `EQUAL` | `eq` | Value == threshold |
| `NOT_EQUAL` | `neq` | Value != threshold |
| `TOP_N` | - | Top N results |
| `BOTTOM_N` | - | Bottom N results |
| `IN_RANGE` | - | Within range |

## Index Operations

```python
# Get indexed documents
doc_ids = analyzer.index.get_all_document_ids()

# Get policy areas
policy_areas = analyzer.index.get_all_policy_areas()

# Get dimensions
dimensions = analyzer.index.get_all_dimensions()

# Get document metadata
doc_meta = analyzer.index.get_document(doc_id)

# Get chunks for document
chunks = analyzer.index.get_document_chunks(doc_id)

# Get chunks for policy area
pa_chunks = analyzer.index.get_policy_area_chunks("PA01")

# Get chunks for dimension
dim_chunks = analyzer.index.get_dimension_chunks("DIM01")

# Get chunks for PA + DIM
chunks = analyzer.index.get_policy_area_dimension_chunks("PA01", "DIM01")

# Compute index hash
hash_value = analyzer.index.compute_index_hash()
```

## Type Safety

All components use Pydantic for validation:

```python
from farfan_pipeline.analysis.cross_document_comparative import (
    ChunkMetrics,
    DocumentMetadata,
    ComparativeResult,
    MultiDocumentStatistics,
)

# All operations are type-safe and validated
result: ComparativeResult = analyzer.find_pdts_with_highest_strategic_importance(n=10)
stats: MultiDocumentStatistics = analyzer.get_global_statistics(ComparisonDimension.COHERENCE_SCORE)
```

## Error Handling

```python
try:
    analyzer.add_document(canon_package)
except ValueError as e:
    print(f"Invalid document: {e}")

try:
    result = analyzer.query_engine.compare_by_dimension(...)
except RuntimeError as e:
    print(f"Query failed: {e}")
```

## Performance Tips

1. **Batch indexing**: Add all documents before querying
2. **Filter early**: Use policy_area_filter and dimension_filter
3. **Choose aggregation wisely**: MEAN is fastest, PERCENTILE_95 is slowest
4. **Cache results**: Store frequently used statistics
5. **Index hash**: Use for cache invalidation

## Testing

```bash
# Unit tests
pytest tests/analysis/test_cross_document_comparative.py -v

# Integration tests
pytest tests/integration/test_cross_document_integration.py -v

# With coverage
pytest tests/ --cov=farfan_pipeline.analysis.cross_document_comparative
```

## Import Paths

```python
# Core framework
from farfan_pipeline.analysis.cross_document_comparative import (
    CrossDocumentAnalyzer,
    DocumentIndex,
    ComparativeQueryEngine,
    ComparisonDimension,
    AggregationMethod,
    ComparisonOperator,
    ComparativeResult,
    MultiDocumentStatistics,
)

# SPC integration
from farfan_pipeline.analysis.cross_document_integration import (
    CrossDocumentPipeline,
    SPCEnricher,
    MockCanonPackageAdapter,
)

# REST API
from farfan_pipeline.api.cross_document_api import (
    cross_document_bp,
    initialize_analyzer,
)
```

## Full Documentation

- Architecture: `docs/CROSS_DOCUMENT_COMPARATIVE_ANALYSIS.md`
- Module README: `src/farfan_pipeline/analysis/README_CROSS_DOCUMENT.md`
- Examples: `examples/cross_document_analysis_example.py`

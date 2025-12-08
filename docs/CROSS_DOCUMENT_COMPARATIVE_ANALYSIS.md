# Cross-Document Comparative Analysis Framework

## Overview

Industrial-grade framework for multi-document comparative analysis that leverages `CanonPolicyPackage` metadata and SPC (Smart Policy Chunks) rich metadata to enable sophisticated cross-document queries and comparisons.

## Features

### Multi-Document Indexing
- **Document ID Tracking**: Leverages `document_id` field in `CanonPolicyPackage` for unique document identification
- **Chunk-Level Metadata**: Indexes rich metadata from SPC including:
  - `semantic_density`: Semantic information density of chunks
  - `coherence_score`: Textual coherence metrics
  - `completeness_index`: Coverage and completeness indicators
  - `strategic_importance`: Strategic value assessment
  - `causal_chain_strength`: Strength of causal reasoning chains
  - `information_density`: Information content metrics
  - `actionability_score`: Implementability assessment

### Comparative Query Capabilities
1. **Dimension-Based Comparisons**: Compare documents across any metadata dimension
2. **Policy Area Analysis**: Cross-document comparisons by policy area (PA01-PA10)
3. **Dimension Analysis**: Comparative analysis by dimension (DIM01-DIM06)
4. **Threshold Queries**: Find documents meeting specific criteria
5. **Ranking Queries**: Top-N documents by selected metrics
6. **Statistical Analysis**: Global and per-document/area/dimension statistics

### Production-Ready Features
- Full type safety with Pydantic validation
- Comprehensive error handling and logging
- REST API integration
- CLI tool for batch operations
- Export capabilities (JSON reports)
- Industrial performance optimization

## Architecture

### Core Components

#### 1. DocumentIndex
Multi-dimensional indexing structure:
```python
from farfan_pipeline.analysis.cross_document_comparative import DocumentIndex

index = DocumentIndex()
index.add_document(canon_package)

# Access indexed data
chunks = index.get_document_chunks(document_id)
policy_area_chunks = index.get_policy_area_chunks("PA01")
dimension_chunks = index.get_dimension_chunks("DIM01")
```

#### 2. ComparativeQueryEngine
Query execution engine:
```python
from farfan_pipeline.analysis.cross_document_comparative import (
    ComparativeQueryEngine,
    ComparisonDimension,
    AggregationMethod
)

engine = ComparativeQueryEngine(index)

# Compare by dimension
result = engine.compare_by_dimension(
    dimension=ComparisonDimension.STRATEGIC_IMPORTANCE,
    aggregation=AggregationMethod.MEAN
)

# Find top documents
top_docs = engine.find_top_documents(
    dimension=ComparisonDimension.COHERENCE_SCORE,
    n=10
)

# Strongest causal chains
causal_result = engine.find_documents_with_strongest_causal_chains(
    n=10,
    min_chain_length=3
)
```

#### 3. CrossDocumentAnalyzer
High-level analysis interface:
```python
from farfan_pipeline.analysis.cross_document_comparative import CrossDocumentAnalyzer

analyzer = CrossDocumentAnalyzer()
analyzer.add_documents(canon_packages)

# Pre-built queries
strategic_result = analyzer.find_pdts_with_highest_strategic_importance(n=10)
causal_result = analyzer.identify_municipalities_with_strongest_causal_chains(n=10)
coherence_result = analyzer.compare_documents_by_coherence_score()

# Export results
analyzer.export_comparison_report(strategic_result, "strategic_report.json")
```

## Usage Examples

### Example 1: Compare Documents by Strategic Importance

```python
from farfan_pipeline.analysis.cross_document_comparative import (
    CrossDocumentAnalyzer,
    ComparisonDimension,
    AggregationMethod
)

analyzer = CrossDocumentAnalyzer()

# Add documents from CanonPolicyPackage instances
for canon_package in canon_packages:
    analyzer.add_document(canon_package)

# Find top 10 PDTs with highest strategic importance
result = analyzer.find_pdts_with_highest_strategic_importance(n=10)

# Print results
for doc_id, score, metadata in result.results:
    print(f"{doc_id}: {score:.4f}")
    print(f"  Policy Areas: {metadata['policy_areas']}")
    print(f"  Chunks: {metadata['total_chunks']}")
```

### Example 2: Identify Municipalities with Strongest Causal Chains

```python
analyzer = CrossDocumentAnalyzer()
analyzer.add_documents(canon_packages)

# Find municipalities with strongest causal reasoning
result = analyzer.identify_municipalities_with_strongest_causal_chains(
    n=10,
    min_chain_length=3
)

for doc_id, strength, metadata in result.results:
    print(f"{doc_id}: Strength={strength:.4f}")
    print(f"  Avg Chain Length: {metadata['avg_chain_length']:.2f}")
    print(f"  Max Chain Length: {metadata['max_chain_length']}")
    print(f"  Total Chunks with Chains: {metadata['total_chunks_with_causal_chains']}")
```

### Example 3: Compare by Multiple Dimensions with Filters

```python
from farfan_pipeline.analysis.cross_document_comparative import (
    CrossDocumentAnalyzer,
    ComparisonDimension,
    AggregationMethod
)

analyzer = CrossDocumentAnalyzer()
analyzer.add_documents(canon_packages)

# Compare by semantic density for specific policy area
result = analyzer.query_engine.compare_by_dimension(
    dimension=ComparisonDimension.SEMANTIC_DENSITY,
    aggregation=AggregationMethod.MEDIAN,
    policy_area_filter=["PA01", "PA02"]
)

# Compare by coherence for specific dimension
coherence_result = analyzer.query_engine.compare_by_dimension(
    dimension=ComparisonDimension.COHERENCE_SCORE,
    aggregation=AggregationMethod.PERCENTILE_90,
    dimension_filter=["DIM01"]
)
```

### Example 4: Global Statistics and Analysis

```python
from farfan_pipeline.analysis.cross_document_comparative import ComparisonDimension

analyzer = CrossDocumentAnalyzer()
analyzer.add_documents(canon_packages)

# Compute global statistics
stats = analyzer.get_global_statistics(ComparisonDimension.COMPLETENESS_INDEX)

print(f"Global Mean: {stats.global_mean:.4f}")
print(f"Global Median: {stats.global_median:.4f}")
print(f"Global Std: {stats.global_std:.4f}")

# Per-document statistics
for doc_id, doc_stats in stats.per_document_stats.items():
    print(f"{doc_id}: Mean={doc_stats['mean']:.4f}, Count={doc_stats['count']}")

# Per-policy-area statistics
for pa, pa_stats in stats.per_policy_area_stats.items():
    print(f"{pa}: Mean={pa_stats['mean']:.4f}")
```

### Example 5: Threshold Queries

```python
from farfan_pipeline.analysis.cross_document_comparative import (
    ComparisonDimension,
    ComparisonOperator,
    AggregationMethod
)

analyzer = CrossDocumentAnalyzer()
analyzer.add_documents(canon_packages)

# Find documents with coherence score >= 0.75
result = analyzer.query_engine.find_documents_by_threshold(
    dimension=ComparisonDimension.COHERENCE_SCORE,
    operator=ComparisonOperator.GREATER_EQUAL,
    threshold=0.75,
    aggregation=AggregationMethod.MEAN
)

print(f"Found {result.total_documents} documents with coherence >= 0.75")
for doc_id, score, _ in result.results:
    print(f"  {doc_id}: {score:.4f}")
```

## CLI Usage

### Compare Documents
```bash
python -m farfan_pipeline.scripts.cross_document_cli compare \
    /path/to/packages/*.json \
    --dimension strategic_importance \
    --aggregation mean \
    --output comparison_report.json
```

### Find Top Strategic Documents
```bash
python -m farfan_pipeline.scripts.cross_document_cli top-strategic \
    /path/to/packages/ \
    --top-n 10 \
    --output top_strategic.json
```

### Find Strongest Causal Chains
```bash
python -m farfan_pipeline.scripts.cross_document_cli strongest-causal \
    /path/to/packages/ \
    --top-n 10 \
    --min-chain-length 3 \
    --output strongest_causal.json
```

### Compute Statistics
```bash
python -m farfan_pipeline.scripts.cross_document_cli statistics \
    /path/to/packages/ \
    --dimension coherence_score \
    --output statistics_report.json
```

### Threshold Query
```bash
python -m farfan_pipeline.scripts.cross_document_cli threshold \
    /path/to/packages/ \
    --dimension completeness_index \
    --operator gte \
    --threshold 0.70 \
    --aggregation mean \
    --output threshold_results.json
```

## REST API

### Initialize API
```python
from flask import Flask
from farfan_pipeline.api.cross_document_api import cross_document_bp, initialize_analyzer
from farfan_pipeline.analysis.cross_document_comparative import CrossDocumentAnalyzer

app = Flask(__name__)

# Initialize analyzer
analyzer = CrossDocumentAnalyzer()
analyzer.add_documents(canon_packages)
initialize_analyzer(analyzer)

# Register blueprint
app.register_blueprint(cross_document_bp)

app.run(debug=False, port=5000)
```

### API Endpoints

#### Health Check
```bash
GET /api/v1/cross-document/health
```

#### Compare Documents
```bash
POST /api/v1/cross-document/compare
Content-Type: application/json

{
  "dimension": "strategic_importance",
  "aggregation_method": "mean",
  "policy_area_filter": ["PA01", "PA02"],
  "top_n": 10
}
```

#### Highest Strategic Importance
```bash
GET /api/v1/cross-document/highest-strategic-importance?n=10
```

#### Strongest Causal Chains
```bash
POST /api/v1/cross-document/strongest-causal-chains
Content-Type: application/json

{
  "top_n": 10,
  "min_chain_length": 3
}
```

#### Threshold Query
```bash
POST /api/v1/cross-document/threshold-query
Content-Type: application/json

{
  "dimension": "coherence_score",
  "operator": "gte",
  "threshold": 0.75,
  "aggregation_method": "mean"
}
```

#### Global Statistics
```bash
POST /api/v1/cross-document/statistics
Content-Type: application/json

{
  "dimension": "completeness_index"
}
```

#### Compare Policy Areas
```bash
GET /api/v1/cross-document/compare-policy-areas?dimension=strategic_importance&aggregation=mean
```

#### Compare Dimensions
```bash
GET /api/v1/cross-document/compare-dimensions?comparison_dimension=coherence_score&aggregation=median
```

#### Index Info
```bash
GET /api/v1/cross-document/index-info
```

## Integration with SPC Pipeline

### Direct Integration
```python
from farfan_pipeline.analysis.cross_document_integration import CrossDocumentPipeline

pipeline = CrossDocumentPipeline()

# Process SPC batches
spc_batches = {
    "document_001": smart_chunks_1,
    "document_002": smart_chunks_2,
    "document_003": smart_chunks_3,
}

analyzer = pipeline.process_spc_batch(spc_batches)

# Run comparative queries
result = analyzer.find_pdts_with_highest_strategic_importance(n=10)
```

### Enrichment from SmartPolicyChunks
```python
from farfan_pipeline.analysis.cross_document_integration import SPCEnricher

enricher = SPCEnricher()

# Convert SmartPolicyChunks to CanonPolicyPackage format
enriched_package = enricher.enrich_canon_package_from_spc(
    smart_chunks=smart_chunks,
    document_id="municipality_001",
    schema_version="SPC-2025.1"
)

# Add to analyzer
analyzer.add_document(enriched_package)

# Extract metrics summary
summary = enricher.extract_spc_metrics_summary(smart_chunks)
print(f"Average Semantic Density: {summary['semantic_density']['mean']:.4f}")
print(f"Average Coherence Score: {summary['coherence_score']['mean']:.4f}")
```

## Comparison Dimensions

Available dimensions for comparison:

| Dimension | Description | Source |
|-----------|-------------|--------|
| `SEMANTIC_DENSITY` | Semantic information density | SPC metadata |
| `COHERENCE_SCORE` | Textual coherence metrics | SPC metadata |
| `COMPLETENESS_INDEX` | Coverage and completeness | SPC metadata |
| `STRATEGIC_IMPORTANCE` | Strategic value assessment | SPC metadata |
| `CAUSAL_CHAIN_STRENGTH` | Strength of causal chains | Computed from causal_chain |
| `INFORMATION_DENSITY` | Information content metrics | SPC metadata |
| `ACTIONABILITY_SCORE` | Implementability assessment | SPC metadata |
| `BUDGET_LINKAGE` | Budget connection indicator | Boolean from chunk.budget |
| `TEMPORAL_ROBUSTNESS` | Temporal coverage | From time_facets |
| `PROVENANCE_COMPLETENESS` | Source traceability | From provenance |

## Aggregation Methods

Available aggregation methods:

- `MEAN`: Average value across chunks
- `MEDIAN`: Median value across chunks
- `MAX`: Maximum value across chunks
- `MIN`: Minimum value across chunks
- `SUM`: Total sum across chunks
- `WEIGHTED_MEAN`: Weighted average (by chunk size)
- `PERCENTILE_90`: 90th percentile
- `PERCENTILE_95`: 95th percentile

## Comparison Operators

Available comparison operators for threshold queries:

- `GREATER_THAN` (gt): Value > threshold
- `GREATER_EQUAL` (gte): Value >= threshold
- `LESS_THAN` (lt): Value < threshold
- `LESS_EQUAL` (lte): Value <= threshold
- `EQUAL` (eq): Value == threshold
- `NOT_EQUAL` (neq): Value != threshold
- `TOP_N`: Top N results
- `BOTTOM_N`: Bottom N results
- `IN_RANGE`: Value within range

## Performance Considerations

### Indexing Performance
- **O(n)** indexing time where n = total chunks across all documents
- Incremental indexing supported (add documents one at a time)
- Index hash caching for quick validation

### Query Performance
- **O(m)** query time where m = chunks matching filters
- Policy area/dimension filtering reduces search space
- Aggregation computed on-demand with numpy optimization

### Memory Considerations
- Index stores lightweight ChunkMetrics (not full chunk text)
- Estimated: ~1KB per chunk metadata
- For 100 documents × 60 chunks = 6000 chunks = ~6MB memory

## Error Handling

### Validation Errors
```python
try:
    analyzer.add_document(canon_package)
except ValueError as e:
    print(f"Invalid document: {e}")
```

### Query Errors
```python
try:
    result = analyzer.query_engine.compare_by_dimension(
        dimension=ComparisonDimension.SEMANTIC_DENSITY,
        aggregation=AggregationMethod.MEAN
    )
except RuntimeError as e:
    print(f"Query failed: {e}")
```

## Testing

### Unit Tests
```bash
pytest tests/analysis/test_cross_document_comparative.py -v
```

### Integration Tests
```bash
pytest tests/integration/test_cross_document_integration.py -v
```

## Future Enhancements

1. **Advanced Queries**:
   - Multi-dimensional scoring
   - Weighted dimension combinations
   - Custom scoring functions

2. **Temporal Analysis**:
   - Time-series comparison across documents
   - Trend detection
   - Evolution tracking

3. **Visualization**:
   - Interactive dashboards
   - Comparison heatmaps
   - Network graphs

4. **Caching & Optimization**:
   - Query result caching
   - Materialized views for common queries
   - Parallel query execution

5. **Export Formats**:
   - Excel reports
   - PDF summaries
   - Interactive HTML reports

## References

- `CanonPolicyPackage`: See `src/farfan_pipeline/processing/models.py`
- `SmartPolicyChunk`: See `src/farfan_pipeline/processing/spc_ingestion.py`
- SPC Pipeline: See `docs/SPC_PIPELINE.md`
- API Documentation: See `docs/API_REFERENCE.md`

# Cross-Document Comparative Analysis - Quick Start Guide

## 5-Minute Setup

### 1. Import the Framework
```python
from farfan_pipeline.analysis.cross_document_comparative import CrossDocumentAnalyzer
```

### 2. Initialize Analyzer
```python
analyzer = CrossDocumentAnalyzer()
```

### 3. Add Documents
```python
# From CanonPolicyPackage instances
analyzer.add_documents(canon_packages)

# Or one at a time
analyzer.add_document(canon_package)
```

### 4. Run Queries
```python
# Find top strategic documents
result = analyzer.find_pdts_with_highest_strategic_importance(n=10)

# Identify strongest causal chains
causal_result = analyzer.identify_municipalities_with_strongest_causal_chains(n=10)

# Compare by coherence
coherence_result = analyzer.compare_documents_by_coherence_score()
```

### 5. Access Results
```python
for doc_id, score, metadata in result.results:
    print(f"{doc_id}: {score:.4f}")
```

## Common Tasks

### Task 1: Find Top 10 Most Strategic PDTs
```python
analyzer = CrossDocumentAnalyzer()
analyzer.add_documents(canon_packages)
result = analyzer.find_pdts_with_highest_strategic_importance(n=10)

for rank, (doc_id, score, meta) in enumerate(result.results, 1):
    print(f"{rank}. {doc_id}: {score:.4f}")
```

### Task 2: Find Municipalities with Strong Causal Chains
```python
result = analyzer.identify_municipalities_with_strongest_causal_chains(
    n=10, 
    min_chain_length=3
)

for doc_id, strength, meta in result.results:
    print(f"{doc_id}: Strength={strength:.4f}, Avg Length={meta['avg_chain_length']:.2f}")
```

### Task 3: Compare Documents Across Dimensions
```python
from farfan_pipeline.analysis.cross_document_comparative import ComparisonDimension

semantic = analyzer.query_engine.compare_by_dimension(
    ComparisonDimension.SEMANTIC_DENSITY
)

coherence = analyzer.query_engine.compare_by_dimension(
    ComparisonDimension.COHERENCE_SCORE
)

completeness = analyzer.query_engine.compare_by_dimension(
    ComparisonDimension.COMPLETENESS_INDEX
)
```

### Task 4: Filter by Quality Threshold
```python
from farfan_pipeline.analysis.cross_document_comparative import ComparisonOperator

high_quality = analyzer.query_engine.find_documents_by_threshold(
    dimension=ComparisonDimension.COHERENCE_SCORE,
    operator=ComparisonOperator.GREATER_EQUAL,
    threshold=0.75
)

print(f"Found {high_quality.total_documents} high-quality documents")
```

### Task 5: Generate Statistics Report
```python
stats = analyzer.get_global_statistics(ComparisonDimension.COMPLETENESS_INDEX)

print(f"Mean: {stats.global_mean:.4f}")
print(f"Median: {stats.global_median:.4f}")
print(f"Std Dev: {stats.global_std:.4f}")

# Export to file
analyzer.export_statistics_report(stats, "completeness_stats.json")
```

## CLI Quick Start

### Compare Documents
```bash
python -m farfan_pipeline.scripts.cross_document_cli compare \
    /path/to/packages/ \
    --dimension strategic_importance \
    --output report.json
```

### Find Top Strategic
```bash
python -m farfan_pipeline.scripts.cross_document_cli top-strategic \
    /path/to/packages/ \
    --top-n 10
```

### Find Strongest Causal Chains
```bash
python -m farfan_pipeline.scripts.cross_document_cli strongest-causal \
    /path/to/packages/ \
    --min-chain-length 3
```

## REST API Quick Start

### Start Server
```python
from flask import Flask
from farfan_pipeline.api.cross_document_api import cross_document_bp, initialize_analyzer
from farfan_pipeline.analysis.cross_document_comparative import CrossDocumentAnalyzer

app = Flask(__name__)

# Initialize analyzer with data
analyzer = CrossDocumentAnalyzer()
analyzer.add_documents(canon_packages)
initialize_analyzer(analyzer)

# Register blueprint
app.register_blueprint(cross_document_bp)

# Run server
app.run(port=5000)
```

### Query Endpoints
```bash
# Health check
curl http://localhost:5000/api/v1/cross-document/health

# Top strategic
curl http://localhost:5000/api/v1/cross-document/highest-strategic-importance?n=10

# Compare
curl -X POST http://localhost:5000/api/v1/cross-document/compare \
  -H "Content-Type: application/json" \
  -d '{"dimension": "coherence_score", "top_n": 10}'
```

## SPC Integration Quick Start

```python
from farfan_pipeline.analysis.cross_document_integration import CrossDocumentPipeline

# Create pipeline
pipeline = CrossDocumentPipeline()

# Process SPC batches
spc_batches = {
    "municipality_001": smart_chunks_1,
    "municipality_002": smart_chunks_2,
    "municipality_003": smart_chunks_3,
}

# Index all documents
analyzer = pipeline.process_spc_batch(spc_batches)

# Run queries
result = analyzer.find_pdts_with_highest_strategic_importance(n=10)
```

## Available Comparison Dimensions

```python
from farfan_pipeline.analysis.cross_document_comparative import ComparisonDimension

# Use any of these:
ComparisonDimension.SEMANTIC_DENSITY
ComparisonDimension.COHERENCE_SCORE
ComparisonDimension.COMPLETENESS_INDEX
ComparisonDimension.STRATEGIC_IMPORTANCE
ComparisonDimension.CAUSAL_CHAIN_STRENGTH
ComparisonDimension.INFORMATION_DENSITY
ComparisonDimension.ACTIONABILITY_SCORE
```

## Available Aggregation Methods

```python
from farfan_pipeline.analysis.cross_document_comparative import AggregationMethod

# Use any of these:
AggregationMethod.MEAN          # Average
AggregationMethod.MEDIAN        # Median
AggregationMethod.MAX           # Maximum
AggregationMethod.MIN           # Minimum
AggregationMethod.PERCENTILE_90 # 90th percentile
AggregationMethod.PERCENTILE_95 # 95th percentile
```

## Next Steps

1. **Read Full Documentation**: `docs/CROSS_DOCUMENT_COMPARATIVE_ANALYSIS.md`
2. **Try Examples**: `examples/cross_document_analysis_example.py`
3. **Run Tests**: `pytest tests/analysis/test_cross_document_comparative.py -v`
4. **Check API Reference**: `docs/CROSS_DOCUMENT_QUICK_REFERENCE.md`

## Troubleshooting

### Issue: No documents indexed
**Solution**: Ensure CanonPolicyPackage has valid `document_id` and `chunk_graph`

### Issue: Empty results
**Solution**: Check that chunks have the metrics you're querying (e.g., coherence_score)

### Issue: Import errors
**Solution**: Ensure you're in the project root and have activated the virtual environment

## Support

For more information:
- Full Documentation: `docs/CROSS_DOCUMENT_COMPARATIVE_ANALYSIS.md`
- Implementation Summary: `CROSS_DOCUMENT_IMPLEMENTATION_SUMMARY.md`
- Quick Reference: `docs/CROSS_DOCUMENT_QUICK_REFERENCE.md`

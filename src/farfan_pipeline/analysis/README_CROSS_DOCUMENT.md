# Cross-Document Comparative Analysis

## Overview

Production-ready framework for multi-document comparative analysis that leverages `CanonPolicyPackage` metadata to enable sophisticated cross-document queries.

## Quick Start

```python
from farfan_pipeline.analysis.cross_document_comparative import CrossDocumentAnalyzer

# Initialize analyzer
analyzer = CrossDocumentAnalyzer()

# Add documents
analyzer.add_documents(canon_packages)

# Run queries
top_strategic = analyzer.find_pdts_with_highest_strategic_importance(n=10)
strongest_causal = analyzer.identify_municipalities_with_strongest_causal_chains(n=10)
coherence_comparison = analyzer.compare_documents_by_coherence_score()
```

## Key Features

### 1. Multi-Document Indexing
- Indexes documents using `document_id` from `CanonPolicyPackage`
- Tracks rich SPC metadata per chunk
- Multi-dimensional indexing (policy areas, dimensions)

### 2. Comparative Queries
- **Dimension-based**: Compare by semantic_density, coherence_score, etc.
- **Ranking**: Top-N documents by any metric
- **Threshold**: Filter documents by criteria
- **Causal chains**: Identify strongest causal reasoning
- **Statistics**: Global and granular statistics

### 3. Production Features
- Type-safe with Pydantic validation
- Comprehensive error handling
- REST API integration
- CLI tool included
- Export capabilities

## Architecture

### Core Components

1. **DocumentIndex**: Multi-dimensional indexing structure
2. **ComparativeQueryEngine**: Query execution engine
3. **CrossDocumentAnalyzer**: High-level analysis interface
4. **CrossDocumentPipeline**: SPC integration layer

## Comparison Dimensions

Available dimensions from SPC metadata:

- `SEMANTIC_DENSITY`: Semantic information density
- `COHERENCE_SCORE`: Textual coherence metrics
- `COMPLETENESS_INDEX`: Coverage and completeness
- `STRATEGIC_IMPORTANCE`: Strategic value assessment
- `CAUSAL_CHAIN_STRENGTH`: Causal reasoning strength
- `INFORMATION_DENSITY`: Information content metrics
- `ACTIONABILITY_SCORE`: Implementability assessment

## Usage Examples

### Find Top Strategic Documents
```python
result = analyzer.find_pdts_with_highest_strategic_importance(n=10)
for doc_id, score, metadata in result.results:
    print(f"{doc_id}: {score:.4f}")
```

### Identify Strongest Causal Chains
```python
result = analyzer.identify_municipalities_with_strongest_causal_chains(
    n=10, min_chain_length=3
)
```

### Compare by Multiple Dimensions
```python
from farfan_pipeline.analysis.cross_document_comparative import ComparisonDimension

coherence = analyzer.compare_documents_by_coherence_score()
semantic = analyzer.compare_documents_by_semantic_density()
completeness = analyzer.compare_documents_by_completeness_index()
```

### Threshold Queries
```python
from farfan_pipeline.analysis.cross_document_comparative import ComparisonOperator

result = analyzer.query_engine.find_documents_by_threshold(
    dimension=ComparisonDimension.COHERENCE_SCORE,
    operator=ComparisonOperator.GREATER_EQUAL,
    threshold=0.75
)
```

### Global Statistics
```python
stats = analyzer.get_global_statistics(ComparisonDimension.COMPLETENESS_INDEX)
print(f"Mean: {stats.global_mean:.4f}")
print(f"Median: {stats.global_median:.4f}")
```

## CLI Usage

```bash
# Compare documents
python -m farfan_pipeline.scripts.cross_document_cli compare \
    /path/to/packages/ --dimension strategic_importance --output report.json

# Find top strategic
python -m farfan_pipeline.scripts.cross_document_cli top-strategic \
    /path/to/packages/ --top-n 10

# Find strongest causal chains
python -m farfan_pipeline.scripts.cross_document_cli strongest-causal \
    /path/to/packages/ --min-chain-length 3

# Compute statistics
python -m farfan_pipeline.scripts.cross_document_cli statistics \
    /path/to/packages/ --dimension coherence_score
```

## REST API

```python
from flask import Flask
from farfan_pipeline.api.cross_document_api import cross_document_bp, initialize_analyzer

app = Flask(__name__)
initialize_analyzer(analyzer)
app.register_blueprint(cross_document_bp)
app.run(port=5000)
```

### Endpoints

- `GET /api/v1/cross-document/health`
- `POST /api/v1/cross-document/compare`
- `GET /api/v1/cross-document/highest-strategic-importance`
- `POST /api/v1/cross-document/strongest-causal-chains`
- `POST /api/v1/cross-document/threshold-query`
- `POST /api/v1/cross-document/statistics`

## Integration with SPC Pipeline

```python
from farfan_pipeline.analysis.cross_document_integration import CrossDocumentPipeline

pipeline = CrossDocumentPipeline()

# Process SPC batches
spc_batches = {
    "doc_001": smart_chunks_1,
    "doc_002": smart_chunks_2,
}

analyzer = pipeline.process_spc_batch(spc_batches)
result = analyzer.find_pdts_with_highest_strategic_importance(n=10)
```

## Module Structure

```
analysis/
├── cross_document_comparative.py    # Core framework
├── cross_document_integration.py    # SPC integration
└── README_CROSS_DOCUMENT.md        # This file

api/
└── cross_document_api.py           # REST API

scripts/
└── cross_document_cli.py           # CLI tool

tests/
├── analysis/
│   └── test_cross_document_comparative.py
└── integration/
    └── test_cross_document_integration.py
```

## Performance

- **Indexing**: O(n) where n = total chunks
- **Query**: O(m) where m = filtered chunks
- **Memory**: ~1KB per chunk metadata

## Testing

```bash
# Unit tests
pytest tests/analysis/test_cross_document_comparative.py -v

# Integration tests
pytest tests/integration/test_cross_document_integration.py -v
```

## Documentation

Full documentation: `docs/CROSS_DOCUMENT_COMPARATIVE_ANALYSIS.md`

## Requirements

- Python 3.12+
- numpy
- pydantic
- Flask (for API)

## License

See project LICENSE file.

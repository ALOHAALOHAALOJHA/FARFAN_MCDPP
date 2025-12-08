# PDT Parsing Tests

This directory contains unit and integration tests for the PDT (Plan de Desarrollo Territorial) structure extractor and parser.

## Overview

The PDT parser extracts structured information from Colombian territorial development plans, including:

- **Tokenization**: Split text on whitespace and count tokens
- **Block Detection**: Identify CAPÍTULO, Línea estratégica, Eje estratégico, and PROGRAMA blocks
- **Hierarchy Validation**: Extract and validate numbered headers (1, 1.1, 1.1.1 format)
- **Sequence Verification**: Verify block ordering and detect inversions
- **Section Analysis**: Extract Diagnóstico, Estratégica, PPI, and Seguimiento sections
- **Table Extraction**: Parse Matriz de Indicadores and Plan Plurianual de Inversiones tables

## Test Files

### `test_pdt_structure.py`
Unit tests for all dataclasses:
- `BlockInfo`: Block metadata (text, tokens, numbers count)
- `HeaderInfo`: Header metadata (level, text, valid numbering)
- `SectionInfo`: Section metadata (presence, tokens, keywords, sources)
- `IndicatorRow`: Indicator matrix row data
- `PPIRow`: PPI matrix row data
- `PDTStructure`: Complete extracted structure

### `test_pdt_parser.py`
Unit tests for parser functionality:
- Tokenization
- Block detection with minimum thresholds
- Header extraction and numbering validation
- Hierarchy scoring (1.0 if ≥80% valid, 0.5 if ≥50%, 0.0 otherwise)
- Sequence verification (1.0 if 0 inversions, 0.5 if 1, 0.0 if ≥2)
- Section analysis with keyword matching
- Table extraction from text

### `test_pdt_parser_pdf.py`
Tests for PDF processing:
- PDF text extraction using PyMuPDF
- Multi-page document handling
- Error handling for missing files
- End-to-end PDF parsing flow

### `test_pdt_integration.py`
Integration tests with realistic PDT content:
- Complete parsing workflow
- Accuracy validation for all components
- Cross-component consistency checks
- Data completeness verification

## Running Tests

```bash
# Run all PDT parsing tests
pytest tests/processing/parsing_tests/ -v

# Run specific test file
pytest tests/processing/parsing_tests/test_pdt_parser.py -v

# Run with coverage
pytest tests/processing/parsing_tests/ -v --cov=farfan_pipeline.processing.pdt_parser --cov=farfan_pipeline.processing.pdt_structure

# Run integration tests only
pytest tests/processing/parsing_tests/test_pdt_integration.py -v
```

## Test Data

The integration tests use a comprehensive sample PDT that includes:
- Multiple chapters and sections
- Hierarchical numbering (1, 1.1, 1.1.1, etc.)
- All four major sections (Diagnóstico, Estratégica, PPI, Seguimiento)
- Indicator matrix with 10 rows
- PPI matrix with 12 investment projects
- Bibliographic references

## Implementation Details

### Tokenization
- Simple whitespace-based splitting
- Count total tokens for document

### Block Detection
- Regex patterns for CAPÍTULO, Línea estratégica, Eje estratégico, PROGRAMA
- Minimum thresholds: 10 tokens, 1 number
- Extract block text spans

### Hierarchy Validation
- Extract numbered headers using regex
- Validate numbering format (1, 1.1, 1.1.1)
- Score based on percentage of valid headers

### Sequence Verification
- Track block order
- Count inversions vs expected sequence
- Score based on inversion count

### Section Analysis
- Keyword matching for each section
- Count tokens, numbers, and sources
- Extract section boundaries

### Table Extraction
- Pattern matching for table headers
- Simple row parsing using delimiters
- Map columns to dataclass fields

## Future Enhancements

- Advanced table extraction using camelot-py or tabula-py
- OCR support for scanned PDFs
- Machine learning-based section detection
- Validation rules for indicator and PPI data
- Export to JSON/CSV formats

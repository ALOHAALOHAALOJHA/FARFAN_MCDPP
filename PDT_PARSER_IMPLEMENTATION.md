# PDT Structure Extractor Implementation

## Overview

Complete implementation of PDT (Plan de Desarrollo Territorial) structure extractor with dataclasses and parser for Colombian territorial development plans.

## Files Created

### Core Implementation

1. **`src/farfan_pipeline/processing/pdt_structure.py`**
   - `PDTStructure`: Main dataclass containing all extracted information
   - `BlockInfo`: Block metadata (text, tokens, numbers_count)
   - `HeaderInfo`: Header metadata (level, text, valid_numbering)
   - `SectionInfo`: Section metadata (present, token_count, keyword_matches, number_count, sources_found)
   - `IndicatorRow`: Matriz de Indicadores row data
   - `PPIRow`: Plan Plurianual de Inversiones row data

2. **`src/farfan_pipeline/processing/pdt_parser.py`**
   - `PDTParser`: Main parser class with all extraction methods
   - PDF text extraction using PyMuPDF
   - Tokenization (whitespace-based)
   - Block detection with regex patterns
   - Hierarchy validation with scoring
   - Sequence verification with inversion counting
   - Section analysis with keyword matching
   - Table extraction for indicators and PPI

3. **`src/farfan_pipeline/processing/__init__.py`**
   - Updated to export new classes

### Test Suite

1. **`tests/processing/parsing_tests/test_pdt_structure.py`**
   - Unit tests for all dataclasses
   - Tests for field validation and defaults
   - Tests for to_dict() methods

2. **`tests/processing/parsing_tests/test_pdt_parser.py`**
   - Unit tests for all parser methods
   - Tokenization tests
   - Block detection tests
   - Hierarchy validation tests
   - Sequence verification tests
   - Section analysis tests
   - Table extraction tests

3. **`tests/processing/parsing_tests/test_pdt_parser_pdf.py`**
   - PDF extraction tests with mocking
   - Multi-page PDF handling
   - Error handling tests
   - End-to-end PDF parsing

4. **`tests/processing/parsing_tests/test_pdt_integration.py`**
   - Comprehensive integration tests
   - Realistic PDT content parsing
   - Cross-component validation
   - Data consistency checks

5. **`tests/processing/parsing_tests/example_usage.py`**
   - Example scripts demonstrating usage
   - Text parsing example
   - PDF parsing example
   - Structured data access example

6. **`tests/processing/parsing_tests/README.md`**
   - Documentation for test suite
   - Test running instructions
   - Implementation details

## Features Implemented

### Tokenization
- Split text on whitespace
- Count total tokens
- Simple and efficient implementation

### Block Detection
- Regex patterns for:
  - CAPÍTULO (chapters)
  - Línea estratégica (strategic lines)
  - Eje estratégico (strategic axes)
  - PROGRAMA (programs)
- Minimum thresholds:
  - MIN_BLOCK_TOKENS = 10
  - MIN_BLOCK_NUMBERS = 1
- Extract text spans for each block
- Count tokens and numbers per block

### Hierarchy Validation
- Extract headers with numbering (1, 1.1, 1.1.1, etc.)
- Validate numbering format
- Scoring system:
  - 1.0 if ≥80% valid headers
  - 0.5 if ≥50% valid headers
  - 0.0 otherwise

### Sequence Verification
- Track block order
- Count inversions vs expected sequence
- Expected order: CAPÍTULO → Eje estratégico → Línea estratégica → PROGRAMA
- Scoring system:
  - 1.0 if 0 inversions
  - 0.5 if 1 inversion
  - 0.0 if ≥2 inversions

### Section Analysis
- Four major sections:
  - Diagnóstico (diagnosis)
  - Estratégica (strategic)
  - PPI (pluriannual investment plan)
  - Seguimiento (monitoring/evaluation)
- Keyword matching for detection
- Extract section boundaries
- Count:
  - Tokens
  - Keyword matches
  - Numbers
  - Sources/references

### Table Extraction

#### Matriz de Indicadores (Indicator Matrix)
- Detect table header pattern
- Parse rows with columns:
  - Tipo (type)
  - Línea Estratégica
  - Programa
  - Nombre Indicador
  - Unidad de Medida
  - Línea Base
  - Meta Cuatrienio
  - Responsable

#### Plan Plurianual de Inversiones (PPI)
- Detect table header pattern
- Parse rows with columns:
  - Línea Estratégica
  - Programa
  - Subprograma
  - Proyecto
  - Costo Total
  - Vigencia 2024/2025/2026/2027
  - Fuente de Recursos

## API Usage

### Basic Text Parsing

```python
from farfan_pipeline.processing.pdt_parser import PDTParser

parser = PDTParser()
result = parser.parse_text(text)

print(f"Total tokens: {result.total_tokens}")
print(f"Blocks found: {len(result.blocks_found)}")
print(f"Hierarchy score: {result.hierarchy_score}")
print(f"Sequence score: {result.sequence_score}")
```

### PDF Parsing

```python
from farfan_pipeline.processing.pdt_parser import PDTParser

parser = PDTParser()
result = parser.parse_pdf("plan_desarrollo.pdf")

for section_name, section_info in result.sections_found.items():
    print(f"{section_name}: {section_info.present}")
```

### Accessing Structured Data

```python
# Access blocks
for block_name, block_info in result.blocks_found.items():
    print(f"{block_name}: {block_info.tokens} tokens")

# Access headers
for header in result.headers:
    print(f"Level {header.level}: {header.text}")

# Access indicator rows
for row in result.indicator_rows:
    print(row.to_dict())

# Access PPI rows
for row in result.ppi_rows:
    print(row.to_dict())
```

## Data Structure

### PDTStructure
```python
@dataclass
class PDTStructure:
    total_tokens: int
    full_text: str
    blocks_found: dict[str, BlockInfo]
    headers: list[HeaderInfo]
    block_sequence: list[str]
    sections_found: dict[str, SectionInfo]
    indicator_rows: list[IndicatorRow]
    ppi_rows: list[PPIRow]
    hierarchy_score: float
    sequence_score: float
```

## Testing

### Run All Tests
```bash
pytest tests/processing/parsing_tests/ -v
```

### Run Specific Test File
```bash
pytest tests/processing/parsing_tests/test_pdt_parser.py -v
```

### Run with Coverage
```bash
pytest tests/processing/parsing_tests/ -v \
  --cov=farfan_pipeline.processing.pdt_parser \
  --cov=farfan_pipeline.processing.pdt_structure
```

### Run Integration Tests
```bash
pytest tests/processing/parsing_tests/test_pdt_integration.py -v
```

## Implementation Details

### Regex Patterns

- **CAPÍTULO**: `CAPÍTULO\s+(\d+)[:\.]?\s*(.+?)(?=\n|$)`
- **Línea estratégica**: `Línea\s+estratégica\s+(\d+)[:\.]?\s*(.+?)(?=\n|$)`
- **Eje estratégico**: `Eje\s+estratégico\s+(\d+)[:\.]?\s*(.+?)(?=\n|$)`
- **PROGRAMA**: `PROGRAMA\s+(\d+)[:\.]?\s*(.+?)(?=\n|$)`
- **Numbering**: `^(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:\.(\d+))?\s+(.+?)$`

### Section Keywords

- **Diagnóstico**: diagnóstico, situación actual, problemática, análisis de contexto
- **Estratégica**: estratégica, estrategia, visión, objetivos estratégicos, líneas estratégicas
- **PPI**: plan plurianual, inversiones, presupuesto, financiación
- **Seguimiento**: seguimiento, evaluación, indicadores, monitoreo, medición

## Dependencies

- **PyMuPDF** (imported as `pymupdf` or `fitz`): PDF text extraction
- **Python 3.12+**: Type hints and dataclasses
- **pytest**: Testing framework

## Future Enhancements

1. **Advanced Table Extraction**: Use camelot-py or tabula-py for better table parsing
2. **OCR Support**: Handle scanned PDFs with OCR
3. **Machine Learning**: Train models for section detection
4. **Validation Rules**: Add business logic validation for extracted data
5. **Export Formats**: JSON, CSV, Excel export capabilities
6. **Multi-language**: Support for documents in other languages
7. **Visualization**: Generate structure diagrams and reports

## Notes

- Simple whitespace tokenization for efficiency
- Regex-based extraction for deterministic results
- Minimum thresholds prevent false positives
- Scoring systems provide quality metrics
- Table extraction is basic but extensible
- All tests are comprehensive and independent
- No external API dependencies
- Works with any PDT document structure

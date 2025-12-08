# PDT Parser Quick Start Guide

## Installation

The PDT parser is part of the farfan_pipeline package. Ensure you have the required dependencies:

```bash
pip install PyMuPDF  # For PDF parsing
```

## Basic Usage

### Parse Text

```python
from farfan_pipeline.processing.pdt_parser import PDTParser

# Create parser instance
parser = PDTParser()

# Parse text
text = """
CAPÍTULO 1: Introducción
Este es el contenido del plan con datos 1 2 3 4 5 6 7 8 9 10...
"""

result = parser.parse_text(text)

# Access results
print(f"Tokens: {result.total_tokens}")
print(f"Blocks: {len(result.blocks_found)}")
print(f"Sections: {result.sections_found}")
```

### Parse PDF

```python
from farfan_pipeline.processing.pdt_parser import PDTParser

parser = PDTParser()
result = parser.parse_pdf("plan_desarrollo.pdf")

# Check sections
for name, info in result.sections_found.items():
    if info.present:
        print(f"{name}: {info.token_count} tokens")
```

## Key Components

### PDTStructure
The main result object containing:
- `total_tokens`: Total word count
- `full_text`: Complete document text
- `blocks_found`: Dictionary of detected blocks
- `headers`: List of hierarchical headers
- `sections_found`: Dictionary of major sections
- `indicator_rows`: Indicator matrix data
- `ppi_rows`: Investment plan data
- `hierarchy_score`: Header validation score (0.0-1.0)
- `sequence_score`: Block order score (0.0-1.0)

### Block Detection
Automatically detects:
- CAPÍTULO (chapters)
- Línea estratégica (strategic lines)
- Eje estratégico (strategic axes)
- PROGRAMA (programs)

### Section Detection
Identifies four major sections:
- **Diagnóstico**: Situational analysis
- **Estratégica**: Strategic framework
- **PPI**: Investment plan
- **Seguimiento**: Monitoring system

## Examples

### Check Document Quality

```python
result = parser.parse_text(text)

if result.hierarchy_score >= 0.8:
    print("✓ Excellent header structure")
elif result.hierarchy_score >= 0.5:
    print("⚠ Acceptable header structure")
else:
    print("✗ Poor header structure")

if result.sequence_score == 1.0:
    print("✓ Perfect block sequence")
elif result.sequence_score == 0.5:
    print("⚠ One sequence inversion")
else:
    print("✗ Multiple sequence issues")
```

### Extract Tables

```python
result = parser.parse_text(text)

# Indicator matrix
print(f"Found {len(result.indicator_rows)} indicators")
for row in result.indicator_rows:
    data = row.to_dict()
    print(f"  {data['Nombre Indicador']}: {data['Meta Cuatrienio']}")

# Investment plan
print(f"Found {len(result.ppi_rows)} projects")
for row in result.ppi_rows:
    data = row.to_dict()
    print(f"  {data['Proyecto']}: ${data['Costo Total']}")
```

### Analyze Sections

```python
result = parser.parse_text(text)

for section_name in ["Diagnóstico", "Estratégica", "PPI", "Seguimiento"]:
    section = result.sections_found[section_name]
    
    if section.present:
        print(f"\n{section_name}:")
        print(f"  Tokens: {section.token_count}")
        print(f"  Keywords: {section.keyword_matches}")
        print(f"  Sources: {section.sources_found}")
    else:
        print(f"\n{section_name}: Not found")
```

### Iterate Blocks

```python
result = parser.parse_text(text)

for block_name in result.block_sequence:
    block = result.blocks_found[block_name]
    print(f"\n{block_name}:")
    print(f"  Tokens: {block.tokens}")
    print(f"  Numbers: {block.numbers_count}")
    print(f"  Preview: {block.text[:100]}...")
```

## Running Tests

```bash
# All tests
pytest tests/processing/parsing_tests/ -v

# Specific test file
pytest tests/processing/parsing_tests/test_pdt_parser.py -v

# With coverage
pytest tests/processing/parsing_tests/ --cov

# Integration tests only
pytest tests/processing/parsing_tests/test_pdt_integration.py -v
```

## Example Script

Run the example usage script:

```bash
python tests/processing/parsing_tests/example_usage.py
```

## Common Use Cases

### 1. Document Completeness Check
```python
parser = PDTParser()
result = parser.parse_pdf("pdt.pdf")

required_sections = ["Diagnóstico", "Estratégica", "PPI", "Seguimiento"]
missing = [s for s in required_sections if not result.sections_found[s].present]

if missing:
    print(f"Missing sections: {', '.join(missing)}")
else:
    print("All required sections present ✓")
```

### 2. Extract All Indicators
```python
result = parser.parse_text(text)

indicators = []
for row in result.indicator_rows:
    indicators.append({
        'name': row.nombre_indicador,
        'baseline': row.linea_base,
        'target': row.meta_cuatrienio,
        'unit': row.unidad_medida,
    })
```

### 3. Budget Summary
```python
result = parser.parse_text(text)

total_budget = 0
for row in result.ppi_rows:
    try:
        cost = float(row.costo_total.replace(',', ''))
        total_budget += cost
    except ValueError:
        pass

print(f"Total budget: ${total_budget:,.0f}")
```

## Tips

1. **Large PDFs**: For very large PDFs, consider processing in chunks
2. **Table Quality**: Table extraction works best with well-formatted text
3. **Validation**: Always check `hierarchy_score` and `sequence_score` for quality
4. **Keywords**: Sections are detected by keywords; ensure they match your document
5. **Thresholds**: Adjust `MIN_BLOCK_TOKENS` and `MIN_BLOCK_NUMBERS` if needed

## Troubleshooting

### No blocks detected
- Check if text contains expected patterns (CAPÍTULO, Línea estratégica, etc.)
- Verify minimum thresholds are met (10 tokens, 1 number)

### No sections found
- Check if section keywords match your document
- Verify text is properly extracted from PDF

### Empty indicator/PPI rows
- Check if table header patterns are present in text
- Verify table formatting is consistent

### Low hierarchy score
- Inspect headers with `result.headers`
- Check for non-standard numbering formats

## Support

For issues or questions:
1. Check test files for examples
2. Review README.md for detailed documentation
3. Run example_usage.py for demonstrations

"""
Example usage of PDT parser.

This script demonstrates how to use the PDT parser to extract
structured information from Plan de Desarrollo Territorial documents.
"""

from pathlib import Path
from farfan_pipeline.processing.pdt_parser import PDTParser


def example_parse_text():
    """Example: Parse PDT text directly."""
    
    sample_text = """
    CAPÍTULO 1: Introducción al Plan
    
    Este documento presenta el Plan de Desarrollo Territorial 2024-2027
    con objetivos estratégicos y metas cuantificables para el municipio.
    Presupuesto total: 50.000 millones de pesos distribuidos en líneas
    estratégicas de educación, salud, desarrollo y ambiente con proyectos
    prioritarios para 45.000 habitantes del territorio municipal 1 2 3 4 5 6 7 8 9 10.
    
    1 Diagnóstico Territorial
    1.1 Situación actual
    
    El diagnóstico identifica problemáticas mediante análisis de contexto
    con datos demográficos, económicos y sociales según fuentes [1] [2].
    Población 45.000 habitantes, cobertura educación 85%, salud 87%.
    
    2 Parte Estratégica
    2.1 Visión municipal
    
    Ser un municipio próspero y sostenible con desarrollo humano integral.
    Los objetivos estratégicos se organizan en líneas estratégicas con
    programas y proyectos para cumplir metas del plan de desarrollo.
    
    Línea estratégica 1: Educación de calidad
    
    Garantizar acceso a educación mediante infraestructura y recursos
    pedagógicos. Meta: incrementar cobertura de 85% a 95% en cuatrienio
    con inversión de 15.000 millones distribuidos en cuatro vigencias.
    
    3 Plan Plurianual de Inversiones
    
    Plan Plurianual de Inversiones
    
    Educación  Infraestructura  Construcción  Escuelas  8000  2000  2000  2000  2000  SGP
    Salud      Atención         Hospitales    Dotación  6000  1500  1500  1500  1500  Regalías
    
    4 Sistema de Seguimiento
    
    Matriz de Indicadores
    
    Resultado  Educación  Calidad  Cobertura  %  85  95  Secretaría
    Resultado  Salud      Atención  Afiliación  %  87  97  Secretaría
    """
    
    parser = PDTParser()
    result = parser.parse_text(sample_text)
    
    print("PDT Parsing Results")
    print("=" * 60)
    print(f"Total tokens: {result.total_tokens}")
    print(f"Blocks found: {len(result.blocks_found)}")
    print(f"Headers extracted: {len(result.headers)}")
    print(f"Hierarchy score: {result.hierarchy_score}")
    print(f"Sequence score: {result.sequence_score}")
    print()
    
    print("Sections Analysis:")
    print("-" * 60)
    for section_name, section_info in result.sections_found.items():
        print(f"{section_name}:")
        print(f"  Present: {section_info.present}")
        print(f"  Tokens: {section_info.token_count}")
        print(f"  Keywords: {section_info.keyword_matches}")
        print(f"  Sources: {section_info.sources_found}")
    print()
    
    print("Blocks Detected:")
    print("-" * 60)
    for block_name, block_info in result.blocks_found.items():
        print(f"{block_name}:")
        print(f"  Tokens: {block_info.tokens}")
        print(f"  Numbers: {block_info.numbers_count}")
        print(f"  Text preview: {block_info.text[:80]}...")
    print()
    
    print(f"Indicator rows: {len(result.indicator_rows)}")
    print(f"PPI rows: {len(result.ppi_rows)}")


def example_parse_pdf():
    """Example: Parse PDT from PDF file."""
    
    pdf_path = "sample_pdt.pdf"
    
    if not Path(pdf_path).exists():
        print(f"PDF file not found: {pdf_path}")
        print("Skipping PDF parsing example.")
        return
    
    parser = PDTParser()
    
    try:
        result = parser.parse_pdf(pdf_path)
        
        print(f"Successfully parsed PDF: {pdf_path}")
        print(f"Total tokens: {result.total_tokens}")
        print(f"Document length: {len(result.full_text)} characters")
        print(f"Blocks found: {len(result.blocks_found)}")
        print(f"Headers: {len(result.headers)}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error parsing PDF: {e}")


def example_access_structured_data():
    """Example: Access structured data from parsing results."""
    
    sample_text = """
    Matriz de Indicadores
    
    Resultado  Educación  Calidad  Tasa de cobertura  %  85  95  Secretaría Educación
    Producto   Salud      Atención  Consultas médicas  Número  1000  1500  Secretaría Salud
    """
    
    parser = PDTParser()
    result = parser.parse_text(sample_text)
    
    print("Indicator Rows:")
    print("-" * 60)
    for i, row in enumerate(result.indicator_rows, 1):
        print(f"Row {i}:")
        row_dict = row.to_dict()
        for key, value in row_dict.items():
            if value:
                print(f"  {key}: {value}")
    
    print("\nPPI Rows:")
    print("-" * 60)
    for i, row in enumerate(result.ppi_rows, 1):
        print(f"Row {i}:")
        row_dict = row.to_dict()
        for key, value in row_dict.items():
            if value:
                print(f"  {key}: {value}")


if __name__ == "__main__":
    print("PDT Parser Examples")
    print("=" * 60)
    print()
    
    print("Example 1: Parse text directly")
    print("-" * 60)
    example_parse_text()
    print()
    
    print("Example 2: Parse PDF file")
    print("-" * 60)
    example_parse_pdf()
    print()
    
    print("Example 3: Access structured data")
    print("-" * 60)
    example_access_structured_data()

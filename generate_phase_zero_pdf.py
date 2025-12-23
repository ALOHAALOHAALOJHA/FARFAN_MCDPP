#!/usr/bin/env python3
"""
Script para generar un PDF con el contenido de todos los archivos Python
de la carpeta Phase_zero.
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
from datetime import datetime

def escape_xml(text: str) -> str:
    """Escapa caracteres XML especiales."""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def create_phase_zero_pdf():
    phase_zero_dir = Path(__file__).parent / "src" / "farfan_pipeline" / "phases" / "Phase_zero"
    output_pdf = Path(__file__).parent / "Phase_zero_source_code.pdf"
    
    # Obtener todos los archivos .py (excluyendo __pycache__)
    py_files = sorted([
        f for f in phase_zero_dir.glob("*.py")
        if f.is_file() and "__pycache__" not in str(f)
    ])
    
    print(f"Encontrados {len(py_files)} archivos Python en Phase_zero")
    
    # Crear documento PDF
    doc = SimpleDocTemplate(
        str(output_pdf),
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_LEFT,
        textColor=colors.darkblue
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=20,
        textColor=colors.grey
    )
    
    file_header_style = ParagraphStyle(
        'FileHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=20,
        spaceAfter=10,
        textColor=colors.darkgreen,
        backColor=colors.lightgrey
    )
    
    code_style = ParagraphStyle(
        'Code',
        parent=styles['Code'],
        fontSize=7,
        fontName='Courier',
        leading=9,
        leftIndent=0,
        rightIndent=0,
        spaceAfter=10
    )
    
    # Construir contenido
    story = []
    
    # Portada
    story.append(Paragraph("F.A.R.F.A.N Pipeline", title_style))
    story.append(Paragraph("Phase Zero - Source Code", styles['Heading2']))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))
    story.append(Paragraph(f"Total de archivos: {len(py_files)}", subtitle_style))
    story.append(Spacer(1, 20))
    
    # Índice de archivos
    story.append(Paragraph("Índice de Archivos:", styles['Heading3']))
    for i, py_file in enumerate(py_files, 1):
        story.append(Paragraph(f"{i}. {py_file.name}", styles['Normal']))
    
    story.append(PageBreak())
    
    # Contenido de cada archivo
    for py_file in py_files:
        print(f"Procesando: {py_file.name}")
        
        # Header del archivo
        story.append(Paragraph(f"📄 {py_file.name}", file_header_style))
        
        try:
            content = py_file.read_text(encoding='utf-8')
            # Escapar caracteres especiales XML
            escaped_content = escape_xml(content)
            
            # Dividir en líneas para mejor formato
            lines = escaped_content.split('\n')
            
            # Añadir números de línea y formatear
            formatted_lines = []
            for i, line in enumerate(lines, 1):
                # Limitar longitud de línea para evitar overflow
                if len(line) > 100:
                    line = line[:97] + "..."
                formatted_lines.append(f"{i:4d} | {line}")
            
            formatted_content = '\n'.join(formatted_lines)
            
            # Usar Preformatted para código
            story.append(Preformatted(formatted_content, code_style))
            
        except Exception as e:
            story.append(Paragraph(f"Error leyendo archivo: {str(e)}", styles['Normal']))
        
        story.append(PageBreak())
    
    # Generar PDF
    print(f"\nGenerando PDF: {output_pdf}")
    doc.build(story)
    print(f"✅ PDF generado exitosamente: {output_pdf}")
    
    return output_pdf

if __name__ == "__main__":
    create_phase_zero_pdf()

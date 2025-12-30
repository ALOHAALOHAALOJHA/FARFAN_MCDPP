import os
from fpdf import FPDF
import math


def _safe_latin1(text: str) -> str:
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _write_wrapped(pdf: FPDF, text: str, line_height: float = 5) -> None:
    pdf.set_x(pdf.l_margin)
    width = pdf.w - pdf.l_margin - pdf.r_margin
    if width <= 0:
        width = 100
    pdf.multi_cell(width, line_height, _safe_latin1(text))

# 1. Leer la lista de archivos .py generada
with open('all_py_files.txt', 'r', encoding='utf-8') as f:
    py_files = [line.strip() for line in f if line.strip()]

py_files.sort()  # Ordena para consistencia

# 2. Divide en 30 grupos lo más equitativos posible
n_groups = 30
group_size = math.ceil(len(py_files) / n_groups)
groups = [py_files[i*group_size:(i+1)*group_size] for i in range(n_groups)]

# 3. Exporta cada grupo a un PDF
for idx, group in enumerate(groups):
    if not group:
        continue
    pdf = FPDF()
    pdf.set_margins(10, 10, 10)
    pdf.set_auto_page_break(auto=True, margin=15)
    for file_path in group:
        pdf.add_page()
        pdf.set_font("Courier", size=10)
        pdf.cell(0, 10, _safe_latin1(os.path.relpath(file_path, '.')), ln=True)
        pdf.ln(2)
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    _write_wrapped(pdf, line.rstrip(), line_height=5)
        except Exception as e:
            _write_wrapped(pdf, f"[ERROR LEYENDO {file_path}: {e}]", line_height=5)
    pdf.output(f"python_sources_part_{idx+1:02d}.pdf")

print("¡Conversión completada! Archivos PDF generados como python_sources_part_XX.pdf")

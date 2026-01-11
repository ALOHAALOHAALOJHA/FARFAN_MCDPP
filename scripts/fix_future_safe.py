#!/usr/bin/env python3
"""Mueve 'from __future__ import annotations' justo después del docstring. 

Versión auditada y corregida.

Uso:
    # Dry-run usando el reporte JSON (recomendado)
    python3 scripts/fix_future_safe.py

    # Aplicar cambios
    python3 scripts/fix_future_safe.py --apply

    # Si quieres escanear todo src/ en vez del reporte: 
    python3 scripts/fix_future_safe.py --all

    # Verificar cambios
    git diff --stat
    git diff  # ver cambios detallados
"""

import json
import sys
from pathlib import Path

DOC_QUOTES = ('"""', "'''")


def find_docstring_end(lines: list[str]) -> int | None:
    """Encuentra el índice de la línea donde termina el docstring inicial.
    
    Retorna None si no hay docstring válido al inicio. 
    """
    if not lines:
        return None
    
    first_stripped = lines[0].lstrip()
    
    # Detectar qué tipo de comillas usa
    quote = None
    for q in DOC_QUOTES:
        if first_stripped.startswith(q):
            quote = q
            break
    
    if quote is None:
        return None
    
    # Caso: docstring de una sola línea (abre y cierra en la misma)
    # Buscar el cierre después de la apertura
    after_open = first_stripped[len(quote):]
    if quote in after_open:
        return 0
    
    # Caso: docstring multi-línea - buscar línea que termine con las comillas
    for i in range(1, len(lines)):
        if lines[i].rstrip().endswith(quote):
            return i
    
    return None


def has_executable_code_between(lines: list[str], start: int, end: int) -> bool:
    """Detecta si hay código ejecutable (no comentarios ni vacías) entre start y end."""
    for i in range(start + 1, end):
        stripped = lines[i].strip()
        if not stripped:
            continue
        if stripped.startswith('#'):
            continue
        # Cualquier otra cosa es código ejecutable
        return True
    return False


def fix_file(filepath: Path, dry_run: bool = True) -> bool:
    """Corrige la posición del 'from __future__ import annotations' en un archivo. 
    
    Retorna True si se hizo (o haría) un cambio.
    """
    content = filepath.read_text(encoding='utf-8')
    lines = content.splitlines(keepends=True)
    
    # Buscar la línea con 'from __future__ import annotations'
    future_idx = None
    for i, line in enumerate(lines):
        if line.strip() == 'from __future__ import annotations':
            future_idx = i
            break
    
    if future_idx is None: 
        return False  # No tiene el import
    
    # Encontrar fin del docstring
    docstring_end = find_docstring_end(lines)
    
    if docstring_end is None:
        return False  # No hay docstring, no modificar
    
    # Si ya está justo después del docstring, no hacer nada
    # (puede estar en docstring_end + 1, o +2 si hay una línea vacía)
    if future_idx <= docstring_end + 1:
        return False
    
    # Solo mover si hay código ejecutable entre el docstring y el import
    if not has_executable_code_between(lines, docstring_end, future_idx):
        return False
    
    # Guardar índice original para el reporte
    original_future_idx = future_idx
    
    if dry_run:
        print(f"[DRY-RUN] {filepath}: mover L{original_future_idx + 1} → L{docstring_end + 2}")
        return True
    
    # Extraer la línea del import
    future_line = lines.pop(future_idx)
    
    # Eliminar líneas vacías que quedaron antes (máximo 3)
    removed = 0
    while future_idx > 0 and removed < 3:
        check_idx = future_idx - 1
        if check_idx < len(lines) and lines[check_idx].strip() == '':
            lines.pop(check_idx)
            future_idx -= 1
            removed += 1
        else:
            break
    
    # Insertar justo después del docstring
    insert_pos = docstring_end + 1
    lines.insert(insert_pos, future_line)
    
    # Guardar archivo
    filepath.write_text(''.join(lines), encoding='utf-8')
    print(f"[FIXED] {filepath}")
    return True


def load_violation_files(report_path: Path) -> list[Path]:
    """Carga la lista de archivos con violaciones desde el reporte JSON."""
    if not report_path.exists():
        return []
    
    with open(report_path, encoding='utf-8') as f:
        data = json.load(f)
    
    return [Path(v['file']) for v in data.get('violations', [])]


def main():
    dry_run = '--apply' not in sys.argv
    use_report = '--all' not in sys.argv
    
    print("=" * 70)
    print("FIX FUTURE IMPORTS - VERSIÓN SEGURA")
    print("=" * 70)
    print(f"Modo: {'DRY-RUN (usa --apply para ejecutar)' if dry_run else 'APLICAR CAMBIOS'}")
    print(f"Fuente: {'Reporte JSON (usa --all para escanear todo src/)' if use_report else 'Todos los .py en src/'}")
    print("=" * 70 + "\n")
    
    # Obtener lista de archivos a procesar
    report_path = Path('artifacts/future_violations_report_v3.json')
    
    if use_report and report_path.exists():
        files = load_violation_files(report_path)
        print(f"Archivos en reporte: {len(files)}\n")
    else:
        files = sorted(Path('src').rglob('*.py'))
        print(f"Archivos en src/: {len(files)}\n")
    
    # Procesar archivos
    fixed = 0
    errors = []
    
    for filepath in files:
        if not filepath.exists():
            errors.append(f"No existe: {filepath}")
            continue
        try:
            if fix_file(filepath, dry_run=dry_run):
                fixed += 1
        except Exception as e:
            errors.append(f"{filepath}: {e}")
    
    # Resumen
    print(f"\n{'=' * 70}")
    print(f"{'Archivos a corregir' if dry_run else 'Archivos corregidos'}: {fixed}")
    
    if errors:
        print(f"\nErrores ({len(errors)}):")
        for err in errors:
            print(f"  - {err}")
    
    # Validación de sintaxis (solo si se aplicaron cambios)
    if not dry_run and fixed > 0:
        print("\nValidando sintaxis...")
        import py_compile
        syntax_errors = 0
        
        for filepath in files:
            if filepath.exists():
                try:
                    py_compile.compile(str(filepath), doraise=True)
                except py_compile.PyCompileError as e:
                    print(f"  ERROR: {e}")
                    syntax_errors += 1
        
        if syntax_errors == 0:
            print("✓ Todos los archivos compilan correctamente")
        else:
            print(f"✗ {syntax_errors} errores de sintaxis")
            sys.exit(1)
    
    print("=" * 70)


if __name__ == '__main__':
    main()

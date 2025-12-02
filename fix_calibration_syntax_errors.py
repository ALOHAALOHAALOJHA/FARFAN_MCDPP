#!/usr/bin/env python3
"""
Script de corrección automática para errores de sintaxis del sistema de calibración.

Corrige 8 archivos con errores de sintaxis causados por el sistema de auto-calibración mal implementado.
"""
import re
from pathlib import Path

# Definición de correcciones específicas
FIXES = [
    {
        'file': 'src/farfan_pipeline/analysis/Analyzer_one.py',
        'line': 538,
        'pattern': r'target_throughput = 5get_parameter_loader\(\)\.get\([^)]+\)\.get\([^)]+\)',
        'replacement': 'target_throughput = 5.0  # Target throughput in requests/sec',
        'description': 'Throughput target for performance analysis'
    },
    {
        'file': 'src/farfan_pipeline/analysis/bayesian_multilevel_system.py',
        'line': 253,
        'pattern': r'return 1get_parameter_loader\(\)\.get\([^)]+\)\.get\([^)]+\) if test_passed else get_parameter_loader\(\)\.get\([^)]+\)\.get\([^)]+\)',
        'replacement': 'return 10.0 if test_passed else 0.9  # Smoking Gun: strong evidence if passed',
        'description': 'Likelihood ratio for Smoking Gun test'
    },
    {
        'file': 'src/farfan_pipeline/analysis/bayesian_multilevel_system.py',
        'line': 255,
        'pattern': r'return 2get_parameter_loader\(\)\.get\([^)]+\)\.get\([^)]+\) if test_passed else get_parameter_loader\(\)\.get\([^)]+\)\.get\([^)]+\)',
        'replacement': 'return 20.0 if test_passed else 0.05  # Doubly Decisive: very strong evidence',
        'description': 'Likelihood ratio for Doubly Decisive test'
    },
    {
        'file': 'src/farfan_pipeline/analysis/financiero_viabilidad_tablas.py',
        'line': 1727,
        'pattern': r', 1get_parameter_loader\(\)\.get\([^)]+\)\.get\([^)]+\)\)',
        'replacement': ', 1.0)  # Max score ceiling',
        'description': 'Financial score normalization ceiling'
    },
    {
        'file': 'src/farfan_pipeline/analysis/micro_prompts.py',
        'line': 124,
        'pattern': r'p95_latency_threshold or 100get_parameter_loader\(\)\.get\([^)]+\)\.get\([^)]+\)',
        'replacement': 'p95_latency_threshold or 1000  # Default 1 second in milliseconds',
        'description': 'P95 latency threshold (1 second = 1000ms)'
    },
    {
        'file': 'src/farfan_pipeline/analysis/teoria_cambio.py',
        'line': 924,
        'pattern': r'success_rate >= 9get_parameter_loader\(\)\.get\([^)]+\)\.get\([^)]+\)',
        'replacement': 'success_rate >= 0.9  # 90% success rate required for certification',
        'description': 'Industrial grade validation threshold'
    },
    {
        'file': 'src/farfan_pipeline/processing/embedding_policy.py',
        'line': 1474,
        'pattern': r'value / 10get_parameter_loader\(\)\.get\([^)]+\)\.get\([^)]+\)',
        'replacement': 'value / 100.0  # Convert percentage to decimal (0-1 scale)',
        'description': 'Percentage normalization'
    },
    {
        'file': 'src/farfan_pipeline/utils/enhanced_contracts.py',
        'line': 151,
        'pattern': r'default="2\.get_parameter_loader\(\)\.get\([^)]+\)\.get\([^)]+\)",',
        'replacement': 'default="2.0.0",  # Semantic versioning',
        'description': 'Contract schema version'
    },
]

# Correcciones estructurales
STRUCTURAL_FIXES = [
    {
        'file': 'src/farfan_pipeline/core/orchestrator/chunk_router.py',
        'action': 'move_future_import',
        'description': 'Move __future__ import to top of file'
    },
    {
        'file': 'src/farfan_pipeline/processing/converter.py',
        'action': 'fix_import_block',
        'description': 'Fix malformed import block'
    },
]

def apply_regex_fix(filepath: Path, pattern: str, replacement: str, description: str) -> bool:
    """Apply a regex-based fix to a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        content = re.sub(pattern, replacement, content)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ {filepath}: {description}")
            return True
        else:
            print(f"⚠ {filepath}: Pattern not found")
            return False
    except Exception as e:
        print(f"✗ {filepath}: Error - {e}")
        return False

def fix_chunk_router():
    """Fix __future__ import position in chunk_router.py"""
    filepath = Path('src/farfan_pipeline/core/orchestrator/chunk_router.py')
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find and remove the __future__ import
        future_line = None
        new_lines = []
        for line in lines:
            if 'from __future__ import annotations' in line:
                future_line = line
            else:
                new_lines.append(line)
        
        # Insert at the beginning (after shebang/docstring if present)
        insert_pos = 0
        if new_lines[0].startswith('#!'):
            insert_pos = 1
        if new_lines[insert_pos].startswith('"""'):
            # Find end of docstring
            for i in range(insert_pos + 1, len(new_lines)):
                if '"""' in new_lines[i]:
                    insert_pos = i + 1
                    break
        
        new_lines.insert(insert_pos, future_line)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print(f"✓ {filepath}: Moved __future__ import to top")
        return True
    except Exception as e:
        print(f"✗ {filepath}: Error - {e}")
        return False

def fix_converter_imports():
    """Fix malformed import block in converter.py"""
    filepath = Path('src/farfan_pipeline/processing/converter.py')
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix the import block
        bad_block = """from farfan_pipeline.processing.cpp_ingestion.models import (
# from farfan_core import get_parameter_loader  # CALIBRATION DISABLED
from farfan_pipeline.core.calibration.decorators import calibrated_method
    KPI,"""
        
        good_block = """# from farfan_core import get_parameter_loader  # CALIBRATION DISABLED
from farfan_pipeline.core.calibration.decorators import calibrated_method

from farfan_pipeline.processing.cpp_ingestion.models import (
    KPI,"""
        
        content = content.replace(bad_block, good_block)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ {filepath}: Fixed import block structure")
        return True
    except Exception as e:
        print(f"✗ {filepath}: Error - {e}")
        return False

def main():
    """Main execution."""
    print("=" * 80)
    print("CORRECCIÓN DE ERRORES DE SINTAXIS DEL SISTEMA DE CALIBRACIÓN")
    print("=" * 80)
    print()
    
    success_count = 0
    fail_count = 0
    
    # Apply regex-based fixes
    print("Aplicando correcciones regex...")
    print("-" * 80)
    for fix in FIXES:
        filepath = Path(fix['file'])
        if filepath.exists():
            if apply_regex_fix(filepath, fix['pattern'], fix['replacement'], fix['description']):
                success_count += 1
            else:
                fail_count += 1
        else:
            print(f"✗ {filepath}: File not found")
            fail_count += 1
    
    print()
    print("Aplicando correcciones estructurales...")
    print("-" * 80)
    
    # Fix chunk_router.py
    if fix_chunk_router():
        success_count += 1
    else:
        fail_count += 1
    
    # Fix converter.py
    if fix_converter_imports():
        success_count += 1
    else:
        fail_count += 1
    
    print()
    print("=" * 80)
    print(f"RESUMEN: {success_count} correcciones exitosas, {fail_count} fallidas")
    print("=" * 80)
    
    if fail_count == 0:
        print("\n✓✓✓ Todos los errores de sintaxis han sido corregidos ✓✓✓")
        return 0
    else:
        print(f"\n⚠ {fail_count} correcciones fallaron - revisar manualmente")
        return 1

if __name__ == "__main__":
    exit(main())

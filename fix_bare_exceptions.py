#!/usr/bin/env python3
"""
Script to fix bare exception handlers by adding logging.
"""
import re
import sys
from pathlib import Path

def fix_file(file_path: Path) -> int:
    """Fix bare exception handlers in a file. Returns number of fixes."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    fixes = 0

    # Pattern 1: except Exception: followed by return/continue (no pass)
    # We want to add logging before the return/continue
    pattern1 = re.compile(
        r'(\s+)except Exception:\n'
        r'(\s+)(return|continue)',
        re.MULTILINE
    )

    def replace1(match):
        indent = match.group(1)
        action_indent = match.group(2)
        action = match.group(3)
        return f'{indent}except Exception as e:\n{action_indent}logger.debug(f"Exception in operation: {{str(e)}}")\n{action_indent}{action}'

    content, n1 = pattern1.subn(replace1, content)
    fixes += n1

    # Pattern 2: except Exception: followed by pass
    pattern2 = re.compile(
        r'(\s+)except Exception:\n'
        r'(\s+)pass',
        re.MULTILINE
    )

    def replace2(match):
        indent = match.group(1)
        action_indent = match.group(2)
        return f'{indent}except Exception as e:\n{action_indent}logger.debug(f"Exception silenced: {{str(e)}}")'

    content, n2 = pattern2.subn(replace2, content)
    fixes += n2

    # Pattern 3: bare except: (catches everything including KeyboardInterrupt)
    pattern3 = re.compile(
        r'(\s+)except:\n'
        r'(\s+)(pass|return|continue)',
        re.MULTILINE
    )

    def replace3(match):
        indent = match.group(1)
        action_indent = match.group(2)
        action = match.group(3)
        if action == 'pass':
            return f'{indent}except Exception as e:\n{action_indent}logger.debug(f"Exception silenced: {{str(e)}}")'
        else:
            return f'{indent}except Exception as e:\n{action_indent}logger.debug(f"Exception in operation: {{str(e)}}")\n{action_indent}{action}'

    content, n3 = pattern3.subn(replace3, content)
    fixes += n3

    if fixes > 0:
        # Check if logger is imported
        if 'import logging' not in content and 'from logging import' not in content:
            # Add logger import after other imports
            import_match = re.search(r'^(import .*\n|from .* import .*\n)+', content, re.MULTILINE)
            if import_match:
                insert_pos = import_match.end()
                content = content[:insert_pos] + '\nimport logging\nlogger = logging.getLogger(__name__)\n' + content[insert_pos:]
            else:
                # Add at the beginning after docstring
                docstring_match = re.search(r'^""".*?"""', content, re.DOTALL)
                if docstring_match:
                    insert_pos = docstring_match.end() + 1
                else:
                    insert_pos = 0
                content = content[:insert_pos] + '\nimport logging\nlogger = logging.getLogger(__name__)\n' + content[insert_pos:]

        # Check if logger is defined
        if 'logger = logging.getLogger' not in content and 'logger = ' not in content:
            # Add logger definition after imports
            import_match = re.search(r'^(import .*\n|from .* import .*\n)+', content, re.MULTILINE)
            if import_match:
                insert_pos = import_match.end()
                content = content[:insert_pos] + '\nlogger = logging.getLogger(__name__)\n' + content[insert_pos:]

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    return fixes

def main():
    production_files = [
        'src/farfan_pipeline/methods/derek_beach.py',
        'src/farfan_pipeline/orchestration/orchestrator.py',
        'src/farfan_pipeline/phases/Phase_01/phase1_13_00_cpp_ingestion.py',
        'src/farfan_pipeline/phases/Phase_02/phase2_60_00_base_executor_with_contract.py',
        'src/farfan_pipeline/methods/teoria_cambio.py',
        'src/farfan_pipeline/methods/financiero_viabilidad_tablas.py',
        'src/farfan_pipeline/phases/Phase_00/phase0_50_01_exit_gates.py',
        'src/farfan_pipeline/phases/Phase_01/phase1_09_00_circuit_breaker.py',
        'src/farfan_pipeline/phases/Phase_02/phase2_90_00_carver.py',
        'canonic_questionnaire_central/resolver.py',
        'src/farfan_pipeline/infrastructure/contractual/dura_lex/context_immutability.py',
        'src/farfan_pipeline/methods/policy_processor.py',
        'src/farfan_pipeline/phases/Phase_00/phase0_90_01_verified_pipeline_runner.py',
    ]

    total_fixes = 0
    for file_rel in production_files:
        file_path = Path(file_rel)
        if not file_path.exists():
            print(f"⚠️  {file_rel} not found")
            continue

        fixes = fix_file(file_path)
        if fixes > 0:
            print(f"✓ {file_rel}: {fixes} fixes")
            total_fixes += fixes
        else:
            print(f"  {file_rel}: no changes needed")

    print(f"\nTotal fixes: {total_fixes}")
    return 0 if total_fixes == 0 else 0

if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""
Add technical debt pragmas to HIGH complexity functions.

This script automatically adds technical debt documentation to function docstrings
for all functions documented in TECHNICAL_DEBT_REGISTER.md.
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Load audit report to get HIGH complexity functions
AUDIT_REPORT = "audit_report_20260129_045427.json"

def load_high_complexity_functions() -> List[Dict]:
    """Load all HIGH complexity functions from audit report."""
    with open(AUDIT_REPORT) as f:
        data = json.load(f)

    high_complexity = [
        issue for issue in data.get('issues', [])
        if (issue.get('severity') == 'HIGH' and
            issue.get('category') == 'COMPLEXITY' and
            'src/farfan_pipeline' in issue.get('file', ''))
    ]

    return high_complexity


def extract_function_info(description: str) -> Tuple[str, int]:
    """Extract function name and complexity from description."""
    # Description format: "Function 'func_name' has high cyclomatic complexity: 30"
    parts = description.split("'")
    if len(parts) >= 2:
        func_name = parts[1]
        complexity = int(description.split(': ')[-1])
        return func_name, complexity
    return "", 0


def add_pragma_to_function(file_path: str, func_name: str, complexity: int) -> bool:
    """Add technical debt pragma to a function's docstring."""
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        return False

    content = path.read_text()
    tree = ast.parse(content, filename=str(path))

    # Find the function
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == func_name:
                # Check if pragma already exists
                docstring = ast.get_docstring(node)
                if docstring and ('TECHNICAL_DEBT_REGISTER' in docstring or
                                   'Technical Debt:' in docstring):
                    print(f"  Pragma already exists for {func_name}")
                    return True

                # Add pragma to docstring
                if docstring:
                    # Find the docstring in the file content
                    lines = content.split('\n')
                    func_line = node.lineno - 1

                    # Find docstring end
                    in_docstring = False
                    docstring_start = None
                    docstring_end = None
                    quote_style = None

                    for i in range(func_line, min(func_line + 50, len(lines))):
                        line = lines[i].strip()

                        if not in_docstring:
                            if '"""' in line or "'''" in line:
                                quote_style = '"""' if '"""' in line else "'''"
                                in_docstring = True
                                docstring_start = i
                                # Check if single-line docstring
                                if line.count(quote_style) >= 2:
                                    docstring_end = i
                                    break
                        else:
                            if quote_style in line:
                                docstring_end = i
                                break

                    if docstring_start is not None and docstring_end is not None:
                        # Add pragma before closing quotes
                        pragma_text = f"\n        Technical Debt: Registered in TECHNICAL_DEBT_REGISTER.md\n        Complexity: {complexity} - Refactoring scheduled Q2-Q3 2026"

                        # Insert pragma
                        indent = "        "  # Adjust based on file
                        if docstring_end == docstring_start:
                            # Single-line docstring - convert to multi-line
                            original_line = lines[docstring_start]
                            close_idx = original_line.rfind(quote_style)
                            new_line = original_line[:close_idx] + pragma_text + "\n" + indent + quote_style
                            lines[docstring_start] = new_line
                        else:
                            # Multi-line docstring - add before closing quotes
                            close_line = lines[docstring_end]
                            close_idx = close_line.find(quote_style)
                            indent_match = close_line[:close_idx]
                            new_line = indent_match + pragma_text + "\n" + close_line
                            lines[docstring_end] = new_line

                        # Write back
                        path.write_text('\n'.join(lines))
                        print(f"  ✓ Added pragma to {func_name} (complexity {complexity})")
                        return True
                else:
                    print(f"  No docstring found for {func_name}")
                    return False

    print(f"  Function {func_name} not found in {file_path}")
    return False


def main():
    """Main function."""
    print("=" * 70)
    print("Adding Technical Debt Pragmas to HIGH Complexity Functions")
    print("=" * 70)
    print()

    # Load HIGH complexity functions
    high_functions = load_high_complexity_functions()
    print(f"Found {len(high_functions)} HIGH complexity functions in production code\n")

    success_count = 0
    for issue in high_functions:
        file_path = issue['file']
        description = issue['description']
        func_name, complexity = extract_function_info(description)

        if func_name:
            print(f"Processing: {func_name} ({Path(file_path).name})")
            if add_pragma_to_function(file_path, func_name, complexity):
                success_count += 1
        print()

    print("=" * 70)
    print(f"Summary: {success_count}/{len(high_functions)} pragmas added successfully")
    print("=" * 70)


if __name__ == "__main__":
    main()

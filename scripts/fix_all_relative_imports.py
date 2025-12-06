#!/usr/bin/env python3
"""Automatically convert all relative imports to absolute imports in farfan_pipeline."""

import re
import sys
from pathlib import Path


def get_package_from_file(file_path: Path, src_dir: Path) -> str:
    """Get the package name from a file path.
    
    E.g., src/farfan_pipeline/core/types.py -> farfan_pipeline.core
          src/farfan_pipeline/core/__init__.py -> farfan_pipeline.core
          src/farfan_pipeline/__init__.py -> farfan_pipeline
    """
    rel_path = file_path.relative_to(src_dir)
    parts = list(rel_path.parts)
    
    if parts[-1] == "__init__.py":
        # For __init__.py, the package is the directory  
        return ".".join(parts[:-1])
    else:
        # For regular modules, the package is the parent directory
        return ".".join(parts[:-1])


def convert_relative_import(line: str, current_package: str) -> str:
    """Convert a single relative import line to absolute.
    
    Args:
        line: The line containing the import
        current_package: The current module's package (e.g., 'farfan_pipeline.core')
    
    Returns:
        The converted line, or the original if no conversion needed
    """
    # Match: from . import x
    # Match: from .. import x  
    # Match: from .module import x
    # Match: from ..module import x
    match = re.match(r'^(\s*)from\s+(\.+)(\S*)\s+import\s+(.+)$', line)
    
    if not match:
        return line
    
    indent, dots, module_suffix, imports = match.groups()
    level = len(dots)
    
    # Split current package into parts
    package_parts = current_package.split('.') if current_package else []
    
    # Special case: if level == 1 and we have module_suffix, we stay in current package
    # Example: from .core import x when in farfan_pipeline => farfan_pipeline.core
    # Example: from .factory import x when in farfan_pipeline.analysis => farfan_pipeline.analysis.factory
    
    if level == 1:
        # from . or from .module
        if module_suffix:
            # from .module import x
            absolute_module = ".".join(package_parts + [module_suffix]) if package_parts else module_suffix
        else:
            # from . import x (import from current package)
            absolute_module = ".".join(package_parts) if package_parts else "farfan_pipeline"
    else:
        # level >= 2: from .. or from ..module or from ...module
        # Go up (level - 1) directories from current package
        steps_up = level - 1
        
        if steps_up >= len(package_parts):
            # Too many levels up
            print(f"⚠️  Warning: Cannot resolve {line.strip()} from {current_package}", file=sys.stderr)
            return line
        
        base_parts = package_parts[:len(package_parts) - steps_up]
        
        if module_suffix:
            absolute_module = ".".join(base_parts + [module_suffix])
        else:
            absolute_module = ".".join(base_parts) if base_parts else "farfan_pipeline"
    
    return f"{indent}from {absolute_module} import {imports}"


def process_file(file_path: Path, src_dir: Path, dry_run: bool = False) -> bool:
    """Process a single file, converting all relative imports.
    
    Returns:
        True if file was modified
    """
    try:
        with open(file_path, 'r', encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"⚠️  Could not read {file_path}: {e}", file=sys.stderr)
        return False
    
    current_package = get_package_from_file(file_path, src_dir)
    new_lines = []
    modified = False
    
    for i, line in enumerate(lines, 1):
        # Only process lines, keeping exact formatting (including newlines)
        line_without_newline = line.rstrip('\r\n')
        newline_chars = line[len(line_without_newline):]
        
        new_line_content = convert_relative_import(line_without_newline, current_package)
        
        if new_line_content != line_without_newline:
            modified = True
            if not dry_run:
                rel_file_path = file_path.relative_to(src_dir.parent)
                print(f"  {rel_file_path}:{i}")
                print(f"    - {line_without_newline}")
                print(f"    + {new_line_content}")
        
        new_lines.append(new_line_content + newline_chars)
    
    if modified and not dry_run:
        with open(file_path, 'w', encoding="utf-8") as f:
            f.writelines(new_lines)
    
    return modified


def main() -> int:
    """Convert all relative imports in farfan_pipeline."""
    repo_root = Path(__file__).resolve().parent.parent
    src_dir = repo_root / "src"
    package_dir = src_dir / "farfan_pipeline"
    
    if not package_dir.exists():
        print(f"❌ Package directory not found: {package_dir}", file=sys.stderr)
        return 2
    
    print("🔧 Converting relative imports to absolute imports...")
    print(f"   Root: {package_dir}\n")
    
    files_processed = 0
    files_modified = 0
    
    for py_file in sorted(package_dir.rglob("*.py")):
        files_processed += 1
        if process_file(py_file, src_dir, dry_run=False):
            files_modified += 1
    
    print(f"\n✅ Processed {files_processed} files, modified {files_modified}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

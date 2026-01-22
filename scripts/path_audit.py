#!/usr/bin/env python3
"""
Path Audit Script for FARFAN_MCDPP
==================================

Run this script to verify the Python path configuration and import structure
of the FARFAN_MCDPP project.

Usage:
    python scripts/path_audit.py

Author: Path Audit Tool
Date: 2026-01-21
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple

# ANSI color codes
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def get_project_root() -> Path:
    """Get the project root directory."""
    # Start from the script location
    script_path = Path(__file__).resolve()
    # Navigate up until we find key markers
    current = script_path.parent
    while current != current.parent:
        if (current / "pyproject.toml").exists() and (current / "src").exists():
            return current
        current = current.parent
    # Fallback to current working directory
    return Path.cwd()


def check_path_configuration(root: Path) -> Dict[str, bool]:
    """Check the Python path configuration."""
    src_path = str(root / "src")

    return {
        "root_in_syspath": str(root) in sys.path,
        "src_in_syspath": src_path in sys.path,
        "empty_string_in_syspath": "" in sys.path,
        "can_import_farfan": can_import_module("farfan_pipeline.orchestration"),
        "can_import_cqc": can_import_module("canonic_questionnaire_central"),
    }


def can_import_module(module_name: str) -> bool:
    """Test if a module can be imported."""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False


def list_package_structure(root: Path) -> List[Dict[str, str]]:
    """List the package structure of the project."""
    packages = []

    # Check src/ packages
    src_dir = root / "src"
    if src_dir.exists():
        for item in sorted(src_dir.iterdir()):
            if item.is_dir() and not item.name.startswith("_"):
                init_file = item / "__init__.py"
                pkg_type = "namespace" if not init_file.exists() else "regular"
                packages.append({
                    "name": item.name,
                    "location": "src/",
                    "type": pkg_type,
                })

    # Check root-level packages
    for item in sorted(root.iterdir()):
        if item.is_dir() and not item.name.startswith(".") and not item.name.startswith("_"):
            init_file = item / "__init__.py"
            if init_file.exists() and item.name not in ["src", "tests"]:
                packages.append({
                    "name": item.name,
                    "location": "root/",
                    "type": "regular",
                })

    return packages


def check_import_patterns(root: Path) -> List[Tuple[str, str, str]]:
    """Check for import patterns in the codebase."""
    patterns = []

    # Check for relative imports
    check_pattern(root, "from . import", "Relative import (sibling)")
    check_pattern(root, "from .. import", "Relative import (parent)")
    check_pattern(root, "from farfan_pipeline", "Absolute import (farfan_pipeline)")
    check_pattern(root, "from canonic_questionnaire_central", "Absolute import (CQC)")

    return patterns


def check_pattern(root: Path, pattern: str, description: str):
    """Check for a specific import pattern."""
    count = 0
    for py_file in root.rglob("*.py"):
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                for line in f:
                    if pattern in line and not line.strip().startswith("#"):
                        count += 1
                        break
        except Exception:
            continue
    icon = Colors.GREEN + "✅" + Colors.END if count > 0 else Colors.RED + "❌" + Colors.END
    print(f"  {icon} {pattern:<45} ({count} files) # {description}")


def print_header(text: str):
    """Print a section header."""
    print(Colors.BOLD + Colors.BLUE + "\n" + text + Colors.END)
    print("-" * 80)


def print_result(icon: str, text: str, status: bool):
    """Print a result line."""
    color = Colors.GREEN if status else Colors.RED
    print(f"  {color}{icon}{Colors.END} {text}")


def main():
    """Main entry point."""
    print(Colors.BOLD + Colors.CYAN)
    print("=" * 80)
    print(" " * 15 + "PATH AUDIT REPORT - FARFAN_MCDPP")
    print("=" * 80)
    print(Colors.END)

    # Get project root
    root = get_project_root()
    print(f"\nProject Root: {root}")

    # Check path configuration
    print_header("1. PATH CONFIGURATION")
    checks = check_path_configuration(root)
    print_result("✅", "src/ in sys.path", checks["src_in_syspath"])
    print_result("❌", "Root in sys.path (expected)", not checks["root_in_syspath"])
    print_result("✅", "Empty string in sys.path (CWD)", checks["empty_string_in_syspath"])

    # Check imports
    print_header("2. IMPORT VERIFICATION")
    print_result("✅" if checks["can_import_farfan"] else "❌",
                "Can import farfan_pipeline.orchestration",
                checks["can_import_farfan"])

    cqc_import_result = checks["can_import_cqc"]
    cqc_note = ""
    if not cqc_import_result and "" in sys.path:
        # Check if we're in the project root
        if Path.cwd() == root:
            cqc_import_result = True
            cqc_note = " (works from project root due to CWD in sys.path)"
    print_result("✅" if cqc_import_result else "❌",
                "Can import canonic_questionnaire_central" + cqc_note,
                cqc_import_result)

    # List packages
    print_header("3. PACKAGE STRUCTURE")
    packages = list_package_structure(root)
    for pkg in packages:
        location_icon = "📦" if pkg["type"] == "regular" else "📦 ns"
        type_color = Colors.YELLOW if pkg["type"] == "namespace" else ""
        print(f"  {location_icon} {pkg['name']}/ ({type_color}{pkg['type']}{Colors.END}, {pkg['location']})")

    # Import patterns
    print_header("4. IMPORT PATERNS DETECTED")
    check_pattern(root, "from . import", "Relative import (sibling)")
    check_pattern(root, "from .. import", "Relative import (parent)")
    check_pattern(root, "from farfan_pipeline", "Absolute import (farfan_pipeline)")
    check_pattern(root, "from canonic_questionnaire_central", "Absolute import (CQC)")

    # Recommendations
    print_header("5. RECOMMENDATIONS")
    recommendations = [
        "Ensure src/ is in PYTHONPATH (currently: ✅)",
        "Consider adding root to PYTHONPATH for CQC imports",
        "Use absolute imports: `from farfan_pipeline.orchestration import ...`",
    ]
    for rec in recommendations:
        print(f"  {Colors.GREEN}➜{Colors.END} {rec}")

    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()

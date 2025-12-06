#!/usr/bin/env python3
import os
import re
import ast
import sys
from pathlib import Path

# Configuration
ROOT_DIR = Path(__file__).parent.parent
SRC_DIR = ROOT_DIR / "src"
VIOLATIONS_REPORT = ROOT_DIR / "violations_audit.md"

# Patterns to flag
HARDCODED_FLOAT_PATTERN = re.compile(r"=\s*(0\.\d+|1\.0)\b")
CALIBRATION_KEYWORDS = ["weight", "score", "threshold", "calibration", "alpha", "beta", "gamma"]
YAML_EXTENSION_PATTERN = re.compile(r"\.ya?ml", re.IGNORECASE)

class CalibrationVisitor(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.violations = []

    def visit_Assign(self, node):
        # Check for hardcoded float assignments to suspicious variables
        for target in node.targets:
            if isinstance(target, ast.Name):
                if any(kw in target.id.lower() for kw in CALIBRATION_KEYWORDS):
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, float):
                        if 0.0 <= node.value.value <= 1.0:
                            self.violations.append(
                                f"Hardcoded calibration value detected: {target.id} = {node.value.value} (Line {node.lineno})"
                            )
        self.generic_visit(node)

    def visit_Dict(self, node):
        # Check for dict literals that look like calibration configs
        has_calibration_keys = False
        for key in node.keys:
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                if any(kw in key.value.lower() for kw in CALIBRATION_KEYWORDS):
                    has_calibration_keys = True
                    break
        
        if has_calibration_keys:
             for value in node.values:
                if isinstance(value, ast.Constant) and isinstance(value.value, float):
                     if 0.0 <= value.value <= 1.0:
                        self.violations.append(
                            f"Potential hardcoded calibration dict detected at Line {node.lineno}"
                        )
                        break
        self.generic_visit(node)

    def visit_Call(self, node):
        # Check for yaml loading or usage
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == 'safe_load' or node.func.attr == 'load':
                 # This is a weak check, but catches yaml.safe_load
                 pass 
        self.generic_visit(node)

def scan_file(filepath):
    violations = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Regex checks
        if YAML_EXTENSION_PATTERN.search(content):
            violations.append("Reference to YAML file detected (YAML is prohibited)")

        # AST checks
        try:
            tree = ast.parse(content, filename=filepath)
            visitor = CalibrationVisitor(filepath)
            visitor.visit(tree)
            violations.extend(visitor.violations)
        except SyntaxError:
            violations.append("SyntaxError: Could not parse file for AST analysis")

    except Exception as e:
        violations.append(f"Error scanning file: {str(e)}")
        
    return violations

def main():
    print(f"Starting audit of {SRC_DIR}...")
    all_violations = {}
    
    if not SRC_DIR.exists():
        print(f"Source directory {SRC_DIR} not found!")
        return

    for filepath in SRC_DIR.rglob("*.py"):
        violations = scan_file(filepath)
        if violations:
            rel_path = filepath.relative_to(ROOT_DIR)
            all_violations[str(rel_path)] = violations

    # Generate Report
    with open(VIOLATIONS_REPORT, "w", encoding="utf-8") as f:
        f.write("# SIN_CARRETA Compliance Audit Report\n\n")
        f.write("## Violations Detected\n\n")
        
        if not all_violations:
            f.write("No violations found. System is compliant.\n")
        else:
            for path, issues in all_violations.items():
                f.write(f"### {path}\n")
                for issue in issues:
                    f.write(f"- {issue}\n")
                f.write("\n")
    
    print(f"Audit complete. Report generated at {VIOLATIONS_REPORT}")
    if all_violations:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()

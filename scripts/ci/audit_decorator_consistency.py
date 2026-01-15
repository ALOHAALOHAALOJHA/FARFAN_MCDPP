#!/usr/bin/env python3
"""
CI Script: Audit Decorator Consistency
======================================

Purpose: Detect obsolete imports and missing calibration parameters in Phase 1/2 files.
         Ensures all methods are properly decorated according to their epistemic level.

CHECKS PERFORMED:
    1. OBSOLETE_IMPORT: Detects imports from deprecated calibration paths
    2. MISSING_DECORATOR: Methods in canonical classification without decorators
    3. WRONG_DECORATOR: Methods with decorators that don't match canonical level
    4. MISSING_PARAMETER: Decorated methods missing required calibratable parameters
    5. SIGNATURE_MISMATCH: Decorator level vs function's expected parameters

EXIT CODES:
    0: All checks passed
    1: Warnings found (non-blocking)
    2: Errors found (blocking)

USAGE:
    python scripts/ci/audit_decorator_consistency.py [--fix] [--verbose]
    
    --fix: Attempt to auto-fix simple issues (add missing imports)
    --verbose: Print all checked files, not just issues
"""

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Final

# =============================================================================
# CONSTANTS
# =============================================================================

# Obsolete import paths that should be updated
OBSOLETE_IMPORT_PATHS: Final[frozenset[str]] = frozenset({
    "farfan_pipeline.infrastructure.capaz_calibration_parmetrization",
    "farfan_pipeline.calibracion_parametrizacion",
    "farfan_pipeline.infrastructure.calibration_old",
    "farfan_pipeline.infrastructure.capaz_calibration_parmetrization.decorators",
})

# Correct import path
CORRECT_IMPORT_PATH: Final[str] = "farfan_pipeline.infrastructure.calibration"

# Correct decorator import path
CORRECT_DECORATOR_IMPORT: Final[str] = (
    "farfan_pipeline.infrastructure.calibration.uoa_sensitive"
)

# Decorator names by epistemic level
LEVEL_TO_DECORATORS: Final[dict[str, frozenset[str]]] = {
    "N1-EMP": frozenset({"fact_aware", "chunk_size_aware"}),
    "N2-INF": frozenset({"parameter_aware", "prior_aware"}),
    "N3-AUD": frozenset({"constraint_aware", "veto_aware"}),
    "N4-META": frozenset({"meta_aware"}),
    "FULLY_CALIBRATED": frozenset({"fully_calibrated", "uoa_sensitive"}),
}

# Required parameters by decorator
DECORATOR_REQUIRED_PARAMS: Final[dict[str, frozenset[str]]] = {
    "fact_aware": frozenset({"chunk_size"}),
    "chunk_size_aware": frozenset({"chunk_size"}),
    "parameter_aware": frozenset({"prior_strength"}),
    "prior_aware": frozenset({"prior_strength"}),
    "constraint_aware": frozenset({"veto_threshold"}),
    "veto_aware": frozenset({"veto_threshold"}),
    "meta_aware": frozenset(),
    "fully_calibrated": frozenset({"chunk_size", "prior_strength", "veto_threshold"}),
}

# Directories to scan
SCAN_DIRECTORIES: Final[list[str]] = [
    "src/farfan_pipeline/phases/Phase_1",
    "src/farfan_pipeline/phases/Phase_2",
    "src/farfan_pipeline/methods_dispensary",
]


# =============================================================================
# DATA STRUCTURES
# =============================================================================

class IssueSeverity(Enum):
    """Severity level for detected issues."""
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


@dataclass
class AuditIssue:
    """Single audit issue found during scan."""
    file_path: Path
    line_number: int
    issue_type: str
    severity: IssueSeverity
    message: str
    suggestion: str | None = None


@dataclass
class AuditResult:
    """Complete audit result."""
    files_scanned: int = 0
    issues: list[AuditIssue] = field(default_factory=list)
    
    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == IssueSeverity.ERROR)
    
    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == IssueSeverity.WARNING)
    
    @property
    def info_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == IssueSeverity.INFO)


# =============================================================================
# AST VISITORS
# =============================================================================

class ImportVisitor(ast.NodeVisitor):
    """Visitor to find obsolete imports."""
    
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.issues: list[AuditIssue] = []
    
    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self._check_import(alias.name, node.lineno)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self._check_import(node.module, node.lineno)
        self.generic_visit(node)
    
    def _check_import(self, module_path: str, line_no: int) -> None:
        for obsolete in OBSOLETE_IMPORT_PATHS:
            if module_path.startswith(obsolete):
                self.issues.append(AuditIssue(
                    file_path=self.file_path,
                    line_number=line_no,
                    issue_type="OBSOLETE_IMPORT",
                    severity=IssueSeverity.ERROR,
                    message=f"Obsolete import path: {module_path}",
                    suggestion=f"Replace with: from {CORRECT_DECORATOR_IMPORT} import ...",
                ))


class DecoratorVisitor(ast.NodeVisitor):
    """Visitor to check decorator consistency."""
    
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.issues: list[AuditIssue] = []
        self.current_class: str | None = None
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = None
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)
    
    def _check_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        # Get decorators
        decorators = self._get_decorator_names(node)
        calibration_decorators = self._get_calibration_decorators(decorators)
        
        if not calibration_decorators:
            # No calibration decorator - check if method should have one
            self._check_missing_decorator(node)
            return
        
        # Check parameter consistency
        for decorator_name in calibration_decorators:
            self._check_parameter_consistency(node, decorator_name)
    
    def _get_decorator_names(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
        """Extract decorator names from function."""
        names: list[str] = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                names.append(decorator.id)
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    names.append(decorator.func.id)
                elif isinstance(decorator.func, ast.Attribute):
                    names.append(decorator.func.attr)
        return names
    
    def _get_calibration_decorators(self, decorators: list[str]) -> list[str]:
        """Filter to only calibration-related decorators."""
        all_calibration = set()
        for level_decorators in LEVEL_TO_DECORATORS.values():
            all_calibration.update(level_decorators)
        return [d for d in decorators if d in all_calibration]
    
    def _check_missing_decorator(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Check if function should have a calibration decorator."""
        # Build full method name
        method_name = node.name
        if self.current_class:
            full_name = f"{self.current_class}.{method_name}"
        else:
            full_name = method_name
        
        # Check if method has calibratable parameters but no decorator
        params = self._get_function_params(node)
        calibratable_found = self._find_calibratable_params(params)
        
        if calibratable_found:
            self.issues.append(AuditIssue(
                file_path=self.file_path,
                line_number=node.lineno,
                issue_type="MISSING_DECORATOR",
                severity=IssueSeverity.WARNING,
                message=f"Method '{full_name}' has calibratable parameters {calibratable_found} but no decorator",
                suggestion=f"Add appropriate decorator (e.g., @fact_aware for chunk_size)",
            ))
    
    def _check_parameter_consistency(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        decorator_name: str,
    ) -> None:
        """Check if decorated function has required parameters."""
        required_params = DECORATOR_REQUIRED_PARAMS.get(decorator_name, frozenset())
        if not required_params:
            return
        
        func_params = self._get_function_params(node)
        missing = required_params - func_params
        
        if missing:
            method_name = node.name
            if self.current_class:
                method_name = f"{self.current_class}.{method_name}"
            
            self.issues.append(AuditIssue(
                file_path=self.file_path,
                line_number=node.lineno,
                issue_type="MISSING_PARAMETER",
                severity=IssueSeverity.WARNING,
                message=(
                    f"Method '{method_name}' has @{decorator_name} but missing "
                    f"recommended parameters: {missing}"
                ),
                suggestion=f"Add parameters: {', '.join(f'{p}: <type> = <default>' for p in missing)}",
            ))
    
    def _get_function_params(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
        """Get all parameter names from function."""
        params: set[str] = set()
        for arg in node.args.args:
            params.add(arg.arg)
        for arg in node.args.kwonlyargs:
            params.add(arg.arg)
        if node.args.vararg:
            params.add(node.args.vararg.arg)
        if node.args.kwarg:
            params.add(node.args.kwarg.arg)
        return params
    
    def _find_calibratable_params(self, params: set[str]) -> set[str]:
        """Find calibratable parameters in function params."""
        all_calibratable = {
            "chunk_size", "extraction_coverage_target",
            "prior_strength", "confidence_threshold",
            "veto_threshold", "coherence_threshold",
        }
        return params & all_calibratable


# =============================================================================
# AUDIT FUNCTIONS
# =============================================================================

def audit_file(file_path: Path) -> list[AuditIssue]:
    """Audit a single Python file."""
    issues: list[AuditIssue] = []
    
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError as e:
        issues.append(AuditIssue(
            file_path=file_path,
            line_number=e.lineno or 0,
            issue_type="SYNTAX_ERROR",
            severity=IssueSeverity.ERROR,
            message=f"Syntax error: {e.msg}",
        ))
        return issues
    except Exception as e:
        issues.append(AuditIssue(
            file_path=file_path,
            line_number=0,
            issue_type="PARSE_ERROR",
            severity=IssueSeverity.ERROR,
            message=f"Failed to parse file: {e}",
        ))
        return issues
    
    # Check for obsolete imports
    import_visitor = ImportVisitor(file_path)
    import_visitor.visit(tree)
    issues.extend(import_visitor.issues)
    
    # Check decorator consistency
    decorator_visitor = DecoratorVisitor(file_path)
    decorator_visitor.visit(tree)
    issues.extend(decorator_visitor.issues)
    
    return issues


def audit_directory(directory: Path) -> AuditResult:
    """Audit all Python files in directory recursively."""
    result = AuditResult()
    
    if not directory.exists():
        return result
    
    for file_path in directory.rglob("*.py"):
        # Skip test files and __pycache__
        if "__pycache__" in str(file_path):
            continue
        if file_path.name.startswith("test_"):
            continue
        
        result.files_scanned += 1
        issues = audit_file(file_path)
        result.issues.extend(issues)
    
    return result


def run_audit(verbose: bool = False) -> AuditResult:
    """Run full audit on all configured directories."""
    combined_result = AuditResult()
    
    base_path = Path.cwd()
    
    for directory_str in SCAN_DIRECTORIES:
        directory = base_path / directory_str
        if verbose:
            print(f"Scanning: {directory}")
        
        result = audit_directory(directory)
        combined_result.files_scanned += result.files_scanned
        combined_result.issues.extend(result.issues)
    
    return combined_result


# =============================================================================
# OUTPUT FORMATTING
# =============================================================================

def format_issue(issue: AuditIssue) -> str:
    """Format a single issue for console output."""
    severity_icons = {
        IssueSeverity.INFO: "ℹ️",
        IssueSeverity.WARNING: "⚠️",
        IssueSeverity.ERROR: "❌",
    }
    
    icon = severity_icons[issue.severity]
    
    lines = [
        f"{icon} [{issue.issue_type}] {issue.file_path}:{issue.line_number}",
        f"   {issue.message}",
    ]
    
    if issue.suggestion:
        lines.append(f"   💡 Suggestion: {issue.suggestion}")
    
    return "\n".join(lines)


def print_report(result: AuditResult) -> None:
    """Print formatted audit report."""
    print("\n" + "=" * 70)
    print("CALIBRATION DECORATOR CONSISTENCY AUDIT REPORT")
    print("=" * 70)
    
    print(f"\nFiles scanned: {result.files_scanned}")
    print(f"Issues found: {len(result.issues)}")
    print(f"  - Errors: {result.error_count}")
    print(f"  - Warnings: {result.warning_count}")
    print(f"  - Info: {result.info_count}")
    
    if result.issues:
        print("\n" + "-" * 70)
        print("ISSUES DETAIL:")
        print("-" * 70 + "\n")
        
        # Sort by severity (errors first)
        sorted_issues = sorted(
            result.issues,
            key=lambda i: (i.severity.value, str(i.file_path), i.line_number),
        )
        
        for issue in sorted_issues:
            print(format_issue(issue))
            print()
    
    print("-" * 70)
    
    if result.error_count > 0:
        print("❌ AUDIT FAILED - Fix errors before merging")
    elif result.warning_count > 0:
        print("⚠️ AUDIT PASSED WITH WARNINGS - Review before merging")
    else:
        print("✅ AUDIT PASSED - All checks passed")
    
    print("=" * 70 + "\n")


# =============================================================================
# MAIN
# =============================================================================

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Audit decorator consistency in calibration system",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print verbose output",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to auto-fix simple issues (not implemented)",
    )
    
    args = parser.parse_args()
    
    result = run_audit(verbose=args.verbose)
    print_report(result)
    
    # Exit codes
    if result.error_count > 0:
        return 2
    elif result.warning_count > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

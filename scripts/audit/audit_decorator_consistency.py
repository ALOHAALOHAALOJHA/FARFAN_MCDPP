#!/usr/bin/env python3
"""
CI Script: Audita consistencia entre decoradores UoA y parámetros de función.

Exit codes:
- 0: All checks passed
- 1: Errors found
"""

import ast
import sys
from pathlib import Path

REQUIRED_PARAMS = {
    "fact_aware": ["chunk_size", "extraction_coverage_target"],
    "parameter_aware": ["prior_strength", "confidence_threshold"],
    "constraint_aware": ["veto_threshold", "significance_level"],
    "chunk_size_aware": ["chunk_size"],
    "prior_aware": ["prior_strength"],
    "veto_aware": ["veto_threshold"],
}

OBSOLETE_IMPORTS = [
    "capaz_calibration_parmetrization",
    "calibracion_parametrizacion.canonical_specs",
]


class DecoratorAuditor(ast.NodeVisitor):
    """AST visitor that audits decorator consistency."""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.errors: list[str] = []
        
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            for obsolete in OBSOLETE_IMPORTS:
                if obsolete in node.module:
                    self.errors.append(
                        f"{self.filepath}:{node.lineno}: OBSOLETE IMPORT - "
                        f"'{node.module}' → use 'farfan_pipeline.infrastructure.calibration'"
                    )
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        for decorator in node.decorator_list:
            dec_name = self._get_decorator_name(decorator)
            
            if dec_name in REQUIRED_PARAMS:
                func_params = [arg.arg for arg in node.args.args]
                has_kwargs = node.args.kwarg is not None
                
                required = REQUIRED_PARAMS[dec_name]
                missing = [p for p in required if p not in func_params]
                
                if missing and not has_kwargs:
                    self.errors.append(
                        f"{self.filepath}:{node.lineno}: @{dec_name} on "
                        f"{node.name}() missing params: {missing}"
                    )
        
        self.generic_visit(node)
    
    def _get_decorator_name(self, decorator: ast.expr) -> str | None:
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
        return None


def audit_file(filepath: Path) -> list[str]:
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError) as e:
        return [f"{filepath}: Error - {e}"]
    
    auditor = DecoratorAuditor(filepath)
    auditor.visit(tree)
    return auditor.errors


def main() -> int:
    audit_paths = [
        Path("src/farfan_pipeline/methods"),
        Path("src/farfan_pipeline/phases"),
        Path("src/farfan_pipeline/infrastructure/calibration"),
    ]
    
    all_errors: list[str] = []
    files_audited = 0
    
    for audit_path in audit_paths:
        if not audit_path.exists():
            continue
            
        for py_file in audit_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            all_errors.extend(audit_file(py_file))
            files_audited += 1
    
    print(f"\n{'='*60}")
    print(f"DECORATOR CONSISTENCY AUDIT")
    print(f"{'='*60}")
    print(f"Files audited: {files_audited}")
    print(f"Errors found: {len(all_errors)}")
    
    if all_errors:
        print("\n❌ ERRORS:\n")
        for error in all_errors:
            print(f"  {error}")
        return 1
    else:
        print("\n✅ All checks passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())

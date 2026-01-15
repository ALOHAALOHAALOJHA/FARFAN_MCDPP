#!/usr/bin/env python3
"""
Generates checklist of methods that should have UoA decorators.
Prioritizes by epistemological level (N3 > N2 > N1).
"""

import ast
import json
import sys
from pathlib import Path
from typing import Any

N1_CANONICAL = {
    "TextMiningEngine.diagnose_critical_links": "fact_aware",
    "SemanticProcessor.chunk_text": "fact_aware",
    "SemanticProcessor.embed_single": "fact_aware",
    "PDETMunicipalPlanAnalyzer._extract_financial_amounts": "fact_aware",
}

N2_CANONICAL = {
    "BayesianNumericalAnalyzer.evaluate_policy_metric": "parameter_aware",
    "AdaptivePriorCalculator.calculate_likelihood_adaptativo": "parameter_aware",
    "TeoriaCambio._encontrar_caminos_completos": "parameter_aware",
}

N3_CANONICAL = {
    "PolicyContradictionDetector._detect_logical_incompatibilities": "constraint_aware",
    "AdvancedDAGValidator._is_acyclic": "constraint_aware",
    "IndustrialGradeValidator.execute_suite": "constraint_aware",
}

ALL_CANONICAL = {**N1_CANONICAL, **N2_CANONICAL, **N3_CANONICAL}

DECORATOR_TO_LEVEL = {
    "fact_aware": "N1-EMP",
    "parameter_aware": "N2-INF",
    "constraint_aware": "N3-AUD",
}


class MethodAuditor(ast.NodeVisitor):
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.current_class: str | None = None
        self.missing: list[dict[str, Any]] = []
        
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self.current_class:
            full_name = f"{self.current_class}.{node.name}"
        else:
            full_name = node.name
        
        if full_name in ALL_CANONICAL:
            has_decorator = any(
                self._get_dec_name(d) in {"fact_aware", "parameter_aware", "constraint_aware", "uoa_sensitive"}
                for d in node.decorator_list
            )
            
            if not has_decorator:
                expected = ALL_CANONICAL[full_name]
                level = DECORATOR_TO_LEVEL.get(expected, "N1-EMP")
                priority = {"N3-AUD": 1, "N2-INF": 2, "N1-EMP": 3}.get(level, 99)
                
                self.missing.append({
                    "file": str(self.filepath),
                    "line": node.lineno,
                    "method": full_name,
                    "expected_decorator": f"@{expected}",
                    "level": level,
                    "priority": priority,
                })
        
        self.generic_visit(node)
    
    def _get_dec_name(self, d: ast.expr) -> str | None:
        if isinstance(d, ast.Name):
            return d.id
        elif isinstance(d, ast.Call) and isinstance(d.func, ast.Name):
            return d.func.id
        return None


def main() -> int:
    methods_dir = Path("src/farfan_pipeline/methods")
    if not methods_dir.exists():
        print(f"❌ Not found: {methods_dir}")
        return 1
    
    all_missing: list[dict[str, Any]] = []
    
    for py_file in methods_dir.glob("*.py"):
        if py_file.name.startswith("__"):
            continue
        try:
            tree = ast.parse(py_file.read_text())
            auditor = MethodAuditor(py_file)
            auditor.visit(tree)
            all_missing.extend(auditor.missing)
        except SyntaxError:
            continue
    
    all_missing.sort(key=lambda x: (x["priority"], x["file"]))
    
    output = {
        "total_missing": len(all_missing),
        "by_level": {
            "N3-AUD": len([m for m in all_missing if m["level"] == "N3-AUD"]),
            "N2-INF": len([m for m in all_missing if m["level"] == "N2-INF"]),
            "N1-EMP": len([m for m in all_missing if m["level"] == "N1-EMP"]),
        },
        "methods": all_missing,
    }
    
    print(json.dumps(output, indent=2))
    return 1 if all_missing else 0


if __name__ == "__main__":
    sys.exit(main())

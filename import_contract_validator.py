"""Import Contract Validator - Enforces architectural import boundaries.

This module validates and enforces the 7 architectural import contracts defined in
pyproject.toml using import-linter. It performs:

1. Programmatic execution of import-linter contracts
2. AST-based import analysis for violation-prone modules
3. Generation of detailed violation reports with remediation strategies
4. Failure on any contract violation

Contracts enforced:
1. core.calibration/core.wiring must not import analysis/processing/api
2. core.orchestrator must not import analysis
3. processing cannot import orchestrator
4. analysis cannot import orchestrator
5. infrastructure must not import orchestrator
6. api only calls orchestrator entry points
7. utils stay leaf modules
"""

from __future__ import annotations

import ast
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ImportViolation:
    """Represents a single import contract violation."""
    source_module: str
    imported_module: str
    line_number: int
    import_statement: str
    contract_name: str
    severity: str = "ERROR"


@dataclass
class ContractViolationReport:
    """Container for all contract violations found."""
    violations: list[ImportViolation] = field(default_factory=list)
    contracts_checked: int = 0
    contracts_passed: int = 0
    contracts_failed: int = 0

    def add_violation(self, violation: ImportViolation) -> None:
        self.violations.append(violation)

    def has_violations(self) -> bool:
        return len(self.violations) > 0


class ASTImportAnalyzer:
    """Analyzes Python source files for import statements using AST."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.src_root = project_root / "src" / "farfan_pipeline"

    def analyze_file(self, file_path: Path) -> list[tuple[str, int, str, int]]:
        try:
            with open(file_path, encoding='utf-8') as f:
                source = f.read()
            tree = ast.parse(source, filename=str(file_path))
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        import_stmt = f"import {alias.name}"
                        imports.append((alias.name, node.lineno, import_stmt, 0))
                elif isinstance(node, ast.ImportFrom) and node.module:
                    level = getattr(node, 'level', 0)
                    dots = '.' * level
                    import_stmt = f"from {dots}{node.module} import {', '.join(a.name for a in node.names)}"
                    imports.append((node.module, node.lineno, import_stmt, level))
            return imports
        except Exception as e:
            print(f"Warning: Failed to analyze {file_path}: {e}")
            return []

    def get_module_name(self, file_path: Path) -> str:
        try:
            rel_path = file_path.relative_to(self.src_root)
            parts = list(rel_path.parts)
            if parts[-1] == '__init__.py':
                parts = parts[:-1]
            elif parts[-1].endswith('.py'):
                parts[-1] = parts[-1][:-3]
            return 'farfan_pipeline.' + '.'.join(parts)
        except ValueError:
            return str(file_path)

    def check_import_violation(self, source_module: str, imported_module: str, forbidden_patterns: list[str], level: int = 0) -> bool:
        resolved_import = self._resolve_relative_import(source_module, imported_module, level)
        return any(resolved_import.startswith(pattern) for pattern in forbidden_patterns)

    def _resolve_relative_import(self, source_module: str, imported_module: str, level: int = 0) -> str:
        """Resolve relative imports to absolute module names."""
        if level == 0:
            return imported_module

        source_parts = source_module.split('.')
        if level >= len(source_parts):
            return imported_module

        base_parts = source_parts[:len(source_parts) - level]
        if imported_module:
            return '.'.join(base_parts + [imported_module])
        return '.'.join(base_parts)


class ImportContractValidator:
    """Main validator that orchestrates contract checking."""

    CONTRACTS = [
        {"name": "Core (excluding orchestrator) must not import analysis", "source_patterns": ["farfan_pipeline.core.calibration", "farfan_pipeline.core.wiring"], "forbidden_patterns": ["farfan_pipeline.analysis", "farfan_pipeline.processing", "farfan_pipeline.api"]},
        {"name": "Core orchestrator must not import analysis", "source_patterns": ["farfan_pipeline.core.orchestrator"], "forbidden_patterns": ["farfan_pipeline.analysis"]},
        {"name": "Processing layer cannot import orchestrator", "source_patterns": ["farfan_pipeline.processing"], "forbidden_patterns": ["farfan_pipeline.core.orchestrator"]},
        {"name": "Analysis layer cannot import orchestrator", "source_patterns": ["farfan_pipeline.analysis"], "forbidden_patterns": ["farfan_pipeline.core.orchestrator"]},
        {"name": "Analysis depends on core but not infrastructure", "source_patterns": ["farfan_pipeline.analysis"], "forbidden_patterns": ["farfan_pipeline.infrastructure"]},
        {"name": "Infrastructure must not pull orchestrator", "source_patterns": ["farfan_pipeline.infrastructure"], "forbidden_patterns": ["farfan_pipeline.core.orchestrator"]},
        {"name": "API layer only calls orchestrator entry points", "source_patterns": ["farfan_pipeline.api"], "forbidden_patterns": ["farfan_pipeline.processing", "farfan_pipeline.analysis", "farfan_pipeline.utils"]},
        {"name": "Utils stay leaf modules", "source_patterns": ["farfan_pipeline.utils"], "forbidden_patterns": ["farfan_pipeline.core.orchestrator", "farfan_pipeline.processing", "farfan_pipeline.analysis"]},
    ]

    VIOLATION_PRONE_MODULES = ["src/farfan_pipeline/core/orchestrator", "src/farfan_pipeline/processing/aggregation.py", "src/farfan_pipeline/utils", "src/farfan_pipeline/analysis", "src/farfan_pipeline/api"]

    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path.cwd()
        self.analyzer = ASTImportAnalyzer(self.project_root)
        self.report = ContractViolationReport()

    def run_import_linter(self) -> tuple[bool, str]:
        try:
            result = subprocess.run(["lint-imports", "--config", "pyproject.toml"], cwd=self.project_root, capture_output=True, text=True, timeout=60, check=False)
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "import-linter execution timed out"
        except Exception as e:
            return False, f"Failed to run import-linter: {e}"

    def analyze_violation_prone_modules(self) -> None:
        for module_path in self.VIOLATION_PRONE_MODULES:
            full_path = self.project_root / module_path
            if full_path.is_dir():
                for py_file in full_path.rglob("*.py"):
                    self._analyze_single_file(py_file)
            elif full_path.exists():
                self._analyze_single_file(full_path)

    def _analyze_single_file(self, file_path: Path) -> None:
        source_module = self.analyzer.get_module_name(file_path)
        imports = self.analyzer.analyze_file(file_path)
        for imported_module, line_no, import_stmt, level in imports:
            for contract in self.CONTRACTS:
                is_source_match = any(source_module.startswith(pattern) for pattern in contract["source_patterns"])
                if not is_source_match:
                    continue
                is_violation = self.analyzer.check_import_violation(source_module, imported_module, contract["forbidden_patterns"], level)
                if is_violation:
                    violation = ImportViolation(source_module=source_module, imported_module=imported_module, line_number=line_no, import_statement=import_stmt, contract_name=contract["name"])
                    self.report.add_violation(violation)
                    print(f"  ✗ Violation: {source_module}:{line_no} imports {imported_module}")

    def _generate_remediation_strategy(self, violation: ImportViolation) -> str:
        strategies = []
        if "orchestrator" in violation.imported_module and "analysis" in violation.source_module:
            strategies.append("- **Dependency Inversion**: Analysis should not depend on orchestrator. Move shared interfaces to core.contracts.")
            strategies.append("- **Signal-Based Decoupling**: Use the flux signal system for communication instead of direct imports.")
        if "analysis" in violation.imported_module and "orchestrator" in violation.source_module:
            strategies.append("- **Interface Extraction**: Extract analysis interfaces to core layer, have orchestrator depend on interfaces.")
            strategies.append("- **Factory Pattern**: Use a factory in core to instantiate analysis components without direct import.")
            strategies.append("- **Registry Pattern**: Register analysis handlers via a registry mechanism instead of direct coupling.")
        if "processing" in violation.imported_module and "orchestrator" in violation.source_module:
            strategies.append("- **Move to Core**: If orchestrator needs processing functionality, move it to core.processing_contracts.")
            strategies.append("- **Data Flow Inversion**: Pass preprocessed data from orchestrator to processing, not the other way around.")
        if "orchestrator" in violation.imported_module and "processing" in violation.source_module:
            strategies.append("- **Remove Circular Dependency**: Processing should receive data from orchestrator, not import it.")
            strategies.append("- **Use Data Contracts**: Define shared data structures in core.contracts that both can import.")
        if "utils" in violation.source_module:
            strategies.append("- **Keep Utils Lean**: Utils should be leaf modules with no domain dependencies.")
            strategies.append("- **Extract to Core**: If utils needs domain logic, extract it to an appropriate core module.")
        if "api" in violation.source_module:
            strategies.append("- **API Layer Isolation**: API should only call orchestrator entry points, not bypass to lower layers.")
            strategies.append("- **Facade Pattern**: Create orchestrator facades that expose only necessary API operations.")
        if not strategies:
            strategies.append("- **General**: Refactor to respect layer boundaries. Consider dependency injection or interface extraction.")
        return "\n".join(strategies)

    def generate_markdown_report(self) -> str:
        lines = ["# Layer Violation Report", "", "## Summary", "", f"- **Total Contracts Checked**: {len(self.CONTRACTS)}", f"- **Violations Found**: {len(self.report.violations)}", f"- **Status**: {'❌ FAILED' if self.report.has_violations() else '✅ PASSED'}", ""]
        if not self.report.has_violations():
            lines.extend(["## ✅ All architectural contracts are satisfied!", "", "No import violations detected. The codebase maintains proper layer separation."])
            return "\n".join(lines)
        lines.extend(["## Violations Detected", ""])
        violations_by_contract: dict[str, list[ImportViolation]] = {}
        for violation in self.report.violations:
            if violation.contract_name not in violations_by_contract:
                violations_by_contract[violation.contract_name] = []
            violations_by_contract[violation.contract_name].append(violation)
        for contract_name, violations in violations_by_contract.items():
            lines.extend([f"### Contract: {contract_name}", "", f"**Violations**: {len(violations)}", ""])
            for violation in violations:
                lines.extend([f"#### Violation in `{violation.source_module}`", "", f"- **Line**: {violation.line_number}", f"- **Import Statement**: `{violation.import_statement}`", f"- **Imported Module**: `{violation.imported_module}`", f"- **Severity**: {violation.severity}", "", "**Remediation Strategy**:", "", self._generate_remediation_strategy(violation), "", "---", ""])
        lines.extend(["## Architectural Guidelines", "", "### Layer Dependencies (Allowed)", "", "```", "API Layer", "  ↓ (calls entry points only)", "Core Orchestrator", "  ↓", "Processing ← → Analysis", "  ↓           ↓", "Core (calibration, wiring)", "  ↓", "Utils (leaf layer)", "```", "", "### Forbidden Dependencies", "", "- ❌ Orchestrator → Analysis", "- ❌ Processing → Orchestrator", "- ❌ Analysis → Orchestrator", "- ❌ Utils → Core/Processing/Analysis", "- ❌ API → Processing/Analysis/Utils (bypass orchestrator)", ""])
        return "\n".join(lines)

    def validate(self) -> int:
        print("=" * 80)
        print("Import Contract Validation")
        print("=" * 80)
        print(f"\nProject Root: {self.project_root}")
        print(f"Contracts to Check: {len(self.CONTRACTS)}\n")
        print("Step 1: Running import-linter...")
        linter_success, linter_output = self.run_import_linter()
        print(linter_output)
        if not linter_success:
            print("\n⚠️  import-linter detected violations\n")
        else:
            print("\n✅ import-linter passed\n")
        print("Step 2: Analyzing violation-prone modules with AST...")
        self.analyze_violation_prone_modules()
        print(f"AST Analysis Complete: {len(self.report.violations)} violations found\n")
        print("Step 3: Generating report...")
        report_content = self.generate_markdown_report()
        report_path = self.project_root / "LAYER_VIOLATION_REPORT.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"Report generated: {report_path}\n")
        print("=" * 80)
        if self.report.has_violations() or not linter_success:
            print("❌ VALIDATION FAILED - Contract violations detected")
            print("=" * 80)
            print(f"\nSee {report_path} for detailed remediation strategies.\n")
            return 1
        else:
            print("✅ VALIDATION PASSED - All contracts satisfied")
            print("=" * 80)
            return 0


def main() -> int:
    validator = ImportContractValidator()
    return validator.validate()


if __name__ == "__main__":
    sys.exit(main())

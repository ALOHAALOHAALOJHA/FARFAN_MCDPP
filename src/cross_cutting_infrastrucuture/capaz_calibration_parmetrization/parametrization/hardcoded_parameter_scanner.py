"""
Hardcoded Parameter Scanner.

Scans all Python source files for hardcoded calibration parameters using AST analysis.
Detects numeric literals in scoring contexts and generates compliance report.
Provides specific file:line citations for violations.
"""

import ast
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Tuple
from datetime import datetime


@dataclass
class HardcodedParameter:
    """Details of a hardcoded parameter."""
    file_path: str
    line_number: int
    column: int
    variable_name: str
    value: Any
    value_type: str
    context_line: str
    surrounding_context: List[str]
    violation_type: str
    severity: str
    suggested_fix: str
    in_function: Optional[str] = None
    in_class: Optional[str] = None


@dataclass
class FileAnalysis:
    """Analysis results for a single file."""
    file_path: str
    total_lines: int
    violations: List[HardcodedParameter]
    compliance_status: str
    has_config_import: bool
    config_usage_count: int


class HardcodedParameterScanner:
    """Scans for hardcoded calibration parameters."""
    
    def __init__(self, src_dir: str = "src"):
        self.src_dir = Path(src_dir)
        
        self.parameter_keywords = {
            "threshold", "thresh", "cutoff",
            "weight", "alpha", "beta", "gamma", "delta", "lambda",
            "scale", "factor", "coeff", "coefficient",
            "param", "parameter",
            "calibration", "score_weight",
            "min_score", "max_score",
            "penalty", "bonus",
            "normalize", "normalization_factor"
        }
        
        self.scoring_context_keywords = {
            "score", "scoring", "evaluate", "compute", "calculate",
            "calibrate", "calibration", "weight", "aggregate", "fusion"
        }
        
        self.severity_rules = {
            "critical": lambda v: (
                v.value_type == "float" and 
                0.0 < v.value < 1.0 and
                any(kw in v.variable_name.lower() for kw in ["weight", "alpha", "beta", "threshold"])
            ),
            "high": lambda v: (
                v.value_type in ["float", "int"] and
                any(kw in v.variable_name.lower() for kw in self.parameter_keywords)
            ),
            "medium": lambda v: (
                v.value_type in ["float", "int"] and
                any(kw in v.context_line.lower() for kw in self.scoring_context_keywords)
            )
        }
        
        self.file_analyses: Dict[str, FileAnalysis] = {}
        self.all_violations: List[HardcodedParameter] = []
    
    def should_scan_file(self, file_path: Path) -> bool:
        """Determine if file should be scanned."""
        if any(exclude in str(file_path) for exclude in [
            "venv", ".venv", "__pycache__", ".git",
            "test_", "tests/", ".pytest_cache"
        ]):
            return False
        
        return file_path.suffix == ".py"
    
    def extract_surrounding_context(self, lines: List[str], line_idx: int, context_size: int = 2) -> List[str]:
        """Extract lines around the violation."""
        start = max(0, line_idx - context_size)
        end = min(len(lines), line_idx + context_size + 1)
        
        return [
            f"{i+1:4d}: {lines[i]}"
            for i in range(start, end)
        ]
    
    def determine_severity(self, param: HardcodedParameter) -> str:
        """Determine severity of violation."""
        for severity in ["critical", "high", "medium"]:
            if self.severity_rules[severity](param):
                return severity
        return "low"
    
    def generate_suggested_fix(self, param: HardcodedParameter) -> str:
        """Generate suggested fix for the violation."""
        config_var = f"config['{param.variable_name}']"
        
        return f"Replace '{param.variable_name} = {param.value}' with '{param.variable_name} = {config_var}'"
    
    def analyze_ast_node(
        self, 
        node: ast.AST, 
        lines: List[str], 
        file_path: Path,
        current_function: Optional[str] = None,
        current_class: Optional[str] = None
    ) -> List[HardcodedParameter]:
        """Analyze AST node for hardcoded parameters."""
        violations = []
        
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id
                    
                    if not any(kw in var_name.lower() for kw in self.parameter_keywords):
                        continue
                    
                    if isinstance(node.value, ast.Constant):
                        value = node.value.value
                        
                        if not isinstance(value, (int, float)):
                            continue
                        
                        line_idx = node.lineno - 1
                        context_line = lines[line_idx] if line_idx < len(lines) else ""
                        
                        param = HardcodedParameter(
                            file_path=str(file_path.relative_to(self.src_dir.parent)),
                            line_number=node.lineno,
                            column=node.col_offset,
                            variable_name=var_name,
                            value=value,
                            value_type=type(value).__name__,
                            context_line=context_line.strip(),
                            surrounding_context=self.extract_surrounding_context(lines, line_idx),
                            violation_type="hardcoded_assignment",
                            severity="medium",
                            suggested_fix="",
                            in_function=current_function,
                            in_class=current_class
                        )
                        
                        param.severity = self.determine_severity(param)
                        param.suggested_fix = self.generate_suggested_fix(param)
                        
                        violations.append(param)
        
        elif isinstance(node, ast.Call):
            for keyword in node.keywords:
                if isinstance(keyword.value, ast.Constant):
                    value = keyword.value.value
                    
                    if isinstance(value, (int, float)):
                        if any(kw in keyword.arg.lower() for kw in self.parameter_keywords):
                            line_idx = node.lineno - 1
                            context_line = lines[line_idx] if line_idx < len(lines) else ""
                            
                            param = HardcodedParameter(
                                file_path=str(file_path.relative_to(self.src_dir.parent)),
                                line_number=node.lineno,
                                column=node.col_offset,
                                variable_name=keyword.arg,
                                value=value,
                                value_type=type(value).__name__,
                                context_line=context_line.strip(),
                                surrounding_context=self.extract_surrounding_context(lines, line_idx),
                                violation_type="hardcoded_function_arg",
                                severity="medium",
                                suggested_fix="",
                                in_function=current_function,
                                in_class=current_class
                            )
                            
                            param.severity = self.determine_severity(param)
                            param.suggested_fix = self.generate_suggested_fix(param)
                            
                            violations.append(param)
        
        elif isinstance(node, ast.Dict):
            if not hasattr(node, 'keys'):
                return violations
            
            for key, value in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and isinstance(value, ast.Constant):
                    key_str = str(key.value)
                    val = value.value
                    
                    if isinstance(val, (int, float)):
                        if any(kw in key_str.lower() for kw in self.parameter_keywords):
                            line_idx = node.lineno - 1
                            context_line = lines[line_idx] if line_idx < len(lines) else ""
                            
                            param = HardcodedParameter(
                                file_path=str(file_path.relative_to(self.src_dir.parent)),
                                line_number=node.lineno,
                                column=node.col_offset,
                                variable_name=key_str,
                                value=val,
                                value_type=type(val).__name__,
                                context_line=context_line.strip(),
                                surrounding_context=self.extract_surrounding_context(lines, line_idx),
                                violation_type="hardcoded_dict_value",
                                severity="medium",
                                suggested_fix="",
                                in_function=current_function,
                                in_class=current_class
                            )
                            
                            param.severity = self.determine_severity(param)
                            param.suggested_fix = self.generate_suggested_fix(param)
                            
                            violations.append(param)
        
        return violations
    
    def scan_file(self, file_path: Path) -> FileAnalysis:
        """Scan a single file for hardcoded parameters."""
        try:
            content = file_path.read_text()
            lines = content.split('\n')
            tree = ast.parse(content)
            
            violations = []
            
            has_config_import = (
                "from" in content and "config" in content.lower() or
                "import" in content and "config" in content.lower()
            )
            
            config_usage_count = content.lower().count("config[")
            
            current_class = None
            current_function = None
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    current_class = node.name
                elif isinstance(node, ast.FunctionDef):
                    current_function = node.name
                
                violations.extend(
                    self.analyze_ast_node(node, lines, file_path, current_function, current_class)
                )
            
            compliance_status = "compliant" if not violations else "non_compliant"
            if violations and has_config_import:
                compliance_status = "partially_migrated"
            
            analysis = FileAnalysis(
                file_path=str(file_path.relative_to(self.src_dir.parent)),
                total_lines=len(lines),
                violations=violations,
                compliance_status=compliance_status,
                has_config_import=has_config_import,
                config_usage_count=config_usage_count
            )
            
            return analysis
        
        except Exception as e:
            return FileAnalysis(
                file_path=str(file_path.relative_to(self.src_dir.parent)),
                total_lines=0,
                violations=[],
                compliance_status="error",
                has_config_import=False,
                config_usage_count=0
            )
    
    def scan_all_files(self) -> None:
        """Scan all Python files in source directory."""
        print(f"Scanning {self.src_dir} for hardcoded parameters...")
        
        files_scanned = 0
        
        for py_file in self.src_dir.rglob("*.py"):
            if not self.should_scan_file(py_file):
                continue
            
            files_scanned += 1
            
            analysis = self.scan_file(py_file)
            
            self.file_analyses[analysis.file_path] = analysis
            
            if analysis.violations:
                self.all_violations.extend(analysis.violations)
        
        print(f"Scanned {files_scanned} files, found {len(self.all_violations)} violations")
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive compliance report."""
        total_files = len(self.file_analyses)
        compliant_files = sum(1 for a in self.file_analyses.values() if a.compliance_status == "compliant")
        partially_migrated = sum(1 for a in self.file_analyses.values() if a.compliance_status == "partially_migrated")
        non_compliant = sum(1 for a in self.file_analyses.values() if a.compliance_status == "non_compliant")
        
        violations_by_severity = {
            "critical": [v for v in self.all_violations if v.severity == "critical"],
            "high": [v for v in self.all_violations if v.severity == "high"],
            "medium": [v for v in self.all_violations if v.severity == "medium"],
            "low": [v for v in self.all_violations if v.severity == "low"]
        }
        
        violations_by_type = {}
        for violation in self.all_violations:
            vtype = violation.violation_type
            if vtype not in violations_by_type:
                violations_by_type[vtype] = []
            violations_by_type[vtype].append(violation)
        
        top_violators = sorted(
            self.file_analyses.values(),
            key=lambda a: len(a.violations),
            reverse=True
        )[:10]
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_files_scanned": total_files,
                "compliant_files": compliant_files,
                "partially_migrated_files": partially_migrated,
                "non_compliant_files": non_compliant,
                "total_violations": len(self.all_violations),
                "compliance_percentage": (compliant_files / total_files * 100) if total_files > 0 else 0.0
            },
            "violations_by_severity": {
                severity: {
                    "count": len(viols),
                    "violations": [asdict(v) for v in viols]
                }
                for severity, viols in violations_by_severity.items()
            },
            "violations_by_type": {
                vtype: {
                    "count": len(viols),
                    "violations": [asdict(v) for v in viols[:5]]
                }
                for vtype, viols in violations_by_type.items()
            },
            "top_violators": [
                {
                    "file": analysis.file_path,
                    "violation_count": len(analysis.violations),
                    "has_config_import": analysis.has_config_import,
                    "config_usage_count": analysis.config_usage_count
                }
                for analysis in top_violators
            ],
            "migration_recommendations": []
        }
        
        for analysis in top_violators[:5]:
            if analysis.violations:
                report["migration_recommendations"].append({
                    "file": analysis.file_path,
                    "priority": "high" if len(analysis.violations) > 5 else "medium",
                    "violation_count": len(analysis.violations),
                    "recommendation": f"Migrate {len(analysis.violations)} hardcoded parameters to config",
                    "has_config_import": analysis.has_config_import
                })
        
        return report
    
    def print_summary(self, report: Dict[str, Any]) -> None:
        """Print summary to console."""
        print("\n" + "=" * 80)
        print("HARDCODED PARAMETER COMPLIANCE REPORT")
        print("=" * 80)
        
        summary = report["summary"]
        print(f"\nFiles Scanned: {summary['total_files_scanned']}")
        print(f"✅ Compliant: {summary['compliant_files']}")
        print(f"⚠️  Partially Migrated: {summary['partially_migrated_files']}")
        print(f"❌ Non-Compliant: {summary['non_compliant_files']}")
        print(f"Compliance: {summary['compliance_percentage']:.1f}%")
        print(f"\nTotal Violations: {summary['total_violations']}")
        
        print("\n" + "=" * 80)
        print("VIOLATIONS BY SEVERITY")
        print("=" * 80)
        
        for severity in ["critical", "high", "medium", "low"]:
            count = report["violations_by_severity"][severity]["count"]
            if count > 0:
                print(f"\n{severity.upper()}: {count} violations")
                
                for violation in report["violations_by_severity"][severity]["violations"][:3]:
                    print(f"  📍 {violation['file_path']}:{violation['line_number']}")
                    print(f"     {violation['variable_name']} = {violation['value']}")
                    print(f"     Context: {violation['context_line'][:60]}...")
        
        if report["top_violators"]:
            print("\n" + "=" * 80)
            print("TOP VIOLATORS (files with most violations)")
            print("=" * 80)
            
            for i, violator in enumerate(report["top_violators"][:5], 1):
                print(f"\n{i}. {violator['file']} ({violator['violation_count']} violations)")
                config_status = "✅ Has config import" if violator['has_config_import'] else "❌ No config import"
                print(f"   {config_status}")
        
        if report["migration_recommendations"]:
            print("\n" + "=" * 80)
            print("MIGRATION RECOMMENDATIONS")
            print("=" * 80)
            
            for i, rec in enumerate(report["migration_recommendations"], 1):
                print(f"\n{i}. {rec['file']} ({rec['priority']} priority)")
                print(f"   {rec['recommendation']}")
        
        print("\n" + "=" * 80)
    
    def save_report(self, report: Dict[str, Any], output_path: str = "artifacts/audit_reports/parameter_compliance_report.json") -> None:
        """Save compliance report to file."""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ Detailed compliance report saved to {output}")


def main():
    """Main entry point."""
    scanner = HardcodedParameterScanner()
    
    scanner.scan_all_files()
    
    report = scanner.generate_compliance_report()
    
    scanner.print_summary(report)
    
    scanner.save_report(report)
    
    print("=" * 80)


if __name__ == "__main__":
    main()

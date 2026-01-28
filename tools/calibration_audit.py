#!/usr/bin/env python3
"""
Calibration Audit Tool - Signature Assessment
==============================================

Scans the codebase to identify files requiring calibration parameters
and validates they are properly integrated with the calibration system.

Usage:
    python tools/calibration_audit.py
"""

import json
import re
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List

# Calibration parameter patterns
CALIBRATION_PATTERNS = {
    "thresholds": r"threshold\s*[=:]\s*([0-9]*\.?[0-9]+)",
    "confidence": r"confidence\s*[=:]\s*([0-9]*\.?[0-9]+)",
    "weights": r"weight\s*[=:]\s*([0-9]*\.?[0-9]+)",
    "prior_strength": r"prior[_\s]strength\s*[=:]\s*([0-9]*\.?[0-9]+)",
    "samples": r"(mcmc_|n_)?samples?\s*[=:]\s*([0-9]+)",
    "significance": r"significance[_\s]level\s*[=:]\s*([0-9]*\.?[0-9]+)",
    "veto": r"veto[_\s]threshold\s*[=:]\s*([0-9]*\.?[0-9]+)",
}


@dataclass
class CalibrationParameter:
    """Represents a calibration parameter found in code."""
    name: str
    value: str
    line_number: int
    context: str
    is_hardcoded: bool = True
    uses_calibration_system: bool = False


@dataclass
class FileAuditResult:
    """Results of auditing a single file."""
    filepath: str
    parameters: List[Dict] = field(default_factory=list)
    imports_calibration: bool = False
    uses_calibration_classes: bool = False
    has_hardcoded_values: bool = False
    calibration_status: str = "UNKNOWN"
    recommendations: List[str] = field(default_factory=list)


class CalibrationAuditor:
    """Audits calibration parameter usage across the codebase."""
    
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.src_path = root_path / "src"
        self.results: List[FileAuditResult] = []
        
    def audit_file(self, filepath: Path) -> FileAuditResult:
        """Audit a single Python file for calibration parameters."""
        result = FileAuditResult(filepath=str(filepath))
        
        try:
            content = filepath.read_text(encoding='utf-8')
        except Exception as e:
            result.calibration_status = "ERROR"
            result.recommendations.append(f"Could not read file: {e}")
            return result
        
        # Check for calibration imports
        result.imports_calibration = self._check_calibration_imports(content)
        
        # Check for calibration class usage
        result.uses_calibration_classes = self._check_calibration_classes(content)
        
        # Find hardcoded parameters
        params = self._find_parameters(content)
        result.parameters = [asdict(p) for p in params]
        result.has_hardcoded_values = any(
            p.is_hardcoded for p in params
        )
        
        # Determine status
        result.calibration_status = self._determine_status(result)
        
        # Generate recommendations
        result.recommendations = self._generate_recommendations(result, params)
        
        return result
    
    def _check_calibration_imports(self, content: str) -> bool:
        """Check if file imports calibration modules."""
        calibration_imports = [
            "from farfan_pipeline.calibration import",
            "from farfan_pipeline.infrastructure.calibration import",
            "import farfan_pipeline.calibration",
        ]
        return any(imp in content for imp in calibration_imports)
    
    def _check_calibration_classes(self, content: str) -> bool:
        """Check if file uses calibration classes."""
        calibration_classes = [
            "N1EmpiricalCalibration",
            "N2InferentialCalibration",
            "N3AuditCalibration",
            "N4MetaCalibration",
            "N0InfrastructureCalibration",
            "EpistemicCalibrationRegistry",
            "Phase1PDMCalibrator",
            "create_calibration",
            "get_default_calibration_for_level",
        ]
        return any(cls in content for cls in calibration_classes)
    
    def _find_parameters(self, content: str) -> List[CalibrationParameter]:
        """Find calibration parameters in file content."""
        parameters = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip comments and docstrings
            if line.strip().startswith('#') or '"""' in line or "'''" in line:
                continue
            
            for param_type, pattern in CALIBRATION_PATTERNS.items():
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    value = match.group(1) if match.lastindex >= 1 else match.group(0)
                    
                    # Check if this is from calibration system
                    uses_calibration = any(
                        keyword in line for keyword in [
                            "calibration", "Calibration", "CALIBRATION",
                            "create_calibration", "get_default"
                        ]
                    )
                    
                    param = CalibrationParameter(
                        name=param_type,
                        value=value,
                        line_number=line_num,
                        context=line.strip()[:80],
                        is_hardcoded=not uses_calibration,
                        uses_calibration_system=uses_calibration
                    )
                    parameters.append(param)
        
        return parameters
    
    def _determine_status(self, result: FileAuditResult) -> str:
        """Determine calibration status of file."""
        if not result.parameters:
            return "NO_PARAMETERS"
        
        if result.uses_calibration_classes:
            return "INTEGRATED"
        
        if result.imports_calibration:
            return "PARTIALLY_INTEGRATED"
        
        if result.has_hardcoded_values:
            return "NEEDS_INTEGRATION"
        
        return "UNKNOWN"
    
    def _generate_recommendations(self, result: FileAuditResult, params: List[CalibrationParameter]) -> List[str]:
        """Generate recommendations for file."""
        recommendations = []
        
        if result.calibration_status == "NEEDS_INTEGRATION":
            recommendations.append(
                f"File has {len(params)} hardcoded parameters. "
                "Should import and use calibration system."
            )
            
            # Identify which level would be appropriate
            if any("threshold" in p.name or "confidence" in p.name for p in params):
                recommendations.append(
                    "Consider using N1EmpiricalCalibration for extraction thresholds."
                )
            
            if any("prior" in p.name or "samples" in p.name for p in params):
                recommendations.append(
                    "Consider using N2InferentialCalibration for Bayesian parameters."
                )
            
            if any("veto" in p.name or "significance" in p.name for p in params):
                recommendations.append(
                    "Consider using N3AuditCalibration for validation parameters."
                )
        
        elif result.calibration_status == "PARTIALLY_INTEGRATED":
            recommendations.append(
                "File imports calibration but may not be fully utilizing it. "
                "Review parameter usage."
            )
        
        return recommendations
    
    def audit_directory(self, directory: Path, pattern: str = "*.py") -> None:
        """Audit all Python files in directory."""
        if not directory.exists():
            return
            
        for filepath in directory.rglob(pattern):
            # Skip test files, __pycache__, and generated files
            if any(skip in str(filepath) for skip in ["__pycache__", "test_", ".pyc", "build", "dist"]):
                continue
            
            result = self.audit_file(filepath)
            self.results.append(result)
    
    def generate_report(self) -> Dict:
        """Generate comprehensive audit report."""
        report = {
            "summary": {
                "total_files": len(self.results),
                "integrated": 0,
                "partially_integrated": 0,
                "needs_integration": 0,
                "no_parameters": 0,
                "errors": 0,
            },
            "files_by_status": {},
            "hardcoded_parameters": [],
            "critical_files": [],
        }
        
        files_by_status = defaultdict(list)
        
        for result in self.results:
            # Update counts
            status = result.calibration_status
            if status == "INTEGRATED":
                report["summary"]["integrated"] += 1
            elif status == "PARTIALLY_INTEGRATED":
                report["summary"]["partially_integrated"] += 1
            elif status == "NEEDS_INTEGRATION":
                report["summary"]["needs_integration"] += 1
            elif status == "NO_PARAMETERS":
                report["summary"]["no_parameters"] += 1
            elif status == "ERROR":
                report["summary"]["errors"] += 1
            
            # Group by status
            try:
                rel_path = str(Path(result.filepath).relative_to(self.root_path))
            except:
                rel_path = result.filepath
                
            files_by_status[status].append({
                "path": rel_path,
                "parameter_count": len(result.parameters),
                "has_hardcoded": result.has_hardcoded_values,
                "recommendations": result.recommendations,
            })
            
            # Track hardcoded parameters
            if result.has_hardcoded_values:
                for param in result.parameters:
                    if param.get("is_hardcoded", False):
                        report["hardcoded_parameters"].append({
                            "file": rel_path,
                            "parameter": param["name"],
                            "value": param["value"],
                            "line": param["line_number"],
                            "context": param["context"],
                        })
            
            # Identify critical files (many parameters, not integrated)
            if len(result.parameters) >= 3 and status == "NEEDS_INTEGRATION":
                report["critical_files"].append({
                    "path": rel_path,
                    "parameter_count": len(result.parameters),
                    "recommendations": result.recommendations,
                })
        
        report["files_by_status"] = dict(files_by_status)
        return report
    
    def print_report(self, report: Dict) -> None:
        """Print formatted audit report."""
        print("=" * 80)
        print("CALIBRATION SYSTEM AUDIT REPORT")
        print("=" * 80)
        print()
        
        print("SUMMARY")
        print("-" * 80)
        summary = report["summary"]
        total = summary["total_files"]
        if total == 0:
            print("No files scanned.")
            return
            
        print(f"Total files scanned: {total}")
        print(f"  ✅ Integrated:            {summary['integrated']:4d} ({summary['integrated']/total*100:5.1f}%)")
        print(f"  ⚠️  Partially integrated:  {summary['partially_integrated']:4d} ({summary['partially_integrated']/total*100:5.1f}%)")
        print(f"  ❌ Needs integration:     {summary['needs_integration']:4d} ({summary['needs_integration']/total*100:5.1f}%)")
        print(f"  ⚪ No parameters:         {summary['no_parameters']:4d} ({summary['no_parameters']/total*100:5.1f}%)")
        if summary['errors'] > 0:
            print(f"  🔴 Errors:                {summary['errors']:4d}")
        print()
        
        # Critical files
        if report["critical_files"]:
            print("CRITICAL FILES (3+ parameters, not integrated)")
            print("-" * 80)
            for file_info in report["critical_files"][:10]:
                print(f"  📁 {file_info['path']}")
                print(f"     Parameters: {file_info['parameter_count']}")
                for rec in file_info['recommendations'][:2]:
                    print(f"     → {rec}")
                print()
        
        # Hardcoded parameters summary
        if report["hardcoded_parameters"]:
            print(f"HARDCODED PARAMETERS FOUND: {len(report['hardcoded_parameters'])}")
            print("-" * 80)
            
            # Group by parameter type
            by_type = defaultdict(int)
            for param in report["hardcoded_parameters"]:
                by_type[param["parameter"]] += 1
            
            for param_type, count in sorted(by_type.items(), key=lambda x: -x[1])[:10]:
                print(f"  {param_type:20s}: {count:4d} occurrences")
            print()
        
        # Status breakdown
        print("STATUS BREAKDOWN")
        print("-" * 80)
        for status in ["NEEDS_INTEGRATION", "PARTIALLY_INTEGRATED", "INTEGRATED"]:
            if status in report["files_by_status"]:
                files = report["files_by_status"][status]
                print(f"{status}: {len(files)} files")
                for file_info in files[:3]:
                    print(f"  • {file_info['path']}")
                if len(files) > 3:
                    print(f"  ... and {len(files) - 3} more")
                print()
        
        print("=" * 80)
        print("AUDIT COMPLETE")
        print("=" * 80)


def main():
    """Run calibration audit."""
    root_path = Path(__file__).parent.parent
    auditor = CalibrationAuditor(root_path)
    
    print("Scanning repository for calibration parameters...")
    print()
    
    # Audit key directories
    auditor.audit_directory(root_path / "src" / "farfan_pipeline" / "methods")
    auditor.audit_directory(root_path / "src" / "farfan_pipeline" / "phases")
    auditor.audit_directory(root_path / "src" / "farfan_pipeline" / "infrastructure")
    auditor.audit_directory(root_path / "src" / "farfan_pipeline" / "calibration")
    
    # Generate and print report
    report = auditor.generate_report()
    auditor.print_report(report)
    
    # Save detailed report
    output_path = root_path / "calibration_audit_report.json"
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\nDetailed report saved to: {output_path}")
    
    # Return exit code based on integration status
    if report["summary"]["needs_integration"] > 10:
        print("\n⚠️  WARNING: Many files need calibration integration!")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

#!/usr/bin/env python3
"""
Phase 0 and Orchestrator Wiring Audit

This script analyzes the interaction and wiring between Phase 0 components
and the orchestrator to identify gaps, validate data flow, and ensure proper
integration.

Audit Objectives:
1. Map Phase 0 bootstrap initialization sequence
2. Trace orchestrator's _load_configuration (Phase 0) execution
3. Identify interaction points between Phase_zero modules and orchestrator
4. Verify RuntimeConfig propagation to orchestrator
5. Check factory integration with Phase 0 components
6. Validate exit gates and error handling flow
"""

import ast
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
PHASE_ZERO_DIR = SRC_DIR / "canonic_phases" / "Phase_zero"
ORCHESTRATOR_FILE = SRC_DIR / "orchestration" / "orchestrator.py"
FACTORY_FILE = SRC_DIR / "orchestration" / "factory.py"


@dataclass
class WiringPoint:
    """Represents a wiring point between Phase 0 and orchestrator."""
    
    source_module: str
    source_class: str | None
    source_method: str | None
    target_module: str
    target_class: str | None
    target_method: str | None
    data_type: str
    line_number: int
    severity: str = "info"  # info, warning, critical


@dataclass
class AuditReport:
    """Complete audit report."""
    
    phase0_modules: list[str] = field(default_factory=list)
    orchestrator_phase0_method: str | None = None
    wiring_points: list[WiringPoint] = field(default_factory=list)
    runtime_config_usage: list[dict[str, Any]] = field(default_factory=list)
    factory_integration: dict[str, Any] = field(default_factory=dict)
    exit_gates: list[dict[str, Any]] = field(default_factory=list)
    issues: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "phase0_modules": self.phase0_modules,
            "orchestrator_phase0_method": self.orchestrator_phase0_method,
            "wiring_points": [
                {
                    "source_module": wp.source_module,
                    "source_class": wp.source_class,
                    "source_method": wp.source_method,
                    "target_module": wp.target_module,
                    "target_class": wp.target_class,
                    "target_method": wp.target_method,
                    "data_type": wp.data_type,
                    "line_number": wp.line_number,
                    "severity": wp.severity,
                }
                for wp in self.wiring_points
            ],
            "runtime_config_usage": self.runtime_config_usage,
            "factory_integration": self.factory_integration,
            "exit_gates": self.exit_gates,
            "issues": self.issues,
            "recommendations": self.recommendations,
        }


class Phase0OrchestratorAuditor:
    """Audits Phase 0 and Orchestrator wiring."""
    
    def __init__(self):
        self.report = AuditReport()
    
    def audit(self) -> AuditReport:
        """Run complete audit."""
        print("🔍 Starting Phase 0 and Orchestrator Wiring Audit\n")
        
        # 1. Discover Phase 0 modules
        self._discover_phase0_modules()
        
        # 2. Analyze orchestrator Phase 0 implementation
        self._analyze_orchestrator_phase0()
        
        # 3. Find wiring points
        self._find_wiring_points()
        
        # 4. Check RuntimeConfig propagation
        self._check_runtime_config()
        
        # 5. Analyze factory integration
        self._analyze_factory()
        
        # 6. Validate exit gates
        self._validate_exit_gates()
        
        # 7. Identify issues
        self._identify_issues()
        
        # 8. Generate recommendations
        self._generate_recommendations()
        
        return self.report
    
    def _discover_phase0_modules(self):
        """Discover all Phase 0 modules."""
        print("📁 Discovering Phase 0 modules...")
        
        if not PHASE_ZERO_DIR.exists():
            self.report.issues.append({
                "severity": "critical",
                "category": "missing_directory",
                "message": f"Phase_zero directory not found: {PHASE_ZERO_DIR}",
            })
            return
        
        for py_file in PHASE_ZERO_DIR.glob("*.py"):
            if py_file.name != "__init__.py":
                self.report.phase0_modules.append(py_file.stem)
        
        print(f"  ✓ Found {len(self.report.phase0_modules)} Phase 0 modules")
        print(f"    Modules: {', '.join(sorted(self.report.phase0_modules)[:5])}...")
    
    def _analyze_orchestrator_phase0(self):
        """Analyze orchestrator's Phase 0 implementation."""
        print("\n🔧 Analyzing orchestrator Phase 0 implementation...")
        
        if not ORCHESTRATOR_FILE.exists():
            self.report.issues.append({
                "severity": "critical",
                "category": "missing_file",
                "message": f"Orchestrator file not found: {ORCHESTRATOR_FILE}",
            })
            return
        
        with open(ORCHESTRATOR_FILE, "r") as f:
            content = f.read()
            tree = ast.parse(content)
        
        # Find the Orchestrator class and _load_configuration method
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "Orchestrator":
                for method in node.body:
                    if isinstance(method, ast.FunctionDef) and method.name == "_load_configuration":
                        self.report.orchestrator_phase0_method = "_load_configuration"
                        
                        # Extract method details
                        method_start = method.lineno
                        method_lines = method.end_lineno - method.lineno + 1
                        
                        print(f"  ✓ Found Phase 0 method: {method.name}")
                        print(f"    Location: {ORCHESTRATOR_FILE.name}:{method_start}")
                        print(f"    Lines: {method_lines}")
                        
                        # Check for imports from Phase_zero
                        for item in method.body:
                            if isinstance(item, ast.ImportFrom) and item.module and "Phase_zero" in item.module:
                                print(f"    Import: from {item.module} import {', '.join(alias.name for alias in item.names)}")
        
        # Check FASES definition
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "FASES":
                        print(f"  ✓ Found FASES definition")
                        if isinstance(node.value, ast.List):
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Tuple) and len(elt.elts) >= 3:
                                    phase_id = ast.literal_eval(elt.elts[0])
                                    if phase_id == 0:
                                        phase_name = ast.literal_eval(elt.elts[3]) if len(elt.elts) > 3 else "Unknown"
                                        print(f"    Phase 0: {phase_name}")
    
    def _find_wiring_points(self):
        """Find wiring points between Phase 0 and orchestrator."""
        print("\n🔌 Finding wiring points...")
        
        # Check for Phase_zero imports in orchestrator
        if ORCHESTRATOR_FILE.exists():
            with open(ORCHESTRATOR_FILE, "r") as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                if "Phase_zero" in line and ("import" in line or "from" in line):
                    # Parse the import
                    if "from canonic_phases.Phase_zero" in line:
                        parts = line.split("import")
                        if len(parts) == 2:
                            imported = parts[1].strip().split(",")
                            for imp in imported:
                                imp = imp.strip()
                                if imp:
                                    wp = WiringPoint(
                                        source_module="Phase_zero",
                                        source_class=None,
                                        source_method=None,
                                        target_module="orchestrator",
                                        target_class="Orchestrator",
                                        target_method=None,
                                        data_type=imp,
                                        line_number=i,
                                        severity="info",
                                    )
                                    self.report.wiring_points.append(wp)
        
        print(f"  ✓ Found {len(self.report.wiring_points)} wiring points")
        
        # Group by imported item
        imports_by_type = defaultdict(list)
        for wp in self.report.wiring_points:
            imports_by_type[wp.data_type].append(wp.line_number)
        
        for data_type, lines in sorted(imports_by_type.items()):
            print(f"    {data_type}: lines {', '.join(map(str, lines))}")
    
    def _check_runtime_config(self):
        """Check RuntimeConfig propagation."""
        print("\n⚙️  Checking RuntimeConfig propagation...")
        
        # Check if RuntimeConfig is imported in orchestrator
        if ORCHESTRATOR_FILE.exists():
            with open(ORCHESTRATOR_FILE, "r") as f:
                content = f.read()
            
            if "RuntimeConfig" in content:
                # Find usage
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if "RuntimeConfig" in line and "import" not in line.lower():
                        self.report.runtime_config_usage.append({
                            "line": i,
                            "context": line.strip()[:80],
                        })
                
                print(f"  ✓ Found {len(self.report.runtime_config_usage)} RuntimeConfig usages")
            else:
                self.report.issues.append({
                    "severity": "warning",
                    "category": "missing_runtime_config",
                    "message": "RuntimeConfig not used in orchestrator",
                })
                print("  ⚠️  RuntimeConfig not found in orchestrator")
        
        # Check if orchestrator __init__ accepts RuntimeConfig
        if ORCHESTRATOR_FILE.exists():
            with open(ORCHESTRATOR_FILE, "r") as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == "Orchestrator":
                    for method in node.body:
                        if isinstance(method, ast.FunctionDef) and method.name == "__init__":
                            params = [arg.arg for arg in method.args.args]
                            if "runtime_config" in params:
                                print("  ✓ Orchestrator.__init__ accepts runtime_config parameter")
                            else:
                                self.report.issues.append({
                                    "severity": "warning",
                                    "category": "missing_parameter",
                                    "message": "Orchestrator.__init__ does not accept runtime_config",
                                })
                                print("  ⚠️  Orchestrator.__init__ missing runtime_config parameter")
    
    def _analyze_factory(self):
        """Analyze factory integration with Phase 0."""
        print("\n🏭 Analyzing factory integration...")
        
        if not FACTORY_FILE.exists():
            self.report.issues.append({
                "severity": "critical",
                "category": "missing_file",
                "message": f"Factory file not found: {FACTORY_FILE}",
            })
            return
        
        with open(FACTORY_FILE, "r") as f:
            content = f.read()
        
        # Check for Phase_zero imports
        phase_zero_imports = []
        for line in content.split("\n"):
            if "Phase_zero" in line and "import" in line:
                phase_zero_imports.append(line.strip())
        
        self.report.factory_integration["phase_zero_imports"] = phase_zero_imports
        print(f"  ✓ Found {len(phase_zero_imports)} Phase_zero imports in factory")
        
        # Check for bootstrap/runtime_config usage
        if "RuntimeConfig" in content:
            print("  ✓ Factory uses RuntimeConfig")
            self.report.factory_integration["uses_runtime_config"] = True
        else:
            print("  ⚠️  Factory does not use RuntimeConfig")
            self.report.factory_integration["uses_runtime_config"] = False
        
        if "bootstrap" in content.lower():
            print("  ✓ Factory references bootstrap")
            self.report.factory_integration["references_bootstrap"] = True
        else:
            print("  ⚠️  Factory does not reference bootstrap")
            self.report.factory_integration["references_bootstrap"] = False
    
    def _validate_exit_gates(self):
        """Validate exit gates."""
        print("\n🚪 Validating exit gates...")
        
        # Check for exit gate implementation in Phase_zero modules
        exit_gate_file = PHASE_ZERO_DIR / "exit_gates.py"
        if exit_gate_file.exists():
            print("  ✓ exit_gates.py exists")
            
            with open(exit_gate_file, "r") as f:
                content = f.read()
                tree = ast.parse(content)
            
            # Find gate checking functions
            gate_functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and "gate" in node.name.lower():
                    gate_functions.append(node.name)
            
            self.report.exit_gates.append({
                "file": "exit_gates.py",
                "functions": gate_functions,
            })
            print(f"    Gate functions: {', '.join(gate_functions)}")
        else:
            self.report.issues.append({
                "severity": "warning",
                "category": "missing_module",
                "message": "exit_gates.py not found in Phase_zero",
            })
            print("  ⚠️  exit_gates.py not found")
        
        # Check for gate enforcement in main.py
        main_file = PHASE_ZERO_DIR / "main.py"
        if main_file.exists():
            with open(main_file, "r") as f:
                content = f.read()
            
            gate_checks = []
            for i, line in enumerate(content.split("\n"), 1):
                if "gate" in line.lower() and ("if" in line or "check" in line):
                    gate_checks.append({
                        "line": i,
                        "context": line.strip()[:80],
                    })
            
            self.report.exit_gates.append({
                "file": "main.py",
                "gate_checks": gate_checks,
            })
            print(f"  ✓ Found {len(gate_checks)} gate checks in main.py")
    
    def _identify_issues(self):
        """Identify issues from analysis."""
        print("\n⚠️  Identifying issues...")
        
        # Issue 1: Missing orchestrator integration with Phase 0 bootstrap
        if not any("bootstrap" in wp.data_type.lower() for wp in self.report.wiring_points):
            self.report.issues.append({
                "severity": "warning",
                "category": "missing_integration",
                "message": "Orchestrator does not import Phase_zero bootstrap components",
            })
        
        # Issue 2: No RuntimeConfig in orchestrator
        if not self.report.runtime_config_usage:
            self.report.issues.append({
                "severity": "critical",
                "category": "missing_runtime_config",
                "message": "RuntimeConfig not propagated to orchestrator",
            })
        
        # Issue 3: Limited wiring points
        if len(self.report.wiring_points) < 3:
            self.report.issues.append({
                "severity": "warning",
                "category": "limited_integration",
                "message": f"Only {len(self.report.wiring_points)} wiring points found - minimal integration",
            })
        
        # Count by severity
        critical = sum(1 for i in self.report.issues if i["severity"] == "critical")
        warning = sum(1 for i in self.report.issues if i["severity"] == "warning")
        
        print(f"  Found {len(self.report.issues)} issues:")
        print(f"    Critical: {critical}")
        print(f"    Warning: {warning}")
    
    def _generate_recommendations(self):
        """Generate recommendations based on findings."""
        print("\n💡 Generating recommendations...")
        
        # Recommendation 1: Orchestrator should accept RuntimeConfig
        if not any(i["category"] == "missing_parameter" for i in self.report.issues):
            # Already good
            pass
        else:
            self.report.recommendations.append(
                "Add runtime_config parameter to Orchestrator.__init__ for phase execution control"
            )
        
        # Recommendation 2: Factory should wire Phase 0 components
        if not self.report.factory_integration.get("uses_runtime_config"):
            self.report.recommendations.append(
                "Factory should load RuntimeConfig and pass to orchestrator during initialization"
            )
        
        # Recommendation 3: Exit gates should be explicit
        if not any("exit_gates.py" == eg.get("file") for eg in self.report.exit_gates):
            self.report.recommendations.append(
                "Create Phase_zero/exit_gates.py to consolidate gate checking logic"
            )
        
        # Recommendation 4: Orchestrator Phase 0 should call bootstrap
        self.report.recommendations.append(
            "Orchestrator._load_configuration should validate Phase 0 bootstrap completion"
        )
        
        print(f"  Generated {len(self.report.recommendations)} recommendations")


def generate_markdown_report(report: AuditReport, output_file: Path):
    """Generate markdown audit report."""
    lines = [
        "# Phase 0 and Orchestrator Wiring Audit Report",
        "",
        "**Generated**: 2025-12-12",
        "**Auditor**: audit_phase0_orchestrator_wiring.py",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"- **Phase 0 Modules**: {len(report.phase0_modules)}",
        f"- **Wiring Points**: {len(report.wiring_points)}",
        f"- **Issues Found**: {len(report.issues)}",
        f"- **Recommendations**: {len(report.recommendations)}",
        "",
        "---",
        "",
        "## 1. Phase 0 Modules",
        "",
        f"Found {len(report.phase0_modules)} modules in `src/canonic_phases/Phase_zero/`:",
        "",
    ]
    
    for module in sorted(report.phase0_modules):
        lines.append(f"- `{module}.py`")
    
    lines.extend([
        "",
        "---",
        "",
        "## 2. Orchestrator Phase 0 Implementation",
        "",
    ])
    
    if report.orchestrator_phase0_method:
        lines.append(f"✅ **Found**: `{report.orchestrator_phase0_method}` method in Orchestrator class")
    else:
        lines.append("❌ **Not Found**: No Phase 0 method in Orchestrator class")
    
    lines.extend([
        "",
        "---",
        "",
        "## 3. Wiring Points",
        "",
        f"Found {len(report.wiring_points)} wiring points between Phase 0 and orchestrator:",
        "",
    ])
    
    for wp in report.wiring_points:
        severity_icon = "🔴" if wp.severity == "critical" else "🟡" if wp.severity == "warning" else "🟢"
        lines.append(
            f"{severity_icon} **{wp.data_type}** - "
            f"`{wp.target_module}` imports from `{wp.source_module}` (line {wp.line_number})"
        )
    
    lines.extend([
        "",
        "---",
        "",
        "## 4. RuntimeConfig Propagation",
        "",
    ])
    
    if report.runtime_config_usage:
        lines.append(f"✅ Found {len(report.runtime_config_usage)} RuntimeConfig usages:")
        lines.append("")
        for usage in report.runtime_config_usage[:10]:  # Limit to 10
            lines.append(f"- Line {usage['line']}: `{usage['context']}`")
    else:
        lines.append("❌ RuntimeConfig not found in orchestrator")
    
    lines.extend([
        "",
        "---",
        "",
        "## 5. Factory Integration",
        "",
    ])
    
    for key, value in report.factory_integration.items():
        if isinstance(value, bool):
            icon = "✅" if value else "❌"
            lines.append(f"{icon} **{key}**: {value}")
        elif isinstance(value, list):
            lines.append(f"**{key}**: {len(value)} items")
    
    lines.extend([
        "",
        "---",
        "",
        "## 6. Exit Gates",
        "",
    ])
    
    for gate in report.exit_gates:
        lines.append(f"### {gate['file']}")
        lines.append("")
        if "functions" in gate:
            for func in gate["functions"]:
                lines.append(f"- `{func}()`")
        if "gate_checks" in gate:
            lines.append(f"- {len(gate['gate_checks'])} gate checks")
        lines.append("")
    
    lines.extend([
        "---",
        "",
        "## 7. Issues",
        "",
    ])
    
    # Group by severity
    critical = [i for i in report.issues if i["severity"] == "critical"]
    warnings = [i for i in report.issues if i["severity"] == "warning"]
    
    if critical:
        lines.append("### 🔴 Critical Issues")
        lines.append("")
        for issue in critical:
            lines.append(f"- **{issue['category']}**: {issue['message']}")
        lines.append("")
    
    if warnings:
        lines.append("### 🟡 Warnings")
        lines.append("")
        for issue in warnings:
            lines.append(f"- **{issue['category']}**: {issue['message']}")
        lines.append("")
    
    lines.extend([
        "---",
        "",
        "## 8. Recommendations",
        "",
    ])
    
    for i, rec in enumerate(report.recommendations, 1):
        lines.append(f"{i}. {rec}")
    
    lines.extend([
        "",
        "---",
        "",
        "## Conclusion",
        "",
        f"The audit identified **{len(report.issues)} issues** and provides **{len(report.recommendations)} recommendations** "
        "to improve the wiring between Phase 0 and the orchestrator.",
        "",
    ])
    
    # Write report
    output_file.write_text("\n".join(lines))


def main():
    """Main entry point."""
    auditor = Phase0OrchestratorAuditor()
    report = auditor.audit()
    
    # Save JSON report
    json_file = PROJECT_ROOT / "audit_phase0_orchestrator_wiring.json"
    with open(json_file, "w") as f:
        json.dump(report.to_dict(), f, indent=2)
    print(f"\n📄 JSON report saved to: {json_file}")
    
    # Generate markdown report
    md_file = PROJECT_ROOT / "PHASE_0_ORCHESTRATOR_WIRING_AUDIT.md"
    generate_markdown_report(report, md_file)
    print(f"📄 Markdown report saved to: {md_file}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("AUDIT SUMMARY")
    print("=" * 80)
    print(f"Phase 0 Modules: {len(report.phase0_modules)}")
    print(f"Wiring Points: {len(report.wiring_points)}")
    print(f"Issues: {len(report.issues)}")
    print(f"Recommendations: {len(report.recommendations)}")
    
    # Exit code based on critical issues
    critical_count = sum(1 for i in report.issues if i["severity"] == "critical")
    if critical_count > 0:
        print(f"\n❌ FAILED: {critical_count} critical issues found")
        return 1
    else:
        print("\n✅ PASSED: No critical issues found")
        return 0


if __name__ == "__main__":
    sys.exit(main())

"""
Determinism Certification Audit Tool
======================================

Comprehensive scanner and certifier for pipeline determinism.
Analyzes all phases (0-9) for non-deterministic operations and generates
a certification report.

Author: Determinism Certification Team
Version: 1.0.0
"""

from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent


@dataclass
class DeterminismIssue:
    """Represents a potential determinism violation."""
    
    file_path: str
    line_number: int
    issue_type: str
    code_snippet: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, ACCEPTABLE
    description: str
    recommendation: str


@dataclass
class PhaseAssessment:
    """Assessment of determinism for a single phase."""
    
    phase_id: str
    phase_name: str
    files_scanned: int
    total_lines: int
    issues: list[DeterminismIssue] = field(default_factory=list)
    determinism_score: float = 0.0
    certification_status: str = "NOT_CERTIFIED"  # CERTIFIED, CERTIFIED_WITH_NOTES, NOT_CERTIFIED
    
    def calculate_score(self) -> None:
        """Calculate determinism score based on issues."""
        if not self.issues:
            self.determinism_score = 1.0
            self.certification_status = "CERTIFIED"
            return
        
        critical_count = sum(1 for i in self.issues if i.severity == "CRITICAL")
        high_count = sum(1 for i in self.issues if i.severity == "HIGH")
        medium_count = sum(1 for i in self.issues if i.severity == "MEDIUM")
        low_count = sum(1 for i in self.issues if i.severity == "LOW")
        acceptable_count = sum(1 for i in self.issues if i.severity == "ACCEPTABLE")
        
        # Calculate penalty
        penalty = (
            critical_count * 0.25 +
            high_count * 0.10 +
            medium_count * 0.05 +
            low_count * 0.02 +
            acceptable_count * 0.00
        )
        
        self.determinism_score = max(0.0, 1.0 - penalty)
        
        if critical_count > 0:
            self.certification_status = "NOT_CERTIFIED"
        elif high_count > 3 or medium_count > 10:
            self.certification_status = "NOT_CERTIFIED"
        elif high_count > 0 or medium_count > 0 or low_count > 0:
            self.certification_status = "CERTIFIED_WITH_NOTES"
        else:
            self.certification_status = "CERTIFIED"


@dataclass
class CertificationReport:
    """Complete determinism certification report."""
    
    report_version: str = "1.0.0"
    report_timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    phases: list[PhaseAssessment] = field(default_factory=list)
    overall_score: float = 0.0
    overall_status: str = "NOT_CERTIFIED"
    summary: dict[str, Any] = field(default_factory=dict)
    
    def calculate_overall(self) -> None:
        """Calculate overall certification status."""
        if not self.phases:
            return
        
        self.overall_score = sum(p.determinism_score for p in self.phases) / len(self.phases)
        
        not_certified = sum(1 for p in self.phases if p.certification_status == "NOT_CERTIFIED")
        certified_with_notes = sum(1 for p in self.phases if p.certification_status == "CERTIFIED_WITH_NOTES")
        
        if not_certified > 0:
            self.overall_status = "NOT_CERTIFIED"
        elif certified_with_notes > 0:
            self.overall_status = "CERTIFIED_WITH_NOTES"
        else:
            self.overall_status = "CERTIFIED"
        
        # Generate summary
        total_issues = sum(len(p.issues) for p in self.phases)
        critical_issues = sum(
            sum(1 for i in p.issues if i.severity == "CRITICAL")
            for p in self.phases
        )
        
        self.summary = {
            "total_phases": len(self.phases),
            "certified_phases": sum(1 for p in self.phases if p.certification_status == "CERTIFIED"),
            "certified_with_notes_phases": certified_with_notes,
            "not_certified_phases": not_certified,
            "total_issues": total_issues,
            "critical_issues": critical_issues,
            "overall_score": round(self.overall_score, 3),
            "recommendation": self._generate_recommendation()
        }
    
    def _generate_recommendation(self) -> str:
        """Generate certification recommendation."""
        if self.overall_status == "CERTIFIED":
            return "Pipeline is CERTIFIED as fully deterministic. All phases meet requirements."
        elif self.overall_status == "CERTIFIED_WITH_NOTES":
            return "Pipeline is CERTIFIED WITH NOTES. Minor issues exist but do not compromise determinism guarantees."
        else:
            return "Pipeline is NOT CERTIFIED. Critical determinism issues must be addressed before certification."


class DeterminismScanner:
    """Scans Python code for non-deterministic patterns."""
    
    PATTERNS = {
        "uuid_generation": {
            "regex": r"uuid\.uuid4\(\)",
            "severity": "CRITICAL",
            "description": "Non-deterministic UUID generation",
            "recommendation": "Use deterministic ID generation based on correlation_id and context"
        },
        "datetime_now": {
            "regex": r"datetime\.now\(\)",
            "severity": "HIGH",
            "description": "Non-deterministic datetime.now() call",
            "recommendation": "Use datetime.utcnow() or inject clock for testing, document if used only for logging"
        },
        "time_time": {
            "regex": r"time\.time\(\)",
            "severity": "ACCEPTABLE",
            "description": "time.time() used for timing/metrics",
            "recommendation": "Acceptable for performance metrics, ensure not used in computation"
        },
        "random_unseeded": {
            "regex": r"random\.(choice|shuffle|sample|randint|uniform|gauss|random)\([^)]*\)",
            "severity": "HIGH",
            "description": "Potentially unseeded random operation",
            "recommendation": "Ensure random.seed() is called with deterministic seed before use"
        },
        "np_random_unseeded": {
            "regex": r"np\.random\.(choice|shuffle|permutation|rand|randn|randint|uniform)\([^)]*\)",
            "severity": "HIGH",
            "description": "Potentially unseeded numpy random operation",
            "recommendation": "Use np.random.default_rng(seed) or ensure np.random.seed() is called"
        },
        "dict_keys_iteration": {
            "regex": r"\.keys\(\)",
            "severity": "LOW",
            "description": "Dictionary keys iteration (potentially non-deterministic order)",
            "recommendation": "Use sorted(dict.keys()) if order matters"
        },
        "set_iteration": {
            "regex": r"for\s+\w+\s+in\s+\w+\s*:",
            "severity": "LOW",
            "description": "Potential set iteration (non-deterministic order)",
            "recommendation": "Use sorted(set) if order matters"
        },
        "asyncio_gather": {
            "regex": r"asyncio\.gather\(",
            "severity": "MEDIUM",
            "description": "asyncio.gather may complete tasks in non-deterministic order",
            "recommendation": "Ensure result processing is order-independent or explicitly order results"
        }
    }
    
    def __init__(self):
        self.issues: list[DeterminismIssue] = []
    
    def scan_file(self, file_path: Path) -> list[DeterminismIssue]:
        """Scan a single Python file for determinism issues."""
        issues: list[DeterminismIssue] = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, start=1):
                for pattern_name, pattern_info in self.PATTERNS.items():
                    if re.search(pattern_info["regex"], line):
                        # Check if it's in a comment or docstring
                        stripped = line.strip()
                        if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                            continue
                        
                        # Special handling for acceptable patterns
                        severity = pattern_info["severity"]
                        
                        # time.time() is acceptable for metrics/logging
                        if pattern_name == "time_time":
                            if any(keyword in line for keyword in ["start_time", "elapsed", "duration", "timestamp"]):
                                severity = "ACCEPTABLE"
                        
                        # datetime.now() is acceptable if used only for logging/display
                        if pattern_name == "datetime_now":
                            if any(keyword in line for keyword in ["timestamp", "isoformat", "created_at", "updated_at"]):
                                if "computation" not in line.lower() and "result" not in line.lower():
                                    severity = "ACCEPTABLE"
                        
                        issues.append(DeterminismIssue(
                            file_path=str(file_path.relative_to(PROJECT_ROOT)),
                            line_number=line_num,
                            issue_type=pattern_name,
                            code_snippet=line.strip(),
                            severity=severity,
                            description=pattern_info["description"],
                            recommendation=pattern_info["recommendation"]
                        ))
        
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
        
        return issues
    
    def scan_directory(self, directory: Path, pattern: str = "*.py") -> list[DeterminismIssue]:
        """Scan all Python files in a directory."""
        issues: list[DeterminismIssue] = []
        
        for file_path in directory.rglob(pattern):
            if file_path.is_file():
                # Skip __pycache__ and test files for now
                if "__pycache__" in str(file_path):
                    continue
                    
                file_issues = self.scan_file(file_path)
                issues.extend(file_issues)
        
        return issues


class DeterminismCertifier:
    """Main certification orchestrator."""
    
    PHASE_MAPPING = {
        "Phase_zero": "Phase 0: Validation & Bootstrap",
        "Phase_one": "Phase 1: Document Ingestion",
        "Phase_two": "Phase 2: Micro Analysis (300 Executors)",
        "Phase_three": "Phase 3: Scoring",
        "Phase_four_five_six_seven": "Phases 4-7: Hierarchical Aggregation",
        "Phase_eight": "Phase 8: Recommendations",
        "Phase_nine": "Phase 9: Report Assembly",
        "orchestration": "Orchestration Layer",
        "cross_cutting_infrastrucuiture": "Cross-Cutting Infrastructure",
        "methods_dispensary": "Methods Dispensary"
    }
    
    def __init__(self):
        self.scanner = DeterminismScanner()
        self.report = CertificationReport()
    
    def audit_phase(self, phase_dir: Path, phase_id: str) -> PhaseAssessment:
        """Audit a single phase directory."""
        print(f"Auditing {phase_id}...")
        
        if not phase_dir.exists():
            return PhaseAssessment(
                phase_id=phase_id,
                phase_name=self.PHASE_MAPPING.get(phase_id, phase_id),
                files_scanned=0,
                total_lines=0
            )
        
        issues = self.scanner.scan_directory(phase_dir)
        
        # Count files and lines
        files_scanned = len(list(phase_dir.rglob("*.py")))
        total_lines = 0
        
        for file_path in phase_dir.rglob("*.py"):
            if file_path.is_file() and "__pycache__" not in str(file_path):
                try:
                    total_lines += len(file_path.read_text(encoding='utf-8').split('\n'))
                except:
                    pass
        
        assessment = PhaseAssessment(
            phase_id=phase_id,
            phase_name=self.PHASE_MAPPING.get(phase_id, phase_id),
            files_scanned=files_scanned,
            total_lines=total_lines,
            issues=issues
        )
        
        assessment.calculate_score()
        return assessment
    
    def run_full_audit(self) -> CertificationReport:
        """Run complete determinism audit across all phases."""
        print("=" * 80)
        print("DETERMINISM CERTIFICATION AUDIT")
        print("=" * 80)
        print()
        
        src_dir = PROJECT_ROOT / "src"
        
        # Audit canonic phases
        phases_dir = src_dir / "canonic_phases"
        for phase_name in self.PHASE_MAPPING.keys():
            if phase_name in ["orchestration", "cross_cutting_infrastrucuiture", "methods_dispensary"]:
                continue
            
            phase_dir = phases_dir / phase_name
            assessment = self.audit_phase(phase_dir, phase_name)
            self.report.phases.append(assessment)
        
        # Audit orchestration
        orch_dir = src_dir / "orchestration"
        assessment = self.audit_phase(orch_dir, "orchestration")
        self.report.phases.append(assessment)
        
        # Audit cross-cutting infrastructure
        infra_dir = src_dir / "cross_cutting_infrastrucuiture"
        assessment = self.audit_phase(infra_dir, "cross_cutting_infrastrucuiture")
        self.report.phases.append(assessment)
        
        # Audit methods dispensary
        methods_dir = src_dir / "methods_dispensary"
        assessment = self.audit_phase(methods_dir, "methods_dispensary")
        self.report.phases.append(assessment)
        
        # Calculate overall scores
        self.report.calculate_overall()
        
        return self.report
    
    def generate_report_json(self, output_path: Path) -> None:
        """Generate JSON report."""
        report_dict = {
            "report_version": self.report.report_version,
            "report_timestamp": self.report.report_timestamp,
            "overall_score": self.report.overall_score,
            "overall_status": self.report.overall_status,
            "summary": self.report.summary,
            "phases": [
                {
                    "phase_id": p.phase_id,
                    "phase_name": p.phase_name,
                    "files_scanned": p.files_scanned,
                    "total_lines": p.total_lines,
                    "determinism_score": p.determinism_score,
                    "certification_status": p.certification_status,
                    "issue_count": len(p.issues),
                    "issues_by_severity": {
                        "CRITICAL": sum(1 for i in p.issues if i.severity == "CRITICAL"),
                        "HIGH": sum(1 for i in p.issues if i.severity == "HIGH"),
                        "MEDIUM": sum(1 for i in p.issues if i.severity == "MEDIUM"),
                        "LOW": sum(1 for i in p.issues if i.severity == "LOW"),
                        "ACCEPTABLE": sum(1 for i in p.issues if i.severity == "ACCEPTABLE")
                    },
                    "issues": [asdict(issue) for issue in p.issues]
                }
                for p in self.report.phases
            ]
        }
        
        output_path.write_text(json.dumps(report_dict, indent=2, ensure_ascii=False))
        print(f"\nJSON report written to: {output_path}")
    
    def generate_report_markdown(self, output_path: Path) -> None:
        """Generate Markdown certification report."""
        md = []
        
        md.append("# F.A.R.F.A.N Pipeline Determinism Certification Report")
        md.append("")
        md.append(f"**Version:** {self.report.report_version}")
        md.append(f"**Generated:** {self.report.report_timestamp}")
        md.append(f"**Overall Score:** {self.report.overall_score:.3f}")
        md.append(f"**Overall Status:** `{self.report.overall_status}`")
        md.append("")
        md.append("---")
        md.append("")
        
        # Executive Summary
        md.append("## Executive Summary")
        md.append("")
        for key, value in self.report.summary.items():
            md.append(f"- **{key.replace('_', ' ').title()}:** {value}")
        md.append("")
        md.append("---")
        md.append("")
        
        # Phase-by-Phase Analysis
        md.append("## Phase-by-Phase Analysis")
        md.append("")
        
        for phase in self.report.phases:
            md.append(f"### {phase.phase_name}")
            md.append("")
            md.append(f"**Phase ID:** `{phase.phase_id}`  ")
            md.append(f"**Status:** `{phase.certification_status}`  ")
            md.append(f"**Determinism Score:** {phase.determinism_score:.3f}  ")
            md.append(f"**Files Scanned:** {phase.files_scanned}  ")
            md.append(f"**Total Lines:** {phase.total_lines}  ")
            md.append("")
            
            if phase.issues:
                # Group by severity
                by_severity = {}
                for issue in phase.issues:
                    by_severity.setdefault(issue.severity, []).append(issue)
                
                md.append("#### Issues by Severity")
                md.append("")
                
                for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "ACCEPTABLE"]:
                    issues = by_severity.get(severity, [])
                    if issues:
                        md.append(f"##### {severity} ({len(issues)} issues)")
                        md.append("")
                        for issue in issues[:10]:  # Limit to first 10 per severity
                            md.append(f"- **{issue.file_path}:{issue.line_number}**")
                            md.append(f"  - Type: `{issue.issue_type}`")
                            md.append(f"  - Code: `{issue.code_snippet}`")
                            md.append(f"  - Recommendation: {issue.recommendation}")
                            md.append("")
                        
                        if len(issues) > 10:
                            md.append(f"  *(... and {len(issues) - 10} more)*")
                            md.append("")
            else:
                md.append("✅ **No determinism issues found**")
                md.append("")
            
            md.append("---")
            md.append("")
        
        # Recommendations
        md.append("## Recommendations")
        md.append("")
        md.append(f"{self.report.summary['recommendation']}")
        md.append("")
        
        if self.report.overall_status != "CERTIFIED":
            md.append("### Priority Actions")
            md.append("")
            md.append("1. **Address all CRITICAL issues** - These prevent certification")
            md.append("2. **Review HIGH severity issues** - May compromise reproducibility")
            md.append("3. **Document ACCEPTABLE patterns** - Ensure they don't affect computation")
            md.append("")
        
        output_path.write_text('\n'.join(md))
        print(f"Markdown report written to: {output_path}")
    
    def print_summary(self) -> None:
        """Print summary to console."""
        print()
        print("=" * 80)
        print("CERTIFICATION SUMMARY")
        print("=" * 80)
        print()
        print(f"Overall Score:  {self.report.overall_score:.3f}")
        print(f"Overall Status: {self.report.overall_status}")
        print()
        print(f"Phases Analyzed:           {self.report.summary['total_phases']}")
        print(f"  - Certified:             {self.report.summary['certified_phases']}")
        print(f"  - Certified with Notes:  {self.report.summary['certified_with_notes_phases']}")
        print(f"  - Not Certified:         {self.report.summary['not_certified_phases']}")
        print()
        print(f"Total Issues Found:        {self.report.summary['total_issues']}")
        print(f"  - Critical:              {self.report.summary['critical_issues']}")
        print()
        print(f"Recommendation: {self.report.summary['recommendation']}")
        print()
        print("=" * 80)


def main():
    """Run determinism certification audit."""
    certifier = DeterminismCertifier()
    
    # Run audit
    report = certifier.run_full_audit()
    
    # Print summary
    certifier.print_summary()
    
    # Generate reports
    json_path = PROJECT_ROOT / "determinism_certification_report.json"
    md_path = PROJECT_ROOT / "DETERMINISM_CERTIFICATION.md"
    
    certifier.generate_report_json(json_path)
    certifier.generate_report_markdown(md_path)
    
    print()
    print("Certification audit complete!")


if __name__ == "__main__":
    main()

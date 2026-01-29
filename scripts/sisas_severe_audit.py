#!/usr/bin/env python3
"""
SISAS SEVERE AUDIT SCRIPT
=========================

A comprehensive test that assesses:
1. FILE STATUS - Existence, size, emptiness
2. IMPORT STATUS - Can each module be imported?
3. WIRING - Are imports pointing to correct modules?
4. REDUNDANCY - Duplicate code/functionality detection
5. ORDER - Proper dependency chain

Author: FARFAN Pipeline Audit System
Date: 2026-01-20
"""

import os
import sys
import ast
import importlib
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict
import json

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

IRRIGATION_BASE = SRC_PATH / "farfan_pipeline" / "infrastructure" / "irrigation_using_signals"
SISAS_BASE = IRRIGATION_BASE / "SISAS"


@dataclass
class FileStatus:
    """Status of a single file."""
    path: str
    exists: bool = False
    size_bytes: int = 0
    line_count: int = 0
    is_empty: bool = True
    is_init: bool = False
    imports_ok: bool = False
    import_error: str = ""
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    content_hash: str = ""


@dataclass
class WiringIssue:
    """A wiring problem found."""
    file: str
    issue_type: str  # BAD_IMPORT, CIRCULAR, MISSING_DEP, WRONG_PATH
    description: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW


@dataclass
class RedundancyIssue:
    """A redundancy problem found."""
    files: List[str]
    issue_type: str  # DUPLICATE_CLASS, DUPLICATE_FUNCTION, SIMILAR_CONTENT
    description: str
    similarity_pct: float = 0.0


@dataclass
class AuditResult:
    """Complete audit result."""
    total_files: int = 0
    files_exist: int = 0
    files_missing: int = 0
    files_empty: int = 0
    imports_ok: int = 0
    imports_failed: int = 0
    wiring_issues: List[WiringIssue] = field(default_factory=list)
    redundancy_issues: List[RedundancyIssue] = field(default_factory=list)
    file_statuses: Dict[str, FileStatus] = field(default_factory=dict)
    

class SISASSevereAudit:
    """Severe audit of SISAS system."""
    
    # All files to audit (130 files from inventory)
    FILE_INVENTORY = {
        "root": [
            "__init__.py",
            "audit_signal_irrigation.py",
            "comprehensive_signal_audit.py",
            "ports.py",
            "visualization_generator.py",
        ],
        "extractors": [
            "__init__.py",
            "base_extractor.py",
            "causal_verb_extractor.py",
            "financial_chain_extractor.py",
            "institutional_ner_extractor.py",
        ],
        "SISAS": [
            "__init__.py",
            "main.py",
            "pdt_quality_integration.py",
            "signal_consumption.py",
            "signals.py",
        ],
        "SISAS/audit": [
            "__init__.py",
            "consumer_auditor.py",
            "consumption_proof.py",
            "decision_auditor.py",
            "questionnaire_access_audit.py",
            "signal_auditor.py",
        ],
        "SISAS/config": [
            "__init__.py",
            "bus_config.yaml",
            "irrigation_config.yaml",
            "vocabulary_config.yaml",
        ],
        "SISAS/consumers": [
            "__init__.py",
            "base_consumer.py",
        ],
        "SISAS/consumers/phase0": [
            "__init__.py",
            "phase0_90_02_bootstrap.py",
            "phase0_assembly_consumer.py",
            "providers.py",
            "wiring_types.py",
        ],
        "SISAS/consumers/phase1": [
            "__init__.py",
            "phase1_11_00_signal_enrichment.py",
            "phase1_13_00_cpp_ingestion.py",
            "phase1_extraction_consumer.py",
        ],
        "SISAS/consumers/phase2": [
            "__init__.py",
            "phase2_contract_consumer.py",
            "phase2_enrichment_consumer.py",
            "phase2_evidence_consumer.py",
            "phase2_executor_consumer.py",
            "phase2_factory_consumer.py",
        ],
        "SISAS/consumers/phase3": [
            "__init__.py",
            "phase3_10_00_signal_enriched_scoring.py",
            "phase3_validation_consumer.py",
        ],
        "SISAS/consumers/phase4": [
            "__init__.py",
            "phase4_aggregation_consumer.py",
            "phase4_dimension_consumer.py",
        ],
        "SISAS/consumers/phase5": [
            "__init__.py",
            "phase5_policy_area_consumer.py",
            "phase5_uncertainty_consumer.py",
        ],
        "SISAS/consumers/phase6": [
            "__init__.py",
            "phase6_cluster_consumer.py",
            "phase6_configuration_consumer.py",
        ],
        "SISAS/consumers/phase7": [
            "__init__.py",
            "phase7_meso_consumer.py",
        ],
        "SISAS/consumers/phase8": [
            "__init__.py",
            "phase8_30_00_signal_enriched_recommendations.py",
            "phase8_macro_consumer.py",
        ],
        "SISAS/consumers/phase9": [
            "__init__.py",
            "phase9_report_consumer.py",
            "phase9_reporting_consumer.py",
        ],
        "SISAS/core": [
            "__init__.py",
            "bus.py",
            "contracts.py",
            "event.py",
            "signal.py",
        ],
        "SISAS/harmonization": [
            "__init__.py",
            "harmonization_validator.py",
        ],
        "SISAS/integration": [
            "__init__.py",
            "signal_consumption_integration.py",
        ],
        "SISAS/irrigation": [
            "__init__.py",
            "irrigation_executor.py",
            "irrigation_map.py",
            "irrigation_validator.py",
        ],
        "SISAS/metadata": [
            "__init__.py",
            "signal_method_metadata.py",
        ],
        "SISAS/orchestration": [
            "__init__.py",
        ],
        "SISAS/schemas": [
            "__init__.py",
            "contract_schema.json",
            "event_schema.json",
            "irrigation_spec_schema.json",
            "signal_schema.json",
        ],
        "SISAS/scripts": [
            "__init__.py",
            "generate_contracts.py",
        ],
        "SISAS/semantic": [
            "__init__.py",
            "signal_semantic_expander.py",
        ],
        "SISAS/signal_types": [
            "__init__.py",
            "cache.py",
            "client.py",
            "registry.py",
        ],
        "SISAS/signal_types/types": [
            "__init__.py",
            "consumption.py",
            "contrast.py",
            "epistemic.py",
            "integrity.py",
            "operational.py",
            "orchestration.py",
            "structural.py",
        ],
        "SISAS/utils": [
            "__init__.py",
            "signal_resolution.py",
            "signal_scoring_context.py",
            "signal_semantic_context.py",
            "signal_validation_specs.py",
        ],
        "SISAS/validators": [
            "__init__.py",
            "depuration.py",
        ],
        "SISAS/vehicles": [
            "__init__.py",
            "base_vehicle.py",
            "signal_context_scoper.py",
            "signal_enhancement_integrator.py",
            "signal_evidence_extractor.py",
            "signal_intelligence_layer.py",
            "signal_irrigator.py",
            "signal_loader.py",
            "signal_quality_metrics.py",
            "signal_registry.py",
            "signals.py",
        ],
        "SISAS/vehicles/contrast": [
            "__init__.py",
            "contrast_signals_vehicle.py",
        ],
        "SISAS/vehicles/structural": [
            "__init__.py",
            "schema_validator_vehicle.py",
        ],
        "SISAS/vocabulary": [
            "__init__.py",
            "alignment_checker.py",
            "capability_vocabulary.py",
            "signal_vocabulary.py",
        ],
        "SISAS/wiring": [
            "__init__.py",
            "wiring_config.py",
        ],
        "SISAS/_deprecated": [
            "__init__.py",
            "signal_types.py",
            "signal_wiring_fixes.py",
        ],
    }
    
    # Known bad import patterns to detect
    BAD_IMPORT_PATTERNS = [
        ("..signals.types.", "..signal_types.types."),
        ("....signals.types.", "...signal_types.types."),
        ("from orchestration.orchestrator", "DEPRECATED"),
        ("from cross_cutting_infrastructure", "DEPRECATED"),
    ]
    
    def __init__(self):
        self.result = AuditResult()
        self.all_classes: Dict[str, List[str]] = defaultdict(list)  # class_name -> [files]
        self.all_functions: Dict[str, List[str]] = defaultdict(list)  # func_name -> [files]
        self.content_hashes: Dict[str, List[str]] = defaultdict(list)  # hash -> [files]
        
    def run(self) -> AuditResult:
        """Run the complete audit."""
        print("=" * 70)
        print("SISAS SEVERE AUDIT")
        print("=" * 70)
        print()
        
        # Phase 1: File Status
        print("[1/5] Checking file status...")
        self._check_file_status()
        
        # Phase 2: Import Status
        print("[2/5] Testing imports...")
        self._check_imports()
        
        # Phase 3: Wiring Analysis
        print("[3/5] Analyzing wiring...")
        self._check_wiring()
        
        # Phase 4: Redundancy Detection
        print("[4/5] Detecting redundancy...")
        self._check_redundancy()
        
        # Phase 5: Order/Dependency Check
        print("[5/5] Checking dependency order...")
        self._check_order()
        
        return self.result
    
    def _get_full_path(self, directory: str, filename: str) -> Path:
        """Get full path for a file."""
        if directory == "root":
            return IRRIGATION_BASE / filename
        return IRRIGATION_BASE / directory / filename
    
    def _check_file_status(self):
        """Check existence and basic status of all files."""
        for directory, files in self.FILE_INVENTORY.items():
            for filename in files:
                path = self._get_full_path(directory, filename)
                rel_path = str(path.relative_to(IRRIGATION_BASE))
                
                status = FileStatus(path=rel_path)
                self.result.total_files += 1
                
                if path.exists():
                    self.result.files_exist += 1
                    status.exists = True
                    status.size_bytes = path.stat().st_size
                    status.is_empty = status.size_bytes == 0
                    status.is_init = filename == "__init__.py"
                    
                    if status.is_empty:
                        self.result.files_empty += 1
                    
                    # Read content for Python files
                    if filename.endswith(".py") and not status.is_empty:
                        try:
                            content = path.read_text(encoding="utf-8")
                            status.line_count = len(content.splitlines())
                            status.content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
                            self.content_hashes[status.content_hash].append(rel_path)
                            
                            # Parse AST
                            self._parse_python_file(content, status)
                        except Exception as e:
                            status.import_error = f"Read error: {str(e)[:50]}"
                else:
                    self.result.files_missing += 1
                
                self.result.file_statuses[rel_path] = status
    
    def _parse_python_file(self, content: str, status: FileStatus):
        """Parse Python file to extract classes, functions, imports."""
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    status.classes.append(node.name)
                    self.all_classes[node.name].append(status.path)
                elif isinstance(node, ast.FunctionDef):
                    if not node.name.startswith("_"):
                        status.functions.append(node.name)
                        self.all_functions[node.name].append(status.path)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        status.imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        status.imports.append(node.module)
        except SyntaxError:
            pass  # File has syntax errors
    
    def _check_imports(self):
        """Test if each module can be imported."""
        for rel_path, status in self.result.file_statuses.items():
            if not status.exists or not rel_path.endswith(".py"):
                continue
            if status.is_empty:
                status.imports_ok = True  # Empty files are "ok"
                self.result.imports_ok += 1
                continue
            
            # Convert path to module name
            module_path = rel_path.replace("/", ".").replace(".py", "")
            full_module = f"farfan_pipeline.infrastructure.irrigation_using_signals.{module_path}"
            
            try:
                importlib.import_module(full_module)
                status.imports_ok = True
                self.result.imports_ok += 1
            except Exception as e:
                status.imports_ok = False
                status.import_error = str(e)[:100]
                self.result.imports_failed += 1
    
    def _check_wiring(self):
        """Check for wiring issues in imports."""
        for rel_path, status in self.result.file_statuses.items():
            if not status.exists or not rel_path.endswith(".py"):
                continue
            
            full_path = IRRIGATION_BASE / rel_path
            if not full_path.exists():
                continue
                
            try:
                content = full_path.read_text(encoding="utf-8")
            except:
                continue
            
            # Check for bad import patterns
            for bad_pattern, replacement in self.BAD_IMPORT_PATTERNS:
                if bad_pattern in content:
                    self.result.wiring_issues.append(WiringIssue(
                        file=rel_path,
                        issue_type="BAD_IMPORT",
                        description=f"Contains '{bad_pattern}' → should be '{replacement}'",
                        severity="HIGH" if replacement != "DEPRECATED" else "MEDIUM"
                    ))
            
            # Check for imports from non-existent modules
            for imp in status.imports:
                if "SISAS.signals.types" in imp:
                    self.result.wiring_issues.append(WiringIssue(
                        file=rel_path,
                        issue_type="WRONG_PATH",
                        description=f"Import from SISAS.signals.types (should be SISAS.signal_types.types)",
                        severity="CRITICAL"
                    ))
    
    def _check_redundancy(self):
        """Check for redundant/duplicate code."""
        # Check for duplicate class names
        for class_name, files in self.all_classes.items():
            if len(files) > 1 and class_name not in ("__init__", "Config"):
                self.result.redundancy_issues.append(RedundancyIssue(
                    files=files,
                    issue_type="DUPLICATE_CLASS",
                    description=f"Class '{class_name}' defined in {len(files)} files",
                ))
        
        # Check for files with identical content hash
        for hash_val, files in self.content_hashes.items():
            if len(files) > 1:
                # Exclude __init__.py files
                non_init = [f for f in files if not f.endswith("__init__.py")]
                if len(non_init) > 1:
                    self.result.redundancy_issues.append(RedundancyIssue(
                        files=non_init,
                        issue_type="SIMILAR_CONTENT",
                        description=f"Files have identical content hash: {hash_val}",
                        similarity_pct=100.0
                    ))
    
    def _check_order(self):
        """Check dependency order and circular imports."""
        # Build dependency graph
        dependencies: Dict[str, Set[str]] = {}
        
        for rel_path, status in self.result.file_statuses.items():
            if not status.exists or not rel_path.endswith(".py"):
                continue
            
            deps = set()
            for imp in status.imports:
                if "SISAS" in imp or "irrigation_using_signals" in imp:
                    deps.add(imp)
            dependencies[rel_path] = deps
        
        # Simple circular detection (would need more sophisticated algorithm for full detection)
        # For now just report files that import each other
        for file_a, deps_a in dependencies.items():
            for file_b, deps_b in dependencies.items():
                if file_a != file_b:
                    # Check if they reference each other's modules
                    a_module = file_a.replace("/", ".").replace(".py", "")
                    b_module = file_b.replace("/", ".").replace(".py", "")
                    
                    a_imports_b = any(b_module in d for d in deps_a)
                    b_imports_a = any(a_module in d for d in deps_b)
                    
                    if a_imports_b and b_imports_a:
                        # Avoid duplicate reports
                        if file_a < file_b:
                            self.result.wiring_issues.append(WiringIssue(
                                file=f"{file_a} <-> {file_b}",
                                issue_type="CIRCULAR",
                                description="Potential circular import detected",
                                severity="MEDIUM"
                            ))
    
    def print_report(self):
        """Print the audit report."""
        r = self.result
        
        print()
        print("=" * 70)
        print("AUDIT REPORT")
        print("=" * 70)
        
        # Summary
        print()
        print("SUMMARY")
        print("-" * 70)
        print(f"Total files inventoried: {r.total_files}")
        print(f"Files exist:            {r.files_exist} ({r.files_exist/r.total_files*100:.1f}%)")
        print(f"Files missing:          {r.files_missing}")
        print(f"Files empty:            {r.files_empty}")
        print(f"Imports OK:             {r.imports_ok}")
        print(f"Imports FAILED:         {r.imports_failed}")
        print(f"Wiring issues:          {len(r.wiring_issues)}")
        print(f"Redundancy issues:      {len(r.redundancy_issues)}")
        
        # Missing files
        if r.files_missing > 0:
            print()
            print("MISSING FILES")
            print("-" * 70)
            for path, status in r.file_statuses.items():
                if not status.exists:
                    print(f"  ❌ {path}")
        
        # Empty files (non-init)
        empty_non_init = [(p, s) for p, s in r.file_statuses.items() 
                          if s.exists and s.is_empty and not s.is_init]
        if empty_non_init:
            print()
            print("EMPTY FILES (non __init__.py)")
            print("-" * 70)
            for path, status in empty_non_init:
                print(f"  ⚠️  {path}")
        
        # Import failures
        if r.imports_failed > 0:
            print()
            print("IMPORT FAILURES")
            print("-" * 70)
            for path, status in r.file_statuses.items():
                if status.exists and not status.imports_ok and not status.is_empty:
                    print(f"  ❌ {path}")
                    print(f"     {status.import_error[:70]}")
        
        # Wiring issues
        if r.wiring_issues:
            print()
            print("WIRING ISSUES")
            print("-" * 70)
            by_severity = defaultdict(list)
            for issue in r.wiring_issues:
                by_severity[issue.severity].append(issue)
            
            for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                issues = by_severity.get(severity, [])
                if issues:
                    print(f"\n  [{severity}] ({len(issues)} issues)")
                    for issue in issues[:10]:  # Limit output
                        print(f"    • {issue.file}")
                        print(f"      {issue.issue_type}: {issue.description[:60]}")
                    if len(issues) > 10:
                        print(f"    ... and {len(issues) - 10} more")
        
        # Redundancy issues
        if r.redundancy_issues:
            print()
            print("REDUNDANCY ISSUES")
            print("-" * 70)
            for issue in r.redundancy_issues[:10]:
                print(f"  • {issue.issue_type}: {issue.description}")
                for f in issue.files[:3]:
                    print(f"    - {f}")
                if len(issue.files) > 3:
                    print(f"    ... and {len(issue.files) - 3} more")
        
        # Top classes by file count
        print()
        print("CLASSES DEFINED IN MULTIPLE FILES")
        print("-" * 70)
        multi_class = [(name, files) for name, files in self.all_classes.items() 
                       if len(files) > 1 and name not in ("Config", "__init__")]
        if multi_class:
            for name, files in sorted(multi_class, key=lambda x: -len(x[1]))[:10]:
                print(f"  {name}: {len(files)} files")
        else:
            print("  None found (good!)")
        
        # Final score
        print()
        print("=" * 70)
        print("FINAL SCORE")
        print("=" * 70)
        
        score = 100
        score -= r.files_missing * 2
        score -= r.imports_failed * 3
        score -= len([i for i in r.wiring_issues if i.severity == "CRITICAL"]) * 10
        score -= len([i for i in r.wiring_issues if i.severity == "HIGH"]) * 5
        score -= len(r.redundancy_issues) * 1
        score = max(0, score)
        
        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        elif score >= 60:
            grade = "D"
        else:
            grade = "F"
        
        print(f"Score: {score}/100 (Grade: {grade})")
        print()
        
        if score >= 80:
            print("✅ SISAS system is in GOOD shape")
        elif score >= 60:
            print("⚠️  SISAS system has MODERATE issues")
        else:
            print("❌ SISAS system has CRITICAL issues")
        
        return score


def main():
    """Main entry point."""
    audit = SISASSevereAudit()
    result = audit.run()
    score = audit.print_report()
    
    # Save detailed results to JSON
    output_path = PROJECT_ROOT / "artifacts" / "sisas_audit_result.json"
    output_path.parent.mkdir(exist_ok=True)
    
    # Convert to serializable format
    output_data = {
        "summary": {
            "total_files": result.total_files,
            "files_exist": result.files_exist,
            "files_missing": result.files_missing,
            "files_empty": result.files_empty,
            "imports_ok": result.imports_ok,
            "imports_failed": result.imports_failed,
            "wiring_issues": len(result.wiring_issues),
            "redundancy_issues": len(result.redundancy_issues),
            "score": score,
        },
        "file_statuses": {
            path: {
                "exists": s.exists,
                "size_bytes": s.size_bytes,
                "line_count": s.line_count,
                "is_empty": s.is_empty,
                "imports_ok": s.imports_ok,
                "import_error": s.import_error,
                "classes": s.classes,
                "functions": s.functions[:10],  # Limit
            }
            for path, s in result.file_statuses.items()
        },
        "wiring_issues": [
            {"file": i.file, "type": i.issue_type, "severity": i.severity, "desc": i.description}
            for i in result.wiring_issues
        ],
        "redundancy_issues": [
            {"files": i.files, "type": i.issue_type, "desc": i.description}
            for i in result.redundancy_issues
        ],
    }
    
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nDetailed results saved to: {output_path}")
    
    return 0 if score >= 60 else 1


if __name__ == "__main__":
    sys.exit(main())

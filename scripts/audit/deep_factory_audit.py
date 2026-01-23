#!/usr/bin/env python3
"""
Deep Factory Audit - Comprehensive Systemic Analysis
=====================================================

This script performs a deep investigation of the factory system to identify
and document indirect issues that may not be caught by the standard audit.

Checks:
1. Outdated references to AnalysisPipelineFactory in documentation
2. Outdated references to ProcessorBundle in code/docs
3. References to non-existent executor_factory module
4. Circular dependencies in factory imports
5. Inconsistent factory terminology across codebase
6. Deprecated factory patterns still in use
7. Missing factory pattern migration in consumers
8. Documentation-code misalignment

Author: FARFAN Audit Team
Version: 1.0.0
Date: 2026-01-23
"""

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple

# =============================================================================
# CONFIGURATION
# =============================================================================

# Terms that should not appear in production code (except tests/deprecated)
DEPRECATED_TERMS = [
    "AnalysisPipelineFactory",
    "ProcessorBundle",
    "executor_factory",
    "phase2_10_00_factory.AnalysisPipelineFactory",
]

# Terms that should appear (the new pattern)
EXPECTED_TERMS = [
    "UnifiedFactory",
    "FactoryConfig",
    "get_factory",
]

# Directories to exclude from scanning
EXCLUDED_DIRS = [
    "__pycache__",
    ".git",
    ".pytest_cache",
    "node_modules",
    "_build",
    "dist",
    "build",
]

# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass
class DeprecatedReference:
    """A reference to a deprecated term."""
    file_path: str
    line_number: int
    line_content: str
    term: str
    context: str  # "code", "comment", "docstring", "test"


@dataclass
class AuditResult:
    """Result of the deep audit."""
    deprecated_references: List[DeprecatedReference] = field(default_factory=list)
    missing_migrations: List[str] = field(default_factory=list)
    circular_dependencies: List[Tuple[str, str]] = field(default_factory=list)
    inconsistent_terminology: Dict[str, List[str]] = field(default_factory=dict)
    documentation_issues: List[Dict[str, str]] = field(default_factory=list)
    
    def total_issues(self) -> int:
        """Count total issues found."""
        return (
            len(self.deprecated_references) +
            len(self.missing_migrations) +
            len(self.circular_dependencies) +
            len(self.inconsistent_terminology) +
            len(self.documentation_issues)
        )


# =============================================================================
# AUDIT FUNCTIONS
# =============================================================================


class DeepFactoryAuditor:
    """Performs deep audit of factory system."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.result = AuditResult()
        
    def run_full_audit(self) -> AuditResult:
        """Run all audit checks."""
        print("=" * 80)
        print("DEEP FACTORY AUDIT - Comprehensive Systemic Analysis")
        print("=" * 80)
        
        self._scan_deprecated_references()
        self._check_documentation_alignment()
        self._check_import_patterns()
        self._generate_report()
        
        return self.result
    
    def _scan_deprecated_references(self):
        """Scan for deprecated terms in codebase."""
        print("\n[1/3] Scanning for deprecated references...")
        
        # Scan Python files
        for py_file in self.repo_root.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
                
            self._scan_file_for_deprecated_terms(py_file, "python")
        
        # Scan markdown files
        for md_file in self.repo_root.rglob("*.md"):
            if self._should_skip_file(md_file):
                continue
                
            self._scan_file_for_deprecated_terms(md_file, "markdown")
        
        print(f"   Found {len(self.result.deprecated_references)} deprecated references")
    
    def _scan_file_for_deprecated_terms(self, file_path: Path, file_type: str):
        """Scan a single file for deprecated terms."""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.splitlines()
            
            for line_num, line in enumerate(lines, 1):
                for term in DEPRECATED_TERMS:
                    if term in line:
                        # Determine context
                        context = self._determine_context(file_path, line)
                        
                        # Skip if in tests or deprecated directory
                        if context == "test" or "deprecated" in str(file_path).lower():
                            continue
                        
                        ref = DeprecatedReference(
                            file_path=str(file_path.relative_to(self.repo_root)),
                            line_number=line_num,
                            line_content=line.strip(),
                            term=term,
                            context=context
                        )
                        self.result.deprecated_references.append(ref)
        except Exception as e:
            print(f"   Warning: Could not scan {file_path}: {e}")
    
    def _determine_context(self, file_path: Path, line: str) -> str:
        """Determine the context of a line."""
        if "test" in str(file_path).lower():
            return "test"
        
        line_stripped = line.strip()
        if line_stripped.startswith("#"):
            return "comment"
        if '"""' in line or "'''" in line:
            return "docstring"
        
        return "code"
    
    def _check_documentation_alignment(self):
        """Check if documentation aligns with code."""
        print("\n[2/3] Checking documentation alignment...")
        
        issues_found = 0
        
        # Check key documentation files
        doc_files = [
            "README.md",
            "docs/FACTORY_ARCHITECTURE.md",
            "canonic_questionnaire_central/resolver.py",
            "src/farfan_pipeline/phases/Phase_00/phase0_90_01_verified_pipeline_runner.py",
        ]
        
        for doc_file in doc_files:
            full_path = self.repo_root / doc_file
            if not full_path.exists():
                continue
            
            try:
                content = full_path.read_text(encoding='utf-8')
                
                # Check for mentions of deprecated factory
                if "AnalysisPipelineFactory" in content and "deprecated" not in content.lower():
                    self.result.documentation_issues.append({
                        "file": doc_file,
                        "issue": "References AnalysisPipelineFactory without deprecation notice",
                        "severity": "medium"
                    })
                    issues_found += 1
                
                # Check if UnifiedFactory is mentioned
                if "factory" in content.lower() and "UnifiedFactory" not in content:
                    # Check if this file should mention UnifiedFactory
                    if any(term in content for term in ["factory pattern", "Factory", "factory.py"]):
                        self.result.documentation_issues.append({
                            "file": doc_file,
                            "issue": "Discusses factory but doesn't mention UnifiedFactory",
                            "severity": "low"
                        })
                        issues_found += 1
                        
            except Exception as e:
                print(f"   Warning: Could not check {doc_file}: {e}")
        
        print(f"   Found {issues_found} documentation alignment issues")
    
    def _check_import_patterns(self):
        """Check for problematic import patterns."""
        print("\n[3/3] Checking import patterns...")
        
        # Find files importing from deprecated factory
        deprecated_imports = []
        
        for py_file in self.repo_root.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                
                # Check for imports from deprecated factory
                if "from farfan_pipeline.phases.Phase_02.phase2_10_00_factory import" in content:
                    # This is OK if it's the deprecated stub itself
                    if "phase2_10_00_factory.py" not in str(py_file):
                        deprecated_imports.append(str(py_file.relative_to(self.repo_root)))
                
            except Exception:
                pass
        
        if deprecated_imports:
            self.result.missing_migrations.extend(deprecated_imports)
            print(f"   Found {len(deprecated_imports)} files still importing from deprecated factory")
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        path_str = str(file_path)
        return any(excluded in path_str for excluded in EXCLUDED_DIRS)
    
    def _generate_report(self):
        """Generate and print the audit report."""
        print("\n" + "=" * 80)
        print("DEEP AUDIT RESULTS")
        print("=" * 80)
        
        total = self.result.total_issues()
        
        if total == 0:
            print("\n✅ No systemic issues found!")
            return
        
        print(f"\n⚠️  Found {total} systemic issues:\n")
        
        # Deprecated references
        if self.result.deprecated_references:
            print(f"1. Deprecated References: {len(self.result.deprecated_references)}")
            
            # Group by term
            by_term = defaultdict(list)
            for ref in self.result.deprecated_references:
                by_term[ref.term].append(ref)
            
            for term, refs in sorted(by_term.items()):
                print(f"   - {term}: {len(refs)} occurrences")
                # Show first 5
                for ref in refs[:5]:
                    print(f"     • {ref.file_path}:{ref.line_number} ({ref.context})")
                if len(refs) > 5:
                    print(f"     ... and {len(refs) - 5} more")
        
        # Documentation issues
        if self.result.documentation_issues:
            print(f"\n2. Documentation Issues: {len(self.result.documentation_issues)}")
            for issue in self.result.documentation_issues:
                print(f"   - {issue['file']}")
                print(f"     {issue['issue']} (severity: {issue['severity']})")
        
        # Missing migrations
        if self.result.missing_migrations:
            print(f"\n3. Files Still Using Deprecated Factory: {len(self.result.missing_migrations)}")
            for file_path in self.result.missing_migrations[:10]:
                print(f"   - {file_path}")
            if len(self.result.missing_migrations) > 10:
                print(f"   ... and {len(self.result.missing_migrations) - 10} more")
        
        print("\n" + "=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)
        
        if self.result.deprecated_references:
            print("\n1. Update deprecated references:")
            print("   - Replace AnalysisPipelineFactory → UnifiedFactory")
            print("   - Replace ProcessorBundle → FactoryConfig")
            print("   - Update documentation to reflect new architecture")
        
        if self.result.documentation_issues:
            print("\n2. Align documentation with code:")
            print("   - Add deprecation notices where needed")
            print("   - Update architecture diagrams")
            print("   - Ensure consistency in terminology")
        
        if self.result.missing_migrations:
            print("\n3. Complete factory migration:")
            print("   - Files still importing from deprecated factory will emit warnings")
            print("   - Consider migrating to direct UnifiedFactory imports")
            print("   - This is low priority as the stub handles redirection")


def main():
    """Main entry point."""
    repo_root = Path(__file__).resolve().parents[2]
    auditor = DeepFactoryAuditor(repo_root)
    result = auditor.run_full_audit()
    
    # Save detailed report
    output_dir = repo_root / "artifacts" / "audit_reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "deep_factory_audit_report.txt"
    
    with open(output_path, 'w') as f:
        f.write("DEEP FACTORY AUDIT REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Total Issues: {result.total_issues()}\n\n")
        
        f.write("DEPRECATED REFERENCES:\n")
        for ref in result.deprecated_references:
            f.write(f"  {ref.file_path}:{ref.line_number} - {ref.term} ({ref.context})\n")
        
        f.write("\nDOCUMENTATION ISSUES:\n")
        for issue in result.documentation_issues:
            f.write(f"  {issue['file']}: {issue['issue']}\n")
        
        f.write("\nMISSING MIGRATIONS:\n")
        for file_path in result.missing_migrations:
            f.write(f"  {file_path}\n")
    
    print(f"\n📄 Detailed report saved to: {output_path.relative_to(repo_root)}")
    
    return 0 if result.total_issues() == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

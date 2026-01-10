#!/usr/bin/env python3
"""
Semantic Validator for GNEA

Validates semantic meaning and consistency of names across the FARFAN_MPP
repository. Ensures names are not only syntactically correct but also
semantically meaningful and consistent.

Document: FPN-GNEA-002
Version: 1.0.0
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class SemanticIssue(Enum):
    """Types of semantic validation issues."""
    MISLEADING_NAME = "MISLEADING_NAME"
    INCONSISTENT_TERMINOLOGY = "INCONSISTENT_TERMINOLOGY"
    ABBREVIATION_WITHOUT_DEFINITION = "ABBREVIATION_WITHOUT_DEFINITION"
    VAGUE_NAME = "VAGUE_NAME"
    DOMAIN_MISMATCH = "DOMAIN_MISMATCH"
    NOUN_VERB_CONFUSION = "NOUN_VERB_CONFUSION"


@dataclass
class SemanticViolation:
    """Represents a semantic naming violation."""
    filepath: Path
    issue_type: SemanticIssue
    name: str
    message: str
    suggestion: Optional[str] = None
    line_number: Optional[int] = None


class SemanticValidator:
    """
    Validates semantic meaning and consistency of names.

    This goes beyond syntactic validation to ensure names are:
    - Semantically meaningful
    - Consistent with domain terminology
    - Not misleading or vague
    - Following established conventions
    """

    # Domain-specific terminology dictionary
    DOMAIN_TERMS = {
        'phase': ['phase', 'stage', 'step', 'portion'],
        'executor': ['executor', 'runner', 'handler', 'processor'],
        'contract': ['contract', 'agreement', 'specification', 'schema'],
        'validation': ['validation', 'validator', 'verify', 'check'],
        'factory': ['factory', 'creator', 'builder', 'maker'],
        'registry': ['registry', 'register', 'catalog', 'index'],
        'nexus': ['nexus', 'hub', 'center', 'core'],
        'router': ['router', 'dispatcher', 'director', 'switch'],
        'config': ['config', 'configuration', 'settings', 'options'],
    }

    # Common abbreviations that should be avoided or documented
    PROBLEMATIC_ABBREVIATIONS = {
        'cfg': 'config',
        'ctx': 'context',
        'env': 'environment',
        'msg': 'message',
        'obj': 'object',
        'param': 'parameter',
        'proc': 'process',
        'resp': 'response',
        'req': 'request',
        'tmp': 'temporary',
        'val': 'value',
        'var': 'variable',
    }

    # Vague or generic names to avoid
    VAGUE_NAMES = {
        'data',
        'info',
        'item',
        'thing',
        'stuff',
        'manager',
        'helper',
        'util',
        'utils',
        'handler',
        'processor',
    }

    # Verbs that should be used for functions
    FUNCTION_VERBS = {
        'get', 'set', 'add', 'remove', 'create', 'delete', 'update',
        'fetch', 'load', 'save', 'store', 'find', 'search', 'filter',
        'validate', 'verify', 'check', 'test', 'run', 'execute',
        'process', 'handle', 'transform', 'convert', 'parse', 'format',
        'calculate', 'compute', 'derive', 'generate', 'build', 'construct',
    }

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path.cwd()
        self.violations: List[SemanticViolation] = []
        self.term_usage: Dict[str, List[str]] = {}
        self._initialize_term_usage()

    def _initialize_term_usage(self):
        """Initialize term usage tracking."""
        for term_group in self.DOMAIN_TERMS.values():
            for term in term_group:
                self.term_usage[term] = []

    def validate_file(self, filepath: Path) -> List[SemanticViolation]:
        """Validate semantic naming in a single file."""
        file_violations = []

        try:
            content = filepath.read_text()
            tree = ast.parse(content, filename=str(filepath))

            # Validate class names
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    file_violations.extend(self._validate_class_name(filepath, node))

                elif isinstance(node, ast.FunctionDef):
                    file_violations.extend(self._validate_function_name(filepath, node))

                elif isinstance(node, ast.Assign):
                    file_violations.extend(self._validate_variable_names(filepath, node))

        except (SyntaxError, UnicodeDecodeError):
            pass

        return file_violations

    def _validate_class_name(self, filepath: Path, node: ast.ClassDef) -> List[SemanticViolation]:
        """Validate class name for semantic issues."""
        violations = []
        name = node.name

        # Check for vague names
        if name.lower() in self.VAGUE_NAMES:
            violations.append(SemanticViolation(
                filepath=filepath,
                issue_type=SemanticIssue.VAGUE_NAME,
                name=name,
                message=f"Class name '{name}' is too vague or generic",
                suggestion="Use a more specific, descriptive name",
                line_number=node.lineno
            ))

        # Check for noun confusion (classes should be nouns)
        if self._looks_like_verb(name):
            violations.append(SemanticViolation(
                filepath=filepath,
                issue_type=SemanticIssue.NOUN_VERB_CONFUSION,
                name=name,
                message=f"Class name '{name}' appears to be a verb (classes should be nouns)",
                suggestion="Use noun form for class names",
                line_number=node.lineno
            ))

        # Track terminology usage
        self._track_term_usage(name.lower())

        return violations

    def _validate_function_name(self, filepath: Path, node: ast.FunctionDef) -> List[SemanticViolation]:
        """Validate function name for semantic issues."""
        violations = []
        name = node.name

        # Skip private/dunder methods
        if name.startswith('__') or name.startswith('_'):
            return violations

        # Check for vague names
        if name.lower() in self.VAGUE_NAMES:
            violations.append(SemanticViolation(
                filepath=filepath,
                issue_type=SemanticIssue.VAGUE_NAME,
                name=name,
                message=f"Function name '{name}' is too vague or generic",
                suggestion="Use a more specific, descriptive name",
                line_number=node.lineno
            ))

        # Check for verb usage (functions should be verbs)
        if not self._starts_with_verb(name):
            violations.append(SemanticViolation(
                filepath=filepath,
                issue_type=SemanticIssue.NOUN_VERB_CONFUSION,
                name=name,
                message=f"Function name '{name}' should start with a verb",
                suggestion=f"Consider: get_{name}, set_{name}, is_{name}, validate_{name}",
                line_number=node.lineno
            ))

        # Track terminology usage
        self._track_term_usage(name.lower())

        return violations

    def _validate_variable_names(self, filepath: Path, node: ast.Assign) -> List[SemanticViolation]:
        """Validate variable names for semantic issues."""
        violations = []

        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id

                # Skip constants (ALL_CAPS)
                if name.isupper():
                    continue

                # Check for problematic abbreviations
                for abbrev, full_form in self.PROBLEMATIC_ABBREVIATIONS.items():
                    if abbrev in name.lower() and name.lower() != full_form:
                        violations.append(SemanticViolation(
                            filepath=filepath,
                            issue_type=SemanticIssue.ABBREVIATION_WITHOUT_DEFINITION,
                            name=name,
                            message=f"Abbreviation '{abbrev}' in '{name}' should be expanded",
                            suggestion=f"Consider using '{full_form}' instead of '{abbrev}'",
                            line_number=node.lineno
                        ))

        return violations

    def _looks_like_verb(self, name: str) -> bool:
        """Check if a name looks like a verb."""
        # Remove common prefixes/suffixes
        base = name.lower()
        for prefix in ['get', 'set', 'is', 'has', 'can', 'should']:
            if base.startswith(prefix):
                return True
        return base in self.FUNCTION_VERBS

    def _starts_with_verb(self, name: str) -> bool:
        """Check if a function name starts with a verb."""
        parts = name.split('_')
        if not parts:
            return False
        return parts[0] in self.FUNCTION_VERBS

    def _track_term_usage(self, term: str) -> None:
        """Track usage of domain terms."""
        # Check if this term matches any of our domain terms
        for domain_term, variations in self.DOMAIN_TERMS.items():
            if term in variations:
                self.term_usage[term].append(domain_term)

    def validate_consistency(self) -> List[SemanticViolation]:
        """Validate terminology consistency across the repository."""
        violations = []

        # Check for inconsistent terminology usage
        for term, usages in self.term_usage.items():
            if len(set(usages)) > 1:
                violations.append(SemanticViolation(
                    filepath=Path.cwd(),  # Repository-level issue
                    issue_type=SemanticIssue.INCONSISTENT_TERMINOLOGY,
                    name=term,
                    message=f"Inconsistent use of '{term}' across different contexts: {set(usages)}",
                    suggestion="Standardize on a single term for this concept"
                ))

        return violations

    def get_violations(self) -> List[SemanticViolation]:
        """Get all collected violations."""
        return self.violations

    def print_report(self) -> None:
        """Print semantic validation report."""
        if not self.violations:
            print("✓ No semantic naming issues found")
            return

        print("\n" + "=" * 70)
        print("SEMANTIC VALIDATION REPORT")
        print("=" * 70)
        print(f"Total Issues: {len(self.violations)}")

        # Group by issue type
        by_type: Dict[SemanticIssue, List[SemanticViolation]] = {}
        for v in self.violations:
            if v.issue_type not in by_type:
                by_type[v.issue_type] = []
            by_type[v.issue_type].append(v)

        for issue_type, violations in by_type.items():
            print(f"\n{issue_type.value}: {len(violations)} occurrences")
            print("-" * 70)
            for v in violations[:5]:  # Show first 5
                rel_path = v.filepath.relative_to(self.repo_root)
                print(f"  {rel_path}:{v.line_number or '?'}")
                print(f"    {v.message}")
                if v.suggestion:
                    print(f"    💡 {v.suggestion}")
            if len(violations) > 5:
                print(f"  ... and {len(violations) - 5} more")

        print("=" * 70)


def main():
    """CLI entry point."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python semantic_validator.py <file_or_directory>")
        sys.exit(1)

    path = Path(sys.argv[1])
    validator = SemanticValidator()

    if path.is_file():
        violations = validator.validate_file(path)
        validator.violations.extend(violations)
    elif path.is_dir():
        for py_file in path.rglob("*.py"):
            violations = validator.validate_file(py_file)
            validator.violations.extend(violations)

    # Check consistency
    validator.violations.extend(validator.validate_consistency())

    validator.print_report()

    # Exit with error code if violations found
    sys.exit(1 if validator.violations else 0)


if __name__ == "__main__":
    main()

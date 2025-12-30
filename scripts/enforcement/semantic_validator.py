#!/usr/bin/env python3
"""
Semantic Name Validator for GNEA
Validates that module names semantically align with their content.

Document: FPN-GNEA-001
Version: 2.0.0
"""
from __future__ import annotations

import ast
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

__version__ = "2.0.0"


class SemanticValidator:
    """Validates semantic alignment between names and content."""

    TECHNICAL_KEYWORDS = {
        "factory": {"create", "build", "construct", "instantiate", "make"},
        "validator": {"validate", "check", "verify", "assert", "ensure"},
        "registry": {"register", "lookup", "get", "store", "cache"},
        "manager": {"manage", "handle", "control", "coordinate"},
        "executor": {"execute", "run", "process", "perform"},
        "router": {"route", "dispatch", "forward", "redirect"},
        "synchronizer": {"sync", "synchronize", "coordinate", "align"},
        "analyzer": {"analyze", "examine", "inspect", "evaluate"},
        "generator": {"generate", "produce", "create", "emit"},
        "loader": {"load", "read", "fetch", "retrieve"},
        "parser": {"parse", "extract", "interpret", "decode"},
        "transformer": {"transform", "convert", "map", "translate"},
        "handler": {"handle", "process", "manage", "deal"},
        "controller": {"control", "direct", "govern", "regulate"},
        "monitor": {"monitor", "watch", "observe", "track"},
        "profiler": {"profile", "measure", "benchmark", "time"},
        "carver": {"carve", "shape", "form", "mold", "synthesize"},
        "nexus": {"connect", "link", "join", "aggregate", "evidence"},
    }

    def __init__(self, threshold: float = 0.3):
        self.threshold = threshold
        self.results: List[Dict[str, Any]] = []

    def validate_file(self, filepath: Path) -> Dict[str, Any]:
        """Validate semantic alignment of a file."""
        if not filepath.exists() or filepath.suffix != ".py":
            return {"valid": True, "score": 1.0}

        try:
            content = filepath.read_text(encoding="utf-8")
            tree = ast.parse(content)
        except Exception as e:
            return {"valid": True, "score": 1.0, "error": str(e)}

        name_parts = self._extract_name_parts(filepath.name)
        content_semantics = self._extract_content_semantics(tree, content)

        alignment_score = self._calculate_alignment(name_parts, content_semantics)

        result = {
            "filepath": str(filepath),
            "name_parts": name_parts,
            "content_keywords": list(content_semantics),
            "alignment_score": alignment_score,
            "valid": alignment_score >= self.threshold,
            "suggestion": None,
        }

        if not result["valid"]:
            result["suggestion"] = self._suggest_better_name(name_parts, content_semantics)

        self.results.append(result)
        return result

    def _extract_name_parts(self, filename: str) -> Set[str]:
        """Extract semantic parts from filename."""
        name = filename.replace(".py", "")
        name = re.sub(r"^phase\d_\d{2}_\d{2}_", "", name)
        parts = set(name.split("_"))
        parts.discard("")
        return parts

    def _extract_content_semantics(self, tree: ast.AST, content: str) -> Set[str]:
        """Extract semantic keywords from file content."""
        keywords = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                keywords.update(self._split_name(node.name))
            elif isinstance(node, ast.ClassDef):
                keywords.update(self._split_name(node.name))
            elif isinstance(node, ast.Name):
                keywords.update(self._split_name(node.id))

        docstring_match = re.search(r'"""(.+?)"""', content, re.DOTALL)
        if docstring_match:
            docstring = docstring_match.group(1).lower()
            words = re.findall(r"\b[a-z]{4,}\b", docstring)
            keywords.update(words[:20])

        return keywords

    def _split_name(self, name: str) -> Set[str]:
        """Split camelCase or snake_case name into parts."""
        parts = set()
        snake_parts = name.lower().split("_")
        parts.update(snake_parts)

        camel_parts = re.findall(r"[A-Z][a-z]+|[a-z]+", name)
        parts.update(p.lower() for p in camel_parts)

        parts.discard("")
        return parts

    def _calculate_alignment(self, name_parts: Set[str], content_semantics: Set[str]) -> float:
        """Calculate semantic alignment score."""
        if not name_parts:
            return 1.0

        matches = 0
        total_weight = 0

        for part in name_parts:
            weight = 2 if part in self.TECHNICAL_KEYWORDS else 1
            total_weight += weight

            if part in content_semantics:
                matches += weight
            else:
                expected_keywords = self.TECHNICAL_KEYWORDS.get(part, set())
                if expected_keywords & content_semantics:
                    matches += weight * 0.8

        return matches / total_weight if total_weight > 0 else 1.0

    def _suggest_better_name(self, name_parts: Set[str], content_semantics: Set[str]) -> Optional[str]:
        """Suggest a better name based on content."""
        suggested_parts = []

        for keyword, expected_funcs in self.TECHNICAL_KEYWORDS.items():
            if expected_funcs & content_semantics:
                suggested_parts.append(keyword)
                if len(suggested_parts) >= 2:
                    break

        if suggested_parts:
            return "_".join(suggested_parts)
        return None

    def generate_report(self) -> Dict[str, Any]:
        """Generate validation report."""
        valid_count = sum(1 for r in self.results if r["valid"])
        total = len(self.results)

        return {
            "total_files": total,
            "valid_files": valid_count,
            "invalid_files": total - valid_count,
            "average_score": sum(r["alignment_score"] for r in self.results) / total if total > 0 else 1.0,
            "threshold": self.threshold,
            "results": self.results,
        }


def main():
    parser = argparse.ArgumentParser(description="GNEA Semantic Name Validator")
    parser.add_argument("files", nargs="*", help="Files to validate")
    parser.add_argument("--path", type=Path, default=Path.cwd(), help="Root path")
    parser.add_argument("--threshold", type=float, default=0.3, help="Alignment threshold")
    parser.add_argument("--output", type=Path, help="Output report path")

    args = parser.parse_args()

    validator = SemanticValidator(threshold=args.threshold)

    if args.files:
        filepaths = [Path(f) for f in args.files]
    else:
        filepaths = list(args.path.rglob("*.py"))

    for filepath in filepaths:
        if "__pycache__" in str(filepath) or ".git" in str(filepath):
            continue
        validator.validate_file(filepath)

    report = validator.generate_report()

    print("=" * 70)
    print("GNEA SEMANTIC VALIDATION REPORT")
    print("=" * 70)
    print(f"Total Files: {report['total_files']}")
    print(f"Valid: {report['valid_files']}")
    print(f"Invalid: {report['invalid_files']}")
    print(f"Average Score: {report['average_score']:.2f}")
    print("=" * 70)

    invalid = [r for r in report["results"] if not r["valid"]]
    for r in invalid[:10]:
        print(f"⚠️  {r['filepath']}")
        print(f"   Score: {r['alignment_score']:.2f}")
        if r["suggestion"]:
            print(f"   💡 Consider: {r['suggestion']}")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)

    sys.exit(0 if report["invalid_files"] == 0 else 1)


if __name__ == "__main__":
    main()

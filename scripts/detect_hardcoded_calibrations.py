#!/usr/bin/env python3
"""
Detect hardcoded calibration values in source code.
Exit code 0 = clean, Exit code 1 = violations found.
"""
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Violation:
    file: str
    line: int
    code: str
    pattern: str
    severity: str  # "CRITICAL" | "WARNING"


PATTERNS: list[tuple[re.Pattern[str], str, str]] = [
    (re.compile(r"(\w*score\w*)\s*=\s*(0\.\d+)"), "score_assignment", "CRITICAL"),
    (re.compile(r"(\w*threshold\w*)\s*=\s*(0\.\d+)"), "threshold_assignment", "CRITICAL"),
    (re.compile(r"(\w*weight\w*)\s*=\s*(0\.\d+)"), "weight_assignment", "CRITICAL"),
    (re.compile(r"(confidence)\s*=\s*(0\.\d+)"), "confidence_assignment", "CRITICAL"),
    (re.compile(r"if\s+\w+\s*[<>]=?\s*(0\.\d+)"), "inline_threshold_comparison", "WARNING"),
]

WHITELIST_COMMENTS = [
    "# FUNCTIONAL_CONSTANT",
    "# NOT_CALIBRATION",
    "# MATH_CONSTANT",
]

EXCLUDED_PATHS = [
    "src/core/calibration/layer_requirements.py",  # Canonical source
    "tests/",
    "scripts/detect_hardcoded_calibrations.py",  # This file
]


def is_excluded(filepath: Path) -> bool:
    path_str = str(filepath)
    return any(excl in path_str for excl in EXCLUDED_PATHS)


def is_whitelisted(line: str) -> bool:
    return any(wl in line for wl in WHITELIST_COMMENTS)


def scan_file(filepath: Path) -> list[Violation]:
    violations: list[Violation] = []
    if is_excluded(filepath):
        return violations
    try:
        content = filepath.read_text()
    except Exception:
        return violations
    for line_num, line in enumerate(content.splitlines(), 1):
        if is_whitelisted(line):
            continue
        for pattern, name, severity in PATTERNS:
            if pattern.search(line):
                violations.append(
                    Violation(
                        file=str(filepath),
                        line=line_num,
                        code=line.strip()[:80],
                        pattern=name,
                        severity=severity,
                    )
                )
    return violations


def main() -> int:
    src_dir = Path("src")
    if not src_dir.exists():
        print("ERROR: src/ directory not found")
        return 1
    all_violations: list[Violation] = []
    for py_file in src_dir.rglob("*.py"):
        all_violations.extend(scan_file(py_file))
    critical = [v for v in all_violations if v.severity == "CRITICAL"]
    warnings = [v for v in all_violations if v.severity == "WARNING"]
    print(f"SCAN COMPLETE: {len(all_violations)} total findings")
    print(f"  CRITICAL: {len(critical)}")
    print(f"  WARNING: {len(warnings)}")
    print("-" * 60)
    for v in all_violations:
        print(f"[{v.severity}] {v.file}:{v.line}")
        print(f"  Pattern: {v.pattern}")
        print(f"  Code: {v.code}")
    if critical:
        print(f"\nFAILED: {len(critical)} CRITICAL violations")
        return 1
    print("\nPASSED: No CRITICAL violations")
    return 0


if __name__ == "__main__":
    sys.exit(main())

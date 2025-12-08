"""Utility to detect and help migrate hardcoded calibration values.

This script scans Python files for potential hardcoded calibration values
and provides suggestions for migration to configuration files.

IMPLEMENTATION_WAVE: GOVERNANCE_WAVE_2024_12_07
WAVE_LABEL: CONFIG_GOVERNANCE_STRICT_FOLDERIZATION
"""

import re
from pathlib import Path

CALIBRATION_PATTERNS = [
    (r"\b(base_score|layer_score)\s*=\s*(\d+\.\d+)", "base_score"),
    (r"\b(weight)\s*=\s*(\d+\.\d+)", "weight"),
    (r"\b(threshold)\s*=\s*(\d+\.\d+)", "threshold"),
    (r"@([buqpdCm])\s*=\s*(\d+\.\d+)", "layer_symbol"),
    (r"\b(factor|coefficient|alpha|beta)\s*=\s*(\d+\.\d+)", "coefficient"),
]

EXCLUDE_DIRS = {
    "__pycache__",
    ".git",
    ".pytest_cache",
    "tests",
    "test",
    "venv",
    "env",
    ".venv",
    "farfan-env",
}

EXCLUDE_FILES = {
    "test_",
    "_test.py",
}


def should_exclude(path: Path) -> bool:
    """Check if path should be excluded from scanning."""
    for part in path.parts:
        if part in EXCLUDE_DIRS:
            return True

    for pattern in EXCLUDE_FILES:
        if pattern in path.name:
            return True

    return False


def scan_file(file_path: Path) -> list[tuple[int, str, str, str]]:
    """Scan file for hardcoded calibration values.

    Returns:
        List of (line_num, line_content, value_type, value) tuples
    """
    findings = []

    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        for line_num, line in enumerate(lines, start=1):
            if "# EXEMPT" in line or "assert" in line:
                continue

            for pattern, value_type in CALIBRATION_PATTERNS:
                matches = re.finditer(pattern, line)
                for match in matches:
                    value = (
                        match.group(2) if len(match.groups()) > 1 else match.group(1)
                    )
                    findings.append((line_num, line.strip(), value_type, value))

    except Exception as e:
        print(f"Warning: Could not scan {file_path}: {e}")

    return findings


def suggest_config_location(value_type: str, _value: str) -> str:
    """Suggest appropriate config file for value type."""
    suggestions = {
        "base_score": "calibration/runtime_layers.json",
        "layer_symbol": "calibration/runtime_layers.json",
        "weight": "calibration/intrinsic_calibration_rubric.json",
        "threshold": "calibration/unit_transforms.json",
        "coefficient": "calibration/unit_transforms.json",
    }
    return suggestions.get(value_type, "calibration/intrinsic_calibration.json")


def generate_migration_report(
    findings_by_file: dict[Path, list[tuple[int, str, str, str]]]
) -> str:
    """Generate markdown migration report."""
    report = ["# Hardcoded Calibration Values Migration Report", ""]
    report.append(f"Total files with hardcoded values: {len(findings_by_file)}")
    report.append("")

    for file_path, findings in sorted(findings_by_file.items()):
        report.append(f"## {file_path}")
        report.append("")

        for line_num, line, value_type, value in findings:
            report.append(f"**Line {line_num}**: `{value_type}` = `{value}`")
            report.append("```python")
            report.append(line)
            report.append("```")
            report.append("")

            config_file = suggest_config_location(value_type, value)
            report.append(f"**Suggestion**: Move to `{config_file}`")
            report.append("")
            report.append("**Migration code:**")
            report.append("```python")
            report.append("from system.config.config_manager import ConfigManager")
            report.append("config = ConfigManager()")
            report.append(f"data = config.load_config_json('{config_file}')")
            report.append("# Access value from data structure")
            report.append("```")
            report.append("")
            report.append("---")
            report.append("")

    return "\n".join(report)


def main() -> None:
    """Main entry point for migration utility."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Scan for hardcoded calibration values"
    )
    parser.add_argument(
        "path", nargs="?", default=".", help="Path to scan (default: current directory)"
    )
    parser.add_argument("--output", "-o", help="Output report file (default: stdout)")

    args = parser.parse_args()

    scan_path = Path(args.path)

    print("=" * 80)
    print("Hardcoded Calibration Values Scanner")
    print("=" * 80)
    print(f"Scanning: {scan_path.absolute()}")
    print()

    findings_by_file: dict[Path, list[tuple[int, str, str, str]]] = {}

    if scan_path.is_file():
        files: list[Path] = [scan_path]
    else:
        files = list(scan_path.rglob("*.py"))

    scanned_count = 0
    for file_path in files:
        if should_exclude(file_path):
            continue

        findings = scan_file(file_path)
        if findings:
            findings_by_file[file_path] = findings

        scanned_count += 1

    print(f"Scanned {scanned_count} Python files")
    print(f"Found hardcoded values in {len(findings_by_file)} files")
    print()

    if not findings_by_file:
        print("✓ No hardcoded calibration values found!")
        return

    total_findings = sum(len(f) for f in findings_by_file.values())
    print(f"Total hardcoded values: {total_findings}")
    print()

    print("Files with hardcoded values:")
    for file_path, findings in sorted(findings_by_file.items()):
        print(f"  {file_path}: {len(findings)} value(s)")

    print()
    print("=" * 80)

    report = generate_migration_report(findings_by_file)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(report, encoding="utf-8")
        print(f"Report written to: {output_path}")
    else:
        print()
        print(report)


if __name__ == "__main__":
    main()

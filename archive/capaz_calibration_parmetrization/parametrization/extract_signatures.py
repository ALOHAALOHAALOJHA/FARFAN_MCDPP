#!/usr/bin/env python3
"""
CLI tool for extracting method signatures from the codebase

Usage:
    python extract_signatures.py
    python extract_signatures.py --output-dir ./artifacts
    python extract_signatures.py --patterns "**/executors.py" "**/methods_dispensary/**/*.py"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from method_signature_extractor import MethodSignatureExtractor


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract method signatures and detect hardcoded parameters"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory for generated files (default: parametrization directory)"
    )
    parser.add_argument(
        "--patterns",
        nargs="+",
        default=None,
        help="File patterns to scan (default: all executors and methods)"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root directory (default: auto-detect)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.repo_root:
        repo_root = args.repo_root.resolve()
    else:
        repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent

    if not repo_root.exists():
        print(f"Error: Repository root does not exist: {repo_root}", file=sys.stderr)
        return 1

    extractor = MethodSignatureExtractor(repo_root)

    if args.patterns:
        extractor.scan_repository(include_patterns=args.patterns)
    else:
        extractor.scan_repository()

    if args.output_dir:
        output_dir = args.output_dir.resolve()
    else:
        output_dir = repo_root / "src" / "cross_cutting_infrastrucuture" / "capaz_calibration_parmetrization" / "parametrization"

    output_dir.mkdir(parents=True, exist_ok=True)

    signatures_path = output_dir / "method_signatures.json"
    extractor.export_signatures(signatures_path)

    migration_path = output_dir / "hardcoded_migration_report.json"
    extractor.export_hardcoded_migration_report(migration_path)

    summary = extractor.generate_summary_report()
    print("\n" + "=" * 60)
    print("METHOD SIGNATURE EXTRACTION SUMMARY")
    print("=" * 60)
    for key, value in summary.items():
        print(f"  {key:.<50} {value}")
    print("=" * 60)
    print(f"\nOutput files:")
    print(f"  Signatures: {signatures_path}")
    print(f"  Migration report: {migration_path}")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Unified Signature-Based Parametrization Analysis Pipeline

Orchestrates the complete analysis:
1. Extract method signatures from codebase
2. Detect hardcoded parameters
3. Analyze output ranges and patterns
4. Generate migration recommendations
5. Export all results

Usage:
    python run_signature_analysis.py
    python run_signature_analysis.py --output-dir ./artifacts
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from method_signature_extractor import MethodSignatureExtractor
from signature_analyzer import analyze_signatures

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_full_analysis(
    repo_root: Path,
    output_dir: Path,
    include_patterns: list[str] | None = None
) -> bool:
    logger.info("=" * 70)
    logger.info("SIGNATURE-BASED PARAMETRIZATION ANALYSIS")
    logger.info("=" * 70)

    logger.info(f"Repository root: {repo_root}")
    logger.info(f"Output directory: {output_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("\n[Step 1/4] Extracting method signatures...")
    extractor = MethodSignatureExtractor(repo_root)

    if include_patterns:
        extractor.scan_repository(include_patterns=include_patterns)
    else:
        extractor.scan_repository()

    signatures_path = output_dir / "method_signatures.json"
    extractor.export_signatures(signatures_path)

    migration_path = output_dir / "hardcoded_migration_report.json"
    extractor.export_hardcoded_migration_report(migration_path)

    summary = extractor.generate_summary_report()
    logger.info("[Step 1/4] Complete")
    logger.info(f"  Total methods scanned: {summary['total_methods']}")
    logger.info(f"  Hardcoded parameters found: {summary['total_hardcoded_parameters']}")

    logger.info("\n[Step 2/4] Analyzing signatures...")
    analysis_path = output_dir / "signature_analysis.json"
    try:
        analyze_signatures(signatures_path, analysis_path)
        logger.info("[Step 2/4] Complete")
    except Exception as e:
        logger.error(f"[Step 2/4] Failed: {e}")
        return False

    logger.info("\n[Step 3/4] Generating summary report...")
    summary_path = output_dir / "analysis_summary.txt"
    generate_text_summary(summary, signatures_path, analysis_path, summary_path)
    logger.info("[Step 3/4] Complete")

    logger.info("\n[Step 4/4] Generating migration config template...")
    config_template_path = output_dir / "COHORT_2024_executor_config_template.json"
    generate_config_template(migration_path, config_template_path)
    logger.info("[Step 4/4] Complete")

    logger.info("\n" + "=" * 70)
    logger.info("ANALYSIS COMPLETE")
    logger.info("=" * 70)
    logger.info("\nGenerated files:")
    logger.info(f"  1. Method signatures:       {signatures_path.name}")
    logger.info(f"  2. Migration report:        {migration_path.name}")
    logger.info(f"  3. Signature analysis:      {analysis_path.name}")
    logger.info(f"  4. Summary report:          {summary_path.name}")
    logger.info(f"  5. Config template:         {config_template_path.name}")
    logger.info("=" * 70 + "\n")

    return True


def generate_text_summary(
    summary: dict,
    signatures_path: Path,
    analysis_path: Path,
    output_path: Path
) -> None:
    import json

    with open(signatures_path, "r") as f:
        sig_data = json.load(f)

    with open(analysis_path, "r") as f:
        analysis_data = json.load(f)

    lines = [
        "=" * 70,
        "SIGNATURE-BASED PARAMETRIZATION ANALYSIS - SUMMARY REPORT",
        "=" * 70,
        "",
        "COHORT_2024 - REFACTOR_WAVE_2024_12",
        "",
        "=" * 70,
        "EXTRACTION STATISTICS",
        "=" * 70,
        "",
    ]

    for key, value in summary.items():
        lines.append(f"  {key.replace('_', ' ').title():<45} {value:>10}")

    lines.extend([
        "",
        "=" * 70,
        "PARAMETER PATTERNS",
        "=" * 70,
        "",
    ])

    patterns = analysis_data.get("parameter_patterns", {})
    for pattern_type, params in patterns.items():
        lines.append(f"  {pattern_type.replace('_', ' ').title():<45} {len(params):>10}")

    lines.extend([
        "",
        "=" * 70,
        "OUTPUT RANGE INFERENCES",
        "=" * 70,
        "",
    ])

    output_ranges = analysis_data.get("output_range_inferences", {})
    lines.append(f"  Total inferences: {len(output_ranges)}")

    confidence_dist = {"high": 0, "medium": 0, "low": 0}
    for inference in output_ranges.values():
        conf = inference.get("confidence", 0)
        if conf >= 0.8:
            confidence_dist["high"] += 1
        elif conf >= 0.5:
            confidence_dist["medium"] += 1
        else:
            confidence_dist["low"] += 1

    lines.append(f"    High confidence (≥0.8):   {confidence_dist['high']}")
    lines.append(f"    Medium confidence (≥0.5): {confidence_dist['medium']}")
    lines.append(f"    Low confidence (<0.5):    {confidence_dist['low']}")

    lines.extend([
        "",
        "=" * 70,
        "TOP MIGRATION PRIORITIES",
        "=" * 70,
        "",
    ])

    migration_priorities = analysis_data.get("migration_priorities", [])
    for i, item in enumerate(migration_priorities[:10], 1):
        lines.append(f"  {i:2d}. {item['signature']}")
        lines.append(f"      Parameter: {item['parameter']} = {item['value']}")
        lines.append(f"      Priority:  {item['priority_score']}")
        lines.append("")

    lines.extend([
        "=" * 70,
        "END OF REPORT",
        "=" * 70,
    ])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def generate_config_template(migration_path: Path, output_path: Path) -> None:
    import json

    with open(migration_path, "r") as f:
        migration_data = json.load(f)

    template = {
        "_cohort_metadata": {
            "cohort_id": "COHORT_2024",
            "creation_date": "2024-12-15T00:00:00+00:00",
            "wave_version": "REFACTOR_WAVE_2024_12",
            "description": "Template for migrating hardcoded parameters to configuration"
        },
        "_note": "Replace null values with appropriate configuration values",
        "parameters": {}
    }

    candidates = migration_data.get("migration_candidates", [])
    for candidate in candidates[:20]:
        key = candidate["suggested_key"]
        template["parameters"][key] = {
            "value": None,
            "original_value": candidate["hardcoded_value"],
            "type": candidate["hardcoded_type"],
            "source": {
                "module": candidate["module"],
                "class": candidate["class"],
                "method": candidate["method"],
                "line": candidate["line_number"]
            }
        }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2, ensure_ascii=False)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run complete signature-based parametrization analysis"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory for generated files"
    )
    parser.add_argument(
        "--patterns",
        nargs="+",
        default=None,
        help="File patterns to scan"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root directory"
    )

    args = parser.parse_args()

    if args.repo_root:
        repo_root = args.repo_root.resolve()
    else:
        repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent

    if args.output_dir:
        output_dir = args.output_dir.resolve()
    else:
        output_dir = repo_root / "src" / "cross_cutting_infrastrucuture" / "capaz_calibration_parmetrization" / "parametrization"

    success = run_full_analysis(repo_root, output_dir, args.patterns)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

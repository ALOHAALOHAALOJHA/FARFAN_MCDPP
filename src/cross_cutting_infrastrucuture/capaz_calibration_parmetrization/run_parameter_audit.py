#!/usr/bin/env python3
"""
Comprehensive Parameter Audit Runner

Orchestrates complete hardcoded parameter audit including:
1. AST-based parameter scanning across entire codebase
2. Executor-specific parameter validation
3. Cross-reference with COHORT_2024 configuration files
4. Unified reporting with certification status

Usage:
    python run_parameter_audit.py
    python run_parameter_audit.py --output-dir custom/path
    python run_parameter_audit.py --verbose
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from hardcoded_parameter_scanner import run_audit, AuditStatistics
from executor_parameter_validator import validate_executors

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )


def generate_unified_report(
    stats: AuditStatistics,
    executor_violations: int,
    output_dir: Path
) -> None:
    """Generate unified certification report combining all audits."""
    report_path = output_dir / "CERTIFICATION_SUMMARY.md"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Parameter Governance Certification Summary\n\n")
        f.write(f"**Generated:** {datetime.utcnow().isoformat()}Z\n\n")
        
        f.write("---\n\n")
        
        f.write("## 🎯 Certification Status\n\n")
        
        overall_pass = (stats.critical_violations == 0 and executor_violations == 0)
        
        if overall_pass:
            f.write("### ✅ **CERTIFICATION: PASSED**\n\n")
            f.write("All critical requirements met:\n")
            f.write("- ✅ Zero critical calibration violations\n")
            f.write("- ✅ All executors load parameters from configuration\n")
            f.write("- ✅ No hardcoded weights, scores, or thresholds in core code\n\n")
        else:
            f.write("### ❌ **CERTIFICATION: FAILED**\n\n")
            f.write("Critical violations requiring immediate attention:\n")
            if stats.critical_violations > 0:
                f.write(f"- ❌ {stats.critical_violations} critical parameter violations\n")
            if executor_violations > 0:
                f.write(f"- ❌ {executor_violations} executor parameter violations\n")
            f.write("\n")
        
        f.write("---\n\n")
        
        f.write("## 📊 Audit Metrics\n\n")
        
        f.write("### General Code Scan\n\n")
        f.write(f"- **Files Scanned:** {stats.total_files_scanned}\n")
        f.write(f"- **Lines Scanned:** {stats.total_lines_scanned:,}\n")
        f.write(f"- **Total Violations:** {stats.violations_found}\n")
        f.write(f"- **Compliance Rate:** {stats.compliance_percentage}%\n\n")
        
        f.write("### Violation Breakdown\n\n")
        f.write(f"| Severity | Count | Description |\n")
        f.write(f"|----------|-------|-------------|\n")
        f.write(f"| CRITICAL | {stats.critical_violations} | Calibration weights/scores |\n")
        f.write(f"| HIGH | {stats.high_violations} | Thresholds/gates |\n")
        f.write(f"| MEDIUM | {stats.medium_violations} | Runtime parameters |\n")
        f.write(f"| LOW | {stats.low_violations} | Minor issues |\n\n")
        
        f.write("### Executor Validation\n\n")
        f.write(f"- **Executor Violations:** {executor_violations}\n")
        if executor_violations == 0:
            f.write("- **Status:** ✅ All executors properly configured\n\n")
        else:
            f.write("- **Status:** ❌ Executors have hardcoded parameters\n\n")
        
        f.write("---\n\n")
        
        f.write("## 📋 Configuration Registry\n\n")
        f.write("The following COHORT_2024 configuration files are recognized:\n\n")
        f.write("### Calibration Files\n")
        f.write("- `COHORT_2024_intrinsic_calibration.json` - Base layer scores and weights\n")
        f.write("- `COHORT_2024_fusion_weights.json` - Layer fusion parameters\n")
        f.write("- `COHORT_2024_method_compatibility.json` - Method compatibility scores\n")
        f.write("- `COHORT_2024_runtime_layers.json` - Runtime layer computations\n\n")
        
        f.write("### Parametrization Files\n")
        f.write("- `COHORT_2024_executor_config.json` - Executor runtime parameters\n")
        f.write("- Environment variables via `os.getenv()` or `ExecutorConfig`\n\n")
        
        f.write("---\n\n")
        
        f.write("## 🔍 Detailed Reports\n\n")
        f.write("For detailed violation information, see:\n\n")
        f.write("- [`violations_audit_report.md`](violations_audit_report.md) - "
               "Complete parameter violation details\n")
        f.write("- [`violations_audit_report.json`](violations_audit_report.json) - "
               "Machine-readable violation data\n")
        f.write("- [`executor_parameter_validation.md`](executor_parameter_validation.md) - "
               "Executor-specific violations\n\n")
        
        f.write("---\n\n")
        
        f.write("## 🚀 Remediation Guidance\n\n")
        
        if stats.critical_violations > 0:
            f.write("### Priority 1: Critical Violations (BLOCKING)\n\n")
            f.write("**Action Required:** Migrate all hardcoded calibration weights and scores "
                   "to COHORT_2024 configuration files.\n\n")
            f.write("**Steps:**\n")
            f.write("1. Review `violations_audit_report.md` for all CRITICAL violations\n")
            f.write("2. Add missing weights/scores to appropriate COHORT_2024 JSON files\n")
            f.write("3. Update code to load values via `CalibrationOrchestrator` or parameter loaders\n")
            f.write("4. Re-run audit to verify fixes\n\n")
        
        if stats.high_violations > 0:
            f.write("### Priority 2: High Violations\n\n")
            f.write("**Action Required:** Move threshold values to configuration.\n\n")
            f.write("**Steps:**\n")
            f.write("1. Identify threshold usage patterns\n")
            f.write("2. Define thresholds in `COHORT_2024_intrinsic_calibration.json`\n")
            f.write("3. Load via configuration system\n\n")
        
        if executor_violations > 0:
            f.write("### Priority 3: Executor Parameter Violations\n\n")
            f.write("**Action Required:** Refactor executors to use ExecutorConfig.\n\n")
            f.write("**Steps:**\n")
            f.write("1. Review `executor_parameter_validation.md`\n")
            f.write("2. Replace hardcoded parameters with config loads:\n")
            f.write("   ```python\n")
            f.write("   # Before\n")
            f.write("   self.timeout = 300\n\n")
            f.write("   # After\n")
            f.write("   self.timeout = config.get('timeout', 300)\n")
            f.write("   ```\n")
            f.write("3. Update `COHORT_2024_executor_config.json` as needed\n\n")
        
        if stats.medium_violations > 0:
            f.write("### Priority 4: Medium Violations\n\n")
            f.write("**Action Recommended:** Migrate runtime parameters to configuration "
                   "or environment variables.\n\n")
        
        if overall_pass:
            f.write("### ✅ All Critical Requirements Met\n\n")
            f.write("Congratulations! The codebase meets certification requirements.\n\n")
            f.write("**Optional Improvements:**\n")
            if stats.medium_violations > 0:
                f.write(f"- Address {stats.medium_violations} medium-priority violations\n")
            if stats.low_violations > 0:
                f.write(f"- Address {stats.low_violations} low-priority violations\n")
            f.write("\n")
        
        f.write("---\n\n")
        
        f.write("## 📚 References\n\n")
        f.write("- **Configuration Governance:** See `CALIBRATION_INTEGRATION.md`\n")
        f.write("- **COHORT_2024 Manifest:** See `COHORT_MANIFEST.json`\n")
        f.write("- **Parameter Loading:** See `parameter_loader.py` and `ExecutorConfig`\n\n")
        
        f.write("---\n\n")
        f.write("*Generated by Comprehensive Parameter Audit System*\n")
    
    logger.info(f"Unified certification report: {report_path}")


def main() -> int:
    """Main audit runner."""
    parser = argparse.ArgumentParser(
        description="Run comprehensive hardcoded parameter audit"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory for reports (default: artifacts/audit_reports)"
    )
    parser.add_argument(
        "--src-path",
        type=Path,
        default=None,
        help="Path to src directory (default: auto-detect)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--no-executor-check",
        action="store_true",
        help="Skip executor-specific validation"
    )
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    
    src_path = args.src_path or project_root / "src"
    output_dir = args.output_dir or project_root / "artifacts" / "audit_reports"
    config_base_path = Path(__file__).resolve().parent
    
    if not src_path.exists():
        logger.error(f"Source path does not exist: {src_path}")
        return 1
    
    if not config_base_path.exists():
        logger.error(f"Config base path does not exist: {config_base_path}")
        return 1
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("=" * 80)
    logger.info("COMPREHENSIVE PARAMETER AUDIT")
    logger.info("=" * 80)
    logger.info(f"Source: {src_path}")
    logger.info(f"Config: {config_base_path}")
    logger.info(f"Output: {output_dir}")
    logger.info("=" * 80)
    
    logger.info("\n>>> Phase 1: General Parameter Scan")
    logger.info("-" * 80)
    stats = run_audit(src_path, config_base_path, output_dir)
    
    executor_violations = 0
    if not args.no_executor_check:
        logger.info("\n>>> Phase 2: Executor Parameter Validation")
        logger.info("-" * 80)
        executor_report_path = output_dir / "executor_parameter_validation.md"
        executor_violations = validate_executors(src_path, executor_report_path)
    
    logger.info("\n>>> Phase 3: Unified Report Generation")
    logger.info("-" * 80)
    generate_unified_report(stats, executor_violations, output_dir)
    
    logger.info("\n" + "=" * 80)
    logger.info("AUDIT COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Files Scanned: {stats.total_files_scanned}")
    logger.info(f"Violations: {stats.violations_found}")
    logger.info(f"Critical: {stats.critical_violations}")
    logger.info(f"Executor Issues: {executor_violations}")
    
    if stats.critical_violations == 0 and executor_violations == 0:
        logger.info("Status: ✅ CERTIFICATION PASSED")
        logger.info("=" * 80)
        return 0
    else:
        logger.warning("Status: ❌ CERTIFICATION FAILED")
        logger.info("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())

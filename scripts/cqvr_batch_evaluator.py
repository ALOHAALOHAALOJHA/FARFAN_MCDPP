#!/usr/bin/env python3
"""
CQVR Batch Contract Evaluator
==============================

Evaluates multiple executor contracts using the CQVR (Calibration, Quality,
Validation, Reliability) framework and generates comprehensive reports.

This script is designed to work with the GitHub Actions workflow for
continuous quality validation of executor contracts.

Usage:
    python scripts/cqvr_batch_evaluator.py \
        --contracts-dir path/to/contracts \
        --output-dir path/to/output \
        --threshold 40 \
        [--contracts contract1.json contract2.json ...]

Exit Codes:
    0 - All contracts passed quality threshold
    1 - Some contracts failed quality threshold (when --fail-below-threshold is set)
    2 - Error in execution

Version: 1.0.0
Author: F.A.R.F.A.N Pipeline Team
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# Add src to path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from farfan_pipeline.phases.Phase_02.phase2_60_01_contract_validator_cqvr import (
    CQVRScore,
    CQVRValidator,
    TriageDecision,
)


@dataclass
class ContractEvaluationResult:
    """Result of evaluating a single contract."""

    contract_name: str
    contract_path: str
    score: CQVRScore
    decision: TriageDecision
    blockers: list[str]
    warnings: list[str]
    recommendations: list[dict[str, Any]]
    rationale: str
    passed_threshold: bool
    timestamp: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "contract_name": self.contract_name,
            "contract_path": self.contract_path,
            "score": {
                "tier1_score": self.score.tier1_score,
                "tier2_score": self.score.tier2_score,
                "tier3_score": self.score.tier3_score,
                "total_score": self.score.total_score,
                "tier1_percentage": self.score.tier1_percentage,
                "tier2_percentage": self.score.tier2_percentage,
                "tier3_percentage": self.score.tier3_percentage,
                "total_percentage": self.score.total_percentage,
            },
            "decision": self.decision.value,
            "triage_status": self._get_triage_status(),
            "blockers": self.blockers,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "rationale": self.rationale,
            "passed_threshold": self.passed_threshold,
            "timestamp": self.timestamp,
        }

    def _get_triage_status(self) -> str:
        """Get human-readable triage status."""
        if self.decision == TriageDecision.PRODUCCION:
            return "PRODUCTION_READY"
        elif self.decision == TriageDecision.PARCHEAR:
            return "NEEDS_PATCHING"
        else:
            return "NEEDS_REFORMULATION"


@dataclass
class CQVREvaluationReport:
    """Comprehensive CQVR evaluation report."""

    timestamp: str
    threshold: int
    total_contracts: int
    passed: int
    failed: int
    results: list[ContractEvaluationResult] = field(default_factory=list)
    failed_contracts: list[str] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp,
            "threshold": self.threshold,
            "total_contracts": self.total_contracts,
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": (
                round(self.passed / self.total_contracts * 100, 2)
                if self.total_contracts > 0
                else 0
            ),
            "results": [r.to_dict() for r in self.results],
            "failed_contracts": self.failed_contracts,
            "summary": self.summary,
        }


class CQVRBatchEvaluator:
    """Batch evaluator for CQVR contract validation."""

    def __init__(self, threshold: int = 40):
        """
        Initialize the batch evaluator.

        Args:
            threshold: Minimum quality threshold (0-100)
        """
        self.threshold = threshold
        self.validator = CQVRValidator()
        self.results: list[ContractEvaluationResult] = []

    def evaluate_contract(self, contract_path: Path) -> ContractEvaluationResult | None:
        """
        Evaluate a single contract.

        Args:
            contract_path: Path to the contract JSON file

        Returns:
            ContractEvaluationResult or None if evaluation failed
        """
        try:
            with open(contract_path, encoding="utf-8") as f:
                contract = json.load(f)

            decision = self.validator.validate_contract(contract)

            result = ContractEvaluationResult(
                contract_name=contract_path.name,
                contract_path=str(contract_path),
                score=decision.score,
                decision=decision.decision,
                blockers=decision.blockers,
                warnings=decision.warnings,
                recommendations=decision.recommendations,
                rationale=decision.rationale,
                passed_threshold=decision.score.total_percentage >= self.threshold,
                timestamp=datetime.now().isoformat(),
            )

            return result

        except json.JSONDecodeError as e:
            print(f"❌ Error decoding JSON in {contract_path}: {e}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"❌ Error evaluating {contract_path}: {e}", file=sys.stderr)
            return None

    def evaluate_contracts(
        self, contracts_dir: Path, specific_contracts: list[str] | None = None
    ) -> CQVREvaluationReport:
        """
        Evaluate multiple contracts.

        Args:
            contracts_dir: Directory containing contract files
            specific_contracts: Optional list of specific contract filenames to evaluate

        Returns:
            CQVREvaluationReport
        """
        if not contracts_dir.exists():
            print(f"❌ Contracts directory not found: {contracts_dir}", file=sys.stderr)
            sys.exit(2)

        # Find contract files
        contract_files: list[Path] = []

        if specific_contracts:
            # Evaluate only specified contracts
            for contract_name in specific_contracts:
                contract_path = contracts_dir / contract_name
                if contract_path.exists():
                    contract_files.append(contract_path)
                else:
                    print(
                        f"⚠️  Contract not found: {contract_path}",
                        file=sys.stderr,
                    )
        else:
            # Evaluate all JSON files in directory
            contract_files = sorted(contracts_dir.glob("*.json"))

        if not contract_files:
            print(f"❌ No contract files found in {contracts_dir}", file=sys.stderr)
            sys.exit(2)

        print(f"📊 Evaluating {len(contract_files)} contracts...")
        print(f"📈 Quality threshold: {self.threshold}/100")
        print()

        # Evaluate each contract
        results = []
        passed = 0
        failed = 0
        failed_contracts = []

        for i, contract_path in enumerate(contract_files, 1):
            print(f"[{i}/{len(contract_files)}] Evaluating {contract_path.name}...", end=" ")

            result = self.evaluate_contract(contract_path)

            if result:
                results.append(result)
                status = "✅ PASS" if result.passed_threshold else "❌ FAIL"
                print(f"{status} ({result.score.total_percentage:.1f}/100)")

                if result.passed_threshold:
                    passed += 1
                else:
                    failed += 1
                    failed_contracts.append(result.contract_name)
            else:
                print("❌ ERROR")
                failed += 1

        # Calculate summary statistics
        summary = self._calculate_summary(results)

        report = CQVREvaluationReport(
            timestamp=datetime.now().isoformat(),
            threshold=self.threshold,
            total_contracts=len(results),
            passed=passed,
            failed=failed,
            results=results,
            failed_contracts=failed_contracts,
            summary=summary,
        )

        return report

    def _calculate_summary(self, results: list[ContractEvaluationResult]) -> dict[str, Any]:
        """Calculate summary statistics from results."""
        if not results:
            return {}

        scores = [r.score.total_score for r in results]
        tier1_scores = [r.score.tier1_score for r in results]

        production_ready = sum(1 for r in results if r.decision == TriageDecision.PRODUCCION)
        needs_patching = sum(1 for r in results if r.decision == TriageDecision.PARCHEAR)
        needs_reformulation = sum(1 for r in results if r.decision == TriageDecision.REFORMULAR)

        total_blockers = sum(len(r.blockers) for r in results)
        total_warnings = sum(len(r.warnings) for r in results)

        return {
            "average_score": round(sum(scores) / len(scores), 2),
            "min_score": round(min(scores), 2),
            "max_score": round(max(scores), 2),
            "average_tier1": round(sum(tier1_scores) / len(tier1_scores), 2),
            "production_ready": production_ready,
            "needs_patching": needs_patching,
            "needs_reformulation": needs_reformulation,
            "total_blockers": total_blockers,
            "total_warnings": total_warnings,
        }

    def save_reports(self, report: CQVREvaluationReport, output_dir: Path) -> None:
        """
        Save evaluation reports in multiple formats.

        Args:
            report: The evaluation report
            output_dir: Directory to save reports
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save JSON report
        json_path = output_dir / "cqvr_evaluation_report.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=2)
        print(f"💾 JSON report saved: {json_path}")

        # Save Markdown report
        md_path = output_dir / "cqvr_evaluation_report.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(self._generate_markdown_report(report))
        print(f"💾 Markdown report saved: {md_path}")

        # Save HTML dashboard
        html_path = output_dir / "cqvr_dashboard.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(self._generate_html_dashboard(report))
        print(f"💾 HTML dashboard saved: {html_path}")

    def _generate_markdown_report(self, report: CQVREvaluationReport) -> str:
        """Generate a Markdown report."""
        lines = [
            "# CQVR Contract Quality Evaluation Report",
            "",
            f"**Generated:** {report.timestamp}",
            f"**Threshold:** {report.threshold}/100",
            "",
            "## Summary",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| **Total Contracts** | {report.total_contracts} |",
            f"| **Passed** | {report.passed} |",
            f"| **Failed** | {report.failed} |",
            (
                f"| **Pass Rate** | {report.passed / report.total_contracts * 100:.1f}% |"
                if report.total_contracts > 0
                else "| **Pass Rate** | N/A |"
            ),
            "",
        ]

        if report.summary:
            lines.extend(
                [
                    "## Statistics",
                    "",
                    f"| Metric | Value |",
                    f"|--------|-------|",
                    f"| **Average Score** | {report.summary.get('average_score', 'N/A')}/100 |",
                    f"| **Min Score** | {report.summary.get('min_score', 'N/A')}/100 |",
                    f"| **Max Score** | {report.summary.get('max_score', 'N/A')}/100 |",
                    f"| **Production Ready** | {report.summary.get('production_ready', 0)} |",
                    f"| **Needs Patching** | {report.summary.get('needs_patching', 0)} |",
                    f"| **Needs Reformulation** | {report.summary.get('needs_reformulation', 0)} |",
                    f"| **Total Blockers** | {report.summary.get('total_blockers', 0)} |",
                    f"| **Total Warnings** | {report.summary.get('total_warnings', 0)} |",
                    "",
                ]
            )

        lines.extend(
            [
                "## Contract Results",
                "",
                "| Contract | Score | Tier 1 | Tier 2 | Tier 3 | Status | Decision |",
                "|----------|-------|--------|--------|--------|--------|----------|",
            ]
        )

        for result in report.results:
            status = "✅" if result.passed_threshold else "❌"
            lines.append(
                f"| {result.contract_name} | "
                f"{result.score.total_percentage:.1f}% | "
                f"{result.score.tier1_percentage:.1f}% | "
                f"{result.score.tier2_percentage:.1f}% | "
                f"{result.score.tier3_percentage:.1f}% | "
                f"{status} | {result._get_triage_status()} |"
            )

        if report.failed_contracts:
            lines.extend(
                [
                    "",
                    "## ❌ Failed Contracts",
                    "",
                    "The following contracts failed to meet the quality threshold:",
                    "",
                ]
            )
            for contract in report.failed_contracts:
                lines.append(f"- {contract}")

        if any(r.blockers for r in report.results):
            lines.extend(
                [
                    "",
                    "## Blockers",
                    "",
                ]
            )
            for result in report.results:
                if result.blockers:
                    lines.append(f"### {result.contract_name}")
                    for blocker in result.blockers:
                        lines.append(f"- {blocker}")
                    lines.append("")

        return "\n".join(lines)

    def _generate_html_dashboard(self, report: CQVREvaluationReport) -> str:
        """Generate an HTML dashboard."""
        pass_rate = (
            report.passed / report.total_contracts * 100 if report.total_contracts > 0 else 0
        )
        avg_score = report.summary.get("average_score", 0)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CQVR Quality Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }}
        .timestamp {{
            color: #666;
            font-size: 0.9em;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            text-align: center;
        }}
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        .metric-label {{
            color: #666;
            margin-top: 5px;
            font-size: 0.9em;
        }}
        .pass {{ color: #28a745; }}
        .fail {{ color: #dc3545; }}
        .warning {{ color: #ffc107; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .status-pass {{
            background: #d4edda;
            color: #155724;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
        }}
        .status-fail {{
            background: #f8d7da;
            color: #721c24;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
        }}
        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #e9ecef;
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }}
        .contract-list {{
            margin-top: 30px;
        }}
        .contract-item {{
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            background: #f8f9fa;
        }}
        .contract-name {{
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }}
        .contract-score {{
            display: flex;
            justify-content: space-between;
            margin-top: 10px;
        }}
        .score-bar {{
            flex: 1;
            margin: 0 10px;
        }}
        .tier-bar {{
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 3px;
        }}
        .tier-fill {{
            height: 100%;
            border-radius: 4px;
        }}
        .tier-1 {{ background: #667eea; }}
        .tier-2 {{ background: #764ba2; }}
        .tier-3 {{ background: #f093fb; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 CQVR Quality Dashboard</h1>
            <div class="timestamp">{report.timestamp}</div>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{report.total_contracts}</div>
                <div class="metric-label">Total Contracts</div>
            </div>
            <div class="metric-card">
                <div class="metric-value pass">{report.passed}</div>
                <div class="metric-label">Passed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value fail">{report.failed}</div>
                <div class="metric-label">Failed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{pass_rate:.1f}%</div>
                <div class="metric-label">Pass Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{avg_score:.1f}</div>
                <div class="metric-label">Avg Score</div>
            </div>
        </div>

        <h2>Overall Progress</h2>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {pass_rate}%">
                {pass_rate:.1f}% Passed
            </div>
        </div>

        <h2>Contract Results</h2>
        <table>
            <thead>
                <tr>
                    <th>Contract</th>
                    <th>Total Score</th>
                    <th>Tier 1</th>
                    <th>Tier 2</th>
                    <th>Tier 3</th>
                    <th>Status</th>
                    <th>Decision</th>
                </tr>
            </thead>
            <tbody>
"""

        for result in report.results:
            status_class = "status-pass" if result.passed_threshold else "status-fail"
            status_text = "PASS" if result.passed_threshold else "FAIL"

            html += f"""
                <tr>
                    <td>{result.contract_name}</td>
                    <td>{result.score.total_percentage:.1f}%</td>
                    <td>{result.score.tier1_percentage:.1f}%</td>
                    <td>{result.score.tier2_percentage:.1f}%</td>
                    <td>{result.score.tier3_percentage:.1f}%</td>
                    <td><span class="{status_class}">{status_text}</span></td>
                    <td>{result._get_triage_status()}</td>
                </tr>
"""

        html += """
            </tbody>
        </table>

        <div class="contract-list">
            <h2>Detailed Breakdown</h2>
"""

        for result in report.results:
            html += f"""
            <div class="contract-item">
                <div class="contract-name">{result.contract_name}</div>
                <div class="contract-score">
                    <span>Score: {result.score.total_percentage:.1f}%</span>
                    <div class="score-bar">
                        <div class="tier-bar"><div class="tier-fill tier-1" style="width: {result.score.tier1_percentage}%"></div></div>
                        <div class="tier-bar"><div class="tier-fill tier-2" style="width: {result.score.tier2_percentage}%"></div></div>
                        <div class="tier-bar"><div class="tier-fill tier-3" style="width: {result.score.tier3_percentage}%"></div></div>
                    </div>
                    <span>{result._get_triage_status()}</span>
                </div>
            </div>
"""

        html += """
        </div>
    </div>
</body>
</html>
"""

        return html


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Batch evaluate executor contracts using CQVR framework"
    )
    parser.add_argument(
        "--contracts-dir",
        type=Path,
        required=True,
        help="Directory containing contract JSON files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("cqvr_reports"),
        help="Output directory for reports (default: cqvr_reports)",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=40,
        help="Minimum quality threshold (0-100, default: 40)",
    )
    parser.add_argument(
        "--contracts",
        nargs="*",
        help="Specific contract filenames to evaluate (default: all contracts)",
    )
    parser.add_argument(
        "--fail-below-threshold",
        action="store_true",
        help="Exit with error code if any contract fails below threshold",
    )

    args = parser.parse_args()

    # Validate threshold
    if not 0 <= args.threshold <= 100:
        print("❌ Error: threshold must be between 0 and 100", file=sys.stderr)
        return 2

    # Run evaluation
    evaluator = CQVRBatchEvaluator(threshold=args.threshold)
    report = evaluator.evaluate_contracts(
        contracts_dir=args.contracts_dir,
        specific_contracts=args.contracts if args.contracts else None,
    )

    # Print summary
    print()
    print("=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Total Contracts: {report.total_contracts}")
    print(f"Passed: {report.passed}")
    print(f"Failed: {report.failed}")
    print(f"Pass Rate: {report.passed / report.total_contracts * 100:.1f}%")
    print("=" * 60)

    if report.failed > 0:
        print()
        print("❌ Failed Contracts:")
        for contract in report.failed_contracts:
            print(f"  - {contract}")
        print()

    # Save reports
    evaluator.save_reports(report, args.output_dir)

    # Exit with appropriate code
    if args.fail_below_threshold and report.failed > 0:
        print(f"❌ {report.failed} contracts failed quality threshold")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

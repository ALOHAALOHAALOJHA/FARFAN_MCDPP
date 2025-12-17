#!/usr/bin/env python3
"""
CQVR Batch Evaluator - CLI tool for evaluating contract quality
Generates evaluation reports, dashboards, and determines pass/fail status
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "farfan_pipeline" / "phases" / "Phase_two" / "json_files_phase_two" / "executor_contracts"))
from cqvr_validator import CQVRValidator


class CQVREvaluator:
    """Batch contract evaluator with reporting"""
    
    def __init__(self, contracts_dir: Path, output_dir: Path, threshold: int = 40):
        self.contracts_dir = contracts_dir
        self.output_dir = output_dir
        self.threshold = threshold
        self.validator = CQVRValidator()
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def evaluate_contracts(self, contract_files: list[str]) -> dict[str, Any]:
        """Evaluate multiple contracts and generate reports"""
        results = []
        failed_contracts = []
        passed_contracts = []
        
        for contract_file in contract_files:
            contract_path = self.contracts_dir / contract_file
            if not contract_path.exists():
                print(f"⚠️  Contract not found: {contract_file}")
                continue
            
            print(f"Evaluating {contract_file}...")
            report = self._evaluate_single_contract(contract_path)
            results.append(report)
            
            if report['score'] < self.threshold:
                failed_contracts.append(report)
            else:
                passed_contracts.append(report)
        
        summary = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_contracts': len(results),
            'passed': len(passed_contracts),
            'failed': len(failed_contracts),
            'threshold': self.threshold,
            'results': results,
            'failed_contracts': [r['contract_name'] for r in failed_contracts],
            'passed_contracts': [r['contract_name'] for r in passed_contracts]
        }
        
        self._save_reports(summary)
        self._generate_dashboard(summary)
        
        return summary
    
    def _evaluate_single_contract(self, contract_path: Path) -> dict[str, Any]:
        """Evaluate a single contract"""
        with open(contract_path) as f:
            contract = json.load(f)
        
        validation_report = self.validator.validate_contract(contract)
        
        return {
            'contract_name': contract_path.name,
            'contract_id': contract.get('identity', {}).get('question_id', 'UNKNOWN'),
            'score': validation_report['total_score'],
            'percentage': validation_report['percentage'],
            'tier1_score': validation_report['tier1_score'],
            'tier2_score': validation_report['tier2_score'],
            'tier3_score': validation_report['tier3_score'],
            'passed': validation_report['passed'],
            'triage_decision': validation_report['triage_decision'],
            'breakdown': validation_report['breakdown']
        }
    
    def _save_reports(self, summary: dict[str, Any]) -> None:
        """Save evaluation reports"""
        report_json = self.output_dir / 'cqvr_evaluation_report.json'
        with open(report_json, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"✅ Saved JSON report: {report_json}")
        
        report_md = self.output_dir / 'cqvr_evaluation_report.md'
        with open(report_md, 'w') as f:
            f.write(self._generate_markdown_report(summary))
        print(f"✅ Saved Markdown report: {report_md}")
    
    def _generate_markdown_report(self, summary: dict[str, Any]) -> str:
        """Generate Markdown report"""
        timestamp = summary['timestamp']
        total = summary['total_contracts']
        passed = summary['passed']
        failed = summary['failed']
        threshold = summary['threshold']
        
        status_emoji = '✅' if failed == 0 else '❌'
        
        report = f"""# 📊 CQVR Evaluation Report

**Timestamp**: {timestamp}  
**Status**: {status_emoji} {passed}/{total} contracts passed (threshold: {threshold}/100)

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Contracts** | {total} |
| **Passed (≥{threshold})** | {passed} |
| **Failed (<{threshold})** | {failed} |
| **Pass Rate** | {passed/total*100:.1f}% |

---

## Results

| Contract | ID | Score | Tier 1 | Tier 2 | Tier 3 | Status | Triage |
|----------|-------|-------|--------|--------|--------|--------|--------|
"""
        
        for result in summary['results']:
            status = '✅' if result['score'] >= threshold else '❌'
            report += f"| {result['contract_name']} | {result['contract_id']} | {result['score']}/100 | {result['tier1_score']}/55 | {result['tier2_score']}/30 | {result['tier3_score']}/15 | {status} | {result['triage_decision']} |\n"
        
        if summary['failed_contracts']:
            report += f"\n---\n\n## ❌ Failed Contracts ({len(summary['failed_contracts'])})\n\n"
            for contract in summary['failed_contracts']:
                report += f"- {contract}\n"
        
        report += "\n---\n\n*Generated by CQVR Batch Evaluator*\n"
        
        return report
    
    def _generate_dashboard(self, summary: dict[str, Any]) -> None:
        """Generate HTML dashboard"""
        dashboard_path = self.output_dir / 'cqvr_dashboard.html'
        
        total = summary['total_contracts']
        passed = summary['passed']
        failed = summary['failed']
        threshold = summary['threshold']
        pass_rate = passed / total * 100 if total > 0 else 0
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CQVR Evaluation Dashboard</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .timestamp {{
            color: #666;
            font-size: 14px;
            margin-bottom: 30px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric {{
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .metric.passed {{
            background: #d4edda;
            border: 1px solid #c3e6cb;
        }}
        .metric.failed {{
            background: #f8d7da;
            border: 1px solid #f5c6cb;
        }}
        .metric.total {{
            background: #d1ecf1;
            border: 1px solid #bee5eb;
        }}
        .metric-value {{
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .metric-label {{
            font-size: 14px;
            color: #666;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
        }}
        .status-pass {{
            color: #28a745;
            font-weight: bold;
        }}
        .status-fail {{
            color: #dc3545;
            font-weight: bold;
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
            background: linear-gradient(90deg, #28a745, #20c997);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            transition: width 0.3s ease;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 CQVR Evaluation Dashboard</h1>
        <div class="timestamp">{summary['timestamp']}</div>
        
        <div class="summary">
            <div class="metric total">
                <div class="metric-value">{total}</div>
                <div class="metric-label">Total Contracts</div>
            </div>
            <div class="metric passed">
                <div class="metric-value">{passed}</div>
                <div class="metric-label">Passed (≥{threshold})</div>
            </div>
            <div class="metric failed">
                <div class="metric-value">{failed}</div>
                <div class="metric-label">Failed (&lt;{threshold})</div>
            </div>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {pass_rate}%">
                {pass_rate:.1f}% Pass Rate
            </div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Contract</th>
                    <th>ID</th>
                    <th>Score</th>
                    <th>Tier 1</th>
                    <th>Tier 2</th>
                    <th>Tier 3</th>
                    <th>Status</th>
                    <th>Triage</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for result in summary['results']:
            status_class = 'status-pass' if result['score'] >= threshold else 'status-fail'
            status_text = '✅ Pass' if result['score'] >= threshold else '❌ Fail'
            html += f"""
                <tr>
                    <td>{result['contract_name']}</td>
                    <td>{result['contract_id']}</td>
                    <td><strong>{result['score']}/100</strong></td>
                    <td>{result['tier1_score']}/55</td>
                    <td>{result['tier2_score']}/30</td>
                    <td>{result['tier3_score']}/15</td>
                    <td class="{status_class}">{status_text}</td>
                    <td>{result['triage_decision']}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
        
        with open(dashboard_path, 'w') as f:
            f.write(html)
        print(f"✅ Generated dashboard: {dashboard_path}")


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CQVR Batch Contract Evaluator')
    parser.add_argument('--contracts-dir', type=Path, required=True,
                       help='Directory containing contract JSON files')
    parser.add_argument('--output-dir', type=Path, default=Path('cqvr_reports'),
                       help='Output directory for reports (default: cqvr_reports)')
    parser.add_argument('--threshold', type=int, default=40,
                       help='Minimum score threshold (default: 40)')
    parser.add_argument('--contracts', nargs='+',
                       help='Specific contracts to evaluate (default: all)')
    parser.add_argument('--fail-below-threshold', action='store_true',
                       help='Exit with error code if any contract fails')
    
    args = parser.parse_args()
    
    if not args.contracts_dir.exists():
        print(f"❌ Contracts directory not found: {args.contracts_dir}")
        sys.exit(1)
    
    if args.contracts:
        contract_files = args.contracts
    else:
        contract_files = sorted([f.name for f in args.contracts_dir.glob('*.json')])
    
    if not contract_files:
        print(f"❌ No contracts found in {args.contracts_dir}")
        sys.exit(1)
    
    print(f"🔍 Evaluating {len(contract_files)} contracts...")
    print(f"📁 Contracts directory: {args.contracts_dir}")
    print(f"📊 Output directory: {args.output_dir}")
    print(f"📏 Threshold: {args.threshold}/100\n")
    
    evaluator = CQVREvaluator(args.contracts_dir, args.output_dir, args.threshold)
    summary = evaluator.evaluate_contracts(contract_files)
    
    print(f"\n{'='*60}")
    print(f"📊 EVALUATION COMPLETE")
    print(f"{'='*60}")
    print(f"Total contracts: {summary['total_contracts']}")
    print(f"Passed: {summary['passed']} ✅")
    print(f"Failed: {summary['failed']} ❌")
    print(f"Pass rate: {summary['passed']/summary['total_contracts']*100:.1f}%")
    
    if summary['failed_contracts']:
        print(f"\n❌ Failed contracts:")
        for contract in summary['failed_contracts']:
            print(f"  - {contract}")
    
    if args.fail_below_threshold and summary['failed'] > 0:
        print(f"\n❌ EVALUATION FAILED: {summary['failed']} contracts below threshold")
        sys.exit(1)
    
    print(f"\n✅ All reports generated in: {args.output_dir}")
    sys.exit(0)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
generate_coverage_report.py - Generate an HTML report for questionnaire coverage gaps.

This script takes the audit_manifest.json as input and generates a user-friendly
HTML report that visualizes the contract coverage gaps. The report includes
overall metrics and a breakdown by dimension and policy area.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
AUDIT_MANIFEST_PATH = PROJECT_ROOT / "artifacts" / "audit" / "audit_manifest.json"
MONOLITH_PATH = PROJECT_ROOT / "data" / "questionnaire_monolith.json"
OUTPUT_DIR = PROJECT_ROOT / "artifacts" / "audit"
HTML_REPORT_PATH = OUTPUT_DIR / "coverage_report.html"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Questionnaire Coverage Report</title>
    <style>
        body {{ font-family: sans-serif; margin: 2em; }}
        h1, h2 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 2em; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .summary {{ background-color: #f9f9f9; padding: 1em; border-radius: 5px; margin-bottom: 2em; }}
        .summary-metric {{ display: inline-block; margin-right: 2em; }}
        .summary-metric h3 {{ margin: 0; color: #555; }}
        .summary-metric p {{ margin: 0; font-size: 2em; font-weight: bold; }}
        .coverage-bar {{ background-color: #e0e0e0; border-radius: 3px; overflow: hidden; height: 20px; }}
        .coverage-fill {{ background-color: #4CAF50; height: 100%; }}
        .gap-list {{ column-count: 3; }}
        .gap-list li {{ margin-bottom: 0.5em; }}
    </style>
</head>
<body>
    <h1>Questionnaire Coverage Report</h1>
    <div class="summary">
        <h2>Executive Summary</h2>
        <div class="summary-metric">
            <h3>Total Micro-Questions</h3>
            <p>{total_micro_questions}</p>
        </div>
        <div class="summary-metric">
            <h3>Contract Coverage</h3>
            <p>{contract_coverage_percentage:.2f}%</p>
        </div>
        <div class="summary-metric">
            <h3>Questions with Contract</h3>
            <p>{questions_with_contract}</p>
        </div>
        <div class="summary-metric">
            <h3>Questions without Contract</h3>
            <p>{questions_without_contract}</p>
        </div>
    </div>

    <h2>Contract Coverage Details</h2>
    <div class="coverage-bar">
        <div class="coverage-fill" style="width: {contract_coverage_percentage:.2f}%;"></div>
    </div>
    <p>{questions_with_contract} of {total_micro_questions} questions have contracts.</p>

    <h2>Missing Contracts</h2>
    <p>There are {num_missing_unique} unique questions missing contracts across all policy areas.</p>
    <div class="gap-list">
        <ul>
            {missing_contracts_list}
        </ul>
    </div>
</body>
</html>
"""

def generate_report():
    """
    Generates the HTML report from the audit manifest.
    """
    print("Generating HTML coverage report...")

    # Load audit manifest
    if not AUDIT_MANIFEST_PATH.exists():
        print(f"Error: Audit manifest not found at {AUDIT_MANIFEST_PATH}")
        return
    manifest = json.loads(AUDIT_MANIFEST_PATH.read_text(encoding="utf-8"))

    metrics = manifest.get("metrics", {})
    gaps = manifest.get("gaps", {})

    missing_contracts_list_items = "".join(
        f"<li>{qid}</li>" for qid in gaps.get("questions_without_contract_details", [])
    )

    html_content = HTML_TEMPLATE.format(
        total_micro_questions=metrics.get("total_micro_questions", 0),
        contract_coverage_percentage=metrics.get("contract_coverage_percentage", 0),
        questions_with_contract=metrics.get("questions_with_contract", 0),
        questions_without_contract=metrics.get("questions_without_contract", 0),
        num_missing_unique=len(gaps.get("questions_without_contract_details", [])),
        missing_contracts_list=missing_contracts_list_items,
    )

    # Write HTML report
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(HTML_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML report generated successfully at {HTML_REPORT_PATH}")

if __name__ == "__main__":
    generate_report()

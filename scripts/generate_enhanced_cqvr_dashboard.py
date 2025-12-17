#!/usr/bin/env python3
"""
Enhanced CQVR Dashboard Generator
Evaluates all 300 contracts with increased severity and generates interactive HTML dashboard
"""
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Import the standalone evaluator
sys.path.insert(0, str(Path(__file__).parent))
from cqvr_evaluator_standalone import evaluate_contract


def evaluate_all_contracts() -> List[Dict[str, Any]]:
    """Evaluate all 300 contracts using the enhanced standalone evaluator."""
    contracts_dir = Path(__file__).parent.parent / "src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized"
    
    contract_files = sorted(contracts_dir.glob("Q*.v3.json"))
    print(f"Found {len(contract_files)} contracts to evaluate")
    
    results = []
    for i, contract_file in enumerate(contract_files, 1):
        if i % 50 == 0:
            print(f"Progress: {i}/{len(contract_files)} contracts evaluated")
        
        try:
            with open(contract_file, encoding="utf-8") as f:
                contract = json.load(f)
            
            # Use the standalone evaluator
            evaluation = evaluate_contract(contract)
            results.append(evaluation)
            
        except Exception as e:
            print(f"ERROR evaluating {contract_file.name}: {e}")
            # Add error placeholder
            results.append({
                "contract_id": contract_file.stem,
                "evaluation_timestamp": datetime.now().isoformat(),
                "cqvr_version": "2.1-enhanced",
                "scores": {
                    "tier1": {"score": 0, "max": 55, "percentage": 0.0},
                    "tier2": {"score": 0, "max": 30, "percentage": 0.0},
                    "tier3": {"score": 0, "max": 15, "percentage": 0.0},
                    "total": {"score": 0, "max": 100, "percentage": 0.0}
                },
                "decision": {"status": "ERROR", "rationale": str(e)},
                "issues": {"all": [f"Evaluation failed: {e}"]}
            })
    
    print(f"Evaluation complete: {len(results)} contracts processed")
    return results


def generate_dashboard_html(results: List[Dict[str, Any]], output_path: Path) -> None:
    """Generate enhanced interactive HTML dashboard."""
    
    # Calculate statistics
    total = len(results)
    produccion = sum(1 for r in results if r["decision"]["status"] == "PRODUCCION")
    parchear = sum(1 for r in results if r["decision"]["status"] == "PARCHEAR")
    reformular = sum(1 for r in results if r["decision"]["status"] == "REFORMULAR")
    errors = sum(1 for r in results if r["decision"]["status"] == "ERROR")
    
    scores = [r["scores"]["total"]["score"] for r in results if r["decision"]["status"] != "ERROR"]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    # Generate contract rows HTML
    contract_rows = []
    for result in results:
        status = result["decision"]["status"]
        status_color = {
            "PRODUCCION": "#10b981",
            "PARCHEAR": "#f59e0b",
            "REFORMULAR": "#ef4444",
            "ERROR": "#6b7280"
        }.get(status, "#6b7280")
        
        status_icon = {
            "PRODUCCION": "✓",
            "PARCHEAR": "⚠",
            "REFORMULAR": "✗",
            "ERROR": "!"
        }.get(status, "?")
        
        t1 = result["scores"]["tier1"]["score"]
        t2 = result["scores"]["tier2"]["score"]
        t3 = result["scores"]["tier3"]["score"]
        total_score = result["scores"]["total"]["score"]
        
        contract_rows.append(f'''
            <tr>
                <td>{result["contract_id"]}</td>
                <td><span class="score-badge">{t1}/55</span></td>
                <td><span class="score-badge">{t2}/30</span></td>
                <td><span class="score-badge">{t3}/15</span></td>
                <td><span class="score-badge total-score">{total_score}/100</span></td>
                <td><span class="status-badge" style="background-color: {status_color}">{status_icon} {status}</span></td>
                <td>{len(result["issues"]["all"])}</td>
            </tr>
        ''')
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced CQVR Evaluation Dashboard - v2.1</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1800px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        header .subtitle {{
            font-size: 1.2em;
            opacity: 0.95;
            margin-bottom: 10px;
        }}
        
        header .version {{
            font-size: 0.9em;
            opacity: 0.8;
            background: rgba(255,255,255,0.2);
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            margin-top: 10px;
        }}
        
        .severity-notice {{
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 20px;
            margin: 20px;
            border-radius: 8px;
        }}
        
        .severity-notice h3 {{
            color: #92400e;
            margin-bottom: 10px;
        }}
        
        .severity-notice ul {{
            margin-left: 20px;
            color: #78350f;
        }}
        
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
        }}
        
        .card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-left: 4px solid;
        }}
        
        .card.total {{ border-left-color: #3b82f6; }}
        .card.produccion {{ border-left-color: #10b981; }}
        .card.parchear {{ border-left-color: #f59e0b; }}
        .card.reformular {{ border-left-color: #ef4444; }}
        .card.avg {{ border-left-color: #8b5cf6; }}
        
        .card-title {{
            font-size: 0.9em;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
        }}
        
        .card-value {{
            font-size: 3em;
            font-weight: 700;
            color: #1f2937;
        }}
        
        .card-percentage {{
            font-size: 0.9em;
            color: #6b7280;
            margin-top: 5px;
        }}
        
        .table-container {{
            padding: 30px;
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
        }}
        
        thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        th, td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        th {{
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 0.5px;
        }}
        
        tbody tr:hover {{
            background: #f9fafb;
        }}
        
        .score-badge {{
            background: #e0e7ff;
            color: #4338ca;
            padding: 4px 12px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 0.9em;
        }}
        
        .total-score {{
            background: #ddd6fe;
            color: #6d28d9;
            font-size: 1em;
        }}
        
        .status-badge {{
            padding: 6px 16px;
            border-radius: 20px;
            font-weight: 600;
            color: white;
            font-size: 0.9em;
            display: inline-block;
        }}
        
        .filter-container {{
            padding: 20px 30px;
            background: #f9fafb;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .filter-buttons {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        
        .filter-btn {{
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s;
        }}
        
        .filter-btn.all {{ background: #3b82f6; color: white; }}
        .filter-btn.produccion {{ background: #10b981; color: white; }}
        .filter-btn.parchear {{ background: #f59e0b; color: white; }}
        .filter-btn.reformular {{ background: #ef4444; color: white; }}
        .filter-btn:hover {{ opacity: 0.8; }}
        
        footer {{
            text-align: center;
            padding: 30px;
            background: #f9fafb;
            color: #6b7280;
            border-top: 1px solid #e5e7eb;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎯 CQVR Evaluation Dashboard</h1>
            <p class="subtitle">Enhanced Contract Quality Validation Report</p>
            <p class="version">Version 2.1 - Increased Severity | Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </header>
        
        <div class="severity-notice">
            <h3>⚠️ Enhanced Severity Thresholds (v2.1)</h3>
            <ul>
                <li>TIER1_THRESHOLD raised to 40 (was 35) - Stricter critical components</li>
                <li>PRODUCTION_THRESHOLD raised to 50/85 (was 45/80) - Higher quality bar</li>
                <li>Added TIER2_MINIMUM=20 and TIER3_MINIMUM=8 requirements</li>
                <li>Production requires ZERO blockers (was allowing some)</li>
                <li>PARCHEAR allows max 1 blocker, requires tier1≥45 and total≥75</li>
                <li>Source hash validation stricter (must be ≥32 chars, no placeholders)</li>
            </ul>
        </div>
        
        <div class="summary-cards">
            <div class="card total">
                <div class="card-title">Total Contracts</div>
                <div class="card-value">{total}</div>
            </div>
            
            <div class="card produccion">
                <div class="card-title">✓ Production Ready</div>
                <div class="card-value">{produccion}</div>
                <div class="card-percentage">{(produccion/total*100):.1f}% of total</div>
            </div>
            
            <div class="card parchear">
                <div class="card-title">⚠ Need Patches</div>
                <div class="card-value">{parchear}</div>
                <div class="card-percentage">{(parchear/total*100):.1f}% of total</div>
            </div>
            
            <div class="card reformular">
                <div class="card-title">✗ Need Reformulation</div>
                <div class="card-value">{reformular}</div>
                <div class="card-percentage">{(reformular/total*100):.1f}% of total</div>
            </div>
            
            <div class="card avg">
                <div class="card-title">Average Score</div>
                <div class="card-value">{avg_score:.1f}</div>
                <div class="card-percentage">out of 100</div>
            </div>
        </div>
        
        <div class="filter-container">
            <div class="filter-buttons">
                <button class="filter-btn all" onclick="filterTable('all')">Show All ({total})</button>
                <button class="filter-btn produccion" onclick="filterTable('PRODUCCION')">Production ({produccion})</button>
                <button class="filter-btn parchear" onclick="filterTable('PARCHEAR')">Patches ({parchear})</button>
                <button class="filter-btn reformular" onclick="filterTable('REFORMULAR')">Reformulation ({reformular})</button>
            </div>
        </div>
        
        <div class="table-container">
            <table id="contractsTable">
                <thead>
                    <tr>
                        <th>Contract ID</th>
                        <th>Tier 1 (Critical)</th>
                        <th>Tier 2 (Functional)</th>
                        <th>Tier 3 (Quality)</th>
                        <th>Total Score</th>
                        <th>Decision</th>
                        <th>Issues</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(contract_rows)}
                </tbody>
            </table>
        </div>
        
        <footer>
            <p><strong>F.A.R.F.A.N Mechanistic Policy Pipeline</strong></p>
            <p>CQVR v2.1 Enhanced Severity Evaluation | {len(results)} contracts evaluated</p>
            <p style="margin-top: 10px; font-size: 0.9em;">
                Thresholds: TIER1≥40, PRODUCTION(TIER1≥50, TIER2≥20, TIER3≥8, TOTAL≥85, blockers=0)
            </p>
        </footer>
    </div>
    
    <script>
        function filterTable(status) {{
            const rows = document.querySelectorAll('#contractsTable tbody tr');
            rows.forEach(row => {{
                if (status === 'all') {{
                    row.style.display = '';
                }} else {{
                    const statusCell = row.cells[5].textContent;
                    row.style.display = statusCell.includes(status) ? '' : 'none';
                }}
            }});
        }}
    </script>
</body>
</html>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Dashboard generated: {output_path}")


def main():
    """Main entry point."""
    print("="*80)
    print("Enhanced CQVR Dashboard Generator v2.1")
    print("Evaluating all 300 contracts with increased severity...")
    print("="*80)
    
    # Evaluate all contracts
    results = evaluate_all_contracts()
    
    # Save JSON results
    json_output = Path(__file__).parent.parent / "cqvr_evaluation_enhanced_v2.1.json"
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump({
            "metadata": {
                "version": "2.1-enhanced",
                "generated_at": datetime.now().isoformat(),
                "total_contracts": len(results),
                "severity_enhancements": [
                    "TIER1_THRESHOLD: 35 → 40",
                    "TIER1_PRODUCTION: 45 → 50",
                    "TOTAL_PRODUCTION: 80 → 85",
                    "Added TIER2_MINIMUM=20",
                    "Added TIER3_MINIMUM=8",
                    "Production requires zero blockers",
                    "PARCHEAR max 1 blocker, tier1≥45, total≥75",
                    "Source hash must be ≥32 chars"
                ]
            },
            "results": results
        }, f, indent=2, ensure_ascii=False)
    print(f"JSON results saved: {json_output}")
    
    # Generate HTML dashboard
    html_output = Path(__file__).parent.parent / "cqvr_dashboard_enhanced_v2.1.html"
    generate_dashboard_html(results, html_output)
    
    print("\n" + "="*80)
    print("✓ Dashboard generation complete!")
    print(f"  - JSON: {json_output}")
    print(f"  - HTML: {html_output}")
    print("="*80)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Utility script to analyze CQVR audit results for Q005-Q020 contracts.

Usage:
    python analyze_audit_results.py --summary
    python analyze_audit_results.py --critical-only
    python analyze_audit_results.py --contract Q010
    python analyze_audit_results.py --worst-contracts 5
    python analyze_audit_results.py --export-csv audit_summary.csv
"""

import argparse
import json
import sys
from pathlib import Path


def load_audit_results(audit_path: str = "contract_audit_Q005_Q020.json") -> dict:
    """Load audit results from JSON file"""
    audit_file = Path(audit_path)
    if not audit_file.exists():
        print(f"❌ Audit file not found: {audit_path}")
        print("Run ./audit_contracts_Q005_Q020.py first to generate the report.")
        sys.exit(1)

    with open(audit_file, encoding="utf-8") as f:
        return json.load(f)


def load_manifest(manifest_path: str = "transformation_requirements_manifest.json") -> dict:
    """Load transformation manifest"""
    manifest_file = Path(manifest_path)
    if not manifest_file.exists():
        print(f"⚠️  Manifest file not found: {manifest_path}")
        return {}

    with open(manifest_file) as f:
        return json.load(f)


def print_summary(results: dict):
    """Print executive summary"""
    stats = results.get("summary_statistics", {})
    metadata = results.get("audit_metadata", {})

    print("=" * 80)
    print("CQVR AUDIT EXECUTIVE SUMMARY")
    print("=" * 80)
    print(f"\nAudit Timestamp: {metadata.get('timestamp', 'N/A')}")
    print(f"Rubric Version: {metadata.get('rubric_version', 'N/A')}")
    print(f"Contract Range: {metadata.get('contract_range', 'N/A')}")

    print("\n📊 Overall Statistics:")
    print(f"  Contracts Audited: {stats.get('contracts_audited', 0)}/{metadata.get('total_contracts', 0)}")
    print(f"  Average Total Score: {stats.get('average_total_score', 0):.1f}/100")
    print(f"  Average Tier 1 Score: {stats.get('average_tier1_score', 0):.1f}/55")
    print(f"  Score Range: {stats.get('min_score', 0)} - {stats.get('max_score', 0)}")

    print("\n✅ Verdict Distribution:")
    print(f"  Production Ready: {stats.get('production_ready', 0)}")
    print(f"  Patchable: {stats.get('patchable', 0)}")
    print(f"  Requires Reformulation: {stats.get('requires_reformulation', 0)}")
    print(f"  Requires Major Work: {stats.get('requires_major_work', 0)}")

    print("\n🔧 Triage Distribution:")
    for decision, count in stats.get('triage_distribution', {}).items():
        print(f"  {decision}: {count}")


def print_critical_only(manifest: dict):
    """Print only critical issues"""
    critical = manifest.get("CRITICAL", {})
    items = critical.get("items", [])

    print("\n" + "=" * 80)
    print(f"🔴 CRITICAL ISSUES ({critical.get('count', 0)} total)")
    print("=" * 80)
    print(f"\n{critical.get('description', '')}\n")

    if not items:
        print("✅ No critical issues found!")
        return

    by_category = {}
    for item in items:
        category = item.get("category", "unknown")
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(item)

    for category, issues in by_category.items():
        print(f"\n📌 {category.upper().replace('_', ' ')} ({len(issues)} contracts):")
        for issue in issues:
            qid = issue.get("question_id", "N/A")
            desc = issue.get("description", "No description")
            score = issue.get("score", 0)
            threshold = issue.get("threshold", 0)
            print(f"  • {qid}: {desc}")
            print(f"    Score: {score}/{threshold}")

            if "orphan_sources" in issue.get("details", {}):
                orphans = issue["details"]["orphan_sources"]
                print(f"    Orphans: {', '.join(orphans[:3])}{'...' if len(orphans) > 3 else ''}")


def print_contract_detail(results: dict, contract_id: str):
    """Print detailed audit for specific contract"""
    audits = results.get("per_contract_audits", {})

    if contract_id not in audits:
        print(f"❌ Contract {contract_id} not found in audit results")
        available = [k for k in audits.keys() if isinstance(audits[k], dict) and "total_score" in audits[k]]
        print(f"Available contracts: {', '.join(sorted(available))}")
        return

    audit = audits[contract_id]

    print("\n" + "=" * 80)
    print(f"DETAILED AUDIT: {contract_id}")
    print("=" * 80)

    print(f"\nContract Version: {audit.get('contract_version', 'N/A')}")
    print(f"Audit Timestamp: {audit.get('audit_timestamp', 'N/A')}")

    print("\n📊 Scores:")
    print(f"  Total: {audit.get('total_score', 0)}/100 ({audit.get('overall_percentage', 0)}%)")
    print(f"  Tier 1 (Critical): {audit.get('tier1_total', 0)}/55 ({audit.get('tier1_percentage', 0)}%)")
    print(f"  Tier 2 (Functional): {audit.get('tier2_total', 0)}/30 ({audit.get('tier2_percentage', 0)}%)")
    print(f"  Tier 3 (Quality): {audit.get('tier3_total', 0)}/15 ({audit.get('tier3_percentage', 0)}%)")

    print("\n🔍 Tier 1 Breakdown:")
    for component, score in audit.get('tier1_scores', {}).items():
        max_score = {"A1_identity_schema": 20, "A2_method_assembly": 20,
                     "A3_signal_integrity": 10, "A4_output_schema": 5}[component]
        status = "✅" if score >= max_score * 0.75 else "⚠️" if score >= max_score * 0.6 else "❌"
        print(f"  {status} {component}: {score}/{max_score}")

    print("\n🔍 Tier 2 Breakdown:")
    for component, score in audit.get('tier2_scores', {}).items():
        max_score = 10
        status = "✅" if score >= 6 else "⚠️" if score >= 4 else "❌"
        print(f"  {status} {component}: {score}/{max_score}")

    print(f"\n🎯 Triage Decision: {audit.get('triage_decision', 'N/A')}")
    print(f"Verdict: {audit.get('verdict', {}).get('status', 'N/A')}")

    gaps = audit.get('gaps_identified', [])
    if gaps:
        print(f"\n⚠️  Identified Gaps ({len(gaps)}):")
        for gap in gaps:
            severity = gap.get('severity', 'UNKNOWN')
            icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡"}.get(severity, "⚪")
            print(f"  {icon} [{severity}] {gap.get('category', 'unknown')}")
            print(f"     {gap.get('description', 'No description')}")
            print(f"     Score: {gap.get('score', 0)}/{gap.get('threshold', 0)}")
    else:
        print("\n✅ No gaps identified!")


def print_worst_contracts(results: dict, count: int = 5):
    """Print N worst-performing contracts"""
    audits = results.get("per_contract_audits", {})
    valid_audits = [(qid, audit) for qid, audit in audits.items()
                    if isinstance(audit, dict) and "total_score" in audit]

    sorted_audits = sorted(valid_audits, key=lambda x: x[1]["total_score"])

    print("\n" + "=" * 80)
    print(f"📉 WORST {count} CONTRACTS")
    print("=" * 80)

    for i, (qid, audit) in enumerate(sorted_audits[:count], 1):
        total = audit.get('total_score', 0)
        tier1 = audit.get('tier1_total', 0)
        decision = audit.get('triage_decision', 'N/A')
        status = audit.get('verdict', {}).get('status', 'N/A')

        print(f"\n{i}. {qid}")
        print(f"   Total: {total}/100 | Tier 1: {tier1}/55")
        print(f"   Decision: {decision}")
        print(f"   Status: {status}")

        gaps = audit.get('gaps_identified', [])
        critical = [g for g in gaps if g.get('severity') == 'CRITICAL']
        if critical:
            print(f"   Critical Issues: {len(critical)}")
            for gap in critical[:2]:
                print(f"     • {gap.get('category', 'unknown')}")


def export_csv(results: dict, output_path: str):
    """Export audit results to CSV"""
    import csv

    audits = results.get("per_contract_audits", {})
    valid_audits = [(qid, audit) for qid, audit in audits.items()
                    if isinstance(audit, dict) and "total_score" in audit]

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Question ID', 'Total Score', 'Tier 1', 'Tier 2', 'Tier 3',
            'Tier 1 %', 'Tier 2 %', 'Tier 3 %', 'Overall %',
            'Triage Decision', 'Verdict Status', 'Critical Gaps', 'High Gaps', 'Medium Gaps'
        ])

        for qid, audit in sorted(valid_audits, key=lambda x: x[0]):
            gaps = audit.get('gaps_identified', [])
            critical_count = len([g for g in gaps if g.get('severity') == 'CRITICAL'])
            high_count = len([g for g in gaps if g.get('severity') == 'HIGH'])
            medium_count = len([g for g in gaps if g.get('severity') == 'MEDIUM'])

            writer.writerow([
                qid,
                audit.get('total_score', 0),
                audit.get('tier1_total', 0),
                audit.get('tier2_total', 0),
                audit.get('tier3_total', 0),
                audit.get('tier1_percentage', 0),
                audit.get('tier2_percentage', 0),
                audit.get('tier3_percentage', 0),
                audit.get('overall_percentage', 0),
                audit.get('triage_decision', ''),
                audit.get('verdict', {}).get('status', ''),
                critical_count,
                high_count,
                medium_count
            ])

    print(f"\n✅ CSV exported to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Analyze CQVR audit results")
    parser.add_argument('--summary', action='store_true', help='Print executive summary')
    parser.add_argument('--critical-only', action='store_true', help='Show only critical issues')
    parser.add_argument('--contract', type=str, help='Show detailed audit for specific contract (e.g., Q010)')
    parser.add_argument('--worst-contracts', type=int, metavar='N', help='Show N worst-performing contracts')
    parser.add_argument('--export-csv', type=str, metavar='FILE', help='Export results to CSV file')
    parser.add_argument('--audit-file', type=str, default='contract_audit_Q005_Q020.json',
                        help='Path to audit results JSON (default: contract_audit_Q005_Q020.json)')

    args = parser.parse_args()

    if not any([args.summary, args.critical_only, args.contract, args.worst_contracts, args.export_csv]):
        parser.print_help()
        return 1

    results = load_audit_results(args.audit_file)

    if args.summary:
        print_summary(results)

    if args.critical_only:
        manifest = load_manifest()
        print_critical_only(manifest)

    if args.contract:
        print_contract_detail(results, args.contract)

    if args.worst_contracts:
        print_worst_contracts(results, args.worst_contracts)

    if args.export_csv:
        export_csv(results, args.export_csv)

    return 0


if __name__ == "__main__":
    sys.exit(main())

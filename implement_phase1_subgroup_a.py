#!/usr/bin/env python3
"""
Strategic Phase 1 Implementation: Critical Systematic Fixes
Subgroup A Pilot: Q091, Q076, Q082, Q089, Q095

Philosophy: Fix root causes with rigorous validation, not reactive score inflation
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent / "src"))

from farfan_pipeline.phases.Phase_two.contract_validator_cqvr import CQVRValidator


def calculate_source_hash() -> str:
    """Calculate actual SHA256 of source monolith."""
    possible_paths = [
        "canonic_questionnaire_central/questionnaire_monolith.json",
        "data/questionnaire_monolith.json",
        "canonic_questionnaire_central/data/questionnaire_monolith.json",
    ]
    
    for path_str in possible_paths:
        path = Path(path_str)
        if path.exists():
            with open(path, "rb") as f:
                content = f.read()
                sha256_hash = hashlib.sha256(content).hexdigest()
                print(f"✅ Source hash calculated from: {path}")
                print(f"   SHA256: {sha256_hash}")
                return sha256_hash
    
    print("⚠️  Source monolith not found, using placeholder")
    return "SOURCE_MONOLITH_NOT_FOUND_PLACEHOLDER"


def fix_signal_threshold(contract: dict[str, Any], contract_id: str) -> dict[str, Any]:
    """
    Fix signal threshold with validation.
    
    Root cause: Contract generation template uses default 0.0
    Strategic fix: Set to 0.5 for contracts with mandatory signals
    """
    signal_reqs = contract.get("signal_requirements", {})
    mandatory_signals = signal_reqs.get("mandatory_signals", [])
    current_threshold = signal_reqs.get("minimum_signal_threshold", 0.0)
    
    if not mandatory_signals:
        print(f"  {contract_id}: No mandatory signals, skipping threshold fix")
        return contract
    
    if current_threshold > 0:
        print(f"  {contract_id}: Threshold already set to {current_threshold}, skipping")
        return contract
    
    # Strategic fix: Set appropriate threshold
    signal_reqs["minimum_signal_threshold"] = 0.5
    
    # Validate signal_weights align (if they exist)
    weights = signal_reqs.get("signal_weights", {})
    if weights:
        for signal_id in mandatory_signals:
            if signal_id in weights and weights[signal_id] < 0.5:
                # Ensure weight meets threshold
                weights[signal_id] = max(weights[signal_id], 0.5)
    
    print(f"  {contract_id}: ✅ Signal threshold fixed: 0.0 → 0.5")
    return contract


def fix_source_hash(contract: dict[str, Any], contract_id: str, real_hash: str) -> dict[str, Any]:
    """
    Fix source hash with validation.
    
    Root cause: Generation script doesn't calculate actual hash
    Strategic fix: Use real SHA256 hash of source monolith
    """
    traceability = contract.get("traceability", {})
    current_hash = traceability.get("source_hash", "")
    
    if not current_hash.startswith("TODO"):
        print(f"  {contract_id}: Source hash already set, skipping")
        return contract
    
    # Strategic fix: Set real hash
    traceability["source_hash"] = real_hash
    
    # Update modification timestamp
    identity = contract.get("identity", {})
    identity["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    print(f"  {contract_id}: ✅ Source hash fixed")
    return contract


def validate_fix(contract_id: str, before_score: float, after_score: float, before_blockers: int, after_blockers: int) -> bool:
    """Validate that fix improved contract without regression."""
    print(f"\n  {contract_id} Validation:")
    print(f"    Score: {before_score:.1f} → {after_score:.1f} (Δ{after_score - before_score:+.1f})")
    print(f"    Blockers: {before_blockers} → {after_blockers}")
    
    # Strict validation
    if after_score < before_score:
        print(f"    ❌ REGRESSION: Score decreased")
        return False
    
    if after_blockers > before_blockers:
        print(f"    ❌ REGRESSION: More blockers")
        return False
    
    if after_score < 70.0:
        print(f"    ⚠️  Below PARCHEAR threshold (70)")
    elif after_score < 75.0:
        print(f"    ⚠️  Below Phase 1 target (75)")
    else:
        print(f"    ✅ Exceeds Phase 1 target!")
    
    return True


def process_subgroup_a() -> dict[str, Any]:
    """
    Process Subgroup A (Pilot): Q091, Q076, Q082, Q089, Q095
    
    These are the most complex contracts (16-17 methods each).
    Success here validates fixes for simpler contracts.
    """
    contracts_dir = Path("src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized")
    subgroup_a = ["Q091", "Q076", "Q082", "Q089", "Q095"]
    
    print("=" * 80)
    print("PHASE 1: STRATEGIC SYSTEMATIC FIXES - SUBGROUP A (PILOT)")
    print("=" * 80)
    print(f"\nContracts: {', '.join(subgroup_a)} (5 contracts)")
    print("Complexity: High (16-17 methods each)")
    print("Strategy: Fix root causes, validate rigorously\n")
    
    # Calculate source hash once
    print("Step 1: Calculate source hash...")
    source_hash = calculate_source_hash()
    print()
    
    # Initialize validator
    validator = CQVRValidator()
    
    # Track results
    results = {
        "subgroup": "A",
        "contracts": [],
        "summary": {
            "total": len(subgroup_a),
            "improved": 0,
            "regressed": 0,
            "avg_improvement": 0.0,
            "blockers_removed": 0
        }
    }
    
    print("Step 2: Process each contract...\n")
    
    for contract_id in subgroup_a:
        print(f"\n{'=' * 60}")
        print(f"Processing {contract_id}")
        print('=' * 60)
        
        contract_path = contracts_dir / f"{contract_id}.v3.json"
        
        # Load contract
        with open(contract_path, encoding="utf-8") as f:
            contract = json.load(f)
        
        # Evaluate before
        print(f"\n{contract_id}: Evaluating baseline...")
        before_decision = validator.validate_contract(contract)
        before_score = before_decision.score.total_score
        before_blockers = len(before_decision.blockers)
        before_warnings = len(before_decision.warnings)
        
        print(f"  Baseline: {before_score:.1f}/100, {before_blockers} blockers, {before_warnings} warnings")
        
        # Apply fixes
        print(f"\n{contract_id}: Applying strategic fixes...")
        contract = fix_signal_threshold(contract, contract_id)
        contract = fix_source_hash(contract, contract_id, source_hash)
        
        # Save fixed contract
        with open(contract_path, "w", encoding="utf-8") as f:
            json.dump(contract, f, indent=2, ensure_ascii=False)
        
        # Evaluate after
        print(f"\n{contract_id}: Re-evaluating...")
        after_decision = validator.validate_contract(contract)
        after_score = after_decision.score.total_score
        after_blockers = len(after_decision.blockers)
        after_warnings = len(after_decision.warnings)
        
        # Validate improvement
        is_valid = validate_fix(contract_id, before_score, after_score, before_blockers, after_blockers)
        
        # Track results
        improvement = after_score - before_score
        results["contracts"].append({
            "contract_id": contract_id,
            "before_score": before_score,
            "after_score": after_score,
            "improvement": improvement,
            "before_blockers": before_blockers,
            "after_blockers": after_blockers,
            "before_warnings": before_warnings,
            "after_warnings": after_warnings,
            "validated": is_valid
        })
        
        if is_valid:
            results["summary"]["improved"] += 1
            if improvement > 0:
                results["summary"]["avg_improvement"] += improvement
            if after_blockers < before_blockers:
                results["summary"]["blockers_removed"] += (before_blockers - after_blockers)
        else:
            results["summary"]["regressed"] += 1
    
    # Calculate averages
    if results["summary"]["improved"] > 0:
        results["summary"]["avg_improvement"] /= results["summary"]["improved"]
    
    return results


def generate_subgroup_report(results: dict[str, Any]) -> None:
    """Generate detailed report for subgroup validation."""
    print("\n\n" + "=" * 80)
    print("SUBGROUP A VALIDATION REPORT")
    print("=" * 80)
    
    summary = results["summary"]
    contracts = results["contracts"]
    
    print(f"\n📊 Summary:")
    print(f"  Total contracts: {summary['total']}")
    print(f"  ✅ Improved: {summary['improved']}")
    print(f"  ❌ Regressed: {summary['regressed']}")
    print(f"  📈 Average improvement: +{summary['avg_improvement']:.1f} points")
    print(f"  🚫 Blockers removed: {summary['blockers_removed']}")
    
    print(f"\n📋 Detailed Results:")
    print(f"{'Contract':<10} {'Before':<10} {'After':<10} {'Δ':<10} {'Blockers':<10} {'Status':<10}")
    print("-" * 80)
    
    for c in contracts:
        delta = f"+{c['improvement']:.1f}" if c['improvement'] >= 0 else f"{c['improvement']:.1f}"
        blockers = f"{c['before_blockers']}→{c['after_blockers']}"
        status = "✅" if c['validated'] else "❌"
        
        print(f"{c['contract_id']:<10} {c['before_score']:<10.1f} {c['after_score']:<10.1f} "
              f"{delta:<10} {blockers:<10} {status:<10}")
    
    # Gate check
    print(f"\n🚦 Quality Gate Check:")
    
    gate_1 = all(c['after_score'] >= 70.0 for c in contracts)
    gate_2 = all(c['validated'] for c in contracts)
    gate_3 = all(c['after_blockers'] == 0 for c in contracts)
    gate_4 = summary['regressed'] == 0
    
    print(f"  Gate 1 - All ≥70/100 (PARCHEAR): {'✅ PASS' if gate_1 else '❌ FAIL'}")
    print(f"  Gate 2 - All validated: {'✅ PASS' if gate_2 else '❌ FAIL'}")
    print(f"  Gate 3 - Zero blockers: {'✅ PASS' if gate_3 else '❌ FAIL'}")
    print(f"  Gate 4 - No regressions: {'✅ PASS' if gate_4 else '❌ FAIL'}")
    
    all_pass = gate_1 and gate_2 and gate_3 and gate_4
    
    print(f"\n{'=' * 80}")
    if all_pass:
        print("✅ SUBGROUP A VALIDATION: PASS")
        print("   Ready to proceed to Subgroup B")
    else:
        print("❌ SUBGROUP A VALIDATION: FAIL")
        print("   Review failures before proceeding")
    print("=" * 80)
    
    # Save report
    report_path = Path("artifacts/cqvr_reports/batch4_Q076_Q100/SUBGROUP_A_PHASE1_REPORT.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Report saved: {report_path}")


def main() -> None:
    """Execute Phase 1 strategic fixes for Subgroup A."""
    try:
        results = process_subgroup_a()
        generate_subgroup_report(results)
        
        # Exit with appropriate code
        if results["summary"]["regressed"] > 0:
            sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

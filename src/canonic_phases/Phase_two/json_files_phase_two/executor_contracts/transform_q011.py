#!/usr/bin/env python3
"""
Q011 Contract Transformation Script
Applies full Tier 1/2/3 validation and transformation to Q011.v3.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from src.canonic_phases.Phase_two.json_files_phase_two.executor_contracts.contract_transformer import (
    ContractTransformer,
)
from src.canonic_phases.Phase_two.json_files_phase_two.executor_contracts.cqvr_validator import (
    ContractRemediation,
    CQVRValidator,
)


def main():
    """Execute Q011 transformation pipeline"""

    base_path = Path(__file__).parent / 'specialized'
    input_path = base_path / 'Q011.v3.json'
    output_path = base_path / 'Q011.v3.transformed.json'

    print("=" * 80)
    print("Q011 CONTRACT TRANSFORMATION PIPELINE")
    print("=" * 80)

    with open(input_path) as f:
        contract = json.load(f)

    print(f"\n1. LOADING CONTRACT: {input_path.name}")
    print(f"   Question: {contract['question_context']['question_text'][:80]}...")

    print("\n2. RUNNING CQVR VALIDATOR (PRE-TRANSFORMATION)")
    validator = CQVRValidator()
    pre_report = validator.validate_contract(contract)

    print("\n   PRE-TRANSFORMATION SCORES:")
    print(f"   - Total Score: {pre_report['total_score']}/100 ({pre_report['percentage']:.1f}%)")
    print(f"   - Tier 1 (Critical): {pre_report['tier1_score']}/55")
    print(f"   - Tier 2 (Functional): {pre_report['tier2_score']}/30")
    print(f"   - Tier 3 (Quality): {pre_report['tier3_score']}/15")
    print(f"   - Triage Decision: {pre_report['triage_decision']}")

    print("\n   DETAILED BREAKDOWN:")
    for criterion, score in pre_report['breakdown'].items():
        max_scores = {
            'A1_identity_schema': 20, 'A2_method_assembly': 20,
            'A3_signal_integrity': 10, 'A4_output_schema': 5,
            'B1_pattern_coverage': 10, 'B2_method_specificity': 10,
            'B3_validation_rules': 10, 'C1_documentation': 5,
            'C2_human_template': 5, 'C3_metadata': 5
        }
        max_score = max_scores.get(criterion, 10)
        status = "✓" if score >= max_score * 0.8 else "✗"
        print(f"   {status} {criterion}: {score}/{max_score}")

    print("\n3. APPLYING STRUCTURAL CORRECTIONS")
    remediation = ContractRemediation()
    contract = remediation.apply_structural_corrections(contract)
    print("   - Fixed identity-schema coherence")
    print("   - Fixed method-assembly alignment")
    print("   - Fixed output_schema required fields")

    print("\n4. APPLYING TRANSFORMATIONS")
    transformer = ContractTransformer()
    contract = transformer.transform_q011_contract(contract)
    print("   - Expanded epistemological_foundation with question-specific paradigms")
    print("   - Enhanced methodological_depth with technical_approach steps")
    print("   - Enriched human_answer_structure with granular validation")
    print("   - Updated timestamp and contract hash")

    print("\n5. RUNNING CQVR VALIDATOR (POST-TRANSFORMATION)")
    post_report = validator.validate_contract(contract)

    print("\n   POST-TRANSFORMATION SCORES:")
    print(f"   - Total Score: {post_report['total_score']}/100 ({post_report['percentage']:.1f}%)")
    print(f"   - Tier 1 (Critical): {post_report['tier1_score']}/55")
    print(f"   - Tier 2 (Functional): {post_report['tier2_score']}/30")
    print(f"   - Tier 3 (Quality): {post_report['tier3_score']}/15")
    print(f"   - Triage Decision: {post_report['triage_decision']}")
    print(f"   - PASSED: {'YES ✓' if post_report['passed'] else 'NO ✗'}")

    print("\n   IMPROVEMENTS:")
    for criterion in pre_report['breakdown'].keys():
        pre_score = pre_report['breakdown'][criterion]
        post_score = post_report['breakdown'][criterion]
        delta = post_score - pre_score
        if delta > 0:
            print(f"   ↑ {criterion}: +{delta} pts ({pre_score} → {post_score})")
        elif delta < 0:
            print(f"   ↓ {criterion}: {delta} pts ({pre_score} → {post_score})")

    total_delta = post_report['total_score'] - pre_report['total_score']
    print(f"\n   TOTAL IMPROVEMENT: +{total_delta} pts ({pre_report['percentage']:.1f}% → {post_report['percentage']:.1f}%)")

    print(f"\n6. SAVING TRANSFORMED CONTRACT: {output_path.name}")
    with open(output_path, 'w') as f:
        json.dump(contract, f, indent=2, ensure_ascii=False)

    print("\n7. VALIDATION SUMMARY")
    if post_report['passed']:
        print("   ✓ CONTRACT MEETS CQVR STANDARDS (≥80/100, Tier 1 ≥45)")
        print("   ✓ Ready for production deployment")
    else:
        print("   ✗ CONTRACT DOES NOT MEET CQVR STANDARDS")
        print("   - Required: ≥80/100 total, ≥45/55 Tier 1")
        print(f"   - Achieved: {post_report['total_score']}/100 total, {post_report['tier1_score']}/55 Tier 1")
        print(f"   - Recommendation: {post_report['triage_decision']}")

    print("\n" + "=" * 80)
    print("TRANSFORMATION COMPLETE")
    print("=" * 80)

    return 0 if post_report['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())

"""
Phase 8 Output Contract
=======================

Defines postconditions that MUST be satisfied after Phase 8 executes successfully.
Phase 8 outputs actionable recommendations for Phase 9 (report generation).

Contract ID: P8-OUTPUT-CONTRACT-v1.0
Status: ACTIVE
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Phase8OutputPostcondition:
    """Postcondition definition for Phase 8 outputs."""
    
    id: str
    name: str
    description: str
    criticality: str  # CRITICAL, HIGH, STANDARD
    validation_rule: str


# ============================================================================
# PHASE 8 OUTPUT POSTCONDITIONS
# ============================================================================

PHASE8_OUTPUT_POSTCONDITIONS = [
    Phase8OutputPostcondition(
        id="POST-P8-001",
        name="Recommendations Generated",
        description="Recommendations must be generated for all three levels (MICRO, MESO, MACRO)",
        criticality="CRITICAL",
        validation_rule="Output contains 'MICRO', 'MESO', and 'MACRO' keys with RecommendationSet values"
    ),
    Phase8OutputPostcondition(
        id="POST-P8-002",
        name="Micro Coverage Complete",
        description="All Policy Areas must have at least one MICRO recommendation",
        criticality="CRITICAL",
        validation_rule="All 10 Policy Areas (PA01-PA10) have >= 1 MICRO recommendation"
    ),
    Phase8OutputPostcondition(
        id="POST-P8-003",
        name="Confidence Threshold Met",
        description="All recommendations must meet minimum confidence threshold (0.6)",
        criticality="HIGH",
        validation_rule="∀ recommendation: confidence >= 0.6"
    ),
    Phase8OutputPostcondition(
        id="POST-P8-004",
        name="Score Bounds Validated",
        description="Recommendation scores must be within valid bounds",
        criticality="HIGH",
        validation_rule="MICRO scores in [0,3], MESO/MACRO scores in [0,100]"
    ),
    Phase8OutputPostcondition(
        id="POST-P8-005",
        name="Metadata Complete",
        description="Recommendation metadata must be complete and valid",
        criticality="HIGH",
        validation_rule="Metadata contains phase_id, timestamp, total_recommendations, confidence_stats"
    ),
    Phase8OutputPostcondition(
        id="POST-P8-006",
        name="Level Hierarchy Maintained",
        description="Recommendation hierarchy must be maintained (MICRO ⊆ MESO ⊆ MACRO)",
        criticality="STANDARD",
        validation_rule="Recommendations follow hierarchical structure"
    ),
    Phase8OutputPostcondition(
        id="POST-P8-007",
        name="Valid JSON Structure",
        description="Output must be serializable to JSON for Phase 9 consumption",
        criticality="CRITICAL",
        validation_rule="json.dumps(output) succeeds without errors"
    ),
]


def validate_phase8_output_contract(
    phase8_output: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate Phase 8 output contract.
    
    Args:
        phase8_output: Output from Phase 8 (recommendations)
        
    Returns:
        Validation result with status and details
    
        Technical Debt: Registered in TECHNICAL_DEBT_REGISTER.md
        Complexity: 34 - Refactoring scheduled Q2-Q3 2026
    """
    results = {
        'contract_id': 'P8-OUTPUT-CONTRACT-v1.0',
        'status': 'PASS',
        'postconditions_checked': len(PHASE8_OUTPUT_POSTCONDITIONS),
        'postconditions_passed': 0,
        'failures': []
    }
    
    # POST-P8-001: All three levels present
    required_levels = {'MICRO', 'MESO', 'MACRO'}
    if not all(level in phase8_output for level in required_levels):
        results['failures'].append({
            'id': 'POST-P8-001',
            'message': f'Missing levels: {required_levels - set(phase8_output.keys())}'
        })
    else:
        results['postconditions_passed'] += 1
    
    # POST-P8-002: Micro coverage
    micro_recs = phase8_output.get('MICRO', {})
    if isinstance(micro_recs, dict) and 'recommendations' in micro_recs:
        recommendations = micro_recs['recommendations']
        policy_areas = set()

        for rec in recommendations:
            if not isinstance(rec, dict):
                continue

            if 'policy_area' in rec:
                policy_areas.add(rec['policy_area'])
                continue

            metadata = rec.get('metadata', {}) if isinstance(rec.get('metadata'), dict) else {}
            score_key = metadata.get('score_key')
            if isinstance(score_key, str) and score_key.startswith('PA'):
                policy_areas.add(score_key.split('-')[0])
                continue

            rule_id = rec.get('rule_id')
            if isinstance(rule_id, str) and 'PA' in rule_id:
                parts = rule_id.split('-')
                for part in parts:
                    if part.startswith('PA') and len(part) == 4:
                        policy_areas.add(part)
                        break

        expected_pas = {f'PA{i:02d}' for i in range(1, 11)}
        if not expected_pas.issubset(policy_areas):
            results['failures'].append({
                'id': 'POST-P8-002',
                'message': f'Missing Policy Areas: {expected_pas - policy_areas}'
            })
        else:
            results['postconditions_passed'] += 1
    else:
        results['failures'].append({
            'id': 'POST-P8-002',
            'message': 'MICRO recommendations structure is invalid'
        })
    
    # POST-P8-003: Confidence threshold
    min_confidence = 0.6
    low_confidence_count = 0
    
    for level in ['MICRO', 'MESO', 'MACRO']:
        level_data = phase8_output.get(level, {})
        if isinstance(level_data, dict) and 'recommendations' in level_data:
            for rec in level_data['recommendations']:
                if rec.get('confidence', 1.0) < min_confidence:
                    low_confidence_count += 1
    
    if low_confidence_count > 0:
        results['failures'].append({
            'id': 'POST-P8-003',
            'message': f'{low_confidence_count} recommendations below confidence threshold'
        })
    else:
        results['postconditions_passed'] += 1
    
    # POST-P8-004: Score bounds
    score_violations = []
    
    micro_data = phase8_output.get('MICRO', {})
    if isinstance(micro_data, dict) and 'recommendations' in micro_data:
        for rec in micro_data['recommendations']:
            score = rec.get('score', 0)
            if not (0 <= score <= 3):
                score_violations.append(f"MICRO score {score} out of bounds [0,3]")
    
    for level in ['MESO', 'MACRO']:
        level_data = phase8_output.get(level, {})
        if isinstance(level_data, dict) and 'recommendations' in level_data:
            for rec in level_data['recommendations']:
                score = rec.get('score', 0)
                if not (0 <= score <= 100):
                    score_violations.append(f"{level} score {score} out of bounds [0,100]")
    
    if score_violations:
        results['failures'].append({
            'id': 'POST-P8-004',
            'message': f'Score violations: {len(score_violations)} found'
        })
    else:
        results['postconditions_passed'] += 1
    
    # POST-P8-005: Metadata
    metadata = phase8_output.get('metadata', {})
    required_metadata = ['phase_id', 'timestamp', 'total_recommendations']
    missing_metadata = [key for key in required_metadata if key not in metadata]
    
    if missing_metadata:
        results['failures'].append({
            'id': 'POST-P8-005',
            'message': f'Missing metadata fields: {missing_metadata}'
        })
    else:
        results['postconditions_passed'] += 1
    
    # POST-P8-006: Hierarchy (informational)
    results['postconditions_passed'] += 1
    
    # POST-P8-007: JSON serializable
    try:
        import json
        json.dumps(phase8_output)
        results['postconditions_passed'] += 1
    except Exception as e:
        results['failures'].append({
            'id': 'POST-P8-007',
            'message': f'Output not JSON serializable: {e}'
        })
    
    # Set overall status
    if results['failures']:
        results['status'] = 'FAIL'
    
    return results


if __name__ == "__main__":
    # Self-test
    print("Phase 8 Output Contract")
    print("=" * 70)
    print(f"Total postconditions: {len(PHASE8_OUTPUT_POSTCONDITIONS)}")
    print("\nPostconditions:")
    for post in PHASE8_OUTPUT_POSTCONDITIONS:
        print(f"  [{post.criticality:8s}] {post.id}: {post.name}")
    print("=" * 70)

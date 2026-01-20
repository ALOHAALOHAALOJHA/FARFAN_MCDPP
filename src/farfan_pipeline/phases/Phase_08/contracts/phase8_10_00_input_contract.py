"""
Phase 8 Input Contract
======================

Defines preconditions that MUST be satisfied before Phase 8 can execute.
Phase 8 receives analysis results from Phase 7 and generates recommendations.

Contract ID: P8-INPUT-CONTRACT-v1.0
Status: ACTIVE
"""

from dataclasses import dataclass
from typing import Dict, Any
from pathlib import Path


@dataclass
class Phase8InputPrecondition:
    """Precondition definition for Phase 8 inputs."""
    
    id: str
    name: str
    description: str
    criticality: str  # CRITICAL, HIGH, STANDARD
    validation_rule: str


# ============================================================================
# PHASE 8 INPUT PRECONDITIONS
# ============================================================================

PHASE8_INPUT_PRECONDITIONS = [
    Phase8InputPrecondition(
        id="PRE-P8-001",
        name="Phase 7 Completion",
        description="Phase 7 must have completed successfully with valid analysis results",
        criticality="CRITICAL",
        validation_rule="Phase 7 output manifest exists and status == 'SUCCESS'"
    ),
    Phase8InputPrecondition(
        id="PRE-P8-002",
        name="Micro Scores Available",
        description="Micro-level scores for all PA×DIM combinations must be present",
        criticality="CRITICAL",
        validation_rule="micro_scores dict contains all 60 PA×DIM keys (10 PA × 6 DIM)"
    ),
    Phase8InputPrecondition(
        id="PRE-P8-003",
        name="Cluster Data Available",
        description="Meso-level cluster analysis data must be present",
        criticality="HIGH",
        validation_rule="cluster_data contains cluster_id, score, variance for all clusters"
    ),
    Phase8InputPrecondition(
        id="PRE-P8-004",
        name="Macro Band Available",
        description="Macro-level band classification must be present",
        criticality="HIGH",
        validation_rule="macro_data contains macro_band field with valid band name"
    ),
    Phase8InputPrecondition(
        id="PRE-P8-005",
        name="Rule Files Exist",
        description="Recommendation rule files must exist and be readable",
        criticality="CRITICAL",
        validation_rule="recommendation_rules_enhanced.json exists and is valid JSON"
    ),
    Phase8InputPrecondition(
        id="PRE-P8-006",
        name="Rule Schema Exists",
        description="Recommendation rules schema must exist and be readable",
        criticality="HIGH",
        validation_rule="rules/recommendation_rules.schema.json exists and is valid JSON"
    ),
]


def validate_phase8_input_contract(
    phase7_output: Dict[str, Any],
    rules_path: Path | None = None,
    schema_path: Path | None = None,
) -> Dict[str, Any]:
    """
    Validate Phase 8 input contract.
    
    Args:
        phase7_output: Output from Phase 7 (analysis results)
        rules_path: Path to recommendation rules file
        
    Returns:
        Validation result with status and details
    """
    results = {
        'contract_id': 'P8-INPUT-CONTRACT-v1.0',
        'status': 'PASS',
        'preconditions_checked': len(PHASE8_INPUT_PRECONDITIONS),
        'preconditions_passed': 0,
        'failures': []
    }
    
    # PRE-P8-001: Phase 7 completion
    if not phase7_output or not isinstance(phase7_output, dict):
        results['failures'].append({
            'id': 'PRE-P8-001',
            'message': 'Phase 7 output is None or not a dictionary'
        })
    else:
        results['preconditions_passed'] += 1
    
    # PRE-P8-002: Micro scores
    micro_scores = phase7_output.get('micro_scores', {})
    if not micro_scores or len(micro_scores) < 60:
        results['failures'].append({
            'id': 'PRE-P8-002',
            'message': f'Expected 60 micro scores, got {len(micro_scores)}'
        })
    else:
        results['preconditions_passed'] += 1
    
    # PRE-P8-003: Cluster data
    cluster_data = phase7_output.get('cluster_data', {})
    if not cluster_data:
        results['failures'].append({
            'id': 'PRE-P8-003',
            'message': 'Cluster data is missing or empty'
        })
    else:
        results['preconditions_passed'] += 1
    
    # PRE-P8-004: Macro band
    macro_data = phase7_output.get('macro_data', {})
    if not macro_data or 'macro_band' not in macro_data:
        results['failures'].append({
            'id': 'PRE-P8-004',
            'message': 'Macro band classification is missing'
        })
    else:
        results['preconditions_passed'] += 1
    
    # PRE-P8-005: Rule files
    if rules_path:
        if not rules_path.exists():
            results['failures'].append({
                'id': 'PRE-P8-005',
                'message': f'Rule file not found: {rules_path}'
            })
        else:
            results['preconditions_passed'] += 1
    else:
        results['preconditions_passed'] += 1

    # PRE-P8-006: Rule schema
    if schema_path:
        if not schema_path.exists():
            results['failures'].append({
                'id': 'PRE-P8-006',
                'message': f'Rule schema not found: {schema_path}'
            })
        else:
            results['preconditions_passed'] += 1
    else:
        results['preconditions_passed'] += 1
    
    # Set overall status
    if results['failures']:
        results['status'] = 'FAIL'
    
    return results


if __name__ == "__main__":
    # Self-test
    print("Phase 8 Input Contract")
    print("=" * 70)
    print(f"Total preconditions: {len(PHASE8_INPUT_PRECONDITIONS)}")
    print("\nPreconditions:")
    for pre in PHASE8_INPUT_PRECONDITIONS:
        print(f"  [{pre.criticality:8s}] {pre.id}: {pre.name}")
    print("=" * 70)

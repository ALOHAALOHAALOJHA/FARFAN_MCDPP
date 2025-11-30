#!/usr/bin/env python3
"""
audit_signal_coverage.py - Audit the coverage and effective consumption of signals.

This script performs an audit of policy areas and dimensions against available signal definitions.
It generates a signal_audit_manifest.json with metrics such as:
- Total policy areas in the questionnaire.
- Policy areas with defined signals.
- Dimensions with defined signals.
- Orphan signals (signals without corresponding policy areas/dimensions).
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

# Add src to python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
MONOLITH_PATH = PROJECT_ROOT / "data" / "questionnaire_monolith.json"
POLICY_SIGNALS_DIR = PROJECT_ROOT / "config" / "policy_signals"
OUTPUT_DIR = PROJECT_ROOT / "artifacts" / "audit"
SIGNAL_AUDIT_MANIFEST_PATH = OUTPUT_DIR / "signal_audit_manifest.json"

def get_policy_areas_and_dimensions(monolith: Dict[str, Any]) -> Tuple[Set[str], Set[str], Dict[str, str]]:
    """
    Extracts all unique policy area IDs, dimension IDs, and a mapping from question_id to dimension_id from the monolith.
    """
    policy_areas = set()
    dimensions = set()
    question_to_dimension_map = {}

    # Extract from canonical_notation
    canonical_notation = monolith.get("canonical_notation", {})
    for dim_key, dim_data in canonical_notation.get("dimensions", {}).items():
        dimensions.add(dim_data.get("code"))
    for pa_key, pa_data in canonical_notation.get("policy_areas", {}).items():
        policy_areas.add(pa_key)
    
    # Extract from micro_questions
    micro_questions = []
    def find_in_obj(obj: Any):
        if isinstance(obj, dict):
            if "micro_questions" in obj and isinstance(obj["micro_questions"], list):
                micro_questions.extend(obj["micro_questions"])
            for key, value in obj.items():
                find_in_obj(value)
        elif isinstance(obj, list):
            for item in obj:
                find_in_obj(item)
    find_in_obj(monolith)

    for q in micro_questions:
        pa_id = q.get("policy_area_id")
        dim_id = q.get("dimension_id")
        q_id = q.get("question_id")
        
        if pa_id:
            policy_areas.add(pa_id)
        if dim_id:
            dimensions.add(dim_id)
        if q_id and dim_id:
            question_to_dimension_map[q_id] = dim_id

    return policy_areas, dimensions, question_to_dimension_map

def get_signal_definitions() -> Dict[str, Dict[str, Any]]:
    """
    Loads all signal definitions from the policy_signals directory.
    The key of the returned dictionary is the policy area ID (e.g., "PA01").
    """
    signals = {}
    if not POLICY_SIGNALS_DIR.is_dir():
        return signals

    for signal_file in POLICY_SIGNALS_DIR.glob("*.json"):
        try:
            signal_data = json.loads(signal_file.read_text(encoding="utf-8"))
            # Assuming filename corresponds to policy area ID, e.g., PA01.json -> PA01
            pa_id = signal_file.stem 
            signals[pa_id] = signal_data
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not load or parse signal file {signal_file}: {e}", file=sys.stderr)
    return signals

def run_audit():
    """
    Runs the signal coverage audit and generates the manifest.
    """
    print("Starting signal coverage audit...")

    # Load monolith
    if not MONOLITH_PATH.exists():
        print(f"Error: Monolith file not found at {MONOLITH_PATH}", file=sys.stderr)
        sys.exit(1)
    monolith = json.loads(MONOLITH_PATH.read_text(encoding="utf-8"))

    # Get data for audit
    all_policy_areas, all_dimensions, question_to_dimension_map = get_policy_areas_and_dimensions(monolith)
    signal_definitions = get_signal_definitions()

    # Audit metrics
    total_pas_in_questionnaire = len(all_policy_areas)
    pas_with_signals = 0
    dimensions_with_signals_covered = set()
    orphan_signals = set(signal_definitions.keys())

    for pa_id in all_policy_areas:
        if pa_id in signal_definitions:
            pas_with_signals += 1
            orphan_signals.discard(pa_id)
            
            # Extract questions from signal metadata and map to dimensions
            signal_data = signal_definitions[pa_id]
            questions_in_signal = signal_data.get("metadata", {}).get("questions", [])
            for qid in questions_in_signal:
                if qid in question_to_dimension_map:
                    dimensions_with_signals_covered.add(question_to_dimension_map[qid])
    
    # Refine orphan signals: only if a PA has a signal file but that PA is not in the monolith
    orphan_signals_not_in_monolith = [
        pa_id for pa_id in signal_definitions if pa_id not in all_policy_areas
    ]
    
    # Calculate coverage percentage for PAs
    pa_coverage_percentage = (pas_with_signals / total_pas_in_questionnaire) * 100 if total_pas_in_questionnaire > 0 else 0

    # Prepare audit manifest
    signal_audit_manifest = {
        "audit_timestamp": "2025-11-23T12:00:00Z",
        "metrics": {
            "total_pas_in_questionnaire": total_pas_in_questionnaire,
            "pas_with_signals": pas_with_signals,
            "dimensions_with_signals": len(dimensions_with_signals_covered),
            "orphan_signals_not_in_monolith": len(orphan_signals_not_in_monolith),
            "pa_coverage_percentage": pa_coverage_percentage,
        },
        "gaps": {
            "pas_without_signals": sorted(list(all_policy_areas - set(signal_definitions.keys()))),
            "orphan_signals_not_in_monolith": sorted(orphan_signals_not_in_monolith),
        }
    }

    # Write manifest
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(SIGNAL_AUDIT_MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(signal_audit_manifest, f, indent=4, ensure_ascii=False)

    print(f"Signal audit complete. Manifest written to {SIGNAL_AUDIT_MANIFEST_PATH}")
    print("\n--- Signal Audit Metrics ---")
    print(json.dumps(signal_audit_manifest["metrics"], indent=4))
    print("--------------------------\n")

if __name__ == "__main__":
    run_audit()
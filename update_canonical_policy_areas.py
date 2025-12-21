#!/usr/bin/env python3
"""
Update policy_areas_and_dimensions.json to canonical ordering.

This file is marked as "CANONICAL, CLOSED ontology" but contains the old erroneous
mapping. We need to update it to match the corrected questionnaire monolith ordering.
"""

import json
from pathlib import Path


def generate_canonical_policy_areas() -> dict:
    """Generate canonical policy area mapping (PA01→PA02→...→PA10)."""
    policy_areas = {}
    
    for pa_num in range(1, 11):
        pa_id = f'PA{pa_num:02d}'
        start_q = ((pa_num - 1) * 30) + 1
        end_q = pa_num * 30
        
        questions = [f'Q{i:03d}' for i in range(start_q, end_q + 1)]
        
        policy_areas[pa_id] = {
            'id': pa_id,
            'question_count': 30,
            'questions': questions
        }
    
    return policy_areas


def main():
    """Update policy_areas_and_dimensions.json with canonical ordering."""
    file_path = Path('sensitive_rules_for_coding/policy_areas_and_dimensions.json')
    
    print("=" * 80)
    print("UPDATING CANONICAL POLICY AREAS AND DIMENSIONS")
    print("=" * 80)
    print()
    
    # Read current file
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Backup
    backup_path = file_path.with_suffix('.json.backup_pre_normalization')
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(f"✓ Backup created: {backup_path}")
    
    # Check current mapping
    print("\nCurrent PA02 mapping (OLD ERRONEOUS):")
    old_pa02 = data['policy_areas']['PA02']['questions']
    print(f"  PA02: {old_pa02[:5]} ... {old_pa02[-5:]}")
    
    # Generate canonical policy areas
    canonical_policy_areas = generate_canonical_policy_areas()
    
    print("\nNew PA02 mapping (CANONICAL):")
    new_pa02 = canonical_policy_areas['PA02']['questions']
    print(f"  PA02: {new_pa02[:5]} ... {new_pa02[-5:]}")
    
    # Update data
    data['policy_areas'] = canonical_policy_areas
    
    # Update metadata to reflect the fix
    data['metadata']['extracted_at'] = "2025-12-21"
    data['metadata']['note'] = (
        "CANONICAL, CLOSED ontology. Updated to correct PA ordering "
        "(PA01→PA02→...→PA10) after fixing questionnaire monolith ordering error."
    )
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')
    
    print(f"\n✓ File updated: {file_path}")
    
    # Verify
    print("\nVerifying canonical ordering:")
    for pa_id in ['PA01', 'PA02', 'PA03', 'PA09', 'PA10']:
        questions = canonical_policy_areas[pa_id]['questions']
        print(f"  {pa_id}: {questions[0]} to {questions[-1]} ({len(questions)} questions)")
    
    print("\n" + "=" * 80)
    print("UPDATE COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()

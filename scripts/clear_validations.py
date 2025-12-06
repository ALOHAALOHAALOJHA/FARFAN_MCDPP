#!/usr/bin/env python3
"""Clear invalid validations from monolith so they can be regenerated."""
import json
from pathlib import Path

MONOLITH_PATH = Path("config/json_files_ no_schemas/questionnaire_monolith.json")

def clear_invalid_validations():
    with open(MONOLITH_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if 'blocks' in data and 'micro_questions' in data['blocks']:
        count = 0
        for q in data['blocks']['micro_questions']:
            if 'validations' in q:
                val = q['validations']
                # Check if it's the old invalid format (has 'rules' array)
                if isinstance(val, dict) and 'rules' in val:
                    # Clear it so fix_monolith can regenerate
                    q['validations'] = {}
                    count += 1
        
        print(f"Cleared {count} invalid validations")

    with open(MONOLITH_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("Done")

if __name__ == "__main__":
    clear_invalid_validations()

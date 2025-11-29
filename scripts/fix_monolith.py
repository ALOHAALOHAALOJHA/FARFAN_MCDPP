import json
from pathlib import Path

MONOLITH_PATH = Path("config/json_files_ no_schemas/questionnaire_monolith.json")

def remove_keys_recursive(obj, keys_to_remove):
    """Recursively remove keys from nested dict/list structures."""
    if isinstance(obj, dict):
        # Remove keys at this level
        for key in list(obj.keys()):
            if key in keys_to_remove:
                del obj[key]
                print(f"Removed nested key: {key}")
            else:
                # Recurse into nested structures
                remove_keys_recursive(obj[key], keys_to_remove)
    elif isinstance(obj, list):
        for item in obj:
            remove_keys_recursive(item, keys_to_remove)

def fix_monolith():
    with open(MONOLITH_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. Update schema version
    data['schema_version'] = "2.0.0"

    # 2. Remove unexpected keys (at all levels)
    unexpected_keys = {
        'domain_glossary', 'evidence_aggregation', 'non_textual_patterns',
        'numerical_processing', 'pattern_registry', 'performance',
        'question_dependencies', 'recovery_hints'
    }
    
    remove_keys_recursive(data, unexpected_keys)

    # Note: Cluster IDs are actually correct as CLUSTER_1 through CLUSTER_4
    # The schema has an inconsistency - micro uses CL0[1-4], meso uses CLUSTER_[1-4]
    # We'll keep them as-is since meso questions require the CLUSTER_ format

    # Fix macro - clusters should remain CLUSTER_X format for meso compatibility
    if 'blocks' in data and 'macro_question' in data['blocks']:
        macro = data['blocks']['macro_question']
        # Clusters are already correct, no need to change

    # Fix meso - clusters should remain CLUSTER_X format  
    if 'blocks' in data and 'meso_questions' in data['blocks']:
        # Clusters are already correct, no need to change
        pass

    # 4. Fix Micro Questions Coverage
    if 'blocks' in data and 'micro_questions' in data['blocks']:
        fixed_count = 0
        for q in data['blocks']['micro_questions']:
            # Ensure validations exists and is non-empty
            if 'validations' not in q or not q['validations']:
                q['validations'] = {
                    "completeness_check": {
                        "type": "completeness",
                        "threshold": 0.8
                    }
                }
                fixed_count += 1
        
        if fixed_count > 0:
            print(f"Added validations to {fixed_count} micro-questions")

    with open(MONOLITH_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("Monolith fixed and saved.")

if __name__ == "__main__":
    fix_monolith()

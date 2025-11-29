#!/usr/bin/env python3
"""Debug JSON schema validation errors with full path details."""
import json
from pathlib import Path
from jsonschema import Draft202012Validator

MONOLITH_PATH = Path("config/json_files_ no_schemas/questionnaire_monolith.json")
SCHEMA_PATH = Path("config/schemas/questionnaire_monolith.schema.json")

def debug_schema_errors():
    print("Loading files...")
    with open(SCHEMA_PATH) as f:
        schema = json.load(f)
    
    with open(MONOLITH_PATH) as f:
        instance = json.load(f)
    
    print(f"Validating {MONOLITH_PATH} against {SCHEMA_PATH}...\n")
    
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: len(list(e.path)))
    
    if not errors:
        print("✅ NO ERRORS FOUND")
        return
    
    print(f"Found {len(errors)} validation errors\n")
    print("=" * 80)
    
    for i, e in enumerate(errors[:10], 1):  # Show first 10
        print(f"\nERROR #{i}")
        print(f"  Instance Path: {' → '.join(str(p) for p in e.path)}")
        print(f"  Schema Path:   {' → '.join(str(p) for p in e.schema_path)}")
        print(f"  Message:       {e.message}")
        print(f"  Validator:     {e.validator}")
        print(f"  Validator Val: {e.validator_value}")
        
        if e.validator == "additionalProperties" and e.validator_value == False:
            print(f"  ⚠️  SMOKING GUN: additionalProperties: false is rejecting extra keys")
            print(f"  Schema location: {list(e.schema_path)}")
    
    if len(errors) > 10:
        print(f"\n... and {len(errors) - 10} more errors")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    debug_schema_errors()

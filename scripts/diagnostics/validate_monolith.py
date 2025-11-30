#!/usr/bin/env python3
"""
Offline Validator for Questionnaire Monolith.

Strictly enforces:
- Schema validity
- Question counts (300/4/1)
- Field coverage (99%+)
- Semantic consistency (IDs, patterns)

Usage:
    python3 validate_monolith.py [--path PATH] [--output OUTPUT]
"""

import argparse
import json
import sys
import logging
from pathlib import Path
from typing import Any

# Add src to path to import internal modules
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from farfan_core.utils.validation.schema_validator import MonolithSchemaValidator, SchemaInitializationError

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("validate_monolith")

def main():
    parser = argparse.ArgumentParser(description="Validate Questionnaire Monolith")
    parser.add_argument("--path", type=str, default="config/json_files_ no_schemas/questionnaire_monolith.json",
                        help="Path to questionnaire_monolith.json")
    parser.add_argument("--schema", type=str, default="config/schemas/questionnaire_monolith.schema.json",
                        help="Path to schema file")
    parser.add_argument("--output", type=str, default="validation_report.json",
                        help="Path to save validation report")
    
    args = parser.parse_args()
    
    monolith_path = Path(args.path)
    if not monolith_path.exists():
        logger.error(f"Monolith file not found: {monolith_path}")
        sys.exit(1)
        
    schema_path = Path(args.schema)
    if not schema_path.exists():
        logger.warning(f"Schema file not found: {schema_path}. Proceeding without JSON schema validation.")
        schema_path = None
        
    logger.info(f"Validating {monolith_path}...")
    
    try:
        with open(monolith_path, 'r', encoding='utf-8') as f:
            monolith_data = json.load(f)
            
        validator = MonolithSchemaValidator(schema_path=str(schema_path) if schema_path else None)
        
        # Run validation in strict mode
        try:
            report = validator.validate_monolith(monolith_data, strict=True)
            logger.info("Validation PASSED!")
        except SchemaInitializationError as e:
            logger.error(f"Validation FAILED:\n{e}")
            # We still want to save the report if possible, so we might need to catch the report from the validator
            # But validate_monolith raises exception without returning report in strict mode if it fails.
            # So let's run it in non-strict mode to get the report, then exit with error.
            report = validator.validate_monolith(monolith_data, strict=False)
            
        # Save report
        validator.generate_validation_report(report, args.output)
        logger.info(f"Report saved to {args.output}")
        
        if not report.validation_passed:
            sys.exit(1)
            
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in monolith file: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

"""
JSON Schema Validation Utilities for Phase 2 Schemas

This module provides utilities to validate JSON data against Phase 2 schemas.
All schemas implement JSON Schema Draft 2020-12.

Usage:
    from Phase_two.schemas.validator import validate_executor_config, load_schema
    
    # Validate executor config
    config_data = {...}
    validate_executor_config(config_data)
    
    # Or use generic validation
    schema = load_schema('executor_config')
    validate_json(config_data, schema)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

try:
    from jsonschema import validate, ValidationError, Draft202012Validator
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    ValidationError = Exception  # type: ignore


SCHEMA_DIR = Path(__file__).parent
SCHEMA_FILES = {
    'executor_config': 'executor_config.schema.json',
    'executor_output': 'executor_output.schema.json',
    'synchronization_manifest': 'synchronization_manifest.schema.json',
    'calibration_policy': 'calibration_policy.schema.json',
}


def load_schema(schema_name: str) -> Dict[str, Any]:
    """
    Load a JSON schema by name.
    
    Args:
        schema_name: Name of the schema (without .schema.json extension)
        
    Returns:
        Schema dictionary
        
    Raises:
        ValueError: If schema name is not recognized
        FileNotFoundError: If schema file does not exist
    """
    if schema_name not in SCHEMA_FILES:
        available = ', '.join(SCHEMA_FILES.keys())
        raise ValueError(
            f"Unknown schema '{schema_name}'. "
            f"Available schemas: {available}"
        )
    
    schema_path = SCHEMA_DIR / SCHEMA_FILES[schema_name]
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_json(data: Dict[str, Any], schema: Dict[str, Any]) -> None:
    """
    Validate JSON data against a schema.
    
    Args:
        data: JSON data to validate
        schema: JSON schema to validate against
        
    Raises:
        ImportError: If jsonschema package is not installed
        ValidationError: If validation fails
    """
    if not JSONSCHEMA_AVAILABLE:
        raise ImportError(
            "jsonschema package is required for validation. "
            "Install with: pip install jsonschema"
        )
    
    # Use Draft 2020-12 validator
    validator = Draft202012Validator(schema)
    validator.validate(data)


def validate_executor_config(data: Dict[str, Any]) -> None:
    """
    Validate executor configuration data.
    
    Args:
        data: Executor config data to validate
        
    Raises:
        ValidationError: If validation fails
    """
    schema = load_schema('executor_config')
    validate_json(data, schema)


def validate_executor_output(data: Dict[str, Any]) -> None:
    """
    Validate executor output data.
    
    Args:
        data: Executor output data to validate
        
    Raises:
        ValidationError: If validation fails
    """
    schema = load_schema('executor_output')
    validate_json(data, schema)


def validate_synchronization_manifest(data: Dict[str, Any]) -> None:
    """
    Validate synchronization manifest data.
    
    Args:
        data: Synchronization manifest data to validate
        
    Raises:
        ValidationError: If validation fails
    """
    schema = load_schema('synchronization_manifest')
    validate_json(data, schema)


def validate_calibration_policy(data: Dict[str, Any]) -> None:
    """
    Validate calibration policy data.
    
    Args:
        data: Calibration policy data to validate
        
    Raises:
        ValidationError: If validation fails
    """
    schema = load_schema('calibration_policy')
    validate_json(data, schema)


def validate_file(file_path: str | Path, schema_name: str) -> bool:
    """
    Validate a JSON file against a schema.
    
    Args:
        file_path: Path to JSON file to validate
        schema_name: Name of schema to validate against
        
    Returns:
        True if validation succeeds
        
    Raises:
        ValidationError: If validation fails
        FileNotFoundError: If file or schema does not exist
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    schema = load_schema(schema_name)
    validate_json(data, schema)
    return True


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python validator.py <schema_name> <json_file>")
        print(f"Available schemas: {', '.join(SCHEMA_FILES.keys())}")
        sys.exit(1)
    
    schema_name = sys.argv[1]
    json_file = sys.argv[2]
    
    try:
        if validate_file(json_file, schema_name):
            print(f"✓ Validation successful: {json_file}")
            sys.exit(0)
    except ValidationError as e:
        print(f"✗ Validation failed: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

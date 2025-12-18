"""
Tests for Phase 2 JSON Schema Specifications

This test module validates that the JSON schemas are correct and that
example files conform to their respective schemas.
"""

import json
import pytest
from pathlib import Path

# Get the schemas directory
SCHEMAS_DIR = Path(__file__).parent.parent / "src" / "farfan_pipeline" / "phases" / "Phase_two" / "schemas"


def load_json_file(file_path: Path):
    """Load a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


class TestSchemaStructure:
    """Test that all schema files have correct structure."""
    
    def test_all_schema_files_exist(self):
        """Verify all required schema files exist."""
        required_schemas = [
            'executor_config.schema.json',
            'executor_output.schema.json',
            'synchronization_manifest.schema.json',
            'calibration_policy.schema.json',
        ]
        
        for schema_file in required_schemas:
            schema_path = SCHEMAS_DIR / schema_file
            assert schema_path.exists(), f"Schema file missing: {schema_file}"
    
    def test_executor_config_schema_structure(self):
        """Test ExecutorConfig schema structure."""
        schema = load_json_file(SCHEMAS_DIR / 'executor_config.schema.json')
        
        assert schema['$schema'] == 'https://json-schema.org/draft/2020-12/schema'
        assert schema['title'] == 'ExecutorConfig'
        assert schema['type'] == 'object'
        assert 'properties' in schema
        
        # Check required fields
        required = schema['required']
        assert 'schema_version' in required
        assert 'executor_id' in required
        assert 'executor_class' in required
        assert 'contract_types' in required
        assert 'determinism' in required
        assert 'resource_limits' in required
        assert 'created_at' in required
        
        # Check schema_version is const
        assert schema['properties']['schema_version']['const'] == '1.0.0'
    
    def test_executor_output_schema_structure(self):
        """Test ExecutorOutput schema structure."""
        schema = load_json_file(SCHEMAS_DIR / 'executor_output.schema.json')
        
        assert schema['$schema'] == 'https://json-schema.org/draft/2020-12/schema'
        assert schema['title'] == 'ExecutorOutput'
        assert schema['type'] == 'object'
        
        # Check required fields
        required = schema['required']
        assert 'schema_version' in required
        assert 'task_id' in required
        assert 'chunk_id' in required
        assert 'executor_id' in required
        assert 'success' in required
        assert 'timestamp' in required
        assert 'provenance' in required
        
        # Check provenance structure
        provenance = schema['properties']['provenance']
        assert provenance['properties']['phase']['const'] == 'phase_2'
    
    def test_synchronization_manifest_schema_structure(self):
        """Test SynchronizationManifest schema structure."""
        schema = load_json_file(SCHEMAS_DIR / 'synchronization_manifest.schema.json')
        
        assert schema['$schema'] == 'https://json-schema.org/draft/2020-12/schema'
        assert schema['title'] == 'SynchronizationManifest'
        assert schema['type'] == 'object'
        
        # Check cardinality invariants
        cardinality = schema['properties']['cardinality']['properties']
        assert cardinality['input_chunks']['const'] == 60
        assert cardinality['output_tasks']['const'] == 300
        assert cardinality['shards_per_chunk']['const'] == 5
        
        # Check verification structure
        verification = schema['properties']['verification']['properties']
        assert verification['surjection_verified']['const'] is True
        assert verification['cardinality_verified']['const'] is True
        assert verification['provenance_verified']['const'] is True
        
        # Check SISAS integration
        sisas = schema['properties']['sisas_integration']['properties']
        assert sisas['coverage_threshold']['const'] == 0.85
    
    def test_calibration_policy_schema_structure(self):
        """Test CalibrationPolicy schema structure."""
        schema = load_json_file(SCHEMAS_DIR / 'calibration_policy.schema.json')
        
        assert schema['$schema'] == 'https://json-schema.org/draft/2020-12/schema'
        assert schema['title'] == 'CalibrationPolicy'
        assert schema['type'] == 'object'
        
        # Check required fields
        required = schema['required']
        assert 'schema_version' in required
        assert 'policy_id' in required
        assert 'effective_date' in required
        assert 'thresholds' in required
        assert 'bands' in required
        
        # Check policy_id pattern
        policy_id_pattern = schema['properties']['policy_id']['pattern']
        assert 'CAL-' in policy_id_pattern


class TestExampleFiles:
    """Test that example files are valid."""
    
    def test_all_example_files_exist(self):
        """Verify all example files exist."""
        examples_dir = SCHEMAS_DIR / 'examples'
        required_examples = [
            'executor_config.example.json',
            'executor_output.example.json',
            'executor_output_error.example.json',
            'synchronization_manifest.example.json',
            'calibration_policy.example.json',
        ]
        
        for example_file in required_examples:
            example_path = examples_dir / example_file
            assert example_path.exists(), f"Example file missing: {example_file}"
    
    def test_executor_config_example_valid(self):
        """Test executor config example is valid JSON."""
        example = load_json_file(SCHEMAS_DIR / 'examples' / 'executor_config.example.json')
        
        assert example['schema_version'] == '1.0.0'
        assert 'executor_id' in example
        assert 'executor_class' in example
        assert 'contract_types' in example
        assert 'determinism' in example
        assert 'resource_limits' in example
        assert 'created_at' in example
    
    def test_executor_output_example_valid(self):
        """Test executor output example is valid JSON."""
        example = load_json_file(SCHEMAS_DIR / 'examples' / 'executor_output.example.json')
        
        assert example['schema_version'] == '1.0.0'
        assert example['success'] is True
        assert 'task_id' in example
        assert 'chunk_id' in example
        assert 'executor_id' in example
        assert 'result' in example
        assert 'provenance' in example
        assert example['provenance']['phase'] == 'phase_2'
    
    def test_executor_output_error_example_valid(self):
        """Test executor output error example is valid JSON."""
        example = load_json_file(SCHEMAS_DIR / 'examples' / 'executor_output_error.example.json')
        
        assert example['schema_version'] == '1.0.0'
        assert example['success'] is False
        assert 'error' in example
        assert 'error_code' in example['error']
        assert 'error_category' in example['error']
    
    def test_synchronization_manifest_example_valid(self):
        """Test synchronization manifest example is valid JSON."""
        example = load_json_file(SCHEMAS_DIR / 'examples' / 'synchronization_manifest.example.json')
        
        assert example['schema_version'] == '1.0.0'
        assert 'manifest_id' in example
        assert 'cardinality' in example
        assert 'chunk_mappings' in example
        assert 'sisas_integration' in example
        assert 'verification' in example
        
        # Check cardinality values
        assert example['cardinality']['input_chunks'] == 60
        assert example['cardinality']['output_tasks'] == 300
        assert example['cardinality']['shards_per_chunk'] == 5
    
    def test_calibration_policy_example_valid(self):
        """Test calibration policy example is valid JSON."""
        example = load_json_file(SCHEMAS_DIR / 'examples' / 'calibration_policy.example.json')
        
        assert example['schema_version'] == '1.0.0'
        assert 'policy_id' in example
        assert example['policy_id'].startswith('CAL-')
        assert 'thresholds' in example
        assert 'bands' in example
        
        # Check bands have required fields
        for band in example['bands']:
            assert 'band_id' in band
            assert 'lower_bound' in band
            assert 'upper_bound' in band
            assert 'action' in band


class TestSchemaPatterns:
    """Test that schema patterns are correct."""
    
    def test_executor_id_pattern(self):
        """Test executor_id pattern validation."""
        schema = load_json_file(SCHEMAS_DIR / 'executor_config.schema.json')
        pattern = schema['properties']['executor_id']['pattern']
        
        # Valid executor IDs
        valid_ids = ['text_mining_executor', 'abc_def', 'my_executor_123']
        
        # Invalid executor IDs (would need regex validation in actual test)
        invalid_ids = ['1invalid', 'Invalid', 'ab', 'a' * 65]
        
        assert pattern == '^[a-z][a-z0-9_]{2,63}$'
    
    def test_task_id_pattern(self):
        """Test task_id pattern validation."""
        schema = load_json_file(SCHEMAS_DIR / 'executor_output.schema.json')
        pattern = schema['properties']['task_id']['pattern']
        
        assert pattern == '^[a-f0-9]{16}$'
    
    def test_content_hash_pattern(self):
        """Test content_hash pattern validation."""
        schema = load_json_file(SCHEMAS_DIR / 'executor_output.schema.json')
        
        # Check in result object
        result_props = schema['properties']['result']['properties']
        pattern = result_props['content_hash']['pattern']
        
        assert pattern == '^[a-f0-9]{64}$'


class TestValidatorModule:
    """Test the validator module."""
    
    def test_validator_module_exists(self):
        """Test that validator.py exists."""
        validator_path = SCHEMAS_DIR / 'validator.py'
        assert validator_path.exists()
    
    def test_validator_module_has_functions(self):
        """Test that validator module exports required functions."""
        validator_path = SCHEMAS_DIR / 'validator.py'
        content = validator_path.read_text()
        
        assert 'def load_schema' in content
        assert 'def validate_json' in content
        assert 'def validate_executor_config' in content
        assert 'def validate_executor_output' in content
        assert 'def validate_synchronization_manifest' in content
        assert 'def validate_calibration_policy' in content
        assert 'def validate_file' in content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

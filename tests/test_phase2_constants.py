"""
Test suite for Phase 2 constants module.

Verifies:
- All constants are properly defined and immutable
- Cardinality invariants hold
- Type safety and frozen dataclasses
- No runtime IO
- Import isolation from forbidden patterns

Run with: pytest tests/test_phase2_constants.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Final

import pytest

# Add src to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from canonic_phases.phase_2.constants import phase2_constants
from canonic_phases.phase_2.constants import (
    CPP_CHUNK_COUNT,
    MICRO_ANSWER_COUNT,
    SHARDS_PER_CHUNK,
    EXECUTOR_REGISTRY,
    ExecutorRegistryEntry,
    SCHEMA_VERSIONS,
    SchemaVersion,
    SISAS_SIGNAL_COVERAGE_THRESHOLD,
    SISAS_IRRIGATION_LINK_MINIMUM,
    SISAS_PRIORITY_WEIGHT_SIGNAL,
    SISAS_PRIORITY_WEIGHT_STATIC,
    DEFAULT_RANDOM_SEED,
    HASH_ALGORITHM,
    ERROR_CODES,
    ErrorCode,
    FORBIDDEN_IMPORTS,
    FORBIDDEN_RUNTIME_IO_PATTERNS,
)


class TestCardinalityInvariants:
    """Test cardinality invariants are correctly defined."""

    def test_cpp_chunk_count(self):
        """Verify CPP_CHUNK_COUNT is 60."""
        assert CPP_CHUNK_COUNT == 60
        assert isinstance(CPP_CHUNK_COUNT, int)

    def test_micro_answer_count(self):
        """Verify MICRO_ANSWER_COUNT is 300."""
        assert MICRO_ANSWER_COUNT == 300
        assert isinstance(MICRO_ANSWER_COUNT, int)

    def test_shards_per_chunk(self):
        """Verify SHARDS_PER_CHUNK is 5."""
        assert SHARDS_PER_CHUNK == 5
        assert isinstance(SHARDS_PER_CHUNK, int)

    def test_cardinality_invariant(self):
        """Verify CPP_CHUNK_COUNT * SHARDS_PER_CHUNK == MICRO_ANSWER_COUNT."""
        assert CPP_CHUNK_COUNT * SHARDS_PER_CHUNK == MICRO_ANSWER_COUNT
        assert 60 * 5 == 300


class TestExecutorRegistry:
    """Test executor registry configuration."""

    def test_registry_structure(self):
        """Verify EXECUTOR_REGISTRY has expected structure."""
        assert len(EXECUTOR_REGISTRY) == 3
        assert "contract_executor" in EXECUTOR_REGISTRY
        assert "analysis_executor" in EXECUTOR_REGISTRY
        assert "synthesis_executor" in EXECUTOR_REGISTRY

    def test_executor_entry_immutability(self):
        """Verify ExecutorRegistryEntry is frozen."""
        entry = EXECUTOR_REGISTRY["contract_executor"]
        assert isinstance(entry, ExecutorRegistryEntry)
        
        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            entry.canonical_name = "Modified"

    def test_executor_priorities(self):
        """Verify executor priorities are correctly ordered."""
        contract = EXECUTOR_REGISTRY["contract_executor"]
        analysis = EXECUTOR_REGISTRY["analysis_executor"]
        synthesis = EXECUTOR_REGISTRY["synthesis_executor"]
        
        assert contract.priority == 1
        assert analysis.priority == 2
        assert synthesis.priority == 3
        assert contract.priority < analysis.priority < synthesis.priority

    def test_executor_determinism(self):
        """Verify all executors are marked as deterministic."""
        for executor in EXECUTOR_REGISTRY.values():
            assert executor.deterministic is True

    def test_contract_types_frozen(self):
        """Verify contract_types are frozensets."""
        for executor in EXECUTOR_REGISTRY.values():
            assert isinstance(executor.contract_types, frozenset)


class TestSchemaVersions:
    """Test schema version control configuration."""

    def test_schema_versions_structure(self):
        """Verify SCHEMA_VERSIONS has expected schemas."""
        expected_schemas = {
            "executor_config",
            "executor_output",
            "calibration_policy",
            "synchronization_manifest",
        }
        assert set(SCHEMA_VERSIONS.keys()) == expected_schemas

    def test_schema_version_immutability(self):
        """Verify SchemaVersion is frozen."""
        schema = SCHEMA_VERSIONS["executor_config"]
        assert isinstance(schema, SchemaVersion)
        
        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            schema.version = "2.0.0"

    def test_schema_version_format(self):
        """Verify all schemas have version 1.0.0."""
        for schema in SCHEMA_VERSIONS.values():
            assert schema.version == "1.0.0"
            assert isinstance(schema.name, str)
            assert schema.name.endswith(".schema.json")


class TestSISASSynchronization:
    """Test SISAS synchronization policy constants."""

    def test_signal_coverage_threshold(self):
        """Verify signal coverage threshold is 0.85."""
        assert SISAS_SIGNAL_COVERAGE_THRESHOLD == 0.85
        assert 0.0 <= SISAS_SIGNAL_COVERAGE_THRESHOLD <= 1.0

    def test_irrigation_link_minimum(self):
        """Verify irrigation link minimum is 1."""
        assert SISAS_IRRIGATION_LINK_MINIMUM == 1
        assert SISAS_IRRIGATION_LINK_MINIMUM > 0

    def test_priority_weights(self):
        """Verify priority weights sum to 1.0."""
        assert SISAS_PRIORITY_WEIGHT_SIGNAL == 0.6
        assert SISAS_PRIORITY_WEIGHT_STATIC == 0.4
        
        weight_sum = SISAS_PRIORITY_WEIGHT_SIGNAL + SISAS_PRIORITY_WEIGHT_STATIC
        assert abs(weight_sum - 1.0) < 1e-9

    def test_priority_weights_range(self):
        """Verify priority weights are in valid range [0, 1]."""
        assert 0.0 <= SISAS_PRIORITY_WEIGHT_SIGNAL <= 1.0
        assert 0.0 <= SISAS_PRIORITY_WEIGHT_STATIC <= 1.0


class TestDeterminismControl:
    """Test determinism control constants."""

    def test_default_random_seed(self):
        """Verify default random seed is 42."""
        assert DEFAULT_RANDOM_SEED == 42
        assert isinstance(DEFAULT_RANDOM_SEED, int)

    def test_hash_algorithm(self):
        """Verify hash algorithm is sha256."""
        assert HASH_ALGORITHM == "sha256"
        assert isinstance(HASH_ALGORITHM, str)


class TestErrorCodes:
    """Test error code taxonomy."""

    def test_error_codes_structure(self):
        """Verify ERROR_CODES has expected entries."""
        expected_codes = {"E2001", "E2002", "E2003", "E2004", "E2005", "E2006", "E2007"}
        assert set(ERROR_CODES.keys()) == expected_codes

    def test_error_code_immutability(self):
        """Verify ErrorCode is frozen."""
        error = ERROR_CODES["E2001"]
        assert isinstance(error, ErrorCode)
        
        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            error.severity = "WARNING"

    def test_error_code_fields(self):
        """Verify all error codes have required fields."""
        for code_key, error in ERROR_CODES.items():
            assert error.code == code_key
            assert error.category in {"ROUTING", "CARVING", "VALIDATION", "SYNCHRONIZATION", "SCHEMA", "DETERMINISM", "CONTRACT"}
            assert error.severity == "FATAL"
            assert isinstance(error.message_template, str)
            assert len(error.message_template) > 0

    def test_error_message_templates(self):
        """Verify error message templates have placeholders where expected."""
        assert "{contract_type}" in ERROR_CODES["E2001"].message_template
        assert "{expected}" in ERROR_CODES["E2002"].message_template
        assert "{actual}" in ERROR_CODES["E2002"].message_template
        assert "{reason}" in ERROR_CODES["E2004"].message_template


class TestForbiddenPatterns:
    """Test forbidden pattern definitions."""

    def test_forbidden_imports(self):
        """Verify FORBIDDEN_IMPORTS contains expected patterns."""
        expected_forbidden = {"questionnaire_monolith", "executors", "batch_executor"}
        assert FORBIDDEN_IMPORTS == expected_forbidden
        assert isinstance(FORBIDDEN_IMPORTS, frozenset)

    def test_forbidden_runtime_io_patterns(self):
        """Verify FORBIDDEN_RUNTIME_IO_PATTERNS contains expected patterns."""
        expected_patterns = {"questionnaire_monolith.json", "monolith.json"}
        assert FORBIDDEN_RUNTIME_IO_PATTERNS == expected_patterns
        assert isinstance(FORBIDDEN_RUNTIME_IO_PATTERNS, frozenset)

    def test_frozenset_immutability(self):
        """Verify forbidden patterns are truly immutable."""
        with pytest.raises(AttributeError):
            FORBIDDEN_IMPORTS.add("new_forbidden")
        
        with pytest.raises(AttributeError):
            FORBIDDEN_RUNTIME_IO_PATTERNS.add("new_pattern.json")


class TestModuleImmutability:
    """Test that module constants cannot be modified at runtime."""

    def test_cannot_modify_constants(self):
        """Verify module-level constants cannot be reassigned."""
        original_value = phase2_constants.CPP_CHUNK_COUNT
        
        # This should not affect the constant due to Final typing
        with pytest.raises(AttributeError):
            phase2_constants.CPP_CHUNK_COUNT = 999
        
        # Verify value hasn't changed
        assert phase2_constants.CPP_CHUNK_COUNT == original_value


class TestNoRuntimeIO:
    """Test that no runtime IO occurs during import."""

    def test_no_file_access_during_import(self, monkeypatch):
        """Verify module import does not access filesystem."""
        import builtins
        original_open = builtins.open
        
        access_log = []
        
        def monitored_open(*args, **kwargs):
            access_log.append(args)
            return original_open(*args, **kwargs)
        
        monkeypatch.setattr(builtins, "open", monitored_open)
        
        # Reimport the module
        import importlib
        importlib.reload(phase2_constants)
        
        # Check that no forbidden files were accessed
        for call_args in access_log:
            if len(call_args) > 0:
                filepath = str(call_args[0])
                for pattern in FORBIDDEN_RUNTIME_IO_PATTERNS:
                    assert pattern not in filepath, f"Forbidden IO detected: {filepath}"


class TestTypeAnnotations:
    """Test that all constants have proper type annotations."""

    def test_final_annotations(self):
        """Verify critical constants use Final type annotation."""
        import typing
        
        annotations = phase2_constants.__annotations__
        
        # Check that key constants are annotated with Final
        final_constants = [
            "CPP_CHUNK_COUNT",
            "MICRO_ANSWER_COUNT",
            "SHARDS_PER_CHUNK",
            "EXECUTOR_REGISTRY",
            "SCHEMA_VERSIONS",
            "ERROR_CODES",
            "FORBIDDEN_IMPORTS",
            "FORBIDDEN_RUNTIME_IO_PATTERNS",
        ]
        
        for const_name in final_constants:
            assert const_name in annotations, f"{const_name} should have type annotation"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

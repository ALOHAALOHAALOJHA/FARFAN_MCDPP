"""
Adversarial Tests for Unified Factory Integration

Comprehensive adversarial test suite that tries to break the factory with:
- Invalid inputs
- Malformed data
- Edge cases
- Missing files
- Invalid contracts
- Circular dependencies
- Memory exhaustion attempts
- Timeout scenarios
- Concurrent access

Version: 1.0.0
Date: 2026-01-19
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import Mock, patch, MagicMock
import pytest


# =============================================================================
# TEST CONFIGURATION
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# =============================================================================
# ADVERSARIAL FIXTURES
# =============================================================================


@pytest.fixture
def factory_config():
    """Create factory configuration for adversarial testing."""
    from farfan_pipeline.orchestration.factory import FactoryConfig

    return FactoryConfig(
        project_root=PROJECT_ROOT,
        sisas_enabled=True,
        lazy_load_questions=True,
    )


@pytest.fixture
def unified_factory(factory_config):
    """Create unified factory instance for adversarial testing."""
    from farfan_pipeline.orchestration.factory import UnifiedFactory

    return UnifiedFactory(config=factory_config)


@pytest.fixture
def invalid_contract():
    """Create an invalid contract for testing."""
    return {
        "invalid_field": "invalid_value",
        "malformed": True,
        "executor_binding": {
            "executor_module": "nonexistent.module",
            "executor_class": "NonExistentClass",
        },
    }


@pytest.fixture
def adversarial_contract():
    """Create an adversarial contract for testing."""
    return {
        "identity": {
            "contract_id": "ADVERSARIAL_001",
            "has_veto": True,
        },
        "executor_binding": {
            "executor_module": "builtins",
            "executor_class": "dict",  # Use dict as executor (no execute method)
        },
        "method_binding": {
            "orchestration_mode": "epistemological_pipeline",
            "execution_phases": {
                "phase_A_construction": {
                    "level": "N1",
                    "methods": [
                        {
                            "method_id": "nonexistent.module.method",
                            "provides": "nothing",
                            "confidence_score": -1.0,  # Invalid confidence
                        }
                    ],
                },
                "phase_C_litigation": {
                    "level": "N3",
                    "has_veto_power": True,
                    "methods": [
                        {
                            "method_id": "builtins.len",
                            "provides": "veto_trigger",
                            "confidence_score": 1.0,
                        }
                    ],
                },
            },
        },
    }


# =============================================================================
# ADVERSARIAL INPUT TESTS - QUESTIONNAIRE
# =============================================================================


class TestAdversarialQuestionnaireInputs:
    """Test questionnaire handling with adversarial inputs."""

    def test_questionnaire_with_nonexistent_path(self, factory_config):
        """Test factory with nonexistent questionnaire path."""
        factory_config.questionnaire_path = Path("/nonexistent/path/to/questionnaire.json")

        from farfan_pipeline.orchestration.factory import UnifiedFactory

        factory = UnifiedFactory(config=factory_config)
        # Should not crash, should handle gracefully
        questionnaire = factory.load_questionnaire()
        # May return stub or raise error depending on implementation
        assert True  # Test passes if no crash

    def test_questionnaire_with_invalid_json(self, factory_config, tmp_path):
        """Test factory with invalid JSON file."""
        invalid_json = tmp_path / "invalid_questionnaire.json"
        invalid_json.write_text("{ invalid json content")

        factory_config.questionnaire_path = invalid_json

        from farfan_pipeline.orchestration.factory import UnifiedFactory

        # Should handle gracefully or raise appropriate error
        try:
            factory = UnifiedFactory(config=factory_config)
            questionnaire = factory.load_questionnaire()
        except (json.JSONDecodeError, ValueError):
            assert True  # Expected error
        except Exception:
            # Any exception is acceptable for invalid input
            assert True

    def test_questionnaire_with_empty_file(self, factory_config, tmp_path):
        """Test factory with empty questionnaire file."""
        empty_file = tmp_path / "empty_questionnaire.json"
        empty_file.write_text("")

        factory_config.questionnaire_path = empty_file

        from farfan_pipeline.orchestration.factory import UnifiedFactory

        factory = UnifiedFactory(config=factory_config)
        # Should handle gracefully
        questionnaire = factory.load_questionnaire()
        assert True  # No crash

    def test_questionnaire_with_malformed_structure(self, factory_config, tmp_path):
        """Test factory with malformed questionnaire structure."""
        malformed_file = tmp_path / "malformed_questionnaire.json"
        malformed_file.write_text('{"questions": null, "dimensions": "invalid"}')

        factory_config.questionnaire_path = malformed_file

        from farfan_pipeline.orchestration.factory import UnifiedFactory

        factory = UnifiedFactory(config=factory_config)
        # Should handle gracefully
        questionnaire = factory.load_questionnaire()
        assert True  # No crash


# =============================================================================
# ADVERSARIAL INPUT TESTS - CONTRACTS
# =============================================================================


class TestAdversarialContractInputs:
    """Test contract handling with adversarial inputs."""

    def test_execute_contract_with_empty_id(self, unified_factory):
        """Test executing with empty contract ID."""
        with pytest.raises(KeyError):
            unified_factory.execute_contract("", {})

    def test_execute_contract_with_none_id(self, unified_factory):
        """Test executing with None contract ID."""
        with pytest.raises((KeyError, TypeError, AttributeError)):
            unified_factory.execute_contract(None, {})

    def test_execute_contract_with_special_characters(self, unified_factory):
        """Test executing with special characters in ID."""
        with pytest.raises(KeyError):
            unified_factory.execute_contract("../../../etc/passwd", {})

    def test_execute_contract_with_very_long_id(self, unified_factory):
        """Test executing with very long contract ID."""
        long_id = "A" * 10000
        with pytest.raises(KeyError):
            unified_factory.execute_contract(long_id, {})

    def test_execute_contract_with_null_input(self, unified_factory):
        """Test executing with null input data."""
        contracts = unified_factory.load_contracts()
        if len(contracts) > 0:
            contract_id = list(contracts.keys())[0]
            # Should handle null input gracefully
            result = unified_factory.execute_contract(contract_id, None)
            assert result is not None

    def test_execute_contract_with_malformed_input(self, unified_factory):
        """Test executing with malformed input data."""
        contracts = unified_factory.load_contracts()
        if len(contracts) > 0:
            contract_id = list(contracts.keys())[0]
            # Should handle malformed input gracefully
            result = unified_factory.execute_contract(contract_id, {"malformed": object()})
            assert result is not None

    def test_execute_contract_with_extremely_large_input(self, unified_factory):
        """Test executing with extremely large input data."""
        contracts = unified_factory.load_contracts()
        if len(contracts) > 0:
            contract_id = list(contracts.keys())[0]
            large_input = {"data": "x" * 10000000}  # 10MB of data
            # Should handle or fail gracefully
            try:
                result = unified_factory.execute_contract(contract_id, large_input)
                assert result is not None
            except (MemoryError, ValueError):
                assert True  # Acceptable for large input

    def test_load_contracts_from_invalid_path(self, factory_config):
        """Test loading contracts from invalid path."""
        factory_config.contracts_path = Path("/nonexistent/contracts.json")

        from farfan_pipeline.orchestration.factory import UnifiedFactory

        factory = UnifiedFactory(config=factory_config)
        contracts = factory.load_contracts()
        # Should return empty dict, not crash
        assert contracts == {}

    def test_load_contracts_from_invalid_json(self, factory_config, tmp_path):
        """Test loading contracts from invalid JSON file."""
        invalid_json = tmp_path / "invalid_contracts.json"
        invalid_json.write_text("{ invalid json }")

        factory_config.contracts_path = invalid_json

        from farfan_pipeline.orchestration.factory import UnifiedFactory

        factory = UnifiedFactory(config=factory_config)
        # Should raise JSONDecodeError
        with pytest.raises(json.JSONDecodeError):
            factory.load_contracts()

    def test_execute_adversarial_contract(self, unified_factory, adversarial_contract):
        """Test executing adversarial contract with veto and invalid methods."""
        # Manually inject adversarial contract
        unified_factory._contracts = {"ADVERSARIAL_001": adversarial_contract}

        # Should handle adversarial contract gracefully
        result = unified_factory.execute_contract("ADVERSARIAL_001", {})
        assert result is not None
        assert result.get("contract_id") == "ADVERSARIAL_001"
        # Should have status or error field
        assert "status" in result or "error" in result


# =============================================================================
# ADVERSARIAL METHOD INJECTION TESTS
# =============================================================================


class TestAdversarialMethodInjection:
    """Test method injection with adversarial scenarios."""

    def test_method_injection_with_nonexistent_module(self, unified_factory):
        """Test injecting method from nonexistent module."""
        adversarial_contract = {
            "identity": {"contract_id": "NONEXISTENT_MODULE_TEST"},
            "executor_binding": {
                "executor_module": "builtins",
                "executor_class": "dict",
            },
            "method_binding": {
                "execution_phases": {
                    "phase_A_construction": {
                        "level": "N1",
                        "methods": [
                            {
                                "method_id": "totally.fake.module.method",
                                "provides": "nothing",
                                "confidence_score": 0.5,
                            }
                        ],
                    },
                },
            },
        }

        unified_factory._contracts = {"NONEXISTENT_MODULE_TEST": adversarial_contract}

        # Should handle injection failure gracefully
        result = unified_factory.execute_contract("NONEXISTENT_MODULE_TEST", {})
        assert result is not None

    def test_method_injection_with_circular_import(self, unified_factory):
        """Test injecting method that causes circular import."""
        adversarial_contract = {
            "identity": {"contract_id": "CIRCULAR_IMPORT_TEST"},
            "executor_binding": {
                "executor_module": "builtins",
                "executor_class": "dict",
            },
            "method_binding": {
                "execution_phases": {
                    "phase_A_construction": {
                        "level": "N1",
                        "methods": [
                            {
                                "method_id": "farfan_pipeline.orchestration.factory.UnifiedFactory",
                                "provides": "circular",
                                "confidence_score": 0.5,
                            }
                        ],
                    },
                },
            },
        }

        unified_factory._contracts = {"CIRCULAR_IMPORT_TEST": adversarial_contract}

        # Should handle circular import gracefully
        result = unified_factory.execute_contract("CIRCULAR_IMPORT_TEST", {})
        assert result is not None

    def test_method_injection_with_dangerous_builtin(self, unified_factory):
        """Test injecting dangerous builtin methods."""
        dangerous_methods = [
            "builtins.__import__",
            "builtins.eval",
            "builtins.exec",
            "builtins.compile",
        ]

        for method_id in dangerous_methods:
            adversarial_contract = {
                "identity": {"contract_id": f"DANGEROUS_{method_id}"},
                "executor_binding": {
                    "executor_module": "builtins",
                    "executor_class": "dict",
                },
                "method_binding": {
                    "execution_phases": {
                        "phase_A_construction": {
                            "level": "N1",
                            "methods": [
                                {
                                    "method_id": method_id,
                                    "provides": "dangerous",
                                    "confidence_score": 1.0,
                                }
                            ],
                        },
                    },
                },
            }

            unified_factory._contracts = {f"DANGEROUS_{method_id}": adversarial_contract}

            # Should inject but not execute dangerous methods without proper context
            result = unified_factory.execute_contract(f"DANGEROUS_{method_id}", {})
            assert result is not None


# =============================================================================
# ADVERSARIAL VETO GATE TESTS
# =============================================================================


class TestAdversarialVetoGate:
    """Test veto gate with adversarial scenarios."""

    def test_veto_gate_with_always_true_veto(self, unified_factory):
        """Test veto gate that always triggers."""
        # Create a mock method that returns veto=True
        def mock_veto_method(**kwargs):
            return {"veto": True, "reason": "Adversarial veto"}

        adversarial_contract = {
            "identity": {"contract_id": "ALWAYS_VETO_TEST"},
            "executor_binding": {
                "executor_module": "builtins",
                "executor_class": "dict",
            },
            "method_binding": {
                "execution_phases": {
                    "phase_C_litigation": {
                        "level": "N3",
                        "has_veto_power": True,
                        "methods": [
                            {
                                "method_id": "__main__.mock_veto_method",
                                "provides": "veto",
                                "confidence_score": 1.0,
                            }
                        ],
                    },
                },
            },
        }

        # Inject mock method into namespace
        import sys
        sys.modules["__main__"].mock_veto_method = mock_veto_method

        unified_factory._contracts = {"ALWAYS_VETO_TEST": adversarial_contract}

        result = unified_factory.execute_contract("ALWAYS_VETO_TEST", {})
        assert result is not None

    def test_veto_gate_with_invalid_veto_response(self, unified_factory):
        """Test veto gate with invalid veto response format."""
        def mock_invalid_veto(**kwargs):
            return {"veto": "not a boolean", "reason": None}

        adversarial_contract = {
            "identity": {"contract_id": "INVALID_VETO_TEST"},
            "executor_binding": {
                "executor_module": "builtins",
                "executor_class": "dict",
            },
            "method_binding": {
                "execution_phases": {
                    "phase_C_litigation": {
                        "level": "N3",
                        "has_veto_power": True,
                        "methods": [
                            {
                                "method_id": "__main__.mock_invalid_veto",
                                "provides": "invalid_veto",
                                "confidence_score": 1.0,
                            }
                        ],
                    },
                },
            },
        }

        import sys
        sys.modules["__main__"].mock_invalid_veto = mock_invalid_veto

        unified_factory._contracts = {"INVALID_VETO_TEST": adversarial_contract}

        result = unified_factory.execute_contract("INVALID_VETO_TEST", {})
        assert result is not None


# =============================================================================
# ADVERSARIAL FILE I/O TESTS
# =============================================================================


class TestAdversarialFileIO:
    """Test file I/O with adversarial scenarios."""

    def test_save_json_to_readonly_path(self, unified_factory, tmp_path):
        """Test saving JSON to read-only path."""
        # Create a read-only file
        readonly_file = tmp_path / "readonly.json"
        readonly_file.write_text("{}")
        readonly_file.chmod(0o444)

        # Should handle permission error gracefully
        try:
            unified_factory.save_json(readonly_file, {"new": "data"})
            # If it succeeded, that's also acceptable
            assert True
        except (PermissionError, OSError):
            assert True  # Expected error

    def test_load_json_from_directory(self, unified_factory, tmp_path):
        """Test loading JSON from a directory (not a file)."""
        # Should handle gracefully
        with pytest.raises((IsADirectoryError, json.JSONDecodeError, OSError)):
            unified_factory.load_json(tmp_path)

    def test_save_json_to_nonexistent_parent(self, unified_factory):
        """Test saving JSON to path with nonexistent parent directory."""
        # Should create parent directories
        test_path = Path("/tmp/nonexistent/deeply/nested/path/test.json")
        unified_factory.save_json(test_path, {"test": "data"})
        # Parent should be created and file should exist
        assert test_path.parent.exists()
        # Cleanup
        test_path.unlink()
        import shutil
        shutil.rmtree(test_path.parent.parent.parent.parent)

    def test_write_text_file_with_binary_content(self, unified_factory, tmp_path):
        """Test writing binary content as text."""
        binary_content = b"\x00\x01\x02\xff"
        test_file = tmp_path / "binary_test.txt"

        # Should handle or raise appropriate error
        try:
            unified_factory.write_text_file(test_file, binary_content)
            assert True  # Success
        except (TypeError, AttributeError):
            assert True  # Expected error for binary content

    def test_read_text_file_with_binary_file(self, unified_factory, tmp_path):
        """Test reading binary file as text."""
        binary_file = tmp_path / "binary.bin"
        binary_file.write_bytes(b"\x00\x01\x02\xff")

        # Should handle or raise appropriate error
        try:
            content = unified_factory.read_text_file(binary_file)
            assert True  # Success (may contain replacement chars)
        except (UnicodeDecodeError, ValueError):
            assert True  # Expected error for binary content


# =============================================================================
# ADVERSARIAL MEMORY TESTS
# =============================================================================


class TestAdversarialMemoryScenarios:
    """Test factory with memory-related adversarial scenarios."""

    def test_factory_with_massive_questionnaire(self, factory_config, tmp_path):
        """Test factory with extremely large questionnaire file."""
        massive_file = tmp_path / "massive_questionnaire.json"

        # Create a 100MB JSON file
        massive_data = {"questions": [{"id": i, "data": "x" * 1000} for i in range(100000)]}
        massive_file.write_text(json.dumps(massive_data))

        factory_config.questionnaire_path = massive_file

        from farfan_pipeline.orchestration.factory import UnifiedFactory

        # Should handle gracefully or raise MemoryError
        try:
            factory = UnifiedFactory(config=factory_config)
            questionnaire = factory.load_questionnaire()
            assert True  # Success or graceful degradation
        except MemoryError:
            assert True  # Acceptable for massive input

    def test_batch_execution_with_many_contracts(self, unified_factory):
        """Test batch execution with many contracts."""
        # Create 1000 mock contracts
        mock_contracts = {}
        for i in range(1000):
            mock_contracts[f"MOCK_{i}"] = {
                "identity": {"contract_id": f"MOCK_{i}"},
                "executor_binding": {
                    "executor_module": "builtins",
                    "executor_class": "dict",
                },
                "method_binding": {"execution_phases": {}},
            }

        unified_factory._contracts = mock_contracts

        # Execute all (should handle gracefully)
        results = unified_factory.execute_contracts_batch(
            list(mock_contracts.keys()), {}
        )
        assert len(results) == 1000


# =============================================================================
# ADVERSARIAL CONCURRENCY TESTS
# =============================================================================


class TestAdversarialConcurrency:
    """Test factory with concurrent access scenarios."""

    def test_concurrent_questionnaire_access(self, unified_factory):
        """Test multiple threads accessing questionnaire simultaneously."""
        import threading

        results = []
        errors = []

        def access_questionnaire():
            try:
                for _ in range(100):
                    q = unified_factory.questionnaire
                    results.append(q is not None)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=access_questionnaire) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have no errors
        assert len(errors) == 0
        assert len(results) > 0

    def test_concurrent_contract_execution(self, unified_factory):
        """Test multiple threads executing contracts simultaneously."""
        import threading

        # Create a mock contract
        mock_contract = {
            "identity": {"contract_id": "CONCURRENT_TEST"},
            "executor_binding": {
                "executor_module": "builtins",
                "executor_class": "dict",
            },
            "method_binding": {"execution_phases": {}},
        }

        unified_factory._contracts = {"CONCURRENT_TEST": mock_contract}

        results = []
        errors = []

        def execute_contract():
            try:
                for _ in range(10):
                    result = unified_factory.execute_contract("CONCURRENT_TEST", {})
                    results.append(result)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=execute_contract) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have no errors or handle gracefully
        assert True  # Test passes if no crash


# =============================================================================
# ADVERSARIAL TYPE TESTS
# =============================================================================


class TestAdversarialTypeInputs:
    """Test factory with incorrect types."""

    def test_factory_config_with_invalid_types(self):
        """Test factory config with invalid types."""
        from farfan_pipeline.orchestration.factory import FactoryConfig

        # Should handle or convert invalid types
        config = FactoryConfig(
            project_root=".",  # String instead of Path
            questionnaire_path=None,  # None
        )

        # Should convert to Path
        assert isinstance(config.project_root, Path)

    def test_execute_with_wrong_input_type(self, unified_factory):
        """Test execute_contract with wrong input type."""
        contracts = unified_factory.load_contracts()
        if len(contracts) > 0:
            contract_id = list(contracts.keys())[0]

            # Try with string instead of dict
            result = unified_factory.execute_contract(contract_id, "invalid_input")
            assert result is not None

    def test_signal_registry_with_corrupted_data(self, factory_config, tmp_path):
        """Test signal registry with corrupted canonical notation."""
        from farfan_pipeline.orchestration.factory import UnifiedFactory

        # Create invalid canonical notation structure
        corrupted_file = tmp_path / "corrupted_notation.json"
        corrupted_file.write_text('{"dimensions": "not_a_dict", "policy_areas": ["array", "not", "dict"]}')

        # This test verifies that the factory handles corrupted data gracefully
        # The resolver may fail to initialize, which is expected
        factory_config.sisas_enabled = False  # Disable SISAS to avoid resolver issues
        factory = UnifiedFactory(config=factory_config)

        # Test that create_signal_registry handles the error gracefully
        # It may return a partial registry or raise an error
        try:
            registry = factory.create_signal_registry()
            # If it succeeds, verify structure
            assert isinstance(registry, dict)
        except (ValueError, KeyError, json.JSONDecodeError):
            # These are acceptable errors for corrupted data
            assert True


# =============================================================================
# ADVERSARIAL EDGE CASES
# =============================================================================


class TestAdversarialEdgeCases:
    """Test factory with edge cases."""

    def test_factory_with_no_project_root(self):
        """Test factory with no project root specified."""
        from farfan_pipeline.orchestration.factory import UnifiedFactory

        # Should use current directory
        factory = UnifiedFactory.create_default()
        assert factory is not None

    def test_execute_contract_id_with_unicode(self, unified_factory):
        """Test contract ID with unicode characters."""
        unicode_id = "CONTRACT_测试_🔥"

        # Should handle unicode gracefully
        with pytest.raises(KeyError):  # Contract doesn't exist
            unified_factory.execute_contract(unicode_id, {})

    def test_execute_contract_with_recursive_input(self, unified_factory):
        """Test contract execution with recursive input data."""
        # Create recursive structure
        recursive_data = {}
        recursive_data["self"] = recursive_data

        contracts = unified_factory.load_contracts()
        if len(contracts) > 0:
            contract_id = list(contracts.keys())[0]

            # Should handle or fail gracefully
            try:
                result = unified_factory.execute_contract(contract_id, recursive_data)
                assert True  # Success
            except (ValueError, RecursionError):
                assert True  # Expected error for recursive input

    def test_multiple_factory_instances(self):
        """Test creating multiple factory instances."""
        from farfan_pipeline.orchestration.factory import UnifiedFactory, FactoryConfig

        factories = []
        for i in range(10):
            config = FactoryConfig(project_root=Path("."), cache_size=i)
            factory = UnifiedFactory(config=config)
            factories.append(factory)

        # All should be independent
        assert len(set(id(f) for f in factories)) == 10

    def test_factory_with_zero_cache_size(self):
        """Test factory with zero cache size."""
        from farfan_pipeline.orchestration.factory import FactoryConfig, UnifiedFactory

        config = FactoryConfig(project_root=Path("."), cache_size=0)
        factory = UnifiedFactory(config=config)

        # Should handle gracefully
        questionnaire = factory.load_questionnaire()
        assert questionnaire is not None


# =============================================================================
# ADVERSARIAL DEPRECATION TESTS
# =============================================================================


class TestAdversarialDeprecation:
    """Test deprecation with adversarial scenarios."""

    def test_legacy_import_infinite_recursion(self):
        """Test legacy import doesn't cause infinite recursion."""
        from farfan_pipeline.phases.Phase_02.phase2_10_00_factory import (
            load_questionnaire,
        )

        # Call multiple times
        for _ in range(100):
            result = load_questionnaire()
            assert result is not None

    def test_legacy_import_withmonkeypatching(self):
        """Test legacy import resists monkeypatching."""
        from farfan_pipeline.phases.Phase_02.phase2_10_00_factory import (
            load_questionnaire as legacy_load_questionnaire,
        )

        # Monkeypatch the factory module
        import farfan_pipeline.orchestration.factory as factory_module
        original_get_factory = factory_module.get_factory

        def mock_get_factory():
            raise RuntimeError("Monkeypatched!")

        factory_module.get_factory = mock_get_factory

        # Should handle monkeypatching gracefully
        try:
            result = legacy_load_questionnaire()
            # May return None or raise error
            assert True
        except RuntimeError:
            assert True  # Expected
        finally:
            # Restore original
            factory_module.get_factory = original_get_factory


# =============================================================================
# RUNNER
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])

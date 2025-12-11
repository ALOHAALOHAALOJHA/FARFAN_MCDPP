"""Tests for IrrigationSynchronizer JOIN table integration.

Tests the integration of canonical JOIN table architecture into IrrigationSynchronizer,
including contract-driven pattern irrigation and verification manifest generation.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest


def test_irrigation_synchronizer_imports():
    """Test that IrrigationSynchronizer can import JOIN table components."""
    from canonic_phases.Phase_two.irrigation_synchronizer import (
        IrrigationSynchronizer,
        SYNCHRONIZER_AVAILABLE,
    )
    
    # Should have the flag
    assert isinstance(SYNCHRONIZER_AVAILABLE, bool)
    
    # Constructor should accept new parameters
    import inspect
    sig = inspect.signature(IrrigationSynchronizer.__init__)
    params = list(sig.parameters.keys())
    
    assert "contracts" in params
    assert "enable_join_table" in params


def test_irrigation_synchronizer_with_join_table_disabled():
    """Test IrrigationSynchronizer with JOIN table disabled (default)."""
    from canonic_phases.Phase_two.irrigation_synchronizer import IrrigationSynchronizer
    
    # Create minimal questionnaire
    questionnaire = {
        "blocks": {
            "D1_Q01": {
                "question": "Test question",
                "question_global": 1,
                "policy_area_id": "PA01",
                "dimension_id": "DIM01",
                "patterns": [],
                "expected_elements": [],
            }
        }
    }
    
    # Create synchronizer without JOIN table
    synchronizer = IrrigationSynchronizer(
        questionnaire=questionnaire,
        document_chunks=[{"chunk_id": "PA01-DIM01", "text": "test"}],
        enable_join_table=False,
    )
    
    assert synchronizer.enable_join_table is False
    assert synchronizer.join_table is None
    assert synchronizer.executor_contracts is None


def test_irrigation_synchronizer_with_join_table_enabled_no_contracts():
    """Test IrrigationSynchronizer with JOIN table enabled but no contracts."""
    from canonic_phases.Phase_two.irrigation_synchronizer import IrrigationSynchronizer
    
    # Create minimal questionnaire
    questionnaire = {
        "blocks": {
            "D1_Q01": {
                "question": "Test question",
                "question_global": 1,
                "policy_area_id": "PA01",
                "dimension_id": "DIM01",
                "patterns": [],
                "expected_elements": [],
            }
        }
    }
    
    # Create synchronizer with JOIN table enabled but no contracts
    synchronizer = IrrigationSynchronizer(
        questionnaire=questionnaire,
        document_chunks=[{"chunk_id": "PA01-DIM01", "text": "test"}],
        enable_join_table=True,
        contracts=None,
    )
    
    # Should be enabled but no JOIN table built without contracts
    # Note: enable_join_table depends on SYNCHRONIZER_AVAILABLE
    assert synchronizer.executor_contracts is None


def test_find_contract_for_question():
    """Test _find_contract_for_question method."""
    from canonic_phases.Phase_two.irrigation_synchronizer import IrrigationSynchronizer
    
    questionnaire = {
        "blocks": {
            "D1_Q01": {
                "question": "Test",
                "question_global": 1,
                "policy_area_id": "PA01",
                "dimension_id": "DIM01",
            }
        }
    }
    
    contracts = [
        {
            "identity": {
                "question_id": "Q001",
                "policy_area_id": "PA01",
                "dimension_id": "DIM01",
            },
            "question_context": {
                "patterns": [{"id": "PAT-001", "pattern": "test"}]
            },
        }
    ]
    
    synchronizer = IrrigationSynchronizer(
        questionnaire=questionnaire,
        document_chunks=[{"chunk_id": "PA01-DIM01", "text": "test"}],
        contracts=contracts,
        enable_join_table=False,
    )
    
    question = {
        "question_id": "D1_Q01",
        "question_global": 1,
        "policy_area_id": "PA01",
        "dimension_id": "DIM01",
    }
    
    contract = synchronizer._find_contract_for_question(question)
    
    assert contract is not None
    assert contract["identity"]["question_id"] == "Q001"


def test_filter_patterns_from_contract():
    """Test _filter_patterns_from_contract method."""
    from canonic_phases.Phase_two.irrigation_synchronizer import IrrigationSynchronizer
    
    questionnaire = {"blocks": {}}
    
    synchronizer = IrrigationSynchronizer(
        questionnaire=questionnaire,
        document_chunks=[{"chunk_id": "PA01-DIM01", "text": "test"}],
    )
    
    contract = {
        "identity": {"question_id": "Q001"},
        "question_context": {
            "patterns": [
                {"id": "PAT-001", "pattern": "test1"},
                {"id": "PAT-002", "pattern": "test2"},
            ]
        },
    }
    
    patterns = synchronizer._filter_patterns_from_contract(contract)
    
    assert isinstance(patterns, tuple)
    assert len(patterns) == 2
    assert patterns[0]["id"] == "PAT-001"
    assert patterns[1]["id"] == "PAT-002"


def test_filter_patterns_from_contract_empty():
    """Test _filter_patterns_from_contract with empty patterns."""
    from canonic_phases.Phase_two.irrigation_synchronizer import IrrigationSynchronizer
    
    questionnaire = {"blocks": {}}
    
    synchronizer = IrrigationSynchronizer(
        questionnaire=questionnaire,
        document_chunks=[{"chunk_id": "PA01-DIM01", "text": "test"}],
    )
    
    contract = {
        "identity": {"question_id": "Q001"},
        "question_context": {"patterns": []},
    }
    
    patterns = synchronizer._filter_patterns_from_contract(contract)
    
    assert isinstance(patterns, tuple)
    assert len(patterns) == 0


def test_build_join_table_if_enabled_disabled():
    """Test _build_join_table_if_enabled when disabled."""
    from canonic_phases.Phase_two.irrigation_synchronizer import IrrigationSynchronizer
    
    questionnaire = {"blocks": {}}
    
    synchronizer = IrrigationSynchronizer(
        questionnaire=questionnaire,
        document_chunks=[{"chunk_id": "PA01-DIM01", "text": "test"}],
        enable_join_table=False,
    )
    
    result = synchronizer._build_join_table_if_enabled([])
    
    assert result is None


def test_join_table_integration_feature_flag():
    """Test that JOIN table integration respects feature flag."""
    from canonic_phases.Phase_two.irrigation_synchronizer import (
        IrrigationSynchronizer,
        SYNCHRONIZER_AVAILABLE,
    )
    
    questionnaire = {"blocks": {}}
    
    # With flag disabled
    sync_disabled = IrrigationSynchronizer(
        questionnaire=questionnaire,
        document_chunks=[{"chunk_id": "PA01-DIM01"}],
        enable_join_table=False,
    )
    
    assert sync_disabled.enable_join_table is False
    
    # With flag enabled (depends on SYNCHRONIZER_AVAILABLE)
    sync_enabled = IrrigationSynchronizer(
        questionnaire=questionnaire,
        document_chunks=[{"chunk_id": "PA01-DIM01"}],
        enable_join_table=True,
    )
    
    # Should be enabled only if SYNCHRONIZER_AVAILABLE is True
    assert sync_enabled.enable_join_table == SYNCHRONIZER_AVAILABLE


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

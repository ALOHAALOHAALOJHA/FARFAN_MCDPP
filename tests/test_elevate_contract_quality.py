"""
Tests for scripts/elevate_contract_quality_95.py

Tests the contract quality elevation script that uses 30-position equivalence 
groups to elevate executor contracts to CQVR ≥95.

Run with: pytest tests/test_elevate_contract_quality.py -v
"""

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import functions to test
from scripts.elevate_contract_quality_95 import (
    NUM_GROUPS,
    NUM_POLICY_AREAS,
    ContractScore,
    GroupSelection,
    _apply_expected_elements,
    _canonical_expected_elements,
    _choose_better_expected_element,
    _compute_contract_hash,
    _compute_monolith_source_hash,
    _generate_validation_rules,
    _group_question_ids,
    _normalize_output_schema_consts,
    _normalize_patterns_policy_area,
    _normalize_question_context_labels,
    _normalize_template_text,
    _normalize_traceability_source_hash,
    _normalize_validation_rules,
    _safe_get,
    _summarize_scores,
    _utc_now_iso,
)


class TestDataClasses:
    """Test dataclass structures."""

    def test_contract_score_creation(self):
        """Test ContractScore dataclass."""
        score = ContractScore(
            contract_id="Q001",
            total_score=95.5,
            decision="PASS"
        )
        assert score.contract_id == "Q001"
        assert score.total_score == 95.5
        assert score.decision == "PASS"

    def test_group_selection_creation(self):
        """Test GroupSelection dataclass."""
        selection = GroupSelection(
            group_id=0,
            canonical_contract_id="Q001",
            canonical_base_slot="D1-Q1"
        )
        assert selection.group_id == 0
        assert selection.canonical_contract_id == "Q001"
        assert selection.canonical_base_slot == "D1-Q1"


class TestUtilityFunctions:
    """Test utility functions."""

    def test_utc_now_iso_format(self):
        """Test UTC timestamp generation."""
        timestamp = _utc_now_iso()
        assert isinstance(timestamp, str)
        assert "T" in timestamp
        assert "Z" in timestamp or "+" in timestamp

    def test_safe_get_nested_dict(self):
        """Test safe nested dictionary access."""
        data = {
            "level1": {
                "level2": {
                    "level3": "value"
                }
            }
        }
        assert _safe_get(data, "level1.level2.level3") == "value"
        assert _safe_get(data, "level1.level2") == {"level3": "value"}
        assert _safe_get(data, "nonexistent.path") is None
        assert _safe_get(data, "level1.nonexistent") is None

    def test_safe_get_with_non_dict(self):
        """Test safe_get with non-dict values in path."""
        data = {"key": "string_value"}
        assert _safe_get(data, "key.nested") is None

    def test_group_question_ids(self):
        """Test question ID generation for groups."""
        # Group 0: Q001, Q031, Q061, Q091, Q121, Q151, Q181, Q211, Q241, Q271
        group_0 = _group_question_ids(0)
        assert len(group_0) == NUM_POLICY_AREAS
        assert group_0[0] == "Q001"
        assert group_0[1] == "Q031"
        assert group_0[-1] == "Q271"

        # Group 29: Q030, Q060, Q090, Q120, Q150, Q180, Q210, Q240, Q270, Q300
        group_29 = _group_question_ids(29)
        assert len(group_29) == NUM_POLICY_AREAS
        assert group_29[0] == "Q030"
        assert group_29[-1] == "Q300"

    def test_compute_monolith_source_hash(self):
        """Test monolith source hash computation."""
        monolith = {"questions": [{"id": "Q001"}], "version": "1.0"}
        hash1 = _compute_monolith_source_hash(monolith)
        assert isinstance(hash1, str)
        assert len(hash1) == 64  # SHA256 hex digest

        # Same input should produce same hash
        hash2 = _compute_monolith_source_hash(monolith)
        assert hash1 == hash2

        # Different input should produce different hash
        monolith_different = {"questions": [{"id": "Q002"}], "version": "1.0"}
        hash3 = _compute_monolith_source_hash(monolith_different)
        assert hash1 != hash3

    def test_compute_contract_hash(self):
        """Test contract hash computation."""
        contract = {
            "identity": {
                "question_id": "Q001",
                "contract_hash": "old_hash"
            },
            "question_context": {"text": "test"}
        }
        hash1 = _compute_contract_hash(contract)
        assert isinstance(hash1, str)
        assert len(hash1) == 64

        # Hash computation should ignore existing contract_hash
        contract_copy = json.loads(json.dumps(contract))
        contract_copy["identity"]["contract_hash"] = "different_old_hash"
        hash2 = _compute_contract_hash(contract_copy)
        assert hash1 == hash2


class TestExpectedElementsLogic:
    """Test expected elements normalization logic."""

    def test_choose_better_expected_element_required_wins(self):
        """Test that required elements win over optional."""
        elem_required = {"type": "test", "required": True, "minimum": 1}
        elem_optional = {"type": "test", "required": False, "minimum": 2}
        
        result = _choose_better_expected_element(elem_required, elem_optional)
        assert result["required"] is True

    def test_choose_better_expected_element_higher_minimum(self):
        """Test that higher minimum wins when both required."""
        elem_low = {"type": "test", "required": True, "minimum": 1}
        elem_high = {"type": "test", "required": True, "minimum": 3}
        
        result = _choose_better_expected_element(elem_low, elem_high)
        assert result["minimum"] == 3

    def test_canonical_expected_elements_deduplication(self):
        """Test canonical expected elements selection."""
        contracts = [
            {
                "question_context": {
                    "expected_elements": [
                        {"type": "type_a", "required": True, "minimum": 2},
                        {"type": "type_b", "required": False, "minimum": 1}
                    ]
                }
            },
            {
                "question_context": {
                    "expected_elements": [
                        {"type": "type_a", "required": True, "minimum": 3},
                        {"type": "type_c", "required": True, "minimum": 1}
                    ]
                }
            }
        ]
        
        result = _canonical_expected_elements(contracts)
        
        # Should have 3 unique types
        types = [e["type"] for e in result]
        assert len(types) == 3
        assert "type_a" in types
        assert "type_b" in types
        assert "type_c" in types
        
        # type_a should have minimum=3 (higher value wins)
        type_a_elem = next(e for e in result if e["type"] == "type_a")
        assert type_a_elem["minimum"] == 3

    def test_apply_expected_elements_updates_contract(self):
        """Test applying expected elements to contract."""
        contract = {"question_context": {"expected_elements": []}}
        new_elements = [{"type": "test", "required": True, "minimum": 1}]
        
        updated = _apply_expected_elements(contract, new_elements)
        assert updated is True
        assert contract["question_context"]["expected_elements"] == new_elements

    def test_apply_expected_elements_no_change_if_same(self):
        """Test that no update occurs if elements are already correct."""
        elements = [{"type": "test", "required": True, "minimum": 1}]
        contract = {"question_context": {"expected_elements": elements}}
        
        updated = _apply_expected_elements(contract, elements)
        assert updated is False


class TestValidationRulesGeneration:
    """Test validation rules generation."""

    def test_generate_validation_rules_basic(self):
        """Test basic validation rules generation."""
        expected_elements = [
            {"type": "required_type", "required": True, "minimum": 2},
            {"type": "optional_type", "required": False, "minimum": 1}
        ]
        
        rules = _generate_validation_rules(expected_elements)
        
        assert len(rules) == 2
        assert rules[0]["type"] == "array"
        assert rules[0]["field"] == "elements_found"
        assert "must_contain" in rules[0]
        assert "should_contain" in rules[1]

    def test_generate_validation_rules_required_only(self):
        """Test validation rules with only required elements."""
        expected_elements = [
            {"type": "req1", "required": True, "minimum": 1},
            {"type": "req2", "required": True, "minimum": 2}
        ]
        
        rules = _generate_validation_rules(expected_elements)
        must_contain = rules[0]["must_contain"]
        
        assert must_contain["count"] == 2
        assert "req1" in must_contain["elements"]
        assert "req2" in must_contain["elements"]

    def test_normalize_validation_rules_creates_new(self):
        """Test that validation rules are created if missing."""
        contract = {
            "question_context": {
                "expected_elements": [
                    {"type": "test", "required": True, "minimum": 1}
                ]
            }
        }
        
        updated = _normalize_validation_rules(contract)
        assert updated is True
        assert "validation_rules" in contract
        assert "rules" in contract["validation_rules"]

    def test_normalize_validation_rules_no_change_if_correct(self):
        """Test that validation rules aren't changed if already correct."""
        expected_elements = [{"type": "test", "required": True, "minimum": 1}]
        correct_rules = _generate_validation_rules(expected_elements)
        
        contract = {
            "question_context": {"expected_elements": expected_elements},
            "validation_rules": {"rules": correct_rules}
        }
        
        updated = _normalize_validation_rules(contract)
        assert updated is False


class TestContractNormalization:
    """Test contract normalization functions."""

    def test_normalize_output_schema_consts(self):
        """Test output schema const normalization."""
        contract = {
            "identity": {
                "question_id": "Q001",
                "policy_area_id": "PA01",
                "dimension_id": "D1"
            },
            "output_contract": {
                "schema": {
                    "properties": {
                        "question_id": {"const": "Q999"},  # Wrong
                        "policy_area_id": {"const": "PA01"}  # Correct
                    }
                }
            }
        }
        
        updated = _normalize_output_schema_consts(contract)
        assert updated is True
        assert contract["output_contract"]["schema"]["properties"]["question_id"]["const"] == "Q001"

    def test_normalize_question_context_labels(self):
        """Test question context label normalization."""
        policy_area_names = {"PA01": "Policy Area 1"}
        dimension_names = {"D1": "Dimension 1"}
        
        contract = {
            "identity": {
                "policy_area_id": "PA01",
                "dimension_id": "D1"
            },
            "question_context": {
                "policy_area_label": "Wrong Label",
                "dimension_label": "Wrong Dimension"
            }
        }
        
        updated = _normalize_question_context_labels(
            contract, policy_area_names, dimension_names
        )
        assert updated is True
        assert contract["question_context"]["policy_area_label"] == "Policy Area 1"
        assert contract["question_context"]["dimension_label"] == "Dimension 1"

    def test_normalize_patterns_policy_area(self):
        """Test patterns policy area normalization."""
        contract = {
            "identity": {"policy_area_id": "PA01"},
            "question_context": {
                "patterns": [
                    {"policy_area": "PA99", "match_type": ""},  # Wrong
                    {"policy_area": "PA01", "confidence_weight": 2.0}  # Invalid weight
                ]
            }
        }
        
        updated = _normalize_patterns_policy_area(contract)
        assert updated is True
        assert contract["question_context"]["patterns"][0]["policy_area"] == "PA01"
        assert contract["question_context"]["patterns"][0]["match_type"] == "REGEX"
        assert contract["question_context"]["patterns"][1]["confidence_weight"] == 0.8

    def test_normalize_template_text_adds_question_id(self):
        """Test template text normalization adds question ID."""
        policy_area_names = {"PA01": "Policy Area"}
        
        contract = {
            "identity": {
                "question_id": "Q001",
                "base_slot": "D1-Q1",
                "policy_area_id": "PA01"
            },
            "output_contract": {
                "human_readable_output": {
                    "template": {
                        "title": "## Some Title",
                        "summary": "A summary"
                    }
                }
            }
        }
        
        updated = _normalize_template_text(contract, policy_area_names)
        assert updated is True
        title = contract["output_contract"]["human_readable_output"]["template"]["title"]
        assert "Q001" in title
        assert "D1-Q1" in title

    def test_normalize_traceability_source_hash(self):
        """Test traceability source hash normalization."""
        contract = {
            "traceability": {
                "monolith_source_hash": "old_hash"
            }
        }
        
        updated = _normalize_traceability_source_hash(contract, "new_hash")
        assert updated is True
        assert contract["traceability"]["monolith_source_hash"] == "new_hash"


class TestScoreSummarization:
    """Test score summarization logic."""

    def test_summarize_scores_basic(self):
        """Test basic score summarization."""
        scores = [
            ContractScore("Q001", 95.0, "PASS"),
            ContractScore("Q002", 96.0, "PASS"),
            ContractScore("Q003", 94.0, "FAIL")
        ]
        
        min_score, avg_score, pass_count = _summarize_scores(scores, 95.0)
        
        assert min_score == 94.0
        assert avg_score == pytest.approx(95.0, 0.01)
        assert pass_count == 2

    def test_summarize_scores_empty_list(self):
        """Test summarization with empty score list."""
        min_score, avg_score, pass_count = _summarize_scores([], 95.0)
        
        assert min_score == 0.0
        assert avg_score == 0.0
        assert pass_count == 0

    def test_summarize_scores_all_pass(self):
        """Test summarization when all scores pass."""
        scores = [
            ContractScore("Q001", 95.0, "PASS"),
            ContractScore("Q002", 96.0, "PASS"),
            ContractScore("Q003", 97.0, "PASS")
        ]
        
        min_score, avg_score, pass_count = _summarize_scores(scores, 95.0)
        
        assert pass_count == 3
        assert min_score == 95.0
        assert avg_score == 96.0

    def test_summarize_scores_all_fail(self):
        """Test summarization when all scores fail."""
        scores = [
            ContractScore("Q001", 90.0, "FAIL"),
            ContractScore("Q002", 92.0, "FAIL"),
            ContractScore("Q003", 94.0, "FAIL")
        ]
        
        min_score, avg_score, pass_count = _summarize_scores(scores, 95.0)
        
        assert pass_count == 0
        assert avg_score == 92.0


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_safe_get_with_none(self):
        """Test safe_get with None values."""
        data = {"key": None}
        assert _safe_get(data, "key.nested") is None

    def test_canonical_expected_elements_with_empty_contracts(self):
        """Test canonical elements with empty contracts list."""
        result = _canonical_expected_elements([])
        assert result == []

    def test_canonical_expected_elements_with_missing_context(self):
        """Test canonical elements when contracts lack expected_elements."""
        contracts = [
            {"question_context": {}},
            {"other_field": "value"}
        ]
        result = _canonical_expected_elements(contracts)
        assert result == []

    def test_normalize_validation_rules_missing_expected_elements(self):
        """Test validation rules normalization with missing expected_elements."""
        contract = {"question_context": {}}
        updated = _normalize_validation_rules(contract)
        assert updated is False

    def test_choose_better_expected_element_with_invalid_minimum(self):
        """Test element selection with invalid minimum values."""
        elem1 = {"type": "test", "required": True, "minimum": "invalid"}
        elem2 = {"type": "test", "required": True, "minimum": 5}
        
        result = _choose_better_expected_element(elem1, elem2)
        # Should handle gracefully and compare properly
        assert result is not None


class TestGroupOperations:
    """Test equivalence group operations."""

    def test_all_groups_covered(self):
        """Test that all 30 groups are covered."""
        all_questions = set()
        for group_id in range(NUM_GROUPS):
            questions = _group_question_ids(group_id)
            all_questions.update(questions)
        
        # Should have 300 total unique questions
        assert len(all_questions) == NUM_GROUPS * NUM_POLICY_AREAS

    def test_group_membership_consistency(self):
        """Test that each question belongs to exactly one group."""
        question_to_group = {}
        
        for group_id in range(NUM_GROUPS):
            questions = _group_question_ids(group_id)
            for q in questions:
                assert q not in question_to_group, f"Question {q} in multiple groups"
                question_to_group[q] = group_id

    def test_group_spacing_correct(self):
        """Test that questions in a group are spaced by 30."""
        for group_id in range(NUM_GROUPS):
            questions = _group_question_ids(group_id)
            question_nums = [int(q[1:]) for q in questions]
            
            # Check spacing
            for i in range(1, len(question_nums)):
                assert question_nums[i] - question_nums[i-1] == NUM_GROUPS


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
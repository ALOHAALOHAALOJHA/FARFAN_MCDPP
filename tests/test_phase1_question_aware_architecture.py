#!/usr/bin/env python3
"""
Phase 1 Question-Aware Architecture Integration Test
====================================================

This test validates the architectural changes made to Phase 1 to support
question-level granularity (300 questions = 10 PA × 6 DIM × 5 Q/slot).

Tests the following audit findings:
- 2.2: 60 chunks (PA×DIM) vs 300 questions (PA×DIM×Q) granularity mismatch
- 2.3: Method sets defined in questionnaire are not invoked
- 2.4: Expected elements are not verified

Run with:
    pytest tests/test_phase1_question_aware_architecture.py -v

Author: F.A.R.F.A.N Pipeline Team
Version: 2.0.0 - Question-Aware Architecture
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add src to path for imports

import pytest


class TestQuestionAwareArchitecture:
    """Test suite for Phase 1 question-aware architecture."""

    @pytest.fixture
    def questionnaire_path(self) -> Path:
        """Path to questionnaire_monolith.json."""
        path = Path(__file__).resolve().parent.parent / "canonic_questionnaire_central" / "questionnaire_monolith.json"
        if not path.exists():
            pytest.skip(f"Questionnaire not found at {path}")
        return path

    @pytest.fixture
    def questionnaire_data(self, questionnaire_path: Path) -> Dict[str, Any]:
        """Load questionnaire JSON data."""
        with open(questionnaire_path) as f:
            return json.load(f)

    @pytest.fixture
    def questionnaire_map(self, questionnaire_path: Path):
        """Load questionnaire map."""
        from farfan_pipeline.phases.Phase_01.phase1_06_00_questionnaire_mapper import load_questionnaire_map
        return load_questionnaire_map(questionnaire_path)

    # ========================================================================
    # Test 1: Questionnaire Mapping (Audit Finding 2.2)
    # ========================================================================

    def test_questionnaire_has_300_questions(self, questionnaire_data: Dict[str, Any]):
        """Verify questionnaire has exactly 300 micro questions."""
        micro_questions = questionnaire_data.get('blocks', {}).get('micro_questions', [])
        assert len(micro_questions) == 300, (
            f"Expected 300 micro questions, got {len(micro_questions)}"
        )

    def test_questionnaire_map_loads_all_questions(self, questionnaire_map):
        """Verify questionnaire map loads all 300 questions."""
        assert questionnaire_map.is_loaded(), "Questionnaire map should be loaded"
        assert len(questionnaire_map.questions_by_id) == 300, (
            f"Expected 300 questions in map, got {len(questionnaire_map.questions_by_id)}"
        )

    def test_question_map_has_correct_structure(self, questionnaire_map):
        """Verify each question has correct PA×DIM×Q mapping."""
        from farfan_pipeline.phases.Phase_01.phase1_06_00_questionnaire_mapper import (
            NUM_POLICY_AREAS, NUM_DIMENSIONS, QUESTIONS_PER_DIMENSION
        )

        expected_combinations = NUM_POLICY_AREAS * NUM_DIMENSIONS

        # Check PA×DIM combinations
        assert len(questionnaire_map.questions_by_pa_dim) == expected_combinations, (
            f"Expected {expected_combinations} PA×DIM combinations, "
            f"got {len(questionnaire_map.questions_by_pa_dim)}"
        )

        # Check each combination has exactly 5 questions
        for key, questions in questionnaire_map.questions_by_pa_dim.items():
            pa, dim = key
            assert len(questions) == QUESTIONS_PER_DIMENSION, (
                f"Expected {QUESTIONS_PER_DIMENSION} questions for {pa}×{dim}, "
                f"got {len(questions)}"
            )

    def test_question_spec_has_required_fields(self, questionnaire_map):
        """Verify each question spec has all required fields."""
        from farfan_pipeline.phases.Phase_01.phase1_06_00_questionnaire_mapper import QuestionSpec

        for question_id, spec in questionnaire_map.questions_by_id.items():
            assert isinstance(spec, QuestionSpec), f"{question_id} should be QuestionSpec"
            assert spec.question_id == question_id, f"ID mismatch for {question_id}"
            assert spec.policy_area.startswith("PA"), f"{question_id} has invalid PA: {spec.policy_area}"
            assert spec.dimension.startswith("DIM"), f"{question_id} has invalid DIM: {spec.dimension}"
            assert 1 <= spec.slot <= 5, f"{question_id} has invalid slot: {spec.slot}"
            # Verify has patterns, method_sets, expected_elements
            assert hasattr(spec, 'patterns'), f"{question_id} missing patterns"
            assert hasattr(spec, 'method_sets'), f"{question_id} missing method_sets"
            assert hasattr(spec, 'expected_elements'), f"{question_id} missing expected_elements"

    # ========================================================================
    # Test 2: Chunk Model Extensions (Audit Finding 2.2)
    # ========================================================================

    def test_chunk_model_has_question_fields(self):
        """Verify Chunk model has question-aware fields."""
        from farfan_pipeline.phases.Phase_01.phase1_03_00_models import Chunk

        chunk = Chunk(
            chunk_id="CHUNK-PA01DIM01-Q1",
            policy_area_id="PA01",
            dimension_id="DIM01",
            question_id="Q001",
            question_slot=1,
        )

        assert chunk.question_id == "Q001", "Chunk should have question_id"
        assert chunk.question_slot == 1, "Chunk should have question_slot"
        assert hasattr(chunk, 'question_patterns'), "Chunk should have question_patterns"
        assert hasattr(chunk, 'question_method_sets'), "Chunk should have question_method_sets"
        assert hasattr(chunk, 'expected_elements'), "Chunk should have expected_elements"
        assert hasattr(chunk, 'elements_verification'), "Chunk should have elements_verification"
        assert hasattr(chunk, 'method_invocation_results'), "Chunk should have method_invocation_results"

    # ========================================================================
    # Test 3: Phase 1 Constants Updated (Audit Finding 2.2)
    # ========================================================================

    def test_phase1_constants_updated_for_300_chunks(self):
        """Verify Phase 1 constants reflect 300 chunk architecture."""
        from farfan_pipeline.phases.Phase_01.PHASE_1_CONSTANTS import (
            TOTAL_CHUNK_COMBINATIONS,
            TOTAL_CHUNK_COMBINATIONS_LEGACY,
            QUESTIONS_PER_DIMENSION,
            CHUNK_ID_PATTERN,
            QUESTION_ID_PATTERN,
            POLICY_AREA_COUNT,
            DIMENSION_COUNT,
        )

        # New constant should be 300
        assert TOTAL_CHUNK_COMBINATIONS == 300, (
            f"TOTAL_CHUNK_COMBINATIONS should be 300, got {TOTAL_CHUNK_COMBINATIONS}"
        )

        # Legacy constant should still be 60
        assert TOTAL_CHUNK_COMBINATIONS_LEGACY == 60, (
            f"TOTAL_CHUNK_COMBINATIONS_LEGACY should be 60, got {TOTAL_CHUNK_COMBINATIONS_LEGACY}"
        )

        # Should have 5 questions per dimension
        assert QUESTIONS_PER_DIMENSION == 5, (
            f"QUESTIONS_PER_DIMENSION should be 5, got {QUESTIONS_PER_DIMENSION}"
        )

        # Chunk pattern should include question slot
        assert "Q[1-5]" in CHUNK_ID_PATTERN, (
            f"CHUNK_ID_PATTERN should include Q[1-5], got {CHUNK_ID_PATTERN}"
        )

        # Should have QUESTION_ID_PATTERN
        assert QUESTION_ID_PATTERN is not None, "QUESTION_ID_PATTERN should be defined"

        # PA and DIM counts should be correct
        assert POLICY_AREA_COUNT == 10, f"POLICY_AREA_COUNT should be 10, got {POLICY_AREA_COUNT}"
        assert DIMENSION_COUNT == 6, f"DIMENSION_COUNT should be 6, got {DIMENSION_COUNT}"

    # ========================================================================
    # Test 4: SP4 Question-Aware Segmentation (Audit Finding 2.2)
    # ========================================================================

    def test_sp4_question_aware_imports(self):
        """Verify SP4 question-aware module can be imported."""
        from farfan_pipeline.phases.Phase_01 import phase1_07_00_sp4_question_aware as sp4_module

        assert hasattr(sp4_module, 'execute_sp4_question_aware'), (
            "SP4 module should have execute_sp4_question_aware function"
        )
        assert hasattr(sp4_module, 'TOTAL_CHUNK_COMBINATIONS'), (
            "SP4 module should export TOTAL_CHUNK_COMBINATIONS"
        )
        assert sp4_module.TOTAL_CHUNK_COMBINATIONS == 300, (
            f"SP4 TOTAL_CHUNK_COMBINATIONS should be 300, got {sp4_module.TOTAL_CHUNK_COMBINATIONS}"
        )

    def test_sp4_question_aware_signature(self):
        """Verify SP4 question-aware function has correct signature."""
        import inspect
        from farfan_pipeline.phases.Phase_01.phase1_07_00_sp4_question_aware import execute_sp4_question_aware

        sig = inspect.signature(execute_sp4_question_aware)
        params = list(sig.parameters.keys())

        # Should have these parameters
        required_params = [
            'preprocessed',
            'structure',
            'kg',
            'questionnaire_path',
        ]
        for param in required_params:
            assert param in params, f"SP4 should have parameter {param}"

        # Optional parameters
        optional_params = ['method_registry', 'signal_enricher']
        for param in optional_params:
            assert param in params, f"SP4 should have optional parameter {param}"

    # ========================================================================
    # Test 5: Question ID Parsing (Audit Finding 2.2)
    # ========================================================================

    def test_parse_question_id(self):
        """Verify question ID parsing works correctly."""
        from farfan_pipeline.phases.Phase_01.phase1_06_00_questionnaire_mapper import parse_question_id

        test_cases = [
            ("Q001", ("PA01", "DIM01", 1)),
            ("Q005", ("PA01", "DIM01", 5)),
            ("Q006", ("PA01", "DIM02", 1)),
            ("Q030", ("PA01", "DIM06", 5)),
            ("Q031", ("PA02", "DIM01", 1)),
            ("Q150", ("PA05", "DIM06", 5)),  # Q150 = PA05 (idx 4), DIM06 (idx 5), slot 5
            ("Q300", ("PA10", "DIM06", 5)),
        ]

        for question_id, expected in test_cases:
            result = parse_question_id(question_id)
            assert result == expected, (
                f"parse_question_id({question_id}) should return {expected}, got {result}"
            )

    def test_create_chunk_id_for_question(self):
        """Verify chunk ID creation works correctly."""
        from farfan_pipeline.phases.Phase_01.phase1_06_00_questionnaire_mapper import create_chunk_id_for_question

        test_cases = [
            (("PA01", "DIM01", 1), "CHUNK-PA01DIM01-Q1"),
            (("PA01", "DIM01", 5), "CHUNK-PA01DIM01-Q5"),
            (("PA10", "DIM06", 3), "CHUNK-PA10DIM06-Q3"),
        ]

        for inputs, expected in test_cases:
            result = create_chunk_id_for_question(*inputs)
            assert result == expected, (
                f"create_chunk_id_for_question{inputs} should return {expected}, got {result}"
            )

    # ========================================================================
    # Test 6: Method Set Invocation (Audit Finding 2.3)
    # ========================================================================

    def test_method_sets_exist_in_questionnaire(self, questionnaire_map):
        """Verify questions have method_sets defined."""
        questions_with_methods = 0

        for question_id, spec in questionnaire_map.questions_by_id.items():
            if spec.method_sets:
                questions_with_methods += 1

                # Verify method_set structure
                for method_spec in spec.method_sets:
                    assert 'class' in method_spec, f"{question_id} method missing 'class'"
                    assert 'function' in method_spec, f"{question_id} method missing 'function'"

        # At least some questions should have method sets
        assert questions_with_methods > 0, (
            f"Expected some questions to have method_sets, got {questions_with_methods}/300"
        )

        logger.warning(
            f"Audit Finding 2.3: {questions_with_methods}/300 questions have method_sets defined"
        )

    # ========================================================================
    # Test 7: Expected Elements Verification (Audit Finding 2.4)
    # ========================================================================

    def test_expected_elements_exist_in_questionnaire(self, questionnaire_map):
        """Verify questions have expected_elements defined."""
        questions_with_elements = 0
        total_required_elements = 0

        for question_id, spec in questionnaire_map.questions_by_id.items():
            if spec.expected_elements:
                questions_with_elements += 1

                # Count required elements
                for elem in spec.expected_elements:
                    if elem.get('required', False):
                        total_required_elements += 1

                    # Verify element structure
                    assert 'type' in elem, f"{question_id} element missing 'type'"

        # At least some questions should have expected elements
        assert questions_with_elements > 0, (
            f"Expected some questions to have expected_elements, got {questions_with_elements}/300"
        )

        logger.warning(
            f"Audit Finding 2.4: {questions_with_elements}/300 questions have expected_elements, "
            f"{total_required_elements} required elements total"
        )

    # ========================================================================
    # Test 8: Pattern Loading (Audit Finding 2.4)
    # ========================================================================

    def test_signal_enrichment_loads_questionnaire_patterns(self, questionnaire_path):
        """Verify signal enrichment can load patterns from questionnaire."""
        from farfan_pipeline.phases.Phase_one.phase1_11_00_signal_enrichment import (
            load_questionnaire_patterns,
            load_causal_patterns_from_questionnaire,
        )

        # Load patterns
        patterns_by_question = load_questionnaire_patterns(questionnaire_path)
        assert len(patterns_by_question) > 0, "Should load patterns from questionnaire"

        # Verify structure
        for q_id, patterns in list(patterns_by_question.items())[:3]:
            assert isinstance(patterns, list), f"Patterns for {q_id} should be a list"
            for pattern, category, weight in patterns:
                assert isinstance(pattern, str), f"Pattern should be string for {q_id}"
                assert isinstance(category, str), f"Category should be string for {q_id}"
                assert isinstance(weight, (int, float)), f"Weight should be numeric for {q_id}"

        # Load causal patterns
        causal_patterns = load_causal_patterns_from_questionnaire(questionnaire_path)
        assert len(causal_patterns) > 0, "Should load causal patterns from questionnaire"

        logger.info(
            f"Loaded {len(patterns_by_question)} questions with patterns, "
            f"{len(causal_patterns)} causal patterns"
        )


# Logger for warnings
import logging
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "--tb=short"])

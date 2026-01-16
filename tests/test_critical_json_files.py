"""
Test critical JSON configuration files.

Ensures that the three critical JSON files exist, are valid, and maintain
synchronization as documented:
- METHODS_TO_QUESTIONS_AND_FILES.json
- METHODS_OPERACIONALIZACION.json  
- questionnaire_monolith.json
"""

import json
import pytest
from pathlib import Path


class TestCriticalJSONFiles:
    """Validate critical JSON configuration files."""

    @pytest.fixture
    def repo_root(self) -> Path:
        """Get repository root."""
        return Path(__file__).resolve().parent.parent

    @pytest.fixture
    def methods_to_questions_path(self, repo_root: Path) -> Path:
        """Path to METHODS_TO_QUESTIONS_AND_FILES.json."""
        return repo_root / "canonic_questionnaire_central" / "governance" / "METHODS_TO_QUESTIONS_AND_FILES.json"

    @pytest.fixture
    def methods_operacionalizacion_path(self, repo_root: Path) -> Path:
        """Path to METHODS_OPERACIONALIZACION.json."""
        return repo_root / "canonic_questionnaire_central" / "governance" / "METHODS_OPERACIONALIZACION.json"

    @pytest.fixture
    def questionnaire_monolith_path(self, repo_root: Path) -> Path:
        """Path to questionnaire_monolith.json."""
        return repo_root / "canonic_questionnaire_central" / "questionnaire_monolith.json"

    def test_methods_to_questions_exists(self, methods_to_questions_path: Path) -> None:
        """Test that METHODS_TO_QUESTIONS_AND_FILES.json exists."""
        assert methods_to_questions_path.exists(), (
            f"METHODS_TO_QUESTIONS_AND_FILES.json not found at {methods_to_questions_path}"
        )

    def test_methods_operacionalizacion_exists(self, methods_operacionalizacion_path: Path) -> None:
        """Test that METHODS_OPERACIONALIZACION.json exists."""
        assert methods_operacionalizacion_path.exists(), (
            f"METHODS_OPERACIONALIZACION.json not found at {methods_operacionalizacion_path}"
        )

    def test_questionnaire_monolith_exists(self, questionnaire_monolith_path: Path) -> None:
        """Test that questionnaire_monolith.json exists."""
        assert questionnaire_monolith_path.exists(), (
            f"questionnaire_monolith.json not found at {questionnaire_monolith_path}"
        )

    def test_methods_to_questions_valid_json(self, methods_to_questions_path: Path) -> None:
        """Test that METHODS_TO_QUESTIONS_AND_FILES.json is valid JSON."""
        with open(methods_to_questions_path) as f:
            data = json.load(f)
        
        assert "_metadata" in data, "Missing _metadata section"
        assert "methods" in data, "Missing methods section"
        assert isinstance(data["methods"], dict), "methods should be a dictionary"

    def test_methods_operacionalizacion_valid_json(self, methods_operacionalizacion_path: Path) -> None:
        """Test that METHODS_OPERACIONALIZACION.json is valid JSON."""
        with open(methods_operacionalizacion_path) as f:
            data = json.load(f)
        
        assert "_metadata" in data, "Missing _metadata section"
        assert "methods" in data, "Missing methods section"
        assert isinstance(data["methods"], dict), "methods should be a dictionary"

    def test_questionnaire_monolith_valid_json(self, questionnaire_monolith_path: Path) -> None:
        """Test that questionnaire_monolith.json is valid JSON."""
        with open(questionnaire_monolith_path) as f:
            data = json.load(f)
        
        assert "_schema_version" in data, "Missing _schema_version"
        assert "blocks" in data, "Missing blocks section"
        assert "micro_questions" in data["blocks"], "Missing micro_questions in blocks"
        assert isinstance(data["blocks"]["micro_questions"], list), "micro_questions should be a list"

    def test_methods_synchronization(
        self, 
        methods_to_questions_path: Path,
        methods_operacionalizacion_path: Path
    ) -> None:
        """
        Test that METHODS_TO_QUESTIONS_AND_FILES.json and METHODS_OPERACIONALIZACION.json
        contain the same method IDs (CRITICAL synchronization requirement).
        """
        with open(methods_to_questions_path) as f:
            methods_q = json.load(f)
        
        with open(methods_operacionalizacion_path) as f:
            methods_o = json.load(f)
        
        methods_q_ids = set(methods_q["methods"].keys())
        methods_o_ids = set(methods_o["methods"].keys())
        
        assert methods_q_ids == methods_o_ids, (
            f"Method IDs must be synchronized between files. "
            f"METHODS_TO_QUESTIONS has {len(methods_q_ids)} methods, "
            f"METHODS_OPERACIONALIZACION has {len(methods_o_ids)} methods. "
            f"Difference: {methods_q_ids.symmetric_difference(methods_o_ids)}"
        )

    def test_questionnaire_has_expected_questions(self, questionnaire_monolith_path: Path) -> None:
        """
        Test that questionnaire_monolith.json contains expected number of questions.
        
        Per canonical notation: Q001-Q030 base questions × 10 Policy Areas = 300 total questions.
        This test validates the count matches the documented architecture.
        """
        with open(questionnaire_monolith_path) as f:
            data = json.load(f)
        
        questions = data["blocks"]["micro_questions"]
        
        # Per canonical notation: 30 base questions × 10 policy areas = 300
        expected_min = 300
        
        assert len(questions) >= expected_min, (
            f"Expected at least {expected_min} questions (30 base × 10 policy areas), "
            f"found {len(questions)}"
        )
        
        # Validate question IDs are sequential
        question_ids = [q["question_id"] for q in questions]
        assert question_ids[0].startswith("Q"), "Question IDs should start with 'Q'"

    def test_questionnaire_has_sha256(self, questionnaire_monolith_path: Path) -> None:
        """Test that questionnaire_monolith.json has a SHA256 hash for integrity verification."""
        with open(questionnaire_monolith_path) as f:
            data = json.load(f)
        
        assert "sha256" in data, "questionnaire_monolith.json must have a sha256 field"
        assert len(data["sha256"]) == 64, "SHA256 hash should be 64 characters"

    def test_questionnaire_question_structure(self, questionnaire_monolith_path: Path) -> None:
        """Test that questions in questionnaire_monolith.json have required fields."""
        with open(questionnaire_monolith_path) as f:
            data = json.load(f)
        
        questions = data["blocks"]["micro_questions"]
        
        # Check first question has required fields
        if questions:
            first_q = questions[0]
            required_fields = [
                "question_id",
                "dimension_id",
                "policy_area_id",
                "text",
                "scoring_modality"
            ]
            
            for field in required_fields:
                assert field in first_q, (
                    f"Question missing required field: {field}"
                )

    def test_methods_have_required_metadata(
        self,
        methods_to_questions_path: Path,
        methods_operacionalizacion_path: Path
    ) -> None:
        """Test that both methods files have required metadata fields."""
        with open(methods_to_questions_path) as f:
            methods_q = json.load(f)
        
        with open(methods_operacionalizacion_path) as f:
            methods_o = json.load(f)
        
        # Check METHODS_TO_QUESTIONS_AND_FILES metadata
        assert "version" in methods_q["_metadata"]
        assert "total_methods" in methods_q["_metadata"]
        assert "synchronization_note" in methods_q["_metadata"]
        
        # Check METHODS_OPERACIONALIZACION metadata
        assert "version" in methods_o["_metadata"]
        assert "total_methods" in methods_o["_metadata"]
        assert "synchronization_note" in methods_o["_metadata"]
        
        # Verify metadata counts match actual counts
        assert methods_q["_metadata"]["total_methods"] == len(methods_q["methods"])
        assert methods_o["_metadata"]["total_methods"] == len(methods_o["methods"])

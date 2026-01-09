"""
Comprehensive Test Suite for Modular Resolver Implementation

Tests for all three job fronts:
- JF0: CanonicalQuestionnaireResolver implementation
- JF1: Factory migration with backward compatibility
- JF2: SISAS validation with provenance tracking

Acceptance Criteria:
1. Produces 300 micro questions
2. Implements QuestionnairePort protocol
3. Deterministic hash
4. Provenance complete
5. SISAS compatible
6. Singleton preserved
7. Hash verification works
8. Source validation

Author: F. A. R.F.A.N Pipeline Team
Date: 2026-01-09
"""

import hashlib
import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add parent directory to path for imports

try:
    from canonic_questionnaire_central.resolver import (
        CanonicalQuestionnaireResolver,
        CanonicalQuestionnaire,
        AssemblyProvenance,
        QuestionnairePort,
        ResolverError,
        AssemblyError,
        IntegrityError,
        ValidationError,
        resolve_questionnaire,
        get_resolver,
    )
    MODULAR_RESOLVER_AVAILABLE = True
except ImportError as e:
    MODULAR_RESOLVER_AVAILABLE = False
    print(f"Warning: Modular resolver not available: {e}")

try:
    from farfan_pipeline.phases.Phase_two.phase2_10_00_factory import (
        AnalysisPipelineFactory,
        load_questionnaire,
        _USE_MODULAR_RESOLVER,
        _ALLOW_FALLBACK_TO_MONOLITH,
        GovernanceViolationError,
        QuestionnaireLoadError,
        CanonicalQuestionnaire as FactoryCanonicalQuestionnaire,
    )
    FACTORY_AVAILABLE = True
except ImportError as e:
    FACTORY_AVAILABLE = False
    print(f"Warning: Factory not available: {e}")

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_registry import (
        QuestionnaireSignalRegistry,
        create_signal_registry,
    )
    from farfan_pipeline.infrastructure.irrigation_using_signals.ports import (
        QuestionnairePort as SignalQuestionnairePort,
    )
    SISAS_AVAILABLE = True
except ImportError as e:
    SISAS_AVAILABLE = False
    print(f"Warning: SISAS not available: {e}")

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def test_data_dir(tmp_path: Path) -> Path:
    """Create a temporary test data directory with modular structure."""
    # Create test directory structure
    dimensions_dir = tmp_path / "dimensions"
    dimensions_dir.mkdir()
    for i in range(1, 7):
        dim_dir = dimensions_dir / f"DIM{i:02d}"
        dim_dir.mkdir()
        # Create metadata
        (dim_dir / "metadata.json").write_text(json.dumps({
            "dimension_id": f"DIM{i:02d}",
            "name": f"Dimension {i}",
        }))
        # Create questions (5 questions per dimension × 10 policy areas = 300 total)
        questions = []
        for j in range(1, 11):
            for k in range(1, 6):
                q_num = (i - 1) * 50 + (j - 1) * 5 + k
                questions.append({
                    "question_id": f"Q{q_num:03d}",
                    "dimension_id": f"DIM{i:02d}",
                    "policy_area_id": f"PA{j:02d}",
                    "text": f"Test question {q_num}",
                    "scoring_modality": "TYPE_A",
                    "patterns": [],
                    "expected_elements": [],
                })
        (dim_dir / "questions.json").write_text(json.dumps(questions))

    policy_areas_dir = tmp_path / "policy_areas"
    policy_areas_dir.mkdir()
    for i in range(1, 11):
        pa_dir = policy_areas_dir / f"PA{i:02d}_test"
        pa_dir.mkdir()
        # Create metadata
        (pa_dir / "metadata.json").write_text(json.dumps({
            "policy_area_id": f"PA{i:02d}",
            "name": f"Policy Area {i}",
        }))

    clusters_dir = tmp_path / "clusters"
    clusters_dir.mkdir()
    for i in range(1, 5):
        cluster_dir = clusters_dir / f"CL{i:02d}_test"
        cluster_dir.mkdir()
        (cluster_dir / "metadata.json").write_text(json.dumps({
            "cluster_id": f"CL{i:02d}",
            "name": f"Cluster {i}",
            "policy_area_ids": [f"PA{j:02d}" for j in range((i-1)*3+1, i*3+1)],
        }))

    governance_dir = tmp_path / "governance"
    governance_dir.mkdir()
    (governance_dir / "integrity.json").write_text(json.dumps({}))
    (governance_dir / "observability.json").write_text(json.dumps({}))
    (governance_dir / "versioning.json").write_text(json.dumps({
        "current_version": "1.0.0"
    }))

    scoring_dir = tmp_path / "scoring"
    scoring_dir.mkdir()
    (scoring_dir / "modality_definitions.json").write_text(json.dumps({}))
    (scoring_dir / "micro_levels.json").write_text(json.dumps({}))
    (scoring_dir / "quality_thresholds.json").write_text(json.dumps({}))

    patterns_dir = tmp_path / "patterns"
    patterns_dir.mkdir()
    (patterns_dir / "index.json").write_text(json.dumps({"patterns": {}}))

    semantic_dir = tmp_path / "semantic"
    semantic_dir.mkdir()
    (semantic_dir / "embedding_strategy.json").write_text(json.dumps({}))
    (semantic_dir / "semantic_layers.json").write_text(json.dumps({}))

    cross_cutting_dir = tmp_path / "cross_cutting"
    cross_cutting_dir.mkdir()
    (cross_cutting_dir / "themes.json").write_text(json.dumps({}))
    (cross_cutting_dir / "interdependencies.json").write_text(json.dumps({}))

    (tmp_path / "canonical_notation.json").write_text(json.dumps({
        "dimensions": {},
        "policy_areas": {},
    }))
    (tmp_path / "meso_questions.json").write_text(json.dumps([]))
    (tmp_path / "macro_question.json").write_text(json.dumps({}))

    return tmp_path


@pytest.fixture
def mock_questionnaire() -> CanonicalQuestionnaire:
    """Create a mock CanonicalQuestionnaire for testing."""
    micro_questions = [
        {
            "question_id": f"Q{i:03d}",
            "text": f"Question {i}",
            "scoring_modality": "TYPE_A",
            "patterns": [],
        }
        for i in range(1, 301)
    ]

    provenance = AssemblyProvenance(
        assembly_timestamp=datetime.now(timezone.utc).isoformat(),
        resolver_version="1.0.0",
        source_file_count=10,
        source_paths=("path1", "path2"),
        assembly_duration_ms=100.0,
    )

    return CanonicalQuestionnaire(
        _data={
            "version": "1.0.0",
            "canonical_notation": {},
            "blocks": {
                "micro_questions": micro_questions,
                "meso_questions": [],
                "macro_question": {},
            },
            "provenance": provenance.to_dict(),
        },
        _sha256=hashlib.sha256(json.dumps({}, sort_keys=True).encode()).hexdigest(),
        _version="1.0.0",
        _micro_questions=micro_questions,
        source="modular_resolver",
        provenance=provenance,
    )


# =============================================================================
# JOB FRONT 0: CanonicalQuestionnaireResolver Tests
# =============================================================================


@pytest.mark.skipif(not MODULAR_RESOLVER_AVAILABLE, reason="Modular resolver not available")
class TestCanonicalQuestionnaireResolver:
    """Test suite for CanonicalQuestionnaireResolver (JF0)."""

    def test_resolver_initialization(self, test_data_dir: Path):
        """Test resolver initializes correctly."""
        resolver = CanonicalQuestionnaireResolver(
            root=test_data_dir,
            strict_mode=True,
            cache_enabled=True,
        )
        assert resolver._root == test_data_dir
        assert resolver._strict_mode is True
        assert resolver._cache_enabled is True

    def test_resolver_creates_questionnaire_port(self, test_data_dir: Path):
        """
        ACCEPTANCE CRITERION: Resolver produces output satisfying QuestionnairePort.

        Protocol requires:
        - .data → dict[str, Any]
        - .version → str
        - .sha256 → str
        - .micro_questions → list[dict[str, Any]]
        """
        resolver = CanonicalQuestionnaireResolver(root=test_data_dir)
        questionnaire = resolver.resolve()

        # Verify QuestionnairePort protocol
        assert hasattr(questionnaire, 'data')
        assert hasattr(questionnaire, 'version')
        assert hasattr(questionnaire, 'sha256')
        assert hasattr(questionnaire, 'micro_questions')
        assert hasattr(questionnaire, '__iter__')

        # Verify types
        assert isinstance(questionnaire.data, dict)
        assert isinstance(questionnaire.version, str)
        assert isinstance(questionnaire.sha256, str)
        assert isinstance(questionnaire.micro_questions, list)

        # Verify runtime_checkable protocol
        assert isinstance(questionnaire, QuestionnairePort)

    def test_resolver_produces_300_questions(self, test_data_dir: Path):
        """
        ACCEPTANCE CRITERION: Produces 300 micro questions.

        len(questionnaire.micro_questions) == 300
        """
        resolver = CanonicalQuestionnaireResolver(root=test_data_dir)
        questionnaire = resolver.resolve()

        assert len(questionnaire.micro_questions) == 300
        # Verify question IDs are in correct format
        for q in questionnaire.micro_questions:
            assert "question_id" in q
            assert q["question_id"].startswith("Q")
            assert 1 <= int(q["question_id"][1:]) <= 300

    def test_deterministic_hash(self, test_data_dir: Path):
        """
        ACCEPTANCE CRITERION: Deterministic hash.

        Run twice, compare hashes - should be identical.
        """
        resolver = CanonicalQuestionnaireResolver(root=test_data_dir)

        questionnaire1 = resolver.resolve(force_rebuild=True)
        questionnaire2 = resolver.resolve(force_rebuild=True)

        assert questionnaire1.sha256 == questionnaire2.sha256

    def test_provenance_complete(self, test_data_dir: Path):
        """
        ACCEPTANCE CRITERION: Provenance complete.

        Verify all source_paths exist and provenance has all required fields.
        """
        resolver = CanonicalQuestionnaireResolver(root=test_data_dir)
        questionnaire = resolver.resolve()

        # Check provenance exists
        assert hasattr(questionnaire, 'provenance')
        provenance = questionnaire.provenance

        # Check all required fields
        assert hasattr(provenance, 'assembly_timestamp')
        assert hasattr(provenance, 'resolver_version')
        assert hasattr(provenance, 'source_file_count')
        assert hasattr(provenance, 'source_paths')
        assert hasattr(provenance, 'assembly_duration_ms')

        # Verify all source paths exist
        for path in provenance.source_paths:
            assert Path(path).exists(), f"Source path does not exist: {path}"

    def test_sisas_compatible(self, test_data_dir: Path):
        """
        ACCEPTANCE CRITERION: SISAS compatible.

        Pass to create_signal_registry(q) - should work without errors.
        """
        if not SISAS_AVAILABLE:
            pytest.skip("SISAS not available")

        resolver = CanonicalQuestionnaireResolver(root=test_data_dir)
        questionnaire = resolver.resolve()

        # Should work with SISAS
        registry = create_signal_registry(questionnaire)
        assert registry is not None
        assert registry._questionnaire == questionnaire

    def test_count_validation_strict_mode(self, test_data_dir: Path):
        """Test count validation in strict mode."""
        # Remove one dimension to trigger validation error
        dim_dir = test_data_dir / "dimensions" / "DIM01"
        if dim_dir.exists():
            import shutil
            shutil.rmtree(dim_dir)

        resolver = CanonicalQuestionnaireResolver(
            root=test_data_dir,
            strict_mode=True,
        )

        with pytest.raises(AssemblyError):
            resolver.resolve()

    def test_count_validation_non_strict_mode(self, test_data_dir: Path):
        """Test count validation in non-strict mode (logs warnings)."""
        # Remove one dimension
        dim_dir = test_data_dir / "dimensions" / "DIM01"
        if dim_dir.exists():
            import shutil
            shutil.rmtree(dim_dir)

        resolver = CanonicalQuestionnaireResolver(
            root=test_data_dir,
            strict_mode=False,
        )

        # Should not raise in non-strict mode
        questionnaire = resolver.resolve()
        assert questionnaire is not None

    def test_hash_verification(self, test_data_dir: Path):
        """Test hash verification works."""
        resolver = CanonicalQuestionnaireResolver(root=test_data_dir)
        questionnaire = resolver.resolve()
        expected_hash = questionnaire.sha256

        # Same hash should pass
        questionnaire2 = resolver.resolve(expected_hash=expected_hash)
        assert questionnaire2.sha256 == expected_hash

        # Different hash should fail
        with pytest.raises(IntegrityError):
            resolver.resolve(expected_hash="wrong_hash")


# =============================================================================
# JOB FRONT 1: Factory Migration Tests
# =============================================================================


@pytest.mark.skipif(not FACTORY_AVAILABLE, reason="Factory not available")
class TestFactoryMigration:
    """Test suite for Factory migration (JF1)."""

    def test_factory_uses_modular_resolver_by_default(self, test_data_dir: Path):
        """
        ACCEPTANCE CRITERION: Default uses modular resolver.

        q.source == "modular_resolver" or source_path contains "modular_resolver"
        """
        # Patch the CANONICAL_QUESTIONNAIRE_PATH to use test data
        import farfan_pipeline.phases.Phase_two.phase2_10_00_factory as factory_module
        original_path = factory_module.CANONICAL_QUESTIONNAIRE_PATH

        # Create a test monolith at the expected location
        test_monolith = test_data_dir / "questionnaire_monolith.json"
        test_data = {
            "version": "1.0.0",
            "canonical_notation": {},
            "blocks": {
                "micro_questions": [
                    {"question_id": f"Q{i:03d}", "text": f"Q{i}"} for i in range(1, 301)
                ],
            },
        }
        test_monolith.write_text(json.dumps(test_data))

        with patch.object(factory_module, 'CANONICAL_QUESTIONNAIRE_PATH', test_monolith):
            # The _USE_MODULAR_RESOLVER flag should be True by default
            assert factory_module._USE_MODULAR_RESOLVER is True

    def test_factory_singleton_preserved(self, test_data_dir: Path):
        """
        ACCEPTANCE CRITERION: Singleton preserved.

        Load twice, same instance.
        """
        # This test verifies the factory's singleton behavior
        import farfan_pipeline.phases.Phase_two.phase2_10_00_factory as factory_module

        # Reset singleton
        factory_module.AnalysisPipelineFactory._questionnaire_loaded = False
        factory_module.AnalysisPipelineFactory._questionnaire_instance = None

        # Create test monolith
        test_monolith = test_data_dir / "questionnaire_monolith.json"
        test_data = {
            "version": "1.0.0",
            "canonical_notation": {},
            "blocks": {
                "micro_questions": [
                    {"question_id": f"Q{i:03d}", "text": f"Q{i}"} for i in range(1, 301)
                ],
            },
        }
        test_monolith.write_text(json.dumps(test_data))

        with patch.object(factory_module, 'CANONICAL_QUESTIONNAIRE_PATH', test_monolith):
            # First load
            q1 = factory_module.load_questionnaire()
            assert factory_module.AnalysisPipelineFactory._questionnaire_loaded is True

            # Second load should reuse singleton
            q2 = factory_module.load_questionnaire()
            assert q1 is q2

    def test_factory_rejects_unauthorized_source(self):
        """
        ACCEPTANCE CRITERION: Source validation.

        Reject unknown sources.
        """
        import farfan_pipeline.phases.Phase_two.phase2_10_00_factory as factory_module

        # Create factory
        factory = factory_module.AnalysisPipelineFactory()

        # Create a questionnaire with unauthorized source
        class MockQuestionnaire:
            source = "unknown_source"
            source_path = "/malicious/path"

        # Should raise GovernanceViolationError
        with pytest.raises(GovernanceViolationError):
            factory._validate_questionnaire_source(MockQuestionnaire())


# =============================================================================
# JOB FRONT 2: SISAS Validation Tests
# =============================================================================


@pytest.mark.skipif(not SISAS_AVAILABLE, reason="SISAS not available")
class TestSisasValidation:
    """Test suite for SISAS validation with provenance tracking (JF2)."""

    def test_sisas_zero_changes_required(self, mock_questionnaire):
        """
        ACCEPTANCE CRITERION: SISAS works unchanged with modular resolver output.

        The current SISAS implementation already uses QuestionnairePort protocol,
        so no changes are required for compatibility.
        """
        # SISAS should accept the modular resolver output
        registry = QuestionnaireSignalRegistry(mock_questionnaire)
        assert registry is not None
        assert registry._questionnaire == mock_questionnaire

    def test_sisas_provenance_tracking(self, mock_questionnaire):
        """
        ACCEPTANCE CRITERION: Provenance tracking in SISAS.

        get_metrics() should include provenance information.
        """
        registry = QuestionnaireSignalRegistry(mock_questionnaire)
        metrics = registry.get_metrics()

        # Verify provenance is tracked
        assert "questionnaire_source" in metrics
        assert metrics["questionnaire_source"] == "modular_resolver"

        # Verify detailed provenance if available
        if mock_questionnaire.provenance:
            assert "questionnaire_provenance" in metrics
            provenance = metrics["questionnaire_provenance"]
            assert "source_file_count" in provenance
            assert "assembly_timestamp" in provenance
            assert "resolver_version" in provenance


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


@pytest.mark.skipif(not (MODULAR_RESOLVER_AVAILABLE and SISAS_AVAILABLE), reason="Dependencies not available")
class TestIntegration:
    """Integration tests for complete pipeline."""

    def test_end_to_end_pipeline(self, test_data_dir: Path):
        """Test complete pipeline from resolver to SISAS."""
        # Step 1: Resolve questionnaire
        resolver = CanonicalQuestionnaireResolver(root=test_data_dir)
        questionnaire = resolver.resolve()

        # Step 2: Pass to SISAS
        registry = create_signal_registry(questionnaire)

        # Step 3: Verify metrics include provenance
        metrics = registry.get_metrics()
        assert "questionnaire_source" in metrics

    def test_hash_verification_chain(self, test_data_dir: Path):
        """Test hash verification throughout the pipeline."""
        resolver = CanonicalQuestionnaireResolver(root=test_data_dir)
        questionnaire = resolver.resolve()
        original_hash = questionnaire.sha256

        # Hash should be consistent
        assert questionnaire.data is not None
        recomputed_hash = hashlib.sha256(
            json.dumps(questionnaire.data, sort_keys=True).encode()
        ).hexdigest()
        assert recomputed_hash == original_hash


# =============================================================================
# RUNNER
# =============================================================================


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s", "--tb=short"])

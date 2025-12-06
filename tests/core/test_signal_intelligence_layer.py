"""
Tests for Signal Intelligence Layer (JOBFRONT 1)

Verifies that EnrichedSignalPack and related types are correctly defined
and have the expected API surface.
"""

import pytest
from unittest.mock import Mock

from farfan_pipeline.core.orchestrator.signal_intelligence_layer import (
    EnrichedSignalPack,
    create_enriched_signal_pack,
    create_document_context,
    PrecisionImprovementStats,
    compute_precision_improvement_stats,
    generate_precision_improvement_report,
    validate_60_percent_target_achievement,
)
from farfan_pipeline.core.orchestrator.signal_evidence_extractor import (
    EvidenceExtractionResult,
)
from farfan_pipeline.core.orchestrator.signal_contract_validator import (
    ValidationResult,
)


@pytest.fixture
def mock_base_signal_pack():
    """Mock base signal pack for testing."""
    mock_pack = Mock(spec=["patterns", "micro_questions"])
    mock_pack.patterns = [
        {
            "id": "PAT_001",
            "pattern": "presupuesto",
            "confidence_weight": 0.85,
            "category": "BUDGET",
        },
        {
            "id": "PAT_002",
            "pattern": "indicador",
            "confidence_weight": 0.75,
            "category": "INDICATOR",
        },
    ]
    mock_pack.micro_questions = [
        {"id": "Q001", "question": "Test question", "patterns": mock_pack.patterns}
    ]
    return mock_pack


def test_enriched_signal_pack_instantiation(mock_base_signal_pack):
    """Test that EnrichedSignalPack can be instantiated."""
    enriched = EnrichedSignalPack(
        mock_base_signal_pack, enable_semantic_expansion=False
    )

    assert enriched is not None
    assert enriched.base_pack == mock_base_signal_pack
    assert len(enriched.patterns) == 2


def test_enriched_signal_pack_has_required_methods(mock_base_signal_pack):
    """Test that EnrichedSignalPack has all required methods."""
    enriched = EnrichedSignalPack(
        mock_base_signal_pack, enable_semantic_expansion=False
    )

    # Check all methods exist
    assert hasattr(enriched, "get_patterns_for_context")
    assert hasattr(enriched, "expand_patterns")
    assert hasattr(enriched, "extract_evidence")
    assert hasattr(enriched, "validate_result")
    assert hasattr(enriched, "get_average_confidence")
    assert hasattr(enriched, "get_node")

    # Check they are callable
    assert callable(enriched.get_patterns_for_context)
    assert callable(enriched.expand_patterns)
    assert callable(enriched.extract_evidence)
    assert callable(enriched.validate_result)
    assert callable(enriched.get_average_confidence)
    assert callable(enriched.get_node)


def test_get_patterns_for_context(mock_base_signal_pack):
    """Test context filtering of patterns with comprehensive stats."""
    enriched = EnrichedSignalPack(
        mock_base_signal_pack, enable_semantic_expansion=False
    )

    doc_context = {"section": "budget", "chapter": 1}
    filtered_patterns, stats = enriched.get_patterns_for_context(doc_context)

    # Should return a tuple with patterns and stats
    assert isinstance(filtered_patterns, list)
    assert isinstance(stats, dict)

    # Verify comprehensive stats are present
    assert "total_patterns" in stats
    assert "passed" in stats
    assert "filter_rate" in stats
    assert "precision_improvement" in stats
    assert "false_positive_reduction" in stats
    assert "performance_gain" in stats
    assert "integration_validated" in stats
    assert "estimated_final_precision" in stats

    # Verify stats are valid
    assert stats["total_patterns"] >= 0
    assert 0.0 <= stats["filter_rate"] <= 1.0
    assert 0.0 <= stats["precision_improvement"] <= 1.0
    assert 0.0 <= stats["false_positive_reduction"] <= 0.6
    assert stats["performance_gain"] >= 0.0
    assert isinstance(stats["integration_validated"], bool)


def test_expand_patterns(mock_base_signal_pack):
    """Test pattern expansion."""
    enriched = EnrichedSignalPack(mock_base_signal_pack, enable_semantic_expansion=True)

    base_patterns = ["presupuesto", "recursos"]
    expanded = enriched.expand_patterns(base_patterns)

    # Should return a list
    assert isinstance(expanded, list)


def test_get_average_confidence(mock_base_signal_pack):
    """Test average confidence calculation."""
    enriched = EnrichedSignalPack(
        mock_base_signal_pack, enable_semantic_expansion=False
    )

    # Test with known patterns
    patterns_used = ["PAT_001", "PAT_002"]
    avg_confidence = enriched.get_average_confidence(patterns_used)

    assert isinstance(avg_confidence, float)
    assert 0.0 <= avg_confidence <= 1.0
    # Expected: (0.85 + 0.75) / 2 = 0.80
    assert avg_confidence == pytest.approx(0.80, abs=0.01)


def test_get_average_confidence_empty_list(mock_base_signal_pack):
    """Test average confidence with empty patterns list."""
    enriched = EnrichedSignalPack(
        mock_base_signal_pack, enable_semantic_expansion=False
    )

    avg_confidence = enriched.get_average_confidence([])

    # Should return default 0.5
    assert avg_confidence == 0.5


def test_get_node(mock_base_signal_pack):
    """Test getting signal node by ID."""
    enriched = EnrichedSignalPack(
        mock_base_signal_pack, enable_semantic_expansion=False
    )

    node = enriched.get_node("Q001")

    # Should find the node
    assert node is not None
    assert isinstance(node, dict)
    assert node["id"] == "Q001"


def test_get_node_not_found(mock_base_signal_pack):
    """Test getting non-existent signal node."""
    enriched = EnrichedSignalPack(
        mock_base_signal_pack, enable_semantic_expansion=False
    )

    node = enriched.get_node("NONEXISTENT")

    # Should return None
    assert node is None


def test_extract_evidence_returns_result_object(mock_base_signal_pack):
    """Test that extract_evidence returns EvidenceExtractionResult."""
    enriched = EnrichedSignalPack(
        mock_base_signal_pack, enable_semantic_expansion=False
    )

    signal_node = {
        "id": "Q001",
        "expected_elements": [{"type": "budget_amount", "required": True}],
        "patterns": mock_base_signal_pack.patterns,
    }

    result = enriched.extract_evidence(
        text="El presupuesto asignado es COP 1,000,000",
        signal_node=signal_node,
        document_context={"section": "budget"},
    )

    # Should return EvidenceExtractionResult
    assert isinstance(result, EvidenceExtractionResult)
    assert hasattr(result, "evidence")
    assert hasattr(result, "completeness")
    assert hasattr(result, "missing_required")
    assert hasattr(result, "extraction_metadata")


def test_validate_result_returns_validation_result(mock_base_signal_pack):
    """Test that validate_result returns ValidationResult."""
    enriched = EnrichedSignalPack(
        mock_base_signal_pack, enable_semantic_expansion=False
    )

    analysis_result = {"amount": 1000000, "currency": "COP", "confidence": 0.85}

    signal_node = {
        "id": "Q001",
        "failure_contract": {
            "abort_if": ["missing_currency"],
            "emit_code": "ERR_TEST_001",
        },
    }

    validation = enriched.validate_result(analysis_result, signal_node)

    # Should return ValidationResult
    assert isinstance(validation, ValidationResult)
    assert hasattr(validation, "status")
    assert hasattr(validation, "passed")
    assert hasattr(validation, "error_code")
    assert hasattr(validation, "remediation")

    # This result should pass (currency is present)
    assert validation.passed is True


def test_create_enriched_signal_pack_factory(mock_base_signal_pack):
    """Test factory function for creating enriched signal pack."""
    enriched = create_enriched_signal_pack(
        mock_base_signal_pack, enable_semantic_expansion=False
    )

    assert isinstance(enriched, EnrichedSignalPack)
    assert enriched.base_pack == mock_base_signal_pack


def test_create_document_context():
    """Test document context creation helper."""
    ctx = create_document_context(
        section="budget", chapter=3, page=47, policy_area="PA01"
    )

    assert isinstance(ctx, dict)
    assert ctx["section"] == "budget"
    assert ctx["chapter"] == 3
    assert ctx["page"] == 47
    assert ctx["policy_area"] == "PA01"


def test_create_document_context_optional_fields():
    """Test document context with only some fields."""
    ctx = create_document_context(section="indicators", custom_field="custom_value")

    assert isinstance(ctx, dict)
    assert ctx["section"] == "indicators"
    assert "chapter" not in ctx
    assert ctx["custom_field"] == "custom_value"


def test_get_patterns_for_context_precision_improvement_measurable():
    """Test that 60% precision improvement is measurable from stats."""
    mock_pack = Mock(spec=["patterns"])
    mock_pack.patterns = [
        {
            "id": "PAT_BUDGET_001",
            "pattern": "presupuesto asignado",
            "confidence_weight": 0.85,
            "context_requirement": {"section": "budget"},
            "context_scope": "section",
        },
        {
            "id": "PAT_BUDGET_002",
            "pattern": "recursos financieros",
            "confidence_weight": 0.75,
            "context_requirement": {"section": "budget"},
            "context_scope": "section",
        },
        {
            "id": "PAT_INDICATOR_001",
            "pattern": "línea de base",
            "confidence_weight": 0.80,
            "context_requirement": {"section": "indicators"},
            "context_scope": "section",
        },
        {
            "id": "PAT_INDICATOR_002",
            "pattern": "meta establecida",
            "confidence_weight": 0.85,
            "context_requirement": {"section": "indicators"},
            "context_scope": "section",
        },
        {
            "id": "PAT_GLOBAL_001",
            "pattern": "política pública",
            "confidence_weight": 0.70,
            "context_scope": "global",
        },
    ]

    enriched = EnrichedSignalPack(mock_pack, enable_semantic_expansion=False)

    # Test with budget context
    budget_context = {"section": "budget", "chapter": 3}
    budget_patterns, budget_stats = enriched.get_patterns_for_context(budget_context)

    # Should filter to budget patterns + global patterns
    assert len(budget_patterns) == 3  # PAT_BUDGET_001, PAT_BUDGET_002, PAT_GLOBAL_001
    assert budget_stats["passed"] == 3
    assert budget_stats["context_filtered"] == 2  # 2 indicator patterns filtered

    # Precision improvement should be measurable
    assert budget_stats["false_positive_reduction"] > 0.0
    assert budget_stats["precision_improvement"] > 0.0
    assert budget_stats["integration_validated"] is True

    # With 40% of patterns filtered, expect ~40% false positive reduction
    expected_fp_reduction = 0.4 * 1.5  # filter_rate * 1.5
    assert budget_stats["false_positive_reduction"] == pytest.approx(
        expected_fp_reduction, abs=0.1
    )

    # Test with indicators context
    indicator_context = {"section": "indicators", "chapter": 5}
    indicator_patterns, indicator_stats = enriched.get_patterns_for_context(
        indicator_context
    )

    # Should filter to indicator patterns + global patterns
    assert (
        len(indicator_patterns) == 3
    )  # PAT_INDICATOR_001, PAT_INDICATOR_002, PAT_GLOBAL_001
    assert indicator_stats["passed"] == 3
    assert indicator_stats["context_filtered"] == 2  # 2 budget patterns filtered

    # Precision improvement should be consistent
    assert indicator_stats["false_positive_reduction"] > 0.0
    assert indicator_stats["integration_validated"] is True


def test_get_patterns_for_context_60_percent_target_validation():
    """Test that stats properly track toward 60% precision improvement target."""
    mock_pack = Mock(spec=["patterns"])

    # Create patterns where 60% have context requirements
    # This should lead to ~60% FP reduction in context-specific scenarios
    patterns = []
    for i in range(100):
        if i < 60:  # 60% have context requirements
            patterns.append(
                {
                    "id": f"PAT_SPECIFIC_{i}",
                    "pattern": f"pattern_{i}",
                    "confidence_weight": 0.75,
                    "context_requirement": {"section": "specific_section"},
                    "context_scope": "section",
                }
            )
        else:  # 40% are global
            patterns.append(
                {
                    "id": f"PAT_GLOBAL_{i}",
                    "pattern": f"global_pattern_{i}",
                    "confidence_weight": 0.70,
                    "context_scope": "global",
                }
            )

    mock_pack.patterns = patterns
    enriched = EnrichedSignalPack(mock_pack, enable_semantic_expansion=False)

    # Test with different context (should filter out the 60 specific patterns)
    other_context = {"section": "other_section", "chapter": 1}
    filtered_patterns, stats = enriched.get_patterns_for_context(other_context)

    # Should keep only global patterns (40)
    assert len(filtered_patterns) == 40
    assert stats["passed"] == 40
    assert stats["context_filtered"] == 60

    # With 60% filtered, false positive reduction should approach 60% target
    assert stats["filter_rate"] == pytest.approx(0.60, abs=0.01)

    # False positive reduction capped at 60% (0.6)
    # With 60% filter rate: min(0.6 * 1.5, 0.6) = 0.6
    assert stats["false_positive_reduction"] == pytest.approx(0.60, abs=0.01)

    # Precision improvement from baseline 40% with 60% FP reduction
    # improvement = 0.6 * 0.4 / (1 - 0.4) = 0.6 * 0.4 / 0.6 = 0.4
    expected_improvement = 0.60 * 0.40 / 0.60
    assert stats["precision_improvement"] == pytest.approx(
        expected_improvement, abs=0.05
    )

    # Final precision should be baseline + FP reduction = 0.4 + 0.6 = 1.0
    assert stats["estimated_final_precision"] == pytest.approx(1.0, abs=0.01)

    # Performance gain should be proportional to filter rate
    assert stats["performance_gain"] == pytest.approx(1.2, abs=0.1)  # 0.6 * 2.0

    assert stats["integration_validated"] is True


def test_get_patterns_for_context_no_filtering_scenario():
    """Test stats when no filtering occurs (all global patterns)."""
    mock_pack = Mock(spec=["patterns"])
    mock_pack.patterns = [
        {"id": "PAT_001", "pattern": "p1", "context_scope": "global"},
        {"id": "PAT_002", "pattern": "p2", "context_scope": "global"},
        {"id": "PAT_003", "pattern": "p3", "context_scope": "global"},
    ]

    enriched = EnrichedSignalPack(mock_pack, enable_semantic_expansion=False)

    context = {"section": "any_section"}
    patterns, stats = enriched.get_patterns_for_context(context)

    # All patterns should pass
    assert len(patterns) == 3
    assert stats["passed"] == 3
    assert stats["context_filtered"] == 0
    assert stats["scope_filtered"] == 0
    assert stats["filter_rate"] == 0.0

    # With no filtering, no precision improvement
    assert stats["false_positive_reduction"] == 0.0
    assert stats["precision_improvement"] == 0.0

    # Integration still validated (all patterns are global)
    assert stats["integration_validated"] is True


def test_get_patterns_for_context_without_tracking():
    """Test that precision tracking can be disabled."""
    mock_pack = Mock(spec=["patterns"])
    mock_pack.patterns = [
        {"id": "PAT_001", "pattern": "test", "context_scope": "global"}
    ]

    enriched = EnrichedSignalPack(mock_pack, enable_semantic_expansion=False)

    context = {"section": "test"}
    patterns, stats = enriched.get_patterns_for_context(
        context, track_precision_improvement=False
    )

    # Should return basic stats only
    assert "total_patterns" in stats
    assert "passed" in stats

    # Comprehensive stats should not be present
    assert "precision_improvement" not in stats
    assert "false_positive_reduction" not in stats
    assert "integration_validated" not in stats


def test_evidence_extraction_result_has_expected_fields():
    """Test that EvidenceExtractionResult has expected structure."""
    result = EvidenceExtractionResult(
        evidence={"budget": [{"value": 1000}]},
        completeness=0.85,
        missing_required=["currency"],
        under_minimum=[("sources", 1, 2)],
        extraction_metadata={"pattern_count": 10},
    )

    assert result.evidence == {"budget": [{"value": 1000}]}
    assert result.completeness == 0.85
    assert result.missing_required == ["currency"]
    assert result.under_minimum == [("sources", 1, 2)]
    assert result.extraction_metadata == {"pattern_count": 10}


def test_validation_result_has_expected_fields():
    """Test that ValidationResult has expected structure."""
    result = ValidationResult(
        status="failed",
        passed=False,
        error_code="ERR_TEST_001",
        condition_violated="missing_currency",
        validation_failures=["currency field missing"],
        remediation="Check source document for currency field",
        details={"amount": 1000},
    )

    assert result.status == "failed"
    assert result.passed is False
    assert result.error_code == "ERR_TEST_001"
    assert result.condition_violated == "missing_currency"
    assert result.validation_failures == ["currency field missing"]
    assert result.remediation == "Check source document for currency field"
    assert result.details == {"amount": 1000}


def test_precision_improvement_stats_dataclass():
    """Test PrecisionImprovementStats dataclass structure."""
    stats = PrecisionImprovementStats(
        total_patterns=100,
        passed=40,
        context_filtered=50,
        scope_filtered=10,
        filter_rate=0.60,
        baseline_precision=0.40,
        false_positive_reduction=0.60,
        precision_improvement=0.40,
        estimated_final_precision=1.0,
        performance_gain=1.2,
        integration_validated=True,
        patterns_per_context=20.0,
        context_specificity=0.40,
    )

    assert stats.total_patterns == 100
    assert stats.passed == 40
    assert stats.filter_rate == 0.60
    assert stats.false_positive_reduction == 0.60
    assert stats.meets_60_percent_target() is True

    # Test format_summary
    summary = stats.format_summary()
    assert isinstance(summary, str)
    assert "60% filtered" in summary
    assert "60% improvement" in summary or "40% improvement" in summary

    # Test to_dict
    stats_dict = stats.to_dict()
    assert isinstance(stats_dict, dict)
    assert stats_dict["total_patterns"] == 100
    assert stats_dict["false_positive_reduction"] == 0.60


def test_precision_improvement_stats_does_not_meet_target():
    """Test meets_60_percent_target returns False when appropriate."""
    stats = PrecisionImprovementStats(
        total_patterns=100,
        passed=80,
        context_filtered=15,
        scope_filtered=5,
        filter_rate=0.20,
        baseline_precision=0.40,
        false_positive_reduction=0.30,
        precision_improvement=0.20,
        estimated_final_precision=0.70,
        performance_gain=0.40,
        integration_validated=True,
        patterns_per_context=40.0,
        context_specificity=0.80,
    )

    assert stats.meets_60_percent_target() is False
    assert stats.false_positive_reduction < 0.55


def test_compute_precision_improvement_stats_with_60_percent_filtering():
    """Test compute_precision_improvement_stats with 60% filter rate."""
    base_stats = {
        "total_patterns": 100,
        "passed": 40,
        "context_filtered": 50,
        "scope_filtered": 10,
    }
    context = {"section": "budget", "chapter": 3}

    stats = compute_precision_improvement_stats(base_stats, context)

    assert stats.total_patterns == 100
    assert stats.passed == 40
    assert stats.context_filtered == 50
    assert stats.scope_filtered == 10
    assert stats.filter_rate == pytest.approx(0.60, abs=0.01)

    # With 60% filter rate, FP reduction should be capped at 60%
    assert stats.false_positive_reduction == pytest.approx(0.60, abs=0.01)

    # Precision improvement: 0.6 * 0.4 / 0.6 = 0.4
    assert stats.precision_improvement == pytest.approx(0.40, abs=0.05)

    # Final precision: 0.4 + 0.6 = 1.0
    assert stats.estimated_final_precision == pytest.approx(1.0, abs=0.01)

    # Performance gain: 0.6 * 2.0 = 1.2
    assert stats.performance_gain == pytest.approx(1.2, abs=0.1)

    assert stats.integration_validated is True
    assert stats.meets_60_percent_target() is True


def test_compute_precision_improvement_stats_with_partial_filtering():
    """Test compute_precision_improvement_stats with partial filtering."""
    base_stats = {
        "total_patterns": 100,
        "passed": 70,
        "context_filtered": 25,
        "scope_filtered": 5,
    }
    context = {"section": "indicators"}

    stats = compute_precision_improvement_stats(base_stats, context)

    assert stats.filter_rate == pytest.approx(0.30, abs=0.01)

    # With 30% filter rate: min(0.3 * 1.5, 0.6) = 0.45
    assert stats.false_positive_reduction == pytest.approx(0.45, abs=0.01)

    # Should not meet 60% target
    assert stats.meets_60_percent_target() is False

    # But should show some improvement
    assert stats.precision_improvement > 0.0
    assert stats.estimated_final_precision > stats.baseline_precision

    assert stats.integration_validated is True


def test_compute_precision_improvement_stats_no_filtering():
    """Test compute_precision_improvement_stats when no filtering occurs."""
    base_stats = {
        "total_patterns": 50,
        "passed": 50,
        "context_filtered": 0,
        "scope_filtered": 0,
    }
    context = {"section": "any"}

    stats = compute_precision_improvement_stats(base_stats, context)

    assert stats.filter_rate == 0.0
    assert stats.false_positive_reduction == 0.0
    assert stats.precision_improvement == 0.0
    assert stats.estimated_final_precision == stats.baseline_precision
    assert stats.performance_gain == 0.0

    # Should still validate (all patterns passed)
    assert stats.integration_validated is True

    assert stats.meets_60_percent_target() is False


def test_compute_precision_improvement_stats_empty_patterns():
    """Test compute_precision_improvement_stats with zero patterns."""
    base_stats = {
        "total_patterns": 0,
        "passed": 0,
        "context_filtered": 0,
        "scope_filtered": 0,
    }
    context = {}

    stats = compute_precision_improvement_stats(base_stats, context)

    assert stats.filter_rate == 0.0
    assert stats.false_positive_reduction == 0.0
    assert stats.integration_validated is False


def test_compute_precision_improvement_stats_algorithm_correctness():
    """Test the algorithm correctness for various filter rates."""
    test_cases = [
        # (filter_rate, expected_fp_reduction_cap)
        (0.10, 0.15),  # 10% filtered → 15% FP reduction (0.1 * 1.5)
        (0.25, 0.375),  # 25% filtered → 37.5% FP reduction (0.25 * 1.5)
        (0.40, 0.60),  # 40% filtered → 60% FP reduction (capped)
        (0.50, 0.60),  # 50% filtered → 60% FP reduction (capped)
        (0.60, 0.60),  # 60% filtered → 60% FP reduction (capped)
        (0.80, 0.60),  # 80% filtered → 60% FP reduction (capped)
    ]

    for filter_rate, expected_fp_reduction in test_cases:
        filtered_count = int(100 * filter_rate)
        passed_count = 100 - filtered_count

        base_stats = {
            "total_patterns": 100,
            "passed": passed_count,
            "context_filtered": filtered_count,
            "scope_filtered": 0,
        }
        context = {"section": "test"}

        stats = compute_precision_improvement_stats(base_stats, context)

        assert stats.filter_rate == pytest.approx(filter_rate, abs=0.01)
        assert stats.false_positive_reduction == pytest.approx(
            expected_fp_reduction, abs=0.01
        )

        # Performance gain should scale linearly with filter rate
        expected_performance_gain = filter_rate * 2.0
        assert stats.performance_gain == pytest.approx(
            expected_performance_gain, abs=0.01
        )


def test_generate_precision_improvement_report_empty():
    """Test report generation with no measurements."""
    report = generate_precision_improvement_report([])

    assert report["total_measurements"] == 0
    assert report["validated_count"] == 0
    assert "No measurements" in report["summary"]


def test_generate_precision_improvement_report_single_measurement():
    """Test report generation with single measurement."""
    measurements = [
        {
            "filter_rate": 0.60,
            "false_positive_reduction": 0.60,
            "precision_improvement": 0.40,
            "estimated_final_precision": 1.0,
            "integration_validated": True,
        }
    ]

    report = generate_precision_improvement_report(measurements)

    assert report["total_measurements"] == 1
    assert report["validated_count"] == 1
    assert report["validation_rate"] == 1.0
    assert report["avg_filter_rate"] == 0.60
    assert report["avg_false_positive_reduction"] == 0.60
    assert report["max_false_positive_reduction"] == 0.60
    assert report["meets_target_count"] == 1
    assert report["target_achievement_rate"] == 1.0
    assert "TARGET MET" in report["summary"]


def test_generate_precision_improvement_report_multiple_measurements():
    """Test report generation with multiple measurements."""
    measurements = [
        {
            "filter_rate": 0.60,
            "false_positive_reduction": 0.60,
            "precision_improvement": 0.40,
            "estimated_final_precision": 1.0,
            "integration_validated": True,
        },
        {
            "filter_rate": 0.40,
            "false_positive_reduction": 0.60,
            "precision_improvement": 0.40,
            "estimated_final_precision": 1.0,
            "integration_validated": True,
        },
        {
            "filter_rate": 0.20,
            "false_positive_reduction": 0.30,
            "precision_improvement": 0.20,
            "estimated_final_precision": 0.70,
            "integration_validated": True,
        },
        {
            "filter_rate": 0.0,
            "false_positive_reduction": 0.0,
            "precision_improvement": 0.0,
            "estimated_final_precision": 0.40,
            "integration_validated": True,
        },
    ]

    report = generate_precision_improvement_report(measurements)

    assert report["total_measurements"] == 4
    assert report["validated_count"] == 4
    assert report["validation_rate"] == 1.0

    # Average filter rate: (0.6 + 0.4 + 0.2 + 0.0) / 4 = 0.3
    assert report["avg_filter_rate"] == pytest.approx(0.30, abs=0.01)

    # Average FP reduction: (0.6 + 0.6 + 0.3 + 0.0) / 4 = 0.375
    assert report["avg_false_positive_reduction"] == pytest.approx(0.375, abs=0.01)

    # Max FP reduction: 0.6
    assert report["max_false_positive_reduction"] == 0.60

    # Meets target (>= 0.55): 2 out of 4
    assert report["meets_target_count"] == 2
    assert report["target_achievement_rate"] == 0.5

    # Should show TARGET MET since max >= 0.55
    assert "TARGET MET" in report["summary"]

    # Check summary format
    assert "n=4" in report["summary"]
    assert "4/4 (100%)" in report["summary"] or "100%" in report["summary"]


def test_generate_precision_improvement_report_below_target():
    """Test report when no measurements meet 60% target."""
    measurements = [
        {
            "filter_rate": 0.10,
            "false_positive_reduction": 0.15,
            "precision_improvement": 0.10,
            "estimated_final_precision": 0.55,
            "integration_validated": True,
        },
        {
            "filter_rate": 0.20,
            "false_positive_reduction": 0.30,
            "precision_improvement": 0.20,
            "estimated_final_precision": 0.70,
            "integration_validated": True,
        },
    ]

    report = generate_precision_improvement_report(measurements)

    assert report["meets_target_count"] == 0
    assert report["target_achievement_rate"] == 0.0
    assert report["max_false_positive_reduction"] < 0.55
    assert "BELOW TARGET" in report["summary"]


def test_generate_precision_improvement_report_with_integration_failures():
    """Test report with some integration validation failures."""
    measurements = [
        {
            "filter_rate": 0.60,
            "false_positive_reduction": 0.60,
            "precision_improvement": 0.40,
            "estimated_final_precision": 1.0,
            "integration_validated": True,
        },
        {
            "filter_rate": 0.0,
            "false_positive_reduction": 0.0,
            "precision_improvement": 0.0,
            "estimated_final_precision": 0.40,
            "integration_validated": False,  # Integration failed
        },
    ]

    report = generate_precision_improvement_report(measurements)

    assert report["total_measurements"] == 2
    assert report["validated_count"] == 1
    assert report["validation_rate"] == 0.5


class TestEnhancedGetPatternsForContext:
    """Test enhanced get_patterns_for_context() with comprehensive stats tracking."""

    def test_enhanced_stats_tracking(self, mock_base_signal_pack):
        """Test that enhanced stats tracking includes all new fields."""
        enriched = EnrichedSignalPack(
            mock_base_signal_pack, enable_semantic_expansion=False
        )

        context = {"section": "budget", "chapter": 3}
        patterns, stats = enriched.get_patterns_for_context(context)

        assert "pre_filter_count" in stats
        assert "post_filter_count" in stats
        assert "filtering_duration_ms" in stats
        assert "context_complexity" in stats
        assert "pattern_distribution" in stats
        assert "meets_60_percent_target" in stats
        assert "timestamp" in stats
        assert "filtering_validation" in stats
        assert "performance_metrics" in stats
        assert "target_achievement" in stats

        validation = stats["filtering_validation"]
        assert "pre_count_matches_total" in validation
        assert "post_count_matches_passed" in validation
        assert "no_patterns_gained" in validation
        assert "filter_sum_correct" in validation
        assert "validation_passed" in validation

    def test_filtering_duration_tracked(self, mock_base_signal_pack):
        """Test that filtering duration is tracked."""
        enriched = EnrichedSignalPack(
            mock_base_signal_pack, enable_semantic_expansion=False
        )

        _, stats = enriched.get_patterns_for_context({})

        assert "filtering_duration_ms" in stats
        assert stats["filtering_duration_ms"] >= 0
        assert isinstance(stats["filtering_duration_ms"], (int, float))

    def test_context_complexity_computation(self, mock_base_signal_pack):
        """Test context complexity score computation."""
        enriched = EnrichedSignalPack(
            mock_base_signal_pack, enable_semantic_expansion=False
        )

        empty_context = {}
        _, stats_empty = enriched.get_patterns_for_context(empty_context)
        assert stats_empty["context_complexity"] == 0.0

        simple_context = {"section": "budget"}
        _, stats_simple = enriched.get_patterns_for_context(simple_context)
        assert 0.0 < stats_simple["context_complexity"] < 1.0

        complex_context = {
            "section": "budget",
            "chapter": 3,
            "page": 47,
            "policy_area": "PA05",
        }
        _, stats_complex = enriched.get_patterns_for_context(complex_context)
        assert stats_complex["context_complexity"] > stats_simple["context_complexity"]

    def test_pattern_distribution_tracking(self, mock_base_signal_pack):
        """Test pattern distribution by scope tracking."""
        enriched = EnrichedSignalPack(
            mock_base_signal_pack, enable_semantic_expansion=False
        )

        _, stats = enriched.get_patterns_for_context({})

        distribution = stats["pattern_distribution"]
        assert "global_scope" in distribution
        assert "section_scope" in distribution
        assert "chapter_scope" in distribution
        assert "page_scope" in distribution
        assert "with_context_requirement" in distribution
        assert "without_context_requirement" in distribution

        total_patterns = (
            distribution["global_scope"]
            + distribution["section_scope"]
            + distribution["chapter_scope"]
            + distribution["page_scope"]
            + distribution["other_scope"]
        )
        assert total_patterns == len(enriched.patterns)

    def test_performance_metrics_tracked(self, mock_base_signal_pack):
        """Test performance metrics are tracked."""
        enriched = EnrichedSignalPack(
            mock_base_signal_pack, enable_semantic_expansion=False
        )

        _, stats = enriched.get_patterns_for_context({})

        perf = stats["performance_metrics"]
        assert "throughput_patterns_per_ms" in perf
        assert "avg_time_per_pattern_us" in perf
        assert "efficiency_score" in perf
        assert all(isinstance(v, (int, float)) for v in perf.values())

    def test_target_achievement_tracking(self, mock_base_signal_pack):
        """Test 60% target achievement tracking."""
        enriched = EnrichedSignalPack(
            mock_base_signal_pack, enable_semantic_expansion=False
        )

        _, stats = enriched.get_patterns_for_context({})

        target_ach = stats["target_achievement"]
        assert "meets_target" in target_ach
        assert "target_threshold" in target_ach
        assert "actual_fp_reduction" in target_ach
        assert "gap_to_target" in target_ach
        assert "target_percentage" in target_ach
        assert "achievement_percentage" in target_ach

        assert target_ach["target_percentage"] == 60.0
        assert 0.0 <= target_ach["achievement_percentage"] <= 100.0
        assert target_ach["gap_to_target"] >= 0.0

    def test_validation_checks_comprehensive(self, mock_base_signal_pack):
        """Test all validation checks are performed."""
        enriched = EnrichedSignalPack(
            mock_base_signal_pack, enable_semantic_expansion=False
        )

        _, stats = enriched.get_patterns_for_context({})

        validation = stats["filtering_validation"]
        assert validation["validation_passed"] is True
        assert validation["pre_count_matches_total"] is True
        assert validation["post_count_matches_passed"] is True
        assert validation["no_patterns_gained"] is True
        assert validation["filter_sum_correct"] is True


class TestEnhancedPrecisionReport:
    """Test enhanced generate_precision_improvement_report()."""

    def test_detailed_breakdown_included(self):
        """Test detailed breakdown is included when enabled."""
        measurements = [
            {
                "total_patterns": 100,
                "passed": 40,
                "filter_rate": 0.60,
                "false_positive_reduction": 0.60,
                "meets_60_percent_target": True,
                "integration_validated": True,
                "filtering_duration_ms": 5.0,
                "context_complexity": 0.7,
                "filtering_validation": {"validation_passed": True},
                "performance_metrics": {
                    "throughput_patterns_per_ms": 20.0,
                    "avg_time_per_pattern_us": 50.0,
                    "efficiency_score": 12.0,
                },
            },
            {
                "total_patterns": 100,
                "passed": 70,
                "filter_rate": 0.30,
                "false_positive_reduction": 0.45,
                "meets_60_percent_target": False,
                "integration_validated": True,
                "filtering_duration_ms": 3.0,
                "context_complexity": 0.4,
                "filtering_validation": {"validation_passed": True},
                "performance_metrics": {
                    "throughput_patterns_per_ms": 33.0,
                    "avg_time_per_pattern_us": 30.0,
                    "efficiency_score": 10.0,
                },
            },
        ]

        report = generate_precision_improvement_report(
            measurements, include_detailed_breakdown=True
        )

        assert "detailed_breakdown" in report
        assert len(report["detailed_breakdown"]) == 2
        assert "top_performers" in report
        assert len(report["top_performers"]) <= 5

        breakdown = report["detailed_breakdown"][0]
        assert "measurement_index" in breakdown
        assert "total_patterns" in breakdown
        assert "passed" in breakdown
        assert "filter_rate" in breakdown
        assert "meets_target" in breakdown
        assert "validation_passed" in breakdown

    def test_median_fp_reduction_tracked(self):
        """Test median false positive reduction is tracked."""
        measurements = [
            {
                "false_positive_reduction": 0.30,
                "filter_rate": 0.0,
                "total_patterns": 0,
                "passed": 0,
            },
            {
                "false_positive_reduction": 0.45,
                "filter_rate": 0.0,
                "total_patterns": 0,
                "passed": 0,
            },
            {
                "false_positive_reduction": 0.60,
                "filter_rate": 0.0,
                "total_patterns": 0,
                "passed": 0,
            },
            {
                "false_positive_reduction": 0.75,
                "filter_rate": 0.0,
                "total_patterns": 0,
                "passed": 0,
            },
            {
                "false_positive_reduction": 0.90,
                "filter_rate": 0.0,
                "total_patterns": 0,
                "passed": 0,
            },
        ]

        report = generate_precision_improvement_report(measurements)

        assert "median_false_positive_reduction" in report
        assert report["median_false_positive_reduction"] == 0.60

    def test_performance_summary_comprehensive(self):
        """Test performance summary includes all metrics."""
        measurements = [
            {
                "total_patterns": 100,
                "passed": 60,
                "filter_rate": 0.40,
                "false_positive_reduction": 0.50,
                "filtering_duration_ms": 10.0,
                "performance_metrics": {
                    "throughput_patterns_per_ms": 10.0,
                    "avg_time_per_pattern_us": 100.0,
                    "efficiency_score": 4.0,
                },
            }
        ]

        report = generate_precision_improvement_report(measurements)

        perf = report["performance_summary"]
        assert "total_patterns_processed" in perf
        assert "total_patterns_passed" in perf
        assert "total_patterns_filtered" in perf
        assert "overall_filter_rate" in perf
        assert "avg_filtering_duration_ms" in perf
        assert "total_filtering_time_ms" in perf
        assert "avg_patterns_per_measurement" in perf

    def test_validation_health_tracking(self):
        """Test validation health is tracked."""
        measurements = [
            {
                "total_patterns": 100,
                "passed": 40,
                "filter_rate": 0.60,
                "false_positive_reduction": 0.60,
                "integration_validated": True,
                "filtering_validation": {"validation_passed": True},
            },
            {
                "total_patterns": 100,
                "passed": 40,
                "filter_rate": 0.60,
                "false_positive_reduction": 0.60,
                "integration_validated": False,
                "filtering_validation": {"validation_passed": False},
            },
        ]

        report = generate_precision_improvement_report(measurements)

        health = report["validation_health"]
        assert "validation_failures" in health
        assert "validation_success_rate" in health
        assert "integration_success_rate" in health
        assert "target_achievement_rate" in health
        assert "overall_health" in health
        assert "health_score" in health

        assert health["validation_failures"] == 1
        assert health["overall_health"] in ["HEALTHY", "DEGRADED", "UNHEALTHY"]
        assert 0.0 <= health["health_score"] <= 1.0

    def test_context_analysis_tracking(self):
        """Test context complexity analysis."""
        measurements = [
            {
                "context_complexity": 0.1,
                "filter_rate": 0.0,
                "false_positive_reduction": 0.0,
                "total_patterns": 0,
                "passed": 0,
            },
            {
                "context_complexity": 0.5,
                "filter_rate": 0.0,
                "false_positive_reduction": 0.0,
                "total_patterns": 0,
                "passed": 0,
            },
            {
                "context_complexity": 0.9,
                "filter_rate": 0.0,
                "false_positive_reduction": 0.0,
                "total_patterns": 0,
                "passed": 0,
            },
        ]

        report = generate_precision_improvement_report(measurements)

        ctx_analysis = report["context_analysis"]
        assert "avg_context_complexity" in ctx_analysis
        assert "max_context_complexity" in ctx_analysis
        assert "min_context_complexity" in ctx_analysis
        assert "contexts_with_high_complexity" in ctx_analysis
        assert "contexts_with_low_complexity" in ctx_analysis

        assert ctx_analysis["max_context_complexity"] == 0.9
        assert ctx_analysis["min_context_complexity"] == 0.1
        assert ctx_analysis["contexts_with_high_complexity"] == 1
        assert ctx_analysis["contexts_with_low_complexity"] == 1

    def test_top_performers_ranked(self):
        """Test top performers are correctly ranked."""
        measurements = []
        for i in range(10):
            measurements.append(
                {
                    "total_patterns": 100,
                    "passed": 50,
                    "filter_rate": 0.50,
                    "false_positive_reduction": i * 0.1,
                    "meets_60_percent_target": i >= 6,
                    "integration_validated": True,
                    "filtering_duration_ms": 5.0,
                    "context_complexity": 0.5,
                    "filtering_validation": {"validation_passed": True},
                }
            )

        report = generate_precision_improvement_report(
            measurements, include_detailed_breakdown=True
        )

        top_performers = report["top_performers"]
        assert len(top_performers) == 5
        assert top_performers[0]["false_positive_reduction"] == 0.9
        assert top_performers[-1]["false_positive_reduction"] == 0.5


class TestValidate60PercentTarget:
    """Test validate_60_percent_target_achievement() function."""

    def test_comprehensive_validation(self, mock_base_signal_pack):
        """Test comprehensive 60% target validation."""
        enriched = EnrichedSignalPack(
            mock_base_signal_pack, enable_semantic_expansion=False
        )

        validation = validate_60_percent_target_achievement(enriched)

        assert "overall_status" in validation
        assert "integration_validated" in validation
        assert "target_achievable" in validation
        assert "target_achievement_details" in validation
        assert "measurement_count" in validation
        assert "validation_checks" in validation
        assert "recommendations" in validation
        assert "test_timestamp" in validation

        assert validation["overall_status"] in ["PASS", "FAIL"]
        assert isinstance(validation["integration_validated"], bool)
        assert isinstance(validation["target_achievable"], bool)

    def test_validation_checks_comprehensive(self, mock_base_signal_pack):
        """Test all validation checks are performed."""
        enriched = EnrichedSignalPack(
            mock_base_signal_pack, enable_semantic_expansion=False
        )

        validation = validate_60_percent_target_achievement(enriched)

        checks = validation["validation_checks"]
        assert "integration_working" in checks
        assert "max_fp_reduction_meets_target" in checks
        assert "majority_meet_target" in checks
        assert "no_validation_failures" in checks
        assert "validation_health_ok" in checks
        assert "performance_acceptable" in checks
        assert "stats_comprehensive" in checks

        assert all(isinstance(v, bool) for v in checks.values())

    def test_recommendations_provided(self, mock_base_signal_pack):
        """Test recommendations are provided when target not met."""
        enriched = EnrichedSignalPack(
            mock_base_signal_pack, enable_semantic_expansion=False
        )

        validation = validate_60_percent_target_achievement(enriched)

        assert "recommendations" in validation
        assert isinstance(validation["recommendations"], list)

    def test_custom_contexts_support(self, mock_base_signal_pack):
        """Test validation with custom test contexts."""
        enriched = EnrichedSignalPack(
            mock_base_signal_pack, enable_semantic_expansion=False
        )

        custom_contexts = [
            {"section": "budget"},
            {"section": "indicators"},
        ]

        validation = validate_60_percent_target_achievement(
            enriched, test_contexts=custom_contexts
        )

        assert validation["measurement_count"] == 2

    def test_strict_mode(self, mock_base_signal_pack):
        """Test strict mode requiring all contexts to pass."""
        enriched = EnrichedSignalPack(
            mock_base_signal_pack, enable_semantic_expansion=False
        )

        validation = validate_60_percent_target_achievement(
            enriched, require_all_pass=True
        )

        assert "target_achievable" in validation


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

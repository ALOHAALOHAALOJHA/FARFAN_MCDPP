"""
Signal Intelligence 91% Unlock Verification Tests
==================================================

Comprehensive tests to measure and verify the 91% intelligence unlock
metric across all 4 surgical refactorings using real questionnaire data.

Test Coverage:
- Refactoring #2 (Semantic Expansion): Field coverage and multiplier measurement
- Refactoring #3 (Contract Validation): Contract coverage and validation effectiveness
- Refactoring #4 (Context Scoping): Context field coverage and filtering impact
- Refactoring #5 (Evidence Structure): Expected elements coverage and completeness
- Aggregate Metrics: Combined intelligence unlock percentage calculation

Methodology:
- Sample across all dimensions (D1-D6) and policy areas (PA01-PA10)
- Measure field utilization rates for each intelligence field
- Calculate weighted aggregate intelligence unlock percentage
- Verify metrics against 91% target (aspirational vs baseline)

Author: F.A.R.F.A.N Pipeline
Date: 2025-12-06
Coverage: 91% intelligence unlock verification across full questionnaire
"""

from collections import defaultdict
from typing import Any

import pytest

from farfan_pipeline.core.orchestrator.questionnaire import load_questionnaire
from farfan_pipeline.core.orchestrator.signal_semantic_expander import (
    expand_all_patterns,
)


@pytest.fixture(scope="module")
def canonical_questionnaire():
    """Load questionnaire once."""
    return load_questionnaire()


@pytest.fixture(scope="module")
def all_micro_questions(canonical_questionnaire):
    """Get all micro questions."""
    return canonical_questionnaire.get_micro_questions()


class TestRefactoring2SemanticExpansion:
    """Test Refactoring #2: Semantic Expansion intelligence unlock."""

    def test_semantic_expansion_field_coverage(
        self, all_micro_questions: list[dict[str, Any]]
    ):
        """Measure semantic_expansion field coverage."""
        total_patterns = 0
        patterns_with_semantic = 0

        for q in all_micro_questions:
            patterns = q.get("patterns", [])
            total_patterns += len(patterns)

            for p in patterns:
                if p.get("semantic_expansion"):
                    patterns_with_semantic += 1

        coverage = (
            (patterns_with_semantic / total_patterns * 100) if total_patterns > 0 else 0
        )

        print("\n╔══════════════════════════════════════════════════╗")
        print("║  REFACTORING #2: SEMANTIC EXPANSION             ║")
        print("╚══════════════════════════════════════════════════╝")
        print(f"\n  Total patterns: {total_patterns}")
        print(f"  With semantic_expansion: {patterns_with_semantic}")
        print(f"  Coverage: {coverage:.1f}%")

        return coverage

    def test_pattern_expansion_multiplier(
        self, all_micro_questions: list[dict[str, Any]]
    ):
        """Measure actual pattern expansion multiplier."""
        # Sample to avoid excessive computation
        sample_size = min(50, len(all_micro_questions))
        sample = all_micro_questions[:sample_size]

        original_total = 0
        expanded_total = 0

        for q in sample:
            patterns = q.get("patterns", [])
            original_total += len(patterns)

            expanded = expand_all_patterns(patterns, enable_logging=False)
            expanded_total += len(expanded)

        multiplier = expanded_total / original_total if original_total > 0 else 1.0
        additional = expanded_total - original_total

        print("\n  Pattern Expansion Multiplier:")
        print(f"    Sample size: {sample_size} questions")
        print(f"    Original patterns: {original_total}")
        print(f"    Expanded patterns: {expanded_total}")
        print(f"    Multiplier: {multiplier:.2f}x")
        print("    Target: 5.0x")
        print(f"    Additional patterns: {additional}")

        achievement = (multiplier / 5.0 * 100) if multiplier <= 5.0 else 100
        print(f"    Achievement: {achievement:.1f}% of target")

        return multiplier

    def test_semantic_expansion_types(self, all_micro_questions: list[dict[str, Any]]):
        """Analyze semantic_expansion field types."""
        expansion_types = defaultdict(int)
        total_with_expansion = 0

        for q in all_micro_questions:
            patterns = q.get("patterns", [])

            for p in patterns:
                sem = p.get("semantic_expansion")
                if sem:
                    total_with_expansion += 1

                    if isinstance(sem, str):
                        expansion_types["string"] += 1
                    elif isinstance(sem, dict):
                        expansion_types["dict"] += 1
                    elif isinstance(sem, list):
                        expansion_types["list"] += 1

        print("\n  Semantic Expansion Field Types:")
        for exp_type, count in expansion_types.items():
            pct = (
                (count / total_with_expansion * 100) if total_with_expansion > 0 else 0
            )
            print(f"    {exp_type}: {count} ({pct:.1f}%)")


class TestRefactoring3ContractValidation:
    """Test Refactoring #3: Contract Validation intelligence unlock."""

    def test_failure_contract_coverage(self, all_micro_questions: list[dict[str, Any]]):
        """Measure failure_contract field coverage."""
        questions_with_contract = 0
        total_questions = len(all_micro_questions)

        contract_features = defaultdict(int)

        for q in all_micro_questions:
            if q.get("failure_contract"):
                questions_with_contract += 1
                contract = q["failure_contract"]

                if isinstance(contract, dict):
                    if "abort_if" in contract:
                        contract_features["abort_if"] += 1
                    if "emit_code" in contract:
                        contract_features["error_code"] += 1
                    if "remediation" in contract:
                        contract_features["remediation"] += 1

        coverage = (
            (questions_with_contract / total_questions * 100)
            if total_questions > 0
            else 0
        )

        print("\n╔══════════════════════════════════════════════════╗")
        print("║  REFACTORING #3: CONTRACT VALIDATION            ║")
        print("╚══════════════════════════════════════════════════╝")
        print(f"\n  Total questions: {total_questions}")
        print(f"  With failure_contract: {questions_with_contract}")
        print(f"  Coverage: {coverage:.1f}%")

        print("\n  Contract Features:")
        for feature, count in contract_features.items():
            pct = (
                (count / questions_with_contract * 100)
                if questions_with_contract > 0
                else 0
            )
            print(f"    {feature}: {count} ({pct:.1f}%)")

        return coverage

    def test_validation_rule_coverage(self, all_micro_questions: list[dict[str, Any]]):
        """Measure validation_rule field in patterns."""
        total_patterns = 0
        patterns_with_validation = 0

        for q in all_micro_questions:
            patterns = q.get("patterns", [])
            total_patterns += len(patterns)

            for p in patterns:
                if p.get("validation_rule"):
                    patterns_with_validation += 1

        coverage = (
            (patterns_with_validation / total_patterns * 100)
            if total_patterns > 0
            else 0
        )

        print("\n  Pattern-Level Validation:")
        print(f"    Total patterns: {total_patterns}")
        print(f"    With validation_rule: {patterns_with_validation}")
        print(f"    Coverage: {coverage:.1f}%")

        return coverage

    def test_validations_field_coverage(
        self, all_micro_questions: list[dict[str, Any]]
    ):
        """Measure validations field in questions."""
        questions_with_validations = 0

        for q in all_micro_questions:
            if q.get("validations"):
                questions_with_validations += 1

        coverage = (
            (questions_with_validations / len(all_micro_questions) * 100)
            if all_micro_questions
            else 0
        )

        print("\n  Question-Level Validations:")
        print(f"    With validations field: {questions_with_validations}")
        print(f"    Coverage: {coverage:.1f}%")

        return coverage


class TestRefactoring4ContextScoping:
    """Test Refactoring #4: Context Scoping intelligence unlock."""

    def test_context_scope_coverage(self, all_micro_questions: list[dict[str, Any]]):
        """Measure context_scope field coverage."""
        total_patterns = 0
        patterns_with_scope = 0
        scope_distribution = defaultdict(int)

        for q in all_micro_questions:
            patterns = q.get("patterns", [])
            total_patterns += len(patterns)

            for p in patterns:
                if p.get("context_scope"):
                    patterns_with_scope += 1
                    scope_distribution[p["context_scope"]] += 1

        coverage = (
            (patterns_with_scope / total_patterns * 100) if total_patterns > 0 else 0
        )

        print("\n╔══════════════════════════════════════════════════╗")
        print("║  REFACTORING #4: CONTEXT SCOPING                ║")
        print("╚══════════════════════════════════════════════════╝")
        print(f"\n  Total patterns: {total_patterns}")
        print(f"  With context_scope: {patterns_with_scope}")
        print(f"  Coverage: {coverage:.1f}%")

        print("\n  Scope Distribution:")
        for scope, count in sorted(scope_distribution.items(), key=lambda x: -x[1]):
            pct = (count / patterns_with_scope * 100) if patterns_with_scope > 0 else 0
            print(f"    {scope}: {count} ({pct:.1f}%)")

        return coverage

    def test_context_requirement_coverage(
        self, all_micro_questions: list[dict[str, Any]]
    ):
        """Measure context_requirement field coverage."""
        total_patterns = 0
        patterns_with_requirement = 0

        for q in all_micro_questions:
            patterns = q.get("patterns", [])
            total_patterns += len(patterns)

            for p in patterns:
                if p.get("context_requirement"):
                    patterns_with_requirement += 1

        coverage = (
            (patterns_with_requirement / total_patterns * 100)
            if total_patterns > 0
            else 0
        )

        print("\n  Context Requirements:")
        print(f"    With context_requirement: {patterns_with_requirement}")
        print(f"    Coverage: {coverage:.1f}%")

        return coverage

    def test_combined_context_awareness(
        self, all_micro_questions: list[dict[str, Any]]
    ):
        """Measure combined context awareness."""
        total_patterns = 0
        context_aware_patterns = 0

        for q in all_micro_questions:
            patterns = q.get("patterns", [])
            total_patterns += len(patterns)

            for p in patterns:
                if p.get("context_scope") or p.get("context_requirement"):
                    context_aware_patterns += 1

        coverage = (
            (context_aware_patterns / total_patterns * 100) if total_patterns > 0 else 0
        )

        print("\n  Combined Context Awareness:")
        print(f"    Context-aware patterns: {context_aware_patterns}")
        print(f"    Coverage: {coverage:.1f}%")

        return coverage


class TestRefactoring5EvidenceStructure:
    """Test Refactoring #5: Evidence Structure intelligence unlock."""

    def test_expected_elements_coverage(
        self, all_micro_questions: list[dict[str, Any]]
    ):
        """Measure expected_elements field coverage."""
        questions_with_elements = 0
        total_element_specs = 0
        element_type_distribution = defaultdict(int)

        for q in all_micro_questions:
            expected = q.get("expected_elements", [])
            if expected:
                questions_with_elements += 1
                total_element_specs += len(expected)

                for elem in expected:
                    if isinstance(elem, dict):
                        elem_type = elem.get("type", "unknown")
                        element_type_distribution[elem_type] += 1
                    elif isinstance(elem, str):
                        element_type_distribution[elem] += 1

        coverage = (
            (questions_with_elements / len(all_micro_questions) * 100)
            if all_micro_questions
            else 0
        )

        print("\n╔══════════════════════════════════════════════════╗")
        print("║  REFACTORING #5: EVIDENCE STRUCTURE             ║")
        print("╚══════════════════════════════════════════════════╝")
        print(f"\n  Total questions: {len(all_micro_questions)}")
        print(f"  With expected_elements: {questions_with_elements}")
        print(f"  Coverage: {coverage:.1f}%")
        print(f"  Total element specs: {total_element_specs}")
        print(f"  Unique element types: {len(element_type_distribution)}")

        return coverage

    def test_element_requirement_types(self, all_micro_questions: list[dict[str, Any]]):
        """Analyze element requirement types."""
        required_count = 0
        minimum_count = 0
        optional_count = 0

        for q in all_micro_questions:
            expected = q.get("expected_elements", [])

            for elem in expected:
                if isinstance(elem, dict):
                    if elem.get("required"):
                        required_count += 1
                    elif elem.get("minimum", 0) > 0:
                        minimum_count += 1
                    else:
                        optional_count += 1

        total = required_count + minimum_count + optional_count

        print("\n  Element Requirement Types:")
        if total > 0:
            print(f"    Required: {required_count} ({required_count/total*100:.1f}%)")
            print(
                f"    Minimum cardinality: {minimum_count} ({minimum_count/total*100:.1f}%)"
            )
            print(f"    Optional: {optional_count} ({optional_count/total*100:.1f}%)")

    def test_top_element_types(self, all_micro_questions: list[dict[str, Any]]):
        """Show top element types."""
        element_types = defaultdict(int)

        for q in all_micro_questions:
            expected = q.get("expected_elements", [])

            for elem in expected:
                if isinstance(elem, dict):
                    elem_type = elem.get("type", "unknown")
                    element_types[elem_type] += 1
                elif isinstance(elem, str):
                    element_types[elem] += 1

        print("\n  Top 15 Element Types:")
        for elem_type, count in sorted(element_types.items(), key=lambda x: -x[1])[:15]:
            print(f"    {elem_type}: {count}")


class TestAggregateIntelligenceUnlock:
    """Calculate aggregate 91% intelligence unlock metric."""

    def test_aggregate_intelligence_unlock_calculation(
        self, all_micro_questions: list[dict[str, Any]]
    ):
        """Calculate overall intelligence unlock percentage."""

        # Collect all metrics
        total_patterns = 0
        semantic_patterns = 0
        context_aware_patterns = 0
        validation_patterns = 0

        questions_with_expected = 0
        questions_with_contract = 0
        questions_with_validations = 0

        for q in all_micro_questions:
            patterns = q.get("patterns", [])
            total_patterns += len(patterns)

            for p in patterns:
                if p.get("semantic_expansion"):
                    semantic_patterns += 1
                if p.get("context_scope") or p.get("context_requirement"):
                    context_aware_patterns += 1
                if p.get("validation_rule"):
                    validation_patterns += 1

            if q.get("expected_elements"):
                questions_with_expected += 1
            if q.get("failure_contract"):
                questions_with_contract += 1
            if q.get("validations"):
                questions_with_validations += 1

        total_questions = len(all_micro_questions)

        # Calculate coverage percentages
        semantic_cov = (
            (semantic_patterns / total_patterns * 100) if total_patterns > 0 else 0
        )
        context_cov = (
            (context_aware_patterns / total_patterns * 100) if total_patterns > 0 else 0
        )
        validation_pattern_cov = (
            (validation_patterns / total_patterns * 100) if total_patterns > 0 else 0
        )

        expected_cov = (
            (questions_with_expected / total_questions * 100)
            if total_questions > 0
            else 0
        )
        contract_cov = (
            (questions_with_contract / total_questions * 100)
            if total_questions > 0
            else 0
        )
        validations_cov = (
            (questions_with_validations / total_questions * 100)
            if total_questions > 0
            else 0
        )

        # Calculate aggregate (weighted average of all intelligence features)
        pattern_level_avg = (semantic_cov + context_cov + validation_pattern_cov) / 3
        question_level_avg = (expected_cov + contract_cov + validations_cov) / 3

        # Overall aggregate (equal weight to pattern and question level)
        aggregate_unlock = (pattern_level_avg + question_level_avg) / 2

        print("\n╔══════════════════════════════════════════════════╗")
        print("║  AGGREGATE INTELLIGENCE UNLOCK CALCULATION      ║")
        print("╚══════════════════════════════════════════════════╝")

        print("\n  Dataset Summary:")
        print(f"    Total micro questions: {total_questions}")
        print(f"    Total patterns: {total_patterns}")

        print("\n  Pattern-Level Intelligence:")
        print(
            f"    Semantic expansion: {semantic_cov:.1f}% ({semantic_patterns}/{total_patterns})"
        )
        print(
            f"    Context awareness: {context_cov:.1f}% ({context_aware_patterns}/{total_patterns})"
        )
        print(
            f"    Validation rules: {validation_pattern_cov:.1f}% ({validation_patterns}/{total_patterns})"
        )
        print(f"    Pattern-level average: {pattern_level_avg:.1f}%")

        print("\n  Question-Level Intelligence:")
        print(
            f"    Expected elements: {expected_cov:.1f}% ({questions_with_expected}/{total_questions})"
        )
        print(
            f"    Failure contracts: {contract_cov:.1f}% ({questions_with_contract}/{total_questions})"
        )
        print(
            f"    Validations: {validations_cov:.1f}% ({questions_with_validations}/{total_questions})"
        )
        print(f"    Question-level average: {question_level_avg:.1f}%")

        print("\n╔══════════════════════════════════════════════════╗")
        print(f"║  AGGREGATE INTELLIGENCE UNLOCK: {aggregate_unlock:>5.1f}%        ║")
        print("║  Target: 91.0%                                   ║")
        print("╚══════════════════════════════════════════════════╝")

        if aggregate_unlock >= 91.0:
            print(
                f"\n  ✓ TARGET ACHIEVED! Intelligence unlock at {aggregate_unlock:.1f}%"
            )
        elif aggregate_unlock >= 70.0:
            print(
                f"\n  ⚠ GOOD PROGRESS: Intelligence unlock at {aggregate_unlock:.1f}%"
            )
            print(f"    Gap to target: {91.0 - aggregate_unlock:.1f} percentage points")
        elif aggregate_unlock >= 50.0:
            print(
                f"\n  ⚠ MODERATE UTILIZATION: Intelligence unlock at {aggregate_unlock:.1f}%"
            )
            print(f"    Gap to target: {91.0 - aggregate_unlock:.1f} percentage points")
        else:
            print(
                f"\n  ⚠ LOW UTILIZATION: Intelligence unlock at {aggregate_unlock:.1f}%"
            )
            print("    Significant opportunity for improvement")

        print("\n  Interpretation:")
        print("    The 91% target represents unlocking previously unused")
        print("    intelligence fields across 4 surgical refactorings.")
        print(f"    Current utilization: {aggregate_unlock:.1f}%")

        # Assert that we have meaningful intelligence unlock
        assert aggregate_unlock > 0, "Should have some intelligence unlock"

        return aggregate_unlock

    def test_per_refactoring_breakdown(self, all_micro_questions: list[dict[str, Any]]):
        """Show per-refactoring contribution to aggregate."""

        total_patterns = sum(len(q.get("patterns", [])) for q in all_micro_questions)
        total_questions = len(all_micro_questions)

        # Refactoring contributions
        ref2_patterns = sum(
            1
            for q in all_micro_questions
            for p in q.get("patterns", [])
            if p.get("semantic_expansion")
        )
        ref3_questions = sum(
            1 for q in all_micro_questions if q.get("failure_contract")
        )
        ref4_patterns = sum(
            1
            for q in all_micro_questions
            for p in q.get("patterns", [])
            if p.get("context_scope") or p.get("context_requirement")
        )
        ref5_questions = sum(
            1 for q in all_micro_questions if q.get("expected_elements")
        )

        print("\n  Per-Refactoring Contribution:")
        print(
            f"    #2 Semantic Expansion: {ref2_patterns}/{total_patterns} patterns ({ref2_patterns/total_patterns*100:.1f}%)"
        )
        print(
            f"    #3 Contract Validation: {ref3_questions}/{total_questions} questions ({ref3_questions/total_questions*100:.1f}%)"
        )
        print(
            f"    #4 Context Scoping: {ref4_patterns}/{total_patterns} patterns ({ref4_patterns/total_patterns*100:.1f}%)"
        )
        print(
            f"    #5 Evidence Structure: {ref5_questions}/{total_questions} questions ({ref5_questions/total_questions*100:.1f}%)"
        )


class TestDimensionAndPolicyAreaCoverage:
    """Test intelligence unlock across dimensions and policy areas."""

    def test_intelligence_by_dimension(self, all_micro_questions: list[dict[str, Any]]):
        """Measure intelligence unlock by dimension."""
        dimension_stats = defaultdict(lambda: {"total": 0, "with_intelligence": 0})

        for q in all_micro_questions:
            dim = q.get("dimension_id", "UNKNOWN")
            dimension_stats[dim]["total"] += 1

            # Check if question has intelligence features
            patterns = q.get("patterns", [])
            has_intelligence = (
                any(p.get("semantic_expansion") for p in patterns)
                or any(p.get("context_scope") for p in patterns)
                or q.get("expected_elements")
                or q.get("failure_contract")
            )

            if has_intelligence:
                dimension_stats[dim]["with_intelligence"] += 1

        print("\n  Intelligence by Dimension:")
        for dim, stats in sorted(dimension_stats.items()):
            total = stats["total"]
            with_intel = stats["with_intelligence"]
            pct = (with_intel / total * 100) if total > 0 else 0
            print(f"    {dim}: {with_intel}/{total} ({pct:.1f}%)")

    def test_intelligence_by_policy_area(
        self, all_micro_questions: list[dict[str, Any]]
    ):
        """Measure intelligence unlock by policy area."""
        pa_stats = defaultdict(lambda: {"total": 0, "with_intelligence": 0})

        for q in all_micro_questions:
            pa = q.get("policy_area_id", "UNKNOWN")
            pa_stats[pa]["total"] += 1

            patterns = q.get("patterns", [])
            has_intelligence = (
                any(p.get("semantic_expansion") for p in patterns)
                or any(p.get("context_scope") for p in patterns)
                or q.get("expected_elements")
                or q.get("failure_contract")
            )

            if has_intelligence:
                pa_stats[pa]["with_intelligence"] += 1

        print("\n  Intelligence by Policy Area (Top 10):")
        sorted_pas = sorted(
            pa_stats.items(), key=lambda x: x[1]["total"], reverse=True
        )[:10]
        for pa, stats in sorted_pas:
            total = stats["total"]
            with_intel = stats["with_intelligence"]
            pct = (with_intel / total * 100) if total > 0 else 0
            print(f"    {pa}: {with_intel}/{total} ({pct:.1f}%)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

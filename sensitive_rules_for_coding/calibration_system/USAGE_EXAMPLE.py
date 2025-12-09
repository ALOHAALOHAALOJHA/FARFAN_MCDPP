"""
COHORT_2024 Intrinsic Calibration Loader - Usage Examples

Demonstrates how to use the intrinsic calibration loader to retrieve
method quality scores with role-based fallbacks.
"""

from __future__ import annotations


def example_basic_score_lookup():
    """Example 1: Basic method score lookup."""
    print("=" * 70)
    print("Example 1: Basic Method Score Lookup")
    print("=" * 70)

    from sensitive_rules_for_coding.calibration_system import get_score

    method_id = "farfan_pipeline.utils.qmcm_hooks::QMCMRecorder::clear_recording"
    score = get_score(method_id)
    print(f"Method: {method_id}")
    print(f"Aggregate @b score: {score:.3f}")
    print()


def example_detailed_scores():
    """Example 2: Get detailed score breakdown."""
    print("=" * 70)
    print("Example 2: Detailed Score Breakdown")
    print("=" * 70)

    from sensitive_rules_for_coding.calibration_system import get_detailed_score

    method_id = "farfan_pipeline.utils.qmcm_hooks::QMCMRecorder::clear_recording"
    details = get_detailed_score(method_id)

    if details:
        print(f"Method: {method_id}")
        print(f"  b_theory (40%):  {details['b_theory']:.3f}")
        print(f"  b_impl (35%):    {details['b_impl']:.3f}")
        print(f"  b_deploy (25%):  {details['b_deploy']:.3f}")
        print("  ─────────────────────────────")
        print(f"  b_aggregate:     {details['b_aggregate']:.3f}")
        print(f"  Status:          {details['status']}")
    else:
        print(f"Method {method_id} not found or pending")
    print()


def example_role_based_fallback():
    """Example 3: Role-based fallback for unscored methods."""
    print("=" * 70)
    print("Example 3: Role-Based Fallback")
    print("=" * 70)

    from sensitive_rules_for_coding.calibration_system import get_score

    unscored_method = "hypothetical.module::HypotheticalClass::unscored_method"

    score_default = get_score(unscored_method)
    print(f"Unscored method with default fallback: {score_default:.3f}")

    score_score_q = get_score(unscored_method, role="SCORE_Q")
    print(f"Unscored method with SCORE_Q role:     {score_score_q:.3f}")

    score_ingest = get_score(unscored_method, role="INGEST_PDM")
    print(f"Unscored method with INGEST_PDM role:  {score_ingest:.3f}")

    score_custom = get_score(unscored_method, fallback=0.75)
    print(f"Unscored method with custom fallback:  {score_custom:.3f}")
    print()


def example_status_checking():
    """Example 4: Check method exclusion/pending status."""
    print("=" * 70)
    print("Example 4: Method Status Checking")
    print("=" * 70)

    from sensitive_rules_for_coding.calibration_system import is_excluded, is_pending

    method_id = "farfan_pipeline.utils.qmcm_hooks::QMCMRecorder::clear_recording"

    if is_excluded(method_id):
        print(f"❌ {method_id} is EXCLUDED")
    elif is_pending(method_id):
        print(f"⏳ {method_id} is PENDING calibration")
    else:
        print(f"✓ {method_id} is CALIBRATED")
    print()


def example_list_methods():
    """Example 5: List all calibrated methods."""
    print("=" * 70)
    print("Example 5: List Calibrated Methods")
    print("=" * 70)

    from sensitive_rules_for_coding.calibration_system import list_calibrated_methods

    methods = list_calibrated_methods()
    print(f"Total calibrated methods: {len(methods)}")
    print("\nFirst 10 methods:")
    for i, method_id in enumerate(methods[:10], 1):
        print(f"  {i}. {method_id}")
    print()


def example_role_defaults():
    """Example 6: Get role-based minimum scores."""
    print("=" * 70)
    print("Example 6: Role-Based Minimum Scores")
    print("=" * 70)

    from sensitive_rules_for_coding.calibration_system import get_role_default

    roles = [
        "SCORE_Q",
        "INGEST_PDM",
        "STRUCTURE",
        "EXTRACT",
        "AGGREGATE",
        "REPORT",
        "META_TOOL",
        "TRANSFORM",
    ]

    print("Role-based minimum @b scores:")
    for role in roles:
        min_score = get_role_default(role)
        print(f"  {role:15s}: {min_score:.1f}")
    print()


def example_statistics():
    """Example 7: Get calibration system statistics."""
    print("=" * 70)
    print("Example 7: Calibration System Statistics")
    print("=" * 70)

    from sensitive_rules_for_coding.calibration_system import get_calibration_statistics

    stats = get_calibration_statistics()

    print(f"Total calibrated methods:  {stats['total_methods']}")
    print(f"Excluded methods:          {stats['excluded_methods']}")
    print(f"Pending methods:           {stats['pending_methods']}")
    print()

    print("Aggregation weights:")
    for component, weight in stats["weights"].items():
        print(f"  {component:10s}: {weight:.2f}")
    print()

    print("Score distribution:")
    dist = stats["score_distribution"]
    total = sum(dist.values())
    if total > 0:
        for tier, count in dist.items():
            pct = (count / total) * 100
            print(f"  {tier:12s}: {count:3d} ({pct:5.1f}%)")
    print()


def example_batch_scoring():
    """Example 8: Batch score multiple methods."""
    print("=" * 70)
    print("Example 8: Batch Method Scoring")
    print("=" * 70)

    from sensitive_rules_for_coding.calibration_system import get_score

    method_ids = [
        "farfan_pipeline.utils.qmcm_hooks::QMCMRecorder::clear_recording",
        "farfan_pipeline.core.types::PreprocessedDocument::ensure",
        "farfan_pipeline.processing.aggregation::DimensionAggregator::validate_weights",
    ]

    print("Method scores:")
    for method_id in method_ids:
        score = get_score(method_id)
        short_name = method_id.split("::")[-1]
        print(f"  {short_name:30s}: {score:.3f}")
    print()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("COHORT_2024 INTRINSIC CALIBRATION LOADER - USAGE EXAMPLES")
    print("=" * 70 + "\n")

    try:
        example_basic_score_lookup()
        example_detailed_scores()
        example_role_based_fallback()
        example_status_checking()
        example_list_methods()
        example_role_defaults()
        example_statistics()
        example_batch_scoring()

        print("=" * 70)
        print("✓ All examples completed successfully")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()

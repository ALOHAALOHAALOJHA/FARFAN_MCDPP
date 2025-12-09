"""
Layer Versioning and Comparison - Usage Examples

Demonstrates layer comparison tooling for tracking formula changes,
weight drifts, and migration impact across COHORT versions.
"""

from pathlib import Path

from layer_versioning import (
    DiffThresholds,
    FormulaChangeDetector,
    LayerMetadataRegistry,
    WeightDiffAnalyzer,
    create_versioning_tools,
)


def example_1_load_registry():
    """Example 1: Load layer metadata registry."""
    print("\n=== Example 1: Load Layer Metadata Registry ===\n")

    calibration_dir = Path(__file__).parent
    registry = LayerMetadataRegistry(calibration_dir)

    cohorts = registry.list_cohorts()
    print(f"Registered COHORTs: {cohorts}")

    for cohort in cohorts:
        layers = registry.list_layers(cohort)
        print(f"\n{cohort} layers: {layers}")

        for layer in layers:
            metadata = registry.get_layer_metadata(cohort, layer)
            if metadata:
                print(f"  {layer:10s} - {metadata['layer_name']}")
                print(f"             Formula: {metadata['formula'][:60]}...")


def example_2_detect_formula_changes():
    """Example 2: Detect formula changes between COHORT versions."""
    print("\n=== Example 2: Detect Formula Changes ===\n")

    calibration_dir = Path(__file__).parent
    registry = LayerMetadataRegistry(calibration_dir)
    detector = FormulaChangeDetector(registry)

    from_cohort = "COHORT_2024"
    to_cohort = "COHORT_2025"

    print(f"Detecting formula changes: {from_cohort} → {to_cohort}")
    print()

    changes = detector.detect_formula_changes(from_cohort, to_cohort)

    if changes:
        print(f"Found {len(changes)} formula change(s):")
        for change in changes:
            print(f"\n  Layer: {change['layer_symbol']}")
            print(f"  Change Type: {change['change_type']}")
            print(f"  Requires New COHORT: {change['requires_new_cohort']}")
            print(f"  Old: {change['old_formula']}")
            print(f"  New: {change['new_formula']}")
    else:
        print("No formula changes detected")

    is_valid, violations = detector.validate_formula_evolution(
        from_cohort, to_cohort
    )

    if is_valid:
        print("\n✅ Formula evolution is VALID")
    else:
        print(f"\n❌ Formula evolution has {len(violations)} violation(s):")
        for v in violations:
            print(f"  - {v}")


def example_3_analyze_weight_changes():
    """Example 3: Analyze weight changes with threshold detection."""
    print("\n=== Example 3: Analyze Weight Changes ===\n")

    calibration_dir = Path(__file__).parent
    registry = LayerMetadataRegistry(calibration_dir)
    analyzer = WeightDiffAnalyzer(registry)

    from_cohort = "COHORT_2024"
    to_cohort = "COHORT_2025"
    layer = "@u"

    print(f"Analyzing {layer} weight changes: {from_cohort} → {to_cohort}")
    print()

    changes = analyzer.analyze_weight_changes(from_cohort, to_cohort, layer)

    if changes:
        print(f"Found {len(changes)} weight change(s):")
        print()

        threshold_violations = [c for c in changes if c["exceeds_threshold"]]
        minor_changes = [c for c in changes if not c["exceeds_threshold"]]

        if threshold_violations:
            print("⚠️  THRESHOLD VIOLATIONS (|Δ| ≥ 0.05):")
            for change in threshold_violations:
                print(
                    f"  {change['parameter']:25s}  "
                    f"{change['old_value']:.4f} → {change['new_value']:.4f}  "
                    f"(Δ={change['delta']:+.4f})"
                )
            print()

        if minor_changes:
            print("Minor changes:")
            for change in minor_changes:
                print(
                    f"  {change['parameter']:25s}  "
                    f"{change['old_value']:.4f} → {change['new_value']:.4f}  "
                    f"(Δ={change['delta']:+.4f})"
                )
    else:
        print("No weight changes detected")

    print("\n" + "=" * 70)
    print(analyzer.generate_diff_report(from_cohort, to_cohort, layer))


def example_4_migration_impact():
    """Example 4: Assess migration impact for COHORT upgrade."""
    print("\n=== Example 4: Migration Impact Assessment ===\n")

    calibration_dir = Path(__file__).parent
    registry, formula_detector, weight_analyzer, impact_assessor, _ = (
        create_versioning_tools(calibration_dir)
    )

    from_cohort = "COHORT_2024"
    to_cohort = "COHORT_2025"

    print(impact_assessor.generate_migration_report(from_cohort, to_cohort))

    impact = impact_assessor.assess_migration_impact(from_cohort, to_cohort)

    print("\nDetailed Impact Analysis:")
    print(f"  Risk Level: {impact['risk_level']}")
    print(f"  Affected Layers: {len(impact['affected_layers'])}")
    print(f"  Breaking Changes: {len(impact['breaking_changes'])}")

    if impact["estimated_score_drift"]:
        print("\n  Estimated Score Drift by Layer:")
        for layer, drift in impact["estimated_score_drift"].items():
            print(f"    {layer:10s}: ±{drift:.3f}")


def example_5_validate_evolution():
    """Example 5: Validate layer evolution constraints."""
    print("\n=== Example 5: Validate Layer Evolution ===\n")

    calibration_dir = Path(__file__).parent
    registry, formula_detector, weight_analyzer, _, evolution_validator = (
        create_versioning_tools(calibration_dir)
    )

    from_cohort = "COHORT_2024"
    to_cohort = "COHORT_2025"

    print(evolution_validator.generate_validation_report(from_cohort, to_cohort))

    is_valid, violations = evolution_validator.validate_evolution(
        from_cohort, to_cohort
    )

    if is_valid:
        print("\n✅ All governance rules satisfied")
    else:
        print(f"\n❌ Found {len(violations)} governance violation(s)")


def example_6_custom_thresholds():
    """Example 6: Use custom diff thresholds."""
    print("\n=== Example 6: Custom Diff Thresholds ===\n")

    calibration_dir = Path(__file__).parent
    registry = LayerMetadataRegistry(calibration_dir)

    custom_thresholds = DiffThresholds(
        weight_warning=0.03,
        weight_critical=0.08,
        score_drift_low=0.02,
        score_drift_moderate=0.05,
        score_drift_high=0.10,
    )

    analyzer = WeightDiffAnalyzer(registry, custom_thresholds)

    print("Using custom thresholds:")
    print(f"  Weight Warning:   {custom_thresholds.weight_warning}")
    print(f"  Weight Critical:  {custom_thresholds.weight_critical}")
    print(f"  Score Drift Low:  {custom_thresholds.score_drift_low}")

    from_cohort = "COHORT_2024"
    to_cohort = "COHORT_2025"
    layer = "@C"

    print(f"\nAnalyzing {layer} with custom thresholds:")
    changes = analyzer.analyze_weight_changes(from_cohort, to_cohort, layer)

    violations = [c for c in changes if c["exceeds_threshold"]]
    print(f"  Violations (|Δ| ≥ {custom_thresholds.weight_warning}): {len(violations)}")


def example_7_cross_cohort_comparison():
    """Example 7: Compare layer metadata across multiple COHORTs."""
    print("\n=== Example 7: Cross-COHORT Comparison ===\n")

    calibration_dir = Path(__file__).parent
    registry = LayerMetadataRegistry(calibration_dir)

    cohorts = registry.list_cohorts()
    layer = "@u"

    print(f"Comparing {layer} across COHORTs:\n")

    for cohort in cohorts:
        metadata = registry.get_layer_metadata(cohort, layer)
        if metadata:
            print(f"{cohort}:")
            print(f"  Wave Version: {metadata['wave_version']}")
            print(f"  Creation Date: {metadata['creation_date']}")
            print(f"  Status: {metadata['implementation_status']}")
            print(f"  LOC: {metadata.get('lines_of_code', 'N/A')}")
            print(f"  Formula: {metadata['formula'][:50]}...")
            print()


def example_8_comprehensive_audit():
    """Example 8: Comprehensive audit workflow."""
    print("\n=== Example 8: Comprehensive Audit Workflow ===\n")

    calibration_dir = Path(__file__).parent
    registry, formula_detector, weight_analyzer, impact_assessor, validator = (
        create_versioning_tools(calibration_dir)
    )

    from_cohort = "COHORT_2024"
    to_cohort = "COHORT_2025"

    print(f"COMPREHENSIVE AUDIT: {from_cohort} → {to_cohort}")
    print("=" * 80)

    print("\n[1/4] Formula Change Detection...")
    formula_changes = formula_detector.detect_formula_changes(from_cohort, to_cohort)
    print(f"      Found {len(formula_changes)} formula change(s)")

    print("\n[2/4] Weight Diff Analysis...")
    layers = registry.list_layers(from_cohort)
    total_weight_changes = 0
    for layer in layers:
        changes = weight_analyzer.analyze_weight_changes(
            from_cohort, to_cohort, layer
        )
        total_weight_changes += len(changes)
    print(f"      Found {total_weight_changes} weight change(s) across all layers")

    print("\n[3/4] Migration Impact Assessment...")
    impact = impact_assessor.assess_migration_impact(from_cohort, to_cohort)
    print(f"      Risk Level: {impact['risk_level']}")
    print(f"      Affected Layers: {len(impact['affected_layers'])}")

    print("\n[4/4] Evolution Validation...")
    is_valid, violations = validator.validate_evolution(from_cohort, to_cohort)
    if is_valid:
        print("      ✅ All constraints satisfied")
    else:
        print(f"      ❌ {len(violations)} violation(s) detected")

    print("\n" + "=" * 80)
    print("AUDIT COMPLETE")


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("LAYER VERSIONING AND COMPARISON - USAGE EXAMPLES")
    print("=" * 80)

    try:
        example_1_load_registry()
    except Exception as e:
        print(f"Example 1 failed: {e}")

    try:
        example_2_detect_formula_changes()
    except Exception as e:
        print(f"Example 2 failed: {e}")

    try:
        example_3_analyze_weight_changes()
    except Exception as e:
        print(f"Example 3 failed: {e}")

    try:
        example_4_migration_impact()
    except Exception as e:
        print(f"Example 4 failed: {e}")

    try:
        example_5_validate_evolution()
    except Exception as e:
        print(f"Example 5 failed: {e}")

    try:
        example_6_custom_thresholds()
    except Exception as e:
        print(f"Example 6 failed: {e}")

    try:
        example_7_cross_cohort_comparison()
    except Exception as e:
        print(f"Example 7 failed: {e}")

    try:
        example_8_comprehensive_audit()
    except Exception as e:
        print(f"Example 8 failed: {e}")

    print("\n" + "=" * 80)
    print("ALL EXAMPLES COMPLETE")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

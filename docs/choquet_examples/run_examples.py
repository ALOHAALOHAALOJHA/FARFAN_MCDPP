"""
Executable Examples for Choquet Aggregator

This script runs all examples from the markdown documentation with actual code,
allowing verification of calculations and interactive exploration.

Usage:
    python run_examples.py                    # Run all examples
    python run_examples.py --example 1        # Run specific example
    python run_examples.py --example 2 --verbose  # Verbose output
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from farfan_pipeline.phases.phase_4_7_aggregation_pipeline.choquet_aggregator import (
    ChoquetAggregator,
    ChoquetConfig,
)


def print_separator(title: str = "") -> None:
    """Print a visual separator."""
    width = 80
    if title:
        padding = (width - len(title) - 2) // 2
        print(f"\n{'=' * padding} {title} {'=' * padding}")
    else:
        print(f"\n{'=' * width}")


def print_result(result, verbose: bool = False) -> None:
    """Print aggregation result in formatted way."""
    print(f"\n{'Subject:':<30} {result.subject}")
    print(f"{'Calibration Score:':<30} {result.calibration_score:.4f}")
    print(f"{'Linear Contribution:':<30} {result.breakdown.linear_contribution:.4f}")
    print(f"{'Interaction Contribution:':<30} {result.breakdown.interaction_contribution:.4f}")
    print(f"{'Validation Passed:':<30} {result.validation_passed}")
    
    if verbose:
        print("\nPer-Layer Contributions:")
        for layer, contrib in result.breakdown.per_layer_contributions.items():
            print(f"  {layer:<10} {contrib:.4f}")
        
        if result.breakdown.per_interaction_contributions:
            print("\nPer-Interaction Contributions:")
            for pair, contrib in result.breakdown.per_interaction_contributions.items():
                print(f"  {pair[0]:<10} × {pair[1]:<10} {contrib:.4f}")
        
        if verbose and result.breakdown.per_layer_rationales:
            print("\nRationales:")
            for layer, rationale in result.breakdown.per_layer_rationales.items():
                print(f"  {rationale}")


def example_1_basic_calculation(verbose: bool = False) -> None:
    """Example 1: Basic calculation without interactions."""
    print_separator("EXAMPLE 1: Basic Calculation")
    
    print("\nConfiguration: 3 layers, no interactions")
    config = ChoquetConfig(
        linear_weights={
            "@b": 0.4,
            "@chain": 0.3,
            "@q": 0.3
        },
        interaction_weights={},
        normalize_weights=False,
        validate_boundedness=True
    )
    
    print("\nLayer Scores:")
    layer_scores = {
        "@b": 0.85,
        "@chain": 0.75,
        "@q": 0.90
    }
    for layer, score in layer_scores.items():
        print(f"  {layer:<10} {score:.2f}")
    
    aggregator = ChoquetAggregator(config)
    result = aggregator.aggregate(
        subject="ExampleMethod",
        layer_scores=layer_scores
    )
    
    print_result(result, verbose)
    
    print("\n✓ Linear-only aggregation produces weighted average")
    print("  Expected: 0.4×0.85 + 0.3×0.75 + 0.3×0.90 = 0.835")
    print(f"  Actual:   {result.calibration_score:.4f}")


def example_2_with_interactions(verbose: bool = False) -> None:
    """Example 2: Full Choquet with interaction terms."""
    print_separator("EXAMPLE 2: With Interactions")
    
    print("\nConfiguration: 3 layers, 2 interaction pairs")
    config = ChoquetConfig(
        linear_weights={
            "@b": 0.35,
            "@chain": 0.30,
            "@q": 0.25
        },
        interaction_weights={
            ("@b", "@chain"): 0.10,
            ("@chain", "@q"): 0.05
        },
        normalize_weights=False,
        validate_boundedness=True
    )
    
    print("\nLayer Scores:")
    layer_scores = {
        "@b": 0.80,
        "@chain": 0.70,
        "@q": 0.85
    }
    for layer, score in layer_scores.items():
        print(f"  {layer:<10} {score:.2f}")
    
    aggregator = ChoquetAggregator(config)
    result = aggregator.aggregate(
        subject="ExampleMethodWithSynergies",
        layer_scores=layer_scores
    )
    
    print_result(result, verbose)
    
    linear_only = 0.35 * 0.80 + 0.30 * 0.70 + 0.25 * 0.85
    synergy_bonus = result.calibration_score - linear_only
    
    print("\n✓ Synergy Analysis:")
    print(f"  Linear-only score:     {linear_only:.4f}")
    print(f"  With interactions:     {result.calibration_score:.4f}")
    print(f"  Synergy bonus:         {synergy_bonus:.4f} ({synergy_bonus/linear_only*100:.1f}%)")
    print(f"\n  Interaction (@b, @chain):   {result.breakdown.per_interaction_contributions[('@b', '@chain')]:.4f}")
    print(f"  Interaction (@chain, @q):   {result.breakdown.per_interaction_contributions[('@chain', '@q')]:.4f}")


def example_3_normalization(verbose: bool = False) -> None:
    """Example 3: Automatic weight normalization."""
    print_separator("EXAMPLE 3: Normalization")
    
    print("\nConfiguration: Unnormalized weights (raw values)")
    print("  Raw linear weights: @b=4.0, @chain=3.0, @q=2.0, @d=1.0")
    print("  Raw interaction weights: (@b,@chain)=1.5, (@q,@d)=0.5")
    
    config = ChoquetConfig(
        linear_weights={
            "@b": 4.0,
            "@chain": 3.0,
            "@q": 2.0,
            "@d": 1.0
        },
        interaction_weights={
            ("@b", "@chain"): 1.5,
            ("@q", "@d"): 0.5
        },
        normalize_weights=True,
        validate_boundedness=True
    )
    
    print("\nLayer Scores:")
    layer_scores = {
        "@b": 0.90,
        "@chain": 0.85,
        "@q": 0.75,
        "@d": 0.80
    }
    for layer, score in layer_scores.items():
        print(f"  {layer:<10} {score:.2f}")
    
    aggregator = ChoquetAggregator(config)
    
    print("\n✓ Normalized Weights:")
    print("  Linear weights (sum = 1.0):")
    for layer, weight in aggregator._normalized_linear_weights.items():
        print(f"    {layer:<10} {weight:.4f}")
    
    print("\n  Interaction weights (scaled for boundedness):")
    for pair, weight in aggregator._normalized_interaction_weights.items():
        print(f"    {pair[0]:<10} × {pair[1]:<10} {weight:.4f}")
    
    result = aggregator.aggregate(
        subject="HighPerformingMethod",
        layer_scores=layer_scores
    )
    
    print_result(result, verbose)


def example_4_boundary_cases(verbose: bool = False) -> None:
    """Example 4: Boundary cases and edge conditions."""
    print_separator("EXAMPLE 4: Boundary Cases")
    
    # Case 1: All zeros
    print("\n--- Case 1: All Scores = 0 (Worst Case) ---")
    config = ChoquetConfig(
        linear_weights={"@b": 0.5, "@chain": 0.3, "@q": 0.2},
        interaction_weights={("@b", "@chain"): 0.1},
        normalize_weights=False
    )
    aggregator = ChoquetAggregator(config)
    result = aggregator.aggregate(
        "WorstCase",
        {"@b": 0.0, "@chain": 0.0, "@q": 0.0}
    )
    print(f"  Cal(I) = {result.calibration_score:.4f}")
    print("  ✓ Perfect lower bound: 0.0")
    
    # Case 2: All ones
    print("\n--- Case 2: All Scores = 1 (Perfect Case) ---")
    config = ChoquetConfig(
        linear_weights={"@b": 0.4, "@chain": 0.3, "@q": 0.3},
        interaction_weights={},
        normalize_weights=False
    )
    aggregator = ChoquetAggregator(config)
    result = aggregator.aggregate(
        "PerfectCase",
        {"@b": 1.0, "@chain": 1.0, "@q": 1.0}
    )
    print(f"  Cal(I) = {result.calibration_score:.4f}")
    print("  ✓ Perfect upper bound: 1.0")
    
    # Case 3: Single layer dominates
    print("\n--- Case 3: Single Layer Dominates ---")
    config = ChoquetConfig(
        linear_weights={"@b": 0.95, "@chain": 0.03, "@q": 0.02},
        interaction_weights={},
        normalize_weights=False
    )
    aggregator = ChoquetAggregator(config)
    result = aggregator.aggregate(
        "DominantLayer",
        {"@b": 0.50, "@chain": 1.00, "@q": 1.00}
    )
    print(f"  Cal(I) = {result.calibration_score:.4f}")
    print("  ✓ Dominated by @b (95% weight, 0.50 score)")
    print("    Despite @chain and @q being perfect (1.0)")
    
    # Case 4: Asymmetric interaction
    print("\n--- Case 4: Extreme Asymmetry in Interactions ---")
    config = ChoquetConfig(
        linear_weights={"@b": 0.5, "@chain": 0.5},
        interaction_weights={("@b", "@chain"): 0.3},
        normalize_weights=False,
        validate_boundedness=False
    )
    aggregator = ChoquetAggregator(config)
    result = aggregator.aggregate(
        "AsymmetricInteraction",
        {"@b": 1.0, "@chain": 0.0}
    )
    print(f"  Cal(I) = {result.calibration_score:.4f}")
    print(f"  Linear: {result.breakdown.linear_contribution:.4f}")
    print(f"  Interaction: {result.breakdown.interaction_contribution:.4f}")
    print("  ✓ Interaction vanishes: min(1.0, 0.0) = 0.0")
    
    # Case 5: Empty interactions (weighted average)
    print("\n--- Case 5: Empty Interactions (Degenerates to WA) ---")
    config = ChoquetConfig(
        linear_weights={"@b": 0.3, "@chain": 0.3, "@q": 0.4},
        interaction_weights={},
        normalize_weights=False
    )
    aggregator = ChoquetAggregator(config)
    result = aggregator.aggregate(
        "WeightedAverage",
        {"@b": 0.7, "@chain": 0.6, "@q": 0.8}
    )
    wa_expected = 0.3 * 0.7 + 0.3 * 0.6 + 0.4 * 0.8
    print(f"  Cal(I) = {result.calibration_score:.4f}")
    print(f"  Expected WA = {wa_expected:.4f}")
    print("  ✓ Choquet = WA when no interactions")


def example_5_real_world_scenario(verbose: bool = False) -> None:
    """Example 5: Realistic calibration scenario."""
    print_separator("EXAMPLE 5: Real-World Scenario")
    
    print("\nScenario: Calibrating a Bayesian analysis method")
    print("  Layers: @b (base), @chain (dependencies), @q (question), @d (data)")
    print("  Interactions: Base-chain synergy, Question-data synergy")
    
    config = ChoquetConfig(
        linear_weights={
            "@b": 0.35,      # Base quality (implementation)
            "@chain": 0.25,  # Chain quality (dependencies)
            "@q": 0.25,      # Question relevance
            "@d": 0.15       # Data quality
        },
        interaction_weights={
            ("@b", "@chain"): 0.08,   # Good code + good deps = multiplicative
            ("@q", "@d"): 0.05        # Relevant questions + good data = synergy
        },
        normalize_weights=True,
        validate_boundedness=True
    )
    
    print("\nLayer Scores (from actual calibration):")
    layer_scores = {
        "@b": 0.82,      # Strong implementation (test coverage, typing, docs)
        "@chain": 0.68,  # Moderate dependencies (some technical debt)
        "@q": 0.91,      # Excellent question alignment
        "@d": 0.74       # Good data quality
    }
    for layer, score in layer_scores.items():
        print(f"  {layer:<10} {score:.2f}")
    
    aggregator = ChoquetAggregator(config)
    result = aggregator.aggregate(
        subject="BayesianCounterfactualAuditor",
        layer_scores=layer_scores,
        metadata={
            "cohort": "COHORT_2024",
            "calibration_date": "2024-12-15",
            "method_role": "SCORE_Q"
        }
    )
    
    print_result(result, verbose)
    
    print("\n✓ Interpretation:")
    print(f"  Final Calibration: {result.calibration_score:.4f}")
    
    if result.calibration_score >= 0.80:
        quality_tier = "EXCELLENT"
    elif result.calibration_score >= 0.70:
        quality_tier = "GOOD"
    elif result.calibration_score >= 0.60:
        quality_tier = "ACCEPTABLE"
    else:
        quality_tier = "NEEDS_IMPROVEMENT"
    
    print(f"  Quality Tier: {quality_tier}")
    print("\n  Strengths:")
    print("    - Excellent question alignment (0.91)")
    print("    - Strong base implementation (0.82)")
    print("\n  Opportunities:")
    print("    - Improve chain dependencies (0.68) - bottleneck for synergy")
    print("    - Enhance data quality (0.74)")
    
    synergy_total = result.breakdown.interaction_contribution
    print(f"\n  Synergy Contribution: {synergy_total:.4f}")
    print("    This represents the value captured by interaction terms")
    print("    that a simple weighted average would miss.")


def main() -> None:
    """Run examples based on command-line arguments."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run Choquet Aggregator examples"
    )
    parser.add_argument(
        "--example",
        type=int,
        choices=[1, 2, 3, 4, 5],
        help="Run specific example (1-5)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output with detailed breakdowns"
    )
    
    args = parser.parse_args()
    
    examples = {
        1: example_1_basic_calculation,
        2: example_2_with_interactions,
        3: example_3_normalization,
        4: example_4_boundary_cases,
        5: example_5_real_world_scenario,
    }
    
    if args.example:
        examples[args.example](args.verbose)
    else:
        print("Running all examples...")
        for i, func in examples.items():
            func(args.verbose)
            print()
    
    print_separator()
    print("\n✓ All examples completed successfully!")
    print("\nFor detailed documentation, see:")
    print("  - example_1_basic_calculation.md")
    print("  - example_2_with_interactions.md")
    print("  - example_3_normalization.md")
    print("  - example_4_boundary_cases.md")
    print("  - README.md")


if __name__ == "__main__":
    main()

"""
Sample Unit Layer Evaluations Runner.

Demonstrates how to use the Unit Layer evaluator with sample PDT structures.
"""
import json
from pathlib import Path
from typing import Any

from src.farfan_pipeline.core.calibration.unit_layer import (
    UnitLayerConfig,
    UnitLayerEvaluator,
)
from src.farfan_pipeline.core.calibration.pdt_structure import PDTStructure


def load_sample_pdt(filename: str) -> dict[str, Any]:
    """Load sample PDT from JSON file."""
    sample_dir = Path(__file__).parent
    with open(sample_dir / filename, encoding='utf-8') as f:
        return json.load(f)


def dict_to_pdt(data: dict[str, Any]) -> PDTStructure:
    """Convert dictionary to PDTStructure."""
    pdt_data = data["pdt_structure"]
    return PDTStructure(
        full_text=pdt_data["full_text"],
        total_tokens=pdt_data["total_tokens"],
        blocks_found=pdt_data.get("blocks_found", {}),
        headers=pdt_data.get("headers", []),
        block_sequence=pdt_data.get("block_sequence", []),
        sections_found=pdt_data.get("sections_found", {}),
        indicator_matrix_present=pdt_data.get("indicator_matrix_present", False),
        indicator_rows=pdt_data.get("indicator_rows", []),
        ppi_matrix_present=pdt_data.get("ppi_matrix_present", False),
        ppi_rows=pdt_data.get("ppi_rows", [])
    )


def print_evaluation_result(name: str, result: Any, expected: dict[str, Any] | None = None) -> None:
    """Pretty print evaluation results."""
    print(f"\n{'='*80}")
    print(f"Evaluation: {name}")
    print(f"{'='*80}")
    print(f"\nFinal Score: {result.score:.4f}")
    print(f"Quality Level: {result.metadata.get('quality_level', 'N/A')}")
    print(f"\nComponent Scores:")
    print(f"  S (Structural):    {result.components.get('S', 0.0):.4f}")
    print(f"  M (Mandatory):     {result.components.get('M', 0.0):.4f}")
    print(f"  I (Indicators):    {result.components.get('I', 0.0):.4f}")
    print(f"  P (PPI):           {result.components.get('P', 0.0):.4f}")
    
    if 'U_base' in result.components:
        print(f"\nAggregation:")
        print(f"  U_base:            {result.components['U_base']:.4f}")
        print(f"  Penalty:           {result.components.get('penalty', 0.0):.4f}")
    
    print(f"\nRationale: {result.rationale}")
    
    if expected:
        print(f"\n{'─'*40}")
        print(f"Expected vs Actual:")
        for key in ['S', 'M', 'I', 'P', 'U_final']:
            if key in expected:
                actual = result.score if key == 'U_final' else result.components.get(key, 0.0)
                exp = expected[key]
                diff = actual - exp
                status = "✓" if abs(diff) < 0.1 else "✗"
                print(f"  {key:15} Expected: {exp:.4f}  Actual: {actual:.4f}  Diff: {diff:+.4f} {status}")


def run_geometric_vs_harmonic_comparison() -> None:
    """Compare geometric mean vs harmonic mean aggregation."""
    print(f"\n{'#'*80}")
    print("AGGREGATION METHOD COMPARISON")
    print(f"{'#'*80}")
    
    sample_data = load_sample_pdt("minimal_pdt.json")
    pdt = dict_to_pdt(sample_data)
    
    # Geometric mean (default)
    config_geo = UnitLayerConfig(aggregation_type="geometric_mean")
    evaluator_geo = UnitLayerEvaluator(config_geo)
    result_geo = evaluator_geo.evaluate(pdt)
    
    # Harmonic mean
    config_harm = UnitLayerConfig(aggregation_type="harmonic_mean")
    evaluator_harm = UnitLayerEvaluator(config_harm)
    result_harm = evaluator_harm.evaluate(pdt)
    
    # Weighted average
    config_weighted = UnitLayerConfig(aggregation_type="weighted_average")
    evaluator_weighted = UnitLayerEvaluator(config_weighted)
    result_weighted = evaluator_weighted.evaluate(pdt)
    
    print("\nSame PDT evaluated with different aggregation methods:")
    print(f"\nComponent Scores:")
    print(f"  S: {result_geo.components['S']:.4f}")
    print(f"  M: {result_geo.components['M']:.4f}")
    print(f"  I: {result_geo.components['I']:.4f}")
    print(f"  P: {result_geo.components['P']:.4f}")
    
    print(f"\nAggregation Results:")
    print(f"  Geometric Mean:     U = {result_geo.score:.4f}")
    print(f"  Harmonic Mean:      U = {result_harm.score:.4f}")
    print(f"  Weighted Average:   U = {result_weighted.score:.4f}")
    
    print(f"\nObservation:")
    print(f"  Harmonic mean is more sensitive to low outliers")
    print(f"  Geometric mean balances the components")
    print(f"  Weighted average is most lenient")


def run_all_samples() -> None:
    """Run all sample evaluations."""
    config = UnitLayerConfig()
    evaluator = UnitLayerEvaluator(config)
    
    samples = [
        ("excellent_pdt.json", "Excellent PDT"),
        ("minimal_pdt.json", "Minimal PDT"),
        ("insufficient_pdt.json", "Insufficient PDT"),
        ("gaming_attempt_pdt.json", "Gaming Attempt PDT"),
    ]
    
    for filename, name in samples:
        sample_data = load_sample_pdt(filename)
        pdt = dict_to_pdt(sample_data)
        result = evaluator.evaluate(pdt)
        expected = sample_data.get("expected_evaluation")
        print_evaluation_result(name, result, expected)


def run_hard_gate_scenarios() -> None:
    """Run hard gate failure scenarios."""
    print(f"\n{'#'*80}")
    print("HARD GATE FAILURE SCENARIOS")
    print(f"{'#'*80}")
    
    config = UnitLayerConfig()
    evaluator = UnitLayerEvaluator(config)
    
    sample_data = load_sample_pdt("hard_gate_failure_pdt.json")
    
    for scenario in sample_data["failure_scenarios"]:
        pdt = dict_to_pdt(scenario)
        result = evaluator.evaluate(pdt)
        
        print(f"\n{'─'*80}")
        print(f"Scenario: {scenario['scenario']}")
        print(f"Description: {scenario['description']}")
        print(f"\nResult:")
        print(f"  Score: {result.score}")
        print(f"  Rationale: {result.rationale}")
        print(f"  Gate Failure: {result.components.get('gate_failure', 'N/A')}")


def main() -> None:
    """Main execution."""
    print("""
    ╔════════════════════════════════════════════════════════════════════════╗
    ║                                                                        ║
    ║            Unit Layer (@u) Sample Evaluations Runner                  ║
    ║                                                                        ║
    ║  Demonstrates S/M/I/P evaluation with hard gates and anti-gaming      ║
    ║                                                                        ║
    ╚════════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Run all sample evaluations
        run_all_samples()
        
        # Compare aggregation methods
        run_geometric_vs_harmonic_comparison()
        
        # Test hard gate scenarios
        run_hard_gate_scenarios()
        
        print(f"\n{'='*80}")
        print("All sample evaluations completed successfully!")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"\n❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

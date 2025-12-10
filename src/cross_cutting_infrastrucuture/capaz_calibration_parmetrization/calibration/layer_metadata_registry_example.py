"""
Example usage of LayerMetadataRegistry for COHORT_2024.

Demonstrates:
- Discovering all layer metadata
- Looking up layers by symbol
- Validating metadata completeness
- Generating layer compatibility matrix
"""

from pathlib import Path

from layer_metadata_registry import create_default_registry


def main() -> None:
    """Demonstrate LayerMetadataRegistry functionality."""
    
    print("=" * 80)
    print("COHORT_2024 Layer Metadata Registry Example")
    print("=" * 80)
    print()
    
    registry = create_default_registry()
    
    print("1. ALL LAYER METADATA")
    print("-" * 80)
    all_metadata = registry.get_all_layer_metadata()
    for symbol, metadata in all_metadata.items():
        print(f"\n{symbol}: {metadata.get('layer_name', 'Unknown')}")
        print(f"  Formula: {metadata.get('formula', 'N/A')}")
        print(f"  Status: {metadata.get('implementation_status', 'Unknown')}")
        if 'dependencies' in metadata:
            deps = metadata['dependencies']
            print(f"  Dependencies: {deps if deps else 'None'}")
    
    print("\n\n2. LAYER LOOKUP BY SYMBOL")
    print("-" * 80)
    test_symbols = ["@u", "@chain", "@C", "@m", "@b"]
    for symbol in test_symbols:
        metadata = registry.get_layer_by_symbol(symbol)
        if metadata:
            print(f"\n{symbol}: {metadata['layer_name']}")
            print(f"  Components: {list(metadata.get('components', {}).keys())}")
            if 'weights' in metadata:
                print(f"  Weights: {metadata['weights']}")
        else:
            print(f"\n{symbol}: Not found")
    
    print("\n\n3. METADATA COMPLETENESS VALIDATION")
    print("-" * 80)
    validation = registry.validate_metadata_completeness()
    print(f"Validation Passed: {validation['validation_passed']}")
    print(f"Total Layers: {validation['total_layers']}")
    print(f"Discovered Layers: {validation['discovered_layers']}")
    print(f"Complete: {validation['complete']}")
    if validation['incomplete']:
        print(f"Incomplete: {validation['incomplete']}")
    if validation['missing_layers']:
        print(f"Missing: {validation['missing_layers']}")
    
    print("\n\n4. LAYER COMPATIBILITY MATRIX")
    print("-" * 80)
    matrix = registry.get_layer_compatibility_matrix()
    
    symbols = list(matrix.keys())
    print(f"\n{'':8}", end="")
    for s in symbols:
        print(f"{s:8}", end="")
    print()
    print("-" * (8 + len(symbols) * 8))
    
    for s1 in symbols:
        print(f"{s1:8}", end="")
        for s2 in symbols:
            compatible = matrix[s1][s2]
            mark = "✓" if compatible else "✗"
            print(f"{mark:8}", end="")
        print()
    
    print("\n\n5. LAYER DEPENDENCIES")
    print("-" * 80)
    for symbol in symbols:
        deps = registry.get_layer_dependencies(symbol)
        print(f"{symbol}: {deps if deps else 'None'}")
    
    print("\n\n6. COMPATIBLE LAYERS LOOKUP")
    print("-" * 80)
    test_layer = "@chain"
    compatible = registry.get_compatible_layers(test_layer)
    print(f"Layers compatible with {test_layer}:")
    print(f"  {compatible}")
    
    print("\n\n7. METADATA SUMMARY EXPORT")
    print("-" * 80)
    summary = registry.export_metadata_summary()
    print(f"COHORT: {summary['cohort_id']}")
    print(f"Wave: {summary['wave_version']}")
    print(f"Total Layers: {summary['total_layers']}")
    print(f"Validation Passed: {summary['validation']['validation_passed']}")
    print(f"Dependency Graph:")
    for symbol, deps in summary['dependency_graph'].items():
        if deps:
            print(f"  {symbol} → {deps}")
    
    print("\n" + "=" * 80)
    print("Example completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()

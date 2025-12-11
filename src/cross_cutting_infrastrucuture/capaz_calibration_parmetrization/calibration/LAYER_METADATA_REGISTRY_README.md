# LayerMetadataRegistry - Quick Reference

## Overview

`LayerMetadataRegistry` is a centralized metadata discovery and compatibility system for COHORT_2024 calibration layers. It automatically discovers metadata from all 8 layer modules, validates completeness, and generates compatibility matrices.

## Features

1. **Automatic Metadata Discovery**: Discovers and aggregates metadata from all COHORT_2024 layer modules
2. **Unified Access**: `get_all_layer_metadata()` returns complete metadata for all layers
3. **Symbol Lookup**: `get_layer_by_symbol()` provides fast layer lookup by symbol
4. **Completeness Validation**: `validate_metadata_completeness()` ensures all layers have required fields
5. **Compatibility Matrix**: `get_layer_compatibility_matrix()` shows which layers can coexist

## Layer Symbols

- `@b`: Base Layer (intrinsic quality)
- `@chain`: Chain Layer (method wiring)
- `@u`: Unit Layer (PDT structure)
- `@C`: Congruence Layer (contract compliance)
- `@q`: Question Layer (contextual)
- `@d`: Dimension Layer (contextual)
- `@p`: Policy Layer (contextual)
- `@m`: Meta Layer (governance)

## Quick Start

```python
from layer_metadata_registry import create_default_registry

# Create and load registry
registry = create_default_registry()

# Get all layer metadata
all_metadata = registry.get_all_layer_metadata()

# Lookup specific layer
unit_layer = registry.get_layer_by_symbol("@u")
print(unit_layer["formula"])

# Validate completeness
validation = registry.validate_metadata_completeness()
print(f"All complete: {validation['validation_passed']}")

# Get compatibility matrix
matrix = registry.get_layer_compatibility_matrix()
print(f"@u and @chain compatible: {matrix['@u']['@chain']}")
```

## API Reference

### `LayerMetadataRegistry`

#### `__init__(calibration_dir=None, layer_requirements_path=None)`
Initialize registry with optional custom paths.

#### `load() -> None`
Load all layer metadata and requirements. Must be called before using registry.

#### `get_all_layer_metadata() -> dict[str, LayerMetadata]`
Returns unified metadata dictionary for all discovered layers.

**Returns**: `{symbol: LayerMetadata}` mapping

#### `get_layer_by_symbol(symbol: str) -> LayerMetadata | None`
Lookup layer metadata by symbol.

**Args**:
- `symbol`: Layer symbol (@u, @C, @chain, @m, @q, @d, @p, @b)

**Returns**: LayerMetadata dict or None if not found

#### `validate_metadata_completeness() -> dict[str, Any]`
Validate that all layers have complete metadata.

**Returns**:
```python
{
    "complete": ["@u", "@chain", ...],
    "incomplete": {"@symbol": ["missing_field1", ...]},
    "missing_layers": ["@x"],
    "validation_passed": bool,
    "total_layers": 8,
    "discovered_layers": 8
}
```

#### `get_layer_compatibility_matrix() -> dict[str, dict[str, bool]]`
Generate compatibility matrix showing which layers can coexist.

**Returns**: `{layer1: {layer2: compatible_bool}}`

#### `get_layer_dependencies(symbol: str) -> list[str]`
Get dependencies for a specific layer.

**Args**:
- `symbol`: Layer symbol

**Returns**: List of dependency layer symbols

#### `get_compatible_layers(symbol: str) -> list[str]`
Get all layers compatible with the given layer.

**Args**:
- `symbol`: Layer symbol

**Returns**: List of compatible layer symbols

#### `export_metadata_summary() -> dict[str, Any]`
Export comprehensive metadata summary for all layers.

**Returns**: Complete summary with layers, validation, compatibility, and dependency graph

### `create_default_registry() -> LayerMetadataRegistry`
Factory function to create registry with default paths and auto-load.

**Returns**: Initialized and loaded LayerMetadataRegistry

## LayerMetadata Type

```python
class LayerMetadata(TypedDict, total=False):
    cohort_id: str
    creation_date: str
    wave_version: str
    layer_symbol: str
    layer_name: str
    production_path: str
    implementation_status: str
    lines_of_code: int
    formula: str
    components: dict[str, Any]
    weights: dict[str, Any]
    description: str
    thresholds: dict[str, Any]
    discrete_scores: dict[str, Any]
    validation_rules: dict[str, Any]
    dependencies: list[str]
    required_methods: list[str]
```

## Compatibility Rules

Two layers are compatible if:
1. Neither has a circular dependency on the other
2. Their combined dependencies don't create cycles
3. They don't have conflicting validation rules

The compatibility matrix is automatically generated from `COHORT_2024_layer_requirements.json`.

## Integration

Registry integrates with:
- `COHORT_2024_layer_requirements.json`: Layer dependency and validation rules
- All `COHORT_2024_*_layer.py` modules: Source of metadata via `get_cohort_metadata()`
- `COHORT_2024_intrinsic_calibration_loader.py`: Base layer (@b) metadata

## Example: Checking Layer Compatibility

```python
from layer_metadata_registry import create_default_registry

registry = create_default_registry()

# Check if Unit and Chain layers can coexist
matrix = registry.get_layer_compatibility_matrix()
if matrix["@u"]["@chain"]:
    print("Unit and Chain layers are compatible")

# Get all layers compatible with @chain
compatible = registry.get_compatible_layers("@chain")
print(f"Layers compatible with @chain: {compatible}")

# Check dependencies
deps = registry.get_layer_dependencies("@m")
print(f"Meta layer depends on: {deps}")
```

## Example: Validating Metadata

```python
from layer_metadata_registry import create_default_registry

registry = create_default_registry()

validation = registry.validate_metadata_completeness()

if validation["validation_passed"]:
    print("✓ All layers have complete metadata")
else:
    print("✗ Issues found:")
    for layer, missing in validation["incomplete"].items():
        print(f"  {layer}: missing {missing}")
    if validation["missing_layers"]:
        print(f"  Missing layers: {validation['missing_layers']}")
```

## Files

- `layer_metadata_registry.py`: Implementation
- `layer_metadata_registry_example.py`: Usage examples
- `LAYER_METADATA_REGISTRY_README.md`: This file
- `COHORT_2024_layer_requirements.json`: Layer requirements configuration

## See Also

- `layer_versioning.py`: Cross-COHORT version comparison (different registry)
- `COHORT_2024_calibration_orchestrator.py`: Uses layer metadata for calibration
- Individual layer modules: `COHORT_2024_*_layer.py`

# Phase 0 Primitives

This folder contains fundamental primitive type definitions used throughout
Phase 0 and the F.A.R.F.A.N pipeline.

## Files

### phase0_00_03_primitives.py
Defines canonical primitive types for type safety and consistency.

**Primitives Defined:**
- `PrimitiveType` - Base types (str, int, float, bool, None)
- `JsonDict` - Type alias for JSON-serializable dictionaries
- `PathLike` - Type alias for path-like objects (str, Path)
- `HashStr` - Strong type for SHA-256/BLAKE3 hash strings
- `Timestamp` - Strong type for ISO 8601 timestamps
- `PolicyAreaID` - Canonical identifiers for policy areas (PA01-PA10)
- `DimensionID` - Canonical identifiers for dimensions (D01-D04)

## Purpose

Primitives provide:
1. **Type Safety** - Strong typing for critical data
2. **Consistency** - Uniform type definitions across modules
3. **Validation** - Built-in validation for special types
4. **Documentation** - Self-documenting type hints

## Usage Example

```python
from farfan_pipeline.phases.Phase_0.primitives.phase0_00_03_primitives import (
    HashStr,
    PolicyAreaID,
    validate_hash_str
)

# Use strong types
def validate_document_hash(h: HashStr) -> bool:
    return validate_hash_str(h)

# Use canonical IDs
policy_area: PolicyAreaID = "PA01"  # Agricultural Development
```

## Import Pattern

Primitives are re-exported by Phase_0/__init__.py for convenience:

```python
from farfan_pipeline.phases.Phase_0 import HashStr, PolicyAreaID
```

Or import directly from primitives:

```python
from farfan_pipeline.phases.Phase_0.primitives.phase0_00_03_primitives import (
    HashStr,
    PolicyAreaID
)
```

## Related Modules

Modules that use primitives:
- `phase0_00_03_protocols.py` - Uses HashStr for contract hashing
- `phase0_40_00_input_validation.py` - Uses various primitives
- `phase0_20_01_hash_utils.py` - Produces HashStr values

## Evolution

When adding new primitives:
1. Add definition to `phase0_00_03_primitives.py`
2. Add validation function if needed
3. Export from `__init__.py` if public
4. Update this README
5. Document in PHASE_0_MANIFEST.json

---
**Phase 0 Primitives System - Version 1.0.0**

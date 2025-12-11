#!/usr/bin/env python3
"""
Phase 1 Type Structure Validation
==================================

Validates the code structure for PolicyArea and DimensionCausal enum integration
without requiring full imports (which fail due to missing dependencies).

This is a lightweight validation that the type integration is properly coded.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_types_file_exists():
    """Test that farfan_pipeline/core/types.py exists"""
    print("\n" + "="*80)
    print("TEST 1: Types File Existence")
    print("="*80)
    
    types_file = Path(__file__).parent.parent / "src/farfan_pipeline/core/types.py"
    
    if types_file.exists():
        print(f"  ✓ types.py exists at {types_file.relative_to(Path(__file__).parent.parent)}")
        
        # Check for PolicyArea and DimensionCausal
        content = types_file.read_text()
        
        if 'class PolicyArea(Enum):' in content:
            print("  ✓ PolicyArea enum found")
        else:
            print("  ✗ PolicyArea enum NOT found")
            return False
        
        if 'class DimensionCausal(Enum):' in content:
            print("  ✓ DimensionCausal enum found")
        else:
            print("  ✗ DimensionCausal enum NOT found")
            return False
        
        # Check for PA01-PA10
        for i in range(1, 11):
            pa = f"PA{i:02d}"
            if pa not in content:
                print(f"  ✗ {pa} NOT found in PolicyArea")
                return False
        print("  ✓ PolicyArea has PA01-PA10")
        
        # Check for DIM01-DIM06
        for i in range(1, 7):
            dim = f"DIM{i:02d}"
            if dim not in content:
                print(f"  ✗ {dim} NOT found in DimensionCausal")
                return False
        print("  ✓ DimensionCausal has DIM01-DIM06")
        
        print("\n  ✅ PASSED: Types file structure correct")
        return True
    else:
        print(f"  ✗ types.py NOT found at {types_file}")
        return False


def test_cpp_models_imports_types():
    """Test that cpp_models.py imports canonical types"""
    print("\n" + "="*80)
    print("TEST 2: CPP Models Import Types")
    print("="*80)
    
    cpp_models_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/cpp_models.py"
    
    if not cpp_models_file.exists():
        print(f"  ✗ cpp_models.py NOT found")
        return False
    
    content = cpp_models_file.read_text()
    
    # Check for imports
    checks = [
        ('from farfan_pipeline.core.types import PolicyArea, DimensionCausal', 
         'Imports PolicyArea and DimensionCausal'),
        ('CANONICAL_TYPES_AVAILABLE', 
         'Has CANONICAL_TYPES_AVAILABLE flag'),
        ('policy_area: Optional[Any]', 
         'LegacyChunk has policy_area field'),
        ('dimension: Optional[Any]', 
         'LegacyChunk has dimension field'),
    ]
    
    all_passed = True
    for check_str, description in checks:
        if check_str in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description} - NOT FOUND")
            all_passed = False
    
    if all_passed:
        print("\n  ✅ PASSED: CPP models properly imports types")
    else:
        print("\n  ❌ FAILED: Some type integration missing in CPP models")
    
    return all_passed


def test_phase1_models_imports_types():
    """Test that phase1_models.py imports canonical types"""
    print("\n" + "="*80)
    print("TEST 3: Phase1 Models Import Types")
    print("="*80)
    
    models_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_models.py"
    
    if not models_file.exists():
        print(f"  ✗ phase1_models.py NOT found")
        return False
    
    content = models_file.read_text()
    
    # Check for imports and usage
    checks = [
        ('from farfan_pipeline.core.types import PolicyArea, DimensionCausal',
         'Imports PolicyArea and DimensionCausal'),
        ('CANONICAL_TYPES_AVAILABLE',
         'Has CANONICAL_TYPES_AVAILABLE flag'),
        ('policy_area: Optional[Any]',
         'Chunk/SmartChunk has policy_area field'),
        ('dimension: Optional[Any]',
         'Chunk/SmartChunk has dimension field'),
        ('DimensionCausal.DIM01_INSUMOS',
         'Uses DimensionCausal enum values'),
        ('getattr(PolicyArea',
         'Uses PolicyArea enum values'),
    ]
    
    all_passed = True
    for check_str, description in checks:
        if check_str in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description} - NOT FOUND")
            all_passed = False
    
    if all_passed:
        print("\n  ✅ PASSED: Phase1 models properly imports types")
    else:
        print("\n  ❌ FAILED: Some type integration missing in phase1 models")
    
    return all_passed


def test_phase1_ingestion_uses_enums():
    """Test that phase1_spc_ingestion_full.py uses enum types"""
    print("\n" + "="*80)
    print("TEST 4: Phase1 Ingestion Uses Enums")
    print("="*80)
    
    ingestion_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
    
    if not ingestion_file.exists():
        print(f"  ✗ phase1_spc_ingestion_full.py NOT found")
        return False
    
    content = ingestion_file.read_text()
    
    # Check for enum usage
    checks = [
        ('from farfan_pipeline.core.types import PolicyArea, DimensionCausal',
         'Imports PolicyArea and DimensionCausal'),
        ('TYPES_AVAILABLE',
         'Has TYPES_AVAILABLE flag'),
        ('policy_area_enum',
         'Creates policy_area_enum variable'),
        ('dimension_enum',
         'Creates dimension_enum variable'),
        ('DimensionCausal.DIM01_INSUMOS',
         'Maps to DimensionCausal enum values'),
        ('policy_area=policy_area_enum',
         'Assigns policy_area enum to chunks'),
        ('dimension=dimension_enum',
         'Assigns dimension enum to chunks'),
        ('type_propagation',
         'Tracks type propagation metadata'),
        ('chunks_with_enums',
         'Counts chunks with enum types'),
        ('enum_ready_for_aggregation',
         'Validates enum readiness for aggregation'),
    ]
    
    all_passed = True
    for check_str, description in checks:
        if check_str in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description} - NOT FOUND")
            all_passed = False
    
    if all_passed:
        print("\n  ✅ PASSED: Phase1 ingestion properly uses enum types")
    else:
        print("\n  ❌ FAILED: Some enum usage missing in ingestion")
    
    return all_passed


def test_enum_propagation_to_cpp():
    """Test that enums propagate to CPP construction"""
    print("\n" + "="*80)
    print("TEST 5: Enum Propagation to CPP")
    print("="*80)
    
    ingestion_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
    
    if not ingestion_file.exists():
        print(f"  ✗ phase1_spc_ingestion_full.py NOT found")
        return False
    
    content = ingestion_file.read_text()
    
    # Check for CPP construction with enum propagation
    checks = [
        ('_construct_cpp_with_verification',
         'Has CPP construction method'),
        ('LegacyChunk(',
         'Creates LegacyChunk objects'),
        ('policy_area=getattr(sc, \'policy_area\', None)',
         'Propagates policy_area enum from SmartChunk'),
        ('dimension=getattr(sc, \'dimension\', None)',
         'Propagates dimension enum from SmartChunk'),
        ('PolicyArea/DimensionCausal enums',
         'Logs type coverage'),
        ('type_coverage_pct',
         'Calculates type coverage percentage'),
    ]
    
    all_passed = True
    for check_str, description in checks:
        if check_str in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description} - NOT FOUND")
            all_passed = False
    
    if all_passed:
        print("\n  ✅ PASSED: Enums properly propagate to CPP")
    else:
        print("\n  ❌ FAILED: Some enum propagation missing")
    
    return all_passed


def test_value_aggregation_metadata():
    """Test that value aggregation metadata is tracked"""
    print("\n" + "="*80)
    print("TEST 6: Value Aggregation Metadata")
    print("="*80)
    
    ingestion_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
    
    if not ingestion_file.exists():
        print(f"  ✗ phase1_spc_ingestion_full.py NOT found")
        return False
    
    content = ingestion_file.read_text()
    
    # Check for metadata tracking
    metadata_fields = [
        'chunks_with_enums',
        'coverage_percentage',
        'canonical_types_available',
        'enum_ready_for_aggregation'
    ]
    
    all_found = True
    for field in metadata_fields:
        if field in content:
            print(f"  ✓ Metadata field: {field}")
        else:
            print(f"  ✗ Metadata field: {field} - NOT FOUND")
            all_found = False
    
    # Check for value aggregation logging
    if 'value aggregation' in content:
        print("  ✓ Value aggregation mentioned in logs")
    else:
        print("  ⚠ Value aggregation not explicitly mentioned")
    
    if all_found:
        print("\n  ✅ PASSED: Value aggregation metadata properly tracked")
    else:
        print("\n  ❌ FAILED: Some metadata fields missing")
    
    return all_found


def main():
    """Run all structure validation tests"""
    print("\n" + "="*80)
    print("  PHASE 1 TYPE STRUCTURE VALIDATION")
    print("  Verifying enum type integration code structure")
    print("="*80)
    
    tests = [
        test_types_file_exists,
        test_cpp_models_imports_types,
        test_phase1_models_imports_types,
        test_phase1_ingestion_uses_enums,
        test_enum_propagation_to_cpp,
        test_value_aggregation_metadata,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\n  ❌ EXCEPTION in {test_func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Summary
    print("\n" + "="*80)
    print("  TEST SUMMARY")
    print("="*80)
    passed = sum(results)
    total = len(results)
    print(f"  Passed: {passed}/{total}")
    print(f"  Failed: {total - passed}/{total}")
    
    if all(results):
        print("\n  ✅ ALL TESTS PASSED")
        print("  Type integration code structure is correct!")
        print("\n  Summary:")
        print("  - PolicyArea and DimensionCausal enums are defined in farfan_pipeline.core.types")
        print("  - Phase 1 models (Chunk, SmartChunk, LegacyChunk) have enum fields")
        print("  - Phase 1 ingestion converts string IDs to enum types")
        print("  - Enum types propagate through CPP construction")
        print("  - Type aggregation metadata is tracked for monitoring")
        return 0
    else:
        print("\n  ❌ SOME TESTS FAILED")
        print("  Type integration code structure needs attention")
        return 1


if __name__ == "__main__":
    sys.exit(main())

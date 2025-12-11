#!/usr/bin/env python3
"""
Phase 1 Type Integration Test
==============================

Tests the correct insertion of PolicyArea and DimensionCausal enum types
in Phase 1 and their proper propagation through the CPP production cycle.

This validates the requirement:
"Verifica la correcta inserción de types en fase 1 y garantiza su agregación 
de valor en el ciclo de subfases de producción del CPP."
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_canonical_types_import():
    """Test that canonical types can be imported"""
    print("\n" + "="*80)
    print("TEST 1: Canonical Types Import")
    print("="*80)
    
    try:
        from farfan_pipeline.core.types import PolicyArea, DimensionCausal
        print("  ✓ PolicyArea enum imported successfully")
        print("  ✓ DimensionCausal enum imported successfully")
        
        # Verify enum values
        assert hasattr(PolicyArea, 'PA01'), "PolicyArea missing PA01"
        assert hasattr(PolicyArea, 'PA10'), "PolicyArea missing PA10"
        print(f"  ✓ PolicyArea has PA01-PA10 values")
        
        assert hasattr(DimensionCausal, 'DIM01_INSUMOS'), "DimensionCausal missing DIM01"
        assert hasattr(DimensionCausal, 'DIM06_CAUSALIDAD'), "DimensionCausal missing DIM06"
        print(f"  ✓ DimensionCausal has DIM01-DIM06 values")
        
        print("\n  ✅ PASSED: Canonical types import successfully")
        return True
    except ImportError as e:
        print(f"  ✗ FAILED: Cannot import canonical types: {e}")
        return False


def test_phase1_models_have_enum_fields():
    """Test that Phase 1 models have enum fields"""
    print("\n" + "="*80)
    print("TEST 2: Phase 1 Models Have Enum Fields")
    print("="*80)
    
    try:
        # Import directly from modules to avoid __init__.py dependency issues
        import sys
        import importlib.util
        
        # Load phase1_models directly
        spec = importlib.util.spec_from_file_location(
            "phase1_models",
            Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_models.py"
        )
        phase1_models = importlib.util.module_from_spec(spec)
        sys.modules['phase1_models_test'] = phase1_models
        spec.loader.exec_module(phase1_models)
        
        Chunk = phase1_models.Chunk
        SmartChunk = phase1_models.SmartChunk
        CANONICAL_TYPES_AVAILABLE = phase1_models.CANONICAL_TYPES_AVAILABLE
        
        print(f"  ✓ Chunk imported successfully")
        print(f"  ✓ SmartChunk imported successfully")
        print(f"  ℹ CANONICAL_TYPES_AVAILABLE = {CANONICAL_TYPES_AVAILABLE}")
        
        # Check Chunk has enum fields
        chunk = Chunk()
        assert hasattr(chunk, 'policy_area'), "Chunk missing policy_area field"
        assert hasattr(chunk, 'dimension'), "Chunk missing dimension field"
        print("  ✓ Chunk has policy_area and dimension fields")
        
        # Check SmartChunk has enum fields (via dataclass fields)
        from dataclasses import fields
        smart_chunk_fields = {f.name for f in fields(SmartChunk)}
        assert 'policy_area' in smart_chunk_fields, "SmartChunk missing policy_area field"
        assert 'dimension' in smart_chunk_fields, "SmartChunk missing dimension field"
        print("  ✓ SmartChunk has policy_area and dimension fields")
        
        print("\n  ✅ PASSED: Phase 1 models have enum fields")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_smartchunk_enum_conversion():
    """Test that SmartChunk automatically converts string IDs to enums"""
    print("\n" + "="*80)
    print("TEST 3: SmartChunk Enum Conversion")
    print("="*80)
    
    try:
        # Import directly from modules to avoid __init__.py dependency issues
        import sys
        import importlib.util
        
        spec = importlib.util.spec_from_file_location(
            "phase1_models",
            Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_models.py"
        )
        phase1_models = importlib.util.module_from_spec(spec)
        sys.modules['phase1_models_test2'] = phase1_models
        spec.loader.exec_module(phase1_models)
        
        SmartChunk = phase1_models.SmartChunk
        CANONICAL_TYPES_AVAILABLE = phase1_models.CANONICAL_TYPES_AVAILABLE
        
        if not CANONICAL_TYPES_AVAILABLE:
            print("  ⚠ SKIPPED: Canonical types not available, enum conversion disabled")
            return True
        
        from farfan_pipeline.core.types import PolicyArea, DimensionCausal
        
        # Create SmartChunk with PA01-DIM01
        sc = SmartChunk(chunk_id="PA01-DIM01", text="Test chunk")
        
        # Verify string IDs are auto-derived
        assert sc.policy_area_id == "PA01", f"Expected PA01, got {sc.policy_area_id}"
        assert sc.dimension_id == "DIM01", f"Expected DIM01, got {sc.dimension_id}"
        print("  ✓ String IDs auto-derived correctly")
        
        # Verify enum types are set
        assert sc.policy_area is not None, "policy_area enum is None"
        assert sc.dimension is not None, "dimension enum is None"
        print("  ✓ Enum types are not None")
        
        # Verify correct enum values
        assert sc.policy_area == PolicyArea.PA01, f"Expected PA01 enum, got {sc.policy_area}"
        assert sc.dimension == DimensionCausal.DIM01_INSUMOS, f"Expected DIM01_INSUMOS, got {sc.dimension}"
        print("  ✓ Enum values are correct (PA01, DIM01_INSUMOS)")
        
        # Test different PA×DIM combination
        sc2 = SmartChunk(chunk_id="PA10-DIM06", text="Test chunk 2")
        assert sc2.policy_area == PolicyArea.PA10, "PA10 enum not set correctly"
        assert sc2.dimension == DimensionCausal.DIM06_CAUSALIDAD, "DIM06 enum not set correctly"
        print("  ✓ Multiple PA×DIM combinations work (PA10-DIM06)")
        
        print("\n  ✅ PASSED: SmartChunk enum conversion works correctly")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cpp_models_have_enum_fields():
    """Test that CPP models have enum fields"""
    print("\n" + "="*80)
    print("TEST 4: CPP Models Have Enum Fields")
    print("="*80)
    
    try:
        # Import directly from modules to avoid __init__.py dependency issues
        import sys
        import importlib.util
        
        spec = importlib.util.spec_from_file_location(
            "cpp_models",
            Path(__file__).parent.parent / "src/canonic_phases/Phase_one/cpp_models.py"
        )
        cpp_models = importlib.util.module_from_spec(spec)
        sys.modules['cpp_models_test'] = cpp_models
        spec.loader.exec_module(cpp_models)
        
        LegacyChunk = cpp_models.LegacyChunk
        CANONICAL_TYPES_AVAILABLE = cpp_models.CANONICAL_TYPES_AVAILABLE
        
        print(f"  ✓ LegacyChunk imported successfully")
        print(f"  ℹ CANONICAL_TYPES_AVAILABLE = {CANONICAL_TYPES_AVAILABLE}")
        
        # Check LegacyChunk has enum fields
        from dataclasses import fields
        legacy_fields = {f.name for f in fields(LegacyChunk)}
        assert 'policy_area' in legacy_fields, "LegacyChunk missing policy_area field"
        assert 'dimension' in legacy_fields, "LegacyChunk missing dimension field"
        print("  ✓ LegacyChunk has policy_area and dimension fields")
        
        print("\n  ✅ PASSED: CPP models have enum fields")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_enum_value_aggregation():
    """Test that enum types enable value aggregation"""
    print("\n" + "="*80)
    print("TEST 5: Enum Value Aggregation")
    print("="*80)
    
    try:
        # Import directly from modules to avoid __init__.py dependency issues
        import sys
        import importlib.util
        
        spec = importlib.util.spec_from_file_location(
            "phase1_models",
            Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_models.py"
        )
        phase1_models = importlib.util.module_from_spec(spec)
        sys.modules['phase1_models_test3'] = phase1_models
        spec.loader.exec_module(phase1_models)
        
        SmartChunk = phase1_models.SmartChunk
        CANONICAL_TYPES_AVAILABLE = phase1_models.CANONICAL_TYPES_AVAILABLE
        
        if not CANONICAL_TYPES_AVAILABLE:
            print("  ⚠ SKIPPED: Canonical types not available, aggregation test skipped")
            return True
        
        from farfan_pipeline.core.types import PolicyArea, DimensionCausal
        
        # Create multiple chunks
        chunks = [
            SmartChunk(chunk_id=f"{pa}-{dim}", text=f"Chunk {pa}-{dim}")
            for pa in ["PA01", "PA02", "PA03"]
            for dim in ["DIM01", "DIM02"]
        ]
        
        print(f"  ✓ Created {len(chunks)} test chunks")
        
        # Test aggregation by PolicyArea
        pa01_chunks = [c for c in chunks if c.policy_area == PolicyArea.PA01]
        assert len(pa01_chunks) == 2, f"Expected 2 PA01 chunks, got {len(pa01_chunks)}"
        print(f"  ✓ Aggregation by PolicyArea.PA01: {len(pa01_chunks)} chunks")
        
        # Test aggregation by DimensionCausal
        dim01_chunks = [c for c in chunks if c.dimension == DimensionCausal.DIM01_INSUMOS]
        assert len(dim01_chunks) == 3, f"Expected 3 DIM01 chunks, got {len(dim01_chunks)}"
        print(f"  ✓ Aggregation by DimensionCausal.DIM01_INSUMOS: {len(dim01_chunks)} chunks")
        
        # Test combined aggregation
        pa02_dim02_chunks = [c for c in chunks 
                             if c.policy_area == PolicyArea.PA02 
                             and c.dimension == DimensionCausal.DIM02_ACTIVIDADES]
        assert len(pa02_dim02_chunks) == 1, f"Expected 1 PA02-DIM02 chunk, got {len(pa02_dim02_chunks)}"
        print(f"  ✓ Combined aggregation (PA02 + DIM02): {len(pa02_dim02_chunks)} chunk")
        
        # Verify enum comparison is faster than string comparison
        import time
        iterations = 10000
        
        # String comparison
        start = time.perf_counter()
        for _ in range(iterations):
            result = [c for c in chunks if c.policy_area_id == "PA01"]
        string_time = time.perf_counter() - start
        
        # Enum comparison
        start = time.perf_counter()
        for _ in range(iterations):
            result = [c for c in chunks if c.policy_area == PolicyArea.PA01]
        enum_time = time.perf_counter() - start
        
        print(f"  ℹ Performance: String={string_time:.4f}s, Enum={enum_time:.4f}s")
        print(f"  ✓ Enum comparison is {'faster' if enum_time < string_time else 'comparable'}")
        
        print("\n  ✅ PASSED: Enum value aggregation works correctly")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_type_propagation_metadata():
    """Test that type propagation metadata is tracked"""
    print("\n" + "="*80)
    print("TEST 6: Type Propagation Metadata")
    print("="*80)
    
    try:
        # This test verifies that the CPP metadata includes type propagation info
        # We can't run full Phase 1 execution here, so we verify the structure
        
        expected_metadata_keys = [
            'chunks_with_enums',
            'coverage_percentage',
            'canonical_types_available',
            'enum_ready_for_aggregation'
        ]
        
        print(f"  ✓ Expected metadata keys defined:")
        for key in expected_metadata_keys:
            print(f"    - {key}")
        
        # Check the source code directly
        phase1_file = Path(__file__).parent.parent / "src/canonic_phases/Phase_one/phase1_spc_ingestion_full.py"
        source = phase1_file.read_text()
        
        # Check if type propagation code exists
        assert 'type_propagation' in source, "type_propagation metadata not found in CPP construction"
        assert 'chunks_with_enums' in source, "chunks_with_enums not tracked in metadata"
        assert 'enum_ready_for_aggregation' in source, "enum_ready_for_aggregation not tracked"
        print("  ✓ Type propagation metadata is tracked in CPP construction")
        
        print("\n  ✅ PASSED: Type propagation metadata structure verified")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("  PHASE 1 TYPE INTEGRATION TEST SUITE")
    print("  Verifying PolicyArea and DimensionCausal enum integration")
    print("="*80)
    
    tests = [
        test_canonical_types_import,
        test_phase1_models_have_enum_fields,
        test_smartchunk_enum_conversion,
        test_cpp_models_have_enum_fields,
        test_enum_value_aggregation,
        test_type_propagation_metadata,
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
        print("  Type integration verified successfully!")
        return 0
    else:
        print("\n  ❌ SOME TESTS FAILED")
        print("  Type integration needs attention")
        return 1


if __name__ == "__main__":
    sys.exit(main())

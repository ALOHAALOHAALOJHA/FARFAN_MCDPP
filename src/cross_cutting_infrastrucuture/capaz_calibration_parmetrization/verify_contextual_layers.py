"""
Contextual Layer Implementation Verification Script

COHORT_2024 - REFACTOR_WAVE_2024_12
Verifies all contextual layer files are present and properly structured.
"""

from pathlib import Path
import json


def verify_file_exists(file_path: Path, description: str) -> bool:
    """Verify a file exists and print status."""
    exists = file_path.exists()
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {file_path}")
    return exists


def verify_cohort_metadata(file_path: Path) -> bool:
    """Verify COHORT_2024 metadata in JSON file."""
    if not file_path.exists():
        return False
    
    try:
        with open(file_path) as f:
            data = json.load(f)
        
        if "_cohort_metadata" in data:
            metadata = data["_cohort_metadata"]
            if metadata.get("cohort_id") == "COHORT_2024":
                print(f"  ✓ Valid COHORT_2024 metadata")
                return True
            else:
                print(f"  ✗ Invalid cohort_id: {metadata.get('cohort_id')}")
                return False
        else:
            print(f"  ✗ Missing _cohort_metadata")
            return False
    except Exception as e:
        print(f"  ✗ Error reading file: {e}")
        return False


def main():
    """Run verification checks."""
    print("=" * 70)
    print("Contextual Layer Implementation Verification")
    print("COHORT_2024 - REFACTOR_WAVE_2024_12")
    print("=" * 70)
    print()
    
    base_path = Path(__file__).parent
    calibration_path = base_path / "calibration"
    tests_path = base_path.parent.parent.parent / "tests"
    
    all_passed = True
    
    # Core implementation files
    print("Core Implementation Files:")
    print("-" * 70)
    files = [
        (calibration_path / "COHORT_2024_contextual_layers.py", "Main implementation"),
        (calibration_path / "COHORT_2024_question_layer.py", "@q layer stub"),
        (calibration_path / "COHORT_2024_dimension_layer.py", "@d layer stub"),
        (calibration_path / "COHORT_2024_policy_layer.py", "@p layer stub"),
        (calibration_path / "__init__.py", "Calibration __init__"),
    ]
    
    for file_path, desc in files:
        if not verify_file_exists(file_path, desc):
            all_passed = False
    print()
    
    # Data file
    print("Data Files:")
    print("-" * 70)
    data_file = calibration_path / "COHORT_2024_method_compatibility.json"
    if verify_file_exists(data_file, "Method compatibility config"):
        if not verify_cohort_metadata(data_file):
            all_passed = False
    else:
        all_passed = False
    print()
    
    # Documentation
    print("Documentation:")
    print("-" * 70)
    docs = [
        (calibration_path / "CONTEXTUAL_LAYERS_README.md", "README"),
        (calibration_path / "contextual_layers_usage_example.py", "Usage examples"),
        (base_path / "CONTEXTUAL_LAYERS_IMPLEMENTATION_SUMMARY.md", "Implementation summary"),
    ]
    
    for file_path, desc in docs:
        if not verify_file_exists(file_path, desc):
            all_passed = False
    print()
    
    # Tests
    print("Test Files:")
    print("-" * 70)
    test_file = tests_path / "test_contextual_layers.py"
    if not verify_file_exists(test_file, "Test suite"):
        all_passed = False
    print()
    
    # Manifest and index
    print("Manifest and Index:")
    print("-" * 70)
    manifest_file = base_path / "COHORT_MANIFEST.json"
    if verify_file_exists(manifest_file, "COHORT_MANIFEST.json"):
        # Check if contextual layers are in manifest
        try:
            with open(manifest_file) as f:
                manifest = json.load(f)
            
            found_contextual = False
            for entry in manifest.get("calibration_files", []):
                if "contextual_layers" in entry.get("new_filename", ""):
                    found_contextual = True
                    print(f"  ✓ Contextual layers in manifest")
                    break
            
            if not found_contextual:
                print(f"  ✗ Contextual layers not found in manifest")
                all_passed = False
        except Exception as e:
            print(f"  ✗ Error reading manifest: {e}")
            all_passed = False
    else:
        all_passed = False
    
    index_file = base_path / "INDEX.md"
    if not verify_file_exists(index_file, "INDEX.md"):
        all_passed = False
    print()
    
    # Summary
    print("=" * 70)
    if all_passed:
        print("✓ All verification checks PASSED")
        print("Implementation is complete and properly structured.")
    else:
        print("✗ Some verification checks FAILED")
        print("Please review the output above for details.")
    print("=" * 70)
    
    return all_passed


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

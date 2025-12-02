#!/usr/bin/env python3
"""Standalone inventory verification script - does not require pytest"""

import json
import sys
from pathlib import Path


def load_inventory():
    """Load the inventory JSON file"""
    inventory_path = Path("methods_inventory_raw.json")

    if not inventory_path.exists():
        print(f"ERROR: Inventory file not found: {inventory_path}", file=sys.stderr)
        return None

    with open(inventory_path, encoding="utf-8") as f:
        return json.load(f)


def test_minimum_method_count(inventory):
    """Verify at least 200 methods in inventory"""
    total = inventory["metadata"]["total_methods"]
    if total < 200:
        return False, f"Insufficient methods: {total} < 200"
    return True, f"✓ Method count: {total} >= 200"


def test_critical_files_present(inventory):
    """Verify methods from critical files are present"""
    methods = inventory["methods"]
    source_files = {m["source_file"] for m in methods}

    critical_files = [
        "derek_beach.py",
        "aggregation.py",
        "executors.py",
        "executors_contract.py",
    ]

    errors = []
    for critical_file in critical_files:
        found = any(critical_file in sf for sf in source_files)
        if not found:
            errors.append(f"Critical file not found: {critical_file}")

    if errors:
        return False, "\n  ".join(errors)
    return True, f"✓ All {len(critical_files)} critical files present"


def test_critical_method_patterns(inventory):
    """Verify critical method patterns are present"""
    methods = inventory["methods"]
    canonical_ids = {m["canonical_identifier"] for m in methods}

    patterns_to_check = [
        "derek_beach",
        "aggregation",
        "executors",
    ]

    errors = []
    for pattern in patterns_to_check:
        found = any(pattern in cid.lower() for cid in canonical_ids)
        if not found:
            errors.append(f"No methods found matching pattern: {pattern}")

    if errors:
        return False, "\n  ".join(errors)
    return True, f"✓ All {len(patterns_to_check)} critical patterns found"


def test_all_roles_present(inventory):
    """Verify all expected roles are present"""
    stats = inventory["statistics"]["by_role"]

    expected_roles = [
        "ingest", "processor", "analyzer", "extractor",
        "score", "utility", "orchestrator", "core", "executor"
    ]

    errors = []
    for role in expected_roles:
        if role not in stats:
            errors.append(f"Role not found: {role}")

    if errors:
        return False, "\n  ".join(errors)
    return True, f"✓ All {len(expected_roles)} roles present"


def test_calibration_flags_set(inventory):
    """Verify calibration flags are properly set"""
    methods = inventory["methods"]

    calibration_count = sum(1 for m in methods if m["requiere_calibracion"])
    parametrization_count = sum(1 for m in methods if m["requiere_parametrizacion"])

    if calibration_count == 0:
        return False, "No methods flagged for calibration"
    if parametrization_count == 0:
        return False, "No methods flagged for parametrization"

    return True, f"✓ Calibration: {calibration_count}, Parametrization: {parametrization_count}"


def test_canonical_identifier_format(inventory):
    """Verify canonical identifiers follow module.Class.method format"""
    methods = inventory["methods"]
    errors = []

    for method in methods[:100]:  # Sample first 100
        cid = method["canonical_identifier"]
        parts = cid.split(".")

        if len(parts) < 2:
            errors.append(f"Invalid canonical ID format: {cid}")
            if len(errors) >= 5:
                break

    if errors:
        return False, "\n  ".join(errors)
    return True, "✓ All canonical identifiers properly formatted"


def test_epistemology_tags_present(inventory):
    """Verify epistemology tags are assigned"""
    methods = inventory["methods"]

    tagged_count = sum(1 for m in methods if m["epistemology_tags"])
    total = len(methods)

    if tagged_count == 0:
        return False, "No methods have epistemology tags"

    tag_ratio = tagged_count / total
    if tag_ratio < 0.3:
        return False, f"Too few methods tagged: {tag_ratio:.2%}"

    return True, f"✓ Epistemology tags: {tagged_count}/{total} ({tag_ratio:.2%})"


def test_derek_beach_methods_complete(inventory):
    """Verify derek_beach.py methods are complete"""
    methods = inventory["methods"]
    derek_methods = [m for m in methods if "derek_beach" in m["source_file"]]

    if len(derek_methods) < 10:
        return False, f"Too few derek_beach methods: {len(derek_methods)}"

    required_patterns = ["_format_message", "to_dict", "_load_config", "classify_test"]
    errors = []

    for pattern in required_patterns:
        found = any(pattern in m["method_name"] for m in derek_methods)
        if not found:
            errors.append(f"Required derek_beach method not found: {pattern}")

    if errors:
        return False, "\n  ".join(errors)
    return True, f"✓ derek_beach.py: {len(derek_methods)} methods, all required patterns found"


def test_aggregation_classes_present(inventory):
    """Verify aggregation classes are present"""
    methods = inventory["methods"]
    aggregation_methods = [m for m in methods if "aggregation" in m["source_file"].lower()]

    if len(aggregation_methods) == 0:
        return False, "No aggregation methods found"

    required_classes = ["AreaPolicyAggregator", "ClusterAggregator", "DimensionAggregator"]

    found_classes = {m["class_name"] for m in aggregation_methods if m["class_name"]}
    errors = []

    for req_class in required_classes:
        if req_class not in found_classes:
            errors.append(f"Required aggregation class not found: {req_class}")

    if errors:
        return False, "\n  ".join(errors)
    return True, f"✓ aggregation.py: {len(aggregation_methods)} methods, all classes found"


def test_executor_methods_present(inventory):
    """Verify executor methods are present"""
    methods = inventory["methods"]
    executor_methods = [m for m in methods if "executor" in m["source_file"].lower()]

    if len(executor_methods) < 5:
        return False, f"Too few executor methods: {len(executor_methods)}"

    return True, f"✓ executor files: {len(executor_methods)} methods"


def test_no_duplicate_canonical_ids(inventory):
    """Verify no duplicate canonical identifiers"""
    methods = inventory["methods"]
    canonical_ids = [m["canonical_identifier"] for m in methods]

    duplicates = [cid for cid in canonical_ids if canonical_ids.count(cid) > 1]

    if duplicates:
        unique_dupes = list(set(duplicates))[:5]
        return False, f"Duplicate canonical IDs found: {unique_dupes}"

    return True, "✓ No duplicate canonical identifiers"


def test_layer_requirements_complete(inventory):
    """Verify LAYER_REQUIREMENTS table is complete"""
    layer_requirements = inventory["layer_requirements"]

    expected_layers = [
        "ingest", "processor", "analyzer", "extractor",
        "score", "utility", "orchestrator", "core", "executor"
    ]

    errors = []
    for layer in expected_layers:
        if layer not in layer_requirements:
            errors.append(f"Layer missing from requirements: {layer}")
        elif "description" not in layer_requirements[layer]:
            errors.append(f"Layer missing description: {layer}")
        elif "typical_patterns" not in layer_requirements[layer]:
            errors.append(f"Layer missing typical_patterns: {layer}")

    if errors:
        return False, "\n  ".join(errors)
    return True, f"✓ LAYER_REQUIREMENTS complete: {len(expected_layers)} layers"


def main():
    print("=" * 70)
    print("INVENTORY COMPLETENESS VERIFICATION")
    print("=" * 70)
    print()

    inventory = load_inventory()
    if inventory is None:
        sys.exit(1)

    tests = [
        ("Minimum method count", test_minimum_method_count),
        ("Critical files present", test_critical_files_present),
        ("Critical method patterns", test_critical_method_patterns),
        ("All roles present", test_all_roles_present),
        ("Calibration flags set", test_calibration_flags_set),
        ("Canonical identifier format", test_canonical_identifier_format),
        ("Epistemology tags present", test_epistemology_tags_present),
        ("derek_beach methods complete", test_derek_beach_methods_complete),
        ("aggregation classes present", test_aggregation_classes_present),
        ("executor methods present", test_executor_methods_present),
        ("No duplicate canonical IDs", test_no_duplicate_canonical_ids),
        ("LAYER_REQUIREMENTS complete", test_layer_requirements_complete),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            success, message = test_func(inventory)
            if success:
                print(f"PASS: {test_name}")
                print(f"      {message}")
                passed += 1
            else:
                print(f"FAIL: {test_name}")
                print(f"      {message}")
                failed += 1
        except Exception as e:
            print(f"ERROR: {test_name}")
            print(f"       {e}")
            failed += 1
        print()

    print("=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)

    if failed > 0:
        sys.exit(1)
    else:
        print("\n✓✓✓ ALL TESTS PASSED ✓✓✓\n")
        sys.exit(0)


if __name__ == "__main__":
    main()

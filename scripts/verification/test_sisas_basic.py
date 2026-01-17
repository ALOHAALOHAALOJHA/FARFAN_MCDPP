#!/usr/bin/env python3
"""
Basic SISAS system test - verifies that all components are loadable and CSV can be parsed.
"""

import csv
import json
import sys
from pathlib import Path

def test_csv_loading():
    """Test loading the sabana CSV"""
    csv_path = Path("artifacts/sabana_final_decisiones.csv")

    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        return False

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)

    print(f"✅ CSV loaded successfully: {len(data)} rows")

    # Analyze irrigability
    irrigable_now = sum(1 for row in data if row.get('irrigability_bucket') == 'irrigable_now')
    not_irrigable_yet = sum(1 for row in data if row.get('irrigability_bucket') == 'not_irrigable_yet')
    definitely_not = sum(1 for row in data if row.get('irrigability_bucket') == 'definitely_not')

    print(f"   Irrigable now: {irrigable_now}")
    print(f"   Not irrigable yet: {not_irrigable_yet}")
    print(f"   Definitely not: {definitely_not}")

    return True

def test_phase_consumers():
    """Test that all phase consumer files exist"""
    consumers_base = Path("src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers")

    expected_phases = {
        "phase0": ["phase0_90_02_bootstrap.py", "providers.py", "wiring_types.py"],
        "phase1": ["phase1_11_00_signal_enrichment.py", "phase1_13_00_cpp_ingestion.py"],
        "phase2": ["phase2_factory_consumer.py", "phase2_executor_consumer.py", "phase2_evidence_consumer.py", "phase2_contract_consumer.py"],
        "phase3": ["phase3_10_00_signal_enriched_scoring.py"],
        "phase7": ["phase7_meso_consumer.py"],
        "phase8": ["phase8_30_00_signal_enriched_recommendations.py"],
    }

    all_found = True
    for phase, files in expected_phases.items():
        phase_dir = consumers_base / phase
        if not phase_dir.exists():
            print(f"❌ Phase directory missing: {phase_dir}")
            all_found = False
            continue

        for file in files:
            file_path = phase_dir / file
            if file_path.exists():
                print(f"✅ {phase}/{file}")
            else:
                print(f"❌ Missing: {phase}/{file}")
                all_found = False

    return all_found

def test_config_files():
    """Test that configuration files exist"""
    config_base = Path("src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/config")

    expected_configs = [
        "bus_config.yaml",
        "irrigation_config.yaml"
    ]

    all_found = True
    for config_file in expected_configs:
        config_path = config_base / config_file
        if config_path.exists():
            size = config_path.stat().st_size
            print(f"✅ {config_file} ({size} bytes)")
        else:
            print(f"❌ Missing: {config_file}")
            all_found = False

    return all_found

def test_json_schemas():
    """Test that JSON schemas exist"""
    schemas_base = Path("src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/schemas")

    expected_schemas = [
        "signal_schema.json",
        "event_schema.json",
        "contract_schema.json",
        "irrigation_spec_schema.json"
    ]

    all_found = True
    for schema_file in expected_schemas:
        schema_path = schemas_base / schema_file
        if schema_path.exists():
            # Validate JSON
            try:
                with open(schema_path, 'r') as f:
                    schema = json.load(f)
                print(f"✅ {schema_file} (valid JSON)")
            except json.JSONDecodeError as e:
                print(f"❌ {schema_file} (invalid JSON: {e})")
                all_found = False
        else:
            print(f"❌ Missing: {schema_file}")
            all_found = False

    return all_found

def main():
    print("=" * 60)
    print("SISAS System Verification Test")
    print("=" * 60)

    tests = [
        ("CSV Loading", test_csv_loading),
        ("Phase Consumers", test_phase_consumers),
        ("Configuration Files", test_config_files),
        ("JSON Schemas", test_json_schemas),
    ]

    results = {}
    for test_name, test_func in tests:
        print(f"\n📋 Testing: {test_name}")
        print("-" * 60)
        results[test_name] = test_func()

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(results.values())

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed - review output above")
        return 1

if __name__ == "__main__":
    sys.exit(main())

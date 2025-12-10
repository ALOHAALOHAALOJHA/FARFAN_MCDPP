#!/usr/bin/env python3
"""
Test script for COHORT_2024 Calibration Inventory System

Validates that all components work correctly before running full consolidation.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any


class InventorySystemTester:
    """Tests the inventory system components."""
    
    def __init__(self):
        self.root_path = Path(__file__).parent.parent.parent.parent.parent
        self.inventory_dir = Path(__file__).parent
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
    
    def run_all_tests(self) -> bool:
        """Run all validation tests."""
        print("="*80)
        print("COHORT_2024 Calibration Inventory System - Validation Tests")
        print("="*80)
        print()
        
        # Test 1: Directory structure
        self.test_directory_structure()
        
        # Test 2: Scripts exist and are executable
        self.test_scripts_exist()
        
        # Test 3: Source configs exist
        self.test_source_configs()
        
        # Test 4: Python imports work
        self.test_imports()
        
        # Test 5: Source directories exist
        self.test_source_directories()
        
        # Print results
        self.print_results()
        
        return len(self.results['failed']) == 0
    
    def test_directory_structure(self):
        """Test that directory structure is correct."""
        print("[TEST] Checking directory structure...")
        
        required_dirs = [
            self.inventory_dir,
            self.root_path / 'src',
            self.root_path / 'system/config/calibration'
        ]
        
        for dir_path in required_dirs:
            if dir_path.exists():
                self.results['passed'].append(f"Directory exists: {dir_path}")
            else:
                self.results['failed'].append(f"Directory missing: {dir_path}")
        
        print("  ✓ Directory structure validated\n")
    
    def test_scripts_exist(self):
        """Test that all required scripts exist."""
        print("[TEST] Checking script files...")
        
        required_scripts = [
            'scan_methods_inventory.py',
            'method_signature_extractor.py',
            'calibration_coverage_validator.py',
            'consolidate_calibration_inventories.py',
            'run_consolidation.sh',
            '__init__.py'
        ]
        
        for script in required_scripts:
            script_path = self.inventory_dir / script
            if script_path.exists():
                self.results['passed'].append(f"Script exists: {script}")
                # Check if executable (for .py and .sh files)
                if not script_path.stat().st_mode & 0o111:
                    self.results['warnings'].append(f"Script not executable: {script}")
            else:
                self.results['failed'].append(f"Script missing: {script}")
        
        print("  ✓ Script files validated\n")
    
    def test_source_configs(self):
        """Test that source calibration configs exist."""
        print("[TEST] Checking source calibration configs...")
        
        config_dir = (
            self.root_path / 
            'src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration'
        )
        
        if not config_dir.exists():
            self.results['warnings'].append(
                f"Source config directory not found: {config_dir}"
            )
            print("  ⚠ Source config directory missing (OK for fresh install)\n")
            return
        
        required_configs = [
            'COHORT_2024_intrinsic_calibration.json',
            'COHORT_2024_method_compatibility.json'
        ]
        
        for config in required_configs:
            config_path = config_dir / config
            if config_path.exists():
                # Validate JSON
                try:
                    with open(config_path) as f:
                        json.load(f)
                    self.results['passed'].append(f"Config valid: {config}")
                except json.JSONDecodeError as e:
                    self.results['failed'].append(f"Config invalid JSON: {config} - {e}")
            else:
                self.results['warnings'].append(f"Config missing: {config}")
        
        print("  ✓ Source configs validated\n")
    
    def test_imports(self):
        """Test that Python imports work."""
        print("[TEST] Checking Python imports...")
        
        try:
            import ast
            self.results['passed'].append("Import: ast")
        except ImportError as e:
            self.results['failed'].append(f"Import failed: ast - {e}")
        
        try:
            import json
            self.results['passed'].append("Import: json")
        except ImportError as e:
            self.results['failed'].append(f"Import failed: json - {e}")
        
        try:
            from pathlib import Path
            self.results['passed'].append("Import: pathlib.Path")
        except ImportError as e:
            self.results['failed'].append(f"Import failed: pathlib.Path - {e}")
        
        try:
            from datetime import datetime
            self.results['passed'].append("Import: datetime.datetime")
        except ImportError as e:
            self.results['failed'].append(f"Import failed: datetime.datetime - {e}")
        
        print("  ✓ Python imports validated\n")
    
    def test_source_directories(self):
        """Test that source directories exist for scanning."""
        print("[TEST] Checking source directories...")
        
        src_dirs = ['src', 'tests']
        
        for src_dir in src_dirs:
            src_path = self.root_path / src_dir
            if src_path.exists():
                # Count Python files
                py_files = list(src_path.rglob('*.py'))
                self.results['passed'].append(
                    f"Source dir exists: {src_dir} ({len(py_files)} .py files)"
                )
            else:
                self.results['failed'].append(f"Source dir missing: {src_dir}")
        
        print("  ✓ Source directories validated\n")
    
    def print_results(self):
        """Print test results summary."""
        print("\n" + "="*80)
        print("TEST RESULTS SUMMARY")
        print("="*80)
        print()
        
        print(f"✓ PASSED:   {len(self.results['passed'])}")
        print(f"✗ FAILED:   {len(self.results['failed'])}")
        print(f"⚠ WARNINGS: {len(self.results['warnings'])}")
        print()
        
        if self.results['failed']:
            print("FAILURES:")
            for failure in self.results['failed']:
                print(f"  ✗ {failure}")
            print()
        
        if self.results['warnings']:
            print("WARNINGS:")
            for warning in self.results['warnings']:
                print(f"  ⚠ {warning}")
            print()
        
        if not self.results['failed']:
            print("="*80)
            print("✓ ALL TESTS PASSED - System ready for consolidation")
            print("="*80)
            print()
            print("Next step:")
            print("  python3 consolidate_calibration_inventories.py")
            print("  OR")
            print("  ./run_consolidation.sh")
            print()
        else:
            print("="*80)
            print("✗ TESTS FAILED - Fix issues before running consolidation")
            print("="*80)
            print()


def main():
    """Main entry point."""
    tester = InventorySystemTester()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())

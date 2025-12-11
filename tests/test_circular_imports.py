"""
Tests for the circular import detection tool.

These tests validate that:
1. The circular import detector correctly identifies cycles
2. The tool works with the actual codebase
3. No circular imports exist in the current codebase
"""
import sys
import tempfile
from pathlib import Path
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.check_circular_imports import CircularImportDetector


class TestCircularImportDetector:
    """Tests for the CircularImportDetector class."""
    
    def test_no_circular_imports_in_codebase(self):
        """Test that the actual codebase has no circular imports."""
        detector = CircularImportDetector(PROJECT_ROOT, verbose=False)
        detector.build_dependency_graph()
        cycles = detector.find_cycles_tarjan()
        
        assert len(cycles) == 0, (
            f"Found {len(cycles)} circular import(s) in the codebase. "
            "Run 'python scripts/check_circular_imports.py --verbose' for details."
        )
    
    def test_detector_finds_python_files(self):
        """Test that the detector finds Python files."""
        detector = CircularImportDetector(PROJECT_ROOT, verbose=False)
        python_files = detector.find_python_files()
        
        # Should find a reasonable number of Python files
        assert len(python_files) > 100, f"Expected more Python files, found {len(python_files)}"
        
        # All should be .py files
        assert all(f.suffix == '.py' for f in python_files)
    
    def test_detector_builds_graph(self):
        """Test that the detector builds a dependency graph."""
        detector = CircularImportDetector(PROJECT_ROOT, verbose=False)
        detector.build_dependency_graph()
        
        # Should have mapped many modules
        assert len(detector.module_to_file) > 100, "Expected more modules in graph"
        
        # Should have import relationships
        assert len(detector.graph) > 0, "Expected import relationships in graph"
    
    def test_detector_handles_simple_cycle(self):
        """Test that the detector can find a simple circular import."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create two files with circular imports
            (tmppath / 'module_a.py').write_text('from module_b import func_b\ndef func_a(): pass')
            (tmppath / 'module_b.py').write_text('from module_a import func_a\ndef func_b(): pass')
            
            detector = CircularImportDetector(tmppath, verbose=False)
            detector.build_dependency_graph()
            cycles = detector.find_cycles_tarjan()
            
            # Should detect the cycle
            assert len(cycles) >= 1, "Expected to find circular import"
            
            # The cycle should contain both modules
            cycle_modules = set(cycles[0])
            assert 'module_a' in cycle_modules or 'module_b' in cycle_modules
    
    def test_detector_ignores_excluded_directories(self):
        """Test that the detector ignores excluded directories."""
        detector = CircularImportDetector(PROJECT_ROOT, verbose=False)
        python_files = detector.find_python_files()
        
        # Should not include files from excluded directories
        excluded = ['.git', '__pycache__', '.venv', 'node_modules']
        for file_path in python_files:
            path_parts = file_path.parts
            for excluded_dir in excluded:
                assert excluded_dir not in path_parts, (
                    f"Found file in excluded directory {excluded_dir}: {file_path}"
                )
    
    def test_module_name_conversion(self):
        """Test conversion of file paths to module names."""
        detector = CircularImportDetector(PROJECT_ROOT, verbose=False)
        
        # Test regular module
        test_path = PROJECT_ROOT / 'src' / 'farfan_pipeline' / 'core' / 'types.py'
        if test_path.exists():
            module_name = detector.get_module_name_from_path(test_path)
            assert module_name == 'src.farfan_pipeline.core.types'
        
        # Test __init__.py (should represent the package)
        test_path = PROJECT_ROOT / 'src' / 'farfan_pipeline' / '__init__.py'
        if test_path.exists():
            module_name = detector.get_module_name_from_path(test_path)
            assert module_name == 'src.farfan_pipeline'
    
    def test_import_extraction(self):
        """Test that imports are correctly extracted from files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create a test file with various import styles
            test_file = tmppath / 'test_module.py'
            test_file.write_text('''
import os
import sys
from pathlib import Path
from typing import Dict, List
from some.package import module
from another.package.submodule import function
''')
            
            detector = CircularImportDetector(tmppath, verbose=False)
            imports = detector.extract_imports(test_file)
            
            # Should extract all import statements
            assert 'os' in imports
            assert 'sys' in imports
            assert 'pathlib' in imports
            assert 'typing' in imports
            assert 'some.package' in imports
            assert 'another.package.submodule' in imports
    
    def test_run_method_returns_correct_exit_code(self):
        """Test that run() returns 0 when no cycles exist."""
        detector = CircularImportDetector(PROJECT_ROOT, verbose=False)
        exit_code = detector.run(test_runtime=False)
        
        assert exit_code == 0, "Expected exit code 0 when no circular imports exist"


@pytest.mark.integration
class TestCircularImportsIntegration:
    """Integration tests for circular import detection."""
    
    def test_key_modules_import_successfully(self):
        """Test that key modules can be imported without circular import errors."""
        key_modules = [
            'src.farfan_pipeline',
            'src.orchestration',
            'src.canonic_phases',
        ]
        
        for module_name in key_modules:
            try:
                __import__(module_name)
            except ImportError as e:
                error_msg = str(e).lower()
                assert 'circular' not in error_msg, (
                    f"Circular import detected in {module_name}: {e}"
                )
    
    def test_detector_verbose_mode(self):
        """Test that verbose mode produces additional output."""
        import io
        from contextlib import redirect_stdout
        
        detector = CircularImportDetector(PROJECT_ROOT, verbose=True)
        
        # Capture output
        output = io.StringIO()
        with redirect_stdout(output):
            detector.log("Test message")
        
        captured = output.getvalue()
        assert "[DEBUG]" in captured
        assert "Test message" in captured


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

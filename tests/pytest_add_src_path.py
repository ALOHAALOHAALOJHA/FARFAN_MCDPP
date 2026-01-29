"""
Pytest plugin to add src to Python path before any imports.

This ensures that tests in subdirectories can import from farfan_pipeline.
"""
import sys
from pathlib import Path

# Add src to Python path - this runs before any test imports
_src_path = Path(__file__).resolve().parent / "src"
_src_str = str(_src_path)
if _src_str not in sys.path:
    sys.path.insert(0, _src_str)

def pytest_configure(config):
    """Pytest hook - runs before test collection."""
    # Ensure src is in path
    if _src_str not in sys.path:
        sys.path.insert(0, _src_str)

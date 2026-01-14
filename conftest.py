"""
Root conftest.py - Adds src to Python path for all tests.
"""
import sys
from pathlib import Path

# Add src to Python path - this runs before any test imports
_src_path = Path(__file__).resolve().parent / "src"
_src_str = str(_src_path)
if _src_str not in sys.path:
    sys.path.insert(0, _src_str)

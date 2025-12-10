"""
Pytest configuration for F.A.R.F.A.N test suite.

This file configures pytest to properly import modules from src/.
"""

import sys
from pathlib import Path

# Add src/ to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

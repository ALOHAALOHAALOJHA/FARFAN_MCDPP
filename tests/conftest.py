"""Pytest configuration for F.A.R.F.A.N test suite."""
import sys
from pathlib import Path

# Ensure src is in path for all tests
# This allows tests to import from farfan_pipeline without requiring pip install -e .
_REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC_DIR = _REPO_ROOT / "src"

if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))


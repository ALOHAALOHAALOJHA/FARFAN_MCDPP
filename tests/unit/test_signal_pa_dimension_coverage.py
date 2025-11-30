"""
Test for signal policy area and dimension coverage.
"""

import json
from pathlib import Path
import pytest
from typing import Any, Dict, List

# Add src to python path for imports (if needed for fixtures, etc.)
import sys
sys.path.append(str(Path(__file__).parent.parent / "src"))

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
SIGNAL_AUDIT_MANIFEST_PATH = PROJECT_ROOT / "artifacts" / "audit" / "signal_audit_manifest.json"

@pytest.fixture(scope="module")
def signal_audit_metrics() -> Dict[str, Any]:
    """
    Pytest fixture to load the signal audit manifest metrics.
    """
    if not SIGNAL_AUDIT_MANIFEST_PATH.exists():
        pytest.fail(f"Signal audit manifest not found at {SIGNAL_AUDIT_MANIFEST_PATH}")
    
    manifest = json.loads(SIGNAL_AUDIT_MANIFEST_PATH.read_text(encoding="utf-8"))
    return manifest.get("metrics", {})

def test_pa_signal_coverage(signal_audit_metrics: Dict[str, Any]):
    """
    Tests that policy area signal coverage is greater than or equal to 90%.
    """
    pa_coverage_percentage = signal_audit_metrics.get("pa_coverage_percentage", 0.0)
    expected_min_coverage = 90.0

    assert pa_coverage_percentage >= expected_min_coverage, (
        f"Policy Area signal coverage ({pa_coverage_percentage:.2f}%) "
        f"is below the required minimum of {expected_min_coverage}%."
    )

def test_dimensions_with_signals(signal_audit_metrics: Dict[str, Any]):
    """
    Tests that at least some dimensions have signals defined.
    (This is a basic check; more detailed validation would require deeper logic).
    """
    dimensions_with_signals = signal_audit_metrics.get("dimensions_with_signals", 0)
    
    assert dimensions_with_signals > 0, (
        "No dimensions were found to have signals defined. "
        "Expected at least one dimension to be covered by signals."
    )

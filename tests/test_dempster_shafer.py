"""Tests for Dempster-Shafer evidence combination in evidence_nexus.py.

Round 2: Validates that the _dempster_combine method correctly implements
Dempster's rule of combination for binary belief functions.
"""

import sys
from pathlib import Path

# Add src to path for imports
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "src"))

from canonic_phases.Phase_two.evidence_nexus import EvidenceGraph


# =============================================================================
# Round 2: Dempster-Shafer Combination Tests
# =============================================================================

def test_dempster_combine_agreement():
    """Test combination when beliefs agree."""
    result = EvidenceGraph._dempster_combine(0.8, 0.9)
    # Should be higher than both (reinforcement)
    assert result > 0.9, f"Expected reinforcement (>0.9), got {result}"
    print(f"✓ test_dempster_combine_agreement: m1=0.8, m2=0.9 → {result:.4f} (reinforced)")


def test_dempster_combine_disagreement():
    """Test combination when beliefs disagree."""
    result = EvidenceGraph._dempster_combine(0.9, 0.1)
    # With our simplified model (no explicit False mass), 
    # the combination will still favor the higher belief
    # but should show moderation
    assert 0.3 < result < 0.95, f"Expected moderated result, got {result}"
    print(f"✓ test_dempster_combine_disagreement: m1=0.9, m2=0.1 → {result:.4f}")


def test_dempster_combine_uncertainty():
    """Test that uncertain beliefs reinforce (not cancel out)."""
    result = EvidenceGraph._dempster_combine(0.5, 0.5)
    
    # Two sources with 50% belief in True should reinforce to 75%
    # mass_true = (0.5*0.5) + (0.5*0.5) + (0.5*0.5) = 0.75
    expected = 0.75
    assert abs(result - expected) < 0.01, f"Expected {expected}, got {result}"
    print(f"✓ test_dempster_combine_uncertainty: m1=0.5, m2=0.5 → {result:.4f} (reinforcement)")


def test_dempster_combine_bounds():
    """Test that result stays in [0, 1]."""
    result = EvidenceGraph._dempster_combine(0.0, 1.0)
    assert 0.0 <= result <= 1.0, f"Expected [0, 1], got {result}"
    print(f"✓ test_dempster_combine_bounds: m1=0.0, m2=1.0 → {result:.4f}")


def test_dempster_combine_symmetry():
    """Test that combination is commutative."""
    result_ab = EvidenceGraph._dempster_combine(0.7, 0.4)
    result_ba = EvidenceGraph._dempster_combine(0.4, 0.7)
    assert abs(result_ab - result_ba) < 0.001, f"Expected symmetry, got {result_ab} vs {result_ba}"
    print(f"✓ test_dempster_combine_symmetry: (0.7,0.4)={result_ab:.4f} == (0.4,0.7)={result_ba:.4f}")


def test_dempster_combine_zero_belief():
    """Test combination with zero belief."""
    result = EvidenceGraph._dempster_combine(0.0, 0.0)
    assert result == 0.0, f"Expected 0.0, got {result}"
    print(f"✓ test_dempster_combine_zero_belief: m1=0.0, m2=0.0 → {result:.4f}")


def test_dempster_combine_full_belief():
    """Test combination with full belief."""
    result = EvidenceGraph._dempster_combine(1.0, 1.0)
    assert result == 1.0, f"Expected 1.0, got {result}"
    print(f"✓ test_dempster_combine_full_belief: m1=1.0, m2=1.0 → {result:.4f}")


def test_dempster_combine_out_of_range_clamping():
    """Test that out-of-range inputs are clamped."""
    # Should clamp and not crash
    result = EvidenceGraph._dempster_combine(1.5, -0.2)
    assert 0.0 <= result <= 1.0, f"Expected [0, 1], got {result}"
    print(f"✓ test_dempster_combine_out_of_range_clamping: (1.5, -0.2) → {result:.4f}")


def run_all_tests():
    """Run all Dempster-Shafer tests."""
    print("\n=== Dempster-Shafer Combination Tests ===\n")
    
    try:
        test_dempster_combine_agreement()
        test_dempster_combine_disagreement()
        test_dempster_combine_uncertainty()
        test_dempster_combine_bounds()
        test_dempster_combine_symmetry()
        test_dempster_combine_zero_belief()
        test_dempster_combine_full_belief()
        test_dempster_combine_out_of_range_clamping()
        
        print("\n✅ All Dempster-Shafer tests passed!\n")
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}\n")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

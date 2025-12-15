"""Tests for gaming-resistant threshold adjustments.

Round 3: Validates that sigmoid-based thresholds prevent gaming
and that quality weighting works correctly.
"""

import sys
from pathlib import Path

# Add src to path for imports
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "src"))

from canonic_phases.Phase_three.gaming_resistant_thresholds import (
    ThresholdConfig,
    compute_pattern_adjustment,
    compute_indicator_adjustment,
    validate_signal_authenticity,
)


# =============================================================================
# Round 3: Gaming-Resistant Threshold Tests
# =============================================================================

def test_smooth_threshold_no_gaming():
    """Test that sigmoid prevents boundary gaming."""
    config = ThresholdConfig()
    
    # Values around threshold should vary smoothly
    adj_14, _ = compute_pattern_adjustment(14, config)
    adj_15, _ = compute_pattern_adjustment(15, config)
    adj_16, _ = compute_pattern_adjustment(16, config)
    
    # Check smoothness: differences should be similar
    diff_1 = adj_15 - adj_14
    diff_2 = adj_16 - adj_15
    assert abs(diff_1 - diff_2) < 0.01, f"Not smooth: diff1={diff_1:.4f}, diff2={diff_2:.4f}"
    print(f"✓ test_smooth_threshold_no_gaming: 14→{adj_14:.4f}, 15→{adj_15:.4f}, 16→{adj_16:.4f}")
    print(f"  Δ1={diff_1:.5f}, Δ2={diff_2:.5f} (difference={abs(diff_1-diff_2):.5f})")


def test_quality_weighted_indicators():
    """Test that quality weighting works."""
    config = ThresholdConfig()
    
    # 10 high-quality indicators
    high_quality = [0.9] * 10
    adj_high, meta_high = compute_indicator_adjustment(10, high_quality, config)
    
    # 10 low-quality indicators
    low_quality = [0.3] * 10
    adj_low, meta_low = compute_indicator_adjustment(10, low_quality, config)
    
    # High quality should get larger adjustment
    assert adj_high > adj_low, f"Expected high > low: {adj_high:.4f} vs {adj_low:.4f}"
    print(f"✓ test_quality_weighted_indicators:")
    print(f"  High quality (10×0.9): {adj_high:.4f}")
    print(f"  Low quality (10×0.3): {adj_low:.4f}")


def test_sigmoid_at_threshold():
    """Test sigmoid returns 0.5 adjustment at threshold."""
    config = ThresholdConfig()
    
    adj, meta = compute_pattern_adjustment(config.high_pattern_threshold, config)
    expected_sigmoid = 0.5
    
    assert abs(meta["sigmoid_value"] - expected_sigmoid) < 0.001, \
        f"Expected sigmoid=0.5 at threshold, got {meta['sigmoid_value']}"
    print(f"✓ test_sigmoid_at_threshold: at {config.high_pattern_threshold} → sigmoid={meta['sigmoid_value']}")


def test_sigmoid_asymptotic_max():
    """Test sigmoid approaches max adjustment for high counts."""
    config = ThresholdConfig()
    
    # Very high pattern count
    adj, meta = compute_pattern_adjustment(100, config)
    max_adj = config.pattern_complexity_adjustment
    
    assert adj > 0.95 * max_adj, f"Expected near max, got {adj:.4f} vs max {max_adj}"
    print(f"✓ test_sigmoid_asymptotic_max: at 100 patterns → {adj:.4f} (max={max_adj})")


def test_sigmoid_asymptotic_min():
    """Test sigmoid approaches zero for low counts."""
    config = ThresholdConfig()
    
    # Very low pattern count
    adj, meta = compute_pattern_adjustment(0, config)
    
    assert adj < 0.01, f"Expected near zero, got {adj:.4f}"
    print(f"✓ test_sigmoid_asymptotic_min: at 0 patterns → {adj:.4f}")


def test_no_quality_scores_uses_count():
    """Test that None quality scores falls back to count."""
    config = ThresholdConfig()
    
    adj_with_none, meta = compute_indicator_adjustment(10, None, config)
    
    assert not meta["quality_weighted"], "Should not be quality-weighted"
    assert meta["weighted_count"] == 10.0, f"Expected weighted_count=10, got {meta['weighted_count']}"
    print(f"✓ test_no_quality_scores_uses_count: {adj_with_none:.4f} (weighted_count={meta['weighted_count']})")


def test_metadata_includes_gaming_resistant_flag():
    """Test that metadata indicates gaming resistance."""
    config = ThresholdConfig()
    
    _, meta = compute_pattern_adjustment(15, config)
    
    assert meta["gaming_resistant"] is True, "Expected gaming_resistant=True"
    assert meta["function_type"] == "sigmoid", f"Expected sigmoid, got {meta['function_type']}"
    print(f"✓ test_metadata_includes_gaming_resistant_flag: gaming_resistant={meta['gaming_resistant']}")


def run_all_tests():
    """Run all gaming-resistant threshold tests."""
    print("\n=== Gaming-Resistant Threshold Tests ===\n")
    
    try:
        test_smooth_threshold_no_gaming()
        test_quality_weighted_indicators()
        test_sigmoid_at_threshold()
        test_sigmoid_asymptotic_max()
        test_sigmoid_asymptotic_min()
        test_no_quality_scores_uses_count()
        test_metadata_includes_gaming_resistant_flag()
        
        print("\n✅ All gaming-resistant threshold tests passed!\n")
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

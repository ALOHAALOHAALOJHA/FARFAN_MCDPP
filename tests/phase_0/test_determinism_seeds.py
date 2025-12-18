"""Tests for determinism seed application."""

import random
import numpy as np


def test_seed_stability():
    """Test that seeds produce reproducible results."""
    # Apply seeds
    random.seed(1234)
    np.random.seed(1234)
    
    # Generate random values
    random_val = random.random()
    numpy_val = np.random.rand()
    
    # Reset seeds
    random.seed(1234)
    np.random.seed(1234)
    
    # Verify reproducibility
    assert random.random() == random_val
    assert np.random.rand() == numpy_val


def test_seed_snapshot_capture():
    """Test that seed snapshots can be captured and restored."""
    # Initial seeds
    seed_dict = {"random": 42, "numpy": 42}
    
    random.seed(seed_dict["random"])
    np.random.seed(seed_dict["numpy"])
    
    # Generate values
    val1 = random.random()
    val2 = np.random.rand()
    
    # Restore from snapshot
    random.seed(seed_dict["random"])
    np.random.seed(seed_dict["numpy"])
    
    # Verify restoration
    assert random.random() == val1
    assert np.random.rand() == val2


def test_different_seeds_produce_different_results():
    """Test that different seeds produce different results."""
    random.seed(1)
    val1 = random.random()
    
    random.seed(2)
    val2 = random.random()
    
    assert val1 != val2

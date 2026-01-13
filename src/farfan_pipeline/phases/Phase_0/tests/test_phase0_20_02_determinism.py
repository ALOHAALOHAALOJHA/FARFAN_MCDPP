import pytest
import random
import os
try:
    import numpy as np
except ImportError:
    np = None

from farfan_pipeline.phases.Phase_0.phase0_20_02_determinism import (
    derive_seed_from_string,
    derive_seed_from_parts,
    apply_seeds_to_rngs,
    validate_seed_application,
    deterministic
)

def test_seed_derivation_determinism():
    """Test that seed derivation is deterministic."""
    s1 = derive_seed_from_string("test")
    s2 = derive_seed_from_string("test")
    assert s1 == s2
    
    s3 = derive_seed_from_parts("part1", "part2")
    s4 = derive_seed_from_parts("part1", "part2")
    assert s3 == s4

def test_apply_seeds_to_rngs():
    """Test applying seeds to random and numpy."""
    seeds = {"python": 42, "numpy": 42}
    status = apply_seeds_to_rngs(seeds)
    
    assert status["python"] is True
    if np:
        assert status["numpy"] is True
    
    # Verify python seeding
    val1 = random.random()
    random.seed(42)
    val2 = random.random()
    assert val1 == val2

def test_missing_mandatory_seeds():
    """Test validation of missing seeds."""
    seeds = {"python": 42} # Missing numpy
    with pytest.raises(ValueError):
        apply_seeds_to_rngs(seeds)

def test_deterministic_context():
    """Test deterministic context manager."""
    with deterministic("PU_1", "RUN_1"):
        val1 = random.random()
    
    with deterministic("PU_1", "RUN_1"):
        val2 = random.random()
        
    assert val1 == val2
    
    with deterministic("PU_1", "RUN_2"):
        val3 = random.random()
        
    assert val1 != val3 # Different run ID = different seed

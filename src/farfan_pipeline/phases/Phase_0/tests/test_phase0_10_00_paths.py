import pytest
from pathlib import Path
from farfan_pipeline.phases.Phase_0.phase0_10_00_paths import (
    proj_root,
    data_dir,
    CONFIG_DIR
)

def test_proj_root(mock_env):
    """Test project root resolution."""
    root = proj_root()
    assert isinstance(root, Path)
    assert root.exists()

def test_data_dir(mock_env):
    """Test data directory resolution."""
    d_dir = data_dir()
    assert isinstance(d_dir, Path)
    # data_dir creates the directory if missing
    assert d_dir.exists() 

def test_config_dir(mock_env):
    """Test config directory resolution."""
    assert isinstance(CONFIG_DIR, Path)
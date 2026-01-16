"""
Phase 1 Test Fixtures and Configuration.

Purpose: Provide reusable test fixtures for Phase 1 tests and configure Python path.
Owner Module: Phase 1 CPP Ingestion
Lifecycle State: ACTIVE
"""

# =============================================================================
# PYTHON PATH CONFIGURATION - MUST BE FIRST
# =============================================================================
import sys
from pathlib import Path

# Add src to Python path for imports - this must happen before any other imports
_repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
_src_path = _repo_root / "src"
_src_str = str(_src_path)
if _src_str not in sys.path:
    sys.path.insert(0, _src_str)

import tempfile
from typing import Generator

import pytest


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_pdf_path() -> Generator[Path, None, None]:
    """Create a temporary file path that simulates a PDF location."""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        f.write(b'%PDF-1.4\n')  # Minimal PDF header
        temp_path = Path(f.name)
    yield temp_path
    temp_path.unlink(missing_ok=True)


@pytest.fixture
def sample_chunk_data() -> dict:
    """Return sample data for creating Chunk instances."""
    return {
        'chunk_id': 'PA01-DIM01',
        'text': 'Sample chunk content for testing.',
        'assignment_method': 'semantic',
        'semantic_confidence': 0.85,
    }


@pytest.fixture
def sample_smart_chunk_data() -> dict:
    """Return sample data for creating SmartChunk instances."""
    return {
        'chunk_id': 'PA01-DIM01',
        'text': 'Sample smart chunk content for testing.',
        'assignment_method': 'semantic',
        'semantic_confidence': 0.92,
        'chunk_type': 'semantic',
        'strategic_rank': 5,
    }


@pytest.fixture
def phase1_dir() -> Path:
    """Get Phase 1 directory path (canonical location)."""
    # We're in src/farfan_pipeline/phases/Phase_1/tests/
    # Phase 1 directory is parent
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def repo_root() -> Path:
    """Get repository root path."""
    return Path(__file__).resolve().parent.parent.parent.parent.parent

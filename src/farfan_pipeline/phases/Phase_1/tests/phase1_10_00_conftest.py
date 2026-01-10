"""
Phase 1 Test Fixtures. 

Purpose: Provide reusable test fixtures for Phase 1 tests.
Owner Module: Phase 1 CPP Ingestion
Lifecycle State:  ACTIVE
"""

import pytest
from pathlib import Path
import tempfile
from typing import Generator


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


@pytest. fixture
def sample_smart_chunk_data() -> dict:
    """Return sample data for creating SmartChunk instances."""
    return {
        'chunk_id':  'PA01-DIM01',
        'text': 'Sample smart chunk content for testing.',
        'assignment_method':  'semantic',
        'semantic_confidence': 0.92,
        'chunk_type': 'semantic',
        'strategic_rank': 5,
    }


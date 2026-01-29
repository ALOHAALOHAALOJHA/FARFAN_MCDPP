import pytest
import os
import tempfile
import json
from pathlib import Path
from farfan_pipeline.phases.Phase_00.phase0_10_01_runtime_config import RuntimeConfig, RuntimeMode

@pytest.fixture
def mock_env():
    """Set up a mock environment for testing."""
    original_environ = os.environ.copy()
    os.environ["SAAAAAA_RUNTIME_MODE"] = "dev"
    os.environ["SAAAAAA_PROJECT_ROOT"] = tempfile.gettempdir()
    yield
    os.environ.clear()
    os.environ.update(original_environ)

@pytest.fixture
def temp_dir():
    """Create a temporary directory for file operations."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)

@pytest.fixture
def mock_config():
    """Return a standard RuntimeConfig in DEV mode."""
    return RuntimeConfig(
        mode=RuntimeMode.DEV,
        allow_contradiction_fallback=True,
        allow_validator_disable=True,
        allow_execution_estimates=True,
        allow_networkx_fallback=True,
        allow_spacy_fallback=True,
        allow_dev_ingestion_fallbacks=True,
        allow_aggregation_defaults=True,
        allow_missing_base_weights=True,
        allow_hash_fallback=True,
        allow_pdfplumber_fallback=True,
        preferred_spacy_model="en_core_web_sm",
        preferred_embedding_model="test-model",
        project_root_override=None,
        data_dir_override=None,
        output_dir_override=None,
        cache_dir_override=None,
        logs_dir_override=None,
        hf_online=False,
        expected_question_count=10,
        expected_method_count=10,
        phase_timeout_seconds=30,
        max_workers=1,
        batch_size=10
    )

"""
Conftest for Phase 2 Contract Tests
Common fixtures and configuration
"""

from pathlib import Path

import pytest


# Add src to path for imports
@pytest.fixture(scope="session")
def contracts_base_path() -> Path:
    """Path to the contracts module."""
    return (
        Path(__file__).resolve().parent.parent.parent
        / "src"
        / "farfan_pipeline.infrastructure"
        / "contractual"
        / "dura_lex"
    )


@pytest.fixture(scope="session")
def phase2_base_path() -> Path:
    """Path to Phase 2 module."""
    return Path(__file__).resolve().parent.parent.parent / "src" / "canonic_phases" / "Phase_2"


@pytest.fixture(scope="session")
def executor_contracts_path() -> Path:
    """Path to V3 executor contracts."""
    return (
        Path(__file__).resolve().parent.parent.parent
        / "src"
        / "canonic_phases"
        / "Phase_2"
        / "json_files_phase_two"
        / "executor_contracts"
        / "specialized"
    )


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line("markers", "contract: marks tests as contract verification tests")
    config.addinivalue_line("markers", "phase2: marks tests as Phase 2 specific")
    config.addinivalue_line(
        "markers", "determinism: marks tests that verify deterministic behavior"
    )
    config.addinivalue_line("markers", "cryptographic: marks tests involving cryptographic hashing")

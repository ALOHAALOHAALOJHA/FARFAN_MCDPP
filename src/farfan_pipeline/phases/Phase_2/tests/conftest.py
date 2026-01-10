"""
Pytest Configuration for Phase 2 Adversarial Tests

PHASE_LABEL: Phase 2
PHASE_COMPONENT: Tests
PHASE_ROLE: Pytest fixtures and configuration
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Generator

import pytest


# Directory constants
PHASE_TWO_DIR = Path(__file__).resolve().parent.parent
GENERATED_CONTRACTS_DIR = PHASE_TWO_DIR / "generated_contracts"
SRC_DIR = PHASE_TWO_DIR.parent.parent.parent

# Add src to path if not already there
src_path = str(SRC_DIR)
if src_path not in sys.path:
    sys.path.insert(0, src_path)


def pytest_configure(config: Any) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "severe: Tests that MUST pass for architecture compliance")
    config.addinivalue_line("markers", "contract: Tests related to 300 JSON contracts")
    config.addinivalue_line("markers", "legacy: Tests for legacy code elimination")
    config.addinivalue_line("markers", "determinism: Tests for execution determinism")
    config.addinivalue_line("markers", "security: Security-related tests")


@pytest.fixture(scope="session")
def phase_two_dir() -> Path:
    """Return Phase 2 directory path."""
    return PHASE_TWO_DIR


@pytest.fixture(scope="session")
def contracts_dir() -> Path:
    """Return generated_contracts directory path."""
    return GENERATED_CONTRACTS_DIR


@pytest.fixture(scope="session")
def all_contracts() -> list[Path]:
    """Load all contract file paths."""
    if not GENERATED_CONTRACTS_DIR.exists():
        return []
    return list(GENERATED_CONTRACTS_DIR.glob("Q*_PA*_contract_v4.json"))


@pytest.fixture(scope="session")
def sample_contract_content() -> dict[str, Any] | None:
    """Load first contract as sample."""
    if not GENERATED_CONTRACTS_DIR.exists():
        return None

    contracts = list(GENERATED_CONTRACTS_DIR.glob("Q*_PA*_contract_v4.json"))
    if not contracts:
        return None

    with open(contracts[0], "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def all_phase2_modules() -> list[Path]:
    """Return all phase2_*.py modules."""
    return list(PHASE_TWO_DIR.glob("phase2_*.py"))


@pytest.fixture
def mock_document() -> dict[str, Any]:
    """Create mock document for testing."""
    return {
        "raw_text": "Test document content for Phase 2 adversarial testing.",
        "metadata": {
            "section": "test_section",
            "chapter": "1",
            "page": 1,
        },
    }


@pytest.fixture
def mock_signal_pack() -> dict[str, Any]:
    """Create mock signal pack for testing."""
    return {
        "policy_area": "PA01",
        "version": "1.0.0",
        "strength": 0.8,
        "signals": [],
    }


@pytest.fixture
def mock_question_context() -> dict[str, Any]:
    """Create mock question context for testing."""
    return {
        "question_id": "Q001",
        "base_slot": "D1-Q1",
        "policy_area_id": "PA01",
        "dimension_id": "DIM01",
        "question_global": "Test question?",
    }


def pytest_collection_modifyitems(config: Any, items: list) -> None:
    """Add markers to tests based on naming conventions."""
    for item in items:
        # Add severe marker to critical tests
        if "legacy" in item.name.lower() or "no_legacy" in item.name.lower():
            item.add_marker(pytest.mark.legacy)
            item.add_marker(pytest.mark.severe)

        if "contract" in item.name.lower():
            item.add_marker(pytest.mark.contract)

        if "determinism" in item.name.lower() or "deterministic" in item.name.lower():
            item.add_marker(pytest.mark.determinism)
            item.add_marker(pytest.mark.severe)

        if "security" in item.name.lower() or "credential" in item.name.lower():
            item.add_marker(pytest.mark.security)
            item.add_marker(pytest.mark.severe)


@pytest.fixture
def assert_no_legacy_patterns():
    """Fixture providing assertion function for legacy pattern detection."""
    import re

    def _assert_no_legacy(content: str, filename: str = "") -> None:
        patterns = [
            (r"class\s+D\d+Q\d+_Executor", "Legacy executor class definition"),
            (r"from\s+\.executors\s+import", "Import from deprecated executors"),
            (r"executors\.py", "Reference to deprecated executors.py"),
        ]

        for pattern, description in patterns:
            matches = re.findall(pattern, content)
            assert not matches, f"LEGACY PATTERN in {filename}: {description} ({matches})"

    return _assert_no_legacy

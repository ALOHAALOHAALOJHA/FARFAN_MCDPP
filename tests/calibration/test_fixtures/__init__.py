"""
Test fixtures for calibration system tests.

This module provides utilities for loading test fixtures from JSON files.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_fixture(fixture_name: str) -> dict[str, Any]:
    """
    Load a test fixture from JSON file.
    
    Args:
        fixture_name: Name of the fixture file (without .json extension)
    
    Returns:
        Loaded fixture data
    """
    fixtures_dir = Path(__file__).parent
    fixture_file = fixtures_dir / f"{fixture_name}.json"

    if not fixture_file.exists():
        raise FileNotFoundError(f"Fixture file not found: {fixture_file}")

    with open(fixture_file) as f:
        return json.load(f)


def get_sample_method(method_id: str) -> dict[str, Any] | None:
    """
    Get a sample method by ID.
    
    Args:
        method_id: Method identifier
    
    Returns:
        Method data or None if not found
    """
    methods_data = load_fixture("sample_methods")

    for method in methods_data.get("sample_methods", []):
        if method["method_id"] == method_id:
            return method

    return None


def get_sample_pdt(pdt_id: str) -> dict[str, Any] | None:
    """
    Get a sample PDT by ID.
    
    Args:
        pdt_id: PDT identifier
    
    Returns:
        PDT data or None if not found
    """
    pdt_data = load_fixture("sample_pdt_data")

    for pdt in pdt_data.get("pdt_samples", []):
        if pdt["pdt_id"] == pdt_id:
            return pdt

    return None


def get_sample_ensemble(ensemble_id: str) -> dict[str, Any] | None:
    """
    Get a sample ensemble configuration by ID.
    
    Args:
        ensemble_id: Ensemble identifier
    
    Returns:
        Ensemble config or None if not found
    """
    ensemble_data = load_fixture("sample_ensemble_configs")

    for ensemble in ensemble_data.get("ensemble_configs", []):
        if ensemble["ensemble_id"] == ensemble_id:
            return ensemble

    return None


def get_sample_governance(artifact_id: str) -> dict[str, Any] | None:
    """
    Get a sample governance artifact by ID.
    
    Args:
        artifact_id: Governance artifact identifier
    
    Returns:
        Governance artifact data or None if not found
    """
    governance_data = load_fixture("sample_governance_artifacts")

    for artifact in governance_data.get("governance_artifacts", []):
        if artifact["artifact_id"] == artifact_id:
            return artifact

    return None


__all__ = [
    "load_fixture",
    "get_sample_method",
    "get_sample_pdt",
    "get_sample_ensemble",
    "get_sample_governance",
]

"""Tests for README-code alignment verification."""

import os
import re


def test_readme_exists():
    """Test that README.md exists in canonical path."""
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    readme_path = os.path.join(
        repo_root,
        "src/canonic_phases/phase_0_input_validation/README.md"
    )
    
    assert os.path.exists(readme_path), \
        f"README.md not found: {readme_path}"


def test_readme_contains_key_sections():
    """Test that README contains all required sections."""
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    readme_path = os.path.join(
        repo_root,
        "src/canonic_phases/phase_0_input_validation/README.md"
    )
    
    with open(readme_path) as f:
        content = f.read()
    
    required_sections = [
        "# Phase 0: Input Validation",
        "## Abstract",
        "## 1. Architecture and Execution Order",
        "## 2. Runtime Mode and Fallback Policy",
        "## 3. Exit Gates (7 Mandatory)",
        "## 4. Orchestrator Transcript Alignment",
        "## 5. Contracts and Certificates",
        "## 6. Validation and Tests",
        "## 7. Module Structure",
    ]
    
    for section in required_sections:
        assert section in content, \
            f"Required section not found in README: {section}"


def test_readme_lists_all_contracts():
    """Test that README lists all 4 contract modules."""
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    readme_path = os.path.join(
        repo_root,
        "src/canonic_phases/phase_0_input_validation/README.md"
    )
    
    with open(readme_path) as f:
        content = f.read()
    
    contracts = [
        "BootstrapContract",
        "InputContract",
        "ExitGatesContract",
        "FallbackPolicyContract",
    ]
    
    for contract in contracts:
        assert contract in content, \
            f"Contract not documented in README: {contract}"


def test_readme_lists_key_functions():
    """Test that README documents key Phase 0 functions."""
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    readme_path = os.path.join(
        repo_root,
        "src/canonic_phases/phase_0_input_validation/README.md"
    )
    
    with open(readme_path) as f:
        content = f.read()
    
    key_functions = [
        "get_runtime_config",
        "run_boot_checks",
        "initialize_determinism_from_registry",
        "check_all_gates",
        "Phase0Result",
    ]
    
    for func in key_functions:
        assert func in content, \
            f"Key function not documented in README: {func}"


def test_readme_documents_15_certificates():
    """Test that README references all 15 certificates."""
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    readme_path = os.path.join(
        repo_root,
        "src/canonic_phases/phase_0_input_validation/README.md"
    )
    
    with open(readme_path) as f:
        content = f.read()
    
    # Look for certificate names in numbered list under "Certificates (15)"
    certificates = [
        "Runtime Mode Enforcement",
        "Bootstrap Initialization",
        "Input File Hashing",
        "Boot Checks Execution",
        "Determinism Seeds Applied",
        "Questionnaire Integrity",
        "Method Registry Validation",
        "Smoke Tests Execution",
        "Exit Gate Sequencing",
        "Canonical Path Enforcement",
        "Naming Convention Compliance",
        "Phase0Result Handoff Readiness",
        "Contract Module Structure",
        "Academic README Alignment",
        "Governance Artifacts Complete",
    ]
    
    for cert_name in certificates:
        assert cert_name in content, \
            f"Certificate '{cert_name}' not listed in README"

"""Tests for legacy path purge verification."""

import subprocess
import os


def test_purge_non_canonical_paths():
    """Test that no legacy Phase_zero paths exist outside canonical location."""
    # Get repository root
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    # Search for Phase_zero directories (excluding canonical path and compatibility shim)
    cmd = (
        f"find {repo_root}/src -type d "
        f"\\( -name 'Phase_zero' -o -name 'phase_zero' \\) "
        f"! -path '*/phase_0_input_validation/*' "
        f"! -path '*/farfan_pipeline/phases/Phase_zero'"
    )
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    # Should find no legacy directories (excluding the compatibility shim)
    assert result.stdout.strip() == "", \
        f"Found legacy Phase 0 directories: {result.stdout}"


def test_no_legacy_imports_in_src():
    """Test that src/ files do not import from legacy Phase_zero path."""
    # Get repository root
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    # Search for legacy imports in src/
    cmd = (
        f"grep -r 'from.*\\.Phase_zero' {repo_root}/src "
        f"--include='*.py' "
        f"! -path '*/phase_0_input_validation/*' "
        f"! -path '*/phases/Phase_zero/*' "
        f"|| true"
    )
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    # Filter out compatibility shim and legacy Phase_zero files themselves
    filtered_lines = [
        line for line in result.stdout.strip().split("\n")
        if line and 
        "canonic_phases/__init__.py" not in line and
        "phases/Phase_zero" not in line
    ]
    
    assert not filtered_lines, \
        f"Found legacy Phase_zero imports in src/: {filtered_lines}"


def test_canonical_path_exists():
    """Test that canonical path exists and contains expected files."""
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    canonical_path = os.path.join(
        repo_root, 
        "src/canonic_phases/phase_0_input_validation"
    )
    
    assert os.path.exists(canonical_path), \
        f"Canonical path does not exist: {canonical_path}"
    
    # Check for key files
    expected_files = [
        "__init__.py",
        "README.md",
        "phase0_runtime_config.py",
        "phase0_boot_checks.py",
        "phase0_exit_gates.py",
        "phase0_results.py",
    ]
    
    for filename in expected_files:
        filepath = os.path.join(canonical_path, filename)
        assert os.path.exists(filepath), \
            f"Expected file not found: {filepath}"


def test_contracts_directory_exists():
    """Test that contracts/ directory exists with expected structure."""
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    contracts_path = os.path.join(
        repo_root,
        "src/canonic_phases/phase_0_input_validation/contracts"
    )
    
    assert os.path.exists(contracts_path), \
        f"Contracts directory does not exist: {contracts_path}"
    
    # Check for contract modules
    contract_files = [
        "phase0_bootstrap_contract.py",
        "phase0_input_contract.py",
        "phase0_exit_gates_contract.py",
        "phase0_fallback_policy_contract.py",
    ]
    
    for filename in contract_files:
        filepath = os.path.join(contracts_path, filename)
        assert os.path.exists(filepath), \
            f"Contract file not found: {filepath}"


def test_certificates_directory_exists():
    """Test that certificates/ directory exists with 15 certificates."""
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    certificates_path = os.path.join(
        repo_root,
        "src/canonic_phases/phase_0_input_validation/contracts/certificates"
    )
    
    assert os.path.exists(certificates_path), \
        f"Certificates directory does not exist: {certificates_path}"
    
    # Count certificate files
    cmd = f"find {certificates_path} -name 'CERTIFICATE_*.md' | wc -l"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    cert_count = int(result.stdout.strip())
    assert cert_count == 15, \
        f"Expected 15 certificates, found {cert_count}"

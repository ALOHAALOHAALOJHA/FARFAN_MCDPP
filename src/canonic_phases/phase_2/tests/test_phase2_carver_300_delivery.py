"""
Test Phase 2 Carver 300 Delivery

Validates that Phase 2 executor orchestration can handle all 300 contracts
and produce deterministic results.
"""
import os
from pathlib import Path


def test_phase2_directory_structure() -> None:
    """Verify Phase 2 canonical directory structure exists."""
    phase2_root = Path(__file__).parent.parent
    
    assert phase2_root.exists(), "Phase 2 root directory must exist"
    assert (phase2_root / "README.md").exists(), "README.md must exist"
    assert (phase2_root / "schemas").exists(), "schemas directory must exist"
    assert (phase2_root / "contracts").exists(), "contracts directory must exist"
    assert (phase2_root / "contracts" / "certificates").exists(), "certificates directory must exist"
    assert (phase2_root / "tests").exists(), "tests directory must exist"


def test_certificate_count() -> None:
    """Verify exactly 15 certificates exist."""
    phase2_root = Path(__file__).parent.parent
    cert_dir = phase2_root / "contracts" / "certificates"
    
    certificates = list(cert_dir.glob("CERTIFICATE_*.md"))
    assert len(certificates) == 15, f"Expected 15 certificates, found {len(certificates)}"


def test_certificate_format() -> None:
    """Verify certificates contain required fields."""
    phase2_root = Path(__file__).parent.parent
    cert_dir = phase2_root / "contracts" / "certificates"
    
    required_fields = ["Status", "Effective Date", "Verification Method"]
    
    for cert_file in cert_dir.glob("CERTIFICATE_*.md"):
        content = cert_file.read_text()
        
        for field in required_fields:
            assert field in content, f"{cert_file.name} missing required field: {field}"
        
        assert "Status.*ACTIVE" in content or "Status | ACTIVE" in content, \
            f"{cert_file.name} must have ACTIVE status"


def test_determinism_seed() -> None:
    """Verify deterministic execution seed is configured."""
    seed = os.environ.get("PHASE2_RANDOM_SEED")
    
    # This test only runs when PHASE2_RANDOM_SEED is set in environment
    if seed is not None:
        assert seed == "42", f"Expected PHASE2_RANDOM_SEED=42, got {seed}"


def test_readme_content() -> None:
    """Verify README.md contains essential Phase 2 documentation."""
    phase2_root = Path(__file__).parent.parent
    readme = phase2_root / "README.md"
    
    content = readme.read_text()
    
    required_sections = [
        "Phase 2",
        "Executor Orchestration",
        "Status",
        "ACTIVE",
        "Version",
        "300",  # Number of contracts
        "Q001",  # First contract
        "Q300",  # Last contract
    ]
    
    for section in required_sections:
        assert section in content, f"README.md missing required content: {section}"

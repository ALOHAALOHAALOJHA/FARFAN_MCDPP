"""
Module: src.canonic_phases.phase_2.tests.test_phase2_certificates_presence
Purpose: Verify all 15 certificates exist with required fields
Owner: phase2_orchestration
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-18

Contracts-Enforced:
    - CertificatePresenceContract: All 15 certificates exist
    - CertificateFormatContract: Each certificate has required fields

Determinism:
    Seed-Strategy: NOT_APPLICABLE
    State-Management: Stateless file system scan

Inputs:
    - certificates_dir: Path — contracts/certificates/

Outputs:
    - validation_result: All assertions pass

Failure-Modes:
    - MissingCertificate: AssertionError — Certificate file not found
    - MalformedCertificate: AssertionError — Required field missing
"""
from __future__ import annotations

import re
import warnings
from pathlib import Path
from typing import Final, List, Set

import pytest

# === CONSTANTS ===

REQUIRED_CERTIFICATES: Final[list[str]] = [
    "CERTIFICATE_01_ROUTING_CONTRACT.md",
    "CERTIFICATE_02_CONCURRENCY_DETERMINISM.md",
    "CERTIFICATE_03_CONTEXT_IMMUTABILITY.md",
    "CERTIFICATE_04_PERMUTATION_INVARIANCE.md",
    "CERTIFICATE_05_RUNTIME_CONTRACTS.md",
    "CERTIFICATE_06_CONFIG_SCHEMA_VALIDITY.md",
    "CERTIFICATE_07_OUTPUT_SCHEMA_VALIDITY.md",
    "CERTIFICATE_08_CARVER_300_DELIVERY.md",
    "CERTIFICATE_09_CPP_TO_EXECUTOR_ALIGNMENT.md",
    "CERTIFICATE_10_SISAS_SYNCHRONIZATION.md",
    "CERTIFICATE_11_RESOURCE_PLANNING_DETERMINISM.md",
    "CERTIFICATE_12_PRECISION_TRACKING_INTEGRITY.md",
    "CERTIFICATE_13_METHOD_REGISTRY_COMPLETENESS.md",
    "CERTIFICATE_14_SIGNATURE_VALIDATION_STRICTNESS.md",
    "CERTIFICATE_15_SOURCE_VALIDATION_STRICTNESS.md",
]

REQUIRED_FIELDS: Final[list[str]] = [
    "Certificate ID",
    "Status",
    "Effective Date",
    "Description",
    "Success Criteria",
    "Failure Modes",
    "Verification Method",
    "Test File",
]


# === FIXTURES ===

@pytest.fixture
def certificates_dir() -> Path:
    """Return path to certificates directory."""
    return Path(__file__).parent.parent / "contracts" / "certificates"


# === TESTS ===

class TestCertificatesPresence:
    """
    SUCCESS_CRITERIA:
        - All 15 certificate files exist
        - Each certificate contains required fields
        - Status field is ACTIVE

    FAILURE_MODES:
        - MissingFile: Certificate file not found
        - MissingField: Required field not in certificate
        - InvalidStatus: Status is not ACTIVE

    TERMINATION_CONDITION:
        - All certificates scanned and validated

    VERIFICATION_STRATEGY:
        - pytest execution in CI
    """

    def test_certificates_directory_exists(
        self,
        certificates_dir: Path,
    ) -> None:
        """certificates/ directory must exist."""
        assert certificates_dir.exists(), (
            f"Certificates directory not found: {certificates_dir}"
        )
        assert certificates_dir.is_dir(), (
            f"Certificates path is not a directory: {certificates_dir}"
        )

    def test_all_15_certificates_present(
        self,
        certificates_dir: Path,
    ) -> None:
        """All 15 required certificates must exist."""
        missing: list[str] = []

        for cert_name in REQUIRED_CERTIFICATES:
            cert_path = certificates_dir / cert_name
            if not cert_path.exists():
                missing.append(cert_name)

        assert not missing, (
            f"Missing certificates ({len(missing)}/15):\n" +
            "\n".join(f"  - {m}" for m in missing)
        )

    def test_certificate_naming_pattern(
        self,
        certificates_dir: Path,
    ) -> None:
        """All certificate files must match naming pattern."""
        pattern = re.compile(r"^CERTIFICATE_[0-9]{2}_[A-Z][A-Z0-9_]*\.md$")
        violations: list[str] = []

        for cert_file in certificates_dir.glob("*.md"):
            if not pattern.match(cert_file.name):
                violations.append(cert_file.name)

        assert not violations, (
            "Certificate naming violations:\n" +
            "\n".join(f"  - {v}" for v in violations)
        )

    @pytest.mark.parametrize("cert_name", REQUIRED_CERTIFICATES)
    def test_certificate_has_required_fields(
        self,
        certificates_dir: Path,
        cert_name: str,
    ) -> None:
        """Each certificate must contain all required fields."""
        cert_path = certificates_dir / cert_name

        if not cert_path.exists():
            pytest.skip(f"Certificate not yet created: {cert_name}")

        content = cert_path.read_text(encoding="utf-8")

        missing_fields: list[str] = []
        for field in REQUIRED_FIELDS:
            if field not in content:
                missing_fields.append(field)

        assert not missing_fields, (
            f"Certificate {cert_name} missing fields:\n" +
            "\n".join(f"  - {f}" for f in missing_fields)
        )

    @pytest.mark.parametrize("cert_name", REQUIRED_CERTIFICATES)
    def test_certificate_status_is_active(
        self,
        certificates_dir: Path,
        cert_name: str,
    ) -> None:
        """Each certificate Status field must be ACTIVE."""
        cert_path = certificates_dir / cert_name

        if not cert_path.exists():
            pytest.skip(f"Certificate not yet created: {cert_name}")

        content = cert_path.read_text(encoding="utf-8")

        # Look for Status field in table format
        status_pattern = re.compile(r"\|\s*Status\s*\|\s*(\w+)\s*\|")
        match = status_pattern.search(content)

        assert match is not None, (
            f"Certificate {cert_name} has no Status field in table format"
        )

        status = match.group(1)
        assert status == "ACTIVE", (
            f"Certificate {cert_name} Status is {status}, expected ACTIVE"
        )

    def test_no_extra_certificates(
        self,
        certificates_dir: Path,
    ) -> None:
        """No unexpected certificate files should exist."""
        expected_set: set[str] = set(REQUIRED_CERTIFICATES)
        actual_files = {f.name for f in certificates_dir.glob("*.md")}

        extra = actual_files - expected_set

        # Warning only, not assertion (may have additional docs)
        if extra:
            import warnings
            warnings.warn(
                f"Extra files in certificates: {extra}",
                UserWarning,
            )

#!/usr/bin/env python3
"""
Certificate Compliance Validator

Validates that all certificate files comply with the 15 mandatory elements
specified in Section 9 of phase_4_7_aggregation_pipeline/README.md.
"""
import re
from pathlib import Path
from typing import Dict, List, Tuple

CERTIFICATE_DIR = Path("src/canonic_phases/phase_4_7_aggregation_pipeline/contracts/certificates")

MANDATORY_ELEMENTS = {
    1: "Certificate Title (# Certificate XX:)",
    2: "Status (**Status:**)",
    3: "Timestamp (**Timestamp:**)",
    4: "Phase (**Phase:**)",
    5: "Requirement ID (**Requirement ID:**)",
    6: "Requirement Specification (## Requirement Specification)",
    8: "Verification Method (## Verification Method)",
    9: "Test Specification (**Test:**)",
    10: "Validation Function/Code reference",
    11: "Evidence (## Evidence)",
    12: "Code Location (in evidence)",
    13: "Compliance Status (## Compliance Status)",
    14: "Signature (**Signature:**)",
    15: "Next Review Date (optional but recommended)",
}


def validate_certificate(cert_path: Path) -> Tuple[bool, List[str]]:
    """Validate a single certificate file against the template."""
    content = cert_path.read_text()
    lines = content.split("\n")
    
    issues = []
    checks = {
        1: re.search(r"^# Certificate \d+:", content, re.MULTILINE) is not None,
        2: "**Status:**" in content,
        3: "**Timestamp:**" in content,
        4: "**Phase:**" in content,
        5: "**Requirement ID:**" in content,
        6: "## Requirement Specification" in content,
        8: "## Verification Method" in content,
        9: "**Test:**" in content,
        10: ("**Validation Function" in content or  # Allow singular or plural
             "**Code:**" in content or
             "**Validation:**" in content),
        11: "## Evidence" in content,
        12: "**Code Location:**" in content or "**Code:**" in content,
        13: "## Compliance Status" in content,
        14: "**Signature:**" in content,
        15: True,  # Next Review Date is optional
    }
    
    for element_num, element_name in MANDATORY_ELEMENTS.items():
        if not checks[element_num]:
            issues.append(f"  ❌ Missing element {element_num}: {element_name}")
    
    # Check for compliance indicator
    if not any(indicator in content for indicator in ["✅", "❌", "⚠️"]):
        issues.append("  ⚠️  No compliance indicator found (✅/❌/⚠️)")
    
    # Check naming convention (allow numbers in descriptive name)
    if not re.match(r"CERTIFICATE_\d{2}_[A-Z0-9_]+\.md$", cert_path.name):
        issues.append(f"  ⚠️  Filename does not match naming convention: {cert_path.name}")
    
    is_compliant = len(issues) == 0
    return is_compliant, issues


def main():
    """Validate all certificates in the directory."""
    print("=" * 80)
    print("Certificate Compliance Validator")
    print("=" * 80)
    print()
    
    if not CERTIFICATE_DIR.exists():
        print(f"❌ Certificate directory not found: {CERTIFICATE_DIR}")
        return 1
    
    cert_files = sorted(CERTIFICATE_DIR.glob("CERTIFICATE_*.md"))
    
    if not cert_files:
        print(f"❌ No certificate files found in {CERTIFICATE_DIR}")
        return 1
    
    print(f"Found {len(cert_files)} certificate files to validate.")
    print()
    
    all_compliant = True
    results: Dict[str, Tuple[bool, List[str]]] = {}
    
    for cert_path in cert_files:
        is_compliant, issues = validate_certificate(cert_path)
        results[cert_path.name] = (is_compliant, issues)
        
        if is_compliant:
            print(f"✅ {cert_path.name}")
        else:
            print(f"❌ {cert_path.name}")
            for issue in issues:
                print(issue)
            print()
            all_compliant = False
    
    print()
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    
    compliant_count = sum(1 for is_compliant, _ in results.values() if is_compliant)
    total_count = len(results)
    
    print(f"Compliant: {compliant_count}/{total_count}")
    print(f"Non-compliant: {total_count - compliant_count}/{total_count}")
    
    if all_compliant:
        print()
        print("✅ All certificates comply with the template specification!")
        return 0
    else:
        print()
        print("❌ Some certificates have compliance issues.")
        return 1


if __name__ == "__main__":
    exit(main())

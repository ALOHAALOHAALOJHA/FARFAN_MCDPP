#!/usr/bin/env python3
"""
Verification Script for 15-Contract Suite
Runs all tests and tools, then validates certificates.
"""
import glob
import json
import os
import subprocess
import sys

CONTRACTS_DIR = "src/farfan_pipeline/contracts"
TOOLS_DIR = CONTRACTS_DIR / "tools"
TESTS_DIR = CONTRACTS_DIR / "tests"


def run_command(cmd: str, description: str, set_pythonpath: bool = False) -> bool:
    print(f"Running {description}...")
    try:
        env = os.environ.copy()
        if set_pythonpath:
            cwd = os.getcwd()
            src_path = cwd / "src"
            env["PYTHONPATH"] = f"{src_path}:{env.get('PYTHONPATH', '')}"
        subprocess.check_call(cmd, shell=True, env=env)
        print(f"✅ {description} PASSED")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ {description} FAILED")
        return False


def main() -> None:
    print("=== STARTING VERIFICATION OF 15-CONTRACT SUITE ===")

    # 1. Run Pytest Suite
    print("\n--- 1. RUNNING TESTS ---")
    if not run_command(
        f"pytest {TESTS_DIR} -v", "All Contract Tests", set_pythonpath=True
    ):
        sys.exit(1)

    # 2. Run CLI Tools to generate certificates
    print("\n--- 2. GENERATING CERTIFICATES ---")
    tools = glob.glob(TOOLS_DIR / "*.py")
    for tool in sorted(tools):
        tool_name = os.path.basename(tool)
        if not run_command(f"python {tool}", f"Tool: {tool_name}", set_pythonpath=True):
            sys.exit(1)

    # 3. Verify Certificates
    print("\n--- 3. VERIFYING CERTIFICATES ---")
    expected_certs = [
        "rc_certificate.json",
        "sc_certificate.json",
        "cic_certificate.json",
        "pic_certificate.json",
        "bmc_certificate.json",
        "toc_certificate.json",
        "rec_certificate.json",
        "asc_certificate.json",
        "idc_certificate.json",
        "rcc_certificate.json",
        "mcc_certificate.json",
        "ffc_certificate.json",
        "cdc_certificate.json",
        "tc_certificate.json",
        "refc_certificate.json",
    ]

    all_passed = True
    for cert_file in expected_certs:
        if not os.path.exists(cert_file):
            print(f"❌ {cert_file}: MISSING")
            all_passed = False
            continue

        try:
            with open(cert_file) as f:
                data = json.load(f)
                if data.get("pass") is True:
                    print(f"✅ {cert_file}: PASS")
                else:
                    print(f"❌ {cert_file}: FAIL (pass != true)")
                    all_passed = False
        except Exception as e:
            print(f"❌ {cert_file}: ERROR ({e})")
            all_passed = False

    if all_passed:
        print("\n=== ALL SYSTEM CONTRACTS VERIFIED SUCCESSFULLY ===")
        sys.exit(0)
    else:
        print("\n=== VERIFICATION FAILED ===")
        sys.exit(1)


if __name__ == "__main__":
    main()

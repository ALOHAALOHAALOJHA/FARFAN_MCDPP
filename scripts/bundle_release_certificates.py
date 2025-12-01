#!/usr/bin/env python3
"""
Release Certificate Bundler
Generates all 15 certificates and bundles them into a release directory.
"""
import os
import sys
import shutil
import glob
import subprocess
from datetime import datetime

CONTRACTS_DIR = "farfan_core/farfan_core/contracts"
TOOLS_DIR = os.path.join(CONTRACTS_DIR, "tools")
RELEASE_DIR = "release_certificates"

def run_command(cmd):
    try:
        # Add farfan_core to PYTHONPATH
        env = os.environ.copy()
        cwd = os.getcwd()
        farfan_core_path = os.path.join(cwd, "farfan_core")
        env["PYTHONPATH"] = f"{farfan_core_path}:{env.get('PYTHONPATH', '')}"
        
        subprocess.check_call(cmd, shell=True, env=env)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_dir = f"{RELEASE_DIR}_{timestamp}"
    
    print(f"Bundling certificates into {target_dir}...")
    os.makedirs(target_dir, exist_ok=True)
    
    # 1. Generate Certificates
    print("Generating certificates...")
    tools = glob.glob(os.path.join(TOOLS_DIR, "*.py"))
    for tool in tools:
        print(f"Running {os.path.basename(tool)}...")
        if not run_command(f"python3 {tool}"):
            print(f"❌ Failed to run {tool}")
            sys.exit(1)
            
    # 2. Collect Certificates
    print("Collecting certificates...")
    certs = glob.glob("*.json")
    cert_files = [c for c in certs if c.endswith("_certificate.json")]
    
    for cert in cert_files:
        shutil.move(cert, os.path.join(target_dir, cert))
        
    print(f"✅ Successfully bundled {len(cert_files)} certificates in {target_dir}")
    
    # Verify count
    if len(cert_files) != 15:
        print(f"⚠️ WARNING: Expected 15 certificates, found {len(cert_files)}")
    else:
        print("All 15 contracts accounted for.")

if __name__ == "__main__":
    main()

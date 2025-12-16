#!/usr/bin/env python3.12
"""Installation script for F.A.R.F.A.N dependencies"""
import subprocess
import sys
from pathlib import Path

def main():
    venv_dir = Path("farfan-env")
    if sys.platform == "win32":
        venv_python = venv_dir / "Scripts" / "python.exe"
    else:
        venv_python = venv_dir / "bin" / "python3.12"
    
    if not venv_python.exists():
        print("Error: Virtual environment not found")
        sys.exit(1)
    
    print("Installing package in editable mode...")
    result = subprocess.run(
        [str(venv_python), "-m", "pip", "install", "-e", "."],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())

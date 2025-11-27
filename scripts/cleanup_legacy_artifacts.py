"""Cleanup Legacy Artifacts.

Deletes files from previous waves (canonical, level 3, etc.) to ensure
a single source of truth.
"""

import os
import glob
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

LEGACY_PATTERNS = [
    "**/*canonical*",
    "**/*metodos_completos*",
    "**/*catalogue*",
    "**/generate_catalogue*",
    "**/validate_canonical*",
]

PRESERVE_LIST = [
    # Add any files we MUST keep here if they match patterns
]

def cleanup():
    print("🧹 Starting Legacy Cleanup...")
    count = 0
    for pattern in LEGACY_PATTERNS:
        # Recursive search
        for filepath in REPO_ROOT.glob(pattern):
            if filepath.name in PRESERVE_LIST:
                continue
            
            if filepath.is_dir():
                # Skip directories for now, handle files first
                continue
                
            try:
                print(f"   Deleting: {filepath.relative_to(REPO_ROOT)}")
                os.remove(filepath)
                count += 1
            except Exception as e:
                print(f"   ❌ Error deleting {filepath}: {e}")

    print(f"✨ Deleted {count} legacy files.")

if __name__ == "__main__":
    cleanup()

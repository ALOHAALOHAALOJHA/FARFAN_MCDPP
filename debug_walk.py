from pathlib import Path
import sys
import os

# Add src to path so we can import farfan_core
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "farfan_core"))

from farfan_core.core.method_inventory import walk_python_files, INVENTORY_ROOTS, _normalize_roots

print(f"Current CWD: {os.getcwd()}")
print(f"INVENTORY_ROOTS: {INVENTORY_ROOTS}")

# Check if roots exist
for r in INVENTORY_ROOTS:
    print(f"Root {r} exists: {r.exists()}")

files = walk_python_files()
print(f"Found {len(files)} files.")

flux_count = 0
for f in files:
    if "flux" in str(f):
        print(f"Flux file: {f}")
        flux_count += 1

print(f"Total flux files found: {flux_count}")

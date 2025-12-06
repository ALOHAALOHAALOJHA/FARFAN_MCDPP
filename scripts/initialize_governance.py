#!/usr/bin/env python3
import os
import json
import hashlib
from pathlib import Path
import datetime

# Configuration
ROOT_DIR = Path(__file__).parent.parent
CONFIG_DIR = ROOT_DIR / "system" / "config"
HASH_REGISTRY = ROOT_DIR / "config_hash_registry.json"

def compute_file_hash(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def initialize_registry():
    print("Initializing Configuration Governance Registry...")
    
    registry = {
        "_metadata": {
            "initialized_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "version": "1.0"
        },
        "files": {}
    }
    
    if not CONFIG_DIR.exists():
        print(f"Config directory {CONFIG_DIR} does not exist. Creating...")
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # Scan for config files
    for filepath in CONFIG_DIR.rglob("*"):
        if filepath.is_file() and filepath.name != ".DS_Store":
            file_hash = compute_file_hash(filepath)
            rel_path = str(filepath.relative_to(ROOT_DIR))
            registry["files"][rel_path] = {
                "hash": file_hash,
                "last_modified": datetime.datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
            }
            print(f"Registered: {rel_path}")

    with open(HASH_REGISTRY, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)
        
    print(f"Registry initialized at {HASH_REGISTRY}")

if __name__ == "__main__":
    initialize_registry()

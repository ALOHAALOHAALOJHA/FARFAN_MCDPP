
import sys
import importlib
import importlib.metadata
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path.cwd() / "src"))

def check_import(module_name):
    try:
        importlib.import_module(module_name)
        print(f"✅ Import successful: {module_name}")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {module_name} - {e}")
        return False

def check_package(package_name):
    try:
        version = importlib.metadata.version(package_name)
        print(f"✅ Package found: {package_name} ({version})")
        return True
    except importlib.metadata.PackageNotFoundError:
        print(f"❌ Package missing: {package_name}")
        return False

print("=== BLOCKER VERIFICATION ===")

# Blocker 1: farfan_pipeline.core.canonical_notation
check_import("farfan_pipeline.core.canonical_notation")

# Blocker 3: Methods
# Check for class_registry
check_import("farfan_pipeline.methods.class_registry")

# Gap 5: FastAPI
check_package("fastapi")
check_package("uvicorn")

# Gap 6: Sentence Transformers
check_package("sentence-transformers")
check_package("torch")
check_package("spacy")

# Check SISAS integration (roughly)
# Check if orchestrator imports SISAS
try:
    # Attempt to find where orchestrator module is.
    # The audit said src/orchestration/orchestrator.py (doesn't exist)
    # But src/farfan_pipeline/orchestration/orchestrator.py exists
    from farfan_pipeline.orchestration import orchestrator
    print("✅ Orchestrator importable")
except ImportError as e:
    print(f"❌ Orchestrator not importable: {e}")

# Check files
files_to_check = [
    "METHODS_TO_QUESTIONS_AND_FILES.json",
    "METHODS_OPERACIONALIZACION.json",
    "canonic_questionnaire_central/questionnaire_monolith.json"
]

print("\n=== FILE CHECK ===")
for f in files_to_check:
    # Search in current dir and subdirs
    found = list(Path(".").rglob(f))
    if found:
         print(f"✅ Found {f} at {found[0]}")
    else:
         print(f"❌ Missing {f}")


import sys
import os
from pathlib import Path

# Setup path like the test does
PROJECT_ROOT = Path(os.getcwd())
sys.path.insert(0, str(PROJECT_ROOT / "src"))

print(f"sys.path: {sys.path}")

try:
    import canonic_phases.Phase_two.evidence_nexus as en
    print("Import successful!")
    print(dir(en))
except ImportError as e:
    print(f"Import failed: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

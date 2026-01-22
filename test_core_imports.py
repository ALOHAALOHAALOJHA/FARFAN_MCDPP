import sys
import os
from pathlib import Path

# Add src to python path
src_path = Path.cwd() / "src"
sys.path.append(str(src_path))

def test_imports():
    print("Testing core imports...")
    
    # 1. Test UnifiedFactory
    try:
        from farfan_pipeline.orchestration.factory import UnifiedFactory
        print("✅ UnifiedFactory imported successfully")
    except ImportError as e:
        print(f"❌ UnifiedFactory import failed: {e}")
        return False

    # 2. Test MethodExecutor (Compatibility)
    try:
        from farfan_pipeline.orchestration.compatibility import MethodExecutor
        print("✅ MethodExecutor (compatibility) imported successfully")
    except ImportError as e:
        print(f"❌ MethodExecutor (compatibility) import failed: {e}")
        return False

    # 3. Test SISAS Integration Hub
    try:
        from farfan_pipeline.orchestration.sisas_integration_hub import SISASIntegrationHub
        print("✅ SISASIntegrationHub imported successfully")
    except ImportError as e:
        print(f"❌ SISASIntegrationHub import failed: {e}")
        return False

    # 4. Test Orchestrator
    try:
        from farfan_pipeline.orchestration.orchestrator import UnifiedOrchestrator
        print("✅ UnifiedOrchestrator imported successfully")
    except ImportError as e:
        print(f"❌ UnifiedOrchestrator import failed: {e}")
        return False

    print("\nAll core imports passed.")
    return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)


import sys
import os

try:
    from farfan_pipeline.infrastructure.calibration.calibration_core import create_calibration_parameter
    print("Success importing from calibration_core")
except ImportError as e:
    print(f"Failed importing from calibration_core: {e}")

try:
    from farfan_pipeline.infrastructure.calibration import create_calibration_parameter
    print("Success importing from calibration package")
except ImportError as e:
    print(f"Failed importing from calibration package: {e}")

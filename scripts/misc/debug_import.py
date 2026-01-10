import sys
import os

sys.path.append(os.getcwd())  # noqa: E501

try:
    from farfan_pipeline.infrastructure.calibration.calibration_core import (
        create_calibration_parameter,
    )

    print("Success importing from calibration_core")
except ImportError as e:
    print(f"Failed importing from calibration_core: {e}")

try:
    import farfan_pipeline.infrastructure.calibration as calibration

    print("Success importing from calibration package")
except ImportError as e:
    print(f"Failed importing from calibration package: {e}")

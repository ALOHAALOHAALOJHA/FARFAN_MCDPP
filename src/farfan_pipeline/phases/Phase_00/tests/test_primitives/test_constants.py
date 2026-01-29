import pytest
from farfan_pipeline.phases.Phase_00.primitives.constants import (
    PHASE_NUMBER,
    STAGE_METADATA,
    VALID_STAGES,
    MODULE_MANIFEST,
    validate_module_name
)

def test_constants_integrity():
    assert PHASE_NUMBER == 0
    assert len(STAGE_METADATA) == len(VALID_STAGES)
    assert len(MODULE_MANIFEST) > 0

def test_module_name_validation():
    assert validate_module_name("phase0_10_00_paths.py") is True
    assert validate_module_name("invalid_name.py") is False
    assert validate_module_name("phase0_10_00.py") is False # Missing name part

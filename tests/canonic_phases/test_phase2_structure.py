"""Test Phase 2 canonical structure and basic imports.

Verifies STEP 01-04 completion:
- Directory structure exists
- Package imports work
- Constants are frozen and validated
- JSON schemas are valid
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest


def test_phase2_directory_structure_exists() -> None:
    """GATE: Directory structure complete (STEP 01)."""
    phase2_root = Path("src/canonic_phases/phase_2")
    
    required_dirs = [
        "constants",
        "schemas",
        "executors/implementations",
        "executors/tests",
        "contracts/certificates",
        "orchestration",
        "sisas",
        "tests",
        "tools",
    ]
    
    for dir_path in required_dirs:
        full_path = phase2_root / dir_path
        assert full_path.exists(), f"Directory {dir_path} does not exist"
        assert full_path.is_dir(), f"{dir_path} is not a directory"


def test_phase2_package_structure_valid() -> None:
    """GATE: Package structure valid (STEP 02)."""
    import src.canonic_phases.phase_2
    import src.canonic_phases.phase_2.constants
    import src.canonic_phases.phase_2.schemas
    import src.canonic_phases.phase_2.executors
    import src.canonic_phases.phase_2.contracts
    import src.canonic_phases.phase_2.orchestration
    import src.canonic_phases.phase_2.sisas
    import src.canonic_phases.phase_2.tests
    import src.canonic_phases.phase_2.tools
    
    assert src.canonic_phases.phase_2 is not None
    assert src.canonic_phases.phase_2.constants is not None


def test_phase2_constants_frozen() -> None:
    """GATE: Constants frozen (STEP 03)."""
    from src.canonic_phases.phase_2.constants.phase2_constants import (
        NUM_CHUNKS,
        NUM_BASE_QUESTIONS,
        NUM_POLICY_AREAS,
        NUM_MICRO_ANSWERS,
        PHASE_2_CARDINALITY_INVARIANT,
    )
    
    assert NUM_CHUNKS == 60, "NUM_CHUNKS must be 60"
    assert NUM_BASE_QUESTIONS == 30, "NUM_BASE_QUESTIONS must be 30"
    assert NUM_POLICY_AREAS == 10, "NUM_POLICY_AREAS must be 10"
    assert NUM_MICRO_ANSWERS == 300, "NUM_MICRO_ANSWERS must be 300"
    
    assert NUM_MICRO_ANSWERS == NUM_BASE_QUESTIONS * NUM_POLICY_AREAS, \
        f"Cardinality invariant failed: {NUM_MICRO_ANSWERS} != {NUM_BASE_QUESTIONS} × {NUM_POLICY_AREAS}"
    
    assert PHASE_2_CARDINALITY_INVARIANT == "60 chunks → 300 micro-answers"


def test_phase2_schemas_valid() -> None:
    """GATE: Schemas valid (STEP 04)."""
    schema_dir = Path("src/canonic_phases/phase_2/schemas")
    
    schemas = [
        "micro_answer_schema.json",
        "execution_plan_schema.json",
        "executor_contract_schema.json",
        "phase2_output_schema.json",
    ]
    
    for schema_name in schemas:
        schema_path = schema_dir / schema_name
        assert schema_path.exists(), f"Schema {schema_name} does not exist"
        
        with open(schema_path, "r") as f:
            schema = json.load(f)
        
        try:
            jsonschema.Draft202012Validator.check_schema(schema)
        except jsonschema.SchemaError as e:
            pytest.fail(f"Schema {schema_name} is invalid: {e}")


def test_phase2_cardinality_assertions() -> None:
    """Verify cardinality assertions in constants module."""
    from src.canonic_phases.phase_2.constants.phase2_constants import (
        NUM_CHUNKS,
        NUM_DIMENSIONS,
        NUM_POLICY_AREAS,
        NUM_BASE_QUESTIONS,
        NUM_MICRO_ANSWERS,
    )
    
    assert NUM_CHUNKS == NUM_POLICY_AREAS * NUM_DIMENSIONS, \
        f"Chunk invariant: {NUM_CHUNKS} != {NUM_POLICY_AREAS} × {NUM_DIMENSIONS}"
    
    assert NUM_MICRO_ANSWERS == NUM_BASE_QUESTIONS * NUM_POLICY_AREAS, \
        f"Output invariant: {NUM_MICRO_ANSWERS} != {NUM_BASE_QUESTIONS} × {NUM_POLICY_AREAS}"


def test_phase2_enum_completeness() -> None:
    """Verify enums in constants are complete."""
    from src.canonic_phases.phase_2.constants.phase2_constants import (
        Dimension,
        PolicyArea,
        DIMENSION_IDS,
        POLICY_AREA_IDS,
        BASE_QUESTION_IDS,
    )
    
    assert len(list(Dimension)) == 6, "Must have 6 dimensions"
    assert len(list(PolicyArea)) == 10, "Must have 10 policy areas"
    
    assert len(DIMENSION_IDS) == 6
    assert len(POLICY_AREA_IDS) == 10
    assert len(BASE_QUESTION_IDS) == 30
    
    assert all(dim_id.startswith("DIM") for dim_id in DIMENSION_IDS)
    assert all(pa_id.startswith("PA") for pa_id in POLICY_AREA_IDS)
    assert all(q_id.startswith("Q") for q_id in BASE_QUESTION_IDS)

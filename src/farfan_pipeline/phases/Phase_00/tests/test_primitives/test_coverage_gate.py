import pytest
from pathlib import Path
from farfan_pipeline.phases.Phase_00.primitives.coverage_gate import (
    count_file_methods,
    validate_schema_exists
)

def test_count_file_methods(temp_dir):
    py_file = temp_dir / "test.py"
    py_file.write_text("def func1(): pass\ndef _func2(): pass\n")
    
    public, total = count_file_methods(py_file)
    assert public == 1
    assert total == 2

def test_validate_schema_exists(temp_dir):
    (temp_dir / "test.schema.json").touch()
    exists, files = validate_schema_exists(temp_dir)
    assert exists is True
    assert "test.schema.json" in files

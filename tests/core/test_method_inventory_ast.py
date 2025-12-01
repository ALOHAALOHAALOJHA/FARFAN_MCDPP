"""
Tests for Core AST Analysis (Stages A-D) of the Method Inventory System.
"""
import ast
import shutil
from pathlib import Path
import pytest
from farfan_core.core.method_inventory import (
    walk_python_files,
    module_path_from_file,
    parse_file,
    extract_raw_methods,
    extract_signature,
    compute_governance_flags_for_file,
    RawMethodNode,
)

# ... (Existing tests remain) ...

def test_extract_signature(tmp_path):
    """Stage F: Verify signature extraction."""
    code = """
def my_func(a, b, *, c, config: "ExecutorConfig") -> int:
    pass

async def async_func(self) -> None:
    pass
"""
    f = tmp_path / "sig.py"
    f.write_text(code, encoding="utf-8")
    tree = parse_file(f)
    
    # Extract raw methods first to get the nodes
    nodes = extract_raw_methods(tree, "test.sig")
    methods = {n.func_def.name: n.func_def for n in nodes}
    
    # Test my_func
    sig1 = extract_signature(methods["my_func"])
    assert sig1.args == ["a", "b"]
    assert sig1.kwargs == ["c", "config"]
    assert sig1.returns == "int"
    assert sig1.accepts_executor_config is True
    assert sig1.is_async is False
    
    # Test async_func
    sig2 = extract_signature(methods["async_func"])
    assert sig2.args == ["self"]
    assert sig2.returns == "None"
    assert sig2.is_async is True

def test_compute_governance_flags(tmp_path):
    """Stage G: Verify governance flags."""
    code = """
import yaml
from ruamel import yaml as ryaml

class BadExecutor(BaseExecutor):
    def run(self):
        timeout = 30.0
        b_theory = 0.5
        
class GoodClass:
    def run(self):
        pass
"""
    f = tmp_path / "gov.py"
    f.write_text(code, encoding="utf-8")
    tree = parse_file(f)
    
    # Test file-level flags
    flags = compute_governance_flags_for_file(tree)
    assert flags.uses_yaml is True
    assert flags.has_hardcoded_timeout is True
    assert flags.has_hardcoded_calibration is True
    assert "timeout = 30.0" in flags.suspicious_magic_numbers
    # is_executor_class is not computed here anymore, it's per-method in build loop
    assert flags.is_executor_class is False


@pytest.fixture
def repo_fixture(tmp_path):
    """
    Creates a mini repository structure for testing.
    
    Structure:
    root/
      farfan_core/
        farfan_core/
          core/
            ports.py
            orchestrator/
              executor.py
            __pycache__/
              cached.py
    """
    root = tmp_path / "repo"
    core = root / "farfan_core" / "farfan_core" / "core"
    core.mkdir(parents=True)
    
    # Create valid python files
    (core / "ports.py").write_text("def foo(): pass\n", encoding="utf-8")
    
    orch = core / "orchestrator"
    orch.mkdir()
    (orch / "executor.py").write_text(
        "class MyExecutor:\n    def execute(self):\n        pass\n    async def run(self):\n        pass\n\ndef helper(): pass\n",
        encoding="utf-8"
    )
    
    # Create __pycache__ to test exclusion
    cache = core / "__pycache__"
    cache.mkdir()
    (cache / "cached.py").write_text("pass", encoding="utf-8")
    
    return core

def test_walk_python_files(repo_fixture):
    """Stage A: Verify file walking and exclusion."""
    files = walk_python_files([repo_fixture])
    
    # Should find ports.py and orchestrator/executor.py
    # Should NOT find __pycache__/cached.py
    
    filenames = [f.name for f in files]
    assert "ports.py" in filenames
    assert "executor.py" in filenames
    assert "cached.py" not in filenames
    
    # Verify sorting
    assert files == sorted(files)

def test_module_path_from_file(repo_fixture):
    """Stage B: Verify module path conversion."""
    # root is .../core
    # file is .../core/ports.py -> farfan_core.core.ports
    
    ports_file = repo_fixture / "ports.py"
    mod_path = module_path_from_file(ports_file, root=repo_fixture)
    assert mod_path == "farfan_core.core.ports"
    
    # file is .../core/orchestrator/executor.py -> farfan_core.core.orchestrator.executor
    exec_file = repo_fixture / "orchestrator" / "executor.py"
    mod_path_exec = module_path_from_file(exec_file, root=repo_fixture)
    assert mod_path_exec == "farfan_core.core.orchestrator.executor"

def test_parse_file(tmp_path):
    """Stage C: Verify AST parsing."""
    f = tmp_path / "valid.py"
    f.write_text("x = 1", encoding="utf-8")
    tree = parse_file(f)
    assert isinstance(tree, ast.Module)
    
    f_invalid = tmp_path / "invalid.py"
    f_invalid.write_text("def broken(", encoding="utf-8")
    with pytest.raises(SyntaxError):
        parse_file(f_invalid)

def test_extract_raw_methods(repo_fixture):
    """Stage D: Verify raw method extraction."""
    # Parse executor.py which has class methods and a top-level function
    exec_file = repo_fixture / "orchestrator" / "executor.py"
    tree = parse_file(exec_file)
    mod_path = "test.module"
    
    nodes = extract_raw_methods(tree, mod_path)
    
    # Expect: MyExecutor.execute, MyExecutor.run, helper (None)
    assert len(nodes) == 3
    
    methods = {n.func_def.name: n for n in nodes}
    
    assert "execute" in methods
    assert methods["execute"].class_name == "MyExecutor"
    assert isinstance(methods["execute"].func_def, ast.FunctionDef)
    
    assert "run" in methods
    assert methods["run"].class_name == "MyExecutor"
    assert isinstance(methods["run"].func_def, ast.AsyncFunctionDef)
    
    assert "helper" in methods
    assert methods["helper"].class_name is None

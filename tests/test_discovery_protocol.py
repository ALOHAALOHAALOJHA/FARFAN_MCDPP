"""
Tests for Discovery Protocol (Section 1.1).

Validates that the mandatory inventory acquisition tool functions correctly
and produces valid YAML inventory output.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def repo_root() -> Path:
    """Get repository root path."""
    return Path(__file__).parent.parent.resolve()


@pytest.fixture
def discovery_script(repo_root: Path) -> Path:
    """Get discovery protocol script path."""
    script_path = repo_root / "scripts" / "discovery_protocol.py"
    assert script_path.exists(), f"Discovery script not found: {script_path}"
    return script_path


@pytest.fixture
def inventory_path(repo_root: Path) -> Path:
    """Get inventory file path."""
    return repo_root / "PHASE2_INVENTORY.yaml"


@pytest.mark.updated
def test_discovery_script_exists(discovery_script: Path) -> None:
    """Verify discovery protocol script exists and is executable."""
    assert discovery_script.exists()
    assert discovery_script.is_file()
    assert discovery_script.suffix == ".py"


@pytest.mark.updated
def test_discovery_script_executes(
    discovery_script: Path, repo_root: Path
) -> None:
    """Verify discovery protocol script executes without errors."""
    result = subprocess.run(
        ["python3", str(discovery_script)],
        check=False, cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, (
        f"Discovery script failed with exit code {result.returncode}\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )
    assert "✓ Discovery protocol completed successfully" in result.stdout


@pytest.mark.updated
def test_inventory_file_generated(
    discovery_script: Path, inventory_path: Path, repo_root: Path
) -> None:
    """Verify inventory YAML file is generated."""
    if inventory_path.exists():
        inventory_path.unlink()

    subprocess.run(
        ["python3", str(discovery_script)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )

    assert inventory_path.exists(), "PHASE2_INVENTORY.yaml was not generated"
    assert inventory_path.stat().st_size > 0, "PHASE2_INVENTORY.yaml is empty"


@pytest.mark.updated
def test_inventory_yaml_valid(
    discovery_script: Path, inventory_path: Path, repo_root: Path
) -> None:
    """Verify inventory file contains valid YAML."""
    if not inventory_path.exists():
        subprocess.run(
            ["python3", str(discovery_script)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=60,
            check=True,
        )

    with open(inventory_path, encoding="utf-8") as f:
        inventory = yaml.safe_load(f)

    assert isinstance(inventory, dict), "Inventory must be a dictionary"
    assert inventory, "Inventory cannot be empty"


@pytest.mark.updated
def test_inventory_required_fields(
    discovery_script: Path, inventory_path: Path, repo_root: Path
) -> None:
    """Verify inventory contains all required fields."""
    if not inventory_path.exists():
        subprocess.run(
            ["python3", str(discovery_script)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=60,
            check=True,
        )

    with open(inventory_path, encoding="utf-8") as f:
        inventory = yaml.safe_load(f)

    required_top_level = [
        "inventory_timestamp",
        "inventory_version",
        "total_files_scanned",
        "file_type_counts",
        "command_results",
        "categorized_files",
        "import_dependencies",
        "legacy_artifacts",
    ]

    for field in required_top_level:
        assert field in inventory, f"Required field missing: {field}"

    assert inventory["inventory_version"] == "1.0.0"
    assert isinstance(inventory["total_files_scanned"], int)
    assert inventory["total_files_scanned"] > 0


@pytest.mark.updated
def test_inventory_command_results(
    discovery_script: Path, inventory_path: Path, repo_root: Path
) -> None:
    """Verify command results are present and structured correctly."""
    if not inventory_path.exists():
        subprocess.run(
            ["python3", str(discovery_script)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=60,
            check=True,
        )

    with open(inventory_path, encoding="utf-8") as f:
        inventory = yaml.safe_load(f)

    command_results = inventory["command_results"]

    required_command_sets = [
        "command_set_1_exhaustive_discovery",
        "command_set_2_directory_mapping",
        "command_set_3_import_dependencies",
        "command_set_4_legacy_artifacts",
    ]

    for cmd_set in required_command_sets:
        assert cmd_set in command_results, f"Command set missing: {cmd_set}"
        assert "count" in command_results[cmd_set]
        assert isinstance(command_results[cmd_set]["count"], int)
        assert command_results[cmd_set]["count"] >= 0


@pytest.mark.updated
def test_inventory_categorized_files(
    discovery_script: Path, inventory_path: Path, repo_root: Path
) -> None:
    """Verify categorized files are present and structured correctly."""
    if not inventory_path.exists():
        subprocess.run(
            ["python3", str(discovery_script)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=60,
            check=True,
        )

    with open(inventory_path, encoding="utf-8") as f:
        inventory = yaml.safe_load(f)

    categorized = inventory["categorized_files"]

    required_categories = [
        "phase2_files",
        "executor_files",
        "carver_files",
        "orchestrator_files",
        "sisas_files",
        "dura_lex_files",
        "synchronization_files",
        "irrigation_files",
        "contract_files",
        "validator_files",
    ]

    for category in required_categories:
        assert category in categorized, f"Category missing: {category}"
        assert "count" in categorized[category]
        assert "files" in categorized[category]
        assert isinstance(categorized[category]["count"], int)
        assert isinstance(categorized[category]["files"], list)
        assert categorized[category]["count"] == len(categorized[category]["files"])


@pytest.mark.updated
def test_inventory_import_dependencies(
    discovery_script: Path, inventory_path: Path, repo_root: Path
) -> None:
    """Verify import dependencies are tracked correctly."""
    if not inventory_path.exists():
        subprocess.run(
            ["python3", str(discovery_script)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=60,
            check=True,
        )

    with open(inventory_path, encoding="utf-8") as f:
        inventory = yaml.safe_load(f)

    imports = inventory["import_dependencies"]

    required_import_categories = [
        "executor_imports",
        "carver_imports",
        "contract_imports",
        "sisas_imports",
        "orchestrator_imports",
    ]

    for category in required_import_categories:
        assert category in imports, f"Import category missing: {category}"
        assert "count" in imports[category]
        assert "imports" in imports[category]
        assert isinstance(imports[category]["count"], int)
        assert isinstance(imports[category]["imports"], list)


@pytest.mark.updated
def test_inventory_legacy_artifacts(
    discovery_script: Path, inventory_path: Path, repo_root: Path
) -> None:
    """Verify legacy artifacts are detected correctly."""
    if not inventory_path.exists():
        subprocess.run(
            ["python3", str(discovery_script)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=60,
            check=True,
        )

    with open(inventory_path, encoding="utf-8") as f:
        inventory = yaml.safe_load(f)

    legacy = inventory["legacy_artifacts"]

    required_legacy_categories = [
        "legacy_executors_py",
        "legacy_batch_py",
        "legacy_v2_files",
        "legacy_final_files",
        "legacy_old_files",
    ]

    for category in required_legacy_categories:
        assert category in legacy, f"Legacy category missing: {category}"
        assert "count" in legacy[category]
        assert "files" in legacy[category]
        assert isinstance(legacy[category]["count"], int)
        assert isinstance(legacy[category]["files"], list)


@pytest.mark.updated
def test_inventory_file_type_counts(
    discovery_script: Path, inventory_path: Path, repo_root: Path
) -> None:
    """Verify file type counts are accurate."""
    if not inventory_path.exists():
        subprocess.run(
            ["python3", str(discovery_script)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=60,
            check=True,
        )

    with open(inventory_path, encoding="utf-8") as f:
        inventory = yaml.safe_load(f)

    file_counts = inventory["file_type_counts"]

    assert "python_files" in file_counts
    assert "json_files" in file_counts
    assert "markdown_files" in file_counts

    assert isinstance(file_counts["python_files"], int)
    assert isinstance(file_counts["json_files"], int)
    assert isinstance(file_counts["markdown_files"], int)

    assert file_counts["python_files"] > 0, "Should have Python files"
    assert file_counts["json_files"] > 0, "Should have JSON files"
    assert file_counts["markdown_files"] > 0, "Should have Markdown files"


@pytest.mark.updated
def test_discovery_deterministic(
    discovery_script: Path, inventory_path: Path, repo_root: Path
) -> None:
    """Verify discovery protocol produces deterministic results (excluding timestamp)."""
    inventory_path.unlink(missing_ok=True)

    subprocess.run(
        ["python3", str(discovery_script)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )

    with open(inventory_path, encoding="utf-8") as f:
        inventory1 = yaml.safe_load(f)

    inventory_path.unlink()

    subprocess.run(
        ["python3", str(discovery_script)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )

    with open(inventory_path, encoding="utf-8") as f:
        inventory2 = yaml.safe_load(f)

    inventory1.pop("inventory_timestamp")
    inventory2.pop("inventory_timestamp")

    assert inventory1 == inventory2, "Discovery protocol should be deterministic"

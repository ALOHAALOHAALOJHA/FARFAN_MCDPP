"""
COHORT 2024 Migration Script
Systematically relocates calibration and parametrization files with metadata tracking.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

COHORT_ID = "COHORT_2024"
CREATION_DATE = datetime.now(timezone.utc).isoformat()
WAVE_VERSION = "REFACTOR_WAVE_2024_12"

REPO_ROOT = Path(__file__).parent.parent


def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA256 hash of file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def embed_metadata_header(content: str, file_type: str) -> str:
    """Embed cohort metadata header in file content."""
    metadata = {
        "cohort_id": COHORT_ID,
        "creation_date": CREATION_DATE,
        "wave_version": WAVE_VERSION,
    }

    if file_type == "json":
        data = json.loads(content)
        if "_cohort_metadata" not in data:
            data["_cohort_metadata"] = metadata
        return json.dumps(data, indent=2, ensure_ascii=False)
    elif file_type == "python":
        header = f'"""\n{COHORT_ID} - {WAVE_VERSION}\nCreated: {CREATION_DATE}\n"""\n\n'
        if not content.startswith('"""'):
            return header + content
        return content
    return content


def migrate_file(
    source_path: Path,
    dest_dir: Path,
    prefix: str = "COHORT_2024_",
    add_metadata: bool = True,
) -> dict[str, Any]:
    """
    Migrate a single file with cohort prefix and metadata.

    Returns migration record with paths and hashes.
    """
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")

    source_hash = calculate_sha256(source_path)

    new_filename = prefix + source_path.name
    dest_path = dest_dir / new_filename

    if add_metadata and source_path.suffix == ".json":
        with open(source_path, encoding="utf-8") as f:
            content = f.read()
        new_content = embed_metadata_header(content, "json")
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        dest_hash = calculate_sha256(dest_path)
    elif add_metadata and source_path.suffix == ".py":
        with open(source_path, encoding="utf-8") as f:
            content = f.read()
        new_content = embed_metadata_header(content, "python")
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        dest_hash = calculate_sha256(dest_path)
    else:
        shutil.copy2(source_path, dest_path)
        dest_hash = calculate_sha256(dest_path)

    return {
        "original_path": str(source_path.relative_to(REPO_ROOT)),
        "new_path": str(dest_path.relative_to(REPO_ROOT)),
        "original_filename": source_path.name,
        "new_filename": new_filename,
        "file_type": source_path.suffix[1:] if source_path.suffix else "unknown",
        "original_sha256": source_hash,
        "new_sha256": dest_hash,
        "cohort_metadata": {
            "cohort_id": COHORT_ID,
            "creation_date": CREATION_DATE,
            "wave_version": WAVE_VERSION,
        },
        "migration_timestamp": datetime.now(timezone.utc).isoformat(),
    }


CALIBRATION_FILES = [
    "system/config/calibration/intrinsic_calibration.json",
    "system/config/calibration/intrinsic_calibration_rubric.json",
    "system/config/questionnaire/questionnaire_monolith.json",
    "config/json_files_ no_schemas/method_compatibility.json",
    "config/json_files_ no_schemas/fusion_specification.json",
    "scripts/inventory/canonical_method_inventory.json",
    "src/farfan_pipeline/core/calibration/layer_assignment.py",
    "src/farfan_pipeline/core/calibration/layer_coexistence.py",
    "src/farfan_pipeline/core/calibration/layer_computers.py",
    "src/farfan_pipeline/core/calibration/layer_influence_model.py",
    "src/farfan_pipeline/core/calibration/chain_layer.py",
    "src/farfan_pipeline/core/calibration/congruence_layer.py",
    "src/farfan_pipeline/core/calibration/meta_layer.py",
    "src/farfan_pipeline/core/calibration/unit_layer.py",
    "src/farfan_pipeline/core/calibration/intrinsic_scoring.py",
    "src/farfan_pipeline/core/calibration/intrinsic_calibration_loader.py",
]

PARAMETRIZATION_FILES = [
    "system/config/calibration/runtime_layers.json",
    "config/json_files_ no_schemas/executor_config.json",
    "src/farfan_pipeline/core/orchestrator/executor_config.py",
    "src/farfan_pipeline/core/orchestrator/executor_profiler.py",
]


def run_migration() -> dict[str, Any]:
    """Execute full migration and return manifest."""
    calibration_dir = REPO_ROOT / "calibration_parametrization_system" / "calibration"
    parametrization_dir = (
        REPO_ROOT / "calibration_parametrization_system" / "parametrization"
    )

    calibration_dir.mkdir(parents=True, exist_ok=True)
    parametrization_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "manifest_version": "1.0.0",
        "cohort_id": COHORT_ID,
        "wave_version": WAVE_VERSION,
        "migration_date": datetime.now(timezone.utc).isoformat(),
        "description": "COHORT 2024 calibration/parametrization file relocation with metadata tracking",
        "calibration_files": [],
        "parametrization_files": [],
    }

    print(f"Migrating {len(CALIBRATION_FILES)} calibration files...")
    for file_path_str in CALIBRATION_FILES:
        file_path = REPO_ROOT / file_path_str
        if file_path.exists():
            try:
                record = migrate_file(file_path, calibration_dir)
                manifest["calibration_files"].append(record)
                print(f"  ✓ {file_path.name} -> {record['new_filename']}")
            except Exception as e:
                print(f"  ✗ Failed to migrate {file_path.name}: {e}")
        else:
            print(f"  ⚠ File not found: {file_path_str}")

    print(f"\nMigrating {len(PARAMETRIZATION_FILES)} parametrization files...")
    for file_path_str in PARAMETRIZATION_FILES:
        file_path = REPO_ROOT / file_path_str
        if file_path.exists():
            try:
                record = migrate_file(file_path, parametrization_dir)
                manifest["parametrization_files"].append(record)
                print(f"  ✓ {file_path.name} -> {record['new_filename']}")
            except Exception as e:
                print(f"  ✗ Failed to migrate {file_path.name}: {e}")
        else:
            print(f"  ⚠ File not found: {file_path_str}")

    manifest["statistics"] = {
        "total_calibration_files": len(manifest["calibration_files"]),
        "total_parametrization_files": len(manifest["parametrization_files"]),
        "total_files_migrated": len(manifest["calibration_files"])
        + len(manifest["parametrization_files"]),
    }

    manifest_path = (
        REPO_ROOT / "calibration_parametrization_system" / "COHORT_MANIFEST.json"
    )
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Migration complete! Manifest saved to {manifest_path}")
    print(f"  - Calibration files: {manifest['statistics']['total_calibration_files']}")
    print(
        f"  - Parametrization files: {manifest['statistics']['total_parametrization_files']}"
    )

    return manifest


if __name__ == "__main__":
    manifest = run_migration()

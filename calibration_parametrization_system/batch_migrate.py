"""
Batch migration script - creates all COHORT_2024 files with metadata.
Run this once to populate both calibration/ and parametrization/ directories.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
COHORT_META = {
    "cohort_id": "COHORT_2024",
    "creation_date": datetime.now(timezone.utc).isoformat(),
    "wave_version": "REFACTOR_WAVE_2024_12",
}


def migrate_json(src: Path, dest: Path) -> None:
    """Add cohort metadata to JSON and save."""
    with open(src, encoding="utf-8") as f:
        data = json.load(f)
    data["_cohort_metadata"] = COHORT_META
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✓ {dest.name}")


def migrate_py(src: Path, dest: Path) -> None:
    """Add cohort header to Python file and save."""
    header = f'"""\n{COHORT_META["cohort_id"]} - {COHORT_META["wave_version"]}\nCreated: {COHORT_META["creation_date"]}\n"""\n\n'
    with open(src, encoding="utf-8") as f:
        content = f.read()
    if not content.startswith('"""'):
        content = header + content
    with open(dest, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ {dest.name}")


CAL_DIR = REPO_ROOT / "calibration_parametrization_system/calibration"
PARAM_DIR = REPO_ROOT / "calibration_parametrization_system/parametrization"

CALIBRATION_MIGRATIONS = [
    (
        "system/config/calibration/intrinsic_calibration.json",
        "COHORT_2024_intrinsic_calibration.json",
    ),
    (
        "system/config/calibration/intrinsic_calibration_rubric.json",
        "COHORT_2024_intrinsic_calibration_rubric.json",
    ),
    (
        "system/config/questionnaire/questionnaire_monolith.json",
        "COHORT_2024_questionnaire_monolith.json",
    ),
    (
        "config/json_files_ no_schemas/method_compatibility.json",
        "COHORT_2024_method_compatibility.json",
    ),
    (
        "config/json_files_ no_schemas/fusion_specification.json",
        "COHORT_2024_fusion_weights.json",
    ),
    (
        "scripts/inventory/canonical_method_inventory.json",
        "COHORT_2024_canonical_method_inventory.json",
    ),
    (
        "src/farfan_pipeline/core/calibration/layer_assignment.py",
        "COHORT_2024_layer_assignment.py",
    ),
    (
        "src/farfan_pipeline/core/calibration/layer_coexistence.py",
        "COHORT_2024_layer_coexistence.py",
    ),
    (
        "src/farfan_pipeline/core/calibration/layer_computers.py",
        "COHORT_2024_layer_computers.py",
    ),
    (
        "src/farfan_pipeline/core/calibration/layer_influence_model.py",
        "COHORT_2024_layer_influence_model.py",
    ),
    (
        "src/farfan_pipeline/core/calibration/chain_layer.py",
        "COHORT_2024_chain_layer.py",
    ),
    (
        "src/farfan_pipeline/core/calibration/congruence_layer.py",
        "COHORT_2024_congruence_layer.py",
    ),
    ("src/farfan_pipeline/core/calibration/meta_layer.py", "COHORT_2024_meta_layer.py"),
    ("src/farfan_pipeline/core/calibration/unit_layer.py", "COHORT_2024_unit_layer.py"),
    (
        "src/farfan_pipeline/core/calibration/intrinsic_scoring.py",
        "COHORT_2024_intrinsic_scoring.py",
    ),
    (
        "src/farfan_pipeline/core/calibration/intrinsic_calibration_loader.py",
        "COHORT_2024_intrinsic_calibration_loader.py",
    ),
]

PARAMETRIZATION_MIGRATIONS = [
    (
        "system/config/calibration/runtime_layers.json",
        "COHORT_2024_runtime_layers.json",
    ),
    (
        "config/json_files_ no_schemas/executor_config.json",
        "COHORT_2024_executor_config.json",
    ),
    (
        "src/farfan_pipeline/core/orchestrator/executor_config.py",
        "COHORT_2024_executor_config.py",
    ),
    (
        "src/farfan_pipeline/core/orchestrator/executor_profiler.py",
        "COHORT_2024_executor_profiler.py",
    ),
]

print("=" * 60)
print("COHORT 2024 BATCH MIGRATION")
print("=" * 60)

print("\n[CALIBRATION FILES]")
for src_rel, dest_name in CALIBRATION_MIGRATIONS:
    src = REPO_ROOT / src_rel
    dest = CAL_DIR / dest_name
    if not src.exists():
        print(f"⚠ SKIP {dest_name} (source not found)")
        continue
    if src.suffix == ".json":
        migrate_json(src, dest)
    elif src.suffix == ".py":
        migrate_py(src, dest)

print("\n[PARAMETRIZATION FILES]")
for src_rel, dest_name in PARAMETRIZATION_MIGRATIONS:
    src = REPO_ROOT / src_rel
    dest = PARAM_DIR / dest_name
    if not src.exists():
        print(f"⚠ SKIP {dest_name} (source not found)")
        continue
    if src.suffix == ".json":
        migrate_json(src, dest)
    elif src.suffix == ".py":
        migrate_py(src, dest)

print("\n" + "=" * 60)
print("MIGRATION COMPLETE")
print("=" * 60)

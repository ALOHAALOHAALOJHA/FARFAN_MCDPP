# tests/test_sisas/scripts/test_generate_contracts.py

import pytest
import csv
import json
import tempfile
from pathlib import Path
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.scripts.generate_contracts import (
    generate_contracts_from_csv,
    generate_gap_resolution_tasks,
    ContractStatus
)

@pytest.fixture
def sample_csv():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow([
            "json_file_path", "stage", "phase",
            "vehiculos_str", "consumidores_str",
            "irrigability_bucket", "gaps_str", "added_value", "file_bytes"
        ])
        # Active contract
        writer.writerow([
            "active.json", "phase_00", "Phase_00",
            "v1", "c1",
            "irrigable_now", "", "YES", "100"
        ])
        # Pending contract
        writer.writerow([
            "pending.json", "phase_00", "Phase_00",
            "NINGUNO", "c1",
            "not_irrigable_yet", "NECESITA_VEHICULO", "YES", "100"
        ])
        return f.name

def test_generate_contracts(sample_csv):
    registry = generate_contracts_from_csv(sample_csv)
    assert len(registry.irrigation_contracts) == 2

    active = [c for c in registry.irrigation_contracts.values() if c.status == ContractStatus.ACTIVE]
    assert len(active) == 1
    assert active[0].source_file == "active.json"

    pending = [c for c in registry.irrigation_contracts.values() if c.status == ContractStatus.DRAFT]
    assert len(pending) == 1
    assert pending[0].source_file == "pending.json"

def test_gap_resolution_tasks(sample_csv):
    registry = generate_contracts_from_csv(sample_csv)
    tasks = generate_gap_resolution_tasks(registry)

    assert len(tasks) == 1
    assert tasks[0]["gap_type"] == "NECESITA_VEHICULO"
    assert tasks[0]["files_affected"] == 1

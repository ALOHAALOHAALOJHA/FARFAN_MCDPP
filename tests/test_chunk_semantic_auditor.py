import json
import tempfile
from pathlib import Path

import pytest

from tools.chunk_semantic_auditor import (
    ChunkMetadata,
    ChunkSemanticAuditor,
    SemanticAuditResult,
)


@pytest.fixture
def temp_artifacts_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_chunks_file(temp_artifacts_dir):
    chunks_data = {
        "chunks": [
            {
                "chunk_id": "chunk_001",
                "policy_area_id": "PA01",
                "dimension_id": "DIM01",
                "text": "The budget allocation for economic development includes funding for small business support programs, entrepreneurship training, and innovation infrastructure with a total investment of $5 million.",
            },
            {
                "chunk_id": "chunk_002",
                "policy_area_id": "PA02",
                "dimension_id": "DIM03",
                "text": "The health program will deliver 50 community clinics, vaccinate 100,000 children, and provide free medical consultations to vulnerable populations.",
            },
            {
                "chunk_id": "chunk_003",
                "policy_area_id": "PA04",
                "dimension_id": "DIM06",
                "text": "The causal link between reforestation activities and improved air quality will be measured through PM2.5 monitoring stations and longitudinal health studies.",
            },
        ]
    }

    chunks_file = temp_artifacts_dir / "test_chunks.json"
    with open(chunks_file, "w") as f:
        json.dump(chunks_data, f)

    return chunks_file


@pytest.fixture
def mismatched_chunks_file(temp_artifacts_dir):
    chunks_data = {
        "chunks": [
            {
                "chunk_id": "chunk_mismatch",
                "policy_area_id": "PA01",
                "dimension_id": "DIM01",
                "text": "This text discusses cultural heritage preservation and traditional music festivals, which has nothing to do with economic development or inputs.",
            }
        ]
    }

    chunks_file = temp_artifacts_dir / "mismatched_chunks.json"
    with open(chunks_file, "w") as f:
        json.dump(chunks_data, f)

    return chunks_file


def test_chunk_metadata_creation():
    chunk = ChunkMetadata(
        chunk_id="test_001",
        file_path="test.json",
        policy_area_id="PA01",
        dimension_id="DIM01",
        text_content="Sample text",
    )

    assert chunk.chunk_id == "test_001"
    assert chunk.policy_area_id == "PA01"
    assert chunk.dimension_id == "DIM01"


def test_auditor_initialization(temp_artifacts_dir):
    auditor = ChunkSemanticAuditor(
        artifacts_dir=temp_artifacts_dir, threshold=0.7, verbose=False
    )

    assert auditor.artifacts_dir == temp_artifacts_dir
    assert auditor.threshold == 0.7
    assert auditor.model is None
    assert len(auditor.chunks) == 0


def test_load_model(temp_artifacts_dir):
    auditor = ChunkSemanticAuditor(artifacts_dir=temp_artifacts_dir, verbose=False)
    auditor.load_model()

    assert auditor.model is not None


def test_discover_chunk_artifacts(sample_chunks_file, temp_artifacts_dir):
    auditor = ChunkSemanticAuditor(artifacts_dir=temp_artifacts_dir, verbose=False)
    chunk_files = auditor.discover_chunk_artifacts()

    assert len(chunk_files) >= 1
    assert sample_chunks_file in chunk_files


def test_load_chunk_metadata(sample_chunks_file, temp_artifacts_dir):
    auditor = ChunkSemanticAuditor(artifacts_dir=temp_artifacts_dir, verbose=False)
    chunks = auditor.load_chunk_metadata(sample_chunks_file)

    assert len(chunks) == 3
    assert chunks[0].chunk_id == "chunk_001"
    assert chunks[0].policy_area_id == "PA01"
    assert chunks[0].dimension_id == "DIM01"
    assert "economic development" in chunks[0].text_content.lower()


def test_load_all_chunks(sample_chunks_file, temp_artifacts_dir):
    auditor = ChunkSemanticAuditor(artifacts_dir=temp_artifacts_dir, verbose=False)
    auditor.load_all_chunks()

    assert len(auditor.chunks) == 3


def test_compute_semantic_coherence(sample_chunks_file, temp_artifacts_dir):
    auditor = ChunkSemanticAuditor(artifacts_dir=temp_artifacts_dir, verbose=False)
    auditor.load_model()
    auditor.load_all_chunks()

    chunk = auditor.chunks[0]
    score = auditor.compute_semantic_coherence(chunk)

    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_audit_chunk_pass(sample_chunks_file, temp_artifacts_dir):
    auditor = ChunkSemanticAuditor(
        artifacts_dir=temp_artifacts_dir, threshold=0.3, verbose=False
    )
    auditor.load_model()
    auditor.load_all_chunks()

    chunk = auditor.chunks[0]
    result = auditor.audit_chunk(chunk)

    assert isinstance(result, SemanticAuditResult)
    assert result.chunk_id == chunk.chunk_id
    assert result.passed is True


def test_audit_chunk_fail(mismatched_chunks_file, temp_artifacts_dir):
    auditor = ChunkSemanticAuditor(
        artifacts_dir=temp_artifacts_dir, threshold=0.7, verbose=False
    )
    auditor.load_model()
    auditor.load_all_chunks()

    chunk = auditor.chunks[0]
    result = auditor.audit_chunk(chunk)

    assert isinstance(result, SemanticAuditResult)
    assert result.passed is False
    assert result.coherence_score < 0.7


def test_audit_all_chunks(sample_chunks_file, temp_artifacts_dir):
    auditor = ChunkSemanticAuditor(
        artifacts_dir=temp_artifacts_dir, threshold=0.3, verbose=False
    )
    auditor.load_model()
    auditor.load_all_chunks()
    auditor.audit_all_chunks()

    assert len(auditor.audit_results) == 3
    assert all(isinstance(r, SemanticAuditResult) for r in auditor.audit_results)


def test_generate_report(sample_chunks_file, temp_artifacts_dir):
    auditor = ChunkSemanticAuditor(
        artifacts_dir=temp_artifacts_dir, threshold=0.3, verbose=False
    )
    auditor.load_model()
    auditor.load_all_chunks()
    auditor.audit_all_chunks()

    report = auditor.generate_report()

    assert "metadata" in report
    assert "summary" in report
    assert "failures" in report
    assert report["metadata"]["total_chunks_audited"] == 3
    assert report["summary"]["passed"] >= 0
    assert report["summary"]["failed"] >= 0
    assert report["summary"]["pass_rate"] >= 0.0


def test_save_report(sample_chunks_file, temp_artifacts_dir):
    auditor = ChunkSemanticAuditor(
        artifacts_dir=temp_artifacts_dir, threshold=0.3, verbose=False
    )
    auditor.load_model()
    auditor.load_all_chunks()
    auditor.audit_all_chunks()

    report = auditor.generate_report()
    output_file = temp_artifacts_dir / "test_report.json"
    auditor.save_report(report, output_file)

    assert output_file.exists()

    with open(output_file) as f:
        loaded_report = json.load(f)

    assert loaded_report == report


def test_full_audit_workflow(sample_chunks_file, temp_artifacts_dir):
    auditor = ChunkSemanticAuditor(
        artifacts_dir=temp_artifacts_dir, threshold=0.3, verbose=False
    )

    exit_code = auditor.run()

    assert exit_code in [0, 1]
    assert (temp_artifacts_dir / "semantic_audit_report.json").exists()


def test_empty_artifacts_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        auditor = ChunkSemanticAuditor(artifacts_dir=Path(tmpdir), verbose=False)
        auditor.load_model()
        auditor.load_all_chunks()

        assert len(auditor.chunks) == 0


def test_invalid_json_file(temp_artifacts_dir):
    invalid_file = temp_artifacts_dir / "invalid_chunks.json"
    with open(invalid_file, "w") as f:
        f.write("{ invalid json }")

    auditor = ChunkSemanticAuditor(artifacts_dir=temp_artifacts_dir, verbose=False)
    chunks = auditor.load_chunk_metadata(invalid_file)

    assert len(chunks) == 0


def test_missing_metadata_fields(temp_artifacts_dir):
    incomplete_chunks = {
        "chunks": [
            {"chunk_id": "c1", "text": "text only"},
            {"policy_area_id": "PA01", "text": "missing dimension"},
            {"dimension_id": "DIM01", "text": "missing policy area"},
        ]
    }

    chunks_file = temp_artifacts_dir / "incomplete.json"
    with open(chunks_file, "w") as f:
        json.dump(incomplete_chunks, f)

    auditor = ChunkSemanticAuditor(artifacts_dir=temp_artifacts_dir, verbose=False)
    chunks = auditor.load_chunk_metadata(chunks_file)

    assert len(chunks) == 0

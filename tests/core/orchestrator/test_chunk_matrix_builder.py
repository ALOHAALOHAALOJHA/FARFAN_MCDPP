"""Unit tests for chunk matrix builder module."""

import pytest
from pathlib import Path

from farfan_pipeline.core.types import ChunkData, PreprocessedDocument, Provenance
from farfan_pipeline.core.orchestrator.chunk_matrix_builder import (
    build_chunk_matrix,
    EXPECTED_CHUNK_COUNT,
    POLICY_AREAS,
    DIMENSIONS,
)


def create_chunk(
    chunk_id: int,
    policy_area_id: str,
    dimension_id: str,
    text: str = "Test chunk content",
) -> ChunkData:
    """Helper to create a valid ChunkData instance."""
    return ChunkData(
        id=chunk_id,
        text=text,
        chunk_type="diagnostic",
        sentences=[],
        tables=[],
        start_pos=0,
        end_pos=len(text),
        confidence=0.9,
        chunk_id=f"{policy_area_id}-{dimension_id}",
        policy_area_id=policy_area_id,
        dimension_id=dimension_id,
        provenance=Provenance(page_number=1),
    )


def create_full_document() -> PreprocessedDocument:
    """Create a valid PreprocessedDocument with all 60 chunks."""
    chunks = []
    idx = 0
    for pa in POLICY_AREAS:
        for dim in DIMENSIONS:
            chunks.append(create_chunk(idx, pa, dim, f"Content for {pa}-{dim}"))
            idx += 1
    
    return PreprocessedDocument(
        document_id="test-doc-001",
        raw_text="Complete policy document text",
        sentences=[],
        tables=[],
        metadata={"chunk_count": 60},
        chunks=chunks,
        processing_mode="chunked",
    )


def test_build_chunk_matrix_success():
    """build_chunk_matrix should accept exactly 60 valid chunks."""
    doc = create_full_document()
    matrix, keys = build_chunk_matrix(doc)
    
    assert len(matrix) == EXPECTED_CHUNK_COUNT
    assert len(keys) == EXPECTED_CHUNK_COUNT
    assert keys[0] == ("PA01", "DIM01")
    assert keys[-1] == ("PA10", "DIM06")
    
    chunk = matrix[("PA05", "DIM03")]
    assert chunk.policy_area_id == "PA05"
    assert chunk.dimension_id == "DIM03"
    assert chunk.text == "Content for PA05-DIM03"


def test_build_chunk_matrix_sorted_keys():
    """Keys should be sorted deterministically by PA then DIM."""
    doc = create_full_document()
    _, keys = build_chunk_matrix(doc)
    
    assert keys[0] == ("PA01", "DIM01")
    assert keys[5] == ("PA01", "DIM06")
    assert keys[6] == ("PA02", "DIM01")
    assert keys[-1] == ("PA10", "DIM06")
    
    for i in range(len(keys) - 1):
        assert keys[i] < keys[i + 1], f"Keys not sorted: {keys[i]} >= {keys[i+1]}"


def test_build_chunk_matrix_rejects_59_chunks():
    """build_chunk_matrix should reject documents with 59 chunks."""
    chunks = []
    idx = 0
    for pa in POLICY_AREAS:
        for dim in DIMENSIONS:
            if pa == "PA10" and dim == "DIM06":
                break
            chunks.append(create_chunk(idx, pa, dim))
            idx += 1
    
    doc = PreprocessedDocument(
        document_id="test-doc-002",
        raw_text="Incomplete document",
        sentences=[],
        tables=[],
        metadata={},
        chunks=chunks,
    )
    
    with pytest.raises(ValueError, match=r"Missing chunk combinations: .*PA10', 'DIM06'.*"):
        build_chunk_matrix(doc)


def test_build_chunk_matrix_rejects_61_chunks():
    """build_chunk_matrix should reject documents with 61 chunks."""
    chunks = []
    idx = 0
    for pa in POLICY_AREAS:
        for dim in DIMENSIONS:
            chunks.append(create_chunk(idx, pa, dim))
            idx += 1
    
    chunks.append(create_chunk(idx, "PA01", "DIM01", "Duplicate chunk"))
    
    doc = PreprocessedDocument(
        document_id="test-doc-003",
        raw_text="Document with duplicate",
        sentences=[],
        tables=[],
        metadata={},
        chunks=chunks,
    )
    
    with pytest.raises(ValueError, match="Duplicate.*PA01-DIM01"):
        build_chunk_matrix(doc)


def test_build_chunk_matrix_detects_duplicate_keys():
    """build_chunk_matrix should reject duplicate (PA, DIM) combinations."""
    chunks = []
    idx = 0
    for pa in POLICY_AREAS:
        for dim in DIMENSIONS:
            if pa == "PA05" and dim == "DIM03":
                continue
            chunks.append(create_chunk(idx, pa, dim))
            idx += 1
    
    chunks.append(create_chunk(idx, "PA01", "DIM01", "Duplicate chunk"))
    
    doc = PreprocessedDocument(
        document_id="test-doc-004",
        raw_text="Document with duplicate key",
        sentences=[],
        tables=[],
        metadata={},
        chunks=chunks,
    )
    
    with pytest.raises(ValueError, match="Duplicate.*PA01-DIM01"):
        build_chunk_matrix(doc)


def test_build_chunk_matrix_detects_missing_combinations():
    """build_chunk_matrix should detect missing PA×DIM combinations."""
    chunks = []
    idx = 0
    for pa in POLICY_AREAS:
        for dim in DIMENSIONS:
            if pa == "PA05" and dim == "DIM03":
                continue
            chunks.append(create_chunk(idx, pa, dim))
            idx += 1
    
    chunks.append(create_chunk(idx, "PA05", "DIM04"))
    
    doc = PreprocessedDocument(
        document_id="test-doc-005",
        raw_text="Document with duplicate and missing",
        sentences=[],
        tables=[],
        metadata={},
        chunks=chunks,
    )
    
    with pytest.raises(ValueError, match="Duplicate.*PA05-DIM04"):
        build_chunk_matrix(doc)


def test_build_chunk_matrix_reports_specific_missing_key():
    """build_chunk_matrix should report specific missing PA-DIM combination."""
    chunks = []
    idx = 0
    for pa in POLICY_AREAS:
        for dim in DIMENSIONS:
            if pa == "PA05" and dim == "DIM03":
                continue
            if pa == "PA07" and dim == "DIM02":
                continue
            chunks.append(create_chunk(idx, pa, dim))
            idx += 1
    
    doc = PreprocessedDocument(
        document_id="test-doc-006",
        raw_text="Document missing PA05-DIM03 and PA07-DIM02",
        sentences=[],
        tables=[],
        metadata={},
        chunks=chunks,
    )
    
    with pytest.raises(ValueError) as exc_info:
        build_chunk_matrix(doc)
    assert (
        "Missing chunk combinations: [('PA05', 'DIM03'), ('PA07', 'DIM02')]"
        in str(exc_info.value)
    )


def test_build_chunk_matrix_rejects_null_policy_area():
    """build_chunk_matrix should reject chunks with null policy_area_id."""
    chunks = []
    idx = 0
    for pa in POLICY_AREAS:
        for dim in DIMENSIONS:
            if pa == "PA01" and dim == "DIM01":
                chunk = ChunkData(
                    id=idx,
                    text="Test",
                    chunk_type="diagnostic",
                    sentences=[],
                    tables=[],
                    start_pos=0,
                    end_pos=4,
                    confidence=0.9,
                    chunk_id="PA01-DIM01",
                    policy_area_id=None,
                    dimension_id=dim,
                )
                chunks.append(chunk)
            else:
                chunks.append(create_chunk(idx, pa, dim))
            idx += 1
    
    doc = PreprocessedDocument(
        document_id="test-doc-007",
        raw_text="Document with null policy_area_id",
        sentences=[],
        tables=[],
        metadata={},
        chunks=chunks,
    )
    
    with pytest.raises(ValueError, match="null policy_area_id"):
        build_chunk_matrix(doc)


def test_build_chunk_matrix_rejects_null_dimension():
    """build_chunk_matrix should reject chunks with null dimension_id."""
    chunks = []
    idx = 0
    for pa in POLICY_AREAS:
        for dim in DIMENSIONS:
            if pa == "PA01" and dim == "DIM01":
                chunk = ChunkData(
                    id=idx,
                    text="Test",
                    chunk_type="diagnostic",
                    sentences=[],
                    tables=[],
                    start_pos=0,
                    end_pos=4,
                    confidence=0.9,
                    chunk_id="PA01-DIM01",
                    policy_area_id=pa,
                    dimension_id=None,
                )
                chunks.append(chunk)
            else:
                chunks.append(create_chunk(idx, pa, dim))
            idx += 1
    
    doc = PreprocessedDocument(
        document_id="test-doc-008",
        raw_text="Document with null dimension_id",
        sentences=[],
        tables=[],
        metadata={},
        chunks=chunks,
    )
    
    with pytest.raises(ValueError, match="null dimension_id"):
        build_chunk_matrix(doc)


def test_build_chunk_matrix_rejects_invalid_policy_area():
    """build_chunk_matrix should reject invalid policy area format."""
    with pytest.raises(ValueError, match="Invalid chunk_id 'PA00-DIM01'"):
        create_chunk(0, "PA00", "DIM01")


def test_build_chunk_matrix_rejects_invalid_dimension():
    """build_chunk_matrix should reject invalid dimension format."""
    with pytest.raises(ValueError, match="Invalid chunk_id 'PA01-DIM07'"):
        create_chunk(0, "PA01", "DIM07")


def test_build_chunk_matrix_rejects_malformed_chunk_id():
    """build_chunk_matrix should reject malformed chunk IDs."""
    with pytest.raises(ValueError, match="Invalid chunk_id 'P01-DIM01'"):
        create_chunk(0, "P01", "DIM01")


def test_build_chunk_matrix_preserves_content():
    """build_chunk_matrix should preserve chunk content and metadata."""
    doc = create_full_document()
    matrix, _ = build_chunk_matrix(doc)
    
    chunk = matrix[("PA07", "DIM04")]
    assert chunk.text == "Content for PA07-DIM04"
    assert chunk.policy_area_id == "PA07"
    assert chunk.dimension_id == "DIM04"
    assert chunk.chunk_type == "diagnostic"
    assert chunk.confidence == 0.9
    assert chunk.provenance is not None
    assert chunk.provenance.page_number == 1


def test_build_chunk_matrix_deterministic_ordering():
    """Multiple calls should produce identical key ordering."""
    doc = create_full_document()
    
    _, keys1 = build_chunk_matrix(doc)
    _, keys2 = build_chunk_matrix(doc)
    
    assert keys1 == keys2


def test_build_chunk_matrix_all_combinations_present():
    """Matrix should contain all 60 PA×DIM combinations."""
    doc = create_full_document()
    matrix, _ = build_chunk_matrix(doc)
    
    for pa in POLICY_AREAS:
        for dim in DIMENSIONS:
            assert (pa, dim) in matrix
            chunk = matrix[(pa, dim)]
            assert chunk.policy_area_id == pa
            assert chunk.dimension_id == dim

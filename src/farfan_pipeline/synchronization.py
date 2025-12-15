from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

logger = logging.getLogger(__name__)

_PA_RE = re.compile(r"^PA(0[1-9]|10)$")
_DIM_RE = re.compile(r"^DIM0[1-6]$")
_CHUNK_ID_RE = re.compile(r"^PA(0[1-9]|10)-DIM0[1-6]$")


def _get_mapping_value(obj: Any, key: str) -> Any:  # noqa: ANN401
    if isinstance(obj, Mapping):
        return obj.get(key)
    return None


def _get_attr_or_key(obj: Any, name: str) -> Any:  # noqa: ANN401
    value = _get_mapping_value(obj, name)
    if value is not None:
        return value
    return getattr(obj, name, None)


def _coerce_id(value: Any) -> str | None:  # noqa: ANN401
    if isinstance(value, str):
        return value
    if hasattr(value, "value") and isinstance(value.value, str):
        return value.value
    return None


def _extract_policy_area_id(chunk: Any) -> str:
    pa_id = _coerce_id(_get_attr_or_key(chunk, "policy_area_id"))
    if pa_id is None:
        pa_id = _coerce_id(_get_attr_or_key(chunk, "policy_area"))
    if pa_id is None:
        chunk_id = _coerce_id(_get_attr_or_key(chunk, "chunk_id")) or _coerce_id(
            _get_attr_or_key(chunk, "id")
        )
        if chunk_id:
            normalized = chunk_id.replace("_", "-")
            if _CHUNK_ID_RE.match(normalized):
                return normalized.split("-", 1)[0]
    if pa_id is None:
        raise ValueError("Chunk missing policy_area_id")
    return pa_id


def _extract_dimension_id(chunk: Any) -> str:
    dim_id = _coerce_id(_get_attr_or_key(chunk, "dimension_id"))
    if dim_id is None:
        dim_id = _coerce_id(_get_attr_or_key(chunk, "dimension"))
    if dim_id is None:
        dim_id = _coerce_id(_get_attr_or_key(chunk, "dimension_causal"))
    if dim_id is None:
        chunk_id = _coerce_id(_get_attr_or_key(chunk, "chunk_id")) or _coerce_id(
            _get_attr_or_key(chunk, "id")
        )
        if chunk_id:
            normalized = chunk_id.replace("_", "-")
            if _CHUNK_ID_RE.match(normalized):
                return normalized.split("-", 1)[1]
    if dim_id is None:
        raise ValueError("Chunk missing dimension_id")
    return dim_id


def _extract_text(chunk: Any) -> str:
    text = _get_attr_or_key(chunk, "text")
    if not isinstance(text, str):
        raise ValueError(f"Chunk text must be str, got {type(text).__name__}")
    return text


def _extract_document_position(chunk: Any) -> tuple[int, int] | None:
    start = _get_attr_or_key(chunk, "start_offset")
    end = _get_attr_or_key(chunk, "end_offset")
    if isinstance(start, int) and isinstance(end, int):
        if start < 0 or end < start:
            raise ValueError(f"Invalid document position: ({start}, {end})")
        return (start, end)

    start = _get_attr_or_key(chunk, "start_pos")
    end = _get_attr_or_key(chunk, "end_pos")
    if isinstance(start, int) and isinstance(end, int):
        if start < 0 or end < start:
            raise ValueError(f"Invalid document position: ({start}, {end})")
        return (start, end)

    text_span = _get_attr_or_key(chunk, "text_span")
    if text_span is not None:
        start = getattr(text_span, "start", None)
        end = getattr(text_span, "end", None)
        if isinstance(start, int) and isinstance(end, int):
            if start < 0 or end < start:
                raise ValueError(f"Invalid document position: ({start}, {end})")
            return (start, end)

    return None


def _validate_ids(policy_area_id: str, dimension_id: str) -> None:
    if not _PA_RE.match(policy_area_id):
        raise ValueError(f"Invalid policy_area_id: {policy_area_id}")
    if not _DIM_RE.match(dimension_id):
        raise ValueError(f"Invalid dimension_id: {dimension_id}")


def _validate_chunk_identity(chunk: Any, *, expected_chunk_id: str) -> None:  # noqa: ANN401
    if not _CHUNK_ID_RE.match(expected_chunk_id):
        raise ValueError(f"Invalid chunk_id format: {expected_chunk_id}")

    declared = _coerce_id(_get_attr_or_key(chunk, "chunk_id"))
    if declared is not None and declared != expected_chunk_id:
        raise ValueError(
            f"Chunk identity mismatch: expected chunk_id={expected_chunk_id} but got {declared}"
        )

    legacy_id = _coerce_id(_get_attr_or_key(chunk, "id"))
    if legacy_id is not None:
        normalized = legacy_id.replace("_", "-")
        if normalized != expected_chunk_id:
            raise ValueError(
                "Chunk identity mismatch: expected chunk_id="
                f"{expected_chunk_id} but got id={legacy_id}"
            )


@dataclass(frozen=True, slots=True)
class SmartPolicyChunk:
    chunk_id: str
    policy_area_id: str
    dimension_id: str
    text: str
    document_position: tuple[int, int] | None
    raw_chunk: Any | None = None

    @property
    def start_pos(self) -> int | None:
        if self.document_position is None:
            return None
        return self.document_position[0]

    @property
    def end_pos(self) -> int | None:
        if self.document_position is None:
            return None
        return self.document_position[1]


class ChunkMatrix:
    """60-slot PA×DIM chunk matrix with strict invariant validation."""

    EXPECTED_CHUNK_COUNT = 60

    def __init__(self, document: Any) -> None:  # noqa: ANN401
        self._preprocessed_document = document
        chunks = self._extract_chunks(document)
        self._chunk_matrix = self._build_matrix(chunks)
        self._matrix_keys_sorted = tuple(sorted(self._chunk_matrix.keys()))
        self._integrity_hash = self._compute_integrity_hash()

    @property
    def chunk_matrix(self) -> dict[tuple[str, str], SmartPolicyChunk]:
        return dict(self._chunk_matrix)

    @property
    def matrix_keys_sorted(self) -> tuple[tuple[str, str], ...]:
        return self._matrix_keys_sorted

    @property
    def integrity_hash(self) -> str:
        return self._integrity_hash

    def raw_chunks_sorted(self) -> tuple[Any, ...]:  # noqa: ANN401
        raw_chunks: list[Any] = []
        for key in self._matrix_keys_sorted:
            raw = self._chunk_matrix[key].raw_chunk
            if raw is None:
                raise ValueError(f"ChunkMatrix missing raw_chunk for key={key}")
            raw_chunks.append(raw)
        return tuple(raw_chunks)

    def get_chunk(self, policy_area_id: str, dimension_id: str) -> SmartPolicyChunk:
        return self._chunk_matrix[(policy_area_id, dimension_id)]

    @staticmethod
    def _extract_chunks(document: Any) -> list[Any]:  # noqa: ANN401
        if document is None:
            raise ValueError("document is required")

        chunks = _get_attr_or_key(document, "chunks")
        if isinstance(chunks, Sequence) and not isinstance(chunks, (str, bytes)):
            return list(chunks)

        chunk_graph = _get_attr_or_key(document, "chunk_graph")
        if chunk_graph is not None:
            graph_chunks = _get_attr_or_key(chunk_graph, "chunks")
            if isinstance(graph_chunks, Mapping):
                return list(graph_chunks.values())

        if isinstance(document, Sequence) and not isinstance(document, (str, bytes)):
            return list(document)

        raise TypeError(
            "Unsupported document type for ChunkMatrix; expected .chunks sequence, "
            ".chunk_graph.chunks mapping, or a sequence of chunks"
        )

    @classmethod
    def _build_matrix(cls, chunks: Sequence[Any]) -> dict[tuple[str, str], SmartPolicyChunk]:
        chunk_matrix: dict[tuple[str, str], SmartPolicyChunk] = {}

        inserted_count = 0
        for chunk in chunks:
            inserted_count += 1
            policy_area_id = _extract_policy_area_id(chunk)
            dimension_id = _extract_dimension_id(chunk)
            _validate_ids(policy_area_id, dimension_id)

            expected_chunk_id = f"{policy_area_id}-{dimension_id}"
            _validate_chunk_identity(chunk, expected_chunk_id=expected_chunk_id)

            text = _extract_text(chunk)
            if not text.strip():
                raise ValueError(f"Chunk {expected_chunk_id} has empty text")

            document_position = _extract_document_position(chunk)

            key = (policy_area_id, dimension_id)
            if key in chunk_matrix:
                raise ValueError(
                    f"Duplicate chunk slot detected for key={key}. "
                    f"Inserted={inserted_count}, unique={len(chunk_matrix)}"
                )

            chunk_matrix[key] = SmartPolicyChunk(
                chunk_id=expected_chunk_id,
                policy_area_id=policy_area_id,
                dimension_id=dimension_id,
                text=text,
                document_position=document_position,
                raw_chunk=chunk,
            )

        if len(chunk_matrix) != cls.EXPECTED_CHUNK_COUNT:
            raise ValueError(
                "Chunk Matrix Invariant Violation: Expected 60 unique (PA, DIM) chunks "
                f"but found {len(chunk_matrix)}"
            )

        expected_keys = {
            (f"PA{pa:02d}", f"DIM{dim:02d}") for pa in range(1, 11) for dim in range(1, 7)
        }
        missing = expected_keys - set(chunk_matrix.keys())
        if missing:
            raise ValueError(f"Missing chunk combinations: {sorted(missing)}")

        chunks_per_policy_area = {
            f"PA{pa:02d}": sum(1 for (pa_id, _) in chunk_matrix if pa_id == f"PA{pa:02d}")
            for pa in range(1, 11)
        }
        chunks_per_dimension = {
            f"DIM{dim:02d}": sum(
                1 for (_, dim_id) in chunk_matrix if dim_id == f"DIM{dim:02d}"
            )
            for dim in range(1, 7)
        }

        logger.info(
            "chunk_matrix_constructed",
            extra={
                "total_chunks": len(chunk_matrix),
                "inserted_count": inserted_count,
                "chunks_per_policy_area": chunks_per_policy_area,
                "chunks_per_dimension": chunks_per_dimension,
            },
        )

        return chunk_matrix

    def _compute_integrity_hash(self) -> str:
        payload = []
        for (pa_id, dim_id) in self._matrix_keys_sorted:
            chunk = self._chunk_matrix[(pa_id, dim_id)]
            text_hash = hashlib.sha256(chunk.text.encode("utf-8")).hexdigest()
            payload.append(
                {
                    "policy_area_id": pa_id,
                    "dimension_id": dim_id,
                    "chunk_id": chunk.chunk_id,
                    "text_sha256": text_hash,
                }
            )

        json_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(json_bytes).hexdigest()


__all__ = ["ChunkMatrix", "SmartPolicyChunk"]

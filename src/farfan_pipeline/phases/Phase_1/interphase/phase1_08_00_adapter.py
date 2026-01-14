"""CPP to Orchestrator Adapter.

This adapter converts Canon Policy Package (CPP) documents from the ingestion pipeline
into the orchestrator's PreprocessedDocument format.

Note: This is the canonical adapter implementation. File cpp_to_orchestrator.py is
deprecated and should be removed.

Design Principles:
- Preserves complete provenance information
- Orders chunks by text_span. start for deterministic ordering
- Computes provenance_completeness metric
- Provides prescriptive error messages on failure
- Supports micro, meso, and macro chunk resolutions
- Optional dependencies handled gracefully (pyarrow, structlog)

Architecture:
- ChunkArtifacts: Immutable container for all outputs from processing a single chunk
- _resolve_chunk_attributes: Single-pass attribute extraction from chunk objects
- _process_chunk:  Encapsulates per-chunk processing logic with strict validation
- to_preprocessed_document:  Orchestrates conversion with 6-layer validation
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 1
__stage__ = 30
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-10"
__criticality__ = "MEDIUM"
__execution_pattern__ = "On-Demand"

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from types import MappingProxyType
from typing import Any, Final

from farfan_pipeline.infrastructure.calibration.parameters import ParameterLoaderV2
from farfan_pipeline.core.types import ChunkData, PreprocessedDocument, Provenance

logger = logging.getLogger(__name__)

_EMPTY_MAPPING: Final[MappingProxyType[str, Any]] = MappingProxyType({})

_VALID_CHUNK_TYPES: Final[frozenset[str]] = frozenset(
    {
        "diagnostic",
        "activity",
        "indicator",
        "resource",
        "temporal",
        "entity",
    }
)


@dataclass(frozen=True, slots=True)
class ChunkArtifacts:
    """Immutable container for all outputs produced by processing a single chunk.

    Attributes:
        sentence:  Sentence representation for orchestrator compatibility
        sentence_metadata: Positional and contextual metadata for the sentence
        chunk_summary: Summary metrics and identifiers for the chunk
        chunk_data: ChunkData object for the orchestrator
        table:  Optional budget table extracted from chunk
        entity_mentions:  Mapping of entity text to chunk indices where mentioned
        temporal_mentions: Mapping of year strings to chunk indices where mentioned
        chunk_text_length: Length of chunk text (for offset calculation)
        has_provenance: Whether chunk has valid provenance data
    """

    sentence: dict[str, Any]
    sentence_metadata: dict[str, Any]
    chunk_summary: dict[str, Any]
    chunk_data: ChunkData
    table: dict[str, Any] | None
    entity_mentions: dict[str, list[int]]
    temporal_mentions: dict[str, list[int]]
    chunk_text_length: int
    has_provenance: bool


class CPPAdapterError(Exception):
    """Raised when CPP to PreprocessedDocument conversion fails.

    Error messages are prescriptive, indicating:
    - What failed
    - What was expected
    - Suggested remediation
    """

    pass


class CPPAdapter:
    """
    Adapter to convert CanonPolicyPackage (CPP output) to PreprocessedDocument.

    This is the canonical adapter for the FARFAN pipeline, converting the rich
    CanonPolicyPackage data into the format expected by the orchestrator.

    Thread Safety: Instances are thread-safe for concurrent to_preprocessed_document calls.

    Attributes:
        enable_runtime_validation: Whether WiringValidator is enabled
        wiring_validator:  Optional WiringValidator instance for contract checking
        config:  Centralized configuration dictionary with all parameter values
    """

    _PARAMETER_CONTEXT: Final[str] = "farfan_core.utils.cpp_adapter.CPPAdapter.__init__"

    def __init__(self, enable_runtime_validation: bool = True) -> None:
        """Initialize the CPP adapter.

        Args:
            enable_runtime_validation: Enable WiringValidator for runtime contract checking.
                When True, validates Adapter → Orchestrator contract after conversion.
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        self.enable_runtime_validation = enable_runtime_validation
        self.wiring_validator: Any = None

        if enable_runtime_validation:
            try:
                from farfan_pipeline.phases.Phase_0.phase0_90_03_wiring_validator import (
                    WiringValidator,
                )

                self.wiring_validator = WiringValidator()
                self.logger.info("WiringValidator enabled for runtime contract checking")
            except ImportError:
                self.logger.warning("WiringValidator not available. Runtime validation disabled.")

        self.config: dict[str, Any] = self._build_config()

    def _build_config(self) -> dict[str, Any]:
        """Build centralized configuration dictionary.

        Returns:
            Configuration dictionary with all parameter values loaded once.
        """
        ctx = self._PARAMETER_CONTEXT
        return {
            "confidence_layout_default": ParameterLoaderV2.get(ctx, "auto_param_L256_66", 0.0),
            "confidence_layout_missing": ParameterLoaderV2.get(ctx, "auto_param_L256_108", 0.0),
            "confidence_ocr_default": ParameterLoaderV2.get(ctx, "auto_param_L257_60", 0.0),
            "confidence_ocr_missing": ParameterLoaderV2.get(ctx, "auto_param_L257_102", 0.0),
            "confidence_typing_default": ParameterLoaderV2.get(ctx, "auto_param_L258_66", 0.0),
            "confidence_typing_missing": ParameterLoaderV2.get(ctx, "auto_param_L258_108", 0.0),
            "quality_metrics_defaults": {
                "provenance_completeness": ParameterLoaderV2.get(ctx, "auto_param_L328_117", 0.0),
                "structural_consistency": ParameterLoaderV2.get(ctx, "auto_param_L329_114", 0.0),
                "boundary_f1": ParameterLoaderV2.get(ctx, "auto_param_L330_81", 0.0),
                "kpi_linkage_rate": ParameterLoaderV2.get(ctx, "auto_param_L331_96", 0.0),
                "budget_consistency_score": ParameterLoaderV2.get(ctx, "auto_param_L332_120", 0.0),
                "temporal_robustness": ParameterLoaderV2.get(ctx, "auto_param_L333_105", 0.0),
                "chunk_context_coverage": ParameterLoaderV2.get(ctx, "auto_param_L334_114", 0.0),
            },
            "provenance_completeness_default": ParameterLoaderV2.get(
                ctx, "auto_param_L397_92", 0.0
            ),
        }

    def _resolve_chunk_attributes(self, chunk: Any) -> dict[str, Any]:
        """Extract all needed attributes from a chunk in a single pass.

        Args:
            chunk:  Chunk object to extract attributes from

        Returns:
            Dictionary with resolved attribute values, using None for missing attributes
        """
        resolution_raw = getattr(chunk, "resolution", None)
        resolution_value = (
            resolution_raw.value.lower()
            if resolution_raw is not None and hasattr(resolution_raw, "value")
            else None
        )

        return {
            "policy_area_id": getattr(chunk, "policy_area_id", None),
            "dimension_id": getattr(chunk, "dimension_id", None),
            "resolution": resolution_value,
            "confidence": getattr(chunk, "confidence", None),
            "provenance": getattr(chunk, "provenance", None),
            "entities": getattr(chunk, "entities", None),
            "time_facets": getattr(chunk, "time_facets", None),
            "geo_facets": getattr(chunk, "geo_facets", None),
            "policy_facets": getattr(chunk, "policy_facets", None),
            "kpi": getattr(chunk, "kpi", None),
            "budget": getattr(chunk, "budget", None),
        }

    def _validate_provenance(self, provenance: Any, chunk_id: str) -> None:
        """Validate provenance data completeness.

        Args:
            provenance:  Provenance object to validate
            chunk_id: Chunk identifier for error messages

        Raises:
            CPPAdapterError: If provenance is missing or incomplete
        """
        if provenance is None:
            raise CPPAdapterError(
                f"Missing provenance in chunk {chunk_id}. "
                f"All chunks must have provenance data for audit trail."
            )

        if not hasattr(provenance, "page_number") or provenance.page_number is None:
            raise CPPAdapterError(
                f"Missing provenance.page_number in chunk {chunk_id}. "
                f"Page number is required for source traceability."
            )

        if not hasattr(provenance, "section_header") or not provenance.section_header:
            raise CPPAdapterError(
                f"Missing provenance.section_header in chunk {chunk_id}. "
                f"Section header is required for document structure mapping."
            )

    def _build_confidence_dict(self, confidence: Any) -> dict[str, float]:
        """Build confidence dictionary from chunk confidence object.

        Args:
            confidence: Confidence object or None

        Returns:
            Dictionary with layout, ocr, and typing confidence values
        """
        if confidence is None:
            return {
                "layout": self.config["confidence_layout_missing"],
                "ocr": self.config["confidence_ocr_missing"],
                "typing": self.config["confidence_typing_missing"],
            }

        return {
            "layout": getattr(confidence, "layout", self.config["confidence_layout_default"]),
            "ocr": getattr(confidence, "ocr", self.config["confidence_ocr_default"]),
            "typing": getattr(confidence, "typing", self.config["confidence_typing_default"]),
        }

    def _process_chunk(self, chunk: Any, idx: int, current_offset: int) -> ChunkArtifacts:
        """Process a single chunk and return all its artifacts.

        Args:
            chunk: Chunk object to process
            idx: Index of the chunk in the sorted list
            current_offset: Current character offset in the full text

        Returns:
            ChunkArtifacts containing all outputs for this chunk

        Raises:
            CPPAdapterError: If chunk data is invalid or missing required fields
        """
        chunk_text = chunk.text
        chunk_start = current_offset
        chunk_end = chunk_start + len(chunk_text)

        attrs = self._resolve_chunk_attributes(chunk)

        sentence = {
            "text": chunk_text,
            "chunk_id": chunk.id,
            "resolution": attrs["resolution"],
        }

        extra_metadata: dict[str, Any] = {
            "chunk_id": chunk.id,
            "policy_area_id": attrs["policy_area_id"],
            "dimension_id": attrs["dimension_id"],
            "resolution": attrs["resolution"],
        }

        if attrs["policy_facets"] is not None:
            extra_metadata["policy_facets"] = {
                "axes": getattr(attrs["policy_facets"], "axes", []),
                "programs": getattr(attrs["policy_facets"], "programs", []),
                "projects": getattr(attrs["policy_facets"], "projects", []),
            }

        if attrs["time_facets"] is not None:
            extra_metadata["time_facets"] = {
                "years": getattr(attrs["time_facets"], "years", []),
                "periods": getattr(attrs["time_facets"], "periods", []),
            }

        if attrs["geo_facets"] is not None:
            extra_metadata["geo_facets"] = {
                "territories": getattr(attrs["geo_facets"], "territories", []),
                "regions": getattr(attrs["geo_facets"], "regions", []),
            }

        sentence_metadata = {
            "index": idx,
            "page_number": None,
            "start_char": chunk_start,
            "end_char": chunk_end,
            "extra": dict(extra_metadata),
        }

        confidence_dict = self._build_confidence_dict(attrs["confidence"])

        chunk_summary = {
            "id": chunk.id,
            "resolution": attrs["resolution"],
            "text_span": {"start": chunk_start, "end": chunk_end},
            "policy_area_id": attrs["policy_area_id"],
            "dimension_id": attrs["dimension_id"],
            "has_kpi": attrs["kpi"] is not None,
            "has_budget": attrs["budget"] is not None,
            "confidence": confidence_dict,
        }

        self._validate_provenance(attrs["provenance"], chunk.id)

        entity_mentions: dict[str, list[int]] = {}
        if attrs["entities"] is not None:
            for entity in attrs["entities"]:
                entity_text = getattr(entity, "text", str(entity))
                if entity_text not in entity_mentions:
                    entity_mentions[entity_text] = []
                entity_mentions[entity_text].append(idx)

        temporal_mentions: dict[str, list[int]] = {}
        if attrs["time_facets"] is not None:
            years = getattr(attrs["time_facets"], "years", None)
            if years:
                for year in years:
                    year_key = str(year)
                    if year_key not in temporal_mentions:
                        temporal_mentions[year_key] = []
                    temporal_mentions[year_key].append(idx)

        table: dict[str, Any] | None = None
        if attrs["budget"] is not None:
            budget = attrs["budget"]
            table = {
                "table_id": f"budget_{idx}",
                "label": f"Budget:  {getattr(budget, 'source', 'Unknown')}",
                "amount": getattr(budget, "amount", 0),
                "currency": getattr(budget, "currency", "COP"),
                "year": getattr(budget, "year", None),
                "use": getattr(budget, "use", None),
                "source": getattr(budget, "source", None),
            }

        chunk_type_value = chunk.chunk_type
        if chunk_type_value not in _VALID_CHUNK_TYPES:
            raise CPPAdapterError(
                f"Invalid chunk_type '{chunk_type_value}' in chunk {chunk.id}. "
                f"Valid types:  {', '.join(sorted(_VALID_CHUNK_TYPES))}"
            )

        provenance_obj = attrs["provenance"]
        chunk_data = ChunkData(
            id=idx,
            text=chunk_text,
            chunk_type=chunk_type_value,
            sentences=[idx],
            tables=[],
            start_pos=chunk_start,
            end_pos=chunk_end,
            confidence=(
                getattr(attrs["confidence"], "overall", 1.0)
                if attrs["confidence"] is not None
                else 1.0
            ),
            edges_out=[],
            policy_area_id=attrs["policy_area_id"],
            dimension_id=attrs["dimension_id"],
            provenance=Provenance(
                page_number=provenance_obj.page_number,
                section_header=getattr(provenance_obj, "section_header", None),
                bbox=getattr(provenance_obj, "bbox", None),
                span_in_page=getattr(provenance_obj, "span_in_page", None),
                source_file=getattr(provenance_obj, "source_file", None),
            ),
        )

        return ChunkArtifacts(
            sentence=sentence,
            sentence_metadata=sentence_metadata,
            chunk_summary=chunk_summary,
            chunk_data=chunk_data,
            table=table,
            entity_mentions=entity_mentions,
            temporal_mentions=temporal_mentions,
            chunk_text_length=len(chunk_text),
            has_provenance=True,
        )

    def _validate_canon_package(self, canon_package: Any, document_id: str) -> None:
        """Execute 6-layer validation for robust phase-one output processing.

        Args:
            canon_package: CanonPolicyPackage to validate
            document_id: Document identifier for error messages

        Raises:
            CPPAdapterError: If any validation layer fails
        """
        if not canon_package:
            raise CPPAdapterError(
                "canon_package is None or empty. " "Ensure ingestion completed successfully."
            )

        if not document_id or not isinstance(document_id, str) or not document_id.strip():
            raise CPPAdapterError(
                f"document_id must be a non-empty string. " f"Received:  {document_id!r}"
            )

        if not hasattr(canon_package, "chunk_graph") or not canon_package.chunk_graph:
            raise CPPAdapterError(
                "canon_package must have a valid chunk_graph.  "
                "Check that SmartChunkConverter produced valid output."
            )

        chunk_graph = canon_package.chunk_graph

        if not chunk_graph.chunks:
            raise CPPAdapterError(
                "chunk_graph. chunks is empty - no chunks to process.  "
                "Minimum 1 chunk required from phase-one."
            )

        validation_failures: list[str] = []
        for chunk_id, chunk in chunk_graph.chunks.items():
            if not hasattr(chunk, "text"):
                validation_failures.append(f"Chunk {chunk_id}:  missing 'text' attribute")
            elif not chunk.text or not chunk.text.strip():
                validation_failures.append(f"Chunk {chunk_id}:  text is empty or whitespace")

            if not hasattr(chunk, "text_span"):
                validation_failures.append(f"Chunk {chunk_id}: missing 'text_span' attribute")
            elif not hasattr(chunk.text_span, "start") or not hasattr(chunk.text_span, "end"):
                validation_failures.append(
                    f"Chunk {chunk_id}:  invalid text_span (missing start/end)"
                )

        if validation_failures:
            failure_summary = "\n  - ".join(validation_failures)
            raise CPPAdapterError(
                f"Chunk validation failed ({len(validation_failures)} errors):\n"
                f"  - {failure_summary}\n"
                f"Total chunks: {len(chunk_graph.chunks)}\n"
                f"This indicates SmartChunkConverter produced invalid output."
            )

    def _validate_chunk_cardinality_and_metadata(self, sorted_chunks: list[Any]) -> None:
        """Enforce cardinality and metadata integrity constraints.

        Args:
            sorted_chunks: List of chunks sorted by text_span. start

        Raises:
            CPPAdapterError: If cardinality or metadata constraints are violated
        """
        if len(sorted_chunks) != 60:
            raise CPPAdapterError(
                f"Cardinality mismatch: Expected 60 chunks for 'chunked' processing mode, "
                f"but found {len(sorted_chunks)}. This is a critical violation of the "
                f"CPP canonical format."
            )

        for chunk in sorted_chunks:
            if not hasattr(chunk, "policy_area_id") or not chunk.policy_area_id:
                raise CPPAdapterError(
                    f"Missing policy_area_id in chunk {chunk. id}. "
                    f"PA×DIM metadata is required for Phase 2 question routing."
                )
            if not hasattr(chunk, "dimension_id") or not chunk.dimension_id:
                raise CPPAdapterError(
                    f"Missing dimension_id in chunk {chunk.id}.  "
                    f"PA×DIM metadata is required for Phase 2 question routing."
                )
            if not hasattr(chunk, "chunk_type") or not chunk.chunk_type:
                raise CPPAdapterError(
                    f"Missing chunk_type in chunk {chunk.id}. "
                    f"Chunk type is required for semantic classification."
                )

    def _build_quality_metrics(self, canon_package: Any) -> dict[str, float]:
        """Extract quality metrics from canon_package or use defaults.

        Args:
            canon_package: CanonPolicyPackage with optional quality_metrics

        Returns:
            Dictionary of quality metric values
        """
        defaults = self.config["quality_metrics_defaults"]

        if not hasattr(canon_package, "quality_metrics") or not canon_package.quality_metrics:
            return dict(defaults)

        qm = canon_package.quality_metrics
        return {
            "provenance_completeness": getattr(
                qm, "provenance_completeness", defaults["provenance_completeness"]
            ),
            "structural_consistency": getattr(
                qm, "structural_consistency", defaults["structural_consistency"]
            ),
            "boundary_f1": getattr(qm, "boundary_f1", defaults["boundary_f1"]),
            "kpi_linkage_rate": getattr(qm, "kpi_linkage_rate", defaults["kpi_linkage_rate"]),
            "budget_consistency_score": getattr(
                qm, "budget_consistency_score", defaults["budget_consistency_score"]
            ),
            "temporal_robustness": getattr(
                qm, "temporal_robustness", defaults["temporal_robustness"]
            ),
            "chunk_context_coverage": getattr(
                qm, "chunk_context_coverage", defaults["chunk_context_coverage"]
            ),
        }

    def _build_policy_manifest(self, canon_package: Any) -> dict[str, list[Any]] | None:
        """Extract policy manifest from canon_package if available.

        Args:
            canon_package: CanonPolicyPackage with optional policy_manifest

        Returns:
            Policy manifest dictionary or None
        """
        if not hasattr(canon_package, "policy_manifest") or not canon_package.policy_manifest:
            return None

        pm = canon_package.policy_manifest
        return {
            "axes": getattr(pm, "axes", []),
            "programs": getattr(pm, "programs", []),
            "projects": getattr(pm, "projects", []),
            "years": getattr(pm, "years", []),
            "territories": getattr(pm, "territories", []),
        }

    def _validate_runtime_contract(
        self, preprocessed_doc: PreprocessedDocument, metadata_dict: dict[str, Any]
    ) -> None:
        """Validate Adapter → Orchestrator contract at runtime.

        Args:
            preprocessed_doc:  The converted PreprocessedDocument
            metadata_dict:  Metadata dictionary for provenance_completeness

        Raises:
            ValueError: If contract validation fails
        """
        if self.wiring_validator is None:
            return

        self.logger.info("Validating Adapter → Orchestrator contract (runtime)")
        try:
            preprocessed_dict = {
                "document_id": preprocessed_doc.document_id,
                "sentence_metadata": preprocessed_doc.sentence_metadata,
                "resolution_index": {},
                "provenance_completeness": metadata_dict.get(
                    "provenance_completeness",
                    self.config["provenance_completeness_default"],
                ),
            }
            self.wiring_validator.validate_adapter_to_orchestrator(preprocessed_dict)
            self.logger.info("✓ Adapter → Orchestrator contract validation passed")
        except Exception as e:
            self.logger.error(f"Adapter → Orchestrator contract validation failed: {e}")
            raise ValueError(
                f"Runtime contract violation at Adapter → Orchestrator boundary: {e}"
            ) from e

    def to_preprocessed_document(
        self, canon_package: Any, document_id: str
    ) -> PreprocessedDocument:
        """
        Convert CanonPolicyPackage to PreprocessedDocument.

        Args:
            canon_package: CanonPolicyPackage from ingestion
            document_id:  Unique document identifier

        Returns:
            PreprocessedDocument ready for orchestrator

        Raises:
            CPPAdapterError: If conversion fails or data is invalid
            ValueError: If runtime contract validation fails

        CanonPolicyPackage Expected Attributes:
            Required:
                - chunk_graph: ChunkGraph with . chunks dict
                - chunk_graph.chunks: dict of chunk objects with . text and .text_span

            Optional (handled with hasattr checks):
                - schema_version: str (default: 'CPP-2025. 1')
                - quality_metrics: object with metrics like provenance_completeness,
                  structural_consistency, boundary_f1, kpi_linkage_rate,
                  budget_consistency_score, temporal_robustness, chunk_context_coverage
                - policy_manifest:  object with axes, programs, projects, years, territories
                - metadata: dict with optional 'spc_rich_data' key

            Chunk Required Attributes:
                - id: str
                - text: str (non-empty)
                - text_span:  object with start and end attributes
                - policy_area_id: str
                - dimension_id: str
                - chunk_type:  str (one of: diagnostic, activity, indicator, resource, temporal, entity)
                - provenance: object with page_number and section_header

            Chunk Optional Attributes:
                - entities: list of entity objects with . text attribute
                - time_facets: object with . years list
                - budget: object with amount, currency, year, use, source attributes
                - confidence:  object with layout, ocr, typing, overall attributes
                - policy_facets: object with axes, programs, projects
                - geo_facets: object with territories, regions
        """
        self.logger.info(f"Converting CanonPolicyPackage to PreprocessedDocument:  {document_id}")

        self._validate_canon_package(canon_package, document_id)

        chunk_graph = canon_package.chunk_graph
        sorted_chunks = sorted(
            chunk_graph.chunks.values(),
            key=lambda c: (c.text_span.start if hasattr(c, "text_span") and c.text_span else 0),
        )

        self._validate_chunk_cardinality_and_metadata(sorted_chunks)

        self.logger.info(f"Processing {len(sorted_chunks)} chunks")

        chunk_index: dict[str, int] = {}
        term_index: dict[str, list[int]] = {}
        numeric_index: dict[str, list[int]] = {}
        temporal_index: dict[str, list[int]] = {}
        entity_index: dict[str, list[int]] = {}

        current_offset = 0
        provenance_with_data = 0

        artifacts_list: list[ChunkArtifacts] = []
        for idx, chunk in enumerate(sorted_chunks):
            chunk_index[chunk.id] = idx
            artifacts = self._process_chunk(chunk, idx, current_offset)
            artifacts_list.append(artifacts)

            if artifacts.has_provenance:
                provenance_with_data += 1

            for entity_text, indices in artifacts.entity_mentions.items():
                if entity_text not in entity_index:
                    entity_index[entity_text] = []
                entity_index[entity_text].extend(indices)

            for year_key, indices in artifacts.temporal_mentions.items():
                if year_key not in temporal_index:
                    temporal_index[year_key] = []
                temporal_index[year_key].extend(indices)

            current_offset += artifacts.chunk_text_length + 1

        full_text_parts = [art.sentence["text"] for art in artifacts_list]
        sentences = [art.sentence for art in artifacts_list]
        sentence_metadata = [art.sentence_metadata for art in artifacts_list]
        chunk_summaries = [art.chunk_summary for art in artifacts_list]

        chunks_data: list[ChunkData] = []
        tables: list[dict[str, Any]] = []
        table_counter = 0

        for art in artifacts_list:
            if art.table is not None:
                updated_chunk_data = ChunkData(
                    id=art.chunk_data.id,
                    text=art.chunk_data.text,
                    chunk_type=art.chunk_data.chunk_type,
                    sentences=art.chunk_data.sentences,
                    tables=[table_counter],
                    start_pos=art.chunk_data.start_pos,
                    end_pos=art.chunk_data.end_pos,
                    confidence=art.chunk_data.confidence,
                    edges_out=art.chunk_data.edges_out,
                    policy_area_id=art.chunk_data.policy_area_id,
                    dimension_id=art.chunk_data.dimension_id,
                    provenance=art.chunk_data.provenance,
                )
                chunks_data.append(updated_chunk_data)
                tables.append(art.table)
                table_counter += 1
            else:
                chunks_data.append(art.chunk_data)

        full_text = " ".join(full_text_parts)

        if not full_text:
            raise CPPAdapterError(
                "Generated full_text is empty. "
                "This indicates all chunks had empty text after processing."
            )

        indexes = {
            "term_index": {k: tuple(v) for k, v in term_index.items()},
            "numeric_index": {k: tuple(v) for k, v in numeric_index.items()},
            "temporal_index": {k: tuple(v) for k, v in temporal_index.items()},
            "entity_index": {k: tuple(v) for k, v in entity_index.items()},
        }

        metadata_dict: dict[str, Any] = {
            "adapter_source": "CPPAdapter",
            "schema_version": getattr(canon_package, "schema_version", "CPP-2025.1"),
            "chunk_count": len(sorted_chunks),
            "processing_mode": "chunked",
            "chunks": chunk_summaries,
        }

        quality_metrics = self._build_quality_metrics(canon_package)
        if quality_metrics:
            metadata_dict["quality_metrics"] = quality_metrics

        policy_manifest = self._build_policy_manifest(canon_package)
        if policy_manifest is not None:
            metadata_dict["policy_manifest"] = policy_manifest

        if hasattr(canon_package, "metadata") and canon_package.metadata:
            if "spc_rich_data" in canon_package.metadata:
                metadata_dict["spc_rich_data"] = canon_package.metadata["spc_rich_data"]

        if len(sorted_chunks) > 0:
            metadata_dict["provenance_completeness"] = provenance_with_data / len(sorted_chunks)

        metadata = MappingProxyType(metadata_dict)

        language = "es"

        preprocessed_doc = PreprocessedDocument(
            document_id=document_id,
            raw_text=full_text,
            sentences=sentences,
            tables=tables,
            metadata=dict(metadata),
            sentence_metadata=sentence_metadata,
            indexes=indexes,
            structured_text={
                "full_text": full_text,
                "sections": (),
                "page_boundaries": (),
            },
            language=language,
            ingested_at=datetime.now(UTC),
            full_text=full_text,
            chunks=chunks_data,
            chunk_index=chunk_index,
            chunk_graph={
                "chunks": {cid: chunk_index[cid] for cid in chunk_index},
                "edges": list(getattr(chunk_graph, "edges", [])),
            },
            processing_mode="chunked",
        )

        self.logger.info(
            f"Conversion complete: {len(sentences)} sentences, "
            f"{len(tables)} tables, {len(entity_index)} entities indexed"
        )

        self._validate_runtime_contract(preprocessed_doc, metadata_dict)

        return preprocessed_doc


def adapt_cpp_to_orchestrator(canon_package: Any, document_id: str) -> PreprocessedDocument:
    """
    Convenience function to adapt CPP to PreprocessedDocument.

    Args:
        canon_package: CanonPolicyPackage from ingestion
        document_id: Unique document identifier

    Returns:
        PreprocessedDocument for orchestrator

    Raises:
        CPPAdapterError:  If conversion fails
        ValueError: If runtime contract validation fails
    """
    adapter = CPPAdapter()
    return adapter.to_preprocessed_document(canon_package, document_id)


__all__ = [
    "CPPAdapter",
    "CPPAdapterError",
    "ChunkArtifacts",
    "adapt_cpp_to_orchestrator",
]

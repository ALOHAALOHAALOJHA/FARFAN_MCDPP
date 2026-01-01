"""CPP to Orchestrator Adapter.

This adapter converts Canon Policy Package (CPP) documents from the ingestion pipeline 
into the orchestrator's PreprocessedDocument format.

Note: This is the canonical adapter implementation.

Design Principles:
- Preserves complete provenance information
- Orders chunks by text_span.start for deterministic ordering
- Computes provenance_completeness metric
- Provides prescriptive error messages on failure
- Supports micro, meso, and macro chunk resolutions
- Optional dependencies handled gracefully (pyarrow, structlog)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any

from farfan_pipeline.core.parameters import ParameterLoaderV2
from farfan_pipeline.core.types import ChunkData, PreprocessedDocument, Provenance

logger = logging.getLogger(__name__)

_EMPTY_MAPPING = MappingProxyType({})


@dataclass
class ChunkArtifacts:
    """Container for all outputs produced by processing a single chunk."""

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
    """Raised when CPP to PreprocessedDocument conversion fails."""

    pass


class CPPAdapter:
    """
    Adapter to convert CanonPolicyPackage (CPP output) to PreprocessedDocument.

    This is the canonical adapter for the FARFAN pipeline, converting the rich
    CanonPolicyPackage data into the format expected by the orchestrator.
    """

    def __init__(self, enable_runtime_validation: bool = True) -> None:
        """Initialize the CPP adapter.

        Args:
            enable_runtime_validation: Enable WiringValidator for runtime contract checking
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        self.enable_runtime_validation = enable_runtime_validation
        if enable_runtime_validation:
            try:
                from orchestration.wiring.validation import WiringValidator

                self.wiring_validator = WiringValidator()
                self.logger.info(
                    "WiringValidator enabled for runtime contract checking"
                )
            except ImportError:
                self.logger.warning(
                    "WiringValidator not available. Runtime validation disabled."
                )
                self.wiring_validator = None
        else:
            self.wiring_validator = None

        self.config = {
            "confidence_layout_default": ParameterLoaderV2.get(
                "farfan_core.utils.cpp_adapter.CPPAdapter.__init__",
                "auto_param_L256_66",
                0.0,
            ),
            "confidence_layout_missing": ParameterLoaderV2.get(
                "farfan_core.utils.cpp_adapter.CPPAdapter.__init__",
                "auto_param_L256_108",
                0.0,
            ),
            "confidence_ocr_default": ParameterLoaderV2.get(
                "farfan_core.utils.cpp_adapter.CPPAdapter.__init__",
                "auto_param_L257_60",
                0.0,
            ),
            "confidence_ocr_missing": ParameterLoaderV2.get(
                "farfan_core.utils.cpp_adapter.CPPAdapter.__init__",
                "auto_param_L257_102",
                0.0,
            ),
            "confidence_typing_default": ParameterLoaderV2.get(
                "farfan_core.utils.cpp_adapter.CPPAdapter.__init__",
                "auto_param_L258_66",
                0.0,
            ),
            "confidence_typing_missing": ParameterLoaderV2.get(
                "farfan_core.utils.cpp_adapter.CPPAdapter.__init__",
                "auto_param_L258_108",
                0.0,
            ),
            "quality_metrics_defaults": {
                "provenance_completeness": ParameterLoaderV2.get(
                    "farfan_core.utils.cpp_adapter.CPPAdapter.__init__",
                    "auto_param_L328_117",
                    0.0,
                ),
                "structural_consistency": ParameterLoaderV2.get(
                    "farfan_core.utils.cpp_adapter.CPPAdapter.__init__",
                    "auto_param_L329_114",
                    0.0,
                ),
                "boundary_f1": ParameterLoaderV2.get(
                    "farfan_core.utils.cpp_adapter.CPPAdapter.__init__",
                    "auto_param_L330_81",
                    0.0,
                ),
                "kpi_linkage_rate": ParameterLoaderV2.get(
                    "farfan_core.utils.cpp_adapter.CPPAdapter.__init__",
                    "auto_param_L331_96",
                    0.0,
                ),
                "budget_consistency_score": ParameterLoaderV2.get(
                    "farfan_core.utils.cpp_adapter.CPPAdapter.__init__",
                    "auto_param_L332_120",
                    0.0,
                ),
                "temporal_robustness": ParameterLoaderV2.get(
                    "farfan_core.utils.cpp_adapter.CPPAdapter.__init__",
                    "auto_param_L333_105",
                    0.0,
                ),
                "chunk_context_coverage": ParameterLoaderV2.get(
                    "farfan_core.utils.cpp_adapter.CPPAdapter.__init__",
                    "auto_param_L334_114",
                    0.0,
                ),
            },
            "provenance_completeness_default": ParameterLoaderV2.get(
                "farfan_core.utils.cpp_adapter.CPPAdapter.__init__",
                "auto_param_L397_92",
                0.0,
            ),
        }

    def _resolve_chunk_attributes(self, chunk: Any) -> dict[str, Any]:
        """Extract all needed attributes from a chunk in a single pass.

        Args:
            chunk: Chunk object to extract attributes from

        Returns:
            Dictionary with resolved attribute values
        """
        return {
            "policy_area_id": getattr(chunk, "policy_area_id", None),
            "dimension_id": getattr(chunk, "dimension_id", None),
            "resolution": (
                chunk.resolution.value.lower()
                if hasattr(chunk, "resolution") and chunk.resolution
                else None
            ),
            "confidence": getattr(chunk, "confidence", None),
            "provenance": getattr(chunk, "provenance", None),
            "entities": getattr(chunk, "entities", None),
            "time_facets": getattr(chunk, "time_facets", None),
            "geo_facets": getattr(chunk, "geo_facets", None),
            "policy_facets": getattr(chunk, "policy_facets", None),
            "kpi": getattr(chunk, "kpi", None),
            "budget": getattr(chunk, "budget", None),
        }

    def _process_chunk(
        self, chunk: Any, idx: int, current_offset: int
    ) -> ChunkArtifacts:
        """Process a single chunk and return all its artifacts.

        Args:
            chunk: Chunk object to process
            idx: Index of the chunk in the sorted list
            current_offset: Current character offset in the full text

        Returns:
            ChunkArtifacts containing all outputs for this chunk

        Raises:
            CPPAdapterError: If chunk data is invalid
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

        extra_metadata = {
            "chunk_id": chunk.id,
            "policy_area_id": attrs["policy_area_id"],
            "dimension_id": attrs["dimension_id"],
            "resolution": attrs["resolution"],
        }

        if attrs["policy_facets"]:
            extra_metadata["policy_facets"] = {
                "axes": getattr(attrs["policy_facets"], "axes", []),
                "programs": getattr(attrs["policy_facets"], "programs", []),
                "projects": getattr(attrs["policy_facets"], "projects", []),
            }

        if attrs["time_facets"]:
            extra_metadata["time_facets"] = {
                "years": getattr(attrs["time_facets"], "years", []),
                "periods": getattr(attrs["time_facets"], "periods", []),
            }

        if attrs["geo_facets"]:
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

        confidence_dict = {
            "layout": (
                getattr(attrs["confidence"], "layout", self.config["confidence_layout_default"])
                if attrs["confidence"]
                else self.config["confidence_layout_missing"]
            ),
            "ocr": (
                getattr(attrs["confidence"], "ocr", self.config["confidence_ocr_default"])
                if attrs["confidence"]
                else self.config["confidence_ocr_missing"]
            ),
            "typing": (
                getattr(attrs["confidence"], "typing", self.config["confidence_typing_default"])
                if attrs["confidence"]
                else self.config["confidence_typing_missing"]
            ),
        }

        chunk_summary = {
            "id": chunk.id,
            "resolution": attrs["resolution"],
            "text_span": {"start": chunk_start, "end": chunk_end},
            "policy_area_id": extra_metadata["policy_area_id"],
            "dimension_id": extra_metadata["dimension_id"],
            "has_kpi": attrs["kpi"] is not None,
            "has_budget": attrs["budget"] is not None,
            "confidence": confidence_dict,
        }

        if attrs["provenance"]:
            if not hasattr(attrs["provenance"], "page_number") or attrs["provenance"].page_number is None:
                raise CPPAdapterError(
                    f"Missing provenance.page_number in chunk {chunk.id}"
                )
            if not hasattr(attrs["provenance"], "section_header") or not attrs["provenance"].section_header:
                raise CPPAdapterError(
                    f"Missing provenance.section_header in chunk {chunk.id}"
                )
        else:
            raise CPPAdapterError(f"Missing provenance in chunk {chunk.id}")

        entity_mentions: dict[str, list[int]] = {}
        if attrs["entities"]:
            for entity in attrs["entities"]:
                entity_text = getattr(entity, "text", str(entity))
                if entity_text not in entity_mentions:
                    entity_mentions[entity_text] = []
                entity_mentions[entity_text].append(idx)

        temporal_mentions: dict[str, list[int]] = {}
        if attrs["time_facets"] and hasattr(attrs["time_facets"], "years") and attrs["time_facets"].years:
            for year in attrs["time_facets"].years:
                year_key = str(year)
                if year_key not in temporal_mentions:
                    temporal_mentions[year_key] = []
                temporal_mentions[year_key].append(idx)

        table = None
        if attrs["budget"]:
            budget = attrs["budget"]
            table = {
                "table_id": f"budget_{idx}",
                "label": f"Budget: {getattr(budget, 'source', 'Unknown')}",
                "amount": getattr(budget, "amount", 0),
                "currency": getattr(budget, "currency", "COP"),
                "year": getattr(budget, "year", None),
                "use": getattr(budget, "use", None),
                "source": getattr(budget, "source", None),
            }

        chunk_type_value = chunk.chunk_type
        if chunk_type_value not in [
            "diagnostic",
            "activity",
            "indicator",
            "resource",
            "temporal",
            "entity",
        ]:
            raise CPPAdapterError(
                f"Invalid chunk_type '{chunk_type_value}' in chunk {chunk.id}"
            )

        chunk_data = ChunkData(
            id=idx,
            text=chunk_text,
            chunk_type=chunk_type_value,
            sentences=[idx],
            tables=[idx] if table else [],
            start_pos=chunk_start,
            end_pos=chunk_end,
            confidence=(
                getattr(attrs["confidence"], "overall", 1.0)
                if attrs["confidence"]
                else 1.0
            ),
            edges_out=[],
            policy_area_id=extra_metadata["policy_area_id"],
            dimension_id=extra_metadata["dimension_id"],
            provenance=(
                Provenance(
                    page_number=attrs["provenance"].page_number,
                    section_header=getattr(attrs["provenance"], "section_header", None),
                    bbox=getattr(attrs["provenance"], "bbox", None),
                    span_in_page=getattr(attrs["provenance"], "span_in_page", None),
                    source_file=getattr(attrs["provenance"], "source_file", None),
                )
                if attrs["provenance"]
                else None
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
            has_provenance=attrs["provenance"] is not None,
        )

    def to_preprocessed_document(
        self, canon_package: Any, document_id: str
    ) -> PreprocessedDocument:
        """
        Convert CanonPolicyPackage to PreprocessedDocument.

        Args:
            canon_package: CanonPolicyPackage from ingestion
            document_id: Unique document identifier

        Returns:
            PreprocessedDocument ready for orchestrator

        Raises:
            CPPAdapterError: If conversion fails or data is invalid

        CanonPolicyPackage Expected Attributes:
            Required:
                - chunk_graph: ChunkGraph with .chunks dict
                - chunk_graph.chunks: dict of chunk objects with .text and .text_span

            Optional (handled with hasattr checks):
                - schema_version: str (default: 'CPP-2025.1')
                - quality_metrics: object with metrics like provenance_completeness,
                  structural_consistency, boundary_f1, kpi_linkage_rate,
                  budget_consistency_score, temporal_robustness, chunk_context_coverage
                - policy_manifest: object with axes, programs, projects, years, territories
                - metadata: dict with optional 'spc_rich_data' key

            Chunk Optional Attributes (handled with hasattr checks):
                - entities: list of entity objects with .text attribute
                - time_facets: object with .years list
                - budget: object with amount, currency, year, use, source attributes
        """
        self.logger.info(
            f"Converting CanonPolicyPackage to PreprocessedDocument: {document_id}"
        )

        # === COMPREHENSIVE VALIDATION PHASE (H1.5) ===
        # 6-layer validation for robust phase-one output processing

        # V1: Validate canon_package exists
        if not canon_package:
            raise CPPAdapterError(
                "canon_package is None or empty. "
                "Ensure ingestion completed successfully."
            )

        # V2: Validate document_id
        if (
            not document_id
            or not isinstance(document_id, str)
            or not document_id.strip()
        ):
            raise CPPAdapterError(
                f"document_id must be a non-empty string. "
                f"Received: {repr(document_id)}"
            )

        # V3: Validate chunk_graph exists
        if not hasattr(canon_package, "chunk_graph") or not canon_package.chunk_graph:
            raise CPPAdapterError(
                "canon_package must have a valid chunk_graph. "
                "Check that SmartChunkConverter produced valid output."
            )

        chunk_graph = canon_package.chunk_graph

        # V4: Validate chunks dict is non-empty
        if not chunk_graph.chunks:
            raise CPPAdapterError(
                "chunk_graph.chunks is empty - no chunks to process. "
                "Minimum 1 chunk required from phase-one."
            )

        # V5: Validate individual chunks have required attributes
        validation_failures = []
        for chunk_id, chunk in chunk_graph.chunks.items():
            if not hasattr(chunk, "text"):
                validation_failures.append(
                    f"Chunk {chunk_id}: missing 'text' attribute"
                )
            elif not chunk.text or not chunk.text.strip():
                validation_failures.append(
                    f"Chunk {chunk_id}: text is empty or whitespace"
                )

            if not hasattr(chunk, "text_span"):
                validation_failures.append(
                    f"Chunk {chunk_id}: missing 'text_span' attribute"
                )
            elif not hasattr(chunk.text_span, "start") or not hasattr(
                chunk.text_span, "end"
            ):
                validation_failures.append(
                    f"Chunk {chunk_id}: invalid text_span (missing start/end)"
                )

        # V6: Report validation failures with context
        if validation_failures:
            failure_summary = "\n  - ".join(validation_failures)
            raise CPPAdapterError(
                f"Chunk validation failed ({len(validation_failures)} errors):\n  - {failure_summary}\n"
                f"Total chunks: {len(chunk_graph.chunks)}\n"
                f"This indicates SmartChunkConverter produced invalid output."
            )

        # Sort chunks by document position for deterministic ordering
        sorted_chunks = sorted(
            chunk_graph.chunks.values(),
            key=lambda c: (
                c.text_span.start if hasattr(c, "text_span") and c.text_span else 0
            ),
        )

        # === PHASE 2 HARDENING: STRICT CARDINALITY & METADATA ===
        # Enforce exactly 60 chunks for CPP canonical documents as per Jobfront 1
        processing_mode = "chunked"
        degradation_reason = None

        if len(sorted_chunks) != 60:
            raise CPPAdapterError(
                f"Cardinality mismatch: Expected 60 chunks for 'chunked' processing mode, "
                f"but found {len(sorted_chunks)}. This is a critical violation of the "
                f"CPP canonical format."
            )

        # Enforce metadata integrity
        for idx, chunk in enumerate(sorted_chunks):
            if not hasattr(chunk, "policy_area_id") or not chunk.policy_area_id:
                raise CPPAdapterError(f"Missing policy_area_id in chunk {chunk.id}")
            if not hasattr(chunk, "dimension_id") or not chunk.dimension_id:
                raise CPPAdapterError(f"Missing dimension_id in chunk {chunk.id}")
            if not hasattr(chunk, "chunk_type") or not chunk.chunk_type:
                raise CPPAdapterError(f"Missing chunk_type in chunk {chunk.id}")

        self.logger.info(f"Processing {len(sorted_chunks)} chunks")

        chunk_index: dict[str, int] = {}
        term_index: dict[str, list[int]] = {}
        numeric_index: dict[str, list[int]] = {}
        temporal_index: dict[str, list[int]] = {}
        entity_index: dict[str, list[int]] = {}

        current_offset = 0
        provenance_with_data = 0
        table_counter = 0

        artifacts_list = []
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
        chunks_data = [art.chunk_data for art in artifacts_list]
        tables = [art.table for art in artifacts_list if art.table is not None]

        for idx, art in enumerate(artifacts_list):
            if art.table is not None:
                chunks_data[idx] = ChunkData(
                    id=chunks_data[idx].id,
                    text=chunks_data[idx].text,
                    chunk_type=chunks_data[idx].chunk_type,
                    sentences=chunks_data[idx].sentences,
                    tables=[table_counter],
                    start_pos=chunks_data[idx].start_pos,
                    end_pos=chunks_data[idx].end_pos,
                    confidence=chunks_data[idx].confidence,
                    edges_out=chunks_data[idx].edges_out,
                    policy_area_id=chunks_data[idx].policy_area_id,
                    dimension_id=chunks_data[idx].dimension_id,
                    provenance=chunks_data[idx].provenance,
                )
                table_counter += 1

        # Join full text
        full_text = " ".join(full_text_parts)

        if not full_text:
            raise CPPAdapterError("Generated full_text is empty")

        # Build document indexes
        indexes = {
            "term_index": {k: tuple(v) for k, v in term_index.items()},
            "numeric_index": {k: tuple(v) for k, v in numeric_index.items()},
            "temporal_index": {k: tuple(v) for k, v in temporal_index.items()},
            "entity_index": {k: tuple(v) for k, v in entity_index.items()},
        }

        # Build metadata from canon_package
        metadata_dict = {
            "adapter_source": "CPPAdapter",
            "schema_version": (
                canon_package.schema_version
                if hasattr(canon_package, "schema_version")
                else "CPP-2025.1"
            ),
            "chunk_count": len(sorted_chunks),
            "processing_mode": "chunked",
            "chunks": chunk_summaries,
        }

        # Add quality metrics if available
        if hasattr(canon_package, "quality_metrics") and canon_package.quality_metrics:
            qm = canon_package.quality_metrics
            qm_defaults = self.config["quality_metrics_defaults"]
            metadata_dict["quality_metrics"] = {
                "provenance_completeness": (
                    qm.provenance_completeness
                    if hasattr(qm, "provenance_completeness")
                    else qm_defaults["provenance_completeness"]
                ),
                "structural_consistency": (
                    qm.structural_consistency
                    if hasattr(qm, "structural_consistency")
                    else qm_defaults["structural_consistency"]
                ),
                "boundary_f1": (
                    qm.boundary_f1
                    if hasattr(qm, "boundary_f1")
                    else qm_defaults["boundary_f1"]
                ),
                "kpi_linkage_rate": (
                    qm.kpi_linkage_rate
                    if hasattr(qm, "kpi_linkage_rate")
                    else qm_defaults["kpi_linkage_rate"]
                ),
                "budget_consistency_score": (
                    qm.budget_consistency_score
                    if hasattr(qm, "budget_consistency_score")
                    else qm_defaults["budget_consistency_score"]
                ),
                "temporal_robustness": (
                    qm.temporal_robustness
                    if hasattr(qm, "temporal_robustness")
                    else qm_defaults["temporal_robustness"]
                ),
                "chunk_context_coverage": (
                    qm.chunk_context_coverage
                    if hasattr(qm, "chunk_context_coverage")
                    else qm_defaults["chunk_context_coverage"]
                ),
            }

        # Add policy manifest if available
        if hasattr(canon_package, "policy_manifest") and canon_package.policy_manifest:
            pm = canon_package.policy_manifest
            metadata_dict["policy_manifest"] = {
                "axes": pm.axes if hasattr(pm, "axes") else [],
                "programs": pm.programs if hasattr(pm, "programs") else [],
                "projects": pm.projects if hasattr(pm, "projects") else [],
                "years": pm.years if hasattr(pm, "years") else [],
                "territories": pm.territories if hasattr(pm, "territories") else [],
            }

        # Add CPP rich data if available in metadata
        if hasattr(canon_package, "metadata") and canon_package.metadata:
            if "spc_rich_data" in canon_package.metadata:
                metadata_dict["spc_rich_data"] = canon_package.metadata["spc_rich_data"]

        if len(sorted_chunks) > 0:
            metadata_dict["provenance_completeness"] = provenance_with_data / len(
                sorted_chunks
            )

        metadata = MappingProxyType(metadata_dict)

        # Detect language (default to Spanish for Colombian policy documents)
        language = "es"

        # Create PreprocessedDocument (canonical orchestrator dataclass)
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
            ingested_at=datetime.now(timezone.utc),
            full_text=full_text,
            chunks=chunks_data,
            chunk_index=chunk_index,
            chunk_graph={
                "chunks": {cid: chunk_index[cid] for cid in chunk_index},
                "edges": list(getattr(chunk_graph, "edges", [])),
            },
            processing_mode=processing_mode,
        )

        self.logger.info(
            f"Conversion complete: {len(sentences)} sentences, "
            f"{len(tables)} tables, {len(entity_index)} entities indexed"
        )

        # RUNTIME VALIDATION: Validate Adapter → Orchestrator contract
        if self.wiring_validator is not None:
            self.logger.info("Validating Adapter → Orchestrator contract (runtime)")
            try:
                # Convert PreprocessedDocument to dict for validation
                preprocessed_dict = {
                    "document_id": preprocessed_doc.document_id,
                    "sentence_metadata": preprocessed_doc.sentence_metadata,
                    "resolution_index": {},
                    "provenance_completeness": metadata_dict.get(
                        "provenance_completeness",
                        self.config["provenance_completeness_default"],
                    ),
                }
                self.wiring_validator.validate_adapter_to_orchestrator(
                    preprocessed_dict
                )
                self.logger.info("✓ Adapter → Orchestrator contract validation passed")
            except Exception as e:
                self.logger.error(
                    f"Adapter → Orchestrator contract validation failed: {e}"
                )
                raise ValueError(
                    f"Runtime contract violation at Adapter → Orchestrator boundary: {e}"
                ) from e

        return preprocessed_doc


def adapt_cpp_to_orchestrator(
    canon_package: Any, document_id: str
) -> PreprocessedDocument:
    """
    Convenience function to adapt CPP to PreprocessedDocument.

    Args:
        canon_package: CanonPolicyPackage from ingestion
        document_id: Unique document identifier

    Returns:
        PreprocessedDocument for orchestrator

    Raises:
        CPPAdapterError: If conversion fails
    """
    adapter = CPPAdapter()
    return adapter.to_preprocessed_document(canon_package, document_id)


__all__ = [
    "CPPAdapter",
    "CPPAdapterError",
    "adapt_cpp_to_orchestrator",
]

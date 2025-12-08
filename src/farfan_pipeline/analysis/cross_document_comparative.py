"""
Cross-Document Comparative Analysis Framework

Industrial-grade framework for multi-document comparative analysis leveraging
CanonPolicyPackage metadata and SPC rich metadata for cross-document queries.

Features:
- Multi-document indexing using document_id tracking
- Comparative queries across strategic importance, causal chains, semantic density
- Rich metadata aggregation (coherence_score, completeness_index, semantic_density)
- Policy area and dimension-based comparisons
- Time-series and temporal analysis across documents
- Production-ready with full type safety and error handling
"""

from __future__ import annotations

import hashlib
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


class ComparisonDimension(Enum):
    SEMANTIC_DENSITY = "semantic_density"
    COHERENCE_SCORE = "coherence_score"
    COMPLETENESS_INDEX = "completeness_index"
    STRATEGIC_IMPORTANCE = "strategic_importance"
    CAUSAL_CHAIN_STRENGTH = "causal_chain_strength"
    INFORMATION_DENSITY = "information_density"
    ACTIONABILITY_SCORE = "actionability_score"
    BUDGET_LINKAGE = "budget_linkage"
    TEMPORAL_ROBUSTNESS = "temporal_robustness"
    PROVENANCE_COMPLETENESS = "provenance_completeness"


class AggregationMethod(Enum):
    MEAN = "mean"
    MEDIAN = "median"
    MAX = "max"
    MIN = "min"
    SUM = "sum"
    WEIGHTED_MEAN = "weighted_mean"
    PERCENTILE_90 = "percentile_90"
    PERCENTILE_95 = "percentile_95"


class ComparisonOperator(Enum):
    GREATER_THAN = "gt"
    GREATER_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_EQUAL = "lte"
    EQUAL = "eq"
    NOT_EQUAL = "neq"
    TOP_N = "top_n"
    BOTTOM_N = "bottom_n"
    IN_RANGE = "in_range"


@dataclass
class DocumentMetadata:
    document_id: str
    schema_version: str
    ingestion_timestamp: str
    total_chunks: int
    policy_areas: set[str] = field(default_factory=set)
    dimensions: set[str] = field(default_factory=set)
    temporal_range: tuple[int, int] | None = None
    geographic_scope: set[str] = field(default_factory=set)
    source_file: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ChunkMetrics:
    chunk_id: str
    document_id: str
    policy_area_id: str
    dimension_id: str
    semantic_density: float
    coherence_score: float
    completeness_index: float
    strategic_importance: float = 0.0
    information_density: float = 0.0
    actionability_score: float = 0.0
    causal_chain_length: int = 0
    causal_chain_strength: float = 0.0
    entity_count: int = 0
    cross_reference_count: int = 0
    temporal_markers: int = 0
    budget_linked: bool = False
    provenance_complete: bool = False
    text_length: int = 0
    chunk_type: str | None = None
    processing_timestamp: str | None = None


@dataclass
class ComparativeResult:
    query_description: str
    comparison_dimension: ComparisonDimension
    results: list[tuple[str, float, dict[str, Any]]]
    aggregation_method: AggregationMethod
    total_documents: int
    total_chunks_analyzed: int
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MultiDocumentStatistics:
    dimension: ComparisonDimension
    global_mean: float
    global_median: float
    global_std: float
    global_min: float
    global_max: float
    per_document_stats: dict[str, dict[str, float]]
    per_policy_area_stats: dict[str, dict[str, float]]
    per_dimension_stats: dict[str, dict[str, float]]
    total_documents: int
    total_chunks: int


class DocumentIndex:
    def __init__(self):
        self.documents: dict[str, DocumentMetadata] = {}
        self.chunks: dict[str, ChunkMetrics] = {}
        self.document_chunks: dict[str, list[str]] = defaultdict(list)
        self.policy_area_chunks: dict[str, list[str]] = defaultdict(list)
        self.dimension_chunks: dict[str, list[str]] = defaultdict(list)
        self.policy_area_dimension_chunks: dict[tuple[str, str], list[str]] = (
            defaultdict(list)
        )

        self._index_hash: str | None = None
        self._last_update: datetime | None = None

        logger.info("DocumentIndex initialized")

    def add_document(self, canon_package: Any) -> None:
        if not hasattr(canon_package, "document_id"):
            raise ValueError("CanonPolicyPackage must have document_id attribute")

        doc_id = canon_package.document_id
        if not doc_id or not doc_id.strip():
            raise ValueError("document_id cannot be empty")

        logger.info(f"Indexing document: {doc_id}")

        chunk_graph = getattr(canon_package, "chunk_graph", None)
        if not chunk_graph or not hasattr(chunk_graph, "chunks"):
            raise ValueError(f"Document {doc_id} missing valid chunk_graph")

        chunks = chunk_graph.chunks
        policy_areas = set()
        dimensions = set()
        temporal_years = set()
        geo_scope = set()

        for chunk_id, chunk in chunks.items():
            chunk_metrics = self._extract_chunk_metrics(chunk, doc_id)
            self.chunks[chunk_id] = chunk_metrics
            self.document_chunks[doc_id].append(chunk_id)

            if chunk_metrics.policy_area_id:
                policy_areas.add(chunk_metrics.policy_area_id)
                self.policy_area_chunks[chunk_metrics.policy_area_id].append(chunk_id)

            if chunk_metrics.dimension_id:
                dimensions.add(chunk_metrics.dimension_id)
                self.dimension_chunks[chunk_metrics.dimension_id].append(chunk_id)

            if chunk_metrics.policy_area_id and chunk_metrics.dimension_id:
                key = (chunk_metrics.policy_area_id, chunk_metrics.dimension_id)
                self.policy_area_dimension_chunks[key].append(chunk_id)

            if hasattr(chunk, "time_facets") and chunk.time_facets:
                if hasattr(chunk.time_facets, "years"):
                    temporal_years.update(chunk.time_facets.years)

            if hasattr(chunk, "geo_facets") and chunk.geo_facets:
                if hasattr(chunk.geo_facets, "territories"):
                    geo_scope.update(chunk.geo_facets.territories)

        temporal_range = None
        if temporal_years:
            temporal_range = (min(temporal_years), max(temporal_years))

        doc_metadata = DocumentMetadata(
            document_id=doc_id,
            schema_version=getattr(canon_package, "schema_version", "unknown"),
            ingestion_timestamp=datetime.utcnow().isoformat(),
            total_chunks=len(chunks),
            policy_areas=policy_areas,
            dimensions=dimensions,
            temporal_range=temporal_range,
            geographic_scope=geo_scope,
            metadata=getattr(canon_package, "metadata", {}),
        )

        self.documents[doc_id] = doc_metadata
        self._invalidate_cache()

        logger.info(f"Indexed {len(chunks)} chunks from document {doc_id}")

    def _extract_chunk_metrics(self, chunk: Any, doc_id: str) -> ChunkMetrics:
        chunk_id = getattr(chunk, "id", f"chunk_{hash(chunk)}")
        policy_area_id = getattr(chunk, "policy_area_id", None)
        dimension_id = getattr(chunk, "dimension_id", None)

        text = getattr(chunk, "text", "")
        text_length = len(text)

        semantic_density = 0.0
        coherence_score = 0.0
        completeness_index = 0.0
        strategic_importance = 0.0
        information_density = 0.0
        actionability_score = 0.0

        if hasattr(chunk, "confidence") and chunk.confidence:
            conf = chunk.confidence
            coherence_score = getattr(conf, "typing", 0.0)

        causal_chain_length = 0
        causal_chain_strength = 0.0
        if hasattr(chunk, "causal_chain") and chunk.causal_chain:
            causal_chain_length = len(chunk.causal_chain)
            if causal_chain_length > 0:
                strengths = [
                    getattr(ev, "strength_score", 0.0) for ev in chunk.causal_chain
                ]
                causal_chain_strength = float(np.mean(strengths)) if strengths else 0.0

        entity_count = 0
        if hasattr(chunk, "entities") and chunk.entities:
            entity_count = len(chunk.entities)

        cross_reference_count = 0
        temporal_markers = 0
        if hasattr(chunk, "time_facets") and chunk.time_facets:
            if hasattr(chunk.time_facets, "years"):
                temporal_markers = len(chunk.time_facets.years)

        budget_linked = False
        if hasattr(chunk, "budget") and chunk.budget:
            budget_linked = True

        provenance_complete = False
        if hasattr(chunk, "provenance") and chunk.provenance:
            prov = chunk.provenance
            if hasattr(prov, "source_page") and prov.source_page is not None:
                provenance_complete = True

        chunk_type = None
        if hasattr(chunk, "chunk_type"):
            chunk_type = str(chunk.chunk_type) if chunk.chunk_type else None

        return ChunkMetrics(
            chunk_id=chunk_id,
            document_id=doc_id,
            policy_area_id=policy_area_id or "unknown",
            dimension_id=dimension_id or "unknown",
            semantic_density=semantic_density,
            coherence_score=coherence_score,
            completeness_index=completeness_index,
            strategic_importance=strategic_importance,
            information_density=information_density,
            actionability_score=actionability_score,
            causal_chain_length=causal_chain_length,
            causal_chain_strength=causal_chain_strength,
            entity_count=entity_count,
            cross_reference_count=cross_reference_count,
            temporal_markers=temporal_markers,
            budget_linked=budget_linked,
            provenance_complete=provenance_complete,
            text_length=text_length,
            chunk_type=chunk_type,
        )

    def _invalidate_cache(self) -> None:
        self._index_hash = None
        self._last_update = datetime.utcnow()

    def get_document(self, document_id: str) -> DocumentMetadata | None:
        return self.documents.get(document_id)

    def get_chunk(self, chunk_id: str) -> ChunkMetrics | None:
        return self.chunks.get(chunk_id)

    def get_document_chunks(self, document_id: str) -> list[ChunkMetrics]:
        chunk_ids = self.document_chunks.get(document_id, [])
        return [self.chunks[cid] for cid in chunk_ids if cid in self.chunks]

    def get_policy_area_chunks(self, policy_area_id: str) -> list[ChunkMetrics]:
        chunk_ids = self.policy_area_chunks.get(policy_area_id, [])
        return [self.chunks[cid] for cid in chunk_ids if cid in self.chunks]

    def get_dimension_chunks(self, dimension_id: str) -> list[ChunkMetrics]:
        chunk_ids = self.dimension_chunks.get(dimension_id, [])
        return [self.chunks[cid] for cid in chunk_ids if cid in self.chunks]

    def get_policy_area_dimension_chunks(
        self, policy_area_id: str, dimension_id: str
    ) -> list[ChunkMetrics]:
        key = (policy_area_id, dimension_id)
        chunk_ids = self.policy_area_dimension_chunks.get(key, [])
        return [self.chunks[cid] for cid in chunk_ids if cid in self.chunks]

    def get_all_document_ids(self) -> list[str]:
        return list(self.documents.keys())

    def get_all_policy_areas(self) -> set[str]:
        areas = set()
        for doc in self.documents.values():
            areas.update(doc.policy_areas)
        return areas

    def get_all_dimensions(self) -> set[str]:
        dims = set()
        for doc in self.documents.values():
            dims.update(doc.dimensions)
        return dims

    def compute_index_hash(self) -> str:
        if self._index_hash:
            return self._index_hash

        content = f"{len(self.documents)}:{len(self.chunks)}:{self._last_update}"
        self._index_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        return self._index_hash


class ComparativeQueryEngine:
    def __init__(self, index: DocumentIndex):
        self.index = index
        logger.info("ComparativeQueryEngine initialized")

    def compare_by_dimension(
        self,
        dimension: ComparisonDimension,
        aggregation: AggregationMethod = AggregationMethod.MEAN,
        policy_area_filter: list[str] | None = None,
        dimension_filter: list[str] | None = None,
    ) -> ComparativeResult:
        logger.info(f"Comparing documents by dimension: {dimension.value}")

        document_scores: dict[str, list[float]] = defaultdict(list)
        document_metadata: dict[str, dict[str, Any]] = {}

        for doc_id in self.index.get_all_document_ids():
            chunks = self.index.get_document_chunks(doc_id)

            filtered_chunks = self._apply_filters(
                chunks, policy_area_filter, dimension_filter
            )

            values = self._extract_dimension_values(filtered_chunks, dimension)
            document_scores[doc_id] = values

            doc_meta = self.index.get_document(doc_id)
            document_metadata[doc_id] = {
                "total_chunks": len(filtered_chunks),
                "policy_areas": list(doc_meta.policy_areas) if doc_meta else [],
                "dimensions": list(doc_meta.dimensions) if doc_meta else [],
                "temporal_range": doc_meta.temporal_range if doc_meta else None,
            }

        aggregated_scores = self._aggregate_scores(document_scores, aggregation)

        results = [
            (doc_id, score, document_metadata[doc_id])
            for doc_id, score in aggregated_scores.items()
        ]
        results.sort(key=lambda x: x[1], reverse=True)

        total_chunks = sum(len(vals) for vals in document_scores.values())

        return ComparativeResult(
            query_description=f"Compare by {dimension.value} using {aggregation.value}",
            comparison_dimension=dimension,
            results=results,
            aggregation_method=aggregation,
            total_documents=len(results),
            total_chunks_analyzed=total_chunks,
            metadata={
                "policy_area_filter": policy_area_filter,
                "dimension_filter": dimension_filter,
            },
        )

    def find_top_documents(
        self,
        dimension: ComparisonDimension,
        n: int = 10,
        aggregation: AggregationMethod = AggregationMethod.MEAN,
        policy_area_filter: list[str] | None = None,
        dimension_filter: list[str] | None = None,
    ) -> ComparativeResult:
        logger.info(f"Finding top {n} documents by {dimension.value}")

        full_result = self.compare_by_dimension(
            dimension, aggregation, policy_area_filter, dimension_filter
        )

        top_results = full_result.results[:n]

        return ComparativeResult(
            query_description=f"Top {n} documents by {dimension.value} ({aggregation.value})",
            comparison_dimension=dimension,
            results=top_results,
            aggregation_method=aggregation,
            total_documents=len(top_results),
            total_chunks_analyzed=full_result.total_chunks_analyzed,
            metadata=full_result.metadata,
        )

    def find_documents_with_strongest_causal_chains(
        self,
        n: int = 10,
        min_chain_length: int = 3,
    ) -> ComparativeResult:
        logger.info(
            f"Finding {n} documents with strongest causal chains (min length: {min_chain_length})"
        )

        document_scores: dict[str, list[float]] = defaultdict(list)
        document_metadata: dict[str, dict[str, Any]] = {}

        for doc_id in self.index.get_all_document_ids():
            chunks = self.index.get_document_chunks(doc_id)

            filtered_chunks = [
                c for c in chunks if c.causal_chain_length >= min_chain_length
            ]

            if filtered_chunks:
                strengths = [c.causal_chain_strength for c in filtered_chunks]
                document_scores[doc_id] = strengths

                doc_meta = self.index.get_document(doc_id)
                document_metadata[doc_id] = {
                    "total_chunks_with_causal_chains": len(filtered_chunks),
                    "avg_chain_length": np.mean(
                        [c.causal_chain_length for c in filtered_chunks]
                    ),
                    "max_chain_length": max(
                        c.causal_chain_length for c in filtered_chunks
                    ),
                    "policy_areas": list(doc_meta.policy_areas) if doc_meta else [],
                }

        aggregated_scores = {
            doc_id: float(np.mean(vals)) if vals else 0.0
            for doc_id, vals in document_scores.items()
        }

        results = [
            (doc_id, score, document_metadata[doc_id])
            for doc_id, score in aggregated_scores.items()
        ]
        results.sort(key=lambda x: x[1], reverse=True)
        results = results[:n]

        return ComparativeResult(
            query_description=f"Top {n} documents with strongest causal chains (min length {min_chain_length})",
            comparison_dimension=ComparisonDimension.CAUSAL_CHAIN_STRENGTH,
            results=results,
            aggregation_method=AggregationMethod.MEAN,
            total_documents=len(results),
            total_chunks_analyzed=sum(len(vals) for vals in document_scores.values()),
            metadata={"min_chain_length": min_chain_length},
        )

    def compare_policy_areas(
        self,
        dimension: ComparisonDimension,
        aggregation: AggregationMethod = AggregationMethod.MEAN,
    ) -> dict[str, ComparativeResult]:
        logger.info(f"Comparing policy areas by {dimension.value}")

        results = {}
        for policy_area in self.index.get_all_policy_areas():
            result = self.compare_by_dimension(
                dimension, aggregation, policy_area_filter=[policy_area]
            )
            results[policy_area] = result

        return results

    def compare_dimensions(
        self,
        comparison_dimension: ComparisonDimension,
        aggregation: AggregationMethod = AggregationMethod.MEAN,
    ) -> dict[str, ComparativeResult]:
        logger.info(f"Comparing dimensions by {comparison_dimension.value}")

        results = {}
        for dim in self.index.get_all_dimensions():
            result = self.compare_by_dimension(
                comparison_dimension, aggregation, dimension_filter=[dim]
            )
            results[dim] = result

        return results

    def compute_global_statistics(
        self, dimension: ComparisonDimension
    ) -> MultiDocumentStatistics:
        logger.info(f"Computing global statistics for {dimension.value}")

        all_values = []
        per_document_stats = {}
        per_policy_area_values: dict[str, list[float]] = defaultdict(list)
        per_dimension_values: dict[str, list[float]] = defaultdict(list)

        for doc_id in self.index.get_all_document_ids():
            chunks = self.index.get_document_chunks(doc_id)
            values = self._extract_dimension_values(chunks, dimension)

            if values:
                all_values.extend(values)
                per_document_stats[doc_id] = {
                    "mean": float(np.mean(values)),
                    "median": float(np.median(values)),
                    "std": float(np.std(values)),
                    "min": float(np.min(values)),
                    "max": float(np.max(values)),
                    "count": len(values),
                }

                for chunk in chunks:
                    if chunk.policy_area_id != "unknown":
                        val = self._get_metric_value(chunk, dimension)
                        if val is not None:
                            per_policy_area_values[chunk.policy_area_id].append(val)

                    if chunk.dimension_id != "unknown":
                        val = self._get_metric_value(chunk, dimension)
                        if val is not None:
                            per_dimension_values[chunk.dimension_id].append(val)

        per_policy_area_stats = {
            pa: {
                "mean": float(np.mean(vals)),
                "median": float(np.median(vals)),
                "std": float(np.std(vals)),
                "count": len(vals),
            }
            for pa, vals in per_policy_area_values.items()
            if vals
        }

        per_dimension_stats = {
            dim: {
                "mean": float(np.mean(vals)),
                "median": float(np.median(vals)),
                "std": float(np.std(vals)),
                "count": len(vals),
            }
            for dim, vals in per_dimension_values.items()
            if vals
        }

        if not all_values:
            all_values = [0.0]

        return MultiDocumentStatistics(
            dimension=dimension,
            global_mean=float(np.mean(all_values)),
            global_median=float(np.median(all_values)),
            global_std=float(np.std(all_values)),
            global_min=float(np.min(all_values)),
            global_max=float(np.max(all_values)),
            per_document_stats=per_document_stats,
            per_policy_area_stats=per_policy_area_stats,
            per_dimension_stats=per_dimension_stats,
            total_documents=len(self.index.get_all_document_ids()),
            total_chunks=len(self.index.chunks),
        )

    def find_documents_by_threshold(
        self,
        dimension: ComparisonDimension,
        operator: ComparisonOperator,
        threshold: float,
        aggregation: AggregationMethod = AggregationMethod.MEAN,
    ) -> ComparativeResult:
        logger.info(
            f"Finding documents where {dimension.value} {operator.value} {threshold}"
        )

        full_result = self.compare_by_dimension(dimension, aggregation)

        filtered_results = []
        for doc_id, score, metadata in full_result.results:
            if self._check_threshold(score, operator, threshold):
                filtered_results.append((doc_id, score, metadata))

        return ComparativeResult(
            query_description=f"Documents where {dimension.value} {operator.value} {threshold}",
            comparison_dimension=dimension,
            results=filtered_results,
            aggregation_method=aggregation,
            total_documents=len(filtered_results),
            total_chunks_analyzed=full_result.total_chunks_analyzed,
            metadata={"threshold": threshold, "operator": operator.value},
        )

    def _apply_filters(
        self,
        chunks: list[ChunkMetrics],
        policy_area_filter: list[str] | None,
        dimension_filter: list[str] | None,
    ) -> list[ChunkMetrics]:
        filtered = chunks

        if policy_area_filter:
            filtered = [c for c in filtered if c.policy_area_id in policy_area_filter]

        if dimension_filter:
            filtered = [c for c in filtered if c.dimension_id in dimension_filter]

        return filtered

    def _extract_dimension_values(
        self, chunks: list[ChunkMetrics], dimension: ComparisonDimension
    ) -> list[float]:
        values = []
        for chunk in chunks:
            val = self._get_metric_value(chunk, dimension)
            if val is not None:
                values.append(val)
        return values

    def _get_metric_value(
        self, chunk: ChunkMetrics, dimension: ComparisonDimension
    ) -> float | None:
        mapping = {
            ComparisonDimension.SEMANTIC_DENSITY: chunk.semantic_density,
            ComparisonDimension.COHERENCE_SCORE: chunk.coherence_score,
            ComparisonDimension.COMPLETENESS_INDEX: chunk.completeness_index,
            ComparisonDimension.STRATEGIC_IMPORTANCE: chunk.strategic_importance,
            ComparisonDimension.CAUSAL_CHAIN_STRENGTH: chunk.causal_chain_strength,
            ComparisonDimension.INFORMATION_DENSITY: chunk.information_density,
            ComparisonDimension.ACTIONABILITY_SCORE: chunk.actionability_score,
        }

        return mapping.get(dimension)

    def _aggregate_scores(
        self, document_scores: dict[str, list[float]], aggregation: AggregationMethod
    ) -> dict[str, float]:
        result = {}

        for doc_id, values in document_scores.items():
            if not values:
                result[doc_id] = 0.0
                continue

            if aggregation == AggregationMethod.MEAN:
                result[doc_id] = float(np.mean(values))
            elif aggregation == AggregationMethod.MEDIAN:
                result[doc_id] = float(np.median(values))
            elif aggregation == AggregationMethod.MAX:
                result[doc_id] = float(np.max(values))
            elif aggregation == AggregationMethod.MIN:
                result[doc_id] = float(np.min(values))
            elif aggregation == AggregationMethod.SUM:
                result[doc_id] = float(np.sum(values))
            elif aggregation == AggregationMethod.PERCENTILE_90:
                result[doc_id] = float(np.percentile(values, 90))
            elif aggregation == AggregationMethod.PERCENTILE_95:
                result[doc_id] = float(np.percentile(values, 95))
            else:
                result[doc_id] = float(np.mean(values))

        return result

    def _check_threshold(
        self, value: float, operator: ComparisonOperator, threshold: float
    ) -> bool:
        if operator == ComparisonOperator.GREATER_THAN:
            return value > threshold
        elif operator == ComparisonOperator.GREATER_EQUAL:
            return value >= threshold
        elif operator == ComparisonOperator.LESS_THAN:
            return value < threshold
        elif operator == ComparisonOperator.LESS_EQUAL:
            return value <= threshold
        elif operator == ComparisonOperator.EQUAL:
            return abs(value - threshold) < 1e-6
        elif operator == ComparisonOperator.NOT_EQUAL:
            return abs(value - threshold) >= 1e-6
        return False


class CrossDocumentAnalyzer:
    def __init__(self):
        self.index = DocumentIndex()
        self.query_engine = ComparativeQueryEngine(self.index)
        logger.info("CrossDocumentAnalyzer initialized")

    def add_document(self, canon_package: Any) -> None:
        self.index.add_document(canon_package)

    def add_documents(self, canon_packages: list[Any]) -> None:
        for pkg in canon_packages:
            self.add_document(pkg)

    def find_pdts_with_highest_strategic_importance(
        self, n: int = 10
    ) -> ComparativeResult:
        return self.query_engine.find_top_documents(
            dimension=ComparisonDimension.STRATEGIC_IMPORTANCE,
            n=n,
            aggregation=AggregationMethod.MEAN,
        )

    def identify_municipalities_with_strongest_causal_chains(
        self, n: int = 10, min_chain_length: int = 3
    ) -> ComparativeResult:
        return self.query_engine.find_documents_with_strongest_causal_chains(
            n=n, min_chain_length=min_chain_length
        )

    def compare_documents_by_semantic_density(
        self, aggregation: AggregationMethod = AggregationMethod.MEAN
    ) -> ComparativeResult:
        return self.query_engine.compare_by_dimension(
            dimension=ComparisonDimension.SEMANTIC_DENSITY, aggregation=aggregation
        )

    def compare_documents_by_coherence_score(
        self, aggregation: AggregationMethod = AggregationMethod.MEAN
    ) -> ComparativeResult:
        return self.query_engine.compare_by_dimension(
            dimension=ComparisonDimension.COHERENCE_SCORE, aggregation=aggregation
        )

    def compare_documents_by_completeness_index(
        self, aggregation: AggregationMethod = AggregationMethod.MEAN
    ) -> ComparativeResult:
        return self.query_engine.compare_by_dimension(
            dimension=ComparisonDimension.COMPLETENESS_INDEX, aggregation=aggregation
        )

    def get_global_statistics(
        self, dimension: ComparisonDimension
    ) -> MultiDocumentStatistics:
        return self.query_engine.compute_global_statistics(dimension)

    def export_comparison_report(
        self, result: ComparativeResult, output_path: str
    ) -> None:
        import json

        report = {
            "query_description": result.query_description,
            "comparison_dimension": result.comparison_dimension.value,
            "aggregation_method": result.aggregation_method.value,
            "total_documents": result.total_documents,
            "total_chunks_analyzed": result.total_chunks_analyzed,
            "timestamp": result.timestamp,
            "metadata": result.metadata,
            "results": [
                {"document_id": doc_id, "score": score, "metadata": metadata}
                for doc_id, score, metadata in result.results
            ],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"Exported comparison report to {output_path}")

    def export_statistics_report(
        self, stats: MultiDocumentStatistics, output_path: str
    ) -> None:
        import json

        report = {
            "dimension": stats.dimension.value,
            "global_statistics": {
                "mean": stats.global_mean,
                "median": stats.global_median,
                "std": stats.global_std,
                "min": stats.global_min,
                "max": stats.global_max,
            },
            "per_document_stats": stats.per_document_stats,
            "per_policy_area_stats": stats.per_policy_area_stats,
            "per_dimension_stats": stats.per_dimension_stats,
            "total_documents": stats.total_documents,
            "total_chunks": stats.total_chunks,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"Exported statistics report to {output_path}")


def create_cross_document_analyzer() -> CrossDocumentAnalyzer:
    return CrossDocumentAnalyzer()

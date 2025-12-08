"""
Cross-Document Integration Module

Integration layer connecting SmartPolicyChunk extraction with cross-document
comparative analysis. Handles conversion and enrichment of SPC data for
multi-document indexing.
"""

from __future__ import annotations

import logging
from typing import Any

from farfan_pipeline.analysis.cross_document_comparative import (
    CrossDocumentAnalyzer,
)

logger = logging.getLogger(__name__)


class SPCEnricher:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def enrich_canon_package_from_spc(
        self,
        smart_chunks: list[Any],
        document_id: str,
        schema_version: str = "SPC-2025.1",
    ) -> dict[str, Any]:
        self.logger.info(
            f"Enriching CanonPolicyPackage from {len(smart_chunks)} SmartPolicyChunks"
        )

        chunk_graph_data = {}
        policy_areas = set()
        dimensions = set()

        for spc in smart_chunks:
            chunk_id = getattr(spc, "chunk_id", f"chunk_{hash(spc)}")

            chunk_data = {
                "id": chunk_id,
                "text": getattr(spc, "text", ""),
                "policy_area_id": getattr(spc, "policy_area_id", None),
                "dimension_id": getattr(spc, "dimension_id", None),
            }

            if hasattr(spc, "semantic_density"):
                chunk_data["semantic_density"] = spc.semantic_density
            if hasattr(spc, "coherence_score"):
                chunk_data["coherence_score"] = spc.coherence_score
            if hasattr(spc, "completeness_index"):
                chunk_data["completeness_index"] = spc.completeness_index
            if hasattr(spc, "strategic_importance"):
                chunk_data["strategic_importance"] = spc.strategic_importance
            if hasattr(spc, "information_density"):
                chunk_data["information_density"] = spc.information_density
            if hasattr(spc, "actionability_score"):
                chunk_data["actionability_score"] = spc.actionability_score

            if hasattr(spc, "causal_chain"):
                chunk_data["causal_chain"] = spc.causal_chain
            if hasattr(spc, "policy_entities"):
                chunk_data["entities"] = spc.policy_entities
            if hasattr(spc, "temporal_dynamics") and spc.temporal_dynamics:
                chunk_data["temporal_markers"] = (
                    len(spc.temporal_dynamics.temporal_markers)
                    if hasattr(spc.temporal_dynamics, "temporal_markers")
                    else 0
                )
            if hasattr(spc, "strategic_context") and spc.strategic_context:
                if (
                    hasattr(spc.strategic_context, "budget_linkage")
                    and spc.strategic_context.budget_linkage
                ):
                    chunk_data["budget_linked"] = True
            if hasattr(spc, "provenance"):
                chunk_data["provenance"] = spc.provenance

            chunk_graph_data[chunk_id] = chunk_data

            if chunk_data.get("policy_area_id"):
                policy_areas.add(chunk_data["policy_area_id"])
            if chunk_data.get("dimension_id"):
                dimensions.add(chunk_data["dimension_id"])

        enriched_package = {
            "document_id": document_id,
            "schema_version": schema_version,
            "chunk_graph": {"chunks": chunk_graph_data},
            "metadata": {
                "spc_rich_data": True,
                "total_chunks": len(smart_chunks),
                "policy_areas": list(policy_areas),
                "dimensions": list(dimensions),
            },
        }

        self.logger.info(f"Enriched package with {len(chunk_graph_data)} chunks")
        return enriched_package

    def extract_spc_metrics_summary(self, smart_chunks: list[Any]) -> dict[str, Any]:
        if not smart_chunks:
            return {}

        semantic_densities = [
            getattr(spc, "semantic_density", 0.0)
            for spc in smart_chunks
            if hasattr(spc, "semantic_density")
        ]
        coherence_scores = [
            getattr(spc, "coherence_score", 0.0)
            for spc in smart_chunks
            if hasattr(spc, "coherence_score")
        ]
        completeness_indices = [
            getattr(spc, "completeness_index", 0.0)
            for spc in smart_chunks
            if hasattr(spc, "completeness_index")
        ]
        strategic_importance_scores = [
            getattr(spc, "strategic_importance", 0.0)
            for spc in smart_chunks
            if hasattr(spc, "strategic_importance")
        ]

        causal_chain_lengths = [
            len(getattr(spc, "causal_chain", []))
            for spc in smart_chunks
            if hasattr(spc, "causal_chain")
        ]

        import numpy as np

        summary = {
            "total_chunks": len(smart_chunks),
            "semantic_density": {
                "mean": (
                    float(np.mean(semantic_densities)) if semantic_densities else 0.0
                ),
                "median": (
                    float(np.median(semantic_densities)) if semantic_densities else 0.0
                ),
                "std": float(np.std(semantic_densities)) if semantic_densities else 0.0,
            },
            "coherence_score": {
                "mean": float(np.mean(coherence_scores)) if coherence_scores else 0.0,
                "median": (
                    float(np.median(coherence_scores)) if coherence_scores else 0.0
                ),
                "std": float(np.std(coherence_scores)) if coherence_scores else 0.0,
            },
            "completeness_index": {
                "mean": (
                    float(np.mean(completeness_indices))
                    if completeness_indices
                    else 0.0
                ),
                "median": (
                    float(np.median(completeness_indices))
                    if completeness_indices
                    else 0.0
                ),
                "std": (
                    float(np.std(completeness_indices)) if completeness_indices else 0.0
                ),
            },
            "strategic_importance": {
                "mean": (
                    float(np.mean(strategic_importance_scores))
                    if strategic_importance_scores
                    else 0.0
                ),
                "median": (
                    float(np.median(strategic_importance_scores))
                    if strategic_importance_scores
                    else 0.0
                ),
                "std": (
                    float(np.std(strategic_importance_scores))
                    if strategic_importance_scores
                    else 0.0
                ),
            },
            "causal_chains": {
                "avg_length": (
                    float(np.mean(causal_chain_lengths))
                    if causal_chain_lengths
                    else 0.0
                ),
                "max_length": (
                    int(np.max(causal_chain_lengths)) if causal_chain_lengths else 0
                ),
                "total_with_chains": sum(1 for l in causal_chain_lengths if l > 0),
            },
        }

        return summary


class CrossDocumentPipeline:
    def __init__(self):
        self.analyzer = CrossDocumentAnalyzer()
        self.enricher = SPCEnricher()
        self.logger = logging.getLogger(self.__class__.__name__)

    def process_spc_batch(
        self, spc_batches: dict[str, list[Any]]
    ) -> CrossDocumentAnalyzer:
        self.logger.info(f"Processing {len(spc_batches)} SPC batches")

        for document_id, smart_chunks in spc_batches.items():
            try:
                enriched_package = self.enricher.enrich_canon_package_from_spc(
                    smart_chunks, document_id
                )

                self.analyzer.add_document(enriched_package)

                self.logger.info(f"Successfully indexed document: {document_id}")
            except Exception as e:
                self.logger.error(f"Failed to process document {document_id}: {e}")

        return self.analyzer

    def add_spc_document(self, smart_chunks: list[Any], document_id: str) -> None:
        enriched_package = self.enricher.enrich_canon_package_from_spc(
            smart_chunks, document_id
        )
        self.analyzer.add_document(enriched_package)

    def get_analyzer(self) -> CrossDocumentAnalyzer:
        return self.analyzer

    def export_indexed_documents(self, output_path: str) -> None:
        import json

        data = {
            "total_documents": len(self.analyzer.index.get_all_document_ids()),
            "total_chunks": len(self.analyzer.index.chunks),
            "document_ids": self.analyzer.index.get_all_document_ids(),
            "policy_areas": sorted(list(self.analyzer.index.get_all_policy_areas())),
            "dimensions": sorted(list(self.analyzer.index.get_all_dimensions())),
            "index_hash": self.analyzer.index.compute_index_hash(),
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Exported index summary to {output_path}")


class MockCanonPackageAdapter:
    @staticmethod
    def from_dict(data: dict[str, Any]) -> Any:
        class MockPackage:
            def __init__(self, data):
                self.document_id = data.get("document_id")
                self.schema_version = data.get("schema_version", "unknown")
                self.metadata = data.get("metadata", {})

                chunk_graph_data = data.get("chunk_graph", {})
                chunks_data = chunk_graph_data.get("chunks", {})

                class MockChunkGraph:
                    def __init__(self, chunks_data):
                        self.chunks = {}
                        for chunk_id, chunk_data in chunks_data.items():
                            self.chunks[chunk_id] = MockChunk(chunk_data)

                class MockChunk:
                    def __init__(self, data):
                        self.id = data.get("id")
                        self.text = data.get("text", "")
                        self.policy_area_id = data.get("policy_area_id")
                        self.dimension_id = data.get("dimension_id")

                        if "causal_chain" in data:
                            self.causal_chain = data["causal_chain"]
                        if "entities" in data:
                            self.entities = data["entities"]
                        if "provenance" in data:
                            self.provenance = type(
                                "Provenance", (), data["provenance"]
                            )()
                        if "budget_linked" in data:
                            self.budget = (
                                type("Budget", (), {})()
                                if data["budget_linked"]
                                else None
                            )

                        class MockConfidence:
                            def __init__(self, typing_score):
                                self.typing = typing_score

                        coherence = data.get("coherence_score", 0.0)
                        self.confidence = MockConfidence(coherence)

                        if "time_facets" in data:

                            class MockTimeFacets:
                                def __init__(self, years):
                                    self.years = years

                            self.time_facets = MockTimeFacets(data["time_facets"])

                self.chunk_graph = MockChunkGraph(chunks_data)

        return MockPackage(data)


def create_cross_document_pipeline() -> CrossDocumentPipeline:
    return CrossDocumentPipeline()

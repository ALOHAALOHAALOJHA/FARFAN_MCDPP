"""
Integration tests for Cross-Document Comparative Analysis with SPC Pipeline
"""

import json

import pytest

from farfan_pipeline.analysis.cross_document_comparative import (
    ComparisonDimension,
    CrossDocumentAnalyzer,
)
from farfan_pipeline.analysis.cross_document_integration import (
    CrossDocumentPipeline,
    MockCanonPackageAdapter,
    SPCEnricher,
)


class MockSmartPolicyChunk:
    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        text: str,
        policy_area_id: str = "PA01",
        dimension_id: str = "DIM01",
        semantic_density: float = 0.75,
        coherence_score: float = 0.80,
        completeness_index: float = 0.85,
        strategic_importance: float = 0.70,
        causal_chain_length: int = 2,
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.text = text
        self.policy_area_id = policy_area_id
        self.dimension_id = dimension_id
        self.semantic_density = semantic_density
        self.coherence_score = coherence_score
        self.completeness_index = completeness_index
        self.strategic_importance = strategic_importance
        self.information_density = 0.65
        self.actionability_score = 0.72

        class CausalEvidence:
            def __init__(self, strength_score):
                self.strength_score = strength_score

        self.causal_chain = [CausalEvidence(0.7) for _ in range(causal_chain_length)]

        class PolicyEntity:
            def __init__(self):
                self.text = "Entity"

        self.policy_entities = [PolicyEntity() for _ in range(3)]

        class Provenance:
            def __init__(self):
                self.source_page = 1

        self.provenance = Provenance()

        class StrategicContext:
            def __init__(self):
                self.budget_linkage = "linked"

        self.strategic_context = StrategicContext()


@pytest.fixture
def sample_spc_batches():
    batches = {}

    for doc_idx in range(3):
        doc_id = f"municipality_{doc_idx:03d}"
        chunks = []

        for pa in range(1, 4):
            for dim in range(1, 3):
                chunk_id = f"PA{pa:02d}-DIM{dim:02d}"
                chunk = MockSmartPolicyChunk(
                    chunk_id=chunk_id,
                    document_id=doc_id,
                    text=f"Policy text for {doc_id} {chunk_id}",
                    policy_area_id=f"PA{pa:02d}",
                    dimension_id=f"DIM{dim:02d}",
                    semantic_density=0.70 + (doc_idx * 0.05),
                    coherence_score=0.75 + (doc_idx * 0.03),
                    completeness_index=0.80 + (doc_idx * 0.02),
                    strategic_importance=0.65 + (doc_idx * 0.08),
                    causal_chain_length=doc_idx + pa,
                )
                chunks.append(chunk)

        batches[doc_id] = chunks

    return batches


class TestSPCEnricher:
    def test_enrich_canon_package_from_spc(self, sample_spc_batches):
        enricher = SPCEnricher()
        doc_id = list(sample_spc_batches.keys())[0]
        chunks = sample_spc_batches[doc_id]

        enriched = enricher.enrich_canon_package_from_spc(
            smart_chunks=chunks, document_id=doc_id
        )

        assert enriched["document_id"] == doc_id
        assert enriched["schema_version"] == "SPC-2025.1"
        assert "chunk_graph" in enriched
        assert "chunks" in enriched["chunk_graph"]
        assert len(enriched["chunk_graph"]["chunks"]) == len(chunks)

    def test_enriched_package_metadata(self, sample_spc_batches):
        enricher = SPCEnricher()
        doc_id = list(sample_spc_batches.keys())[0]
        chunks = sample_spc_batches[doc_id]

        enriched = enricher.enrich_canon_package_from_spc(
            smart_chunks=chunks, document_id=doc_id
        )

        metadata = enriched["metadata"]
        assert metadata["spc_rich_data"] is True
        assert metadata["total_chunks"] == len(chunks)
        assert len(metadata["policy_areas"]) > 0
        assert len(metadata["dimensions"]) > 0

    def test_extract_spc_metrics_summary(self, sample_spc_batches):
        enricher = SPCEnricher()
        chunks = list(sample_spc_batches.values())[0]

        summary = enricher.extract_spc_metrics_summary(chunks)

        assert "total_chunks" in summary
        assert summary["total_chunks"] == len(chunks)
        assert "semantic_density" in summary
        assert "coherence_score" in summary
        assert "completeness_index" in summary
        assert "strategic_importance" in summary
        assert "causal_chains" in summary

        assert summary["semantic_density"]["mean"] > 0
        assert summary["coherence_score"]["mean"] > 0
        assert summary["completeness_index"]["mean"] > 0


class TestCrossDocumentPipeline:
    def test_process_spc_batch(self, sample_spc_batches):
        pipeline = CrossDocumentPipeline()

        analyzer = pipeline.process_spc_batch(sample_spc_batches)

        assert len(analyzer.index.documents) == len(sample_spc_batches)
        assert len(analyzer.index.chunks) > 0

    def test_add_spc_document(self, sample_spc_batches):
        pipeline = CrossDocumentPipeline()
        doc_id = list(sample_spc_batches.keys())[0]
        chunks = sample_spc_batches[doc_id]

        pipeline.add_spc_document(chunks, doc_id)

        analyzer = pipeline.get_analyzer()
        assert doc_id in analyzer.index.documents
        assert len(analyzer.index.get_document_chunks(doc_id)) > 0

    def test_get_analyzer(self, sample_spc_batches):
        pipeline = CrossDocumentPipeline()
        pipeline.process_spc_batch(sample_spc_batches)

        analyzer = pipeline.get_analyzer()

        assert isinstance(analyzer, CrossDocumentAnalyzer)
        assert len(analyzer.index.documents) > 0

    def test_export_indexed_documents(self, sample_spc_batches, tmp_path):
        pipeline = CrossDocumentPipeline()
        pipeline.process_spc_batch(sample_spc_batches)

        output_path = tmp_path / "index_summary.json"
        pipeline.export_indexed_documents(str(output_path))

        assert output_path.exists()

        with open(output_path) as f:
            data = json.load(f)

        assert "total_documents" in data
        assert "total_chunks" in data
        assert "document_ids" in data
        assert data["total_documents"] == len(sample_spc_batches)


class TestEndToEndIntegration:
    def test_full_pipeline_with_comparative_queries(self, sample_spc_batches):
        pipeline = CrossDocumentPipeline()
        analyzer = pipeline.process_spc_batch(sample_spc_batches)

        result = analyzer.find_pdts_with_highest_strategic_importance(n=2)

        assert result.total_documents == 2
        assert len(result.results) == 2

        scores = [score for _, score, _ in result.results]
        assert scores[0] >= scores[1]

    def test_causal_chain_analysis_integration(self, sample_spc_batches):
        pipeline = CrossDocumentPipeline()
        analyzer = pipeline.process_spc_batch(sample_spc_batches)

        result = analyzer.identify_municipalities_with_strongest_causal_chains(
            n=3, min_chain_length=2
        )

        assert result.total_documents > 0
        assert len(result.results) <= 3

        for _, strength, metadata in result.results:
            assert strength >= 0.0
            assert "avg_chain_length" in metadata
            assert metadata["avg_chain_length"] >= 2.0

    def test_multiple_dimension_comparisons(self, sample_spc_batches):
        pipeline = CrossDocumentPipeline()
        analyzer = pipeline.process_spc_batch(sample_spc_batches)

        dimensions = [
            ComparisonDimension.SEMANTIC_DENSITY,
            ComparisonDimension.COHERENCE_SCORE,
            ComparisonDimension.COMPLETENESS_INDEX,
            ComparisonDimension.STRATEGIC_IMPORTANCE,
        ]

        for dimension in dimensions:
            result = analyzer.query_engine.compare_by_dimension(dimension)
            assert result.total_documents == len(sample_spc_batches)
            assert len(result.results) == len(sample_spc_batches)

    def test_global_statistics_integration(self, sample_spc_batches):
        pipeline = CrossDocumentPipeline()
        analyzer = pipeline.process_spc_batch(sample_spc_batches)

        stats = analyzer.get_global_statistics(ComparisonDimension.COHERENCE_SCORE)

        assert stats.total_documents == len(sample_spc_batches)
        assert stats.total_chunks > 0
        assert stats.global_mean > 0
        assert len(stats.per_document_stats) == len(sample_spc_batches)

    def test_policy_area_filtering_integration(self, sample_spc_batches):
        pipeline = CrossDocumentPipeline()
        analyzer = pipeline.process_spc_batch(sample_spc_batches)

        result = analyzer.query_engine.compare_by_dimension(
            dimension=ComparisonDimension.COHERENCE_SCORE, policy_area_filter=["PA01"]
        )

        assert result.total_documents == len(sample_spc_batches)
        assert result.total_chunks_analyzed > 0

    def test_dimension_filtering_integration(self, sample_spc_batches):
        pipeline = CrossDocumentPipeline()
        analyzer = pipeline.process_spc_batch(sample_spc_batches)

        result = analyzer.query_engine.compare_by_dimension(
            dimension=ComparisonDimension.COHERENCE_SCORE, dimension_filter=["DIM01"]
        )

        assert result.total_documents == len(sample_spc_batches)
        assert result.total_chunks_analyzed > 0


class TestMockCanonPackageAdapter:
    def test_from_dict_basic(self):
        data = {
            "document_id": "test_doc",
            "schema_version": "SPC-2025.1",
            "chunk_graph": {
                "chunks": {
                    "chunk_1": {
                        "id": "chunk_1",
                        "text": "Test text",
                        "policy_area_id": "PA01",
                        "dimension_id": "DIM01",
                        "coherence_score": 0.8,
                    }
                }
            },
        }

        package = MockCanonPackageAdapter.from_dict(data)

        assert package.document_id == "test_doc"
        assert package.schema_version == "SPC-2025.1"
        assert hasattr(package, "chunk_graph")
        assert len(package.chunk_graph.chunks) == 1

    def test_from_dict_with_causal_chains(self):
        data = {
            "document_id": "test_doc",
            "chunk_graph": {
                "chunks": {
                    "chunk_1": {
                        "id": "chunk_1",
                        "text": "Test",
                        "policy_area_id": "PA01",
                        "dimension_id": "DIM01",
                        "causal_chain": [{"strength": 0.7}, {"strength": 0.8}],
                    }
                }
            },
        }

        package = MockCanonPackageAdapter.from_dict(data)
        chunk = package.chunk_graph.chunks["chunk_1"]

        assert hasattr(chunk, "causal_chain")
        assert len(chunk.causal_chain) == 2


class TestDataConsistency:
    def test_enriched_data_indexable(self, sample_spc_batches):
        enricher = SPCEnricher()
        doc_id = list(sample_spc_batches.keys())[0]
        chunks = sample_spc_batches[doc_id]

        enriched = enricher.enrich_canon_package_from_spc(chunks, doc_id)

        mock_package = MockCanonPackageAdapter.from_dict(enriched)

        analyzer = CrossDocumentAnalyzer()
        analyzer.add_document(mock_package)

        assert doc_id in analyzer.index.documents
        assert len(analyzer.index.get_document_chunks(doc_id)) == len(chunks)

    def test_metrics_preservation(self, sample_spc_batches):
        doc_id = list(sample_spc_batches.keys())[0]
        original_chunks = sample_spc_batches[doc_id]

        pipeline = CrossDocumentPipeline()
        pipeline.add_spc_document(original_chunks, doc_id)

        analyzer = pipeline.get_analyzer()
        indexed_chunks = analyzer.index.get_document_chunks(doc_id)

        assert len(indexed_chunks) == len(original_chunks)

        for indexed_chunk in indexed_chunks:
            assert indexed_chunk.document_id == doc_id
            assert indexed_chunk.policy_area_id is not None
            assert indexed_chunk.dimension_id is not None

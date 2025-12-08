"""
Unit tests for Cross-Document Comparative Analysis Framework
"""

import json
from typing import Any

import pytest

from farfan_pipeline.analysis.cross_document_comparative import (
    AggregationMethod,
    ChunkMetrics,
    ComparativeQueryEngine,
    ComparisonDimension,
    ComparisonOperator,
    CrossDocumentAnalyzer,
    DocumentIndex,
)


class MockCanonPackage:
    def __init__(
        self,
        document_id: str,
        chunks: dict[str, Any],
        schema_version: str = "SPC-2025.1",
    ):
        self.document_id = document_id
        self.schema_version = schema_version
        self.metadata = {}

        class ChunkGraph:
            def __init__(self, chunks):
                self.chunks = chunks

        self.chunk_graph = ChunkGraph(chunks)


class MockChunk:
    def __init__(
        self,
        chunk_id: str,
        text: str,
        policy_area_id: str = "PA01",
        dimension_id: str = "DIM01",
        coherence_score: float = 0.8,
        causal_chain_length: int = 0,
    ):
        self.id = chunk_id
        self.text = text
        self.policy_area_id = policy_area_id
        self.dimension_id = dimension_id

        class Confidence:
            def __init__(self, typing):
                self.typing = typing

        self.confidence = Confidence(coherence_score)

        if causal_chain_length > 0:
            self.causal_chain = [
                type("CausalEvidence", (), {"strength_score": 0.7})()
                for _ in range(causal_chain_length)
            ]
        else:
            self.causal_chain = []


@pytest.fixture
def sample_packages():
    packages = []

    for i in range(3):
        doc_id = f"doc_{i:03d}"
        chunks = {}

        for pa in range(1, 4):
            for dim in range(1, 3):
                chunk_id = f"chunk_{i}_{pa}_{dim}"
                chunk = MockChunk(
                    chunk_id=chunk_id,
                    text=f"Sample text for chunk {chunk_id}",
                    policy_area_id=f"PA{pa:02d}",
                    dimension_id=f"DIM{dim:02d}",
                    coherence_score=0.7 + (i * 0.05) + (pa * 0.02),
                    causal_chain_length=i + pa,
                )
                chunks[chunk_id] = chunk

        package = MockCanonPackage(doc_id, chunks)
        packages.append(package)

    return packages


@pytest.fixture
def document_index(sample_packages):
    index = DocumentIndex()
    for package in sample_packages:
        index.add_document(package)
    return index


@pytest.fixture
def query_engine(document_index):
    return ComparativeQueryEngine(document_index)


@pytest.fixture
def analyzer(sample_packages):
    analyzer = CrossDocumentAnalyzer()
    for package in sample_packages:
        analyzer.add_document(package)
    return analyzer


class TestDocumentIndex:
    def test_index_initialization(self):
        index = DocumentIndex()
        assert len(index.documents) == 0
        assert len(index.chunks) == 0

    def test_add_document(self, sample_packages):
        index = DocumentIndex()
        package = sample_packages[0]

        index.add_document(package)

        assert len(index.documents) == 1
        assert package.document_id in index.documents
        assert len(index.chunks) == len(package.chunk_graph.chunks)

    def test_add_multiple_documents(self, sample_packages):
        index = DocumentIndex()

        for package in sample_packages:
            index.add_document(package)

        assert len(index.documents) == len(sample_packages)
        assert len(index.chunks) > 0

    def test_get_document_chunks(self, document_index, sample_packages):
        doc_id = sample_packages[0].document_id
        chunks = document_index.get_document_chunks(doc_id)

        assert len(chunks) > 0
        assert all(isinstance(c, ChunkMetrics) for c in chunks)
        assert all(c.document_id == doc_id for c in chunks)

    def test_get_policy_area_chunks(self, document_index):
        chunks = document_index.get_policy_area_chunks("PA01")

        assert len(chunks) > 0
        assert all(c.policy_area_id == "PA01" for c in chunks)

    def test_get_dimension_chunks(self, document_index):
        chunks = document_index.get_dimension_chunks("DIM01")

        assert len(chunks) > 0
        assert all(c.dimension_id == "DIM01" for c in chunks)

    def test_get_policy_area_dimension_chunks(self, document_index):
        chunks = document_index.get_policy_area_dimension_chunks("PA01", "DIM01")

        assert len(chunks) > 0
        assert all(
            c.policy_area_id == "PA01" and c.dimension_id == "DIM01" for c in chunks
        )

    def test_compute_index_hash(self, document_index):
        hash1 = document_index.compute_index_hash()
        assert hash1 is not None
        assert len(hash1) > 0

        hash2 = document_index.compute_index_hash()
        assert hash1 == hash2


class TestComparativeQueryEngine:
    def test_compare_by_dimension(self, query_engine):
        result = query_engine.compare_by_dimension(
            dimension=ComparisonDimension.COHERENCE_SCORE,
            aggregation=AggregationMethod.MEAN,
        )

        assert result.total_documents > 0
        assert len(result.results) == result.total_documents
        assert result.comparison_dimension == ComparisonDimension.COHERENCE_SCORE

    def test_find_top_documents(self, query_engine):
        result = query_engine.find_top_documents(
            dimension=ComparisonDimension.COHERENCE_SCORE, n=2
        )

        assert len(result.results) <= 2

        scores = [score for _, score, _ in result.results]
        assert scores == sorted(scores, reverse=True)

    def test_find_strongest_causal_chains(self, query_engine):
        result = query_engine.find_documents_with_strongest_causal_chains(
            n=3, min_chain_length=2
        )

        assert result.total_documents > 0
        assert len(result.results) <= 3

    def test_compare_policy_areas(self, query_engine):
        results = query_engine.compare_policy_areas(
            dimension=ComparisonDimension.COHERENCE_SCORE
        )

        assert len(results) > 0
        assert "PA01" in results or "PA02" in results or "PA03" in results

    def test_compare_dimensions(self, query_engine):
        results = query_engine.compare_dimensions(
            comparison_dimension=ComparisonDimension.COHERENCE_SCORE
        )

        assert len(results) > 0
        assert "DIM01" in results or "DIM02" in results

    def test_compute_global_statistics(self, query_engine):
        stats = query_engine.compute_global_statistics(
            dimension=ComparisonDimension.COHERENCE_SCORE
        )

        assert stats.total_documents > 0
        assert stats.total_chunks > 0
        assert stats.global_mean >= 0
        assert stats.global_median >= 0
        assert stats.global_std >= 0
        assert len(stats.per_document_stats) > 0

    def test_find_documents_by_threshold(self, query_engine):
        result = query_engine.find_documents_by_threshold(
            dimension=ComparisonDimension.COHERENCE_SCORE,
            operator=ComparisonOperator.GREATER_EQUAL,
            threshold=0.7,
        )

        assert result.total_documents >= 0
        for _, score, _ in result.results:
            assert score >= 0.7

    def test_aggregation_methods(self, query_engine):
        for method in [
            AggregationMethod.MEAN,
            AggregationMethod.MEDIAN,
            AggregationMethod.MAX,
        ]:
            result = query_engine.compare_by_dimension(
                dimension=ComparisonDimension.COHERENCE_SCORE, aggregation=method
            )
            assert result.aggregation_method == method


class TestCrossDocumentAnalyzer:
    def test_analyzer_initialization(self):
        analyzer = CrossDocumentAnalyzer()
        assert analyzer.index is not None
        assert analyzer.query_engine is not None

    def test_add_documents(self, sample_packages):
        analyzer = CrossDocumentAnalyzer()
        analyzer.add_documents(sample_packages)

        assert len(analyzer.index.documents) == len(sample_packages)

    def test_find_pdts_with_highest_strategic_importance(self, analyzer):
        result = analyzer.find_pdts_with_highest_strategic_importance(n=2)

        assert len(result.results) <= 2
        assert result.comparison_dimension == ComparisonDimension.STRATEGIC_IMPORTANCE

    def test_identify_municipalities_with_strongest_causal_chains(self, analyzer):
        result = analyzer.identify_municipalities_with_strongest_causal_chains(
            n=2, min_chain_length=2
        )

        assert len(result.results) <= 2

    def test_compare_documents_by_semantic_density(self, analyzer):
        result = analyzer.compare_documents_by_semantic_density()

        assert result.comparison_dimension == ComparisonDimension.SEMANTIC_DENSITY
        assert result.total_documents > 0

    def test_compare_documents_by_coherence_score(self, analyzer):
        result = analyzer.compare_documents_by_coherence_score()

        assert result.comparison_dimension == ComparisonDimension.COHERENCE_SCORE
        assert result.total_documents > 0

    def test_compare_documents_by_completeness_index(self, analyzer):
        result = analyzer.compare_documents_by_completeness_index()

        assert result.comparison_dimension == ComparisonDimension.COMPLETENESS_INDEX
        assert result.total_documents > 0

    def test_get_global_statistics(self, analyzer):
        stats = analyzer.get_global_statistics(ComparisonDimension.COHERENCE_SCORE)

        assert stats.dimension == ComparisonDimension.COHERENCE_SCORE
        assert stats.total_documents > 0

    def test_export_comparison_report(self, analyzer, tmp_path):
        result = analyzer.find_pdts_with_highest_strategic_importance(n=2)
        output_path = tmp_path / "report.json"

        analyzer.export_comparison_report(result, str(output_path))

        assert output_path.exists()

        with open(output_path) as f:
            data = json.load(f)

        assert "query_description" in data
        assert "results" in data
        assert len(data["results"]) <= 2

    def test_export_statistics_report(self, analyzer, tmp_path):
        stats = analyzer.get_global_statistics(ComparisonDimension.COHERENCE_SCORE)
        output_path = tmp_path / "stats.json"

        analyzer.export_statistics_report(stats, str(output_path))

        assert output_path.exists()

        with open(output_path) as f:
            data = json.load(f)

        assert "dimension" in data
        assert "global_statistics" in data
        assert "per_document_stats" in data


class TestComparisonOperators:
    @pytest.mark.parametrize(
        "operator,value,threshold,expected",
        [
            (ComparisonOperator.GREATER_THAN, 0.8, 0.7, True),
            (ComparisonOperator.GREATER_THAN, 0.6, 0.7, False),
            (ComparisonOperator.GREATER_EQUAL, 0.7, 0.7, True),
            (ComparisonOperator.LESS_THAN, 0.6, 0.7, True),
            (ComparisonOperator.LESS_THAN, 0.8, 0.7, False),
            (ComparisonOperator.LESS_EQUAL, 0.7, 0.7, True),
        ],
    )
    def test_threshold_checks(self, query_engine, operator, value, threshold, expected):
        result = query_engine._check_threshold(value, operator, threshold)
        assert result == expected


class TestEdgeCases:
    def test_empty_index(self):
        index = DocumentIndex()
        engine = ComparativeQueryEngine(index)

        result = engine.compare_by_dimension(
            dimension=ComparisonDimension.COHERENCE_SCORE
        )

        assert result.total_documents == 0
        assert len(result.results) == 0

    def test_document_without_chunks(self):
        index = DocumentIndex()
        package = MockCanonPackage("empty_doc", {})

        with pytest.raises(ValueError):
            index.add_document(package)

    def test_invalid_document_id(self):
        chunks = {"chunk_1": MockChunk("chunk_1", "text")}
        package = MockCanonPackage("", chunks)

        index = DocumentIndex()
        with pytest.raises(ValueError):
            index.add_document(package)

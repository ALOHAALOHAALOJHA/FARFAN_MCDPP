"""
Cross-Document Comparative Analysis API

REST API endpoints for multi-document comparative queries and analysis.
Production-ready API with comprehensive validation and error handling.
"""

from __future__ import annotations

import logging

from farfan_pipeline.analysis.cross_document_comparative import (
    AggregationMethod,
    ComparisonDimension,
    ComparisonOperator,
    CrossDocumentAnalyzer,
)
from flask import Blueprint, jsonify, request
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)

cross_document_bp = Blueprint("cross_document", __name__, url_prefix="/api/v1/cross-document")


class ComparisonRequest(BaseModel):
    dimension: str = Field(..., description="Comparison dimension to use")
    aggregation_method: str = Field(default="mean", description="Aggregation method")
    policy_area_filter: list[str] | None = Field(default=None, description="Filter by policy areas")
    dimension_filter: list[str] | None = Field(default=None, description="Filter by dimensions")
    top_n: int | None = Field(default=None, description="Return only top N results")


class ThresholdQueryRequest(BaseModel):
    dimension: str = Field(..., description="Comparison dimension")
    operator: str = Field(..., description="Comparison operator (gt, gte, lt, lte, eq, neq)")
    threshold: float = Field(..., description="Threshold value")
    aggregation_method: str = Field(default="mean", description="Aggregation method")


class CausalChainQueryRequest(BaseModel):
    top_n: int = Field(default=10, description="Number of top results to return")
    min_chain_length: int = Field(default=3, description="Minimum causal chain length")


class StatisticsRequest(BaseModel):
    dimension: str = Field(..., description="Dimension to compute statistics for")


_analyzer: CrossDocumentAnalyzer | None = None


def initialize_analyzer(analyzer: CrossDocumentAnalyzer) -> None:
    global _analyzer
    _analyzer = analyzer
    logger.info("Cross-document analyzer initialized for API")


def get_analyzer() -> CrossDocumentAnalyzer:
    if _analyzer is None:
        raise RuntimeError("CrossDocumentAnalyzer not initialized. Call initialize_analyzer first.")
    return _analyzer


@cross_document_bp.route("/health", methods=["GET"])
def health_check():
    try:
        analyzer = get_analyzer()
        doc_count = len(analyzer.index.get_all_document_ids())
        chunk_count = len(analyzer.index.chunks)

        return (
            jsonify(
                {
                    "status": "healthy",
                    "documents_indexed": doc_count,
                    "chunks_indexed": chunk_count,
                    "policy_areas": len(analyzer.index.get_all_policy_areas()),
                    "dimensions": len(analyzer.index.get_all_dimensions()),
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 503


@cross_document_bp.route("/compare", methods=["POST"])
def compare_documents():
    try:
        data = request.get_json()
        req = ComparisonRequest(**data)

        try:
            dimension = ComparisonDimension(req.dimension)
        except ValueError:
            return (
                jsonify(
                    {
                        "error": f"Invalid dimension: {req.dimension}",
                        "valid_dimensions": [d.value for d in ComparisonDimension],
                    }
                ),
                400,
            )

        try:
            aggregation = AggregationMethod(req.aggregation_method)
        except ValueError:
            return (
                jsonify(
                    {
                        "error": f"Invalid aggregation method: {req.aggregation_method}",
                        "valid_methods": [m.value for m in AggregationMethod],
                    }
                ),
                400,
            )

        analyzer = get_analyzer()

        if req.top_n:
            result = analyzer.query_engine.find_top_documents(
                dimension=dimension,
                n=req.top_n,
                aggregation=aggregation,
                policy_area_filter=req.policy_area_filter,
                dimension_filter=req.dimension_filter,
            )
        else:
            result = analyzer.query_engine.compare_by_dimension(
                dimension=dimension,
                aggregation=aggregation,
                policy_area_filter=req.policy_area_filter,
                dimension_filter=req.dimension_filter,
            )

        return (
            jsonify(
                {
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
            ),
            200,
        )

    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.errors()}), 400
    except Exception as e:
        logger.error(f"Comparison failed: {e}", exc_info=True)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@cross_document_bp.route("/highest-strategic-importance", methods=["GET"])
def highest_strategic_importance():
    try:
        n = request.args.get("n", default=10, type=int)

        analyzer = get_analyzer()
        result = analyzer.find_pdts_with_highest_strategic_importance(n=n)

        return (
            jsonify(
                {
                    "query_description": result.query_description,
                    "total_documents": result.total_documents,
                    "total_chunks_analyzed": result.total_chunks_analyzed,
                    "results": [
                        {
                            "document_id": doc_id,
                            "strategic_importance_score": score,
                            "metadata": metadata,
                        }
                        for doc_id, score, metadata in result.results
                    ],
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Strategic importance query failed: {e}", exc_info=True)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@cross_document_bp.route("/strongest-causal-chains", methods=["POST"])
def strongest_causal_chains():
    try:
        data = request.get_json() or {}
        req = CausalChainQueryRequest(**data)

        analyzer = get_analyzer()
        result = analyzer.identify_municipalities_with_strongest_causal_chains(
            n=req.top_n, min_chain_length=req.min_chain_length
        )

        return (
            jsonify(
                {
                    "query_description": result.query_description,
                    "total_documents": result.total_documents,
                    "total_chunks_analyzed": result.total_chunks_analyzed,
                    "metadata": result.metadata,
                    "results": [
                        {
                            "document_id": doc_id,
                            "causal_chain_strength": score,
                            "metadata": metadata,
                        }
                        for doc_id, score, metadata in result.results
                    ],
                }
            ),
            200,
        )

    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.errors()}), 400
    except Exception as e:
        logger.error(f"Causal chain query failed: {e}", exc_info=True)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@cross_document_bp.route("/threshold-query", methods=["POST"])
def threshold_query():
    try:
        data = request.get_json()
        req = ThresholdQueryRequest(**data)

        try:
            dimension = ComparisonDimension(req.dimension)
        except ValueError:
            return (
                jsonify(
                    {
                        "error": f"Invalid dimension: {req.dimension}",
                        "valid_dimensions": [d.value for d in ComparisonDimension],
                    }
                ),
                400,
            )

        try:
            operator = ComparisonOperator(req.operator)
        except ValueError:
            return (
                jsonify(
                    {
                        "error": f"Invalid operator: {req.operator}",
                        "valid_operators": [o.value for o in ComparisonOperator],
                    }
                ),
                400,
            )

        try:
            aggregation = AggregationMethod(req.aggregation_method)
        except ValueError:
            return (
                jsonify(
                    {
                        "error": f"Invalid aggregation method: {req.aggregation_method}",
                        "valid_methods": [m.value for m in AggregationMethod],
                    }
                ),
                400,
            )

        analyzer = get_analyzer()
        result = analyzer.query_engine.find_documents_by_threshold(
            dimension=dimension,
            operator=operator,
            threshold=req.threshold,
            aggregation=aggregation,
        )

        return (
            jsonify(
                {
                    "query_description": result.query_description,
                    "total_documents": result.total_documents,
                    "total_chunks_analyzed": result.total_chunks_analyzed,
                    "metadata": result.metadata,
                    "results": [
                        {"document_id": doc_id, "score": score, "metadata": metadata}
                        for doc_id, score, metadata in result.results
                    ],
                }
            ),
            200,
        )

    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.errors()}), 400
    except Exception as e:
        logger.error(f"Threshold query failed: {e}", exc_info=True)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@cross_document_bp.route("/statistics", methods=["POST"])
def global_statistics():
    try:
        data = request.get_json()
        req = StatisticsRequest(**data)

        try:
            dimension = ComparisonDimension(req.dimension)
        except ValueError:
            return (
                jsonify(
                    {
                        "error": f"Invalid dimension: {req.dimension}",
                        "valid_dimensions": [d.value for d in ComparisonDimension],
                    }
                ),
                400,
            )

        analyzer = get_analyzer()
        stats = analyzer.get_global_statistics(dimension)

        return (
            jsonify(
                {
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
            ),
            200,
        )

    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.errors()}), 400
    except Exception as e:
        logger.error(f"Statistics query failed: {e}", exc_info=True)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@cross_document_bp.route("/compare-policy-areas", methods=["GET"])
def compare_policy_areas():
    try:
        dimension_str = request.args.get("dimension", default="strategic_importance")
        aggregation_str = request.args.get("aggregation", default="mean")

        try:
            dimension = ComparisonDimension(dimension_str)
        except ValueError:
            return (
                jsonify(
                    {
                        "error": f"Invalid dimension: {dimension_str}",
                        "valid_dimensions": [d.value for d in ComparisonDimension],
                    }
                ),
                400,
            )

        try:
            aggregation = AggregationMethod(aggregation_str)
        except ValueError:
            return (
                jsonify(
                    {
                        "error": f"Invalid aggregation method: {aggregation_str}",
                        "valid_methods": [m.value for m in AggregationMethod],
                    }
                ),
                400,
            )

        analyzer = get_analyzer()
        results_by_area = analyzer.query_engine.compare_policy_areas(
            dimension=dimension, aggregation=aggregation
        )

        return (
            jsonify(
                {
                    "dimension": dimension.value,
                    "aggregation_method": aggregation.value,
                    "policy_areas": {
                        area: {
                            "query_description": result.query_description,
                            "total_documents": result.total_documents,
                            "total_chunks_analyzed": result.total_chunks_analyzed,
                            "results": [
                                {
                                    "document_id": doc_id,
                                    "score": score,
                                    "metadata": metadata,
                                }
                                for doc_id, score, metadata in result.results
                            ],
                        }
                        for area, result in results_by_area.items()
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Policy area comparison failed: {e}", exc_info=True)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@cross_document_bp.route("/compare-dimensions", methods=["GET"])
def compare_dimensions():
    try:
        comparison_dim_str = request.args.get(
            "comparison_dimension", default="strategic_importance"
        )
        aggregation_str = request.args.get("aggregation", default="mean")

        try:
            comparison_dimension = ComparisonDimension(comparison_dim_str)
        except ValueError:
            return (
                jsonify(
                    {
                        "error": f"Invalid comparison dimension: {comparison_dim_str}",
                        "valid_dimensions": [d.value for d in ComparisonDimension],
                    }
                ),
                400,
            )

        try:
            aggregation = AggregationMethod(aggregation_str)
        except ValueError:
            return (
                jsonify(
                    {
                        "error": f"Invalid aggregation method: {aggregation_str}",
                        "valid_methods": [m.value for m in AggregationMethod],
                    }
                ),
                400,
            )

        analyzer = get_analyzer()
        results_by_dim = analyzer.query_engine.compare_dimensions(
            comparison_dimension=comparison_dimension, aggregation=aggregation
        )

        return (
            jsonify(
                {
                    "comparison_dimension": comparison_dimension.value,
                    "aggregation_method": aggregation.value,
                    "dimensions": {
                        dim: {
                            "query_description": result.query_description,
                            "total_documents": result.total_documents,
                            "total_chunks_analyzed": result.total_chunks_analyzed,
                            "results": [
                                {
                                    "document_id": doc_id,
                                    "score": score,
                                    "metadata": metadata,
                                }
                                for doc_id, score, metadata in result.results
                            ],
                        }
                        for dim, result in results_by_dim.items()
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Dimension comparison failed: {e}", exc_info=True)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@cross_document_bp.route("/index-info", methods=["GET"])
def index_info():
    try:
        analyzer = get_analyzer()

        return (
            jsonify(
                {
                    "total_documents": len(analyzer.index.get_all_document_ids()),
                    "total_chunks": len(analyzer.index.chunks),
                    "policy_areas": sorted(list(analyzer.index.get_all_policy_areas())),
                    "dimensions": sorted(list(analyzer.index.get_all_dimensions())),
                    "document_ids": sorted(analyzer.index.get_all_document_ids()),
                    "index_hash": analyzer.index.compute_index_hash(),
                    "last_update": (
                        analyzer.index._last_update.isoformat()
                        if analyzer.index._last_update
                        else None
                    ),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Index info retrieval failed: {e}", exc_info=True)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

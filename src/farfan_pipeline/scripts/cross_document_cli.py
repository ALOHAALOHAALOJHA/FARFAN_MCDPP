"""
Cross-Document Comparative Analysis CLI

Command-line interface for multi-document comparative analysis operations.
Production-ready CLI with comprehensive functionality and reporting.
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from farfan_pipeline.analysis.cross_document_comparative import (
    AggregationMethod,
    ComparisonDimension,
    ComparisonOperator,
    CrossDocumentAnalyzer,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_canon_packages(package_paths: list[str]) -> list[any]:
    packages = []

    for path_str in package_paths:
        path = Path(path_str)
        if not path.exists():
            logger.warning(f"Package path does not exist: {path_str}")
            continue

        if path.is_file() and path.suffix == ".json":
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                packages.append(data)
                logger.info(f"Loaded package from {path_str}")
            except Exception as e:
                logger.error(f"Failed to load package from {path_str}: {e}")
        elif path.is_dir():
            for json_file in path.glob("*.json"):
                try:
                    with open(json_file, encoding="utf-8") as f:
                        data = json.load(f)
                    packages.append(data)
                    logger.info(f"Loaded package from {json_file}")
                except Exception as e:
                    logger.error(f"Failed to load package from {json_file}: {e}")

    return packages


def cmd_compare(args):
    analyzer = CrossDocumentAnalyzer()

    packages = load_canon_packages(args.packages)
    if not packages:
        logger.error("No packages loaded. Exiting.")
        return 1

    for pkg in packages:
        try:
            analyzer.add_document(pkg)
        except Exception as e:
            logger.error(f"Failed to add document: {e}")

    try:
        dimension = ComparisonDimension(args.dimension)
    except ValueError:
        logger.error(f"Invalid dimension: {args.dimension}")
        logger.error(f"Valid dimensions: {[d.value for d in ComparisonDimension]}")
        return 1

    try:
        aggregation = AggregationMethod(args.aggregation)
    except ValueError:
        logger.error(f"Invalid aggregation method: {args.aggregation}")
        logger.error(f"Valid methods: {[m.value for m in AggregationMethod]}")
        return 1

    policy_area_filter = args.policy_areas.split(",") if args.policy_areas else None
    dimension_filter = args.dimensions.split(",") if args.dimensions else None

    result = analyzer.query_engine.compare_by_dimension(
        dimension=dimension,
        aggregation=aggregation,
        policy_area_filter=policy_area_filter,
        dimension_filter=dimension_filter,
    )

    print(f"\n{'='*80}")
    print(f"Comparison Results: {result.query_description}")
    print(f"{'='*80}")
    print(f"Total Documents: {result.total_documents}")
    print(f"Total Chunks Analyzed: {result.total_chunks_analyzed}")
    print(f"Aggregation Method: {result.aggregation_method.value}")
    print(f"{'='*80}\n")

    for i, (doc_id, score, metadata) in enumerate(result.results, 1):
        print(f"{i}. {doc_id}")
        print(f"   Score: {score:.4f}")
        print(f"   Total Chunks: {metadata.get('total_chunks', 'N/A')}")
        print(f"   Policy Areas: {', '.join(metadata.get('policy_areas', []))}")
        print(f"   Dimensions: {', '.join(metadata.get('dimensions', []))}")
        if metadata.get("temporal_range"):
            print(f"   Temporal Range: {metadata['temporal_range']}")
        print()

    if args.output:
        analyzer.export_comparison_report(result, args.output)
        print(f"Report exported to: {args.output}")

    return 0


def cmd_top_strategic(args):
    analyzer = CrossDocumentAnalyzer()

    packages = load_canon_packages(args.packages)
    if not packages:
        logger.error("No packages loaded. Exiting.")
        return 1

    for pkg in packages:
        try:
            analyzer.add_document(pkg)
        except Exception as e:
            logger.error(f"Failed to add document: {e}")

    result = analyzer.find_pdts_with_highest_strategic_importance(n=args.top_n)

    print(f"\n{'='*80}")
    print(f"Top {args.top_n} Documents by Strategic Importance")
    print(f"{'='*80}")
    print(f"Total Documents Analyzed: {result.total_documents}")
    print(f"Total Chunks Analyzed: {result.total_chunks_analyzed}")
    print(f"{'='*80}\n")

    for i, (doc_id, score, metadata) in enumerate(result.results, 1):
        print(f"{i}. {doc_id}")
        print(f"   Strategic Importance Score: {score:.4f}")
        print(f"   Total Chunks: {metadata.get('total_chunks', 'N/A')}")
        print(f"   Policy Areas: {', '.join(metadata.get('policy_areas', []))}")
        print()

    if args.output:
        analyzer.export_comparison_report(result, args.output)
        print(f"Report exported to: {args.output}")

    return 0


def cmd_strongest_causal(args):
    analyzer = CrossDocumentAnalyzer()

    packages = load_canon_packages(args.packages)
    if not packages:
        logger.error("No packages loaded. Exiting.")
        return 1

    for pkg in packages:
        try:
            analyzer.add_document(pkg)
        except Exception as e:
            logger.error(f"Failed to add document: {e}")

    result = analyzer.identify_municipalities_with_strongest_causal_chains(
        n=args.top_n, min_chain_length=args.min_chain_length
    )

    print(f"\n{'='*80}")
    print(f"Top {args.top_n} Documents with Strongest Causal Chains")
    print(f"(Minimum Chain Length: {args.min_chain_length})")
    print(f"{'='*80}")
    print(f"Total Documents: {result.total_documents}")
    print(f"Total Chunks Analyzed: {result.total_chunks_analyzed}")
    print(f"{'='*80}\n")

    for i, (doc_id, score, metadata) in enumerate(result.results, 1):
        print(f"{i}. {doc_id}")
        print(f"   Causal Chain Strength: {score:.4f}")
        print(
            f"   Chunks with Causal Chains: {metadata.get('total_chunks_with_causal_chains', 'N/A')}"
        )
        print(f"   Avg Chain Length: {metadata.get('avg_chain_length', 'N/A'):.2f}")
        print(f"   Max Chain Length: {metadata.get('max_chain_length', 'N/A')}")
        print(f"   Policy Areas: {', '.join(metadata.get('policy_areas', []))}")
        print()

    if args.output:
        analyzer.export_comparison_report(result, args.output)
        print(f"Report exported to: {args.output}")

    return 0


def cmd_statistics(args):
    analyzer = CrossDocumentAnalyzer()

    packages = load_canon_packages(args.packages)
    if not packages:
        logger.error("No packages loaded. Exiting.")
        return 1

    for pkg in packages:
        try:
            analyzer.add_document(pkg)
        except Exception as e:
            logger.error(f"Failed to add document: {e}")

    try:
        dimension = ComparisonDimension(args.dimension)
    except ValueError:
        logger.error(f"Invalid dimension: {args.dimension}")
        logger.error(f"Valid dimensions: {[d.value for d in ComparisonDimension]}")
        return 1

    stats = analyzer.get_global_statistics(dimension)

    print(f"\n{'='*80}")
    print(f"Global Statistics for {dimension.value}")
    print(f"{'='*80}")
    print(f"Total Documents: {stats.total_documents}")
    print(f"Total Chunks: {stats.total_chunks}")
    print(f"{'='*80}\n")

    print("Global Statistics:")
    print(f"  Mean:   {stats.global_mean:.4f}")
    print(f"  Median: {stats.global_median:.4f}")
    print(f"  Std:    {stats.global_std:.4f}")
    print(f"  Min:    {stats.global_min:.4f}")
    print(f"  Max:    {stats.global_max:.4f}")
    print()

    if stats.per_document_stats:
        print("Per-Document Statistics:")
        for doc_id, doc_stats in sorted(stats.per_document_stats.items())[:10]:
            print(f"  {doc_id}:")
            print(
                f"    Mean: {doc_stats['mean']:.4f}, "
                f"Median: {doc_stats['median']:.4f}, "
                f"Count: {doc_stats['count']}"
            )
        if len(stats.per_document_stats) > 10:
            print(f"  ... and {len(stats.per_document_stats) - 10} more documents")
        print()

    if stats.per_policy_area_stats:
        print("Per-Policy-Area Statistics:")
        for pa, pa_stats in sorted(stats.per_policy_area_stats.items()):
            print(f"  {pa}:")
            print(
                f"    Mean: {pa_stats['mean']:.4f}, "
                f"Median: {pa_stats['median']:.4f}, "
                f"Count: {pa_stats['count']}"
            )
        print()

    if stats.per_dimension_stats:
        print("Per-Dimension Statistics:")
        for dim, dim_stats in sorted(stats.per_dimension_stats.items()):
            print(f"  {dim}:")
            print(
                f"    Mean: {dim_stats['mean']:.4f}, "
                f"Median: {dim_stats['median']:.4f}, "
                f"Count: {dim_stats['count']}"
            )
        print()

    if args.output:
        analyzer.export_statistics_report(stats, args.output)
        print(f"Statistics report exported to: {args.output}")

    return 0


def cmd_threshold(args):
    analyzer = CrossDocumentAnalyzer()

    packages = load_canon_packages(args.packages)
    if not packages:
        logger.error("No packages loaded. Exiting.")
        return 1

    for pkg in packages:
        try:
            analyzer.add_document(pkg)
        except Exception as e:
            logger.error(f"Failed to add document: {e}")

    try:
        dimension = ComparisonDimension(args.dimension)
    except ValueError:
        logger.error(f"Invalid dimension: {args.dimension}")
        logger.error(f"Valid dimensions: {[d.value for d in ComparisonDimension]}")
        return 1

    try:
        operator = ComparisonOperator(args.operator)
    except ValueError:
        logger.error(f"Invalid operator: {args.operator}")
        logger.error(f"Valid operators: {[o.value for o in ComparisonOperator]}")
        return 1

    try:
        aggregation = AggregationMethod(args.aggregation)
    except ValueError:
        logger.error(f"Invalid aggregation method: {args.aggregation}")
        logger.error(f"Valid methods: {[m.value for m in AggregationMethod]}")
        return 1

    result = analyzer.query_engine.find_documents_by_threshold(
        dimension=dimension,
        operator=operator,
        threshold=args.threshold,
        aggregation=aggregation,
    )

    print(f"\n{'='*80}")
    print(f"Threshold Query Results: {result.query_description}")
    print(f"{'='*80}")
    print(f"Total Documents Matching: {result.total_documents}")
    print(f"Total Chunks Analyzed: {result.total_chunks_analyzed}")
    print(f"{'='*80}\n")

    for i, (doc_id, score, metadata) in enumerate(result.results, 1):
        print(f"{i}. {doc_id}")
        print(f"   Score: {score:.4f}")
        print(f"   Total Chunks: {metadata.get('total_chunks', 'N/A')}")
        print()

    if args.output:
        analyzer.export_comparison_report(result, args.output)
        print(f"Report exported to: {args.output}")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Cross-Document Comparative Analysis CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    compare_parser = subparsers.add_parser(
        "compare", help="Compare documents by dimension"
    )
    compare_parser.add_argument(
        "packages",
        nargs="+",
        help="Paths to CanonPolicyPackage JSON files or directories",
    )
    compare_parser.add_argument(
        "--dimension", required=True, help="Comparison dimension"
    )
    compare_parser.add_argument(
        "--aggregation", default="mean", help="Aggregation method"
    )
    compare_parser.add_argument(
        "--policy-areas", help="Comma-separated list of policy areas to filter"
    )
    compare_parser.add_argument(
        "--dimensions", help="Comma-separated list of dimensions to filter"
    )
    compare_parser.add_argument("--output", help="Output JSON file path")
    compare_parser.set_defaults(func=cmd_compare)

    strategic_parser = subparsers.add_parser(
        "top-strategic", help="Find documents with highest strategic importance"
    )
    strategic_parser.add_argument(
        "packages",
        nargs="+",
        help="Paths to CanonPolicyPackage JSON files or directories",
    )
    strategic_parser.add_argument(
        "--top-n", type=int, default=10, help="Number of top results"
    )
    strategic_parser.add_argument("--output", help="Output JSON file path")
    strategic_parser.set_defaults(func=cmd_top_strategic)

    causal_parser = subparsers.add_parser(
        "strongest-causal", help="Find documents with strongest causal chains"
    )
    causal_parser.add_argument(
        "packages",
        nargs="+",
        help="Paths to CanonPolicyPackage JSON files or directories",
    )
    causal_parser.add_argument(
        "--top-n", type=int, default=10, help="Number of top results"
    )
    causal_parser.add_argument(
        "--min-chain-length", type=int, default=3, help="Minimum causal chain length"
    )
    causal_parser.add_argument("--output", help="Output JSON file path")
    causal_parser.set_defaults(func=cmd_strongest_causal)

    stats_parser = subparsers.add_parser("statistics", help="Compute global statistics")
    stats_parser.add_argument(
        "packages",
        nargs="+",
        help="Paths to CanonPolicyPackage JSON files or directories",
    )
    stats_parser.add_argument(
        "--dimension", required=True, help="Dimension to compute statistics for"
    )
    stats_parser.add_argument("--output", help="Output JSON file path")
    stats_parser.set_defaults(func=cmd_statistics)

    threshold_parser = subparsers.add_parser(
        "threshold", help="Find documents by threshold"
    )
    threshold_parser.add_argument(
        "packages",
        nargs="+",
        help="Paths to CanonPolicyPackage JSON files or directories",
    )
    threshold_parser.add_argument(
        "--dimension", required=True, help="Comparison dimension"
    )
    threshold_parser.add_argument(
        "--operator",
        required=True,
        help="Comparison operator (gt, gte, lt, lte, eq, neq)",
    )
    threshold_parser.add_argument(
        "--threshold", type=float, required=True, help="Threshold value"
    )
    threshold_parser.add_argument(
        "--aggregation", default="mean", help="Aggregation method"
    )
    threshold_parser.add_argument("--output", help="Output JSON file path")
    threshold_parser.set_defaults(func=cmd_threshold)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        return args.func(args)
    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

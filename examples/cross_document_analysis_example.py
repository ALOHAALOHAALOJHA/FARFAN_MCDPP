"""
Cross-Document Comparative Analysis - Usage Examples

Demonstrates various use cases for the cross-document comparative analysis framework.
"""

import json
from pathlib import Path

from farfan_pipeline.analysis.cross_document_comparative import (
    AggregationMethod,
    ComparisonDimension,
    ComparisonOperator,
    CrossDocumentAnalyzer,
)
from farfan_pipeline.analysis.cross_document_integration import (
    CrossDocumentPipeline,
    SPCEnricher,
)


def example_1_basic_comparison():
    print("=" * 80)
    print("Example 1: Basic Document Comparison by Strategic Importance")
    print("=" * 80)
    
    analyzer = CrossDocumentAnalyzer()
    
    print("\nStep 1: Load and index CanonPolicyPackages...")
    print("(In production, load actual packages from SPC pipeline)")
    
    print("\nStep 2: Find top 10 PDTs with highest strategic importance")
    result = analyzer.find_pdts_with_highest_strategic_importance(n=10)
    
    print(f"\nResults:")
    print(f"Total Documents Analyzed: {result.total_documents}")
    print(f"Total Chunks Analyzed: {result.total_chunks_analyzed}")
    print(f"\nTop Documents:")
    for i, (doc_id, score, metadata) in enumerate(result.results[:5], 1):
        print(f"{i}. {doc_id}")
        print(f"   Strategic Importance Score: {score:.4f}")
        print(f"   Total Chunks: {metadata.get('total_chunks', 'N/A')}")
        print(f"   Policy Areas: {', '.join(metadata.get('policy_areas', []))}")


def example_2_causal_chain_analysis():
    print("\n" + "=" * 80)
    print("Example 2: Identify Municipalities with Strongest Causal Chains")
    print("=" * 80)
    
    analyzer = CrossDocumentAnalyzer()
    
    print("\nFinding municipalities with strongest causal reasoning...")
    result = analyzer.identify_municipalities_with_strongest_causal_chains(
        n=10,
        min_chain_length=3
    )
    
    print(f"\nResults:")
    print(f"Total Documents with Strong Causal Chains: {result.total_documents}")
    print(f"Total Chunks Analyzed: {result.total_chunks_analyzed}")
    print(f"\nTop Municipalities:")
    for i, (doc_id, strength, metadata) in enumerate(result.results[:5], 1):
        print(f"{i}. {doc_id}")
        print(f"   Causal Chain Strength: {strength:.4f}")
        print(f"   Avg Chain Length: {metadata.get('avg_chain_length', 'N/A'):.2f}")
        print(f"   Max Chain Length: {metadata.get('max_chain_length', 'N/A')}")


def example_3_multi_dimension_comparison():
    print("\n" + "=" * 80)
    print("Example 3: Multi-Dimensional Document Comparison")
    print("=" * 80)
    
    analyzer = CrossDocumentAnalyzer()
    
    dimensions = [
        (ComparisonDimension.SEMANTIC_DENSITY, "Semantic Density"),
        (ComparisonDimension.COHERENCE_SCORE, "Coherence Score"),
        (ComparisonDimension.COMPLETENESS_INDEX, "Completeness Index"),
    ]
    
    for dimension, name in dimensions:
        print(f"\n{name} Comparison:")
        result = analyzer.query_engine.compare_by_dimension(
            dimension=dimension,
            aggregation=AggregationMethod.MEAN
        )
        
        print(f"  Documents Analyzed: {result.total_documents}")
        if result.results:
            top_doc = result.results[0]
            print(f"  Top Document: {top_doc[0]} (Score: {top_doc[1]:.4f})")


def main():
    print("\n" + "=" * 80)
    print("Cross-Document Comparative Analysis - Usage Examples")
    print("=" * 80)
    
    print("\nNote: These examples demonstrate API usage.")
    print("In production, replace mock data with actual CanonPolicyPackage instances.")
    
    print("\n" + "=" * 80)
    print("Running example demonstrations...")
    print("=" * 80)
    
    examples = [
        ("Basic Comparison", example_1_basic_comparison),
        ("Causal Chain Analysis", example_2_causal_chain_analysis),
        ("Multi-Dimensional Comparison", example_3_multi_dimension_comparison),
    ]
    
    for name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\nExample '{name}' requires actual data to run: {e}")
    
    print("\n" + "=" * 80)
    print("Examples complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()

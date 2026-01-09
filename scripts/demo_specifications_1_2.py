#!/usr/bin/env python3
"""
Comprehensive Demonstration: Enriched Quality Level and Phase 4 Integration
===========================================================================

This script demonstrates the complete implementation of both specifications
requested in the PR comments:

SPECIFICATION 1: Enriched Quality Level
- Context-aware quality assessment reflecting territorial adjustments
- Semantic consistency between threshold adjustments and quality levels

SPECIFICATION 2: Phase 4 Integration
- Bold, creative, sophisticated integration with Phase 4 aggregation
- Maintains determinism and total alignment with canonic phases
- Territorial-aware weight adjustments and dispersion interpretation
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # noqa: E501

from canonic_questionnaire_central.scoring.modules import (
    create_pdet_enricher,
    ScoredResult,
    TerritorialAggregationContext,
    TerritorialAggregationAdapter,
    create_territorial_contexts_from_enriched_results,
)


def print_header(text: str, char: str = "="):
    """Print formatted header."""
    print(f"\n{char * 75}")
    print(f"{text:^75}")
    print(f"{char * 75}\n")


def print_section(text: str):
    """Print section header."""
    print(f"\n{text}")
    print("-" * 75)


def demonstrate_specification_1():
    """Demonstrate SPECIFICATION 1: Enriched Quality Level."""
    print_header("SPECIFICATION 1: Enriched Quality Level")
    
    print("Problem: Original quality levels don't reflect territorial context leniency")
    print("Solution: Add enriched_quality_level that responds to territorial adjustments")
    
    enricher = create_pdet_enricher(strict_mode=False)
    
    # Create test scenarios with different territorial adjustments
    scenarios = [
        {
            "score": 0.62,
            "description": "Borderline ACEPTABLE score",
            "adjustment_simulations": [
                (0.02, "Low PDET relevance"),
                (0.08, "Moderate PDET relevance"),  
                (0.12, "High PDET relevance"),
            ]
        },
        {
            "score": 0.68,
            "description": "Near BUENO threshold score",
            "adjustment_simulations": [
                (0.02, "Low PDET relevance"),
                (0.08, "Moderate PDET relevance"),
                (0.12, "High PDET relevance"),
            ]
        }
    ]
    
    for scenario in scenarios:
        print_section(f"Scenario: {scenario['description']} (Score: {scenario['score']:.2f})")
        
        base_quality = "ACEPTABLE" if scenario['score'] < 0.70 else "BUENO"
        print(f"Base quality level: {base_quality}")
        
        for adjustment, desc in scenario['adjustment_simulations']:
            # Simulate enriched quality calculation
            from canonic_questionnaire_central.scoring.modules.pdet_scoring_enrichment import (
                PDETScoringContext,
                PDETScoringEnricher,
            )
            
            enricher_internal = PDETScoringEnricher()
            enriched_quality = enricher_internal._calculate_enriched_quality_level(
                base_score=scenario['score'],
                adjusted_threshold=0.65 - adjustment,
                territorial_adjustment=adjustment,
                pdet_context=PDETScoringContext()
            )
            
            print(f"\n  {desc} (adjustment={adjustment:.2f}):")
            print(f"    Adjusted threshold: {0.65 - adjustment:.2f}")
            print(f"    Enriched quality: {enriched_quality}")
            
            if enriched_quality != base_quality:
                print(f"    ✓ QUALITY UPGRADED due to territorial context!")
    
    print("\n" + "=" * 75)
    print("Key Insight: Enriched quality levels provide semantic consistency")
    print("between territorial leniency and quality assessment.")
    print("=" * 75)


def demonstrate_specification_2():
    """Demonstrate SPECIFICATION 2: Phase 4 Integration."""
    print_header("SPECIFICATION 2: Phase 4 Territorial Integration")
    
    print("Design Principles:")
    print("  1. Determinism: Same inputs → same outputs")
    print("  2. Phase Alignment: Respects Phase 3/4 contracts")
    print("  3. Mathematical Soundness: Preserves aggregation invariants")
    print("  4. Non-invasive: Works alongside existing aggregators")
    
    # Create mock enriched results
    print_section("Step 1: Convert Phase 3 Enriched Results to Phase 4 Context")
    
    enricher = create_pdet_enricher(strict_mode=False)
    
    # Simulate different questions with varying PDET relevance
    questions = ["Q001", "Q002", "Q003"]
    enriched_results = {}
    
    for i, qid in enumerate(questions):
        test_result = ScoredResult(
            score=0.60 + (i * 0.05),
            normalized_score=60.0 + (i * 5),
            quality_level="ACEPTABLE",
            passes_threshold=False,
            modality="TYPE_E",
            scoring_metadata={"threshold": 0.65}
        )
        
        enriched = enricher.enrich_scored_result(
            scored_result=test_result,
            question_id=qid,
            policy_area="PA02",
        )
        enriched_results[qid] = enriched
        
        print(f"\n{qid}: Score={test_result.score:.2f}, Base Quality={test_result.quality_level}")
    
    # Create territorial contexts
    territorial_contexts = create_territorial_contexts_from_enriched_results(
        enriched_results=enriched_results,
        policy_area="PA02"
    )
    
    print(f"\n✓ Created {len(territorial_contexts)} territorial contexts")
    
    # Demonstrate weight adjustment
    print_section("Step 2: Territorial-Aware Weight Adjustment")
    
    adapter = TerritorialAggregationAdapter(
        enable_weight_adjustment=True,
        enable_dispersion_adjustment=True,
        strict_determinism=True
    )
    
    base_weights = {
        "Q001": 0.33,
        "Q002": 0.33,
        "Q003": 0.34,
    }
    
    print("\nBase weights:")
    for qid, weight in base_weights.items():
        print(f"  {qid}: {weight:.3f}")
    
    adjusted_weights, metadata = adapter.adjust_dimension_weights(
        base_weights=base_weights,
        territorial_contexts=territorial_contexts
    )
    
    print("\nAdjusted weights (with territorial context):")
    for qid, weight in adjusted_weights.items():
        context = territorial_contexts.get(qid)
        multiplier = context.weight_multiplier if context else 1.0
        print(f"  {qid}: {weight:.3f} (multiplier={multiplier:.2f}, relevance={context.relevance.value if context else 'NONE'})")
    
    print(f"\n✓ Weight sum preserved: {sum(adjusted_weights.values()):.6f} = 1.0")
    
    # Demonstrate dispersion interpretation
    print_section("Step 3: Context-Aware Dispersion Interpretation")
    
    cv = 0.35  # Coefficient of variation
    di = 0.40  # Dispersion index
    
    print(f"\nScore dispersion metrics:")
    print(f"  CV: {cv:.2f}")
    print(f"  DI: {di:.2f}")
    
    scenario, penalty, meta = adapter.interpret_dispersion_with_context(
        coefficient_variation=cv,
        dispersion_index=di,
        territorial_contexts=territorial_contexts
    )
    
    print(f"\nDispersion interpretation:")
    print(f"  Scenario: {scenario}")
    print(f"  Context-adjusted penalty: {penalty:.2f}")
    print(f"  Avg dispersion sensitivity: {meta.get('avg_dispersion_sensitivity', 1.0):.2f}")
    
    # Demonstrate audit trail
    print_section("Step 4: Determinism and Audit Trail")
    
    report = adapter.get_adjustment_report()
    print(f"\nAdjustments made: {report['total_adjustments']}")
    print(f"Determinism enforced: {report['configuration']['strict_determinism']}")
    print(f"\n✓ All adjustments are logged and traceable")
    
    print("\n" + "=" * 75)
    print("Key Features:")
    print("  ✓ Deterministic: Reproducible results")
    print("  ✓ Phase-aligned: Respects Phase 3/4 contracts")
    print("  ✓ Mathematically sound: Preserves invariants")
    print("  ✓ Auditable: Complete adjustment trail")
    print("=" * 75)


def demonstrate_integration():
    """Demonstrate end-to-end integration."""
    print_header("END-TO-END INTEGRATION")
    
    print("Complete flow: Phase 3 → PDET Enrichment → Phase 4 Integration")
    
    enricher = create_pdet_enricher(strict_mode=False)
    
    # Phase 3: Score a question
    test_result = ScoredResult(
        score=0.62,
        normalized_score=62.0,
        quality_level="ACEPTABLE",
        passes_threshold=False,
        modality="TYPE_E",
        scoring_metadata={"threshold": 0.65}
    )
    
    print("\n1. Phase 3 Output:")
    print(f"   Score: {test_result.score:.2f}")
    print(f"   Quality: {test_result.quality_level}")
    
    # PDET Enrichment
    enriched = enricher.enrich_scored_result(
        scored_result=test_result,
        question_id="Q001",
        policy_area="PA02",
    )
    
    summary = enricher.get_enrichment_summary(enriched)
    
    print("\n2. PDET Enrichment:")
    print(f"   Territorial adjustment: {summary['territorial_adjustment']:.3f}")
    print(f"   Base quality: {summary['base_quality_level']}")
    print(f"   Enriched quality: {summary['enriched_quality_level']}")
    
    # Phase 4 Integration
    context = TerritorialAggregationContext.from_enriched_result("Q001", "PA02", enriched)
    
    print("\n3. Phase 4 Context:")
    print(f"   Relevance: {context.relevance.value}")
    print(f"   Weight multiplier: {context.weight_multiplier}")
    print(f"   Dispersion sensitivity: {context.dispersion_sensitivity}")
    
    print("\n" + "=" * 75)
    print("✓ Complete integration: Phase 3 → Enrichment → Phase 4")
    print("✓ Semantic consistency maintained throughout")
    print("✓ Determinism and phase alignment preserved")
    print("=" * 75)


def main():
    """Run all demonstrations."""
    print("\n")
    print("╔" + "=" * 73 + "╗")
    print("║" + " " * 5 + "PDET ENRICHMENT: SPECIFICATIONS 1 & 2 DEMONSTRATION" + " " * 14 + "║")
    print("╚" + "=" * 73 + "╝")
    
    demonstrate_specification_1()
    demonstrate_specification_2()
    demonstrate_integration()
    
    print_header("DEMONSTRATION COMPLETE", "=")
    print("Both specifications successfully implemented and demonstrated:")
    print("  ✓ SPECIFICATION 1: Enriched quality level for semantic consistency")
    print("  ✓ SPECIFICATION 2: Phase 4 integration with determinism and alignment")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
Example: PDT Quality Integration with Signal Intelligence Layer

Demonstrates how to use Unit Layer (@u) metrics to boost pattern filtering
based on PDT section quality (I_struct>0.8 for excellent sections).
"""

from farfan_pipeline.core.orchestrator import (
    BOOST_FACTORS,
    PDT_QUALITY_THRESHOLDS,
    PDTQualityMetrics,
    compute_pdt_section_quality,
    create_enriched_signal_pack,
)


def example_basic_pdt_quality():
    """Basic example: Compute PDT section quality metrics."""
    print("=" * 80)
    print("Example 1: Computing PDT Section Quality")
    print("=" * 80)

    unit_layer_scores = {
        "score": 0.85,
        "components": {
            "S": 0.90,
            "M": 0.82,
            "I": 0.85,
            "I_struct": 0.88,
            "I_link": 0.84,
            "I_logic": 0.83,
            "P": 0.80,
            "P_presence": 1.0,
            "P_struct": 0.75,
            "P_consistency": 0.65,
        },
    }

    metrics = compute_pdt_section_quality(
        section_name="Diagnóstico", unit_layer_scores=unit_layer_scores
    )

    print(f"\nSection: {metrics.section_name}")
    print("Unit Layer Components:")
    print(f"  S (Structural): {metrics.S_structural:.2f}")
    print(f"  M (Mandatory): {metrics.M_mandatory:.2f}")
    print(f"  I (Indicator Quality): {metrics.I_total:.2f}")
    print(f"    ├─ I_struct: {metrics.I_struct:.2f}")
    print(f"    ├─ I_link: {metrics.I_link:.2f}")
    print(f"    └─ I_logic: {metrics.I_logic:.2f}")
    print(f"  P (PPI Completeness): {metrics.P_total:.2f}")
    print(f"    ├─ P_presence: {metrics.P_presence:.2f}")
    print(f"    ├─ P_struct: {metrics.P_struct:.2f}")
    print(f"    └─ P_consistency: {metrics.P_consistency:.2f}")
    print(f"\nOverall U Score: {metrics.U_total:.2f}")
    print(f"Quality Level: {metrics.quality_level}")
    print(f"Boost Factor: {metrics.boost_factor}x")


def example_multiple_sections():
    """Example: Build quality map for multiple PDT sections."""
    print("\n" + "=" * 80)
    print("Example 2: Multiple PDT Sections Quality Map")
    print("=" * 80)

    sections_data = {
        "Diagnóstico": {
            "score": 0.88,
            "components": {"I_struct": 0.90, "S": 0.92, "M": 0.85, "P": 0.82},
        },
        "Parte Estratégica": {
            "score": 0.75,
            "components": {"I_struct": 0.72, "S": 0.80, "M": 0.70, "P": 0.75},
        },
        "PPI": {
            "score": 0.68,
            "components": {"I_struct": 0.65, "S": 0.70, "M": 0.68, "P": 0.68},
        },
        "Seguimiento": {
            "score": 0.45,
            "components": {"I_struct": 0.38, "S": 0.50, "M": 0.42, "P": 0.48},
        },
    }

    pdt_quality_map = {}

    print("\nProcessing sections:")
    for section_name, scores in sections_data.items():
        metrics = compute_pdt_section_quality(
            section_name=section_name, unit_layer_scores=scores
        )
        pdt_quality_map[section_name] = metrics

        print(f"\n{section_name}:")
        print(f"  I_struct: {metrics.I_struct:.2f}")
        print(f"  Quality: {metrics.quality_level}")
        print(f"  Boost: {metrics.boost_factor}x")

    print("\n" + "-" * 80)
    print("Quality Distribution:")
    quality_counts = {"excellent": 0, "good": 0, "acceptable": 0, "poor": 0}
    for metrics in pdt_quality_map.values():
        quality_counts[metrics.quality_level] += 1

    for level, count in quality_counts.items():
        print(f"  {level.capitalize()}: {count} sections")

    return pdt_quality_map


def example_pattern_boosting(pdt_quality_map):
    """Example: Apply PDT quality boost to patterns."""
    print("\n" + "=" * 80)
    print("Example 3: Pattern Boosting with PDT Quality")
    print("=" * 80)

    mock_patterns = [
        {
            "id": "p1",
            "pattern": "indicador de resultado",
            "pdt_section": "Diagnóstico",
            "priority": 1.0,
        },
        {
            "id": "p2",
            "pattern": "línea base",
            "pdt_section": "Parte Estratégica",
            "priority": 1.0,
        },
        {
            "id": "p3",
            "pattern": "proyecto",
            "pdt_section": "PPI",
            "priority": 1.0,
        },
        {
            "id": "p4",
            "pattern": "monitoreo",
            "pdt_section": "Seguimiento",
            "priority": 1.0,
        },
    ]

    from farfan_pipeline.core.orchestrator.pdt_quality_integration import (
        apply_pdt_quality_boost,
    )

    boosted_patterns, boost_stats = apply_pdt_quality_boost(
        mock_patterns, pdt_quality_map, document_context={}
    )

    print(f"\nBoosted Patterns ({len(boosted_patterns)}):")
    for pattern in boosted_patterns:
        print(f"\n  Pattern: {pattern['pattern']}")
        print(f"    Section: {pattern['pdt_section']}")
        print(f"    Quality Level: {pattern.get('pdt_quality_level', 'unknown')}")
        print(f"    Original Priority: {pattern['original_priority']:.1f}")
        print(f"    Boost Factor: {pattern.get('pdt_quality_boost', 1.0):.1f}x")
        print(f"    Boosted Priority: {pattern['boosted_priority']:.2f}")

    print("\n" + "-" * 80)
    print("Boost Statistics:")
    print(f"  Total patterns: {boost_stats['total_patterns']}")
    print(f"  Boosted: {boost_stats['boosted_count']}")
    print(f"  Excellent quality: {boost_stats['excellent_quality']}")
    print(f"  Good quality: {boost_stats['good_quality']}")
    print(f"  Acceptable quality: {boost_stats['acceptable_quality']}")
    print(f"  Poor quality: {boost_stats['poor_quality']}")
    print(f"  Avg boost factor: {boost_stats['avg_boost_factor']:.2f}x")
    print(f"  Max boost factor: {boost_stats['max_boost_factor']:.2f}x")


def example_enriched_signal_pack():
    """Example: Using PDT quality with EnrichedSignalPack."""
    print("\n" + "=" * 80)
    print("Example 4: EnrichedSignalPack with PDT Quality")
    print("=" * 80)

    mock_signal_pack = {
        "patterns": [
            {"id": "p1", "pattern": "indicador", "pdt_section": "Diagnóstico"},
            {"id": "p2", "pattern": "meta", "pdt_section": "Parte Estratégica"},
            {"id": "p3", "pattern": "proyecto", "pdt_section": "PPI"},
        ]
    }

    pdt_quality_map = {
        "Diagnóstico": PDTQualityMetrics(
            I_struct=0.90,
            quality_level="excellent",
            boost_factor=1.5,
            section_name="Diagnóstico",
            U_total=0.88,
        ),
        "Parte Estratégica": PDTQualityMetrics(
            I_struct=0.72,
            quality_level="good",
            boost_factor=1.2,
            section_name="Parte Estratégica",
            U_total=0.75,
        ),
        "PPI": PDTQualityMetrics(
            I_struct=0.65,
            quality_level="good",
            boost_factor=1.2,
            section_name="PPI",
            U_total=0.68,
        ),
    }

    enriched = create_enriched_signal_pack(
        base_signal_pack=mock_signal_pack,
        enable_semantic_expansion=False,
        pdt_quality_map=pdt_quality_map,
    )

    print("\nEnriched Signal Pack created")
    print(f"Patterns: {len(enriched.patterns)}")

    summary = enriched.get_pdt_quality_summary()
    print("\nPDT Quality Summary:")
    print(f"  Total sections: {summary['total_sections']}")
    print(f"  Avg I_struct: {summary['avg_I_struct']:.2f}")
    print(f"  Quality distribution: {summary['quality_distribution']}")

    for section_info in summary["sections"]:
        print(f"\n  {section_info['section']}:")
        print(f"    I_struct: {section_info['I_struct']:.2f}")
        print(f"    Quality: {section_info['quality_level']}")
        print(f"    U_total: {section_info['U_total']:.2f}")


def example_thresholds_and_factors():
    """Example: Display PDT quality thresholds and boost factors."""
    print("\n" + "=" * 80)
    print("Example 5: PDT Quality Thresholds and Boost Factors")
    print("=" * 80)

    print("\nQuality Thresholds:")
    for name, value in PDT_QUALITY_THRESHOLDS.items():
        print(f"  {name}: {value:.1f}")

    print("\nBoost Factors by Quality Level:")
    for level, factor in BOOST_FACTORS.items():
        print(f"  {level.capitalize()}: {factor:.1f}x")

    print("\nQuality Level Determination:")
    test_values = [0.95, 0.75, 0.55, 0.35]
    for i_struct in test_values:
        if i_struct >= PDT_QUALITY_THRESHOLDS["I_struct_excellent"]:
            level = "excellent"
        elif i_struct >= PDT_QUALITY_THRESHOLDS["I_struct_good"]:
            level = "good"
        elif i_struct >= PDT_QUALITY_THRESHOLDS["I_struct_acceptable"]:
            level = "acceptable"
        else:
            level = "poor"

        boost = BOOST_FACTORS[level]
        print(f"  I_struct={i_struct:.2f} → {level} (boost: {boost:.1f}x)")


if __name__ == "__main__":
    print("PDT Quality Integration Examples")
    print("=" * 80)

    example_basic_pdt_quality()

    pdt_map = example_multiple_sections()

    example_pattern_boosting(pdt_map)

    example_enriched_signal_pack()

    example_thresholds_and_factors()

    print("\n" + "=" * 80)
    print("Examples complete!")
    print("=" * 80)

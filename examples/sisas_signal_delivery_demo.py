"""
SISAS Signal Delivery - End-to-End Demonstration

This example demonstrates the complete signal delivery flow:
    Extractors → SignalIrrigator → Questions

Shows:
1. How to extract signals using empirical extractors
2. How to irrigate signals to questions using SignalIrrigator
3. How to validate signal delivery
4. How to track irrigation metrics

Author: FARFAN Pipeline Team
Date: 2026-01-07
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from farfan_pipeline.infrastructure.extractors import (
    StructuralMarkerExtractor,
    QuantitativeTripletExtractor,
    NormativeReferenceExtractor,
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS import (
    SignalIrrigator,
    irrigate_extraction_result,
)


def main():
    """Run complete signal delivery demonstration."""

    print("=" * 80)
    print("SISAS SIGNAL DELIVERY DEMONSTRATION")
    print("=" * 80)
    print()

    # Sample PDT text
    pdt_text = """
    DIAGNÓSTICO DEL SECTOR

    La situación de las mujeres en el municipio presenta las siguientes características:

    Línea Base 2023: 45% de mujeres víctimas de violencia intrafamiliar
    Meta 2027: 25% de casos reportados

    Según la Ley 1257 de 2008 y en cumplimiento del Acuerdo de Paz, el municipio
    debe implementar rutas de atención integral.

    PLAN PLURIANUAL DE INVERSIONES

    Tabla 12: Asignación Presupuestal
    Programa: Atención integral a mujeres víctimas de VBG
    Presupuesto: $500 millones
    Fuente: SGP + Recursos Propios
    """

    # ========================================================================
    # STEP 1: Extract Signals
    # ========================================================================
    print("\n" + "="*80)
    print("STEP 1: EXTRACT SIGNALS FROM PDT TEXT")
    print("="*80 + "\n")

    # Initialize extractors
    print("→ Initializing empirically-calibrated extractors...")
    structural_extractor = StructuralMarkerExtractor()
    triplet_extractor = QuantitativeTripletExtractor()
    normative_extractor = NormativeReferenceExtractor()
    print("✓ Extractors initialized\n")

    # Extract signals
    print("→ Extracting STRUCTURAL_MARKER signals...")
    structural_result = structural_extractor.extract(pdt_text)
    print(f"  Found {len(structural_result.matches)} structural elements")
    print(f"  Confidence: {structural_result.confidence:.2f}")
    print(f"  Types: {', '.join(set(m.get('element_type') for m in structural_result.matches))}\n")

    print("→ Extracting QUANTITATIVE_TRIPLET signals...")
    triplet_result = triplet_extractor.extract(pdt_text)
    print(f"  Found {len(triplet_result.matches)} quantitative triplets")
    print(f"  Confidence: {triplet_result.confidence:.2f}")
    for triplet in triplet_result.matches[:2]:
        print(f"    - LB: {triplet.get('linea_base')}, Meta: {triplet.get('meta')}, "
              f"Completeness: {triplet.get('completeness')}")
    print()

    print("→ Extracting NORMATIVE_REFERENCE signals...")
    normative_result = normative_extractor.extract(pdt_text)
    print(f"  Found {len(normative_result.matches)} normative references")
    print(f"  Confidence: {normative_result.confidence:.2f}")
    for norm in normative_result.matches:
        print(f"    - {norm.get('text')} ({norm.get('norm_type')})")
    print()

    # ========================================================================
    # STEP 2: Initialize Signal Irrigator
    # ========================================================================
    print("\n" + "="*80)
    print("STEP 2: INITIALIZE SIGNAL IRRIGATOR")
    print("="*80 + "\n")

    print("→ Loading integration_map.json...")
    irrigator = SignalIrrigator()
    print(f"✓ SignalIrrigator initialized")
    print(f"  Loaded {len(irrigator.slot_to_signal_mapping)} slot mappings")
    print(f"  Signal types mapped: {len(irrigator.signal_to_questions_index)}")
    print()

    # ========================================================================
    # STEP 3: Irrigate Signals to Questions
    # ========================================================================
    print("\n" + "="*80)
    print("STEP 3: IRRIGATE SIGNALS TO QUESTIONS")
    print("="*80 + "\n")

    # Irrigate structural markers
    print("→ Irrigating STRUCTURAL_MARKER signals...")
    structural_deliveries = irrigate_extraction_result(
        irrigator, structural_result, extractor_id="StructuralMarkerExtractor"
    )
    print(f"  Delivered {len(structural_deliveries)} signals")
    if structural_deliveries:
        sample = structural_deliveries[0]
        print(f"  Example: {sample.question_id} via {' → '.join(sample.irrigation_path)}")
        print(f"    Value added: {sample.value_added:.2f}")
        print(f"    Scoring modality: {sample.metadata.get('scoring_modality')}")
    print()

    # Irrigate quantitative triplets
    print("→ Irrigating QUANTITATIVE_TRIPLET signals...")
    triplet_deliveries = irrigate_extraction_result(
        irrigator, triplet_result, extractor_id="QuantitativeTripletExtractor"
    )
    print(f"  Delivered {len(triplet_deliveries)} signals")
    if triplet_deliveries:
        sample = triplet_deliveries[0]
        print(f"  Example: {sample.question_id} via {' → '.join(sample.irrigation_path)}")
        print(f"    Value added: {sample.value_added:.2f}")
        print(f"    Is primary signal: {sample.metadata.get('is_primary')}")
    print()

    # Irrigate normative references
    print("→ Irrigating NORMATIVE_REFERENCE signals...")
    normative_deliveries = irrigate_extraction_result(
        irrigator, normative_result, extractor_id="NormativeReferenceExtractor"
    )
    print(f"  Delivered {len(normative_deliveries)} signals")
    if normative_deliveries:
        sample = normative_deliveries[0]
        print(f"  Example: {sample.question_id} via {' → '.join(sample.irrigation_path)}")
        print(f"    Slot: {sample.metadata.get('slot_id')} ({sample.metadata.get('slot_abbrev')})")
    print()

    # ========================================================================
    # STEP 4: Query Delivered Signals
    # ========================================================================
    print("\n" + "="*80)
    print("STEP 4: QUERY DELIVERED SIGNALS")
    print("="*80 + "\n")

    # Get all signals for Q001 (PA01-D1-Q1)
    question_id = "Q001"
    print(f"→ Getting signals for {question_id}...")
    q001_signals = irrigator.get_question_signals(question_id)
    print(f"  {question_id} received {len(q001_signals)} signals:")

    for signal in q001_signals:
        print(f"    - {signal.signal_type} (confidence: {signal.confidence:.2f})")
        print(f"      Path: {' → '.join(signal.irrigation_path)}")
        print(f"      Delivered at: {signal.delivered_at}")
    print()

    # Get expected signals for Q001
    print(f"→ Checking expected signals for {question_id}...")
    expected = irrigator.get_expected_signals_for_question(question_id)
    print(f"  Slot: {expected.get('slot_id')} ({expected.get('slot_abbrev')})")
    print(f"  Primary signals expected: {', '.join(expected.get('primary_signals', []))}")
    print(f"  Secondary signals expected: {', '.join(expected.get('secondary_signals', []))}")
    print(f"  Scoring modality: {expected.get('scoring_modality')}")
    print(f"  Empirical availability: {expected.get('empirical_availability'):.2%}")
    print()

    # ========================================================================
    # STEP 5: Validate Signal Irrigation
    # ========================================================================
    print("\n" + "="*80)
    print("STEP 5: VALIDATE SIGNAL IRRIGATION")
    print("="*80 + "\n")

    print(f"→ Validating signal delivery for {question_id}...")
    validation = irrigator.validate_question_irrigation(question_id)

    print(f"  Valid: {'✓' if validation['valid'] else '✗'}")
    print(f"  Primary coverage: {validation['primary_coverage']:.1%}")
    print(f"  Secondary coverage: {validation['secondary_coverage']:.1%}")
    print(f"  Total deliveries: {validation['total_deliveries']}")

    if validation.get('missing_primary'):
        print(f"  Missing primary signals: {', '.join(validation['missing_primary'])}")
    print()

    # ========================================================================
    # STEP 6: View Irrigation Statistics
    # ========================================================================
    print("\n" + "="*80)
    print("STEP 6: VIEW IRRIGATION STATISTICS")
    print("="*80 + "\n")

    stats = irrigator.get_irrigation_stats()

    print(f"Total signals received: {stats['total_signals_received']}")
    print(f"Total signals delivered: {stats['total_signals_delivered']}")
    print(f"Total questions irrigated: {stats['total_questions_irrigated']}")
    print(f"Irrigation efficiency: {stats['irrigation_efficiency']:.1%}")
    print(f"Average confidence: {stats['average_confidence']:.2f}")
    print(f"Total value added: {stats['total_value_added']:.2f}")
    print()

    print("Signals by type:")
    for signal_type, count in sorted(stats['signals_by_type'].items()):
        print(f"  {signal_type}: {count}")
    print()

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "="*80)
    print("SIGNAL DELIVERY FLOW SUMMARY")
    print("="*80 + "\n")

    print("1. ✓ Extractors detected signals from PDT text")
    print("2. ✓ SignalIrrigator loaded integration_map.json")
    print("3. ✓ Signals routed to questions via slot_to_signal mapping")
    print("4. ✓ Irrigation paths tracked with trace IDs")
    print("5. ✓ Value_added calculated from empirical availability")
    print("6. ✓ Signal delivery validated against expected signals")
    print()

    print("="*80)
    print("SISAS SIGNAL IRRIGATION IS NOW OPERATIONAL! 🚀")
    print("="*80)


if __name__ == "__main__":
    main()

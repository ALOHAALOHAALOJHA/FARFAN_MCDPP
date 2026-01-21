"""
Wiring Configuration - Configuración de Cableado
=================================================

Define las reglas de cableado entre:
- Consumers y sus signal types
- Extractors y sus consumers destino
- Phases y sus consumers

Este archivo es la FUENTE DE VERDAD para validación de contratos.

Author: FARFAN Pipeline Team
Version: 1.0.0
Date: 2026-01-20
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, FrozenSet, Optional, Any
from enum import Enum


class WiringStatus(str, Enum):
    """Estado de cableado."""
    ACTIVE = "ACTIVE"
    DRAFT = "DRAFT"
    SUSPENDED = "SUSPENDED"
    DEPRECATED = "DEPRECATED"


@dataclass(frozen=True)
class ConsumerWiring:
    """Configuración de cableado para un consumer."""
    consumer_id: str
    phase: str
    subscribed_signal_types: FrozenSet[str]
    required_capabilities: FrozenSet[str]
    status: WiringStatus = WiringStatus.ACTIVE


@dataclass(frozen=True)
class ExtractorWiring:
    """Configuración de cableado para un extractor."""
    extractor_id: str
    produces_signal_type: str
    target_consumers: FrozenSet[str]
    required_capabilities: FrozenSet[str]
    status: WiringStatus = WiringStatus.ACTIVE


# =============================================================================
# CONSUMER WIRING CONFIGURATION (17 CONSUMERS)
# =============================================================================

CONSUMER_WIRING: Dict[str, ConsumerWiring] = {
    # Phase 0
    "phase_00_bootstrap_consumer": ConsumerWiring(
        consumer_id="phase_00_bootstrap_consumer",
        phase="phase_0",
        subscribed_signal_types=frozenset(["SIGNAL_PACK", "STATIC_LOAD"]),
        required_capabilities=frozenset(["STATIC_LOAD", "BOOTSTRAP"]),
    ),
    "phase_00_providers_consumer": ConsumerWiring(
        consumer_id="phase_00_providers_consumer",
        phase="phase_0",
        subscribed_signal_types=frozenset(["STATIC_LOAD"]),
        required_capabilities=frozenset(["PROVIDER_INIT"]),
    ),

    # Phase 1
    "phase_01_extraction_consumer": ConsumerWiring(
        consumer_id="phase_01_extraction_consumer",
        phase="phase_1",
        subscribed_signal_types=frozenset([
            "MC01_STRUCTURAL", "MC02_QUANTITATIVE", "MC03_NORMATIVE",
            "MC04_PROGRAMMATIC", "MC05_FINANCIAL", "MC06_POPULATION",
            "MC07_TEMPORAL", "MC08_CAUSAL", "MC09_INSTITUTIONAL", "MC10_SEMANTIC"
        ]),
        required_capabilities=frozenset(["EXTRACTION"]),
    ),
    "phase_01_enrichment_consumer": ConsumerWiring(
        consumer_id="phase_01_enrichment_consumer",
        phase="phase_1",
        subscribed_signal_types=frozenset(["SIGNAL_PACK", "STATIC_LOAD"]),
        required_capabilities=frozenset(["SIGNAL_ENRICHMENT"]),
    ),

    # Phase 2
    "phase_02_enrichment_consumer": ConsumerWiring(
        consumer_id="phase_02_enrichment_consumer",
        phase="phase_2",
        subscribed_signal_types=frozenset([
            "PATTERN_ENRICHMENT", "KEYWORD_ENRICHMENT", "ENTITY_ENRICHMENT"
        ]),
        required_capabilities=frozenset(["ENRICHMENT"]),
    ),
    "phase_02_contract_consumer": ConsumerWiring(
        consumer_id="phase_02_contract_consumer",
        phase="phase_2",
        subscribed_signal_types=frozenset(["PATTERN_ENRICHMENT"]),
        required_capabilities=frozenset(["CONTRACT_EXECUTION"]),
    ),
    "phase_02_evidence_consumer": ConsumerWiring(
        consumer_id="phase_02_evidence_consumer",
        phase="phase_2",
        subscribed_signal_types=frozenset(["ENTITY_ENRICHMENT"]),
        required_capabilities=frozenset(["EVIDENCE_COLLECTION"]),
    ),
    "phase_02_executor_consumer": ConsumerWiring(
        consumer_id="phase_02_executor_consumer",
        phase="phase_2",
        subscribed_signal_types=frozenset(["PATTERN_ENRICHMENT", "KEYWORD_ENRICHMENT"]),
        required_capabilities=frozenset(["EXECUTOR"]),
    ),

    # Phase 3
    "phase_03_validation_consumer": ConsumerWiring(
        consumer_id="phase_03_validation_consumer",
        phase="phase_3",
        subscribed_signal_types=frozenset([
            "NORMATIVE_VALIDATION", "ENTITY_VALIDATION", "COHERENCE_VALIDATION"
        ]),
        required_capabilities=frozenset(["VALIDATION"]),
    ),
    "phase_03_scoring_consumer": ConsumerWiring(
        consumer_id="phase_03_scoring_consumer",
        phase="phase_3",
        subscribed_signal_types=frozenset(["COHERENCE_VALIDATION"]),
        required_capabilities=frozenset(["SCORING", "SIGNAL_ENRICHED_SCORING"]),
    ),

    # Phase 4-6
    "phase_04_micro_consumer": ConsumerWiring(
        consumer_id="phase_04_micro_consumer",
        phase="phase_4",
        subscribed_signal_types=frozenset(["MICRO_SCORE"]),
        required_capabilities=frozenset(["SCORING", "MICRO_LEVEL"]),
    ),
    "phase_05_meso_consumer": ConsumerWiring(
        consumer_id="phase_05_meso_consumer",
        phase="phase_5",
        subscribed_signal_types=frozenset(["MESO_SCORE"]),
        required_capabilities=frozenset(["SCORING", "MESO_LEVEL"]),
    ),
    "phase_06_macro_consumer": ConsumerWiring(
        consumer_id="phase_06_macro_consumer",
        phase="phase_6",
        subscribed_signal_types=frozenset(["MACRO_SCORE"]),
        required_capabilities=frozenset(["SCORING", "MACRO_LEVEL"]),
    ),

    # Phase 7-8
    "phase_07_meso_aggregation_consumer": ConsumerWiring(
        consumer_id="phase_07_meso_aggregation_consumer",
        phase="phase_7",
        subscribed_signal_types=frozenset(["MESO_AGGREGATION"]),
        required_capabilities=frozenset(["AGGREGATION", "CLUSTER_AGGREGATION"]),
    ),
    "phase_08_macro_aggregation_consumer": ConsumerWiring(
        consumer_id="phase_08_macro_aggregation_consumer",
        phase="phase_8",
        subscribed_signal_types=frozenset(["MACRO_AGGREGATION"]),
        required_capabilities=frozenset(["AGGREGATION", "RECOMMENDATION_ENGINE"]),
    ),

    # Phase 9
    "phase_09_report_consumer": ConsumerWiring(
        consumer_id="phase_09_report_consumer",
        phase="phase_9",
        subscribed_signal_types=frozenset(["REPORT_ASSEMBLY"]),
        required_capabilities=frozenset(["REPORT_GENERATION"]),
    ),
}


# =============================================================================
# EXTRACTOR WIRING CONFIGURATION (10 EXTRACTORS MC01-MC10)
# =============================================================================

EXTRACTOR_WIRING: Dict[str, ExtractorWiring] = {
    "MC01_structural_marker_extractor": ExtractorWiring(
        extractor_id="MC01_structural_marker_extractor",
        produces_signal_type="MC01_STRUCTURAL",
        target_consumers=frozenset(["phase_01_extraction_consumer"]),
        required_capabilities=frozenset(["TABLE_PARSING"]),
    ),
    "MC02_quantitative_triplet_extractor": ExtractorWiring(
        extractor_id="MC02_quantitative_triplet_extractor",
        produces_signal_type="MC02_QUANTITATIVE",
        target_consumers=frozenset(["phase_01_extraction_consumer"]),
        required_capabilities=frozenset(["NUMERIC_PARSING"]),
    ),
    "MC03_normative_reference_extractor": ExtractorWiring(
        extractor_id="MC03_normative_reference_extractor",
        produces_signal_type="MC03_NORMATIVE",
        target_consumers=frozenset(["phase_01_extraction_consumer"]),
        required_capabilities=frozenset(["NER_EXTRACTION"]),
    ),
    "MC04_programmatic_hierarchy_extractor": ExtractorWiring(
        extractor_id="MC04_programmatic_hierarchy_extractor",
        produces_signal_type="MC04_PROGRAMMATIC",
        target_consumers=frozenset(["phase_01_extraction_consumer"]),
        required_capabilities=frozenset(["GRAPH_CONSTRUCTION"]),
    ),
    "MC05_financial_chain_extractor": ExtractorWiring(
        extractor_id="MC05_financial_chain_extractor",
        produces_signal_type="MC05_FINANCIAL",
        target_consumers=frozenset(["phase_01_extraction_consumer"]),
        required_capabilities=frozenset(["NUMERIC_PARSING", "FINANCIAL_ANALYSIS"]),
    ),
    "MC06_population_disaggregation_extractor": ExtractorWiring(
        extractor_id="MC06_population_disaggregation_extractor",
        produces_signal_type="MC06_POPULATION",
        target_consumers=frozenset(["phase_01_extraction_consumer"]),
        required_capabilities=frozenset(["NER_EXTRACTION"]),
    ),
    "MC07_temporal_consistency_extractor": ExtractorWiring(
        extractor_id="MC07_temporal_consistency_extractor",
        produces_signal_type="MC07_TEMPORAL",
        target_consumers=frozenset(["phase_01_extraction_consumer"]),
        required_capabilities=frozenset(["TEMPORAL_REASONING"]),
    ),
    "MC08_causal_verb_extractor": ExtractorWiring(
        extractor_id="MC08_causal_verb_extractor",
        produces_signal_type="MC08_CAUSAL",
        target_consumers=frozenset(["phase_01_extraction_consumer"]),
        required_capabilities=frozenset(["CAUSAL_INFERENCE"]),
    ),
    "MC09_institutional_ner_extractor": ExtractorWiring(
        extractor_id="MC09_institutional_ner_extractor",
        produces_signal_type="MC09_INSTITUTIONAL",
        target_consumers=frozenset(["phase_01_extraction_consumer"]),
        required_capabilities=frozenset(["NER_EXTRACTION"]),
    ),
    "MC10_semantic_relationship_extractor": ExtractorWiring(
        extractor_id="MC10_semantic_relationship_extractor",
        produces_signal_type="MC10_SEMANTIC",
        target_consumers=frozenset(["phase_01_extraction_consumer"]),
        required_capabilities=frozenset(["SEMANTIC_PROCESSING", "GRAPH_CONSTRUCTION"]),
    ),
}


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_consumer_wiring(consumer_id: str) -> tuple[bool, List[str]]:
    """Valida el cableado de un consumer."""
    errors = []

    wiring = CONSUMER_WIRING.get(consumer_id)
    if wiring is None:
        return False, [f"Consumer {consumer_id} not found in wiring config"]

    # Validar que tiene signal types
    if not wiring.subscribed_signal_types:
        errors.append(f"Consumer {consumer_id} has no subscribed signal types")

    # Validar que tiene capabilities
    if not wiring.required_capabilities:
        errors.append(f"Consumer {consumer_id} has no required capabilities")

    # Validar status
    if wiring.status == WiringStatus.SUSPENDED:
        errors.append(f"Consumer {consumer_id} is SUSPENDED")

    return len(errors) == 0, errors


def validate_extractor_wiring(extractor_id: str) -> tuple[bool, List[str]]:
    """Valida el cableado de un extractor."""
    errors = []

    wiring = EXTRACTOR_WIRING.get(extractor_id)
    if wiring is None:
        return False, [f"Extractor {extractor_id} not found in wiring config"]

    # Validar que produce un signal type
    if not wiring.produces_signal_type:
        errors.append(f"Extractor {extractor_id} produces no signal type")

    # Validar que tiene target consumers
    if not wiring.target_consumers:
        errors.append(f"Extractor {extractor_id} has no target consumers")

    # Validar que los target consumers existen
    for consumer_id in wiring.target_consumers:
        if consumer_id not in CONSUMER_WIRING:
            errors.append(f"Target consumer {consumer_id} not found")

    return len(errors) == 0, errors


def validate_all_wiring() -> tuple[bool, Dict[str, List[str]]]:
    """Valida todo el cableado del sistema."""
    all_errors = {}

    # Validar consumers
    for consumer_id in CONSUMER_WIRING:
        valid, errors = validate_consumer_wiring(consumer_id)
        if not valid:
            all_errors[consumer_id] = errors

    # Validar extractors
    for extractor_id in EXTRACTOR_WIRING:
        valid, errors = validate_extractor_wiring(extractor_id)
        if not valid:
            all_errors[extractor_id] = errors

    return len(all_errors) == 0, all_errors


def get_wiring_summary() -> Dict[str, Any]:
    """Obtiene resumen del cableado."""
    return {
        "total_consumers": len(CONSUMER_WIRING),
        "total_extractors": len(EXTRACTOR_WIRING),
        "consumers_by_phase": {
            phase: len([c for c in CONSUMER_WIRING.values() if c.phase == phase])
            for phase in sorted(set(c.phase for c in CONSUMER_WIRING.values()))
        },
        "signal_types_covered": len(set(
            st for c in CONSUMER_WIRING.values()
            for st in c.subscribed_signal_types
        )),
        "active_consumers": len([
            c for c in CONSUMER_WIRING.values()
            if c.status == WiringStatus.ACTIVE
        ]),
        "active_extractors": len([
            e for e in EXTRACTOR_WIRING.values()
            if e.status == WiringStatus.ACTIVE
        ]),
    }


def get_consumers_for_phase(phase: str) -> List[str]:
    """Obtiene IDs de consumers para una fase."""
    return [
        consumer_id
        for consumer_id, wiring in CONSUMER_WIRING.items()
        if wiring.phase == phase
    ]


def get_signal_types_for_phase(phase: str) -> set[str]:
    """Obtiene todos los signal types para una fase."""
    signal_types = set()
    for wiring in CONSUMER_WIRING.values():
        if wiring.phase == phase:
            signal_types.update(wiring.subscribed_signal_types)
    return signal_types


__all__ = [
    "WiringStatus",
    "ConsumerWiring",
    "ExtractorWiring",
    "CONSUMER_WIRING",
    "EXTRACTOR_WIRING",
    "validate_consumer_wiring",
    "validate_extractor_wiring",
    "validate_all_wiring",
    "get_wiring_summary",
    "get_consumers_for_phase",
    "get_signal_types_for_phase",
]

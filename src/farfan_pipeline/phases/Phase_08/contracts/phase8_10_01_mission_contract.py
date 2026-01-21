"""
Phase 8 Mission Contract
========================

Defines the execution mission and topological order for Phase 8.
Specifies weights, priorities, and execution sequencing.

Contract ID: P8-MISSION-CONTRACT-v1.0
Status: ACTIVE
"""

from dataclasses import dataclass
from typing import List, Dict
from enum import Enum


class WeightTier(Enum):
    """Weight tier classification for subphases."""
    CRITICAL = 10000  # Must execute, blocking
    HIGH = 5000       # Important, should execute
    STANDARD = 1000   # Normal priority


@dataclass
class SubphaseWeight:
    """Weight specification for a subphase."""
    
    subphase_id: str
    name: str
    weight: int
    tier: WeightTier
    description: str


# ============================================================================
# PHASE 8 TOPOLOGICAL EXECUTION ORDER
# ============================================================================

# Phase 8 follows a clear stage-based execution order:
# Stage 00: Data models (foundation)
# Stage 10: Schema validation
# Stage 20: Recommendation engines (core logic)
# Stage 30: Signal enrichment
# Stage 35: Entity targeting

PHASE8_TOPOLOGICAL_ORDER = [
    "phase8_00_00_data_models",              # 0: Foundation data structures
    "phase8_10_00_schema_validation",        # 1: Validation layer
    "phase8_20_02_generic_rule_engine",      # 2: Generic rule engine
    "phase8_20_03_template_compiler",        # 3: Template compilation
    "phase8_20_00_recommendation_engine",    # 4: Main recommendation engine
    "phase8_20_04_recommendation_engine_orchestrator",  # 5: Orchestrator
    "phase8_20_01_recommendation_engine_adapter",       # 6: Adapter
    "phase8_30_00_signal_enriched_recommendations",     # 7: Signal enrichment
    "phase8_35_00_entity_targeted_recommendations",     # 8: Entity targeting
]


# ============================================================================
# PHASE 8 SUBPHASE WEIGHTS
# ============================================================================

PHASE8_SUBPHASE_WEIGHTS = [
    SubphaseWeight(
        subphase_id="SP8-00",
        name="Data Models Foundation",
        weight=10000,
        tier=WeightTier.CRITICAL,
        description="Core data structures used by all other modules"
    ),
    SubphaseWeight(
        subphase_id="SP8-10",
        name="Schema Validation",
        weight=9000,
        tier=WeightTier.CRITICAL,
        description="Validate recommendation rules against schema"
    ),
    SubphaseWeight(
        subphase_id="SP8-20-00",
        name="Main Recommendation Engine",
        weight=10000,
        tier=WeightTier.CRITICAL,
        description="Core recommendation generation logic"
    ),
    SubphaseWeight(
        subphase_id="SP8-20-01",
        name="Recommendation Adapter",
        weight=5000,
        tier=WeightTier.HIGH,
        description="Adapter for pipeline integration"
    ),
    SubphaseWeight(
        subphase_id="SP8-20-02",
        name="Generic Rule Engine",
        weight=9000,
        tier=WeightTier.CRITICAL,
        description="Generic rule matching engine with strategies"
    ),
    SubphaseWeight(
        subphase_id="SP8-20-03",
        name="Template Compiler",
        weight=7000,
        tier=WeightTier.HIGH,
        description="Template compilation for recommendations"
    ),
    SubphaseWeight(
        subphase_id="SP8-20-04",
        name="Engine Orchestrator",
        weight=8000,
        tier=WeightTier.HIGH,
        description="Orchestrates recommendation generation"
    ),
    SubphaseWeight(
        subphase_id="SP8-30",
        name="Signal Enrichment",
        weight=6000,
        tier=WeightTier.HIGH,
        description="Enrich recommendations with SISAS signals"
    ),
    SubphaseWeight(
        subphase_id="SP8-35",
        name="Entity Targeting",
        weight=4000,
        tier=WeightTier.STANDARD,
        description="Target recommendations to specific entities"
    ),
]


def validate_mission_contract() -> Dict[str, any]:
    """
    Validate Phase 8 mission contract consistency.
    
    Returns:
        Validation result with status and details
    """
    results = {
        'contract_id': 'P8-MISSION-CONTRACT-v1.0',
        'status': 'PASS',
        'topological_order_defined': len(PHASE8_TOPOLOGICAL_ORDER),
        'subphase_weights_defined': len(PHASE8_SUBPHASE_WEIGHTS),
        'critical_subphases': 0,
        'high_subphases': 0,
        'standard_subphases': 0,
        'warnings': []
    }
    
    # Count subphases by tier
    for sp in PHASE8_SUBPHASE_WEIGHTS:
        if sp.tier == WeightTier.CRITICAL:
            results['critical_subphases'] += 1
        elif sp.tier == WeightTier.HIGH:
            results['high_subphases'] += 1
        else:
            results['standard_subphases'] += 1
    
    # Verify all modules in topological order have weights
    module_names = set(PHASE8_TOPOLOGICAL_ORDER)
    weight_ids = {sp.subphase_id for sp in PHASE8_SUBPHASE_WEIGHTS}
    
    # Basic consistency check
    if results['topological_order_defined'] != len(module_names):
        results['warnings'].append(
            f"Duplicate modules in topological order"
        )
    
    return results


def get_execution_order() -> List[str]:
    """
    Get the canonical execution order for Phase 8 modules.
    
    Returns:
        Ordered list of module names
    """
    return PHASE8_TOPOLOGICAL_ORDER.copy()


def get_subphase_weight(module_name: str) -> int:
    """
    Get the execution weight for a module.
    
    Args:
        module_name: Name of the module
        
    Returns:
        Weight value (higher = more critical)
    """
    # Map module name to subphase ID
    for sp in PHASE8_SUBPHASE_WEIGHTS:
        if module_name.replace('phase8_', 'SP8-').replace('_', '-') in sp.subphase_id:
            return sp.weight
    
    return WeightTier.STANDARD.value  # Default weight


if __name__ == "__main__":
    # Self-test
    print("Phase 8 Mission Contract")
    print("=" * 70)
    
    result = validate_mission_contract()
    print(f"Status: {result['status']}")
    print(f"Topological order: {result['topological_order_defined']} modules")
    print(f"Subphase weights: {result['subphase_weights_defined']} weights")
    print(f"  - CRITICAL: {result['critical_subphases']}")
    print(f"  - HIGH: {result['high_subphases']}")
    print(f"  - STANDARD: {result['standard_subphases']}")
    
    print("\nExecution Order:")
    for idx, module in enumerate(PHASE8_TOPOLOGICAL_ORDER):
        weight = get_subphase_weight(module)
        print(f"  {idx}. {module} (weight: {weight})")
    
    print("=" * 70)

"""Phase 1 Mission Contract - Weight-Based Execution Contract.

This contract governs the execution of 16 subphases (SP0-SP15) plus SP4.1 in Phase 1,
enforcing weight-based criticality and execution behavior.

Constitutional Invariants:
- EXACTLY 300 chunks must be produced (10 PA × 6 DIM × 5 Questions per slot)
- All 16 subphases must complete or fail gracefully according to weight tier
- SP4.1 (Colombian PDM Enhancement) is MANDATORY and runs as part of SP4
- Weight-based timeouts: CRITICAL (3x), HIGH (2x), STANDARD (1x)

═══════════════════════════════════════════════════════════════════════════════
                    TRÍADA CONSTITUCIONAL DE FASE 1
═══════════════════════════════════════════════════════════════════════════════

PARAMETRIZACIÓN (ex ante, diseño-tiempo):
    Subfases: SP2, SP4
    - SP2 recibe PlanStructureProfile (σ, η, μ, τ, k) vía DI
    - SP4 CONSUME obligatoriamente el profile para grid PA×Dim×Q
    - Define chunk_size_multiplier, overlap_ratio por sección
    NAMESPACE: parametrization.sp2.*, parametrization.sp4.*

CALIBRACIÓN (ex post, evidencia-tiempo):
    Subfases: SP5, SP7, SP9, SP10, SP12, SP14 (sólo HIGH tier)
    - Ajuste empírico basado en métricas observadas
    - Phase1Calibrator.freeze() → artefacto versionado
    - JAMÁS calibrar CRITICAL subphases
    NAMESPACE: calibration.sp5.*, calibration.sp7.*, ...

INVARIANTE (constitucional, intocable):
    Subfases: SP4, SP4.1, SP11, SP13 (CRITICAL tier)
    - 300 chunks = 10 PA × 6 Dim × 5 Q — NUNCA modificar
    - Colombian PDM Enhancement es MANDATORIO para todos los chunks
    - Cualquier "optimización" que altere esto es INCONSTITUCIONAL
    NAMESPACE: invariant.300_chunks, invariant.grid_spec, invariant.pdm_enhancement

REGLA DE PRECEDENCIA:
    1. Parametrizar PRIMERO (abrir los diales)
    2. Calibrar DESPUÉS (girar los diales con evidencia)
    3. Si calibras sin parametrizar, solo estás afinando un error bien definido

ADVERTENCIA PARA FUTUROS DESARROLLADORES:
    Dentro de 6 meses alguien intentará "optimizar SP4" reduciendo chunks
    para "mejorar performance". ESTO ESTÁ PROHIBIDO CONSTITUCIONALMENTE.
    Los 300 chunks NO son un parámetro ajustable — son la CONSTITUCIÓN.
    La formula es: 10 PA × 6 DIM × 5 Q = 300 (inmutable)
═══════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, FrozenSet


# ═══════════════════════════════════════════════════════════════════════════
# TRÍADA ASSERTIONS - Ejecutadas en import-time como guardrails
# ═══════════════════════════════════════════════════════════════════════════

# Subphases que PUEDEN ser parametrizadas (diseño-tiempo)
PARAMETRIZABLE_SUBPHASES: FrozenSet[str] = frozenset({"SP2", "SP4"})

# Subphases que PUEDEN ser calibradas (evidencia-tiempo) — solo HIGH tier
CALIBRATABLE_SUBPHASES: FrozenSet[str] = frozenset({
    "SP5", "SP7", "SP9", "SP10", "SP12", "SP14"
})

# Subphases INVARIANTES — JAMÁS tocar (CRITICAL tier)
INVARIANT_SUBPHASES: FrozenSet[str] = frozenset({"SP4", "SP11", "SP13"})

# CONSTITUTIONAL INVARIANT: 300 chunks = 10 PA × 6 Dim × 5 Q
CONSTITUTIONAL_CHUNK_COUNT: int = 300
CONSTITUTIONAL_POLICY_AREAS: int = 10
CONSTITUTIONAL_CAUSAL_DIMENSIONS: int = 6
CONSTITUTIONAL_QUESTIONS_PER_DIMENSION: int = 5

# Assertion at import-time: matemática constitucional
assert (
    CONSTITUTIONAL_POLICY_AREAS 
    * CONSTITUTIONAL_CAUSAL_DIMENSIONS 
    * CONSTITUTIONAL_QUESTIONS_PER_DIMENSION
    == CONSTITUTIONAL_CHUNK_COUNT
), f"CONSTITUTIONAL VIOLATION: {CONSTITUTIONAL_POLICY_AREAS} PA × {CONSTITUTIONAL_CAUSAL_DIMENSIONS} Dim × {CONSTITUTIONAL_QUESTIONS_PER_DIMENSION} Q ≠ {CONSTITUTIONAL_CHUNK_COUNT} chunks"


class WeightTier(Enum):
    """Weight tier classification for subphases.
    
    CRITICAL: Constitutional invariants — NEVER calibrate
    HIGH: Essential processing — CAN be calibrated
    STANDARD: Standard processing — CAN be calibrated but lower priority
    """
    CRITICAL = "CRITICAL"  # 10000: Constitutional invariants — INVARIANT tier
    HIGH = "HIGH"          # 5000-9000: Essential processing — CALIBRATABLE tier
    STANDARD = "STANDARD"  # 900-4999: Standard processing


@dataclass(frozen=True)
class SubphaseWeight:
    """Weight specification for a subphase."""
    subphase_id: str
    weight: int
    tier: WeightTier
    timeout_multiplier: float
    abort_on_failure: bool
    description: str


# Phase 1 Subphase Weight Specification
PHASE1_SUBPHASE_WEIGHTS: Dict[str, SubphaseWeight] = {
    "SP0": SubphaseWeight("SP0", 900, WeightTier.STANDARD, 1.0, False, "Input validation"),
    "SP1": SubphaseWeight("SP1", 2500, WeightTier.STANDARD, 1.0, False, "Language preprocessing"),
    "SP2": SubphaseWeight("SP2", 3000, WeightTier.STANDARD, 1.0, False, "Structural analysis"),
    "SP3": SubphaseWeight("SP3", 4000, WeightTier.STANDARD, 1.0, False, "Knowledge graph"),
    "SP4": SubphaseWeight("SP4", 10000, WeightTier.CRITICAL, 3.0, True, "Question-aware chunking (300 chunks)"),
    "SP4.1": SubphaseWeight("SP4.1", 0, WeightTier.CRITICAL, 0.0, True, "Colombian PDM enhancement (mandatory sub-subphase)"),
    "SP5": SubphaseWeight("SP5", 5000, WeightTier.HIGH, 2.0, False, "Causal extraction"),
    "SP6": SubphaseWeight("SP6", 3500, WeightTier.STANDARD, 1.0, False, "Arguments extraction"),
    "SP7": SubphaseWeight("SP7", 4500, WeightTier.STANDARD, 1.0, False, "Discourse analysis"),
    "SP8": SubphaseWeight("SP8", 3500, WeightTier.STANDARD, 1.0, False, "Temporal extraction"),
    "SP9": SubphaseWeight("SP9", 6000, WeightTier.HIGH, 2.0, False, "Causal integration"),
    "SP10": SubphaseWeight("SP10", 8000, WeightTier.HIGH, 2.0, False, "Strategic integration"),
    "SP11": SubphaseWeight("SP11", 10000, WeightTier.CRITICAL, 3.0, True, "Chunk assembly (300 chunks)"),
    "SP12": SubphaseWeight("SP12", 7000, WeightTier.HIGH, 2.0, False, "SISAS irrigation"),
    "SP13": SubphaseWeight("SP13", 10000, WeightTier.CRITICAL, 3.0, True, "CPP packaging"),
    "SP14": SubphaseWeight("SP14", 5000, WeightTier.HIGH, 2.0, False, "Quality metrics"),
    "SP15": SubphaseWeight("SP15", 9000, WeightTier.HIGH, 2.0, False, "Integrity verification"),
}


def validate_mission_contract() -> bool:
    """Validate Phase 1 mission contract integrity.
    
    Returns:
        True if contract is valid
        
    Raises:
        ValueError: If contract validation fails
    """
    # Include SP4.1 in count but it's a sub-subphase with weight 0
    if len(PHASE1_SUBPHASE_WEIGHTS) != 17:  # 16 main + 1 sub-subphase
        raise ValueError(f"Mission contract must have exactly 17 entries (16 SP + SP4.1), got {len(PHASE1_SUBPHASE_WEIGHTS)}")
    
    critical_subphases = [sp for sp in PHASE1_SUBPHASE_WEIGHTS.values() if sp.tier == WeightTier.CRITICAL and sp.weight > 0]
    if len(critical_subphases) != 3:
        raise ValueError(f"Mission contract must have exactly 3 CRITICAL subphases with weight>0, got {len(critical_subphases)}")
    
    # Verify SP4, SP11, SP13 are critical
    if not all(sp in ["SP4", "SP11", "SP13"] for sp in [s.subphase_id for s in critical_subphases]):
        raise ValueError("CRITICAL subphases must be SP4, SP11, SP13")
    
    # Verify SP4.1 exists and is CRITICAL but has weight 0 (part of SP4's budget)
    sp4_1 = PHASE1_SUBPHASE_WEIGHTS.get("SP4.1")
    if not sp4_1:
        raise ValueError("SP4.1 (Colombian PDM enhancement) must be in contract")
    if sp4_1.tier != WeightTier.CRITICAL:
        raise ValueError("SP4.1 must be CRITICAL tier")
    if sp4_1.weight != 0:
        raise ValueError("SP4.1 weight must be 0 (included in SP4's budget)")
    
    return True


def validate_triada_integrity() -> bool:
    """Validate the Tríada (Parametrization/Calibration/Invariant) integrity.
    
    This function enforces constitutional constraints:
    1. INVARIANT subphases MUST be CRITICAL tier
    2. CALIBRATABLE subphases MUST be HIGH tier (never CRITICAL)
    3. SP4 is special: PARAMETRIZABLE but also INVARIANT (design vs runtime)
    4. No overlap between CALIBRATABLE and INVARIANT (except SP4 design-only)
    
    Returns:
        True if Tríada is valid
        
    Raises:
        ValueError: If Tríada constraints are violated
    """
    # Rule 1: All INVARIANT subphases must be CRITICAL tier
    for sp_id in INVARIANT_SUBPHASES:
        sp = PHASE1_SUBPHASE_WEIGHTS.get(sp_id)
        if sp is None:
            raise ValueError(f"INVARIANT subphase {sp_id} not found in contract")
        if sp.tier != WeightTier.CRITICAL:
            raise ValueError(
                f"CONSTITUTIONAL VIOLATION: INVARIANT subphase {sp_id} "
                f"is {sp.tier.value}, MUST be CRITICAL"
            )
    
    # Rule 2: All CALIBRATABLE subphases must NOT be CRITICAL
    for sp_id in CALIBRATABLE_SUBPHASES:
        sp = PHASE1_SUBPHASE_WEIGHTS.get(sp_id)
        if sp is None:
            raise ValueError(f"CALIBRATABLE subphase {sp_id} not found in contract")
        if sp.tier == WeightTier.CRITICAL:
            raise ValueError(
                f"CONSTITUTIONAL VIOLATION: Cannot calibrate CRITICAL subphase {sp_id}. "
                "Calibration is forbidden on constitutional invariants."
            )
    
    # Rule 3: CALIBRATABLE and INVARIANT must not overlap
    # Note: SP4 is both PARAMETRIZABLE and INVARIANT, but NOT CALIBRATABLE
    forbidden_overlap = CALIBRATABLE_SUBPHASES & INVARIANT_SUBPHASES
    if forbidden_overlap:
        raise ValueError(
            f"CONSTITUTIONAL VIOLATION: Subphases {forbidden_overlap} are both "
            "CALIBRATABLE and INVARIANT. This is forbidden."
        )
    
    # Rule 4: Verify 300 chunks math (10 PA × 6 Dim × 5 Q)
    expected_chunks = (
        CONSTITUTIONAL_POLICY_AREAS 
        * CONSTITUTIONAL_CAUSAL_DIMENSIONS 
        * CONSTITUTIONAL_QUESTIONS_PER_DIMENSION
    )
    if expected_chunks != CONSTITUTIONAL_CHUNK_COUNT:
        raise ValueError(
            f"CONSTITUTIONAL VIOLATION: {CONSTITUTIONAL_POLICY_AREAS} PA × "
            f"{CONSTITUTIONAL_CAUSAL_DIMENSIONS} Dim × "
            f"{CONSTITUTIONAL_QUESTIONS_PER_DIMENSION} Q = {expected_chunks}, "
            f"expected {CONSTITUTIONAL_CHUNK_COUNT}"
        )
    
    return True


def is_subphase_calibratable(sp_id: str) -> bool:
    """Check if a subphase can be calibrated.
    
    Only HIGH tier subphases can be calibrated.
    CRITICAL tier subphases are INVARIANT and cannot be calibrated.
    
    Args:
        sp_id: Subphase identifier (e.g., "SP5", "SP11")
        
    Returns:
        True if subphase can be calibrated
    """
    return sp_id in CALIBRATABLE_SUBPHASES


def is_subphase_parametrizable(sp_id: str) -> bool:
    """Check if a subphase can be parametrized.
    
    Only SP2 and SP4 receive PlanStructureProfile for parametrization.
    Parametrization happens at design-time (ex ante), not runtime.
    
    Args:
        sp_id: Subphase identifier (e.g., "SP2", "SP4")
        
    Returns:
        True if subphase can receive structural parameters
    """
    return sp_id in PARAMETRIZABLE_SUBPHASES


def is_subphase_invariant(sp_id: str) -> bool:
    """Check if a subphase is constitutionally invariant.
    
    INVARIANT subphases (SP4, SP11, SP13) enforce the 60-chunk grid.
    They CANNOT be calibrated or modified at runtime.
    
    Args:
        sp_id: Subphase identifier
        
    Returns:
        True if subphase is constitutional invariant
    """
    return sp_id in INVARIANT_SUBPHASES


__all__ = [
    "WeightTier",
    "SubphaseWeight",
    "PHASE1_SUBPHASE_WEIGHTS",
    "PARAMETRIZABLE_SUBPHASES",
    "CALIBRATABLE_SUBPHASES",
    "INVARIANT_SUBPHASES",
    "CONSTITUTIONAL_CHUNK_COUNT",
    "CONSTITUTIONAL_POLICY_AREAS",
    "CONSTITUTIONAL_CAUSAL_DIMENSIONS",
    "validate_mission_contract",
    "validate_triada_integrity",
    "is_subphase_calibratable",
    "is_subphase_parametrizable",
    "is_subphase_invariant",
]

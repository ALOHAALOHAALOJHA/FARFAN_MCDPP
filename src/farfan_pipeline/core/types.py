"""
Core type definitions for F.A.R.F.A.N analytical pipeline.

This module defines the fundamental analytical dimensions used for empirical
evidence extraction and causal mechanism identification in policy documents.

EPISTEMOLOGICAL FOUNDATION:
---------------------------
Following Derek Beach & Rasmus Brun Pedersen's process-tracing methodology:

1. ANALYTICAL DIMENSIONS: Orthogonal epistemological operations for evidence extraction
2. CAUSAL MECHANISMS: Real-world entities with parts that transmit causal forces
3. EMPIRICAL FINGERPRINTS: Observable implications of mechanism operation

Our dimensions are NOT steps in a logical chain but distinct analytical 
operations that extract different types of evidence about underlying mechanisms.

The MECANISMOS dimension captures explicit mechanistic reasoning about HOW
and WHY interventions produce outcomes through specific causal pathways.

Author: F.A.R.F.A.N Core Team
Created: 2026-01-16
Updated: 2026-01-21
Version: 4.0.0-beach-pedersen
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum, unique
from typing import Dict, List, Literal, Optional, Protocol, Set, Tuple, Any

import structlog

logger = structlog.get_logger(__name__)


# ============================================================================
# TYPE ALIASES - Process Tracing Evidence Categories
# ============================================================================

#: Types of process-tracing tests (Beach & Pedersen, 2019)
ProcessTracingTestType = Literal[
    "hoop",            # Necessary but not sufficient (must pass to survive)
    "smoking_gun",     # Sufficient but not necessary (passing confirms)
    "doubly_decisive", # Necessary AND sufficient (decisive test)
    "straw_in_wind"    # Neither necessary nor sufficient (weak update)
]

#: Evidence diagnostic power levels for hypothesis discrimination
DiagnosticPowerType = Literal["negligible", "low", "moderate", "high", "decisive"]

#: Mechanism component types in Beach-Pedersen framework
MechanismPartType = Literal[
    "entity",                  # Actor or structure with causal powers
    "activity",               # What the entity does
    "observable_implication"  # Empirical fingerprint we should observe
]

#: Output types from epistemic levels (aligned with episteme_rules.md)
EpistemicOutputType = Literal["FACT", "PARAMETER", "CONSTRAINT", "NARRATIVE", "META_ANALYSIS"]


# ============================================================================
# PROTOCOLS - Analytical Interfaces
# ============================================================================

class EvidenceExtractable(Protocol):
    """Protocol for objects that can yield empirical evidence."""

    def extract_evidence(self) -> List[Dict[str, Any]]:
        """Extract empirical evidence from this object."""
        ...

    def diagnostic_power(self) -> DiagnosticPowerType:
        """Assess diagnostic power of extracted evidence."""
        ...


class MechanismTestable(Protocol):
    """Protocol for objects that can be tested as causal mechanisms."""

    def mechanism_parts(self) -> List[MechanismPartType]:
        """Identify parts of the causal mechanism."""
        ...

    def test_mechanism(self, test_type: ProcessTracingTestType) -> float:
        """Apply process-tracing test to mechanism."""
        ...


# ============================================================================
# ANALYTICAL DIMENSIONS - Epistemological Lenses
# ============================================================================

@unique
class DimensionAnalitica(IntEnum):
    """
    Dimensiones analíticas para extracción de evidencia empírica.
    
    ESTAS NO SON ESLABONES DE UNA CADENA sino operaciones analíticas
    ortogonales que extraen diferentes tipos de evidencia sobre los
    mecanismos causales subyacentes en un documento de política.
    
    Cada dimensión representa una lente epistemológica distinta:
    
    D1_CONTEXTO: Evidencia sobre condiciones contextuales y diagnóstico
    D2_DISEÑO: Evidencia sobre teoría del programa y diseño de intervención  
    D3_IMPLEMENTACION: Evidencia sobre procesos de implementación
    D4_SEGUIMIENTO: Evidencia sobre monitoreo y métricas
    D5_EVALUACION: Evidencia sobre evaluación de resultados
    D6_MECANISMOS: Evidencia sobre mecanismos causales explícitos
    
    La dimensión D6_MECANISMOS es especial: captura afirmaciones
    mecanísticas explícitas sobre CÓMO y POR QUÉ las intervenciones
    producen cambios (no solo QUÉ cambios producen).
    """
    
    D1_CONTEXTO = 1        # Análisis contextual y diagnóstico
    D2_DISEÑO = 2          # Diseño de intervención y teoría del programa
    D3_IMPLEMENTACION = 3  # Procesos y actividades de implementación
    D4_SEGUIMIENTO = 4     # Monitoreo y seguimiento de indicadores
    D5_EVALUACION = 5      # Evaluación de resultados y outcomes
    D6_MECANISMOS = 6      # Mecanismos causales explícitos
    
    @property
    def extraction_focus(self) -> str:
        """Define el foco de extracción de evidencia para esta dimensión."""
        focus_map = {
            self.D1_CONTEXTO: "Condiciones iniciales, problemas, línea base",
            self.D2_DISEÑO: "Objetivos, estrategias, teoría del programa",
            self.D3_IMPLEMENTACION: "Actividades, procesos, recursos utilizados",
            self.D4_SEGUIMIENTO: "Indicadores, metas, sistemas de monitoreo",
            self.D5_EVALUACION: "Resultados alcanzados, impactos medidos",
            self.D6_MECANISMOS: "Vínculos causales, mecanismos, teoría de cambio"
        }
        return focus_map.get(self, "")
    
    @property
    def evidence_type(self) -> str:
        """Tipo de evidencia que esta dimensión busca extraer."""
        type_map = {
            self.D1_CONTEXTO: "descriptive",
            self.D2_DISEÑO: "theoretical",
            self.D3_IMPLEMENTACION: "process",
            self.D4_SEGUIMIENTO: "metric",
            self.D5_EVALUACION: "outcome",
            self.D6_MECANISMOS: "mechanistic"
        }
        return type_map.get(self, "mixed")
    
    @property
    def process_tracing_test(self) -> ProcessTracingTestType:
        """Test de process-tracing más apropiado para esta dimensión."""
        test_map = {
            self.D1_CONTEXTO: "straw_in_wind",      # Context is suggestive
            self.D2_DISEÑO: "hoop",                 # Design must pass basic tests
            self.D3_IMPLEMENTACION: "hoop",         # Implementation necessary
            self.D4_SEGUIMIENTO: "straw_in_wind",   # Monitoring is informative
            self.D5_EVALUACION: "smoking_gun",      # Results can be decisive
            self.D6_MECANISMOS: "doubly_decisive"   # Mechanisms are crucial
        }
        return test_map.get(self, "straw_in_wind")
    
    def is_mechanistic(self) -> bool:
        """Check if this dimension deals with causal mechanisms."""
        return self == self.D6_MECANISMOS
    
    def is_empirical(self) -> bool:
        """Check if this dimension focuses on empirical evidence."""
        return self in {self.D1_CONTEXTO, self.D3_IMPLEMENTACION, 
                       self.D4_SEGUIMIENTO, self.D5_EVALUACION}
    
    def is_theoretical(self) -> bool:
        """Check if this dimension focuses on theoretical constructs."""
        return self in {self.D2_DISEÑO, self.D6_MECANISMOS}


# ============================================================================
# CAUSAL MECHANISM COMPONENTS - Beach & Pedersen Framework
# ============================================================================

@dataclass
class MechanismPart:
    """
    Parte de un mecanismo causal según Beach & Pedersen.
    
    Un mecanismo consta de:
    - Entidades (actors, institutions)
    - Actividades (what entities do)
    - Implicaciones observables (empirical fingerprints)
    """
    
    part_type: MechanismPartType
    description: str
    dimension: DimensionAnalitica
    observable_implications: List[str]
    diagnostic_power: DiagnosticPowerType
    
    def test_presence(self, evidence: List[str]) -> float:
        """
        Test if this mechanism part is present given evidence.
        
        Returns confidence score (0.0 - 1.0)
        """
        matches = sum(1 for impl in self.observable_implications 
                     if any(impl.lower() in e.lower() for e in evidence))
        return matches / len(self.observable_implications) if self.observable_implications else 0.0


@dataclass  
class CausalMechanism:
    """
    Complete causal mechanism with multiple parts.
    
    Following Beach & Pedersen, a mechanism is a system that
    transmits causal forces from X to Y through a series of
    interlocking parts.
    """
    
    name: str
    parts: List[MechanismPart]
    scope_conditions: List[str]
    
    def completeness_score(self) -> float:
        """Calculate how complete the mechanism specification is."""
        part_types = {p.part_type for p in self.parts}
        expected_types = {"entity", "activity", "observable_implication"}
        return len(part_types & expected_types) / len(expected_types)
    
    def test_mechanism(self, evidence_by_dimension: Dict[DimensionAnalitica, List[str]]) -> Dict[str, float]:
        """
        Test mechanism against evidence organized by dimension.
        
        Returns dict with confidence scores for each part.
        """
        results = {}
        for part in self.parts:
            evidence = evidence_by_dimension.get(part.dimension, [])
            results[part.description] = part.test_presence(evidence)
        return results


# ============================================================================
# LEGACY COMPATIBILITY - Bridge to Existing Code
# ============================================================================

# Map old CategoriaCausal to new DimensionAnalitica
# This maintains backward compatibility while we migrate

class CategoriaCausal(Enum):
    """
    DEPRECATED: Use DimensionAnalitica instead.
    
    Maintained for backward compatibility with existing validators.
    Maps heuristic chain categories to analytical dimensions.
    """
    
    INSUMOS = 1      # Maps to D1_CONTEXTO
    PROCESOS = 2     # Maps to D3_IMPLEMENTACION  
    PRODUCTOS = 3    # Maps to D4_SEGUIMIENTO
    RESULTADOS = 4   # Maps to D5_EVALUACION
    CAUSALIDAD = 5   # Maps to D6_MECANISMOS
    
    def to_dimension(self) -> DimensionAnalitica:
        """Convert to analytical dimension."""
        mapping = {
            self.INSUMOS: DimensionAnalitica.D1_CONTEXTO,
            self.PROCESOS: DimensionAnalitica.D3_IMPLEMENTACION,
            self.PRODUCTOS: DimensionAnalitica.D4_SEGUIMIENTO,
            self.RESULTADOS: DimensionAnalitica.D5_EVALUACION,
            self.CAUSALIDAD: DimensionAnalitica.D6_MECANISMOS
        }
        return mapping.get(self, DimensionAnalitica.D1_CONTEXTO)


# ============================================================================
# EVIDENCE CLASSIFICATION - For Bayesian Updates
# ============================================================================

@unique
class EvidenceStrength(Enum):
    """
    Clasificación de fuerza probatoria para actualización Bayesiana.
    
    Basado en la capacidad diagnóstica de la evidencia para
    discriminar entre hipótesis rivales (Beach & Pedersen).
    """
    
    DECISIVE = "decisive"      # Doubly decisive test passed
    HIGH = "high"              # Smoking gun test passed  
    MODERATE = "moderate"      # Hoop test passed
    LOW = "low"               # Straw in wind test passed
    NEGLIGIBLE = "negligible"  # No diagnostic power
    
    @property
    def bayesian_weight(self) -> float:
        """Weight for Bayesian updating."""
        weights = {
            self.DECISIVE: 0.95,
            self.HIGH: 0.80,
            self.MODERATE: 0.60,
            self.LOW: 0.40,
            self.NEGLIGIBLE: 0.20
        }
        return weights.get(self, 0.5)
    
    @classmethod
    def from_diagnostic_power(cls, power: DiagnosticPowerType) -> "EvidenceStrength":
        """Convert diagnostic power to evidence strength."""
        mapping = {
            "decisive": cls.DECISIVE,
            "high": cls.HIGH,
            "moderate": cls.MODERATE,
            "low": cls.LOW
        }
        return mapping.get(power, cls.NEGLIGIBLE)


# ============================================================================
# SCORE CLASSIFICATION - For Result Interpretation
# ============================================================================

@unique
class ScoreBand(Enum):
    """Clasificación de bandas de score para interpretación."""
    
    INSUFICIENTE = "INSUFICIENTE"
    BAJO = "BAJO"
    MEDIO = "MEDIO"
    ALTO = "ALTO"
    SATISFACTORIO = "SATISFACTORIO"
    
    @classmethod
    def from_score(cls, score: float, scale_max: float = 3.0) -> "ScoreBand":
        """Classify score into band."""
        normalized = score / scale_max
        if normalized < 0.3:
            return cls.INSUFICIENTE
        elif normalized < 0.5:
            return cls.BAJO
        elif normalized < 0.7:
            return cls.MEDIO
        elif normalized < 0.85:
            return cls.ALTO
        else:
            return cls.SATISFACTORIO


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    # Core analytical framework
    "DimensionAnalitica",
    "MechanismPart",
    "CausalMechanism",
    # Evidence classification
    "EvidenceStrength",
    "ScoreBand",
    # Type aliases
    "ProcessTracingTestType",
    "DiagnosticPowerType",
    "MechanismPartType",
    "EpistemicOutputType",
    # Protocols
    "EvidenceExtractable",
    "MechanismTestable",
    # Legacy compatibility
    "CategoriaCausal",
]

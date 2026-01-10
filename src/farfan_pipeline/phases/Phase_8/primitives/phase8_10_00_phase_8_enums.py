"""
Module: src.farfan_pipeline.phases.Phase_8.primitives.PHASE_8_ENUMS
Purpose: Enumeration types for Phase 8 - Recommendation Engine
Owner: phase8_core
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2026-01-05

This module provides enumeration types for Phase 8, ensuring type safety
and preventing invalid values.
"""

from __future__ import annotations

from enum import Enum, unique


@unique
class Level(str, Enum):
    """Recommendation level enumeration."""

    MICRO = "MICRO"
    MESO = "MESO"
    MACRO = "MACRO"

    def __str__(self) -> str:
        return self.value


@unique
class ScoreBand(str, Enum):
    """Score band classification."""

    BAJO = "BAJO"
    MEDIO = "MEDIO"
    ALTO = "ALTO"
    SATISFACTORIO = "SATISFACTORIO"
    INSUFICIENTE = "INSUFICIENTE"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_score(cls, score: float, level: Level = Level.MESO) -> ScoreBand:
        """
        Determine score band from numeric score.

        Args:
            score: Numeric score value
            level: Level context (MESO uses 0-100, MICRO uses 0-3)

        Returns:
            Appropriate ScoreBand
        """
        if level == Level.MICRO:
            # MICRO: 0-3 scale
            if score < 1.0:
                return cls.INSUFICIENTE
            elif score < 1.65:
                return cls.BAJO
            elif score < 2.5:
                return cls.MEDIO
            else:
                return cls.ALTO
        # MESO/MACRO: 0-100 scale
        elif score < 55:
            return cls.BAJO
        elif score < 75:
            return cls.MEDIO
        else:
            return cls.ALTO


@unique
class VarianceLevel(str, Enum):
    """Variance level classification."""

    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_variance(cls, variance: float) -> VarianceLevel:
        """
        Determine variance level from numeric variance.

        Args:
            variance: Numeric variance value (0.0 - 1.0)

        Returns:
            Appropriate VarianceLevel
        """
        if variance < 0.08:
            return cls.BAJA
        elif variance < 0.18:
            return cls.MEDIA
        else:
            return cls.ALTA


@unique
class QualityLevel(str, Enum):
    """Quality level classification."""

    EXCELENTE = "EXCELENTE"
    SATISFACTORIO = "SATISFACTORIO"
    ACEPTABLE = "ACEPTABLE"
    INSUFICIENTE = "INSUFICIENTE"
    DEFICIENTE = "DEFICIENTE"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_score(cls, score: float) -> QualityLevel:
        """
        Determine quality level from normalized score (0-1).

        Args:
            score: Normalized score (0.0 - 1.0)

        Returns:
            Appropriate QualityLevel
        """
        if score >= 0.9:
            return cls.EXCELENTE
        elif score >= 0.75:
            return cls.SATISFACTORIO
        elif score >= 0.55:
            return cls.ACEPTABLE
        elif score >= 0.3:
            return cls.INSUFICIENTE
        else:
            return cls.DEFICIENTE


@unique
class HorizonType(str, Enum):
    """Time horizon type."""

    T0 = "T0"  # Immediate (0-3 months)
    T1 = "T1"  # Short-term (3-6 months)
    T2 = "T2"  # Medium-term (6-12 months)
    T3 = "T3"  # Long-term (12-24 months)

    def __str__(self) -> str:
        return self.value

    @property
    def months_range(self) -> tuple[int, int]:
        """Return the month range for this horizon."""
        ranges = {
            "T0": (0, 3),
            "T1": (3, 6),
            "T2": (6, 12),
            "T3": (12, 24),
        }
        return ranges[self.value]


@unique
class VerificationFormat(str, Enum):
    """Verification artifact format."""

    PDF = "PDF"
    DATABASE_QUERY = "DATABASE_QUERY"
    JSON = "JSON"
    XML = "XML"
    EXCEL = "EXCEL"
    ATTESTATION = "ATTESTATION"

    def __str__(self) -> str:
        return self.value


@unique
class VerificationArtifactType(str, Enum):
    """Verification artifact type."""

    DOCUMENT = "DOCUMENT"
    SYSTEM_STATE = "SYSTEM_STATE"
    METRIC = "METRIC"
    ATTESTATION = "ATTESTATION"
    CERTIFICATE = "CERTIFICATE"

    def __str__(self) -> str:
        return self.value


@unique
class ModuleType(str, Enum):
    """Phase 8 module type classification."""

    ENGINE = "ENG"
    ADAPTER = "ADP"
    ENRICHER = "ENR"
    UTILITY = "UTIL"
    VALIDATOR = "VAL"
    INTERFACE = "INTF"

    def __str__(self) -> str:
        return self.value


@unique
class CriticalityLevel(str, Enum):
    """Module criticality level."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

    def __str__(self) -> str:
        return self.value


@unique
class ExecutionPattern(str, Enum):
    """Module execution pattern."""

    ON_DEMAND = "On-Demand"
    STREAMING = "Streaming"
    BATCH = "Batch"
    SCHEDULED = "Scheduled"

    def __str__(self) -> str:
        return self.value


@unique
class Stage(Enum):
    """Phase 8 stage enumeration."""

    BASE = 0
    INIT = 10
    ENGINE = 20
    ENRICHMENT = 30

    @property
    def name_label(self) -> str:
        """Return human-readable name."""
        labels = {
            0: "Base",
            10: "Init",
            20: "Engine",
            30: "Enrichment",
        }
        return labels[self.value]


@unique
class RuleLevel(str, Enum):
    """Rule application level (maps to Level but specific to rules)."""

    MICRO = "MICRO"
    MESO = "MESO"
    MACRO = "MACRO"

    def __str__(self) -> str:
        return self.value


@unique
class Cluster(str, Enum):
    """Cluster identifier enumeration."""

    CL01 = "CL01"
    CL02 = "CL02"
    CL03 = "CL03"
    CL04 = "CL04"

    def __str__(self) -> str:
        return self.value


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "Cluster",
    "CriticalityLevel",
    "ExecutionPattern",
    "HorizonType",
    "Level",
    "ModuleType",
    "QualityLevel",
    "RuleLevel",
    "ScoreBand",
    "Stage",
    "VarianceLevel",
    "VerificationArtifactType",
    "VerificationFormat",
]

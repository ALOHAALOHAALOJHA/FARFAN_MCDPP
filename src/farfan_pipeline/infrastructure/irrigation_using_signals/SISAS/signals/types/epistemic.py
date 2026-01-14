# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signals/types/epistemic.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from enum import Enum

from ...core.signal import Signal, SignalCategory, SignalContext, SignalSource, SignalConfidence


class DeterminacyLevel(Enum):
    """Niveles de determinismo de una respuesta"""
    HIGH = "HIGH"           # Afirmación clara y sin ambigüedad
    MEDIUM = "MEDIUM"       # Afirmación con alguna vaguedad
    LOW = "LOW"             # Afirmación muy vaga o condicional
    INDETERMINATE = "INDETERMINATE"  # No se puede determinar


class SpecificityLevel(Enum):
    """Niveles de especificidad"""
    HIGH = "HIGH"           # Menciona instrumento, alcance, responsable
    MEDIUM = "MEDIUM"       # Menciona algunos elementos
    LOW = "LOW"             # Muy genérico
    NONE = "NONE"           # Sin especificidad


class EmpiricalSupportLevel(Enum):
    """Niveles de soporte empírico"""
    STRONG = "STRONG"       # Referencia documental clara
    MODERATE = "MODERATE"   # Referencia parcial
    WEAK = "WEAK"           # Sin referencia pero plausible
    NONE = "NONE"           # Sin evidencia


class MethodStatus(Enum):
    """Estado de aplicación de método"""
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILURE = "FAILURE"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass
class AnswerDeterminacySignal(Signal):
    """
    Señal que evalúa qué tan determinante es una respuesta.

    Uso: Evaluar "Sí, se realiza evaluación previa en algunos casos"
    → MEDIUM (afirmación con scope ambiguity)
    """

    signal_type:  str = field(default="AnswerDeterminacySignal", init=False)

    # Payload específico
    question_id: str = ""
    determinacy_level: DeterminacyLevel = DeterminacyLevel.INDETERMINATE

    # Indicadores detectados
    affirmative_markers: List[str] = field(default_factory=list)
    # ["sí", "existe", "se realiza"]

    ambiguity_markers: List[str] = field(default_factory=list)
    # ["algunos casos", "a veces", "parcialmente"]

    negation_markers: List[str] = field(default_factory=list)
    # ["no", "nunca", "ninguno"]

    conditional_markers: List[str] = field(default_factory=list)
    # ["si", "cuando", "dependiendo"]

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.EPISTEMIC


@dataclass
class AnswerSpecificitySignal(Signal):
    """
    Señal que evalúa qué tan específica es una respuesta.

    Uso:  Detectar si menciona instrumento formal, alcance obligatorio,
    responsable institucional.
    """

    signal_type: str = field(default="AnswerSpecificitySignal", init=False)

    # Payload específico
    question_id: str = ""
    specificity_level: SpecificityLevel = SpecificityLevel.NONE

    # Elementos esperados vs encontrados
    expected_elements: List[str] = field(default_factory=list)
    # ["formal_instrument", "mandatory_scope", "institutional_owner"]

    found_elements: List[str] = field(default_factory=list)
    missing_elements: List[str] = field(default_factory=list)

    specificity_score: float = 0.0

    # Análisis detallado
    element_details: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    # {"formal_instrument": {"found": True, "value": "Decreto 1234", "confidence": 0.9}}

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.EPISTEMIC

    def __post_init__(self):
        super().__post_init__()
        # Calcular elementos faltantes
        self.missing_elements = [e for e in self.expected_elements if e not in self.found_elements]
        # Calcular score
        if self.expected_elements:
            self.specificity_score = len(self.found_elements) / len(self.expected_elements)

    def get_specificity_report(self) -> Dict[str, Any]:
        """Reporte detallado de especificidad"""
        return {
            "specificity_level": self.specificity_level.value,
            "specificity_score": self.specificity_score,
            "expected_count": len(self.expected_elements),
            "found_count": len(self.found_elements),
            "missing_count": len(self.missing_elements),
            "coverage_percentage": self.specificity_score * 100,
            "is_acceptable": self.specificity_score >= 0.6,
            "critical_missing": self.missing_elements[:3] if self.missing_elements else []
        }

    def get_improvement_actions(self) -> List[str]:
        """Genera acciones de mejora"""
        actions = []
        for missing in self.missing_elements:
            actions.append(f"Add {missing} to response")
        
        if self.specificity_score < 0.5:
            actions.append("Consider comprehensive revision of response")
        
        return actions

    def is_sufficient_for_compliance(self) -> bool:
        """Verifica si es suficiente para cumplimiento"""
        return self.specificity_level in [SpecificityLevel.HIGH, SpecificityLevel.MEDIUM]


@dataclass
class EmpiricalSupportSignal(Signal):
    """
    Señal que evalúa el soporte empírico/documental de una respuesta.

    Uso: Detectar si hay referencia a ley, decreto, resolución, documento.
    """

    signal_type: str = field(default="EmpiricalSupportSignal", init=False)

    # Payload específico
    question_id: str = ""
    support_level: EmpiricalSupportLevel = EmpiricalSupportLevel.NONE

    # Referencias encontradas
    normative_references: List[str] = field(default_factory=list)
    # ["Ley 1448 de 2011", "Decreto 4800"]

    document_references: List[str] = field(default_factory=list)
    # ["Plan Nacional de Desarrollo", "CONPES 3932"]

    institutional_references: List[str] = field(default_factory=list)
    # ["Ministerio del Interior", "Unidad de Víctimas"]

    temporal_references: List[str] = field(default_factory=list)
    # ["2022", "desde 2018", "vigencia 2023"]

    # Información adicional
    reference_quality_scores: Dict[str, float] = field(default_factory=dict)
    # {"Ley 1448": 1.0, "documento interno": 0.5}
    
    total_references: int = 0

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.EPISTEMIC

    def __post_init__(self):
        super().__post_init__()
        self.total_references = (
            len(self.normative_references) +
            len(self.document_references) +
            len(self.institutional_references) +
            len(self.temporal_references)
        )

    def compute_support_score(self) -> float:
        """Calcula score de soporte empírico"""
        if self.support_level == EmpiricalSupportLevel.STRONG:
            return 1.0
        elif self.support_level == EmpiricalSupportLevel.MODERATE:
            return 0.7
        elif self.support_level == EmpiricalSupportLevel.WEAK:
            return 0.4
        return 0.0

    def get_evidence_summary(self) -> Dict[str, Any]:
        """Resumen de evidencia"""
        return {
            "support_level": self.support_level.value,
            "support_score": self.compute_support_score(),
            "total_references": self.total_references,
            "normative_count": len(self.normative_references),
            "document_count": len(self.document_references),
            "institutional_count": len(self.institutional_references),
            "temporal_count": len(self.temporal_references),
            "has_legal_basis": len(self.normative_references) > 0,
            "has_institutional_backing": len(self.institutional_references) > 0,
            "is_time_bound": len(self.temporal_references) > 0
        }

    def get_strongest_references(self, limit: int = 3) -> List[str]:
        """Retorna referencias más fuertes"""
        # Priorizar normativas, luego documentos
        strong_refs = []
        strong_refs.extend(self.normative_references[:limit])
        if len(strong_refs) < limit:
            strong_refs.extend(self.document_references[:limit - len(strong_refs)])
        return strong_refs

    def requires_additional_evidence(self) -> bool:
        """Determina si requiere más evidencia"""
        return (
            self.support_level in [EmpiricalSupportLevel.WEAK, EmpiricalSupportLevel.NONE] or
            self.total_references < 2
        )


@dataclass
class MethodApplicationSignal(Signal):
    """
    Señal que indica el resultado de aplicar un método de evaluación.

    Uso: Registrar qué método se aplicó y su resultado.
    """

    signal_type: str = field(default="MethodApplicationSignal", init=False)

    # Payload específico
    question_id: str = ""
    method_id: str = ""  # "MC01", "MC05_financial_chains"
    method_version: str = ""

    # Resultado
    method_result: Dict[str, Any] = field(default_factory=dict)
    extraction_successful: bool = False
    extracted_values: List[Any] = field(default_factory=list)

    processing_time_ms: float = 0.0
    
    # Información adicional
    method_status: MethodStatus = MethodStatus.SUCCESS
    error_messages: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.EPISTEMIC

    def get_execution_report(self) -> Dict[str, Any]:
        """Reporte de ejecución del método"""
        return {
            "method_id": self.method_id,
            "method_version": self.method_version,
            "status": self.method_status.value,
            "extraction_successful": self.extraction_successful,
            "values_extracted": len(self.extracted_values),
            "processing_time_ms": self.processing_time_ms,
            "has_errors": len(self.error_messages) > 0,
            "error_count": len(self.error_messages),
            "performance_rating": self._get_performance_rating()
        }

    def _get_performance_rating(self) -> str:
        """Califica el performance"""
        if self.processing_time_ms < 100:
            return "excellent"
        elif self.processing_time_ms < 500:
            return "good"
        elif self.processing_time_ms < 2000:
            return "acceptable"
        return "slow"

    def is_reliable(self) -> bool:
        """Determina si el resultado es confiable"""
        return (
            self.method_status == MethodStatus.SUCCESS and
            self.extraction_successful and
            len(self.error_messages) == 0
        )

    def get_extracted_summary(self) -> Dict[str, Any]:
        """Resumen de valores extraídos"""
        return {
            "count": len(self.extracted_values),
            "types": list(set(type(v).__name__ for v in self.extracted_values)),
            "sample": self.extracted_values[:3] if self.extracted_values else []
        }

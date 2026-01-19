# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signals/types/epistemic.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
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
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory. EPISTEMIC


@dataclass
class EmpiricalSupportSignal(Signal):
    """
    Señal que evalúa el soporte empírico/documental de una respuesta.
    
    Uso: Detectar si hay referencia a ley, decreto, resolución, documento.
    """
    
    signal_type: str = field(default="EmpiricalSupportSignal", init=False)
    
    # Payload específico
    question_id: str = ""
    support_level: EmpiricalSupportLevel = EmpiricalSupportLevel. NONE
    
    # Referencias encontradas
    normative_references: List[str] = field(default_factory=list)
    # ["Ley 1448 de 2011", "Decreto 4800"]
    
    document_references: List[str] = field(default_factory=list)
    # ["Plan Nacional de Desarrollo", "CONPES 3932"]
    
    institutional_references: List[str] = field(default_factory=list)
    # ["Ministerio del Interior", "Unidad de Víctimas"]
    
    temporal_references: List[str] = field(default_factory=list)
    # ["2022", "desde 2018", "vigencia 2023"]
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory.EPISTEMIC


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
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory.EPISTEMIC
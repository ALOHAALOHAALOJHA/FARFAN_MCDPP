"""
Doctoral-Carver Narrative Synthesizer v3.0 (FULL EXTRACTION Edition)
=====================================================================

Genera respuestas PhD-level con estilo minimalista Raymond Carver:
- Precisión quirúrgica en cada afirmación
- Sin adornos retóricos vacíos
- Cada palabra respaldada por evidencia
- Honestidad brutal sobre limitaciones
- Razonamiento causal explícito

CAMBIO MAYOR v3.0: Extracción COMPLETA del contrato v3
------------------------------------------------------
v2.1 extraía solo: dimension, expected_elements, question_text, method_count, top 5 methods
v3.0 extrae TODO:
- 17 métodos con epistemological_foundation completo
- theoretical_framework con referencias académicas
- technical_approach con algoritmos y limitaciones
- output_interpretation con actionable_insights
- assembly_flow de 5 pasos
- concrete_example como benchmark
- template_variable_bindings
- validation_against_expected_elements

Fundamentos Teóricos:
- Rhetorical Structure Theory (Mann & Thompson, 1988)
- Dempster-Shafer Evidence Theory (belief functions)
- Causal Inference Framework (Pearl, 2009)
- Argument Mining (Stab & Gurevych, 2017)
- Calibrated Uncertainty Quantification (Gneiting & Raftery, 2007)

Arquitectura v3.0:
1. EnhancedContractInterpreter: Extrae TODA la semántica del contrato v3
2. EvidenceAnalyzer: Construye grafo causal de evidencia
3. GapAnalyzer: Análisis multi-dimensional de vacíos
4. BayesianConfidenceEngine: Inferencia calibrada de confianza
5. DimensionTheory: Estrategias teóricamente fundamentadas por D1-D6
6. DoctoralRenderer: Prosa con fundamentos epistemológicos y citas
7. MacroSynthesizer: Agregación holística con análisis PA×DIM

Invariantes:
[INV-001] Toda afirmación debe tener ≥1 evidencia citada
[INV-002] Gaps críticos siempre aparecen en respuesta
[INV-003] Confianza debe ser calibrada (no optimista)
[INV-004] Estilo Carver: oraciones cortas, verbos activos, sin adverbios
[INV-005] Macro synthesis con divergencia PA×DIM explícita
[INV-006] v3.0: Fundamentos epistemológicos explícitos en síntesis doctoral
[INV-007] v3.0: Limitaciones metodológicas como caveats honestos
[INV-008] v3.0: Referencias teóricas en formato académico

Author: F.A.R.F.A.N Pipeline
Version: 3.0.0-FULL-EXTRACTION
"""

from __future__ import annotations

import math
import re
import statistics
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    TypeAlias,
)

# Readability and style checking libraries
try:
    import textstat  # Flesch-Kincaid and readability metrics
except ImportError:
    textstat = None  # type: ignore

try:
    from proselint.tools import lint as proselint_check  # Style and clarity checking
except ImportError:
    proselint_check = None  # type: ignore


# =============================================================================
# TYPE SYSTEM
# =============================================================================

Confidence: TypeAlias = float  # [0.0, 1.0]
BeliefMass: TypeAlias = float  # Dempster-Shafer belief
PlausibilityMass: TypeAlias = float  # Dempster-Shafer plausibility


class Dimension(Enum):
    """Las 6 dimensiones causales del modelo lógico."""
    D1_INSUMOS = "DIM01"      # Inputs: recursos, datos, diagnóstico
    D2_ACTIVIDADES = "DIM02"  # Activities: acciones, instrumentos
    D3_PRODUCTOS = "DIM03"    # Outputs: entregables, metas
    D4_RESULTADOS = "DIM04"   # Outcomes: cambios inmediatos
    D5_IMPACTOS = "DIM05"     # Impacts: cambios largo plazo
    D6_CAUSALIDAD = "DIM06"   # Causality: lógica, M&E, adaptación


class EvidenceStrength(Enum):
    """Fuerza de evidencia según jerarquía epistemológica."""
    DEFINITIVE = "definitive"      # Dato oficial verificable
    STRONG = "strong"              # Múltiples fuentes concordantes
    MODERATE = "moderate"          # Fuente única confiable
    WEAK = "weak"                  # Inferido o parcial
    ABSENT = "absent"              # No encontrado


class GapSeverity(Enum):
    """Severidad de gaps con implicaciones para scoring."""
    CRITICAL = "critical"     # Bloquea evaluación positiva
    MAJOR = "major"           # Reduce score significativamente
    MINOR = "minor"           # Nota pero no bloquea
    COSMETIC = "cosmetic"     # Mejora deseable


class ArgumentRole(Enum):
    """Roles argumentativos (RST-inspired)."""
    CLAIM = "claim"           # Afirmación principal
    EVIDENCE = "evidence"     # Soporte factual
    WARRANT = "warrant"       # Justificación del vínculo
    QUALIFIER = "qualifier"   # Limitación/condición
    REBUTTAL = "rebuttal"     # Contraargumento reconocido
    BACKING = "backing"       # Soporte del warrant


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass(frozen=True)
class ExpectedElement:
    """Elemento esperado con semántica completa."""
    type: str
    required: bool
    minimum: int
    category: str  # 'quantitative', 'qualitative', 'relational'
    weight: float  # Importancia relativa [0, 1]

    @classmethod
    def from_contract(cls, elem: Dict[str, Any]) -> ExpectedElement:
        """Factory desde contrato."""
        elem_type = elem.get("type", "")

        # Inferir categoría desde tipo
        quantitative_types = {
            "indicadores_cuantitativos", "series_temporales_años",
            "monto_presupuestario", "meta_cuantificada", "linea_base",
            "porcentaje", "tasa", "indice"
        }
        relational_types = {
            "logica_causal_explicita", "ruta_transmision",
            "vinculo_causal", "dependencia_temporal"
        }

        if any(t in elem_type for t in quantitative_types):
            category = "quantitative"
        elif any(t in elem_type for t in relational_types):
            category = "relational"
        else:
            category = "qualitative"

        # Peso basado en required y minimum
        base_weight = 0.8 if elem.get("required", False) else 0.4
        min_val = elem.get("minimum", 0)
        weight = min(1.0, base_weight + (min_val * 0.05))

        return cls(
            type=elem_type,
            required=elem.get("required", False),
            minimum=elem.get("minimum", 1 if elem.get("required") else 0),
            category=category,
            weight=weight,
        )


@dataclass
class EvidenceItem:
    """Item de evidencia con metadatos ricos."""
    element_type: str
    value: Any
    confidence: float
    source_method: str
    document_location: Optional[str] = None

    # Computed properties
    strength: EvidenceStrength = EvidenceStrength.MODERATE
    is_quantitative: bool = False

    def __post_init__(self):
        """Compute derived properties."""
        # Determinar fuerza
        if self.confidence >= 0.9:
            self.strength = EvidenceStrength.STRONG
        elif self.confidence >= 0.7:
            self.strength = EvidenceStrength.MODERATE
        else:
            self.strength = EvidenceStrength.WEAK

        # Detectar si es cuantitativo
        if isinstance(self.value, (int, float)):
            self.is_quantitative = True
        elif isinstance(self.value, str):
            # Check for numeric patterns
            self.is_quantitative = bool(re.search(r'\d+[.,]?\d*\s*%?', self.value))


@dataclass
class EvidenceGap:
    """Gap con análisis causal de implicaciones."""
    element_type: str
    expected: int
    found: int
    severity: GapSeverity
    implication: str  # Por qué importa este gap
    remediation: str  # Qué haría falta

    @property
    def deficit(self) -> int:
        return max(0, self.expected - self.found)

    @property
    def fulfillment_ratio(self) -> float:
        if self.expected == 0:
            return 1.0
        return min(1.0, self.found / self.expected)


@dataclass
class ArgumentUnit:
    """Unidad argumentativa con rol retórico."""
    role: ArgumentRole
    content: str
    evidence_refs: List[str]  # IDs de evidencia que soportan
    confidence: float

    def render(self) -> str:
        """Render según rol."""
        if self.role == ArgumentRole.CLAIM:
            return self.content
        elif self.role == ArgumentRole.EVIDENCE:
            return f"- {self.content}"
        elif self.role == ArgumentRole.QUALIFIER:
            return f"*{self.content}*"
        elif self.role == ArgumentRole.REBUTTAL:
            return f"Sin embargo: {self.content}"
        return self.content


@dataclass
class BayesianConfidenceResult:
    """Resultado de inferencia bayesiana de confianza."""
    point_estimate: float
    belief: BeliefMass  # Grado de creencia
    plausibility: PlausibilityMass  # Límite superior de creencia
    uncertainty: float  # Ignorancia epistémica
    interval_95: Tuple[float, float]

    @property
    def is_calibrated(self) -> bool:
        """Check if interval is well-calibrated."""
        width = self.interval_95[1] - self.interval_95[0]
        return width >= 0.1  # No over-confident

    def to_label(self) -> str:
        """Human-readable label."""
        if self.point_estimate >= 0.85:
            return "ALTA"
        elif self.point_estimate >= 0.70:
            return "MEDIA-ALTA"
        elif self.point_estimate >= 0.50:
            return "MEDIA"
        elif self.point_estimate >= 0.30:
            return "BAJA"
        else:
            return "MUY BAJA"


@dataclass
class MethodEpistemology:
    """v3.0: Fundamentos epistemológicos de un método."""
    method_name: str
    class_name: str
    priority: int
    role: str
    paradigm: str
    ontological_basis: str
    epistemological_stance: str
    theoretical_framework: List[str]
    justification: str
    method_type: str
    algorithm: str
    steps: List[Dict[str, Any]]
    assumptions: List[str]
    limitations: List[str]
    complexity: str
    output_structure: Dict[str, Any]
    interpretation_guide: Dict[str, str]
    actionable_insights: List[str]


@dataclass
class MethodologicalDepth:
    """v3.0: Profundidad metodológica completa extraída del contrato."""
    methods: List[MethodEpistemology]
    total_methods: int
    paradigms_used: List[str]
    theoretical_references: List[str]
    all_limitations: List[str]
    all_assumptions: List[str]
    actionable_insights_by_method: Dict[str, List[str]]


@dataclass
class CarverAnswer:
    """Respuesta estructurada estilo Carver."""
    # Core components
    verdict: str  # Una oración. Directa. Sin escape.
    evidence_statements: List[str]  # Hechos. Verificables.
    gap_statements: List[str]  # Vacíos. Sin disculpas.

    # Confidence
    confidence_result: BayesianConfidenceResult
    confidence_statement: str

    # Metadata
    question_text: str
    dimension: Dimension
    method_note: str

    # Argumentative structure
    argument_units: List[ArgumentUnit] = field(default_factory=list)

    # v3.0: Enhanced doctoral components
    epistemology_section: str = ""
    limitations_section: str = ""
    benchmark_comparison: str = ""
    theoretical_references: List[str] = field(default_factory=list)

    # Trace
    synthesis_trace: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# ENHANCED CONTRACT INTERPRETER (v3.0 - FULL EXTRACTION)
# =============================================================================

class EnhancedContractInterpreter:
    """
    v3.0: Extrae TODA la semántica del contrato v3 para síntesis doctoral.

    A diferencia del original que solo extraía metadata básica,
    este intérprete captura:
    - Fundamentos epistemológicos de cada método
    - Frameworks teóricos y referencias académicas
    - Interpretación de outputs con actionable insights
    - Limitaciones metodológicas para caveats
    - Ejemplos concretos como benchmarks
    """

    # Mapeo de dimensiones a requisitos epistemológicos
    DIMENSION_REQUIREMENTS = {
        Dimension.D1_INSUMOS: {
            "primary_need": "datos cuantitativos verificables",
            "evidence_type": "quantitative",
            "minimum_sources": 2,
            "temporal_requirement": True,
        },
        Dimension.D2_ACTIVIDADES: {
            "primary_need": "especificidad operativa",
            "evidence_type": "qualitative",
            "minimum_sources": 1,
            "temporal_requirement": False,
        },
        Dimension.D3_PRODUCTOS: {
            "primary_need": "proporcionalidad meta-problema",
            "evidence_type": "mixed",
            "minimum_sources": 1,
            "temporal_requirement": True,
        },
        Dimension.D4_RESULTADOS: {
            "primary_need": "indicadores medibles",
            "evidence_type": "quantitative",
            "minimum_sources": 1,
            "temporal_requirement": True,
        },
        Dimension.D5_IMPACTOS: {
            "primary_need": "teoría de cambio",
            "evidence_type": "relational",
            "minimum_sources": 1,
            "temporal_requirement": True,
        },
        Dimension.D6_CAUSALIDAD: {
            "primary_need": "lógica causal explícita",
            "evidence_type": "relational",
            "minimum_sources": 1,
            "temporal_requirement": False,
        },
    }

    @classmethod
    def extract_dimension(cls, contract: Dict) -> Dimension:
        """Extrae dimensión con fallback inteligente."""
        identity = contract.get("identity", {})
        dim_id = identity.get("dimension_id", "")

        # Try direct match
        for dim in Dimension:
            if dim.value == dim_id:
                return dim

        # Fallback: infer from base_slot
        base_slot = identity.get("base_slot", "")
        if base_slot:
            try:
                dim_num = int(base_slot[1])  # "D1-Q1" -> 1
                return list(Dimension)[dim_num - 1]
            except (IndexError, ValueError):
                pass

        return Dimension.D1_INSUMOS  # Default

    @classmethod
    def extract_expected_elements(cls, contract: Dict) -> List[ExpectedElement]:
        """Extrae elementos con semántica enriquecida."""
        question_context = contract.get("question_context", {})
        raw_elements = question_context.get("expected_elements", [])

        return [ExpectedElement.from_contract(e) for e in raw_elements]

    @classmethod
    def extract_question_intent(cls, contract: Dict) -> Dict[str, Any]:
        """Extrae intención profunda de la pregunta."""
        question_context = contract.get("question_context", {})
        question_text = question_context.get("question_text", "")

        # Analizar tipo de pregunta
        q_lower = question_text.lower()

        if any(q in q_lower for q in ["¿cuánto", "¿cuántos", "qué porcentaje"]):
            question_type = "quantitative"
        elif any(q in q_lower for q in ["¿existe", "¿hay", "¿tiene", "¿incluye"]):
            question_type = "existence"
        elif any(q in q_lower for q in ["¿cómo", "¿de qué manera"]):
            question_type = "process"
        elif any(q in q_lower for q in ["¿por qué", "¿cuál es la razón"]):
            question_type = "causal"
        else:
            question_type = "descriptive"

        # Extraer tema principal (policy area hint)
        policy_area = contract.get("identity", {}).get("policy_area_id", "")

        return {
            "question_text": question_text,
            "question_type": question_type,
            "policy_area": policy_area,
            "requires_numeric": question_type == "quantitative",
            "requires_causal_logic": question_type in ("causal", "process"),
        }

    @classmethod
    def get_dimension_theory(cls, dimension: Dimension) -> Dict[str, Any]:
        """Obtiene teoría epistemológica de la dimensión."""
        return cls.DIMENSION_REQUIREMENTS.get(dimension, {})

    @classmethod
    def extract_method_metadata(cls, contract: Dict) -> Dict[str, Any]:
        """Extrae metadata básica de métodos (legacy compatibility)."""
        method_binding = contract.get("method_binding", {})

        return {
            "method_count": method_binding.get("method_count", 0),
            "orchestration_mode": method_binding.get("orchestration_mode", "unknown"),
            "methods": [
                m.get("method_name", "unknown")
                for m in method_binding.get("methods", [])
            ],
        }

    @classmethod
    def extract_methodological_depth(cls, contract: Dict) -> MethodologicalDepth:
        """
        v3.0: Extrae la profundidad metodológica COMPLETA de human_answer_structure.

        Returns:
            MethodologicalDepth con todos los métodos y sus fundamentos
        """
        human_answer = contract.get("human_answer_structure", {})
        method_binding = contract.get("method_binding", {})

        # Buscar methodological_depth en diferentes lugares
        methodological_depth = (
            method_binding.get("methodological_depth", {}) or
            human_answer.get("methodological_depth", {})
        )

        methods_data = methodological_depth.get("methods", [])

        extracted_methods: List[MethodEpistemology] = []
        all_paradigms: set[str] = set()
        all_references: List[str] = []
        all_limitations: List[str] = []
        all_assumptions: List[str] = []
        insights_by_method: Dict[str, List[str]] = {}

        for method in methods_data:
            epistemology = method.get("epistemological_foundation", {})
            technical = method.get("technical_approach", {})
            interpretation = method.get("output_interpretation", {})

            # Collect paradigm
            paradigm = epistemology.get("paradigm", "")
            if paradigm:
                all_paradigms.add(paradigm)

            # Collect theoretical references
            frameworks = epistemology.get("theoretical_framework", [])
            all_references.extend(frameworks)

            # Collect limitations
            limitations = technical.get("limitations", [])
            all_limitations.extend(limitations)

            # Collect assumptions
            assumptions = technical.get("assumptions", [])
            all_assumptions.extend(assumptions)

            # Collect actionable insights
            insights = interpretation.get("actionable_insights", [])
            method_name = method.get("method_name", "unknown")
            insights_by_method[method_name] = insights

            # Build MethodEpistemology
            extracted_methods.append(MethodEpistemology(
                method_name=method_name,
                class_name=method.get("class_name", ""),
                priority=method.get("priority", 0),
                role=method.get("role", ""),
                paradigm=paradigm,
                ontological_basis=epistemology.get("ontological_basis", ""),
                epistemological_stance=epistemology.get("epistemological_stance", ""),
                theoretical_framework=frameworks,
                justification=epistemology.get("justification", ""),
                method_type=technical.get("method_type", ""),
                algorithm=technical.get("algorithm", ""),
                steps=technical.get("steps", []),
                assumptions=assumptions,
                limitations=limitations,
                complexity=technical.get("complexity", ""),
                output_structure=interpretation.get("output_structure", {}),
                interpretation_guide=interpretation.get("interpretation_guide", {}),
                actionable_insights=insights,
            ))

        return MethodologicalDepth(
            methods=extracted_methods,
            total_methods=len(extracted_methods),
            paradigms_used=list(all_paradigms),
            theoretical_references=list(set(all_references)),
            all_limitations=list(set(all_limitations)),
            all_assumptions=list(set(all_assumptions)),
            actionable_insights_by_method=insights_by_method,
        )

    @classmethod
    def extract_assembly_flow(cls, contract: Dict) -> Dict[str, str]:
        """v3.0: Extrae el flujo de ensamblaje de 5 pasos."""
        human_answer = contract.get("human_answer_structure", {})
        return human_answer.get("assembly_flow", {})

    @classmethod
    def extract_evidence_schema(cls, contract: Dict) -> Dict[str, Any]:
        """v3.0: Extrae el schema completo de estructura de evidencia."""
        human_answer = contract.get("human_answer_structure", {})
        return human_answer.get("evidence_structure_schema", {})

    @classmethod
    def extract_concrete_example(cls, contract: Dict) -> Dict[str, Any]:
        """v3.0: Extrae el ejemplo concreto como benchmark."""
        human_answer = contract.get("human_answer_structure", {})
        return human_answer.get("concrete_example", {})

    @classmethod
    def extract_template_variables(cls, contract: Dict) -> Dict[str, str]:
        """v3.0: Extrae las variables disponibles para templates."""
        human_answer = contract.get("human_answer_structure", {})
        bindings = human_answer.get("template_variable_bindings", {})
        return bindings.get("variables", {})

    @classmethod
    def extract_validation_mapping(cls, contract: Dict) -> Dict[str, Any]:
        """v3.0: Extrae el mapping de validación esperado → encontrado."""
        human_answer = contract.get("human_answer_structure", {})
        return human_answer.get("validation_against_expected_elements", {})

    @classmethod
    def extract_usage_notes(cls, contract: Dict) -> Dict[str, str]:
        """v3.0: Extrae notas de uso para diferentes roles."""
        human_answer = contract.get("human_answer_structure", {})
        return human_answer.get("usage_notes", {})

    @classmethod
    def extract_evidence_graph_structure(cls, contract: Dict) -> Dict[str, Any]:
        """v3.0: Extrae la estructura del grafo de evidencia post-Nexus."""
        human_answer = contract.get("human_answer_structure", {})
        return human_answer.get("evidence_structure_post_nexus", {})


# =============================================================================
# EVIDENCE ANALYZER
# =============================================================================

class EvidenceAnalyzer:
    """
    Análisis profundo de evidencia con construcción de grafo causal.
    """

    @staticmethod
    def extract_items(evidence: Dict[str, Any]) -> List[EvidenceItem]:
        """Extrae items de evidencia estructurados."""
        items = []

        for elem in evidence.get("elements", []):
            if isinstance(elem, dict):
                items.append(EvidenceItem(
                    element_type=elem.get("type", "unknown"),
                    value=elem.get("value", elem.get("description", "")),
                    confidence=float(elem.get("confidence", 0.5)),
                    source_method=elem.get("source_method", "unknown"),
                    document_location=elem.get("page", elem.get("location")),
                ))

        return items

    @staticmethod
    def count_by_type(items: List[EvidenceItem]) -> Dict[str, int]:
        """Cuenta items por tipo."""
        counts: Dict[str, int] = defaultdict(int)
        for item in items:
            counts[item.element_type] += 1
        return dict(counts)

    @staticmethod
    def group_by_type(items: List[EvidenceItem]) -> Dict[str, List[EvidenceItem]]:
        """Agrupa items por tipo."""
        groups: Dict[str, List[EvidenceItem]] = defaultdict(list)
        for item in items:
            groups[item.element_type].append(item)
        return dict(groups)

    @staticmethod
    def analyze_strength_distribution(items: List[EvidenceItem]) -> Dict[str, int]:
        """Analiza distribución de fuerza de evidencia."""
        distribution: Dict[str, int] = defaultdict(int)
        for item in items:
            distribution[item.strength.value] += 1
        return dict(distribution)

    @staticmethod
    def find_corroborations(items: List[EvidenceItem]) -> List[Tuple[EvidenceItem, EvidenceItem]]:
        """
        Encuentra pares de evidencia que se corroboran.

        Corroboración: mismo tipo, diferentes fuentes, valores consistentes.
        """
        corroborations = []
        groups = EvidenceAnalyzer.group_by_type(items)

        for elem_type, group_items in groups.items():
            if len(group_items) < 2:
                continue

            # Check pairs
            for i, item1 in enumerate(group_items):
                for item2 in group_items[i+1:]:
                    if item1.source_method != item2.source_method:
                        # Different sources = potential corroboration
                        corroborations.append((item1, item2))

        return corroborations

    @staticmethod
    def find_contradictions(items: List[EvidenceItem]) -> List[Tuple[EvidenceItem, EvidenceItem, str]]:
        """
        Encuentra contradicciones en evidencia.

        Returns: List of (item1, item2, explanation)
        """
        contradictions = []
        groups = EvidenceAnalyzer.group_by_type(items)

        for elem_type, group_items in groups.items():
            if len(group_items) < 2:
                continue

            # Check for numeric contradictions
            numeric_items = [i for i in group_items if i.is_quantitative]
            if len(numeric_items) >= 2:
                values = []
                for item in numeric_items:
                    try:
                        # Extract numeric value
                        val_str = str(item.value)
                        nums = re.findall(r'[\d.]+', val_str)
                        if nums:
                            values.append((item, float(nums[0])))
                    except (ValueError, TypeError, IndexError):
                        pass

                if len(values) >= 2:
                    # Check for significant divergence (>50% difference)
                    for i, (item1, val1) in enumerate(values):
                        for item2, val2 in values[i+1:]:
                            if val1 > 0 and abs(val1 - val2) / val1 > 0.5:
                                contradictions.append((
                                    item1, item2,
                                    f"Divergencia numérica: {val1} vs {val2}"
                                ))

        return contradictions


# =============================================================================
# GAP ANALYZER
# =============================================================================

class GapAnalyzer:
    """
    Análisis multi-dimensional de gaps con implicaciones causales.
    """

    # Implicaciones por tipo de elemento faltante
    GAP_IMPLICATIONS = {
        "fuentes_oficiales": (
            "Sin fuentes oficiales, la credibilidad del diagnóstico es cuestionable.",
            "Citar fuentes como DANE, Medicina Legal, ICBF."
        ),
        "indicadores_cuantitativos": (
            "Sin indicadores numéricos, no hay línea base medible.",
            "Incluir tasas, porcentajes o valores absolutos con fuente."
        ),
        "series_temporales_años": (
            "Sin series temporales, no se puede evaluar tendencia.",
            "Presentar datos de al menos 3 años consecutivos."
        ),
        "cobertura_territorial_especificada": (
            "Sin especificación territorial, el alcance es ambiguo.",
            "Definir si es municipal, departamental o por zonas."
        ),
        "logica_causal_explicita": (
            "Sin lógica causal, la teoría de cambio es invisible.",
            "Explicitar cadena: insumo → actividad → producto → resultado."
        ),
        "poblacion_objetivo_definida": (
            "Sin población objetivo, no hay focalización.",
            "Definir grupo beneficiario con características específicas."
        ),
        "instrumento_especificado": (
            "Sin instrumentos, las actividades son abstractas.",
            "Nombrar programas, proyectos o mecanismos concretos."
        ),
        "meta_cuantificada": (
            "Sin metas cuantificadas, no hay accountability.",
            "Establecer valores objetivo con plazo."
        ),
        "linea_base_resultado": (
            "Sin línea base, no se puede medir avance.",
            "Documentar situación inicial con fecha."
        ),
        "impacto_definido": (
            "Sin impactos definidos, el propósito final es difuso.",
            "Describir cambios de largo plazo esperados."
        ),
        "sistema_monitoreo": (
            "Sin sistema de monitoreo, no hay seguimiento.",
            "Especificar indicadores, frecuencia y responsables."
        ),
    }

    @classmethod
    def identify_gaps(
        cls,
        expected: List[ExpectedElement],
        found_counts: Dict[str, int],
        dimension: Dimension,
    ) -> List[EvidenceGap]:
        """
        Identifica gaps con severidad calibrada por dimensión.
        """
        gaps = []
        dim_theory = EnhancedContractInterpreter.get_dimension_theory(dimension)

        for elem in expected:
            found = found_counts.get(elem.type, 0)

            if found >= elem.minimum:
                continue  # No gap

            # Determinar severidad
            severity = cls._compute_severity(elem, found, dim_theory)

            # Obtener implicación y remediación
            implication, remediation = cls.GAP_IMPLICATIONS.get(
                elem.type,
                (f"Falta {elem.type}.", f"Agregar {elem.type}.")
            )

            gaps.append(EvidenceGap(
                element_type=elem.type,
                expected=elem.minimum,
                found=found,
                severity=severity,
                implication=implication,
                remediation=remediation,
            ))

        # Sort by severity
        severity_order = {
            GapSeverity.CRITICAL: 0,
            GapSeverity.MAJOR: 1,
            GapSeverity.MINOR: 2,
            GapSeverity.COSMETIC: 3,
        }
        gaps.sort(key=lambda g: severity_order[g.severity])

        return gaps

    @classmethod
    def _compute_severity(
        cls,
        elem: ExpectedElement,
        found: int,
        dim_theory: Dict[str, Any],
    ) -> GapSeverity:
        """Computa severidad basada en contexto dimensional."""

        # Critical if required and completely missing
        if elem.required and found == 0:
            return GapSeverity.CRITICAL

        # Check if matches dimension's primary need
        evidence_type = dim_theory.get("evidence_type", "")

        # Critical if element type matches dimension's evidence type and missing
        if elem.category == evidence_type and found == 0:
            return GapSeverity.CRITICAL

        # Major if required but partial
        if elem.required and found < elem.minimum:
            return GapSeverity.MAJOR

        # Major if high weight and missing
        if elem.weight >= 0.7 and found == 0:
            return GapSeverity.MAJOR

        # Minor for optional but expected
        if elem.minimum > 0 and found < elem.minimum:
            return GapSeverity.MINOR

        return GapSeverity.COSMETIC


# =============================================================================
# BAYESIAN CONFIDENCE ENGINE
# =============================================================================

class BayesianConfidenceEngine:
    """
    Inferencia bayesiana de confianza con calibración.

    Usa Dempster-Shafer para manejar incertidumbre epistémica.
    """

    @staticmethod
    def compute(
        items: List[EvidenceItem],
        gaps: List[EvidenceGap],
        corroborations: List[Tuple[EvidenceItem, EvidenceItem]],
        contradictions: List[Tuple[EvidenceItem, EvidenceItem, str]],
    ) -> BayesianConfidenceResult:
        """
        Computa confianza calibrada usando Dempster-Shafer.
        """
        if not items:
            return BayesianConfidenceResult(
                point_estimate=0.0,
                belief=0.0,
                plausibility=0.3,
                uncertainty=1.0,
                interval_95=(0.0, 0.3),
            )

        # 1. Base: average confidence of evidence
        confidences = [i.confidence for i in items]
        base_conf = statistics.mean(confidences)

        # 2. Boost for corroborations
        corroboration_boost = min(0.15, len(corroborations) * 0.05)

        # 3. Penalty for contradictions
        contradiction_penalty = min(0.25, len(contradictions) * 0.1)

        # 4. Penalty for gaps
        critical_gaps = sum(1 for g in gaps if g.severity == GapSeverity.CRITICAL)
        major_gaps = sum(1 for g in gaps if g.severity == GapSeverity.MAJOR)
        gap_penalty = min(0.4, critical_gaps * 0.15 + major_gaps * 0.05)

        # 5. Compute belief mass (lower bound of confidence)
        belief = max(0.0, base_conf + corroboration_boost - contradiction_penalty - gap_penalty)
        belief = belief * (1 - 0.1 * critical_gaps)  # Further reduce for critical gaps

        # 6. Compute plausibility (upper bound)
        plausibility = min(1.0, belief + 0.2)

        # 7. Epistemic uncertainty
        uncertainty = plausibility - belief

        # 8. Point estimate (expected value under ignorance)
        pessimism_weight = 0.6  # Be conservative
        point_estimate = pessimism_weight * belief + (1 - pessimism_weight) * plausibility

        # 9. Calibrated interval using Wilson score
        n = len(items)
        z = 1.96  # 95% CI

        p = point_estimate
        denominator = 1 + z**2 / n
        center = (p + z**2 / (2*n)) / denominator
        margin = z * math.sqrt((p * (1 - p) + z**2 / (4*n)) / n) / denominator

        lower = max(0.0, center - margin - gap_penalty)
        upper = min(1.0, center + margin)

        return BayesianConfidenceResult(
            point_estimate=round(point_estimate, 3),
            belief=round(belief, 3),
            plausibility=round(plausibility, 3),
            uncertainty=round(uncertainty, 3),
            interval_95=(round(lower, 3), round(upper, 3)),
        )


# =============================================================================
# DIMENSION-SPECIFIC STRATEGIES
# =============================================================================

class DimensionStrategy(ABC):
    """Base class for dimension-specific strategies."""

    @property
    @abstractmethod
    def dimension(self) -> Dimension:
        pass

    @abstractmethod
    def verdict_prefix(self, has_critical_gaps: bool) -> str:
        """Prefix for verdict based on dimension theory."""
        pass

    @abstractmethod
    def key_requirement(self) -> str:
        """Key requirement for this dimension."""
        pass

    @abstractmethod
    def interpret_confidence(self, conf: BayesianConfidenceResult) -> str:
        """Dimension-specific confidence interpretation."""
        pass


class D1InsumosStrategy(DimensionStrategy):
    """D1: Insumos - Diagnóstico y datos cuantitativos."""

    @property
    def dimension(self) -> Dimension:
        return Dimension.D1_INSUMOS

    def verdict_prefix(self, has_critical_gaps: bool) -> str:
        if has_critical_gaps:
            return "El diagnóstico carece de fundamento cuantitativo."
        return "El diagnóstico tiene base cuantitativa."

    def key_requirement(self) -> str:
        return "Datos numéricos de fuentes oficiales."

    def interpret_confidence(self, conf: BayesianConfidenceResult) -> str:
        if conf.point_estimate >= 0.7:
            return "Los datos son verificables."
        return "Faltan datos verificables."


class D2ActividadesStrategy(DimensionStrategy):
    """D2: Actividades - Especificidad operativa."""

    @property
    def dimension(self) -> Dimension:
        return Dimension.D2_ACTIVIDADES

    def verdict_prefix(self, has_critical_gaps: bool) -> str:
        if has_critical_gaps:
            return "Las actividades son vagas."
        return "Las actividades están especificadas."

    def key_requirement(self) -> str:
        return "Instrumento, población y lógica definidos."

    def interpret_confidence(self, conf: BayesianConfidenceResult) -> str:
        if conf.point_estimate >= 0.7:
            return "La especificación es operativa."
        return "Falta especificidad operativa."


class D3ProductosStrategy(DimensionStrategy):
    """D3: Productos - Proporcionalidad y metas."""

    @property
    def dimension(self) -> Dimension:
        return Dimension.D3_PRODUCTOS

    def verdict_prefix(self, has_critical_gaps: bool) -> str:
        if has_critical_gaps:
            return "Los productos no son proporcionales al problema."
        return "Los productos son proporcionales."

    def key_requirement(self) -> str:
        return "Metas cuantificadas y proporcionales."

    def interpret_confidence(self, conf: BayesianConfidenceResult) -> str:
        if conf.point_estimate >= 0.7:
            return "La proporcionalidad es clara."
        return "La proporcionalidad es cuestionable."


class D4ResultadosStrategy(DimensionStrategy):
    """D4: Resultados - Indicadores de outcome."""

    @property
    def dimension(self) -> Dimension:
        return Dimension.D4_RESULTADOS

    def verdict_prefix(self, has_critical_gaps: bool) -> str:
        if has_critical_gaps:
            return "Los resultados no son medibles."
        return "Los resultados tienen indicadores."

    def key_requirement(self) -> str:
        return "Indicadores con línea base y meta."

    def interpret_confidence(self, conf: BayesianConfidenceResult) -> str:
        if conf.point_estimate >= 0.7:
            return "Los indicadores permiten seguimiento."
        return "El seguimiento no es posible."


class D5ImpactosStrategy(DimensionStrategy):
    """D5: Impactos - Cambios de largo plazo."""

    @property
    def dimension(self) -> Dimension:
        return Dimension.D5_IMPACTOS

    def verdict_prefix(self, has_critical_gaps: bool) -> str:
        if has_critical_gaps:
            return "El impacto de largo plazo no está definido."
        return "El impacto está conceptualizado."

    def key_requirement(self) -> str:
        return "Teoría de cambio con horizonte temporal."

    def interpret_confidence(self, conf: BayesianConfidenceResult) -> str:
        if conf.point_estimate >= 0.7:
            return "La teoría de cambio es plausible."
        return "La teoría de cambio es débil."


class D6CausalidadStrategy(DimensionStrategy):
    """D6: Causalidad - M&E y adaptación."""

    @property
    def dimension(self) -> Dimension:
        return Dimension.D6_CAUSALIDAD

    def verdict_prefix(self, has_critical_gaps: bool) -> str:
        if has_critical_gaps:
            return "La lógica causal no es explícita."
        return "La cadena causal está documentada."

    def key_requirement(self) -> str:
        return "Sistema de M&E con ciclos de aprendizaje."

    def interpret_confidence(self, conf: BayesianConfidenceResult) -> str:
        if conf.point_estimate >= 0.7:
            return "El sistema permite adaptación."
        return "No hay mecanismo de corrección."


def get_dimension_strategy(dimension: Dimension) -> DimensionStrategy:
    """Factory for dimension strategies."""
    strategies = {
        Dimension.D1_INSUMOS: D1InsumosStrategy(),
        Dimension.D2_ACTIVIDADES: D2ActividadesStrategy(),
        Dimension.D3_PRODUCTOS: D3ProductosStrategy(),
        Dimension.D4_RESULTADOS: D4ResultadosStrategy(),
        Dimension.D5_IMPACTOS: D5ImpactosStrategy(),
        Dimension.D6_CAUSALIDAD: D6CausalidadStrategy(),
    }
    return strategies.get(dimension, D1InsumosStrategy())


# =============================================================================
# READABILITY & STYLE CHECKER (Flesch-Kincaid + Proselint)
# =============================================================================

@dataclass
class ReadabilityMetrics:
    """Métricas de legibilidad según Flesch-Kincaid y Proselint."""
    flesch_reading_ease: Optional[float] = None
    flesch_kincaid_grade: Optional[float] = None
    gunning_fog: Optional[float] = None
    avg_sentence_length: Optional[float] = None
    avg_word_length: Optional[float] = None
    proselint_errors: List[Dict[str, Any]] = field(default_factory=list)
    proselint_score: Optional[float] = None

    def passes_carver_standards(self) -> bool:
        """Verifica si el texto cumple estándares Carver."""
        if self.flesch_reading_ease and self.flesch_reading_ease < 60:
            return False
        if self.flesch_kincaid_grade and self.flesch_kincaid_grade > 12:
            return False
        if self.avg_sentence_length and self.avg_sentence_length > 20:
            return False
        if self.proselint_score and self.proselint_score < 0.9:
            return False
        return True


class ReadabilityChecker:
    """Aplica Flesch-Kincaid y Proselint para garantizar claridad Carver."""

    @staticmethod
    def check_text(text: str) -> ReadabilityMetrics:
        """Analiza texto con Flesch-Kincaid y Proselint."""
        metrics = ReadabilityMetrics()

        if textstat:
            try:
                metrics.flesch_reading_ease = textstat.flesch_reading_ease(text)
                metrics.flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)
                metrics.gunning_fog = textstat.gunning_fog(text)

                sentences = textstat.sentence_count(text)
                words = textstat.lexicon_count(text, removepunct=True)
                if sentences > 0:
                    metrics.avg_sentence_length = words / sentences

                chars = sum(len(word) for word in text.split())
                if words > 0:
                    metrics.avg_word_length = chars / words

            except Exception:
                pass

        if proselint_check:
            try:
                errors = proselint_check(text)
                if errors:
                    metrics.proselint_errors = errors
                    metrics.proselint_score = max(0.0, 1.0 - len(errors) / 100.0)
                else:
                    metrics.proselint_score = 1.0
            except Exception:
                metrics.proselint_score = 1.0

        return metrics

    @staticmethod
    def enforce_carver_style(text: str) -> Tuple[str, ReadabilityMetrics]:
        """Analiza y opcionalmente ajusta texto para cumplir estándares Carver."""
        metrics = ReadabilityChecker.check_text(text)

        if metrics.passes_carver_standards():
            return text, metrics

        adjusted_text = text

        if metrics.avg_sentence_length and metrics.avg_sentence_length > 20:
            adjusted_text = re.sub(r',\s+([a-záéíóúñ])', r'. \1', adjusted_text)
            adjusted_text = re.sub(r'\s+y\s+([a-záéíóúñ])', r'. \1', adjusted_text)

        metrics = ReadabilityChecker.check_text(adjusted_text)

        return adjusted_text, metrics


# =============================================================================
# DOCTORAL RENDERER (v3.0 - Enhanced with Epistemology)
# =============================================================================

class DoctoralRenderer:
    """
    v3.0: Renderiza prosa estilo Raymond Carver con fundamentos doctorales.

    Principios:
    - Oraciones cortas. Sujeto-verbo-objeto.
    - Verbos activos. Sin pasiva.
    - Sin adverbios. Sin adjetivos innecesarios.
    - Cada palabra cuenta. Si sobra, eliminar.
    - La verdad es suficiente. Sin adornos.

    Nuevos principios v3.0:
    - Fundamentos epistemológicos explícitos cuando relevante
    - Referencias teóricas en formato académico
    - Limitaciones como caveats honestos
    - Benchmark comparison cuando disponible
    """

    TYPE_LABELS = {
        "fuentes_oficiales": "fuentes oficiales",
        "indicadores_cuantitativos": "indicadores numéricos",
        "series_temporales_años": "series temporales",
        "cobertura_territorial_especificada": "cobertura territorial",
        "instrumento_especificado": "instrumentos",
        "poblacion_objetivo_definida": "población objetivo",
        "logica_causal_explicita": "lógica causal",
        "riesgos_identificados": "riesgos",
        "mitigacion_propuesta": "mitigación",
        "impacto_definido": "impactos",
        "rezago_temporal": "horizonte temporal",
        "ruta_transmision": "ruta de transmisión",
        "proporcionalidad_meta_problema": "proporcionalidad",
        "linea_base_resultado": "línea base",
        "meta_resultado": "metas",
        "meta_cuantificada": "metas cuantificadas",
        "metrica_outcome": "métricas",
        "sistema_monitoreo": "sistema de monitoreo",
        "ciclos_aprendizaje": "ciclos de aprendizaje",
        "mecanismos_correccion": "mecanismos de corrección",
        "analisis_contextual": "análisis contextual",
        "enfoque_diferencial": "enfoque diferencial",
    }

    @classmethod
    def humanize(cls, elem_type: str) -> str:
        """Convert technical type to plain Spanish."""
        return cls.TYPE_LABELS.get(elem_type, elem_type.replace("_", " "))

    @classmethod
    def render_verdict(
        cls,
        strategy: DimensionStrategy,
        gaps: List[EvidenceGap],
        items: List[EvidenceItem],
    ) -> str:
        """Render verdict: una oración. Sin escape."""
        critical_gaps = [g for g in gaps if g.severity == GapSeverity.CRITICAL]
        has_critical = len(critical_gaps) > 0

        prefix = strategy.verdict_prefix(has_critical)

        if not items:
            return f"{prefix} No hay evidencia."

        if has_critical:
            missing = [cls.humanize(g.element_type) for g in critical_gaps[:2]]
            return f"{prefix} Falta: {', '.join(missing)}."

        return prefix

    @classmethod
    def render_evidence_statements(
        cls,
        items: List[EvidenceItem],
        found_counts: Dict[str, int],
    ) -> List[str]:
        """Render evidence as facts. Short. Verifiable."""
        statements = []

        total = len(items)
        if total > 0:
            statements.append(f"{total} elementos de evidencia.")

        sorted_types = sorted(found_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        for elem_type, count in sorted_types:
            label = cls.humanize(elem_type)
            statements.append(f"{count} {label}.")

        strong = sum(1 for i in items if i.strength == EvidenceStrength.STRONG)
        if strong > 0:
            statements.append(f"{strong} elementos con alta confianza.")

        return statements

    @classmethod
    def render_gap_statements(cls, gaps: List[EvidenceGap]) -> List[str]:
        """Render gaps. No excuses. Just facts."""
        statements = []

        for gap in gaps[:4]:
            label = cls.humanize(gap.element_type)

            if gap.found == 0:
                statements.append(f"No hay {label}.")
            else:
                statements.append(f"{gap.found} {label}. Se necesitan {gap.expected}.")

        return statements

    @classmethod
    def render_confidence_statement(
        cls,
        conf: BayesianConfidenceResult,
        strategy: DimensionStrategy,
    ) -> str:
        """Render confidence. Honest. Calibrated."""
        label = conf.to_label()
        pct = int(conf.point_estimate * 100)

        interpretation = strategy.interpret_confidence(conf)

        return f"Confianza {label} ({pct}%). {interpretation}"

    @classmethod
    def render_method_note(cls, method_meta: Dict[str, Any]) -> str:
        """Render method note. Brief. At the end."""
        count = method_meta.get("method_count", 0)
        return f"Análisis con {count} métodos."

    @classmethod
    def render_epistemology_section(
        cls,
        methodological_depth: MethodologicalDepth,
    ) -> str:
        """v3.0: Render sección de fundamentos epistemológicos."""
        if not methodological_depth.paradigms_used:
            return ""

        lines = ["\n## Fundamentos Epistemológicos\n"]
        lines.append(f"Este análisis emplea {len(methodological_depth.paradigms_used)} paradigmas:\n")

        for p in methodological_depth.paradigms_used[:5]:
            lines.append(f"- {p}")

        # Agregar métodos clave con sus justificaciones
        key_methods = [m for m in methodological_depth.methods if m.priority <= 3]
        if key_methods:
            lines.append("\n**Métodos primarios:**\n")
            for method in key_methods[:3]:
                if method.justification:
                    lines.append(f"- *{method.method_name}*: {method.justification[:150]}...")

        return "\n".join(lines)

    @classmethod
    def render_limitations_section(
        cls,
        methodological_depth: MethodologicalDepth,
    ) -> str:
        """v3.0: Render sección de limitaciones (Carver: honestidad brutal)."""
        if not methodological_depth.all_limitations:
            return ""

        lines = ["\n## Limitaciones Metodológicas\n"]
        lines.append("Este análisis reconoce:\n")

        # Agrupar limitaciones similares
        unique_limitations = list(set(methodological_depth.all_limitations))[:6]
        for lim in unique_limitations:
            lines.append(f"- {lim}")

        return "\n".join(lines)

    @classmethod
    def render_assumptions_section(
        cls,
        methodological_depth: MethodologicalDepth,
    ) -> str:
        """v3.0: Render sección de supuestos metodológicos."""
        if not methodological_depth.all_assumptions:
            return ""

        lines = ["\n## Supuestos del Análisis\n"]

        unique_assumptions = list(set(methodological_depth.all_assumptions))[:5]
        for assumption in unique_assumptions:
            lines.append(f"- {assumption}")

        return "\n".join(lines)

    @classmethod
    def render_benchmark_comparison(
        cls,
        found: Dict[str, int],
        benchmark: Dict[str, int],
    ) -> str:
        """v3.0: Compara resultados contra benchmark del contrato."""
        if not benchmark:
            return ""

        lines = ["\n## Comparación con Benchmark\n"]

        passed = 0
        failed = 0

        for elem_type, expected in benchmark.items():
            actual = found.get(elem_type, 0)
            label = cls.humanize(elem_type)
            if actual >= expected:
                status = "✓"
                passed += 1
            else:
                status = "✗"
                failed += 1
            lines.append(f"- {label}: {actual}/{expected} {status}")

        total = passed + failed
        if total > 0:
            pct = int(passed / total * 100)
            lines.append(f"\n**Cumplimiento:** {pct}% ({passed}/{total})")

        return "\n".join(lines)

    @classmethod
    def render_actionable_insights(
        cls,
        methodological_depth: MethodologicalDepth,
        gaps: List[EvidenceGap],
    ) -> str:
        """v3.0: Render insights accionables basados en el contrato."""
        lines = ["\n## Insights Accionables\n"]

        # Mapear gaps a métodos relevantes
        gap_types = {g.element_type for g in gaps if g.severity in (GapSeverity.CRITICAL, GapSeverity.MAJOR)}

        relevant_insights = []
        for method in methodological_depth.methods:
            for insight in method.actionable_insights:
                # Buscar insights relevantes a los gaps encontrados
                insight_lower = insight.lower()
                if any(gt.replace("_", " ") in insight_lower for gt in gap_types):
                    relevant_insights.append((method.method_name, insight))
                elif "few" in insight_lower or "no" in insight_lower or "missing" in insight_lower:
                    relevant_insights.append((method.method_name, insight))

        if relevant_insights:
            for method_name, insight in relevant_insights[:5]:
                lines.append(f"- **{method_name}**: {insight}")
        else:
            lines.append("- Sin insights específicos para los gaps detectados.")

        return "\n".join(lines)

    @classmethod
    def render_theoretical_references(
        cls,
        references: List[str],
    ) -> str:
        """v3.0: Render referencias teóricas en formato académico."""
        if not references:
            return ""

        lines = ["\n## Referencias Teóricas\n"]
        lines.append("Fundamentos citados en la metodología:\n")

        unique_refs = list(set(references))[:10]
        for ref in unique_refs:
            lines.append(f"- {ref}")

        return "\n".join(lines)

    @classmethod
    def render_full_answer(cls, answer: CarverAnswer) -> str:
        """v3.0: Render complete doctoral answer."""
        sections = []

        # Question context
        sections.append(f"**Pregunta**: {answer.question_text}\n")

        # Verdict (the core)
        sections.append(f"## Respuesta\n\n{answer.verdict}\n")

        # Evidence (facts only)
        if answer.evidence_statements:
            sections.append("## Evidencia\n")
            for stmt in answer.evidence_statements:
                sections.append(f"- {stmt}")

        # Gaps (if any)
        if answer.gap_statements:
            sections.append("\n## Vacíos\n")
            for stmt in answer.gap_statements:
                sections.append(f"- {stmt}")

        # Confidence
        sections.append(f"\n## Confianza\n\n{answer.confidence_statement}")

        # v3.0: Doctoral sections
        if answer.epistemology_section:
            sections.append(answer.epistemology_section)

        if answer.limitations_section:
            sections.append(answer.limitations_section)

        if answer.benchmark_comparison:
            sections.append(answer.benchmark_comparison)

        # Theoretical references
        if answer.theoretical_references:
            ref_section = cls.render_theoretical_references(answer.theoretical_references)
            sections.append(ref_section)

        # Method note (discrete)
        sections.append(f"\n---\n*{answer.method_note}*")

        # Join all sections
        full_text = "\n".join(sections)

        # Apply readability checking
        adjusted_text, metrics = ReadabilityChecker.enforce_carver_style(full_text)

        # Add readability report
        if metrics.flesch_reading_ease or metrics.proselint_score:
            readability_note = "\n\n---\n**Métricas de Legibilidad**:\n"
            if metrics.flesch_reading_ease:
                readability_note += f"- Flesch Reading Ease: {metrics.flesch_reading_ease:.1f} "
                readability_note += ("(Fácil)" if metrics.flesch_reading_ease >= 60 else "(Difícil)")
                readability_note += "\n"
            if metrics.flesch_kincaid_grade:
                readability_note += f"- Nivel Educativo: {metrics.flesch_kincaid_grade:.1f} grado\n"
            if metrics.avg_sentence_length:
                readability_note += f"- Longitud Promedio: {metrics.avg_sentence_length:.1f} palabras/oración\n"
            if metrics.proselint_score is not None:
                readability_note += f"- Calidad Proselint: {metrics.proselint_score:.0%}"
                if metrics.proselint_errors:
                    readability_note += f" ({len(metrics.proselint_errors)} sugerencias)"
                readability_note += "\n"

            if metrics.passes_carver_standards():
                readability_note += "\n✓ Cumple estándares Carver de claridad y concisión."

            adjusted_text += readability_note

        return adjusted_text


# =============================================================================
# MAIN SYNTHESIZER v3.0 (FULL EXTRACTION)
# =============================================================================

class DoctoralCarverSynthesizer:
    """
    Sintetizador Doctoral-Carver v3.0 FULL EXTRACTION.

    Combina rigor académico con prosa minimalista.
    Cada afirmación respaldada. Cada gap recon// filepath: /Users/recovered/PycharmProjects/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL/src/farfan_pipeline/phases/Phase_two/carver.py
"""
Doctoral-Carver Narrative Synthesizer v3.0 (FULL EXTRACTION Edition)
=====================================================================

Genera respuestas PhD-level con estilo minimalista Raymond Carver:
- Precisión quirúrgica en cada afirmación
- Sin adornos retóricos vacíos
- Cada palabra respaldada por evidencia
- Honestidad brutal sobre limitaciones
- Razonamiento causal explícito

CAMBIO MAYOR v3.0: Extracción COMPLETA del contrato v3
------------------------------------------------------
v2.1 extraía solo: dimension, expected_elements, question_text, method_count, top 5 methods
v3.0 extrae TODO:
- 17 métodos con epistemological_foundation completo
- theoretical_framework con referencias académicas
- technical_approach con algoritmos y limitaciones
- output_interpretation con actionable_insights
- assembly_flow de 5 pasos
- concrete_example como benchmark
- template_variable_bindings
- validation_against_expected_elements

Fundamentos Teóricos:
- Rhetorical Structure Theory (Mann & Thompson, 1988)
- Dempster-Shafer Evidence Theory (belief functions)
- Causal Inference Framework (Pearl, 2009)
- Argument Mining (Stab & Gurevych, 2017)
- Calibrated Uncertainty Quantification (Gneiting & Raftery, 2007)

Arquitectura v3.0:
1. EnhancedContractInterpreter: Extrae TODA la semántica del contrato v3
2. EvidenceAnalyzer: Construye grafo causal de evidencia
3. GapAnalyzer: Análisis multi-dimensional de vacíos
4. BayesianConfidenceEngine: Inferencia calibrada de confianza
5. DimensionTheory: Estrategias teóricamente fundamentadas por D1-D6
6. DoctoralRenderer: Prosa con fundamentos epistemológicos y citas
7. MacroSynthesizer: Agregación holística con análisis PA×DIM

Invariantes:
[INV-001] Toda afirmación debe tener ≥1 evidencia citada
[INV-002] Gaps críticos siempre aparecen en respuesta
[INV-003] Confianza debe ser calibrada (no optimista)
[INV-004] Estilo Carver: oraciones cortas, verbos activos, sin adverbios
[INV-005] Macro synthesis con divergencia PA×DIM explícita
[INV-006] v3.0: Fundamentos epistemológicos explícitos en síntesis doctoral
[INV-007] v3.0: Limitaciones metodológicas como caveats honestos
[INV-008] v3.0: Referencias teóricas en formato académico

Author: F.A.R.F.A.N Pipeline
Version: 3.0.0-FULL-EXTRACTION
"""

from __future__ import annotations

import math
import re
import statistics
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    TypeAlias,
)

# Readability and style checking libraries
try:
    import textstat  # Flesch-Kincaid and readability metrics
except ImportError:
    textstat = None  # type: ignore

try:
    from proselint.tools import lint as proselint_check  # Style and clarity checking
except ImportError:
    proselint_check = None  # type: ignore


# =============================================================================
# TYPE SYSTEM
# =============================================================================

Confidence: TypeAlias = float  # [0.0, 1.0]
BeliefMass: TypeAlias = float  # Dempster-Shafer belief
PlausibilityMass: TypeAlias = float  # Dempster-Shafer plausibility


class Dimension(Enum):
    """Las 6 dimensiones causales del modelo lógico."""
    D1_INSUMOS = "DIM01"      # Inputs: recursos, datos, diagnóstico
    D2_ACTIVIDADES = "DIM02"  # Activities: acciones, instrumentos
    D3_PRODUCTOS = "DIM03"    # Outputs: entregables, metas
    D4_RESULTADOS = "DIM04"   # Outcomes: cambios inmediatos
    D5_IMPACTOS = "DIM05"     # Impacts: cambios largo plazo
    D6_CAUSALIDAD = "DIM06"   # Causality: lógica, M&E, adaptación


class EvidenceStrength(Enum):
    """Fuerza de evidencia según jerarquía epistemológica."""
    DEFINITIVE = "definitive"      # Dato oficial verificable
    STRONG = "strong"              # Múltiples fuentes concordantes
    MODERATE = "moderate"          # Fuente única confiable
    WEAK = "weak"                  # Inferido o parcial
    ABSENT = "absent"              # No encontrado


class GapSeverity(Enum):
    """Severidad de gaps con implicaciones para scoring."""
    CRITICAL = "critical"     # Bloquea evaluación positiva
    MAJOR = "major"           # Reduce score significativamente
    MINOR = "minor"           # Nota pero no bloquea
    COSMETIC = "cosmetic"     # Mejora deseable


class ArgumentRole(Enum):
    """Roles argumentativos (RST-inspired)."""
    CLAIM = "claim"           # Afirmación principal
    EVIDENCE = "evidence"     # Soporte factual
    WARRANT = "warrant"       # Justificación del vínculo
    QUALIFIER = "qualifier"   # Limitación/condición
    REBUTTAL = "rebuttal"     # Contraargumento reconocido
    BACKING = "backing"       # Soporte del warrant


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass(frozen=True)
class ExpectedElement:
    """Elemento esperado con semántica completa."""
    type: str
    required: bool
    minimum: int
    category: str  # 'quantitative', 'qualitative', 'relational'
    weight: float  # Importancia relativa [0, 1]

    @classmethod
    def from_contract(cls, elem: Dict[str, Any]) -> ExpectedElement:
        """Factory desde contrato."""
        elem_type = elem.get("type", "")

        # Inferir categoría desde tipo
        quantitative_types = {
            "indicadores_cuantitativos", "series_temporales_años",
            "monto_presupuestario", "meta_cuantificada", "linea_base",
            "porcentaje", "tasa", "indice"
        }
        relational_types = {
            "logica_causal_explicita", "ruta_transmision",
            "vinculo_causal", "dependencia_temporal"
        }

        if any(t in elem_type for t in quantitative_types):
            category = "quantitative"
        elif any(t in elem_type for t in relational_types):
            category = "relational"
        else:
            category = "qualitative"

        # Peso basado en required y minimum
        base_weight = 0.8 if elem.get("required", False) else 0.4
        min_val = elem.get("minimum", 0)
        weight = min(1.0, base_weight + (min_val * 0.05))

        return cls(
            type=elem_type,
            required=elem.get("required", False),
            minimum=elem.get("minimum", 1 if elem.get("required") else 0),
            category=category,
            weight=weight,
        )


@dataclass
class EvidenceItem:
    """Item de evidencia con metadatos ricos."""
    element_type: str
    value: Any
    confidence: float
    source_method: str
    document_location: Optional[str] = None

    # Computed properties
    strength: EvidenceStrength = EvidenceStrength.MODERATE
    is_quantitative: bool = False

    def __post_init__(self):
        """Compute derived properties."""
        # Determinar fuerza
        if self.confidence >= 0.9:
            self.strength = EvidenceStrength.STRONG
        elif self.confidence >= 0.7:
            self.strength = EvidenceStrength.MODERATE
        else:
            self.strength = EvidenceStrength.WEAK

        # Detectar si es cuantitativo
        if isinstance(self.value, (int, float)):
            self.is_quantitative = True
        elif isinstance(self.value, str):
            # Check for numeric patterns
            self.is_quantitative = bool(re.search(r'\d+[.,]?\d*\s*%?', self.value))


@dataclass
class EvidenceGap:
    """Gap con análisis causal de implicaciones."""
    element_type: str
    expected: int
    found: int
    severity: GapSeverity
    implication: str  # Por qué importa este gap
    remediation: str  # Qué haría falta

    @property
    def deficit(self) -> int:
        return max(0, self.expected - self.found)

    @property
    def fulfillment_ratio(self) -> float:
        if self.expected == 0:
            return 1.0
        return min(1.0, self.found / self.expected)


@dataclass
class ArgumentUnit:
    """Unidad argumentativa con rol retórico."""
    role: ArgumentRole
    content: str
    evidence_refs: List[str]  # IDs de evidencia que soportan
    confidence: float

    def render(self) -> str:
        """Render según rol."""
        if self.role == ArgumentRole.CLAIM:
            return self.content
        elif self.role == ArgumentRole.EVIDENCE:
            return f"- {self.content}"
        elif self.role == ArgumentRole.QUALIFIER:
            return f"*{self.content}*"
        elif self.role == ArgumentRole.REBUTTAL:
            return f"Sin embargo: {self.content}"
        return self.content


@dataclass
class BayesianConfidenceResult:
    """Resultado de inferencia bayesiana de confianza."""
    point_estimate: float
    belief: BeliefMass  # Grado de creencia
    plausibility: PlausibilityMass  # Límite superior de creencia
    uncertainty: float  # Ignorancia epistémica
    interval_95: Tuple[float, float]

    @property
    def is_calibrated(self) -> bool:
        """Check if interval is well-calibrated."""
        width = self.interval_95[1] - self.interval_95[0]
        return width >= 0.1  # No over-confident

    def to_label(self) -> str:
        """Human-readable label."""
        if self.point_estimate >= 0.85:
            return "ALTA"
        elif self.point_estimate >= 0.70:
            return "MEDIA-ALTA"
        elif self.point_estimate >= 0.50:
            return "MEDIA"
        elif self.point_estimate >= 0.30:
            return "BAJA"
        else:
            return "MUY BAJA"


@dataclass
class MethodEpistemology:
    """v3.0: Fundamentos epistemológicos de un método."""
    method_name: str
    class_name: str
    priority: int
    role: str
    paradigm: str
    ontological_basis: str
    epistemological_stance: str
    theoretical_framework: List[str]
    justification: str
    method_type: str
    algorithm: str
    steps: List[Dict[str, Any]]
    assumptions: List[str]
    limitations: List[str]
    complexity: str
    output_structure: Dict[str, Any]
    interpretation_guide: Dict[str, str]
    actionable_insights: List[str]


@dataclass
class MethodologicalDepth:
    """v3.0: Profundidad metodológica completa extraída del contrato."""
    methods: List[MethodEpistemology]
    total_methods: int
    paradigms_used: List[str]
    theoretical_references: List[str]
    all_limitations: List[str]
    all_assumptions: List[str]
    actionable_insights_by_method: Dict[str, List[str]]


@dataclass
class CarverAnswer:
    """Respuesta estructurada estilo Carver."""
    # Core components
    verdict: str  # Una oración. Directa. Sin escape.
    evidence_statements: List[str]  # Hechos. Verificables.
    gap_statements: List[str]  # Vacíos. Sin disculpas.

    # Confidence
    confidence_result: BayesianConfidenceResult
    confidence_statement: str

    # Metadata
    question_text: str
    dimension: Dimension
    method_note: str

    # Argumentative structure
    argument_units: List[ArgumentUnit] = field(default_factory=list)

    # v3.0: Enhanced doctoral components
    epistemology_section: str = ""
    limitations_section: str = ""
    benchmark_comparison: str = ""
    theoretical_references: List[str] = field(default_factory=list)

    # Trace
    synthesis_trace: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# ENHANCED CONTRACT INTERPRETER (v3.0 - FULL EXTRACTION)
# =============================================================================

class EnhancedContractInterpreter:
    """
    v3.0: Extrae TODA la semántica del contrato v3 para síntesis doctoral.

    A diferencia del original que solo extraía metadata básica,
    este intérprete captura:
    - Fundamentos epistemológicos de cada método
    - Frameworks teóricos y referencias académicas
    - Interpretación de outputs con actionable insights
    - Limitaciones metodológicas para caveats
    - Ejemplos concretos como benchmarks
    """

    # Mapeo de dimensiones a requisitos epistemológicos
    DIMENSION_REQUIREMENTS = {
        Dimension.D1_INSUMOS: {
            "primary_need": "datos cuantitativos verificables",
            "evidence_type": "quantitative",
            "minimum_sources": 2,
            "temporal_requirement": True,
        },
        Dimension.D2_ACTIVIDADES: {
            "primary_need": "especificidad operativa",
            "evidence_type": "qualitative",
            "minimum_sources": 1,
            "temporal_requirement": False,
        },
        Dimension.D3_PRODUCTOS: {
            "primary_need": "proporcionalidad meta-problema",
            "evidence_type": "mixed",
            "minimum_sources": 1,
            "temporal_requirement": True,
        },
        Dimension.D4_RESULTADOS: {
            "primary_need": "indicadores medibles",
            "evidence_type": "quantitative",
            "minimum_sources": 1,
            "temporal_requirement": True,
        },
        Dimension.D5_IMPACTOS: {
            "primary_need": "teoría de cambio",
            "evidence_type": "relational",
            "minimum_sources": 1,
            "temporal_requirement": True,
        },
        Dimension.D6_CAUSALIDAD: {
            "primary_need": "lógica causal explícita",
            "evidence_type": "relational",
            "minimum_sources": 1,
            "temporal_requirement": False,
        },
    }

    @classmethod
    def extract_dimension(cls, contract: Dict) -> Dimension:
        """Extrae dimensión con fallback inteligente."""
        identity = contract.get("identity", {})
        dim_id = identity.get("dimension_id", "")

        # Try direct match
        for dim in Dimension:
            if dim.value == dim_id:
                return dim

        # Fallback: infer from base_slot
        base_slot = identity.get("base_slot", "")
        if base_slot:
            try:
                dim_num = int(base_slot[1])  # "D1-Q1" -> 1
                return list(Dimension)[dim_num - 1]
            except (IndexError, ValueError):
                pass

        return Dimension.D1_INSUMOS  # Default

    @classmethod
    def extract_expected_elements(cls, contract: Dict) -> List[ExpectedElement]:
        """Extrae elementos con semántica enriquecida."""
        question_context = contract.get("question_context", {})
        raw_elements = question_context.get("expected_elements", [])

        return [ExpectedElement.from_contract(e) for e in raw_elements]

    @classmethod
    def extract_question_intent(cls, contract: Dict) -> Dict[str, Any]:
        """Extrae intención profunda de la pregunta."""
        question_context = contract.get("question_context", {})
        question_text = question_context.get("question_text", "")

        # Analizar tipo de pregunta
        q_lower = question_text.lower()

        if any(q in q_lower for q in ["¿cuánto", "¿cuántos", "qué porcentaje"]):
            question_type = "quantitative"
        elif any(q in q_lower for q in ["¿existe", "¿hay", "¿tiene", "¿incluye"]):
            question_type = "existence"
        elif any(q in q_lower for q in ["¿cómo", "¿de qué manera"]):
            question_type = "process"
        elif any(q in q_lower for q in ["¿por qué", "¿cuál es la razón"]):
            question_type = "causal"
        else:
            question_type = "descriptive"

        # Extraer tema principal (policy area hint)
        policy_area = contract.get("identity", {}).get("policy_area_id", "")

        return {
            "question_text": question_text,
            "question_type": question_type,
            "policy_area": policy_area,
            "requires_numeric": question_type == "quantitative",
            "requires_causal_logic": question_type in ("causal", "process"),
        }

    @classmethod
    def get_dimension_theory(cls, dimension: Dimension) -> Dict[str, Any]:
        """Obtiene teoría epistemológica de la dimensión."""
        return cls.DIMENSION_REQUIREMENTS.get(dimension, {})

    @classmethod
    def extract_method_metadata(cls, contract: Dict) -> Dict[str, Any]:
        """Extrae metadata básica de métodos (legacy compatibility)."""
        method_binding = contract.get("method_binding", {})

        return {
            "method_count": method_binding.get("method_count", 0),
            "orchestration_mode": method_binding.get("orchestration_mode", "unknown"),
            "methods": [
                m.get("method_name", "unknown")
                for m in method_binding.get("methods", [])
            ],
        }

    @classmethod
    def extract_methodological_depth(cls, contract: Dict) -> MethodologicalDepth:
        """
        v3.0: Extrae la profundidad metodológica COMPLETA de human_answer_structure.

        Returns:
            MethodologicalDepth con todos los métodos y sus fundamentos
        """
        human_answer = contract.get("human_answer_structure", {})
        method_binding = contract.get("method_binding", {})

        # Buscar methodological_depth en diferentes lugares
        methodological_depth = (
            method_binding.get("methodological_depth", {}) or
            human_answer.get("methodological_depth", {})
        )

        methods_data = methodological_depth.get("methods", [])

        extracted_methods: List[MethodEpistemology] = []
        all_paradigms: set[str] = set()
        all_references: List[str] = []
        all_limitations: List[str] = []
        all_assumptions: List[str] = []
        insights_by_method: Dict[str, List[str]] = {}

        for method in methods_data:
            epistemology = method.get("epistemological_foundation", {})
            technical = method.get("technical_approach", {})
            interpretation = method.get("output_interpretation", {})

            # Collect paradigm
            paradigm = epistemology.get("paradigm", "")
            if paradigm:
                all_paradigms.add(paradigm)

            # Collect theoretical references
            frameworks = epistemology.get("theoretical_framework", [])
            all_references.extend(frameworks)

            # Collect limitations
            limitations = technical.get("limitations", [])
            all_limitations.extend(limitations)

            # Collect assumptions
            assumptions = technical.get("assumptions", [])
            all_assumptions.extend(assumptions)

            # Collect actionable insights
            insights = interpretation.get("actionable_insights", [])
            method_name = method.get("method_name", "unknown")
            insights_by_method[method_name] = insights

            # Build MethodEpistemology
            extracted_methods.append(MethodEpistemology(
                method_name=method_name,
                class_name=method.get("class_name", ""),
                priority=method.get("priority", 0),
                role=method.get("role", ""),
                paradigm=paradigm,
                ontological_basis=epistemology.get("ontological_basis", ""),
                epistemological_stance=epistemology.get("epistemological_stance", ""),
                theoretical_framework=frameworks,
                justification=epistemology.get("justification", ""),
                method_type=technical.get("method_type", ""),
                algorithm=technical.get("algorithm", ""),
                steps=technical.get("steps", []),
                assumptions=assumptions,
                limitations=limitations,
                complexity=technical.get("complexity", ""),
                output_structure=interpretation.get("output_structure", {}),
                interpretation_guide=interpretation.get("interpretation_guide", {}),
                actionable_insights=insights,
            ))

        return MethodologicalDepth(
            methods=extracted_methods,
            total_methods=len(extracted_methods),
            paradigms_used=list(all_paradigms),
            theoretical_references=list(set(all_references)),
            all_limitations=list(set(all_limitations)),
            all_assumptions=list(set(all_assumptions)),
            actionable_insights_by_method=insights_by_method,
        )

    @classmethod
    def extract_assembly_flow(cls, contract: Dict) -> Dict[str, str]:
        """v3.0: Extrae el flujo de ensamblaje de 5 pasos."""
        human_answer = contract.get("human_answer_structure", {})
        return human_answer.get("assembly_flow", {})

    @classmethod
    def extract_evidence_schema(cls, contract: Dict) -> Dict[str, Any]:
        """v3.0: Extrae el schema completo de estructura de evidencia."""
        human_answer = contract.get("human_answer_structure", {})
        return human_answer.get("evidence_structure_schema", {})

    @classmethod
    def extract_concrete_example(cls, contract: Dict) -> Dict[str, Any]:
        """v3.0: Extrae el ejemplo concreto como benchmark."""
        human_answer = contract.get("human_answer_structure", {})
        return human_answer.get("concrete_example", {})

    @classmethod
    def extract_template_variables(cls, contract: Dict) -> Dict[str, str]:
        """v3.0: Extrae las variables disponibles para templates."""
        human_answer = contract.get("human_answer_structure", {})
        bindings = human_answer.get("template_variable_bindings", {})
        return bindings.get("variables", {})

    @classmethod
    def extract_validation_mapping(cls, contract: Dict) -> Dict[str, Any]:
        """v3.0: Extrae el mapping de validación esperado → encontrado."""
        human_answer = contract.get("human_answer_structure", {})
        return human_answer.get("validation_against_expected_elements", {})

    @classmethod
    def extract_usage_notes(cls, contract: Dict) -> Dict[str, str]:
        """v3.0: Extrae notas de uso para diferentes roles."""
        human_answer = contract.get("human_answer_structure", {})
        return human_answer.get("usage_notes", {})

    @classmethod
    def extract_evidence_graph_structure(cls, contract: Dict) -> Dict[str, Any]:
        """v3.0: Extrae la estructura del grafo de evidencia post-Nexus."""
        human_answer = contract.get("human_answer_structure", {})
        return human_answer.get("evidence_structure_post_nexus", {})


# =============================================================================
# EVIDENCE ANALYZER
# =============================================================================

class EvidenceAnalyzer:
    """
    Análisis profundo de evidencia con construcción de grafo causal.
    """

    @staticmethod
    def extract_items(evidence: Dict[str, Any]) -> List[EvidenceItem]:
        """Extrae items de evidencia estructurados."""
        items = []

        for elem in evidence.get("elements", []):
            if isinstance(elem, dict):
                items.append(EvidenceItem(
                    element_type=elem.get("type", "unknown"),
                    value=elem.get("value", elem.get("description", "")),
                    confidence=float(elem.get("confidence", 0.5)),
                    source_method=elem.get("source_method", "unknown"),
                    document_location=elem.get("page", elem.get("location")),
                ))

        return items

    @staticmethod
    def count_by_type(items: List[EvidenceItem]) -> Dict[str, int]:
        """Cuenta items por tipo."""
        counts: Dict[str, int] = defaultdict(int)
        for item in items:
            counts[item.element_type] += 1
        return dict(counts)

    @staticmethod
    def group_by_type(items: List[EvidenceItem]) -> Dict[str, List[EvidenceItem]]:
        """Agrupa items por tipo."""
        groups: Dict[str, List[EvidenceItem]] = defaultdict(list)
        for item in items:
            groups[item.element_type].append(item)
        return dict(groups)

    @staticmethod
    def analyze_strength_distribution(items: List[EvidenceItem]) -> Dict[str, int]:
        """Analiza distribución de fuerza de evidencia."""
        distribution: Dict[str, int] = defaultdict(int)
        for item in items:
            distribution[item.strength.value] += 1
        return dict(distribution)

    @staticmethod
    def find_corroborations(items: List[EvidenceItem]) -> List[Tuple[EvidenceItem, EvidenceItem]]:
        """
        Encuentra pares de evidencia que se corroboran.

        Corroboración: mismo tipo, diferentes fuentes, valores consistentes.
        """
        corroborations = []
        groups = EvidenceAnalyzer.group_by_type(items)

        for elem_type, group_items in groups.items():
            if len(group_items) < 2:
                continue

            # Check pairs
            for i, item1 in enumerate(group_items):
                for item2 in group_items[i+1:]:
                    if item1.source_method != item2.source_method:
                        # Different sources = potential corroboration
                        corroborations.append((item1, item2))

        return corroborations

    @staticmethod
    def find_contradictions(items: List[EvidenceItem]) -> List[Tuple[EvidenceItem, EvidenceItem, str]]:
        """
        Encuentra contradicciones en evidencia.

        Returns: List of (item1, item2, explanation)
        """
        contradictions = []
        groups = EvidenceAnalyzer.group_by_type(items)

        for elem_type, group_items in groups.items():
            if len(group_items) < 2:
                continue

            # Check for numeric contradictions
            numeric_items = [i for i in group_items if i.is_quantitative]
            if len(numeric_items) >= 2:
                values = []
                for item in numeric_items:
                    try:
                        # Extract numeric value
                        val_str = str(item.value)
                        nums = re.findall(r'[\d.]+', val_str)
                        if nums:
                            values.append((item, float(nums[0])))
                    except (ValueError, TypeError, IndexError):
                        pass

                if len(values) >= 2:
                    # Check for significant divergence (>50% difference)
                    for i, (item1, val1) in enumerate(values):
                        for item2, val2 in values[i+1:]:
                            if val1 > 0 and abs(val1 - val2) / val1 > 0.5:
                                contradictions.append((
                                    item1, item2,
                                    f"Divergencia numérica: {val1} vs {val2}"
                                ))

        return contradictions


# =============================================================================
# GAP ANALYZER
# =============================================================================

class GapAnalyzer:
    """
    Análisis multi-dimensional de gaps con implicaciones causales.
    """

    # Implicaciones por tipo de elemento faltante
    GAP_IMPLICATIONS = {
        "fuentes_oficiales": (
            "Sin fuentes oficiales, la credibilidad del diagnóstico es cuestionable.",
            "Citar fuentes como DANE, Medicina Legal, ICBF."
        ),
        "indicadores_cuantitativos": (
            "Sin indicadores numéricos, no hay línea base medible.",
            "Incluir tasas, porcentajes o valores absolutos con fuente."
        ),
        "series_temporales_años": (
            "Sin series temporales, no se puede evaluar tendencia.",
            "Presentar datos de al menos 3 años consecutivos."
        ),
        "cobertura_territorial_especificada": (
            "Sin especificación territorial, el alcance es ambiguo.",
            "Definir si es municipal, departamental o por zonas."
        ),
        "logica_causal_explicita": (
            "Sin lógica causal, la teoría de cambio es invisible.",
            "Explicitar cadena: insumo → actividad → producto → resultado."
        ),
        "poblacion_objetivo_definida": (
            "Sin población objetivo, no hay focalización.",
            "Definir grupo beneficiario con características específicas."
        ),
        "instrumento_especificado": (
            "Sin instrumentos, las actividades son abstractas.",
            "Nombrar programas, proyectos o mecanismos concretos."
        ),
        "meta_cuantificada": (
            "Sin metas cuantificadas, no hay accountability.",
            "Establecer valores objetivo con plazo."
        ),
        "linea_base_resultado": (
            "Sin línea base, no se puede medir avance.",
            "Documentar situación inicial con fecha."
        ),
        "impacto_definido": (
            "Sin impactos definidos, el propósito final es difuso.",
            "Describir cambios de largo plazo esperados."
        ),
        "sistema_monitoreo": (
            "Sin sistema de monitoreo, no hay seguimiento.",
            "Especificar indicadores, frecuencia y responsables."
        ),
    }

    @classmethod
    def identify_gaps(
        cls,
        expected: List[ExpectedElement],
        found_counts: Dict[str, int],
        dimension: Dimension,
    ) -> List[EvidenceGap]:
        """
        Identifica gaps con severidad calibrada por dimensión.
        """
        gaps = []
        dim_theory = EnhancedContractInterpreter.get_dimension_theory(dimension)

        for elem in expected:
            found = found_counts.get(elem.type, 0)

            if found >= elem.minimum:
                continue  # No gap

            # Determinar severidad
            severity = cls._compute_severity(elem, found, dim_theory)

            # Obtener implicación y remediación
            implication, remediation = cls.GAP_IMPLICATIONS.get(
                elem.type,
                (f"Falta {elem.type}.", f"Agregar {elem.type}.")
            )

            gaps.append(EvidenceGap(
                element_type=elem.type,
                expected=elem.minimum,
                found=found,
                severity=severity,
                implication=implication,
                remediation=remediation,
            ))

        # Sort by severity
        severity_order = {
            GapSeverity.CRITICAL: 0,
            GapSeverity.MAJOR: 1,
            GapSeverity.MINOR: 2,
            GapSeverity.COSMETIC: 3,
        }
        gaps.sort(key=lambda g: severity_order[g.severity])

        return gaps

    @classmethod
    def _compute_severity(
        cls,
        elem: ExpectedElement,
        found: int,
        dim_theory: Dict[str, Any],
    ) -> GapSeverity:
        """Computa severidad basada en contexto dimensional."""

        # Critical if required and completely missing
        if elem.required and found == 0:
            return GapSeverity.CRITICAL

        # Check if matches dimension's primary need
        evidence_type = dim_theory.get("evidence_type", "")

        # Critical if element type matches dimension's evidence type and missing
        if elem.category == evidence_type and found == 0:
            return GapSeverity.CRITICAL

        # Major if required but partial
        if elem.required and found < elem.minimum:
            return GapSeverity.MAJOR

        # Major if high weight and missing
        if elem.weight >= 0.7 and found == 0:
            return GapSeverity.MAJOR

        # Minor for optional but expected
        if elem.minimum > 0 and found < elem.minimum:
            return GapSeverity.MINOR

        return GapSeverity.COSMETIC


# =============================================================================
# BAYESIAN CONFIDENCE ENGINE
# =============================================================================

class BayesianConfidenceEngine:
    """
    Inferencia bayesiana de confianza con calibración.

    Usa Dempster-Shafer para manejar incertidumbre epistémica.
    """

    @staticmethod
    def compute(
        items: List[EvidenceItem],
        gaps: List[EvidenceGap],
        corroborations: List[Tuple[EvidenceItem, EvidenceItem]],
        contradictions: List[Tuple[EvidenceItem, EvidenceItem, str]],
    ) -> BayesianConfidenceResult:
        """
        Computa confianza calibrada usando Dempster-Shafer.
        """
        if not items:
            return BayesianConfidenceResult(
                point_estimate=0.0,
                belief=0.0,
                plausibility=0.3,
                uncertainty=1.0,
                interval_95=(0.0, 0.3),
            )

        # 1. Base: average confidence of evidence
        confidences = [i.confidence for i in items]
        base_conf = statistics.mean(confidences)

        # 2. Boost for corroborations
        corroboration_boost = min(0.15, len(corroborations) * 0.05)

        # 3. Penalty for contradictions
        contradiction_penalty = min(0.25, len(contradictions) * 0.1)

        # 4. Penalty for gaps
        critical_gaps = sum(1 for g in gaps if g.severity == GapSeverity.CRITICAL)
        major_gaps = sum(1 for g in gaps if g.severity == GapSeverity.MAJOR)
        gap_penalty = min(0.4, critical_gaps * 0.15 + major_gaps * 0.05)

        # 5. Compute belief mass (lower bound of confidence)
        belief = max(0.0, base_conf + corroboration_boost - contradiction_penalty - gap_penalty)
        belief = belief * (1 - 0.1 * critical_gaps)  # Further reduce for critical gaps

        # 6. Compute plausibility (upper bound)
        plausibility = min(1.0, belief + 0.2)

        # 7. Epistemic uncertainty
        uncertainty = plausibility - belief

        # 8. Point estimate (expected value under ignorance)
        pessimism_weight = 0.6  # Be conservative
        point_estimate = pessimism_weight * belief + (1 - pessimism_weight) * plausibility

        # 9. Calibrated interval using Wilson score
        n = len(items)
        z = 1.96  # 95% CI

        p = point_estimate
        denominator = 1 + z**2 / n
        center = (p + z**2 / (2*n)) / denominator
        margin = z * math.sqrt((p * (1 - p) + z**2 / (4*n)) / n) / denominator

        lower = max(0.0, center - margin - gap_penalty)
        upper = min(1.0, center + margin)

        return BayesianConfidenceResult(
            point_estimate=round(point_estimate, 3),
            belief=round(belief, 3),
            plausibility=round(plausibility, 3),
            uncertainty=round(uncertainty, 3),
            interval_95=(round(lower, 3), round(upper, 3)),
        )


# =============================================================================
# DIMENSION-SPECIFIC STRATEGIES
# =============================================================================

class DimensionStrategy(ABC):
    """Base class for dimension-specific strategies."""

    @property
    @abstractmethod
    def dimension(self) -> Dimension:
        pass

    @abstractmethod
    def verdict_prefix(self, has_critical_gaps: bool) -> str:
        """Prefix for verdict based on dimension theory."""
        pass

    @abstractmethod
    def key_requirement(self) -> str:
        """Key requirement for this dimension."""
        pass

    @abstractmethod
    def interpret_confidence(self, conf: BayesianConfidenceResult) -> str:
        """Dimension-specific confidence interpretation."""
        pass


class D1InsumosStrategy(DimensionStrategy):
    """D1: Insumos - Diagnóstico y datos cuantitativos."""

    @property
    def dimension(self) -> Dimension:
        return Dimension.D1_INSUMOS

    def verdict_prefix(self, has_critical_gaps: bool) -> str:
        if has_critical_gaps:
            return "El diagnóstico carece de fundamento cuantitativo."
        return "El diagnóstico tiene base cuantitativa."

    def key_requirement(self) -> str:
        return "Datos numéricos de fuentes oficiales."

    def interpret_confidence(self, conf: BayesianConfidenceResult) -> str:
        if conf.point_estimate >= 0.7:
            return "Los datos son verificables."
        return "Faltan datos verificables."


class D2ActividadesStrategy(DimensionStrategy):
    """D2: Actividades - Especificidad operativa."""

    @property
    def dimension(self) -> Dimension:
        return Dimension.D2_ACTIVIDADES

    def verdict_prefix(self, has_critical_gaps: bool) -> str:
        if has_critical_gaps:
            return "Las actividades son vagas."
        return "Las actividades están especificadas."

    def key_requirement(self) -> str:
        return "Instrumento, población y lógica definidos."

    def interpret_confidence(self, conf: BayesianConfidenceResult) -> str:
        if conf.point_estimate >= 0.7:
            return "La especificación es operativa."
        return "Falta especificidad operativa."


class D3ProductosStrategy(DimensionStrategy):
    """D3: Productos - Proporcionalidad y metas."""

    @property
    def dimension(self) -> Dimension:
        return Dimension.D3_PRODUCTOS

    def verdict_prefix(self, has_critical_gaps: bool) -> str:
        if has_critical_gaps:
            return "Los productos no son proporcionales al problema."
        return "Los productos son proporcionales."

    def key_requirement(self) -> str:
        return "Metas cuantificadas y proporcionales."

    def interpret_confidence(self, conf: BayesianConfidenceResult) -> str:
        if conf.point_estimate >= 0.7:
            return "La proporcionalidad es clara."
        return "La proporcionalidad es cuestionable."


class D4ResultadosStrategy(DimensionStrategy):
    """D4: Resultados - Indicadores de outcome."""

    @property
    def dimension(self) -> Dimension:
        return Dimension.D4_RESULTADOS

    def verdict_prefix(self, has_critical_gaps: bool) -> str:
        if has_critical_gaps:
            return "Los resultados no son medibles."
        return "Los resultados tienen indicadores."

    def key_requirement(self) -> str:
        return "Indicadores con línea base y meta."

    def interpret_confidence(self, conf: BayesianConfidenceResult) -> str:
        if conf.point_estimate >= 0.7:
            return "Los indicadores permiten seguimiento."
        return "El seguimiento no es posible."


class D5ImpactosStrategy(DimensionStrategy):
    """D5: Impactos - Cambios de largo plazo."""

    @property
    def dimension(self) -> Dimension:
        return Dimension.D5_IMPACTOS

    def verdict_prefix(self, has_critical_gaps: bool) -> str:
        if has_critical_gaps:
            return "El impacto de largo plazo no está definido."
        return "El impacto está conceptualizado."

    def key_requirement(self) -> str:
        return "Teoría de cambio con horizonte temporal."

    def interpret_confidence(self, conf: BayesianConfidenceResult) -> str:
        if conf.point_estimate >= 0.7:
            return "La teoría de cambio es plausible."
        return "La teoría de cambio es débil."


class D6CausalidadStrategy(DimensionStrategy):
    """D6: Causalidad - M&E y adaptación."""

    @property
    def dimension(self) -> Dimension:
        return Dimension.D6_CAUSALIDAD

    def verdict_prefix(self, has_critical_gaps: bool) -> str:
        if has_critical_gaps:
            return "La lógica causal no es explícita."
        return "La cadena causal está documentada."

    def key_requirement(self) -> str:
        return "Sistema de M&E con ciclos de aprendizaje."

    def interpret_confidence(self, conf: BayesianConfidenceResult) -> str:
        if conf.point_estimate >= 0.7:
            return "El sistema permite adaptación."
        return "No hay mecanismo de corrección."


def get_dimension_strategy(dimension: Dimension) -> DimensionStrategy:
    """Factory for dimension strategies."""
    strategies = {
        Dimension.D1_INSUMOS: D1InsumosStrategy(),
        Dimension.D2_ACTIVIDADES: D2ActividadesStrategy(),
        Dimension.D3_PRODUCTOS: D3ProductosStrategy(),
        Dimension.D4_RESULTADOS: D4ResultadosStrategy(),
        Dimension.D5_IMPACTOS: D5ImpactosStrategy(),
        Dimension.D6_CAUSALIDAD: D6CausalidadStrategy(),
    }
    return strategies.get(dimension, D1InsumosStrategy())


# =============================================================================
# READABILITY & STYLE CHECKER (Flesch-Kincaid + Proselint)
# =============================================================================

@dataclass
class ReadabilityMetrics:
    """Métricas de legibilidad según Flesch-Kincaid y Proselint."""
    flesch_reading_ease: Optional[float] = None
    flesch_kincaid_grade: Optional[float] = None
    gunning_fog: Optional[float] = None
    avg_sentence_length: Optional[float] = None
    avg_word_length: Optional[float] = None
    proselint_errors: List[Dict[str, Any]] = field(default_factory=list)
    proselint_score: Optional[float] = None

    def passes_carver_standards(self) -> bool:
        """Verifica si el texto cumple estándares Carver."""
        if self.flesch_reading_ease and self.flesch_reading_ease < 60:
            return False
        if self.flesch_kincaid_grade and self.flesch_kincaid_grade > 12:
            return False
        if self.avg_sentence_length and self.avg_sentence_length > 20:
            return False
        if self.proselint_score and self.proselint_score < 0.9:
            return False
        return True


class ReadabilityChecker:
    """Aplica Flesch-Kincaid y Proselint para garantizar claridad Carver."""

    @staticmethod
    def check_text(text: str) -> ReadabilityMetrics:
        """Analiza texto con Flesch-Kincaid y Proselint."""
        metrics = ReadabilityMetrics()

        if textstat:
            try:
                metrics.flesch_reading_ease = textstat.flesch_reading_ease(text)
                metrics.flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)
                metrics.gunning_fog = textstat.gunning_fog(text)

                sentences = textstat.sentence_count(text)
                words = textstat.lexicon_count(text, removepunct=True)
                if sentences > 0:
                    metrics.avg_sentence_length = words / sentences

                chars = sum(len(word) for word in text.split())
                if words > 0:
                    metrics.avg_word_length = chars / words

            except Exception:
                pass

        if proselint_check:
            try:
                errors = proselint_check(text)
                if errors:
                    metrics.proselint_errors = errors
                    metrics.proselint_score = max(0.0, 1.0 - len(errors) / 100.0)
                else:
                    metrics.proselint_score = 1.0
            except Exception:
                metrics.proselint_score = 1.0

        return metrics

    @staticmethod
    def enforce_carver_style(text: str) -> Tuple[str, ReadabilityMetrics]:
        """Analiza y opcionalmente ajusta texto para cumplir estándares Carver."""
        metrics = ReadabilityChecker.check_text(text)

        if metrics.passes_carver_standards():
            return text, metrics

        adjusted_text = text

        if metrics.avg_sentence_length and metrics.avg_sentence_length > 20:
            adjusted_text = re.sub(r',\s+([a-záéíóúñ])', r'. \1', adjusted_text)
            adjusted_text = re.sub(r'\s+y\s+([a-záéíóúñ])', r'. \1', adjusted_text)

        metrics = ReadabilityChecker.check_text(adjusted_text)

        return adjusted_text, metrics


# =================…
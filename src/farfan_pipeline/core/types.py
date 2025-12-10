"""
Core types for F.A.R.F.A.N Policy Analysis Pipeline - VERSIÓN DEFINITIVA PDET

Tipos canónicos para el análisis de Planes de Desarrollo Territorial (PDT) colombianos,
optimizados para municipios PDET (Programas de Desarrollo con Enfoque Territorial).

Basados en:
- Ley 152 de 1994 (Ley Orgánica del Plan de Desarrollo)
- Metodología DNP (Departamento Nacional de Planeación)
- Acuerdo de Paz - Reforma Rural Integral (RRI)
- Plan Marco de Implementación (PMI)
- questionnaire_schema.json v2.0.0
- questionnaire_monolith.json (300 micro-questions)
- pattern_registry.json
- reporte_unit_of_analysis.json

Jerarquía estructural PDT:
    PDT → Título → Línea Estratégica → Sector → Programa → Producto → Meta → SubMeta

Jerarquía de preguntas (questionnaire):
    MacroQuestion → MesoQuestion → MicroQuestion (300)

Dimensiones causales (Cadena de valor DNP):
    D1_Insumos → D2_Actividades → D3_Productos → D4_Resultados → D5_Impactos → D6_Causalidad

Policy Areas (PA01-PA10):
    Derechos humanos específicos del contexto colombiano y construcción de paz
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, Union
import re


# =============================================================================
# ENUMS - Clasificadores del dominio PDET
# =============================================================================

class NivelJerarquico(Enum):
    """
    Nivel jerárquico en la estructura del PDT.
    Refleja la organización real de los documentos PDM/PDET.
    """
    H1_TITULO = auto()              # CAPÍTULO / TÍTULO (ej: CAPÍTULO 5. BUENOS AIRES...)
    H2_LINEA_ESTRATEGICA = auto()   # Línea Estratégica / Eje Estratégico
    H3_SECTOR = auto()              # Sector (ej: 41 Inclusión Social)
    H4_PROGRAMA = auto()            # Programa Presupuestal
    H5_PRODUCTO = auto()            # Producto / Proyecto MGA
    H6_META = auto()                # Meta Cuatrienio / Indicador
    H7_SUBMETA = auto()             # Metas anuales desagregadas (2024-2027)


class SeccionPDT(Enum):
    """
    Secciones principales del PDT según Ley 152/1994 y estructura real PDET.
    Incluye secciones obligatorias y contextuales.
    """
    # === TÍTULO I: Fundamentos y Componente General ===
    FUNDAMENTOS = "fundamentos"                  # Marco normativo y alineación
    METODOLOGIA = "metodologia"                  # Participación ciudadana, SisPT
    DIAGNOSTICO = "diagnostico"                  # Caracterización territorial, Análisis de brechas
    
    # === TÍTULO II: Parte Estratégica ===
    PRINCIPIOS = "principios"                    # Visión, Misión, Principios Rectores
    ENFOQUES = "enfoques"                        # Enfoques Transversales
    PARTE_ESTRATEGICA = "parte_estrategica"      # Líneas/Ejes, Programas, Metas
    
    # === TÍTULO III: Componente Financiero ===
    PLAN_FINANCIERO = "plan_financiero"          # Diagnóstico fiscal, MFMP
    PLAN_INVERSIONES = "plan_inversiones"        # PPI - Matriz presupuestaria
    
    # === Capítulos Especiales (Obligatorios/Contextuales) ===
    CAPITULO_PAZ = "capitulo_paz"                # Construcción de paz / PDET (obligatorio)
    CAPITULO_SGR = "capitulo_sgr"                # Inversiones SGR (independiente)
    
    # === TÍTULO IV: Seguimiento y Evaluación ===
    SEGUIMIENTO = "seguimiento"                  # Indicadores, Plan de Acción, SisPT
    
    # === Otros ===
    ANEXOS = "anexos"                            # Matrices, tablas complementarias


class DimensionCausal(Enum):
    """
    Dimensiones de la cadena de valor DNP.
    Alineado con canonical_notation.dimensions del questionnaire_monolith.json
    Refleja la lógica de intervención pública territorial.
    """
    DIM01_INSUMOS = "DIM01"       # D1: Diagnóstico, Recursos, Capacidad institucional
    DIM02_ACTIVIDADES = "DIM02"   # D2: Diseño de Intervención, Procesos operativos
    DIM03_PRODUCTOS = "DIM03"     # D3: Productos y Outputs (bienes/servicios entregados)
    DIM04_RESULTADOS = "DIM04"    # D4: Resultados y Outcomes (efectos/cambios generados)
    DIM05_IMPACTOS = "DIM05"      # D5: Impactos de Largo Plazo (transformación territorial)
    DIM06_CAUSALIDAD = "DIM06"    # D6: Teoría de Cambio (coherencia cadena de valor)

    @classmethod
    def from_legacy(cls, legacy_id: str) -> "DimensionCausal": 
        """Convierte D1-D6 a DIM01-DIM06."""
        mapping = {
            "D1": cls.DIM01_INSUMOS,
            "D2": cls.DIM02_ACTIVIDADES,
            "D3": cls.DIM03_PRODUCTOS,
            "D4": cls.DIM04_RESULTADOS,
            "D5": cls.DIM05_IMPACTOS,
            "D6": cls.DIM06_CAUSALIDAD,
        }
        return mapping.get(legacy_id, cls.DIM01_INSUMOS)


class CategoriaCausal(Enum):
    """
    Categorías causales jerárquicas para teoría de cambio.
    Axioma: 1-5 en orden INSUMOS->CAUSALIDAD.
    """
    INSUMOS = 1
    PROCESOS = 2
    PRODUCTOS = 3
    RESULTADOS = 4
    CAUSALIDAD = 5


class PolicyArea(Enum):
    """
    Áreas de política del questionnaire (PA01-PA10).
    Alineado con canonical_notation.policy_areas del questionnaire_monolith.json
    Enfoque de derechos humanos en contexto colombiano y PDET.
    """
    PA01 = "PA01"  # Derechos de las mujeres e igualdad de género
    PA02 = "PA02"  # Prevención de la violencia y protección frente al conflicto
    PA03 = "PA03"  # Ambiente sano, cambio climático, prevención de desastres
    PA04 = "PA04"  # Derechos económicos, sociales y culturales (DESC)
    PA05 = "PA05"  # Derechos de las víctimas y construcción de paz
    PA06 = "PA06"  # Derecho al buen futuro de la niñez, adolescencia, juventud
    PA07 = "PA07"  # Tierras y territorios (Reforma Rural Integral - RRI)
    PA08 = "PA08"  # Líderes y defensores de derechos humanos
    PA09 = "PA09"  # Crisis de derechos de personas privadas de la libertad
    PA10 = "PA10"  # Enfoque étnico-diferencial (indígenas, afro, comunidades)

    @classmethod
    def from_legacy(cls, legacy_id: str) -> "PolicyArea":
        """Convierte P1-P10 a PA01-PA10."""
        mapping = {f"P{i}": getattr(cls, f"PA{i:02d}") for i in range(1, 11)}
        return mapping.get(legacy_id, cls.PA01)


class MarcadorContextual(Enum):
    """
    Marcadores P-D-Q para clasificación de contenido según contexto semántico.
    Permite identificar el tipo de información en el texto del PDT.
    """
    P_PROBLEMA = "problema"      # Diagnóstico, brechas, necesidades, problemáticas
    D_DECISION = "decision"      # Elección estratégica, priorización, objetivos
    Q_PREGUNTA = "pregunta"      # Investigación, evaluación, seguimiento


class TipoIndicador(Enum):
    """
    Clasificación de indicadores según metodología DNP.
    Refleja los tipos reales encontrados en matrices de indicadores PDT.
    """
    PRODUCTO = "producto"        # Bienes/servicios entregados (outputs)
    RESULTADO = "resultado"      # Efectos/cambios generados (outcomes)
    BIENESTAR = "bienestar"      # Calidad de vida, cierre de brechas
    GESTION = "gestion"          # Procesos internos, eficiencia administrativa


class FuenteFinanciacion(Enum):
    """
    Fuentes de financiación en el sistema territorial colombiano.
    Refleja las columnas reales del Plan Plurianual de Inversiones (PPI).
    """
    SGP = "sgp"                          # Sistema General de Participaciones
    SGR = "sgr"                          # Sistema General de Regalías
    RECURSOS_PROPIOS = "recursos_propios"  # Ingresos tributarios locales
    CREDITO = "credito"                  # Endeudamiento público
    COOPERACION = "cooperacion"          # Cooperación internacional
    OTRAS = "otras"                      # Cofinanciación, transferencias
    FONDO_SUBREGIONAL = "fondo_subregional"  # Ej: Alto Patía


class NivelConfianza(Enum):
    """
    Nivel de confianza en la extracción y análisis de datos.
    Basado en umbrales de scoring y calidad de evidencia.
    """
    ALTA = "alta"       # 0.9-1.0 - Datos explícitos, verificados, cuantitativos
    MEDIA = "media"     # 0.6-0.8 - Datos inferidos, parciales, cualitativos
    BAJA = "baja"       # <0.6 - Datos ausentes, ambiguos o "S/D"


class ScoringLevel(Enum):
    """
    Niveles de scoring del questionnaire.
    Alineado con scoring.micro_levels del questionnaire_schema.json
    """
    EXCELENTE = "excelente"      # min_score: 0.85
    BUENO = "bueno"              # min_score: 0.70
    ACEPTABLE = "aceptable"      # min_score: 0.55
    INSUFICIENTE = "insuficiente"  # min_score: 0.0

    @classmethod
    def from_score(cls, score: float) -> "ScoringLevel":
        """Determina nivel de scoring basado en puntaje."""
        if score >= 0.85:
            return cls.EXCELENTE
        elif score >= 0.70:
            return cls.BUENO
        elif score >= 0.55:
            return cls.ACEPTABLE
        return cls.INSUFICIENTE


class PatternMatchType(Enum):
    """
    Tipos de matching de patrones.
    Alineado con PatternItem.match_type del questionnaire_schema.json
    """
    REGEX = "REGEX"
    LITERAL = "LITERAL"
    NER_OR_REGEX = "NER_OR_REGEX"


class PatternSpecificity(Enum):
    """
    Especificidad de patrones de detección.
    Alineado con PatternItem.specificity del questionnaire_schema.json
    """
    HIGH = "HIGH"      # Patrones muy específicos (ej: códigos MGA)
    MEDIUM = "MEDIUM"  # Patrones moderados (ej: términos técnicos)
    LOW = "LOW"        # Patrones genéricos (ej: palabras comunes)


class PatternContextScope(Enum):
    """
    Alcance de contexto para patrones de detección.
    Alineado con PatternItem.context_scope del questionnaire_schema.json
    """
    SENTENCE = "SENTENCE"      # Oración individual
    PARAGRAPH = "PARAGRAPH"    # Párrafo completo
    SECTION = "SECTION"        # Sección del documento
    DOCUMENT = "DOCUMENT"      # Documento completo


class MethodType(Enum):
    """
    Tipos de métodos analíticos.
    Alineado con MethodSet.method_type del questionnaire_schema.json
    """
    ANALYSIS = "analysis"          # Análisis de contenido
    AGGREGATION = "aggregation"    # Agregación de resultados
    ROUTING = "routing"            # Enrutamiento de preguntas
    VALIDATION = "validation"      # Validación de datos
    EXTRACTION = "extraction"      # Extracción de información
    SCORING = "scoring"            # Cálculo de puntajes


class AggregationMethod(Enum):
    """
    Métodos de agregación para preguntas multinivel.
    Alineado con MacroQuestion.aggregation_method del questionnaire_schema.json
    """
    HOLISTIC_ASSESSMENT = "holistic_assessment"  # Evaluación holística cualitativa
    WEIGHTED_AVERAGE = "weighted_average"        # Promedio ponderado
    HIERARCHICAL = "hierarchical"                # Agregación jerárquica


class TipoEntidadInstitucional(Enum):
    """
    Tipos de entidades institucionales en el sistema colombiano.
    Refleja la estructura real del Estado y actores territoriales.
    """
    NACIONAL = "nacional"              # DNP, Ministerios, Fiscalía, JEP, UARIV
    DEPARTAMENTAL = "departamental"    # Gobernación, CAR
    MUNICIPAL = "municipal"            # Alcaldía, Secretarías, Consejo Municipal
    COOPERACION = "cooperacion"        # Organismos internacionales
    SOCIEDAD_CIVIL = "sociedad_civil"  # JAC, Consejos Comunitarios, Mesas
    CONTROL = "control"                # Contraloría, Personería


class TipoReferenciaLegal(Enum):
    """
    Tipos de referencias legales en el ordenamiento colombiano.
    """
    CONSTITUCION = "constitucion"  # Constitución Política (Art. 339)
    LEY = "ley"                    # Ley 152 de 1994, Ley 2056 de 2020
    DECRETO = "decreto"            # Decreto 111 de 1996, Decreto 413 de 2018
    RESOLUCION = "resolucion"      # Resolución DNP
    ACUERDO = "acuerdo"            # Acuerdo Municipal
    CIRCULAR = "circular"          # Circular conjunta
    SENTENCIA = "sentencia"        # Sentencias de Cortes


class ZonaPDET(Enum):
    """
    Subregiones PDET (Programas de Desarrollo con Enfoque Territorial).
    16 subregiones priorizadas del Acuerdo de Paz.
    """
    # Cauca
    ALTO_PATIA_NORTE_CAUCA = "alto_patia_norte_cauca"
    PACIFICO_MEDIO = "pacifico_medio"
    
    # Otras regiones PDET (ejemplos)
    ARAUCA = "arauca"
    BAJO_CAUCA_NORDESTE_ANTIOQUIA = "bajo_cauca_nordeste_antioquia"
    CATATUMBO = "catatumbo"
    CHOCO = "choco"
    CUENCA_CAGUAN_PUTUMAYO = "cuenca_caguan_putumayo"
    MACARENA_GUAVIARE = "macarena_guaviare"
    MONTES_MARIA = "montes_maria"
    PACIFICO_NARINO = "pacifico_narino"
    PACÍFICO_SUR = "pacifico_sur"
    PUTUMAYO = "putumayo"
    SUR_BOLIVAR = "sur_bolivar"
    SUR_CORDOBA = "sur_cordoba"
    SUR_TOLIMA = "sur_tolima"
    URABÁ_ANTIOQUEÑO = "uraba_antioqueno"


class PilarRRI(Enum):
    """
    Pilares de la Reforma Rural Integral (RRI) - Acuerdo de Paz.
    Los 8 pilares PDET vinculados al capítulo de paz del PDT.
    """
    PILAR_1_ORDENAMIENTO = "pilar_1_ordenamiento_social_propiedad"
    PILAR_2_INFRAESTRUCTURA = "pilar_2_infraestructura_adecuacion_tierras"
    PILAR_3_SALUD = "pilar_3_salud_rural"
    PILAR_4_EDUCACION = "pilar_4_educacion_rural"
    PILAR_5_VIVIENDA = "pilar_5_vivienda_agua_saneamiento"
    PILAR_6_REACTIVACION = "pilar_6_reactivacion_economica_produccion_agropecuaria"
    PILAR_7_RECONCILIACION = "pilar_7_reconciliacion_convivencia_paz"
    PILAR_8_SISTEMA_ALIMENTARIO = "pilar_8_sistema_alimentacion_nutricional"


# =============================================================================
# TIPOS BASE - Provenance y Chunks
# =============================================================================

@dataclass
class Provenance: 
    """
    Rastrea el origen y transformación de datos.
    Permite auditoría completa desde el PDF original hasta el análisis final.
    
    CRÍTICO: Todos los datos extraídos deben tener provenance para trazabilidad.
    """
    source_file: str
    page_number: Optional[int] = None
    chunk_id: Optional[str] = None
    extraction_method: str = "unknown"
    timestamp: Optional[datetime] = None

    # Localización semántica en el documento
    seccion_pdt: Optional[SeccionPDT] = None
    nivel_jerarquico: Optional[NivelJerarquico] = None

    # Offsets para trazabilidad exacta (posición en el texto)
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None

    # Confianza en la extracción
    confidence_score: float = 0.0
    nivel_confianza: NivelConfianza = NivelConfianza.BAJA

    # Contexto adicional
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serializa provenance a diccionario."""
        return {
            "source_file": self.source_file,
            "page_number": self.page_number,
            "chunk_id": self.chunk_id,
            "extraction_method": self.extraction_method,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "seccion_pdt": self.seccion_pdt.value if self.seccion_pdt else None,
            "nivel_jerarquico": self.nivel_jerarquico.value if self.nivel_jerarquico else None,
            "start_offset": self.start_offset,
            "end_offset": self.end_offset,
            "confidence_score": self.confidence_score,
            "nivel_confianza": self.nivel_confianza.value,
            "metadata": self.metadata
        }


@dataclass
class TextSpan:
    """
    Representa un span de texto con posición exacta.
    Útil para resaltar evidencias en el documento original.
    """
    text: str
    start: int
    end: int
    page: Optional[int] = None


@dataclass
class ChunkData:
    """
    Unidad mínima de texto extraído con contexto completo. 

    Cada chunk preserva: 
    - Texto original sin modificar
    - Posición exacta (offsets, página)
    - Clasificación semántica (sección, nivel, dimensión causal, policy area)
    - Provenance completo
    - Relaciones jerárquicas (parent/children)
    
    INVARIANTE CRÍTICO: El sistema debe generar exactamente 60 chunks base:
    10 Policy Areas × 6 Dimensions = 60 chunks
    """
    chunk_id: str
    text: str
    start_offset: int
    end_offset: int

    # Localización física
    page_number: Optional[int] = None
    seccion_pdt: Optional[SeccionPDT] = None
    nivel_jerarquico: Optional[NivelJerarquico] = None

    # Clasificación semántica (coordenadas en el espacio de análisis)
    dimension_causal: Optional[DimensionCausal] = None
    policy_area: Optional[PolicyArea] = None
    marcador_contextual: Optional[MarcadorContextual] = None

    # Trazabilidad
    provenance: Optional[Provenance] = None

    # Relaciones jerárquicas
    parent_chunk_id: Optional[str] = None
    child_chunk_ids: List[str] = field(default_factory=list)

    # Metadatos adicionales
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_coordinate(self) -> Tuple[str, str]:
        """
        Retorna la coordenada (PolicyArea, Dimension) del chunk.
        Útil para indexación y búsqueda.
        """
        pa = self.policy_area.value if self.policy_area else "UNKNOWN"
        dim = self.dimension_causal.value if self.dimension_causal else "UNKNOWN"
        return (pa, dim)


# =============================================================================
# TIPOS DE QUESTIONNAIRE - Alineados con questionnaire_schema.json
# =============================================================================

@dataclass
class PatternItem:
    """
    Patrón de detección para análisis de texto.
    Alineado con definitions.PatternItem del questionnaire_schema.json
    
    Los patrones son la base del análisis automatizado de PDTs.
    """
    id: str
    pattern: str
    match_type: PatternMatchType
    category: str

    # Contexto semántico
    context_requirement: Optional[str] = None
    context_scope: PatternContextScope = PatternContextScope.PARAGRAPH

    # Especificidad y expansión
    specificity: PatternSpecificity = PatternSpecificity.MEDIUM
    semantic_expansion: Optional[Union[str, Dict, List]] = None
    synonym_clusters: Optional[List[str]] = None

    # Validación y confianza
    validation_rule: Optional[str] = None
    confidence_weight: Optional[float] = None
    negative_filter: Optional[bool] = None

    # Tipo de entidad
    entity_type: Optional[str] = None
    element_tags: Optional[List[str]] = None

    # Referencia a patrón compartido (pattern_registry.json)
    pattern_ref: Optional[str] = None  # e.g., "PAT-0001"

    def matches(self, text: str, context: Optional[str] = None) -> bool:
        """
        Verifica si el patrón hace match con el texto.
        Considera el contexto si es requerido.
        """
        if self.match_type == PatternMatchType.LITERAL:
            return self.pattern.lower() in text.lower()
        elif self.match_type == PatternMatchType.REGEX:
            return bool(re.search(self.pattern, text, re.IGNORECASE))
        elif self.match_type == PatternMatchType.NER_OR_REGEX:
            # Requiere integración con NER, por ahora fallback a regex
            return bool(re.search(self.pattern, text, re.IGNORECASE))
        return False


@dataclass
class MethodSet:
    """
    Conjunto de métodos analíticos para una pregunta.
    Alineado con definitions.MethodSet del questionnaire_schema.json
    
    Define la estrategia de análisis para responder una micro-question.
    """
    class_name: str  # Pattern: ^[A-Za-z_][A-Za-z0-9_]*$
    function: str    # Pattern: ^[A-Za-z_][A-Za-z0-9_]*$
    method_type: MethodType

    priority: int = 0
    description: Optional[str] = None

    # Dependencias de patrones
    depends_on_patterns: List[str] = field(default_factory=list)
    pattern_dependencies: List[str] = field(default_factory=list)

    # Output esperado
    produces_elements: List[str] = field(default_factory=list)
    output_validates: List[str] = field(default_factory=list)

    failure_mode: Optional[str] = None


@dataclass
class MicroQuestion:
    """
    Pregunta micro del cuestionario (300 preguntas).
    Alineado con definitions.MicroQuestion del questionnaire_schema.json
    
    Representa la unidad atómica de análisis del PDT.
    Cada micro-question evalúa un aspecto específico de la calidad del plan.
    """
    question_id: str  # Pattern: ^Q\d{3}$ (Q001-Q300)
    text: str
    cluster_id: str
    dimension_id: str  # DIM01-DIM06

    policy_area_id: Optional[str] = None  # PA01-PA10
    base_slot: Optional[str] = None
    question_global: Optional[int] = None
    scoring_modality: Optional[str] = None
    scoring_definition_ref: Optional[str] = None

    # Elementos esperados en la respuesta
    expected_elements: List[str] = field(default_factory=list)

    # Contrato de fallo (qué hacer si no se puede responder)
    failure_contract: Optional[Dict[str, Any]] = None

    # Métodos y patrones asociados
    method_sets: List[MethodSet] = field(default_factory=list)
    patterns: List[PatternItem] = field(default_factory=list)

    # Validaciones
    validations: Optional[Dict[str, Any]] = None

    def validate_question_id(self) -> bool:
        """Valida que question_id siga el patrón ^Q\\d{3}$."""
        return bool(re.match(r"^Q\d{3}$", self.question_id))


@dataclass
class MesoQuestion:
    """
    Pregunta meso del cuestionario (clusters temáticos).
    Alineado con definitions.MesoQuestion del questionnaire_schema.json
    
    Agrega múltiples micro-questions relacionadas temáticamente.
    """
    question_id: str  # Pattern: ^MESO_[A-Z0-9_]+$
    cluster_id: str
    text: str
    type: str

    question_global: Optional[int] = None
    aggregation_method: Optional[str] = None
    scoring_modality: Optional[str] = None
    policy_areas: List[str] = field(default_factory=list)
    patterns: List[Dict[str, Any]] = field(default_factory=list)

    # Micro questions que agrega
    micro_question_ids: List[str] = field(default_factory=list)


@dataclass
class MacroQuestion:
    """
    Pregunta macro del cuestionario (evaluación holística).
    Alineado con definitions.MacroQuestion del questionnaire_schema.json
    
    Evaluación de más alto nivel que integra múltiples meso-questions.
    """
    question_global: int
    aggregation_method: AggregationMethod

    clusters: List[str] = field(default_factory=list)
    patterns: List[Dict[str, Any]] = field(default_factory=list)
    fallback: Optional[Dict[str, Any]] = None


@dataclass
class ScoringDefinition:
    """
    Definición de scoring para un nivel de evaluación.
    Vincula puntajes numéricos con categorías cualitativas.
    """
    level: ScoringLevel
    min_score: float
    criteria: str = ""
    color: Optional[str] = None  # Para visualización


# =============================================================================
# TIPOS DE DOMINIO PDT - Estructura Jerárquica del Territorio
# =============================================================================

@dataclass
class EntidadInstitucional:
    """
    Entidad institucional colombiana referenciada en el PDT.
    Refleja el ecosistema de actores del sistema territorial.
    """
    nombre: str
    sigla: Optional[str] = None
    tipo: TipoEntidadInstitucional = TipoEntidadInstitucional.MUNICIPAL
    rol: Optional[str] = None
    
    # Información de contacto/ubicación (opcional)
    nivel_gobierno: Optional[str] = None  # nacional, departamental, municipal
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReferenciaLegal:
    """
    Referencia a normativa colombiana citada en el PDT.
    Permite rastrear el marco legal de las intervenciones.
    """
    tipo: TipoReferenciaLegal
    numero: str
    año: int
    articulo: Optional[str] = None
    descripcion: Optional[str] = None
    
    # Texto completo de la referencia (ej: "Ley 152 de 1994")
    texto_completo: Optional[str] = None


@dataclass
class Meta:
    """
    Meta cuantificable del PDT.
    Vincula indicador + línea base + objetivo cuatrienal.
    
    Refleja la estructura real de las Matrices de Indicadores.
    """
    codigo: Optional[str] = None
    descripcion: str = ""

    # Indicador asociado
    tipo_indicador: TipoIndicador = TipoIndicador.PRODUCTO
    indicador_nombre: str = ""
    codigo_indicador: Optional[str] = None
    unidad_medida: str = ""

    # Valores (Línea Base → Meta Cuatrienio)
    linea_base: Optional[float] = None
    año_linea_base: Optional[int] = None
    meta_cuatrienio: Optional[float] = None

    # Desagregación anual (submetas)
    meta_2024: Optional[float] = None
    meta_2025: Optional[float] = None
    meta_2026: Optional[float] = None
    meta_2027: Optional[float] = None

     # Información adicional
    fuente_informacion: Optional[str] = None
    responsable: Optional[str] = None  # Secretaría responsable

    # Grupo poblacional objetivo
    poblacion_objetivo: Optional[str] = None

    # Trazabilidad
    provenance: Optional[Provenance] = None

    def cumplimiento_porcentual(self) -> Optional[float]:
        """Calcula % de cumplimiento si hay línea base y meta."""
        if self.linea_base is not None and self.meta_cuatrienio is not None:
            if self.meta_cuatrienio == 0:
                return None
            return (self.linea_base / self.meta_cuatrienio) * 100
        return None


@dataclass
class Producto:
    """
    Producto del PDT (bien o servicio entregable).
    Codificado según catálogo MGA (Metodología General Ajustada) del DNP.
    
    Representa el nivel H5 de la jerarquía PDT.
    """
    codigo_mga: Optional[str] = None  # Código del catálogo MGA (ej: 2106003)
    nombre: str = ""
    descripcion: str = ""

    # Indicadores y metas asociadas
    indicadores: List[Meta] = field(default_factory=list)

    # Presupuesto del producto
    costo_total: Optional[float] = None
    fuentes_financiacion: Dict[FuenteFinanciacion, float] = field(default_factory=dict)

    # Información adicional
    alcance_geografico: Optional[str] = None  # Rural, Urbano, Corregimientos específicos
    poblacion_beneficiaria: Optional[str] = None

    # Trazabilidad
    provenance: Optional[Provenance] = None


@dataclass
class Programa:
    """
    Programa presupuestal del PDT. 
    Agrupa productos relacionados bajo un código presupuestal único.
    
    Representa el nivel H4 de la jerarquía PDT.
    Refleja la estructura real de los documentos (ej: "Programa: Salud Pública").
    """
    codigo_presupuestal: Optional[str] = None  # Código del programa (ej: 1203)
    nombre: str = ""
    descripcion: str = ""
    sector: Optional[str] = None  # Ej: "41 Inclusión Social"

    # Contenido del programa
    productos: List[Producto] = field(default_factory=list)
    metas_resultado: List[Meta] = field(default_factory=list)

    # Presupuesto agregado
    costo_total_cuatrienio: Optional[float] = None
    distribucion_anual: Dict[int, float] = field(default_factory=dict)  # {2024: monto, ...}

    # Justificación (vínculo con diagnóstico)
    justificacion: Optional[str] = None
    problematicas_atendidas: List[str] = field(default_factory=list)

    # Trazabilidad
    provenance: Optional[Provenance] = None


@dataclass
class LineaEstrategica:
    """
    Línea/Eje estratégico del PDT.
    Nivel más alto de organización programática (H2).
    
    Refleja las "grandes apuestas" de la administración territorial.
    Ej: "Línea Estratégica 1: Territorio, Ambiente y Ruralidad"
    """
    codigo: Optional[str] = None
    numero: Optional[int] = None
    titulo: str = ""
    descripcion: Optional[str] = None

    # Enfoques transversales aplicados
    enfoques: List[str] = field(default_factory=list)  
    # Ej: ["derechos", "género", "territorial", "diferencial", "sostenibilidad"]

    # Contenido de la línea
    programas: List[Programa] = field(default_factory=list)

    # Presupuesto agregado de la línea
    inversion_total: Optional[float] = None
    distribucion_anual: Dict[int, float] = field(default_factory=dict)

    # Vinculación con ODS y PND
    ods_vinculados: List[int] = field(default_factory=list)  # Números de ODS (1-17)
    vinculacion_pnd: Optional[str] = None  # Transformación Colombia Potencia Mundial de la Vida

    # Trazabilidad
    provenance: Optional[Provenance] = None


@dataclass
class DiagnosticoTerritorial:
    """
    Información del diagnóstico/caracterización del PDT (Título I).
    Fundamenta la intervención pública identificando brechas y necesidades.
    """
    # === Datos demográficos ===
    poblacion_total: Optional[int] = None
    poblacion_urbana: Optional[int] = None
    poblacion_rural: Optional[int] = None
    poblacion_etnica: Optional[Dict[str, int]] = None  # {"indigena": X, "afro": Y}

    # === Indicadores socioeconómicos ===
    indice_pobreza_multidimensional: Optional[float] = None  # IPM
    nbi: Optional[float] = None  # Necesidades Básicas Insatisfechas
    cobertura_salud: Optional[Dict[str, int]] = None  # {"contributivo": X, "subsidiado": Y}
    tasas_educacion: Optional[Dict[str, float]] = None  # {"cobertura": X, "desercion": Y}

    # === Problemáticas identificadas ===
    problematicas: List[str] = field(default_factory=list)
    brechas: List[str] = field(default_factory=list)
    ejes_problematicos: List[str] = field(default_factory=list)

    # === División territorial ===
    corregimientos: List[str] = field(default_factory=list)
    veredas: List[str] = field(default_factory=list)
    consejos_comunitarios: List[str] = field(default_factory=list)

    # === Instrumentos de ordenamiento ===
    tiene_pot: bool = False
    tiene_pbot: bool = False
    tiene_eot: bool = False
    fecha_actualizacion_ot: Optional[datetime] = None

    # Trazabilidad
    provenance: Optional[Provenance] = None


@dataclass
class PlanPlurianuaInversiones:
    """
    Plan Plurianual de Inversiones (PPI) - Título III del PDT.
    Componente financiero obligatorio que proyecta recursos del cuatrienio.
    
    Refleja la estructura real de las Matrices PPI encontradas en los documentos.
    """
    # === Totales por vigencia (año fiscal) ===
    total_2024: Optional[float] = None
    total_2025: Optional[float] = None
    total_2026: Optional[float] = None
    total_2027: Optional[float] = None
    total_cuatrienio: Optional[float] = None

    # === Desglose por fuente de financiación ===
    total_sgp: Optional[float] = None  # Sistema General de Participaciones
    total_sgr: Optional[float] = None  # Sistema General de Regalías
    total_recursos_propios: Optional[float] = None
    total_credito: Optional[float] = None
    total_cooperacion: Optional[float] = None
    total_otras_fuentes: Optional[float] = None

    # === Matriz de inversiones detallada ===
    # Lista de diccionarios con estructura:
    # {"linea": str, "sector": str, "programa": str, "2024": float, "2025": float, ...}
    matriz_inversiones: List[Dict[str, Any]] = field(default_factory=list)

    # === Análisis fiscal ===
    marco_fiscal_mediano_plazo: Optional[Dict[str, Any]] = None  # MFMP (proyección 10 años)
    sostenibilidad_fiscal: Optional[str] = None  # Análisis cualitativo

    # Trazabilidad
    provenance: Optional[Provenance] = None

    def calcular_porcentaje_fuente(self, fuente: FuenteFinanciacion) -> Optional[float]:
        """Calcula % de una fuente respecto al total."""
        if self.total_cuatrienio is None or self.total_cuatrienio == 0:
            return None
        
        mapping = {
            FuenteFinanciacion.SGP: self.total_sgp,
            FuenteFinanciacion.SGR: self.total_sgr,
            FuenteFinanciacion.RECURSOS_PROPIOS: self.total_recursos_propios,
            FuenteFinanciacion.CREDITO: self.total_credito,
            FuenteFinanciacion.COOPERACION: self.total_cooperacion,
            FuenteFinanciacion.OTRAS: self.total_otras_fuentes,
        }
        
        valor = mapping.get(fuente)
        if valor is not None:
            return (valor / self.total_cuatrienio) * 100
        return None


@dataclass
class IniciativaPDET:
    """
    Iniciativa específica del PDET vinculada al capítulo de paz.
    Las iniciativas PDET son priorizadas por las comunidades en los PATR
    (Planes de Acción para la Transformación Regional).
    """
    # Clasificación PDET - REQUIRED FIELD FIRST
    pilar_rri: PilarRRI  # Uno de los 8 pilares
    
    # Optional fields
    codigo: Optional[str] = None
    nombre: str = ""
    descripcion: str = ""
    linea_accion: Optional[str] = None
    
    # Vinculación con el PDT
    programa_vinculado: Optional[str] = None  # Código del programa PDT
    presupuesto_asignado: Optional[float] = None
    
    # Ubicación
    corregimientos_veredas: List[str] = field(default_factory=list)
    
    # Trazabilidad
    provenance: Optional[Provenance] = None


@dataclass
class CapituloPaz:
    """
    Capítulo de Paz/PDET - Obligatorio en municipios PDET.
    
    Articulación del PDT con el Acuerdo de Paz (2016) y el Plan Marco 
    de Implementación (PMI). Fundamental en zonas afectadas por el conflicto.
    
    Refleja la estructura real del "CAPÍTULO 5. BUENOS AIRES ACTÚA POR LA PAZ"
    y secciones similares en documentos PDET.
    """
    # === Clasificación PDET ===
    es_municipio_pdet: bool = False
    subregion_pdet: Optional[ZonaPDET] = None
    
    # === Iniciativas PDET priorizadas ===
    iniciativas_pdet: List[IniciativaPDET] = field(default_factory=list)
    total_iniciativas_priorizadas: int = 0
    
    # === Articulación con pilares RRI ===
    pilares_abordados: List[PilarRRI] = field(default_factory=list)
    
    # === Articulación institucional ===
    articulacion_pmi: Optional[str] = None  # Plan Marco de Implementación
    articulacion_patr: Optional[str] = None  # Plan de Acción Transformación Regional
    articulacion_pnis: Optional[str] = None  # Programa Nacional Integral Sustitución
    
    # === Presupuesto específico paz ===
    presupuesto_total_paz: Optional[float] = None
    fuentes_paz: Dict[FuenteFinanciacion, float] = field(default_factory=dict)
    
    # === Población beneficiaria ===
    victimas_conflicto: Optional[int] = None
    excombatientes: Optional[int] = None
    comunidades_etnicas_beneficiadas: List[str] = field(default_factory=list)
    
    # === Metas específicas de construcción de paz ===
    metas_reconciliacion: List[Meta] = field(default_factory=list)
    metas_reintegracion: List[Meta] = field(default_factory=list)
    metas_reparacion_victimas: List[Meta] = field(default_factory=list)
    
    # === Coordinación interinstitucional ===
    entidades_coordinacion: List[EntidadInstitucional] = field(default_factory=list)
    # Ej: ART, Agencia Renovación Territorio; ARN, Agencia Reintegración
    
    # Trazabilidad
    provenance: Optional[Provenance] = None


# =============================================================================
# DOCUMENTO PREPROCESADO - Output de Phase 1
# =============================================================================

@dataclass
class PreprocessedDocument:
    """
    Documento PDT después de preprocesamiento. 

    Output canónico de Phase 1 (Ingestion).
    Input para el Orchestrator y fases subsiguientes. 

    INVARIANTE CRÍTICO: chunk_count == 60 (10 Policy Areas × 6 Dimensions)
    Cada chunk debe tener coordenadas (PA, DIM) únicas.
    """
    # === Identificación ===
    document_id: str
    source_path: str
    municipio: Optional[str] = None
    departamento: str = "Cauca"  # Default para el contexto actual
    periodo: str = "2024-2027"

    # === Clasificación PDET ===
    es_municipio_pdet: bool = False
    subregion_pdet: Optional[ZonaPDET] = None

    # === Chunks extraídos (60 unidades mínimas) ===
    chunks: List[ChunkData] = field(default_factory=list)

    # === Estructura jerárquica parseada ===
    diagnostico: Optional[DiagnosticoTerritorial] = None
    lineas_estrategicas: List[LineaEstrategica] = field(default_factory=list)
    plan_inversiones: Optional[PlanPlurianuaInversiones] = None
    capitulo_paz: Optional[CapituloPaz] = None

    # === Entidades y referencias extraídas ===
    entidades_mencionadas: List[EntidadInstitucional] = field(default_factory=list)
    referencias_legales: List[ReferenciaLegal] = field(default_factory=list)

    # === Metadatos de extracción ===
    total_pages: int = 0
    extraction_timestamp: Optional[datetime] = None
    extraction_method: str = "unknown"

    # === Métricas de calidad ===
    provenance_completeness: float = 0.0
    chunks_with_provenance: int = 0
    chunks_total: int = 0

    # === Validación de invariantes ===
    invariant_60_chunks: bool = False
    coverage_matrix: Dict[Tuple[str, str], bool] = field(default_factory=dict)
    # Matriz PA×DIM: {("PA01", "DIM01"): True, ...}

    metadata: Dict[str, Any] = field(default_factory=dict)

    def compute_provenance_completeness(self) -> float:
        """Calcula métrica de completitud de provenance."""
        if not self.chunks:
            return 0.0

        with_provenance = sum(1 for c in self.chunks if c.provenance is not None)
        self.chunks_with_provenance = with_provenance
        self.chunks_total = len(self.chunks)
        self.provenance_completeness = with_provenance / len(self.chunks)

        return self.provenance_completeness

    def validate_chunk_invariant(self) -> bool:
        """
        Valida el invariante de 60 chunks (10 PA × 6 DIM).
        Retorna True si la estructura es correcta.
        """
        self.invariant_60_chunks = len(self.chunks) == 60
        
        # Construir matriz de cobertura
        self.coverage_matrix = {}
        for pa_num in range(1, 11):  # PA01-PA10
            for dim_num in range(1, 7):  # DIM01-DIM06
                pa_id = f"PA{pa_num:02d}"
                dim_id = f"DIM{dim_num:02d}"
                coord = (pa_id, dim_id)
                
                # Verificar si existe chunk con esta coordenada
                has_chunk = any(
                    c.policy_area and c.dimension_causal and
                    c.policy_area.value == pa_id and c.dimension_causal.value == dim_id
                    for c in self.chunks
                )
                self.coverage_matrix[coord] = has_chunk
        
        # Verificar cobertura completa
        full_coverage = all(self.coverage_matrix.values())
        
        return self.invariant_60_chunks and full_coverage

    def get_chunk_by_coordinate(self, policy_area: str, dimension: str) -> Optional[ChunkData]:
        """Obtiene chunk específico por coordenada (PA, DIM)."""
        for chunk in self.chunks:
            if (chunk.policy_area and chunk.policy_area.value == policy_area and
                chunk.dimension_causal and chunk.dimension_causal.value == dimension):
                return chunk
        return None

    def get_chunks_by_policy_area(self, policy_area: str) -> List[ChunkData]:
        """Obtiene todos los chunks de una Policy Area específica."""
        return [c for c in self.chunks 
                if c.policy_area and c.policy_area.value == policy_area]

    def get_chunks_by_dimension(self, dimension: str) -> List[ChunkData]:
        """Obtiene todos los chunks de una Dimensión específica."""
        return [c for c in self.chunks 
                if c.dimension_causal and c.dimension_causal.value == dimension]


# =============================================================================
# TIPOS PARA ANÁLISIS - Phases 2+
# =============================================================================

@dataclass
class CausalLink:
    """
    Vínculo causal identificado en el PDT.
    Conecta elementos de la cadena de valor DNP (D1→D2→D3→D4→D5).
    
    Crítico para evaluar la coherencia lógica del plan (Dimensión D6).
    """
    source_chunk_id: str
    target_chunk_id: str

    dimension_source: DimensionCausal
    dimension_target: DimensionCausal

    # Tipo de relación
    tipo_relacion: str  # "causa", "temporal", "jerarquica", "geografica"
    conector_textual: Optional[str] = None  # Frase que establece el vínculo
    
    # Ejemplo: "a través de la estructuración y ejecución de proyectos... 
    # que contribuyen al logro de las transformaciones"

    # Fortaleza del vínculo
    confidence: float = 0.0
    explicito: bool = False  # ¿Vínculo explícito o inferido?

    # Trazabilidad
    provenance: Optional[Provenance] = None


@dataclass
class ExtractedEvidence:
    """
    Evidencia extraída para responder una pregunta de análisis.
    Vincula texto específico del PDT con una micro-question del questionnaire.
    """
    question_id: str  # Q001-Q300
    chunk_ids: List[str] = field(default_factory=list)

    # Evidencia textual
    evidencia_textual: str = ""
    evidencia_contraria: Optional[str] = None  # Contraejemplos o inconsistencias

    # Clasificación
    dimension_causal: Optional[DimensionCausal] = None
    policy_area: Optional[PolicyArea] = None
    marcador_contextual: Optional[MarcadorContextual] = None

    # Scoring
    score: float = 0.0
    scoring_level: ScoringLevel = ScoringLevel.INSUFICIENTE
    nivel_confianza: NivelConfianza = NivelConfianza.BAJA

    # Trazabilidad
    provenance: Optional[Provenance] = None


@dataclass
class MicroQuestionResult:
    """
    Resultado de evaluación de una MicroQuestion (Q001-Q300).
    Unidad atómica de análisis del pipeline.
    """
    question_id: str  # Q001-Q300
    question_text: str

    # === Scoring ===
    score: float
    scoring_level: ScoringLevel
    scoring_modality: Optional[str] = None

    # === Evidencias ===
    evidencias: List[ExtractedEvidence] = field(default_factory=list)
    n_evidencias_positivas: int = 0
    n_evidencias_negativas: int = 0

    # === Patrones y métodos aplicados ===
    patterns_matched: List[str] = field(default_factory=list)
    methods_applied: List[str] = field(default_factory=list)

    # === Contexto ===
    dimension_id: Optional[str] = None  # DIM01-DIM06
    policy_area_id: Optional[str] = None  # PA01-PA10
    cluster_id: Optional[str] = None

    # === Hallazgos específicos ===
    hallazgos: List[str] = field(default_factory=list)
    recomendaciones: List[str] = field(default_factory=list)

    # === Trazabilidad y performance ===
    execution_time_ms: Optional[float] = None
    provenance: Optional[Provenance] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MesoQuestionResult:
    """
    Resultado agregado de evaluación de una MesoQuestion (cluster temático).
    Agrega múltiples micro-questions relacionadas.
    """
    question_id: str  # MESO_[ID]
    question_text: str

    # === Scoring agregado ===
    score: float
    scoring_level: ScoringLevel
    aggregation_method: AggregationMethod

    # === Micro questions agregadas ===
    micro_results: List[MicroQuestionResult] = field(default_factory=list)
    n_micro_evaluated: int = 0
    
    # Distribución de scoring
    distribution: Dict[ScoringLevel, int] = field(default_factory=dict)

    # === Contexto ===
    cluster_id: str = ""
    policy_areas: List[str] = field(default_factory=list)

    # === Hallazgos consolidados ===
    hallazgos: List[str] = field(default_factory=list)
    recomendaciones: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MacroQuestionResult:
    """
    Resultado de evaluación holística (MacroQuestion).
    Nivel más alto de agregación, integra múltiples meso-questions.
    """
    score: float
    scoring_level: ScoringLevel
    aggregation_method: AggregationMethod

    # === Meso questions agregadas ===
    meso_results: List[MesoQuestionResult] = field(default_factory=list)
    n_meso_evaluated: int = 0

    # === Hallazgos globales ===
    hallazgos: List[str] = field(default_factory=list)
    recomendaciones: List[str] = field(default_factory=list)
    
    # Fortalezas y debilidades identificadas
    fortalezas: List[str] = field(default_factory=list)
    debilidades: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    """
    Resultado completo del análisis del pipeline F.A.R.F.A.N.
    Representa el output final de todo el proceso de evaluación.
    
    Este es el artefacto que se entrega como resultado del análisis.
    """
    # === Identificación ===
    document_id: str
    municipio: str
    departamento: str = "Cauca"
    periodo: str = "2024-2027"
    analysis_timestamp: datetime = field(default_factory=datetime.now)

    # === Clasificación PDET ===
    es_municipio_pdet: bool = False
    subregion_pdet: Optional[ZonaPDET] = None

    # === Resultados por nivel jerárquico ===
    macro_result: Optional[MacroQuestionResult] = None
    meso_results: List[MesoQuestionResult] = field(default_factory=list)
    micro_results: List[MicroQuestionResult] = field(default_factory=list)

    # === Métricas agregadas globales ===
    overall_score: float = 0.0
    overall_level: ScoringLevel = ScoringLevel.INSUFICIENTE

    # === Scoring por dimensión (cadena de valor) ===
    scores_by_dimension: Dict[str, float] = field(default_factory=dict)
    # {"DIM01": 0.75, "DIM02": 0.82, ...}

    # === Scoring por policy area (derechos) ===
    scores_by_policy_area: Dict[str, float] = field(default_factory=dict)
    # {"PA01": 0.68, "PA05": 0.91, ...}

    # === Matriz de cobertura PA×DIM ===
    coverage_matrix_scores: Dict[Tuple[str, str], float] = field(default_factory=dict)
    # {("PA01", "DIM01"): 0.85, ...}

    # === Hallazgos y recomendaciones consolidadas ===
    hallazgos_principales: List[str] = field(default_factory=list)
    recomendaciones_prioritarias: List[str] = field(default_factory=list)
    
    fortalezas_principales: List[str] = field(default_factory=list)
    debilidades_principales: List[str] = field(default_factory=list)

    # === Evaluación específica PDET (si aplica) ===
    evaluacion_pdet: Optional[Dict[str, Any]] = None
    # {"articulacion_patr": score, "pilares_rri_cubiertos": [...], ...}

    # === Integridad del análisis ===
    questions_executed: int = 0
    questions_total: int = 300
    execution_success: bool = False
    execution_errors: List[str] = field(default_factory=list)

    # === Hashes para verificación de integridad ===
    input_hash: Optional[str] = None  # Hash del documento de entrada
    output_hash: Optional[str] = None  # Hash de este resultado

    # === Performance ===
    total_execution_time_seconds: Optional[float] = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    def compute_overall_score(self) -> float:
        """
        Calcula el score global del análisis.
        Puede usar diferentes estrategias de agregación.
        """
        if self.macro_result:
            self.overall_score = self.macro_result.score
        elif self.meso_results:
            # Promedio ponderado de meso-questions
            self.overall_score = sum(m.score for m in self.meso_results) / len(self.meso_results)
        elif self.micro_results:
            # Promedio simple de micro-questions
            self.overall_score = sum(m.score for m in self.micro_results) / len(self.micro_results)
        
        self.overall_level = ScoringLevel.from_score(self.overall_score)
        return self.overall_score

    def generate_summary_report(self) -> Dict[str, Any]:
        """
        Genera un resumen ejecutivo del análisis.
        Útil para visualización y reportes.
        """
        return {
            "municipio": self.municipio,
            "departamento": self.departamento,
            "periodo": self.periodo,
            "es_pdet": self.es_municipio_pdet,
            "score_global": self.overall_score,
            "nivel_global": self.overall_level.value,
            "fecha_analisis": self.analysis_timestamp.isoformat(),
            "preguntas_evaluadas": f"{self.questions_executed}/{self.questions_total}",
            "fortalezas": self.fortalezas_principales[:5],  # Top 5
            "debilidades": self.debilidades_principales[:5],  # Top 5
            "recomendaciones": self.recomendaciones_prioritarias[:10],  # Top 10
            "scores_por_dimension": self.scores_by_dimension,
            "scores_por_policy_area": self.scores_by_policy_area,
        }


# =============================================================================
# UTILIDADES Y VALIDACIONES
# =============================================================================

def validate_pdt_structure(doc: PreprocessedDocument) -> Dict[str, Any]:
    """
    Valida la estructura de un PDT preprocesado contra los requisitos.
    
    Returns:
        Dict con resultados de validación y errores encontrados.
    """
    errors = []
    warnings = []
    
    # Validar invariante de 60 chunks
    if not doc.validate_chunk_invariant():
        errors.append(f"Invariante de 60 chunks no cumplido. Found: {len(doc.chunks)}")
    
    # Validar completitud de provenance
    if doc.provenance_completeness < 0.9:
        warnings.append(f"Provenance completeness bajo: {doc.provenance_completeness:.2%}")
    
    # Validar secciones obligatorias
    if not doc.diagnostico:
        errors.append("Falta sección de Diagnóstico (obligatoria)")
    
    if not doc.lineas_estrategicas:
        errors.append("Faltan Líneas Estratégicas (obligatorias)")
    
    if not doc.plan_inversiones:
        errors.append("Falta Plan Plurianual de Inversiones (obligatorio)")
    
    # Validar capítulo PDET si es municipio PDET
    if doc.es_municipio_pdet and not doc.capitulo_paz:
        errors.append("Municipio PDET sin Capítulo de Paz (obligatorio)")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "checks_passed": {
            "chunk_invariant": doc.invariant_60_chunks,
            "provenance_complete": doc.provenance_completeness >= 0.9,
            "has_diagnostico": doc.diagnostico is not None,
            "has_estrategia": len(doc.lineas_estrategicas) > 0,
            "has_ppi": doc.plan_inversiones is not None,
            "has_paz_if_pdet": not doc.es_municipio_pdet or doc.capitulo_paz is not None,
        }
    }


def create_empty_preprocessed_document(
    document_id: str,
    source_path: str,
    municipio: str,
    es_pdet: bool = False
) -> PreprocessedDocument:
    """
    Crea un PreprocessedDocument vacío con la estructura básica.
    Útil para inicializar el pipeline.
    """
    return PreprocessedDocument(
        document_id=document_id,
        source_path=source_path,
        municipio=municipio,
        departamento="Cauca",
        periodo="2024-2027",
        es_municipio_pdet=es_pdet,
        extraction_timestamp=datetime.now(),
        extraction_method="unknown"
    )


# =============================================================================
# CONSTANTES DEL DOMINIO
# =============================================================================

# Municipios PDET de la subregión Alto Patía y Norte del Cauca
MUNICIPIOS_PDET_ALTO_PATIA_NORTE_CAUCA = [
    "Buenos Aires", "Caldono", "Caloto", "Corinto", "El Tambo",
    "Jambaló", "Mercaderes", "Miranda", "Morales", "Piendamó",
    "Santander de Quilichao", "Suárez", "Toribío"
]

# ODS relacionados con contexto PDET (Objetivos de Desarrollo Sostenible)
ODS_PDET_PRIORITARIOS = [1, 2, 3, 5, 8, 10, 11, 15, 16]
# 1-Fin pobreza, 2-Hambre cero, 3-Salud, 5-Igualdad género, 
# 8-Trabajo decente, 10-Reducción desigualdades, 11-Ciudades sostenibles,
# 15-Vida ecosistemas terrestres, 16-Paz y justicia

# Sectores presupuestales estándar DNP (ejemplos)
SECTORES_DNP = {
    "12": "Justicia y del Derecho",
    "33": "Salud y Protección Social",
    "41": "Inclusión Social y Reconciliación",
    "43": "Agropecuario",
    "46": "Transporte",
    "47": "Vivienda, Ciudad y Territorio",
}

__version__ = "2.0.0"
__author__ = "F.A.R.F.A.N Policy Analysis Team"

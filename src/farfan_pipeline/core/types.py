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


# Backward compatibility alias
CategoriaCausal = DimensionCausal


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
    """
    id: str
    pattern: str
    match_type: PatternMatchType
    category: str
    context_requirement: Optional[str] = None
    context_scope: PatternContextScope = PatternContextScope.PARAGRAPH
    specificity: PatternSpecificity = PatternSpecificity.MEDIUM
    semantic_expansion: Optional[Union[str, Dict, List]] = None
    synonym_clusters: Optional[List[str]] = None
    validation_rule: Optional[str] = None
    confidence_weight: Optional[float] = None
    negative_filter: Optional[bool] = None
    entity_type: Optional[str] = None
    element_tags: Optional[List[str]] = None
    pattern_ref: Optional[str] = None

    def matches(self, text: str, context: Optional[str] = None) -> bool:
        """Verifica si el patrón hace match con el texto."""
        if self.match_type == PatternMatchType.LITERAL:
            return self.pattern.lower() in text.lower()
        elif self.match_type == PatternMatchType.REGEX:
            return bool(re.search(self.pattern, text, re.IGNORECASE))
        elif self.match_type == PatternMatchType.NER_OR_REGEX:
            return bool(re.search(self.pattern, text, re.IGNORECASE))
        return False


@dataclass
class MethodSet:
    """
    Conjunto de métodos analíticos para una pregunta.
    Alineado con definitions.MethodSet del questionnaire_schema.json
    """
    class_name: str
    function: str
    method_type: MethodType
    priority: int = 0
    description: Optional[str] = None
    depends_on_patterns: List[str] = field(default_factory=list)
    pattern_dependencies: List[str] = field(default_factory=list)
    produces_elements: List[str] = field(default_factory=list)
    output_validates: List[str] = field(default_factory=list)
    failure_mode: Optional[str] = None


@dataclass
class MicroQuestion:
    """
    Pregunta micro del cuestionario (300 preguntas Q001-Q300).
    Representa la unidad atómica de análisis del PDT.
    """
    question_id: str
    text: str
    cluster_id: str
    dimension_id: str
    policy_area_id: Optional[str] = None
    base_slot: Optional[str] = None
    question_global: Optional[int] = None
    scoring_modality: Optional[str] = None
    scoring_definition_ref: Optional[str] = None
    expected_elements: List[str] = field(default_factory=list)
    failure_contract: Optional[Dict[str, Any]] = None
    method_sets: List[MethodSet] = field(default_factory=list)
    patterns: List[PatternItem] = field(default_factory=list)
    validations: Optional[Dict[str, Any]] = None


@dataclass
class MesoQuestion:
    """
    Pregunta meso del cuestionario (clusters temáticos).
    Agrega múltiples micro-questions relacionadas temáticamente.
    """
    question_id: str
    cluster_id: str
    text: str
    type: str
    question_global: Optional[int] = None
    aggregation_method: Optional[str] = None
    scoring_modality: Optional[str] = None
    policy_areas: List[str] = field(default_factory=list)
    patterns: List[Dict[str, Any]] = field(default_factory=list)
    micro_question_ids: List[str] = field(default_factory=list)


@dataclass
class MacroQuestion:
    """
    Pregunta macro del cuestionario (evaluación holística).
    Evaluación de más alto nivel que integra múltiples meso-questions.
    """
    question_global: int
    aggregation_method: AggregationMethod
    clusters: List[str] = field(default_factory=list)
    patterns: List[Dict[str, Any]] = field(default_factory=list)
    fallback: Optional[Dict[str, Any]] = None


# =============================================================================
# TIPOS DE DOMINIO PDT - Estructura Jerárquica
# =============================================================================

@dataclass
class EntidadInstitucional:
    """Entidad institucional colombiana referenciada en el PDT."""
    nombre: str
    sigla: Optional[str] = None
    tipo: TipoEntidadInstitucional = TipoEntidadInstitucional.MUNICIPAL
    rol: Optional[str] = None
    nivel_gobierno: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReferenciaLegal:
    """Referencia a normativa colombiana citada en el PDT."""
    tipo: TipoReferenciaLegal
    numero: str
    año: int
    articulo: Optional[str] = None
    descripcion: Optional[str] = None
    texto_completo: Optional[str] = None


@dataclass
class Meta:
    """Meta cuantificable del PDT con indicador, línea base y objetivo."""
    codigo: Optional[str] = None
    descripcion: str = ""
    tipo_indicador: TipoIndicador = TipoIndicador.PRODUCTO
    indicador_nombre: str = ""
    codigo_indicador: Optional[str] = None
    unidad_medida: str = ""
    linea_base: Optional[float] = None
    año_linea_base: Optional[int] = None
    meta_cuatrienio: Optional[float] = None
    meta_2024: Optional[float] = None
    meta_2025: Optional[float] = None
    meta_2026: Optional[float] = None
    meta_2027: Optional[float] = None
    fuente_informacion: Optional[str] = None
    responsable: Optional[str] = None
    poblacion_objetivo: Optional[str] = None
    provenance: Optional[Provenance] = None


@dataclass
class Producto:
    """Producto del PDT codificado según catálogo MGA del DNP."""
    codigo_mga: Optional[str] = None
    nombre: str = ""
    descripcion: str = ""
    indicadores: List[Meta] = field(default_factory=list)
    costo_total: Optional[float] = None
    fuentes_financiacion: Dict[FuenteFinanciacion, float] = field(default_factory=dict)
    alcance_geografico: Optional[str] = None
    poblacion_beneficiaria: Optional[str] = None
    provenance: Optional[Provenance] = None


@dataclass
class Programa:
    """Programa presupuestal del PDT que agrupa productos relacionados."""
    codigo_presupuestal: Optional[str] = None
    nombre: str = ""
    descripcion: str = ""
    sector: Optional[str] = None
    productos: List[Producto] = field(default_factory=list)
    metas_resultado: List[Meta] = field(default_factory=list)
    costo_total_cuatrienio: Optional[float] = None
    distribucion_anual: Dict[int, float] = field(default_factory=dict)
    justificacion: Optional[str] = None
    problematicas_atendidas: List[str] = field(default_factory=list)
    provenance: Optional[Provenance] = None


@dataclass
class LineaEstrategica:
    """Línea/Eje estratégico del PDT - nivel más alto de organización programática."""
    codigo: Optional[str] = None
    numero: Optional[int] = None
    titulo: str = ""
    descripcion: Optional[str] = None
    enfoques: List[str] = field(default_factory=list)
    programas: List[Programa] = field(default_factory=list)
    inversion_total: Optional[float] = None
    distribucion_anual: Dict[int, float] = field(default_factory=dict)
    ods_vinculados: List[int] = field(default_factory=list)
    vinculacion_pnd: Optional[str] = None
    provenance: Optional[Provenance] = None


@dataclass
class DiagnosticoTerritorial:
    """Información del diagnóstico/caracterización del PDT."""
    poblacion_total: Optional[int] = None
    poblacion_urbana: Optional[int] = None
    poblacion_rural: Optional[int] = None
    poblacion_etnica: Optional[Dict[str, int]] = None
    indice_pobreza_multidimensional: Optional[float] = None
    nbi: Optional[float] = None
    cobertura_salud: Optional[Dict[str, int]] = None
    tasas_educacion: Optional[Dict[str, float]] = None
    problematicas: List[str] = field(default_factory=list)
    brechas: List[str] = field(default_factory=list)
    ejes_problematicos: List[str] = field(default_factory=list)
    corregimientos: List[str] = field(default_factory=list)
    veredas: List[str] = field(default_factory=list)
    consejos_comunitarios: List[str] = field(default_factory=list)
    tiene_pot: bool = False
    tiene_pbot: bool = False
    tiene_eot: bool = False
    fecha_actualizacion_ot: Optional[datetime] = None
    provenance: Optional[Provenance] = None


@dataclass
class PlanPlurianuaInversiones:
    """Plan Plurianual de Inversiones (PPI) - Componente financiero del PDT."""
    total_2024: Optional[float] = None
    total_2025: Optional[float] = None
    total_2026: Optional[float] = None
    total_2027: Optional[float] = None
    total_cuatrienio: Optional[float] = None
    total_sgp: Optional[float] = None
    total_sgr: Optional[float] = None
    total_recursos_propios: Optional[float] = None
    total_credito: Optional[float] = None
    total_cooperacion: Optional[float] = None
    total_otras_fuentes: Optional[float] = None
    matriz_inversiones: List[Dict[str, Any]] = field(default_factory=list)
    marco_fiscal_mediano_plazo: Optional[Dict[str, Any]] = None
    sostenibilidad_fiscal: Optional[str] = None
    provenance: Optional[Provenance] = None


@dataclass
class IniciativaPDET:
    """Iniciativa específica del PDET vinculada al capítulo de paz."""
    codigo: Optional[str] = None
    nombre: str = ""
    descripcion: str = ""
    pilar_rri: PilarRRI = PilarRRI.PILAR_1_ORDENAMIENTO
    linea_accion: Optional[str] = None
    programa_vinculado: Optional[str] = None
    presupuesto_asignado: Optional[float] = None
    corregimientos_veredas: List[str] = field(default_factory=list)
    provenance: Optional[Provenance] = None


@dataclass
class CapituloPaz:
    """Capítulo de Paz/PDET - Obligatorio en municipios PDET."""
    es_municipio_pdet: bool = False
    subregion_pdet: Optional[ZonaPDET] = None
    iniciativas_pdet: List[IniciativaPDET] = field(default_factory=list)
    total_iniciativas_priorizadas: int = 0
    pilares_abordados: List[PilarRRI] = field(default_factory=list)
    articulacion_pmi: Optional[str] = None
    articulacion_patr: Optional[str] = None
    articulacion_pnis: Optional[str] = None
    presupuesto_total_paz: Optional[float] = None
    fuentes_paz: Dict[FuenteFinanciacion, float] = field(default_factory=dict)
    victimas_conflicto: Optional[int] = None
    excombatientes: Optional[int] = None
    comunidades_etnicas_beneficiadas: List[str] = field(default_factory=list)
    metas_reconciliacion: List[Meta] = field(default_factory=list)
    metas_reintegracion: List[Meta] = field(default_factory=list)
    metas_reparacion_victimas: List[Meta] = field(default_factory=list)
    entidades_coordinacion: List[EntidadInstitucional] = field(default_factory=list)
    provenance: Optional[Provenance] = None


# =============================================================================
# DOCUMENTO PREPROCESADO - Output de Phase 1
# =============================================================================

@dataclass
class PreprocessedDocument:
    """
    Documento PDT después de preprocesamiento - Output canónico de Phase 1.
    
    INVARIANTE CRÍTICO: chunk_count == 60 (10 Policy Areas × 6 Dimensions)
    """
    document_id: str
    source_path: str
    municipio: Optional[str] = None
    departamento: str = "Cauca"
    periodo: str = "2024-2027"
    es_municipio_pdet: bool = False
    subregion_pdet: Optional[ZonaPDET] = None
    chunks: List[ChunkData] = field(default_factory=list)
    diagnostico: Optional[DiagnosticoTerritorial] = None
    lineas_estrategicas: List[LineaEstrategica] = field(default_factory=list)
    plan_inversiones: Optional[PlanPlurianuaInversiones] = None
    capitulo_paz: Optional[CapituloPaz] = None
    entidades_mencionadas: List[EntidadInstitucional] = field(default_factory=list)
    referencias_legales: List[ReferenciaLegal] = field(default_factory=list)
    total_pages: int = 0
    extraction_timestamp: Optional[datetime] = None
    extraction_method: str = "unknown"
    provenance_completeness: float = 0.0
    chunks_with_provenance: int = 0
    chunks_total: int = 0
    invariant_60_chunks: bool = False
    coverage_matrix: Dict[Tuple[str, str], bool] = field(default_factory=dict)
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
        """Valida el invariante de 60 chunks (10 PA × 6 DIM)."""
        self.invariant_60_chunks = len(self.chunks) == 60
        self.coverage_matrix = {}
        for pa_num in range(1, 11):
            for dim_num in range(1, 7):
                pa_id = f"PA{pa_num:02d}"
                dim_id = f"DIM{dim_num:02d}"
                coord = (pa_id, dim_id)
                has_chunk = any(
                    c.policy_area and c.dimension_causal and
                    c.policy_area.value == pa_id and c.dimension_causal.value == dim_id
                    for c in self.chunks
                )
                self.coverage_matrix[coord] = has_chunk
        full_coverage = all(self.coverage_matrix.values())
        return self.invariant_60_chunks and full_coverage

    def get_chunk_by_coordinate(self, policy_area: str, dimension: str) -> Optional[ChunkData]:
        """Obtiene chunk específico por coordenada (PA, DIM)."""
        for chunk in self.chunks:
            if (chunk.policy_area and chunk.policy_area.value == policy_area and
                chunk.dimension_causal and chunk.dimension_causal.value == dimension):
                return chunk
        return None


# =============================================================================
# TIPOS PARA ANÁLISIS - Phases 2+
# =============================================================================

@dataclass
class CausalLink:
    """Vínculo causal identificado en el PDT."""
    source_chunk_id: str
    target_chunk_id: str
    dimension_source: DimensionCausal
    dimension_target: DimensionCausal
    tipo_relacion: str
    conector_textual: Optional[str] = None
    confidence: float = 0.0
    explicito: bool = False
    provenance: Optional[Provenance] = None


@dataclass
class ExtractedEvidence:
    """Evidencia extraída para responder una pregunta de análisis."""
    question_id: str
    chunk_ids: List[str] = field(default_factory=list)
    evidencia_textual: str = ""
    evidencia_contraria: Optional[str] = None
    dimension_causal: Optional[DimensionCausal] = None
    policy_area: Optional[PolicyArea] = None
    marcador_contextual: Optional[MarcadorContextual] = None
    score: float = 0.0
    scoring_level: ScoringLevel = ScoringLevel.INSUFICIENTE
    nivel_confianza: NivelConfianza = NivelConfianza.BAJA
    provenance: Optional[Provenance] = None


@dataclass
class MicroQuestionResult:
    """Resultado de evaluación de una MicroQuestion (Q001-Q300)."""
    question_id: str
    question_text: str
    score: float
    scoring_level: ScoringLevel
    scoring_modality: Optional[str] = None
    evidencias: List[ExtractedEvidence] = field(default_factory=list)
    n_evidencias_positivas: int = 0
    n_evidencias_negativas: int = 0
    patterns_matched: List[str] = field(default_factory=list)
    methods_applied: List[str] = field(default_factory=list)
    dimension_id: Optional[str] = None
    policy_area_id: Optional[str] = None
    cluster_id: Optional[str] = None
    hallazgos: List[str] = field(default_factory=list)
    recomendaciones: List[str] = field(default_factory=list)
    execution_time_ms: Optional[float] = None
    provenance: Optional[Provenance] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MesoQuestionResult:
    """Resultado agregado de evaluación de una MesoQuestion."""
    question_id: str
    question_text: str
    score: float
    scoring_level: ScoringLevel
    aggregation_method: AggregationMethod
    micro_results: List[MicroQuestionResult] = field(default_factory=list)
    n_micro_evaluated: int = 0
    distribution: Dict[ScoringLevel, int] = field(default_factory=dict)
    cluster_id: str = ""
    policy_areas: List[str] = field(default_factory=list)
    hallazgos: List[str] = field(default_factory=list)
    recomendaciones: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MacroQuestionResult:
    """Resultado de evaluación holística (MacroQuestion)."""
    score: float
    scoring_level: ScoringLevel
    aggregation_method: AggregationMethod
    meso_results: List[MesoQuestionResult] = field(default_factory=list)
    n_meso_evaluated: int = 0
    hallazgos: List[str] = field(default_factory=list)
    recomendaciones: List[str] = field(default_factory=list)
    fortalezas: List[str] = field(default_factory=list)
    debilidades: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    """Resultado completo del análisis del pipeline F.A.R.F.A.N."""
    document_id: str
    municipio: str
    departamento: str = "Cauca"
    periodo: str = "2024-2027"
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    es_municipio_pdet: bool = False
    subregion_pdet: Optional[ZonaPDET] = None
    macro_result: Optional[MacroQuestionResult] = None
    meso_results: List[MesoQuestionResult] = field(default_factory=list)
    micro_results: List[MicroQuestionResult] = field(default_factory=list)
    overall_score: float = 0.0
    overall_level: ScoringLevel = ScoringLevel.INSUFICIENTE
    scores_by_dimension: Dict[str, float] = field(default_factory=dict)
    scores_by_policy_area: Dict[str, float] = field(default_factory=dict)
    coverage_matrix_scores: Dict[Tuple[str, str], float] = field(default_factory=dict)
    hallazgos_principales: List[str] = field(default_factory=list)
    recomendaciones_prioritarias: List[str] = field(default_factory=list)
    fortalezas_principales: List[str] = field(default_factory=list)
    debilidades_principales: List[str] = field(default_factory=list)
    evaluacion_pdet: Optional[Dict[str, Any]] = None
    questions_executed: int = 0
    questions_total: int = 300
    execution_success: bool = False
    execution_errors: List[str] = field(default_factory=list)
    input_hash: Optional[str] = None
    output_hash: Optional[str] = None
    total_execution_time_seconds: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def compute_overall_score(self) -> float:
        """Calcula el score global del análisis."""
        if self.macro_result:
            self.overall_score = self.macro_result.score
        elif self.meso_results:
            self.overall_score = sum(m.score for m in self.meso_results) / len(self.meso_results)
        elif self.micro_results:
            self.overall_score = sum(m.score for m in self.micro_results) / len(self.micro_results)
        self.overall_level = ScoringLevel.from_score(self.overall_score)
        return self.overall_score


# =============================================================================
# UTILIDADES Y VALIDACIONES
# =============================================================================

def validate_pdt_structure(doc: PreprocessedDocument) -> Dict[str, Any]:
    """Valida la estructura de un PDT preprocesado contra los requisitos."""
    errors = []
    warnings = []
    
    if not doc.validate_chunk_invariant():
        errors.append(f"Invariante de 60 chunks no cumplido. Found: {len(doc.chunks)}")
    
    if doc.provenance_completeness < 0.9:
        warnings.append(f"Provenance completeness bajo: {doc.provenance_completeness:.2%}")
    
    if not doc.diagnostico:
        errors.append("Falta sección de Diagnóstico (obligatoria)")
    
    if not doc.lineas_estrategicas:
        errors.append("Faltan Líneas Estratégicas (obligatorias)")
    
    if not doc.plan_inversiones:
        errors.append("Falta Plan Plurianual de Inversiones (obligatorio)")
    
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


# =============================================================================
# CONSTANTES DEL DOMINIO
# =============================================================================

MUNICIPIOS_PDET_ALTO_PATIA_NORTE_CAUCA = [
    "Buenos Aires", "Caldono", "Caloto", "Corinto", "El Tambo",
    "Jambaló", "Mercaderes", "Miranda", "Morales", "Piendamó",
    "Santander de Quilichao", "Suárez", "Toribío"
]

ODS_PDET_PRIORITARIOS = [1, 2, 3, 5, 8, 10, 11, 15, 16]

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

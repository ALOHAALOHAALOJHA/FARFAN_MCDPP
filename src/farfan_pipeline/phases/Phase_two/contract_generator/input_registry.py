"""
Módulo:  input_registry.py
Propósito: Cargar, validar e indexar todos los insumos como registro inmutable

Ubicación: src/farfan_pipeline/phases/Phase_two/contract_generator/input_registry. py

RESPONSABILIDADES: 
1. Cargar los 3 archivos JSON de insumos
2. Validar estructura y contenido de cada archivo
3. Construir objetos tipados inmutables
4. Crear índices para acceso eficiente
5. Validar referencias cruzadas (E-001: coherencia nivel-fase)
6. Proveer registro inmutable para el resto del sistema

ARCHIVOS DE ENTRADA:
- classified_methods. json: Dispensario de 608 métodos clasificados
- contratos_clasificados.json: 30 contratos base con clasificación
- method_sets_by_question.json: Asignaciones de métodos por pregunta

INVARIANTES: 
- Todos los objetos retornados son inmutables (frozen dataclasses)
- El orden de métodos se preserva exactamente como en el input
- Falla duro ante cualquier inconsistencia

Versión: 4.0.0-granular
Fecha: 2026-01-03
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ══════════════════════════════════════════════════════════════════════════════

EXPECTED_BASE_CONTRACTS = 30
EXPECTED_SECTORS = 10
EXPECTED_TOTAL_CONTRACTS = EXPECTED_BASE_CONTRACTS * EXPECTED_SECTORS  # 300

VALID_EPISTEMOLOGICAL_LEVELS = frozenset({
    "N0-INFRA",
    "N1-EMP",
    "N2-INF",
    "N3-AUD",
    "N4-META",
})

VALID_CONTRACT_LEVELS = frozenset({
    "N1-EMP",
    "N2-INF",
    "N3-AUD",
})

VALID_CONTRACT_TYPES = frozenset({
    "TYPE_A",
    "TYPE_B",
    "TYPE_C",
    "TYPE_D",
    "TYPE_E",
})

VALID_OUTPUT_TYPES = frozenset({
    "INFRASTRUCTURE",
    "FACT",
    "PARAMETER",
    "CONSTRAINT",
    "META_ANALYSIS",
})

VALID_FUSION_BEHAVIORS = frozenset({
    "additive",
    "multiplicative",
    "gate",
    "terminal",
    "none",
})

# ══════════════════════════════════════════════════════════════════════════════
# SECTORES CANÓNICOS (FUENTE: monolith)
# ══════════════════════════════════════════════════════════════════════════════

SECTOR_DEFINITIONS:  dict[str, dict[str, str]] = {
    "PA01": {
        "canonical_id": "PA01",
        "canonical_name": "Derechos de las mujeres e igualdad de género",
    },
    "PA02": {
        "canonical_id": "PA02",
        "canonical_name": (
            "Prevención de la violencia y protección de la población frente al "
            "conflicto armado y la violencia generada por grupos delincuenciales "
            "organizados, asociada a economías ilegales"
        ),
    },
    "PA03": {
        "canonical_id": "PA03",
        "canonical_name":  "Ambiente sano, cambio climático, prevención y atención a desastres",
    },
    "PA04": {
        "canonical_id": "PA04",
        "canonical_name": "Derechos económicos, sociales y culturales",
    },
    "PA05":  {
        "canonical_id":  "PA05",
        "canonical_name": "Derechos de las víctimas y construcción de paz",
    },
    "PA06": {
        "canonical_id": "PA06",
        "canonical_name": (
            "Derecho al buen futuro de la niñez, adolescencia, juventud "
            "y entornos protectores"
        ),
    },
    "PA07": {
        "canonical_id": "PA07",
        "canonical_name": "Tierras y territorios",
    },
    "PA08": {
        "canonical_id": "PA08",
        "canonical_name": (
            "Líderes y lideresas, defensores y defensoras de derechos humanos, "
            "comunitarios, sociales, ambientales, de la tierra, el territorio "
            "y de la naturaleza"
        ),
    },
    "PA09": {
        "canonical_id": "PA09",
        "canonical_name": "Crisis de derechos de personas privadas de la libertad",
    },
    "PA10": {
        "canonical_id": "PA10",
        "canonical_name":  "Migración transfronteriza",
    },
}

LOADER_VERSION = "4.0.0-granular"


# ══════════════════════════════════════════════════════════════════════════════
# DATACLASSES INMUTABLES - DEFINICIONES DE MÉTODOS
# ══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class MethodDefinition:
    """
    Definición completa de un método del dispensario. 

    Representa un método tal como está clasificado en classified_methods.json. 
    INMUTABLE después de carga.

    Atributos:
        class_name:  Nombre de la clase que contiene el método
        method_name:  Nombre del método
        mother_file: Archivo fuente donde está definido
        provides:  Identificador de lo que provee (formato: classname. methodname)
        level: Nivel epistemológico (N0-INFRA, N1-EMP, N2-INF, N3-AUD, N4-META)
        level_name: Nombre descriptivo del nivel
        epistemology: Marco epistemológico aplicable
        output_type: Tipo de output (INFRASTRUCTURE, FACT, PARAMETER, CONSTRAINT, META_ANALYSIS)
        fusion_behavior:  Comportamiento de fusión (additive, multiplicative, gate, terminal)
        fusion_symbol: Símbolo de fusión (⊕, ⊗, ⊘, ⊙)
        classification_rationale: Justificación de la clasificación
        confidence_score: Score de confianza de la clasificación (0.0 - 1.0)
        contract_affinities: Afinidades con tipos de contrato {TYPE_X:  score}
        parameters: Parámetros del método
        return_type: Tipo de retorno
        is_private: Si el método es privado (prefijo _)
    """
    class_name: str
    method_name: str
    mother_file: str
    provides:  str
    level: str
    level_name: str
    epistemology: str
    output_type: str
    fusion_behavior: str
    fusion_symbol:  str
    classification_rationale:  str
    confidence_score: float
    contract_affinities:  dict[str, float]
    parameters: tuple[str, ...]
    return_type: str
    is_private: bool

    @property
    def full_id(self) -> str:
        """Identificador único del método:  ClassName.method_name"""
        return f"{self.class_name}.{self.method_name}"

    @property
    def level_prefix(self) -> str:
        """Prefijo del nivel (N0, N1, N2, N3, N4)"""
        return self.level.split("-")[0] if "-" in self.level else self.level

    def has_affinity_for(self, contract_type: str, threshold: float = 0.5) -> bool:
        """Verifica si tiene afinidad suficiente con un tipo de contrato."""
        return self.contract_affinities.get(contract_type, 0.0) >= threshold


@dataclass(frozen=True)
class ContractClassification:
    """
    Clasificación de un contrato según contratos_clasificados.json. 

    Representa la clasificación epistémica de una pregunta base.
    INMUTABLE. 

    Atributos: 
        contract_id: ID del contrato (Q001, Q002, etc.)
        dimension_key: Clave de dimensión (D1_Q1, D1_Q2, etc.)
        pregunta:  Texto completo de la pregunta
        tipo_contrato: Diccionario con {codigo, nombre, foco}
        niveles_epistemologicos_requeridos: Niveles requeridos por fase
        estrategias_fusion: Estrategias de fusión por nivel {N1:  strategy, N2: strategy, N3: strategy}
        roles_argumentativos: Roles argumentativos aplicables
        clases_dominantes: Clases dominantes para este contrato
    """
    contract_id: str
    dimension_key: str
    pregunta: str
    tipo_contrato: dict[str, str]
    niveles_epistemologicos_requeridos:  dict[str, dict[str, str]]
    estrategias_fusion: dict[str, str]
    roles_argumentativos: tuple[str, ...]
    clases_dominantes: tuple[str, ...]

    @property
    def type_code(self) -> str:
        """Código del tipo de contrato (TYPE_A, TYPE_B, etc.)"""
        return self. tipo_contrato.get("codigo", "")

    @property
    def type_name(self) -> str:
        """Nombre del tipo de contrato (Semántico, Bayesiano, etc.)"""
        return self.tipo_contrato. get("nombre", "")

    @property
    def type_focus(self) -> str:
        """Foco del tipo de contrato"""
        return self.tipo_contrato.get("foco", "")

    @property
    def dimension_number(self) -> int:
        """Número de dimensión extraído de dimension_key (D1_Q1 -> 1)"""
        if self.dimension_key and self.dimension_key.startswith("D"):
            try:
                return int(self. dimension_key[1:2])
            except ValueError:
                return 0
        return 0

    @property
    def question_number(self) -> int:
        """Número de pregunta extraído de dimension_key (D1_Q1 -> 1)"""
        if "_Q" in self.dimension_key:
            try:
                return int(self. dimension_key.split("_Q")[1])
            except (ValueError, IndexError):
                return 0
        return 0


@dataclass(frozen=True)
class MethodAssignment:
    """
    Asignación de un método a una pregunta específica.

    Proviene de method_sets_by_question.json.
    INMUTABLE. 

    Contiene toda la información necesaria para expandir el método
    en el contexto de un contrato específico.
    """
    class_name: str
    method_name: str
    mother_file: str
    provides:  str
    level: str
    level_name: str
    epistemology: str
    output_type: str
    fusion_behavior: str
    fusion_symbol:  str
    classification_rationale:  str
    confidence_score: float
    contract_affinities:  dict[str, float]
    parameters: tuple[str, ...]
    return_type: str
    is_private: bool

    @property
    def full_id(self) -> str:
        """Identificador único del método: ClassName.method_name"""
        return f"{self. class_name}.{self.method_name}"

    @property
    def level_prefix(self) -> str:
        """Prefijo del nivel (N1, N2, N3)"""
        return self.level. split("-")[0] if "-" in self.level else self.level

    @property
    def is_low_confidence(self) -> bool:
        """Indica si el método tiene baja confianza (< 0.7)"""
        return self.confidence_score < 0.7


@dataclass(frozen=True)
class QuestionMethodSet:
    """
    Conjunto de métodos asignados a una pregunta. 

    Proviene de method_sets_by_question.json. 
    INMUTABLE.

    Representa la asignación completa de métodos para una pregunta base,
    organizada por fase epistémica.
    """
    question_id: str
    contract_type: dict[str, str]
    phase_a_N1: tuple[MethodAssignment, ...]
    phase_b_N2: tuple[MethodAssignment, ...]
    phase_c_N3: tuple[MethodAssignment, ...]
    efficiency_score: float
    mathematical_evidence: dict[str, Any]
    doctoral_justification: str

    @property
    def all_methods_ordered(self) -> tuple[MethodAssignment, ...]: 
        """Retorna todos los métodos en orden epistémico:  N1 → N2 → N3"""
        return self.phase_a_N1 + self.phase_b_N2 + self.phase_c_N3

    @property
    def total_methods(self) -> int:
        """Número total de métodos asignados"""
        return len(self.phase_a_N1) + len(self.phase_b_N2) + len(self.phase_c_N3)

    @property
    def n1_count(self) -> int:
        """Número de métodos N1"""
        return len(self.phase_a_N1)

    @property
    def n2_count(self) -> int:
        """Número de métodos N2"""
        return len(self.phase_b_N2)

    @property
    def n3_count(self) -> int:
        """Número de métodos N3"""
        return len(self.phase_c_N3)

    @property
    def type_code(self) -> str:
        """Código del tipo de contrato"""
        return self.contract_type.get("code", "")

    @property
    def has_low_confidence_methods(self) -> bool:
        """Indica si hay métodos con baja confianza"""
        return any(m.is_low_confidence for m in self.all_methods_ordered)

    def get_low_confidence_methods(self) -> tuple[MethodAssignment, ...]: 
        """Retorna métodos con baja confianza"""
        return tuple(m for m in self.all_methods_ordered if m.is_low_confidence)


@dataclass(frozen=True)
class SectorDefinition:
    """
    Definición de un sector/área de política.

    INMUTABLE. 
    """
    sector_id: str
    canonical_name: str

    @property
    def short_name(self) -> str:
        """Nombre corto (primeras 50 caracteres)"""
        if len(self.canonical_name) <= 50:
            return self.canonical_name
        return self.canonical_name[:47] + "..."


# ══════════════════════════════════════════════════════════════════════════════
# DATACLASS PRINCIPAL - REGISTRO INMUTABLE
# ══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class InputRegistry:
    """
    Registro inmutable de todos los insumos. 

    Una vez construido, no puede modificarse.
    Provee acceso indexado a todos los datos necesarios para generación. 

    Atributos:
        classified_methods_hash: Hash SHA256 truncado del archivo de métodos
        contratos_clasificados_hash: Hash SHA256 truncado del archivo de contratos
        method_sets_hash: Hash SHA256 truncado del archivo de asignaciones
        methods_by_full_id: Índice de métodos por full_id
        methods_by_level:  Índice de métodos por nivel epistémico
        methods_by_class: Índice de métodos por clase
        contracts_by_id: Índice de contratos por dimension_key
        contracts_by_type: Índice de contratos por tipo
        contracts_by_contract_id: Índice de contratos por contract_id (Q001, etc.)
        method_sets_by_question:  Asignaciones de métodos por pregunta
        sectors:  Definiciones de sectores
        total_methods: Total de métodos en el dispensario
        total_contracts: Total de contratos base (30)
        total_sectors: Total de sectores (10)
        level_counts: Conteo de métodos por nivel
        load_timestamp: Timestamp de carga
        loader_version: Versión del loader
    """
    # Hashes para trazabilidad
    classified_methods_hash: str
    contratos_clasificados_hash: str
    method_sets_hash: str

    # Índices de métodos
    methods_by_full_id: dict[str, MethodDefinition]
    methods_by_level: dict[str, tuple[MethodDefinition, ...]]
    methods_by_class:  dict[str, tuple[MethodDefinition, ...]]

    # Índices de contratos
    contracts_by_id:  dict[str, ContractClassification]
    contracts_by_type: dict[str, tuple[ContractClassification, ...]]
    contracts_by_contract_id: dict[str, ContractClassification]

    # Asignaciones autoritativas
    method_sets_by_question: dict[str, QuestionMethodSet]

    # Sectores
    sectors: dict[str, SectorDefinition]

    # Estadísticas
    total_methods:  int
    total_contracts: int
    total_sectors: int
    level_counts: dict[str, int]

    # Metadata
    load_timestamp: str
    loader_version: str

    def get_method(self, full_id: str) -> MethodDefinition | None:
        """Obtiene un método por su full_id."""
        return self.methods_by_full_id.get(full_id)

    def get_contract(self, dimension_key: str) -> ContractClassification | None:
        """Obtiene un contrato por su dimension_key (D1_Q1, etc.)."""
        return self.contracts_by_id.get(dimension_key)

    def get_contract_by_qid(self, contract_id: str) -> ContractClassification | None:
        """Obtiene un contrato por su contract_id (Q001, etc.)."""
        return self.contracts_by_contract_id.get(contract_id)

    def get_method_set(self, question_id: str) -> QuestionMethodSet | None:
        """Obtiene el set de métodos para una pregunta."""
        return self.method_sets_by_question.get(question_id)

    def get_sector(self, sector_id:  str) -> SectorDefinition | None:
        """Obtiene la definición de un sector."""
        return self.sectors.get(sector_id)

    def get_methods_for_level(self, level: str) -> tuple[MethodDefinition, ... ]: 
        """Obtiene todos los métodos de un nivel específico."""
        return self.methods_by_level.get(level, ())

    def get_contracts_for_type(self, type_code: str) -> tuple[ContractClassification, ...]: 
        """Obtiene todos los contratos de un tipo específico."""
        return self.contracts_by_type. get(type_code, ())

    def iter_all_contract_sector_pairs(self):
        """
        Itera sobre todos los pares (contrato, sector) para generar 300 contratos. 

        Yields:
            Tuplas de (ContractClassification, SectorDefinition, contract_number)
            donde contract_number va de 1 a 300.
        """
        contract_number = 0
        for sector_idx, sector_id in enumerate(sorted(self.sectors.keys())):
            sector = self.sectors[sector_id]
            for contract in sorted(self.contracts_by_id.values(), key=lambda c: c.contract_id):
                contract_number += 1
                yield contract, sector, contract_number


# ══════════════════════════════════════════════════════════════════════════════
# CLASE CARGADORA
# ══════════════════════════════════════════════════════════════════════════════


class InputLoader:
    """
    Cargador de insumos con validación estricta.

    PROPIEDADES GARANTIZADAS:
    1. Carga determinista (orden de claves preservado)
    2. Validación exhaustiva antes de construir registro
    3. Hash de inputs para trazabilidad
    4. Fallo duro si cualquier validación falla

    USO:
        loader = InputLoader(Path("path/to/epistemological_assets"))
        registry = loader.load_and_validate()
    """

    def __init__(self, assets_path: Path):
        """
        Inicializa el loader. 

        Args:
            assets_path: Ruta al directorio que contiene los archivos JSON
        """
        self.assets_path = Path(assets_path)
        if not self.assets_path.exists():
            raise FileNotFoundError(
                f"HARD FAILURE: Assets directory not found:  {self.assets_path}"
            )
        if not self.assets_path.is_dir():
            raise ValueError(
                f"HARD FAILURE:  Assets path is not a directory: {self. assets_path}"
            )

    def load_and_validate(self) -> InputRegistry:
        """
        Carga todos los insumos y construye registro inmutable.

        SECUENCIA:
        1. Cargar JSONs con orden preservado
        2. Calcular hashes
        3. Validar estructuras
        4. Construir objetos tipados
        5. Construir índices
        6. Validar referencias cruzadas
        7. Retornar registro inmutable

        Returns:
            InputRegistry inmutable con todos los datos indexados

        Raises:
            FileNotFoundError: Si un archivo requerido no existe
            ValueError:  Si la estructura o contenido es inválido
            json.JSONDecodeError: Si un archivo JSON está malformado
        """
        logger.info(f"Loading inputs from {self.assets_path}")

        # ══════════════════════════════════════════════════════════════════
        # PASO 1: Cargar JSONs
        # ══════════════════════════════════════════════════════════════════
        classified_methods_raw = self._load_json("classified_methods.json")
        contratos_clasificados_raw = self._load_json("contratos_clasificados. json")
        method_sets_raw = self._load_json("method_sets_by_question.json")

        logger.debug("  All JSON files loaded successfully")

        # ══════════════════════════════════════════════════════════════════
        # PASO 2: Calcular hashes (para reproducibilidad)
        # ══════════════════════════════════════════════════════════════════
        cm_hash = self._compute_hash(classified_methods_raw)
        cc_hash = self._compute_hash(contratos_clasificados_raw)
        ms_hash = self._compute_hash(method_sets_raw)

        logger.debug(f"  Hashes computed: CM={cm_hash}, CC={cc_hash}, MS={ms_hash}")

        # ══════════════════════════════════════════════════════════════════
        # PASO 3: Validar estructuras
        # ══════════════════════════════════════════════════════════════════
        self._validate_classified_methods_structure(classified_methods_raw)
        self._validate_contratos_clasificados_structure(contratos_clasificados_raw)
        self._validate_method_sets_structure(method_sets_raw)

        logger.debug("  All structures validated")

        # ══════════════════════════════════════════════════════════════════
        # PASO 4: Construir objetos tipados
        # ══════════════════════════════════════════════════════════════════
        methods_by_full_id = self._build_method_definitions(classified_methods_raw)
        contracts_by_id = self._build_contract_classifications(contratos_clasificados_raw)
        method_sets = self._build_method_sets(method_sets_raw)
        sectors = self._build_sector_definitions()

        logger.debug(
            f"  Objects built: {len(methods_by_full_id)} methods, "
            f"{len(contracts_by_id)} contracts, {len(method_sets)} method sets"
        )

        # ══════════════════════════════════════════════════════════════════
        # PASO 5: Construir índices secundarios
        # ══════════════════════════════════════════════════════════════════
        methods_by_level = self._index_methods_by_level(methods_by_full_id)
        methods_by_class = self._index_methods_by_class(methods_by_full_id)
        contracts_by_type = self._index_contracts_by_type(contracts_by_id)
        contracts_by_contract_id = self._index_contracts_by_contract_id(contracts_by_id)

        logger.debug("  Secondary indices built")

        # ══════════════════════════════════════════════════════════════════
        # PASO 6: Validación cruzada
        # ══════════════════════════════════════════════════════════════════
        self._validate_cross_references(methods_by_full_id, method_sets)

        logger.debug("  Cross-references validated")

        # ══════════════════════════════════════════════════════════════════
        # PASO 7: Calcular estadísticas y construir registro
        # ══════════════════════════════════════════════════════════════════
        level_counts = {level: len(methods) for level, methods in methods_by_level.items()}

        registry = InputRegistry(
            classified_methods_hash=cm_hash,
            contratos_clasificados_hash=cc_hash,
            method_sets_hash=ms_hash,
            methods_by_full_id=methods_by_full_id,
            methods_by_level=methods_by_level,
            methods_by_class=methods_by_class,
            contracts_by_id=contracts_by_id,
            contracts_by_type=contracts_by_type,
            contracts_by_contract_id=contracts_by_contract_id,
            method_sets_by_question=method_sets,
            sectors=sectors,
            total_methods=len(methods_by_full_id),
            total_contracts=len(contracts_by_id),
            total_sectors=len(sectors),
            level_counts=level_counts,
            load_timestamp=datetime.now(timezone.utc).isoformat(),
            loader_version=LOADER_VERSION,
        )

        logger.info(
            f"InputRegistry built:  {registry.total_methods} methods, "
            f"{registry.total_contracts} contracts, {registry.total_sectors} sectors"
        )

        return registry

    # ══════════════════════════════════════════════════════════════════════════
    # MÉTODOS PRIVADOS - CARGA Y HASH
    # ══════════════════════════════════════════════════════════════════════════

    def _load_json(self, filename: str) -> dict[str, Any]:
        """
        Carga JSON preservando orden de claves.

        Args:
            filename: Nombre del archivo a cargar

        Returns:
            Diccionario con contenido del JSON

        Raises:
            FileNotFoundError: Si el archivo no existe
            json.JSONDecodeError: Si el JSON está malformado
        """
        path = self.assets_path / filename

        if not path.exists():
            raise FileNotFoundError(
                f"HARD FAILURE:  Required file not found: {path}\n"
                f"Expected location: {path.absolute()}"
            )

        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"HARD FAILURE: Invalid JSON in {filename}: {e. msg}",
                e. doc,
                e.pos,
            ) from e

    def _compute_hash(self, data: dict[str, Any]) -> str:
        """
        Computa hash SHA256 truncado de datos para trazabilidad.

        Args:
            data: Diccionario a hashear

        Returns:
            String de 16 caracteres hex
        """
        serialized = json.dumps(data, sort_keys=True, ensure_ascii=False)
        full_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        return full_hash[:16]

    # ══════════════════════════════════════════════════════════════════════════
    # MÉTODOS PRIVADOS - VALIDACIÓN DE ESTRUCTURA
    # ══════════════════════════════════════════════════════════════════════════

    def _validate_classified_methods_structure(self, data: dict[str, Any]) -> None:
        """
        Valida estructura de classified_methods.json.

        ESTRUCTURA ESPERADA:
        {
            "metadata": {... },
            "statistics": {...},
            "methods_by_level": {
                "N0-INFRA": [...],
                "N1-EMP": [...],
                "N2-INF": [...],
                "N3-AUD": [...],
                "N4-META": [...]
            }
        }
        """
        required_keys = {"metadata", "statistics", "methods_by_level"}
        missing = required_keys - set(data. keys())
        if missing: 
            raise ValueError(
                f"HARD FAILURE:  classified_methods.json missing required keys: {missing}\n"
                f"Present keys: {set(data.keys())}"
            )

        actual_levels = set(data["methods_by_level"].keys())
        missing_levels = VALID_EPISTEMOLOGICAL_LEVELS - actual_levels
        if missing_levels: 
            raise ValueError(
                f"HARD FAILURE: classified_methods.json missing epistemological levels: {missing_levels}\n"
                f"Present levels: {actual_levels}"
            )

        # Validar que hay métodos
        total_methods = sum(len(methods) for methods in data["methods_by_level"].values())
        if total_methods == 0:
            raise ValueError(
                "HARD FAILURE: classified_methods.json contains no methods"
            )

        logger.debug(f"    classified_methods.json: {total_methods} methods across {len(actual_levels)} levels")

    def _validate_contratos_clasificados_structure(self, data:  dict[str, Any]) -> None:
        """
        Valida estructura de contratos_clasificados.json.

        ESTRUCTURA ESPERADA:
        {
            "metadata": {...},
            "taxonomias_aplicadas": {... },
            "contratos":  {
                "DIM01_INSUMOS": {"D1_Q1": {... }, ...},
                "DIM02_ACTIVIDADES": {"D2_Q1": {...}, ...},
                ... 
            }
        }
        """
        if "contratos" not in data: 
            raise ValueError(
                "HARD FAILURE:  contratos_clasificados.json missing 'contratos' key"
            )

        # Contar contratos totales
        total = 0
        for dim_key, dim_contracts in data["contratos"].items():
            if not isinstance(dim_contracts, dict):
                raise ValueError(
                    f"HARD FAILURE: contratos_clasificados.json['{dim_key}'] "
                    f"is not a dict:  {type(dim_contracts)}"
                )
            total += len(dim_contracts)

        if total != EXPECTED_BASE_CONTRACTS:
            raise ValueError(
                f"HARD FAILURE: Expected {EXPECTED_BASE_CONTRACTS} base contracts, "
                f"found {total} in contratos_clasificados.json"
            )

        logger.debug(f"    contratos_clasificados.json: {total} contracts")

    def _validate_method_sets_structure(self, data:  dict[str, Any]) -> None:
        """
        Valida estructura de method_sets_by_question.json.

        ESTRUCTURA ESPERADA:
        {
            "metadata": {...},
            "method_sets": {
                "D1_Q1": {
                    "question_id": "D1_Q1",
                    "contract_type": {... },
                    "phase_a_N1": [... ],
                    "phase_b_N2": [...],
                    "phase_c_N3": [... ],
                    "efficiency_score": float,
                    "mathematical_evidence": {... },
                    "doctoral_justification": str
                },
                ... 
            }
        }
        """
        if "method_sets" not in data:
            raise ValueError(
                "HARD FAILURE: method_sets_by_question.json missing 'method_sets' key"
            )

        method_sets = data["method_sets"]

        if len(method_sets) != EXPECTED_BASE_CONTRACTS:
            raise ValueError(
                f"HARD FAILURE: Expected {EXPECTED_BASE_CONTRACTS} method sets, "
                f"found {len(method_sets)} in method_sets_by_question. json"
            )

        # Validar que cada set tenga las tres fases y campos requeridos
        required_fields = {
            "question_id",
            "contract_type",
            "phase_a_N1",
            "phase_b_N2",
            "phase_c_N3",
            "efficiency_score",
            "mathematical_evidence",
            "doctoral_justification",
        }

        for q_id, q_set in method_sets.items():
            missing = required_fields - set(q_set.keys())
            if missing:
                raise ValueError(
                    f"HARD FAILURE:  method_sets_by_question. json['{q_id}'] "
                    f"missing required fields: {missing}"
                )

            # Validar que las fases son listas
            for phase in ["phase_a_N1", "phase_b_N2", "phase_c_N3"]: 
                if not isinstance(q_set[phase], list):
                    raise ValueError(
                        f"HARD FAILURE: method_sets_by_question.json['{q_id}']['{phase}'] "
                        f"is not a list: {type(q_set[phase])}"
                    )

        logger.debug(f"    method_sets_by_question.json: {len(method_sets)} method sets")

    # ══════════════════════════════════════════════════════════════════════════
    # MÉTODOS PRIVADOS - CONSTRUCCIÓN DE OBJETOS
    # ══════════════════════════════════════════════════════════════════════════

    def _build_method_definitions(
        self,
        data: dict[str, Any],
    ) -> dict[str, MethodDefinition]:
        """
        Construye diccionario de definiciones de métodos.

        Args:
            data: Datos crudos de classified_methods.json

        Returns:
            Diccionario {full_id: MethodDefinition}
        """
        result:  dict[str, MethodDefinition] = {}

        for level, methods in data["methods_by_level"].items():
            for m in methods:
                try:
                    method_def = MethodDefinition(
                        class_name=m["class_name"],
                        method_name=m["method_name"],
                        mother_file=m["mother_file"],
                        provides=m["provides"],
                        level=m["level"],
                        level_name=m["level_name"],
                        epistemology=m["epistemology"],
                        output_type=m["output_type"],
                        fusion_behavior=m["fusion_behavior"],
                        fusion_symbol=m["fusion_symbol"],
                        classification_rationale=m["classification_rationale"],
                        confidence_score=float(m["confidence_score"]),
                        contract_affinities=dict(m["contract_affinities"]),
                        parameters=tuple(m["parameters"]),
                        return_type=m["return_type"],
                        is_private=bool(m["is_private"]),
                    )

                    # Verificar duplicados
                    if method_def.full_id in result:
                        raise ValueError(
                            f"HARD FAILURE:  Duplicate method full_id: {method_def. full_id}"
                        )

                    result[method_def.full_id] = method_def

                except KeyError as e:
                    raise ValueError(
                        f"HARD FAILURE: Method in level '{level}' missing field: {e}\n"
                        f"Method data: {m}"
                    ) from e

        return result

    def _build_contract_classifications(
        self,
        data:  dict[str, Any],
    ) -> dict[str, ContractClassification]:
        """
        Construye diccionario de clasificaciones de contratos.

        Args:
            data: Datos crudos de contratos_clasificados.json

        Returns:
            Diccionario {dimension_key: ContractClassification}
        """
        result: dict[str, ContractClassification] = {}

        for dim_key, dim_contracts in data["contratos"].items():
            for q_key, q_data in dim_contracts.items():
                try:
                    contract = ContractClassification(
                        contract_id=q_data["contract_id"],
                        dimension_key=q_key,
                        pregunta=q_data["pregunta"],
                        tipo_contrato=dict(q_data["tipo_contrato"]),
                        niveles_epistemologicos_requeridos=dict(
                            q_data["niveles_epistemologicos_requeridos"]
                        ),
                        estrategias_fusion=dict(q_data["estrategias_fusion"]),
                        roles_argumentativos=tuple(q_data["roles_argumentativos"]),
                        clases_dominantes=tuple(q_data["clases_dominantes"]),
                    )

                    # Validar tipo de contrato
                    if contract.type_code not in VALID_CONTRACT_TYPES:
                        raise ValueError(
                            f"HARD FAILURE: Contract {q_key} has invalid type:  {contract.type_code}\n"
                            f"Valid types: {VALID_CONTRACT_TYPES}"
                        )

                    result[q_key] = contract

                except KeyError as e:
                    raise ValueError(
                        f"HARD FAILURE: Contract '{q_key}' in '{dim_key}' missing field:  {e}\n"
                        f"Contract data: {q_data}"
                    ) from e

        return result

    def _build_method_sets(
        self,
        data: dict[str, Any],
    ) -> dict[str, QuestionMethodSet]:
        """
        Construye diccionario de asignaciones de métodos por pregunta.

        Args:
            data: Datos crudos de method_sets_by_question.json

        Returns:
            Diccionario {question_id: QuestionMethodSet}
        """
        result: dict[str, QuestionMethodSet] = {}

        for q_id, q_set in data["method_sets"].items():
            try:
                # Convertir listas de métodos a tuplas de MethodAssignment
                phase_a = tuple(
                    self._dict_to_method_assignment(m)
                    for m in q_set["phase_a_N1"]
                )
                phase_b = tuple(
                    self._dict_to_method_assignment(m)
                    for m in q_set["phase_b_N2"]
                )
                phase_c = tuple(
                    self._dict_to_method_assignment(m)
                    for m in q_set["phase_c_N3"]
                )

                method_set = QuestionMethodSet(
                    question_id=q_id,
                    contract_type=dict(q_set["contract_type"]),
                    phase_a_N1=phase_a,
                    phase_b_N2=phase_b,
                    phase_c_N3=phase_c,
                    efficiency_score=float(q_set["efficiency_score"]),
                    mathematical_evidence=dict(q_set["mathematical_evidence"]),
                    doctoral_justification=str(q_set["doctoral_justification"]),
                )

                result[q_id] = method_set

            except (KeyError, TypeError) as e:
                raise ValueError(
                    f"HARD FAILURE: Error building QuestionMethodSet for '{q_id}': {e}"
                ) from e

        return result

    def _dict_to_method_assignment(self, m: dict[str, Any]) -> MethodAssignment:
        """
        Convierte diccionario a MethodAssignment.

        Args:
            m: Diccionario con datos del método

        Returns:
            MethodAssignment inmutable
        """
        return MethodAssignment(
            class_name=m["class_name"],
            method_name=m["method_name"],
            mother_file=m["mother_file"],
            provides=m["provides"],
            level=m["level"],
            level_name=m["level_name"],
            epistemology=m["epistemology"],
            output_type=m["output_type"],
            fusion_behavior=m["fusion_behavior"],
            fusion_symbol=m["fusion_symbol"],
            classification_rationale=m["classification_rationale"],
            confidence_score=float(m["confidence_score"]),
            contract_affinities=dict(m["contract_affinities"]),
            parameters=tuple(m["parameters"]),
            return_type=m["return_type"],
            is_private=bool(m["is_private"]),
        )

    def _build_sector_definitions(self) -> dict[str, SectorDefinition]:
        """
        Construye diccionario de definiciones de sectores.

        Returns:
            Diccionario {sector_id: SectorDefinition}
        """
        result: dict[str, SectorDefinition] = {}

        for sector_id, sector_data in SECTOR_DEFINITIONS.items():
            result[sector_id] = SectorDefinition(
                sector_id=sector_id,
                canonical_name=sector_data["canonical_name"],
            )

        return result

    # ══════════════════════════════════════════════════════════════════════════
    # MÉTODOS PRIVADOS - CONSTRUCCIÓN DE ÍNDICES
    # ══════════════════════════════════════════════════════════════════════════

    def _index_methods_by_level(
        self,
        methods: dict[str, MethodDefinition],
    ) -> dict[str, tuple[MethodDefinition, ...]]:
        """
        Construye índice de métodos por nivel epistémico.

        Args:
            methods: Diccionario de métodos por full_id

        Returns:
            Diccionario {level:  tuple[MethodDefinition, ...]}
        """
        index: dict[str, list[MethodDefinition]] = defaultdict(list)

        for method in methods.values():
            index[method.level].append(method)

        # Convertir a tuplas inmutables
        return {k: tuple(v) for k, v in index.items()}

    def _index_methods_by_class(
        self,
        methods: dict[str, MethodDefinition],
    ) -> dict[str, tuple[MethodDefinition, ...]]:
        """
        Construye índice de métodos por nombre de clase.

        Args:
            methods: Diccionario de métodos por full_id

        Returns:
            Diccionario {class_name: tuple[MethodDefinition, ...]}
        """
        index: dict[str, list[MethodDefinition]] = defaultdict(list)

        for method in methods.values():
            index[method.class_name].append(method)

        return {k: tuple(v) for k, v in index.items()}

    def _index_contracts_by_type(
        self,
        contracts: dict[str, ContractClassification],
    ) -> dict[str, tuple[ContractClassification, ...]]:
        """
        Construye índice de contratos por tipo (TYPE_A, TYPE_B, etc.).

        Args:
            contracts: Diccionario de contratos por dimension_key

        Returns:
            Diccionario {type_code: tuple[ContractClassification, ...]}
        """
        index: dict[str, list[ContractClassification]] = defaultdict(list)

        for contract in contracts.values():
            index[contract.type_code].append(contract)

        return {k: tuple(v) for k, v in index.items()}

    def _index_contracts_by_contract_id(
        self,
        contracts: dict[str, ContractClassification],
    ) -> dict[str, ContractClassification]:
        """
        Construye índice de contratos por contract_id (Q001, Q002, etc.).

        Args:
            contracts: Diccionario de contratos por dimension_key

        Returns:
            Diccionario {contract_id:  ContractClassification}
        """
        return {contract.contract_id: contract for contract in contracts.values()}

    # ══════════════════════════════════════════════════════════════════════════
    # MÉTODOS PRIVADOS - VALIDACIÓN CRUZADA
    # ══════════════════════════════════════════════════════════════════════════

    def _validate_cross_references(
        self,
        methods: dict[str, MethodDefinition],
        method_sets: dict[str, QuestionMethodSet],
    ) -> None:
        """
        Valida referencias cruzadas entre archivos.

        VALIDACIONES:
        1. Todos los métodos en method_sets tienen niveles válidos para contratos
        2. Coherencia nivel-fase (E-001)

        Args:
            methods:  Diccionario de métodos del dispensario
            method_sets: Diccionario de asignaciones por pregunta

        Raises: 
            ValueError: Si hay inconsistencias
        """
        # Validar niveles válidos para contratos
        for q_id, q_set in method_sets.items():
            for method in q_set.all_methods_ordered: 
                if method.level not in VALID_CONTRACT_LEVELS:
                    raise ValueError(
                        f"HARD FAILURE: {q_id} has method {method.full_id} "
                        f"with level '{method.level}' which is not valid for contracts.\n"
                        f"Valid contract levels: {VALID_CONTRACT_LEVELS}"
                    )

        # Validar coherencia nivel-fase (E-001)
        self._validate_phase_level_coherence(method_sets)

    def _validate_phase_level_coherence(
        self,
        method_sets: dict[str, QuestionMethodSet],
    ) -> None:
        """
        Valida que los métodos asignados a cada fase tengan el nivel correcto.

        REGLAS ESTRICTAS:
        - phase_a_N1 → SOLO métodos con level que empiece con "N1"
        - phase_b_N2 → SOLO métodos con level que empiece con "N2"
        - phase_c_N3 → SOLO métodos con level que empiece con "N3"

        Esta es la validación principal para prevenir el error E-001.

        Args:
            method_sets: Diccionario de asignaciones por pregunta

        Raises:
            ValueError: Si cualquier método viola la regla de coherencia
        """
        all_violations:  list[str] = []

        for q_id, q_set in method_sets.items():
            violations:  list[str] = []

            # Validar phase_a_N1
            for method in q_set.phase_a_N1:
                if not method.level.startswith("N1"):
                    violations.append(
                        f"    phase_a_N1: {method.full_id} has level '{method.level}' (expected N1-*)"
                    )

            # Validar phase_b_N2
            for method in q_set.phase_b_N2:
                if not method.level. startswith("N2"):
                    violations.append(
                        f"    phase_b_N2: {method.full_id} has level '{method.level}' (expected N2-*)"
                    )

            # Validar phase_c_N3
            for method in q_set.phase_c_N3:
                if not method.level. startswith("N3"):
                    violations.append(
                        f"    phase_c_N3: {method.full_id} has level '{method.level}' (expected N3-*)"
                    )

            if violations:
                all_violations.append(f"  Question {q_id}:")
                all_violations.extend(violations)

        if all_violations:
            error_report = "\n".join(all_violations)
            raise ValueError(
                f"INPUT VALIDATION FAILURE (E-001): Phase-Level Coherence Violation\n"
                f"\n"
                f"The following methods are assigned to phases that don't match their level:\n"
                f"\n"
                f"{error_report}\n"
                f"\n"
                f"CORRECTIVE ACTION REQUIRED:\n"
                f"  1. Open method_sets_by_question.json\n"
                f"  2. For each violation, either:\n"
                f"     a) Move the method to the correct phase array, OR\n"
                f"     b) Correct the method's level in classified_methods.json\n"
                f"  3. Re-run the generator"
            )

        logger.debug(f"    Phase-level coherence validated for {len(method_sets)} method sets")
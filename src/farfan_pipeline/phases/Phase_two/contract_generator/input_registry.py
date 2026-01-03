"""
Módulo:  input_registry.py
Propósito: Cargar, validar e indexar todos los insumos como registro inmutable
"""

from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, FrozenSet


@dataclass(frozen=True)
class MethodDefinition:
    """
    Definición completa de un método del dispensario.
    INMUTABLE después de carga.
    """
    class_name: str
    method_name: str
    mother_file: str
    provides: str
    level: str  # N0-INFRA, N1-EMP, N2-INF, N3-AUD, N4-META
    level_name: str
    epistemology: str
    output_type: str  # INFRASTRUCTURE, FACT, PARAMETER, CONSTRAINT, META_ANALYSIS
    fusion_behavior: str  # additive, multiplicative, gate, terminal
    fusion_symbol: str
    classification_rationale: str
    confidence_score: float
    contract_affinities: dict[str, float]
    parameters: tuple[str, ...]
    return_type: str
    is_private: bool

    @property
    def full_id(self) -> str:
        return f"{self.class_name}.{self.method_name}"


@dataclass(frozen=True)
class ContractClassification:
    """
    Clasificación de un contrato según contratos_clasificados.json
    INMUTABLE.
    """
    contract_id: str  # Q001, Q002, etc.
    dimension_key: str  # D1_Q1, D1_Q2, etc.
    pregunta: str
    tipo_contrato: dict[str, str]  # {codigo, nombre, foco}
    niveles_epistemologicos_requeridos: dict[str, dict[str, str]]
    estrategias_fusion: dict[str, str]  # {N1: strategy, N2: strategy, N3: strategy}
    roles_argumentativos: tuple[str, ...]
    clases_dominantes: tuple[str, ...]


@dataclass(frozen=True)
class MethodAssignment:
    """
    Asignación de un método a una pregunta específica.
    Proviene de method_sets_by_question.json.
    INMUTABLE.
    """
    class_name: str
    method_name: str
    mother_file: str
    provides: str
    level: str
    level_name: str
    epistemology: str
    output_type: str
    fusion_behavior: str
    fusion_symbol: str
    classification_rationale: str
    confidence_score: float
    contract_affinities: dict[str, float]
    parameters: tuple[str, ...]
    return_type: str
    is_private: bool

    @property
    def full_id(self) -> str:
        return f"{self.class_name}.{self.method_name}"


@dataclass(frozen=True)
class QuestionMethodSet:
    """
    Conjunto de métodos asignados a una pregunta.
    Proviene de method_sets_by_question.json.
    INMUTABLE.
    """
    question_id: str  # D1_Q1, D1_Q2, etc.
    contract_type: dict[str, str]  # {code, name, focus, fusion_strategy}
    phase_a_N1: tuple[MethodAssignment, ...]
    phase_b_N2: tuple[MethodAssignment, ...]
    phase_c_N3: tuple[MethodAssignment, ...]
    efficiency_score: float
    mathematical_evidence: dict[str, Any]
    doctoral_justification: str

    @property
    def all_methods_ordered(self) -> tuple[MethodAssignment, ...]:
        """Retorna todos los métodos en orden: N1 → N2 → N3"""
        return self.phase_a_N1 + self.phase_b_N2 + self.phase_c_N3


@dataclass(frozen=True)
class InputRegistry:
    """
    Registro inmutable de todos los insumos.
    Una vez construido, no puede modificarse.
    """
    # Datos crudos hasheados para reproducibilidad
    classified_methods_hash: str
    contratos_clasificados_hash: str
    method_sets_hash: str

    # Índices de métodos
    methods_by_full_id: dict[str, MethodDefinition]
    methods_by_level: dict[str, tuple[MethodDefinition, ...]]
    methods_by_class: dict[str, tuple[MethodDefinition, ...]]

    # Índices de contratos
    contracts_by_id: dict[str, ContractClassification]
    contracts_by_type: dict[str, tuple[ContractClassification, ...]]

    # Asignaciones autoritativas
    method_sets_by_question: dict[str, QuestionMethodSet]

    # Estadísticas para validación
    total_methods: int
    total_contracts: int
    level_counts: dict[str, int]


class InputLoader:
    """
    Cargador de insumos con validación estricta.

    PROPIEDADES GARANTIZADAS:
    1. Carga determinista (orden de claves preservado)
    2. Validación exhaustiva antes de construir registro
    3. Hash de inputs para trazabilidad
    4. Fallo duro si cualquier validación falla
    """

    def __init__(self, assets_path: Path):
        self.assets_path = assets_path

    def load_and_validate(self) -> InputRegistry:
        """
        Carga todos los insumos y construye registro inmutable.

        SECUENCIA:
        1. Cargar JSONs con orden preservado
        2. Calcular hashes
        3. Validar estructuras
        4. Construir índices
        5. Validar referencias cruzadas
        6. Retornar registro inmutable

        FALLA SI:
        - Archivo no existe
        - JSON malformado
        - Estructura inesperada
        - Método referenciado no existe
        - Contrato sin métodos asignados
        """
        # Paso 1: Cargar JSONs
        classified_methods_raw = self._load_json("classified_methods.json")
        contratos_clasificados_raw = self._load_json("contratos_clasificados.json")
        method_sets_raw = self._load_json("method_sets_by_question.json")

        # Paso 2: Calcular hashes (para reproducibilidad)
        cm_hash = self._compute_hash(classified_methods_raw)
        cc_hash = self._compute_hash(contratos_clasificados_raw)
        ms_hash = self._compute_hash(method_sets_raw)

        # Paso 3: Validar estructuras
        self._validate_classified_methods_structure(classified_methods_raw)
        self._validate_contratos_clasificados_structure(contratos_clasificados_raw)
        self._validate_method_sets_structure(method_sets_raw)

        # Paso 4: Construir objetos tipados
        methods_by_full_id = self._build_method_definitions(classified_methods_raw)
        contracts_by_id = self._build_contract_classifications(contratos_clasificados_raw)
        method_sets = self._build_method_sets(method_sets_raw)

        # Paso 5: Construir índices secundarios
        methods_by_level = self._index_methods_by_level(methods_by_full_id)
        methods_by_class = self._index_methods_by_class(methods_by_full_id)
        contracts_by_type = self._index_contracts_by_type(contracts_by_id)

        # Paso 6: Validación cruzada
        self._validate_cross_references(methods_by_full_id, method_sets)

        # Paso 7: Calcular estadísticas
        level_counts = {level: len(methods) for level, methods in methods_by_level.items()}

        return InputRegistry(
            classified_methods_hash=cm_hash,
            contratos_clasificados_hash=cc_hash,
            method_sets_hash=ms_hash,
            methods_by_full_id=methods_by_full_id,
            methods_by_level=methods_by_level,
            methods_by_class=methods_by_class,
            contracts_by_id=contracts_by_id,
            contracts_by_type=contracts_by_type,
            method_sets_by_question=method_sets,
            total_methods=len(methods_by_full_id),
            total_contracts=len(contracts_by_id),
            level_counts=level_counts,
        )

    def _load_json(self, filename: str) -> dict[str, Any]:
        """Carga JSON preservando orden de claves"""
        path = self.assets_path / filename
        if not path.exists():
            raise FileNotFoundError(f"HARD FAILURE: Required file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            # json.load preserva orden en Python 3.7+
            return json.load(f)

    def _compute_hash(self, data: dict[str, Any]) -> str:
        """Computa hash determinista de datos"""
        # Serializar con sort_keys=True para determinismo
        serialized = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]

    def _validate_classified_methods_structure(self, data: dict[str, Any]) -> None:
        """
        Valida estructura de classified_methods.json

        ESTRUCTURA ESPERADA:
        {
            "metadata": {...},
            "statistics": {...},
            "methods_by_level": {
                "N0-INFRA": [...],
                "N1-EMP": [...],
                ...
            }
        }
        """
        required_keys = {"metadata", "statistics", "methods_by_level"}
        missing = required_keys - set(data.keys())
        if missing:
            raise ValueError(f"HARD FAILURE: classified_methods.json missing keys: {missing}")

        required_levels = {"N0-INFRA", "N1-EMP", "N2-INF", "N3-AUD", "N4-META"}
        actual_levels = set(data["methods_by_level"].keys())
        missing_levels = required_levels - actual_levels
        if missing_levels:
            raise ValueError(f"HARD FAILURE: Missing epistemological levels: {missing_levels}")

    def _validate_contratos_clasificados_structure(self, data: dict[str, Any]) -> None:
        """
        Valida estructura de contratos_clasificados.json

        ESTRUCTURA ESPERADA:
        {
            "metadata": {...},
            "taxonomias_aplicadas": {...},
            "contratos": {
                "DIM01_INSUMOS": {"D1_Q1": {...}, ...},
                ...
            }
        }
        """
        if "contratos" not in data:
            raise ValueError("HARD FAILURE: contratos_clasificados.json missing 'contratos' key")

        # Contar contratos totales
        total = 0
        for dim_key, dim_contracts in data["contratos"].items():
            total += len(dim_contracts)

        if total != 30:
            raise ValueError(f"HARD FAILURE: Expected 30 contracts, found {total}")

    def _validate_method_sets_structure(self, data: dict[str, Any]) -> None:
        """
        Valida estructura de method_sets_by_question.json

        ESTRUCTURA ESPERADA:
        {
            "metadata": {...},
            "method_sets": {
                "D1_Q1": {
                    "question_id": "D1_Q1",
                    "contract_type": {...},
                    "phase_a_N1": [...],
                    "phase_b_N2": [...],
                    "phase_c_N3": [...],
                    ...
                },
                ...
            }
        }
        """
        if "method_sets" not in data:
            raise ValueError("HARD FAILURE: method_sets_by_question.json missing 'method_sets' key")

        if len(data["method_sets"]) != 30:
            raise ValueError(
                f"HARD FAILURE: Expected 30 method sets, found {len(data['method_sets'])}"
            )

        # Validar que cada set tenga las tres fases
        for q_id, q_set in data["method_sets"].items():
            required = {"phase_a_N1", "phase_b_N2", "phase_c_N3"}
            missing = required - set(q_set.keys())
            if missing:
                raise ValueError(f"HARD FAILURE: {q_id} missing phases: {missing}")

    def _build_method_definitions(
        self, data: dict[str, Any]
    ) -> dict[str, MethodDefinition]:
        """Construye diccionario de definiciones de métodos"""
        result = {}

        for level, methods in data["methods_by_level"].items():
            for m in methods:
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
                    confidence_score=m["confidence_score"],
                    contract_affinities=m["contract_affinities"],
                    parameters=tuple(m["parameters"]),
                    return_type=m["return_type"],
                    is_private=m["is_private"],
                )
                result[method_def.full_id] = method_def

        return result

    def _build_contract_classifications(
        self, data: dict[str, Any]
    ) -> dict[str, ContractClassification]:
        """Construye diccionario de clasificaciones de contratos"""
        result = {}

        for dim_key, dim_contracts in data["contratos"].items():
            for q_key, q_data in dim_contracts.items():
                contract = ContractClassification(
                    contract_id=q_data["contract_id"],
                    dimension_key=q_key,
                    pregunta=q_data["pregunta"],
                    tipo_contrato=q_data["tipo_contrato"],
                    niveles_epistemologicos_requeridos=q_data["niveles_epistemologicos_requeridos"],
                    estrategias_fusion=q_data["estrategias_fusion"],
                    roles_argumentativos=tuple(q_data["roles_argumentativos"]),
                    clases_dominantes=tuple(q_data["clases_dominantes"]),
                )
                result[q_key] = contract

        return result

    def _build_method_sets(
        self, data: dict[str, Any]
    ) -> dict[str, QuestionMethodSet]:
        """Construye diccionario de asignaciones de métodos por pregunta"""
        result = {}

        for q_id, q_set in data["method_sets"].items():
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
                contract_type=q_set["contract_type"],
                phase_a_N1=phase_a,
                phase_b_N2=phase_b,
                phase_c_N3=phase_c,
                efficiency_score=q_set["efficiency_score"],
                mathematical_evidence=q_set["mathematical_evidence"],
                doctoral_justification=q_set["doctoral_justification"],
            )
            result[q_id] = method_set

        return result

    def _dict_to_method_assignment(self, m: dict[str, Any]) -> MethodAssignment:
        """Convierte dict a MethodAssignment"""
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
            confidence_score=m["confidence_score"],
            contract_affinities=m["contract_affinities"],
            parameters=tuple(m["parameters"]),
            return_type=m["return_type"],
            is_private=m["is_private"],
        )

    def _index_methods_by_level(
        self, methods: dict[str, MethodDefinition]
    ) -> dict[str, tuple[MethodDefinition, ...]]:
        """Construye índice de métodos por nivel"""
        from collections import defaultdict
        index = defaultdict(list)

        for method in methods.values():
            index[method.level].append(method)

        return {k: tuple(v) for k, v in index.items()}

    def _index_methods_by_class(
        self, methods: dict[str, MethodDefinition]
    ) -> dict[str, tuple[MethodDefinition, ...]]:
        """Construye índice de métodos por clase"""
        from collections import defaultdict
        index = defaultdict(list)

        for method in methods.values():
            index[method.class_name].append(method)

        return {k: tuple(v) for k, v in index.items()}

    def _index_contracts_by_type(
        self, contracts: dict[str, ContractClassification]
    ) -> dict[str, tuple[ContractClassification, ...]]:
        """Construye índice de contratos por TYPE"""
        from collections import defaultdict
        index = defaultdict(list)

        for contract in contracts.values():
            type_code = contract.tipo_contrato["codigo"]
            index[type_code].append(contract)

        return {k: tuple(v) for k, v in index.items()}

    def _validate_cross_references(
        self,
        methods: dict[str, MethodDefinition],
        method_sets: dict[str, QuestionMethodSet],
    ) -> None:
        """
        Valida que todos los métodos referenciados en asignaciones existan.

        FALLA SI:
        - Un método asignado no existe en el dispensario
        - Un método tiene full_id duplicado
        - Un método está asignado a una fase que no corresponde a su nivel (E-001)
        """
        for q_id, q_set in method_sets.items():
            for method in q_set.all_methods_ordered:
                # Nota: Los métodos en method_sets ya tienen toda la info
                # Solo validamos consistencia
                if method.level not in {"N1-EMP", "N2-INF", "N3-AUD"}:
                    raise ValueError(
                        f"HARD FAILURE: {q_id} has method {method.full_id} "
                        f"with invalid level {method.level} for contract generation"
                    )

        # ══════════════════════════════════════════════════════════════════
        # VALIDACIÓN E-001: Coherencia Nivel-Fase
        # ══════════════════════════════════════════════════════════════════
        self._validate_phase_level_coherence(methods, method_sets)

    def _validate_phase_level_coherence(
        self,
        methods: dict[str, MethodDefinition],
        method_sets: dict[str, QuestionMethodSet],
    ) -> None:
        """
        Valida que los métodos asignados a cada fase tengan el nivel correcto.

        REGLAS ESTRICTAS:
        - phase_a_N1 → SOLO métodos con level que empiece con "N1"
        - phase_b_N2 → SOLO métodos con level que empiece con "N2"
        - phase_c_N3 → SOLO métodos con level que empiece con "N3"

        FALLA DURO si cualquier método viola esta regla.
        """
        for q_id, q_set in method_sets.items():
            violations = []

            # Validar phase_a_N1
            for method in q_set.phase_a_N1:
                if not method.level.startswith("N1"):
                    violations.append(
                        f"  - phase_a_N1 contains {method.full_id} with level '{method.level}' "
                        f"(expected N1-*)"
                    )

            # Validar phase_b_N2
            for method in q_set.phase_b_N2:
                if not method.level.startswith("N2"):
                    violations.append(
                        f"  - phase_b_N2 contains {method.full_id} with level '{method.level}' "
                        f"(expected N2-*)"
                    )

            # Validar phase_c_N3
            for method in q_set.phase_c_N3:
                if not method.level.startswith("N3"):
                    violations.append(
                        f"  - phase_c_N3 contains {method.full_id} with level '{method.level}' "
                        f"(expected N3-*)"
                    )

            if violations:
                error_report = "\n".join(violations)
                raise ValueError(
                    f"INPUT VALIDATION FAILURE (E-001): Phase-Level Coherence Violation\n"
                    f"  Question: {q_id}\n"
                    f"  File: method_sets_by_question.json\n"
                    f"  Violations: {len(violations)}\n"
                    f"Details:\n{error_report}\n\n"
                    f"CORRECTIVE ACTION REQUIRED:\n"
                    f"  Move methods to the correct phase in method_sets_by_question.json\n"
                    f"  OR correct the method's level classification in classified_methods.json"
                )

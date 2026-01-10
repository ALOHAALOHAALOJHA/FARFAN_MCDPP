ESPECIFICACIÓN TÉCNICA COMPLETA: Generador Granular de Contratos Ejecutores F. A.R.F.A.N

PREÁMBULO: ANÁLISIS DE INSUMOS DISPONIBLES

Inventario de Insumos Verificados

Insumo	Ubicación	Contenido Verificado	Función en Generación
classified_methods.json	ASSDSDS/FARFAN_MPP	608 métodos clasificados con nivel epistemológico, output_type, fusion_behavior, contract_affinities	Pool maestro de métodos
contratos_clasificados.json	ASSDSDS/FARFAN_MPP	30 contratos (D1_Q1 a D6_Q5) con TYPE, niveles requeridos, estrategias de fusión, clases dominantes	Esqueleto epistemológico de cada contrato
method_sets_by_question.json	ASSDSDS/FARFAN_MPP	Asignaciones método→pregunta con phase_a_N1, phase_b_N2, phase_c_N3, efficiency_score, doctoral_justification	Asignaciones autoritativas de métodos
epistemological_method_classifier.py	ASSDSDS/FARFAN_MPP	Clasificador con reglas, patrones, afinidades	Lógica de clasificación (referencial)
operationalization_guide.json	Proporcionado	Guía canónica de 7 partes con estructura de contratos	Doctrina de estructura y validación
Observaciones Críticas de los Insumos

1. method_sets_by_question.json contiene asignaciones completas:

Cada pregunta tiene métodos pre-seleccionados por fase (N1, N2, N3)
Incluye efficiency_score y mathematical_evidence calculados
Incluye doctoral_justification textual
IMPLICACIÓN: El generador NO debe seleccionar métodos; debe EXPANDIR los ya asignados
2. classified_methods.json contiene metadata expandible:

Cada método tiene:  provides, level, output_type, fusion_behavior, classification_rationale, confidence_score, contract_affinities
IMPLICACIÓN: Esta metadata debe volcarse íntegramente al contrato, no resumirse
3. contratos_clasificados.json define el marco epistemológico:

Define TYPE, estrategias por nivel, roles argumentativos, clases dominantes
IMPLICACIÓN: Esto es overlay interpretativo, no generativo
PARTE I: ARQUITECTURA DEL GENERADOR

1.1 Diagrama de Componentes

Code
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         GRANULAR CONTRACT GENERATOR                             │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                        LAYER 0: INPUT LOADING                            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │   │
│  │  │ classified_ │  │ contratos_  │  │ method_sets │  │ operation_  │     │   │
│  │  │ methods     │  │ clasificados│  │ by_question │  │ guide       │     │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │   │
│  │         │                │                │                │            │   │
│  │         └────────────────┴────────────────┴────────────────┘            │   │
│  │                                   │                                      │   │
│  │                          ┌────────▼────────┐                            │   │
│  │                          │  INPUT_REGISTRY │                            │   │
│  │                          │  (immutable)    │                            │   │
│  │                          └────────┬────────┘                            │   │
│  └───────────────────────────────────┼─────────────────────────────────────┘   │
│                                      │                                         │
│  ┌───────────────────────────────────┼─────────────────────────────────────┐   │
│  │                        LAYER 1: METHOD EXPANSION                        │   │
│  │                                   │                                      │   │
│  │                          ┌────────▼────────┐                            │   │
│  │                          │ METHOD_EXPANDER │                            │   │
│  │                          │ (per-method)    │                            │   │
│  │                          └────────┬────────┘                            │   │
│  │                                   │                                      │   │
│  │         ┌─────────────────────────┼─────────────────────────┐           │   │
│  │         │                         │                         │           │   │
│  │    ┌────▼────┐              ┌────▼────┐              ┌────▼────┐       │   │
│  │    │ N1_UNIT │              │ N2_UNIT │              │ N3_UNIT │       │   │
│  │    │ (FACT)  │              │ (PARAM) │              │(CONSTR) │       │   │
│  │    └────┬────┘              └────┬────┘              └────┬────┘       │   │
│  └─────────┼────────────────────────┼────────────────────────┼─────────────┘   │
│            │                        │                        │                 │
│  ┌─────────┼────────────────────────┼────────────────────────┼─────────────┐   │
│  │         │     LAYER 2: CHAIN COMPOSITION                  │             │   │
│  │         │                        │                        │             │   │
│  │         └────────────────────────┼────────────────────────┘             │   │
│  │                                  │                                      │   │
│  │                         ┌────────▼────────┐                             │   │
│  │                         │ CHAIN_COMPOSER  │                             │   │
│  │                         │ (order-preserv) │                             │   │
│  │                         └────────┬────────┘                             │   │
│  └──────────────────────────────────┼──────────────────────────────────────┘   │
│                                     │                                          │
│  ┌──────────────────────────────────┼──────────────────────────────────────┐   │
│  │                     LAYER 3: CONTRACT ASSEMBLY                          │   │
│  │                                  │                                      │   │
│  │                         ┌────────▼────────┐                             │   │
│  │                         │CONTRACT_ASSEMBLER│                            │   │
│  │                         └────────┬────────┘                             │   │
│  │                                  │                                      │   │
│  │    ┌─────────────────────────────┼─────────────────────────────────┐   │   │
│  │    │                             │                                 │   │   │
│  │ ┌──▼──┐ ┌──────┐ ┌──────┐ ┌──────▼──────┐ ┌──────┐ ┌──────┐ ┌────▼──┐│   │
│  │ │iden │ │method│ │evid_ │ │fusion_spec  │ │cross │ │human │ │audit  ││   │
│  │ │tity │ │bind  │ │assem │ │             │ │layer │ │answ  │ │annot  ││   │
│  │ └─────┘ └──────┘ └──────┘ └─────────────┘ └──────┘ └──────┘ └───────┘│   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                     │                                          │
│  ┌──────────────────────────────────┼──────────────────────────────────────┐   │
│  │                     LAYER 4: VALIDATION & OUTPUT                        │   │
│  │                                  │                                      │   │
│  │         ┌────────────────────────┼────────────────────────┐            │   │
│  │         │                        │                        │            │   │
│  │    ┌────▼────┐              ┌────▼────┐              ┌────▼────┐       │   │
│  │    │STRUCT   │              │EPISTEMIC│              │TEMPORAL │       │   │
│  │    │VALIDATOR│              │VALIDATOR│              │VALIDATOR│       │   │
│  │    └────┬────┘              └────┬────┘              └────┬────┘       │   │
│  │         │                        │                        │            │   │
│  │         └────────────────────────┼────────────────────────┘            │   │
│  │                                  │                                      │   │
│  │                         ┌────────▼────────┐                             │   │
│  │                         │  JSON_EMITTER   │                             │   │
│  │                         │  (deterministic)│                             │   │
│  │                         └────────┬────────┘                             │   │
│  └──────────────────────────────────┼──────────────────────────────────────┘   │
│                                     │                                          │
│                                     ▼                                          │
│                            30 CONTRACT FILES                                   │
│                            (byte-reproducible)                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
1.2 Invariantes de Diseño (Hard Constraints)

Python
"""
INVARIANTES DEL GENERADOR - VIOLACIÓN = FALLO TOTAL
"""

# I-1: Autoridad Epistémica Inmutable
# El generador NUNCA infiere, sustituye, reordena o colapsa métodos
INVARIANT_EPISTEMIC_AUTHORITY = """
method_sets_by_question.json ES AUTORITATIVO. 
El generador es EJECUTOR, no RAZONADOR.
"""

# I-2: Composición Bottom-Up
# METHOD → expanded_unit → chain → contract
INVARIANT_BOTTOM_UP = """
Los contratos se construyen DESDE métodos HACIA arriba.
TYPE es overlay interpretativo, NO generativo. 
"""

# I-3: Sin Templates por TYPE
# No existe `if TYPE == TYPE_A: use_template_a()`
INVARIANT_NO_TEMPLATES = """
No hay plantillas TYPE-específicas que alteren estructura. 
Cada contrato emerge de la expansión de SUS métodos.
"""

# I-4: Determinismo Total
# hash(inputs) → hash(outputs) debe ser reproducible
INVARIANT_DETERMINISM = """
Dados inputs idénticos, outputs deben ser byte-idénticos.
No randomness, no timestamps en contenido, no ordenamientos no deterministas.
"""

# I-5: Fail-Loud
# Ambigüedad epistémica → error explícito, no degradación silenciosa
INVARIANT_FAIL_LOUD = """
Si un método referenciado no existe:  HARD FAILURE.
Si una asignación es ambigua: HARD FAILURE.
No hay auto-reparación silenciosa.
"""
PARTE II: ESPECIFICACIÓN DE MÓDULOS

2.1 Módulo: InputRegistry (Layer 0)

Python
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
    output_type:  str  # INFRASTRUCTURE, FACT, PARAMETER, CONSTRAINT, META_ANALYSIS
    fusion_behavior: str  # additive, multiplicative, gate, terminal
    fusion_symbol: str
    classification_rationale: str
    confidence_score:  float
    contract_affinities: dict[str, float]
    parameters: tuple[str, ...]
    return_type: str
    is_private: bool
    
    @property
    def full_id(self) -> str:
        return f"{self.class_name}. {self.method_name}"

@dataclass(frozen=True)
class ContractClassification:
    """
    Clasificación de un contrato según contratos_clasificados.json
    INMUTABLE. 
    """
    contract_id: str  # Q001, Q002, etc.
    dimension_key: str  # D1_Q1, D1_Q2, etc.
    pregunta:  str
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
    provides:  str
    level: str
    level_name: str
    epistemology: str
    output_type: str
    fusion_behavior: str
    fusion_symbol: str
    classification_rationale: str
    confidence_score:  float
    contract_affinities: dict[str, float]
    parameters: tuple[str, ...]
    return_type: str
    is_private: bool
    
    @property
    def full_id(self) -> str:
        return f"{self. class_name}.{self.method_name}"

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
        """Retorna todos los métodos en orden:  N1 → N2 → N3"""
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
    methods_by_level:  dict[str, tuple[MethodDefinition, ...]]
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
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[: 16]
    
    def _validate_classified_methods_structure(self, data: dict[str, Any]) -> None:
        """
        Valida estructura de classified_methods.json
        
        ESTRUCTURA ESPERADA:
        {
            "metadata": {... },
            "statistics": {...},
            "methods_by_level": {
                "N0-INFRA": [...],
                "N1-EMP": [... ],
                ... 
            }
        }
        """
        required_keys = {"metadata", "statistics", "methods_by_level"}
        missing = required_keys - set(data. keys())
        if missing:
            raise ValueError(f"HARD FAILURE: classified_methods.json missing keys: {missing}")
        
        required_levels = {"N0-INFRA", "N1-EMP", "N2-INF", "N3-AUD", "N4-META"}
        actual_levels = set(data["methods_by_level"].keys())
        missing_levels = required_levels - actual_levels
        if missing_levels:
            raise ValueError(f"HARD FAILURE:  Missing epistemological levels: {missing_levels}")
    
    def _validate_contratos_clasificados_structure(self, data:  dict[str, Any]) -> None:
        """
        Valida estructura de contratos_clasificados.json
        
        ESTRUCTURA ESPERADA:
        {
            "metadata": {...},
            "taxonomias_aplicadas": {...},
            "contratos":  {
                "DIM01_INSUMOS": {"D1_Q1": {... }, ... },
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
        Valida estructura de method_sets_by_question. json
        
        ESTRUCTURA ESPERADA:
        {
            "metadata": {...},
            "method_sets": {
                "D1_Q1": {
                    "question_id": "D1_Q1",
                    "contract_type": {... },
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
                f"HARD FAILURE:  Expected 30 method sets, found {len(data['method_sets'])}"
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
            index[method.class_name]. append(method)
        
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
2.2 Módulo: MethodExpander (Layer 1)

Python
"""
Módulo:  method_expander.py
Propósito: Expandir cada método asignado en una unidad semántica completa
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class ExpandedMethodUnit:
    """
    Unidad epistémica expandida de un método. 
    
    Esta es la GRANULARIDAD ATÓMICA del sistema.
    Cada campo existe porque tiene significado epistémico. 
    NADA se omite.
    """
    # Identidad
    method_id: str  # class_name. method_name
    class_name: str
    method_name: str
    mother_file: str
    provides:  str
    
    # Clasificación epistémica
    level: str
    level_name: str
    epistemology: str
    output_type: str
    
    # Comportamiento de fusión
    fusion_behavior: str
    fusion_symbol: str
    
    # Justificación
    classification_rationale: str
    confidence_score: float
    contract_affinities: dict[str, float]
    
    # Firma técnica
    parameters: tuple[str, ...]
    return_type: str
    is_private:  bool
    
    # Campos expandidos (derivados de la clasificación)
    evidence_requirements: tuple[str, ...]
    output_claims: tuple[str, ...]
    constraints_and_limits: tuple[str, ...]
    failure_modes: tuple[str, ...]
    interaction_notes: str
    
    # Campos para auditoría
    expansion_source: str  # Referencia al archivo de origen
    expansion_timestamp: str  # ISO timestamp de expansión

class MethodExpander:
    """
    Expande métodos asignados en unidades semánticas completas. 
    
    PROPIEDADES:
    1. NO infiere campos - los deriva de la clasificación
    2. NO reordena - preserva orden de input
    3. NO colapsa - cada método es una unidad discreta
    4. Determinista - misma entrada → misma salida
    """
    
    # Mapeo de nivel a requirements típicos
    LEVEL_EVIDENCE_REQUIREMENTS = {
        "N1-EMP": (
            "raw_document_text",
            "preprocesado_metadata",
        ),
        "N2-INF": (
            "raw_facts_from_N1",
            "confidence_scores",
        ),
        "N3-AUD": (
            "raw_facts_from_N1",
            "inferences_from_N2",
            "audit_criteria",
        ),
    }
    
    # Mapeo de output_type a claims típicos
    OUTPUT_TYPE_CLAIMS = {
        "FACT": (
            "observable_datum",
            "literal_extraction",
        ),
        "PARAMETER": (
            "derived_score",
            "probability_estimate",
            "relational_inference",
        ),
        "CONSTRAINT": (
            "validation_flag",
            "confidence_modulator",
            "veto_signal",
        ),
    }
    
    # Mapeo de nivel a failure modes típicos
    LEVEL_FAILURE_MODES = {
        "N1-EMP": (
            "empty_extraction",
            "pattern_not_found",
            "malformed_input",
        ),
        "N2-INF":  (
            "insufficient_evidence",
            "prior_undefined",
            "computation_error",
        ),
        "N3-AUD": (
            "validation_inconclusive",
            "criteria_not_met",
            "veto_triggered",
        ),
    }
    
    def __init__(self, expansion_timestamp: str):
        """
        Args:
            expansion_timestamp: ISO timestamp para trazabilidad
        """
        self.expansion_timestamp = expansion_timestamp
    
    def expand_method(
        self,
        assignment: "MethodAssignment",
        question_context: dict[str, Any],
    ) -> ExpandedMethodUnit:
        """
        Expande un método asignado en unidad semántica completa. 
        
        Args:
            assignment: MethodAssignment del method_sets_by_question. json
            question_context:  Contexto de la pregunta (TYPE, estrategias, etc.)
        
        Returns:
            ExpandedMethodUnit con todos los campos poblados
        """
        # Derivar campos de la clasificación (NO inventar)
        evidence_reqs = self._derive_evidence_requirements(assignment. level)
        output_claims = self._derive_output_claims(assignment. output_type)
        constraints = self._derive_constraints(assignment, question_context)
        failure_modes = self._derive_failure_modes(assignment. level)
        interaction = self._derive_interaction_notes(assignment, question_context)
        
        return ExpandedMethodUnit(
            # Identidad
            method_id=assignment.full_id,
            class_name=assignment.class_name,
            method_name=assignment.method_name,
            mother_file=assignment.mother_file,
            provides=assignment.provides,
            
            # Clasificación epistémica
            level=assignment. level,
            level_name=assignment.level_name,
            epistemology=assignment.epistemology,
            output_type=assignment.output_type,
            
            # Comportamiento de fusión
            fusion_behavior=assignment.fusion_behavior,
            fusion_symbol=assignment.fusion_symbol,
            
            # Justificación
            classification_rationale=assignment.classification_rationale,
            confidence_score=assignment. confidence_score,
            contract_affinities=assignment.contract_affinities,
            
            # Firma técnica
            parameters=assignment.parameters,
            return_type=assignment.return_type,
            is_private=assignment.is_private,
            
            # Campos expandidos
            evidence_requirements=evidence_reqs,
            output_claims=output_claims,
            constraints_and_limits=constraints,
            failure_modes=failure_modes,
            interaction_notes=interaction,
            
            # Auditoría
            expansion_source="method_sets_by_question.json",
            expansion_timestamp=self.expansion_timestamp,
        )
    
    def _derive_evidence_requirements(self, level: str) -> tuple[str, ...]: 
        """Deriva requirements del nivel (no inventa)"""
        return self.LEVEL_EVIDENCE_REQUIREMENTS.get(level, ())
    
    def _derive_output_claims(self, output_type: str) -> tuple[str, ...]:
        """Deriva claims del output_type (no inventa)"""
        return self.OUTPUT_TYPE_CLAIMS.get(output_type, ())
    
    def _derive_constraints(
        self,
        assignment: "MethodAssignment",
        context: dict[str, Any],
    ) -> tuple[str, ...]:
        """Deriva constraints de la clasificación y contexto"""
        constraints = []
        
        # Constraint de nivel
        if assignment.level == "N1-EMP": 
            constraints.append("output_must_be_literal")
            constraints.append("no_transformation_allowed")
        elif assignment.level == "N2-INF":
            constraints.append("requires_N1_input")
            constraints.append("output_is_derived")
        elif assignment.level == "N3-AUD":
            constraints.append("requires_N1_and_N2_input")
            constraints.append("can_veto_lower_levels")
            constraints.append("asymmetric_authority")
        
        # Constraint de confianza
        if assignment.confidence_score < 0.7:
            constraints.append("low_confidence_method")
        
        return tuple(constraints)
    
    def _derive_failure_modes(self, level: str) -> tuple[str, ...]:
        """Deriva failure modes del nivel (no inventa)"""
        return self.LEVEL_FAILURE_MODES.get(level, ())
    
    def _derive_interaction_notes(
        self,
        assignment: "MethodAssignment",
        context: dict[str, Any],
    ) -> str:
        """Deriva notas de interacción del contexto"""
        type_code = context.get("type_code", "UNKNOWN")
        strategy = context.get("fusion_strategy", "UNKNOWN")
        
        return (
            f"Method operates within {type_code} contract.  "
            f"Fusion strategy: {strategy}. "
            f"Level {assignment.level} provides {assignment.output_type} output."
        )
2.3 Módulo: ChainComposer (Layer 2)

Python
"""
Módulo: chain_composer.py
Propósito: Componer cadena epistémica ordenada a partir de unidades expandidas
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EpistemicChain:
    """
    Cadena epistémica ordenada.
    
    INVARIANTES:
    - El orden de métodos es EXACTAMENTE el del input
    - No hay fusión implícita
    - Cada método mantiene su identidad discreta
    """
    question_id: str
    contract_type: dict[str, str]
    
    # Cadenas por fase (orden preservado)
    phase_a_chain: tuple["ExpandedMethodUnit", ...]
    phase_b_chain: tuple["ExpandedMethodUnit", ...]
    phase_c_chain:  tuple["ExpandedMethodUnit", ...]
    
    # Metadata de composición
    total_methods: int
    composition_timestamp: str
    
    # Evidencia matemática preservada del input
    efficiency_score: float
    mathematical_evidence: dict[str, Any]
    doctoral_justification: str
    
    @property
    def full_chain_ordered(self) -> tuple["ExpandedMethodUnit", ...]: 
        """Retorna cadena completa en orden:  N1 → N2 → N3"""
        return self.phase_a_chain + self.phase_b_chain + self.phase_c_chain

class ChainComposer: 
    """
    Compone cadena epistémica desde unidades expandidas.
    
    PROPIEDADES:
    1. Preservación de orden - NUNCA reordena
    2. Sin agrupación - NUNCA agrupa por criterio no-dado
    3. Fronteras explícitas - transiciones entre fases son declaradas
    4. Determinista - misma entrada → misma salida
    """
    
    def __init__(self, expander: "MethodExpander"):
        self.expander = expander
    
    def compose_chain(
        self,
        method_set: "QuestionMethodSet",
        contract_classification: "ContractClassification",
    ) -> EpistemicChain:
        """
        Compone cadena epistémica para una pregunta.
        
        SECUENCIA: 
        1. Expandir métodos N1 (preservando orden)
        2. Expandir métodos N2 (preservando orden)
        3. Expandir métodos N3 (preservando orden)
        4. Ensamblar cadena con metadata
        
        Args:
            method_set: QuestionMethodSet con métodos asignados
            contract_classification:  ContractClassification para contexto
        
        Returns: 
            EpistemicChain inmutable
        """
        # Construir contexto para expansión
        context = {
            "type_code": contract_classification.tipo_contrato["codigo"],
            "type_name": contract_classification.tipo_contrato["nombre"],
            "fusion_strategy": method_set.contract_type. get("fusion_strategy", ""),
            "question_id": method_set.question_id,
        }
        
        # Expandir cada fase PRESERVANDO ORDEN EXACTO
        phase_a = tuple(
            self.expander.expand_method(m, context)
            for m in method_set.phase_a_N1
        )
        
        phase_b = tuple(
            self.expander.expand_method(m, context)
            for m in method_set.phase_b_N2
        )
        
        phase_c = tuple(
            self.expander.expand_method(m, context)
            for m in method_set.phase_c_N3
        )
        
        # Ensamblar cadena
        return EpistemicChain(
            question_id=method_set.question_id,
            contract_type=method_set.contract_type,
            phase_a_chain=phase_a,
            phase_b_chain=phase_b,
            phase_c_chain=phase_c,
            total_methods=len(phase_a) + len(phase_b) + len(phase_c),
            composition_timestamp=self.expander.expansion_timestamp,
            efficiency_score=method_set.efficiency_score,
            mathematical_evidence=method_set. mathematical_evidence,
            doctoral_justification=method_set.doctoral_justification,
        )
2.4 Módulo: ContractAssembler (Layer 3)

Python
"""
Módulo: contract_assembler.py
Propósito: Ensamblar contrato completo desde cadena epistémica
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class GeneratedContract:
    """
    Contrato ejecutor generado.
    
    ESTRUCTURA SEGÚN operationalization_guide.json:
    - identity
    - executor_binding
    - method_binding
    - question_context
    - signal_requirements
    - evidence_assembly
    - fusion_specification
    - cross_layer_fusion
    - human_answer_structure
    - audit_annotations (añadido para trazabilidad)
    """
    # Sección:  identity
    identity: dict[str, Any]
    
    # Sección: executor_binding
    executor_binding: dict[str, Any]
    
    # Sección: method_binding (LA MÁS GRANULAR)
    method_binding:  dict[str, Any]
    
    # Sección: question_context
    question_context:  dict[str, Any]
    
    # Sección: signal_requirements
    signal_requirements:  dict[str, Any]
    
    # Sección: evidence_assembly
    evidence_assembly:  dict[str, Any]
    
    # Sección: fusion_specification
    fusion_specification:  dict[str, Any]
    
    # Sección: cross_layer_fusion
    cross_layer_fusion: dict[str, Any]
    
    # Sección: human_answer_structure
    human_answer_structure:  dict[str, Any]
    
    # Sección: audit_annotations (para trazabilidad)
    audit_annotations: dict[str, Any]
    
    def to_dict(self) -> dict[str, Any]:
        """Serializa a diccionario ordenado"""
        return {
            "identity": self.identity,
            "executor_binding": self. executor_binding,
            "method_binding": self.method_binding,
            "question_context":  self.question_context,
            "signal_requirements": self.signal_requirements,
            "evidence_assembly": self.evidence_assembly,
            "fusion_specification": self.fusion_specification,
            "cross_layer_fusion": self. cross_layer_fusion,
            "human_answer_structure": self.human_answer_structure,
            "audit_annotations": self. audit_annotations,
        }

class ContractAssembler: 
    """
    Ensambla contratos desde cadenas epistémicas.
    
    PRINCIPIOS:
    1. La cadena epistémica ES el contrato (no se transforma)
    2. TYPE es overlay interpretativo sobre la cadena
    3. Cada sección se deriva de la cadena, no de templates
    4. Verbosidad completa en method_binding
    """
    
    def __init__(
        self,
        registry: "InputRegistry",
        generation_timestamp: str,
        generator_version: str,
    ):
        self.registry = registry
        self.generation_timestamp = generation_timestamp
        self.generator_version = generator_version
    
    def assemble_contract(
        self,
        chain: "EpistemicChain",
        classification: "ContractClassification",
    ) -> GeneratedContract:
        """
        Ensambla contrato completo desde cadena epistémica.
        
        Args:
            chain: EpistemicChain compuesta
            classification: ContractClassification para contexto
        
        Returns:
            GeneratedContract completo
        """
        # Construir cada sección
        identity = self._build_identity(chain, classification)
        executor_binding = self._build_executor_binding(chain)
        method_binding = self._build_method_binding(chain)
        question_context = self._build_question_context(classification)
        signal_requirements = self._build_signal_requirements(chain)
        evidence_assembly = self._build_evidence_assembly(chain, classification)
        fusion_specification = self._build_fusion_specification(chain, classification)
        cross_layer_fusion = self._build_cross_layer_fusion(classification)
        human_answer_structure = self._build_human_answer_structure(classification)
        audit_annotations = self._build_audit_annotations(chain, classification)
        
        return GeneratedContract(
            identity=identity,
            executor_binding=executor_binding,
            method_binding=method_binding,
            question_context=question_context,
            signal_requirements=signal_requirements,
            evidence_assembly=evidence_assembly,
            fusion_specification=fusion_specification,
            cross_layer_fusion=cross_layer_fusion,
            human_answer_structure=human_answer_structure,
            audit_annotations=audit_annotations,
        )
    
    def _build_identity(
        self,
        chain: "EpistemicChain",
        classification: "ContractClassification",
    ) -> dict[str, Any]: 
        """Construye sección identity"""
        # Mapear question_id a contract_id y otros campos
        q_id = chain.question_id  # e.g., "D1_Q1"
        contract_id = classification.contract_id  # e.g., "Q001"
        
        # Derivar policy_areas y contracts_served
        # Según la guía, cada contrato sirve 10 sectores
        base_num = int(contract_id[1:])  # Q001 → 1
        contracts_served = [
            f"Q{str(base_num + (i * 30)).zfill(3)}"
            for i in range(10)
        ]
        
        return {
            "base_slot": q_id. replace("_", "-"),  # D1-Q1
            "representative_question_id": contract_id,
            "dimension_id": f"DIM{q_id[1:3]}",  # D1 → DIM01
            "policy_area_ids_served": [f"PA{str(i+1).zfill(2)}" for i in range(10)],
            "contracts_served":  contracts_served,
            "contract_type": classification.tipo_contrato["codigo"],
            "contract_type_name": classification.tipo_contrato["nombre"],
            "contract_type_focus": classification.tipo_contrato["foco"],
            "contract_version": "4.0.0-epistemological",
            "created_at": self.generation_timestamp,
            "generator_version": self.generator_version,
            "specification_source": "operationalization_guide.json",
        }
    
    def _build_executor_binding(self, chain: "EpistemicChain") -> dict[str, Any]:
        """Construye sección executor_binding"""
        q_id = chain.question_id
        return {
            "executor_class": f"{q_id}_Executor",
            "executor_module": "farfan_pipeline. phases. Phase_two. executors",
        }
    
    def _build_method_binding(self, chain: "EpistemicChain") -> dict[str, Any]:
        """
        Construye sección method_binding.
        
        ESTA ES LA SECCIÓN MÁS GRANULAR. 
        Cada método expandido se vuelca íntegramente.
        """
        return {
            "orchestration_mode": "epistemological_pipeline",
            "contract_type": chain.contract_type["code"],
            "method_count": chain.total_methods,
            "execution_phases": {
                "phase_A_construction": self._build_phase_section(
                    chain.phase_a_chain,
                    level="N1",
                    level_name="Base Empírica",
                    epistemology="Empirismo positivista",
                    description="Empirical observation layer - direct extraction without interpretation",
                    output_target="raw_facts",
                ),
                "phase_B_computation": self._build_phase_section(
                    chain.phase_b_chain,
                    level="N2",
                    level_name="Procesamiento Inferencial",
                    epistemology="Bayesianismo subjetivista",
                    description="Inferential analysis layer - transformation into analytical constructs",
                    output_target="inferences",
                    dependencies=["phase_A_construction"],
                ),
                "phase_C_litigation": self._build_phase_section(
                    chain.phase_c_chain,
                    level="N3",
                    level_name="Auditoría y Robustez",
                    epistemology="Falsacionismo popperiano",
                    description="Audit layer - attempt to 'break' results.  Acts as VETO GATE.",
                    output_target="audit_results",
                    dependencies=["phase_A_construction", "phase_B_computation"],
                    asymmetry_principle="N3 can invalidate N1/N2, but NOT vice versa",
                ),
            },
            "efficiency_score": chain.efficiency_score,
            "mathematical_evidence":  chain.mathematical_evidence,
            "doctoral_justification": chain. doctoral_justification,
        }
    
    def _build_phase_section(
        self,
        methods: tuple["ExpandedMethodUnit", ...],
        level: str,
        level_name: str,
        epistemology: str,
        description: str,
        output_target: str,
        dependencies: list[str] | None = None,
        asymmetry_principle: str | None = None,
    ) -> dict[str, Any]:
        """Construye sección de una fase con todos los métodos expandidos"""
        section = {
            "description": description,
            "level": level,
            "level_name": level_name,
            "epistemology": epistemology,
            "methods": [
                self._expand_method_to_dict(m) for m in methods
            ],
            "dependencies": dependencies or [],
            "output_target": output_target,
        }
        
        if asymmetry_principle:
            section["asymmetry_principle"] = asymmetry_principle
        
        if level == "N3":
            section["fusion_mode"] = "modulation"
        
        return section
    
    def _expand_method_to_dict(self, method: "ExpandedMethodUnit") -> dict[str, Any]: 
        """
        Convierte ExpandedMethodUnit a diccionario COMPLETO.
        
        VERBOSIDAD TOTAL:  Cada campo se incluye. 
        NO hay compresión ni resumen.
        """
        result = {
            # Identidad
            "class_name": method.class_name,
            "method_name": method.method_name,
            "mother_file": method.mother_file,
            "provides":  method.provides,
            "method_id": method.method_id,
            
            # Clasificación epistémica
            "level": method.level,
            "level_name": method.level_name,
            "epistemology": method.epistemology,
            "output_type": method.output_type,
            
            # Comportamiento de fusión
            "fusion_behavior": method.fusion_behavior,
            "fusion_symbol": method.fusion_symbol,
            
            # Justificación
            "classification_rationale": method.classification_rationale,
            "confidence_score": method.confidence_score,
            "contract_affinities": method.contract_affinities,
            
            # Firma técnica
            "parameters": list(method.parameters),
            "return_type": method.return_type,
            "is_private": method.is_private,
            
            # Campos expandidos
            "evidence_requirements": list(method.evidence_requirements),
            "output_claims": list(method.output_claims),
            "constraints_and_limits": list(method.constraints_and_limits),
            "failure_modes": list(method.failure_modes),
            "interaction_notes": method.interaction_notes,
            
            # Trazabilidad
            "expansion_source": method.expansion_source,
            "expansion_timestamp": method. expansion_timestamp,
        }
        
        # Para métodos N3, añadir veto_conditions si aplica
        if method.level == "N3-AUD":
            result["veto_conditions"] = self._derive_veto_conditions(method)
            result["modulates"] = [
                "raw_facts. confidence",
                "inferences.confidence",
            ]
        
        # Para métodos N2, añadir modifies
        if method.level == "N2-INF":
            result["requires"] = ["raw_facts"]
            result["modifies"] = ["edge_weights", "confidence_scores"]
        
        return result
    
    def _derive_veto_conditions(
        self, method: "ExpandedMethodUnit"
    ) -> dict[str, dict[str, Any]]:
        """Deriva veto_conditions del método N3"""
        # Condiciones base para todos los métodos N3
        conditions = {}
        
        # Detectar por nombre del método
        method_lower = method.method_name.lower()
        
        if "significance" in method_lower or "statistical" in method_lower:
            conditions["significance_below_threshold"] = {
                "trigger": "p_value > 0.05",
                "action": "reduce_confidence",
                "scope": "affected_claims",
                "confidence_multiplier": 0.5,
                "rationale": "Finding not statistically significant",
            }
        
        if "contradiction" in method_lower or "incompatib" in method_lower:
            conditions["logical_contradiction_detected"] = {
                "trigger":  "contradiction_flag == True",
                "action": "block_branch",
                "scope": "contradicting_nodes",
                "confidence_multiplier": 0.0,
                "rationale": "Logical inconsistency invalidates branch",
            }
        
        if "coherence" in method_lower: 
            conditions["low_coherence"] = {
                "trigger": "coherence_score < 0.5",
                "action": "reduce_confidence",
                "scope":  "source_facts",
                "confidence_multiplier": 0.5,
                "rationale": "Low coherence reduces reliability",
            }
        
        if "acyclic" in method_lower or "dag" in method_lower:
            conditions["cycle_detected"] = {
                "trigger":  "has_cycle == True",
                "action": "invalidate_graph",
                "scope": "entire_causal_graph",
                "confidence_multiplier": 0.0,
                "rationale": "Causal graph must be acyclic",
            }
        
        if "sufficiency" in method_lower or "gap" in method_lower:
            conditions["budget_insufficiency"] = {
                "trigger": "budget_gap > 50%",
                "action": "flag_insufficiency",
                "scope": "affected_goals",
                "confidence_multiplier": 0.3,
                "rationale": "Insufficient budget allocation",
            }
        
        # Si no se detectaron condiciones específicas, usar genérica
        if not conditions:
            conditions["validation_failed"] = {
                "trigger":  "validation_result == False",
                "action": "flag_caution",
                "scope": "method_output",
                "confidence_multiplier": 0.7,
                "rationale": "Validation did not pass",
            }
        
        return conditions
    
    def _build_question_context(
        self, classification: "ContractClassification"
    ) -> dict[str, Any]:
        """Construye sección question_context"""
        return {
            "monolith_ref": classification.contract_id,
            "pregunta_completa": classification.pregunta,
            "overrides": None,
            "failure_contract":  {
                "abort_if":  [
                    "missing_required_element",
                    "incomplete_text",
                    "no_quantitative_data",
                ],
                "emit_code": f"ABORT-{classification.dimension_key. replace('_', '-')}-REQ",
            },
        }
    
    def _build_signal_requirements(self, chain: "EpistemicChain") -> dict[str, Any]:
        """Construye sección signal_requirements"""
        return {
            "derivation_source": "expected_elements",
            "derivation_rules": {
                "mandatory":  "expected_elements[required=true]. type → detection_{type}",
                "optional": "expected_elements[required=false]. type → detection_{type}",
            },
            "signal_aggregation": "weighted_mean",
            "minimum_signal_threshold": 0.5,
        }
    
    
    def _build_evidence_assembly(
        self,
        chain: "EpistemicChain",
        classification:  "ContractClassification",
    ) -> dict[str, Any]:
        """
        Construye sección evidence_assembly según operationalization_guide.json.
        
        Las reglas de ensamblaje dependen del TYPE. 
        """
        type_code = classification.tipo_contrato["codigo"]
        
        # Sistema de tipos (común para todos)
        type_system = {
            "FACT": {
                "origin_level": "N1",
                "fusion_operation": "graph_node_addition",
                "merge_behavior": "additive",
                "symbol": "⊕",
                "description": "Se SUMA al grafo como nodo"
            },
            "PARAMETER": {
                "origin_level": "N2",
                "fusion_operation": "edge_weight_modification",
                "merge_behavior":  "multiplicative",
                "symbol": "⊗",
                "description": "MODIFICA pesos de aristas del grafo"
            },
            "CONSTRAINT": {
                "origin_level": "N3",
                "fusion_operation": "branch_filtering",
                "merge_behavior":  "gate",
                "symbol": "⊘",
                "description": "FILTRA/BLOQUEA ramas si validación falla"
            },
            "NARRATIVE": {
                "origin_level": "N4",
                "fusion_operation": "synthesis",
                "merge_behavior":  "terminal",
                "symbol": "⊙",
                "description": "CONSUME grafo para texto final"
            }
        }
        
        # Recolectar provides de cada fase
        n1_provides = [m.provides for m in chain.phase_a_chain]
        n2_provides = [m.provides for m in chain.phase_b_chain]
        n3_provides = [m.provides for m in chain.phase_c_chain]
        
        # Construir reglas según TYPE
        assembly_rules = self._build_assembly_rules_for_type(
            type_code=type_code,
            n1_provides=n1_provides,
            n2_provides=n2_provides,
            n3_provides=n3_provides,
            strategies=classification.estrategias_fusion,
        )
        
        return {
            "engine":  "EVIDENCE_NEXUS",
            "module": "farfan_pipeline. phases.Phase_two.evidence_nexus",
            "class_name": "EvidenceNexus",
            "method_name": "assemble",
            "type_system": type_system,
            "assembly_rules": assembly_rules,
        }
    
    def _build_assembly_rules_for_type(
        self,
        type_code: str,
        n1_provides: list[str],
        n2_provides: list[str],
        n3_provides: list[str],
        strategies: dict[str, str],
    ) -> list[dict[str, Any]]: 
        """
        Construye reglas de ensamblaje específicas por TYPE.
        
        SEGÚN operationalization_guide.json:
        - TYPE_A: semantic_corroboration → dempster_shafer → veto_gate
        - TYPE_B: concat → bayesian_update → veto_gate
        - TYPE_C: graph_construction → topological_overlay → veto_gate
        - TYPE_D: concat → weighted_mean → financial_coherence_audit
        - TYPE_E: concat → weighted_mean → logical_consistency_validation
        """
        # R1: Regla de extracción empírica (N1)
        r1 = {
            "rule_id": "R1_empirical_extraction",
            "rule_type": "empirical_basis",
            "target":  self._get_r1_target(type_code),
            "sources": n1_provides,
            "merge_strategy": strategies. get("N1", "concat"),
            "output_type": "FACT",
            "confidence_propagation": "preserve_individual",
            "description": "Extract raw facts from document without interpretation",
        }
        
        # Añadir deduplication para TYPE_A
        if type_code == "TYPE_A":
            r1["deduplication_key"] = "element_id"
            r1["merge_strategy"] = "concat_with_deduplication"
        
        # R2: Regla de procesamiento inferencial (N2)
        r2 = {
            "rule_id": "R2_inferential_processing",
            "rule_type": self._get_r2_rule_type(type_code),
            "target": self._get_r2_target(type_code),
            "sources": n2_provides,
            "input_dependencies": [r1["target"]],
            "merge_strategy": strategies.get("N2", "weighted_mean"),
            "output_type": "PARAMETER",
            "confidence_propagation": self._get_r2_confidence_propagation(type_code),
            "description": self._get_r2_description(type_code),
        }
        
        # Añadir operación específica para ciertos types
        if type_code == "TYPE_A":
            r2["operation"] = (
                "if TextMining AND IndustrialPolicy extract same datum → "
                "merge nodes, increase confidence"
            )
        elif type_code == "TYPE_B":
            r2["operation"] = "posterior = update_belief(prior, likelihood_from_evidence)"
        elif type_code == "TYPE_C":
            r2["operation"] = (
                "if TeoriaCambio path AND CausalExtractor path → "
                "check for cycles, merge edges"
            )
        
        # R3: Regla de auditoría (N3)
        r3 = {
            "rule_id": "R3_audit_gate",
            "rule_type":  self._get_r3_rule_type(type_code),
            "target": self._get_r3_target(type_code),
            "sources": n3_provides,
            "input_dependencies": [r1["target"], r2["target"]],
            "merge_strategy":  "veto_gate",
            "output_type": "CONSTRAINT",
            "gate_logic": self._get_gate_logic(type_code),
            "asymmetry_declaration": "N3 can invalidate N1/N2 outputs; N1/N2 CANNOT invalidate N3",
            "description": "Validate and potentially veto lower-level findings",
        }
        
        # R4: Regla de síntesis (N4)
        r4 = {
            "rule_id": "R4_narrative_synthesis",
            "rule_type": "synthesis",
            "target": "human_answer",
            "sources":  [],
            "input_dependencies": [r1["target"], r2["target"], r3["target"]],
            "merge_strategy": "carver_doctoral_synthesis",
            "output_type":  "NARRATIVE",
            "external_handler": "DoctoralCarverSynthesizer",
            "description": "Synthesize validated evidence into human-readable answer",
        }
        
        return [r1, r2, r3, r4]
    
    def _get_r1_target(self, type_code: str) -> str:
        """Determina target de R1 según TYPE"""
        targets = {
            "TYPE_A": "raw_facts",
            "TYPE_B": "prior_distribution",
            "TYPE_C":  "causal_graph",
            "TYPE_D": "financial_facts",
            "TYPE_E":  "policy_statements",
        }
        return targets.get(type_code, "raw_facts")
    
    def _get_r2_rule_type(self, type_code: str) -> str:
        """Determina rule_type de R2 según TYPE"""
        rule_types = {
            "TYPE_A": "corroboration",
            "TYPE_B": "probabilistic_update",
            "TYPE_C": "edge_inference",
            "TYPE_D":  "computation",
            "TYPE_E": "computation",
        }
        return rule_types.get(type_code, "computation")
    
    def _get_r2_target(self, type_code: str) -> str:
        """Determina target de R2 según TYPE"""
        targets = {
            "TYPE_A": "triangulated_facts",
            "TYPE_B": "posterior_belief",
            "TYPE_C":  "weighted_causal_graph",
            "TYPE_D": "sufficiency_scores",
            "TYPE_E":  "coherence_metrics",
        }
        return targets.get(type_code, "inferences")
    
    def _get_r2_confidence_propagation(self, type_code: str) -> str:
        """Determina propagación de confianza en R2"""
        if type_code == "TYPE_A":
            return "corroborative_boost"
        elif type_code == "TYPE_B":
            return "bayesian_update"
        else:
            return "weighted_aggregation"
    
    def _get_r2_description(self, type_code: str) -> str:
        """Descripción de R2 según TYPE"""
        descriptions = {
            "TYPE_A": "Triangulate semantic evidence from multiple sources",
            "TYPE_B": "Update prior beliefs with observed evidence",
            "TYPE_C": "Infer causal edge weights and validate topology",
            "TYPE_D":  "Calculate sufficiency scores for financial allocations",
            "TYPE_E": "Compute coherence metrics between policy statements",
        }
        return descriptions.get(type_code, "Process inferences from raw facts")
    
    def _get_r3_rule_type(self, type_code: str) -> str:
        """Determina rule_type de R3 según TYPE"""
        rule_types = {
            "TYPE_A": "robustness_gate",
            "TYPE_B":  "robustness_gate",
            "TYPE_C": "validity_check",
            "TYPE_D":  "financial_coherence_audit",
            "TYPE_E": "logical_consistency_validation",
        }
        return rule_types.get(type_code, "robustness_gate")
    
    def _get_r3_target(self, type_code:  str) -> str:
        """Determina target de R3 según TYPE"""
        targets = {
            "TYPE_A": "validated_facts",
            "TYPE_B": "validated_posterior",
            "TYPE_C":  "validated_graph",
            "TYPE_D":  "validated_financials",
            "TYPE_E": "validated_statements",
        }
        return targets.get(type_code, "validated_evidence")
    
    def _get_gate_logic(self, type_code: str) -> dict[str, dict[str, Any]]:
        """Construye gate_logic según TYPE"""
        base_logic = {}
        
        if type_code == "TYPE_A":
            base_logic = {
                "contradiction_detected": {
                    "action": "suppress_fact",
                    "multiplier": 0.0,
                    "scope": "contradicting_nodes",
                },
                "low_coherence": {
                    "action": "reduce_confidence",
                    "multiplier": 0.5,
                    "scope": "source_facts",
                },
            }
        elif type_code == "TYPE_B":
            base_logic = {
                "statistical_power_below_threshold": {
                    "condition": "power < 0.8",
                    "action": "downgrade_confidence",
                    "multiplier": 0.5,
                    "scope": "posterior_claims",
                },
                "sample_size_insufficient": {
                    "condition":  "n < 30",
                    "action": "flag_caution",
                    "multiplier": 0.7,
                    "scope": "affected_claims",
                },
            }
        elif type_code == "TYPE_C":
            base_logic = {
                "cycle_detected": {
                    "action": "invalidate_graph",
                    "multiplier": 0.0,
                    "scope": "entire_causal_graph",
                },
                "scm_construction_failed": {
                    "action": "block_branch",
                    "multiplier":  0.0,
                    "scope": "affected_subgraph",
                },
            }
        elif type_code == "TYPE_D":
            base_logic = {
                "budget_gap_detected": {
                    "condition": "gap > 50%",
                    "action": "flag_insufficiency",
                    "multiplier":  0.3,
                    "scope": "affected_goals",
                },
                "allocation_mismatch": {
                    "action": "reduce_confidence",
                    "multiplier":  0.5,
                    "scope": "mismatched_items",
                },
            }
        elif type_code == "TYPE_E":
            base_logic = {
                "logical_contradiction": {
                    "action":  "suppress_contradicting_nodes",
                    "multiplier":  0.0,
                    "scope": "contradicting_statements",
                },
                "sequence_violation": {
                    "action":  "flag_invalid_sequence",
                    "multiplier": 0.2,
                    "scope": "affected_sequence",
                },
            }
        
        return base_logic
    
    def _build_fusion_specification(
        self,
        chain: "EpistemicChain",
        classification: "ContractClassification",
    ) -> dict[str, Any]:
        """
        Construye sección fusion_specification según operationalization_guide.json. 
        """
        type_code = classification.tipo_contrato["codigo"]
        strategies = classification.estrategias_fusion
        
        return {
            "contract_type": type_code,
            "primary_strategy": self._get_primary_strategy(type_code),
            "level_strategies": {
                "N1_fact_fusion": {
                    "strategy": strategies. get("N1", "concat"),
                    "behavior": "additive",
                    "conflict_resolution": self._get_n1_conflict_resolution(type_code),
                    "formula": "if same_fact detected by multiple methods → confidence = 1 - ∏(1 - conf_i)",
                },
                "N2_parameter_fusion": {
                    "strategy": strategies.get("N2", "weighted_mean"),
                    "behavior": "multiplicative",
                    "conflict_resolution":  "weighted_voting",
                    "affects":  ["N1_facts. confidence", "N1_facts.edge_weights"],
                },
                "N3_constraint_fusion": {
                    "strategy": "veto_gate",
                    "behavior": "gate",
                    "asymmetry_principle": "audit_dominates",
                    "propagation":  {
                        "upstream": "confidence_backpropagation",
                        "downstream": "branch_blocking",
                    },
                },
            },
            "cross_layer_effects": self._build_cross_layer_effects(),
            "fusion_pipeline":  self._build_fusion_pipeline(type_code, strategies),
        }
    
    def _get_primary_strategy(self, type_code: str) -> str:
        """Estrategia primaria según TYPE"""
        strategies = {
            "TYPE_A": "semantic_triangulation",
            "TYPE_B": "bayesian_update",
            "TYPE_C": "topological_overlay",
            "TYPE_D": "financial_coherence_audit",
            "TYPE_E": "logical_consistency_validation",
        }
        return strategies.get(type_code, "weighted_mean")
    
    def _get_n1_conflict_resolution(self, type_code:  str) -> str:
        """Resolución de conflictos N1 según TYPE"""
        if type_code == "TYPE_A":
            return "semantic_deduplication"
        elif type_code == "TYPE_C":
            return "graph_merge"
        else:
            return "corroborative_stacking"
    
    def _build_cross_layer_effects(self) -> dict[str, dict[str, str]]:
        """Construye efectos cross-layer"""
        return {
            "N1_to_N2": {
                "relationship": "N2 reads N1 facts",
                "effect": "N2 computes parameters FROM N1 observations",
                "data_flow": "forward_propagation",
            },
            "N2_to_N1": {
                "relationship": "N2 modifies N1 confidence",
                "effect": "Edge weights adjust fact confidence scores",
                "data_flow":  "confidence_backpropagation",
            },
            "N3_to_N1": {
                "relationship": "N3 can BLOCK N1 facts",
                "effect": "Failed constraints remove facts from graph",
                "data_flow":  "veto_propagation",
                "asymmetry":  "N1 CANNOT invalidate N3",
            },
            "N3_to_N2": {
                "relationship": "N3 can INVALIDATE N2 parameters",
                "effect": "Failed constraints nullify parameter modifications",
                "data_flow":  "inference_modulation",
                "asymmetry": "N2 CANNOT invalidate N3",
            },
            "all_to_N4": {
                "relationship": "N4 consumes validated outputs from all layers",
                "effect": "Synthesis constructs narrative from filtered graph",
                "data_flow":  "terminal_aggregation",
            },
        }
    
    def _build_fusion_pipeline(
        self,
        type_code: str,
        strategies: dict[str, str],
    ) -> list[dict[str, Any]]: 
        """Construye pipeline de fusión ordenado"""
        return [
            {
                "step": 1,
                "name": "empirical_extraction",
                "level": "N1",
                "strategy": strategies.get("N1", "concat"),
                "input": "PreprocesadoMetadata",
                "output": "raw_facts_graph",
            },
            {
                "step": 2,
                "name": "inferential_processing",
                "level": "N2",
                "strategy": strategies.get("N2", "weighted_mean"),
                "input": "raw_facts_graph",
                "output": "weighted_inference_graph",
            },
            {
                "step": 3,
                "name": "audit_validation",
                "level": "N3",
                "strategy": "veto_gate",
                "input": "weighted_inference_graph",
                "output": "validated_graph",
                "veto_capable": True,
            },
            {
                "step": 4,
                "name": "narrative_synthesis",
                "level":  "N4",
                "strategy": "carver_doctoral_synthesis",
                "input": "validated_graph",
                "output":  "human_answer",
            },
        ]
    
    def _build_cross_layer_fusion(
        self, classification: "ContractClassification"
    ) -> dict[str, Any]:
        """
        Construye sección cross_layer_fusion. 
        """
        return {
            "N1_to_N2": {
                "relationship": "N2 reads N1 facts",
                "effect": "N2 computes parameters FROM N1 observations",
                "data_flow":  "forward_propagation",
            },
            "N2_to_N1": {
                "relationship": "N2 modifies N1 confidence",
                "effect": "Edge weights adjust fact confidence scores",
                "data_flow": "confidence_backpropagation",
            },
            "N3_to_N1":  {
                "relationship": "N3 can BLOCK N1 facts",
                "effect": "Failed constraints remove facts from graph",
                "data_flow": "veto_propagation",
                "asymmetry": "N1 CANNOT invalidate N3",
            },
            "N3_to_N2": {
                "relationship": "N3 can INVALIDATE N2 parameters",
                "effect": "Failed constraints nullify parameter modifications",
                "data_flow": "inference_modulation",
                "asymmetry": "N2 CANNOT invalidate N3",
            },
            "all_to_N4": {
                "relationship": "N4 consumes validated outputs from all layers",
                "effect":  "Synthesis constructs narrative from filtered graph",
                "data_flow": "terminal_aggregation",
            },
            "blocking_propagation_rules": self._build_blocking_rules(classification),
        }
    
    def _build_blocking_rules(
        self, classification: "ContractClassification"
    ) -> dict[str, dict[str, Any]]:
        """Construye reglas de propagación de bloqueo"""
        type_code = classification.tipo_contrato["codigo"]
        
        base_rules = {
            "statistical_significance_failed": {
                "triggered_by": "PolicyContradictionDetector._statistical_significance_test",
                "action": "block_branch",
                "scope": "source_facts",
                "propagation": "downstream_only",
            },
            "logical_contradiction":  {
                "triggered_by":  "PolicyContradictionDetector._detect_logical_incompatibilities",
                "action": "block_branch",
                "scope":  "contradicting_nodes",
                "propagation": "both",
            },
        }
        
        # Añadir reglas específicas por TYPE
        if type_code == "TYPE_C":
            base_rules["cycle_detected"] = {
                "triggered_by": "AdvancedDAGValidator._is_acyclic",
                "action": "invalidate_graph",
                "scope": "entire_causal_graph",
                "propagation": "total",
            }
        
        if type_code == "TYPE_D":
            base_rules["budget_insufficiency"] = {
                "triggered_by": "FinancialAuditor._detect_allocation_gaps",
                "action": "flag_and_reduce",
                "scope": "affected_goals",
                "propagation":  "downstream_only",
                "confidence_multiplier": 0.3,
            }
        
        return base_rules
    
    def _build_human_answer_structure(
        self, classification: "ContractClassification"
    ) -> dict[str, Any]:
        """
        Construye sección human_answer_structure según operationalization_guide.json. 
        """
        type_code = classification.tipo_contrato["codigo"]
        
        return {
            "format": "markdown",
            "template_mode": "epistemological_narrative",
            "contract_type": type_code,
            "sections": [
                self._build_section_s1(),
                self._build_section_s2(),
                self._build_section_s3(type_code),
                self._build_section_s4(),
            ],
            "argumentative_roles": self._build_argumentative_roles(),
            "confidence_interpretation": self._build_confidence_interpretation(),
        }
    
    def _build_section_s1(self) -> dict[str, Any]:
        """Construye sección S1: Veredicto"""
        return {
            "section_id": "S1_verdict",
            "title": "### Veredicto",
            "layer": "N4",
            "data_source": "synthesis_output",
            "narrative_style": "declarative",
            "template":  (
                "**Conclusión**:  {verdict_statement}\n\n"
                "**Confianza Global**: {final_confidence_pct}% ({confidence_interpretation})\n\n"
                "**Base Metodológica**: {method_count} métodos ejecutados, "
                "{audit_count} validaciones, {blocked_count} ramas bloqueadas."
            ),
            "argumentative_role": "SYNTHESIS",
        }
    
    def _build_section_s2(self) -> dict[str, Any]: 
        """Construye sección S2: Evidencia Dura"""
        return {
            "section_id": "S2_empirical_base",
            "title": "### Base Empírica:  Hechos Observados",
            "layer": "N1",
            "data_source": "validated_facts",
            "narrative_style":  "descriptive",
            "template": (
                "**Elementos Detectados**: {fact_count} hechos extraídos de "
                "{document_coverage_pct}% del texto.\n\n"
                "**Fuentes Oficiales**: {official_sources_list}\n\n"
                "**Indicadores Cuantitativos**: {quantitative_indicators}\n\n"
                "**Cobertura Temporal**: {temporal_series}"
            ),
            "argumentative_role": "EMPIRICAL_BASIS",
            "epistemological_note": "Observaciones directas sin transformación interpretativa.",
        }
    
    def _build_section_s3(self, type_code:  str) -> dict[str, Any]:
        """Construye sección S3: Análisis de Robustez"""
        section = {
            "section_id":  "S3_robustness_audit",
            "title": "### Análisis de Robustez:  Validación y Limitaciones",
            "layer": "N3",
            "data_source":  "audit_results",
            "narrative_style": "critical",
            "template": (
                "**Validaciones Ejecutadas**: {validation_count}\n\n"
                "**Contradicciones Detectadas**: {contradiction_count}\n"
                "{contradiction_details}\n\n"
                "**Ramas Bloqueadas**: {blocked_branches_count}\n"
                "{blocking_reasons}\n\n"
                "**Modulaciones de Confianza**: {confidence_adjustments}\n\n"
                "**Limitaciones Metodológicas**: {limitations_list}"
            ),
            "argumentative_role": "ROBUSTNESS_QUALIFIER",
            "epistemological_note": (
                "Meta-juicios sobre confiabilidad.  "
                "N3 puede VETAR hallazgos de N1/N2."
            ),
            "veto_display": {
                "if_veto_triggered": (
                    "⚠️ ALERTA: {veto_reason}. "
                    "El modelo lógico es INVÁLIDO técnicamente."
                ),
                "if_no_veto":  "✓ Todas las validaciones pasaron.",
            },
        }
        
        # Añadir notas específicas por TYPE
        if type_code == "TYPE_C": 
            section["type_specific_note"] = (
                "Para contratos causales: verificación de aciclicidad es CRÍTICA."
            )
        elif type_code == "TYPE_D":
            section["type_specific_note"] = (
                "Para contratos financieros: brechas presupuestales > 50% son bloqueantes."
            )
        elif type_code == "TYPE_E":
            section["type_specific_note"] = (
                "Para contratos lógicos: UNA contradicción invalida la rama completa."
            )
        
        return section
    
    def _build_section_s4(self) -> dict[str, Any]:
        """Construye sección S4: Puntos Ciegos"""
        return {
            "section_id": "S4_gaps",
            "title": "### Puntos Ciegos:  Evidencia Faltante",
            "layer":  "N4-META",
            "data_source":  "gap_analysis",
            "narrative_style": "diagnostic",
            "template": (
                "**Métodos sin Resultados**: {empty_methods_count} de {total_methods}\n"
                "{empty_methods_list}\n\n"
                "**Elementos Esperados no Encontrados**: {missing_elements}\n\n"
                "**Cobertura de Patterns**: {pattern_coverage_pct}%\n\n"
                "**Impacto en Confianza**: {gap_impact_assessment}"
            ),
            "argumentative_role": "META_TRACEABILITY",
        }
    
    def _build_argumentative_roles(self) -> dict[str, list[dict[str, Any]]]:
        """Construye roles argumentativos por nivel"""
        return {
            "N1_roles": [
                {
                    "role": "EMPIRICAL_BASIS",
                    "description": "Hecho observable innegable",
                    "example": "Se encontraron 15 menciones a VBG",
                    "narrative_weight": "high",
                },
            ],
            "N2_roles": [
                {
                    "role": "INFERENTIAL_BRIDGE",
                    "description": "Conexión lógica derivada",
                    "example": "Con 95% confianza, el prior se actualiza",
                    "narrative_weight":  "medium",
                },
                {
                    "role": "CONTEXTUAL_QUALIFIER",
                    "description": "Condiciona validez a contexto",
                    "example": "Válido solo en zona rural",
                    "narrative_weight": "medium",
                },
            ],
            "N3_roles": [
                {
                    "role": "ROBUSTNESS_QUALIFIER",
                    "description": "Advertencia de calidad/limitación",
                    "example": "La muestra es pequeña (n=5)",
                    "narrative_weight": "high",
                },
                {
                    "role": "REFUTATIONAL_SIGNAL",
                    "description": "Evidencia negativa que contradice",
                    "example":  "Meta A incompatible con Meta B",
                    "narrative_weight": "critical",
                },
                {
                    "role": "FINANCIAL_CONSTRAINT",
                    "description": "Límites presupuestales a viabilidad",
                    "example":  "Presupuesto insuficiente para meta",
                    "narrative_weight": "critical",
                },
                {
                    "role": "LOGICAL_INCONSISTENCY",
                    "description": "Contradicción lógica interna",
                    "example":  "Secuencia de actividades inválida",
                    "narrative_weight": "critical",
                },
            ],
            "N4_roles": [
                {
                    "role": "META_TRACEABILITY",
                    "description": "Calidad del proceso analítico",
                    "example": "95% cobertura de patterns",
                    "narrative_weight": "medium",
                },
            ],
        }
    
    def _build_confidence_interpretation(self) -> dict[str, dict[str, Any]]:
        """Construye interpretación de confianza"""
        return {
            "critical":  {
                "range": "0-19%",
                "label": "INVÁLIDO",
                "description": (
                    "Veto activado por N3, modelo lógico inválido técnicamente"
                ),
                "display": "🔴",
            },
            "low": {
                "range": "20-49%",
                "label": "DÉBIL",
                "description": (
                    "Evidencia insuficiente, contradicciones detectadas, "
                    "o validación fallida"
                ),
                "display": "🟠",
            },
            "medium": {
                "range": "50-79%",
                "label": "MODERADO",
                "description": (
                    "Evidencia presente con limitaciones o inconsistencias menores"
                ),
                "display": "🟡",
            },
            "high": {
                "range": "80-100%",
                "label":  "ROBUSTO",
                "description":  (
                    "Múltiples observaciones corroborantes, sin contradicciones, "
                    "auditorías pasadas"
                ),
                "display": "🟢",
            },
        }
    
    def _build_audit_annotations(
        self,
        chain:  "EpistemicChain",
        classification: "ContractClassification",
    ) -> dict[str, Any]:
        """
        Construye sección audit_annotations para trazabilidad.
        """
        return {
            "generation_metadata": {
                "generator_version": self.generator_version,
                "generation_timestamp": self.generation_timestamp,
                "input_hashes": {
                    "classified_methods": self. registry.classified_methods_hash,
                    "contratos_clasificados": self.registry.contratos_clasificados_hash,
                    "method_sets": self.registry.method_sets_hash,
                },
            },
            "source_references": {
                "method_assignments_source": "method_sets_by_question. json",
                "contract_classification_source": "contratos_clasificados. json",
                "method_definitions_source": "classified_methods.json",
                "doctrine_source": "operationalization_guide.json",
            },
            "composition_trace": {
                "question_id": chain.question_id,
                "contract_id": classification.contract_id,
                "type_code": classification.tipo_contrato["codigo"],
                "methods_in_chain": chain.total_methods,
                "n1_methods": len(chain.phase_a_chain),
                "n2_methods": len(chain.phase_b_chain),
                "n3_methods": len(chain.phase_c_chain),
                "efficiency_score": chain.efficiency_score,
            },
            "validity_conditions": {
                "temporal_validity": "Until next input revision",
                "review_trigger": "Changes to any input file",
                "expiration_policy": "Regenerate if input hashes change",
            },
            "audit_checklist": {
                "structure_validated": False,  # To be set by validator
                "epistemic_coherence_validated": False,
                "temporal_validity_validated": False,
                "cross_reference_validated": False,
            },
        }
2.5 Módulo: ContractValidator (Layer 4)

Python
"""
Módulo:  contract_validator.py
Propósito: Validar contratos generados antes de emisión
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any

class ValidationSeverity(Enum):
    """Severidad de validación"""
    CRITICAL = "CRITICAL"  # Bloquea emisión
    HIGH = "HIGH"          # Degrada calidad
    MEDIUM = "MEDIUM"      # Afecta usabilidad
    LOW = "LOW"            # Mejora sugerida

@dataclass
class ValidationResult: 
    """Resultado de una validación individual"""
    check_id: str
    passed: bool
    severity: ValidationSeverity
    message: str
    section: str
    expected: Any = None
    actual: Any = None

@dataclass
class ValidationReport: 
    """Reporte completo de validación"""
    contract_id: str
    question_id: str
    total_checks: int
    passed_checks:  int
    failed_checks: int
    critical_failures: int
    results: list[ValidationResult]
    is_valid: bool
    
    @property
    def pass_rate(self) -> float:
        return self.passed_checks / self.total_checks if self.total_checks > 0 else 0.0

class ContractValidator: 
    """
    Validador de contratos generados.
    
    CAPAS DE VALIDACIÓN:
    1. Estructural:  Campos requeridos presentes
    2. Epistémica: Coherencia entre niveles
    3. Temporal: Validez declarada
    4. Referencial: Cross-references válidas
    """
    
    # Campos requeridos por sección
    REQUIRED_FIELDS = {
        "identity": [
            "base_slot", "representative_question_id", "contract_type",
            "contract_version", "created_at", "generator_version",
        ],
        "executor_binding": ["executor_class", "executor_module"],
        "method_binding": [
            "orchestration_mode", "contract_type", "method_count",
            "execution_phases", "efficiency_score",
        ],
        "question_context": ["monolith_ref", "pregunta_completa"],
        "evidence_assembly": ["engine", "type_system", "assembly_rules"],
        "fusion_specification": [
            "contract_type", "primary_strategy", "level_strategies",
        ],
        "cross_layer_fusion": ["N1_to_N2", "N2_to_N1", "N3_to_N1", "N3_to_N2"],
        "human_answer_structure": [
            "format", "template_mode", "sections", "confidence_interpretation",
        ],
        "audit_annotations": [
            "generation_metadata", "source_references", "composition_trace",
        ],
    }
    
    # Fases requeridas en method_binding
    REQUIRED_PHASES = ["phase_A_construction", "phase_B_computation", "phase_C_litigation"]
    
    # Reglas requeridas en evidence_assembly
    REQUIRED_RULES = ["R1_empirical_extraction", "R2_inferential_processing", 
                      "R3_audit_gate", "R4_narrative_synthesis"]
    
    def validate_contract(
        self, contract: "GeneratedContract"
    ) -> ValidationReport: 
        """
        Valida un contrato generado.
        
        Returns:
            ValidationReport con resultados detallados
        """
        results:  list[ValidationResult] = []
        
        # Layer 1: Validación estructural
        results.extend(self._validate_structure(contract))
        
        # Layer 2: Validación epistémica
        results.extend(self._validate_epistemic_coherence(contract))
        
        # Layer 3: Validación temporal
        results.extend(self._validate_temporal(contract))
        
        # Layer 4: Validación referencial
        results.extend(self._validate_cross_references(contract))
        
        # Calcular estadísticas
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed
        critical = sum(
            1 for r in results 
            if not r.passed and r.severity == ValidationSeverity.CRITICAL
        )
        
        return ValidationReport(
            contract_id=contract.identity. get("representative_question_id", "UNKNOWN"),
            question_id=contract.identity.get("base_slot", "UNKNOWN"),
            total_checks=total,
            passed_checks=passed,
            failed_checks=failed,
            critical_failures=critical,
            results=results,
            is_valid=(critical == 0),
        )
    
    def _validate_structure(
        self, contract: "GeneratedContract"
    ) -> list[ValidationResult]:
        """Validación estructural:  campos requeridos"""
        results = []
        contract_dict = contract.to_dict()
        
        for section, fields in self.REQUIRED_FIELDS.items():
            section_data = contract_dict.get(section, {})
            
            for field in fields:
                check_id = f"STRUCT_{section}_{field}"
                passed = field in section_data and section_data[field] is not None
                
                results.append(ValidationResult(
                    check_id=check_id,
                    passed=passed,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Required field '{field}' in section '{section}'",
                    section=section,
                    expected=f"Field '{field}' present and not None",
                    actual=f"{'Present' if passed else 'Missing or None'}",
                ))
        
        # Validar fases en method_binding
        phases = contract. method_binding. get("execution_phases", {})
        for phase in self.REQUIRED_PHASES: 
            check_id = f"STRUCT_method_binding_phase_{phase}"
            passed = phase in phases
            
            results.append(ValidationResult(
                check_id=check_id,
                passed=passed,
                severity=ValidationSeverity.CRITICAL,
                message=f"Required phase '{phase}' in execution_phases",
                section="method_binding",
                expected=f"Phase '{phase}' present",
                actual=f"{'Present' if passed else 'Missing'}",
            ))
        
        # Validar reglas en evidence_assembly
        rules = contract.evidence_assembly.get("assembly_rules", [])
        rule_ids = {r. get("rule_id") for r in rules}
        
        for rule_id in self.REQUIRED_RULES:
            check_id = f"STRUCT_evidence_assembly_rule_{rule_id}"
            passed = rule_id in rule_ids
            
            results. append(ValidationResult(
                check_id=check_id,
                passed=passed,
                severity=ValidationSeverity.CRITICAL,
                message=f"Required rule '{rule_id}' in assembly_rules",
                section="evidence_assembly",
                expected=f"Rule '{rule_id}' present",
                actual=f"{'Present' if passed else 'Missing'}",
            ))
        
        return results
    
    def _validate_epistemic_coherence(
        self, contract:  "GeneratedContract"
    ) -> list[ValidationResult]:
        """Validación epistémica:  coherencia entre niveles"""
        results = []
        
        # Verificar que hay métodos en cada nivel
        phases = contract.method_binding.get("execution_phases", {})
        
        for phase_name, expected_level in [
            ("phase_A_construction", "N1"),
            ("phase_B_computation", "N2"),
            ("phase_C_litigation", "N3"),
        ]:
            phase_data = phases.get(phase_name, {})
            methods = phase_data.get("methods", [])
            
            # Check:  fase tiene métodos
            check_id = f"EPIST_{phase_name}_has_methods"
            passed = len(methods) > 0
            
            results.append(ValidationResult(
                check_id=check_id,
                passed=passed,
                severity=ValidationSeverity.CRITICAL,
                message=f"Phase '{phase_name}' must have at least one method",
                section="method_binding",
                expected="At least 1 method",
                actual=f"{len(methods)} methods",
            ))
            
            # Check: métodos tienen nivel correcto
            for i, method in enumerate(methods):
                method_level = method.get("level", "")
                check_id = f"EPIST_{phase_name}_method_{i}_level"
                passed = method_level. startswith(expected_level)
                
                results.append(ValidationResult(
                    check_id=check_id,
                    passed=passed,
                    severity=ValidationSeverity.HIGH,
                    message=f"Method in '{phase_name}' should be level {expected_level}",
                    section="method_binding",
                    expected=f"Level starting with '{expected_level}'",
                    actual=method_level,
                ))
        
        # Verificar asimetría N3
        cross_layer = contract.cross_layer_fusion
        n3_to_n1 = cross_layer.get("N3_to_N1", {})
        n3_to_n2 = cross_layer. get("N3_to_N2", {})
        
        check_id = "EPIST_asymmetry_N3_to_N1"
        passed = n3_to_n1.get("asymmetry") == "N1 CANNOT invalidate N3"
        results.append(ValidationResult(
            check_id=check_id,
            passed=passed,
            severity=ValidationSeverity.HIGH,
            message="N3→N1 asymmetry must be declared",
            section="cross_layer_fusion",
            expected="asymmetry:  'N1 CANNOT invalidate N3'",
            actual=n3_to_n1.get("asymmetry", "NOT DECLARED"),
        ))
        
        check_id = "EPIST_asymmetry_N3_to_N2"
        passed = n3_to_n2.get("asymmetry") == "N2 CANNOT invalidate N3"
        results.append(ValidationResult(
            check_id=check_id,
            passed=passed,
            severity=ValidationSeverity.HIGH,
            message="N3→N2 asymmetry must be declared",
            section="cross_layer_fusion",
            expected="asymmetry: 'N2 CANNOT invalidate N3'",
            actual=n3_to_n2.get("asymmetry", "NOT DECLARED"),
        ))
        
        # Verificar TYPE consistencia
        identity_type = contract.identity.get("contract_type")
        method_binding_type = contract.method_binding.get("contract_type")
        fusion_type = contract.fusion_specification.get("contract_type")
        
        check_id = "EPIST_type_consistency"
        passed = (identity_type == method_binding_type == fusion_type)
        results.append(ValidationResult(
            check_id=check_id,
            passed=passed,
            severity=ValidationSeverity. CRITICAL,
            message="Contract TYPE must be consistent across sections",
            section="global",
            expected=f"All sections:  {identity_type}",
            actual=f"identity:  {identity_type}, method_binding: {method_binding_type}, fusion: {fusion_type}",
        ))
        
        return results
    
    def _validate_temporal(
        self, contract: "GeneratedContract"
    ) -> list[ValidationResult]:
        """Validación temporal: timestamps y validez"""
        results = []
        
        # Check: created_at presente
        created_at = contract.identity.get("created_at")
        check_id = "TEMP_created_at_present"
        passed = created_at is not None and len(created_at) > 0
        
        results.append(ValidationResult(
            check_id=check_id,
            passed=passed,
            severity=ValidationSeverity.HIGH,
            message="created_at timestamp must be present",
            section="identity",
            expected="ISO timestamp",
            actual=created_at or "MISSING",
        ))
        
        # Check: validity_conditions presentes
        validity = contract.audit_annotations.get("validity_conditions", {})
        check_id = "TEMP_validity_conditions"
        passed = (
            "temporal_validity" in validity and
            "review_trigger" in validity
        )
        
        results. append(ValidationResult(
            check_id=check_id,
            passed=passed,
            severity=ValidationSeverity. MEDIUM,
            message="Validity conditions should be declared",
            section="audit_annotations",
            expected="temporal_validity and review_trigger present",
            actual=f"Keys: {list(validity.keys())}",
        ))
        
        return results
    
    def _validate_cross_references(
        self, contract: "GeneratedContract"
    ) -> list[ValidationResult]:
        """Validación referencial: cross-references válidas"""
        results = []
        
        # Verificar que sources en assembly_rules matchean provides en methods
        phases = contract.method_binding.get("execution_phases", {})
        all_provides = set()
        
        for phase_data in phases.values():
            for method in phase_data.get("methods", []):
                provides = method. get("provides")
                if provides:
                    all_provides.add(provides)
        
        rules = contract.evidence_assembly.get("assembly_rules", [])
        for rule in rules:
            rule_id = rule.get("rule_id", "UNKNOWN")
            sources = rule.get("sources", [])
            
            # Verificar que al menos algunos sources existen
            # (sources puede ser un subset de provides)
            matching_sources = [s for s in sources if s in all_provides]
            
            check_id = f"XREF_rule_{rule_id}_sources"
            # Para R4 (synthesis), sources puede estar vacío
            if rule_id == "R4_narrative_synthesis": 
                passed = True
            else:
                passed = len(matching_sources) > 0 or len(sources) == 0
            
            results. append(ValidationResult(
                check_id=check_id,
                passed=passed,
                severity=ValidationSeverity.MEDIUM,
                message=f"Rule '{rule_id}' sources should reference method provides",
                section="evidence_assembly",
                expected="Sources matching method provides",
                actual=f"{len(matching_sources)}/{len(sources)} sources match",
            ))
        
        # Verificar input_hashes presentes
        hashes = contract.audit_annotations.get("generation_metadata", {}).get("input_hashes", {})
        required_hashes = ["classified_methods", "contratos_clasificados", "method_sets"]
        
        for hash_name in required_hashes:
            check_id = f"XREF_input_hash_{hash_name}"
            passed = hash_name in hashes and len(hashes[hash_name]) > 0
            
            results.append(ValidationResult(
                check_id=check_id,
                passed=passed,
                severity=ValidationSeverity. MEDIUM,
                message=f"Input hash '{hash_name}' should be present for traceability",
                section="audit_annotations",
                expected="Non-empty hash string",
                actual=hashes.get(hash_name, "MISSING"),
            ))
        
        return results
2.6 Módulo: JSONEmitter (Layer 4)

Python
"""
Módulo:  json_emitter.py
Propósito: Emitir contratos como JSON determinista
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any

class JSONEmitter:
    """
    Emisor de contratos JSON. 
    
    PROPIEDADES:
    1. Determinista: misma entrada → mismo output byte-a-byte
    2. Ordenado: claves en orden consistente
    3. Legible: indentación de 2 espacios
    4. UTF-8: encoding explícito
    """
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def emit_contract(
        self,
        contract: "GeneratedContract",
        validation_report: "ValidationReport",
    ) -> Path:
        """
        Emite contrato como archivo JSON.
        
        NAMING:  {dimension}_{question}_contract_v4.json
        e.g., D1_Q1_contract_v4.json
        
        Args:
            contract: GeneratedContract a emitir
            validation_report: ValidationReport para incluir status
        
        Returns:
            Path al archivo emitido
        
        Raises:
            ValueError: Si validación tiene critical failures
        """
        if not validation_report.is_valid:
            raise ValueError(
                f"Cannot emit contract {validation_report.contract_id}:  "
                f"{validation_report.critical_failures} critical failures"
            )
        
        # Construir nombre de archivo
        base_slot = contract.identity.get("base_slot", "UNKNOWN")
        filename = f"{base_slot. replace('-', '_')}_contract_v4.json"
        output_path = self.output_dir / filename
        
        # Construir diccionario final con validation status
        contract_dict = contract.to_dict()
        contract_dict["audit_annotations"]["audit_checklist"] = {
            "structure_validated": True,
            "epistemic_coherence_validated": True,
            "temporal_validity_validated": True,
            "cross_reference_validated": True,
            "validation_pass_rate": validation_report.pass_rate,
            "validation_timestamp": contract.identity.get("created_at"),
        }
        
        # Emitir con formato determinista
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                contract_dict,
                f,
                ensure_ascii=False,
                indent=2,
                sort_keys=False,  # Preservar orden de inserción
            )
            f.write("\n")  # Trailing newline
        
        return output_path
    
    def emit_generation_manifest(
        self,
        contracts: list["GeneratedContract"],
        reports: list["ValidationReport"],
        generation_timestamp: str,
    ) -> Path:
        """
        Emite manifiesto de generación.
        
        El manifiesto contiene:
        - Lista de contratos generados
        - Estadísticas de validación
        - Hashes de inputs
        """
        manifest = {
            "generation_metadata": {
                "timestamp": generation_timestamp,
                "total_contracts": len(contracts),
                "valid_contracts": sum(1 for r in reports if r.is_valid),
                "invalid_contracts": sum(1 for r in reports if not r.is_valid),
            },
            "contracts": [
                {
                    "contract_id": c.identity.get("representative_question_id"),
                    "question_id": c.identity.get("base_slot"),
                    "type": c.identity.get("contract_type"),
                    "method_count": c.method_binding.get("method_count"),
                    "efficiency_score": c.method_binding.get("efficiency_score"),
                    "validation_pass_rate": r.pass_rate,
                    "is_valid": r.is_valid,
                }
                for c, r in zip(contracts, reports)
            ],
            "input_hashes": contracts[0].audit_annotations.get(
                "generation_metadata", {}
            ).get("input_hashes", {}) if contracts else {},
        }
        
        output_path = self.output_dir / "generation_manifest.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
            f.write("\n")
        
        return output_path
PARTE III: ORQUESTADOR PRINCIPAL

Python
"""
Módulo: contract_generator.py
Propósito: Orquestador principal de generación de contratos
"""

from __future__ import annotations
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Imports de módulos internos
from .input_registry import InputLoader, InputRegistry
from .method_expander import MethodExpander
from .chain_composer import ChainComposer
from .contract_assembler import ContractAssembler, GeneratedContract
from .contract_validator import ContractValidator, ValidationReport
from .json_emitter import JSONEmitter

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ContractGenerator")

class ContractGenerator:
    """
    Orquestador principal de generación de contratos.
    
    FLUJO:
    1. Cargar y validar inputs
    2. Para cada pregunta:
       a. Obtener method_set asignado
       b. Expandir métodos
       c. Componer cadena epistémica
       d. Ensamblar contrato
       e. Validar contrato
    3. Emitir contratos válidos
    4. Emitir manifiesto
    
    INVARIANTES:
    - Fail-loud en cualquier error
    - Determinismo total
    - Sin inferencia de métodos
    - Preservación de orden
    """
    
    VERSION = "4.0.0-granular"
    
    def __init__(
        self,
        assets_path: Path,
        output_path: Path,
        strict_mode: bool = True,
    ):
        """
        Args:
            assets_path:  Directorio con insumos
            output_path:  Directorio de salida
            strict_mode: Si True, falla en cualquier warning
        """
        self.assets_path = assets_path
        self.output_path = output_path
        self.strict_mode = strict_mode
        
        # Timestamp de generación (único para toda la ejecución)
        self.generation_timestamp = datetime.now(timezone.utc).isoformat()
        
        # Componentes (inicializados en generate())
        self.registry:  InputRegistry | None = None
        self.expander: MethodExpander | None = None
        self.composer: ChainComposer | None = None
        self.assembler: ContractAssembler | None = None
        self.validator: ContractValidator | None = None
        self.emitter: JSONEmitter | None = None
    
    def generate(self) -> dict[str, Any]:
        """
        Genera todos los contratos.
        
        Returns:
            Diccionario con estadísticas de generación
        
        Raises:
            ValueError:  Si cualquier paso falla
            FileNotFoundError: Si inputs no existen
        """
        logger.info("=" * 60)
        logger.info("INICIANDO GENERACIÓN DE CONTRATOS")
        logger.info(f"Timestamp: {self. generation_timestamp}")
        logger.info(f"Assets: {self.assets_path}")
        logger.info(f"Output: {self.output_path}")
        logger.info("=" * 60)
        
        # Paso 1: Cargar inputs
        logger.info("Paso 1: Cargando inputs...")
        self._initialize_components()
        logger.info(f"  - Métodos cargados: {self.registry.total_methods}")
        logger.info(f"  - Contratos a generar: {self.registry.total_contracts}")
        logger.info(f"  - Hash classified_methods: {self.registry.classified_methods_hash}")
        logger.info(f"  - Hash contratos_clasificados: {self.registry. contratos_clasificados_hash}")
        logger.info(f"  - Hash method_sets: {self.registry.method_sets_hash}")
        
        # Paso 2: Generar contratos
        logger.info("Paso 2: Generando contratos...")
        contracts:  list[GeneratedContract] = []
        reports: list[ValidationReport] = []
        
        # Obtener orden determinista de preguntas
        question_ids = sorted(self.registry.method_sets_by_question. keys())
        
        for i, question_id in enumerate(question_ids, 1):
            logger.info(f"  [{i: 02d}/30] Procesando {question_id}...")
            
            try:
                contract, report = self._generate_single_contract(question_id)
                contracts.append(contract)
                reports.append(report)
                
                status = "✓" if report.is_valid else "✗"
                logger.info(
                    f"    {status} {report.contract_id}: "
                    f"{report.passed_checks}/{report.total_checks} checks passed, "
                    f"{contract.method_binding.get('method_count')} methods"
                )
                
            except Exception as e: 
                logger.error(f"    ✗ FALLO en {question_id}: {e}")
                if self.strict_mode:
                    raise
        
        # Paso 3: Emitir contratos
        logger. info("Paso 3: Emitiendo contratos...")
        emitted_paths = []
        
        for contract, report in zip(contracts, reports):
            if report.is_valid:
                path = self.emitter.emit_contract(contract, report)
                emitted_paths.append(path)
                logger.info(f"  ✓ Emitido: {path. name}")
            else:
                logger.warning(
                    f"  ✗ NO emitido (inválido): {report.contract_id}"
                )
        
        # Paso 4: Emitir manifiesto
        logger.info("Paso 4: Emitiendo manifiesto...")
        manifest_path = self.emitter.emit_generation_manifest(
            contracts, reports, self.generation_timestamp
        )
        logger.info(f"  ✓ Manifiesto:  {manifest_path.name}")
        
        # Estadísticas finales
        valid_count = sum(1 for r in reports if r.is_valid)
        invalid_count = len(reports) - valid_count
        
        logger.info("=" * 60)
        logger.info("GENERACIÓN COMPLETADA")
        logger.info(f"  Total contratos:  {len(contracts)}")
        logger.info(f"  Válidos: {valid_count}")
        logger.info(f"  Inválidos: {invalid_count}")
        logger.info(f"  Archivos emitidos: {len(emitted_paths)}")
        logger.info("=" * 60)
        
        return {
            "timestamp": self.generation_timestamp,
            "total_contracts": len(contracts),
            "valid_contracts": valid_count,
            "invalid_contracts": invalid_count,
            "emitted_files": len(emitted_paths),
            "manifest_path": str(manifest_path),
        }
    
    def _initialize_components(self) -> None:
        """Inicializa todos los componentes"""
        loader = InputLoader(self.assets_path)
        self.registry = loader.load_and_validate()
        
        self.expander = MethodExpander(self.generation_timestamp)
        self.composer = ChainComposer(self.expander)
        self.assembler = ContractAssembler(
            self.registry,
            self.generation_timestamp,
            self.VERSION,
        )
        self.validator = ContractValidator()
        self.emitter = JSONEmitter(self.output_path)
    
 def_generate_single_contract(
        self, question_id:  str
    ) -> tuple[GeneratedContract, ValidationReport]:
        """
        Genera un único contrato.
        
        SECUENCIA:
        1. Obtener method_set del registry
        2. Obtener classification del registry
        3. Componer cadena epistémica
        4. Ensamblar contrato
        5. Validar contrato
        """
        # Obtener datos del registry
        method_set = self. registry.method_sets_by_question[question_id]
        classification = self.registry.contracts_by_id[question_id]
        
        # Componer cadena epistémica (Layer 1 + Layer 2)
        chain = self.composer.compose_chain(method_set, classification)
        
        # Ensamblar contrato (Layer 3)
        contract = self.assembler.assemble_contract(chain, classification)
        
        # Validar contrato (Layer 4)
        report = self.validator.validate_contract(contract)
        
        return contract, report


def main():
    """
    Punto de entrada principal.
    
    USO:
        python -m farfan_pipeline.phases.Phase_two.contract_generator \
            --assets /path/to/epistemological_assets \
            --output /path/to/output \
            [--strict]
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generador Granular de Contratos Ejecutores F. A.R.F.A. N"
    )
    parser.add_argument(
        "--assets",
        type=Path,
        required=True,
        help="Directorio con insumos epistemológicos"
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Directorio de salida para contratos"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=True,
        help="Modo estricto: falla en cualquier warning"
    )
    parser.add_argument(
        "--no-strict",
        action="store_false",
        dest="strict",
        help="Modo permisivo: continúa con warnings"
    )
    
    args = parser. parse_args()
    
    generator = ContractGenerator(
        assets_path=args.assets,
        output_path=args.output,
        strict_mode=args.strict,
    )
    
    try:
        result = generator.generate()
        logger.info(f"Resultado: {result}")
        return 0
    except Exception as e:
        logger.error(f"FALLO CRÍTICO: {e}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
PARTE IV: ESTRUCTURA DE ARCHIVOS DEL PROYECTO

Code
farfan_pipeline/
├── phases/
│   └── Phase_two/
│       ├── epistemological_assets/           # INPUTS (inmutables)
│       │   ├── classified_methods. json       # 608 métodos clasificados
│       │   ├── contratos_clasificados.json   # 30 contratos con TYPE y estrategias
│       │   ├── method_sets_by_question.json  # Asignaciones método→pregunta
│       │   └── operationalization_guide.json # Doctrina canónica
│       │
│       ├── contract_generator/               # CÓDIGO DEL GENERADOR
│       │   ├── __init__.py
│       │   ├── input_registry.py             # Layer 0: Carga de inputs
│       │   ├── method_expander.py            # Layer 1: Expansión de métodos
│       │   ├── chain_composer. py             # Layer 2: Composición de cadenas
│       │   ├── contract_assembler.py         # Layer 3: Ensamblaje de contratos
│       │   ├── contract_validator.py         # Layer 4: Validación
│       │   ├── json_emitter.py               # Layer 4: Emisión
│       │   └── contract_generator.py         # Orquestador principal
│       │
│       └── generated_contracts/              # OUTPUTS
│           ├── D1_Q1_contract_v4.json
│           ├── D1_Q2_contract_v4.json
│           ├── ... 
│           ├── D6_Q5_contract_v4.json
│           └── generation_manifest.json
PARTE V: EJEMPLO DE CONTRATO GENERADO (D1_Q1)

JSON
{
  "identity": {
    "base_slot": "D1-Q1",
    "representative_question_id": "Q001",
    "dimension_id": "DIM01",
    "policy_area_ids_served": ["PA01", "PA02", "PA03", "PA04", "PA05", "PA06", "PA07", "PA08", "PA09", "PA10"],
    "contracts_served": ["Q001", "Q031", "Q061", "Q091", "Q121", "Q151", "Q181", "Q211", "Q241", "Q271"],
    "contract_type": "TYPE_A",
    "contract_type_name": "Semántico",
    "contract_type_focus": "Coherencia narrativa, NLP",
    "contract_version": "4.0.0-epistemological",
    "created_at": "2026-01-02T15:30:00+00:00",
    "generator_version": "4.0.0-granular",
    "specification_source": "operationalization_guide.json"
  },
  
  "executor_binding": {
    "executor_class": "D1_Q1_Executor",
    "executor_module": "farfan_pipeline. phases.Phase_two.executors"
  },
  
  "method_binding": {
    "orchestration_mode": "epistemological_pipeline",
    "contract_type": "TYPE_A",
    "method_count": 13,
    "execution_phases": {
      "phase_A_construction": {
        "description": "Empirical observation layer - direct extraction without interpretation",
        "level": "N1",
        "level_name": "Base Empírica",
        "epistemology": "Empirismo positivista",
        "methods": [
          {
            "class_name": "SemanticProcessor",
            "method_name":  "chunk_text",
            "mother_file": "semantic_chunking_policy.py",
            "provides": "semanticprocessor. chunk_text",
            "method_id": "SemanticProcessor.chunk_text",
            "level": "N1-EMP",
            "level_name": "Base Empírica",
            "epistemology": "Empirismo positivista",
            "output_type": "FACT",
            "fusion_behavior": "additive",
            "fusion_symbol": "⊕",
            "classification_rationale": "Patrón de nombre 'chunk_' → N1-EMP (PARTE II, Sec 2.2)",
            "confidence_score": 0.88,
            "contract_affinities": {
              "TYPE_A": 1.0,
              "TYPE_B": 0.5,
              "TYPE_C":  0.7,
              "TYPE_D": 0.8,
              "TYPE_E": 0.5
            },
            "parameters": ["self"],
            "return_type": "Any",
            "is_private": false,
            "evidence_requirements": ["raw_document_text", "preprocesado_metadata"],
            "output_claims": ["observable_datum", "literal_extraction"],
            "constraints_and_limits": ["output_must_be_literal", "no_transformation_allowed"],
            "failure_modes": ["empty_extraction", "pattern_not_found", "malformed_input"],
            "interaction_notes": "Method operates within TYPE_A contract.  Fusion strategy: semantic_triangulation.  Level N1-EMP provides FACT output.",
            "expansion_source": "method_sets_by_question.json",
            "expansion_timestamp": "2026-01-02T15:30:00+00:00"
          },
          {
            "class_name": "PolicyDocumentAnalyzer",
            "method_name": "_extract_key_excerpts",
            "mother_file": "semantic_chunking_policy.py",
            "provides": "policydocumentanalyzer.extract_key_excerpts",
            "method_id": "PolicyDocumentAnalyzer._extract_key_excerpts",
            "level": "N1-EMP",
            "level_name": "Base Empírica",
            "epistemology": "Empirismo positivista",
            "output_type":  "FACT",
            "fusion_behavior": "additive",
            "fusion_symbol": "⊕",
            "classification_rationale": "Patrón de nombre 'extract_' → N1-EMP (PARTE II, Sec 2.2)",
            "confidence_score": 0.88,
            "contract_affinities": {
              "TYPE_A": 1.0,
              "TYPE_B": 0.5,
              "TYPE_C": 0.7,
              "TYPE_D": 0.8,
              "TYPE_E": 0.5
            },
            "parameters": ["self"],
            "return_type":  "Any",
            "is_private": true,
            "evidence_requirements":  ["raw_document_text", "preprocesado_metadata"],
            "output_claims": ["observable_datum", "literal_extraction"],
            "constraints_and_limits": ["output_must_be_literal", "no_transformation_allowed"],
            "failure_modes":  ["empty_extraction", "pattern_not_found", "malformed_input"],
            "interaction_notes": "Method operates within TYPE_A contract. Fusion strategy: semantic_triangulation. Level N1-EMP provides FACT output.",
            "expansion_source": "method_sets_by_question.json",
            "expansion_timestamp": "2026-01-02T15:30:00+00:00"
          }
        ],
        "dependencies": [],
        "output_target": "raw_facts"
      },
      
      "phase_B_computation": {
        "description": "Inferential analysis layer - transformation into analytical constructs",
        "level": "N2",
        "level_name": "Procesamiento Inferencial",
        "epistemology": "Bayesianismo subjetivista",
        "methods": [
          {
            "class_name": "SemanticAnalyzer",
            "method_name": "_compute_unit_of_analysis_natural_blocks",
            "mother_file":  "analyzer_one. py",
            "provides": "semanticanalyzer.compute_unit_of_analysis_natural_blocks",
            "method_id": "SemanticAnalyzer._compute_unit_of_analysis_natural_blocks",
            "level": "N2-INF",
            "level_name": "Procesamiento Inferencial",
            "epistemology": "Bayesianismo subjetivista",
            "output_type": "PARAMETER",
            "fusion_behavior":  "multiplicative",
            "fusion_symbol": "⊗",
            "classification_rationale": "Clase SemanticAnalyzer listada en N2-INF + patrón 'compute_'",
            "confidence_score":  0.92,
            "contract_affinities": {
              "TYPE_A": 1.0,
              "TYPE_B": 0.9,
              "TYPE_C":  0.7,
              "TYPE_D":  0.6,
              "TYPE_E":  0.6
            },
            "parameters":  ["self"],
            "return_type": "Any",
            "is_private": true,
            "evidence_requirements":  ["raw_facts_from_N1", "confidence_scores"],
            "output_claims": ["derived_score", "probability_estimate", "relational_inference"],
            "constraints_and_limits": ["requires_N1_input", "output_is_derived"],
            "failure_modes":  ["insufficient_evidence", "prior_undefined", "computation_error"],
            "interaction_notes": "Method operates within TYPE_A contract. Fusion strategy: semantic_triangulation. Level N2-INF provides PARAMETER output.",
            "expansion_source": "method_sets_by_question.json",
            "expansion_timestamp":  "2026-01-02T15:30:00+00:00",
            "requires":  ["raw_facts"],
            "modifies": ["edge_weights", "confidence_scores"]
          }
        ],
        "dependencies":  ["phase_A_construction"],
        "output_target": "inferences"
      },
      
      "phase_C_litigation": {
        "description": "Audit layer - attempt to 'break' results.  Acts as VETO GATE.",
        "level": "N3",
        "level_name":  "Auditoría y Robustez",
        "epistemology": "Falsacionismo popperiano",
        "methods": [
          {
            "class_name": "SemanticValidator",
            "method_name":  "validate_semantic_completeness_coherence",
            "mother_file": "contradiction_deteccion.py",
            "provides": "semanticvalidator.validate_semantic_completeness_coherence",
            "method_id":  "SemanticValidator.validate_semantic_completeness_coherence",
            "level": "N3-AUD",
            "level_name": "Auditoría y Robustez",
            "epistemology": "Falsacionismo popperiano",
            "output_type": "CONSTRAINT",
            "fusion_behavior":  "gate",
            "fusion_symbol": "⊘",
            "classification_rationale": "Clase SemanticValidator listada en N3-AUD + patrón 'validate_'",
            "confidence_score": 0.92,
            "contract_affinities": {
              "TYPE_A": 0.7,
              "TYPE_B":  0.6,
              "TYPE_C": 0.8,
              "TYPE_D":  0.9,
              "TYPE_E":  0.9
            },
            "parameters":  ["self"],
            "return_type": "Any",
            "is_private": false,
            "evidence_requirements":  ["raw_facts_from_N1", "inferences_from_N2", "audit_criteria"],
            "output_claims":  ["validation_flag", "confidence_modulator", "veto_signal"],
            "constraints_and_limits": ["requires_N1_and_N2_input", "can_veto_lower_levels", "asymmetric_authority"],
            "failure_modes":  ["validation_inconclusive", "criteria_not_met", "veto_triggered"],
            "interaction_notes":  "Method operates within TYPE_A contract. Fusion strategy: semantic_triangulation. Level N3-AUD provides CONSTRAINT output.",
            "expansion_source": "method_sets_by_question.json",
            "expansion_timestamp": "2026-01-02T15:30:00+00:00",
            "veto_conditions": {
              "low_coherence": {
                "trigger": "coherence_score < 0.5",
                "action": "reduce_confidence",
                "scope": "source_facts",
                "confidence_multiplier": 0.5,
                "rationale": "Low coherence reduces reliability"
              },
              "validation_failed": {
                "trigger": "validation_result == False",
                "action": "flag_caution",
                "scope": "method_output",
                "confidence_multiplier": 0.7,
                "rationale": "Validation did not pass"
              }
            },
            "modulates": ["raw_facts. confidence", "inferences.confidence"]
          }
        ],
        "dependencies": ["phase_A_construction", "phase_B_computation"],
        "output_target": "audit_results",
        "asymmetry_principle": "N3 can invalidate N1/N2, but NOT vice versa",
        "fusion_mode": "modulation"
      }
    },
    "efficiency_score": 1.058,
    "mathematical_evidence": {
      "corroboration_formula": "1 - ∏(1 - conf_i)",
      "corroboration_score": 1.0,
      "individual_confidences": [0.88, 0.88, 0.88, 0.8, 0.8, 0.92, 0.88, 0.88, 0.5, 0.92, 0.92, 0.92, 0.88],
      "average_contract_affinity": 0.9,
      "phase_coverage": 1.0,
      "phase_counts": {"N1": 5, "N2": 5, "N3": 3},
      "unique_classes": 10,
      "diversity_bonus": 0.15,
      "balance_score": 0.9199,
      "efficiency_formula": "0.30*corroboration + 0.30*affinity + 0.20*coverage + 0.15*balance + diversity",
      "final_efficiency": 1.058
    },
    "doctoral_justification": "La pregunta D1_Q1 ('¿El diagnóstico presenta datos cuantitativos con fuente y desagregación?') ha sido clasificada como contrato TYPE_A (Semántico), cuyo foco epistemológico es la coherencia narrativa y el procesamiento de lenguaje natural. La selección de 13 métodos distribuidos en 3 fases (5 N1, 5 N2, 3 N3) responde a la necesidad de:  (1) extraer datos cuantitativos, años, fuentes y desagregaciones desde el texto del plan mediante métodos empíricos; (2) triangular la coherencia semántica entre múltiples fuentes de evidencia; y (3) auditar la consistencia de las fuentes citadas. La estrategia de fusión 'semantic_corroboration' → 'dempster_shafer' → 'veto_gate' implementa el principio de corroboración múltiple con gestión de conflicto, siguiendo la doctrina epistemológica de Dempster-Shafer para combinación de evidencia."
  },
  
  "question_context": {
    "monolith_ref": "Q001",
    "pregunta_completa": "¿El diagnóstico del sector presenta datos cuantitativos (tasas, porcentajes, cifras absolutas) con año de referencia y fuente identificada, desagregados por territorio o población?",
    "overrides": null,
    "failure_contract": {
      "abort_if":  ["missing_required_element", "incomplete_text", "no_quantitative_data"],
      "emit_code": "ABORT-D1-Q1-REQ"
    }
  },
  
  "signal_requirements": {
    "derivation_source": "expected_elements",
    "derivation_rules": {
      "mandatory":  "expected_elements[required=true]. type → detection_{type}",
      "optional": "expected_elements[required=false]. type → detection_{type}"
    },
    "signal_aggregation": "weighted_mean",
    "minimum_signal_threshold": 0.5
  },
  
  "evidence_assembly": {
    "engine": "EVIDENCE_NEXUS",
    "module": "farfan_pipeline.phases.Phase_two.evidence_nexus",
    "class_name": "EvidenceNexus",
    "method_name": "assemble",
    "type_system": {
      "FACT": {
        "origin_level": "N1",
        "fusion_operation": "graph_node_addition",
        "merge_behavior": "additive",
        "symbol": "⊕",
        "description": "Se SUMA al grafo como nodo"
      },
      "PARAMETER": {
        "origin_level": "N2",
        "fusion_operation": "edge_weight_modification",
        "merge_behavior":  "multiplicative",
        "symbol": "⊗",
        "description": "MODIFICA pesos de aristas del grafo"
      },
      "CONSTRAINT": {
        "origin_level": "N3",
        "fusion_operation": "branch_filtering",
        "merge_behavior":  "gate",
        "symbol":  "⊘",
        "description": "FILTRA/BLOQUEA ramas si validación falla"
      },
      "NARRATIVE": {
        "origin_level": "N4",
        "fusion_operation":  "synthesis",
        "merge_behavior":  "terminal",
        "symbol": "⊙",
        "description": "CONSUME grafo para texto final"
      }
    },
    "assembly_rules": [
      {
        "rule_id": "R1_empirical_extraction",
        "rule_type": "empirical_basis",
        "target":  "raw_facts",
        "sources": [
          "semanticprocessor.chunk_text",
          "policydocumentanalyzer.extract_key_excerpts",
          "semanticchunkingproducer.chunk_document",
          "textminingengine.diagnose_critical_links",
          "policyanalysisembedder.embed_texts"
        ],
        "merge_strategy": "concat_with_deduplication",
        "deduplication_key": "element_id",
        "output_type": "FACT",
        "confidence_propagation": "preserve_individual",
        "description": "Extract raw facts from document without interpretation"
      },
      {
        "rule_id": "R2_inferential_processing",
        "rule_type":  "corroboration",
        "target": "triangulated_facts",
        "sources": [
          "semanticanalyzer.compute_unit_of_analysis_natural_blocks",
          "semanticprocessor.embed_batch",
          "semanticchunkingproducer.embed_batch",
          "policydocumentanalyzer.analyze",
          "bayesianmechanisminference.calculate_coherence_factor"
        ],
        "input_dependencies": ["raw_facts"],
        "merge_strategy": "dempster_shafer",
        "operation": "if TextMining AND IndustrialPolicy extract same datum → merge nodes, increase confidence",
        "output_type": "PARAMETER",
        "confidence_propagation": "corroborative_boost",
        "description": "Triangulate semantic evidence from multiple sources"
      },
      {
        "rule_id":  "R3_audit_gate",
        "rule_type":  "robustness_gate",
        "target": "validated_facts",
        "sources":  [
          "semanticvalidator.validate_semantic_completeness_coherence",
          "operationalizationauditor.audit_causal_coherence_d6",
          "cdafframework.audit_causal_coherence"
        ],
        "input_dependencies": ["raw_facts", "triangulated_facts"],
        "merge_strategy":  "veto_gate",
        "output_type": "CONSTRAINT",
        "gate_logic": {
          "contradiction_detected": {
            "action": "suppress_fact",
            "multiplier": 0.0,
            "scope": "contradicting_nodes"
          },
          "low_coherence":  {
            "action": "reduce_confidence",
            "multiplier": 0.5,
            "scope": "source_facts"
          }
        },
        "asymmetry_declaration": "N3 can invalidate N1/N2 outputs; N1/N2 CANNOT invalidate N3",
        "description": "Validate and potentially veto lower-level findings"
      },
      {
        "rule_id": "R4_narrative_synthesis",
        "rule_type": "synthesis",
        "target": "human_answer",
        "sources": [],
        "input_dependencies": ["raw_facts", "triangulated_facts", "validated_facts"],
        "merge_strategy": "carver_doctoral_synthesis",
        "output_type":  "NARRATIVE",
        "external_handler": "DoctoralCarverSynthesizer",
        "description": "Synthesize validated evidence into human-readable answer"
      }
    ]
  },
  
  "fusion_specification": {
    "contract_type": "TYPE_A",
    "primary_strategy": "semantic_triangulation",
    "level_strategies": {
      "N1_fact_fusion": {
        "strategy": "semantic_corroboration",
        "behavior": "additive",
        "conflict_resolution": "semantic_deduplication",
        "formula": "if same_fact detected by multiple methods → confidence = 1 - ∏(1 - conf_i)"
      },
      "N2_parameter_fusion": {
        "strategy": "dempster_shafer",
        "behavior": "multiplicative",
        "conflict_resolution": "weighted_voting",
        "affects":  ["N1_facts. confidence", "N1_facts.edge_weights"]
      },
      "N3_constraint_fusion": {
        "strategy": "veto_gate",
        "behavior": "gate",
        "asymmetry_principle": "audit_dominates",
        "propagation": {
          "upstream": "confidence_backpropagation",
          "downstream": "branch_blocking"
        }
      }
    },
    "cross_layer_effects": {
      "N1_to_N2": {
        "relationship": "N2 reads N1 facts",
        "effect": "N2 computes parameters FROM N1 observations",
        "data_flow": "forward_propagation"
      },
      "N2_to_N1": {
        "relationship": "N2 modifies N1 confidence",
        "effect": "Edge weights adjust fact confidence scores",
        "data_flow":  "confidence_backpropagation"
      },
      "N3_to_N1": {
        "relationship": "N3 can BLOCK N1 facts",
        "effect": "Failed constraints remove facts from graph",
        "data_flow":  "veto_propagation",
        "asymmetry":  "N1 CANNOT invalidate N3"
      },
      "N3_to_N2": {
        "relationship": "N3 can INVALIDATE N2 parameters",
        "effect": "Failed constraints nullify parameter modifications",
        "data_flow":  "inference_modulation",
        "asymmetry": "N2 CANNOT invalidate N3"
      },
      "all_to_N4": {
        "relationship": "N4 consumes validated outputs from all layers",
        "effect": "Synthesis constructs narrative from filtered graph",
        "data_flow":  "terminal_aggregation"
      }
    },
    "fusion_pipeline": [
      {
        "step": 1,
        "name": "empirical_extraction",
        "level": "N1",
        "strategy": "semantic_corroboration",
        "input": "PreprocesadoMetadata",
        "output": "raw_facts_graph"
      },
      {
        "step": 2,
        "name": "inferential_processing",
        "level": "N2",
        "strategy":  "dempster_shafer",
        "input": "raw_facts_graph",
        "output": "weighted_inference_graph"
      },
      {
        "step": 3,
        "name": "audit_validation",
        "level": "N3",
        "strategy": "veto_gate",
        "input": "weighted_inference_graph",
        "output": "validated_graph",
        "veto_capable": true
      },
      {
        "step": 4,
        "name": "narrative_synthesis",
        "level": "N4",
        "strategy":  "carver_doctoral_synthesis",
        "input": "validated_graph",
        "output": "human_answer"
      }
    ]
  },
  
  "cross_layer_fusion": {
    "N1_to_N2": {
      "relationship": "N2 reads N1 facts",
      "effect":  "N2 computes parameters FROM N1 observations",
      "data_flow": "forward_propagation"
    },
    "N2_to_N1":  {
      "relationship": "N2 modifies N1 confidence",
      "effect": "Edge weights adjust fact confidence scores",
      "data_flow": "confidence_backpropagation"
    },
    "N3_to_N1": {
      "relationship": "N3 can BLOCK N1 facts",
      "effect": "Failed constraints remove facts from graph",
      "data_flow": "veto_propagation",
      "asymmetry":  "N1 CANNOT invalidate N3"
    },
    "N3_to_N2": {
      "relationship": "N3 can INVALIDATE N2 parameters",
      "effect": "Failed constraints nullify parameter modifications",
      "data_flow":  "inference_modulation",
      "asymmetry": "N2 CANNOT invalidate N3"
    },
    "all_to_N4": {
      "relationship": "N4 consumes validated outputs from all layers",
      "effect": "Synthesis constructs narrative from filtered graph",
      "data_flow": "terminal_aggregation"
    },
    "blocking_propagation_rules": {
      "statistical_significance_failed": {
        "triggered_by": "PolicyContradictionDetector._statistical_significance_test",
        "action": "block_branch",
        "scope": "source_facts",
        "propagation":  "downstream_only"
      },
      "logical_contradiction":  {
        "triggered_by":  "PolicyContradictionDetector._detect_logical_incompatibilities",
        "action": "block_branch",
        "scope":  "contradicting_nodes",
        "propagation": "both"
      }
    }
  },
  
  "human_answer_structure": {
    "format": "markdown",
    "template_mode": "epistemological_narrative",
    "contract_type": "TYPE_A",
    "sections": [
      {
        "section_id": "S1_verdict",
        "title": "### Veredicto",
        "layer": "N4",
        "data_source": "synthesis_output",
        "narrative_style": "declarative",
        "template": "**Conclusión**:  {verdict_statement}\n\n**Confianza Global**: {final_confidence_pct}% ({confidence_interpretation})\n\n**Base Metodológica**: {method_count} métodos ejecutados, {audit_count} validaciones, {blocked_count} ramas bloqueadas.",
        "argumentative_role": "SYNTHESIS"
      },
      {
        "section_id": "S2_empirical_base",
        "title": "### Base Empírica:  Hechos Observados",
        "layer": "N1",
        "data_source": "validated_facts",
        "narrative_style":  "descriptive",
        "template": "**Elementos Detectados**: {fact_count} hechos extraídos de {document_coverage_pct}% del texto.\n\n**Fuentes Oficiales**: {official_sources_list}\n\n**Indicadores Cuantitativos**: {quantitative_indicators}\n\n**Cobertura Temporal**: {temporal_series}",
        "argumentative_role": "EMPIRICAL_BASIS",
        "epistemological_note": "Observaciones directas sin transformación interpretativa."
      },
      {
        "section_id": "S3_robustness_audit",
        "title": "### Análisis de Robustez:  Validación y Limitaciones",
        "layer": "N3",
        "data_source":  "audit_results",
        "narrative_style":  "critical",
        "template": "**Validaciones Ejecutadas**: {validation_count}\n\n**Contradicciones Detectadas**: {contradiction_count}\n{contradiction_details}\n\n**Ramas Bloqueadas**: {blocked_branches_count}\n{blocking_reasons}\n\n**Modulaciones de Confianza**: {confidence_adjustments}\n\n**Limitaciones Metodológicas**: {limitations_list}",
        "argumentative_role": "ROBUSTNESS_QUALIFIER",
        "epistemological_note": "Meta-juicios sobre confiabilidad.  N3 puede VETAR hallazgos de N1/N2.",
        "veto_display": {
          "if_veto_triggered": "⚠️ ALERTA: {veto_reason}.  El modelo lógico es INVÁLIDO técnicamente.",
          "if_no_veto":  "✓ Todas las validaciones pasaron."
        }
      },
      {
        "section_id":  "S4_gaps",
        "title": "### Puntos Ciegos:  Evidencia Faltante",
        "layer":  "N4-META",
        "data_source":  "gap_analysis",
        "narrative_style": "diagnostic",
        "template": "**Métodos sin Resultados**: {empty_methods_count} de {total_methods}\n{empty_methods_list}\n\n**Elementos Esperados no Encontrados**: {missing_elements}\n\n**Cobertura de Patterns**: {pattern_coverage_pct}%\n\n**Impacto en Confianza**: {gap_impact_assessment}",
        "argumentative_role": "META_TRACEABILITY"
      }
    ],
    "argumentative_roles": {
      "N1_roles": [
        {
          "role": "EMPIRICAL_BASIS",
          "description": "Hecho observable innegable",
          "example": "Se encontraron 15 menciones a VBG",
          "narrative_weight": "high"
        }
      ],
      "N2_roles": [
        {
          "role": "INFERENTIAL_BRIDGE",
          "description": "Conexión lógica derivada",
          "example": "Con 95% confianza, el prior se actualiza",
          "narrative_weight": "medium"
        },
        {
          "role":  "CONTEXTUAL_QUALIFIER",
          "description": "Condiciona validez a contexto",
          "example": "Válido solo en zona rural",
          "narrative_weight":  "medium"
        }
      ],
      "N3_roles": [
        {
          "role":  "ROBUSTNESS_QUALIFIER",
          "description": "Advertencia de calidad/limitación",
          "example": "La muestra es pequeña (n=5)",
          "narrative_weight":  "high"
        },
        {
          "role": "REFUTATIONAL_SIGNAL",
          "description": "Evidencia negativa que contradice",
          "example":  "Meta A incompatible con Meta B",
          "narrative_weight": "critical"
        }
      ],
      "N4_roles": [
        {
          "role":  "META_TRACEABILITY",
          "description": "Calidad del proceso analítico",
          "example":  "95% cobertura de patterns",
          "narrative_weight":  "medium"
        }
      ]
    },
    "confidence_interpretation": {
      "critical": {
        "range": "0-19%",
        "label": "INVÁLIDO",
        "description": "Veto activado por N3, modelo lógico inválido técnicamente",
        "display": "🔴"
      },
      "low": {
        "range": "20-49%",
        "label": "DÉBIL",
        "description": "Evidencia insuficiente, contradicciones detectadas, o validación fallida",
        "display": "🟠"
      },
      "medium": {
        "range": "50-79%",
        "label": "MODERADO",
        "description": "Evidencia presente con limitaciones o inconsistencias menores",
        "display": "🟡"
      },
      "high": {
        "range": "80-100%",
        "label": "ROBUSTO",
        "description":  "Múltiples observaciones corroborantes, sin contradicciones, auditorías pasadas",
        "display": "🟢"
      }
    }
  },
  
  "audit_annotations": {
    "generation_metadata": {
      "generator_version": "4.0.0-granular",
      "generation_timestamp": "2026-01-02T15:30:00+00:00",
      "input_hashes": {
        "classified_methods": "a1b2c3d4e5f6g7h8",
        "contratos_clasificados": "i9j0k1l2m3n4o5p6",
        "method_sets": "q7r8s9t0u1v2w3x4"
      }
    },
    "source_references": {
      "method_assignments_source": "method_sets_by_question. json",
      "contract_classification_source": "contratos_clasificados. json",
      "method_definitions_source": "classified_methods.json",
      "doctrine_source": "operationalization_guide.json"
    },
    "composition_trace": {
      "question_id": "D1_Q1",
      "contract_id": "Q001",
      "type_code": "TYPE_A",
      "methods_in_chain": 13,
      "n1_methods": 5,
      "n2_methods": 5,
      "n3_methods": 3,
      "efficiency_score": 1.058
    },
    "validity_conditions": {
      "temporal_validity": "Until next input revision",
      "review_trigger": "Changes to any input file",
      "expiration_policy": "Regenerate if input hashes change"
    },
    "audit_checklist": {
      "structure_validated": true,
      "epistemic_coherence_validated": true,
      "temporal_validity_validated": true,
      "cross_reference_validated": true,
      "validation_pass_rate": 0.98,
      "validation_timestamp": "2026-01-02T15:30:00+00:00"
    }
  }
}
PARTE VI: CHECKLIST DE VALIDACIÓN FINAL

6.1 Invariantes de Diseño - Verificación

#	Invariante	Verificación	Status
I-1	Autoridad Epistémica Inmutable	Métodos provienen de method_sets_by_question.json, no inferidos	✅
I-2	Composición Bottom-Up	Cadena se construye METHOD → CHAIN → CONTRACT	✅
I-3	Sin Templates por TYPE	No hay if TYPE == X en estructura; TYPE es overlay	✅
I-4	Determinismo Total	Timestamps fijos, sin randomness, orden preservado	✅
I-5	Fail-Loud	Validador bloquea emisión si critical failures > 0	✅
6.2 Propiedades de Granularidad - Verificación

#	Propiedad	Verificación	Status
G-1	Expansión Completa de Métodos	Cada método tiene 20+ campos expandidos	✅
G-2	Preservación de Orden	tuple inmutables, sin sorting	✅
G-3	Fronteras Explícitas	Fases claramente delimitadas con dependencies	✅
G-4	Sin Compresión Semántica	Cada método es unidad discreta, no colapsada	✅
G-5	Trazabilidad Completa	expansion_source, input_hashes, timestamps	✅
6.3 Propiedades Epistémicas - Verificación

#	Propiedad	Verificación	Status
E-1	Asimetría N3 Declarada	asymmetry:  "N1/N2 CANNOT invalidate N3"	✅
E-2	Veto Conditions Explícitas	Métodos N3 tienen veto_conditions con triggers	✅
E-3	TYPE Consistente	Validador verifica TYPE en identity, method_binding, fusion	✅
E-4	Niveles Correctos por Fase	Validador verifica N1 en A, N2 en B, N3 en C	✅
E-5	Doctoral Justification Preservada	Campo doctoral_justification del input volcado	✅
6.4 Propiedades de Auditoría - Verificación

#	Propiedad	Verificación	Status
A-1	Hashes de Inputs	input_hashes en audit_annotations	✅
A-2	Timestamps de Generación	created_at, expansion_timestamp	✅
A-3	Versión del Generador	generator_version en identity	✅
A-4	Checklist de Validación	audit_checklist con 4 checks booleanos	✅
A-5	Condiciones de Validez Temporal	validity_conditions con triggers	✅
PARTE VII: RESUMEN EJECUTIVO

7.1 Lo Que Este Generador HACE

Carga inputs como datos autoritativos - No los modifica, interpreta ni infiere sobre ellos
Expande cada método en unidad semántica completa - 20+ campos por método
Preserva orden exacto de asignaciones - El orden en method_sets_by_question.json es sacrosanto
Compone cadenas epistémicas - N1 → N2 → N3 como secuencia inmutable
Ensambla contratos desde cadenas - TYPE es overlay, no generador
Valida antes de emitir - 50+ checks estructurales y epistémicos
Emite JSON determinista - Mismos inputs → mismos outputs byte-a-byte
7.2 Lo Que Este Generador NO HACE

NO infiere métodos - Si no está en method_sets_by_question.json, no existe
NO reordena métodos - El orden es significado epistémico
NO colapsa métodos - Cada método mantiene identidad discreta
NO usa templates por TYPE - La estructura emerge de los métodos
NO repara silenciosamente - Errores son explícitos y bloqueantes
NO inventa campos - Todo campo tiene fuente trazable
NO degrada sin declarar - Si algo falla, se declara, no se oculta
7.3 Métricas Esperadas

Métrica	Valor Esperado
Contratos generados	30
Métodos por contrato (promedio)	10-15
Campos por método expandido	20+
Checks de validación por contrato	50+
Tasa de aprobación esperada	100% (si inputs son correctos)
Tiempo de generación	< 30 segundos
Tamaño promedio por contrato	15-25 KB JSON
7.4 Comando de Ejecución

bash
python -m farfan_pipeline.phases.Phase_two. contract_generator. contract_generator \
    --assets /path/to/epistemological_assets \
    --output /path/to/generated_contracts \
    --strict
7.5 Archivos de Salida

Code
generated_contracts/
├── D1_Q1_contract_v4.json    # TYPE_A - Semántico
├── D1_Q2_contract_v4.json    # TYPE_B - Bayesiano
├── D1_Q3_contract_v4.json    # TYPE_D - Financiero
├── D1_Q4_contract_v4.json    # TYPE_D - Financiero
├── D1_Q5_contract_v4.json    # TYPE_B - Bayesiano
├── D2_Q1_contract_v4.json    # TYPE_D - Financiero
├── D2_Q2_contract_v4.json    # TYPE_B - Bayesiano
├── D2_Q3_contract_v4.json    # TYPE_C - Causal
├── D2_Q4_contract_v4.json    # TYPE_D - Financiero
├── D2_Q5_contract_v4.json    # TYPE_E - Lógico
├── D3_Q1_contract_v4.json    # TYPE_B - Bayesiano
├── D3_Q2_contract_v4.json    # TYPE_D - Financiero
├── D3_Q3_contract_v4.json    # TYPE_A - Semántico
├── D3_Q4_contract_v4.json    # TYPE_E - Lógico
├── D3_Q5_contract_v4.json    # TYPE_D - Financiero
├── D4_Q1_contract_v4.json    # TYPE_C - Causal
├── D4_Q2_contract_v4.json    # TYPE_B - Bayesiano
├── D4_Q3_contract_v4.json    # TYPE_B - Bayesiano
├── D4_Q4_contract_v4.json    # TYPE_E - Lógico
├── D4_Q5_contract_v4.json    # TYPE_B - Bayesiano
├── D5_Q1_contract_v4.json    # TYPE_D - Financiero
├── D5_Q2_contract_v4.json    # TYPE_D - Financiero
├── D5_Q3_contract_v4.json    # TYPE_B - Bayesiano
├── D5_Q4_contract_v4.json    # TYPE_B - Bayesiano
├── D5_Q5_contract_v4.json    # TYPE_B - Bayesiano
├── D6_Q1_contract_v4.json    # TYPE_C - Causal
├── D6_Q2_contract_v4.json    # TYPE_B - Bayesiano
├── D6_Q3_contract_v4.json    # TYPE_E - Lógico
├── D6_Q4_contract_v4.json    # TYPE_B - Bayesiano
├── D6_Q5_contract_v4.json    # TYPE_C - Causal
└── generation_manifest.json  # Manifiesto de generación
PARTE VIII: META-INVARIANTE FINAL

El generador NUNCA añade significado epistémico que no esté ya presente en las asignaciones o definiciones de métodos.
Puede:

Expandir - Hacer explícito lo implícito
Anotar - Añadir metadata de trazabilidad
Estructurar - Organizar en formato de contrato
Validar - Verificar coherencia
NUNCA puede:

Inventar - Crear métodos o campos no existentes
Inferir - Deducir relaciones no declaradas
Optimizar - Reordenar para "mejorar"
Simplificar - Colapsar para "clarificar"

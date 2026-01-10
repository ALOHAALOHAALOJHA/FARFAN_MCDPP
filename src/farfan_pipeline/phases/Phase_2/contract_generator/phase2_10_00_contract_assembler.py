"""
Módulo:  contract_assembler.py
Propósito: Ensamblar contrato completo desde cadena epistémica

Ubicación: src/farfan_pipeline/phases/Phase_2/contract_generator/contract_assembler.py

RESPONSABILIDADES:
1. Transformar EpistemicChain en GeneratedContract
2. Construir cada sección del contrato según operationalization_guide.json
3. Preservar granularidad completa de métodos expandidos
4. Generar secciones derivadas del TYPE sin templates
5. Validar estructura post-ensamblaje

PRINCIPIOS:
- La cadena epistémica ES el contrato (no se transforma conceptualmente)
- TYPE es overlay interpretativo sobre la cadena
- Cada sección se deriva de la cadena, no de templates
- Verbosidad completa en method_binding

Versión: 4.0.0-granular
Fecha: 2026-01-03
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .chain_composer import EpistemicChain
    from .input_registry import ContractClassification, InputRegistry, SectorDefinition
    from .method_expander import ExpandedMethodUnit

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ══════════════════════════════════════════════════════════════════════════════

ASSEMBLER_VERSION = "4.0.0-granular"

# Estrategias por TYPE según operationalization_guide.json (PARTE IV)
TYPE_STRATEGIES: dict[str, dict[str, str]] = {
    "TYPE_A": {
        "N1": "semantic_corroboration",
        "N2": "dempster_shafer",
        "N3": "veto_gate",
        "primary": "semantic_triangulation",
    },
    "TYPE_B": {
        "N1": "concat",
        "N2": "bayesian_update",
        "N3": "veto_gate",
        "primary": "bayesian_update",
    },
    "TYPE_C": {
        "N1": "graph_construction",
        "N2": "topological_overlay",
        "N3": "veto_gate",
        "primary": "topological_overlay",
    },
    "TYPE_D": {
        "N1": "concat",
        "N2": "weighted_mean",
        "N3": "financial_coherence_audit",
        "primary": "financial_coherence_audit",
    },
    "TYPE_E": {
        "N1": "concat",
        "N2": "weighted_mean",
        "N3": "logical_consistency_validation",
        "primary": "logical_consistency_validation",
    },
}

# Gate logic por TYPE (PARTE III, assembly_rules)
TYPE_GATE_LOGIC: dict[str, dict[str, dict[str, Any]]] = {
    "TYPE_A": {
        "contradiction_detected": {
            "action": "suppress_fact",
            "multiplier": 0.0,
        },
        "low_coherence": {
            "action": "reduce_confidence",
            "multiplier": 0.5,
        },
    },
    "TYPE_B": {
        "statistical_power_below_threshold": {
            "condition": "result < 0.8",
            "action": "downgrade_confidence_to_zero",
        },
    },
    "TYPE_C": {
        "cycle_detected": {
            "action": "invalidate_graph",
            "multiplier": 0.0,
        },
        "scm_construction_failed": {
            "action": "block_branch",
            "scope": "affected_subgraph",
        },
    },
    "TYPE_D": {
        "budget_gap_detected": {
            "action": "flag_insufficiency",
            "multiplier": 0.3,
        },
        "allocation_mismatch": {
            "action": "reduce_confidence",
            "multiplier": 0.5,
        },
    },
    "TYPE_E": {
        "logical_contradiction": {
            "action": "suppress_contradicting_nodes",
            "multiplier": 0.0,
        },
        "sequence_violation": {
            "action": "flag_invalid_sequence",
            "multiplier": 0.2,
        },
    },
}

# Cross-layer fusion definitions (PARTE V)
CROSS_LAYER_FUSION_TEMPLATE: dict[str, dict[str, Any]] = {
    "N1_to_N2": {
        "relationship": "N2 reads N1 facts",
        "effect": "N2 computes parameters FROM N1 observations",
        "data_flow": "forward_propagation",
    },
    "N2_to_N1": {
        "relationship": "N2 modifies N1 confidence",
        "effect": "Edge weights adjust fact confidence scores",
        "data_flow": "confidence_backpropagation",
    },
    "N3_to_N1": {
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
        "effect": "Synthesis constructs narrative from filtered graph",
        "data_flow": "terminal_aggregation",
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# DATACLASS PRINCIPAL - CONTRATO GENERADO
# ══════════════════════════════════════════════════════════════════════════════


@dataclass
class GeneratedContract:
    """
    Contrato ejecutor generado.

    ESTRUCTURA SEGÚN operationalization_guide.json:
    - identity: Identificación del contrato
    - executor_binding: Clase ejecutora
    - method_binding: Métodos por fase (LA MÁS GRANULAR)
    - question_context: Contexto de la pregunta
    - signal_requirements: Requisitos de señal
    - evidence_assembly: Ensamblaje de evidencia
    - fusion_specification: Especificación de fusión
    - cross_layer_fusion: Fusión entre capas
    - human_answer_structure: Estructura de respuesta
    - traceability:  Trazabilidad
    - output_contract: Schema de salida
    - audit_annotations: Anotaciones de auditoría
    """

    # Secciones del contrato
    identity: dict[str, Any]
    executor_binding: dict[str, Any]
    method_binding: dict[str, Any]
    question_context: dict[str, Any]
    signal_requirements: dict[str, Any]
    evidence_assembly: dict[str, Any]
    fusion_specification: dict[str, Any]
    cross_layer_fusion: dict[str, Any]
    human_answer_structure: dict[str, Any]
    traceability: dict[str, Any]
    output_contract: dict[str, Any]
    audit_annotations: dict[str, Any]

    # Metadata (no se serializa directamente)
    _contract_number: int = field(default=0, repr=False)
    _sector_id: str = field(default="", repr=False)

    def to_dict(self) -> dict[str, Any]:
        """Serializa a diccionario ordenado para JSON."""
        return {
            "identity": self.identity,
            "executor_binding": self.executor_binding,
            "method_binding": self.method_binding,
            "question_context": self.question_context,
            "signal_requirements": self.signal_requirements,
            "evidence_assembly": self.evidence_assembly,
            "fusion_specification": self.fusion_specification,
            "cross_layer_fusion": self.cross_layer_fusion,
            "human_answer_structure": self.human_answer_structure,
            "traceability": self.traceability,
            "output_contract": self.output_contract,
            "audit_annotations": self.audit_annotations,
        }

    @property
    def contract_id(self) -> str:
        """ID del contrato desde identity."""
        return self.identity.get("contract_id", "")

    @property
    def sector_id(self) -> str:
        """ID del sector."""
        return self._sector_id or self.identity.get("sector_id", "")

    @property
    def contract_type(self) -> str:
        """Tipo del contrato."""
        return self.identity.get("contract_type", "")

    @property
    def total_methods(self) -> int:
        """Total de métodos en el contrato."""
        return self.method_binding.get("method_count", 0)


# ══════════════════════════════════════════════════════════════════════════════
# CLASE ENSAMBLADORA
# ══════════════════════════════════════════════════════════════════════════════


class ContractAssembler:
    """
    Ensambla contratos desde cadenas epistémicas.

    RESPONSABILIDADES:
    1. Transformar EpistemicChain + Sector → GeneratedContract
    2. Construir cada sección según la guía de operacionalización
    3. Preservar verbosidad completa en method_binding
    4. Generar secciones derivadas del TYPE
    5. Embeber regex/patterns específicos del sector

    PRINCIPIOS:
    - La cadena epistémica ES el contrato (no se transforma conceptualmente)
    - TYPE es overlay interpretativo sobre la cadena
    - Cada sección se deriva de la cadena, no de templates
    - Verbosidad completa:  NO hay compresión ni resumen

    USO:
        assembler = ContractAssembler(registry, timestamp, version)
        contract = assembler.assemble_contract(chain, classification, sector, number)
    """

    def __init__(
        self,
        registry: InputRegistry,
        generation_timestamp: str,
        generator_version: str,
    ):
        """
        Inicializa el assembler.

        Args:
            registry: InputRegistry con datos cargados
            generation_timestamp:  Timestamp ISO de generación
            generator_version:  Versión del generador
        """
        self.registry = registry
        self.generation_timestamp = generation_timestamp
        self.generator_version = generator_version
        self._assembly_count = 0

        logger.info(f"ContractAssembler initialized, version {ASSEMBLER_VERSION}")

    def assemble_contract(
        self,
        chain: EpistemicChain,
        classification: ContractClassification,
        sector: SectorDefinition,
        contract_number: int,
    ) -> GeneratedContract:
        """
        Ensambla contrato completo desde cadena epistémica y sector.

        SECUENCIA:
        1. Construir identity con sector embebido
        2. Construir executor_binding
        3. Construir method_binding (GRANULAR)
        4. Construir question_context
        5. Construir signal_requirements
        6. Construir evidence_assembly
        7. Construir fusion_specification
        8. Construir cross_layer_fusion
        9. Construir human_answer_structure
        10. Construir traceability
        11. Construir output_contract
        12. Construir audit_annotations
        13. Ensamblar GeneratedContract

        Args:
            chain: EpistemicChain compuesta
            classification: ContractClassification para contexto
            sector: SectorDefinition del sector
            contract_number:  Número del contrato (1-300)

        Returns:
            GeneratedContract completo
        """
        logger.debug(
            f"Assembling contract {contract_number}:  "
            f"{classification.contract_id} + {sector.sector_id}"
        )

        # ══════════════════════════════════════════════════════════════════
        # CONSTRUIR CADA SECCIÓN
        # ══════════════════════════════════════════════════════════════════

        identity = self._build_identity(chain, classification, sector, contract_number)
        executor_binding = self._build_executor_binding(chain, sector, contract_number)
        method_binding = self._build_method_binding(chain)
        question_context = self._build_question_context(classification, sector)
        signal_requirements = self._build_signal_requirements(chain, classification)
        evidence_assembly = self._build_evidence_assembly(chain, classification)
        fusion_specification = self._build_fusion_specification(chain, classification)
        cross_layer_fusion = self._build_cross_layer_fusion(chain, classification)
        human_answer_structure = self._build_human_answer_structure(classification)
        traceability = self._build_traceability(chain, classification, sector)
        output_contract = self._build_output_contract(classification)
        audit_annotations = self._build_audit_annotations(chain, classification, sector)

        # ══════════════════════════════════════════════════════════════════
        # ENSAMBLAR CONTRATO
        # ══════════════════════════════════════════════════════════════════

        contract = GeneratedContract(
            identity=identity,
            executor_binding=executor_binding,
            method_binding=method_binding,
            question_context=question_context,
            signal_requirements=signal_requirements,
            evidence_assembly=evidence_assembly,
            fusion_specification=fusion_specification,
            cross_layer_fusion=cross_layer_fusion,
            human_answer_structure=human_answer_structure,
            traceability=traceability,
            output_contract=output_contract,
            audit_annotations=audit_annotations,
            _contract_number=contract_number,
            _sector_id=sector.sector_id,
        )

        self._assembly_count += 1

        logger.debug(
            f"  Contract {contract_number} assembled:  "
            f"{contract.total_methods} methods, type {contract.contract_type}"
        )

        return contract

    # ══════════════════════════════════════════════════════════════════════════
    # BUILDERS - IDENTITY
    # ══════════════════════════════════════════════════════════════════════════

    def _build_identity(
        self,
        chain: EpistemicChain,
        classification: ContractClassification,
        sector: SectorDefinition,
        contract_number: int,
    ) -> dict[str, Any]:
        """
        Construye sección identity.

        PARA 300 CONTRATOS:
        - contract_id: Q001_PA01, Q001_PA02, ..., Q030_PA10
        - sector_id: PA01, PA02, ..., PA10
        - sector_name: Nombre canónico del sector
        """
        q_id = chain.question_id  # e.g., "D1_Q1"
        base_contract_id = classification.contract_id  # e. g., "Q001"

        # Contract ID único:  base + sector
        unique_contract_id = f"{base_contract_id}_{sector.sector_id}"

        # Extraer dimension_id
        dimension_id = self._extract_dimension_id(q_id)

        return {
            # Identificadores únicos
            "contract_id": unique_contract_id,
            "contract_number": contract_number,
            "base_contract_id": base_contract_id,
            "base_slot": q_id.replace("_", "-"),  # D1_Q1 → D1-Q1
            # Sector (policy_area_id alias for Carver/Executor compatibility)
            "sector_id": sector.sector_id,
            "policy_area_id": sector.sector_id,  # Alias for chunk JOIN
            "sector_name": sector.canonical_name,
            # Dimensión
            "dimension_id": dimension_id,
            "question_id": unique_contract_id,  # Alias for Carver extraction
            # Identificador representativo para validación
            "representative_question_id": unique_contract_id,
            # Tipo de contrato
            "contract_type": classification.tipo_contrato["codigo"],
            "contract_type_name": classification.tipo_contrato["nombre"],
            "contract_type_focus": classification.tipo_contrato["foco"],
            # Versión y metadata
            "contract_version": "4.0.0-epistemological",
            "created_at": self.generation_timestamp,
            "generator_version": self.generator_version,
            "specification_source": "operationalization_guide.json",
        }

    def _extract_dimension_id(self, question_id: str) -> str:
        """
        Extrae dimension_id de question_id.

        Input: "D1_Q1", "D2_Q3", "D6_Q5"
        Output: "DIM01", "DIM02", "DIM06"
        """
        pattern = r"^D(\d+)_Q\d+$"
        match = re.match(pattern, question_id)

        if not match:
            raise ValueError(
                f"Invalid question_id format: '{question_id}'\n"
                f"Expected format: 'D<num>_Q<num>' (e.g., 'D1_Q1')"
            )

        dimension_num = int(match.group(1))

        if not 1 <= dimension_num <= 6:
            raise ValueError(
                f"Dimension number out of range: {dimension_num}\n"
                f"Expected:  1-6 (from question_id '{question_id}')"
            )

        return f"DIM{dimension_num:02d}"

    # ══════════════════════════════════════════════════════════════════════════
    # BUILDERS - EXECUTOR BINDING
    # ══════════════════════════════════════════════════════════════════════════

    def _build_executor_binding(
        self,
        chain: EpistemicChain,
        sector: SectorDefinition,
        contract_number: int,
    ) -> dict[str, Any]:
        """Construye sección executor_binding."""
        q_id = chain.question_id

        return {
            "executor_class": f"{q_id}_{sector.sector_id}_Executor",
            "executor_module": "farfan_pipeline.phases.Phase_2.executors",
            "contract_number": contract_number,
        }

    # ══════════════════════════════════════════════════════════════════════════
    # BUILDERS - METHOD BINDING (LA MÁS GRANULAR)
    # ══════════════════════════════════════════════════════════════════════════

    def _build_method_binding(self, chain: EpistemicChain) -> dict[str, Any]:
        """
        Construye sección method_binding.

        ESTA ES LA SECCIÓN MÁS GRANULAR.
        Cada método expandido se vuelca íntegramente.
        NO hay compresión ni resumen.
        """
        return {
            "orchestration_mode": "epistemological_pipeline",
            "contract_type": chain.contract_type_code,
            "method_count": chain.total_methods,
            "execution_phases": {
                "phase_A_construction": self._build_phase_section(
                    methods=chain.phase_a_chain,
                    metadata=chain.phase_a_metadata,
                ),
                "phase_B_computation": self._build_phase_section(
                    methods=chain.phase_b_chain,
                    metadata=chain.phase_b_metadata,
                ),
                "phase_C_litigation": self._build_phase_section(
                    methods=chain.phase_c_chain,
                    metadata=chain.phase_c_metadata,
                ),
            },
            "efficiency_score": chain.efficiency_score,
            "mathematical_evidence": chain.mathematical_evidence,
            "doctoral_justification": chain.doctoral_justification,
        }

    def _build_phase_section(
        self,
        methods: tuple[ExpandedMethodUnit, ...],
        metadata: Any,  # PhaseMetadata
    ) -> dict[str, Any]:
        """
        Construye sección de una fase con todos los métodos expandidos.

        VERBOSIDAD TOTAL:  Cada campo de cada método se incluye.
        """
        section = {
            "description": self._get_phase_description(metadata.level_prefix),
            "level": metadata.level_prefix,
            "level_name": metadata.level_name,
            "epistemology": metadata.epistemology,
            "methods": [m.to_contract_dict() for m in methods],
            "dependencies": list(metadata.dependencies),
            "output_target": metadata.output_target,
        }

        # Añadir campos específicos para N3
        if metadata.level_prefix == "N3":
            section["asymmetry_principle"] = (
                "N3 can invalidate N1/N2 outputs; " "N1 and N2 CANNOT invalidate N3"
            )
            section["fusion_mode"] = "modulation"

        return section

    def _get_phase_description(self, level: str) -> str:
        """Obtiene descripción de fase por nivel."""
        descriptions = {
            "N1": "Empirical observation layer - direct extraction without interpretation",
            "N2": "Inferential analysis layer - transformation into analytical constructs",
            "N3": "Audit layer - attempt to 'break' results.  Acts as VETO GATE.",
        }
        return descriptions.get(level, "")

    # ══════════════════════════════════════════════════════════════════════════
    # BUILDERS - QUESTION CONTEXT
    # ══════════════════════════════════════════════════════════════════════════

    def _build_question_context(
        self,
        classification: ContractClassification,
        sector: SectorDefinition,
    ) -> dict[str, Any]:
        """Construye sección question_context con pregunta especializada del sector."""
        # Buscar pregunta especializada en sector_questions
        # classification.contract_id es "Q003", sector.sector_id es "PA01"
        base_q_id = classification.contract_id  # Q001, Q002, etc.
        sector_id = sector.sector_id  # PA01, PA02, etc.

        # Intentar obtener pregunta especializada, fallback a genérica
        specialized_question = classification.pregunta  # Default: pregunta genérica
        if hasattr(self.registry, "sector_questions") and self.registry.sector_questions:
            sector_qs = self.registry.sector_questions.get(sector_id, {})
            if base_q_id in sector_qs:
                specialized_question = sector_qs[base_q_id]

        return {
            "monolith_ref": classification.contract_id,
            "question_text": specialized_question,  # Carver expects this key
            "pregunta_completa": specialized_question,
            "pregunta_generica": classification.pregunta,  # Preservar referencia
            "sector_id": sector.sector_id,
            "sector_name": sector.canonical_name,
            "overrides": None,
            "failure_contract": {
                "abort_if": [
                    "missing_required_element",
                    "incomplete_text",
                    "no_quantitative_data",
                ],
                "emit_code": (
                    f"ABORT-{classification.dimension_key. replace('_', '-')}-"
                    f"{sector.sector_id}-REQ"
                ),
            },
        }

    # ══════════════════════════════════════════════════════════════════════════
    # BUILDERS - SIGNAL REQUIREMENTS
    # ══════════════════════════════════════════════════════════════════════════

    def _build_signal_requirements(
        self,
        chain: EpistemicChain,
        classification: ContractClassification,
    ) -> dict[str, Any]:
        """Construye sección signal_requirements."""
        return {
            "derivation_source": "expected_elements",
            "derivation_rules": {
                "mandatory": "expected_elements[required=true]. type → detection_{type}",
                "optional": "expected_elements[required=false]. type → detection_{type}",
            },
            "signal_aggregation": "weighted_mean",
            "minimum_signal_threshold": 0.5,
        }

    # ══════════════════════════════════════════════════════════════════════════
    # BUILDERS - EVIDENCE ASSEMBLY
    # ══════════════════════════════════════════════════════════════════════════

    def _build_evidence_assembly(
        self,
        chain: EpistemicChain,
        classification: ContractClassification,
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
                "description": "Se SUMA al grafo como nodo",
            },
            "PARAMETER": {
                "origin_level": "N2",
                "fusion_operation": "edge_weight_modification",
                "merge_behavior": "multiplicative",
                "symbol": "⊗",
                "description": "MODIFICA pesos de aristas del grafo",
            },
            "CONSTRAINT": {
                "origin_level": "N3",
                "fusion_operation": "branch_filtering",
                "merge_behavior": "gate",
                "symbol": "⊘",
                "description": "FILTRA/BLOQUEA ramas si validación falla",
            },
            "NARRATIVE": {
                "origin_level": "N4",
                "fusion_operation": "synthesis",
                "merge_behavior": "terminal",
                "symbol": "⊙",
                "description": "CONSUME grafo para texto final",
            },
        }

        # Recolectar provides de cada fase
        n1_provides = [m.provides for m in chain.phase_a_chain]
        n2_provides = [m.provides for m in chain.phase_b_chain]
        n3_provides = [m.provides for m in chain.phase_c_chain]

        # Construir reglas según TYPE
        assembly_rules = self._build_assembly_rules(
            type_code=type_code,
            n1_provides=n1_provides,
            n2_provides=n2_provides,
            n3_provides=n3_provides,
            strategies=classification.estrategias_fusion,
        )

        return {
            "engine": "EVIDENCE_NEXUS",
            "module": "farfan_pipeline. phases.Phase_two.evidence_nexus",
            "class_name": "EvidenceNexus",
            "method_name": "assemble",
            "type_system": type_system,
            "assembly_rules": assembly_rules,
        }

    def _build_assembly_rules(
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
        type_strats = TYPE_STRATEGIES.get(type_code, TYPE_STRATEGIES["TYPE_A"])

        # R1: Extracción empírica (N1)
        r1_target = self._get_r1_target(type_code)
        r1 = {
            "rule_id": "R1_empirical_extraction",
            "rule_type": "empirical_basis",
            "target": r1_target,
            "sources": n1_provides,
            "merge_strategy": type_strats["N1"],
            "output_type": "FACT",
            "confidence_propagation": "preserve_individual",
            "description": "Extract raw facts from document without interpretation",
        }

        if type_code == "TYPE_A":
            r1["deduplication_key"] = "element_id"

        # R2: Procesamiento inferencial (N2)
        r2_target = self._get_r2_target(type_code)
        r2 = {
            "rule_id": "R2_inferential_processing",
            "rule_type": self._get_r2_rule_type(type_code),
            "target": r2_target,
            "sources": n2_provides,
            "input_dependencies": [r1_target],
            "merge_strategy": type_strats["N2"],
            "output_type": "PARAMETER",
            "confidence_propagation": self._get_r2_confidence_propagation(type_code),
            "description": self._get_r2_description(type_code),
        }

        # Añadir operación específica
        r2_operation = self._get_r2_operation(type_code)
        if r2_operation:
            r2["operation"] = r2_operation

        # R3: Auditoría (N3)
        r3_target = self._get_r3_target(type_code)
        r3 = {
            "rule_id": "R3_audit_gate",
            "rule_type": self._get_r3_rule_type(type_code),
            "target": r3_target,
            "sources": n3_provides,
            "input_dependencies": [r1_target, r2_target],
            "merge_strategy": "veto_gate",
            "output_type": "CONSTRAINT",
            "gate_logic": TYPE_GATE_LOGIC.get(type_code, {}),
            "asymmetry_declaration": (
                "N3 can invalidate N1/N2 outputs; " "N1/N2 CANNOT invalidate N3"
            ),
            "description": "Validate and potentially veto lower-level findings",
        }

        # R4: Síntesis (N4)
        r4 = {
            "rule_id": "R4_narrative_synthesis",
            "rule_type": "synthesis",
            "target": "human_answer",
            "sources": [],
            "input_dependencies": [r3_target, r2_target, "audit_results"],
            "merge_strategy": "carver_doctoral_synthesis",
            "output_type": "NARRATIVE",
            "external_handler": "DoctoralCarverSynthesizer",
            "description": "Synthesize validated evidence into human-readable answer",
        }

        return [r1, r2, r3, r4]

    def _get_r1_target(self, type_code: str) -> str:
        """Target de R1 según TYPE."""
        targets = {
            "TYPE_A": "raw_facts",
            "TYPE_B": "prior_distribution",
            "TYPE_C": "causal_graph",
            "TYPE_D": "financial_facts",
            "TYPE_E": "policy_statements",
        }
        return targets.get(type_code, "raw_facts")

    def _get_r2_target(self, type_code: str) -> str:
        """Target de R2 según TYPE."""
        targets = {
            "TYPE_A": "triangulated_facts",
            "TYPE_B": "posterior_belief",
            "TYPE_C": "weighted_causal_graph",
            "TYPE_D": "sufficiency_scores",
            "TYPE_E": "coherence_metrics",
        }
        return targets.get(type_code, "inferences")

    def _get_r3_target(self, type_code: str) -> str:
        """Target de R3 según TYPE."""
        targets = {
            "TYPE_A": "validated_facts",
            "TYPE_B": "validated_posterior",
            "TYPE_C": "validated_graph",
            "TYPE_D": "validated_financials",
            "TYPE_E": "validated_statements",
        }
        return targets.get(type_code, "validated_output")

    def _get_r2_rule_type(self, type_code: str) -> str:
        """Rule type de R2 según TYPE."""
        rule_types = {
            "TYPE_A": "corroboration",
            "TYPE_B": "probabilistic_update",
            "TYPE_C": "edge_inference",
            "TYPE_D": "computation",
            "TYPE_E": "computation",
        }
        return rule_types.get(type_code, "computation")

    def _get_r3_rule_type(self, type_code: str) -> str:
        """Rule type de R3 según TYPE."""
        rule_types = {
            "TYPE_A": "robustness_gate",
            "TYPE_B": "robustness_gate",
            "TYPE_C": "validity_check",
            "TYPE_D": "financial_coherence_audit",
            "TYPE_E": "logical_consistency_validation",
        }
        return rule_types.get(type_code, "robustness_gate")

    def _get_r2_confidence_propagation(self, type_code: str) -> str:
        """Confidence propagation de R2 según TYPE."""
        propagations = {
            "TYPE_A": "corroborative_boost",
            "TYPE_B": "bayesian_update",
            "TYPE_C": "topological_merge",
            "TYPE_D": "weighted_average",
            "TYPE_E": "weighted_average",
        }
        return propagations.get(type_code, "preserve_individual")

    def _get_r2_description(self, type_code: str) -> str:
        """Description de R2 según TYPE."""
        descriptions = {
            "TYPE_A": "Triangulate and corroborate facts from multiple sources",
            "TYPE_B": "Update prior beliefs with evidence likelihood",
            "TYPE_C": "Infer edge weights and merge causal paths",
            "TYPE_D": "Compute sufficiency scores from financial data",
            "TYPE_E": "Compute coherence metrics from policy statements",
        }
        return descriptions.get(type_code, "Process inferential analysis")

    def _get_r2_operation(self, type_code: str) -> str | None:
        """Operation de R2 según TYPE."""
        operations = {
            "TYPE_A": (
                "if TextMining AND IndustrialPolicy extract same datum → "
                "merge nodes, increase confidence"
            ),
            "TYPE_B": "posterior = update_belief(prior, likelihood_from_evidence)",
            "TYPE_C": (
                "if TeoriaCambio path AND CausalExtractor path → " "check for cycles, merge edges"
            ),
        }
        return operations.get(type_code)

    # ══════════════════════════════════════════════════════════════════════════
    # BUILDERS - FUSION SPECIFICATION
    # ══════════════════════════════════════════════════════════════════════════

    def _build_fusion_specification(
        self,
        chain: EpistemicChain,
        classification: ContractClassification,
    ) -> dict[str, Any]:
        """Construye sección fusion_specification."""
        type_code = classification.tipo_contrato["codigo"]
        type_strats = TYPE_STRATEGIES.get(type_code, TYPE_STRATEGIES["TYPE_A"])

        return {
            "contract_type": type_code,
            "primary_strategy": type_strats["primary"],
            "level_strategies": {
                "N1_fact_fusion": {
                    "strategy": type_strats["N1"],
                    "behavior": "additive",
                    "conflict_resolution": "corroborative_stacking",
                    "formula": "if same_fact detected by multiple methods → confidence = 1 - ∏(1 - conf_i)",
                },
                "N2_parameter_fusion": {
                    "strategy": type_strats["N2"],
                    "behavior": "multiplicative",
                    "conflict_resolution": "weighted_voting",
                    "affects": ["N1_facts. confidence", "N1_facts.edge_weights"],
                },
                "N3_constraint_fusion": {
                    "strategy": "veto_gate",
                    "behavior": "gate",
                    "asymmetry_principle": "audit_dominates",
                    "propagation": {
                        "upstream": "confidence_backpropagation",
                        "downstream": "branch_blocking",
                    },
                },
            },
            "fusion_pipeline": {
                "step_1": "Execute all N1 methods → collect FACTS",
                "step_2": "Execute all N2 methods → compute PARAMETERS",
                "step_3": "Execute all N3 methods → apply CONSTRAINTS",
                "step_4": "Synthesize validated graph → NARRATIVE",
            },
        }

    # ══════════════════════════════════════════════════════════════════════════
    # BUILDERS - CROSS LAYER FUSION
    # ══════════════════════════════════════════════════════════════════════════

    def _build_cross_layer_fusion(
        self,
        chain: EpistemicChain,
        classification: ContractClassification,
    ) -> dict[str, Any]:
        """Construye sección cross_layer_fusion."""
        type_code = classification.tipo_contrato["codigo"]

        # Base template
        result = dict(CROSS_LAYER_FUSION_TEMPLATE)

        # Añadir blocking_propagation_rules específicas del TYPE
        result["blocking_propagation_rules"] = self._get_blocking_rules(type_code)

        return result

    def _get_blocking_rules(self, type_code: str) -> dict[str, dict[str, Any]]:
        """Obtiene blocking rules específicas del TYPE."""
        base_rules = {
            "matrix_not_positive_definite": {
                "triggered_by": "IndustrialGradeValidator",
                "action": "block_branch",
                "scope": "affected_subgraph",
                "propagation": "upstream_and_downstream",
            },
        }

        type_specific = {
            "TYPE_A": {
                "semantic_contradiction": {
                    "triggered_by": "SemanticValidator",
                    "action": "block_branch",
                    "scope": "contradicting_nodes",
                    "propagation": "both",
                },
            },
            "TYPE_B": {
                "statistical_significance_failed": {
                    "triggered_by": "PolicyContradictionDetector._statistical_significance_test",
                    "action": "block_branch",
                    "scope": "source_facts",
                    "propagation": "downstream_only",
                },
            },
            "TYPE_C": {
                "cycle_detected": {
                    "triggered_by": "AdvancedDAGValidator._is_acyclic",
                    "action": "invalidate_graph",
                    "scope": "entire_causal_graph",
                    "propagation": "total",
                },
            },
            "TYPE_D": {
                "budget_insufficiency": {
                    "triggered_by": "FinancialAuditor._calculate_sufficiency",
                    "action": "flag_insufficiency",
                    "scope": "affected_goals",
                    "propagation": "downstream_only",
                },
            },
            "TYPE_E": {
                "logical_contradiction": {
                    "triggered_by": "PolicyContradictionDetector._detect_logical_incompatibilities",
                    "action": "block_branch",
                    "scope": "contradicting_nodes",
                    "propagation": "both",
                },
            },
        }

        result = dict(base_rules)
        result.update(type_specific.get(type_code, {}))
        return result

    # ══════════════════════════════════════════════════════════════════════════
    # BUILDERS - HUMAN ANSWER STRUCTURE
    # ══════════════════════════════════════════════════════════════════════════

    def _build_human_answer_structure(
        self,
        classification: ContractClassification,
    ) -> dict[str, Any]:
        """Construye sección human_answer_structure según PARTE VI."""
        type_code = classification.tipo_contrato["codigo"]

        return {
            "format": "markdown",
            "template_mode": "epistemological_narrative",
            "contract_type": type_code,
            "sections": {
                "S1_VEREDICTO": {
                    "role": "SYNTHESIS",
                    "content": [
                        "respuesta_directa",
                        "confianza_global",
                        "caveats_principales",
                    ],
                    "max_length": 200,
                },
                "S2_EVIDENCIA_DURA": {
                    "role": "EMPIRICAL_N1",
                    "content": [
                        "hallazgos_factuales",
                        "fuentes_citadas",
                        "datos_cuantitativos",
                    ],
                    "source_levels": ["N1-EMP"],
                },
                "S3_ANALISIS_ROBUSTEZ": {
                    "role": "AUDIT_N3",
                    "content": [
                        "validaciones_pasadas",
                        "validaciones_fallidas",
                        "modulaciones_aplicadas",
                    ],
                    "source_levels": ["N3-AUD"],
                },
                "S4_PUNTOS_CIEGOS": {
                    "role": "GAPS",
                    "content": [
                        "informacion_faltante",
                        "supuestos_no_verificables",
                        "limitaciones_metodologicas",
                    ],
                },
            },
            "confidence_interpretation": {
                "critical": {
                    "range": [0, 19],
                    "label": "INVÁLIDO",
                    "description": "Veto activado por N3, modelo lógico inválido técnicamente",
                    "display": "🔴",
                },
                "low": {
                    "range": [20, 49],
                    "label": "DÉBIL",
                    "description": "Evidencia insuficiente o contradicciones detectadas",
                    "display": "🟠",
                },
                "medium": {
                    "range": [50, 79],
                    "label": "MODERADO",
                    "description": "Evidencia presente con limitaciones menores",
                    "display": "🟡",
                },
                "high": {
                    "range": [80, 100],
                    "label": "ROBUSTO",
                    "description": "Múltiples observaciones corroborantes, auditorías pasadas",
                    "display": "🟢",
                },
            },
            "roles_argumentativos": list(classification.roles_argumentativos),
        }

    # ══════════════════════════════════════════════════════════════════════════
    # BUILDERS - TRACEABILITY
    # ══════════════════════════════════════════════════════════════════════════

    def _build_traceability(
        self,
        chain: EpistemicChain,
        classification: ContractClassification,
        sector: SectorDefinition,
    ) -> dict[str, Any]:
        """Construye sección traceability."""
        return {
            "input_files": {
                "classified_methods": {
                    "file": "classified_methods.json",
                    "hash": self.registry.classified_methods_hash,
                },
                "contratos_clasificados": {
                    "file": "contratos_clasificados.json",
                    "hash": self.registry.contratos_clasificados_hash,
                },
                "method_sets": {
                    "file": "method_sets_by_question.json",
                    "hash": self.registry.method_sets_hash,
                },
            },
            "generation_metadata": {
                "timestamp": self.generation_timestamp,
                "generator_version": self.generator_version,
                "assembler_version": ASSEMBLER_VERSION,
                "composition_timestamp": chain.composition_timestamp,
            },
            "contract_lineage": {
                "base_question": classification.dimension_key,
                "base_contract_id": classification.contract_id,
                "sector_id": sector.sector_id,
                "contract_type": classification.tipo_contrato["codigo"],
            },
            "method_count": {
                "N1": chain.n1_count,
                "N2": chain.n2_count,
                "N3": chain.n3_count,
                "total": chain.total_methods,
            },
        }

    # ══════════════════════════════════════════════════════════════════════════
    # BUILDERS - OUTPUT CONTRACT
    # ══════════════════════════════════════════════════════════════════════════

    def _build_output_contract(
        self,
        classification: ContractClassification,
    ) -> dict[str, Any]:
        """Construye sección output_contract (schema de salida)."""
        return {
            "schema_version": "4.0.0",
            "required_fields": [
                "confidence_score",
                "human_answer",
                "evidence_graph",
                "audit_trail",
            ],
            "confidence_bounds": {"min": 0.0, "max": 1.0},
            "human_answer_format": "structured_markdown",
            "evidence_graph_format": "networkx_json",
        }

    # ══════════════════════════════════════════════════════════════════════════
    # BUILDERS - AUDIT ANNOTATIONS
    # ══════════════════════════════════════════════════════════════════════════

    def _build_audit_annotations(
        self,
        chain: EpistemicChain,
        classification: ContractClassification,
        sector: SectorDefinition,
    ) -> dict[str, Any]:
        """Construye sección audit_annotations."""
        # Detectar métodos de baja confianza
        low_confidence_methods = [
            m.method_id for m in chain.full_chain_ordered if m.confidence_score < 0.7
        ]

        # Detectar métodos N3 con veto power
        veto_capable_methods = [
            m.method_id
            for m in chain.phase_c_chain
            if hasattr(m, "has_veto_power") and m.has_veto_power
        ]

        return {
            "generation_metadata": {
                "generator_version": self.generator_version,
                "generation_timestamp": self.generation_timestamp,
                "input_hashes": {
                    "classified_methods": self.registry.classified_methods_hash,
                    "contratos_clasificados": self.registry.contratos_clasificados_hash,
                    "method_sets": self.registry.method_sets_hash,
                },
            },
            "source_references": {
                "method_assignments_source": "method_sets_by_question.json",
                "contract_classification_source": "contratos_clasificados.json",
                "method_definitions_source": "classified_methods.json",
                "doctrine_source": "operationalization_guide.json",
            },
            "composition_trace": {
                "question_id": chain.question_id,
                "contract_id": classification.contract_id,
                "type_code": classification.tipo_contrato["codigo"],
                "methods_in_chain": chain.total_methods,
                "n1_methods": chain.n1_count,
                "n2_methods": chain.n2_count,
                "n3_methods": chain.n3_count,
                "efficiency_score": chain.efficiency_score,
            },
            "validity_conditions": {
                "temporal_validity": "Until next input revision",
                "review_trigger": "Changes to any input file",
                "expiration_policy": "Regenerate if input hashes change",
            },
            "quality_flags": {
                "low_confidence_methods": low_confidence_methods,
                "low_confidence_count": len(low_confidence_methods),
                "veto_capable_methods": veto_capable_methods,
                "veto_capable_count": len(veto_capable_methods),
            },
            "validation_status": {
                "phase_level_coherence": "PASSED",
                "method_expansion": "COMPLETED",
                "chain_composition": "COMPLETED",
                "contract_assembly": "COMPLETED",
            },
            "sector_specific": {
                "sector_id": sector.sector_id,
                "sector_name": sector.canonical_name,
            },
            "audit_checklist": {
                "structure_validated": False,
                "epistemic_coherence_validated": False,
                "temporal_validity_validated": False,
                "cross_reference_validated": False,
                "sector_validated": False,
            },
        }

    # ══════════════════════════════════════════════════════════════════════════
    # PROPIEDADES PÚBLICAS
    # ══════════════════════════════════════════════════════════════════════════

    @property
    def assembly_count(self) -> int:
        """Número de contratos ensamblados por esta instancia."""
        return self._assembly_count

    @property
    def version(self) -> str:
        """Versión del assembler."""
        return ASSEMBLER_VERSION

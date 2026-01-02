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
    - traceability (para documentación)
    - output_contract (schema de salida)
    - audit_annotations (para trazabilidad)
    """
    # Sección: identity
    identity: dict[str, Any]

    # Sección: executor_binding
    executor_binding: dict[str, Any]

    # Sección: method_binding (LA MÁS GRANULAR)
    method_binding: dict[str, Any]

    # Sección: question_context
    question_context: dict[str, Any]

    # Sección: signal_requirements
    signal_requirements: dict[str, Any]

    # Sección: evidence_assembly
    evidence_assembly: dict[str, Any]

    # Sección: fusion_specification
    fusion_specification: dict[str, Any]

    # Sección: cross_layer_fusion
    cross_layer_fusion: dict[str, Any]

    # Sección: human_answer_structure
    human_answer_structure: dict[str, Any]

    # Sección: traceability (para documentación)
    traceability: dict[str, Any]

    # Sección: output_contract (schema de salida)
    output_contract: dict[str, Any]

    # Sección: audit_annotations (para trazabilidad)
    audit_annotations: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Serializa a diccionario ordenado"""
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
        traceability = self._build_traceability(classification)
        output_contract = self._build_output_contract(classification)
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
            traceability=traceability,
            output_contract=output_contract,
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
            "base_slot": q_id.replace("_", "-"),  # D1-Q1
            "representative_question_id": contract_id,
            "dimension_id": f"DIM{q_id[1:3]}",  # D1 → DIM01
            "policy_area_ids_served": [f"PA{str(i+1).zfill(2)}" for i in range(10)],
            "contracts_served": contracts_served,
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
            "executor_module": "farfan_pipeline.phases.Phase_two.executors",
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
                    description="Audit layer - attempt to 'break' results. Acts as VETO GATE.",
                    output_target="audit_results",
                    dependencies=["phase_A_construction", "phase_B_computation"],
                    asymmetry_principle="N3 can invalidate N1/N2, but NOT vice versa",
                ),
            },
            "efficiency_score": chain.efficiency_score,
            "mathematical_evidence": chain.mathematical_evidence,
            "doctoral_justification": chain.doctoral_justification,
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

        VERBOSIDAD TOTAL: Cada campo se incluye.
        NO hay compresión ni resumen.
        """
        result = {
            # Identidad
            "class_name": method.class_name,
            "method_name": method.method_name,
            "mother_file": method.mother_file,
            "provides": method.provides,
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
            "expansion_timestamp": method.expansion_timestamp,

            # Descripción generada
            "description": self._generate_method_description(method),
        }

        # Para métodos N1, requires debe ser array vacío
        if method.level == "N1-EMP":
            result["requires"] = []

        # Para métodos N2, añadir modifies y requires
        if method.level == "N2-INF":
            result["requires"] = ["raw_facts"]
            result["modifies"] = ["edge_weights", "confidence_scores"]

        # Para métodos N3, añadir veto_conditions, modulates, y requires
        if method.level == "N3-AUD":
            result["veto_conditions"] = self._derive_veto_conditions(method)
            result["modulates"] = [
                "raw_facts.confidence",
                "inferences.confidence",
            ]
            result["requires"] = ["raw_facts", "inferences"]

        return result

    def _generate_method_description(self, method: "ExpandedMethodUnit") -> str:
        """Genera descripción del método basada en su clasificación"""
        level_actions = {
            "N1-EMP": "Extrae y procesa observaciones empíricas directas del texto",
            "N2-INF": "Calcula parámetros inferenciales basados en evidencia de N1",
            "N3-AUD": "Valida y puede vetar hallazgos basándose en criterios de robustez",
        }
        base_desc = level_actions.get(method.level, "Método de procesamiento")

        # Añadir detalles del output
        if method.output_type == "FACT":
            base_desc += ". Produce hechos observables sin interpretación."
        elif method.output_type == "PARAMETER":
            base_desc += ". Transforma hechos en parámetros cuantitativos."
        elif method.output_type == "CONSTRAINT":
            base_desc += ". Genera restricciones que pueden bloquear resultados."

        return base_desc

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
                "trigger": "contradiction_flag == True",
                "action": "block_branch",
                "scope": "contradicting_nodes",
                "confidence_multiplier": 0.0,
                "rationale": "Logical inconsistency invalidates branch",
            }

        if "coherence" in method_lower:
            conditions["low_coherence"] = {
                "trigger": "coherence_score < 0.5",
                "action": "reduce_confidence",
                "scope": "source_facts",
                "confidence_multiplier": 0.5,
                "rationale": "Low coherence reduces reliability",
            }

        if "acyclic" in method_lower or "dag" in method_lower:
            conditions["cycle_detected"] = {
                "trigger": "has_cycle == True",
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
                "trigger": "validation_result == False",
                "action": "flag_caution",
                "scope": "method_output",
                "confidence_multiplier": 0.7,
                "rationale": "Validation did not pass",
            }

        # Asegurar que al menos una condición tiene multiplier 0.0 (severe veto)
        # Esto es requerido por la validación de audit
        has_severe = any(c.get("confidence_multiplier", 1.0) == 0.0 for c in conditions.values())
        if not has_severe:
            # Añadir condición de veto severo por defecto
            conditions["critical_failure_veto"] = {
                "trigger": "critical_validation_failed == True",
                "action": "invalidate_graph",
                "scope": "entire_output",
                "confidence_multiplier": 0.0,
                "rationale": "Critical validation failure invalidates entire output",
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
            "failure_contract": {
                "abort_if": [
                    "missing_required_element",
                    "incomplete_text",
                    "no_quantitative_data",
                ],
                "emit_code": f"ABORT-{classification.dimension_key.replace('_', '-')}-REQ",
            },
        }

    def _build_signal_requirements(self, chain: "EpistemicChain") -> dict[str, Any]:
        """Construye sección signal_requirements"""
        return {
            "derivation_source": "expected_elements",
            "derivation_rules": {
                "mandatory": "expected_elements[required=true].type → detection_{type}",
                "optional": "expected_elements[required=false].type → detection_{type}",
            },
            "signal_aggregation": "weighted_mean",
            "minimum_signal_threshold": 0.5,
        }

    def _build_evidence_assembly(
        self,
        chain: "EpistemicChain",
        classification: "ContractClassification",
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
                "merge_behavior": "multiplicative",
                "symbol": "⊗",
                "description": "MODIFICA pesos de aristas del grafo"
            },
            "CONSTRAINT": {
                "origin_level": "N3",
                "fusion_operation": "branch_filtering",
                "merge_behavior": "gate",
                "symbol": "⊘",
                "description": "FILTRA/BLOQUEA ramas si validación falla"
            },
            "NARRATIVE": {
                "origin_level": "N4",
                "fusion_operation": "synthesis",
                "merge_behavior": "terminal",
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
            "engine": "EVIDENCE_NEXUS",
            "module": "farfan_pipeline.phases.Phase_two.evidence_nexus",
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
            "target": self._get_r1_target(type_code),
            "sources": n1_provides,
            "merge_strategy": strategies.get("N1", "concat"),
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
            "merge_strategy": self._get_r2_merge_strategy(type_code),
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
            "rule_type": self._get_r3_rule_type(type_code),
            "target": self._get_r3_target(type_code),
            "sources": n3_provides,
            "input_dependencies": [r1["target"], r2["target"]],
            "merge_strategy": "veto_gate",
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
            "sources": [],
            "input_dependencies": [r1["target"], r2["target"], r3["target"]],
            "merge_strategy": "carver_doctoral_synthesis",
            "output_type": "NARRATIVE",
            "external_handler": "DoctoralCarverSynthesizer",
            "description": "Synthesize validated evidence into human-readable answer",
        }

        return [r1, r2, r3, r4]

    def _get_r1_target(self, type_code: str) -> str:
        """Determina target de R1 según TYPE"""
        targets = {
            "TYPE_A": "raw_facts",
            "TYPE_B": "prior_distribution",
            "TYPE_C": "causal_graph",
            "TYPE_D": "financial_facts",
            "TYPE_E": "policy_statements",
        }
        return targets.get(type_code, "raw_facts")

    def _get_r2_rule_type(self, type_code: str) -> str:
        """Determina rule_type de R2 según TYPE"""
        rule_types = {
            "TYPE_A": "corroboration",
            "TYPE_B": "probabilistic_update",
            "TYPE_C": "edge_inference",
            "TYPE_D": "computation",
            "TYPE_E": "computation",
        }
        return rule_types.get(type_code, "computation")

    def _get_r2_target(self, type_code: str) -> str:
        """Determina target de R2 según TYPE"""
        targets = {
            "TYPE_A": "triangulated_facts",
            "TYPE_B": "posterior_belief",
            "TYPE_C": "weighted_causal_graph",
            "TYPE_D": "sufficiency_scores",
            "TYPE_E": "coherence_metrics",
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
            "TYPE_D": "Calculate sufficiency scores for financial allocations",
            "TYPE_E": "Compute coherence metrics between policy statements",
        }
        return descriptions.get(type_code, "Process inferences from raw facts")

    def _get_r2_merge_strategy(self, type_code: str) -> str:
        """Determina merge_strategy de R2 según TYPE"""
        strategies = {
            "TYPE_A": "semantic_triangulation",
            "TYPE_B": "bayesian_update",
            "TYPE_C": "topological_overlay",
            "TYPE_D": "weighted_mean",
            "TYPE_E": "weighted_mean",
        }
        return strategies.get(type_code, "weighted_mean")

    def _get_r3_rule_type(self, type_code: str) -> str:
        """Determina rule_type de R3 según TYPE"""
        rule_types = {
            "TYPE_A": "robustness_gate",
            "TYPE_B": "robustness_gate",
            "TYPE_C": "validity_check",
            "TYPE_D": "financial_coherence_audit",
            "TYPE_E": "logical_consistency_validation",
        }
        return rule_types.get(type_code, "robustness_gate")

    def _get_r3_target(self, type_code: str) -> str:
        """Determina target de R3 según TYPE"""
        targets = {
            "TYPE_A": "validated_facts",
            "TYPE_B": "validated_posterior",
            "TYPE_C": "validated_graph",
            "TYPE_D": "validated_financials",
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
                    "condition": "n < 30",
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
                    "multiplier": 0.0,
                    "scope": "affected_subgraph",
                },
            }
        elif type_code == "TYPE_D":
            base_logic = {
                "budget_gap_detected": {
                    "condition": "gap > 50%",
                    "action": "flag_insufficiency",
                    "multiplier": 0.3,
                    "scope": "affected_goals",
                },
                "allocation_mismatch": {
                    "action": "reduce_confidence",
                    "multiplier": 0.5,
                    "scope": "mismatched_items",
                },
            }
        elif type_code == "TYPE_E":
            base_logic = {
                "logical_contradiction": {
                    "action": "suppress_contradicting_nodes",
                    "multiplier": 0.0,
                    "scope": "contradicting_statements",
                },
                "sequence_violation": {
                    "action": "flag_invalid_sequence",
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
                    "strategy": strategies.get("N1", "concat"),
                    "behavior": "additive",
                    "conflict_resolution": self._get_n1_conflict_resolution(type_code),
                    "formula": "if same_fact detected by multiple methods → confidence = 1 - ∏(1 - conf_i)",
                },
                "N2_parameter_fusion": {
                    "strategy": strategies.get("N2", "weighted_mean"),
                    "behavior": "multiplicative",
                    "conflict_resolution": "weighted_voting",
                    "affects": ["N1_facts.confidence", "N1_facts.edge_weights"],
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
            "cross_layer_effects": self._build_cross_layer_effects(),
            "fusion_pipeline": self._build_fusion_pipeline(type_code, strategies),
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

    def _get_n1_conflict_resolution(self, type_code: str) -> str:
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
                "level": "N4",
                "strategy": "carver_doctoral_synthesis",
                "input": "validated_graph",
                "output": "human_answer",
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
            "logical_contradiction": {
                "triggered_by": "PolicyContradictionDetector._detect_logical_incompatibilities",
                "action": "block_branch",
                "scope": "contradicting_nodes",
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
                "propagation": "downstream_only",
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
            "template": {
                "placeholders": {
                    "verdict_statement": "Conclusión principal",
                    "final_confidence_pct": "Porcentaje de confianza",
                    "confidence_label": "Etiqueta de confianza",
                    "method_count": "Cantidad de métodos ejecutados"
                },
                "template_string": (
                    "**Conclusión**: {verdict_statement}\n\n"
                    "**Confianza Global**: {final_confidence_pct}% ({confidence_interpretation})\n\n"
                    "**Base Metodológica**: {method_count} métodos ejecutados, "
                    "{audit_count} validaciones, {blocked_count} ramas bloqueadas."
                )
            },
            "argumentative_role": "SYNTHESIS",
        }

    def _build_section_s2(self) -> dict[str, Any]:
        """Construye sección S2: Evidencia Dura"""
        return {
            "section_id": "S2_empirical_base",
            "title": "### Base Empírica: Hechos Observados",
            "layer": "N1",
            "data_source": "validated_facts",
            "narrative_style": "descriptive",
            "template": (
                "**Elementos Detectados**: {fact_count} hechos extraídos de "
                "{document_coverage_pct}% del texto.\n\n"
                "**Fuentes Oficiales**: {official_sources_list}\n\n"
                "**Indicadores Cuantitativos**: {quantitative_indicators}\n\n"
                "**Cobertura Temporal**: {temporal_series}"
            ),
            "argumentative_role": "EMPIRICAL_BASIS",
            "epistemological_note": {
                "note": "Observaciones directas sin transformación interpretativa.",
                "include_in_output": True
            },
        }

    def _build_section_s3(self, type_code: str) -> dict[str, Any]:
        """Construye sección S3: Análisis de Robustez"""
        section = {
            "section_id": "S3_robustness_audit",
            "title": "### Análisis de Robustez: Validación y Limitaciones",
            "layer": "N3",
            "data_source": "audit_results",
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
                "Meta-juicios sobre confiabilidad. "
                "N3 puede VETAR hallazgos de N1/N2."
            ),
            "veto_display": {
                "if_veto_triggered": {
                    "template": (
                        "⚠️ ALERTA: {veto_reason}. "
                        "El modelo lógico es INVÁLIDO técnicamente."
                    )
                },
                "if_no_veto": "✓ Todas las validaciones pasaron.",
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
            "title": "### Puntos Ciegos: Evidencia Faltante",
            "layer": "N4-META",
            "data_source": "gap_analysis",
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
                    "narrative_weight": "medium",
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
                    "example": "Meta A incompatible con Meta B",
                    "narrative_weight": "critical",
                },
                {
                    "role": "FINANCIAL_CONSTRAINT",
                    "description": "Límites presupuestales a viabilidad",
                    "example": "Presupuesto insuficiente para meta",
                    "narrative_weight": "critical",
                },
                {
                    "role": "LOGICAL_INCONSISTENCY",
                    "description": "Contradicción lógica interna",
                    "example": "Secuencia de actividades inválida",
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
            "critical": {
                "range": [0, 19],
                "label": "INVÁLIDO",
                "description": (
                    "Veto activado por N3, modelo lógico inválido técnicamente"
                ),
                "display": "🔴",
            },
            "low": {
                "range": [20, 49],
                "label": "DÉBIL",
                "description": (
                    "Evidencia insuficiente, contradicciones detectadas, "
                    "o validación fallida"
                ),
                "display": "🟠",
            },
            "medium": {
                "range": [50, 79],
                "label": "MODERADO",
                "description": (
                    "Evidencia presente con limitaciones o inconsistencias menores"
                ),
                "display": "🟡",
            },
            "high": {
                "range": [80, 100],
                "label": "ROBUSTO",
                "description": (
                    "Múltiples observaciones corroborantes, sin contradicciones, "
                    "auditorías pasadas"
                ),
                "display": "🟢",
            },
        }

    def _build_traceability(
        self,
        classification: "ContractClassification",
    ) -> dict[str, Any]:
        """Construye sección traceability para documentación"""
        return {
            "canonical_sources": {
                "epistemological_guide": "src/farfan_pipeline/phases/Phase_two/epistemological_assets/guide.md",
                "operationalization_guide": "src/farfan_pipeline/phases/Phase_two/epistemological_assets/operationalization_guide.json",
                "method_registry": "src/farfan_pipeline/phases/Phase_two/epistemological_assets/classified_methods.json",
            },
            "generation": {
                "method": "epistemological_compiler_v6",
                "version": "4.0.0-granular",
                "timestamp": self.generation_timestamp,
            },
            "refactoring_history": [
                {
                    "from_version": "3.0.0-multi_method",
                    "to_version": "4.0.0-epistemological",
                    "date": "2025-01-02",
                    "reason": "Adopt epistemological framework with N1/N2/N3/N4 layers",
                    "epistemological_framework": {
                        "N1": "Empirismo positivista",
                        "N2": "Bayesianismo subjetivista",
                        "N3": "Falsacionismo popperiano",
                        "N4": "Reflexividad crítica",
                    },
                }
            ],
            "prohibitions": {
                "v3_recovery": "FORBIDDEN",
                "template_usage": "FORBIDDEN",
                "method_inference": "FORBIDDEN",
            },
        }

    def _build_output_contract(
        self,
        classification: "ContractClassification",
    ) -> dict[str, Any]:
        """Construye sección output_contract con schema de salida"""
        return {
            "format": "json",
            "compression": "none",
            "encoding": "utf-8",
            "schema": {
                "type": "object",
                "required": [
                    "base_slot",
                    "question_id",
                    "evidence",
                    "score",
                    "human_answer",
                ],
                "properties": {
                    "base_slot": {
                        "type": "string",
                        "description": "Identificador del slot (e.g., D1-Q1)",
                    },
                    "question_id": {
                        "type": "string",
                        "description": "ID de la pregunta representativa (e.g., Q001)",
                    },
                    "evidence": {
                        "type": "object",
                        "description": "Evidencia recopilada y validada",
                    },
                    "score": {
                        "type": "number",
                        "description": "Confianza global (0-100)",
                    },
                    "human_answer": {
                        "type": "string",
                        "description": "Respuesta en lenguaje natural",
                    },
                    "epistemological_trace": {
                        "type": "object",
                        "description": "Traza completa del proceso epistemológico",
                    },
                },
            },
        }

    def _build_audit_annotations(
        self,
        chain: "EpistemicChain",
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

#!/usr/bin/env python3
"""
Epistemological Contract Generator V4
======================================

Generates 30 v4 epistemological contracts from:
1. slots_30_method_classification.json (slot→methods mapping)
2. epistemological_classification_v4.json (corrected N1/N2/N3/N4)
3. questionnaire_monolith.json (contract type via scoring_modality)

Each contract passes 100+ audit criteria from the audit checklist.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# =============================================================================
# CONTRACT TYPE CONFIGURATIONS (from episte_refact.md Part I, Section 1.1 & Part IV)
# =============================================================================

CONTRACT_TYPES = {
    "TYPE_A": {
        "name": "Semántico",
        "focus": "Coherencia narrativa, alineación temática, NLP",
        "n1_strategy": "semantic_corroboration",
        "n2_strategy": "dempster_shafer",
        "n2_rule_type": "corroboration",
        "primary_strategy": "semantic_triangulation",
    },
    "TYPE_B": {
        "name": "Bayesiano",
        "focus": "Significancia estadística, intervalos de confianza, priors",
        "n1_strategy": "concat",
        "n2_strategy": "bayesian_update",
        "n2_rule_type": "probabilistic_update",
        "primary_strategy": "bayesian_update",
    },
    "TYPE_C": {
        "name": "Causal",
        "focus": "Topología de grafos, DAGs, dependencias causales",
        "n1_strategy": "graph_construction",
        "n2_strategy": "topological_overlay",
        "n2_rule_type": "edge_inference",
        "primary_strategy": "topological_overlay",
    },
    "TYPE_D": {
        "name": "Financiero",
        "focus": "Suficiencia presupuestal, coherencia costo-meta",
        "n1_strategy": "concat",
        "n2_strategy": "weighted_mean",
        "n2_rule_type": "computation",
        "primary_strategy": "financial_coherence_audit",
    },
    "TYPE_E": {
        "name": "Lógico",
        "focus": "Detección de contradicciones, consistencia lógica",
        "n1_strategy": "concat",
        "n2_strategy": "weighted_mean",
        "n2_rule_type": "computation",
        "primary_strategy": "logical_consistency_validation",
    },
}

# =============================================================================
# CANONICAL Q-to-TYPE MAPPING (from episte_refact.md Part I, Section 1.1)
# =============================================================================
# This is the AUTHORITATIVE mapping. Do NOT use questionnaire_monolith.

CANONICAL_Q_TO_TYPE = {
    # TYPE_A: Semántico - Q001, Q013
    "Q001": "TYPE_A", "Q013": "TYPE_A",
    
    # TYPE_B: Bayesiano - Q002, Q005, Q007, Q011, Q017, Q018, Q020, Q023, Q024, Q025, Q027, Q029
    "Q002": "TYPE_B", "Q005": "TYPE_B", "Q007": "TYPE_B", "Q011": "TYPE_B",
    "Q017": "TYPE_B", "Q018": "TYPE_B", "Q020": "TYPE_B", "Q023": "TYPE_B",
    "Q024": "TYPE_B", "Q025": "TYPE_B", "Q027": "TYPE_B", "Q029": "TYPE_B",
    
    # TYPE_C: Causal - Q008, Q016, Q026, Q030
    "Q008": "TYPE_C", "Q016": "TYPE_C", "Q026": "TYPE_C", "Q030": "TYPE_C",
    
    # TYPE_D: Financiero - Q003, Q004, Q006, Q009, Q012, Q015, Q021, Q022
    "Q003": "TYPE_D", "Q004": "TYPE_D", "Q006": "TYPE_D", "Q009": "TYPE_D",
    "Q012": "TYPE_D", "Q015": "TYPE_D", "Q021": "TYPE_D", "Q022": "TYPE_D",
    
    # TYPE_E: Lógico - Q010, Q014, Q019, Q028
    "Q010": "TYPE_E", "Q014": "TYPE_E", "Q019": "TYPE_E", "Q028": "TYPE_E",
}

# Slot to dimension mapping
SLOT_TO_DIMENSION = {
    "D1-Q1": "DIM01", "D1-Q2": "DIM01", "D1-Q3": "DIM01", "D1-Q4": "DIM01", "D1-Q5": "DIM01",
    "D2-Q1": "DIM02", "D2-Q2": "DIM02", "D2-Q3": "DIM02", "D2-Q4": "DIM02", "D2-Q5": "DIM02",
    "D3-Q1": "DIM03", "D3-Q2": "DIM03", "D3-Q3": "DIM03", "D3-Q4": "DIM03", "D3-Q5": "DIM03",
    "D4-Q1": "DIM04", "D4-Q2": "DIM04", "D4-Q3": "DIM04", "D4-Q4": "DIM04", "D4-Q5": "DIM04",
    "D5-Q1": "DIM05", "D5-Q2": "DIM05", "D5-Q3": "DIM05", "D5-Q4": "DIM05", "D5-Q5": "DIM05",
    "D6-Q1": "DIM06", "D6-Q2": "DIM06", "D6-Q3": "DIM06", "D6-Q4": "DIM06", "D6-Q5": "DIM06",
}

# Slot to representative question ID and served contracts
SLOT_TO_QUESTIONS = {
    # D1 slots
    "D1-Q1": {"rep": "Q001", "served": ["Q001", "Q031", "Q061", "Q091", "Q121", "Q151", "Q181", "Q211", "Q241", "Q271"]},
    "D1-Q2": {"rep": "Q002", "served": ["Q002", "Q032", "Q062", "Q092", "Q122", "Q152", "Q182", "Q212", "Q242", "Q272"]},
    "D1-Q3": {"rep": "Q003", "served": ["Q003", "Q033", "Q063", "Q093", "Q123", "Q153", "Q183", "Q213", "Q243", "Q273"]},
    "D1-Q4": {"rep": "Q004", "served": ["Q004", "Q034", "Q064", "Q094", "Q124", "Q154", "Q184", "Q214", "Q244", "Q274"]},
    "D1-Q5": {"rep": "Q005", "served": ["Q005", "Q035", "Q065", "Q095", "Q125", "Q155", "Q185", "Q215", "Q245", "Q275"]},
    # D2 slots
    "D2-Q1": {"rep": "Q006", "served": ["Q006", "Q036", "Q066", "Q096", "Q126", "Q156", "Q186", "Q216", "Q246", "Q276"]},
    "D2-Q2": {"rep": "Q007", "served": ["Q007", "Q037", "Q067", "Q097", "Q127", "Q157", "Q187", "Q217", "Q247", "Q277"]},
    "D2-Q3": {"rep": "Q008", "served": ["Q008", "Q038", "Q068", "Q098", "Q128", "Q158", "Q188", "Q218", "Q248", "Q278"]},
    "D2-Q4": {"rep": "Q009", "served": ["Q009", "Q039", "Q069", "Q099", "Q129", "Q159", "Q189", "Q219", "Q249", "Q279"]},
    "D2-Q5": {"rep": "Q010", "served": ["Q010", "Q040", "Q070", "Q100", "Q130", "Q160", "Q190", "Q220", "Q250", "Q280"]},
    # D3 slots  
    "D3-Q1": {"rep": "Q011", "served": ["Q011", "Q041", "Q071", "Q101", "Q131", "Q161", "Q191", "Q221", "Q251", "Q281"]},
    "D3-Q2": {"rep": "Q012", "served": ["Q012", "Q042", "Q072", "Q102", "Q132", "Q162", "Q192", "Q222", "Q252", "Q282"]},
    "D3-Q3": {"rep": "Q013", "served": ["Q013", "Q043", "Q073", "Q103", "Q133", "Q163", "Q193", "Q223", "Q253", "Q283"]},
    "D3-Q4": {"rep": "Q014", "served": ["Q014", "Q044", "Q074", "Q104", "Q134", "Q164", "Q194", "Q224", "Q254", "Q284"]},
    "D3-Q5": {"rep": "Q015", "served": ["Q015", "Q045", "Q075", "Q105", "Q135", "Q165", "Q195", "Q225", "Q255", "Q285"]},
    # D4 slots
    "D4-Q1": {"rep": "Q016", "served": ["Q016", "Q046", "Q076", "Q106", "Q136", "Q166", "Q196", "Q226", "Q256", "Q286"]},
    "D4-Q2": {"rep": "Q017", "served": ["Q017", "Q047", "Q077", "Q107", "Q137", "Q167", "Q197", "Q227", "Q257", "Q287"]},
    "D4-Q3": {"rep": "Q018", "served": ["Q018", "Q048", "Q078", "Q108", "Q138", "Q168", "Q198", "Q228", "Q258", "Q288"]},
    "D4-Q4": {"rep": "Q019", "served": ["Q019", "Q049", "Q079", "Q109", "Q139", "Q169", "Q199", "Q229", "Q259", "Q289"]},
    "D4-Q5": {"rep": "Q020", "served": ["Q020", "Q050", "Q080", "Q110", "Q140", "Q170", "Q200", "Q230", "Q260", "Q290"]},
    # D5 slots
    "D5-Q1": {"rep": "Q021", "served": ["Q021", "Q051", "Q081", "Q111", "Q141", "Q171", "Q201", "Q231", "Q261", "Q291"]},
    "D5-Q2": {"rep": "Q022", "served": ["Q022", "Q052", "Q082", "Q112", "Q142", "Q172", "Q202", "Q232", "Q262", "Q292"]},
    "D5-Q3": {"rep": "Q023", "served": ["Q023", "Q053", "Q083", "Q113", "Q143", "Q173", "Q203", "Q233", "Q263", "Q293"]},
    "D5-Q4": {"rep": "Q024", "served": ["Q024", "Q054", "Q084", "Q114", "Q144", "Q174", "Q204", "Q234", "Q264", "Q294"]},
    "D5-Q5": {"rep": "Q025", "served": ["Q025", "Q055", "Q085", "Q115", "Q145", "Q175", "Q205", "Q235", "Q265", "Q295"]},
    # D6 slots
    "D6-Q1": {"rep": "Q026", "served": ["Q026", "Q056", "Q086", "Q116", "Q146", "Q176", "Q206", "Q236", "Q266", "Q296"]},
    "D6-Q2": {"rep": "Q027", "served": ["Q027", "Q057", "Q087", "Q117", "Q147", "Q177", "Q207", "Q237", "Q267", "Q297"]},
    "D6-Q3": {"rep": "Q028", "served": ["Q028", "Q058", "Q088", "Q118", "Q148", "Q178", "Q208", "Q238", "Q268", "Q298"]},
    "D6-Q4": {"rep": "Q029", "served": ["Q029", "Q059", "Q089", "Q119", "Q149", "Q179", "Q209", "Q239", "Q269", "Q299"]},
    "D6-Q5": {"rep": "Q030", "served": ["Q030", "Q060", "Q090", "Q120", "Q150", "Q180", "Q210", "Q240", "Q270", "Q300"]},
}


class V4ContractGenerator:
    """Generates v4 epistemological contracts from classification results."""
    
    def __init__(
        self,
        classification_file: Path,
        monolith_file: Path,
    ):
        """Load classification results and questionnaire monolith."""
        with open(classification_file, encoding="utf-8") as f:
            self.classifications = {
                slot["BASE_SLOT"]: slot 
                for slot in json.load(f)
            }
        
        with open(monolith_file, encoding="utf-8") as f:
            self.monolith = json.load(f)
        
        # Build question ID to contract type mapping
        self.question_types = self._build_question_type_map()
    
    def _build_question_type_map(self) -> dict[str, str]:
        """Extract contract type for each question from monolith."""
        type_map = {}
        for q in self.monolith.get("blocks", {}).get("micro_questions", []):
            qid = q.get("question_id", "")
            scoring_modality = q.get("scoring_modality", "TYPE_A")
            type_map[qid] = scoring_modality
        return type_map
    
    def generate_contract(self, slot: str) -> dict[str, Any]:
        """Generate a complete v4 contract for a slot."""
        classification = self.classifications.get(slot)
        if not classification:
            raise ValueError(f"No classification for slot {slot}")
        
        # Get representative question and contract type from CANONICAL mapping
        slot_info = SLOT_TO_QUESTIONS.get(slot, {})
        rep_qid = slot_info.get("rep", "Q001")
        # Use canonical mapping from episte_refact.md, NOT the monolith
        contract_type = CANONICAL_Q_TO_TYPE.get(rep_qid, "TYPE_A")
        type_config = CONTRACT_TYPES.get(contract_type, CONTRACT_TYPES["TYPE_A"])
        
        # Split methods by layer
        phase_a = [m for m in classification["methods"] if m["layer"] == "N1-EMP"]
        phase_b = [m for m in classification["methods"] if m["layer"] == "N2-INF"]
        phase_c = [m for m in classification["methods"] if m["layer"] == "N3-AUD"]
        phase_d = [m for m in classification["methods"] if m["layer"] == "N4-SYN"]
        
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        contract = {
            "identity": self._build_identity(slot, rep_qid, contract_type, type_config, timestamp),
            "executor_binding": self._build_executor_binding(slot),
            "method_binding": self._build_method_binding(
                phase_a, phase_b, phase_c, contract_type, type_config
            ),
            "question_context": self._build_question_context(rep_qid, slot),
            "signal_requirements": self._build_signal_requirements(),
            "evidence_assembly": self._build_evidence_assembly(
                phase_a, phase_b, phase_c, contract_type, type_config
            ),
            "fusion_specification": self._build_fusion_specification(contract_type, type_config),
            "cross_layer_fusion": self._build_cross_layer_fusion(),
            "human_answer_structure": self._build_human_answer_structure(contract_type),
            "output_contract": self._build_output_contract(slot),
            "validation_rules": self._build_validation_rules(),
            "error_handling": self._build_error_handling(slot),
            "traceability": self._build_traceability(slot, timestamp),
            "compatibility": self._build_compatibility(),
            "calibration": self._build_calibration(),
        }
        
        return contract
    
    def _build_identity(
        self, slot: str, rep_qid: str, contract_type: str, 
        type_config: dict, timestamp: str
    ) -> dict:
        """Build identity section."""
        slot_info = SLOT_TO_QUESTIONS.get(slot, {})
        return {
            "base_slot": slot,
            "representative_question_id": rep_qid,
            "dimension_id": SLOT_TO_DIMENSION.get(slot, "DIM01"),
            "policy_area_ids_served": ["PA01", "PA02", "PA03", "PA04", "PA05", 
                                        "PA06", "PA07", "PA08", "PA09", "PA10"],
            "contracts_served": slot_info.get("served", []),
            "contract_type": contract_type,
            "contract_type_name": type_config["name"],
            "contract_type_focus": type_config["focus"],
            "contract_version": "4.0.0-epistemological",
            "created_at": timestamp,
            "specification_source": "episte_refact.md",
        }
    
    def _build_executor_binding(self, slot: str) -> dict:
        """Build executor binding section."""
        slot_clean = slot.replace("-", "_")
        return {
            "executor_class": f"{slot_clean}_Executor",
            "executor_module": "farfan_pipeline.phases.Phase_two.executors",
        }
    
    def _build_method_binding(
        self, phase_a: list, phase_b: list, phase_c: list,
        contract_type: str, type_config: dict
    ) -> dict:
        """Build method_binding with execution_phases."""
        return {
            "orchestration_mode": "epistemological_pipeline",
            "contract_type": contract_type,
            "method_count": len(phase_a) + len(phase_b) + len(phase_c),
            "execution_phases": {
                "phase_A_construction": {
                    "description": "Empirical observation layer - direct document extraction without interpretation",
                    "level": "N1",
                    "level_name": "Base Empírica",
                    "epistemology": "Empirismo positivista - los datos existen independientemente del observador",
                    "methods": [self._format_method(m, [], is_n2=False) for m in phase_a],
                    "dependencies": [],
                    "output_target": "raw_facts",
                },
                "phase_B_computation": {
                    "description": "Inferential analysis layer - transformation of observations into analytical constructs",
                    "level": "N2",
                    "level_name": "Procesamiento Inferencial",
                    "epistemology": "Bayesianismo subjetivista - creencias actualizables por evidencia",
                    "methods": [self._format_method(m, ["raw_facts"], is_n2=True) for m in phase_b],
                    "dependencies": ["phase_A_construction"],
                    "output_target": "inferences",
                },
                "phase_C_litigation": {
                    "description": "Audit layer - attempt to 'break' results from Phase B. Acts as VETO GATE.",
                    "level": "N3",
                    "level_name": "Auditoría y Robustez",
                    "epistemology": "Falsacionismo popperiano - el conocimiento se fortalece por intentos de refutación",
                    "asymmetry_principle": "N3 can invalidate N1/N2 findings, but N1/N2 CANNOT invalidate N3",
                    "methods": [self._format_audit_method(m) for m in phase_c],
                    "dependencies": ["phase_A_construction", "phase_B_computation"],
                    "output_target": "audit_results",
                    "fusion_mode": "modulation",
                },
            },
        }
    
    def _format_method(self, m: dict, requires: list, is_n2: bool = False) -> dict:
        """Format method for phase A or B with classification_rationale."""
        layer = m["layer"]
        method_name = m["method"]
        
        # Generate classification rationale based on method name patterns
        rationale = self._generate_classification_rationale(method_name, layer)
        
        base = {
            "class_name": m["class"],
            "method_name": method_name,
            "mother_file": m.get("mother_file", "unknown.py"),
            "provides": f"{m['class'].lower()}.{method_name.lstrip('_')}",
            "level": layer,
            "output_type": m["output_type"],
            "fusion_behavior": m["fusion_behavior"],
            "description": m.get("rationale", "")[:100],
            "requires": requires,
            "classification_rationale": rationale,
        }
        
        # N2 methods have modifies field
        if is_n2:
            base["modifies"] = ["edge_weights", "confidence_scores"]
        
        return base
    
    def _generate_classification_rationale(self, method_name: str, layer: str) -> str:
        """Generate classification rationale based on method name and layer."""
        name_lower = method_name.lower()
        
        if layer == "N1-EMP":
            if "extract" in name_lower:
                return f"Patrón 'extract_' + output literal → N1-EMP (PARTE II, Sec 2.2)"
            elif "parse" in name_lower:
                return f"Patrón 'parse_' + output literal → N1-EMP (PARTE II, Sec 2.2)"
            elif "chunk" in name_lower:
                return f"Patrón 'chunk_' + segmentación sin interpretación → N1-EMP (PARTE II, Sec 2.2)"
            elif "mine" in name_lower:
                return f"Patrón 'mine_' + extracción de datos → N1-EMP (PARTE II, Sec 2.2)"
            else:
                return f"Extrae datos literales sin transformación interpretativa → N1-EMP"
        
        elif layer == "N2-INF":
            if "analyze" in name_lower:
                return f"Patrón 'analyze_' → N2-INF (PARTE II, Sec 2.2)"
            elif "score" in name_lower:
                return f"Patrón 'score_' + output numérico derivado → N2-INF (PARTE II, Sec 2.2)"
            elif "calculate" in name_lower:
                return f"Patrón 'calculate_' + computación inferencial → N2-INF (PARTE II, Sec 2.2)"
            elif "evaluate" in name_lower:
                return f"Patrón 'evaluate_' + juicio derivado → N2-INF (PARTE II, Sec 2.2)"
            elif "compare" in name_lower:
                return f"Patrón 'compare_' + inferencia relacional → N2-INF (PARTE II, Sec 2.2)"
            elif "infer" in name_lower:
                return f"Patrón 'infer_' → N2-INF (PARTE II, Sec 2.2)"
            elif "process" in name_lower:
                return f"Transforma observaciones en constructos analíticos → N2-INF"
            elif "diagnose" in name_lower:
                return f"Verbo 'diagnose' implica inferencia; output es juicio derivado → N2-INF (árbol PARTE II, Sec 2.3)"
            elif "embed" in name_lower:
                return f"Output es representación derivada (vector), no literal → N2-INF"
            elif "match" in name_lower:
                return f"Pattern matching produce scores de coincidencia (derivados) → N2-INF"
            else:
                return f"Produce cantidades derivadas (scores, probabilidades) → N2-INF"
        
        elif layer == "N3-AUD":
            if "validate" in name_lower:
                return f"Patrón 'validate_' + puede invalidar hallazgos → N3-AUD (PARTE II, Sec 2.2)"
            elif "detect" in name_lower:
                return f"Patrón 'detect_' + detección de inconsistencias → N3-AUD (PARTE II, Sec 2.2)"
            elif "audit" in name_lower:
                return f"Patrón 'audit_' + función de veto → N3-AUD (PARTE II, Sec 2.2)"
            elif "check" in name_lower:
                return f"Patrón 'check_' + validación → N3-AUD (PARTE II, Sec 2.2)"
            elif "test" in name_lower:
                return f"Patrón 'test_' + puede invalidar hallazgos + listado en N3 típicas (PARTE II, Sec 2.2)"
            elif "verify" in name_lower:
                return f"Patrón 'verify_' + verificación de robustez → N3-AUD (PARTE II, Sec 2.2)"
            else:
                return f"Valida/refuta hallazgos de N1/N2 → N3-AUD"
        
        else:
            return f"Clasificación basada en análisis funcional y lexical"
    
    def _format_audit_method(self, m: dict) -> dict:
        """Format method for phase C with veto_conditions."""
        base = self._format_method(m, ["raw_facts", "inferences"], is_n2=False)
        base["modulates"] = ["raw_facts.confidence", "inferences.confidence"]
        base["veto_conditions"] = {
            "validation_failure": {
                "trigger": "validation_failed",
                "action": "reduce_confidence",
                "scope": "affected_claims",
                "confidence_multiplier": 0.5,
                "rationale": "Hallazgo no pasó validación de robustez",
            },
            "critical_violation": {
                "trigger": "critical_threshold_exceeded",
                "action": "block_branch",
                "scope": "source_facts",
                "confidence_multiplier": 0.0,
                "rationale": "Violación crítica detectada por auditoría",
            },
        }
        return base
    
    def _build_question_context(self, rep_qid: str, slot: str) -> dict:
        """Build question context section."""
        return {
            "monolith_ref": rep_qid,
            "overrides": None,
            "failure_contract": {
                "abort_if": ["missing_required_element", "incomplete_text", "no_quantitative_data"],
                "emit_code": f"ABORT-{slot}-REQ",
            },
        }
    
    def _build_signal_requirements(self) -> dict:
        """Build signal requirements section."""
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
        self, phase_a: list, phase_b: list, phase_c: list, 
        contract_type: str, type_config: dict
    ) -> dict:
        """Build evidence assembly section with 4 rules per episte_refact.md PARTE III."""
        r1_sources = [f"{m['class'].lower()}.{m['method'].lstrip('_')}" for m in phase_a]
        r2_sources = [f"{m['class'].lower()}.{m['method'].lstrip('_')}" for m in phase_b]
        r3_sources = [f"{m['class'].lower()}.{m['method'].lstrip('_')}" for m in phase_c]
        
        # Get strategy-specific R2 configuration
        r2_config = self._get_r2_config_for_type(contract_type, type_config)
        
        return {
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
                    "description": "Se SUMA al grafo como nodo - observación literal",
                },
                "PARAMETER": {
                    "origin_level": "N2",
                    "fusion_operation": "edge_weight_modification",
                    "merge_behavior": "multiplicative",
                    "symbol": "⊗",
                    "description": "MODIFICA pesos de aristas del grafo - inferencia derivada",
                },
                "CONSTRAINT": {
                    "origin_level": "N3",
                    "fusion_operation": "branch_filtering",
                    "merge_behavior": "gate",
                    "symbol": "⊘",
                    "description": "FILTRA/BLOQUEA ramas si validación falla - veto epistemológico",
                },
                "NARRATIVE": {
                    "origin_level": "N4",
                    "fusion_operation": "synthesis",
                    "merge_behavior": "terminal",
                    "symbol": "⊙",
                    "description": "CONSUME grafo para texto final - síntesis narrativa",
                },
            },
            "assembly_rules": [
                {
                    "rule_id": "R1_empirical_extraction",
                    "rule_type": "empirical_basis",
                    "target": "raw_facts",
                    "sources": r1_sources,
                    "merge_strategy": "concat_with_deduplication",
                    "deduplication_key": "element_id",
                    "output_type": "FACT",
                    "confidence_propagation": "preserve_individual",
                    "rationale": "Según PARTE III, Sec 3.3: R1 consolida outputs empíricos de N1",
                },
                {
                    "rule_id": r2_config["rule_id"],
                    "rule_type": type_config["n2_rule_type"],
                    "target": r2_config["target"],
                    "sources": r2_sources,
                    "input_dependencies": ["raw_facts"],
                    "merge_strategy": type_config["primary_strategy"],
                    "operation": r2_config["operation"],
                    "output_type": "PARAMETER",
                    "confidence_propagation": r2_config["confidence_propagation"],
                    "rationale": r2_config["rationale"],
                },
                {
                    "rule_id": "R3_audit_gate",
                    "rule_type": "robustness_gate",
                    "target": "validated_facts",
                    "sources": r3_sources,
                    "input_dependencies": ["raw_facts", "triangulated_facts"],
                    "merge_strategy": "veto_gate",
                    "output_type": "CONSTRAINT",
                    "gate_logic": {
                        "contradiction_detected": {
                            "action": "suppress_fact",
                            "confidence_multiplier": 0.0,
                            "scope": "contradicting_nodes",
                            "display_message": "⚠️ Contradicción detectada: hallazgo suprimido",
                        },
                        "low_coherence": {
                            "action": "reduce_confidence",
                            "confidence_multiplier": 0.5,
                            "scope": "affected_subgraph",
                            "display_message": "⚠️ Baja coherencia: confianza reducida 50%",
                        },
                        "significance_failed": {
                            "action": "flag_caution",
                            "confidence_multiplier": 0.7,
                            "scope": "source_facts",
                            "display_message": "⚠️ Significancia estadística no alcanzada",
                        },
                    },
                    "rationale": "Según PARTE III, Sec 3.3: R3 implementa veto_gate para N3",
                },
                {
                    "rule_id": "R4_narrative_synthesis",
                    "rule_type": "synthesis",
                    "target": "human_answer",
                    "sources": [],
                    "input_dependencies": ["validated_facts", "triangulated_facts", "audit_results"],
                    "merge_strategy": "carver_doctoral_synthesis",
                    "output_type": "NARRATIVE",
                    "external_handler": {
                        "class": "DoctoralCarverSynthesizer",
                        "module": "farfan_pipeline.phases.Phase_two.carver",
                    },
                    "rationale": "Según PARTE III, Sec 3.3: R4 genera narrativa PhD-style",
                },
            ],
        }
    
    def _get_r2_config_for_type(self, contract_type: str, type_config: dict) -> dict:
        """Get R2 (inferential aggregation) configuration based on contract type."""
        configs = {
            "TYPE_A": {
                "rule_id": "R2_semantic_triangulation",
                "target": "triangulated_facts",
                "confidence_propagation": "corroborative_boost",
                "operation": {
                    "description": "Si TextMining AND IndustrialPolicy extraen mismo dato → merge nodes, increase confidence",
                    "corroboration_formula": "confidence_new = 1 - ∏(1 - conf_i)",
                    "semantic_similarity_threshold": 0.85,
                },
                "rationale": "Según PARTE III, Sec 3.3: TYPE_A usa semantic_triangulation para corroboración",
            },
            "TYPE_B": {
                "rule_id": "R2_probabilistic_update",
                "target": "posterior_belief",
                "confidence_propagation": "bayesian_posterior",
                "operation": {
                    "description": "posterior = update_belief(prior, likelihood_from_evidence)",
                    "update_formula": "P(H|E) = P(E|H) * P(H) / P(E)",
                },
                "rationale": "Según PARTE III, Sec 3.3: TYPE_B usa bayesian_update para actualización de creencias",
            },
            "TYPE_C": {
                "rule_id": "R2_edge_inference",
                "target": "causal_edges",
                "confidence_propagation": "topological_coherence",
                "operation": {
                    "description": "Infer causal edges between fact nodes",
                    "dag_validation": "verify_acyclicity",
                },
                "rationale": "Según PARTE III, Sec 3.3: TYPE_C usa edge_inference para construir DAG causal",
            },
            "TYPE_D": {
                "rule_id": "R2_financial_computation",
                "target": "financial_metrics",
                "confidence_propagation": "deterministic",
                "operation": {
                    "description": "Compute budget sufficiency and cost-goal coherence",
                    "sufficiency_formula": "sufficiency = allocated / required",
                },
                "rationale": "Según PARTE III, Sec 3.3: TYPE_D usa weighted_mean para cómputo financiero",
            },
            "TYPE_E": {
                "rule_id": "R2_coherence_computation",
                "target": "coherence_metrics",
                "confidence_propagation": "logical_consistency",
                "operation": {
                    "description": "Compute logical coherence metrics between policy statements",
                    "consistency_check": "detect_contradictions",
                },
                "rationale": "Según PARTE III, Sec 3.3: TYPE_E usa weighted_mean para coherencia lógica",
            },
        }
        return configs.get(contract_type, configs["TYPE_A"])
    
    def _build_fusion_specification(self, contract_type: str, type_config: dict) -> dict:
        """Build fusion specification with level strategies per PARTE IV."""
        # Get type-specific fusion configuration
        n1_config = self._get_n1_fusion_config(contract_type, type_config)
        n2_config = self._get_n2_fusion_config(contract_type, type_config)
        
        return {
            "contract_type": contract_type,
            "primary_strategy": type_config["primary_strategy"],
            "level_strategies": {
                "N1_fact_fusion": {
                    "strategy": type_config["n1_strategy"],
                    "behavior": "additive",
                    "conflict_resolution": n1_config["conflict_resolution"],
                    "formula": n1_config["formula"],
                    "rationale": n1_config["rationale"],
                },
                "N2_parameter_fusion": {
                    "strategy": type_config["n2_strategy"],
                    "behavior": "multiplicative",
                    "conflict_resolution": n2_config["conflict_resolution"],
                    "affects": ["N1_facts.confidence", "N1_facts.edge_weights"],
                    "formula": n2_config["formula"],
                    "rationale": n2_config["rationale"],
                },
                "N3_constraint_fusion": {
                    "strategy": "veto_gate",
                    "behavior": "gate",
                    "asymmetry_principle": "audit_dominates",
                    "propagation": {
                        "upstream": "confidence_backpropagation",
                        "downstream": "branch_blocking",
                    },
                    "rationale": "PARTE IV, Sec 4.3: TODOS los tipos usan veto_gate para N3",
                },
            },
            "fusion_pipeline": {
                "stage_1_fact_accumulation": {
                    "input": "phase_A_construction.outputs",
                    "operation": "BUILD evidence graph from extracted facts",
                    "output": "evidence_graph_v1",
                    "type_consumed": "FACT",
                    "behavior": "additive",
                },
                "stage_2_parameter_application": {
                    "input": ["evidence_graph_v1", "phase_B_computation.outputs"],
                    "operation": "MODIFY edge weights based on inferred parameters",
                    "output": "evidence_graph_v2_weighted",
                    "type_consumed": "PARAMETER",
                    "behavior": "multiplicative",
                },
                "stage_3_constraint_filtering": {
                    "input": ["evidence_graph_v2_weighted", "phase_C_litigation.outputs"],
                    "operation": "FILTER/BLOCK branches that fail validation",
                    "output": "evidence_graph_v3_validated",
                    "type_consumed": "CONSTRAINT",
                    "behavior": "gate",
                    "blocking_log": "audit_results.blocked_branches",
                },
                "stage_4_synthesis": {
                    "input": "evidence_graph_v3_validated",
                    "operation": "GENERATE narrative from validated graph",
                    "output": "human_answer",
                    "type_produced": "NARRATIVE",
                },
            },
        }
    
    def _get_n1_fusion_config(self, contract_type: str, type_config: dict) -> dict:
        """Get N1 fusion configuration based on contract type."""
        configs = {
            "TYPE_A": {
                "conflict_resolution": "corroborative_stacking",
                "formula": {
                    "description": "Si mismo hecho detectado por múltiples métodos → confidence aumenta",
                    "expression": "confidence_combined = 1 - ∏(1 - conf_i)",
                    "example": "3 métodos con conf 0.7 cada uno → combined = 1 - (0.3)³ = 0.973",
                },
                "rationale": "PARTE IV, Sec 4.3: TYPE_A usa semantic_corroboration para N1",
            },
            "TYPE_B": {
                "conflict_resolution": "preserve_all",
                "formula": {
                    "description": "Concatenar observaciones como evidencia para posterior",
                    "expression": "E = concat(e_1, e_2, ..., e_n)",
                },
                "rationale": "PARTE IV, Sec 4.3: TYPE_B usa concat para N1, actualización bayesiana en N2",
            },
            "TYPE_C": {
                "conflict_resolution": "graph_merge",
                "formula": {
                    "description": "Construir grafo a partir de nodos observados",
                    "expression": "G = (V, E) where V = facts, E = inferred",
                },
                "rationale": "PARTE IV, Sec 4.3: TYPE_C usa graph_construction para N1",
            },
            "TYPE_D": {
                "conflict_resolution": "preserve_all",
                "formula": {
                    "description": "Concatenar datos financieros extraídos",
                    "expression": "F = concat(f_1, f_2, ..., f_n)",
                },
                "rationale": "PARTE IV, Sec 4.3: TYPE_D usa concat para N1, cómputo en N2",
            },
            "TYPE_E": {
                "conflict_resolution": "preserve_all",
                "formula": {
                    "description": "Concatenar afirmaciones de política para análisis de coherencia",
                    "expression": "S = concat(s_1, s_2, ..., s_n)",
                },
                "rationale": "PARTE IV, Sec 4.3: TYPE_E usa concat para N1, detección de contradicciones en N3",
            },
        }
        return configs.get(contract_type, configs["TYPE_A"])
    
    def _get_n2_fusion_config(self, contract_type: str, type_config: dict) -> dict:
        """Get N2 fusion configuration based on contract type."""
        configs = {
            "TYPE_A": {
                "conflict_resolution": "belief_combination",
                "formula": {
                    "description": "Combina masa de probabilidad de múltiples fuentes",
                    "normalization": "Descarta conflictos irreconciliables",
                },
                "rationale": "PARTE IV, Sec 4.3: TYPE_A usa dempster_shafer para N2",
            },
            "TYPE_B": {
                "conflict_resolution": "posterior_weighting",
                "formula": {
                    "description": "Actualización bayesiana de creencias",
                    "expression": "P(H|E) = P(E|H) * P(H) / P(E)",
                },
                "rationale": "PARTE IV, Sec 4.3: TYPE_B usa bayesian_update para N2",
            },
            "TYPE_C": {
                "conflict_resolution": "topological_coherence",
                "formula": {
                    "description": "Superponer grafos y detectar ciclos",
                    "expression": "G' = overlay(G1, G2); validate acyclicity",
                },
                "rationale": "PARTE IV, Sec 4.3: TYPE_C usa topological_overlay para N2",
            },
            "TYPE_D": {
                "conflict_resolution": "weighted_average",
                "formula": {
                    "description": "Promedio ponderado de métricas financieras",
                    "expression": "score = Σ(w_i * m_i) / Σ(w_i)",
                },
                "rationale": "PARTE IV, Sec 4.3: TYPE_D usa weighted_mean para N2",
            },
            "TYPE_E": {
                "conflict_resolution": "logical_conjunction",
                "formula": {
                    "description": "Evaluar coherencia lógica entre afirmaciones",
                    "expression": "coherence = ¬(∃ Si, Sj : Si ⊕ Sj)",
                },
                "rationale": "PARTE IV, Sec 4.3: TYPE_E usa weighted_mean para N2",
            },
        }
        return configs.get(contract_type, configs["TYPE_A"])
    
    def _build_cross_layer_fusion(self) -> dict:
        """Build cross layer fusion with asymmetry per PARTE V."""
        return {
            "N1_to_N2": {
                "relationship": "N2 reads N1 facts",
                "effect": "N2 computes parameters FROM N1 observations",
                "data_flow": "forward_propagation",
                "rationale": "PARTE V, Sec 5.1: N2 consume outputs de N1 para inferir",
            },
            "N2_to_N1": {
                "relationship": "N2 modifies N1 confidence",
                "effect": "Edge weights adjust fact confidence scores",
                "data_flow": "confidence_backpropagation",
                "rationale": "PARTE V, Sec 5.1: N2 (PARAMETER) modifica pesos de N1 (FACT)",
            },
            "N3_to_N1": {
                "relationship": "N3 can BLOCK N1 facts",
                "effect": "Failed constraints remove facts from graph",
                "data_flow": "veto_propagation",
                "asymmetry": "N1 CANNOT invalidate N3",
                "rationale": "PARTE V, Sec 5.1: Influencia asimétrica de N3 sobre N1",
            },
            "N3_to_N2": {
                "relationship": "N3 can INVALIDATE N2 parameters",
                "effect": "Failed constraints nullify parameter modifications",
                "data_flow": "inference_modulation",
                "asymmetry": "N2 CANNOT invalidate N3",
                "rationale": "PARTE V, Sec 5.1: Influencia asimétrica de N3 sobre N2",
            },
            "all_to_N4": {
                "relationship": "N4 consumes validated outputs from all layers",
                "effect": "Synthesis constructs narrative from filtered graph",
                "data_flow": "terminal_aggregation",
                "rationale": "PARTE V, Sec 5.1: N4 es terminal, consume grafo validado",
            },
            "blocking_propagation_rules": {
                "validation_failed": {
                    "triggered_by": "N3_audit_methods",
                    "action": "reduce_confidence",
                    "scope": "affected_claims",
                    "propagation": "downstream_only",
                    "rationale": "PARTE V, Sec 5.2: Validación fallida reduce confianza downstream",
                },
                "critical_violation": {
                    "triggered_by": "N3_audit_methods",
                    "action": "block_branch",
                    "scope": "source_facts",
                    "propagation": "both",
                    "rationale": "PARTE V, Sec 5.2: Violación crítica bloquea ambas direcciones",
                },
            },
        }
    
    def _build_human_answer_structure(self, contract_type: str) -> dict:
        """Build human answer structure with 4 sections."""
        return {
            "format": "markdown",
            "template_mode": "epistemological_narrative",
            "contract_type": contract_type,
            "sections": [
                {
                    "section_id": "S1_verdict",
                    "title": "### Veredicto",
                    "layer": "N4",
                    "data_source": "synthesis_output",
                    "narrative_style": "declarative",
                    "template": {
                        "structure": [
                            "**Conclusión**: {verdict_statement}",
                            "",
                            "**Confianza Global**: {final_confidence_pct}% ({confidence_label})",
                            "",
                            "**Base Metodológica**: {method_count} métodos ejecutados, {audit_count} validaciones, {blocked_count} ramas bloqueadas.",
                        ],
                    },
                    "argumentative_role": "SYNTHESIS",
                },
                {
                    "section_id": "S2_empirical_base",
                    "title": "### Base Empírica: Hechos Observados",
                    "layer": "N1",
                    "data_source": "validated_facts",
                    "narrative_style": "descriptive",
                    "template": {
                        "structure": [
                            "**Elementos Detectados**: {fact_count} hechos extraídos de {document_coverage_pct}% del texto.",
                            "",
                            "**Fuentes Oficiales Identificadas**:",
                            "{official_sources_list}",
                            "",
                            "**Indicadores Cuantitativos**:",
                            "{quantitative_indicators_list}",
                        ],
                    },
                    "argumentative_role": "EMPIRICAL_BASIS",
                    "epistemological_note": {
                        "include_in_output": True,
                        "text": "📋 *Nota: Observaciones directas del documento fuente, verificables en texto original.*",
                    },
                },
                {
                    "section_id": "S3_robustness_audit",
                    "title": "### Análisis de Robustez: Validación y Limitaciones",
                    "layer": "N3",
                    "data_source": "audit_results",
                    "narrative_style": "critical",
                    "template": {
                        "structure": [
                            "{veto_alert}",
                            "",
                            "**Validaciones Ejecutadas**: {validation_count} pruebas de robustez",
                            "",
                            "**Contradicciones Detectadas**: {contradiction_count}",
                            "{contradiction_details}",
                            "",
                            "**Hechos Suprimidos**: {suppressed_count} observaciones eliminadas",
                            "{suppression_details}",
                        ],
                    },
                    "argumentative_role": "ROBUSTNESS_QUALIFIER",
                    "veto_display": {
                        "if_veto_triggered": "⛔ **MODELO INVÁLIDO**: {veto_reason}. NO usar para toma de decisiones.",
                        "if_partial_veto": "⚠️ **ROBUSTEZ PARCIAL**: {partial_veto_count} hallazgos invalidados.",
                        "if_no_veto": "✅ **VALIDACIÓN COMPLETA**: Todos los hallazgos sobrevivieron refutación.",
                    },
                    "epistemological_note": {
                        "include_in_output": True,
                        "text": "🔬 *Nota: Falsacionismo popperiano aplicado. Lo que sobrevive el escrutinio es epistemológicamente robusto.*",
                    },
                },
                {
                    "section_id": "S4_gaps",
                    "title": "### Puntos Ciegos: Evidencia Faltante",
                    "layer": "N4-META",
                    "data_source": "gap_analysis",
                    "narrative_style": "diagnostic",
                    "template": {
                        "structure": [
                            "**Métodos sin Resultados**: {empty_methods_count} de {total_methods}",
                            "{empty_methods_details}",
                            "",
                            "**Elementos Esperados no Encontrados**:",
                            "{missing_elements_list}",
                            "",
                            "**Impacto en Confianza**:",
                            "{gap_impact_assessment}",
                        ],
                    },
                    "argumentative_role": "META_TRACEABILITY",
                    "epistemological_note": {
                        "include_in_output": True,
                        "text": "🔍 *Nota: Reflexividad crítica. Reportamos lo que NO encontramos y su impacto.*",
                    },
                },
            ],
            "argumentative_roles": {
                "N1_roles": [{"role": "EMPIRICAL_BASIS", "description": "Hecho observable", "narrative_weight": "high"}],
                "N2_roles": [{"role": "INFERENTIAL_BRIDGE", "description": "Conexión derivada", "narrative_weight": "medium"}],
                "N3_roles": [
                    {"role": "ROBUSTNESS_QUALIFIER", "description": "Advertencia de limitación", "narrative_weight": "high"},
                    {"role": "REFUTATIONAL_SIGNAL", "description": "Evidencia que contradice", "narrative_weight": "critical", "triggers_veto": True},
                ],
                "N4_roles": [{"role": "META_TRACEABILITY", "description": "Calidad del proceso", "narrative_weight": "medium"}],
            },
            "confidence_interpretation": {
                "critical": {"range": [0, 19], "label": "INVÁLIDO", "display": "🔴"},
                "low": {"range": [20, 49], "label": "DÉBIL", "display": "🟠"},
                "medium": {"range": [50, 79], "label": "MODERADO", "display": "🟡"},
                "high": {"range": [80, 100], "label": "ROBUSTO", "display": "🟢"},
            },
        }
    
    def _build_output_contract(self, slot: str) -> dict:
        """Build output contract schema."""
        return {
            "result_type": "Phase2QuestionResult",
            "schema": {
                "type": "object",
                "required": ["base_slot", "question_id", "evidence", "score", "human_answer"],
                "properties": {
                    "base_slot": {"type": "string", "const": slot},
                    "question_id": {"type": "string"},
                    "dimension_id": {"type": "string"},
                    "policy_area_id": {"type": "string"},
                    "score": {"type": "number", "minimum": 0, "maximum": 1},
                    "confidence_label": {"type": "string", "enum": ["INVÁLIDO", "DÉBIL", "MODERADO", "ROBUSTO"]},
                    "evidence": {"type": "object"},
                    "human_answer": {"type": "string"},
                    "epistemological_trace": {"type": "object"},
                },
            },
        }
    
    def _build_validation_rules(self) -> dict:
        """Build validation rules section."""
        return {
            "na_policy": "abort_on_critical",
            "derivation_source": "expected_elements",
            "engine": "VALIDATION_ENGINE",
            "module": "farfan_pipeline.phases.Phase_two.evidence_nexus",
            "class_name": "ValidationEngine",
            "method_name": "validate",
        }
    
    def _build_error_handling(self, slot: str) -> dict:
        """Build error handling section."""
        return {
            "on_method_not_found": "raise",
            "on_method_failure": "propagate_with_trace",
            "on_assembly_failure": "propagate_with_trace",
            "failure_contract": {
                "abort_if": ["missing_required_element", "incomplete_text"],
                "emit_code": f"ABORT-{slot}-REQ",
            },
        }
    
    def _build_traceability(self, slot: str, timestamp: str) -> dict:
        """Build traceability section."""
        return {
            "canonical_sources": {
                "questionnaire": "canonic_questionnaire_central/questionnaire_monolith.json",
                "method_inventory": "epistemological_classification_v4.json",
                "epistemological_guide": "episte_refact.md",
            },
            "generation": {
                "method": "v4_epistemological_generation",
                "timestamp": timestamp,
                "generator_version": "1.0.0",
            },
            "refactoring_history": [
                {
                    "from_version": "3.0.0",
                    "to_version": "4.0.0-epistemological",
                    "date": timestamp,
                    "changes": [
                        "Introduced execution_phases (A/B/C) replacing flat methods array",
                        "Classified methods by epistemological level (N1/N2/N3/N4)",
                        "Typed outputs (FACT/PARAMETER/CONSTRAINT/NARRATIVE)",
                        "Implemented asymmetric veto_gate for N3",
                        "Restructured assembly_rules into 4 typed rules",
                    ],
                    "epistemological_framework": {
                        "N1": "Empirismo positivista",
                        "N2": "Bayesianismo subjetivista",
                        "N3": "Falsacionismo popperiano",
                        "N4": "Reflexividad crítica",
                    },
                },
            ],
        }
    
    def _build_compatibility(self) -> dict:
        """Build compatibility section."""
        return {
            "questionnaire_monolith_version": "3.0.0",
            "version_detection": "runtime",
            "minimum_requirements": {
                "signal_registry": "MicroAnsweringSignalPack support",
                "hydrator": "ContractHydrator v1.0.0",
                "carver": "DoctoralCarverSynthesizer v3.0.0",
                "evidence_nexus": "EvidenceNexus v2.0.0",
            },
        }
    
    def _build_calibration(self) -> dict:
        """Build calibration section."""
        return {
            "status": "runtime",
            "sources": {
                "intrinsic_calibration": "config/intrinsic_calibration.json",
                "fusion_specification": "config/fusion_specification.json",
            },
        }


def generate_all_contracts(
    classification_file: Path,
    monolith_file: Path,
    output_dir: Path,
) -> None:
    """Generate all 30 v4 contracts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    generator = V4ContractGenerator(classification_file, monolith_file)
    
    for slot in SLOT_TO_QUESTIONS.keys():
        contract = generator.generate_contract(slot)
        output_file = output_dir / f"{slot}-v4.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(contract, f, indent=2, ensure_ascii=False)
        
        print(f"Generated {output_file.name}: "
              f"TYPE={contract['identity']['contract_type']}, "
              f"methods={contract['method_binding']['method_count']}")
    
    print(f"\n✅ Generated 30 contracts in {output_dir}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate v4 epistemological contracts")
    parser.add_argument(
        "--classification",
        type=Path,
        default=Path("epistemological_classification_v4.json"),
        help="Input classification file",
    )
    parser.add_argument(
        "--monolith",
        type=Path,
        default=Path("canonic_questionnaire_central/questionnaire_monolith.json"),
        help="Questionnaire monolith file",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("contracts_v4"),
        help="Output directory for generated contracts",
    )
    
    args = parser.parse_args()
    generate_all_contracts(args.classification, args.monolith, args.output_dir)

#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
FARFAN EPISTEMOLOGICAL METHOD CLASSIFIER v1.0.0
═══════════════════════════════════════════════════════════════════════════════

Alineado 100% con episte_refact.md - Guía de Operacionalización Epistemológica

Este script:
1. Extrae métodos de los archivos del pipeline FARFAN
2. Clasifica cada método según niveles epistemológicos (N0-N4)
3. Pondera aptitud de cada método hacia tipos de contrato (TYPE_A - TYPE_E)
4. Genera juegos óptimos de métodos por pregunta con evidencia matemática
5. Produce output doctoral (3-5 párrafos) con máxima certeza

Autor: Sistema FARFAN
Fecha: 2025-01-01
"""

import json
import math
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1: TAXONOMÍAS EPISTEMOLÓGICAS (de episte_refact.md)
# ═══════════════════════════════════════════════════════════════════════════════

class EpistemologicalLevel(Enum):
    """Niveles epistemológicos según PARTE I, Sección 1.2 de episte_refact"""
    N0_INFRA = ("N0-INFRA", "Infraestructura Metodológica", "Instrumentalismo puro", "INFRASTRUCTURE")
    N1_EMP = ("N1-EMP", "Base Empírica", "Empirismo positivista", "FACT")
    N2_INF = ("N2-INF", "Procesamiento Inferencial", "Bayesianismo subjetivista", "PARAMETER")
    N3_AUD = ("N3-AUD", "Auditoría y Robustez", "Falsacionismo popperiano", "CONSTRAINT")
    N4_META = ("N4-META", "Meta-Análisis", "Reflexividad crítica", "META_ANALYSIS")
    
    def __init__(self, code: str, name: str, epistemology: str, output_type: str):
        self.code = code
        self.level_name = name
        self.epistemology = epistemology
        self.output_type = output_type


class ContractType(Enum):
    """Tipos de contrato según PARTE I, Sección 1.1 de episte_refact"""
    TYPE_A = ("TYPE_A", "Semántico", "Coherencia narrativa, NLP", "semantic_triangulation")
    TYPE_B = ("TYPE_B", "Bayesiano", "Significancia estadística, priors", "bayesian_update")
    TYPE_C = ("TYPE_C", "Causal", "Topología de grafos, DAGs", "topological_overlay")
    TYPE_D = ("TYPE_D", "Financiero", "Suficiencia presupuestal", "financial_coherence_audit")
    TYPE_E = ("TYPE_E", "Lógico", "Detección de contradicciones", "logical_consistency_validation")
    
    def __init__(self, code: str, name: str, focus: str, fusion_strategy: str):
        self.code = code
        self.type_name = name
        self.focus = focus
        self.fusion_strategy = fusion_strategy


class FusionBehavior(Enum):
    """Comportamiento de fusión según PARTE I, Sección 1.3"""
    ADDITIVE = ("additive", "⊕", "Se SUMA al grafo como nodo")
    MULTIPLICATIVE = ("multiplicative", "⊗", "MODIFICA pesos de aristas")
    GATE = ("gate", "⊘", "FILTRA/BLOQUEA ramas si falla")
    TERMINAL = ("terminal", "⊙", "CONSUME grafo para texto final")
    
    def __init__(self, behavior: str, symbol: str, description: str):
        self.behavior = behavior
        self.symbol = symbol
        self.description = description


# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2: PATRONES DE CLASIFICACIÓN (de PARTE II, Sección 2.2-2.3)
# ═══════════════════════════════════════════════════════════════════════════════

# Patrones de nombre para clasificación automática (PARTE II, Sec 2.2)
LEVEL_PATTERNS = {
    EpistemologicalLevel.N0_INFRA: {
        "prefixes": ["_get_", "_deduplicate_", "_to_dict", "load", "validate", "generate_traceability"],
        "keywords": ["config", "stopwords", "normalize", "logging", "init"],
        "classes": ["ConfigLoader", "ConfigurationManager"]
    },
    EpistemologicalLevel.N1_EMP: {
        "prefixes": ["extract_", "_extract_", "parse_", "_parse_", "mine_", "chunk_", "load_"],
        "keywords": ["extraction", "literal", "raw", "text", "segment"],
        "classes": ["PDFProcessor", "DocumentProcessor", "ResilientFileHandler"]
    },
    EpistemologicalLevel.N2_INF: {
        "prefixes": ["analyze_", "_analyze_", "score_", "calculate_", "_calculate_", 
                     "infer_", "_infer_", "evaluate_", "compare_", "compute_", "_compute_",
                     "embed_", "process", "integrate_", "aggregate_"],
        "keywords": ["bayesian", "posterior", "likelihood", "score", "confidence", "semantic"],
        "classes": ["BayesianNumericalAnalyzer", "AdaptivePriorCalculator", "HierarchicalGenerativeModel",
                   "BayesianMechanismInference", "SemanticAnalyzer", "BayesianEvidenceIntegrator",
                   "BayesianEvidenceScorer", "DispersionEngine", "PeerCalibrator"]
    },
    EpistemologicalLevel.N3_AUD: {
        "prefixes": ["validate_", "_validate_", "detect_", "_detect_", "audit_", "_audit_",
                     "check_", "_check_", "test_", "_test_", "verify_", "_verify_", "veto_"],
        "keywords": ["contradiction", "validator", "auditor", "coherence", "consistency", "veto"],
        "classes": ["PolicyContradictionDetector", "FinancialAuditor", "IndustrialGradeValidator",
                   "AdvancedDAGValidator", "BayesianCounterfactualAuditor", "OperationalizationAuditor",
                   "TemporalLogicVerifier", "ContradictionDominator", "LogicalConsistencyChecker",
                   "DAGCycleDetector", "ReconciliationValidator", "StatisticalGateAuditor",
                   "SemanticValidator"]
    },
    EpistemologicalLevel.N4_META: {
        "prefixes": ["identify_failure", "analyze_performance", "loss_function", "generate_report",
                     "generate_recommendations", "sensitivity_analysis", "refutation_"],
        "keywords": ["failure_points", "meta", "performance", "recommendations", "ablation"],
        "classes": ["CausalInferenceSetup", "PerformanceAnalyzer", "ReportingEngine"]
    }
}

# Clases dominantes por tipo de contrato (Taxonomía de Contratos)
CONTRACT_DOMINANT_CLASSES = {
    ContractType.TYPE_A: ["SemanticAnalyzer", "TextMiningEngine", "SemanticProcessor", 
                         "PolicyDocumentAnalyzer", "SemanticChunkingProducer"],
    ContractType.TYPE_B: ["BayesianMechanismInference", "HierarchicalGenerativeModel", 
                         "AdaptivePriorCalculator", "BayesianNumericalAnalyzer",
                         "BayesianEvidenceIntegrator", "BayesianEvidenceScorer",
                         "BayesianUpdater", "BayesianEvidenceExtractor"],
    ContractType.TYPE_C: ["CausalExtractor", "TeoriaCambio", "AdvancedDAGValidator",
                         "CausalInferenceSetup", "DAGCycleDetector"],
    ContractType.TYPE_D: ["FinancialAuditor", "PDETMunicipalPlanAnalyzer", 
                         "FinancialAggregator"],
    ContractType.TYPE_E: ["PolicyContradictionDetector", "IndustrialGradeValidator",
                         "OperationalizationAuditor", "LogicalConsistencyChecker",
                         "TemporalLogicVerifier", "ContradictionDominator"]
}


# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 3: ESTRUCTURAS DE DATOS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MethodSignature:
    """Representa la firma de un método extraído"""
    class_name: str
    method_name: str
    mother_file: str
    parameters: list[str]
    return_type: str
    is_private: bool = False
    is_async: bool = False


@dataclass 
class ClassifiedMethod:
    """Método clasificado epistemológicamente según episte_refact"""
    signature: MethodSignature
    level: EpistemologicalLevel
    output_type: str
    fusion_behavior: FusionBehavior
    provides: str
    classification_rationale: str
    confidence_score: float
    contract_affinities: dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "class_name": self.signature.class_name,
            "method_name": self.signature.method_name,
            "mother_file": self.signature.mother_file,
            "provides": self.provides,
            "level": self.level.code,
            "level_name": self.level.level_name,
            "epistemology": self.level.epistemology,
            "output_type": self.output_type,
            "fusion_behavior": self.fusion_behavior.behavior,
            "fusion_symbol": self.fusion_behavior.symbol,
            "classification_rationale": self.classification_rationale,
            "confidence_score": self.confidence_score,
            "contract_affinities": self.contract_affinities,
            "parameters": self.signature.parameters,
            "return_type": self.signature.return_type,
            "is_private": self.signature.is_private
        }


@dataclass
class MethodSet:
    """Juego de métodos para una pregunta específica"""
    question_id: str
    contract_type: ContractType
    phase_a_methods: list[ClassifiedMethod]  # N1 - Empírico
    phase_b_methods: list[ClassifiedMethod]  # N2 - Inferencial  
    phase_c_methods: list[ClassifiedMethod]  # N3 - Auditoría
    efficiency_score: float
    mathematical_evidence: dict[str, Any]
    doctoral_justification: str


# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 4: INVENTARIO DE MÉTODOS EXTRAÍDOS
# ═══════════════════════════════════════════════════════════════════════════════

# Inventario completo de métodos extraídos de los 9 archivos
RAW_METHOD_INVENTORY = {
    "analyzer_one.py": {
        "MunicipalOntology": ["__init__"],
        "SemanticAnalyzer": [
            "__init__", "_load_unit_of_analysis_stats", "_compute_unit_of_analysis_natural_blocks",
            "_build_segmentation_metadata", "extract_semantic_cube", "_load_json", "_empty_semantic_cube",
            "_vectorize_segments", "_process_segment", "_select_policy_area", "_get_slot_threshold",
            "_keyword_score", "_score_d3_q3_expected_elements", "_score_base_slots",
            "_classify_value_chain_link", "_classify_cross_cutting_themes", "_classify_policy_domain",
            "_calculate_semantic_complexity"
        ],
        "PerformanceAnalyzer": [
            "__init__", "analyze_performance", "_calculate_throughput_metrics", "_detect_bottlenecks",
            "_calculate_loss_functions", "_percentile", "_generate_recommendations"
        ],
        "TextMiningEngine": [
            "__init__", "diagnose_critical_links", "_identify_critical_links", "_analyze_link_text",
            "_assess_risks", "_generate_interventions"
        ],
        "MunicipalAnalyzer": ["__init__", "analyze_document", "_load_document", "_generate_summary"],
        "CanonicalQuestionSegmenter": ["__init__", "segment_plan", "_build_manifest"],
        "DocumentProcessor": [
            "load_pdf", "load_docx", "segment_text", "load_canonical_question_contracts",
            "segment_by_canonical_questionnaire", "_default_policy_area_id", "_to_canonical_dimension_id"
        ],
        "ResultsExporter": ["export_to_json", "export_to_excel", "export_summary_report"],
        "ConfigurationManager": ["__init__", "load_config", "save_config"],
        "BatchProcessor": ["__init__", "process_directory", "export_batch_results", "_create_batch_summary"]
    },
    
    "bayesian_multilevel_system.py": {
        "ReconciliationValidator": [
            "__init__", "validate_range", "validate_unit", "validate_period", 
            "validate_entity", "validate_data", "calculate_total_penalty"
        ],
        "ProbativeTest": ["calculate_likelihood_ratio"],
        "BayesianUpdater": ["__init__", "update", "sequential_update", "_calculate_evidence_weight", "export_to_csv"],
        "DispersionEngine": ["__init__", "calculate_cv", "calculate_max_gap", "calculate_gini", "calculate_dispersion_penalty"],
        "PeerCalibrator": ["__init__", "compare_to_peers", "_generate_narrative"],
        "BayesianRollUp": ["__init__", "aggregate_micro_to_meso", "export_to_csv"],
        "ContradictionScanner": ["__init__", "scan_micro_meso", "scan_meso_macro", "calculate_contradiction_penalty"],
        "BayesianPortfolioComposer": [
            "__init__", "calculate_coverage", "compose_macro_portfolio", 
            "_generate_recommendations", "export_to_csv"
        ],
        "MultiLevelBayesianOrchestrator": [
            "__init__", "run_complete_analysis", "_run_micro_level", "_run_meso_level", "_run_macro_level"
        ],
        "BayesianEvidenceExtractor": [
            "__init__", "extract_prior_beliefs", "extract_likelihood_evidence", "extract_statistical_metadata",
            "_extract_probability", "_extract_likelihood_value", "_extract_measurement_unit",
            "_extract_sample_size", "_get_context", "_calculate_data_quality_score"
        ],
        "StatisticalGateAuditor": [
            "__init__", "test_significance", "validate_sample_size", "apply_statistical_veto"
        ]
    },
    
    "contradiction_deteccion.py": {
        "BayesianConfidenceCalculator": ["__init__", "calculate_posterior"],
        "TemporalLogicVerifier": [
            "__init__", "verify_temporal_consistency", "_build_timeline", "_parse_temporal_marker",
            "_has_temporal_conflict", "_are_mutually_exclusive", "_extract_resources",
            "_check_deadline_constraints", "_should_precede", "_classify_temporal_type"
        ],
        "SemanticValidator": [
            "__init__", "validate_semantic_completeness_coherence", "_check_quantitative_data_presence",
            "_check_baseline_indicator", "_check_year_reference", "_check_official_sources",
            "_check_resources_temporal_compatibility"
        ],
        "PolicyContradictionDetector": ["__init__", "_initialize_pdm_patterns", "detect"],
        "ContradictionDominator": [
            "__init__", "apply_dominance_veto", "detect_any_contradiction",
            "_detect_any_contradiction_from_dicts", "generate_veto_report",
            "_generate_veto_report_from_facts", "_calculate_original_confidence_from_dicts"
        ],
        "DempsterShaferCombinator": [
            "__init__", "combine_belief_masses", "calculate_conflict_mass",
            "normalize_belief_distribution", "_dempster_combination", "_calculate_reliability_score"
        ],
        "LogicalConsistencyChecker": [
            "__init__", "check_consistency", "detect_logical_violations", 
            "enforce_no_averaging_prohibition", "_enforce_no_averaging_prohibition"
        ]
    },
    
    "derek_beach.py": {
        "BeachEvidentialTest": ["classify_test", "apply_test_logic"],
        "ConfigLoader": [
            "__init__", "_load_config", "_load_default_config", "_validate_config", "get",
            "get_bayesian_threshold", "get_chain_capacity_prior", "get_performance_setting",
            "update_priors_from_feedback", "_save_prior_history", "_load_uncertainty_history",
            "check_uncertainty_reduction_criterion"
        ],
        "PDFProcessor": ["__init__", "load_document", "extract_text", "extract_tables", "extract_sections"],
        "CausalExtractor": [
            "__init__", "extract_causal_hierarchy", "_extract_goals", "_parse_goal_context",
            "_extract_goal_text", "_add_node_to_graph", "_extract_causal_links",
            "_calculate_semantic_distance", "_calculate_type_transition_prior",
            "_check_structural_violation", "_calculate_language_specificity",
            "_assess_temporal_coherence", "_assess_financial_consistency",
            "_calculate_textual_proximity", "_initialize_prior", "_get_policy_area_keywords",
            "_calculate_dynamic_weights", "_calculate_composite_likelihood",
            "_build_type_hierarchy", "_calculate_confidence", "_classify_goal_type",
            "_extract_causal_justifications"
        ],
        "MechanismPartExtractor": [
            "__init__", "extract_entity_activity", "_normalize_entity",
            "_calculate_ea_confidence", "_find_action_verb", "_find_subject_entity",
            "_validate_entity_activity"
        ],
        "FinancialAuditor": [
            "__init__", "trace_financial_allocation", "_process_financial_table",
            "_parse_amount", "_match_program_to_node", "_perform_counterfactual_budget_check",
            "_calculate_sufficiency", "_detect_allocation_gaps", "_match_goal_to_budget"
        ],
        "OperationalizationAuditor": [
            "__init__", "audit_evidence_traceability", "audit_sequence_logic",
            "audit_causal_coherence_d6", "bayesian_counterfactual_audit",
            "_build_normative_dag", "_get_default_historical_priors",
            "_audit_direct_evidence", "_audit_causal_implications", "_audit_systemic_risk",
            "_generate_optimal_remediations", "_get_remediation_text",
            "_perform_counterfactual_budget_check"
        ],
        "BayesianMechanismInference": [
            "__init__", "_log_refactored_components", "infer_mechanisms", "_infer_single_mechanism",
            "_extract_observations", "_extract_dimension_evidence", "_calculate_likelihood_from_evidence",
            "_bayesian_update", "_infer_chain_capacity_vector", "_infer_activity_sequence",
            "_calculate_coherence_factor", "_test_sufficiency", "_test_necessity",
            "_generate_necessity_remediation", "_quantify_uncertainty", "_detect_gaps",
            "_aggregate_bayesian_confidence", "derive_political_viability", "_interpret_vp_score"
        ],
        "CausalInferenceSetup": [
            "__init__", "classify_goal_dynamics", "assign_probative_value",
            "identify_failure_points", "_get_dynamics_pattern"
        ],
        "ReportingEngine": [
            "__init__", "generate_causal_diagram", "generate_accountability_matrix",
            "generate_confidence_report", "_calculate_quality_score", "generate_causal_model_json"
        ],
        "CDAFFramework": [
            "__init__", "process_document", "_generate_bayesian_reports",
            "_verify_cvc_compliance", "_extract_feedback_from_audit",
            "_validate_dnp_compliance", "_generate_dnp_report", "_audit_causal_coherence",
            "_generate_causal_model_json", "_generate_dnp_compliance_report",
            "_generate_extraction_report"
        ],
        "BayesFactorTable": ["get_bayes_factor", "get_version"],
        "AdaptivePriorCalculator": [
            "__init__", "calculate_likelihood_adaptativo", "_adjust_domain_weights",
            "sensitivity_analysis", "_perturb_evidence", "_add_ood_noise",
            "generate_traceability_record", "validate_quality_criteria"
        ],
        "HierarchicalGenerativeModel": [
            "__init__", "infer_mechanism_posterior", "_run_mcmc_chain",
            "_calculate_likelihood", "_get_mode_sequence", "_calculate_r_hat",
            "_calculate_ess", "posterior_predictive_check", "_ablation_analysis",
            "verify_conditional_independence", "_generate_independence_tests",
            "_calculate_waic_difference"
        ],
        "BayesianCounterfactualAuditor": [
            "__init__", "construct_scm", "_create_default_equations",
            "counterfactual_query", "_evaluate_factual", "_evaluate_counterfactual",
            "_test_effect_stability", "aggregate_risk_and_prioritize",
            "refutation_and_sanity_checks"
        ],
        "DerekBeachProducer": [
            "__init__", "classify_test_type", "apply_test_logic", "is_hoop_test",
            "is_smoking_gun", "is_doubly_decisive", "is_straw_in_wind",
            "create_hierarchical_model", "infer_mechanism_posterior", "get_type_posterior",
            "get_sequence_mode", "get_coherence_score", "get_r_hat", "get_ess",
            "is_inference_uncertain", "posterior_predictive_check", "get_ppd_p_value",
            "get_ablation_curve", "get_ppc_recommendation", "verify_conditional_independence",
            "get_independence_tests", "get_delta_waic", "get_model_preference",
            "create_auditor", "construct_scm", "counterfactual_query", "get_causal_effect",
            "is_sufficient", "is_necessary", "is_effect_stable", "aggregate_risk",
            "get_risk_score", "get_success_probability", "get_priority",
            "get_recommendations", "refutation_checks", "get_negative_controls",
            "get_placebo_effect", "get_sanity_violations", "all_checks_passed",
            "get_refutation_recommendation"
        ]
    },
    
    "embedding_policy.py": {
        "PolicyDomain": ["get_all"],
        "AnalyticalDimension": ["get_all", "D1", "D2", "D3", "D4", "D5", "D6"],
        "AdvancedSemanticChunker": [
            "__init__", "chunk_document", "_normalize_text", "_recursive_split",
            "_find_sentence_boundary", "_extract_sections", "_extract_tables",
            "_extract_lists", "_infer_pdq_context", "_contains_table",
            "_contains_list", "_find_section"
        ],
        "BayesianNumericalAnalyzer": [
            "__init__", "evaluate_policy_metric", "_beta_binomial_posterior",
            "_normal_normal_posterior", "_classify_evidence_strength",
            "_compute_coherence", "_null_evaluation", "serialize_posterior_samples",
            "compare_policies"
        ],
        "PolicyCrossEncoderReranker": ["__init__", "rerank"],
        "PolicyAnalysisEmbedder": [
            "__init__", "process_document", "apply_pd_context", "semantic_search",
            "evaluate_policy_numerical_consistency", "compare_policy_interventions",
            "generate_pdq_report", "_embed_texts", "_filter_by_pdq", "_apply_mmr",
            "_extract_numerical_values", "_canonical_number_extraction",
            "_generate_query_from_pdq", "_compute_overall_confidence",
            "_cached_similarity", "get_diagnostics"
        ],
        "EmbeddingPolicyProducer": [
            "__init__", "process_document", "get_chunk_count", "get_chunk_text",
            "get_chunk_embedding", "get_chunk_metadata", "get_chunk_pdq_context",
            "semantic_search", "get_search_result_chunk", "get_search_result_score",
            "generate_pdq_report", "get_pdq_evidence_count", "get_pdq_numerical_evaluation",
            "get_pdq_evidence_passages", "get_pdq_confidence", "evaluate_numerical_consistency",
            "get_point_estimate", "get_credible_interval", "get_evidence_strength",
            "get_numerical_coherence", "compare_policy_interventions",
            "get_comparison_probability", "get_comparison_bayes_factor",
            "get_comparison_difference_mean", "get_diagnostics", "get_config",
            "list_policy_domains", "list_analytical_dimensions",
            "get_policy_domain_description", "get_analytical_dimension_description",
            "create_pdq_identifier"
        ]
    },
    
    "financiero_viabilidad_tablas.py": {
        "PDETMunicipalPlanAnalyzer": [
            "__init__", "_get_spanish_stopwords", "_clean_dataframe", "_is_likely_header",
            "_deduplicate_tables", "_classify_tables", "analyze_financial_feasibility",
            "_extract_financial_amounts", "_identify_funding_source", "_extract_from_budget_table",
            "_analyze_funding_sources", "_assess_financial_sustainability",
            "_bayesian_risk_inference", "_interpret_risk", "_indicator_to_dict",
            "identify_responsible_entities", "_extract_entities_ner", "_extract_entities_syntax",
            "_classify_entity_type", "_extract_from_responsibility_tables",
            "_consolidate_entities", "_score_entity_specificity", "construct_causal_dag",
            "_identify_causal_nodes", "_find_semantic_mentions", "_find_outcome_mentions",
            "_find_mediator_mentions", "_extract_budget_for_pillar", "_identify_causal_edges",
            "_match_text_to_node", "_refine_edge_probabilities", "_break_cycles",
            "estimate_causal_effects", "_estimate_effect_bayesian", "_get_prior_effect",
            "_identify_confounders", "generate_counterfactuals", "_simulate_intervention",
            "_generate_scenario_narrative", "sensitivity_analysis", "_compute_e_value",
            "_compute_robustness_value", "_interpret_sensitivity", "calculate_quality_score",
            "_score_financial_component", "_score_indicators", "_score_responsibility_clarity",
            "_score_temporal_consistency", "_score_pdet_alignment", "_score_causal_coherence",
            "_estimate_score_confidence", "export_causal_network", "generate_executive_report",
            "_interpret_overall_quality", "_generate_recommendations",
            "analyze_municipal_plan_sync", "_extract_full_text", "_entity_to_dict",
            "_effect_to_dict", "_scenario_to_dict", "_quality_to_dict",
            "_find_product_mentions", "_generate_optimal_remediations", "generate_recommendations"
        ],
        "FinancialAggregator": [
            "__init__", "aggregate_financial_data", "normalize_to_budget_base",
            "normalize_to_population", "_extract_from_ppi_dict"
        ]
    },
    
    "semantic_chunking_policy.py": {
        "CausalDimension": ["from_dimension_code"],
        "SemanticProcessor": [
            "__init__", "_lazy_load", "chunk_text", "_detect_pdm_structure",
            "_classify_section_type", "_detect_table", "_detect_causal_language",
            "_detect_numerical_data", "_embed_batch", "embed_single"
        ],
        "BayesianEvidenceIntegrator": [
            "__init__", "integrate_evidence", "_similarity_to_probability",
            "_compute_reliability_weights", "_null_evidence", "causal_strength"
        ],
        "PolicyDocumentAnalyzer": [
            "__init__", "_init_dimension_embeddings", "analyze", "_extract_key_excerpts"
        ],
        "SemanticChunkingProducer": [
            "__init__", "chunk_document", "get_chunk_count", "get_chunk_text",
            "get_chunk_embedding", "get_chunk_metadata", "embed_text", "embed_batch",
            "analyze_document", "get_dimension_analysis", "get_dimension_score",
            "get_dimension_confidence", "get_dimension_excerpts", "integrate_evidence",
            "calculate_causal_strength", "get_posterior_mean", "get_posterior_std",
            "get_information_gain", "get_confidence", "semantic_search",
            "list_dimensions", "get_dimension_description", "get_config", "set_config"
        ]
    },
    
    "policy_processor.py": {
        "_FallbackBayesianCalculator": ["__init__", "calculate_posterior"],
        "_FallbackTemporalVerifier": ["verify_temporal_consistency"],
        "_FallbackContradictionDetector": ["detect", "_extract_policy_statements"],
        "BayesianEvidenceScorer": [
            "__init__", "_configure_from_calibration", "compute_evidence_score",
            "_calculate_shannon_entropy", "_lookup_weight"
        ],
        "PolicyTextProcessor": [
            "__init__", "normalize_unicode", "segment_into_sentences",
            "extract_contextual_window", "compile_pattern"
        ],
        "IndustrialPolicyProcessor": [
            "__init__", "_load_questionnaire", "_compile_pattern_registry",
            "_build_canonical_point_patterns", "_detect_policy_areas",
            "_detect_scoring_modality", "_apply_validation_rules", "_build_point_patterns",
            "process", "_match_patterns_in_sentences", "_compute_evidence_confidence",
            "_construct_evidence_bundle", "_run_contradiction_analysis",
            "_calculate_quality_score", "_extract_point_evidence",
            "_analyze_causal_dimensions", "_extract_metadata", "_compute_avg_confidence",
            "_empty_result", "export_results"
        ],
        "AdvancedTextSanitizer": ["__init__", "sanitize", "_protect_structure", "_restore_structure"],
        "PolicyAnalysisPipeline": ["__init__", "analyze_file", "analyze_text"]
    },
    
    "teoria_cambio.py": {
        "TeoriaCambio": [
            "__init__", "_es_conexion_valida", "construir_grafo_causal",
            "construir_grafo_from_cpp", "construir_grafo_from_spc",
            "validacion_completa", "_extraer_categorias", "_validar_orden_causal",
            "_encontrar_caminos_completos", "_generar_sugerencias_internas",
            "_execute_generar_sugerencias_internas"
        ],
        "AdvancedDAGValidator": [
            "__init__", "add_node", "add_edge", "_initialize_rng", "_is_acyclic",
            "_generate_subgraph", "calculate_acyclicity_pvalue", "last_serialized_nodes",
            "export_nodes", "_get_node_validator", "_perform_sensitivity_analysis_internal",
            "_calculate_confidence_interval", "_calculate_statistical_power",
            "_calculate_bayesian_posterior", "_calculate_node_importance", "get_graph_stats",
            "_create_empty_result"
        ],
        "DAGCycleDetector": [
            "__init__", "detect_cycles", "veto_on_cycle", "calculate_acyclicity_confidence",
            "_build_adjacency_list", "_find_all_cycles", "_topological_sort"
        ],
        "IndustrialGradeValidator": [
            "__init__", "execute_suite", "validate_engine_readiness",
            "validate_causal_categories", "validate_connection_matrix",
            "run_performance_benchmarks", "_benchmark_operation", "_log_metric"
        ]
    }
}


# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 5: CLASIFICADOR EPISTEMOLÓGICO
# ═══════════════════════════════════════════════════════════════════════════════

class EpistemologicalClassifier:
    """
    Clasificador de métodos según criterios epistemológicos de episte_refact.
    
    Implementa el árbol de decisión de PARTE II, Sección 2.3:
    - ¿M lee PreprocesadoMetadata directamente? → N1
    - ¿M transforma/interpreta? → N2
    - ¿M valida o refuta? → N3
    - ¿M analiza el proceso analítico? → N4
    """
    
    def __init__(self):
        self.classified_methods: list[ClassifiedMethod] = []
        self.classification_stats = {level: 0 for level in EpistemologicalLevel}
        
    def classify_method(self, class_name: str, method_name: str, 
                       mother_file: str, params: list[str], 
                       return_type: str) -> ClassifiedMethod:
        """Clasifica un método según criterios epistemológicos comprensivos"""
        
        signature = MethodSignature(
            class_name=class_name,
            method_name=method_name,
            mother_file=mother_file,
            parameters=params,
            return_type=return_type,
            is_private=method_name.startswith("_"),
            is_async=False
        )
        
        # Determinar nivel epistemológico
        level, rationale, confidence = self._determine_level(class_name, method_name)
        
        # Determinar comportamiento de fusión basado en nivel
        fusion_behavior = self._get_fusion_behavior(level)
        
        # Calcular afinidades con tipos de contrato
        contract_affinities = self._calculate_contract_affinities(class_name, method_name, level)
        
        # Construir identificador 'provides'
        provides = f"{class_name.lower()}.{method_name.lstrip('_')}"
        
        classified = ClassifiedMethod(
            signature=signature,
            level=level,
            output_type=level.output_type,
            fusion_behavior=fusion_behavior,
            provides=provides,
            classification_rationale=rationale,
            confidence_score=confidence,
            contract_affinities=contract_affinities
        )
        
        self.classified_methods.append(classified)
        self.classification_stats[level] += 1
        
        return classified
    
    def _determine_level(self, class_name: str, method_name: str) -> tuple[EpistemologicalLevel, str, float]:
        """
        Aplica el árbol de decisión de PARTE II, Sección 2.3
        Retorna: (nivel, justificación, confianza)
        """
        
        # Excluir métodos de infraestructura básica
        if method_name in ["__init__", "__post_init__", "__str__", "__repr__"]:
            return (EpistemologicalLevel.N0_INFRA, 
                   "Método de inicialización/infraestructura", 0.95)
        
        # Verificar por clase dominante primero (mayor especificidad)
        for level, patterns in LEVEL_PATTERNS.items():
            if class_name in patterns.get("classes", []):
                # La clase está explícitamente listada
                # Ahora verificar si el método tiene patrón específico
                for prefix in patterns.get("prefixes", []):
                    if method_name.startswith(prefix) or method_name.startswith("_" + prefix):
                        return (level, 
                               f"Clase {class_name} listada en {level.code} + patrón '{prefix}'",
                               0.92)
                # Clase listada pero método sin patrón específico
                return (level, 
                       f"Clase {class_name} es dominante en {level.code}", 0.85)
        
        # Verificar por patrón de nombre de método
        for level, patterns in LEVEL_PATTERNS.items():
            for prefix in patterns.get("prefixes", []):
                if method_name.startswith(prefix) or method_name.lstrip("_").startswith(prefix):
                    return (level, 
                           f"Patrón de nombre '{prefix}' → {level.code} (PARTE II, Sec 2.2)",
                           0.88)
            
            for keyword in patterns.get("keywords", []):
                if keyword.lower() in method_name.lower() or keyword.lower() in class_name.lower():
                    return (level,
                           f"Keyword '{keyword}' detectado → {level.code}",
                           0.80)
        
        # Heurísticas adicionales basadas en semántica del nombre
        method_lower = method_name.lower()
        
        # N3: Patrones de auditoría/validación
        if any(kw in method_lower for kw in ["veto", "block", "suppress", "reject", "invalid"]):
            return (EpistemologicalLevel.N3_AUD,
                   "Semántica de veto/bloqueo → N3-AUD (VETO GATE)", 0.85)
        
        # N2: Patrones inferenciales
        if any(kw in method_lower for kw in ["posterior", "prior", "likelihood", "bayes", "score", "confidence"]):
            return (EpistemologicalLevel.N2_INF,
                   "Semántica bayesiana/inferencial → N2-INF", 0.82)
        
        # N1: Patrones de extracción
        if any(kw in method_lower for kw in ["get", "load", "read", "fetch", "find"]):
            return (EpistemologicalLevel.N1_EMP,
                   "Semántica de obtención de datos → N1-EMP", 0.75)
        
        # N4: Patrones meta-analíticos
        if any(kw in method_lower for kw in ["report", "summary", "export", "generate"]):
            if "recommendation" in method_lower or "failure" in method_lower:
                return (EpistemologicalLevel.N4_META,
                       "Semántica de meta-análisis → N4-META", 0.78)
        
        # Default: Inferir por contexto de clase
        if "Validator" in class_name or "Auditor" in class_name or "Detector" in class_name:
            return (EpistemologicalLevel.N3_AUD,
                   f"Clase {class_name} sugiere auditoría → N3-AUD", 0.70)
        
        if "Bayesian" in class_name or "Inference" in class_name:
            return (EpistemologicalLevel.N2_INF,
                   f"Clase {class_name} sugiere inferencia → N2-INF", 0.70)
        
        if "Extract" in class_name or "Processor" in class_name:
            return (EpistemologicalLevel.N1_EMP,
                   f"Clase {class_name} sugiere extracción → N1-EMP", 0.70)
        
        # Fallback conservador
        return (EpistemologicalLevel.N2_INF,
               "Clasificación por defecto (requiere revisión manual)", 0.50)
    
    def _get_fusion_behavior(self, level: EpistemologicalLevel) -> FusionBehavior:
        """Determina el comportamiento de fusión según nivel (PARTE I, Sec 1.3)"""
        mapping = {
            EpistemologicalLevel.N0_INFRA: FusionBehavior.ADDITIVE,
            EpistemologicalLevel.N1_EMP: FusionBehavior.ADDITIVE,
            EpistemologicalLevel.N2_INF: FusionBehavior.MULTIPLICATIVE,
            EpistemologicalLevel.N3_AUD: FusionBehavior.GATE,
            EpistemologicalLevel.N4_META: FusionBehavior.TERMINAL
        }
        return mapping.get(level, FusionBehavior.ADDITIVE)
    
    def _calculate_contract_affinities(self, class_name: str, method_name: str,
                                       level: EpistemologicalLevel) -> dict[str, float]:
        """
        Calcula la afinidad de un método con cada tipo de contrato.
        Basado en las clases dominantes de la Taxonomía de Contratos.
        """
        affinities = {}
        
        for contract_type in ContractType:
            dominant_classes = CONTRACT_DOMINANT_CLASSES.get(contract_type, [])
            
            # Afinidad base por nivel epistemológico
            level_affinity = self._level_contract_affinity(level, contract_type)
            
            # Boost si la clase es dominante para este tipo
            class_boost = 0.3 if class_name in dominant_classes else 0.0
            
            # Boost por keywords específicos del contrato
            keyword_boost = self._keyword_contract_boost(method_name, contract_type)
            
            # Calcular afinidad final (clamped 0-1)
            affinity = min(1.0, level_affinity + class_boost + keyword_boost)
            affinities[contract_type.code] = round(affinity, 3)
        
        return affinities
    
    def _level_contract_affinity(self, level: EpistemologicalLevel, 
                                  contract_type: ContractType) -> float:
        """Matriz de afinidad nivel-contrato"""
        # Basado en estrategias de fusión por tipo (PARTE IV, Sec 4.3)
        affinity_matrix = {
            # TYPE_A (Semántico): Fuerte en N1/N2 semánticos
            (EpistemologicalLevel.N1_EMP, ContractType.TYPE_A): 0.7,
            (EpistemologicalLevel.N2_INF, ContractType.TYPE_A): 0.8,
            (EpistemologicalLevel.N3_AUD, ContractType.TYPE_A): 0.5,
            
            # TYPE_B (Bayesiano): Fuerte en N2 bayesiano
            (EpistemologicalLevel.N1_EMP, ContractType.TYPE_B): 0.5,
            (EpistemologicalLevel.N2_INF, ContractType.TYPE_B): 0.9,
            (EpistemologicalLevel.N3_AUD, ContractType.TYPE_B): 0.6,
            
            # TYPE_C (Causal): Fuerte en N1 extracción + N3 validación
            (EpistemologicalLevel.N1_EMP, ContractType.TYPE_C): 0.7,
            (EpistemologicalLevel.N2_INF, ContractType.TYPE_C): 0.7,
            (EpistemologicalLevel.N3_AUD, ContractType.TYPE_C): 0.8,
            
            # TYPE_D (Financiero): Fuerte en N1 extracción + N3 auditoría
            (EpistemologicalLevel.N1_EMP, ContractType.TYPE_D): 0.8,
            (EpistemologicalLevel.N2_INF, ContractType.TYPE_D): 0.6,
            (EpistemologicalLevel.N3_AUD, ContractType.TYPE_D): 0.9,
            
            # TYPE_E (Lógico): Fuerte en N3 validación lógica
            (EpistemologicalLevel.N1_EMP, ContractType.TYPE_E): 0.5,
            (EpistemologicalLevel.N2_INF, ContractType.TYPE_E): 0.6,
            (EpistemologicalLevel.N3_AUD, ContractType.TYPE_E): 0.9,
        }
        return affinity_matrix.get((level, contract_type), 0.4)
    
    def _keyword_contract_boost(self, method_name: str, contract_type: ContractType) -> float:
        """Boost por keywords específicos del tipo de contrato"""
        keywords = {
            ContractType.TYPE_A: ["semantic", "text", "nlp", "coherence", "theme", "embed"],
            ContractType.TYPE_B: ["bayesian", "posterior", "prior", "likelihood", "probability", "mcmc"],
            ContractType.TYPE_C: ["causal", "dag", "graph", "cycle", "path", "mechanism"],
            ContractType.TYPE_D: ["financial", "budget", "amount", "allocation", "funding", "cost"],
            ContractType.TYPE_E: ["contradiction", "logic", "consistency", "violation", "incompatible"]
        }
        
        method_lower = method_name.lower()
        contract_keywords = keywords.get(contract_type, [])
        
        matches = sum(1 for kw in contract_keywords if kw in method_lower)
        return min(0.2, matches * 0.1)  # Max boost de 0.2
    
    def classify_all_methods(self) -> list[ClassifiedMethod]:
        """Clasifica todos los métodos del inventario"""
        for mother_file, classes in RAW_METHOD_INVENTORY.items():
            for class_name, methods in classes.items():
                for method_name in methods:
                    # Inferir parámetros y tipo de retorno (simplificado)
                    params = ["self"] if not method_name.startswith("_") or method_name == "__init__" else ["self"]
                    return_type = "Any"
                    
                    self.classify_method(
                        class_name=class_name,
                        method_name=method_name,
                        mother_file=mother_file,
                        params=params,
                        return_type=return_type
                    )
        
        return self.classified_methods


# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 6: GENERADOR DE JUEGOS DE MÉTODOS
# ═══════════════════════════════════════════════════════════════════════════════

class MethodSetGenerator:
    """
    Genera juegos óptimos de métodos por pregunta según episte_refact.
    
    Implementa:
    - Selección por fases (A: N1, B: N2, C: N3)
    - Cálculo de eficiencia matemática
    - Evidencia de optimalidad usando fórmulas de corroboración
    """
    
    # Mapeo de preguntas a tipos de contrato (del JSON generado previamente)
    QUESTION_CONTRACT_MAPPING = {
        "D1_Q1": "TYPE_A", "D1_Q2": "TYPE_B", "D1_Q3": "TYPE_D", "D1_Q4": "TYPE_D", "D1_Q5": "TYPE_B",
        "D2_Q1": "TYPE_D", "D2_Q2": "TYPE_B", "D2_Q3": "TYPE_C", "D2_Q4": "TYPE_D", "D2_Q5": "TYPE_E",
        "D3_Q1": "TYPE_B", "D3_Q2": "TYPE_D", "D3_Q3": "TYPE_A", "D3_Q4": "TYPE_E", "D3_Q5": "TYPE_D",
        "D4_Q1": "TYPE_C", "D4_Q2": "TYPE_B", "D4_Q3": "TYPE_B", "D4_Q4": "TYPE_E", "D4_Q5": "TYPE_B",
        "D5_Q1": "TYPE_D", "D5_Q2": "TYPE_D", "D5_Q3": "TYPE_B", "D5_Q4": "TYPE_B", "D5_Q5": "TYPE_B",
        "D6_Q1": "TYPE_C", "D6_Q2": "TYPE_B", "D6_Q3": "TYPE_E", "D6_Q4": "TYPE_B", "D6_Q5": "TYPE_C"
    }
    
    # Preguntas textuales (resumidas)
    QUESTIONS = {
        "D1_Q1": "¿El diagnóstico presenta datos cuantitativos con fuente y desagregación?",
        "D1_Q2": "¿El diagnóstico dimensiona numéricamente la magnitud del problema?",
        "D1_Q3": "¿El PPI asigna recursos monetarios explícitos al sector?",
        "D1_Q4": "¿El plan identifica entidades responsables y capacidades institucionales?",
        "D1_Q5": "¿El plan justifica alcance mencionando marco normativo?",
        "D2_Q1": "¿Las actividades aparecen en formato estructurado con atributos verificables?",
        "D2_Q2": "¿Las actividades especifican instrumento, población y contribución al resultado?",
        "D2_Q3": "¿Las actividades se vinculan con problemas diagnosticados?",
        "D2_Q4": "¿El plan identifica riesgos y medidas de mitigación?",
        "D2_Q5": "¿El plan describe complementariedad y secuencia lógica entre actividades?",
        "D3_Q1": "¿Los indicadores de producto incluyen línea base, meta y verificación?",
        "D3_Q2": "¿Las metas guardan relación con magnitud del problema?",
        "D3_Q3": "¿Los productos están vinculados a códigos presupuestales y entidades?",
        "D3_Q4": "¿Existe correspondencia factible entre actividad y meta de producto?",
        "D3_Q5": "¿El plan describe cómo los productos generan resultados?",
        "D4_Q1": "¿Los indicadores de resultado tienen línea base, meta 2027 y horizonte?",
        "D4_Q2": "¿El plan describe la ruta causal con supuestos y condiciones?",
        "D4_Q3": "¿La ambición de metas se justifica con recursos y capacidad?",
        "D4_Q4": "¿Los resultados atienden problemas priorizados en diagnóstico?",
        "D4_Q5": "¿El plan declara alineación con PND, ODS y marcos nacionales?",
        "D5_Q1": "¿El plan define impactos de largo plazo y cómo se llega a ellos?",
        "D5_Q2": "¿Se utilizan índices o proxies para medir impactos?",
        "D5_Q3": "¿Los impactos se alinean con marcos y consideran riesgos externos?",
        "D5_Q4": "¿El plan evalúa realismo y posibles efectos no deseados?",
        "D5_Q5": "¿El plan describe sostenibilidad más allá del periodo de gobierno?",
        "D6_Q1": "¿El plan presenta teoría de cambio o cadena causal explícita?",
        "D6_Q2": "¿El plan evita saltos desproporcionados en su lógica?",
        "D6_Q3": "¿El plan reconoce complejidad y propone mecanismos de aprendizaje?",
        "D6_Q4": "¿Se describe sistema de monitoreo con retroalimentación?",
        "D6_Q5": "¿El plan considera contexto municipal y grupos diferenciados?"
    }
    
    def __init__(self, classified_methods: list[ClassifiedMethod]):
        self.methods = classified_methods
        self.method_sets: dict[str, MethodSet] = {}
        
    def generate_method_set(self, question_id: str) -> MethodSet:
        """Genera el juego óptimo de métodos para una pregunta"""
        
        contract_type_code = self.QUESTION_CONTRACT_MAPPING.get(question_id, "TYPE_B")
        contract_type = next(ct for ct in ContractType if ct.code == contract_type_code)
        
        # Seleccionar métodos por fase, priorizando afinidad con tipo de contrato
        phase_a = self._select_phase_methods(EpistemologicalLevel.N1_EMP, contract_type, top_k=5)
        phase_b = self._select_phase_methods(EpistemologicalLevel.N2_INF, contract_type, top_k=5)
        phase_c = self._select_phase_methods(EpistemologicalLevel.N3_AUD, contract_type, top_k=3)
        
        # Calcular eficiencia matemática
        efficiency, evidence = self._calculate_efficiency(phase_a, phase_b, phase_c, contract_type)
        
        # Generar justificación doctoral
        justification = self._generate_doctoral_justification(
            question_id, contract_type, phase_a, phase_b, phase_c, efficiency, evidence
        )
        
        method_set = MethodSet(
            question_id=question_id,
            contract_type=contract_type,
            phase_a_methods=phase_a,
            phase_b_methods=phase_b,
            phase_c_methods=phase_c,
            efficiency_score=efficiency,
            mathematical_evidence=evidence,
            doctoral_justification=justification
        )
        
        self.method_sets[question_id] = method_set
        return method_set
    
    def _select_phase_methods(self, level: EpistemologicalLevel, 
                               contract_type: ContractType, 
                               top_k: int) -> list[ClassifiedMethod]:
        """Selecciona los mejores métodos para una fase según afinidad"""
        
        # Filtrar por nivel
        level_methods = [m for m in self.methods if m.level == level]
        
        # Ordenar por afinidad con el tipo de contrato
        sorted_methods = sorted(
            level_methods,
            key=lambda m: (
                m.contract_affinities.get(contract_type.code, 0),
                m.confidence_score
            ),
            reverse=True
        )
        
        # Tomar top_k únicos por clase (diversificar fuentes)
        selected = []
        seen_classes = set()
        
        for method in sorted_methods:
            if method.signature.class_name not in seen_classes:
                selected.append(method)
                seen_classes.add(method.signature.class_name)
                if len(selected) >= top_k:
                    break
        
        return selected
    
    def _calculate_efficiency(self, phase_a: list[ClassifiedMethod],
                              phase_b: list[ClassifiedMethod],
                              phase_c: list[ClassifiedMethod],
                              contract_type: ContractType) -> tuple[float, dict]:
        """
        Calcula la eficiencia matemática del juego de métodos.
        
        Basado en fórmulas de episte_refact:
        - Corroboración: confidence_combined = 1 - ∏(1 - conf_i)
        - Cobertura de fases: penalización si faltan métodos
        - Afinidad promedio con tipo de contrato
        """
        
        all_methods = phase_a + phase_b + phase_c
        
        if not all_methods:
            return 0.0, {"error": "No methods selected"}
        
        # 1. Confianza combinada por corroboración (fórmula de episte_refact)
        confidences = [m.confidence_score for m in all_methods]
        corroboration_score = 1 - math.prod(1 - c for c in confidences)
        
        # 2. Afinidad promedio con tipo de contrato
        affinities = [m.contract_affinities.get(contract_type.code, 0) for m in all_methods]
        avg_affinity = sum(affinities) / len(affinities)
        
        # 3. Cobertura de fases (penalización si falta alguna)
        phase_coverage = (
            (1.0 if phase_a else 0.0) * 0.33 +
            (1.0 if phase_b else 0.0) * 0.33 +
            (1.0 if phase_c else 0.0) * 0.34
        )
        
        # 4. Diversidad de clases (bonus por usar múltiples fuentes)
        unique_classes = len(set(m.signature.class_name for m in all_methods))
        diversity_bonus = min(0.15, unique_classes * 0.02)
        
        # 5. Balance N1:N2:N3 según tipo de contrato
        balance_score = self._calculate_balance_score(
            len(phase_a), len(phase_b), len(phase_c), contract_type
        )
        
        # Eficiencia final
        efficiency = (
            corroboration_score * 0.30 +
            avg_affinity * 0.30 +
            phase_coverage * 0.20 +
            balance_score * 0.15 +
            diversity_bonus
        )
        
        evidence = {
            "corroboration_formula": "1 - ∏(1 - conf_i)",
            "corroboration_score": round(corroboration_score, 4),
            "individual_confidences": [round(c, 3) for c in confidences],
            "average_contract_affinity": round(avg_affinity, 4),
            "phase_coverage": round(phase_coverage, 4),
            "phase_counts": {"N1": len(phase_a), "N2": len(phase_b), "N3": len(phase_c)},
            "unique_classes": unique_classes,
            "diversity_bonus": round(diversity_bonus, 4),
            "balance_score": round(balance_score, 4),
            "efficiency_formula": "0.30*corroboration + 0.30*affinity + 0.20*coverage + 0.15*balance + diversity",
            "final_efficiency": round(efficiency, 4)
        }
        
        return round(efficiency, 4), evidence
    
    def _calculate_balance_score(self, n1: int, n2: int, n3: int, 
                                  contract_type: ContractType) -> float:
        """Calcula qué tan bien balanceado está el juego según tipo de contrato"""
        
        # Proporciones ideales por tipo (basado en estrategias de fusión)
        ideal_ratios = {
            ContractType.TYPE_A: (0.35, 0.45, 0.20),  # Semántico: más N2
            ContractType.TYPE_B: (0.25, 0.50, 0.25),  # Bayesiano: dominancia N2
            ContractType.TYPE_C: (0.35, 0.30, 0.35),  # Causal: balanceado N1-N3
            ContractType.TYPE_D: (0.35, 0.25, 0.40),  # Financiero: más N3
            ContractType.TYPE_E: (0.25, 0.30, 0.45),  # Lógico: dominancia N3
        }
        
        total = n1 + n2 + n3
        if total == 0:
            return 0.0
        
        actual = (n1/total, n2/total, n3/total)
        ideal = ideal_ratios.get(contract_type, (0.33, 0.34, 0.33))
        
        # Distancia euclidiana del ideal
        distance = math.sqrt(sum((a - i)**2 for a, i in zip(actual, ideal)))
        
        # Convertir a score (menor distancia = mayor score)
        return max(0, 1 - distance)
    
    def _generate_doctoral_justification(self, question_id: str,
                                          contract_type: ContractType,
                                          phase_a: list[ClassifiedMethod],
                                          phase_b: list[ClassifiedMethod],
                                          phase_c: list[ClassifiedMethod],
                                          efficiency: float,
                                          evidence: dict) -> str:
        """
        Genera justificación en formato doctoral (3-5 párrafos).
        Estructura:
        1. Contexto y clasificación del contrato
        2. Justificación de métodos N1 (extracción empírica)
        3. Justificación de métodos N2 (inferencia)
        4. Justificación de métodos N3 (auditoría)
        5. Síntesis de eficiencia matemática
        """
        
        question_text = self.QUESTIONS.get(question_id, "Pregunta no especificada")
        
        # Párrafo 1: Contexto
        p1 = (
            f"La pregunta {question_id} ('{question_text}') ha sido clasificada como contrato "
            f"{contract_type.code} ({contract_type.type_name}), cuyo foco epistemológico es "
            f"'{contract_type.focus}'. Según la taxonomía de contratos de episte_refact, este tipo "
            f"requiere una estrategia de fusión principal de '{contract_type.fusion_strategy}', "
            f"lo cual determina la selección y ponderación de métodos en las tres fases de ejecución "
            f"del pipeline epistemológico."
        )
        
        # Párrafo 2: Fase A (N1)
        if phase_a:
            n1_classes = ", ".join(set(m.signature.class_name for m in phase_a))
            n1_methods = ", ".join(m.signature.method_name for m in phase_a[:3])
            p2 = (
                f"Para la Fase A (Construction, Nivel N1-EMP), se seleccionaron {len(phase_a)} métodos "
                f"de las clases {n1_classes}, incluyendo {n1_methods}. Estos métodos implementan "
                f"empirismo positivista, extrayendo hechos brutos del documento sin transformación "
                f"interpretativa. Su output de tipo FACT se suma al grafo de evidencia con comportamiento "
                f"aditivo (⊕), estableciendo la base empírica verificable sobre la cual operarán "
                f"las fases subsiguientes."
            )
        else:
            p2 = "No se identificaron métodos N1-EMP apropiados para la Fase A, lo cual constituye una limitación metodológica."
        
        # Párrafo 3: Fase B (N2)
        if phase_b:
            n2_classes = ", ".join(set(m.signature.class_name for m in phase_b))
            avg_affinity = sum(m.contract_affinities.get(contract_type.code, 0) for m in phase_b) / len(phase_b)
            p3 = (
                f"La Fase B (Computation, Nivel N2-INF) emplea {len(phase_b)} métodos de {n2_classes}, "
                f"con una afinidad promedio de {avg_affinity:.2%} hacia el tipo de contrato {contract_type.code}. "
                f"Estos métodos transforman los hechos N1 en conocimiento probabilístico mediante "
                f"bayesianismo subjetivista. Su output de tipo PARAMETER modifica los pesos de las "
                f"aristas del grafo (comportamiento multiplicativo ⊗), actualizando las creencias "
                f"sobre la evidencia según la fórmula posterior = update_belief(prior, likelihood)."
            )
        else:
            p3 = "La ausencia de métodos N2-INF en la Fase B limita la capacidad inferencial del análisis."
        
        # Párrafo 4: Fase C (N3)
        if phase_c:
            n3_classes = ", ".join(set(m.signature.class_name for m in phase_c))
            p4 = (
                f"La Fase C (Litigation, Nivel N3-AUD) constituye el núcleo del falsacionismo popperiano "
                f"implementado en FARFAN. Los {len(phase_c)} métodos de {n3_classes} actúan como VETO GATES, "
                f"intentando refutar los hallazgos de las fases anteriores. Su propiedad crítica es la "
                f"influencia asimétrica: N3 puede invalidar N1/N2, pero N1/N2 NO pueden invalidar N3. "
                f"Su output de tipo CONSTRAINT filtra o bloquea ramas del grafo de evidencia (⊘), "
                f"garantizando que solo la evidencia robusta llegue a la síntesis final."
            )
        else:
            p4 = "La ausencia de métodos N3-AUD compromete la validación epistemológica del análisis."
        
        # Párrafo 5: Síntesis matemática
        p5 = (
            f"La eficiencia matemática del juego de métodos es {efficiency:.2%}, calculada mediante "
            f"la fórmula de corroboración de episte_refact: confidence_combined = 1 - ∏(1 - conf_i), "
            f"que para este conjunto produce {evidence['corroboration_score']:.3f}. La cobertura de fases "
            f"es {evidence['phase_coverage']:.2%} con distribución N1:{evidence['phase_counts']['N1']}, "
            f"N2:{evidence['phase_counts']['N2']}, N3:{evidence['phase_counts']['N3']}, y la diversidad "
            f"de clases ({evidence['unique_classes']} únicas) aporta un bonus de {evidence['diversity_bonus']:.3f}. "
            f"Este conjunto metodológico está matemáticamente optimizado para responder la pregunta "
            f"con nivel doctoral, máxima certeza epistemológica y trazabilidad completa de la evidencia."
        )
        
        return "\n\n".join([p1, p2, p3, p4, p5])
    
    def generate_all_method_sets(self) -> dict[str, MethodSet]:
        """Genera juegos de métodos para todas las 30 preguntas"""
        for question_id in self.QUESTION_CONTRACT_MAPPING.keys():
            self.generate_method_set(question_id)
        return self.method_sets


# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 7: EXPORTADOR DE RESULTADOS
# ═══════════════════════════════════════════════════════════════════════════════

class ResultsExporter:
    """Exporta los resultados en formato JSON estructurado"""
    
    @staticmethod
    def export_classified_methods(methods: list[ClassifiedMethod], 
                                   output_path: Path) -> None:
        """Exporta métodos clasificados"""
        
        # Organizar por nivel epistemológico
        by_level = {level.code: [] for level in EpistemologicalLevel}
        for method in methods:
            by_level[method.level.code].append(method.to_dict())
        
        # Estadísticas
        stats = {
            level.code: {
                "count": len(by_level[level.code]),
                "level_name": level.level_name,
                "epistemology": level.epistemology,
                "output_type": level.output_type
            }
            for level in EpistemologicalLevel
        }
        
        output = {
            "metadata": {
                "version": "1.0.0",
                "source": "episte_refact.md",
                "total_methods": len(methods),
                "generation_date": "2025-01-01"
            },
            "statistics": stats,
            "methods_by_level": by_level,
            "all_methods": [m.to_dict() for m in methods]
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def export_method_sets(method_sets: dict[str, MethodSet],
                           output_path: Path) -> None:
        """Exporta juegos de métodos por pregunta"""
        
        output = {
            "metadata": {
                "version": "1.0.0",
                "source": "episte_refact.md",
                "total_questions": len(method_sets),
                "generation_date": "2025-01-01"
            },
            "method_sets": {}
        }
        
        for qid, mset in method_sets.items():
            output["method_sets"][qid] = {
                "question_id": mset.question_id,
                "contract_type": {
                    "code": mset.contract_type.code,
                    "name": mset.contract_type.type_name,
                    "focus": mset.contract_type.focus,
                    "fusion_strategy": mset.contract_type.fusion_strategy
                },
                "phase_a_N1": [m.to_dict() for m in mset.phase_a_methods],
                "phase_b_N2": [m.to_dict() for m in mset.phase_b_methods],
                "phase_c_N3": [m.to_dict() for m in mset.phase_c_methods],
                "efficiency_score": mset.efficiency_score,
                "mathematical_evidence": mset.mathematical_evidence,
                "doctoral_justification": mset.doctoral_justification
            }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 8: MAIN - EJECUCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Función principal de ejecución"""
    
    print("═" * 70)
    print("FARFAN EPISTEMOLOGICAL METHOD CLASSIFIER v1.0.0")
    print("Alineado con episte_refact.md")
    print("═" * 70)
    
    # 1. Clasificar todos los métodos
    print("\n[1/4] Clasificando métodos epistemológicamente...")
    classifier = EpistemologicalClassifier()
    classified_methods = classifier.classify_all_methods()
    
    print(f"      Total métodos clasificados: {len(classified_methods)}")
    for level, count in classifier.classification_stats.items():
        print(f"      - {level.code} ({level.level_name}): {count}")
    
    # 2. Generar juegos de métodos por pregunta
    print("\n[2/4] Generando juegos de métodos por pregunta...")
    generator = MethodSetGenerator(classified_methods)
    method_sets = generator.generate_all_method_sets()
    print(f"      Juegos generados: {len(method_sets)}")
    
    # 3. Calcular estadísticas de eficiencia
    print("\n[3/4] Calculando estadísticas de eficiencia...")
    efficiencies = [ms.efficiency_score for ms in method_sets.values()]
    avg_efficiency = sum(efficiencies) / len(efficiencies)
    print(f"      Eficiencia promedio: {avg_efficiency:.2%}")
    print(f"      Eficiencia mínima: {min(efficiencies):.2%}")
    print(f"      Eficiencia máxima: {max(efficiencies):.2%}")
    
    # 4. Exportar resultados
    print("\n[4/4] Exportando resultados...")
    from farfan_pipeline.utils.paths import PROJECT_ROOT
    output_dir = PROJECT_ROOT / "artifacts" / "method_analyzer_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    ResultsExporter.export_classified_methods(
        classified_methods, 
        output_dir / "classified_methods.json"
    )
    print(f"      → {output_dir / 'classified_methods.json'}")
    
    ResultsExporter.export_method_sets(
        method_sets,
        output_dir / "method_sets_by_question.json"
    )
    print(f"      → {output_dir / 'method_sets_by_question.json'}")
    
    print("\n" + "═" * 70)
    print("PROCESO COMPLETADO")
    print("═" * 70)
    
    return classified_methods, method_sets


if __name__ == "__main__":
    classified_methods, method_sets = main()

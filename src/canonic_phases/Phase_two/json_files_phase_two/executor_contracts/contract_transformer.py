"""
Contract Transformation Engine
Implements full Tier 1/2/3 enhancements for executor contracts
"""
import copy
import hashlib
import json
from datetime import datetime


class ContractTransformer:
    """Transform contracts with epistemological depth and methodological rigor"""

    EPISTEMOLOGICAL_TEMPLATES = {
        'PDETMunicipalPlanAnalyzer._score_indicators': {
            'paradigm': 'Quantitative indicator analysis with municipal development framework',
            'ontological_basis': 'Product indicators exist as measurable outcomes traceable to baseline data, targets, and verification sources in municipal planning documents',
            'epistemological_stance': 'Empirical-analytical: Knowledge emerges from systematic scoring of indicator completeness (baseline, target, source presence) against structured criteria',
            'theoretical_framework': [
                'Results-based management: Product indicators must link outputs to verifiable evidence (Kusek & Rist, 2004)',
                'PDET framework: Territorial development plans require gender-disaggregated metrics with accountability mechanisms'
            ],
            'justification': 'Scoring indicators reveals institutional capacity to operationalize gender commitments through measurable, verifiable product delivery'
        },
        'OperationalizationAuditor.audit_evidence_traceability': {
            'paradigm': 'Evidence chain verification with traceability analysis',
            'ontological_basis': 'Evidence exists as traceable artifacts linking claims to sources through verifiable chains of custody',
            'epistemological_stance': 'Critical-analytical: Knowledge validity depends on transparent provenance from claim to primary source',
            'theoretical_framework': [
                'Evidence-based policy: Claims require traceable evidence chains (Nutley et al., 2007)',
                'Audit theory: Traceability establishes epistemic warrant for policy assertions'
            ],
            'justification': 'Auditing traceability exposes gaps between rhetorical commitments and evidentiary foundations'
        },
        'CausalInferenceSetup.assign_probative_value': {
            'paradigm': 'Bayesian probative value assignment for causal inference',
            'ontological_basis': 'Evidence has varying probative strength based on causal proximity, reliability, and inferential warrant',
            'epistemological_stance': 'Bayesian-inferential: Evidence strength quantified through posterior probabilities given causal structure',
            'theoretical_framework': [
                'Bayesian epistemology: Probative value reflects evidential support for causal hypotheses (Joyce, 2003)',
                'Beach & Pedersen: Process tracing assigns probative weight based on test type (hoop/smoking gun/doubly decisive)'
            ],
            'justification': 'Probative value assignment enables weighted aggregation of evidence with differential epistemic strength'
        },
        'BeachEvidentialTest.apply_test_logic': {
            'paradigm': 'Process-tracing evidential tests (Beach & Pedersen framework)',
            'ontological_basis': 'Evidence can be classified by logical strength: hoop tests (necessary), smoking gun tests (sufficient), doubly decisive tests (both)',
            'epistemological_stance': 'Quasi-experimental: Causal mechanisms inferred through structured evidential tests eliminating rival hypotheses',
            'theoretical_framework': [
                'Beach & Pedersen (2013): Process tracing uses evidential tests to evaluate causal mechanisms',
                'Van Evera (1997): Tests vary in uniqueness and certainty, affecting inferential strength'
            ],
            'justification': 'Structured evidential tests provide rigorous basis for causal claims in observational policy contexts'
        },
        'TextMiningEngine.diagnose_critical_links': {
            'paradigm': 'Critical text mining with causal link detection',
            'ontological_basis': 'Texts contain latent causal structures detectable through linguistic patterns indicating causal relationships',
            'epistemological_stance': 'Empirical-interpretive: Knowledge about policy mechanisms emerges from detecting linguistic markers of causality',
            'theoretical_framework': [
                'Causal discourse analysis: Texts reveal causal beliefs through linguistic constructions (Fairclough, 2003)',
                'Theory of change reconstruction: Policy documents encode theories of change extractable via causal link detection (Weiss, 1995)'
            ],
            'justification': 'Diagnosing critical causal links reveals whether policymakers understand causal pathways between gender inequalities and determinants'
        },
        'IndustrialPolicyProcessor._extract_metadata': {
            'paradigm': 'Metadata extraction for policy document characterization',
            'ontological_basis': 'Policy documents contain structured and unstructured metadata revealing document provenance, scope, and administrative context',
            'epistemological_stance': 'Empirical-descriptive: Document metadata provides contextual knowledge for interpretation and validation',
            'theoretical_framework': [
                'Document analysis: Metadata enables systematic comparison and quality assessment (Prior, 2003)',
                'Administrative records theory: Metadata reveals institutional production conditions'
            ],
            'justification': 'Metadata extraction enables quality filtering and contextualization of evidence by document characteristics'
        },
        'IndustrialPolicyProcessor._calculate_quality_score': {
            'paradigm': 'Multi-dimensional document quality assessment',
            'ontological_basis': 'Document quality is a composite construct spanning completeness, consistency, traceability, and specification',
            'epistemological_stance': 'Evaluative-analytical: Quality emerges from weighted aggregation of measurable quality dimensions',
            'theoretical_framework': [
                'Information quality framework: Quality assessed via completeness, accuracy, consistency dimensions (Wang & Strong, 1996)',
                'Policy quality metrics: Operationalization quality predicts implementation success'
            ],
            'justification': 'Quality scoring enables prioritization of high-reliability evidence and flagging of low-quality sources'
        },
        'AdaptivePriorCalculator.generate_traceability_record': {
            'paradigm': 'Bayesian prior adaptation with full provenance tracking',
            'ontological_basis': 'Prior distributions encode background knowledge that should adapt as evidence accumulates, with adaptation traced for reproducibility',
            'epistemological_stance': 'Bayesian-reflexive: Priors updated systematically with transparent documentation of adaptation rationale',
            'theoretical_framework': [
                'Adaptive Bayesian inference: Priors updated via empirical Bayes or hierarchical modeling (Gelman et al., 2013)',
                'Provenance tracking: Scientific reproducibility requires documented lineage of analytical choices'
            ],
            'justification': 'Traceability records enable auditing of prior choices and sensitivity analysis of posterior conclusions'
        }
    }

    TECHNICAL_APPROACHES = {
        'PDETMunicipalPlanAnalyzer._score_indicators': {
            'method_type': 'rule_based_scoring_with_pattern_matching',
            'algorithm': 'Structured indicator completeness scoring across baseline/target/source dimensions',
            'steps': [
                {
                    'step': 1,
                    'description': 'Extract indicator mentions using regex patterns for product indicators (capacitadas, kits entregados, etc.)'
                },
                {
                    'step': 2,
                    'description': 'For each indicator, search context window (±50 tokens) for baseline markers (Línea Base, LB, Valor inicial)'
                },
                {
                    'step': 3,
                    'description': 'Search for target markers (Meta Cuatrienio, Meta, Valor esperado) with numeric extraction'
                },
                {
                    'step': 4,
                    'description': 'Detect verification sources (Fuente de verificación, Medio de verificación, listados de asistencia)'
                },
                {
                    'step': 5,
                    'description': 'Calculate completeness score: 1.0 if all three elements present, 0.67 if two, 0.33 if one, 0.0 if zero'
                }
            ],
            'assumptions': [
                'Indicators appear in proximity to their baseline/target/source specifications',
                'Standard Colombian planning terminology used (Meta Cuatrienio, Línea Base, etc.)',
                'Context window of ±50 tokens captures most indicator metadata'
            ],
            'limitations': [
                'Cannot detect implicit baselines or targets without linguistic markers',
                'May miss indicators specified in tables or structured data formats',
                'Assumes Spanish-language documents with Colombian public sector conventions'
            ],
            'complexity': 'O(n*p) where n=document sentences, p=indicator patterns'
        },
        'OperationalizationAuditor.audit_evidence_traceability': {
            'method_type': 'chain_of_custody_validation',
            'algorithm': 'Backward tracing from claims to sources with gap detection',
            'steps': [
                {
                    'step': 1,
                    'description': 'Identify quantitative claims (numeric assertions about gender indicators)'
                },
                {
                    'step': 2,
                    'description': 'Extract source citations (DANE, INML, Secretary reports) within claim context'
                },
                {
                    'step': 3,
                    'description': 'Validate source authority (official entity, publication year, dataset ID)'
                },
                {
                    'step': 4,
                    'description': 'Flag traceability gaps: claims without sources, sources without validation, broken citation chains'
                },
                {
                    'step': 5,
                    'description': 'Generate traceability score: (validated_claims / total_claims) * confidence_weight'
                }
            ],
            'assumptions': [
                'Claims and sources appear in same paragraph or adjacent paragraphs',
                'Standard citation patterns used (según DANE, fuente: X, datos de Y)'
            ],
            'limitations': [
                'Cannot validate source authenticity without external database lookup',
                'May miss indirect citations or footnote-based referencing'
            ],
            'complexity': 'O(n*c) where n=claims, c=citation patterns'
        },
        'CausalInferenceSetup.assign_probative_value': {
            'method_type': 'bayesian_weight_assignment',
            'algorithm': 'Posterior probability computation for evidential strength',
            'steps': [
                {
                    'step': 1,
                    'description': 'Classify evidence by type (statistical, observational, testimonial)'
                },
                {
                    'step': 2,
                    'description': 'Assign prior probative weight based on evidence type (statistical: 0.9, observational: 0.7, testimonial: 0.5)'
                },
                {
                    'step': 3,
                    'description': 'Adjust for source reliability (official sources +0.1, academic +0.15, anecdotal -0.2)'
                },
                {
                    'step': 4,
                    'description': 'Compute posterior probative value via Bayesian updating given document quality score'
                },
                {
                    'step': 5,
                    'description': 'Return ranked evidence with probative values for weighted aggregation'
                }
            ],
            'assumptions': [
                'Prior probative weights reflect true evidential strength hierarchy',
                'Source reliability is independent of evidence type'
            ],
            'limitations': [
                'Subjective priors for probative weights may not generalize across contexts',
                'Independence assumptions may not hold for correlated evidence'
            ],
            'complexity': 'O(e) where e=evidence elements'
        },
        'BeachEvidentialTest.apply_test_logic': {
            'method_type': 'structured_process_tracing',
            'algorithm': 'Multi-test evidential logic with elimination inferencing',
            'steps': [
                {
                    'step': 1,
                    'description': 'Define mechanism hypothesis (e.g., "lack of baseline data causes incomplete indicator specification")'
                },
                {
                    'step': 2,
                    'description': 'Apply hoop test: Is baseline data presence necessary? If absent, mechanism rejected'
                },
                {
                    'step': 3,
                    'description': 'Apply smoking gun test: Is complete indicator spec sufficient to confirm mechanism? If present, mechanism confirmed'
                },
                {
                    'step': 4,
                    'description': 'Aggregate test results: passed hoop + passed smoking gun = strong confirmation, failed hoop = rejection'
                },
                {
                    'step': 5,
                    'description': 'Return mechanism confidence: doubly decisive (both passed) = 0.9, smoking gun only = 0.7, hoop only = 0.4, neither = 0.1'
                }
            ],
            'assumptions': [
                'Mechanisms are discrete and testable via observable implications',
                'Tests are correctly classified as hoop/smoking gun based on logical strength'
            ],
            'limitations': [
                'Requires pre-specified mechanism hypotheses, cannot discover novel mechanisms',
                'Test classification subjective and context-dependent'
            ],
            'complexity': 'O(m*t) where m=mechanisms, t=tests per mechanism'
        },
        'TextMiningEngine.diagnose_critical_links': {
            'method_type': 'pattern_based_causal_link_extraction',
            'algorithm': 'Multi-pattern regex matching with context window analysis',
            'steps': [
                {
                    'step': 1,
                    'description': 'Identify causal connectors (porque, por lo tanto, conduce a, genera, resulta en)'
                },
                {
                    'step': 2,
                    'description': 'Extract entities before connector (cause) and after connector (effect) within ±30 token window'
                },
                {
                    'step': 3,
                    'description': 'Classify link criticality based on proximity to gender indicators (VBG, autonomía, participación)'
                },
                {
                    'step': 4,
                    'description': 'Filter for critical links: criticality ≥ 0.7, coherence score ≥ 0.6 (cause-effect semantic similarity)'
                },
                {
                    'step': 5,
                    'description': 'Return ranked critical links with cause-effect pairs and confidence scores'
                }
            ],
            'assumptions': [
                'Causal language reflects causal understanding (not merely rhetorical)',
                'Critical links mention gender-related outcomes within 30-token proximity'
            ],
            'limitations': [
                'Cannot detect implicit causality without linguistic markers',
                'May miss causal relationships expressed across distant sentences or paragraphs'
            ],
            'complexity': 'O(n*p) where n=sentences, p=causal patterns'
        },
        'IndustrialPolicyProcessor._extract_metadata': {
            'method_type': 'structured_metadata_extraction',
            'algorithm': 'Pattern-based metadata field extraction with validation',
            'steps': [
                {
                    'step': 1,
                    'description': 'Extract document identifiers (plan name, municipality, year) from title and header sections'
                },
                {
                    'step': 2,
                    'description': 'Detect policy area classification (gender, rural development, etc.) via keyword matching'
                },
                {
                    'step': 3,
                    'description': 'Parse temporal scope (plan period: 2020-2023) from common metadata fields'
                },
                {
                    'step': 4,
                    'description': 'Identify responsible entities (Secretarías, alcaldía) from authorship and approval sections'
                },
                {
                    'step': 5,
                    'description': 'Validate metadata completeness and flag missing critical fields (year, municipality)'
                }
            ],
            'assumptions': [
                'Metadata fields appear in standard locations (headers, footers, first pages)',
                'Standard Colombian municipal plan structure followed'
            ],
            'limitations': [
                'Cannot extract metadata from unstructured or non-standard documents',
                'May fail on scanned PDFs without OCR or poorly formatted text'
            ],
            'complexity': 'O(n) where n=document tokens (single-pass extraction)'
        },
        'IndustrialPolicyProcessor._calculate_quality_score': {
            'method_type': 'composite_quality_scoring',
            'algorithm': 'Weighted aggregation of quality dimensions with threshold checks',
            'steps': [
                {
                    'step': 1,
                    'description': 'Calculate completeness: (present_fields / required_fields) * 0.3'
                },
                {
                    'step': 2,
                    'description': 'Calculate consistency: 1 - (contradictions_detected / total_claims) * 0.25'
                },
                {
                    'step': 3,
                    'description': 'Calculate traceability: (claims_with_sources / total_claims) * 0.25'
                },
                {
                    'step': 4,
                    'description': 'Calculate specification: (indicators_with_baseline_target / total_indicators) * 0.2'
                },
                {
                    'step': 5,
                    'description': 'Aggregate: quality_score = completeness + consistency + traceability + specification (0-1 scale)'
                }
            ],
            'assumptions': [
                'Quality dimensions are independent and equally important within their weights',
                'Weighted formula reflects true document quality construct'
            ],
            'limitations': [
                'Weights subjectively chosen, may not match all use cases',
                'Cannot assess semantic quality or logical coherence beyond contradiction detection'
            ],
            'complexity': 'O(n) where n=document elements (claims, indicators, fields)'
        },
        'AdaptivePriorCalculator.generate_traceability_record': {
            'method_type': 'provenance_logging_with_bayesian_updating',
            'algorithm': 'Structured prior adaptation with full audit trail generation',
            'steps': [
                {
                    'step': 1,
                    'description': 'Initialize prior distribution from expert elicitation or empirical data (e.g., Beta(2, 5) for baseline presence)'
                },
                {
                    'step': 2,
                    'description': 'Update prior to posterior using observed data via Bayesian conjugate updating'
                },
                {
                    'step': 3,
                    'description': 'Log adaptation record: prior parameters, observed data, posterior parameters, update rationale'
                },
                {
                    'step': 4,
                    'description': 'Generate provenance graph: link posterior to evidence elements and methods contributing to update'
                },
                {
                    'step': 5,
                    'description': 'Return traceability record with full audit trail for reproducibility and sensitivity analysis'
                }
            ],
            'assumptions': [
                'Conjugate priors available for efficient updating (Beta-Binomial, Normal-Normal, etc.)',
                'Prior choice transparent and justified via expert knowledge or data'
            ],
            'limitations': [
                'Non-conjugate updates require MCMC or variational inference (computationally expensive)',
                'Prior sensitivity not automatically assessed, requires additional sensitivity analysis'
            ],
            'complexity': 'O(d) where d=data points for posterior update (O(1) for conjugate, O(n*iterations) for MCMC)'
        }
    }

    OUTPUT_INTERPRETATIONS = {
        'PDETMunicipalPlanAnalyzer._score_indicators': {
            'output_structure': {
                'indicator_scores': 'List of dicts with {indicator_name, baseline_present, target_present, source_present, completeness_score}',
                'aggregate_score': 'Mean completeness across all indicators (0-1 scale)',
                'missing_elements': 'List of indicators missing baseline/target/source'
            },
            'interpretation_guide': {
                'high_completeness': '≥0.8: Indicators fully specified with baseline, target, and verification sources',
                'medium_completeness': '0.5-0.79: Most indicators have 2/3 elements, some gaps remain',
                'low_completeness': '<0.5: Systematic gaps in indicator specification, likely implementation challenges'
            },
            'actionable_insights': [
                'If baseline missing: Cannot assess progress, need baseline data collection',
                'If targets missing: Unclear success criteria, need target specification',
                'If sources missing: Verification impossible, need source identification and validation protocols'
            ]
        },
        'OperationalizationAuditor.audit_evidence_traceability': {
            'output_structure': {
                'traced_claims': 'List of claims with {claim_text, source_citation, source_valid, traceability_score}',
                'traceability_gaps': 'Claims without sources or with invalid sources',
                'aggregate_traceability': 'Percentage of claims with valid source traceability'
            },
            'interpretation_guide': {
                'high_traceability': '≥0.8: Strong evidence chain, most claims traceable to valid sources',
                'medium_traceability': '0.5-0.79: Moderate gaps, some claims lack source validation',
                'low_traceability': '<0.5: Weak evidence foundation, many unsubstantiated claims'
            },
            'actionable_insights': [
                'If many gaps: Request source documentation from plan authors',
                'If invalid sources: Flag for verification with official databases',
                'If high traceability: Evidence foundation strong, can proceed with confidence'
            ]
        },
        'CausalInferenceSetup.assign_probative_value': {
            'output_structure': {
                'evidence_elements': 'List with {element_id, evidence_type, source_reliability, prior_weight, posterior_probative_value}',
                'high_value_evidence': 'Elements with probative_value ≥ 0.8',
                'low_value_evidence': 'Elements with probative_value < 0.5'
            },
            'interpretation_guide': {
                'high_probative': '≥0.8: Strong evidential warrant, suitable for primary inferences',
                'medium_probative': '0.5-0.79: Moderate strength, useful for triangulation',
                'low_probative': '<0.5: Weak warrant, use cautiously or discard'
            },
            'actionable_insights': [
                'Prioritize high-probative evidence for causal claims',
                'Use medium-probative for corroboration, not primary inference',
                'Flag low-probative evidence for exclusion or sensitivity analysis'
            ]
        },
        'BeachEvidentialTest.apply_test_logic': {
            'output_structure': {
                'mechanism': 'Hypothesized causal mechanism being tested',
                'hoop_test_result': '{passed: bool, evidence: str, confidence: float}',
                'smoking_gun_result': '{passed: bool, evidence: str, confidence: float}',
                'overall_confidence': 'Mechanism confidence (0-1) based on test outcomes'
            },
            'interpretation_guide': {
                'doubly_decisive': 'Both tests passed (0.9): Strong mechanism confirmation',
                'smoking_gun_only': 'Sufficient but not necessary (0.7): Mechanism plausible but not unique',
                'hoop_only': 'Necessary but not sufficient (0.4): Mechanism possible but not confirmed',
                'both_failed': 'Neither test passed (0.1): Mechanism rejected or unsupported'
            },
            'actionable_insights': [
                'Doubly decisive: Accept mechanism, use for intervention design',
                'Smoking gun only: Consider alternative mechanisms with same sufficient evidence',
                'Hoop only: Mechanism survives but needs additional evidence',
                'Both failed: Reject mechanism, explore alternative causal pathways'
            ]
        },
        'TextMiningEngine.diagnose_critical_links': {
            'output_structure': {
                'critical_links': 'List of {cause_entity, effect_entity, causal_connector, criticality_score, coherence_score, context}',
                'gender_focused_links': 'Subset of links directly mentioning gender outcomes (VBG, autonomía, participación)',
                'link_count': 'Total number of critical causal links detected'
            },
            'interpretation_guide': {
                'high_criticality': '≥0.8: Link directly connects to gender inequality outcomes',
                'medium_criticality': '0.5-0.79: Link relates to intermediate factors (economic, social)',
                'low_criticality': '<0.5: Peripheral causal relationship'
            },
            'actionable_insights': [
                'If few critical links: Diagnosis lacks causal depth, may be purely descriptive',
                'If many links but low criticality: Diagnosis discusses tangential issues, not core gender inequalities',
                'If high-criticality links present: Diagnosis demonstrates causal understanding, good foundation for intervention'
            ]
        },
        'IndustrialPolicyProcessor._extract_metadata': {
            'output_structure': {
                'document_id': 'Unique identifier (plan name + municipality + year)',
                'metadata_fields': 'Dict with {municipality, year, policy_area, temporal_scope, responsible_entity, author}',
                'completeness': 'Percentage of required metadata fields present',
                'validation_flags': 'Missing or invalid fields requiring attention'
            },
            'interpretation_guide': {
                'complete_metadata': '100%: All required fields present and valid',
                'partial_metadata': '50-99%: Some fields missing, usable with caveats',
                'incomplete_metadata': '<50%: Critical fields missing, document may be unreliable'
            },
            'actionable_insights': [
                'Complete metadata: Document well-characterized, suitable for analysis',
                'Partial metadata: Use with caution, note limitations in reporting',
                'Incomplete metadata: Request additional documentation or exclude from analysis'
            ]
        },
        'IndustrialPolicyProcessor._calculate_quality_score': {
            'output_structure': {
                'quality_score': 'Composite score (0-1) aggregating completeness, consistency, traceability, specification',
                'dimension_scores': 'Dict with {completeness, consistency, traceability, specification} subscores',
                'quality_flags': 'Specific issues detected (contradictions, missing sources, incomplete indicators)'
            },
            'interpretation_guide': {
                'high_quality': '≥0.8: Document meets quality standards, suitable for primary evidence',
                'medium_quality': '0.6-0.79: Acceptable quality with minor issues',
                'low_quality': '<0.6: Quality concerns, use cautiously or exclude'
            },
            'actionable_insights': [
                'High quality: Proceed with analysis, document is reliable',
                'Medium quality: Flag specific issues, use with caveats',
                'Low quality: Request document revision or seek alternative sources'
            ]
        },
        'AdaptivePriorCalculator.generate_traceability_record': {
            'output_structure': {
                'prior_distribution': 'Initial distribution (e.g., Beta(2, 5))',
                'observed_data': 'Data used for updating (e.g., 8 successes in 10 trials)',
                'posterior_distribution': 'Updated distribution (e.g., Beta(10, 7))',
                'adaptation_rationale': 'Reason for update (observed data, expert input)',
                'provenance_graph': 'Linkage from posterior to contributing evidence elements'
            },
            'interpretation_guide': {
                'strong_update': 'Large shift in posterior mean (>0.2): Data highly informative',
                'moderate_update': 'Moderate shift (0.05-0.2): Data provides some information',
                'weak_update': 'Small shift (<0.05): Data weakly informative, prior dominates'
            },
            'actionable_insights': [
                'Strong update: Data-driven inference, posterior reflects observed patterns',
                'Moderate update: Balanced inference, both prior and data contribute',
                'Weak update: Prior-dominated, consider collecting more data or refining prior',
                'Always check provenance graph for sensitivity to specific evidence elements'
            ]
        }
    }

    def transform_q011_contract(self, contract: dict) -> dict:
        """Apply full transformation to Q011 contract"""
        contract = copy.deepcopy(contract)

        contract = self._fix_identity_schema_coherence(contract)
        contract = self._fix_method_assembly_alignment(contract)
        contract = self._fix_output_schema_required(contract)
        contract = self._expand_epistemological_foundation(contract)
        contract = self._enhance_methodological_depth(contract)
        contract = self._enrich_human_answer_structure(contract)
        contract = self._update_timestamp_and_hash(contract)

        return contract

    def _fix_identity_schema_coherence(self, contract: dict) -> dict:
        """Fix A1: Identity-Schema const field coherence"""
        identity = contract['identity']
        schema_props = contract['output_contract']['schema']['properties']

        schema_props['question_id']['const'] = identity['question_id']
        schema_props['policy_area_id']['const'] = identity['policy_area_id']
        schema_props['dimension_id']['const'] = identity['dimension_id']
        schema_props['question_global']['const'] = identity['question_global']
        schema_props['base_slot']['const'] = identity['base_slot']

        return contract

    def _fix_method_assembly_alignment(self, contract: dict) -> dict:
        """Fix A2: Method-Assembly provides-sources alignment"""
        methods = contract['method_binding']['methods']
        provides = [m['provides'] for m in methods]

        contract['evidence_assembly']['assembly_rules'][0]['sources'] = provides
        contract['evidence_assembly']['assembly_rules'][0]['description'] = f'Combine evidence from {len(provides)} methods'

        return contract

    def _fix_output_schema_required(self, contract: dict) -> dict:
        """Fix A4: Ensure all required fields are in properties"""
        schema = contract['output_contract']['schema']
        required = schema['required']
        properties = schema['properties']

        for field in required:
            if field not in properties:
                properties[field] = {
                    'type': ['object', 'null'],
                    'additionalProperties': True
                }

        return contract

    def _expand_epistemological_foundation(self, contract: dict) -> dict:
        """Expand epistemological_foundation with question-specific paradigms"""
        methods = contract['output_contract']['human_readable_output']['methodological_depth']['methods']

        for method in methods:
            method_key = f"{method['class_name']}.{method['method_name']}"

            if method_key in self.EPISTEMOLOGICAL_TEMPLATES:
                method['epistemological_foundation'] = self.EPISTEMOLOGICAL_TEMPLATES[method_key]
            else:
                method['epistemological_foundation'] = {
                    'paradigm': f'{method["class_name"]} analytical paradigm',
                    'ontological_basis': f'Analysis via {method_key}',
                    'epistemological_stance': 'Empirical-analytical approach',
                    'theoretical_framework': [
                        f'Method {method["method_name"]} implements structured analysis for {contract["identity"]["base_slot"]}'
                    ],
                    'justification': f'This method contributes to {contract["identity"]["base_slot"]} analysis'
                }

        return contract

    def _enhance_methodological_depth(self, contract: dict) -> dict:
        """Enhance technical_approach with detailed steps and output_interpretation"""
        methods = contract['output_contract']['human_readable_output']['methodological_depth']['methods']

        for method in methods:
            method_key = f"{method['class_name']}.{method['method_name']}"

            if method_key in self.TECHNICAL_APPROACHES:
                method['technical_approach'] = self.TECHNICAL_APPROACHES[method_key]
            else:
                method['technical_approach'] = {
                    'method_type': 'analytical_processing',
                    'algorithm': f'{method_key} algorithm',
                    'steps': [
                        {'step': 1, 'description': f'Execute {method["method_name"]}'},
                        {'step': 2, 'description': 'Process results'},
                        {'step': 3, 'description': 'Return structured output'}
                    ],
                    'assumptions': ['Input data is preprocessed and valid'],
                    'limitations': ['Method-specific limitations apply'],
                    'complexity': 'O(n) where n=input size'
                }

            if method_key in self.OUTPUT_INTERPRETATIONS:
                method['output_interpretation'] = self.OUTPUT_INTERPRETATIONS[method_key]
            else:
                method['output_interpretation'] = {
                    'output_structure': {
                        'result': f'Structured output from {method["method_name"]}'
                    },
                    'interpretation_guide': {
                        'high_confidence': '≥0.8: Strong evidence',
                        'medium_confidence': '0.5-0.79: Moderate evidence',
                        'low_confidence': '<0.5: Weak evidence'
                    },
                    'actionable_insights': [
                        f'Use {method["method_name"]} results for downstream analysis'
                    ]
                }

        return contract

    def _enrich_human_answer_structure(self, contract: dict) -> dict:
        """Enrich concrete_example with granular validation against expected_elements"""
        has = contract['human_answer_structure']
        expected = contract['question_context']['expected_elements']

        validation_section = {}
        for elem in expected:
            elem_type = elem['type']
            elem_required = elem.get('required', False)

            concrete = has['concrete_example']
            elements_found = concrete.get('elements_found', [])
            matching = [e for e in elements_found if e.get('type') == elem_type]

            validation_section[elem_type] = {
                'required': elem_required,
                'found_in_example': len(matching) > 0,
                'count': len(matching)
            }

            if matching:
                validation_section[elem_type]['example_element_id'] = matching[0].get('element_id')

        has['validation_against_expected_elements'] = validation_section
        has['validation_against_expected_elements']['overall_validation_result'] = (
            'PASS - All required elements present'
            if all(v['found_in_example'] for k, v in validation_section.items() if v['required'])
            else 'FAIL - Some required elements missing'
        )

        return contract

    def _update_timestamp_and_hash(self, contract: dict) -> dict:
        """Update contract metadata with new timestamp and hash"""
        contract['identity']['created_at'] = datetime.now().isoformat() + '+00:00'

        hashable = {k: v for k, v in contract.items() if k not in ['identity', 'calibration']}
        contract_str = json.dumps(hashable, sort_keys=True)
        contract['identity']['contract_hash'] = hashlib.sha256(contract_str.encode()).hexdigest()

        return contract


def transform_contract_file(input_path: str, output_path: str) -> None:
    """Transform contract file and save to output"""
    with open(input_path) as f:
        contract = json.load(f)

    transformer = ContractTransformer()
    transformed = transformer.transform_q011_contract(contract)

    with open(output_path, 'w') as f:
        json.dump(transformed, f, indent=2, ensure_ascii=False)

#!/usr/bin/env python3
import json
from pathlib import Path

with open('canonic_questionnaire_central/questionnaire_monolith.json') as f:
    monolith = json.load(f)

q014_data = None
for question in monolith['blocks']['micro_questions']:
    if question.get('question_id') == 'Q014':
        q014_data = question
        break

if not q014_data:
    raise ValueError("Q014 not found")

identity = {
    'base_slot': q014_data.get('base_slot', 'D3-Q4'),
    'question_id': q014_data.get('question_id', 'Q014'),
    'question_global': q014_data.get('question_global', 14),
    'policy_area_id': q014_data.get('policy_area_id', 'PA01'),
    'dimension_id': q014_data.get('dimension_id', 'DIM03'),
    'cluster_id': q014_data.get('cluster_id', 'CL02')
}

method_sets = q014_data.get('method_sets', [])
method_count = len(method_sets)
provides = [f"{m['class']}.{m['function']}".lower() for m in method_sets]

assembly_rules = [
    {
        'target': 'elements_found',
        'sources': provides,
        'merge_strategy': 'concat',
        'description': 'Aggregate all discovered evidence elements'
    },
    {
        'target': 'confidence_scores',
        'sources': [p for p in provides if 'bayesian' in p or 'confidence' in p or 'calculate' in p],
        'merge_strategy': 'weighted_mean',
        'description': 'Aggregate confidence scores from Bayesian methods'
    },
    {
        'target': 'pattern_matches',
        'sources': [p for p in provides if 'extract' in p or 'detect' in p or 'identify' in p],
        'merge_strategy': 'concat',
        'description': 'Collect pattern matches from extraction methods'
    },
    {
        'target': 'metadata',
        'sources': ['*.metadata'],
        'merge_strategy': 'deep_merge',
        'description': 'Merge metadata from all methods'
    }
]

output_schema = {
    'type': 'object',
    'required': ['base_slot', 'question_id', 'question_global', 'evidence', 'validation'],
    'properties': {
        'base_slot': {'type': 'string', 'const': identity['base_slot']},
        'question_id': {'type': 'string', 'const': identity['question_id']},
        'question_global': {'type': 'integer', 'const': identity['question_global']},
        'policy_area_id': {'type': 'string', 'const': identity['policy_area_id']},
        'dimension_id': {'type': 'string', 'const': identity['dimension_id']},
        'cluster_id': {'type': 'string', 'const': identity['cluster_id']},
        'evidence': {
            'type': 'object',
            'properties': {
                'elements_found': {'type': 'array'},
                'confidence_scores': {'type': 'object'},
                'pattern_matches': {'type': 'array'}
            }
        },
        'validation': {
            'type': 'object',
            'properties': {
                'completeness': {'type': 'number'},
                'consistency': {'type': 'number'},
                'signal_strength': {'type': 'number'}
            }
        },
        'trace': {
            'type': 'object',
            'properties': {
                'executor_id': {'type': 'string'},
                'timestamp': {'type': 'string'},
                'version': {'type': 'string'}
            }
        },
        'metadata': {'type': 'object'}
    }
}

signal_requirements = {
    'mandatory_signals': [
        'feasibility_score',
        'resource_coherence',
        'deadline_realism',
        'operational_capacity',
        'activity_product_link'
    ],
    'minimum_signal_threshold': 0.5,
    'signal_aggregation': 'weighted_mean',
    'signal_weights': {
        'feasibility_score': 0.3,
        'resource_coherence': 0.25,
        'deadline_realism': 0.2,
        'operational_capacity': 0.15,
        'activity_product_link': 0.1
    }
}

methodological_depth = {
    'epistemological_foundation': {
        'paradigm': 'Bayesian Causal Inference with Temporal Logic Verification',
        'theoretical_framework': [
            'Counterfactual reasoning for policy feasibility assessment',
            'Bayesian mechanism inference for activity-product linkage',
            'Temporal constraint satisfaction for deadline realism'
        ],
        'assumptions': [
            'Resource allocation follows municipal budget constraints',
            'Activity feasibility depends on operational capacity',
            'Deadline realism requires temporal consistency across policy documents'
        ],
        'limitations': [
            'Historical data may not reflect future conditions',
            'Organizational capacity assessment relies on documented evidence',
            'Cross-sectoral dependencies not fully modeled'
        ]
    },
    'technical_approach': {
        'methods': [
            {
                'method_id': 'advanceddagvalidator.calculate_acyclicity_pvalue',
                'paradigm': 'Statistical Hypothesis Testing on Graph Structure',
                'technical_approach': {
                    'steps': [
                        {
                            'order': 1,
                            'description': 'Construct adjacency matrix from causal graph edges',
                            'complexity': 'O(n²) where n = number of nodes'
                        },
                        {
                            'order': 2,
                            'description': 'Perform random permutation test (1000 iterations) to assess acyclicity',
                            'complexity': 'O(k·n³) where k = permutations'
                        },
                        {
                            'order': 3,
                            'description': 'Calculate p-value using null distribution of cycle counts',
                            'complexity': 'O(1)'
                        }
                    ]
                },
                'outputs': ['acyclicity_pvalue', 'cycle_count', 'statistical_power']
            },
            {
                'method_id': 'bayesianmechanisminference._test_necessity',
                'paradigm': 'Counterfactual Necessity Testing',
                'technical_approach': {
                    'steps': [
                        {
                            'order': 1,
                            'description': 'Identify mechanism components (activity, product, outcome)',
                            'complexity': 'O(n) where n = evidence elements'
                        },
                        {
                            'order': 2,
                            'description': 'Calculate P(outcome | do(remove_activity)) using Bayesian intervention',
                            'complexity': 'O(m) where m = graph edges'
                        },
                        {
                            'order': 3,
                            'description': 'Compare factual vs counterfactual probabilities for necessity',
                            'complexity': 'O(1)'
                        }
                    ]
                },
                'outputs': ['necessity_score', 'counterfactual_probability', 'confidence_interval']
            },
            {
                'method_id': 'industrialgradevalidator.execute_suite',
                'paradigm': 'Systematic Validation Pipeline',
                'technical_approach': {
                    'steps': [
                        {
                            'order': 1,
                            'description': 'Load validation rules from contract specifications',
                            'complexity': 'O(r) where r = number of rules'
                        },
                        {
                            'order': 2,
                            'description': 'Execute each validator against evidence corpus',
                            'complexity': 'O(r·n) where n = evidence size'
                        },
                        {
                            'order': 3,
                            'description': 'Aggregate validation results with confidence weighting',
                            'complexity': 'O(r)'
                        }
                    ]
                },
                'outputs': ['validation_summary', 'rule_outcomes', 'aggregate_confidence']
            }
        ]
    }
}

contract = {
    'contract_version': '3.0.0',
    'question_id': 'Q014',
    'identity': identity,
    'question_context': {
        'text': q014_data.get('text', ''),
        'base_slot': identity['base_slot'],
        'cluster_id': identity['cluster_id'],
        'dimension_id': identity['dimension_id'],
        'policy_area_id': identity['policy_area_id'],
        'question_global': identity['question_global'],
        'scoring_modality': q014_data.get('scoring_modality', 'TYPE_A'),
        'scoring_definition_ref': q014_data.get('scoring_definition_ref', 'scoring_modalities.TYPE_A'),
        'expected_elements': q014_data.get('expected_elements', []),
        'patterns': q014_data.get('patterns', []),
        'validations': q014_data.get('validations', {})
    },
    'method_binding': {
        'method_count': method_count,
        'methods': [{
            'provides': provides[i],
            'class': method_sets[i]['class'],
            'function': method_sets[i]['function'],
            'method_type': method_sets[i].get('method_type', 'analysis'),
            'priority': method_sets[i].get('priority', i + 1),
            'description': method_sets[i].get('description', f"{method_sets[i]['class']}.{method_sets[i]['function']}")
        } for i in range(method_count)]
    },
    'evidence_assembly': {
        'assembly_rules': assembly_rules
    },
    'output_contract': {
        'schema': output_schema,
        'human_readable_output': {
            'template': {
                'title': 'Q014: Feasibility Analysis for Gender Policy Activities',
                'summary': 'Assessment of feasibility between activities and product goals',
                'evidence_detail': '{evidence_list}',
                'confidence': 'Confidence: {confidence_score}',
                'required_placeholders': [
                    '{score}', '{evidence_count}', '{confidence_score}',
                    '{question_number}', '{question_text}', '{evidence_list}'
                ]
            },
            'methodological_depth': methodological_depth
        }
    },
    'signal_requirements': signal_requirements,
    'failure_contract': q014_data.get('failure_contract', {}),
    'traceability': {
        'source_questionnaire': 'questionnaire_monolith.json',
        'source_hash': 'TODO_SHA256_HASH_OF_QUESTIONNAIRE_MONOLITH',
        'generation_timestamp': '2025-01-01T00:00:00Z',
        'contract_author': 'Q014ContractTransformer',
        'cqvr_audit_version': '2.0'
    }
}

output_path = Path('src/canonic_phases/Phase_two/json_files_phase_two/executor_contracts/specialized/Q014.v3.json')
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(contract, f, indent=2, ensure_ascii=False)

print(f"✅ Generated Q014.v3.json with {method_count} methods")
print(f"✅ Identity: {identity}")
print(f"✅ Assembly rules: {len(assembly_rules)}")
print(f"✅ Signal threshold: {signal_requirements['minimum_signal_threshold']}")

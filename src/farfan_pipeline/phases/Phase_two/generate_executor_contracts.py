"""
Generate 300 Executor Contracts with Method Bindings
Final assemblance of methods into executable contracts per F.A.R.F.A.N pipeline
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class MethodBinding:
    """Single method binding in a contract"""
    class_name: str
    method_name: str
    mother_file: str
    provides: str
    level: str
    output_type: str
    fusion_behavior: str
    description: str
    requires: List[str]


@dataclass
class ExecutorContract:
    """Complete executor contract for a Policy-Dimension-Question tuple"""
    contract_id: str
    policy_area: str
    dimension_code: str
    question_id: str
    question_type: str
    question_text: str

    method_binding: Dict[str, Any]
    evidence_assembly: Dict[str, Any]

    epistemological_justification: str
    fusion_strategies: Dict[str, str]


class ContractGenerator:
    """Generates 300 executor contracts from method selections"""

    POLICY_AREAS = [
        "D01_MUJER_GENERO", "D02_EDUCACION", "D03_SALUD", "D04_CULTURA",
        "D05_DEPORTE", "D06_VIVIENDA", "D07_AGROPECUARIO", "D08_TRANSPORTE",
        "D09_MEDIO_AMBIENTE", "D10_ATENCION_GRUPOS"
    ]

    FUSION_STRATEGIES = {
        'TYPE_A': {
            'n1': 'semantic_bundling',
            'n2': 'dempster_shafer',
            'n3': 'contradiction_veto'
        },
        'TYPE_B': {
            'n1': 'evidence_concatenation',
            'n2': 'bayesian_update',
            'n3': 'statistical_gate'
        },
        'TYPE_C': {
            'n1': 'graph_element_collection',
            'n2': 'topological_overlay',
            'n3': 'cycle_detection_veto'
        },
        'TYPE_D': {
            'n1': 'financial_aggregation',
            'n2': 'weighted_financial_mean',
            'n3': 'sufficiency_gate'
        },
        'TYPE_E': {
            'n1': 'fact_collation',
            'n2': 'logical_consistency_check',
            'n3': 'contradiction_dominance'
        }
    }

    def __init__(self, selection_path: Path, classification_path: Path, dispensary_path: Path):
        """Initialize contract generator"""
        with open(selection_path) as f:
            self.selections = json.load(f)['selections']

        with open(classification_path) as f:
            self.classification = json.load(f)['contracts']

        with open(dispensary_path) as f:
            self.dispensary = json.load(f)

    def generate_method_binding(self, question_id: str, question_type: str) -> Dict[str, Any]:
        """Generate method_binding section for a contract"""
        selection = self.selections[question_id]

        # Extract selected methods per phase
        phase_a_methods = []
        phase_b_methods = []
        phase_c_methods = []

        for level, data in selection['method_selection'].items():
            methods = data['selected_methods']

            for m in methods:
                method_id = m['method_id']
                class_name, method_name = method_id.split('.', 1)

                binding = {
                    'class_name': class_name,
                    'method_name': method_name,
                    'mother_file': self.dispensary.get(class_name, {}).get('file_path', 'unknown'),
                    'provides': m.get('provides', []),
                    'requires': m.get('requires', []),
                    'level': level,
                    'description': f"{method_id} - {m.get('rationale', '')[:100]}"
                }

                if level == 'N1-EMP':
                    phase_a_methods.append(binding)
                elif level == 'N2-INF':
                    phase_b_methods.append(binding)
                elif level == 'N3-AUD':
                    phase_c_methods.append(binding)

        return {
            'orchestration_mode': 'epistemological_pipeline',
            'contract_type': question_type,
            'method_count': len(phase_a_methods) + len(phase_b_methods) + len(phase_c_methods),
            'execution_phases': {
                'phase_A_construction': {
                    'methods': phase_a_methods,
                    'fusion_strategy': self.FUSION_STRATEGIES[question_type]['n1']
                },
                'phase_B_computation': {
                    'methods': phase_b_methods,
                    'fusion_strategy': self.FUSION_STRATEGIES[question_type]['n2']
                },
                'phase_C_litigation': {
                    'methods': phase_c_methods,
                    'fusion_strategy': self.FUSION_STRATEGIES[question_type]['n3']
                }
            }
        }

    def generate_evidence_assembly(self, question_type: str) -> Dict[str, Any]:
        """Generate evidence_assembly section per contract type"""

        type_rules = {
            'TYPE_A': [
                {
                    'rule_id': 'R1_semantic_bundling',
                    'rule_type': 'empirical_basis',
                    'target': 'semantic_bundles',
                    'merge_strategy': 'semantic_bundling',
                    'output_type': 'FACT'
                },
                {
                    'rule_id': 'R2_dempster_combination',
                    'rule_type': 'corroboration',
                    'target': 'belief_mass',
                    'merge_strategy': 'dempster_shafer',
                    'output_type': 'PARAMETER'
                },
                {
                    'rule_id': 'R3_contradiction_veto',
                    'rule_type': 'robustness_gate',
                    'target': 'validated_belief',
                    'merge_strategy': 'contradiction_veto',
                    'output_type': 'CONSTRAINT'
                },
                {
                    'rule_id': 'R4_synthesis',
                    'rule_type': 'synthesis',
                    'target': 'human_answer',
                    'merge_strategy': 'carver_doctoral_synthesis',
                    'output_type': 'NARRATIVE'
                }
            ],
            'TYPE_B': [
                {
                    'rule_id': 'R1_evidence_collection',
                    'rule_type': 'empirical_basis',
                    'target': 'evidence_array',
                    'merge_strategy': 'evidence_concatenation',
                    'output_type': 'FACT'
                },
                {
                    'rule_id': 'R2_bayesian_inference',
                    'rule_type': 'probabilistic_update',
                    'target': 'posterior_belief',
                    'merge_strategy': 'bayesian_update',
                    'output_type': 'PARAMETER'
                },
                {
                    'rule_id': 'R3_statistical_gate',
                    'rule_type': 'robustness_gate',
                    'target': 'validated_posterior',
                    'merge_strategy': 'statistical_gate',
                    'output_type': 'CONSTRAINT'
                },
                {
                    'rule_id': 'R4_synthesis',
                    'rule_type': 'synthesis',
                    'target': 'human_answer',
                    'merge_strategy': 'carver_doctoral_synthesis',
                    'output_type': 'NARRATIVE'
                }
            ],
            'TYPE_C': [
                {
                    'rule_id': 'R1_graph_collection',
                    'rule_type': 'structure_definition',
                    'target': 'graph_elements',
                    'merge_strategy': 'graph_element_collection',
                    'output_type': 'FACT'
                },
                {
                    'rule_id': 'R2_topology_overlay',
                    'rule_type': 'edge_inference',
                    'target': 'weighted_dag',
                    'merge_strategy': 'topological_overlay',
                    'output_type': 'PARAMETER'
                },
                {
                    'rule_id': 'R3_cycle_veto',
                    'rule_type': 'validity_check',
                    'target': 'validated_dag',
                    'merge_strategy': 'cycle_detection_veto',
                    'output_type': 'CONSTRAINT'
                },
                {
                    'rule_id': 'R4_synthesis',
                    'rule_type': 'synthesis',
                    'target': 'human_answer',
                    'merge_strategy': 'carver_doctoral_synthesis',
                    'output_type': 'NARRATIVE'
                }
            ],
            'TYPE_D': [
                {
                    'rule_id': 'R1_financial_agg',
                    'rule_type': 'empirical_basis',
                    'target': 'normalized_financials',
                    'merge_strategy': 'financial_aggregation',
                    'output_type': 'FACT'
                },
                {
                    'rule_id': 'R2_weighted_mean',
                    'rule_type': 'computation',
                    'target': 'sufficiency_index',
                    'merge_strategy': 'weighted_financial_mean',
                    'output_type': 'PARAMETER'
                },
                {
                    'rule_id': 'R3_sufficiency_gate',
                    'rule_type': 'financial_coherence_audit',
                    'target': 'validated_viability',
                    'merge_strategy': 'sufficiency_gate',
                    'output_type': 'CONSTRAINT'
                },
                {
                    'rule_id': 'R4_synthesis',
                    'rule_type': 'synthesis',
                    'target': 'human_answer',
                    'merge_strategy': 'carver_doctoral_synthesis',
                    'output_type': 'NARRATIVE'
                }
            ],
            'TYPE_E': [
                {
                    'rule_id': 'R1_fact_collation',
                    'rule_type': 'empirical_basis',
                    'target': 'logical_facts',
                    'merge_strategy': 'fact_collation',
                    'output_type': 'FACT'
                },
                {
                    'rule_id': 'R2_consistency_check',
                    'rule_type': 'logical_validation',
                    'target': 'consistency_score',
                    'merge_strategy': 'logical_consistency_check',
                    'output_type': 'PARAMETER'
                },
                {
                    'rule_id': 'R3_contradiction_dominance',
                    'rule_type': 'logical_veto',
                    'target': 'validated_consistency',
                    'merge_strategy': 'contradiction_dominance',
                    'output_type': 'CONSTRAINT'
                },
                {
                    'rule_id': 'R4_synthesis',
                    'rule_type': 'synthesis',
                    'target': 'human_answer',
                    'merge_strategy': 'carver_doctoral_synthesis',
                    'output_type': 'NARRATIVE'
                }
            ]
        }

        return {
            'engine': 'EVIDENCE_NEXUS',
            'module': 'farfan_pipeline.phases.Phase_two.evidence_nexus',
            'class_name': 'EvidenceNexus',
            'method_name': 'assemble',
            'assembly_rules': type_rules.get(question_type, [])
        }

    def generate_contract(self, question_id: str, policy_area: str) -> Dict[str, Any]:
        """Generate a single executor contract"""
        question_data = self.classification[question_id]
        question_type = question_data['type']

        contract_id = f"{policy_area}_{question_id}_CONTRACT"

        # Extract dimension from question
        dimension_code = question_data.get('generic_code', 'D0.Q0').split('.')[0]

        contract = {
            'contract_id': contract_id,
            'policy_area': policy_area,
            'dimension_code': dimension_code,
            'question_id': question_id,
            'question_type': question_type,
            'question_text': question_data['question_text'],
            'question_title': question_data.get('question_title', ''),

            'method_binding': self.generate_method_binding(question_id, question_type),
            'evidence_assembly': self.generate_evidence_assembly(question_type),

            'epistemological_justification': question_data.get('epistemological_justification', ''),
            'fusion_strategies': self.FUSION_STRATEGIES[question_type],

            'n1_strategy_refined': question_data.get('n1_strategy_refined', {}),
            'n2_strategy_refined': question_data.get('n2_strategy_refined', {}),
            'n3_fusion_refined': question_data.get('n3_fusion_refined', {})
        }

        return contract

    def generate_all_contracts(self) -> Dict[str, Any]:
        """Generate all 300 contracts (30 questions × 10 policy areas)"""
        contracts = {}

        question_ids = [f"Q{i:03d}" for i in range(1, 31)]

        for policy_area in self.POLICY_AREAS:
            for question_id in question_ids:
                if question_id not in self.classification:
                    continue

                contract_id = f"{policy_area}_{question_id}_CONTRACT"
                contracts[contract_id] = self.generate_contract(question_id, policy_area)

        return {
            'metadata': {
                'version': '1.0.0',
                'date': '2025-12-31',
                'total_contracts': len(contracts),
                'policy_areas': len(self.POLICY_AREAS),
                'questions_per_area': 30,
                'protocol': 'PROMPT_MAESTRO_V1',
                'compliance': ['GNEA_v2.0.0', 'EPISTEMOLOGICAL_GUIDE_V4']
            },
            'contracts': contracts
        }


def main():
    """Generate all 300 executor contracts"""
    print("="*80)
    print("GENERATING 300 EXECUTOR CONTRACTS")
    print("="*80)

    base_path = Path("/home/user/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL")

    selection_path = base_path / "artifacts/data/methods/method_selection_per_question.json"
    classification_path = base_path / "src/farfan_pipeline/phases/Phase_two/epistemological_assets/PHASE2_CLASSIFICATION_MASTER_ENRICHED.json"
    dispensary_path = base_path / "src/farfan_pipeline/phases/Phase_two/epistemological_assets/METHODS_DISPENSARY_V4.json"
    output_path = base_path / "artifacts/data/contracts/EXECUTOR_CONTRACTS_300_FINAL.json"

    generator = ContractGenerator(selection_path, classification_path, dispensary_path)

    print(f"\n[Generating Contracts...]")
    all_contracts = generator.generate_all_contracts()

    print(f"  Generated: {all_contracts['metadata']['total_contracts']} contracts")
    print(f"  Policy Areas: {all_contracts['metadata']['policy_areas']}")
    print(f"  Questions per Area: {all_contracts['metadata']['questions_per_area']}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(all_contracts, f, indent=2, ensure_ascii=False)

    print(f"\n[Saved]")
    print(f"  File: {output_path}")
    print(f"  Size: {output_path.stat().st_size / 1024:.1f} KB")

    # Generate summary statistics
    type_counts = {}
    for contract in all_contracts['contracts'].values():
        qtype = contract['question_type']
        type_counts[qtype] = type_counts.get(qtype, 0) + 1

    print(f"\n[Contract Distribution by TYPE]")
    for qtype, count in sorted(type_counts.items()):
        print(f"  {qtype}: {count} contracts")

    print(f"\n{'='*80}")
    print("✅ 300 EXECUTOR CONTRACTS GENERATED")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()

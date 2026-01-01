#!/usr/bin/env python3
"""
Comprehensive Audit Script for questionnaire_monolith.json

This script performs an equity-focused audit of the questionnaire structure,
analyzing hierarchy, coverage, balance, and identifying gaps across:
- Signal and expected_elements richness
- Validation contract diversity
- Scoring modalities
- Cluster and policy area coverage
- Documentation completeness
- Expected elements granularity
- Intersectionality and cross-cutting issues
"""

import json
import sys
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime


class QuestionnaireAuditor:
    """Comprehensive auditor for questionnaire_monolith.json"""
    
    def __init__(self, json_path: str):
        self.json_path = json_path
        self.data: Dict[str, Any] = {}
        self.micro_questions: List[Dict] = []
        self.audit_results: Dict[str, Any] = {}
        
    def load_data(self) -> None:
        """Load the questionnaire JSON file"""
        with open(self.json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.micro_questions = self.data.get('blocks', {}).get('micro_questions', [])
        print(f"✓ Loaded {len(self.micro_questions)} micro questions")
    
    def audit_structure_hierarchy(self) -> Dict[str, Any]:
        """Audit 1: Structure and hierarchy analysis"""
        print("\n=== AUDIT 1: Structure & Hierarchy ===")
        
        canonical = self.data.get('canonical_notation', {})
        dimensions = canonical.get('dimensions', {})
        policy_areas = canonical.get('policy_areas', {})
        clusters = canonical.get('clusters', {})
        
        result = {
            'dimensions_count': len(dimensions),
            'policy_areas_count': len(policy_areas),
            'clusters_count': len(clusters),
            'total_micro_questions': len(self.micro_questions),
            'dimensions': list(dimensions.keys()),
            'policy_areas': list(policy_areas.keys()),
            'clusters': list(clusters.keys()) if clusters else []
        }
        
        print(f"  - Dimensions: {result['dimensions_count']}")
        print(f"  - Policy Areas: {result['policy_areas_count']}")
        print(f"  - Clusters: {result['clusters_count']}")
        print(f"  - Micro Questions: {result['total_micro_questions']}")
        
        return result
    
    def audit_classification_distribution(self) -> Dict[str, Any]:
        """Audit 2: Classification distribution across dimensions, policy areas, clusters"""
        print("\n=== AUDIT 2: Classification Distribution ===")
        
        dimension_counts = defaultdict(int)
        policy_area_counts = defaultdict(int)
        cluster_counts = defaultdict(int)
        
        # Track questions without proper classification
        missing_dimension = []
        missing_policy_area = []
        missing_cluster = []
        
        for i, q in enumerate(self.micro_questions):
            q_id = q.get('question_id', f'Q{i+1:03d}')
            dim = q.get('dimension_id', None)
            cluster = q.get('cluster_id', None)
            
            # Check for policy area in base_slot pattern (e.g., "D1-Q1-PA01")
            base_slot = q.get('base_slot', '')
            pa = None
            if '-PA' in base_slot:
                pa = base_slot.split('-PA')[-1][:2]
                pa = f'PA{pa}'
            
            if dim:
                dimension_counts[dim] += 1
            else:
                missing_dimension.append(q_id)
            
            if pa:
                policy_area_counts[pa] += 1
            else:
                missing_policy_area.append(q_id)
            
            if cluster:
                cluster_counts[cluster] += 1
            else:
                missing_cluster.append(q_id)
        
        result = {
            'by_dimension': dict(dimension_counts),
            'by_policy_area': dict(policy_area_counts),
            'by_cluster': dict(cluster_counts),
            'missing_classification': {
                'dimension': len(missing_dimension),
                'policy_area': len(missing_policy_area),
                'cluster': len(missing_cluster)
            }
        }
        
        print(f"\n  Distribution by Dimension:")
        for dim, count in sorted(dimension_counts.items()):
            print(f"    {dim}: {count} questions")
        
        print(f"\n  Distribution by Policy Area:")
        for pa, count in sorted(policy_area_counts.items()):
            print(f"    {pa}: {count} questions")
        
        print(f"\n  Distribution by Cluster:")
        for cluster, count in sorted(cluster_counts.items()):
            print(f"    {cluster}: {count} questions")
        
        if missing_dimension or missing_policy_area or missing_cluster:
            print(f"\n  ⚠ Missing Classifications:")
            if missing_dimension:
                print(f"    - {len(missing_dimension)} questions without dimension")
            if missing_policy_area:
                print(f"    - {len(missing_policy_area)} questions without policy area")
            if missing_cluster:
                print(f"    - {len(missing_cluster)} questions without cluster")
        
        return result
    
    def audit_expected_elements_richness(self) -> Dict[str, Any]:
        """Audit 3: Expected elements richness and granularity"""
        print("\n=== AUDIT 3: Expected Elements Richness ===")
        
        total_with_expected = 0
        total_without_expected = 0
        element_type_counts = Counter()
        required_counts = defaultdict(int)
        granularity_scores = []
        vague_elements = []
        
        for i, q in enumerate(self.micro_questions):
            q_id = q.get('question_id', f'Q{i+1:03d}')
            expected = q.get('expected_elements', [])
            
            if expected:
                total_with_expected += 1
                granularity_scores.append(len(expected))
                
                for elem in expected:
                    elem_type = elem.get('type', 'unspecified')
                    element_type_counts[elem_type] += 1
                    
                    if elem.get('required', False):
                        required_counts[elem_type] += 1
                    
                    # Flag vague elements
                    if elem_type in ['texto_general', 'unspecified', 'general']:
                        vague_elements.append((q_id, elem_type))
            else:
                total_without_expected += 1
        
        avg_granularity = sum(granularity_scores) / len(granularity_scores) if granularity_scores else 0
        
        result = {
            'with_expected_elements': total_with_expected,
            'without_expected_elements': total_without_expected,
            'average_elements_per_question': avg_granularity,
            'element_types_used': dict(element_type_counts),
            'required_elements': dict(required_counts),
            'vague_elements_count': len(vague_elements)
        }
        
        print(f"  - Questions with expected_elements: {total_with_expected} ({total_with_expected/len(self.micro_questions)*100:.1f}%)")
        print(f"  - Questions without expected_elements: {total_without_expected}")
        print(f"  - Average elements per question: {avg_granularity:.2f}")
        print(f"  - Unique element types: {len(element_type_counts)}")
        print(f"  - Vague/unspecified elements: {len(vague_elements)}")
        
        print(f"\n  Top element types:")
        for elem_type, count in element_type_counts.most_common(10):
            print(f"    {elem_type}: {count}")
        
        return result
    
    def audit_signals_richness(self) -> Dict[str, Any]:
        """Audit 4: Signals richness and depth"""
        print("\n=== AUDIT 4: Signals Richness ===")
        
        total_with_signals = 0
        total_without_signals = 0
        signal_counts = []
        signal_types = Counter()
        
        for i, q in enumerate(self.micro_questions):
            signals = q.get('signals', [])
            
            if signals:
                total_with_signals += 1
                signal_counts.append(len(signals))
                
                for signal in signals:
                    if isinstance(signal, dict):
                        signal_type = signal.get('type', 'unspecified')
                        signal_types[signal_type] += 1
            else:
                total_without_signals += 1
        
        avg_signals = sum(signal_counts) / len(signal_counts) if signal_counts else 0
        
        result = {
            'with_signals': total_with_signals,
            'without_signals': total_without_signals,
            'average_signals_per_question': avg_signals,
            'signal_types': dict(signal_types)
        }
        
        print(f"  - Questions with signals: {total_with_signals} ({total_with_signals/len(self.micro_questions)*100:.1f}%)")
        print(f"  - Questions without signals: {total_without_signals}")
        print(f"  - Average signals per question: {avg_signals:.2f}")
        
        return result
    
    def audit_validation_contracts(self) -> Dict[str, Any]:
        """Audit 5: Validation contract diversity and distribution"""
        print("\n=== AUDIT 5: Validation Contracts ===")
        
        total_with_validation = 0
        total_without_validation = 0
        validation_types = Counter()
        abort_conditions = Counter()
        
        for i, q in enumerate(self.micro_questions):
            failure_contract = q.get('failure_contract', {})
            validation_contract = q.get('validation_contract', {})
            
            has_validation = bool(failure_contract or validation_contract)
            
            if has_validation:
                total_with_validation += 1
                
                # Analyze failure contract
                if failure_contract:
                    abort_if = failure_contract.get('abort_if', [])
                    for condition in abort_if:
                        abort_conditions[condition] += 1
                
                # Analyze validation contract
                if validation_contract:
                    for key in validation_contract.keys():
                        validation_types[key] += 1
            else:
                total_without_validation += 1
        
        result = {
            'with_validation': total_with_validation,
            'without_validation': total_without_validation,
            'abort_conditions': dict(abort_conditions),
            'validation_types': dict(validation_types)
        }
        
        print(f"  - Questions with validation: {total_with_validation} ({total_with_validation/len(self.micro_questions)*100:.1f}%)")
        print(f"  - Questions without validation: {total_without_validation}")
        print(f"  - Unique abort conditions: {len(abort_conditions)}")
        
        print(f"\n  Top abort conditions:")
        for condition, count in abort_conditions.most_common(10):
            print(f"    {condition}: {count}")
        
        return result
    
    def audit_scoring_modalities(self) -> Dict[str, Any]:
        """Audit 6: Scoring modalities (TYPE_A-F) usage and balance"""
        print("\n=== AUDIT 6: Scoring Modalities ===")
        
        modality_counts = Counter()
        modality_by_dimension = defaultdict(Counter)
        modality_by_policy_area = defaultdict(Counter)
        
        for i, q in enumerate(self.micro_questions):
            scoring = q.get('scoring', {})
            if isinstance(scoring, dict):
                modality = scoring.get('modality', q.get('scoring_modality', 'UNSPECIFIED'))
            else:
                modality = q.get('scoring_modality', 'UNSPECIFIED')
            
            modality_counts[modality] += 1
            
            dim = q.get('dimension_id', 'UNKNOWN')
            modality_by_dimension[dim][modality] += 1
            
            base_slot = q.get('base_slot', '')
            pa = 'UNKNOWN'
            if '-PA' in base_slot:
                pa = base_slot.split('-PA')[-1][:2]
                pa = f'PA{pa}'
            modality_by_policy_area[pa][modality] += 1
        
        result = {
            'overall_modality_distribution': dict(modality_counts),
            'by_dimension': {dim: dict(counts) for dim, counts in modality_by_dimension.items()},
            'by_policy_area': {pa: dict(counts) for pa, counts in modality_by_policy_area.items()}
        }
        
        print(f"  Overall modality distribution:")
        for modality, count in sorted(modality_counts.items()):
            print(f"    {modality}: {count} ({count/len(self.micro_questions)*100:.1f}%)")
        
        return result
    
    def audit_method_sets(self) -> Dict[str, Any]:
        """Audit 7: Method sets coverage and patterns"""
        print("\n=== AUDIT 7: Method Sets Coverage ===")
        
        total_with_methods = 0
        total_without_methods = 0
        method_counts = []
        class_usage = Counter()
        function_usage = Counter()
        method_type_usage = Counter()
        
        for i, q in enumerate(self.micro_questions):
            method_sets = q.get('method_sets', [])
            
            if method_sets:
                total_with_methods += 1
                method_counts.append(len(method_sets))
                
                for method in method_sets:
                    class_name = method.get('class', 'Unknown')
                    function_name = method.get('function', 'Unknown')
                    method_type = method.get('method_type', 'unspecified')
                    
                    class_usage[class_name] += 1
                    function_usage[f"{class_name}.{function_name}"] += 1
                    method_type_usage[method_type] += 1
            else:
                total_without_methods += 1
        
        avg_methods = sum(method_counts) / len(method_counts) if method_counts else 0
        
        result = {
            'with_method_sets': total_with_methods,
            'without_method_sets': total_without_methods,
            'average_methods_per_question': avg_methods,
            'unique_classes': len(class_usage),
            'unique_functions': len(function_usage),
            'method_types': dict(method_type_usage),
            'top_classes': dict(class_usage.most_common(15)),
            'top_functions': dict(function_usage.most_common(15))
        }
        
        print(f"  - Questions with method_sets: {total_with_methods} ({total_with_methods/len(self.micro_questions)*100:.1f}%)")
        print(f"  - Questions without method_sets: {total_without_methods}")
        print(f"  - Average methods per question: {avg_methods:.2f}")
        print(f"  - Unique classes used: {len(class_usage)}")
        print(f"  - Unique functions used: {len(function_usage)}")
        
        print(f"\n  Top 5 classes:")
        for class_name, count in class_usage.most_common(5):
            print(f"    {class_name}: {count}")
        
        return result
    
    def audit_documentation(self) -> Dict[str, Any]:
        """Audit 8: Documentation completeness"""
        print("\n=== AUDIT 8: Documentation Completeness ===")
        
        fields_to_check = [
            'question_id',
            'text',
            'rationale',
            'documentation',
            'description',
            'context',
            'guidance'
        ]
        
        field_presence = defaultdict(int)
        fully_documented = 0
        poorly_documented = []
        
        for i, q in enumerate(self.micro_questions):
            q_id = q.get('question_id', f'Q{i+1:03d}')
            doc_count = 0
            
            for field in fields_to_check:
                if field in q and q[field]:
                    field_presence[field] += 1
                    doc_count += 1
            
            if doc_count >= 5:
                fully_documented += 1
            elif doc_count < 2:
                poorly_documented.append(q_id)
        
        result = {
            'field_presence': dict(field_presence),
            'fully_documented': fully_documented,
            'poorly_documented_count': len(poorly_documented),
            'documentation_coverage': {
                field: (count / len(self.micro_questions) * 100)
                for field, count in field_presence.items()
            }
        }
        
        print(f"  - Fully documented questions: {fully_documented} ({fully_documented/len(self.micro_questions)*100:.1f}%)")
        print(f"  - Poorly documented questions: {len(poorly_documented)}")
        
        print(f"\n  Field presence:")
        for field in fields_to_check:
            count = field_presence.get(field, 0)
            pct = count / len(self.micro_questions) * 100
            print(f"    {field}: {count} ({pct:.1f}%)")
        
        return result
    
    def audit_intersectionality(self) -> Dict[str, Any]:
        """Audit 9: Cross-cutting issues and intersectionality"""
        print("\n=== AUDIT 9: Intersectionality & Cross-Cutting Issues ===")
        
        # Keywords for cross-cutting themes
        gender_keywords = ['género', 'mujer', 'mujeres', 'femenino', 'masculino', 'lgbti', 'diversidad sexual']
        rights_keywords = ['derecho', 'derechos', 'humanos', 'dignidad', 'libertad']
        vulnerability_keywords = ['vulnerable', 'vulnerabilidad', 'pobreza', 'exclusión', 'marginación', 'discriminación']
        equity_keywords = ['equidad', 'igualdad', 'inclusión', 'acceso', 'participación']
        
        gender_mentions = 0
        rights_mentions = 0
        vulnerability_mentions = 0
        equity_mentions = 0
        
        cross_cutting_by_policy_area = defaultdict(lambda: {'gender': 0, 'rights': 0, 'vulnerability': 0, 'equity': 0})
        
        for i, q in enumerate(self.micro_questions):
            q_text = str(q.get('text', '')).lower()
            
            base_slot = q.get('base_slot', '')
            pa = 'UNKNOWN'
            if '-PA' in base_slot:
                pa = base_slot.split('-PA')[-1][:2]
                pa = f'PA{pa}'
            
            has_gender = any(kw in q_text for kw in gender_keywords)
            has_rights = any(kw in q_text for kw in rights_keywords)
            has_vulnerability = any(kw in q_text for kw in vulnerability_keywords)
            has_equity = any(kw in q_text for kw in equity_keywords)
            
            if has_gender:
                gender_mentions += 1
                cross_cutting_by_policy_area[pa]['gender'] += 1
            if has_rights:
                rights_mentions += 1
                cross_cutting_by_policy_area[pa]['rights'] += 1
            if has_vulnerability:
                vulnerability_mentions += 1
                cross_cutting_by_policy_area[pa]['vulnerability'] += 1
            if has_equity:
                equity_mentions += 1
                cross_cutting_by_policy_area[pa]['equity'] += 1
        
        result = {
            'gender_mentions': gender_mentions,
            'rights_mentions': rights_mentions,
            'vulnerability_mentions': vulnerability_mentions,
            'equity_mentions': equity_mentions,
            'by_policy_area': dict(cross_cutting_by_policy_area)
        }
        
        print(f"  - Gender mentions: {gender_mentions} ({gender_mentions/len(self.micro_questions)*100:.1f}%)")
        print(f"  - Rights mentions: {rights_mentions} ({rights_mentions/len(self.micro_questions)*100:.1f}%)")
        print(f"  - Vulnerability mentions: {vulnerability_mentions} ({vulnerability_mentions/len(self.micro_questions)*100:.1f}%)")
        print(f"  - Equity mentions: {equity_mentions} ({equity_mentions/len(self.micro_questions)*100:.1f}%)")
        
        return result
    
    def identify_equity_risks(self) -> Dict[str, Any]:
        """Audit 10: Identify equity risks and imbalances"""
        print("\n=== AUDIT 10: Equity Risks & Imbalances ===")
        
        risks = []
        
        # Check distribution imbalances
        dimension_counts = defaultdict(int)
        for q in self.micro_questions:
            dim = q.get('dimension_id', 'UNKNOWN')
            dimension_counts[dim] += 1
        
        if dimension_counts:
            avg_per_dim = sum(dimension_counts.values()) / len(dimension_counts)
            for dim, count in dimension_counts.items():
                if count < avg_per_dim * 0.7:
                    risks.append({
                        'type': 'under_representation',
                        'area': f'Dimension {dim}',
                        'severity': 'MEDIUM',
                        'description': f'{dim} has only {count} questions, below average of {avg_per_dim:.0f}'
                    })
        
        # Check validation coverage imbalance
        validation_by_dim = defaultdict(lambda: {'with': 0, 'without': 0})
        for q in self.micro_questions:
            dim = q.get('dimension_id', 'UNKNOWN')
            has_validation = bool(q.get('failure_contract') or q.get('validation_contract'))
            if has_validation:
                validation_by_dim[dim]['with'] += 1
            else:
                validation_by_dim[dim]['without'] += 1
        
        for dim, counts in validation_by_dim.items():
            total = counts['with'] + counts['without']
            if total > 0:
                validation_pct = counts['with'] / total * 100
                if validation_pct < 50:
                    risks.append({
                        'type': 'validation_gap',
                        'area': f'Dimension {dim}',
                        'severity': 'HIGH',
                        'description': f'Only {validation_pct:.1f}% of questions in {dim} have validation'
                    })
        
        result = {
            'total_risks': len(risks),
            'risks': risks
        }
        
        print(f"  - Total equity risks identified: {len(risks)}")
        for risk in risks[:10]:
            print(f"    [{risk['severity']}] {risk['type']}: {risk['description']}")
        
        return result
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        print("\n" + "="*60)
        print("COMPREHENSIVE AUDIT OF questionnaire_monolith.json")
        print("="*60)
        
        self.audit_results = {
            'audit_metadata': {
                'timestamp': datetime.now().isoformat(),
                'file_path': self.json_path,
                'auditor_version': '1.0.0'
            },
            'structure_hierarchy': self.audit_structure_hierarchy(),
            'classification_distribution': self.audit_classification_distribution(),
            'expected_elements_richness': self.audit_expected_elements_richness(),
            'signals_richness': self.audit_signals_richness(),
            'validation_contracts': self.audit_validation_contracts(),
            'scoring_modalities': self.audit_scoring_modalities(),
            'method_sets': self.audit_method_sets(),
            'documentation': self.audit_documentation(),
            'intersectionality': self.audit_intersectionality(),
            'equity_risks': self.identify_equity_risks()
        }
        
        return self.audit_results
    
    def save_report(self, output_path: str) -> None:
        """Save audit report to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.audit_results, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Audit report saved to: {output_path}")


def main():
    """Main execution function"""
    repo_root = Path(__file__).parent.parent.parent
    json_path = repo_root / 'canonic_questionnaire_central' / 'questionnaire_monolith.json'
    output_path = repo_root / 'artifacts' / 'reports' / 'audit' / 'questionnaire_monolith_audit_report.json'
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Run audit
    auditor = QuestionnaireAuditor(str(json_path))
    auditor.load_data()
    auditor.generate_report()
    auditor.save_report(str(output_path))
    
    print("\n" + "="*60)
    print("AUDIT COMPLETE")
    print("="*60)
    print(f"\nSee detailed results in: {output_path}")


if __name__ == '__main__':
    main()

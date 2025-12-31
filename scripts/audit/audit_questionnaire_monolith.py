#!/usr/bin/env python3
"""
Comprehensive Audit Script for questionnaire_monolith.json

This script performs a detailed analysis of the questionnaire structure to identify:
1. Signal/Element Richness gaps
2. Validation Diversity issues
3. Scoring Modality imbalances
4. Cluster & Policy Area Coverage
5. Documentation gaps
6. Expected Elements granularity
7. Equity imbalances

Author: FARFAN Audit Team
Date: 2025-12-31
"""

import json
import sys
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Any, Tuple


class QuestionnaireAuditor:
    """Auditor for questionnaire_monolith.json structure and content."""

    def __init__(self, json_path: str):
        """Initialize the auditor with the path to questionnaire_monolith.json."""
        self.json_path = Path(json_path)
        self.data = self._load_json()
        self.micro_questions = self.data.get('blocks', {}).get('micro_questions', [])
        self.canonical_notation = self.data.get('canonical_notation', {})
        
        # Statistics containers
        self.stats = {
            'total_questions': len(self.micro_questions),
            'by_policy_area': Counter(),
            'by_dimension': Counter(),
            'by_cluster': Counter(),
            'by_scoring_modality': Counter(),
            'validation_counts': [],
            'signal_richness': [],
            'expected_elements_counts': [],
            'method_sets_counts': [],
            'missing_fields': defaultdict(list),
            'empty_fields': defaultdict(list),
        }

    def _load_json(self) -> Dict:
        """Load and parse the JSON file."""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"ERROR: File not found: {self.json_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON: {e}")
            sys.exit(1)

    def audit_structure(self) -> Dict[str, Any]:
        """Audit the overall structure of the questionnaire."""
        return {
            'schema_version': self.data.get('schema_version', 'MISSING'),
            'version': self.data.get('version', 'MISSING'),
            'generated_at': self.data.get('generated_at', 'MISSING'),
            'top_level_keys': list(self.data.keys()),
            'has_integrity': 'integrity' in self.data,
            'has_observability': 'observability' in self.data,
        }

    def audit_canonical_notation(self) -> Dict[str, Any]:
        """Audit the canonical notation section."""
        dimensions = self.canonical_notation.get('dimensions', {})
        policy_areas = self.canonical_notation.get('policy_areas', {})
        clusters = self.canonical_notation.get('clusters', {})
        
        return {
            'dimensions_count': len(dimensions),
            'dimensions_list': list(dimensions.keys()),
            'policy_areas_count': len(policy_areas),
            'policy_areas_list': list(policy_areas.keys()),
            'clusters_count': len(clusters),
            'clusters_list': list(clusters.keys()),
        }

    def audit_micro_questions(self) -> Dict[str, Any]:
        """Perform detailed audit of micro questions."""
        issues = {
            'missing_signals': [],
            'weak_signals': [],
            'missing_expected_elements': [],
            'vague_expected_elements': [],
            'missing_validations': [],
            'weak_validations': [],
            'missing_failure_contract': [],
            'missing_scoring_modality': [],
            'missing_method_sets': [],
            'missing_documentation': [],
            'missing_patterns': [],
        }
        
        for idx, q in enumerate(self.micro_questions):
            q_id = q.get('question_id', f'UNKNOWN_{idx}')
            
            # Collect statistics
            policy_area = q.get('policy_area_id', 'UNKNOWN')
            dimension = q.get('dimension_id', 'UNKNOWN')
            cluster = q.get('cluster_id', 'UNKNOWN')
            scoring_modality = q.get('scoring_modality', 'UNKNOWN')
            
            self.stats['by_policy_area'][policy_area] += 1
            self.stats['by_dimension'][dimension] += 1
            self.stats['by_cluster'][cluster] += 1
            self.stats['by_scoring_modality'][scoring_modality] += 1
            
            # Note: 'signals' field does not exist in current schema v2.0.0
            # Keeping this check for future compatibility
            signals = q.get('signals', [])
            if 'signals' in q and not signals:
                issues['missing_signals'].append(q_id)
            elif 'signals' in q and len(signals) < 3:
                issues['weak_signals'].append((q_id, len(signals)))
            
            # Audit expected_elements (can be list of dicts or strings)
            expected_elements = q.get('expected_elements', [])
            if not expected_elements:
                issues['missing_expected_elements'].append(q_id)
            else:
                self.stats['expected_elements_counts'].append(len(expected_elements))
                # Check for elements with insufficient detail
                weak_elements = []
                for e in expected_elements:
                    if isinstance(e, dict):
                        # Check if dict has minimal info (type-only)
                        if len(e.keys()) == 1 and 'type' in e:
                            weak_elements.append(e)
                    elif isinstance(e, str) and len(e.split()) <= 2:
                        weak_elements.append(e)
                
                if len(weak_elements) > len(expected_elements) * 0.5:
                    issues['vague_expected_elements'].append((q_id, len(weak_elements), len(expected_elements)))
            
            # Audit validations
            validations = q.get('validations', [])
            self.stats['validation_counts'].append(len(validations))
            if not validations:
                issues['missing_validations'].append(q_id)
            elif len(validations) < 2:
                issues['weak_validations'].append((q_id, len(validations)))
            
            # Audit failure_contract (should have abort_if or conditions)
            failure_contract = q.get('failure_contract', {})
            if not failure_contract:
                issues['missing_failure_contract'].append(q_id)
            elif not failure_contract.get('abort_if') and not failure_contract.get('conditions'):
                issues['missing_failure_contract'].append(q_id)
            
            # Audit scoring_modality
            if not scoring_modality or scoring_modality == 'UNKNOWN':
                issues['missing_scoring_modality'].append(q_id)
            
            # Audit method_sets
            method_sets = q.get('method_sets', [])
            self.stats['method_sets_counts'].append(len(method_sets))
            if not method_sets:
                issues['missing_method_sets'].append(q_id)
            
            # Audit documentation/definition
            definition = q.get('definition', '')
            if not definition or len(definition) < 20:
                issues['missing_documentation'].append(q_id)
            
            # Audit patterns
            patterns = q.get('patterns', [])
            if not patterns:
                issues['missing_patterns'].append(q_id)
        
        return issues

    def calculate_equity_metrics(self) -> Dict[str, Any]:
        """Calculate metrics related to equity and balance across the questionnaire."""
        # Calculate standard deviation and coefficient of variation for distributions
        
        # Questions per policy area balance
        pa_counts = list(self.stats['by_policy_area'].values())
        pa_mean = sum(pa_counts) / len(pa_counts) if pa_counts else 0
        pa_variance = sum((x - pa_mean) ** 2 for x in pa_counts) / len(pa_counts) if pa_counts else 0
        pa_std = pa_variance ** 0.5
        pa_cv = (pa_std / pa_mean * 100) if pa_mean > 0 else 0
        
        # Validations per question balance
        val_counts = self.stats['validation_counts']
        val_mean = sum(val_counts) / len(val_counts) if val_counts else 0
        val_variance = sum((x - val_mean) ** 2 for x in val_counts) / len(val_counts) if val_counts else 0
        val_std = val_variance ** 0.5
        val_cv = (val_std / val_mean * 100) if val_mean > 0 else 0
        
        # Expected elements per question balance
        ee_counts = self.stats['expected_elements_counts']
        ee_mean = sum(ee_counts) / len(ee_counts) if ee_counts else 0
        ee_variance = sum((x - ee_mean) ** 2 for x in ee_counts) / len(ee_counts) if ee_counts else 0
        ee_std = ee_variance ** 0.5
        ee_cv = (ee_std / ee_mean * 100) if ee_mean > 0 else 0
        
        return {
            'policy_area_distribution': {
                'mean': round(pa_mean, 2),
                'std_dev': round(pa_std, 2),
                'coefficient_variation': round(pa_cv, 2),
                'counts': dict(self.stats['by_policy_area']),
            },
            'validation_distribution': {
                'mean': round(val_mean, 2),
                'std_dev': round(val_std, 2),
                'coefficient_variation': round(val_cv, 2),
                'min': min(val_counts) if val_counts else 0,
                'max': max(val_counts) if val_counts else 0,
            },
            'expected_elements_distribution': {
                'mean': round(ee_mean, 2),
                'std_dev': round(ee_std, 2),
                'coefficient_variation': round(ee_cv, 2),
                'min': min(ee_counts) if ee_counts else 0,
                'max': max(ee_counts) if ee_counts else 0,
            },
        }

    def generate_report(self) -> str:
        """Generate a comprehensive audit report."""
        structure = self.audit_structure()
        canonical = self.audit_canonical_notation()
        issues = self.audit_micro_questions()
        equity = self.calculate_equity_metrics()
        
        report_lines = [
            "=" * 100,
            "QUESTIONNAIRE_MONOLITH.JSON - COMPREHENSIVE AUDIT REPORT",
            "=" * 100,
            "",
            "Generated: 2025-12-31",
            "Audit Scope: Structure, Hierarchy, Coverage, Balance, and Equity",
            "",
            "=" * 100,
            "1. OVERALL STRUCTURE",
            "=" * 100,
            f"Schema Version: {structure['schema_version']}",
            f"Version: {structure['version']}",
            f"Generated At: {structure['generated_at']}",
            f"Top-level Keys: {', '.join(structure['top_level_keys'])}",
            f"Has Integrity Section: {'YES' if structure['has_integrity'] else 'NO'}",
            f"Has Observability Section: {'YES' if structure['has_observability'] else 'NO'}",
            "",
            "=" * 100,
            "2. CANONICAL NOTATION",
            "=" * 100,
            f"Dimensions: {canonical['dimensions_count']} ({', '.join(canonical['dimensions_list'])})",
            f"Policy Areas: {canonical['policy_areas_count']} ({', '.join(canonical['policy_areas_list'])})",
            f"Clusters: {canonical['clusters_count']} ({', '.join(canonical['clusters_list'])})",
            "",
            "=" * 100,
            "3. MICRO QUESTIONS OVERVIEW",
            "=" * 100,
            f"Total Micro Questions: {self.stats['total_questions']}",
            "",
            "Distribution by Policy Area:",
        ]
        
        for pa in sorted(self.stats['by_policy_area'].keys()):
            report_lines.append(f"  {pa}: {self.stats['by_policy_area'][pa]} questions")
        
        report_lines.extend([
            "",
            "Distribution by Dimension:",
        ])
        
        for dim in sorted(self.stats['by_dimension'].keys()):
            report_lines.append(f"  {dim}: {self.stats['by_dimension'][dim]} questions")
        
        report_lines.extend([
            "",
            "Distribution by Cluster:",
        ])
        
        for cluster in sorted(self.stats['by_cluster'].keys()):
            report_lines.append(f"  {cluster}: {self.stats['by_cluster'][cluster]} questions")
        
        report_lines.extend([
            "",
            "Distribution by Scoring Modality:",
        ])
        
        for modality in sorted(self.stats['by_scoring_modality'].keys()):
            report_lines.append(f"  {modality}: {self.stats['by_scoring_modality'][modality]} questions")
        
        report_lines.extend([
            "",
            "=" * 100,
            "4. GAPS AND ISSUES IDENTIFIED",
            "=" * 100,
            "",
            f"4.1 Signal/Element Richness Issues",
            f"  - Questions with MISSING signals: {len(issues['missing_signals'])}",
            f"  - Questions with WEAK signals (<3): {len(issues['weak_signals'])}",
            f"  - Questions with MISSING expected_elements: {len(issues['missing_expected_elements'])}",
            f"  - Questions with VAGUE expected_elements: {len(issues['vague_expected_elements'])}",
            "",
            f"4.2 Validation Issues",
            f"  - Questions with NO validations: {len(issues['missing_validations'])}",
            f"  - Questions with WEAK validations (<2): {len(issues['weak_validations'])}",
            "",
            f"4.3 Scoring & Method Issues",
            f"  - Questions with MISSING scoring_modality: {len(issues['missing_scoring_modality'])}",
            f"  - Questions with MISSING method_sets: {len(issues['missing_method_sets'])}",
            "",
            f"4.4 Documentation Issues",
            f"  - Questions with MISSING/WEAK documentation: {len(issues['missing_documentation'])}",
            f"  - Questions with MISSING failure_contract: {len(issues['missing_failure_contract'])}",
            f"  - Questions with MISSING patterns: {len(issues['missing_patterns'])}",
            "",
            "=" * 100,
            "5. EQUITY AND BALANCE METRICS",
            "=" * 100,
            "",
            "5.1 Policy Area Distribution Balance",
            f"  Mean questions per policy area: {equity['policy_area_distribution']['mean']}",
            f"  Standard deviation: {equity['policy_area_distribution']['std_dev']}",
            f"  Coefficient of variation: {equity['policy_area_distribution']['coefficient_variation']}%",
            f"  Assessment: {'BALANCED' if equity['policy_area_distribution']['coefficient_variation'] < 10 else 'IMBALANCED'}",
            "",
            "5.2 Validation Distribution Balance",
            f"  Mean validations per question: {equity['validation_distribution']['mean']}",
            f"  Standard deviation: {equity['validation_distribution']['std_dev']}",
            f"  Range: {equity['validation_distribution']['min']} - {equity['validation_distribution']['max']}",
            f"  Coefficient of variation: {equity['validation_distribution']['coefficient_variation']}%",
            f"  Assessment: {'BALANCED' if equity['validation_distribution']['coefficient_variation'] < 50 else 'IMBALANCED'}",
            "",
            "5.3 Expected Elements Distribution Balance",
            f"  Mean expected_elements per question: {equity['expected_elements_distribution']['mean']}",
            f"  Standard deviation: {equity['expected_elements_distribution']['std_dev']}",
            f"  Range: {equity['expected_elements_distribution']['min']} - {equity['expected_elements_distribution']['max']}",
            f"  Coefficient of variation: {equity['expected_elements_distribution']['coefficient_variation']}%",
            f"  Assessment: {'BALANCED' if equity['expected_elements_distribution']['coefficient_variation'] < 50 else 'IMBALANCED'}",
            "",
            "=" * 100,
            "6. DETAILED ISSUE LISTS (Top 20 per category)",
            "=" * 100,
            "",
        ])
        
        # Add detailed lists of issues (limited to first 20 for readability)
        if issues['missing_signals']:
            report_lines.append("6.1 Questions with MISSING Signals (sample):")
            for q_id in issues['missing_signals'][:20]:
                report_lines.append(f"  - {q_id}")
            if len(issues['missing_signals']) > 20:
                report_lines.append(f"  ... and {len(issues['missing_signals']) - 20} more")
            report_lines.append("")
        
        if issues['missing_validations']:
            report_lines.append("6.2 Questions with NO Validations (sample):")
            for q_id in issues['missing_validations'][:20]:
                report_lines.append(f"  - {q_id}")
            if len(issues['missing_validations']) > 20:
                report_lines.append(f"  ... and {len(issues['missing_validations']) - 20} more")
            report_lines.append("")
        
        if issues['missing_documentation']:
            report_lines.append("6.3 Questions with WEAK/MISSING Documentation (sample):")
            for q_id in issues['missing_documentation'][:20]:
                report_lines.append(f"  - {q_id}")
            if len(issues['missing_documentation']) > 20:
                report_lines.append(f"  ... and {len(issues['missing_documentation']) - 20} more")
            report_lines.append("")
        
        if issues['vague_expected_elements']:
            report_lines.append("6.4 Questions with VAGUE Expected Elements (sample):")
            for q_id, vague_count, total_count in issues['vague_expected_elements'][:20]:
                report_lines.append(f"  - {q_id}: {vague_count}/{total_count} elements are vague")
            if len(issues['vague_expected_elements']) > 20:
                report_lines.append(f"  ... and {len(issues['vague_expected_elements']) - 20} more")
            report_lines.append("")
        
        report_lines.extend([
            "=" * 100,
            "7. RECOMMENDATIONS",
            "=" * 100,
            "",
            "Based on this audit, the following actions are recommended:",
            "",
            "Priority 1 - Critical Issues:",
        ])
        
        critical_issues = []
        if len(issues['missing_validations']) > self.stats['total_questions'] * 0.1:
            critical_issues.append(f"  • {len(issues['missing_validations'])} questions lack validations (>{10}% of total)")
        if len(issues['missing_expected_elements']) > self.stats['total_questions'] * 0.05:
            critical_issues.append(f"  • {len(issues['missing_expected_elements'])} questions lack expected_elements (>{5}% of total)")
        if equity['validation_distribution']['coefficient_variation'] > 50:
            critical_issues.append(f"  • Validation distribution is highly imbalanced (CV: {equity['validation_distribution']['coefficient_variation']}%)")
        
        if critical_issues:
            report_lines.extend(critical_issues)
        else:
            report_lines.append("  • No critical issues identified")
        
        report_lines.extend([
            "",
            "Priority 2 - High Priority:",
            f"  • Enrich {len(issues['weak_signals'])} questions with weak signals",
            f"  • Add documentation to {len(issues['missing_documentation'])} questions",
            f"  • Clarify {len(issues['vague_expected_elements'])} questions with vague expected_elements",
            "",
            "Priority 3 - Medium Priority:",
            f"  • Add failure_contracts to {len(issues['missing_failure_contract'])} questions",
            f"  • Add patterns to {len(issues['missing_patterns'])} questions",
            f"  • Review and normalize scoring modalities across all questions",
            "",
            "=" * 100,
            "END OF AUDIT REPORT",
            "=" * 100,
        ])
        
        return "\n".join(report_lines)

    def save_detailed_json_report(self, output_path: str):
        """Save a detailed JSON report with all issues for programmatic access."""
        structure = self.audit_structure()
        canonical = self.audit_canonical_notation()
        issues = self.audit_micro_questions()
        equity = self.calculate_equity_metrics()
        
        detailed_report = {
            'audit_metadata': {
                'generated_at': '2025-12-31T21:13:00Z',
                'questionnaire_file': str(self.json_path),
                'total_questions_audited': self.stats['total_questions'],
            },
            'structure': structure,
            'canonical_notation': canonical,
            'statistics': {
                'by_policy_area': dict(self.stats['by_policy_area']),
                'by_dimension': dict(self.stats['by_dimension']),
                'by_cluster': dict(self.stats['by_cluster']),
                'by_scoring_modality': dict(self.stats['by_scoring_modality']),
            },
            'issues': issues,
            'equity_metrics': equity,
            'summary': {
                'total_issues_found': sum(len(v) if isinstance(v, list) else len(v) for v in issues.values()),
                'critical_severity': len(issues['missing_validations']) + len(issues['missing_expected_elements']),
                'high_severity': len(issues['weak_signals']) + len(issues['missing_documentation']),
                'medium_severity': len(issues['missing_failure_contract']) + len(issues['missing_patterns']),
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(detailed_report, f, indent=2, ensure_ascii=False)
        
        print(f"\nDetailed JSON report saved to: {output_path}")


def main():
    """Main execution function."""
    # Determine the path to questionnaire_monolith.json
    repo_root = Path(__file__).parent.parent.parent
    json_path = repo_root / 'canonic_questionnaire_central' / 'questionnaire_monolith.json'
    
    if not json_path.exists():
        print(f"ERROR: questionnaire_monolith.json not found at {json_path}")
        sys.exit(1)
    
    # Create auditor and run audit
    auditor = QuestionnaireAuditor(str(json_path))
    
    # Generate text report
    report = auditor.generate_report()
    print(report)
    
    # Save text report
    report_dir = repo_root / 'artifacts' / 'reports' / 'audit'
    report_dir.mkdir(parents=True, exist_ok=True)
    
    text_report_path = report_dir / 'questionnaire_audit_report.txt'
    with open(text_report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nText report saved to: {text_report_path}")
    
    # Save detailed JSON report
    json_report_path = report_dir / 'questionnaire_audit_report.json'
    auditor.save_detailed_json_report(str(json_report_path))
    
    print("\n✓ Audit complete!")


if __name__ == '__main__':
    main()

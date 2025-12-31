#!/usr/bin/env python3
"""
Deep Equity Analysis for questionnaire_monolith.json

Performs detailed analysis to identify hidden imbalances and equity concerns
across policy areas, dimensions, and clusters.

Author: FARFAN Audit Team
Date: 2025-12-31
"""

import json
import sys
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Any


def load_questionnaire(json_path: str) -> Dict:
    """Load the questionnaire JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_validation_by_policy_area(data: Dict) -> Dict[str, Any]:
    """Analyze validation distribution by policy area."""
    micro_questions = data.get('blocks', {}).get('micro_questions', [])
    
    pa_validations = defaultdict(list)
    
    for q in micro_questions:
        pa = q.get('policy_area_id', 'UNKNOWN')
        validations = q.get('validations', [])
        pa_validations[pa].append(len(validations))
    
    # Calculate statistics for each policy area
    pa_stats = {}
    for pa, val_counts in sorted(pa_validations.items()):
        mean = sum(val_counts) / len(val_counts) if val_counts else 0
        min_val = min(val_counts) if val_counts else 0
        max_val = max(val_counts) if val_counts else 0
        
        pa_stats[pa] = {
            'mean': round(mean, 2),
            'min': min_val,
            'max': max_val,
            'total_questions': len(val_counts),
            'weak_validations': sum(1 for v in val_counts if v < 2),
        }
    
    return pa_stats


def analyze_validation_by_dimension(data: Dict) -> Dict[str, Any]:
    """Analyze validation distribution by dimension."""
    micro_questions = data.get('blocks', {}).get('micro_questions', [])
    
    dim_validations = defaultdict(list)
    
    for q in micro_questions:
        dim = q.get('dimension_id', 'UNKNOWN')
        validations = q.get('validations', [])
        dim_validations[dim].append(len(validations))
    
    # Calculate statistics for each dimension
    dim_stats = {}
    for dim, val_counts in sorted(dim_validations.items()):
        mean = sum(val_counts) / len(val_counts) if val_counts else 0
        min_val = min(val_counts) if val_counts else 0
        max_val = max(val_counts) if val_counts else 0
        
        dim_stats[dim] = {
            'mean': round(mean, 2),
            'min': min_val,
            'max': max_val,
            'total_questions': len(val_counts),
            'weak_validations': sum(1 for v in val_counts if v < 2),
        }
    
    return dim_stats


def analyze_scoring_modality_by_policy_area(data: Dict) -> Dict[str, Any]:
    """Analyze scoring modality distribution by policy area."""
    micro_questions = data.get('blocks', {}).get('micro_questions', [])
    
    pa_modalities = defaultdict(lambda: Counter())
    
    for q in micro_questions:
        pa = q.get('policy_area_id', 'UNKNOWN')
        modality = q.get('scoring_modality', 'UNKNOWN')
        pa_modalities[pa][modality] += 1
    
    return {pa: dict(modalities) for pa, modalities in sorted(pa_modalities.items())}


def analyze_expected_elements_diversity(data: Dict) -> Dict[str, Any]:
    """Analyze diversity of expected_elements types used."""
    micro_questions = data.get('blocks', {}).get('micro_questions', [])
    
    element_types = Counter()
    pa_element_types = defaultdict(lambda: Counter())
    
    for q in micro_questions:
        pa = q.get('policy_area_id', 'UNKNOWN')
        elements = q.get('expected_elements', [])
        
        for elem in elements:
            if isinstance(elem, dict):
                elem_type = elem.get('type', 'UNKNOWN')
                element_types[elem_type] += 1
                pa_element_types[pa][elem_type] += 1
    
    return {
        'global_types': dict(element_types.most_common(20)),
        'by_policy_area': {pa: dict(types.most_common(10)) for pa, types in sorted(pa_element_types.items())},
    }


def analyze_method_class_distribution(data: Dict) -> Dict[str, Any]:
    """Analyze which method classes are used most frequently."""
    micro_questions = data.get('blocks', {}).get('micro_questions', [])
    
    class_counts = Counter()
    pa_class_counts = defaultdict(lambda: Counter())
    
    for q in micro_questions:
        pa = q.get('policy_area_id', 'UNKNOWN')
        method_sets = q.get('method_sets', [])
        
        for method in method_sets:
            if isinstance(method, dict):
                method_class = method.get('class', 'UNKNOWN')
                class_counts[method_class] += 1
                pa_class_counts[pa][method_class] += 1
    
    return {
        'global_classes': dict(class_counts.most_common(20)),
        'by_policy_area': {pa: dict(classes.most_common(10)) for pa, classes in sorted(pa_class_counts.items())},
    }


def identify_cross_cutting_gaps(data: Dict) -> Dict[str, Any]:
    """Identify potential gaps in cross-cutting themes like gender, rights, vulnerability."""
    micro_questions = data.get('blocks', {}).get('micro_questions', [])
    policy_areas = data.get('canonical_notation', {}).get('policy_areas', {})
    
    # Keywords to search for
    gender_keywords = ['género', 'mujer', 'mujeres', 'gender', 'femenin', 'masculin', 'equidad de género']
    rights_keywords = ['derechos', 'derecho', 'rights', 'humanos', 'human rights']
    vulnerability_keywords = ['vulnerab', 'discriminación', 'exclusión', 'marginad', 'discapacidad', 'pobreza']
    
    pa_themes = defaultdict(lambda: {'gender': 0, 'rights': 0, 'vulnerability': 0, 'total': 0})
    
    for q in micro_questions:
        pa = q.get('policy_area_id', 'UNKNOWN')
        text = q.get('text', '').lower()
        
        pa_themes[pa]['total'] += 1
        
        # Check for keywords
        if any(kw in text for kw in gender_keywords):
            pa_themes[pa]['gender'] += 1
        if any(kw in text for kw in rights_keywords):
            pa_themes[pa]['rights'] += 1
        if any(kw in text for kw in vulnerability_keywords):
            pa_themes[pa]['vulnerability'] += 1
    
    # Calculate percentages
    results = {}
    for pa, counts in sorted(pa_themes.items()):
        total = counts['total']
        results[pa] = {
            'total_questions': total,
            'gender_coverage': f"{counts['gender']} ({counts['gender']/total*100:.1f}%)",
            'rights_coverage': f"{counts['rights']} ({counts['rights']/total*100:.1f}%)",
            'vulnerability_coverage': f"{counts['vulnerability']} ({counts['vulnerability']/total*100:.1f}%)",
        }
    
    return results


def generate_deep_equity_report(json_path: str) -> str:
    """Generate comprehensive equity analysis report."""
    data = load_questionnaire(json_path)
    
    # Run all analyses
    pa_validations = analyze_validation_by_policy_area(data)
    dim_validations = analyze_validation_by_dimension(data)
    pa_modalities = analyze_scoring_modality_by_policy_area(data)
    element_diversity = analyze_expected_elements_diversity(data)
    method_distribution = analyze_method_class_distribution(data)
    cross_cutting = identify_cross_cutting_gaps(data)
    
    report_lines = [
        "=" * 100,
        "DEEP EQUITY ANALYSIS REPORT - questionnaire_monolith.json",
        "=" * 100,
        "",
        "Generated: 2025-12-31",
        "Focus: Hidden imbalances, cross-cutting themes, methodological diversity",
        "",
        "=" * 100,
        "1. VALIDATION EQUITY BY POLICY AREA",
        "=" * 100,
        "",
        "Policy Area | Mean | Min | Max | Weak (<2) | Assessment",
        "-" * 100,
    ]
    
    for pa, stats in pa_validations.items():
        weak_pct = stats['weak_validations'] / stats['total_questions'] * 100
        assessment = "⚠️ HIGH RISK" if weak_pct > 80 else ("⚠️ MODERATE" if weak_pct > 60 else "✓ OK")
        report_lines.append(
            f"{pa:8} | {stats['mean']:4.2f} | {stats['min']:3d} | {stats['max']:3d} | "
            f"{stats['weak_validations']:2d} ({weak_pct:5.1f}%) | {assessment}"
        )
    
    report_lines.extend([
        "",
        "KEY FINDINGS:",
    ])
    
    # Identify most/least validated policy areas
    sorted_pa = sorted(pa_validations.items(), key=lambda x: x[1]['mean'])
    report_lines.append(f"  • Least validated: {sorted_pa[0][0]} (mean: {sorted_pa[0][1]['mean']})")
    report_lines.append(f"  • Most validated: {sorted_pa[-1][0]} (mean: {sorted_pa[-1][1]['mean']})")
    report_lines.append(f"  • Range: {sorted_pa[-1][1]['mean'] - sorted_pa[0][1]['mean']:.2f} validations")
    
    report_lines.extend([
        "",
        "=" * 100,
        "2. VALIDATION EQUITY BY DIMENSION",
        "=" * 100,
        "",
        "Dimension | Mean | Min | Max | Weak (<2) | Assessment",
        "-" * 100,
    ])
    
    for dim, stats in dim_validations.items():
        weak_pct = stats['weak_validations'] / stats['total_questions'] * 100
        assessment = "⚠️ HIGH RISK" if weak_pct > 80 else ("⚠️ MODERATE" if weak_pct > 60 else "✓ OK")
        report_lines.append(
            f"{dim:9} | {stats['mean']:4.2f} | {stats['min']:3d} | {stats['max']:3d} | "
            f"{stats['weak_validations']:2d} ({weak_pct:5.1f}%) | {assessment}"
        )
    
    report_lines.extend([
        "",
        "=" * 100,
        "3. SCORING MODALITY DIVERSITY BY POLICY AREA",
        "=" * 100,
        "",
    ])
    
    for pa, modalities in pa_modalities.items():
        total = sum(modalities.values())
        report_lines.append(f"{pa}:")
        for modality, count in sorted(modalities.items()):
            pct = count / total * 100
            report_lines.append(f"  {modality}: {count} ({pct:.1f}%)")
        report_lines.append("")
    
    report_lines.extend([
        "ASSESSMENT:",
        "  • Check if any policy area is over-reliant on a single modality",
        "  • Verify if modality choice matches policy area evaluation needs",
        "",
        "=" * 100,
        "4. EXPECTED ELEMENTS TYPE DIVERSITY",
        "=" * 100,
        "",
        "Top 20 Most Common Element Types (Global):",
        "",
    ])
    
    for elem_type, count in element_diversity['global_types'].items():
        report_lines.append(f"  {elem_type}: {count}")
    
    report_lines.extend([
        "",
        "Element Type Usage by Policy Area (Top 10 per area):",
        "",
    ])
    
    for pa, types in sorted(element_diversity['by_policy_area'].items()):
        report_lines.append(f"{pa}:")
        for elem_type, count in list(types.items())[:5]:  # Show top 5 only
            report_lines.append(f"  {elem_type}: {count}")
        report_lines.append("")
    
    report_lines.extend([
        "=" * 100,
        "5. METHOD CLASS DISTRIBUTION",
        "=" * 100,
        "",
        "Top 20 Most Used Method Classes (Global):",
        "",
    ])
    
    for method_class, count in method_distribution['global_classes'].items():
        report_lines.append(f"  {method_class}: {count}")
    
    report_lines.extend([
        "",
        "=" * 100,
        "6. CROSS-CUTTING THEME ANALYSIS",
        "=" * 100,
        "",
        "Analysis of gender, rights, and vulnerability themes across all policy areas:",
        "",
        "Policy Area | Total Q | Gender Coverage | Rights Coverage | Vulnerability Coverage",
        "-" * 100,
    ])
    
    for pa, coverage in cross_cutting.items():
        report_lines.append(
            f"{pa:8} | {coverage['total_questions']:7} | {coverage['gender_coverage']:15} | "
            f"{coverage['rights_coverage']:15} | {coverage['vulnerability_coverage']:22}"
        )
    
    report_lines.extend([
        "",
        "EQUITY ASSESSMENT:",
        "  • Policy areas with <10% gender coverage may need enrichment",
        "  • Rights-based approach should appear in multiple policy areas",
        "  • Vulnerability considerations should not be limited to PA10",
        "",
        "=" * 100,
        "7. KEY RECOMMENDATIONS FOR EQUITY",
        "=" * 100,
        "",
        "Based on this deep analysis:",
        "",
        "1. VALIDATION NORMALIZATION:",
    ])
    
    # Identify policy areas needing most validation work
    high_risk_pas = [pa for pa, stats in pa_validations.items() 
                     if stats['weak_validations'] / stats['total_questions'] > 0.8]
    if high_risk_pas:
        report_lines.append(f"   • Priority: {', '.join(high_risk_pas)} (>80% weak validation)")
    
    report_lines.extend([
        "",
        "2. SCORING MODALITY REVIEW:",
        "   • Examine policy areas with 100% TYPE_A scoring",
        "   • Consider TYPE_B, TYPE_E for qualitative assessments",
        "   • Introduce TYPE_C/D/F for specialized evaluation needs",
        "",
        "3. CROSS-CUTTING ENRICHMENT:",
        "   • Add gender perspective to non-PA01 areas with <10% coverage",
        "   • Integrate rights-based language across all dimensions",
        "   • Ensure vulnerability is addressed beyond PA10",
        "",
        "4. METHOD DIVERSIFICATION:",
        "   • Review method class concentration by policy area",
        "   • Ensure analytical diversity matches policy complexity",
        "   • Avoid over-reliance on single method classes",
        "",
        "=" * 100,
        "END OF DEEP EQUITY ANALYSIS",
        "=" * 100,
    ])
    
    return "\n".join(report_lines)


def main():
    """Main execution function."""
    repo_root = Path(__file__).parent.parent.parent
    json_path = repo_root / 'canonic_questionnaire_central' / 'questionnaire_monolith.json'
    
    if not json_path.exists():
        print(f"ERROR: questionnaire_monolith.json not found at {json_path}")
        sys.exit(1)
    
    # Generate report
    report = generate_deep_equity_report(str(json_path))
    print(report)
    
    # Save report
    report_dir = repo_root / 'artifacts' / 'reports' / 'audit'
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_path = report_dir / 'questionnaire_deep_equity_analysis.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✓ Deep equity analysis saved to: {report_path}")


if __name__ == '__main__':
    main()

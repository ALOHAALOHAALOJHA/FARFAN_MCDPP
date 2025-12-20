#!/usr/bin/env python3
"""
Comprehensive Signal Irrigation Blocker Audit
==============================================

Audits the complete signal system to identify blockers preventing strategic
irrigation of questionnaire_monolith signals across all pipeline phases.

Focus Areas:
1. Questionnaire_monolith structure and completeness
2. Signal extraction and registry creation
3. Signal propagation through phases
4. Missing signal consumption points
5. Gaps in signal utilization
6. Blockers in current architecture

Author: F.A.R.F.A.N Pipeline Team
Version: 1.0.0
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from orchestration.factory import get_canonical_questionnaire


def audit_questionnaire_monolith(monolith_path: Path) -> dict[str, Any]:
    """Audit questionnaire_monolith structure and signal richness."""
    print("\n" + "=" * 80)
    print("AUDIT 1: QUESTIONNAIRE_MONOLITH STRUCTURE")
    print("=" * 80)
    
    canonical_questionnaire = get_canonical_questionnaire(
        questionnaire_path=monolith_path,
    )
    monolith = canonical_questionnaire.data
    
    results = {
        "file_size_kb": monolith_path.stat().st_size / 1024,
        "line_count": len(json.dumps(monolith).splitlines()),
        "top_level_keys": list(monolith.keys()),
    }
    
    # Check canonical_notation
    if "canonical_notation" in monolith:
        cn = monolith["canonical_notation"]
        results["dimensions"] = len(cn.get("dimensions", {}))
        results["policy_areas"] = len(cn.get("policy_areas", {}))
        print(f"✓ Canonical notation: {results['dimensions']} dimensions, {results['policy_areas']} policy areas")
    
    # Check blocks structure
    if "blocks" in monolith:
        blocks = monolith["blocks"]
        results["blocks"] = list(blocks.keys())
        
        # Micro questions
        micro_questions = blocks.get("micro_questions", [])
        results["micro_questions_count"] = len(micro_questions)
        print(f"✓ Micro questions: {len(micro_questions)} total")
        
        if micro_questions:
            # Analyze signal richness per question
            pattern_counts = []
            indicator_counts = []
            method_counts = []
            validation_counts = []
            
            for q in micro_questions:
                patterns = q.get("patterns", [])
                pattern_counts.append(len(patterns))
                
                # Count indicators in patterns
                indicators = [p for p in patterns if p.get("category") == "INDICADOR"]
                indicator_counts.append(len(indicators))
                
                # Count methods
                method_sets = q.get("method_sets", [])
                method_counts.append(len(method_sets))
                
                # Count validations
                validations = q.get("validations", {})
                validation_counts.append(len(validations.get("checks", [])))
            
            results["avg_patterns_per_question"] = sum(pattern_counts) / len(pattern_counts)
            results["avg_indicators_per_question"] = sum(indicator_counts) / len(indicator_counts)
            results["avg_methods_per_question"] = sum(method_counts) / len(method_counts)
            results["avg_validations_per_question"] = sum(validation_counts) / len(validation_counts)
            results["total_patterns"] = sum(pattern_counts)
            results["total_indicators"] = sum(indicator_counts)
            
            print(f"  Patterns: {results['total_patterns']} total, avg {results['avg_patterns_per_question']:.1f} per question")
            print(f"  Indicators: {results['total_indicators']} total, avg {results['avg_indicators_per_question']:.1f} per question")
            print(f"  Methods: avg {results['avg_methods_per_question']:.1f} per question")
            print(f"  Validations: avg {results['avg_validations_per_question']:.1f} per question")
        
        # MESO questions
        meso_questions = blocks.get("meso_questions", [])
        results["meso_questions_count"] = len(meso_questions)
        print(f"✓ MESO questions: {len(meso_questions)} total")
        
        # Macro question
        macro_question = blocks.get("macro_question", {})
        results["has_macro_question"] = bool(macro_question)
        print(f"✓ Macro question: {'Present' if macro_question else 'MISSING'}")
    
    return results


def audit_signal_registry_creation(src_path: Path) -> dict[str, Any]:
    """Audit signal registry creation and infrastructure."""
    print("\n" + "=" * 80)
    print("AUDIT 2: SIGNAL REGISTRY INFRASTRUCTURE")
    print("=" * 80)
    
    results = {
        "registry_exists": False,
        "loader_exists": False,
        "factory_integration": False,
        "blockers": [],
    }
    
    # Check if signal_registry.py exists
    registry_path = src_path / "cross_cutting_infrastrucuture/irrigation_using_signals/SISAS/signal_registry.py"
    if registry_path.exists():
        results["registry_exists"] = True
        print(f"✓ Signal registry exists: {registry_path.relative_to(src_path.parent)}")
        
        # Check for create_signal_registry function
        registry_content = registry_path.read_text()
        if "create_signal_registry" in registry_content:
            results["has_create_function"] = True
            print("  ✓ create_signal_registry() function found")
        else:
            results["has_create_function"] = False
            results["blockers"].append("BLOCKER: create_signal_registry() function not found")
            print("  ✗ BLOCKER: create_signal_registry() function not found")
    else:
        results["blockers"].append("BLOCKER: signal_registry.py does not exist")
        print(f"✗ BLOCKER: Signal registry does not exist")
    
    # Check if signal_loader.py exists
    loader_path = src_path / "cross_cutting_infrastrucuture/irrigation_using_signals/SISAS/signal_loader.py"
    if loader_path.exists():
        results["loader_exists"] = True
        print(f"✓ Signal loader exists: {loader_path.relative_to(src_path.parent)}")
    else:
        results["blockers"].append("INFO: signal_loader.py does not exist (may be deprecated)")
        print(f"ℹ  Signal loader does not exist (may be deprecated per factory.py comments)")
    
    # Check factory.py integration
    factory_path = src_path / "orchestration/factory.py"
    if factory_path.exists():
        factory_content = factory_path.read_text()
        if "create_signal_registry" in factory_content:
            results["factory_integration"] = True
            print(f"✓ Factory integrates signal registry")
        else:
            results["blockers"].append("BLOCKER: Factory does not integrate signal registry")
            print(f"✗ BLOCKER: Factory does not integrate signal registry")
    
    return results


def audit_phase_signal_consumption(src_path: Path) -> dict[str, Any]:
    """Audit signal consumption across all phases."""
    print("\n" + "=" * 80)
    print("AUDIT 3: SIGNAL CONSUMPTION BY PHASE")
    print("=" * 80)
    
    results = {}
    phases = {
        "Phase_zero": "Phase 0 (Bootstrap)",
        "Phase_one": "Phase 1 (Ingestion)",
        "Phase_two": "Phase 2 (Execution)",
        "Phase_three": "Phase 3 (Scoring)",
        "Phase_four_five_six_seven": "Phase 4-7 (Aggregation)",
        "Phase_eight": "Phase 8 (Recommendations)",
        "Phase_nine": "Phase 9 (Reporting)",
    }
    
    for phase_dir, phase_name in phases.items():
        phase_path = src_path / "canonic_phases" / phase_dir
        if not phase_path.exists():
            print(f"  {phase_name}: Directory not found")
            results[phase_dir] = {"exists": False}
            continue
        
        # Search for signal usage
        signal_terms = [
            "signal_registry",
            "signal_pack",
            "SignalEnrichedScorer",
            "SignalEnrichedAggregator",
            "SignalEnrichedRecommender",
            "SignalEnrichedReporter",
        ]
        
        phase_files = list(phase_path.rglob("*.py"))
        signal_usage = defaultdict(list)
        
        for py_file in phase_files:
            content = py_file.read_text()
            for term in signal_terms:
                if term in content:
                    signal_usage[term].append(py_file.name)
        
        results[phase_dir] = {
            "exists": True,
            "files": len(phase_files),
            "signal_usage": dict(signal_usage),
            "has_signals": bool(signal_usage),
        }
        
        if signal_usage:
            print(f"✓ {phase_name}: Signal usage found")
            for term, files in signal_usage.items():
                print(f"    - {term}: {len(files)} file(s)")
        else:
            print(f"✗ {phase_name}: NO signal usage found")
    
    return results


def audit_signal_propagation_gaps(src_path: Path) -> dict[str, Any]:
    """Identify gaps in signal propagation through pipeline."""
    print("\n" + "=" * 80)
    print("AUDIT 4: SIGNAL PROPAGATION GAPS")
    print("=" * 80)
    
    results = {
        "gaps": [],
        "recommendations": [],
    }
    
    # Check orchestrator signal passing
    orchestrator_path = src_path / "orchestration/orchestrator.py"
    if orchestrator_path.exists():
        orch_content = orchestrator_path.read_text()
        
        # Check if signal_registry is passed to phases
        checks = [
            ("signal_registry attribute", "self.signal_registry"),
            ("Phase 1 signal passing", "signal_registry="),
            ("Phase 3 signal integration", "SignalEnrichedScorer"),
            ("Phase 4-7 signal integration", "SignalEnrichedAggregator"),
        ]
        
        for check_name, check_pattern in checks:
            if check_pattern in orch_content:
                print(f"✓ {check_name}: Found")
            else:
                results["gaps"].append(f"GAP: {check_name} not found in orchestrator")
                print(f"✗ GAP: {check_name} not found in orchestrator")
    
    # Check if newly created signal enhancement modules are integrated
    new_modules = [
        ("Phase 3", "canonic_phases/Phase_three/signal_enriched_scoring.py"),
        ("Phase 4-7", "canonic_phases/Phase_four_five_six_seven/signal_enriched_aggregation.py"),
        ("Phase 8", "canonic_phases/Phase_eight/signal_enriched_recommendations.py"),
        ("Phase 9", "canonic_phases/Phase_nine/signal_enriched_reporting.py"),
    ]
    
    for phase_name, module_path in new_modules:
        full_path = src_path / module_path
        if full_path.exists():
            print(f"✓ {phase_name} enhancement module exists: {module_path}")
            results[f"{phase_name}_module_exists"] = True
        else:
            results["gaps"].append(f"GAP: {phase_name} enhancement module missing")
            print(f"✗ GAP: {phase_name} enhancement module missing")
    
    # Generate recommendations
    if results["gaps"]:
        results["recommendations"].append(
            "CRITICAL: Integrate signal enhancement modules into orchestrator"
        )
        results["recommendations"].append(
            "ACTION: Add signal_registry parameter passing in orchestrator phase methods"
        )
        results["recommendations"].append(
            "ACTION: Instantiate Signal*Enriched classes in each phase"
        )
    
    return results


def audit_questionnaire_utilization(monolith_path: Path) -> dict[str, Any]:
    """Audit how much of questionnaire_monolith is actually utilized."""
    print("\n" + "=" * 80)
    print("AUDIT 5: QUESTIONNAIRE_MONOLITH UTILIZATION")
    print("=" * 80)
    
    canonical_questionnaire = get_canonical_questionnaire(
        questionnaire_path=monolith_path,
    )
    monolith = canonical_questionnaire.data
    
    results = {
        "utilization_rate": {},
        "underutilized_fields": [],
    }
    
    # Check micro questions utilization
    micro_questions = monolith.get("blocks", {}).get("micro_questions", [])
    if micro_questions:
        sample_q = micro_questions[0]
        
        # Fields that should be heavily used
        critical_fields = [
            "patterns",
            "expected_elements", 
            "method_sets",
            "validations",
            "scoring_modality",
            "scoring_definition_ref",
            "failure_contract",
        ]
        
        for field in critical_fields:
            if field in sample_q:
                value = sample_q[field]
                is_populated = bool(value) if not isinstance(value, list) else len(value) > 0
                
                if is_populated:
                    print(f"✓ Field '{field}': Populated")
                else:
                    results["underutilized_fields"].append(field)
                    print(f"⚠  Field '{field}': Empty/minimal")
    
    # Check for advanced features
    advanced_features = {
        "niveles_abstraccion": "Abstraction levels (cluster mappings)",
        "niveles_abstraccion.macro": "MACRO level definition",
        "niveles_abstraccion.meso": "MESO level definition",
        "niveles_abstraccion.micro": "MICRO level definition",
    }
    
    print("\nAdvanced features:")
    for feature_path, feature_desc in advanced_features.items():
        parts = feature_path.split(".")
        current = monolith.get("blocks", {})
        found = True
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                found = False
                break
        
        if found and current:
            print(f"✓ {feature_desc}: Present")
        else:
            print(f"✗ {feature_desc}: Missing")
            results["underutilized_fields"].append(feature_path)
    
    return results


def generate_blocker_report(all_results: dict[str, Any]) -> None:
    """Generate comprehensive blocker report."""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE BLOCKER REPORT")
    print("=" * 80)
    
    blockers = []
    warnings = []
    recommendations = []
    
    # Collect all blockers
    for audit_name, audit_results in all_results.items():
        if isinstance(audit_results, dict):
            if "blockers" in audit_results:
                blockers.extend(audit_results["blockers"])
            if "gaps" in audit_results:
                warnings.extend(audit_results["gaps"])
            if "recommendations" in audit_results:
                recommendations.extend(audit_results["recommendations"])
    
    print(f"\n🚫 CRITICAL BLOCKERS ({len(blockers)}):")
    if blockers:
        for i, blocker in enumerate(blockers, 1):
            print(f"  {i}. {blocker}")
    else:
        print("  ✓ No critical blockers found")
    
    print(f"\n⚠️  WARNINGS ({len(warnings)}):")
    if warnings:
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
    else:
        print("  ✓ No warnings")
    
    print(f"\n💡 RECOMMENDATIONS ({len(recommendations)}):")
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    else:
        recommendations = [
            "RECOMMENDATION: Signal infrastructure is complete - enable in orchestrator",
            "RECOMMENDATION: Add signal_registry DI to all phase execution methods",
            "RECOMMENDATION: Instantiate SignalEnriched* classes in phase stubs",
            "RECOMMENDATION: Add signal provenance to all phase outputs",
        ]
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")


def main():
    """Run complete signal irrigation audit."""
    print("\n" + "=" * 80)
    print("SIGNAL IRRIGATION BLOCKER AUDIT")
    print("Strategic Questionnaire_Monolith Utilization Assessment")
    print("=" * 80)
    
    repo_root = Path(__file__).parent
    monolith_path = repo_root / "canonic_questionnaire_central/questionnaire_monolith.json"
    src_path = repo_root / "src"
    
    if not monolith_path.exists():
        print(f"✗ ERROR: Questionnaire monolith not found at {monolith_path}")
        sys.exit(1)
    
    if not src_path.exists():
        print(f"✗ ERROR: Source directory not found at {src_path}")
        sys.exit(1)
    
    # Run all audits
    all_results = {}
    
    all_results["questionnaire_monolith"] = audit_questionnaire_monolith(monolith_path)
    all_results["signal_registry"] = audit_signal_registry_creation(src_path)
    all_results["phase_consumption"] = audit_phase_signal_consumption(src_path)
    all_results["propagation_gaps"] = audit_signal_propagation_gaps(src_path)
    all_results["monolith_utilization"] = audit_questionnaire_utilization(monolith_path)
    
    # Generate final report
    generate_blocker_report(all_results)
    
    # Save results to JSON
    output_path = repo_root / "audit_signal_irrigation_blockers_report.json"
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n✓ Audit complete. Full results saved to: {output_path}")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()

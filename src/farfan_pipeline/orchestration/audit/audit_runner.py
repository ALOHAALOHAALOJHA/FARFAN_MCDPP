"""
Audit Runner - Standalone script for running equipment audits.

Usage:
    python -m farfan_pipeline.orchestration.audit.audit_runner

Or import and use programmatically:
    from farfan_pipeline.orchestration.audit import run_full_audit
    result = run_full_audit()
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

from .equipment_auditor import EquipmentAuditor, EquipmentAuditResult


# Consumer configurations - MUST match UnifiedOrchestrator.CONSUMER_CONFIGS
CANONICAL_CONSUMER_CONFIGS = [
    {
        "consumer_id": "phase_00_assembly_consumer",
        "capabilities": ["STATIC_LOAD", "SIGNAL_PACK", "PHASE_MONITORING"],
    },
    {
        "consumer_id": "phase_01_extraction_consumer",
        "capabilities": ["EXTRACTION", "STRUCTURAL_PARSING", "TRIPLET_EXTRACTION",
                        "NUMERIC_PARSING", "NORMATIVE_LOOKUP", "HIERARCHY_PARSING",
                        "FINANCIAL_ANALYSIS", "POPULATION_PARSING", "TEMPORAL_PARSING",
                        "CAUSAL_ANALYSIS", "NER", "SEMANTIC_ANALYSIS", "PHASE_MONITORING",
                        "CITATION_PARSING", "TREE_CONSTRUCTION", "DEMOGRAPHIC_ANALYSIS",
                        "DATE_NORMALIZATION", "VERB_EXTRACTION", "INSTITUTIONAL_RECOGNITION",
                        "RELATIONSHIP_EXTRACTION"],
    },
    {
        "consumer_id": "phase_02_enrichment_consumer",
        "capabilities": ["ENRICHMENT", "PATTERN_MATCHING", "KEYWORD_EXTRACTION",
                        "ENTITY_RECOGNITION", "PHASE_MONITORING"],
    },
    {
        "consumer_id": "phase_03_validation_consumer",
        "capabilities": ["VALIDATION", "NORMATIVE_CHECK", "ENTITY_CHECK",
                        "COHERENCE_CHECK", "PHASE_MONITORING"],
    },
    {
        "consumer_id": "phase_04_micro_consumer",
        "capabilities": ["SCORING", "MICRO_LEVEL", "CHOQUET_INTEGRAL", "PHASE_MONITORING"],
    },
    {
        "consumer_id": "phase_05_meso_consumer",
        "capabilities": ["SCORING", "MESO_LEVEL", "DIMENSION_AGGREGATION", "PHASE_MONITORING"],
    },
    {
        "consumer_id": "phase_06_macro_consumer",
        "capabilities": ["SCORING", "MACRO_LEVEL", "POLICY_AREA_AGGREGATION", "PHASE_MONITORING"],
    },
    {
        "consumer_id": "phase_07_aggregation_consumer",
        "capabilities": ["AGGREGATION", "CLUSTER_LEVEL", "PHASE_MONITORING"],
    },
    {
        "consumer_id": "phase_08_integration_consumer",
        "capabilities": ["AGGREGATION", "HOLISTIC_LEVEL", "RECOMMENDATION_ENGINE", "PHASE_MONITORING"],
    },
    {
        "consumer_id": "phase_09_report_consumer",
        "capabilities": ["REPORT_GENERATION", "ASSEMBLY", "EXPORT", "PHASE_MONITORING"],
    },
]


def run_full_audit(
    consumer_configs: List[Dict] = None,
    output_path: Path = None
) -> EquipmentAuditResult:
    """
    Run a full equipment audit.

    Args:
        consumer_configs: Consumer configurations to audit.
                         If None, uses CANONICAL_CONSUMER_CONFIGS.
        output_path: Path to save JSON report. If None, uses default.

    Returns:
        EquipmentAuditResult with complete audit findings.
    """
    configs = consumer_configs or CANONICAL_CONSUMER_CONFIGS

    auditor = EquipmentAuditor()
    result = auditor.audit_all_consumers(configs)

    if output_path is None:
        output_path = Path("artifacts/audits") / f"equipment_audit_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

    auditor.save_report(output_path)

    return result


def generate_audit_report() -> str:
    """Generate a human-readable audit report."""
    result = run_full_audit()

    lines = [
        "=" * 80,
        "SISAS DATA EQUIPMENT AUDIT REPORT",
        "=" * 80,
        f"Timestamp: {result.audit_timestamp}",
        f"Total Consumers: {result.total_consumers}",
        f"Total Signal Types: {result.total_signal_types}",
        f"Total Capability Gaps: {result.total_capability_gaps}",
        f"Overall Equipment Score: {result.overall_equipment_score:.2%}",
        "",
        "-" * 80,
        "CONSUMER DETAILS",
        "-" * 80,
    ]

    for report in result.consumer_reports:
        lines.append(f"\n{report.consumer_id}")
        lines.append(f"  Phase: {report.phase}")
        lines.append(f"  Equipment Score: {report.equipment_score:.2%}")
        lines.append(f"  Equipped for: {sorted(report.signal_types_equipped)}")
        if report.signal_types_unequipped:
            lines.append(f"  UNEQUIPPED for: {sorted(report.signal_types_unequipped)}")
            for gap in report.capability_gaps:
                lines.append(f"    - {gap.signal_type}: missing {sorted(gap.missing_capabilities)}")

    lines.append("")
    lines.append("-" * 80)
    lines.append("RECOMMENDATIONS")
    lines.append("-" * 80)
    for rec in result.recommendations:
        lines.append(f"  • {rec}")

    lines.append("")
    lines.append("=" * 80)

    return "\n".join(lines)


if __name__ == "__main__":
    print(generate_audit_report())

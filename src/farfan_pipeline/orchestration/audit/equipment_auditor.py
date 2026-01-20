"""
Equipment Auditor - Verifies consumer capability alignment.

This auditor answers the question:
"For each signal type, which consumers are EQUIPPED to handle it?"

SOTA Pattern: Capability Matrix Analysis
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, FrozenSet, Tuple, Optional
from datetime import datetime
import json
from pathlib import Path


@dataclass(frozen=True)
class CapabilityGap:
    """Represents a missing capability for a consumer-signal pair."""
    consumer_id: str
    signal_type: str
    required_capabilities: FrozenSet[str]
    available_capabilities: FrozenSet[str]
    missing_capabilities: FrozenSet[str]

    @property
    def gap_severity(self) -> str:
        """Calculate gap severity based on missing count."""
        missing_count = len(self.missing_capabilities)
        if missing_count == 0:
            return "NONE"
        elif missing_count == 1:
            return "LOW"
        elif missing_count <= 3:
            return "MEDIUM"
        else:
            return "HIGH"


@dataclass
class ConsumerEquipmentReport:
    """Equipment report for a single consumer."""
    consumer_id: str
    phase: str
    declared_capabilities: FrozenSet[str]
    signal_types_subscribed: FrozenSet[str]
    signal_types_equipped: FrozenSet[str]
    signal_types_unequipped: FrozenSet[str]
    capability_gaps: Tuple[CapabilityGap, ...]
    equipment_score: float  # 0.0 to 1.0

    def to_dict(self) -> Dict:
        return {
            "consumer_id": self.consumer_id,
            "phase": self.phase,
            "declared_capabilities": sorted(self.declared_capabilities),
            "signal_types_subscribed": sorted(self.signal_types_subscribed),
            "signal_types_equipped": sorted(self.signal_types_equipped),
            "signal_types_unequipped": sorted(self.signal_types_unequipped),
            "capability_gaps": [
                {
                    "signal_type": g.signal_type,
                    "missing": sorted(g.missing_capabilities),
                    "severity": g.gap_severity,
                }
                for g in self.capability_gaps
            ],
            "equipment_score": round(self.equipment_score, 4),
        }


@dataclass
class EquipmentAuditResult:
    """Complete audit result for all consumers."""
    audit_timestamp: str
    total_consumers: int
    total_signal_types: int
    total_capability_gaps: int
    overall_equipment_score: float
    consumer_reports: Tuple[ConsumerEquipmentReport, ...]
    recommendations: Tuple[str, ...]

    def to_dict(self) -> Dict:
        return {
            "audit_timestamp": self.audit_timestamp,
            "summary": {
                "total_consumers": self.total_consumers,
                "total_signal_types": self.total_signal_types,
                "total_capability_gaps": self.total_capability_gaps,
                "overall_equipment_score": round(self.overall_equipment_score, 4),
            },
            "consumer_reports": [r.to_dict() for r in self.consumer_reports],
            "recommendations": list(self.recommendations),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


class EquipmentAuditor:
    """
    Audits consumer equipment against signal requirements.

    This auditor:
    1. Loads signal type → required capabilities mapping
    2. Loads consumer → declared capabilities mapping
    3. Computes capability matrix
    4. Identifies gaps
    5. Generates recommendations
    """

    # Canonical signal type to required capabilities mapping
    # This is the DEFINITIVE source of truth for what each signal needs
    SIGNAL_CAPABILITY_REQUIREMENTS: Dict[str, FrozenSet[str]] = {
        # Phase 0 - Assembly
        "SIGNAL_PACK": frozenset(["STATIC_LOAD", "SIGNAL_PACK"]),
        "STATIC_LOAD": frozenset(["STATIC_LOAD"]),

        # Phase 1 - Extraction (MC01-MC10)
        "MC01": frozenset(["EXTRACTION", "STRUCTURAL_PARSING"]),
        "MC02": frozenset(["EXTRACTION", "TRIPLET_EXTRACTION", "NUMERIC_PARSING"]),
        "MC03": frozenset(["EXTRACTION", "NORMATIVE_LOOKUP", "CITATION_PARSING"]),
        "MC04": frozenset(["EXTRACTION", "HIERARCHY_PARSING", "TREE_CONSTRUCTION"]),
        "MC05": frozenset(["EXTRACTION", "FINANCIAL_ANALYSIS", "NUMERIC_PARSING"]),
        "MC06": frozenset(["EXTRACTION", "POPULATION_PARSING", "DEMOGRAPHIC_ANALYSIS"]),
        "MC07": frozenset(["EXTRACTION", "TEMPORAL_PARSING", "DATE_NORMALIZATION"]),
        "MC08": frozenset(["EXTRACTION", "CAUSAL_ANALYSIS", "VERB_EXTRACTION"]),
        "MC09": frozenset(["EXTRACTION", "NER", "INSTITUTIONAL_RECOGNITION"]),
        "MC10": frozenset(["EXTRACTION", "SEMANTIC_ANALYSIS", "RELATIONSHIP_EXTRACTION"]),

        # Phase 2 - Enrichment
        "PATTERN_ENRICHMENT": frozenset(["ENRICHMENT", "PATTERN_MATCHING"]),
        "KEYWORD_ENRICHMENT": frozenset(["ENRICHMENT", "KEYWORD_EXTRACTION"]),
        "ENTITY_ENRICHMENT": frozenset(["ENRICHMENT", "ENTITY_RECOGNITION"]),

        # Phase 3 - Validation
        "NORMATIVE_VALIDATION": frozenset(["VALIDATION", "NORMATIVE_CHECK"]),
        "ENTITY_VALIDATION": frozenset(["VALIDATION", "ENTITY_CHECK"]),
        "COHERENCE_VALIDATION": frozenset(["VALIDATION", "COHERENCE_CHECK"]),

        # Phase 4-6 - Scoring
        "MICRO_SCORE": frozenset(["SCORING", "MICRO_LEVEL", "CHOQUET_INTEGRAL"]),
        "MESO_SCORE": frozenset(["SCORING", "MESO_LEVEL", "DIMENSION_AGGREGATION"]),
        "MACRO_SCORE": frozenset(["SCORING", "MACRO_LEVEL", "POLICY_AREA_AGGREGATION"]),

        # Phase 7-8 - Aggregation
        "MESO_AGGREGATION": frozenset(["AGGREGATION", "CLUSTER_LEVEL"]),
        "MACRO_AGGREGATION": frozenset(["AGGREGATION", "HOLISTIC_LEVEL"]),

        # Phase 9 - Report
        "REPORT_ASSEMBLY": frozenset(["REPORT_GENERATION", "ASSEMBLY", "EXPORT"]),
    }

    # Phase to signal type mapping
    PHASE_SIGNAL_MAPPING: Dict[str, FrozenSet[str]] = {
        "phase_0": frozenset(["SIGNAL_PACK", "STATIC_LOAD"]),
        "phase_1": frozenset(["MC01", "MC02", "MC03", "MC04", "MC05",
                             "MC06", "MC07", "MC08", "MC09", "MC10"]),
        "phase_2": frozenset(["PATTERN_ENRICHMENT", "KEYWORD_ENRICHMENT",
                             "ENTITY_ENRICHMENT"]),
        "phase_3": frozenset(["NORMATIVE_VALIDATION", "ENTITY_VALIDATION",
                             "COHERENCE_VALIDATION"]),
        "phase_4": frozenset(["MICRO_SCORE"]),
        "phase_5": frozenset(["MESO_SCORE"]),
        "phase_6": frozenset(["MACRO_SCORE"]),
        "phase_7": frozenset(["MESO_AGGREGATION"]),
        "phase_8": frozenset(["MACRO_AGGREGATION"]),
        "phase_9": frozenset(["REPORT_ASSEMBLY"]),
    }

    def __init__(self):
        self._audit_results: Optional[EquipmentAuditResult] = None

    def audit_consumer(
        self,
        consumer_id: str,
        phase: str,
        declared_capabilities: Set[str]
    ) -> ConsumerEquipmentReport:
        """Audit a single consumer's equipment."""
        declared = frozenset(declared_capabilities)
        subscribed_signals = self.PHASE_SIGNAL_MAPPING.get(phase, frozenset())

        equipped = set()
        unequipped = set()
        gaps = []

        for signal_type in subscribed_signals:
            required = self.SIGNAL_CAPABILITY_REQUIREMENTS.get(signal_type, frozenset())
            missing = required - declared

            if not missing:
                equipped.add(signal_type)
            else:
                unequipped.add(signal_type)
                gaps.append(CapabilityGap(
                    consumer_id=consumer_id,
                    signal_type=signal_type,
                    required_capabilities=required,
                    available_capabilities=declared,
                    missing_capabilities=frozenset(missing),
                ))

        total_subscribed = len(subscribed_signals)
        equipment_score = len(equipped) / total_subscribed if total_subscribed > 0 else 1.0

        return ConsumerEquipmentReport(
            consumer_id=consumer_id,
            phase=phase,
            declared_capabilities=declared,
            signal_types_subscribed=subscribed_signals,
            signal_types_equipped=frozenset(equipped),
            signal_types_unequipped=frozenset(unequipped),
            capability_gaps=tuple(gaps),
            equipment_score=equipment_score,
        )

    def audit_all_consumers(
        self,
        consumer_configs: List[Dict]
    ) -> EquipmentAuditResult:
        """Audit all consumers and generate comprehensive report."""
        reports = []
        total_gaps = 0

        for config in consumer_configs:
            consumer_id = config["consumer_id"]
            # Extract phase from consumer_id (e.g., "phase_01_extraction_consumer" -> "phase_1")
            phase_part = consumer_id.split("_")[1]  # "01", "02", etc.
            phase = f"phase_{int(phase_part)}"

            report = self.audit_consumer(
                consumer_id=consumer_id,
                phase=phase,
                declared_capabilities=set(config.get("capabilities", [])),
            )
            reports.append(report)
            total_gaps += len(report.capability_gaps)

        # Calculate overall score
        if reports:
            overall_score = sum(r.equipment_score for r in reports) / len(reports)
        else:
            overall_score = 0.0

        # Generate recommendations
        recommendations = self._generate_recommendations(reports)

        result = EquipmentAuditResult(
            audit_timestamp=datetime.utcnow().isoformat(),
            total_consumers=len(reports),
            total_signal_types=len(self.SIGNAL_CAPABILITY_REQUIREMENTS),
            total_capability_gaps=total_gaps,
            overall_equipment_score=overall_score,
            consumer_reports=tuple(reports),
            recommendations=tuple(recommendations),
        )

        self._audit_results = result
        return result

    def _generate_recommendations(
        self,
        reports: List[ConsumerEquipmentReport]
    ) -> List[str]:
        """Generate actionable recommendations from audit results."""
        recommendations = []

        for report in reports:
            if report.equipment_score < 1.0:
                missing_all = set()
                for gap in report.capability_gaps:
                    missing_all.update(gap.missing_capabilities)

                if missing_all:
                    recommendations.append(
                        f"Consumer '{report.consumer_id}' is missing capabilities: "
                        f"{sorted(missing_all)}. Add these to handle all subscribed signals."
                    )

        if not recommendations:
            recommendations.append("All consumers are fully equipped for their subscribed signals.")

        return recommendations

    def save_report(self, output_path: Path) -> None:
        """Save audit report to JSON file."""
        if self._audit_results is None:
            raise ValueError("No audit results available. Run audit_all_consumers first.")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(self._audit_results.to_json(indent=2))

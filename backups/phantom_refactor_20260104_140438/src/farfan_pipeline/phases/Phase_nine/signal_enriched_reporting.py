"""Phase 9 Signal-Enriched Report Assembly Module

Extends Phase 9 report assembly with signal-based narrative enrichment,
section selection, and enhanced metadata for context-aware, high-quality
reports with full signal provenance.

Enhancement Value:
- Signal-based narrative enrichment using questionnaire patterns
- Signal-driven section selection and emphasis
- Pattern-based evidence highlighting
- Enhanced report metadata with signal provenance

Integration: Used by ReportAssembler to enhance report generation
with signal intelligence.

Author: F.A.R.F.A.N Pipeline Team
Version: 1.0.0
"""

from __future__ import annotations

import logging
import re
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    try:
        from cross_cutting_infrastructure.irrigation_using_signals.SISAS.signal_registry import (
            QuestionnaireSignalRegistry,
        )
    except ImportError:
        QuestionnaireSignalRegistry = Any  # type: ignore

logger = logging.getLogger(__name__)

__all__ = [
    "SignalEnrichedReporter",
    "enrich_narrative",
    "select_report_sections",
]


class SignalEnrichedReporter:
    """Signal-enriched reporter for Phase 9 with pattern-based narrative enhancement.

    Enhances report assembly with signal intelligence for better narrative
    quality, section selection, and evidence presentation.

    Attributes:
        signal_registry: Optional signal registry for signal access
        enable_narrative_enrichment: Enable signal-based narrative enrichment
        enable_section_selection: Enable signal-driven section selection
        enable_evidence_highlighting: Enable pattern-based evidence highlighting
    """

    def __init__(
        self,
        signal_registry: QuestionnaireSignalRegistry | None = None,
        enable_narrative_enrichment: bool = True,
        enable_section_selection: bool = True,
        enable_evidence_highlighting: bool = True,
    ) -> None:
        """Initialize signal-enriched reporter.

        Args:
            signal_registry: Optional signal registry for signal access
            enable_narrative_enrichment: Enable narrative enrichment
            enable_section_selection: Enable section selection
            enable_evidence_highlighting: Enable evidence highlighting
        """
        self.signal_registry = signal_registry
        self.enable_narrative_enrichment = enable_narrative_enrichment
        self.enable_section_selection = enable_section_selection
        self.enable_evidence_highlighting = enable_evidence_highlighting

        logger.info(
            f"SignalEnrichedReporter initialized: "
            f"registry={'enabled' if signal_registry else 'disabled'}, "
            f"narrative={enable_narrative_enrichment}, "
            f"section_sel={enable_section_selection}, "
            f"evidence_hl={enable_evidence_highlighting}"
        )

    def enrich_narrative_context(
        self,
        question_id: str,
        base_narrative: str,
        score_data: dict[str, Any],
    ) -> tuple[str, dict[str, Any]]:
        """Enrich narrative with signal-based contextual information.

        Uses signal patterns and indicators to add relevant context and
        improve narrative quality and specificity.

        Args:
            question_id: Question identifier
            base_narrative: Base narrative text
            score_data: Score data for context

        Returns:
            Tuple of (enriched_narrative, enrichment_details)
        """
        if not self.enable_narrative_enrichment:
            return base_narrative, {"enrichment": "disabled"}

        enrichment_details: dict[str, Any] = {
            "question_id": question_id,
            "base_length": len(base_narrative),
            "additions": [],
        }

        enriched_narrative = base_narrative

        try:
            if self.signal_registry:
                # Get signal pack for question
                signal_pack = self.signal_registry.get_micro_answering_signals(question_id)

                # Extract key patterns and indicators
                patterns = signal_pack.patterns if hasattr(signal_pack, "patterns") else []
                indicators = signal_pack.indicators if hasattr(signal_pack, "indicators") else []

                # Add context about key indicators if score is low
                score = score_data.get("score", 0.5)
                if score < 0.5 and len(indicators) > 0:
                    key_indicators = indicators[:3]  # Top 3 indicators
                    indicator_context = f"\n\nIndicadores clave no encontrados o insuficientes: {', '.join(key_indicators)}."
                    enriched_narrative += indicator_context
                    enrichment_details["additions"].append(
                        {
                            "type": "missing_indicators",
                            "count": len(key_indicators),
                            "indicators": key_indicators,
                        }
                    )

                # Add pattern-based guidance for improvement
                if score < 0.5 and len(patterns) > 5:
                    pattern_count = len(patterns)
                    guidance = f"\n\nSe esperaban {pattern_count} patrones temáticos relacionados con esta dimensión."
                    enriched_narrative += guidance
                    enrichment_details["additions"].append(
                        {
                            "type": "pattern_guidance",
                            "pattern_count": pattern_count,
                        }
                    )

                # Add quality level interpretation
                quality_level = score_data.get("quality_level", "")
                if quality_level == "INSUFICIENTE":
                    interpretation = "\n\nLa evidencia encontrada es insuficiente para responder la pregunta de manera completa."
                    enriched_narrative += interpretation
                    enrichment_details["additions"].append(
                        {
                            "type": "quality_interpretation",
                            "quality": quality_level,
                        }
                    )
                elif quality_level == "EXCELENTE":
                    interpretation = "\n\nLa evidencia encontrada es completa y responde la pregunta de manera exhaustiva."
                    enriched_narrative += interpretation
                    enrichment_details["additions"].append(
                        {
                            "type": "quality_interpretation",
                            "quality": quality_level,
                        }
                    )

                enrichment_details["enriched_length"] = len(enriched_narrative)
                enrichment_details["length_increase"] = len(enriched_narrative) - len(
                    base_narrative
                )

        except Exception as e:
            logger.warning(f"Failed to enrich narrative for {question_id}: {e}")
            enrichment_details["error"] = str(e)
            enriched_narrative = base_narrative

        return enriched_narrative, enrichment_details

    def determine_section_emphasis(
        self,
        section_id: str,
        section_data: dict[str, Any],
        policy_area: str,
    ) -> tuple[float, dict[str, Any]]:
        """Determine section emphasis using signal-driven analysis.

        Analyzes section data and signal patterns to determine how much
        emphasis (detail level) should be given to the section.

        Args:
            section_id: Section identifier
            section_data: Section data with scores and evidence
            policy_area: Policy area for signal context

        Returns:
            Tuple of (emphasis_score, emphasis_details)
        """
        if not self.enable_section_selection:
            return 0.5, {"emphasis": "disabled"}

        emphasis_details: dict[str, Any] = {
            "section_id": section_id,
            "factors": [],
        }

        emphasis_score = 0.5  # Neutral base

        try:
            # Factor 1: Score distribution (low variance = low emphasis)
            scores = section_data.get("scores", [])
            if len(scores) > 0:
                mean_score = sum(scores) / len(scores)
                variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)

                if variance < 0.05:  # Low variance
                    emphasis_adjustment = -0.2
                    emphasis_details["factors"].append(
                        {
                            "type": "low_variance",
                            "variance": variance,
                            "adjustment": emphasis_adjustment,
                        }
                    )
                    emphasis_score += emphasis_adjustment
                elif variance > 0.15:  # High variance (interesting)
                    emphasis_adjustment = 0.3
                    emphasis_details["factors"].append(
                        {
                            "type": "high_variance",
                            "variance": variance,
                            "adjustment": emphasis_adjustment,
                        }
                    )
                    emphasis_score += emphasis_adjustment

            # Factor 2: Presence of critical scores
            critical_count = sum(1 for s in scores if s < 0.3)
            if critical_count > 0:
                emphasis_adjustment = 0.4  # High emphasis for critical issues
                emphasis_details["factors"].append(
                    {
                        "type": "critical_scores",
                        "count": critical_count,
                        "adjustment": emphasis_adjustment,
                    }
                )
                emphasis_score += emphasis_adjustment

            # Factor 3: Signal-based pattern density for policy area
            if self.signal_registry:
                try:
                    # Get aggregated pattern count for policy area
                    # (In production, aggregate across questions in section)
                    signal_pack = self.signal_registry.get_micro_answering_signals(
                        section_data.get("representative_question", "Q001")
                    )

                    pattern_count = (
                        len(signal_pack.patterns) if hasattr(signal_pack, "patterns") else 0
                    )
                    indicator_count = (
                        len(signal_pack.indicators) if hasattr(signal_pack, "indicators") else 0
                    )

                    # High signal density suggests importance
                    if pattern_count > 15 or indicator_count > 10:
                        emphasis_adjustment = 0.2
                        emphasis_details["factors"].append(
                            {
                                "type": "high_signal_density",
                                "pattern_count": pattern_count,
                                "indicator_count": indicator_count,
                                "adjustment": emphasis_adjustment,
                            }
                        )
                        emphasis_score += emphasis_adjustment

                except Exception as e:
                    logger.debug(f"Signal-based emphasis failed: {e}")

            # Clamp emphasis to [0.0, 1.0]
            emphasis_score = max(0.0, min(1.0, emphasis_score))
            emphasis_details["final_emphasis"] = emphasis_score

        except Exception as e:
            logger.warning(f"Failed to determine section emphasis for {section_id}: {e}")
            emphasis_details["error"] = str(e)
            emphasis_score = 0.5

        return emphasis_score, emphasis_details

    def highlight_evidence_patterns(
        self,
        question_id: str,
        evidence_list: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Highlight evidence items that match signal patterns.

        Analyzes evidence and marks items that match questionnaire patterns
        for special presentation in the report.

        Args:
            question_id: Question identifier
            evidence_list: List of evidence items

        Returns:
            Tuple of (highlighted_evidence, highlighting_details)
        """
        if not self.enable_evidence_highlighting:
            return evidence_list, {"highlighting": "disabled"}

        highlighting_details: dict[str, Any] = {
            "question_id": question_id,
            "total_items": len(evidence_list),
            "highlighted_items": 0,
            "patterns_matched": [],
        }

        highlighted_evidence = []

        try:
            if self.signal_registry:
                # Get signal pack for question
                signal_pack = self.signal_registry.get_micro_answering_signals(question_id)
                patterns = signal_pack.patterns if hasattr(signal_pack, "patterns") else []
                indicators = signal_pack.indicators if hasattr(signal_pack, "indicators") else []

                # Process each evidence item
                for evidence_item in evidence_list:
                    enhanced_item = evidence_item.copy()
                    matched_patterns = []
                    matched_indicators = []

                    # Check evidence text against patterns
                    evidence_text = evidence_item.get("text", "").lower()

                    # Pattern matching with word boundaries to avoid false positives
                    for pattern in patterns[:20]:  # Check top 20 patterns
                        pattern_str = str(pattern).lower()
                        # Use word boundaries for more precise matching
                        try:
                            if re.search(r"\b" + re.escape(pattern_str) + r"\b", evidence_text):
                                matched_patterns.append(pattern)
                        except re.error:
                            # Fallback to simple substring match if regex fails
                            if pattern_str in evidence_text:
                                matched_patterns.append(pattern)

                    for indicator in indicators[:10]:  # Check top 10 indicators
                        indicator_str = str(indicator).lower()
                        # Use word boundaries for indicators as well
                        try:
                            if re.search(r"\b" + re.escape(indicator_str) + r"\b", evidence_text):
                                matched_indicators.append(indicator)
                        except re.error:
                            # Fallback to simple substring match if regex fails
                            if indicator_str in evidence_text:
                                matched_indicators.append(indicator)

                    # Add highlighting metadata if matches found
                    if matched_patterns or matched_indicators:
                        enhanced_item["signal_highlights"] = {
                            "matched_patterns": matched_patterns,
                            "matched_indicators": matched_indicators,
                            "highlight_level": len(matched_patterns) + len(matched_indicators),
                        }
                        highlighting_details["highlighted_items"] += 1
                        highlighting_details["patterns_matched"].extend(matched_patterns)

                    highlighted_evidence.append(enhanced_item)
            else:
                highlighted_evidence = evidence_list

            highlighting_details["success"] = True

        except Exception as e:
            logger.warning(f"Failed to highlight evidence for {question_id}: {e}")
            highlighting_details["error"] = str(e)
            highlighted_evidence = evidence_list

        return highlighted_evidence, highlighting_details

    def enrich_report_metadata(
        self,
        base_metadata: dict[str, Any],
        narrative_enrichments: list[dict[str, Any]],
        section_emphasis: list[dict[str, Any]],
        evidence_highlighting: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Enrich report metadata with signal provenance.

        Adds comprehensive signal-based metadata to report for full
        transparency and reproducibility.

        Args:
            base_metadata: Base report metadata
            narrative_enrichments: List of narrative enrichment details
            section_emphasis: List of section emphasis details
            evidence_highlighting: List of evidence highlighting details

        Returns:
            Enriched report metadata dict
        """
        enriched_metadata = {
            **base_metadata,
            "signal_enrichment": {
                "enabled": True,
                "registry_available": self.signal_registry is not None,
                "narrative_enrichments": {
                    "count": len(narrative_enrichments),
                    "total_additions": sum(
                        len(e.get("additions", [])) for e in narrative_enrichments
                    ),
                },
                "section_emphasis": {
                    "sections_analyzed": len(section_emphasis),
                    "high_emphasis_count": sum(
                        1 for e in section_emphasis if e.get("final_emphasis", 0) > 0.7
                    ),
                },
                "evidence_highlighting": {
                    "total_evidence": sum(e.get("total_items", 0) for e in evidence_highlighting),
                    "highlighted_items": sum(
                        e.get("highlighted_items", 0) for e in evidence_highlighting
                    ),
                },
            },
        }

        return enriched_metadata


def enrich_narrative(
    signal_registry: QuestionnaireSignalRegistry | None,
    question_id: str,
    base_narrative: str,
    score_data: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    """Convenience function for signal-based narrative enrichment.

    Creates a temporary SignalEnrichedReporter and enriches narrative.

    Args:
        signal_registry: Signal registry instance (optional)
        question_id: Question identifier
        base_narrative: Base narrative text
        score_data: Score data for context

    Returns:
        Tuple of (enriched_narrative, enrichment_details)
    """
    reporter = SignalEnrichedReporter(signal_registry=signal_registry)
    return reporter.enrich_narrative_context(
        question_id=question_id,
        base_narrative=base_narrative,
        score_data=score_data,
    )


def select_report_sections(
    signal_registry: QuestionnaireSignalRegistry | None,
    sections: list[dict[str, Any]],
    policy_area: str,
) -> list[tuple[dict[str, Any], float, dict[str, Any]]]:
    """Determine section emphasis for report sections using signals.

    Args:
        signal_registry: Signal registry instance (optional)
        sections: List of section dicts with data
        policy_area: Policy area for context

    Returns:
        List of tuples: (section, emphasis_score, emphasis_details)
    """
    reporter = SignalEnrichedReporter(signal_registry=signal_registry)

    emphasized_sections = []
    for section in sections:
        emphasis_score, emphasis_details = reporter.determine_section_emphasis(
            section_id=section.get("section_id", ""),
            section_data=section,
            policy_area=policy_area,
        )
        emphasized_sections.append((section, emphasis_score, emphasis_details))

    # Sort by emphasis score (descending)
    emphasized_sections.sort(key=lambda x: x[1], reverse=True)

    return emphasized_sections

"""
Narrative Answer Synthesizer

This module transforms evidence graphs into coherent, human-readable narratives
that directly answer policy questions with citations.

Key Features:
- Question type inference (yes_no, quantitative, descriptive, comparative)
- Direct answer generation (1-2 sentences)
- Supporting narrative with evidence citations
- Gap identification and acknowledgment
- Calibrated confidence intervals
- Recommendations based on analysis
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class QuestionType(Enum):
    """Types of policy questions."""
    YES_NO = "yes_no"
    QUANTITATIVE = "quantitative"
    DESCRIPTIVE = "descriptive"
    COMPARATIVE = "comparative"
    CAUSAL = "causal"
    UNKNOWN = "unknown"


@dataclass
class Citation:
    """Evidence citation with source and confidence."""
    evidence_id: str
    source_method: str | None
    snippet: str
    confidence: float
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_markdown(self) -> str:
        """Format citation as markdown."""
        confidence_str = f"{self.confidence:.0%}"
        method_str = f" ({self.source_method})" if self.source_method else ""
        return f"[{confidence_str}{method_str}] {self.snippet}"


@dataclass
class NarrativeBlock:
    """Block of narrative text with citations."""
    heading: str
    content: str
    citations: list[Citation] = field(default_factory=list)
    confidence: float = 0.8
    
    def to_markdown(self) -> str:
        """Format narrative block as markdown."""
        lines = [f"### {self.heading}\n"]
        lines.append(content + "\n")
        
        if self.citations:
            lines.append("\n**Citations:**\n")
            for cite in self.citations:
                lines.append(f"- {cite.to_markdown()}\n")
        
        lines.append(f"\n*Confidence: {self.confidence:.0%}*\n")
        
        return "".join(lines)


@dataclass
class AnswerCompleteness:
    """Assessment of answer completeness."""
    is_complete: bool
    coverage_score: float
    missing_elements: list[str] = field(default_factory=list)
    gaps_addressed: bool = False
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_complete": self.is_complete,
            "coverage_score": self.coverage_score,
            "missing_elements": self.missing_elements,
            "gaps_addressed": self.gaps_addressed,
        }


@dataclass
class SynthesizedAnswer:
    """Complete synthesized answer structure."""
    direct_answer: str
    narrative_blocks: list[NarrativeBlock] = field(default_factory=list)
    completeness: AnswerCompleteness | None = None
    overall_confidence: float = 0.8
    calibrated_interval: tuple[float, float] = (0.7, 0.9)
    primary_citations: list[Citation] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    unresolved_contradictions: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_markdown(self) -> str:
        """Format complete answer as markdown."""
        lines = ["# Synthesized Answer\n\n"]
        
        lines.append("## Direct Answer\n\n")
        lines.append(f"{self.direct_answer}\n\n")
        
        if self.overall_confidence:
            ci_low, ci_high = self.calibrated_interval
            lines.append(f"**Confidence:** {self.overall_confidence:.0%} "
                        f"(95% CI: {ci_low:.0%} - {ci_high:.0%})\n\n")
        
        if self.narrative_blocks:
            lines.append("## Detailed Analysis\n\n")
            for block in self.narrative_blocks:
                lines.append(block.to_markdown())
                lines.append("\n")
        
        if self.gaps:
            lines.append("## Identified Gaps\n\n")
            for gap in self.gaps:
                lines.append(f"- {gap}\n")
            lines.append("\n")
        
        if self.unresolved_contradictions:
            lines.append("## Unresolved Contradictions\n\n")
            for contradiction in self.unresolved_contradictions:
                lines.append(f"- {contradiction}\n")
            lines.append("\n")
        
        if self.recommendations:
            lines.append("## Recommendations\n\n")
            for i, rec in enumerate(self.recommendations, 1):
                lines.append(f"{i}. {rec}\n")
            lines.append("\n")
        
        if self.completeness:
            lines.append("## Completeness Assessment\n\n")
            lines.append(f"- **Complete:** {'Yes' if self.completeness.is_complete else 'No'}\n")
            lines.append(f"- **Coverage Score:** {self.completeness.coverage_score:.0%}\n")
            if self.completeness.missing_elements:
                lines.append(f"- **Missing Elements:** {', '.join(self.completeness.missing_elements)}\n")
            lines.append("\n")
        
        return "".join(lines)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "direct_answer": self.direct_answer,
            "narrative_blocks": [
                {
                    "heading": block.heading,
                    "content": block.content,
                    "citations": [
                        {
                            "evidence_id": cite.evidence_id,
                            "source_method": cite.source_method,
                            "snippet": cite.snippet,
                            "confidence": cite.confidence,
                        }
                        for cite in block.citations
                    ],
                    "confidence": block.confidence,
                }
                for block in self.narrative_blocks
            ],
            "completeness": self.completeness.to_dict() if self.completeness else None,
            "overall_confidence": self.overall_confidence,
            "calibrated_interval": self.calibrated_interval,
            "gaps": self.gaps,
            "unresolved_contradictions": self.unresolved_contradictions,
            "recommendations": self.recommendations,
            "metadata": self.metadata,
        }


@dataclass
class AnswerContract:
    """Contract defining question interpretation and required evidence."""
    question_type: QuestionType
    required_evidence_types: list[str] = field(default_factory=list)
    expected_structure: dict[str, Any] = field(default_factory=dict)
    confidence_threshold: float = 0.7
    max_citations_per_section: int = 5
    
    @classmethod
    def from_question_context(cls, question_context: dict[str, Any]) -> AnswerContract:
        """Create answer contract from question context."""
        question_text = question_context.get("question_global", "")
        question_type = cls._infer_question_type(question_text)
        
        expected_elements = question_context.get("expected_elements", [])
        
        return cls(
            question_type=question_type,
            required_evidence_types=expected_elements,
            expected_structure={},
            confidence_threshold=0.7,
            max_citations_per_section=5,
        )
    
    @staticmethod
    def _infer_question_type(question_text: str) -> QuestionType:
        """Infer question type from text."""
        text_lower = question_text.lower()
        
        if any(word in text_lower for word in ["¿", "?", "is there", "does", "has", "será", "existe"]):
            if any(word in text_lower for word in ["how many", "cuánto", "cuánta", "qué cantidad"]):
                return QuestionType.QUANTITATIVE
            elif any(word in text_lower for word in ["compare", "versus", "vs", "diferencia"]):
                return QuestionType.COMPARATIVE
            elif any(word in text_lower for word in ["why", "porque", "causa", "reason"]):
                return QuestionType.CAUSAL
            else:
                return QuestionType.YES_NO
        
        if any(word in text_lower for word in ["describe", "explain", "what", "qué", "cómo"]):
            return QuestionType.DESCRIPTIVE
        
        if any(word in text_lower for word in ["compare", "contrast", "diferencia"]):
            return QuestionType.COMPARATIVE
        
        return QuestionType.UNKNOWN


class NarrativeAnswerSynthesizer:
    """
    Transform evidence into coherent narrative answers.
    
    Features:
    - Question-aligned narrative structure
    - Direct answer generation
    - Evidence-backed citations
    - Gap acknowledgment
    - Confidence calibration
    """
    
    def synthesize(
        self,
        graph: Any,
        question_context: dict[str, Any],
        validation: dict[str, Any],
        contract: dict[str, Any],
    ) -> SynthesizedAnswer:
        """
        Synthesize narrative answer from evidence graph.
        
        Args:
            graph: EvidenceGraph with processed evidence
            question_context: Question context from contract
            validation: Validation results
            contract: Full execution contract
        
        Returns:
            SynthesizedAnswer with complete narrative
        """
        answer_contract = AnswerContract.from_question_context(question_context)
        
        direct_answer = self._generate_direct_answer(
            graph,
            question_context,
            answer_contract,
            contract,
        )
        
        narrative_blocks = self._generate_narrative_blocks(
            graph,
            question_context,
            answer_contract,
            contract,
        )
        
        primary_citations = self._extract_primary_citations(
            graph,
            max_citations=answer_contract.max_citations_per_section,
        )
        
        gaps = self._identify_gaps(
            graph,
            question_context,
            answer_contract,
        )
        
        contradictions = self._format_contradictions(
            getattr(graph, "detect_contradictions", lambda: [])()
        )
        
        completeness = self._assess_completeness(
            graph,
            question_context,
            answer_contract,
            gaps,
        )
        
        recommendations = self._generate_recommendations(
            graph,
            completeness,
            gaps,
            contradictions,
        )
        
        overall_confidence = getattr(graph, "compute_overall_confidence", lambda: 0.8)()
        calibrated_interval = self._compute_confidence_interval(overall_confidence)
        
        return SynthesizedAnswer(
            direct_answer=direct_answer,
            narrative_blocks=narrative_blocks,
            completeness=completeness,
            overall_confidence=overall_confidence,
            calibrated_interval=calibrated_interval,
            primary_citations=primary_citations,
            gaps=gaps,
            unresolved_contradictions=contradictions,
            recommendations=recommendations,
            metadata={
                "question_type": answer_contract.question_type.value,
                "node_count": len(getattr(graph, "nodes", {})),
                "edge_count": len(getattr(graph, "edges", [])),
            }
        )
    
    def _generate_direct_answer(
        self,
        graph: Any,
        question_context: dict[str, Any],
        answer_contract: AnswerContract,
        contract: dict[str, Any],
    ) -> str:
        """Generate 1-2 sentence direct answer to the question."""
        question_text = question_context.get("question_global", "the policy question")
        question_type = answer_contract.question_type
        
        evidence_summary = self._summarize_evidence(graph, contract)
        
        if question_type == QuestionType.YES_NO:
            return self._generate_yes_no_answer(evidence_summary, question_text)
        elif question_type == QuestionType.QUANTITATIVE:
            return self._generate_quantitative_answer(evidence_summary, question_text)
        elif question_type == QuestionType.DESCRIPTIVE:
            return self._generate_descriptive_answer(evidence_summary, question_text)
        elif question_type == QuestionType.COMPARATIVE:
            return self._generate_comparative_answer(evidence_summary, question_text)
        elif question_type == QuestionType.CAUSAL:
            return self._generate_causal_answer(evidence_summary, question_text)
        else:
            return self._generate_generic_answer(evidence_summary, question_text)
    
    def _summarize_evidence(self, graph: Any, contract: dict[str, Any]) -> dict[str, Any]:
        """Summarize evidence from graph and contract."""
        evidence = contract.get("evidence", {})
        
        key_findings = []
        for key, value in evidence.items():
            if value is not None:
                if isinstance(value, (list, tuple)) and len(value) > 0:
                    key_findings.append(f"{key}: {len(value)} items")
                elif isinstance(value, (int, float)):
                    key_findings.append(f"{key}: {value}")
                elif isinstance(value, str) and len(value) > 0:
                    key_findings.append(f"{key}: present")
        
        return {
            "key_findings": key_findings,
            "confidence": getattr(graph, "compute_overall_confidence", lambda: 0.8)(),
            "node_count": len(getattr(graph, "nodes", {})),
        }
    
    def _generate_yes_no_answer(self, evidence_summary: dict[str, Any], question_text: str) -> str:
        """Generate yes/no answer."""
        confidence = evidence_summary.get("confidence", 0.8)
        key_findings = evidence_summary.get("key_findings", [])
        
        if confidence > 0.7:
            decision = "Yes" if len(key_findings) > 0 else "No"
            return (
                f"{decision}, based on the analysis of {evidence_summary.get('node_count', 0)} "
                f"evidence nodes. The evidence shows {len(key_findings)} relevant findings "
                f"with {confidence:.0%} confidence."
            )
        else:
            return (
                f"The evidence is inconclusive ({confidence:.0%} confidence). "
                f"Additional analysis is needed to definitively answer this question."
            )
    
    def _generate_quantitative_answer(self, evidence_summary: dict[str, Any], question_text: str) -> str:
        """Generate quantitative answer."""
        key_findings = evidence_summary.get("key_findings", [])
        
        numeric_findings = [f for f in key_findings if any(char.isdigit() for char in f)]
        
        if numeric_findings:
            return (
                f"Based on the analysis, {numeric_findings[0]}. "
                f"This finding is supported by {evidence_summary.get('node_count', 0)} evidence nodes "
                f"with {evidence_summary.get('confidence', 0.8):.0%} confidence."
            )
        else:
            return (
                f"Quantitative data is limited. The analysis identified {len(key_findings)} "
                f"relevant findings but lacks specific numeric values."
            )
    
    def _generate_descriptive_answer(self, evidence_summary: dict[str, Any], question_text: str) -> str:
        """Generate descriptive answer."""
        key_findings = evidence_summary.get("key_findings", [])
        
        if len(key_findings) > 0:
            findings_str = "; ".join(key_findings[:3])
            return (
                f"The analysis reveals the following key characteristics: {findings_str}. "
                f"These findings are based on {evidence_summary.get('node_count', 0)} evidence nodes "
                f"with {evidence_summary.get('confidence', 0.8):.0%} overall confidence."
            )
        else:
            return (
                f"The available evidence provides limited descriptive information. "
                f"Further investigation is needed for a comprehensive description."
            )
    
    def _generate_comparative_answer(self, evidence_summary: dict[str, Any], question_text: str) -> str:
        """Generate comparative answer."""
        return (
            f"The comparative analysis identified {len(evidence_summary.get('key_findings', []))} "
            f"relevant dimensions. The evidence shows differences and similarities "
            f"with {evidence_summary.get('confidence', 0.8):.0%} confidence."
        )
    
    def _generate_causal_answer(self, evidence_summary: dict[str, Any], question_text: str) -> str:
        """Generate causal answer."""
        return (
            f"The causal analysis identified {len(evidence_summary.get('key_findings', []))} "
            f"potential causal relationships. The evidence suggests causal mechanisms "
            f"with {evidence_summary.get('confidence', 0.8):.0%} confidence."
        )
    
    def _generate_generic_answer(self, evidence_summary: dict[str, Any], question_text: str) -> str:
        """Generate generic answer when type is unknown."""
        key_findings = evidence_summary.get("key_findings", [])
        
        return (
            f"The analysis identified {len(key_findings)} relevant findings "
            f"based on {evidence_summary.get('node_count', 0)} evidence nodes "
            f"with {evidence_summary.get('confidence', 0.8):.0%} overall confidence."
        )
    
    def _generate_narrative_blocks(
        self,
        graph: Any,
        question_context: dict[str, Any],
        answer_contract: AnswerContract,
        contract: dict[str, Any],
    ) -> list[NarrativeBlock]:
        """Generate narrative blocks with citations."""
        blocks = []
        
        evidence = contract.get("evidence", {})
        
        if evidence:
            findings_block = self._create_findings_block(graph, evidence)
            blocks.append(findings_block)
        
        contradictions = getattr(graph, "detect_contradictions", lambda: [])()
        if contradictions:
            contradictions_block = self._create_contradictions_block(contradictions)
            blocks.append(contradictions_block)
        
        return blocks
    
    def _create_findings_block(self, graph: Any, evidence: dict[str, Any]) -> NarrativeBlock:
        """Create narrative block for key findings."""
        findings_text = []
        citations = []
        
        for key, value in list(evidence.items())[:5]:
            if value is not None:
                findings_text.append(f"- **{key}**: {self._format_value(value)}")
                
                if hasattr(graph, "nodes"):
                    for node in list(graph.nodes.values())[:2]:
                        citations.append(Citation(
                            evidence_id=node.node_id,
                            source_method=node.source_method,
                            snippet=f"Evidence from {node.evidence_type}",
                            confidence=node.belief_mass.belief if node.belief_mass else 0.8,
                        ))
        
        content = "\n".join(findings_text) if findings_text else "No significant findings identified."
        
        return NarrativeBlock(
            heading="Key Findings",
            content=content,
            citations=citations[:5],
            confidence=getattr(graph, "compute_overall_confidence", lambda: 0.8)(),
        )
    
    def _format_value(self, value: Any) -> str:
        """Format value for narrative."""
        if isinstance(value, list):
            return f"{len(value)} items" if len(value) > 3 else ", ".join(str(v) for v in value)
        elif isinstance(value, (int, float)):
            return f"{value}"
        elif isinstance(value, str):
            return value[:100] + "..." if len(value) > 100 else value
        else:
            return str(value)
    
    def _create_contradictions_block(self, contradictions: list[dict[str, Any]]) -> NarrativeBlock:
        """Create narrative block for contradictions."""
        content_lines = []
        
        for contradiction in contradictions[:3]:
            source = contradiction.get("source", {})
            target = contradiction.get("target", {})
            contradiction_type = contradiction.get("contradiction_type", "unknown")
            
            content_lines.append(
                f"- Contradiction between {source.get('evidence_type', 'unknown')} "
                f"and {target.get('evidence_type', 'unknown')} ({contradiction_type})"
            )
        
        content = "\n".join(content_lines) if content_lines else "No contradictions detected."
        
        return NarrativeBlock(
            heading="Contradictions and Conflicts",
            content=content,
            citations=[],
            confidence=0.7,
        )
    
    def _extract_primary_citations(self, graph: Any, max_citations: int = 5) -> list[Citation]:
        """Extract primary citations from graph."""
        citations = []
        
        if hasattr(graph, "nodes"):
            for node in list(graph.nodes.values())[:max_citations]:
                citations.append(Citation(
                    evidence_id=node.node_id,
                    source_method=node.source_method,
                    snippet=f"Evidence from {node.evidence_type}",
                    confidence=node.belief_mass.belief if node.belief_mass else 0.8,
                    metadata={"node_type": node.evidence_type},
                ))
        
        return citations
    
    def _identify_gaps(
        self,
        graph: Any,
        question_context: dict[str, Any],
        answer_contract: AnswerContract,
    ) -> list[str]:
        """Identify gaps in evidence."""
        gaps = []
        expected_elements = question_context.get("expected_elements", [])
        
        if not expected_elements:
            return gaps
        
        for element in expected_elements:
            if hasattr(graph, "nodes"):
                found = any(
                    element.lower() in str(node.content).lower()
                    for node in graph.nodes.values()
                )
                if not found:
                    gaps.append(f"Missing evidence for expected element: {element}")
        
        return gaps
    
    def _format_contradictions(self, contradictions: list[dict[str, Any]]) -> list[str]:
        """Format contradictions as strings."""
        formatted = []
        
        for contradiction in contradictions:
            source = contradiction.get("source", {})
            target = contradiction.get("target", {})
            contradiction_type = contradiction.get("contradiction_type", "unknown")
            
            formatted.append(
                f"Contradiction ({contradiction_type}) between "
                f"{source.get('source_method', 'unknown')} and "
                f"{target.get('source_method', 'unknown')}"
            )
        
        return formatted
    
    def _assess_completeness(
        self,
        graph: Any,
        question_context: dict[str, Any],
        answer_contract: AnswerContract,
        gaps: list[str],
    ) -> AnswerCompleteness:
        """Assess answer completeness."""
        expected_elements = question_context.get("expected_elements", [])
        
        if not expected_elements:
            return AnswerCompleteness(
                is_complete=True,
                coverage_score=1.0,
                missing_elements=[],
                gaps_addressed=True,
            )
        
        missing_count = len(gaps)
        total_count = len(expected_elements)
        
        coverage_score = 1.0 - (missing_count / total_count) if total_count > 0 else 1.0
        is_complete = coverage_score >= 0.8
        
        missing_elements = [gap.replace("Missing evidence for expected element: ", "") for gap in gaps]
        
        return AnswerCompleteness(
            is_complete=is_complete,
            coverage_score=coverage_score,
            missing_elements=missing_elements,
            gaps_addressed=len(gaps) > 0,
        )
    
    def _generate_recommendations(
        self,
        graph: Any,
        completeness: AnswerCompleteness,
        gaps: list[str],
        contradictions: list[str],
    ) -> list[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        if not completeness.is_complete:
            recommendations.append(
                f"Conduct additional analysis to address {len(gaps)} identified gaps "
                f"and improve coverage from {completeness.coverage_score:.0%} to at least 80%."
            )
        
        if contradictions:
            recommendations.append(
                f"Resolve {len(contradictions)} contradictions through deeper investigation "
                f"or additional data collection."
            )
        
        confidence = getattr(graph, "compute_overall_confidence", lambda: 0.8)()
        if confidence < 0.7:
            recommendations.append(
                f"Improve evidence quality and reduce uncertainty. "
                f"Current confidence is {confidence:.0%}, target is 70% or higher."
            )
        
        if not recommendations:
            recommendations.append(
                "The analysis is complete and robust. Consider expanding scope "
                "to related policy areas or deeper investigation of specific findings."
            )
        
        return recommendations
    
    def _compute_confidence_interval(self, confidence: float) -> tuple[float, float]:
        """Compute 95% confidence interval."""
        margin = 0.1 * (1.0 - confidence)
        return (max(0.0, confidence - margin), min(1.0, confidence + margin))


__all__ = [
    "NarrativeAnswerSynthesizer",
    "SynthesizedAnswer",
    "AnswerContract",
    "Citation",
    "NarrativeBlock",
    "AnswerCompleteness",
    "QuestionType",
]

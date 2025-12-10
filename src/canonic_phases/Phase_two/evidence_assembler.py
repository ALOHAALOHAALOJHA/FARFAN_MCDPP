from __future__ import annotations

import re
import statistics
from dataclasses import dataclass, field
from typing import Any, Iterable, Literal

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


# ============================================================================
# QUESTION IDENTITY CONTRACT
# ============================================================================

@dataclass(frozen=True)
class QuestionIdentity:
    """Immutable identity tuple for a micro-question.
    
    This defines the TRIPLE IDENTITY that determines the scope of evidence:
    - question_id: Q001-Q300 (specific micro-question)
    - dimension_id: DIM01-DIM06 (analytical dimension)
    - policy_area_id: PA01-PA10 (policy domain)
    
    Evidence that doesn't match this identity is OUT OF SCOPE.
    """
    question_id: str
    dimension_id: str
    policy_area_id: str
    
    def __post_init__(self) -> None:
        """Validate identity components."""
        if not re.match(r'^Q\d{3}$', self.question_id):
            raise ValueError(f"Invalid question_id: {self.question_id}")
        if not re.match(r'^DIM\d{2}$', self.dimension_id):
            raise ValueError(f"Invalid dimension_id: {self.dimension_id}")
        if not re.match(r'^PA\d{2}$', self.policy_area_id):
            raise ValueError(f"Invalid policy_area_id: {self.policy_area_id}")
    
    def matches_scope(self, dim: str | None, pa: str | None) -> bool:
        """Check if given dimension/policy_area matches this identity's scope."""
        if dim and dim != self.dimension_id:
            return False
        if pa and pa != self.policy_area_id:
            return False
        return True


@dataclass
class ExpectedElement:
    """Expected element specification from questionnaire monolith.
    
    Defines what evidence types are expected for a micro-question.
    """
    type: str
    required: bool = False
    minimum: int = 0
    description: str = ""


@dataclass
class EvidenceClassification:
    """Classification result for assembled evidence.
    
    Maps raw evidence to expected element types with confidence scoring.
    """
    element_type: str
    value: Any
    confidence: float = 0.0
    source_method: str = ""
    matches_expected: bool = False
    pattern_id: str | None = None


@dataclass
class AssemblyResult:
    """Comprehensive result of evidence assembly.
    
    Includes:
    - Assembled evidence dict (for Phase 3)
    - Classification by expected element types
    - Completeness metrics
    - Trace for debugging
    """
    evidence: dict[str, Any]
    trace: dict[str, Any]
    identity: QuestionIdentity | None = None
    classifications: list[EvidenceClassification] = field(default_factory=list)
    completeness: float = 0.0
    missing_required: list[str] = field(default_factory=list)
    expected_elements_met: dict[str, bool] = field(default_factory=dict)
    out_of_scope_filtered: int = 0


def _resolve_value(source: str, method_outputs: dict[str, Any]) -> Any:
    """Resolve dotted source paths from method_outputs."""
    if not source:
        return None
    parts = source.split(".")
    current: Any = method_outputs
    for idx, part in enumerate(parts):
        if idx == 0 and part in method_outputs:
            current = method_outputs[part]
            continue
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


class EvidenceAssembler:
    """
    Assemble evidence fields from method outputs using deterministic merge strategies.
    """

    MERGE_STRATEGIES = {
        "concat",
        "first",
        "last",
        "mean",
        "max",
        "min",
        "weighted_mean",
        "majority",
    }

    @staticmethod
    def assemble(
        method_outputs: dict[str, Any],
        assembly_rules: list[dict[str, Any]],
        signal_pack: Any | None = None,  # NEW: Optional signal pack for provenance
    ) -> dict[str, Any]:
        evidence: dict[str, Any] = {}
        trace: dict[str, Any] = {}

        # NEW: Track signal pack provenance if provided
        if signal_pack is not None:
            trace["signal_provenance"] = {
                "signal_pack_id": getattr(signal_pack, "id", None) or getattr(signal_pack, "pack_id", "unknown"),
                "policy_area": getattr(signal_pack, "policy_area", None) or getattr(signal_pack, "policy_area_id", None),
                "version": getattr(signal_pack, "version", "unknown"),
                "patterns_available": len(getattr(signal_pack, "patterns", [])),
                "source_hash": getattr(signal_pack, "source_hash", None),
            }
            logger.info(
                "signal_pack_attached",
                signal_pack_id=trace["signal_provenance"]["signal_pack_id"],
                policy_area=trace["signal_provenance"]["policy_area"],
            )

        if "_signal_usage" in method_outputs:
            logger.info("signal_consumption_trace", signals_used=method_outputs["_signal_usage"])
            trace["signal_usage"] = method_outputs["_signal_usage"]
            # Remove from method_outputs to not interfere with evidence assembly
            del method_outputs["_signal_usage"]

        for rule in assembly_rules:
            target = rule.get("target")
            sources: Iterable[str] = rule.get("sources", [])
            strategy: str = rule.get("merge_strategy", "first")
            weights: list[float] | None = rule.get("weights")
            default = rule.get("default")

            if strategy not in EvidenceAssembler.MERGE_STRATEGIES:
                raise ValueError(f"Unsupported merge_strategy '{strategy}' for target '{target}'")

            values = []
            for src in sources:
                val = _resolve_value(src, method_outputs)
                if val is not None:
                    values.append(val)

            merged = EvidenceAssembler._merge(values, strategy, weights, default)
            evidence[target] = merged
            trace[target] = {"sources": list(sources), "strategy": strategy, "values": values}

        # PHASE 2→3 CONTRACT NORMALIZATION: Ensure canonical field names for Phase 3 consumption
        # Map contract-style names to Phase 3 expected names without breaking existing contracts
        evidence = EvidenceAssembler._normalize_for_phase3(evidence)

        return {"evidence": evidence, "trace": trace}

    @staticmethod
    def _normalize_for_phase3(evidence: dict[str, Any]) -> dict[str, Any]:
        """Normalize evidence fields to match Phase 3 ScoringEvidence contract.
        
        Phase 2 contracts produce:
          - elements_found, confidence_scores, pattern_matches, metadata
        
        Phase 3 expects:
          - elements (list)
          - raw_results: { confidence_scores, semantic_similarity, pattern_matches, metadata }
        
        This normalization ensures seamless Phase 2→3 handoff without modifying 300 contracts.
        """
        normalized = {}
        
        # Map elements_found → elements (canonical name for Phase 3)
        if "elements_found" in evidence:
            normalized["elements"] = evidence["elements_found"]
        elif "elements" in evidence:
            normalized["elements"] = evidence["elements"]
        else:
            normalized["elements"] = []
        
        # Build raw_results structure expected by Phase 3 ScoringEvidence
        raw_results: dict[str, Any] = {}
        
        # confidence_scores: keep at top level AND in raw_results for compatibility
        if "confidence_scores" in evidence:
            raw_results["confidence_scores"] = evidence["confidence_scores"]
            normalized["confidence_scores"] = evidence["confidence_scores"]
        else:
            raw_results["confidence_scores"] = []
            normalized["confidence_scores"] = []
        
        # pattern_matches: keep at top level AND in raw_results
        if "pattern_matches" in evidence:
            raw_results["pattern_matches"] = evidence["pattern_matches"]
            normalized["pattern_matches"] = evidence["pattern_matches"]
        else:
            raw_results["pattern_matches"] = {}
            normalized["pattern_matches"] = {}
        
        # semantic_similarity: Phase 3 optional field
        if "semantic_similarity" in evidence:
            raw_results["semantic_similarity"] = evidence["semantic_similarity"]
        else:
            raw_results["semantic_similarity"] = None
        
        # metadata: preserve all metadata
        if "metadata" in evidence:
            raw_results["metadata"] = evidence["metadata"]
            normalized["metadata"] = evidence["metadata"]
        else:
            raw_results["metadata"] = {}
            normalized["metadata"] = {}
        
        # Store raw_results for Phase 3 ScoringEvidence construction
        normalized["raw_results"] = raw_results
        
        # Preserve any additional fields from the original evidence
        for key, value in evidence.items():
            if key not in normalized:
                normalized[key] = value
        
        return normalized

    @staticmethod
    def _merge(values: list[Any], strategy: str, weights: list[float] | None, default: Any) -> Any:
        if not values:
            return default
        if strategy == "first":
            return values[0]
        if strategy == "last":
            return values[-1]
        if strategy == "concat":
            merged: list[Any] = []
            for v in values:
                if isinstance(v, list):
                    merged.extend(v)
                else:
                    merged.append(v)
            return merged
        numeric_values = [float(v) for v in values if EvidenceAssembler._is_number(v)]
        if strategy == "mean":
            return statistics.fmean(numeric_values) if numeric_values else default
        if strategy == "max":
            return max(numeric_values) if numeric_values else default
        if strategy == "min":
            return min(numeric_values) if numeric_values else default
        if strategy == "weighted_mean":
            if not numeric_values:
                return default
            if not weights:
                weights = [1.0] * len(numeric_values)
            w = weights[: len(numeric_values)] or [1.0] * len(numeric_values)
            total = sum(w) or 1.0
            return sum(v * w_i for v, w_i in zip(numeric_values, w)) / total
        if strategy == "majority":
            counts: dict[Any, int] = {}
            for v in values:
                counts[v] = counts.get(v, 0) + 1
            return max(counts.items(), key=lambda item: item[1])[0] if counts else default
        return default

    @staticmethod
    def _is_number(value: Any) -> bool:
        try:
            float(value)
            return not isinstance(value, bool)
        except (TypeError, ValueError) as e:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Non-numeric value: {value!r} ({type(value).__name__}): {e}")
            return False

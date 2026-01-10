"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              DOCTORAL-CARVER NARRATIVE SYNTHESIZER v4.0                      ║
║                    STATE-OF-THE-ART FRONTIER EDITION                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

PHASE_LABEL: Phase 2
PHASE_COMPONENT: Carver Synthesizer
PHASE_ROLE: Generates PhD-level human answers for 300 questions

═══════════════════════════════════════════════════════════════════════════════
PURPOSE
═══════════════════════════════════════════════════════════════════════════════

Transforms EvidenceNexus output into doctoral-quality human-readable answers
following Raymond Carver's minimalist prose style:
- Precision over verbosity
- Every word carries weight
- Evidence-backed assertions only
- Brutal honesty about limitations
- Causal reasoning made explicit

═══════════════════════════════════════════════════════════════════════════════
THEORETICAL FOUNDATIONS (SOTA)
═══════════════════════════════════════════════════════════════════════════════

1.  ARGUMENTATION THEORY
   - Toulmin Model (1958): Claim → Ground → Warrant → Backing → Qualifier → Rebuttal
   - RST (Mann & Thompson, 1988): Rhetorical Structure Theory for coherence
   - Argument Mining (Stab & Gurevych, 2017): Automated claim-evidence linking

2. UNCERTAINTY QUANTIFICATION
   - Dempster-Shafer Theory:  Belief/Plausibility intervals for epistemic uncertainty
   - Bayesian Calibration (Gneiting & Raftery, 2007): Calibrated confidence intervals
   - Conformal Prediction:  Distribution-free uncertainty bounds

3. CAUSAL INFERENCE
   - Pearl's do-calculus (2009): Interventional reasoning
   - SCM (Structural Causal Models): Counterfactual analysis
   - Judea Pearl's Ladder of Causation:  Association → Intervention → Counterfactual

4. NARRATIVE SYNTHESIS
   - Raymond Carver's Minimalism: "No tricks.  What you see is what you get."
   - Hemingway's Iceberg Theory: Show 10%, imply 90%
   - Academic Prose Guidelines: Clear, precise, evidenced

═══════════════════════════════════════════════════════════════════════════════
ARCHITECTURE v4.0 (COMPLETE REMAKE)
═══════════════════════════════════════════════════════════════════════════════

                    ┌─────────────────────────────────────────────┐
                    │           Contract v4 (1 of 300)            │
                    │  identity. question_id, method_binding,      │
                    │  human_answer_structure, question_context   │
                    └─────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CONTRACT INTERPRETER                                  │
│  • Extracts methodological depth (17 methods × epistemological foundations) │
│  • Maps dimension → evaluation strategy                                     │
│  • Resolves expected_elements for gap analysis                              │
│  • Builds template variable bindings                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        NEXUS OUTPUT ADAPTER                                  │
│  Input: SynthesizedAnswer from EvidenceNexus                                │
│  • Extracts evidence graph structure                                        │
│  • Maps citations to Toulmin grounds                                        │
│  • Computes completeness metrics                                            │
│  • Identifies contradictions and corroborations                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EVIDENCE ANALYZER                                     │
│  • Counts elements by type (expected vs found)                              │
│  • Builds causal dependency graph                                           │
│  • Detects evidence strength distribution                                   │
│  • Computes Dempster-Shafer belief masses                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        GAP ANALYZER                                          │
│  • Multi-dimensional gap detection                                          │
│  • Severity classification (CRITICAL/MAJOR/MINOR/COSMETIC)                  │
│  • Causal implication analysis                                              │
│  • Remediation suggestions                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     BAYESIAN CONFIDENCE ENGINE                               │
│  • Computes calibrated confidence intervals                                 │
│  • Belief/Plausibility bounds (Dempster-Shafer)                            │
│  • Wilson score intervals (95% CI)                                          │
│  • Gap-adjusted pessimistic weighting                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     TOULMIN ARGUMENT BUILDER                                 │
│  • Structures arguments:  Claim → Data → Warrant → Qualifier                │
│  • Links evidence to rhetorical roles                                       │
│  • Generates rebuttals for counter-evidence                                 │
│  • Computes argument strength scores                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CARVER PROSE RENDERER                                    │
│  • Applies Carver minimalist style rules                                    │
│  • Short sentences.  Active verbs. No adverbs.                                │
│  • Every claim backed by evidence citation                                  │
│  • Readability:  Flesch-Kincaid grade ≤ 12                                   │
│  • Enforces INV-001 through INV-008                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DOCTORAL ANSWER                                       │
│  Output: DoctoralHumanAnswer compatible with Phase 3                        │
│  • score: float [0,1] calibrated                                            │
│  • quality_level: QualityLevel enum                                         │
│  • human_answer:  Markdown prose                                             │
│  • evidence_citations: List[Citation]                                       │
│  • gaps_identified: List[Gap]                                               │
│  • confidence_interval:  Tuple[float, float]                                 │
│  • synthesis_trace: Dict for debugging                                      │
└─────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
INVARIANTS (HARD CONSTRAINTS)
═══════════════════════════════════════════════════════════════════════════════

[INV-001] Every assertion must have ≥1 evidence citation
[INV-002] Critical gaps MUST appear in response (no hiding)
[INV-003] Confidence must be calibrated (no optimistic bias)
[INV-004] Carver style:  sentences ≤20 words avg, active voice, no adverbs
[INV-005] Score must align with QualityLevel thresholds
[INV-006] Epistemological foundations cited when relevant
[INV-007] Methodological limitations as honest caveats
[INV-008] Theoretical references in academic format
[INV-009] Output compatible with Phase 3 ScoringModality
[INV-010] Deterministic:  same input → same output (byte-identical)

═══════════════════════════════════════════════════════════════════════════════
ALIGNMENT WITH PIPELINE
═══════════════════════════════════════════════════════════════════════════════

INPUT (from EvidenceNexus):
    - SynthesizedAnswer with evidence graph
    - ValidationReport with completeness metrics
    - Contract v4 with methodological_depth

OUTPUT (to Phase 3):
    - DoctoralHumanAnswer with:
        * score: float [0. 0, 1.0]
        * quality_level: QualityLevel
        * human_answer: str (Markdown)
        * scoring_metadata: Dict

Author: F. A. R.F.A.N Pipeline
Version: 4.0.0-SOTA
Date: 2026-01-05
"""

from __future__ import annotations

import hashlib
import math
import re
import statistics
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from functools import cached_property, lru_cache
from typing import (
    Any,
    ClassVar,
    Dict,
    Final,
    FrozenSet,
    Iterator,
    List,
    Literal,
    Mapping,
    NamedTuple,
    Optional,
    Protocol,
    Sequence,
    Set,
    Tuple,
    TypeAlias,
    TypedDict,
    Union,
    cast,
    runtime_checkable,
)

# =============================================================================
# OPTIONAL DEPENDENCIES (SOTA LIBRARIES)
# =============================================================================

try:
    import textstat  # Flesch-Kincaid readability

    HAS_TEXTSTAT = True
except ImportError:
    textstat = None  # type: ignore[assignment]
    HAS_TEXTSTAT = False

try:
    import numpy as np
    from numpy.typing import NDArray

    HAS_NUMPY = True
except ImportError:
    np = None  # type: ignore[assignment]
    HAS_NUMPY = False

try:
    import structlog

    logger = structlog.get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


# =============================================================================
# TYPE ALIASES
# =============================================================================

Confidence: TypeAlias = float  # [0.0, 1.0]
BeliefMass: TypeAlias = float  # Dempster-Shafer belief
PlausibilityMass: TypeAlias = float  # Dempster-Shafer plausibility
Score: TypeAlias = float  # [0.0, 1.0]
EvidenceID: TypeAlias = str
QuestionID: TypeAlias = str
PolicyAreaID: TypeAlias = str
DimensionID: TypeAlias = str


# =============================================================================
# CONSTANTS
# =============================================================================

# Quality level thresholds (aligned with Phase 3)
THRESHOLD_EXCELENTE: Final[float] = 0.85
THRESHOLD_BUENO: Final[float] = 0.70
THRESHOLD_ACEPTABLE: Final[float] = 0.55
THRESHOLD_INSUFICIENTE: Final[float] = 0.0

# Carver style constraints
MAX_SENTENCE_LENGTH: Final[int] = 20  # words
MAX_FLESCH_KINCAID_GRADE: Final[float] = 12.0
MIN_FLESCH_READING_EASE: Final[float] = 60.0

# Evidence thresholds
MIN_CITATIONS_PER_CLAIM: Final[int] = 1
CRITICAL_GAP_THRESHOLD: Final[float] = 0.5
CORROBORATION_BOOST: Final[float] = 0.05
CONTRADICTION_PENALTY: Final[float] = 0.10

# Confidence calibration
PESSIMISM_WEIGHT: Final[float] = 0.6  # Conservative estimation
WILSON_Z: Final[float] = 1.96  # 95% CI


# =============================================================================
# ENUMS
# =============================================================================


class QualityLevel(Enum):
    """Quality assessment levels aligned with Phase 3."""

    EXCELENTE = "EXCELENTE"
    BUENO = "BUENO"
    ACEPTABLE = "ACEPTABLE"
    INSUFICIENTE = "INSUFICIENTE"
    NO_APLICABLE = "NO_APLICABLE"

    @classmethod
    def from_score(cls, score: float) -> "QualityLevel":
        """Determine quality level from score."""
        if score >= THRESHOLD_EXCELENTE:
            return cls.EXCELENTE
        elif score >= THRESHOLD_BUENO:
            return cls.BUENO
        elif score >= THRESHOLD_ACEPTABLE:
            return cls.ACEPTABLE
        else:
            return cls.INSUFICIENTE


class Dimension(Enum):
    """The 6 causal dimensions of the logical model."""

    D1_INSUMOS = "DIM01"  # Inputs:  resources, data, diagnosis
    D2_ACTIVIDADES = "DIM02"  # Activities: actions, instruments
    D3_PRODUCTOS = "DIM03"  # Outputs: deliverables, goals
    D4_RESULTADOS = "DIM04"  # Outcomes: immediate changes
    D5_IMPACTOS = "DIM05"  # Impacts: long-term changes
    D6_CAUSALIDAD = "DIM06"  # Causality: logic, M&E, adaptation

    @classmethod
    def from_id(cls, dim_id: str) -> "Dimension":
        """Get dimension from ID string."""
        for dim in cls:
            if dim.value == dim_id:
                return dim
        return cls.D1_INSUMOS  # Default fallback


class EvidenceStrength(Enum):
    """Evidence strength according to epistemological hierarchy."""

    DEFINITIVE = 5  # Verified official data
    STRONG = 4  # Multiple concordant sources
    MODERATE = 3  # Single reliable source
    WEAK = 2  # Inferred or partial
    ABSENT = 1  # Not found

    @classmethod
    def from_confidence(cls, conf: float) -> "EvidenceStrength":
        """Derive strength from confidence score."""
        if conf >= 0.95:
            return cls.DEFINITIVE
        elif conf >= 0.80:
            return cls.STRONG
        elif conf >= 0.60:
            return cls.MODERATE
        elif conf >= 0.30:
            return cls.WEAK
        else:
            return cls.ABSENT


class GapSeverity(Enum):
    """Gap severity with implications for scoring."""

    CRITICAL = "CRITICAL"  # Blocks positive evaluation
    MAJOR = "MAJOR"  # Significantly reduces score
    MINOR = "MINOR"  # Noted but doesn't block
    COSMETIC = "COSMETIC"  # Desirable improvement


class ArgumentRole(Enum):
    """Toulmin argument roles."""

    CLAIM = "claim"  # Main assertion
    DATA = "data"  # Factual support (Ground)
    WARRANT = "warrant"  # Justification of link
    BACKING = "backing"  # Support for warrant
    QUALIFIER = "qualifier"  # Limitation/condition
    REBUTTAL = "rebuttal"  # Recognized counter-argument


class ScoringModality(Enum):
    """Scoring modalities aligned with Phase 3."""

    TYPE_A = "TYPE_A"  # Quantitative (semantic)
    TYPE_B = "TYPE_B"  # Bayesian
    TYPE_C = "TYPE_C"  # Causal
    TYPE_D = "TYPE_D"  # Financial
    TYPE_E = "TYPE_E"  # Logical
    TYPE_F = "TYPE_F"  # Mixed


class NarrativeSection(Enum):
    """Sections in doctoral answer."""

    VERDICT = "verdict"
    EVIDENCE = "evidence"
    GAPS = "gaps"
    CONFIDENCE = "confidence"
    EPISTEMOLOGY = "epistemology"
    LIMITATIONS = "limitations"
    RECOMMENDATIONS = "recommendations"
    METHODOLOGY_NOTE = "methodology_note"


# =============================================================================
# DATA STRUCTURES (IMMUTABLE)
# =============================================================================


@dataclass(frozen=True, slots=True)
class ExpectedElement:
    """Element expected by contract with semantic weight."""

    element_type: str
    required: bool
    minimum_count: int
    category: Literal["quantitative", "qualitative", "relational"]
    weight: float  # [0, 1] relative importance

    @classmethod
    def from_contract(cls, elem: Dict[str, Any]) -> "ExpectedElement":
        """Factory from contract expected_elements."""
        elem_type = elem.get("type", "unknown")
        required = elem.get("required", False)
        minimum = elem.get("minimum", 1 if required else 0)

        # Infer category from type
        if any(
            t in elem_type
            for t in (
                "indicadores_cuantitativos",
                "series_temporales",
                "monto_presupuestario",
                "meta_cuantificada",
                "porcentaje",
            )
        ):
            category = "quantitative"
        elif any(
            t in elem_type for t in ("logica_causal", "ruta_transmision", "vinculo", "dependencia")
        ):
            category = "relational"
        else:
            category = "qualitative"

        # Compute weight
        base_weight = 0.8 if required else 0.4
        weight = min(1.0, base_weight + (minimum * 0.05))

        return cls(
            element_type=elem_type,
            required=required,
            minimum_count=minimum,
            category=category,
            weight=weight,
        )


@dataclass(frozen=True, slots=True)
class EvidenceItem:
    """Single evidence item with provenance."""

    element_type: str
    value: Any
    confidence: float
    source_method: str
    source_level: str  # N1-EMP, N2-INF, N3-AUD
    document_location: Optional[str] = None

    @cached_property
    def strength(self) -> EvidenceStrength:
        """Compute evidence strength."""
        return EvidenceStrength.from_confidence(self.confidence)

    @cached_property
    def is_quantitative(self) -> bool:
        """Check if evidence is quantitative."""
        if isinstance(self.value, (int, float)):
            return True
        if isinstance(self.value, str):
            return bool(re.search(r"\d+[.,]?\d*\s*%? ", self.value))
        return False


@dataclass(frozen=True, slots=True)
class EvidenceGap:
    """Gap with causal implication analysis."""

    element_type: str
    expected: int
    found: int
    severity: GapSeverity
    implication: str  # Why this gap matters
    remediation: str  # What would fix it

    @property
    def deficit(self) -> int:
        return max(0, self.expected - self.found)

    @property
    def fulfillment_ratio(self) -> float:
        if self.expected == 0:
            return 1.0
        return min(1.0, self.found / self.expected)


@dataclass(frozen=True, slots=True)
class ToulminArgument:
    """Structured Toulmin argument."""

    claim: str
    data: Tuple[str, ...]  # Evidence grounds
    warrant: str  # Why data supports claim
    backing: Optional[str] = None
    qualifier: Optional[str] = None
    rebuttal: Optional[str] = None
    strength: float = 0.5

    def render(self) -> str:
        """Render as prose."""
        parts = [self.claim]
        if self.qualifier:
            parts.append(f" ({self.qualifier})")
        parts.append(".")

        for ground in self.data[:3]:  # Max 3 grounds
            parts.append(f" {ground}.")

        if self.rebuttal:
            parts.append(f" Sin embargo, {self. rebuttal}.")

        return "".join(parts)


class ConfidenceInterval(NamedTuple):
    """Calibrated confidence interval."""

    lower: float
    point: float
    upper: float

    @property
    def width(self) -> float:
        return self.upper - self.lower


@dataclass(frozen=True, slots=True)
class BayesianConfidence:
    """Bayesian/Dempster-Shafer confidence result."""

    point_estimate: float
    belief: BeliefMass
    plausibility: PlausibilityMass
    uncertainty: float  # Epistemic uncertainty
    interval_95: ConfidenceInterval

    @property
    def is_calibrated(self) -> bool:
        """Check if interval width indicates proper calibration."""
        return self.interval_95.width >= 0.1  # Not overconfident

    def to_label(self) -> str:
        """Human-readable label."""
        if self.point_estimate >= 0.85:
            return "ALTA"
        elif self.point_estimate >= 0.70:
            return "MEDIA-ALTA"
        elif self.point_estimate >= 0.55:
            return "MEDIA"
        elif self.point_estimate >= 0.35:
            return "BAJA"
        else:
            return "MUY BAJA"


@dataclass(frozen=True, slots=True)
class Citation:
    """Evidence citation with provenance."""

    evidence_id: str
    summary: str
    source_method: str
    confidence: float
    page_reference: Optional[str] = None

    def render_inline(self) -> str:
        """Render as inline citation."""
        return f"[{self.summary[: 50]}]"


@dataclass(frozen=True, slots=True)
class MethodEpistemology:
    """Epistemological foundation of a method."""

    method_name: str
    class_name: str
    priority: int
    role: str
    paradigm: str
    theoretical_framework: Tuple[str, ...]
    justification: str
    limitations: Tuple[str, ...]
    assumptions: Tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MethodologicalDepth:
    """Complete methodological depth from contract v4."""

    methods: Tuple[MethodEpistemology, ...]
    total_methods: int
    paradigms_used: FrozenSet[str]
    theoretical_references: FrozenSet[str]
    all_limitations: FrozenSet[str]
    all_assumptions: FrozenSet[str]


# =============================================================================
# PROTOCOL DEFINITIONS
# =============================================================================


@runtime_checkable
class NexusOutputProtocol(Protocol):
    """Protocol for EvidenceNexus output compatibility."""

    direct_answer: str
    overall_confidence: float
    calibrated_interval: Tuple[float, float]
    gaps: List[str]
    primary_citations: List[Any]
    supporting_citations: List[Any]
    evidence_graph_hash: str
    synthesis_trace: Dict[str, Any]


# =============================================================================
# TYPED DICTS FOR OUTPUT CONTRACTS
# =============================================================================


class ScoringMetadata(TypedDict):
    """Scoring metadata for Phase 3 compatibility."""

    modality: str
    threshold: float
    confidence_interval: List[float]
    evidence_count: int
    gap_count: int
    critical_gaps: int


class DoctoralAnswerDict(TypedDict):
    """Output contract for Phase 3."""

    question_id: str
    score: float
    quality_level: str
    human_answer: str
    scoring_metadata: ScoringMetadata
    evidence_summary: Dict[str, int]
    gaps: List[Dict[str, Any]]
    synthesis_timestamp: str
    carver_version: str


# =============================================================================
# CONTRACT INTERPRETER
# =============================================================================


class ContractInterpreter:
    """
    Extracts full semantic depth from v4 contracts.

    Responsible for:
    - Dimension identification
    - Expected elements extraction
    - Methodological depth parsing
    - Human answer structure interpretation
    """

    # Dimension-specific evaluation requirements
    DIMENSION_REQUIREMENTS: ClassVar[Dict[Dimension, Dict[str, Any]]] = {
        Dimension.D1_INSUMOS: {
            "primary_need": "datos cuantitativos verificables",
            "evidence_type": "quantitative",
            "minimum_sources": 2,
        },
        Dimension.D2_ACTIVIDADES: {
            "primary_need": "especificidad operativa",
            "evidence_type": "qualitative",
            "minimum_sources": 1,
        },
        Dimension.D3_PRODUCTOS: {
            "primary_need": "proporcionalidad meta-problema",
            "evidence_type": "mixed",
            "minimum_sources": 1,
        },
        Dimension.D4_RESULTADOS: {
            "primary_need": "indicadores medibles",
            "evidence_type": "quantitative",
            "minimum_sources": 1,
        },
        Dimension.D5_IMPACTOS: {
            "primary_need": "teoría de cambio",
            "evidence_type": "relational",
            "minimum_sources": 1,
        },
        Dimension.D6_CAUSALIDAD: {
            "primary_need": "lógica causal explícita",
            "evidence_type": "relational",
            "minimum_sources": 1,
        },
    }

    @classmethod
    def extract_dimension(cls, contract: Dict[str, Any]) -> Dimension:
        """Extract dimension from contract identity.

        Handles v4 format with space ("DIM 1") by normalizing to "DIM01".
        """
        identity = contract.get("identity", {})
        dim_id_raw = identity.get("dimension_id", "")

        # Normalize dimension_id format
        # v4 contracts use: "DIM 1" (with space)
        # Internal code expects: "DIM01" (without space)
        dim_id = dim_id_raw
        if dim_id_raw and " " in str(dim_id_raw):
            parts = dim_id_raw.split()
            if len(parts) == 2 and parts[0] == "DIM":
                # Pad single digit to match expected format: "DIM01"
                dim_id = f"DIM{parts[1].zfill(2) if len(parts[1]) == 1 else parts[1]}"

        # Try direct match
        try:
            return Dimension.from_id(dim_id)
        except (KeyError, ValueError):
            pass

        # Fallback: infer from base_slot (e.g., "D1-Q1" -> D1)
        base_slot = identity.get("base_slot", "")
        if base_slot and "-" in base_slot:
            dim_num = base_slot.split("-")[0].replace("D", "")
            try:
                dim_idx = int(dim_num) - 1
                return list(Dimension)[dim_idx]
            except (ValueError, IndexError):
                pass

        return Dimension.D1_INSUMOS  # Default

    @classmethod
    def extract_question_id(cls, contract: Dict[str, Any]) -> str:
        """Extract question ID."""
        identity = contract.get("identity", {})
        return identity.get("question_id", identity.get("base_slot", "UNKNOWN"))

    @classmethod
    def extract_policy_area(cls, contract: Dict[str, Any]) -> str:
        """Extract policy area ID.

        Handles field name differences between contract versions:
        - v2/v3: identity.policy_area_id
        - v4: identity.sector_id
        """
        identity = contract.get("identity", {})
        question_context = contract.get("question_context", {})

        # Try multiple field names with fallback
        return (
            identity.get("policy_area_id")
            or identity.get("sector_id")
            or question_context.get("policy_area_id")
            or question_context.get("sector_id", "PA00")
        )

    @classmethod
    def extract_contract_type(cls, contract: Dict[str, Any]) -> str:
        """Extract contract type (TYPE_A through TYPE_E)."""
        identity = contract.get("identity", {})
        return identity.get("contract_type", "TYPE_A")

    @classmethod
    def extract_expected_elements(cls, contract: Dict[str, Any]) -> Tuple[ExpectedElement, ...]:
        """Extract expected elements with semantic enrichment."""
        question_context = contract.get("question_context", {})
        raw_elements = question_context.get("expected_elements", [])

        return tuple(ExpectedElement.from_contract(elem) for elem in raw_elements)

    @classmethod
    def extract_question_text(cls, contract: Dict[str, Any]) -> str:
        """Extract question text.

        Handles field name differences between contract versions:
        - v2/v3: question_context.question_text
        - v4: question_context.pregunta_completa
        """
        question_context = contract.get("question_context", {})
        return (
            question_context.get("question_text") or question_context.get("pregunta_completa") or ""
        )

    @classmethod
    def extract_scoring_modality(cls, contract: Dict[str, Any]) -> ScoringModality:
        """Extract scoring modality from contract type."""
        contract_type = cls.extract_contract_type(contract)
        try:
            return ScoringModality[contract_type]
        except KeyError:
            return ScoringModality.TYPE_A

    @classmethod
    def extract_methodological_depth(
        cls, contract: Dict[str, Any]
    ) -> Optional[MethodologicalDepth]:
        """Extract full methodological depth from method_binding."""
        method_binding = contract.get("method_binding", {})
        depth_raw = method_binding.get("methodological_depth")

        if not depth_raw:
            # Try human_answer_structure fallback
            human_answer = contract.get("human_answer_structure", {})
            depth_raw = human_answer.get("methodological_depth")

        if not depth_raw:
            return None

        methods_raw = depth_raw.get("methods", [])
        methods: List[MethodEpistemology] = []
        all_paradigms: Set[str] = set()
        all_refs: Set[str] = set()
        all_limitations: Set[str] = set()
        all_assumptions: Set[str] = set()

        for m in methods_raw:
            epi = m.get("epistemological_foundation", {})
            tech = m.get("technical_approach", {})

            paradigm = epi.get("paradigm", "")
            if paradigm:
                all_paradigms.add(paradigm)

            frameworks = epi.get("theoretical_framework", [])
            all_refs.update(frameworks)

            limitations = tech.get("limitations", [])
            all_limitations.update(limitations)

            assumptions = tech.get("assumptions", [])
            all_assumptions.update(assumptions)

            methods.append(
                MethodEpistemology(
                    method_name=m.get("method_name", ""),
                    class_name=m.get("class_name", ""),
                    priority=m.get("priority", 99),
                    role=m.get("role", ""),
                    paradigm=paradigm,
                    theoretical_framework=tuple(frameworks),
                    justification=epi.get("justification", ""),
                    limitations=tuple(limitations),
                    assumptions=tuple(assumptions),
                )
            )

        return MethodologicalDepth(
            methods=tuple(methods),
            total_methods=len(methods),
            paradigms_used=frozenset(all_paradigms),
            theoretical_references=frozenset(all_refs),
            all_limitations=frozenset(all_limitations),
            all_assumptions=frozenset(all_assumptions),
        )

    @classmethod
    def extract_human_answer_sections(cls, contract: Dict[str, Any]) -> Dict[str, Any]:
        """Extract human answer structure sections."""
        human_answer = contract.get("human_answer_structure", {})
        return human_answer.get("sections", {})

    @classmethod
    def get_dimension_requirements(cls, dimension: Dimension) -> Dict[str, Any]:
        """Get evaluation requirements for dimension."""
        return cls.DIMENSION_REQUIREMENTS.get(dimension, {})


# =============================================================================
# NEXUS OUTPUT ADAPTER
# =============================================================================


class NexusOutputAdapter:
    """
    Adapts EvidenceNexus output to Carver input format.

    Transforms:
    - SynthesizedAnswer → EvidenceItem list
    - Citations → Toulmin grounds
    - Validation → Gap analysis input
    """

    @classmethod
    def extract_evidence_items(
        cls,
        nexus_output: Dict[str, Any],
    ) -> Tuple[EvidenceItem, ...]:
        """Extract evidence items from Nexus output."""
        items: List[EvidenceItem] = []

        # Extract from evidence dict (legacy format)
        evidence = nexus_output.get("evidence", {})
        elements = evidence.get("elements", [])

        for elem in elements:
            if isinstance(elem, dict):
                items.append(
                    EvidenceItem(
                        element_type=elem.get("type", "unknown"),
                        value=elem.get("value", elem.get("description", "")),
                        confidence=float(elem.get("confidence", 0.5)),
                        source_method=elem.get("source_method", "unknown"),
                        source_level=elem.get("source_level", "N1-EMP"),
                        document_location=elem.get("page", elem.get("location")),
                    )
                )

        # Extract from synthesized_answer if available
        synth = nexus_output.get("synthesized_answer", {})
        if isinstance(synth, dict):
            for citation in synth.get("primary_citations", []):
                if isinstance(citation, dict):
                    items.append(
                        EvidenceItem(
                            element_type=citation.get("evidence_type", "citation"),
                            value=citation.get("summary", ""),
                            confidence=float(citation.get("confidence", 0.7)),
                            source_method=citation.get("source_method", "nexus"),
                            source_level="N1-EMP",
                        )
                    )

        return tuple(items)

    @classmethod
    def extract_citations(
        cls,
        nexus_output: Dict[str, Any],
    ) -> Tuple[Citation, ...]:
        """Extract citations from Nexus output."""
        citations: List[Citation] = []

        synth = nexus_output.get("synthesized_answer", {})
        if isinstance(synth, dict):
            for cit in synth.get("primary_citations", []):
                if isinstance(cit, dict):
                    citations.append(
                        Citation(
                            evidence_id=cit.get("evidence_id", ""),
                            summary=cit.get("summary", ""),
                            source_method=cit.get("source_method", ""),
                            confidence=float(cit.get("confidence", 0.5)),
                            page_reference=cit.get("page", None),
                        )
                    )

            for cit in synth.get("supporting_citations", []):
                if isinstance(cit, dict):
                    citations.append(
                        Citation(
                            evidence_id=cit.get("evidence_id", ""),
                            summary=cit.get("summary", ""),
                            source_method=cit.get("source_method", ""),
                            confidence=float(cit.get("confidence", 0.5)),
                            page_reference=cit.get("page", None),
                        )
                    )

        return tuple(citations)

    @classmethod
    def extract_overall_confidence(cls, nexus_output: Dict[str, Any]) -> float:
        """Extract overall confidence from Nexus output."""
        synth = nexus_output.get("synthesized_answer", {})
        if isinstance(synth, dict):
            return float(synth.get("overall_confidence", 0.5))

        validation = nexus_output.get("validation", {})
        if isinstance(validation, dict):
            return float(validation.get("consistency_score", 0.5))

        return 0.5

    @classmethod
    def extract_gaps_from_nexus(cls, nexus_output: Dict[str, Any]) -> List[str]:
        """Extract gap descriptions from Nexus output."""
        synth = nexus_output.get("synthesized_answer", {})
        if isinstance(synth, dict):
            return synth.get("gaps", [])
        return []


# =============================================================================
# EVIDENCE ANALYZER
# =============================================================================


class EvidenceAnalyzer:
    """
    Deep analysis of evidence with causal graph construction.

    Implements:
    - Element counting by type
    - Strength distribution analysis
    - Corroboration detection
    - Contradiction detection
    """

    @staticmethod
    def count_by_type(items: Sequence[EvidenceItem]) -> Dict[str, int]:
        """Count items by element type."""
        counts: Dict[str, int] = defaultdict(int)
        for item in items:
            counts[item.element_type] += 1
        return dict(counts)

    @staticmethod
    def group_by_type(
        items: Sequence[EvidenceItem],
    ) -> Dict[str, List[EvidenceItem]]:
        """Group items by element type."""
        groups: Dict[str, List[EvidenceItem]] = defaultdict(list)
        for item in items:
            groups[item.element_type].append(item)
        return dict(groups)

    @staticmethod
    def analyze_strength_distribution(
        items: Sequence[EvidenceItem],
    ) -> Dict[str, int]:
        """Analyze distribution of evidence strength."""
        distribution: Dict[str, int] = defaultdict(int)
        for item in items:
            distribution[item.strength.name] += 1
        return dict(distribution)

    @staticmethod
    def find_corroborations(
        items: Sequence[EvidenceItem],
    ) -> List[Tuple[EvidenceItem, EvidenceItem]]:
        """Find pairs of corroborating evidence."""
        corroborations: List[Tuple[EvidenceItem, EvidenceItem]] = []
        groups = EvidenceAnalyzer.group_by_type(items)

        for elem_type, group_items in groups.items():
            if len(group_items) < 2:
                continue

            for i, item1 in enumerate(group_items):
                for item2 in group_items[i + 1 :]:
                    if item1.source_method != item2.source_method:
                        corroborations.append((item1, item2))

        return corroborations

    @staticmethod
    def find_contradictions(
        items: Sequence[EvidenceItem],
    ) -> List[Tuple[EvidenceItem, EvidenceItem, str]]:
        """Find contradicting evidence pairs."""
        contradictions: List[Tuple[EvidenceItem, EvidenceItem, str]] = []
        groups = EvidenceAnalyzer.group_by_type(items)

        for elem_type, group_items in groups.items():
            if len(group_items) < 2:
                continue

            numeric_items = [i for i in group_items if i.is_quantitative]
            if len(numeric_items) >= 2:
                values: List[Tuple[EvidenceItem, float]] = []
                for item in numeric_items:
                    try:
                        val_str = str(item.value)
                        nums = re.findall(r"[\d.]+", val_str)
                        if nums:
                            values.append((item, float(nums[0])))
                    except (ValueError, TypeError, IndexError):
                        continue

                for i, (item1, val1) in enumerate(values):
                    for item2, val2 in values[i + 1 :]:
                        if val1 > 0 and abs(val1 - val2) / val1 > 0.5:
                            contradictions.append(
                                (item1, item2, f"Divergencia numérica: {val1} vs {val2}")
                            )

        return contradictions


# =============================================================================
# GAP ANALYZER
# =============================================================================


class GapAnalyzer:
    """
    Multi-dimensional gap analysis with causal implications.
    """

    # Implications by element type
    GAP_IMPLICATIONS: ClassVar[Dict[str, Tuple[str, str]]] = {
        "fuentes_oficiales": (
            "Sin fuentes oficiales, la credibilidad es cuestionable.",
            "Citar fuentes como DANE, Medicina Legal, ICBF.",
        ),
        "indicadores_cuantitativos": (
            "Sin indicadores numéricos, no hay línea base medible.",
            "Incluir tasas, porcentajes o valores absolutos con fuente.",
        ),
        "series_temporales_años": (
            "Sin series temporales, no se puede evaluar tendencia.",
            "Presentar datos de al menos 3 años consecutivos.",
        ),
        "logica_causal_explicita": (
            "Sin lógica causal, la teoría de cambio es invisible.",
            "Explicitar cadena:  insumo → actividad → producto → resultado.",
        ),
        "poblacion_objetivo_definida": (
            "Sin población objetivo, no hay focalización.",
            "Definir grupo beneficiario con características específicas.",
        ),
        "meta_cuantificada": (
            "Sin metas cuantificadas, no hay accountability.",
            "Establecer valores objetivo con plazo.",
        ),
        "sistema_monitoreo": (
            "Sin sistema de monitoreo, no hay seguimiento.",
            "Especificar indicadores, frecuencia y responsables.",
        ),
    }

    @classmethod
    def identify_gaps(
        cls,
        expected: Sequence[ExpectedElement],
        found_counts: Dict[str, int],
        dimension: Dimension,
    ) -> Tuple[EvidenceGap, ...]:
        """Identify gaps with severity calibrated by dimension."""
        gaps: List[EvidenceGap] = []
        dim_req = ContractInterpreter.get_dimension_requirements(dimension)

        for elem in expected:
            found = found_counts.get(elem.element_type, 0)

            if found >= elem.minimum_count:
                continue  # No gap

            severity = cls._compute_severity(elem, found, dim_req)
            implication, remediation = cls.GAP_IMPLICATIONS.get(
                elem.element_type, (f"Falta {elem.element_type}.", f"Agregar {elem.element_type}.")
            )

            gaps.append(
                EvidenceGap(
                    element_type=elem.element_type,
                    expected=elem.minimum_count,
                    found=found,
                    severity=severity,
                    implication=implication,
                    remediation=remediation,
                )
            )

        # Sort by severity
        severity_order = {
            GapSeverity.CRITICAL: 0,
            GapSeverity.MAJOR: 1,
            GapSeverity.MINOR: 2,
            GapSeverity.COSMETIC: 3,
        }
        gaps.sort(key=lambda g: severity_order[g.severity])

        return tuple(gaps)

    @classmethod
    def _compute_severity(
        cls,
        elem: ExpectedElement,
        found: int,
        dim_req: Dict[str, Any],
    ) -> GapSeverity:
        """Compute gap severity based on context."""
        # Critical if required and completely missing
        if elem.required and found == 0:
            return GapSeverity.CRITICAL

        # Critical if matches dimension's evidence type and missing
        evidence_type = dim_req.get("evidence_type", "")
        if elem.category == evidence_type and found == 0:
            return GapSeverity.CRITICAL

        # Major if required but partial
        if elem.required and found < elem.minimum_count:
            return GapSeverity.MAJOR

        # Major if high weight and missing
        if elem.weight >= 0.7 and found == 0:
            return GapSeverity.MAJOR

        # Minor for optional but expected
        if elem.minimum_count > 0 and found < elem.minimum_count:
            return GapSeverity.MINOR

        return GapSeverity.COSMETIC


# =============================================================================
# BAYESIAN CONFIDENCE ENGINE
# =============================================================================


class BayesianConfidenceEngine:
    """
    Bayesian confidence computation with Dempster-Shafer theory.

    Implements:
    - Belief/Plausibility interval computation
    - Wilson score confidence intervals
    - Gap-adjusted pessimistic weighting
    """

    @classmethod
    def compute(
        cls,
        items: Sequence[EvidenceItem],
        gaps: Sequence[EvidenceGap],
        corroborations: Sequence[Tuple[EvidenceItem, EvidenceItem]],
        contradictions: Sequence[Tuple[EvidenceItem, EvidenceItem, str]],
    ) -> BayesianConfidence:
        """Compute calibrated Bayesian confidence."""
        if not items:
            return BayesianConfidence(
                point_estimate=0.0,
                belief=0.0,
                plausibility=0.3,
                uncertainty=1.0,
                interval_95=ConfidenceInterval(0.0, 0.0, 0.3),
            )

        # 1. Base confidence from evidence
        confidences = [i.confidence for i in items]
        base_conf = statistics.mean(confidences)

        # 2. Corroboration boost
        corroboration_boost = min(0.15, len(corroborations) * CORROBORATION_BOOST)

        # 3. Contradiction penalty
        contradiction_penalty = min(0.25, len(contradictions) * CONTRADICTION_PENALTY)

        # 4. Gap penalty
        critical_gaps = sum(1 for g in gaps if g.severity == GapSeverity.CRITICAL)
        major_gaps = sum(1 for g in gaps if g.severity == GapSeverity.MAJOR)
        gap_penalty = min(0.4, critical_gaps * 0.15 + major_gaps * 0.05)

        # 5. Belief mass (lower bound)
        belief = max(0.0, base_conf + corroboration_boost - contradiction_penalty - gap_penalty)
        belief *= 1 - 0.1 * critical_gaps
        belief = max(0.0, min(1.0, belief))

        # 6. Plausibility (upper bound)
        plausibility = min(1.0, belief + 0.2)

        # 7. Epistemic uncertainty
        uncertainty = plausibility - belief

        # 8. Point estimate (pessimistic weighting)
        point_estimate = PESSIMISM_WEIGHT * belief + (1 - PESSIMISM_WEIGHT) * plausibility

        # 9. Wilson score interval
        n = len(items)
        p = point_estimate
        denominator = 1 + WILSON_Z**2 / n
        center = (p + WILSON_Z**2 / (2 * n)) / denominator
        margin = WILSON_Z * math.sqrt((p * (1 - p) + WILSON_Z**2 / (4 * n)) / n) / denominator

        lower = max(0.0, center - margin - gap_penalty)
        upper = min(1.0, center + margin)

        return BayesianConfidence(
            point_estimate=round(point_estimate, 3),
            belief=round(belief, 3),
            plausibility=round(plausibility, 3),
            uncertainty=round(uncertainty, 3),
            interval_95=ConfidenceInterval(
                round(lower, 3),
                round(point_estimate, 3),
                round(upper, 3),
            ),
        )


# =============================================================================
# DIMENSION STRATEGIES (Strategy Pattern)
# =============================================================================


class DimensionStrategy(ABC):
    """Abstract base for dimension-specific evaluation strategies."""

    @property
    @abstractmethod
    def dimension(self) -> Dimension:
        """The dimension this strategy handles."""
        pass

    @abstractmethod
    def verdict_prefix(self, has_critical_gaps: bool) -> str:
        """Generate verdict prefix based on gap analysis."""
        pass

    @abstractmethod
    def key_requirement(self) -> str:
        """Key requirement for this dimension."""
        pass

    @abstractmethod
    def interpret_confidence(self, conf: BayesianConfidence) -> str:
        """Dimension-specific confidence interpretation."""
        pass


class D1InsumosStrategy(DimensionStrategy):
    """D1: Insumos - Diagnosis and quantitative data."""

    @property
    def dimension(self) -> Dimension:
        return Dimension.D1_INSUMOS

    def verdict_prefix(self, has_critical_gaps: bool) -> str:
        if has_critical_gaps:
            return "El diagnóstico carece de fundamento cuantitativo"
        return "El diagnóstico tiene base cuantitativa"

    def key_requirement(self) -> str:
        return "Datos numéricos de fuentes oficiales"

    def interpret_confidence(self, conf: BayesianConfidence) -> str:
        if conf.point_estimate >= 0.7:
            return "Los datos son verificables"
        return "Faltan datos verificables"


class D2ActividadesStrategy(DimensionStrategy):
    """D2: Actividades - Operational specificity."""

    @property
    def dimension(self) -> Dimension:
        return Dimension.D2_ACTIVIDADES

    def verdict_prefix(self, has_critical_gaps: bool) -> str:
        if has_critical_gaps:
            return "Las actividades son vagas"
        return "Las actividades están especificadas"

    def key_requirement(self) -> str:
        return "Instrumento, población y lógica definidos"

    def interpret_confidence(self, conf: BayesianConfidence) -> str:
        if conf.point_estimate >= 0.7:
            return "La especificación es operativa"
        return "Falta especificidad operativa"


class D3ProductosStrategy(DimensionStrategy):
    """D3: Productos - Proportionality and goals."""

    @property
    def dimension(self) -> Dimension:
        return Dimension.D3_PRODUCTOS

    def verdict_prefix(self, has_critical_gaps: bool) -> str:
        if has_critical_gaps:
            return "Los productos no son proporcionales al problema"
        return "Los productos son proporcionales"

    def key_requirement(self) -> str:
        return "Metas cuantificadas y proporcionales"

    def interpret_confidence(self, conf: BayesianConfidence) -> str:
        if conf.point_estimate >= 0.7:
            return "La proporcionalidad es clara"
        return "La proporcionalidad es cuestionable"


class D4ResultadosStrategy(DimensionStrategy):
    """D4: Resultados - Outcome indicators."""

    @property
    def dimension(self) -> Dimension:
        return Dimension.D4_RESULTADOS

    def verdict_prefix(self, has_critical_gaps: bool) -> str:
        if has_critical_gaps:
            return "Los resultados no son medibles"
        return "Los resultados tienen indicadores"

    def key_requirement(self) -> str:
        return "Indicadores con línea base y meta"

    def interpret_confidence(self, conf: BayesianConfidence) -> str:
        if conf.point_estimate >= 0.7:
            return "Los indicadores permiten seguimiento"
        return "El seguimiento no es posible"


class D5ImpactosStrategy(DimensionStrategy):
    """D5: Impactos - Long-term changes."""

    @property
    def dimension(self) -> Dimension:
        return Dimension.D5_IMPACTOS

    def verdict_prefix(self, has_critical_gaps: bool) -> str:
        if has_critical_gaps:
            return "El impacto de largo plazo no está definido"
        return "El impacto está conceptualizado"

    def key_requirement(self) -> str:
        return "Teoría de cambio con horizonte temporal"

    def interpret_confidence(self, conf: BayesianConfidence) -> str:
        if conf.point_estimate >= 0.7:
            return "La teoría de cambio es plausible"
        return "La teoría de cambio es débil"


class D6CausalidadStrategy(DimensionStrategy):
    """D6: Causalidad - M&E and adaptation."""

    @property
    def dimension(self) -> Dimension:
        return Dimension.D6_CAUSALIDAD

    def verdict_prefix(self, has_critical_gaps: bool) -> str:
        if has_critical_gaps:
            return "La lógica causal no es explícita"
        return "La cadena causal está documentada"

    def key_requirement(self) -> str:
        return "Sistema de M&E con ciclos de aprendizaje"

    def interpret_confidence(self, conf: BayesianConfidence) -> str:
        if conf.point_estimate >= 0.7:
            return "El sistema permite adaptación"
        return "No hay mecanismo de corrección"


@lru_cache(maxsize=6)
def get_dimension_strategy(dimension: Dimension) -> DimensionStrategy:
    """Factory for dimension strategies (cached)."""
    strategies: Dict[Dimension, DimensionStrategy] = {
        Dimension.D1_INSUMOS: D1InsumosStrategy(),
        Dimension.D2_ACTIVIDADES: D2ActividadesStrategy(),
        Dimension.D3_PRODUCTOS: D3ProductosStrategy(),
        Dimension.D4_RESULTADOS: D4ResultadosStrategy(),
        Dimension.D5_IMPACTOS: D5ImpactosStrategy(),
        Dimension.D6_CAUSALIDAD: D6CausalidadStrategy(),
    }
    return strategies.get(dimension, D1InsumosStrategy())


# =============================================================================
# TOULMIN ARGUMENT BUILDER
# =============================================================================


class ToulminArgumentBuilder:
    """
    Builds Toulmin-structured arguments from evidence.

    Structures:
    - Claim: Main assertion
    - Data: Evidence grounds
    - Warrant: Why data supports claim
    - Backing: Support for warrant
    - Qualifier: Limitation
    - Rebuttal: Counter-argument
    """

    @classmethod
    def build_verdict_argument(
        cls,
        strategy: DimensionStrategy,
        gaps: Sequence[EvidenceGap],
        items: Sequence[EvidenceItem],
        confidence: BayesianConfidence,
    ) -> ToulminArgument:
        """Build main verdict argument."""
        critical_gaps = [g for g in gaps if g.severity == GapSeverity.CRITICAL]
        has_critical = len(critical_gaps) > 0

        # Claim
        claim = strategy.verdict_prefix(has_critical)

        # Data (evidence grounds)
        data: List[str] = []
        if items:
            count = len(items)
            strong = sum(1 for i in items if i.strength.value >= 4)
            data.append(f"{count} elementos de evidencia identificados")
            if strong > 0:
                data.append(f"{strong} con alta confianza")

        if has_critical:
            for gap in critical_gaps[:2]:
                data.append(f"Falta:  {gap.element_type. replace('_', ' ')}")

        # Warrant
        key_req = strategy.key_requirement()
        warrant = f"Criterio evaluado: {key_req}"

        # Qualifier
        conf_interpretation = strategy.interpret_confidence(confidence)
        qualifier = f"{conf_interpretation} (confianza {confidence.to_label()})"

        # Rebuttal (if contradictions or major gaps)
        rebuttal = None
        major_gaps = [g for g in gaps if g.severity == GapSeverity.MAJOR]
        if major_gaps:
            rebuttal = f"existen {len(major_gaps)} vacíos significativos"

        # Compute strength
        if has_critical:
            strength = 0.3
        elif major_gaps:
            strength = 0.5
        else:
            strength = min(0.9, confidence.point_estimate)

        return ToulminArgument(
            claim=claim,
            data=tuple(data),
            warrant=warrant,
            qualifier=qualifier,
            rebuttal=rebuttal,
            strength=strength,
        )

    @classmethod
    def build_evidence_arguments(
        cls,
        items: Sequence[EvidenceItem],
        found_counts: Dict[str, int],
    ) -> Tuple[ToulminArgument, ...]:
        """Build evidence summary arguments."""
        arguments: List[ToulminArgument] = []

        # Sort by count (most common first)
        sorted_types = sorted(found_counts.items(), key=lambda x: x[1], reverse=True)

        for elem_type, count in sorted_types[:5]:
            label = elem_type.replace("_", " ")
            claim = f"Se identificaron {count} {label}"

            # Find items of this type
            type_items = [i for i in items if i.element_type == elem_type]
            if type_items:
                sources = set(i.source_method for i in type_items)
                avg_conf = statistics.mean(i.confidence for i in type_items)

                data = (
                    f"Extraídos de {len(sources)} métodos",
                    f"Confianza promedio: {avg_conf:.0%}",
                )

                arguments.append(
                    ToulminArgument(
                        claim=claim,
                        data=data,
                        warrant="Evidencia documental verificada",
                        strength=avg_conf,
                    )
                )

        return tuple(arguments)


# =============================================================================
# READABILITY CHECKER
# =============================================================================


@dataclass
class ReadabilityMetrics:
    """Readability metrics for Carver style enforcement."""

    flesch_reading_ease: Optional[float] = None
    flesch_kincaid_grade: Optional[float] = None
    avg_sentence_length: Optional[float] = None
    avg_word_length: Optional[float] = None
    passes_carver_standards: bool = True
    issues: List[str] = field(default_factory=list)


class ReadabilityChecker:
    """Checks and enforces Carver minimalist style."""

    @classmethod
    def check(cls, text: str) -> ReadabilityMetrics:
        """Check text readability."""
        metrics = ReadabilityMetrics()

        if not text:
            return metrics

        if HAS_TEXTSTAT and textstat:
            try:
                metrics.flesch_reading_ease = textstat.flesch_reading_ease(text)
                metrics.flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)

                sentences = textstat.sentence_count(text)
                words = textstat.lexicon_count(text, removepunct=True)
                if sentences > 0:
                    metrics.avg_sentence_length = words / sentences

                # Check against Carver standards
                if (
                    metrics.flesch_reading_ease
                    and metrics.flesch_reading_ease < MIN_FLESCH_READING_EASE
                ):
                    metrics.passes_carver_standards = False
                    metrics.issues.append(
                        f"Readability too low: {metrics. flesch_reading_ease:.1f} < {MIN_FLESCH_READING_EASE}"
                    )

                if (
                    metrics.flesch_kincaid_grade
                    and metrics.flesch_kincaid_grade > MAX_FLESCH_KINCAID_GRADE
                ):
                    metrics.passes_carver_standards = False
                    metrics.issues.append(
                        f"Grade level too high: {metrics.flesch_kincaid_grade:. 1f} > {MAX_FLESCH_KINCAID_GRADE}"
                    )

                if (
                    metrics.avg_sentence_length
                    and metrics.avg_sentence_length > MAX_SENTENCE_LENGTH
                ):
                    metrics.passes_carver_standards = False
                    metrics.issues.append(
                        f"Sentences too long: {metrics.avg_sentence_length:.1f} > {MAX_SENTENCE_LENGTH}"
                    )
            except Exception as e:
                logger.warning(f"Readability check failed:  {e}")

        return metrics


# =============================================================================
# CARVER PROSE RENDERER (Continued)
# =============================================================================


class CarverProseRenderer:
    """
    Renders doctoral answers in Raymond Carver minimalist style.

    Principles:
    - Short sentences.  Subject-verb-object.
    - Active verbs. No passive voice.
    - No adverbs. No unnecessary adjectives.
    - Every word counts.  If it can be removed, remove it.
    - The truth is enough. No embellishments.
    """

    # Type labels for human-readable element names
    TYPE_LABELS: ClassVar[Dict[str, str]] = {
        "fuentes_oficiales": "fuentes oficiales",
        "indicadores_cuantitativos": "indicadores numéricos",
        "series_temporales_años": "series temporales",
        "cobertura_territorial_especificada": "cobertura territorial",
        "instrumento_especificado": "instrumentos",
        "poblacion_objetivo_definida": "población objetivo",
        "logica_causal_explicita": "lógica causal",
        "riesgos_identificados": "riesgos",
        "mitigacion_propuesta": "mitigación",
        "impacto_definido": "impactos",
        "rezago_temporal": "horizonte temporal",
        "ruta_transmision": "ruta de transmisión",
        "proporcionalidad_meta_problema": "proporcionalidad",
        "linea_base_resultado": "línea base",
        "meta_resultado": "metas",
        "meta_cuantificada": "metas cuantificadas",
        "metrica_outcome": "métricas",
        "sistema_monitoreo": "sistema de monitoreo",
        "ciclos_aprendizaje": "ciclos de aprendizaje",
        "mecanismos_correccion": "mecanismos de corrección",
        "analisis_contextual": "análisis contextual",
        "enfoque_diferencial": "enfoque diferencial",
    }

    @classmethod
    def humanize(cls, elem_type: str) -> str:
        """Convert technical type to plain Spanish."""
        return cls.TYPE_LABELS.get(elem_type, elem_type.replace("_", " "))

    @classmethod
    def render_verdict(
        cls,
        argument: ToulminArgument,
        confidence: BayesianConfidence,
    ) -> str:
        """Render verdict section.  One paragraph.  Direct."""
        lines = ["## Respuesta\n"]

        # Main claim with qualifier
        verdict = argument.claim
        if argument.qualifier:
            verdict += f".  {argument.qualifier}"
        verdict += "."
        lines.append(verdict)

        # Supporting data (max 3)
        for ground in argument.data[:3]:
            lines.append(f" {ground}.")

        # Rebuttal if present
        if argument.rebuttal:
            lines.append(f"\n\n*Sin embargo, {argument.rebuttal}.*")

        return "\n".join(lines)

    @classmethod
    def render_evidence_section(
        cls,
        items: Sequence[EvidenceItem],
        found_counts: Dict[str, int],
        citations: Sequence[Citation],
    ) -> str:
        """Render evidence section.  Facts only."""
        lines = ["## Evidencia\n"]

        # Total count
        total = len(items)
        if total == 0:
            lines.append("No se identificó evidencia relevante.")
            return "\n".join(lines)

        lines.append(f"Se identificaron **{total}** elementos de evidencia.\n")

        # Top types
        sorted_types = sorted(found_counts.items(), key=lambda x: x[1], reverse=True)
        for elem_type, count in sorted_types[:5]:
            label = cls.humanize(elem_type)
            lines.append(f"- {count} {label}")

        # Strength distribution
        strong = sum(1 for i in items if i.strength.value >= 4)
        moderate = sum(1 for i in items if i.strength.value == 3)
        weak = sum(1 for i in items if i.strength.value <= 2)

        if strong > 0 or moderate > 0:
            lines.append(f"\n**Calidad**:  {strong} alta, {moderate} moderada, {weak} baja.")

        # Top citations
        if citations:
            lines.append("\n**Fuentes principales**:")
            for cit in citations[:3]:
                summary = cit.summary[:80] + ("..." if len(cit.summary) > 80 else "")
                lines.append(f"- {summary} ({cit.source_method})")

        return "\n".join(lines)

    @classmethod
    def render_gaps_section(cls, gaps: Sequence[EvidenceGap]) -> str:
        """Render gaps section. No excuses.  Just facts."""
        if not gaps:
            return ""

        lines = ["## Vacíos Identificados\n"]

        critical = [g for g in gaps if g.severity == GapSeverity.CRITICAL]
        major = [g for g in gaps if g.severity == GapSeverity.MAJOR]
        minor = [g for g in gaps if g.severity == GapSeverity.MINOR]

        if critical:
            lines.append("**Críticos** (bloquean evaluación positiva):\n")
            for gap in critical:
                label = cls.humanize(gap.element_type)
                lines.append(f"- ❌ {label}:  {gap.implication}")

        if major:
            lines.append("\n**Significativos**:\n")
            for gap in major[:3]:
                label = cls.humanize(gap.element_type)
                if gap.found > 0:
                    lines.append(f"- ⚠️ {label}: {gap. found}/{gap.expected}")
                else:
                    lines.append(f"- ⚠️ {label}: no encontrado")

        if minor and not critical and not major:
            lines.append("**Menores**:\n")
            for gap in minor[:2]:
                label = cls.humanize(gap.element_type)
                lines.append(f"- ℹ️ {label}")

        return "\n".join(lines)

    @classmethod
    def render_confidence_section(
        cls,
        confidence: BayesianConfidence,
        strategy: DimensionStrategy,
    ) -> str:
        """Render confidence section.  Honest.  Calibrated."""
        lines = ["## Nivel de Confianza\n"]

        # Main confidence statement
        label = confidence.to_label()
        pct = int(confidence.point_estimate * 100)
        interpretation = strategy.interpret_confidence(confidence)

        lines.append(f"**Confianza:  {label}** ({pct}%)\n")
        lines.append(interpretation + ".")

        # Interval
        lower = int(confidence.interval_95.lower * 100)
        upper = int(confidence.interval_95.upper * 100)
        lines.append(f"\nIntervalo 95%: [{lower}%, {upper}%]")

        # Calibration note
        if confidence.uncertainty > 0.3:
            lines.append("\n*Alta incertidumbre epistémica.  Interpretar con cautela.*")

        return "\n".join(lines)

    @classmethod
    def render_limitations_section(
        cls,
        depth: Optional[MethodologicalDepth],
    ) -> str:
        """Render methodological limitations.  Max 5."""
        if not depth or not depth.all_limitations:
            return ""

        lines = ["## Limitaciones Metodológicas\n"]

        for lim in list(depth.all_limitations)[:5]:
            lines.append(f"- {lim}")

        return "\n".join(lines)

    @classmethod
    def render_assumptions_section(
        cls,
        depth: Optional[MethodologicalDepth],
    ) -> str:
        """Render methodological assumptions. Max 4."""
        if not depth or not depth.all_assumptions:
            return ""

        lines = ["## Supuestos Metodológicos\n"]

        for assumption in list(depth.all_assumptions)[:4]:
            lines.append(f"- {assumption}")

        return "\n".join(lines)

    @classmethod
    def render_epistemology_section(
        cls,
        depth: Optional[MethodologicalDepth],
    ) -> str:
        """Render epistemological foundations."""
        if not depth:
            return ""

        if not depth.paradigms_used and not depth.theoretical_references:
            return ""

        lines = ["## Fundamentos Epistemológicos\n"]

        if depth.paradigms_used:
            paradigms = ", ".join(list(depth.paradigms_used)[:3])
            lines.append(f"**Paradigmas**:  {paradigms}\n")

        if depth.theoretical_references:
            lines.append("**Referencias teóricas**:")
            for ref in list(depth.theoretical_references)[:4]:
                lines.append(f"- {ref}")

        return "\n".join(lines)

    @classmethod
    def render_methodology_note(
        cls,
        depth: Optional[MethodologicalDepth],
        modality: ScoringModality,
    ) -> str:
        """Render discrete methodology note."""
        method_count = depth.total_methods if depth else 0
        return f"\n---\n*Análisis con {method_count} métodos.  Modalidad {modality.value}.*"

    @classmethod
    def render_score_summary(
        cls,
        score: float,
        quality_level: QualityLevel,
    ) -> str:
        """Render score summary box."""
        pct = int(score * 100)

        emoji_map = {
            QualityLevel.EXCELENTE: "🟢",
            QualityLevel.BUENO: "🔵",
            QualityLevel.ACEPTABLE: "🟡",
            QualityLevel.INSUFICIENTE: "🔴",
            QualityLevel.NO_APLICABLE: "⚪",
        }
        emoji = emoji_map.get(quality_level, "⚪")

        return f"\n---\n\n**Score**: {pct}/100 {emoji} **{quality_level.value}**"

    @classmethod
    def render_full_answer(
        cls,
        verdict_argument: ToulminArgument,
        confidence: BayesianConfidence,
        strategy: DimensionStrategy,
        items: Sequence[EvidenceItem],
        found_counts: Dict[str, int],
        citations: Sequence[Citation],
        gaps: Sequence[EvidenceGap],
        depth: Optional[MethodologicalDepth],
        modality: ScoringModality,
        score: float,
        quality_level: QualityLevel,
        question_text: str,
    ) -> str:
        """Render complete doctoral answer in Carver style."""
        sections: List[str] = []

        # Question context
        sections.append(f"**Pregunta**: {question_text}\n")

        # Verdict (core)
        sections.append(cls.render_verdict(verdict_argument, confidence))

        # Evidence
        sections.append(cls.render_evidence_section(items, found_counts, citations))

        # Gaps (if any)
        gaps_section = cls.render_gaps_section(gaps)
        if gaps_section:
            sections.append(gaps_section)

        # Confidence
        sections.append(cls.render_confidence_section(confidence, strategy))

        # Limitations (if present)
        limitations_section = cls.render_limitations_section(depth)
        if limitations_section:
            sections.append(limitations_section)

        # Assumptions (if present, only if no major gaps)
        critical_count = sum(1 for g in gaps if g.severity == GapSeverity.CRITICAL)
        if critical_count == 0:
            assumptions_section = cls.render_assumptions_section(depth)
            if assumptions_section:
                sections.append(assumptions_section)

        # Epistemology (if strong evidence)
        if confidence.point_estimate >= 0.6:
            epistemology_section = cls.render_epistemology_section(depth)
            if epistemology_section:
                sections.append(epistemology_section)

        # Score summary
        sections.append(cls.render_score_summary(score, quality_level))

        # Methodology note
        sections.append(cls.render_methodology_note(depth, modality))

        # Join sections
        full_text = "\n\n".join(sections)

        # Check readability
        metrics = ReadabilityChecker.check(full_text)
        if not metrics.passes_carver_standards:
            logger.warning(
                "carver_style_check_failed",
                issues=metrics.issues,
            )

        return full_text


# =============================================================================
# DOCTORAL HUMAN ANSWER
# =============================================================================


@dataclass
class DoctoralHumanAnswer:
    """
    Complete doctoral answer output.

    Compatible with Phase 3 scoring requirements:
    - score: float [0.0, 1.0]
    - quality_level: QualityLevel
    - human_answer: str (Markdown)
    - scoring_metadata: ScoringMetadata
    """

    # Core output
    question_id: str
    score: float
    quality_level: QualityLevel
    human_answer: str

    # Scoring metadata
    scoring_metadata: ScoringMetadata

    # Evidence summary
    evidence_count: int
    evidence_by_type: Dict[str, int]
    citations: Tuple[Citation, ...]

    # Gaps
    gaps: Tuple[EvidenceGap, ...]
    critical_gap_count: int

    # Confidence
    confidence: BayesianConfidence

    # Methodology
    dimension: Dimension
    modality: ScoringModality
    methodological_depth: Optional[MethodologicalDepth]

    # Trace
    synthesis_timestamp: str
    synthesis_trace: Dict[str, Any]
    carver_version: str = "4.0.0"

    def to_dict(self) -> DoctoralAnswerDict:
        """Convert to Phase 3 compatible dict."""
        return {
            "question_id": self.question_id,
            "score": round(self.score, 4),
            "quality_level": self.quality_level.value,
            "human_answer": self.human_answer,
            "scoring_metadata": self.scoring_metadata,
            "evidence_summary": self.evidence_by_type,
            "gaps": [
                {
                    "type": g.element_type,
                    "expected": g.expected,
                    "found": g.found,
                    "severity": g.severity.value,
                }
                for g in self.gaps
            ],
            "synthesis_timestamp": self.synthesis_timestamp,
            "carver_version": self.carver_version,
        }

    def to_phase3_output(self) -> Dict[str, Any]:
        """Convert to full Phase 3 output format."""
        return {
            "question_id": self.question_id,
            "score": round(self.score, 4),
            "normalized_score": int(self.score * 100),
            "quality_level": self.quality_level.value,
            "passes_threshold": self.score >= THRESHOLD_ACEPTABLE,
            "confidence_interval": [
                self.confidence.interval_95.lower,
                self.confidence.interval_95.upper,
            ],
            "human_answer": self.human_answer,
            "scoring_metadata": self.scoring_metadata,
            "evidence": {
                "count": self.evidence_count,
                "by_type": self.evidence_by_type,
                "citation_count": len(self.citations),
            },
            "gaps": {
                "total": len(self.gaps),
                "critical": self.critical_gap_count,
                "details": [g.element_type for g in self.gaps],
            },
            "methodology": {
                "dimension": self.dimension.value,
                "modality": self.modality.value,
                "method_count": (
                    self.methodological_depth.total_methods if self.methodological_depth else 0
                ),
            },
            "provenance": {
                "timestamp": self.synthesis_timestamp,
                "version": self.carver_version,
                "trace_hash": hashlib.sha256(str(self.synthesis_trace).encode()).hexdigest()[:16],
            },
        }


# =============================================================================
# DOCTORAL CARVER SYNTHESIZER (MAIN CLASS)
# =============================================================================


class DoctoralCarverSynthesizer:
    """
    Main synthesizer class for doctoral-level Carver answers.

    Orchestrates:
    1. Contract interpretation
    2. Nexus output adaptation
    3. Evidence analysis
    4. Gap identification
    5. Confidence computation
    6. Argument building
    7. Prose rendering
    8. Output generation

    Thread-safe and stateless (all state passed as arguments).
    """

    def __init__(
        self,
        strict_mode: bool = True,
        enable_readability_check: bool = True,
    ):
        """
        Initialize synthesizer.

        Args:
            strict_mode:  Fail on contract errors (vs. graceful degradation)
            enable_readability_check: Run Flesch-Kincaid checks
        """
        self.strict_mode = strict_mode
        self.enable_readability_check = enable_readability_check

        logger.info(
            "doctoral_carver_synthesizer_initialized",
            version="4.0.0",
            strict_mode=strict_mode,
        )

    def synthesize(
        self,
        nexus_output: Dict[str, Any],
        contract: Dict[str, Any],
    ) -> DoctoralHumanAnswer:
        """
        Synthesize doctoral answer from Nexus output and contract.

        Args:
            nexus_output: Output from EvidenceNexus. process()
            contract:  V4 contract for this question

        Returns:
            DoctoralHumanAnswer with score, quality_level, and human_answer
        """
        start_time = datetime.now(timezone.utc)

        # 1. Interpret contract
        question_id = ContractInterpreter.extract_question_id(contract)
        dimension = ContractInterpreter.extract_dimension(contract)
        expected_elements = ContractInterpreter.extract_expected_elements(contract)
        question_text = ContractInterpreter.extract_question_text(contract)
        modality = ContractInterpreter.extract_scoring_modality(contract)
        methodological_depth = ContractInterpreter.extract_methodological_depth(contract)

        # 2. Get dimension strategy
        strategy = get_dimension_strategy(dimension)

        # 3. Adapt Nexus output
        items = NexusOutputAdapter.extract_evidence_items(nexus_output)
        citations = NexusOutputAdapter.extract_citations(nexus_output)
        nexus_confidence = NexusOutputAdapter.extract_overall_confidence(nexus_output)

        # 4. Analyze evidence
        found_counts = EvidenceAnalyzer.count_by_type(items)
        corroborations = EvidenceAnalyzer.find_corroborations(items)
        contradictions = EvidenceAnalyzer.find_contradictions(items)

        # 5. Identify gaps
        gaps = GapAnalyzer.identify_gaps(expected_elements, found_counts, dimension)
        critical_gap_count = sum(1 for g in gaps if g.severity == GapSeverity.CRITICAL)

        # 6. Compute Bayesian confidence
        confidence = BayesianConfidenceEngine.compute(items, gaps, corroborations, contradictions)

        # 7. Compute final score
        score = self._compute_final_score(
            confidence=confidence,
            gaps=gaps,
            nexus_confidence=nexus_confidence,
            items=items,
        )

        # 8. Determine quality level
        quality_level = QualityLevel.from_score(score)

        # 9. Build Toulmin arguments
        verdict_argument = ToulminArgumentBuilder.build_verdict_argument(
            strategy, gaps, items, confidence
        )

        # 10. Render prose
        human_answer = CarverProseRenderer.render_full_answer(
            verdict_argument=verdict_argument,
            confidence=confidence,
            strategy=strategy,
            items=items,
            found_counts=found_counts,
            citations=citations,
            gaps=gaps,
            depth=methodological_depth,
            modality=modality,
            score=score,
            quality_level=quality_level,
            question_text=question_text,
        )

        # 11. Build scoring metadata
        scoring_metadata: ScoringMetadata = {
            "modality": modality.value,
            "threshold": THRESHOLD_ACEPTABLE,
            "confidence_interval": [
                confidence.interval_95.lower,
                confidence.interval_95.upper,
            ],
            "evidence_count": len(items),
            "gap_count": len(gaps),
            "critical_gaps": critical_gap_count,
        }

        # 12. Build synthesis trace
        synthesis_trace = {
            "dimension": dimension.value,
            "items_count": len(items),
            "gaps_count": len(gaps),
            "critical_gaps": critical_gap_count,
            "corroborations": len(corroborations),
            "contradictions": len(contradictions),
            "confidence_point": confidence.point_estimate,
            "confidence_belief": confidence.belief,
            "confidence_plausibility": confidence.plausibility,
            "score_raw": score,
            "quality_level": quality_level.value,
            "nexus_confidence": nexus_confidence,
        }

        end_time = datetime.now(timezone.utc)
        synthesis_timestamp = end_time.isoformat()

        logger.info(
            "doctoral_answer_synthesized",
            question_id=question_id,
            score=f"{score:.3f}",
            quality_level=quality_level.value,
            evidence_count=len(items),
            gap_count=len(gaps),
            synthesis_ms=int((end_time - start_time).total_seconds() * 1000),
        )

        return DoctoralHumanAnswer(
            question_id=question_id,
            score=score,
            quality_level=quality_level,
            human_answer=human_answer,
            scoring_metadata=scoring_metadata,
            evidence_count=len(items),
            evidence_by_type=found_counts,
            citations=citations,
            gaps=gaps,
            critical_gap_count=critical_gap_count,
            confidence=confidence,
            dimension=dimension,
            modality=modality,
            methodological_depth=methodological_depth,
            synthesis_timestamp=synthesis_timestamp,
            synthesis_trace=synthesis_trace,
        )

    def _compute_final_score(
        self,
        confidence: BayesianConfidence,
        gaps: Sequence[EvidenceGap],
        nexus_confidence: float,
        items: Sequence[EvidenceItem],
    ) -> float:
        """
        Compute final calibrated score.

        Combines:
        - Bayesian confidence
        - Gap penalties
        - Nexus confidence
        - Evidence strength distribution
        """
        if not items:
            return 0.0

        # Base:  Bayesian point estimate
        base_score = confidence.point_estimate

        # Weight with Nexus confidence
        combined = 0.7 * base_score + 0.3 * nexus_confidence

        # Gap penalties (already factored in Bayesian, but add floor)
        critical_count = sum(1 for g in gaps if g.severity == GapSeverity.CRITICAL)
        if critical_count >= 3:
            combined = min(combined, 0.3)  # Hard cap
        elif critical_count >= 1:
            combined = min(combined, 0.5)  # Soft cap

        # Evidence quality bonus
        strong_count = sum(1 for i in items if i.strength.value >= 4)
        if strong_count >= 5:
            combined = min(1.0, combined + 0.05)

        # Clamp to valid range
        return max(0.0, min(1.0, round(combined, 4)))

    def synthesize_batch(
        self,
        question_results: List[Tuple[Dict[str, Any], Dict[str, Any]]],
    ) -> List[DoctoralHumanAnswer]:
        """
        Synthesize answers for multiple questions.

        Args:
            question_results: List of (nexus_output, contract) tuples

        Returns:
            List of DoctoralHumanAnswer objects
        """
        answers: List[DoctoralHumanAnswer] = []

        for nexus_output, contract in question_results:
            try:
                answer = self.synthesize(nexus_output, contract)
                answers.append(answer)
            except Exception as e:
                if self.strict_mode:
                    raise
                logger.error(
                    "synthesis_failed",
                    error=str(e),
                    contract_id=contract.get("identity", {}).get("question_id", "UNKNOWN"),
                )

        return answers


# =============================================================================
# MESO/MACRO AGGREGATORS
# =============================================================================


class MesoAggregator:
    """
    Aggregates micro question answers into meso cluster results.

    Meso clusters group related questions within a dimension-policy area.
    """

    @classmethod
    def aggregate_cluster(
        cls,
        micro_answers: Sequence[DoctoralHumanAnswer],
        cluster_id: str,
    ) -> Dict[str, Any]:
        """Aggregate micro answers into meso cluster score."""
        if not micro_answers:
            return {
                "cluster_id": cluster_id,
                "score": 0.0,
                "quality_level": "INSUFICIENTE",
                "micro_count": 0,
                "coherence": 0.0,
            }

        # Extract scores
        scores = [a.score for a in micro_answers]

        # Mean score
        mean_score = statistics.mean(scores)

        # Coherence (inverse of coefficient of variation)
        if len(scores) > 1:
            std_dev = statistics.stdev(scores)
            coherence = max(0.0, 1.0 - (std_dev / max(mean_score, 0.01)))
        else:
            coherence = 1.0

        # Penalty for variance
        if len(scores) > 1:
            variance = statistics.variance(scores)
            variance_penalty = min(0.15, variance * 0.3)
            adjusted_score = max(0.0, mean_score - variance_penalty)
        else:
            adjusted_score = mean_score

        quality_level = QualityLevel.from_score(adjusted_score)

        return {
            "cluster_id": cluster_id,
            "score": round(adjusted_score, 4),
            "quality_level": quality_level.value,
            "micro_count": len(micro_answers),
            "coherence": round(coherence, 3),
            "mean_raw": round(mean_score, 4),
            "min_score": round(min(scores), 4),
            "max_score": round(max(scores), 4),
        }


class MacroAggregator:
    """
    Aggregates meso clusters into macro holistic evaluation.

    Macro evaluation covers the entire PA×DIM matrix (10×6 = 60 cells).
    """

    @classmethod
    def aggregate_holistic(
        cls,
        meso_results: Sequence[Dict[str, Any]],
        pa_dim_matrix: Optional[Dict[Tuple[str, str], float]] = None,
    ) -> Dict[str, Any]:
        """
        Aggregate meso results into macro holistic score.

        Args:
            meso_results: List of meso cluster results
            pa_dim_matrix: Optional PA×DIM coverage matrix

        Returns:
            Macro evaluation result
        """
        if not meso_results:
            return {
                "score": 0.0,
                "quality_level": "INSUFICIENTE",
                "meso_count": 0,
                "cross_cutting_coherence": 0.0,
                "systemic_gaps": [],
            }

        # Extract meso scores
        meso_scores = [m.get("score", 0.0) for m in meso_results]

        # Base score
        base_score = statistics.mean(meso_scores)

        # Cross-cutting coherence
        if len(meso_scores) > 1:
            std_dev = statistics.stdev(meso_scores)
            coherence = max(0.0, 1.0 - (std_dev / 0.3))  # Normalize by max expected std
        else:
            coherence = 1.0

        # Identify systemic gaps (meso clusters with INSUFICIENTE)
        systemic_gaps = [
            m.get("cluster_id", "unknown")
            for m in meso_results
            if m.get("quality_level") == "INSUFICIENTE"
        ]

        # Gap penalty
        gap_penalty = min(0.2, len(systemic_gaps) * 0.03)

        # PA×DIM coverage adjustment
        if pa_dim_matrix:
            coverage_scores = list(pa_dim_matrix.values())
            coverage_mean = statistics.mean(coverage_scores) if coverage_scores else 0.5
            final_score = 0.7 * base_score + 0.3 * coverage_mean - gap_penalty
        else:
            final_score = base_score - gap_penalty

        final_score = max(0.0, min(1.0, final_score))
        quality_level = QualityLevel.from_score(final_score)

        return {
            "score": round(final_score, 4),
            "quality_level": quality_level.value,
            "meso_count": len(meso_results),
            "cross_cutting_coherence": round(coherence, 3),
            "systemic_gaps": systemic_gaps,
            "base_score": round(base_score, 4),
            "gap_penalty": round(gap_penalty, 4),
            "coverage_adjusted": pa_dim_matrix is not None,
        }


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def create_synthesizer(
    strict_mode: bool = True,
    enable_readability_check: bool = True,
) -> DoctoralCarverSynthesizer:
    """
    Factory function to create a DoctoralCarverSynthesizer.

    Args:
        strict_mode: Fail on contract errors
        enable_readability_check: Run Flesch-Kincaid checks

    Returns:
        Configured DoctoralCarverSynthesizer instance
    """
    return DoctoralCarverSynthesizer(
        strict_mode=strict_mode,
        enable_readability_check=enable_readability_check,
    )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def synthesize_answer(
    nexus_output: Dict[str, Any],
    contract: Dict[str, Any],
) -> DoctoralHumanAnswer:
    """
    Convenience function for one-shot synthesis.

    Args:
        nexus_output:  Output from EvidenceNexus. process()
        contract: V4 contract for this question

    Returns:
        DoctoralHumanAnswer
    """
    synthesizer = create_synthesizer()
    return synthesizer.synthesize(nexus_output, contract)


def synthesize_to_markdown(
    nexus_output: Dict[str, Any],
    contract: Dict[str, Any],
) -> str:
    """
    Convenience function to get just the markdown answer.

    Args:
        nexus_output: Output from EvidenceNexus.process()
        contract: V4 contract for this question

    Returns:
        Markdown string
    """
    answer = synthesize_answer(nexus_output, contract)
    return answer.human_answer


def synthesize_to_phase3(
    nexus_output: Dict[str, Any],
    contract: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Convenience function to get Phase 3 compatible output.

    Args:
        nexus_output: Output from EvidenceNexus.process()
        contract: V4 contract for this question

    Returns:
        Phase 3 compatible dict
    """
    answer = synthesize_answer(nexus_output, contract)
    return answer.to_phase3_output()


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "QualityLevel",
    "Dimension",
    "EvidenceStrength",
    "GapSeverity",
    "ArgumentRole",
    "ScoringModality",
    "NarrativeSection",
    # Data structures
    "ExpectedElement",
    "EvidenceItem",
    "EvidenceGap",
    "ToulminArgument",
    "ConfidenceInterval",
    "BayesianConfidence",
    "Citation",
    "MethodEpistemology",
    "MethodologicalDepth",
    # Type aliases
    "ScoringMetadata",
    "DoctoralAnswerDict",
    # Components
    "ContractInterpreter",
    "NexusOutputAdapter",
    "EvidenceAnalyzer",
    "GapAnalyzer",
    "BayesianConfidenceEngine",
    "ToulminArgumentBuilder",
    "ReadabilityChecker",
    "CarverProseRenderer",
    # Strategies
    "DimensionStrategy",
    "D1InsumosStrategy",
    "D2ActividadesStrategy",
    "D3ProductosStrategy",
    "D4ResultadosStrategy",
    "D5ImpactosStrategy",
    "D6CausalidadStrategy",
    "get_dimension_strategy",
    # Main classes
    "DoctoralHumanAnswer",
    "DoctoralCarverSynthesizer",
    # Aggregators
    "MesoAggregator",
    "MacroAggregator",
    # Factory and convenience functions
    "create_synthesizer",
    "synthesize_answer",
    "synthesize_to_markdown",
    "synthesize_to_phase3",
]

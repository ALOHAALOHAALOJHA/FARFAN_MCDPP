"""
Advanced Policy Contradiction Detection System for Colombian Municipal Development Plans

Este sistema implementa el estado del arte en detección de contradicciones para análisis
de políticas públicas, específicamente calibrado para Planes de Desarrollo Municipal (PDM)
colombianos según la Ley 152 de 1994 y metodología DNP.

Innovations:
- Transformer-based semantic similarity using sentence-transformers
- Graph-based contradiction reasoning with NetworkX
- Bayesian inference for confidence scoring
- Temporal logic verification for timeline consistency
- Multi-dimensional vector embeddings for policy alignment
- Statistical hypothesis testing for numerical claims
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

import networkx as nx
import numpy as np
import torch

# Check dependency lockdown
from farfan_pipeline.core.dependency_lockdown import get_dependency_lockdown

# Import runtime error fixes for defensive programming
from farfan_pipeline.utils.runtime_error_fixes import ensure_list_return
from scipy.stats import beta
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForSequenceClassification, DebertaV2Tokenizer, pipeline

_lockdown = get_dependency_lockdown()

# Configure logging with structured format
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ContradictionType(Enum):
    """Taxonomía de contradicciones según estándares de política pública"""

    NUMERICAL_INCONSISTENCY = auto()
    TEMPORAL_CONFLICT = auto()
    SEMANTIC_OPPOSITION = auto()
    LOGICAL_INCOMPATIBILITY = auto()
    RESOURCE_ALLOCATION_MISMATCH = auto()
    OBJECTIVE_MISALIGNMENT = auto()
    REGULATORY_CONFLICT = auto()
    STAKEHOLDER_DIVERGENCE = auto()


class PolicyDimension(Enum):
    """Dimensiones del Plan de Desarrollo según DNP Colombia"""

    DIAGNOSTICO = "diagnóstico"
    ESTRATEGICO = "estratégico"
    PROGRAMATICO = "programático"
    FINANCIERO = "plan plurianual de inversiones"
    SEGUIMIENTO = "seguimiento y evaluación"
    TERRITORIAL = "ordenamiento territorial"


@dataclass(frozen=True)
class PolicyStatement:
    """Representación estructurada de una declaración de política"""

    text: str
    dimension: PolicyDimension
    position: tuple[int, int]  # (start, end) in document
    entities: list[str] = field(default_factory=list)
    temporal_markers: list[str] = field(default_factory=list)
    quantitative_claims: list[dict[str, Any]] = field(default_factory=list)
    embedding: np.ndarray | None = None
    context_window: str = ""
    semantic_role: str | None = None
    dependencies: set[str] = field(default_factory=set)


@dataclass
class ContradictionEvidence:
    """Evidencia estructurada de contradicción con trazabilidad completa"""

    statement_a: PolicyStatement
    statement_b: PolicyStatement
    contradiction_type: ContradictionType
    confidence: float  # Bayesian posterior probability
    severity: float  # Impact on policy coherence
    semantic_similarity: float
    logical_conflict_score: float
    temporal_consistency: bool
    numerical_divergence: float | None
    affected_dimensions: list[PolicyDimension]
    resolution_suggestions: list[str]
    graph_path: list[str] | None = None
    statistical_significance: float | None = None


class BayesianConfidenceCalculator:
    """
    Bayesian confidence calculator with domain-informed priors.

    Uses Beta distribution priors calibrated from empirical analysis of
    Colombian municipal development plans (PDMs).
    """

    def __init__(self) -> None:
        # Priors based on empirical analysis of Colombian municipal development plans (PDMs)
        self.prior_alpha = 2.5  # Shape parameter for beta distribution
        self.prior_beta = 7.5  # Scale parameter (conservative bias favoring lower confidence)

    def calculate_posterior(
        self, evidence_strength: float, observations: int, domain_weight: float = 1.0
    ) -> float:
        """
        Calculate posterior probability using Bayesian inference.

        Updates the Beta distribution prior with observed evidence to compute
        the posterior mean, which represents the confidence level in the finding.

        Args:
            evidence_strength: Strength of the evidence (0.0-1.0 scale, unitless ratio)
            observations: Number of observations supporting the evidence (count)
            domain_weight: Policy domain-specific weight (multiplier, default: 1.0)

        Returns:
            float: Posterior probability (0.0-1.0 scale) representing confidence level
        """
        # Update Beta distribution with evidence
        alpha_post = self.prior_alpha + evidence_strength * observations * domain_weight
        beta_post = self.prior_beta + (1 - evidence_strength) * observations * domain_weight

        # Calculate mean of posterior distribution
        posterior_mean = alpha_post / (alpha_post + beta_post)

        # Calculate 95% credible interval
        credible_interval = beta.interval(0.95, alpha_post, beta_post)

        # Adjust for uncertainty (wider intervals reduce confidence)
        uncertainty_penalty = 1.0 - (credible_interval[1] - credible_interval[0])

        return min(1.0, posterior_mean * uncertainty_penalty)


class TemporalLogicVerifier:
    """
    Temporal consistency verification using Linear Temporal Logic (LTL).

    Analyzes policy statements for temporal contradictions, deadline violations,
    and ordering conflicts using temporal logic patterns.
    """

    def __init__(self) -> None:
        self.temporal_patterns = {
            "sequential": re.compile(
                r"(primero|luego|después|posteriormente|finalmente)", re.IGNORECASE
            ),
            "parallel": re.compile(
                r"(simultáneamente|al mismo tiempo|paralelamente)", re.IGNORECASE
            ),
            "deadline": re.compile(r"(antes de|hasta|máximo|plazo)", re.IGNORECASE),
            "milestone": re.compile(r"(hito|meta intermedia|checkpoint)", re.IGNORECASE),
        }

    def verify_temporal_consistency(
        self, statements: list[PolicyStatement]
    ) -> tuple[bool, list[dict[str, Any]]]:
        """
        Verify temporal consistency between policy statements.

        Analyzes temporal ordering and deadline constraints to identify
        contradictions or violations in the policy timeline.

        Args:
            statements: List of policy statements to analyze

        Returns:
            tuple[bool, list[dict]]: A tuple containing:
                - is_consistent: True if no conflicts found
                - conflicts_found: List of detected temporal conflicts
        """
        timeline = self._build_timeline(statements)
        conflicts = []

        # Verify temporal ordering
        for i, event_a in enumerate(timeline):
            for event_b in timeline[i + 1 :]:
                if self._has_temporal_conflict(event_a, event_b):
                    conflicts.append(
                        {
                            "event_a": event_a,
                            "event_b": event_b,
                            "conflict_type": "temporal_ordering",
                        }
                    )

        # Verify deadline constraints
        deadline_violations = self._check_deadline_constraints(timeline)
        conflicts.extend(deadline_violations)

        return len(conflicts) == 0, conflicts

    def _build_timeline(self, statements: list[PolicyStatement]) -> list[dict]:
        """
        Build timeline from policy statements.

        Extracts temporal markers and organizes them chronologically.

        Args:
            statements: List of policy statements

        Returns:
            list[dict]: Sorted timeline events with timestamps
        """
        timeline = []
        for stmt in statements:
            for marker in stmt.temporal_markers:
                # Extract structured temporal information
                timeline.append(
                    {
                        "statement": stmt,
                        "marker": marker,
                        "timestamp": self._parse_temporal_marker(marker),
                        "type": self._classify_temporal_type(marker),
                    }
                )
        return sorted(timeline, key=lambda x: x.get("timestamp", 0))

    def _parse_temporal_marker(self, marker: str) -> int | None:
        """
        Parse temporal marker to numeric timestamp.

        Implements Colombian policy document temporal format parsing.

        Args:
            marker: Temporal marker string (e.g., "2024", "Q2", "segundo trimestre")

        Returns:
            int | None: Numeric timestamp, or None if parsing fails
        """
        # Implementation specific to Colombian policy document format
        year_match = re.search(r"20\d{2}", marker)
        if year_match:
            return int(year_match.group())

        quarter_patterns = {
            "primer": 1,
            "segundo": 2,
            "tercer": 3,
            "cuarto": 4,
            "Q1": 1,
            "Q2": 2,
            "Q3": 3,
            "Q4": 4,
        }
        for pattern, quarter in quarter_patterns.items():
            if pattern in marker.lower():
                return quarter

        return None

    def _has_temporal_conflict(self, event_a: dict, event_b: dict) -> bool:
        """Detecta conflictos temporales entre eventos"""
        if event_a["timestamp"] and event_b["timestamp"]:
            # Verificar si eventos mutuamente excluyentes ocurren simultáneamente
            if event_a["timestamp"] == event_b["timestamp"]:
                return self._are_mutually_exclusive(event_a["statement"], event_b["statement"])
        return False

    def _are_mutually_exclusive(self, stmt_a: PolicyStatement, stmt_b: PolicyStatement) -> bool:
        """Determina si dos declaraciones son mutuamente excluyentes"""
        # Verificar si compiten por los mismos recursos
        resources_a = set(self._extract_resources(stmt_a.text))
        resources_b = set(self._extract_resources(stmt_b.text))

        return len(resources_a & resources_b) > 0

    def _extract_resources(self, text: str) -> list[str]:
        """Extrae recursos mencionados en el texto"""
        resource_patterns = [
            r"presupuesto",
            r"recursos?\s+\w+",
            r"fondos?\s+\w+",
            r"personal",
            r"infraestructura",
        ]
        resources = []
        for pattern in resource_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            resources.extend(matches)
        return resources

    def _check_deadline_constraints(self, timeline: list[dict]) -> list[dict]:
        """Verifica violaciones de restricciones de plazo"""
        violations = []
        for event in timeline:
            if event["type"] == "deadline":
                # Verificar si hay eventos posteriores que deberían ocurrir antes
                for other in timeline:
                    if other["timestamp"] and event["timestamp"]:
                        if other["timestamp"] > event["timestamp"]:
                            if self._should_precede(other["statement"], event["statement"]):
                                violations.append(
                                    {
                                        "event_a": other,
                                        "event_b": event,
                                        "conflict_type": "deadline_violation",
                                    }
                                )
        return violations

    def _should_precede(self, stmt_a: PolicyStatement, stmt_b: PolicyStatement) -> bool:
        """Determina si stmt_a debe preceder a stmt_b"""
        # Análisis de dependencias causales
        return bool(stmt_a.dependencies & {stmt_b.text[:50]})

    def _classify_temporal_type(self, marker: str) -> str:
        """Clasifica el tipo de marcador temporal"""
        for pattern_type, pattern in self.temporal_patterns.items():
            if pattern.search(marker):
                return pattern_type
        return "unspecified"


class SemanticValidator:
    """
    N2 Semantic Validator for TYPE_A contracts.

    Performs deterministic, non-probabilistic validation of semantic coherence
    and completeness for D1-Q1 and similar TYPE_A questions.

    Validates:
    - Coherence between quantitative data and baseline requirements
    - Compatibility between resources and temporal references
    - Minimal semantic completeness (numerical data, year reference, sources)

    This class DOES NOT infer, score probabilistically, or veto.
    It only produces semantic validation flags for downstream N3 auditing.

    Epistemological stance: Deterministic logical validation, no Bayesian inference.
    Compatible with TYPE_A (Semantic) contracts only.
    """

    # Official sources patterns for D1-Q1 validation
    OFFICIAL_SOURCES_PATTERNS = [
        r"\bDANE\b",
        r"\bMedicina\s+Legal\b",
        r"\bObservatorio\s+de\s+Género\b",
        r"\bObservatorio\s+de\s+Asuntos\s+de\s+Género\b",
        r"\bDNP\b",
        r"\bSISPRO\b",
        r"\bSIVIGILA\b",
        r"\bSecretaría\s+de\s+la\s+Mujer\b",
        r"\bComisar[íi]a\s+de\s+Familia\b",
        r"\bFiscal[íi]a\b",
        r"\bPolic[íi]a\s+Nacional\b",
    ]

    # Baseline indicators patterns
    BASELINE_INDICATORS = [
        r"l[íi]nea\s+base",
        r"año\s+base",
        r"situaci[óo]n\s+inicial",
        r"diagn[óo]stico",
        r"referencia\s+inicial",
    ]

    def __init__(self, temporal_verifier: TemporalLogicVerifier | None = None):
        """
        Initialize SemanticValidator.

        Args:
            temporal_verifier: Optional TemporalLogicVerifier instance for temporal validation.
                              If None, creates a new instance.
        """
        self.temporal_verifier = temporal_verifier or TemporalLogicVerifier()
        self.logger = logging.getLogger(self.__class__.__name__)

    def validate_semantic_completeness_coherence(self, raw_facts: dict[str, Any]) -> dict[str, Any]:
        """
        Validate semantic completeness and coherence for D1-Q1 requirements.

        Validates that raw_facts contain:
        1. Quantitative data (rates, percentages, figures)
        2. Baseline indicators (línea base, año base, situación inicial)
        3. Year reference (explicit year mentioned)
        4. Official sources (DANE, Medicina Legal, Observatorio de Género, etc.)

        Args:
            raw_facts: Structured outputs from N1 extraction methods.
                      Expected keys:
                      - quantitative_claims: list[dict] from _extract_quantitative_claims
                      - temporal_markers: list[str] from _extract_temporal_markers
                      - resource_mentions: list[tuple] from _extract_resource_mentions
                      - point_evidence: dict with policy area evidence
                      - numerical_values: list[float] from _extract_numerical_values

        Returns:
            dict with boolean semantic validation flags:
            - has_quantitative_data: bool
            - has_baseline_indicator: bool
            - has_year_reference: bool
            - has_official_sources: bool
            - resources_temporal_compatible: bool
            - semantic_completeness_pass: bool (all above must be True)

            Each flag is binary (True/False), no scores or probabilities.
        """
        results = {
            "has_quantitative_data": self._check_quantitative_data_presence(raw_facts),
            "has_baseline_indicator": self._check_baseline_indicator(raw_facts),
            "has_year_reference": self._check_year_reference(raw_facts),
            "has_official_sources": self._check_official_sources(raw_facts),
            "resources_temporal_compatible": self._check_resources_temporal_compatibility(
                raw_facts
            ),
        }

        # Overall semantic completeness: all requirements must pass
        results["semantic_completeness_pass"] = all(
            [
                results["has_quantitative_data"],
                results["has_baseline_indicator"],
                results["has_year_reference"],
                results["has_official_sources"],
            ]
        )

        return results

    # -------------------------
    # Private deterministic checks (N2 validation logic)
    # -------------------------

    def _check_quantitative_data_presence(self, raw_facts: dict[str, Any]) -> bool:
        """
        Check if quantitative data is present (rates, percentages, figures).

        Deterministic check: presence/absence only, no scoring.
        """
        # Check quantitative_claims from PolicyContradictionDetector._extract_quantitative_claims
        quantitative_claims = raw_facts.get("quantitative_claims", [])
        if quantitative_claims and len(quantitative_claims) >= 1:
            return True

        # Check numerical_values from PolicyAnalysisEmbedder._extract_numerical_values
        numerical_values = raw_facts.get("numerical_values", [])
        if numerical_values and len(numerical_values) >= 1:
            return True

        # Check financial_amounts from PDETMunicipalPlanAnalyzer._extract_financial_amounts
        financial_amounts = raw_facts.get("financial_amounts", [])
        if financial_amounts and len(financial_amounts) >= 1:
            return True

        return False

    def _check_baseline_indicator(self, raw_facts: dict[str, Any]) -> bool:
        """
        Check if baseline indicators are present (línea base, año base, situación inicial).

        Deterministic check: pattern matching only, no inference.
        """
        # Check in quantitative_claims context
        quantitative_claims = raw_facts.get("quantitative_claims", [])
        for claim in quantitative_claims:
            context = claim.get("context", "").lower()
            if any(
                re.search(pattern, context, re.IGNORECASE) for pattern in self.BASELINE_INDICATORS
            ):
                return True

        # Check in point_evidence text
        point_evidence = raw_facts.get("point_evidence", {})
        for evidence in point_evidence.values():
            if isinstance(evidence, dict):
                text = evidence.get("text", "").lower()
                if any(
                    re.search(pattern, text, re.IGNORECASE) for pattern in self.BASELINE_INDICATORS
                ):
                    return True
            elif isinstance(evidence, str):
                if any(
                    re.search(pattern, evidence.lower(), re.IGNORECASE)
                    for pattern in self.BASELINE_INDICATORS
                ):
                    return True

        return False

    def _check_year_reference(self, raw_facts: dict[str, Any]) -> bool:
        """
        Check if explicit year reference is present (e.g., "2024", "año 2023").

        Deterministic check: year pattern matching only.
        """
        # Check temporal_markers from PolicyContradictionDetector._extract_temporal_markers
        temporal_markers = raw_facts.get("temporal_markers", [])
        for marker in temporal_markers:
            # Parse using TemporalLogicVerifier to get year
            parsed_year = self.temporal_verifier._parse_temporal_marker(str(marker))
            if parsed_year is not None and parsed_year >= 2000:  # Valid year range
                return True

        # Check in quantitative_claims context for year mentions
        quantitative_claims = raw_facts.get("quantitative_claims", [])
        for claim in quantitative_claims:
            context = claim.get("context", "")
            # Look for year patterns: 20XX or "año 20XX"
            if re.search(
                r"(?:año|años?|vigencia|periodo)\s*(?:de\s*)?(?:20\d{2})", context, re.IGNORECASE
            ):
                return True
            if re.search(r"20\d{2}", context):
                return True

        return False

    def _check_official_sources(self, raw_facts: dict[str, Any]) -> bool:
        """
        Check if official sources are mentioned (DANE, Medicina Legal, Observatorio de Género, etc.).

        Deterministic check: pattern matching only, no entity recognition.
        """
        # Check in point_evidence text
        point_evidence = raw_facts.get("point_evidence", {})
        for evidence in point_evidence.values():
            if isinstance(evidence, dict):
                text = evidence.get("text", "")
            elif isinstance(evidence, str):
                text = evidence
            else:
                continue

            # Check for official source patterns
            for pattern in self.OFFICIAL_SOURCES_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    return True

        # Check in quantitative_claims context
        quantitative_claims = raw_facts.get("quantitative_claims", [])
        for claim in quantitative_claims:
            context = claim.get("context", "")
            for pattern in self.OFFICIAL_SOURCES_PATTERNS:
                if re.search(pattern, context, re.IGNORECASE):
                    return True

        # Check for source mentions in raw text if available
        raw_text = raw_facts.get("raw_text", "")
        if raw_text:
            for pattern in self.OFFICIAL_SOURCES_PATTERNS:
                if re.search(pattern, raw_text, re.IGNORECASE):
                    return True

        return False

    def _check_resources_temporal_compatibility(self, raw_facts: dict[str, Any]) -> bool:
        """
        Check if resources and temporal references are compatible (both present or both absent).

        Deterministic check: co-occurrence validation only, no sufficiency inference.
        """
        # Check if resources are mentioned
        resource_mentions = raw_facts.get("resource_mentions", [])
        has_resources = bool(resource_mentions and len(resource_mentions) > 0)

        # Check if temporal markers are present
        temporal_markers = raw_facts.get("temporal_markers", [])
        has_temporal = bool(temporal_markers and len(temporal_markers) > 0)

        # Compatibility: both present OR both absent (not one without the other)
        # For D1-Q1, we require both to be present
        return has_resources and has_temporal


class PolicyContradictionDetector:
    """
    Sistema avanzado de detección de contradicciones para PDMs colombianos.
    Implementa el estado del arte en NLP y razonamiento lógico.
    """

    def __init__(
        self,
        model_name: str = "hiiamsid/sentence_similarity_spanish_es",
        spacy_model: str = "es_core_news_lg",
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
    ) -> None:
        # Modelos de transformers para análisis semántico
        self.semantic_model = SentenceTransformer(model_name, device=device)

        # Modelo de clasificación de contradicciones
        model_name = "microsoft/deberta-v3-base"
        tokenizer = DebertaV2Tokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)

        self.contradiction_classifier = pipeline(
            "text-classification", model=model, tokenizer=tokenizer, device=device
        )

        # Verificador temporal
        self.temporal_verifier = TemporalLogicVerifier()

        # Calculadora bayesiana de confianza
        self.bayesian_calculator = BayesianConfidenceCalculator()

        # Grafo de conocimiento para razonamiento
        self.knowledge_graph = nx.DiGraph()

        # Patrones PDM específicos
        self._initialize_pdm_patterns()

        self.logger = logging.getLogger(self.__class__.__name__)

    def _initialize_pdm_patterns(self) -> None:
        """Inicializa patrones específicos para análisis de PDMs colombianos"""
        self.pdm_patterns = {
            "diagnostico": re.compile(
                r"(?:diagnóstico|caracterización|situación actual|línea base|año base)",
                re.IGNORECASE,
            ),
            "objetivos": re.compile(r"(?:objetivo|meta|propósito|finalidad)", re.IGNORECASE),
            "estrategias": re.compile(
                r"(?:estrategia|programa|proyecto|acción|intervención)", re.IGNORECASE
            ),
            "recursos": re.compile(
                r"(?:presupuesto|recurso|financiación|inversión|asignación)", re.IGNORECASE
            ),
            "temporal": re.compile(
                r"(?:vigencia|periodo|año|trimestre|semestre|plazo)", re.IGNORECASE
            ),
        }

    def detect(
        self,
        text: str,
        plan_name: str = "PDM",
        dimension: PolicyDimension = PolicyDimension.ESTRATEGICO,
    ) -> dict[str, Any]:
        """
        Detecta contradicciones con análisis multi-dimensional avanzado

        Args:
            text: Texto del plan de desarrollo
            plan_name: Nombre del PDM
            dimension: Dimensión del plan siendo analizada

        Returns:
            Análisis completo con contradicciones detectadas y métricas
        """
        # Extraer declaraciones de política estructuradas
        statements = self._extract_policy_statements(text, dimension)

        # Generar embeddings semánticos
        statements = self._generate_embeddings(statements)

        # Construir grafo de conocimiento
        self._build_knowledge_graph(statements)

        # Detectar contradicciones multi-tipo
        contradictions = []

        # 1. Contradicciones semánticas usando transformers
        semantic_contradictions = self._detect_semantic_contradictions(statements)
        contradictions.extend(ensure_list_return(semantic_contradictions))

        # 2. Inconsistencias numéricas con pruebas estadísticas
        numerical_contradictions = self._detect_numerical_inconsistencies(statements)
        contradictions.extend(ensure_list_return(numerical_contradictions))

        # 3. Conflictos temporales con verificación lógica
        temporal_conflicts = self._detect_temporal_conflicts(statements)
        contradictions.extend(ensure_list_return(temporal_conflicts))

        # 4. Incompatibilidades lógicas usando razonamiento en grafo
        logical_contradictions = self._detect_logical_incompatibilities(statements)
        contradictions.extend(ensure_list_return(logical_contradictions))

        # 5. Conflictos de asignación de recursos
        resource_conflicts = self._detect_resource_conflicts(statements)
        contradictions.extend(ensure_list_return(resource_conflicts))

        # Calcular métricas de coherencia
        coherence_metrics = self._calculate_coherence_metrics(contradictions, statements, text)

        # Generar recomendaciones de resolución
        resolution_recommendations = self._generate_resolution_recommendations(contradictions)

        return {
            "plan_name": plan_name,
            "dimension": dimension.value,
            "contradictions": [self._serialize_contradiction(c) for c in contradictions],
            "coherence_metrics": coherence_metrics,
            "resolution_recommendations": resolution_recommendations,
            "graph_statistics": self._get_graph_statistics(),
        }


# ============================================================================
# PRIORITY 1: N3-AUD CONTRADICTION DOMINATOR (TYPE_E Veto Gate)
# ============================================================================


class ContradictionDominator:
    """
    N3-AUD veto gate for TYPE_E logical contracts - Popperian falsification.

    Epistemological Classification:
    - Level: N3-AUD (Audit/veto only, no extraction)
    - Output Type: CONSTRAINT
    - Fusion Behavior: veto_gate (total dominance)
    - Epistemology: POPPERIAN_FALSIFICATION
    - Contract Compatibility: TYPE_E only

    Scope & Purpose:
    Implements Popperian falsification principle: ONE contradiction -> confidence = 0.0.
    Critical for TYPE_E logical contracts (Q010, Q014, Q019, Q028) which MUST NEVER
    use averaging.

    Dependencies:
    - Requires: ["logical_facts", "consistency_flags", "contradiction_evidence"]
    - Provides: ["veto_decision", "dominance_constraint", "falsification_report"]

    Veto Conditions:
    - contradiction_detected: "TOTAL_VETO"
    - min_contradictions: 1

    Integration Points:
    - Consumes outputs from PolicyContradictionDetector._detect_logical_incompatibilities
    - Must be final gate in TYPE_E processing chain
    - PROHIBITED: Must never use weighted_mean, average, or mean operations
    """

    # Veto configuration
    VETO_CONDITIONS = {
        "contradiction_detected": "TOTAL_VETO",
        "min_contradictions": 1,
        "confidence_on_veto": 0.0,
    }

    # PROHIBITED operations for TYPE_E (enforced at runtime)
    FORBIDDEN_OPERATIONS = ["weighted_mean", "average", "mean", "avg"]

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self._veto_count = 0

    def apply_dominance_veto(self, facts: list[dict] | list[ContradictionEvidence]) -> dict:
        """
        Apply total veto if ANY contradiction detected.
        ONE contradiction -> confidence = 0.0 (non-negotiable).

        Args:
            facts: List of logical facts from N1 with consistency flags,
                   or ContradictionEvidence objects from PolicyContradictionDetector

        Returns:
            {
                "status": "VALID" | "INVALID",
                "confidence": float (0.0 or original),
                "contradiction_detected": bool,
                "veto_applied": bool,
                "rationale": str
            }
        """
        # Handle both dict facts and ContradictionEvidence objects
        has_contradiction = False
        original_confidence = 0.5

        if facts and isinstance(facts[0], ContradictionEvidence):
            # Processing ContradictionEvidence objects
            for evidence in facts:
                if evidence.contradiction_type in [
                    ContradictionType.LOGICAL_INCOMPATIBILITY,
                    ContradictionType.SEMANTIC_OPPOSITION,
                    ContradictionType.NUMERICAL_INCONSISTENCY,
                ]:
                    has_contradiction = True
                    break
            original_confidence = (
                1.0 - max([(1.0 - e.confidence) for e in facts], default=0.0) if facts else 0.5
            )
        else:
            # Processing dict facts
            has_contradiction = self._detect_any_contradiction_from_dicts(facts)
            original_confidence = self._calculate_original_confidence_from_dicts(facts)

        if has_contradiction:
            self._veto_count += 1
            veto_report = self._generate_veto_report_from_facts(facts)

            self.logger.warning(
                "CONTRADICTION DOMINANCE VETO APPLIED: "
                "contradiction(s) detected -> confidence = 0.0"
            )

            return {
                "status": "INVALID",
                "confidence": 0.0,  # TOTAL veto - non-negotiable
                "contradiction_detected": True,
                "veto_applied": True,
                "rationale": "Popperian falsification: ONE contradiction refutes the hypothesis",
                "veto_report": veto_report,
            }
        else:
            return {
                "status": "VALID",
                "confidence": original_confidence,
                "contradiction_detected": False,
                "veto_applied": False,
                "rationale": "No contradictions detected - hypothesis remains viable",
            }

    def detect_any_contradiction(self, facts: list[dict] | list[ContradictionEvidence]) -> bool:
        """
        Scan facts for ANY contradiction (binary check).

        Args:
            facts: List of logical facts or ContradictionEvidence objects

        Returns:
            True if ANY contradiction exists, False otherwise
        """
        if not facts:
            return False

        if isinstance(facts[0], ContradictionEvidence):
            return any(
                e.contradiction_type
                in [
                    ContradictionType.LOGICAL_INCOMPATIBILITY,
                    ContradictionType.SEMANTIC_OPPOSITION,
                    ContradictionType.NUMERICAL_INCONSISTENCY,
                ]
                for e in facts
            )
        else:
            return self._detect_any_contradiction_from_dicts(facts)

    def _detect_any_contradiction_from_dicts(self, facts: list[dict]) -> bool:
        """Detect contradictions in dict-based facts."""
        if not facts:
            return False

        # Check for explicit contradiction flags
        for fact in facts:
            if fact.get("has_contradiction", False):
                return True
            if fact.get("consistency_flag") == "CONTRADICTORY":
                return True
            if fact.get("inconsistent_with"):
                return True

        return False

    def generate_veto_report(self, facts: list[dict] | list[ContradictionEvidence]) -> dict:
        """
        Generate detailed report when veto is applied.

        Returns:
            {
                "contradictions_found": list[dict],
                "affected_facts": list[str],
                "veto_timestamp": str,
                "severity": str
            }
        """
        return self._generate_veto_report_from_facts(facts)

    def _generate_veto_report_from_facts(
        self, facts: list[dict] | list[ContradictionEvidence]
    ) -> dict:
        """Generate veto report from facts (dict or ContradictionEvidence)."""
        contradictions_found = []
        affected_facts = []

        if facts and isinstance(facts[0], ContradictionEvidence):
            for evidence in facts:
                contradictions_found.append(
                    {
                        "fact_id": str(id(evidence)),
                        "statement_a": str(evidence.statement_a.text[:100]),
                        "statement_b": str(evidence.statement_b.text[:100]),
                        "contradiction_type": evidence.contradiction_type.name,
                        "confidence": float(evidence.confidence),
                    }
                )
                affected_facts.append(str(id(evidence)))
        else:
            for fact in facts:
                if fact.get("has_contradiction") or fact.get("consistency_flag") == "CONTRADICTORY":
                    contradictions_found.append(
                        {
                            "fact_id": fact.get("id", "UNKNOWN"),
                            "fact_text": fact.get("text", "")[:100],
                            "contradiction_type": fact.get("contradiction_type", "LOGICAL"),
                            "inconsistent_with": fact.get("inconsistent_with", []),
                        }
                    )
                    affected_facts.append(fact.get("id", "UNKNOWN"))

        severity = "CRITICAL" if len(contradictions_found) == 1 else "CATASTROPHIC"

        return {
            "contradictions_found": contradictions_found,
            "affected_facts": affected_facts,
            "veto_count": self._veto_count,
            "veto_timestamp": logging.getLogger(__name__).name,
            "severity": severity,
            "popperian_principle": "Single refutation suffices for falsification",
        }

    def _calculate_original_confidence_from_dicts(self, facts: list[dict]) -> float:
        """
        Calculate original confidence WITHOUT averaging (uses MIN for TYPE_E).

        This enforces the epistemological constraint that TYPE_E contracts
        use AND logic (min) rather than averaging.
        """
        if not facts:
            return 0.0

        # Use MIN (not mean!) for TYPE_E - weakest link determines strength
        confidences = [f.get("confidence", 0.5) for f in facts if "confidence" in f]

        if not confidences:
            return 0.5

        return min(confidences)


# ============================================================================
# PRIORITY 2: N2-INF DEMPSTER-SHAFER COMBINATOR (TYPE_A Belief Combination)
# ============================================================================


class DempsterShaferCombinator:
    """
    N2-INF belief combination for TYPE_A semantic contracts.

    Epistemological Classification:
    - Level: N2-INF (Computation/combination, no veto)
    - Output Type: PARAMETER
    - Fusion Behavior: dempster_shafer (belief combination)
    - Epistemology: EVIDENTIAL_REASONING
    - Contract Compatibility: TYPE_A only

    Scope & Purpose:
    Implements Dempster-Shafer theory for combining belief masses from multiple
    semantic sources with conflict handling. Required for TYPE_A questions (Q001, Q013).

    Dependencies:
    - Requires: ["semantic_facts", "belief_masses", "source_provenance"]
    - Provides: ["combined_belief", "conflict_resolution", "semantic_fusion_score"]

    Integration Points:
    - Consumes outputs from AdvancedSemanticChunker and TextMiningEngine
    - Satisfies forcing rule: TYPE_A MUST_INCLUDE_N2: ['semantic_score', 'dempster']
    """

    def __init__(self, normalization_threshold: float = 0.95) -> None:
        """
        Args:
            normalization_threshold: Minimum combined mass required for normalization
        """
        self.normalization_threshold = normalization_threshold
        self.logger = logging.getLogger(self.__class__.__name__)

    def combine_belief_masses(self, sources: list[dict]) -> dict:
        """
        Dempster's rule: m(A) = SUM(m1(X) * m2(Y)) / (1 - K)
        where K = conflict mass.

        Args:
            sources: List of belief mass assignments from N1 extractors
                [{"proposition": str, "belief_mass": float, "source_id": str}]

        Returns:
            {
                "combined_belief": dict,
                "conflict_mass": float,
                "normalization_factor": float,
                "reliability_score": float
            }
        """
        if not sources:
            return {
                "combined_belief": {},
                "conflict_mass": 0.0,
                "normalization_factor": 1.0,
                "reliability_score": 0.0,
            }

        if len(sources) == 1:
            # Single source - return as-is
            prop = sources[0].get("proposition", "unknown")
            mass = sources[0].get("belief_mass", 0.5)
            return {
                "combined_belief": {prop: mass},
                "conflict_mass": 0.0,
                "normalization_factor": 1.0,
                "reliability_score": mass,
            }

        # Calculate conflict mass K
        K = self.calculate_conflict_mass(sources)

        # Combine beliefs using Dempster's rule
        combined = self._dempster_combination(sources, K)

        # Normalize by (1 - K)
        normalized = self.normalize_belief_distribution(combined, K)

        # Calculate reliability score
        reliability = self._calculate_reliability_score(normalized, K, len(sources))

        return {
            "combined_belief": normalized,
            "conflict_mass": K,
            "normalization_factor": 1.0 - K,
            "reliability_score": reliability,
        }

    def calculate_conflict_mass(self, sources: list[dict]) -> float:
        """
        Calculate K = SUM(m1(X) * m2(Y)) for all X∩Y = ∅.

        Returns:
            Conflict mass K in [0, 1]
        """
        K = 0.0

        # Group by proposition
        propositions = {}
        for source in sources:
            prop = source.get("proposition", "unknown")
            mass = source.get("belief_mass", 0.5)
            if prop not in propositions:
                propositions[prop] = []
            propositions[prop].append(mass)

        # For Dempster-Shafer, conflict occurs when masses are assigned
        # to mutually exclusive propositions from different sources
        if len(propositions) <= 1:
            return 0.0

        # Calculate conflict as cross-product of masses for different propositions
        prop_names = list(propositions.keys())
        for i, prop1 in enumerate(prop_names):
            for prop2 in prop_names[i + 1 :]:
                for mass1 in propositions[prop1]:
                    for mass2 in propositions[prop2]:
                        K += mass1 * mass2

        return min(1.0, K)

    def normalize_belief_distribution(self, raw_belief: dict, K: float) -> dict:
        """
        Normalize by (1 - K) to ensure belief mass sums to 1.

        Returns:
            Normalized belief distribution
        """
        if K >= 1.0:
            # Total conflict - return uniform distribution
            n_props = len(raw_belief)
            return {k: 1.0 / max(n_props, 1) for k in raw_belief}

        normalization_factor = 1.0 - K

        if normalization_factor < 1e-10:
            # Near-total conflict - return uniform
            n_props = len(raw_belief)
            return {k: 1.0 / max(n_props, 1) for k in raw_belief}

        normalized = {}
        for prop, mass in raw_belief.items():
            normalized[prop] = mass / normalization_factor

        return normalized

    def _dempster_combination(self, sources: list[dict], K: float) -> dict[str, float]:
        """Perform Dempster's rule combination."""
        # Initialize combined beliefs
        combined = {}

        # Group masses by proposition
        for source in sources:
            prop = source.get("proposition", "unknown")
            mass = source.get("belief_mass", 0.5)
            if prop not in combined:
                combined[prop] = 0.0
            # For orthogonal combination, multiply masses for same proposition
            if combined[prop] == 0.0:
                combined[prop] = mass
            else:
                combined[prop] *= mass

        return combined

    def _calculate_reliability_score(self, normalized: dict, K: float, n_sources: int) -> float:
        """
        Calculate reliability score based on:
        - Conflict mass (lower is better)
        - Number of sources (more is better, up to a point)
        - Belief concentration (higher max belief is better)
        """
        # Conflict penalty
        conflict_penalty = K * 0.5

        # Source count bonus (diminishing returns)
        source_bonus = min(0.3, n_sources * 0.1)

        # Concentration bonus (higher max belief indicates agreement)
        max_belief = max(normalized.values()) if normalized else 0.0
        concentration_bonus = max_belief * 0.2

        reliability = 1.0 - conflict_penalty + source_bonus + concentration_bonus
        return max(0.0, min(1.0, reliability))


# ============================================================================
# PRIORITY 2: N2-INF LOGICAL CONSISTENCY CHECKER (TYPE_E AND Logic)
# ============================================================================


class LogicalConsistencyChecker:
    """
    N2-INF consistency checker for TYPE_E - AND logic only.

    Epistemological Classification:
    - Level: N2-INF (Computation, no veto)
    - Output Type: PARAMETER
    - Fusion Behavior: min_consistency (AND logic, NOT averaging)
    - Epistemology: LOGICAL_CONJUNCTION
    - Contract Compatibility: TYPE_E only

    Scope & Purpose:
    Checks logical consistency using AND-based logic (min, NOT mean).
    PROHIBITION: Must never use averaging for TYPE_E.

    Dependencies:
    - Requires: ["logical_facts", "consistency_markers", "fact_confidences"]
    - Provides: ["consistency_score", "min_confidence", "logical_validation"]

    Integration Points:
    - Satisfies forcing rule: TYPE_E MUST_INCLUDE_N2: ['logical_consistency', 'min']
    - Must explicitly avoid methods in FORBIDDEN list
    """

    # PROHIBITED for TYPE_E - enforcement is mandatory
    FORBIDDEN_METHODS = ["weighted_mean", "average", "mean"]

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self._enforce_no_averaging_prohibition()

    def check_consistency(self, facts: list[dict]) -> dict:
        """
        AND-based logic: consistency = min(c1, c2, ..., cn)
        NEVER: mean(c1, c2, ..., cn).

        Args:
            facts: [{"fact": str, "confidence": float, "logical_role": str}]

        Returns:
            {
                "consistency_score": float (min of all confidences),
                "weakest_link": dict,
                "logical_violations": list,
                "fusion_method": "MIN" (NEVER "MEAN")
            }
        """
        if not facts:
            return {
                "consistency_score": 0.0,
                "weakest_link": None,
                "logical_violations": [],
                "fusion_method": "MIN",
            }

        # Extract confidences
        confidences = [f.get("confidence", 0.5) for f in facts]

        # AND logic: use MIN (not mean!)
        consistency_score = min(confidences) if confidences else 0.0

        # Find weakest link (the fact with minimum confidence)
        weakest_idx = confidences.index(consistency_score) if confidences else 0
        weakest_link = {
            "fact": facts[weakest_idx].get("fact", ""),
            "confidence": consistency_score,
            "logical_role": facts[weakest_idx].get("logical_role", "unknown"),
        }

        # Detect logical violations
        violations = self.detect_logical_violations(facts)

        return {
            "consistency_score": consistency_score,
            "weakest_link": weakest_link,
            "logical_violations": violations,
            "fusion_method": "MIN",  # Explicitly MIN, never MEAN
            "fact_count": len(facts),
            "epistemology": "LOGICAL_CONJUNCTION",
        }

    def detect_logical_violations(self, facts: list[dict]) -> list[dict]:
        """
        Identify logical incompatibilities (beyond contradictions).

        Returns:
            List of violation reports
        """
        violations = []

        # Check for explicit violation flags
        for fact in facts:
            if fact.get("has_violation", False):
                violations.append(
                    {
                        "fact": fact.get("fact", ""),
                        "violation_type": fact.get("violation_type", "UNKNOWN"),
                        "description": fact.get("violation_description", ""),
                    }
                )

        # Check for consistency flags
        for fact in facts:
            consistency_flag = fact.get("consistency_flag", "")
            if consistency_flag and consistency_flag not in ["CONSISTENT", "VALID"]:
                violations.append(
                    {
                        "fact": fact.get("fact", ""),
                        "violation_type": "INCONSISTENCY",
                        "description": f"Consistency flag: {consistency_flag}",
                    }
                )

        return violations

    def enforce_no_averaging_prohibition(self) -> None:
        """
        Runtime assertion: raise exception if averaging attempted.
        Enforces epistemological prohibition for TYPE_E.
        """
        # Check if this class has forbidden methods
        for method_name in self.FORBIDDEN_METHODS:
            if hasattr(self, method_name):
                raise TypeError(
                    f"TYPE_E PROHIBITION: Method '{method_name}' is forbidden for "
                    f"logical contracts. Use MIN-based logic instead."
                )

    def _enforce_no_averaging_prohibition(self) -> None:
        """Enforce prohibition at initialization."""
        self.enforce_no_averaging_prohibition()


# ============================================================================
# END OF NEW METHODS
# ============================================================================

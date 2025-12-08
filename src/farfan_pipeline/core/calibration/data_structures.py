"""
Three-Pillar Calibration System - Core Data Structures

This module defines the fundamental data structures for the calibration system
as specified in the SUPERPROMPT Three-Pillar Calibration System.

Spec compliance: Section 1 (Core Objects), Section 7 (Certificates)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CalibrationConfigError(Exception):
    """
    Raised when calibration configuration violates mathematical constraints.

    This error indicates:
    - Fusion weights don't sum to valid range
    - Weight constraints violated (must be ≥ 0)
    - Invalid layer configuration
    - Misconfigured calibration parameters

    SIN_CARRETA Policy: Fail loudly on misconfiguration, never silently clamp.
    """

    pass


class LayerType(Enum):
    """Eight fixed calibration layers - NO RENAMING ALLOWED"""

    BASE = "@b"  # Intrinsic quality
    CHAIN = "@chain"  # Chain compatibility
    UNIT = "@u"  # Unit-of-analysis sensitivity
    QUESTION = "@q"  # Question compatibility
    DIMENSION = "@d"  # Dimension compatibility
    POLICY = "@p"  # Policy compatibility
    INTERPLAY = "@C"  # Interplay congruence
    META = "@m"  # Meta/governance


class MethodRole(Enum):
    """Method roles with fixed required layer sets"""

    INGEST_PDM = "INGEST_PDM"
    STRUCTURE = "STRUCTURE"
    EXTRACT = "EXTRACT"
    SCORE_Q = "SCORE_Q"
    AGGREGATE = "AGGREGATE"
    REPORT = "REPORT"
    META_TOOL = "META_TOOL"
    TRANSFORM = "TRANSFORM"


# Role-based required layers (L_* from spec Section 4)
REQUIRED_LAYERS: dict[MethodRole, set[LayerType]] = {
    MethodRole.INGEST_PDM: {
        LayerType.BASE,
        LayerType.CHAIN,
        LayerType.UNIT,
        LayerType.META,
    },
    MethodRole.STRUCTURE: {
        LayerType.BASE,
        LayerType.CHAIN,
        LayerType.UNIT,
        LayerType.META,
    },
    MethodRole.EXTRACT: {
        LayerType.BASE,
        LayerType.CHAIN,
        LayerType.UNIT,
        LayerType.META,
    },
    MethodRole.SCORE_Q: {
        LayerType.BASE,
        LayerType.CHAIN,
        LayerType.QUESTION,
        LayerType.DIMENSION,
        LayerType.POLICY,
        LayerType.INTERPLAY,
        LayerType.UNIT,
        LayerType.META,
    },
    MethodRole.AGGREGATE: {
        LayerType.BASE,
        LayerType.CHAIN,
        LayerType.DIMENSION,
        LayerType.POLICY,
        LayerType.INTERPLAY,
        LayerType.META,
    },
    MethodRole.REPORT: {
        LayerType.BASE,
        LayerType.CHAIN,
        LayerType.INTERPLAY,
        LayerType.META,
    },
    MethodRole.META_TOOL: {LayerType.BASE, LayerType.CHAIN, LayerType.META},
    MethodRole.TRANSFORM: {LayerType.BASE, LayerType.CHAIN, LayerType.META},
}


@dataclass(frozen=True)
class Context:
    """
    Execution context: ctx = (Q, D, P, U)

    Spec compliance: Definition 1.2

    Q: Question ID or None
    D: Dimension ID (DIM01-DIM06)
    P: Policy area ID (PA01-PA10)
    U: Unit-of-analysis quality [0,1]
    """

    question_id: str | None = None  # Q ∈ Questions ∪ {⊥}
    dimension_id: str = "DIM01"  # D ∈ Dimensions
    policy_id: str = "PA01"  # P ∈ Policies
    unit_quality: float = 0.85  # U ∈ [0,1]

    def __post_init__(self):
        """Validate context constraints"""
        if self.unit_quality < 0.0 or self.unit_quality > 1.0:
            raise ValueError(f"unit_quality must be in [0,1], got {self.unit_quality}")

        if self.dimension_id and not self.dimension_id.startswith("DIM"):
            raise ValueError(
                f"dimension_id must match DIM* pattern, got {self.dimension_id}"
            )

        if self.policy_id and not self.policy_id.startswith("PA"):
            raise ValueError(f"policy_id must match PA* pattern, got {self.policy_id}")


@dataclass
class ComputationGraph:
    """
    Computation graph: Γ = (V, E, T, S)

    Spec compliance: Definition 1.1

    V: finite set of method instance nodes
    E: directed edges (must be DAG)
    T: edge typing function
    S: node signature function
    """

    nodes: set[str] = field(default_factory=set)  # V
    edges: list[tuple[str, str]] = field(default_factory=list)  # E ⊆ V × V
    edge_types: dict[tuple[str, str], dict[str, Any]] = field(default_factory=dict)  # T
    node_signatures: dict[str, dict[str, Any]] = field(default_factory=dict)  # S

    def validate_dag(self) -> bool:
        """Axiom 1.1: Graph must be acyclic"""
        # Simple cycle detection via DFS
        visited = set()
        rec_stack = set()

        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for edge in self.edges:
                if edge[0] == node:
                    neighbor = edge[1]
                    if neighbor not in visited:
                        if has_cycle(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        return True

            rec_stack.remove(node)
            return False

        for node in self.nodes:
            if node not in visited:
                if has_cycle(node):
                    return False
        return True


@dataclass
class InterplaySubgraph:
    """
    Valid interplay: G = (V_G, E_G) ⊆ Γ

    Spec compliance: Definition 2.1

    Must satisfy:
    1. Single target property
    2. Declared fusion rule
    3. Type compatibility
    """

    nodes: set[str]
    edges: list[tuple[str, str]]
    target_output: str
    fusion_rule: str
    compatible: bool = True


@dataclass(frozen=True)
class CalibrationCertificate:
    """
    Complete calibration certificate with audit trail.

    Spec compliance: Section 7 (Definition 7.1)

    MUST allow exact reconstruction of Cal(I) from contents.
    Property 7.1: No hidden behavior - all computations must appear here.
    """

    # Identity
    instance_id: str
    method_id: str
    node_id: str
    context: Context

    # Scores
    intrinsic_score: float  # x_@b
    layer_scores: dict[str, float]  # All x_ℓ(I)
    calibrated_score: float  # Cal(I)

    # Transparency
    fusion_formula: dict[str, Any]  # symbolic, expanded, computation_trace
    parameter_provenance: dict[str, dict[str, Any]]  # Where each parameter came from
    evidence_trail: dict[str, Any]  # Evidence used for layer computations

    # Integrity
    config_hash: str  # SHA256 of all config files
    graph_hash: str  # SHA256 of computation graph

    # Validation
    validation_checks: dict[str, Any] = field(default_factory=dict)
    sensitivity_analysis: dict[str, Any] = field(default_factory=dict)

    # Audit
    timestamp: str = ""
    validator_version: str = "1.0.0"

    def __post_init__(self):
        """Validate certificate constraints"""
        # Boundedness check
        if not (0.0 <= self.calibrated_score <= 1.0):
            raise ValueError(
                f"calibrated_score must be in [0,1], got {self.calibrated_score}"
            )

        if not (0.0 <= self.intrinsic_score <= 1.0):
            raise ValueError(
                f"intrinsic_score must be in [0,1], got {self.intrinsic_score}"
            )

        for layer, score in self.layer_scores.items():
            if not (0.0 <= score <= 1.0):
                raise ValueError(f"layer_scores[{layer}] must be in [0,1], got {score}")


@dataclass
class CalibrationSubject:
    """
    Calibration subject: I = (M, v, Γ, G, ctx)

    Spec compliance: Definition 1.3

    M: method artifact
    v: node instance
    Γ: containing graph
    G: interplay subgraph (or None)
    ctx: execution context
    """

    method_id: str  # M (canonical method ID)
    node_id: str  # v ∈ V
    graph: ComputationGraph  # Γ
    interplay: InterplaySubgraph | None  # G
    context: Context  # ctx

    # Additional metadata
    role: MethodRole | None = None
    active_layers: set[LayerType] = field(default_factory=set)


@dataclass
class EvidenceStore:
    """
    Storage for evidence used in calibration computations.
    All evidence must be traceable and auditable.
    """

    pdt_structure: dict[str, Any] = field(default_factory=dict)
    pdm_metrics: dict[str, Any] = field(default_factory=dict)
    runtime_metrics: dict[str, Any] = field(default_factory=dict)
    test_results: dict[str, Any] = field(default_factory=dict)
    deployment_history: dict[str, Any] = field(default_factory=dict)

    def get_evidence(self, key: str, default: Any = None) -> Any:
        """Retrieve evidence by key"""
        for store in [
            self.pdt_structure,
            self.pdm_metrics,
            self.runtime_metrics,
            self.test_results,
            self.deployment_history,
        ]:
            if key in store:
                return store[key]
        return default


@dataclass(frozen=True)
class CompatibilityMapping:
    """
    Defines how compatible a method is with questions/dimensions/policies.

    This implements the Q_f, D_f, P_f functions from the theoretical model.

    Compatibility Scores (from theoretical model):
        1.0 = Primary (designed specifically for this context)
        0.7 = Secondary (works well, but not optimal)
        0.3 = Compatible (can work, limited effectiveness)
        0.1 = Undeclared (penalty, not validated for this context)

    Example:
        CompatibilityMapping(
            method_id="pattern_extractor_v2",
            questions={"Q001": 1.0, "Q031": 0.7, "Q091": 0.3},
            dimensions={"DIM01": 1.0, "DIM03": 0.7},
            policies={"PA01": 1.0, "PA10": 0.7}
        )
    """

    method_id: str
    questions: dict[str, float] = field(default_factory=dict)
    dimensions: dict[str, float] = field(default_factory=dict)
    policies: dict[str, float] = field(default_factory=dict)

    def get_question_score(self, question_id: str) -> float:
        """
        Get compatibility score for a question.

        Returns 0.1 (penalty) if question not declared.
        """
        return self.questions.get(question_id, 0.1)

    def get_dimension_score(self, dimension: str) -> float:
        """
        Get compatibility score for a dimension.

        Returns 0.1 (penalty) if dimension not declared.
        """
        return self.dimensions.get(dimension, 0.1)

    def get_policy_score(self, policy: str) -> float:
        """
        Get compatibility score for a policy area.

        Returns 0.1 (penalty) if policy not declared.
        """
        return self.policies.get(policy, 0.1)

    def check_anti_universality(self, threshold: float = 0.9) -> bool:
        """
        Check Anti-Universality Theorem compliance.

        The theorem states: NO method can have average compatibility ≥ 0.9
        across ALL questions, dimensions, AND policies simultaneously.

        Returns:
            True if compliant (method is NOT universal)
            False if violation detected
        """
        if not self.questions or not self.dimensions or not self.policies:
            return True

        avg_q = sum(self.questions.values()) / len(self.questions)
        avg_d = sum(self.dimensions.values()) / len(self.dimensions)
        avg_p = sum(self.policies.values()) / len(self.policies)

        is_universal = avg_q >= threshold and avg_d >= threshold and avg_p >= threshold

        return not is_universal

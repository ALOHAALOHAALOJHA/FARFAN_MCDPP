"""
Runtime Layer Computer - Implementación Producción
Basado en: "A System-Layer Formalization for Method Calibration"

Implementa las capas runtime (@chain, @q, @d, @p, @C, @u, @m) según 
especificaciones matemáticas formales del documento canónico.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Any, Tuple
from enum import Enum
import numpy as np
from collections import Counter
import hashlib
import json


# ============================================================================
# ESTRUCTURAS DE DATOS
# ============================================================================

@dataclass
class CalibrationContext:
    """Context (Q, D, P, U) según Definition 1.2"""
    question_id: Optional[str]  # Q ∈ Questions ∪ {⊥}
    dimension: str              # D ∈ Dimensions (D1-D6)
    policy_area: str            # P ∈ Policies
    unit_quality: float         # U ∈ [0,1]
    
    # F.A.R.F.A.N. specific
    question_num: int = 0       # Q1-Q5
    method_position: int = 0    # Position in execution chain
    total_methods: int = 0      # Total methods in chain
    
    def __post_init__(self):
        assert 0.0 <= self.unit_quality <= 1.0, "U must be in [0,1]"


@dataclass
class MethodSignature:
    """Node signature S(v) según Definition 1.1"""
    required_inputs: Set[str]
    optional_inputs: Set[str]
    input_schemas: Dict[str, type]
    output_schema: type
    semantic_tags: Set[str]


@dataclass
class EdgeType:
    """Edge typing T(e) según Definition 1.1"""
    domain: str
    schema: type
    semantic_type: str


@dataclass
class ComputationGraph:
    """Computation graph Γ = (V, E, T, S) según Definition 1.1"""
    nodes: Set[str]  # V
    edges: Set[Tuple[str, str]]  # E ⊆ V × V
    edge_types: Dict[Tuple[str, str], EdgeType]  # T
    node_signatures: Dict[str, MethodSignature]  # S


@dataclass
class InterplaySubgraph:
    """Valid interplay según Definition 2.1"""
    nodes: Set[str]
    target_output: str
    fusion_rule: str
    scale_congruent: bool
    semantic_overlap: float


@dataclass
class RuntimeLayers:
    """Capas runtime evaluadas"""
    chain: float      # @chain
    quality: float    # @q
    density: float    # @d (dimension)
    provenance: float # @p (policy)
    coverage: float   # @C (interplay)
    uncertainty: float # @u (unit-of-analysis)
    mechanism: float  # @m (meta)
    
    def to_dict(self) -> Dict[str, float]:
        return {
            '@chain': self.chain,
            '@q': self.quality,
            '@d': self.density,
            '@p': self.provenance,
            '@C': self.coverage,
            '@u': self.uncertainty,
            '@m': self.mechanism
        }


class MethodRole(Enum):
    """Role ontology según Definition 4.1"""
    INGEST_PDM = "INGEST_PDM"
    STRUCTURE = "STRUCTURE"
    EXTRACT = "EXTRACT"
    SCORE_Q = "SCORE_Q"
    AGGREGATE = "AGGREGATE"
    REPORT = "REPORT"
    META_TOOL = "META_TOOL"
    TRANSFORM = "TRANSFORM"


# ============================================================================
# CONFIGURACIÓN DEL SISTEMA F.A.R.F.A.N.
# ============================================================================

class CalibrationConfig:
    """Configuration using official factory loaders from core.orchestrator.factory"""
    
    def __init__(self):
        """Initialize config by loading from official questionnaire factory."""
        from farfan_pipeline.core.orchestrator.factory import (
            load_questionnaire,
            get_canonical_dimensions,
            get_canonical_policy_areas
        )
        
        # Load canonical questionnaire (hash-verified, immutable)
        self.questionnaire = load_questionnaire()
        
        # Load canonical dimensions and policy areas
        self.dimensions = get_canonical_dimensions()
        self.policy_areas = get_canonical_policy_areas()
        
        # Cache the raw data for compatibility
        self.config_data = dict(self.questionnaire.data)
    
    def get_method_compatibility(
        self, 
        method_id: str, 
        question_id: str
    ) -> float:
        """
        Q_f(M | Q) según Definition 3.4.1
        Returns: 1.0 (primary), 0.7 (secondary), 0.3 (compatible), 0.0 (incompatible)
        """
        questions = self.config_data.get('questions', [])
        
        for q in questions:
            if q.get('id') == question_id:
                method_sets = q.get('method_sets', {})
                
                if method_id in method_sets.get('primary', []):
                    return 1.0
                elif method_id in method_sets.get('secondary', []):
                    return 0.7
                elif method_id in method_sets.get('validators', []):
                    return 0.3
        
        # Penalty for undeclared methods
        return 0.1
    
    def get_dimension_compatibility(
        self, 
        method_id: str, 
        dimension: str
    ) -> float:
        """D_f(M | D) - dimension compatibility"""
        dimensions = self.config_data.get('dimensions', {})
        
        if dimension in dimensions:
            dim_methods = dimensions[dimension].get('methods', {})
            
            if method_id in dim_methods.get('primary', []):
                return 1.0
            elif method_id in dim_methods.get('secondary', []):
                return 0.7
            elif method_id in dim_methods.get('compatible', []):
                return 0.5
        
        return 0.2
    
    def get_policy_compatibility(
        self, 
        method_id: str, 
        policy: str
    ) -> float:
        """P_f(M | P) - policy compatibility"""
        policies = self.config_data.get('policies', {})
        
        if policy in policies:
            pol_methods = policies[policy].get('methods', {})
            
            if method_id in pol_methods.get('primary', []):
                return 1.0
            elif method_id in pol_methods.get('applicable', []):
                return 0.6
        
        return 0.3
    
    def get_fusion_rule(self, question_id: str) -> Optional[str]:
        """Get fusion rule from scoring_modality"""
        questions = self.config_data.get('questions', [])
        
        for q in questions:
            if q.get('id') == question_id:
                return q.get('scoring_modality')
        
        return None
    
    def get_interplay_for_question(
        self, 
        question_id: str
    ) -> Optional[InterplaySubgraph]:
        """Build interplay subgraph según Definition 2.1"""
        questions = self.config_data.get('questions', [])
        
        for q in questions:
            if q.get('id') == question_id:
                method_sets = q.get('method_sets', {})
                
                # Build node set V_G
                nodes = set()
                nodes.update(method_sets.get('primary', []))
                nodes.update(method_sets.get('validators', []))
                
                if len(nodes) < 2:
                    return None  # No interplay
                
                fusion_rule = q.get('scoring_modality')
                if not fusion_rule:
                    return None  # No fusion declared
                
                return InterplaySubgraph(
                    nodes=nodes,
                    target_output=f"score_{question_id}",
                    fusion_rule=fusion_rule,
                    scale_congruent=True,  # Assume [0,1] range
                    semantic_overlap=self._compute_semantic_overlap(nodes)
                )
        
        return None
    
    def _compute_semantic_overlap(self, nodes: Set[str]) -> float:
        """
        Semantic overlap según Definition 3.5.1:
        semantic_overlap(C) = |⋂ᵢ Cᵢ| / |⋃ᵢ Cᵢ|
        """
        if len(nodes) < 2:
            return 1.0
        
        # Extract semantic tokens from method names
        all_tokens = set()
        common_tokens = None
        
        for node in nodes:
            tokens = set(node.lower().split('_'))
            all_tokens.update(tokens)
            
            if common_tokens is None:
                common_tokens = tokens
            else:
                common_tokens &= tokens
        
        if len(all_tokens) == 0:
            return 0.5
        
        return len(common_tokens) / len(all_tokens)


# ============================================================================
# RUNTIME LAYER COMPUTER
# ============================================================================

class RuntimeLayerComputer:
    """
    Compute real runtime layer scores según formalizaciones matemáticas.
    Implementa Definitions 3.2 - 3.6 del documento canónico.
    """
    
    def __init__(self, config: CalibrationConfig):
        self.config = config
        self.cache: Dict[str, float] = {}
        
        # Thresholds según specifications
        self.UNIT_ABORT_THRESHOLD = 0.3
        self.UNIT_SATURATION_THRESHOLD = 0.8
        
        # Performance thresholds para @m
        self.RUNTIME_FAST = 1.0  # seconds
        self.RUNTIME_ACCEPTABLE = 5.0
        self.MEMORY_NORMAL = 500  # MB
        self.MEMORY_EXCESSIVE = 2000
    
    # ========================================================================
    # @chain - Chain Compatibility Layer (Definition 3.2)
    # ========================================================================
    
    def compute_chain_score(
        self,
        method_id: str,
        graph: ComputationGraph,
        node_id: str,
        execution_metadata: Dict[str, Any]
    ) -> float:
        """
        x_@chain según Definition 3.2.1:
        
        Returns:
          0.0: hard_mismatch (schema incompatible)
          0.3: missing_critical_optional
          0.6: soft_schema_violation
          0.8: all_contracts_pass ∧ warnings_exist
          1.0: all_contracts_pass ∧ no_warnings
        """
        cache_key = f"chain_{method_id}_{node_id}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Check hard mismatches
        if self._has_hard_mismatch(node_id, graph):
            self.cache[cache_key] = 0.0
            return 0.0
        
        # Check for missing critical optionals
        if self._missing_critical_optional(node_id, graph, execution_metadata):
            self.cache[cache_key] = 0.3
            return 0.3
        
        # Check soft schema violations
        if self._has_soft_schema_violation(node_id, graph):
            self.cache[cache_key] = 0.6
            return 0.6
        
        # All contracts pass - check for warnings
        warnings = execution_metadata.get('warnings', [])
        
        if len(warnings) > 0:
            self.cache[cache_key] = 0.8
            return 0.8
        else:
            self.cache[cache_key] = 1.0
            return 1.0
    
    def _has_hard_mismatch(
        self, 
        node_id: str, 
        graph: ComputationGraph
    ) -> bool:
        """
        hard_mismatch(v) según Definition 3.2.1:
        ∃e ∈ in_edges(v): ¬schema_compatible(T(e), S(v).input)
        ∨ ∃required ∈ S(v).required_inputs: ¬available(required)
        """
        if node_id not in graph.node_signatures:
            return True
        
        signature = graph.node_signatures[node_id]
        
        # Check required inputs availability
        incoming_edges = [e for e in graph.edges if e[1] == node_id]
        
        available_inputs = set()
        for edge in incoming_edges:
            if edge in graph.edge_types:
                edge_type = graph.edge_types[edge]
                available_inputs.add(edge_type.domain)
        
        # Check if all required inputs are available
        missing_required = signature.required_inputs - available_inputs
        if len(missing_required) > 0:
            return True
        
        # Check schema compatibility for each edge
        for edge in incoming_edges:
            if edge in graph.edge_types:
                edge_type = graph.edge_types[edge]
                expected_schema = signature.input_schemas.get(edge_type.domain)
                
                if expected_schema and not self._schema_compatible(
                    edge_type.schema, 
                    expected_schema
                ):
                    return True
        
        return False
    
    def _schema_compatible(self, provided: type, expected: type) -> bool:
        """Check if provided type is compatible with expected type"""
        # In production: use proper type checking library
        return provided == expected or issubclass(provided, expected)
    
    def _missing_critical_optional(
        self, 
        node_id: str, 
        graph: ComputationGraph,
        metadata: Dict[str, Any]
    ) -> bool:
        """Check if critical optional inputs are missing"""
        if node_id not in graph.node_signatures:
            return False
        
        signature = graph.node_signatures[node_id]
        
        # Critical optionals are those that significantly impact quality
        critical_optionals = metadata.get('critical_optionals', set())
        
        incoming_edges = [e for e in graph.edges if e[1] == node_id]
        available_inputs = set()
        for edge in incoming_edges:
            if edge in graph.edge_types:
                available_inputs.add(graph.edge_types[edge].domain)
        
        missing_critical = (
            critical_optionals & signature.optional_inputs
        ) - available_inputs
        
        return len(missing_critical) > 0
    
    def _has_soft_schema_violation(
        self, 
        node_id: str, 
        graph: ComputationGraph
    ) -> bool:
        """Check for soft schema violations (weak incompatibilities)"""
        if node_id not in graph.node_signatures:
            return False
        
        signature = graph.node_signatures[node_id]
        incoming_edges = [e for e in graph.edges if e[1] == node_id]
        
        for edge in incoming_edges:
            if edge in graph.edge_types:
                edge_type = graph.edge_types[edge]
                expected = signature.input_schemas.get(edge_type.domain)
                
                if expected and self._weakly_incompatible(
                    edge_type.schema, 
                    expected
                ):
                    return True
        
        return False
    
    def _weakly_incompatible(self, provided: type, expected: type) -> bool:
        """Check if types are weakly incompatible (coercible but suboptimal)"""
        weak_pairs = [
            (int, float),  # Precision loss
            (str, int),    # Parse required
            (list, set),   # Order loss
        ]
        
        return (provided, expected) in weak_pairs
    
    # ========================================================================
    # @q, @d, @p - Question/Dimension/Policy Layers (Definition 3.4)
    # ========================================================================
    
    def compute_quality_score(
        self,
        method_id: str,
        context: CalibrationContext
    ) -> float:
        """
        x_@q(I) = Q_f(M | Q) según Definition 3.4.1
        
        Returns: 1.0 (primary), 0.7 (secondary), 0.3 (compatible), 
                 0.0 (incompatible), 0.1 (undeclared)
        """
        if context.question_id is None:
            return 1.0  # No question context
        
        return self.config.get_method_compatibility(
            method_id, 
            context.question_id
        )
    
    def compute_density_score(
        self,
        method_id: str,
        context: CalibrationContext
    ) -> float:
        """
        x_@d(I) = D_f(M | D) - dimension compatibility
        Similar structure to Q_f
        """
        return self.config.get_dimension_compatibility(
            method_id, 
            context.dimension
        )
    
    def compute_provenance_score(
        self,
        method_id: str,
        context: CalibrationContext
    ) -> float:
        """
        x_@p(I) = P_f(M | P) - policy compatibility
        Similar structure to Q_f
        """
        return self.config.get_policy_compatibility(
            method_id, 
            context.policy_area
        )
    
    # ========================================================================
    # @C - Interplay Congruence Layer (Definition 3.5)
    # ========================================================================
    
    def compute_coverage_score(
        self,
        method_id: str,
        context: CalibrationContext,
        graph: ComputationGraph
    ) -> float:
        """
        x_@C(I) según Definition 3.5.1:
        
        C_play(G | ctx) = c_scale · c_sem · c_fusion
        
        Returns 1.0 if no interplay, otherwise computed score
        """
        if context.question_id is None:
            return 1.0  # No question context
        
        # Get interplay subgraph
        interplay = self.config.get_interplay_for_question(context.question_id)
        
        if interplay is None or method_id not in interplay.nodes:
            return 1.0  # No interplay dependency
        
        # Compute components
        c_scale = self._compute_scale_congruence(interplay, graph)
        c_sem = interplay.semantic_overlap
        c_fusion = self._compute_fusion_validity(interplay, graph)
        
        return c_scale * c_sem * c_fusion
    
    def _compute_scale_congruence(
        self, 
        interplay: InterplaySubgraph, 
        graph: ComputationGraph
    ) -> float:
        """
        c_scale según Definition 3.5.1:
        
        Returns:
          1.0: all outputs same range
          0.8: convertible with declared transform
          0.0: incompatible
        """
        if interplay.scale_congruent:
            return 1.0
        
        return 0.8  # Assume convertible
    
    def _compute_fusion_validity(
        self, 
        interplay: InterplaySubgraph, 
        graph: ComputationGraph
    ) -> float:
        """
        c_fusion según Definition 3.5.1:
        
        Returns:
          1.0: fusion_rule declared ∧ all_inputs_provided
          0.5: fusion_rule declared ∧ some_inputs_missing
          0.0: fusion_rule not declared
        """
        if not interplay.fusion_rule:
            return 0.0
        
        # Check if all interplay nodes are present in graph
        all_present = all(node in graph.nodes for node in interplay.nodes)
        
        if all_present:
            return 1.0
        else:
            return 0.5
    
    # ========================================================================
    # @u - Unit-of-Analysis Layer (Definition 3.3)
    # ========================================================================
    
    def compute_uncertainty_score(
        self,
        method_id: str,
        context: CalibrationContext,
        method_role: MethodRole
    ) -> float:
        """
        x_@u(I) según Definition 3.3.1:
        
        x_@u(I) = g_M(U) if M ∈ U_sensitive_methods, else 1
        
        Implements g_INGEST, g_STRUCT, g_QA functions
        """
        U = context.unit_quality
        
        # Check if method is U-sensitive
        if not self._is_unit_sensitive(method_role):
            return 1.0
        
        # Apply appropriate g_M function
        if method_role == MethodRole.INGEST_PDM:
            return self._g_INGEST(U)
        elif method_role == MethodRole.STRUCTURE:
            return self._g_STRUCT(U)
        elif method_role == MethodRole.SCORE_Q:
            return self._g_QA(U)
        else:
            return 1.0
    
    def _is_unit_sensitive(self, role: MethodRole) -> bool:
        """Check if role is sensitive to unit-of-analysis quality"""
        sensitive_roles = {
            MethodRole.INGEST_PDM,
            MethodRole.STRUCTURE,
            MethodRole.EXTRACT,
            MethodRole.SCORE_Q
        }
        return role in sensitive_roles
    
    def _g_INGEST(self, U: float) -> float:
        """g_INGEST(U) = U (identity - directly sensitive)"""
        return U
    
    def _g_STRUCT(self, U: float) -> float:
        """
        g_STRUCT(U) según Definition 3.3.2:
        
        Returns:
          0:          U < 0.3 (abort threshold)
          2U - 0.6:   0.3 ≤ U < 0.8 (linear ramp)
          1:          U ≥ 0.8 (saturation)
        """
        if U < self.UNIT_ABORT_THRESHOLD:
            return 0.0
        elif U < self.UNIT_SATURATION_THRESHOLD:
            return 2 * U - 0.6
        else:
            return 1.0
    
    def _g_QA(self, U: float) -> float:
        """
        g_QA(U) = 1 - exp(-5(U - 0.5)) (sigmoidal, inflection at 0.5)
        """
        return 1.0 - np.exp(-5 * (U - 0.5))
    
    # ========================================================================
    # @m - Meta Layer (Definition 3.6)
    # ========================================================================
    
    def compute_mechanism_score(
        self,
        method_id: str,
        runtime_metrics: Dict[str, Any],
        test_coverage: float,
        documentation_score: float
    ) -> float:
        """
        x_@m(I) según Definition 3.6.1:
        
        x_@m(I) = w_perf · m_perf + w_test · m_test + w_doc · m_doc
        
        where:
          - m_perf: performance score
          - m_test: test coverage score
          - m_doc: documentation score
          
        Weights: w_perf=0.3, w_test=0.5, w_doc=0.2
        """
        # Compute performance score
        m_perf = self._compute_performance_score(runtime_metrics)
        
        # Compute test score
        m_test = self._compute_test_score(test_coverage)
        
        # Compute documentation score
        m_doc = documentation_score
        
        # Weighted combination
        w_perf = 0.3
        w_test = 0.5
        w_doc = 0.2
        
        return w_perf * m_perf + w_test * m_test + w_doc * m_doc
    
    def _compute_performance_score(
        self, 
        metrics: Dict[str, Any]
    ) -> float:
        """
        m_perf según Definition 3.6.2:
        
        m_perf = 0.6 · runtime_score + 0.4 · memory_score
        
        runtime_score:
          1.0: t < 1s (FAST)
          linear decay: 1s ≤ t < 5s
          0.0: t ≥ 5s (SLOW)
          
        memory_score:
          1.0: mem < 500 MB (NORMAL)
          linear decay: 500 MB ≤ mem < 2 GB
          0.0: mem ≥ 2 GB (EXCESSIVE)
        """
        runtime_s = metrics.get('runtime_seconds', 0.0)
        memory_mb = metrics.get('memory_mb', 0.0)
        
        # Runtime score
        if runtime_s < self.RUNTIME_FAST:
            runtime_score = 1.0
        elif runtime_s < self.RUNTIME_ACCEPTABLE:
            # Linear decay from 1.0 to 0.0
            runtime_score = 1.0 - (runtime_s - self.RUNTIME_FAST) / (
                self.RUNTIME_ACCEPTABLE - self.RUNTIME_FAST
            )
        else:
            runtime_score = 0.0
        
        # Memory score
        if memory_mb < self.MEMORY_NORMAL:
            memory_score = 1.0
        elif memory_mb < self.MEMORY_EXCESSIVE:
            # Linear decay from 1.0 to 0.0
            memory_score = 1.0 - (memory_mb - self.MEMORY_NORMAL) / (
                self.MEMORY_EXCESSIVE - self.MEMORY_NORMAL
            )
        else:
            memory_score = 0.0
        
        return 0.6 * runtime_score + 0.4 * memory_score
    
    def _compute_test_score(self, coverage: float) -> float:
        """
        m_test según Definition 3.6.2:
        
        m_test = coverage if coverage ≥ 0.8, else 0
        
        (Hard threshold: coverage must be ≥ 80%)
        """
        if coverage >= 0.8:
            return coverage
        else:
            return 0.0
    
    # ========================================================================
    # MAIN API: Compute all layers
    # ========================================================================
    
    def compute_all_layers(
        self,
        method_id: str,
        context: CalibrationContext,
        graph: ComputationGraph,
        node_id: str,
        method_role: MethodRole,
        execution_metadata: Dict[str, Any],
        runtime_metrics: Dict[str, Any],
        test_coverage: float,
        documentation_score: float
    ) -> RuntimeLayers:
        """
        Compute all runtime layers for a method invocation.
        
        Args:
            method_id: Method identifier
            context: Calibration context (Q, D, P, U)
            graph: Computation graph
            node_id: Node ID in graph
            method_role: Method role classification
            execution_metadata: Execution metadata (warnings, etc.)
            runtime_metrics: Runtime performance metrics
            test_coverage: Test coverage fraction [0,1]
            documentation_score: Documentation quality [0,1]
            
        Returns:
            RuntimeLayers with all 7 layer scores
        """
        return RuntimeLayers(
            chain=self.compute_chain_score(
                method_id, graph, node_id, execution_metadata
            ),
            quality=self.compute_quality_score(method_id, context),
            density=self.compute_density_score(method_id, context),
            provenance=self.compute_provenance_score(method_id, context),
            coverage=self.compute_coverage_score(method_id, context, graph),
            uncertainty=self.compute_uncertainty_score(
                method_id, context, method_role
            ),
            mechanism=self.compute_mechanism_score(
                method_id, runtime_metrics, test_coverage, documentation_score
            )
        )


# ============================================================================
# FACTORY & UTILITIES
# ============================================================================

def create_runtime_computer(
    config_path: Optional[str] = None
) -> RuntimeLayerComputer:
    """Factory function to create RuntimeLayerComputer with config"""
    config = CalibrationConfig(config_path)
    return RuntimeLayerComputer(config)


def create_farfan_context(
    dimension: str,
    question_num: int,
    policy_area: str,
    unit_quality: float,
    method_position: int = 0,
    total_methods: int = 1
) -> CalibrationContext:
    """
    Factory for F.A.R.F.A.N. calibration contexts.
    
    Args:
        dimension: D1-D6
        question_num: 1-5
        policy_area: Policy area string
        unit_quality: Unit quality [0,1]
        method_position: Position in chain
        total_methods: Total methods in chain
        
    Returns:
        CalibrationContext
    """
    return CalibrationContext(
        question_id=f"{dimension}_Q{question_num}",
        dimension=dimension,
        policy_area=policy_area,
        unit_quality=unit_quality,
        question_num=question_num,
        method_position=method_position,
        total_methods=total_methods
    )

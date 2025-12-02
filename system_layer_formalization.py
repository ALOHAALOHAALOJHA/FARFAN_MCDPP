"""
Runtime Layer Computer - Production Implementation
Based on: "A System-Layer Formalization for Method Calibration"

Implements runtime layers (@b, @chain, @q, @d, @p, @C, @u, @m) according to
formal mathematical specifications from the canonical document.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Any, Tuple
from enum import Enum
import numpy as np
import hashlib
import json

# ============================================================================
# CORE DATA STRUCTURES
# ============================================================================

@dataclass
class CalibrationContext:
    """Context (Q, D, P, U) según Definition 1.2"""
    question_id: Optional[str]  # Q ∈ Questions ∪ {⊥}
    dimension: str              # D ∈ Dimensions
    policy_area: str            # P ∈ Policies
    unit_quality: float         # U ∈ [0,1]
    
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
    nodes: Set[str]
    edges: Set[Tuple[str, str]]
    edge_types: Dict[Tuple[str, str], EdgeType]
    node_signatures: Dict[str, MethodSignature]


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
    base: float         # @b
    chain: float        # @chain
    quality: float      # @q
    density: float      # @d
    provenance: float   # @p
    coverage: float     # @C
    uncertainty: float  # @u
    mechanism: float    # @m
    
    def to_dict(self) -> Dict[str, float]:
        return {
            '@b': self.base,
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
# CONFIGURATION MANAGER
# ============================================================================

class CalibrationConfig:
    """Configuration manager - loads from questionnaire_monolith.json"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_data = self._load_config(config_path) if config_path else {}
        
    def _load_config(self, path: str) -> Dict:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_method_compatibility(self, method_id: str, question_id: str) -> float:
        """Q_f(M | Q) según Definition 3.4.1"""
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
        
        return 0.1  # Penalty for undeclared
    
    def get_dimension_compatibility(self, method_id: str, dimension: str) -> float:
        """D_f(M | D) - similar structure to Q_f"""
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
    
    def get_policy_compatibility(self, method_id: str, policy: str) -> float:
        """P_f(M | P) - similar structure"""
        policies = self.config_data.get('policies', {})
        
        if policy in policies:
            pol_methods = policies[policy].get('methods', {})
            
            if method_id in pol_methods.get('primary', []):
                return 1.0
            elif method_id in pol_methods.get('applicable', []):
                return 0.6
        
        return 0.3
    
    def get_interplay_for_question(self, question_id: str) -> Optional[InterplaySubgraph]:
        """Build interplay subgraph según Definition 2.1"""
        questions = self.config_data.get('questions', [])
        
        for q in questions:
            if q.get('id') == question_id:
                method_sets = q.get('method_sets', {})
                
                nodes = set()
                nodes.update(method_sets.get('primary', []))
                nodes.update(method_sets.get('validators', []))
                
                if len(nodes) < 2:
                    return None
                
                fusion_rule = q.get('scoring_modality')
                if not fusion_rule:
                    return None
                
                return InterplaySubgraph(
                    nodes=nodes,
                    target_output=f"score_{question_id}",
                    fusion_rule=fusion_rule,
                    scale_congruent=True,
                    semantic_overlap=self._compute_semantic_overlap(nodes)
                )
        
        return None
    
    def _compute_semantic_overlap(self, nodes: Set[str]) -> float:
        """semantic_overlap(C) = |⋂ᵢ Cᵢ| / |⋃ᵢ Cᵢ|"""
        if len(nodes) < 2:
            return 1.0
        
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
    Implementa Definitions 3.1 - 3.6 del documento canónico.
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
    # @b - Base Layer (Definition 3.1)
    # ========================================================================
    
    def compute_base_score(self, method_id: str, method_metadata: Dict[str, Any]) -> float:
        """
        x_@b(I) según Definition 3.1.1:
        x_@b(I) = w_th · b_theory(M) + w_imp · b_impl(M) + w_dep · b_deploy(M)
        """
        w_th, w_imp, w_dep = 0.4, 0.35, 0.25
        
        b_theory = self._compute_theory_score(method_metadata)
        b_impl = self._compute_implementation_score(method_metadata)
        b_deploy = self._compute_deployment_score(method_metadata)
        
        return w_th * b_theory + w_imp * b_impl + w_dep * b_deploy
    
    def _compute_theory_score(self, metadata: Dict[str, Any]) -> float:
        """b_theory(M) según Definition 3.1.1"""
        theory_scores = metadata.get('theory_scores', {})
        
        weights = {
            'grounded_in_valid_statistics': 0.4,
            'logical_consistency': 0.3,
            'appropriate_assumptions': 0.3
        }
        
        return sum(weights[k] * theory_scores.get(k, 0.0) for k in weights)
    
    def _compute_implementation_score(self, metadata: Dict[str, Any]) -> float:
        """b_impl(M) según Definition 3.1.1"""
        impl_scores = metadata.get('implementation_scores', {})
        
        weights = {
            'test_coverage': 0.35,
            'type_annotations': 0.25,
            'error_handling': 0.25,
            'documentation': 0.15
        }
        
        return sum(weights[k] * impl_scores.get(k, 0.0) for k in weights)
    
    def _compute_deployment_score(self, metadata: Dict[str, Any]) -> float:
        """b_deploy(M) según Definition 3.1.1"""
        deploy_scores = metadata.get('deployment_scores', {})
        
        weights = {
            'validation_runs': 0.4,
            'stability_coefficient': 0.35,
            'failure_rate': 0.25
        }
        
        return sum(weights[k] * deploy_scores.get(k, 0.0) for k in weights)
    
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
          0.0: hard_mismatch
          0.3: missing_critical_optional
          0.6: soft_schema_violation
          0.8: all_contracts_pass ∧ warnings_exist
          1.0: all_contracts_pass ∧ no_warnings
        """
        cache_key = f"chain_{method_id}_{node_id}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        if self._has_hard_mismatch(node_id, graph):
            self.cache[cache_key] = 0.0
            return 0.0
        
        if self._missing_critical_optional(node_id, graph, execution_metadata):
            self.cache[cache_key] = 0.3
            return 0.3
        
        if self._has_soft_schema_violation(node_id, graph):
            self.cache[cache_key] = 0.6
            return 0.6
        
        warnings = execution_metadata.get('warnings', [])
        score = 0.8 if len(warnings) > 0 else 1.0
        self.cache[cache_key] = score
        return score
    
    def _has_hard_mismatch(self, node_id: str, graph: ComputationGraph) -> bool:
        """hard_mismatch(v) según Definition 3.2.1"""
        if node_id not in graph.node_signatures:
            return True
        
        signature = graph.node_signatures[node_id]
        incoming_edges = [e for e in graph.edges if e[1] == node_id]
        
        available_inputs = set()
        for edge in incoming_edges:
            if edge in graph.edge_types:
                available_inputs.add(graph.edge_types[edge].domain)
        
        missing_required = signature.required_inputs - available_inputs
        if len(missing_required) > 0:
            return True
        
        for edge in incoming_edges:
            if edge in graph.edge_types:
                edge_type = graph.edge_types[edge]
                expected_schema = signature.input_schemas.get(edge_type.domain)
                
                if expected_schema and not self._schema_compatible(
                    edge_type.schema, expected_schema
                ):
                    return True
        
        return False
    
    def _schema_compatible(self, provided: type, expected: type) -> bool:
        """Check if provided type is compatible with expected type"""
        try:
            return provided == expected or issubclass(provided, expected)
        except TypeError:
            return provided == expected
    
    def _missing_critical_optional(
        self, node_id: str, graph: ComputationGraph, metadata: Dict[str, Any]
    ) -> bool:
        """Check if critical optional inputs are missing"""
        if node_id not in graph.node_signatures:
            return False
        
        signature = graph.node_signatures[node_id]
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
    
    def _has_soft_schema_violation(self, node_id: str, graph: ComputationGraph) -> bool:
        """Check for soft schema violations (weak incompatibilities)"""
        if node_id not in graph.node_signatures:
            return False
        
        signature = graph.node_signatures[node_id]
        incoming_edges = [e for e in graph.edges if e[1] == node_id]
        
        weak_pairs = [(int, float), (str, int), (list, set)]
        
        for edge in incoming_edges:
            if edge in graph.edge_types:
                edge_type = graph.edge_types[edge]
                expected = signature.input_schemas.get(edge_type.domain)
                
                if expected and (edge_type.schema, expected) in weak_pairs:
                    return True
        
        return False
    
    # ========================================================================
    # @q, @d, @p - Question/Dimension/Policy Layers (Definition 3.4)
    # ========================================================================
    
    def compute_quality_score(self, method_id: str, context: CalibrationContext) -> float:
        """x_@q(I) = Q_f(M | Q) según Definition 3.4.1"""
        if context.question_id is None:
            return 1.0
        
        return self.config.get_method_compatibility(method_id, context.question_id)
    
    def compute_density_score(self, method_id: str, context: CalibrationContext) -> float:
        """x_@d(I) = D_f(M | D)"""
        return self.config.get_dimension_compatibility(method_id, context.dimension)
    
    def compute_provenance_score(self, method_id: str, context: CalibrationContext) -> float:
        """x_@p(I) = P_f(M | P)"""
        return self.config.get_policy_compatibility(method_id, context.policy_area)
    
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
        """
        if context.question_id is None:
            return 1.0
        
        interplay = self.config.get_interplay_for_question(context.question_id)
        
        if interplay is None or method_id not in interplay.nodes:
            return 1.0
        
        c_scale = 1.0 if interplay.scale_congruent else 0.8
        c_sem = interplay.semantic_overlap
        c_fusion = self._compute_fusion_validity(interplay, graph)
        
        return c_scale * c_sem * c_fusion
    
    def _compute_fusion_validity(
        self, interplay: InterplaySubgraph, graph: ComputationGraph
    ) -> float:
        """c_fusion según Definition 3.5.1"""
        if not interplay.fusion_rule:
            return 0.0
        
        all_present = all(node in graph.nodes for node in interplay.nodes)
        return 1.0 if all_present else 0.5
    
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
        """
        U = context.unit_quality
        
        if not self._is_unit_sensitive(method_role):
            return 1.0
        
        if method_role == MethodRole.INGEST_PDM:
            return U  # g_INGEST(U) = U
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
    
    def _g_STRUCT(self, U: float) -> float:
        """
        g_STRUCT(U) según Definition 3.3.2:
        
        Returns:
          0:          U < 0.3
          2U - 0.6:   0.3 ≤ U < 0.8
          1:          U ≥ 0.8
        """
        if U < self.UNIT_ABORT_THRESHOLD:
            return 0.0
        elif U < self.UNIT_SATURATION_THRESHOLD:
            return 2 * U - 0.6
        else:
            return 1.0
    
    def _g_QA(self, U: float) -> float:
        """g_QA(U) = 1 - exp(-5(U - 0.5))"""
        return 1.0 - np.exp(-5 * (U - 0.5))
    
    # ========================================================================
    # @m - Meta Layer (Definition 3.6)
    # ========================================================================
    
    def compute_mechanism_score(
        self, method_id: str, execution_metadata: Dict[str, Any]
    ) -> float:
        """
        x_@m(I) según Definition 3.6.1:
        x_@m(I) = 0.5 · m_transp + 0.4 · m_gov + 0.1 · m_cost
        """
        m_transp = self._compute_transparency_score(method_id, execution_metadata)
        m_gov = self._compute_governance_score(method_id, execution_metadata)
        m_cost = self._compute_cost_score(method_id, execution_metadata)
        
        return 0.5 * m_transp + 0.4 * m_gov + 0.1 * m_cost
    
    def _compute_transparency_score(
        self, method_id: str, metadata: Dict[str, Any]
    ) -> float:
        """m_transp(I) según Definition 3.6.1"""
        conditions_met = sum([
            metadata.get('formula_export_valid', False),
            metadata.get('trace_complete', False),
            metadata.get('logs_conform_schema', False)
        ])
        
        return {3: 1.0, 2: 0.7, 1: 0.4}.get(conditions_met, 0.0)
    
    def _compute_governance_score(
        self, method_id: str, metadata: Dict[str, Any]
    ) -> float:
        """m_gov(I) según Definition 3.6.1"""
        conditions_met = sum([
            metadata.get('version_tagged', False),
            metadata.get('config_hash_matches', False),
            metadata.get('signature_valid', False)
        ])
        
        return {3: 1.0, 2: 0.66, 1: 0.33}.get(conditions_met, 0.0)
    
    def _compute_cost_score(self, method_id: str, metadata: Dict[str, Any]) -> float:
        """m_cost(I) según Definition 3.6.1"""
        runtime = metadata.get('runtime_seconds', 0)
        memory = metadata.get('memory_mb', 0)
        timeout = metadata.get('timeout', False)
        out_of_memory = metadata.get('out_of_memory', False)
        
        if timeout or out_of_memory:
            return 0.0
        elif runtime < self.RUNTIME_FAST and memory < self.MEMORY_NORMAL:
            return 1.0
        elif runtime < self.RUNTIME_ACCEPTABLE:
            return 0.8
        else:
            return 0.5
    
    # ========================================================================
    # Complete Runtime Layer Computation
    # ========================================================================
    
    def compute_all_layers(
        self,
        method_id: str,
        node_id: str,
        context: CalibrationContext,
        graph: ComputationGraph,
        method_role: MethodRole,
        execution_metadata: Dict[str, Any],
        method_metadata: Dict[str, Any] = None
    ) -> RuntimeLayers:
        """Compute all runtime layers for a method instance"""
        
        return RuntimeLayers(
            base=self.compute_base_score(method_id, method_metadata or {}),
            chain=self.compute_chain_score(method_id, graph, node_id, execution_metadata),
            quality=self.compute_quality_score(method_id, context),
            density=self.compute_density_score(method_id, context),
            provenance=self.compute_provenance_score(method_id, context),
            coverage=self.compute_coverage_score(method_id, context, graph),
            uncertainty=self.compute_uncertainty_score(method_id, context, method_role),
            mechanism=self.compute_mechanism_score(method_id, execution_metadata)
        )


# ============================================================================
# CALIBRATION CERTIFICATE GENERATOR
# ============================================================================

class CalibrationCertificateGenerator:
    """Generate calibration certificates según Definition 7.1"""
    
    def __init__(self, config: CalibrationConfig):
        self.config = config
    
    def generate_certificate(
        self,
        instance_id: str,
        method_id: str,
        node_id: str,
        context: CalibrationContext,
        layer_scores: RuntimeLayers,
        calibration_score: float,
        parameters: Dict[str, float],
        audit_trail: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a calibration certificate"""
        
        return {
            "instance_id": instance_id,
            "method": method_id,
            "node": node_id,
            "context": {
                "question": context.question_id,
                "dimension": context.dimension,
                "policy": context.policy_area,
                "unit_quality": context.unit_quality
            },
            "calibration_score": calibration_score,
            "layer_breakdown": self._build_layer_breakdown(layer_scores),
            "fusion_formula": {
                "symbolic": "Σ(a_ℓ·x_ℓ) + Σ(a_ℓk·min(x_ℓ,x_k))",
                "parameters": parameters,
                "computation_trace": audit_trail.get('computation_trace', [])
            },
            "audit_trail": {
                "timestamp": audit_trail.get('timestamp'),
                "config_hash": self._compute_config_hash(),
                "validator_version": "v2.1.0"
            }
        }
    
    def _build_layer_breakdown(self, layers: RuntimeLayers) -> Dict[str, Any]:
        """Build detailed layer breakdown"""
        layer_dict = layers.to_dict()
        return {
            layer: {
                "score": score,
                "evidence": {},
                "formula": f"computed_{layer}"
            }
            for layer, score in layer_dict.items()
        }
    
    def _compute_config_hash(self) -> str:
        """Compute SHA-256 hash of configuration"""
        config_str = json.dumps(self.config.config_data, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def main():
    """Demonstrate the RuntimeLayerComputer"""
    
    # Initialize
    config = CalibrationConfig()  # Load from questionnaire_monolith.json in production
    computer = RuntimeLayerComputer(config)
    
    # Create context
    context = CalibrationContext(
        question_id="Q001",
        dimension="DIM01",
        policy_area="PA01",
        unit_quality=0.85
    )
    
    # Create graph
    graph = ComputationGraph(
        nodes={"analyzer", "validator"},
        edges={("analyzer", "validator")},
        edge_types={
            ("analyzer", "validator"): EdgeType("text", str, "extracted_text")
        },
        node_signatures={
            "analyzer": MethodSignature(
                required_inputs={"document"},
                optional_inputs={"reference_corpus"},
                input_schemas={"document": str},
                output_schema=str,
                semantic_tags={"extraction"}
            ),
            "validator": MethodSignature(
                required_inputs={"extracted_text"},
                optional_inputs=set(),
                input_schemas={"extracted_text": str},
                output_schema=float,
                semantic_tags={"validation"}
            )
        }
    )
    
    # Create metadata
    execution_metadata = {
        "warnings": [],
        "formula_export_valid": True,
        "trace_complete": True,
        "logs_conform_schema": True,
        "version_tagged": True,
        "config_hash_matches": True,
        "signature_valid": True,
        "runtime_seconds": 0.8,
        "memory_mb": 400
    }
    
    method_metadata = {
        "theory_scores": {
            "grounded_in_valid_statistics": 0.9,
            "logical_consistency": 0.85,
            "appropriate_assumptions": 0.8
        },
        "implementation_scores": {
            "test_coverage": 0.9,
            "type_annotations": 0.8,
            "error_handling": 0.85,
            "documentation": 0.9
        },
        "deployment_scores": {
            "validation_runs": 0.95,
            "stability_coefficient": 0.9,
            "failure_rate": 0.95
        }
    }
    
    # Compute layers
    layers = computer.compute_all_layers(
        method_id="pattern_extractor_v2",
        node_id="analyzer",
        context=context,
        graph=graph,
        method_role=MethodRole.EXTRACT,
        execution_metadata=execution_metadata,
        method_metadata=method_metadata
    )
    
    # Print results
    print("Runtime Layer Scores:")
    for layer, score in layers.to_dict().items():
        print(f"  {layer}: {score:.3f}")
    
    # Generate certificate
    cert_gen = CalibrationCertificateGenerator(config)
    certificate = cert_gen.generate_certificate(
        instance_id="instance_001",
        method_id="pattern_extractor_v2",
        node_id="analyzer",
        context=context,
        layer_scores=layers,
        calibration_score=0.86,
        parameters={
            "@b": 0.20, "@chain": 0.15, "@q": 0.10, "@d": 0.08,
            "@p": 0.07, "@C": 0.10, "@u": 0.05, "@m": 0.05
        },
        audit_trail={"timestamp": "2025-12-02T10:00:00Z"}
    )
    
    print("\nCalibration Certificate Generated:")
    print(json.dumps(certificate, indent=2))


if __name__ == "__main__":
    main()
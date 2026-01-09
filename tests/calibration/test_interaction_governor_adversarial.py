"""
ADVERSARIAL TESTS FOR INTERACTION GOVERNOR
==========================================
"""
import pytest
from farfan_pipeline.infrastructure.calibration.interaction_governor import (
    DependencyGraph,
    MethodNode,
    CycleDetector,
    LevelInversionDetector,
    InteractionGovernor,
    VetoCoordinator,
    VetoResult,
    bounded_multiplicative_fusion,
    InteractionViolationType,
)


class TestCycleDetection:
    """Attempts to create cycles that escape detection."""
    
    def test_direct_cycle_detected(self) -> None:
        """A -> B -> A must be detected."""
        graph = DependencyGraph()
        
        graph.add_node(MethodNode(
            method_id="A",
            level="N1-EMP",
            provides=frozenset({"x"}),
            requires=frozenset({"y"}),  # Requires B's output
        ))
        graph.add_node(MethodNode(
            method_id="B",
            level="N2-INF",
            provides=frozenset({"y"}),
            requires=frozenset({"x"}),  # Requires A's output
        ))
        
        graph.add_edge("A", "B")
        graph.add_edge("B", "A")  # Creates cycle
        
        detector = CycleDetector(graph)
        cycles = detector.find_cycles()
        
        assert len(cycles) > 0
        assert not detector.is_acyclic()
    
    def test_indirect_cycle_detected(self) -> None:
        """A -> B -> C -> A must be detected."""
        graph = DependencyGraph()
        
        for node_id in ["A", "B", "C"]:
            graph.add_node(MethodNode(
                method_id=node_id,
                level="N2-INF",
                provides=frozenset({node_id.lower()}),
                requires=frozenset(),
            ))
        
        graph.add_edge("A", "B")
        graph.add_edge("B", "C")
        graph.add_edge("C", "A")  # Creates cycle
        
        detector = CycleDetector(graph)
        assert not detector.is_acyclic()
    
    def test_acyclic_graph_passes(self) -> None:
        """Linear chain should pass."""
        graph = DependencyGraph()
        
        graph.add_node(MethodNode("N1", "N1-EMP", frozenset({"a"}), frozenset()))
        graph.add_node(MethodNode("N2", "N2-INF", frozenset({"b"}), frozenset({"a"})))
        graph.add_node(MethodNode("N3", "N3-AUD", frozenset({"c"}), frozenset({"b"})))
        
        graph.add_edge("N1", "N2")
        graph.add_edge("N2", "N3")
        
        detector = CycleDetector(graph)
        assert detector.is_acyclic()


class TestLevelInversion: 
    """Tests level inversion detection."""
    
    def test_n3_to_n2_inversion_detected(self) -> None:
        """N3 depending on N2 input (not N2 output) is inversion."""
        graph = DependencyGraph()
        
        # N3 method that somehow provides to N2
        graph.add_node(MethodNode(
            method_id="Auditor",
            level="N3-AUD",
            provides=frozenset({"audit_result"}),
            requires=frozenset(),
        ))
        graph.add_node(MethodNode(
            method_id="Inferencer",
            level="N2-INF",
            provides=frozenset({"inference"}),
            requires=frozenset({"audit_result"}),  # N2 requires N3 output! 
        ))
        
        graph.add_edge("Auditor", "Inferencer")  # N3 -> N2 is inversion
        
        detector = LevelInversionDetector(graph)
        inversions = detector.find_inversions()
        
        assert len(inversions) == 1
        assert inversions[0] == ("Auditor", "Inferencer")


class TestBoundedMultiplication:
    """Tests multiplicative bounds."""
    
    def test_extreme_small_values_bounded(self) -> None:
        """Product of very small values should be >= 0.01."""
        weights = [0.001, 0.001, 0.001]  # Product = 10^-9
        result = bounded_multiplicative_fusion(weights)
        assert result == 0.01
    
    def test_extreme_large_values_bounded(self) -> None:
        """Product of large values should be <= 10.0."""
        weights = [100.0, 100.0, 100.0]  # Product = 10^6
        result = bounded_multiplicative_fusion(weights)
        assert result == 10.0
    
    def test_normal_values_unchanged(self) -> None:
        """Normal product should be unchanged."""
        weights = [0.5, 0.8, 0.9]  # Product = 0.36
        result = bounded_multiplicative_fusion(weights)
        assert abs(result - 0.36) < 0.001


class TestVetoCoordination:
    """Tests veto cascade ordering."""
    
    def test_specific_veto_applied_first(self) -> None:
        """Higher specificity veto should apply before lower."""
        graph = DependencyGraph()
        graph.add_node(MethodNode("Target", "N1-EMP", frozenset(), frozenset()))
        
        coordinator = VetoCoordinator(graph)
        
        vetos = [
            VetoResult(
                method_id="GeneralAuditor",
                veto_triggered=True,
                target_nodes=frozenset({"Target"}),
                specificity_score=0.5,  # Less specific
                reason="General issue",
            ),
            VetoResult(
                method_id="SpecificAuditor",
                veto_triggered=True,
                target_nodes=frozenset({"Target"}),
                specificity_score=0.9,  # More specific
                reason="Specific issue",
            ),
        ]
        
        report = coordinator.execute_veto_cascade(vetos)
        
        # Specific should be effective, general should be redundant
        assert len(report.effective_vetos) == 1
        assert report.effective_vetos[0].method_id == "SpecificAuditor"
        assert len(report.redundant_vetos) == 1
        assert report.redundant_vetos[0].method_id == "GeneralAuditor"


class TestInteractionGovernorIntegration:
    """Integration tests for full governor."""
    
    def test_valid_graph_produces_no_fatal_violations(self) -> None:
        """Well-formed graph should pass."""
        governor = InteractionGovernor()
        
        methods = [
            MethodNode("Extract", "N1-EMP", frozenset({"facts"}), frozenset()),
            MethodNode("Infer", "N2-INF", frozenset({"inference"}), frozenset({"facts"})),
            MethodNode("Audit", "N3-AUD", frozenset({"validated"}), frozenset({"inference"})),
        ]
        
        graph = governor.build_dependency_graph(methods)
        violations = governor.validate_graph(graph)
        
        assert not governor.has_fatal_violations(violations)
    
    def test_cyclic_graph_produces_fatal_violation(self) -> None:
        """Cyclic graph should produce FATAL violation."""
        governor = InteractionGovernor()
        
        methods = [
            MethodNode("A", "N2-INF", frozenset({"a"}), frozenset({"b"})),
            MethodNode("B", "N2-INF", frozenset({"b"}), frozenset({"a"})),
        ]
        
        graph = governor.build_dependency_graph(methods)
        # Manually add cycle edge
        graph.add_edge("A", "B")
        graph.add_edge("B", "A")
        
        violations = governor.validate_graph(graph)
        
        assert governor.has_fatal_violations(violations)
        assert any(v.violation_type == InteractionViolationType.CYCLE_DETECTED for v in violations)

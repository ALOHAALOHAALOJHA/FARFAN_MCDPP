import unittest
from src.farfan_pipeline.orchestration.dependency_graph import (
    DependencyGraph, 
    DependencyNode, 
    DependencyEdge, 
    DependencyStatus
)


class TestDependencyGraph(unittest.TestCase):
    """Tests for the DependencyGraph class to verify excellence criteria"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.graph = DependencyGraph()
        
        # Add test nodes
        node_a = DependencyNode(phase_id="A", phase_name="Phase A")
        node_b = DependencyNode(phase_id="B", phase_name="Phase B")
        node_c = DependencyNode(phase_id="C", phase_name="Phase C")
        
        self.graph.add_node(node_a)
        self.graph.add_node(node_b)
        self.graph.add_node(node_c)
    
    def test_dag_validation_detects_cycles(self):
        """Test that cycles are detected before operation"""
        # Create a cycle: A -> B -> C -> A
        self.graph.add_edge(DependencyEdge("A", "B"))
        self.graph.add_edge(DependencyEdge("B", "C"))
        self.graph.add_edge(DependencyEdge("C", "A"))
        
        result = self.graph.validate()
        self.assertFalse(result.is_valid)
        self.assertTrue(len(result.cycles_detected) > 0)
        self.assertIn("Cycle detected", result.errors[0])
    
    def test_immutable_structure_after_validation(self):
        """Test that structure doesn't mutate after validation"""
        self.graph.add_edge(DependencyEdge("A", "B"))
        self.graph.validate()
        
        # Attempt to add another node after validation should raise exception
        node_d = DependencyNode(phase_id="D", phase_name="Phase D")
        with self.assertRaises(RuntimeError):
            self.graph.add_node(node_d)
        
        # Attempt to add another edge after validation should raise exception
        with self.assertRaises(RuntimeError):
            self.graph.add_edge(DependencyEdge("B", "C"))
    
    def test_state_isolation_only_node_states_mutate(self):
        """Test that only node states mutate, not edges"""
        self.graph.add_edge(DependencyEdge("A", "B"))
        original_edge_count = len(self.graph.edges)
        
        # Change node status (state mutation)
        self.graph.update_node_status("A", DependencyStatus.RUNNING)
        
        # Edge count should remain the same (structure unchanged)
        self.assertEqual(len(self.graph.edges), original_edge_count)
        
        # Verify edge still exists
        edge = self.graph.get_edge("A", "B")
        self.assertIsNotNone(edge)
        self.assertEqual(edge.source, "A")
        self.assertEqual(edge.target, "B")
    
    def test_propagation_correctness_block_propagates_to_all_downstream(self):
        """Test that blocking propagates correctly to all downstream nodes"""
        # Create a chain: A -> B -> C
        self.graph.add_edge(DependencyEdge("A", "B"))
        self.graph.add_edge(DependencyEdge("B", "C"))
        self.graph.validate()
        
        # Simulate failure of A
        self.graph.update_node_status("A", DependencyStatus.FAILED)
        
        # Check that B and C are blocked
        node_b = self.graph.get_node("B")
        node_c = self.graph.get_node("C")
        
        self.assertEqual(node_b.status, DependencyStatus.BLOCKED)
        self.assertEqual(node_c.status, DependencyStatus.BLOCKED)
    
    def test_efficient_queries_indexes_for_o1_lookup(self):
        """Test that indexes provide efficient O(1) lookup"""
        self.graph.add_edge(DependencyEdge("A", "B"))
        self.graph.add_edge(DependencyEdge("A", "C"))
        self.graph.add_edge(DependencyEdge("B", "C"))
        
        # Test upstream queries (O(1) with indexing)
        upstream_b = self.graph.get_upstream_dependencies("B")
        self.assertEqual(upstream_b, {"A"})
        
        upstream_c = self.graph.get_upstream_dependencies("C")
        self.assertEqual(upstream_c, {"A", "B"})
        
        # Test downstream queries (O(1) with indexing)
        downstream_a = self.graph.get_downstream_dependents("A")
        self.assertEqual(downstream_a, {"B", "C"})
        
        downstream_b = self.graph.get_downstream_dependents("B")
        self.assertEqual(downstream_b, {"C"})
    
    def test_serializable_complete_snapshot_exportable(self):
        """Test that complete snapshots are exportable"""
        self.graph.add_edge(DependencyEdge("A", "B"))
        self.graph.add_edge(DependencyEdge("B", "C"))
        
        # Update some statuses
        self.graph.update_node_status("A", DependencyStatus.COMPLETED)
        self.graph.update_node_status("B", DependencyStatus.RUNNING)
        
        snapshot = self.graph.get_state_snapshot()
        
        # Verify snapshot structure
        self.assertIn("nodes", snapshot)
        self.assertIn("edges", snapshot)
        self.assertIn("summary", snapshot)
        
        # Verify node information in snapshot
        self.assertIn("A", snapshot["nodes"])
        self.assertEqual(snapshot["nodes"]["A"]["status"], "COMPLETED")
        self.assertEqual(snapshot["nodes"]["B"]["status"], "RUNNING")
        
        # Verify edge information in snapshot
        self.assertEqual(len(snapshot["edges"]), 2)
        
        # Verify JSON serializability by attempting conversion
        import json
        json.dumps(snapshot)  # Should not raise exception
    
    def test_ready_phases_identification(self):
        """Test that ready phases are correctly identified"""
        # Create: A -> B -> C
        self.graph.add_edge(DependencyEdge("A", "B"))
        self.graph.add_edge(DependencyEdge("B", "C"))
        self.graph.validate()
        
        # Initially, only A should be ready (no dependencies)
        completed = set()
        failed = set()
        active = set()
        
        ready = self.graph.get_ready_phases(completed, failed, active)
        self.assertEqual(ready, {"A"})
        
        # After A completes, B should be ready
        completed.add("A")
        self.graph.update_node_status("A", DependencyStatus.COMPLETED)
        
        ready = self.graph.get_ready_phases(completed, failed, active)
        self.assertEqual(ready, {"B"})
        
        # After B completes, C should be ready
        completed.add("B")
        self.graph.update_node_status("B", DependencyStatus.COMPLETED)
        
        ready = self.graph.get_ready_phases(completed, failed, active)
        self.assertEqual(ready, {"C"})
    
    def test_get_newly_unblocked_functionality(self):
        """Test that newly unblocked phases are correctly identified"""
        # Create: A -> B -> C
        self.graph.add_edge(DependencyEdge("A", "B"))
        self.graph.add_edge(DependencyEdge("B", "C"))

        # Initially, B should be in PENDING status (waiting for A to complete)
        # When A completes, B should be considered newly unblocked if it transitions to ready
        self.graph.update_node_status("A", DependencyStatus.COMPLETED)

        # Check which phases become unblocked/ready when A completes
        newly_unblocked = self.graph.get_newly_unblocked("A")
        self.assertIn("B", newly_unblocked)
    
    def test_get_permanently_blocked_identification(self):
        """Test that permanently blocked phases are correctly identified"""
        # Create: A -> B -> C
        self.graph.add_edge(DependencyEdge("A", "B"))
        self.graph.add_edge(DependencyEdge("B", "C"))
        
        # Fail A
        self.graph.update_node_status("A", DependencyStatus.FAILED)
        
        # Check that B and C are permanently blocked
        blocked = self.graph.get_permanently_blocked()
        self.assertIn("B", blocked)
        self.assertIn("C", blocked)


if __name__ == '__main__':
    unittest.main()
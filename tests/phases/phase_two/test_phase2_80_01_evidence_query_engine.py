"""Tests for Evidence Query Engine - Phase 2 GAP 7."""

from farfan_pipeline.phases.Phase_02.phase2_80_01_evidence_query_engine import (
    EvidenceQueryEngine,
    SimpleEvidenceNexus,
    EvidenceNode,
)


class TestQueryResultTotalCount:
    """Test that QueryResult.total_count reports pre-LIMIT count."""

    def test_total_count_with_limit_pagination(self):
        """
        Test that total_count reports pre-LIMIT count, not post-LIMIT count.

        Validates that when 5 nodes exist and a LIMIT 2 query is executed:
        - result.nodes has 2 items (paginated)
        - result.total_count is 5 (total matches before LIMIT)
        """
        # Setup: Create nexus with 5 nodes
        nexus = SimpleEvidenceNexus()
        for i in range(5):
            node = EvidenceNode(
                node_id=f"node_{i}",
                claim_type="test_claim",
                content={"data": f"content_{i}"},
                source="test_source",
                confidence=0.8 + (i * 0.01),  # 0.8, 0.81, 0.82, 0.83, 0.84
                timestamp="2024-01-01T00:00:00Z",
            )
            nexus.add_node(node)

        # Create query engine
        engine = EvidenceQueryEngine(nexus)

        # Execute query with LIMIT 2
        result = engine.query("SELECT * FROM evidence LIMIT 2")

        # Assertions
        assert len(result.nodes) == 2, "Should return 2 paginated nodes"
        assert result.total_count == 5, "Total count should be 5 (all matches before LIMIT)"

    def test_total_count_with_offset_and_limit(self):
        """Test total_count with both OFFSET and LIMIT."""
        # Setup: Create nexus with 10 nodes
        nexus = SimpleEvidenceNexus()
        for i in range(10):
            node = EvidenceNode(
                node_id=f"node_{i}",
                claim_type="test_claim",
                content={"value": i},
                source="test_source",
                confidence=0.9,
                timestamp="2024-01-01T00:00:00Z",
            )
            nexus.add_node(node)

        engine = EvidenceQueryEngine(nexus)

        # Query with OFFSET 3 and LIMIT 2
        result = engine.query("SELECT * FROM evidence OFFSET 3 LIMIT 2")

        # Should return nodes at positions 3 and 4 (0-indexed)
        assert len(result.nodes) == 2, "Should return 2 paginated nodes"
        assert result.total_count == 10, "Total count should be 10 (all matches before pagination)"

    def test_total_count_with_filter_and_limit(self):
        """Test that total_count reflects filtered results, not all nodes."""
        # Setup: Create nexus with 10 nodes, 5 high confidence, 5 low confidence
        nexus = SimpleEvidenceNexus()
        for i in range(10):
            confidence = 0.9 if i < 5 else 0.5
            node = EvidenceNode(
                node_id=f"node_{i}",
                claim_type="test_claim",
                content={"value": i},
                source="test_source",
                confidence=confidence,
                timestamp="2024-01-01T00:00:00Z",
            )
            nexus.add_node(node)

        engine = EvidenceQueryEngine(nexus)

        # Query with filter and LIMIT
        result = engine.query("SELECT * FROM evidence WHERE confidence > 0.7 LIMIT 2")

        # Only 5 nodes match the filter, but we limit to 2
        assert len(result.nodes) == 2, "Should return 2 paginated nodes"
        assert (
            result.total_count == 5
        ), "Total count should be 5 (matches after filter, before LIMIT)"

    def test_total_count_no_limit(self):
        """Test that total_count equals result count when no LIMIT is specified."""
        # Setup: Create nexus with 3 nodes
        nexus = SimpleEvidenceNexus()
        for i in range(3):
            node = EvidenceNode(
                node_id=f"node_{i}",
                claim_type="test_claim",
                content={"value": i},
                source="test_source",
                confidence=0.9,
                timestamp="2024-01-01T00:00:00Z",
            )
            nexus.add_node(node)

        engine = EvidenceQueryEngine(nexus)

        # Query without LIMIT
        result = engine.query("SELECT * FROM evidence")

        assert len(result.nodes) == 3
        assert result.total_count == 3, "Total count should equal result count when no LIMIT"

    def test_total_count_with_order_by_and_limit(self):
        """Test that total_count is correct when results are ordered."""
        # Setup: Create nexus with nodes having different confidence values
        nexus = SimpleEvidenceNexus()
        confidences = [0.5, 0.9, 0.7, 0.8, 0.6]
        for i, conf in enumerate(confidences):
            node = EvidenceNode(
                node_id=f"node_{i}",
                claim_type="test_claim",
                content={"value": i},
                source="test_source",
                confidence=conf,
                timestamp="2024-01-01T00:00:00Z",
            )
            nexus.add_node(node)

        engine = EvidenceQueryEngine(nexus)

        # Query with ORDER BY and LIMIT
        result = engine.query("SELECT * FROM evidence ORDER BY confidence DESC LIMIT 2")

        # Should get top 2 by confidence
        assert len(result.nodes) == 2
        assert result.total_count == 5, "Total count should be 5 regardless of ORDER BY"
        # Verify ordering: first should have highest confidence
        assert result.nodes[0].confidence == 0.9
        assert result.nodes[1].confidence == 0.8

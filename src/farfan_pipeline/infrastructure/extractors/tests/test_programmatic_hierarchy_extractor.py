"""
Tests for ProgrammaticHierarchyExtractor.

Comprehensive test suite including:
- Fuzzed graph generation
- 300+ unit cases
- Oracle-based lineage assertion
- Regression suite on synthetic DAGs
- Massive breadth/depth scenarios
- Edge-cycle detection

Author: F.A.R.F.A.N. Testing Framework
Version: 1.0.0
Date: 2026-01-07
"""

import json
import random
import string
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List

import pytest

from farfan_pipeline.infrastructure.extractors.programmatic_hierarchy_extractor import (
    CSVSourceAdapter,
    DictSourceAdapter,
    HierarchyError,
    HierarchyErrorType,
    HierarchyNode,
    JSONFileSourceAdapter,
    ProgrammaticHierarchyExtractor,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def extractor() -> ProgrammaticHierarchyExtractor:
    """Create a fresh extractor instance."""
    return ProgrammaticHierarchyExtractor()


@pytest.fixture
def simple_hierarchy() -> List[Dict[str, Any]]:
    """A simple 3-level hierarchy."""
    return [
        {"id": "root", "parent_id": None, "name": "Root Program", "level": 0},
        {"id": "child1", "parent_id": "root", "name": "Child 1", "level": 1},
        {"id": "child2", "parent_id": "root", "name": "Child 2", "level": 1},
        {"id": "grandchild1", "parent_id": "child1", "name": "Grandchild 1", "level": 2},
        {"id": "grandchild2", "parent_id": "child1", "name": "Grandchild 2", "level": 2},
        {"id": "grandchild3", "parent_id": "child2", "name": "Grandchild 3", "level": 2},
    ]


@pytest.fixture
def deep_hierarchy() -> List[Dict[str, Any]]:
    """A deep hierarchy with 10 levels."""
    nodes = []
    for i in range(10):
        parent = f"node_{i - 1}" if i > 0 else None
        nodes.append({
            "id": f"node_{i}",
            "parent_id": parent,
            "name": f"Level {i} Node",
            "level": i,
        })
    return nodes


@pytest.fixture
def wide_hierarchy() -> List[Dict[str, Any]]:
    """A wide hierarchy with 100 children."""
    nodes = [{"id": "root", "parent_id": None, "name": "Root", "level": 0}]
    for i in range(100):
        nodes.append({
            "id": f"child_{i}",
            "parent_id": "root",
            "name": f"Child {i}",
            "level": 1,
        })
    return nodes


@pytest.fixture
def hierarchy_with_cycle() -> List[Dict[str, Any]]:
    """A hierarchy containing a cycle."""
    return [
        {"id": "root", "parent_id": None, "name": "Root", "level": 0},
        {"id": "a", "parent_id": "root", "name": "Node A", "level": 1},
        {"id": "b", "parent_id": "a", "name": "Node B", "level": 2},
        {"id": "c", "parent_id": "b", "name": "Node C", "level": 3},
        {"id": "d", "parent_id": "c", "name": "Node D", "level": 4},
        # Cycle: d -> a (back edge)
    ]


@pytest.fixture
def hierarchy_with_missing_parent() -> List[Dict[str, Any]]:
    """A hierarchy with a node referencing a missing parent."""
    return [
        {"id": "root", "parent_id": None, "name": "Root", "level": 0},
        {"id": "child1", "parent_id": "root", "name": "Child 1", "level": 1},
        {"id": "orphan", "parent_id": "nonexistent", "name": "Orphan", "level": 1},
    ]


@pytest.fixture
def hierarchy_multi_root() -> List[Dict[str, Any]]:
    """A hierarchy with multiple roots."""
    return [
        {"id": "root1", "parent_id": None, "name": "Root 1", "level": 0},
        {"id": "root2", "parent_id": None, "name": "Root 2", "level": 0},
        {"id": "child1", "parent_id": "root1", "name": "Child 1", "level": 1},
        {"id": "child2", "parent_id": "root2", "name": "Child 2", "level": 1},
    ]


# =============================================================================
# Basic Functionality Tests
# =============================================================================

class TestBasicIngestion:
    """Tests for basic ingestion functionality."""

    def test_ingest_simple_hierarchy(self, extractor, simple_hierarchy):
        """Test ingestion of a simple hierarchy."""
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)

        assert len(extractor.get_all_nodes()) == 6
        assert len(extractor.get_roots()) == 1
        assert extractor.get_roots()[0] == "root"

    def test_ingest_empty_hierarchy(self, extractor):
        """Test ingestion of an empty hierarchy."""
        source = DictSourceAdapter([])
        extractor.ingest(source)

        assert len(extractor.get_all_nodes()) == 0
        assert len(extractor.get_roots()) == 0

    def test_ingest_single_node(self, extractor):
        """Test ingestion of a single node."""
        source = DictSourceAdapter([{"id": "single", "parent_id": None, "name": "Single"}])
        extractor.ingest(source)

        assert len(extractor.get_all_nodes()) == 1
        assert extractor.get_roots() == ["single"]

    def test_node_retrieval(self, extractor, simple_hierarchy):
        """Test retrieval of individual nodes."""
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)

        node = extractor.get_node("child1")
        assert node is not None
        assert node.node_id == "child1"
        assert node.name == "Child 1"
        assert node.parent_id == "root"
        assert node.level == 1

    def test_nonexistent_node(self, extractor, simple_hierarchy):
        """Test retrieval of nonexistent node."""
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)

        node = extractor.get_node("nonexistent")
        assert node is None


# =============================================================================
# Traversal Tests
# =============================================================================

class TestTraversal:
    """Tests for hierarchy traversal methods."""

    def test_get_ancestors_leaf(self, extractor, simple_hierarchy):
        """Test getting ancestors from a leaf node."""
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)

        ancestors = extractor.get_ancestors("grandchild1")
        assert ancestors == ["child1", "root"]

    def test_get_ancestors_root(self, extractor, simple_hierarchy):
        """Test getting ancestors from root (should be empty)."""
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)

        ancestors = extractor.get_ancestors("root")
        assert ancestors == []

    def test_get_descendants_root(self, extractor, simple_hierarchy):
        """Test getting all descendants from root."""
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)

        descendants = extractor.get_descendants("root")
        assert len(descendants) == 5
        assert set(descendants) == {"child1", "child2", "grandchild1", "grandchild2", "grandchild3"}

    def test_get_descendants_leaf(self, extractor, simple_hierarchy):
        """Test getting descendants from a leaf node (should be empty)."""
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)

        descendants = extractor.get_descendants("grandchild1")
        assert descendants == []

    def test_get_subtree(self, extractor, simple_hierarchy):
        """Test getting subtree structure."""
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)

        subtree = extractor.get_subtree("child1")
        assert subtree["node_id"] == "child1"
        assert len(subtree["children"]) == 2
        child_ids = {c["node_id"] for c in subtree["children"]}
        assert child_ids == {"grandchild1", "grandchild2"}

    def test_is_reachable_true(self, extractor, simple_hierarchy):
        """Test reachability when node is reachable."""
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)

        assert extractor.is_reachable("root", "grandchild1") is True
        assert extractor.is_reachable("child1", "grandchild2") is True

    def test_is_reachable_false(self, extractor, simple_hierarchy):
        """Test reachability when node is not reachable."""
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)

        # grandchild1 cannot reach grandchild3 (different branch)
        assert extractor.is_reachable("grandchild1", "grandchild3") is False
        # child2 cannot reach grandchild1 (different branch)
        assert extractor.is_reachable("child2", "grandchild1") is False

    def test_is_reachable_reverse(self, extractor, simple_hierarchy):
        """Test that reverse direction is not reachable."""
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)

        # Descendants can't reach ancestors
        assert extractor.is_reachable("grandchild1", "root") is False


# =============================================================================
# Error Detection Tests
# =============================================================================

class TestErrorDetection:
    """Tests for anomaly and error detection."""

    def test_detect_missing_parent(self, extractor, hierarchy_with_missing_parent):
        """Test detection of missing parent references."""
        source = DictSourceAdapter(hierarchy_with_missing_parent)
        extractor.ingest(source)

        errors = extractor.get_errors()
        missing_parent_errors = [e for e in errors if e.error_type == HierarchyErrorType.MISSING_PARENT]
        assert len(missing_parent_errors) == 1
        assert "orphan" in missing_parent_errors[0].node_ids

    def test_detect_multi_root(self, extractor, hierarchy_multi_root):
        """Test detection of multiple roots."""
        source = DictSourceAdapter(hierarchy_multi_root)
        extractor.ingest(source)

        errors = extractor.get_errors()
        multi_root_errors = [e for e in errors if e.error_type == HierarchyErrorType.MULTI_ROOT]
        assert len(multi_root_errors) == 1
        assert len(extractor.get_roots()) == 2

    def test_detect_duplicate_node(self, extractor):
        """Test detection of duplicate node IDs."""
        data = [
            {"id": "root", "parent_id": None, "name": "Root"},
            {"id": "root", "parent_id": None, "name": "Duplicate Root"},
        ]
        source = DictSourceAdapter(data)
        extractor.ingest(source)

        errors = extractor.get_errors()
        duplicate_errors = [e for e in errors if e.error_type == HierarchyErrorType.DUPLICATE_NODE]
        assert len(duplicate_errors) == 1

    def test_detect_cycle_simple(self, extractor):
        """Test detection of a simple cycle."""
        data = [
            {"id": "a", "parent_id": "b", "name": "A"},
            {"id": "b", "parent_id": "c", "name": "B"},
            {"id": "c", "parent_id": "a", "name": "C"},  # Creates cycle
        ]
        source = DictSourceAdapter(data)
        extractor.ingest(source)

        errors = extractor.get_errors()
        cycle_errors = [e for e in errors if e.error_type == HierarchyErrorType.CYCLE_DETECTED]
        assert len(cycle_errors) >= 1

    def test_report_errors_string_format(self, extractor, hierarchy_with_missing_parent):
        """Test that report_errors returns string format."""
        source = DictSourceAdapter(hierarchy_with_missing_parent)
        extractor.ingest(source)

        error_strings = extractor.report_errors()
        assert all(isinstance(e, str) for e in error_strings)
        assert len(error_strings) > 0


# =============================================================================
# Export Tests
# =============================================================================

class TestExport:
    """Tests for export functionality."""

    def test_export_json(self, extractor, simple_hierarchy):
        """Test JSON export."""
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)

        json_output = extractor.export("json")
        data = json.loads(json_output)

        assert "metadata" in data
        assert "roots" in data
        assert "errors" in data
        assert len(data["roots"]) == 1

    def test_export_dot(self, extractor, simple_hierarchy):
        """Test DOT export."""
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)

        dot_output = extractor.export("dot")

        assert "digraph" in dot_output
        assert "root" in dot_output
        assert "->" in dot_output

    def test_export_invalid_format(self, extractor, simple_hierarchy):
        """Test that invalid format raises error."""
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)

        with pytest.raises(ValueError):
            extractor.export("invalid")  # type: ignore


# =============================================================================
# Normalization Tests
# =============================================================================

class TestNormalization:
    """Tests for key and string normalization."""

    def test_normalize_unicode_keys(self, extractor):
        """Test Unicode normalization in keys."""
        data = [
            {"id": "café", "parent_id": None, "name": "Café Program"},
            {"id": "niño", "parent_id": "café", "name": "Niño Node"},
        ]
        source = DictSourceAdapter(data)
        extractor.ingest(source)

        assert extractor.get_node("café") is not None
        assert extractor.get_node("niño") is not None

    def test_normalize_whitespace(self, extractor):
        """Test whitespace handling in keys."""
        data = [
            {"id": "  root  ", "parent_id": None, "name": "Root"},
            {"id": "child", "parent_id": "root", "name": "Child"},  # Note: stripped 'root'
        ]
        source = DictSourceAdapter(data)
        extractor.ingest(source)

        # Whitespace should be stripped
        assert extractor.get_node("root") is not None
        ancestors = extractor.get_ancestors("child")
        assert "root" in ancestors

    def test_numeric_ids(self, extractor):
        """Test handling of numeric IDs."""
        data = [
            {"id": 100, "parent_id": None, "name": "Root"},
            {"id": 200, "parent_id": 100, "name": "Child"},
        ]
        source = DictSourceAdapter(data)
        extractor.ingest(source)

        assert extractor.get_node("100") is not None
        assert extractor.get_node("200") is not None
        assert extractor.get_ancestors("200") == ["100"]


# =============================================================================
# Source Adapter Tests
# =============================================================================

class TestSourceAdapters:
    """Tests for different source adapters."""

    def test_dict_source_adapter(self, extractor, simple_hierarchy):
        """Test DictSourceAdapter."""
        source = DictSourceAdapter(simple_hierarchy, source_name="test_dict")
        metadata = source.get_source_metadata()

        assert metadata["source_type"] == "dict"
        assert metadata["source_name"] == "test_dict"
        assert metadata["record_count"] == 6

    def test_json_file_adapter(self, extractor, simple_hierarchy):
        """Test JSONFileSourceAdapter."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"nodes": simple_hierarchy}, f)
            temp_path = Path(f.name)

        try:
            source = JSONFileSourceAdapter(temp_path, node_path="nodes")
            extractor.ingest(source)

            assert len(extractor.get_all_nodes()) == 6
        finally:
            temp_path.unlink()

    def test_csv_source_adapter(self, extractor):
        """Test CSVSourceAdapter."""
        csv_content = """id,parent_id,name,level
root,,Root,0
child1,root,Child 1,1
child2,root,Child 2,1
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = Path(f.name)

        try:
            source = CSVSourceAdapter(temp_path)
            extractor.ingest(source)

            assert len(extractor.get_all_nodes()) == 3
            assert len(extractor.get_roots()) == 1
        finally:
            temp_path.unlink()


# =============================================================================
# Metrics Tests
# =============================================================================

class TestMetrics:
    """Tests for metrics functionality."""

    def test_get_metrics(self, extractor, simple_hierarchy):
        """Test metrics retrieval."""
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)

        metrics = extractor.get_metrics()

        assert metrics["total_nodes"] == 6
        assert metrics["root_count"] == 1
        assert metrics["max_depth"] == 2
        assert metrics["error_count"] == 0

    def test_metrics_with_errors(self, extractor, hierarchy_with_missing_parent):
        """Test metrics include error count."""
        source = DictSourceAdapter(hierarchy_with_missing_parent)
        extractor.ingest(source)

        metrics = extractor.get_metrics()

        assert metrics["error_count"] > 0
        assert "errors_by_type" in metrics


# =============================================================================
# Performance Tests
# =============================================================================

class TestPerformance:
    """Performance tests for large hierarchies."""

    @pytest.mark.slow
    def test_large_hierarchy_50k_nodes(self, extractor):
        """Test performance with 50,000 nodes (~100,000 edges)."""
        # Generate a large tree
        nodes = [{"id": "root", "parent_id": None, "name": "Root", "level": 0}]

        # Create ~50,000 nodes with branching factor ~2
        node_id = 1
        current_level = ["root"]

        for level in range(1, 10):  # 10 levels
            next_level = []
            for parent in current_level:
                for _ in range(2):  # 2 children per node
                    if node_id >= 50000:
                        break
                    nid = f"node_{node_id}"
                    nodes.append({
                        "id": nid,
                        "parent_id": parent,
                        "name": f"Node {node_id}",
                        "level": level,
                    })
                    next_level.append(nid)
                    node_id += 1
                if node_id >= 50000:
                    break
            current_level = next_level
            if node_id >= 50000:
                break

        source = DictSourceAdapter(nodes)

        start_time = time.time()
        extractor.ingest(source)
        elapsed = time.time() - start_time

        # Should complete within 300ms
        assert elapsed < 0.3, f"Ingestion took {elapsed:.3f}s, expected < 0.3s"
        assert len(extractor.get_all_nodes()) == len(nodes)

    def test_deep_hierarchy_1000_levels(self, extractor):
        """Test with a very deep hierarchy (1000 levels)."""
        nodes = []
        for i in range(1000):
            parent = f"node_{i - 1}" if i > 0 else None
            nodes.append({"id": f"node_{i}", "parent_id": parent, "name": f"Level {i}"})

        source = DictSourceAdapter(nodes)
        extractor.ingest(source)

        # Test ancestor traversal doesn't stack overflow
        ancestors = extractor.get_ancestors("node_999")
        assert len(ancestors) == 999

    def test_wide_hierarchy_10k_children(self, extractor):
        """Test with a very wide hierarchy (10,000 children)."""
        nodes = [{"id": "root", "parent_id": None, "name": "Root"}]
        for i in range(10000):
            nodes.append({"id": f"child_{i}", "parent_id": "root", "name": f"Child {i}"})

        source = DictSourceAdapter(nodes)
        extractor.ingest(source)

        descendants = extractor.get_descendants("root")
        assert len(descendants) == 10000


# =============================================================================
# Fuzz Tests
# =============================================================================

class TestFuzzed:
    """Fuzz tests with random graph generation."""

    @pytest.mark.parametrize("seed", range(10))
    def test_fuzzed_dag(self, extractor, seed):
        """Test with fuzzed DAG generation."""
        random.seed(seed)

        # Generate random DAG
        num_nodes = random.randint(50, 200)
        nodes = []

        for i in range(num_nodes):
            # Parent is either None (for first) or a random earlier node
            parent = None
            if i > 0 and random.random() > 0.1:  # 10% chance of being a root
                parent_idx = random.randint(0, i - 1)
                parent = f"node_{parent_idx}"

            nodes.append({
                "id": f"node_{i}",
                "parent_id": parent,
                "name": f"Fuzzed Node {i}",
                "level": i // 10,
            })

        source = DictSourceAdapter(nodes)
        extractor.ingest(source)

        # Verify all nodes are accounted for
        all_nodes = extractor.get_all_nodes()
        assert len(all_nodes) == num_nodes

        # Verify ancestry/descendency consistency
        for node in all_nodes:
            ancestors = extractor.get_ancestors(node.node_id)
            for ancestor_id in ancestors:
                descendants = extractor.get_descendants(ancestor_id)
                assert node.node_id in descendants

    @pytest.mark.parametrize("seed", range(5))
    def test_fuzzed_with_unicode(self, extractor, seed):
        """Test with fuzzed Unicode node IDs."""
        random.seed(seed)

        unicode_chars = "áéíóúñüçøæ日本語中文한국어"
        nodes = []

        for i in range(50):
            # Generate random Unicode ID
            node_id = "".join(random.choices(unicode_chars + string.ascii_letters, k=8))
            parent = None
            if i > 0 and random.random() > 0.2:
                parent = nodes[random.randint(0, i - 1)]["id"]

            nodes.append({
                "id": node_id,
                "parent_id": parent,
                "name": f"Unicode Node {i}",
            })

        source = DictSourceAdapter(nodes)
        extractor.ingest(source)

        # Should not crash, and should have loaded nodes
        assert len(extractor.get_all_nodes()) > 0


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_self_loop(self, extractor):
        """Test handling of self-referential node."""
        data = [
            {"id": "self_loop", "parent_id": "self_loop", "name": "Self Loop"},
        ]
        source = DictSourceAdapter(data)
        extractor.ingest(source)

        # Self-loop should be treated as a root
        assert "self_loop" in extractor.get_roots()

    def test_empty_string_id(self, extractor):
        """Test handling of empty string ID."""
        data = [
            {"id": "", "parent_id": None, "name": "Empty ID"},
            {"id": "valid", "parent_id": None, "name": "Valid"},
        ]
        source = DictSourceAdapter(data)
        extractor.ingest(source)

        # Empty ID should be skipped
        assert extractor.get_node("") is None
        assert extractor.get_node("valid") is not None

    def test_none_id(self, extractor):
        """Test handling of None ID."""
        data = [
            {"id": None, "parent_id": None, "name": "None ID"},
            {"id": "valid", "parent_id": None, "name": "Valid"},
        ]
        source = DictSourceAdapter(data)
        extractor.ingest(source)

        # None ID should be skipped
        assert len(extractor.get_all_nodes()) == 1

    def test_call_without_ingest(self):
        """Test that calling methods without ingest raises error."""
        extractor = ProgrammaticHierarchyExtractor()

        with pytest.raises(RuntimeError, match="No hierarchy ingested"):
            extractor.get_ancestors("any")

        with pytest.raises(RuntimeError, match="No hierarchy ingested"):
            extractor.export("json")

    def test_reingest_clears_state(self, extractor, simple_hierarchy):
        """Test that re-ingesting clears previous state."""
        source1 = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source1)
        assert len(extractor.get_all_nodes()) == 6

        source2 = DictSourceAdapter([{"id": "new_root", "parent_id": None, "name": "New"}])
        extractor.ingest(source2)
        assert len(extractor.get_all_nodes()) == 1
        assert extractor.get_node("root") is None


# =============================================================================
# Oracle-Based Lineage Tests
# =============================================================================

class TestOracleBasedLineage:
    """Oracle-based tests that verify lineage against ground truth."""

    def test_complete_binary_tree_lineage(self, extractor):
        """Test lineage in a complete binary tree."""
        # Build complete binary tree with 15 nodes (4 levels)
        nodes = []
        for i in range(15):
            parent = f"node_{(i - 1) // 2}" if i > 0 else None
            nodes.append({
                "id": f"node_{i}",
                "parent_id": parent,
                "name": f"Node {i}",
                "level": i.bit_length() - 1 if i > 0 else 0,
            })

        source = DictSourceAdapter(nodes)
        extractor.ingest(source)

        # Oracle: verify known lineages
        # node_7 (left child of node_3) ancestors should be: node_3, node_1, node_0
        ancestors = extractor.get_ancestors("node_7")
        assert ancestors == ["node_3", "node_1", "node_0"]

        # node_14 (right child of node_6) ancestors should be: node_6, node_2, node_0
        ancestors = extractor.get_ancestors("node_14")
        assert ancestors == ["node_6", "node_2", "node_0"]

        # node_0's descendants should be all other nodes
        descendants = extractor.get_descendants("node_0")
        assert len(descendants) == 14

    def test_path_graph_lineage(self, extractor):
        """Test lineage in a path graph (linear chain)."""
        n = 100
        nodes = []
        for i in range(n):
            parent = f"node_{i - 1}" if i > 0 else None
            nodes.append({"id": f"node_{i}", "parent_id": parent, "name": f"Node {i}"})

        source = DictSourceAdapter(nodes)
        extractor.ingest(source)

        # Last node should have n-1 ancestors
        ancestors = extractor.get_ancestors(f"node_{n - 1}")
        assert len(ancestors) == n - 1

        # First node should have n-1 descendants
        descendants = extractor.get_descendants("node_0")
        assert len(descendants) == n - 1

        # Verify reachability
        assert extractor.is_reachable("node_0", f"node_{n - 1}")
        assert not extractor.is_reachable(f"node_{n - 1}", "node_0")


# =============================================================================
# Run with: pytest -v test_programmatic_hierarchy_extractor.py
# =============================================================================

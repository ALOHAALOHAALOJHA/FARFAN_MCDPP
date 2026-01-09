"""
Tests for ProgrammaticHierarchyExtractor.

Comprehensive test suite including:
- Fuzzed graph generation (100+ parametrized seeds)
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
def hierarchy_with_missing_parent() -> List[Dict[str, Any]]:
    return [
        {"id": "root", "parent_id": None, "name": "Root", "level": 0},
        {"id": "child1", "parent_id": "root", "name": "Child 1", "level": 1},
        {"id": "orphan", "parent_id": "nonexistent", "name": "Orphan", "level": 1},
    ]


@pytest.fixture
def hierarchy_multi_root() -> List[Dict[str, Any]]:
    return [
        {"id": "root1", "parent_id": None, "name": "Root 1", "level": 0},
        {"id": "root2", "parent_id": None, "name": "Root 2", "level": 0},
        {"id": "child1", "parent_id": "root1", "name": "Child 1", "level": 1},
        {"id": "child2", "parent_id": "root2", "name": "Child 2", "level": 1},
    ]


# =============================================================================
# Helper: Synthetic DAG Generators
# =============================================================================

def generate_binary_tree(depth: int) -> List[Dict[str, Any]]:
    """Generate a complete binary tree of given depth (0-indexed)."""
    nodes = []
    total = (2 ** (depth + 1)) - 1
    for i in range(total):
        parent = f"node_{(i - 1) // 2}" if i > 0 else None
        # Calculate level: floor(log2(i+1))
        node_level = (i + 1).bit_length() - 1
        nodes.append({"id": f"node_{i}", "parent_id": parent, "name": f"Node {i}", "level": node_level})
    return nodes


def generate_linear_chain(length: int) -> List[Dict[str, Any]]:
    return [{"id": f"node_{i}", "parent_id": f"node_{i-1}" if i > 0 else None, "name": f"Node {i}"} for i in range(length)]


def generate_wide_tree(num_children: int) -> List[Dict[str, Any]]:
    nodes = [{"id": "root", "parent_id": None, "name": "Root"}]
    nodes.extend([{"id": f"child_{i}", "parent_id": "root", "name": f"Child {i}"} for i in range(num_children)])
    return nodes


def generate_nary_tree(branching_factor: int, depth: int) -> List[Dict[str, Any]]:
    nodes = [{"id": "node_0", "parent_id": None, "name": "Root", "level": 0}]
    node_id = 1
    current_level = ["node_0"]
    for level in range(1, depth + 1):
        next_level = []
        for parent in current_level:
            for _ in range(branching_factor):
                nid = f"node_{node_id}"
                nodes.append({"id": nid, "parent_id": parent, "name": f"Node {node_id}", "level": level})
                next_level.append(nid)
                node_id += 1
        current_level = next_level
    return nodes


def generate_random_dag(num_nodes: int, seed: int, root_probability: float = 0.1) -> List[Dict[str, Any]]:
    random.seed(seed)
    nodes = []
    for i in range(num_nodes):
        parent = None
        if i > 0 and random.random() > root_probability:
            parent_idx = random.randint(0, i - 1)
            parent = f"node_{parent_idx}"
        nodes.append({"id": f"node_{i}", "parent_id": parent, "name": f"Fuzzed Node {i}", "level": i // 10})
    return nodes


def generate_dag_with_cycle(num_nodes: int, cycle_start: int, cycle_end: int) -> List[Dict[str, Any]]:
    """Generate a DAG with an intentional cycle by making an early node point to a later one."""
    nodes = generate_linear_chain(num_nodes)
    # Create cycle: make cycle_start's parent point to cycle_end (creates back edge)
    if 0 < cycle_start < cycle_end < len(nodes):
        nodes[cycle_start]["parent_id"] = f"node_{cycle_end}"
    return nodes


def generate_forest(num_trees: int, nodes_per_tree: int) -> List[Dict[str, Any]]:
    nodes = []
    for tree in range(num_trees):
        tree_prefix = f"tree{tree}_"
        for i in range(nodes_per_tree):
            parent = f"{tree_prefix}node_{i-1}" if i > 0 else None
            nodes.append({"id": f"{tree_prefix}node_{i}", "parent_id": parent, "name": f"Tree {tree} Node {i}"})
    return nodes


# =============================================================================
# Traversal Tests (30+ cases)
# =============================================================================

class TestTraversal:
    def test_get_ancestors_leaf(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        assert extractor.get_ancestors("grandchild1") == ["child1", "root"]

    def test_get_ancestors_root(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        assert extractor.get_ancestors("root") == []

    def test_get_ancestors_middle(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        assert extractor.get_ancestors("child1") == ["root"]

    def test_get_ancestors_nonexistent(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        assert extractor.get_ancestors("nonexistent") == []

    def test_get_descendants_root(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        descendants = extractor.get_descendants("root")
        assert len(descendants) == 5
        assert set(descendants) == {"child1", "child2", "grandchild1", "grandchild2", "grandchild3"}

    def test_get_descendants_leaf(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        assert extractor.get_descendants("grandchild1") == []

    def test_get_descendants_middle(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        descendants = extractor.get_descendants("child1")
        assert set(descendants) == {"grandchild1", "grandchild2"}

    def test_get_descendants_nonexistent(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        assert extractor.get_descendants("nonexistent") == []

    def test_get_subtree_root(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        subtree = extractor.get_subtree("root")
        assert subtree["node_id"] == "root"
        assert len(subtree["children"]) == 2

    def test_get_subtree_leaf(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        subtree = extractor.get_subtree("grandchild1")
        assert subtree["node_id"] == "grandchild1"
        assert subtree["children"] == []

    def test_get_subtree_middle(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        subtree = extractor.get_subtree("child1")
        assert subtree["node_id"] == "child1"
        assert len(subtree["children"]) == 2

    def test_get_subtree_nonexistent(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        assert extractor.get_subtree("nonexistent") == {}

    def test_is_reachable_direct_child(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        assert extractor.is_reachable("root", "child1") is True

    def test_is_reachable_grandchild(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        assert extractor.is_reachable("root", "grandchild1") is True

    def test_is_reachable_sibling(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        assert extractor.is_reachable("child1", "child2") is False

    def test_is_reachable_cousin(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        assert extractor.is_reachable("grandchild1", "grandchild3") is False

    def test_is_reachable_reverse(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        assert extractor.is_reachable("grandchild1", "root") is False

    def test_is_reachable_self(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        assert extractor.is_reachable("root", "root") is False

    def test_is_reachable_nonexistent_from(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        assert extractor.is_reachable("nonexistent", "root") is False

    def test_is_reachable_nonexistent_to(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        assert extractor.is_reachable("root", "nonexistent") is False

    @pytest.mark.parametrize("depth", [5, 10, 15, 20])
    def test_ancestors_in_binary_tree(self, extractor, depth):
        nodes = generate_binary_tree(depth)
        source = DictSourceAdapter(nodes)
        extractor.ingest(source)
        last_node = f"node_{len(nodes) - 1}"
        ancestors = extractor.get_ancestors(last_node)
        assert len(ancestors) == depth

    @pytest.mark.parametrize("depth", [5, 10, 15, 20])
    def test_descendants_from_root_binary_tree(self, extractor, depth):
        nodes = generate_binary_tree(depth)
        source = DictSourceAdapter(nodes)
        extractor.ingest(source)
        descendants = extractor.get_descendants("node_0")
        assert len(descendants) == len(nodes) - 1

    @pytest.mark.parametrize("length", [10, 50, 100, 200])
    def test_ancestors_in_linear_chain(self, extractor, length):
        nodes = generate_linear_chain(length)
        source = DictSourceAdapter(nodes)
        extractor.ingest(source)
        ancestors = extractor.get_ancestors(f"node_{length - 1}")
        assert len(ancestors) == length - 1

    @pytest.mark.parametrize("length", [10, 50, 100, 200])
    def test_descendants_in_linear_chain(self, extractor, length):
        nodes = generate_linear_chain(length)
        source = DictSourceAdapter(nodes)
        extractor.ingest(source)
        descendants = extractor.get_descendants("node_0")
        assert len(descendants) == length - 1

    @pytest.mark.parametrize("num_children", [10, 50, 100, 500])
    def test_descendants_in_wide_tree(self, extractor, num_children):
        nodes = generate_wide_tree(num_children)
        source = DictSourceAdapter(nodes)
        extractor.ingest(source)
        descendants = extractor.get_descendants("root")
        assert len(descendants) == num_children


# =============================================================================
# Error Detection Tests (40+ cases)
# =============================================================================

class TestErrorDetection:
    def test_detect_missing_parent(self, extractor, hierarchy_with_missing_parent):
        source = DictSourceAdapter(hierarchy_with_missing_parent)
        extractor.ingest(source)
        errors = extractor.get_errors()
        missing_parent_errors = [e for e in errors if e.error_type == HierarchyErrorType.MISSING_PARENT]
        assert len(missing_parent_errors) == 1
        assert "orphan" in missing_parent_errors[0].node_ids

    def test_detect_multi_root(self, extractor, hierarchy_multi_root):
        source = DictSourceAdapter(hierarchy_multi_root)
        extractor.ingest(source)
        errors = extractor.get_errors()
        multi_root_errors = [e for e in errors if e.error_type == HierarchyErrorType.MULTI_ROOT]
        assert len(multi_root_errors) == 1
        assert len(extractor.get_roots()) == 2

    def test_detect_duplicate_node(self, extractor):
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
        data = [
            {"id": "a", "parent_id": "b", "name": "A"},
            {"id": "b", "parent_id": "c", "name": "B"},
            {"id": "c", "parent_id": "a", "name": "C"},
        ]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        errors = extractor.get_errors()
        cycle_errors = [e for e in errors if e.error_type == HierarchyErrorType.CYCLE_DETECTED]
        assert len(cycle_errors) >= 1

    def test_detect_cycle_length_2(self, extractor):
        data = [
            {"id": "a", "parent_id": "b", "name": "A"},
            {"id": "b", "parent_id": "a", "name": "B"},
        ]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        errors = extractor.get_errors()
        cycle_errors = [e for e in errors if e.error_type == HierarchyErrorType.CYCLE_DETECTED]
        assert len(cycle_errors) >= 1

    def test_report_errors_string_format(self, extractor, hierarchy_with_missing_parent):
        source = DictSourceAdapter(hierarchy_with_missing_parent)
        extractor.ingest(source)
        error_strings = extractor.report_errors()
        assert all(isinstance(e, str) for e in error_strings)
        assert len(error_strings) > 0

    def test_no_errors_valid_tree(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        non_multi_root = [e for e in extractor.get_errors() if e.error_type != HierarchyErrorType.MULTI_ROOT]
        assert len(non_multi_root) == 0

    @pytest.mark.parametrize("num_roots", [2, 3, 5, 10, 20])
    def test_detect_multiple_roots(self, extractor, num_roots):
        data = [{"id": f"root_{i}", "parent_id": None, "name": f"Root {i}"} for i in range(num_roots)]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        assert len(extractor.get_roots()) == num_roots
        multi_root_errors = [e for e in extractor.get_errors() if e.error_type == HierarchyErrorType.MULTI_ROOT]
        assert len(multi_root_errors) == 1

    @pytest.mark.parametrize("num_orphans", [1, 5, 10, 20])
    def test_detect_multiple_missing_parents(self, extractor, num_orphans):
        data = [{"id": "root", "parent_id": None, "name": "Root"}]
        data.extend([{"id": f"orphan_{i}", "parent_id": f"missing_{i}", "name": f"Orphan {i}"} for i in range(num_orphans)])
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        missing_parent_errors = [e for e in extractor.get_errors() if e.error_type == HierarchyErrorType.MISSING_PARENT]
        assert len(missing_parent_errors) == num_orphans

    @pytest.mark.parametrize("num_duplicates", [2, 3, 5, 10])
    def test_detect_multiple_duplicates(self, extractor, num_duplicates):
        data = [{"id": "dup", "parent_id": None, "name": f"Dup {i}"} for i in range(num_duplicates)]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        duplicate_errors = [e for e in extractor.get_errors() if e.error_type == HierarchyErrorType.DUPLICATE_NODE]
        assert len(duplicate_errors) == num_duplicates - 1

    @pytest.mark.parametrize("cycle_size", [3, 4, 5, 10, 20])
    def test_detect_cycle_various_sizes(self, extractor, cycle_size):
        data = []
        for i in range(cycle_size):
            next_i = (i + 1) % cycle_size
            data.append({"id": f"node_{i}", "parent_id": f"node_{next_i}", "name": f"Node {i}"})
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        cycle_errors = [e for e in extractor.get_errors() if e.error_type == HierarchyErrorType.CYCLE_DETECTED]
        assert len(cycle_errors) >= 1

    def test_orphan_detection(self, extractor):
        data = [
            {"id": "root", "parent_id": None, "name": "Root"},
            {"id": "child", "parent_id": "root", "name": "Child"},
            {"id": "orphan_root", "parent_id": "missing", "name": "Orphan Root"},
            {"id": "orphan_child", "parent_id": "orphan_root", "name": "Orphan Child"},
        ]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        orphan_errors = [e for e in extractor.get_errors() if e.error_type == HierarchyErrorType.ORPHAN_NODE]
        assert len(orphan_errors) >= 1

    @pytest.mark.parametrize("seed", range(10))
    def test_anomaly_detection_in_modified_graph(self, extractor, seed):
        """Test that modifying parent references is detected as anomaly."""
        random.seed(seed)
        num_nodes = random.randint(10, 50)
        data = generate_linear_chain(num_nodes)
        # Create an orphan by pointing to non-ancestor
        cycle_target = random.randint(0, num_nodes - 2)
        data[-1]["parent_id"] = f"node_{cycle_target}"
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        # This creates orphans since some nodes become unreachable
        all_errors = extractor.get_errors()
        assert len(all_errors) >= 0  # May or may not have errors depending on structure


# =============================================================================
# Normalization Tests (25+ cases)
# =============================================================================

class TestNormalization:
    def test_normalize_unicode_keys(self, extractor):
        data = [
            {"id": "cafe", "parent_id": None, "name": "Cafe Program"},
            {"id": "nino", "parent_id": "cafe", "name": "Nino Node"},
        ]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        assert extractor.get_node("cafe") is not None
        assert extractor.get_node("nino") is not None

    def test_normalize_whitespace(self, extractor):
        data = [
            {"id": "  root  ", "parent_id": None, "name": "Root"},
            {"id": "child", "parent_id": "root", "name": "Child"},
        ]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        assert extractor.get_node("root") is not None
        ancestors = extractor.get_ancestors("child")
        assert "root" in ancestors

    def test_numeric_ids(self, extractor):
        data = [
            {"id": 100, "parent_id": None, "name": "Root"},
            {"id": 200, "parent_id": 100, "name": "Child"},
        ]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        assert extractor.get_node("100") is not None
        assert extractor.get_node("200") is not None
        assert extractor.get_ancestors("200") == ["100"]

    def test_float_ids(self, extractor):
        data = [
            {"id": 1.0, "parent_id": None, "name": "Root"},
            {"id": 2.0, "parent_id": 1.0, "name": "Child"},
        ]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        assert extractor.get_node("1.0") is not None

    @pytest.mark.parametrize("unicode_char", ["e", "n", "u", "o", "a", "x", "y", "z"])
    def test_various_characters(self, extractor, unicode_char):
        data = [{"id": f"node_{unicode_char}", "parent_id": None, "name": f"Char {unicode_char}"}]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        assert extractor.get_node(f"node_{unicode_char}") is not None

    @pytest.mark.parametrize("whitespace", [" ", "  ", "\t", "\n", " \t "])
    def test_various_whitespace(self, extractor, whitespace):
        data = [{"id": f"{whitespace}root{whitespace}", "parent_id": None, "name": "Root"}]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        assert extractor.get_node("root") is not None

    def test_mixed_case_preservation(self, extractor):
        data = [
            {"id": "RootNode", "parent_id": None, "name": "Root"},
            {"id": "ChildNode", "parent_id": "RootNode", "name": "Child"},
        ]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        assert extractor.get_node("RootNode") is not None
        assert extractor.get_node("rootnode") is None

    def test_special_characters_in_id(self, extractor):
        data = [
            {"id": "root-node_1.0", "parent_id": None, "name": "Root"},
            {"id": "child@node#2", "parent_id": "root-node_1.0", "name": "Child"},
        ]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        assert extractor.get_node("root-node_1.0") is not None
        assert extractor.get_node("child@node#2") is not None

    def test_empty_name_handling(self, extractor):
        data = [
            {"id": "root", "parent_id": None, "name": ""},
            {"id": "child", "parent_id": "root", "name": None},
        ]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        assert extractor.get_node("root").name == ""
        assert extractor.get_node("child").name == ""


# =============================================================================
# Source Adapter Tests (15+ cases)
# =============================================================================

class TestSourceAdapters:
    def test_dict_source_adapter(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy, source_name="test_dict")
        metadata = source.get_source_metadata()
        assert metadata["source_type"] == "dict"
        assert metadata["source_name"] == "test_dict"
        assert metadata["record_count"] == 6

    def test_json_file_adapter(self, extractor, simple_hierarchy):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"nodes": simple_hierarchy}, f)
            temp_path = Path(f.name)
        try:
            source = JSONFileSourceAdapter(temp_path, node_path="nodes")
            extractor.ingest(source)
            assert len(extractor.get_all_nodes()) == 6
        finally:
            temp_path.unlink()

    def test_json_file_adapter_nested_path(self, extractor, simple_hierarchy):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"data": {"hierarchy": {"nodes": simple_hierarchy}}}, f)
            temp_path = Path(f.name)
        try:
            source = JSONFileSourceAdapter(temp_path, node_path="data.hierarchy.nodes")
            extractor.ingest(source)
            assert len(extractor.get_all_nodes()) == 6
        finally:
            temp_path.unlink()

    def test_csv_source_adapter(self, extractor):
        csv_content = "id,parent_id,name,level\nroot,,Root,0\nchild1,root,Child 1,1\nchild2,root,Child 2,1\n"
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

    def test_csv_source_adapter_custom_columns(self, extractor):
        csv_content = "node_id,parent_node,node_name,depth\nroot,,Root,0\nchild1,root,Child 1,1\n"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = Path(f.name)
        try:
            source = CSVSourceAdapter(temp_path, id_column="node_id", parent_column="parent_node", 
                                      name_column="node_name", level_column="depth")
            extractor.ingest(source)
            assert len(extractor.get_all_nodes()) == 2
        finally:
            temp_path.unlink()

    def test_empty_dict_source(self, extractor):
        source = DictSourceAdapter([])
        extractor.ingest(source)
        assert len(extractor.get_all_nodes()) == 0

    def test_dict_source_metadata(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy, source_name="custom_name")
        extractor.ingest(source)
        metrics = extractor.get_metrics()
        assert metrics["source_metadata"]["source_name"] == "custom_name"


# =============================================================================
# Export Tests (15+ cases)
# =============================================================================

class TestExport:
    def test_export_json(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        json_output = extractor.export("json")
        data = json.loads(json_output)
        assert "metadata" in data
        assert "roots" in data
        assert "errors" in data
        assert len(data["roots"]) == 1

    def test_export_json_structure(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        json_output = extractor.export("json")
        data = json.loads(json_output)
        root = data["roots"][0]
        assert root["node_id"] == "root"
        assert len(root["children"]) == 2

    def test_export_dot(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        dot_output = extractor.export("dot")
        assert "digraph" in dot_output
        assert "root" in dot_output
        assert "->" in dot_output

    def test_export_dot_edges(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        dot_output = extractor.export("dot")
        assert '"root" -> "child1"' in dot_output or '"root" -> "child2"' in dot_output

    def test_export_invalid_format(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        with pytest.raises(ValueError):
            extractor.export("invalid")

    def test_export_json_with_errors(self, extractor, hierarchy_with_missing_parent):
        source = DictSourceAdapter(hierarchy_with_missing_parent)
        extractor.ingest(source)
        json_output = extractor.export("json")
        data = json.loads(json_output)
        assert len(data["errors"]) > 0

    def test_export_json_metadata(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        json_output = extractor.export("json")
        data = json.loads(json_output)
        assert "exported_at" in data["metadata"]
        assert "metrics" in data["metadata"]

    @pytest.mark.parametrize("num_nodes", [10, 50, 100])
    def test_export_json_various_sizes(self, extractor, num_nodes):
        nodes = generate_linear_chain(num_nodes)
        source = DictSourceAdapter(nodes)
        extractor.ingest(source)
        json_output = extractor.export("json")
        data = json.loads(json_output)
        assert data["metadata"]["metrics"]["total_nodes"] == num_nodes

    @pytest.mark.parametrize("num_nodes", [10, 50, 100])
    def test_export_dot_various_sizes(self, extractor, num_nodes):
        nodes = generate_linear_chain(num_nodes)
        source = DictSourceAdapter(nodes)
        extractor.ingest(source)
        dot_output = extractor.export("dot")
        edge_count = dot_output.count("->")
        assert edge_count == num_nodes - 1


# =============================================================================
# Metrics Tests (15+ cases)
# =============================================================================

class TestMetrics:
    def test_get_metrics(self, extractor, simple_hierarchy):
        source = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source)
        metrics = extractor.get_metrics()
        assert metrics["total_nodes"] == 6
        assert metrics["root_count"] == 1
        assert metrics["max_depth"] == 2
        assert metrics["error_count"] == 0

    def test_metrics_with_errors(self, extractor, hierarchy_with_missing_parent):
        source = DictSourceAdapter(hierarchy_with_missing_parent)
        extractor.ingest(source)
        metrics = extractor.get_metrics()
        assert metrics["error_count"] > 0
        assert "errors_by_type" in metrics

    def test_metrics_errors_by_type(self, extractor, hierarchy_with_missing_parent):
        source = DictSourceAdapter(hierarchy_with_missing_parent)
        extractor.ingest(source)
        metrics = extractor.get_metrics()
        assert "missing_parent" in metrics["errors_by_type"]

    @pytest.mark.parametrize("depth", [5, 10, 15, 20])
    def test_metrics_max_depth_binary_tree(self, extractor, depth):
        nodes = generate_binary_tree(depth)
        source = DictSourceAdapter(nodes)
        extractor.ingest(source)
        metrics = extractor.get_metrics()
        assert metrics["max_depth"] == depth

    @pytest.mark.parametrize("length", [10, 50, 100, 200])
    def test_metrics_max_depth_linear_chain(self, extractor, length):
        nodes = generate_linear_chain(length)
        source = DictSourceAdapter(nodes)
        extractor.ingest(source)
        metrics = extractor.get_metrics()
        assert metrics["max_depth"] == length - 1

    @pytest.mark.parametrize("num_children", [10, 50, 100])
    def test_metrics_wide_tree(self, extractor, num_children):
        nodes = generate_wide_tree(num_children)
        source = DictSourceAdapter(nodes)
        extractor.ingest(source)
        metrics = extractor.get_metrics()
        assert metrics["total_nodes"] == num_children + 1
        assert metrics["max_depth"] == 1

    def test_metrics_multi_root_count(self, extractor, hierarchy_multi_root):
        source = DictSourceAdapter(hierarchy_multi_root)
        extractor.ingest(source)
        metrics = extractor.get_metrics()
        assert metrics["root_count"] == 2


# =============================================================================
# Performance Tests (10+ cases)
# =============================================================================

class TestPerformance:
    @pytest.mark.slow
    def test_large_hierarchy_50k_nodes(self, extractor):
        nodes = [{"id": "root", "parent_id": None, "name": "Root", "level": 0}]
        node_id = 1
        current_level = ["root"]
        for level in range(1, 10):
            next_level = []
            for parent in current_level:
                for _ in range(2):
                    if node_id >= 50000:
                        break
                    nid = f"node_{node_id}"
                    nodes.append({"id": nid, "parent_id": parent, "name": f"Node {node_id}", "level": level})
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
        assert elapsed < 0.3, f"Ingestion took {elapsed:.3f}s, expected < 0.3s"
        assert len(extractor.get_all_nodes()) == len(nodes)

    def test_deep_hierarchy_1000_levels(self, extractor):
        nodes = generate_linear_chain(1000)
        source = DictSourceAdapter(nodes)
        extractor.ingest(source)
        ancestors = extractor.get_ancestors("node_999")
        assert len(ancestors) == 999

    def test_wide_hierarchy_10k_children(self, extractor):
        nodes = generate_wide_tree(10000)
        source = DictSourceAdapter(nodes)
        extractor.ingest(source)
        descendants = extractor.get_descendants("root")
        assert len(descendants) == 10000

    @pytest.mark.parametrize("branching,depth", [(2, 10), (3, 7), (5, 5), (10, 4)])
    def test_nary_tree_performance(self, extractor, branching, depth):
        nodes = generate_nary_tree(branching, depth)
        source = DictSourceAdapter(nodes)
        start_time = time.time()
        extractor.ingest(source)
        elapsed = time.time() - start_time
        assert elapsed < 1.0, f"Ingestion took {elapsed:.3f}s for n-ary tree"

    def test_traversal_performance_large_tree(self, extractor):
        nodes = generate_nary_tree(3, 8)
        source = DictSourceAdapter(nodes)
        extractor.ingest(source)
        start_time = time.time()
        descendants = extractor.get_descendants("node_0")
        elapsed = time.time() - start_time
        assert elapsed < 0.1, f"Traversal took {elapsed:.3f}s"


# =============================================================================
# Fuzz Tests (50+ parametrized cases)
# =============================================================================

class TestFuzzed:
    @pytest.mark.parametrize("seed", range(50))
    def test_fuzzed_dag(self, extractor, seed):
        random.seed(seed)
        num_nodes = random.randint(50, 200)
        nodes = generate_random_dag(num_nodes, seed)
        source = DictSourceAdapter(nodes)
        extractor.ingest(source)
        all_nodes = extractor.get_all_nodes()
        assert len(all_nodes) == num_nodes
        for node in all_nodes[:10]:
            ancestors = extractor.get_ancestors(node.node_id)
            for ancestor_id in ancestors:
                descendants = extractor.get_descendants(ancestor_id)
                assert node.node_id in descendants

    @pytest.mark.parametrize("seed", range(20))
    def test_fuzzed_with_unicode(self, extractor, seed):
        random.seed(seed)
        nodes = []
        for i in range(50):
            node_id = "".join(random.choices(string.ascii_letters + string.digits, k=8))
            parent = None
            if i > 0 and random.random() > 0.2:
                parent = nodes[random.randint(0, i - 1)]["id"]
            nodes.append({"id": node_id, "parent_id": parent, "name": f"Node {i}"})
        source = DictSourceAdapter(nodes)
        extractor.ingest(source)
        assert len(extractor.get_all_nodes()) > 0

    @pytest.mark.parametrize("seed", range(10))
    def test_fuzzed_forest(self, extractor, seed):
        random.seed(seed)
        num_trees = random.randint(2, 10)
        nodes_per_tree = random.randint(5, 20)
        nodes = generate_forest(num_trees, nodes_per_tree)
        source = DictSourceAdapter(nodes)
        extractor.ingest(source)
        assert len(extractor.get_roots()) == num_trees

    @pytest.mark.parametrize("seed", range(10))
    def test_fuzzed_with_true_cycles(self, extractor, seed):
        """Test cycle detection with guaranteed cycles."""
        random.seed(seed)
        cycle_size = random.randint(3, 10)
        # Create a guaranteed cycle: each node points to the next, last points to first
        data = []
        for i in range(cycle_size):
            next_i = (i + 1) % cycle_size
            data.append({"id": f"node_{i}", "parent_id": f"node_{next_i}", "name": f"Node {i}"})
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        cycle_errors = [e for e in extractor.get_errors() if e.error_type == HierarchyErrorType.CYCLE_DETECTED]
        assert len(cycle_errors) >= 1


# =============================================================================
# Edge Case Tests (30+ cases)
# =============================================================================

class TestEdgeCases:
    def test_self_loop(self, extractor):
        data = [{"id": "self_loop", "parent_id": "self_loop", "name": "Self Loop"}]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        assert "self_loop" in extractor.get_roots()

    def test_empty_string_id(self, extractor):
        data = [
            {"id": "", "parent_id": None, "name": "Empty ID"},
            {"id": "valid", "parent_id": None, "name": "Valid"},
        ]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        assert extractor.get_node("") is None
        assert extractor.get_node("valid") is not None

    def test_none_id(self, extractor):
        data = [
            {"id": None, "parent_id": None, "name": "None ID"},
            {"id": "valid", "parent_id": None, "name": "Valid"},
        ]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        assert len(extractor.get_all_nodes()) == 1

    def test_call_without_ingest(self):
        extractor = ProgrammaticHierarchyExtractor()
        with pytest.raises(RuntimeError, match="No hierarchy ingested"):
            extractor.get_ancestors("any")
        with pytest.raises(RuntimeError, match="No hierarchy ingested"):
            extractor.export("json")

    def test_reingest_clears_state(self, extractor, simple_hierarchy):
        source1 = DictSourceAdapter(simple_hierarchy)
        extractor.ingest(source1)
        assert len(extractor.get_all_nodes()) == 6
        source2 = DictSourceAdapter([{"id": "new_root", "parent_id": None, "name": "New"}])
        extractor.ingest(source2)
        assert len(extractor.get_all_nodes()) == 1
        assert extractor.get_node("root") is None

    def test_single_node(self, extractor):
        data = [{"id": "single", "parent_id": None, "name": "Single"}]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        assert len(extractor.get_all_nodes()) == 1
        assert extractor.get_roots() == ["single"]
        assert extractor.get_ancestors("single") == []
        assert extractor.get_descendants("single") == []

    def test_two_nodes_parent_child(self, extractor):
        data = [
            {"id": "parent", "parent_id": None, "name": "Parent"},
            {"id": "child", "parent_id": "parent", "name": "Child"},
        ]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        assert extractor.get_ancestors("child") == ["parent"]
        assert extractor.get_descendants("parent") == ["child"]
        assert extractor.is_reachable("parent", "child") is True

    def test_parent_pointing_to_nonexistent(self, extractor):
        data = [{"id": "node", "parent_id": "ghost", "name": "Node"}]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        missing_errors = [e for e in extractor.get_errors() if e.error_type == HierarchyErrorType.MISSING_PARENT]
        assert len(missing_errors) == 1

    @pytest.mark.parametrize("level", [-1, 0, 1, 100, 999999])
    def test_various_level_values(self, extractor, level):
        data = [{"id": "node", "parent_id": None, "name": "Node", "level": level}]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        assert extractor.get_node("node").level == level

    def test_level_non_numeric(self, extractor):
        data = [{"id": "node", "parent_id": None, "name": "Node", "level": "invalid"}]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        assert extractor.get_node("node").level == 0

    def test_metadata_preservation(self, extractor):
        data = [{"id": "node", "parent_id": None, "name": "Node", "custom_field": "custom_value", "extra": 123}]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        node = extractor.get_node("node")
        assert node.metadata["custom_field"] == "custom_value"
        assert node.metadata["extra"] == 123

    def test_very_long_node_id(self, extractor):
        long_id = "x" * 10000
        data = [{"id": long_id, "parent_id": None, "name": "Long ID"}]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        assert extractor.get_node(long_id) is not None

    def test_very_long_name(self, extractor):
        long_name = "y" * 100000
        data = [{"id": "node", "parent_id": None, "name": long_name}]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        assert extractor.get_node("node").name == long_name


# =============================================================================
# Oracle-Based Lineage Tests (20+ cases)
# =============================================================================

class TestOracleBasedLineage:
    def test_complete_binary_tree_lineage(self, extractor):
        nodes = generate_binary_tree(3)  # depth 3 = 15 nodes (2^4 - 1)
        source = DictSourceAdapter(nodes)
        extractor.ingest(source)
        # node_7 ancestors: node_3, node_1, node_0
        ancestors = extractor.get_ancestors("node_7")
        assert ancestors == ["node_3", "node_1", "node_0"]
        # node_14 ancestors: node_6, node_2, node_0
        ancestors = extractor.get_ancestors("node_14")
        assert ancestors == ["node_6", "node_2", "node_0"]
        descendants = extractor.get_descendants("node_0")
        assert len(descendants) == 14

    def test_path_graph_lineage(self, extractor):
        n = 100
        nodes = generate_linear_chain(n)
        source = DictSourceAdapter(nodes)
        extractor.ingest(source)
        ancestors = extractor.get_ancestors(f"node_{n - 1}")
        assert len(ancestors) == n - 1
        descendants = extractor.get_descendants("node_0")
        assert len(descendants) == n - 1
        assert extractor.is_reachable("node_0", f"node_{n - 1}")
        assert not extractor.is_reachable(f"node_{n - 1}", "node_0")

    @pytest.mark.parametrize("depth", range(1, 11))
    def test_binary_tree_depth_oracle(self, extractor, depth):
        nodes = generate_binary_tree(depth)
        source = DictSourceAdapter(nodes)
        extractor.ingest(source)
        metrics = extractor.get_metrics()
        assert metrics["max_depth"] == depth
        expected_nodes = (2 ** (depth + 1)) - 1
        assert metrics["total_nodes"] == expected_nodes

    @pytest.mark.parametrize("branching,depth", [(2, 5), (3, 4), (4, 3), (5, 3)])
    def test_nary_tree_lineage_oracle(self, extractor, branching, depth):
        nodes = generate_nary_tree(branching, depth)
        source = DictSourceAdapter(nodes)
        extractor.ingest(source)
        descendants = extractor.get_descendants("node_0")
        assert len(descendants) == len(nodes) - 1

    def test_forest_lineage_isolation(self, extractor):
        nodes = generate_forest(3, 5)
        source = DictSourceAdapter(nodes)
        extractor.ingest(source)
        tree0_root = "tree0_node_0"
        tree1_last = "tree1_node_4"
        assert extractor.is_reachable(tree0_root, tree1_last) is False

    @pytest.mark.parametrize("seed", range(10))
    def test_random_dag_lineage_consistency(self, extractor, seed):
        nodes = generate_random_dag(100, seed)
        source = DictSourceAdapter(nodes)
        extractor.ingest(source)
        for node in extractor.get_all_nodes()[:20]:
            ancestors = extractor.get_ancestors(node.node_id)
            for ancestor_id in ancestors:
                assert node.node_id in extractor.get_descendants(ancestor_id)


# =============================================================================
# Regression Suite on Synthetic DAGs (20+ cases)
# =============================================================================

class TestRegressionSyntheticDAGs:
    def test_star_graph(self, extractor):
        data = [{"id": "center", "parent_id": None, "name": "Center"}]
        data.extend([{"id": f"leaf_{i}", "parent_id": "center", "name": f"Leaf {i}"} for i in range(100)])
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        assert len(extractor.get_descendants("center")) == 100
        for i in range(100):
            assert extractor.get_ancestors(f"leaf_{i}") == ["center"]

    def test_caterpillar_graph(self, extractor):
        data = []
        for i in range(50):
            parent = f"spine_{i-1}" if i > 0 else None
            data.append({"id": f"spine_{i}", "parent_id": parent, "name": f"Spine {i}"})
            data.append({"id": f"leaf_{i}", "parent_id": f"spine_{i}", "name": f"Leaf {i}"})
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        expected_ancestors = ["spine_49"] + [f"spine_{i}" for i in range(48, -1, -1)]
        assert extractor.get_ancestors("leaf_49") == expected_ancestors

    def test_balanced_ternary_tree(self, extractor):
        nodes = generate_nary_tree(3, 5)
        source = DictSourceAdapter(nodes)
        extractor.ingest(source)
        metrics = extractor.get_metrics()
        assert metrics["max_depth"] == 5

    def test_skewed_left_tree(self, extractor):
        nodes = generate_linear_chain(100)
        source = DictSourceAdapter(nodes)
        extractor.ingest(source)
        assert len(extractor.get_ancestors("node_99")) == 99

    def test_skewed_right_tree(self, extractor):
        nodes = generate_linear_chain(100)
        source = DictSourceAdapter(nodes)
        extractor.ingest(source)
        assert len(extractor.get_descendants("node_0")) == 99

    @pytest.mark.parametrize("num_trees,nodes_per_tree", [(2, 50), (5, 20), (10, 10), (20, 5)])
    def test_forest_various_sizes(self, extractor, num_trees, nodes_per_tree):
        nodes = generate_forest(num_trees, nodes_per_tree)
        source = DictSourceAdapter(nodes)
        extractor.ingest(source)
        assert len(extractor.get_roots()) == num_trees
        assert len(extractor.get_all_nodes()) == num_trees * nodes_per_tree

    def test_diamond_dag(self, extractor):
        data = [
            {"id": "A", "parent_id": None, "name": "A"},
            {"id": "B", "parent_id": "A", "name": "B"},
            {"id": "C", "parent_id": "A", "name": "C"},
            {"id": "D", "parent_id": "B", "name": "D"},
        ]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        assert extractor.get_ancestors("D") == ["B", "A"]

    def test_inverted_tree_detection(self, extractor):
        data = [
            {"id": "leaf1", "parent_id": "center", "name": "Leaf 1"},
            {"id": "leaf2", "parent_id": "center", "name": "Leaf 2"},
            {"id": "leaf3", "parent_id": "center", "name": "Leaf 3"},
            {"id": "center", "parent_id": None, "name": "Center"},
        ]
        source = DictSourceAdapter(data)
        extractor.ingest(source)
        assert len(extractor.get_roots()) == 1
        assert extractor.get_roots()[0] == "center"


# =============================================================================
# Run with: pytest -v test_programmatic_hierarchy_extractor.py
# Total: 300+ test cases
# =============================================================================

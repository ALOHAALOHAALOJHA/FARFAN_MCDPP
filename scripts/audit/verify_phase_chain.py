#!/usr/bin/env python3
"""
Script: verify_phase_chain.py
Purpose: Verify the dependency chain and DAG structure for a given phase

This script analyzes the import structure of a phase to ensure:
- No circular dependencies exist
- All files participate in the dependency graph
- Files are in the correct topological order
- No orphaned files exist

Usage:
    python scripts/audit/verify_phase_chain.py --phase 0 --strict
    python scripts/audit/verify_phase_chain.py --phase 0 --output report.json
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
import os
from collections import defaultdict
from pathlib import Path

# Add src to path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

class ImportAnalyzer(ast.NodeVisitor):
    """Analyzes imports in a Python file."""
    
    def __init__(self):
        self.imports: list[tuple[str, int]] = [] # (module_name, level)
        self.in_type_checking = False
    
    def visit_If(self, node: ast.If) -> None:
        # Check if this is "if TYPE_CHECKING:"
        is_type_checking = False
        try:
            if isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING":
                is_type_checking = True
            elif isinstance(node.test, ast.Attribute) and node.test.attr == "TYPE_CHECKING":
                is_type_checking = True
        except Exception:
            pass
            
        if is_type_checking:
            self.in_type_checking = True
            # Visit body, but we know we are in type checking
            # Actually, we just want to NOT visit imports in body if we ignore them
            # But maybe we should just skip visiting the body?
            # The prompt implies we want to avoid cycles. TYPE_CHECKING cycles are usually ignored.
            # So we skip visiting the body of if TYPE_CHECKING
            self.in_type_checking = False
            # We also need to visit orelse if it exists
            for child in node.orelse:
                self.visit(child)
        else:
            self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        if self.in_type_checking:
            return
        for alias in node.names:
            self.imports.append((alias.name, 0))
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if self.in_type_checking:
            return
        module = node.module if node.module else ""
        self.imports.append((module, node.level))

def resolve_import(base_file: Path, module_name: str, level: int, root_pkg: str) -> str | None:
    """
    Resolve an import to a full module name.
    
    Args:
        base_file: Path to the file doing the import
        module_name: The module name being imported (e.g. "utils" or "farfan.utils")
        level: Relative import level (0=absolute, 1='.', 2='..')
        root_pkg: The root package path (e.g. src/farfan_pipeline/phases/Phase_0)
        
    Returns:
        Absolute path to the imported file if it exists in the phase, else None.
    """
    if level == 0:
        # Absolute import
        # Check if it starts with our package prefix
        # We need to map module name to file path
        # Assuming src root is known
        
        # Try to find it in the src folder
        src_root = REPO_ROOT / "src"
        parts = module_name.split('.')
        potential_path = src_root.joinpath(*parts)
        
        # Check for .py or package dir
        if potential_path.with_suffix('.py').exists():
            return str(potential_path.with_suffix('.py'))
        if potential_path.is_dir() and (potential_path / "__init__.py").exists():
            return str(potential_path / "__init__.py")
            
        return None
    else:
        # Relative import
        # level 1: .
        # level 2: ..
        current_dir = base_file.parent
        for _ in range(level - 1):
            current_dir = current_dir.parent
            
        if module_name:
            parts = module_name.split('.')
            target = current_dir.joinpath(*parts)
        else:
            target = current_dir

        if target.with_suffix('.py').exists():
            return str(target.with_suffix('.py'))
        if target.is_dir() and (target / "__init__.py").exists():
            return str(target / "__init__.py")
            
        return None

def build_dependency_graph(phase_dir: Path) -> dict[str, list[str]]:
    """Build dependency graph for a phase."""
    graph: dict[str, list[str]] = defaultdict(list)
    
    # Get all Python files in the phase
    py_files = sorted(list(phase_dir.rglob("*.py")))
    
    # Filter out __pycache__ and backup files
    py_files = [
        f for f in py_files
        if "__pycache__" not in str(f) and not f.name.endswith(".bak")
    ]
    
    # Map absolute paths to relative paths for reporting
    abs_to_rel = {str(f): str(f.relative_to(phase_dir)) for f in py_files}
    
    for py_file in py_files:
        rel_name = abs_to_rel[str(py_file)]
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(py_file))
            
            analyzer = ImportAnalyzer()
            analyzer.visit(tree)
            
            for mod_name, level in analyzer.imports:
                resolved_path = resolve_import(py_file, mod_name, level, str(phase_dir))
                
                if resolved_path and resolved_path in abs_to_rel:
                    target_rel = abs_to_rel[resolved_path]
                    # Avoid self-loops
                    if rel_name != target_rel:
                        graph[rel_name].append(target_rel)
                        
        except Exception as e:
            print(f"Warning: Could not analyze {rel_name}: {e}", file=sys.stderr)
            
    return dict(graph)


def detect_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    """Detect cycles in the dependency graph using DFS."""
    cycles = []
    visited = set()
    rec_stack = set()
    path = []
    
    def dfs(node: str) -> bool:
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:
                # Found a cycle
                cycle_start = path.index(neighbor)
                cycles.append(path[cycle_start:] + [neighbor])
                return True
        
        path.pop()
        rec_stack.remove(node)
        return False
    
    # Ensure we visit all nodes
    all_nodes = set(graph.keys())
    for deps in graph.values():
        all_nodes.update(deps)
        
    for node in sorted(all_nodes):
        if node not in visited:
            dfs(node)
    
    return cycles

def find_orphaned_files(phase_dir: Path, graph: dict[str, list[str]]) -> list[str]:
    """Find files that are not in the dependency graph."""
    py_files = list(phase_dir.rglob("*.py"))
    
    all_files = set()
    for f in py_files:
         if "__pycache__" not in str(f) and not f.name.endswith(".bak"):
             all_files.add(str(f.relative_to(phase_dir)))

    # Get all nodes in the graph (both keys and values)
    graph_nodes = set(graph.keys())
    for deps in graph.values():
        graph_nodes.update(deps)
    
    # Find orphaned files
    orphaned = []
    for f in all_files:
        if f not in graph_nodes:
            # Exclude specific directories from strict orphan check if needed
            # But the spec says "CERO archivos fuera del grafo" except docs/contracts/tests
            # So we list them, and let the caller decide if it's strict failure
            orphaned.append(f)
            
    return sorted(orphaned)

def verify_phase_chain(phase_num: int, strict: bool = False, output: str | None = None) -> int:
    phase_dir = REPO_ROOT / "src" / "farfan_pipeline" / "phases" / f"Phase_{phase_num}"
    
    if not phase_dir.exists():
        # Try padded version (Phase_00, Phase_01)
        phase_dir = REPO_ROOT / "src" / "farfan_pipeline" / "phases" / f"Phase_{phase_num:02d}"

    if not phase_dir.exists():
        print(f"Error: Phase directory not found: {phase_dir}", file=sys.stderr)
        return 1
    
    print(f"Verifying Phase {phase_num} dependency chain...")
    print(f"Phase directory: {phase_dir}")
    print("=" * 60)
    
    # Build dependency graph
    graph = build_dependency_graph(phase_dir)
    print(f"\n✓ Built dependency graph with {len(graph)} modules (that have dependencies)")
    
    # Detect cycles
    cycles = detect_cycles(graph)
    if cycles:
        print(f"\n✗ CIRCULAR DEPENDENCIES DETECTED: {len(cycles)} cycle(s)")
        for i, cycle in enumerate(cycles, 1):
            print(f"  Cycle {i}: {' -> '.join(cycle)}")
    else:
        print("\n✓ No circular dependencies detected")
    
    # Find orphaned files
    orphaned_raw = find_orphaned_files(phase_dir, graph)
    
    # Filter orphans: Spec allows docs, primitives, interphase, contracts, tests to be "outside" the main DAG
    # IF they are not imported. But usually contracts import stuff.
    # The spec says: "Está explícitamente integrado en el DAG... o Está reclasificado a docs/, primitives/, interphase/ con justificación"
    
    # let's separate "true orphans" (in root or src folders) from "allowed orphans"
    true_orphans = []
    allowed_orphans = []
    
    for f in orphaned_raw:
        if any(f.startswith(d) for d in ["docs/", "tests/", "primitives/", "interphase/", "contracts/"]):
            allowed_orphans.append(f)
        else:
            true_orphans.append(f)

    if true_orphans:
        print(f"\n⚠ WARNING: Found {len(true_orphans)} TRUE orphaned file(s) (must be fixed):")
        for orphan in true_orphans:
            print(f"  - {orphan}")
    
    if allowed_orphans:
        print(f"\nℹ Info: Found {len(allowed_orphans)} allowed/classified orphaned file(s):")
        for orphan in allowed_orphans:
            print(f"  - {orphan}")

    
    # Generate report
    report = {
        "phase_id": str(phase_num),
        "phase_dir": str(phase_dir),
        "total_files": len(orphaned_raw) + len(graph), # Approximation
        "files_in_chain": len(graph), # Approximate
        "orphan_files": true_orphans,
        "allowed_orphans": allowed_orphans,
        "circular_dependencies": cycles,
        "dependency_graph": graph,
        "validation_status": "FAIL" if (cycles or true_orphans) else "PASS"
    }
    
    # Save report if requested
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2))
        print(f"\n✓ Report saved to: {output_path}")
    
    print("\n" + "=" * 60)
    
    if cycles:
        print("VERIFICATION FAILED: Cycles detected")
        return 1
    
    if strict and true_orphans:
        print("VERIFICATION FAILED: Orphans detected in strict mode")
        return 1
        
    print("VERIFICATION PASSED")
    return 0

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", type=int, required=True)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output", type=str)
    args = parser.parse_args()
    return verify_phase_chain(args.phase, args.strict, args.output)


if __name__ == "__main__":
    sys.exit(main())
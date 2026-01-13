#!/usr/bin/env python3
"""
Advanced Phase DAG Analyzer
Analyzes the true dependency graph of a phase including __init__.py imports
"""
from __future__ import annotations

import ast
import json
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, List, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))


class DependencyAnalyzer:
    """Analyze Python file dependencies within a phase."""
    
    def __init__(self, phase_dir: Path, phase_num: int):
        self.phase_dir = phase_dir
        self.phase_num = phase_num
        self.files: Dict[str, Path] = {}
        self.imports: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_imports: Dict[str, Set[str]] = defaultdict(set)
        
    def scan_files(self):
        """Scan all Python files in the phase."""
        for py_file in self.phase_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            rel_path = str(py_file.relative_to(self.phase_dir))
            self.files[rel_path] = py_file
            
    def extract_phase_imports(self, file_path: Path) -> Set[str]:
        """Extract imports from this phase only."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))
        except Exception as e:
            print(f"Warning: Could not parse {file_path}: {e}", file=sys.stderr)
            return set()
        
        imports = set()
        phase_prefix = f"farfan_pipeline.phases.Phase_{self.phase_num}"
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith(phase_prefix):
                        imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith(phase_prefix):
                    imports.add(node.module)
        
        return imports
    
    def resolve_to_file(self, import_path: str) -> str | None:
        """Resolve an import path to a file path."""
        # Extract the module part after Phase_N
        parts = import_path.split(".")
        try:
            phase_idx = parts.index(f"Phase_{self.phase_num}")
            module_parts = parts[phase_idx + 1:]
        except ValueError:
            return None
        
        if not module_parts:
            return "__init__.py"
        
        # Try as direct file
        file_path = "/".join(module_parts) + ".py"
        if file_path in self.files:
            return file_path
        
        # Try as package
        package_path = "/".join(module_parts) + "/__init__.py"
        if package_path in self.files:
            return package_path
        
        # Try parent package
        if len(module_parts) > 1:
            parent = "/".join(module_parts[:-1]) + ".py"
            if parent in self.files:
                return parent
        
        return None
    
    def build_graph(self):
        """Build the dependency graph."""
        for rel_path, abs_path in self.files.items():
            imports = self.extract_phase_imports(abs_path)
            for imp in imports:
                target_file = self.resolve_to_file(imp)
                if target_file and target_file != rel_path:
                    self.imports[rel_path].add(target_file)
                    self.reverse_imports[target_file].add(rel_path)
    
    def find_cycles(self) -> List[List[str]]:
        """Find circular dependencies using DFS."""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.imports[node]:
                if neighbor not in visited:
                    dfs(neighbor, path[:])
                elif neighbor in rec_stack:
                    # Found cycle
                    try:
                        cycle_start = path.index(neighbor)
                        cycle = path[cycle_start:] + [neighbor]
                        if cycle not in cycles:
                            cycles.append(cycle)
                    except ValueError:
                        pass
            
            rec_stack.remove(node)
        
        for file in self.files:
            if file not in visited:
                dfs(file, [])
        
        return cycles
    
    def topological_sort(self) -> Tuple[List[str], List[str]]:
        """Perform topological sort. Returns (sorted, orphans)."""
        # Find all files referenced in the graph
        in_graph = set(self.imports.keys()) | set(self.reverse_imports.keys())
        
        # Find orphans (files not in graph)
        orphans = [f for f in self.files if f not in in_graph and f != "__init__.py"]
        
        # Kahn's algorithm for topological sort
        in_degree = {f: 0 for f in in_graph}
        for deps in self.imports.values():
            for dep in deps:
                if dep in in_degree:
                    in_degree[dep] += 1
        
        queue = deque([f for f, deg in in_degree.items() if deg == 0])
        sorted_order = []
        
        while queue:
            node = queue.popleft()
            sorted_order.append(node)
            
            for dependent in self.reverse_imports.get(node, []):
                if dependent in in_degree:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)
        
        return sorted_order, orphans
    
    def analyze(self) -> Dict:
        """Perform full analysis."""
        self.scan_files()
        self.build_graph()
        
        cycles = self.find_cycles()
        sorted_files, orphans = self.topological_sort()
        
        # Check for label mismatches
        label_mismatches = []
        for idx, file in enumerate(sorted_files):
            # Extract numeric labels from filename
            parts = file.split("_")
            if len(parts) >= 3 and parts[0].startswith("phase"):
                try:
                    stage_code = int(parts[1])
                    sub_code = int(parts[2])
                    expected_pos = f"{stage_code:02d}_{sub_code:02d}"
                    label_mismatches.append({
                        "file": file,
                        "label": f"{stage_code}_{sub_code}",
                        "actual_position": idx,
                        "note": f"Appears at position {idx} in topological order"
                    })
                except (ValueError, IndexError):
                    pass
        
        return {
            "phase_id": self.phase_num,
            "phase_dir": str(self.phase_dir.relative_to(REPO_ROOT)),
            "total_files": len(self.files),
            "files_in_chain": len(sorted_files),
            "orphan_files": orphans,
            "topological_order": sorted_files,
            "circular_dependencies": cycles,
            "label_position_mismatches": label_mismatches,
            "validation_status": "PASS" if not cycles and not orphans else "FAIL",
            "dependency_graph": {k: list(v) for k, v in self.imports.items()},
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Analyze phase DAG")
    parser.add_argument("--phase", type=int, required=True)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()
    
    phase_dir = REPO_ROOT / "src" / "farfan_pipeline" / "phases" / f"Phase_{args.phase}"
    
    if not phase_dir.exists():
        print(f"Error: Phase directory not found: {phase_dir}", file=sys.stderr)
        return 1
    
    analyzer = DependencyAnalyzer(phase_dir, args.phase)
    result = analyzer.analyze()
    
    # Print summary
    print(f"Phase {args.phase} Analysis:")
    print(f"  Total files: {result['total_files']}")
    print(f"  Files in chain: {result['files_in_chain']}")
    print(f"  Orphaned files: {len(result['orphan_files'])}")
    print(f"  Circular dependencies: {len(result['circular_dependencies'])}")
    print(f"  Status: {result['validation_status']}")
    
    # Save report
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\nReport saved to: {output_path}")
    
    return 0 if result['validation_status'] == 'PASS' else 1


if __name__ == "__main__":
    sys.exit(main())

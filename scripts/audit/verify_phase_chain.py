#!/usr/bin/env python3
"""
Phase Chain Verification Script
================================

Analyzes import dependencies, topological order, and identifies issues
in Phase directories following the FARFAN audit specifications.

Usage:
    python scripts/audit/verify_phase_chain.py --phase 1 --strict --output contracts/phase1_chain_report.json

Author: F.A.R.F.A.N Pipeline Audit System
Version: 1.0.0
"""

import argparse
import ast
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


class PhaseChainAnalyzer:
    """Analyzes import chains and dependency graphs for a phase."""

    def __init__(self, phase_dir: Path, phase_id: int):
        self.phase_dir = phase_dir
        self.phase_id = phase_id
        self.phase_prefix = f"phase{phase_id}"
        
        # Analysis results
        self.all_files: Set[str] = set()
        self.imports: Dict[str, Set[str]] = defaultdict(set)
        self.imported_by: Dict[str, Set[str]] = defaultdict(set)
        self.topological_order: List[str] = []
        self.orphan_files: Set[str] = set()
        self.circular_deps: List[List[str]] = []
        self.label_mismatches: List[Dict[str, Any]] = []

    def discover_python_files(self) -> Set[str]:
        """Discover all Python files in the phase root directory."""
        py_files = set()
        for f in self.phase_dir.glob("*.py"):
            if not f.name.startswith("__") and f.is_file():
                py_files.add(f.stem)
        self.all_files = py_files
        return py_files

    def extract_imports(self, file_path: Path) -> Set[str]:
        """Extract imported module names from a Python file."""
        imports = set()
        try:
            tree = ast.parse(file_path.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Extract base module name
                        module_name = alias.name.split('.')[0]
                        imports.add(module_name)
                        # Also add full local module if it's a phase file
                        if self.phase_prefix in alias.name:
                            local_module = alias.name.split('.')[-1]
                            imports.add(local_module)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_name = node.module.split('.')[0]
                        imports.add(module_name)
                        # For relative imports in same phase
                        if self.phase_prefix in node.module:
                            local_module = node.module.split('.')[-1]
                            imports.add(local_module)
                    # Handle from . import statements
                    for alias in node.names:
                        imports.add(alias.name)
        except Exception as e:
            print(f"Warning: Could not parse {file_path}: {e}", file=sys.stderr)
        return imports

    def build_dependency_graph(self) -> None:
        """Build the import dependency graph."""
        for file_stem in self.all_files:
            file_path = self.phase_dir / f"{file_stem}.py"
            if file_path.exists():
                imports = self.extract_imports(file_path)
                # Only track imports within the same phase
                local_imports = imports & self.all_files
                self.imports[file_stem] = local_imports
                for imported in local_imports:
                    self.imported_by[imported].add(file_stem)

    def detect_orphans(self) -> Set[str]:
        """Detect orphan files (not imported and don't import anything in the phase)."""
        orphans = set()
        for file_stem in self.all_files:
            # A file is orphan if it's not imported by anyone AND doesn't import anyone
            has_imports = len(self.imports.get(file_stem, set())) > 0
            is_imported = len(self.imported_by.get(file_stem, set())) > 0
            
            if not has_imports and not is_imported:
                # Special case: constants files might not import anything
                if "constant" not in file_stem.lower():
                    orphans.add(file_stem)
        
        self.orphan_files = orphans
        return orphans

    def topological_sort(self) -> List[str]:
        """Perform topological sort of the dependency graph."""
        # Kahn's algorithm
        in_degree = {file: 0 for file in self.all_files}
        
        # Calculate in-degrees
        for file in self.all_files:
            for imported in self.imports.get(file, set()):
                if imported in in_degree:
                    in_degree[file] += 1
        
        # Queue of files with no dependencies
        queue = [f for f in self.all_files if in_degree[f] == 0]
        result = []
        
        while queue:
            # Sort for deterministic output
            queue.sort()
            current = queue.pop(0)
            result.append(current)
            
            # For each file that imports current
            for importer in self.imported_by.get(current, set()):
                in_degree[importer] -= 1
                if in_degree[importer] == 0:
                    queue.append(importer)
        
        # If not all files processed, there's a cycle
        if len(result) < len(self.all_files):
            unprocessed = self.all_files - set(result)
            self.detect_circular_dependencies(unprocessed)
        
        self.topological_order = result
        return result

    def detect_circular_dependencies(self, unprocessed: Set[str]) -> None:
        """Detect circular dependencies in remaining files."""
        # Simple cycle detection - could be enhanced
        for file in unprocessed:
            cycle = self._find_cycle(file, set(), [])
            if cycle and cycle not in self.circular_deps:
                self.circular_deps.append(cycle)

    def _find_cycle(self, node: str, visited: Set[str], path: List[str]) -> List[str]:
        """DFS to find cycles."""
        if node in path:
            cycle_start = path.index(node)
            return path[cycle_start:] + [node]
        
        if node in visited:
            return []
        
        visited.add(node)
        path.append(node)
        
        for imported in self.imports.get(node, set()):
            cycle = self._find_cycle(imported, visited, path[:])
            if cycle:
                return cycle
        
        return []

    def check_label_position_alignment(self) -> List[Dict[str, Any]]:
        """Check if file naming labels match topological positions."""
        mismatches = []
        
        # Extract position from filename (e.g., phase1_20_00_xxx -> 20)
        for idx, file_stem in enumerate(self.topological_order):
            if self.phase_prefix in file_stem:
                parts = file_stem.split('_')
                if len(parts) >= 3 and parts[0] == self.phase_prefix:
                    try:
                        label_position = int(parts[1])
                        actual_position = idx
                        
                        # Allow some tolerance (files with same prefix should be close)
                        if abs(label_position - actual_position * 10) > 15:
                            mismatches.append({
                                "file": file_stem,
                                "label_suggests": label_position,
                                "actual_position": actual_position,
                                "action": "Review and potentially rename or reorder"
                            })
                    except ValueError:
                        # Filename does not contain a valid numeric label; treat as a mismatch.
                        mismatches.append({
                            "file": file_stem,
                            "label_suggests": parts[1],
                            "actual_position": idx,
                            "action": "Filename label is not a valid integer; review naming convention"
                        })
        
        self.label_mismatches = mismatches
        return mismatches

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report."""
        return {
            "phase_id": self.phase_id,
            "phase_dir": str(self.phase_dir),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_files": len(self.all_files),
            "files_in_chain": len(self.topological_order),
            "orphan_files": sorted(list(self.orphan_files)),
            "topological_order": self.topological_order,
            "label_position_mismatches": self.label_mismatches,
            "circular_dependencies": self.circular_deps,
            "validation_status": "PASS" if not self.orphan_files and not self.circular_deps else "FAIL",
            "issues_summary": {
                "orphan_count": len(self.orphan_files),
                "circular_dependency_count": len(self.circular_deps),
                "label_mismatch_count": len(self.label_mismatches)
            }
        }


def main():
    parser = argparse.ArgumentParser(
        description="Verify phase import chain and dependency structure"
    )
    parser.add_argument(
        "--phase",
        type=int,
        required=True,
        help="Phase number to analyze (e.g., 1, 2, 3)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict validation mode"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output JSON file path for the report"
    )
    parser.add_argument(
        "--phase-root",
        type=str,
        default=None,
        help="Override phase root directory (default: src/farfan_pipeline/phases/Phase_N)"
    )
    
    args = parser.parse_args()
    
    # Determine phase directory
    if args.phase_root:
        phase_dir = Path(args.phase_root)
    else:
        repo_root = Path(__file__).parent.parent.parent
        phase_dir = repo_root / "src" / "farfan_pipeline" / "phases" / f"Phase_{args.phase}"
    
    if not phase_dir.exists():
        print(f"Error: Phase directory not found: {phase_dir}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Analyzing Phase {args.phase} at {phase_dir}")
    print("=" * 80)
    
    # Run analysis
    analyzer = PhaseChainAnalyzer(phase_dir, args.phase)
    
    print("1. Discovering Python files...")
    files = analyzer.discover_python_files()
    print(f"   Found {len(files)} Python files")
    
    print("2. Building dependency graph...")
    analyzer.build_dependency_graph()
    print(f"   Tracked {sum(len(deps) for deps in analyzer.imports.values())} import relationships")
    
    print("3. Detecting orphan files...")
    orphans = analyzer.detect_orphans()
    if orphans:
        print(f"   WARNING: Found {len(orphans)} orphan files:")
        for orphan in sorted(orphans):
            print(f"      - {orphan}")
    else:
        print("   ✓ No orphan files detected")
    
    print("4. Computing topological order...")
    topo_order = analyzer.topological_sort()
    print(f"   Generated topological order with {len(topo_order)} nodes")
    if topo_order:
        print("   Order:")
        for idx, file in enumerate(topo_order[:10]):
            print(f"      {idx:2d}. {file}")
        if len(topo_order) > 10:
            print(f"      ... and {len(topo_order) - 10} more")
    
    print("5. Checking for circular dependencies...")
    if analyzer.circular_deps:
        print(f"   ERROR: Found {len(analyzer.circular_deps)} circular dependencies:")
        for cycle in analyzer.circular_deps:
            print(f"      - {' -> '.join(cycle)}")
    else:
        print("   ✓ No circular dependencies detected")
    
    print("6. Verifying label-position alignment...")
    mismatches = analyzer.check_label_position_alignment()
    if mismatches:
        print(f"   WARNING: Found {len(mismatches)} label mismatches:")
        for mismatch in mismatches[:5]:
            print(f"      - {mismatch['file']}: label={mismatch['label_suggests']}, actual={mismatch['actual_position']}")
    else:
        print("   ✓ All labels align with positions")
    
    # Generate report
    report = analyzer.generate_report()
    
    print("\n" + "=" * 80)
    print(f"VALIDATION STATUS: {report['validation_status']}")
    print("=" * 80)
    
    # Save report if output specified
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2))
        print(f"\nReport saved to: {output_path}")
    else:
        print("\nFull report:")
        print(json.dumps(report, indent=2))
    
    # Exit with error if strict mode and validation failed
    if args.strict and report['validation_status'] != 'PASS':
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Circular Import Detection Tool for F.A.R.F.A.N Pipeline

This script detects circular imports in the Python codebase using multiple strategies:
1. Static AST analysis to build import dependency graph
2. Tarjan's algorithm for strongly connected components detection
3. Runtime import testing for actual circular import issues

Usage:
    python scripts/check_circular_imports.py
    python scripts/check_circular_imports.py --verbose
    python scripts/check_circular_imports.py --test-runtime
"""
import ast
import argparse
import importlib
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))


class ImportAnalyzer(ast.NodeVisitor):
    """AST visitor to extract all imports from a Python module."""
    
    def __init__(self):
        self.imports: List[str] = []
    
    def visit_Import(self, node: ast.Import) -> None:
        """Handle 'import X' statements."""
        for alias in node.names:
            self.imports.append(alias.name)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Handle 'from X import Y' statements."""
        if node.module:
            self.imports.append(node.module)


class CircularImportDetector:
    """Main circular import detection engine."""
    
    def __init__(self, root_dir: Path, verbose: bool = False):
        self.root_dir = root_dir
        self.verbose = verbose
        self.graph: Dict[str, Set[str]] = defaultdict(set)
        self.module_to_file: Dict[str, str] = {}
        self.excluded_dirs = {
            '.git', '__pycache__', '.venv', '.venv-1', 'venv', 'env',
            'node_modules', '.pytest_cache', 'test_output', 'artifacts',
            'artifact', 'archive', 'evidence_traces', 'trace_examples',
            'data', 'system', '.tox', 'build', 'dist', '.eggs'
        }
        self.excluded_files = {'setup.py'}
    
    def log(self, message: str) -> None:
        """Log message if verbose mode is enabled."""
        if self.verbose:
            print(f"[DEBUG] {message}")
    
    def get_module_name_from_path(self, file_path: Path) -> Optional[str]:
        """Convert file path to Python module name."""
        try:
            rel_path = file_path.relative_to(self.root_dir)
            parts = list(rel_path.parts)
            
            # Remove .py extension
            if parts[-1].endswith('.py'):
                parts[-1] = parts[-1][:-3]
            
            # Handle __init__.py files (represent package itself)
            if parts[-1] == '__init__':
                parts = parts[:-1]
            
            if not parts:
                return None
            
            return '.'.join(parts)
        except (ValueError, IndexError):
            return None
    
    def extract_imports(self, file_path: Path) -> List[str]:
        """Extract all imports from a Python file using AST."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            analyzer = ImportAnalyzer()
            analyzer.visit(tree)
            
            return analyzer.imports
        except SyntaxError as e:
            self.log(f"Syntax error in {file_path}: {e}")
            return []
        except Exception as e:
            self.log(f"Error parsing {file_path}: {e}")
            return []
    
    def find_python_files(self) -> List[Path]:
        """Find all Python files in the project."""
        python_files = []
        
        for root, dirs, files in os.walk(self.root_dir):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in self.excluded_dirs]
            
            for file in files:
                if file.endswith('.py') and file not in self.excluded_files:
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def build_dependency_graph(self) -> None:
        """Build the complete import dependency graph."""
        python_files = self.find_python_files()
        self.log(f"Found {len(python_files)} Python files")
        
        # First pass: map all module names to files
        for file_path in python_files:
            module_name = self.get_module_name_from_path(file_path)
            if module_name:
                self.module_to_file[module_name] = str(file_path)
        
        self.log(f"Mapped {len(self.module_to_file)} modules")
        
        # Second pass: build dependency graph
        for file_path in python_files:
            module_name = self.get_module_name_from_path(file_path)
            if not module_name:
                continue
            
            imports = self.extract_imports(file_path)
            
            for imp in imports:
                # Try to match import to known modules
                # Check exact match first, then parent packages
                imp_parts = imp.split('.')
                
                for i in range(len(imp_parts), 0, -1):
                    potential_module = '.'.join(imp_parts[:i])
                    if potential_module in self.module_to_file:
                        self.graph[module_name].add(potential_module)
                        break
        
        self.log(f"Built graph with {sum(len(deps) for deps in self.graph.values())} edges")
    
    def find_cycles_tarjan(self) -> List[List[str]]:
        """
        Find all strongly connected components (cycles) using Tarjan's algorithm.
        
        Returns:
            List of cycles, where each cycle is a list of module names.
        """
        index_counter = [0]
        stack: List[str] = []
        lowlinks: Dict[str, int] = {}
        index: Dict[str, int] = {}
        on_stack: Set[str] = set()
        sccs: List[List[str]] = []
        
        def strongconnect(node: str) -> None:
            """Tarjan's strongconnect subroutine."""
            index[node] = index_counter[0]
            lowlinks[node] = index_counter[0]
            index_counter[0] += 1
            stack.append(node)
            on_stack.add(node)
            
            for neighbor in self.graph.get(node, set()):
                if neighbor not in index:
                    strongconnect(neighbor)
                    lowlinks[node] = min(lowlinks[node], lowlinks[neighbor])
                elif neighbor in on_stack:
                    lowlinks[node] = min(lowlinks[node], index[neighbor])
            
            if lowlinks[node] == index[node]:
                scc = []
                while True:
                    w = stack.pop()
                    on_stack.remove(w)
                    scc.append(w)
                    if w == node:
                        break
                # Only report SCCs with more than one node (actual cycles)
                if len(scc) > 1:
                    sccs.append(scc)
        
        for node in self.graph:
            if node not in index:
                strongconnect(node)
        
        return sccs
    
    def test_runtime_imports(self, modules_to_test: Optional[List[str]] = None) -> List[Tuple[str, str]]:
        """
        Test actual runtime imports to detect circular import errors.
        
        Args:
            modules_to_test: Optional list of specific modules to test.
                           If None, tests key top-level modules.
        
        Returns:
            List of (module_name, error_message) tuples for modules with circular imports.
        """
        if modules_to_test is None:
            # Test key top-level modules
            modules_to_test = [
                'src.farfan_pipeline',
                'src.orchestration',
                'src.canonic_phases',
                'src.cross_cutting_infrastrucuiture',
                'src.methods_dispensary',
            ]
        
        circular_errors = []
        
        for module in modules_to_test:
            try:
                importlib.import_module(module)
                self.log(f"✅ Successfully imported {module}")
            except ImportError as e:
                error_msg = str(e)
                if 'circular' in error_msg.lower() or 'cannot import' in error_msg.lower():
                    circular_errors.append((module, error_msg))
                    self.log(f"⚠️  Circular import detected in {module}")
                else:
                    self.log(f"Import error (not circular) in {module}: {error_msg}")
            except Exception as e:
                self.log(f"Other error in {module}: {type(e).__name__}: {e}")
        
        return circular_errors
    
    def format_cycle_report(self, cycles: List[List[str]]) -> str:
        """Format cycle detection results into a human-readable report."""
        if not cycles:
            return "✅ No circular imports detected!"
        
        report_lines = [
            f"⚠️  Found {len(cycles)} circular import(s):",
            "=" * 80,
        ]
        
        for i, cycle in enumerate(cycles, 1):
            report_lines.append(f"\nCircular Import #{i} ({len(cycle)} modules):")
            report_lines.append("-" * 80)
            
            # Show modules in the cycle
            for module in sorted(cycle):
                file_path = self.module_to_file.get(module, 'unknown')
                rel_path = os.path.relpath(file_path, self.root_dir) if file_path != 'unknown' else 'unknown'
                report_lines.append(f"  • {module}")
                report_lines.append(f"    File: {rel_path}")
            
            # Show dependencies within the cycle
            report_lines.append("\n  Import dependencies within cycle:")
            for module in sorted(cycle):
                deps_in_cycle = [dep for dep in self.graph.get(module, set()) if dep in cycle]
                if deps_in_cycle:
                    report_lines.append(f"    {module}")
                    for dep in sorted(deps_in_cycle):
                        report_lines.append(f"      → imports {dep}")
            
            report_lines.append("=" * 80)
        
        return '\n'.join(report_lines)
    
    def run(self, test_runtime: bool = False) -> int:
        """
        Run the circular import detection.
        
        Args:
            test_runtime: If True, also test runtime imports.
        
        Returns:
            Exit code: 0 if no circular imports, 1 otherwise.
        """
        print("F.A.R.F.A.N Circular Import Detection")
        print("=" * 80)
        print(f"Scanning: {self.root_dir}")
        print()
        
        # Build dependency graph
        self.build_dependency_graph()
        
        print(f"Analyzed {len(self.module_to_file)} modules")
        print(f"Found {sum(len(deps) for deps in self.graph.values())} import relationships")
        print()
        
        # Find cycles using static analysis
        cycles = self.find_cycles_tarjan()
        
        print("Static Analysis Results:")
        print("-" * 80)
        print(self.format_cycle_report(cycles))
        print()
        
        # Optionally test runtime imports
        if test_runtime:
            print("\nRuntime Import Testing:")
            print("-" * 80)
            runtime_errors = self.test_runtime_imports()
            
            if runtime_errors:
                print(f"⚠️  Found {len(runtime_errors)} runtime circular import(s):")
                for module, error in runtime_errors:
                    print(f"\n  Module: {module}")
                    print(f"  Error: {error}")
            else:
                print("✅ No runtime circular imports detected!")
            print()
        
        # Return exit code
        has_issues = len(cycles) > 0 or (test_runtime and len(runtime_errors) > 0)
        return 1 if has_issues else 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Detect circular imports in the F.A.R.F.A.N codebase',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic check (static analysis only)
  python scripts/check_circular_imports.py
  
  # Verbose output with detailed logging
  python scripts/check_circular_imports.py --verbose
  
  # Include runtime import testing
  python scripts/check_circular_imports.py --test-runtime
  
  # Full check with all options
  python scripts/check_circular_imports.py --verbose --test-runtime
        """
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output with detailed logging'
    )
    
    parser.add_argument(
        '--test-runtime', '-r',
        action='store_true',
        help='Test runtime imports in addition to static analysis'
    )
    
    args = parser.parse_args()
    
    detector = CircularImportDetector(PROJECT_ROOT, verbose=args.verbose)
    return detector.run(test_runtime=args.test_runtime)


if __name__ == '__main__':
    sys.exit(main())

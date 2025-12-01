#!/usr/bin/env python3
"""
FARFAN Method Inventory Scanner - PRODUCTION GRADE
Scans repository for all analytical methods with AST-based extraction.

REQUIREMENTS:
- Coverage: ≥95% of executor methods
- Accuracy: 0 phantom methods
- Determinism: Hash(run1) == Hash(run2)
- Performance: < 10 seconds
"""
import ast
import hashlib
import json
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Optional, Any

# MANDATORY SCAN PATHS - Verified to exist
MANDATORY_SCAN_PATHS = [
    "farfan_core/farfan_core/core",
    "farfan_core/farfan_core/processing",
    "farfan_core/farfan_core/analysis",
    "farfan_core/farfan_core/orchestrator",
    "farfan_core/farfan_core/utils",
]

EXCLUDE_PATTERNS = [
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "build",
    "dist",
    ".pytest_cache",
    ".mypy_cache",
]


@dataclass
class MethodSignature:
    """Method signature information"""
    args: List[str]
    kwargs: List[str]
    returns: Optional[str]
    is_async: bool
    accepts_executor_config: bool
    decorators: List[str]


@dataclass
class GovernanceFlags:
    """Governance and compliance flags"""
    uses_yaml: bool
    has_hardcoded_calibration: bool
    has_hardcoded_timeout: bool
    suspicious_magic_numbers: List[float]
    is_executor_class: bool


@dataclass
class LocationInfo:
    """Source location information"""
    file_path: str
    line_start: int
    line_end: int


@dataclass
class MethodDescriptor:
    """Complete method descriptor"""
    method_id: str
    role: str
    aggregation_level: str
    module: str
    class_name: Optional[str]
    method_name: str
    signature: MethodSignature
    governance_flags: GovernanceFlags
    location: LocationInfo
    ast_hash: str
    docstring: Optional[str]
    complexity: int
    dependencies: List[str]


class MethodInventoryScanner:
    """Production-grade method inventory scanner with full validation"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root.resolve()
        self.inventory: Dict[str, MethodDescriptor] = {}
        self.failures: List[Dict[str, str]] = []
        self.files_scanned = 0
        self.start_time = time.time()
        
    def scan(self) -> Dict[str, Any]:
        """Execute full scan with validation"""
        print(f"🔍 Scanning repository: {self.repo_root}")
        
        # STEP 1: Verify all mandatory paths exist
        self._verify_paths()
        
        # STEP 2: Load questionnaire_monolith.json for cross-reference (if exists)
        monolith_methods = self._load_monolith_methods()
        
        # STEP 3: Scan all Python files
        python_files = self._find_python_files()
        print(f"📁 Found {len(python_files)} Python files to scan")
        
        # STEP 4: Parse each file and extract methods
        for py_file in python_files:
            self._scan_file(py_file)
        
        # STEP 5: Cross-reference with monolith
        if monolith_methods:
            self._cross_reference_monolith(monolith_methods)
        
        # STEP 6: Generate manifest
        return self._generate_manifest()
    
    def _verify_paths(self):
        """Verify all mandatory scan paths exist"""
        print("✓ Verifying mandatory paths...")
        for path_str in MANDATORY_SCAN_PATHS:
            full_path = self.repo_root / path_str
            if not full_path.exists():
                error = f"Missing mandatory path: {path_str}"
                self.failures.append({
                    "type": "missing_path",
                    "path": path_str,
                    "error": error
                })
                print(f"  ❌ {error}")
            else:
                print(f"  ✓ {path_str}")
    
    def _load_monolith_methods(self) -> Set[str]:
        """Load method references from questionnaire_monolith.json"""
        monolith_path = self.repo_root / "system/config/questionnaire/questionnaire_monolith.json"
        
        if not monolith_path.exists():
            print(f"⚠️  Monolith not found (optional): {monolith_path}")
            return set()
        
        try:
            with open(monolith_path) as f:
                monolith = json.load(f)
            
            # Extract all method references from method_sets
            methods = set()
            for question in monolith.get("questions", []):
                for method_set in question.get("method_sets", {}).values():
                    methods.update(method_set.get("methods", []))
            
            print(f"✓ Loaded {len(methods)} method references from monolith")
            return methods
        except Exception as e:
            print(f"⚠️  Failed to load monolith: {e}")
            return set()
    
    def _find_python_files(self) -> List[Path]:
        """Find all Python files in mandatory scan paths"""
        python_files = []
        
        for path_str in MANDATORY_SCAN_PATHS:
            scan_path = self.repo_root / path_str
            if not scan_path.exists():
                continue
            
            for py_file in scan_path.rglob("*.py"):
                # Skip excluded patterns
                if any(pattern in str(py_file) for pattern in EXCLUDE_PATTERNS):
                    continue
                python_files.append(py_file)
        
        return sorted(python_files)
    
    def _scan_file(self, file_path: Path):
        """Scan a single Python file for methods"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(file_path))
            self.files_scanned += 1
            
            # Extract module path
            rel_path = file_path.relative_to(self.repo_root)
            module = self._path_to_module(rel_path)
            
            # Visit all nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    self._extract_method(node, module, str(rel_path), None)
                elif isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            self._extract_method(item, module, str(rel_path), node.name)
        
        except SyntaxError as e:
            self.failures.append({
                "type": "syntax_error",
                "file": str(file_path.relative_to(self.repo_root)),
                "error": str(e)
            })
        except Exception as e:
            self.failures.append({
                "type": "parse_error",
                "file": str(file_path.relative_to(self.repo_root)),
                "error": str(e)
            })
    
    def _path_to_module(self, path: Path) -> str:
        """Convert file path to module name"""
        parts = list(path.parts)
        
        # Remove .py extension
        if parts[-1].endswith('.py'):
            parts[-1] = parts[-1][:-3]
        
        # Remove __init__
        if parts[-1] == '__init__':
            parts = parts[:-1]
        
        return '.'.join(parts)
    
    def _extract_method(self, node: ast.FunctionDef, module: str, file_path: str, 
                       class_name: Optional[str]):
        """Extract method descriptor from AST node"""
        method_name = node.name
        
        # Skip private methods starting with _
        if method_name.startswith('_') and method_name != '__init__':
            return
        
        # Build method_id
        if class_name:
            method_id = f"{class_name}.{method_name}"
        else:
            method_id = method_name
        
        # Extract signature
        signature = self._extract_signature(node)
        
        # Extract governance flags
        governance = self._extract_governance_flags(node)
        
        # Compute AST hash
        ast_hash = self._compute_ast_hash(node)
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Compute cyclomatic complexity
        complexity = self._compute_complexity(node)
        
        # Extract dependencies (method calls)
        dependencies = self._extract_dependencies(node)
        
        # Infer role and aggregation level
        role, agg_level = self._infer_role(method_id, class_name, file_path)
        
        # Create descriptor
        descriptor = MethodDescriptor(
            method_id=method_id,
            role=role,
            aggregation_level=agg_level,
            module=module,
            class_name=class_name,
            method_name=method_name,
            signature=signature,
            governance_flags=governance,
            location=LocationInfo(
                file_path=file_path,
                line_start=node.lineno,
                line_end=node.end_lineno or node.lineno
            ),
            ast_hash=ast_hash,
            docstring=docstring,
            complexity=complexity,
            dependencies=dependencies
        )
        
        self.inventory[method_id] = descriptor
    
    def _extract_signature(self, node: ast.FunctionDef) -> MethodSignature:
        """Extract method signature"""
        args = [arg.arg for arg in node.args.args]
        kwargs = [arg.arg for arg in node.args.kwonlyargs]
        
        # Extract return type
        returns = None
        if node.returns:
            returns = ast.unparse(node.returns)
        
        # Check if async
        is_async = isinstance(node, ast.AsyncFunctionDef)
        
        # Check if accepts executor_config
        accepts_config = 'config' in args or 'executor_config' in args
        
        # Extract decorators
        decorators = [ast.unparse(dec) for dec in node.decorator_list]
        
        return MethodSignature(
            args=args,
            kwargs=kwargs,
            returns=returns,
            is_async=is_async,
            accepts_executor_config=accepts_config,
            decorators=decorators
        )
    
    def _extract_governance_flags(self, node: ast.FunctionDef) -> GovernanceFlags:
        """Extract governance and compliance flags"""
        source = ast.unparse(node)
        
        # Check for YAML usage
        uses_yaml = 'yaml' in source.lower() or '.yml' in source.lower()
        
        # Check for hardcoded calibration values
        has_hardcoded_cal = any(keyword in source for keyword in [
            'b_theory', 'b_impl', 'b_deploy', 'calibration_score'
        ])
        
        # Check for hardcoded timeouts
        has_hardcoded_timeout = 'timeout' in source and any(
            f'timeout={val}' in source or f'timeout = {val}' in source
            for val in range(1, 100)
        )
        
        # Detect suspicious magic numbers
        magic_numbers = []
        for n in ast.walk(node):
            if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
                if n.value not in [0, 1, -1, 2, 10, 100, 1000]:
                    magic_numbers.append(float(n.value))
        
        # Check if executor class
        is_executor = 'Executor' in (node.name if hasattr(node, 'name') else '')
        
        return GovernanceFlags(
            uses_yaml=uses_yaml,
            has_hardcoded_calibration=has_hardcoded_cal,
            has_hardcoded_timeout=has_hardcoded_timeout,
            suspicious_magic_numbers=magic_numbers[:5],  # Limit to 5
            is_executor_class=is_executor
        )
    
    def _compute_ast_hash(self, node: ast.FunctionDef) -> str:
        """Compute deterministic SHA256 hash of normalized AST"""
        # Normalize AST by unparsing and re-parsing to remove formatting
        normalized = ast.unparse(node)
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    
    def _compute_complexity(self, node: ast.FunctionDef) -> int:
        """Compute cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for n in ast.walk(node):
            # Count decision points
            if isinstance(n, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(n, ast.BoolOp):
                complexity += len(n.values) - 1
        
        return complexity
    
    def _extract_dependencies(self, node: ast.FunctionDef) -> List[str]:
        """Extract method call dependencies"""
        dependencies = set()
        
        for n in ast.walk(node):
            if isinstance(n, ast.Call):
                if isinstance(n.func, ast.Attribute):
                    # Method call: obj.method()
                    dependencies.add(n.func.attr)
                elif isinstance(n.func, ast.Name):
                    # Function call: function()
                    dependencies.add(n.func.id)
        
        return sorted(list(dependencies))[:20]  # Limit to 20
    
    def _infer_role(self, method_id: str, class_name: Optional[str], 
                   file_path: str) -> tuple[str, str]:
        """Infer method role and aggregation level"""
        role = "UNKNOWN"
        agg_level = "UNKNOWN"
        
        # Infer from class name
        if class_name:
            if 'Executor' in class_name:
                role = "EXECUTOR"
                agg_level = "LEVEL_3"
            elif 'Processor' in class_name:
                role = "PROCESSOR"
                agg_level = "LEVEL_4"
            elif 'Analyzer' in class_name:
                role = "ANALYZER"
                agg_level = "LEVEL_4"
        
        # Infer from file path
        if 'orchestrator' in file_path:
            role = "ENGINE"
            agg_level = "LEVEL_0"
        elif 'processing' in file_path:
            role = "PROCESSOR"
        elif 'analysis' in file_path:
            role = "ANALYZER"
        
        return role, agg_level
    
    def _cross_reference_monolith(self, monolith_methods: Set[str]):
        """Cross-reference inventory with monolith"""
        inventory_methods = set(self.inventory.keys())
        
        # Find phantom methods (in monolith but not in inventory)
        phantom = monolith_methods - inventory_methods
        if phantom:
            print(f"⚠️  Found {len(phantom)} phantom methods in monolith:")
            for method in sorted(phantom)[:10]:
                print(f"    - {method}")
        
        # Find orphan methods (in inventory but not in monolith)
        orphan = inventory_methods - monolith_methods
        print(f"ℹ️  Found {len(orphan)} methods not referenced in monolith")
    
    def _generate_manifest(self) -> Dict[str, Any]:
        """Generate final manifest"""
        elapsed = time.time() - self.start_time
        
        manifest = {
            "metadata": {
                "scan_timestamp": datetime.now(timezone.utc).isoformat(),
                "repository": "PEROPOROBTANTE/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL",
                "total_files_scanned": self.files_scanned,
                "total_methods_found": len(self.inventory),
                "ast_parse_failures": self.failures,
                "scan_duration_seconds": round(elapsed, 2)
            },
            "methods": {
                method_id: asdict(descriptor)
                for method_id, descriptor in sorted(self.inventory.items())
            },
            "_version": "2.0.0",
            "_comment": "Method inventory with AST hashing and cross-references"
        }
        
        return manifest
    
    def compute_checksum(self) -> str:
        """Compute deterministic checksum of inventory"""
        # Sort keys for determinism
        sorted_methods = sorted(self.inventory.items())
        
        # Compute hash of all AST hashes
        combined = ''.join(desc.ast_hash for _, desc in sorted_methods)
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="FARFAN Method Inventory Scanner")
    parser.add_argument('--repo-root', type=Path, default=Path('.'),
                       help='Repository root path')
    parser.add_argument('--output', type=Path, 
                       default=Path('method_inventory_verified.json'),
                       help='Output JSON file')
    parser.add_argument('--checksum', action='store_true',
                       help='Output only checksum')
    
    args = parser.parse_args()
    
    # Create scanner
    scanner = MethodInventoryScanner(args.repo_root)
    
    # Execute scan
    manifest = scanner.scan()
    
    if args.checksum:
        # Output checksum only
        checksum = scanner.compute_checksum()
        print(checksum)
    else:
        # Save manifest
        with open(args.output, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"\n✅ Scan complete!")
        print(f"   Files scanned: {manifest['metadata']['total_files_scanned']}")
        print(f"   Methods found: {manifest['metadata']['total_methods_found']}")
        print(f"   Parse failures: {len(manifest['metadata']['ast_parse_failures'])}")
        print(f"   Duration: {manifest['metadata']['scan_duration_seconds']}s")
        print(f"   Output: {args.output}")
        
        # Compute and display checksum
        checksum = scanner.compute_checksum()
        print(f"   Checksum: {checksum}")
        
        return 0 if len(scanner.failures) == 0 else 1


if __name__ == '__main__':
    sys.exit(main())

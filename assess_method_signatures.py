#!/usr/bin/env python3
"""
Method Signature and Parametrization Assessment Tool
Validates all method signatures in modified files and identifies issues.
"""

import sys
import ast
import json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

@dataclass
class MethodSignature:
    """Represents a method signature for validation."""
    file: str
    class_name: str
    method_name: str
    line: int
    parameters: List[Dict[str, Any]]
    return_type: str
    has_type_hints: bool
    missing_hints: List[str]
    issues: List[str]

class SignatureValidator:
    """Validates method signatures for type hints and correctness."""
    
    def __init__(self, src_path: str = 'src'):
        self.src_path = Path(src_path)
        self.signatures: List[MethodSignature] = []
        
    def validate_file(self, file_path: Path) -> List[MethodSignature]:
        """Validate all method signatures in a file."""
        signatures = []
        
        if not file_path.exists():
            return signatures
            
        with open(file_path, 'r') as f:
            try:
                tree = ast.parse(f.read(), filename=str(file_path))
            except SyntaxError as e:
                print(f"❌ Syntax error in {file_path}: {e}")
                return signatures
        
        current_class = None
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                current_class = node.name
            elif isinstance(node, ast.FunctionDef):
                sig = self._analyze_function(node, file_path, current_class)
                signatures.append(sig)
                
        return signatures
    
    def _analyze_function(self, node: ast.FunctionDef, file_path: Path, class_name: str = None) -> MethodSignature:
        """Analyze a single function/method signature."""
        parameters = []
        missing_hints = []
        issues = []
        
        # Analyze parameters
        for arg in node.args.args:
            param_info = {
                'name': arg.arg,
                'has_annotation': arg.annotation is not None,
                'annotation': ast.unparse(arg.annotation) if arg.annotation else None
            }
            parameters.append(param_info)
            
            # Check for missing type hints (except self/cls)
            if arg.annotation is None and arg.arg not in ('self', 'cls'):
                missing_hints.append(arg.arg)
        
        # Check return type
        return_type = ast.unparse(node.returns) if node.returns else None
        has_type_hints = all(p['has_annotation'] or p['name'] in ('self', 'cls') for p in parameters)
        
        if has_type_hints and return_type:
            has_type_hints = True
        elif missing_hints or not return_type:
            if not node.name.startswith('_'):
                issues.append("Public method missing type hints")
        
        return MethodSignature(
            file=str(file_path),
            class_name=class_name,
            method_name=node.name,
            line=node.lineno,
            parameters=parameters,
            return_type=return_type or 'None',
            has_type_hints=has_type_hints,
            missing_hints=missing_hints,
            issues=issues
        )
    
    def validate_modified_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """Validate all modified files and return results."""
        results = {
            'total_methods': 0,
            'methods_with_hints': 0,
            'methods_without_hints': 0,
            'issues': [],
            'files': {}
        }
        
        for file_path in file_paths:
            path = Path(file_path)
            if not path.exists():
                results['issues'].append(f"File not found: {file_path}")
                continue
            
            signatures = self.validate_file(path)
            
            file_results = {
                'total': len(signatures),
                'with_hints': sum(1 for s in signatures if s.has_type_hints),
                'without_hints': sum(1 for s in signatures if not s.has_type_hints),
                'methods': [asdict(s) for s in signatures if s.issues or s.missing_hints]
            }
            
            results['files'][str(path)] = file_results
            results['total_methods'] += file_results['total']
            results['methods_with_hints'] += file_results['with_hints']
            results['methods_without_hints'] += file_results['without_hints']
        
        return results

def main():
    """Main execution function."""
    print("=" * 70)
    print("METHOD SIGNATURE & PARAMETRIZATION ASSESSMENT")
    print("=" * 70)
    print()
    
    # Files modified in the PR
    modified_files = [
        'src/orchestration/unit_layer.py',
        'src/cross_cutting_infrastrucuiture/capaz_calibration_parmetrization/calibration/__init__.py',
        'src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/__init__.py'
    ]
    
    validator = SignatureValidator()
    results = validator.validate_modified_files(modified_files)
    
    # Print summary
    print(f"📊 Summary:")
    print(f"  Total methods analyzed: {results['total_methods']}")
    print(f"  Methods with type hints: {results['methods_with_hints']}")
    print(f"  Methods without hints: {results['methods_without_hints']}")
    
    if results['methods_with_hints'] == results['total_methods']:
        print(f"  ✅ All methods have proper type hints")
    else:
        print(f"  ⚠️  {results['methods_without_hints']} methods need type hints")
    
    print()
    
    # Print per-file results
    print("📁 Per-file analysis:")
    print()
    
    for file_path, file_results in results['files'].items():
        print(f"  {Path(file_path).name}:")
        print(f"    Total methods: {file_results['total']}")
        print(f"    With hints: {file_results['with_hints']}")
        print(f"    Without hints: {file_results['without_hints']}")
        
        if file_results['methods']:
            print(f"    ⚠️  Methods needing attention:")
            for method in file_results['methods'][:5]:  # Show first 5
                print(f"      - {method['method_name']} (line {method['line']})")
                if method['missing_hints']:
                    print(f"        Missing hints for: {', '.join(method['missing_hints'])}")
        else:
            print(f"    ✅ All methods properly typed")
        print()
    
    # Save detailed report
    report_path = Path('method_signature_assessment.json')
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📄 Detailed report saved to: {report_path}")
    print()
    
    # Overall status
    if results['issues']:
        print("❌ Issues found:")
        for issue in results['issues']:
            print(f"  - {issue}")
        return 1
    
    if results['methods_without_hints'] == 0:
        print("✅ All method signatures are properly typed")
        return 0
    else:
        print("⚠️  Some methods lack complete type hints (see report)")
        return 0  # Don't fail, just warn

if __name__ == '__main__':
    sys.exit(main())

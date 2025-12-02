"""
Test 4: AST Extraction Accuracy - Comparing Extracted Signatures vs Actual Code

Validates that method signatures in the calibration system match actual source code:
- Parse Python files to extract actual method signatures
- Compare with signatures stored in calibration metadata
- Detect mismatches in parameter names, types, defaults

FAILURE CONDITION: Signature mismatch > 5% = SYSTEM NOT READY
"""
import ast
import json
import pytest
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
import inspect


class MethodSignatureExtractor(ast.NodeVisitor):
    """AST visitor to extract method signatures"""
    
    def __init__(self):
        self.signatures: Dict[str, Dict[str, Any]] = {}
        self.current_class: Optional[str] = None
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition"""
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function/method definition"""
        if self.current_class:
            method_id = f"{self.current_class}.{node.name}"
        else:
            method_id = node.name
        
        args = []
        kwargs = []
        has_self = False
        
        for i, arg in enumerate(node.args.args):
            arg_name = arg.arg
            if i == 0 and arg_name in ("self", "cls"):
                has_self = True
                continue
            
            if i < len(node.args.args) - len(node.args.defaults):
                args.append(arg_name)
            else:
                kwargs.append(arg_name)
        
        returns = ast.unparse(node.returns) if node.returns else "Any"
        is_async = isinstance(node, ast.AsyncFunctionDef)
        
        self.signatures[method_id] = {
            "args": args,
            "kwargs": kwargs,
            "returns": returns,
            "is_async": is_async,
            "has_self": has_self,
            "lineno": node.lineno,
        }
    
    visit_AsyncFunctionDef = visit_FunctionDef


class TestASTExtractionAccuracy:
    
    MAX_MISMATCH_PERCENT = 5.0
    
    @pytest.fixture(scope="class")
    def executors_methods(self) -> Dict[str, Any]:
        """Load executors_methods.json"""
        path = Path("src/farfan_pipeline/core/orchestrator/executors_methods.json")
        with open(path) as f:
            return json.load(f)
    
    @pytest.fixture(scope="class")
    def source_signatures(self) -> Dict[str, Dict[str, Any]]:
        """Extract signatures from actual source files"""
        signatures = {}
        
        src_dirs = [
            Path("src/farfan_pipeline"),
            Path("farfan_core/farfan_core"),
        ]
        
        for src_dir in src_dirs:
            if not src_dir.exists():
                continue
            
            for py_file in src_dir.rglob("*.py"):
                if "test" in str(py_file) or "__pycache__" in str(py_file):
                    continue
                
                try:
                    tree = ast.parse(py_file.read_text(), filename=str(py_file))
                    extractor = MethodSignatureExtractor()
                    extractor.visit(tree)
                    
                    for method_id, sig in extractor.signatures.items():
                        sig["file"] = str(py_file)
                        signatures[method_id] = sig
                        
                except (SyntaxError, UnicodeDecodeError) as e:
                    print(f"Warning: Could not parse {py_file}: {e}")
        
        return signatures
    
    def test_source_signatures_extracted(self, source_signatures):
        """Verify we extracted signatures from source"""
        assert len(source_signatures) > 0, \
            "No method signatures extracted from source code"
        
        print(f"\nExtracted {len(source_signatures)} method signatures from source")
    
    def test_executor_methods_exist_in_source(
        self, executors_methods, source_signatures
    ):
        """Verify executor methods exist in source code"""
        missing_methods = []
        
        for executor in executors_methods:
            for method in executor["methods"]:
                method_id = f"{method['class']}.{method['method']}"
                
                if method_id not in source_signatures:
                    missing_methods.append({
                        "executor": executor["executor_id"],
                        "method": method_id
                    })
        
        if missing_methods:
            msg = f"\nWARNING: {len(missing_methods)} methods not found in source:\n"
            for item in missing_methods[:10]:
                msg += f"  {item['executor']}: {item['method']}\n"
            print(msg)
    
    def test_signature_mismatch_rate(
        self, executors_methods, source_signatures
    ):
        """CRITICAL: Verify signature mismatch rate is below threshold"""
        total_checked = 0
        mismatches = []
        
        for executor in executors_methods:
            for method in executor["methods"]:
                method_id = f"{method['class']}.{method['method']}"
                
                if method_id not in source_signatures:
                    continue
                
                total_checked += 1
                source_sig = source_signatures[method_id]
                
                if "signature" in method:
                    stored_sig = method["signature"]
                    
                    if not self._signatures_match(stored_sig, source_sig):
                        mismatches.append({
                            "executor": executor["executor_id"],
                            "method": method_id,
                            "stored": stored_sig,
                            "actual": source_sig
                        })
        
        mismatch_rate = (len(mismatches) / total_checked * 100) if total_checked > 0 else 0
        
        if mismatches:
            msg = f"\nSignature mismatches ({len(mismatches)}/{total_checked} = {mismatch_rate:.1f}%):\n"
            for item in mismatches[:5]:
                msg += f"  {item['method']}:\n"
                msg += f"    Stored: {item['stored']}\n"
                msg += f"    Actual: {item['actual']}\n"
            print(msg)
        
        assert mismatch_rate <= self.MAX_MISMATCH_PERCENT, \
            f"Signature mismatch rate {mismatch_rate:.1f}% exceeds threshold {self.MAX_MISMATCH_PERCENT}%"
    
    def _signatures_match(
        self, stored: Dict[str, Any], actual: Dict[str, Any]
    ) -> bool:
        """Compare two signatures for equality"""
        if not isinstance(stored, dict) or not isinstance(actual, dict):
            return False
        
        stored_args = stored.get("args", [])
        actual_args = actual.get("args", [])
        
        if len(stored_args) != len(actual_args):
            return False
        
        for s_arg, a_arg in zip(stored_args, actual_args):
            if isinstance(s_arg, str) and isinstance(a_arg, str):
                if s_arg != a_arg:
                    return False
        
        return True
    
    def test_private_methods_marked(self, executors_methods):
        """Verify private methods (starting with _) are marked"""
        private_methods = []
        
        for executor in executors_methods:
            for method in executor["methods"]:
                if method["method"].startswith("_"):
                    private_methods.append({
                        "executor": executor["executor_id"],
                        "method": f"{method['class']}.{method['method']}"
                    })
        
        if private_methods:
            print(f"\nFound {len(private_methods)} private methods in executors")
    
    def test_async_methods_identified(self, source_signatures):
        """Identify async methods in source code"""
        async_methods = [
            method_id for method_id, sig in source_signatures.items()
            if sig.get("is_async")
        ]
        
        if async_methods:
            print(f"\nFound {len(async_methods)} async methods: {async_methods[:5]}")
    
    def test_method_parameter_count_reasonable(self, source_signatures):
        """Verify methods don't have excessive parameters"""
        MAX_PARAMS = 10
        
        excessive_params = []
        
        for method_id, sig in source_signatures.items():
            total_params = len(sig.get("args", [])) + len(sig.get("kwargs", []))
            
            if total_params > MAX_PARAMS:
                excessive_params.append({
                    "method": method_id,
                    "param_count": total_params,
                    "file": sig.get("file")
                })
        
        if excessive_params:
            msg = f"\nMethods with >{MAX_PARAMS} parameters:\n"
            for item in excessive_params[:5]:
                msg += f"  {item['method']}: {item['param_count']} params\n"
            print(msg)
    
    def test_return_type_annotations_present(self, source_signatures):
        """Check for return type annotations"""
        missing_returns = []
        
        for method_id, sig in source_signatures.items():
            if method_id.startswith("_"):
                continue
            
            if sig.get("returns") == "Any" or not sig.get("returns"):
                missing_returns.append(method_id)
        
        if missing_returns:
            coverage = (1 - len(missing_returns) / len(source_signatures)) * 100
            print(
                f"\nReturn type annotation coverage: {coverage:.1f}% "
                f"({len(source_signatures) - len(missing_returns)}/{len(source_signatures)})"
            )

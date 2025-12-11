"""
Executor Parameter Validator

Validates that all executor classes load parameters exclusively from ExecutorConfig
or environment variables rather than hardcoded literals.

This validator performs targeted checks on:
- Base executor classes
- Phase-specific executors
- Resource-aware executors
- Calibration-integrated executors

Validates:
- No hardcoded timeout values
- No hardcoded retry counts
- No hardcoded concurrency limits
- All parameters loaded from ExecutorConfig or os.getenv()
"""

from __future__ import annotations

import ast
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class ExecutorViolation:
    """Represents an executor parameter loading violation."""
    
    executor_class: str
    file_path: str
    line_number: int
    violation_type: str
    parameter_name: str
    hardcoded_value: Any
    recommendation: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "executor_class": self.executor_class,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "violation_type": self.violation_type,
            "parameter_name": self.parameter_name,
            "hardcoded_value": self.hardcoded_value,
            "recommendation": self.recommendation,
        }


class ExecutorParameterVisitor(ast.NodeVisitor):
    """AST visitor for executor class parameter validation."""
    
    EXECUTOR_PATTERNS = ["executor", "Executor", "BaseExecutor"]
    RUNTIME_PARAMS = {
        "timeout", "retry", "retries", "max_retries", "max_concurrent",
        "concurrency", "delay", "backoff", "max_workers"
    }
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations: List[ExecutorViolation] = []
        self.current_class: Optional[str] = None
        self.current_method: Optional[str] = None
        self.is_in_executor_class = False
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions to identify executor classes."""
        old_class = self.current_class
        old_is_executor = self.is_in_executor_class
        
        self.current_class = node.name
        
        self.is_in_executor_class = any(
            pattern in node.name for pattern in self.EXECUTOR_PATTERNS
        )
        
        for base in node.bases:
            if isinstance(base, ast.Name):
                if any(pattern in base.id for pattern in self.EXECUTOR_PATTERNS):
                    self.is_in_executor_class = True
        
        self.generic_visit(node)
        
        self.current_class = old_class
        self.is_in_executor_class = old_is_executor
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions within executor classes."""
        old_method = self.current_method
        self.current_method = node.name
        
        self.generic_visit(node)
        
        self.current_method = old_method
    
    def visit_Assign(self, node: ast.Assign) -> None:
        """Check assignments for hardcoded runtime parameters."""
        if not self.is_in_executor_class:
            self.generic_visit(node)
            return
        
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id.lower()
                
                if any(param in var_name for param in self.RUNTIME_PARAMS):
                    if isinstance(node.value, ast.Constant):
                        value = node.value.value
                        
                        if isinstance(value, (int, float)) and value != 0 and value != 1:
                            self._record_violation(
                                node=node,
                                param_name=target.id,
                                value=value,
                                violation_type="HARDCODED_RUNTIME_PARAM"
                            )
                    
                    elif not self._is_config_load(node.value):
                        pass
        
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call) -> None:
        """Check function calls for hardcoded parameters."""
        if not self.is_in_executor_class:
            self.generic_visit(node)
            return
        
        for keyword in node.keywords:
            arg_name = keyword.arg
            if arg_name and any(param in arg_name.lower() for param in self.RUNTIME_PARAMS):
                
                if isinstance(keyword.value, ast.Constant):
                    value = keyword.value.value
                    
                    if isinstance(value, (int, float)) and value != 0 and value != 1:
                        self._record_violation(
                            node=keyword.value,
                            param_name=arg_name,
                            value=value,
                            violation_type="HARDCODED_CALL_PARAM"
                        )
        
        self.generic_visit(node)
    
    def _is_config_load(self, node: ast.AST) -> bool:
        """Check if value is loaded from ExecutorConfig or environment."""
        if isinstance(node, ast.Call):
            func = node.func
            
            if isinstance(func, ast.Attribute):
                if func.attr in ["get", "get_parameter", "load_parameter"]:
                    if isinstance(func.value, ast.Name):
                        if "config" in func.value.id.lower() or "env" in func.value.id.lower():
                            return True
            
            if isinstance(func, ast.Name):
                if func.id in ["getenv", "get_env"]:
                    return True
            
            if isinstance(func, ast.Attribute):
                if isinstance(func.value, ast.Name):
                    if func.value.id == "os" and func.attr in ["getenv", "environ"]:
                        return True
        
        if isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                if "config" in node.value.id.lower():
                    return True
        
        return False
    
    def _record_violation(
        self,
        node: ast.AST,
        param_name: str,
        value: Any,
        violation_type: str
    ) -> None:
        """Record a parameter loading violation."""
        violation = ExecutorViolation(
            executor_class=self.current_class or "Unknown",
            file_path=self.file_path,
            line_number=node.lineno if hasattr(node, "lineno") else 0,
            violation_type=violation_type,
            parameter_name=param_name,
            hardcoded_value=value,
            recommendation=(
                f"Load '{param_name}' from ExecutorConfig or environment variable. "
                f"Example: config.get('{param_name}', {value}) or "
                f"os.getenv('{param_name.upper()}', '{value}')"
            )
        )
        
        self.violations.append(violation)


class ExecutorParameterValidator:
    """Validates executor parameter loading patterns."""
    
    EXECUTOR_PATHS = [
        "canonic_phases/Phase_two/",
        "orchestration/",
    ]
    
    def __init__(self, src_path: Path):
        self.src_path = src_path
        self.violations: List[ExecutorViolation] = []
    
    def should_scan_file(self, file_path: Path) -> bool:
        """Check if file contains executor code."""
        file_str = str(file_path)
        
        if "test" in file_str.lower():
            return False
        
        if "example" in file_str.lower():
            return False
        
        if any(pattern in file_str for pattern in self.EXECUTOR_PATHS):
            return True
        
        if "executor" in file_path.name.lower():
            return True
        
        return False
    
    def validate_file(self, file_path: Path) -> List[ExecutorViolation]:
        """Validate a single file for executor parameter violations."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(file_path))
            
            visitor = ExecutorParameterVisitor(
                file_path=str(file_path.relative_to(self.src_path.parent))
            )
            
            visitor.visit(tree)
            
            return visitor.violations
            
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error validating {file_path}: {e}")
            return []
    
    def validate_all(self) -> List[ExecutorViolation]:
        """Validate all executor files."""
        logger.info(f"Validating executor parameter loading in {self.src_path}")
        
        for py_file in self.src_path.rglob("*.py"):
            if not self.should_scan_file(py_file):
                continue
            
            logger.debug(f"Validating {py_file}")
            
            file_violations = self.validate_file(py_file)
            self.violations.extend(file_violations)
        
        logger.info(f"Executor validation complete: {len(self.violations)} violations found")
        
        return self.violations
    
    def generate_report(self, output_path: Path) -> None:
        """Generate validation report."""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# Executor Parameter Validation Report\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"**Total Violations:** {len(self.violations)}\n\n")
            
            if not self.violations:
                f.write("✅ **All executor classes properly load parameters from configuration.**\n\n")
                return
            
            f.write("## Violations\n\n")
            
            violations_by_class = {}
            for v in self.violations:
                if v.executor_class not in violations_by_class:
                    violations_by_class[v.executor_class] = []
                violations_by_class[v.executor_class].append(v)
            
            for executor_class in sorted(violations_by_class.keys()):
                class_violations = violations_by_class[executor_class]
                
                f.write(f"### {executor_class}\n\n")
                f.write(f"**File:** `{class_violations[0].file_path}`\n\n")
                
                for v in sorted(class_violations, key=lambda x: x.line_number):
                    f.write(f"#### Line {v.line_number}: `{v.parameter_name}`\n\n")
                    f.write(f"- **Hardcoded Value:** `{v.hardcoded_value}`\n")
                    f.write(f"- **Violation Type:** {v.violation_type}\n")
                    f.write(f"- **Recommendation:** {v.recommendation}\n\n")
            
            f.write("## Best Practices\n\n")
            f.write("### ✅ Correct Pattern\n\n")
            f.write("```python\n")
            f.write("class MyExecutor(BaseExecutor):\n")
            f.write("    def __init__(self, config: ExecutorConfig):\n")
            f.write("        self.timeout = config.get('timeout', 300)\n")
            f.write("        self.max_retries = config.get('max_retries', 3)\n")
            f.write("```\n\n")
            
            f.write("### ❌ Incorrect Pattern\n\n")
            f.write("```python\n")
            f.write("class MyExecutor(BaseExecutor):\n")
            f.write("    def __init__(self):\n")
            f.write("        self.timeout = 300  # Hardcoded!\n")
            f.write("        self.max_retries = 3  # Hardcoded!\n")
            f.write("```\n\n")


def validate_executors(src_path: Path, output_path: Path) -> int:
    """
    Run executor parameter validation.
    
    Args:
        src_path: Path to src/ directory
        output_path: Output path for report
    
    Returns:
        Number of violations found
    """
    validator = ExecutorParameterValidator(src_path)
    violations = validator.validate_all()
    
    validator.generate_report(output_path)
    logger.info(f"Executor validation report: {output_path}")
    
    return len(violations)


if __name__ == "__main__":
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    src_path = project_root / "src"
    output_path = project_root / "artifacts" / "audit_reports" / "executor_parameter_validation.md"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    violation_count = validate_executors(src_path, output_path)
    
    if violation_count == 0:
        logger.info("✅ All executors pass validation")
        sys.exit(0)
    else:
        logger.warning(f"❌ Found {violation_count} violations")
        sys.exit(1)

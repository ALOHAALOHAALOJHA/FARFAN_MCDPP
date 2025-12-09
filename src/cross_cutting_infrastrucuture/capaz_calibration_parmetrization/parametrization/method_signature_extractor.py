"""
Method Signature Extractor - Signature-Based Parametrization Analysis

Scans all executor methods and core scripts via AST parsing to extract:
- required_inputs
- optional_inputs
- critical_optional
- output_type
- output_range

Stores results in method_signatures.json with normalized notation (module.Class.method).
Detects hardcoded parameters for migration to COHORT_2024_executor_config.json.

COHORT_2024 - REFACTOR_WAVE_2024_12
"""

from __future__ import annotations

import ast
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ParameterSignature:
    name: str
    type_annotation: str | None
    default_value: Any | None
    is_required: bool
    is_critical: bool = False


@dataclass
class MethodSignature:
    module: str
    class_name: str | None
    method_name: str
    required_inputs: list[str]
    optional_inputs: list[str]
    critical_optional: list[str]
    output_type: str | None
    output_range: dict[str, Any] | None
    hardcoded_parameters: list[dict[str, Any]]
    docstring: str | None
    line_number: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": self.module,
            "class_name": self.class_name,
            "method_name": self.method_name,
            "required_inputs": self.required_inputs,
            "optional_inputs": self.optional_inputs,
            "critical_optional": self.critical_optional,
            "output_type": self.output_type,
            "output_range": self.output_range,
            "hardcoded_parameters": self.hardcoded_parameters,
            "docstring": self.docstring,
            "line_number": self.line_number,
        }

    @property
    def normalized_name(self) -> str:
        if self.class_name:
            return f"{self.module}.{self.class_name}.{self.method_name}"
        return f"{self.module}.{self.method_name}"


class HardcodedParameterDetector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.hardcoded_params: list[dict[str, Any]] = []
        self.current_function: str | None = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function

    def visit_Assign(self, node: ast.Assign) -> None:
        self._check_hardcoded_assignment(node)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._check_hardcoded_assignment(node)
        self.generic_visit(node)

    def _check_hardcoded_assignment(self, node: ast.Assign | ast.AnnAssign) -> None:
        if not self.current_function:
            return

        value_node = node.value
        if not value_node:
            return

        hardcoded_value = self._extract_literal_value(value_node)
        if hardcoded_value is not None:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.hardcoded_params.append({
                            "function": self.current_function,
                            "variable": target.id,
                            "value": hardcoded_value,
                            "line": node.lineno,
                            "type": type(hardcoded_value).__name__,
                        })
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                self.hardcoded_params.append({
                    "function": self.current_function,
                    "variable": node.target.id,
                    "value": hardcoded_value,
                    "line": node.lineno,
                    "type": type(hardcoded_value).__name__,
                })

    def _extract_literal_value(self, node: ast.expr) -> Any:
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, (ast.List, ast.Tuple)):
            return [self._extract_literal_value(elt) for elt in node.elts]
        elif isinstance(node, ast.Dict):
            keys = [self._extract_literal_value(k) for k in node.keys if k]
            values = [self._extract_literal_value(v) for v in node.values]
            return dict(zip(keys, values))
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            value = self._extract_literal_value(node.operand)
            return -value if isinstance(value, (int, float)) else None
        return None


class MethodSignatureExtractor:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.signatures: dict[str, MethodSignature] = {}
        self.critical_params = {
            "threshold", "confidence", "alpha", "beta", "prior",
            "temperature", "max_tokens", "timeout", "seed",
            "max_iter", "tol", "n_samples", "min_samples"
        }

    def scan_repository(self, include_patterns: list[str] | None = None) -> None:
        if include_patterns is None:
            include_patterns = [
                "**/executors.py",
                "**/executor*.py",
                "**/methods_dispensary/**/*.py",
                "**/farfan_pipeline/**/*.py",
                "**/canonic_phases/**/*.py",
            ]

        python_files: list[Path] = []
        for pattern in include_patterns:
            python_files.extend(self.repo_root.glob(pattern))

        python_files = list(set(python_files))
        logger.info(f"Scanning {len(python_files)} Python files")

        for file_path in python_files:
            try:
                self._scan_file(file_path)
            except Exception as e:
                logger.warning(f"Failed to scan {file_path}: {e}")

    def _scan_file(self, file_path: Path) -> None:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()
        except Exception as e:
            logger.warning(f"Failed to read {file_path}: {e}")
            return

        try:
            tree = ast.parse(source_code, filename=str(file_path))
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
            return

        module_name = self._get_module_name(file_path)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._extract_class_methods(node, module_name, source_code)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if self._is_top_level_function(node, tree):
                    self._extract_function_signature(node, module_name, None, source_code)

    def _get_module_name(self, file_path: Path) -> str:
        try:
            rel_path = file_path.relative_to(self.repo_root / "src")
            module_parts = list(rel_path.parts[:-1]) + [rel_path.stem]
            return ".".join(module_parts)
        except ValueError:
            return file_path.stem

    def _is_top_level_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef, tree: ast.Module) -> bool:
        return node in tree.body

    def _extract_class_methods(self, class_node: ast.ClassDef, module_name: str, source_code: str) -> None:
        class_name = class_node.name

        for node in class_node.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._extract_function_signature(node, module_name, class_name, source_code)

    def _extract_function_signature(
        self,
        func_node: ast.FunctionDef | ast.AsyncFunctionDef,
        module_name: str,
        class_name: str | None,
        source_code: str
    ) -> None:
        method_name = func_node.name

        if method_name.startswith("_") and not method_name.startswith("__"):
            return

        required_inputs: list[str] = []
        optional_inputs: list[str] = []
        critical_optional: list[str] = []

        args = func_node.args
        defaults = args.defaults
        num_defaults = len(defaults)
        num_args = len(args.args)
        num_required = num_args - num_defaults

        for i, arg in enumerate(args.args):
            arg_name = arg.arg
            if arg_name in ("self", "cls"):
                continue

            type_annotation = self._get_type_annotation(arg.annotation)

            if i < num_required:
                required_inputs.append(arg_name)
            else:
                optional_inputs.append(arg_name)
                if arg_name.lower() in self.critical_params:
                    critical_optional.append(arg_name)

        for arg in args.kwonlyargs:
            arg_name = arg.arg
            optional_inputs.append(arg_name)
            if arg_name.lower() in self.critical_params:
                critical_optional.append(arg_name)

        output_type = self._get_type_annotation(func_node.returns)

        hardcoded_detector = HardcodedParameterDetector()
        hardcoded_detector.visit(func_node)

        signature = MethodSignature(
            module=module_name,
            class_name=class_name,
            method_name=method_name,
            required_inputs=required_inputs,
            optional_inputs=optional_inputs,
            critical_optional=critical_optional,
            output_type=output_type,
            output_range=self._infer_output_range(output_type),
            hardcoded_parameters=hardcoded_detector.hardcoded_params,
            docstring=ast.get_docstring(func_node),
            line_number=func_node.lineno,
        )

        self.signatures[signature.normalized_name] = signature

    def _get_type_annotation(self, annotation: ast.expr | None) -> str | None:
        if annotation is None:
            return None
        return ast.unparse(annotation)

    def _infer_output_range(self, output_type: str | None) -> dict[str, Any] | None:
        if not output_type:
            return None

        output_type_lower = output_type.lower()

        if "bool" in output_type_lower:
            return {"type": "boolean", "values": [True, False]}
        elif "int" in output_type_lower:
            return {"type": "integer", "min": None, "max": None}
        elif "float" in output_type_lower:
            return {"type": "float", "min": None, "max": None}
        elif "str" in output_type_lower:
            return {"type": "string"}
        elif "list" in output_type_lower or "list[" in output_type:
            return {"type": "array"}
        elif "dict" in output_type_lower or "dict[" in output_type:
            return {"type": "object"}
        elif "tuple" in output_type_lower:
            return {"type": "tuple"}

        return {"type": "unknown", "annotation": output_type}

    def export_signatures(self, output_path: Path) -> None:
        output_data = {
            "_metadata": {
                "cohort_id": "COHORT_2024",
                "creation_date": "2024-12-15T00:00:00+00:00",
                "wave_version": "REFACTOR_WAVE_2024_12",
                "total_signatures": len(self.signatures),
            },
            "signatures": {
                name: sig.to_dict() for name, sig in sorted(self.signatures.items())
            }
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Exported {len(self.signatures)} method signatures to {output_path}")

    def export_hardcoded_migration_report(self, output_path: Path) -> None:
        migration_candidates: list[dict[str, Any]] = []

        for sig_name, sig in sorted(self.signatures.items()):
            if sig.hardcoded_parameters:
                for param in sig.hardcoded_parameters:
                    migration_candidates.append({
                        "signature": sig_name,
                        "module": sig.module,
                        "class": sig.class_name,
                        "method": sig.method_name,
                        "hardcoded_variable": param["variable"],
                        "hardcoded_value": param["value"],
                        "hardcoded_type": param["type"],
                        "line_number": param["line"],
                        "migration_target": "COHORT_2024_executor_config.json",
                        "suggested_key": f"{sig.module}.{sig.class_name or sig.method_name}.{param['variable']}",
                    })

        report_data = {
            "_metadata": {
                "cohort_id": "COHORT_2024",
                "creation_date": "2024-12-15T00:00:00+00:00",
                "wave_version": "REFACTOR_WAVE_2024_12",
                "total_candidates": len(migration_candidates),
            },
            "migration_candidates": migration_candidates
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Exported {len(migration_candidates)} hardcoded parameter migration candidates to {output_path}")

    def generate_summary_report(self) -> dict[str, Any]:
        total_methods = len(self.signatures)
        methods_with_required = sum(1 for sig in self.signatures.values() if sig.required_inputs)
        methods_with_optional = sum(1 for sig in self.signatures.values() if sig.optional_inputs)
        methods_with_critical = sum(1 for sig in self.signatures.values() if sig.critical_optional)
        methods_with_hardcoded = sum(1 for sig in self.signatures.values() if sig.hardcoded_parameters)

        total_required = sum(len(sig.required_inputs) for sig in self.signatures.values())
        total_optional = sum(len(sig.optional_inputs) for sig in self.signatures.values())
        total_critical = sum(len(sig.critical_optional) for sig in self.signatures.values())
        total_hardcoded = sum(len(sig.hardcoded_parameters) for sig in self.signatures.values())

        modules = set(sig.module for sig in self.signatures.values())
        classes = set(sig.class_name for sig in self.signatures.values() if sig.class_name)

        return {
            "total_methods": total_methods,
            "methods_with_required_inputs": methods_with_required,
            "methods_with_optional_inputs": methods_with_optional,
            "methods_with_critical_optional": methods_with_critical,
            "methods_with_hardcoded_params": methods_with_hardcoded,
            "total_required_inputs": total_required,
            "total_optional_inputs": total_optional,
            "total_critical_optional": total_critical,
            "total_hardcoded_parameters": total_hardcoded,
            "unique_modules": len(modules),
            "unique_classes": len(classes),
        }


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    logger.info(f"Repository root: {repo_root}")

    extractor = MethodSignatureExtractor(repo_root)
    extractor.scan_repository()

    output_dir = repo_root / "src" / "cross_cutting_infrastrucuture" / "capaz_calibration_parmetrization" / "parametrization"

    signatures_path = output_dir / "method_signatures.json"
    extractor.export_signatures(signatures_path)

    migration_path = output_dir / "hardcoded_migration_report.json"
    extractor.export_hardcoded_migration_report(migration_path)

    summary = extractor.generate_summary_report()
    logger.info("Summary Report:")
    for key, value in summary.items():
        logger.info(f"  {key}: {value}")


if __name__ == "__main__":
    main()

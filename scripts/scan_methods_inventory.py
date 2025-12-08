#!/usr/bin/env python3
"""
Canonical Method Inventory Generator with Role Classification

Scans src/farfan_pipeline recursively, extracts all 1995+ methods with MODULE:CLASS.METHOD@LAYER notation,
applies three-stage decision automaton for role classification, and generates canonical inventory.

Decision Automaton:
    Q1: Analytically active? (keywords: score, compute, evaluate, analyze)
    Q2: Parametric? (keywords: threshold, weight, prior, alpha, beta)
    Q3: Safety-critical? (layer in {analyzer, processor, orchestrator})

Role Classification:
    - analyzer → SCORE_Q (analytical scoring/computation)
    - executor → SCORE_Q (D[1-6]Q[1-5]_Executor pattern)
    - processor → EXTRACT (data transformation)
    - ingestion → INGEST_PDM (document parsing)
    - utility → META_TOOL (helper functions)
    - orchestrator → TRANSFORM (workflow coordination)

Output Files:
    - canonical_method_inventory.json: Full inventory with role metadata
    - method_statistics.json: Counts per role/layer
    - excluded_methods.json: Utility methods excluded by pattern
"""

import ast
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

EXECUTOR_PATTERN = re.compile(r"D[1-6](?:_)?Q[1-5]", re.IGNORECASE)
MINIMUM_METHOD_COUNT = 200

ANALYTICAL_KEYWORDS = {
    "score",
    "compute",
    "evaluate",
    "analyze",
    "assess",
    "calculate",
    "infer",
    "measure",
    "rate",
    "rank",
    "validate",
    "judge",
}

PARAMETRIC_KEYWORDS = {
    "threshold",
    "weight",
    "prior",
    "alpha",
    "beta",
    "gamma",
    "lambda",
    "coefficient",
    "parameter",
    "calibration",
    "tuning",
    "optimization",
}

EXCLUSION_PATTERNS = [
    "_format_",
    "_log_",
    "__init__",
    "to_json",
    "to_dict",
    "visit_",
    "__repr__",
    "__str__",
    "_helper_",
    "_get_",
    "_set_",
    "__enter__",
    "__exit__",
    "__len__",
    "__iter__",
    "__next__",
    "from_dict",
    "__hash__",
    "__eq__",
]


@dataclass
class MethodMetadata:
    """Metadata for a single method with role classification"""

    method_id: str
    canonical_name: str
    module: str
    class_name: str | None
    method: str
    signature: str
    layer: str
    role: str
    is_executor: bool
    is_analytically_active: bool
    is_parametric: bool
    is_safety_critical: bool
    line_number: int
    source_file: str


class MethodInventoryScanner(ast.NodeVisitor):
    """AST visitor to extract and classify all methods"""

    def __init__(self, module_path: str, source_file: str):
        self.module_path = module_path
        self.source_file = source_file
        self.methods: list[MethodMetadata] = []
        self.class_stack: list[str] = []
        self.function_depth: int = 0

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Track class context for nested classes"""
        self.class_stack.append(node.name)
        self.generic_visit(node)
        self.class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Process function definitions (skip nested functions)"""
        if self.function_depth == 0:
            self._process_function(node)
        self.function_depth += 1
        self.generic_visit(node)
        self.function_depth -= 1

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Process async function definitions (skip nested functions)"""
        if self.function_depth == 0:
            self._process_function(node)
        self.function_depth += 1
        self.generic_visit(node)
        self.function_depth -= 1

    def _process_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Extract metadata and classify a single method"""
        method_name = node.name
        class_name = ".".join(self.class_stack) if self.class_stack else None

        args = [arg.arg for arg in node.args.args]
        signature = f"({', '.join(args)})"

        layer = self._determine_layer(class_name, method_name)
        is_executor = self._detect_executor_pattern(class_name)

        q1_analytical = self._is_analytically_active(method_name, class_name)
        q2_parametric = self._is_parametric(method_name, class_name)
        q3_safety_critical = layer in {"analyzer", "processor", "orchestrator"}

        role = self._classify_role(
            method_name,
            class_name,
            layer,
            is_executor,
            q1_analytical,
            q2_parametric,
            q3_safety_critical,
        )

        canonical_name = self._build_canonical_name(
            self.module_path, class_name, method_name, layer
        )
        method_id = self._build_method_id(self.module_path, class_name, method_name)

        metadata = MethodMetadata(
            method_id=method_id,
            canonical_name=canonical_name,
            module=self.source_file,
            class_name=class_name,
            method=method_name,
            signature=signature,
            layer=layer,
            role=role,
            is_executor=is_executor,
            is_analytically_active=q1_analytical,
            is_parametric=q2_parametric,
            is_safety_critical=q3_safety_critical,
            line_number=node.lineno,
            source_file=self.source_file,
        )

        self.methods.append(metadata)

    def _build_canonical_name(
        self, module_path: str, class_name: str | None, method_name: str, layer: str
    ) -> str:
        """Build canonical name: MODULE:CLASS.METHOD@LAYER"""
        if class_name:
            return f"{module_path}:{class_name}.{method_name}@{layer}"
        return f"{module_path}:{method_name}@{layer}"

    def _build_method_id(
        self, module_path: str, class_name: str | None, method_name: str
    ) -> str:
        """Build unique method ID: MODULE::CLASS::METHOD"""
        if class_name:
            return f"{module_path}::{class_name}::{method_name}"
        return f"{module_path}::{method_name}"

    def _determine_layer(self, class_name: str | None, method_name: str) -> str:
        """Determine layer based on path and naming patterns"""
        path_lower = self.source_file.lower().replace("\\", "/")
        method_lower = method_name.lower()
        class_lower = class_name.lower() if class_name else ""

        if "/orchestrator/" in path_lower or "orchestrator" in class_lower:
            return "orchestrator"

        if class_name and EXECUTOR_PATTERN.search(class_name):
            return "orchestrator"

        if any(
            kw in method_lower
            for kw in ["parse", "load", "ingest", "read_doc", "extract_raw"]
        ):
            return "ingestion"

        if "/processing/" in path_lower or any(
            kw in method_lower for kw in ["process", "transform", "normalize"]
        ):
            return "processor"

        if (
            "/analysis/" in path_lower
            or "analyzer" in class_lower
            or any(kw in method_lower for kw in ["analyze", "infer", "assess"])
        ):
            return "analyzer"

        if "/scoring/" in path_lower or "scorer" in class_lower:
            return "scorer"

        return "utility"

    def _detect_executor_pattern(self, class_name: str | None) -> bool:
        """Detect D[1-6]Q[1-5]_Executor pattern in class name"""
        return bool(class_name and EXECUTOR_PATTERN.search(class_name))

    def _is_analytically_active(self, method_name: str, class_name: str | None) -> bool:
        """Q1: Check for analytical activity keywords"""
        method_lower = method_name.lower()
        class_lower = class_name.lower() if class_name else ""

        return any(
            kw in method_lower or kw in class_lower for kw in ANALYTICAL_KEYWORDS
        )

    def _is_parametric(self, method_name: str, class_name: str | None) -> bool:
        """Q2: Check for parametric keywords"""
        method_lower = method_name.lower()
        class_lower = class_name.lower() if class_name else ""

        return any(
            kw in method_lower or kw in class_lower for kw in PARAMETRIC_KEYWORDS
        )

    def _classify_role(
        self,
        method_name: str,
        class_name: str | None,
        layer: str,
        is_executor: bool,
        q1_analytical: bool,
        q2_parametric: bool,
        q3_safety_critical: bool,
    ) -> str:
        """
        Classify method role based on decision automaton results

        Role Mapping:
        - Executor pattern → SCORE_Q
        - Analyzer + analytical → SCORE_Q
        - Processor → EXTRACT
        - Ingestion → INGEST_PDM
        - Orchestrator → TRANSFORM
        - Utility/helper → META_TOOL
        """
        _ = method_name, class_name, q2_parametric
        if is_executor:
            return "SCORE_Q"

        if layer == "analyzer" and q1_analytical:
            return "SCORE_Q"

        if layer == "scorer" and q1_analytical:
            return "SCORE_Q"

        if layer == "processor":
            return "EXTRACT"

        if layer == "ingestion":
            return "INGEST_PDM"

        if layer == "orchestrator":
            return "TRANSFORM"

        if q3_safety_critical and q1_analytical:
            return "SCORE_Q"

        return "META_TOOL"


def scan_python_file(file_path: Path, base_path: Path) -> list[MethodMetadata]:
    """Scan a single Python file for methods"""
    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source, filename=str(file_path))

        relative_path = file_path.relative_to(base_path)
        module_parts = list(relative_path.parts[:-1]) + [relative_path.stem]
        module_path = ".".join(module_parts)

        scanner = MethodInventoryScanner(module_path, str(file_path))
        scanner.visit(tree)

        return scanner.methods

    except SyntaxError as e:
        print(f"WARNING: Syntax error in {file_path}: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"WARNING: Error processing {file_path}: {e}", file=sys.stderr)
        return []


def scan_directory(
    directory: Path,
) -> tuple[list[MethodMetadata], list[MethodMetadata]]:
    """Scan directory for all methods, returning (included, excluded)"""
    all_methods = []
    python_files = sorted(directory.rglob("*.py"))

    print(f"Scanning {len(python_files)} Python files in {directory}...")

    for file_path in python_files:
        methods = scan_python_file(file_path, directory)
        all_methods.extend(methods)

    included = []
    excluded = []

    for method in all_methods:
        if should_exclude(method.method):
            excluded.append(method)
        else:
            included.append(method)

    print(f"  Total methods found: {len(all_methods)}")
    print(f"  Included: {len(included)}")
    print(f"  Excluded: {len(excluded)}")

    return included, excluded


def should_exclude(method_name: str) -> bool:
    """Check if method matches exclusion patterns"""
    return any(pattern in method_name for pattern in EXCLUSION_PATTERNS)


def generate_statistics(methods: list[MethodMetadata]) -> dict[str, int | dict[str, int]]:
    """Generate statistics by role and layer"""
    by_role: dict[str, int] = {}
    by_layer: dict[str, int] = {}
    executor_count = 0
    analytically_active_count = 0
    parametric_count = 0
    safety_critical_count = 0

    for method in methods:
        role = method.role
        layer = method.layer

        by_role[role] = by_role.get(role, 0) + 1
        by_layer[layer] = by_layer.get(layer, 0) + 1

        if method.is_executor:
            executor_count += 1
        if method.is_analytically_active:
            analytically_active_count += 1
        if method.is_parametric:
            parametric_count += 1
        if method.is_safety_critical:
            safety_critical_count += 1

    return {
        "total_methods": len(methods),
        "by_role": by_role,
        "by_layer": by_layer,
        "executor_count": executor_count,
        "analytically_active_count": analytically_active_count,
        "parametric_count": parametric_count,
        "safety_critical_count": safety_critical_count,
    }


def convert_to_output_format(method: MethodMetadata) -> dict[str, str | bool | None]:
    """Convert MethodMetadata to output dictionary format"""
    return {
        "method_id": method.method_id,
        "canonical_name": method.canonical_name,
        "module": method.module,
        "class": method.class_name,
        "method": method.method,
        "signature": method.signature,
        "layer": method.layer,
        "role": method.role,
        "is_executor": method.is_executor,
    }


def save_inventory(
    methods: list[MethodMetadata],
    excluded: list[MethodMetadata],
    output_dir: Path,
) -> None:
    """Save canonical method inventory and statistics"""
    inventory_dict = {}
    for method in methods:
        inventory_dict[method.method_id] = convert_to_output_format(method)

    stats = generate_statistics(methods)

    excluded_list = []
    for method in excluded:
        reason = (
            "trivial_formatter" if "__init__" in method.method else "utility_formatter"
        )
        excluded_list.append(
            {
                "canonical_id": method.canonical_name.split("@")[0],
                "reason": reason,
                "method_name": method.method,
                "file_path": method.source_file.replace("src/farfan_pipeline/", ""),
                "line_number": method.line_number,
            }
        )

    excluded_data = {
        "metadata": {
            "total_excluded": len(excluded),
            "exclusion_patterns": EXCLUSION_PATTERNS,
        },
        "excluded_methods": excluded_list,
    }

    inventory_file = output_dir / "canonical_method_inventory.json"
    stats_file = output_dir / "method_statistics.json"
    excluded_file = output_dir / "excluded_methods.json"

    with open(inventory_file, "w", encoding="utf-8") as f:
        json.dump(inventory_dict, f, indent=2, ensure_ascii=False)

    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    with open(excluded_file, "w", encoding="utf-8") as f:
        json.dump(excluded_data, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*70}")
    print("INVENTORY GENERATION COMPLETE")
    print(f"{'='*70}")
    print(f"Canonical inventory: {inventory_file}")
    print(f"Statistics: {stats_file}")
    print(f"Excluded methods: {excluded_file}")
    print(f"\n{'='*70}")
    print("STATISTICS SUMMARY")
    print(f"{'='*70}")
    print(f"Total methods: {stats['total_methods']}")
    print(f"Executor count (D[1-6]Q[1-5] pattern): {stats['executor_count']}")
    print(f"Analytically active (Q1): {stats['analytically_active_count']}")
    print(f"Parametric (Q2): {stats['parametric_count']}")
    print(f"Safety-critical (Q3): {stats['safety_critical_count']}")
    print("\nBy Role:")
    by_role = stats["by_role"]
    if isinstance(by_role, dict):
        for role, count in sorted(by_role.items(), key=lambda x: -x[1]):
            print(f"  {role}: {count}")
    print("\nBy Layer:")
    by_layer = stats["by_layer"]
    if isinstance(by_layer, dict):
        for layer, count in sorted(by_layer.items(), key=lambda x: -x[1]):
            print(f"  {layer}: {count}")


def main() -> None:
    """Main entry point"""
    pipeline_dir = Path("src/farfan_pipeline")
    output_dir = Path(".")

    if not pipeline_dir.exists():
        print(f"ERROR: Directory {pipeline_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    print("=" * 70)
    print("CANONICAL METHOD INVENTORY GENERATOR")
    print("=" * 70)
    print(f"Source directory: {pipeline_dir}")
    print(f"Output directory: {output_dir}")
    print("Notation: MODULE:CLASS.METHOD@LAYER")
    print("=" * 70)

    included_methods, excluded_methods = scan_directory(pipeline_dir)

    if len(included_methods) < MINIMUM_METHOD_COUNT:
        print(
            f"\nWARNING: Low method count ({len(included_methods)}), expected 1995+",
            file=sys.stderr,
        )

    save_inventory(included_methods, excluded_methods, output_dir)

    print(f"\n{'='*70}")
    print("SUCCESS: Canonical method inventory generated")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()

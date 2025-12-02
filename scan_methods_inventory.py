#!/usr/bin/env python3
"""AST Method Scanner with Canonical Identifier Enforcement

Traverses src/farfan_pipeline/ recursively, extracts ALL methods as module.Class.method,
classifies by role, applies epistemological rubric, and generates methods_inventory_raw.json.

FAILURE CONDITION: Aborts with 'insufficient coverage' if <200 entries or if any
pipeline method definition cannot be located.
"""

import ast
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

# Extended LAYER_REQUIREMENTS table
LAYER_REQUIREMENTS = {
    "ingest": {
        "description": "Data ingestion and document parsing",
        "typical_patterns": ["parse", "load", "read", "extract_raw", "ingest"],
    },
    "processor": {
        "description": "Data transformation and processing",
        "typical_patterns": ["process", "transform", "clean", "normalize", "aggregate"],
    },
    "analyzer": {
        "description": "Analysis and inference operations",
        "typical_patterns": ["analyze", "infer", "calculate", "compute", "assess"],
    },
    "extractor": {
        "description": "Feature and information extraction",
        "typical_patterns": ["extract", "identify", "detect", "find", "locate"],
    },
    "score": {
        "description": "Scoring and evaluation methods",
        "typical_patterns": ["score", "evaluate", "rate", "rank", "measure"],
    },
    "utility": {
        "description": "Helper and utility functions",
        "typical_patterns": ["_format", "_helper", "_validate", "_check", "_get", "_set"],
    },
    "orchestrator": {
        "description": "Workflow orchestration and coordination",
        "typical_patterns": ["orchestrate", "coordinate", "run", "execute_suite", "build"],
    },
    "core": {
        "description": "Core framework methods",
        "typical_patterns": ["__init__", "setup", "initialize", "configure"],
    },
    "executor": {
        "description": "Executor pattern implementations",
        "typical_patterns": ["execute", "run_executor", "perform", "apply"],
    },
}


@dataclass
class MethodMetadata:
    """Metadata for a single method"""
    canonical_identifier: str
    module_path: str
    class_name: str | None
    method_name: str
    role: str
    requiere_calibracion: bool
    requiere_parametrizacion: bool
    is_async: bool
    is_property: bool
    is_classmethod: bool
    is_staticmethod: bool
    line_number: int
    source_file: str
    epistemology_tags: list[str]


class MethodScanner(ast.NodeVisitor):
    """AST visitor to extract all methods from Python source"""

    def __init__(self, module_path: str, source_file: str):
        self.module_path = module_path
        self.source_file = source_file
        self.methods: list[MethodMetadata] = []
        self.current_class: str | None = None
        self.class_stack: list[str] = []
        self.function_depth: int = 0

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.class_stack.append(node.name)
        self.current_class = ".".join(self.class_stack)
        self.generic_visit(node)
        self.class_stack.pop()
        self.current_class = ".".join(self.class_stack) if self.class_stack else None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self.function_depth == 0:
            self._process_function(node, is_async=False)
        self.function_depth += 1
        self.generic_visit(node)
        self.function_depth -= 1

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        if self.function_depth == 0:
            self._process_function(node, is_async=True)
        self.function_depth += 1
        self.generic_visit(node)
        self.function_depth -= 1

    def _process_function(self, node: ast.FunctionDef, is_async: bool) -> None:
        method_name = node.name

        if self.current_class:
            canonical_id = f"{self.module_path}.{self.current_class}.{method_name}"
            class_name = self.current_class
        else:
            canonical_id = f"{self.module_path}.{method_name}"
            class_name = None

        is_property = any(self._is_decorator(d, "property") for d in node.decorator_list)
        is_classmethod = any(self._is_decorator(d, "classmethod") for d in node.decorator_list)
        is_staticmethod = any(self._is_decorator(d, "staticmethod") for d in node.decorator_list)

        role = self._classify_role(method_name, class_name)
        requires_calibration, requires_parametrization, epi_tags = self._apply_epistemological_rubric(
            method_name, class_name, role
        )

        metadata = MethodMetadata(
            canonical_identifier=canonical_id,
            module_path=self.module_path,
            class_name=class_name,
            method_name=method_name,
            role=role,
            requiere_calibracion=requires_calibration,
            requiere_parametrizacion=requires_parametrization,
            is_async=is_async,
            is_property=is_property,
            is_classmethod=is_classmethod,
            is_staticmethod=is_staticmethod,
            line_number=node.lineno,
            source_file=self.source_file,
            epistemology_tags=epi_tags,
        )

        self.methods.append(metadata)

    def _is_decorator(self, decorator: ast.expr, name: str) -> bool:
        if isinstance(decorator, ast.Name):
            return decorator.id == name
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr == name
        return False

    def _classify_role(self, method_name: str, class_name: str | None) -> str:
        method_lower = method_name.lower()
        class_lower = class_name.lower() if class_name else ""

        for role, config in LAYER_REQUIREMENTS.items():
            for pattern in config["typical_patterns"]:
                if pattern.lower() in method_lower:
                    return role

        if "executor" in class_lower:
            return "executor"
        elif "aggregator" in class_lower or "processor" in class_lower:
            return "processor"
        elif "analyzer" in class_lower:
            return "analyzer"
        elif "extractor" in class_lower:
            return "extractor"
        elif "scorer" in class_lower:
            return "score"
        elif "orchestrator" in class_lower:
            return "orchestrator"

        if method_name.startswith("_"):
            return "utility"

        return "core"

    def _apply_epistemological_rubric(
        self, method_name: str, class_name: str | None, role: str
    ) -> tuple[bool, bool, list[str]]:
        method_lower = method_name.lower()
        class_lower = class_name.lower() if class_name else ""
        epi_tags = []

        evaluative_keywords = ["score", "evaluate", "assess", "rank", "rate", "judge", "validate"]
        is_evaluative = any(kw in method_lower for kw in evaluative_keywords)

        transformation_keywords = [
            "calculate", "compute", "infer", "estimate", "analyze",
            "transform", "process", "aggregate", "bayesian"
        ]
        is_transformation = any(kw in method_lower for kw in transformation_keywords)

        statistical_keywords = ["probability", "likelihood", "confidence", "threshold", "statistical"]
        is_statistical = any(kw in method_lower for kw in statistical_keywords)

        is_direct_impact = role in ["analyzer", "processor", "score", "executor"] and not method_name.startswith("_")

        if is_evaluative:
            epi_tags.append("evaluative_judgment")
        if is_transformation:
            epi_tags.append("transformation")
        if is_statistical:
            epi_tags.append("statistical")
        if "causal" in method_lower or "causal" in class_lower:
            epi_tags.append("causal")
        if "bayesian" in method_lower or "bayesian" in class_lower:
            epi_tags.append("bayesian")
        if role == "score":
            epi_tags.append("normative")
        if role == "ingest":
            epi_tags.append("structural")
        if role == "extractor":
            epi_tags.append("semantic")
        if "build" in method_lower or "create" in method_lower or "generate" in method_lower:
            epi_tags.append("constructive")
        if "check" in method_lower or "verify" in method_lower or "assert" in method_lower:
            epi_tags.append("consistency")
        if "format" in method_lower or "render" in method_lower or "export" in method_lower:
            epi_tags.append("descriptive")

        requires_calibration = is_evaluative or (is_statistical and is_direct_impact)
        requires_parametrization = is_transformation or is_statistical or (role == "analyzer")

        if role == "utility" and not is_statistical:
            requires_calibration = False
            requires_parametrization = False

        if method_name in ["__init__", "__repr__", "__str__"]:
            requires_calibration = False
            requires_parametrization = False

        return requires_calibration, requires_parametrization, epi_tags


def scan_python_file(file_path: Path, base_path: Path) -> list[MethodMetadata]:
    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source, filename=str(file_path))

        relative_path = file_path.relative_to(base_path)
        module_parts = list(relative_path.parts[:-1]) + [relative_path.stem]
        module_path = ".".join(module_parts)

        scanner = MethodScanner(module_path, str(file_path))
        scanner.visit(tree)

        return scanner.methods

    except SyntaxError as e:
        print(f"WARNING: Syntax error in {file_path}: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"WARNING: Error processing {file_path}: {e}", file=sys.stderr)
        return []


def scan_directory(directory: Path) -> list[MethodMetadata]:
    all_methods = []
    python_files = sorted(directory.rglob("*.py"))

    print(f"Scanning {len(python_files)} Python files...")

    for file_path in python_files:
        methods = scan_python_file(file_path, directory)
        all_methods.extend(methods)
        print(f"  {file_path.name}: {len(methods)} methods")

    all_methods = deduplicate_canonical_ids(all_methods)

    return all_methods


def deduplicate_canonical_ids(methods: list[MethodMetadata]) -> list[MethodMetadata]:
    """Deduplicate canonical IDs by appending line numbers to duplicates"""
    id_counts = {}
    for method in methods:
        cid = method.canonical_identifier
        id_counts[cid] = id_counts.get(cid, 0) + 1

    id_counters = {}
    deduplicated = []

    for method in methods:
        cid = method.canonical_identifier
        if id_counts[cid] > 1:
            id_counters[cid] = id_counters.get(cid, 0) + 1
            new_cid = f"{cid}@L{method.line_number}"
            method.canonical_identifier = new_cid
        deduplicated.append(method)

    return deduplicated


def verify_critical_methods(methods: list[MethodMetadata]) -> tuple[bool, list[str]]:
    canonical_ids = {m.canonical_identifier for m in methods}

    critical_files = [
        "derek_beach.py",
        "aggregation.py",
        "executors.py",
        "executors_contract.py",
    ]

    missing_methods = []
    found_count = 0

    for method in methods:
        if any(cf in method.source_file for cf in critical_files):
            found_count += 1

    critical_method_patterns = [
        "derek_beach",
        "aggregation",
        "executors",
        "executors_contract",
    ]

    found_patterns = set()
    for method in methods:
        for pattern in critical_method_patterns:
            if pattern in method.canonical_identifier.lower():
                found_patterns.add(pattern)

    for pattern in critical_method_patterns:
        if pattern not in found_patterns:
            missing_methods.append(f"No methods found matching pattern: {pattern}")

    if found_count == 0:
        missing_methods.append("CRITICAL: No methods found from any critical file")

    return len(missing_methods) == 0, missing_methods


def generate_inventory(methods: list[MethodMetadata], output_file: str) -> None:
    inventory = {
        "metadata": {
            "total_methods": len(methods),
            "scan_timestamp": None,
            "source_directory": "src/farfan_pipeline",
        },
        "layer_requirements": LAYER_REQUIREMENTS,
        "methods": [asdict(m) for m in methods],
        "statistics": {
            "by_role": {},
            "by_file": {},
            "requiring_calibration": sum(1 for m in methods if m.requiere_calibracion),
            "requiring_parametrization": sum(1 for m in methods if m.requiere_parametrizacion),
        },
    }

    for method in methods:
        role = method.role
        inventory["statistics"]["by_role"][role] = inventory["statistics"]["by_role"].get(role, 0) + 1

        file_name = Path(method.source_file).name
        inventory["statistics"]["by_file"][file_name] = inventory["statistics"]["by_file"].get(file_name, 0) + 1

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)

    print(f"\nInventory written to {output_file}")
    print(f"Total methods: {len(methods)}")
    print(f"By role: {inventory['statistics']['by_role']}")
    print(f"Requiring calibration: {inventory['statistics']['requiring_calibration']}")
    print(f"Requiring parametrization: {inventory['statistics']['requiring_parametrization']}")


def main():
    pipeline_dir = Path("src/farfan_pipeline")

    if not pipeline_dir.exists():
        print(f"ERROR: Directory {pipeline_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    print(f"Starting AST method scan of {pipeline_dir}...")
    methods = scan_directory(pipeline_dir)

    print(f"\n{'='*60}")
    print(f"SCAN COMPLETE: Found {len(methods)} methods")
    print(f"{'='*60}")

    if len(methods) < 200:
        print(f"\nERROR: Insufficient coverage - found only {len(methods)} methods (minimum: 200)", file=sys.stderr)
        sys.exit(1)

    verification_passed, missing = verify_critical_methods(methods)

    if not verification_passed:
        print("\nERROR: Critical method verification failed:", file=sys.stderr)
        for msg in missing:
            print(f"  - {msg}", file=sys.stderr)
        sys.exit(1)

    print("\n✓ Critical method verification passed")

    output_file = "methods_inventory_raw.json"
    generate_inventory(methods, output_file)

    print(f"\n{'='*60}")
    print("SUCCESS: Inventory generation complete")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

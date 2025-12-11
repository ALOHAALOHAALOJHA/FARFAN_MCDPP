#!/usr/bin/env python3
"""
Canonical Method Catalog Builder - JOBFRONT 1

PURPOSE: INVENTORY ONLY - Discover and list ALL public methods.
         Does NOT determine calibration requirements.
         Calibration determination is done by triage_intrinsic_calibration.py

Key Principles:
✅ Universal Coverage - No method omitted
✅ Raw Metadata Only - No calibration decisions here
✅ Layer from Directory Structure - Not invented keywords
✅ Triage-Ready Output - Feeds into Pass 1/2/3 of triage
"""

import ast
import hashlib
import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class MethodMetadata:
    """Raw method metadata for catalog. Calibration fields set by TRIAGE."""
    # Core identification
    unique_id: str
    canonical_name: str
    method_name: str
    class_name: str | None
    file_path: str
    module_path: str
    
    # Layer from actual directory structure
    layer: str
    
    # Signature and interface
    signature: str
    input_parameters: list[dict[str, Any]]
    return_type: str | None
    
    # Calibration tracking - SET BY TRIAGE, not here
    # These are placeholders, triage_intrinsic_calibration.py populates them
    requires_calibration: bool | None  # None = not yet triaged
    calibration_status: str  # "pending_triage" until triage runs
    
    # Method characteristics (raw facts for triage to use)
    docstring: str | None
    decorators: list[str]
    is_async: bool
    is_private: bool
    is_abstract: bool
    is_staticmethod: bool
    is_classmethod: bool
    is_property: bool
    
    # Complexity metrics (raw)
    num_arguments: int
    has_return_type: bool
    docstring_length: int
    num_branches: int
    num_loops: int
    
    # Source tracking
    line_number: int
    end_line_number: int
    source_hash: str
    last_scanned: str


def compute_unique_id(canonical_name: str, source_code: str) -> str:
    """Generate SHA256-based unique ID (first 16 chars)."""
    content = f"{canonical_name}:{source_code}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def compute_source_hash(source_code: str) -> str:
    """Generate hash of method source."""
    return hashlib.sha256(source_code.encode()).hexdigest()[:12]


def get_layer_from_path(file_path: str) -> str:
    """
    Derive layer from ACTUAL directory structure.
    No invented keywords - use real folder names.
    """
    parts = file_path.lower().split("/")
    
    # Map actual directories to layers
    if "canonic_phases" in parts:
        return "canonic_phases"
    if "orchestration" in parts:
        return "orchestration"
    if "core" in parts:
        return "core"
    if "methods_dispensary" in parts:
        return "methods_dispensary"
    if "cross_cutting_infrastrucuture" in parts:
        return "cross_cutting"
    if "farfan_pipeline" in parts:
        return "farfan_pipeline"
    if "batch_concurrence" in parts:
        return "batch_concurrence"
    if "dashboard" in parts:
        return "dashboard"
    
    return "other"


def count_branches_and_loops(node: ast.FunctionDef) -> tuple[int, int]:
    """Count branching statements and loops."""
    branches = 0
    loops = 0
    
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.IfExp, ast.Try, ast.ExceptHandler)):
            branches += 1
        elif isinstance(child, (ast.For, ast.While, ast.AsyncFor)):
            loops += 1
    
    return branches, loops


def extract_parameters(node: ast.FunctionDef) -> list[dict[str, Any]]:
    """Extract parameter information."""
    params = []
    
    for arg in node.args.args:
        if arg.arg == "self":
            continue
        
        param = {
            "name": arg.arg,
            "type_hint": None,
            "has_default": False
        }
        
        if arg.annotation:
            try:
                param["type_hint"] = ast.unparse(arg.annotation)
            except:
                param["type_hint"] = "unknown"
        
        params.append(param)
    
    # Mark defaults
    num_defaults = len(node.args.defaults)
    if num_defaults > 0:
        for i in range(num_defaults):
            idx = len(params) - num_defaults + i
            if 0 <= idx < len(params):
                params[idx]["has_default"] = True
    
    return params


def extract_return_type(node: ast.FunctionDef) -> str | None:
    """Extract return type annotation."""
    if node.returns:
        try:
            return ast.unparse(node.returns)
        except:
            return "unknown"
    return None


def extract_decorators(node: ast.FunctionDef) -> list[str]:
    """Extract decorator names."""
    decorators = []
    for dec in node.decorator_list:
        try:
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)
            elif isinstance(dec, ast.Call):
                if isinstance(dec.func, ast.Name):
                    decorators.append(dec.func.id)
                elif isinstance(dec.func, ast.Attribute):
                    decorators.append(dec.func.attr)
            elif isinstance(dec, ast.Attribute):
                decorators.append(dec.attr)
        except:
            pass
    return decorators


def has_decorator(decorators: list[str], name: str) -> bool:
    """Check if decorator list contains a specific decorator."""
    return any(name in d for d in decorators)


def build_signature(node: ast.FunctionDef) -> str:
    """Build method signature string."""
    try:
        params = []
        for arg in node.args.args:
            param_str = arg.arg
            if arg.annotation:
                param_str += f": {ast.unparse(arg.annotation)}"
            params.append(param_str)
        
        sig = f"({', '.join(params)})"
        
        if node.returns:
            sig += f" -> {ast.unparse(node.returns)}"
        
        return sig
    except:
        return "()"


def extract_method_metadata(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    class_name: str | None,
    module_path: str,
    file_path: str,
    source: str,
) -> MethodMetadata:
    """Extract RAW metadata. NO calibration decisions."""
    method_name = node.name
    
    # Build canonical name
    if class_name:
        canonical_name = f"{module_path}.{class_name}.{method_name}"
    else:
        canonical_name = f"{module_path}.{method_name}"
    
    # Get source segment
    try:
        source_lines = source.split("\n")
        end_line = node.end_lineno if node.end_lineno else node.lineno
        method_source = "\n".join(source_lines[node.lineno - 1:end_line])
    except:
        method_source = ""
    
    # Extract raw facts
    decorators = extract_decorators(node)
    docstring = ast.get_docstring(node)
    params = extract_parameters(node)
    return_type = extract_return_type(node)
    num_branches, num_loops = count_branches_and_loops(node)
    
    return MethodMetadata(
        unique_id=compute_unique_id(canonical_name, method_source),
        canonical_name=canonical_name,
        method_name=method_name,
        class_name=class_name,
        file_path=file_path,
        module_path=module_path,
        layer=get_layer_from_path(file_path),
        signature=build_signature(node),
        input_parameters=params,
        return_type=return_type,
        # Calibration: NOT DECIDED HERE - set by triage
        requires_calibration=None,  # Triage will determine
        calibration_status="pending_triage",
        # Raw characteristics for triage to analyze
        docstring=docstring,
        decorators=decorators,
        is_async=isinstance(node, ast.AsyncFunctionDef),
        is_private=method_name.startswith("_"),
        is_abstract=has_decorator(decorators, "abstractmethod"),
        is_staticmethod=has_decorator(decorators, "staticmethod"),
        is_classmethod=has_decorator(decorators, "classmethod"),
        is_property=has_decorator(decorators, "property"),
        num_arguments=len(params),
        has_return_type=return_type is not None,
        docstring_length=len(docstring) if docstring else 0,
        num_branches=num_branches,
        num_loops=num_loops,
        line_number=node.lineno,
        end_line_number=node.end_lineno or node.lineno,
        source_hash=compute_source_hash(method_source),
        last_scanned=datetime.now(timezone.utc).isoformat()
    )


def scan_file(file_path: Path, repo_root: Path) -> list[MethodMetadata]:
    """Scan a single Python file for ALL public methods."""
    methods = []
    
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))
    except Exception as e:
        print(f"  ⚠️ Parse error {file_path.name}: {e}", file=sys.stderr)
        return methods
    
    rel_path = str(file_path.relative_to(repo_root))
    module_path = rel_path.replace("/", ".").replace(".py", "")
    
    # Scan module-level functions and classes
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Only PUBLIC functions (not starting with _)
            if not node.name.startswith("_"):
                method = extract_method_metadata(
                    node, None, module_path, rel_path, source
                )
                methods.append(method)
        
        elif isinstance(node, ast.ClassDef):
            class_name = node.name
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Only PUBLIC methods (not starting with _)
                    if not item.name.startswith("_"):
                        method = extract_method_metadata(
                            item, class_name, module_path, rel_path, source
                        )
                        methods.append(method)
    
    return methods


def scan_repository(repo_root: Path) -> list[MethodMetadata]:
    """Scan entire src/ for ALL public methods."""
    all_methods = []
    src_path = repo_root / "src"
    
    if not src_path.exists():
        print(f"ERROR: {src_path} does not exist", file=sys.stderr)
        return all_methods
    
    # Find all Python files, EXCLUDING _new_calibration_system
    py_files = [
        f for f in src_path.rglob("*.py")
        if "_new_calibration_system" not in str(f)
        and "__pycache__" not in str(f)
    ]
    
    print(f"Scanning {len(py_files)} Python files for public methods...")
    
    for i, py_file in enumerate(sorted(py_files)):
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i + 1}/{len(py_files)} files...")
        
        methods = scan_file(py_file, repo_root)
        all_methods.extend(methods)
    
    return all_methods


def build_catalog(methods: list[MethodMetadata]) -> dict[str, Any]:
    """Build the canonical method catalog - RAW INVENTORY."""
    # Count by layer (actual directory structure)
    by_layer: dict[str, int] = {}
    for m in methods:
        by_layer[m.layer] = by_layer.get(m.layer, 0) + 1
    
    return {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "purpose": "Raw method inventory - calibration determined by triage",
            "total_methods": len(methods),
            "note": "requires_calibration and calibration_status are set by triage_intrinsic_calibration.py"
        },
        "summary": {
            "total_methods": len(methods),
            "by_layer": dict(sorted(by_layer.items(), key=lambda x: -x[1])),
            "triage_status": "pending"
        },
        "methods": [asdict(m) for m in methods]
    }


def main():
    """Build canonical method catalog - INVENTORY ONLY."""
    script_dir = Path(__file__).parent  # .../src/_new_calibration_system/scripts
    config_dir = script_dir.parent / "config"  # .../src/_new_calibration_system/config
    # Navigate: scripts -> _new_calibration_system -> src -> REPO_ROOT
    repo_root = script_dir.parent.parent.parent  # 3 levels up, not 4
    
    print("=" * 70)
    print("CANONICAL METHOD CATALOG - INVENTORY SCAN")
    print("=" * 70)
    print(f"Repository: {repo_root}")
    print(f"Output: {config_dir}")
    print()
    print("NOTE: This produces RAW inventory only.")
    print("      Calibration decisions made by triage_intrinsic_calibration.py")
    print()
    
    methods = scan_repository(repo_root)
    
    print(f"\nPublic methods discovered: {len(methods)}")
    
    catalog = build_catalog(methods)
    
    output_path = config_dir / "canonical_method_catalog.json"
    with open(output_path, "w") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
        f.write("\n")
    
    print(f"\n✅ Catalog saved: {output_path}")
    
    print("\n" + "=" * 70)
    print("INVENTORY SUMMARY")
    print("=" * 70)
    print(f"Total public methods: {catalog['summary']['total_methods']}")
    print("\nBy Directory Layer:")
    for layer, count in catalog['summary']['by_layer'].items():
        print(f"  {layer}: {count}")
    print("\n⏳ Next: Run triage_intrinsic_calibration.py for calibration analysis")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

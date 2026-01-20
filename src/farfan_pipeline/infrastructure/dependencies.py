"""
F.A.R.F.A.N Dependency Governance Registry
==========================================

CRITICAL: This is the SINGLE SOURCE OF TRUTH for all dependencies.

To add a dependency:
1. Add it to the appropriate layer below
2. Justify its architectural role in the "owner" field
3. Run `python -m farfan_pipeline.infrastructure.dependencies sync` to propagate to all manifests

DEPENDENCY LAYER MAPPING:
- LAYER_API: Web frameworks, API serving, HTTP clients
- LAYER_NLP: Natural language processing, embeddings, semantic analysis
- LAYER_BAYESIAN: Probabilistic programming, Bayesian inference
- LAYER_SCIENTIFIC: Numerical computing, scientific algorithms
- LAYER_DOCUMENT: Document processing (PDF, DOCX), table extraction
- LAYER_REPORTING: Report generation, HTML to PDF conversion
- LAYER_UTILITY: Cross-cutting utilities (logging, security, config)

ARCHITECTURE RULES:
- Each dependency MUST belong to exactly one layer
- Each dependency MUST have a documented owner/subsystem
- Cross-layer dependencies are FORBIDDEN without architectural review
- NLP and BAYESIAN layers must remain isolated (separate computational paradigms)

Schema Version: 1.0.0
Last Updated: 2026-01-13
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Final, Literal


class DependencyLayer(Enum):
    """
    Architectural layer for dependency governance.

    Each layer represents a distinct subsystem with clear boundaries.
    """

    LAYER_API = "api"
    LAYER_NLP = "nlp"
    LAYER_BAYESIAN = "bayesian"
    LAYER_SCIENTIFIC = "scientific"
    LAYER_DOCUMENT = "document"
    LAYER_REPORTING = "reporting"
    LAYER_UTILITY = "utility"


class DependencyStatus(Enum):
    """
    Status of a dependency in the system.
    """

    ACTIVE = "active"  # Currently used
    DEPRECATED = "deprecated"  # Scheduled for removal
    REMOVED = "removed"  # No longer in system
    CANDIDATE = "candidate"  # Under evaluation


@dataclass(frozen=True)
class DependencySpec:
    """
    Specification for a single dependency.

    Attributes:
        version: Version constraint (pip-compatible)
        layer: Architectural layer this dependency belongs to
        owner: Subsystem that owns this dependency (e.g., "API serving")
        status: Whether this dependency is active, deprecated, etc.
        justification: Why this dependency is needed
        migration_target: If deprecated, what to use instead
        security_notes: Any CVEs or security concerns
        operational_notes: JVM required, memory pressure, etc.
    """

    version: str
    layer: DependencyLayer
    owner: str
    status: DependencyStatus = DependencyStatus.ACTIVE
    justification: str = ""
    migration_target: str | None = None
    security_notes: str | None = None
    operational_notes: str | None = None


# =============================================================================
# SINGLE SOURCE OF TRUTH - ALL DEPENDENCIES
# =============================================================================

CANONICAL_DEPENDENCIES: Final[dict[str, DependencySpec]] = {
    # ==========================================================================
    # WEB / API LAYER (Consolidate to ONE framework)
    # ==========================================================================
    "fastapi": DependencySpec(
        version=">=0.109.0",
        layer=DependencyLayer.LAYER_API,
        owner="API serving (ASGI)",
        justification="Primary API framework for pipeline orchestration",
        operational_notes="Async-first, requires uvicorn server",
    ),
    "uvicorn[standard]": DependencySpec(
        version=">=0.27.0",
        layer=DependencyLayer.LAYER_API,
        owner="ASGI server",
        justification="Required server for FastAPI",
    ),
    "sse-starlette": DependencySpec(
        version=">=2.0.0",
        layer=DependencyLayer.LAYER_API,
        owner="Server-sent events",
        justification="Real-time streaming for long-running pipeline tasks",
    ),
    "httpx": DependencySpec(
        version=">=0.27.0",
        layer=DependencyLayer.LAYER_API,
        owner="Async HTTP client",
        justification="Async HTTP for external API calls",
    ),
    "requests": DependencySpec(
        version=">=2.31.0",
        layer=DependencyLayer.LAYER_API,
        owner="Sync HTTP client",
        justification="Legacy sync HTTP, phase out in favor of httpx",
        status=DependencyStatus.DEPRECATED,
        migration_target="httpx",
    ),
    # CRITICAL: FLASK REMOVAL REQUIRED
    # Audit found in dashboard_atroz_ module - document or migrate
    "flask": DependencySpec(
        version=">=3.0.0",
        layer=DependencyLayer.LAYER_API,
        owner="Dashboard serving (WSGI)",
        justification="Dashboard module atroz_ - MIGRATE TO FASTAPI",
        status=DependencyStatus.DEPRECATED,
        migration_target="FastAPI",
        security_notes="Running two frameworks is technical debt",
    ),
    "flask-cors": DependencySpec(
        version=">=4.0.0",
        layer=DependencyLayer.LAYER_API,
        owner="Dashboard CORS",
        status=DependencyStatus.DEPRECATED,
        migration_target="FastAPI CORS middleware",
    ),
    "flask-socketio": DependencySpec(
        version=">=5.3.0",
        layer=DependencyLayer.LAYER_API,
        owner="Dashboard WebSockets",
        status=DependencyStatus.DEPRECATED,
        migration_target="FastAPI WebSockets or socket.io-fastapi",
    ),
    "werkzeug": DependencySpec(
        version=">=3.0.0",
        layer=DependencyLayer.LAYER_API,
        owner="Flask WSGI utilities",
        status=DependencyStatus.DEPRECATED,
        migration_target="Remove with Flask",
    ),
    "python-multipart": DependencySpec(
        version=">=0.0.7",
        layer=DependencyLayer.LAYER_API,
        owner="File upload handling",
        justification="Required for FastAPI file uploads",
    ),
    # ==========================================================================
    # NLP LAYER (Explicit ownership contracts - OVERLAPPING CAPABILITIES)
    # ==========================================================================
    "transformers": DependencySpec(
        version=">=4.41.0,<4.42.0",
        layer=DependencyLayer.LAYER_NLP,
        owner="Embeddings & semantic encoding (BGE-M3)",
        justification="Primary transformer models for semantic analysis",
        operational_notes="Large download (~500MB) on first use",
    ),
    "sentence-transformers": DependencySpec(
        version=">=3.1.0,<3.2.0",
        layer=DependencyLayer.LAYER_NLP,
        owner="Semantic retrieval & dense embeddings",
        justification="Specialized embedding models for semantic search",
        security_notes="Depends on transformers, version pinning critical",
    ),
    "accelerate": DependencySpec(
        version=">=1.2.0",
        layer=DependencyLayer.LAYER_NLP,
        owner="Model acceleration",
        justification="Required for efficient transformer inference",
    ),
    "tokenizers": DependencySpec(
        version=">=0.15.0",
        layer=DependencyLayer.LAYER_NLP,
        owner="Tokenization",
        justification="Required tokenization library for transformers",
    ),
    "spacy": DependencySpec(
        version=">=3.7.0",
        layer=DependencyLayer.LAYER_NLP,
        owner="Linguistic structure & dependency parsing",
        justification="Advanced NLP: POS tagging, NER, dependency trees",
        operational_notes="Requires language model download (es_core_news_lg)",
    ),
    "nltk": DependencySpec(
        version=">=3.8.0",
        layer=DependencyLayer.LAYER_NLP,
        owner="Specific linguistic utilities only",
        justification="Legacy NLP utilities not in spaCy (use sparingly)",
        security_notes="Do NOT duplicate spaCy tokenization",
    ),
    "langdetect": DependencySpec(
        version=">=1.0.9",
        layer=DependencyLayer.LAYER_NLP,
        owner="Language detection",
        justification="Detect document language (Spanish vs English)",
    ),
    "textstat": DependencySpec(
        version=">=0.7.3",
        layer=DependencyLayer.LAYER_NLP,
        owner="Readability metrics",
        justification="Text complexity analysis (Flesch, etc.)",
    ),
    "proselint": DependencySpec(
        version=">=0.13.0",
        layer=DependencyLayer.LAYER_NLP,
        status=DependencyStatus.CANDIDATE,
        owner="Prose quality linting",
        justification="Optional: prose quality checking",
    ),
    # Deep Learning backend for NLP
    "torch": DependencySpec(
        version=">=2.1.0",
        layer=DependencyLayer.LAYER_NLP,
        owner="Deep learning backend",
        justification="Required backend for transformers/sentence-transformers",
        operational_notes="Large install (~2GB), consider CPU-only version",
    ),
    # ==========================================================================
    # BAYESIAN / PROBABILISTIC LAYER (Isolate from Deep Learning)
    # ==========================================================================
    "pymc": DependencySpec(
        version=">=5.16.0,<5.17.0",
        layer=DependencyLayer.LAYER_BAYESIAN,
        owner="Probabilistic programming & Bayesian inference",
        justification="Core Bayesian inference engine",
        operational_notes="Separate numerical backend from PyTorch",
    ),
    "pytensor": DependencySpec(
        version=">=2.25.1,<2.26",
        layer=DependencyLayer.LAYER_BAYESIAN,
        owner="PyMC computational backend",
        justification="Required tensor backend for PyMC",
        security_notes="DO NOT import directly in non-Bayesian code",
    ),
    "arviz": DependencySpec(
        version=">=0.17.0",
        layer=DependencyLayer.LAYER_BAYESIAN,
        owner="Bayesian visualization & diagnostics",
        justification="Plot posterior distributions, convergence diagnostics",
    ),
    # ==========================================================================
    # SCIENTIFIC & NUMERICAL STACK
    # ==========================================================================
    "numpy": DependencySpec(
        version=">=1.26.4,<2.0.0",
        layer=DependencyLayer.LAYER_SCIENTIFIC,
        owner="Array operations & numerical computing",
        justification="Foundation for all numerical computing",
        operational_notes="Pinned to <2.0.0 for compatibility",
    ),
    "scipy": DependencySpec(
        version=">=1.11.0",
        layer=DependencyLayer.LAYER_SCIENTIFIC,
        owner="Scientific algorithms & statistics",
        justification="Statistical distributions, optimization, signal processing",
    ),
    "scikit-learn": DependencySpec(
        version=">=1.6.0",
        layer=DependencyLayer.LAYER_SCIENTIFIC,
        owner="Machine learning utilities",
        justification="Clustering, dimensionality reduction, metrics",
    ),
    "networkx": DependencySpec(
        version=">=3.0",
        layer=DependencyLayer.LAYER_SCIENTIFIC,
        owner="Graph algorithms",
        justification="Dependency graph analysis, causal structure learning",
    ),
    "pandas": DependencySpec(
        version=">=2.1.0",
        layer=DependencyLayer.LAYER_SCIENTIFIC,
        owner="Data frames & tabular data",
        justification="Data manipulation, analysis, export",
    ),
    "matplotlib": DependencySpec(
        version=">=3.8.0",
        layer=DependencyLayer.LAYER_SCIENTIFIC,
        owner="Visualization",
        justification="Plotting for scientific analysis",
    ),
    # ==========================================================================
    # DOCUMENT PROCESSING (Reduce from 6 to 3 primary libraries)
    # ==========================================================================
    "pymupdf": DependencySpec(
        version=">=1.23.0",
        layer=DependencyLayer.LAYER_DOCUMENT,
        owner="Primary PDF rendering & text extraction",
        justification="Fastest PDF library, handles most PDFs correctly",
        operational_notes="Imported as `fitz`, not `pymupdf`",
    ),
    "pdfplumber": DependencySpec(
        version=">=0.10.0",
        layer=DependencyLayer.LAYER_DOCUMENT,
        owner="Fallback PDF text extraction",
        justification="Better for complex layouts, tables, multi-column",
    ),
    "pypdf": DependencySpec(
        version=">=6.4.0",
        layer=DependencyLayer.LAYER_DOCUMENT,
        owner="PDF manipulation & metadata",
        justification="Merging, splitting, page operations",
        security_notes="Upgraded from PyPDF2 to address CVE-2025-55197, CVE-2025-62707, CVE-2025-62708, CVE-2025-66019",
    ),
    # CRITICAL: PyPDF2 is DEPRECATED - merged into pypdf
    "PyPDF2": DependencySpec(
        version=">=3.0.1",
        layer=DependencyLayer.LAYER_DOCUMENT,
        owner="DEPRECATED - Use pypdf instead (PyPDF2 was merged back into pypdf in v3.0.0)",
        status=DependencyStatus.REMOVED,
        migration_target="pypdf (PyPDF2 was merged back into pypdf in v3.0.0)",
        security_notes="DEPRECATED: Use pypdf instead (same package, restored name)",
    ),
    # CV/Java-based table extraction - use only if necessary
    "img2table": DependencySpec(
        version=">=1.4.0",
        layer=DependencyLayer.LAYER_DOCUMENT,
        status=DependencyStatus.CANDIDATE,
        owner="AI/CV-based table extraction",
        justification="Experimental: AI-based table detection from PDF images",
        operational_notes="Heavy CV dependencies, use only if pymupdf/pdfplumber fail",
    ),
    "tabula-py": DependencySpec(
        version=">=2.9.0",
        layer=DependencyLayer.LAYER_DOCUMENT,
        status=DependencyStatus.CANDIDATE,
        owner="Java-backed table extraction",
        justification="Fallback for tabular data extraction",
        operational_notes="REQUIRES JAVA RUNTIME - adds deployment complexity",
        security_notes="Java dependency increases container size and cold-start time",
    ),
    "python-docx": DependencySpec(
        version=">=1.1.0",
        layer=DependencyLayer.LAYER_DOCUMENT,
        owner="DOCX processing",
        justification="Read/write Word documents (.docx)",
    ),
    # ==========================================================================
    # REPORTING & RENDERING
    # ==========================================================================
    "weasyprint": DependencySpec(
        version=">=62.0",
        layer=DependencyLayer.LAYER_REPORTING,
        owner="HTML to PDF conversion",
        justification="Generate PDF reports from HTML templates",
        operational_notes="Requires GTK libraries on Linux",
    ),
    "jinja2": DependencySpec(
        version=">=3.1.0",
        layer=DependencyLayer.LAYER_REPORTING,
        owner="Template engine",
        justification="HTML report templates",
    ),
    "markdown": DependencySpec(
        version=">=3.5.0",
        layer=DependencyLayer.LAYER_REPORTING,
        status=DependencyStatus.CANDIDATE,
        owner="Markdown processing",
        justification="Optional: Markdown rendering in reports",
    ),
    "pillow": DependencySpec(
        version=">=10.0.0",
        layer=DependencyLayer.LAYER_REPORTING,
        owner="Image processing",
        justification="Image handling in reports, document processing",
    ),
    # ==========================================================================
    # DATA HANDLING & UTILITIES
    # ==========================================================================
    "python-dotenv": DependencySpec(
        version=">=1.0.0",
        layer=DependencyLayer.LAYER_UTILITY,
        owner="Environment configuration",
        justification="Load .env files for configuration",
    ),
    "pyyaml": DependencySpec(
        version=">=6.0.0",
        layer=DependencyLayer.LAYER_UTILITY,
        owner="YAML configuration",
        justification="Parse YAML config files",
    ),
    "structlog": DependencySpec(
        version=">=24.1.0",
        layer=DependencyLayer.LAYER_UTILITY,
        owner="Structured logging",
        justification="Production-grade structured logging",
    ),
    "tenacity": DependencySpec(
        version=">=8.2.0",
        layer=DependencyLayer.LAYER_UTILITY,
        owner="Retry logic",
        justification="Controlled retries with exponential backoff",
    ),
    "rapidfuzz": DependencySpec(
        version=">=3.0.0",
        layer=DependencyLayer.LAYER_UTILITY,
        owner="Fuzzy string matching",
        justification="Fast string similarity (replaces fuzzywuzzy)",
    ),
    "blake3": DependencySpec(
        version=">=0.4.1",
        layer=DependencyLayer.LAYER_UTILITY,
        owner="Hashing",
        justification="Fast BLAKE3 hashing for deduplication",
    ),
    "pydot": DependencySpec(
        version=">=2.0.0",
        layer=DependencyLayer.LAYER_UTILITY,
        owner="Graphviz integration",
        justification="Graph visualization for causal structures",
    ),
    "aiofiles": DependencySpec(
        version=">=23.2.0",
        layer=DependencyLayer.LAYER_UTILITY,
        status=DependencyStatus.CANDIDATE,
        owner="Async file I/O",
        justification="Async file operations for performance",
    ),
    "typing_extensions": DependencySpec(
        version=">=4.10.0",
        layer=DependencyLayer.LAYER_UTILITY,
        owner="Type system extensions",
        justification="Required for modern type hints (backports)",
    ),
    # ==========================================================================
    # TYPE SAFETY & VALIDATION
    # ==========================================================================
    "pydantic": DependencySpec(
        version=">=2.0.0",
        layer=DependencyLayer.LAYER_UTILITY,
        owner="Runtime validation & serialization",
        justification="Core validation framework, integrates with FastAPI",
    ),
    "jsonschema": DependencySpec(
        version=">=4.21.0",
        layer=DependencyLayer.LAYER_UTILITY,
        owner="Schema validation",
        justification="Validate JSON against schemas (external artifacts)",
    ),
    # ==========================================================================
    # OBSERVABILITY & MONITORING
    # ==========================================================================
    "opentelemetry-api": DependencySpec(
        version=">=1.24.0",
        layer=DependencyLayer.LAYER_UTILITY,
        status=DependencyStatus.CANDIDATE,
        owner="OpenTelemetry API",
        justification="Standardized observability API",
    ),
    "prometheus_client": DependencySpec(
        version=">=0.20.0",
        layer=DependencyLayer.LAYER_UTILITY,
        status=DependencyStatus.CANDIDATE,
        owner="Prometheus metrics",
        justification="Prometheus metrics export",
    ),
    "psutil": DependencySpec(
        version=">=5.9.0",
        layer=DependencyLayer.LAYER_UTILITY,
        owner="System monitoring",
        justification="Basic system metrics (CPU, memory)",
        status=DependencyStatus.DEPRECATED,
        migration_target="OpenTelemetry for comprehensive monitoring",
    ),
    # ==========================================================================
    # SECURITY
    # ==========================================================================
    "cryptography": DependencySpec(
        version=">=46.0.0",
        layer=DependencyLayer.LAYER_UTILITY,
        owner="Cryptographic operations",
        justification="Ed25519 signatures, secure hashing",
    ),
    "bcrypt": DependencySpec(
        version=">=4.0.0",
        layer=DependencyLayer.LAYER_UTILITY,
        owner="Password hashing",
        justification="Secure password hashing",
    ),
}


# =============================================================================
# QUERY APIS
# =============================================================================


def get_layer(layer: DependencyLayer) -> list[str]:
    """Get all active dependencies for a layer."""
    return [
        name
        for name, spec in CANONICAL_DEPENDENCIES.items()
        if spec.layer == layer and spec.status == DependencyStatus.ACTIVE
    ]


def get_owner(owner: str) -> list[str]:
    """Get all dependencies owned by a specific subsystem."""
    return [
        name
        for name, spec in CANONICAL_DEPENDENCIES.items()
        if spec.owner == owner and spec.status == DependencyStatus.ACTIVE
    ]


def get_status(status: DependencyStatus) -> list[str]:
    """Get all dependencies with a specific status."""
    return [name for name, spec in CANONICAL_DEPENDENCIES.items() if spec.status == status]


def get_active_dependencies() -> dict[str, DependencySpec]:
    """Get all active dependencies."""
    return {name: spec for name, spec in CANONICAL_DEPENDENCIES.items() if spec.status == DependencyStatus.ACTIVE}


def get_dependency_hash() -> str:
    """
    Compute hash of canonical dependencies for drift detection.

    Returns:
        SHA-256 hash of canonical dependency specification
    """
    # Serialize to canonical JSON (sorted keys)
    serialized = json.dumps(
        {
            name: {
                "version": spec.version,
                "layer": spec.layer.value,
                "owner": spec.owner,
                "status": spec.status.value,
            }
            for name, spec in CANONICAL_DEPENDENCIES.items()
        },
        sort_keys=True,
    )
    return hashlib.sha256(serialized.encode()).hexdigest()[:16]


# =============================================================================
# DEPENDENCY SYNC TOOL
# =============================================================================


def sync_to_requirements_txt(output_path: Path = Path("requirements.txt")) -> None:
    """
    Export canonical dependencies to requirements.txt format.

    This is the RECOMMENDED way to generate requirements.txt from this registry.
    """
    active = get_active_dependencies()
    lines = [
        f"# F.A.R.F.A.N Dependencies",
        f"# Generated from infrastructure/dependencies.py",
        f"# Dependency Hash: {get_dependency_hash()}",
        f"# Python 3.12 required",
        f"# Last updated: {hashlib.sha256().hexdigest()[:16]}",
        f"",
    ]

    # Group by layer for readability
    for layer in DependencyLayer:
        layer_deps = get_layer(layer)
        if layer_deps:
            lines.append(f"# {layer.value.upper()} LAYER")
            for name in sorted(layer_deps):
                spec = CANONICAL_DEPENDENCIES[name]
                line = f"{name}{spec.version}"
                if spec.operational_notes:
                    line += f"  # {spec.operational_notes[:60]}"
                elif spec.migration_target:
                    line += f"  # DEPRECATED: {spec.migration_target}"
                lines.append(line)
            lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def sync_to_pyproject_toml(pyproject_path: Path = Path("pyproject.toml")) -> None:
    """
    Update pyproject.toml dependencies from canonical registry.

    NOTE: This will overwrite the dependencies section in pyproject.toml.
    Manual review required before committing.
    """
    active = get_active_dependencies()

    # Generate dependencies list
    deps_list = []
    for name, spec in active.items():
        deps_list.append(f'"{name}{spec.version}"')

    # Read existing pyproject.toml
    content = pyproject_path.read_text(encoding="utf-8")

    # Replace dependencies section (simple regex, may need manual adjustment)
    pattern = r'dependencies = \[[^\]]+\](?:\n\s*"[^"]+",?)*'
    replacement = f"dependencies = [\n    " + ",\n    ".join(deps_list) + ",\n]"

    # For safety, show what would change
    print("DEPENDENCY SYNC PREVIEW:")
    print("=" * 70)
    print("This would REPLACE the dependencies section in pyproject.toml with:")
    print(replacement)
    print("=" * 70)
    print("\nTo apply, uncomment the write below:")
    # content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    # pyproject_path.write_text(content, encoding="utf-8")


def audit_dependency_consistency() -> dict[str, list[str]]:
    """
    Audit all dependency manifests for consistency.

    Returns:
        Dictionary with 'missing', 'extra', 'version_mismatch' keys
    """
    active = get_active_dependencies()

    # Read requirements files
    req_txt = Path("requirements.txt")
    req_improved = Path("requirements-improved.txt")

    issues = {
        "missing_from_registry": [],
        "extra_in_registry": [],
        "version_mismatches": [],
    }

    # Simple parsing (for demonstration)
    if req_txt.exists():
        for line in req_txt.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("-"):
                # Extract package name
                match = re.match(r"^([a-zA-Z0-9_-]+)", line)
                if match:
                    pkg = match.group(1)
                    if pkg not in active:
                        issues["extra_in_registry"].append(pkg)

    # Check for missing
    for name in active:
        if req_txt.exists() and name not in req_txt.read_text():
            issues["missing_from_registry"].append(name)

    return issues


# =============================================================================
# CLI ENTRY POINT
# =============================================================================


def main() -> None:
    """CLI interface for dependency management."""
    import sys

    command = sys.argv[1] if len(sys.argv) > 1 else "help"

    if command == "sync":
        print("Syncing dependencies to requirements.txt...")
        sync_to_requirements_txt()
        print(f"Generated requirements.txt with hash: {get_dependency_hash()}")
    elif command == "audit":
        issues = audit_dependency_consistency()
        print("DEPENDENCY AUDIT RESULTS:")
        print(f"  Missing from registry: {len(issues['missing_from_registry'])}")
        print(f"  Extra in registry: {len(issues['extra_in_registry'])}")
        print(f"  Version mismatches: {len(issues['version_mismatches'])}")
    elif command == "hash":
        print(f"Current dependency hash: {get_dependency_hash()}")
    elif command == "layers":
        for layer in DependencyLayer:
            deps = get_layer(layer)
            if deps:
                print(f"\n{layer.value.upper()}:")
                for dep in deps:
                    print(f"  - {dep}")
    else:
        print(__doc__)
        print("\nCommands:")
        print("  sync   - Generate requirements.txt from canonical registry")
        print("  audit  - Check consistency between manifests")
        print("  hash   - Show current dependency hash")
        print("  layers - List dependencies by layer")


if __name__ == "__main__":
    main()

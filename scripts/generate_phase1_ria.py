#!/usr/bin/env python3
"""Generate Phase 1 CPP Repository Inventory Artifact (RIA).

Outputs a deterministic, reviewable report with:
- Phase 1 file inventory (path, bytes, sha256)
- Reference inventory for critical strings (path:line)
- Orchestrator call-graph evidence (Phase 1 entrypoints and call sites)

Run:
  python scripts/generate_phase1_ria.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

PHASE1_IMPL_DIR = (
    REPO_ROOT / "src" / "farfan_pipeline" / "phases" / "Phase_one"
)

DOC_PATHS = [
    REPO_ROOT / "docs" / "PHASE_1_CIRCUIT_BREAKER.md",
    REPO_ROOT / "requirements-phase1.txt",
]

DOC_GLOBS = [
    REPO_ROOT / "artifacts" / "reports",
]


@dataclass(frozen=True, slots=True)
class FileRecord:
    path: Path
    size_bytes: int
    sha256: str
    category: str


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _is_text_candidate(path: Path) -> bool:
    if path.is_dir():
        return False
    if path.name.startswith("."):
        return False
    if any(part in {".git", "__pycache__", ".venv", "venv", ".mypy_cache"} for part in path.parts):
        return False
    return True


def _collect_phase1_files() -> list[FileRecord]:
    records: list[FileRecord] = []

    if PHASE1_IMPL_DIR.exists():
        for p in sorted(PHASE1_IMPL_DIR.rglob("*")):
            if not p.is_file():
                continue
            records.append(
                FileRecord(
                    path=p.relative_to(REPO_ROOT),
                    size_bytes=p.stat().st_size,
                    sha256=_sha256(p),
                    category="phase1_implementation",
                )
            )

    for p in DOC_PATHS:
        if p.exists() and p.is_file():
            records.append(
                FileRecord(
                    path=p.relative_to(REPO_ROOT),
                    size_bytes=p.stat().st_size,
                    sha256=_sha256(p),
                    category="phase1_documentation",
                )
            )

    for root in DOC_GLOBS:
        if not root.exists():
            continue
        for p in sorted(root.glob("PHASE1*.md")) + sorted(root.glob("PHASE_1*.md")):
            if p.exists() and p.is_file():
                records.append(
                    FileRecord(
                        path=p.relative_to(REPO_ROOT),
                        size_bytes=p.stat().st_size,
                        sha256=_sha256(p),
                        category="phase1_documentation",
                    )
                )

    tests_dir = REPO_ROOT / "tests"
    if tests_dir.exists():
        for p in sorted(tests_dir.glob("test_phase1*.py")):
            records.append(
                FileRecord(
                    path=p.relative_to(REPO_ROOT),
                    size_bytes=p.stat().st_size,
                    sha256=_sha256(p),
                    category="phase1_tests",
                )
            )

    # Any remaining direct Phase 1 references in tests
    for p in sorted((REPO_ROOT / "tests").glob("*.py")):
        if p.name.startswith("test_phase1"):
            continue
        try:
            txt = p.read_text(encoding="utf-8")
        except Exception:
            continue
        if "canonic_phases.Phase_one" in txt or "Phase_one" in txt:
            records.append(
                FileRecord(
                    path=p.relative_to(REPO_ROOT),
                    size_bytes=p.stat().st_size,
                    sha256=_sha256(p),
                    category="phase1_tests",
                )
            )

    # De-duplicate by path
    dedup: dict[str, FileRecord] = {}
    for r in records:
        dedup[str(r.path)] = r
    return [dedup[k] for k in sorted(dedup.keys())]


def _run_rg(pattern: str) -> str:
    cmd = [
        "rg",
        "-n",
        "--no-ignore",
        "--max-columns",
        "200",
        "--max-columns-preview",
        "-S",
        pattern,
        ".",
    ]
    proc = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "LC_ALL": "C"},
    )
    if proc.returncode == 0:
        return proc.stdout.strip()
    if proc.returncode == 1:
        return ""
    return f"[rg_error] rc={proc.returncode} stderr={proc.stderr.strip()}"


def _render_file_inventory(records: list[FileRecord]) -> str:
    lines = []
    lines.append("| Category | Path | Bytes | SHA-256 |")
    lines.append("|---|---|---:|---|")
    for r in records:
        lines.append(f"| `{r.category}` | `{r.path.as_posix()}` | {r.size_bytes} | `{r.sha256}` |")
    return "\n".join(lines)


def _render_reference_inventory() -> str:
    patterns = [
        ("canonic_phases.Phase_one", r"canonic_phases\.Phase_one"),
        ("Phase_one", r"\bPhase_one\b"),
        ("phase_1_cpp_ingestion", r"phase_1_cpp_ingestion"),
        ("phase1_", r"phase1_"),
        ("importlib.import_module", r"importlib\\.import_module"),
        ("__import__(", r"__import__\\("),
        ("FORCING ROUTE", r"FORCING ROUTE"),
    ]

    out = []
    for label, pat in patterns:
        hits = _run_rg(pat)
        count = 0 if not hits else len(hits.splitlines())
        out.append(f"### {label}\n\nhits={count}\n")
        if hits:
            out.append("```text")
            out.append(hits)
            out.append("```")
        else:
            out.append("```text\n(no hits)\n```")
        out.append("")
    return "\n".join(out)


def _render_orchestrator_call_graph() -> str:
    targets = [
        ("execute_phase_1_with_full_contract (all call sites)", r"execute_phase_1_with_full_contract"),
        ("from canonic_phases.Phase_one import ...", r"from canonic_phases\\.Phase_one import"),
        ("from canonic_phases.Phase_one\\.phase1_.*", r"canonic_phases\\.Phase_one\\.phase1_"),
    ]
    out = []
    for label, pat in targets:
        hits = _run_rg(pat)
        count = 0 if not hits else len(hits.splitlines())
        out.append(f"### {label}\n\nhits={count}\n")
        out.append("```text")
        out.append(hits if hits else "(no hits)")
        out.append("```")
        out.append("")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path for the report (default: artifacts/reports/PHASE1_CPP_RIA_YYYY-MM-DD.md)",
    )
    args = parser.parse_args()

    today = datetime.now(timezone.utc).date().isoformat()
    output = args.output or (
        REPO_ROOT / "artifacts" / "reports" / f"PHASE1_CPP_RIA_{today}.md"
    )
    output.parent.mkdir(parents=True, exist_ok=True)

    records = _collect_phase1_files()
    report = f"""# Phase 1 CPP Repository Inventory Artifact (RIA)

Generated: `{_utc_now_iso()}`

## 1) Phase 1 File Inventory

files={len(records)}

{_render_file_inventory(records)}

## 2) Import/Reference Inventory

{_render_reference_inventory()}

## 3) Orchestrator Call Graph Evidence

{_render_orchestrator_call_graph()}
"""

    output.write_text(report, encoding="utf-8")
    print(json.dumps({"output": str(output.relative_to(REPO_ROOT)), "files": len(records)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class BundledFile:
    path: str
    sha256: str
    size_bytes: int
    content: str


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_text(path: Path) -> tuple[bytes, str]:
    raw = path.read_bytes()
    return raw, raw.decode("utf-8", errors="replace")


def _expand_glob(root: Path, pattern: str) -> list[Path]:
    return sorted((root / pattern).parent.glob((root / pattern).name))


def _expand_rglob(root: Path, pattern: str) -> list[Path]:
    return sorted(root.rglob(pattern))


def _collect_paths(root: Path) -> list[Path]:
    include_paths: list[Path] = []
    include_paths.extend(_expand_rglob(root / "src", "*.py"))
    include_paths.extend(_expand_rglob(root / "tests", "*.py"))
    include_paths.extend(_expand_glob(root, "*.py"))

    for rel in [
        "pyproject.toml",
        "setup.py",
        "AGENTS.md",
        "README.md",
        "README.ES.md",
        "pdt_analysis_report.json",
        "canonic_questionnaire_central/pattern_registry.json",
    ]:
        path = root / rel
        if path.exists():
            include_paths.append(path)

    unique: dict[str, Path] = {}
    for path in include_paths:
        if path.is_file():
            unique[str(path.resolve())] = path
    return sorted(unique.values(), key=lambda p: str(p))


def _bundle_file(root: Path, path: Path) -> BundledFile:
    raw, text = _read_text(path)
    return BundledFile(
        path=str(path.relative_to(root)),
        sha256=_sha256_bytes(raw),
        size_bytes=len(raw),
        content=text,
    )


def build_bundle(root: Path) -> dict[str, Any]:
    paths = _collect_paths(root)
    bundled = [_bundle_file(root, path) for path in paths]
    total_bytes = sum(item.size_bytes for item in bundled)
    return {
        "root": str(root),
        "file_count": len(bundled),
        "total_bytes": total_bytes,
        "files": [item.__dict__ for item in bundled],
    }


def main() -> None:
    root = Path(__file__).resolve().parent
    bundle = build_bundle(root)
    try:
        sys.stdout.write(json.dumps(bundle, ensure_ascii=False))
    except BrokenPipeError:
        raise SystemExit(0) from None


if __name__ == "__main__":
    main()

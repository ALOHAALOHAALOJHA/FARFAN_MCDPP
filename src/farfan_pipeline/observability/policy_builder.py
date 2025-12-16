"""Import/path policy builder.

The verified runner optionally uses this to audit import/path hygiene.
This implementation is conservative and intentionally lightweight.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


def compute_repo_root() -> Path:
    """Best-effort repo root detection (pyproject.toml marker)."""

    cur = Path(__file__).resolve()
    for parent in [cur.parent] + list(cur.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    return cur.parent


@dataclass(frozen=True)
class ImportPolicy:
    allowed_roots: tuple[Path, ...]


@dataclass(frozen=True)
class PathPolicy:
    repo_root: Path


def build_import_policy(repo_root: Path) -> ImportPolicy:
    return ImportPolicy(allowed_roots=(repo_root / "src",))


def build_path_policy(repo_root: Path) -> PathPolicy:
    return PathPolicy(repo_root=repo_root)

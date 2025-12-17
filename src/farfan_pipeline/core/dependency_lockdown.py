from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def _env_flag(name: str) -> bool | None:
    value = os.environ.get(name)
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off", ""}:
        return False
    return None


def _is_offline_mode() -> bool:
    if _env_flag("TRANSFORMERS_OFFLINE") is True:
        return True
    if _env_flag("HF_HUB_OFFLINE") is True:
        return True
    hf_online = _env_flag("HF_ONLINE")
    if hf_online is True:
        return False
    return True


def _candidate_hf_cache_dirs() -> list[Path]:
    candidates: list[Path] = []

    for env_name in ("HF_HUB_CACHE", "HUGGINGFACE_HUB_CACHE", "TRANSFORMERS_CACHE", "SENTENCE_TRANSFORMERS_HOME"):
        raw = os.environ.get(env_name)
        if raw:
            candidates.append(Path(raw).expanduser())

    hf_home = os.environ.get("HF_HOME")
    if hf_home:
        candidates.append(Path(hf_home).expanduser() / "hub")

    xdg_cache = os.environ.get("XDG_CACHE_HOME")
    if xdg_cache:
        candidates.append(Path(xdg_cache).expanduser() / "huggingface" / "hub")

    candidates.append(Path.home() / ".cache" / "huggingface" / "hub")

    deduped: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved not in seen:
            seen.add(resolved)
            deduped.append(resolved)
    return deduped


def _model_cache_folder_name(model_name: str) -> str:
    normalized = model_name.strip()
    if not normalized:
        return ""
    if normalized.startswith("models--"):
        return normalized
    return f"models--{normalized.replace('/', '--')}"


def _is_model_cached(model_name: str) -> bool:
    model_name = model_name.strip()
    if not model_name:
        return False

    local_path = Path(model_name).expanduser()
    if local_path.exists():
        return True

    cache_folder = _model_cache_folder_name(model_name)
    if not cache_folder:
        return False

    for cache_dir in _candidate_hf_cache_dirs():
        folder = cache_dir / cache_folder
        if not folder.exists() or not folder.is_dir():
            continue
        snapshots = folder / "snapshots"
        if snapshots.exists() and any(snapshots.iterdir()):
            return True
        refs = folder / "refs"
        if refs.exists() and any(refs.iterdir()):
            return True
        if any(folder.iterdir()):
            return True

    return False


@dataclass(frozen=True, slots=True)
class DependencyLockdown:
    offline: bool

    def get_mode_description(self) -> str:
        if self.offline:
            return "Offline mode - remote dependency access disabled"
        return "Online mode - remote dependency access enabled"

    def check_online_model_access(self, model_name: str, operation: str) -> None:
        if not self.offline:
            return
        if _is_model_cached(model_name):
            return
        raise RuntimeError(
            f"Dependency lockdown: '{operation}' requires downloading '{model_name}', "
            "but offline mode is enabled. Set HF_ONLINE=1 (and allow network access) "
            "or pre-cache the model locally."
        )


@lru_cache(maxsize=1)
def get_dependency_lockdown() -> DependencyLockdown:
    return DependencyLockdown(offline=_is_offline_mode())


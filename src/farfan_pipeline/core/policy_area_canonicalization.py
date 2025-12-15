from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Final

_LEGACY_POLICY_AREA_RE: Final[re.Pattern[str]] = re.compile(r"^P(?:10|[1-9])$")
_CANONICAL_POLICY_AREA_RE: Final[re.Pattern[str]] = re.compile(r"^PA(?:0[1-9]|10)$")

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[3]
_MAPPING_PATH: Final[Path] = _REPO_ROOT / "policy_area_mapping.json"


class PolicyAreaCanonicalizationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class PolicyAreaMappingEntry:
    legacy_id: str
    canonical_id: str
    canonical_name: str
    source_of_truth: str


def is_legacy_policy_area_id(value: str) -> bool:
    return _LEGACY_POLICY_AREA_RE.fullmatch(value) is not None


def is_canonical_policy_area_id(value: str) -> bool:
    return _CANONICAL_POLICY_AREA_RE.fullmatch(value) is not None


@lru_cache(maxsize=1)
def _load_policy_area_mapping_entries() -> tuple[PolicyAreaMappingEntry, ...]:
    try:
        payload = json.loads(_MAPPING_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        msg = f"Missing policy area mapping file: {_MAPPING_PATH}"
        raise PolicyAreaCanonicalizationError(msg) from exc
    except json.JSONDecodeError as exc:
        msg = f"Invalid JSON in policy area mapping file: {_MAPPING_PATH}"
        raise PolicyAreaCanonicalizationError(msg) from exc

    if not isinstance(payload, list):
        msg = "policy_area_mapping.json must be a JSON list"
        raise PolicyAreaCanonicalizationError(msg)

    entries: list[PolicyAreaMappingEntry] = []
    for idx, item in enumerate(payload):
        if not isinstance(item, dict):
            msg = f"Mapping entry {idx} must be an object"
            raise PolicyAreaCanonicalizationError(msg)

        legacy_id = item.get("legacy_id")
        canonical_id = item.get("canonical_id")
        canonical_name = item.get("canonical_name")
        source_of_truth = item.get("source_of_truth")

        if not isinstance(legacy_id, str) or not is_legacy_policy_area_id(legacy_id):
            msg = f"Mapping entry {idx} has invalid legacy_id: {legacy_id!r}"
            raise PolicyAreaCanonicalizationError(msg)

        if not isinstance(canonical_id, str) or not is_canonical_policy_area_id(canonical_id):
            msg = f"Mapping entry {idx} has invalid canonical_id: {canonical_id!r}"
            raise PolicyAreaCanonicalizationError(msg)

        if not isinstance(canonical_name, str) or not canonical_name.strip():
            msg = f"Mapping entry {idx} has invalid canonical_name: {canonical_name!r}"
            raise PolicyAreaCanonicalizationError(msg)

        if source_of_truth != "monolith":
            msg = f"Mapping entry {idx} has invalid source_of_truth: {source_of_truth!r}"
            raise PolicyAreaCanonicalizationError(msg)

        entries.append(
            PolicyAreaMappingEntry(
                legacy_id=legacy_id,
                canonical_id=canonical_id,
                canonical_name=canonical_name,
                source_of_truth=source_of_truth,
            )
        )

    legacy_ids = [e.legacy_id for e in entries]
    canonical_ids = [e.canonical_id for e in entries]

    if len(set(legacy_ids)) != len(legacy_ids):
        msg = "policy_area_mapping.json contains duplicate legacy_id entries"
        raise PolicyAreaCanonicalizationError(msg)

    if len(set(canonical_ids)) != len(canonical_ids):
        msg = "policy_area_mapping.json contains duplicate canonical_id entries"
        raise PolicyAreaCanonicalizationError(msg)

    return tuple(sorted(entries, key=lambda e: e.canonical_id))


@lru_cache(maxsize=1)
def _legacy_to_canonical_map() -> dict[str, str]:
    return {e.legacy_id: e.canonical_id for e in _load_policy_area_mapping_entries()}


@lru_cache(maxsize=1)
def _canonical_to_name_map() -> dict[str, str]:
    return {e.canonical_id: e.canonical_name for e in _load_policy_area_mapping_entries()}


def canonicalize_policy_area_id(value: str) -> str:
    if is_canonical_policy_area_id(value):
        if value in _canonical_to_name_map():
            return value
        raise PolicyAreaCanonicalizationError(f"Unknown canonical policy area id: {value}")

    if is_legacy_policy_area_id(value):
        mapped = _legacy_to_canonical_map().get(value)
        if mapped is None:
            raise PolicyAreaCanonicalizationError(f"Unknown legacy policy area id: {value}")
        return mapped

    raise PolicyAreaCanonicalizationError(
        f"Invalid policy area id: {value!r} (expected legacy or canonical id)"
    )


def canonical_policy_area_name(value: str) -> str:
    canonical_id = canonicalize_policy_area_id(value)
    return _canonical_to_name_map()[canonical_id]


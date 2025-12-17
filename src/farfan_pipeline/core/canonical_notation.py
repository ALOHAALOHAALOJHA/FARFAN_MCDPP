from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any

_DIMENSION_MAPPING_FILE = "dimension_mapping.json"
_POLICY_MAPPING_FILE = "policy_area_mapping.json"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None


@dataclass(frozen=True, slots=True)
class DimensionInfo:
    legacy_id: str
    code: str
    name: str
    label: str | None


@dataclass(frozen=True, slots=True)
class PolicyAreaInfo:
    code: str
    name: str
    legacy_id: str | None


class CanonicalDimension(Enum):
    D1 = "DIM01"
    D2 = "DIM02"
    D3 = "DIM03"
    D4 = "DIM04"
    D5 = "DIM05"
    D6 = "DIM06"


@lru_cache(maxsize=1)
def get_all_dimensions() -> dict[str, DimensionInfo]:
    mapping_path = _repo_root() / _DIMENSION_MAPPING_FILE
    payload = _load_json(mapping_path)
    if not isinstance(payload, list):
        return {}

    result: dict[str, DimensionInfo] = {}
    for entry in payload:
        if not isinstance(entry, dict):
            continue

        legacy_id = entry.get("legacy_id")
        code = entry.get("canonical_id")
        name = entry.get("canonical_name")
        if not isinstance(legacy_id, str) or not isinstance(code, str) or not isinstance(name, str):
            continue

        result[legacy_id] = DimensionInfo(legacy_id=legacy_id, code=code, name=name, label=None)

    return result


@lru_cache(maxsize=1)
def get_all_policy_areas() -> dict[str, PolicyAreaInfo]:
    mapping_path = _repo_root() / _POLICY_MAPPING_FILE
    payload = _load_json(mapping_path)
    if not isinstance(payload, list):
        return {}

    result: dict[str, PolicyAreaInfo] = {}
    for entry in payload:
        if not isinstance(entry, dict):
            continue

        legacy_id = entry.get("legacy_id")
        code = entry.get("canonical_id")
        name = entry.get("canonical_name")
        if not isinstance(code, str) or not isinstance(name, str):
            continue

        result[code] = PolicyAreaInfo(
            code=code, name=name, legacy_id=legacy_id if isinstance(legacy_id, str) else None
        )

    return result


CANONICAL_DIMENSIONS: dict[str, str] = {info.code: info.name for info in get_all_dimensions().values()}
CANONICAL_POLICY_AREAS: dict[str, str] = {
    code: info.name for code, info in get_all_policy_areas().items()
}


def get_dimension_info(dimension_key: str) -> DimensionInfo:
    dimensions = get_all_dimensions()
    if dimension_key in dimensions:
        return dimensions[dimension_key]

    for info in dimensions.values():
        if info.code == dimension_key:
            return info

    raise KeyError(f"Unknown dimension key: {dimension_key}")


def get_dimension_description(dimension_code: str) -> str:
    try:
        return get_dimension_info(dimension_code).name
    except KeyError:
        return dimension_code


def get_policy_description(policy_code: str) -> str:
    policy_areas = get_all_policy_areas()
    if policy_code in policy_areas:
        return policy_areas[policy_code].name
    return policy_code

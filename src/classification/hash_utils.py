"""Utilities for deterministic hashing of epistemological classifications.

This module is intentionally dependency-free and deterministic.

Design goals:
- Hash must change if *any* decision field changes.
- Hash must be stable across dict insertion order.
- Inputs must be normalized (e.g., None vs "" for signature strings).
- Fail loudly if the decision cannot be deterministically serialized.

Canonicalization:
`json.dumps(..., sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)`
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import fields, is_dataclass
from typing import Any, Mapping


def _norm_text(value: object) -> str:
    return "" if value is None else str(value)


def _normalize_parameters(parameters: object) -> list[dict[str, Any]]:
    if not isinstance(parameters, list):
        return []
    normalized: list[dict[str, Any]] = []
    for p in parameters:
        if not isinstance(p, dict):
            continue
        # Normalize common keys without guessing extra schema.
        normalized.append(
            {
                **p,
                "name": _norm_text(p.get("name")),
                "type": _norm_text(p.get("type")),
            }
        )
    return normalized


def _method_signature_blob(method_name: str, method: Mapping[str, Any]) -> str:
    """Builds a deterministic signature blob from a method signature dict.

    This is designed to be stable across runs and independent of dict insertion order.
    """

    payload = {
        "method_name": _norm_text(method_name),
        "return_type": _norm_text(method.get("return_type")),
        "docstring": _norm_text(method.get("docstring")),
        "parameters": _normalize_parameters(method.get("parameters", [])),
    }
    return json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    )


def decision_payload_for_hash(decision: object) -> dict[str, Any]:
    """Serializa *todos* los campos del dataclass de decisión.

    Contract:
    - Si `decision` no es dataclass -> TypeError.
    - El payload incluye exactamente los campos `dataclasses.fields(decision)`.
    """

    if not is_dataclass(decision):
        raise TypeError(
            "decision_payload_for_hash requiere un dataclass (p.ej. MethodDecision). "
            f"Recibido: {type(decision)!r}"
        )

    return {f.name: getattr(decision, f.name) for f in fields(decision)}


def compute_classification_hash(
    method: Mapping[str, Any],
    decision: object,
    *,
    method_name: str | None = None,
) -> str:
    """Hash determinístico para detectar cambios en clasificación.

    Requirements (rigor):
    - `sort_keys=True` is mandatory for determinism.
    - Hash is computed over UTF-8 encoded canonical JSON.
    - Includes method signature blob + explicit decision attributes.

    The function is resilient to different `MethodDecision` shapes by reading common
    attributes via `getattr`.
    """

    resolved_name = (
        method_name
        if method_name is not None
        else _norm_text(method.get("name"))
        if method.get("name") is not None
        else _norm_text(method.get("method_name"))
    )

    decision_payload = decision_payload_for_hash(decision)

    blob = {
        "method_signature": _method_signature_blob(resolved_name, method),
        "decision": decision_payload,
    }

    canonical_json = json.dumps(
        blob,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

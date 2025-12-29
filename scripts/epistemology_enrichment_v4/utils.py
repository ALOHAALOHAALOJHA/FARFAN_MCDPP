from __future__ import annotations

import json
import unicodedata
from typing import Any


def norm(value: object) -> str:
    return "" if value is None else str(value)


def norm_text_for_match(value: object) -> str:
    """Normalización determinista para matching cross-language.

    - NFKC para reducir variantes Unicode.
    - casefold (más robusto que lower para Unicode).
    """

    return unicodedata.normalize("NFKC", norm(value)).casefold()


def contains_any(haystack: str, needles: list[str]) -> bool:
    h = norm_text_for_match(haystack)
    return any(norm_text_for_match(n) in h for n in needles)


def method_signature_blob(method_name: str, method: dict[str, Any]) -> str:
    return " ".join(
        [
            method_name,
            norm(method.get("return_type")),
            norm(method.get("docstring")),
            json.dumps(method.get("parameters", []), ensure_ascii=False, sort_keys=True),
        ]
    )

"""AtroZ Dashboard API v1 helpers."""

from __future__ import annotations

import re
import unicodedata


_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_value.lower()
    slug = _NON_ALNUM_RE.sub("-", lowered).strip("-")
    return slug

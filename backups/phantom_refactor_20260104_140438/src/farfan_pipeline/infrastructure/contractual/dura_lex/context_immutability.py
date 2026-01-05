from __future__ import annotations

import json
from dataclasses import is_dataclass, fields, FrozenInstanceError
from typing import Any
from collections.abc import Mapping as ABCMapping
from types import MappingProxyType
from collections.abc import Sequence as ABCSequence  # optional, for type checks

class ContextImmutabilityContract:
    @staticmethod
    def _to_plain(obj: Any) -> Any:
        """
        Convert dataclasses + immutable containers (MappingProxyType, tuples, frozensets)
        into plain Python structures without deepcopy(). This avoids mappingproxy pickling.
        """
        if is_dataclass(obj):
            return {f.name: ContextImmutabilityContract._to_plain(getattr(obj, f.name)) for f in fields(obj)}
        if isinstance(obj, (MappingProxyType, ABCMapping)):
            return {k: ContextImmutabilityContract._to_plain(v) for k, v in obj.items()}
        if isinstance(obj, (tuple, list, set, frozenset)):
            return [ContextImmutabilityContract._to_plain(v) for v in obj]
        return obj

    @staticmethod
    def _to_canonical(obj: Any) -> Any:
        # Sort mapping keys deterministically; lists already deterministic after _to_plain
        if isinstance(obj, dict):
            return {k: ContextImmutabilityContract._to_canonical(obj[k]) for k in sorted(obj.keys())}
        if isinstance(obj, list):
            return [ContextImmutabilityContract._to_canonical(v) for v in obj]
        return obj

    @staticmethod
    def canonical_digest(ctx: Any) -> str:
        # Build plain JSON-safe object without deepcopy(), then canonicalize & hash.
        plain = ContextImmutabilityContract._to_plain(ctx)
        canon = ContextImmutabilityContract._to_canonical(plain)
        s = json.dumps(canon, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        try:
            import blake3
            return blake3.blake3(s.encode("utf-8")).hexdigest()
        except Exception:
            import hashlib
            return hashlib.sha256(s.encode("utf-8")).hexdigest()

    @staticmethod
    def verify_immutability(ctx: Any) -> str:
        """
        Attempt to mutate: (1) top-level attribute, (2) deep mapping.
        Both must fail. Return canonical digest for equality comparisons.
        """
        # 1) Top-level attribute mutation must fail
        try:
            setattr(ctx, "traceability_id", "MUTATE_ME")
            raise RuntimeError("Mutation succeeded but should have failed!")
        except (FrozenInstanceError, AttributeError, TypeError):
            pass  # expected

        # 2) Deep mapping mutation must fail
        deep_map = getattr(ctx, "dnp_standards", None)
        if isinstance(deep_map, (MappingProxyType, ABCMapping)):
            try:
                deep_map["__MUTATE__"] = 1  # type: ignore[index]
                raise RuntimeError("Deep mutation succeeded but should have failed!")
            except (TypeError, AttributeError):
                pass  # expected

        # 3) Deterministic canonical digest
        return ContextImmutabilityContract.canonical_digest(ctx)

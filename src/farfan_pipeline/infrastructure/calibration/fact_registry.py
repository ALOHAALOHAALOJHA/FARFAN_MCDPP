"""
Canonical Fact Registry
=======================
Enforces granularity without redundancy.

DESIGN PATTERNS:
- Registry Pattern: Central repository of facts
- Flyweight Pattern: Shared representation for identical content
- Observer Pattern: Notifies on duplicate detection

INVARIANTS:
- INV-FACT-001: Every fact has exactly one canonical representation
- INV-FACT-002: Duplicate content triggers provenance logging, not addition
- INV-FACT-003: Verbosity ratio = |unique_facts| / |total_submissions| >= 0.90
"""

from __future__ import annotations

import hashlib
import logging
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Final

logger = logging.getLogger(__name__)


class EpistemologicalLevel(Enum):
    """Epistemic level that produced the fact."""

    N1_EMP = "N1-EMP"
    N2_INF = "N2-INF"
    N3_AUD = "N3-AUD"


@dataclass(frozen=True, slots=True)
class FactEntry:
    """
    Atomic fact unit in contract.

    Immutable once created.  Content hash determines identity.
    """

    fact_id: str  # UUID assigned at registration
    content_hash: str  # SHA-256 of normalized content
    source_method: str  # method_id that produced it
    content: str  # normalized text
    epistemic_level: EpistemologicalLevel
    timestamp: datetime
    dependencies: frozenset[str]  # fact_ids this depends on

    @staticmethod
    def compute_content_hash(content: str) -> str:
        """Compute hash of normalized content."""
        normalized = content.strip().lower()
        return hashlib.sha256(normalized.encode()).hexdigest()


@dataclass(frozen=True)
class DuplicateRecord:
    """Record of a duplicate fact submission."""

    original_fact_id: str
    duplicate_source_method: str
    duplicate_timestamp: datetime
    content_hash: str


@dataclass
class RegistryStatistics:
    """Statistics about registry state."""

    total_submissions: int
    unique_facts: int
    duplicate_count: int
    verbosity_ratio: float
    facts_by_level: dict[str, int]


class CanonicalFactRegistry:
    """
    Central registry for facts with deduplication.

    Thread-safe for single-threaded async operations.
    NOT thread-safe for true multi-threading.
    """

    _VERBOSITY_THRESHOLD: Final[float] = 0.90

    def __init__(
        self,
        on_duplicate: Callable[[DuplicateRecord], None] | None = None,
    ) -> None:
        self._facts: dict[str, FactEntry] = {}
        self._content_hashes: dict[str, str] = {}  # hash -> fact_id
        self._duplicates: list[DuplicateRecord] = []
        self._submission_count: int = 0
        self._on_duplicate = on_duplicate or self._default_duplicate_handler
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def register(self, fact: FactEntry) -> tuple[bool, str]:
        """
        Register a fact.

        Returns:
            Tuple of (was_new, canonical_fact_id)
            - was_new: True if fact was new, False if duplicate
            - canonical_fact_id: ID of the canonical fact (original if duplicate)
        """
        self._submission_count += 1

        if fact.content_hash in self._content_hashes:
            # Duplicate content
            original_id = self._content_hashes[fact.content_hash]
            duplicate_record = DuplicateRecord(
                original_fact_id=original_id,
                duplicate_source_method=fact.source_method,
                duplicate_timestamp=fact.timestamp,
                content_hash=fact.content_hash,
            )
            self._duplicates.append(duplicate_record)
            self._on_duplicate(duplicate_record)
            return (False, original_id)

        # New fact
        self._facts[fact.fact_id] = fact
        self._content_hashes[fact.content_hash] = fact.fact_id

        self._logger.debug(f"Registered fact {fact.fact_id[: 8]}... from {fact.source_method}")

        return (True, fact.fact_id)

    def get(self, fact_id: str) -> FactEntry | None:
        """Retrieve fact by ID."""
        return self._facts.get(fact_id)

    def get_by_hash(self, content_hash: str) -> FactEntry | None:
        """Retrieve fact by content hash."""
        fact_id = self._content_hashes.get(content_hash)
        if fact_id:
            return self._facts.get(fact_id)
        return None

    def get_by_level(self, level: EpistemologicalLevel) -> Iterator[FactEntry]:
        """Iterate facts from a specific epistemic level."""
        for fact in self._facts.values():
            if fact.epistemic_level == level:
                yield fact

    def get_statistics(self) -> RegistryStatistics:
        """Compute registry statistics."""
        unique_count = len(self._facts)
        duplicate_count = len(self._duplicates)

        verbosity_ratio = (
            unique_count / self._submission_count if self._submission_count > 0 else 1.0
        )

        facts_by_level = {level.value: 0 for level in EpistemologicalLevel}
        for fact in self._facts.values():
            facts_by_level[fact.epistemic_level.value] += 1

        return RegistryStatistics(
            total_submissions=self._submission_count,
            unique_facts=unique_count,
            duplicate_count=duplicate_count,
            verbosity_ratio=verbosity_ratio,
            facts_by_level=facts_by_level,
        )

    def validate_verbosity(self) -> bool:
        """
        Check if verbosity ratio meets threshold.

        INV-FACT-003: verbosity_ratio >= 0.90
        """
        stats = self.get_statistics()
        if stats.verbosity_ratio < self._VERBOSITY_THRESHOLD:
            self._logger.warning(
                f"Verbosity ratio {stats.verbosity_ratio:.2%} below threshold "
                f"{self._VERBOSITY_THRESHOLD:.2%}"
            )
            return False
        return True

    def export_provenance(self) -> dict[str, object]:
        """Export complete provenance for audit."""
        return {
            "facts": {
                fid: {
                    "content_hash": f.content_hash,
                    "source_method": f.source_method,
                    "epistemic_level": f.epistemic_level.value,
                    "timestamp": f.timestamp.isoformat(),
                    "dependencies": list(f.dependencies),
                    "content_preview": (
                        f.content[:100] + "..." if len(f.content) > 100 else f.content
                    ),
                }
                for fid, f in self._facts.items()
            },
            "duplicates": [
                {
                    "original_fact_id": d.original_fact_id,
                    "duplicate_source": d.duplicate_source_method,
                    "timestamp": d.duplicate_timestamp.isoformat(),
                }
                for d in self._duplicates
            ],
            "statistics": {
                "total_submissions": self._submission_count,
                "unique_facts": len(self._facts),
                "duplicate_count": len(self._duplicates),
                "verbosity_ratio": self.get_statistics().verbosity_ratio,
            },
        }

    def _default_duplicate_handler(self, record: DuplicateRecord) -> None:
        """Default handler logs duplicates."""
        self._logger.info(
            f"DUPLICATE_FACT:  {record.duplicate_source_method} produced content "
            f"identical to fact {record.original_fact_id}"
        )


class FactFactory:
    """
    Factory for creating facts with proper IDs and hashes.

    DESIGN PATTERN: Factory Pattern
    - Ensures consistent fact creation
    - Handles ID generation
    """

    _counter: int = 0

    @classmethod
    def create(
        cls,
        content: str,
        source_method: str,
        epistemic_level: EpistemologicalLevel,
        dependencies: frozenset[str] | None = None,
    ) -> FactEntry:
        """Create a new fact entry."""
        cls._counter += 1
        fact_id = f"FACT_{cls._counter:08d}_{hashlib.md5(content.encode()).hexdigest()[:8]}"

        return FactEntry(
            fact_id=fact_id,
            content_hash=FactEntry.compute_content_hash(content),
            source_method=source_method,
            content=content,
            epistemic_level=epistemic_level,
            timestamp=datetime.now(UTC),
            dependencies=dependencies or frozenset(),
        )

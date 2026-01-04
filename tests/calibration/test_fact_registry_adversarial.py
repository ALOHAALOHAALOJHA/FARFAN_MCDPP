"""
ADVERSARIAL TESTS FOR FACT REGISTRY
===================================
"""
import pytest
from datetime import datetime, timezone
from src.farfan_pipeline.infrastructure.calibration.fact_registry import (
    CanonicalFactRegistry,
    FactEntry,
    FactFactory,
    EpistemologicalLevel,
)


class TestDeduplication:
    """Attempts to insert duplicates."""

    def test_exact_duplicate_not_added(self) -> None:
        """Identical content from different methods should deduplicate."""
        registry = CanonicalFactRegistry()

        fact1 = FactFactory.create(
            content="El municipio tiene 50,000 habitantes.",
            source_method="Extractor1.extract",
            epistemic_level=EpistemologicalLevel.N1_EMP,
        )

        fact2 = FactFactory.create(
            content="El municipio tiene 50,000 habitantes.",  # IDENTICAL
            source_method="Extractor2.extract",  # Different method
            epistemic_level=EpistemologicalLevel.N1_EMP,
        )

        was_new1, id1 = registry.register(fact1)
        was_new2, id2 = registry.register(fact2)

        assert was_new1 is True
        assert was_new2 is False
        assert id1 == id2  # Should return original ID
        assert registry.get_statistics().unique_facts == 1
        assert registry.get_statistics().duplicate_count == 1

    def test_whitespace_normalization_deduplicates(self) -> None:
        """Content differing only in whitespace should deduplicate."""
        registry = CanonicalFactRegistry()

        fact1 = FactFactory.create(
            content="Budget is 1,000,000 COP",
            source_method="Method1",
            epistemic_level=EpistemologicalLevel.N1_EMP,
        )

        fact2 = FactFactory.create(
            content="  Budget is 1,000,000 COP  ",  # Extra whitespace
            source_method="Method2",
            epistemic_level=EpistemologicalLevel.N1_EMP,
        )

        registry.register(fact1)
        was_new, _ = registry.register(fact2)

        assert was_new is False

    def test_case_normalization_deduplicates(self) -> None:
        """Content differing only in case should deduplicate."""
        registry = CanonicalFactRegistry()

        fact1 = FactFactory.create(
            content="POPULATION IS 100000",
            source_method="Method1",
            epistemic_level=EpistemologicalLevel.N1_EMP,
        )

        fact2 = FactFactory.create(
            content="population is 100000",  # Different case
            source_method="Method2",
            epistemic_level=EpistemologicalLevel.N1_EMP,
        )

        registry.register(fact1)
        was_new, _ = registry.register(fact2)

        assert was_new is False


class TestVerbosityInvariant:
    """Tests verbosity threshold enforcement."""

    def test_low_verbosity_fails_validation(self) -> None:
        """Verbosity below 0.90 should fail validation."""
        registry = CanonicalFactRegistry()

        # Register 5 unique facts
        for i in range(5):
            fact = FactFactory.create(
                content=f"Unique fact {i}",
                source_method="Method",
                epistemic_level=EpistemologicalLevel.N1_EMP,
            )
            registry.register(fact)

        # Now submit 50 duplicates of the first fact
        duplicate_content = "Unique fact 0"
        for i in range(50):
            fact = FactFactory.create(
                content=duplicate_content,
                source_method=f"DuplicateMethod{i}",
                epistemic_level=EpistemologicalLevel.N1_EMP,
            )
            registry.register(fact)

        # Verbosity = 5 / 55 = 0.09 < 0.90
        assert registry.validate_verbosity() is False
        stats = registry.get_statistics()
        assert stats.verbosity_ratio < 0.90


class TestProvenanceExport:
    """Tests provenance export completeness."""

    def test_export_contains_all_required_fields(self) -> None:
        """Export must have facts, duplicates, statistics."""
        registry = CanonicalFactRegistry()

        fact = FactFactory.create(
            content="Test fact",
            source_method="TestMethod",
            epistemic_level=EpistemologicalLevel.N1_EMP,
        )
        registry.register(fact)

        export = registry.export_provenance()

        assert "facts" in export
        assert "duplicates" in export
        assert "statistics" in export

        # Check fact fields
        fact_data = list(export["facts"].values())[0]
        assert "content_hash" in fact_data
        assert "source_method" in fact_data
        assert "epistemic_level" in fact_data
        assert "timestamp" in fact_data
        assert "dependencies" in fact_data


class TestHashCollisionResistance:
    """Tests hash collision resistance with high volume."""

    def test_no_collisions_with_10k_unique_entries(self) -> None:
        """10K unique facts should have 10K unique hashes."""
        registry = CanonicalFactRegistry()
        
        for i in range(10000):
            fact = FactFactory.create(
                content=f"Unique fact number {i} with additional context to ensure uniqueness",
                source_method=f"Method{i}",
                epistemic_level=EpistemologicalLevel.N1_EMP,
            )
            was_new, _ = registry.register(fact)
            assert was_new is True, f"Collision detected at fact {i}"
        
        stats = registry.get_statistics()
        assert stats.unique_facts == 10000
        assert stats.duplicate_count == 0
        assert stats.verbosity_ratio == 1.0


class TestDuplicateObserver:
    """Tests Observer pattern for duplicate notification."""

    def test_duplicate_callback_invoked(self) -> None:
        """Observer callback must be invoked on duplicate."""
        duplicates_received: list = []
        
        def on_duplicate(record):
            duplicates_received.append(record)
        
        registry = CanonicalFactRegistry(on_duplicate=on_duplicate)
        
        fact1 = FactFactory.create(
            content="Same content",
            source_method="Method1",
            epistemic_level=EpistemologicalLevel.N1_EMP,
        )
        fact2 = FactFactory.create(
            content="Same content",
            source_method="Method2",
            epistemic_level=EpistemologicalLevel.N1_EMP,
        )
        
        registry.register(fact1)
        registry.register(fact2)
        
        assert len(duplicates_received) == 1
        assert duplicates_received[0].duplicate_source_method == "Method2"


class TestFactsByLevel:
    """Tests filtering facts by epistemic level."""

    def test_get_by_level_filters_correctly(self) -> None:
        """Facts should be retrievable by epistemic level."""
        registry = CanonicalFactRegistry()
        
        # Register facts at different levels
        for i, level in enumerate(EpistemologicalLevel):
            for j in range(3):
                fact = FactFactory.create(
                    content=f"Fact {i}_{j} at level {level.value}",
                    source_method="Method",
                    epistemic_level=level,
                )
                registry.register(fact)
        
        # Check each level has exactly 3 facts
        for level in EpistemologicalLevel:
            facts = list(registry.get_by_level(level))
            assert len(facts) == 3, f"Expected 3 facts at {level}, got {len(facts)}"

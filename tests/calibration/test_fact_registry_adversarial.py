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
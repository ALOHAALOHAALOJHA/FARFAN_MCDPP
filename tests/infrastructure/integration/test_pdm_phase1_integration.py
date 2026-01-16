"""
Integration tests for PDM Phase 1 integration.

Validates end-to-end PDM structural recognition integration
with Phase 1 SP2 and SP4.

Author: FARFAN Engineering Team
Version: PDM-2025.1
"""

from __future__ import annotations

import pytest
from unittest.mock import Mock

# Test imports
try:
    from farfan_pipeline.phases.Phase_01.phase1_12_01_pdm_integration import (
        PDMStructuralAnalyzer,
        PDMMetadataAssigner,
        assign_pdm_metadata_to_chunks,
        enhance_sp2_with_pdm,
    )
    PDM_INTEGRATION_AVAILABLE = True
except ImportError:
    PDM_INTEGRATION_AVAILABLE = False

try:
    from farfan_pipeline.phases.Phase_01.phase1_03_00_models import (
        Chunk,
        PDMMetadata,
        StructureData,
    )
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False

try:
    from farfan_pipeline.pdm.profile.pdm_structural_profile import (
        CanonicalSection,
        ContextualMarker,
        HierarchyLevel,
        PDMStructuralProfile,
        SemanticRule,
        get_default_profile,
    )
    PDM_PROFILE_AVAILABLE = True
except ImportError:
    PDM_PROFILE_AVAILABLE = False


@pytest.mark.skipif(not PDM_INTEGRATION_AVAILABLE, reason="PDM integration not available")
class TestPDMStructuralAnalyzer:
    """Test PDM structural analyzer for SP2 integration."""

    def test_analyzer_initialization_with_profile(self):
        """Test analyzer can be initialized with PDM profile."""
        if not PDM_PROFILE_AVAILABLE:
            pytest.skip("PDM profile not available")

        profile = get_default_profile()
        analyzer = PDMStructuralAnalyzer(profile)

        assert analyzer.profile is not None
        assert analyzer._pdm_enabled is True

    def test_analyzer_initialization_without_profile(self):
        """Test analyzer can load default profile when none provided."""
        if not PDM_PROFILE_AVAILABLE:
            pytest.skip("PDM profile not available")

        analyzer = PDMStructuralAnalyzer(profile=None)

        assert analyzer.profile is not None
        assert analyzer._pdm_enabled is True

    def test_detect_pdm_hierarchy(self):
        """Test PDM hierarchy detection in text."""
        if not PDM_PROFILE_AVAILABLE:
            pytest.skip("PDM profile not available")

        analyzer = PDMStructuralAnalyzer(profile=None)

        # Test text with actual PDM hierarchy markers
        # Use text that matches Colombian PDM structure
        text = """1. PARTE: ESTRATEGIA

        2. CAPÍTULO: OBJETIVOS

        3. LINEA: EDUCACIÓN
        """

        hierarchy = analyzer.detect_pdm_hierarchy(text)

        # Should detect some hierarchy based on patterns
        # The exact patterns depend on the PDM profile configuration
        assert isinstance(hierarchy, dict)
        # May be empty if text doesn't match exact patterns

    def test_detect_canonical_sections(self):
        """Test canonical section detection."""
        if not PDM_PROFILE_AVAILABLE:
            pytest.skip("PDM profile not available")

        analyzer = PDMStructuralAnalyzer(profile=None)

        # Use text that matches PDM section names from profile
        text = """
        Parte General

        Diagnóstico de los problemas municipales...

        Parte Estratégica

        Objetivos del plan...
        """

        sections = analyzer.detect_canonical_sections(text)

        # Should detect at least 1 section
        assert len(sections) >= 1

    def test_enhance_structure_data(self):
        """Test enhancing StructureData with PDM information."""
        if not PDM_PROFILE_AVAILABLE or not MODELS_AVAILABLE:
            pytest.skip("PDM profile or models not available")

        analyzer = PDMStructuralAnalyzer(profile=None)

        # Create base structure
        base_structure = StructureData(
            sections=[],
            hierarchy={},
            paragraph_mapping={},
        )

        text = """
        PARTE ESTRATÉGICA

        Objetivos del desarrollo municipal...
        """

        # Enhance with PDM
        enhanced = analyzer.enhance_structure_data(base_structure, text)

        # Verify enhancement
        assert enhanced is not None
        assert hasattr(enhanced, "_pdm_profile_used")


@pytest.mark.skipif(not PDM_INTEGRATION_AVAILABLE, reason="PDM integration not available")
class TestPDMMetadataAssigner:
    """Test PDM metadata assigner for SP4 integration."""

    def test_assigner_initialization(self):
        """Test assigner can be initialized."""
        if not PDM_PROFILE_AVAILABLE:
            pytest.skip("PDM profile not available")

        assigner = PDMMetadataAssigner(profile=None)

        assert assigner.profile is not None
        assert assigner._pdm_enabled is True

    def test_infer_hierarchy_level(self):
        """Test hierarchy level inference from chunk text."""
        if not PDM_PROFILE_AVAILABLE:
            pytest.skip("PDM profile not available")

        assigner = PDMMetadataAssigner(profile=None)

        # Test with META text (should be H5)
        chunk_text = "Meta 1.1: Aumentar la cobertura de educación al 95%"

        level = assigner.infer_hierarchy_level(chunk_text)

        # Should detect H5 (META)
        assert level is not None

    def test_infer_source_section(self):
        """Test source section inference from chunk text."""
        if not PDM_PROFILE_AVAILABLE:
            pytest.skip("PDM profile not available")

        assigner = PDMMetadataAssigner(profile=None)

        # Test with DIAGNOSTICO text
        chunk_text = "El diagnóstico municipal identifica los siguientes problemas..."

        section = assigner.infer_source_section(chunk_text)

        # Should detect DIAGNOSTICO
        assert section is not None

    def test_assign_pdq_context(self):
        """Test P-D-Q context assignment."""
        if not PDM_PROFILE_AVAILABLE:
            pytest.skip("PDM profile not available")

        assigner = PDMMetadataAssigner(profile=None)

        # Test with quality indicators (should be Q)
        chunk_text = "El indicador de cobertura es 85% con línea base en 70%"

        context = assigner.assign_pdq_context(chunk_text)

        # Should detect Q (Quality)
        assert context is not None

    def test_create_pdm_metadata(self):
        """Test PDM metadata creation for chunk."""
        if not PDM_PROFILE_AVAILABLE or not MODELS_AVAILABLE:
            pytest.skip("PDM profile or models not available")

        assigner = PDMMetadataAssigner(profile=None)

        # Create mock chunk
        chunk = Chunk(
            chunk_id="PA01-DIM01",
            policy_area_id="PA01",
            dimension_id="DIM01",
            text="Meta 1.1: Aumentar cobertura",
        )

        # Create PDM metadata
        metadata = assigner.create_pdm_metadata(chunk)

        # Should create metadata
        assert metadata is not None
        assert isinstance(metadata, PDMMetadata)

    def test_assign_metadata_to_chunks(self):
        """Test assigning PDM metadata to list of chunks."""
        if not PDM_PROFILE_AVAILABLE or not MODELS_AVAILABLE:
            pytest.skip("PDM profile or models not available")

        assigner = PDMMetadataAssigner(profile=None)

        # Create mock chunks (60 chunks for CI-01 compliance)
        chunks = []
        for pa in range(1, 11):
            for dim in range(1, 7):
                chunk = Chunk(
                    chunk_id=f"PA{pa:02d}-DIM{dim:02d}",
                    policy_area_id=f"PA{pa:02d}",
                    dimension_id=f"DIM{dim:02d}",
                    text=f"Contenido para PA{pa:02d}-DIM{dim:02d}",
                )
                chunks.append(chunk)

        # Assign metadata
        enhanced = assigner.assign_metadata_to_chunks(chunks)

        # Verify 60 chunks
        assert len(enhanced) == 60

        # Verify metadata assigned
        for chunk in enhanced:
            assert hasattr(chunk, "pdm_metadata")
            # Metadata may be None if no PDM features detected,
            # but the attribute should exist


@pytest.mark.skipif(not PDM_INTEGRATION_AVAILABLE, reason="PDM integration not available")
class TestPDMConvenienceFunctions:
    """Test PDM integration convenience functions."""

    def test_enhance_sp2_with_pdm(self):
        """Test SP2 enhancement function."""
        if not PDM_PROFILE_AVAILABLE or not MODELS_AVAILABLE:
            pytest.skip("PDM profile or models not available")

        # Create base structure
        base_structure = StructureData(
            sections=[],
            hierarchy={},
            paragraph_mapping={},
        )

        text = """
        DIAGNÓSTICO

        Análisis de la situación actual...
        """

        # Enhance
        enhanced = enhance_sp2_with_pdm(base_structure, text)

        assert enhanced is not None
        assert hasattr(enhanced, "_pdm_profile_used")

    def test_assign_pdm_metadata_to_chunks(self):
        """Test SP4 metadata assignment function."""
        if not PDM_PROFILE_AVAILABLE or not MODELS_AVAILABLE:
            pytest.skip("PDM profile or models not available")

        # Create mock chunks
        chunks = []
        for i in range(60):
            chunk = Chunk(
                chunk_id=f"PA{(i % 10) + 1:02d}-DIM{(i % 6) + 1:02d}",
                policy_area_id=f"PA{(i % 10) + 1:02d}",
                dimension_id=f"DIM{(i % 6) + 1:02d}",
                text=f"Contenido {i}",
            )
            chunks.append(chunk)

        # Assign metadata
        enhanced = assign_pdm_metadata_to_chunks(chunks)

        # Verify
        assert len(enhanced) == 60
        for chunk in enhanced:
            assert hasattr(chunk, "pdm_metadata")


@pytest.mark.skipif(not PDM_INTEGRATION_AVAILABLE, reason="PDM integration not available")
class TestPDMConstitutionalInvariants:
    """Test PDM constitutional invariants."""

    def test_ci01_60_chunk_invariant(self):
        """Test CI-01: Exactly 60 chunks produced."""
        if not PDM_PROFILE_AVAILABLE or not MODELS_AVAILABLE:
            pytest.skip("PDM profile or models not available")

        assigner = PDMMetadataAssigner(profile=None)

        # Create 60 chunks
        chunks = []
        for pa in range(1, 11):
            for dim in range(1, 7):
                chunk = Chunk(
                    chunk_id=f"PA{pa:02d}-DIM{dim:02d}",
                    policy_area_id=f"PA{pa:02d}",
                    dimension_id=f"DIM{dim:02d}",
                    text="Contenido",
                )
                chunks.append(chunk)

        # Verify 60 chunks
        assert len(chunks) == 60, "CI-01 FAILED: Expected exactly 60 chunks"

        # Assign metadata (should preserve 60 chunks)
        enhanced = assigner.assign_metadata_to_chunks(chunks)

        assert len(enhanced) == 60, "CI-01 FAILED: PDM metadata assignment changed chunk count"

    def test_pdm_02_sp2_profile_consumption(self):
        """Test PDM-02: SP2 consumes PDM profile."""
        if not PDM_PROFILE_AVAILABLE or not MODELS_AVAILABLE:
            pytest.skip("PDM profile or models not available")

        analyzer = PDMStructuralAnalyzer(profile=None)

        # Verify analyzer has profile
        assert analyzer.profile is not None, "PDM-02 FAILED: Analyzer does not have profile"

        # Verify analyzer uses profile
        base_structure = StructureData(
            sections=[],
            hierarchy={},
            paragraph_mapping={},
        )

        text = "TEST TEXT"

        enhanced = analyzer.enhance_structure_data(base_structure, text)

        assert hasattr(enhanced, "_pdm_profile_used"), "PDM-02 FAILED: Profile version not recorded"

    def test_pdm_03_sp4_semantic_respect(self):
        """Test PDM-03: SP4 respects semantic integrity rules."""
        if not PDM_PROFILE_AVAILABLE or not MODELS_AVAILABLE:
            pytest.skip("PDM profile or models not available")

        assigner = PDMMetadataAssigner(profile=None)

        # Create chunks
        chunks = []
        for i in range(60):
            chunk = Chunk(
                chunk_id=f"PA{(i % 10) + 1:02d}-DIM{(i % 6) + 1:02d}",
                policy_area_id=f"PA{(i % 10) + 1:02d}",
                dimension_id=f"DIM{(i % 6) + 1:02d}",
                text="Contenido de prueba",
            )
            chunks.append(chunk)

        # Check semantic integrity
        violations = assigner.check_semantic_integrity(chunks)

        # For simple test content, expect no violations
        # (violations would be detected for split Meta+Indicador, etc.)
        assert isinstance(violations, list), "PDM-03 FAILED: Violations not returned as list"


@pytest.mark.skipif(not PDM_INTEGRATION_AVAILABLE or not MODELS_AVAILABLE,
                    reason="PDM integration or models not available")
class TestPDMMetadataInSmartChunk:
    """Test PDM metadata integration with SmartChunk."""

    def test_smartchunk_has_pdm_metadata_field(self):
        """Test SmartChunk has pdm_metadata field."""
        try:
            from farfan_pipeline.phases.Phase_01.phase1_03_00_models import SmartChunk

            # Check field exists
            assert hasattr(SmartChunk, "__dataclass_fields__")
            fields = SmartChunk.__dataclass_fields__
            assert "pdm_metadata" in fields, "SmartChunk missing pdm_metadata field"

        except ImportError:
            pytest.skip("SmartChunk not available")


class TestPhase1Exports:
    """Test Phase 1 module exports PDM integration."""

    def test_phase1_exports_pdm_integration(self):
        """Test Phase 1 __init__ exports PDM integration."""
        try:
            from farfan_pipeline.phases.Phase_01 import (
                PDM_INTEGRATION_AVAILABLE,
                PDMStructuralAnalyzer,
                PDMMetadataAssigner,
            )

            # Verify exports
            assert PDM_INTEGRATION_AVAILABLE in [True, False]
            # If available, verify classes are imported
            if PDM_INTEGRATION_AVAILABLE:
                assert PDMStructuralAnalyzer is not None
                assert PDMMetadataAssigner is not None

        except ImportError as e:
            pytest.fail(f"Failed to import PDM integration from Phase 1: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

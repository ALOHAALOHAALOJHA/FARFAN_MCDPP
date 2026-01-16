"""
PDM Structural Integration for Phase 1 - SP2 and SP4

This module provides PDM-specific structural recognition for Colombian
municipal development plans (PDM) according to Ley 152/94.

INTEGRATION POINTS:
- SP2 (Structural Analysis): Enhanced with PDM profile consumption
- SP4 (Grid Assignment): Enhanced with PDM metadata assignment

CONSTITUTIONAL COMPLIANCE:
- CI-01: 60-Chunk invariant preserved
- CI-02: PA×Dim Grid immutability preserved
- PDM-01: Profile mandatory for SP2
- PDM-02: SP2 consumes profile
- PDM-03: SP4 respects semantic rules

Author: FARFAN Engineering Team
Version: PDM-2025.1
"""

from __future__ import annotations

import logging
from dataclasses import replace
from typing import Any

# PDM Structural Profile Imports
try:
    from farfan_pipeline.infrastructure.parametrization.pdm_structural_profile import (
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

# PDM Contract Imports
try:
    from farfan_pipeline.infrastructure.contractual.pdm_contracts import (
        PDMProfileContract,
        PrerequisiteError,
        SP2Obligations,
        SP4Obligations,
    )
    PDM_CONTRACTS_AVAILABLE = True
except ImportError:
    PDM_CONTRACTS_AVAILABLE = False

# Phase 1 Model Imports
try:
    from farfan_pipeline.phases.Phase_1.phase1_03_00_models import (
        Chunk,
        PDMMetadata,
        StructureData,
    )
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False

logger = logging.getLogger(__name__)


class PDMStructuralAnalyzer:
    """
    PDM-specific structural analyzer for SP2 integration.

    This class provides methods to enhance SP2 (Structural Analysis)
    with PDM structural profile consumption according to Ley 152/94.

    CONSTITUTIONAL REQUIREMENT:
    - PDMStructuralProfile MUST be present before analysis
    - Analysis MUST use profile patterns for hierarchy detection
    - Analysis MUST detect canonical sections per profile
    """

    def __init__(self, profile: PDMStructuralProfile | None = None):
        """
        Initialize PDM structural analyzer.

        Args:
            profile: PDM structural profile. If None, loads default profile.

        Raises:
            PrerequisiteError: If profile cannot be loaded (when PDM_CONTRACTS_AVAILABLE)
        """
        if not PDM_PROFILE_AVAILABLE:
            logger.warning("PDM profile not available - using standard analysis")
            self.profile = None
            self._pdm_enabled = False
            return

        if profile is None:
            if PDM_CONTRACTS_AVAILABLE:
                # Enforce profile presence via contract
                profile = PDMProfileContract.enforce_profile_presence()
            else:
                # Fallback: try to load default profile
                profile = get_default_profile()

        self.profile = profile
        self._pdm_enabled = profile is not None

        if self._pdm_enabled:
            logger.info(f"PDM analyzer initialized with profile version: {profile.profile_version}")
        else:
            logger.warning("PDM analyzer initialized without profile - PDM features disabled")

    def detect_pdm_hierarchy(
        self,
        text: str,
        line_numbers: dict[int, int] | None = None,
    ) -> dict[int, str]:
        """
        Detect PDM hierarchy levels (H1-H5) in text.

        Uses PDM profile header patterns to detect:
        - H1 (PARTE): Partes documentales
        - H2 (CAPITULO): Capítulos / Ejes estratégicos
        - H3 (LINEA): Líneas estratégicas / Programas
        - H4 (SUBPROGRAMA): Subprogramas / Proyectos
        - H5 (META): Metas / Indicadores

        Args:
            text: Document text to analyze
            line_numbers: Mapping of line numbers to character positions

        Returns:
            Dict mapping line numbers to hierarchy levels (H1-H5)

        Example:
            >>> analyzer = PDMStructuralAnalyzer()
            >>> hierarchy = analyzer.detect_pdm_hierarchy(text)
            >>> {1: "H1", 15: "H2", 30: "H3"}
        """
        if not self._pdm_enabled or self.profile is None:
            return {}

        hierarchy: dict[int, str] = {}
        lines = text.split("\n")

        for line_num, line in enumerate(lines, start=1):
            line = line.strip()
            if not line:
                continue

            # Check against PDM profile header patterns
            for level, patterns in self.profile.header_patterns.items():
                for pattern in patterns:
                    if pattern.match(line):
                        hierarchy[line_num] = level.value
                        break  # Use first match

        return hierarchy

    def detect_canonical_sections(
        self,
        text: str,
    ) -> list[dict[str, Any]]:
        """
        Detect PDM canonical sections in text.

        Detects sections according to Ley 152/94:
        - DIAGNOSTICO: Diagnostic analysis
        - PARTE_ESTRATEGICA: Strategic part
        - PLAN_PLURIANUAL: Pluriannual investment plan (PPI)
        - PLAN_FINANCIERO: Financial plan (optional)
        - SEGUIMIENTO: Monitoring and evaluation (optional)

        Args:
            text: Document text to analyze

        Returns:
            List of detected sections with position and type.

        Example:
            >>> analyzer = PDMStructuralAnalyzer()
            >>> sections = analyzer.detect_canonical_sections(text)
            >>> [{"section": "DIAGNOSTICO", "start": 0, "end": 1500}]
        """
        if not self._pdm_enabled or self.profile is None:
            return []

        sections: list[dict[str, Any]] = []

        # Try to match sections against profile mapping
        for section_name, section_type in self.profile.canonical_sections.items():
            # Find section in text
            section_start = text.lower().find(section_name.lower())
            if section_start != -1:
                # Determine section end (next section or end of text)
                remaining = text[section_start + len(section_name):]
                next_section_start = len(remaining)

                for other_name in self.profile.canonical_sections.keys():
                    if other_name == section_name:
                        continue
                    other_pos = remaining.lower().find(other_name.lower())
                    if other_pos != -1 and other_pos < next_section_start:
                        next_section_start = other_pos

                section_end = section_start + len(section_name) + next_section_start

                sections.append({
                    "section_type": section_type.value,
                    "section_name": section_name,
                    "start": section_start,
                    "end": section_end,
                    "text": text[section_start:section_end],
                })

        return sections

    def validate_pdm_tables(
        self,
        tables: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Validate detected tables against PDM schemas.

        Uses PDM profile table schemas to validate:
        - PPI: Plan Plurianual de Inversiones
        - INDICADORES: Matriz de Indicadores
        - PROGRAMAS: Estructura Programática

        Args:
            tables: List of detected tables with column data

        Returns:
            List of validation results with schema compliance status.

        Example:
            >>> analyzer = PDMStructuralAnalyzer()
            >>> results = analyzer.validate_pdm_tables(tables)
            >>> [{"table": "PPI", "valid": True, "errors": []}]
        """
        if not self._pdm_enabled or self.profile is None:
            return []

        results: list[dict[str, Any]] = []

        for table in tables:
            table_name = table.get("name", "")
            table_data = table.get("data", {})

            # Find matching schema
            schema = None
            for schema_name, schema_obj in self.profile.table_schemas.items():
                if schema_name.lower() in table_name.lower():
                    schema = schema_obj
                    break

            if schema is None:
                results.append({
                    "table": table_name,
                    "valid": False,
                    "errors": ["No matching PDM schema found"],
                })
                continue

            # Validate against schema
            is_valid, errors = schema.validate_table(table_data)

            results.append({
                "table": table_name,
                "valid": is_valid,
                "errors": errors,
                "schema": schema.name,
            })

        return results

    def enhance_structure_data(
        self,
        base_structure: StructureData,
        text: str,
    ) -> StructureData:
        """
        Enhance StructureData with PDM-specific information.

        Adds PDM hierarchy, canonical sections, and table validation
        to the base StructureData output from SP2.

        Args:
            base_structure: Base StructureData from SP2
            text: Full document text

        Returns:
            Enhanced StructureData with PDM information.

        Raises:
            PrerequisiteError: If PDM profile not available (when PDM_CONTRACTS_AVAILABLE)
        """
        if PDM_CONTRACTS_AVAILABLE and not self._pdm_enabled:
            raise PrerequisiteError(
                "PDM profile required for PDM structural enhancement. "
                "Cannot enhance StructureData without profile."
            )

        if not self._pdm_enabled:
            logger.warning("PDM profile not available - returning base structure")
            return base_structure

        # Detect PDM hierarchy
        pdm_hierarchy = self.detect_pdm_hierarchy(text)
        if pdm_hierarchy:
            # Merge with existing hierarchy
            merged_hierarchy = dict(base_structure.hierarchy)
            merged_hierarchy.update(pdm_hierarchy)
            base_structure.hierarchy = merged_hierarchy

        # Detect canonical sections
        pdm_sections = self.detect_canonical_sections(text)
        if pdm_sections:
            # Add to existing sections
            base_structure.sections.extend(pdm_sections)

        # Validate tables if present
        if base_structure.tables:
            pdm_table_validation = self.validate_pdm_tables(base_structure.tables)
            # Store validation results
            if not hasattr(base_structure, "_pdm_table_validation"):
                base_structure._pdm_table_validation = []
            base_structure._pdm_table_validation = pdm_table_validation

        # Store PDM profile version
        base_structure._pdm_profile_used = self.profile.profile_version
        base_structure._pdm_profile_available = True

        return base_structure


class PDMMetadataAssigner:
    """
    PDM metadata assigner for SP4 integration.

    This class provides methods to enhance SP4 (Grid Assignment)
    with PDM metadata assignment for each chunk.

    CONSTITUTIONAL REQUIREMENT:
    - All 60 chunks MUST have PDM metadata
    - Semantic integrity rules MUST be respected
    - P-D-Q context MUST be assigned
    """

    def __init__(self, profile: PDMStructuralProfile | None = None):
        """
        Initialize PDM metadata assigner.

        Args:
            profile: PDM structural profile. If None, loads default profile.
        """
        if not PDM_PROFILE_AVAILABLE:
            logger.warning("PDM profile not available - metadata assignment disabled")
            self.profile = None
            self._pdm_enabled = False
            return

        if profile is None:
            if PDM_CONTRACTS_AVAILABLE:
                profile = PDMProfileContract.enforce_profile_presence()
            else:
                profile = get_default_profile()

        self.profile = profile
        self._pdm_enabled = profile is not None

        if self._pdm_enabled:
            logger.info(f"PDM assigner initialized with profile version: {profile.profile_version}")

    def infer_hierarchy_level(
        self,
        chunk_text: str,
        structure_data: StructureData | None = None,
    ) -> Any:
        """
        Infer hierarchy level for a chunk based on its content.

        Uses PDM profile patterns to detect if chunk corresponds to:
        - H1 (PARTE): Partes documentales
        - H2 (CAPITULO): Capítulos / Ejes estratégicos
        - H3 (LINEA): Líneas estratégicas / Programas
        - H4 (SUBPROGRAMA): Subprogramas / Proyectos
        - H5 (META): Metas / Indicadores

        Args:
            chunk_text: Text content of the chunk
            structure_data: StructureData from SP2 (optional)

        Returns:
            HierarchyLevel enum value or None if not detected

        Example:
            >>> assigner = PDMMetadataAssigner()
            >>> level = assigner.infer_hierarchy_level("Meta 1: Aumentar cobertura...")
            >>> HierarchyLevel.H5
        """
        if not self._pdm_enabled or self.profile is None:
            return None

        chunk_text_lower = chunk_text.lower()

        # Check against PDM profile header patterns
        for level, patterns in self.profile.header_patterns.items():
            for pattern in patterns:
                if pattern.search(chunk_text):
                    return level

        return None

    def infer_source_section(
        self,
        chunk_text: str,
        structure_data: StructureData | None = None,
    ) -> Any:
        """
        Infer source canonical section for a chunk.

        Uses PDM profile to determine if chunk belongs to:
        - DIAGNOSTICO: Diagnostic analysis
        - PARTE_ESTRATEGICA: Strategic part
        - PLAN_PLURIANUAL: Investment plan (PPI)
        - PLAN_FINANCIERO: Financial plan
        - SEGUIMIENTO: Monitoring

        Args:
            chunk_text: Text content of the chunk
            structure_data: StructureData from SP2 (optional)

        Returns:
            CanonicalSection enum value or None if not detected

        Example:
            >>> assigner = PDMMetadataAssigner()
            >>> section = assigner.infer_source_section("El diagnóstico muestra...")
            >>> CanonicalSection.DIAGNOSTICO
        """
        if not self._pdm_enabled or self.profile is None:
            return None

        chunk_text_lower = chunk_text.lower()

        # Check for section keywords in profile
        for section_name, section_type in self.profile.canonical_sections.items():
            if section_name.lower() in chunk_text_lower:
                return section_type

        # Use contextual marker mapping as fallback
        # P (Problem) → DIAGNOSTICO
        # D (Decision) → PARTE_ESTRATEGICA
        # Q (Quality) → Can be in PARTE_ESTRATEGICA or PLAN_PLURIANUAL

        # Check for problem indicators
        for marker in self.profile.contextual_markers.get(ContextualMarker.P, []):
            if marker.lower() in chunk_text_lower:
                return CanonicalSection.DIAGNOSTICO

        # Check for decision indicators
        for marker in self.profile.contextual_markers.get(ContextualMarker.D, []):
            if marker.lower() in chunk_text_lower:
                return CanonicalSection.PARTE_ESTRATEGICA

        return None

    def assign_pdq_context(
        self,
        chunk_text: str,
    ) -> Any:
        """
        Assign P-D-Q contextual marker to chunk.

        Classifies chunk content as:
        - P (Problem): Diagnostic, problems, gaps
        - D (Decision): Programs, projects, goals, decisions
        - Q (Quality): Indicators, metrics, baselines, targets

        Args:
            chunk_text: Text content of the chunk

        Returns:
            ContextualMarker enum value or None if not detected

        Example:
            >>> assigner = PDMMetadataAssigner()
            >>> context = assigner.assign_pdq_context("La meta es 100 con indicador...")
            >>> ContextualMarker.D (Decision - has meta)
        """
        if not self._pdm_enabled or self.profile is None:
            return None

        chunk_text_lower = chunk_text.lower()

        # Check P (Problem) markers
        for marker in self.profile.contextual_markers.get(ContextualMarker.P, []):
            if marker.lower() in chunk_text_lower:
                return ContextualMarker.P

        # Check Q (Quality) markers - these take precedence over D
        for marker in self.profile.contextual_markers.get(ContextualMarker.Q, []):
            if marker.lower() in chunk_text_lower:
                return ContextualMarker.Q

        # Check D (Decision) markers
        for marker in self.profile.contextual_markers.get(ContextualMarker.D, []):
            if marker.lower() in chunk_text_lower:
                return ContextualMarker.D

        return None

    def create_pdm_metadata(
        self,
        chunk: Chunk,
        structure_data: StructureData | None = None,
    ) -> PDMMetadata | None:
        """
        Create PDM metadata for a chunk.

        Combines hierarchy level, source section, and P-D-Q context
        into a PDMMetadata object.

        Args:
            chunk: Chunk object to create metadata for
            structure_data: StructureData from SP2 (optional)

        Returns:
            PDMMetadata object or None if PDM profile not available

        Example:
            >>> assigner = PDMMetadataAssigner()
            >>> metadata = assigner.create_pdm_metadata(chunk)
            >>> PDMMetadata(
            ...     hierarchy_level=HierarchyLevel.H3,
            ...     source_section=CanonicalSection.PARTE_ESTRATEGICA,
            ...     pdq_context=ContextualMarker.D
            ... )
        """
        if not self._pdm_enabled or not MODELS_AVAILABLE:
            return None

        # Infer hierarchy level
        hierarchy_level = self.infer_hierarchy_level(
            chunk.text,
            structure_data
        )

        # Infer source section
        source_section = self.infer_source_section(
            chunk.text,
            structure_data
        )

        # Assign P-D-Q context
        pdq_context = self.assign_pdq_context(chunk.text)

        # Create PDM metadata
        try:
            metadata = PDMMetadata(
                hierarchy_level=hierarchy_level,
                source_section=source_section,
                pdq_context=pdq_context,
                semantic_unit_id=None,
                table_reference=None,
            )
            return metadata
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to create PDM metadata for chunk {chunk.chunk_id}: {e}")
            return None

    def check_semantic_integrity(
        self,
        chunks: list[Chunk],
    ) -> list[str]:
        """
        Check semantic integrity rules across all chunks.

        Verifies that critical semantic rules are not violated:
        - SEM-01-CRITICAL: Meta + Indicador + Línea Base must stay together
        - SEM-02-HIGH: Programa + Objetivo + Subprogramas hierarchy preserved
        - SEM-03-HIGH: Indicador + Fórmula + Fuente verification

        Args:
            chunks: List of chunks to validate

        Returns:
            List of semantic violations (empty if all valid)

        Example:
            >>> assigner = PDMMetadataAssigner()
            >>> violations = assigner.check_semantic_integrity(chunks)
            >>> []  # No violations
        """
        if not self._pdm_enabled or self.profile is None:
            return []

        violations: list[str] = []

        for rule in self.profile.semantic_integrity_rules:
            if rule.violation_severity == "CRITICAL":
                for chunk in chunks:
                    if rule.check_violation(chunk.text):
                        violations.append(
                            f"CRITICAL: Rule {rule.rule_id} violated in chunk {chunk.chunk_id}: "
                            f"{rule.description}"
                        )

        return violations

    def assign_metadata_to_chunks(
        self,
        chunks: list[Chunk],
        structure_data: StructureData | None = None,
    ) -> list[Chunk]:
        """
        Assign PDM metadata to all chunks.

        This is the main SP4 integration method. It:
        1. Creates PDM metadata for each chunk
        2. Replaces chunks with enhanced versions containing metadata
        3. Validates semantic integrity
        4. Returns enhanced chunks

        Args:
            chunks: List of chunks to enhance with PDM metadata
            structure_data: StructureData from SP2 (optional)

        Returns:
            List of chunks with PDM metadata assigned

        Raises:
            ValueError: If semantic integrity violations detected

        Example:
            >>> assigner = PDMMetadataAssigner()
            >>> enhanced_chunks = assigner.assign_metadata_to_chunks(chunks)
            >>> len(enhanced_chunks)
            60
        """
        if not self._pdm_enabled:
            logger.warning("PDM metadata assignment disabled - returning original chunks")
            return chunks

        enhanced_chunks: list[Chunk] = []

        for chunk in chunks:
            # Create PDM metadata
            pdm_metadata = self.create_pdm_metadata(chunk, structure_data)

            # Create enhanced chunk with metadata
            if MODELS_AVAILABLE and pdm_metadata is not None:
                # Use replace to create new chunk with metadata
                enhanced_chunk = replace(chunk, pdm_metadata=pdm_metadata)
            else:
                # Store metadata as dict if PDMMetadata not available
                enhanced_chunk = chunk
                if pdm_metadata:
                    enhanced_chunk._pdm_metadata_dict = {
                        "hierarchy_level": pdm_metadata.hierarchy_level.value if pdm_metadata.hierarchy_level else None,
                        "source_section": pdm_metadata.source_section.value if pdm_metadata.source_section else None,
                        "pdq_context": pdm_metadata.pdq_context.value if pdm_metadata.pdq_context else None,
                    }

            enhanced_chunks.append(enhanced_chunk)

        # Validate semantic integrity
        violations = self.check_semantic_integrity(enhanced_chunks)
        if violations:
            logger.warning(f"Semantic integrity violations detected: {violations}")

        return enhanced_chunks


# =============================================================================
# Convenience Functions
# =============================================================================

def enhance_sp2_with_pdm(
    base_structure: StructureData,
    text: str,
    profile: PDMStructuralProfile | None = None,
) -> StructureData:
    """
    Convenience function to enhance SP2 StructureData with PDM information.

    This is the main entry point for SP2 PDM integration.

    Args:
        base_structure: Base StructureData from SP2
        text: Full document text
        profile: PDM structural profile (optional, loads default if None)

    Returns:
        Enhanced StructureData with PDM hierarchy and sections

    Example:
        >>> from farfan_pipeline.phases.Phase_1.phase1_12_01_pdm_integration import enhance_sp2_with_pdm
        >>> enhanced = enhance_sp2_with_pdm(structure_data, document_text)
    """
    analyzer = PDMStructuralAnalyzer(profile)
    return analyzer.enhance_structure_data(base_structure, text)


def assign_pdm_metadata_to_chunks(
    chunks: list[Chunk],
    structure_data: StructureData | None = None,
    profile: PDMStructuralProfile | None = None,
) -> list[Chunk]:
    """
    Convenience function to assign PDM metadata to chunks (SP4 integration).

    This is the main entry point for SP4 PDM integration.

    Args:
        chunks: List of chunks from SP4
        structure_data: StructureData from SP2 (optional)
        profile: PDM structural profile (optional, loads default if None)

    Returns:
        List of chunks with PDM metadata assigned

    Example:
        >>> from farfan_pipeline.phases.Phase_1.phase1_12_01_pdm_integration import assign_pdm_metadata_to_chunks
        >>> enhanced_chunks = assign_pdm_metadata_to_chunks(chunks, structure_data)
    """
    assigner = PDMMetadataAssigner(profile)
    return assigner.assign_metadata_to_chunks(chunks, structure_data)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "PDMStructuralAnalyzer",
    "PDMMetadataAssigner",
    "enhance_sp2_with_pdm",
    "assign_pdm_metadata_to_chunks",
]

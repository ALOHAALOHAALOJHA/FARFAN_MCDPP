"""
Structural normalization with policy-awareness.

Segments documents into policy-aware units.

EPISTEMOLOGICAL LEVEL: N1-EMP (Empirical)
OUTPUT TYPE: FACT
FUSION BEHAVIOR: additive
"""

# =============================================================================
# METADATA
# =============================================================================

__version__ = "2.0.0"
__phase__ = 1
__stage__ = 70
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-14"
__criticality__ = "MEDIUM"
__execution_pattern__ = "On-Demand"
__epistemic_level__ = "N1-EMP"
__output_type__ = "FACT"
__fusion_behavior__ = "additive"

from typing import Any

# =============================================================================
# CALIBRATION IMPORTS - FIXED: Use unified calibration module
# =============================================================================
try:
    from farfan_pipeline.calibration.uoa_sensitive import (
        fact_aware,
        is_uoa_sensitive,
        get_epistemic_level,
    )
    from farfan_pipeline.calibration.runtime_context import (
        get_calibration_context,
    )
    _CALIBRATION_AVAILABLE = True
except ImportError:
    _CALIBRATION_AVAILABLE = False
    
    # Stub decorators for environments without calibration
    def fact_aware(func):  # type: ignore[misc]
        """No-op decorator when calibration not available."""
        return func
    
    def is_uoa_sensitive(func) -> bool:  # type: ignore[misc]
        """Return False when calibration not available."""
        return False
    
    def get_epistemic_level(func) -> str | None:  # type: ignore[misc]
        """Return None when calibration not available."""
        return None
    
    def get_calibration_context():  # type: ignore[misc]
        """Return None when calibration not available."""
        return None


class StructuralNormalizer:
    """
    Policy-aware structural normalizer.
    
    EPISTEMOLOGICAL CLASSIFICATION:
    - Level: N1-EMP (Base Empírica)
    - Output Type: FACT
    - Fusion Behavior: additive (⊕)
    - Epistemology: Empirismo positivista
    
    All methods extract literal facts from documents without
    interpretive transformation.
    """

    @fact_aware
    def normalize(
        self,
        raw_objects: dict[str, Any],
        chunk_size: int = 512,
        extraction_coverage_target: float = 0.95,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Normalize document structure with policy awareness.
        
        EPISTEMOLOGICAL NOTE:
        This method produces FACT outputs (N1-EMP level).
        Parameters chunk_size and extraction_coverage_target are
        auto-calibrated based on UoA complexity when executed
        within calibration_context().

        Args:
            raw_objects: Raw parsed objects from document
            chunk_size: Auto-calibrated chunk size (chars). Calibrated based on
                       UoA complexity: Medellín → ~2048, small town → ~512
            extraction_coverage_target: Auto-calibrated coverage target (0.0-1.0).
                                       Higher for complex UoAs.
            **kwargs: Additional calibration parameters (passed through)

        Returns:
            Policy graph with structured sections (FACT output)
            
        Note:
            When called within `with calibration_context(ctx):`, the
            chunk_size and extraction_coverage_target parameters are
            automatically injected from the calibration context.
        """
        policy_graph: dict[str, Any] = {
            "sections": [],
            "policy_units": [],
            "axes": [],
            "programs": [],
            "projects": [],
            "years": [],
            "territories": [],
            "_epistemic_metadata": {
                "level": "N1-EMP",
                "output_type": "FACT",
                "fusion_behavior": "additive",
                "calibration_applied": _CALIBRATION_AVAILABLE,
                "chunk_size_used": chunk_size,
                "coverage_target_used": extraction_coverage_target,
            },
        }

        # Extract sections from pages
        pages = raw_objects.get("pages", [])
        for page in pages:
            text = page.get("text", "")

            # Detect policy units (N1 - no interpretation)
            policy_units = self._detect_policy_units(text, chunk_size=chunk_size)
            policy_graph["policy_units"].extend(policy_units)

            # Create section
            section = {
                "text": text,
                "page": page.get("page_num"),
                "title": self._extract_title(text, chunk_size=chunk_size),
                "area": None,
                "eje": None,
            }
            policy_graph["sections"].append(section)

        # Extract axes, programs, projects from detected units
        for unit in policy_graph["policy_units"]:
            unit_type = unit.get("type", "")
            unit_name = unit.get("name", "")
            
            if unit_type == "eje":
                policy_graph["axes"].append(unit_name)
            elif unit_type == "programa":
                policy_graph["programs"].append(unit_name)
            elif unit_type == "proyecto":
                policy_graph["projects"].append(unit_name)

        return policy_graph

    @fact_aware
    def _detect_policy_units(
        self,
        text: str,
        chunk_size: int = 512,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Detect policy units in text.
        
        EPISTEMOLOGICAL NOTE:
        Produces FACT outputs - literal detection without interpretation.
        Uses keyword-based detection (N1 - no probabilistic inference).
        
        Args:
            text: Text to analyze for policy units
            chunk_size: Chunk size for processing (auto-calibrated)
            **kwargs: Additional calibration parameters
        
        Returns:
            List of detected policy units with type and name.
            Each unit is a FACT (N1 output) that can be verified
            in the source document.
        """
        units: list[dict[str, Any]] = []

        # Simple keyword-based detection (N1 - no interpretation)
        # These are LITERAL matches, not probabilistic inference
        keywords: dict[str, list[str]] = {
            "eje": ["eje", "pilar", "eje estratégico", "pilar estratégico"],
            "programa": ["programa", "programa estratégico"],
            "proyecto": ["proyecto", "proyecto de inversión"],
            "meta": ["meta", "meta de producto", "meta de resultado"],
            "indicador": ["indicador", "indicador de gestión"],
        }

        text_lower = text.lower()
        
        for unit_type, keywords_list in keywords.items():
            for keyword in keywords_list:
                if keyword in text_lower:
                    units.append({
                        "type": unit_type,
                        "name": f"{keyword.capitalize()} detected",
                        "keyword_matched": keyword,
                        "_epistemic_level": "N1-EMP",
                        "_output_type": "FACT",
                    })

        return units

    @fact_aware
    def _extract_title(
        self,
        text: str,
        chunk_size: int = 512,
        **kwargs: Any,
    ) -> str:
        """
        Extract title from text.
        
        EPISTEMOLOGICAL NOTE:
        Produces FACT output - literal extraction of first line.
        No interpretation or inference applied.
        
        Args:
            text: Text to extract title from
            chunk_size: Chunk size for processing (auto-calibrated)
            **kwargs: Additional calibration parameters
        
        Returns:
            Extracted title string (FACT output).
            This is the literal first line of text, truncated to 100 chars.
        """
        lines = text.split("\n")
        if lines:
            # Return first non-empty line, truncated
            for line in lines:
                stripped = line.strip()
                if stripped:
                    return stripped[:100]
        return ""

    @fact_aware
    def _extract_temporal_markers(
        self,
        text: str,
        chunk_size: int = 512,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Extract temporal markers (years, date ranges) from text.
        
        EPISTEMOLOGICAL NOTE:
        Produces FACT outputs - literal extraction of temporal references.
        
        Args:
            text: Text to analyze
            chunk_size: Chunk size (auto-calibrated)
            **kwargs: Additional parameters
        
        Returns:
            List of temporal markers as FACT outputs
        """
        import re
        
        markers: list[dict[str, Any]] = []
        
        # Year patterns (literal extraction, not inference)
        year_pattern = re.compile(r'\b(20[0-3][0-9])\b')
        for match in year_pattern.finditer(text):
            markers.append({
                "type": "year",
                "value": match.group(1),
                "position": match.start(),
                "_epistemic_level": "N1-EMP",
            })
        
        # Date range patterns
        range_pattern = re.compile(r'\b(20[0-3][0-9])\s*[-–]\s*(20[0-3][0-9])\b')
        for match in range_pattern.finditer(text):
            markers.append({
                "type": "year_range",
                "start_year": match.group(1),
                "end_year": match.group(2),
                "position": match.start(),
                "_epistemic_level": "N1-EMP",
            })
        
        return markers


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "StructuralNormalizer",
]

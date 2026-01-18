"""
Colombian PDM-Specific Chunk Enhancement Module
================================================

Purpose: Enhance semantic chunking with Colombian Municipal Development Plan (PDM)
         specific patterns, terminology, and structural markers.

This module provides domain-specific enhancements for Phase 1 SP4 chunking
to ensure chunks are:
- SMART: Contain relevant PDM-specific context
- COMPREHENSIVE: Cover all standard PDM sections
- DETAILED: Include fine-grained territorial and policy markers

Author: F.A.R.F.A.N Core Team
Version: 1.0.0
Date: 2026-01-18
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 1
__stage__ = 7
__order__ = 1
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-18"
__modified__ = "2026-01-18"
__criticality__ = "MEDIUM"
__execution_pattern__ = "On-Demand"

import logging
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# COLOMBIAN PDM STRUCTURAL MARKERS
# =============================================================================

@dataclass(frozen=True)
class ColombianPDMPatterns:
    """
    Colombian Municipal Development Plan (PDM) specific patterns.
    
    Based on:
    - Ley 152 de 1994 (Organic Planning Law)
    - DNP Guidelines for Territorial Planning
    - CONPES Social policies integration
    - Standard PDM structure used across Colombian municipalities
    """
    
    # Regulatory framework references
    regulatory_markers: tuple[str, ...] = (
        r"Ley\s+152\s+de\s+1994",  # Planning law
        r"Ley\s+1098\s+de\s+2006",  # Children's code
        r"Constitución\s+Política",
        r"CONPES\s+\d+",  # Policy documents
        r"DNP",  # National Planning Department
        r"POT|PBOT|EOT",  # Territorial ordering plans
        r"Acuerdo\s+de\s+Paz",  # Peace agreement
        r"Ley\s+1448",  # Victims law
    )
    
    # Standard PDM section markers
    section_markers: tuple[str, ...] = (
        r"(?i)diagnóstico\s+territorial",
        r"(?i)visión\s+y\s+objetivos",
        r"(?i)ejes?\s+estratégicos?",
        r"(?i)programas?\s+y\s+subprogramas?",
        r"(?i)plan\s+plurianual\s+de\s+inversiones?",
        r"(?i)plan\s+de\s+inversión",
        r"(?i)indicadores?\s+y\s+metas?",
        r"(?i)sistema\s+de\s+seguimiento",
        r"(?i)marco\s+fiscal\s+de\s+mediano\s+plazo",
        r"(?i)participación\s+ciudadana",
    )
    
    # Colombian territorial indicators
    territorial_indicators: tuple[str, ...] = (
        r"NBI",  # Unsatisfied Basic Needs
        r"SISBEN",  # Socioeconomic classification
        r"(?i)cobertura\s+\w+",  # Coverage indicators
        r"(?i)tasa\s+de\s+\w+",  # Rate indicators
        r"DANE",  # National statistics
        r"(?i)código\s+DANE",
        r"(?i)categoría\s+[1-6]",  # Municipal category
        r"IPM",  # Multidimensional poverty index
    )
    
    # Budget and financial markers
    financial_markers: tuple[str, ...] = (
        r"(?i)presupuesto\s+(?:de\s+)?inversión",
        r"(?i)fuentes?\s+de\s+financiación",
        r"(?i)recursos?\s+(?:propios?|transferidos?)",
        r"(?i)sistema\s+general\s+de\s+participaciones",
        r"SGP",  # General participation system
        r"(?i)regalías",
        r"(?i)cofinanciación",
        r"(?i)recursos?\s+del\s+crédito",
    )
    
    # Differential approach markers (enfoque diferencial)
    differential_approach_markers: tuple[str, ...] = (
        r"(?i)enfoque\s+diferencial",
        r"(?i)pueblos?\s+indígenas?",
        r"(?i)comunidades?\s+afrodescendientes?",
        r"(?i)población\s+LGBTI",
        r"(?i)personas?\s+con\s+discapacidad",
        r"(?i)adultos?\s+mayores?",
        r"(?i)primera\s+infancia",
        r"(?i)perspectiva\s+de\s+género",
        r"(?i)víctimas?\s+del\s+conflicto",
    )
    
    # PDM-specific quantitative markers
    quantitative_markers: tuple[str, ...] = (
        r"\d+(?:\.\d+)?\s*%",  # Percentages
        r"(?i)\d+\s+(?:millones?|miles?|billones?)",
        r"(?i)\d+\s+(?:hectáreas?|metros?|kilómetros?)",
        r"(?i)\d+\s+(?:viviendas?|familias?|hogares?)",
        r"(?i)\d+\s+(?:personas?|habitantes?|beneficiarios?)",
        r"(?i)meta:?\s*\d+",
        r"(?i)línea\s+base:?\s*\d+",
    )
    
    # Strategic planning markers
    strategic_markers: tuple[str, ...] = (
        r"(?i)objetivos?\s+(?:estratégicos?|específicos?)",
        r"(?i)metas?\s+(?:del\s+)?cuatrienio",
        r"(?i)indicadores?\s+de\s+(?:producto|resultado|impacto)",
        r"(?i)teoría\s+del?\s+cambio",
        r"(?i)cadena\s+de\s+valor",
        r"(?i)marco\s+lógico",
        r"(?i)articulación\s+con",
    )


@dataclass
class PDMChunkEnhancement:
    """Enhancement metadata for a chunk with Colombian PDM-specific information."""
    
    has_regulatory_reference: bool = False
    regulatory_refs_count: int = 0
    
    has_section_marker: bool = False
    detected_sections: list[str] = field(default_factory=list)
    
    has_territorial_indicator: bool = False
    indicator_types: list[str] = field(default_factory=list)
    
    has_financial_info: bool = False
    financial_types: list[str] = field(default_factory=list)
    
    has_differential_approach: bool = False
    population_groups: list[str] = field(default_factory=list)
    
    quantitative_density: float = 0.0  # Ratio of quantitative markers to text length
    
    has_strategic_elements: bool = False
    strategic_elements: list[str] = field(default_factory=list)
    
    pdm_specificity_score: float = 0.0  # Overall score 0-1 indicating PDM relevance
    
    colombian_context_markers: dict[str, int] = field(default_factory=dict)


class ColombianPDMChunkEnhancer:
    """
    Enhancer that analyzes chunk content for Colombian PDM-specific patterns.
    
    This enhancer:
    1. Identifies standard PDM structural elements
    2. Detects Colombian regulatory framework references
    3. Recognizes territorial and socioeconomic indicators
    4. Flags differential approach content
    5. Quantifies PDM specificity for better chunk quality
    """
    
    def __init__(self):
        """Initialize enhancer with Colombian PDM patterns."""
        self.patterns = ColombianPDMPatterns()
        logger.info("Colombian PDM Chunk Enhancer initialized")
    
    def enhance_chunk(self, chunk_content: str, chunk_metadata: dict[str, Any]) -> PDMChunkEnhancement:
        """
        Analyze chunk content and extract PDM-specific enhancements.
        
        Note: Pattern matching is performed in separate loops for clarity and maintainability.
        For most PDM documents (~1000-2000 chars per chunk), this approach is efficient.
        If performance becomes an issue with very large chunks, consider combining pattern
        detection into a single pass.
        
        Args:
            chunk_content: Text content of the chunk
            chunk_metadata: Existing chunk metadata
            
        Returns:
            PDMChunkEnhancement: Enhancement metadata
        """
        enhancement = PDMChunkEnhancement()
        
        if not chunk_content:
            return enhancement
        
        content_length = len(chunk_content)
        
        # Analyze regulatory references
        for pattern in self.patterns.regulatory_markers:
            if re.search(pattern, chunk_content, re.IGNORECASE):
                enhancement.has_regulatory_reference = True
                enhancement.regulatory_refs_count += 1
        
        # Detect PDM section markers
        for pattern in self.patterns.section_markers:
            matches = re.findall(pattern, chunk_content, re.IGNORECASE)
            if matches:
                enhancement.has_section_marker = True
                enhancement.detected_sections.extend(matches)
        
        # Identify territorial indicators
        for pattern in self.patterns.territorial_indicators:
            matches = re.findall(pattern, chunk_content, re.IGNORECASE)
            if matches:
                enhancement.has_territorial_indicator = True
                enhancement.indicator_types.extend(matches)
        
        # Detect financial information
        for pattern in self.patterns.financial_markers:
            matches = re.findall(pattern, chunk_content, re.IGNORECASE)
            if matches:
                enhancement.has_financial_info = True
                enhancement.financial_types.extend(matches)
        
        # Identify differential approach markers
        for pattern in self.patterns.differential_approach_markers:
            matches = re.findall(pattern, chunk_content, re.IGNORECASE)
            if matches:
                enhancement.has_differential_approach = True
                enhancement.population_groups.extend(matches)
        
        # Calculate quantitative density
        # Density = (number of quantitative markers) / (text length in hundreds of chars)
        # This normalizes to "markers per 100 characters" for comparability
        DENSITY_NORMALIZATION_FACTOR = 100  # chars per unit
        quant_matches = 0
        for pattern in self.patterns.quantitative_markers:
            quant_matches += len(re.findall(pattern, chunk_content, re.IGNORECASE))
        enhancement.quantitative_density = quant_matches / max(1, content_length / DENSITY_NORMALIZATION_FACTOR)
        
        # Detect strategic planning elements
        for pattern in self.patterns.strategic_markers:
            matches = re.findall(pattern, chunk_content, re.IGNORECASE)
            if matches:
                enhancement.has_strategic_elements = True
                enhancement.strategic_elements.extend(matches)
        
        # Calculate overall PDM specificity score
        enhancement.pdm_specificity_score = self._calculate_specificity_score(enhancement)
        
        # Add Colombian context markers summary
        enhancement.colombian_context_markers = {
            "regulatory": enhancement.regulatory_refs_count,
            "sections": len(enhancement.detected_sections),
            "indicators": len(enhancement.indicator_types),
            "financial": len(enhancement.financial_types),
            "differential": len(enhancement.population_groups),
            "strategic": len(enhancement.strategic_elements),
        }
        
        logger.debug(
            f"PDM enhancement complete: specificity={enhancement.pdm_specificity_score:.2f}, "
            f"markers={sum(enhancement.colombian_context_markers.values())}"
        )
        
        return enhancement
    
    def _calculate_specificity_score(self, enhancement: PDMChunkEnhancement) -> float:
        """
        Calculate overall PDM specificity score.
        
        Score components:
        - Regulatory references: 0.15
        - Section markers: 0.20
        - Territorial indicators: 0.20
        - Financial info: 0.15
        - Differential approach: 0.15
        - Strategic elements: 0.15
        
        Returns:
            float: Score between 0.0 and 1.0
        """
        score = 0.0
        
        # Regulatory references (max 0.15)
        if enhancement.has_regulatory_reference:
            score += min(0.15, enhancement.regulatory_refs_count * 0.05)
        
        # Section markers (max 0.20)
        if enhancement.has_section_marker:
            score += min(0.20, len(enhancement.detected_sections) * 0.04)
        
        # Territorial indicators (max 0.20)
        if enhancement.has_territorial_indicator:
            score += min(0.20, len(enhancement.indicator_types) * 0.04)
        
        # Financial information (max 0.15)
        if enhancement.has_financial_info:
            score += min(0.15, len(enhancement.financial_types) * 0.05)
        
        # Differential approach (max 0.15)
        if enhancement.has_differential_approach:
            score += min(0.15, len(enhancement.population_groups) * 0.03)
        
        # Strategic elements (max 0.15)
        if enhancement.has_strategic_elements:
            score += min(0.15, len(enhancement.strategic_elements) * 0.03)
        
        return min(1.0, score)
    
    def add_enhancement_to_metadata(
        self,
        chunk_metadata: dict[str, Any],
        enhancement: PDMChunkEnhancement
    ) -> dict[str, Any]:
        """
        Add enhancement information to chunk metadata.
        
        Args:
            chunk_metadata: Existing chunk metadata dictionary
            enhancement: PDM enhancement to add
            
        Returns:
            dict: Updated metadata with enhancement info
        """
        chunk_metadata["colombian_pdm_enhancement"] = {
            "pdm_specificity_score": enhancement.pdm_specificity_score,
            "has_regulatory_reference": enhancement.has_regulatory_reference,
            "has_section_marker": enhancement.has_section_marker,
            "has_territorial_indicator": enhancement.has_territorial_indicator,
            "has_financial_info": enhancement.has_financial_info,
            "has_differential_approach": enhancement.has_differential_approach,
            "quantitative_density": enhancement.quantitative_density,
            "has_strategic_elements": enhancement.has_strategic_elements,
            "context_markers": enhancement.colombian_context_markers,
            "detected_sections": enhancement.detected_sections[:5],  # Top 5
            "indicator_types": enhancement.indicator_types[:5],  # Top 5
            "population_groups": enhancement.population_groups[:5],  # Top 5
        }
        
        return chunk_metadata


# =============================================================================
# DOCUMENT PROCESSING GUARD
# =============================================================================

class AlreadyChunkedError(Exception):
    """Raised when attempting to chunk a document that is already chunked."""
    pass


def check_if_already_chunked(document: Any) -> bool:
    """
    Check if a document has already been chunked.
    
    This guard prevents methods from attempting to re-chunk documents
    that have already gone through Phase 1 chunking.
    
    Args:
        document: Document object to check
        
    Returns:
        bool: True if document is already chunked, False otherwise
    """
    # Check for chunked indicators
    if hasattr(document, "chunks") and document.chunks:
        return True
    
    if hasattr(document, "metadata"):
        metadata = document.metadata
        if isinstance(metadata, dict):
            if metadata.get("is_chunked"):
                return True
            if metadata.get("chunk_count", 0) > 0:
                return True
            if "chunking_method" in metadata:
                return True
    
    if hasattr(document, "is_chunked") and document.is_chunked:
        return True
    
    return False


def assert_not_chunked(document: Any, method_name: str = "") -> None:
    """
    Assert that a document is not already chunked.
    
    Use this at the beginning of document processing methods that
    should not operate on already-chunked documents.
    
    Args:
        document: Document to check
        method_name: Name of the calling method (for error messages)
        
    Raises:
        AlreadyChunkedError: If document is already chunked
    """
    if check_if_already_chunked(document):
        method_info = f" in method '{method_name}'" if method_name else ""
        
        # Safely get chunk count
        chunk_count = "unknown"
        if hasattr(document, 'chunks') and document.chunks:
            chunk_count = len(document.chunks)
        elif hasattr(document, 'metadata') and isinstance(document.metadata, dict):
            chunk_count = document.metadata.get('chunk_count', 'unknown')
        
        raise AlreadyChunkedError(
            f"Cannot process document that is already chunked{method_info}. "
            f"This method requires an unchunked document as input. "
            f"Document has {chunk_count} chunks."
        )

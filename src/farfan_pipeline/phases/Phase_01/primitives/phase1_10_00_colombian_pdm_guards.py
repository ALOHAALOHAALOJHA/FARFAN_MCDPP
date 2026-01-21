"""
Colombian PDM Enhancement Guard Functions
==========================================

Purpose: Primitive guard functions for Colombian Municipal Development Plan
         enhancement ensuring proper document state and enhancement validation.

These primitives are used throughout Phase 1 to verify:
- Documents are not already chunked before processing
- Chunks have mandatory PDM enhancement metadata
- Enhancement metadata meets quality standards

Author: F.A.R.F.A.N Core Team
Version: 1.0.0
Date: 2026-01-18
"""

from typing import Any, Dict, List


def check_chunk_pdm_enhancement(chunk_metadata: Dict[str, Any]) -> bool:
    """
    Check if chunk metadata contains valid Colombian PDM enhancement.
    
    Args:
        chunk_metadata: Chunk metadata dictionary
        
    Returns:
        bool: True if valid PDM enhancement present, False otherwise
    """
    if "colombian_pdm_enhancement" not in chunk_metadata:
        return False
    
    pdm_meta = chunk_metadata["colombian_pdm_enhancement"]
    
    # Check required fields
    required_fields = [
        "pdm_specificity_score",
        "has_regulatory_reference",
        "has_section_marker",
        "has_territorial_indicator",
        "has_financial_info",
        "has_differential_approach",
        "quantitative_density",
        "has_strategic_elements",
        "context_markers",
    ]
    
    for field in required_fields:
        if field not in pdm_meta:
            return False
    
    # Validate specificity score range
    score = pdm_meta["pdm_specificity_score"]
    if not isinstance(score, (int, float)) or not (0.0 <= score <= 1.0):
        return False
    
    return True


def validate_pdm_enhancement_completeness(chunks: List[Any]) -> bool:
    """
    Validate that ALL chunks have valid Colombian PDM enhancement.
    
    Args:
        chunks: List of chunk objects with metadata
        
    Returns:
        bool: True if all chunks have valid enhancement
        
    Raises:
        ValueError: If any chunk lacks valid enhancement
    """
    for chunk in chunks:
        if not hasattr(chunk, 'metadata'):
            raise ValueError(f"Chunk {getattr(chunk, 'chunk_id', 'UNKNOWN')} has no metadata attribute")
        
        if not check_chunk_pdm_enhancement(chunk.metadata):
            raise ValueError(
                f"Chunk {chunk.metadata.get('chunk_id', 'UNKNOWN')} missing or invalid "
                f"Colombian PDM enhancement. Enhancement is MANDATORY for all chunks."
            )
    
    return True


def get_pdm_specificity_stats(chunks: List[Any]) -> Dict[str, float]:
    """
    Calculate PDM specificity statistics across chunks.
    
    Args:
        chunks: List of chunks with PDM enhancement
        
    Returns:
        dict: Statistics including mean, min, max, median scores
    """
    scores = []
    
    for chunk in chunks:
        if not hasattr(chunk, 'metadata'):
            continue
        
        if "colombian_pdm_enhancement" not in chunk.metadata:
            continue
        
        score = chunk.metadata["colombian_pdm_enhancement"].get("pdm_specificity_score")
        if score is not None:
            scores.append(score)
    
    if not scores:
        return {
            "mean": 0.0,
            "min": 0.0,
            "max": 0.0,
            "median": 0.0,
            "count": 0,
        }
    
    scores_sorted = sorted(scores)
    n = len(scores)
    median = scores_sorted[n // 2] if n % 2 == 1 else (scores_sorted[n // 2 - 1] + scores_sorted[n // 2]) / 2
    
    return {
        "mean": sum(scores) / len(scores),
        "min": min(scores),
        "max": max(scores),
        "median": median,
        "count": len(scores),
    }


def count_pdm_pattern_categories(chunk_metadata: Dict[str, Any]) -> int:
    """
    Count how many PDM pattern categories are present in chunk.
    
    Categories:
    1. Regulatory references
    2. Section markers
    3. Territorial indicators
    4. Financial information
    5. Differential approach
    6. Strategic elements
    
    Args:
        chunk_metadata: Chunk metadata with PDM enhancement
        
    Returns:
        int: Number of categories present (0-6)
    """
    if "colombian_pdm_enhancement" not in chunk_metadata:
        return 0
    
    pdm_meta = chunk_metadata["colombian_pdm_enhancement"]
    
    categories_present = 0
    
    if pdm_meta.get("has_regulatory_reference"):
        categories_present += 1
    if pdm_meta.get("has_section_marker"):
        categories_present += 1
    if pdm_meta.get("has_territorial_indicator"):
        categories_present += 1
    if pdm_meta.get("has_financial_info"):
        categories_present += 1
    if pdm_meta.get("has_differential_approach"):
        categories_present += 1
    if pdm_meta.get("has_strategic_elements"):
        categories_present += 1
    
    return categories_present


def get_high_specificity_chunks(chunks: List[Any], threshold: float = 0.7) -> List[Any]:
    """
    Filter chunks with high PDM specificity scores.
    
    Args:
        chunks: List of chunks with PDM enhancement
        threshold: Minimum specificity score (default: 0.7)
        
    Returns:
        list: Chunks with specificity >= threshold
    """
    high_specificity = []
    
    for chunk in chunks:
        if not hasattr(chunk, 'metadata'):
            continue
        
        if "colombian_pdm_enhancement" not in chunk.metadata:
            continue
        
        score = chunk.metadata["colombian_pdm_enhancement"].get("pdm_specificity_score", 0.0)
        
        if score >= threshold:
            high_specificity.append(chunk)
    
    return high_specificity


__all__ = [
    "check_chunk_pdm_enhancement",
    "validate_pdm_enhancement_completeness",
    "get_pdm_specificity_stats",
    "count_pdm_pattern_categories",
    "get_high_specificity_chunks",
]

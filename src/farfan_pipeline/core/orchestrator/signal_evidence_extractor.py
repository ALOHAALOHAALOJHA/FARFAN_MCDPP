"""
Evidence Structure Enforcer - PROPOSAL #5
==========================================

Exploits 'expected_elements' field (1,200 specs) to extract structured
evidence instead of unstructured text blobs.

Intelligence Unlocked: 1,200 element specifications
Impact: Structured dict with completeness metrics (0.0-1.0)
ROI: From text blob → structured evidence with measurable completeness

Author: F.A.R.F.A.N Pipeline
Date: 2025-12-02
Refactoring: Surgical #2 of 4 (complement to semantic expansion)
"""

import re
from dataclasses import dataclass, field
from typing import Any, Callable

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


@dataclass
class EvidenceExtractionResult:
    """Structured evidence extraction result."""
    
    evidence: dict[str, Any]  # Extracted evidence by element name
    completeness: float  # 0.0 - 1.0
    missing_elements: list[str]
    extraction_metadata: dict[str, Any] = field(default_factory=dict)


# Registry of element extractors
ELEMENT_EXTRACTORS: dict[str, Callable] = {}


def register_extractor(element_name: str):
    """Decorator to register element extractor function."""
    def decorator(func):
        ELEMENT_EXTRACTORS[element_name] = func
        return func
    return decorator


@register_extractor('baseline_indicator')
def extract_baseline_indicator(
    text: str,
    patterns: list[dict[str, Any]],
    validations: dict[str, Any]
) -> dict[str, Any] | None:
    """
    Extract baseline indicator value.
    
    Args:
        text: Source text
        patterns: Applicable patterns from signal node
        validations: Validation rules
    
    Returns:
        Extracted baseline or None
    """
    # Look for patterns mentioning "baseline", "línea de base", "actual"
    baseline_patterns = [
        r'l[íi]nea\s+de\s+base[:\s]+([0-9.,]+\s*%?)',
        r'actual[:\s]+([0-9.,]+\s*%?)',
        r'baseline[:\s]+([0-9.,]+\s*%?)',
        r'situaci[óo]n\s+actual[:\s]+([0-9.,]+\s*%?)'
    ]
    
    for pattern_str in baseline_patterns:
        match = re.search(pattern_str, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            return {
                'value': value,
                'raw_text': match.group(0),
                'confidence': 0.8
            }
    
    return None


@register_extractor('target_value')
def extract_target_value(
    text: str,
    patterns: list[dict[str, Any]],
    validations: dict[str, Any]
) -> dict[str, Any] | None:
    """Extract target/goal value."""
    target_patterns = [
        r'meta[:\s]+([0-9.,]+\s*%?)',
        r'objetivo[:\s]+([0-9.,]+\s*%?)',
        r'target[:\s]+([0-9.,]+\s*%?)',
        r'alcanzar[:\s]+([0-9.,]+\s*%?)',
        r'reducir\s+a[:\s]+([0-9.,]+\s*%?)'
    ]
    
    for pattern_str in target_patterns:
        match = re.search(pattern_str, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            return {
                'value': value,
                'raw_text': match.group(0),
                'confidence': 0.8
            }
    
    return None


@register_extractor('timeline')
def extract_timeline(
    text: str,
    patterns: list[dict[str, Any]],
    validations: dict[str, Any]
) -> dict[str, Any] | None:
    """Extract timeline/deadline."""
    timeline_patterns = [
        r'para\s+(20\d{2})',
        r'en\s+(20\d{2})',
        r'hasta\s+(20\d{2})',
        r'(20\d{2})\s*[-–]\s*(20\d{2})',  # Range
        r'plazo[:\s]+([0-9]+)\s+(a[ñn]os?|meses?)'
    ]
    
    for pattern_str in timeline_patterns:
        match = re.search(pattern_str, text, re.IGNORECASE)
        if match:
            return {
                'value': match.group(1) if match.lastindex >= 1 else match.group(0),
                'raw_text': match.group(0),
                'confidence': 0.7
            }
    
    return None


@register_extractor('responsible_entity')
def extract_responsible_entity(
    text: str,
    patterns: list[dict[str, Any]],
    validations: dict[str, Any]
) -> dict[str, Any] | None:
    """Extract responsible entity/institution."""
    entity_patterns = [
        r'responsable[:\s]+([A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ\s]+(?:Secretar[íi]a|Departamento|Oficina|Alcald[íi]a))',
        r'ejecuta[:\s]+([A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ\s]+(?:Secretar[íi]a|Departamento|Oficina))',
        r'a\s+cargo\s+de[:\s]+([A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ\s]{3,40})',
    ]
    
    for pattern_str in entity_patterns:
        match = re.search(pattern_str, text, re.IGNORECASE)
        if match:
            entity = match.group(1).strip()
            return {
                'value': entity,
                'raw_text': match.group(0),
                'confidence': 0.6
            }
    
    return None


@register_extractor('budget_amount')
def extract_budget_amount(
    text: str,
    patterns: list[dict[str, Any]],
    validations: dict[str, Any]
) -> dict[str, Any] | None:
    """Extract budget amount with currency."""
    budget_patterns = [
        r'(?:COP|[$]|pesos)\s*([0-9.,]+(?:\s*(?:millones?|mil|billones?))?)',
        r'([0-9.,]+)\s*(?:COP|pesos|millones?\s+de\s+pesos)',
        r'presupuesto[:\s]+(?:COP|[$])\s*([0-9.,]+)'
    ]
    
    for pattern_str in budget_patterns:
        match = re.search(pattern_str, text, re.IGNORECASE)
        if match:
            amount = match.group(1).strip()
            # Try to detect currency
            currency = 'COP' if 'COP' in match.group(0) or 'peso' in match.group(0).lower() else 'USD'
            
            return {
                'value': amount,
                'currency': currency,
                'raw_text': match.group(0),
                'confidence': 0.75
            }
    
    return None


def get_element_extractor(element_name: str) -> Callable | None:
    """
    Get registered extractor for element.
    
    Args:
        element_name: Element to extract
    
    Returns:
        Extractor function or None
    """
    return ELEMENT_EXTRACTORS.get(element_name)


def extract_structured_evidence(
    text: str,
    signal_node: dict[str, Any],
    document_context: dict[str, Any] | None = None
) -> EvidenceExtractionResult:
    """
    Extract structured evidence based on expected_elements.
    
    This is the main entry point for structured evidence extraction.
    
    Args:
        text: Source text to extract from
        signal_node: Signal node with expected_elements, patterns, validations
        document_context: Optional document context
    
    Returns:
        EvidenceExtractionResult with structured evidence dict
    
    Example:
        >>> node = {
        ...     'expected_elements': ['baseline_indicator', 'target_value', 'timeline'],
        ...     'patterns': [...],
        ...     'validations': {}
        ... }
        >>> text = "Línea de base: 8.5%. Meta: 6% para 2027."
        >>> result = extract_structured_evidence(text, node)
        >>> result.evidence
        {
            'baseline_indicator': {'value': '8.5%', 'confidence': 0.8},
            'target_value': {'value': '6%', 'confidence': 0.8},
            'timeline': {'value': '2027', 'confidence': 0.7}
        }
        >>> result.completeness
        1.0
    """
    expected_elements = signal_node.get('expected_elements', [])
    patterns = signal_node.get('patterns', [])
    validations = signal_node.get('validations', {})
    
    evidence = {}
    missing = []
    
    logger.debug(
        "structured_extraction_start",
        expected_elements=expected_elements,
        text_length=len(text)
    )
    
    # Extract each expected element
    for element_name in expected_elements:
        extractor = get_element_extractor(element_name)
        
        if extractor is None:
            logger.warning(
                "extractor_not_found",
                element_name=element_name
            )
            missing.append(element_name)
            continue
        
        try:
            extracted = extractor(text, patterns, validations)
            
            if extracted:
                evidence[element_name] = extracted
                logger.debug(
                    "element_extracted",
                    element_name=element_name,
                    value=extracted.get('value'),
                    confidence=extracted.get('confidence')
                )
            else:
                missing.append(element_name)
                logger.debug(
                    "element_not_found",
                    element_name=element_name
                )
        
        except Exception as e:
            logger.error(
                "extraction_error",
                element_name=element_name,
                error=str(e)
            )
            missing.append(element_name)
    
    # Calculate completeness
    completeness = (
        len(evidence) / len(expected_elements)
        if expected_elements else 1.0
    )
    
    # Build metadata
    metadata = {
        'text_length': len(text),
        'expected_count': len(expected_elements),
        'extracted_count': len(evidence),
        'missing_count': len(missing)
    }
    
    if document_context:
        metadata['document_context'] = document_context
    
    return EvidenceExtractionResult(
        evidence=evidence,
        completeness=completeness,
        missing_elements=missing,
        extraction_metadata=metadata
    )


def register_custom_extractor(
    element_name: str,
    extractor_func: Callable
) -> None:
    """
    Register a custom element extractor.
    
    Args:
        element_name: Name of element to extract
        extractor_func: Function with signature:
            (text: str, patterns: list, validations: dict) -> dict | None
    
    Example:
        >>> def extract_custom_field(text, patterns, validations):
        ...     # Custom extraction logic
        ...     return {'value': 'extracted', 'confidence': 0.9}
        >>> register_custom_extractor('custom_field', extract_custom_field)
    """
    ELEMENT_EXTRACTORS[element_name] = extractor_func
    logger.info(
        "custom_extractor_registered",
        element_name=element_name
    )


# === EXPORTS ===

__all__ = [
    'EvidenceExtractionResult',
    'extract_structured_evidence',
    'register_extractor',
    'register_custom_extractor',
    'get_element_extractor',
]

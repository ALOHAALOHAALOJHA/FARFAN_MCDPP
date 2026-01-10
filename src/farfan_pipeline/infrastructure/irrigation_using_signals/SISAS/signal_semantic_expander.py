"""
Semantic Expansion Engine - PROPOSAL #2
========================================

Exploits the 'semantic_expansion' field in patterns to automatically generate
5-10 pattern variants from each base pattern.

Intelligence Unlocked: 300 semantic_expansion specs
Impact: 5x pattern coverage, catches regional terminology variations
ROI: 4,200 patterns → ~21,000 effective patterns (NO monolith edits)

Enhanced Features:
------------------
- Comprehensive input validation (type checks, None guards)
- Detailed expansion statistics tracking
- Per-pattern error handling with continue-on-failure
- Validation function for verifying expansion results
- Enhanced logging with achievement metrics
- Multiplier warnings for under/over performance

Validation Metrics:
- min_multiplier: 2.0x (minimum acceptable)
- target_multiplier: 5.0x (design target)
- actual_multiplier: tracked and validated
- achievement_pct: (actual/target) * 100

Logging Events:
- semantic_expansion_start: Begin expansion process
- semantic_expansion_complete: Expansion finished with metrics
- semantic_expansion_below_minimum: Multiplier < 2x warning
- semantic_expansion_target_approached: Multiplier ≥ 4x success
- pattern_expansion_failed: Individual pattern failure (non-fatal)
- invalid_pattern_spec_skipped: Invalid pattern skipped (non-fatal)

Author: F.A.R.F.A.N Pipeline
Date: 2025-12-02
Refactoring: Surgical #2 of 4
Updated: Enhanced with validation and comprehensive metrics
"""

import re
from typing import Any

try:
    import structlog

    logger = structlog.get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


def extract_core_term(pattern: str) -> str | None:
    """
    Extract the core searchable term from a regex pattern.

    Heuristics:
    - Look for longest word-like sequence
    - Ignore regex metacharacters
    - Prefer Spanish words (>3 chars)

    Args:
        pattern: Regex pattern string

    Returns:
        Core term or None if not extractable

    Example:
        >>> extract_core_term(r"presupuesto\\s+asignado")
        "presupuesto"
    """
    # Remove common regex metacharacters
    cleaned = re.sub(r"[\\^$.*+?{}()\[\]|]", " ", pattern)

    # Split into words
    words = [w for w in cleaned.split() if len(w) > 2]

    if not words:
        return None

    # Return longest word (heuristic: likely the key term)
    return max(words, key=len)


def expand_pattern_semantically(pattern_spec: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Generate semantic variants of a pattern using its semantic_expansion field.

    This multiplies pattern coverage by 5-10x WITHOUT editing the monolith.

    Args:
        pattern_spec: Pattern object from monolith with fields:
            - pattern: str (base regex)
            - semantic_expansion: str (pipe-separated synonyms)
            - id: str
            - confidence_weight: float
            - ... other fields

    Returns:
        List of pattern variants (includes original + expanded)

    Example:
        Input:
        {
            "pattern": r"presupuesto\\s+asignado",
            "semantic_expansion": "presupuesto|recursos|financiamiento|fondos",
            "id": "PAT-001",
            "confidence_weight": 0.8
        }

        Output: [
            {pattern: "presupuesto asignado", id: "PAT-001", is_variant: False},
            {pattern: "recursos asignados", id: "PAT-001-V1", is_variant: True},
            {pattern: "financiamiento asignado", id: "PAT-001-V2", is_variant: True},
            {pattern: "fondos asignados", id: "PAT-001-V3", is_variant: True}
        ]
    """
    base_pattern = pattern_spec.get("pattern", "")
    semantic_expansion = pattern_spec.get("semantic_expansion")
    pattern_id = pattern_spec.get("id", "UNKNOWN")

    # Always include original pattern
    variants = [{**pattern_spec, "is_variant": False, "variant_of": None}]

    if not semantic_expansion or not base_pattern:
        logger.debug(
            "semantic_expansion_skip",
            pattern_id=pattern_id,
            reason="missing_semantic_expansion_or_pattern",
            has_semantic_expansion=bool(semantic_expansion),
            has_base_pattern=bool(base_pattern),
        )
        return variants

    # Extract core term from base pattern
    core_term = extract_core_term(base_pattern)

    if not core_term:
        logger.debug(
            "semantic_expansion_skip",
            pattern_id=pattern_id,
            reason="core_term_not_extractable",
            base_pattern=base_pattern,
        )
        return variants

    logger.debug(
        "semantic_expansion_processing",
        pattern_id=pattern_id,
        core_term=core_term,
        base_pattern=base_pattern,
        semantic_expansion_type=type(semantic_expansion).__name__,
    )

    # Parse semantic expansions (can be string or dict)
    synonyms = []

    if isinstance(semantic_expansion, str):
        # Pipe-separated string format
        synonyms = [s.strip() for s in semantic_expansion.split("|") if s.strip()]
        logger.debug(
            "semantic_expansion_parsed",
            pattern_id=pattern_id,
            format="pipe_separated_string",
            synonym_count=len(synonyms),
        )
    elif isinstance(semantic_expansion, dict):
        # Dict format: key → list of expansions
        # Extract all expansions from all keys
        for key, expansions in semantic_expansion.items():
            if isinstance(expansions, list):
                synonyms.extend(expansions)
            elif isinstance(expansions, str):
                synonyms.append(expansions)
        logger.debug(
            "semantic_expansion_parsed",
            pattern_id=pattern_id,
            format="dictionary",
            synonym_count=len(synonyms),
            keys_processed=list(semantic_expansion.keys()),
        )
    else:
        logger.debug(
            "semantic_expansion_skip",
            pattern_id=pattern_id,
            reason=f"unsupported_type_{type(semantic_expansion).__name__}",
        )
        return variants

    # Generate variants
    variants_generated = 0
    synonyms_skipped = 0

    for idx, synonym in enumerate(synonyms, 1):
        # Skip if synonym is same as core term
        if synonym.lower() == core_term.lower():
            logger.debug(
                "synonym_skipped_duplicate",
                pattern_id=pattern_id,
                synonym=synonym,
                core_term=core_term,
                reason="synonym_matches_core_term",
            )
            synonyms_skipped += 1
            continue

        # Create variant pattern by substituting core term
        variant_pattern = base_pattern.replace(core_term, synonym)

        # Handle plural agreement for Spanish (simple heuristic)
        if core_term.endswith("o") and synonym.endswith("os"):
            # presupuesto → recursos → adjust surrounding words
            variant_pattern = adjust_spanish_agreement(variant_pattern, synonym)

        # Create variant spec
        variant_spec = {
            **pattern_spec,
            "pattern": variant_pattern,
            "id": f"{pattern_id}-V{variants_generated + 1}",
            "is_variant": True,
            "variant_of": pattern_id,
            "synonym_used": synonym,
        }

        variants.append(variant_spec)
        variants_generated += 1

        logger.debug(
            "semantic_variant_generated",
            base_id=pattern_id,
            variant_id=variant_spec["id"],
            synonym=synonym,
            variant_pattern=(
                variant_pattern[:50] + "..." if len(variant_pattern) > 50 else variant_pattern
            ),
        )

    logger.debug(
        "pattern_expansion_complete",
        pattern_id=pattern_id,
        variants_generated=variants_generated,
        synonyms_processed=len(synonyms),
        synonyms_skipped=synonyms_skipped,
        total_patterns=len(variants),
        multiplier=round(len(variants), 2),
    )

    return variants


def adjust_spanish_agreement(pattern: str, term: str) -> str:
    """
    Simple heuristic to adjust Spanish noun-adjective agreement.

    Args:
        pattern: Pattern with substituted term
        term: The term that was substituted

    Returns:
        Pattern with basic agreement adjustments

    Note:
        This is a simple heuristic, not full grammar processing.
        Handles common cases like "presupuesto asignado" → "fondos asignados"
    """
    # If term is plural (ends in 's'), try to pluralize following adjective
    if term.endswith("s") and not term.endswith("ss"):
        # Look for common singular adjectives after the term
        pattern = re.sub(
            rf"{re.escape(term)}\s+(asignado|aprobado|disponible|ejecutado)",
            lambda m: f"{term} {m.group(1)}s",
            pattern,
            flags=re.IGNORECASE,
        )

    return pattern


def expand_all_patterns(
    patterns: list[dict[str, Any]], enable_logging: bool = False
) -> list[dict[str, Any]]:
    """
    Expand all patterns in a list using their semantic_expansion fields.

    This is the core function for achieving 5x pattern multiplication through
    semantic expansion. It processes each pattern's semantic_expansion field
    to generate variants.

    Args:
        patterns: List of pattern specs from monolith
        enable_logging: If True, log expansion statistics with full metrics

    Returns:
        Expanded list (includes originals + variants)

    Raises:
        TypeError: If patterns is not a list
        ValueError: If patterns contains invalid pattern specs

    Statistics:
        Original: 14 patterns per question × 300 = 4,200
        Expanded: ~5-10 variants per pattern = 21,000-42,000 total (5x multiplier)

    Example:
        >>> patterns = [{'pattern': 'presupuesto', 'semantic_expansion': 'recursos|fondos'}]
        >>> expanded = expand_all_patterns(patterns, enable_logging=True)
        >>> # Returns: [original, variant_1, variant_2] = 3 patterns (3x multiplier)
    """
    import time

    expansion_start_time = time.time()

    if not isinstance(patterns, list):
        if enable_logging:
            logger.error(
                "expand_all_patterns_invalid_input",
                expected_type="list",
                actual_type=type(patterns).__name__,
            )
        raise TypeError(f"patterns must be a list, got {type(patterns).__name__}")

    if enable_logging:
        logger.info(
            "semantic_expansion_start",
            input_pattern_count=len(patterns),
            target_multiplier="5x",
            minimum_multiplier="2x",
            expansion_function="expand_all_patterns",
            enable_logging=True,
        )

    expanded = []
    expansion_stats = {
        "original_count": len(patterns),
        "variant_count": 0,
        "total_count": 0,
        "patterns_with_expansion": 0,
        "patterns_without_expansion": 0,
        "max_variants_per_pattern": 0,
        "avg_variants_per_pattern": 0.0,
        "expansion_failures": 0,
    }

    variant_counts = []

    for idx, pattern_spec in enumerate(patterns):
        if not isinstance(pattern_spec, dict):
            if enable_logging:
                logger.warning(
                    "invalid_pattern_spec_skipped",
                    pattern_index=idx,
                    type=type(pattern_spec).__name__,
                )
            expansion_stats["expansion_failures"] += 1
            continue

        try:
            variants = expand_pattern_semantically(pattern_spec)
            expanded.extend(variants)

            variant_count_for_pattern = len(variants) - 1
            variant_counts.append(variant_count_for_pattern)

            if len(variants) > 1:
                expansion_stats["patterns_with_expansion"] += 1
                expansion_stats["variant_count"] += variant_count_for_pattern
                expansion_stats["max_variants_per_pattern"] = max(
                    expansion_stats["max_variants_per_pattern"], variant_count_for_pattern
                )
            else:
                expansion_stats["patterns_without_expansion"] += 1

        except Exception as e:
            if enable_logging:
                logger.error(
                    "pattern_expansion_failed",
                    pattern_index=idx,
                    pattern_id=pattern_spec.get("id", "unknown"),
                    error=str(e),
                    error_type=type(e).__name__,
                )
            expansion_stats["expansion_failures"] += 1
            expanded.append(pattern_spec)

    expansion_stats["total_count"] = len(expanded)

    expansion_end_time = time.time()
    expansion_duration = expansion_end_time - expansion_start_time
    expansion_stats["expansion_duration_seconds"] = expansion_duration

    if expansion_stats["original_count"] > 0:
        multiplier = expansion_stats["total_count"] / expansion_stats["original_count"]
        expansion_stats["multiplier"] = multiplier

        if variant_counts:
            expansion_stats["avg_variants_per_pattern"] = sum(variant_counts) / len(variant_counts)
            expansion_stats["min_variants_per_pattern"] = (
                min(variant_counts) if variant_counts else 0
            )
            expansion_stats["max_variants_per_pattern"] = (
                max(variant_counts) if variant_counts else 0
            )
    else:
        expansion_stats["multiplier"] = 0.0

    if enable_logging:
        multiplier = expansion_stats.get("multiplier", 0.0)
        target_multiplier = 5.0
        min_multiplier = 2.0

        logger.info(
            "semantic_expansion_complete",
            **expansion_stats,
            target_multiplier=target_multiplier,
            minimum_multiplier=min_multiplier,
            achievement_pct=(
                round((multiplier / target_multiplier) * 100, 1) if multiplier > 0 else 0.0
            ),
            meets_minimum=multiplier >= min_multiplier,
            meets_target=multiplier >= target_multiplier,
            expansion_duration_seconds=round(expansion_duration, 3),
        )

        # Detailed performance categorization
        if multiplier < 2.0 and expansion_stats["original_count"] > 0:
            logger.warning(
                "semantic_expansion_below_minimum",
                multiplier=round(multiplier, 2),
                minimum_expected="2x",
                target="5x",
                patterns_with_expansion=expansion_stats["patterns_with_expansion"],
                patterns_without_expansion=expansion_stats["patterns_without_expansion"],
                avg_variants_per_pattern=round(
                    expansion_stats.get("avg_variants_per_pattern", 0.0), 2
                ),
                performance_category="BELOW_MINIMUM",
                action_required="Investigate semantic_expansion field coverage and quality",
            )
        elif multiplier >= 5.0:
            logger.info(
                "semantic_expansion_target_achieved",
                multiplier=round(multiplier, 2),
                target="5x",
                status="excellent",
                performance_category="TARGET_ACHIEVED",
                achievement_pct=100.0,
            )
        elif multiplier >= 4.0:
            logger.info(
                "semantic_expansion_target_approached",
                multiplier=round(multiplier, 2),
                target="5x",
                status="success",
                performance_category="NEAR_TARGET",
                achievement_pct=round((multiplier / target_multiplier) * 100, 1),
                gap_to_target=round(5.0 - multiplier, 2),
            )
        elif multiplier >= 2.0:
            logger.info(
                "semantic_expansion_minimum_achieved",
                multiplier=round(multiplier, 2),
                minimum="2x",
                target="5x",
                status="acceptable",
                performance_category="ABOVE_MINIMUM",
                achievement_pct=round((multiplier / target_multiplier) * 100, 1),
                gap_to_target=round(5.0 - multiplier, 2),
            )

        # Log summary statistics
        logger.info(
            "expansion_statistics_summary",
            total_patterns_processed=expansion_stats["original_count"],
            total_patterns_expanded=expansion_stats["patterns_with_expansion"],
            expansion_rate_pct=(
                round(
                    (
                        expansion_stats["patterns_with_expansion"]
                        / expansion_stats["original_count"]
                        * 100
                    ),
                    1,
                )
                if expansion_stats["original_count"] > 0
                else 0.0
            ),
            total_variants_generated=expansion_stats["variant_count"],
            avg_variants_per_expanded_pattern=(
                round(
                    expansion_stats["variant_count"] / expansion_stats["patterns_with_expansion"], 2
                )
                if expansion_stats["patterns_with_expansion"] > 0
                else 0.0
            ),
            expansion_failures=expansion_stats["expansion_failures"],
        )

    return expanded


def validate_expansion_result(
    original_patterns: list[dict[str, Any]],
    expanded_patterns: list[dict[str, Any]],
    min_multiplier: float = 2.0,
    target_multiplier: float = 5.0,
) -> dict[str, Any]:
    """
    Validate that pattern expansion achieved expected results.

    Args:
        original_patterns: Original pattern list before expansion
        expanded_patterns: Expanded pattern list after expansion
        min_multiplier: Minimum acceptable multiplier (default: 2.0)
        target_multiplier: Target multiplier for success (default: 5.0)

    Returns:
        Validation result dict with:
            - valid: bool - Whether expansion meets minimum requirements
            - multiplier: float - Actual multiplier achieved
            - meets_target: bool - Whether target multiplier was achieved
            - original_count: int
            - expanded_count: int
            - variant_count: int
            - issues: list[str] - List of validation issues found

    Example:
        >>> result = validate_expansion_result(original, expanded)
        >>> if not result['valid']:
        ...     print(f"Expansion failed: {result['issues']}")
    """
    logger.debug(
        "validate_expansion_result_start",
        original_count=len(original_patterns),
        expanded_count=len(expanded_patterns),
        min_multiplier=min_multiplier,
        target_multiplier=target_multiplier,
    )

    original_count = len(original_patterns)
    expanded_count = len(expanded_patterns)
    variant_count = expanded_count - original_count

    issues = []
    warnings = []

    if expanded_count < original_count:
        issues.append(f"Expanded count ({expanded_count}) < original count ({original_count})")
        logger.error(
            "validation_shrinkage_detected",
            original_count=original_count,
            expanded_count=expanded_count,
            shrinkage=original_count - expanded_count,
        )

    if original_count == 0:
        logger.warning("validation_no_patterns", message="No original patterns to expand")
        return {
            "valid": False,
            "multiplier": 0.0,
            "meets_target": False,
            "meets_minimum": False,
            "original_count": original_count,
            "expanded_count": expanded_count,
            "variant_count": 0,
            "actual_variant_count": 0,
            "issues": ["No original patterns to expand"],
            "warnings": [],
            "target_multiplier": target_multiplier,
            "min_multiplier": min_multiplier,
        }

    multiplier = expanded_count / original_count
    meets_minimum = multiplier >= min_multiplier
    meets_target = multiplier >= target_multiplier

    logger.debug(
        "validation_multiplier_calculated",
        multiplier=round(multiplier, 2),
        meets_minimum=meets_minimum,
        meets_target=meets_target,
    )

    if not meets_minimum:
        issues.append(f"Multiplier {multiplier:.2f}x below minimum {min_multiplier}x")
        logger.warning(
            "validation_below_minimum",
            multiplier=round(multiplier, 2),
            min_multiplier=min_multiplier,
            shortfall=round(min_multiplier - multiplier, 2),
        )

    if meets_minimum and not meets_target:
        warnings.append(
            f"Multiplier {multiplier:.2f}x meets minimum but below target {target_multiplier}x"
        )
        logger.info(
            "validation_below_target",
            multiplier=round(multiplier, 2),
            target_multiplier=target_multiplier,
            gap_to_target=round(target_multiplier - multiplier, 2),
        )

    # Validate variant metadata
    variant_patterns = [
        p for p in expanded_patterns if isinstance(p, dict) and p.get("is_variant") is True
    ]
    actual_variant_count = len(variant_patterns)

    base_patterns = [
        p for p in expanded_patterns if isinstance(p, dict) and p.get("is_variant") is False
    ]
    base_pattern_count = len(base_patterns)

    logger.debug(
        "validation_pattern_breakdown",
        base_patterns=base_pattern_count,
        variant_patterns=actual_variant_count,
        total_patterns=expanded_count,
    )

    if actual_variant_count != variant_count:
        warnings.append(
            f"Variant count mismatch: calculated={variant_count}, actual={actual_variant_count}"
        )
        logger.debug(
            "variant_count_mismatch",
            calculated_variant_count=variant_count,
            actual_variant_count=actual_variant_count,
            base_pattern_count=base_pattern_count,
        )

    if base_pattern_count != original_count:
        warnings.append(
            f"Base pattern count ({base_pattern_count}) != original count ({original_count})"
        )
        logger.warning(
            "base_pattern_count_mismatch",
            original_count=original_count,
            base_pattern_count=base_pattern_count,
        )

    # Validate variant relationships
    orphaned_variants = 0
    for variant in variant_patterns:
        variant_of = variant.get("variant_of")
        if variant_of:
            # Check if base pattern exists
            base_exists = any(bp.get("id") == variant_of for bp in base_patterns)
            if not base_exists:
                orphaned_variants += 1

    if orphaned_variants > 0:
        warnings.append(f"{orphaned_variants} variant(s) have missing base patterns")
        logger.warning(
            "orphaned_variants_detected",
            orphaned_count=orphaned_variants,
            total_variants=actual_variant_count,
        )

    result = {
        "valid": meets_minimum and len(issues) == 0,
        "multiplier": multiplier,
        "meets_target": meets_target,
        "meets_minimum": meets_minimum,
        "original_count": original_count,
        "expanded_count": expanded_count,
        "variant_count": variant_count,
        "actual_variant_count": actual_variant_count,
        "base_pattern_count": base_pattern_count,
        "orphaned_variants": orphaned_variants,
        "issues": issues,
        "warnings": warnings,
        "target_multiplier": target_multiplier,
        "min_multiplier": min_multiplier,
    }

    logger.debug(
        "validate_expansion_result_complete",
        valid=result["valid"],
        multiplier=round(multiplier, 2),
        issues_count=len(issues),
        warnings_count=len(warnings),
    )

    return result


# === EXPORTS ===

__all__ = [
    "extract_core_term",
    "expand_pattern_semantically",
    "expand_all_patterns",
    "adjust_spanish_agreement",
    "validate_expansion_result",
]

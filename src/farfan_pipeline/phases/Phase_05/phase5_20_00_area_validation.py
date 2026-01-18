"""
Phase 5 Area Validation Module (UPGRADED v2.0)

This module provides comprehensive validation functions for Phase 5 with:

STANDARD VALIDATIONS:
- Output count (exactly 10 AreaScore objects)
- Hermeticity (exactly 6 dimensions per area)
- Score bounds ([0.0, 3.0])
- Quality level consistency
- Cluster assignments (for Phase 6 transition)

UPGRADED VALIDATIONS (v2.0):
========================
1. Statistical Validation:
   - Distribution analysis (normality, skewness, kurtosis)
   - Outlier detection and flagging
   - Consistency checks across areas

2. Anomaly Detection:
   - Z-score based anomaly detection
   - IQR-based outlier identification
   - Unexpected score patterns

3. Cross-Validation:
   - Dimension-to-area aggregation consistency
   - Quality level threshold validation
   - Cluster coherence validation

4. Quality Metrics:
   - Coverage completeness
   - Score distribution health
   - Uncertainty bounds validation

Module: src/farfan_pipeline/phases/Phase_05/phase5_20_00_area_validation.py
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "2.0.0"
__phase__ = 5
__stage__ = 20
__order__ = 1
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-13"
__modified__ = "2026-01-18"
__criticality__ = "CRITICAL"
__execution_pattern__ = "On-Demand"
__upgrade__ = "FRONTIER_GRADE_v2.0"

import logging
import math
from typing import Any

from farfan_pipeline.phases.Phase_05.phase5_00_00_area_score import AreaScore
from farfan_pipeline.phases.Phase_05.PHASE_5_CONSTANTS import (
    CLUSTER_ASSIGNMENTS,
    DIMENSIONS_PER_AREA,
    DIMENSION_IDS,
    EXPECTED_AREA_SCORE_COUNT,
    MAX_SCORE,
    MIN_SCORE,
    POLICY_AREAS,
    QUALITY_THRESHOLDS,
)

# Import Phase 5 primitives (UPGRADED)
from farfan_pipeline.phases.Phase_05.primitives.phase5_00_00_statistical_primitives import (
    compute_consistency_score,
    compute_entropy,
    compute_gini_coefficient,
    compute_statistical_metrics,
    detect_outliers_iqr,
    detect_outliers_zscore,
)
from farfan_pipeline.phases.Phase_05.primitives.phase5_00_00_comparative_analytics import (
    identify_outliers as identify_outlier_areas,
)

logger = logging.getLogger(__name__)


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================


def validate_phase5_output(
    area_scores: list[AreaScore],
    strict: bool = True,
) -> tuple[bool, dict[str, Any]]:
    """
    Validate Phase 5 output (10 AreaScore objects).
    
    Checks:
    1. Count: Exactly 10 area scores
    2. Hermeticity: Each area has exactly 6 dimensions
    3. Bounds: All scores in [0.0, 3.0]
    4. Coverage: All policy areas present (PA01-PA10)
    5. Quality levels: Consistent with score thresholds
    
    Args:
        area_scores: List of AreaScore objects to validate
        strict: Whether to fail on any violation (default: True)
    
    Returns:
        Tuple of (is_valid, details_dict)
        - is_valid: True if all checks pass
        - details_dict: Dict with validation results
    """
    logger.info(f"Validating Phase 5 output: {len(area_scores)} area scores")
    
    details = {
        "count_valid": False,
        "hermeticity_valid": False,
        "bounds_valid": False,
        "coverage_valid": False,
        "quality_valid": False,
        "violations": [],
    }
    
    # 1. Validate count
    if len(area_scores) != EXPECTED_AREA_SCORE_COUNT:
        msg = f"Expected {EXPECTED_AREA_SCORE_COUNT} area scores, got {len(area_scores)}"
        logger.error(msg)
        details["violations"].append(msg)
    else:
        details["count_valid"] = True
    
    # 2. Validate hermeticity
    hermeticity_violations = []
    for area_score in area_scores:
        if len(area_score.dimension_scores) != DIMENSIONS_PER_AREA:
            msg = (
                f"Area {area_score.area_id}: expected {DIMENSIONS_PER_AREA} dimensions, "
                f"got {len(area_score.dimension_scores)}"
            )
            hermeticity_violations.append(msg)
        else:
            # Check exact dimension set
            dim_ids = {ds.dimension_id for ds in area_score.dimension_scores}
            if dim_ids != set(DIMENSION_IDS):
                missing = set(DIMENSION_IDS) - dim_ids
                extra = dim_ids - set(DIMENSION_IDS)
                msg = f"Area {area_score.area_id}: missing {missing}, extra {extra}"
                hermeticity_violations.append(msg)
    
    if hermeticity_violations:
        logger.error(f"Hermeticity violations: {len(hermeticity_violations)}")
        details["violations"].extend(hermeticity_violations)
    else:
        details["hermeticity_valid"] = True
    
    # 3. Validate bounds
    bounds_violations = []
    for area_score in area_scores:
        if area_score.score < MIN_SCORE or area_score.score > MAX_SCORE:
            msg = (
                f"Area {area_score.area_id}: score {area_score.score} "
                f"out of bounds [{MIN_SCORE}, {MAX_SCORE}]"
            )
            bounds_violations.append(msg)
    
    if bounds_violations:
        logger.error(f"Bounds violations: {len(bounds_violations)}")
        details["violations"].extend(bounds_violations)
    else:
        details["bounds_valid"] = True
    
    # 4. Validate coverage
    present_areas = {area.area_id for area in area_scores}
    expected_areas = set(POLICY_AREAS)
    if present_areas != expected_areas:
        missing = expected_areas - present_areas
        extra = present_areas - expected_areas
        msg = f"Coverage violation: missing {missing}, extra {extra}"
        logger.error(msg)
        details["violations"].append(msg)
    else:
        details["coverage_valid"] = True
    
    # 5. Validate quality levels
    quality_violations = []
    for area_score in area_scores:
        expected_quality = _get_expected_quality(area_score.score)
        if area_score.quality_level != expected_quality:
            msg = (
                f"Area {area_score.area_id}: quality level '{area_score.quality_level}' "
                f"inconsistent with score {area_score.score} (expected '{expected_quality}')"
            )
            quality_violations.append(msg)
    
    if quality_violations:
        logger.warning(f"Quality level inconsistencies: {len(quality_violations)}")
        details["violations"].extend(quality_violations)
    else:
        details["quality_valid"] = True
    
    # Overall validity
    is_valid = (
        details["count_valid"]
        and details["hermeticity_valid"]
        and details["bounds_valid"]
        and details["coverage_valid"]
        and details["quality_valid"]
    )
    
    if is_valid:
        logger.info("Phase 5 output validation: PASSED")
    else:
        logger.error(f"Phase 5 output validation: FAILED ({len(details['violations'])} violations)")
    
    return is_valid, details


def _get_expected_quality(score: float) -> str:
    """
    Get expected quality level for a score.
    
    Args:
        score: Score in [0.0, 3.0]
    
    Returns:
        Expected quality level string
    """
    normalized = score / MAX_SCORE
    if normalized >= QUALITY_THRESHOLDS["EXCELENTE"]:
        return "EXCELENTE"
    elif normalized >= QUALITY_THRESHOLDS["BUENO"]:
        return "BUENO"
    elif normalized >= QUALITY_THRESHOLDS["ACEPTABLE"]:
        return "ACEPTABLE"
    else:
        return "INSUFICIENTE"


def validate_area_score_hermeticity(area_score: AreaScore) -> tuple[bool, str]:
    """
    Validate hermeticity for a single AreaScore.
    
    Args:
        area_score: AreaScore to validate
    
    Returns:
        Tuple of (is_valid, message)
    """
    dim_count = len(area_score.dimension_scores)
    if dim_count != DIMENSIONS_PER_AREA:
        return False, f"Expected {DIMENSIONS_PER_AREA} dimensions, got {dim_count}"
    
    dim_ids = {ds.dimension_id for ds in area_score.dimension_scores}
    expected_dims = set(DIMENSION_IDS)
    if dim_ids != expected_dims:
        missing = expected_dims - dim_ids
        extra = dim_ids - expected_dims
        return False, f"Missing: {missing}, Extra: {extra}"
    
    return True, "Hermeticity OK"


def validate_area_score_bounds(area_score: AreaScore) -> tuple[bool, str]:
    """
    Validate score bounds for a single AreaScore.

    Args:
        area_score: AreaScore to validate

    Returns:
        Tuple of (is_valid, message)
    """
    if area_score.score < MIN_SCORE:
        return False, f"Score {area_score.score} below minimum {MIN_SCORE}"
    if area_score.score > MAX_SCORE:
        return False, f"Score {area_score.score} above maximum {MAX_SCORE}"
    return True, "Bounds OK"


# =============================================================================
# UPGRADED VALIDATION FUNCTIONS (v2.0)
# =============================================================================


def validate_phase5_output_comprehensive(
    area_scores: list[AreaScore],
    strict: bool = True,
    enable_statistical_validation: bool = True,
    enable_anomaly_detection: bool = True,
) -> tuple[bool, dict[str, Any]]:
    """
    Comprehensive validation with statistical analysis and anomaly detection (v2.0).

    Extends standard validation with:
    - Statistical distribution analysis
    - Anomaly detection
    - Consistency checks
    - Quality distribution validation

    Args:
        area_scores: List of AreaScore objects to validate
        strict: Whether to fail on any violation
        enable_statistical_validation: Enable statistical checks
        enable_anomaly_detection: Enable anomaly detection

    Returns:
        Tuple of (is_valid, comprehensive_details_dict)
    """
    logger.info(f"Comprehensive validation v2.0: {len(area_scores)} area scores")

    # Run standard validation first
    is_valid, details = validate_phase5_output(area_scores, strict=strict)

    # Add v2.0 validations
    if enable_statistical_validation:
        stat_valid, stat_details = validate_statistical_distribution(area_scores)
        details["statistical_validation"] = stat_details
        if not stat_valid and strict:
            is_valid = False

    if enable_anomaly_detection:
        anomaly_valid, anomaly_details = detect_anomalies(area_scores)
        details["anomaly_detection"] = anomaly_details
        if not anomaly_valid and strict:
            is_valid = False

    # Validate cluster assignments
    cluster_valid, cluster_details = validate_cluster_assignments(area_scores)
    details["cluster_validation"] = cluster_details
    if not cluster_valid and strict:
        is_valid = False

    # Validate quality distribution
    quality_valid, quality_details = validate_quality_distribution(area_scores)
    details["quality_distribution"] = quality_details
    if not quality_valid:
        details["warnings"] = details.get("warnings", []) + quality_details.get("warnings", [])

    # Overall status
    details["comprehensive_validation"] = is_valid

    if is_valid:
        logger.info("Comprehensive Phase 5 validation v2.0: PASSED")
    else:
        logger.error(f"Comprehensive Phase 5 validation v2.0: FAILED")

    return is_valid, details


def validate_statistical_distribution(
    area_scores: list[AreaScore],
) -> tuple[bool, dict[str, Any]]:
    """
    Validate statistical distribution of area scores.

    Checks:
    - Distribution metrics (mean, std, skewness, kurtosis)
    - Consistency across areas
    - Entropy (score diversity)
    - Gini coefficient (equality)

    Args:
        area_scores: List of AreaScore objects

    Returns:
        Tuple of (is_valid, statistical_details)
    """
    if not area_scores:
        return False, {"error": "No area scores provided"}

    scores = [area.score for area in area_scores]

    # Compute statistical metrics
    stats = compute_statistical_metrics(scores)

    # Compute additional metrics
    consistency = compute_consistency_score(scores)
    entropy = compute_entropy(scores, bins=10)
    gini = compute_gini_coefficient(scores)

    # Validation checks
    warnings = []
    is_valid = True

    # Check 1: Excessive variance (CV > 0.5)
    if stats.coefficient_of_variation > 0.5:
        warnings.append(
            f"High coefficient of variation ({stats.coefficient_of_variation:.3f}), "
            f"scores are highly dispersed"
        )

    # Check 2: Extreme skewness (|skew| > 2)
    if abs(stats.skewness) > 2.0:
        warnings.append(
            f"Extreme skewness ({stats.skewness:.3f}), distribution is highly asymmetric"
        )

    # Check 3: Low entropy (< 2.0)
    if entropy < 2.0:
        warnings.append(
            f"Low entropy ({entropy:.3f}), scores lack diversity"
        )

    # Check 4: High inequality (Gini > 0.4)
    if gini > 0.4:
        warnings.append(
            f"High Gini coefficient ({gini:.3f}), significant inequality in scores"
        )

    # Check 5: Low consistency (< 0.7)
    if consistency < 0.7:
        warnings.append(
            f"Low consistency score ({consistency:.3f}), high variability across areas"
        )

    details = {
        "statistics": {
            "mean": stats.mean,
            "median": stats.median,
            "std_dev": stats.std_dev,
            "coefficient_of_variation": stats.coefficient_of_variation,
            "skewness": stats.skewness,
            "kurtosis": stats.kurtosis,
            "min": stats.min_score,
            "max": stats.max_score,
            "range": stats.range,
            "iqr": stats.iqr,
        },
        "quality_metrics": {
            "consistency_score": consistency,
            "entropy": entropy,
            "gini_coefficient": gini,
        },
        "warnings": warnings,
        "is_valid": is_valid,
    }

    return is_valid, details


def detect_anomalies(
    area_scores: list[AreaScore],
) -> tuple[bool, dict[str, Any]]:
    """
    Detect anomalous area scores.

    Uses multiple methods:
    - Z-score based detection
    - IQR-based detection
    - Comparative analysis

    Args:
        area_scores: List of AreaScore objects

    Returns:
        Tuple of (no_anomalies_found, anomaly_details)
    """
    if not area_scores:
        return True, {"anomalies": [], "count": 0}

    scores_dict = {area.area_id: area.score for area in area_scores}

    # Detect outliers using comparative analytics
    outliers_zscore = identify_outlier_areas(scores_dict, method="zscore", threshold=2.5)
    outliers_iqr = identify_outlier_areas(scores_dict, method="iqr", threshold=1.5)

    # Combine outliers
    all_outliers = set(outliers_zscore) | set(outliers_iqr)

    # Build detailed anomaly report
    anomaly_details = []
    for area_id in all_outliers:
        area = next((a for a in area_scores if a.area_id == area_id), None)
        if area:
            anomaly_details.append({
                "area_id": area_id,
                "area_name": area.area_name,
                "score": area.score,
                "quality_level": area.quality_level,
                "detected_by": {
                    "zscore": area_id in outliers_zscore,
                    "iqr": area_id in outliers_iqr,
                },
            })

    no_anomalies_found = len(all_outliers) == 0

    details = {
        "anomalies": anomaly_details,
        "count": len(all_outliers),
        "outliers_zscore": list(outliers_zscore),
        "outliers_iqr": list(outliers_iqr),
        "no_anomalies": no_anomalies_found,
    }

    if not no_anomalies_found:
        logger.warning(f"Detected {len(all_outliers)} anomalous area scores")

    return no_anomalies_found, details


def validate_cluster_assignments(
    area_scores: list[AreaScore],
) -> tuple[bool, dict[str, Any]]:
    """
    Validate cluster assignments for Phase 6 transition.

    Checks:
    - All areas have cluster_id assigned
    - Cluster assignments match CLUSTER_ASSIGNMENTS constant
    - All clusters are represented

    Args:
        area_scores: List of AreaScore objects

    Returns:
        Tuple of (is_valid, cluster_validation_details)
    """
    missing_clusters = []
    incorrect_assignments = []

    # Check each area
    for area in area_scores:
        if not area.cluster_id:
            missing_clusters.append(area.area_id)
        else:
            # Verify against CLUSTER_ASSIGNMENTS
            expected_cluster = None
            for cluster, areas in CLUSTER_ASSIGNMENTS.items():
                if area.area_id in areas:
                    expected_cluster = cluster
                    break

            if expected_cluster and area.cluster_id != expected_cluster:
                incorrect_assignments.append({
                    "area_id": area.area_id,
                    "expected": expected_cluster,
                    "actual": area.cluster_id,
                })

    # Check cluster representation
    assigned_clusters = set(area.cluster_id for area in area_scores if area.cluster_id)
    expected_clusters = set(CLUSTER_ASSIGNMENTS.keys())
    missing_cluster_ids = expected_clusters - assigned_clusters

    is_valid = (
        len(missing_clusters) == 0
        and len(incorrect_assignments) == 0
        and len(missing_cluster_ids) == 0
    )

    details = {
        "missing_cluster_assignments": missing_clusters,
        "incorrect_assignments": incorrect_assignments,
        "missing_cluster_ids": list(missing_cluster_ids),
        "assigned_clusters": list(assigned_clusters),
        "is_valid": is_valid,
    }

    if not is_valid:
        logger.error(
            f"Cluster validation failed: {len(missing_clusters)} missing, "
            f"{len(incorrect_assignments)} incorrect"
        )

    return is_valid, details


def validate_quality_distribution(
    area_scores: list[AreaScore],
) -> tuple[bool, dict[str, Any]]:
    """
    Validate quality level distribution.

    Checks for:
    - Balanced distribution (not all in one category)
    - Expected distribution patterns
    - Threshold consistency

    Args:
        area_scores: List of AreaScore objects

    Returns:
        Tuple of (is_acceptable, distribution_details)
    """
    if not area_scores:
        return False, {"error": "No area scores provided"}

    # Count quality levels
    quality_counts = {
        "EXCELENTE": 0,
        "BUENO": 0,
        "ACEPTABLE": 0,
        "INSUFICIENTE": 0,
    }

    for area in area_scores:
        if area.quality_level in quality_counts:
            quality_counts[area.quality_level] += 1

    # Check for imbalance
    warnings = []
    total = len(area_scores)

    # Warning if more than 50% in any single category
    for level, count in quality_counts.items():
        percentage = (count / total) * 100 if total > 0 else 0
        if percentage > 50:
            warnings.append(
                f"More than 50% of areas ({percentage:.1f}%) are '{level}'"
            )

    # Warning if no areas in EXCELENTE
    if quality_counts["EXCELENTE"] == 0:
        warnings.append("No areas achieved 'EXCELENTE' quality level")

    # Warning if too many INSUFICIENTE
    if quality_counts["INSUFICIENTE"] > total * 0.3:
        warnings.append(
            f"More than 30% of areas ({quality_counts['INSUFICIENTE']}/{total}) are 'INSUFICIENTE'"
        )

    is_acceptable = len(warnings) == 0

    details = {
        "quality_distribution": quality_counts,
        "percentages": {
            level: (count / total * 100 if total > 0 else 0)
            for level, count in quality_counts.items()
        },
        "warnings": warnings,
        "is_acceptable": is_acceptable,
    }

    return is_acceptable, details


def validate_dimension_to_area_consistency(
    area_scores: list[AreaScore],
) -> tuple[bool, dict[str, Any]]:
    """
    Validate consistency between dimension scores and area scores.

    Checks:
    - Area score is within expected range given dimension scores
    - No dimension scores significantly dominate
    - Reasonable aggregation properties

    Args:
        area_scores: List of AreaScore objects

    Returns:
        Tuple of (is_consistent, consistency_details)
    """
    inconsistencies = []

    for area in area_scores:
        if not area.dimension_scores:
            continue

        dim_scores = [ds.score for ds in area.dimension_scores]

        # Check 1: Area score should be between min and max dimension scores
        min_dim = min(dim_scores)
        max_dim = max(dim_scores)

        if not (min_dim <= area.score <= max_dim):
            inconsistencies.append({
                "area_id": area.area_id,
                "issue": "area_score_out_of_dimension_range",
                "area_score": area.score,
                "dim_range": [min_dim, max_dim],
            })

        # Check 2: Area score shouldn't be too far from mean of dimensions
        mean_dim = sum(dim_scores) / len(dim_scores)
        deviation = abs(area.score - mean_dim)

        # Deviation > 0.5 is suspicious for weighted average
        if deviation > 0.5:
            inconsistencies.append({
                "area_id": area.area_id,
                "issue": "large_deviation_from_dimension_mean",
                "area_score": area.score,
                "dim_mean": mean_dim,
                "deviation": deviation,
            })

    is_consistent = len(inconsistencies) == 0

    details = {
        "inconsistencies": inconsistencies,
        "count": len(inconsistencies),
        "is_consistent": is_consistent,
    }

    if not is_consistent:
        logger.warning(f"Found {len(inconsistencies)} dimension-to-area inconsistencies")

    return is_consistent, details

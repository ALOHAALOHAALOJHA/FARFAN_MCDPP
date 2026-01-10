"""
PDT Quality Integration - Production Implementation
====================================================

State-of-the-art implementation of Unit Layer (@u) analysis for PDT calibration.
Implements S/M/I/P metrics with full statistical rigor, error handling, and observability.

Author: F.A.R.F.A.N Pipeline
Date: 2025-12-12
Version: 2.0.0 (Production)
"""

from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, TypedDict, Union

import numpy as np
from numpy.typing import NDArray

# ============================================================================
# TYPE DEFINITIONS
# ============================================================================


class QualityLevel(str, Enum):
    """Quality tier classification based on aggregate scores."""

    EXCELLENT = "excellent"  # >= 0.80
    GOOD = "good"  # >= 0.65
    ACCEPTABLE = "acceptable"  # >= 0.45
    POOR = "poor"  # < 0.45


class MetricType(str, Enum):
    """S/M/I/P metric types."""

    STRUCTURE = "S"
    MECHANICS = "M"
    INTEGRITY = "I"
    PRECISION = "P"


@dataclass
class PatternDefinition:
    """Immutable pattern definition for regex compilation."""

    category: MetricType
    pattern: str
    weight: float = 1.0
    flags: int = re.IGNORECASE | re.MULTILINE
    description: str = ""

    def __post_init__(self):
        """Validate pattern definition."""
        if not 0 < self.weight <= 2.0:
            raise ValueError(f"Weight must be in (0, 2.0], got {self.weight}")
        try:
            re.compile(self.pattern, self.flags)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")


class PDTQualityMetrics(TypedDict):
    """
    Unit Layer (@u) Quality Metrics (S/M/I/P).
    All scores normalized to [0.0, 1.0].
    """

    structure_score: float  # S: H1/H2/H3 hierarchy compliance
    mechanics_score: float  # M: Causal language density
    integrity_score: float  # I: Institutional entity density
    precision_score: float  # P: Metric/indicator usage
    aggregate_quality: float  # Weighted combination
    quality_level: str  # EXCELLENT/GOOD/ACCEPTABLE/POOR
    boost_factor: float  # Multiplicative boost for high-quality sections
    U_total: float  # Total unit score (sum of S+M+I+P)
    I_struct: float  # Structural integrity index (0-1)
    metadata: Dict[str, Any]  # Computation metadata


# ============================================================================
# REGEX PATTERN CATALOG
# ============================================================================


class PatternCatalog:
    """
    Comprehensive catalog of PDT analysis patterns.
    Derived from canonic_description_unit_analysis.json (Sections II-VIII).
    """

    # S: Structure Markers (Section II - Patterns of delimitation)
    STRUCTURE_PATTERNS = [
        PatternDefinition(
            MetricType.STRUCTURE,
            r"(?:CAPÍTULO|TÍTULO|PARTE)\s+[IVX\d]+",
            weight=1.5,
            description="Major chapter markers",
        ),
        PatternDefinition(
            MetricType.STRUCTURE,
            r"Línea\s+Estratégica\s+(?:\d+|[IVX]+)",
            weight=1.3,
            description="Strategic lines",
        ),
        PatternDefinition(
            MetricType.STRUCTURE,
            r"(?:ARTÍCULO|NUMERAL)\s+\d+",
            weight=1.2,
            description="Article/numeral markers",
        ),
        PatternDefinition(
            MetricType.STRUCTURE,
            r"^\s*\d+\.\d+\.?\s+[A-ZÁÉÍÓÚÑ\s]+$",
            weight=1.0,
            description="Numbered section headers",
        ),
        PatternDefinition(
            MetricType.STRUCTURE,
            r"Programa:?\s+[A-ZÁÉÍÓÚÑ]",
            weight=0.9,
            description="Program declarations",
        ),
        PatternDefinition(
            MetricType.STRUCTURE,
            r"Sector:?\s+[A-ZÁÉÍÓÚÑ]",
            weight=0.9,
            description="Sector declarations",
        ),
    ]

    # M: Mechanics Markers (Section III - Causal Language / D2_Actividades)
    MECHANICS_PATTERNS = [
        PatternDefinition(
            MetricType.MECHANICS,
            r"\b(?:implementar|fortalecer|garantizar|desarrollar|construir|adecuar|dotar)\b",
            weight=1.2,
            description="Core action verbs",
        ),
        PatternDefinition(
            MetricType.MECHANICS,
            r"\b(?:realizar|ejecutar|promover|articular|gestionar|fomentar|impulsar)\b",
            weight=1.0,
            description="Secondary action verbs",
        ),
        PatternDefinition(
            MetricType.MECHANICS,
            r"\b(?:mediante|a\s+través\s+de|por\s+medio\s+de|con\s+el\s+fin\s+de)\b",
            weight=0.8,
            description="Causal connectors",
        ),
        PatternDefinition(
            MetricType.MECHANICS,
            r"\b(?:coordinar|integrar|articular|vincular|conectar)\b",
            weight=0.9,
            description="Integration verbs",
        ),
    ]

    # I: Integrity Markers (Section VII - Entities / Section VIII - Legal)
    INTEGRITY_PATTERNS = [
        PatternDefinition(
            MetricType.INTEGRITY,
            r"\b(?:DNP|SGP|SGR|SISBEN|DANE|POT|EOT|PBOT|MFMP|POAI|RRI|PDET)\b",
            weight=1.5,
            description="National institutional acronyms",
        ),
        PatternDefinition(
            MetricType.INTEGRITY,
            r"Constituci[óo]n|Ley\s+\d+|Decreto\s+\d+|Resoluci[óo]n\s+\d*|Acuerdo\s+Municipal",
            weight=1.3,
            description="Legal references",
        ),
        PatternDefinition(
            MetricType.INTEGRITY,
            r"\b(?:Alcald[íi]a|Gobernaci[óo]n|Concejo\s+Municipal|Secretar[íi]a)\b",
            weight=1.1,
            description="Municipal/departmental entities",
        ),
        PatternDefinition(
            MetricType.INTEGRITY,
            r"\b(?:Ministerio|Instituto|Agencia|Autoridad)\s+[A-ZÁÉÍÓÚÑ]",
            weight=1.2,
            description="National agency patterns",
        ),
        PatternDefinition(
            MetricType.INTEGRITY,
            r"\b(?:Fiscalía|JEP|UBPD|UARIV|ANT|ART)\b",
            weight=1.4,
            description="Peace/justice entities",
        ),
    ]

    # P: Precision Markers (Section VI - Tables / D3_Productos / D4_Resultados)
    PRECISION_PATTERNS = [
        PatternDefinition(
            MetricType.PRECISION,
            r"\b(?:Indicador|Meta|L[íi]nea\s+Base|Producto|Resultado)\b",
            weight=1.4,
            description="Core measurement terms",
        ),
        PatternDefinition(
            MetricType.PRECISION,
            r"\b(?:Cobertura|Tasa|Porcentaje|N[úu]mero\s+de)\b",
            weight=1.2,
            description="Quantification terms",
        ),
        PatternDefinition(
            MetricType.PRECISION,
            r"\bC[óo]digo\s+(?:MGA|BPIN|Producto)",
            weight=1.3,
            description="Project/product codes",
        ),
        PatternDefinition(
            MetricType.PRECISION,
            r"\b(?:Vigencia|Presupuesto|Inversi[óo]n)\s+\d{4}",
            weight=1.1,
            description="Budget/timeline specificity",
        ),
        PatternDefinition(
            MetricType.PRECISION,
            r"\d{1,3}(?:[\.,]\d{3})*(?:\,\d+)?(?:\s*(?:COP|pesos?|millones?|miles?))?",
            weight=1.0,
            description="Currency/numeric values",
        ),
        PatternDefinition(
            MetricType.PRECISION, r"\d+(?:\.\d+)?\s*%", weight=0.9, description="Percentage values"
        ),
    ]

    @classmethod
    def get_all_patterns(cls) -> Dict[MetricType, List[PatternDefinition]]:
        """Get all patterns organized by metric type."""
        return {
            MetricType.STRUCTURE: cls.STRUCTURE_PATTERNS,
            MetricType.MECHANICS: cls.MECHANICS_PATTERNS,
            MetricType.INTEGRITY: cls.INTEGRITY_PATTERNS,
            MetricType.PRECISION: cls.PRECISION_PATTERNS,
        }


# ============================================================================
# PATTERN MATCHING ENGINE
# ============================================================================


@dataclass
class MatchResult:
    """Result of pattern matching operation."""

    metric_type: MetricType
    pattern_id: str
    matches: List[Tuple[str, int, int]]  # (text, start, end)
    confidence: float
    weight: float

    @property
    def match_count(self) -> int:
        return len(self.matches)


class PatternMatcher:
    """
    High-performance pattern matching engine with caching.
    """

    def __init__(self):
        self._compiled_patterns: Dict[str, re.Pattern] = {}
        self._pattern_defs: Dict[str, PatternDefinition] = {}
        self._cache: Dict[str, List[MatchResult]] = {}
        self._compile_all_patterns()

    def _compile_all_patterns(self) -> None:
        """Pre-compile all patterns for performance."""
        for metric_type, patterns in PatternCatalog.get_all_patterns().items():
            for idx, pattern_def in enumerate(patterns):
                pattern_id = f"{metric_type.value}-{idx:03d}"
                self._compiled_patterns[pattern_id] = re.compile(
                    pattern_def.pattern, pattern_def.flags
                )
                self._pattern_defs[pattern_id] = pattern_def

    def match_text(self, text: str, metric_type: Optional[MetricType] = None) -> List[MatchResult]:
        """
        Match text against patterns.

        Args:
            text: Text to analyze
            metric_type: If specified, only match patterns of this type

        Returns:
            List of match results sorted by confidence
        """
        # Generate cache key
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        cache_key = f"{text_hash}:{metric_type.value if metric_type else 'all'}"

        if cache_key in self._cache:
            return self._cache[cache_key]

        results: List[MatchResult] = []

        for pattern_id, compiled_pattern in self._compiled_patterns.items():
            pattern_def = self._pattern_defs[pattern_id]

            # Skip if filtering by metric type
            if metric_type and pattern_def.category != metric_type:
                continue

            # Find all matches
            matches = [
                (match.group(0), match.start(), match.end())
                for match in compiled_pattern.finditer(text)
            ]

            if matches:
                # Calculate confidence based on match quality
                confidence = self._calculate_confidence(matches, len(text))

                results.append(
                    MatchResult(
                        metric_type=pattern_def.category,
                        pattern_id=pattern_id,
                        matches=matches,
                        confidence=confidence,
                        weight=pattern_def.weight,
                    )
                )

        # Sort by confidence descending
        results.sort(key=lambda x: x.confidence, reverse=True)

        # Cache results
        self._cache[cache_key] = results

        return results

    @staticmethod
    def _calculate_confidence(matches: List[Tuple[str, int, int]], text_length: int) -> float:
        """
        Calculate confidence score for matches.

        Higher confidence for:
        - More matches relative to text length
        - Longer match spans
        - Better distribution across text
        """
        if not matches or text_length == 0:
            return 0.0

        # Density component
        density = min(len(matches) / (text_length / 1000), 1.0) * 0.4

        # Length component
        avg_length = np.mean([end - start for _, start, end in matches])
        length_score = min(avg_length / 50, 1.0) * 0.3

        # Distribution component (variance of match positions)
        positions = np.array([start / text_length for _, start, _ in matches])
        distribution_score = 1.0 - min(np.std(positions) * 2, 1.0)
        distribution_score *= 0.3

        return min(density + length_score + distribution_score, 1.0)


# ============================================================================
# SCORING ENGINE
# ============================================================================


class ScoringEngine:
    """
    Compute S/M/I/P scores with statistical rigor.
    """

    # Weights for aggregate quality calculation
    AGGREGATE_WEIGHTS = {
        MetricType.STRUCTURE: 0.20,
        MetricType.MECHANICS: 0.30,
        MetricType.INTEGRITY: 0.20,
        MetricType.PRECISION: 0.30,
    }

    # Normalization parameters (tuned for Colombian PDTs)
    NORMALIZATION_PARAMS = {
        MetricType.STRUCTURE: {"scale": 2.0, "shift": 0.1},
        MetricType.MECHANICS: {"scale": 1.5, "shift": 0.0},
        MetricType.INTEGRITY: {"scale": 2.5, "shift": 0.05},
        MetricType.PRECISION: {"scale": 1.0, "shift": 0.0},
    }

    @classmethod
    def compute_metric_score(
        cls, match_results: List[MatchResult], text_length: int, metric_type: MetricType
    ) -> float:
        """
        Compute individual metric score using log-squash normalization.

        Score formula: 1 - exp(-density * scale + shift)
        where density = weighted_hits / normalization_factor
        """
        if text_length < 50:
            return 0.0

        # Calculate weighted hit count
        weighted_hits = sum(
            result.match_count * result.weight * result.confidence
            for result in match_results
            if result.metric_type == metric_type
        )

        # Normalize by text length (per 500 chars)
        normalization_factor = max(text_length / 500.0, 1.0)
        density = weighted_hits / normalization_factor

        # Apply metric-specific normalization
        params = cls.NORMALIZATION_PARAMS[metric_type]
        raw_score = 1.0 - np.exp(-density * params["scale"])

        # Apply shift and clip
        score = np.clip(raw_score + params["shift"], 0.0, 1.0)

        return float(score)

    @classmethod
    def compute_aggregate_quality(
        cls, s_score: float, m_score: float, i_score: float, p_score: float
    ) -> float:
        """Compute weighted aggregate quality score."""
        aggregate = (
            s_score * cls.AGGREGATE_WEIGHTS[MetricType.STRUCTURE]
            + m_score * cls.AGGREGATE_WEIGHTS[MetricType.MECHANICS]
            + i_score * cls.AGGREGATE_WEIGHTS[MetricType.INTEGRITY]
            + p_score * cls.AGGREGATE_WEIGHTS[MetricType.PRECISION]
        )
        return float(np.clip(aggregate, 0.0, 1.0))

    @staticmethod
    def classify_quality_level(aggregate_score: float) -> QualityLevel:
        """Map aggregate score to quality level."""
        if aggregate_score >= 0.80:
            return QualityLevel.EXCELLENT
        elif aggregate_score >= 0.65:
            return QualityLevel.GOOD
        elif aggregate_score >= 0.45:
            return QualityLevel.ACCEPTABLE
        else:
            return QualityLevel.POOR

    @staticmethod
    def compute_boost_factor(aggregate_score: float) -> float:
        """
        Compute multiplicative boost factor for high-quality sections.

        Boost curve:
        - 0.0-0.4: 1.0x (no boost)
        - 0.4-0.6: 1.0-1.1x (linear)
        - 0.6-0.8: 1.1-1.25x (accelerating)
        - 0.8-1.0: 1.25-1.5x (max boost)
        """
        if aggregate_score < 0.4:
            return 1.0
        elif aggregate_score < 0.6:
            return 1.0 + (aggregate_score - 0.4) * 0.5
        elif aggregate_score < 0.8:
            return 1.1 + (aggregate_score - 0.6) ** 1.5 * 0.75
        else:
            return 1.25 + (aggregate_score - 0.8) * 1.25


# ============================================================================
# MAIN ANALYZER
# ============================================================================


@dataclass
class AnalysisMetadata:
    """Metadata about the analysis process."""

    timestamp: str
    text_length: int
    processing_time_ms: float
    pattern_matches_total: int
    cache_hits: int
    version: str = "2.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "text_length": self.text_length,
            "processing_time_ms": round(self.processing_time_ms, 3),
            "pattern_matches_total": self.pattern_matches_total,
            "cache_hits": self.cache_hits,
            "version": self.version,
        }


class PDTQualityAnalyzer:
    """
    Production-grade PDT quality analyzer.
    """

    def __init__(self):
        self.matcher = PatternMatcher()
        self.scoring = ScoringEngine()
        self._analysis_count = 0

    def analyze_section(
        self, section_content: str, section_name: str = "unknown"
    ) -> PDTQualityMetrics:
        """
        Analyze PDT section and compute S/M/I/P quality metrics.

        Args:
            section_content: Raw text of the section
            section_name: Name/ID of the section for logging

        Returns:
            Complete quality metrics with metadata

        Raises:
            ValueError: If section_content is invalid
        """
        start_time = time.perf_counter()

        # Validate input
        if not section_content or not isinstance(section_content, str):
            return self._create_zero_metrics(section_name, "Invalid or empty section content")

        if len(section_content) < 50:
            return self._create_zero_metrics(
                section_name, f"Section too short: {len(section_content)} chars"
            )

        # Match all patterns
        all_matches = self.matcher.match_text(section_content)

        # Compute individual metric scores
        s_score = self.scoring.compute_metric_score(
            all_matches, len(section_content), MetricType.STRUCTURE
        )
        m_score = self.scoring.compute_metric_score(
            all_matches, len(section_content), MetricType.MECHANICS
        )
        i_score = self.scoring.compute_metric_score(
            all_matches, len(section_content), MetricType.INTEGRITY
        )
        p_score = self.scoring.compute_metric_score(
            all_matches, len(section_content), MetricType.PRECISION
        )

        # Compute derived metrics
        aggregate = self.scoring.compute_aggregate_quality(s_score, m_score, i_score, p_score)
        quality_level = self.scoring.classify_quality_level(aggregate)
        boost_factor = self.scoring.compute_boost_factor(aggregate)

        # Compute unit scores
        U_total = s_score + m_score + i_score + p_score
        I_struct = self._compute_structural_integrity(s_score, m_score, i_score, p_score)

        # Create metadata
        end_time = time.perf_counter()
        metadata = AnalysisMetadata(
            timestamp=datetime.now(timezone.utc).isoformat(),
            text_length=len(section_content),
            processing_time_ms=(end_time - start_time) * 1000,
            pattern_matches_total=sum(r.match_count for r in all_matches),
            cache_hits=len(self.matcher._cache),
        )

        self._analysis_count += 1

        return PDTQualityMetrics(
            structure_score=round(s_score, 3),
            mechanics_score=round(m_score, 3),
            integrity_score=round(i_score, 3),
            precision_score=round(p_score, 3),
            aggregate_quality=round(aggregate, 3),
            quality_level=quality_level.value,
            boost_factor=round(boost_factor, 3),
            U_total=round(U_total, 3),
            I_struct=round(I_struct, 3),
            metadata={
                "section_name": section_name,
                "analysis_id": self._analysis_count,
                **metadata.to_dict(),
            },
        )

    @staticmethod
    def _compute_structural_integrity(s: float, m: float, i: float, p: float) -> float:
        """
        Compute I_struct (Structural Integrity Index).

        Measures how well the four dimensions are balanced.
        Perfect balance (all equal) → 1.0
        Severe imbalance → 0.0
        """
        scores = np.array([s, m, i, p])
        mean_score = np.mean(scores)

        if mean_score == 0:
            return 0.0

        # Calculate coefficient of variation
        cv = np.std(scores) / mean_score

        # Convert to integrity score (lower CV = higher integrity)
        integrity = 1.0 / (1.0 + cv * 2.0)

        return float(np.clip(integrity, 0.0, 1.0))

    @staticmethod
    def _create_zero_metrics(section_name: str, reason: str) -> PDTQualityMetrics:
        """Create zero-valued metrics with reason."""
        return PDTQualityMetrics(
            structure_score=0.0,
            mechanics_score=0.0,
            integrity_score=0.0,
            precision_score=0.0,
            aggregate_quality=0.0,
            quality_level=QualityLevel.POOR.value,
            boost_factor=1.0,
            U_total=0.0,
            I_struct=0.0,
            metadata={
                "section_name": section_name,
                "reason": reason,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )


# ============================================================================
# PATTERN BOOSTING ENGINE
# ============================================================================


@dataclass
class BoostStatistics:
    """Statistics from pattern boosting operation."""

    total_patterns: int
    boosted_count: int
    avg_boost_factor: float
    section_metrics: PDTQualityMetrics
    boost_distribution: Dict[str, int]  # quality_level -> count


class PatternBooster:
    """
    Applies quality-based boosting to signal patterns.
    """

    BOOST_THRESHOLD = 0.6  # Minimum aggregate quality for boosting

    @classmethod
    def apply_boost(
        cls,
        patterns: List[Dict[str, Any]],
        quality_map: Dict[str, PDTQualityMetrics],
        context: Dict[str, Any],
    ) -> Tuple[List[Dict[str, Any]], BoostStatistics]:
        """
        Apply quality boosting to patterns based on section quality.

        Args:
            patterns: List of pattern dictionaries
            quality_map: Section ID -> quality metrics
            context: Current document context (must contain 'section' key)

        Returns:
            Tuple of (boosted_patterns, boost_statistics)
        """
        section_id = context.get("section")

        if not section_id or section_id not in quality_map:
            return patterns, cls._create_no_boost_stats(len(patterns), "no_section_quality_data")

        metrics = quality_map[section_id]
        is_high_quality = metrics["aggregate_quality"] > cls.BOOST_THRESHOLD

        if not is_high_quality:
            return patterns, cls._create_no_boost_stats(
                len(patterns), "low_section_quality", metrics
            )

        # Apply boosting
        boosted_patterns = []
        boost_distribution: Dict[str, int] = {}

        for pattern in patterns:
            boosted = pattern.copy() if isinstance(pattern, dict) else pattern

            if isinstance(boosted, dict):
                boosted["_pdt_boost"] = True
                boosted["_quality_context"] = metrics
                boosted["_boost_factor"] = metrics["boost_factor"]

                quality_level = metrics["quality_level"]
                boost_distribution[quality_level] = boost_distribution.get(quality_level, 0) + 1

            boosted_patterns.append(boosted)

        stats = BoostStatistics(
            total_patterns=len(patterns),
            boosted_count=len(boosted_patterns),
            avg_boost_factor=metrics["boost_factor"],
            section_metrics=metrics,
            boost_distribution=boost_distribution,
        )

        return boosted_patterns, stats

    @staticmethod
    def _create_no_boost_stats(
        pattern_count: int, reason: str, metrics: Optional[PDTQualityMetrics] = None
    ) -> BoostStatistics:
        """Create statistics for no-boost scenario."""
        return BoostStatistics(
            total_patterns=pattern_count,
            boosted_count=0,
            avg_boost_factor=1.0,
            section_metrics=metrics
            or PDTQualityMetrics(
                structure_score=0.0,
                mechanics_score=0.0,
                integrity_score=0.0,
                precision_score=0.0,
                aggregate_quality=0.0,
                quality_level="poor",
                boost_factor=1.0,
                U_total=0.0,
                I_struct=0.0,
                metadata={"reason": reason},
            ),
            boost_distribution={},
        )


# ============================================================================
# CORRELATION ANALYSIS
# ============================================================================


@dataclass
class CorrelationMetrics:
    """Correlation between PDT quality and pattern retention."""

    high_quality_retention_rate: float
    quality_correlation: float  # Point-biserial correlation
    high_quality_patterns_count: int
    retained_high_quality_count: int
    quality_score_distribution: Dict[str, int]


class CorrelationAnalyzer:
    """
    Analyze correlation between PDT quality and filtering precision.
    """

    QUALITY_THRESHOLD = 0.6

    @classmethod
    def analyze_correlation(
        cls,
        all_patterns: List[Dict[str, Any]],
        filtered_patterns: List[Dict[str, Any]],
        quality_map: Dict[str, PDTQualityMetrics],
    ) -> CorrelationMetrics:
        """
        Analyze if filtered patterns correlate with higher quality sections.

        High correlation implies the filter successfully preserves content
        from well-structured sections of the PDT.
        """
        if not all_patterns:
            return cls._create_zero_correlation()

        # Create filtered set for O(1) lookup
        filtered_ids = {id(p) for p in filtered_patterns}

        # Analyze each pattern
        high_quality_total = 0
        high_quality_retained = 0
        quality_scores: List[float] = []
        retention_labels: List[float] = []
        distribution: Dict[str, int] = {}

        for pattern in all_patterns:
            quality_score = cls._get_pattern_quality(pattern, quality_map)
            is_high_quality = quality_score > cls.QUALITY_THRESHOLD
            is_retained = id(pattern) in filtered_ids

            if is_high_quality:
                high_quality_total += 1
                if is_retained:
                    high_quality_retained += 1

            quality_scores.append(quality_score)
            retention_labels.append(1.0 if is_retained else 0.0)

            # Track distribution
            level = cls._classify_quality(quality_score)
            distribution[level] = distribution.get(level, 0) + 1

        # Compute retention rate
        retention_rate = (
            high_quality_retained / high_quality_total if high_quality_total > 0 else 0.0
        )

        # Compute point-biserial correlation
        correlation = cls._compute_correlation(quality_scores, retention_labels)

        return CorrelationMetrics(
            high_quality_retention_rate=round(retention_rate, 3),
            quality_correlation=round(correlation, 3),
            high_quality_patterns_count=high_quality_total,
            retained_high_quality_count=high_quality_retained,
            quality_score_distribution=distribution,
        )

    @staticmethod
    def _get_pattern_quality(
        pattern: Dict[str, Any], quality_map: Dict[str, PDTQualityMetrics]
    ) -> float:
        """Extract quality score for a pattern."""
        # Check if quality context was injected
        if isinstance(pattern, dict):
            if "_quality_context" in pattern:
                return pattern["_quality_context"]["aggregate_quality"]

            # Try to resolve from pattern's context
            if "context" in pattern and isinstance(pattern["context"], dict):
                section_id = pattern["context"].get("section")
                if section_id and section_id in quality_map:
                    return quality_map[section_id]["aggregate_quality"]

        return 0.0

    @staticmethod
    def _classify_quality(score: float) -> str:
        """Classify quality score into level."""
        if score >= 0.80:
            return "excellent"
        elif score >= 0.65:
            return "good"
        elif score >= 0.45:
            return "acceptable"
        else:
            return "poor"

    @staticmethod
    def _compute_correlation(quality_scores: List[float], retention_labels: List[float]) -> float:
        """
        Compute point-biserial correlation.

        Measures linear relationship between continuous quality scores
        and binary retention labels.
        """
        if len(quality_scores) < 2 or len(set(retention_labels)) < 2:
            return 0.0

        try:
            correlation_matrix = np.corrcoef(quality_scores, retention_labels)
            correlation = float(correlation_matrix[0, 1])

            # Handle NaN (constant variance case)
            if np.isnan(correlation):
                return 0.0

            return correlation
        except Exception:
            return 0.0

    @staticmethod
    def _create_zero_correlation() -> CorrelationMetrics:
        """Create zero correlation metrics."""
        return CorrelationMetrics(
            high_quality_retention_rate=0.0,
            quality_correlation=0.0,
            high_quality_patterns_count=0,
            retained_high_quality_count=0,
            quality_score_distribution={},
        )


# ============================================================================
# BATCH PROCESSING
# ============================================================================


@dataclass
class BatchAnalysisResult:
    """Result of batch analysis operation."""

    section_metrics: Dict[str, PDTQualityMetrics]
    summary_statistics: Dict[str, Any]
    processing_time_ms: float
    timestamp: str


class BatchAnalyzer:
    """
    Batch processing for multiple PDT sections.
    """

    def __init__(self):
        self.analyzer = PDTQualityAnalyzer()

    def analyze_sections(self, sections: Dict[str, str]) -> BatchAnalysisResult:
        """
        Analyze multiple sections in batch.

        Args:
            sections: Mapping of section_id -> section_text

        Returns:
            Batch analysis result with summary statistics
        """
        start_time = time.perf_counter()

        section_metrics: Dict[str, PDTQualityMetrics] = {}

        for section_id, section_text in sections.items():
            metrics = self.analyzer.analyze_section(section_text, section_id)
            section_metrics[section_id] = metrics

        # Compute summary statistics
        summary = self._compute_summary_statistics(section_metrics)

        end_time = time.perf_counter()

        return BatchAnalysisResult(
            section_metrics=section_metrics,
            summary_statistics=summary,
            processing_time_ms=(end_time - start_time) * 1000,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    @staticmethod
    def _compute_summary_statistics(metrics: Dict[str, PDTQualityMetrics]) -> Dict[str, Any]:
        """Compute aggregate statistics across all sections."""
        if not metrics:
            return {}

        # Extract scores
        s_scores = [m["structure_score"] for m in metrics.values()]
        m_scores = [m["mechanics_score"] for m in metrics.values()]
        i_scores = [m["integrity_score"] for m in metrics.values()]
        p_scores = [m["precision_score"] for m in metrics.values()]
        agg_scores = [m["aggregate_quality"] for m in metrics.values()]

        # Quality level distribution
        level_distribution = {}
        for m in metrics.values():
            level = m["quality_level"]
            level_distribution[level] = level_distribution.get(level, 0) + 1

        return {
            "total_sections": len(metrics),
            "average_scores": {
                "structure": round(float(np.mean(s_scores)), 3),
                "mechanics": round(float(np.mean(m_scores)), 3),
                "integrity": round(float(np.mean(i_scores)), 3),
                "precision": round(float(np.mean(p_scores)), 3),
                "aggregate": round(float(np.mean(agg_scores)), 3),
            },
            "std_scores": {
                "structure": round(float(np.std(s_scores)), 3),
                "mechanics": round(float(np.std(m_scores)), 3),
                "integrity": round(float(np.std(i_scores)), 3),
                "precision": round(float(np.std(p_scores)), 3),
                "aggregate": round(float(np.std(agg_scores)), 3),
            },
            "quality_distribution": level_distribution,
            "high_quality_count": sum(1 for m in metrics.values() if m["aggregate_quality"] > 0.6),
            "excellent_sections": [
                section_id for section_id, m in metrics.items() if m["quality_level"] == "excellent"
            ],
            "poor_sections": [
                section_id for section_id, m in metrics.items() if m["quality_level"] == "poor"
            ],
        }


# ============================================================================
# EXPORT/REPORTING
# ============================================================================


class MetricsExporter:
    """
    Export quality metrics to various formats.
    """

    @staticmethod
    def to_dict(metrics: PDTQualityMetrics) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return dict(metrics)

    @staticmethod
    def to_summary_dict(
        metrics: PDTQualityMetrics, include_metadata: bool = False
    ) -> Dict[str, Any]:
        """Convert metrics to summary dictionary."""
        summary = {
            "quality_level": metrics["quality_level"],
            "aggregate_quality": metrics["aggregate_quality"],
            "boost_factor": metrics["boost_factor"],
            "scores": {
                "structure": metrics["structure_score"],
                "mechanics": metrics["mechanics_score"],
                "integrity": metrics["integrity_score"],
                "precision": metrics["precision_score"],
            },
            "derived": {
                "U_total": metrics["U_total"],
                "I_struct": metrics["I_struct"],
            },
        }

        if include_metadata:
            summary["metadata"] = metrics["metadata"]

        return summary

    @staticmethod
    def format_report(metrics: PDTQualityMetrics, verbose: bool = False) -> str:
        """Format metrics as human-readable report."""
        report_lines = [
            f"PDT Quality Analysis Report",
            f"=" * 60,
            f"Section: {metrics['metadata'].get('section_name', 'unknown')}",
            f"",
            f"Quality Level: {metrics['quality_level'].upper()}",
            f"Aggregate Score: {metrics['aggregate_quality']:.3f}",
            f"Boost Factor: {metrics['boost_factor']:.3f}x",
            f"",
            f"Individual Scores:",
            f"  Structure (S):  {metrics['structure_score']:.3f}",
            f"  Mechanics (M):  {metrics['mechanics_score']:.3f}",
            f"  Integrity (I):  {metrics['integrity_score']:.3f}",
            f"  Precision (P):  {metrics['precision_score']:.3f}",
            f"",
            f"Derived Metrics:",
            f"  U_total:   {metrics['U_total']:.3f}",
            f"  I_struct:  {metrics['I_struct']:.3f}",
        ]

        if verbose and "metadata" in metrics:
            meta = metrics["metadata"]
            report_lines.extend(
                [
                    f"",
                    f"Analysis Metadata:",
                    f"  Text Length: {meta.get('text_length', 0):,} chars",
                    f"  Processing Time: {meta.get('processing_time_ms', 0):.2f} ms",
                    f"  Pattern Matches: {meta.get('pattern_matches_total', 0)}",
                    f"  Timestamp: {meta.get('timestamp', 'N/A')}",
                ]
            )

        return "\n".join(report_lines)


# ============================================================================
# INTEGRATION HELPERS
# ============================================================================


def compute_pdt_section_quality(
    section_content: str, section_name: str = "unknown"
) -> PDTQualityMetrics:
    """
    Convenience function for single-section analysis.

    This is the main entry point matching the original API.

    Args:
        section_content: Raw text of the document section
        section_name: Optional name/ID for the section

    Returns:
        PDTQualityMetrics with normalized 0.0-1.0 scores
    """
    analyzer = PDTQualityAnalyzer()
    return analyzer.analyze_section(section_content, section_name)


def apply_pdt_quality_boost(
    patterns: List[Dict[str, Any]],
    quality_map: Dict[str, PDTQualityMetrics],
    context: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Apply quality boosting to patterns based on section quality.

    This is the main entry point matching the original API.

    Args:
        patterns: List of pattern dictionaries/objects
        quality_map: Mapping of section_id -> PDTQualityMetrics
        context: Current document context (must contain 'section' identifier)

    Returns:
        Tuple of (boosted_patterns, boost_stats_dict)
    """
    booster = PatternBooster()
    boosted_patterns, stats = booster.apply_boost(patterns, quality_map, context)

    # Convert stats to dict
    stats_dict = {
        "boosted_count": stats.boosted_count,
        "avg_boost_factor": stats.avg_boost_factor,
        "section_metrics": stats.section_metrics,
        "boost_distribution": stats.boost_distribution,
        "total_patterns": stats.total_patterns,
    }

    return boosted_patterns, stats_dict


def track_pdt_precision_correlation(
    all_patterns: List[Dict[str, Any]],
    filtered_patterns: List[Dict[str, Any]],
    quality_map: Dict[str, PDTQualityMetrics],
    stats: Dict[str, Any],
) -> Dict[str, float]:
    """
    Analyze if filtered patterns come from higher quality sections.

    This is the main entry point matching the original API.

    Args:
        all_patterns: All patterns before filtering
        filtered_patterns: Patterns after filtering
        quality_map: Section quality metrics
        stats: Additional statistics (not used, for API compatibility)

    Returns:
        Dictionary with correlation metrics
    """
    analyzer = CorrelationAnalyzer()
    metrics = analyzer.analyze_correlation(all_patterns, filtered_patterns, quality_map)

    return {
        "high_quality_retention_rate": metrics.high_quality_retention_rate,
        "quality_correlation": metrics.quality_correlation,
        "high_quality_patterns_count": metrics.high_quality_patterns_count,
        "retained_high_quality_count": metrics.retained_high_quality_count,
        "quality_score_distribution": metrics.quality_score_distribution,
    }


# ============================================================================
# VALIDATION & TESTING
# ============================================================================


class QualityValidator:
    """
    Validation utilities for quality metrics.
    """

    @staticmethod
    def validate_metrics(metrics: PDTQualityMetrics) -> Tuple[bool, List[str]]:
        """
        Validate quality metrics structure and values.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check required fields
        required_fields = [
            "structure_score",
            "mechanics_score",
            "integrity_score",
            "precision_score",
            "aggregate_quality",
            "quality_level",
            "boost_factor",
            "U_total",
            "I_struct",
            "metadata",
        ]

        for field in required_fields:
            if field not in metrics:
                errors.append(f"Missing required field: {field}")

        # Validate score ranges
        score_fields = [
            "structure_score",
            "mechanics_score",
            "integrity_score",
            "precision_score",
            "aggregate_quality",
            "I_struct",
        ]

        for field in score_fields:
            if field in metrics:
                value = metrics[field]
                if not (0.0 <= value <= 1.0):
                    errors.append(f"{field} out of range [0,1]: {value}")

        # Validate boost_factor
        if "boost_factor" in metrics:
            bf = metrics["boost_factor"]
            if not (1.0 <= bf <= 1.5):
                errors.append(f"boost_factor out of expected range [1.0,1.5]: {bf}")

        # Validate U_total
        if "U_total" in metrics:
            u = metrics["U_total"]
            if not (0.0 <= u <= 4.0):
                errors.append(f"U_total out of range [0,4]: {u}")

        # Validate quality_level
        if "quality_level" in metrics:
            level = metrics["quality_level"]
            valid_levels = ["excellent", "good", "acceptable", "poor"]
            if level not in valid_levels:
                errors.append(f"Invalid quality_level: {level}")

        return len(errors) == 0, errors

    @staticmethod
    def check_consistency(metrics: PDTQualityMetrics) -> Tuple[bool, List[str]]:
        """
        Check internal consistency of metrics.

        Returns:
            Tuple of (is_consistent, list_of_warnings)
        """
        warnings = []

        # Check aggregate vs individual scores
        s = metrics["structure_score"]
        m = metrics["mechanics_score"]
        i = metrics["integrity_score"]
        p = metrics["precision_score"]

        expected_aggregate = s * 0.20 + m * 0.30 + i * 0.20 + p * 0.30

        actual_aggregate = metrics["aggregate_quality"]

        if abs(expected_aggregate - actual_aggregate) > 0.01:
            warnings.append(
                f"Aggregate quality mismatch: "
                f"expected {expected_aggregate:.3f}, "
                f"got {actual_aggregate:.3f}"
            )

        # Check U_total
        expected_u = s + m + i + p
        actual_u = metrics["U_total"]

        if abs(expected_u - actual_u) > 0.01:
            warnings.append(
                f"U_total mismatch: " f"expected {expected_u:.3f}, " f"got {actual_u:.3f}"
            )

        # Check quality_level vs aggregate
        agg = metrics["aggregate_quality"]
        level = metrics["quality_level"]

        expected_level = (
            "excellent"
            if agg >= 0.80
            else "good" if agg >= 0.65 else "acceptable" if agg >= 0.45 else "poor"
        )

        if level != expected_level:
            warnings.append(
                f"Quality level inconsistent with score: "
                f"expected '{expected_level}', got '{level}'"
            )

        return len(warnings) == 0, warnings


# ============================================================================
# DEMO & TESTING
# ============================================================================


def demo_analysis():
    """
    Demonstration of the PDT Quality Analysis system.
    """
    # Sample PDT text (realistic excerpt)
    sample_text = """
    CAPÍTULO 5. BUENOS AIRES ACTÚA POR LA PAZ
    
    Línea Estratégica 2: Construcción de Paz y Convivencia
    
    El municipio de Buenos Aires implementará acciones concretas para 
    fortalecer la construcción de paz territorial, mediante la articulación
    con el PDET y la Reforma Rural Integral (RRI). Según datos del DNP
    y la Fiscalía General de la Nación, se evidencia una reducción del 
    45.3% en los indicadores de violencia entre 2019 y 2023.
    
    Programa: Reconciliación y Memoria Histórica
    
    Meta Cuatrienio: 1.000 personas capacitadas en resolución de conflictos.
    Línea Base: 120 personas (2023, Secretaría de Gobierno).
    Indicador de Producto: Número de talleres realizados.
    Presupuesto 2024-2027: $455.000.000 COP (SGP: 60%, SGR: 40%).
    
    La Alcaldía Municipal coordinará con la Gobernación del Cauca y el 
    Ministerio del Interior para garantizar la ejecución del plan, conforme
    a la Ley 152 de 1994 y el Decreto 1082 de 2015.
    """

    print("=" * 70)
    print("PDT QUALITY ANALYSIS - DEMONSTRATION")
    print("=" * 70)
    print()

    # Initialize analyzer
    analyzer = PDTQualityAnalyzer()

    # Analyze section
    print("Analyzing sample PDT section...")
    metrics = analyzer.analyze_section(sample_text, "CAPITULO_5_PAZ")

    # Print report
    exporter = MetricsExporter()
    print()
    print(exporter.format_report(metrics, verbose=True))
    print()

    # Validate
    validator = QualityValidator()
    is_valid, errors = validator.validate_metrics(metrics)
    is_consistent, warnings = validator.check_consistency(metrics)

    print("=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)
    print(f"Metrics Valid: {'✓ YES' if is_valid else '✗ NO'}")
    if errors:
        for error in errors:
            print(f"  ERROR: {error}")

    print(f"Metrics Consistent: {'✓ YES' if is_consistent else '✗ NO'}")
    if warnings:
        for warning in warnings:
            print(f"  WARNING: {warning}")

    print()

    return metrics


# ============================================================================
# EXPORTS
# ============================================================================


__all__ = [
    # Type definitions
    "PDTQualityMetrics",
    "QualityLevel",
    "MetricType",
    "PatternDefinition",
    "MatchResult",
    "AnalysisMetadata",
    "BoostStatistics",
    "CorrelationMetrics",
    "BatchAnalysisResult",
    # Core classes
    "PatternCatalog",
    "PatternMatcher",
    "ScoringEngine",
    "PDTQualityAnalyzer",
    "PatternBooster",
    "CorrelationAnalyzer",
    "BatchAnalyzer",
    "MetricsExporter",
    "QualityValidator",
    # Main API functions (matching original interface)
    "compute_pdt_section_quality",
    "apply_pdt_quality_boost",
    "track_pdt_precision_correlation",
    # Demo
    "demo_analysis",
]

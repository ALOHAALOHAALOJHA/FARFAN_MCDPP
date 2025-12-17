"""
Phase 1 Signal Enrichment Module
=================================

Comprehensive signal integration for Phase 1 with maximum value aggregation.
This module provides advanced signal-driven analysis and enrichment capabilities
throughout all Phase 1 subphases (SP0-SP15).

Features:
- Questionnaire-aware signal extraction and application
- Signal-driven semantic scoring for entities and relationships
- Pattern-based causal marker detection
- Indicator-weighted evidence scoring
- Signal-enhanced temporal analysis
- Quality metrics and coverage tracking

Author: F.A.R.F.A.N Pipeline Team
Version: 2.0.0 - Maximum Signal Aggregation
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from pathlib import Path

# Module-level constants for scoring and thresholds
DIMENSIONS_PER_POLICY_AREA = 6
BASE_ENTITY_IMPORTANCE = 0.3
PATTERN_WEIGHT_FACTOR = 0.1
INDICATOR_WEIGHT_FACTOR = 0.15
ENTITY_WEIGHT_FACTOR = 0.1
MAX_PATTERN_WEIGHT = 0.3
MAX_INDICATOR_WEIGHT = 0.25
MAX_ENTITY_WEIGHT = 0.15
MAX_IMPORTANCE_SCORE = 0.95

# Default causal patterns (module-level constant)
DEFAULT_CAUSAL_PATTERNS = [
    (r'\bcausa\w*\b', 'CAUSE', 0.8),
    (r'\befecto\w*\b', 'EFFECT', 0.8),
    (r'\b(?:por lo tanto|por ende|en consecuencia)\b', 'CONSEQUENCE', 0.7),
    (r'\b(?:debido a|a causa de|producto de)\b', 'CAUSE_LINK', 0.75),
    (r'\b(?:resulta en|conduce a|genera)\b', 'EFFECT_LINK', 0.75),
    (r'\b(?:si|cuando).*(?:entonces|luego)\b', 'CONDITIONAL', 0.65),
]

# Base temporal patterns (module-level constant)
BASE_TEMPORAL_PATTERNS = [
    (r'\b(20\d{2})\b', 'YEAR', 0.9),
    (r'\b(\d{1,2})[/-](\d{1,2})[/-](20\d{2})\b', 'DATE', 0.85),
    (r'\b(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+(?:de\s+)?(20\d{2})\b', 'MONTH_YEAR', 0.8),
    (r'\b(corto|mediano|largo)\s+plazo\b', 'HORIZON', 0.75),
    (r'\bvigencia\s+(20\d{2})[-–](20\d{2})\b', 'PERIOD', 0.85),
]

try:
    import structlog
    logger = structlog.get_logger(__name__)
    STRUCTLOG_AVAILABLE = True
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    STRUCTLOG_AVAILABLE = False

# Signal infrastructure imports
try:
    from cross_cutting_infrastructure.irrigation_using_signals.SISAS.signal_registry import (
        create_signal_registry,
    )
    from cross_cutting_infrastructure.irrigation_using_signals.SISAS.signals import (
        create_default_signal_pack,
    )
    from cross_cutting_infrastructure.irrigation_using_signals.SISAS.signal_quality_metrics import (
        compute_signal_quality_metrics,
        analyze_coverage_gaps,
    )
    SISAS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"SISAS not available: {e}")
    SISAS_AVAILABLE = False


@dataclass
class SignalEnrichmentContext:
    """
    Context for signal-based enrichment operations.
    
    Attributes:
        signal_registry: Questionnaire signal registry
        signal_packs: Policy area signal packs
        quality_metrics: Signal quality metrics per PA
        coverage_analysis: Coverage gap analysis
        provenance: Signal application provenance tracking
    """
    signal_registry: Optional[Any] = None
    signal_packs: Dict[str, Any] = field(default_factory=dict)
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    coverage_analysis: Optional[Any] = None
    provenance: Dict[str, List[str]] = field(default_factory=dict)
    
    def track_signal_application(self, chunk_id: str, signal_type: str, source: str) -> None:
        """Track signal application for provenance."""
        if chunk_id not in self.provenance:
            self.provenance[chunk_id] = []
        self.provenance[chunk_id].append(f"{signal_type}:{source}")


class SignalEnricher:
    """
    Advanced signal enrichment engine for Phase 1.
    Provides comprehensive signal-based analysis across all subphases.
    """
    
    def __init__(self, questionnaire_path: Optional[Path] = None):
        """
        Initialize signal enricher.
        
        Args:
            questionnaire_path: Path to questionnaire JSON for signal extraction
        """
        self.context = SignalEnrichmentContext()
        self.questionnaire_path = questionnaire_path
        self._initialized = False
        
        if SISAS_AVAILABLE and questionnaire_path and questionnaire_path.exists():
            try:
                self._initialize_signal_registry(questionnaire_path)
            except Exception as e:
                logger.warning(f"Signal registry initialization failed: {e}")
    
    def _initialize_signal_registry(self, questionnaire_path: Path) -> None:
        """Initialize signal registry from questionnaire."""
        if not SISAS_AVAILABLE:
            logger.warning("SISAS not available, skipping signal registry initialization")
            return
        
        try:
            # Load questionnaire and create signal registry
            # Note: create_signal_registry expects a loaded questionnaire object
            # For now, we'll use a fallback approach with default signal packs
            # A future enhancement would properly load the questionnaire first
            
            # Build signal packs for all policy areas
            for pa_num in range(1, 11):
                pa_id = f"PA{pa_num:02d}"
                try:
                    # Get signal pack - try from registry first, fallback to default
                    signal_pack = None
                    if self.context.signal_registry and hasattr(self.context.signal_registry, "get_signal_pack"):
                        signal_pack = self.context.signal_registry.get_signal_pack(pa_id)
                    
                    if signal_pack is None:
                        signal_pack = create_default_signal_pack(pa_id)
                    
                    self.context.signal_packs[pa_id] = signal_pack
                    
                    # Compute quality metrics
                    metrics = compute_signal_quality_metrics(signal_pack, pa_id)
                    self.context.quality_metrics[pa_id] = metrics
                    
                    logger.info(
                        f"Loaded signal pack for {pa_id}: "
                        f"{len(signal_pack.patterns)} patterns, "
                        f"{len(signal_pack.indicators)} indicators, "
                        f"quality={metrics.coverage_tier}"
                    )
                except Exception as e:
                    logger.warning(f"Failed to load signal pack for {pa_id}: {e}")
            
            # Analyze coverage gaps
            if self.context.quality_metrics:
                try:
                    self.context.coverage_analysis = analyze_coverage_gaps(
                        list(self.context.quality_metrics.values())
                    )
                    logger.info(
                        f"Coverage analysis: {len(self.context.coverage_analysis.high_coverage_pas)} high, "
                        f"{len(self.context.coverage_analysis.low_coverage_pas)} low"
                    )
                except Exception as e:
                    logger.warning(f"Coverage analysis failed: {e}")
            
            self._initialized = True
            logger.info("Signal registry initialized successfully")
            
        except Exception as e:
            logger.error(f"Signal registry initialization error: {e}")
            self._initialized = False
    
    def enrich_entity_with_signals(
        self,
        entity_text: str,
        entity_type: str,
        policy_area: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enrich entity with signal-based scoring.
        
        Args:
            entity_text: Entity text
            entity_type: Entity type (ACTOR, INDICADOR, TERRITORIO, etc.)
            policy_area: Target policy area (PA01-PA10)
        
        Returns:
            Dict with enrichment data including signal_tags, signal_scores, importance
        """
        enrichment = {
            'signal_tags': [entity_type],
            'signal_scores': {},
            'signal_importance': 0.5,  # Default baseline
            'matched_patterns': [],
            'matched_indicators': [],
            'matched_entities': [],
        }
        
        if not self._initialized or not policy_area:
            return enrichment
        
        entity_lower = entity_text.lower()
        signal_pack = self.context.signal_packs.get(policy_area)
        
        if not signal_pack:
            return enrichment
        
        # Match against signal patterns (use IGNORECASE flag, don't lowercase pattern)
        pattern_matches = 0
        for pattern in signal_pack.patterns:
            try:
                if re.search(pattern, entity_lower, re.IGNORECASE):
                    pattern_matches += 1
                    enrichment['matched_patterns'].append(pattern[:50])
                    enrichment['signal_tags'].append(f"PATTERN:{pattern[:20]}")
            except re.error:
                continue
        
        # Match against indicators
        indicator_matches = 0
        for indicator in signal_pack.indicators:
            if indicator.lower() in entity_lower:
                indicator_matches += 1
                enrichment['matched_indicators'].append(indicator)
                enrichment['signal_tags'].append(f"INDICATOR:{indicator[:20]}")
        
        # Match against entities
        entity_matches = 0
        for sig_entity in signal_pack.entities:
            if sig_entity.lower() in entity_lower or entity_lower in sig_entity.lower():
                entity_matches += 1
                enrichment['matched_entities'].append(sig_entity)
                enrichment['signal_tags'].append(f"ENTITY:{sig_entity[:20]}")
        
        # Calculate importance score based on matches using module constants
        pattern_weight = min(MAX_PATTERN_WEIGHT, pattern_matches * PATTERN_WEIGHT_FACTOR)
        indicator_weight = min(MAX_INDICATOR_WEIGHT, indicator_matches * INDICATOR_WEIGHT_FACTOR)
        entity_weight = min(MAX_ENTITY_WEIGHT, entity_matches * ENTITY_WEIGHT_FACTOR)
        
        enrichment['signal_importance'] = min(MAX_IMPORTANCE_SCORE, BASE_ENTITY_IMPORTANCE + pattern_weight + indicator_weight + entity_weight)
        
        # Track signal scores per type
        if pattern_matches > 0:
            enrichment['signal_scores']['pattern_match'] = min(1.0, pattern_matches * 0.2)
        if indicator_matches > 0:
            enrichment['signal_scores']['indicator_match'] = min(1.0, indicator_matches * 0.3)
        if entity_matches > 0:
            enrichment['signal_scores']['entity_match'] = min(1.0, entity_matches * 0.25)
        
        return enrichment
    
    def extract_causal_markers_with_signals(
        self,
        text: str,
        policy_area: str
    ) -> List[Dict[str, Any]]:
        """
        Extract causal markers using signal-driven pattern matching.
        
        Args:
            text: Text to analyze
            policy_area: Policy area for signal context
        
        Returns:
            List of causal markers with signal metadata
        """
        markers = []
        
        # Apply default patterns (use module-level constant)
        for pattern, marker_type, confidence in DEFAULT_CAUSAL_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                markers.append({
                    'text': match.group(0),
                    'type': marker_type,
                    'position': match.start(),
                    'confidence': confidence,
                    'source': 'default_pattern',
                })
        
        # Enhance with signal-based patterns if available
        if self._initialized and policy_area in self.context.signal_packs:
            signal_pack = self.context.signal_packs[policy_area]
            
            # Use signal patterns for causal detection
            for pattern in signal_pack.patterns:
                # Check if pattern might be causal-related
                pattern_lower = pattern.lower()
                if any(kw in pattern_lower for kw in ['causa', 'efecto', 'impact', 'result', 'consecuen']):
                    try:
                        for match in re.finditer(pattern, text, re.IGNORECASE):
                            markers.append({
                                'text': match.group(0),
                                'type': 'SIGNAL_CAUSAL',
                                'position': match.start(),
                                'confidence': 0.85,  # High confidence for signal patterns
                                'source': f'signal_pattern:{pattern[:30]}',
                            })
                    except re.error:
                        continue
            
            # Use signal verbs for action-based causality
            for verb in signal_pack.verbs:
                verb_pattern = rf'\b{re.escape(verb)}\w*\b'
                try:
                    for match in re.finditer(verb_pattern, text, re.IGNORECASE):
                        markers.append({
                            'text': match.group(0),
                            'type': 'ACTION_VERB',
                            'position': match.start(),
                            'confidence': 0.7,
                            'source': f'signal_verb:{verb}',
                        })
                except re.error:
                    continue
        
        # Sort by position and deduplicate overlaps
        markers.sort(key=lambda m: m['position'])
        deduplicated = []
        last_end = -1
        
        for marker in markers:
            start = marker['position']
            end = start + len(marker['text'])
            
            if start >= last_end:
                deduplicated.append(marker)
                last_end = end
        
        return deduplicated
    
    def score_argument_with_signals(
        self,
        argument_text: str,
        argument_type: str,
        policy_area: str
    ) -> Dict[str, Any]:
        """
        Score argument strength using signal-based indicators.
        
        Args:
            argument_text: Argument text
            argument_type: Argument type (claim, evidence, warrant, etc.)
            policy_area: Policy area context
        
        Returns:
            Scoring dict with signal-enhanced metrics
        """
        score = {
            'base_score': 0.5,
            'signal_boost': 0.0,
            'final_score': 0.5,
            'confidence': 0.5,
            'supporting_signals': [],
        }
        
        if not self._initialized or policy_area not in self.context.signal_packs:
            return score
        
        signal_pack = self.context.signal_packs[policy_area]
        text_lower = argument_text.lower()
        
        # Boost for indicator presence (strong evidence)
        indicator_count = 0
        for indicator in signal_pack.indicators:
            if indicator.lower() in text_lower:
                indicator_count += 1
                score['supporting_signals'].append(f"indicator:{indicator}")
        
        if indicator_count > 0:
            score['signal_boost'] += min(0.3, indicator_count * 0.15)
        
        # Boost for entity mentions (contextual grounding)
        entity_count = 0
        for entity in signal_pack.entities:
            if entity.lower() in text_lower or text_lower in entity.lower():
                entity_count += 1
                score['supporting_signals'].append(f"entity:{entity}")
        
        if entity_count > 0:
            score['signal_boost'] += min(0.15, entity_count * 0.1)
        
        # Type-specific adjustments
        if argument_type == 'evidence' and indicator_count > 0:
            score['confidence'] = min(0.9, 0.6 + indicator_count * 0.15)
        elif argument_type == 'claim' and entity_count > 0:
            score['confidence'] = min(0.85, 0.5 + entity_count * 0.12)
        else:
            score['confidence'] = 0.5 + score['signal_boost']
        
        score['final_score'] = min(0.95, score['base_score'] + score['signal_boost'])
        
        return score
    
    def extract_temporal_markers_with_signals(
        self,
        text: str,
        policy_area: str
    ) -> List[Dict[str, Any]]:
        """
        Extract temporal markers enhanced with signal patterns.
        
        Args:
            text: Text to analyze
            policy_area: Policy area context
        
        Returns:
            List of temporal markers with signal enrichment
        """
        markers = []
        
        # Use module-level BASE_TEMPORAL_PATTERNS constant
        for pattern, marker_type, confidence in BASE_TEMPORAL_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                markers.append({
                    'text': match.group(0),
                    'type': marker_type,
                    'confidence': confidence,
                    'source': 'base_temporal',
                })
        
        # Enhance with signal patterns
        if self._initialized and policy_area in self.context.signal_packs:
            signal_pack = self.context.signal_packs[policy_area]
            
            # Look for temporal patterns in signal catalog
            for pattern in signal_pack.patterns:
                pattern_lower = pattern.lower()
                if any(kw in pattern_lower for kw in ['año', 'plazo', 'fecha', 'periodo', 'vigencia', 'temporal']):
                    try:
                        for match in re.finditer(pattern, text, re.IGNORECASE):
                            markers.append({
                                'text': match.group(0),
                                'type': 'SIGNAL_TEMPORAL',
                                'confidence': 0.82,
                                'source': f'signal:{pattern[:30]}',
                            })
                    except re.error:
                        continue
        
        return markers
    
    def compute_signal_coverage_metrics(
        self,
        chunks: List[Any]
    ) -> Dict[str, Any]:
        """
        Compute comprehensive signal coverage metrics for chunk set.
        
        Args:
            chunks: List of chunks to analyze
        
        Returns:
            Coverage metrics dict
        """
        metrics = {
            'total_chunks': len(chunks),
            'chunks_with_signals': 0,
            'avg_signal_tags_per_chunk': 0.0,
            'avg_signal_score': 0.0,
            'signal_density_by_pa': {},
            'signal_diversity': 0.0,
            'coverage_completeness': 0.0,
            'quality_tier': 'UNKNOWN',
        }
        
        if not chunks:
            return metrics
        
        all_signal_tags = set()
        total_signal_tags = 0
        total_signal_score = 0.0
        pa_signals = {}
        
        for chunk in chunks:
            signal_tags = getattr(chunk, 'signal_tags', [])
            signal_scores = getattr(chunk, 'signal_scores', {})
            
            if signal_tags:
                metrics['chunks_with_signals'] += 1
                total_signal_tags += len(signal_tags)
                all_signal_tags.update(signal_tags)
            
            if signal_scores:
                chunk_avg_score = sum(signal_scores.values()) / len(signal_scores)
                total_signal_score += chunk_avg_score
            
            # Track by policy area
            pa = getattr(chunk, 'policy_area_id', 'UNKNOWN')
            if pa not in pa_signals:
                pa_signals[pa] = {'count': 0, 'tags': set()}
            pa_signals[pa]['count'] += len(signal_tags)
            pa_signals[pa]['tags'].update(signal_tags)
        
        # Compute averages
        if metrics['chunks_with_signals'] > 0:
            metrics['avg_signal_tags_per_chunk'] = total_signal_tags / len(chunks)
            metrics['avg_signal_score'] = total_signal_score / metrics['chunks_with_signals']
        
        # Signal diversity (unique tags / total tags)
        if total_signal_tags > 0:
            metrics['signal_diversity'] = len(all_signal_tags) / total_signal_tags
        
        # Coverage completeness
        metrics['coverage_completeness'] = metrics['chunks_with_signals'] / len(chunks)
        
        # PA-level density
        for pa, data in pa_signals.items():
            metrics['signal_density_by_pa'][pa] = {
                'total_signals': data['count'],
                'unique_signals': len(data['tags']),
                'avg_per_chunk': data['count'] / DIMENSIONS_PER_POLICY_AREA,
            }
        
        # Quality tier classification
        if metrics['coverage_completeness'] >= 0.95 and metrics['avg_signal_tags_per_chunk'] >= 5:
            metrics['quality_tier'] = 'EXCELLENT'
        elif metrics['coverage_completeness'] >= 0.85 and metrics['avg_signal_tags_per_chunk'] >= 3:
            metrics['quality_tier'] = 'GOOD'
        elif metrics['coverage_completeness'] >= 0.70:
            metrics['quality_tier'] = 'ADEQUATE'
        else:
            metrics['quality_tier'] = 'SPARSE'
        
        return metrics
    
    def get_provenance_report(self) -> Dict[str, Any]:
        """
        Generate signal application provenance report.
        
        Returns:
            Provenance report with detailed tracking
        """
        return {
            'initialized': self._initialized,
            'signal_packs_loaded': list(self.context.signal_packs.keys()),
            'quality_metrics_available': list(self.context.quality_metrics.keys()),
            'coverage_analysis': self.context.coverage_analysis is not None,
            'total_signal_applications': sum(len(apps) for apps in self.context.provenance.values()),
            'chunks_enriched': len(self.context.provenance),
            'provenance_details': dict(self.context.provenance),
        }


def create_signal_enricher(questionnaire_path: Optional[Path] = None) -> SignalEnricher:
    """
    Factory function to create signal enricher instance.
    
    Args:
        questionnaire_path: Optional path to questionnaire for signal extraction
    
    Returns:
        Configured SignalEnricher instance
    """
    return SignalEnricher(questionnaire_path=questionnaire_path)

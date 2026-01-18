"""Phase 3 Empirical Thresholds Loader

Loads empirical confidence thresholds and scoring weights from corpus_thresholds_weights.json
for use in Phase 3 scorers. Provides calibrated thresholds validated on 14 real PDT plans.

Key Functions:
- load_empirical_thresholds: Load full corpus with all thresholds
- get_signal_confidence_threshold: Get min_confidence for a signal type
- get_phase3_scoring_weights: Get layer-specific weights (@b, @u, @q, @d, @p, @C, @chain)
- apply_confidence_boost: Apply empirical boosts (completeness, validation, hierarchy)

EMPIRICAL BASELINE: 14 PDT Colombia 2024-2027
SOURCE: canonic_questionnaire_central/scoring/calibration/empirical_weights.json
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 3
__stage__ = 10
__order__ = 6
__author__ = "F.A.R.F.A.N Core Team - Empirical Corpus Integration"
__created__ = "2026-01-12"
__modified__ = "2026-01-12"
__criticality__ = "HIGH"
__execution_pattern__ = "On-Demand"

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "EmpiricalThresholdsLoader",
    "load_empirical_thresholds",
    "get_signal_confidence_threshold",
    "get_phase3_scoring_weights",
]

# =============================================================================
# CORPUS LOADING
# =============================================================================


def load_empirical_thresholds(corpus_path: Path | str | None = None) -> dict[str, Any]:
    """Load empirical thresholds corpus from registry.

    Args:
        corpus_path: Optional path to empirical_weights.json.
                    Defaults to canonic_questionnaire_central/scoring/calibration/

    Returns:
        Parsed JSON corpus with signal thresholds and scoring weights

    Raises:
        FileNotFoundError: If corpus file not found
        json.JSONDecodeError: If corpus file is malformed
    """
    if corpus_path is None:
        # Default path: canonic_questionnaire_central/scoring/calibration/empirical_weights.json
        # Try multiple potential repository root locations
        current_file = Path(__file__).resolve()

        # Try different levels of parent directories
        for parent_level in [4, 5, 3]:
            try:
                repo_root = current_file.parents[parent_level]
                potential_path = (
                    repo_root
                    / "canonic_questionnaire_central"
                    / "scoring"
                    / "calibration"
                    / "empirical_weights.json"
                )
                if potential_path.exists():
                    corpus_path = potential_path
                    break
            except (IndexError, OSError):
                continue

        # If still None, try working directory
        if corpus_path is None:
            cwd_path = Path.cwd() / "canonic_questionnaire_central" / "scoring" / "calibration" / "empirical_weights.json"
            if cwd_path.exists():
                corpus_path = cwd_path
            else:
                # Last resort: use parent[4] and let the FileNotFoundError happen below
                repo_root = current_file.parents[4]
                corpus_path = (
                    repo_root
                    / "canonic_questionnaire_central"
                    / "scoring"
                    / "calibration"
                    / "empirical_weights.json"
                )

    corpus_path = Path(corpus_path)

    if not corpus_path.exists():
        raise FileNotFoundError(f"Empirical thresholds corpus not found: {corpus_path}")

    logger.info(f"Loading empirical thresholds corpus from: {corpus_path}")

    with corpus_path.open("r", encoding="utf-8") as f:
        corpus = json.load(f)

    logger.info(
        f"Loaded empirical thresholds v{corpus.get('calibration_config_version', 'unknown')} "
        f"from {corpus.get('empirical_baseline', 'unknown')}"
    )

    return corpus


# =============================================================================
# EMPIRICAL THRESHOLDS LOADER
# =============================================================================


class EmpiricalThresholdsLoader:
    """Loads and provides empirical thresholds for Phase 3 scoring.

    Attributes:
        corpus: Loaded empirical thresholds corpus
        signal_thresholds: Confidence thresholds per signal type
        phase3_weights: Scoring weights for Phase 3 layers
        aggregation_weights: Aggregation weights for Phases 4-7
        value_add_thresholds: Value-add thresholds for signal filtering
    """

    def __init__(self, corpus_path: Path | str | None = None):
        """Initialize loader with empirical thresholds corpus.

        Args:
            corpus_path: Optional path to empirical_weights.json
        """
        self.corpus = load_empirical_thresholds(corpus_path)
        self.signal_thresholds = self.corpus.get("signal_confidence_thresholds", {})
        self.phase3_weights = self.corpus.get("phase3_scoring_weights", {})
        self.aggregation_weights = self.corpus.get("aggregation_weights", {})
        self.value_add_thresholds = self.corpus.get("value_add_thresholds", {})

        logger.info(
            f"EmpiricalThresholdsLoader initialized: "
            f"{len(self.signal_thresholds)} signal types, "
            f"{len(self.phase3_weights)} Phase 3 layers"
        )

    def get_signal_confidence_threshold(
        self,
        signal_type: str,
        extraction_method: str = "default",
    ) -> float:
        """Get minimum confidence threshold for a signal type.

        Args:
            signal_type: Signal type (e.g., "QUANTITATIVE_TRIPLET")
            extraction_method: Extraction method (e.g., "from_table", "from_text")

        Returns:
            Minimum confidence threshold (0.0-1.0), defaults to 0.75
        """
        signal_config = self.signal_thresholds.get(signal_type, {})

        # Try extraction method-specific threshold
        method_config = signal_config.get(extraction_method, {})
        if method_config:
            threshold = method_config.get("min_confidence")
            if threshold is not None:
                return float(threshold)

        # Fallback: Try to find any threshold in signal_config
        for method, config in signal_config.items():
            if isinstance(config, dict) and "min_confidence" in config:
                threshold = config.get("min_confidence")
                logger.debug(
                    f"Using fallback threshold for {signal_type}.{extraction_method}: "
                    f"{threshold} (from {method})"
                )
                return float(threshold)

        # Default threshold
        logger.debug(f"Using default threshold for {signal_type}.{extraction_method}: 0.75")
        return 0.75

    def get_confidence_boost(
        self,
        signal_type: str,
        boost_type: str,
    ) -> float:
        """Get confidence boost factor for a signal type.

        Args:
            signal_type: Signal type (e.g., "QUANTITATIVE_TRIPLET")
            boost_type: Boost type (e.g., "completeness_boost", "validated_closure")

        Returns:
            Boost factor (typically 1.0-1.3), defaults to 1.0
        """
        signal_config = self.signal_thresholds.get(signal_type, {})
        boost_config = signal_config.get(boost_type, {})

        # Handle different boost formats
        if isinstance(boost_config, dict):
            # Format 1: {"boost": 1.20, "conditions": "..."}
            if "boost" in boost_config:
                return float(boost_config["boost"])
            # Format 2: {"value": 1.30, "conditions": "..."}
            if "value" in boost_config:
                return float(boost_config["value"])
            # Format 3: {"COMPLETO": 1.0, "ALTO": 0.95, ...}
            # Return dict for caller to resolve specific key
            return boost_config

        # Scalar boost value
        if isinstance(boost_config, (int, float)):
            return float(boost_config)

        # Default: no boost
        return 1.0

    def get_phase3_layer_weights(self, layer: str) -> dict[str, float]:
        """Get scoring weights for a Phase 3 layer.

        Args:
            layer: Layer name (e.g., "layer_b_baseline", "layer_q_quality")

        Returns:
            Dict of component weights for the layer
        """
        layer_weights = self.phase3_weights.get(layer, {})

        # Filter out non-weight keys (e.g., "note", "required_sections")
        weights = {
            k: v
            for k, v in layer_weights.items()
            if isinstance(v, (int, float)) and not k.startswith("_")
        }

        return weights

    def get_aggregation_weights(self, phase: str) -> dict[str, Any]:
        """Get aggregation weights for a specific phase.

        Args:
            phase: Phase name (e.g., "phase4_dimension_aggregation",
                   "phase5_policy_area_aggregation")

        Returns:
            Aggregation weights dict for the phase
        """
        return self.aggregation_weights.get(phase, {})

    def get_value_add_threshold(self, signal_type: str) -> float:
        """Get value-add threshold for a signal type.

        Args:
            signal_type: Signal type (e.g., "QUANTITATIVE_TRIPLET_complete")

        Returns:
            Value-add threshold (delta_score improvement required)
        """
        high_value = self.value_add_thresholds.get("high_value_signals", {})
        low_value = self.value_add_thresholds.get("low_value_signals", {})
        minimum = self.value_add_thresholds.get("minimum_value_add", {})

        # Check high-value signals
        if signal_type in high_value:
            return float(high_value[signal_type])

        # Check low-value signals
        if signal_type in low_value:
            return float(low_value[signal_type])

        # Default minimum value-add
        return float(minimum.get("delta_score", 0.05))

    def validate_signal_confidence(
        self,
        signal_type: str,
        confidence: float,
        extraction_method: str = "default",
    ) -> bool:
        """Validate if signal confidence meets empirical threshold.

        Args:
            signal_type: Signal type
            confidence: Signal confidence (0.0-1.0)
            extraction_method: Extraction method

        Returns:
            True if confidence >= threshold, False otherwise
        """
        threshold = self.get_signal_confidence_threshold(signal_type, extraction_method)
        return confidence >= threshold


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def get_signal_confidence_threshold(
    signal_type: str,
    extraction_method: str = "default",
    corpus_path: Path | str | None = None,
) -> float:
    """Convenience function to get signal confidence threshold.

    Args:
        signal_type: Signal type
        extraction_method: Extraction method
        corpus_path: Optional path to empirical_weights.json

    Returns:
        Minimum confidence threshold
    """
    loader = EmpiricalThresholdsLoader(corpus_path=corpus_path)
    return loader.get_signal_confidence_threshold(signal_type, extraction_method)


def get_phase3_scoring_weights(
    layer: str,
    corpus_path: Path | str | None = None,
) -> dict[str, float]:
    """Convenience function to get Phase 3 layer weights.

    Args:
        layer: Layer name (e.g., "layer_b_baseline")
        corpus_path: Optional path to empirical_weights.json

    Returns:
        Layer weights dict
    """
    loader = EmpiricalThresholdsLoader(corpus_path=corpus_path)
    return loader.get_phase3_layer_weights(layer)


# =============================================================================
# SINGLETON INSTANCE (LAZY LOAD)
# =============================================================================

_global_loader: EmpiricalThresholdsLoader | None = None


def get_global_thresholds_loader(corpus_path: Path | str | None = None) -> EmpiricalThresholdsLoader:
    """Get global singleton EmpiricalThresholdsLoader instance.

    Args:
        corpus_path: Optional path to empirical_weights.json

    Returns:
        Global EmpiricalThresholdsLoader instance
    """
    global _global_loader
    if _global_loader is None:
        _global_loader = EmpiricalThresholdsLoader(corpus_path=corpus_path)
    return _global_loader
        # =========================================================================
    # PHASE 3: LAYER SCORING - COMPLETE IMPLEMENTATION
    # =========================================================================
    
    def _execute_phase_3(self) -> dict[str, Any]:
        """
        Execute Phase 3: 8-Layer Quality Assessment.
        
        Transforms 300 task results from Phase 2 into 2400 layer scores
        (300 questions × 8 layers = 2400 scores).
        
        8 CANONICAL LAYERS:
        1. @b (Baseline) - Basic presence and structure
        2. @u (Understanding) - Comprehension depth
        3. @q (Quality) - Evidence quality and reliability
        4. @d (Development) - Implementation maturity
        5. @p (Progress) - Evolution and advancement
        6. @C (Coherence) - Internal consistency
        7. @chain (Causality) - Causal chain integrity
        8. @cross (Cross-cutting) - Transversal themes
        
        Constitutional Invariants:
        - 300 task results input (from Phase 2)
        - 2400 layer scores output (300 × 8)
        - Score range [0.0, 1.0] with clamping
        - Quality levels: EXCELENTE/ACEPTABLE/INSUFICIENTE/NO_APLICABLE
        - Empirical thresholds from 14 PDT baseline
        """
        from farfan_pipeline.phases.Phase_03.phase3_20_00_score_extraction import (
            extract_score_from_nexus,
            map_completeness_to_quality,
        )
        from farfan_pipeline.phases.Phase_03.phase3_22_00_validation import (
            ValidationCounters,
            validate_micro_results_input,
            validate_evidence_presence,
            validate_and_clamp_score,
            validate_quality_level,
        )
        from farfan_pipeline.phases.Phase_03.phase3_24_00_signal_enriched_scoring import (
            SignalEnrichedScorer,
            generate_quality_promotion_report,
        )
        from farfan_pipeline.phases.Phase_03.phase3_15_00_empirical_thresholds_loader import (
            EmpiricalThresholdsLoader,
        )
        from farfan_pipeline.phases.Phase_03.phase3_26_00_normative_compliance_validator import (
            NormativeComplianceValidator,
        )
        
        stage_timings = {}
        sub_phase_results = {}
        
        # =====================================================================
        # STAGE 1: INPUT VALIDATION
        # =====================================================================
        stage_start = time.time()
        self.logger.info("phase_3_stage_1_input_validation")
        
        # Get task results from Phase 2
        phase2_output = self.context.get_phase_output(PhaseID.PHASE_2)
        if not phase2_output:
            raise RuntimeError("Phase 2 output not available")
        
        task_results = phase2_output.get("task_results", [])
        carved_answers = phase2_output.get("carved_answers", [])
        evidence_nexus = phase2_output.get("evidence_nexus")
        
        # Validate we have exactly 300 task results
        validate_micro_results_input(task_results, expected_count=300)
        
        # Initialize validation counters
        validation_counters = ValidationCounters(total_questions=300)
        
        sub_phase_results["input_validation"] = {
            "task_results_count": len(task_results),
            "carved_answers_count": len(carved_answers),
            "evidence_nexus_available": evidence_nexus is not None,
        }
        stage_timings["input_validation"] = time.time() - stage_start
        
        # =====================================================================
        # STAGE 2: INITIALIZE SCORING COMPONENTS
        # =====================================================================
        stage_start = time.time()
        self.logger.info("phase_3_stage_2_initialize_scorers")
        
        # Load empirical thresholds from 14 PDT baseline
        empirical_loader = EmpiricalThresholdsLoader()
        
        # Initialize signal-enriched scorer
        signal_registry = self.context.sisas.signal_registry if self.context.sisas else None
        signal_scorer = SignalEnrichedScorer(
            signal_registry=signal_registry,
            enable_threshold_adjustment=True,
            enable_quality_validation=True,
        )
        
        # Initialize normative compliance validator
        normative_validator = NormativeComplianceValidator()
        
        # Get municipality context for contextual validation
        municipality_context = self.context.config.get("municipality_context", {})
        
        sub_phase_results["initialization"] = {
            "empirical_corpus_loaded": True,
            "signal_scoring_enabled": signal_registry is not None,
            "normative_validation_enabled": True,
            "municipality_context": municipality_context,
        }
        stage_timings["initialization"] = time.time() - stage_start
        
        # =====================================================================
        # STAGE 3: EXTRACT BASE SCORES FROM PHASE 2
        # =====================================================================
        stage_start = time.time()
        self.logger.info("phase_3_stage_3_extract_base_scores")
        
        base_scores = []
        quality_levels = []
        
        for idx, task_result in enumerate(task_results):
            # Extract question info
            question_id = getattr(task_result, "question_id", f"Q{idx+1:03d}")
            question_global = getattr(task_result, "question_global", idx + 1)
            
            # Get result data and evidence
            result_data = getattr(task_result, "result", {})
            evidence = getattr(task_result, "evidence")
            
            # Validate evidence presence
            if not validate_evidence_presence(
                evidence, question_id, question_global, validation_counters
            ):
                # Use default score for missing evidence
                base_scores.append(0.0)
                quality_levels.append("INSUFICIENTE")
                continue
            
            # Extract score from EvidenceNexus result
            raw_score = extract_score_from_nexus(result_data)
            
            # Validate and clamp score
            clamped_score = validate_and_clamp_score(
                raw_score, question_id, question_global, validation_counters
            )
            
            # Extract quality level
            completeness = result_data.get("completeness")
            quality_level = map_completeness_to_quality(completeness)
            
            # Validate quality level
            validated_quality = validate_quality_level(
                quality_level, question_id, question_global, validation_counters
            )
            
            base_scores.append(clamped_score)
            quality_levels.append(validated_quality)
        
        sub_phase_results["base_extraction"] = {
            "scores_extracted": len(base_scores),
            "quality_levels_extracted": len(quality_levels),
            "validation_issues": {
                "missing_evidence": validation_counters.missing_evidence,
                "out_of_bounds_scores": validation_counters.out_of_bounds_scores,
                "invalid_quality_levels": validation_counters.invalid_quality_levels,
            }
        }
        stage_timings["base_extraction"] = time.time() - stage_start
        
        # =====================================================================
        # STAGE 4: APPLY 8-LAYER SCORING
        # =====================================================================
        stage_start = time.time()
        self.logger.critical("phase_3_stage_4_layer_scoring - CRITICAL: 8 LAYERS")
        
        # Initialize layer scores structure (300 questions × 8 layers)
        layer_scores = {
            "layer_b_baseline": [],      # Layer 1
            "layer_u_understanding": [],  # Layer 2
            "layer_q_quality": [],        # Layer 3
            "layer_d_development": [],    # Layer 4
            "layer_p_progress": [],       # Layer 5
            "layer_C_coherence": [],      # Layer 6
            "layer_chain_causality": [],  # Layer 7
            "layer_cross_cutting": [],    # Layer 8
        }
        
        # Process each question through all 8 layers
        for idx, task_result in enumerate(task_results):
            question_id = getattr(task_result, "question_id", f"Q{idx+1:03d}")
            base_score = base_scores[idx]
            quality_level = quality_levels[idx]
            
            # Get enriched evidence pack if available
            enriched_pack = None
            if hasattr(task_result, "enriched_pack"):
                enriched_pack = task_result.enriched_pack
            
            # =========== LAYER 1: BASELINE (@b) ===========
            layer_b_score = self._score_layer_baseline(
                base_score=base_score,
                quality_level=quality_level,
                task_result=task_result,
                empirical_loader=empirical_loader,
            )
            layer_scores["layer_b_baseline"].append(layer_b_score)
            
            # =========== LAYER 2: UNDERSTANDING (@u) ===========
            layer_u_score = self._score_layer_understanding(
                base_score=base_score,
                quality_level=quality_level,
                task_result=task_result,
                empirical_loader=empirical_loader,
            )
            layer_scores["layer_u_understanding"].append(layer_u_score)
            
            # =========== LAYER 3: QUALITY (@q) ===========
            layer_q_score = self._score_layer_quality(
                base_score=base_score,
                quality_level=quality_level,
                task_result=task_result,
                empirical_loader=empirical_loader,
                signal_scorer=signal_scorer,
                enriched_pack=enriched_pack,
            )
            layer_scores["layer_q_quality"].append(layer_q_score)
            
            # =========== LAYER 4: DEVELOPMENT (@d) ===========
            layer_d_score = self._score_layer_development(
                base_score=base_score,
                quality_level=quality_level,
                task_result=task_result,
                empirical_loader=empirical_loader,
            )
            layer_scores["layer_d_development"].append(layer_d_score)
            
            # =========== LAYER 5: PROGRESS (@p) ===========
            layer_p_score = self._score_layer_progress(
                base_score=base_score,
                quality_level=quality_level,
                task_result=task_result,
                empirical_loader=empirical_loader,
            )
            layer_scores["layer_p_progress"].append(layer_p_score)
            
            # =========== LAYER 6: COHERENCE (@C) ===========
            layer_C_score = self._score_layer_coherence(
                base_score=base_score,
                quality_level=quality_level,
                task_result=task_result,
                empirical_loader=empirical_loader,
                all_task_results=task_results,  # For cross-reference
            )
            layer_scores["layer_C_coherence"].append(layer_C_score)
            
            # =========== LAYER 7: CAUSALITY (@chain) ===========
            layer_chain_score = self._score_layer_causality(
                base_score=base_score,
                quality_level=quality_level,
                task_result=task_result,
                empirical_loader=empirical_loader,
            )
            layer_scores["layer_chain_causality"].append(layer_chain_score)
            
            # =========== LAYER 8: CROSS-CUTTING (@cross) ===========
            layer_cross_score = self._score_layer_cross_cutting(
                base_score=base_score,
                quality_level=quality_level,
                task_result=task_result,
                empirical_loader=empirical_loader,
                normative_validator=normative_validator,
                municipality_context=municipality_context,
            )
            layer_scores["layer_cross_cutting"].append(layer_cross_score)
        
        # Validate we have 2400 total scores (300 × 8)
        total_scores = sum(len(scores) for scores in layer_scores.values())
        if total_scores != 2400:
            raise ValueError(
                f"CRITICAL: Expected 2400 layer scores (300 × 8), got {total_scores}"
            )
        
        sub_phase_results["layer_scoring"] = {
            "layers_processed": len(layer_scores),
            "scores_per_layer": {
                layer: len(scores) for layer, scores in layer_scores.items()
            },
            "total_scores": total_scores,
        }
        stage_timings["layer_scoring"] = time.time() - stage_start
        
        # =====================================================================
        # STAGE 5: SIGNAL-ENRICHED ADJUSTMENTS
        # =====================================================================
        stage_start = time.time()
        self.logger.info("phase_3_stage_5_signal_adjustments")
        
        adjusted_scores = {}
        validation_details_all = []
        
        for layer_name, scores in layer_scores.items():
            adjusted_layer = []
            
            for idx, score in enumerate(scores):
                question_id = f"Q{idx+1:03d}"
                quality_level = quality_levels[idx]
                
                # Apply signal-based threshold adjustment
                base_threshold = empirical_loader.get_signal_confidence_threshold(
                    signal_type="GENERIC",
                    extraction_method="default"
                )
                
                adjusted_threshold, threshold_details = signal_scorer.adjust_threshold_for_question(
                    question_id=question_id,
                    base_threshold=base_threshold,
                    score=score,
                    metadata={"layer": layer_name}
                )
                
                # Validate and potentially adjust quality level
                validated_quality, validation_details = signal_scorer.validate_quality_level(
                    question_id=question_id,
                    quality_level=quality_level,
                    score=score,
                    completeness=task_results[idx].result.get("completeness") if idx < len(task_results) else None
                )
                
                validation_details["question_id"] = question_id
                validation_details_all.append(validation_details)
                
                adjusted_layer.append({
                    "score": score,
                    "adjusted_threshold": adjusted_threshold,
                    "quality_level": validated_quality,
                    "adjustments": threshold_details,
                })
            
            adjusted_scores[layer_name] = adjusted_layer
        
        # Generate quality promotion report
        quality_report = generate_quality_promotion_report(validation_details_all)
        
        sub_phase_results["signal_adjustments"] = {
            "threshold_adjustments_applied": sum(
                1 for d in validation_details_all if d.get("adjustments")
            ),
            "quality_promotions": quality_report["summary"]["promotions"],
            "quality_demotions": quality_report["summary"]["demotions"],
        }
        stage_timings["signal_adjustments"] = time.time() - stage_start
        
        # =====================================================================
        # STAGE 6: COMPILE SCORED RESULTS
        # =====================================================================
        stage_start = time.time()
        self.logger.info("phase_3_stage_6_compile_results")
        
        # Create structured output for Phase 4
        scored_micro_questions = []
        
        for idx in range(300):
            question_id = f"Q{idx+1:03d}"
            
            scored_question = {
                "question_id": question_id,
                "question_global": idx + 1,
                "layer_scores": {
                    layer: adjusted_scores[layer][idx]["score"]
                    for layer in layer_scores.keys()
                },
                "quality_level": adjusted_scores["layer_b_baseline"][idx]["quality_level"],
                "metadata": {
                    "phase3_timestamp": datetime.utcnow().isoformat(),
                    "empirical_corpus_version": empirical_loader.corpus.get("calibration_config_version"),
                    "signal_adjusted": signal_registry is not None,
                }
            }
            scored_micro_questions.append(scored_question)
        
        # Calculate layer statistics
        layer_statistics = {}
        for layer_name, scores in layer_scores.items():
            layer_statistics[layer_name] = {
                "mean": sum(scores) / len(scores),
                "min": min(scores),
                "max": max(scores),
                "count": len(scores),
            }
        
        phase3_output = {
            "scored_micro_questions": scored_micro_questions,
            "layer_scores": layer_scores,
            "layer_statistics": layer_statistics,
            "quality_report": quality_report,
            "validation_summary": validation_counters.__dict__,
            "scored_results": scored_micro_questions,  # Alias for Phase 4 compatibility
        }
        
        sub_phase_results["compilation"] = {
            "scored_questions": len(scored_micro_questions),
            "layers_compiled": len(layer_scores),
            "statistics_computed": True,
        }
        stage_timings["compilation"] = time.time() - stage_start
        
        # =====================================================================
        # FINAL: Log validation summary and store results
        # =====================================================================
        
        validation_counters.log_summary()
        
        # Store results
        self.context.phase_results[PhaseID.PHASE_3].sub_phase_results = sub_phase_results
        self.context.phase_results[PhaseID.PHASE_3].stage_timings = stage_timings
        
        self.logger.critical(
            "PHASE 3 COMPLETE - 8-LAYER SCORING SUCCESS",
            questions_scored=len(scored_micro_questions),
            total_layer_scores=total_scores,
            layers=list(layer_scores.keys()),
            quality_promotions=quality_report["summary"]["promotions"],
            validation_issues={
                "missing_evidence": validation_counters.missing_evidence,
                "out_of_bounds": validation_counters.out_of_bounds_scores,
                "invalid_quality": validation_counters.invalid_quality_levels,
            },
            total_time_seconds=sum(stage_timings.values()),
        )
        
        return phase3_output
    
    # =========================================================================
    # LAYER SCORING METHODS
    # =========================================================================
    
    def _score_layer_baseline(
        self, base_score: float, quality_level: str, task_result: Any, empirical_loader: Any
    ) -> float:
        """Score Layer 1: Baseline (@b) - Basic presence and structure."""
        weights = empirical_loader.get_phase3_layer_weights("layer_b_baseline")
        
        # Baseline focuses on existence and basic completeness
        if quality_level == "EXCELENTE":
            return min(1.0, base_score * weights.get("excelente_multiplier", 1.0))
        elif quality_level == "ACEPTABLE":
            return base_score * weights.get("aceptable_multiplier", 0.85)
        else:
            return base_score * weights.get("insuficiente_multiplier", 0.7)
    
    def _score_layer_understanding(
        self, base_score: float, quality_level: str, task_result: Any, empirical_loader: Any
    ) -> float:
        """Score Layer 2: Understanding (@u) - Comprehension depth."""
        weights = empirical_loader.get_phase3_layer_weights("layer_u_understanding")
        
        # Check for comprehension indicators
        evidence = getattr(task_result, "evidence", {})
        has_context = "context" in evidence
        has_rationale = "rationale" in evidence
        
        comprehension_bonus = 0.0
        if has_context:
            comprehension_bonus += weights.get("context_bonus", 0.05)
        if has_rationale:
            comprehension_bonus += weights.get("rationale_bonus", 0.05)
        
        return min(1.0, base_score + comprehension_bonus)
    
    def _score_layer_quality(
        self, base_score: float, quality_level: str, task_result: Any, 
        empirical_loader: Any, signal_scorer: Any, enriched_pack: Any
    ) -> float:
        """Score Layer 3: Quality (@q) - Evidence quality with signal enrichment."""
        weights = empirical_loader.get_phase3_layer_weights("layer_q_quality")
        
        # Apply signal-based adjustments if available
        if signal_scorer and enriched_pack:
            adjusted_score, adjustment_log = signal_scorer.apply_signal_adjustments(
                raw_score=base_score,
                question_id=getattr(task_result, "question_id", "UNKNOWN"),
                enriched_pack=enriched_pack,
            )
            return adjusted_score
        
        # Fallback to weight-based scoring
        return base_score * weights.get("base_multiplier", 1.0)
    
    def _score_layer_development(
        self, base_score: float, quality_level: str, task_result: Any, empirical_loader: Any
    ) -> float:
        """Score Layer 4: Development (@d) - Implementation maturity."""
        weights = empirical_loader.get_phase3_layer_weights("layer_d_development")
        
        # Check for development indicators
        evidence = getattr(task_result, "evidence", {})
        has_timeline = "timeline" in evidence or "milestones" in evidence
        has_budget = "budget" in evidence or "resources" in evidence
        
        development_score = base_score
        if has_timeline:
            development_score *= weights.get("timeline_multiplier", 1.1)
        if has_budget:
            development_score *= weights.get("budget_multiplier", 1.1)
        
        return min(1.0, development_score)
    
    def _score_layer_progress(
        self, base_score: float, quality_level: str, task_result: Any, empirical_loader: Any
    ) -> float:
        """Score Layer 5: Progress (@p) - Evolution and advancement."""
        weights = empirical_loader.get_phase3_layer_weights("layer_p_progress")
        
        # Check for progress indicators
        evidence = getattr(task_result, "evidence", {})
        has_baseline = "baseline" in evidence
        has_targets = "targets" in evidence or "goals" in evidence
        has_indicators = "indicators" in evidence
        
        progress_score = base_score
        if has_baseline and has_targets:
            progress_score += weights.get("baseline_target_bonus", 0.1)
        if has_indicators:
            progress_score += weights.get("indicators_bonus", 0.05)
        
        return min(1.0, progress_score)
    
    def _score_layer_coherence(
        self, base_score: float, quality_level: str, task_result: Any, 
        empirical_loader: Any, all_task_results: list
    ) -> float:
        """Score Layer 6: Coherence (@C) - Internal consistency."""
        weights = empirical_loader.get_phase3_layer_weights("layer_C_coherence")
        
        # Check coherence with related questions (simplified)
        policy_area = getattr(task_result, "policy_area", None)
        if policy_area:
            # Find other questions in same policy area
            related_scores = [
                getattr(r, "score", 0.0) for r in all_task_results
                if getattr(r, "policy_area", None) == policy_area
            ]
            if related_scores:
                avg_related = sum(related_scores) / len(related_scores)
                deviation = abs(base_score - avg_related)
                coherence_penalty = deviation * weights.get("deviation_penalty", 0.2)
                return max(0.0, base_score - coherence_penalty)
        
        return base_score
    
    def _score_layer_causality(
        self, base_score: float, quality_level: str, task_result: Any, empirical_loader: Any
    ) -> float:
        """Score Layer 7: Causality (@chain) - Causal chain integrity."""
        weights = empirical_loader.get_phase3_layer_weights("layer_chain_causality")
        
        # Check for causal chain elements
        evidence = getattr(task_result, "evidence", {})
        has_causes = "causes" in evidence or "drivers" in evidence
        has_effects = "effects" in evidence or "impacts" in evidence
        has_mechanisms = "mechanisms" in evidence or "processes" in evidence
        
        causal_score = base_score
        chain_completeness = sum([has_causes, has_effects, has_mechanisms]) / 3.0
        causal_score *= (1.0 + chain_completeness * weights.get("chain_bonus", 0.2))
        
        return min(1.0, causal_score)
    
    def _score_layer_cross_cutting(
        self, base_score: float, quality_level: str, task_result: Any, 
        empirical_loader: Any, normative_validator: Any, municipality_context: dict
    ) -> float:
        """Score Layer 8: Cross-cutting (@cross) - Transversal themes."""
        weights = empirical_loader.get_phase3_layer_weights("layer_cross_cutting")
        
        # Extract normative references
        evidence = getattr(task_result, "evidence", {})
        extracted_norms = evidence.get("normative_references", [])
        policy_area = getattr(task_result, "policy_area", "UNKNOWN")
        
        # Validate normative compliance
        if normative_validator and extracted_norms:
            compliance_result = normative_validator.validate_compliance(
                policy_area=policy_area,
                extracted_norms=extracted_norms,
                context=municipality_context,
            )
            
            # Apply compliance score
            compliance_score = compliance_result["score"]
            return base_score * (0.7 + 0.3 * compliance_score)  # 70% base + 30% compliance
        
        return base_score * weights.get("no_compliance_multiplier", 0.85)

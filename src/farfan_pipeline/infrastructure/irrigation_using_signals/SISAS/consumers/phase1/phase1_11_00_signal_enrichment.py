# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase1/phase1_11_00_signal_enrichment.py

from dataclasses import dataclass, field
from typing import Any, Dict, List

from ..base_consumer import BaseConsumer
from ...core.signal import Signal, SignalConfidence
from ...core.contracts import ConsumptionContract


@dataclass
class Phase1SignalEnrichmentConsumer(BaseConsumer):
    """
    Consumidor para signal enrichment en Phase 1.

    Procesa señales de:
    - EMPIRICAL_CORPUS_INDEX.json
    - MC01_structural_markers.json
    - Membership criteria extractors

    Responsabilidad: Enriquecer datos con extracción de membership criteria
    y preparar para procesamiento en fases posteriores.
    
    ENHANCED: Signal aggregation and synthesis for MC01-MC10 extractors.
    """

    consumer_id: str = "phase1_11_00_signal_enrichment.py"
    consumer_phase: str = "phase_01"
    
    # Aggregation state for MC01-MC10 signals
    _mc_signal_buffer: Dict[str, List[Signal]] = field(default_factory=dict)
    _aggregation_window_size: int = 10  # Aggregate every 10 signals

    def __post_init__(self):
        super().__post_init__()

        self.consumption_contract = ConsumptionContract(
            contract_id="CC_PHASE1_ENRICHMENT",
            consumer_id=self.consumer_id,
            consumer_phase=self.consumer_phase,
            subscribed_signal_types=[
                "StructuralAlignmentSignal",
                "EventPresenceSignal",
                "MethodApplicationSignal",
                "AnswerSpecificitySignal"
            ],
            subscribed_buses=["structural_bus", "integrity_bus", "epistemic_bus"],
            context_filters={
                "phase": ["phase_01"],
                "consumer_scope": ["Phase_01"]
            },
            required_capabilities=["can_extract", "can_enrich"]
        )

    def process_signal(self, signal: Signal) -> Dict[str, Any]:
        """
        Procesa señales en Phase 1.

        Enfoque: Análisis de extracción y enriquecimiento
        - Verificar que membership criteria se aplican correctamente
        - Evaluar quality metrics de extracción
        - Identificar gaps en datos empíricos
        - ENHANCED: Aggregate MC01-MC10 signals for synthesis
        """
        result = {
            "signal_id": signal.signal_id,
            "signal_type": signal.signal_type,
            "processed": True,
            "enrichment_analysis": {},
            "quality_score": 0.0
        }

        if signal.signal_type == "MethodApplicationSignal":
            analysis = self._analyze_method_application(signal)
            result["enrichment_analysis"] = analysis
            result["quality_score"] = analysis.get("quality_score", 0.0)
            
            # ENHANCED: Aggregate MC signals for synthesis
            self._aggregate_mc_signal(signal)

        elif signal.signal_type == "AnswerSpecificitySignal":
            analysis = self._analyze_specificity(signal)
            result["enrichment_analysis"] = analysis
            result["quality_score"] = analysis.get("specificity_score", 0.0)

        elif signal.signal_type == "StructuralAlignmentSignal":
            analysis = self._analyze_corpus_structure(signal)
            result["enrichment_analysis"] = analysis

        elif signal.signal_type == "EventPresenceSignal":
            analysis = self._analyze_extraction_presence(signal)
            result["enrichment_analysis"] = analysis

        return result
    
    def _aggregate_mc_signal(self, signal: Signal):
        """
        SIGNAL AGGREGATION: Buffer MC01-MC10 signals for synthesis.
        
        Collects multiple extraction signals and triggers synthesis when
        aggregation window is full. This provides a unified view of all
        membership criteria extractors rather than treating them independently.
        """
        method_id = getattr(signal, 'method_id', '')
        
        # Check if this is an MC extractor signal
        if method_id.startswith('MC') or any(mc in method_id for mc in ['MC01', 'MC02', 'MC03', 'MC04', 'MC05', 
                                                                          'MC06', 'MC07', 'MC08', 'MC09', 'MC10']):
            question_id = getattr(signal, 'question_id', 'unknown')
            
            if question_id not in self._mc_signal_buffer:
                self._mc_signal_buffer[question_id] = []
            
            self._mc_signal_buffer[question_id].append(signal)
            
            # Check if we should trigger synthesis
            if len(self._mc_signal_buffer[question_id]) >= self._aggregation_window_size:
                self._synthesize_mc_signals(question_id)
    
    def _synthesize_mc_signals(self, question_id: str) -> Dict[str, Any]:
        """
        SIGNAL SYNTHESIS: Aggregate MC01-MC10 signals into unified extraction summary.
        
        Instead of 10 independent signals, produce one ConsistencySignal that
        synthesizes the overall extraction quality and completeness for a question.
        
        Args:
            question_id: Question whose signals to synthesize
            
        Returns:
            Synthesis result with aggregated metrics
        """
        signals = self._mc_signal_buffer.get(question_id, [])
        if not signals:
            return {}
        
        synthesis = {
            "question_id": question_id,
            "total_extractors": len(signals),
            "successful_extractors": 0,
            "failed_extractors": 0,
            "total_extractions": 0,
            "average_quality": 0.0,
            "consistency_score": 0.0,
            "extractor_breakdown": {}
        }
        
        quality_scores = []
        
        for sig in signals:
            method_id = getattr(sig, 'method_id', 'unknown')
            successful = getattr(sig, 'extraction_successful', False)
            extracted = getattr(sig, 'extracted_values', [])
            
            if successful:
                synthesis["successful_extractors"] += 1
            else:
                synthesis["failed_extractors"] += 1
            
            synthesis["total_extractions"] += len(extracted)
            
            # Calculate quality score for this signal
            quality = 1.0 if successful and extracted else (0.5 if successful else 0.0)
            quality_scores.append(quality)
            
            synthesis["extractor_breakdown"][method_id] = {
                "successful": successful,
                "extraction_count": len(extracted),
                "quality": quality
            }
        
        # Calculate aggregate metrics
        synthesis["average_quality"] = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        # Consistency score: How consistent are extractors in finding data?
        # High if most extractors succeed or most fail (consistent), low if mixed
        success_rate = synthesis["successful_extractors"] / len(signals) if signals else 0
        synthesis["consistency_score"] = 1.0 - abs(0.5 - success_rate) * 2  # Peak at 0.5, drops to 0 at extremes
        
        # Clear buffer after synthesis
        self._mc_signal_buffer[question_id] = []
        
        return synthesis
    
    def get_aggregation_stats(self) -> Dict[str, Any]:
        """
        Get statistics about signal aggregation.
        
        Returns:
            Dict with aggregation metrics
        """
        return {
            "questions_buffered": len(self._mc_signal_buffer),
            "total_signals_buffered": sum(len(sigs) for sigs in self._mc_signal_buffer.values()),
            "aggregation_window_size": self._aggregation_window_size,
            "questions_ready_for_synthesis": sum(
                1 for sigs in self._mc_signal_buffer.values() 
                if len(sigs) >= self._aggregation_window_size
            )
        }

    def _analyze_method_application(self, signal: Signal) -> Dict[str, Any]:
        """Analiza aplicación de métodos de extracción"""
        method_id = getattr(signal, 'method_id', '')
        successful = getattr(signal, 'extraction_successful', False)
        extracted = getattr(signal, 'extracted_values', [])
        processing_time = getattr(signal, 'processing_time_ms', 0.0)

        quality_score = 1.0 if successful and extracted else 0.0
        if successful and not extracted:
            quality_score = 0.5  # Method ran but found nothing

        insights = []
        if not successful:
            insights.append(f"Extraction method {method_id} failed")
        if processing_time > 1000:
            insights.append(f"Slow extraction ({processing_time:.0f}ms)")
        if successful and len(extracted) > 10:
            insights.append(f"Rich extraction - {len(extracted)} values found")

        return {
            "method_id": method_id,
            "successful": successful,
            "extracted_count": len(extracted),
            "extracted_values": extracted[:5],  # Sample
            "processing_time_ms": processing_time,
            "quality_score": quality_score,
            "insights": insights
        }

    def _analyze_specificity(self, signal: Signal) -> Dict[str, Any]:
        """Analiza especificidad de respuestas"""
        level = str(getattr(signal, 'specificity_level', 'NONE'))
        score = getattr(signal, 'specificity_score', 0.0)
        expected = getattr(signal, 'expected_elements', [])
        found = getattr(signal, 'found_elements', [])
        missing = getattr(signal, 'missing_elements', [])

        insights = []
        if score < 0.3:
            insights.append("Low specificity - needs more detail")
        if missing:
            insights.append(f"Missing {len(missing)} expected elements")
        if score > 0.8:
            insights.append("High specificity - good quality data")

        return {
            "specificity_level": level,
            "specificity_score": score,
            "expected_elements": expected,
            "found_elements": found,
            "missing_elements": missing,
            "coverage": len(found) / len(expected) if expected else 0.0,
            "insights": insights
        }

    def _analyze_corpus_structure(self, signal: Signal) -> Dict[str, Any]:
        """Analiza estructura del corpus empírico"""
        alignment = str(getattr(signal, 'alignment_status', 'UNKNOWN'))
        missing = getattr(signal, 'missing_elements', [])

        return {
            "alignment_status": alignment,
            "missing_elements": missing,
            "is_complete": len(missing) == 0,
            "recommendation": "Add missing corpus elements" if missing else "Corpus structure OK"
        }

    def _analyze_extraction_presence(self, signal: Signal) -> Dict[str, Any]:
        """Analiza presencia de extracciones esperadas"""
        presence = str(getattr(signal, 'presence_status', 'UNKNOWN'))
        count = getattr(signal, 'event_count', 0)

        status = "OK" if count > 0 else "MISSING"

        return {
            "presence_status": presence,
            "event_count": count,
            "status": status,
            "expected_event": getattr(signal, 'expected_event_type', ''),
            "recommendation": "Verify extraction pipeline" if count == 0 else "OK"
        }

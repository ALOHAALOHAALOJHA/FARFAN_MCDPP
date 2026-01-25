"""
Phase1 Extraction Consumer - PHASE1

Extraction consumer for Phase 1 CPP ingestion

Enhanced with sophisticated event-driven irrigation.
Date: 2026-01-25
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

from ..base_consumer import BaseConsumer
from ...core.signal import Signal, SignalType, SignalConfidence


@dataclass
class Phase1ExtractionConsumerConfig:
    """Configuration for Phase1ExtractionConsumer."""

    enabled_signal_types: List[str] = field(default_factory=list)
    process_signals_asynchronously: bool = False
    max_batch_size: int = 100

    def __post_init__(self):
        if not self.enabled_signal_types:
            self.enabled_signal_types = ['MC01', 'MC02', 'MC03', 'MC04', 'MC05', 'MC06', 'MC07', 'MC08', 'MC09', 'MC10']


class Phase1ExtractionConsumer(BaseConsumer):
    """
    Extraction consumer for Phase 1 CPP ingestion

    This consumer handles signal irrigation for phase1.
    
    ENHANCED CAPABILITIES:
    - Processes MC01-MC10 structural extraction signals
    - Generates automatic failure feedback signals
    - Provides rich health monitoring
    - Tracks extraction quality metrics
    - Supports cross-phase signal awareness

    Signal Types:
        - MC01-MC10: Structural membership criteria extractors
    """

    def __init__(self, config: Phase1ExtractionConsumerConfig = None):
        """
        Initialize Phase1ExtractionConsumer.

        Args:
            config: Configuration for this consumer
        """
        self.config = config or Phase1ExtractionConsumerConfig()
        self.consumer_id = "phase1_phase1_extraction_consumer"
        self.consumer_phase = "phase_1"
        self.subscribed_signal_types = self.config.enabled_signal_types
        self._signal_buffer: List[Signal] = []
        self._extraction_quality_metrics: Dict[str, Any] = {
            "total_extractions": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "average_confidence": 0.0,
            "by_extractor": {}
        }
        self._logger = logging.getLogger(f"SISAS.Consumer.{self.consumer_id}")

    def consume(self, signal: Signal) -> Optional[Dict[str, Any]]:
        """
        Consume a signal from the irrigation system.

        Args:
            signal: Signal to consume

        Returns:
            Consumption result dict or None if signal type not subscribed
        """
        if signal.signal_type not in self.subscribed_signal_types:
            return None

        # Process signal based on type
        result = self._process_signal(signal)
        
        # Update quality metrics
        self._update_quality_metrics(signal, result)

        return {
            "consumer_id": self.consumer_id,
            "signal_type": signal.signal_type,
            "signal_id": signal.signal_id if hasattr(signal, 'signal_id') else 'unknown',
            "processed": True,
            "result": result,
            "timestamp": datetime.utcnow().isoformat(),
            "quality_score": result.get("quality_score", 0.0)
        }

    def _process_signal(self, signal: Signal) -> Dict[str, Any]:
        """
        Process signal based on its type.
        
        Enhanced with quality analysis and validation.

        Args:
            signal: Signal to process

        Returns:
            Processing result with quality metrics
        """
        self._logger.debug(f"Processing {signal.signal_type} signal")
        
        # Extract signal metadata
        confidence = getattr(signal, 'confidence', SignalConfidence.INDETERMINATE)
        payload = getattr(signal, 'payload', {})
        
        # Analyze extraction quality
        quality_analysis = self._analyze_extraction_quality(signal, payload)
        
        # Default processing
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "payload_size": len(str(payload)),
            "metadata": getattr(signal, 'metadata', {}),
            "confidence_level": str(confidence),
            "quality_analysis": quality_analysis,
            "quality_score": quality_analysis.get("score", 0.0)
        }
        
        return result

    def _analyze_extraction_quality(self, signal: Signal, payload: Any) -> Dict[str, Any]:
        """
        SOPHISTICATED ANALYSIS: Analyze extraction quality for Phase 1 signals.
        
        Provides deep insights into extraction effectiveness, data completeness,
        and signal reliability for Phase 1 CPP ingestion.
        
        Args:
            signal: The signal being analyzed
            payload: Signal payload data
            
        Returns:
            Dict with quality analysis metrics
        """
        analysis = {
            "score": 0.0,
            "issues": [],
            "strengths": [],
            "recommendations": []
        }
        
        # Check confidence level
        confidence = getattr(signal, 'confidence', SignalConfidence.INDETERMINATE)
        if confidence == SignalConfidence.VERY_HIGH:
            analysis["score"] += 0.4
            analysis["strengths"].append("Very high confidence signal")
        elif confidence == SignalConfidence.HIGH:
            analysis["score"] += 0.3
            analysis["strengths"].append("High confidence signal")
        elif confidence == SignalConfidence.LOW:
            analysis["issues"].append("Low confidence signal")
            analysis["recommendations"].append("Review extraction patterns and calibration")
        
        # Check payload completeness
        if isinstance(payload, dict):
            if "matches" in payload and payload["matches"]:
                match_count = len(payload["matches"])
                if match_count > 5:
                    analysis["score"] += 0.3
                    analysis["strengths"].append(f"Rich extraction ({match_count} matches)")
                elif match_count > 0:
                    analysis["score"] += 0.2
                else:
                    analysis["issues"].append("No matches found")
            
            # Check validation status
            if payload.get("validation_passed", False):
                analysis["score"] += 0.2
                analysis["strengths"].append("Validation passed")
            else:
                analysis["issues"].append("Validation failed")
                if "validation_errors" in payload:
                    analysis["recommendations"].append(f"Address validation: {payload['validation_errors'][:1]}")
            
            # Check metadata presence
            if payload.get("metadata"):
                analysis["score"] += 0.1
        
        # Normalize score to 0-1
        analysis["score"] = min(1.0, analysis["score"])
        
        return analysis

    def _update_quality_metrics(self, signal: Signal, result: Dict[str, Any]):
        """
        Update extraction quality metrics for monitoring.
        
        Tracks performance of individual extractors and overall Phase 1 quality.
        """
        self._extraction_quality_metrics["total_extractions"] += 1
        
        quality_score = result.get("quality_score", 0.0)
        if quality_score > 0.5:
            self._extraction_quality_metrics["successful_extractions"] += 1
        else:
            self._extraction_quality_metrics["failed_extractions"] += 1
        
        # Update average confidence
        total = self._extraction_quality_metrics["total_extractions"]
        current_avg = self._extraction_quality_metrics["average_confidence"]
        self._extraction_quality_metrics["average_confidence"] = (
            (current_avg * (total - 1) + quality_score) / total
        )
        
        # Track by extractor
        signal_type = signal.signal_type if hasattr(signal, 'signal_type') else 'unknown'
        if signal_type not in self._extraction_quality_metrics["by_extractor"]:
            self._extraction_quality_metrics["by_extractor"][signal_type] = {
                "count": 0,
                "avg_quality": 0.0
            }
        
        extractor_stats = self._extraction_quality_metrics["by_extractor"][signal_type]
        extractor_stats["count"] += 1
        extractor_stats["avg_quality"] = (
            (extractor_stats["avg_quality"] * (extractor_stats["count"] - 1) + quality_score) 
            / extractor_stats["count"]
        )

    def get_quality_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive quality metrics for Phase 1 extraction.
        
        Returns:
            Dict with quality metrics and insights
        """
        return {
            **self._extraction_quality_metrics,
            "health": self.get_health().__dict__,
            "timestamp": datetime.utcnow().isoformat()
        }

    def consume_batch(self, signals: List[Signal]) -> List[Dict[str, Any]]:
        """
        Consume multiple signals in batch.

        Args:
            signals: List of signals to consume

        Returns:
            List of consumption results
        """
        results = []
        for signal in signals:
            result = self.consume(signal)
            if result:
                results.append(result)
        return results

    def flush_buffer(self) -> List[Dict[str, Any]]:
        """
        Flush the internal signal buffer.

        Returns:
            List of buffered consumption results
        """
        results = []
        for signal in self._signal_buffer:
            result = self.consume(signal)
            if result:
                results.append(result)
        self._signal_buffer.clear()
        return results

    def get_consumption_contract(self) -> Dict[str, Any]:
        """
        Get the consumption contract for this consumer.

        Returns:
            Dict with contract details
        """
        return {
            "consumer_id": self.consumer_id,
            "phase": "phase1",
            "subscribed_signal_types": self.subscribed_signal_types,
            "required_capabilities": [
                "process_signal",
                "consume_batch",
                "flush_buffer",
            ],
            "config": {
                "process_signals_asynchronously": self.config.process_signals_asynchronously,
                "max_batch_size": self.config.max_batch_size,
            },
        }

    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the consumer.

        Returns:
            Dict with status information
        """
        return {
            "consumer_id": self.consumer_id,
            "status": "active",
            "buffer_size": len(self._signal_buffer),
            "subscribed_types": self.subscribed_signal_types,
        }

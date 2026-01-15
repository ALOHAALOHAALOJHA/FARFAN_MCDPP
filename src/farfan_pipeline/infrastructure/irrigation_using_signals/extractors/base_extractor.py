"""
Base Signal Extractor

Abstract base class for all signal-emitting extractors.
Provides common functionality:
- SDO integration
- Provenance tracking
- Metrics collection
- Error handling

Author: F.A.R.F.A.N Pipeline Team
Version: 2.0.0
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import logging

from canonic_questionnaire_central.core.signal import Signal, SignalType, SignalScope, SignalProvenance
from canonic_questionnaire_central.core.signal_distribution_orchestrator import SignalDistributionOrchestrator

logger = logging.getLogger(__name__)


@dataclass
class ExtractionContext:
    """Context for extraction operations."""
    
    source_file: str
    policy_area: str = "UNKNOWN"
    document_id: Optional[str] = None
    section: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractionResult:
    """Result of an extraction operation."""
    
    signals_created: int = 0
    signals_dispatched: int = 0
    signals_delivered: int = 0
    errors: List[str] = field(default_factory=list)
    duration_ms: float = 0.0


class BaseSignalExtractor(ABC):
    """
    Abstract base class for signal extractors.
    
    All extractors must:
    1. Define their signal_type
    2. Define required capabilities
    3. Define empirical_availability (from MC calibration)
    4. Implement extract() method
    """
    
    # Subclasses must override these
    SIGNAL_TYPE: SignalType = None
    CAPABILITIES_REQUIRED: List[str] = []
    EMPIRICAL_AVAILABILITY: float = 0.5
    DEFAULT_PHASE: str = "phase_1"
    DEFAULT_SLOT: str = "ALL"
    
    def __init__(self, sdo: SignalDistributionOrchestrator):
        """
        Initialize extractor with SDO.
        
        Args:
            sdo: SignalDistributionOrchestrator for dispatching signals
        """
        self.sdo = sdo
        self._signals_created = 0
        self._signals_dispatched = 0
        self._errors = 0
        
        if self.SIGNAL_TYPE is None:
            raise ValueError(f"{self.__class__.__name__} must define SIGNAL_TYPE")
        
        logger.info(f"Initialized {self.__class__.__name__}", extra={
            "signal_type": self.SIGNAL_TYPE.value,
            "capabilities": self.CAPABILITIES_REQUIRED,
            "empirical_availability": self.EMPIRICAL_AVAILABILITY
        })
    
    @abstractmethod
    def extract(self, text: str, context: ExtractionContext) -> List[Signal]:
        """
        Extract signals from text.
        
        Args:
            text: The text to analyze
            context: Extraction context with metadata
            
        Returns:
            List of created Signal objects
        """
        pass
    
    def extract_and_dispatch(self, text: str, context: ExtractionContext) -> ExtractionResult:
        """
        Extract signals and dispatch through SDO.
        
        This is the main entry point for extraction.
        """
        start_time = datetime.now(timezone.utc)
        result = ExtractionResult()
        
        try:
            signals = self.extract(text, context)
            result.signals_created = len(signals)
            self._signals_created += len(signals)
            
            for signal in signals:
                success = self.sdo.dispatch(signal)
                if success:
                    result.signals_delivered += 1
                result.signals_dispatched += 1
                self._signals_dispatched += 1
            
        except Exception as e:
            result.errors.append(str(e))
            self._errors += 1
            logger.error(f"Extraction error in {self.__class__.__name__}: {e}", exc_info=True)
        
        end_time = datetime.now(timezone.utc)
        result.duration_ms = (end_time - start_time).total_seconds() * 1000
        
        return result
    
    def create_signal(
        self,
        payload: Any,
        context: ExtractionContext,
        slot: Optional[str] = None,
        extraction_pattern: Optional[str] = None,
        enrichment: bool = True
    ) -> Signal:
        """
        Helper to create a properly formatted signal.
        
        Args:
            payload: The extracted data
            context: Extraction context
            slot: Question slot (defaults to DEFAULT_SLOT)
            extraction_pattern: The pattern/rule used for extraction
            enrichment: Whether this adds value beyond raw extraction
        """
        scope = SignalScope(
            phase=self.DEFAULT_PHASE,
            policy_area=context.policy_area,
            slot=slot or self.DEFAULT_SLOT
        )
        
        provenance = SignalProvenance(
            extractor=self.__class__.__name__,
            source_file=context.source_file,
            source_location=context.section,
            extraction_pattern=extraction_pattern
        )
        
        return Signal.create(
            signal_type=self.SIGNAL_TYPE,
            scope=scope,
            payload=payload,
            provenance=provenance,
            capabilities_required=self.CAPABILITIES_REQUIRED,
            empirical_availability=self.EMPIRICAL_AVAILABILITY,
            enrichment=enrichment
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get extractor metrics."""
        return {
            "extractor": self.__class__.__name__,
            "signal_type": self.SIGNAL_TYPE.value,
            "signals_created": self._signals_created,
            "signals_dispatched": self._signals_dispatched,
            "errors": self._errors,
            "success_rate": (
                self._signals_dispatched / self._signals_created 
                if self._signals_created > 0 else 0
            )
        }

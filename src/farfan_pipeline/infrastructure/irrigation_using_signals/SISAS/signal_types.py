"""
Signal Types and Schema for SISAS (Signal-based Information Sharing and Aggregation System).

SPEC REFERENCE: Section 5.2
PURPOSE: Define the unified signal schema for all signal types in the FARFAN pipeline.

Signal Types (10 Membership Criteria):
- MC01: STRUCTURAL_MARKER
- MC02: QUANTITATIVE_TRIPLET
- MC03: NORMATIVE_REFERENCE
- MC04: PROGRAMMATIC_HIERARCHY
- MC05: FINANCIAL_CHAIN
- MC06: POPULATION_DISAGGREGATION
- MC07: TEMPORAL_MARKER
- MC08: CAUSAL_LINK
- MC09: INSTITUTIONAL_ENTITY
- MC10: SEMANTIC_RELATIONSHIP

Additional Types:
- CROSS_CUTTING_THEME
- COHERENCE_SIGNAL
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Optional, Tuple, Dict, List
from datetime import datetime
import hashlib
import json


class SignalType(Enum):
    """Types of signals supported by the SISAS system.
    
    Each signal type corresponds to a Membership Criteria (MC01-MC10)
    as defined in the CQC specification.
    """
    
    # Membership Criteria Signal Types
    STRUCTURAL_MARKER = "structural_marker"           # MC01 - Tables, sections, structure
    QUANTITATIVE_TRIPLET = "quantitative_triplet"     # MC02 - LB + Meta + Year
    NORMATIVE_REFERENCE = "normative_reference"       # MC03 - Laws, decrees, CONPES
    PROGRAMMATIC_HIERARCHY = "programmatic_hierarchy" # MC04 - Eje→Programa→Meta
    FINANCIAL_CHAIN = "financial_chain"               # MC05 - Monto→Fuente→Programa
    POPULATION_DISAGGREGATION = "population_disaggregation"  # MC06 - Groups
    TEMPORAL_MARKER = "temporal_marker"               # MC07 - Dates, periods
    CAUSAL_LINK = "causal_link"                       # MC08 - Cause-effect verbs
    INSTITUTIONAL_ENTITY = "institutional_entity"     # MC09 - DNP, DANE, etc.
    SEMANTIC_RELATIONSHIP = "semantic_relationship"   # MC10 - Embeddings, similarity
    
    # Cross-cutting
    CROSS_CUTTING_THEME = "cross_cutting_theme"
    
    # Aggregated signals
    COHERENCE_SIGNAL = "coherence_signal"
    
    @classmethod
    def from_mc_id(cls, mc_id: str) -> "SignalType":
        """Convert membership criteria ID to signal type."""
        mc_map = {
            "MC01": cls.STRUCTURAL_MARKER,
            "MC02": cls.QUANTITATIVE_TRIPLET,
            "MC03": cls.NORMATIVE_REFERENCE,
            "MC04": cls.PROGRAMMATIC_HIERARCHY,
            "MC05": cls.FINANCIAL_CHAIN,
            "MC06": cls.POPULATION_DISAGGREGATION,
            "MC07": cls.TEMPORAL_MARKER,
            "MC08": cls.CAUSAL_LINK,
            "MC09": cls.INSTITUTIONAL_ENTITY,
            "MC10": cls.SEMANTIC_RELATIONSHIP,
        }
        return mc_map.get(mc_id, cls.STRUCTURAL_MARKER)
    
    def to_mc_id(self) -> Optional[str]:
        """Convert signal type to membership criteria ID."""
        mc_map = {
            self.STRUCTURAL_MARKER: "MC01",
            self.QUANTITATIVE_TRIPLET: "MC02",
            self.NORMATIVE_REFERENCE: "MC03",
            self.PROGRAMMATIC_HIERARCHY: "MC04",
            self.FINANCIAL_CHAIN: "MC05",
            self.POPULATION_DISAGGREGATION: "MC06",
            self.TEMPORAL_MARKER: "MC07",
            self.CAUSAL_LINK: "MC08",
            self.INSTITUTIONAL_ENTITY: "MC09",
            self.SEMANTIC_RELATIONSHIP: "MC10",
        }
        return mc_map.get(self)


@dataclass(frozen=True)
class Signal:
    """Immutable signal with complete metadata.
    
    Signals are the atomic units of information flow in SISAS.
    They are produced by extractors (Phase 1) and consumed by
    scorers and aggregators (Phases 2-7).
    
    Attributes:
        signal_id: Unique identifier (format: SIG-{type}-{hash})
        signal_type: Type of signal (from SignalType enum)
        source_chunk_id: ID of the text chunk that produced this signal
        confidence: Confidence score [0.0, 1.0]
        payload: Signal-specific data (varies by signal type)
        producer_node: Name of the extractor that produced this signal
        produced_at: Timestamp of signal creation
        required_capabilities: Capabilities needed to process this signal
        scope_tags: Tags for scope-based filtering
        estimated_value_add: Estimated value contribution [0.0, 1.0]
        parent_signal_ids: IDs of signals this was derived from
    """
    
    signal_id: str
    signal_type: SignalType
    source_chunk_id: str
    confidence: float
    
    payload: Dict[str, Any]
    
    # Provenance
    producer_node: str
    produced_at: datetime = field(default_factory=datetime.now)
    
    # Capabilities required to process (Rule 3)
    required_capabilities: Tuple[str, ...] = field(default_factory=tuple)
    
    # Scope information (Rule 1)
    scope_tags: Tuple[str, ...] = field(default_factory=tuple)
    
    # Value-add estimation (Rule 2)
    estimated_value_add: float = 0.5
    
    # Lineage
    parent_signal_ids: Tuple[str, ...] = field(default_factory=tuple)
    
    def __hash__(self):
        return hash(self.signal_id)
    
    def __eq__(self, other):
        if isinstance(other, Signal):
            return self.signal_id == other.signal_id
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert signal to dictionary for serialization."""
        return {
            "signal_id": self.signal_id,
            "signal_type": self.signal_type.value,
            "source_chunk_id": self.source_chunk_id,
            "confidence": self.confidence,
            "payload": self.payload,
            "producer_node": self.producer_node,
            "produced_at": self.produced_at.isoformat() if isinstance(self.produced_at, datetime) else str(self.produced_at),
            "required_capabilities": list(self.required_capabilities),
            "scope_tags": list(self.scope_tags),
            "estimated_value_add": self.estimated_value_add,
            "parent_signal_ids": list(self.parent_signal_ids)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Signal":
        """Create signal from dictionary."""
        return cls(
            signal_id=data["signal_id"],
            signal_type=SignalType(data["signal_type"]),
            source_chunk_id=data["source_chunk_id"],
            confidence=data["confidence"],
            payload=data["payload"],
            producer_node=data["producer_node"],
            produced_at=datetime.fromisoformat(data["produced_at"]) if isinstance(data["produced_at"], str) else data["produced_at"],
            required_capabilities=tuple(data.get("required_capabilities", [])),
            scope_tags=tuple(data.get("scope_tags", [])),
            estimated_value_add=data.get("estimated_value_add", 0.5),
            parent_signal_ids=tuple(data.get("parent_signal_ids", []))
        )
    
    def with_updated_confidence(self, new_confidence: float) -> "Signal":
        """Create a new signal with updated confidence (immutable update)."""
        return Signal(
            signal_id=self.signal_id,
            signal_type=self.signal_type,
            source_chunk_id=self.source_chunk_id,
            confidence=new_confidence,
            payload=self.payload,
            producer_node=self.producer_node,
            produced_at=self.produced_at,
            required_capabilities=self.required_capabilities,
            scope_tags=self.scope_tags,
            estimated_value_add=self.estimated_value_add,
            parent_signal_ids=self.parent_signal_ids
        )


class SignalFactory:
    """Factory for creating properly formatted signals.
    
    Ensures all signals follow the SISAS schema and have
    appropriate IDs, capabilities, and value-add estimates.
    """
    
    # Mapping of signal types to required capabilities
    CAPABILITY_MAP = {
        SignalType.STRUCTURAL_MARKER: ("TABLE_PARSING",),
        SignalType.QUANTITATIVE_TRIPLET: ("NUMERIC_PARSING",),
        SignalType.NORMATIVE_REFERENCE: ("NER_EXTRACTION",),
        SignalType.PROGRAMMATIC_HIERARCHY: (),
        SignalType.FINANCIAL_CHAIN: ("NUMERIC_PARSING", "FINANCIAL_ANALYSIS"),
        SignalType.POPULATION_DISAGGREGATION: (),
        SignalType.TEMPORAL_MARKER: ("TEMPORAL_REASONING",),
        SignalType.CAUSAL_LINK: ("CAUSAL_INFERENCE", "GRAPH_CONSTRUCTION"),
        SignalType.INSTITUTIONAL_ENTITY: ("NER_EXTRACTION",),
        SignalType.SEMANTIC_RELATIONSHIP: ("SEMANTIC_PROCESSING", "GRAPH_CONSTRUCTION"),
        SignalType.CROSS_CUTTING_THEME: ("SEMANTIC_PROCESSING",),
        SignalType.COHERENCE_SIGNAL: (),
    }
    
    # Base value-add estimates by signal type (from corpus_thresholds_weights.json)
    VALUE_ADD_MAP = {
        SignalType.STRUCTURAL_MARKER: 0.15,
        SignalType.QUANTITATIVE_TRIPLET: 0.25,
        SignalType.NORMATIVE_REFERENCE: 0.18,
        SignalType.PROGRAMMATIC_HIERARCHY: 0.10,
        SignalType.FINANCIAL_CHAIN: 0.20,
        SignalType.POPULATION_DISAGGREGATION: 0.12,
        SignalType.TEMPORAL_MARKER: 0.02,
        SignalType.CAUSAL_LINK: 0.15,
        SignalType.INSTITUTIONAL_ENTITY: 0.10,
        SignalType.SEMANTIC_RELATIONSHIP: 0.03,
        SignalType.CROSS_CUTTING_THEME: 0.12,
        SignalType.COHERENCE_SIGNAL: 0.08,
    }
    
    _counter = 0
    
    @classmethod
    def _generate_id(cls, signal_type: SignalType, payload: Dict) -> str:
        """Generate unique signal ID."""
        cls._counter += 1
        content = f"{signal_type.value}:{cls._counter}:{json.dumps(payload, sort_keys=True)}"
        hash_part = hashlib.sha256(content.encode()).hexdigest()[:8]
        return f"SIG-{signal_type.value.upper()[:4]}-{hash_part}"
    
    @classmethod
    def create(
        cls,
        signal_type: SignalType,
        source_chunk_id: str,
        confidence: float,
        payload: Dict[str, Any],
        producer_node: str,
        scope_tags: Optional[Tuple[str, ...]] = None,
        parent_signal_ids: Optional[Tuple[str, ...]] = None,
    ) -> Signal:
        """Create a new signal with proper defaults.
        
        Args:
            signal_type: Type of signal to create
            source_chunk_id: ID of source text chunk
            confidence: Confidence score [0.0, 1.0]
            payload: Signal-specific data
            producer_node: Name of producing extractor
            scope_tags: Optional scope tags for filtering
            parent_signal_ids: Optional parent signal IDs for lineage
        
        Returns:
            Properly formatted Signal instance
        """
        signal_id = cls._generate_id(signal_type, payload)
        required_caps = cls.CAPABILITY_MAP.get(signal_type, ())
        base_value_add = cls.VALUE_ADD_MAP.get(signal_type, 0.10)
        
        # Adjust value-add based on payload completeness
        value_add = cls._estimate_value_add(signal_type, payload, base_value_add)
        
        return Signal(
            signal_id=signal_id,
            signal_type=signal_type,
            source_chunk_id=source_chunk_id,
            confidence=confidence,
            payload=payload,
            producer_node=producer_node,
            produced_at=datetime.now(),
            required_capabilities=required_caps,
            scope_tags=scope_tags or (),
            estimated_value_add=value_add,
            parent_signal_ids=parent_signal_ids or ()
        )
    
    @classmethod
    def _estimate_value_add(
        cls,
        signal_type: SignalType,
        payload: Dict[str, Any],
        base_value: float
    ) -> float:
        """Estimate value-add based on signal type and payload completeness."""
        
        if signal_type == SignalType.QUANTITATIVE_TRIPLET:
            # Higher value if triplet is complete
            completeness = payload.get("completeness", "BAJO")
            multiplier = {"COMPLETO": 1.2, "ALTO": 1.0, "MEDIO": 0.8, "BAJO": 0.5}
            return min(1.0, base_value * multiplier.get(completeness, 0.8))
        
        elif signal_type == SignalType.FINANCIAL_CHAIN:
            # Higher value if linked to program
            if payload.get("programa_vinculado"):
                return min(1.0, base_value * 1.3)
            return base_value
        
        elif signal_type == SignalType.STRUCTURAL_MARKER:
            # Higher value for PPI tables
            if payload.get("section_context") == "PPI":
                return min(1.0, base_value * 1.5)
            return base_value
        
        elif signal_type == SignalType.NORMATIVE_REFERENCE:
            # Higher value for laws vs articles
            norm_type = payload.get("norm_type", "")
            if norm_type in ("ley", "LEY"):
                return min(1.0, base_value * 1.2)
            return base_value
        
        return base_value


# Type aliases for common signal collections
SignalList = List[Signal]
SignalDict = Dict[str, Signal]
SignalsByType = Dict[SignalType, SignalList]

"""
Capability Validator - REGLA 3 Enforcement

"Information is provided only if the consumer possesses the 
necessary tools and capabilities to use that information effectively."
"""
from enum import Enum
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from pathlib import Path
import json


class SignalCapability(Enum):
    NUMERIC_PARSING = "CAP_NUMERIC_PARSING"
    SEMANTIC_PROCESSING = "CAP_SEMANTIC_PROCESSING"
    GRAPH_CONSTRUCTION = "CAP_GRAPH_CONSTRUCTION"
    TABLE_PARSING = "CAP_TABLE_PARSING"
    TEMPORAL_REASONING = "CAP_TEMPORAL_REASONING"
    CAUSAL_INFERENCE = "CAP_CAUSAL_INFERENCE"
    FINANCIAL_ANALYSIS = "CAP_FINANCIAL_ANALYSIS"
    NER_EXTRACTION = "CAP_NER_EXTRACTION"


class SignalType(Enum):
    STRUCTURAL_MARKER = "STRUCTURAL_MARKER"
    QUANTITATIVE_TRIPLET = "QUANTITATIVE_TRIPLET"
    NORMATIVE_REFERENCE = "NORMATIVE_REFERENCE"
    PROGRAMMATIC_HIERARCHY = "PROGRAMMATIC_HIERARCHY"
    FINANCIAL_CHAIN = "FINANCIAL_CHAIN"
    POPULATION_DISAGGREGATION = "POPULATION_DISAGGREGATION"
    TEMPORAL_MARKER = "TEMPORAL_MARKER"
    CAUSAL_LINK = "CAUSAL_LINK"
    INSTITUTIONAL_ENTITY = "INSTITUTIONAL_ENTITY"
    SEMANTIC_RELATIONSHIP = "SEMANTIC_RELATIONSHIP"


@dataclass
class CapabilityValidationResult:
    is_valid: bool
    consumer_id: str
    signal_type: str
    required_capabilities: List[str]
    consumer_capabilities: List[str]
    missing_capabilities: List[str]
    message: str


class CapabilityValidator:
    """Validates consumer capabilities against signal requirements."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path(__file__).parent.parent.parent / "_registry" / "capabilities"
        self._load_config()
    
    def _load_config(self):
        map_file = self.config_path / "signal_capability_map.json"
        if map_file.exists():
            with open(map_file) as f:
                data = json.load(f)
                # Extract required capabilities from the signal_capability_requirements structure
                self.signal_capability_map = {}
                for signal_type, requirements in data.get("signal_capability_requirements", {}).items():
                    self.signal_capability_map[signal_type] = requirements.get("required", [])
        else:
            self.signal_capability_map = self._default_map()
    
    def _default_map(self) -> Dict[str, List[str]]:
        return {
            "STRUCTURAL_MARKER": ["TABLE_PARSING"],
            "QUANTITATIVE_TRIPLET": ["NUMERIC_PARSING"],
            "NORMATIVE_REFERENCE": ["NER_EXTRACTION"],
            "PROGRAMMATIC_HIERARCHY": ["GRAPH_CONSTRUCTION"],
            "FINANCIAL_CHAIN": ["NUMERIC_PARSING", "FINANCIAL_ANALYSIS"],
            "POPULATION_DISAGGREGATION": ["NER_EXTRACTION"],
            "TEMPORAL_MARKER": ["TEMPORAL_REASONING"],
            "CAUSAL_LINK": ["CAUSAL_INFERENCE", "GRAPH_CONSTRUCTION"],
            "INSTITUTIONAL_ENTITY": ["NER_EXTRACTION"],
            "SEMANTIC_RELATIONSHIP": ["SEMANTIC_PROCESSING", "GRAPH_CONSTRUCTION"]
        }
    
    def validate(self, consumer_id: str, consumer_capabilities: List[str], signal_type: str) -> CapabilityValidationResult:
        required = set(self.signal_capability_map.get(signal_type, []))
        has = set(consumer_capabilities)
        missing = required - has
        
        return CapabilityValidationResult(
            is_valid=len(missing) == 0,
            consumer_id=consumer_id,
            signal_type=signal_type,
            required_capabilities=list(required),
            consumer_capabilities=consumer_capabilities,
            missing_capabilities=list(missing),
            message=f"PASS" if len(missing) == 0 else f"MISSING: {missing}"
        )
    
    def can_process(self, consumer_capabilities: List[str], signal_type: str) -> bool:
        required = set(self.signal_capability_map.get(signal_type, []))
        return required.issubset(set(consumer_capabilities))
    
    def get_processable_signals(self, consumer_capabilities: List[str]) -> Set[str]:
        result = set()
        for signal_type in self.signal_capability_map:
            if self.can_process(consumer_capabilities, signal_type):
                result.add(signal_type)
        return result

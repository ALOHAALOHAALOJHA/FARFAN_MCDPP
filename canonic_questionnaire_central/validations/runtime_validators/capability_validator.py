"""
Capability Validator for SISAS Signal Processing.

Implements Rule 3: Tool Capability Check
"Information is provided only if the consumer possesses the
necessary tools and capabilities to use that information."
"""

from dataclasses import dataclass, field
from typing import Protocol, Set, List, Any, Optional
from enum import Enum
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class SignalCapability(Enum):
    """Capabilities requeridas para procesar señales."""
    NUMERIC_PARSING = "NUMERIC_PARSING"
    SEMANTIC_PROCESSING = "SEMANTIC_PROCESSING"
    GRAPH_CONSTRUCTION = "GRAPH_CONSTRUCTION"
    TABLE_PARSING = "TABLE_PARSING"
    TEMPORAL_REASONING = "TEMPORAL_REASONING"
    CAUSAL_INFERENCE = "CAUSAL_INFERENCE"
    FINANCIAL_ANALYSIS = "FINANCIAL_ANALYSIS"
    NER_EXTRACTION = "NER_EXTRACTION"


class SignalConsumerProtocol(Protocol):
    """Protocol que todos los consumidores deben implementar."""
    
    @property
    def consumer_id(self) -> str: ...
    
    @property
    def declared_capabilities(self) -> Set[SignalCapability]: ...


@dataclass
class CapabilityValidationResult:
    """Resultado de validación de capabilities."""
    can_process: bool
    consumer_id: str
    signal_type: str
    required_capabilities: Set[str]
    consumer_capabilities: Set[str]
    missing_capabilities: Set[str]
    warnings: List[str] = field(default_factory=list)


class CapabilityValidator:
    """Validador de capabilities (Regla 3)."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self._signal_capability_map: dict[str, dict[str, List[str]]] = {}
        self._load_config(config_path)
        self._validation_log: List[CapabilityValidationResult] = []
    
    def _load_config(self, config_path: Optional[Path]) -> None:
        """Carga el mapeo signal→capabilities."""
        if config_path is None:
            config_path = Path(__file__).resolve().parent.parent.parent / \
                         "_registry/capabilities/signal_capability_map.json"
        
        if config_path.exists():
            with open(config_path) as f:
                data = json.load(f)
                self._signal_capability_map = data.get("signal_capability_requirements", {})
        else:
            self._signal_capability_map = {
                "QUANTITATIVE_TRIPLET": {"required": ["NUMERIC_PARSING"], "optional": []},
                "FINANCIAL_CHAIN": {"required": ["NUMERIC_PARSING", "FINANCIAL_ANALYSIS"], "optional": []},
                "CAUSAL_LINK": {"required": ["CAUSAL_INFERENCE", "GRAPH_CONSTRUCTION"], "optional": []},
                "NORMATIVE_REFERENCE": {"required": ["NER_EXTRACTION"], "optional": []},
                "STRUCTURAL_MARKER": {"required": ["TABLE_PARSING"], "optional": []},
                "TEMPORAL_MARKER": {"required": ["TEMPORAL_REASONING"], "optional": []},
                "SEMANTIC_RELATIONSHIP": {"required": ["SEMANTIC_PROCESSING", "GRAPH_CONSTRUCTION"], "optional": []},
                "POPULATION_DISAGGREGATION": {"required": [], "optional": ["SEMANTIC_PROCESSING"]},
                "PROGRAMMATIC_HIERARCHY": {"required": [], "optional": ["GRAPH_CONSTRUCTION"]},
                "INSTITUTIONAL_ENTITY": {"required": ["NER_EXTRACTION"], "optional": []},
            }
    
    def validate(
        self, 
        consumer: SignalConsumerProtocol, 
        signal_type: str
    ) -> CapabilityValidationResult:
        """Valida si un consumidor puede procesar un tipo de señal."""
        
        requirements = self._signal_capability_map.get(signal_type, {"required": [], "optional": []})
        required_caps = set(requirements.get("required", []))
        consumer_caps = {cap.value for cap in consumer.declared_capabilities}
        
        missing = required_caps - consumer_caps
        
        result = CapabilityValidationResult(
            can_process=len(missing) == 0,
            consumer_id=consumer.consumer_id,
            signal_type=signal_type,
            required_capabilities=required_caps,
            consumer_capabilities=consumer_caps,
            missing_capabilities=missing
        )
        
        optional_caps = set(requirements.get("optional", []))
        missing_optional = optional_caps - consumer_caps
        if missing_optional:
            result.warnings.append(
                f"Missing optional capabilities for enhanced processing: {missing_optional}"
            )
        
        self._validation_log.append(result)
        return result
    
    def can_process(
        self, 
        consumer: SignalConsumerProtocol, 
        signal_type: str
    ) -> bool:
        """Shortcut para verificación rápida."""
        return self.validate(consumer, signal_type).can_process
    
    def get_processable_signal_types(
        self, 
        consumer: SignalConsumerProtocol
    ) -> Set[str]:
        """Retorna todos los signal types que el consumer puede procesar."""
        consumer_caps = {cap.value for cap in consumer.declared_capabilities}
        processable = set()
        
        for signal_type, requirements in self._signal_capability_map.items():
            required_caps = set(requirements.get("required", []))
            if required_caps <= consumer_caps:
                processable.add(signal_type)
        
        return processable
    
    def get_validation_report(self) -> dict[str, Any]:
        """Genera reporte de validaciones realizadas."""
        total = len(self._validation_log)
        passed = sum(1 for r in self._validation_log if r.can_process)
        failed = total - passed
        
        failures_by_consumer = {}
        for r in self._validation_log:
            if not r.can_process:
                if r.consumer_id not in failures_by_consumer:
                    failures_by_consumer[r.consumer_id] = []
                failures_by_consumer[r.consumer_id].append({
                    "signal_type": r.signal_type,
                    "missing": list(r.missing_capabilities)
                })
        
        return {
            "rule": "REGLA_3_TOOL_CAPABILITY_CHECK",
            "total_validations": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / total if total > 0 else 1.0,
            "failures_by_consumer": failures_by_consumer,
            "status": "COMPLIANT" if failed == 0 else "VIOLATIONS_DETECTED"
        }
    
    def reset_log(self) -> None:
        """Limpia el log de validaciones."""
        self._validation_log.clear()

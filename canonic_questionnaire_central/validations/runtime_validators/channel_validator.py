"""
Channel Authenticity and Integrity Validator for SISAS Signal Processing.

Implements Rule 4: Channel Authenticity and Integrity
"All data channels (flows) must be explicit, traceable, governed, and resilient,
supporting observability and change control. Undocumented or implicit flows are prohibited."
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
from pathlib import Path
import json
import hashlib
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ChannelStatus(Enum):
    """Status of a data channel."""
    EXPLICIT = "EXPLICIT"
    IMPLICIT = "IMPLICIT"
    DOCUMENTED = "DOCUMENTED"
    UNDOCUMENTED = "UNDOCUMENTED"
    TRACEABLE = "TRACEABLE"
    NON_TRACEABLE = "NON_TRACEABLE"
    GOVERNED = "GOVERNED"
    UNGOVERNED = "UNGOVERNED"


class ChannelType(Enum):
    """Types of data channels in the system."""
    DIRECT_SIGNAL_FLOW = "DIRECT_SIGNAL_FLOW"
    ENRICHMENT_FLOW = "ENRICHMENT_FLOW"
    AGGREGATION_FLOW = "AGGREGATION_FLOW"
    CROSS_CUTTING_FLOW = "CROSS_CUTTING_FLOW"
    EXTERNAL_DATA_FLOW = "EXTERNAL_DATA_FLOW"
    CONFIGURATION_FLOW = "CONFIGURATION_FLOW"


@dataclass
class DataFlow:
    """Definition of a data flow/channel."""
    
    flow_id: str
    flow_type: ChannelType
    source: str
    destination: str
    data_schema: str
    governance_policy: str
    is_explicit: bool
    is_documented: bool
    is_traceable: bool
    is_governed: bool
    documentation_path: Optional[str] = None
    change_control_id: Optional[str] = None
    observability_endpoint: Optional[str] = None
    resilience_level: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChannelValidationResult:
    """Result of channel validation."""
    valid: bool
    flow_id: str
    flow_type: str
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    compliance_score: float = 0.0
    status_flags: Dict[str, bool] = field(default_factory=dict)


@dataclass
class FlowManifest:
    """Manifest of all data flows in the system."""
    
    manifest_version: str
    generated_at: str
    flows: List[DataFlow]
    flow_registry: Dict[str, DataFlow] = field(default_factory=dict)
    
    def __post_init__(self):
        """Build flow registry from flows list."""
        for flow in self.flows:
            self.flow_registry[flow.flow_id] = flow


class ChannelValidator:
    """Validator for channel authenticity and integrity (Rule 4)."""
    
    def __init__(
        self,
        flow_manifest_path: Optional[Path] = None,
        strict_mode: bool = True,
        require_documentation: bool = True,
        require_change_control: bool = True
    ):
        self._strict_mode = strict_mode
        self._require_documentation = require_documentation
        self._require_change_control = require_change_control
        self._validation_log: List[ChannelValidationResult] = []
        self._violations_count = 0
        self._registered_flows: Dict[str, DataFlow] = {}
        
        # Load flow manifest
        if flow_manifest_path and flow_manifest_path.exists():
            self._load_flow_manifest(flow_manifest_path)
        else:
            self._initialize_default_flows()
    
    def _load_flow_manifest(self, path: Path) -> None:
        """Load flow manifest from JSON file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                manifest = FlowManifest(
                    manifest_version=data.get("manifest_version", "1.0.0"),
                    generated_at=data.get("generated_at", datetime.now().isoformat()),
                    flows=[
                        DataFlow(
                            flow_id=flow["flow_id"],
                            flow_type=ChannelType(flow["flow_type"]),
                            source=flow["source"],
                            destination=flow["destination"],
                            data_schema=flow["data_schema"],
                            governance_policy=flow["governance_policy"],
                            is_explicit=flow.get("is_explicit", False),
                            is_documented=flow.get("is_documented", False),
                            is_traceable=flow.get("is_traceable", False),
                            is_governed=flow.get("is_governed", False),
                            documentation_path=flow.get("documentation_path"),
                            change_control_id=flow.get("change_control_id"),
                            observability_endpoint=flow.get("observability_endpoint"),
                            resilience_level=flow.get("resilience_level"),
                            metadata=flow.get("metadata", {})
                        )
                        for flow in data.get("flows", [])
                    ]
                )
                self._registered_flows = manifest.flow_registry
        except Exception as e:
            logger.warning(f"Failed to load flow manifest from {path}: {e}")
            self._initialize_default_flows()
    
    def _initialize_default_flows(self) -> None:
        """Initialize default documented flows."""
        default_flows = [
            DataFlow(
                flow_id="SIGNAL_TO_CONSUMER",
                flow_type=ChannelType.DIRECT_SIGNAL_FLOW,
                source="signal_registry",
                destination="signal_consumer",
                data_schema="Signal",
                governance_policy="scope_based_irrigation",
                is_explicit=True,
                is_documented=True,
                is_traceable=True,
                is_governed=True,
                documentation_path="docs/flows/signal_to_consumer.md"
            ),
            DataFlow(
                flow_id="PDET_ENRICHMENT",
                flow_type=ChannelType.ENRICHMENT_FLOW,
                source="colombia_context.pdet_info",
                destination="questionnaire_enrichment",
                data_schema="PdetInfo",
                governance_policy="value_add_validation",
                is_explicit=True,
                is_documented=True,
                is_traceable=True,
                is_governed=True,
                documentation_path="canonic_questionnaire_central/colombia_context/README.md"
            ),
            DataFlow(
                flow_id="MUNICIPAL_CONTEXT_FLOW",
                flow_type=ChannelType.ENRICHMENT_FLOW,
                source="colombia_context.municipal_governance",
                destination="questionnaire_enrichment",
                data_schema="MunicipalGovernance",
                governance_policy="value_add_validation",
                is_explicit=True,
                is_documented=True,
                is_traceable=True,
                is_governed=True,
                documentation_path="canonic_questionnaire_central/colombia_context/README.md"
            ),
        ]
        self._registered_flows = {flow.flow_id: flow for flow in default_flows}
    
    def register_flow(self, flow: DataFlow) -> None:
        """Register a new data flow."""
        if flow.flow_id in self._registered_flows:
            logger.warning(f"Flow {flow.flow_id} already registered. Overwriting.")
        self._registered_flows[flow.flow_id] = flow
    
    def validate_flow(self, flow_id: str, data_payload: Optional[Dict[str, Any]] = None) -> ChannelValidationResult:
        """Validate a specific data flow."""
        
        if flow_id not in self._registered_flows:
            return ChannelValidationResult(
                valid=False,
                flow_id=flow_id,
                flow_type="UNKNOWN",
                violations=[f"Flow {flow_id} is not registered in the flow manifest"],
                compliance_score=0.0,
                status_flags={"registered": False}
            )
        
        flow = self._registered_flows[flow_id]
        violations = []
        warnings = []
        status_flags = {}
        
        # Check explicitness
        status_flags["explicit"] = flow.is_explicit
        if not flow.is_explicit:
            violations.append(f"Flow {flow_id} is implicit - must be explicit")
        
        # Check documentation
        status_flags["documented"] = flow.is_documented
        if self._require_documentation and not flow.is_documented:
            violations.append(f"Flow {flow_id} lacks documentation")
        elif flow.is_documented and not flow.documentation_path:
            warnings.append(f"Flow {flow_id} claims documentation but path is missing")
        
        # Check traceability
        status_flags["traceable"] = flow.is_traceable
        if not flow.is_traceable:
            violations.append(f"Flow {flow_id} is not traceable")
        
        # Check governance
        status_flags["governed"] = flow.is_governed
        if not flow.is_governed:
            violations.append(f"Flow {flow_id} lacks governance policy")
        
        # Check change control
        status_flags["change_controlled"] = flow.change_control_id is not None
        if self._require_change_control and not flow.change_control_id:
            warnings.append(f"Flow {flow_id} has no change control ID")
        
        # Check observability
        status_flags["observable"] = flow.observability_endpoint is not None
        if not flow.observability_endpoint:
            warnings.append(f"Flow {flow_id} has no observability endpoint")
        
        # Check resilience
        status_flags["resilient"] = flow.resilience_level is not None
        if not flow.resilience_level:
            warnings.append(f"Flow {flow_id} has no resilience level defined")
        
        # Validate data payload schema if provided
        if data_payload is not None:
            schema_validation = self._validate_payload_schema(flow, data_payload)
            if not schema_validation["valid"]:
                violations.extend(schema_validation["errors"])
        
        # Calculate compliance score
        required_checks = ["explicit", "documented", "traceable", "governed"]
        passed_checks = sum(1 for check in required_checks if status_flags.get(check, False))
        compliance_score = passed_checks / len(required_checks)
        
        is_valid = len(violations) == 0
        
        result = ChannelValidationResult(
            valid=is_valid,
            flow_id=flow_id,
            flow_type=flow.flow_type.value,
            violations=violations,
            warnings=warnings,
            compliance_score=compliance_score,
            status_flags=status_flags
        )
        
        self._validation_log.append(result)
        
        if not is_valid:
            self._violations_count += 1
        
        return result
    
    def _validate_payload_schema(self, flow: DataFlow, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data payload against expected schema."""
        # Basic schema validation - can be extended with jsonschema
        errors = []
        
        if not isinstance(payload, dict):
            errors.append("Payload must be a dictionary")
            return {"valid": False, "errors": errors}
        
        # Check for required metadata
        if "source" not in payload:
            errors.append("Payload missing 'source' metadata")
        
        if "timestamp" not in payload:
            errors.append("Payload missing 'timestamp' metadata")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    def validate_all_flows(self) -> List[ChannelValidationResult]:
        """Validate all registered flows."""
        results = []
        for flow_id in self._registered_flows.keys():
            result = self.validate_flow(flow_id)
            results.append(result)
        return results
    
    def check_flow_integrity(self, flow_id: str, data_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Check integrity of data flowing through a channel."""
        if flow_id not in self._registered_flows:
            return {
                "valid": False,
                "error": f"Flow {flow_id} not registered"
            }
        
        flow = self._registered_flows[flow_id]
        
        # Compute data hash for traceability
        payload_str = json.dumps(data_payload, sort_keys=True)
        data_hash = hashlib.sha256(payload_str.encode()).hexdigest()[:16]
        
        # Check source matches
        claimed_source = data_payload.get("source", "")
        if claimed_source != flow.source:
            return {
                "valid": False,
                "error": f"Source mismatch: claimed '{claimed_source}', expected '{flow.source}'",
                "data_hash": data_hash
            }
        
        # Check destination matches
        claimed_destination = data_payload.get("destination", "")
        if claimed_destination and claimed_destination != flow.destination:
            return {
                "valid": False,
                "error": f"Destination mismatch: claimed '{claimed_destination}', expected '{flow.destination}'",
                "data_hash": data_hash
            }
        
        return {
            "valid": True,
            "flow_id": flow_id,
            "data_hash": data_hash,
            "timestamp": datetime.now().isoformat(),
            "flow_type": flow.flow_type.value
        }
    
    def get_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance report for Rule 4."""
        total = len(self._validation_log)
        valid = sum(1 for r in self._validation_log if r.valid)
        
        violations_by_flow = {}
        avg_compliance_by_type = {}
        type_counts = {}
        
        for r in self._validation_log:
            if not r.valid:
                violations_by_flow[r.flow_id] = r.violations
            
            # Track compliance by type
            if r.flow_type not in type_counts:
                type_counts[r.flow_type] = {"count": 0, "total_score": 0.0}
            type_counts[r.flow_type]["count"] += 1
            type_counts[r.flow_type]["total_score"] += r.compliance_score
        
        for flow_type, data in type_counts.items():
            avg_compliance_by_type[flow_type] = data["total_score"] / data["count"]
        
        return {
            "rule": "REGLA_4_CHANNEL_AUTHENTICITY_AND_INTEGRITY",
            "total_flows_validated": total,
            "valid_flows": valid,
            "violations": self._violations_count,
            "compliance_rate": valid / total if total > 0 else 1.0,
            "violations_by_flow": violations_by_flow,
            "average_compliance_by_type": avg_compliance_by_type,
            "registered_flows": len(self._registered_flows),
            "status": "COMPLIANT" if self._violations_count == 0 else "VIOLATIONS_DETECTED"
        }
    
    def export_flow_manifest(self, output_path: Path) -> None:
        """Export current flow registry to a manifest file."""
        manifest = {
            "manifest_version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "total_flows": len(self._registered_flows),
            "flows": [
                {
                    "flow_id": flow.flow_id,
                    "flow_type": flow.flow_type.value,
                    "source": flow.source,
                    "destination": flow.destination,
                    "data_schema": flow.data_schema,
                    "governance_policy": flow.governance_policy,
                    "is_explicit": flow.is_explicit,
                    "is_documented": flow.is_documented,
                    "is_traceable": flow.is_traceable,
                    "is_governed": flow.is_governed,
                    "documentation_path": flow.documentation_path,
                    "change_control_id": flow.change_control_id,
                    "observability_endpoint": flow.observability_endpoint,
                    "resilience_level": flow.resilience_level,
                    "metadata": flow.metadata
                }
                for flow in self._registered_flows.values()
            ]
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Flow manifest exported to {output_path}")
    
    def reset_log(self) -> None:
        """Reset validation log."""
        self._validation_log.clear()
        self._violations_count = 0

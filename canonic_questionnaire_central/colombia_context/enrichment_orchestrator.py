"""
Enrichment Orchestrator for PDET Context Integration.

Coordinates the four validation gates for data enrichment:
1. Consumer Scope Validity - Authorization check
2. Value Contribution - Material improvement verification
3. Consumer Capability and Readiness - Technical maturity check
4. Channel Authenticity and Integrity - Traceability and governance

This module orchestrates the enrichment of canonical questionnaire data
with PDET Colombian municipalities context, ensuring compliance with
all governance requirements.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from canonic_questionnaire_central.validations.runtime_validators.scope_validator import (
    ScopeValidator,
    SignalScope,
)
from canonic_questionnaire_central.validations.runtime_validators.value_add_validator import (
    ValueAddScorer,
)
from canonic_questionnaire_central.validations.runtime_validators.capability_validator import (
    CapabilityValidator,
    SignalCapability,
)
from canonic_questionnaire_central.validations.runtime_validators.channel_validator import (
    ChannelValidator,
    DataFlow,
    ChannelType,
)

logger = logging.getLogger(__name__)


@dataclass
class EnrichmentRequest:
    """Request to enrich data with PDET context."""
    
    consumer_id: str
    consumer_scope: SignalScope
    consumer_capabilities: List[SignalCapability]
    target_policy_areas: List[str]
    target_questions: List[str]
    requested_context: List[str]  # e.g., ["municipalities", "subregions", "pillars"]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnrichmentResult:
    """Result of enrichment orchestration."""
    
    request_id: str
    success: bool
    enriched_data: Dict[str, Any]
    validation_results: Dict[str, Any]
    gate_status: Dict[str, bool]
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class EnrichmentOrchestrator:
    """
    Orchestrates PDET context enrichment with four-gate validation.
    
    Validates data enrichment through:
    - Gate 1: Scope-based authorization
    - Gate 2: Value-add verification
    - Gate 3: Capability readiness check
    - Gate 4: Channel authenticity and integrity
    """
    
    def __init__(
        self,
        pdet_data_path: Optional[Path] = None,
        strict_mode: bool = True,
        enable_all_gates: bool = True
    ):
        """
        Initialize enrichment orchestrator.
        
        Args:
            pdet_data_path: Path to PDET municipalities data
            strict_mode: If True, all gates must pass for enrichment
            enable_all_gates: If True, all four gates are enforced
        """
        self._strict_mode = strict_mode
        self._enable_all_gates = enable_all_gates
        
        # Initialize validators (Gates 1-4)
        self._scope_validator = ScopeValidator(strict_mode=strict_mode)
        self._value_add_scorer = ValueAddScorer(min_value_add_threshold=0.10)
        self._capability_validator = CapabilityValidator()
        self._channel_validator = ChannelValidator(strict_mode=strict_mode)
        
        # Register PDET enrichment flow
        self._register_pdet_flow()
        
        # Load PDET data
        self._pdet_data: Dict[str, Any] = {}
        if pdet_data_path and pdet_data_path.exists():
            self._load_pdet_data(pdet_data_path)
        else:
            default_path = Path(__file__).parent.parent / "colombia_context" / "pdet_municipalities.json"
            if default_path.exists():
                self._load_pdet_data(default_path)
        
        self._enrichment_log: List[EnrichmentResult] = []
    
    def _register_pdet_flow(self) -> None:
        """Register PDET enrichment as a data flow in channel validator."""
        pdet_flow = DataFlow(
            flow_id="PDET_MUNICIPALITY_ENRICHMENT",
            flow_type=ChannelType.ENRICHMENT_FLOW,
            source="colombia_context.pdet_municipalities",
            destination="questionnaire_enrichment.canonical_data",
            data_schema="PdetMunicipalityContext",
            governance_policy="four_gate_validation",
            is_explicit=True,
            is_documented=True,
            is_traceable=True,
            is_governed=True,
            documentation_path="canonic_questionnaire_central/colombia_context/README.md",
            change_control_id="CCP-PDET-2024",
            observability_endpoint="/api/enrichment/pdet/metrics",
            resilience_level="HIGH",
            metadata={
                "validation_gates": 4,
                "data_classification": "public_with_restrictions",
                "update_frequency": "quarterly",
                "authoritative_source": "ART/DNP"
            }
        )
        self._channel_validator.register_flow(pdet_flow)
    
    def _load_pdet_data(self, path: Path) -> None:
        """Load PDET municipalities data."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                self._pdet_data = json.load(f)
            logger.info(f"Loaded PDET data from {path}")
        except Exception as e:
            logger.error(f"Failed to load PDET data from {path}: {e}")
            self._pdet_data = {}
    
    def enrich(self, request: EnrichmentRequest) -> EnrichmentResult:
        """
        Enrich data with PDET context through four validation gates.
        
        Args:
            request: Enrichment request with consumer details
            
        Returns:
            EnrichmentResult with enriched data and validation status
        """
        request_id = f"ENR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{request.consumer_id}"
        
        gate_status = {}
        violations = []
        warnings = []
        validation_results = {}
        
        # Gate 1: Consumer Scope Validity
        gate1_result = self._validate_scope(request)
        gate_status["gate_1_scope"] = gate1_result["valid"]
        validation_results["gate_1"] = gate1_result
        if not gate1_result["valid"]:
            violations.extend(gate1_result["violations"])
        
        # Gate 2: Value Contribution
        gate2_result = self._validate_value_add(request)
        gate_status["gate_2_value_add"] = gate2_result["valid"]
        validation_results["gate_2"] = gate2_result
        if not gate2_result["valid"]:
            violations.extend(gate2_result["violations"])
        warnings.extend(gate2_result.get("warnings", []))
        
        # Gate 3: Consumer Capability and Readiness
        gate3_result = self._validate_capability(request)
        gate_status["gate_3_capability"] = gate3_result["valid"]
        validation_results["gate_3"] = gate3_result
        if not gate3_result["valid"]:
            violations.extend(gate3_result["violations"])
        warnings.extend(gate3_result.get("warnings", []))
        
        # Gate 4: Channel Authenticity and Integrity
        gate4_result = self._validate_channel()
        gate_status["gate_4_channel"] = gate4_result["valid"]
        validation_results["gate_4"] = gate4_result
        if not gate4_result["valid"]:
            violations.extend(gate4_result["violations"])
        warnings.extend(gate4_result.get("warnings", []))
        
        # Determine if enrichment can proceed
        all_gates_pass = all(gate_status.values())
        can_enrich = all_gates_pass if self._enable_all_gates else gate_status.get("gate_1_scope", False)
        
        # Perform enrichment if gates pass
        enriched_data = {}
        if can_enrich:
            enriched_data = self._perform_enrichment(request)
        else:
            if self._strict_mode:
                violations.append(
                    f"Enrichment blocked: {sum(1 for v in gate_status.values() if not v)} gate(s) failed"
                )
        
        result = EnrichmentResult(
            request_id=request_id,
            success=can_enrich,
            enriched_data=enriched_data,
            validation_results=validation_results,
            gate_status=gate_status,
            violations=violations,
            warnings=warnings
        )
        
        self._enrichment_log.append(result)
        return result
    
    def _validate_scope(self, request: EnrichmentRequest) -> Dict[str, Any]:
        """Gate 1: Validate consumer scope authorization."""
        # Check if consumer scope includes pdet_context
        required_scope = "pdet_context"
        
        # For this implementation, we check if the consumer has appropriate scope level
        if not request.consumer_scope:
            return {
                "valid": False,
                "gate": "GATE_1_SCOPE_VALIDITY",
                "violations": ["Consumer scope not provided"],
                "required_scope": required_scope
            }
        
        # Check if scope allows PDET enrichment data types
        allowed_types = request.consumer_scope.allowed_signal_types
        if "ENRICHMENT_DATA" not in allowed_types and "*" not in allowed_types:
            return {
                "valid": False,
                "gate": "GATE_1_SCOPE_VALIDITY",
                "violations": [
                    f"Consumer scope does not include 'ENRICHMENT_DATA'. Allowed: {allowed_types}"
                ],
                "required_scope": required_scope
            }
        
        # Check policy area authorization
        if request.consumer_scope.allowed_policy_areas:
            unauthorized_pas = set(request.target_policy_areas) - set(request.consumer_scope.allowed_policy_areas)
            if unauthorized_pas:
                return {
                    "valid": False,
                    "gate": "GATE_1_SCOPE_VALIDITY",
                    "violations": [
                        f"Consumer not authorized for policy areas: {unauthorized_pas}"
                    ],
                    "unauthorized_policy_areas": list(unauthorized_pas)
                }
        
        return {
            "valid": True,
            "gate": "GATE_1_SCOPE_VALIDITY",
            "violations": [],
            "consumer_id": request.consumer_id,
            "authorized_scope": request.consumer_scope.scope_name
        }
    
    def _validate_value_add(self, request: EnrichmentRequest) -> Dict[str, Any]:
        """Gate 2: Verify material value contribution."""
        warnings = []
        
        # Estimate value-add for PDET enrichment
        context_types = request.requested_context
        
        # PDET enrichment provides high value for territorial analysis
        estimated_value = 0.0
        value_breakdown = {}
        
        for context_type in context_types:
            if context_type == "municipalities":
                estimated_value += 0.25  # High value for municipality-level data
                value_breakdown["municipalities"] = 0.25
            elif context_type == "subregions":
                estimated_value += 0.20  # High value for subregion context
                value_breakdown["subregions"] = 0.20
            elif context_type == "pillars":
                estimated_value += 0.15  # Medium-high value for pillar mapping
                value_breakdown["pillars"] = 0.15
            elif context_type == "policy_area_mappings":
                estimated_value += 0.30  # Very high value for PA mappings
                value_breakdown["policy_area_mappings"] = 0.30
            else:
                estimated_value += 0.05
                value_breakdown[context_type] = 0.05
        
        # Check if value exceeds threshold
        threshold = self._value_add_scorer._min_threshold
        provides_value = estimated_value >= threshold
        
        if not provides_value:
            return {
                "valid": False,
                "gate": "GATE_2_VALUE_CONTRIBUTION",
                "violations": [
                    f"Estimated value-add ({estimated_value:.2f}) below threshold ({threshold:.2f})"
                ],
                "warnings": warnings,
                "estimated_value": estimated_value,
                "value_breakdown": value_breakdown
            }
        
        # Check for redundancy
        if "municipalities" in context_types and "subregions" in context_types:
            # Both are valuable, but flag potential redundancy
            warnings.append(
                "Both municipalities and subregions requested - ensure consumer can handle granular data"
            )
        
        return {
            "valid": True,
            "gate": "GATE_2_VALUE_CONTRIBUTION",
            "violations": [],
            "warnings": warnings,
            "estimated_value": estimated_value,
            "value_breakdown": value_breakdown,
            "contribution": "Enables territorial targeting and resource allocation optimization"
        }
    
    def _validate_capability(self, request: EnrichmentRequest) -> Dict[str, Any]:
        """Gate 3: Check consumer technical capability and readiness."""
        warnings = []
        
        # Check for required capabilities
        required_caps = {
            SignalCapability.SEMANTIC_PROCESSING,  # For understanding territorial context
            SignalCapability.TABLE_PARSING,  # For municipality tables
        }
        
        consumer_caps = set(request.consumer_capabilities)
        missing_caps = required_caps - consumer_caps
        
        if missing_caps:
            return {
                "valid": False,
                "gate": "GATE_3_CAPABILITY_READINESS",
                "violations": [
                    f"Consumer lacks required capabilities: {[c.value for c in missing_caps]}"
                ],
                "warnings": warnings,
                "required_capabilities": [c.value for c in required_caps],
                "consumer_capabilities": [c.value for c in consumer_caps],
                "remediation": "Implement SEMANTIC_PROCESSING and TABLE_PARSING capabilities"
            }
        
        # Check for recommended capabilities
        recommended_caps = {
            SignalCapability.GRAPH_CONSTRUCTION,  # For subregion-municipality relationships
            SignalCapability.FINANCIAL_ANALYSIS,  # For OCAD Paz investment data
        }
        
        missing_recommended = recommended_caps - consumer_caps
        if missing_recommended:
            warnings.append(
                f"Consumer missing recommended capabilities: {[c.value for c in missing_recommended]}"
            )
        
        return {
            "valid": True,
            "gate": "GATE_3_CAPABILITY_READINESS",
            "violations": [],
            "warnings": warnings,
            "consumer_capabilities": [c.value for c in consumer_caps],
            "capability_score": len(consumer_caps & (required_caps | recommended_caps)) / len(required_caps | recommended_caps)
        }
    
    def _validate_channel(self) -> Dict[str, Any]:
        """Gate 4: Validate channel authenticity and integrity."""
        # Validate the PDET enrichment flow
        flow_result = self._channel_validator.validate_flow("PDET_MUNICIPALITY_ENRICHMENT")
        
        return {
            "valid": flow_result.valid,
            "gate": "GATE_4_CHANNEL_AUTHENTICITY",
            "violations": flow_result.violations,
            "warnings": flow_result.warnings,
            "compliance_score": flow_result.compliance_score,
            "status_flags": flow_result.status_flags,
            "flow_id": flow_result.flow_id
        }
    
    def _perform_enrichment(self, request: EnrichmentRequest) -> Dict[str, Any]:
        """Perform actual data enrichment."""
        enriched = {
            "source": "colombia_context.pdet_municipalities",
            "enrichment_timestamp": datetime.now().isoformat(),
            "consumer_id": request.consumer_id,
            "data": {}
        }
        
        # Extract requested context
        for context_type in request.requested_context:
            if context_type == "municipalities":
                # Filter municipalities by target policy areas
                enriched["data"]["municipalities"] = self._get_municipalities_for_policy_areas(
                    request.target_policy_areas
                )
            elif context_type == "subregions":
                enriched["data"]["subregions"] = self._get_subregions_for_policy_areas(
                    request.target_policy_areas
                )
            elif context_type == "pillars":
                enriched["data"]["pdet_pillars"] = self._pdet_data.get("overview", {})
            elif context_type == "policy_area_mappings":
                enriched["data"]["policy_area_mappings"] = self._get_policy_area_mappings(
                    request.target_policy_areas
                )
            elif context_type == "statistics":
                enriched["data"]["aggregate_statistics"] = self._pdet_data.get("aggregate_statistics", {})
        
        return enriched
    
    def _get_municipalities_for_policy_areas(self, policy_areas: List[str]) -> List[Dict[str, Any]]:
        """Get municipalities relevant to specified policy areas."""
        municipalities = []
        pa_mappings = self._pdet_data.get("policy_area_mappings", {})
        
        relevant_subregion_ids = set()
        for pa in policy_areas:
            pa_key = f"{pa}" if pa.startswith("PA") else f"PA{pa}"
            pa_data = pa_mappings.get(pa_key, {})
            relevant_subregion_ids.update(pa_data.get("relevant_subregions", []))
        
        # Extract municipalities from relevant subregions
        for subregion in self._pdet_data.get("subregions", []):
            if subregion["subregion_id"] in relevant_subregion_ids:
                municipalities.extend(subregion.get("municipalities", []))
        
        return municipalities
    
    def _get_subregions_for_policy_areas(self, policy_areas: List[str]) -> List[Dict[str, Any]]:
        """Get subregions relevant to specified policy areas."""
        pa_mappings = self._pdet_data.get("policy_area_mappings", {})
        
        relevant_subregion_ids = set()
        for pa in policy_areas:
            pa_key = f"{pa}" if pa.startswith("PA") else f"PA{pa}"
            pa_data = pa_mappings.get(pa_key, {})
            relevant_subregion_ids.update(pa_data.get("relevant_subregions", []))
        
        # Filter subregions
        relevant_subregions = [
            subregion for subregion in self._pdet_data.get("subregions", [])
            if subregion["subregion_id"] in relevant_subregion_ids
        ]
        
        return relevant_subregions
    
    def _get_policy_area_mappings(self, policy_areas: List[str]) -> Dict[str, Any]:
        """Get policy area mappings."""
        pa_mappings = self._pdet_data.get("policy_area_mappings", {})
        
        filtered_mappings = {}
        for pa in policy_areas:
            pa_key = f"{pa}" if pa.startswith("PA") else f"PA{pa}"
            if pa_key in pa_mappings:
                filtered_mappings[pa_key] = pa_mappings[pa_key]
        
        return filtered_mappings
    
    def get_enrichment_report(self) -> Dict[str, Any]:
        """Generate comprehensive enrichment report."""
        total_requests = len(self._enrichment_log)
        successful = sum(1 for r in self._enrichment_log if r.success)
        
        gate_failures = {
            "gate_1": 0,
            "gate_2": 0,
            "gate_3": 0,
            "gate_4": 0
        }
        
        for result in self._enrichment_log:
            for gate_key, passed in result.gate_status.items():
                if not passed:
                    gate_number = gate_key.split("_")[1]
                    gate_failures[f"gate_{gate_number}"] += 1
        
        return {
            "enrichment_orchestrator_report": {
                "total_requests": total_requests,
                "successful_enrichments": successful,
                "failed_enrichments": total_requests - successful,
                "success_rate": successful / total_requests if total_requests > 0 else 1.0,
                "gate_failure_counts": gate_failures,
                "strict_mode": self._strict_mode,
                "all_gates_enabled": self._enable_all_gates
            },
            "gate_1_scope_validator": self._scope_validator.get_compliance_report(),
            "gate_2_value_add_scorer": self._value_add_scorer.get_report(),
            "gate_3_capability_validator": self._capability_validator.get_validation_report(),
            "gate_4_channel_validator": self._channel_validator.get_compliance_report()
        }
    
    def export_enrichment_log(self, output_path: Path) -> None:
        """Export enrichment log to JSON file."""
        log_data = {
            "log_version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "total_enrichments": len(self._enrichment_log),
            "enrichments": [
                {
                    "request_id": r.request_id,
                    "success": r.success,
                    "gate_status": r.gate_status,
                    "violations_count": len(r.violations),
                    "warnings_count": len(r.warnings),
                    "timestamp": r.timestamp
                }
                for r in self._enrichment_log
            ]
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Enrichment log exported to {output_path}")

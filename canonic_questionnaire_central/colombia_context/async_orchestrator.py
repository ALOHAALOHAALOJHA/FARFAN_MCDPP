"""
Async Enrichment Orchestrator with Parallel Gate Validation

Provides async/await support for concurrent gate validation and
non-blocking I/O operations for improved performance.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

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
)
from canonic_questionnaire_central.colombia_context.context_providers import (
    get_context_factory,
    EnrichmentContext,
)

logger = logging.getLogger(__name__)


@dataclass
class AsyncEnrichmentRequest:
    """Request for async enrichment."""

    consumer_id: str
    consumer_scope: SignalScope
    consumer_capabilities: List[SignalCapability]
    target_policy_areas: List[str]
    target_questions: List[str]
    requested_context: List[str]
    context_provider: str = "PDET_Colombia"
    metadata: Dict[str, Any] = field(default_factory=dict)
    timeout: float = 30.0  # seconds


@dataclass
class AsyncEnrichmentResult:
    """Result of async enrichment."""

    request_id: str
    success: bool
    enriched_data: Dict[str, Any]
    validation_results: Dict[str, Any]
    gate_status: Dict[str, bool]
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class AsyncEnrichmentOrchestrator:
    """
    Async orchestrator for parallel gate validation.

    Validates gates concurrently for improved performance while
    maintaining data governance compliance.
    """

    def __init__(
        self,
        strict_mode: bool = True,
        enable_all_gates: bool = True,
        max_concurrent_validations: int = 4,
    ):
        self._strict_mode = strict_mode
        self._enable_all_gates = enable_all_gates
        self._max_concurrent = max_concurrent_validations

        # Initialize validators
        self._scope_validator = ScopeValidator(strict_mode=strict_mode)
        self._value_add_scorer = ValueAddScorer()
        self._capability_validator = CapabilityValidator()
        self._channel_validator = ChannelValidator(strict_mode=strict_mode)

        # Get context factory
        self._context_factory = get_context_factory()

        # Performance tracking
        self._enrichment_log: List[AsyncEnrichmentResult] = []

    async def enrich(self, request: AsyncEnrichmentRequest) -> AsyncEnrichmentResult:
        """
        Enrich data asynchronously with parallel gate validation.

        Args:
            request: Async enrichment request

        Returns:
            AsyncEnrichmentResult with enriched data
        """
        start_time = datetime.now()
        request_id = f"ASYNC_ENR_{start_time.strftime('%Y%m%d_%H%M%S')}_{request.consumer_id}"

        try:
            # Create validation tasks
            validation_tasks = [
                self._validate_scope_async(request),
                self._validate_value_add_async(request),
                self._validate_capability_async(request),
                self._validate_channel_async(),
            ]

            # Run gates in parallel with timeout
            gate_results = await asyncio.wait_for(
                asyncio.gather(*validation_tasks, return_exceptions=True), timeout=request.timeout
            )

            # Process results
            gate_status = {}
            validation_results = {}
            violations = []
            warnings = []

            gate_names = ["gate_1_scope", "gate_2_value_add", "gate_3_capability", "gate_4_channel"]

            for i, (name, result) in enumerate(zip(gate_names, gate_results)):
                if isinstance(result, Exception):
                    logger.error(f"Gate {name} failed with exception: {result}")
                    gate_status[name] = False
                    validation_results[name] = {"error": str(result), "valid": False}
                    violations.append(f"Gate {name} encountered error: {result}")
                else:
                    gate_status[name] = result["valid"]
                    validation_results[name] = result
                    if not result["valid"]:
                        violations.extend(result.get("violations", []))
                    warnings.extend(result.get("warnings", []))

            # Determine if enrichment can proceed
            all_gates_pass = all(gate_status.values())
            can_enrich = (
                all_gates_pass if self._enable_all_gates else gate_status.get("gate_1_scope", False)
            )

            # Load enrichment data if gates pass
            enriched_data = {}
            if can_enrich:
                enriched_data = await self._load_enrichment_data_async(request)
            else:
                if self._strict_mode:
                    violations.append(
                        f"Enrichment blocked: {sum(1 for v in gate_status.values() if not v)} gate(s) failed"
                    )

            execution_time = (datetime.now() - start_time).total_seconds()

            result = AsyncEnrichmentResult(
                request_id=request_id,
                success=can_enrich,
                enriched_data=enriched_data,
                validation_results=validation_results,
                gate_status=gate_status,
                violations=violations,
                warnings=warnings,
                execution_time=execution_time,
            )

            self._enrichment_log.append(result)
            return result

        except asyncio.TimeoutError:
            execution_time = (datetime.now() - start_time).total_seconds()
            return AsyncEnrichmentResult(
                request_id=request_id,
                success=False,
                enriched_data={},
                validation_results={},
                gate_status={},
                violations=[f"Enrichment timed out after {request.timeout}s"],
                execution_time=execution_time,
            )
        except Exception as e:
            logger.error(f"Enrichment failed with exception: {e}", exc_info=True)
            execution_time = (datetime.now() - start_time).total_seconds()
            return AsyncEnrichmentResult(
                request_id=request_id,
                success=False,
                enriched_data={},
                validation_results={},
                gate_status={},
                violations=[f"Enrichment error: {str(e)}"],
                execution_time=execution_time,
            )

    async def _validate_scope_async(self, request: AsyncEnrichmentRequest) -> Dict[str, Any]:
        """Async Gate 1: Scope validation."""
        # Run in thread pool for CPU-bound work
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._validate_scope_sync, request)

    def _validate_scope_sync(self, request: AsyncEnrichmentRequest) -> Dict[str, Any]:
        """Sync scope validation."""
        required_scope = "pdet_context"

        if not request.consumer_scope:
            return {
                "valid": False,
                "gate": "GATE_1_SCOPE_VALIDITY",
                "violations": ["Consumer scope not provided"],
                "warnings": [],
                "required_scope": required_scope,
            }

        allowed_types = request.consumer_scope.allowed_signal_types
        if "ENRICHMENT_DATA" not in allowed_types and "*" not in allowed_types:
            return {
                "valid": False,
                "gate": "GATE_1_SCOPE_VALIDITY",
                "violations": [
                    f"Consumer scope does not include 'ENRICHMENT_DATA'. Allowed: {allowed_types}"
                ],
                "warnings": [],
                "required_scope": required_scope,
            }

        if request.consumer_scope.allowed_policy_areas:
            unauthorized_pas = set(request.target_policy_areas) - set(
                request.consumer_scope.allowed_policy_areas
            )
            if unauthorized_pas:
                return {
                    "valid": False,
                    "gate": "GATE_1_SCOPE_VALIDITY",
                    "violations": [f"Consumer not authorized for policy areas: {unauthorized_pas}"],
                    "warnings": [],
                    "unauthorized_policy_areas": list(unauthorized_pas),
                }

        return {
            "valid": True,
            "gate": "GATE_1_SCOPE_VALIDITY",
            "violations": [],
            "warnings": [],
            "consumer_id": request.consumer_id,
            "authorized_scope": request.consumer_scope.scope_name,
        }

    async def _validate_value_add_async(self, request: AsyncEnrichmentRequest) -> Dict[str, Any]:
        """Async Gate 2: Value-add validation."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._validate_value_add_sync, request)

    def _validate_value_add_sync(self, request: AsyncEnrichmentRequest) -> Dict[str, Any]:
        """Sync value-add validation."""
        warnings = []
        context_types = request.requested_context

        estimated_value = 0.0
        value_breakdown = {}

        for context_type in context_types:
            if context_type == "municipalities":
                estimated_value += 0.25
                value_breakdown["municipalities"] = 0.25
            elif context_type == "subregions":
                estimated_value += 0.20
                value_breakdown["subregions"] = 0.20
            elif context_type == "pillars":
                estimated_value += 0.15
                value_breakdown["pillars"] = 0.15
            elif context_type == "policy_area_mappings":
                estimated_value += 0.30
                value_breakdown["policy_area_mappings"] = 0.30
            else:
                estimated_value += 0.05
                value_breakdown[context_type] = 0.05

        threshold = self._value_add_scorer._min_threshold
        provides_value = estimated_value >= threshold

        return {
            "valid": provides_value,
            "gate": "GATE_2_VALUE_CONTRIBUTION",
            "violations": (
                []
                if provides_value
                else [
                    f"Estimated value-add ({estimated_value:.2f}) below threshold ({threshold:.2f})"
                ]
            ),
            "warnings": warnings,
            "estimated_value": estimated_value,
            "value_breakdown": value_breakdown,
        }

    async def _validate_capability_async(self, request: AsyncEnrichmentRequest) -> Dict[str, Any]:
        """Async Gate 3: Capability validation."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._validate_capability_sync, request)

    def _validate_capability_sync(self, request: AsyncEnrichmentRequest) -> Dict[str, Any]:
        """Sync capability validation."""
        warnings = []

        required_caps = {SignalCapability.SEMANTIC_PROCESSING, SignalCapability.TABLE_PARSING}
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
                "remediation": "Implement SEMANTIC_PROCESSING and TABLE_PARSING capabilities",
            }

        return {
            "valid": True,
            "gate": "GATE_3_CAPABILITY_READINESS",
            "violations": [],
            "warnings": warnings,
            "consumer_capabilities": [c.value for c in consumer_caps],
        }

    async def _validate_channel_async(self) -> Dict[str, Any]:
        """Async Gate 4: Channel validation."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._validate_channel_sync)

    def _validate_channel_sync(self) -> Dict[str, Any]:
        """Sync channel validation."""
        flow_result = self._channel_validator.validate_flow("PDET_MUNICIPALITY_ENRICHMENT")

        return {
            "valid": flow_result.valid,
            "gate": "GATE_4_CHANNEL_AUTHENTICITY",
            "violations": flow_result.violations,
            "warnings": flow_result.warnings,
            "compliance_score": flow_result.compliance_score,
            "status_flags": flow_result.status_flags,
            "flow_id": flow_result.flow_id,
        }

    async def _load_enrichment_data_async(self, request: AsyncEnrichmentRequest) -> Dict[str, Any]:
        """Load enrichment data asynchronously."""
        loop = asyncio.get_event_loop()

        # Load context using factory
        context = await loop.run_in_executor(
            None,
            self._context_factory.load_context,
            "municipalities",  # context_type
            request.context_provider,
            {"policy_areas": request.target_policy_areas},
        )

        return {
            "source": context.context_id,
            "enrichment_timestamp": datetime.now().isoformat(),
            "consumer_id": request.consumer_id,
            "data": context.data,
            "metadata": context.metadata,
        }

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        if not self._enrichment_log:
            return {"total_requests": 0, "avg_execution_time": 0.0}

        total = len(self._enrichment_log)
        successful = sum(1 for r in self._enrichment_log if r.success)
        exec_times = [r.execution_time for r in self._enrichment_log]

        return {
            "total_requests": total,
            "successful_requests": successful,
            "failed_requests": total - successful,
            "success_rate": successful / total,
            "avg_execution_time": sum(exec_times) / len(exec_times),
            "min_execution_time": min(exec_times),
            "max_execution_time": max(exec_times),
        }

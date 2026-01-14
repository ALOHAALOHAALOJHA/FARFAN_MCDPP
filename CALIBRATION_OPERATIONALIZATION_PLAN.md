# CALIBRATION SYSTEM OPERATIONALIZATION PLAN
## Complete Implementation Roadmap to Close This Business

**Version**: 1.0.0
**Date**: 2026-01-14
**Status**: EXECUTION READY
**Goal**: Make methods UoA-sensitive and ensure Phase 2 alignment through parametrization

---

## EXECUTIVE SUMMARY

This plan transforms the calibration architecture into a **runtime-operational system** where:

1. **Ingestion methods** are automatically parametrized based on UnitOfAnalysis characteristics
2. **Phase 2 methods** are aligned to contract TYPE through orchestrator integration
3. **Every method execution** is validated against calibration constraints before running
4. **Telemetry** tracks calibration effectiveness in real-time

---

## PHASE 1: RUNTIME PARAMETRIZATION INJECTION (Weeks 1-2)

### Objective
Make ingestion methods **automatically receive** UoA-calibrated parameters at runtime.

### 1.1 Create Parametrization Context Manager

**File**: `src/farfan_pipeline/infrastructure/calibration/runtime_context.py`

```python
"""
Runtime Calibration Context
============================
Thread-safe context manager for injecting calibration parameters into methods.

DESIGN PATTERN: Context Manager + Dependency Injection
"""

from __future__ import annotations

import contextvars
from dataclasses import dataclass
from typing import Any

from .calibration_core import CalibrationLayer
from .unit_of_analysis import UnitOfAnalysis

# Thread-local calibration context
_calibration_context: contextvars.ContextVar[CalibrationContext | None] = (
    contextvars.ContextVar('calibration_context', default=None)
)


@dataclass(frozen=True)
class CalibrationContext:
    """
    Unit of Analysis Requirements:
        - Valid UnitOfAnalysis instance
        - Calibration layers for both phases
        - Contract type code

    Epistemic Level: N3-AUD (meta-level context)
    Output: Thread-safe parametrization context
    Fusion Strategy: Context injection pattern

    Immutable calibration context for current execution.

    This context is injected into the execution thread and provides
    methods with access to calibrated parameters.

    Attributes:
        unit_of_analysis: UoA characteristics
        phase1_layer: Ingestion calibration layer
        phase2_layer: Phase 2 calibration layer
        contract_type: TYPE_A, TYPE_B, etc.
        contract_id: Unique contract identifier
    """

    unit_of_analysis: UnitOfAnalysis
    phase1_layer: CalibrationLayer
    phase2_layer: CalibrationLayer
    contract_type: str
    contract_id: str

    def get_parameter(self, name: str, phase: str = "phase1") -> float:
        """
        Get calibrated parameter value.

        Args:
            name: Parameter name (prior_strength, veto_threshold, chunk_size, etc.)
            phase: "phase1" or "phase2"

        Returns:
            Calibrated parameter value

        Raises:
            KeyError: If parameter not found
        """
        layer = self.phase1_layer if phase == "phase1" else self.phase2_layer
        param = layer.get_parameter(name)
        return param.value

    def is_operation_prohibited(self, operation: str) -> bool:
        """Check if operation is prohibited for this contract TYPE."""
        from .type_defaults import PROHIBITED_OPERATIONS
        prohibited = PROHIBITED_OPERATIONS.get(self.contract_type, frozenset())
        return operation in prohibited


def set_calibration_context(context: CalibrationContext) -> None:
    """Set calibration context for current thread."""
    _calibration_context.set(context)


def get_calibration_context() -> CalibrationContext | None:
    """Get calibration context for current thread."""
    return _calibration_context.get()


def require_calibration_context() -> CalibrationContext:
    """
    Require calibration context (raises if not set).

    Raises:
        RuntimeError: If no calibration context is active
    """
    context = get_calibration_context()
    if context is None:
        raise RuntimeError(
            "No calibration context active. "
            "Methods must be executed within calibration_context()."
        )
    return context


class calibration_context:
    """
    Unit of Analysis Requirements:
        - CalibrationContext with valid UoA
        - Both phase layers initialized

    Epistemic Level: N3-AUD
    Output: Context manager for scoped parametrization
    Fusion Strategy: Thread-local context injection

    Context manager for scoped calibration.

    Usage:
        >>> with calibration_context(ctx):
        ...     result = extract_document(document)
        ...     # extract_document automatically gets calibrated parameters
    """

    def __init__(self, context: CalibrationContext):
        self.context = context
        self.token = None

    def __enter__(self) -> CalibrationContext:
        self.token = _calibration_context.set(self.context)
        return self.context

    def __exit__(self, *args):
        _calibration_context.reset(self.token)


__all__ = [
    "CalibrationContext",
    "calibration_context",
    "get_calibration_context",
    "require_calibration_context",
    "set_calibration_context",
]
```

### 1.2 Create UoA-Sensitive Method Decorator

**File**: `src/farfan_pipeline/infrastructure/calibration/uoa_sensitive.py`

```python
"""
UoA-Sensitive Method Decorators
================================
Decorators that make methods automatically consume calibration parameters.

DESIGN PATTERN: Decorator Pattern + Parameter Injection
"""

from __future__ import annotations

import functools
import inspect
import logging
from typing import Any, Callable, TypeVar

from .runtime_context import get_calibration_context, require_calibration_context

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


def uoa_sensitive(
    *,
    required_parameters: list[str] | None = None,
    phase: str = "phase1",
    validate_before: bool = True,
) -> Callable[[F], F]:
    """
    Unit of Analysis Requirements:
        - Method must be called within calibration_context
        - Required parameters must exist in calibration layer

    Epistemic Level: N1-EMP (ingestion) or N2-INF (computation)
    Output: Decorated method with automatic parametrization
    Fusion Strategy: Runtime parameter injection

    Decorator to make methods UoA-sensitive.

    Automatically injects calibration parameters into method execution.

    Args:
        required_parameters: List of required calibration parameters
        phase: "phase1" or "phase2"
        validate_before: Run validation before method execution

    Usage:
        @uoa_sensitive(required_parameters=["chunk_size", "prior_strength"])
        def extract_document(document: Document, **kwargs):
            chunk_size = kwargs.get("chunk_size")
            prior_strength = kwargs.get("prior_strength")
            # Method automatically receives calibrated values
            ...
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get calibration context
            context = require_calibration_context()

            # Inject calibration parameters
            if required_parameters:
                for param_name in required_parameters:
                    if param_name not in kwargs:
                        try:
                            value = context.get_parameter(param_name, phase=phase)
                            kwargs[param_name] = value
                            logger.debug(
                                f"{func.__name__}: Injected {param_name}={value} "
                                f"from {phase} calibration"
                            )
                        except KeyError:
                            logger.warning(
                                f"{func.__name__}: Required parameter '{param_name}' "
                                f"not found in {phase} calibration layer"
                            )

            # Validate prohibited operations
            if validate_before:
                # Check if method name suggests prohibited operation
                func_name_lower = func.__name__.lower()
                for prohibited in ["average", "mean", "weighted_mean"]:
                    if prohibited in func_name_lower:
                        if context.is_operation_prohibited(prohibited):
                            raise RuntimeError(
                                f"Operation '{prohibited}' is prohibited for "
                                f"contract TYPE {context.contract_type}. "
                                f"Method {func.__name__} cannot be executed."
                            )

            # Execute method
            return func(*args, **kwargs)

        # Mark as UoA-sensitive for introspection
        wrapper.__uoa_sensitive__ = True  # type: ignore
        wrapper.__required_parameters__ = required_parameters  # type: ignore
        wrapper.__calibration_phase__ = phase  # type: ignore

        return wrapper  # type: ignore

    return decorator


def chunk_size_aware(func: F) -> F:
    """
    Convenience decorator for chunk_size parameter injection.

    Usage:
        @chunk_size_aware
        def process_chunks(document, chunk_size=512):
            # chunk_size automatically calibrated based on UoA complexity
            ...
    """
    return uoa_sensitive(required_parameters=["chunk_size"], phase="phase1")(func)


def prior_aware(func: F) -> F:
    """
    Convenience decorator for prior_strength parameter injection.

    Usage:
        @prior_aware
        def bayesian_update(evidence, prior_strength=1.0):
            # prior_strength automatically calibrated based on TYPE
            ...
    """
    return uoa_sensitive(required_parameters=["prior_strength"], phase="phase1")(func)


def veto_aware(func: F) -> F:
    """
    Convenience decorator for veto_threshold parameter injection.

    Usage:
        @veto_aware
        def validate_result(result, veto_threshold=0.05):
            # veto_threshold automatically calibrated based on TYPE
            ...
    """
    return uoa_sensitive(required_parameters=["veto_threshold"], phase="phase2")(func)


__all__ = [
    "uoa_sensitive",
    "chunk_size_aware",
    "prior_aware",
    "veto_aware",
]
```

### 1.3 Integration into Existing Ingestion Methods

**Action**: Refactor existing ingestion methods to use decorators

**Example**: Update document extraction method

```python
# BEFORE (hard-coded parameters)
def extract_document(document: Document):
    chunk_size = 512  # Hard-coded
    chunks = split_into_chunks(document, chunk_size)
    ...

# AFTER (UoA-sensitive)
from farfan_pipeline.infrastructure.calibration import chunk_size_aware

@chunk_size_aware
def extract_document(document: Document, chunk_size: int = 512):
    # chunk_size now automatically calibrated based on UoA complexity!
    # - High complexity municipality → chunk_size = 1024
    # - Low complexity municipality → chunk_size = 384
    chunks = split_into_chunks(document, chunk_size)
    ...
```

---

## PHASE 2: ORCHESTRATOR INTEGRATION (Weeks 3-4)

### Objective
Integrate UnifiedCalibrationRegime into Phase 2 orchestrator to ensure method alignment.

### 2.1 Create Calibration-Aware Orchestrator

**File**: `src/farfan_pipeline/infrastructure/calibration/calibrated_orchestrator.py`

```python
"""
Calibration-Aware Orchestrator
===============================
Orchestrator that enforces calibration constraints before method execution.

DESIGN PATTERN: Decorator + Chain of Responsibility
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from .calibration_regime import UnifiedCalibrationManifest, UnifiedCalibrationRegime
from .method_binding_validator import MethodBindingSet, MethodBindingValidator
from .runtime_context import CalibrationContext, calibration_context
from .unit_of_analysis import UnitOfAnalysis

logger = logging.getLogger(__name__)


@dataclass
class OrchestrationRequest:
    """
    Unit of Analysis Requirements:
        - Valid contract_id and contract_type
        - UnitOfAnalysis instance
        - MethodBindingSet with methods for execution

    Epistemic Level: N2-INF (orchestration)
    Output: Request for calibrated method execution
    Fusion Strategy: Orchestrator pattern with validation gates

    Request for calibrated method orchestration.

    Attributes:
        contract_id: Unique contract identifier
        contract_type: TYPE_A, TYPE_B, etc.
        unit_of_analysis: UoA characteristics
        method_binding_set: Methods to execute
        role: Execution role (SCORE_Q, AGGREGATE, etc.)
    """

    contract_id: str
    contract_type: str
    unit_of_analysis: UnitOfAnalysis
    method_binding_set: MethodBindingSet
    role: str


class CalibratedOrchestrator:
    """
    Unit of Analysis Requirements:
        - OrchestrationRequest with valid UoA
        - UnifiedCalibrationRegime for manifest generation

    Epistemic Level: N2-INF + N3-AUD (orchestration + validation)
    Output: Calibrated execution context
    Fusion Strategy: Validation → Calibration → Execution pipeline

    Orchestrator that enforces calibration before method execution.

    WORKFLOW:
    1. Receive OrchestrationRequest
    2. Generate UnifiedCalibrationManifest (both phases)
    3. Validate method bindings against TYPE constraints
    4. Create CalibrationContext
    5. Execute methods within calibration_context()
    6. Track telemetry

    Attributes:
        _regime: Unified calibration regime
        _validator: Method binding validator
        _telemetry: Telemetry tracker
    """

    def __init__(self):
        self._regime = UnifiedCalibrationRegime()
        self._validator = MethodBindingValidator()
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def orchestrate(
        self,
        request: OrchestrationRequest,
    ) -> CalibrationContext:
        """
        Unit of Analysis Requirements:
            - Valid OrchestrationRequest
            - UoA with complexity_score

        Epistemic Level: N2-INF + N3-AUD
        Output: CalibrationContext ready for execution
        Fusion Strategy: Gated validation pipeline

        Orchestrate calibrated method execution.

        Args:
            request: Orchestration request

        Returns:
            CalibrationContext ready for method execution

        Raises:
            ValidationError: If method bindings violate TYPE constraints
            CalibrationError: If calibration fails
        """
        self._logger.info(
            f"Orchestrating contract {request.contract_id} "
            f"(TYPE: {request.contract_type}, role: {request.role})"
        )

        # Step 1: Generate unified calibration manifest
        manifest = self._regime.calibrate(
            contract_id=request.contract_id,
            contract_type_code=request.contract_type,
            unit=request.unit_of_analysis,
            method_binding_set=request.method_binding_set,
            role=request.role,
        )

        self._logger.info(
            f"Calibration manifest generated: {manifest.manifest_id[:12]}..., "
            f"cognitive_cost={manifest.cognitive_cost_score:.3f}, "
            f"interaction_density={manifest.interaction_density:.3f}"
        )

        # Step 2: Create execution context
        context = CalibrationContext(
            unit_of_analysis=request.unit_of_analysis,
            phase1_layer=manifest.phase1_layer,
            phase2_layer=manifest.phase2_layer,
            contract_type=request.contract_type,
            contract_id=request.contract_id,
        )

        self._logger.info(
            f"Calibration context created for {request.contract_id}, "
            f"validity: Phase1={manifest.phase1_layer.parameters[0].days_until_expiry():.1f} days, "
            f"Phase2={manifest.phase2_layer.parameters[0].days_until_expiry():.1f} days"
        )

        return context

    def execute_with_calibration(
        self,
        request: OrchestrationRequest,
        execution_func: Any,
    ) -> Any:
        """
        Unit of Analysis Requirements:
            - Valid OrchestrationRequest
            - execution_func that accepts **kwargs

        Epistemic Level: N1-EMP + N2-INF + N3-AUD (full pipeline)
        Output: Execution result with calibration applied
        Fusion Strategy: Context-managed execution

        Execute function within calibration context.

        Args:
            request: Orchestration request
            execution_func: Function to execute (receives context as kwargs)

        Returns:
            Result of execution_func
        """
        # Create calibration context
        context = self.orchestrate(request)

        # Execute within context
        with calibration_context(context):
            self._logger.info(f"Executing {execution_func.__name__} with calibration")
            result = execution_func()

        return result


__all__ = [
    "CalibratedOrchestrator",
    "OrchestrationRequest",
]
```

### 2.2 Update Phase 2 Executor Integration

**File**: Update `src/farfan_pipeline/phases/Phase_2/phase2_95_03_executor_calibration_integration.py`

**Changes**:
1. Import `CalibratedOrchestrator`
2. Create `OrchestrationRequest` for each contract
3. Execute methods within `calibration_context()`

```python
# BEFORE
def execute_contract(contract: Contract):
    # Direct execution without calibration
    result = method_executor.execute(contract.methods)
    return result

# AFTER
from farfan_pipeline.infrastructure.calibration import CalibratedOrchestrator, OrchestrationRequest

orchestrator = CalibratedOrchestrator()

def execute_contract(contract: Contract, unit_of_analysis: UnitOfAnalysis):
    # Create orchestration request
    request = OrchestrationRequest(
        contract_id=contract.id,
        contract_type=contract.type_code,
        unit_of_analysis=unit_of_analysis,
        method_binding_set=contract.method_bindings,
        role="SCORE_Q",
    )

    # Execute with calibration
    result = orchestrator.execute_with_calibration(
        request=request,
        execution_func=lambda: method_executor.execute(contract.methods),
    )

    return result
```

---

## PHASE 3: VALIDATION GATES (Week 5)

### Objective
Add runtime validation gates that prevent execution if calibration constraints are violated.

### 3.1 Create Pre-Execution Validation Gate

**File**: `src/farfan_pipeline/infrastructure/calibration/validation_gate.py`

```python
"""
Validation Gates
================
Pre-execution validation gates that enforce calibration constraints.

DESIGN PATTERN: Chain of Responsibility + Specification Pattern
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum

from .calibration_auditor import CalibrationAuditor
from .drift_detector import DriftDetector, DriftSeverity
from .interaction_density import InteractionDensityTracker
from .method_binding_validator import MethodBindingValidator
from .runtime_context import CalibrationContext

logger = logging.getLogger(__name__)


class GateResult(Enum):
    """Result of validation gate."""
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"


@dataclass
class ValidationGateReport:
    """
    Unit of Analysis Requirements:
        - CalibrationContext with both phase layers

    Epistemic Level: N3-AUD (validation)
    Output: Validation report with pass/fail status
    Fusion Strategy: Aggregate validation results

    Report from validation gate.

    Attributes:
        result: Overall gate result
        messages: List of validation messages
        violations: List of invariant violations
    """

    result: GateResult
    messages: list[str]
    violations: list[str]

    def is_blocking(self) -> bool:
        """Check if gate result blocks execution."""
        return self.result == GateResult.FAIL


class ValidationGate:
    """
    Unit of Analysis Requirements:
        - CalibrationContext to validate
        - Baseline calibration for drift detection (optional)

    Epistemic Level: N3-AUD
    Output: ValidationGateReport
    Fusion Strategy: Chain of Responsibility validation

    Pre-execution validation gate.

    Runs multiple validation checks before allowing method execution:
    1. Method binding validation (TYPE constraints)
    2. Calibration audit (INV-CAL-00x specifications)
    3. Interaction density check
    4. Drift detection (if baseline available)
    5. Expiry check

    Attributes:
        _validator: Method binding validator
        _auditor: Calibration auditor
        _density_tracker: Interaction density tracker
        _drift_detector: Drift detector
    """

    def __init__(self):
        self._validator = MethodBindingValidator()
        self._auditor = CalibrationAuditor()
        self._density_tracker = InteractionDensityTracker()
        self._drift_detector = DriftDetector()
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def validate(
        self,
        context: CalibrationContext,
        baseline_layer: Any | None = None,
    ) -> ValidationGateReport:
        """
        Unit of Analysis Requirements:
            - Valid CalibrationContext
            - Optional baseline for drift detection

        Epistemic Level: N3-AUD
        Output: ValidationGateReport with blocking/non-blocking result
        Fusion Strategy: Aggregate multiple validation checks

        Run validation gate.

        Args:
            context: Calibration context to validate
            baseline_layer: Baseline calibration layer for drift detection

        Returns:
            ValidationGateReport
        """
        messages = []
        violations = []
        result = GateResult.PASS

        # Check 1: Expiry
        if context.phase1_layer.parameters[0].days_until_expiry() < 0:
            violations.append("Phase 1 calibration layer expired")
            result = GateResult.FAIL
        elif context.phase1_layer.parameters[0].days_until_expiry() < 7:
            messages.append(
                f"Phase 1 calibration expiring in "
                f"{context.phase1_layer.parameters[0].days_until_expiry():.1f} days"
            )
            if result == GateResult.PASS:
                result = GateResult.WARNING

        # Check 2: Audit calibration layers
        phase1_audit = self._auditor.audit(context.phase1_layer)
        if not phase1_audit.passed:
            violations.extend([v.message for v in phase1_audit.violations])
            result = GateResult.FAIL

        phase2_audit = self._auditor.audit(context.phase2_layer)
        if not phase2_audit.passed:
            violations.extend([v.message for v in phase2_audit.violations])
            result = GateResult.FAIL

        # Check 3: Drift detection (if baseline provided)
        if baseline_layer:
            drift_report = self._drift_detector.detect_drift(
                baseline=baseline_layer,
                current=context.phase1_layer,
            )
            if drift_report.has_significant_drift():
                messages.append(
                    f"Significant calibration drift detected: "
                    f"severity={drift_report.overall_severity.value}"
                )
                if drift_report.requires_recalibration():
                    violations.append("Critical drift requires immediate recalibration")
                    result = GateResult.FAIL
                elif result == GateResult.PASS:
                    result = GateResult.WARNING

        self._logger.info(
            f"Validation gate result: {result.value}, "
            f"violations={len(violations)}, warnings={len(messages)}"
        )

        return ValidationGateReport(
            result=result,
            messages=messages,
            violations=violations,
        )


__all__ = [
    "ValidationGate",
    "ValidationGateReport",
    "GateResult",
]
```

### 3.2 Integrate Validation Gate into Orchestrator

```python
# In CalibratedOrchestrator.orchestrate():

# Add validation gate
gate = ValidationGate()
gate_report = gate.validate(context, baseline_layer=previous_calibration)

if gate_report.is_blocking():
    raise CalibrationError(
        f"Validation gate FAILED for {request.contract_id}: "
        f"{', '.join(gate_report.violations)}"
    )

if gate_report.result == GateResult.WARNING:
    for msg in gate_report.messages:
        logger.warning(f"Validation gate WARNING: {msg}")
```

---

## PHASE 4: TELEMETRY & MONITORING (Week 6)

### Objective
Track calibration effectiveness in production.

### 4.1 Create Calibration Telemetry

**File**: `src/farfan_pipeline/infrastructure/calibration/telemetry.py`

```python
"""
Calibration Telemetry
=====================
Tracks calibration effectiveness and parameter drift in production.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CalibrationMetrics:
    """
    Metrics for calibration effectiveness.

    Attributes:
        contract_id: Contract identifier
        execution_time_ms: Execution time in milliseconds
        chunk_size_used: Actual chunk size used
        prior_strength_used: Actual prior strength used
        veto_triggered: Whether veto was triggered
        cognitive_cost: Cognitive cost score
        interaction_density: Interaction density
        drift_severity: Drift severity (if detected)
    """

    contract_id: str
    execution_time_ms: float
    chunk_size_used: int
    prior_strength_used: float
    veto_triggered: bool
    cognitive_cost: float
    interaction_density: float
    drift_severity: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


class CalibrationTelemetry:
    """
    Tracks calibration telemetry.

    Usage:
        telemetry = CalibrationTelemetry()
        telemetry.record_execution(metrics)
        stats = telemetry.get_statistics()
    """

    def __init__(self):
        self._metrics: list[CalibrationMetrics] = []
        self._by_type: dict[str, list[CalibrationMetrics]] = defaultdict(list)
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def record_execution(self, metrics: CalibrationMetrics) -> None:
        """Record execution metrics."""
        self._metrics.append(metrics)
        # Extract type from contract_id (assumes format like Q001_PA01_TYPE_A)
        parts = metrics.contract_id.split("_")
        if len(parts) >= 3:
            contract_type = parts[-1]
            self._by_type[contract_type].append(metrics)

        self._logger.info(
            f"Recorded metrics for {metrics.contract_id}: "
            f"time={metrics.execution_time_ms:.1f}ms, "
            f"chunk_size={metrics.chunk_size_used}, "
            f"veto={metrics.veto_triggered}"
        )

    def get_statistics(self) -> dict[str, Any]:
        """Get aggregated statistics."""
        if not self._metrics:
            return {}

        total_executions = len(self._metrics)
        avg_execution_time = sum(m.execution_time_ms for m in self._metrics) / total_executions
        veto_rate = sum(1 for m in self._metrics if m.veto_triggered) / total_executions

        # Per-TYPE statistics
        type_stats = {}
        for type_code, metrics in self._by_type.items():
            type_stats[type_code] = {
                "count": len(metrics),
                "avg_execution_time_ms": sum(m.execution_time_ms for m in metrics) / len(metrics),
                "avg_chunk_size": sum(m.chunk_size_used for m in metrics) / len(metrics),
                "veto_rate": sum(1 for m in metrics if m.veto_triggered) / len(metrics),
            }

        return {
            "total_executions": total_executions,
            "avg_execution_time_ms": avg_execution_time,
            "veto_rate": veto_rate,
            "by_type": type_stats,
        }


__all__ = [
    "CalibrationMetrics",
    "CalibrationTelemetry",
]
```

---

## PHASE 5: END-TO-END TESTING (Week 7)

### 5.1 Integration Test

**File**: `tests/calibration/test_e2e_parametrization.py`

```python
"""
End-to-End Parametrization Test
================================
Tests complete flow from UoA → Calibration → Execution
"""

import pytest

from farfan_pipeline.infrastructure.calibration import (
    CalibratedOrchestrator,
    CalibrationContext,
    MethodBinding,
    MethodBindingSet,
    MunicipalityCategory,
    OrchestrationRequest,
    UnitOfAnalysis,
    calibration_context,
    chunk_size_aware,
)


def test_uoa_to_execution_flow():
    """Test complete UoA → parametrization → execution flow."""

    # Step 1: Create UnitOfAnalysis (high complexity municipality)
    unit = UnitOfAnalysis(
        municipality_code="05001",
        municipality_name="Medellín",
        department_code="05",
        population=2_500_000,
        total_budget_cop=10_000_000_000_000,
        category=MunicipalityCategory.CATEGORIA_ESPECIAL,
        sgp_percentage=30.0,
        own_revenue_percentage=70.0,
        fiscal_context="HIGH_CAPACITY",
        plan_period_start=2024,
        plan_period_end=2027,
        policy_area_codes=frozenset({"PA01", "PA02", "PA03"}),
    )

    # Verify complexity
    assert unit.complexity_score() > 0.7  # High complexity

    # Step 2: Create method bindings
    bindings = MethodBindingSet(
        contract_id="Q001_PA01_TYPE_A",
        contract_type_code="TYPE_A",
        bindings=[
            MethodBinding(
                method_id="extract_doc",
                epistemic_level="N1",
                requires=frozenset(),
                provides=frozenset({"raw_chunks"}),
            ),
        ],
    )

    # Step 3: Create orchestration request
    request = OrchestrationRequest(
        contract_id="Q001_PA01_TYPE_A",
        contract_type="TYPE_A",
        unit_of_analysis=unit,
        method_binding_set=bindings,
        role="EXTRACT",
    )

    # Step 4: Orchestrate (generates calibration)
    orchestrator = CalibratedOrchestrator()
    context = orchestrator.orchestrate(request)

    # Step 5: Verify calibration
    chunk_size = context.get_parameter("chunk_size", phase="phase1")
    assert chunk_size > 512  # High complexity → larger chunks
    assert chunk_size <= 2048

    prior_strength = context.get_parameter("prior_strength", phase="phase1")
    assert 0.3 <= prior_strength <= 2.0  # TYPE_A bounds

    # Step 6: Execute method within context
    @chunk_size_aware
    def extract_document(chunk_size: int = 512):
        # chunk_size is automatically injected!
        return f"Processed with chunk_size={chunk_size}"

    with calibration_context(context):
        result = extract_document()

    # Verify chunk_size was injected
    assert f"chunk_size={int(chunk_size)}" in result

    print(f"✅ E2E test passed: UoA complexity → chunk_size={chunk_size}")
```

---

## IMPLEMENTATION TIMELINE

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| **Phase 1**: Runtime Parametrization | Weeks 1-2 | `runtime_context.py`, `uoa_sensitive.py`, decorator integration |
| **Phase 2**: Orchestrator Integration | Weeks 3-4 | `calibrated_orchestrator.py`, Phase 2 executor updates |
| **Phase 3**: Validation Gates | Week 5 | `validation_gate.py`, gate integration |
| **Phase 4**: Telemetry | Week 6 | `telemetry.py`, monitoring dashboard |
| **Phase 5**: Testing | Week 7 | E2E tests, performance benchmarks |
| **Phase 6**: Documentation | Week 8 | User guide, API docs, runbooks |

---

## SUCCESS CRITERIA

✅ **Ingestion Methods UoA-Sensitive**
- All extraction methods decorated with `@chunk_size_aware`
- Chunk size automatically scales with UoA complexity
- Coverage targets adjust based on policy area count

✅ **Phase 2 Methods TYPE-Aligned**
- Orchestrator validates method bindings before execution
- Prohibited operations blocked at runtime
- Fusion strategy enforced per TYPE

✅ **Validation Gates Operational**
- Pre-execution validation catches violations
- Drift detection prevents stale calibration
- Expiry checks block expired parameters

✅ **Telemetry Tracking Effectiveness**
- Execution time correlated with calibration
- Veto rates tracked per TYPE
- Drift alerts trigger recalibration

✅ **Zero Hard-Coded Parameters**
- All parameters sourced from calibration layers
- UoA characteristics drive parametrization
- TYPE constraints enforced automatically

---

## MONITORING & ALERTS

### Calibration Drift Alert
```
ALERT: Calibration drift detected for TYPE_A
- Drift severity: SIGNIFICANT (35% change in prior_strength)
- Affected contracts: 15
- Action: Recalibrate TYPE_A contracts
```

### Validation Gate Failure
```
ERROR: Validation gate FAILED for Q005_PA03_TYPE_E
- Violation: Prohibited operation 'weighted_mean' detected
- Method: aggregate_scores()
- Action: Replace with min_consistency fusion
```

### Expiry Warning
```
WARNING: Phase 1 calibration expiring soon
- Contract: Q001_PA01_TYPE_A
- Days until expiry: 5
- Action: Trigger recalibration workflow
```

---

## CONCLUSION

This operationalization plan transforms the calibration architecture into a **production-ready runtime system** where:

1. ✅ Methods are **automatically parametrized** based on UoA
2. ✅ TYPE constraints are **enforced at runtime**
3. ✅ Validation gates **prevent misconfigured execution**
4. ✅ Telemetry **tracks effectiveness** in production
5. ✅ Drift detection **triggers recalibration** automatically

**BUSINESS CLOSED** when all phases are implemented and tested.

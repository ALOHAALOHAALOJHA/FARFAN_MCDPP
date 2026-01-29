"""
SISAS Bus Audit Integration Module

Provides integration hooks for connecting the Bus Audit System
with existing SISAS components without modifying frozen code.

This module enables:
1. Automatic SDO audit bridge initialization
2. Gate validation audit hooks
3. Consumer registration tracking
4. Signal lifecycle correlation

Usage:
    from canonic_questionnaire_central.audits.integration import enable_sdo_bus_audit

    # Enable bus audit for an existing SDO instance
    sdo = SignalDistributionOrchestrator()
    audit_manager, bridge = enable_sdo_bus_audit(sdo)

Author: F.A.R.F.A.N Pipeline Team
Version: 2.0.0
"""

import logging
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, Callable

from .bus_audit import (
    BusAuditManager,
    SDOAuditBridge,
    BusAuditEventType,
    get_bus_audit_manager,
)

logger = logging.getLogger(__name__)


# =============================================================================
# SDO INTEGRATION
# =============================================================================

def enable_sdo_bus_audit(
    sdo: 'SignalDistributionOrchestrator',
    audit_manager: Optional[BusAuditManager] = None,
    audit_path: Optional[Path] = None
) -> Tuple[BusAuditManager, SDOAuditBridge]:
    """
    Enable comprehensive bus auditing for a SignalDistributionOrchestrator.

    This function creates an audit bridge that extends SDO's internal
    audit with bus-level metrics, correlation tracking, and health monitoring.

    The integration is NON-INVASIVE - it wraps SDO's methods without
    modifying the frozen core code.

    Args:
        sdo: SignalDistributionOrchestrator instance
        audit_manager: Optional existing BusAuditManager (creates new if None)
        audit_path: Optional path for audit persistence

    Returns:
        Tuple of (BusAuditManager, SDOAuditBridge)

    Example:
        >>> from canonic_questionnaire_central.core import SignalDistributionOrchestrator
        >>> from canonic_questionnaire_central.audits.integration import enable_sdo_bus_audit
        >>>
        >>> sdo = SignalDistributionOrchestrator()
        >>> audit_mgr, bridge = enable_sdo_bus_audit(sdo)
        >>>
        >>> # Now all SDO operations are automatically audited
        >>> report = audit_mgr.get_system_health_report()
    """
    if audit_manager is None:
        audit_manager = get_bus_audit_manager(audit_path)

    # Create and connect the bridge
    bridge = SDOAuditBridge(sdo, audit_manager)

    # Audit existing consumers
    for consumer_id, consumer in sdo.consumers.items():
        bridge.audit_consumer_registration(
            consumer_id=consumer_id,
            scopes=list(consumer.scopes) if hasattr(consumer, 'scopes') else [],
            capabilities=list(consumer.capabilities) if hasattr(consumer, 'capabilities') else [],
            registered=True
        )

    logger.info(f"Bus audit enabled for SDO with {len(sdo.consumers)} existing consumers")

    return audit_manager, bridge


def wrap_gate_validation(
    sdo: 'SignalDistributionOrchestrator',
    bridge: SDOAuditBridge
) -> None:
    """
    Wrap SDO's gate validation methods for comprehensive audit.

    Args:
        sdo: SignalDistributionOrchestrator instance
        bridge: SDOAuditBridge instance
    """
    # Wrap gate validation methods
    original_validate_gates = sdo.validate_all_gates

    def audited_validate_gates(signal, post_dispatch=False):
        """Wrapper for gate validation with audit."""
        # Call original validation
        all_valid, gate_errors = original_validate_gates(signal, post_dispatch)

        # Audit each gate result
        gate_names = [
            "gate_1_scope_alignment",
            "gate_2_value_add",
            "gate_3_capability",
        ]
        if post_dispatch:
            gate_names.append("gate_4_irrigation_channel")

        for gate_name in gate_names:
            passed = gate_name not in gate_errors
            errors = gate_errors.get(gate_name, []) if not passed else []
            bridge.audit_gate_validation(signal, gate_name, passed, errors)

        return all_valid, gate_errors

    # Replace method
    sdo.validate_all_gates = audited_validate_gates

    logger.info("Wrapped SDO gate validation for audit")


def wrap_consumer_registration(
    sdo: 'SignalDistributionOrchestrator',
    bridge: SDOAuditBridge
) -> None:
    """
    Wrap SDO's consumer registration methods for audit.

    Args:
        sdo: SignalDistributionOrchestrator instance
        bridge: SDOAuditBridge instance
    """
    # Wrap register_consumer
    original_register = sdo.register_consumer

    def audited_register(consumer_id, scopes, capabilities, handler):
        """Wrapper for consumer registration with audit."""
        result = original_register(consumer_id, scopes, capabilities, handler)

        # Audit the registration
        bridge.audit_consumer_registration(
            consumer_id=consumer_id,
            scopes=[scope if hasattr(scope, 'to_dict') else scope for scope in scopes],
            capabilities=capabilities,
            registered=True
        )

        return result

    # Wrap unregister_consumer
    original_unregister = sdo.unregister_consumer

    def audited_unregister(consumer_id):
        """Wrapper for consumer unregistration with audit."""
        result = original_unregister(consumer_id)

        if result:
            bridge.audit_consumer_registration(
                consumer_id=consumer_id,
                scopes=[],
                capabilities=[],
                registered=False
            )

        return result

    # Replace methods
    sdo.register_consumer = audited_register
    sdo.unregister_consumer = audited_unregister

    logger.info("Wrapped SDO consumer registration for audit")


def enable_full_sdo_audit(
    sdo: 'SignalDistributionOrchestrator',
    audit_manager: Optional[BusAuditManager] = None,
    audit_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Enable comprehensive SDO auditing with all integration hooks.

    This is the RECOMMENDED way to enable full bus audit for SDO.

    Args:
        sdo: SignalDistributionOrchestrator instance
        audit_manager: Optional existing BusAuditManager
        audit_path: Optional path for audit persistence

    Returns:
        Dict with audit_manager, bridge, and integration status

    Example:
        >>> sdo = SignalDistributionOrchestrator()
        >>> audit_config = enable_full_sdo_audit(sdo)
        >>>
        >>> # Generate comprehensive health report
        >>> report = audit_config['audit_manager'].get_system_health_report()
    """
    # Get or create audit manager
    if audit_manager is None:
        audit_manager = get_bus_audit_manager(audit_path)

    # Enable basic SDO audit
    audit_manager, bridge = enable_sdo_bus_audit(sdo, audit_manager)

    # Wrap gate validation
    wrap_gate_validation(sdo, bridge)

    # Wrap consumer registration
    wrap_consumer_registration(sdo, bridge)

    # Perform initial health check
    trail = audit_manager.get_sdo_trail()
    trail.create_entry(
        event_type=BusAuditEventType.BUS_HEALTH_CHECK,
        detail="SDO bus audit fully enabled with all integration hooks",
        metadata={
            "consumers_count": len(sdo.consumers),
            "dead_letters_enabled": sdo.rules.dead_letter_enabled if hasattr(sdo, 'rules') else True,
            "empirical_threshold": sdo.rules.empirical_availability_min if hasattr(sdo, 'rules') else 0.30,
        }
    )

    logger.info("Full SDO bus audit enabled with all integration hooks")

    return {
        "audit_manager": audit_manager,
        "bridge": bridge,
        "sdo": sdo,
        "integration_status": {
            "basic_audit": True,
            "gate_validation": True,
            "consumer_registration": True,
            "health_check": True,
        }
    }


# =============================================================================
# RESOLVER INTEGRATION
# =============================================================================

def enable_resolver_bus_audit(
    resolver: 'CanonicalQuestionnaireResolver',
    audit_manager: Optional[BusAuditManager] = None,
    audit_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Enable bus audit for the CanonicalQuestionnaireResolver.

    The resolver typically has an SDO instance that can be audited.

    Args:
        resolver: CanonicalQuestionnaireResolver instance
        audit_manager: Optional existing BusAuditManager
        audit_path: Optional path for audit persistence

    Returns:
        Dict with audit_manager and bridge info
    """
    # Check if resolver has SDO
    if not hasattr(resolver, '_sdo') or resolver._sdo is None:
        logger.warning("Resolver does not have an SDO instance, audit cannot be enabled")
        return {
            "error": "No SDO instance found in resolver",
            "audit_enabled": False
        }

    # Enable SDO audit
    config = enable_full_sdo_audit(resolver._sdo, audit_manager, audit_path)

    # Audit resolver initialization
    trail = config["audit_manager"].get_sdo_trail()
    trail.create_entry(
        event_type=BusAuditEventType.BUS_CREATED,
        detail="Resolver bus audit initialized",
        metadata={
            "resolver_type": type(resolver).__name__,
            "sdo_connected": True,
        }
    )

    config["resolver"] = resolver
    return config


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_sdo_health_report(sdo: 'SignalDistributionOrchestrator') -> Dict[str, Any]:
    """
    Generate health report for an SDO instance.

    Args:
        sdo: SignalDistributionOrchestrator instance

    Returns:
        Dict with health metrics
    """
    audit_manager = get_bus_audit_manager()

    # Generate system health report
    system_report = audit_manager.get_system_health_report()

    # Add SDO-specific metrics
    sdo_key = f"sdo:SignalDistributionOrchestrator"
    sdo_report = system_report.get("buses", {}).get(sdo_key, {})

    # Add SDO internal metrics
    sdo_metrics = sdo.get_metrics() if hasattr(sdo, 'get_metrics') else {}
    sdo_health = sdo.health_check() if hasattr(sdo, 'health_check') else {}

    return {
        "bus_audit": sdo_report,
        "sdo_metrics": sdo_metrics,
        "sdo_health": sdo_health,
        "system_summary": system_report.get("summary", {}),
    }


def export_sdo_audit_trail(
    sdo: 'SignalDistributionOrchestrator',
    output_path: Path
) -> None:
    """
    Export the SDO audit trail to a file.

    Args:
        sdo: SignalDistributionOrchestrator instance
        output_path: Path to output file
    """
    audit_manager = get_bus_audit_manager()
    trail = audit_manager.get_sdo_trail()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    trail.export_to_file(output_path)

    logger.info(f"Exported SDO audit trail to {output_path}")


def get_signal_flow_trace(
    sdo: 'SignalDistributionOrchestrator',
    signal_id: str
) -> Dict[str, Any]:
    """
    Get complete flow trace for a signal through SDO.

    Args:
        sdo: SignalDistributionOrchestrator instance
        signal_id: Signal ID to trace

    Returns:
        Dict with complete signal lifecycle and flow
    """
    audit_manager = get_bus_audit_manager()

    # Try to get existing bridge
    bridge = None
    if hasattr(audit_manager, '_sdo_trail'):
        # We need to find the bridge that was used
        # For now, create a temporary bridge
        bridge = SDOAuditBridge(sdo, audit_manager)

    if bridge:
        return bridge.get_signal_flow_trace(signal_id)

    # Fallback: direct SDO audit
    return {
        "signal_id": signal_id,
        "sdo_audit": [e.to_dict() for e in sdo.get_audit_log(signal_id)],
        "note": "Full bus audit trace not available - bridge not initialized",
    }

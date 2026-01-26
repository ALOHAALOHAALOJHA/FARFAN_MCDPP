"""
Bus Audit System for SISAS

Provides comprehensive auditing, monitoring, and health analysis for both:
- Signal Distribution Orchestrator (SDO) - Main pub/sub bus
- Legacy SignalBus system - Category-based message buses

This module extends the existing audit trail patterns with bus-specific
metrics, correlation tracking, and sophisticated health monitoring.

Usage:
    from canonic_questionnaire_central.audits import (
        get_bus_audit_manager,
        BusAuditManager,
        SDOAuditBridge,
        BusAuditEntry,
        BusAuditEventType,
    )

    # Get the global audit manager
    audit_manager = get_bus_audit_manager()

    # Connect to SDO
    from canonic_questionnaire_central.core import SignalDistributionOrchestrator
    sdo = SignalDistributionOrchestrator()
    bridge = SDOAuditBridge(sdo, audit_manager)

    # Generate health report
    report = audit_manager.get_system_health_report()

Author: F.A.R.F.A.N Pipeline Team
Version: 2.0.0
"""

from .bus_audit import (
    # Enums
    BusSystemType,
    LegacyBusType,
    BusAuditEventType,
    # Core classes
    BusAuditEntry,
    BusAuditTrail,
    BusAuditManager,
    # Bridges
    SDOAuditBridge,
    LegacyBusAuditBridge,
    # Global manager
    get_bus_audit_manager,
)

__all__ = [
    # Enums
    "BusSystemType",
    "LegacyBusType",
    "BusAuditEventType",
    # Core classes
    "BusAuditEntry",
    "BusAuditTrail",
    "BusAuditManager",
    # Bridges
    "SDOAuditBridge",
    "LegacyBusAuditBridge",
    # Global manager
    "get_bus_audit_manager",
]

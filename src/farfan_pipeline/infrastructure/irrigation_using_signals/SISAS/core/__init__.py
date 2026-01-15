# -*- coding: utf-8 -*-
"""
SISAS Core Module

Este módulo expone la infraestructura base del sistema SISAS (Signal-based Irrigation System Architecture).

Exports:
    Signal, SignalContext, SignalSource, SignalCategory, SignalConfidence: Clases base de señales
    Event, EventStore, EventType, EventPayload: Sistema de eventos empíricos
    PublicationContract, ConsumptionContract, IrrigationContract, ContractRegistry: Sistema de contratos
    SignalBus, BusRegistry, BusType, BusMessage: Sistema de buses de señales
"""

from .signal import (
    Signal,
    SignalContext,
    SignalSource,
    SignalCategory,
    SignalConfidence
)

from .event import (
    Event,
    EventStore,
    EventType,
    EventPayload
)

from .contracts import (
    PublicationContract,
    ConsumptionContract,
    IrrigationContract,
    ContractRegistry,
    ContractType,
    ContractStatus,
    SignalTypeSpec
)

from .bus import (
    SignalBus,
    BusRegistry,
    BusType,
    BusMessage
)

__all__ = [
    # Signal components
    "Signal",
    "SignalContext",
    "SignalSource",
    "SignalCategory",
    "SignalConfidence",
    # Event components
    "Event",
    "EventStore",
    "EventType",
    "EventPayload",
    # Contract components
    "PublicationContract",
    "ConsumptionContract",
    "IrrigationContract",
    "ContractRegistry",
    "ContractType",
    "ContractStatus",
    "SignalTypeSpec",
    # Bus components
    "SignalBus",
    "BusRegistry",
    "BusType",
    "BusMessage",
]
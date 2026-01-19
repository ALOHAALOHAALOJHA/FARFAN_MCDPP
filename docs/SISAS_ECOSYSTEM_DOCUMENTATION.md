# SISAS ECOSYSTEM - COMPREHENSIVE DOCUMENTATION

**Signal Irrigation System for Adaptive Signal-driven Architecture**

Version: 2.0.0
Date: 2026-01-19
Authors: FARFAN Pipeline Architecture Team

---

## ⚠️ IMPORTANT DISCLAIMER

**This documentation describes a system that is PARTIALLY IMPLEMENTED.**

**What IS working:**
- Core signal infrastructure (`SISAS/core/`)
- Signal consumers for phases 0-9
- 17 signal types (structural, integrity, epistemic, contrast, operational, consumption)
- Contract loading and execution

**What is NOT working (orphan code removed):**
- Orchestration signal types (`orchestration.py`) - REMOVED as unused
- Integration between orchestrator and SISAS signals - NOT IMPLEMENTED
- Signal emission from orchestrator - NOT IMPLEMENTED

**Reality:** The SISAS signal types exist but the orchestrator does NOT emit them.
The system has signal infrastructure but lacks actual signal flow from orchestration.

---

## TABLE OF CONTENTS

1. [Introduction](#chapter-1-introduction)
2. [Architecture Overview](#chapter-2-architecture-overview)
3. [Core Concepts](#chapter-3-core-concepts)
4. [Signal System](#chapter-4-signal-system)
5. [Contracts System](#chapter-5-contracts-system)
6. [Consumers Framework](#chapter-6-consumers-framework)
7. [Vehicles System](#chapter-7-vehicles-system)
8. [Irrigation Protocol](#chapter-8-irrigation-protocol)
9. [Integration Guide](#chapter-9-integration-guide)
10. [Reference](#chapter-10-reference)

---

# CHAPTER 1: INTRODUCTION

## 1.1 What is SISAS?

SISAS (**Signal Irrigation System for Adaptive Signal-driven Architecture**) is a comprehensive signal distribution and consumption framework designed for the FARFAN pipeline. It enables decoupled communication between pipeline phases through a publish-subscribe pattern with type-safe signal routing.

### 1.1.1 Core Philosophy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SISAS CORE PHILOSOPHY                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  "Signals should FLOW like water through an irrigation system,               │
│   reaching every consumer that needs them, regardless of                    │
│   where they are in the pipeline architecture."                             │
│                                                                              │
│  Key Principles:                                                             │
│  • Decoupling: Producers don't know consumers                                │
│  • Type Safety: Signal types define contracts                               │
│  • Routing: Automatic signal-to-consumer matching                           │
│  • Scalability: Add consumers without modifying producers                   │
│  • Observability: Every signal is tracked and logged                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.1.2 Historical Context

SISAS evolved from the need to:
1. **Eliminate tight coupling** between pipeline phases
2. **Enable parallel execution** of independent signal consumers
3. **Provide traceability** for all signal flows
4. **Support dynamic discovery** of signal consumers
5. **Facilitate testing** through signal isolation

## 1.2 System Scope

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SISAS SYSTEM SCOPE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │                    PIPELINE PHASES (0-9)                          │    │
│  │  Phase 0: Bootstrap & Validation                                   │    │
│  │  Phase 1: CPP Ingestion                                            │    │
│  │  Phase 2: Task Execution & Enrichment                              │    │
│  │  Phase 3: Validation & Scoring                                     │    │
│  │  Phase 4: Dimension Aggregation                                    │    │
│  │  Phase 5: Policy Area Aggregation                                  │    │
│  │  Phase 6: Cluster Aggregation                                     │    │
│  │  Phase 7: Macro Aggregation                                        │    │
│  │  Phase 8: Recommendations                                         │    │
│  │  Phase 9: Report Assembly                                         │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                              │                                             │
│                              ▼                                             │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │              SIGNAL DISTRIBUTION ORCHESTRATOR (SDO)                │    │
│  │              Routes signals to registered consumers                │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                              │                                             │
│                ┌─────────────┼─────────────┐                            │
│                ▼             ▼             ▼                            │
│         ┌──────────┐  ┌──────────┐  ┌──────────┐                       │
│         │ Consumers│  │ Vehicles │  │Contracts │                       │
│         └──────────┘  └──────────┘  └──────────┘                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 1.3 Document Structure

This document is organized into 10 chapters:

| Chapter | Topic | Focus |
|---------|-------|-------|
| 1 | Introduction | Overview, philosophy, scope |
| 2 | Architecture Overview | System design, components |
| 3 | Core Concepts | Signals, scopes, types |
| 4 | Signal System | Signal lifecycle, routing |
| 5 | Contracts System | Irrigation contracts |
| 6 | Consumers Framework | Consumer types, patterns |
| 7 | Vehicles System | Signal transport |
| 8 | Irrigation Protocol | Verification, sync |
| 9 | Integration Guide | Usage examples |
| 10 | Reference | API documentation |

---

# CHAPTER 2: ARCHITECTURE OVERVIEW

## 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SISAS HIGH-LEVEL ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        PRODUCERS                                      │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │  │
│  │  │ Phase 0  │→│ Phase 1  │→│ Phase 2  │→│  ...     │           │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                │                                            │
│                                ▼                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      SIGNAL LAYER                                    │  │
│  │  ┌─────────────────────────────────────────────────────────────┐    │  │
│  │  │            Signal (Immutable Atomic Unit)                    │    │  │
│  │  │  - signal_id (hash)                                          │    │  │
│  │  │  - signal_type (enum)                                         │    │  │
│  │  │  - payload (any)                                              │    │  │
│  │  │  - timestamp                                                  │    │  │
│  │  │  - metadata                                                   │    │  │
│  │  └─────────────────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                │                                            │
│                                ▼                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                 SIGNAL DISTRIBUTION ORCHESTRATOR                      │  │
│  │  ┌────────────────────────────────────────────────────────────────┐  │  │
│  │  │  1. Register Consumers (with signal type subscriptions)       │  │  │
│  │  │  2. Receive Signal                                            │  │  │
│  │  │  3. Match to Consumers (by signal type)                       │  │  │
│  │  │  4. Dispatch to Vehicles                                      │  │  │
│  │  │  5. Execute Contracts                                         │  │
│  │  └────────────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                │                                            │
│            ┌─────────────────────┼─────────────────────┐                   │
│            ▼                     ▼                     ▼                   │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐              │
│  │   CONSUMERS   │    │   VEHICLES    │    │   CONTRACTS   │              │
│  │               │    │               │    │               │              │
│  │ Phase 0-9     │    │ Transport     │    │ Irrigation    │              │
│  │ Assembly      │    │ Dispatch      │    │ Agreements    │              │
│  │ Extraction    │    │ Async Queue   │    │ Validation    │              │
│  │ Enrichment    │    │ Batch Process │    │ Status        │              │
│  │ Validation    │    │               │    │               │              │
│  │ Aggregation   │    │               │    │               │              │
│  │ Scoring       │    │               │    │               │              │
│  │ Reporting     │    │               │    │               │              │
│  └───────────────┘    └───────────────┘    └───────────────┘              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2.2 Component Hierarchy

```
SISAS/
├── core/                          # Core abstractions
│   ├── signal.py                   # Signal, SignalType enums
│   ├── signal_distribution_orchestrator.py  # SDO main class
│   ├── contracts.py                # Irrigation contracts
│   └── schemas.py                  # Data schemas
│
├── consumers/                      # Signal consumers (10 phases)
│   ├── phase0/
│   │   └── phase0_assembly_consumer.py
│   ├── phase1/
│   │   └── phase1_extraction_consumer.py
│   ├── phase2/
│   │   └── phase2_enrichment_consumer.py
│   ├── phase3/
│   │   └── phase3_validation_consumer.py
│   ├── phase4/
│   │   └── phase4_dimension_consumer.py
│   ├── phase5/
│   │   └── phase5_policy_area_consumer.py
│   ├── phase6/
│   │   └── phase6_cluster_consumer.py
│   ├── phase7/
│   │   └── phase7_meso_consumer.py
│   ├── phase8/
│   │   └── phase8_macro_consumer.py
│   ├── phase9/
│   │   └── phase9_report_consumer.py
│   └── base_consumer.py            # Base consumer class
│
├── vehicles/                       # Signal transport vehicles
│   ├── async_vehicle.py             # Async dispatch
│   ├── batch_vehicle.py             # Batch processing
│   ├── sync_vehicle.py              # Synchronous dispatch
│   └── priority_vehicle.py          # Priority-based dispatch
│
├── irrigation/                     # Irrigation system
│   ├── irrigation_executor.py       # Execute irrigation
│   ├── irrigation_map.py            # Map sources to consumers
│   └── irrigation_validator.py      # Validate irrigability
│
├── config/                         # Configuration
│   ├── signal_types_config.json     # Signal type definitions
│   └── consumer_config.json         # Consumer configurations
│
├── scripts/                        # Utility scripts
│   ├── generate_contracts.py        # Generate from CSV
│   └── validate_irrigation.py       # Validate system state
│
└── signal_types/                   # Signal type definitions
    ├── phase0_signals.py
    ├── phase1_signals.py
    ├── phase2_signals.py
    └── ...
```

## 2.3 Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SISAS DATA FLOW                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. PRODUCTION                                                              │
│     ┌────────────────────────────────────────────────────────────────┐     │
│     │ producer.emit(signal_type, payload, metadata)                  │     │
│     └────────────────────────────────────────────────────────────────┘     │
│                              │                                             │
│                              ▼                                             │
│  2. SIGNAL CREATION                                                         │
│     ┌────────────────────────────────────────────────────────────────┐     │
│     │ Signal(                                                             │     │
│     │   signal_id = blake3(payload),                                     │     │
│     │   signal_type = SIGNAL_TYPE_ENUM,                                  │     │
│     │   payload = {...},                                                 │     │
│     │   timestamp = datetime.utcnow(),                                   │     │
│     │   metadata = {...}                                                 │     │
│     │ )                                                                   │     │
│     └────────────────────────────────────────────────────────────────┘     │
│                              │                                             │
│                              ▼                                             │
│  3. SDO ROUTING                                                            │
│     ┌────────────────────────────────────────────────────────────────┐     │
│     │ subscribers = sdo._signal_registry[signal_type]                │     │
│     │ vehicles = sdo._select_vehicle(subscribers)                     │     │
│     └────────────────────────────────────────────────────────────────┘     │
│                              │                                             │
│                              ▼                                             │
│  4. VEHICLE DISPATCH                                                       │
│     ┌────────────────────────────────────────────────────────────────┐     │
│     │ vehicle.deliver(signal, consumer)                              │     │
│     │   → async: asyncio.create_task()                               │     │
│     │   → batch: accumulate and process                               │     │
│     │   → sync: direct call                                          │     │
│     │   → priority: sort by priority                                  │     │
│     └────────────────────────────────────────────────────────────────┘     │
│                              │                                             │
│                              ▼                                             │
│  5. CONSUMER CONSUMPTION                                                   │
│     ┌────────────────────────────────────────────────────────────────┐     │
│     │ consumer.consume(signal)                                       │     │
│     │   result = process(signal.payload)                             │     │
│     │   return ConsumerResult(status, result)                        │     │
│     └────────────────────────────────────────────────────────────────┘     │
│                              │                                             │
│                              ▼                                             │
│  6. RESULT AGGREGATION                                                     │
│     ┌────────────────────────────────────────────────────────────────┐     │
│     │ sdo._result_aggregator.add(result)                             │     │
│     │ metrics.update(consumer_id, result)                            │     │
│     └────────────────────────────────────────────────────────────────┘     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2.4 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Core Language | Python 3.12+ | Main implementation |
| Async Runtime | asyncio | Asynchronous signal processing |
| Hashing | blake3 | Unique signal identification |
| Serialization | JSON | Contract storage |
| Type Safety | dataclasses, TypeVar | Compile-time type checking |
| Logging | structlog | Structured logging |
| Configuration | JSON | Signal type and consumer config |

---

# CHAPTER 3: CORE CONCEPTS

## 3.1 Signal

A **Signal** is the fundamental unit of communication in SISAS. It is an immutable, typed message that flows from producers to consumers.

### 3.1.1 Signal Structure

```python
@dataclass(frozen=True)
class Signal:
    """Immutable atomic unit of signal transmission."""

    signal_id: str                    # BLAKE3 hash of payload
    signal_type: SignalType           # Enum of signal type
    payload: Any                      # Signal payload
    timestamp: datetime               # Creation time
    metadata: Dict[str, Any]          # Additional metadata
    source_phase: str                 # Origin phase
    correlation_id: Optional[str]     # For signal chains
```

### 3.1.2 Signal Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SIGNAL LIFECYCLE                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│  │  CREATED │───│ ROUTED   │───│DELIVERED│───│CONSUMED │             │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘             │
│       │              │              │              │                       │
│       ▼              ▼              ▼              ▼                       │
│   Producer        SDO            Vehicle        Consumer                    │
│   generates      matches         transports    processes                   │
│   signal        subscribers    signal         payload                      │
│                                                                              │
│   State Transitions:                                                         │
│   CREATED → ROUTED: SDO finds matching consumers                            │
│   ROUTED → DELIVERED: Vehicle delivers to consumer                          │
│   DELIVERED → CONSUMED: Consumer processes successfully                      │
│   Any state → FAILED: Error occurred (logged but doesn't block)             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 3.2 Signal Type

A **SignalType** is a typed enumeration that defines the category of signal.

### 3.2.1 Signal Type Hierarchy

```
SignalType (Enum)
│
├─ PHASE_0_SIGNALS
│  ├─ STATIC_LOAD
│  ├─ SIGNAL_PACK
│  └─ INITIALIZATION
│
├─ PHASE_1_SIGNALS
│  ├─ MC01  # Municipal Chunk 01
│  ├─ MC02
│  ├─ ...
│  └─ MC10
│
├─ PHASE_2_SIGNALS
│  ├─ PATTERN_MATCHING
│  ├─ TF_IDF
│  └─ SEMANTIC_SIMILARITY
│
├─ PHASE_3_SIGNALS
│  ├─ NORMATIVE_LOOKUP
│  ├─ COMPLIANCE_CHECK
│  └─ VALIDATION_RESULT
│
├─ AGGREGATION_SIGNALS
│  ├─ DIMENSION_AGGREGATION
│  ├─ POLICY_AREA_AGGREGATION
│  ├─ CLUSTER_AGGREGATION
│  └─ MACRO_AGGREGATION
│
└─ REPORT_SIGNALS
   ├─ TEMPLATE_ENGINE
   ├─ REPORT_GENERATION
   └─ FINAL_OUTPUT
```

### 3.2.2 Signal Type Registration

```python
# Signal types are registered in config/signal_types_config.json
{
  "SIGNAL_TYPES": {
    "STATIC_LOAD": {
      "description": "Static resource loading signal",
      "phase": "phase0",
      "payload_schema": {"type": "object", "properties": {...}}
    },
    "MC01": {
      "description": "Municipal Chunk 01 extraction",
      "phase": "phase1",
      "payload_schema": {...}
    },
    ...
  }
}
```

## 3.3 Signal Scope

A **SignalScope** defines which phases and contexts a signal can reach.

### 3.3.1 Scope Definition

```python
@dataclass(frozen=True)
class SignalScope:
    """Defines the reach of a signal."""

    phase: str                    # Source phase (e.g., "phase0")
    context_filters: Dict[str, Any]  # Filters for consumers
    required_capabilities: List[str]  # Required consumer capabilities
    propagation_rules: List[str]      # Propagation constraints
```

### 3.3.2 Scope Examples

```python
# Local scope - stays within phase
local_scope = SignalScope(
    phase="phase2",
    context_filters={"local": True},
    required_capabilities=["process_enrichment"],
    propagation_rules=["no_propagation"]
)

# Global scope - propagates everywhere
global_scope = SignalScope(
    phase="phase0",
    context_filters={},
    required_capabilities=[],
    propagation_rules=["propagate_all"]
)

# Cross-phase scope - specific target phases
cross_phase_scope = SignalScope(
    phase="phase2",
    context_filters={"target_phases": ["phase3", "phase4"]},
    required_capabilities=["aggregate"],
    propagation_rules=["selective_propagation"]
)
```

## 3.4 Consumer Contract

A **ConsumerContract** defines the agreement between signal producers and consumers.

### 3.4.1 Contract Structure

```python
@dataclass
class ConsumptionContract:
    """Contract defining signal consumption terms."""

    consumer_id: str                     # Unique consumer identifier
    subscribed_signal_types: List[str]   # Signals this consumer wants
    context_filters: Dict[str, Any]       # When to consume
    required_capabilities: List[str]     # Consumer capabilities
    delivery_mode: str                   # SYNC, ASYNC, BATCH
    qos_requirements: Dict[str, Any]     # Quality of service
```

### 3.4.2 Contract Validation

```python
# Validate contract before registration
def validate_contract(contract: ConsumptionContract) -> ValidationResult:
    """Validate a consumption contract."""

    # Check signal types exist
    for signal_type in contract.subscribed_signal_types:
        if signal_type not in SIGNAL_TYPE_REGISTRY:
            return ValidationResult(False, f"Unknown signal type: {signal_type}")

    # Check capabilities match consumer
    consumer_capabilities = get_consumer_capabilities(contract.consumer_id)
    for required in contract.required_capabilities:
        if required not in consumer_capabilities:
            return ValidationResult(False, f"Missing capability: {required}")

    return ValidationResult(True, "Contract valid")
```

---

# CHAPTER 4: SIGNAL SYSTEM

## 4.1 Signal Distribution Orchestrator (SDO)

The **Signal Distribution Orchestrator** is the central component that routes signals to consumers.

### 4.1.1 SDO Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              SIGNAL DISTRIBUTION ORCHESTRATOR (SDO)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                     CONSUMER REGISTRY                                 │  │
│  │  consumer_id → ConsumptionContract                                   │  │
│  │                                                                      │  │
│  │  {                                                                  │  │
│  │    "phase0_assembly": {                                             │  │
│  │      "subscribed_signal_types": ["STATIC_LOAD", "SIGNAL_PACK"],      │  │
│  │      "delivery_mode": "ASYNC"                                        │  │
│  │    },                                                               │  │
│  │    "phase1_extraction": {                                           │  │
│  │      "subscribed_signal_types": ["MC01", "MC02", ...],              │  │
│  │      "delivery_mode": "BATCH"                                        │  │
│  │    },                                                               │  │
│  │    ...                                                              │  │
│  │  }                                                                  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                              │                                             │
│                              ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                  SIGNAL TYPE INDEX (Inverted)                        │  │
│  │  signal_type → [consumer_ids]                                        │  │
│  │                                                                      │  │
│  │  {                                                                  │  │
│  │    "STATIC_LOAD": ["phase0_assembly"],                              │  │
│  │    "MC01": ["phase1_extraction", "phase2_enrichment"],              │  │
│  │    "DIMENSION_AGGREGATION": ["phase4_dimension", "phase7_meso"],    │  │
│  │    ...                                                              │  │
│  │  }                                                                  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                              │                                             │
│                              ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                     VEHICLE SELECTION                                │  │
│  │  ┌────────────────────────────────────────────────────────────────┐ │  │
│  │  │ Dispatch Strategy                                               │ │  │
│  │  │ → ASYNC: Use async_vehicle for concurrent processing            │ │  │
│  │  │ → BATCH: Use batch_vehicle for bulk operations                  │ │  │
│  │  │ → SYNC: Use sync_vehicle for immediate processing               │ │  │
│  │  │ → PRIORITY: Use priority_vehicle for ordered processing          │ │  │
│  │  └────────────────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                              │                                             │
│                              ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                     RESULT AGGREGATION                                │  │
│  │  Collect results, update metrics, track performance                 │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.1.2 SDO Key Methods

```python
class SignalDistributionOrchestrator:
    """Central signal routing coordinator."""

    def register_consumer(
        self,
        consumer: BaseConsumer,
        contract: ConsumptionContract
    ) -> None:
        """Register a consumer with its contract."""

    def dispatch(self, signal: Signal) -> DispatchResult:
        """Dispatch a signal to all matching consumers."""

    def dispatch_batch(self, signals: List[Signal]) -> List[DispatchResult]:
        """Dispatch multiple signals efficiently."""

    def health_check(self) -> HealthStatus:
        """Check system health and consumer status."""

    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
```

## 4.2 Signal Routing

### 4.2.1 Routing Algorithm

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SIGNAL ROUTING ALGORITHM                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Input: signal, consumer_registry, signal_index                            │
│                                                                              │
│  1. LOOKUP SUBSCRIBERS                                                       │
│     subscribers = signal_index[signal.signal_type]                         │
│     if not subscribers:                                                     │
│         return ROUTING_SKIPPED                                              │
│                                                                              │
│  2. FILTER BY CONTEXT                                                       │
│     eligible_consumers = []                                                │
│     for consumer_id in subscribers:                                        │
│         contract = consumer_registry[consumer_id]                          │
│         if matches_context(signal, contract.context_filters):              │
│             eligible_consumers.append(consumer_id)                          │
│                                                                              │
│  3. SELECT VEHICLE                                                         │
│     vehicle = select_vehicle(eligible_consumers)                           │
│                                                                              │
│  4. DELIVER                                                                │
│     for consumer_id in eligible_consumers:                                  │
│         vehicle.deliver(signal, consumer_id)                               │
│                                                                              │
│  5. AGGREGATE RESULTS                                                      │
│     results = collect_results(eligible_consumers)                          │
│     return ROUTING_SUCCESS                                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2.2 Context Matching

```python
def matches_context(signal: Signal, filters: Dict[str, Any]) -> bool:
    """Check if signal matches consumer context filters."""

    for key, value in filters.items():
        # Special keys
        if key == "phase":
            if signal.source_phase != value:
                return False

        elif key == "min_priority":
            if signal.metadata.get("priority", 0) < value:
                return False

        elif key == "target_phases":
            if signal.source_phase not in value:
                return False

        # Generic metadata matching
        elif key in signal.metadata:
            if signal.metadata[key] != value:
                return False

        else:
            return False

    return True
```

## 4.3 Signal Processing Pipeline

### 4.3.1 Pipeline Stages

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SIGNAL PROCESSING PIPELINE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  STAGE 1: SIGNAL VALIDATION                                                 │
│  ┌────────────────────────────────────────────────────────────────┐       │
│  │  • Verify signal_type is registered                               │       │
│  │  • Validate payload against schema                                │       │
│  │  • Check timestamp is within acceptable range                     │       │
│  │  • Verify metadata completeness                                    │       │
│  └────────────────────────────────────────────────────────────────┘       │
│                              │                                             │
│                              ▼                                             │
│  STAGE 2: CONSUMER DISCOVERY                                               │
│  ┌────────────────────────────────────────────────────────────────┐       │
│  │  • Lookup signal type in inverted index                           │       │
│  │  • Get all subscribed consumers                                   │       │
│  │  • Filter by context requirements                                 │       │
│  │  • Check consumer health status                                   │       │
│  └────────────────────────────────────────────────────────────────┘       │
│                              │                                             │
│                              ▼                                             │
│  STAGE 3: VEHICLE SELECTION                                               │
│  ┌────────────────────────────────────────────────────────────────┐       │
│  │  • Determine optimal delivery mode                               │       │
│  │  • Select vehicle based on QoS requirements                      │       │
│  │  • Check vehicle capacity and availability                       │       │
│  └────────────────────────────────────────────────────────────────┘       │
│                              │                                             │
│                              ▼                                             │
│  STAGE 4: DELIVERY                                                          │
│  ┌────────────────────────────────────────────────────────────────┐       │
│  │  FOR EACH CONSUMER:                                              │       │
│  │    • Vehicle delivers signal                                     │       │
│  │    • Consumer processes signal                                   │       │
│  │    • Result collected and aggregated                             │       │
│  │    • Error handling with retry logic                             │       │
│  └────────────────────────────────────────────────────────────────┘       │
│                              │                                             │
│                              ▼                                             │
│  STAGE 5: RESULT AGGREGATION                                               │
│  ┌────────────────────────────────────────────────────────────────┐       │
│  │  • Collect all consumer results                                   │       │
│  │  • Update performance metrics                                     │       │
│  │  • Log completion statistics                                      │       │
│  │  • Trigger downstream signals if applicable                       │       │
│  └────────────────────────────────────────────────────────────────┘       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# CHAPTER 5: CONTRACTS SYSTEM

## 5.1 Irrigation Contracts

An **IrrigationContract** defines the terms of signal delivery between a source file and consumers.

### 5.1.1 Contract Structure

```python
@dataclass
class IrrigationContract:
    """Contract for signal irrigation from source to consumers."""

    # Identity
    contract_id: str                  # Unique contract identifier
    source_file: str                  # Source JSON file
    source_path: str                  # Full path to source
    source_phase: str                 # Origin phase

    # Delivery
    vehicles: List[str]               # Vehicles to use
    consumers: List[str]             # Target consumers
    vocabulary_aligned: bool         # Signal vocab alignment

    # Status
    gaps: List[str]                   # Known gaps
    status: ContractStatus            # DRAFT, ACTIVE, SUSPENDED, TERMINATED
```

### 5.1.2 Contract States

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CONTRACT STATE MACHINE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────┐    activate()    ┌─────────┐    suspend()    ┌─────────┐   │
│  │  DRAFT  │─────────────────→│  ACTIVE  │─────────────────→│SUSPENDED│   │
│  └─────────┘                  └─────────┘                  └─────────┘   │
│       │                             │                             │           │
│       │ terminate()                  │ terminate()                 │           │
│       ▼                             ▼                             ▼           │
│  ┌─────────┐                  ┌─────────┐                  ┌─────────┐   │
│  │TERMINATED│                  │TERMINATED│                  │TERMINATED│   │
│  └─────────┘                  └─────────┘                  └─────────┘   │
│                                                                              │
│  State Transitions:                                                         │
│  • DRAFT → ACTIVE: All vehicles and consumers available, vocab aligned    │
│  • ACTIVE → SUSPENDED: Gap detected or system issue                         │
│  • SUSPENDED → ACTIVE: Gap resolved                                         │
│  • Any → TERMINATED: Contract explicitly terminated                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 5.2 Contract Registry

The **ContractRegistry** manages all irrigation contracts.

### 5.2.1 Registry Structure

```python
class ContractRegistry:
    """Registry for irrigation contracts."""

    def __init__(self):
        self.irrigation_contracts: Dict[str, IrrigationContract] = {}
        self.publication_contracts: Dict[str, PublicationContract] = {}
        self.consumption_contracts: Dict[str, ConsumptionContract] = {}

    def register_irrigation(self, contract: IrrigationContract) -> None:
        """Register an irrigation contract."""

    def get_active_contracts(self) -> List[IrrigationContract]:
        """Get all active irrigation contracts."""

    def get_contracts_by_phase(self, phase: str) -> List[IrrigationContract]:
        """Get all contracts for a specific phase."""

    def validate_all_contracts(self) -> ValidationResult:
        """Validate all registered contracts."""
```

### 5.2.2 Contract Generation

Contracts are generated from CSV decision matrix:

```python
# From: sabana_final_decisiones.csv
# Columns: json_file_path, stage, phase, vehiculos_str, consumidores_str,
#          gaps_str, irrigability_bucket

def generate_contracts_from_csv(csv_path: str) -> ContractRegistry:
    """Generate contracts from CSV decision matrix."""

    registry = ContractRegistry()

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Skip non-canonical items
            if row.get("added_value") == "MARGINAL":
                continue
            if row.get("stage") == "External":
                continue

            # Determine status from irrigability
            if row.get("irrigability_bucket") == "irrigable_now":
                status = ContractStatus.ACTIVE
            else:
                status = ContractStatus.DRAFT

            # Create contract
            contract = IrrigationContract(
                contract_id=f"IC_{row['json_file_path'].replace('/', '_')}",
                source_file=row['json_file_path'].split('/')[-1],
                source_path=row['json_file_path'],
                source_phase=row['phase'],
                vehicles=parse_list(row['vehiculos_str']),
                consumers=parse_list(row['consumidores_str']),
                vocabulary_aligned=("VOCAB_SEÑALES_NO_ALINEADO" not in row['gaps_str']),
                gaps=parse_list(row['gaps_str']),
                status=status
            )

            registry.register_irrigation(contract)

    return registry
```

## 5.3 Irrigability Assessment

### 5.3.1 Irrigability Buckets

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      IRRIGABILITY BUCKETS                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  IRRIGABLE_NOW                                                          │  │
│  │  • All vehicles available                                             │  │
│  │  • All consumers available                                            │  │
│  │  • Vocabulary aligned                                                 │  │
│  │  • No gaps identified                                                 │  │
│  │  → Status: ACTIVE                                                     │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  NOT_IRRIGABLE_YET                                                    │  │
│  │  • Missing one or more vehicles                                       │  │
│  │  • Missing one or more consumers                                      │  │
│  │  • Vocabulary not aligned                                             │  │
│  │  • Gaps identified                                                    │  │
│  │  → Status: DRAFT                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  BLOCKED                                                               │  │
│  │  • Critical gaps that prevent irrigation                              │  │
│  │  • Missing vocabulary entirely                                        │  │
│  │  • Contract violations                                                │  │
│  │  → Status: SUSPENDED                                                  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.3.2 Gap Detection

```python
def detect_gaps(contract: IrrigationContract) -> List[str]:
    """Detect gaps that prevent irrigation."""

    gaps = []

    # Check vehicle availability
    for vehicle in contract.vehicles:
        if not vehicle_exists(vehicle):
            gaps.append(f"MISSING_VEHICLE:{vehicle}")

    # Check consumer availability
    for consumer in contract.consumers:
        if not consumer_exists(consumer):
            gaps.append(f"MISSING_CONSUMER:{consumer}")

    # Check vocabulary alignment
    if not contract.vocabulary_aligned:
        gaps.append("VOCAB_SEÑALES_NO_ALINEADO")
        gaps.append("VOCAB_CAPACIDADES_NO_ALINEADO")

    return gaps
```

---

# CHAPTER 6: CONSUMERS FRAMEWORK

## 6.1 Base Consumer

All consumers inherit from **BaseConsumer**, providing common functionality.

### 6.1.1 Base Consumer Interface

```python
class BaseConsumer(ABC):
    """Abstract base class for all SISAS consumers."""

    @abstractmethod
    def consume(self, signal: Signal) -> Optional[Dict[str, Any]]:
        """Consume a single signal."""
        pass

    def consume_batch(self, signals: List[Signal]) -> List[Dict[str, Any]]:
        """Consume multiple signals (default: sequential)."""
        results = []
        for signal in signals:
            result = self.consume(signal)
            if result:
                results.append(result)
        return results

    def get_consumption_contract(self) -> Dict[str, Any]:
        """Get the consumption contract for this consumer."""
        return {
            "consumer_id": self.consumer_id,
            "subscribed_signal_types": self.subscribed_signal_types,
            "required_capabilities": self._get_capabilities(),
        }

    def health_check(self) -> HealthStatus:
        """Check consumer health."""
        return HealthStatus(
            consumer_id=self.consumer_id,
            status="healthy",
            last_activity=self._last_activity,
        )
```

## 6.2 Phase Consumers

Each pipeline phase has a dedicated consumer.

### 6.2.1 Consumer Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE CONSUMERS                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  PHASE 0: Bootstrap & Validation                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  phase0_assembly_consumer                                             │  │
│  │  Signals: STATIC_LOAD, SIGNAL_PACK, INITIALIZATION                    │  │
│  │  Purpose: Load static resources and initialize pipeline                │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  PHASE 1: CPP Ingestion                                                    │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  phase1_extraction_consumer                                            │  │
│  │  Signals: MC01-MC10 (municipal chunks)                                │  │
│  │  Purpose: Extract structured content from municipal documents          │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  PHASE 2: Enrichment                                                       │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  phase2_enrichment_consumer                                            │  │
│  │  Signals: PATTERN_MATCHING, TF_IDF, SEMANTIC_SIMILARITY              │  │
│  │  Purpose: Enrich extracted content with patterns and semantics        │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  PHASE 3: Validation                                                       │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  phase3_validation_consumer                                            │  │
│  │  Signals: NORMATIVE_LOOKUP, COMPLIANCE_CHECK, VALIDATION_RESULT       │  │
│  │  Purpose: Validate content against norms and rules                     │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  PHASE 4-6: Aggregation                                                    │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  phase4_dimension_consumer   → Dimension aggregation (D1-D6)         │  │
│  │  phase5_policy_area_consumer  → Policy area aggregation (PA01-PA10)   │  │
│  │  phase6_cluster_consumer      → Cluster aggregation (CL01-CL04)       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  PHASE 7: Macro Aggregation                                                │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  phase7_meso_consumer                                                 │  │
│  │  Signals: AGGREGATION_ENGINE, MESO_LEVEL_SCORES                       │  │
│  │  Purpose: Aggregate dimension and policy area scores                   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  PHASE 8: Holistic Scoring                                                 │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  phase8_macro_consumer                                                │  │
│  │  Signals: HOLISTIC_SCORING, MACRO_LEVEL_AGGREGATION, FINAL_SCORE     │  │
│  │  Purpose: Compute holistic scores and recommendations                 │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  PHASE 9: Reporting                                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  phase9_report_consumer                                                │  │
│  │  Signals: TEMPLATE_ENGINE, REPORT_GENERATION, FINAL_OUTPUT           │  │
│  │  Purpose: Generate final reports and documentation                    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2.2 Consumer Implementation Example

```python
class Phase2EnrichmentConsumer(BaseConsumer):
    """Consumer for Phase 2 enrichment processing."""

    def __init__(self, config: Phase2EnrichmentConsumerConfig = None):
        self.config = config or Phase2EnrichmentConsumerConfig()
        self.consumer_id = "phase2_enrichment_consumer"
        self.subscribed_signal_types = [
            "PATTERN_MATCHING",
            "TF_IDF",
            "SEMANTIC_SIMILARITY",
        ]

        # Initialize NLP components
        self._pattern_matcher = PatternMatcher()
        self._tfidf_calculator = TfidfCalculator()
        self._semantic_comparator = SemanticComparator()

    def consume(self, signal: Signal) -> Optional[Dict[str, Any]]:
        """Consume enrichment signal."""

        if signal.signal_type == "PATTERN_MATCHING":
            return self._process_patterns(signal)
        elif signal.signal_type == "TF_IDF":
            return self._process_tfidf(signal)
        elif signal.signal_type == "SEMANTIC_SIMILARITY":
            return self._process_similarity(signal)

        return None

    def _process_patterns(self, signal: Signal) -> Dict[str, Any]:
        """Process pattern matching signal."""
        payload = signal.payload
        patterns = self._pattern_matcher.match(payload["text"])

        return {
            "consumer_id": self.consumer_id,
            "signal_id": signal.signal_id,
            "patterns_found": len(patterns),
            "patterns": patterns,
        }
```

## 6.3 Consumer Patterns

### 6.3.1 Synchronous Consumer

```python
class SynchronousConsumer(BaseConsumer):
    """Consumer that processes signals immediately."""

    def consume(self, signal: Signal) -> Optional[Dict[str, Any]]:
        """Process signal synchronously."""
        start_time = time.time()

        # Process immediately
        result = self._process(signal.payload)

        return {
            "consumer_id": self.consumer_id,
            "signal_id": signal.signal_id,
            "result": result,
            "processing_time_ms": (time.time() - start_time) * 1000,
        }
```

### 6.3.2 Asynchronous Consumer

```python
class AsynchronousConsumer(BaseConsumer):
    """Consumer that processes signals asynchronously."""

    async def consume_async(self, signal: Signal) -> Optional[Dict[str, Any]]:
        """Process signal asynchronously."""
        start_time = time.time()

        # Process asynchronously
        result = await self._process_async(signal.payload)

        return {
            "consumer_id": self.consumer_id,
            "signal_id": signal.signal_id,
            "result": result,
            "processing_time_ms": (time.time() - start_time) * 1000,
        }

    def consume(self, signal: Signal) -> Optional[Dict[str, Any]]:
        """Synchronous wrapper for async consumption."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.consume_async(signal))
```

### 6.3.3 Batch Consumer

```python
class BatchConsumer(BaseConsumer):
    """Consumer that accumulates and processes signals in batches."""

    def __init__(self, batch_size: int = 100, timeout_ms: int = 1000):
        self._batch_size = batch_size
        self._timeout_ms = timeout_ms
        self._buffer: List[Signal] = []
        self._last_flush = time.time()

    def consume(self, signal: Signal) -> Optional[Dict[str, Any]]:
        """Add signal to buffer, flush if batch is ready."""
        self._buffer.append(signal)

        should_flush = (
            len(self._buffer) >= self._batch_size or
            (time.time() - self._last_flush) * 1000 >= self._timeout_ms
        )

        if should_flush:
            return self.flush_buffer()

        return None

    def flush_buffer(self) -> Dict[str, Any]:
        """Process all buffered signals."""
        batch = self._buffer.copy()
        self._buffer.clear()
        self._last_flush = time.time()

        results = self._process_batch(batch)

        return {
            "consumer_id": self.consumer_id,
            "batch_size": len(batch),
            "results": results,
        }
```

---

# CHAPTER 7: VEHICLES SYSTEM

## 7.1 Vehicle Overview

**Vehicles** are the transport mechanism that delivers signals to consumers.

### 7.1.1 Vehicle Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          VEHICLE HIERARCHY                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                      Vehicle (Abstract Base)                               │
│                              │                                             │
│         ┌──────────────┼──────────────┬──────────────┐                     │
│         ▼              ▼               ▼              ▼                     │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│   │   Sync   │  │  Async   │  │  Batch   │  │ Priority │                │
│   │ Vehicle  │  │ Vehicle  │  │ Vehicle  │  │ Vehicle  │                │
│   └──────────┘  └──────────┘  └──────────┘  └──────────┘                │
│         │              │               │              │                     │
│         ▼              ▼               ▼              ▼                     │
│   Immediate     Concurrent      Accumulated     Ordered by                 │
│   delivery      execution       processing     priority                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.1.2 Vehicle Interface

```python
class Vehicle(ABC):
    """Abstract base class for signal delivery vehicles."""

    @abstractmethod
    def deliver(
        self,
        signal: Signal,
        consumer: BaseConsumer
    ) -> DeliveryResult:
        """Deliver signal to consumer."""
        pass

    @abstractmethod
    def deliver_batch(
        self,
        signals: List[Signal],
        consumers: List[BaseConsumer]
    ) -> List[DeliveryResult]:
        """Deliver multiple signals to multiple consumers."""
        pass

    @abstractmethod
    def get_capacity(self) -> int:
        """Get current capacity (0-100)."""
        pass

    @abstractmethod
    def get_status(self) -> VehicleStatus:
        """Get vehicle status."""
        pass
```

## 7.2 Vehicle Types

### 7.2.1 Synchronous Vehicle

```python
class SyncVehicle(Vehicle):
    """Vehicle for immediate synchronous delivery."""

    def deliver(
        self,
        signal: Signal,
        consumer: BaseConsumer
    ) -> DeliveryResult:
        """Deliver signal immediately."""
        try:
            start_time = time.time()
            result = consumer.consume(signal)
            elapsed_ms = (time.time() - start_time) * 1000

            return DeliveryResult(
                vehicle_id="sync_vehicle",
                consumer_id=consumer.consumer_id,
                signal_id=signal.signal_id,
                status="delivered",
                result=result,
                delivery_time_ms=elapsed_ms,
            )
        except Exception as e:
            return DeliveryResult(
                vehicle_id="sync_vehicle",
                consumer_id=consumer.consumer_id,
                signal_id=signal.signal_id,
                status="failed",
                error=str(e),
            )
```

### 7.2.2 Asynchronous Vehicle

```python
class AsyncVehicle(Vehicle):
    """Vehicle for concurrent asynchronous delivery."""

    def __init__(self, max_concurrent: int = 10):
        self._max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._active_tasks: Set[asyncio.Task] = set()

    async def deliver_async(
        self,
        signal: Signal,
        consumer: BaseConsumer
    ) -> DeliveryResult:
        """Deliver signal asynchronously."""
        async with self._semaphore:
            try:
                start_time = time.time()

                if hasattr(consumer, 'consume_async'):
                    result = await consumer.consume_async(signal)
                else:
                    # Run synchronous consume in thread pool
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        None, consumer.consume, signal
                    )

                elapsed_ms = (time.time() - start_time) * 1000

                return DeliveryResult(
                    vehicle_id="async_vehicle",
                    consumer_id=consumer.consumer_id,
                    signal_id=signal.signal_id,
                    status="delivered",
                    result=result,
                    delivery_time_ms=elapsed_ms,
                )
            except Exception as e:
                return DeliveryResult(
                    vehicle_id="async_vehicle",
                    consumer_id=consumer.consumer_id,
                    signal_id=signal.signal_id,
                    status="failed",
                    error=str(e),
                )

    def deliver(
        self,
        signal: Signal,
        consumer: BaseConsumer
    ) -> DeliveryResult:
        """Synchronous wrapper for async delivery."""
        loop = asyncio.get_event_loop()
        task = asyncio.create_task(self.deliver_async(signal, consumer))
        self._active_tasks.add(task)
        task.add_done_callback(self._active_tasks.discard)

        # Wait for completion
        loop.run_until_complete(asyncio.sleep(0))
        return self._get_task_result(task)
```

### 7.2.3 Batch Vehicle

```python
class BatchVehicle(Vehicle):
    """Vehicle for batch processing of signals."""

    def __init__(self, batch_size: int = 100, timeout_ms: int = 1000):
        self._batch_size = batch_size
        self._timeout_ms = timeout_ms
        self._pending_signals: Dict[str, List[Signal]] = {}

    def deliver(
        self,
        signal: Signal,
        consumer: BaseConsumer
    ) -> DeliveryResult:
        """Add signal to batch, process if batch is full."""
        consumer_id = consumer.consumer_id

        if consumer_id not in self._pending_signals:
            self._pending_signals[consumer_id] = []

        self._pending_signals[consumer_id].append(signal)

        should_flush = (
            len(self._pending_signals[consumer_id]) >= self._batch_size
        )

        if should_flush:
            return self._flush_consumer(consumer_id)

        return DeliveryResult(
            vehicle_id="batch_vehicle",
            consumer_id=consumer_id,
            signal_id=signal.signal_id,
            status="buffered",
        )

    def _flush_consumer(self, consumer_id: str) -> DeliveryResult:
        """Process all pending signals for a consumer."""
        signals = self._pending_signals.get(consumer_id, [])
        if not signals:
            return None

        consumer = self._get_consumer(consumer_id)
        results = consumer.consume_batch(signals)

        self._pending_signals[consumer_id] = []

        return DeliveryResult(
            vehicle_id="batch_vehicle",
            consumer_id=consumer_id,
            signal_id=f"batch_{len(signals)}",
            status="delivered",
            batch_results=results,
        )
```

### 7.2.4 Priority Vehicle

```python
class PriorityVehicle(Vehicle):
    """Vehicle that delivers signals based on priority."""

    def __init__(self):
        self._priority_queue: List[Tuple[int, Signal, BaseConsumer]] = []
        self._lock = threading.Lock()

    def deliver(
        self,
        signal: Signal,
        consumer: BaseConsumer
    ) -> DeliveryResult:
        """Add signal to priority queue."""
        priority = signal.metadata.get("priority", 0)

        with self._lock:
            heapq.heappush(self._priority_queue, (-priority, signal, consumer))

        # Process if queue is non-empty
        if self._priority_queue:
            return self._process_next()

        return DeliveryResult(
            vehicle_id="priority_vehicle",
            consumer_id=consumer.consumer_id,
            signal_id=signal.signal_id,
            status="queued",
            priority=priority,
        )

    def _process_next(self) -> DeliveryResult:
        """Process highest priority signal."""
        with self._lock:
            if not self._priority_queue:
                return None

            neg_priority, signal, consumer = heapq.heappop(self._priority_queue)
            priority = -neg_priority

        # Actually deliver the signal
        result = consumer.consume(signal)

        return DeliveryResult(
            vehicle_id="priority_vehicle",
            consumer_id=consumer.consumer_id,
            signal_id=signal.signal_id,
            status="delivered",
            result=result,
            priority=priority,
        )
```

## 7.3 Vehicle Selection

### 7.3.1 Selection Strategy

```python
def select_vehicle(
    consumers: List[BaseConsumer],
    signal: Signal
) -> Vehicle:
    """Select optimal vehicle based on consumer and signal characteristics."""

    # Check consumer preferences
    consumer_modes = [
        c.get_consumption_contract().get("delivery_mode", "SYNC")
        for c in consumers
    ]

    # Majority vote
    mode_counts = Counter(consumer_modes)
    preferred_mode = mode_counts.most_common(1)[0][0]

    # Select vehicle based on mode
    if preferred_mode == "ASYNC":
        return AsyncVehicle(max_concurrent=len(consumers))
    elif preferred_mode == "BATCH":
        return BatchVehicle(batch_size=100)
    elif preferred_mode == "PRIORITY":
        return PriorityVehicle()
    else:
        return SyncVehicle()
```

---

# CHAPTER 8: IRRIGATION PROTOCOL

## 8.1 Protocol Overview

The **IrrigationProtocol** is the master verification and synchronization system for SISAS.

### 8.1.1 Protocol Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      IRRIGATION PROTOCOL ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    IrrigationProtocol                                 │  │
│  │                                                                     │  │
│  │  ┌─────────────────────────────────────────────────────────────┐    │  │
│  │  │              InventoryVerifier                                 │    │  │
│  │  │  • Count JSON files in CQC                                     │    │  │
│  │  │  • Verify directory structure                                  │    │  │
│  │  │  • Check expected vs actual                                   │    │  │
│  │  └─────────────────────────────────────────────────────────────┘    │  │
│  │                                                                     │  │
│  │  ┌─────────────────────────────────────────────────────────────┐    │  │
│  │  │              MethodSynchronizer                                │    │  │
│  │  │  • Count method file entries                                   │    │  │
│  │  │  • Verify method structure                                     │    │  │
│  │  │  • Report synchronization status                                │    │  │
│  │  └─────────────────────────────────────────────────────────────┘    │  │
│  │                                                                     │  │
│  │  ┌─────────────────────────────────────────────────────────────┐    │  │
│  │  │              ConsumerCreator                                   │    │  │
│  │  │  • Verify consumer existence                                   │    │  │
│  │  │  • Create missing consumers                                    │    │  │
│  │  │  • Validate consumer contracts                                │    │  │
│  │  └─────────────────────────────────────────────────────────────┘    │  │
│  │                                                                     │  │
│  │  ┌─────────────────────────────────────────────────────────────┐    │  │
│  │  │              IrrigationExecutor                                 │    │  │
│  │  │  • Run complete protocol                                       │    │  │
│  │  │  • Generate reports                                            │    │  │
│  │  │  • Provide recommendations                                     │    │  │
│  │  └─────────────────────────────────────────────────────────────┘    │  │
│  │                                                                     │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 8.2 Verification Steps

### 8.2.1 Step 1: Inventory Verification

```python
class InventoryVerifier:
    """Verifies the real inventory of canonic_questionnaire_central."""

    def verify_inventory(self) -> InventoryReport:
        """Verify inventory against expected configuration."""

        report = InventoryReport()

        # Count JSON files
        json_files = list(cqc_path.rglob("*.json"))
        report.json_files_found = len(json_files)

        # Count by directory
        for json_file in json_files:
            parent_dir = str(json_file.parent.relative_to(cqc_path))
            report.directories_found[parent_dir] = \
                report.directories_found.get(parent_dir, 0) + 1

        # Check against expected
        if report.json_files_found == EXPECTED_JSON_FILES:
            report.verification_status = "verified"
        else:
            report.verification_status = "discrepancy"

        return report
```

### 8.2.2 Step 2: Method Synchronization

```python
class MethodSynchronizer:
    """Synchronizes method files to ensure correct entry counts."""

    def verify_method_file(self, file_name: str) -> MethodSyncReport:
        """Verify a single method file."""

        report = MethodSyncReport(file_name=file_name)

        # Load and count entries
        with open(method_file_path) as f:
            data = json.load(f)

        # Count entries (including nested methods)
        for key, value in data.items():
            report.entries_found += 1
            if isinstance(value, dict) and "methods" in value:
                report.entries_found += len(value["methods"])

        # Check against expected
        if report.entries_found == EXPECTED_METHOD_COUNT:
            report.sync_status = "synchronized"
        else:
            report.sync_status = "needs_sync"

        return report
```

### 8.2.3 Step 3: Consumer Verification

```python
class ConsumerCreator:
    """Creates and verifies SISAS consumers."""

    REQUIRED_CONSUMERS = {
        "phase0": ["phase0_assembly_consumer"],
        "phase1": ["phase1_extraction_consumer"],
        "phase2": ["phase2_enrichment_consumer"],
        "phase3": ["phase3_validation_consumer"],
        "phase4": ["phase4_dimension_consumer"],
        "phase5": ["phase5_policy_area_consumer"],
        "phase6": ["phase6_cluster_consumer"],
        "phase7": ["phase7_meso_consumer"],
        "phase8": ["phase8_macro_consumer"],
        "phase9": ["phase9_report_consumer"],
    }

    def verify_all_consumers(self) -> List[ConsumerCreationReport]:
        """Verify all required consumers exist."""

        reports = []

        for phase, consumers in self.REQUIRED_CONSUMERS.items():
            for consumer_name in consumers:
                consumer_path = consumers_path / phase / f"{consumer_name}.py"

                report = ConsumerCreationReport(
                    phase=phase,
                    consumer_name=consumer_name,
                )

                if consumer_path.exists():
                    report.creation_status = "exists"
                    report.file_path = str(consumer_path)
                else:
                    report.creation_status = "missing"

                reports.append(report)

        return reports
```

### 8.2.4 Step 4: Execution

```python
class IrrigationExecutor:
    """Executes the complete irrigation protocol."""

    def execute_irrigation(self) -> IrrigationExecutionReport:
        """Execute the complete irrigation protocol."""

        report = IrrigationExecutionReport()

        # Run all verification steps
        inventory_report = self.inventory_verifier.verify_inventory()
        method_reports = self.method_sync.verify_all_method_files()
        consumer_summary = self.consumer_creator.get_consumer_summary()

        # Execute irrigation script if available
        irrigation_script = sisas_path / "scripts" / "generate_contracts.py"

        if irrigation_script.exists():
            result = subprocess.run(
                [sys.executable, str(irrigation_script)],
                capture_output=True,
            )

            report.execution_status = "completed" if result.returncode == 0 else "partial"

        # Compile statistics
        report.contracts_executed = inventory_report.json_files_found
        report.consumers_active = consumer_summary["exists"]
        report.signals_dispatched = inventory_report.json_files_found

        return report
```

## 8.3 Protocol Output

### 8.3.1 Report Structure

```json
{
  "protocol_version": "1.0.0",
  "timestamp": "2026-01-19T19:15:11.615724",
  "steps": {
    "inventory": {
      "json_files_found": 489,
      "directories_count": 59,
      "verification_status": "verified",
      "discrepancies": []
    },
    "methods": {
      "total_files": 2,
      "synchronized": 0,
      "needs_sync": 2,
      "total_entries": 1417,
      "reports": [...]
    },
    "consumers": {
      "total_required": 10,
      "exists": 10,
      "missing": 0,
      "phases": {
        "phase0": 1,
        "phase1": 1,
        ...
      }
    },
    "execution": {
      "execution_status": "completed",
      "contracts_executed": 489,
      "signals_dispatched": 489,
      "consumers_active": 10
    }
  },
  "overall_status": "passed",
  "recommendations": []
}
```

---

# CHAPTER 9: INTEGRATION GUIDE

## 9.1 Quick Start

### 9.1.1 Basic Signal Emission

```python
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.signal import (
    Signal,
    SignalType
)

# Create a signal
signal = Signal(
    signal_id=blake3.blake3(b"test_payload").hexdigest()[:16],
    signal_type=SignalType.STATIC_LOAD,
    payload={"resource": "questionnaire", "version": "2.0.0"},
    timestamp=datetime.utcnow(),
    metadata={"source": "quickstart"},
    source_phase="phase0",
    correlation_id=None
)

# Emit via SDO
from canonic_questionnaire_central.resolver import SignalDistributionOrchestrator

sdo = SignalDistributionOrchestrator()
sdo.register_consumer(my_consumer, my_contract)
dispatch_result = sdo.dispatch(signal)
```

### 9.1.2 Consumer Registration

```python
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.consumers.phase2 import (
    phase2_enrichment_consumer
)

# Create consumer instance
consumer = phase2_enrichment_consumer.Phase2EnrichmentConsumer()

# Get contract
contract = consumer.get_consumption_contract()

# Register with SDO
sdo.register_consumer(consumer, contract)
```

## 9.2 Advanced Usage

### 9.2.1 Custom Consumer

```python
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.consumers.base_consumer import (
    BaseConsumer
)

class MyCustomConsumer(BaseConsumer):
    """Custom consumer for specific signal types."""

    def __init__(self):
        self.consumer_id = "my_custom_consumer"
        self.subscribed_signal_types = ["CUSTOM_SIGNAL_A", "CUSTOM_SIGNAL_B"]
        self._state = {}

    def consume(self, signal: Signal) -> Optional[Dict[str, Any]]:
        """Consume custom signals."""

        if signal.signal_type == "CUSTOM_SIGNAL_A":
            return self._process_signal_a(signal)
        elif signal.signal_type == "CUSTOM_SIGNAL_B":
            return self._process_signal_b(signal)

        return None

    def _process_signal_a(self, signal: Signal) -> Dict[str, Any]:
        """Process SIGNAL_A type."""
        payload = signal.payload
        # Custom processing logic
        return {
            "consumer_id": self.consumer_id,
            "processed": True,
            "result": f"Processed {payload['data']}"
        }

    def _process_signal_b(self, signal: Signal) -> Dict[str, Any]:
        """Process SIGNAL_B type."""
        payload = signal.payload
        # Custom processing logic
        return {
            "consumer_id": self.consumer_id,
            "processed": True,
            "result": f"Processed {payload['data']}"
        }

# Register custom consumer
custom_consumer = MyCustomConsumer()
custom_contract = custom_consumer.get_consumption_contract()
sdo.register_consumer(custom_consumer, custom_contract)
```

### 9.2.2 Batch Signal Dispatch

```python
# Create multiple signals
signals = [
    Signal(
        signal_id=blake3.blake3(f"signal_{i}".encode()).hexdigest()[:16],
        signal_type=SignalType.MC01,
        payload={"chunk_id": i, "data": f"chunk_{i}"},
        timestamp=datetime.utcnow(),
        metadata={},
        source_phase="phase1",
        correlation_id=None
    )
    for i in range(100)
]

# Dispatch batch
results = sdo.dispatch_batch(signals)

# Process results
for result in results:
    if result.status == "delivered":
        print(f"Delivered {result.signal_id} to {result.consumer_id}")
    else:
        print(f"Failed {result.signal_id}: {result.error}")
```

### 9.2.3 Vehicle Selection

```python
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vehicles.async_vehicle import (
    AsyncVehicle
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vehicles.batch_vehicle import (
    BatchVehicle
)

# Create specific vehicles
async_vehicle = AsyncVehicle(max_concurrent=20)
batch_vehicle = BatchVehicle(batch_size=50, timeout_ms=2000)

# Use vehicles directly
result = async_vehicle.deliver(signal, consumer)

# Or let SDO select optimal vehicle
sdo.register_vehicle("async", async_vehicle)
sdo.register_vehicle("batch", batch_vehicle)
```

## 9.3 Integration with FARFAN Pipeline

### 9.3.1 Phase Integration

```python
from farfan_pipeline.orchestration.orchestrator import UnifiedOrchestrator
from farfan_pipeline.orchestration.factory import UnifiedFactory, FactoryConfig

# Create orchestrator with SISAS enabled
factory = UnifiedFactory(
    config=FactoryConfig(
        project_root=Path("."),
        sisas_enabled=True,
    )
)

# Get SISAS central
sisas_central = factory.get_sisas_central()

# Register consumers for each phase
for phase_num in range(10):
    phase = f"phase{phase_num}"
    consumer = factory._create_consumer(phase)
    sisas_central.register_consumer(consumer, consumer.get_consumption_contract())

# Execute pipeline
orchestrator = UnifiedOrchestrator(config=config)
result = orchestrator.execute()
```

### 9.3.2 Contract Execution

```python
# Execute 300 contracts via factory
contracts = factory.load_contracts()

for contract_id, contract in contracts.items():
    if contract.get("status") == "ACTIVE":
        result = factory.execute_contract(
            contract_id,
            input_data={"plan_text": "..."}
        )

        print(f"Contract {contract_id}: {result['status']}")
```

---

# CHAPTER 10: REFERENCE

## 10.1 API Reference

### 10.1.1 SignalDistributionOrchestrator

```python
class SignalDistributionOrchestrator:
    """Central signal routing coordinator."""

    def __init__(self):
        """Initialize SDO with empty registries."""

    def register_consumer(
        self,
        consumer: BaseConsumer,
        contract: ConsumptionContract
    ) -> None:
        """Register a consumer with its consumption contract."""

    def unregister_consumer(self, consumer_id: str) -> None:
        """Unregister a consumer by ID."""

    def dispatch(self, signal: Signal) -> DispatchResult:
        """Dispatch a single signal to matching consumers."""

    def dispatch_batch(
        self,
        signals: List[Signal]
    ) -> List[DispatchResult]:
        """Dispatch multiple signals efficiently."""

    def health_check(self) -> HealthStatus:
        """Check health of all registered consumers."""

    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""

    def get_subscribers(
        self,
        signal_type: SignalType
    ) -> List[str]:
        """Get all consumer IDs subscribed to a signal type."""

    def shutdown(self) -> None:
        """Gracefully shutdown the orchestrator."""
```

### 10.1.2 Signal

```python
@dataclass(frozen=True)
class Signal:
    """Immutable atomic unit of signal transmission."""

    signal_id: str
    signal_type: SignalType
    payload: Any
    timestamp: datetime
    metadata: Dict[str, Any]
    source_phase: str
    correlation_id: Optional[str]

    def with_metadata(self, **kwargs) -> 'Signal':
        """Create a new signal with additional metadata."""

    def correlate(self, signal_id: str) -> 'Signal':
        """Create a correlated signal."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert signal to dictionary."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Signal':
        """Create signal from dictionary."""
```

### 10.1.3 BaseConsumer

```python
class BaseConsumer(ABC):
    """Abstract base class for all SISAS consumers."""

    consumer_id: str
    subscribed_signal_types: List[str]

    @abstractmethod
    def consume(self, signal: Signal) -> Optional[Dict[str, Any]]:
        """Consume a single signal."""

    def consume_batch(
        self,
        signals: List[Signal]
    ) -> List[Dict[str, Any]]:
        """Consume multiple signals."""

    def get_consumption_contract(self) -> Dict[str, Any]:
        """Get consumption contract."""

    def health_check(self) -> HealthStatus:
        """Check consumer health."""

    def flush(self) -> List[Dict[str, Any]]:
        """Flush any buffered signals."""
```

## 10.2 Configuration

### 10.2.1 Signal Types Configuration

```json
{
  "SIGNAL_TYPES": {
    "STATIC_LOAD": {
      "description": "Static resource loading signal",
      "phase": "phase0",
      "payload_schema": {
        "type": "object",
        "properties": {
          "resource": {"type": "string"},
          "version": {"type": "string"}
        },
        "required": ["resource"]
      }
    },
    "MC01": {
      "description": "Municipal Chunk 01",
      "phase": "phase1",
      "payload_schema": {
        "type": "object",
        "properties": {
          "chunk_id": {"type": "integer"},
          "municipality": {"type": "string"},
          "content": {"type": "string"}
        }
      }
    }
  }
}
```

### 10.2.2 Consumer Configuration

```json
{
  "CONSUMERS": {
    "phase0_assembly_consumer": {
      "class": "phase0.phase0_assembly_consumer.Phase0AssemblyConsumer",
      "subscribed_signal_types": [
        "STATIC_LOAD",
        "SIGNAL_PACK",
        "INITIALIZATION"
      ],
      "delivery_mode": "ASYNC",
      "max_concurrent": 5
    },
    "phase1_extraction_consumer": {
      "class": "phase1.phase1_extraction_consumer.Phase1ExtractionConsumer",
      "subscribed_signal_types": ["MC01", "MC02", "MC03", "MC04", "MC05"],
      "delivery_mode": "BATCH",
      "batch_size": 50
    }
  }
}
```

## 10.3 Error Handling

### 10.3.1 Error Types

```python
class SISASError(Exception):
    """Base exception for SISAS errors."""
    pass

class SignalDispatchError(SISASError):
    """Raised when signal dispatch fails."""
    pass

class ConsumerRegistrationError(SISASError):
    """Raised when consumer registration fails."""
    pass

class VehicleError(SISASError):
    """Raised when vehicle operation fails."""
    pass

class ContractViolationError(SISASError):
    """Raised when contract terms are violated."""
    pass
```

### 10.3.2 Error Handling Pattern

```python
try:
    result = sdo.dispatch(signal)

except SignalDispatchError as e:
    logger.error("Signal dispatch failed", signal_id=signal.signal_id, error=str(e))

    # Retry logic
    if retry_count < MAX_RETRIES:
        sdo.dispatch(signal)  # Retry

except ConsumerRegistrationError as e:
    logger.error("Consumer not registered", consumer_id=consumer_id)

    # Register consumer
    sdo.register_consumer(consumer, contract)

except Exception as e:
    logger.error("Unexpected error", error=str(e), exc_info=True)
```

## 10.4 Performance Considerations

### 10.4.1 Optimization Guidelines

| Aspect | Recommendation |
|--------|---------------|
| **Signal Size** | Keep payloads under 1MB for optimal performance |
| **Batch Size** | Use batch sizes of 50-100 for throughput |
| **Async Concurrency** | Limit to 10-20 concurrent operations |
| **Consumer Count** | Design for 10-50 consumers per signal type |
| **Vehicle Selection** | Use async for I/O-bound, batch for CPU-bound |

### 10.4.2 Monitoring

```python
# Get SDO metrics
metrics = sdo.get_metrics()

print(f"Signals dispatched: {metrics['signals_dispatched']}")
print(f"Signals delivered: {metrics['signals_delivered']}")
print(f"Signals failed: {metrics['signals_failed']}")
print(f"Average delivery time: {metrics['avg_delivery_time_ms']}ms")
print(f"Active consumers: {metrics['active_consumers']}")

# Get consumer health
health = sdo.health_check()

for consumer_status in health.consumer_statuses:
    print(f"{consumer_status.consumer_id}: {consumer_status.status}")
```

---

# APPENDICES

## Appendix A: Signal Type Reference

Complete list of all signal types in SISAS.

| Signal Type | Phase | Description | Payload Schema |
|-------------|-------|-------------|----------------|
| STATIC_LOAD | 0 | Static resource loading | `{"resource": str, "version": str}` |
| SIGNAL_PACK | 0 | Signal bundle delivery | `{"signals": List[Signal]}` |
| INITIALIZATION | 0 | System initialization | `{"config": Dict}` |
| MC01-MC10 | 1 | Municipal chunk extraction | `{"chunk_id": int, "content": str}` |
| PATTERN_MATCHING | 2 | Pattern detection | `{"patterns": List[str]}` |
| TF_IDF | 2 | TF-IDF calculation | `{"document": str, "terms": List[str]}` |
| SEMANTIC_SIMILARITY | 2 | Semantic similarity | `{"text1": str, "text2": str}` |
| NORMATIVE_LOOKUP | 3 | Normative lookup | `{"query": str, "norms": List[str]}` |
| COMPLIANCE_CHECK | 3 | Compliance validation | `{"content": str, "rules": List[str]}` |
| DIMENSION_AGGREGATION | 4 | Dimension score aggregation | `{"dimension": str, "scores": List[float]}` |
| POLICY_AREA_AGGREGATION | 5 | Policy area aggregation | `{"policy_area": str, "scores": List[float]}` |
| CLUSTER_AGGREGATION | 6 | Cluster aggregation | `{"cluster": str, "scores": List[float]}` |
| AGGREGATION_ENGINE | 7 | Meso-level aggregation | `{"aggregations": Dict}` |
| HOLISTIC_SCORING | 8 | Holistic scoring | `{"factors": Dict[str, float]}` |
| TEMPLATE_ENGINE | 9 | Report template engine | `{"template": str, "data": Dict}` |
| REPORT_GENERATION | 9 | Report generation | `{"format": str, "content": Dict}` |
| FINAL_OUTPUT | 9 | Final output | `{"output_path": str, "data": Dict}` |

## Appendix B: Consumer Reference

Complete list of all consumers in SISAS.

| Consumer ID | Phase | Signal Types | Delivery Mode |
|-------------|-------|---------------|---------------|
| phase0_assembly_consumer | 0 | STATIC_LOAD, SIGNAL_PACK, INITIALIZATION | ASYNC |
| phase1_extraction_consumer | 1 | MC01-MC10 | BATCH |
| phase2_enrichment_consumer | 2 | PATTERN_MATCHING, TF_IDF, SEMANTIC_SIMILARITY | ASYNC |
| phase3_validation_consumer | 3 | NORMATIVE_LOOKUP, COMPLIANCE_CHECK, VALIDATION_RESULT | SYNC |
| phase4_dimension_consumer | 4 | DIMENSION_AGGREGATION, D1_SCORE-D6_SCORE | BATCH |
| phase5_policy_area_consumer | 5 | POLICY_AREA_AGGREGATION, PA01_SCORE-PA10_SCORE | BATCH |
| phase6_cluster_consumer | 6 | CLUSTER_AGGREGATION, CL01_SCORE-CL04_SCORE | BATCH |
| phase7_meso_consumer | 7 | AGGREGATION_ENGINE, MESO_LEVEL_SCORES | ASYNC |
| phase8_macro_consumer | 8 | HOLISTIC_SCORING, MACRO_LEVEL_AGGREGATION, FINAL_SCORE | SYNC |
| phase9_report_consumer | 9 | TEMPLATE_ENGINE, REPORT_GENERATION, FINAL_OUTPUT | ASYNC |

## Appendix C: Configuration Reference

Complete configuration options for SISAS.

```yaml
# SISAS Configuration
sisas:
  # Orchestrator settings
  orchestrator:
    max_concurrent_displays: 20
    default_vehicle: "async"
    health_check_interval_seconds: 60

  # Vehicle settings
  vehicles:
    async:
      max_concurrent: 20
      queue_size: 1000
    batch:
      batch_size: 100
      timeout_ms: 2000
    priority:
      queue_size: 5000

  # Consumer settings
  consumers:
    auto_register: true
    health_check_enabled: true
    retry_failed_consumers: true
    max_retries: 3

  # Signal settings
  signals:
    max_payload_size_mb: 1
    ttl_seconds: 3600
    compression_enabled: false

  # Metrics settings
  metrics:
    enabled: true
    retention_days: 30
    export_format: "json"
```

## Appendix D: Troubleshooting

### D.1 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Signal not delivered | Consumer not registered | Register consumer with SDO |
| Signal not delivered | Signal type mismatch | Check subscribed_signal_types |
| Consumer timeout | Processing too slow | Increase timeout or use async |
| Memory leak | Signal buffer not flushed | Call flush() periodically |
| Contract violation | Gap in vocabulary | Align vocab between source/consumer |

### D.2 Debug Mode

```python
import logging
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core import signal_distribution_orchestrator

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Enable SDO debug mode
sdo = SignalDistributionOrchestrator(debug=True)

# Trace signal flow
sdo.set_trace_enabled(True)

# Get detailed logs
result = sdo.dispatch(signal)
print(result.to_dict())
```

---

## DOCUMENTATION VERSION

**Version**: 2.0.0
**Last Updated**: 2026-01-19
**Maintained By**: FARFAN Pipeline Architecture Team

---

## CHANGELOG

### v2.0.0 (2026-01-19)
- Complete rewrite of SISAS ecosystem documentation
- Added all 10 phase consumers
- Implemented irrigation protocol
- Added contract system documentation
- Added vehicle system documentation
- Added integration guide

### v1.0.0 (2026-01-01)
- Initial SISAS documentation
- Core signal system
- Base consumer framework
- Initial SDO implementation

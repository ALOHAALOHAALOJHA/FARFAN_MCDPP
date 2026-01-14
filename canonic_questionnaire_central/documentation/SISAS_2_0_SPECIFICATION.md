# SISAS 2.0: Signal Irrigation System Architecture Specification

## SOTA Frontier Implementation Document

**Version:** 2.0.0  
**Date:** 2026-01-14  
**Status:** IMPLEMENTATION READY  
**Author:** F.A.R.F.A.N Pipeline Team

---

## EXECUTIVE SUMMARY

This document specifies the complete transformation of SISAS from a **static data loader** to a **true event-driven signal system**. The current implementation (v1.x) achieved 85% effectiveness as a data assembly mechanism but lacks the dynamic signal routing, pub/sub architecture, and real-time irrigation capabilities promised by its name.

SISAS 2.0 delivers:

| Capability | v1.x (Current) | v2.0 (This Spec) |
|------------|----------------|------------------|
| Signal Routing | Static paths | Dynamic pub/sub |
| Consumer Matching | Implicit | Capability-based |
| Deduplication | None | Content-hash based |
| Dead Letters | None | Full persistence |
| Audit Trail | Partial | Complete |
| Value Gating | None | Empirical threshold |
| Real-time Dispatch | No | Yes |

---

## ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SISAS 2.0 ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐                                                        │
│  │   EXTRACTORS     │                                                        │
│  │  ───────────     │                                                        │
│  │  MC05 Financial  │──┐                                                     │
│  │  MC08 Causal     │──┼──► CREATE SIGNALS                                   │
│  │  MC09 Institut.  │──┤                                                     │
│  │  MC01-MC10 etc   │──┘                                                     │
│  └──────────────────┘                                                        │
│            │                                                                 │
│            ▼                                                                 │
│  ┌──────────────────────────────────────────────────────────────────┐       │
│  │           SIGNAL DISTRIBUTION ORCHESTRATOR (SDO)                  │       │
│  │  ────────────────────────────────────────────────────────────────│       │
│  │                                                                   │       │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐             │       │
│  │  │VALIDATE │──│ DEDUP   │──│ VALUE   │──│ ROUTE   │             │       │
│  │  │ SCOPE   │  │ CHECK   │  │ GATE    │  │ MATCH   │             │       │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘             │       │
│  │       │            │            │            │                   │       │
│  │       ▼            ▼            ▼            ▼                   │       │
│  │  ┌─────────────────────────────────────────────────────────┐    │       │
│  │  │                   DEAD LETTER QUEUE                      │    │       │
│  │  │  - INVALID_SCOPE    - LOW_VALUE    - NO_CONSUMER        │    │       │
│  │  │  - DUPLICATE        - HANDLER_ERROR                      │    │       │
│  │  └─────────────────────────────────────────────────────────┘    │       │
│  │                                                                   │       │
│  └──────────────────────────────────────────────────────────────────┘       │
│            │                                                                 │
│            ▼                                                                 │
│  ┌──────────────────────────────────────────────────────────────────┐       │
│  │                    REGISTERED CONSUMERS                           │       │
│  │  ────────────────────────────────────────────────────────────────│       │
│  │                                                                   │       │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │       │
│  │  │  PHASE 1    │  │  PHASE 2    │  │  PHASE 3    │              │       │
│  │  │ Extraction  │  │ Enrichment  │  │ Validation  │              │       │
│  │  │ MC05,08,09  │  │ PATTERN,KW  │  │ NORMATIVE   │              │       │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │       │
│  │                                                                   │       │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │       │
│  │  │  PHASE 4-6  │  │  PHASE 7    │  │  PHASE 8    │              │       │
│  │  │  Scoring    │  │  MESO Agg   │  │  MACRO Agg  │              │       │
│  │  │ MICRO_SCORE │  │ MESO_SCORE  │  │ MACRO_SCORE │              │       │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │       │
│  │                                                                   │       │
│  └──────────────────────────────────────────────────────────────────┘       │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────┐       │
│  │                       AUDIT TRAIL                                 │       │
│  │  - Every signal dispatch logged                                   │       │
│  │  - Every delivery logged                                          │       │
│  │  - Every rejection logged with reason                             │       │
│  └──────────────────────────────────────────────────────────────────┘       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## CORE COMPONENTS

### 1. Signal (Atomic Unit)

```python
@dataclass
class Signal:
    signal_id: str           # UUID
    signal_type: SignalType  # MC05, MC08, MC09, etc.
    scope: SignalScope       # {phase, policy_area, slot}
    payload: Any             # Extracted data
    provenance: SignalProvenance  # Full audit trail
    capabilities_required: List[str]  # Consumer requirements
    empirical_availability: float     # 0.0-1.0 from calibration
    enrichment: bool         # True = adds value beyond raw extraction
    timestamp: datetime
```

**Key Properties:**
- **Immutable after dispatch** - modifications create new signals
- **Self-validating** - validate() checks integrity
- **Hashable** - content_hash() for deduplication
- **Serializable** - to_dict() / from_dict()

### 2. Signal Scope (Routing Coordinates)

```python
@dataclass
class SignalScope:
    phase: str       # phase_0 through phase_9
    policy_area: str # PA01-PA10, ALL, CROSS_CUTTING
    slot: str        # D1-Q1 format or ALL
```

**Scope Matching Rules:**
- Exact match or wildcard (ALL)
- Consumer must declare scopes it listens to
- Signal must match at least one consumer scope

### 3. Signal Distribution Orchestrator (SDO)

The **heart of SISAS 2.0** - replaces passive data loading with active pub/sub.

**Dispatch Pipeline:**
```
Signal → VALIDATE → DEDUP → VALUE_GATE → ROUTE → DELIVER
              ↓         ↓         ↓          ↓
         DEAD_LETTER (on failure at any stage)
```

**Validation Rules:**
```json
{
  "thresholds": {
    "empirical_availability_min": 0.30
  },
  "routing": {
    "phase_1": ["MC01", "MC02", "MC03", "MC04", "MC05", "MC06", "MC07", "MC08", "MC09", "MC10"]
  },
  "capabilities_required": {
    "MC05": ["NUMERIC_PARSING", "FINANCIAL_ANALYSIS"]
  }
}
```

### 4. Consumer Registration

```python
sdo.register_consumer(
    consumer_id="phase_1_extraction",
    scopes=[{"phase": "phase_1", "policy_area": "ALL", "slot": "ALL"}],
    capabilities=["NUMERIC_PARSING", "FINANCIAL_ANALYSIS", "CAUSAL_INFERENCE", ...],
    handler=phase_1_handler_function
)
```

**Matching Algorithm:**
1. Check if signal scope matches any consumer scope
2. Check if consumer has ALL required capabilities
3. If both pass → deliver to consumer

### 5. Dead Letter Queue

Signals that cannot be delivered are persisted with reason:

| Reason | Description |
|--------|-------------|
| INVALID_SCOPE | Signal type not allowed in declared phase |
| DUPLICATE | Content hash collision within dedup window |
| LOW_VALUE | empirical_availability below threshold |
| NO_CONSUMER | No registered consumer matches scope+capabilities |
| CAPABILITY_MISMATCH | Consumer lacks required capabilities |
| HANDLER_ERROR | Consumer handler threw exception |
| VALIDATION_FAILED | Signal failed integrity validation |

**Persistence:**
```
_registry/dead_letter/
├── {uuid1}.json
├── {uuid2}.json
└── ...
```

### 6. Audit Trail

Every operation is logged:

```python
@dataclass
class AuditEntry:
    entry_id: str
    action: str  # DISPATCHED, DELIVERED, REJECTED, DEAD_LETTERED
    signal_id: str
    signal_type: str
    consumer_id: Optional[str]
    detail: str
    timestamp: datetime
```

---

## EXTRACTORS (Signal Producers)

### MC05: Financial Chain Extractor

**Purpose:** Extract financial/budgetary amounts from text

**Patterns:**
- `$X millones/billones`
- `X millones de pesos`
- `presupuesto de $X`
- `inversión de/por $X`

**Output Signal:**
```json
{
  "signal_type": "MC05",
  "scope": {"phase": "phase_1", "policy_area": "PA01", "slot": "D1-Q1"},
  "payload": {
    "amount": 150000000000,
    "currency": "COP",
    "unit": "millones",
    "context_snippet": "...asignación de $150 millones para..."
  },
  "empirical_availability": 0.85
}
```

### MC08: Causal Verb Extractor

**Purpose:** Extract causal relationships (action → connector → outcome)

**Verb Categories:**
- TRANSFORMATIVE: garantizar, fortalecer, implementar
- CORRECTIVE: reducir, eliminar, prevenir
- STRUCTURAL: establecer, crear, diseñar
- MONITORING: verificar, evaluar, monitorear

**Output Signal:**
```json
{
  "signal_type": "MC08",
  "scope": {"phase": "phase_1", "policy_area": "PA02", "slot": "D6-Q1"},
  "payload": {
    "action_verb": "fortalecer",
    "connector": "mediante",
    "outcome": "mejora",
    "chain_structure": "VERB-CONNECTOR-OUTCOME",
    "confidence": 0.85
  },
  "empirical_availability": 0.72
}
```

### MC09: Institutional NER Extractor

**Purpose:** Extract institutional entities

**Entity Types:**
- NATIONAL: Ministerios, Departamentos, Agencias
- TERRITORIAL: Gobernaciones, Alcaldías, Secretarías
- JUSTICE: Juzgados, Tribunales, Fiscalía
- INTERNATIONAL: ONU, PNUD, UNICEF
- PDET_SPECIFIC: ART, CTJT, PNIS

**Output Signal:**
```json
{
  "signal_type": "MC09",
  "scope": {"phase": "phase_1", "policy_area": "PA05", "slot": "D2-Q2"},
  "payload": {
    "entity_name": "Agencia de Renovación del Territorio",
    "entity_type": "PDET_SPECIFIC",
    "entity_id": "ART",
    "occurrences": 3,
    "confidence": 0.9
  },
  "empirical_availability": 0.68
}
```

---

## INTEGRATION WITH RESOLVER

The existing `CanonicalQuestionnaireResolver` gains SDO integration:

```python
class CanonicalQuestionnaireResolver:
    def __init__(self, base_path: str):
        # ... existing init ...
        
        # NEW: Initialize SDO
        rules_path = self.base_path / "_registry/irrigation_validation_rules.json"
        self.sdo = SignalDistributionOrchestrator(str(rules_path))
        
        # Register phase consumers
        self._register_consumers()
    
    def _register_consumers(self):
        self.sdo.register_consumer(
            consumer_id="phase_0_assembly",
            scopes=[{"phase": "phase_0", "policy_area": "ALL", "slot": "ALL"}],
            capabilities=["STATIC_LOAD", "SIGNAL_PACK"],
            handler=self._handle_phase_0
        )
        # ... more consumers
```

---

## METRICS & OBSERVABILITY

### Health Check

```python
sdo.health_check()
# Returns:
{
  "status": "HEALTHY",  # or "DEGRADED"
  "dead_letter_rate": 0.02,
  "error_rate": 0.01,
  "consumers_healthy": 8,
  "consumers_total": 9,
  "metrics": {
    "signals_dispatched": 15423,
    "signals_delivered": 15100,
    "signals_rejected": 200,
    "signals_deduplicated": 123,
    "dead_letters": 200,
    "consumer_errors": 50
  }
}
```

### Per-Consumer Stats

```python
sdo.get_consumer_stats()
# Returns:
{
  "phase_1_extraction": {
    "signals_processed": 5000,
    "errors": 10,
    "enabled": True
  },
  ...
}
```

---

## FILE STRUCTURE

```
canonic_questionnaire_central/
├── core/                           # NEW: SISAS Core
│   ├── __init__.py
│   ├── signal.py                   # Signal, SignalType, SignalScope
│   └── signal_distribution_orchestrator.py  # SDO
├── _registry/
│   ├── irrigation_validation_rules.json  # NEW: Routing rules
│   ├── dead_letter/                # NEW: Failed signals
│   └── ... (existing)
└── ... (existing)

src/farfan_pipeline/infrastructure/irrigation_using_signals/
├── extractors/                     # NEW: Signal producers
│   ├── __init__.py
│   ├── base_extractor.py
│   ├── financial_chain_extractor.py  # MC05
│   ├── causal_verb_extractor.py      # MC08
│   └── institutional_ner_extractor.py # MC09
└── ... (existing SISAS folder)
```

---

## IMPLEMENTATION CHECKLIST

### Phase 1: Foundation (Week 1) ✅ COMPLETED
- [x] `canonic_questionnaire_central/core/signal.py`
- [x] `canonic_questionnaire_central/core/signal_distribution_orchestrator.py`
- [x] `_registry/irrigation_validation_rules.json`
- [x] `_registry/dead_letter/` directory

### Phase 2: Extractors (Week 2) ✅ COMPLETED
- [x] `extractors/base_extractor.py`
- [x] `extractors/financial_chain_extractor.py` (MC05)
- [x] `extractors/causal_verb_extractor.py` (MC08)
- [x] `extractors/institutional_ner_extractor.py` (MC09)

### Phase 3: Resolver Integration (Week 3) ✅ COMPLETED
- [x] Modify `resolver.py` to initialize SDO (v2.0.0)
- [x] Register 10 phase consumers (phase_0 through phase_9)
- [x] Wire extractors via `ExtractorOrchestrator`
- [x] Add `dispatch_signal()` and `get_sdo_health()` methods

### Phase 4: Testing & Validation (Week 4) ✅ COMPLETED
- [x] Unit tests for Signal, SDO (25 tests)
- [x] Integration tests for extractors (10 tests)
- [x] Dead letter queue tests
- [x] Keyword consolidation (2043 keywords across 10 PAs)
- [x] Documentation updates

---

## SUCCESS METRICS

After full implementation:

| Metric | Target |
|--------|--------|
| Signals with full audit trail | 100% |
| Dead letter persistence rate | 100% |
| Deduplication accuracy | >99% |
| Capability matching enforcement | 100% |
| Value gating enforcement | 100% |
| Consumer error rate | <5% |
| Dead letter rate | <10% |

---

## MIGRATION PATH

1. **Week 1-2:** Deploy core + extractors (no breaking changes)
2. **Week 3:** Integrate SDO into resolver (backward compatible)
3. **Week 4:** Enable SDO routing for new documents
4. **Week 5:** Migrate existing flows to SDO
5. **Week 6:** Deprecate v1.x static loading paths

---

## APPENDIX: Signal Type Reference

| Type | Phase | Description | Empirical Availability |
|------|-------|-------------|----------------------|
| MC01 | 1 | Structural markers | 0.92 |
| MC02 | 1 | Quantitative triplets | 0.78 |
| MC03 | 1 | Normative references | 0.85 |
| MC04 | 1 | Programmatic hierarchy | 0.71 |
| MC05 | 1 | Financial chains | 0.85 |
| MC06 | 1 | Population disaggregation | 0.65 |
| MC07 | 1 | Temporal markers | 0.88 |
| MC08 | 1 | Causal verbs | 0.72 |
| MC09 | 1 | Institutional network | 0.68 |
| MC10 | 1 | Semantic relationships | 0.55 |
| PATTERN_ENRICHMENT | 2 | Pattern matching | N/A |
| KEYWORD_ENRICHMENT | 2 | Keyword matching | N/A |
| NORMATIVE_VALIDATION | 3 | Compliance check | N/A |
| MICRO_SCORE | 4-6 | Question scoring | N/A |
| MESO_AGGREGATION | 7 | Cluster aggregation | N/A |
| MACRO_AGGREGATION | 8 | Final aggregation | N/A |

---

**END OF SPECIFICATION**

*This document represents the complete technical specification for SISAS 2.0 SOTA Frontier implementation.*

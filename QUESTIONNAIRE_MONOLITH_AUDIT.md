# QUESTIONNAIRE MONOLITH - SIGNAL SYSTEM ARCHITECTURE

**Date**: 2025-12-02  
**Nature**: NOT just questions - It's a **SIGNAL IRRIGATION SYSTEM**  
**Size**: 67,261 lines | 300 signal nodes | Cross-cutting patterns

---

## 🎯 WHAT IT REALLY IS

This is **NOT** a simple questionnaire. It's a:

```
📡 SIGNAL SYSTEM MONOLITH
├── Questions (text) ← Surface layer
├── Patterns (regex) ← Detection layer
├── Evidence (expected_elements) ← Validation layer
├── Methods (method_sets) ← Analysis layer
├── Contracts (failure_contract) ← Enforcement layer
└── Signals ← Cross-cutting irrigation system
```

### Your Architecture Vision:

```
SIGNALS as SATELLITAL COMPONENT
    ↓ (cross-cutting)
    ↓ irrigates →→→
    ↓
All Pipeline Processes (horizontal dimension)
```

**Key Insight**: Signals are NOT about questions. They're about:
- **Pattern detection** (regex, NLP)
- **Evidence extraction** (what must be present)
- **Cross-cutting concerns** (flow through entire pipeline)
- **Validation contracts** (what invalidates)

---

## 🔬 SIGNAL STRUCTURE (per micro-question)

Each of the 300 "questions" is actually a **SIGNAL NODE** with:

### 1. **PATTERNS** (Detection Layer)
```json
{
  "patterns": [
    {
      "id": "PAT-Q001-000",
      "category": "TEMPORAL",
      "match_type": "REGEX",
      "pattern": "...",
      "flags": "i",
      "confidence_weight": 0.8,
      "specificity": 0.9,
      "validation_rule": "...",
      "context_requirement": "...",
      "semantic_expansion": "...",
      "context_scope": "..."
    }
  ]
}
```

**Purpose**: Detect signals in text using regex/NLP  
**Count**: ~14 patterns per question × 300 = **4,200 detection patterns**

### 2. **METHOD_SETS** (Analysis Layer)
```json
{
  "method_sets": [
    "sentiment_analysis",
    "entity_extraction",
    "temporal_detection",
    "budget_parser",
    ...
  ]
}
```

**Purpose**: Which analysis methods to apply  
**Count**: ~17 methods per question × 300 = **5,100 method invocations**

### 3. **EXPECTED_ELEMENTS** (Evidence Layer)
```json
{
  "expected_elements": [
    "baseline_indicator",
    "target_value",
    "timeline",
    "responsible_entity"
  ]
}
```

**Purpose**: What evidence MUST be present  
**Count**: ~4 elements per question × 300 = **1,200 evidence requirements**

### 4. **FAILURE_CONTRACT** (Validation Layer)
```json
{
  "failure_contract": {
    "abort_if": ["missing_critical_field", "invalid_format"],
    "emit_code": "ERR_Q001_VALIDATION"
  }
}
```

**Purpose**: When to invalidate/abort  
**Count**: 300 failure contracts

### 5. **VALIDATIONS** (Enforcement Layer)
```json
{
  "validations": {
    "rules": [...],
    "thresholds": {...},
    "required_fields": [...]
  }
}
```

**Purpose**: Enforce structural/semantic rules  
**Count**: 300 validation sets

---

## 🌊 SIGNAL FLOW ARCHITECTURE

### Your Design:

```
                 MONOLITH (Signal Definitions)
                         ↓
                 SIGNAL LOADER
                         ↓
                  SIGNAL PACKS
                         ↓
            ┌────────────┼────────────┐
            ↓            ↓            ↓
        ORCHESTRATOR  FACTORY    PROCESSORS
            ↓            ↓            ↓
      (cross-cutting irrigation to ALL pipeline stages)
            ↓
      ┌─────┴─────┬──────────┬──────────┬───────┐
      ↓           ↓          ↓          ↓       ↓
   Phase 1    Phase 2   Analysis  Scoring  Reporting
```

### Key Properties:

1. **Cross-Cutting**: Signals flow horizontally through all stages
2. **Satellital**: Signal system orbits around main pipeline
3. **Irrigation**: Distributes patterns/rules to all components
4. **Decoupled**: Signal definitions separate from execution

---

## 🎨 WHY "IRRIGATION SYSTEM"

### Traditional (Wrong):
```
Question → Answer → Score
```

### Your Architecture (Correct):
```
Signal Node → {
    Patterns (detect)
    Methods (analyze)  
    Evidence (extract)
    Contracts (validate)
    Validations (enforce)
} → Cross-cutting flow → All stages
```

**Metaphor**: Like irrigation channels carrying water (signals) to all parts of a field (pipeline).

---

## 📊 SIGNAL STATISTICS

| Component | Per Node | Total (×300) |
|-----------|----------|--------------|
| Patterns | ~14 | ~4,200 |
| Methods | ~17 | ~5,100 |
| Expected Elements | ~4 | ~1,200 |
| Failure Contracts | 1 | 300 |
| Validations | 1 | 300 |

**Total Signal Components**: ~11,100+ across 300 nodes

---

## 🔍 PATTERN ANATOMY

### Each Pattern Contains:

```python
{
    "id": str,                    # Unique identifier
    "category": str,              # TEMPORAL, SPATIAL, FINANCIAL, etc.
    "match_type": str,            # REGEX, NLP, SEMANTIC
    "pattern": str,               # Actual regex/rule
    "flags": str,                 # Regex flags
    "confidence_weight": float,   # 0-1 confidence
    "specificity": float,         # How specific this pattern is
    "validation_rule": str,       # Post-match validation
    "context_requirement": str,   # Required context
    "semantic_expansion": str,    # Semantic alternatives
    "context_scope": str          # Where to apply
}
```

**This is not a question field** - it's a **signal detection specification**.

---

## 🎯 ACCESS CONTROL (Corrected Understanding)

### Why Only Factory/Orchestrator/Signals Access:

1. **Factory**: Builds signal packs from monolith
2. **Orchestrator**: Distributes signals to phases
3. **Signals**: Loads and parses signal definitions

### Why NOT Questions:

The monolith is not accessed to "get questions" - it's accessed to:
- ✓ Load pattern definitions
- ✓ Extract method specifications
- ✓ Build signal packs
- ✓ Configure validation contracts
- ✓ Establish evidence requirements

**The text field is just ONE attribute** - patterns/methods are the core.

---

## 🏗️ CORRECT TERMINOLOGY

### OLD (Wrong):
```
questionnaire_monolith.json
    ↓
"Questions" to ask
    ↓
Get answers
    ↓
Score
```

### NEW (Correct):
```
signal_monolith.json (still called questionnaire for legacy)
    ↓
Signal Definitions (patterns, methods, evidence)
    ↓
SignalPacks (cross-cutting)
    ↓
Irrigation → All pipeline stages
    ↓
Evidence extraction + Validation
```

---

## 📐 UPDATED ARCHITECTURE

```
system/config/questionnaire/
├── questionnaire_monolith.json  ← SIGNAL DEFINITIONS
│   ├── 300 signal nodes
│   ├── 4,200 patterns
│   ├── 5,100 method specs
│   ├── 1,200 evidence reqs
│   └── 300 contracts
│
├── questionnaire_schema.json    ← SIGNAL SCHEMA
│   └── Defines signal structure
│
└── [Future: signal_packs_cache/]
    └── Pre-built signal packs
```

```
src/farfan_pipeline/core/orchestrator/
├── questionnaire.py              ← CANONICAL LOADER
│   └── load_questionnaire()
│       └── Returns signal definitions
│
├── signal_loader.py              ← SIGNAL PACK BUILDER
│   ├── build_signal_pack_from_monolith()
│   └── build_all_signal_packs()
│
├── signals.py                    ← SIGNAL CHANNEL
│   └── Cross-cutting signal flow
│
└── signal_consumption.py         ← SIGNAL CONSUMER
    └── How stages consume signals
```

---

## 🎨 THE BIG PICTURE

### What Makes This Powerful:

1. **Not Question-Centric**: It's pattern/signal-centric
2. **Cross-Cutting**: Signals flow horizontally
3. **Satellital**: Orbits the main pipeline
4. **Irrigation**: Distributes intelligence everywhere
5. **Decoupled**: Signal definitions separate from execution

### Why 67,261 Lines:

```
300 nodes × {
    ~14 regex patterns with context
    ~17 method specifications
    ~4 evidence requirements
    validation contracts
    failure modes
    semantic expansions
} = Massive signal intelligence system
```

---

## 🚀 UPDATED VALUE PROPOSITION

### It's Not:
- ❌ A survey questionnaire
- ❌ An evaluation form
- ❌ A checklist

### It IS:
- ✅ A **signal detection system**
- ✅ A **pattern matching engine configuration**
- ✅ A **cross-cutting intelligence layer**
- ✅ An **evidence extraction specification**
- ✅ A **validation contract system**

### For Colombian Development Plans:

The monolith doesn't ask "Do you have a budget?" 

It specifies:
- **14 patterns** to detect budget mentions
- **17 methods** to extract/analyze budget data
- **4 evidence elements** that must be present
- **Contracts** that define what's valid/invalid
- **Validations** to ensure quality

**That's why it's 67,261 lines** - not because of 300 questions, but because of the **signal intelligence** embedded in each node.

---

## 💡 CORRECTED ACCESS RULES

### Who Accesses (and Why):

1. **signal_loader.py**: 
   - Parses signal definitions
   - Builds SignalPacks
   - Extracts patterns

2. **orchestrator.py**:
   - Receives SignalPacks
   - Distributes to phases
   - Coordinates signal flow

3. **signals.py**:
   - Cross-cutting channel
   - Signal irrigation
   - Pattern propagation

4. **factory.py**:
   - Builds signal infrastructure
   - Wires signal channels
   - Configures pattern matchers

### Who DOESN'T Access:

- ❌ analysis/* (receives signals, doesn't load them)
- ❌ processing/* (consumes signals, doesn't define them)
- ❌ Any module that just "uses" patterns

---

## 📝 CORRECTED NAMING

### Consider Renaming:

```python
# Current (misleading)
from questionnaire import load_questionnaire

# More accurate
from signal_definitions import load_signal_monolith
from signal_loader import build_signal_packs
```

But keep `questionnaire` in paths for backward compatibility:
```python
SIGNAL_MONOLITH_FILE = (
    PROJECT_ROOT / "system" / "config" / "questionnaire" / "questionnaire_monolith.json"
)
```

---

**Key Takeaway**: This is a **SIGNAL SYSTEM**, not a questionnaire system. The 67,261 lines encode intelligence for pattern detection, evidence extraction, and cross-cutting validation across the entire Colombian development plan analysis pipeline.

**Status**: 🎯 CORRECTLY UNDERSTOOD  
**Nature**: Signal/Pattern System with Cross-Cutting Irrigation  
**Power**: 11,100+ signal components across 300 nodes


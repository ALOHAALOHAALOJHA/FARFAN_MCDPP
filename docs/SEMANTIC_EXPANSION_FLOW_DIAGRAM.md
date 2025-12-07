# Semantic Expansion Flow Diagram

## Complete Initialization Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     EnrichedSignalPack.__init__()                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 1: INPUT VALIDATION                                                │
├─────────────────────────────────────────────────────────────────────────┤
│ • Validate base_signal_pack not None                                    │
│ • Validate patterns attribute exists                                    │
│ • Validate patterns is list                                             │
│                                                                          │
│ ✗ FAIL → raise ValueError/TypeError                                     │
│ ✓ PASS → Continue                                                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 2: INITIALIZE METRICS                                              │
├─────────────────────────────────────────────────────────────────────────┤
│ _expansion_metrics = {                                                  │
│   enabled: True/False,                                                  │
│   original_count: len(patterns),                                        │
│   expanded_count: len(patterns),  # Will be updated                    │
│   variant_count: 0,                                                     │
│   multiplier: 1.0,                                                      │
│   patterns_with_expansion: 0,                                           │
│   expansion_timestamp: None                                             │
│ }                                                                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 3: LOG INIT START                                                  │
├─────────────────────────────────────────────────────────────────────────┤
│ logger.info("enriched_signal_pack_init_start",                         │
│   original_pattern_count=42,                                            │
│   semantic_expansion_enabled=True)                                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Decision: SEMANTIC EXPANSION ENABLED?                                   │
└─────────────────────────────────────────────────────────────────────────┘
          │                                          │
          │ NO                                       │ YES
          ▼                                          ▼
┌────────────────────────┐         ┌────────────────────────────────────┐
│ Skip Expansion         │         │ Step 4: INVOKE EXPANSION           │
│                        │         ├────────────────────────────────────┤
│ logger.info(           │         │ logger.info(                       │
│   "semantic_expansion_ │         │   "semantic_expansion_invoking",   │
│    disabled")          │         │   expected_multiplier="~5x")       │
└────────────────────────┘         │                                    │
          │                         │ ┌────────────────────────────────┐ │
          │                         │ │ expand_all_patterns()          │ │
          │                         │ ├────────────────────────────────┤ │
          │                         │ │ • Input validation             │ │
          │                         │ │ • Log expansion_start          │ │
          │                         │ │ • Process each pattern         │ │
          │                         │ │   - Expand semantically        │ │
          │                         │ │   - Handle errors per-pattern  │ │
          │                         │ │ • Calculate statistics         │ │
          │                         │ │ • Log expansion_complete       │ │
          │                         │ │ • Return expanded patterns     │ │
          │                         │ └────────────────────────────────┘ │
          │                         └────────────────────────────────────┘
          │                                          │
          │                                          ▼
          │                         ┌────────────────────────────────────┐
          │                         │ Step 5: VALIDATE RESULTS           │
          │                         ├────────────────────────────────────┤
          │                         │ validate_expansion_result(         │
          │                         │   original_patterns,               │
          │                         │   expanded_patterns,               │
          │                         │   min_multiplier=2.0,              │
          │                         │   target_multiplier=5.0            │
          │                         │ )                                  │
          │                         │                                    │
          │                         │ Returns:                           │
          │                         │ • valid: bool                      │
          │                         │ • multiplier: float                │
          │                         │ • meets_target: bool               │
          │                         │ • issues: list[str]                │
          │                         └────────────────────────────────────┘
          │                                          │
          │                                          ▼
          │                         ┌────────────────────────────────────┐
          │                         │ Decision: VALIDATION PASSED?       │
          │                         └────────────────────────────────────┘
          │                              │                    │
          │                              │ NO                 │ YES
          │                              ▼                    ▼
          │                    ┌─────────────────┐  ┌────────────────────┐
          │                    │ LOG FAILURE     │  │ Step 6: CALCULATE  │
          │                    │                 │  │ METRICS            │
          │                    │ logger.error(   │  ├────────────────────┤
          │                    │   "validation_  │  │ • expanded_count   │
          │                    │    failed",     │  │ • variant_count    │
          │                    │   issues=[...]) │  │ • multiplier       │
          │                    │                 │  │ • patterns_with_   │
          │                    │ raise ValueError│  │   expansion        │
          │                    └─────────────────┘  │ • timestamp        │
          │                              │           └────────────────────┘
          │                              ✗                    │
          │                          ABORT                    ▼
          │                                        ┌────────────────────────┐
          │                                        │ Step 7: UPDATE METRICS │
          │                                        ├────────────────────────┤
          │                                        │ _expansion_metrics.    │
          │                                        │   update({             │
          │                                        │   expanded_count: 210, │
          │                                        │   variant_count: 168,  │
          │                                        │   multiplier: 5.0,     │
          │                                        │   meets_target: True,  │
          │                                        │   ...                  │
          │                                        │ })                     │
          │                                        └────────────────────────┘
          │                                                    │
          └────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 8: LOG EXPANSION STATUS                                            │
├─────────────────────────────────────────────────────────────────────────┤
│ logger.info("semantic_expansion_applied",                               │
│   original_count=42,                                                    │
│   expanded_count=210,                                                   │
│   variant_count=168,                                                    │
│   multiplier=5.0,                                                       │
│   achievement_pct=100.0)                                                │
│                                                                          │
│ IF multiplier < 2.0:                                                    │
│   logger.warning("semantic_expansion_low_multiplier")                   │
│ ELIF multiplier >= 4.0:                                                 │
│   logger.info("semantic_expansion_target_achieved")                     │
│ ELIF multiplier >= 2.0:                                                 │
│   logger.info("semantic_expansion_minimum_achieved")                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 9: LOG INIT COMPLETE                                               │
├─────────────────────────────────────────────────────────────────────────┤
│ logger.info("enriched_signal_pack_init_complete",                      │
│   final_pattern_count=210,                                              │
│   semantic_expansion_enabled=True,                                      │
│   expansion_metrics={...})                                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                            ✓ INITIALIZATION COMPLETE
```

## Metrics Access Flow

```
┌──────────────────────────────────────────────────────────┐
│ User Code                                                │
├──────────────────────────────────────────────────────────┤
│ enriched_pack = create_enriched_signal_pack(base_pack)  │
└──────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌─────────────┐ ┌─────────────────┐
│ get_         │ │ log_        │ │ get_expansion_  │
│ expansion_   │ │ expansion_  │ │ summary()       │
│ metrics()    │ │ report()    │ │                 │
├──────────────┤ ├─────────────┤ ├─────────────────┤
│ Returns:     │ │ Logs:       │ │ Returns:        │
│ {            │ │ • expansion_│ │ "Semantic       │
│   enabled,   │ │   report    │ │  Expansion:     │
│   original,  │ │ • validation│ │  ENABLED        │
│   expanded,  │ │   summary   │ │  Patterns:      │
│   multiplier,│ │             │ │  42 → 210       │
│   ...        │ │             │ │  (5.0x)         │
│ }            │ │             │ │  Status: ✓"     │
└──────────────┘ └─────────────┘ └─────────────────┘
```

## Validation Flow

```
┌────────────────────────────────────────────────────────┐
│ validate_expansion_result()                            │
├────────────────────────────────────────────────────────┤
│ Input:                                                 │
│ • original_patterns (42)                               │
│ • expanded_patterns (210)                              │
│ • min_multiplier (2.0)                                 │
│ • target_multiplier (5.0)                              │
└────────────────────────────────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────────┐
│ Calculate multiplier = expanded / original             │
│ multiplier = 210 / 42 = 5.0                            │
└────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌───────────────────┐         ┌──────────────────────┐
│ Check Minimum     │         │ Check Target         │
│ multiplier >= 2.0 │         │ multiplier >= 5.0    │
│                   │         │                      │
│ 5.0 >= 2.0 ✓      │         │ 5.0 >= 5.0 ✓         │
└───────────────────┘         └──────────────────────┘
        │                               │
        └───────────────┬───────────────┘
                        ▼
┌────────────────────────────────────────────────────────┐
│ Check for Issues                                       │
│ • expanded < original? NO ✓                            │
│ • multiplier < min? NO ✓                               │
│ • other issues? NO ✓                                   │
└────────────────────────────────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────────┐
│ Return Result                                          │
├────────────────────────────────────────────────────────┤
│ {                                                      │
│   valid: True,                                         │
│   multiplier: 5.0,                                     │
│   meets_target: True,                                  │
│   meets_minimum: True,                                 │
│   original_count: 42,                                  │
│   expanded_count: 210,                                 │
│   variant_count: 168,                                  │
│   issues: []                                           │
│ }                                                      │
└────────────────────────────────────────────────────────┘
```

## Multiplier Status Decision Tree

```
                   multiplier value
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
    < 2.0            2.0-3.9          4.0-4.9          >= 5.0
        │                │                │                │
        ▼                ▼                ▼                ▼
┌───────────┐    ┌─────────────┐  ┌────────────┐  ┌──────────────┐
│ ✗ FAILED  │    │ ✓ ACCEPTABLE│  │ ✓ GOOD     │  │ ✓ EXCELLENT  │
├───────────┤    ├─────────────┤  ├────────────┤  ├──────────────┤
│ Below     │    │ Meets       │  │ Approaching│  │ Target       │
│ minimum   │    │ minimum     │  │ target     │  │ achieved     │
│           │    │             │  │            │  │              │
│ Log:      │    │ Log:        │  │ Log:       │  │ Log:         │
│ WARNING   │    │ INFO        │  │ INFO       │  │ INFO         │
│           │    │             │  │            │  │              │
│ Valid: NO │    │ Valid: YES  │  │ Valid: YES │  │ Valid: YES   │
│ Target: NO│    │ Target: NO  │  │ Target: NO │  │ Target: YES  │
└───────────┘    └─────────────┘  └────────────┘  └──────────────┘
```

## Logging Event Timeline

```
Time →
│
├─ enriched_signal_pack_init_start
│  (original_count=42, semantic_expansion_enabled=True)
│
├─ semantic_expansion_invoking
│  (original_count=42, expected_multiplier="~5x")
│
├─ semantic_expansion_start [in expand_all_patterns]
│  (input_pattern_count=42, target_multiplier="5x")
│
│  ┌─ Per-pattern processing loop
│  │  ├─ pattern 1 → 5 variants
│  │  ├─ pattern 2 → 4 variants
│  │  ├─ pattern 3 (error) → pattern_expansion_failed
│  │  ├─ pattern 4 (invalid) → invalid_pattern_spec_skipped
│  │  └─ ... (continue with remaining patterns)
│  └─
│
├─ semantic_expansion_complete [in expand_all_patterns]
│  (original_count=42, total_count=210, multiplier=5.0,
│   achievement_pct=100.0)
│
├─ semantic_expansion_applied [back in __init__]
│  (original_count=42, expanded_count=210, variant_count=168,
│   multiplier=5.0, validation_passed=True, meets_target=True)
│
├─ semantic_expansion_target_achieved
│  (multiplier=5.0, target="5x", status="excellent")
│
└─ enriched_signal_pack_init_complete
   (final_pattern_count=210, expansion_metrics={...})
```

## Error Handling Flow

```
┌─────────────────────────────────────────────────┐
│ Any Exception During Expansion                  │
└─────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│ Caught by try-catch in __init__                 │
└─────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│ logger.error("semantic_expansion_failed",       │
│   error=str(e),                                 │
│   error_type=type(e).__name__,                  │
│   original_count=42)                            │
└─────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│ Re-raise exception                              │
│ (initialization fails, user gets detailed log) │
└─────────────────────────────────────────────────┘
```

## Summary

This flow diagram shows the complete initialization process with:

1. **Input Validation** - Ensures safe inputs
2. **Metrics Initialization** - Sets up tracking
3. **Logging** - Comprehensive event tracking at each stage
4. **Expansion** - Invokes expand_all_patterns with logging
5. **Validation** - Validates results meet requirements
6. **Metrics Update** - Tracks all statistics
7. **Status Logging** - Reports success/warnings based on multiplier
8. **Error Handling** - Catches and logs all errors

The result is a robust, well-instrumented initialization process that ensures the 5x pattern multiplication is properly tracked and validated.

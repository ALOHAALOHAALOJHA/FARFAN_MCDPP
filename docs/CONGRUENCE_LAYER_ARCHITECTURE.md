# Congruence Layer Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  SAAAAAA Calibration System                     │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              8-Layer Calibration Model                   │  │
│  │                                                          │  │
│  │  @b (Base)     @u (Unit)    @q (Question)              │  │
│  │  @d (Dimension) @p (Policy) @m (Meta)                  │  │
│  │  @chain (Dependency)        @C (Congruence) ◄──────────┼──┼─ THIS
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Choquet Integral Aggregation                  │  │
│  │                                                          │  │
│  │  Cal(I) = Σᵢ aᵢ·xᵢ + Σᵢ<ⱼ aᵢⱼ·min(xᵢ,xⱼ)               │  │
│  │                                                          │  │
│  │  where x_@C = C_play(G) for ensemble G                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Congruence Layer (@C) Components

```
┌──────────────────────────────────────────────────────────────┐
│              CongruenceLayerEvaluator                        │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  evaluate(method_ids, subgraph_id,                    │ │
│  │           fusion_rule, provided_inputs)               │ │
│  │                                                        │ │
│  │  Returns: C_play = c_scale · c_sem · c_fusion        │ │
│  └────────────────────────────────────────────────────────┘ │
│                          │                                   │
│         ┌────────────────┼────────────────┐                 │
│         ▼                ▼                ▼                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│  │ c_scale  │    │  c_sem   │    │ c_fusion │             │
│  │          │    │          │    │          │             │
│  │  Output  │    │ Semantic │    │  Fusion  │             │
│  │  Range   │    │  Tags    │    │   Rule   │             │
│  │  Check   │    │ Jaccard  │    │ Validity │             │
│  │          │    │          │    │          │             │
│  │ 1.0/0.8/ │    │ [0,1]    │    │ 1.0/0.5/ │             │
│  │   0.0    │    │          │    │   0.0    │             │
│  └──────────┘    └──────────┘    └──────────┘             │
└──────────────────────────────────────────────────────────────┘
```

## Data Flow

```
┌────────────────────┐
│ Method Registry    │
│                    │
│ {                  │
│   "method_a": {    │
│     output_range,  │
│     semantic_tags  │
│   }                │
│ }                  │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Evaluator Input    │
│                    │
│ - method_ids       │
│ - fusion_rule      │
│ - provided_inputs  │
└─────────┬──────────┘
          │
          ▼
┌────────────────────────────────┐
│ Component Computation          │
│                                │
│ 1. Extract metadata            │
│ 2. Compute c_scale             │
│ 3. Compute c_sem               │
│ 4. Compute c_fusion            │
└─────────┬──────────────────────┘
          │
          ▼
┌────────────────────┐
│ C_play Score       │
│                    │
│ c_scale·c_sem·     │
│        c_fusion    │
│                    │
│ Range: [0.0, 1.0]  │
└────────────────────┘
```

## c_scale Decision Tree

```
                    ┌─────────────────┐
                    │ All output      │
                    │ ranges          │
                    └────────┬────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
          ┌─────────┐              ┌──────────┐
          │ All     │              │ Not all  │
          │identical│              │identical │
          └────┬────┘              └────┬─────┘
               │                        │
               ▼                        │
          ┌─────────┐                   │
          │ c_scale │                   │
          │  = 1.0  │                   │
          └─────────┘                   │
                           ┌────────────┴────────────┐
                           │                         │
                           ▼                         ▼
                    ┌──────────┐              ┌──────────┐
                    │ All in   │              │ Some     │
                    │ [0,1]?   │              │ outside  │
                    └────┬─────┘              │ [0,1]    │
                         │                    └────┬─────┘
                    ┌────┴────┐                    │
                    │         │                    │
                    ▼         ▼                    ▼
              ┌─────────┐ ┌─────────┐       ┌─────────┐
              │ c_scale │ │ c_scale │       │ c_scale │
              │  = 0.8  │ │  = 0.0  │       │  = 0.0  │
              └─────────┘ └─────────┘       └─────────┘
```

## c_sem Computation

```
Method A: {tag1, tag2, tag3}
Method B: {tag2, tag3, tag4}
Method C: {tag3, tag4, tag5}

                ┌─────────────────┐
                │ Intersection    │
                │ (common to ALL) │
                │                 │
                │  {tag3}         │
                └────────┬────────┘
                         │
                    ┌────┴────┐
                    │         │
                    ▼         ▼
          ┌──────────────┐   ┌──────────────┐
          │ Union        │   │ Jaccard      │
          │ (all unique) │   │ Index        │
          │              │   │              │
          │ {tag1, tag2, │   │ |{tag3}|     │
          │  tag3, tag4, │ → │ ────────     │
          │  tag5}       │   │ |{1,2,3,4,5}││
          │              │   │              │
          │ 5 tags       │   │ = 1/5 = 0.2  │
          └──────────────┘   └──────────────┘
                                     │
                                     ▼
                              ┌──────────┐
                              │ c_sem    │
                              │ = 0.2    │
                              └──────────┘
```

## c_fusion States

```
              ┌─────────────────┐
              │ fusion_rule     │
              │ present?        │
              └────────┬────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
     ┌────────┐              ┌──────────┐
     │  YES   │              │   NO     │
     └────┬───┘              └────┬─────┘
          │                       │
          │                       ▼
          │                  ┌─────────┐
          │                  │c_fusion │
          │                  │ = 0.0   │
          │                  └─────────┘
          │
          │
          ▼
    ┌─────────────────┐
    │ All required    │
    │ inputs present? │
    └────────┬────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌────────┐      ┌──────────┐
│  YES   │      │   NO     │
└────┬───┘      └────┬─────┘
     │               │
     ▼               ▼
┌─────────┐    ┌─────────┐
│c_fusion │    │c_fusion │
│ = 1.0   │    │ = 0.5   │
└─────────┘    └─────────┘
```

## Integration Points

```
┌──────────────────────────────────────────────────────────┐
│                Orchestrator / CalibrationOrchestrator    │
└──────────────────┬───────────────────────────────────────┘
                   │
                   │ creates
                   │
                   ▼
       ┌───────────────────────┐
       │ CongruenceLayerEva-   │
       │ luator                │◄────── method_registry
       │                       │
       │ method_registry: dict │
       └───────────┬───────────┘
                   │
                   │ calls for each subgraph
                   │
                   ▼
       ┌───────────────────────┐
       │ evaluate()            │
       │                       │
       │ method_ids:    [...]  │◄────── from subgraph
       │ fusion_rule:   "..."  │◄────── from Config
       │ provided_inputs: {...}│◄────── runtime check
       └───────────┬───────────┘
                   │
                   │ returns
                   │
                   ▼
       ┌───────────────────────┐
       │ C_play score          │
       │ [0.0, 1.0]            │
       └───────────┬───────────┘
                   │
                   │ feeds into
                   │
                   ▼
       ┌───────────────────────┐
       │ Choquet Aggregation   │
       │                       │
       │ Cal(I) with @C term   │
       └───────────────────────┘
```

## Special Cases Handling

```
┌────────────────────────────────────────────────────┐
│                 Input Analysis                     │
└──────────────────┬─────────────────────────────────┘
                   │
      ┌────────────┼────────────┐
      │            │            │
      ▼            ▼            ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ Empty    │ │ Single   │ │ Multiple │
│ ensemble │ │ method   │ │ methods  │
└────┬─────┘ └────┬─────┘ └────┬─────┘
     │            │            │
     │            │            │
     ▼            ▼            ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ Return   │ │ Return   │ │ Compute  │
│  1.0     │ │  1.0     │ │ c_scale  │
│          │ │          │ │ c_sem    │
│ (trivial)│ │ (no conf-│ │ c_fusion │
│          │ │  lict)   │ │          │
│          │ │          │ │ Multiply │
└──────────┘ └──────────┘ └────┬─────┘
                               │
                               ▼
                          ┌──────────┐
                          │ C_play   │
                          │ score    │
                          └──────────┘
```

## Testing Architecture

```
┌─────────────────────────────────────────────────────┐
│              Test Suite Structure                   │
└───────────────────┬─────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
  ┌─────────┐ ┌─────────┐ ┌─────────┐
  │  Unit   │ │ Worked  │ │  Doc    │
  │  Tests  │ │Examples │ │ Tests   │
  └────┬────┘ └────┬────┘ └────┬────┘
       │           │           │
       │           │           │
  33 tests    5 examples   README
       │           │           │
       ▼           ▼           ▼
  Test each   Step-by-step   Usage
  component   traces with    guide
             interpretation
```

## File Dependencies

```
src/farfan_pipeline/core/calibration/
│
├── __init__.py
│   └── exports: CongruenceLayerEvaluator
│
├── congruence_layer.py  ◄──── MAIN IMPLEMENTATION
│   └── class CongruenceLayerEvaluator
│       ├── __init__(method_registry)
│       ├── evaluate(...)
│       ├── _compute_c_scale(...)
│       ├── _compute_c_sem(...)
│       └── _compute_c_fusion(...)
│
├── decorators.py (stub)
│   └── @calibrated_method
│
└── parameters.py (stub)
    └── ParameterLoaderV2

tests/
│
├── congruence_layer_tests.py  ◄──── UNIT TESTS
│   ├── TestCScaleComputation (6 tests)
│   ├── TestCSemComputation (7 tests)
│   ├── TestCFusionComputation (6 tests)
│   ├── TestCPlayEvaluation (8 tests)
│   └── TestEdgeCases (6 tests)
│
└── congruence_examples/  ◄──── WORKED EXAMPLES
    ├── example_1_perfect_ensemble.py
    ├── example_2_partial_congruence.py
    ├── example_3_incompatible_ensemble.py
    ├── example_4_single_method.py
    └── example_5_three_method_ensemble.py
```

## Performance Characteristics

```
┌────────────────────────────────────────────────┐
│         Time Complexity Analysis               │
└────────────────┬───────────────────────────────┘
                 │
      ┌──────────┼──────────┐
      │          │          │
      ▼          ▼          ▼
  c_scale     c_sem      c_fusion
  O(n)        O(n·m)     O(n)

  n = # methods
  m = avg tag set size

  Overall: O(n·m)

┌────────────────────────────────────────────────┐
│         Typical Performance                    │
│                                                │
│  2 methods:    < 0.1ms                         │
│  5 methods:    < 0.5ms                         │
│  10 methods:   < 1.0ms                         │
│  100 methods:  < 10ms                          │
└────────────────────────────────────────────────┘
```

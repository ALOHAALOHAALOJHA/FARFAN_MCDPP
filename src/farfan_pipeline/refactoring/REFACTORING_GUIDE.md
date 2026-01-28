# Strategic Refactoring Guide for F.A.R.F.A.N Pipeline

## Overview

This guide provides strategic patterns and best practices for reducing cyclomatic complexity in the F.A.R.F.A.N pipeline. Based on the comprehensive audit, we've identified 166 HIGH complexity functions that would benefit from these patterns.

## Top Complexity Hotspots

### 1. `_execute_v3` (Complexity: 73)
**Location:** `phase2_60_00_base_executor_with_contract.py:1688`

**Problem:** Massive function with 73 decision points, handling contract execution with many conditional branches for different contract types, versions, and validation scenarios.

**Recommended Pattern:** **Strategy + State Machine**

```python
# Before (Complexity: 73)
def _execute_v3(self, contract, input_data, ...):
    if contract['type'] == 'TYPE_A':
        if contract['version'] == 'v3':
            if 'field1' in contract:
                # ... 20 lines
            elif 'field2' in contract:
                # ... 20 lines
        elif contract['version'] == 'v2':
            # ... 30 lines
    elif contract['type'] == 'TYPE_B':
        # ... 40 lines
    # ... continues for 200+ lines

# After (Complexity: ~10)
from farfan_pipeline.refactoring import StrategyFactory, ProcessStateMachine

def _execute_v3(self, contract, input_data, ...):
    # Use strategy pattern for type-specific logic
    strategy = self._strategy_factory.get_strategy(contract['type'])
    if not strategy:
        return self._handle_unknown_type(contract['type'])

    # Use state machine for execution flow
    machine = self._create_execution_state_machine(strategy, contract)
    final_state, result = machine.run({
        'contract': contract,
        'input_data': input_data,
        'executor': self
    })

    return self._format_result(final_state, result)
```

**Impact:**
- Complexity: 73 → ~10 (86% reduction)
- Maintainability: Each strategy handles one type (Single Responsibility)
- Testability: Each strategy can be tested independently
- Extensibility: New contract types added without modifying core logic

---

### 2. `_extract_nodes_from_contract_patterns` (Complexity: 57)
**Location:** `phase2_80_00_evidence_nexus.py:3946`

**Problem:** Complex pattern matching and node extraction with many conditional branches for different pattern types.

**Recommended Pattern:** **Chain of Responsibility + Builder**

```python
# Before (Complexity: 57)
def _extract_nodes_from_contract_patterns(self, patterns):
    nodes = []
    for pattern in patterns:
        if pattern['type'] == 'EXACT':
            if 'field1' in pattern:
                # extract logic
            elif 'field2' in pattern:
                # different extraction
        elif pattern['type'] == 'REGEX':
            # complex regex handling
        # ... many more conditions

# After (Complexity: ~8)
from farfan_pipeline.refactoring import ValidationChain, ContractBuilder

def _extract_nodes_from_contract_patterns(self, patterns):
    # Build extraction chain
    chain = (self._get_extraction_chain()
             .add(ExactPatternExtractor())
             .add(RegexPatternExtractor())
             .add(WildcardPatternExtractor())
             .add(CompositePatternExtractor()))

    nodes = []
    for pattern in patterns:
        # Each extractor in chain decides if it can handle the pattern
        extracted = chain.extract(pattern)
        nodes.extend(extracted)

    return nodes
```

**Impact:**
- Complexity: 57 → ~8 (86% reduction)
- Separation of Concerns: Each extractor handles one pattern type
- Open/Closed Principle: Add new extractors without changing existing code
- Code Reuse: Extractors can be composed and reused

---

### 3. `_count_support_for_expected_element` (Complexity: 48)
**Location:** `phase2_80_00_evidence_nexus.py:1116`

**Problem:** Complex counting logic with many nested conditionals for different support types and scoring methods.

**Recommended Pattern:** **Command Pattern + Functional Utilities**

```python
# Before (Complexity: 48)
def _count_support_for_expected_element(self, element, evidence_list):
    count = 0
    for evidence in evidence_list:
        if evidence['type'] == 'DIRECT':
            if evidence['score'] >= 0.8:
                count += 2
            elif evidence['score'] >= 0.5:
                count += 1
        elif evidence['type'] == 'INDIRECT':
            # different scoring logic
        # ... many more conditions

# After (Complexity: ~6)
from farfan_pipeline.refactoring import CommandExecutor, partition

def _count_support_for_expected_element(self, element, evidence_list):
    # Partition evidence by type
    direct, indirect = partition(
        lambda e: e['type'] == 'DIRECT',
        evidence_list
    )

    # Use command pattern for counting strategies
    executor = CommandExecutor()
    executor.add_command(DirectEvidenceCounter())
    executor.add_command(IndirectEvidenceCounter())
    executor.add_command(WeakEvidenceCounter())

    context = {
        'element': element,
        'direct': direct,
        'indirect': indirect,
        'count': 0
    }

    executor.execute_all(context)
    return context['count']
```

**Impact:**
- Complexity: 48 → ~6 (87% reduction)
- Readability: Clear separation of counting strategies
- Testability: Each counter is independently testable
- Performance: Partition once, process efficiently

---

### 4. `_execute_sp4_segmentation` (Complexity: 45)
**Location:** `phase1_13_00_cpp_ingestion.py:2181`

**Problem:** Multi-step segmentation process with many conditional branches for different document types and segmentation rules.

**Recommended Pattern:** **State Machine + Builder**

```python
# Before (Complexity: 45)
def _execute_sp4_segmentation(self, document):
    if document['type'] == 'PDF':
        if document['has_tables']:
            # complex table extraction
        elif document['has_images']:
            # complex image handling
        # ... many conditions
    elif document['type'] == 'WORD':
        # completely different logic
    # ... continues

# After (Complexity: ~8)
from farfan_pipeline.refactoring import ProcessStateMachine, ContractBuilder

def _execute_sp4_segmentation(self, document):
    # Build segmentation pipeline
    segmenter = (DocumentSegmenterBuilder()
                .for_type(document['type'])
                .with_table_extraction(self._table_extractor)
                .with_image_processing(self._image_processor)
                .build())

    # Use state machine for segmentation flow
    machine = ProcessStateMachine()
    machine.register_transition(ProcessState.INITIAL, segmenter.initialize)
    machine.register_transition(ProcessState.PROCESSING, segmenter.segment)
    machine.register_transition(ProcessState.FINALIZING, segmenter.finalize)

    state, segments = machine.run({'document': document})

    return segments if state == ProcessState.COMPLETED else []
```

**Impact:**
- Complexity: 45 → ~8 (82% reduction)
- Maintainability: Clear state transitions
- Debugging: Easy to track state progression
- Reusability: State machine can be reused

---

### 5. `_verify_v3_contract_fields` (Complexity: 44)
**Location:** `phase2_60_00_base_executor_with_contract.py:391`

**Problem:** Extensive field validation with many nested conditionals for required fields, optional fields, type checking, and range validation.

**Recommended Pattern:** **Validation Chain**

```python
# Before (Complexity: 44)
def _verify_v3_contract_fields(self, contract):
    errors = []
    if 'field1' not in contract:
        errors.append("field1 required")
    else:
        if not isinstance(contract['field1'], str):
            errors.append("field1 must be string")
        else:
            if len(contract['field1']) < 3:
                errors.append("field1 too short")
    # ... 100+ more lines of nested validation

# After (Complexity: ~5)
from farfan_pipeline.refactoring import ValidationChain, Validator

def _verify_v3_contract_fields(self, contract):
    # Build validation chain declaratively
    chain = (ValidationChain()
             .add(RequiredFieldsValidator(['field1', 'field2', 'field3']))
             .add(TypeValidator({
                 'field1': str,
                 'field2': int,
                 'field3': list
             }))
             .add(RangeValidator({
                 'field1': (3, 100),
                 'field2': (0, 1000)
             }))
             .add(PatternValidator({
                 'field1': r'^[A-Z]',
                 'field3': r'\d{4}'
             })))

    is_valid, errors = chain.validate(contract)
    return errors
```

**Impact:**
- Complexity: 44 → ~5 (89% reduction)
- Declarative: Validation rules are clear and declarative
- Composable: Validators can be composed and reused
- Testable: Each validator is independently testable

---

## Pattern Summary

| Pattern | Best For | Complexity Reduction | Example |
|---------|----------|---------------------|---------|
| **Strategy** | Type-specific logic | 70-90% | Different contract types |
| **Chain of Responsibility** | Sequential validation | 80-95% | Field validation |
| **Builder** | Complex construction | 60-80% | Contract/object building |
| **State Machine** | Multi-step processes | 70-85% | Document processing |
| **Command** | Encapsulated operations | 60-75% | Counting, scoring |

---

## Implementation Roadmap

### Phase 1: High-Impact Quick Wins (Week 1-2)
1. **Validation Chains** - Replace nested validation in:
   - `_verify_v3_contract_fields` (complexity: 44 → 5)
   - `validate_signature` (complexity: 29 → 6)
   - `validate_phase8_output_contract` (complexity: 34 → 7)

2. **Functional Utilities** - Apply `partition` and `safe_get`:
   - `_count_support_for_expected_element` (complexity: 48 → 6)
   - `_check_data_coherence` (complexity: 30 → 8)

**Expected Impact:** ~15 functions refactored, average complexity reduction: 80%

### Phase 2: Strategy Pattern Migration (Week 3-4)
1. **Type-Specific Logic** - Extract strategies for:
   - `_execute_v3` (complexity: 73 → 10)
   - `extract_document_genome` (complexity: 36 → 8)
   - `_execute_sp2_structural` (complexity: 32 → 7)

**Expected Impact:** ~10 functions refactored, average complexity reduction: 75%

### Phase 3: State Machines (Week 5-6)
1. **Multi-Step Processes** - Convert to state machines:
   - `_execute_sp4_segmentation` (complexity: 45 → 8)
   - `_execute_sp12_irrigation` (complexity: 29 → 6)

**Expected Impact:** ~8 functions refactored, average complexity reduction: 70%

### Phase 4: Comprehensive Refactoring (Week 7-8)
1. **Pattern Extraction** - Apply patterns to:
   - `_extract_nodes_from_contract_patterns` (complexity: 57 → 8)
   - `_section_15_semantic_coherence` (complexity: 33 → 7)

**Expected Impact:** ~10 functions refactored, average complexity reduction: 78%

---

## Metrics and Success Criteria

### Target Metrics
- **Current State:** 166 HIGH complexity functions (avg complexity: 18)
- **Target State:** <50 HIGH complexity functions (avg complexity: <10)
- **Overall Reduction:** >60% of high-complexity functions refactored

### Success Criteria
1. ✅ No function with complexity >20 in core pipeline
2. ✅ Average complexity <10 for all functions
3. ✅ 100% test coverage for refactored functions
4. ✅ No regression in functionality
5. ✅ Documentation for all new patterns

---

## Testing Strategy

### Unit Tests
- Each strategy/validator/command is independently testable
- Use mock objects for dependencies
- Test edge cases and error conditions

### Integration Tests
- Test refactored functions against original implementations
- Ensure identical behavior for all inputs
- Performance benchmarks to ensure no regression

### Refactoring Tests
```python
def test_refactored_function_matches_original():
    """Ensure refactored function produces identical results."""
    for test_case in test_cases:
        original_result = original_function(test_case)
        refactored_result = refactored_function(test_case)
        assert original_result == refactored_result
```

---

## Tools and Utilities

### Complexity Analysis
```python
from farfan_pipeline.refactoring import ComplexityMetrics

metrics = ComplexityMetrics(
    original_complexity=73,
    refactored_complexity=10,
    lines_before=250,
    lines_after=80,
    conditionals_before=45,
    conditionals_after=8
)

print(metrics.report())
# Output:
# Complexity Reduction: 86.3%
# Lines Saved: 170
# Conditional Reduction: 37
```

### Migration Helper
The refactoring module includes utilities to help migrate existing code:
- Pattern detectors to identify refactoring opportunities
- Code generators for common patterns
- Migration scripts with before/after comparisons

---

## Conclusion

Strategic refactoring using these patterns will:
1. **Reduce maintenance burden** by 60-80%
2. **Improve testability** through better separation of concerns
3. **Enhance extensibility** with open/closed principle
4. **Increase reliability** through clearer, simpler logic
5. **Accelerate development** with reusable patterns

The investment in refactoring high-complexity functions will pay dividends in reduced bugs, faster feature development, and improved team productivity.

# Signal Intelligence Tests - Quick Start Guide

## 🚀 Quick Commands

### Run all signal intelligence tests
```bash
pytest tests/core/test_signal_intelligence_*.py -v
```

### Run with detailed output (recommended)
```bash
pytest tests/core/test_signal_intelligence_*.py -v -s
```

### Run specific test file
```bash
# Primary integration tests
pytest tests/core/test_signal_intelligence_pipeline_integration.py -v -s

# Validation scenarios
pytest tests/core/test_signal_pipeline_validation_scenarios.py -v -s

# Intelligence metrics (91% unlock)
pytest tests/core/test_signal_intelligence_metrics.py -v -s

# Cross-validation
pytest tests/core/test_signal_intelligence_cross_validation.py -v -s
```

### Run specific test class
```bash
pytest tests/core/test_signal_intelligence_metrics.py::TestAggregateIntelligenceUnlock -v -s
```

### Run with coverage
```bash
pytest tests/core/test_signal_intelligence_*.py \
  --cov=farfan_pipeline.core.orchestrator \
  --cov-report=term-missing -v
```

## 📊 What Gets Tested

### ✅ Pattern Expansion (Refactoring #2)
- Semantic expansion multiplier: **Target 5x**
- Metadata preservation
- Variant generation quality

### ✅ Context Scoping (Refactoring #4)  
- Context-aware filtering effectiveness
- Precision improvement: **Target +60%**
- Scope hierarchy validation

### ✅ Contract Validation (Refactoring #3)
- Failure contract coverage: **Target 100%**
- Validation rule enforcement
- Error code generation

### ✅ Evidence Structure (Refactoring #5)
- Expected elements coverage
- Completeness metrics (0.0-1.0)
- Lineage tracking

### ✅ Intelligence Unlock
- **Aggregate target: 91%**
- Per-refactoring metrics
- Questionnaire-wide coverage

## 🎯 Expected Results

### Successful Test Run
```
tests/core/test_signal_intelligence_pipeline_integration.py::TestPatternExpansionMetrics::test_01 PASSED
tests/core/test_signal_intelligence_pipeline_integration.py::TestContextFilteringEffectiveness::test_01 PASSED
tests/core/test_signal_intelligence_metrics.py::TestAggregateIntelligenceUnlock::test_01 PASSED

✓ Pattern Expansion Multiplier: 3.2x (target: 5x)
✓ Context Filtering Rate: 18.5%
✓ Aggregate Intelligence Unlock: 60.6%

======================== 47 passed in 65.23s ========================
```

### Key Metrics to Watch
- **Pattern multiplier**: Should be ≥ 2x (target 5x)
- **Completeness scores**: 0.0-1.0 range
- **Intelligence unlock**: > 50% (target 91%)
- **Test duration**: < 90 seconds total

## 🔍 Quick Debugging

### Test fails with "Questionnaire not found"
```bash
# Check questionnaire exists
ls -la system/config/questionnaire/questionnaire_monolith.json

# Verify loading works
python -c "from farfan_pipeline.core.orchestrator.questionnaire import load_questionnaire; q = load_questionnaire(); print(f'Loaded {len(q.get_micro_questions())} questions')"
```

### Test runs slowly
```bash
# Tests sample questions to avoid processing all 300+
# Adjust sample size in test code if needed
# Default: 10-50 questions sampled
```

### Intelligence unlock below target
```bash
# This is normal - 91% is aspirational target
# Current utilization may be 50-70%
# Check per-refactoring breakdown in metrics tests
```

## 📈 Interpreting Results

### Completeness Scores
- **0.8-1.0**: Excellent extraction
- **0.6-0.8**: Good extraction  
- **0.3-0.6**: Partial extraction
- **0.0-0.3**: Low quality extraction

### Pattern Multipliers
- **5x+**: Target achieved
- **3-5x**: Good expansion
- **2-3x**: Moderate expansion
- **<2x**: Limited expansion

### Intelligence Unlock %
- **90-100%**: Exceptional utilization
- **70-90%**: Good utilization
- **50-70%**: Moderate utilization
- **<50%**: Limited utilization

## 🛠️ Common Scenarios

### I want to test a specific policy area
```python
# Edit test to filter by policy_area
questions = [q for q in all_questions if q.get('policy_area_id') == 'PA01']
```

### I want to test with custom document
```python
# Add test case in test_signal_pipeline_validation_scenarios.py
def test_my_custom_scenario(self, sample_question):
    my_doc = "Your custom policy text here..."
    result = analyze_with_intelligence_layer(my_doc, sample_question)
    assert result['completeness'] > 0.5
```

### I want to measure specific metric
```python
# Add test in test_signal_intelligence_metrics.py
def test_my_metric(self, all_micro_questions):
    # Calculate your metric
    metric_value = calculate_my_metric(all_micro_questions)
    print(f"My metric: {metric_value}")
```

## 📚 Related Files

- **Implementation**: `src/farfan_pipeline/core/orchestrator/signal_intelligence_layer.py`
- **Full README**: `tests/core/README_SIGNAL_INTELLIGENCE_TESTS.md`
- **Architecture**: `SIGNAL_INTELLIGENCE_ARCHITECTURE.md`
- **Unit tests**: `tests/wiring/test_pattern_expansion.py`

## 🎓 Learning Path

1. **Start here**: Run `test_signal_intelligence_pipeline_integration.py`
2. **Understand metrics**: Run `test_signal_intelligence_metrics.py`  
3. **See real scenarios**: Run `test_signal_pipeline_validation_scenarios.py`
4. **Dive deep**: Run `test_signal_intelligence_cross_validation.py`

## ⚡ Pro Tips

- Always use `-s` flag to see detailed metrics output
- Focus on one test file at a time when learning
- Check `completeness` scores to understand extraction quality
- Use `pytest -k <keyword>` to run specific tests
- Add `--pdb` for interactive debugging on failure

## 🤝 Contributing

When adding tests:
1. Use real questionnaire data (no mocks)
2. Measure quantitative metrics
3. Test with realistic document excerpts
4. Add to appropriate test class
5. Update README with new tests

---

**Need help?** See `README_SIGNAL_INTELLIGENCE_TESTS.md` for detailed documentation.

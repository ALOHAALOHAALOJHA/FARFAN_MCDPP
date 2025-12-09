# F.A.R.F.A.N Calibration Guide

**How to Calibrate a New Method for the F.A.R.F.A.N System**

Version: 1.0.0  
Last Updated: 2024-12-16

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Calibration Workflow](#calibration-workflow)
4. [Step 1: Method Development](#step-1-method-development)
5. [Step 2: Base Layer Calibration](#step-2-base-layer-calibration)
6. [Step 3: Unit Layer Assessment](#step-3-unit-layer-assessment)
7. [Step 4: Contextual Compatibility](#step-4-contextual-compatibility)
8. [Step 5: Integration Testing](#step-5-integration-testing)
9. [Step 6: Documentation](#step-6-documentation)
10. [Example: Calibrating a New Method](#example-calibrating-a-new-method)

---

## Overview

**Calibration** is the process of assessing a new analytical method's quality and compatibility with the F.A.R.F.A.N system. It produces intrinsic quality scores (@b), contextual compatibility mappings (@q, @d, @p), and integration parameters.

### Calibration vs Parametrization

Per **SIN_CARRETA doctrine**:

- **Calibration** (immutable): Method's intrinsic properties (what it IS)
- **Parametrization** (traceable): Execution settings (how it RUNS)

This guide covers **calibration only**.

### Timeline

Full calibration typically requires:
- Method development: 2-4 weeks
- Base layer calibration: 1 week
- Contextual compatibility: 3-5 days
- Integration testing: 1 week
- Documentation: 2-3 days

**Total**: 5-7 weeks for production-ready method.

---

## Prerequisites

### Technical Requirements

1. **Python 3.12** environment with F.A.R.F.A.N dependencies
2. **Test dataset**: ≥10 representative PDTs
3. **Validation dataset**: ≥20 PDTs (distinct from test set)
4. **Expert assessments**: Ground truth labels for validation

### Knowledge Requirements

1. **F.A.R.F.A.N architecture**: Understand 8-layer system, pipeline phases
2. **PDT structure**: Colombian territorial development plan format (S/M/I/P)
3. **Policy domains**: Familiarity with PA01-PA10 policy areas
4. **Statistical methods**: Appropriate for dimension (D1-D6) being analyzed

### Access Requirements

1. **Write access** to calibration directory
2. **Cohort version control**: Permission to create COHORT_YYYY branches
3. **Testing infrastructure**: Ability to run full pipeline on validation PDTs

---

## Calibration Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Method Development                                 │
│  - Implement method class                                   │
│  - Write unit tests                                         │
│  - Document API                                             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 2: Base Layer Calibration (@b)                        │
│  - Assess b_theory (theoretical soundness)                  │
│  - Assess b_impl (implementation quality)                   │
│  - Assess b_deploy (deployment stability)                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 3: Unit Layer Assessment (@u)                         │
│  - Test on PDTs with varying quality                        │
│  - Measure sensitivity to PDT structure                     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 4: Contextual Compatibility                           │
│  - Map to questions (@q): semantic alignment                │
│  - Map to dimensions (@d): analytical capability            │
│  - Map to policies (@p): domain knowledge                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 5: Integration Testing                                │
│  - Run on validation PDTs (≥20)                             │
│  - Compare with existing methods                            │
│  - Validate contract compliance                             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 6: Documentation & Registration                       │
│  - Update intrinsic_calibration.json                        │
│  - Update method_compatibility.json                         │
│  - Write method documentation                               │
│  - Register in cohort manifest                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 1: Method Development

### 1.1 Implement Method Class

Create method in `src/methods_dispensary/`:

```python
"""
New Method for [Dimension] [Question]
======================================

Purpose: Brief description of what this method does

Theoretical Foundation: Cite academic sources
- Author1 et al. (Year)
- Framework name

Calibration Wave: COHORT_YYYY
"""

from typing import Any, Dict
from pydantic import BaseModel, Field


class NewMethodInput(BaseModel):
    """Input contract for NewMethod."""
    
    preprocessed_doc: Dict[str, Any]
    question_context: Dict[str, Any]
    sisas_signals: Dict[str, Any] | None = None


class NewMethodOutput(BaseModel):
    """Output contract for NewMethod."""
    
    score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: Dict[str, Any]
    provenance: Dict[str, Any]


class NewMethod:
    """
    Analytical method for [specific purpose].
    
    This method implements [technique] to assess [aspect] of the PDT.
    
    Example:
        >>> method = NewMethod()
        >>> input_data = NewMethodInput(
        ...     preprocessed_doc=doc,
        ...     question_context=ctx
        ... )
        >>> result = method.execute(input_data)
        >>> print(f"Score: {result.score:.3f}")
    """
    
    def __init__(self, seed: int = 42):
        """
        Initialize method with deterministic seed.
        
        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        # Initialize any required models, data structures
    
    def execute(self, input_data: NewMethodInput) -> NewMethodOutput:
        """
        Execute method on input data.
        
        Args:
            input_data: Validated input
        
        Returns:
            Validated output with score and evidence
        """
        # 1. Extract relevant data
        doc = input_data.preprocessed_doc
        context = input_data.question_context
        
        # 2. Apply analytical technique
        score = self._compute_score(doc, context)
        confidence = self._compute_confidence(doc, context)
        evidence = self._extract_evidence(doc, context)
        
        # 3. Build provenance
        provenance = {
            "method_id": "NewMethod",
            "method_version": "1.0.0",
            "cohort": "COHORT_YYYY",
            "seed": self.seed,
        }
        
        # 4. Validate and return
        return NewMethodOutput(
            score=score,
            confidence=confidence,
            evidence=evidence,
            provenance=provenance,
        )
    
    def _compute_score(self, doc, context) -> float:
        """Core scoring logic."""
        # Implement scoring algorithm
        pass
    
    def _compute_confidence(self, doc, context) -> float:
        """Confidence estimation."""
        # Implement confidence calculation
        pass
    
    def _extract_evidence(self, doc, context) -> Dict[str, Any]:
        """Evidence extraction with provenance."""
        # Extract supporting evidence
        pass
```

### 1.2 Write Unit Tests

Create test file in `tests/methods/`:

```python
"""Tests for NewMethod."""

import pytest
from src.methods_dispensary.new_method import NewMethod, NewMethodInput


class TestNewMethod:
    """Unit tests for NewMethod."""
    
    @pytest.fixture
    def method(self):
        """Create method instance."""
        return NewMethod(seed=42)
    
    @pytest.fixture
    def valid_input(self):
        """Create valid input data."""
        return NewMethodInput(
            preprocessed_doc={
                "text": "Sample PDT text...",
                "chunks": [...],
                "pdt_structure": {...},
            },
            question_context={
                "dimension": "D1",
                "question_id": "Q1",
                "policy_area": "PA01",
            }
        )
    
    def test_execute_returns_valid_output(self, method, valid_input):
        """Test method produces valid output."""
        result = method.execute(valid_input)
        
        assert 0.0 <= result.score <= 1.0
        assert 0.0 <= result.confidence <= 1.0
        assert result.evidence is not None
        assert result.provenance is not None
    
    def test_deterministic_execution(self, valid_input):
        """Test method is deterministic."""
        method1 = NewMethod(seed=42)
        method2 = NewMethod(seed=42)
        
        result1 = method1.execute(valid_input)
        result2 = method2.execute(valid_input)
        
        assert result1.score == result2.score
        assert result1.confidence == result2.confidence
    
    def test_score_range(self, method, valid_input):
        """Test score is always in [0, 1]."""
        for _ in range(10):
            result = method.execute(valid_input)
            assert 0.0 <= result.score <= 1.0
    
    def test_provenance_complete(self, method, valid_input):
        """Test provenance tracking is complete."""
        result = method.execute(valid_input)
        
        assert "method_id" in result.provenance
        assert "method_version" in result.provenance
        assert "cohort" in result.provenance
        assert "seed" in result.provenance
```

**Target**: ≥80% code coverage, all tests passing.

---

## Step 2: Base Layer Calibration (@b)

### 2.1 Assess b_theory (Theoretical Validity)

**Checklist**:

- [ ] **Statistical validity** (0.4 weight):
  - [ ] Statistical tests correctly applied?
  - [ ] Sample size requirements met?
  - [ ] Confidence intervals properly computed?
  - [ ] P-values interpreted correctly (no p-hacking)?

- [ ] **Logical consistency** (0.3 weight):
  - [ ] Reasoning chains sound (no fallacies)?
  - [ ] Conclusions follow from premises?
  - [ ] Edge cases handled?
  - [ ] No circular dependencies?

- [ ] **Appropriate assumptions** (0.3 weight):
  - [ ] Assumptions explicitly stated?
  - [ ] Assumptions justified for domain?
  - [ ] Violations detected and reported?
  - [ ] Sensitivity analysis validates robustness?

**Scoring**:
```python
b_theory = 0.4 * statistical_validity + 0.3 * logical_consistency + 0.3 * appropriate_assumptions
```

**Example**:
```python
# D6_Q5_TheoryOfChange
b_theory = 0.4 * 0.92 + 0.3 * 0.88 + 0.3 * 0.85 = 0.887
# HIGH: Uses PyMC with proper priors, explicit DAG, sensitivity checks
```

---

### 2.2 Assess b_impl (Implementation Quality)

**Checklist**:

- [ ] **Test coverage** (0.35 weight):
  - [ ] Unit tests for core logic?
  - [ ] Integration tests for data flow?
  - [ ] Edge case coverage?
  - [ ] Coverage ≥80%?

- [ ] **Type annotations** (0.25 weight):
  - [ ] All functions have type hints?
  - [ ] TypedDict contracts at boundaries?
  - [ ] mypy strict mode passes?
  - [ ] No unjustified `Any` types?

- [ ] **Error handling** (0.25 weight):
  - [ ] Exceptions typed and specific?
  - [ ] Error messages actionable?
  - [ ] Failures logged with context?
  - [ ] Resources cleaned up?

- [ ] **Documentation** (0.15 weight):
  - [ ] Docstrings for public functions?
  - [ ] Parameter descriptions?
  - [ ] Return value descriptions?
  - [ ] Example usage?

**Scoring**:
```python
b_impl = 0.35 * test_coverage + 0.25 * type_annotations + 0.25 * error_handling + 0.15 * documentation
```

**Measurement Tools**:
```bash
# Test coverage
pytest --cov=src/methods_dispensary/new_method --cov-report=term

# Type checking
mypy --strict src/methods_dispensary/new_method.py

# Docstring coverage
interrogate src/methods_dispensary/new_method.py
```

**Example**:
```python
# High-quality implementation
test_coverage = 0.87      # 87% line coverage
type_annotations = 0.95   # mypy strict passes, minimal Any
error_handling = 0.82     # All exceptions handled, logged
documentation = 0.78      # Docstrings present, examples included

b_impl = 0.35 * 0.87 + 0.25 * 0.95 + 0.25 * 0.82 + 0.15 * 0.78
       = 0.862
```

---

### 2.3 Assess b_deploy (Deployment Stability)

**Checklist**:

- [ ] **Validation runs** (0.4 weight):
  - [ ] Tested on ≥10 representative PDTs?
  - [ ] Diverse input data (different sizes, structures)?
  - [ ] Cross-validation on held-out data?

- [ ] **Stability coefficient** (0.35 weight):
  - [ ] Low output variance across runs?
  - [ ] Deterministic execution (seed control)?
  - [ ] CV < 0.05 for key metrics?

- [ ] **Failure rate** (0.25 weight):
  - [ ] Failure rate < 1%?
  - [ ] Graceful degradation on edge cases?
  - [ ] Recovery from transient errors?

**Scoring**:
```python
b_deploy = 0.4 * validation_runs + 0.35 * stability_coefficient + 0.25 * failure_rate
```

**Measurement Procedure**:

```python
def calibrate_b_deploy(method, validation_pdts: list) -> float:
    """
    Calibrate b_deploy through repeated validation.
    
    Args:
        method: Method instance
        validation_pdts: List of ≥10 PDTs
    
    Returns:
        b_deploy score
    """
    # 1. Run method on all PDTs
    results = []
    failures = 0
    
    for pdt in validation_pdts:
        try:
            result = method.execute(pdt)
            results.append(result.score)
        except Exception as e:
            failures += 1
            print(f"Failed on {pdt.id}: {e}")
    
    # 2. Validation runs score
    num_runs = len(results)
    if num_runs >= 20:
        runs_score = 1.0
    elif num_runs >= 10:
        runs_score = 0.8
    elif num_runs >= 5:
        runs_score = 0.5
    else:
        runs_score = 0.0
    
    # 3. Stability coefficient (CV)
    import numpy as np
    cv = np.std(results) / np.mean(results) if results else float('inf')
    
    if cv <= 0.05:
        stability_score = 1.0
    elif cv <= 0.10:
        stability_score = 0.8
    elif cv <= 0.20:
        stability_score = 0.5
    else:
        stability_score = 0.0
    
    # 4. Failure rate
    failure_rate = failures / (len(results) + failures)
    
    if failure_rate <= 0.01:
        failure_score = 1.0
    elif failure_rate <= 0.05:
        failure_score = 0.8
    elif failure_rate <= 0.10:
        failure_score = 0.5
    else:
        failure_score = 0.0
    
    # 5. Compute b_deploy
    b_deploy = 0.4 * runs_score + 0.35 * stability_score + 0.25 * failure_score
    
    print(f"Validation runs: {num_runs} (score: {runs_score})")
    print(f"CV: {cv:.4f} (score: {stability_score})")
    print(f"Failure rate: {failure_rate:.2%} (score: {failure_score})")
    print(f"b_deploy: {b_deploy:.3f}")
    
    return b_deploy
```

---

### 2.4 Compute Final @b Score

```python
@b = (b_theory + b_impl + b_deploy) / 3
```

**Example**:
```python
b_theory = 0.887
b_impl = 0.862
b_deploy = 0.947

@b = (0.887 + 0.862 + 0.947) / 3 = 0.899
```

**Interpretation**:
- **@b ≥ 0.7**: Production-ready ✅
- **0.5 ≤ @b < 0.7**: Needs improvement
- **@b < 0.5**: Not reliable (hard gate failure)

---

## Step 3: Unit Layer Assessment (@u)

**Objective**: Assess how method performs on PDTs with varying structural quality.

### 3.1 Create Test PDT Set

Assemble PDTs spanning @u quality range:

```python
TEST_PDTS = {
    "high_quality": [
        {"id": "PDT_001", "@u": 0.92},  # Excellent structure
        {"id": "PDT_002", "@u": 0.88},
        {"id": "PDT_003", "@u": 0.81},
    ],
    "medium_quality": [
        {"id": "PDT_004", "@u": 0.65},  # Acceptable structure
        {"id": "PDT_005", "@u": 0.58},
        {"id": "PDT_006", "@u": 0.52},
    ],
    "low_quality": [
        {"id": "PDT_007", "@u": 0.42},  # Poor structure
        {"id": "PDT_008", "@u": 0.35},
        {"id": "PDT_009", "@u": 0.28},
    ],
}
```

### 3.2 Measure Performance vs PDT Quality

```python
def assess_unit_layer_impact(method, test_pdts: dict) -> dict:
    """
    Measure method performance vs PDT quality.
    
    Returns:
        Sensitivity metrics
    """
    results = {"high": [], "medium": [], "low": []}
    
    for quality_band in ["high_quality", "medium_quality", "low_quality"]:
        for pdt in test_pdts[quality_band]:
            result = method.execute(pdt)
            results[quality_band.split("_")[0]].append({
                "pdt_id": pdt["id"],
                "@u": pdt["@u"],
                "score": result.score,
                "confidence": result.confidence,
            })
    
    # Compute sensitivity
    high_scores = [r["score"] for r in results["high"]]
    low_scores = [r["score"] for r in results["low"]]
    
    sensitivity = (np.mean(high_scores) - np.mean(low_scores)) / 0.6  # 0.6 = range of @u
    
    return {
        "results": results,
        "sensitivity": sensitivity,
        "interpretation": (
            "High sensitivity" if sensitivity > 0.5 else
            "Moderate sensitivity" if sensitivity > 0.2 else
            "Low sensitivity"
        ),
    }
```

**Interpretation**:
- **High sensitivity** (>0.5): Method strongly depends on PDT quality (good for @u interaction term)
- **Moderate sensitivity** (0.2-0.5): Method somewhat robust to PDT quality
- **Low sensitivity** (<0.2): Method very robust (may not leverage rich structure)

---

## Step 4: Contextual Compatibility

### 4.1 Question Appropriateness (@q)

**Objective**: Map method to questions it can answer.

**Procedure**:

1. **Semantic Alignment**: Compute embeddings similarity

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

# Question text
question_texts = {
    "Q1": "¿El plan presenta un diagnóstico cuantitativo?",
    "Q2": "¿Los indicadores tienen línea base?",
    "Q3": "¿Las actividades están vinculadas a objetivos?",
    "Q4": "¿Los resultados son medibles?",
    "Q5": "¿El plan incluye una teoría de cambio?",
}

# Method capability description
method_description = "Este método evalúa la presencia de teoría de cambio mediante análisis causal bayesiano."

# Compute similarities
method_emb = model.encode(method_description)
question_embs = {q_id: model.encode(q_text) for q_id, q_text in question_texts.items()}

from sklearn.metrics.pairwise import cosine_similarity
similarities = {
    q_id: cosine_similarity([method_emb], [q_emb])[0][0]
    for q_id, q_emb in question_embs.items()
}

print(similarities)
# Output:
# {
#   "Q1": 0.32,  # Low - method not for baseline analysis
#   "Q2": 0.28,  # Low - method not for indicators
#   "Q3": 0.45,  # Medium - method somewhat relevant
#   "Q4": 0.51,  # Medium - method partially relevant
#   "Q5": 0.89,  # HIGH - method directly addresses theory of change
# }
```

2. **Priority Matching**: Assign method priority and compute @q

```python
METHOD_PRIORITY = 3  # Supplementary (theory of change not mandatory)

def compute_q_score(question_id: str, semantic_sim: float, question_priority: int, method_priority: int) -> float:
    """Compute @q score."""
    priority_matrix = {
        (1, 1): 1.0, (1, 2): 0.7, (1, 3): 0.4,
        (2, 1): 0.9, (2, 2): 1.0, (2, 3): 0.6,
        (3, 1): 0.8, (3, 2): 0.9, (3, 3): 1.0,
    }
    priority_score = priority_matrix[(question_priority, method_priority)]
    
    @q = 0.6 * semantic_sim + 0.4 * priority_score
    return @q

# Example: Q5 (priority 3)
@q_Q5 = compute_q_score("Q5", 0.89, 3, 3)
print(f"@q for Q5: {@q_Q5:.3f}")
# Output: @q for Q5: 0.934 (excellent fit)
```

**Result**: Populate method_compatibility.json

```json
{
  "NewMethod": {
    "questions": {
      "Q1": 0.32,
      "Q2": 0.28,
      "Q3": 0.45,
      "Q4": 0.51,
      "Q5": 0.93
    }
  }
}
```

---

### 4.2 Dimension Alignment (@d)

**Objective**: Determine which dimensions the method can analyze.

**Criteria per dimension**:

- **D1 (INSUMOS)**: Quantitative profiling, baseline extraction
- **D2 (ACTIVIDADES)**: Logical framework, feasibility
- **D3 (PRODUCTOS)**: Output quantification, deliverables
- **D4 (RESULTADOS)**: Outcome logic, attribution
- **D5 (IMPACTOS)**: Impact pathways, sustainability
- **D6 (CAUSALIDAD)**: Causal inference, mechanism tracing

**Scoring**:

```python
DIMENSION_REQUIREMENTS = {
    "D1": ["quantitative_analysis", "baseline_extraction"],
    "D2": ["logical_framework", "feasibility_assessment"],
    "D3": ["output_quantification", "deliverable_tracking"],
    "D4": ["outcome_logic", "attribution_analysis"],
    "D5": ["impact_pathway", "sustainability_assessment"],
    "D6": ["causal_inference", "mechanism_tracing"],
}

METHOD_CAPABILITIES = {
    "NewMethod": [
        "causal_inference",       # Primary
        "mechanism_tracing",      # Primary
        "outcome_logic",          # Secondary
        "attribution_analysis",   # Secondary
    ]
}

def compute_d_score(dimension: str, method_capabilities: list) -> float:
    """Compute @d score."""
    required = set(DIMENSION_REQUIREMENTS[dimension])
    has = set(method_capabilities)
    
    overlap = required & has
    coverage = len(overlap) / len(required)
    
    # Bonus for perfect match
    if coverage == 1.0:
        return 1.0
    elif coverage >= 0.5:
        return 0.5 + 0.5 * coverage
    else:
        return coverage

# Example: NewMethod vs D6
@d_D6 = compute_d_score("D6", METHOD_CAPABILITIES["NewMethod"])
print(f"@d for D6: {@d_D6:.3f}")
# Output: @d for D6: 1.000 (perfect match)

# Example: NewMethod vs D4
@d_D4 = compute_d_score("D4", METHOD_CAPABILITIES["NewMethod"])
print(f"@d for D4: {@d_D4:.3f}")
# Output: @d for D4: 0.750 (good match, 2/2 capabilities)
```

**Result**: Update method_compatibility.json

```json
{
  "NewMethod": {
    "dimensions": {
      "DIM01": 0.20,
      "DIM02": 0.35,
      "DIM03": 0.40,
      "DIM04": 0.75,
      "DIM05": 0.60,
      "DIM06": 1.00
    }
  }
}
```

---

### 4.3 Policy Area Fit (@p)

**Objective**: Assess domain knowledge for PA01-PA10.

**Procedure**: Test on policy-area-specific PDTs

```python
def calibrate_p_scores(method, policy_area_pdts: dict) -> dict:
    """
    Calibrate @p scores by running on policy-area-specific PDTs.
    
    Args:
        policy_area_pdts: Dict mapping PA01-PA10 to list of PDTs
    
    Returns:
        @p scores per policy area
    """
    p_scores = {}
    
    for pa_id, pdts in policy_area_pdts.items():
        scores = []
        for pdt in pdts:
            result = method.execute(pdt)
            scores.append(result.score)
        
        # Average performance = domain fit
        mean_score = np.mean(scores)
        std_score = np.std(scores)
        
        # Lower variance = better domain fit
        p_score = mean_score * (1 - std_score)
        p_scores[pa_id] = p_score
    
    return p_scores

# Example
p_scores = calibrate_p_scores(new_method, {
    "PA01": [pdt_pa01_1, pdt_pa01_2, pdt_pa01_3],
    "PA02": [pdt_pa02_1, pdt_pa02_2, pdt_pa02_3],
    # ... PA03-PA10
})

print(p_scores)
# Output:
# {
#   "PA01": 0.85,  # High - gender equality (strong causal focus)
#   "PA02": 0.78,  # Good - violence prevention
#   "PA03": 0.65,  # Medium - environment
#   ...
# }
```

---

## Step 5: Integration Testing

### 5.1 End-to-End Pipeline Test

Run method through full pipeline:

```bash
# Activate environment
source farfan-env/bin/activate

# Run pipeline with new method
python -m src.orchestration.orchestrator \
  --pdt data/test_pdts/municipality_X.pdf \
  --questionnaire config/questionnaire_monolith.json \
  --cohort COHORT_2024 \
  --executor NewMethod \
  --output output/test_newmethod/
```

**Verify**:
- [ ] No errors or warnings
- [ ] Output contract validated
- [ ] @chain = 1.0 (chain intact)
- [ ] @C ≥ 0.7 (contract compliance)
- [ ] Results in expected range

---

### 5.2 Comparison with Existing Methods

Compare new method vs existing baselines:

```python
def compare_with_baselines(new_method, baseline_methods, validation_pdts):
    """Compare new method with existing methods."""
    results = {"NewMethod": [], "Baseline1": [], "Baseline2": []}
    
    for pdt in validation_pdts:
        results["NewMethod"].append(new_method.execute(pdt).score)
        for baseline_name, baseline_method in baseline_methods.items():
            results[baseline_name].append(baseline_method.execute(pdt).score)
    
    # Correlation analysis
    from scipy.stats import spearmanr
    
    print("Correlation with baselines:")
    for baseline_name in baseline_methods:
        corr, p_value = spearmanr(results["NewMethod"], results[baseline_name])
        print(f"  {baseline_name}: r={corr:.3f}, p={p_value:.4f}")
    
    # Mean performance
    print("\nMean scores:")
    for method_name, scores in results.items():
        print(f"  {method_name}: {np.mean(scores):.3f} ± {np.std(scores):.3f}")
```

**Target**: New method should correlate ≥0.7 with existing methods for same dimension/question.

---

### 5.3 Contract Validation

Verify all output contracts:

```python
def validate_output_contracts(method, test_cases):
    """Validate method outputs against contracts."""
    violations = []
    
    for test_case in test_cases:
        result = method.execute(test_case)
        
        # Check score range
        if not (0.0 <= result.score <= 1.0):
            violations.append(f"Score out of range: {result.score}")
        
        # Check confidence range
        if not (0.0 <= result.confidence <= 1.0):
            violations.append(f"Confidence out of range: {result.confidence}")
        
        # Check required fields
        required_fields = ["evidence", "provenance"]
        for field in required_fields:
            if not hasattr(result, field) or getattr(result, field) is None:
                violations.append(f"Missing required field: {field}")
        
        # Check provenance completeness
        required_prov_fields = ["method_id", "method_version", "cohort", "seed"]
        for field in required_prov_fields:
            if field not in result.provenance:
                violations.append(f"Provenance missing: {field}")
    
    if violations:
        print("Contract violations:")
        for v in violations:
            print(f"  - {v}")
        return False
    else:
        print("All contracts validated ✓")
        return True
```

---

## Step 6: Documentation

### 6.1 Update intrinsic_calibration.json

Add method entry:

```json
{
  "methods": {
    "NewMethod": {
      "b_theory": 0.887,
      "b_impl": 0.862,
      "b_deploy": 0.947,
      "b_overall": 0.899,
      "notes": "Bayesian causal inference for theory of change. Strong theoretical foundation, excellent deployment stability.",
      "calibration_date": "2024-12-16",
      "calibrator": "Analyst Name",
      "cohort": "COHORT_2024"
    }
  }
}
```

### 6.2 Update method_compatibility.json

Add compatibility mappings:

```json
{
  "NewMethod": {
    "questions": {
      "Q1": 0.32, "Q2": 0.28, "Q3": 0.45, "Q4": 0.51, "Q5": 0.93
    },
    "dimensions": {
      "DIM01": 0.20, "DIM02": 0.35, "DIM03": 0.40,
      "DIM04": 0.75, "DIM05": 0.60, "DIM06": 1.00
    },
    "policies": {
      "PA01": 0.85, "PA02": 0.78, "PA03": 0.65,
      "PA04": 0.82, "PA05": 0.88, "PA06": 0.75,
      "PA07": 0.70, "PA08": 0.80, "PA09": 0.68, "PA10": 0.72
    }
  }
}
```

### 6.3 Write Method Documentation

Create `docs/methods/NewMethod.md`:

```markdown
# NewMethod

**Bayesian Causal Inference for Theory of Change Analysis**

## Overview

NewMethod implements Bayesian causal inference using PyMC to evaluate the presence and quality of a Theory of Change in PDTs.

## Theoretical Foundation

- **Framework**: Falleti & Lynch (2009) - Process tracing with Bayesian mechanisms
- **Implementation**: PyMC probabilistic programming
- **Citation**: Pearl (2000) - Causality: Models, Reasoning, and Inference

## Calibration Scores

| Layer | Score | Band |
|-------|-------|------|
| @b (Intrinsic) | 0.899 | EXCELLENT |
| b_theory | 0.887 | EXCELLENT |
| b_impl | 0.862 | EXCELLENT |
| b_deploy | 0.947 | EXCELLENT |

## Best Suited For

- **Dimensions**: D6 (Causality), D4 (Outcomes)
- **Questions**: Q5 (Theory of Change), Q4 (Result Logic)
- **Policy Areas**: PA01 (Gender), PA05 (Victims' Rights), PA02 (Violence Prevention)

## Usage Example

\`\`\`python
from src.methods_dispensary.new_method import NewMethod

method = NewMethod(seed=42)
result = method.execute(input_data)

print(f"Theory of Change Score: {result.score:.3f}")
print(f"Confidence: {result.confidence:.3f}")
\`\`\`

## Limitations

- Requires structured PDT with Estratégica section
- Minimum 500 tokens needed for causal analysis
- Struggles with implicit theories (prefers explicit)

## Calibration History

- **COHORT_2024** (2024-12-16): Initial calibration
  - Validated on 25 PDTs
  - @b = 0.899, @u sensitivity = 0.45
```

### 6.4 Register in Cohort Manifest

Update `COHORT_MANIFEST.json`:

```json
{
  "cohort_id": "COHORT_2024",
  "methods": {
    "NewMethod": {
      "calibration_hash": "sha256:abc123...",
      "calibration_date": "2024-12-16",
      "status": "production",
      "executors": ["D6_Q5_NewMethod"]
    }
  }
}
```

---

## Example: Calibrating a New Method

**Scenario**: Calibrate "SustainabilityScorer" for D5 (Impacts).

### Step 1: Implement

```python
class SustainabilityScorer:
    """Assess long-term sustainability of PDT programs."""
    
    def execute(self, input_data):
        # Extract sustainability indicators
        financial = self._assess_financial_sustainability(input_data)
        institutional = self._assess_institutional_capacity(input_data)
        social = self._assess_social_support(input_data)
        
        # Weighted score
        score = 0.4 * financial + 0.35 * institutional + 0.25 * social
        
        return SustainabilityScorerOutput(
            score=score,
            confidence=self._compute_confidence(...),
            evidence={...},
            provenance={...},
        )
```

### Step 2: Calibrate @b

```python
# b_theory: Sustainability framework is well-established
b_theory = 0.4 * 0.85 + 0.3 * 0.80 + 0.3 * 0.82 = 0.826

# b_impl: 75% test coverage, strict typing, good docs
b_impl = 0.35 * 0.75 + 0.25 * 0.90 + 0.25 * 0.78 + 0.15 * 0.85 = 0.810

# b_deploy: 15 validation runs, CV=0.08, 2% failure rate
b_deploy = 0.4 * 0.80 + 0.35 * 0.80 + 0.25 * 0.80 = 0.800

# Final @b
@b = (0.826 + 0.810 + 0.800) / 3 = 0.812  # EXCELLENT
```

### Step 3: Calibrate @u Sensitivity

```python
# Test on high/medium/low quality PDTs
high_avg = 0.78
low_avg = 0.52
sensitivity = (0.78 - 0.52) / 0.6 = 0.43  # MODERATE
```

### Step 4: Calibrate @q, @d, @p

```python
# Semantic alignment with D5 questions
@q = {
    "Q1": 0.45,  # Medium - partially relevant
    "Q2": 0.62,  # Good - targets sustainability
    "Q3": 0.88,  # Excellent - directly about sustainability
    "Q4": 0.71,  # Good - spillover related
    "Q5": 0.67,  # Good - structural change related
}

# Dimension fit
@d = {
    "DIM05": 1.00,  # Perfect - designed for impacts
    "DIM04": 0.65,  # Good - outcomes related
    "DIM03": 0.40,  # Weak - outputs not main focus
}

# Policy area fit (test on PA-specific PDTs)
@p = {
    "PA01": 0.72, "PA02": 0.68, "PA03": 0.85,  # High for environment
    # ... PA04-PA10
}
```

### Step 5: Register

```json
{
  "methods": {
    "SustainabilityScorer": {
      "b_overall": 0.812,
      "b_theory": 0.826,
      "b_impl": 0.810,
      "b_deploy": 0.800,
      "cohort": "COHORT_2024",
      "calibration_date": "2024-12-16"
    }
  }
}
```

**Result**: SustainabilityScorer is now production-ready for D5 analysis! ✅

---

## Related Documentation

- [CONFIG_REFERENCE.md](./CONFIG_REFERENCE.md) - Configuration schemas
- [THRESHOLD_GUIDE.md](./THRESHOLD_GUIDE.md) - Quality thresholds
- [DETERMINISM.md](./DETERMINISM.md) - Calibration vs parametrization
- [LAYER_SYSTEM.md](./LAYER_SYSTEM.md) - Layer definitions

---

**Last Updated**: 2024-12-16  
**Version**: 1.0.0  
**Maintainers**: Policy Analytics Research Unit

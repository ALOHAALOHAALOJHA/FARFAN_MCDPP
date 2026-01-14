# Method Registry Governance

## Methods → Unit of Analysis Mapping

Each method MUST document which unit characteristics it uses:

| Method | Uses UnitOfAnalysis? | Which Characteristics | Justification |
|--------|---------------------|---------------------|---------------|
| `bayesian_multilevel_system.py` | YES | `complexity_score()`, `population` | Micro-level reconciliation needs scale |
| `semantic_chunking_policy.py` | NO | N/A | Content-agnostic chunking |
| `policy_processor.py` | YES | ALL | Full policy analysis needs context |
| `causal_inference_dowhy.py` | YES | `fiscal_context` | Causal inference varies by fiscal capacity |

## Required Documentation Pattern

Each method class MUST have:

```python
class SomeMethod:
    """
    Method Description...

    Unit of Analysis Requirements:
    - Requires: [population, budget, fiscal_context]
    - Sensitive_to: [complexity_score, municipality_category]
    - Calibration_adjustments: [complexity_score > 0.7 → increase_prior_strength]

    Epistemological Level:
    - Level: N2-INF (or N1-EMP, N3-AUD)
    - Output: FACT (or PROBABILITY, CONSTRAINT)
    - Fusion: concatenative (or multiplicative, gated)
    """
```

Audit Command

# Find methods missing Unit of Analysis documentation
grep -L "Unit of Analysis Requirements" src/farfan_pipeline/methods/*.py

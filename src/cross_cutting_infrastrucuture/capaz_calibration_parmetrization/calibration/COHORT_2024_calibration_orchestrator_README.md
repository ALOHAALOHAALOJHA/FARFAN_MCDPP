# COHORT_2024 Calibration Orchestrator

**SENSITIVE - CALIBRATION SYSTEM CRITICAL**

## Overview

The `CalibrationOrchestrator` implements the complete calibration workflow for F.A.R.F.A.N. methods, orchestrating layer score computation, Choquet integral fusion, and certificate generation.

## Authority

- **Cohort**: COHORT_2024
- **Wave**: REFACTOR_WAVE_2024_12 / GOVERNANCE_WAVE_2024_12_07
- **Authority**: Doctrina SIN_CARRETA
- **Compliance**: SUPERPROMPT Three-Pillar Calibration System
- **Label**: CONFIG_GOVERNANCE_STRICT_FOLDERIZATION

## Architecture

### Layer System

The orchestrator evaluates 8 calibration layers based on method role:

| Layer | Symbol | Description | Source |
|-------|--------|-------------|--------|
| Base | `@b` | Code quality (theory, implementation, deployment) | intrinsic_calibration.json |
| Chain | `@chain` | Method wiring/orchestration | intrinsic_scores |
| Question | `@q` | Question appropriateness | method_compatibility.json |
| Dimension | `@d` | Dimension alignment | method_compatibility.json |
| Policy | `@p` | Policy area fit | method_compatibility.json |
| Contract | `@C` | Contract compliance | intrinsic_scores |
| Unit | `@u` | Document quality | PDT structure |
| Meta | `@m` | Governance maturity | governance_artifacts |

### Role-Based Layer Requirements

Role mapping via `LAYER_REQUIREMENTS`:

```python
LAYER_REQUIREMENTS = {
    "executor": ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"],  # All 8 layers
    "analyzer": ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"],  # All 8 layers
    "score": ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"],     # All 8 layers
    "core": ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"],      # All 8 layers
    "ingest": ["@b", "@chain", "@u", "@m"],                            # 4 layers
    "processor": ["@b", "@chain", "@u", "@m"],                         # 4 layers
    "extractor": ["@b", "@chain", "@u", "@m"],                         # 4 layers
    "orchestrator": ["@b", "@chain", "@m"],                            # 3 layers
    "utility": ["@b", "@chain", "@m"],                                 # 3 layers
}
```

### Choquet Integral Fusion

**Formula**: `Cal(I) = Σ(a_ℓ · x_ℓ) + Σ(a_ℓk · min(x_ℓ, x_k))`

Where:
- `a_ℓ`: Linear weights from `COHORT_2024_fusion_weights.json`
- `a_ℓk`: Interaction weights for layer pairs
- `x_ℓ`: Layer scores ∈ [0,1]

**Constraints**:
- `a_ℓ ≥ 0` for all `ℓ`
- `a_ℓk ≥ 0` for all `(ℓ,k)`
- `Σ(a_ℓ) + Σ(a_ℓk) = 1.0`
- `Cal(I) ∈ [0,1]` (bounded)
- `∂Cal/∂x_ℓ ≥ 0` (monotonic)

## API Reference

### CalibrationOrchestrator

```python
class CalibrationOrchestrator:
    def __init__(self, fusion_weights_path: str | None = None):
        """
        Initialize calibration orchestrator.
        
        Args:
            fusion_weights_path: Path to fusion weights JSON (defaults to COHORT_2024_fusion_weights.json)
        """
    
    def calibrate(
        self,
        method_id: str,
        context: CalibrationContext | None = None,
        evidence: CalibrationEvidence | None = None,
    ) -> CalibrationResult:
        """
        Perform complete calibration for a method.
        
        Args:
            method_id: Fully qualified method identifier
            context: Contextual information (question_id, dimension_id, policy_area_id)
            evidence: Evidence artifacts (intrinsic_scores, compatibility_registry, pdt_structure, governance_artifacts)
        
        Returns:
            CalibrationResult with final score, layer breakdown, and certificate
        """
```

### Data Structures

```python
class CalibrationContext(TypedDict, total=False):
    question_id: str | None          # e.g., "Q001"
    dimension_id: str | None         # e.g., "DIM01"
    policy_area_id: str | None       # e.g., "PA01"

class CalibrationEvidence(TypedDict, total=False):
    intrinsic_scores: dict[str, float]              # Base/chain/contract scores
    compatibility_registry: dict[str, dict[str, float]]  # method_compatibility.json
    pdt_structure: dict[str, Any]                   # PDT structure for unit layer
    governance_artifacts: dict[str, Any]            # Version/hash/signature for meta layer

class CalibrationResult(TypedDict):
    method_id: str
    role: str
    final_score: float                              # ∈ [0.0, 1.0]
    layer_scores: dict[str, float]                  # Scores for active layers
    active_layers: list[str]                        # Required layers for this role
    fusion_breakdown: dict[str, Any]                # Linear/interaction contributions
    certificate_metadata: dict[str, Any]            # SHA256 hash, timestamp, authority
    validation: dict[str, Any]                      # Boundedness check
```

## Usage Examples

### Example 1: Basic Calibration

```python
from src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration.COHORT_2024_calibration_orchestrator import (
    CalibrationOrchestrator,
    CalibrationContext,
    CalibrationEvidence,
)

orchestrator = CalibrationOrchestrator()

result = orchestrator.calibrate(
    method_id="farfan_pipeline.core.executors.D1_Q1_Executor",
    context=CalibrationContext(
        question_id="Q001",
        dimension_id="DIM01",
        policy_area_id="PA01",
    ),
    evidence=CalibrationEvidence(
        intrinsic_scores={
            "base_layer_score": 0.85,
            "chain_layer_score": 0.78,
            "contract_layer_score": 0.92,
        },
    ),
)

print(f"Final Score: {result['final_score']:.3f}")
print(f"Active Layers: {result['active_layers']}")
print(f"Certificate ID: {result['certificate_metadata']['certificate_id']}")
```

### Example 2: With Full Evidence

```python
result = orchestrator.calibrate(
    method_id="farfan_pipeline.processing.ingest.PDTParser",
    evidence=CalibrationEvidence(
        intrinsic_scores={
            "b_theory": 0.90,
            "b_impl": 0.85,
            "b_deploy": 0.88,
            "chain_layer_score": 0.82,
        },
        pdt_structure={
            "total_tokens": 12000,
            "blocks_found": {"Diagnóstico": {}, "Estratégica": {}, "PPI": {}, "Seguimiento": {}},
            "indicator_matrix_present": True,
            "ppi_matrix_present": True,
        },
        governance_artifacts={
            "version_tag": "COHORT_2024_v1.2.3",
            "config_hash": "a" * 64,
            "signature": "b" * 64,
        },
    ),
)
```

### Example 3: Minimal (Defaults)

```python
result = orchestrator.calibrate(
    method_id="farfan_pipeline.utils.StringNormalizer"
)
```

## Layer Score Computation

### Base Layer (`@b`)

Computed from:
1. `intrinsic_scores["base_layer_score"]` (if present), OR
2. Weighted sum: `0.40 * b_theory + 0.35 * b_impl + 0.25 * b_deploy`
3. Default: `0.5`

### Contextual Layers (`@q`, `@d`, `@p`)

Looked up from `compatibility_registry[method_id]`:
- `@q`: `questions[question_id]` (default: 0.5)
- `@d`: `dimensions[dimension_id]` (default: 0.5)
- `@p`: `policies[policy_area_id]` (default: 0.5)

### Chain Layer (`@chain`)

From `intrinsic_scores["chain_layer_score"]` (default: 0.7)

### Contract Layer (`@C`)

From `intrinsic_scores["contract_layer_score"]` (default: 0.8)

### Unit Layer (`@u`)

Computed from PDT structure:
- Structure score: `min(len(blocks_found) / 4.0, 1.0)` (40% weight)
- Token score: thresholded on total_tokens (30% weight)
- Matrix score: indicator + PPI presence (30% weight)

Default: `0.5`

### Meta Layer (`@m`)

Computed from governance artifacts:
- 3 valid artifacts → 1.0
- 2 valid artifacts → 0.66
- 1 valid artifact → 0.33
- 0 valid artifacts → 0.0

Default: `0.5`

## Fusion Breakdown

The `fusion_breakdown` field contains:

```python
{
    "final_score": 0.823,              # Cal(I)
    "linear_sum": 0.598,               # Σ(a_ℓ · x_ℓ)
    "interaction_sum": 0.225,          # Σ(a_ℓk · min(x_ℓ, x_k))
    "linear_contributions": {
        "@b": 0.122,
        "@chain": 0.065,
        "@q": 0.082,
        "@d": 0.066,
        "@p": 0.049,
        "@C": 0.082,
        "@u": 0.098,
        "@m": 0.034
    },
    "interaction_contributions": {
        "(@u,@chain)": 0.150,
        "(@chain,@C)": 0.120,
        "(@q,@d)": 0.080,
        "(@d,@p)": 0.050
    }
}
```

## Certificate Metadata

Every calibration produces a cryptographic certificate:

```python
{
    "certificate_id": "a3f9d2c1b8e7",  # First 16 chars of hash
    "certificate_hash": "a3f9d2c1b8e7...",  # Full SHA256
    "timestamp": "2024-12-15T14:23:45.123456+00:00",
    "cohort_id": "COHORT_2024",
    "wave_version": "REFACTOR_WAVE_2024_12",
    "implementation_wave": "GOVERNANCE_WAVE_2024_12_07",
    "authority": "Doctrina SIN_CARRETA",
    "spec_compliance": "SUPERPROMPT Three-Pillar Calibration System",
    "fusion_formula": "Cal(I) = Σ(a_ℓ · x_ℓ) + Σ(a_ℓk · min(x_ℓ, x_k))"
}
```

## Validation

The orchestrator validates:

1. **Boundedness**: `Cal(I) ∈ [0.0, 1.0]`
   - If violated, score is clamped
   - Violation recorded in `validation["violation"]`

2. **Monotonicity**: Ensured by non-negative weights

3. **Normalization**: `Σ(a_ℓ) + Σ(a_ℓk) = 1.0` (validated at load time)

## File Dependencies

Required JSON files:
- `COHORT_2024_fusion_weights.json` (or `fusion_weights.json` fallback)
- `COHORT_2024_intrinsic_calibration.json`
- `COHORT_2024_method_compatibility.json`

Required Python modules:
- `COHORT_2024_layer_assignment.py` (for `LAYER_REQUIREMENTS`)

## Integration Points

### With Phase Orchestrator

```python
from src.orchestration.orchestrator import Orchestrator
from src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration.COHORT_2024_calibration_orchestrator import CalibrationOrchestrator

calibrator = CalibrationOrchestrator()

# In phase handler:
result = calibrator.calibrate(
    method_id=f"farfan_pipeline.core.executors.{executor_class.__name__}",
    context={"question_id": "Q001", "dimension_id": "DIM01"},
    evidence={"intrinsic_scores": load_method_scores(executor_class)}
)
```

### With Method Registry

```python
from src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.method_registry import MethodRegistry

registry = MethodRegistry()
calibrator = CalibrationOrchestrator()

for method_id in registry.list_methods():
    result = calibrator.calibrate(method_id)
    registry.update_calibration_score(method_id, result["final_score"])
```

## Audit Trail

All calibrations produce:
1. **Certificate hash**: SHA256 of (method_id, role, score, layers, fusion_breakdown)
2. **Timestamp**: UTC ISO 8601
3. **Cohort metadata**: Full traceability to COHORT_2024
4. **Authority**: Doctrina SIN_CARRETA attribution

## Security & Sensitivity

This module is **SENSITIVE** because it:
- Determines final calibration scores for all methods
- Implements the core fusion algorithm
- Generates cryptographic certificates
- Enforces role-based layer requirements

**Access Control**: Restricted to calibration system administrators and audit trails.

**Change Management**: All changes require:
1. COHORT governance approval
2. Mathematical validation of fusion formula
3. Regression testing against canonical inventory
4. Update to certificate generation logic

## References

- **Mathematical Foundation**: `mathematical_foundations_capax_system.md`
- **Layer Assignment**: `COHORT_2024_layer_assignment.py`
- **Fusion Weights**: `COHORT_2024_fusion_weights.json`
- **Intrinsic Calibration**: `COHORT_2024_intrinsic_calibration.json`
- **Method Compatibility**: `COHORT_2024_method_compatibility.json`

## Version History

- **1.0.0** (2024-12-15): Initial COHORT_2024 implementation
  - Role-based layer requirements
  - Choquet integral fusion
  - Certificate generation
  - Boundedness validation

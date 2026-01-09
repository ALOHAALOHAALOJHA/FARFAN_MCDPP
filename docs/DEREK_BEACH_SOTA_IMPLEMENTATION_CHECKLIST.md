# Derek Beach SOTA Implementation Checklist

## Quick Reference Guide for Library Enhancement

---

## Phase 1: Quick Wins (Week 1-2)

### ✅ Task 1.1: Standardize BGE-M3 Embeddings (2 hours)

**File**: `src/farfan_pipeline/methods/embedding_policy.py`

**Change**:
```python
# Line 62 - Replace:
MODEL_PARAPHRASE_MULTILINGUAL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

# With:
MODEL_PARAPHRASE_MULTILINGUAL = "BAAI/bge-m3"
```

**Validation**:
```bash
pytest tests/ -k embedding
python -m farfan_pipeline.methods.embedding_policy  # If standalone test exists
```

---

### ✅ Task 1.2: Install DoWhy (3-5 days)

**Step 1**: Add to requirements
```bash
# Add to requirements.txt:
dowhy>=0.11.1

# Install:
pip install dowhy>=0.11.1
```

**Step 2**: Update `pyproject.toml`
```toml
# Add to dependencies list (line ~39):
"dowhy>=0.11.1",
```

**Step 3**: Create DoWhy integration module
```bash
# Create new file:
src/farfan_pipeline/methods/causal_inference_dowhy.py
```

**Step 4**: Basic integration template
```python
# src/farfan_pipeline/methods/causal_inference_dowhy.py

"""
DoWhy Integration for Causal Inference
Enhances derek_beach.py with formal causal identification
"""

from typing import Any
import pandas as pd
import networkx as nx
from dowhy import CausalModel

class DoWhyCausalAnalyzer:
    """Wrapper for DoWhy causal inference operations"""

    def __init__(self, causal_graph: nx.DiGraph):
        self.graph = causal_graph

    def identify_effect(
        self,
        data: pd.DataFrame,
        treatment: str,
        outcome: str,
        common_causes: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Identify causal effect using do-calculus

        Args:
            data: Policy data as DataFrame
            treatment: Treatment variable (e.g., 'intervencion')
            outcome: Outcome variable (e.g., 'resultado')
            common_causes: List of confounders

        Returns:
            Dictionary with identified effect and diagnostics
        """
        model = CausalModel(
            data=data,
            treatment=treatment,
            outcome=outcome,
            graph=self._convert_to_dowhy_graph(self.graph),
            common_causes=common_causes
        )

        identified_estimand = model.identify_effect(proceed_when_unidentifiable=True)

        return {
            'estimand': identified_estimand,
            'identification_status': 'identified' if identified_estimand else 'unidentified',
            'backdoor_paths': identified_estimand.backdoor_variables if identified_estimand else [],
        }

    def estimate_effect(
        self,
        data: pd.DataFrame,
        treatment: str,
        outcome: str,
        method: str = "backdoor.linear_regression"
    ) -> dict[str, Any]:
        """Estimate causal effect with specified method"""
        model = CausalModel(
            data=data,
            treatment=treatment,
            outcome=outcome,
            graph=self._convert_to_dowhy_graph(self.graph)
        )

        identified_estimand = model.identify_effect()
        estimate = model.estimate_effect(
            identified_estimand,
            method_name=method
        )

        return {
            'value': estimate.value,
            'confidence_interval': (estimate.value - 1.96*estimate.stderr,
                                   estimate.value + 1.96*estimate.stderr),
            'method': method,
        }

    def refute_estimate(
        self,
        data: pd.DataFrame,
        treatment: str,
        outcome: str,
        estimate: Any,
        methods: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Refute causal estimate with robustness checks

        Methods:
        - placebo_treatment_refuter
        - random_common_cause
        - data_subset_refuter
        """
        if methods is None:
            methods = [
                "placebo_treatment_refuter",
                "random_common_cause",
                "data_subset_refuter"
            ]

        model = CausalModel(
            data=data,
            treatment=treatment,
            outcome=outcome,
            graph=self._convert_to_dowhy_graph(self.graph)
        )

        identified_estimand = model.identify_effect()

        refutation_results = {}
        for method in methods:
            try:
                refute = model.refute_estimate(
                    identified_estimand,
                    estimate,
                    method_name=method
                )
                refutation_results[method] = {
                    'refuted': refute.refutation_result is not None,
                    'p_value': getattr(refute, 'p_value', None),
                    'summary': str(refute)
                }
            except Exception as e:
                refutation_results[method] = {'error': str(e)}

        return refutation_results

    def _convert_to_dowhy_graph(self, nx_graph: nx.DiGraph) -> str:
        """Convert NetworkX graph to DoWhy GML format"""
        edges = [f"{u}->{v}" for u, v in nx_graph.edges()]
        return "digraph {" + "; ".join(edges) + "}"
```

> **Note:** DoWhy accepts NetworkX DiGraph objects directly via the `graph=`
> parameter. No format conversion is required. The `_get_dowhy_compatible_graph`
> method exists for API consistency and documentation purposes.

**Step 5**: Integration with `derek_beach.py`
```python
# Add to derek_beach.py imports:
from farfan_pipeline.methods.causal_inference_dowhy import DoWhyCausalAnalyzer

# In CDAFEngine.__init__ (around line 5815):
self.dowhy_analyzer = DoWhyCausalAnalyzer(nx.DiGraph())

# In extract_causal_links method (around line 2567):
if self.dowhy_analyzer:
    # Convert evidence to DataFrame
    policy_df = self._prepare_policy_dataframe(nodes, text)

    # Identify causal effects
    causal_analysis = self.dowhy_analyzer.identify_effect(
        data=policy_df,
        treatment='source_node',
        outcome='target_node'
    )

    self.logger.info(f"DoWhy identification: {causal_analysis['identification_status']}")
```

**Validation**:
```bash
pytest tests/test_causal_inference_dowhy.py
python -c "from farfan_pipeline.methods.causal_inference_dowhy import DoWhyCausalAnalyzer; print('OK')"
```

---

## Phase 2: Core Infrastructure (Week 3-4)

### ✅ Task 2.1: Create Bayesian Engine Module (7-10 days)

**Step 1**: Create directory structure
```bash
mkdir -p src/farfan_pipeline/inference
touch src/farfan_pipeline/inference/__init__.py
touch src/farfan_pipeline/inference/bayesian_adapter.py
touch src/farfan_pipeline/inference/bayesian_prior_builder.py
touch src/farfan_pipeline/inference/bayesian_sampling_engine.py
touch src/farfan_pipeline/inference/bayesian_diagnostics.py
```

**Step 2**: Implement `bayesian_adapter.py`
```python
# src/farfan_pipeline/inference/bayesian_adapter.py

"""
Bayesian Engine Adapter (F1.2 Refactoring)
Unified interface for Bayesian inference operations
"""

from typing import Any
import logging
import pymc as pm
import arviz as az
import numpy as np

from .bayesian_prior_builder import BayesianPriorBuilder
from .bayesian_sampling_engine import BayesianSamplingEngine

class BayesianEngineAdapter:
    """
    Unified Bayesian inference adapter

    Integrates:
    - BayesianPriorBuilder (AGUJA I): Adaptive prior construction
    - BayesianSamplingEngine (AGUJA II): MCMC sampling with diagnostics
    - BayesianDiagnostics: Model validation and convergence checks
    """

    def __init__(self, config: Any, nlp_model: Any = None):
        self.config = config
        self.nlp = nlp_model
        self.logger = logging.getLogger(self.__class__.__name__)

        self.prior_builder = BayesianPriorBuilder(config)
        self.sampling_engine = BayesianSamplingEngine(config)

        self.logger.info("BayesianEngineAdapter initialized")

    def is_available(self) -> bool:
        """Check if all components are available"""
        return (
            self.prior_builder is not None
            and self.sampling_engine is not None
        )

    def get_component_status(self) -> dict[str, str]:
        """Get status of all components"""
        return {
            'prior_builder': '✓ disponible' if self.prior_builder else '✗ no disponible',
            'sampling_engine': '✓ disponible' if self.sampling_engine else '✗ no disponible',
        }

    def test_necessity_from_observations(
        self,
        observations: list[float],
        prior: dict[str, float]
    ) -> dict[str, Any]:
        """
        Necessity test with Bayesian inference

        Args:
            observations: List of binary observations (0/1)
            prior: Prior parameters {'alpha': float, 'beta': float}

        Returns:
            Posterior statistics and diagnostics
        """
        with pm.Model() as model:
            # Beta prior for success probability
            theta = pm.Beta(
                'theta',
                alpha=prior.get('alpha', 1.0),
                beta=prior.get('beta', 1.0)
            )

            # Binomial likelihood
            y = pm.Binomial(
                'y',
                n=len(observations),
                p=theta,
                observed=sum(observations)
            )

            # Sample posterior
            trace = pm.sample(
                2000,
                return_inferencedata=True,
                progressbar=False,
                random_seed=42
            )

        # Extract diagnostics
        posterior_mean = float(trace.posterior['theta'].mean().item())
        hdi = az.hdi(trace, hdi_prob=0.95)['theta'].values
        rhat = float(az.rhat(trace)['theta'].item())

        return {
            'posterior_mean': posterior_mean,
            'hdi_95': (float(hdi[0]), float(hdi[1])),
            'rhat': rhat,
            'converged': rhat < 1.05,
            'n_observations': len(observations),
            'n_successes': sum(observations),
        }

    def update_prior_with_evidence(
        self,
        prior_alpha: float,
        prior_beta: float,
        evidence_count: int,
        success_count: int
    ) -> dict[str, float]:
        """
        Bayesian update with Beta-Binomial conjugacy

        Args:
            prior_alpha: Prior alpha parameter
            prior_beta: Prior beta parameter
            evidence_count: Total number of observations
            success_count: Number of successes

        Returns:
            Posterior parameters
        """
        posterior_alpha = prior_alpha + success_count
        posterior_beta = prior_beta + (evidence_count - success_count)

        return {
            'alpha': posterior_alpha,
            'beta': posterior_beta,
            'mean': posterior_alpha / (posterior_alpha + posterior_beta),
            'mode': (posterior_alpha - 1) / (posterior_alpha + posterior_beta - 2)
                    if posterior_alpha > 1 and posterior_beta > 1 else None,
        }
```

**Step 3**: Implement `bayesian_prior_builder.py`
```python
# src/farfan_pipeline/inference/bayesian_prior_builder.py

"""
Bayesian Prior Builder (AGUJA I)
Adaptive prior construction based on evidence strength
"""

from typing import Any
import numpy as np

class BayesianPriorBuilder:
    """Constructs adaptive Bayesian priors based on evidence characteristics"""

    def __init__(self, config: Any):
        self.config = config
        self.default_alpha = config.get('bayesian_thresholds', {}).get('prior_alpha', 1.0)
        self.default_beta = config.get('bayesian_thresholds', {}).get('prior_beta', 1.0)

    def build_prior_for_evidence_type(
        self,
        evidence_type: str,
        rarity: float = 0.5
    ) -> dict[str, float]:
        """
        Build prior based on evidence type and rarity

        Args:
            evidence_type: One of ['straw_in_wind', 'hoop', 'smoking_gun', 'doubly_decisive']
            rarity: Evidence rarity (0=common, 1=rare)

        Returns:
            Prior parameters {'alpha': float, 'beta': float}
        """
        # Beach's test-specific priors
        base_priors = {
            'straw_in_wind': {'alpha': 1.5, 'beta': 1.5},  # Weakly informative
            'hoop': {'alpha': 2.0, 'beta': 1.0},  # Favor necessity
            'smoking_gun': {'alpha': 1.0, 'beta': 2.0},  # Favor sufficiency
            'doubly_decisive': {'alpha': 3.0, 'beta': 3.0},  # Strong prior
        }

        prior = base_priors.get(evidence_type, {'alpha': self.default_alpha, 'beta': self.default_beta})

        # Adjust for rarity (rare evidence = stronger prior)
        prior['alpha'] *= (1 + rarity)
        prior['beta'] *= (1 + rarity)

        return prior

    def build_hierarchical_prior(
        self,
        group_sizes: list[int],
        overall_alpha: float = 2.0,
        overall_beta: float = 2.0
    ) -> dict[str, Any]:
        """
        Build hierarchical prior for multi-level analysis

        Args:
            group_sizes: Number of observations per group
            overall_alpha: Population-level alpha
            overall_beta: Population-level beta

        Returns:
            Hierarchical prior specification
        """
        n_groups = len(group_sizes)

        return {
            'population': {'alpha': overall_alpha, 'beta': overall_beta},
            'groups': [
                {
                    'alpha': overall_alpha / n_groups,
                    'beta': overall_beta / n_groups,
                    'n_obs': size
                }
                for size in group_sizes
            ]
        }
```

**Step 4**: Implement `bayesian_sampling_engine.py`
```python
# src/farfan_pipeline/inference/bayesian_sampling_engine.py

"""
Bayesian Sampling Engine (AGUJA II)
MCMC sampling with diagnostics and convergence checks
"""

from typing import Any
import pymc as pm
import arviz as az

class BayesianSamplingEngine:
    """Executes MCMC sampling with comprehensive diagnostics"""

    def __init__(self, config: Any):
        self.config = config
        self.n_samples = config.get('bayesian_thresholds', {}).get('mcmc_samples', 2000)
        self.n_chains = config.get('bayesian_thresholds', {}).get('mcmc_chains', 4)

    def sample_beta_binomial(
        self,
        n_successes: int,
        n_trials: int,
        prior_alpha: float = 1.0,
        prior_beta: float = 1.0
    ) -> dict[str, Any]:
        """
        Sample from Beta-Binomial model

        Args:
            n_successes: Number of successes
            n_trials: Total trials
            prior_alpha: Prior alpha
            prior_beta: Prior beta

        Returns:
            Posterior samples and diagnostics
        """
        with pm.Model() as model:
            theta = pm.Beta('theta', alpha=prior_alpha, beta=prior_beta)
            y = pm.Binomial('y', n=n_trials, p=theta, observed=n_successes)

            trace = pm.sample(
                self.n_samples,
                chains=self.n_chains,
                return_inferencedata=True,
                progressbar=False,
                random_seed=42
            )

        return self._extract_diagnostics(trace, 'theta')

    def _extract_diagnostics(self, trace: az.InferenceData, param: str) -> dict[str, Any]:
        """Extract comprehensive diagnostics from trace"""
        posterior = trace.posterior[param]

        return {
            'posterior_mean': float(posterior.mean().item()),
            'posterior_std': float(posterior.std().item()),
            'hdi_95': az.hdi(trace, hdi_prob=0.95)[param].values.tolist(),
            'rhat': float(az.rhat(trace)[param].item()),
            'ess': float(az.ess(trace)[param].item()),
            'converged': float(az.rhat(trace)[param].item()) < 1.05,
            'n_samples': self.n_samples,
            'n_chains': self.n_chains,
        }
```

**Step 5**: Update `__init__.py`
```python
# src/farfan_pipeline/inference/__init__.py

"""
Bayesian Inference Engine
Refactored Bayesian components (F1.2)
"""

from .bayesian_adapter import BayesianEngineAdapter
from .bayesian_prior_builder import BayesianPriorBuilder
from .bayesian_sampling_engine import BayesianSamplingEngine

__all__ = [
    'BayesianEngineAdapter',
    'BayesianPriorBuilder',
    'BayesianSamplingEngine',
]
```

**Validation**:
```bash
pytest tests/test_inference/
python -c "from farfan_pipeline.inference import BayesianEngineAdapter; print('OK')"
```

---

### ✅ Task 2.2: Install CausalNex (5-7 days)

**Step 1**: Add to requirements
```bash
# Add to requirements.txt:
causalnex>=0.12.0

# Install:
pip install causalnex>=0.12.0
```

**Step 2**: Create CausalNex integration
```python
# src/farfan_pipeline/methods/causal_structure_learning.py

"""
CausalNex Integration for Bayesian Network Structure Learning
"""

from typing import Any
import pandas as pd
import networkx as nx
from causalnex.structure import StructureModel
from causalnex.structure.notears import from_pandas
from causalnex.network import BayesianNetwork

class CausalStructureLearner:
    """Learn causal structure from policy data using NOTEARS algorithm"""

    def __init__(self, tabu_edges: list[tuple[str, str]] | None = None):
        self.tabu_edges = tabu_edges or []

    def learn_structure(
        self,
        data: pd.DataFrame,
        w_threshold: float = 0.3
    ) -> StructureModel:
        """
        Learn causal DAG structure from data

        Args:
            data: Policy data as DataFrame
            w_threshold: Edge weight threshold

        Returns:
            Learned structure model
        """
        sm = from_pandas(
            data,
            tabu_edges=self.tabu_edges,
            w_threshold=w_threshold
        )
        return sm
```

#### Data Requirements for CausalNex

CausalNex Bayesian Networks require **discrete features**. Continuous data must
be discretized before use:

```python
def _discretize_data(self, data: pd.DataFrame, n_bins: int = 5) -> pd.DataFrame:
    """Quantile-bin continuous columns for CausalNex compatibility."""
    discretized = data.copy()
    for col in data.select_dtypes(include=['float64', 'float32']).columns:
        discretized[col] = pd.qcut(
            data[col], q=n_bins, labels=False, duplicates='drop'
        )
    return discretized
```

Call this method before `from_pandas()` and before fitting/predicting.

```python
    def create_bayesian_network(
        self,
        structure: StructureModel,
        data: pd.DataFrame
    ) -> BayesianNetwork:
        """Create and fit Bayesian Network"""
        bn = BayesianNetwork(structure)
        bn = bn.fit_node_states(data)
        bn = bn.fit_cpds(data)
        return bn

    def predict_intervention_effect(
        self,
        bn: BayesianNetwork,
        data: pd.DataFrame,
        target_node: str,
        intervention: dict[str, Any]
    ) -> pd.Series:
        """
        Predict effect of intervention

        Args:
            bn: Fitted Bayesian Network
            data: Test data
            target_node: Node to predict
            intervention: Intervention values {'node': value}

        Returns:
            Predicted probabilities
        """
        # Apply intervention (do-calculus)
        intervened_data = data.copy()
        for node, value in intervention.items():
            intervened_data[node] = value

        predictions = bn.predict(intervened_data, target_node)
        return predictions
```

**Validation**:
```bash
pytest tests/test_causal_structure_learning.py
```

---

## Phase 3: Advanced Features (Month 2)

### ✅ Task 3.1: Add EconML (5-7 days)

**Step 1**: Install
```bash
# Add to requirements.txt:
econml>=0.15.0

pip install econml>=0.15.0
```

**Step 2**: Create impact evaluation module
```python
# src/farfan_pipeline/methods/policy_impact_evaluation.py

"""
EconML Integration for Heterogeneous Treatment Effect Estimation
"""

from typing import Any
import pandas as pd
import numpy as np
from econml.dml import DML
from sklearn.ensemble import RandomForestRegressor

class PolicyImpactEvaluator:
    """Estimate causal effects of policy interventions using EconML"""

    def __init__(self):
        self.dml_model = None

    def estimate_treatment_effect(
        self,
        Y: np.ndarray,
        T: np.ndarray,
        X: np.ndarray
    ) -> dict[str, Any]:
        """
        Estimate heterogeneous treatment effects

        Args:
            Y: Outcomes
            T: Treatment assignments
            X: Covariates

        Returns:
            Treatment effect estimates and confidence intervals
        """
        self.dml_model = DML(
            model_y=RandomForestRegressor(n_estimators=100, random_state=42),
            model_t=RandomForestRegressor(n_estimators=100, random_state=42),
            discrete_treatment=False
        )

        self.dml_model.fit(Y=Y, T=T, X=X)

        # Estimate effects
        treatment_effects = self.dml_model.effect(X)

        # Get confidence intervals
        lb, ub = self.dml_model.effect_interval(X, alpha=0.05)

        return {
            'treatment_effects': treatment_effects,
            'confidence_intervals': list(zip(lb, ub)),
            'mean_effect': float(np.mean(treatment_effects)),
            'std_effect': float(np.std(treatment_effects)),
        }
```

---

## Testing Checklist

### Unit Tests
- [ ] `tests/test_causal_inference_dowhy.py`
- [ ] `tests/test_inference/test_bayesian_adapter.py`
- [ ] `tests/test_inference/test_prior_builder.py`
- [ ] `tests/test_inference/test_sampling_engine.py`
- [ ] `tests/test_causal_structure_learning.py`
- [ ] `tests/test_policy_impact_evaluation.py`

### Integration Tests
- [ ] DoWhy integration with derek_beach.py
- [ ] Bayesian engine adapter with existing code
- [ ] CausalNex with policy data
- [ ] EconML with impact evaluation pipeline

### Validation Tests
- [ ] BGE-M3 embedding quality (semantic similarity benchmarks)
- [ ] DoWhy causal identification accuracy
- [ ] Bayesian convergence diagnostics (R-hat < 1.05)
- [ ] CausalNex structure learning validation

---

## Documentation Checklist

- [ ] Update `docs/ARCHITECTURE.md` with new modules
- [ ] Create `docs/CAUSAL_INFERENCE_GUIDE.md`
- [ ] Update `README.md` with new dependencies
- [ ] Add docstrings to all new functions
- [ ] Create usage examples for each new module

---

## Rollback Plan

If integration fails:

1. **Revert dependencies**:
   ```bash
   git checkout HEAD -- requirements.txt pyproject.toml
   pip install -r requirements.txt
   ```

2. **Remove new modules**:
   ```bash
   rm -rf src/farfan_pipeline/inference/
   rm src/farfan_pipeline/methods/causal_inference_dowhy.py
   rm src/farfan_pipeline/methods/causal_structure_learning.py
   rm src/farfan_pipeline/methods/policy_impact_evaluation.py
   ```

3. **Restore derek_beach.py**:
   ```bash
   git checkout HEAD -- src/farfan_pipeline/methods/derek_beach.py
   ```

---

**Last Updated**: 2026-01-07
**Next Review**: After Phase 1 completion

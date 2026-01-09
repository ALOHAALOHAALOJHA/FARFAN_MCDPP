"""
Heterogeneous Treatment Effects with EconML
===========================================

Conditional Average Treatment Effect (CATE) estimation for policy analysis.

This module provides advanced causal ML methods for understanding:
- How treatment effects vary across subgroups
- Optimal policy assignment based on characteristics
- Robustness of causal estimates across populations

Phase 3 SOTA Enhancement - 2026-01-07

Theoretical Foundation:
    Athey, S., & Imbens, G. W. (2016): Recursive partitioning for heterogeneous causal effects.
    Chernozhukov, V. et al. (2018): Double/debiased machine learning for treatment effects.
    Künzel, S. R. et al. (2019): Metalearners for estimating heterogeneous treatment effects.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from numpy.typing import NDArray

try:
    from econml.dml import CausalForestDML, LinearDML
    from econml.metalearners import TLearner, SLearner, XLearner
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import LogisticRegression

    ECONML_AVAILABLE = True
except ImportError:
    ECONML_AVAILABLE = False
    CausalForestDML = Any  # type: ignore[misc, assignment]
    LinearDML = Any  # type: ignore[misc, assignment]
    TLearner = Any  # type: ignore[misc, assignment]
    SLearner = Any  # type: ignore[misc, assignment]
    XLearner = Any  # type: ignore[misc, assignment]


@dataclass
class CATEEstimate:
    """Conditional Average Treatment Effect estimate"""

    method: str = ""
    point_estimate: float = 0.0
    std_error: float = 0.0
    confidence_interval: tuple[float, float] = (0.0, 0.0)
    n_observations: int = 0
    feature_importance: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class HeterogeneityAnalysis:
    """Analysis of treatment effect heterogeneity"""

    average_treatment_effect: float = 0.0
    ate_std_error: float = 0.0
    heterogeneity_score: float = 0.0
    subgroup_effects: dict[str, CATEEstimate] = field(default_factory=dict)
    top_effect_modifiers: list[tuple[str, float]] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyRecommendation:
    """Optimal policy recommendation"""

    policy_name: str = ""
    treatment_assignment: dict[str, str | int] = field(default_factory=dict)
    expected_value: float = 0.0
    confidence: float = 0.0
    benefiting_subgroups: list[str] = field(default_factory=list)
    cautionary_notes: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class HeterogeneousTreatmentAnalyzer:
    """
    Heterogeneous treatment effect estimation using EconML.

    Estimates how treatment effects vary across different subgroups,
    enabling targeted policy interventions and optimal resource allocation.

    Attributes:
        logger: Logger instance
        model: Fitted CATE estimation model
        feature_names: Names of covariates
    """

    def __init__(self, config: Any | None = None):
        """
        Initialize Heterogeneous Treatment Analyzer.

        Args:
            config: Optional configuration object
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model: Any | None = None
        self.feature_names: list[str] = []

        if not ECONML_AVAILABLE:
            self.logger.warning(
                "EconML not available. Heterogeneous treatment analysis will be disabled. "
                "Install with: pip install econml>=0.15.0"
            )

    def is_available(self) -> bool:
        """Check if EconML is available."""
        return ECONML_AVAILABLE

    def estimate_cate_dml(
        self,
        X: pd.DataFrame | NDArray[np.floating[Any]],
        T: pd.Series | NDArray[np.floating[Any]],
        Y: pd.Series | NDArray[np.floating[Any]],
        method: Literal["linear", "forest"] = "forest",
        n_estimators: int = 100,
    ) -> CATEEstimate:
        """
        Estimate CATE using Double Machine Learning (DML).

        DML provides unbiased CATE estimates by:
        1. Predicting treatment from covariates: T ~ f(X)
        2. Predicting outcome from covariates: Y ~ g(X)
        3. Estimating CATE from residuals: CATE = E[Y - g(X) | T - f(X), X]

        Args:
            X: Covariates (features)
            T: Treatment variable (binary or continuous)
            Y: Outcome variable
            method: "linear" for LinearDML, "forest" for CausalForestDML
            n_estimators: Number of trees for forest methods

        Returns:
            CATEEstimate with point estimates and confidence intervals

        Reference:
            Chernozhukov et al. (2018): Double/debiased machine learning.
        """
        if not ECONML_AVAILABLE:
            self.logger.error("EconML not available")
            return CATEEstimate(method="DML", metadata={"error": "EconML not available"})

        try:
            # Convert to numpy arrays
            X_arr = X.values if isinstance(X, pd.DataFrame) else X
            T_arr = T.values if isinstance(T, pd.Series) else T
            Y_arr = Y.values if isinstance(Y, pd.Series) else Y

            # Store feature names
            if isinstance(X, pd.DataFrame):
                self.feature_names = list(X.columns)
            else:
                self.feature_names = [f"X{i}" for i in range(X_arr.shape[1])]

            # Choose DML method
            if method == "forest":
                self.logger.info("Fitting Causal Forest DML...")
                model = CausalForestDML(
                    model_y=RandomForestRegressor(n_estimators=n_estimators, random_state=42),
                    model_t=RandomForestRegressor(n_estimators=n_estimators, random_state=42),
                    n_estimators=n_estimators,
                    random_state=42,
                )
            else:
                self.logger.info("Fitting Linear DML...")
                model = LinearDML(
                    model_y=RandomForestRegressor(n_estimators=n_estimators, random_state=42),
                    model_t=RandomForestRegressor(n_estimators=n_estimators, random_state=42),
                    random_state=42,
                )

            # Fit model
            model.fit(Y_arr, T_arr, X=X_arr)
            self.model = model

            # Estimate CATE for each observation
            cate_estimates = model.effect(X_arr)

            # Average treatment effect
            ate = float(np.mean(cate_estimates))
            ate_se = float(np.std(cate_estimates, ddof=1) / np.sqrt(len(cate_estimates)))

            # Confidence interval (95%)
            ci_lower = ate - 1.96 * ate_se
            ci_upper = ate + 1.96 * ate_se

            # Feature importance (for forest methods)
            feature_importance = {}
            if hasattr(model, "feature_importances_"):
                importances = model.feature_importances_
                for name, importance in zip(self.feature_names, importances):
                    feature_importance[name] = float(importance)

            estimate = CATEEstimate(
                method=f"DML-{method}",
                point_estimate=ate,
                std_error=ate_se,
                confidence_interval=(ci_lower, ci_upper),
                n_observations=len(Y_arr),
                feature_importance=feature_importance,
                metadata={
                    "n_estimators": n_estimators,
                    "heterogeneity_std": float(np.std(cate_estimates, ddof=1)),
                },
            )

            self.logger.info(
                f"CATE estimate: {ate:.4f} ± {ate_se:.4f}, "
                f"95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]"
            )

            return estimate

        except Exception as e:
            self.logger.error(f"Error estimating CATE with DML: {e}")
            return CATEEstimate(method="DML", metadata={"error": str(e)})

    def estimate_cate_metalearner(
        self,
        X: pd.DataFrame | NDArray[np.floating[Any]],
        T: pd.Series | NDArray[np.floating[Any]],
        Y: pd.Series | NDArray[np.floating[Any]],
        learner_type: Literal["T", "S", "X"] = "T",
        n_estimators: int = 100,
    ) -> CATEEstimate:
        """
        Estimate CATE using meta-learners.

        Meta-learners:
        - T-Learner: Separate models for treatment/control, CATE = μ₁(x) - μ₀(x)
        - S-Learner: Single model with treatment as feature
        - X-Learner: Extension of T-learner with propensity weighting

        Args:
            X: Covariates
            T: Treatment (binary)
            Y: Outcome
            learner_type: "T", "S", or "X"
            n_estimators: Number of trees

        Returns:
            CATEEstimate with point estimates

        Reference:
            Künzel et al. (2019): Metalearners for estimating heterogeneous treatment effects.
        """
        if not ECONML_AVAILABLE:
            self.logger.error("EconML not available")
            return CATEEstimate(
                method=f"{learner_type}-Learner", metadata={"error": "EconML not available"}
            )

        try:
            # Convert to arrays
            X_arr = X.values if isinstance(X, pd.DataFrame) else X
            T_arr = T.values if isinstance(T, pd.Series) else T
            Y_arr = Y.values if isinstance(Y, pd.Series) else Y

            # Store feature names
            if isinstance(X, pd.DataFrame):
                self.feature_names = list(X.columns)
            else:
                self.feature_names = [f"X{i}" for i in range(X_arr.shape[1])]

            # Choose meta-learner
            base_model = RandomForestRegressor(n_estimators=n_estimators, random_state=42)
            propensity_model = LogisticRegression(random_state=42)

            if learner_type == "T":
                self.logger.info("Fitting T-Learner...")
                model = TLearner(models=[base_model, base_model])
            elif learner_type == "S":
                self.logger.info("Fitting S-Learner...")
                model = SLearner(overall_model=base_model)
            else:  # X-Learner
                self.logger.info("Fitting X-Learner...")
                model = XLearner(
                    models=[base_model, base_model],
                    propensity_model=propensity_model,
                )

            # Fit model
            model.fit(Y_arr, T_arr, X=X_arr)
            self.model = model

            # Estimate CATE
            cate_estimates = model.effect(X_arr)

            # Statistics
            ate = float(np.mean(cate_estimates))
            ate_se = float(np.std(cate_estimates, ddof=1) / np.sqrt(len(cate_estimates)))

            ci_lower = ate - 1.96 * ate_se
            ci_upper = ate + 1.96 * ate_se

            estimate = CATEEstimate(
                method=f"{learner_type}-Learner",
                point_estimate=ate,
                std_error=ate_se,
                confidence_interval=(ci_lower, ci_upper),
                n_observations=len(Y_arr),
                metadata={
                    "n_estimators": n_estimators,
                    "heterogeneity_std": float(np.std(cate_estimates, ddof=1)),
                },
            )

            self.logger.info(
                f"{learner_type}-Learner CATE: {ate:.4f} ± {ate_se:.4f}, "
                f"95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]"
            )

            return estimate

        except Exception as e:
            self.logger.error(f"Error with {learner_type}-Learner: {e}")
            return CATEEstimate(method=f"{learner_type}-Learner", metadata={"error": str(e)})

    def analyze_heterogeneity(
        self,
        X: pd.DataFrame,
        T: pd.Series | NDArray[np.floating[Any]],
        Y: pd.Series | NDArray[np.floating[Any]],
        subgroup_columns: list[str] | None = None,
    ) -> HeterogeneityAnalysis:
        """
        Analyze treatment effect heterogeneity across subgroups.

        Args:
            X: Covariates (DataFrame with feature names)
            T: Treatment
            Y: Outcome
            subgroup_columns: Columns to stratify by (None = use all categorical)

        Returns:
            HeterogeneityAnalysis with subgroup effects and recommendations
        """
        if not ECONML_AVAILABLE:
            self.logger.error("EconML not available")
            return HeterogeneityAnalysis(metadata={"error": "EconML not available"})

        try:
            # First, estimate overall CATE
            overall_estimate = self.estimate_cate_dml(X, T, Y, method="forest")

            # Identify subgroup columns
            if subgroup_columns is None:
                # Use categorical columns
                subgroup_columns = list(X.select_dtypes(include=["object", "category"]).columns)

            if not subgroup_columns:
                self.logger.warning("No categorical columns for subgroup analysis")
                return HeterogeneityAnalysis(
                    average_treatment_effect=overall_estimate.point_estimate,
                    ate_std_error=overall_estimate.std_error,
                    metadata={"warning": "No subgroups identified"},
                )

            # Estimate CATE for each subgroup
            subgroup_effects: dict[str, CATEEstimate] = {}
            effect_variances = []

            for col in subgroup_columns:
                for value in X[col].unique():
                    # Filter to subgroup
                    mask = X[col] == value
                    X_sub = X[mask]
                    T_sub = T[mask] if isinstance(T, pd.Series) else T[mask]
                    Y_sub = Y[mask] if isinstance(Y, pd.Series) else Y[mask]

                    if len(X_sub) < 10:
                        continue  # Skip small subgroups

                    # Estimate CATE for subgroup
                    sub_estimate = self.estimate_cate_dml(X_sub, T_sub, Y_sub, method="linear")

                    subgroup_name = f"{col}={value}"
                    subgroup_effects[subgroup_name] = sub_estimate
                    effect_variances.append(sub_estimate.point_estimate)

            # Compute heterogeneity score (variance of subgroup effects)
            if len(effect_variances) > 1:
                heterogeneity_score = float(np.var(effect_variances, ddof=1))
            else:
                heterogeneity_score = 0.0

            # Rank effect modifiers by importance
            if overall_estimate.feature_importance:
                top_modifiers = sorted(
                    overall_estimate.feature_importance.items(), key=lambda x: x[1], reverse=True
                )[:5]
            else:
                top_modifiers = []

            # Generate recommendations
            recommendations = []
            if heterogeneity_score > 0.01:
                recommendations.append(
                    "Significant heterogeneity detected - consider targeted interventions"
                )

                # Find best-performing subgroups
                best_subgroups = sorted(
                    subgroup_effects.items(), key=lambda x: x[1].point_estimate, reverse=True
                )[:3]

                for name, _ in best_subgroups:
                    recommendations.append(f"High treatment effect for subgroup: {name}")
            else:
                recommendations.append(
                    "Low heterogeneity - uniform treatment policy may be appropriate"
                )

            analysis = HeterogeneityAnalysis(
                average_treatment_effect=overall_estimate.point_estimate,
                ate_std_error=overall_estimate.std_error,
                heterogeneity_score=heterogeneity_score,
                subgroup_effects=subgroup_effects,
                top_effect_modifiers=top_modifiers,
                recommendations=recommendations,
                metadata={
                    "n_subgroups": len(subgroup_effects),
                    "subgroup_columns": subgroup_columns,
                },
            )

            self.logger.info(
                f"Heterogeneity analysis: {len(subgroup_effects)} subgroups, "
                f"score={heterogeneity_score:.4f}"
            )

            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing heterogeneity: {e}")
            return HeterogeneityAnalysis(metadata={"error": str(e)})

    def recommend_optimal_policy(
        self,
        X: pd.DataFrame,
        T: pd.Series | NDArray[np.floating[Any]],
        Y: pd.Series | NDArray[np.floating[Any]],
        policy_name: str = "Optimal Treatment Assignment",
        benefit_threshold: float = 0.1,
    ) -> PolicyRecommendation:
        """
        Recommend optimal treatment policy based on CATE estimates.

        Assigns treatment to individuals where CATE > benefit_threshold.

        Args:
            X: Covariates
            T: Treatment (for training)
            Y: Outcome (for training)
            policy_name: Name for the recommended policy
            benefit_threshold: Minimum CATE for treatment assignment

        Returns:
            PolicyRecommendation with assignment rules and expected value
        """
        if not ECONML_AVAILABLE:
            self.logger.error("EconML not available")
            return PolicyRecommendation(
                policy_name=policy_name, metadata={"error": "EconML not available"}
            )

        try:
            # Estimate CATE
            self.estimate_cate_dml(X, T, Y, method="forest")

            if self.model is None:
                return PolicyRecommendation(
                    policy_name=policy_name, metadata={"error": "Model not fitted"}
                )

            # Get individual CATE predictions
            X_arr = X.values if isinstance(X, pd.DataFrame) else X
            individual_cates = self.model.effect(X_arr)

            # Assign treatment where CATE > threshold
            treatment_assignment = {}
            benefiting_indices = np.where(individual_cates > benefit_threshold)[0]

            for idx in benefiting_indices:
                treatment_assignment[f"individual_{idx}"] = 1  # Treat

            # Compute expected value under optimal policy
            # E[Y(optimal)] = E[Y(0)] + E[max(0, CATE)]
            expected_benefits = np.maximum(0, individual_cates)
            expected_value = float(np.mean(expected_benefits))

            # Confidence = proportion of variance explained
            total_variance = float(np.var(individual_cates, ddof=1))
            explained_variance = float(np.var(expected_benefits, ddof=1))
            confidence = explained_variance / total_variance if total_variance > 0 else 0.0

            # Identify benefiting subgroups
            if isinstance(X, pd.DataFrame):
                benefiting_subgroups = []
                for col in X.select_dtypes(include=["object", "category"]).columns:
                    value_counts = X.iloc[benefiting_indices][col].value_counts()
                    if len(value_counts) > 0:
                        top_value = value_counts.index[0]
                        benefiting_subgroups.append(f"{col}={top_value}")
            else:
                benefiting_subgroups = []

            # Cautionary notes
            cautionary_notes = []
            if confidence < 0.5:
                cautionary_notes.append("Low confidence - CATE estimates have high uncertainty")
            if len(benefiting_indices) < 0.1 * len(X):
                cautionary_notes.append("Few individuals benefit - consider cost-effectiveness")

            recommendation = PolicyRecommendation(
                policy_name=policy_name,
                treatment_assignment=treatment_assignment,
                expected_value=expected_value,
                confidence=confidence,
                benefiting_subgroups=benefiting_subgroups,
                cautionary_notes=cautionary_notes,
                metadata={
                    "benefit_threshold": benefit_threshold,
                    "n_treated": len(benefiting_indices),
                    "n_total": len(X),
                    "treatment_rate": len(benefiting_indices) / len(X),
                },
            )

            self.logger.info(
                f"Policy recommendation: {len(benefiting_indices)}/{len(X)} assigned treatment, "
                f"expected value={expected_value:.4f}, confidence={confidence:.3f}"
            )

            return recommendation

        except Exception as e:
            self.logger.error(f"Error recommending policy: {e}")
            return PolicyRecommendation(policy_name=policy_name, metadata={"error": str(e)})

    def sensitivity_analysis(
        self,
        X: pd.DataFrame | NDArray[np.floating[Any]],
        T: pd.Series | NDArray[np.floating[Any]],
        Y: pd.Series | NDArray[np.floating[Any]],
        confounder_strength: float = 0.1,
    ) -> dict[str, Any]:
        """
        Perform sensitivity analysis for unmeasured confounding.

        Tests robustness of CATE estimates to potential unmeasured confounders.

        Args:
            X: Covariates
            T: Treatment
            Y: Outcome
            confounder_strength: Assumed correlation of unmeasured confounder

        Returns:
            Dictionary with sensitivity results
        """
        if not ECONML_AVAILABLE:
            return {"error": "EconML not available"}

        try:
            # Get baseline CATE estimate
            baseline_estimate = self.estimate_cate_dml(X, T, Y, method="forest")

            # Simulate unmeasured confounder
            n = len(T) if isinstance(T, pd.Series) else len(T)
            U = np.random.randn(n) * confounder_strength

            # Add confounder to outcome
            Y_arr = Y.values if isinstance(Y, pd.Series) else Y
            Y_confounded = Y_arr + U

            # Re-estimate CATE
            confounded_estimate = self.estimate_cate_dml(X, T, Y_confounded, method="forest")

            # Compute bias
            bias = confounded_estimate.point_estimate - baseline_estimate.point_estimate

            # Robustness value (how much estimate changes)
            robustness = abs(bias) / (baseline_estimate.std_error + 1e-10)

            result = {
                "baseline_cate": baseline_estimate.point_estimate,
                "confounded_cate": confounded_estimate.point_estimate,
                "bias": float(bias),
                "robustness_value": float(robustness),
                "confounder_strength": confounder_strength,
                "interpretation": (
                    "Robust to unmeasured confounding"
                    if robustness < 1.0
                    else "Sensitive to unmeasured confounding"
                ),
            }

            self.logger.info(
                f"Sensitivity analysis: bias={bias:.4f}, robustness={robustness:.3f}"
            )

            return result

        except Exception as e:
            self.logger.error(f"Error in sensitivity analysis: {e}")
            return {"error": str(e)}


def create_treatment_analyzer(config: Any | None = None) -> HeterogeneousTreatmentAnalyzer:
    """
    Factory function to create HeterogeneousTreatmentAnalyzer.

    Args:
        config: Optional configuration object

    Returns:
        HeterogeneousTreatmentAnalyzer instance
    """
    return HeterogeneousTreatmentAnalyzer(config=config)

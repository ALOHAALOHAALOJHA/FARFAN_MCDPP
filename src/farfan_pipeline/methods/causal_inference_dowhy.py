"""
DoWhy Integration for Causal Inference
======================================

Enhances derek_beach.py with formal causal identification using Microsoft's DoWhy library.

This module provides:
- Formal causal effect identification using do-calculus (Pearl 2009)
- Backdoor and instrumental variable identification
- Refutation tests for robustness checking
- Integration with existing NetworkX causal graphs

Theoretical Foundation:
- Pearl, J. (2009). Causality: Models, Reasoning, and Inference (2nd ed.)
- Beach, D. (2017). Process-Tracing Methods in Social Science
- Sharma, A., & Kiciman, E. (2020). DoWhy: An End-to-End Library for Causal Inference

Phase 1 SOTA Enhancement - 2026-01-07
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import networkx as nx
import pandas as pd

if TYPE_CHECKING:
    from collections.abc import Sequence

try:
    from dowhy import CausalModel

    DOWHY_AVAILABLE = True
except ImportError:
    DOWHY_AVAILABLE = False
    # Define stub types for type checking
    CausalModel = Any  # type: ignore[misc, assignment]


@dataclass
class CausalAnalysisResult:
    """Results from DoWhy causal analysis"""

    identified: bool = False
    estimand: Any = None
    backdoor_variables: list[str] = field(default_factory=list)
    instrumental_variables: list[str] = field(default_factory=list)
    frontdoor_variables: list[str] = field(default_factory=list)
    identification_status: str = "unidentified"
    warnings: list[str] = field(default_factory=list)


@dataclass
class CausalEffectEstimate:
    """Results from causal effect estimation"""

    value: float = 0.0
    confidence_interval: tuple[float, float] = (0.0, 0.0)
    standard_error: float = 0.0
    method: str = ""
    identified: bool = False
    warnings: list[str] = field(default_factory=list)


@dataclass
class RefutationResult:
    """Results from refutation tests"""

    method: str = ""
    refuted: bool = False
    p_value: float | None = None
    new_effect: float | None = None
    original_effect: float | None = None
    summary: str = ""
    passed: bool = True


class DoWhyCausalAnalyzer:
    """
    DoWhy integration wrapper for causal inference operations.

    Provides formal causal identification and estimation using Pearl's do-calculus,
    integrated with existing NetworkX causal graphs from derek_beach.py.

    Usage:
        analyzer = DoWhyCausalAnalyzer(causal_graph)
        result = analyzer.identify_effect(data, treatment='intervention', outcome='resultado')
        if result.identified:
            estimate = analyzer.estimate_effect(data, treatment='intervention', outcome='resultado')
    """

    def __init__(self, causal_graph: nx.DiGraph | None = None):
        """
        Initialize DoWhy analyzer.

        Args:
            causal_graph: NetworkX directed graph representing causal structure
        """
        self.graph = causal_graph or nx.DiGraph()
        self.logger = logging.getLogger(self.__class__.__name__)

        if not DOWHY_AVAILABLE:
            self.logger.warning(
                "DoWhy library not available. Causal identification will be limited. "
                "Install with: pip install dowhy>=0.11.1"
            )

    def is_available(self) -> bool:
        """Check if DoWhy is available for use."""
        return DOWHY_AVAILABLE

    def identify_effect(
        self,
        data: pd.DataFrame,
        treatment: str,
        outcome: str,
        common_causes: list[str] | None = None,
        instruments: list[str] | None = None,
    ) -> CausalAnalysisResult:
        """
        Identify causal effect using do-calculus.

        Applies Pearl's identification criteria to determine if causal effect
        can be estimated from observational data.

        Args:
            data: Policy data as DataFrame
            treatment: Treatment variable (e.g., 'intervencion')
            outcome: Outcome variable (e.g., 'resultado')
            common_causes: List of common causes (confounders)
            instruments: List of instrumental variables

        Returns:
            CausalAnalysisResult with identification status and identified variables

        Raises:
            ValueError: If treatment or outcome not in data
            RuntimeError: If DoWhy is not available
        """
        if not DOWHY_AVAILABLE:
            self.logger.error("DoWhy not available for causal identification")
            return CausalAnalysisResult(
                identified=False,
                identification_status="dowhy_unavailable",
                warnings=["DoWhy library not installed"],
            )

        # Validate inputs
        if treatment not in data.columns:
            raise ValueError(f"Treatment variable '{treatment}' not found in data")
        if outcome not in data.columns:
            raise ValueError(f"Outcome variable '{outcome}' not found in data")

        try:
            # Create DoWhy causal model
            model = CausalModel(
                data=data,
                treatment=treatment,
                outcome=outcome,
                graph=self._get_dowhy_compatible_graph(self.graph),
                common_causes=common_causes,
                instruments=instruments,
            )

            # Identify causal effect
            identified_estimand = model.identify_effect(proceed_when_unidentifiable=True)

            # Extract identification results
            if identified_estimand is None:
                return CausalAnalysisResult(
                    identified=False,
                    identification_status="unidentified",
                    warnings=["Causal effect could not be identified from the graph"],
                )

            # Parse backdoor variables
            backdoor_vars = []
            if hasattr(identified_estimand, "backdoor_variables"):
                backdoor_vars = list(identified_estimand.backdoor_variables or [])

            # Parse instrumental variables
            instrumental_vars = []
            if hasattr(identified_estimand, "instrumental_variables"):
                instrumental_vars = list(identified_estimand.instrumental_variables or [])

            # Parse frontdoor variables
            frontdoor_vars = []
            if hasattr(identified_estimand, "frontdoor_variables"):
                frontdoor_vars = list(identified_estimand.frontdoor_variables or [])

            # Determine identification status
            if backdoor_vars or instrumental_vars or frontdoor_vars:
                status = "identified"
                identified = True
            else:
                status = "unidentified"
                identified = False

            self.logger.info(
                f"Causal identification for {treatment}->{outcome}: {status}"
                f" (backdoor: {len(backdoor_vars)}, IV: {len(instrumental_vars)})"
            )

            return CausalAnalysisResult(
                identified=identified,
                estimand=identified_estimand,
                backdoor_variables=backdoor_vars,
                instrumental_variables=instrumental_vars,
                frontdoor_variables=frontdoor_vars,
                identification_status=status,
            )

        except Exception as e:
            self.logger.error(f"Error during causal identification: {e}")
            return CausalAnalysisResult(
                identified=False,
                identification_status="error",
                warnings=[f"Identification error: {str(e)}"],
            )

    def estimate_effect(
        self,
        data: pd.DataFrame,
        treatment: str,
        outcome: str,
        method: str = "backdoor.linear_regression",
        common_causes: list[str] | None = None,
    ) -> CausalEffectEstimate:
        """
        Estimate causal effect with specified method.

        Available methods:
        - backdoor.linear_regression: Linear regression with backdoor adjustment
        - backdoor.propensity_score_matching: PSM with backdoor adjustment
        - iv.instrumental_variable: Two-stage least squares
        - frontdoor.adjustment: Frontdoor criterion

        Args:
            data: Policy data as DataFrame
            treatment: Treatment variable
            outcome: Outcome variable
            method: Estimation method
            common_causes: List of confounders

        Returns:
            CausalEffectEstimate with point estimate and confidence interval

        Raises:
            ValueError: If treatment or outcome not in data
            RuntimeError: If DoWhy is not available
        """
        if not DOWHY_AVAILABLE:
            self.logger.error("DoWhy not available for causal estimation")
            return CausalEffectEstimate(
                value=0.0,
                confidence_interval=(0.0, 0.0),
                method=method,
                identified=False,
                warnings=["DoWhy library not installed"],
            )

        # Validate inputs
        if treatment not in data.columns:
            raise ValueError(f"Treatment variable '{treatment}' not found in data")
        if outcome not in data.columns:
            raise ValueError(f"Outcome variable '{outcome}' not found in data")

        try:
            # Create causal model
            model = CausalModel(
                data=data,
                treatment=treatment,
                outcome=outcome,
                graph=self._get_dowhy_compatible_graph(self.graph),
                common_causes=common_causes,
            )

            # Identify effect
            identified_estimand = model.identify_effect()

            if identified_estimand is None:
                self.logger.warning(f"Causal effect {treatment}->{outcome} could not be identified")
                return CausalEffectEstimate(
                    value=0.0,
                    confidence_interval=(0.0, 0.0),
                    method=method,
                    identified=False,
                    warnings=["Causal effect not identified"],
                )

            # Estimate effect
            estimate = model.estimate_effect(identified_estimand, method_name=method)

            # Extract results
            effect_value = float(estimate.value)
            stderr = float(getattr(estimate, "stderr", 0.0))
            ci_lower = effect_value - 1.96 * stderr
            ci_upper = effect_value + 1.96 * stderr

            self.logger.info(
                f"Estimated causal effect {treatment}->{outcome}: "
                f"{effect_value:.4f} (95% CI: [{ci_lower:.4f}, {ci_upper:.4f}])"
            )

            return CausalEffectEstimate(
                value=effect_value,
                confidence_interval=(ci_lower, ci_upper),
                standard_error=stderr,
                method=method,
                identified=True,
            )

        except Exception as e:
            self.logger.error(f"Error during causal estimation: {e}")
            return CausalEffectEstimate(
                value=0.0,
                confidence_interval=(0.0, 0.0),
                method=method,
                identified=False,
                warnings=[f"Estimation error: {str(e)}"],
            )

    def refute_estimate(
        self,
        data: pd.DataFrame,
        treatment: str,
        outcome: str,
        estimate: CausalEffectEstimate,
        methods: Sequence[str] | None = None,
    ) -> dict[str, RefutationResult]:
        """
        Refute causal estimate with robustness checks.

        Refutation methods test the validity of causal estimates by:
        - Replacing treatment with random variable (placebo test)
        - Adding random common cause (unobserved confounding test)
        - Using data subsets (stability test)

        Args:
            data: Policy data as DataFrame
            treatment: Treatment variable
            outcome: Outcome variable
            estimate: Previously computed causal estimate
            methods: List of refutation methods to apply

        Returns:
            Dictionary mapping method names to RefutationResult objects

        Available methods:
        - placebo_treatment_refuter: Replace treatment with random variable
        - random_common_cause: Add random confounder
        - data_subset_refuter: Test on data subsets
        """
        if not DOWHY_AVAILABLE:
            self.logger.error("DoWhy not available for refutation tests")
            return {}

        if methods is None:
            methods = [
                "placebo_treatment_refuter",
                "random_common_cause",
                "data_subset_refuter",
            ]

        # Create causal model (needed for refutation)
        try:
            model = CausalModel(
                data=data,
                treatment=treatment,
                outcome=outcome,
                graph=self._get_dowhy_compatible_graph(self.graph),
            )

            identified_estimand = model.identify_effect()
            if identified_estimand is None:
                self.logger.warning("Cannot refute: effect not identified")
                return {}

            # Re-estimate for refutation (DoWhy needs CausalEstimate object)
            dowhy_estimate = model.estimate_effect(identified_estimand, method_name=estimate.method)

        except Exception as e:
            self.logger.error(f"Error setting up refutation: {e}")
            return {}

        # Run refutation tests
        refutation_results: dict[str, RefutationResult] = {}

        for method in methods:
            try:
                refute = model.refute_estimate(
                    identified_estimand, dowhy_estimate, method_name=method
                )

                # Extract refutation results
                p_value = getattr(refute, "p_value", None)
                new_effect = getattr(refute, "new_effect", None)

                # Interpretation: refutation "passes" if new effect ≈ 0 for placebo
                # or effect is stable under perturbations
                passed = True
                if method == "placebo_treatment_refuter":
                    # For placebo, we want new_effect ≈ 0
                    passed = (
                        abs(new_effect) < abs(estimate.value) * 0.5
                        if new_effect is not None
                        else True
                    )
                elif p_value is not None:
                    # For other tests, high p-value = no refutation = passed
                    passed = p_value > 0.05

                refutation_results[method] = RefutationResult(
                    method=method,
                    refuted=not passed,
                    p_value=float(p_value) if p_value is not None else None,
                    new_effect=float(new_effect) if new_effect is not None else None,
                    original_effect=estimate.value,
                    summary=str(refute),
                    passed=passed,
                )

                self.logger.info(
                    f"Refutation {method}: "
                    f"{'PASSED' if passed else 'FAILED'} "
                    f"(p={p_value:.4f if p_value else 'N/A'})"
                )

            except Exception as e:
                self.logger.error(f"Error in refutation method {method}: {e}")
                refutation_results[method] = RefutationResult(
                    method=method,
                    refuted=False,
                    summary=f"Error: {str(e)}",
                    passed=False,
                )

        return refutation_results

    def _get_dowhy_compatible_graph(self, nx_graph: nx.DiGraph) -> nx.DiGraph:
        """
        Return NetworkX DiGraph for DoWhy consumption.

        DoWhy's CausalModel accepts NetworkX DiGraph objects directly via the
        graph= parameter. No format conversion is required.

        Args:
            nx_graph: Source causal graph as NetworkX DiGraph

        Returns:
            The same nx.DiGraph instance (pass-through for API consistency)

        Note:
            Previous implementation incorrectly produced a pseudo-DOT string format
            that DoWhy cannot parse. DoWhy supports: NetworkX DiGraph, GML string,
            or proper DOT format. Direct NetworkX pass-through is the recommended
            approach per DoWhy documentation.
        """
        return nx_graph

    def get_all_paths(self, source: str, target: str) -> list[list[str]]:
        """
        Find all causal paths from source to target.

        Args:
            source: Source node
            target: Target node

        Returns:
            List of paths (each path is a list of nodes)
        """
        try:
            return list(nx.all_simple_paths(self.graph, source, target))
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []

    def find_confounders(self, treatment: str, outcome: str) -> list[str]:
        """
        Find potential confounders (common causes) for treatment->outcome.

        A confounder is a node that has directed paths to both treatment and outcome.

        Args:
            treatment: Treatment variable
            outcome: Outcome variable

        Returns:
            List of potential confounders
        """
        confounders = []

        for node in self.graph.nodes():
            if node == treatment or node == outcome:
                continue

            # Check if node has paths to both treatment and outcome
            has_path_to_treatment = nx.has_path(self.graph, node, treatment)
            has_path_to_outcome = nx.has_path(self.graph, node, outcome)

            if has_path_to_treatment and has_path_to_outcome:
                confounders.append(node)

        return confounders

    def find_mediators(self, treatment: str, outcome: str) -> list[str]:
        """
        Find mediators on the causal path from treatment to outcome.

        A mediator lies on a directed path from treatment to outcome.

        Args:
            treatment: Treatment variable
            outcome: Outcome variable

        Returns:
            List of mediators
        """
        if not nx.has_path(self.graph, treatment, outcome):
            return []

        all_paths = list(nx.all_simple_paths(self.graph, treatment, outcome))
        mediators = set()

        for path in all_paths:
            # Add all intermediate nodes
            mediators.update(path[1:-1])

        return list(mediators)

    def visualize_causal_graph(self, filepath: str | None = None) -> None:
        """
        Visualize causal graph (requires matplotlib and graphviz).

        Args:
            filepath: Optional path to save visualization
        """
        try:
            import matplotlib.pyplot as plt

            pos = nx.spring_layout(self.graph, k=2, iterations=50)
            plt.figure(figsize=(12, 8))

            nx.draw(
                self.graph,
                pos,
                with_labels=True,
                node_color="lightblue",
                node_size=3000,
                font_size=10,
                font_weight="bold",
                arrows=True,
                arrowsize=20,
                edge_color="gray",
            )

            if filepath:
                plt.savefig(filepath, dpi=300, bbox_inches="tight")
                self.logger.info(f"Causal graph saved to {filepath}")
            else:
                plt.show()

        except ImportError:
            self.logger.warning("matplotlib not available for visualization")


# Convenience factory function
def create_dowhy_analyzer(causal_graph: nx.DiGraph | None = None) -> DoWhyCausalAnalyzer:
    """
    Factory function to create DoWhy analyzer.

    Args:
        causal_graph: Optional NetworkX causal graph

    Returns:
        Configured DoWhyCausalAnalyzer instance
    """
    return DoWhyCausalAnalyzer(causal_graph)

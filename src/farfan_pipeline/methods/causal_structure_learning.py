"""
Causal Structure Learning with CausalNex
=========================================

Bayesian Network structure learning for policy analysis.

This module provides automated causal discovery using:
- NOTEARS algorithm for structure learning
- Bayesian Network inference for what-if scenarios
- Integration with DoWhy for hybrid causal reasoning

Phase 2 SOTA Enhancement - 2026-01-07

Theoretical Foundation:
    Zheng et al. (2018): DAGs with NO TEARS: Continuous Optimization for Structure Learning.
    Pearl, J. (2009): Causality: Models, Reasoning and Inference (2nd ed.).
    Spirtes, P., Glymour, C., Scheines, R. (2000): Causation, Prediction, and Search.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from numpy.typing import NDArray

try:
    from causalnex.structure import StructureModel
    from causalnex.structure.notears import from_pandas
    from causalnex.network import BayesianNetwork
    from causalnex.inference import InferenceEngine

    CAUSALNEX_AVAILABLE = True
except ImportError:
    CAUSALNEX_AVAILABLE = False
    StructureModel = Any  # type: ignore[misc, assignment]
    BayesianNetwork = Any  # type: ignore[misc, assignment]
    InferenceEngine = Any  # type: ignore[misc, assignment]


@dataclass
class StructureLearningResult:
    """Results from structure learning"""

    structure: Any | None = None  # StructureModel
    n_nodes: int = 0
    n_edges: int = 0
    edge_list: list[tuple[str, str]] = field(default_factory=list)
    edge_weights: dict[tuple[str, str], float] = field(default_factory=dict)
    is_dag: bool = True
    cycles: list[list[str]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class InferenceResult:
    """Results from Bayesian Network inference"""

    query_variable: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)
    posterior_distribution: dict[Any, float] = field(default_factory=dict)
    map_estimate: Any | None = None
    entropy: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class WhatIfScenario:
    """What-if scenario analysis result"""

    scenario_name: str = ""
    interventions: dict[str, Any] = field(default_factory=dict)
    predictions: dict[str, dict[Any, float]] = field(default_factory=dict)
    causal_effects: dict[str, float] = field(default_factory=dict)
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class CausalStructureLearner:
    """
    Bayesian Network structure learning for causal discovery.

    Uses CausalNex's NOTEARS algorithm to learn DAG structures from data,
    then performs Bayesian inference for what-if scenario analysis.

    Attributes:
        logger: Logger instance
        structure_model: Learned causal structure (DAG)
        bayesian_network: Fitted Bayesian Network
        inference_engine: Inference engine for queries
    """

    def __init__(self, config: Any | None = None):
        """
        Initialize Causal Structure Learner.

        Args:
            config: Optional configuration object
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.structure_model: Any | None = None
        self.bayesian_network: Any | None = None
        self.inference_engine: Any | None = None

        if not CAUSALNEX_AVAILABLE:
            self.logger.warning(
                "CausalNex not available. Structure learning will be disabled. "
                "Install with: pip install causalnex>=0.12.0"
            )

    def is_available(self) -> bool:
        """Check if CausalNex is available."""
        return CAUSALNEX_AVAILABLE

    def learn_structure(
        self,
        data: pd.DataFrame,
        w_threshold: float = 0.3,
        max_iter: int = 100,
        tabu_edges: list[tuple[str, str]] | None = None,
        tabu_parent_nodes: list[str] | None = None,
        tabu_child_nodes: list[str] | None = None,
    ) -> StructureLearningResult:
        """
        Learn causal structure from data using NOTEARS algorithm.

        Args:
            data: DataFrame with observations (rows) and variables (columns)
            w_threshold: Threshold for edge weights (edges below this are removed)
            max_iter: Maximum iterations for NOTEARS optimization
            tabu_edges: List of forbidden edges (from, to)
            tabu_parent_nodes: Nodes that cannot be parents
            tabu_child_nodes: Nodes that cannot be children

        Returns:
            StructureLearningResult with learned DAG structure

        Notes:
            NOTEARS formulates structure learning as continuous optimization:
            min_{W} F(W) s.t. h(W) = 0
            where h(W) = tr(e^{W◦W}) - d = 0 enforces acyclicity
        """
        if not CAUSALNEX_AVAILABLE:
            self.logger.error("CausalNex not available for structure learning")
            return StructureLearningResult(metadata={"error": "CausalNex not available"})

        if data.empty:
            self.logger.warning("Empty dataset provided for structure learning")
            return StructureLearningResult(metadata={"error": "Empty dataset"})

        # Validation warnings
        warnings = []
        n_samples = len(data)
        if n_samples < 1000:
            warning_msg = (
                f"Sample size ({n_samples}) is below recommended minimum (1000). "
                f"Structure learning may be unreliable with small samples."
            )
            self.logger.warning(warning_msg)
            warnings.append(warning_msg)

        # Check for continuous variables (CausalNex Bayesian Networks expect discrete)
        continuous_cols = []
        for col in data.columns:
            if data[col].dtype in ['float64', 'float32', 'float16']:
                continuous_cols.append(col)

        if continuous_cols:
            warning_msg = (
                f"Continuous variables detected: {continuous_cols}. "
                f"CausalNex Bayesian Networks expect discrete variables. "
                f"Consider discretizing continuous features for BN inference."
            )
            self.logger.warning(warning_msg)
            warnings.append(warning_msg)

        try:
            # Learn structure using NOTEARS
            self.logger.info(
                f"Learning causal structure from {len(data)} observations, "
                f"{len(data.columns)} variables"
            )

            sm = from_pandas(
                data,
                w_threshold=w_threshold,
                max_iter=max_iter,
                tabu_edges=tabu_edges or [],
                tabu_parent_nodes=tabu_parent_nodes or [],
                tabu_child_nodes=tabu_child_nodes or [],
            )

            self.structure_model = sm

            # Extract structure information
            edge_list = list(sm.edges)
            n_nodes = len(sm.nodes)
            n_edges = len(edge_list)

            # Get edge weights
            edge_weights = {}
            for u, v in edge_list:
                weight = sm.get_edge_data(u, v).get("weight", 0.0)
                edge_weights[(u, v)] = float(weight)

            # Check for cycles (should not exist after NOTEARS)
            from networkx import simple_cycles

            cycles = list(simple_cycles(sm))
            is_dag = len(cycles) == 0

            result = StructureLearningResult(
                structure=sm,
                n_nodes=n_nodes,
                n_edges=n_edges,
                edge_list=edge_list,
                edge_weights=edge_weights,
                is_dag=is_dag,
                cycles=cycles,
                metadata={
                    "w_threshold": w_threshold,
                    "max_iter": max_iter,
                    "algorithm": "NOTEARS",
                    "warnings": warnings,
                    "n_samples": n_samples,
                },
            )

            self.logger.info(
                f"Learned DAG structure: {n_nodes} nodes, {n_edges} edges, "
                f"is_dag={is_dag}"
            )

            return result

        except Exception as e:
            self.logger.error(f"Error learning structure: {e}")
            return StructureLearningResult(metadata={"error": str(e)})

    def fit_bayesian_network(
        self,
        data: pd.DataFrame,
        structure: Any | None = None,
    ) -> bool:
        """
        Fit Bayesian Network from structure and data.

        Args:
            data: DataFrame with observations
            structure: Optional StructureModel (uses self.structure_model if None)

        Returns:
            True if successful, False otherwise

        Notes:
            Learns conditional probability distributions P(X|parents(X))
            for each node given the learned DAG structure.
        """
        if not CAUSALNEX_AVAILABLE:
            self.logger.error("CausalNex not available")
            return False

        if structure is None:
            structure = self.structure_model

        if structure is None:
            self.logger.error("No structure available. Run learn_structure() first.")
            return False

        if data.empty:
            self.logger.warning("Empty dataset for Bayesian Network fitting")
            return False

        try:
            # Create Bayesian Network from structure
            bn = BayesianNetwork(structure)

            # Fit CPDs from data
            bn.fit_node_states(data)
            bn.fit_cpds(data)

            self.bayesian_network = bn
            self.inference_engine = InferenceEngine(bn)

            self.logger.info(
                f"Fitted Bayesian Network with {len(bn.nodes)} nodes, "
                f"{len(bn.edges)} edges"
            )

            return True

        except Exception as e:
            self.logger.error(f"Error fitting Bayesian Network: {e}")
            return False

    def query_distribution(
        self,
        query_variable: str,
        evidence: dict[str, Any] | None = None,
    ) -> InferenceResult:
        """
        Query posterior distribution given evidence.

        Args:
            query_variable: Variable to query
            evidence: Dictionary of evidence {variable: value}

        Returns:
            InferenceResult with posterior distribution

        Example:
            >>> result = learner.query_distribution(
            ...     query_variable="policy_success",
            ...     evidence={"budget": "high", "stakeholder_support": "strong"}
            ... )
            >>> print(result.posterior_distribution)
            {'yes': 0.75, 'no': 0.25}
        """
        if not CAUSALNEX_AVAILABLE:
            self.logger.error("CausalNex not available")
            return InferenceResult(
                query_variable=query_variable,
                evidence=evidence or {},
                metadata={"error": "CausalNex not available"},
            )

        if self.inference_engine is None:
            self.logger.error("No inference engine. Run fit_bayesian_network() first.")
            return InferenceResult(
                query_variable=query_variable,
                evidence=evidence or {},
                metadata={"error": "No inference engine"},
            )

        try:
            # Query posterior distribution
            posterior = self.inference_engine.query()[query_variable]

            if evidence:
                # Update with evidence
                posterior = self.inference_engine.query(evidence)[query_variable]

            # Convert to dictionary
            posterior_dict = dict(posterior)

            # Get MAP estimate (most probable value)
            map_estimate = max(posterior_dict, key=posterior_dict.get)  # type: ignore[arg-type]

            # Compute entropy
            probs = np.array(list(posterior_dict.values()))
            entropy = float(-np.sum(probs * np.log2(probs + 1e-10)))

            result = InferenceResult(
                query_variable=query_variable,
                evidence=evidence or {},
                posterior_distribution=posterior_dict,
                map_estimate=map_estimate,
                entropy=entropy,
                metadata={"n_states": len(posterior_dict)},
            )

            self.logger.debug(
                f"Query {query_variable} | {evidence}: MAP={map_estimate}, "
                f"H={entropy:.3f}"
            )

            return result

        except Exception as e:
            self.logger.error(f"Error querying distribution: {e}")
            return InferenceResult(
                query_variable=query_variable,
                evidence=evidence or {},
                metadata={"error": str(e)},
            )

    def what_if_analysis(
        self,
        scenario_name: str,
        interventions: dict[str, Any],
        query_variables: list[str],
        baseline_evidence: dict[str, Any] | None = None,
    ) -> WhatIfScenario:
        """
        Perform what-if scenario analysis with interventions.

        Compares posterior distributions under interventions vs baseline.

        Args:
            scenario_name: Name for this scenario
            interventions: Dictionary of interventions {variable: value}
            query_variables: Variables to predict under intervention
            baseline_evidence: Baseline evidence (no intervention)

        Returns:
            WhatIfScenario with predictions and causal effects

        Example:
            >>> scenario = learner.what_if_analysis(
            ...     scenario_name="Increase Budget",
            ...     interventions={"budget": "high"},
            ...     query_variables=["policy_success", "stakeholder_satisfaction"],
            ...     baseline_evidence={"budget": "medium"}
            ... )
            >>> print(scenario.causal_effects)
            {'policy_success': 0.15, 'stakeholder_satisfaction': 0.10}
        """
        if not CAUSALNEX_AVAILABLE:
            self.logger.error("CausalNex not available")
            return WhatIfScenario(
                scenario_name=scenario_name,
                interventions=interventions,
                metadata={"error": "CausalNex not available"},
            )

        if self.inference_engine is None:
            self.logger.error("No inference engine. Run fit_bayesian_network() first.")
            return WhatIfScenario(
                scenario_name=scenario_name,
                interventions=interventions,
                metadata={"error": "No inference engine"},
            )

        if not query_variables:
            self.logger.warning("No query variables specified for what-if analysis")
            return WhatIfScenario(
                scenario_name=scenario_name,
                interventions=interventions,
                predictions={},
                causal_effects={},
                confidence=0.0,
                metadata={"warning": "No query variables specified"},
            )

        try:
            predictions: dict[str, dict[Any, float]] = {}
            causal_effects: dict[str, float] = {}

            # Get baseline distributions
            baseline_distributions = {}
            for var in query_variables:
                baseline_result = self.query_distribution(var, baseline_evidence)
                baseline_distributions[var] = baseline_result.posterior_distribution

            # Get intervention distributions
            # Merge baseline evidence with interventions (interventions override)
            intervention_evidence = {**(baseline_evidence or {}), **interventions}

            for var in query_variables:
                intervention_result = self.query_distribution(var, intervention_evidence)
                predictions[var] = intervention_result.posterior_distribution

                # Compute causal effect (difference in MAP probabilities)
                baseline_map_prob = max(baseline_distributions[var].values())
                intervention_map_prob = max(predictions[var].values())
                causal_effect = intervention_map_prob - baseline_map_prob
                causal_effects[var] = float(causal_effect)

            # Compute overall confidence (average entropy reduction)
            total_entropy_reduction = 0.0
            for var in query_variables:
                baseline_probs = np.array(list(baseline_distributions[var].values()))
                baseline_entropy = float(-np.sum(baseline_probs * np.log2(baseline_probs + 1e-10)))

                intervention_probs = np.array(list(predictions[var].values()))
                intervention_entropy = float(
                    -np.sum(intervention_probs * np.log2(intervention_probs + 1e-10))
                )

                entropy_reduction = baseline_entropy - intervention_entropy
                total_entropy_reduction += entropy_reduction

            avg_entropy_reduction = total_entropy_reduction / len(query_variables)
            confidence = float(np.clip(avg_entropy_reduction / 2.0, 0.0, 1.0))

            scenario = WhatIfScenario(
                scenario_name=scenario_name,
                interventions=interventions,
                predictions=predictions,
                causal_effects=causal_effects,
                confidence=confidence,
                metadata={
                    "baseline_evidence": baseline_evidence,
                    "n_query_variables": len(query_variables),
                    "avg_entropy_reduction": avg_entropy_reduction,
                },
            )

            self.logger.info(
                f"What-if scenario '{scenario_name}': "
                f"{len(query_variables)} predictions, confidence={confidence:.3f}"
            )

            return scenario

        except Exception as e:
            self.logger.error(f"Error in what-if analysis: {e}")
            return WhatIfScenario(
                scenario_name=scenario_name,
                interventions=interventions,
                metadata={"error": str(e)},
            )

    def find_causal_paths(
        self,
        source: str,
        target: str,
        max_paths: int = 10,
        max_path_length: int | None = None,
    ) -> list[list[str]]:
        """
        Find causal paths between nodes.
        
        Args:
            source: Starting node
            target: Ending node
            max_paths: Maximum number of paths to return
            max_path_length: Maximum path length (number of edges), None for unlimited
            
        Returns:
            List of paths, each path is a list of node names
        """
        if not self.structure_model:
            return []
        
        try:
            # Get all paths up to max_path_length
            all_paths = list(nx.all_simple_paths(
                self.structure_model,
                source,
                target,
                cutoff=max_path_length  # Limits LENGTH, not count
            ))
            
            # Then limit COUNT of returned paths
            result = all_paths[:max_paths]
            
            self.logger.debug(
                f"Found {len(all_paths)} total paths from {source} to {target}, "
                f"returning {len(result)}"
            )
            
            return result
        except nx.NetworkXError as e:
            self.logger.warning(f"Path finding failed: {e}")
            return []
            self.logger.error(f"Error finding causal paths: {e}")
            return []

    def find_markov_blanket(self, variable: str) -> list[str]:
        """
        Find Markov blanket of a variable.

        The Markov blanket includes:
        - Parents of the variable
        - Children of the variable
        - Other parents of the children (co-parents)

        Args:
            variable: Variable to find Markov blanket for

        Returns:
            List of variables in Markov blanket
        """
        if not CAUSALNEX_AVAILABLE or self.structure_model is None:
            return []

        try:
            sm = self.structure_model
            blanket = set()

            # Add parents
            parents = list(sm.predecessors(variable))
            blanket.update(parents)

            # Add children
            children = list(sm.successors(variable))
            blanket.update(children)

            # Add co-parents (other parents of children)
            for child in children:
                co_parents = list(sm.predecessors(child))
                blanket.update(co_parents)

            # Remove the variable itself
            blanket.discard(variable)

            result = list(blanket)
            self.logger.debug(f"Markov blanket of {variable}: {result}")
            return result

        except Exception as e:
            self.logger.error(f"Error finding Markov blanket: {e}")
            return []

    def export_structure_dot(self, output_path: str) -> bool:
        """
        Export structure as DOT file for visualization.

        Args:
            output_path: Path to save DOT file

        Returns:
            True if successful, False otherwise
        """
        if not CAUSALNEX_AVAILABLE or self.structure_model is None:
            return False

        try:
            from networkx.drawing.nx_pydot import write_dot

            write_dot(self.structure_model, output_path)
            self.logger.info(f"Structure exported to {output_path}")
            return True

        except ImportError:
            self.logger.warning("pydot not available for DOT export")
            return False
        except Exception as e:
            self.logger.error(f"Error exporting structure: {e}")
            return False

    def get_structure_summary(self) -> dict[str, Any]:
        """
        Get summary statistics for learned structure.

        Returns:
            Dictionary with summary statistics
        """
        if not CAUSALNEX_AVAILABLE or self.structure_model is None:
            return {"error": "No structure available"}

        try:
            sm = self.structure_model

            # Basic stats
            n_nodes = len(sm.nodes)
            n_edges = len(sm.edges)

            # Degree statistics
            in_degrees = dict(sm.in_degree())
            out_degrees = dict(sm.out_degree())

            # Handle empty graph case
            if n_nodes == 0 or not in_degrees:
                avg_in_degree = 0.0
                avg_out_degree = 0.0
            else:
                avg_in_degree = np.mean(list(in_degrees.values()))
                avg_out_degree = np.mean(list(out_degrees.values()))

            # Find root nodes (no parents)
            root_nodes = [node for node in sm.nodes if sm.in_degree(node) == 0]

            # Find leaf nodes (no children)
            leaf_nodes = [node for node in sm.nodes if sm.out_degree(node) == 0]

            # Find most connected nodes
            total_degrees = {node: in_degrees[node] + out_degrees[node] for node in sm.nodes}
            most_connected = sorted(total_degrees.items(), key=lambda x: x[1], reverse=True)[:5]

            return {
                "n_nodes": n_nodes,
                "n_edges": n_edges,
                "avg_in_degree": float(avg_in_degree),
                "avg_out_degree": float(avg_out_degree),
                "n_root_nodes": len(root_nodes),
                "n_leaf_nodes": len(leaf_nodes),
                "root_nodes": root_nodes,
                "leaf_nodes": leaf_nodes,
                "most_connected": most_connected,
                "density": float(n_edges / (n_nodes * (n_nodes - 1))) if n_nodes > 1 else 0.0,
            }

        except Exception as e:
            self.logger.error(f"Error getting structure summary: {e}")
            return {"error": str(e)}


def create_structure_learner(config: Any | None = None) -> CausalStructureLearner:
    """
    Factory function to create CausalStructureLearner.

    Args:
        config: Optional configuration object

    Returns:
        CausalStructureLearner instance
    """
    return CausalStructureLearner(config=config)

"""
Congruence Layer Evaluator (@C) for Method Ensembles

Implements the congruence layer evaluation for method ensembles as specified in
mathematical_foundations_capax_system.md Section 3.5.

Formula: C_play(G | ctx) = c_scale · c_sem · c_fusion

where:
- c_scale: Scale congruence (output range compatibility)
- c_sem: Semantic congruence (Jaccard index of semantic tags)
- c_fusion: Fusion validity (rule presence and input availability)

Special case: Single method ensembles return 1.0
"""

from typing import Any


class CongruenceLayerEvaluator:
    """
    Evaluates congruence (@C) for method ensembles.
    
    The congruence layer measures how well methods in a subgraph can work together,
    considering their output ranges, semantic compatibility, and fusion configuration.
    """
    
    def __init__(self, method_registry: dict[str, Any] | None = None) -> None:
        """
        Initialize the congruence evaluator.
        
        Args:
            method_registry: Dictionary mapping method_id to method metadata containing:
                - output_range: tuple[float, float] or list[float, float]
                - semantic_tags: set[str] or list[str]
        """
        self.method_registry = method_registry or {}
    
    def _compute_c_scale(self, method_ids: list[str]) -> float:
        """
        Compute scale congruence for method ensemble.
        
        Returns:
            1.0 if all output_range identical
            0.8 if all in [0,1] or convertible to [0,1]
            0.0 otherwise
        """
        if not method_ids:
            return 1.0
        
        if len(method_ids) == 1:
            return 1.0
        
        ranges = []
        for method_id in method_ids:
            method_info = self.method_registry.get(method_id, {})
            output_range = method_info.get("output_range")
            
            if output_range is None:
                return 0.0
            
            if isinstance(output_range, (list, tuple)) and len(output_range) == 2:
                ranges.append((float(output_range[0]), float(output_range[1])))
            else:
                return 0.0
        
        if not ranges:
            return 0.0
        
        first_range = ranges[0]
        all_identical = all(r == first_range for r in ranges)
        
        if all_identical:
            return 1.0
        
        all_convertible = all(
            (r[0] >= 0.0 and r[1] <= 1.0) or
            (r[0] == 0.0 and r[1] == 1.0)
            for r in ranges
        )
        
        if all_convertible:
            return 0.8
        
        return 0.0
    
    def _compute_c_sem(self, method_ids: list[str]) -> float:
        """
        Compute semantic congruence via Jaccard index.
        
        Returns: |intersection| / |union| of semantic_tags
        """
        if not method_ids:
            return 1.0
        
        if len(method_ids) == 1:
            return 1.0
        
        tag_sets = []
        for method_id in method_ids:
            method_info = self.method_registry.get(method_id, {})
            semantic_tags = method_info.get("semantic_tags", [])
            
            if isinstance(semantic_tags, set):
                tag_sets.append(semantic_tags)
            elif isinstance(semantic_tags, list):
                tag_sets.append(set(semantic_tags))
            else:
                tag_sets.append(set())
        
        if not tag_sets:
            return 0.0
        
        intersection = set.intersection(*tag_sets) if tag_sets else set()
        union = set.union(*tag_sets) if tag_sets else set()
        
        if len(union) == 0:
            return 0.0
        
        jaccard = len(intersection) / len(union)
        return float(jaccard)
    
    def _compute_c_fusion(
        self,
        fusion_rule: str | None,
        provided_inputs: set[str] | None,
        required_method_ids: list[str]
    ) -> float:
        """
        Compute fusion validity.
        
        Returns:
            1.0 if fusion_rule present AND all inputs provided
            0.5 if fusion_rule present BUT some inputs missing
            0.0 if fusion_rule not present
        """
        if fusion_rule is None or fusion_rule == "":
            return 0.0
        
        if provided_inputs is None:
            provided_inputs = set()
        
        if not required_method_ids:
            return 1.0
        
        required_set = set(required_method_ids)
        all_inputs_present = required_set.issubset(provided_inputs)
        
        if all_inputs_present:
            return 1.0
        
        some_inputs_present = len(required_set.intersection(provided_inputs)) > 0
        if some_inputs_present:
            return 0.5
        
        return 0.5
    
    def evaluate(
        self,
        method_ids: list[str],
        subgraph_id: str | None = None,
        fusion_rule: str | None = None,
        provided_inputs: set[str] | None = None
    ) -> float:
        """
        Evaluate congruence layer score for method ensemble.
        
        Args:
            method_ids: List of method IDs in the ensemble
            subgraph_id: Optional subgraph identifier (for tracing)
            fusion_rule: Fusion rule from Config (e.g., "TYPE_A", "weighted_average")
            provided_inputs: Set of method IDs whose inputs are available
        
        Returns:
            C_play score in [0.0, 1.0]
            
        Special cases:
            - Empty ensemble: returns 1.0
            - Single method: returns 1.0
            - Multi-method: returns c_scale · c_sem · c_fusion
        """
        if not method_ids:
            return 1.0
        
        if len(method_ids) == 1:
            method_id = method_ids[0]
            if method_id not in self.method_registry:
                return 1.0
            return 1.0
        
        c_scale = self._compute_c_scale(method_ids)
        c_sem = self._compute_c_sem(method_ids)
        c_fusion = self._compute_c_fusion(fusion_rule, provided_inputs, method_ids)
        
        c_play = c_scale * c_sem * c_fusion
        
        return c_play

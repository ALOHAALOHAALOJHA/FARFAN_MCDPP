"""
Phase 5 Mission Contract

Defines the mission and transformation logic for Phase 5.

Mission:
- Transform 60 DimensionScores into 10 AreaScores
- Preserve hermeticity (6 dimensions per area)
- Apply weighted averaging
- Validate all bounds and constraints

Module: src/farfan_pipeline/phases/Phase_05/contracts/phase5_mission_contract.py
"""
from __future__ import annotations

__version__ = "1.0.0"
__author__ = "F.A.R.F.A.N Core Team"

import logging
from typing import Any

logger = logging.getLogger(__name__)


class Phase5MissionContract:
    """
    Mission contract for Phase 5.
    
    Defines:
    - Topological order of operations
    - Weight resolution strategy
    - Hermeticity validation logic
    - Quality level assignment rules
    """

    # Topological order of operations
    TOPOLOGICAL_ORDER = [
        "validate_input",
        "group_by_area",
        "validate_hermeticity",
        "apply_weights",
        "compute_weighted_average",
        "clamp_bounds",
        "assign_quality_level",
        "propagate_uncertainty",
        "validate_output",
    ]

    # Default weights (equal weighting)
    DEFAULT_WEIGHTS = {
        f"DIM{i:02d}": 1.0 / 6 for i in range(1, 7)
    }

    # Quality thresholds (normalized 0-1)
    QUALITY_THRESHOLDS = {
        "EXCELENTE": 0.85,
        "BUENO": 0.70,
        "ACEPTABLE": 0.55,
        "INSUFICIENTE": 0.0,
    }

    @staticmethod
    def get_weights_for_area(
        area_id: str,
        monolith: dict[str, Any] | None = None,
    ) -> dict[str, float]:
        """
        Get dimension weights for a policy area.
        
        Args:
            area_id: Policy area identifier
            monolith: Questionnaire monolith (optional)
        
        Returns:
            Dict mapping dimension_id to weight
        """
        # TODO: Extract weights from monolith when available
        # For now, use equal weights
        return Phase5MissionContract.DEFAULT_WEIGHTS.copy()

    @staticmethod
    def validate_topological_order(executed_steps: list[str]) -> tuple[bool, str]:
        """
        Validate that operations followed topological order.
        
        Args:
            executed_steps: List of executed operation names
        
        Returns:
            Tuple of (is_valid, message)
        """
        expected = Phase5MissionContract.TOPOLOGICAL_ORDER
        
        # Check that all required steps were executed
        missing = set(expected) - set(executed_steps)
        if missing:
            return False, f"Missing required steps: {missing}"
        
        # Check order (allowing extra steps)
        expected_idx = {step: i for i, step in enumerate(expected)}
        executed_with_idx = [(step, expected_idx.get(step, -1)) for step in executed_steps]
        
        # Filter to only expected steps and check ordering
        filtered = [(step, idx) for step, idx in executed_with_idx if idx >= 0]
        for i in range(len(filtered) - 1):
            if filtered[i][1] > filtered[i + 1][1]:
                return False, f"Order violation: {filtered[i][0]} before {filtered[i+1][0]}"
        
        return True, "Topological order valid"

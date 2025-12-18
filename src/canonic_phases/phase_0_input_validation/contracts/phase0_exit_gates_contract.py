"""Phase 0 Exit Gates Contract

Validates that all exit gates passed successfully.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ExitGatesContract:
    """Contract for Phase 0 exit gate validation.
    
    Ensures that all 7 mandatory exit gates have passed before proceeding to Phase 1.
    """
    
    def validate(self, gate_results: list[dict[str, Any]]) -> None:
        """Validate all exit gates passed.
        
        Args:
            gate_results: List of gate result dictionaries
            
        Raises:
            AssertionError: If any exit gate failed
        """
        assert gate_results, "No gate results provided"
        assert len(gate_results) == 7, f"Expected 7 gates, got {len(gate_results)}"
        
        failed_gates = [
            gr.get("gate_name", f"gate_{gr.get('gate_id', 'unknown')}")
            for gr in gate_results
            if not gr.get("passed", False)
        ]
        
        assert not failed_gates, f"Exit gates failed: {', '.join(failed_gates)}"
        
        # Verify all required gate IDs present
        gate_ids = {gr.get("gate_id") for gr in gate_results}
        expected_ids = {1, 2, 3, 4, 5, 6, 7}
        assert gate_ids == expected_ids, \
            f"Missing gate IDs: {expected_ids - gate_ids}"

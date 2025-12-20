"""
Module: phase2_d_calibration_policy
PHASE_LABEL: Phase 2
Sequence: D
Description: Calibration policies for quality scoring

Version: 1.0.0
Last Modified: 2025-12-20
Author: F.A.R.F.A.N Policy Pipeline
License: Proprietary

This module is part of Phase 2: Analysis & Question Execution.
All files in Phase_two/ must contain PHASE_LABEL: Phase 2.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CalibrationParameters:
    """Calibration parameters for a specific scope (global/dimension/PA/contract)."""
    
    confidence_threshold: float = 0.7
    method_weights: dict[str, float] = field(default_factory=dict)
    bayesian_priors: dict[str, Any] = field(default_factory=dict)
    random_seed: int = 42
    enable_belief_propagation: bool = True
    dempster_shafer_enabled: bool = True
    
    def validate(self) -> None:
        """Validate calibration parameters."""
        if not 0 <= self.confidence_threshold <= 1:
            raise ValueError(
                f"confidence_threshold must be in [0, 1], got {self.confidence_threshold}"
            )
        if self.random_seed < 0:
            raise ValueError(f"random_seed must be non-negative, got {self.random_seed}")


class CalibrationPolicy:
    """Manages calibration policies for JSON contract-based execution.
    
    Provides hierarchical calibration:
    - Global defaults
    - Dimension overrides (D1-D6)
    - Policy area overrides (PA01-PA10)
    - Contract overrides (Q001-Q300)
    """
    
    def __init__(self) -> None:
        self._global_params = CalibrationParameters()
        self._dimension_params: dict[str, CalibrationParameters] = {}
        self._policy_area_params: dict[str, CalibrationParameters] = {}
        self._contract_params: dict[str, CalibrationParameters] = {}
        
    def get_parameters(
        self,
        question_id: str,
        dimension_id: str | None = None,
        policy_area_id: str | None = None,
    ) -> CalibrationParameters:
        """Get calibration parameters for a specific context.
        
        Resolution order:
        1. Contract-specific (Q{i})
        2. Policy area-specific (PA{j})
        3. Dimension-specific (DIM{k})
        4. Global defaults
        """
        # Check contract-specific
        if question_id in self._contract_params:
            return self._contract_params[question_id]
        
        # Check policy area-specific
        if policy_area_id and policy_area_id in self._policy_area_params:
            return self._policy_area_params[policy_area_id]
        
        # Check dimension-specific
        if dimension_id and dimension_id in self._dimension_params:
            return self._dimension_params[dimension_id]
        
        # Return global defaults
        return self._global_params
    
    def set_dimension_parameters(
        self, dimension_id: str, params: CalibrationParameters
    ) -> None:
        """Set calibration parameters for a specific dimension (D1-D6)."""
        params.validate()
        self._dimension_params[dimension_id] = params
        logger.info(f"Set calibration parameters for dimension {dimension_id}")
    
    def set_policy_area_parameters(
        self, policy_area_id: str, params: CalibrationParameters
    ) -> None:
        """Set calibration parameters for a specific policy area (PA01-PA10)."""
        params.validate()
        self._policy_area_params[policy_area_id] = params
        logger.info(f"Set calibration parameters for policy area {policy_area_id}")
    
    def set_contract_parameters(
        self, question_id: str, params: CalibrationParameters
    ) -> None:
        """Set calibration parameters for a specific contract (Q001-Q300)."""
        params.validate()
        self._contract_params[question_id] = params
        logger.info(f"Set calibration parameters for contract {question_id}")
    
    def load_from_contract(self, contract: dict[str, Any]) -> CalibrationParameters:
        """Load calibration parameters from a contract specification.
        
        Args:
            contract: Q{i}.v3.json contract dict
            
        Returns:
            CalibrationParameters extracted from contract or defaults
        """
        calibration_spec = contract.get("calibration", {})
        
        params = CalibrationParameters(
            confidence_threshold=calibration_spec.get("confidence_threshold", 0.7),
            method_weights=calibration_spec.get("method_weights", {}),
            bayesian_priors=calibration_spec.get("bayesian_priors", {}),
            random_seed=calibration_spec.get("random_seed", 42),
            enable_belief_propagation=calibration_spec.get(
                "enable_belief_propagation", True
            ),
            dempster_shafer_enabled=calibration_spec.get(
                "dempster_shafer_enabled", True
            ),
        )
        
        params.validate()
        return params


class ParametrizationManager:
    """Manages runtime parametrization for 300 JSON contract executors."""
    
    def __init__(self, calibration_policy: CalibrationPolicy) -> None:
        self._calibration_policy = calibration_policy
        
    def get_execution_parameters(
        self, contract: dict[str, Any]
    ) -> dict[str, Any]:
        """Extract execution parameters from contract for executor.
        
        Returns dict suitable for passing to GenericContractExecutor.
        """
        identity = contract.get("identity", {})
        question_id = identity.get("question_id")
        dimension_id = identity.get("dimension_id")
        policy_area_id = identity.get("policy_area_id")
        
        # Get calibration parameters
        calib_params = self._calibration_policy.get_parameters(
            question_id=question_id,
            dimension_id=dimension_id,
            policy_area_id=policy_area_id,
        )
        
        # Build execution parameters
        return {
            "question_id": question_id,
            "dimension_id": dimension_id,
            "policy_area_id": policy_area_id,
            "calibration": {
                "confidence_threshold": calib_params.confidence_threshold,
                "method_weights": calib_params.method_weights,
                "random_seed": calib_params.random_seed,
                "enable_belief_propagation": calib_params.enable_belief_propagation,
                "dempster_shafer_enabled": calib_params.dempster_shafer_enabled,
            },
            "method_binding": contract.get("method_binding", {}),
            "evidence_assembly": contract.get("evidence_assembly", {}),
        }


class ConfidenceCalibrator:
    """Bayesian confidence calibration for multi-method outputs.
    
    Implements Dempster-Shafer belief propagation and calibrated
    confidence intervals for method aggregation.
    """
    
    def __init__(self, calibration_policy: CalibrationPolicy) -> None:
        self._calibration_policy = calibration_policy
        
    def calibrate_confidence(
        self,
        method_outputs: list[dict[str, Any]],
        question_id: str,
        dimension_id: str,
        policy_area_id: str,
    ) -> float:
        """Calibrate overall confidence from multi-method outputs.
        
        Uses Bayesian aggregation with method-specific weights.
        
        Returns:
            Calibrated confidence score in [0, 1]
        """
        params = self._calibration_policy.get_parameters(
            question_id=question_id,
            dimension_id=dimension_id,
            policy_area_id=policy_area_id,
        )
        
        if not method_outputs:
            return 0.0
        
        # Extract confidence scores from method outputs
        confidences = []
        weights = []
        
        for output in method_outputs:
            conf = output.get("confidence", 0.5)
            method_name = output.get("method_name", "unknown")
            weight = params.method_weights.get(method_name, 1.0)
            
            confidences.append(conf)
            weights.append(weight)
        
        # Weighted average
        if sum(weights) == 0:
            return 0.0
        
        calibrated = sum(c * w for c, w in zip(confidences, weights)) / sum(weights)
        
        # Apply Dempster-Shafer if enabled
        if params.dempster_shafer_enabled:
            calibrated = self._apply_dempster_shafer(calibrated, method_outputs)
        
        return min(max(calibrated, 0.0), 1.0)
    
    def _apply_dempster_shafer(
        self, base_confidence: float, method_outputs: list[dict[str, Any]]
    ) -> float:
        """Apply Dempster-Shafer belief propagation.
        
        This is a simplified implementation. Full Dempster-Shafer
        is implemented in EvidenceNexus.
        """
        # Simplified: adjust confidence based on method agreement
        if len(method_outputs) < 2:
            return base_confidence
        
        # Calculate variance in method confidences
        confidences = [o.get("confidence", 0.5) for o in method_outputs]
        variance = sum((c - base_confidence) ** 2 for c in confidences) / len(
            confidences
        )
        
        # Reduce confidence if high variance (methods disagree)
        disagreement_penalty = min(variance * 2, 0.3)
        
        return base_confidence * (1 - disagreement_penalty)

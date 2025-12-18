"""Phase 0 Fallback Policy Contract

Enforces strict fallback policies in PROD mode.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class FallbackPolicyContract:
    """Contract for Phase 0 fallback policy enforcement.
    
    Ensures that PROD mode forbids Category A (critical) and Category C (development)
    fallbacks that could compromise result integrity.
    """
    
    def enforce_prod_policy(self, config: Any) -> None:
        """Enforce PROD mode fallback policy.
        
        Args:
            config: Runtime configuration object to validate
            
        Raises:
            AssertionError: If forbidden fallbacks are enabled in PROD
        """
        # Category A - Critical System Integrity (FORBIDDEN in PROD)
        allow_contradiction = getattr(config, "allow_contradiction_fallback", False)
        assert not allow_contradiction, \
            "Category A fallback (contradiction detection) forbidden in PROD"
        
        allow_validator_disable = getattr(config, "allow_validator_disable", False)
        assert not allow_validator_disable, \
            "Category A fallback (validator disable) forbidden in PROD"
        
        allow_execution_estimates = getattr(config, "allow_execution_estimates", False)
        assert not allow_execution_estimates, \
            "Category A fallback (execution estimates) forbidden in PROD"
        
        # Category C - Development Convenience (FORBIDDEN in PROD)
        allow_dev_ingestion = getattr(config, "allow_dev_ingestion_fallbacks", False)
        assert not allow_dev_ingestion, \
            "Category C fallback (dev ingestion) forbidden in PROD"
        
        allow_aggregation_defaults = getattr(config, "allow_aggregation_defaults", False)
        assert not allow_aggregation_defaults, \
            "Category C fallback (aggregation defaults) forbidden in PROD"

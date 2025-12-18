"""Phase 0 Bootstrap Contract

Validates that bootstrap initialization completed successfully.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class BootstrapContract:
    """Contract for Phase 0 bootstrap validation.
    
    Ensures that the pipeline runner has successfully completed bootstrap
    initialization including runtime config loading and artifact directory setup.
    """
    
    def validate(self, runner: Any) -> None:
        """Validate bootstrap state of the runner.
        
        Args:
            runner: The Phase 0 runner instance to validate
            
        Raises:
            AssertionError: If bootstrap validation fails
        """
        # Check bootstrap did not fail
        bootstrap_failed = getattr(runner, "_bootstrap_failed", False)
        assert bootstrap_failed is False, "Bootstrap failed"
        
        # Check runtime config loaded
        runtime_config = getattr(runner, "runtime_config", None)
        assert runtime_config is not None, "Runtime config not loaded"
        
        # Check no bootstrap errors
        errors = getattr(runner, "errors", [])
        assert not errors, f"Bootstrap errors detected: {errors}"

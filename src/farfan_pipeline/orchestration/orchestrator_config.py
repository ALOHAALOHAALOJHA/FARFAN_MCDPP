"""
Orchestrator Configuration Module
=================================

Provides configuration management for the CoreOrchestrator.
"""

from dataclasses import dataclass, field
from typing import Any, Optional


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


@dataclass
class OrchestratorConfig:
    """Configuration for the CoreOrchestrator."""
    
    # Core settings
    municipality_name: str = "Unknown"
    document_path: Optional[str] = None
    output_dir: str = "./output"
    
    # Execution settings
    strict_mode: bool = False
    phases_to_execute: str = "ALL"
    
    # Resource settings
    seed: int = 42
    max_workers: int = 4
    enable_parallel_execution: bool = True
    
    # Feature flags
    enable_sisas: bool = True
    enable_calibration: bool = True
    enable_checkpoint: bool = True
    
    # Paths
    questionnaire_path: str = "canonic_questionnaire_central/questionnaire_monolith.json"
    methods_file: str = "json_methods/METHODS_OPERACIONALIZACION.json"
    
    # Resource limits
    resource_limits: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "municipality_name": self.municipality_name,
            "document_path": self.document_path,
            "output_dir": self.output_dir,
            "strict_mode": self.strict_mode,
            "phases_to_execute": self.phases_to_execute,
            "seed": self.seed,
            "max_workers": self.max_workers,
            "enable_parallel_execution": self.enable_parallel_execution,
            "enable_sisas": self.enable_sisas,
            "enable_calibration": self.enable_calibration,
            "enable_checkpoint": self.enable_checkpoint,
            "questionnaire_path": self.questionnaire_path,
            "methods_file": self.methods_file,
            "resource_limits": self.resource_limits,
        }


def validate_config(config: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate configuration dictionary.
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Required fields
    if not config.get("document_path"):
        errors.append("document_path is required")
    
    # Type validation
    if config.get("seed") is not None and not isinstance(config.get("seed"), int):
        errors.append("seed must be an integer")
    
    if config.get("max_workers") is not None:
        workers = config.get("max_workers")
        if not isinstance(workers, int) or workers < 1:
            errors.append("max_workers must be a positive integer")
    
    return len(errors) == 0, errors


def get_development_config() -> OrchestratorConfig:
    """Get configuration preset for development."""
    return OrchestratorConfig(
        strict_mode=False,
        enable_sisas=True,
        enable_calibration=False,
        max_workers=2,
    )


def get_production_config() -> OrchestratorConfig:
    """Get configuration preset for production."""
    return OrchestratorConfig(
        strict_mode=True,
        enable_sisas=True,
        enable_calibration=True,
        max_workers=4,
    )


def get_testing_config() -> OrchestratorConfig:
    """Get configuration preset for testing."""
    return OrchestratorConfig(
        strict_mode=True,
        enable_sisas=False,
        enable_calibration=False,
        max_workers=1,
        phases_to_execute="0-2",  # Only run Phase 0-2 for testing
    )

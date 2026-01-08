"""
Validator Strategy Pattern - Base Abstractions

Defines protocols and base classes for extensible validator system.
Validators can be dynamically registered and composed.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol
from enum import Enum


class ValidationSeverity(Enum):
    """Severity levels for validation results."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class ValidationResult:
    """Generic validation result."""
    
    validator_name: str
    valid: bool
    severity: ValidationSeverity
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    score: float = 1.0  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "validator_name": self.validator_name,
            "valid": self.valid,
            "severity": self.severity.value,
            "violations": self.violations,
            "warnings": self.warnings,
            "metadata": self.metadata,
            "score": self.score
        }


class ValidatorProtocol(Protocol):
    """Protocol that all validators must implement."""
    
    @property
    def name(self) -> str:
        """Unique validator name."""
        ...
    
    @property
    def version(self) -> str:
        """Validator version."""
        ...
    
    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate the given context.
        
        Args:
            context: Dictionary containing all necessary validation context
            
        Returns:
            ValidationResult with validation outcome
        """
        ...
    
    def get_required_context_keys(self) -> List[str]:
        """Return list of required context keys."""
        ...


class BaseValidator(ABC):
    """Base class for all validators with common functionality."""
    
    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        enabled: bool = True,
        strict_mode: bool = True
    ):
        self._name = name
        self._version = version
        self._enabled = enabled
        self._strict_mode = strict_mode
        self._validation_count = 0
        self._failure_count = 0
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def version(self) -> str:
        return self._version
    
    @property
    def enabled(self) -> bool:
        return self._enabled
    
    def enable(self) -> None:
        """Enable this validator."""
        self._enabled = True
    
    def disable(self) -> None:
        """Disable this validator."""
        self._enabled = False
    
    @abstractmethod
    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate the given context.
        
        Must be implemented by subclasses.
        """
        pass
    
    @abstractmethod
    def get_required_context_keys(self) -> List[str]:
        """Return list of required context keys."""
        pass
    
    def _record_validation(self, result: ValidationResult) -> None:
        """Record validation statistics."""
        self._validation_count += 1
        if not result.valid:
            self._failure_count += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get validator statistics."""
        return {
            "validator_name": self.name,
            "version": self.version,
            "enabled": self.enabled,
            "total_validations": self._validation_count,
            "failures": self._failure_count,
            "success_rate": (
                (self._validation_count - self._failure_count) / self._validation_count
                if self._validation_count > 0
                else 1.0
            )
        }


class ValidatorRegistry:
    """Registry for dynamically managing validators."""
    
    def __init__(self):
        self._validators: Dict[str, ValidatorProtocol] = {}
        self._validator_order: List[str] = []
    
    def register(
        self,
        validator: ValidatorProtocol,
        priority: Optional[int] = None
    ) -> None:
        """
        Register a validator.
        
        Args:
            validator: Validator instance
            priority: Optional priority (lower number = higher priority)
        """
        name = validator.name
        if name in self._validators:
            raise ValueError(f"Validator {name} already registered")
        
        self._validators[name] = validator
        
        if priority is not None and 0 <= priority < len(self._validator_order):
            self._validator_order.insert(priority, name)
        else:
            self._validator_order.append(name)
    
    def unregister(self, validator_name: str) -> None:
        """Unregister a validator."""
        if validator_name in self._validators:
            del self._validators[validator_name]
            self._validator_order.remove(validator_name)
    
    def get(self, validator_name: str) -> Optional[ValidatorProtocol]:
        """Get a validator by name."""
        return self._validators.get(validator_name)
    
    def get_all(self) -> List[ValidatorProtocol]:
        """Get all validators in priority order."""
        return [self._validators[name] for name in self._validator_order if name in self._validators]
    
    def get_enabled(self) -> List[ValidatorProtocol]:
        """Get all enabled validators."""
        return [v for v in self.get_all() if hasattr(v, 'enabled') and v.enabled]
    
    def validate_all(
        self,
        context: Dict[str, Any],
        stop_on_first_failure: bool = False
    ) -> List[ValidationResult]:
        """
        Run all enabled validators on the given context.
        
        Args:
            context: Validation context
            stop_on_first_failure: If True, stop on first validation failure
            
        Returns:
            List of validation results
        """
        results = []
        
        for validator in self.get_enabled():
            result = validator.validate(context)
            results.append(result)
            
            if stop_on_first_failure and not result.valid:
                break
        
        return results
    
    def clear(self) -> None:
        """Clear all registered validators."""
        self._validators.clear()
        self._validator_order.clear()


class CompositeValidator(BaseValidator):
    """
    Composite validator that runs multiple validators.
    
    Allows grouping validators and treating them as a single unit.
    """
    
    def __init__(
        self,
        name: str,
        validators: List[ValidatorProtocol],
        require_all: bool = True,
        version: str = "1.0.0"
    ):
        super().__init__(name, version)
        self._validators = validators
        self._require_all = require_all
    
    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """Run all sub-validators."""
        results = []
        all_violations = []
        all_warnings = []
        
        for validator in self._validators:
            if hasattr(validator, 'enabled') and not validator.enabled:
                continue
            
            result = validator.validate(context)
            results.append(result)
            all_violations.extend(result.violations)
            all_warnings.extend(result.warnings)
        
        if self._require_all:
            valid = all(r.valid for r in results)
        else:
            valid = any(r.valid for r in results)
        
        avg_score = sum(r.score for r in results) / len(results) if results else 0.0
        
        composite_result = ValidationResult(
            validator_name=self.name,
            valid=valid,
            severity=ValidationSeverity.ERROR if not valid else ValidationSeverity.INFO,
            violations=all_violations,
            warnings=all_warnings,
            score=avg_score,
            metadata={
                "sub_validators": [r.to_dict() for r in results],
                "require_all": self._require_all
            }
        )
        
        self._record_validation(composite_result)
        return composite_result
    
    def get_required_context_keys(self) -> List[str]:
        """Aggregate required keys from all sub-validators."""
        keys = set()
        for validator in self._validators:
            keys.update(validator.get_required_context_keys())
        return list(keys)

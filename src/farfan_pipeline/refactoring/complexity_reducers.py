"""
Complexity Reduction Patterns and Refactoring Utilities

This module provides strategic patterns and utilities to reduce cyclomatic complexity
in pipeline functions. It demonstrates best practices for refactoring high-complexity
code while maintaining functionality and testability.

Key Patterns:
- Strategy Pattern: Replace conditional logic with polymorphic strategies
- Builder Pattern: Simplify complex object construction
- Chain of Responsibility: Replace nested if-else with validation chains
- State Machine: Manage complex multi-step processes
- Command Pattern: Encapsulate operations for better testability
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol, Tuple, TypeVar

import logging

logger = logging.getLogger(__name__)

# Type variables for generic patterns
T = TypeVar('T')
V = TypeVar('V')


# ============================================================================
# STRATEGY PATTERN: Replace conditional logic with polymorphic strategies
# ============================================================================

class ValidationStrategy(ABC):
    """Base class for validation strategies.

    Use this to replace large if-elif chains that validate different types.

    Before (High Complexity):
        if contract_type == 'TYPE_A':
            # 20 lines of TYPE_A validation
        elif contract_type == 'TYPE_B':
            # 20 lines of TYPE_B validation
        elif contract_type == 'TYPE_C':
            # 20 lines of TYPE_C validation
        # ... (adds 10+ to complexity)

    After (Low Complexity):
        strategy = strategy_factory.get_strategy(contract_type)
        return strategy.validate(contract)  # complexity: 1
    """

    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate data and return (is_valid, errors)."""
        pass

    @abstractmethod
    def get_type_name(self) -> str:
        """Return the type this strategy handles."""
        pass


class StrategyFactory:
    """Factory for managing validation strategies.

    Reduces complexity by eliminating type-checking conditionals.
    """

    def __init__(self):
        self._strategies: Dict[str, ValidationStrategy] = {}

    def register(self, strategy: ValidationStrategy) -> None:
        """Register a validation strategy."""
        self._strategies[strategy.get_type_name()] = strategy

    def get_strategy(self, type_name: str) -> Optional[ValidationStrategy]:
        """Get strategy for a type. Returns None if not found."""
        return self._strategies.get(type_name)

    def validate(self, type_name: str, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate data using the appropriate strategy."""
        strategy = self.get_strategy(type_name)
        if not strategy:
            return False, [f"No validation strategy for type: {type_name}"]
        return strategy.validate(data)


# ============================================================================
# CHAIN OF RESPONSIBILITY: Replace nested validation with chain
# ============================================================================

class Validator(ABC):
    """Base validator in a chain of responsibility.

    Use this to replace deeply nested validation logic.

    Before (High Complexity):
        errors = []
        if not field1:
            errors.append("field1 missing")
        else:
            if not validate_field1(field1):
                errors.append("field1 invalid")
                if field1_type == 'A':
                    # nested validation
                elif field1_type == 'B':
                    # nested validation
        if not field2:
            # ... more nesting
        # (complexity compounds with each level)

    After (Low Complexity):
        return validation_chain.validate(data)  # complexity: 1
    """

    def __init__(self, next_validator: Optional[Validator] = None):
        self._next = next_validator

    def validate(self, data: Dict[str, Any], errors: List[str]) -> bool:
        """Validate data, append errors, and pass to next validator."""
        # Perform this validator's check
        is_valid = self._check(data, errors)

        # Pass to next in chain
        if self._next:
            return self._next.validate(data, errors) and is_valid
        return is_valid

    @abstractmethod
    def _check(self, data: Dict[str, Any], errors: List[str]) -> bool:
        """Perform this validator's specific check."""
        pass


class ValidationChain:
    """Builder for creating validation chains."""

    def __init__(self):
        self._validators: List[Validator] = []

    def add(self, validator: Validator) -> ValidationChain:
        """Add a validator to the chain (builder pattern)."""
        self._validators.append(validator)
        return self

    def build(self) -> Validator:
        """Build the validation chain."""
        if not self._validators:
            raise ValueError("Validation chain is empty")

        # Link validators together
        for i in range(len(self._validators) - 1):
            self._validators[i]._next = self._validators[i + 1]

        return self._validators[0]

    def validate(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Convenience method to build and validate."""
        if not self._validators:
            return True, []

        errors: List[str] = []
        validator = self.build()
        is_valid = validator.validate(data, errors)
        return is_valid, errors


# ============================================================================
# BUILDER PATTERN: Simplify complex object construction
# ============================================================================

class ContractBuilder:
    """Builder for constructing complex contract objects.

    Use this to replace functions with many parameters and complex setup.

    Before (High Complexity):
        def create_contract(type, version, fields, patterns, constraints,
                          validations, metadata, options, ...):
            # 50+ lines of conditional construction
            # complexity: 15+

    After (Low Complexity):
        contract = (ContractBuilder()
                   .with_type(type)
                   .with_version(version)
                   .with_fields(fields)
                   .build())  # complexity: 1
    """

    def __init__(self):
        self._contract: Dict[str, Any] = {}
        self._errors: List[str] = []

    def with_type(self, contract_type: str) -> ContractBuilder:
        """Set contract type."""
        self._contract['type'] = contract_type
        return self

    def with_version(self, version: str) -> ContractBuilder:
        """Set contract version."""
        self._contract['version'] = version
        return self

    def with_fields(self, fields: Dict[str, Any]) -> ContractBuilder:
        """Set contract fields."""
        self._contract['fields'] = fields
        return self

    def with_patterns(self, patterns: List[str]) -> ContractBuilder:
        """Set validation patterns."""
        self._contract['patterns'] = patterns
        return self

    def with_metadata(self, metadata: Dict[str, Any]) -> ContractBuilder:
        """Set contract metadata."""
        self._contract['metadata'] = metadata
        return self

    def validate(self) -> bool:
        """Validate the contract being built."""
        if 'type' not in self._contract:
            self._errors.append("Contract type is required")
        if 'version' not in self._contract:
            self._errors.append("Contract version is required")
        return len(self._errors) == 0

    def build(self) -> Dict[str, Any]:
        """Build and return the contract."""
        if not self.validate():
            raise ValueError(f"Invalid contract: {', '.join(self._errors)}")
        return self._contract

    def get_errors(self) -> List[str]:
        """Get validation errors."""
        return self._errors.copy()


# ============================================================================
# STATE MACHINE: Manage multi-step processes
# ============================================================================

class ProcessState(Enum):
    """States for a multi-step process."""
    INITIAL = "initial"
    VALIDATING = "validating"
    PROCESSING = "processing"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"


class StateTransition(Protocol):
    """Protocol for state transition functions."""
    def __call__(self, context: Dict[str, Any]) -> ProcessState:
        ...


class ProcessStateMachine:
    """State machine for managing complex multi-step processes.

    Use this to replace long sequences of conditional steps.

    Before (High Complexity):
        state = 'init'
        while state != 'done':
            if state == 'init':
                if validate():
                    state = 'processing'
                else:
                    state = 'error'
            elif state == 'processing':
                if step1():
                    if step2():
                        state = 'finalizing'
                    else:
                        state = 'retry'
                else:
                    state = 'error'
            # ... many more states (complexity: 20+)

    After (Low Complexity):
        machine = ProcessStateMachine()
        return machine.run(context)  # complexity: 2
    """

    def __init__(self):
        self._state = ProcessState.INITIAL
        self._context: Dict[str, Any] = {}
        self._transitions: Dict[ProcessState, StateTransition] = {}

    def register_transition(
        self,
        from_state: ProcessState,
        transition_fn: StateTransition
    ) -> None:
        """Register a state transition function."""
        self._transitions[from_state] = transition_fn

    def run(self, initial_context: Dict[str, Any]) -> Tuple[ProcessState, Dict[str, Any]]:
        """Run the state machine to completion."""
        self._context = initial_context.copy()
        self._state = ProcessState.INITIAL

        max_iterations = 100  # Prevent infinite loops
        iterations = 0

        while self._state not in [ProcessState.COMPLETED, ProcessState.FAILED]:
            if iterations >= max_iterations:
                logger.error("State machine exceeded max iterations")
                self._state = ProcessState.FAILED
                break

            transition = self._transitions.get(self._state)
            if not transition:
                logger.error(f"No transition defined for state: {self._state}")
                self._state = ProcessState.FAILED
                break

            try:
                self._state = transition(self._context)
            except Exception as e:
                logger.error(f"State transition failed: {str(e)}")
                self._state = ProcessState.FAILED

            iterations += 1

        return self._state, self._context

    def get_state(self) -> ProcessState:
        """Get current state."""
        return self._state


# ============================================================================
# COMMAND PATTERN: Encapsulate operations
# ============================================================================

class Command(ABC):
    """Base class for commands.

    Use this to encapsulate operations and reduce conditional logic.
    """

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> bool:
        """Execute the command. Returns success status."""
        pass

    @abstractmethod
    def can_execute(self, context: Dict[str, Any]) -> bool:
        """Check if command can execute in current context."""
        pass

    def undo(self, context: Dict[str, Any]) -> None:
        """Undo the command (optional)."""
        pass


class CommandExecutor:
    """Executor for running commands in sequence.

    Reduces complexity by eliminating sequential conditional logic.
    """

    def __init__(self):
        self._commands: List[Command] = []
        self._executed: List[Command] = []

    def add_command(self, command: Command) -> CommandExecutor:
        """Add a command to execute (builder pattern)."""
        self._commands.append(command)
        return self

    def execute_all(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Execute all commands in sequence."""
        errors: List[str] = []

        for command in self._commands:
            if not command.can_execute(context):
                errors.append(f"Cannot execute command: {command.__class__.__name__}")
                continue

            try:
                success = command.execute(context)
                if success:
                    self._executed.append(command)
                else:
                    errors.append(f"Command failed: {command.__class__.__name__}")
                    break
            except Exception as e:
                errors.append(f"Command error: {str(e)}")
                break

        return len(errors) == 0, errors

    def rollback(self, context: Dict[str, Any]) -> None:
        """Rollback executed commands in reverse order."""
        for command in reversed(self._executed):
            try:
                command.undo(context)
            except Exception as e:
                logger.error(f"Rollback failed for {command.__class__.__name__}: {str(e)}")


# ============================================================================
# FUNCTIONAL UTILITIES: Reduce imperative complexity
# ============================================================================

def partition(predicate: Callable[[T], bool], items: List[T]) -> Tuple[List[T], List[T]]:
    """Partition a list into two lists based on a predicate.

    Reduces complexity of filtering logic.

    Before (Imperative):
        valid = []
        invalid = []
        for item in items:
            if predicate(item):
                valid.append(item)
            else:
                invalid.append(item)
        # complexity: 2

    After (Functional):
        valid, invalid = partition(predicate, items)  # complexity: 1
    """
    passed = [item for item in items if predicate(item)]
    failed = [item for item in items if not predicate(item)]
    return passed, failed


def pipeline(*functions: Callable[[T], T]) -> Callable[[T], T]:
    """Create a function pipeline.

    Reduces complexity of sequential transformations.

    Before (Sequential):
        result = step1(data)
        result = step2(result)
        result = step3(result)
        # ... more steps (complexity grows)

    After (Pipeline):
        process = pipeline(step1, step2, step3)
        result = process(data)  # complexity: 1
    """
    def composed(value: T) -> T:
        result = value
        for func in functions:
            result = func(result)
        return result
    return composed


def safe_get(dictionary: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Safely navigate nested dictionaries.

    Reduces complexity of nested key access.

    Before (Nested checks):
        value = None
        if 'a' in data:
            if 'b' in data['a']:
                if 'c' in data['a']['b']:
                    value = data['a']['b']['c']
        # complexity: 3

    After (Safe get):
        value = safe_get(data, 'a', 'b', 'c', default=None)  # complexity: 1
    """
    result = dictionary
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
            if result is None:
                return default
        else:
            return default
    return result if result is not None else default


# ============================================================================
# COMPLEXITY METRICS: Measure refactoring impact
# ============================================================================

@dataclass
class ComplexityMetrics:
    """Metrics for measuring complexity reduction."""
    original_complexity: int
    refactored_complexity: int
    lines_before: int
    lines_after: int
    conditionals_before: int
    conditionals_after: int

    def reduction_percentage(self) -> float:
        """Calculate complexity reduction percentage."""
        if self.original_complexity == 0:
            return 0.0
        return ((self.original_complexity - self.refactored_complexity) /
                self.original_complexity * 100)

    def lines_saved(self) -> int:
        """Calculate lines of code saved."""
        return self.lines_before - self.lines_after

    def report(self) -> str:
        """Generate a metrics report."""
        return f"""
Complexity Reduction Report:
---------------------------
Original Complexity: {self.original_complexity}
Refactored Complexity: {self.refactored_complexity}
Reduction: {self.reduction_percentage():.1f}%

Lines of Code:
  Before: {self.lines_before}
  After: {self.lines_after}
  Saved: {self.lines_saved()}

Conditionals:
  Before: {self.conditionals_before}
  After: {self.conditionals_after}
  Reduction: {self.conditionals_before - self.conditionals_after}
"""

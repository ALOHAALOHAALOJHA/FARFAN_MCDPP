"""
Refactoring Module: Strategic Patterns for Complexity Reduction

This module provides design patterns and utilities for reducing cyclomatic complexity
in the F.A.R.F.A.N pipeline. It demonstrates strategic architectural improvements
that can be applied to high-complexity functions.

Key Components:
- ValidationStrategy: Strategy pattern for type-specific validation
- ValidationChain: Chain of Responsibility for sequential validation
- ContractBuilder: Builder pattern for complex object construction
- ProcessStateMachine: State machine for multi-step processes
- CommandExecutor: Command pattern for encapsulated operations

Usage Example:
    from farfan_pipeline.refactoring import (
        StrategyFactory,
        ValidationChain,
        ContractBuilder
    )

    # Replace 20+ line if-elif chain with strategy pattern
    factory = StrategyFactory()
    result = factory.validate(contract_type, data)

    # Replace nested validation with chain
    chain = ValidationChain()
    chain.add(RequiredFieldsValidator())
    chain.add(TypeValidator())
    chain.add(RangeValidator())
    is_valid, errors = chain.validate(data)

    # Replace complex construction with builder
    contract = (ContractBuilder()
               .with_type('TYPE_A')
               .with_version('v3')
               .with_fields(fields)
               .build())
"""

from farfan_pipeline.refactoring.complexity_reducers import (
    # Strategy Pattern
    ValidationStrategy,
    StrategyFactory,

    # Chain of Responsibility
    Validator,
    ValidationChain,

    # Builder Pattern
    ContractBuilder,

    # State Machine
    ProcessState,
    ProcessStateMachine,

    # Command Pattern
    Command,
    CommandExecutor,

    # Utilities
    partition,
    pipeline,
    safe_get,

    # Metrics
    ComplexityMetrics,
)

__all__ = [
    # Strategy Pattern
    'ValidationStrategy',
    'StrategyFactory',

    # Chain of Responsibility
    'Validator',
    'ValidationChain',

    # Builder Pattern
    'ContractBuilder',

    # State Machine
    'ProcessState',
    'ProcessStateMachine',

    # Command Pattern
    'Command',
    'CommandExecutor',

    # Utilities
    'partition',
    'pipeline',
    'safe_get',

    # Metrics
    'ComplexityMetrics',
]

__version__ = '1.0.0'

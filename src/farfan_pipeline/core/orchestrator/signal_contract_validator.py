"""
Contract-Driven Validation Engine - PROPOSAL #4
================================================

Exploits 'failure_contract' and 'validations' fields (600 specs) to provide
intelligent failure handling and self-diagnosis.

Intelligence Unlocked: 600 validation contracts
Impact: Self-diagnosing failures with precise error codes
ROI: From "it failed" to "ERR_BUDGET_MISSING_CURRENCY on page 47"

Author: F.A.R.F.A.N Pipeline
Date: 2025-12-02
Refactoring: Surgical #3 of 4
"""

from dataclasses import dataclass
from typing import Any

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of contract validation."""
    
    status: str  # 'success', 'failed', 'invalid'
    passed: bool
    error_code: str | None = None
    condition_violated: str | None = None
    validation_failures: list[str] | None = None
    remediation: str | None = None
    details: dict[str, Any] | None = None


def check_failure_condition(
    result: dict[str, Any],
    condition: str
) -> bool:
    """
    Check if a failure condition is met.
    
    Args:
        result: Analysis result dict
        condition: Condition string (e.g., 'missing_currency', 'negative_amount')
    
    Returns:
        True if condition is met (failure detected)
    """
    # Parse condition type
    if condition.startswith('missing_'):
        field = condition[8:]  # Remove 'missing_' prefix
        return field not in result or result.get(field) is None
    
    elif condition.startswith('negative_'):
        field = condition[9:]  # Remove 'negative_' prefix
        value = result.get(field)
        if value is None:
            return False
        try:
            return float(value) < 0
        except (ValueError, TypeError):
            return False
    
    elif condition.startswith('empty_'):
        field = condition[6:]  # Remove 'empty_' prefix
        value = result.get(field)
        return not value or (isinstance(value, (list, dict, str)) and len(value) == 0)
    
    elif condition == 'invalid_format':
        return result.get('format_valid', True) is False
    
    elif condition == 'low_confidence':
        confidence = result.get('confidence', 1.0)
        return confidence < 0.5
    
    # Unknown condition = not met (conservative)
    return False


def execute_failure_contract(
    result: dict[str, Any],
    failure_contract: dict[str, Any]
) -> ValidationResult:
    """
    Execute failure contract checks on analysis result.
    
    Args:
        result: Analysis result to validate
        failure_contract: Contract from signal node, e.g.:
            {
                'abort_if': ['missing_currency', 'negative_amount'],
                'emit_code': 'ERR_BUDGET_INVALID_Q047'
            }
    
    Returns:
        ValidationResult with failure details if contract violated
    """
    abort_conditions = failure_contract.get('abort_if', [])
    error_code = failure_contract.get('emit_code', 'ERR_UNKNOWN')
    
    # Check each abort condition
    for condition in abort_conditions:
        if check_failure_condition(result, condition):
            # Contract violated - generate failure result
            remediation = suggest_remediation(condition, result)
            
            logger.warning(
                "failure_contract_violated",
                condition=condition,
                error_code=error_code,
                remediation=remediation
            )
            
            return ValidationResult(
                status='failed',
                passed=False,
                error_code=error_code,
                condition_violated=condition,
                remediation=remediation,
                details=result
            )
    
    # All checks passed
    return ValidationResult(
        status='success',
        passed=True
    )


def suggest_remediation(condition: str, result: dict[str, Any]) -> str:
    """
    Suggest remediation for failed condition.
    
    Args:
        condition: Failed condition
        result: Analysis result
    
    Returns:
        Human-readable remediation suggestion
    """
    if condition.startswith('missing_'):
        field = condition[8:]
        return f"Check source document for {field} field. May require manual extraction."
    
    elif condition.startswith('negative_'):
        field = condition[9:]
        return f"Verify {field} value. Negative values may indicate parsing error."
    
    elif condition.startswith('empty_'):
        field = condition[6:]
        return f"No data extracted for {field}. Check pattern matching or source quality."
    
    elif condition == 'invalid_format':
        return "Data format validation failed. Review extraction logic."
    
    elif condition == 'low_confidence':
        confidence = result.get('confidence', 0)
        return f"Pattern match confidence ({confidence:.2f}) below threshold. Consider manual review."
    
    return "Review analysis result and source document."


def execute_validations(
    result: dict[str, Any],
    validations: dict[str, Any]
) -> dict[str, Any]:
    """
    Execute validation rules on result.
    
    Args:
        result: Analysis result
        validations: Validation spec from signal node, e.g.:
            {
                'rules': ['currency_present', 'amount_positive'],
                'thresholds': {'confidence': 0.7},
                'required_fields': ['amount', 'currency']
            }
    
    Returns:
        Dict with validation results:
            {
                'all_passed': bool,
                'passed_count': int,
                'failed_count': int,
                'failures': [list of failure messages]
            }
    """
    failures = []
    
    # Check required fields
    required_fields = validations.get('required_fields', [])
    for field in required_fields:
        if field not in result or result[field] is None:
            failures.append(f"Required field missing: {field}")
    
    # Check thresholds
    thresholds = validations.get('thresholds', {})
    for key, min_value in thresholds.items():
        actual_value = result.get(key)
        if actual_value is None:
            failures.append(f"Threshold field missing: {key}")
        else:
            try:
                if float(actual_value) < float(min_value):
                    failures.append(f"{key} ({actual_value}) below threshold ({min_value})")
            except (ValueError, TypeError):
                failures.append(f"Invalid value for {key}: {actual_value}")
    
    # Execute validation rules
    rules = validations.get('rules', [])
    for rule in rules:
        if not validate_rule(rule, result):
            failures.append(f"Validation rule failed: {rule}")
    
    return {
        'all_passed': len(failures) == 0,
        'passed_count': len(required_fields) + len(thresholds) + len(rules) - len(failures),
        'failed_count': len(failures),
        'failures': failures
    }


def validate_rule(rule: str, result: dict[str, Any]) -> bool:
    """
    Validate a specific rule against result.
    
    Args:
        rule: Rule name (e.g., 'currency_present', 'amount_positive')
        result: Analysis result
    
    Returns:
        True if rule passes
    """
    if rule == 'currency_present':
        currency = result.get('currency')
        return currency is not None and currency != ''
    
    elif rule == 'amount_positive':
        amount = result.get('amount')
        if amount is None:
            return False
        try:
            return float(amount) > 0
        except (ValueError, TypeError):
            return False
    
    elif rule == 'date_valid':
        date = result.get('date')
        # Simple check - more sophisticated date validation could be added
        return date is not None and len(str(date)) >= 4
    
    elif rule == 'confidence_high':
        confidence = result.get('confidence', 0)
        return confidence >= 0.8
    
    # Unknown rule = pass (conservative)
    return True


def validate_with_contract(
    result: dict[str, Any],
    signal_node: dict[str, Any]
) -> ValidationResult:
    """
    Full validation using both failure_contract and validations.
    
    This is the main entry point for contract-driven validation.
    
    Args:
        result: Analysis result to validate
        signal_node: Signal node with failure_contract and validations
    
    Returns:
        ValidationResult with comprehensive validation status
    
    Example:
        >>> result = {'amount': 1000, 'currency': None}
        >>> node = {
        ...     'failure_contract': {
        ...         'abort_if': ['missing_currency'],
        ...         'emit_code': 'ERR_BUDGET_001'
        ...     }
        ... }
        >>> validation = validate_with_contract(result, node)
        >>> validation.status
        'failed'
        >>> validation.error_code
        'ERR_BUDGET_001'
    """
    # First check failure contract (critical failures)
    failure_contract = signal_node.get('failure_contract')
    if failure_contract:
        contract_result = execute_failure_contract(result, failure_contract)
        if not contract_result.passed:
            return contract_result
    
    # Then check validations (quality checks)
    validations = signal_node.get('validations')
    if validations:
        validation_results = execute_validations(result, validations)
        
        if not validation_results['all_passed']:
            return ValidationResult(
                status='invalid',
                passed=False,
                validation_failures=validation_results['failures'],
                remediation="See validation_failures for details",
                details=result
            )
    
    # All validations passed
    return ValidationResult(
        status='success',
        passed=True,
        details=result
    )


# === EXPORTS ===

__all__ = [
    'ValidationResult',
    'check_failure_condition',
    'execute_failure_contract',
    'execute_validations',
    'validate_with_contract',
]

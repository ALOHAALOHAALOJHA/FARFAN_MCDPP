"""
Contract-Driven Validation Engine - PROPOSAL #4 (ENHANCED)
===========================================================

Exploits 'failure_contract' and 'validations' fields (600 specs) to provide
intelligent failure handling and self-diagnosis.

Intelligence Unlocked: 600 validation contracts
Impact: Self-diagnosing failures with precise error codes
ROI: From "it failed" to "ERR_BUDGET_MISSING_CURRENCY on page 47"

ENHANCEMENTS:
- ValidationOrchestrator for tracking all 300 question validations
- Comprehensive failure diagnostics with remediation suggestions
- Detailed reporting and metrics for validation coverage
- Integration with base executors for automatic validation tracking
- Export capabilities (JSON, CSV, Markdown)

INTEGRATION GUIDE:
==================

1. AUTOMATIC INTEGRATION (Recommended):

   Use global validation orchestrator with base executors:

   ```python
   from cross_cutting_infrastructure.irrigation_using_signals.SISAS.signal_contract_validator import (
       get_global_validation_orchestrator,
       reset_global_validation_orchestrator
   )

   # Initialize orchestrator before processing
   orchestrator = get_global_validation_orchestrator()
   orchestrator.start_orchestration()

   # Process all questions (validation happens automatically in executors)
   results = process_all_questions(...)

   # Complete orchestration and get report
   orchestrator.complete_orchestration()
   report = orchestrator.get_remediation_report()
   print(report)

   # Export results
   json_export = orchestrator.export_validation_results('json')
   csv_export = orchestrator.export_validation_results('csv')
   ```

2. MANUAL INTEGRATION (Fine-grained control):

   Use validate_result_with_orchestrator for explicit validation:

   ```python
   from cross_cutting_infrastructure.irrigation_using_signals.SISAS.signal_contract_validator import (
       ValidationOrchestrator,
       validate_result_with_orchestrator
   )

   # Create orchestrator
   orchestrator = ValidationOrchestrator(expected_question_count=300)
   orchestrator.start_orchestration()

   # Validate each result
   for question in all_questions:
       result = analyze_question(question)
       validation = validate_result_with_orchestrator(
           result=result,
           signal_node=question,
           orchestrator=orchestrator,
           auto_register=True
       )

       if not validation.passed:
           print(f"Failed: {validation.error_code}")
           print(f"Remediation: {validation.remediation}")

   # Complete and report
   orchestrator.complete_orchestration()
   summary = orchestrator.get_validation_summary()
   print(f"Success rate: {summary['success_rate']:.1%}")
   ```

3. EXECUTOR INTEGRATION:

   Pass validation orchestrator to executors:

   ```python
   from farfan_pipeline.phases.Phase_two.base_executor_with_contract import (
       BaseExecutorWithContract
   )
   from cross_cutting_infrastructure.irrigation_using_signals.SISAS.signal_contract_validator import (
       ValidationOrchestrator
   )

   # Create orchestrator
   orchestrator = ValidationOrchestrator(expected_question_count=300)

   # Pass to executor
   executor = MyExecutor(
       method_executor=method_executor,
       signal_registry=signal_registry,
       config=config,
       questionnaire_provider=questionnaire_provider,
       validation_orchestrator=orchestrator
   )

   # Validation happens automatically during execute()
   result = executor.execute(document, method_executor, question_context=context)

   # Check contract validation metadata
   print(result['contract_validation'])
   ```

4. VALIDATION COVERAGE ANALYSIS:

   ```python
   # Get missing questions
   expected_ids = ['Q001', 'Q002', ..., 'Q300']
   coverage = orchestrator.get_validation_coverage_report(expected_ids)
   print(f"Coverage: {coverage['coverage_percentage']:.1f}%")
   print(f"Missing: {coverage['missing_questions']}")

   # Get detailed summary
   summary = orchestrator.get_validation_summary()
   print(f"Error code frequency: {summary['error_code_frequency']}")
   print(f"Severity distribution: {summary['severity_counts']}")
   ```

5. REMEDIATION PRIORITIES:

   ```python
   # Get comprehensive remediation report
   report = orchestrator.get_remediation_report(
       include_all_details=True,
       max_failures_per_question=5
   )

   # Report includes:
   # - Summary statistics
   # - Failure breakdown by type
   # - Error code frequency
   # - Detailed failure information
   # - Prioritized remediation recommendations
   ```

VALIDATION CONTRACT STRUCTURE:
==============================

Each signal node can have two validation sections:

1. failure_contract: Critical conditions that abort execution

   ```json
   {
     "failure_contract": {
       "abort_if": ["missing_currency", "negative_amount"],
       "emit_code": "ERR_BUDGET_001",
       "severity": "error"
     }
   }
   ```

2. validations: Validation rules and thresholds

   ```json
   {
     "validations": {
       "rules": ["currency_present", "amount_positive"],
       "thresholds": {"confidence": 0.7},
       "required_fields": ["amount", "currency"]
     }
   }
   ```

FAILURE DIAGNOSTICS:
===================

Each ValidationResult includes:
- status: 'success', 'failed', 'invalid', 'error', 'skipped'
- passed: boolean
- error_code: standardized error code
- condition_violated: specific condition(s) that failed
- validation_failures: list of failure messages
- remediation: detailed remediation suggestions
- failures_detailed: structured failure information with:
  - failure_type: category of failure
  - field_name: field that failed
  - expected: expected value/format
  - actual: actual value received
  - severity: 'error', 'warning', 'info'
  - message: human-readable message
  - remediation: specific remediation steps
  - context: additional context information

Author: F.A.R.F.A.N Pipeline
Date: 2025-12-02
Refactoring: Surgical #3 of 4
Enhanced: 2025-12-02
"""

from dataclasses import dataclass, field
from typing import Any

try:
    import structlog

    logger = structlog.get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


# === GLOBAL ORCHESTRATOR INSTANCE ===
# This allows sharing a single orchestrator across all executor instances

_GLOBAL_VALIDATION_ORCHESTRATOR: "ValidationOrchestrator | None" = None


def get_global_validation_orchestrator() -> "ValidationOrchestrator":
    """
    Get or create the global validation orchestrator instance.

    Returns:
        Global ValidationOrchestrator instance
    """
    global _GLOBAL_VALIDATION_ORCHESTRATOR
    if _GLOBAL_VALIDATION_ORCHESTRATOR is None:
        _GLOBAL_VALIDATION_ORCHESTRATOR = ValidationOrchestrator(expected_question_count=300)
        logger.info("global_validation_orchestrator_created")
    return _GLOBAL_VALIDATION_ORCHESTRATOR


def set_global_validation_orchestrator(orchestrator: "ValidationOrchestrator | None") -> None:
    """
    Set the global validation orchestrator instance.

    Args:
        orchestrator: ValidationOrchestrator instance or None to clear
    """
    global _GLOBAL_VALIDATION_ORCHESTRATOR
    _GLOBAL_VALIDATION_ORCHESTRATOR = orchestrator
    if orchestrator:
        logger.info("global_validation_orchestrator_set")
    else:
        logger.info("global_validation_orchestrator_cleared")


def reset_global_validation_orchestrator() -> None:
    """Reset the global validation orchestrator to a fresh state."""
    global _GLOBAL_VALIDATION_ORCHESTRATOR
    if _GLOBAL_VALIDATION_ORCHESTRATOR is not None:
        _GLOBAL_VALIDATION_ORCHESTRATOR.reset()
        logger.info("global_validation_orchestrator_reset")
    else:
        logger.warning("global_validation_orchestrator_not_initialized")


@dataclass
class ValidationFailure:
    """Detailed information about a single validation failure."""

    failure_type: str
    field_name: str
    expected: Any
    actual: Any
    severity: str
    message: str
    remediation: str
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of contract validation with detailed diagnostics."""

    status: str
    passed: bool
    error_code: str | None = None
    condition_violated: str | None = None
    validation_failures: list[str] | None = None
    remediation: str | None = None
    details: dict[str, Any] | None = None
    failures_detailed: list[ValidationFailure] = field(default_factory=list)
    execution_metadata: dict[str, Any] = field(default_factory=dict)
    diagnostics: dict[str, Any] = field(default_factory=dict)


def check_failure_condition(
    result: dict[str, Any], condition: str
) -> tuple[bool, ValidationFailure | None]:
    """
    Check if a failure condition is met with detailed diagnostics.

    Args:
        result: Analysis result dict
        condition: Condition string (e.g., 'missing_currency', 'negative_amount')

    Returns:
        Tuple of (condition_met, failure_details)
    """
    if condition.startswith("missing_"):
        field = condition[8:]
        is_missing = field not in result or result.get(field) is None
        if is_missing:
            failure = ValidationFailure(
                failure_type="missing_field",
                field_name=field,
                expected="non-null value",
                actual=result.get(field),
                severity="error",
                message=f"Required field '{field}' is missing or null",
                remediation=f"Extract {field} from source document. Check pattern matching rules for {field} extraction.",
                context={"condition": condition, "available_fields": list(result.keys())},
            )
            return True, failure
        return False, None

    elif condition.startswith("negative_"):
        field = condition[9:]
        value = result.get(field)
        if value is None:
            return False, None
        try:
            is_negative = float(value) < 0
            if is_negative:
                failure = ValidationFailure(
                    failure_type="invalid_value",
                    field_name=field,
                    expected="positive value",
                    actual=value,
                    severity="error",
                    message=f"Field '{field}' has negative value: {value}",
                    remediation=f"Verify {field} extraction logic. Negative values may indicate parsing error or incorrect pattern matching.",
                    context={"condition": condition, "parsed_value": value},
                )
                return True, failure
        except (ValueError, TypeError) as e:
            failure = ValidationFailure(
                failure_type="type_error",
                field_name=field,
                expected="numeric value",
                actual=value,
                severity="error",
                message=f"Field '{field}' cannot be converted to number: {e}",
                remediation=f"Check {field} format in source document. Ensure numeric extraction patterns are correct.",
                context={"condition": condition, "error": str(e)},
            )
            return True, failure
        return False, None

    elif condition.startswith("empty_"):
        field = condition[6:]
        value = result.get(field)
        is_empty = not value or (isinstance(value, list | dict | str) and len(value) == 0)
        if is_empty:
            failure = ValidationFailure(
                failure_type="empty_field",
                field_name=field,
                expected="non-empty value",
                actual=value,
                severity="warning",
                message=f"Field '{field}' is empty",
                remediation=f"No data extracted for {field}. Verify pattern matching or check if field exists in source document.",
                context={"condition": condition, "value_type": type(value).__name__},
            )
            return True, failure
        return False, None

    elif condition == "invalid_format":
        is_invalid = result.get("format_valid", True) is False
        if is_invalid:
            failure = ValidationFailure(
                failure_type="format_validation",
                field_name="format_valid",
                expected=True,
                actual=False,
                severity="error",
                message="Data format validation failed",
                remediation="Review extraction logic and validate against expected format. Check pattern matching rules.",
                context={"condition": condition},
            )
            return True, failure
        return False, None

    elif condition == "low_confidence":
        confidence = result.get("confidence", 1.0)
        is_low = confidence < 0.5
        if is_low:
            failure = ValidationFailure(
                failure_type="low_confidence",
                field_name="confidence",
                expected="≥0.5",
                actual=confidence,
                severity="warning",
                message=f"Pattern match confidence ({confidence:.2f}) below threshold",
                remediation=f"Review source quality and pattern matching. Confidence {confidence:.2f} suggests weak evidence. Consider manual review.",
                context={"condition": condition, "threshold": 0.5},
            )
            return True, failure
        return False, None

    elif condition.startswith("threshold_"):
        parts = condition.split("_", 2)
        if len(parts) >= 3:
            field = parts[2]
            value = result.get(field)
            if value is not None:
                try:
                    threshold = result.get(f"{field}_threshold", 0.7)
                    is_below = float(value) < float(threshold)
                    if is_below:
                        failure = ValidationFailure(
                            failure_type="threshold_violation",
                            field_name=field,
                            expected=f"≥{threshold}",
                            actual=value,
                            severity="warning",
                            message=f"Field '{field}' ({value}) below threshold ({threshold})",
                            remediation=f"Improve {field} quality or adjust threshold. Current value suggests weak evidence.",
                            context={"condition": condition, "threshold": threshold},
                        )
                        return True, failure
                except (ValueError, TypeError):
                    pass
        return False, None

    logger.warning("unknown_failure_condition", condition=condition)
    return False, None


def execute_failure_contract(
    result: dict[str, Any], failure_contract: dict[str, Any], question_id: str | None = None
) -> ValidationResult:
    """
    Execute failure contract checks on analysis result with detailed diagnostics.

    Args:
        result: Analysis result to validate
        failure_contract: Contract from signal node, e.g.:
            {
                'abort_if': ['missing_currency', 'negative_amount'],
                'emit_code': 'ERR_BUDGET_INVALID_Q047',
                'severity': 'error'
            }
        question_id: Optional question ID for context

    Returns:
        ValidationResult with comprehensive failure details
    """
    abort_conditions = failure_contract.get("abort_if", [])
    error_code = failure_contract.get("emit_code", "ERR_UNKNOWN")
    severity = failure_contract.get("severity", "error")

    detailed_failures = []
    violated_conditions = []

    for condition in abort_conditions:
        is_met, failure_detail = check_failure_condition(result, condition)
        if is_met and failure_detail:
            violated_conditions.append(condition)
            detailed_failures.append(failure_detail)

            logger.warning(
                "failure_contract_violated",
                condition=condition,
                error_code=error_code,
                field=failure_detail.field_name,
                question_id=question_id,
                remediation=failure_detail.remediation,
            )

    if detailed_failures:
        detailed_failures[0]
        all_remediations = [f.remediation for f in detailed_failures]
        combined_remediation = (
            f"Contract {error_code} violated. "
            f"{len(detailed_failures)} condition(s) failed:\n"
            + "\n".join([f"  - {f.message}" for f in detailed_failures])
            + "\n\nRemediation steps:\n"
            + "\n".join([f"  {i+1}. {r}" for i, r in enumerate(all_remediations)])
        )

        diagnostics = {
            "total_conditions_checked": len(abort_conditions),
            "conditions_failed": len(violated_conditions),
            "conditions_passed": len(abort_conditions) - len(violated_conditions),
            "severity": severity,
            "question_id": question_id,
            "failure_summary": {
                "missing_fields": [
                    f.field_name for f in detailed_failures if f.failure_type == "missing_field"
                ],
                "invalid_values": [
                    f.field_name for f in detailed_failures if f.failure_type == "invalid_value"
                ],
                "empty_fields": [
                    f.field_name for f in detailed_failures if f.failure_type == "empty_field"
                ],
                "other_failures": [
                    f.field_name
                    for f in detailed_failures
                    if f.failure_type not in ["missing_field", "invalid_value", "empty_field"]
                ],
            },
        }

        return ValidationResult(
            status="failed",
            passed=False,
            error_code=error_code,
            condition_violated=", ".join(violated_conditions),
            validation_failures=[f.message for f in detailed_failures],
            remediation=combined_remediation,
            details=result,
            failures_detailed=detailed_failures,
            diagnostics=diagnostics,
            execution_metadata={
                "contract_type": "failure_contract",
                "conditions_evaluated": abort_conditions,
                "severity": severity,
            },
        )

    return ValidationResult(
        status="success",
        passed=True,
        diagnostics={
            "total_conditions_checked": len(abort_conditions),
            "conditions_failed": 0,
            "conditions_passed": len(abort_conditions),
            "severity": severity,
            "question_id": question_id,
        },
        execution_metadata={
            "contract_type": "failure_contract",
            "conditions_evaluated": abort_conditions,
        },
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
    if condition.startswith("missing_"):
        field = condition[8:]
        return f"Check source document for {field} field. May require manual extraction."

    elif condition.startswith("negative_"):
        field = condition[9:]
        return f"Verify {field} value. Negative values may indicate parsing error."

    elif condition.startswith("empty_"):
        field = condition[6:]
        return f"No data extracted for {field}. Check pattern matching or source quality."

    elif condition == "invalid_format":
        return "Data format validation failed. Review extraction logic."

    elif condition == "low_confidence":
        confidence = result.get("confidence", 0)
        return (
            f"Pattern match confidence ({confidence:.2f}) below threshold. Consider manual review."
        )

    return "Review analysis result and source document."


def execute_validations(
    result: dict[str, Any], validations: dict[str, Any], question_id: str | None = None
) -> dict[str, Any]:
    """
    Execute validation rules on result with detailed diagnostics.

    Args:
        result: Analysis result
        validations: Validation spec from signal node, e.g.:
            {
                'rules': ['currency_present', 'amount_positive'],
                'thresholds': {'confidence': 0.7},
                'required_fields': ['amount', 'currency']
            }
        question_id: Optional question ID for context

    Returns:
        Dict with comprehensive validation results
    """
    failures = []
    detailed_failures = []
    passed_checks = []

    required_fields = validations.get("required_fields", [])
    for field in required_fields:
        if field not in result or result[field] is None:
            msg = f"Required field missing: {field}"
            failures.append(msg)
            detailed_failures.append(
                ValidationFailure(
                    failure_type="missing_required_field",
                    field_name=field,
                    expected="non-null value",
                    actual=result.get(field),
                    severity="error",
                    message=msg,
                    remediation=f"Ensure {field} is extracted from source document. Check extraction patterns for {field}.",
                    context={"validation_type": "required_field", "question_id": question_id},
                )
            )
        else:
            passed_checks.append(f"Required field present: {field}")

    thresholds = validations.get("thresholds", {})
    for key, min_value in thresholds.items():
        actual_value = result.get(key)
        if actual_value is None:
            msg = f"Threshold field missing: {key}"
            failures.append(msg)
            detailed_failures.append(
                ValidationFailure(
                    failure_type="missing_threshold_field",
                    field_name=key,
                    expected=f"value ≥ {min_value}",
                    actual=None,
                    severity="error",
                    message=msg,
                    remediation=f"Field {key} required for threshold check. Ensure it is included in result.",
                    context={
                        "validation_type": "threshold",
                        "threshold": min_value,
                        "question_id": question_id,
                    },
                )
            )
        else:
            try:
                if float(actual_value) < float(min_value):
                    msg = f"{key} ({actual_value}) below threshold ({min_value})"
                    failures.append(msg)
                    detailed_failures.append(
                        ValidationFailure(
                            failure_type="threshold_violation",
                            field_name=key,
                            expected=f"≥ {min_value}",
                            actual=actual_value,
                            severity="warning",
                            message=msg,
                            remediation=f"Improve {key} quality to meet threshold {min_value}. Current: {actual_value}",
                            context={
                                "validation_type": "threshold",
                                "threshold": min_value,
                                "question_id": question_id,
                            },
                        )
                    )
                else:
                    passed_checks.append(f"Threshold met: {key} ({actual_value}) ≥ {min_value}")
            except (ValueError, TypeError) as e:
                msg = f"Invalid value for {key}: {actual_value}"
                failures.append(msg)
                detailed_failures.append(
                    ValidationFailure(
                        failure_type="type_error",
                        field_name=key,
                        expected="numeric value",
                        actual=actual_value,
                        severity="error",
                        message=msg,
                        remediation=f"Ensure {key} is properly formatted as a number. Current type: {type(actual_value).__name__}",
                        context={
                            "validation_type": "threshold",
                            "error": str(e),
                            "question_id": question_id,
                        },
                    )
                )

    rules = validations.get("rules", [])
    for rule in rules:
        rule_passed, rule_failure = validate_rule_detailed(rule, result, question_id)
        if not rule_passed and rule_failure:
            failures.append(rule_failure.message)
            detailed_failures.append(rule_failure)
        elif rule_passed:
            passed_checks.append(f"Rule passed: {rule}")

    total_checks = len(required_fields) + len(thresholds) + len(rules)

    return {
        "all_passed": len(failures) == 0,
        "passed_count": len(passed_checks),
        "failed_count": len(failures),
        "failures": failures,
        "detailed_failures": detailed_failures,
        "passed_checks": passed_checks,
        "diagnostics": {
            "total_checks": total_checks,
            "required_fields_checked": len(required_fields),
            "thresholds_checked": len(thresholds),
            "rules_checked": len(rules),
            "question_id": question_id,
        },
    }


def validate_rule(rule: str, result: dict[str, Any]) -> bool:
    """
    Validate a specific rule against result (legacy interface).

    Args:
        rule: Rule name (e.g., 'currency_present', 'amount_positive')
        result: Analysis result

    Returns:
        True if rule passes
    """
    passed, _ = validate_rule_detailed(rule, result)
    return passed


def validate_rule_detailed(
    rule: str, result: dict[str, Any], question_id: str | None = None
) -> tuple[bool, ValidationFailure | None]:
    """
    Validate a specific rule with detailed diagnostics.

    Args:
        rule: Rule name (e.g., 'currency_present', 'amount_positive')
        result: Analysis result
        question_id: Optional question ID for context

    Returns:
        Tuple of (rule_passed, failure_detail)
    """
    if rule == "currency_present":
        currency = result.get("currency")
        passed = currency is not None and currency != ""
        if not passed:
            return False, ValidationFailure(
                failure_type="rule_validation",
                field_name="currency",
                expected="non-empty currency code",
                actual=currency,
                severity="error",
                message="Rule 'currency_present' failed: currency is missing or empty",
                remediation="Extract currency code from budget information. Check for ISO 4217 codes (USD, EUR, COP, etc.).",
                context={"rule": rule, "question_id": question_id},
            )
        return True, None

    elif rule == "amount_positive":
        amount = result.get("amount")
        if amount is None:
            return False, ValidationFailure(
                failure_type="rule_validation",
                field_name="amount",
                expected="positive number",
                actual=None,
                severity="error",
                message="Rule 'amount_positive' failed: amount is missing",
                remediation="Extract numeric amount from document. Verify extraction patterns capture monetary values.",
                context={"rule": rule, "question_id": question_id},
            )
        try:
            passed = float(amount) > 0
            if not passed:
                return False, ValidationFailure(
                    failure_type="rule_validation",
                    field_name="amount",
                    expected="positive number",
                    actual=amount,
                    severity="error",
                    message=f"Rule 'amount_positive' failed: amount ({amount}) is not positive",
                    remediation="Verify amount extraction. Negative/zero values indicate parsing errors or invalid source data.",
                    context={"rule": rule, "question_id": question_id},
                )
            return True, None
        except (ValueError, TypeError) as e:
            return False, ValidationFailure(
                failure_type="rule_validation",
                field_name="amount",
                expected="numeric value",
                actual=amount,
                severity="error",
                message=f"Rule 'amount_positive' failed: cannot convert amount to number - {e}",
                remediation=f"Ensure amount is numeric. Current type: {type(amount).__name__}. Check extraction format.",
                context={"rule": rule, "error": str(e), "question_id": question_id},
            )

    elif rule == "date_valid":
        date = result.get("date")
        passed = date is not None and len(str(date)) >= 4
        if not passed:
            return False, ValidationFailure(
                failure_type="rule_validation",
                field_name="date",
                expected="valid date string (≥4 chars)",
                actual=date,
                severity="warning",
                message="Rule 'date_valid' failed: date is missing or too short",
                remediation="Extract date from document. Look for YYYY, YYYY-MM-DD, or other standard formats.",
                context={"rule": rule, "question_id": question_id},
            )
        return True, None

    elif rule == "confidence_high":
        confidence = result.get("confidence", 0)
        passed = confidence >= 0.8
        if not passed:
            return False, ValidationFailure(
                failure_type="rule_validation",
                field_name="confidence",
                expected="≥0.8",
                actual=confidence,
                severity="warning",
                message=f"Rule 'confidence_high' failed: confidence ({confidence}) below 0.8",
                remediation=f"Low confidence ({confidence}) suggests weak evidence. Review source quality and pattern matching.",
                context={"rule": rule, "threshold": 0.8, "question_id": question_id},
            )
        return True, None

    elif rule == "completeness_check":
        completeness = result.get("completeness", 0)
        passed = completeness >= 0.7
        if not passed:
            return False, ValidationFailure(
                failure_type="rule_validation",
                field_name="completeness",
                expected="≥0.7",
                actual=completeness,
                severity="warning",
                message=f"Rule 'completeness_check' failed: completeness ({completeness}) below 0.7",
                remediation=f"Result incomplete ({completeness:.1%}). Check missing_elements field for details on what's lacking.",
                context={"rule": rule, "threshold": 0.7, "question_id": question_id},
            )
        return True, None

    logger.debug("unknown_validation_rule", rule=rule, question_id=question_id)
    return True, None


def validate_with_contract(result: dict[str, Any], signal_node: dict[str, Any]) -> ValidationResult:
    """
    Full validation using both failure_contract and validations with comprehensive diagnostics.

    This is the main entry point for contract-driven validation of all 300 micro-questions.
    Each validation provides detailed failure diagnostics and remediation suggestions.

    Args:
        result: Analysis result to validate
        signal_node: Signal node with failure_contract and validations, plus:
            - id: Question ID for tracking
            - expected_elements: List of expected fields
            - validations: Validation rules dict
            - failure_contract: Critical failure conditions

    Returns:
        ValidationResult with comprehensive validation status and diagnostics

    Example:
        >>> result = {'amount': 1000, 'currency': None}
        >>> node = {
        ...     'id': 'Q047',
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
        >>> print(validation.remediation)
        Contract ERR_BUDGET_001 violated...
    """
    question_id = signal_node.get("id", "UNKNOWN")
    all_detailed_failures = []

    failure_contract = signal_node.get("failure_contract")
    if failure_contract:
        contract_result = execute_failure_contract(result, failure_contract, question_id)
        if not contract_result.passed:
            logger.error(
                "contract_validation_failed",
                question_id=question_id,
                error_code=contract_result.error_code,
                conditions_violated=contract_result.condition_violated,
                failures_count=len(contract_result.failures_detailed),
            )
            return contract_result
        all_detailed_failures.extend(contract_result.failures_detailed)

    validations = signal_node.get("validations")
    if validations:
        validation_results = execute_validations(result, validations, question_id)

        if not validation_results["all_passed"]:
            all_detailed_failures.extend(validation_results.get("detailed_failures", []))

            remediation_steps = []
            for failure in validation_results.get("detailed_failures", []):
                remediation_steps.append(f"- {failure.remediation}")

            combined_remediation = (
                f"Validation failed for question {question_id}.\n"
                f"{validation_results['failed_count']} check(s) failed:\n"
                + "\n".join([f"  - {msg}" for msg in validation_results["failures"][:5]])
                + "\n\nRemediation steps:\n"
                + "\n".join(remediation_steps[:5])
            )

            logger.warning(
                "validation_checks_failed",
                question_id=question_id,
                failed_count=validation_results["failed_count"],
                passed_count=validation_results["passed_count"],
            )

            return ValidationResult(
                status="invalid",
                passed=False,
                validation_failures=validation_results["failures"],
                remediation=combined_remediation,
                details=result,
                failures_detailed=validation_results.get("detailed_failures", []),
                diagnostics=validation_results.get("diagnostics", {}),
                execution_metadata={
                    "contract_type": "validations",
                    "question_id": question_id,
                    "total_checks": validation_results["diagnostics"]["total_checks"],
                },
            )

    logger.info(
        "contract_validation_passed",
        question_id=question_id,
        failure_contract_checked=failure_contract is not None,
        validations_checked=validations is not None,
    )

    return ValidationResult(
        status="success",
        passed=True,
        details=result,
        diagnostics={
            "question_id": question_id,
            "failure_contract_checked": failure_contract is not None,
            "validations_checked": validations is not None,
            "all_checks_passed": True,
        },
        execution_metadata={"question_id": question_id, "validation_complete": True},
    )


class ValidationOrchestrator:
    """
    Orchestrates validation for all 300 micro-questions with comprehensive tracking.

    This class ensures every question validation is executed, tracked, and reported
    with detailed diagnostics and remediation suggestions.

    Features:
    - Automatic registration of all validation executions
    - Detailed failure tracking with remediation suggestions
    - Comprehensive reporting and metrics
    - Integration with validate_with_contract for 600 contract specifications
    - Real-time validation coverage monitoring
    - Prioritized remediation recommendations
    - Multiple export formats (JSON, CSV, Markdown)
    - Error code frequency analysis
    - Severity distribution tracking

    Usage:
        >>> orchestrator = ValidationOrchestrator(expected_question_count=300)
        >>> orchestrator.start_orchestration()
        >>>
        >>> # Process all questions (validation happens in executors)
        >>> results = process_all_questions(...)
        >>>
        >>> # Complete and get comprehensive report
        >>> orchestrator.complete_orchestration()
        >>> report = orchestrator.get_remediation_report()
        >>> print(report)
        >>>
        >>> # Export for external analysis
        >>> json_data = orchestrator.export_validation_results('json')
        >>> csv_data = orchestrator.export_validation_results('csv')
    """

    def __init__(self, expected_question_count: int = 300) -> None:
        self.validation_registry: dict[str, ValidationResult] = {}
        self.total_questions = expected_question_count
        self.validated_count = 0
        self.passed_count = 0
        self.failed_count = 0
        self.invalid_count = 0
        self.skipped_count = 0
        self.error_count = 0
        self._execution_order: list[str] = []
        self._start_time: float | None = None
        self._end_time: float | None = None

    def start_orchestration(self) -> None:
        """Mark the start of validation orchestration."""
        import time

        self._start_time = time.perf_counter()
        logger.info("validation_orchestration_started", expected_questions=self.total_questions)

    def complete_orchestration(self) -> None:
        """Mark the completion of validation orchestration."""
        import time

        self._end_time = time.perf_counter()
        duration = (self._end_time - self._start_time) if self._start_time else 0.0

        logger.info(
            "validation_orchestration_completed",
            validated=self.validated_count,
            passed=self.passed_count,
            failed=self.failed_count,
            invalid=self.invalid_count,
            skipped=self.skipped_count,
            duration_s=duration,
            completion_rate=(
                self.validated_count / self.total_questions if self.total_questions > 0 else 0
            ),
        )

    def register_validation(self, question_id: str, validation_result: ValidationResult) -> None:
        """
        Register a validation result for tracking.

        Args:
            question_id: Question identifier
            validation_result: Validation result to register
        """
        if question_id in self.validation_registry:
            logger.warning(
                "validation_duplicate_registration",
                question_id=question_id,
                previous_status=self.validation_registry[question_id].status,
                new_status=validation_result.status,
            )

        self.validation_registry[question_id] = validation_result
        self._execution_order.append(question_id)
        self.validated_count += 1

        if validation_result.passed:
            self.passed_count += 1
        elif validation_result.status == "failed":
            self.failed_count += 1
        elif validation_result.status == "invalid":
            self.invalid_count += 1
        elif validation_result.status == "error":
            self.error_count += 1
        elif validation_result.status == "skipped":
            self.skipped_count += 1

        logger.debug(
            "validation_registered",
            question_id=question_id,
            status=validation_result.status,
            passed=validation_result.passed,
            error_code=validation_result.error_code,
        )

    def register_skipped(self, question_id: str, reason: str) -> None:
        """
        Register a skipped question with reason.

        Args:
            question_id: Question identifier
            reason: Reason for skipping
        """
        skipped_result = ValidationResult(
            status="skipped",
            passed=False,
            diagnostics={"skip_reason": reason, "question_id": question_id},
        )
        self.register_validation(question_id, skipped_result)

    def register_error(
        self, question_id: str, error: Exception, context: dict[str, Any] | None = None
    ) -> None:
        """
        Register a validation error.

        Args:
            question_id: Question identifier
            error: Exception that occurred
            context: Additional context information
        """
        error_result = ValidationResult(
            status="error",
            passed=False,
            error_code="VALIDATION_ERROR",
            remediation=f"Validation failed with error: {str(error)}. Check signal node configuration and result format.",
            diagnostics={
                "question_id": question_id,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context or {},
            },
        )
        self.register_validation(question_id, error_result)

    def validate_and_register(
        self, result: dict[str, Any], signal_node: dict[str, Any]
    ) -> ValidationResult:
        """
        Validate a result and register it in one step.

        Args:
            result: Analysis result to validate
            signal_node: Signal node with contracts

        Returns:
            ValidationResult
        """
        validation_result = validate_with_contract(result, signal_node)
        question_id = signal_node.get("id", "UNKNOWN")
        self.register_validation(question_id, validation_result)
        return validation_result

    def get_validation_summary(self) -> dict[str, Any]:
        """
        Get comprehensive validation summary across all questions.

        Returns:
            Summary dict with statistics and failed validations
        """
        failed_validations = {
            qid: result for qid, result in self.validation_registry.items() if not result.passed
        }

        failure_breakdown = {
            "missing_fields": [],
            "invalid_values": [],
            "empty_fields": [],
            "threshold_violations": [],
            "rule_failures": [],
            "other": [],
        }

        error_code_frequency: dict[str, int] = {}
        severity_counts: dict[str, int] = {"error": 0, "warning": 0, "info": 0}

        for qid, result in failed_validations.items():
            if result.error_code:
                error_code_frequency[result.error_code] = (
                    error_code_frequency.get(result.error_code, 0) + 1
                )

            for failure in result.failures_detailed:
                entry = {
                    "question_id": qid,
                    "field": failure.field_name,
                    "message": failure.message,
                    "severity": failure.severity,
                    "remediation": failure.remediation,
                }

                severity_counts[failure.severity] = severity_counts.get(failure.severity, 0) + 1

                if failure.failure_type in ("missing_field", "missing_required_field"):
                    failure_breakdown["missing_fields"].append(entry)
                elif failure.failure_type in ("invalid_value", "type_error"):
                    failure_breakdown["invalid_values"].append(entry)
                elif failure.failure_type == "empty_field":
                    failure_breakdown["empty_fields"].append(entry)
                elif failure.failure_type == "threshold_violation":
                    failure_breakdown["threshold_violations"].append(entry)
                elif failure.failure_type == "rule_validation":
                    failure_breakdown["rule_failures"].append(entry)
                else:
                    failure_breakdown["other"].append(entry)

        duration = (
            (self._end_time - self._start_time) if (self._start_time and self._end_time) else None
        )

        return {
            "total_questions_expected": self.total_questions,
            "validated_count": self.validated_count,
            "passed_count": self.passed_count,
            "failed_count": self.failed_count,
            "invalid_count": self.invalid_count,
            "skipped_count": self.skipped_count,
            "error_count": self.error_count,
            "completion_rate": (
                self.validated_count / self.total_questions if self.total_questions > 0 else 0
            ),
            "success_rate": (
                self.passed_count / self.validated_count if self.validated_count > 0 else 0
            ),
            "failure_rate": (
                self.failed_count / self.validated_count if self.validated_count > 0 else 0
            ),
            "failed_validations": {
                qid: result.error_code for qid, result in failed_validations.items()
            },
            "failure_breakdown": failure_breakdown,
            "error_code_frequency": error_code_frequency,
            "severity_counts": severity_counts,
            "validation_registry_size": len(self.validation_registry),
            "execution_order": self._execution_order,
            "duration_seconds": duration,
            "validations_per_second": (
                self.validated_count / duration if duration and duration > 0 else None
            ),
        }

    def get_failed_questions(self) -> dict[str, ValidationResult]:
        """Get all questions that failed validation."""
        return {
            qid: result for qid, result in self.validation_registry.items() if not result.passed
        }

    def get_remediation_report(
        self, include_all_details: bool = True, max_failures_per_question: int = 5
    ) -> str:
        """
        Generate a comprehensive remediation report for all failures.

        Args:
            include_all_details: If True, include all failure details
            max_failures_per_question: Maximum number of failures to show per question

        Returns:
            Formatted report string
        """
        failed = self.get_failed_questions()
        summary = self.get_validation_summary()

        if not failed:
            report_lines = [
                "=" * 80,
                "VALIDATION REMEDIATION REPORT",
                "=" * 80,
                f"Total Questions: {self.total_questions}",
                f"Validated: {self.validated_count}",
                f"Passed: {self.passed_count}",
                "",
                "✓ ALL VALIDATIONS PASSED - NO REMEDIATION NEEDED",
                "",
                "=" * 80,
            ]
            return "\n".join(report_lines)

        report_lines = [
            "=" * 80,
            "VALIDATION REMEDIATION REPORT",
            "=" * 80,
            f"Total Questions: {self.total_questions}",
            f"Validated: {self.validated_count}",
            f"Passed: {self.passed_count}",
            f"Failed: {self.failed_count}",
            f"Invalid: {self.invalid_count}",
            f"Skipped: {self.skipped_count}",
            f"Errors: {self.error_count}",
            "",
            f"Success Rate: {summary['success_rate']:.1%}",
            f"Completion Rate: {summary['completion_rate']:.1%}",
            "",
        ]

        if summary["duration_seconds"]:
            report_lines.append(f"Duration: {summary['duration_seconds']:.2f}s")
            report_lines.append(
                f"Throughput: {summary['validations_per_second']:.1f} validations/sec"
            )
            report_lines.append("")

        report_lines.extend(
            [
                "=" * 80,
                "FAILURE BREAKDOWN BY TYPE:",
                "=" * 80,
                f"  Missing Fields: {len(summary['failure_breakdown']['missing_fields'])}",
                f"  Invalid Values: {len(summary['failure_breakdown']['invalid_values'])}",
                f"  Empty Fields: {len(summary['failure_breakdown']['empty_fields'])}",
                f"  Threshold Violations: {len(summary['failure_breakdown']['threshold_violations'])}",
                f"  Rule Failures: {len(summary['failure_breakdown']['rule_failures'])}",
                f"  Other: {len(summary['failure_breakdown']['other'])}",
                "",
            ]
        )

        if summary["error_code_frequency"]:
            report_lines.extend(["ERROR CODE FREQUENCY:", ""])
            for error_code, count in sorted(
                summary["error_code_frequency"].items(), key=lambda x: x[1], reverse=True
            )[:10]:
                report_lines.append(f"  {error_code}: {count} occurrences")
            report_lines.append("")

        if summary["severity_counts"]:
            report_lines.extend(["SEVERITY DISTRIBUTION:", ""])
            for severity, count in sorted(
                summary["severity_counts"].items(), key=lambda x: x[1], reverse=True
            ):
                report_lines.append(f"  {severity.upper()}: {count}")
            report_lines.append("")

        report_lines.extend(["=" * 80, "FAILED VALIDATIONS (Detailed):", "=" * 80, ""])

        for qid, result in sorted(failed.items()):
            report_lines.append(f"Question: {qid}")
            report_lines.append(f"  Status: {result.status.upper()}")
            if result.error_code:
                report_lines.append(f"  Error Code: {result.error_code}")
            if result.condition_violated:
                report_lines.append(f"  Conditions Violated: {result.condition_violated}")
            report_lines.append("")

            if result.failures_detailed:
                report_lines.append("  Failures:")
                for i, failure in enumerate(result.failures_detailed[:max_failures_per_question]):
                    report_lines.append(f"    [{i+1}] {failure.message}")
                    report_lines.append(f"        Type: {failure.failure_type}")
                    report_lines.append(f"        Field: {failure.field_name}")
                    report_lines.append(f"        Severity: {failure.severity.upper()}")
                    if include_all_details:
                        report_lines.append(f"        Expected: {failure.expected}")
                        report_lines.append(f"        Actual: {failure.actual}")

                if len(result.failures_detailed) > max_failures_per_question:
                    remaining = len(result.failures_detailed) - max_failures_per_question
                    report_lines.append(f"    ... and {remaining} more failure(s)")
                report_lines.append("")

            if result.remediation:
                report_lines.append("  Remediation:")
                for line in result.remediation.split("\n"):
                    if line.strip():
                        report_lines.append(f"    {line.strip()}")
                report_lines.append("")

            if result.diagnostics and include_all_details:
                report_lines.append("  Diagnostics:")
                for key, value in result.diagnostics.items():
                    if key not in ["question_id"]:
                        report_lines.append(f"    {key}: {value}")
                report_lines.append("")

            report_lines.append("-" * 80)
            report_lines.append("")

        report_lines.extend(["=" * 80, "REMEDIATION PRIORITIES:", "=" * 80, ""])

        priorities = self._generate_remediation_priorities(summary)
        for priority in priorities:
            report_lines.append(f"  • {priority}")

        report_lines.extend(["", "=" * 80])

        return "\n".join(report_lines)

    def _generate_remediation_priorities(self, summary: dict[str, Any]) -> list[str]:
        """
        Generate prioritized remediation recommendations based on failure patterns.

        Args:
            summary: Validation summary dict

        Returns:
            List of prioritized remediation recommendations
        """
        priorities = []
        fb = summary["failure_breakdown"]

        if len(fb["missing_fields"]) > 10:
            priorities.append(
                f"HIGH PRIORITY: {len(fb['missing_fields'])} missing field failures. "
                "Review extraction patterns and ensure all required fields are extracted."
            )

        if len(fb["invalid_values"]) > 10:
            priorities.append(
                f"HIGH PRIORITY: {len(fb['invalid_values'])} invalid value failures. "
                "Verify data type conversions and format parsing logic."
            )

        if len(fb["threshold_violations"]) > 5:
            priorities.append(
                f"MEDIUM PRIORITY: {len(fb['threshold_violations'])} threshold violations. "
                "Consider adjusting confidence thresholds or improving pattern quality."
            )

        if len(fb["rule_failures"]) > 5:
            priorities.append(
                f"MEDIUM PRIORITY: {len(fb['rule_failures'])} rule validation failures. "
                "Review validation rules for appropriateness and adjust as needed."
            )

        if len(fb["empty_fields"]) > 5:
            priorities.append(
                f"LOW PRIORITY: {len(fb['empty_fields'])} empty field warnings. "
                "These may be acceptable if fields are truly absent in source documents."
            )

        error_codes = summary.get("error_code_frequency", {})
        if error_codes:
            most_frequent = max(error_codes.items(), key=lambda x: x[1])
            if most_frequent[1] > 5:
                priorities.append(
                    f"INVESTIGATE: Error code '{most_frequent[0]}' occurred {most_frequent[1]} times. "
                    "This indicates a systematic issue requiring immediate attention."
                )

        if not priorities:
            priorities.append(
                "All failures are unique. Review individual remediation suggestions above."
            )

        return priorities

    def reset(self) -> None:
        """Reset the orchestrator state."""
        self.validation_registry.clear()
        self._execution_order.clear()
        self.validated_count = 0
        self.passed_count = 0
        self.failed_count = 0
        self.invalid_count = 0
        self.skipped_count = 0
        self.error_count = 0
        self._start_time = None
        self._end_time = None

    def get_missing_questions(self, expected_question_ids: list[str] | None = None) -> list[str]:
        """
        Identify questions that were expected but not validated.

        Args:
            expected_question_ids: List of expected question IDs (optional)

        Returns:
            List of missing question IDs
        """
        if not expected_question_ids:
            return []

        validated_ids = set(self.validation_registry.keys())
        expected_ids = set(expected_question_ids)
        missing = expected_ids - validated_ids

        if missing:
            logger.warning(
                "validation_missing_questions",
                missing_count=len(missing),
                expected_count=len(expected_ids),
                validated_count=len(validated_ids),
                missing_sample=list(missing)[:10],
            )

        return sorted(missing)

    def get_validation_coverage_report(
        self, expected_question_ids: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Generate a coverage report showing which questions were validated.

        Args:
            expected_question_ids: List of expected question IDs

        Returns:
            Coverage report dict
        """
        missing = self.get_missing_questions(expected_question_ids)

        return {
            "total_expected": (
                len(expected_question_ids) if expected_question_ids else self.total_questions
            ),
            "total_validated": len(self.validation_registry),
            "missing_count": len(missing),
            "missing_questions": missing,
            "coverage_percentage": (
                (len(self.validation_registry) / len(expected_question_ids) * 100)
                if expected_question_ids
                else 0
            ),
            "validation_statuses": {
                "passed": self.passed_count,
                "failed": self.failed_count,
                "invalid": self.invalid_count,
                "skipped": self.skipped_count,
                "error": self.error_count,
            },
        }

    def export_validation_results(self, format: str = "json") -> str | dict[str, Any]:
        """
        Export validation results in specified format.

        Args:
            format: Export format ('json', 'csv', or 'markdown')

        Returns:
            Formatted export string or dict
        """
        if format == "json":
            return self._export_json()
        elif format == "csv":
            return self._export_csv()
        elif format == "markdown":
            return self._export_markdown()
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _export_json(self) -> dict[str, Any]:
        """Export validation results as JSON-serializable dict."""
        return {
            "summary": self.get_validation_summary(),
            "validations": {
                qid: {
                    "status": result.status,
                    "passed": result.passed,
                    "error_code": result.error_code,
                    "condition_violated": result.condition_violated,
                    "validation_failures": result.validation_failures,
                    "remediation": result.remediation,
                    "diagnostics": result.diagnostics,
                    "failure_count": len(result.failures_detailed),
                    "failures": [
                        {
                            "type": f.failure_type,
                            "field": f.field_name,
                            "message": f.message,
                            "severity": f.severity,
                            "remediation": f.remediation,
                            "expected": str(f.expected),
                            "actual": str(f.actual),
                        }
                        for f in result.failures_detailed
                    ],
                }
                for qid, result in self.validation_registry.items()
            },
        }

    def _export_csv(self) -> str:
        """Export validation results as CSV string."""
        lines = ["question_id,status,passed,error_code,failure_count,severity,condition_violated"]

        for qid, result in sorted(self.validation_registry.items()):
            severity = "none"
            if result.failures_detailed:
                severities = [f.severity for f in result.failures_detailed]
                if "error" in severities:
                    severity = "error"
                elif "warning" in severities:
                    severity = "warning"

            lines.append(
                f"{qid},{result.status},{result.passed},{result.error_code or ''},"
                f"{len(result.failures_detailed)},{severity},{result.condition_violated or ''}"
            )

        return "\n".join(lines)

    def _export_markdown(self) -> str:
        """Export validation results as Markdown table."""
        lines = [
            "# Validation Results",
            "",
            "## Summary",
            "",
            f"- **Total Expected**: {self.total_questions}",
            f"- **Validated**: {self.validated_count}",
            f"- **Passed**: {self.passed_count}",
            f"- **Failed**: {self.failed_count}",
            f"- **Invalid**: {self.invalid_count}",
            (
                f"- **Success Rate**: {self.passed_count / self.validated_count * 100:.1f}%"
                if self.validated_count > 0
                else "- **Success Rate**: N/A"
            ),
            "",
            "## Failed Validations",
            "",
            "| Question ID | Status | Error Code | Failures | Remediation |",
            "|-------------|--------|------------|----------|-------------|",
        ]

        failed = self.get_failed_questions()
        for qid, result in sorted(failed.items()):
            failure_count = len(result.failures_detailed)
            error_code = result.error_code or "N/A"
            remediation = (
                (result.remediation or "None")[:50] + "..."
                if result.remediation and len(result.remediation) > 50
                else (result.remediation or "None")
            )

            lines.append(
                f"| {qid} | {result.status} | {error_code} | {failure_count} | {remediation} |"
            )

        return "\n".join(lines)


def validate_result_with_orchestrator(
    result: dict[str, Any],
    signal_node: dict[str, Any],
    orchestrator: ValidationOrchestrator | None = None,
    auto_register: bool = True,
) -> ValidationResult:
    """
    Validate a result and optionally register it with the orchestrator.

    This is the recommended entry point for validation that ensures proper
    tracking and registration of all validation executions.

    Args:
        result: Analysis result to validate
        signal_node: Signal node with contracts
        orchestrator: Optional ValidationOrchestrator instance
        auto_register: If True and orchestrator provided, automatically register result

    Returns:
        ValidationResult

    Example:
        >>> orchestrator = ValidationOrchestrator(expected_question_count=300)
        >>> orchestrator.start_orchestration()
        >>>
        >>> for question in all_questions:
        ...     result = analyze_question(question)
        ...     validation = validate_result_with_orchestrator(
        ...         result, question, orchestrator, auto_register=True
        ...     )
        ...     if not validation.passed:
        ...         print(f"Failed: {validation.error_code}")
        ...
        >>> orchestrator.complete_orchestration()
        >>> print(orchestrator.get_remediation_report())
    """
    question_id = signal_node.get("id", "UNKNOWN")

    try:
        validation_result = validate_with_contract(result, signal_node)

        if orchestrator and auto_register:
            orchestrator.register_validation(question_id, validation_result)

        return validation_result

    except Exception as e:
        logger.error(
            "validation_execution_error", question_id=question_id, error=str(e), exc_info=True
        )

        error_result = ValidationResult(
            status="error",
            passed=False,
            error_code="VALIDATION_EXECUTION_ERROR",
            remediation=f"Validation execution failed: {str(e)}",
            diagnostics={
                "question_id": question_id,
                "error_type": type(e).__name__,
                "error_message": str(e),
            },
        )

        if orchestrator and auto_register:
            orchestrator.register_error(question_id, e)

        return error_result


def validate_batch_results(
    results: list[tuple[dict[str, Any], dict[str, Any]]],
    orchestrator: ValidationOrchestrator | None = None,
    continue_on_error: bool = True,
) -> list[ValidationResult]:
    """
    Validate a batch of results with their corresponding signal nodes.

    Args:
        results: List of (result, signal_node) tuples
        orchestrator: Optional ValidationOrchestrator for tracking
        continue_on_error: If True, continue validation even if errors occur

    Returns:
        List of ValidationResult objects

    Example:
        >>> results_with_nodes = [
        ...     (result1, signal_node1),
        ...     (result2, signal_node2),
        ...     ...
        ... ]
        >>> orchestrator = ValidationOrchestrator(expected_question_count=300)
        >>> orchestrator.start_orchestration()
        >>>
        >>> validations = validate_batch_results(
        ...     results_with_nodes,
        ...     orchestrator=orchestrator
        ... )
        >>>
        >>> orchestrator.complete_orchestration()
        >>> failed = [v for v in validations if not v.passed]
        >>> print(f"Failed: {len(failed)}/{len(validations)}")
    """
    validation_results = []

    for result, signal_node in results:
        try:
            validation = validate_result_with_orchestrator(
                result=result,
                signal_node=signal_node,
                orchestrator=orchestrator,
                auto_register=True,
            )
            validation_results.append(validation)
        except Exception as e:
            if not continue_on_error:
                raise

            question_id = signal_node.get("id", "UNKNOWN")
            logger.error(
                "batch_validation_error", question_id=question_id, error=str(e), exc_info=True
            )

            error_result = ValidationResult(
                status="error",
                passed=False,
                error_code="BATCH_VALIDATION_ERROR",
                remediation=f"Batch validation error: {str(e)}",
                diagnostics={
                    "question_id": question_id,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                },
            )
            validation_results.append(error_result)

            if orchestrator:
                orchestrator.register_error(question_id, e)

    return validation_results


def ensure_complete_validation_coverage(
    expected_question_ids: list[str], orchestrator: ValidationOrchestrator
) -> dict[str, Any]:
    """
    Ensure all expected questions have been validated.

    This function checks validation coverage and logs warnings for missing validations.
    Use this at the end of processing to ensure 100% validation coverage.

    Args:
        expected_question_ids: List of all expected question IDs
        orchestrator: ValidationOrchestrator instance

    Returns:
        Coverage report dict

    Example:
        >>> expected_ids = [f"Q{i:03d}" for i in range(1, 301)]
        >>> coverage = ensure_complete_validation_coverage(
        ...     expected_ids,
        ...     orchestrator
        ... )
        >>>
        >>> if coverage['missing_count'] > 0:
        ...     print(f"WARNING: {coverage['missing_count']} questions not validated")
        ...     print(f"Missing: {coverage['missing_questions'][:10]}")
    """
    coverage = orchestrator.get_validation_coverage_report(expected_question_ids)

    if coverage["missing_count"] > 0:
        logger.warning(
            "incomplete_validation_coverage",
            expected=coverage["total_expected"],
            validated=coverage["total_validated"],
            missing=coverage["missing_count"],
            coverage_pct=coverage["coverage_percentage"],
            missing_sample=coverage["missing_questions"][:20],
        )

        # Register skipped entries for missing questions
        for question_id in coverage["missing_questions"]:
            orchestrator.register_skipped(
                question_id=question_id, reason="Question was not processed or executed"
            )
    else:
        logger.info(
            "complete_validation_coverage",
            total_validated=coverage["total_validated"],
            coverage_pct=100.0,
        )

    return coverage


# === EXPORTS ===

__all__ = [
    "ValidationFailure",
    "ValidationResult",
    "ValidationOrchestrator",
    "check_failure_condition",
    "execute_failure_contract",
    "execute_validations",
    "validate_with_contract",
    "validate_rule",
    "validate_rule_detailed",
    "validate_result_with_orchestrator",
    "validate_batch_results",
    "ensure_complete_validation_coverage",
    "get_global_validation_orchestrator",
    "set_global_validation_orchestrator",
    "reset_global_validation_orchestrator",
]

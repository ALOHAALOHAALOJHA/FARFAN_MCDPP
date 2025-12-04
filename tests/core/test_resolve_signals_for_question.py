"""Comprehensive unit test suite for _resolve_signals_for_question.

This module tests the _resolve_signals_for_question method with:
- Signal requirement normalization (missing key, None value)
- Successful resolution with all signals available
- Hard-fail semantics for missing signals
- Registry contract validation
- Signal structure validation
- Duplicate signal type handling
- Immutability guarantees
- Dataclass and dict signal access
- Correlation ID propagation
"""

import logging
from typing import Any
from unittest.mock import Mock

import pytest
import structlog
from structlog.testing import LogCapture


def _extract_signal_type(sig: Any, idx: int) -> str:
    """Extract signal type from signal object or dict."""
    if hasattr(sig, "signal_type"):
        return sig.signal_type
    if isinstance(sig, dict):
        if "signal_type" in sig:
            return sig["signal_type"]
        if "signal_id" in sig:
            return sig["signal_id"]
        raise ValueError(
            f"Signal at index {idx} missing field signal_id or signal_type"
        )
    sig_type = getattr(sig, "signal_id", None)
    if sig_type is None:
        raise ValueError(f"Signal at index {idx} missing field signal_id")
    return sig_type


def _normalize_signal_requirements(signal_requirements: Any) -> set[str]:
    """Normalize signal requirements to a set."""
    if signal_requirements is None or not signal_requirements:
        return set()
    if not isinstance(signal_requirements, set | list | tuple):
        return set()
    return (
        set(signal_requirements)
        if isinstance(signal_requirements, list | tuple)
        else signal_requirements
    )


def _resolve_signals_for_question(
    question: dict[str, Any],
    chunk_id: str,
    signal_registry: Any,
    correlation_id: str,
) -> tuple[Any, ...]:
    """Resolve signals for a micro-question context.

    Args:
        question: Question dict with optional signal_requirements field
        chunk_id: Chunk identifier for logging
        signal_registry: Registry with get_signals_for_chunk method
        correlation_id: Correlation ID for tracing

    Returns:
        Immutable tuple of resolved signals

    Raises:
        ValueError: When required signals are missing
        TypeError: When registry returns None (contract violation)
        ValueError: When signal structure is invalid
    """
    logger = structlog.get_logger(__name__)

    required_types = _normalize_signal_requirements(question.get("signal_requirements"))

    if not required_types:
        return ()

    signals = signal_registry.get_signals_for_chunk(chunk_id, required_types)

    if signals is None:
        raise TypeError(
            f"Signal registry returned None for chunk {chunk_id}, violating contract. "
            "Expected list or tuple of signals."
        )

    resolved_types = {_extract_signal_type(sig, idx) for idx, sig in enumerate(signals)}

    missing_signals = required_types - resolved_types

    if missing_signals:
        sorted_missing = sorted(missing_signals)
        question_id = question.get("question_id", "UNKNOWN")
        raise ValueError(
            f"Synchronization Failure for MQC {question_id}: "
            f"Missing required signals {set(sorted_missing)} for chunk {chunk_id}"
        )

    duplicate_types = {}
    for sig in signals:
        sig_type = (
            sig.signal_type
            if hasattr(sig, "signal_type")
            else (
                sig.get("signal_type") or sig.get("signal_id")
                if isinstance(sig, dict)
                else getattr(sig, "signal_id", None)
            )
        )

        if sig_type:
            duplicate_types[sig_type] = duplicate_types.get(sig_type, 0) + 1

    duplicates = {k: v for k, v in duplicate_types.items() if v > 1}
    if duplicates:
        logger.warning(
            "duplicate_signal_types_detected",
            chunk_id=chunk_id,
            question_id=question.get("question_id"),
            duplicate_types=list(duplicates.keys()),
            correlation_id=correlation_id,
        )

    logger.debug(
        "signals_resolved_for_question",
        question_id=question.get("question_id"),
        chunk_id=chunk_id,
        resolved_count=len(signals),
        correlation_id=correlation_id,
    )

    return tuple(signals)


class TestNormalizeMissingSignalRequirements:
    """Test handling of questions without signal_requirements key."""

    def test_normalize_missing_signal_requirements(self):
        """Question without signal_requirements key returns empty tuple with no exceptions."""
        question = {"question_id": "D1-Q1", "dimension_id": "DIM01"}
        chunk_id = "PA01-DIM01"
        mock_registry = Mock()
        correlation_id = "test-correlation-id"

        result = _resolve_signals_for_question(
            question, chunk_id, mock_registry, correlation_id
        )

        assert isinstance(result, tuple)
        assert len(result) == 0
        mock_registry.get_signals_for_chunk.assert_not_called()


class TestNormalizeNoneSignalRequirements:
    """Test handling of questions with None signal_requirements."""

    def test_normalize_none_signal_requirements(self):
        """Question with None value for signal_requirements returns empty tuple."""
        question = {
            "question_id": "D1-Q2",
            "dimension_id": "DIM01",
            "signal_requirements": None,
        }
        chunk_id = "PA01-DIM01"
        mock_registry = Mock()
        correlation_id = "test-correlation-id"

        result = _resolve_signals_for_question(
            question, chunk_id, mock_registry, correlation_id
        )

        assert isinstance(result, tuple)
        assert len(result) == 0
        mock_registry.get_signals_for_chunk.assert_not_called()


class TestSuccessfulResolutionAllAvailable:
    """Test successful signal resolution when all required signals are available."""

    def test_successful_resolution_all_available(self, caplog):
        """Mock registry returns matching signals, verify tuple and debug log."""
        caplog.set_level(logging.DEBUG)
        expected_signal_count = 2

        question = {
            "question_id": "D3-Q2",
            "dimension_id": "DIM03",
            "signal_requirements": {"budget", "actor"},
        }
        chunk_id = "PA05-DIM03"
        correlation_id = "correlation-abc-123"

        mock_signal_budget = Mock()
        mock_signal_budget.signal_type = "budget"

        mock_signal_actor = Mock()
        mock_signal_actor.signal_type = "actor"

        mock_registry = Mock()
        mock_registry.get_signals_for_chunk.return_value = [
            mock_signal_budget,
            mock_signal_actor,
        ]

        log_capture = LogCapture()
        structlog.configure(processors=[log_capture])

        result = _resolve_signals_for_question(
            question, chunk_id, mock_registry, correlation_id
        )

        assert isinstance(result, tuple)
        assert len(result) == expected_signal_count
        assert mock_signal_budget in result
        assert mock_signal_actor in result

        mock_registry.get_signals_for_chunk.assert_called_once_with(
            chunk_id, {"budget", "actor"}
        )

        assert any(
            entry["event"] == "signals_resolved_for_question"
            and entry.get("question_id") == "D3-Q2"
            and entry.get("chunk_id") == chunk_id
            and entry.get("correlation_id") == correlation_id
            for entry in log_capture.entries
        )


class TestHardFailMissingSignals:
    """Test hard-fail behavior when required signals are missing."""

    def test_hard_fail_missing_signals(self):
        """Mock registry omits required signal type, assert ValueError with exact format."""
        question = {
            "question_id": "D4-Q3",
            "dimension_id": "DIM04",
            "signal_requirements": {"budget", "actor", "timeline"},
        }
        chunk_id = "PA02-DIM04"

        mock_signal_budget = Mock()
        mock_signal_budget.signal_type = "budget"

        mock_registry = Mock()
        mock_registry.get_signals_for_chunk.return_value = [mock_signal_budget]

        with pytest.raises(ValueError) as exc_info:
            _resolve_signals_for_question(
                question, chunk_id, mock_registry, "test-corr-id"
            )

        error_msg = str(exc_info.value)
        assert "Synchronization Failure for MQC D4-Q3" in error_msg
        assert "Missing required signals" in error_msg
        assert "PA02-DIM04" in error_msg

        assert "actor" in error_msg or "timeline" in error_msg


class TestRejectNoneRegistryReturn:
    """Test rejection of None return from registry."""

    def test_reject_none_registry_return(self):
        """Mock registry returns None, assert TypeError with contract violation message."""
        question = {
            "question_id": "D2-Q1",
            "dimension_id": "DIM02",
            "signal_requirements": {"semantic"},
        }
        chunk_id = "PA03-DIM02"

        mock_registry = Mock()
        mock_registry.get_signals_for_chunk.return_value = None

        with pytest.raises(TypeError) as exc_info:
            _resolve_signals_for_question(
                question, chunk_id, mock_registry, "test-corr-id"
            )

        error_msg = str(exc_info.value)
        assert "Signal registry returned None" in error_msg
        assert "violating contract" in error_msg
        assert chunk_id in error_msg


class TestValidateSignalStructure:
    """Test validation of signal structure."""

    def test_validate_signal_structure(self):
        """Mock registry returns dict missing signal_id, assert ValueError."""
        question = {
            "question_id": "D5-Q2",
            "dimension_id": "DIM05",
            "signal_requirements": {"causal"},
        }
        chunk_id = "PA04-DIM05"

        invalid_signal = {"content": {"some": "data"}}

        mock_registry = Mock()
        mock_registry.get_signals_for_chunk.return_value = [invalid_signal]

        with pytest.raises(ValueError) as exc_info:
            _resolve_signals_for_question(
                question, chunk_id, mock_registry, "test-corr-id"
            )

        error_msg = str(exc_info.value)
        assert "Signal at index 0" in error_msg
        assert "missing field signal_id" in error_msg


class TestDuplicateSignalTypeWarning:
    """Test warning emission for duplicate signal types."""

    def test_duplicate_signal_type_warning(self):
        """Mock registry returns two signals with same type, verify warning log."""
        expected_duplicate_count = 2
        question = {
            "question_id": "D6-Q1",
            "dimension_id": "DIM06",
            "signal_requirements": {"budget"},
        }
        chunk_id = "PA01-DIM06"
        correlation_id = "correlation-xyz-789"

        mock_signal_1 = Mock()
        mock_signal_1.signal_type = "budget"

        mock_signal_2 = Mock()
        mock_signal_2.signal_type = "budget"

        mock_registry = Mock()
        mock_registry.get_signals_for_chunk.return_value = [
            mock_signal_1,
            mock_signal_2,
        ]

        log_capture = LogCapture()
        structlog.configure(processors=[log_capture])

        result = _resolve_signals_for_question(
            question, chunk_id, mock_registry, correlation_id
        )

        assert isinstance(result, tuple)
        assert len(result) == expected_duplicate_count
        assert mock_signal_1 in result
        assert mock_signal_2 in result

        assert any(
            entry["event"] == "duplicate_signal_types_detected"
            and "budget" in entry.get("duplicate_types", [])
            and entry.get("correlation_id") == correlation_id
            for entry in log_capture.entries
        )


class TestImmutabilityGuarantee:
    """Test immutability of returned tuple."""

    def test_immutability_guarantee(self):
        """Capture return tuple, verify tuple assignment raises TypeError."""
        question = {
            "question_id": "D1-Q3",
            "dimension_id": "DIM01",
            "signal_requirements": {"semantic"},
        }
        chunk_id = "PA07-DIM01"

        mock_signal = Mock()
        mock_signal.signal_type = "semantic"

        mock_registry = Mock()
        mock_registry.get_signals_for_chunk.return_value = [mock_signal]

        result = _resolve_signals_for_question(
            question, chunk_id, mock_registry, "test-corr-id"
        )

        assert isinstance(result, tuple)

        with pytest.raises(TypeError):
            result[0] = Mock()

        with pytest.raises(AttributeError):
            result.append(Mock())


class TestAttributeAndDictFieldAccess:
    """Test processing of both dataclass and dict signals."""

    def test_attribute_and_dict_field_access(self):
        """Mock registry returns mix of dataclass and dict signals, verify both processed."""
        expected_mixed_signal_count = 2
        question = {
            "question_id": "D2-Q5",
            "dimension_id": "DIM02",
            "signal_requirements": {"budget", "actor"},
        }
        chunk_id = "PA08-DIM02"

        mock_dataclass_signal = Mock()
        mock_dataclass_signal.signal_type = "budget"

        dict_signal = {"signal_type": "actor", "content": {"name": "Ministry"}}

        mock_registry = Mock()
        mock_registry.get_signals_for_chunk.return_value = [
            mock_dataclass_signal,
            dict_signal,
        ]

        result = _resolve_signals_for_question(
            question, chunk_id, mock_registry, "test-corr-id"
        )

        assert isinstance(result, tuple)
        assert len(result) == expected_mixed_signal_count
        assert mock_dataclass_signal in result
        assert dict_signal in result


class TestCorrelationIdPropagation:
    """Test correlation_id propagation through all log records."""

    def test_correlation_id_propagation(self):
        """Configure log capture, invoke method, verify all logs contain correlation_id."""
        question = {
            "question_id": "D3-Q4",
            "dimension_id": "DIM03",
            "signal_requirements": {"budget", "timeline"},
        }
        chunk_id = "PA09-DIM03"
        correlation_id = "unique-correlation-id-test"

        mock_signal_budget = Mock()
        mock_signal_budget.signal_type = "budget"

        mock_signal_timeline = Mock()
        mock_signal_timeline.signal_type = "timeline"

        mock_registry = Mock()
        mock_registry.get_signals_for_chunk.return_value = [
            mock_signal_budget,
            mock_signal_timeline,
        ]

        log_capture = LogCapture()
        structlog.configure(processors=[log_capture])

        _resolve_signals_for_question(question, chunk_id, mock_registry, correlation_id)

        for entry in log_capture.entries:
            assert entry.get("correlation_id") == correlation_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

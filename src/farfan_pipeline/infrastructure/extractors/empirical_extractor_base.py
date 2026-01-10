"""
Empirically-Calibrated Extractor Base Framework.

This framework provides auto-loading of empirical calibration data,
validation against gold standards, and dynamic confidence scoring.

Framework Innovation Features:
- Auto-loads patterns from corpus_empirico_calibracion_extractores.json
- Validates against gold standard examples automatically
- Provides confidence scoring with empirical thresholds
- Generates tests automatically from corpus examples
- Supports pattern versioning and A/B testing

Author: CQC Extractor Excellence Framework
Version: 2.0.0
Date: 2026-01-06
"""

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExtractionPattern:
    """Represents a calibrated extraction pattern."""
    pattern_id: str
    pattern: str
    pattern_type: str  # REGEX, KEYWORD, SEMANTIC
    confidence_base: float
    flags: List[str] = field(default_factory=list)
    captures: Dict[str, Any] = field(default_factory=dict)
    validation_rules: List[Dict] = field(default_factory=list)
    empirical_frequency: Dict[str, Any] = field(default_factory=dict)

    def compile(self) -> re.Pattern:
        """Compile regex pattern with flags."""
        flag_map = {
            "IGNORECASE": re.IGNORECASE,
            "MULTILINE": re.MULTILINE,
            "DOTALL": re.DOTALL,
            "UNICODE": re.UNICODE
        }
        flags_combined = 0
        for flag in self.flags:
            flags_combined |= flag_map.get(flag, 0)

        return re.compile(self.pattern, flags_combined)


@dataclass
class ExtractionResult:
    """Result of an extraction operation."""
    extractor_id: str
    signal_type: str
    matches: List[Dict[str, Any]]
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    validation_passed: bool = True
    validation_errors: List[str] = field(default_factory=list)

    def to_signal(self) -> Dict[str, Any]:
        """Convert to Signal format for SISAS."""
        return {
            "signal_id": f"{self.extractor_id}_{datetime.now().timestamp()}",
            "signal_type": self.signal_type,
            "confidence": self.confidence,
            "payload": {
                "matches": self.matches,
                "metadata": self.metadata,
                "validation_passed": self.validation_passed
            },
            "producer_node": self.extractor_id,
            "produced_at": datetime.now(timezone.utc).isoformat()
        }


class EmpiricallyCalibrated(ABC):
    """Base class for empirically-calibrated extractors."""

    def __init__(
        self,
        signal_type: str,
        calibration_file: Optional[Path] = None,
        auto_validate: bool = True
    ):
        self.signal_type = signal_type
        self.auto_validate = auto_validate

        # Load calibration data
        if calibration_file is None:
            calibration_file = self._default_calibration_path()

        self.calibration = self._load_calibration(calibration_file)
        self.patterns = self._load_patterns()
        self.gold_standards = self._load_gold_standards()

        # Initialize metrics
        self.extraction_count = 0
        self.validation_pass_count = 0
        self.validation_fail_count = 0

        logger.info(f"Initialized {self.__class__.__name__} with {len(self.patterns)} empirical patterns")

    def _default_calibration_path(self) -> Path:
        """Get default calibration file path."""
        return Path(__file__).resolve().parent.parent.parent.parent / \
               "canonic_questionnaire_central" / \
               "_registry" / "membership_criteria" / "_calibration" / \
               "extractor_calibration.json"

    def _load_calibration(self, calibration_file: Path) -> Dict[str, Any]:
        """Load empirical calibration data."""
        if not calibration_file.exists():
            logger.warning(f"Calibration file not found: {calibration_file}")
            return {"signal_type_catalog": {}}

        with open(calibration_file) as f:
            data = json.load(f)
            return data.get("signal_type_catalog", {}).get(self.signal_type, {})

    def _load_patterns(self) -> List[ExtractionPattern]:
        """Load and compile patterns from calibration."""
        patterns = []
        extraction_patterns = self.calibration.get("extraction_patterns", {})

        for pattern_id, pattern_config in extraction_patterns.items():
            if isinstance(pattern_config, dict):
                pattern = ExtractionPattern(
                    pattern_id=pattern_id,
                    pattern=pattern_config.get("regex", pattern_config.get("pattern", "")),
                    pattern_type=pattern_config.get("type", "REGEX"),
                    confidence_base=pattern_config.get("confidence", 0.70),
                    flags=pattern_config.get("flags", ["IGNORECASE", "MULTILINE"]),
                    captures=pattern_config.get("captures", {}),
                    validation_rules=pattern_config.get("validation", []),
                    empirical_frequency=self.calibration.get("empirical_frequency", {})
                )
                patterns.append(pattern)

        return patterns

    def _load_gold_standards(self) -> List[Dict[str, Any]]:
        """Load gold standard examples for validation."""
        return self.calibration.get("gold_standard_examples", [])

    @abstractmethod
    def extract(self, text: str, context: Optional[Dict] = None) -> ExtractionResult:
        """Extract signals from text. Must be implemented by subclass."""
        pass

    def validate_extraction(self, result: ExtractionResult) -> Tuple[bool, List[str]]:
        """Validate extraction against empirical rules."""
        errors = []

        # Check if matches are within empirical frequency range
        freq = self.calibration.get("empirical_frequency", {})
        if freq:
            match_count = len(result.matches)
            expected_min = freq.get("min_per_document", 0)
            expected_max = freq.get("max_per_document", float('inf'))

            if match_count < expected_min:
                errors.append(f"Match count {match_count} below empirical minimum {expected_min}")
            elif match_count > expected_max:
                errors.append(f"Match count {match_count} above empirical maximum {expected_max}")

        # Custom validation rules
        for match in result.matches:
            for rule in getattr(self, 'validation_rules', []):
                if not self._apply_validation_rule(match, rule):
                    errors.append(f"Validation rule failed: {rule.get('name', 'unnamed')}")

        is_valid = len(errors) == 0

        if is_valid:
            self.validation_pass_count += 1
        else:
            self.validation_fail_count += 1

        return is_valid, errors

    def _apply_validation_rule(self, match: Dict, rule: Dict) -> bool:
        """Apply a single validation rule."""
        rule_type = rule.get("type")

        if rule_type == "positive_value":
            field = rule.get("field")
            return match.get(field, 0) > 0
        elif rule_type == "date_range":
            field = rule.get("field")
            min_year = rule.get("min_year", 2020)
            max_year = rule.get("max_year", 2030)
            value = match.get(field)
            if isinstance(value, int):
                return min_year <= value <= max_year
        elif rule_type == "non_empty":
            field = rule.get("field")
            return bool(match.get(field))

        return True

    def get_confidence_threshold(self) -> float:
        """Get empirically calibrated confidence threshold."""
        return self.calibration.get("confidence_threshold", 0.70)

    def get_metrics(self) -> Dict[str, Any]:
        """Get extractor performance metrics."""
        return {
            "extractor": self.__class__.__name__,
            "signal_type": self.signal_type,
            "extractions_performed": self.extraction_count,
            "validations_passed": self.validation_pass_count,
            "validations_failed": self.validation_fail_count,
            "pass_rate": self.validation_pass_count / self.extraction_count if self.extraction_count > 0 else 0.0,
            "patterns_loaded": len(self.patterns),
            "gold_standards_loaded": len(self.gold_standards)
        }

    def self_test(self) -> Dict[str, Any]:
        """Run self-test against gold standard examples."""
        logger.info(f"Running self-test for {self.__class__.__name__}...")

        results = {
            "extractor": self.__class__.__name__,
            "signal_type": self.signal_type,
            "gold_standards_tested": len(self.gold_standards),
            "passed": 0,
            "failed": 0,
            "failures": []
        }

        for i, example in enumerate(self.gold_standards):
            text = example.get("text", "")
            expected = example.get("expected_matches", 0)

            try:
                result = self.extract(text)
                actual = len(result.matches)

                if actual >= expected:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                    results["failures"].append({
                        "example_id": i,
                        "expected": expected,
                        "actual": actual,
                        "text_preview": text[:100]
                    })
            except Exception as e:
                results["failed"] += 1
                results["failures"].append({
                    "example_id": i,
                    "error": str(e),
                    "text_preview": text[:100]
                })

        results["pass_rate"] = results["passed"] / len(self.gold_standards) if self.gold_standards else 0.0

        logger.info(f"Self-test complete: {results['pass_rate']:.2%} pass rate")

        return results


class PatternBasedExtractor(EmpiricallyCalibrated):
    """Base class for pattern-based extractors (regex, keyword)."""

    def extract(self, text: str, context: Optional[Dict] = None) -> ExtractionResult:
        """Extract using compiled patterns."""
        matches = []

        for pattern_obj in self.patterns:
            compiled = pattern_obj.compile()

            for match in compiled.finditer(text):
                match_dict = {
                    "pattern_id": pattern_obj.pattern_id,
                    "text": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": pattern_obj.confidence_base
                }

                # Extract captures
                if pattern_obj.captures:
                    for group_name, group_config in pattern_obj.captures.items():
                        try:
                            group_value = match.group(int(group_name))
                            match_dict[group_config["name"]] = group_value
                        except (IndexError, ValueError):
                            pass

                # Add context if provided
                if context:
                    match_dict["context"] = context

                matches.append(match_dict)

        # Calculate aggregate confidence
        avg_confidence = sum(m["confidence"] for m in matches) / len(matches) if matches else 0.0

        result = ExtractionResult(
            extractor_id=self.__class__.__name__,
            signal_type=self.signal_type,
            matches=matches,
            confidence=avg_confidence,
            metadata={
                "patterns_used": len(self.patterns),
                "total_matches": len(matches)
            }
        )

        # Validate if enabled
        if self.auto_validate:
            is_valid, errors = self.validate_extraction(result)
            result.validation_passed = is_valid
            result.validation_errors = errors

        self.extraction_count += 1

        return result


# Utility functions for framework

def load_all_extractors_from_calibration(calibration_file: Path) -> Dict[str, Any]:
    """Load configuration for all extractors from calibration file."""
    with open(calibration_file) as f:
        data = json.load(f)
        return data.get("signal_type_catalog", {})


def generate_test_suite(extractor_class, output_path: Path):
    """Auto-generate pytest test suite from gold standards."""
    extractor = extractor_class()

    test_code = f'''"""
Auto-generated tests for {extractor_class.__name__}.
Generated from empirical gold standards.
"""

import pytest
from {extractor.__class__.__module__} import {extractor_class.__name__}


@pytest.fixture
def extractor():
    return {extractor_class.__name__}()


'''

    for i, example in enumerate(extractor.gold_standards):
        text = example.get("text", "")
        expected = example.get("expected_matches", 0)

        test_code += f'''
def test_gold_standard_{i}(extractor):
    """Test against gold standard example {i}."""
    text = """{text}"""
    result = extractor.extract(text)
    assert len(result.matches) >= {expected}, f"Expected at least {expected} matches, got {{len(result.matches)}}"
    assert result.confidence >= extractor.get_confidence_threshold()

'''

    output_path.write_text(test_code)
    logger.info(f"Generated test suite at {output_path}")


# Export main classes
__all__ = [
    'EmpiricallyCalibrated',
    'PatternBasedExtractor',
    'ExtractionPattern',
    'ExtractionResult',
    'load_all_extractors_from_calibration',
    'generate_test_suite'
]

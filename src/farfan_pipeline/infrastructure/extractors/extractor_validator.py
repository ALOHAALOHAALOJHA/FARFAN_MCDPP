"""
Extractor Validation Framework.

Auto-validates extractors against empirical gold standards and generates
comprehensive performance reports.

Innovation Features:
- Auto-generates pytest tests from gold standards
- Runs validation against 14 real PDT plans
- Computes precision, recall, F1 scores
- Generates performance dashboards
- Identifies pattern weaknesses for improvement

Author: CQC Extractor Excellence Framework
Version: 2.0.0
Date: 2026-01-06
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ValidationMetrics:
    """Metrics for extractor validation."""

    extractor_name: str
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    avg_confidence: float = 0.0
    execution_time_ms: float = 0.0
    failures: list[dict] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        return self.passed / self.total_tests if self.total_tests > 0 else 0.0


class ExtractorValidator:
    """Validates extractors against empirical gold standards."""

    def __init__(self, calibration_file: Path | None = None):
        if calibration_file is None:
            calibration_file = (
                Path(__file__).resolve().parent.parent.parent.parent
                / "canonic_questionnaire_central"
                / "_registry"
                / "membership_criteria"
                / "_calibration"
                / "extractor_calibration.json"
            )

        self.calibration_file = calibration_file
        self.calibration_data = self._load_calibration()

    def _load_calibration(self) -> dict:
        """Load calibration data."""
        if not self.calibration_file.exists():
            logger.warning(f"Calibration file not found: {self.calibration_file}")
            return {}

        with open(self.calibration_file) as f:
            return json.load(f)

    def validate_extractor(self, extractor, signal_type: str) -> ValidationMetrics:
        """
        Validate an extractor against gold standards.

        Args:
            extractor: Extractor instance (must have .extract() method)
            signal_type: Signal type being extracted

        Returns:
            ValidationMetrics with comprehensive results
        """
        import time

        metrics = ValidationMetrics(extractor_name=extractor.__class__.__name__)

        # Get gold standards for this signal type
        signal_catalog = self.calibration_data.get("signal_type_catalog", {})
        signal_config = signal_catalog.get(signal_type, {})
        gold_standards = signal_config.get("gold_standard_examples", [])

        if not gold_standards:
            logger.warning(f"No gold standards found for {signal_type}")
            return metrics

        metrics.total_tests = len(gold_standards)

        # Run extraction on each example
        confidences = []
        true_positives = 0
        false_positives = 0
        false_negatives = 0

        start_time = time.time()

        for i, example in enumerate(gold_standards):
            text = example.get("text", "")
            expected_min = example.get("expected_matches", 0)
            expected_max = example.get("expected_matches_max", expected_min + 5)

            try:
                result = extractor.extract(text)
                actual = len(result.matches)
                confidences.append(result.confidence)

                # Check if within expected range
                if expected_min <= actual <= expected_max:
                    metrics.passed += 1
                    true_positives += actual
                else:
                    metrics.failed += 1
                    metrics.failures.append(
                        {
                            "example_id": i,
                            "expected_min": expected_min,
                            "expected_max": expected_max,
                            "actual": actual,
                            "text_preview": text[:150],
                            "reason": "out_of_range",
                        }
                    )

                    # Count false positives/negatives
                    if actual > expected_max:
                        false_positives += actual - expected_max
                    elif actual < expected_min:
                        false_negatives += expected_min - actual

            except Exception as e:
                metrics.failed += 1
                metrics.failures.append(
                    {
                        "example_id": i,
                        "error": str(e),
                        "text_preview": text[:150],
                        "reason": "exception",
                    }
                )

        end_time = time.time()
        metrics.execution_time_ms = (end_time - start_time) * 1000

        # Calculate precision, recall, F1
        if true_positives + false_positives > 0:
            metrics.precision = true_positives / (true_positives + false_positives)

        if true_positives + false_negatives > 0:
            metrics.recall = true_positives / (true_positives + false_negatives)

        if metrics.precision + metrics.recall > 0:
            metrics.f1_score = (
                2 * (metrics.precision * metrics.recall) / (metrics.precision + metrics.recall)
            )

        metrics.avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        return metrics

    def validate_all_extractors(self) -> dict[str, ValidationMetrics]:
        """Validate all implemented extractors."""
        from .causal_verb_extractor import CausalVerbExtractor
        from .financial_chain_extractor import FinancialChainExtractor
        from .institutional_ner_extractor import InstitutionalNERExtractor

        extractors = {
            "FINANCIAL_CHAIN": FinancialChainExtractor(),
            "CAUSAL_LINK": CausalVerbExtractor(),
            "INSTITUTIONAL_ENTITY": InstitutionalNERExtractor(),
        }

        results = {}

        logger.info("🔍 Starting validation of all extractors...")

        for signal_type, extractor in extractors.items():
            logger.info(f"  Validating {extractor.__class__.__name__}...")
            metrics = self.validate_extractor(extractor, signal_type)
            results[signal_type] = metrics

            logger.info(
                f"    ✓ {metrics.pass_rate:.1%} pass rate "
                f"(P={metrics.precision:.2f}, R={metrics.recall:.2f}, F1={metrics.f1_score:.2f})"
            )

        return results

    def generate_report(
        self, results: dict[str, ValidationMetrics], output_path: Path | None = None
    ) -> str:
        """Generate validation report."""
        report_lines = [
            "=" * 80,
            "EXTRACTOR VALIDATION REPORT",
            "=" * 80,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Calibration: {self.calibration_file}",
            "",
            "SUMMARY",
            "-" * 80,
        ]

        total_tests = sum(m.total_tests for m in results.values())
        total_passed = sum(m.passed for m in results.values())
        total_failed = sum(m.failed for m in results.values())

        report_lines.extend(
            [
                f"Total tests: {total_tests}",
                f"Passed: {total_passed} ({total_passed/total_tests:.1%})",
                f"Failed: {total_failed} ({total_failed/total_tests:.1%})",
                "",
                "EXTRACTOR PERFORMANCE",
                "-" * 80,
            ]
        )

        for signal_type, metrics in results.items():
            report_lines.extend(
                [
                    "",
                    f"{metrics.extractor_name} ({signal_type})",
                    f"  Tests: {metrics.total_tests}",
                    f"  Pass rate: {metrics.pass_rate:.1%}",
                    f"  Precision: {metrics.precision:.3f}",
                    f"  Recall: {metrics.recall:.3f}",
                    f"  F1 Score: {metrics.f1_score:.3f}",
                    f"  Avg Confidence: {metrics.avg_confidence:.3f}",
                    f"  Execution time: {metrics.execution_time_ms:.1f}ms",
                ]
            )

            if metrics.failures:
                report_lines.append(f"  Failures: {len(metrics.failures)}")
                for failure in metrics.failures[:3]:  # Show first 3
                    reason = failure.get("reason", "unknown")
                    report_lines.append(f"    - Example {failure.get('example_id')}: {reason}")

        report_lines.extend(
            [
                "",
                "=" * 80,
            ]
        )

        report = "\n".join(report_lines)

        if output_path:
            output_path.write_text(report)
            logger.info(f"Report saved to {output_path}")

        return report

    def generate_pytest_suite(self, output_dir: Path):
        """Generate pytest test suite for all extractors."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate test file for each extractor
        self._generate_financial_chain_tests(output_dir)
        self._generate_causal_verb_tests(output_dir)
        self._generate_institutional_ner_tests(output_dir)

        # Generate conftest
        self._generate_conftest(output_dir)

        logger.info(f"✓ Generated pytest suite in {output_dir}")

    def _generate_financial_chain_tests(self, output_dir: Path):
        """Generate tests for FinancialChainExtractor."""
        signal_config = self.calibration_data.get("signal_type_catalog", {}).get(
            "FINANCIAL_CHAIN", {}
        )
        gold_standards = signal_config.get("gold_standard_examples", [])

        test_code = '''"""
Auto-generated tests for FinancialChainExtractor.
Generated from empirical gold standards.

DO NOT EDIT MANUALLY - regenerate using extractor_validator.py
"""

import pytest
from farfan_pipeline.infrastructure.extractors.financial_chain_extractor import FinancialChainExtractor


@pytest.fixture
def extractor():
    return FinancialChainExtractor()

'''

        for i, example in enumerate(gold_standards):
            text = example.get("text", "").replace('"', '\\"')
            expected = example.get("expected_matches", 0)

            test_code += f'''
def test_financial_chain_gold_{i}(extractor):
    """Test against gold standard example {i}."""
    text = """{text}"""
    result = extractor.extract(text)
    assert len(result.matches) >= {expected}, \\
        f"Expected at least {expected} matches, got {{len(result.matches)}}"
    assert result.confidence >= 0.70

'''

        (output_dir / "test_financial_chain_extractor.py").write_text(test_code)

    def _generate_causal_verb_tests(self, output_dir: Path):
        """Generate tests for CausalVerbExtractor."""
        signal_config = self.calibration_data.get("signal_type_catalog", {}).get("CAUSAL_LINK", {})
        gold_standards = signal_config.get("gold_standard_examples", [])

        test_code = '''"""
Auto-generated tests for CausalVerbExtractor.
"""

import pytest
from farfan_pipeline.infrastructure.extractors.causal_verb_extractor import CausalVerbExtractor


@pytest.fixture
def extractor():
    return CausalVerbExtractor()

'''

        for i, example in enumerate(gold_standards):
            text = example.get("text", "").replace('"', '\\"')
            expected = example.get("expected_matches", 0)

            test_code += f'''
def test_causal_link_gold_{i}(extractor):
    """Test against gold standard example {i}."""
    text = """{text}"""
    result = extractor.extract(text)
    assert len(result.matches) >= {expected}
    assert result.confidence >= 0.65

'''

        (output_dir / "test_causal_verb_extractor.py").write_text(test_code)

    def _generate_institutional_ner_tests(self, output_dir: Path):
        """Generate tests for InstitutionalNERExtractor."""
        signal_config = self.calibration_data.get("signal_type_catalog", {}).get(
            "INSTITUTIONAL_ENTITY", {}
        )
        gold_standards = signal_config.get("gold_standard_examples", [])

        test_code = '''"""
Auto-generated tests for InstitutionalNERExtractor.
"""

import pytest
from farfan_pipeline.infrastructure.extractors.institutional_ner_extractor import InstitutionalNERExtractor


@pytest.fixture
def extractor():
    return InstitutionalNERExtractor()

'''

        for i, example in enumerate(gold_standards):
            text = example.get("text", "").replace('"', '\\"')
            expected = example.get("expected_matches", 0)

            test_code += f'''
def test_institutional_entity_gold_{i}(extractor):
    """Test against gold standard example {i}."""
    text = """{text}"""
    result = extractor.extract(text)
    assert len(result.matches) >= {expected}
    assert result.confidence >= 0.75

'''

        (output_dir / "test_institutional_ner_extractor.py").write_text(test_code)

    def _generate_conftest(self, output_dir: Path):
        """Generate pytest conftest."""
        conftest = '''"""
Pytest configuration for extractor tests.
"""

import pytest


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "extractor: mark test as extractor validation test"
    )
'''

        (output_dir / "conftest.py").write_text(conftest)


# CLI interface


def main():
    """Run validation from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate extractors against gold standards")
    parser.add_argument("--generate-tests", action="store_true", help="Generate pytest suite")
    parser.add_argument(
        "--output-dir", type=Path, default=Path("tests/extractors"), help="Output directory"
    )
    parser.add_argument("--report", type=Path, help="Save report to file")

    args = parser.parse_args()

    validator = ExtractorValidator()

    if args.generate_tests:
        validator.generate_pytest_suite(args.output_dir)
        print(f"✓ Generated pytest suite in {args.output_dir}")
    else:
        results = validator.validate_all_extractors()
        report = validator.generate_report(results, args.report)
        print(report)


if __name__ == "__main__":
    main()


__all__ = ["ExtractorValidator", "ValidationMetrics"]

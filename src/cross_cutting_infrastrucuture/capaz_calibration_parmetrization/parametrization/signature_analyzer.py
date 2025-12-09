"""
Advanced Signature Analyzer - Extended Analysis for Method Signatures

Provides advanced analysis capabilities:
- Infers output ranges from docstrings and return statements
- Analyzes parameter dependencies and relationships
- Detects common patterns (thresholds, configs, etc.)
- Generates migration recommendations

COHORT_2024 - REFACTOR_WAVE_2024_12
"""

from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from method_signature_extractor import MethodSignature


@dataclass
class OutputRangeInference:
    inferred_type: str
    min_value: float | None = None
    max_value: float | None = None
    possible_values: list[Any] | None = None
    confidence: float = 0.0
    source: str = ""


class SignatureAnalyzer:
    def __init__(self, signatures: dict[str, MethodSignature]) -> None:
        self.signatures = signatures

    def analyze_output_ranges(self) -> dict[str, OutputRangeInference]:
        results: dict[str, OutputRangeInference] = {}

        for sig_name, sig in self.signatures.items():
            inference = self._infer_output_range_from_context(sig)
            if inference:
                results[sig_name] = inference

        return results

    def _infer_output_range_from_context(self, sig: MethodSignature) -> OutputRangeInference | None:
        docstring = sig.docstring or ""

        if "probability" in sig.method_name.lower() or "prob" in sig.method_name.lower():
            return OutputRangeInference(
                inferred_type="float",
                min_value=0.0,
                max_value=1.0,
                confidence=0.8,
                source="method_name_pattern"
            )

        if "confidence" in sig.method_name.lower():
            return OutputRangeInference(
                inferred_type="float",
                min_value=0.0,
                max_value=1.0,
                confidence=0.8,
                source="method_name_pattern"
            )

        if "score" in sig.method_name.lower():
            range_match = re.search(r"(?:score|range).*?(\d+\.?\d*)\s*(?:to|-)\s*(\d+\.?\d*)", docstring, re.IGNORECASE)
            if range_match:
                return OutputRangeInference(
                    inferred_type="float",
                    min_value=float(range_match.group(1)),
                    max_value=float(range_match.group(2)),
                    confidence=0.9,
                    source="docstring_range"
                )

        return_match = re.search(r"(?:returns?|output):\s*(.*?)(?:\n\n|\n[A-Z]|$)", docstring, re.IGNORECASE | re.DOTALL)
        if return_match:
            return_desc = return_match.group(1).lower()
            if "0" in return_desc and "1" in return_desc:
                return OutputRangeInference(
                    inferred_type="float",
                    min_value=0.0,
                    max_value=1.0,
                    confidence=0.7,
                    source="docstring_description"
                )

        return None

    def detect_parameter_patterns(self) -> dict[str, list[str]]:
        patterns: dict[str, list[str]] = {
            "bayesian_params": [],
            "threshold_params": [],
            "config_params": [],
            "model_params": [],
            "io_params": [],
        }

        for sig_name, sig in self.signatures.items():
            all_params = sig.required_inputs + sig.optional_inputs

            for param in all_params:
                param_lower = param.lower()

                if any(kw in param_lower for kw in ["prior", "posterior", "likelihood", "alpha", "beta"]):
                    patterns["bayesian_params"].append(f"{sig_name}.{param}")

                if any(kw in param_lower for kw in ["threshold", "min_", "max_", "cutoff"]):
                    patterns["threshold_params"].append(f"{sig_name}.{param}")

                if any(kw in param_lower for kw in ["config", "settings", "options"]):
                    patterns["config_params"].append(f"{sig_name}.{param}")

                if any(kw in param_lower for kw in ["model", "estimator", "predictor"]):
                    patterns["model_params"].append(f"{sig_name}.{param}")

                if any(kw in param_lower for kw in ["path", "file", "input", "output"]):
                    patterns["io_params"].append(f"{sig_name}.{param}")

        return patterns

    def generate_migration_priority(self) -> list[dict[str, Any]]:
        priorities: list[dict[str, Any]] = []

        for sig_name, sig in self.signatures.items():
            if not sig.hardcoded_parameters:
                continue

            for param in sig.hardcoded_parameters:
                priority_score = 0

                if param["variable"].lower() in ["threshold", "alpha", "beta", "confidence"]:
                    priority_score += 10

                if isinstance(param["value"], (int, float)):
                    priority_score += 5

                if param["variable"].isupper():
                    priority_score += 3

                priorities.append({
                    "signature": sig_name,
                    "parameter": param["variable"],
                    "value": param["value"],
                    "priority_score": priority_score,
                    "line": param["line"],
                    "suggested_config_key": f"{sig.module}.{sig.class_name or sig.method_name}.{param['variable']}",
                })

        priorities.sort(key=lambda x: x["priority_score"], reverse=True)
        return priorities

    def export_analysis(self, output_path: Path) -> None:
        output_ranges = self.analyze_output_ranges()
        parameter_patterns = self.detect_parameter_patterns()
        migration_priorities = self.generate_migration_priority()

        analysis_data = {
            "_metadata": {
                "cohort_id": "COHORT_2024",
                "creation_date": "2024-12-15T00:00:00+00:00",
                "wave_version": "REFACTOR_WAVE_2024_12",
            },
            "output_range_inferences": {
                sig_name: {
                    "inferred_type": inf.inferred_type,
                    "min_value": inf.min_value,
                    "max_value": inf.max_value,
                    "possible_values": inf.possible_values,
                    "confidence": inf.confidence,
                    "source": inf.source,
                }
                for sig_name, inf in output_ranges.items()
            },
            "parameter_patterns": parameter_patterns,
            "migration_priorities": migration_priorities[:50],
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)


def analyze_signatures(signatures_path: Path, output_path: Path) -> None:
    with open(signatures_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    signatures_dict = {}
    for sig_name, sig_data in data.get("signatures", {}).items():
        signatures_dict[sig_name] = MethodSignature(
            module=sig_data["module"],
            class_name=sig_data["class_name"],
            method_name=sig_data["method_name"],
            required_inputs=sig_data["required_inputs"],
            optional_inputs=sig_data["optional_inputs"],
            critical_optional=sig_data["critical_optional"],
            output_type=sig_data["output_type"],
            output_range=sig_data["output_range"],
            hardcoded_parameters=sig_data["hardcoded_parameters"],
            docstring=sig_data["docstring"],
            line_number=sig_data["line_number"],
        )

    analyzer = SignatureAnalyzer(signatures_dict)
    analyzer.export_analysis(output_path)


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    parametrization_dir = repo_root / "src" / "cross_cutting_infrastrucuture" / "capaz_calibration_parmetrization" / "parametrization"

    signatures_path = parametrization_dir / "method_signatures.json"
    output_path = parametrization_dir / "signature_analysis.json"

    if signatures_path.exists():
        analyze_signatures(signatures_path, output_path)
        print(f"Analysis exported to {output_path}")
    else:
        print(f"Error: {signatures_path} not found. Run method_signature_extractor.py first.")

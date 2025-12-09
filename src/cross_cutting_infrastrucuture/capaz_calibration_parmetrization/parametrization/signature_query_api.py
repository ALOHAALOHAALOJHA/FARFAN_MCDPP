"""
Signature Query API - Programmatic Interface for Method Signatures

Provides a clean Python API for querying method signatures:

Usage:
    from signature_query_api import SignatureDatabase

    db = SignatureDatabase.load()
    
    # Query by method name
    results = db.find_by_method_name("calculate_probability")
    
    # Query by module
    results = db.find_by_module("methods_dispensary.derek_beach")
    
    # Query by class
    results = db.find_by_class("FinancialAuditor")
    
    # Get signature details
    sig = db.get_signature("methods_dispensary.derek_beach.FinancialAuditor.analyze_budget")
    print(sig.required_inputs)
    print(sig.critical_optional)

COHORT_2024 - REFACTOR_WAVE_2024_12
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Signature:
    normalized_name: str
    module: str
    class_name: str | None
    method_name: str
    required_inputs: list[str]
    optional_inputs: list[str]
    critical_optional: list[str]
    output_type: str | None
    output_range: dict[str, Any] | None
    hardcoded_parameters: list[dict[str, Any]]
    docstring: str | None
    line_number: int

    @classmethod
    def from_dict(cls, normalized_name: str, data: dict[str, Any]) -> Signature:
        return cls(
            normalized_name=normalized_name,
            module=data["module"],
            class_name=data["class_name"],
            method_name=data["method_name"],
            required_inputs=data["required_inputs"],
            optional_inputs=data["optional_inputs"],
            critical_optional=data["critical_optional"],
            output_type=data["output_type"],
            output_range=data["output_range"],
            hardcoded_parameters=data["hardcoded_parameters"],
            docstring=data["docstring"],
            line_number=data["line_number"],
        )

    @property
    def has_required_inputs(self) -> bool:
        return len(self.required_inputs) > 0

    @property
    def has_optional_inputs(self) -> bool:
        return len(self.optional_inputs) > 0

    @property
    def has_critical_params(self) -> bool:
        return len(self.critical_optional) > 0

    @property
    def has_hardcoded_params(self) -> bool:
        return len(self.hardcoded_parameters) > 0

    @property
    def is_class_method(self) -> bool:
        return self.class_name is not None

    @property
    def total_parameters(self) -> int:
        return len(self.required_inputs) + len(self.optional_inputs)


class SignatureDatabase:
    def __init__(self, signatures: dict[str, Signature], metadata: dict[str, Any]) -> None:
        self.signatures = signatures
        self.metadata = metadata

    @classmethod
    def load(cls, path: Path | None = None) -> SignatureDatabase:
        if path is None:
            repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
            path = repo_root / "src" / "cross_cutting_infrastrucuture" / "capaz_calibration_parmetrization" / "parametrization" / "method_signatures.json"

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        signatures = {
            name: Signature.from_dict(name, sig_data)
            for name, sig_data in data.get("signatures", {}).items()
        }

        return cls(signatures=signatures, metadata=data.get("_metadata", {}))

    def get_signature(self, normalized_name: str) -> Signature | None:
        return self.signatures.get(normalized_name)

    def find_by_method_name(self, method_name: str, exact: bool = True) -> list[Signature]:
        results = []
        for sig in self.signatures.values():
            if exact:
                if sig.method_name == method_name:
                    results.append(sig)
            else:
                if method_name.lower() in sig.method_name.lower():
                    results.append(sig)
        return results

    def find_by_module(self, module: str, exact: bool = True) -> list[Signature]:
        results = []
        for sig in self.signatures.values():
            if exact:
                if sig.module == module:
                    results.append(sig)
            else:
                if module.lower() in sig.module.lower():
                    results.append(sig)
        return results

    def find_by_class(self, class_name: str, exact: bool = True) -> list[Signature]:
        results = []
        for sig in self.signatures.values():
            if sig.class_name is None:
                continue
            if exact:
                if sig.class_name == class_name:
                    results.append(sig)
            else:
                if class_name.lower() in sig.class_name.lower():
                    results.append(sig)
        return results

    def find_with_critical_params(self) -> list[Signature]:
        return [sig for sig in self.signatures.values() if sig.has_critical_params]

    def find_with_hardcoded_params(self) -> list[Signature]:
        return [sig for sig in self.signatures.values() if sig.has_hardcoded_params]

    def find_by_output_type(self, output_type: str) -> list[Signature]:
        results = []
        for sig in self.signatures.values():
            if sig.output_type and output_type.lower() in sig.output_type.lower():
                results.append(sig)
        return results

    def find_by_parameter_name(self, param_name: str, exact: bool = False) -> list[Signature]:
        results = []
        for sig in self.signatures.values():
            all_params = sig.required_inputs + sig.optional_inputs
            if exact:
                if param_name in all_params:
                    results.append(sig)
            else:
                if any(param_name.lower() in p.lower() for p in all_params):
                    results.append(sig)
        return results

    def get_all_modules(self) -> list[str]:
        return sorted(set(sig.module for sig in self.signatures.values()))

    def get_all_classes(self) -> list[str]:
        return sorted(set(sig.class_name for sig in self.signatures.values() if sig.class_name))

    def get_all_method_names(self) -> list[str]:
        return sorted(set(sig.method_name for sig in self.signatures.values()))

    def get_statistics(self) -> dict[str, int]:
        return {
            "total_signatures": len(self.signatures),
            "class_methods": sum(1 for sig in self.signatures.values() if sig.is_class_method),
            "module_functions": sum(1 for sig in self.signatures.values() if not sig.is_class_method),
            "with_required_inputs": sum(1 for sig in self.signatures.values() if sig.has_required_inputs),
            "with_optional_inputs": sum(1 for sig in self.signatures.values() if sig.has_optional_inputs),
            "with_critical_params": sum(1 for sig in self.signatures.values() if sig.has_critical_params),
            "with_hardcoded_params": sum(1 for sig in self.signatures.values() if sig.has_hardcoded_params),
            "unique_modules": len(self.get_all_modules()),
            "unique_classes": len(self.get_all_classes()),
        }


def example_usage() -> None:
    db = SignatureDatabase.load()

    print("=== Database Statistics ===")
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"{key:.<40} {value:>6}")
    print()

    print("=== Finding Bayesian Methods ===")
    bayesian_methods = db.find_by_method_name("bayesian", exact=False)
    for sig in bayesian_methods[:5]:
        print(f"  - {sig.normalized_name}")
    print(f"  Total: {len(bayesian_methods)}")
    print()

    print("=== Methods in derek_beach Module ===")
    derek_beach_methods = db.find_by_module("derek_beach", exact=False)
    print(f"  Total: {len(derek_beach_methods)}")
    print()

    print("=== Methods with 'threshold' Parameter ===")
    threshold_methods = db.find_by_parameter_name("threshold", exact=False)
    for sig in threshold_methods[:5]:
        print(f"  - {sig.normalized_name}")
        all_params = sig.required_inputs + sig.optional_inputs
        threshold_params = [p for p in all_params if "threshold" in p.lower()]
        print(f"    Threshold params: {', '.join(threshold_params)}")
    print(f"  Total: {len(threshold_methods)}")
    print()

    print("=== Methods with Hardcoded Parameters ===")
    hardcoded_methods = db.find_with_hardcoded_params()
    hardcoded_methods_sorted = sorted(hardcoded_methods, key=lambda s: len(s.hardcoded_parameters), reverse=True)
    for sig in hardcoded_methods_sorted[:5]:
        print(f"  - {sig.normalized_name}")
        print(f"    Hardcoded: {len(sig.hardcoded_parameters)} parameters")
    print(f"  Total: {len(hardcoded_methods)}")
    print()


if __name__ == "__main__":
    example_usage()

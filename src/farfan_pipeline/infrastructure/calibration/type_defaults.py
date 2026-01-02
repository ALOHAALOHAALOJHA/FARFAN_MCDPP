"""
Type-Specific Calibration Defaults
==================================
Derived from: artifacts/data/epistemic_inputs_v4/epistemic_minima_by_type.json

DESIGN PATTERN: Flyweight Pattern
- Each ContractType has ONE canonical CalibrationDefaults instance
- Prevents proliferation of duplicate configuration objects
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Final

from .calibration_core import CalibrationBounds

_EPISTEMIC_MINIMA_PATH: Final[Path] = Path(
    "artifacts/data/epistemic_inputs_v4/epistemic_minima_by_type.json"
)


@lru_cache(maxsize=5)
def get_type_defaults(contract_type_code: str) -> dict[str, CalibrationBounds]:
    """
    Load calibration defaults for a contract type.

    FLYWEIGHT PATTERN: Cached per type, never recomputed.
    """
    if not _EPISTEMIC_MINIMA_PATH.exists():
        raise FileNotFoundError(
            f"FATAL: Epistemic minima file not found at {_EPISTEMIC_MINIMA_PATH}"
        )

    with open(_EPISTEMIC_MINIMA_PATH, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Handle malformed JSON: strip the invalid epistemic_necessity_logic section
    # which contains Python triple-quoted strings (invalid JSON)
    if '"epistemic_necessity_logic"' in content:
        # Find the start of the malformed section
        start_idx = content.find('"epistemic_necessity_logic"')
        # Find the closing brace by counting braces
        brace_count = 0
        i = start_idx
        while i < len(content):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                if brace_count == 1:
                    # Found the end of epistemic_necessity_logic section
                    # Replace it with empty object
                    before = content[:start_idx]
                    after = content[i+1:]
                    # Remove trailing comma before this section if exists
                    before = before.rstrip().rstrip(',')
                    content = before + '\n' + after
                    break
                brace_count -= 1
            i += 1
    
    minima = json.loads(content)

    type_spec = minima.get("type_specifications", {}).get(contract_type_code)
    if type_spec is None:
        raise KeyError(f"Unknown contract type: {contract_type_code}")

    layer_ratios = type_spec.get("expected_layer_ratio", {})

    defaults = {
        "n1_ratio": CalibrationBounds(
            min_value=layer_ratios.get("N1_EMP", {}).get("min", 0.2),
            max_value=layer_ratios.get("N1_EMP", {}).get("max", 0.4),
            default_value=(
                layer_ratios.get("N1_EMP", {}).get("min", 0.2)
                + layer_ratios.get("N1_EMP", {}).get("max", 0.4)
            )
            / 2,
            unit="ratio",
        ),
        "n2_ratio": CalibrationBounds(
            min_value=layer_ratios.get("N2_INF", {}).get("min", 0.3),
            max_value=layer_ratios.get("N2_INF", {}).get("max", 0.5),
            default_value=(
                layer_ratios.get("N2_INF", {}).get("min", 0.3)
                + layer_ratios.get("N2_INF", {}).get("max", 0.5)
            )
            / 2,
            unit="ratio",
        ),
        "n3_ratio": CalibrationBounds(
            min_value=layer_ratios.get("N3_AUD", {}).get("min", 0.1),
            max_value=layer_ratios.get("N3_AUD", {}).get("max", 0.3),
            default_value=(
                layer_ratios.get("N3_AUD", {}).get("min", 0.1)
                + layer_ratios.get("N3_AUD", {}).get("max", 0.3)
            )
            / 2,
            unit="ratio",
        ),
        "veto_threshold": CalibrationBounds(
            min_value=0.01 if contract_type_code == "TYPE_E" else 0.03,
            max_value=0.10 if contract_type_code == "TYPE_D" else 0.05,
            default_value=0.05,
            unit="probability",
        ),
        "prior_strength": CalibrationBounds(
            min_value=0.1,
            max_value=10.0,
            default_value=1.0 if contract_type_code != "TYPE_B" else 2.0,
            unit="prior_weight",
        ),
    }

    return defaults


PROHIBITED_OPERATIONS: Final[dict[str, frozenset[str]]] = {
    "TYPE_A": frozenset({"weighted_mean", "concat_only"}),
    "TYPE_B": frozenset({"weighted_mean", "simple_concat"}),
    "TYPE_C": frozenset({"concat_only", "weighted_mean"}),
    "TYPE_D": frozenset({"concat_only", "simple_concat"}),
    "TYPE_E": frozenset({"weighted_mean", "average", "mean", "avg"}),
}


def is_operation_prohibited(contract_type_code: str, operation: str) -> bool:
    """Check if operation is prohibited for contract type."""
    prohibited = PROHIBITED_OPERATIONS.get(contract_type_code, frozenset())
    return operation.lower() in prohibited or any(p in operation.lower() for p in prohibited)

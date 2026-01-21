# Phase 3 Mission Contract
# Defines topological order and mission control

from typing import List, Dict

PHASE_ID = "03"
PHASE_NAME = "Scoring Transformation"

# Topological Order Definition
TOPOLOGICAL_ORDER = [
    "phase3_15_00_empirical_thresholds_loader",
    "phase3_20_00_score_extraction",
    "phase3_22_00_validation",
    "phase3_24_00_signal_enriched_scoring",
    "phase3_26_00_normative_compliance_validator"
]

# File to Topological Position Mapping
FILE_MAPPING = {
    "phase3_15_00_empirical_thresholds_loader.py": 1,
    "phase3_20_00_score_extraction.py": 2,
    "phase3_22_00_validation.py": 3,
    "phase3_24_00_signal_enriched_scoring.py": 4,
    "phase3_26_00_normative_compliance_validator.py": 5
}

# Artifacts outside sequence justification
EXCLUDED_ARTIFACTS = {
    "primitives": "Fundamental mathematical definitions",
    "interphase": "Interface contracts and validators",
    "contracts": "Formal phase contracts",
    "tests": "Verification suite",
    "docs": "Documentation"
}

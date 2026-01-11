"""
Monotone Compliance Contract (MCC) - Implementation
"""

from enum import IntEnum
from typing import Any


class Label(IntEnum):
    UNSAT = 0
    PARTIAL = 1
    SAT = 2


class MonotoneComplianceContract:
    @staticmethod
    def evaluate(evidence: set[str], rules: dict[str, Any]) -> Label:
        """
        Evaluates label based on evidence and Horn-like clauses.
        Simple logic:
        - SAT if all 'sat_reqs' present
        - PARTIAL if all 'partial_reqs' present
        - UNSAT otherwise
        """
        sat_reqs = set(rules.get("sat_reqs", []))
        partial_reqs = set(rules.get("partial_reqs", []))

        if sat_reqs.issubset(evidence):
            return Label.SAT
        elif partial_reqs.issubset(evidence):
            return Label.PARTIAL
        else:
            return Label.UNSAT

    @staticmethod
    def verify_monotonicity(
        evidence_subset: set[str], evidence_superset: set[str], rules: dict[str, Any]
    ) -> bool:
        """
        Verifies label(E') >= label(E) for E ⊆ E'.
        """
        if not evidence_subset.issubset(evidence_superset):
            raise ValueError("Subset is not contained in superset")

        l1 = MonotoneComplianceContract.evaluate(evidence_subset, rules)
        l2 = MonotoneComplianceContract.evaluate(evidence_superset, rules)

        return l2 >= l1

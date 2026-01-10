"""
Test MCC - Monotone Compliance Contract
Verifies: More evidence ≠ worse label (monotonic logic)
Compliance monotonicity guarantee
"""
import pytest
from pathlib import Path
from typing import Any

from cross_cutting_infrastructure.contractual.dura_lex.monotone_compliance import (
    MonotoneComplianceContract,
    Label,
)


class TestMonotoneComplianceContract:
    """MCC: Compliance label is monotonically increasing with evidence."""

    @pytest.fixture
    def compliance_rules(self) -> dict[str, Any]:
        """Phase 2 compliance rules (Horn-like clauses)."""
        return {
            "sat_reqs": ["fuente_oficial", "indicador_cuantitativo", "serie_temporal"],
            "partial_reqs": ["fuente_oficial", "indicador_cuantitativo"],
        }

    def test_mcc_001_empty_evidence_unsat(
        self, compliance_rules: dict[str, Any]
    ) -> None:
        """MCC-001: Empty evidence = UNSAT."""
        evidence: set[str] = set()
        label = MonotoneComplianceContract.evaluate(evidence, compliance_rules)
        assert label == Label.UNSAT

    def test_mcc_002_partial_evidence_partial(
        self, compliance_rules: dict[str, Any]
    ) -> None:
        """MCC-002: Partial evidence = PARTIAL."""
        evidence = {"fuente_oficial", "indicador_cuantitativo"}
        label = MonotoneComplianceContract.evaluate(evidence, compliance_rules)
        assert label == Label.PARTIAL

    def test_mcc_003_full_evidence_sat(
        self, compliance_rules: dict[str, Any]
    ) -> None:
        """MCC-003: Full evidence = SAT."""
        evidence = {"fuente_oficial", "indicador_cuantitativo", "serie_temporal"}
        label = MonotoneComplianceContract.evaluate(evidence, compliance_rules)
        assert label == Label.SAT

    def test_mcc_004_superset_evidence_sat(
        self, compliance_rules: dict[str, Any]
    ) -> None:
        """MCC-004: Superset of required evidence = SAT."""
        evidence = {
            "fuente_oficial",
            "indicador_cuantitativo",
            "serie_temporal",
            "extra_evidence",
        }
        label = MonotoneComplianceContract.evaluate(evidence, compliance_rules)
        assert label == Label.SAT

    def test_mcc_005_monotonicity_subset_superset(
        self, compliance_rules: dict[str, Any]
    ) -> None:
        """MCC-005: label(E) <= label(E') for E ⊆ E'."""
        subset = {"fuente_oficial"}
        superset = {"fuente_oficial", "indicador_cuantitativo", "serie_temporal"}
        assert MonotoneComplianceContract.verify_monotonicity(
            subset, superset, compliance_rules
        )

    def test_mcc_006_monotonicity_incremental(
        self, compliance_rules: dict[str, Any]
    ) -> None:
        """MCC-006: Adding evidence never decreases label."""
        e0: set[str] = set()
        e1 = {"fuente_oficial"}
        e2 = {"fuente_oficial", "indicador_cuantitativo"}
        e3 = {"fuente_oficial", "indicador_cuantitativo", "serie_temporal"}

        l0 = MonotoneComplianceContract.evaluate(e0, compliance_rules)
        l1 = MonotoneComplianceContract.evaluate(e1, compliance_rules)
        l2 = MonotoneComplianceContract.evaluate(e2, compliance_rules)
        l3 = MonotoneComplianceContract.evaluate(e3, compliance_rules)

        assert l0 <= l1 <= l2 <= l3

    def test_mcc_007_invalid_subset_raises(
        self, compliance_rules: dict[str, Any]
    ) -> None:
        """MCC-007: Non-subset raises ValueError."""
        not_subset = {"A", "B", "C"}
        superset = {"X", "Y", "Z"}
        with pytest.raises(ValueError, match="Subset is not contained"):
            MonotoneComplianceContract.verify_monotonicity(
                not_subset, superset, compliance_rules
            )

    def test_mcc_008_label_ordering(self) -> None:
        """MCC-008: Label enum has correct ordering."""
        assert Label.UNSAT < Label.PARTIAL < Label.SAT
        assert Label.UNSAT.value == 0
        assert Label.PARTIAL.value == 1
        assert Label.SAT.value == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

from __future__ import annotations

import pytest

from farfan_pipeline.dashboard_atroz_.pdet_colombia_data import PDETSubregion, PDET_MUNICIPALITIES


def test_pdet_reference_counts() -> None:
    assert len(PDET_MUNICIPALITIES) == 170
    assert len(set(m.dane_code for m in PDET_MUNICIPALITIES)) == 170
    assert len(set(m.subregion for m in PDET_MUNICIPALITIES)) == len(PDETSubregion) == 16


def test_pdet_reference_unique_name_department_pairs() -> None:
    pairs = {(m.name.strip().lower(), m.department.strip().lower()) for m in PDET_MUNICIPALITIES}
    assert len(pairs) == 170


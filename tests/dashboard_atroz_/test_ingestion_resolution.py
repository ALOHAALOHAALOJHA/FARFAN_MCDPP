from __future__ import annotations

from dataclasses import dataclass

from farfan_pipeline.dashboard_atroz_.ingestion import _resolve_municipality_from_context


@dataclass
class _InputData:
    document_id: str
    pdf_path: str
    run_id: str = "run_test_1"


@dataclass
class _Document:
    input_data: _InputData


def test_resolve_municipality_by_dane_code_in_document_id() -> None:
    context = {
        "document": _Document(input_data=_InputData(document_id="pdt_19050", pdf_path="/tmp/whatever.pdf")),
    }
    municipality = _resolve_municipality_from_context(context)
    assert municipality is not None
    assert municipality.dane_code == "19050"
    assert municipality.name.lower() == "argelia"


def test_resolve_municipality_by_dane_code_in_pdf_path() -> None:
    context = {
        "document": _Document(input_data=_InputData(document_id="doc_x", pdf_path="/tmp/pdt_81794.pdf")),
    }
    municipality = _resolve_municipality_from_context(context)
    assert municipality is not None
    assert municipality.dane_code == "81794"
    assert municipality.name.lower() == "tame"


from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from farfan_pipeline.core.policy_area_canonicalization import canonicalize_policy_area_id

_LEGACY_POLICY_AREA_RE = re.compile(r"\bP(?:10|[1-9])\b")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _iter_src_python_files() -> list[Path]:
    src_root = _repo_root() / "src"
    return sorted(p for p in src_root.rglob("*.py") if "__pycache__" not in p.parts)


def test_policy_area_mapping_matches_monolith() -> None:
    repo_root = _repo_root()
    mapping_path = repo_root / "policy_area_mapping.json"
    monolith_path = repo_root / "canonic_questionnaire_central" / "questionnaire_monolith.json"

    mapping_payload = json.loads(mapping_path.read_text(encoding="utf-8"))
    monolith = json.loads(monolith_path.read_text(encoding="utf-8"))
    policy_areas = monolith["canonical_notation"]["policy_areas"]

    expected = [
        {
            "legacy_id": policy_areas[canonical_id]["legacy_id"],
            "canonical_id": canonical_id,
            "canonical_name": policy_areas[canonical_id]["name"],
            "source_of_truth": "monolith",
        }
        for canonical_id in sorted(policy_areas.keys())
    ]

    assert mapping_payload == expected


def test_no_internal_legacy_policy_ids_text_scan() -> None:
    repo_root = _repo_root()
    offenders: dict[str, list[int]] = {}

    for path in _iter_src_python_files():
        line_numbers: list[int] = []
        for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if _LEGACY_POLICY_AREA_RE.search(line):
                line_numbers.append(idx)

        if line_numbers:
            offenders[str(path.relative_to(repo_root))] = line_numbers[:10]

    assert offenders == {}


def test_no_internal_legacy_policy_ids_ast_scan() -> None:
    repo_root = _repo_root()
    offenders: dict[str, list[int]] = {}

    for path in _iter_src_python_files():
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))

        hit_lines: set[int] = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
                continue
            if _LEGACY_POLICY_AREA_RE.search(node.value):
                lineno = getattr(node, "lineno", None)
                if isinstance(lineno, int):
                    hit_lines.add(lineno)

        if hit_lines:
            offenders[str(path.relative_to(repo_root))] = sorted(hit_lines)[:10]

    assert offenders == {}


def test_canonicalization_prevents_misrouting_on_overlap() -> None:
    vocab = {
        "PA01": {"mujeres", "protección"},
        "PA05": {"víctimas", "protección"},
    }

    text = "Programa de protección integral a víctimas del conflicto."
    legacy_input = "P5"

    def naive_area_pick(area_id: str) -> str:
        return area_id if area_id in vocab else "PA01"

    naive_area = naive_area_pick(legacy_input)
    assert naive_area == "PA01"
    assert "protección" in text.lower()

    canonical_area = canonicalize_policy_area_id(legacy_input)
    assert canonical_area == "PA05"

    canonical_pick = naive_area_pick(canonical_area)
    assert canonical_pick == "PA05"

    naive_matches = {term for term in vocab[naive_area] if term in text.lower()}
    canonical_matches = {term for term in vocab[canonical_pick] if term in text.lower()}

    assert naive_matches == {"protección"}
    assert canonical_matches == {"protección", "víctimas"}

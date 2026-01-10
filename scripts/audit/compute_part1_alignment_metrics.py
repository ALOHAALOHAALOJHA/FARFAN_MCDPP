"""Part I - Empirical Alignment Metrics (Plans vs. Canonical Questionnaire)

Goal
----
Quantify how well each plan text covers the *canonical* questionnaire requirements
(ONLY the 10 policy areas PA01-PA10), across:
- 300 micro questions (Q001-Q300)
- 6 dimensions (DIM01-DIM06)
- 10 policy areas (PA01-PA10)
- expected_elements (required/minimum)
- PA keyword lexicons

Outputs
-------
Writes:
- artifacts/reports/part1_alignment_metrics.json
- artifacts/reports/part1_alignment_metrics.md

Notes
-----
This is an empirical text-based coverage audit, not semantic correctness.
It measures presence/coverage signals in the plan texts.

Date context: 2026-01-05
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CANONIC = PROJECT_ROOT / "canonic_questionnaire_central"
PLANS_TEXT_DIR = PROJECT_ROOT / "artifacts" / "plans_text"
REPORT_DIR = PROJECT_ROOT / "artifacts" / "reports"

PLAN_TEXT_FILES = [
    PLANS_TEXT_DIR / "Plan_1.txt",
    PLANS_TEXT_DIR / "Plan_2.txt",
    PLANS_TEXT_DIR / "Plan_3.txt",
]

DIM_DIR = CANONIC / "dimensions"
PA_DIR = CANONIC / "policy_areas"


@dataclass(frozen=True)
class ExpectedElementSpec:
    type: str
    required: bool
    minimum: int


@dataclass(frozen=True)
class QuestionSpec:
    question_id: str
    dimension_id: str
    base_slot: str
    cluster_id: str | None
    expected_elements: tuple[ExpectedElementSpec, ...]

    @property
    def pa_id(self) -> str:
        # Q001-Q300 -> PA01..PA10 (30 each)
        m = re.fullmatch(r"Q(\d{3})", self.question_id)
        if not m:
            return "PA??"
        n = int(m.group(1))
        pa = (n - 1) // 30 + 1
        return f"PA{pa:02d}" if 1 <= pa <= 10 else "PA??"


def _safe_int(v: Any, default: int = 1) -> int:
    try:
        return int(v)
    except Exception:
        return default


def load_dimension_questions() -> list[QuestionSpec]:
    questions: list[QuestionSpec] = []
    for dim_folder in sorted(DIM_DIR.iterdir()):
        if not dim_folder.is_dir():
            continue
        questions_path = dim_folder / "questions.json"
        if not questions_path.exists():
            continue

        data = json.loads(questions_path.read_text(encoding="utf-8"))
        dim_id = data.get("dimension_id") or data.get("dimension_metadata", {}).get("dimension_id")
        for q in data.get("questions", []):
            qid = q.get("question_id")
            if not qid:
                continue
            expected: list[ExpectedElementSpec] = []
            for el in q.get("expected_elements", []) or []:
                et = str(el.get("type", "")).strip()
                if not et:
                    continue
                required = bool(el.get("required", False))
                minimum = _safe_int(el.get("minimum", 1), default=1)
                expected.append(ExpectedElementSpec(type=et, required=required, minimum=minimum))

            questions.append(
                QuestionSpec(
                    question_id=str(qid),
                    dimension_id=str(q.get("dimension_id", dim_id) or dim_id),
                    base_slot=str(q.get("base_slot", "")),
                    cluster_id=q.get("cluster_id"),
                    expected_elements=tuple(expected),
                )
            )

    # Guard: ensure we got 300 distinct Q ids
    unique_ids = {q.question_id for q in questions}
    if len(unique_ids) != 300:
        raise RuntimeError(
            f"Expected 300 distinct questions, got {len(unique_ids)} (raw={len(questions)})."
        )

    # Prefer one QuestionSpec per question_id (should already be unique)
    by_id: dict[str, QuestionSpec] = {q.question_id: q for q in questions}
    return [by_id[qid] for qid in sorted(by_id.keys())]


def load_pa_keywords() -> dict[str, list[str]]:
    keywords_by_pa: dict[str, list[str]] = {}
    for pa_folder in sorted(PA_DIR.iterdir()):
        if not pa_folder.is_dir():
            continue
        keywords_path = pa_folder / "keywords.json"
        metadata_path = pa_folder / "metadata.json"
        if not keywords_path.exists() or not metadata_path.exists():
            continue
        meta = json.loads(metadata_path.read_text(encoding="utf-8"))
        pa_id = meta.get("policy_area_id")
        if not pa_id:
            continue
        kw = json.loads(keywords_path.read_text(encoding="utf-8")).get("keywords", [])
        keywords_by_pa[str(pa_id)] = [str(x) for x in kw if str(x).strip()]

    # Guard
    if len(keywords_by_pa) != 10:
        raise RuntimeError(f"Expected 10 policy areas with keywords, got {len(keywords_by_pa)}")
    return keywords_by_pa


def normalize_text(s: str) -> str:
    # Keep accents; lowercase for matching.
    return s.lower()


def compile_regex(pattern: str) -> re.Pattern[str]:
    return re.compile(pattern, re.IGNORECASE | re.MULTILINE)


# -----------------------------------------------------------------------------
# Expected element detectors
# -----------------------------------------------------------------------------
# These are conservative, Colombian PDM-oriented heuristics.
# We count matches, then score vs. element.minimum.

DETECTORS: dict[str, list[re.Pattern[str]]] = {
    # Territorial specificity
    "cobertura_territorial_especificada": [
        compile_regex(r"\b(urbano|rural|cabecera|corregimiento|vereda|resguardo|comuna|barrio)\b"),
        compile_regex(r"\b(municipio|territorio|territorial|zona)\b"),
    ],
    "desagregacion_territorial": [
        compile_regex(r"\b(urbano|rural|cabecera|corregimiento|vereda|resguardo|comuna|barrio)\b"),
    ],
    # Official sources
    "fuentes_oficiales": [
        compile_regex(r"\b(DANE|DNP|SISBEN|SISBÉN|SISPT|SGR|SGP|OCAD|ART|ICBF|SIVIGILA|RUV|SUI)\b"),
        compile_regex(
            r"\b(ministerio|minsalud|mineducación|mineducacion|minambiente|policía|policia)\b"
        ),
        compile_regex(r"\b(registro\s+único\s+de\s+víctimas|registro\s+unico\s+de\s+victimas)\b"),
    ],
    "official_stats": [
        compile_regex(r"\b(DANE|DNP)\b"),
    ],
    "official_documents": [
        compile_regex(
            r"\b(ley\s+\d+|decreto\s+\d+|conpes|acuerdo\s+no\.?|acto\s+administrativo)\b"
        ),
    ],
    # Quant indicators / baselines / targets
    "indicadores_cuantitativos": [
        compile_regex(r"\b(indicador(?:es)?|tasa|porcentaje|%|índice|indice|ratio|cobertura)\b"),
        compile_regex(r"\b\d{1,3}(?:[\.,]\d{1,2})?\s*(%|por\s+ciento)\b"),
        compile_regex(r"\b\d{1,3}(?:[\.,]\d{3})+(?:[\.,]\d+)?\b"),
    ],
    "linea_base": [
        compile_regex(r"\b(l[ií]nea\s+base|baseline)\b"),
    ],
    "linea_base_cuantitativa": [
        compile_regex(r"\b(l[ií]nea\s+base)\b"),
        compile_regex(r"\b\d{1,3}(?:[\.,]\d{1,2})?\s*(%|por\s+ciento)?\b"),
    ],
    "meta": [
        compile_regex(r"\b(meta(?:s)?|objetivo(?:s)?)\b"),
    ],
    "meta_cuatrienio": [
        compile_regex(
            r"\b(meta\s+cuatrienio|cuatrienio\s+\(20\d{2}-20\d{2}\)|20\d{2}\s*[-–]\s*20\d{2})\b"
        ),
    ],
    "unidad_medida": [
        compile_regex(
            r"\b(unidad\s+de\s+medida|unidad(?:es)?|km|hect[aá]rea(?:s)?|vivienda(?:s)?|persona(?:s)?|familia(?:s)?)\b"
        ),
    ],
    "fuente_verificacion": [
        compile_regex(r"\b(fuente\s+de\s+verificaci[oó]n|fuente)\b"),
    ],
    # Temporal series
    "series_temporales_años": [
        compile_regex(r"\b(19\d{2}|20\d{2})\b"),
    ],
    "año_referencia": [
        compile_regex(r"\b(19\d{2}|20\d{2})\b"),
    ],
    # Budget / financing / traceability
    "recursos_identificados": [
        compile_regex(
            r"\b(presupuesto|financiaci[oó]n|recursos|inversi[oó]n|fuente(?:s)?\s+de\s+financiaci[oó]n)\b"
        ),
        compile_regex(r"\b(PPI|plan\s+plurianual\s+de\s+inversiones|marco\s+fiscal)\b"),
        compile_regex(r"\b(SGP|SGR|regal[ií]as)\b"),
    ],
    "trazabilidad_presupuestal": [
        compile_regex(r"\b(PPI|plan\s+plurianual\s+de\s+inversiones)\b"),
    ],
    # Participation / governance
    "participacion_efectiva": [
        compile_regex(
            r"\b(participaci[oó]n\s+ciudadana|mesa(?:s)?\s+de\s+trabajo|audiencia(?:s)?\s+p[uú]blica(?:s)?)\b"
        ),
    ],
    "responsable_medicion": [
        compile_regex(r"\b(responsable|secretar[ií]a|dependencia|entidad)\b"),
    ],
    # Causal / theory of change
    "supuestos_clave": [
        compile_regex(r"\b(supuesto(?:s)?|riesgo(?:s)?)\b"),
    ],
}


def count_detector_hits(text_norm: str, patterns: list[re.Pattern[str]]) -> int:
    hits = 0
    for pat in patterns:
        hits += len(pat.findall(text_norm))
    return hits


def count_distinct_years(text_norm: str) -> int:
    years = set(re.findall(r"\b(19\d{2}|20\d{2})\b", text_norm, flags=re.IGNORECASE))
    # Defensive: ignore far-future or odd OCR artifacts
    yrs_int = {int(y) for y in years if y.isdigit()}
    yrs_int = {y for y in yrs_int if 1950 <= y <= 2099}
    return len(yrs_int)


def count_distinct_institutions(text_norm: str) -> int:
    inst = set(
        re.findall(
            r"\b(DANE|DNP|SISBEN|SISBÉN|SISPT|SGR|SGP|OCAD|ART|ICBF|SIVIGILA|RUV|SUI)\b",
            text_norm,
            flags=re.IGNORECASE,
        )
    )
    return len(inst)


def element_score(element: ExpectedElementSpec, text_norm: str) -> tuple[float, int, str]:
    # Special handling for some types where "hits" should mean distinct items
    if element.type in ("series_temporales_años", "año_referencia"):
        hits = count_distinct_years(text_norm)
        minimum = max(1, element.minimum)
        return (min(hits / minimum, 1.0), hits, "OK")

    if element.type in ("fuentes_oficiales", "official_stats"):
        hits = count_distinct_institutions(text_norm)
        minimum = max(1, element.minimum)
        return (min(hits / minimum, 1.0), hits, "OK")

    # For "línea base cuantitativa", require co-occurrence within a window
    if element.type == "linea_base_cuantitativa":
        pat = re.compile(
            r"(l[ií]nea\s+base.{0,80}\d|\d.{0,80}l[ií]nea\s+base)", re.IGNORECASE | re.MULTILINE
        )
        hits = len(pat.findall(text_norm))
        minimum = max(1, element.minimum)
        return (min(hits / minimum, 1.0), hits, "OK")

    detectors = DETECTORS.get(element.type, [])
    if not detectors:
        return (math.nan, 0, "NO_DETECTOR")

    hits = count_detector_hits(text_norm, detectors)
    minimum = max(1, element.minimum)
    score = min(hits / minimum, 1.0)
    return (score, hits, "OK")


def keyword_coverage(text_norm: str, keywords: list[str]) -> tuple[float, int, int]:
    if not keywords:
        return (math.nan, 0, 0)

    found = 0
    # exact-ish, but case-insensitive substring in normalized text
    for kw in keywords:
        k = kw.strip().lower()
        if not k:
            continue
        if k in text_norm:
            found += 1

    return (found / len(keywords), found, len(keywords))


def pctl(values: list[float], p: float) -> float:
    if not values:
        return math.nan
    xs = sorted(values)
    if p <= 0:
        return xs[0]
    if p >= 1:
        return xs[-1]
    k = (len(xs) - 1) * p
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return xs[int(k)]
    d0 = xs[f] * (c - k)
    d1 = xs[c] * (k - f)
    return d0 + d1


def summarize(values: Iterable[float]) -> dict[str, float | None]:
    xs = [v for v in values if not math.isnan(v)]
    if not xs:
        return {"mean": None, "p10": None, "min": None}
    return {
        "mean": round(mean(xs), 4),
        "p10": round(pctl(xs, 0.10), 4),
        "min": round(min(xs), 4),
    }


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    questions = load_dimension_questions()
    keywords_by_pa = load_pa_keywords()

    plan_texts: dict[str, str] = {}
    for f in PLAN_TEXT_FILES:
        if not f.exists():
            raise FileNotFoundError(f"Missing plan text artifact: {f}")
        plan_texts[f.stem] = normalize_text(f.read_text(encoding="utf-8", errors="replace"))

    # Evaluate
    results: dict[str, Any] = {
        "date": "2026-01-05",
        "plans": list(plan_texts.keys()),
        "question_count": len(questions),
        "dimensions": sorted({q.dimension_id for q in questions}),
        "policy_areas": [f"PA{i:02d}" for i in range(1, 11)],
        "detector_coverage": {
            "known_element_types": sorted(DETECTORS.keys()),
            "unknown_element_types": [],
        },
        "per_plan": {},
        "convergence": {},
    }

    all_element_types = sorted({el.type for q in questions for el in q.expected_elements})
    unknown = [t for t in all_element_types if t not in DETECTORS]
    results["detector_coverage"]["unknown_element_types"] = unknown

    # Per plan details
    per_plan_question_scores: dict[str, dict[str, float]] = {}
    per_plan_question_scores_canonical: dict[str, dict[str, float]] = {}

    for plan_name, text_norm in plan_texts.items():
        per_question: dict[str, Any] = {}
        question_scores: dict[str, float] = {}
        question_scores_canonical: dict[str, float] = {}

        # Aggregate by dimension/PA
        dim_scores: dict[str, list[float]] = {}
        pa_scores: dict[str, list[float]] = {}
        element_type_scores: dict[str, list[float]] = {}

        for q in questions:
            element_scores: list[float] = []
            element_scores_canonical: list[float] = []
            element_details: list[dict[str, Any]] = []

            for el in q.expected_elements:
                sc, hits, status = element_score(el, text_norm)

                # Keep for aggregation, but only if detector exists
                if not math.isnan(sc):
                    element_scores.append(sc)
                    element_type_scores.setdefault(el.type, []).append(sc)
                    element_scores_canonical.append(sc)
                else:
                    # Canonical score penalizes unknown types as 0 until we implement detectors
                    element_scores_canonical.append(0.0)

                element_details.append(
                    {
                        "type": el.type,
                        "required": el.required,
                        "minimum": el.minimum,
                        "score": None if math.isnan(sc) else round(sc, 4),
                        "hits": hits,
                        "status": status,
                    }
                )

            # Question-level score: mean over scorable expected elements.
            q_score = mean(element_scores) if element_scores else math.nan
            question_scores[q.question_id] = q_score

            # Canonical question score: include unknown expected_elements as 0.
            q_score_canonical = (
                mean(element_scores_canonical) if element_scores_canonical else math.nan
            )
            question_scores_canonical[q.question_id] = q_score_canonical

            dim_scores.setdefault(q.dimension_id, []).append(q_score)
            pa_scores.setdefault(q.pa_id, []).append(q_score)

            per_question[q.question_id] = {
                "dimension_id": q.dimension_id,
                "policy_area": q.pa_id,
                "base_slot": q.base_slot,
                "expected_elements": element_details,
                "question_score": None if math.isnan(q_score) else round(q_score, 4),
                "question_score_canonical": (
                    None if math.isnan(q_score_canonical) else round(q_score_canonical, 4)
                ),
            }

        # Keyword coverage per PA
        pa_keyword: dict[str, Any] = {}
        for pa_id, kws in keywords_by_pa.items():
            cov, found, total = keyword_coverage(text_norm, kws)
            pa_keyword[pa_id] = {
                "keyword_coverage": None if math.isnan(cov) else round(cov, 4),
                "keywords_found": found,
                "keywords_total": total,
            }

        # Summaries
        q_values = [v for v in question_scores.values() if not math.isnan(v)]
        q_values_canonical = [v for v in question_scores_canonical.values() if not math.isnan(v)]
        overall = {
            "question_score_mean": round(mean(q_values), 4) if q_values else None,
            "question_score_p10": round(pctl(q_values, 0.10), 4) if q_values else None,
            "question_score_min": round(min(q_values), 4) if q_values else None,
            "question_score_std": round(pstdev(q_values), 4) if len(q_values) > 1 else 0.0,
            "question_score_canonical_mean": (
                round(mean(q_values_canonical), 4) if q_values_canonical else None
            ),
            "question_score_canonical_p10": (
                round(pctl(q_values_canonical, 0.10), 4) if q_values_canonical else None
            ),
            "question_score_canonical_min": (
                round(min(q_values_canonical), 4) if q_values_canonical else None
            ),
            "question_score_canonical_std": (
                round(pstdev(q_values_canonical), 4) if len(q_values_canonical) > 1 else 0.0
            ),
        }

        # Dimension / PA summaries
        dim_summary = {dim: summarize(xs) for dim, xs in dim_scores.items()}
        pa_summary = {pa: summarize(xs) for pa, xs in pa_scores.items()}

        # Worst questions
        worst = sorted(
            ((qid, sc) for qid, sc in question_scores.items() if not math.isnan(sc)),
            key=lambda t: t[1],
        )[:20]

        worst_canonical = sorted(
            ((qid, sc) for qid, sc in question_scores_canonical.items() if not math.isnan(sc)),
            key=lambda t: t[1],
        )[:20]

        results["per_plan"][plan_name] = {
            "overall": overall,
            "by_dimension": dim_summary,
            "by_policy_area": pa_summary,
            "by_policy_area_keywords": pa_keyword,
            "worst_questions": [{"question_id": qid, "score": round(sc, 4)} for qid, sc in worst],
            "worst_questions_canonical": [
                {"question_id": qid, "score": round(sc, 4)} for qid, sc in worst_canonical
            ],
            "per_question": per_question,
            "element_type_summary": {et: summarize(xs) for et, xs in element_type_scores.items()},
        }
        per_plan_question_scores[plan_name] = {
            qid: sc for qid, sc in question_scores.items() if not math.isnan(sc)
        }
        per_plan_question_scores_canonical[plan_name] = {
            qid: sc for qid, sc in question_scores_canonical.items() if not math.isnan(sc)
        }

    # Convergence across plans (only questions that have scores everywhere)
    common_qids = set.intersection(*(set(d.keys()) for d in per_plan_question_scores.values()))
    common_scores_matrix: dict[str, list[float]] = {}
    for qid in sorted(common_qids):
        common_scores_matrix[qid] = [per_plan_question_scores[p][qid] for p in plan_texts.keys()]

    per_q_mean = {qid: mean(vs) for qid, vs in common_scores_matrix.items()}
    per_q_min = {qid: min(vs) for qid, vs in common_scores_matrix.items()}
    per_q_std = {
        qid: (pstdev(vs) if len(vs) > 1 else 0.0) for qid, vs in common_scores_matrix.items()
    }

    means = list(per_q_mean.values())
    mins = list(per_q_min.values())

    results["convergence"] = {
        "question_mean_of_means": round(mean(means), 4) if means else None,
        "question_mean_of_mins": round(mean(mins), 4) if mins else None,
        "question_p10_of_mins": round(pctl(mins, 0.10), 4) if mins else None,
        "most_divergent_questions": [
            {
                "question_id": qid,
                "mean": round(per_q_mean[qid], 4),
                "min": round(per_q_min[qid], 4),
                "std": round(per_q_std[qid], 4),
            }
            for qid, _ in sorted(per_q_std.items(), key=lambda t: t[1], reverse=True)[:25]
        ],
        "lowest_common_questions": [
            {
                "question_id": qid,
                "mean": round(per_q_mean[qid], 4),
                "min": round(per_q_min[qid], 4),
                "std": round(per_q_std[qid], 4),
            }
            for qid, _ in sorted(per_q_min.items(), key=lambda t: t[1])[:25]
        ],
    }

    # Canonical convergence (penalizing unknown expected_elements)
    common_qids_canonical = set.intersection(
        *(set(d.keys()) for d in per_plan_question_scores_canonical.values())
    )
    common_scores_matrix_canonical: dict[str, list[float]] = {}
    for qid in sorted(common_qids_canonical):
        common_scores_matrix_canonical[qid] = [
            per_plan_question_scores_canonical[p][qid] for p in plan_texts.keys()
        ]
    per_q_mean_c = {qid: mean(vs) for qid, vs in common_scores_matrix_canonical.items()}
    per_q_min_c = {qid: min(vs) for qid, vs in common_scores_matrix_canonical.items()}
    per_q_std_c = {
        qid: (pstdev(vs) if len(vs) > 1 else 0.0)
        for qid, vs in common_scores_matrix_canonical.items()
    }
    means_c = list(per_q_mean_c.values())
    mins_c = list(per_q_min_c.values())
    results["convergence_canonical"] = {
        "question_mean_of_means": round(mean(means_c), 4) if means_c else None,
        "question_mean_of_mins": round(mean(mins_c), 4) if mins_c else None,
        "question_p10_of_mins": round(pctl(mins_c, 0.10), 4) if mins_c else None,
        "most_divergent_questions": [
            {
                "question_id": qid,
                "mean": round(per_q_mean_c[qid], 4),
                "min": round(per_q_min_c[qid], 4),
                "std": round(per_q_std_c[qid], 4),
            }
            for qid, _ in sorted(per_q_std_c.items(), key=lambda t: t[1], reverse=True)[:25]
        ],
        "lowest_common_questions": [
            {
                "question_id": qid,
                "mean": round(per_q_mean_c[qid], 4),
                "min": round(per_q_min_c[qid], 4),
                "std": round(per_q_std_c[qid], 4),
            }
            for qid, _ in sorted(per_q_min_c.items(), key=lambda t: t[1])[:25]
        ],
    }

    # Write JSON
    out_json = REPORT_DIR / "part1_alignment_metrics.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    # Write Markdown summary (compact)
    out_md = REPORT_DIR / "part1_alignment_metrics.md"
    md_lines: list[str] = []
    md_lines.append("# Parte I — Métricas de alineación empírica (Planes vs. Canónico)\n")
    md_lines.append("\n## Resumen\n")
    md_lines.append(f"- Fecha: {results['date']}")
    md_lines.append(f"- Planes: {', '.join(results['plans'])}")
    md_lines.append(f"- Preguntas evaluadas: {results['question_count']} (Q001–Q300)")
    md_lines.append(f"- Tipos de expected_elements: {len(all_element_types)}")
    md_lines.append(f"- Tipos sin detector: {len(unknown)}")

    md_lines.append("\n## Convergencia (entre planes)\n")
    conv = results["convergence"]
    md_lines.append(f"- Media de medias (pregunta): {conv['question_mean_of_means']}")
    md_lines.append(f"- Media de mínimos (pregunta): {conv['question_mean_of_mins']}")
    md_lines.append(f"- P10 de mínimos (pregunta): {conv['question_p10_of_mins']}")

    md_lines.append("\n## Convergencia CANONICAL (penaliza expected_elements sin detector)\n")
    convc = results.get("convergence_canonical", {})
    md_lines.append(f"- Media de medias (pregunta): {convc.get('question_mean_of_means')}")
    md_lines.append(f"- Media de mínimos (pregunta): {convc.get('question_mean_of_mins')}")
    md_lines.append(f"- P10 de mínimos (pregunta): {convc.get('question_p10_of_mins')}")

    md_lines.append("\n## Por plan (score de preguntas basado en expected_elements)\n")
    for plan_name in results["plans"]:
        p = results["per_plan"][plan_name]["overall"]
        md_lines.append(f"\n### {plan_name}\n")
        md_lines.append(
            f"- OBS mean={p['question_score_mean']} p10={p['question_score_p10']} min={p['question_score_min']} std={p['question_score_std']}"
        )
        md_lines.append(
            f"- CAN mean={p['question_score_canonical_mean']} p10={p['question_score_canonical_p10']} min={p['question_score_canonical_min']} std={p['question_score_canonical_std']}"
        )

    md_lines.append("\n## 20 preguntas con menor score (por plan)\n")
    for plan_name in results["plans"]:
        md_lines.append(f"\n### {plan_name}\n")
        for item in results["per_plan"][plan_name]["worst_questions"]:
            md_lines.append(f"- {item['question_id']}: {item['score']}")

        md_lines.append("\nPeores (CANONICAL)\n")
        for item in results["per_plan"][plan_name]["worst_questions_canonical"]:
            md_lines.append(f"- {item['question_id']}: {item['score']}")

    md_lines.append("\n## Nota metodológica\n")
    md_lines.append(
        "- OBS (observable): score por pregunta = media de expected_elements con detector. "
        "Los NO_DETECTOR no entran en la media."
    )
    md_lines.append(
        "- CAN (canonical): score por pregunta = media incluyendo NO_DETECTOR como 0.0 (penaliza brechas de instrumentación)."
    )
    md_lines.append(
        "- Keyword coverage por PA se calcula aparte (presencia de keywords en el texto)."
    )

    out_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(f"WROTE {out_json}")
    print(f"WROTE {out_md}")
    print(f"Unknown element types without detectors: {len(unknown)}")
    if unknown:
        print("First 30 unknown types:", unknown[:30])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

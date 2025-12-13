"""
Analyzer One calibration pipeline producing canonical artifacts.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ontology.canonical_value_chain import VALUE_CHAIN_DIMENSIONS


ARTIFACT_ROOT = Path("artifacts/plan1")
CG_ROOT = ARTIFACT_ROOT / "canonical_ground_truth"
CAL_ROOT = ARTIFACT_ROOT / "calibration"
TEST_ROOT = ARTIFACT_ROOT / "tests"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def resolve_patterns(monolith: Dict[str, Any], registry: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    patterns_source: List[Dict[str, Any]]
    if isinstance(registry, list):
        patterns_source = registry
    elif isinstance(registry, dict):
        patterns_source = registry.get("patterns", [])
    else:
        raise TypeError(f"Unsupported pattern registry type: {type(registry).__name__}")

    registry_index = {
        (item.get("id") or item.get("pattern_id")): item for item in patterns_source if isinstance(item, dict)
    }
    resolved: List[Dict[str, Any]] = []
    missing: List[str] = []
    pattern_usage = defaultdict(int)
    for mq in monolith.get("blocks", {}).get("micro_questions", []):
        for pat in mq.get("patterns", []) or []:
            pattern_ref = pat.get("pattern_ref")
            if pattern_ref:
                src = registry_index.get(pattern_ref)
                if not src:
                    missing.append(pattern_ref)
                    continue
                pattern_usage[pattern_ref] += 1
                resolved.append(
                    {
                        "pattern_ref": pattern_ref,
                        "pattern_id_source": src.get("id") or src.get("pattern_id"),
                        "pattern_resolved": src.get("pattern"),
                        "match_type": src.get("match_type"),
                        "usage_count": src.get("usage_count", 0),
                    }
                )
            else:
                resolved.append(
                    {
                        "pattern_ref": pat.get("id"),
                        "pattern_id_source": pat.get("id"),
                        "pattern_resolved": pat.get("pattern"),
                        "match_type": pat.get("match_type"),
                        "usage_count": pat.get("usage_count", 0),
                    }
                )
    if missing:
        raise ValueError(f"Missing pattern_refs: {sorted(set(missing))}")
    return resolved, pattern_usage


def build_monolith_index(monolith: Dict[str, Any], resolved_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
    micro = monolith.get("blocks", {}).get("micro_questions", [])
    if len(micro) != 300:
        raise ValueError(f"Micro question count mismatch: {len(micro)} != 300")
    questions_by_base: Dict[str, List[str]] = defaultdict(list)
    expected_by_base: Dict[str, List[str]] = defaultdict(list)
    patterns_by_q: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    questions_by_dim: Dict[str, List[str]] = defaultdict(list)
    questions_by_pa: Dict[str, List[str]] = defaultdict(list)
    resolved_map = {p["pattern_ref"]: p for p in resolved_patterns}
    for mq in micro:
        qid = mq["question_id"]
        base = mq["base_slot"]
        dim = mq["dimension_id"]
        pa = mq["policy_area_id"]
        questions_by_base[base].append(qid)
        expected_by_base[base].extend(mq.get("expected_elements", []))
        questions_by_dim[dim].append(qid)
        questions_by_pa[pa].append(qid)
        for pat in mq.get("patterns", []) or []:
            pref = pat.get("pattern_ref") or pat.get("id")
            res = resolved_map.get(pref)
            if res:
                patterns_by_q[qid].append(res)
    return {
        "integrity": monolith.get("integrity", {}),
        "questions_by_base_slot": questions_by_base,
        "expected_elements_by_base_slot": expected_by_base,
        "patterns_by_question_id": patterns_by_q,
        "questions_by_dimension_id": questions_by_dim,
        "questions_by_policy_area_id": questions_by_pa,
    }


def build_unit_of_analysis_index(report_path: Path) -> Dict[str, Any]:
    if not report_path.exists():
        raise FileNotFoundError(str(report_path))
    report = load_json(report_path)
    return {
        "source_examples": report.get("examples", []),
        "section_headers": report.get("section_headers", []),
        "table_columns": report.get("table_columns", {}),
        "causal_connectors": report.get("causal_connectors", []),
        "temporal_expressions": report.get("temporal_expressions", []),
    }


def compute_vocab_tokens(monolith_index: Dict[str, Any], unit_index: Dict[str, Any]) -> List[str]:
    tokens: List[str] = []
    for expected_list in monolith_index["expected_elements_by_base_slot"].values():
        for elem in expected_list:
            elem_text: str | None = None
            if isinstance(elem, str):
                elem_text = elem
            elif isinstance(elem, dict):
                elem_type = elem.get("type")
                if isinstance(elem_type, str):
                    elem_text = elem_type
            if elem_text:
                tokens.extend(re.findall(r"[\wáéíóúñ]+", elem_text.lower()))
    for qids in monolith_index["questions_by_base_slot"].values():
        for qid in qids:
            pass  # no text content available here
    for header in unit_index.get("section_headers", []):
        tokens.extend(re.findall(r"[\wáéíóúñ]+", header.lower()))
    for cols in unit_index.get("table_columns", {}).values():
        for col in cols:
            tokens.extend(re.findall(r"[\wáéíóúñ]+", col.lower()))
    for conn in unit_index.get("causal_connectors", []):
        tokens.extend(re.findall(r"[\wáéíóúñ]+", conn.lower()))
    for tmp in unit_index.get("temporal_expressions", []):
        tokens.extend(re.findall(r"[\wáéíóúñ]+", tmp.lower()))
    for dim in VALUE_CHAIN_DIMENSIONS.values():
        for kw in dim.get("keywords_general", []):
            tokens.extend(re.findall(r"[\wáéíóúñ]+", kw.lower()))
    return tokens


def compute_vectorizer_params(tokens: List[str]) -> Dict[str, Any]:
    vocab = set(tokens)
    vocab_size = len(vocab)
    if vocab_size == 0:
        raise ValueError("Calibration failed: empty token vocabulary derived from repo data")
    alpha = 1 + (0 / vocab_size if vocab_size else 0)
    max_features = math.ceil(alpha * vocab_size) if vocab_size else 0
    phrase_lengths: List[int] = []
    phrase_lengths.extend([len(t.split()) for t in vocab])
    if phrase_lengths:
        p90 = int(np.percentile(phrase_lengths, 90))
    else:
        p90 = 1
    max_n = min(5, max(2, p90))
    return {
        "vocab_size_total": vocab_size,
        "alpha": alpha,
        "max_features": max_features,
        "ngram_range": (1, max_n),
        "p50_phrase_len": int(np.percentile(phrase_lengths, 50)) if phrase_lengths else 1,
        "p90_phrase_len": p90,
    }


def calibrate_thresholds(monolith: Dict[str, Any], monolith_index: Dict[str, Any], vec_params: Dict[str, Any]) -> Dict[str, Any]:
    micro = monolith.get("blocks", {}).get("micro_questions", [])
    base_to_segments = defaultdict(list)
    for mq in micro:
        base_to_segments[mq["base_slot"]].append(mq.get("text", ""))
    vectorizer = TfidfVectorizer(max_features=vec_params["max_features"], ngram_range=vec_params["ngram_range"])
    thresholds: Dict[str, Any] = {}
    for base, pos_segments in base_to_segments.items():
        neg_segments = []
        for other_base, segs in base_to_segments.items():
            if other_base != base:
                neg_segments.extend(segs)
        if not pos_segments or not neg_segments:
            thresholds[base] = {"error": "missing_positive_or_negative", "success": False}
            continue
        corpus = pos_segments + neg_segments
        X = vectorizer.fit_transform(corpus)
        pos_vec = X[: len(pos_segments)]
        neg_vec = X[len(pos_segments) :]
        sim_pos = cosine_similarity(pos_vec, pos_vec).flatten()
        sim_neg = cosine_similarity(pos_vec, neg_vec).flatten()
        median_pos = float(np.median(sim_pos))
        median_neg = float(np.median(sim_neg))
        iqr_pos = float(np.percentile(sim_pos, 75) - np.percentile(sim_pos, 25))
        iqr_neg = float(np.percentile(sim_neg, 75) - np.percentile(sim_neg, 25))
        lam = min(1.0, (median_pos - median_neg) / (iqr_pos + iqr_neg + 1e-6))
        tau = max(median_neg + lam * iqr_neg, median_pos - lam * iqr_pos)
        thresholds[base] = {
            "median_pos": median_pos,
            "median_neg": median_neg,
            "iqr_pos": iqr_pos,
            "iqr_neg": iqr_neg,
            "lambda": lam,
            "threshold": float(tau),
            "pos_count": len(pos_segments),
            "neg_count": len(neg_segments),
            "success": True,
        }
    return thresholds


def _expected_base_slots() -> List[str]:
    return [
        slot
        for dim_id in sorted(VALUE_CHAIN_DIMENSIONS)
        for slot in VALUE_CHAIN_DIMENSIONS[dim_id]["base_slots"]
    ]


def _build_thresholds_by_base_slot(thresholds_detail: Dict[str, Any]) -> Dict[str, float]:
    expected = _expected_base_slots()
    missing = [slot for slot in expected if slot not in thresholds_detail]
    if missing:
        raise KeyError(f"Missing thresholds for base slots: {missing}")

    thresholds_by_slot: Dict[str, float] = {}
    for slot in expected:
        entry = thresholds_detail[slot]
        if not isinstance(entry, dict) or not entry.get("success"):
            raise ValueError(f"Threshold calibration failed for slot {slot}: {entry}")
        raw = entry.get("threshold")
        if not isinstance(raw, (int, float)):
            raise TypeError(f"Invalid threshold type for slot {slot}: {type(raw).__name__}")
        value = float(raw)
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"Invalid threshold range for slot {slot}: {value}")
        thresholds_by_slot[slot] = value
    return thresholds_by_slot


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    _ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))


def run_pipeline(
    monolith_path: Path = Path("canonic_questionnaire_central/questionnaire_monolith.json"),
    registry_path: Path = Path("canonic_questionnaire_central/pattern_registry.json"),
    pdt_report_path: Path = Path("pdt_analysis_report.json"),
) -> Dict[str, Any]:
    monolith = load_json(monolith_path)
    registry = load_json(registry_path)
    resolved_patterns, pattern_usage = resolve_patterns(monolith, registry)
    write_json(CG_ROOT / "pattern_registry_resolved.json", resolved_patterns)

    monolith_index = build_monolith_index(monolith, resolved_patterns)
    write_json(CG_ROOT / "monolith_index.json", monolith_index)

    try:
        unit_index = build_unit_of_analysis_index(pdt_report_path)
    except FileNotFoundError as exc:
        unit_index = {"error": str(exc), "success": False}
    write_json(CG_ROOT / "unit_of_analysis_index.json", unit_index)

    tokens = compute_vocab_tokens(monolith_index, unit_index if isinstance(unit_index, dict) else {})
    vec_params = compute_vectorizer_params(tokens)
    thresholds_detail = calibrate_thresholds(monolith, monolith_index, vec_params)
    thresholds_by_base_slot = _build_thresholds_by_base_slot(thresholds_detail)
    calibration = {
        "inputs": {
            "monolith_hash": _sha256_file(monolith_path),
            "pattern_registry_hash": _sha256_file(registry_path),
            "pdt_analysis_report_hash": _sha256_file(pdt_report_path) if pdt_report_path.exists() else None,
        },
        "max_features": vec_params["max_features"],
        "ngram_range": vec_params["ngram_range"],
        "thresholds_by_base_slot": thresholds_by_base_slot,
        "vectorizer": vec_params,
        "thresholds_detail_by_base_slot": thresholds_detail,
    }
    write_json(CAL_ROOT / "analyzer_one_calibration.json", calibration)
    value_chain_quant = {
        "success": False,
        "reason": "Pending integration",
        "hashes": calibration["inputs"],
    }
    write_json(CAL_ROOT / "value_chain_quantification.json", value_chain_quant)

    smoke = {
        "hashes": {
            "monolith": calibration["inputs"]["monolith_hash"],
            "pattern_registry": calibration["inputs"]["pattern_registry_hash"],
            "pdt_analysis_report": calibration["inputs"]["pdt_analysis_report_hash"],
            "pattern_registry_resolved": _sha256_file(CG_ROOT / "pattern_registry_resolved.json"),
            "monolith_index": _sha256_file(CG_ROOT / "monolith_index.json"),
            "unit_of_analysis_index": _sha256_file(CG_ROOT / "unit_of_analysis_index.json"),
            "analyzer_one_calibration": _sha256_file(CAL_ROOT / "analyzer_one_calibration.json"),
            "value_chain_quantification": _sha256_file(CAL_ROOT / "value_chain_quantification.json"),
        },
        "counts": {
            "base_slots_present": len(monolith_index.get("questions_by_base_slot", {})),
            "question_ids_present": sum(len(v) for v in monolith_index.get("questions_by_base_slot", {}).values()),
            "pattern_refs_resolved_count": len(resolved_patterns),
        },
        "failures": [],
        "success": True,
    }
    if "error" in unit_index:
        smoke["failures"].append(unit_index["error"])
        smoke["success"] = False
    write_json(TEST_ROOT / "analyzer_one_smoke_report.json", smoke)
    return smoke


if __name__ == "__main__":
    run_pipeline()

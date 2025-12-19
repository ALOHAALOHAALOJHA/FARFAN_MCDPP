from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterator


class HarvestError(RuntimeError):
    pass


def utc_now_z() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def parse_range_q(range_expr: str) -> list[str]:
    m = re.fullmatch(r"Q(\d{3})-Q(\d{3})", range_expr.strip())
    if not m:
        raise HarvestError(f"Invalid range: {range_expr!r} expected Q001-Q030")
    a = int(m.group(1))
    b = int(m.group(2))
    if b < a:
        raise HarvestError(f"Invalid range bounds: {range_expr!r}")
    return [f"Q{i:03d}" for i in range(a, b + 1)]


def walk(x: Any, path: str = "$") -> Iterator[tuple[str, Any]]:
    yield path, x
    if isinstance(x, dict):
        for k in sorted(x.keys()):
            yield from walk(x[k], f"{path}.{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from walk(v, f"{path}[{i}]")


PLACEHOLDER_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bTODO_VERSION\b", re.IGNORECASE),
    re.compile(r"\bTODO\b", re.IGNORECASE),
    re.compile(r"\bTBD\b", re.IGNORECASE),
    re.compile(r"\?\?\?\?\?\?", re.IGNORECASE),
    re.compile(r"\bUNSPECIFIED\b", re.IGNORECASE),
]

PAT_ID_RX = re.compile(r"^PAT-Q\d{3}-\d{3}$")
QUESTION_ID_RX = re.compile(r"^Q\d{3}$")


def type_tag(v: Any) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int) and not isinstance(v, bool):
        return "int"
    if isinstance(v, float):
        return "float"
    if isinstance(v, str):
        return "str"
    if isinstance(v, dict):
        return "object"
    if isinstance(v, list):
        return "array"
    return type(v).__name__


def try_load_monolith(monolith_path: Path) -> Any | None:
    if not monolith_path.exists():
        return None
    return read_json(monolith_path)


def resolve_monolith_pointer(monolith: Any, json_path: str) -> Any | None:
    if not isinstance(json_path, str):
        return None
    if not json_path.startswith("blocks."):
        return None
    cur: Any = monolith
    tokens = json_path.split(".")
    for t in tokens:
        if "[" in t and t.endswith("]"):
            name, idx_s = t[:-1].split("[", 1)
            if not isinstance(cur, dict) or name not in cur:
                return None
            cur = cur[name]
            if not isinstance(cur, list):
                return None
            idx = int(idx_s)
            if idx < 0 or idx >= len(cur):
                return None
            cur = cur[idx]
        else:
            if not isinstance(cur, dict) or t not in cur:
                return None
            cur = cur[t]
    return cur


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--contracts-root",
        type=Path,
        default=Path(
            "src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized"
        ),
    )
    ap.add_argument("--range", type=str, default="Q001-Q030")
    ap.add_argument("--date-tag", type=str, default="2025-12-19")
    ap.add_argument("--monolith-path", type=Path, default=Path("data/questionnaire_monolith.json"))
    args = ap.parse_args()

    subset = parse_range_q(args.range)
    artifacts = Path("artifacts")
    artifacts.mkdir(parents=True, exist_ok=True)

    monolith = try_load_monolith(args.monolith_path)

    type_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    presence_counts: dict[str, int] = defaultdict(int)

    placeholder_hits: list[dict[str, Any]] = []
    pattern_findings: list[dict[str, Any]] = []
    monolith_mismatches: list[dict[str, Any]] = []
    method_binding_summaries: list[dict[str, Any]] = []

    for q in subset:
        p = args.contracts_root / f"{q}.v3.json"
        if not p.exists():
            raise HarvestError(f"Missing contract: {p}")
        doc = read_json(p)

        seen_paths = set()
        for jpath, v in walk(doc):
            type_counts[jpath][type_tag(v)] += 1
            seen_paths.add(jpath)
        for jpath in seen_paths:
            presence_counts[jpath] += 1

        for jpath, v in walk(doc):
            if isinstance(v, str):
                for rx in PLACEHOLDER_PATTERNS:
                    if rx.search(v):
                        placeholder_hits.append(
                            {
                                "file": str(p),
                                "json_path": jpath,
                                "match": rx.pattern,
                                "value_excerpt": v[:240],
                            }
                        )
                        break

        mb = doc.get("method_binding") if isinstance(doc, dict) else None
        methods = mb.get("methods") if isinstance(mb, dict) else None
        provides: list[str] = []
        if isinstance(methods, list):
            for m in methods:
                if isinstance(m, dict) and isinstance(m.get("provides"), str):
                    provides.append(m["provides"])
        method_binding_summaries.append(
            {
                "file": str(p),
                "question_id": (doc.get("identity") or {}).get("question_id")
                if isinstance(doc, dict)
                else None,
                "method_count": mb.get("method_count") if isinstance(mb, dict) else None,
                "methods_len": (len(methods) if isinstance(methods, list) else None),
                "provides_len": len(provides),
            }
        )

        qc = doc.get("question_context") if isinstance(doc, dict) else None
        pats = qc.get("patterns") if isinstance(qc, dict) else None
        if isinstance(pats, list):
            for i, patt in enumerate(pats):
                if not isinstance(patt, dict):
                    pattern_findings.append(
                        {"file": str(p), "index": i, "error": "pattern_not_object"}
                    )
                    continue
                pid = patt.get("id")
                if not isinstance(pid, str) or not PAT_ID_RX.fullmatch(pid):
                    pattern_findings.append(
                        {
                            "file": str(p),
                            "index": i,
                            "error": "pattern_id_invalid",
                            "id": pid,
                        }
                    )

        if monolith is not None:
            tr = doc.get("traceability") if isinstance(doc, dict) else None
            ptr = tr.get("json_path") if isinstance(tr, dict) else None
            node = resolve_monolith_pointer(monolith, ptr)
            if node is None:
                monolith_mismatches.append(
                    {
                        "file": str(p),
                        "error": "monolith_pointer_unresolved",
                        "json_path": ptr,
                    }
                )
            else:
                mono_expected = node.get("expected_elements") if isinstance(node, dict) else None
                cont_expected = qc.get("expected_elements") if isinstance(qc, dict) else None
                if mono_expected != cont_expected:
                    monolith_mismatches.append({"file": str(p), "error": "expected_elements_mismatch"})

                mono_patterns = node.get("patterns") if isinstance(node, dict) else None
                cont_patterns = qc.get("patterns") if isinstance(qc, dict) else None
                if mono_patterns != cont_patterns:
                    monolith_mismatches.append({"file": str(p), "error": "patterns_mismatch"})

    n = len(subset)

    path_profile: list[dict[str, Any]] = []
    for jpath in sorted(type_counts.keys()):
        present = presence_counts.get(jpath, 0)
        types = dict(type_counts[jpath])
        path_profile.append(
            {
                "json_path": jpath,
                "present_in_contracts": present,
                "presence_ratio": present / n,
                "types": types,
                "type_entropy_proxy": len(types),
            }
        )

    constants = [p for p in path_profile if p["presence_ratio"] == 1.0 and p["type_entropy_proxy"] == 1]
    variable = [p for p in path_profile if p["presence_ratio"] == 1.0 and p["type_entropy_proxy"] > 1]
    missing = [p for p in path_profile if p["presence_ratio"] < 1.0]

    out = artifacts / f"contract_evidence_harvest_v3_{args.date_tag}_{args.range}.json"
    payload = {
        "generated_at": utc_now_z(),
        "contracts_root": str(args.contracts_root),
        "range": args.range,
        "contracts": n,
        "monolith_path": str(args.monolith_path),
        "monolith_loaded": monolith is not None,
        "placeholder_hits_count": len(placeholder_hits),
        "pattern_findings_count": len(pattern_findings),
        "monolith_mismatches_count": len(monolith_mismatches),
        "meta_schema": {
            "path_profile_count": len(path_profile),
            "constants_count": len(constants),
            "variable_type_paths_count": len(variable),
            "missing_paths_count": len(missing),
            "constants_top_200": constants[:200],
            "variable_type_paths_top_200": variable[:200],
            "missing_paths_top_200": missing[:200],
        },
        "placeholder_hits": placeholder_hits,
        "pattern_findings": pattern_findings,
        "monolith_mismatches": monolith_mismatches,
        "method_binding_summaries": method_binding_summaries,
    }

    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    out.write_text(text, encoding="utf-8")

    print("written:", out)
    print("contracts:", n)
    print("monolith_loaded:", monolith is not None)
    print("placeholder_hits_count:", len(placeholder_hits))
    print("pattern_findings_count:", len(pattern_findings))
    print("monolith_mismatches_count:", len(monolith_mismatches))
    print("meta_schema_constants_count:", len(constants))
    print("sha256:", sha256_text(text))


if __name__ == "__main__":
    main()

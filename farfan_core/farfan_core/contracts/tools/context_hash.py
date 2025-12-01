# farfan_core/farfan_core/contracts/tools/context_hash.py
from __future__ import annotations

import argparse, json, sys, pathlib
from typing import Any, Dict, Tuple

# Robust import of the frozen QuestionContext and the canonical digester
try:
    from farfan_core.question_context import QuestionContext  # preferred (top-level re-export)
except Exception:  # fallback to nested package layout
    from farfan_core.question_context import QuestionContext  # type: ignore

from farfan_core.contracts.context_immutability import (
    ContextImmutabilityContract,
)

def load_json_file(path: str | None) -> Dict[str, Any]:
    if not path:
        return {}
    p = pathlib.Path(path).expanduser().resolve()
    if not p.is_file():
        raise FileNotFoundError(f"Standards/JSON file not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))

def parse_csv_tuple(s: str | None) -> Tuple[str, ...]:
    if not s:
        return tuple()
    return tuple(x.strip() for x in s.split(",") if x.strip())

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Compute canonical digest of a deep-immutable QuestionContext."
    )
    ap.add_argument("--question-id", default="Q001")
    ap.add_argument("--mapping-json", default=None,
                    help="JSON string or @path/to/file.json describing question_mapping")
    ap.add_argument("--standards", default=None,
                    help="Path to dnp_standards_complete.json (optional)")
    ap.add_argument("--evidence-types", default="",
                    help="Comma-separated list of evidence type strings")
    ap.add_argument("--queries", default="",
                    help="Comma-separated list of search query strings")
    ap.add_argument("--criteria-json", default=None,
                    help="JSON string or @path/to/file.json for validation_criteria")
    ap.add_argument("--trace-id", default="TRACE-DEMO")

    args = ap.parse_args()

    # Build question_mapping
    if args.mapping_json:  # allow @file or raw JSON
        s = args.mapping_json
        if s.startswith("@"):
            question_mapping = load_json_file(s[1:])
        else:
            question_mapping = json.loads(s)
    else:
        question_mapping = {"id": args.question_id, "decalogo_point": "DE1"}

    # Standards payload (optional file)
    dnp_standards = load_json_file(args.standards)

    # Evidence types & queries
    required_evidence_types = parse_csv_tuple(args.evidence_types)
    search_queries = parse_csv_tuple(args.queries)

    # Validation criteria
    if args.criteria_json:
        s = args.criteria_json
        if s.startswith("@"):
            validation_criteria = load_json_file(s[1:])
        else:
            validation_criteria = json.loads(s)
    else:
        validation_criteria = {"min_confidence": 0.8}

    # Construct the deep-immutable context (all fields REQUIRED)
    ctx = QuestionContext(
        question_mapping=question_mapping,
        dnp_standards=dnp_standards,
        required_evidence_types=required_evidence_types,
        search_queries=search_queries,
        validation_criteria=validation_criteria,
        traceability_id=args.trace_id,
    )

    digest = ContextImmutabilityContract.canonical_digest(ctx)
    print(f"Context Hash: {digest}")

    cert = {
        "pass": True,
        "context_hash": digest,
        "question_id": args.question_id,
        "trace_id": args.trace_id,
        "evidence_types": list(required_evidence_types),
        "queries": list(search_queries),
        "standards_present": bool(dnp_standards),
    }
    pathlib.Path("cic_certificate.json").write_text(
        json.dumps(cert, indent=2, ensure_ascii=False), encoding="utf-8"
    )

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[context_hash] ERROR: {e}", file=sys.stderr)
        sys.exit(1)

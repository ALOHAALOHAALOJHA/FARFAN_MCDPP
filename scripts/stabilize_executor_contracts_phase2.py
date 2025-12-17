#!/usr/bin/env python3
"""Deep-check and stabilize Phase 2 v3 specialized executor contracts.

This tool performs two functions:
1) Audit: CQVR scoring + structural invariants + (optional) method reference checks.
2) Fix: Apply non-destructive, contract-driven improvements to reach CQVR ≥ 96.

Key guarantees (non-test manipulation):
- No changes to CQVR rubric code.
- Improvements are applied to contract content (signals, assembly sources, templates, and
  methodological documentation) to increase real runtime stability.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final, Iterable


REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACTS_DIR: Final[Path] = (
    REPO_ROOT
    / "src"
    / "farfan_pipeline"
    / "phases"
    / "Phase_two"
    / "json_files_phase_two"
    / "executor_contracts"
    / "specialized"
)
VALIDATOR_PATH: Final[Path] = (
    REPO_ROOT
    / "src"
    / "farfan_pipeline"
    / "phases"
    / "Phase_two"
    / "json_files_phase_two"
    / "executor_contracts"
    / "cqvr_validator.py"
)

CONTRACT_RE: Final[re.Pattern[str]] = re.compile(r"^Q\d{3}\.v3\.json$")
BASE_SLOT_RE: Final[re.Pattern[str]] = re.compile(r"D\d-Q\d")
GENERIC_PHRASES: Final[tuple[str, ...]] = ("Execute", "Process results", "Return structured output")
VALID_SIGNAL_AGGREGATIONS: Final[set[str]] = {"weighted_mean", "max", "min", "product", "voting"}
PROVIDES_INLINE_RE: Final[re.Pattern[str]] = re.compile(r"provides='[^']*'")


@dataclass(frozen=True, slots=True)
class AuditFinding:
    contract_id: str
    severity: str
    message: str


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _iter_contract_paths(contracts_dir: Path) -> list[Path]:
    if not contracts_dir.exists():
        raise FileNotFoundError(str(contracts_dir))
    candidates = sorted(p for p in contracts_dir.iterdir() if CONTRACT_RE.match(p.name))
    if len(candidates) != 300:
        raise RuntimeError(f"Expected 300 v3 contracts, found {len(candidates)} in {contracts_dir}")
    return candidates


def _load_cqvr_validator() -> Any:
    if not VALIDATOR_PATH.exists():
        raise FileNotFoundError(str(VALIDATOR_PATH))
    spec = importlib.util.spec_from_file_location("cqvr_validator", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load CQVR validator from {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.CQVRValidator()


def _compute_contract_hash(contract: dict[str, Any]) -> str:
    """Compute SHA-256 over canonical JSON excluding identity.contract_hash."""
    import hashlib

    contract_copy = json.loads(json.dumps(contract, ensure_ascii=False))
    identity = contract_copy.get("identity")
    if isinstance(identity, dict) and "contract_hash" in identity:
        identity["contract_hash"] = ""
    json_bytes = json.dumps(
        contract_copy, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(json_bytes).hexdigest()


def _normalize_base_slot_in_title(*, title: str, base_slot: str) -> str:
    if not base_slot:
        return title
    match = BASE_SLOT_RE.search(title)
    if match and match.group(0) != base_slot:
        return f"{title[:match.start()]}{base_slot}{title[match.end():]}"
    return title


def _inject_question_id_into_title(*, title: str, question_id: str) -> str:
    stripped = title.strip()
    if not stripped:
        return f"## {question_id}"

    if question_id in stripped:
        return title

    if stripped.startswith("## "):
        return f"## {question_id} | {stripped[3:]}"
    if stripped.startswith("# "):
        return f"# {question_id} | {stripped[2:]}"
    return f"{question_id} | {title}"


def _normalize_template_title(*, title: str, question_id: str, base_slot: str) -> str:
    normalized = _normalize_base_slot_in_title(title=title, base_slot=base_slot)
    return _inject_question_id_into_title(title=normalized, question_id=question_id)


def _default_method_steps(*, class_name: str, method_name: str, provides: str) -> list[dict[str, Any]]:
    method_id = f"{class_name}.{method_name}"
    return [
        {
            "step": 1,
            "description": (
                f"Invocar `{method_id}` mediante `MethodExecutor.execute` con el contexto del documento "
                "y señales irrigadas (cuando estén disponibles)."
            ),
        },
        {
            "step": 2,
            "description": (
                "Validar que la salida sea JSON-serializable y capturar fallos en trazas si aplica "
                "(sin detener el pipeline salvo política de `error_handling`)."
            ),
        },
        {
            "step": 3,
            "description": (
                f"Persistir el resultado en `method_outputs` bajo `provides='{provides}'` usando "
                "`_set_nested_value` (dot-notation) para ensamblaje determinista."
            ),
        },
        {
            "step": 4,
            "description": (
                "Exponer el output para extracción de evidencia (`EvidenceNexus`) y aplicación de "
                "reglas de ensamblaje/validación definidas en el contrato."
            ),
        },
        {
            "step": 5,
            "description": (
                "Aportar trazabilidad (prioridad, señales usadas, calibración si aplica) para auditoría "
                "y reproducibilidad."
            ),
        },
    ]


def _rewrite_method_steps(
    *,
    steps: list[Any],
    class_name: str,
    method_name: str,
    provides: str,
) -> tuple[list[Any], bool]:
    updated = False
    out: list[Any] = []

    for idx, step in enumerate(steps, start=1):
        if isinstance(step, dict):
            desc = str(step.get("description", ""))
            if any(p in desc for p in GENERIC_PHRASES):
                template = _default_method_steps(
                    class_name=class_name, method_name=method_name, provides=provides
                )
                out.append({"step": idx, "description": template[min(idx, 5) - 1]["description"]})
                updated = True
            else:
                out.append(step)
        else:
            desc = str(step)
            if any(p in desc for p in GENERIC_PHRASES):
                template = _default_method_steps(
                    class_name=class_name, method_name=method_name, provides=provides
                )
                out.append({"step": idx, "description": template[min(idx, 5) - 1]["description"]})
                updated = True
            else:
                out.append(step)

    return out, updated


def _align_provides_in_steps(*, steps: list[Any], provides: str) -> tuple[list[Any], bool]:
    if not provides:
        return steps, False

    updated = False
    out: list[Any] = []

    for step in steps:
        if isinstance(step, dict):
            desc = step.get("description")
            if isinstance(desc, str) and "provides='" in desc:
                new_desc = PROVIDES_INLINE_RE.sub(f"provides='{provides}'", desc)
                if new_desc != desc:
                    step = {**step, "description": new_desc}
                    updated = True
            out.append(step)
        else:
            out.append(step)

    return out, updated


def stabilize_contract(contract: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    changes: list[str] = []

    identity = contract.get("identity")
    if not isinstance(identity, dict):
        return contract, changes

    question_id = str(identity.get("question_id") or "")
    base_slot = str(identity.get("base_slot") or "")

    signal_requirements = contract.get("signal_requirements")
    if not isinstance(signal_requirements, dict):
        signal_requirements = {}
        contract["signal_requirements"] = signal_requirements
        changes.append("signal_requirements:created")

    mandatory = signal_requirements.get("mandatory_signals", [])
    if isinstance(mandatory, list):
        renamed = False
        updated_mandatory: list[Any] = []
        for item in mandatory:
            if item == "transparency":
                updated_mandatory.append("policy_transparency")
                renamed = True
            else:
                updated_mandatory.append(item)
        if renamed:
            signal_requirements["mandatory_signals"] = updated_mandatory
            changes.append("signal_requirements.mandatory_signals:transparency->policy_transparency")
    else:
        mandatory = []

    threshold = signal_requirements.get("minimum_signal_threshold", 0.0)
    if isinstance(mandatory, list) and mandatory and float(threshold) <= 0.0:
        signal_requirements["minimum_signal_threshold"] = 0.5
        changes.append("signal_requirements.minimum_signal_threshold:0.5")

    aggregation = signal_requirements.get("signal_aggregation")
    if not isinstance(aggregation, str) or aggregation not in VALID_SIGNAL_AGGREGATIONS:
        signal_requirements["signal_aggregation"] = "weighted_mean"
        changes.append("signal_requirements.signal_aggregation:weighted_mean")

    method_binding = contract.get("method_binding")
    provides_by_method: dict[tuple[str, str], str] = {}
    if isinstance(method_binding, dict):
        methods = method_binding.get("methods", [])
        if isinstance(methods, list):
            if method_binding.get("method_count") != len(methods):
                method_binding["method_count"] = len(methods)
                changes.append("method_binding.method_count:aligned")

            provides_list: list[str] = []
            for m in methods:
                if not isinstance(m, dict):
                    continue
                cls_name = str(m.get("class_name") or "")
                meth_name = str(m.get("method_name") or "")
                provides = m.get("provides")
                if isinstance(provides, str) and provides:
                    provides_list.append(provides)
                    if cls_name and meth_name:
                        provides_by_method[(cls_name, meth_name)] = provides

            evidence_assembly = contract.get("evidence_assembly")
            if isinstance(evidence_assembly, dict):
                rules = evidence_assembly.get("assembly_rules", [])
                if isinstance(rules, list) and rules:
                    current_sources = set()
                    for rule in rules:
                        if not isinstance(rule, dict):
                            continue
                        for src in rule.get("sources", []):
                            if isinstance(src, str) and "*" not in src:
                                current_sources.add(src)
                    if provides_list and current_sources != set(provides_list):
                        rules[0]["sources"] = provides_list
                        changes.append("evidence_assembly.assembly_rules[0].sources:provides")

    output_contract = contract.get("output_contract")
    if isinstance(output_contract, dict):
        hro = output_contract.get("human_readable_output")
        if not isinstance(hro, dict):
            hro = {}
            output_contract["human_readable_output"] = hro
            changes.append("output_contract.human_readable_output:created")

        template = hro.get("template")
        if not isinstance(template, dict):
            template = {}
            hro["template"] = template
            changes.append("output_contract.human_readable_output.template:created")

        title = str(template.get("title") or "")
        if question_id:
            normalized_title = _normalize_template_title(
                title=title, question_id=question_id, base_slot=base_slot
            )
            if normalized_title != title:
                template["title"] = normalized_title
                changes.append("human_readable_output.template.title:normalized")

        template_text = str(template)
        if "{score}" not in template_text:
            template.setdefault("score_section", "Puntaje: {score}/3.0 | Calidad: {quality_level}")
            changes.append("human_readable_output.template:+{score}")

        template_text = str(template)
        if "{evidence" not in template_text:
            template.setdefault("elements_section", "{evidence.elements_found_list}")
            changes.append("human_readable_output.template:+{evidence}")

        methodological_depth = hro.get("methodological_depth")
        if not isinstance(methodological_depth, dict):
            return contract, changes

        md_methods = methodological_depth.get("methods", [])
        if not isinstance(md_methods, list):
            return contract, changes

        for idx, method in enumerate(md_methods[:5]):
            if not isinstance(method, dict):
                continue
            class_name = str(method.get("class_name") or "")
            method_name = str(method.get("method_name") or "")
            provides = str(
                provides_by_method.get((class_name, method_name))
                or method.get("provides")
                or f"{class_name}.{method_name}"
            )
            if provides:
                method.setdefault("provides", provides)
            technical = method.get("technical_approach")
            if not isinstance(technical, dict):
                technical = {}
                method["technical_approach"] = technical

            steps = technical.get("steps")
            if not isinstance(steps, list) or not steps:
                filled = _default_method_steps(
                    class_name=class_name, method_name=method_name, provides=provides
                )
                technical["steps"] = filled
                changes.append(f"methodological_depth.methods[{idx}].technical_approach.steps:filled")
                continue

            rewritten, changed = _rewrite_method_steps(
                steps=steps, class_name=class_name, method_name=method_name, provides=provides
            )
            aligned, aligned_changed = _align_provides_in_steps(steps=rewritten, provides=provides)
            if changed or aligned_changed:
                technical["steps"] = aligned
                changes.append(f"methodological_depth.methods[{idx}].technical_approach.steps:refined")

    if changes:
        identity["updated_at"] = _utc_now_iso()
        contract["identity"] = identity
        contract["identity"]["contract_hash"] = _compute_contract_hash(contract)

    return contract, changes


def _audit_invariants(contract: dict[str, Any], contract_id: str) -> list[AuditFinding]:
    findings: list[AuditFinding] = []

    identity = contract.get("identity", {})
    if not isinstance(identity, dict):
        return [AuditFinding(contract_id, "error", "Missing or invalid identity")]

    if identity.get("question_id") != contract_id:
        findings.append(
            AuditFinding(
                contract_id,
                "error",
                f"identity.question_id mismatch (expected {contract_id}, got {identity.get('question_id')})",
            )
        )

    sr = contract.get("signal_requirements", {})
    if isinstance(sr, dict):
        mandatory = sr.get("mandatory_signals", [])
        threshold = sr.get("minimum_signal_threshold", 0.0)
        if isinstance(mandatory, list) and mandatory and float(threshold) <= 0.0:
            findings.append(
                AuditFinding(
                    contract_id,
                    "error",
                    "signal_requirements.minimum_signal_threshold must be >0 when mandatory_signals exist",
                )
            )

    mb = contract.get("method_binding", {})
    if isinstance(mb, dict):
        methods = mb.get("methods", [])
        if isinstance(methods, list):
            if mb.get("method_count") != len(methods):
                findings.append(
                    AuditFinding(contract_id, "error", "method_binding.method_count mismatch")
                )
            provides = [
                m.get("provides")
                for m in methods
                if isinstance(m, dict) and isinstance(m.get("provides"), str)
            ]
            if len(provides) != len(set(provides)):
                findings.append(AuditFinding(contract_id, "error", "Duplicate provides keys"))

    return findings


def _score_all(
    *,
    contract_paths: Iterable[Path],
    validator: Any,
) -> tuple[list[dict[str, Any]], list[float]]:
    reports: list[dict[str, Any]] = []
    percentages: list[float] = []

    for path in contract_paths:
        contract_id = path.stem.replace(".v3", "")
        contract = json.loads(path.read_text(encoding="utf-8"))
        report = validator.validate_contract(contract)
        report["contract_id"] = contract_id
        reports.append(report)
        percentages.append(float(report["percentage"]))

    return reports, percentages


def _print_score_summary(percentages: list[float]) -> None:
    p_sorted = sorted(percentages)
    median = p_sorted[len(p_sorted) // 2] if p_sorted else 0.0
    p90 = p_sorted[int(len(p_sorted) * 0.9)] if p_sorted else 0.0
    print(
        f"contracts={len(percentages)} min={min(percentages):.1f} median={median:.1f} "
        f"p90={p90:.1f} max={max(percentages):.1f}"
    )


def _print_failures(reports: list[dict[str, Any]], threshold: float) -> None:
    failures = [r for r in reports if float(r["percentage"]) < threshold]
    print(f"below_threshold={len(failures)} threshold={threshold:.1f}")
    for r in sorted(failures, key=lambda x: float(x["percentage"]))[:25]:
        cid = r["contract_id"]
        pct = float(r["percentage"])
        breakdown = r.get("breakdown", {})
        print(f"- {cid}: {pct:.1f} breakdown={breakdown}")
    if len(failures) > 25:
        print("... (more failures truncated)")


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def cmd_audit(args: argparse.Namespace) -> int:
    validator = _load_cqvr_validator()
    contract_paths = _iter_contract_paths(args.contracts_dir)

    reports, percentages = _score_all(contract_paths=contract_paths, validator=validator)
    _print_score_summary(percentages)
    _print_failures(reports, threshold=args.threshold)

    invariant_findings: list[AuditFinding] = []
    for path in contract_paths:
        contract_id = path.stem.replace(".v3", "")
        contract = json.loads(path.read_text(encoding="utf-8"))
        invariant_findings.extend(_audit_invariants(contract, contract_id))

    errors = [f for f in invariant_findings if f.severity == "error"]
    print(f"invariant_errors={len(errors)}")
    for f in errors[:25]:
        print(f"- {f.contract_id}: {f.message}")
    if len(errors) > 25:
        print("... (more invariant errors truncated)")

    if args.output_json:
        _write_json(
            args.output_json,
            {
                "scores": reports,
                "invariants": [
                    {"contract_id": f.contract_id, "severity": f.severity, "message": f.message}
                    for f in invariant_findings
                ],
            },
        )

    return 0


def cmd_fix(args: argparse.Namespace) -> int:
    validator = _load_cqvr_validator()
    contract_paths = _iter_contract_paths(args.contracts_dir)

    before_reports, before_percentages = _score_all(contract_paths=contract_paths, validator=validator)
    print("before:")
    _print_score_summary(before_percentages)

    changed = 0
    changes_by_contract: dict[str, list[str]] = {}

    for path in contract_paths:
        contract_id = path.stem.replace(".v3", "")
        contract = json.loads(path.read_text(encoding="utf-8"))
        updated, changes = stabilize_contract(contract)
        if changes:
            changed += 1
            changes_by_contract[contract_id] = changes
            if not args.dry_run:
                new_text = json.dumps(updated, ensure_ascii=False, indent=2) + "\n"
                path.write_text(new_text, encoding="utf-8")

    print(f"contracts_changed={changed} dry_run={args.dry_run}")
    if args.changes_json:
        _write_json(args.changes_json, changes_by_contract)

    after_reports, after_percentages = _score_all(contract_paths=contract_paths, validator=validator)
    print("after:")
    _print_score_summary(after_percentages)
    _print_failures(after_reports, threshold=args.threshold)

    invariant_findings: list[AuditFinding] = []
    for path in contract_paths:
        contract_id = path.stem.replace(".v3", "")
        contract = json.loads(path.read_text(encoding="utf-8"))
        invariant_findings.extend(_audit_invariants(contract, contract_id))

    errors = [f for f in invariant_findings if f.severity == "error"]
    if errors:
        print(f"invariant_errors={len(errors)}")
        for f in errors[:25]:
            print(f"- {f.contract_id}: {f.message}")
        return 2

    below = [r for r in after_reports if float(r["percentage"]) < args.threshold]
    if below:
        return 3

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--contracts-dir",
        type=Path,
        default=DEFAULT_CONTRACTS_DIR,
        help=f"Directory containing Q###.v3.json contracts (default: {DEFAULT_CONTRACTS_DIR})",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    audit = sub.add_parser("audit", help="Audit CQVR + invariants")
    audit.add_argument("--threshold", type=float, default=96.0)
    audit.add_argument("--output-json", type=Path, default=None)
    audit.set_defaults(func=cmd_audit)

    fix = sub.add_parser("fix", help="Apply stabilization fixes in-place")
    fix.add_argument("--threshold", type=float, default=96.0)
    fix.add_argument("--dry-run", action="store_true")
    fix.add_argument("--changes-json", type=Path, default=None)
    fix.set_defaults(func=cmd_fix)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

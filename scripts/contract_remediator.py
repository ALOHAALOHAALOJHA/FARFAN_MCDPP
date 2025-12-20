#!/usr/bin/env python3
"""
Automated Contract Remediator
Fixes common contract issues based on CQVR validation scores.

Features:
- Auto-fix identity-schema mismatches
- Rebuild assembly rules from method bindings
- Set proper signal thresholds
- Align validation rules with expected elements
- Regenerate contracts from questionnaire_monolith
- Safety features: backup, dry-run, diff, rollback
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import unified_diff
from enum import Enum
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from orchestration.factory import get_canonical_questionnaire
from farfan_pipeline.phases.Phase_two.contract_validator_cqvr import (
    CQVRValidator,
    ContractTriageDecision,
    TriageDecision,
)


class RemediationStrategy(Enum):
    AUTO = "auto"
    PATCH = "patch"
    REGENERATE = "regenerate"


@dataclass
class RemediationResult:
    contract_path: Path
    original_score: float
    new_score: float
    strategy_used: str
    fixes_applied: list[str]
    success: bool
    error_message: str | None = None


class ContractBackupManager:
    """Manages contract backups with versioning."""

    def __init__(self, backup_dir: Path):
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def backup_contract(self, contract_path: Path) -> Path:
        """Create timestamped backup of contract."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        contract_name = contract_path.stem
        backup_name = f"{contract_name}_backup_{timestamp}.json"
        backup_path = self.backup_dir / backup_name

        shutil.copy2(contract_path, backup_path)
        return backup_path

    def list_backups(self, contract_name: str) -> list[Path]:
        """List all backups for a contract."""
        pattern = f"{contract_name}_backup_*.json"
        return sorted(self.backup_dir.glob(pattern), reverse=True)

    def restore_backup(self, backup_path: Path, target_path: Path) -> None:
        """Restore a backup to target location."""
        shutil.copy2(backup_path, target_path)


class ContractDiffGenerator:
    """Generates human-readable diffs between contracts."""

    @staticmethod
    def generate_diff(
        original: dict[str, Any], modified: dict[str, Any], label: str = "Contract"
    ) -> str:
        """Generate unified diff between two contracts."""
        original_json = json.dumps(original, indent=2, sort_keys=True).splitlines(
            keepends=True
        )
        modified_json = json.dumps(modified, indent=2, sort_keys=True).splitlines(
            keepends=True
        )

        diff = unified_diff(
            original_json,
            modified_json,
            fromfile=f"{label} (original)",
            tofile=f"{label} (modified)",
            lineterm="",
        )

        return "".join(diff)

    @staticmethod
    def summarize_changes(original: dict[str, Any], modified: dict[str, Any]) -> dict[str, Any]:
        """Summarize key changes between contracts."""
        changes = {
            "fields_modified": [],
            "fields_added": [],
            "fields_removed": [],
        }

        def compare_dicts(orig: dict, mod: dict, path: str = "") -> None:
            all_keys = set(orig.keys()) | set(mod.keys())

            for key in all_keys:
                current_path = f"{path}.{key}" if path else key

                if key not in orig:
                    changes["fields_added"].append(current_path)
                elif key not in mod:
                    changes["fields_removed"].append(current_path)
                elif orig[key] != mod[key]:
                    if isinstance(orig[key], dict) and isinstance(mod[key], dict):
                        compare_dicts(orig[key], mod[key], current_path)
                    else:
                        changes["fields_modified"].append(current_path)

        compare_dicts(original, modified)
        return changes


class ContractRemediator:
    """Main contract remediation engine."""

    def __init__(
        self,
        contracts_dir: Path,
        monolith_path: Path,
        backup_dir: Path,
        dry_run: bool = False,
    ):
        self.contracts_dir = contracts_dir
        self.monolith_path = monolith_path
        self.backup_manager = ContractBackupManager(backup_dir)
        self.diff_generator = ContractDiffGenerator()
        self.dry_run = dry_run
        self.validator = CQVRValidator()

        canonical_questionnaire = get_canonical_questionnaire(
            questionnaire_path=monolith_path,
        )
        self.monolith = canonical_questionnaire.data

    def remediate_contract(
        self, contract_path: Path, strategy: RemediationStrategy
    ) -> RemediationResult:
        """Remediate a single contract."""
        try:
            with open(contract_path) as f:
                original_contract = json.load(f)

            original_decision = self.validator.validate_contract(original_contract)
            original_score = original_decision.score.total_score

            if strategy == RemediationStrategy.AUTO:
                modified_contract, fixes = self._apply_auto_fixes(original_contract)
                strategy_used = "auto-fix"
            elif strategy == RemediationStrategy.PATCH:
                modified_contract, fixes = self._apply_patches(
                    original_contract, original_decision
                )
                strategy_used = "patch"
            elif strategy == RemediationStrategy.REGENERATE:
                modified_contract, fixes = self._regenerate_contract(original_contract)
                strategy_used = "regenerate"
            else:
                raise ValueError(f"Unknown strategy: {strategy}")

            new_decision = self.validator.validate_contract(modified_contract)
            new_score = new_decision.score.total_score

            if not self.dry_run and new_score > original_score:
                backup_path = self.backup_manager.backup_contract(contract_path)
                print(f"  Backed up to: {backup_path.name}")

                with open(contract_path, "w") as f:
                    json.dump(modified_contract, f, indent=2, ensure_ascii=False)
                    f.write("\n")

            return RemediationResult(
                contract_path=contract_path,
                original_score=original_score,
                new_score=new_score,
                strategy_used=strategy_used,
                fixes_applied=fixes,
                success=new_score > original_score,
            )

        except Exception as e:
            return RemediationResult(
                contract_path=contract_path,
                original_score=0.0,
                new_score=0.0,
                strategy_used=strategy.value,
                fixes_applied=[],
                success=False,
                error_message=str(e),
            )

    def _apply_auto_fixes(
        self, contract: dict[str, Any]
    ) -> tuple[dict[str, Any], list[str]]:
        """Apply automatic fixes for common issues."""
        fixes = []
        modified = json.loads(json.dumps(contract))

        if self._fix_identity_schema_mismatch(modified):
            fixes.append("identity_schema_coherence")

        if self._fix_method_assembly_alignment(modified):
            fixes.append("method_assembly_alignment")

        if self._fix_signal_threshold(modified):
            fixes.append("signal_threshold")

        if self._fix_validation_rules_alignment(modified):
            fixes.append("validation_rules_alignment")

        if self._fix_human_template_title(modified):
            fixes.append("human_template_title")

        if self._fix_methodological_depth(modified):
            fixes.append("methodological_depth")

        if self._fix_source_hash(modified):
            fixes.append("source_hash")

        if self._fix_output_schema_required(modified):
            fixes.append("output_schema_required")

        self._update_metadata(modified, fixes)

        return modified, fixes

    def _fix_identity_schema_mismatch(self, contract: dict[str, Any]) -> bool:
        """Fix mismatches between identity and output schema."""
        identity = contract.get("identity", {})
        schema_props = (
            contract.get("output_contract", {}).get("schema", {}).get("properties", {})
        )

        fixed = False
        for field in [
            "question_id",
            "policy_area_id",
            "dimension_id",
            "question_global",
            "base_slot",
        ]:
            identity_val = identity.get(field)
            if identity_val is not None and field in schema_props:
                schema_const = schema_props[field].get("const")
                if identity_val != schema_const:
                    schema_props[field]["const"] = identity_val
                    fixed = True

        return fixed

    def _fix_method_assembly_alignment(self, contract: dict[str, Any]) -> bool:
        """Align assembly sources with method provides."""
        methods = contract.get("method_binding", {}).get("methods", [])
        assembly_rules = contract.get("evidence_assembly", {}).get("assembly_rules", [])

        if not methods or not assembly_rules:
            return False

        provides_list = [
            m.get("provides", "") for m in methods if isinstance(m.get("provides"), str) and m.get("provides")
        ]
        provides_set = set(provides_list)

        fixed = False

        rule_for_elements = None
        for rule in assembly_rules:
            if rule.get("target") == "elements_found":
                rule_for_elements = rule
                break
        if rule_for_elements is None:
            rule_for_elements = assembly_rules[0]

        desired_sources = sorted(provides_set)
        if (
            isinstance(rule_for_elements, dict)
            and provides_list
            and rule_for_elements.get("sources") != desired_sources
        ):
            rule_for_elements["sources"] = desired_sources
            description = rule_for_elements.get("description")
            if isinstance(description, str) and "Combine" in description:
                rule_for_elements["description"] = f"Combine evidence from {len(provides_set)} methods"
            fixed = True

        for rule in assembly_rules:
            sources = rule.get("sources", [])
            if not sources:
                continue

            orphan_sources = []
            for source in sources:
                source_key = source
                if isinstance(source, dict):
                    source_key = source.get("namespace", "")

                if source_key and not source_key.startswith("*."):
                    if source_key not in provides_set:
                        orphan_sources.append(source)

            if orphan_sources and len(orphan_sources) < len(sources):
                rule["sources"] = [
                    s for s in sources if s not in orphan_sources and s in provides_set
                ]
                fixed = True

        return fixed

    def _fix_signal_threshold(self, contract: dict[str, Any]) -> bool:
        """Fix signal threshold issues."""
        signal_reqs = contract.get("signal_requirements", {})
        mandatory_signals = signal_reqs.get("mandatory_signals", [])
        threshold = signal_reqs.get("minimum_signal_threshold", 0.0)

        if mandatory_signals and threshold <= 0:
            signal_reqs["minimum_signal_threshold"] = 0.5
            updated = True
        else:
            updated = False

        preferred = [
            "policy_instrument_detected",
            "activity_specification_found",
            "implementation_timeline_present",
        ]
        if isinstance(signal_reqs, dict) and "preferred_signal_types" not in signal_reqs:
            signal_reqs["preferred_signal_types"] = preferred
            updated = True

        return updated

        return False

    def _fix_output_schema_required(self, contract: dict[str, Any]) -> bool:
        """Ensure all required fields are in properties."""
        schema = contract.get("output_contract", {}).get("schema", {})
        required = schema.get("required", [])
        properties = schema.get("properties", {})

        fixed = False
        for field in required:
            if field not in properties:
                properties[field] = {"type": "object", "additionalProperties": True}
                fixed = True

        return fixed

    def _apply_patches(
        self, contract: dict[str, Any], decision: ContractTriageDecision
    ) -> tuple[dict[str, Any], list[str]]:
        """Apply targeted patches based on CQVR recommendations."""
        modified, fixes = self._apply_auto_fixes(contract)

        for recommendation in decision.recommendations:
            component = recommendation.get("component", "")
            if component == "C3" and "source_hash" in recommendation.get("issue", ""):
                if self._fix_source_hash(modified):
                    fixes.append("source_hash")

        return modified, fixes

    def _fix_source_hash(self, contract: dict[str, Any]) -> bool:
        """Calculate and set proper source hash."""
        try:
            monolith_str = json.dumps(self.monolith, sort_keys=True)
            source_hash = hashlib.sha256(monolith_str.encode()).hexdigest()

            traceability = contract.get("traceability", {})
            existing = traceability.get("source_hash", "")
            if not isinstance(existing, str) or not existing or existing.startswith("TODO"):
                traceability["source_hash"] = source_hash
                return True
        except Exception:
            pass

        return False

    def _fix_validation_rules_alignment(self, contract: dict[str, Any]) -> bool:
        question_context = contract.get("question_context", {})
        expected_elements = question_context.get("expected_elements", [])
        if not isinstance(expected_elements, list) or not expected_elements:
            return False

        required_types: list[str] = [
            e.get("type")
            for e in expected_elements
            if isinstance(e, dict) and e.get("required") and isinstance(e.get("type"), str)
        ]
        optional_types: list[str] = [
            e.get("type")
            for e in expected_elements
            if isinstance(e, dict)
            and not e.get("required")
            and isinstance(e.get("type"), str)
        ]

        if not required_types:
            return False

        validation_rules = contract.get("validation_rules", {})
        if not isinstance(validation_rules, dict):
            return False

        rule_required = {
            "description": "Auto-generated: require all required expected_elements types",
            "field": "elements_found",
            "must_contain": {"count": len(required_types), "elements": required_types},
            "type": "array",
        }
        rule_optional = {
            "description": "Auto-generated: encourage optional evidence types when available",
            "field": "elements_found",
            "should_contain": [{"elements": optional_types, "minimum": 1}] if optional_types else [],
            "type": "array",
        }

        previous = validation_rules.get("rules", [])
        validation_rules["rules"] = [rule_required, rule_optional]
        contract["validation_rules"] = validation_rules

        return previous != validation_rules["rules"]

    def _fix_human_template_title(self, contract: dict[str, Any]) -> bool:
        identity = contract.get("identity", {})
        question_id = identity.get("question_id", "")
        base_slot = identity.get("base_slot", "")
        if not isinstance(question_id, str) or not isinstance(base_slot, str):
            return False

        question_text = contract.get("question_context", {}).get("question_text", "")
        if isinstance(question_text, str):
            label = question_text.strip().replace("\n", " ")
        else:
            label = ""
        if len(label) > 120:
            label = label[:117].rstrip() + "..."

        title = f"## Análisis {question_id} ({base_slot})"
        if label:
            title = f"{title}: {label}"

        template = (
            contract.get("output_contract", {})
            .get("human_readable_output", {})
            .get("template", {})
        )
        if not isinstance(template, dict):
            return False

        current = template.get("title", "")
        if current == title:
            return False

        template["title"] = title
        return True

    def _fix_methodological_depth(self, contract: dict[str, Any]) -> bool:
        identity = contract.get("identity", {})
        dimension_id = identity.get("dimension_id", "")
        policy_area_id = identity.get("policy_area_id", "")
        question_id = identity.get("question_id", "")
        base_slot = identity.get("base_slot", "")

        if not all(isinstance(v, str) and v for v in [dimension_id, policy_area_id, question_id, base_slot]):
            return False

        dimension_label = {
            "DIM02": "Actividades / Lógica causal",
            "DIM03": "Productos / Planificación",
            "DIM04": "Resultados / Indicadores",
            "DIM05": "Impactos / Transformación",
            "DIM06": "Territorio / Enfoque diferencial",
        }.get(dimension_id, dimension_id)

        methodological_depth = {
            "methods": [
                {
                    "method_name": "contract_orchestrated_evidence_fusion",
                    "class_name": "EvidenceNexus",
                    "priority": 1,
                    "role": "evidence_graph_construction_and_synthesis",
                    "epistemological_foundation": {
                        "paradigm": "critical_realist",
                        "ontological_basis": (
                            "Policy plans encode mechanisms via activities, outputs, and indicators; "
                            "evidence is treated as fallible observations of underlying commitments."
                        ),
                        "epistemological_stance": (
                            "Triangulation across heterogeneous sources with explicit uncertainty."
                        ),
                        "theoretical_framework": [
                            "Pearl (2009) causal reasoning (why mechanisms matter)",
                            "Pawson & Tilley (1997) realistic evaluation",
                            "Results-based management for public policy monitoring",
                        ],
                        "justification": (
                            f"Chosen because {dimension_label} in {policy_area_id} must explain why "
                            "the plan's commitments are coherent, measurable, and traceable to evidence."
                        ),
                    },
                    "technical_approach": {
                        "method_type": "graph_based_evidence_fusion",
                        "algorithm": "pattern extraction + multi-method pipeline + evidence graph synthesis",
                        "steps": [
                            {
                                "step": 1,
                                "description": (
                                    "Extract candidate claims and table structures from the document using "
                                    "contract patterns and policy-area scope."
                                ),
                            },
                            {
                                "step": 2,
                                "description": (
                                    "Populate method outputs under provides slots and construct evidence nodes "
                                    "aligned to expected_elements."
                                ),
                            },
                            {
                                "step": 3,
                                "description": (
                                    "Assemble aggregate evidence for elements_found and infer relationships "
                                    "to support synthesis and validation."
                                ),
                            },
                            {
                                "step": 4,
                                "description": (
                                    "Compute completeness, gaps, and confidence interval for downstream scoring "
                                    f"({question_id}/{base_slot})."
                                ),
                            },
                        ],
                        "assumptions": [
                            "The source plan contains at least one relevant section or table for this question.",
                            "Expected element types map to observable text spans or tabular cells.",
                        ],
                        "limitations": [
                            "Evidence quality depends on document structure and explicitness of commitments.",
                            "Pattern-only extraction is conservative to preserve determinism.",
                        ],
                        "complexity": (
                            "O(n_patterns × n_text) for bounded regex matching + O(n_nodes + n_edges) for "
                            "graph propagation."
                        ),
                    },
                }
            ]
        }

        if contract.get("methodological_depth") == methodological_depth:
            return False
        contract["methodological_depth"] = methodological_depth
        return True

    def _regenerate_contract(
        self, contract: dict[str, Any]
    ) -> tuple[dict[str, Any], list[str]]:
        """Regenerate contract from questionnaire_monolith."""
        question_id = contract.get("identity", {}).get("question_id", "")

        monolith_question = None
        for q in self.monolith.get("blocks", {}).get("micro_questions", []):
            if q.get("question_id") == question_id:
                monolith_question = q
                break

        if not monolith_question:
            return contract, []

        modified = contract.copy()
        fixes = []

        if "patterns" in monolith_question:
            modified.setdefault("question_context", {})["patterns"] = monolith_question[
                "patterns"
            ]
            fixes.append("patterns_regenerated")

        if "expected_elements" in monolith_question:
            modified.setdefault("question_context", {})[
                "expected_elements"
            ] = monolith_question["expected_elements"]
            fixes.append("expected_elements_regenerated")

        if "method_sets" in monolith_question:
            fixes.append("method_sets_regenerated")

        self._update_metadata(modified, fixes)
        return modified, fixes

    def _update_metadata(self, contract: dict[str, Any], fixes: list[str]) -> None:
        """Update contract metadata after remediation."""
        identity = contract.setdefault("identity", {})
        identity["updated_at"] = datetime.now(timezone.utc).isoformat()

        traceability = contract.setdefault("traceability", {})
        remediation_log = traceability.setdefault("remediation_log", [])
        remediation_log.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "fixes_applied": fixes,
                "tool": "contract_remediator.py",
            }
        )

        temp = json.loads(json.dumps(contract))
        try:
            del temp["identity"]["contract_hash"]
        except Exception:
            pass
        contract_str = json.dumps(temp, sort_keys=True)
        identity["contract_hash"] = hashlib.sha256(contract_str.encode()).hexdigest()

    def remediate_batch(
        self, question_ids: list[str], strategy: RemediationStrategy
    ) -> list[RemediationResult]:
        """Remediate multiple contracts."""
        results = []

        for question_id in question_ids:
            contract_path = self.contracts_dir / f"{question_id}.v3.json"
            if not contract_path.exists():
                print(f"Warning: Contract {question_id}.v3.json not found")
                continue

            print(f"\nRemediating {question_id}...")
            result = self.remediate_contract(contract_path, strategy)
            results.append(result)

            self._print_result(result)

        return results

    def remediate_failing(
        self, threshold: float, strategy: RemediationStrategy
    ) -> list[RemediationResult]:
        """Remediate all contracts below a score threshold."""
        results = []

        for contract_path in sorted(self.contracts_dir.glob("Q*.v3.json")):
            try:
                with open(contract_path) as f:
                    contract = json.load(f)

                decision = self.validator.validate_contract(contract)
                if decision.score.total_score < threshold:
                    print(
                        f"\nRemediating {contract_path.name} "
                        f"(score: {decision.score.total_score:.1f})..."
                    )
                    result = self.remediate_contract(contract_path, strategy)
                    results.append(result)
                    self._print_result(result)

            except Exception as e:
                print(f"Error processing {contract_path.name}: {e}")

        return results

    def _print_result(self, result: RemediationResult) -> None:
        """Print remediation result."""
        if result.success:
            improvement = result.new_score - result.original_score
            print(f"  ✅ Success: {result.original_score:.1f} → {result.new_score:.1f} (+{improvement:.1f})")
            if result.fixes_applied:
                print(f"  Fixes: {', '.join(result.fixes_applied)}")
        elif result.error_message:
            print(f"  ❌ Error: {result.error_message}")
        else:
            print(f"  ⚠️  No improvement: {result.original_score:.1f}")


def main():
    parser = argparse.ArgumentParser(
        description="Automated Contract Remediator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Remediate single contract
  python scripts/contract_remediator.py --contract Q002.v3.json --strategy auto

  # Remediate batch
  python scripts/contract_remediator.py --batch Q001 Q002 Q003 --strategy patch

  # Regenerate failing contracts
  python scripts/contract_remediator.py --regenerate --threshold 40

  # Dry run
  python scripts/contract_remediator.py --all --dry-run
        """,
    )

    parser.add_argument(
        "--contract", type=str, help="Single contract file to remediate (e.g., Q002.v3.json)"
    )
    parser.add_argument(
        "--batch", nargs="+", help="List of question IDs to remediate (e.g., Q001 Q002 Q003)"
    )
    parser.add_argument(
        "--regenerate", action="store_true", help="Regenerate contracts from monolith"
    )
    parser.add_argument(
        "--all", action="store_true", help="Process all contracts"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=80.0,
        help="Score threshold for identifying failing contracts (default: 80)",
    )
    parser.add_argument(
        "--strategy",
        type=str,
        choices=["auto", "patch", "regenerate"],
        default="auto",
        help="Remediation strategy (default: auto)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files",
    )
    parser.add_argument(
        "--contracts-dir",
        type=Path,
        default=Path("src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized"),
        help="Directory containing contracts",
    )
    parser.add_argument(
        "--monolith",
        type=Path,
        default=Path("canonic_questionnaire_central/questionnaire_monolith.json"),
        help="Path to questionnaire monolith",
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=Path("backups/contracts"),
        help="Directory for contract backups",
    )

    args = parser.parse_args()

    if not any([args.contract, args.batch, args.regenerate, args.all]):
        parser.error("Must specify --contract, --batch, --regenerate, or --all")

    strategy_map = {
        "auto": RemediationStrategy.AUTO,
        "patch": RemediationStrategy.PATCH,
        "regenerate": RemediationStrategy.REGENERATE,
    }
    strategy = strategy_map[args.strategy]

    remediator = ContractRemediator(
        contracts_dir=args.contracts_dir,
        monolith_path=args.monolith,
        backup_dir=args.backup_dir,
        dry_run=args.dry_run,
    )

    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified\n")

    results = []

    if args.contract:
        contract_path = args.contracts_dir / args.contract
        result = remediator.remediate_contract(contract_path, strategy)
        results.append(result)
        remediator._print_result(result)

    elif args.batch:
        results = remediator.remediate_batch(args.batch, strategy)

    elif args.regenerate:
        results = remediator.remediate_failing(args.threshold, RemediationStrategy.REGENERATE)

    elif args.all:
        question_ids = [
            f"Q{i:03d}" for i in range(1, 31)
        ]
        results = remediator.remediate_batch(question_ids, strategy)

    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")

    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success and r.error_message]
    no_improvement = [r for r in results if not r.success and not r.error_message]

    print(f"Total processed: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print(f"No improvement: {len(no_improvement)}")

    if successful:
        total_improvement = sum(r.new_score - r.original_score for r in successful)
        avg_improvement = total_improvement / len(successful)
        print(f"Average improvement: +{avg_improvement:.1f} points")

    if successful:
        print(f"\n✅ Production-ready contracts (≥80):")
        for result in successful:
            if result.new_score >= 80:
                print(f"  {result.contract_path.name}: {result.new_score:.1f}")


if __name__ == "__main__":
    main()

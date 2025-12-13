#!/usr/bin/env python3
"""
Contract Quality Verification Rubric (CQVR) Audit for Q005-Q020

This script audits executor contracts Q005 through Q020 using the CQVR v2.0 rubric
to identify critical gaps, assess quality, and generate transformation requirements.

Output:
- contract_audit_Q005_Q020.json: Comprehensive audit report with per-contract breakdowns
- transformation_requirements_manifest.json: Categorized transformation requirements

Exit codes:
    0 - Audit completed successfully
    1 - Audit failed or critical errors found
"""

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


class CQVRValidator:
    """Contract Quality Verification Rubric v2.0 Validator"""

    def __init__(self):
        self.contracts_dir = Path("src/canonic_phases/Phase_two/json_files_phase_two/executor_contracts/specialized")
        self.results = {
            "audit_metadata": {
                "timestamp": datetime.now().isoformat(),
                "rubric_version": "CQVR v2.0",
                "contract_range": "Q005-Q020",
                "total_contracts": 16
            },
            "per_contract_audits": {},
            "summary_statistics": {},
            "transformation_manifest": {
                "CRITICAL": [],
                "HIGH": [],
                "MEDIUM": []
            }
        }

    def audit_all_contracts(self) -> dict[str, Any]:
        """Run CQVR audit on contracts Q005-Q020"""
        print("=" * 80)
        print("CONTRACT QUALITY VERIFICATION RUBRIC (CQVR) v2.0 AUDIT")
        print("Auditing Contracts Q005-Q020")
        print("=" * 80)
        print()

        question_ids = [f"Q{i:03d}" for i in range(5, 21)]

        for qid in question_ids:
            print(f"Auditing {qid}...")
            contract_path = self.contracts_dir / f"{qid}.v3.json"

            if not contract_path.exists():
                print(f"  ⚠️  Contract file not found: {contract_path}")
                self.results["per_contract_audits"][qid] = {
                    "status": "FILE_NOT_FOUND",
                    "error": f"Contract file not found at {contract_path}"
                }
                continue

            try:
                with open(contract_path, encoding='utf-8') as f:
                    contract = json.load(f)

                audit_result = self.audit_contract(qid, contract)
                self.results["per_contract_audits"][qid] = audit_result

                status_icon = "✅" if audit_result["verdict"]["status"] == "PRODUCTION" else "⚠️" if audit_result["verdict"]["status"] == "PATCHABLE" else "❌"
                print(f"  {status_icon} Total: {audit_result['total_score']}/100 | Decision: {audit_result['triage_decision']}")

            except Exception as e:
                print(f"  ❌ Error auditing {qid}: {e}")
                self.results["per_contract_audits"][qid] = {
                    "status": "AUDIT_ERROR",
                    "error": str(e)
                }

        print()
        self._calculate_summary_statistics()
        self._generate_transformation_manifest()

        return self.results

    def audit_contract(self, qid: str, contract: dict[str, Any]) -> dict[str, Any]:
        """Audit a single contract using CQVR v2.0"""

        tier1_scores = {
            "A1_identity_schema": self._score_identity_schema_coherence(contract),
            "A2_method_assembly": self._score_method_assembly_alignment(contract),
            "A3_signal_integrity": self._score_signal_requirements(contract),
            "A4_output_schema": self._score_output_schema(contract)
        }

        tier2_scores = {
            "B1_pattern_coverage": self._score_pattern_coverage(contract),
            "B2_method_specificity": self._score_method_specificity(contract),
            "B3_validation_rules": self._score_validation_rules(contract)
        }

        tier3_scores = {
            "C1_documentation": self._score_documentation_quality(contract),
            "C2_human_template": self._score_human_template(contract),
            "C3_metadata": self._score_metadata_completeness(contract)
        }

        tier1_total = sum(tier1_scores.values())
        tier2_total = sum(tier2_scores.values())
        tier3_total = sum(tier3_scores.values())
        total_score = tier1_total + tier2_total + tier3_total

        triage_decision = self._triage_decision(tier1_scores, tier2_scores, tier1_total, tier2_total, total_score)
        gaps_identified = self._identify_gaps(tier1_scores, tier2_scores, tier3_scores, contract)

        verdict_status = self._determine_verdict_status(tier1_total, total_score, triage_decision)

        return {
            "question_id": qid,
            "contract_version": contract.get("identity", {}).get("contract_version", "unknown"),
            "audit_timestamp": datetime.now().isoformat(),
            "tier1_scores": tier1_scores,
            "tier2_scores": tier2_scores,
            "tier3_scores": tier3_scores,
            "tier1_total": tier1_total,
            "tier2_total": tier2_total,
            "tier3_total": tier3_total,
            "total_score": total_score,
            "tier1_percentage": round((tier1_total / 55) * 100, 1),
            "tier2_percentage": round((tier2_total / 30) * 100, 1),
            "tier3_percentage": round((tier3_total / 15) * 100, 1),
            "overall_percentage": round((total_score / 100) * 100, 1),
            "triage_decision": triage_decision,
            "gaps_identified": gaps_identified,
            "verdict": {
                "status": verdict_status,
                "tier1_threshold": "≥35/55",
                "total_threshold": "≥80/100 for production"
            }
        }

    def _score_identity_schema_coherence(self, contract: dict) -> int:
        """A1. Coherencia Identity-Schema [20 pts]"""
        identity = contract.get("identity", {})
        schema_props = contract.get("output_contract", {}).get("schema", {}).get("properties", {})

        score = 0
        checks = {
            "question_id": 5,
            "policy_area_id": 5,
            "dimension_id": 5,
            "question_global": 3,
            "base_slot": 2
        }

        for field, points in checks.items():
            identity_val = identity.get(field)
            schema_const = schema_props.get(field, {}).get("const")
            if identity_val == schema_const:
                score += points

        return score

    def _score_method_assembly_alignment(self, contract: dict) -> int:
        """A2. Alineación Method-Assembly [20 pts]"""
        methods = contract.get("method_binding", {}).get("methods", [])
        assembly_rules = contract.get("evidence_assembly", {}).get("assembly_rules", [])

        if not methods:
            return 0

        provides = {m.get("provides", "") for m in methods if m.get("provides")}

        sources = set()
        for rule in assembly_rules:
            rule_sources = rule.get("sources", [])
            sources.update(rule_sources)

        orphan_sources = sources - provides
        if orphan_sources:
            orphan_penalty = min(10, len(orphan_sources) * 2.5)
            return max(0, int(20 - orphan_penalty))

        unused_provides = provides - sources
        usage_ratio = 1 - (len(unused_provides) / len(provides)) if provides else 0
        usage_score = 5 * usage_ratio

        method_count_ok = 3 if contract.get("method_binding", {}).get("method_count") == len(methods) else 0

        return int(10 + usage_score + method_count_ok + 2)

    def _score_signal_requirements(self, contract: dict) -> int:
        """A3. Integridad de Señales [10 pts]"""
        reqs = contract.get("signal_requirements", {})
        mandatory_signals = reqs.get("mandatory_signals", [])
        threshold = reqs.get("minimum_signal_threshold", 0)

        if mandatory_signals and threshold <= 0:
            return 0

        score = 5

        valid_aggregations = ["weighted_mean", "max", "min", "product", "voting"]
        if reqs.get("signal_aggregation") in valid_aggregations:
            score += 2

        if all(isinstance(s, str) and len(s) > 0 for s in mandatory_signals):
            score += 3

        return score

    def _score_output_schema(self, contract: dict) -> int:
        """A4. Validación de Output Schema [5 pts]"""
        schema = contract.get("output_contract", {}).get("schema", {})
        required = set(schema.get("required", []))
        properties = set(schema.get("properties", {}).keys())

        if required.issubset(properties):
            return 5

        missing = required - properties
        penalty = len(missing)
        return max(0, 5 - penalty)

    def _score_pattern_coverage(self, contract: dict) -> int:
        """B1. Coherencia de Patrones [10 pts]"""
        patterns = contract.get("question_context", {}).get("patterns", [])
        expected = contract.get("question_context", {}).get("expected_elements", [])

        if not patterns:
            return 0

        coverage_score = min(5, len(patterns) / 5 * 5) if patterns else 0

        weights_valid = all(0 < p.get("confidence_weight", 0) <= 1 for p in patterns)
        weight_score = 3 if weights_valid else 0

        ids = [p.get("id") for p in patterns]
        id_score = 2 if len(ids) == len(set(ids)) and all(id and "PAT-" in str(id) for id in ids) else 0

        return int(coverage_score + weight_score + id_score)

    def _score_method_specificity(self, contract: dict) -> int:
        """B2. Especificidad Metodológica [10 pts]"""
        methods = contract.get("output_contract", {}).get("human_readable_output", {}).get("methodological_depth", {}).get("methods", [])

        if not methods:
            return 5

        generic_phrases = ["Execute", "Process results", "Return structured output", "Run analysis", "Perform calculation"]
        total_steps = 0
        non_generic_steps = 0

        for method in methods[:5]:
            steps = method.get("technical_approach", {}).get("steps", [])
            total_steps += len(steps)
            non_generic_steps += sum(1 for s in steps
                                     if not any(g in s.get("description", "") for g in generic_phrases))

        if total_steps == 0:
            return 5

        specificity_ratio = non_generic_steps / total_steps
        return int(10 * specificity_ratio)

    def _score_validation_rules(self, contract: dict) -> int:
        """B3. Reglas de Validación [10 pts]"""
        rules = contract.get("validation", {}).get("rules", [])
        expected = contract.get("question_context", {}).get("expected_elements", [])

        if not rules:
            return 0

        required_elements = {e.get("type") for e in expected if e.get("required")}
        validated_elements = set()

        for rule in rules:
            if "must_contain" in rule:
                validated_elements.update(rule["must_contain"].get("elements", []))
            if "should_contain" in rule:
                validated_elements.update(rule["should_contain"].get("elements", []))

        coverage = len(required_elements & validated_elements) / len(required_elements) if required_elements else 1
        coverage_score = int(5 * coverage)

        must_count = sum(1 for r in rules if "must_contain" in r)
        should_count = sum(1 for r in rules if "should_contain" in r)
        balance_score = 3 if must_count <= 2 and should_count >= must_count else 1

        failure_score = 2 if contract.get("error_handling", {}).get("failure_contract", {}).get("emit_code") else 0

        return coverage_score + balance_score + failure_score

    def _score_documentation_quality(self, contract: dict) -> int:
        """C1. Documentación Epistemológica [5 pts]"""
        return 3

    def _score_human_template(self, contract: dict) -> int:
        """C2. Template Human-Readable [5 pts]"""
        template = contract.get("output_contract", {}).get("human_readable_output", {}).get("template", {})

        score = 0
        question_id = contract.get("identity", {}).get("question_id", "")
        if question_id and question_id in str(template.get("title", "")):
            score += 3

        template_str = str(template)
        if "{score}" in template_str or "{evidence" in template_str:
            score += 2

        return score

    def _score_metadata_completeness(self, contract: dict) -> int:
        """C3. Metadatos y Trazabilidad [5 pts]"""
        identity = contract.get("identity", {})
        score = 0

        contract_hash = identity.get("contract_hash", "")
        if contract_hash and len(contract_hash) == 64:
            score += 2
        if identity.get("created_at"):
            score += 1
        if identity.get("validated_against_schema"):
            score += 1
        if identity.get("contract_version") and "." in identity["contract_version"]:
            score += 1

        return score

    def _triage_decision(self, tier1_scores: dict, tier2_scores: dict,
                        tier1_total: int, tier2_total: int, total_score: int) -> str:
        """Determine triage decision based on scores"""

        if tier1_total < 35:
            blockers = []
            if tier1_scores["A1_identity_schema"] < 15:
                blockers.append("IDENTITY_SCHEMA_MISMATCH")
            if tier1_scores["A2_method_assembly"] < 12:
                blockers.append("ASSEMBLY_SOURCES_BROKEN")
            if tier1_scores["A3_signal_integrity"] < 5:
                blockers.append("SIGNAL_THRESHOLD_ZERO")
            if tier1_scores["A4_output_schema"] < 3:
                blockers.append("SCHEMA_INVALID")

            if len(blockers) >= 2:
                return f"REFORMULAR_COMPLETO: {', '.join(blockers)}"
            elif "ASSEMBLY_SOURCES_BROKEN" in blockers:
                return "REFORMULAR_ASSEMBLY"
            elif "IDENTITY_SCHEMA_MISMATCH" in blockers:
                return "REFORMULAR_SCHEMA"
            else:
                return "PARCHEAR_CRITICO"

        elif tier1_total >= 45 and total_score >= 70:
            return "PARCHEAR_MINOR"
        elif tier1_total >= 35 and total_score >= 60:
            return "PARCHEAR_MAJOR"
        elif tier2_scores["B2_method_specificity"] < 3:
            return "PARCHEAR_DOCS"
        elif tier2_scores["B1_pattern_coverage"] < 6:
            return "PARCHEAR_PATTERNS"
        else:
            return "PARCHEAR_MAJOR"

    def _identify_gaps(self, tier1_scores: dict, tier2_scores: dict,
                      tier3_scores: dict, contract: dict) -> list[dict]:
        """Identify specific gaps in the contract"""
        gaps = []

        if tier1_scores["A1_identity_schema"] < 15:
            gaps.append({
                "severity": "CRITICAL",
                "category": "schema_mismatch",
                "description": "Identity and output schema fields do not match",
                "score": tier1_scores["A1_identity_schema"],
                "threshold": 15
            })

        if tier1_scores["A2_method_assembly"] < 12:
            methods = contract.get("method_binding", {}).get("methods", [])
            assembly_rules = contract.get("evidence_assembly", {}).get("assembly_rules", [])
            provides = {m.get("provides") for m in methods if m.get("provides")}
            sources = set()
            for rule in assembly_rules:
                sources.update(rule.get("sources", []))
            orphans = list(sources - provides)

            gaps.append({
                "severity": "CRITICAL",
                "category": "assembly_orphans",
                "description": f"Assembly rules reference non-existent provides: {orphans}",
                "orphan_sources": orphans,
                "score": tier1_scores["A2_method_assembly"],
                "threshold": 12
            })

        if tier1_scores["A3_signal_integrity"] < 5:
            threshold = contract.get("signal_requirements", {}).get("minimum_signal_threshold", 0)
            gaps.append({
                "severity": "CRITICAL",
                "category": "signal_threshold_zero",
                "description": f"Signal threshold is {threshold}, must be > 0",
                "current_threshold": threshold,
                "score": tier1_scores["A3_signal_integrity"],
                "threshold": 5
            })

        if tier2_scores["B2_method_specificity"] < 5:
            gaps.append({
                "severity": "HIGH",
                "category": "weak_methodological_depth",
                "description": "Method descriptions are too generic or boilerplate",
                "score": tier2_scores["B2_method_specificity"],
                "threshold": 5
            })

        if tier2_scores["B1_pattern_coverage"] < 6:
            patterns_count = len(contract.get("question_context", {}).get("patterns", []))
            gaps.append({
                "severity": "HIGH",
                "category": "insufficient_patterns",
                "description": f"Only {patterns_count} patterns defined, need more coverage",
                "patterns_count": patterns_count,
                "score": tier2_scores["B1_pattern_coverage"],
                "threshold": 6
            })

        if tier3_scores["C2_human_template"] < 3:
            gaps.append({
                "severity": "MEDIUM",
                "category": "documentation_gaps",
                "description": "Human-readable template lacks proper references or placeholders",
                "score": tier3_scores["C2_human_template"],
                "threshold": 3
            })

        return gaps

    def _determine_verdict_status(self, tier1_total: int, total_score: int,
                                   triage_decision: str) -> str:
        """Determine overall verdict status"""
        if "REFORMULAR" in triage_decision:
            return "REQUIRES_REFORMULATION"
        elif total_score >= 80 and tier1_total >= 45:
            return "PRODUCTION"
        elif total_score >= 60 and tier1_total >= 35:
            return "PATCHABLE"
        else:
            return "REQUIRES_MAJOR_WORK"

    def _calculate_summary_statistics(self):
        """Calculate summary statistics across all audited contracts"""
        audits = [a for a in self.results["per_contract_audits"].values()
                 if isinstance(a, dict) and "total_score" in a]

        if not audits:
            return

        total_scores = [a["total_score"] for a in audits]
        tier1_scores = [a["tier1_total"] for a in audits]

        verdict_counts = defaultdict(int)
        triage_counts = defaultdict(int)

        for audit in audits:
            verdict_counts[audit["verdict"]["status"]] += 1
            triage_key = audit["triage_decision"].split(":")[0]
            triage_counts[triage_key] += 1

        self.results["summary_statistics"] = {
            "contracts_audited": len(audits),
            "average_total_score": round(sum(total_scores) / len(total_scores), 1),
            "average_tier1_score": round(sum(tier1_scores) / len(tier1_scores), 1),
            "min_score": min(total_scores),
            "max_score": max(total_scores),
            "production_ready": verdict_counts.get("PRODUCTION", 0),
            "patchable": verdict_counts.get("PATCHABLE", 0),
            "requires_reformulation": verdict_counts.get("REQUIRES_REFORMULATION", 0),
            "requires_major_work": verdict_counts.get("REQUIRES_MAJOR_WORK", 0),
            "verdict_distribution": dict(verdict_counts),
            "triage_distribution": dict(triage_counts)
        }

    def _generate_transformation_manifest(self):
        """Generate manifest of transformation requirements categorized by severity"""

        critical_items = []
        high_items = []
        medium_items = []

        for qid, audit in self.results["per_contract_audits"].items():
            if not isinstance(audit, dict) or "gaps_identified" not in audit:
                continue

            for gap in audit["gaps_identified"]:
                severity = gap.get("severity", "MEDIUM")
                item = {
                    "question_id": qid,
                    "category": gap.get("category"),
                    "description": gap.get("description"),
                    "score": gap.get("score"),
                    "threshold": gap.get("threshold"),
                    "details": {k: v for k, v in gap.items()
                               if k not in ["severity", "category", "description", "score", "threshold"]}
                }

                if severity == "CRITICAL":
                    critical_items.append(item)
                elif severity == "HIGH":
                    high_items.append(item)
                else:
                    medium_items.append(item)

        self.results["transformation_manifest"] = {
            "CRITICAL": {
                "count": len(critical_items),
                "description": "CRITICAL: schema mismatches, assembly orphans, signal threshold zero",
                "items": critical_items
            },
            "HIGH": {
                "count": len(high_items),
                "description": "HIGH: weak methodological depth, insufficient patterns",
                "items": high_items
            },
            "MEDIUM": {
                "count": len(medium_items),
                "description": "MEDIUM: documentation gaps, template issues",
                "items": medium_items
            }
        }

    def save_results(self, output_path: str = "contract_audit_Q005_Q020.json"):
        """Save audit results to JSON file"""
        output_file = Path(output_path)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Audit report saved to: {output_file}")

        manifest_file = Path("transformation_requirements_manifest.json")
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(self.results["transformation_manifest"], f, indent=2, ensure_ascii=False)
        print(f"✅ Transformation manifest saved to: {manifest_file}")

    def print_summary(self):
        """Print summary of audit results"""
        print("\n" + "=" * 80)
        print("AUDIT SUMMARY")
        print("=" * 80)

        stats = self.results["summary_statistics"]
        print(f"\nContracts Audited: {stats.get('contracts_audited', 0)}")
        print(f"Average Score: {stats.get('average_total_score', 0)}/100")
        print(f"Average Tier 1 (Critical): {stats.get('average_tier1_score', 0)}/55")
        print(f"Score Range: {stats.get('min_score', 0)} - {stats.get('max_score', 0)}")

        print("\nVerdict Distribution:")
        print(f"  ✅ Production Ready: {stats.get('production_ready', 0)}")
        print(f"  ⚠️  Patchable: {stats.get('patchable', 0)}")
        print(f"  🔧 Requires Reformulation: {stats.get('requires_reformulation', 0)}")
        print(f"  ❌ Requires Major Work: {stats.get('requires_major_work', 0)}")

        manifest = self.results["transformation_manifest"]
        print("\nTransformation Requirements:")
        print(f"  🔴 CRITICAL: {manifest['CRITICAL']['count']} issues")
        print(f"  🟠 HIGH: {manifest['HIGH']['count']} issues")
        print(f"  🟡 MEDIUM: {manifest['MEDIUM']['count']} issues")

        print("\n" + "=" * 80)


def main():
    """Main execution"""
    validator = CQVRValidator()

    try:
        validator.audit_all_contracts()
        validator.save_results()
        validator.print_summary()

        stats = validator.results["summary_statistics"]
        if stats.get("requires_reformulation", 0) > 0:
            print("\n⚠️  WARNING: Some contracts require reformulation")
            return 1

        return 0

    except Exception as e:
        print(f"\n❌ Audit failed with error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

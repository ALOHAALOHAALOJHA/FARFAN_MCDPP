import hashlib
import json
import sys
from pathlib import Path


from farfan_pipeline.phases.Phase_02.contract_validator_cqvr import CQVRValidator  # noqa: E402

# Use modular questionnaire helper instead of monolith
from tests.test_helpers.questionnaire_compat import get_questionnaire_data, get_questionnaire_sha256


CONTRACTS_DIR = (
    REPO_ROOT
    / "src"
    / "farfan_pipeline"
    / "phases"
    / "Phase_02"
    / "json_files_phase_two"
    / "executor_contracts"
    / "specialized"
)


def _monolith_source_hash() -> str:
    """
    Get source hash from modular questionnaire.

    Previously loaded from questionnaire_monolith.json, now uses
    the modular CQC via the compatibility helper.
    """
    # Try to get SHA256 from CQC loader first
    sha256 = get_questionnaire_sha256()
    if sha256:
        return sha256

    # Fallback: compute hash from assembled questionnaire data
    questionnaire = get_questionnaire_data()
    questionnaire_str = json.dumps(questionnaire, sort_keys=True)
    return hashlib.sha256(questionnaire_str.encode()).hexdigest()


def test_batch6_contracts_are_production_ready() -> None:
    validator = CQVRValidator()
    failing: list[str] = []
    for q_num in range(126, 151):
        contract_path = CONTRACTS_DIR / f"Q{q_num:03d}.v3.json"
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        decision = validator.validate_contract(contract)
        if not decision.is_production_ready():
            failing.append(
                f"Q{q_num:03d} score={decision.score.total_score:.1f} tier1={decision.score.tier1_score:.1f}"
            )
    assert not failing, f"Non-production contracts: {failing}"


def test_batch6_signal_thresholds_normalized() -> None:
    for q_num in range(126, 151):
        contract_path = CONTRACTS_DIR / f"Q{q_num:03d}.v3.json"
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        signal_reqs = contract.get("signal_requirements", {})
        assert signal_reqs.get("minimum_signal_threshold") == 0.5
        assert signal_reqs.get("preferred_signal_types") == [
            "policy_instrument_detected",
            "activity_specification_found",
            "implementation_timeline_present",
        ]


def test_batch6_assembly_rules_use_all_provides() -> None:
    for q_num in range(126, 151):
        contract_path = CONTRACTS_DIR / f"Q{q_num:03d}.v3.json"
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        methods = contract.get("method_binding", {}).get("methods", [])
        provides_set = {
            m.get("provides")
            for m in methods
            if isinstance(m, dict) and isinstance(m.get("provides"), str) and m.get("provides")
        }
        assembly_rules = contract.get("evidence_assembly", {}).get("assembly_rules", [])
        assert assembly_rules, f"Missing evidence_assembly.assembly_rules in Q{q_num:03d}"
        sources = assembly_rules[0].get("sources", [])
        sources_set = {s for s in sources if isinstance(s, str)}
        assert sources_set == provides_set, (
            f"Q{q_num:03d} provides/sources mismatch: "
            f"provides={len(provides_set)} sources={len(sources_set)}"
        )


def test_batch6_validation_rules_cover_required_expected_elements() -> None:
    for q_num in range(126, 151):
        contract_path = CONTRACTS_DIR / f"Q{q_num:03d}.v3.json"
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        expected_elements = contract.get("question_context", {}).get("expected_elements", [])
        required = {
            e.get("type")
            for e in expected_elements
            if isinstance(e, dict) and e.get("required") and isinstance(e.get("type"), str)
        }
        rules = contract.get("validation_rules", {}).get("rules", [])
        must: set[str] = set()
        should: set[str] = set()
        for rule in rules:
            if not isinstance(rule, dict):
                continue
            must_contain = rule.get("must_contain", {})
            if isinstance(must_contain, dict):
                must.update([e for e in must_contain.get("elements", []) if isinstance(e, str)])
            should_contain = rule.get("should_contain", [])
            if isinstance(should_contain, list):
                for item in should_contain:
                    if isinstance(item, dict):
                        should.update([e for e in item.get("elements", []) if isinstance(e, str)])
        assert required.issubset(
            must | should
        ), f"Q{q_num:03d} missing required validation coverage"


def test_batch6_methodological_depth_is_non_boilerplate() -> None:
    generic_step_patterns = ["Execute", "Process results", "Return structured output"]
    generic_complexity_patterns = ["O(n) where n=input size"]
    generic_assumption_patterns = ["preprocessed"]

    for q_num in range(126, 151):
        contract_path = CONTRACTS_DIR / f"Q{q_num:03d}.v3.json"
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        md = contract.get("methodological_depth", {})
        methods = md.get("methods", [])
        assert methods, f"Q{q_num:03d} missing methodological_depth.methods"

        technical = methods[0].get("technical_approach", {}) if isinstance(methods[0], dict) else {}
        steps = technical.get("steps", [])
        assert (
            steps
        ), f"Q{q_num:03d} missing methodological_depth.methods[0].technical_approach.steps"

        step_descs = [s.get("description", "") for s in steps if isinstance(s, dict)]
        assert all(
            not any(pat in desc for pat in generic_step_patterns) for desc in step_descs
        ), f"Q{q_num:03d} contains boilerplate step descriptions"

        complexity = technical.get("complexity", "")
        assert not any(pat in str(complexity) for pat in generic_complexity_patterns)

        assumptions = technical.get("assumptions", [])
        assert all(
            not any(pat in str(a).lower() for pat in generic_assumption_patterns)
            for a in assumptions
        )


def test_batch6_traceability_source_hash_set() -> None:
    expected_hash = _monolith_source_hash()
    for q_num in range(126, 151):
        contract_path = CONTRACTS_DIR / f"Q{q_num:03d}.v3.json"
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        source_hash = contract.get("traceability", {}).get("source_hash", "")
        assert source_hash == expected_hash

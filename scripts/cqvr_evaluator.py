#!/usr/bin/env python3
"""
CQVR Evaluator - Contract Quality Validation and Remediation
Complete implementation with all scoring functions, decision logic, and report generation.
"""
import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import track
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None  # type: ignore


@dataclass
class CQVRScore:
    """CQVR scoring results"""
    tier1_score: float
    tier2_score: float
    tier3_score: float
    total_score: float
    tier1_max: float = 55.0
    tier2_max: float = 30.0
    tier3_max: float = 15.0
    total_max: float = 100.0
    component_scores: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CQVRDecision:
    """CQVR triage decision"""
    decision: str
    score: CQVRScore
    blockers: List[str]
    warnings: List[str]
    recommendations: List[Dict[str, str]]
    rationale: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision,
            "score": self.score.to_dict(),
            "blockers": self.blockers,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "rationale": self.rationale,
            "timestamp": self.timestamp,
        }


def verify_identity_schema_coherence(contract: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    Verify coherence between identity and output schema.
    
    A1: Identity-Schema Coherence (20 points max)
    - Ensures critical fields match between identity and schema
    
    Returns:
        Tuple of (score, issues_list)
    """
    identity = contract.get("identity", {})
    output_schema = contract.get("output_contract", {}).get("schema", {})
    properties = output_schema.get("properties", {})

    score = 0
    issues = []

    fields_to_check = {
        "question_id": 5,
        "policy_area_id": 5,
        "dimension_id": 5,
        "question_global": 3,
        "base_slot": 2,
    }

    for field, points in fields_to_check.items():
        identity_value = identity.get(field)
        schema_prop = properties.get(field, {})
        schema_value = schema_prop.get("const")

        if identity_value is None:
            issues.append(f"Missing '{field}' in identity")
            continue

        if schema_value is None:
            issues.append(f"Missing const for '{field}' in output_schema")
            continue

        if identity_value == schema_value:
            score += points
        else:
            issues.append(
                f"Identity-Schema mismatch for '{field}': "
                f"identity={identity_value}, schema={schema_value}"
            )

    return score, issues


def verify_method_assembly_alignment(contract: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    Verify alignment between method binding and evidence assembly.
    
    A2: Method-Assembly Alignment (20 points max)
    - Ensures methods defined in binding are properly used in assembly
    
    Returns:
        Tuple of (score, issues_list)
    """
    method_binding = contract.get("method_binding", {})
    methods = method_binding.get("methods", [])
    evidence_assembly = contract.get("evidence_assembly", {})
    assembly_rules = evidence_assembly.get("assembly_rules", [])

    score = 0
    issues = []

    if not methods:
        issues.append("No methods defined in method_binding")
        return 0, issues

    # Build provides set
    provides_set = set()
    for method in methods:
        provides = method.get("provides", "")
        if provides:
            provides_set.add(provides)

    # Check method count accuracy
    method_count_declared = method_binding.get("method_count", len(methods))
    if method_count_declared == len(methods):
        score += 3
    else:
        issues.append(
            f"method_count mismatch: "
            f"declared={method_count_declared}, actual={len(methods)}"
        )

    # Check for orphan sources
    sources_referenced = set()
    orphan_sources = []

    for rule in assembly_rules:
        sources = rule.get("sources", [])
        for source in sources:
            if isinstance(source, dict):
                source_key = source.get("namespace", "")
                if source_key and not source_key.startswith("*."):
                    sources_referenced.add(source_key)
                    if source_key not in provides_set:
                        orphan_sources.append(source_key)
            elif isinstance(source, str):
                if not source.startswith("*."):
                    sources_referenced.add(source)
                    if source not in provides_set:
                        orphan_sources.append(source)

    if not orphan_sources:
        score += 10
    else:
        issues.append(f"Assembly sources not in provides: {orphan_sources[:5]}")

    # Calculate usage ratio
    usage_ratio = len(sources_referenced) / len(provides_set) if provides_set else 0
    if usage_ratio >= 0.9:
        score += 5
    elif usage_ratio >= 0.7:
        score += 3
    elif usage_ratio >= 0.5:
        score += 1
    else:
        issues.append(
            f"Low method usage ratio: {usage_ratio:.1%} "
            f"({len(sources_referenced)}/{len(provides_set)})"
        )

    if not orphan_sources:
        score += 2

    return score, issues


def verify_signal_requirements(contract: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    Verify signal requirement configuration.
    
    A3: Signal Requirements (10 points max)
    - Ensures signal validation is properly configured
    
    Returns:
        Tuple of (score, issues_list)
    """
    signal_requirements = contract.get("signal_requirements", {})

    score = 0
    issues = []

    mandatory_signals = signal_requirements.get("mandatory_signals", [])
    threshold = signal_requirements.get("minimum_signal_threshold", 0.0)
    aggregation = signal_requirements.get("signal_aggregation", "")

    # Critical blocker check
    if mandatory_signals and threshold <= 0:
        issues.append(
            f"CRITICAL - minimum_signal_threshold={threshold} "
            "but mandatory_signals defined. "
            "This allows zero-strength signals to pass validation."
        )
        return 0, issues

    # Score mandatory signals configuration
    if mandatory_signals and threshold > 0:
        score += 5
    elif not mandatory_signals:
        score += 5

    # Check signal format
    if mandatory_signals and all(isinstance(s, str) for s in mandatory_signals):
        score += 3
    elif mandatory_signals:
        issues.append("Some mandatory_signals are not well-formed strings")

    # Check aggregation method
    valid_aggregations = ["weighted_mean", "minimum", "product", "harmonic_mean"]
    if aggregation in valid_aggregations:
        score += 2
    elif aggregation:
        issues.append(f"Unknown signal_aggregation method: {aggregation}")

    return score, issues


def verify_output_schema(contract: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    Verify output schema completeness.
    
    A4: Output Schema (5 points max)
    - Ensures output schema is properly defined
    
    Returns:
        Tuple of (score, issues_list)
    """
    output_contract = contract.get("output_contract", {})
    schema = output_contract.get("schema", {})

    score = 0
    issues = []

    required = schema.get("required", [])
    properties = schema.get("properties", {})

    if not required:
        issues.append("No required fields in output_schema")
        return 0, issues

    # Check all required fields are defined
    all_defined = all(field in properties for field in required)
    if all_defined:
        score += 3
    else:
        missing = [f for f in required if f not in properties]
        issues.append(f"Required fields not in properties: {missing}")

    # Check traceability
    traceability = contract.get("traceability", {})
    source_hash = traceability.get("source_hash", "")
    if source_hash and not source_hash.startswith("TODO"):
        score += 2
    else:
        issues.append("source_hash is placeholder or missing")
        score += 1

    return score, issues


def verify_pattern_coverage(contract: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    Verify pattern coverage for question context.
    
    B1: Pattern Coverage (10 points max)
    - Ensures patterns adequately cover expected elements
    
    Returns:
        Tuple of (score, issues_list)
    """
    question_context = contract.get("question_context", {})
    patterns = question_context.get("patterns", [])
    expected_elements = question_context.get("expected_elements", [])

    score = 0
    issues = []

    if not expected_elements:
        issues.append("No expected_elements defined")
        return 0, issues

    if not patterns:
        issues.append("No patterns defined")
        return 0, issues

    required_elements = [e for e in expected_elements if e.get("required")]

    # Calculate coverage score
    coverage_score = min(len(patterns) / max(len(required_elements), 1) * 5.0, 5.0)
    score += int(coverage_score)

    # Check confidence weights
    confidence_weights = [
        p.get("confidence_weight", 0) for p in patterns if isinstance(p, dict)
    ]
    if confidence_weights:
        valid_weights = all(0 <= w <= 1 for w in confidence_weights)
        if valid_weights:
            score += 3
        else:
            issues.append("Some confidence_weights out of [0,1] range")

    # Check pattern IDs uniqueness
    pattern_ids = [p.get("id", "") for p in patterns if isinstance(p, dict)]
    unique_ids = len(set(pattern_ids)) == len(pattern_ids)
    if unique_ids and all(pattern_ids):
        score += 2
    else:
        issues.append("Pattern IDs not unique or missing")

    return score, issues


def verify_method_specificity(contract: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    Verify methodological specificity.
    
    B2: Method Specificity (10 points max)
    - Ensures methods have specific, non-boilerplate documentation
    
    Returns:
        Tuple of (score, issues_list)
    """
    methodological_depth = contract.get("methodological_depth", {})
    methods = methodological_depth.get("methods", [])

    score = 0
    issues = []

    if not methods:
        issues.append("No methodological_depth.methods defined")
        return 0, issues

    generic_patterns = [
        "Execute", "Process results", "Return structured output",
        "O(n) where n=input size", "Input data is preprocessed and valid"
    ]

    specific_count = 0
    boilerplate_count = 0

    for method_info in methods:
        technical = method_info.get("technical_approach", {})
        steps = technical.get("steps", [])
        complexity = technical.get("complexity", "")

        is_specific = True

        for step in steps:
            step_desc = step.get("description", "")
            if any(pattern in step_desc for pattern in generic_patterns):
                is_specific = False
                boilerplate_count += 1
                break

        if is_specific and complexity and not any(p in complexity for p in generic_patterns):
            specific_count += 1

    # Calculate specificity score
    if methods:
        specificity_ratio = specific_count / len(methods)
        score += int(specificity_ratio * 6.0)

    # Score complexity documentation
    complexity_count = sum(
        1 for m in methods
        if m.get("technical_approach", {}).get("complexity")
        and "input size" not in m.get("technical_approach", {}).get("complexity", "")
    )
    if methods:
        score += int((complexity_count / len(methods)) * 2.0)

    # Score assumptions documentation
    assumptions_count = sum(
        1 for m in methods
        if m.get("technical_approach", {}).get("assumptions")
        and not any(
            "preprocessed" in str(a).lower()
            for a in m.get("technical_approach", {}).get("assumptions", [])
        )
    )
    if methods:
        score += int((assumptions_count / len(methods)) * 2.0)

    if boilerplate_count > len(methods) * 0.5:
        issues.append(
            f"High boilerplate ratio: {boilerplate_count}/{len(methods)} methods"
        )

    return score, issues


def verify_validation_rules(contract: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    Verify validation rules completeness.
    
    B3: Validation Rules (10 points max)
    - Ensures validation rules cover expected elements
    
    Returns:
        Tuple of (score, issues_list)
    """
    validation_rules = contract.get("validation_rules", {})
    rules = validation_rules.get("rules", [])
    question_context = contract.get("question_context", {})
    expected_elements = question_context.get("expected_elements", [])

    score = 0
    issues = []

    if not rules:
        issues.append("No validation_rules.rules defined")
        return 0, issues

    required_elements = {e.get("type") for e in expected_elements if e.get("required")}

    must_contain_elements = set()
    should_contain_elements = set()

    for rule in rules:
        must_contain = rule.get("must_contain", {})
        if isinstance(must_contain, dict):
            elements = must_contain.get("elements", [])
            must_contain_elements.update(elements)

        should_contain = rule.get("should_contain", [])
        if isinstance(should_contain, list):
            for item in should_contain:
                if isinstance(item, dict):
                    elements = item.get("elements", [])
                    should_contain_elements.update(elements)

    all_validation_elements = must_contain_elements | should_contain_elements

    # Check coverage of required elements
    if required_elements and required_elements.issubset(all_validation_elements):
        score += 5
    elif required_elements:
        missing = required_elements - all_validation_elements
        issues.append(f"Required elements not in validation rules: {missing}")

    # Score validation structure
    if must_contain_elements and should_contain_elements:
        score += 3
    elif must_contain_elements or should_contain_elements:
        score += 1

    # Check error handling
    error_handling = contract.get("error_handling", {})
    failure_contract = error_handling.get("failure_contract", {})
    if failure_contract.get("emit_code"):
        score += 2
    else:
        issues.append("No emit_code in failure_contract")

    return score, issues


def verify_documentation_quality(contract: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    Verify documentation quality.
    
    C1: Documentation Quality (5 points max)
    - Ensures epistemological foundations are documented
    
    Returns:
        Tuple of (score, issues_list)
    """
    methodological_depth = contract.get("methodological_depth", {})
    methods = methodological_depth.get("methods", [])

    score = 0
    issues = []

    if not methods:
        issues.append("No methodological_depth for documentation check")
        return 0, issues

    boilerplate_patterns = [
        "analytical paradigm",
        "This method contributes",
        "method implements structured analysis"
    ]

    specific_paradigms = 0
    for method_info in methods:
        epist = method_info.get("epistemological_foundation", {})
        paradigm = epist.get("paradigm", "")
        justification = epist.get("justification", "")

        is_specific = True
        for pattern in boilerplate_patterns:
            if pattern.lower() in paradigm.lower() or pattern.lower() in justification.lower():
                is_specific = False
                break

        if is_specific:
            specific_paradigms += 1

    # Score paradigm specificity
    if methods:
        paradigm_ratio = specific_paradigms / len(methods)
        score += int(paradigm_ratio * 2.0)

    # Score justification quality
    justifications_with_why = sum(
        1 for m in methods
        if (
            "why" in m.get("epistemological_foundation", {}).get("justification", "").lower()
            or "vs" in m.get("epistemological_foundation", {}).get("justification", "").lower()
            or "alternative"
            in m.get("epistemological_foundation", {}).get("justification", "").lower()
        )
    )
    if methods:
        score += int((justifications_with_why / len(methods)) * 2.0)

    # Check for references
    has_references = any(
        m.get("epistemological_foundation", {}).get("theoretical_framework")
        for m in methods
    )
    if has_references:
        score += 1

    return score, issues


def verify_human_template(contract: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    Verify human-readable template quality.
    
    C2: Human Template (5 points max)
    - Ensures human-readable output is properly configured
    
    Returns:
        Tuple of (score, issues_list)
    """
    output_contract = contract.get("output_contract", {})
    human_readable = output_contract.get("human_readable_output", {})
    template = human_readable.get("template", {})

    score = 0
    issues = []

    identity = contract.get("identity", {})
    base_slot = identity.get("base_slot", "")
    question_id = identity.get("question_id", "")

    title = template.get("title", "")
    summary = template.get("summary", "")

    # Check for references in title
    has_references = False
    if base_slot and base_slot in title:
        has_references = True
    if question_id and question_id in title:
        has_references = True

    if has_references:
        score += 3
    else:
        issues.append("Template title does not reference base_slot or question_id")

    # Check for placeholders in summary
    import re
    placeholder_pattern = r"\{.*?\}"

    if re.search(placeholder_pattern, summary):
        score += 2
    else:
        issues.append("Template summary has no dynamic placeholders")

    return score, issues


def verify_metadata_completeness(contract: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    Verify metadata completeness.
    
    C3: Metadata Completeness (5 points max)
    - Ensures metadata is complete and valid
    
    Returns:
        Tuple of (score, issues_list)
    """
    identity = contract.get("identity", {})
    traceability = contract.get("traceability", {})

    score = 0
    issues = []

    # Check contract hash
    contract_hash = identity.get("contract_hash", "")
    if contract_hash and len(contract_hash) == 64:
        score += 2
    else:
        issues.append("contract_hash missing or invalid")

    # Check created_at timestamp
    created_at = identity.get("created_at", "")
    if created_at and "T" in created_at:
        score += 1
    else:
        issues.append("created_at missing or invalid ISO 8601 format")

    # Check validated_against
    validated_against = identity.get("validated_against_schema", "")
    if validated_against:
        score += 1

    # Check version
    contract_version = identity.get("contract_version", "")
    if contract_version and "." in contract_version:
        score += 1

    return min(score, 5), issues


class CQVRDecisionEngine:
    """Decision engine for CQVR triage"""

    TIER1_THRESHOLD = 35.0
    TIER1_PRODUCTION_THRESHOLD = 45.0
    TOTAL_PRODUCTION_THRESHOLD = 80.0

    @classmethod
    def make_decision(
        cls,
        score: CQVRScore,
        blockers: List[str],
        warnings: List[str]
    ) -> str:
        """
        Make triage decision based on score and issues.
        
        Decision Matrix:
        - PRODUCCION: Tier1 >= 45, Total >= 80, 0 blockers
        - PARCHEAR: Tier1 >= 35, Total >= 70, <= 2 blockers
        - REFORMULAR: Otherwise
        """
        # Critical Tier 1 failure
        if score.tier1_score < cls.TIER1_THRESHOLD:
            return "REFORMULAR"

        # Production ready
        if (score.tier1_score >= cls.TIER1_PRODUCTION_THRESHOLD and
            score.total_score >= cls.TOTAL_PRODUCTION_THRESHOLD and
            len(blockers) == 0):
            return "PRODUCCION"

        # Patchable
        if len(blockers) == 0 and score.total_score >= 70:
            return "PARCHEAR"

        if len(blockers) <= 2 and score.tier1_score >= 40:
            return "PARCHEAR"

        return "REFORMULAR"

    @classmethod
    def generate_rationale(
        cls,
        decision: str,
        score: CQVRScore,
        blockers: List[str],
        warnings: List[str]
    ) -> str:
        """Generate rationale for the decision"""
        tier1_pct = (score.tier1_score / score.tier1_max) * 100
        total_pct = (score.total_score / score.total_max) * 100

        if decision == "PRODUCCION":
            return (
                f"Contract approved for production: "
                f"Tier 1: {score.tier1_score:.1f}/{score.tier1_max} ({tier1_pct:.1f}%), "
                f"Total: {score.total_score:.1f}/{score.total_max} ({total_pct:.1f}%). "
                f"Blockers: {len(blockers)}, Warnings: {len(warnings)}."
            )
        elif decision == "PARCHEAR":
            return (
                f"Contract can be patched: "
                f"Tier 1: {score.tier1_score:.1f}/{score.tier1_max} ({tier1_pct:.1f}%), "
                f"Total: {score.total_score:.1f}/{score.total_max} ({total_pct:.1f}%). "
                f"Blockers: {len(blockers)} (resolvable), Warnings: {len(warnings)}. "
                f"Apply recommended patches to reach production threshold."
            )
        else:
            reason_parts = []
            if score.tier1_score < cls.TIER1_THRESHOLD:
                reason_parts.append(f"Tier 1 score below minimum ({cls.TIER1_THRESHOLD})")
            elif score.tier1_score < cls.TIER1_PRODUCTION_THRESHOLD:
                reason_parts.append(f"Tier 1 below production threshold ({cls.TIER1_PRODUCTION_THRESHOLD})")
            if score.total_score < cls.TOTAL_PRODUCTION_THRESHOLD:
                reason_parts.append(f"Total below production threshold ({cls.TOTAL_PRODUCTION_THRESHOLD})")
            if len(blockers) > 0:
                reason_parts.append(f"{len(blockers)} critical blocker(s)")

            reason_str = "; ".join(reason_parts) if reason_parts else "Failed decision criteria"

            return (
                f"Contract requires reformulation: "
                f"Tier 1: {score.tier1_score:.1f}/{score.tier1_max} ({tier1_pct:.1f}%), "
                f"Total: {score.total_score:.1f}/{score.total_max} ({total_pct:.1f}%). "
                f"Reasons: {reason_str}. Contract needs substantial rework."
            )


class CQVREvaluator:
    """Main CQVR Evaluator class"""

    def __init__(self) -> None:
        self.console = Console() if RICH_AVAILABLE else None

    def evaluate_contract(self, contract: Dict[str, Any]) -> CQVRDecision:
        """
        Evaluate a single contract.
        
        Returns:
            CQVRDecision with complete evaluation results
        """
        # Tier 1: Critical Components (55 points)
        a1_score, a1_issues = verify_identity_schema_coherence(contract)
        a2_score, a2_issues = verify_method_assembly_alignment(contract)
        a3_score, a3_issues = verify_signal_requirements(contract)
        a4_score, a4_issues = verify_output_schema(contract)

        tier1_score = a1_score + a2_score + a3_score + a4_score

        # Tier 2: Functional Components (30 points)
        b1_score, b1_issues = verify_pattern_coverage(contract)
        b2_score, b2_issues = verify_method_specificity(contract)
        b3_score, b3_issues = verify_validation_rules(contract)

        tier2_score = b1_score + b2_score + b3_score

        # Tier 3: Quality Components (15 points)
        c1_score, c1_issues = verify_documentation_quality(contract)
        c2_score, c2_issues = verify_human_template(contract)
        c3_score, c3_issues = verify_metadata_completeness(contract)

        tier3_score = c1_score + c2_score + c3_score

        # Aggregate scores
        score = CQVRScore(
            tier1_score=float(tier1_score),
            tier2_score=float(tier2_score),
            tier3_score=float(tier3_score),
            total_score=float(tier1_score + tier2_score + tier3_score),
            component_scores={
                "A1": float(a1_score),
                "A2": float(a2_score),
                "A3": float(a3_score),
                "A4": float(a4_score),
                "B1": float(b1_score),
                "B2": float(b2_score),
                "B3": float(b3_score),
                "C1": float(c1_score),
                "C2": float(c2_score),
                "C3": float(c3_score),
            }
        )

        # Collect all issues
        all_issues = (
            a1_issues + a2_issues + a3_issues + a4_issues +
            b1_issues + b2_issues + b3_issues +
            c1_issues + c2_issues + c3_issues
        )

        # Separate blockers and warnings
        blockers = [issue for issue in all_issues if "CRITICAL" in issue or "not in provides" in issue or "Required fields not" in issue]
        warnings = [issue for issue in all_issues if issue not in blockers]

        # Make decision
        decision = CQVRDecisionEngine.make_decision(score, blockers, warnings)
        rationale = CQVRDecisionEngine.generate_rationale(decision, score, blockers, warnings)

        # Generate recommendations
        recommendations = self._generate_recommendations(score, blockers, warnings)

        return CQVRDecision(
            decision=decision,
            score=score,
            blockers=blockers,
            warnings=warnings,
            recommendations=recommendations,
            rationale=rationale
        )

    def _generate_recommendations(
        self,
        score: CQVRScore,
        blockers: List[str],
        warnings: List[str]
    ) -> List[Dict[str, str]]:
        """Generate remediation recommendations"""
        recommendations = []

        # Tier 1 recommendations
        if score.tier1_score < 35:
            recommendations.append({
                "priority": "CRITICAL",
                "component": "Tier 1",
                "issue": "Tier 1 score below minimum threshold",
                "fix": "Review identity-schema coherence and method-assembly alignment",
                "impact": "Required for PARCHEAR eligibility"
            })

        # Signal requirements
        if any("signal" in b.lower() for b in blockers):
            recommendations.append({
                "priority": "HIGH",
                "component": "A3",
                "issue": "Signal threshold misconfiguration",
                "fix": "Set minimum_signal_threshold > 0 when mandatory_signals are defined",
                "impact": "+10 pts potential"
            })

        # Orphan sources
        if any("orphan" in b.lower() or "not in provides" in b.lower() for b in blockers):
            recommendations.append({
                "priority": "HIGH",
                "component": "A2",
                "issue": "Orphan assembly sources",
                "fix": "Ensure all assembly sources match method provides namespaces",
                "impact": "+10 pts potential"
            })

        return recommendations

    def evaluate_batch(
        self,
        contracts_dir: Path,
        start_q: int,
        end_q: int
    ) -> List[Tuple[str, CQVRDecision, Dict[str, Any]]]:
        """
        Evaluate a batch of contracts.
        
        Args:
            contracts_dir: Directory containing contract files
            start_q: Starting question number
            end_q: Ending question number
            
        Returns:
            List of (contract_id, decision, contract_data) tuples
        """
        results = []

        if self.console:
            self.console.print(f"\n[bold]Evaluating Q{start_q:03d}-Q{end_q:03d}[/bold]\n")
        else:
            print(f"\nEvaluating Q{start_q:03d}-Q{end_q:03d}\n")

        question_range = range(start_q, end_q + 1)
        iterator = track(question_range, description="Processing") if self.console else question_range

        for q_num in iterator:
            contract_id = f"Q{q_num:03d}"
            contract_path = contracts_dir / f"{contract_id}.v3.json"

            if not contract_path.exists():
                if not self.console:
                    print(f"⚠️  {contract_id}: File not found")
                continue

            try:
                with open(contract_path, "r", encoding="utf-8") as f:
                    contract = json.load(f)

                decision = self.evaluate_contract(contract)
                results.append((contract_id, decision, contract))

                if not self.console:
                    status = "✅" if decision.decision == "PRODUCCION" else ("⚠️" if decision.decision == "PARCHEAR" else "❌")
                    print(f"{status} {contract_id}: {decision.score.total_score:.1f}/100")

            except Exception as e:
                if not self.console:
                    print(f"❌ {contract_id}: ERROR - {e}")
                continue

        return results

    def generate_json_report(
        self,
        results: List[Tuple[str, CQVRDecision, Dict[str, Any]]],
        output_path: Path
    ) -> None:
        """Generate JSON report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "evaluator": "CQVR Evaluator v2.0",
            "rubric": "CQVR v2.0 (100 points)",
            "contracts_evaluated": len(results),
            "summary": self._calculate_summary(results),
            "contracts": [
                {
                    "contract_id": cid,
                    "decision": decision.to_dict(),
                }
                for cid, decision, _ in results
            ]
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        if self.console:
            self.console.print(f"✅ JSON report saved: {output_path}")
        else:
            print(f"✅ JSON report saved: {output_path}")

    def generate_console_report(
        self,
        results: List[Tuple[str, CQVRDecision, Dict[str, Any]]]
    ) -> None:
        """Generate human-readable console report"""
        if not self.console:
            self._generate_text_report(results)
            return

        # Summary statistics
        summary = self._calculate_summary(results)

        # Create summary table
        summary_table = Table(title="CQVR Evaluation Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="magenta")

        summary_table.add_row("Total Evaluated", str(summary["total_evaluated"]))
        summary_table.add_row("Average Score", f"{summary['average_score']:.1f}/100")
        summary_table.add_row("Production Ready", str(summary["production_ready"]))
        summary_table.add_row("Need Patches", str(summary["need_patches"]))
        summary_table.add_row("Need Reformulation", str(summary["need_reformulation"]))

        self.console.print(summary_table)

        # Results table
        results_table = Table(title="Individual Contract Results")
        results_table.add_column("Contract", style="cyan")
        results_table.add_column("Tier 1", justify="right")
        results_table.add_column("Tier 2", justify="right")
        results_table.add_column("Tier 3", justify="right")
        results_table.add_column("Total", justify="right", style="bold")
        results_table.add_column("Decision", justify="center")
        results_table.add_column("Blockers", justify="right")

        for cid, decision, _ in results:
            score = decision.score
            decision_emoji = "✅" if decision.decision == "PRODUCCION" else ("⚠️" if decision.decision == "PARCHEAR" else "❌")

            results_table.add_row(
                cid,
                f"{score.tier1_score:.0f}/55",
                f"{score.tier2_score:.0f}/30",
                f"{score.tier3_score:.0f}/15",
                f"{score.total_score:.0f}/100",
                f"{decision_emoji} {decision.decision}",
                str(len(decision.blockers))
            )

        self.console.print(results_table)

    def _generate_text_report(
        self,
        results: List[Tuple[str, CQVRDecision, Dict[str, Any]]]
    ) -> None:
        """Generate text-based report when Rich is not available"""
        summary = self._calculate_summary(results)

        print("\n" + "="*80)
        print("CQVR EVALUATION SUMMARY")
        print("="*80)
        print(f"Total Evaluated: {summary['total_evaluated']}")
        print(f"Average Score: {summary['average_score']:.1f}/100")
        print(f"Production Ready: {summary['production_ready']}")
        print(f"Need Patches: {summary['need_patches']}")
        print(f"Need Reformulation: {summary['need_reformulation']}")
        print("="*80)
        print("\nIndividual Results:")
        print("-"*80)

        for cid, decision, _ in results:
            score = decision.score
            if decision.decision == "PRODUCCION":
                status = "✅"
            elif decision.decision == "PARCHEAR":
                status = "⚠️"
            else:
                status = "❌"
            print(
                f"{status} {cid}: {score.total_score:.1f}/100 "
                f"[{decision.decision}] - {len(decision.blockers)} blockers"
            )

        print("-"*80)

    def _calculate_summary(
        self,
        results: List[Tuple[str, CQVRDecision, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Calculate summary statistics"""
        total = len(results)
        scores = [d.score.total_score for _, d, _ in results]
        avg_score = sum(scores) / len(scores) if scores else 0

        production_ready = sum(1 for _, d, _ in results if d.decision == "PRODUCCION")
        need_patches = sum(1 for _, d, _ in results if d.decision == "PARCHEAR")
        need_reformulation = sum(1 for _, d, _ in results if d.decision == "REFORMULAR")

        return {
            "total_evaluated": total,
            "average_score": avg_score,
            "production_ready": production_ready,
            "need_patches": need_patches,
            "need_reformulation": need_reformulation,
        }


def main() -> None:
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="CQVR Evaluator - Contract Quality Validation and Remediation"
    )
    parser.add_argument(
        "--contract",
        type=Path,
        help="Evaluate a single contract file"
    )
    parser.add_argument(
        "--batch",
        type=int,
        choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        help="Evaluate a batch (25 contracts each, batch 12 = 25 contracts)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Evaluate all 300 contracts"
    )
    parser.add_argument(
        "--contracts-dir",
        type=Path,
        default=Path("src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized"),
        help="Directory containing contract files"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/cqvr"),
        help="Output directory for reports"
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Generate JSON report only (no console output)"
    )

    args = parser.parse_args()

    # Validate arguments
    if not any([args.contract, args.batch, args.all]):
        parser.error("Must specify one of: --contract, --batch, or --all")

    evaluator = CQVREvaluator()

    # Single contract evaluation
    if args.contract:
        if not args.contract.exists():
            print(f"Error: Contract file not found: {args.contract}")
            sys.exit(1)

        with open(args.contract, "r", encoding="utf-8") as f:
            contract = json.load(f)

        decision = evaluator.evaluate_contract(contract)

        # Output results
        if not args.json_only:
            evaluator.generate_console_report([(args.contract.stem, decision, contract)])

        # Save JSON
        json_path = args.output_dir / f"{args.contract.stem}_CQVR.json"
        evaluator.generate_json_report([(args.contract.stem, decision, contract)], json_path)

    # Batch evaluation
    elif args.batch:
        start_q = (args.batch - 1) * 25 + 1
        end_q = min(args.batch * 25, 300)

        results = evaluator.evaluate_batch(args.contracts_dir, start_q, end_q)

        if not args.json_only:
            evaluator.generate_console_report(results)

        json_path = args.output_dir / f"batch_{args.batch}_CQVR.json"
        evaluator.generate_json_report(results, json_path)

    # All contracts
    elif args.all:
        results = evaluator.evaluate_batch(args.contracts_dir, 1, 300)

        if not args.json_only:
            evaluator.generate_console_report(results)

        json_path = args.output_dir / "all_contracts_CQVR.json"
        evaluator.generate_json_report(results, json_path)

    print("\n✅ Evaluation complete!")


if __name__ == "__main__":
    main()

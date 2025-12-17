#!/usr/bin/env python3
"""
CQVR Evaluator Script - Contract Quality Validation and Remediation
Implements all scoring functions with explicit return signatures
Supports single contract, batch (25), and full (300) evaluation modes

SEVERITY ENHANCEMENTS (v2.1 - 2025-12-17):
- Raised TIER1_THRESHOLD from 35 to 40 (stricter critical component requirements)
- Raised TIER1_PRODUCTION_THRESHOLD from 45 to 50 (near-perfect Tier 1 required)
- Raised TOTAL_PRODUCTION_THRESHOLD from 80 to 85 (higher overall quality bar)
- Added TIER2_MINIMUM=20 requirement (functional components must meet minimum)
- Added TIER3_MINIMUM=8 requirement (quality standards must meet minimum)
- Production now requires ZERO blockers (was allowing some blockers)
- PARCHEAR now allows max 1 blocker (was 2), requires tier1≥45 and total≥75
- A4 source_hash validation stricter: must be ≥32 chars, placeholder is CRITICAL
- These changes reduce error probability in production implementation
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# ============================================================================
# CORE SCORING FUNCTIONS (TIER 1: CRITICAL COMPONENTS - 55 pts)
# ============================================================================

# Constants for validation
MINIMUM_SOURCE_HASH_LENGTH = 32  # Minimum length for SHA256 or similar hashes


def verify_identity_schema_coherence(contract: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    A1. Verify coherence between identity and output_schema (20 pts max)
    
    Checks that critical fields (question_id, policy_area_id, dimension_id,
    question_global, base_slot) match between identity and schema.const values.
    
    Args:
        contract: Executor contract dict
        
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
        "base_slot": 2
    }
    
    for field, points in fields_to_check.items():
        identity_value = identity.get(field)
        schema_prop = properties.get(field, {})
        schema_value = schema_prop.get("const")
        
        if identity_value is not None and schema_value is not None:
            if identity_value == schema_value:
                score += points
            else:
                issues.append(
                    f"A1: Identity-Schema mismatch for '{field}': "
                    f"identity={identity_value}, schema={schema_value}"
                )
        else:
            if identity_value is None:
                issues.append(f"A1: Missing '{field}' in identity")
            if schema_value is None:
                issues.append(f"A1: Missing const for '{field}' in output_schema")
    
    return score, issues


def verify_method_assembly_alignment(contract: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    A2. Verify alignment between method_binding and evidence_assembly (20 pts max)
    
    Ensures all assembly sources reference valid method 'provides' namespaces
    and validates method count consistency.
    
    Args:
        contract: Executor contract dict
        
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
        issues.append("A2: No methods defined in method_binding")
        return 0, issues
    
    # Build provides set
    provides_set = set()
    for method in methods:
        provides = method.get("provides", "")
        if provides:
            provides_set.add(provides)
    
    # Check method_count consistency (3 pts)
    method_count_declared = method_binding.get("method_count", len(methods))
    if method_count_declared == len(methods):
        score += 3
    else:
        issues.append(
            f"A2: method_count mismatch: "
            f"declared={method_count_declared}, actual={len(methods)}"
        )
    
    # Check orphan sources (10 pts)
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
        issues.append(
            f"A2: Assembly sources not in provides: {orphan_sources[:5]}"
        )
    
    # Usage ratio (5 pts)
    usage_ratio = len(sources_referenced) / len(provides_set) if provides_set else 0
    if usage_ratio >= 0.9:
        score += 5
    elif usage_ratio >= 0.7:
        score += 3
    elif usage_ratio >= 0.5:
        score += 1
    else:
        issues.append(
            f"A2: Low method usage ratio: {usage_ratio:.1%} "
            f"({len(sources_referenced)}/{len(provides_set)})"
        )
    
    # Bonus for clean alignment (2 pts)
    if not orphan_sources:
        score += 2
    
    return score, issues


def verify_signal_requirements(contract: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    A3. Verify signal requirements configuration (10 pts max)
    
    Validates mandatory_signals, minimum_signal_threshold, and signal_aggregation.
    CRITICAL: threshold must be > 0 if mandatory_signals defined.
    
    Args:
        contract: Executor contract dict
        
    Returns:
        Tuple of (score, issues_list)
    """
    signal_requirements = contract.get("signal_requirements", {})
    
    score = 0
    issues = []
    
    mandatory_signals = signal_requirements.get("mandatory_signals", [])
    threshold = signal_requirements.get("minimum_signal_threshold", 0.0)
    aggregation = signal_requirements.get("signal_aggregation", "")
    
    # CRITICAL check: mandatory_signals + threshold=0 is invalid (0 pts)
    if mandatory_signals and threshold <= 0:
        issues.append(
            f"A3: CRITICAL - minimum_signal_threshold={threshold} "
            "but mandatory_signals defined. "
            "This allows zero-strength signals to pass validation."
        )
        return 0, issues
    
    # Valid signal configuration (5 pts)
    if mandatory_signals and threshold > 0:
        score += 5
    elif not mandatory_signals:
        score += 5
    
    # Well-formed mandatory signals (3 pts)
    if mandatory_signals and all(isinstance(s, str) for s in mandatory_signals):
        score += 3
    elif mandatory_signals:
        issues.append("A3: Some mandatory_signals are not well-formed strings")
    
    # Valid aggregation method (2 pts)
    if aggregation in ["weighted_mean", "minimum", "product", "harmonic_mean"]:
        score += 2
    elif aggregation:
        issues.append(f"A3: Unknown signal_aggregation method: {aggregation}")
    
    return score, issues


def verify_output_schema(contract: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    A4. Verify output schema completeness (5 pts max)
    
    Ensures all required fields have property definitions and checks traceability.
    
    Args:
        contract: Executor contract dict
        
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
        issues.append("A4: No required fields in output_schema")
        return 0, issues
    
    # All required fields have definitions (3 pts)
    all_defined = all(field in properties for field in required)
    if all_defined:
        score += 3
    else:
        missing = [f for f in required if f not in properties]
        issues.append(f"A4: Required fields not in properties: {missing}")
    
    # Traceability source_hash (2 pts) - STRICTER: now mandatory
    traceability = contract.get("traceability", {})
    source_hash = traceability.get("source_hash", "")
    if source_hash and not source_hash.startswith("TODO") and len(source_hash) >= MINIMUM_SOURCE_HASH_LENGTH:
        score += 2
    elif source_hash and not source_hash.startswith("TODO"):
        # Has hash but too short
        issues.append(f"A4: source_hash too short (minimum {MINIMUM_SOURCE_HASH_LENGTH} characters)")
        score += 1
    else:
        # Missing or placeholder - now a critical issue
        issues.append("A4: CRITICAL - source_hash is placeholder or missing (breaks provenance chain)")
        # No points awarded for missing provenance
    
    return score, issues


# ============================================================================
# TIER 2: FUNCTIONAL COMPONENTS (30 pts)
# ============================================================================


def verify_pattern_coverage(contract: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    B1. Verify pattern coverage of expected elements (10 pts max)
    
    Checks question_context patterns against expected_elements.
    
    Args:
        contract: Executor contract dict
        
    Returns:
        Tuple of (score, issues_list)
    """
    question_context = contract.get("question_context", {})
    patterns = question_context.get("patterns", [])
    expected_elements = question_context.get("expected_elements", [])
    
    score = 0
    issues = []
    
    if not expected_elements:
        issues.append("B1: No expected_elements defined")
        return 0, issues
    
    if not patterns:
        issues.append("B1: No patterns defined")
        return 0, issues
    
    required_elements = [e for e in expected_elements if e.get("required")]
    
    # Pattern coverage ratio (5 pts)
    coverage_score = min(len(patterns) / max(len(required_elements), 1) * 5.0, 5.0)
    score += int(coverage_score)
    
    # Valid confidence weights (3 pts)
    confidence_weights = [
        p.get("confidence_weight", 0) for p in patterns if isinstance(p, dict)
    ]
    if confidence_weights:
        valid_weights = all(0 <= w <= 1 for w in confidence_weights)
        if valid_weights:
            score += 3
        else:
            issues.append("B1: Some confidence_weights out of [0,1] range")
    
    # Unique pattern IDs (2 pts)
    pattern_ids = [p.get("id", "") for p in patterns if isinstance(p, dict)]
    unique_ids = len(set(pattern_ids)) == len(pattern_ids)
    if unique_ids and all(pattern_ids):
        score += 2
    else:
        issues.append("B1: Pattern IDs not unique or missing")
    
    return score, issues


def verify_method_specificity(contract: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    B2. Verify methodological specificity (10 pts max)
    
    Detects boilerplate vs specific technical approaches, complexity, and assumptions.
    
    Args:
        contract: Executor contract dict
        
    Returns:
        Tuple of (score, issues_list)
    """
    methodological_depth = contract.get("methodological_depth", {})
    methods = methodological_depth.get("methods", [])
    
    score = 0
    issues = []
    
    if not methods:
        issues.append("B2: No methodological_depth.methods defined")
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
    
    # Specificity ratio (6 pts)
    if methods:
        specificity_ratio = specific_count / len(methods)
        score += int(specificity_ratio * 6)
    
    # Non-generic complexity (2 pts)
    complexity_count = sum(
        1 for m in methods
        if m.get("technical_approach", {}).get("complexity")
        and "input size" not in m.get("technical_approach", {}).get("complexity", "")
    )
    if methods:
        score += int((complexity_count / len(methods)) * 2)
    
    # Specific assumptions (2 pts)
    assumptions_count = sum(
        1 for m in methods
        if m.get("technical_approach", {}).get("assumptions")
        and not any(
            "preprocessed" in str(a).lower()
            for a in m.get("technical_approach", {}).get("assumptions", [])
        )
    )
    if methods:
        score += int((assumptions_count / len(methods)) * 2)
    
    if boilerplate_count > len(methods) * 0.5:
        issues.append(
            f"B2: High boilerplate ratio: {boilerplate_count}/{len(methods)} methods"
        )
    
    return score, issues


def verify_validation_rules(contract: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    B3. Verify validation rules completeness (10 pts max)
    
    Ensures validation_rules.rules cover expected_elements and include error handling.
    
    Args:
        contract: Executor contract dict
        
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
        issues.append("B3: No validation_rules.rules defined")
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
    
    # Required elements coverage (5 pts)
    if required_elements and required_elements.issubset(all_validation_elements):
        score += 5
    elif required_elements:
        missing = required_elements - all_validation_elements
        issues.append(
            f"B3: Required elements not in validation rules: {missing}"
        )
    
    # Must/should contain presence (3 pts)
    if must_contain_elements and should_contain_elements:
        score += 3
    elif must_contain_elements or should_contain_elements:
        score += 1
    
    # Error handling (2 pts)
    error_handling = contract.get("error_handling", {})
    failure_contract = error_handling.get("failure_contract", {})
    if failure_contract.get("emit_code"):
        score += 2
    else:
        issues.append("B3: No emit_code in failure_contract")
    
    return score, issues


# ============================================================================
# TIER 3: QUALITY COMPONENTS (15 pts)
# ============================================================================


def verify_documentation_quality(contract: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    C1. Verify epistemological documentation quality (5 pts max)
    
    Checks for specific (non-boilerplate) paradigms, justifications, and frameworks.
    
    Args:
        contract: Executor contract dict
        
    Returns:
        Tuple of (score, issues_list)
    """
    methodological_depth = contract.get("methodological_depth", {})
    methods = methodological_depth.get("methods", [])
    
    score = 0
    issues = []
    
    if not methods:
        issues.append("C1: No methodological_depth for documentation check")
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
    
    # Specific paradigms (2 pts)
    if methods:
        paradigm_ratio = specific_paradigms / len(methods)
        score += int(paradigm_ratio * 2)
    
    # Justifications with "why" (2 pts)
    justifications_with_why = sum(
        1 for m in methods
        if (
            "why" in m.get("epistemological_foundation", {}).get("justification", "").lower()
            or "vs" in m.get("epistemological_foundation", {}).get("justification", "").lower()
            or "alternative" in m.get("epistemological_foundation", {}).get("justification", "").lower()
        )
    )
    if methods:
        score += int((justifications_with_why / len(methods)) * 2)
    
    # Theoretical framework references (1 pt)
    has_references = any(
        m.get("epistemological_foundation", {}).get("theoretical_framework")
        for m in methods
    )
    if has_references:
        score += 1
    
    return score, issues


def verify_human_template(contract: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    C2. Verify human-readable template quality (5 pts max)
    
    Ensures template references base_slot/question_id and has dynamic placeholders.
    
    Args:
        contract: Executor contract dict
        
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
    
    # Template references identity (3 pts)
    has_references = False
    if base_slot and base_slot in title:
        has_references = True
    if question_id and question_id in title:
        has_references = True
    
    if has_references:
        score += 3
    else:
        issues.append("C2: Template title does not reference base_slot or question_id")
    
    # Dynamic placeholders in summary (2 pts)
    import re
    placeholder_patterns = [r"\{.*?\}"]
    
    has_placeholders = False
    for pattern in placeholder_patterns:
        if re.search(pattern, summary):
            has_placeholders = True
            break
    
    if has_placeholders:
        score += 2
    else:
        issues.append("C2: Template summary has no dynamic placeholders")
    
    return score, issues


def verify_metadata_completeness(contract: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    C3. Verify metadata completeness (5 pts max)
    
    Validates contract_hash, created_at, contract_version, and source_hash.
    
    Args:
        contract: Executor contract dict
        
    Returns:
        Tuple of (score, issues_list)
    """
    identity = contract.get("identity", {})
    traceability = contract.get("traceability", {})
    
    score = 0
    issues = []
    
    # Contract hash (2 pts)
    contract_hash = identity.get("contract_hash", "")
    if contract_hash and len(contract_hash) == 64:
        score += 2
    else:
        issues.append("C3: contract_hash missing or invalid")
    
    # Created at timestamp (1 pt)
    created_at = identity.get("created_at", "")
    if created_at and "T" in created_at:
        score += 1
    else:
        issues.append("C3: created_at missing or invalid ISO 8601 format")
    
    # Validated against schema (1 pt)
    validated_against = identity.get("validated_against_schema", "")
    if validated_against:
        score += 1
    
    # Contract version (1 pt - base allocation)
    contract_version = identity.get("contract_version", "")
    if contract_version and "." in contract_version:
        score += 1
    
    # Source hash bonus (3 pts bonus, but capped at 5 pts total)
    source_hash = traceability.get("source_hash", "")
    if source_hash and not source_hash.startswith("TODO"):
        # Add bonus but ensure total doesn't exceed 5
        score = min(score + 3, 5)
    else:
        issues.append("C3: source_hash is placeholder - breaks provenance chain")
    
    return min(score, 5), issues


# ============================================================================
# DECISION ENGINE
# ============================================================================


def make_triage_decision(
    tier1_score: int,
    tier2_score: int,
    tier3_score: int,
    all_issues: List[str]
) -> Dict[str, Any]:
    """
    Decision matrix for contract triage
    
    Args:
        tier1_score: Tier 1 score (0-55)
        tier2_score: Tier 2 score (0-30)
        tier3_score: Tier 3 score (0-15)
        all_issues: Combined list of all issues
        
    Returns:
        Decision dict with status, rationale, and recommendations
    """
    total_score = tier1_score + tier2_score + tier3_score
    
    # Count blocker-level issues (those starting with "CRITICAL" or from Tier 1)
    blockers = [i for i in all_issues if "CRITICAL" in i or i.startswith("A1:") or i.startswith("A2:")]
    blocker_count = len(blockers)
    
    # Decision thresholds - INCREASED SEVERITY for production safety
    # These stricter thresholds reduce error probability in implementation
    TIER1_THRESHOLD = 40  # Raised from 35: Require stronger critical components
    TIER1_PRODUCTION_THRESHOLD = 50  # Raised from 45: Demand near-perfect Tier 1
    TIER2_MINIMUM = 20  # NEW: Require minimum functional component quality
    TIER3_MINIMUM = 8  # NEW: Require minimum quality standards
    TOTAL_PRODUCTION_THRESHOLD = 85  # Raised from 80: Higher overall bar
    
    decision = {}
    
    # REFORMULAR: Critical component failures
    if tier1_score < TIER1_THRESHOLD:
        decision["status"] = "REFORMULAR"
        decision["rationale"] = (
            f"Contract requires reformulation: Tier 1 score ({tier1_score}/55) "
            f"below minimum threshold ({TIER1_THRESHOLD}). "
            f"Total: {total_score}/100. Blockers: {blocker_count}."
        )
        decision["remediation"] = [
            "Regenerate contract from monolith questionnaire",
            "Fix identity-schema coherence issues",
            "Validate method-assembly alignment",
            "Re-run CQVR evaluation"
        ]
    
    # REFORMULAR: Insufficient tier 2 or tier 3 (NEW SEVERITY CHECK)
    elif tier2_score < TIER2_MINIMUM or tier3_score < TIER3_MINIMUM:
        decision["status"] = "REFORMULAR"
        decision["rationale"] = (
            f"Contract requires reformulation: Tier 2 ({tier2_score}/30) or "
            f"Tier 3 ({tier3_score}/15) below minimum thresholds "
            f"(Tier2≥{TIER2_MINIMUM}, Tier3≥{TIER3_MINIMUM}). "
            f"Total: {total_score}/100."
        )
        decision["remediation"] = [
            "Enhance pattern coverage and validation rules" if tier2_score < TIER2_MINIMUM else "Improve documentation and metadata",
            "Address quality components systematically",
            "Re-run CQVR evaluation"
        ]
    
    # PRODUCCION: Meets all strict thresholds
    elif (tier1_score >= TIER1_PRODUCTION_THRESHOLD and 
          tier2_score >= TIER2_MINIMUM and
          tier3_score >= TIER3_MINIMUM and
          total_score >= TOTAL_PRODUCTION_THRESHOLD and
          blocker_count == 0):  # NEW: Zero blockers required for production
        decision["status"] = "PRODUCCION"
        decision["rationale"] = (
            f"Contract approved for production: Tier 1: {tier1_score}/55, "
            f"Tier 2: {tier2_score}/30, Tier 3: {tier3_score}/15, "
            f"Total: {total_score}/100. Blockers: {blocker_count}."
        )
        decision["remediation"] = [
            "Final quality review",
            "Integration testing",
            "Deploy to production"
        ]
    
    # PARCHEAR: Good scores but minor issues (STRICTER: only 1 blocker allowed)
    elif blocker_count <= 1 and tier1_score >= 45 and total_score >= 75:
        decision["status"] = "PARCHEAR"
        blocker_text = f"Resolve the {blocker_count} identified blocker" if blocker_count == 1 else "Address warnings"
        decision["rationale"] = (
            f"Contract can be patched: Tier 1: {tier1_score}/55, "
            f"Total: {total_score}/100. Blockers: {blocker_count} (resolvable)."
        )
        decision["remediation"] = [
            blocker_text,
            "Apply recommended corrections",
            "Re-run CQVR evaluation"
        ]
    
    # REFORMULAR: Default case
    else:
        decision["status"] = "REFORMULAR"
        decision["rationale"] = (
            f"Contract requires reformulation: Tier 1: {tier1_score}/55, "
            f"Total: {total_score}/100. Blockers: {blocker_count}. "
            "Failed decision criteria."
        )
        decision["remediation"] = [
            "Analyze critical blockers",
            "Consider regeneration from monolith",
            "Fix tier 1 component issues",
            "Re-run CQVR post-reformulation"
        ]
    
    decision["blockers"] = blockers
    decision["warnings"] = [i for i in all_issues if i not in blockers]
    
    return decision


# ============================================================================
# EVALUATION ORCHESTRATOR
# ============================================================================


def evaluate_contract(contract: Dict[str, Any]) -> Dict[str, Any]:
    """
    Full CQVR evaluation of a single contract
    
    Args:
        contract: Executor contract dict
        
    Returns:
        Evaluation report dict with scores, issues, and decision
    """
    # Tier 1 evaluation
    a1_score, a1_issues = verify_identity_schema_coherence(contract)
    a2_score, a2_issues = verify_method_assembly_alignment(contract)
    a3_score, a3_issues = verify_signal_requirements(contract)
    a4_score, a4_issues = verify_output_schema(contract)
    
    tier1_score = a1_score + a2_score + a3_score + a4_score
    tier1_issues = a1_issues + a2_issues + a3_issues + a4_issues
    
    # Tier 2 evaluation
    b1_score, b1_issues = verify_pattern_coverage(contract)
    b2_score, b2_issues = verify_method_specificity(contract)
    b3_score, b3_issues = verify_validation_rules(contract)
    
    tier2_score = b1_score + b2_score + b3_score
    tier2_issues = b1_issues + b2_issues + b3_issues
    
    # Tier 3 evaluation
    c1_score, c1_issues = verify_documentation_quality(contract)
    c2_score, c2_issues = verify_human_template(contract)
    c3_score, c3_issues = verify_metadata_completeness(contract)
    
    tier3_score = c1_score + c2_score + c3_score
    tier3_issues = c1_issues + c2_issues + c3_issues
    
    # Total
    total_score = tier1_score + tier2_score + tier3_score
    all_issues = tier1_issues + tier2_issues + tier3_issues
    
    # Decision
    decision = make_triage_decision(tier1_score, tier2_score, tier3_score, all_issues)
    
    # Build report
    report = {
        "contract_id": contract.get("identity", {}).get("question_id", "UNKNOWN"),
        "evaluation_timestamp": datetime.now().isoformat(),
        "cqvr_version": "2.0",
        "scores": {
            "tier1": {
                "score": tier1_score,
                "max": 55,
                "percentage": round((tier1_score / 55) * 100, 1),
                "components": {
                    "A1_identity_schema": a1_score,
                    "A2_method_assembly": a2_score,
                    "A3_signal_requirements": a3_score,
                    "A4_output_schema": a4_score
                }
            },
            "tier2": {
                "score": tier2_score,
                "max": 30,
                "percentage": round((tier2_score / 30) * 100, 1),
                "components": {
                    "B1_pattern_coverage": b1_score,
                    "B2_method_specificity": b2_score,
                    "B3_validation_rules": b3_score
                }
            },
            "tier3": {
                "score": tier3_score,
                "max": 15,
                "percentage": round((tier3_score / 15) * 100, 1),
                "components": {
                    "C1_documentation_quality": c1_score,
                    "C2_human_template": c2_score,
                    "C3_metadata_completeness": c3_score
                }
            },
            "total": {
                "score": total_score,
                "max": 100,
                "percentage": round((total_score / 100) * 100, 1)
            }
        },
        "decision": decision,
        "issues": {
            "tier1": tier1_issues,
            "tier2": tier2_issues,
            "tier3": tier3_issues,
            "all": all_issues
        }
    }
    
    return report


# ============================================================================
# REPORT GENERATION
# ============================================================================


def generate_json_report(evaluations: List[Dict[str, Any]], output_path: Path) -> None:
    """Generate machine-readable JSON report"""
    summary = {
        "evaluation_timestamp": datetime.now().isoformat(),
        "cqvr_version": "2.0",
        "total_contracts": len(evaluations),
        "statistics": {
            "avg_score": sum(e["scores"]["total"]["score"] for e in evaluations) / len(evaluations) if evaluations else 0,
            "production_ready": sum(1 for e in evaluations if e["decision"]["status"] == "PRODUCCION"),
            "need_patches": sum(1 for e in evaluations if e["decision"]["status"] == "PARCHEAR"),
            "need_reformulation": sum(1 for e in evaluations if e["decision"]["status"] == "REFORMULAR")
        },
        "evaluations": evaluations
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)


def generate_console_summary(evaluations: List[Dict[str, Any]]) -> None:
    """Generate human-readable console output"""
    try:
        from rich.console import Console
        from rich.table import Table
        
        console = Console()
        
        console.print("\n[bold cyan]═" * 40)
        console.print("[bold cyan]CQVR EVALUATION SUMMARY")
        console.print("[bold cyan]═" * 40 + "\n")
        
        # Statistics
        total = len(evaluations)
        production = sum(1 for e in evaluations if e["decision"]["status"] == "PRODUCCION")
        patches = sum(1 for e in evaluations if e["decision"]["status"] == "PARCHEAR")
        reformulation = sum(1 for e in evaluations if e["decision"]["status"] == "REFORMULAR")
        avg_score = sum(e["scores"]["total"]["score"] for e in evaluations) / total if total > 0 else 0
        
        console.print(f"[bold]Total Contracts:[/bold] {total}")
        console.print(f"[bold]Average Score:[/bold] {avg_score:.1f}/100")
        console.print(f"[green]✓ Production Ready:[/green] {production}")
        console.print(f"[yellow]⚠ Need Patches:[/yellow] {patches}")
        console.print(f"[red]✗ Need Reformulation:[/red] {reformulation}\n")
        
        # Table
        table = Table(title="Contract Evaluation Results")
        table.add_column("Contract", style="cyan", no_wrap=True)
        table.add_column("Tier 1", justify="right")
        table.add_column("Tier 2", justify="right")
        table.add_column("Tier 3", justify="right")
        table.add_column("Total", justify="right")
        table.add_column("Decision", justify="center")
        
        for eval_data in evaluations:
            contract_id = eval_data["contract_id"]
            t1 = eval_data["scores"]["tier1"]["score"]
            t2 = eval_data["scores"]["tier2"]["score"]
            t3 = eval_data["scores"]["tier3"]["score"]
            total_score = eval_data["scores"]["total"]["score"]
            decision = eval_data["decision"]["status"]
            
            decision_icon = "✓" if decision == "PRODUCCION" else "⚠" if decision == "PARCHEAR" else "✗"
            decision_style = "green" if decision == "PRODUCCION" else "yellow" if decision == "PARCHEAR" else "red"
            
            table.add_row(
                contract_id,
                f"{t1}/55",
                f"{t2}/30",
                f"{t3}/15",
                f"{total_score}/100",
                f"[{decision_style}]{decision_icon} {decision}[/{decision_style}]"
            )
        
        console.print(table)
        console.print()
        
    except ImportError:
        # Fallback to basic output if Rich not available
        print("\n" + "=" * 80)
        print("CQVR EVALUATION SUMMARY")
        print("=" * 80 + "\n")
        
        total = len(evaluations)
        production = sum(1 for e in evaluations if e["decision"]["status"] == "PRODUCCION")
        patches = sum(1 for e in evaluations if e["decision"]["status"] == "PARCHEAR")
        reformulation = sum(1 for e in evaluations if e["decision"]["status"] == "REFORMULAR")
        avg_score = sum(e["scores"]["total"]["score"] for e in evaluations) / total if total > 0 else 0
        
        print(f"Total Contracts: {total}")
        print(f"Average Score: {avg_score:.1f}/100")
        print(f"✓ Production Ready: {production}")
        print(f"⚠ Need Patches: {patches}")
        print(f"✗ Need Reformulation: {reformulation}\n")
        
        for eval_data in evaluations:
            contract_id = eval_data["contract_id"]
            total_score = eval_data["scores"]["total"]["score"]
            decision = eval_data["decision"]["status"]
            print(f"{contract_id}: {total_score}/100 - {decision}")
        
        print()


# ============================================================================
# CLI INTERFACE
# ============================================================================


def main() -> int:
    """Main entry point for CQVR evaluator script"""
    parser = argparse.ArgumentParser(
        description="CQVR Evaluator - Contract Quality Validation and Remediation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate single contract
  python cqvr_evaluator_standalone.py --contract Q001.v3.json
  
  # Evaluate batch of 25 contracts (Q001-Q025)
  python cqvr_evaluator_standalone.py --batch 1
  
  # Evaluate all 300 contracts
  python cqvr_evaluator_standalone.py --all
  
  # Evaluate specific range
  python cqvr_evaluator_standalone.py --range 1 30
        """
    )
    
    parser.add_argument(
        "--contract",
        type=str,
        help="Evaluate single contract by filename (e.g., Q001.v3.json)"
    )
    parser.add_argument(
        "--batch",
        type=int,
        help="Evaluate batch number (1-12, each batch = 25 contracts)"
    )
    parser.add_argument(
        "--range",
        type=int,
        nargs=2,
        metavar=("START", "END"),
        help="Evaluate range of questions (e.g., --range 1 30)"
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
        help="Directory containing contract JSON files"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/cqvr_evaluation"),
        help="Output directory for reports"
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        help="Output JSON file path (default: output_dir/cqvr_evaluation.json)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress console output (only generate JSON)"
    )
    
    args = parser.parse_args()
    
    # Determine which contracts to evaluate
    contract_files = []
    
    if args.contract:
        contract_files = [args.contract]
    elif args.batch:
        start = (args.batch - 1) * 25 + 1
        end = args.batch * 25
        contract_files = [f"Q{i:03d}.v3.json" for i in range(start, end + 1)]
    elif args.range:
        start, end = args.range
        contract_files = [f"Q{i:03d}.v3.json" for i in range(start, end + 1)]
    elif args.all:
        contract_files = [f"Q{i:03d}.v3.json" for i in range(1, 301)]
    else:
        parser.error("Must specify --contract, --batch, --range, or --all")
    
    # Make paths absolute
    base_dir = Path(__file__).parent.parent
    contracts_dir = base_dir / args.contracts_dir
    output_dir = base_dir / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Evaluate contracts
    evaluations = []
    errors = []
    
    if not args.quiet:
        print(f"\n{'='*80}")
        print(f"CQVR Evaluator v2.0")
        print(f"{'='*80}")
        print(f"Evaluating {len(contract_files)} contract(s)...")
        print(f"Input: {contracts_dir}")
        print(f"Output: {output_dir}")
        print(f"{'='*80}\n")
    
    for contract_file in contract_files:
        contract_path = contracts_dir / contract_file
        
        if not contract_path.exists():
            errors.append(f"Contract not found: {contract_file}")
            continue
        
        try:
            with open(contract_path, "r", encoding="utf-8") as f:
                contract = json.load(f)
            
            evaluation = evaluate_contract(contract)
            evaluations.append(evaluation)
            
            if not args.quiet:
                score = evaluation["scores"]["total"]["score"]
                decision = evaluation["decision"]["status"]
                icon = "✓" if decision == "PRODUCCION" else "⚠" if decision == "PARCHEAR" else "✗"
                print(f"{icon} {contract_file}: {score}/100 - {decision}")
        
        except json.JSONDecodeError as e:
            errors.append(f"Malformed JSON in {contract_file}: {e}")
        except Exception as e:
            errors.append(f"Error evaluating {contract_file}: {e}")
    
    # Generate reports
    if evaluations:
        output_json = args.output_json or (output_dir / "cqvr_evaluation.json")
        generate_json_report(evaluations, output_json)
        
        if not args.quiet:
            print(f"\n{'='*80}\n")
            generate_console_summary(evaluations)
            print(f"JSON report: {output_json}")
    
    # Report errors
    if errors:
        print(f"\n{'='*80}")
        print("ERRORS:")
        print(f"{'='*80}")
        for error in errors:
            print(f"✗ {error}")
        print()
        return 1
    
    if not args.quiet:
        print(f"{'='*80}")
        print("✓ Evaluation complete!")
        print(f"{'='*80}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

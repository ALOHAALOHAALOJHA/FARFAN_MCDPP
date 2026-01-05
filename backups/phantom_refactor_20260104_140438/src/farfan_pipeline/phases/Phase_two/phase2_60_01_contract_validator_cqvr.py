"""Contract Validator using CQVR (Calibration, Quality, Validation, Reliability) framework.

PHASE_LABEL: Phase 2
PHASE_COMPONENT: CQVR Validator
PHASE_ROLE: Validates executor contracts using multi-tier quality scoring

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TriageDecision(Enum):
    PRODUCCION = "PRODUCCION"
    REFORMULAR = "REFORMULAR"
    PARCHEAR = "PARCHEAR"


@dataclass
class CQVRScore:
    tier1_score: float
    tier2_score: float
    tier3_score: float
    total_score: float
    tier1_max: float = 55.0
    tier2_max: float = 30.0
    tier3_max: float = 15.0
    total_max: float = 100.0
    component_scores: dict[str, float] = field(default_factory=dict)
    component_details: dict[str, dict[str, Any]] = field(default_factory=dict)

    @property
    def tier1_percentage(self) -> float:
        return (self.tier1_score / self.tier1_max) * 100 if self.tier1_max > 0 else 0

    @property
    def tier2_percentage(self) -> float:
        return (self.tier2_score / self.tier2_max) * 100 if self.tier2_max > 0 else 0

    @property
    def tier3_percentage(self) -> float:
        return (self.tier3_score / self.tier3_max) * 100 if self.tier3_max > 0 else 0

    @property
    def total_percentage(self) -> float:
        return (self.total_score / self.total_max) * 100 if self.total_max > 0 else 0


@dataclass
class ContractTriageDecision:
    decision: TriageDecision
    score: CQVRScore
    blockers: list[str]
    warnings: list[str]
    recommendations: list[dict[str, Any]]
    rationale: str
    
    def is_production_ready(self) -> bool:
        return self.decision == TriageDecision.PRODUCCION
    
    def requires_reformulation(self) -> bool:
        return self.decision == TriageDecision.REFORMULAR
    
    def can_be_patched(self) -> bool:
        return self.decision == TriageDecision.PARCHEAR


class CQVRValidator:
    TIER1_THRESHOLD = 35.0
    TIER1_PRODUCTION_THRESHOLD = 45.0
    TOTAL_PRODUCTION_THRESHOLD = 80.0
    
    def __init__(self) -> None:
        self.blockers: list[str] = []
        self.warnings: list[str] = []
        self.recommendations: list[dict[str, Any]] = []
    
    def validate_contract(self, contract: dict[str, Any]) -> ContractTriageDecision:
        self.blockers = []
        self.warnings = []
        self.recommendations = []
        
        tier1_score = self._evaluate_tier1(contract)
        tier2_score = self._evaluate_tier2(contract)
        tier3_score = self._evaluate_tier3(contract)
        
        score = CQVRScore(
            tier1_score=tier1_score,
            tier2_score=tier2_score,
            tier3_score=tier3_score,
            total_score=tier1_score + tier2_score + tier3_score
        )
        
        decision = self._make_triage_decision(score)
        rationale = self._generate_rationale(decision, score)
        
        return ContractTriageDecision(
            decision=decision,
            score=score,
            blockers=self.blockers.copy(),
            warnings=self.warnings.copy(),
            recommendations=self.recommendations.copy(),
            rationale=rationale
        )
    
    def _evaluate_tier1(self, contract: dict[str, Any]) -> float:
        a1_score = self.verify_identity_schema_coherence(contract)
        a2_score = self.verify_method_assembly_alignment(contract)
        a3_score = self.verify_signal_requirements(contract)
        a4_score = self.verify_output_schema(contract)
        
        return a1_score + a2_score + a3_score + a4_score
    
    def _evaluate_tier2(self, contract: dict[str, Any]) -> float:
        b1_score = self.verify_pattern_coverage(contract)
        b2_score = self.verify_method_specificity(contract)
        b3_score = self.verify_validation_rules(contract)
        
        return b1_score + b2_score + b3_score
    
    def _evaluate_tier3(self, contract: dict[str, Any]) -> float:
        c1_score = self.verify_documentation_quality(contract)
        c2_score = self.verify_human_template(contract)
        c3_score = self.verify_metadata_completeness(contract)
        
        return c1_score + c2_score + c3_score
    
    def verify_identity_schema_coherence(self, contract: dict[str, Any]) -> float:
        identity = contract.get("identity", {})
        output_schema = contract.get("output_contract", {}).get("schema", {})
        properties = output_schema.get("properties", {})
        
        score = 0.0
        max_score = 20.0
        
        fields_to_check = {
            "question_id": 5.0,
            "policy_area_id": 5.0,
            "dimension_id": 5.0,
            "question_global": 3.0,
            "base_slot": 2.0
        }
        
        for field, points in fields_to_check.items():
            identity_value = identity.get(field)
            schema_prop = properties.get(field, {})
            schema_value = schema_prop.get("const")
            
            if identity_value is not None and schema_value is not None:
                if identity_value == schema_value:
                    score += points
                else:
                    self.blockers.append(
                        f"A1: Identity-Schema mismatch for '{field}': "
                        f"identity={identity_value}, schema={schema_value}"
                    )
            else:
                if identity_value is None:
                    self.blockers.append(f"A1: Missing '{field}' in identity")
                if schema_value is None:
                    self.warnings.append(f"A1: Missing const for '{field}' in output_schema")
        
        return score
    
    def verify_method_assembly_alignment(self, contract: dict[str, Any]) -> float:
        method_binding = contract.get("method_binding", {})
        methods = method_binding.get("methods", [])
        evidence_assembly = contract.get("evidence_assembly", {})
        assembly_rules = evidence_assembly.get("assembly_rules", [])
        
        score = 0.0
        max_score = 20.0
        
        if not methods:
            self.blockers.append("A2: No methods defined in method_binding")
            return 0.0
        
        provides_set = set()
        for method in methods:
            provides = method.get("provides", "")
            if provides:
                provides_set.add(provides)
        
        method_count_declared = method_binding.get("method_count", len(methods))
        if method_count_declared == len(methods):
            score += 3.0
        else:
            self.warnings.append(
                f"A2: method_count mismatch: "
                f"declared={method_count_declared}, actual={len(methods)}"
            )
        
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
            score += 10.0
        else:
            self.blockers.append(
                f"A2: Assembly sources not in provides: {orphan_sources[:5]}"
            )
        
        usage_ratio = len(sources_referenced) / len(provides_set) if provides_set else 0
        if usage_ratio >= 0.9:
            score += 5.0
        elif usage_ratio >= 0.7:
            score += 3.0
        elif usage_ratio >= 0.5:
            score += 1.0
        else:
            self.warnings.append(
                f"A2: Low method usage ratio: {usage_ratio:.1%} "
                f"({len(sources_referenced)}/{len(provides_set)})"
            )
        
        if not orphan_sources:
            score += 2.0
        
        return score
    
    def verify_signal_requirements(self, contract: dict[str, Any]) -> float:
        signal_requirements = contract.get("signal_requirements", {})
        
        score = 0.0
        max_score = 10.0
        
        mandatory_signals = signal_requirements.get("mandatory_signals", [])
        threshold = signal_requirements.get("minimum_signal_threshold", 0.0)
        aggregation = signal_requirements.get("signal_aggregation", "")
        
        if mandatory_signals and threshold <= 0:
            self.blockers.append(
                f"A3: CRITICAL - minimum_signal_threshold={threshold} "
                "but mandatory_signals defined. "
                "This allows zero-strength signals to pass validation."
            )
            return 0.0
        
        if mandatory_signals and threshold > 0:
            score += 5.0
        elif not mandatory_signals:
            score += 5.0
        
        if mandatory_signals and all(isinstance(s, str) for s in mandatory_signals):
            score += 3.0
        elif mandatory_signals:
            self.warnings.append("A3: Some mandatory_signals are not well-formed strings")
        
        if aggregation in ["weighted_mean", "minimum", "product", "harmonic_mean"]:
            score += 2.0
        elif aggregation:
            self.warnings.append(f"A3: Unknown signal_aggregation method: {aggregation}")
        
        return score
    
    def verify_output_schema(self, contract: dict[str, Any]) -> float:
        output_contract = contract.get("output_contract", {})
        schema = output_contract.get("schema", {})
        
        score = 0.0
        max_score = 5.0
        
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        
        if not required:
            self.warnings.append("A4: No required fields in output_schema")
            return 0.0
        
        all_defined = all(field in properties for field in required)
        if all_defined:
            score += 3.0
        else:
            missing = [f for f in required if f not in properties]
            self.blockers.append(f"A4: Required fields not in properties: {missing}")
        
        traceability = contract.get("traceability", {})
        source_hash = traceability.get("source_hash", "")
        if source_hash and not source_hash.startswith("TODO"):
            score += 2.0
        else:
            self.warnings.append("A4: source_hash is placeholder or missing")
            score += 1.0
        
        return score
    
    def verify_pattern_coverage(self, contract: dict[str, Any]) -> float:
        question_context = contract.get("question_context", {})
        patterns = question_context.get("patterns", [])
        expected_elements = question_context.get("expected_elements", [])
        
        score = 0.0
        max_score = 10.0
        
        if not expected_elements:
            self.warnings.append("B1: No expected_elements defined")
            return 0.0
        
        if not patterns:
            self.warnings.append("B1: No patterns defined")
            return 0.0
        
        required_elements = [e for e in expected_elements if e.get("required")]
        
        pattern_categories = set()
        for pattern in patterns:
            if isinstance(pattern, dict):
                category = pattern.get("category", "GENERAL")
                pattern_categories.add(category)
        
        coverage_score = min(len(patterns) / max(len(required_elements), 1) * 5.0, 5.0)
        score += coverage_score
        
        confidence_weights = [
            p.get("confidence_weight", 0) for p in patterns if isinstance(p, dict)
        ]
        if confidence_weights:
            valid_weights = all(0 <= w <= 1 for w in confidence_weights)
            if valid_weights:
                score += 3.0
            else:
                self.warnings.append("B1: Some confidence_weights out of [0,1] range")
        
        pattern_ids = [p.get("id", "") for p in patterns if isinstance(p, dict)]
        unique_ids = len(set(pattern_ids)) == len(pattern_ids)
        if unique_ids and all(pattern_ids):
            score += 2.0
        else:
            self.warnings.append("B1: Pattern IDs not unique or missing")
        
        return score
    
    def verify_method_specificity(self, contract: dict[str, Any]) -> float:
        methodological_depth = contract.get("methodological_depth", {})
        methods = methodological_depth.get("methods", [])
        
        score = 0.0
        max_score = 10.0
        
        if not methods:
            self.warnings.append("B2: No methodological_depth.methods defined")
            return 0.0
        
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
            assumptions = technical.get("assumptions", [])
            
            is_specific = True
            
            for step in steps:
                step_desc = step.get("description", "")
                if any(pattern in step_desc for pattern in generic_patterns):
                    is_specific = False
                    boilerplate_count += 1
                    break
            
            if is_specific and complexity and not any(p in complexity for p in generic_patterns):
                specific_count += 1
        
        if methods:
            specificity_ratio = specific_count / len(methods)
            score += specificity_ratio * 6.0
        
        complexity_count = sum(
            1 for m in methods
            if m.get("technical_approach", {}).get("complexity")
            and "input size" not in m.get("technical_approach", {}).get("complexity", "")
        )
        if methods:
            score += (complexity_count / len(methods)) * 2.0
        
        assumptions_count = sum(
            1 for m in methods
            if m.get("technical_approach", {}).get("assumptions")
            and not any(
                "preprocessed" in str(a).lower()
                for a in m.get("technical_approach", {}).get("assumptions", [])
            )
        )
        if methods:
            score += (assumptions_count / len(methods)) * 2.0
        
        if boilerplate_count > len(methods) * 0.5:
            self.warnings.append(
                f"B2: High boilerplate ratio: {boilerplate_count}/{len(methods)} methods"
            )
        
        return score
    
    def verify_validation_rules(self, contract: dict[str, Any]) -> float:
        validation_rules = contract.get("validation_rules", {})
        rules = validation_rules.get("rules", [])
        question_context = contract.get("question_context", {})
        expected_elements = question_context.get("expected_elements", [])
        
        score = 0.0
        max_score = 10.0
        
        if not rules:
            self.blockers.append("B3: No validation_rules.rules defined")
            return 0.0
        
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
        
        if required_elements and required_elements.issubset(all_validation_elements):
            score += 5.0
        elif required_elements:
            missing = required_elements - all_validation_elements
            self.warnings.append(
                f"B3: Required elements not in validation rules: {missing}"
            )
        
        if must_contain_elements and should_contain_elements:
            score += 3.0
        elif must_contain_elements or should_contain_elements:
            score += 1.0
        
        error_handling = contract.get("error_handling", {})
        failure_contract = error_handling.get("failure_contract", {})
        if failure_contract.get("emit_code"):
            score += 2.0
        else:
            self.warnings.append("B3: No emit_code in failure_contract")
        
        return score
    
    def verify_documentation_quality(self, contract: dict[str, Any]) -> float:
        methodological_depth = contract.get("methodological_depth", {})
        methods = methodological_depth.get("methods", [])
        
        score = 0.0
        max_score = 5.0
        
        if not methods:
            self.warnings.append("C1: No methodological_depth for documentation check")
            return 0.0
        
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
            framework = epist.get("theoretical_framework", [])
            
            is_specific = True
            for pattern in boilerplate_patterns:
                if pattern.lower() in paradigm.lower() or pattern.lower() in justification.lower():
                    is_specific = False
                    break
            
            if is_specific:
                specific_paradigms += 1
        
        if methods:
            paradigm_ratio = specific_paradigms / len(methods)
            score += paradigm_ratio * 2.0
        
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
            score += (justifications_with_why / len(methods)) * 2.0
        
        has_references = any(
            m.get("epistemological_foundation", {}).get("theoretical_framework")
            for m in methods
        )
        if has_references:
            score += 1.0
        
        return score
    
    def verify_human_template(self, contract: dict[str, Any]) -> float:
        output_contract = contract.get("output_contract", {})
        human_readable = output_contract.get("human_readable_output", {})
        template = human_readable.get("template", {})
        
        score = 0.0
        max_score = 5.0
        
        identity = contract.get("identity", {})
        base_slot = identity.get("base_slot", "")
        question_id = identity.get("question_id", "")
        
        title = template.get("title", "")
        summary = template.get("summary", "")
        
        has_references = False
        if base_slot and base_slot in title:
            has_references = True
        if question_id and question_id in title:
            has_references = True
        
        if has_references:
            score += 3.0
        else:
            self.warnings.append("C2: Template title does not reference base_slot or question_id")
        
        placeholder_patterns = [
            r"\{.*?\}"
        ]
        
        has_placeholders = False
        for pattern in placeholder_patterns:
            if re.search(pattern, summary):
                has_placeholders = True
                break
        
        if has_placeholders:
            score += 2.0
        else:
            self.warnings.append("C2: Template summary has no dynamic placeholders")
        
        return score
    
    def verify_metadata_completeness(self, contract: dict[str, Any]) -> float:
        identity = contract.get("identity", {})
        traceability = contract.get("traceability", {})
        
        score = 0.0
        max_score = 5.0
        
        contract_hash = identity.get("contract_hash", "")
        if contract_hash and len(contract_hash) == 64:
            score += 2.0
        else:
            self.warnings.append("C3: contract_hash missing or invalid")
        
        created_at = identity.get("created_at", "")
        if created_at and "T" in created_at:
            score += 1.0
        else:
            self.warnings.append("C3: created_at missing or invalid ISO 8601 format")
        
        validated_against = identity.get("validated_against_schema", "")
        if validated_against:
            score += 1.0
        
        contract_version = identity.get("contract_version", "")
        if contract_version and "." in contract_version:
            score += 1.0
        
        source_hash = traceability.get("source_hash", "")
        if source_hash and not source_hash.startswith("TODO"):
            score += 3.0
        else:
            self.warnings.append("C3: source_hash is placeholder - breaks provenance chain")
            self.recommendations.append({
                "component": "C3",
                "priority": "HIGH",
                "issue": "Missing source_hash",
                "fix": (
                    "Calculate SHA256 of questionnaire_monolith.json "
                    "and update traceability.source_hash"
                ),
                "impact": "+3 pts"
            })
        
        return min(score, max_score)
    
    def _make_triage_decision(self, score: CQVRScore) -> TriageDecision:
        if score.tier1_score < self.TIER1_THRESHOLD:
            return TriageDecision.REFORMULAR
        
        if (score.tier1_score >= self.TIER1_PRODUCTION_THRESHOLD and 
            score.total_score >= self.TOTAL_PRODUCTION_THRESHOLD):
            return TriageDecision.PRODUCCION
        
        if len(self.blockers) == 0 and score.total_score >= 70:
            return TriageDecision.PARCHEAR
        
        if len(self.blockers) <= 2 and score.tier1_score >= 40:
            return TriageDecision.PARCHEAR
        
        return TriageDecision.REFORMULAR
    
    def _generate_rationale(self, decision: TriageDecision, score: CQVRScore) -> str:
        if decision == TriageDecision.PRODUCCION:
            return (
                f"Contract approved for production: "
                f"Tier 1: {score.tier1_score:.1f}/{score.tier1_max} "
                f"({score.tier1_percentage:.1f}%), "
                f"Total: {score.total_score:.1f}/{score.total_max} "
                f"({score.total_percentage:.1f}%). "
                f"Blockers: {len(self.blockers)}, Warnings: {len(self.warnings)}."
            )
        elif decision == TriageDecision.PARCHEAR:
            return (
                f"Contract can be patched: "
                f"Tier 1: {score.tier1_score:.1f}/{score.tier1_max} "
                f"({score.tier1_percentage:.1f}%), "
                f"Total: {score.total_score:.1f}/{score.total_max} "
                f"({score.total_percentage:.1f}%). "
                f"Blockers: {len(self.blockers)} (resolvable), "
                f"Warnings: {len(self.warnings)}. "
                f"Apply recommended patches to reach production threshold."
            )
        else:
            reason_parts = []
            if score.tier1_score < self.TIER1_THRESHOLD:
                reason_parts.append(f"Tier 1 score below minimum threshold ({self.TIER1_THRESHOLD})")
            elif score.tier1_score < self.TIER1_PRODUCTION_THRESHOLD:
                reason_parts.append(f"Tier 1 score below production threshold ({self.TIER1_PRODUCTION_THRESHOLD})")
            if score.total_score < self.TOTAL_PRODUCTION_THRESHOLD:
                reason_parts.append(f"Total score below production threshold ({self.TOTAL_PRODUCTION_THRESHOLD})")
            if len(self.blockers) > 0:
                reason_parts.append(f"{len(self.blockers)} critical blocker(s)")
            
            reason_str = "; ".join(reason_parts) if reason_parts else "Failed decision criteria"
            
            return (
                f"Contract requires reformulation: "
                f"Tier 1: {score.tier1_score:.1f}/{score.tier1_max} "
                f"({score.tier1_percentage:.1f}%), "
                f"Total: {score.total_score:.1f}/{score.total_max} "
                f"({score.total_percentage:.1f}%). "
                f"Reasons: {reason_str}. "
                f"Contract needs substantial rework."
            )

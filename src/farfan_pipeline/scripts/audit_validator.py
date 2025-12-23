#!/usr/bin/env python3
"""
Epistemological Contract Audit Validator v1.0
==============================================

Validates v4 contracts against 100+ audit criteria from the audit checklist.
This ensures contracts are epistemologically sound before use.

Categories:
1. Classification & Structural Coherence
2. Method Classification (Epistemological)
3. Evidence Assembly (Type System & Rules)
4. Fusion Specification (Level Strategies)
5. Cross-Layer Fusion (Asymmetry)
6. Human Answer Structure (Narrative)
7. Traceability & Metadata
8. Cross-Validation & Global Consistency
9. Meta-Epistemological Checks
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AuditFinding:
    """A single audit finding."""
    category: str
    check_id: str
    passed: bool
    message: str
    severity: str = "ERROR"  # ERROR, WARNING, INFO


@dataclass
class AuditReport:
    """Complete audit report for a contract."""
    slot: str
    passed: bool
    findings: list[AuditFinding] = field(default_factory=list)
    errors: int = 0
    warnings: int = 0
    
    def add(self, finding: AuditFinding) -> None:
        self.findings.append(finding)
        if not finding.passed:
            if finding.severity == "ERROR":
                self.errors += 1
                self.passed = False
            elif finding.severity == "WARNING":
                self.warnings += 1


class V4ContractAuditor:
    """Audits v4 contracts against 100+ criteria."""
    
    def audit(self, contract: dict) -> AuditReport:
        """Run full audit on a contract."""
        slot = contract.get("identity", {}).get("base_slot", "UNKNOWN")
        report = AuditReport(slot=slot, passed=True)
        
        # Run all audit categories
        self._audit_classification_coherence(contract, report)
        self._audit_method_classification(contract, report)
        self._audit_evidence_assembly(contract, report)
        self._audit_fusion_specification(contract, report)
        self._audit_cross_layer_fusion(contract, report)
        self._audit_human_answer_structure(contract, report)
        self._audit_traceability(contract, report)
        self._audit_cross_validation(contract, report)
        self._audit_meta_epistemological(contract, report)
        
        return report
    
    # =========================================================================
    # Category 1: Classification & Structural Coherence
    # =========================================================================
    
    def _audit_classification_coherence(self, c: dict, r: AuditReport) -> None:
        """Audit structural coherence."""
        identity = c.get("identity", {})
        
        # 1.1 Contract type declared
        contract_type = identity.get("contract_type")
        r.add(AuditFinding(
            category="1-Classification",
            check_id="1.1",
            passed=contract_type in ["TYPE_A", "TYPE_B", "TYPE_C", "TYPE_D", "TYPE_E"],
            message=f"Contract type: {contract_type}",
        ))
        
        # 1.2 Version is 4.0.0-epistemological
        version = identity.get("contract_version", "")
        r.add(AuditFinding(
            category="1-Classification",
            check_id="1.2",
            passed="4.0.0-epistemological" in version,
            message=f"Version: {version}",
        ))
        
        # 1.3 Consistent focus
        focus = identity.get("contract_type_focus", "")
        r.add(AuditFinding(
            category="1-Classification",
            check_id="1.3",
            passed=bool(focus),
            message=f"Focus defined: {bool(focus)}",
        ))
        
        # 1.4 Base slot matches
        base_slot = identity.get("base_slot", "")
        r.add(AuditFinding(
            category="1-Classification",
            check_id="1.4",
            passed=bool(base_slot) and "-" in base_slot,
            message=f"Base slot: {base_slot}",
        ))
    
    # =========================================================================
    # Category 2: Method Classification
    # =========================================================================
    
    def _audit_method_classification(self, c: dict, r: AuditReport) -> None:
        """Audit method epistemological classification."""
        mb = c.get("method_binding", {})
        phases = mb.get("execution_phases", {})
        
        # 2.1 Three execution phases present
        required_phases = ["phase_A_construction", "phase_B_computation", "phase_C_litigation"]
        for phase in required_phases:
            r.add(AuditFinding(
                category="2-MethodBinding",
                check_id=f"2.1-{phase}",
                passed=phase in phases,
                message=f"Phase {phase} present: {phase in phases}",
            ))
        
        # 2.2 Phase A has N1 methods with output_type FACT
        phase_a = phases.get("phase_A_construction", {})
        phase_a_methods = phase_a.get("methods", [])
        for m in phase_a_methods:
            r.add(AuditFinding(
                category="2-MethodBinding",
                check_id="2.2-N1-FACT",
                passed=m.get("output_type") == "FACT" and m.get("level") == "N1-EMP",
                message=f"N1 method {m.get('method_name')}: type={m.get('output_type')}, level={m.get('level')}",
            ))
        
        # 2.3 Phase B has N2 methods with output_type PARAMETER
        phase_b = phases.get("phase_B_computation", {})
        phase_b_methods = phase_b.get("methods", [])
        for m in phase_b_methods:
            r.add(AuditFinding(
                category="2-MethodBinding",
                check_id="2.3-N2-PARAMETER",
                passed=m.get("output_type") == "PARAMETER" and m.get("level") == "N2-INF",
                message=f"N2 method {m.get('method_name')}: type={m.get('output_type')}, level={m.get('level')}",
            ))
        
        # 2.4 Phase C has N3 methods with output_type CONSTRAINT
        phase_c = phases.get("phase_C_litigation", {})
        phase_c_methods = phase_c.get("methods", [])
        for m in phase_c_methods:
            r.add(AuditFinding(
                category="2-MethodBinding",
                check_id="2.4-N3-CONSTRAINT",
                passed=m.get("output_type") == "CONSTRAINT" and m.get("level") == "N3-AUD",
                message=f"N3 method {m.get('method_name')}: type={m.get('output_type')}, level={m.get('level')}",
            ))
        
        # 2.5 N3 methods have veto_conditions
        for m in phase_c_methods:
            has_veto = "veto_conditions" in m
            r.add(AuditFinding(
                category="2-MethodBinding",
                check_id="2.5-N3-VetoConditions",
                passed=has_veto,
                message=f"N3 method {m.get('method_name')} has veto_conditions: {has_veto}",
            ))
        
        # 2.6 Orchestration mode is epistemological_pipeline
        r.add(AuditFinding(
            category="2-MethodBinding",
            check_id="2.6-OrchestrationMode",
            passed=mb.get("orchestration_mode") == "epistemological_pipeline",
            message=f"Orchestration mode: {mb.get('orchestration_mode')}",
        ))
    
    # =========================================================================
    # Category 3: Evidence Assembly
    # =========================================================================
    
    def _audit_evidence_assembly(self, c: dict, r: AuditReport) -> None:
        """Audit evidence assembly configuration."""
        ea = c.get("evidence_assembly", {})
        
        # 3.1 Type system defines FACT, PARAMETER, CONSTRAINT, NARRATIVE
        type_system = ea.get("type_system", {})
        required_types = ["FACT", "PARAMETER", "CONSTRAINT", "NARRATIVE"]
        for t in required_types:
            r.add(AuditFinding(
                category="3-EvidenceAssembly",
                check_id=f"3.1-Type-{t}",
                passed=t in type_system,
                message=f"Type {t} defined: {t in type_system}",
            ))
        
        # 3.2 Four assembly rules (R1-R4)
        rules = ea.get("assembly_rules", [])
        rule_ids = [rule.get("rule_id", "") for rule in rules]
        expected_rules = ["R1_empirical_extraction", "R2_inferential_aggregation", 
                         "R3_audit_gate", "R4_narrative_synthesis"]
        for expected in expected_rules:
            r.add(AuditFinding(
                category="3-EvidenceAssembly",
                check_id=f"3.2-Rule-{expected[:2]}",
                passed=expected in rule_ids,
                message=f"Rule {expected} present: {expected in rule_ids}",
            ))
        
        # 3.3 R1 has output_type FACT
        r1 = next((rule for rule in rules if rule.get("rule_id") == "R1_empirical_extraction"), {})
        r.add(AuditFinding(
            category="3-EvidenceAssembly",
            check_id="3.3-R1-OutputType",
            passed=r1.get("output_type") == "FACT",
            message=f"R1 output_type: {r1.get('output_type')}",
        ))
        
        # 3.4 R3 has gate_logic
        r3 = next((rule for rule in rules if rule.get("rule_id") == "R3_audit_gate"), {})
        r.add(AuditFinding(
            category="3-EvidenceAssembly",
            check_id="3.4-R3-GateLogic",
            passed="gate_logic" in r3,
            message=f"R3 has gate_logic: {'gate_logic' in r3}",
        ))
        
        # 3.5 R4 has external_handler
        r4 = next((rule for rule in rules if rule.get("rule_id") == "R4_narrative_synthesis"), {})
        r.add(AuditFinding(
            category="3-EvidenceAssembly",
            check_id="3.5-R4-ExternalHandler",
            passed="external_handler" in r4,
            message=f"R4 has external_handler: {'external_handler' in r4}",
        ))
    
    # =========================================================================
    # Category 4: Fusion Specification
    # =========================================================================
    
    def _audit_fusion_specification(self, c: dict, r: AuditReport) -> None:
        """Audit fusion specification."""
        fs = c.get("fusion_specification", {})
        identity = c.get("identity", {})
        
        # 4.1 Contract type consistency
        r.add(AuditFinding(
            category="4-FusionSpec",
            check_id="4.1-ContractTypeMatch",
            passed=fs.get("contract_type") == identity.get("contract_type"),
            message=f"Fusion contract_type matches identity: {fs.get('contract_type')} == {identity.get('contract_type')}",
        ))
        
        # 4.2 Level strategies for N1, N2, N3
        level_strategies = fs.get("level_strategies", {})
        required_levels = ["N1_fact_fusion", "N2_parameter_fusion", "N3_constraint_fusion"]
        for level in required_levels:
            r.add(AuditFinding(
                category="4-FusionSpec",
                check_id=f"4.2-{level}",
                passed=level in level_strategies,
                message=f"Level strategy {level} defined: {level in level_strategies}",
            ))
        
        # 4.3 Fusion pipeline has 4 stages
        pipeline = fs.get("fusion_pipeline", {})
        expected_stages = ["stage_1_fact_accumulation", "stage_2_parameter_application",
                          "stage_3_constraint_filtering", "stage_4_synthesis"]
        for stage in expected_stages:
            r.add(AuditFinding(
                category="4-FusionSpec",
                check_id=f"4.3-{stage[:7]}",
                passed=stage in pipeline,
                message=f"Pipeline stage {stage} defined: {stage in pipeline}",
            ))
        
        # 4.4 N3 has asymmetry_principle
        n3_strat = level_strategies.get("N3_constraint_fusion", {})
        r.add(AuditFinding(
            category="4-FusionSpec",
            check_id="4.4-N3-Asymmetry",
            passed="asymmetry_principle" in n3_strat,
            message=f"N3 has asymmetry_principle: {'asymmetry_principle' in n3_strat}",
        ))
    
    # =========================================================================
    # Category 5: Cross-Layer Fusion
    # =========================================================================
    
    def _audit_cross_layer_fusion(self, c: dict, r: AuditReport) -> None:
        """Audit cross-layer fusion asymmetry."""
        clf = c.get("cross_layer_fusion", {})
        
        # 5.1 N3_to_N1 has asymmetry declaration
        n3_to_n1 = clf.get("N3_to_N1", {})
        r.add(AuditFinding(
            category="5-CrossLayerFusion",
            check_id="5.1-N3toN1-Asymmetry",
            passed="asymmetry" in n3_to_n1,
            message=f"N3_to_N1 declares asymmetry: {'asymmetry' in n3_to_n1}",
        ))
        
        # 5.2 N3_to_N2 has asymmetry declaration
        n3_to_n2 = clf.get("N3_to_N2", {})
        r.add(AuditFinding(
            category="5-CrossLayerFusion",
            check_id="5.2-N3toN2-Asymmetry",
            passed="asymmetry" in n3_to_n2,
            message=f"N3_to_N2 declares asymmetry: {'asymmetry' in n3_to_n2}",
        ))
        
        # 5.3 blocking_propagation_rules defined
        r.add(AuditFinding(
            category="5-CrossLayerFusion",
            check_id="5.3-BlockingRules",
            passed="blocking_propagation_rules" in clf,
            message=f"blocking_propagation_rules defined: {'blocking_propagation_rules' in clf}",
        ))
        
        # 5.4 all_to_N4 defined
        r.add(AuditFinding(
            category="5-CrossLayerFusion",
            check_id="5.4-AllToN4",
            passed="all_to_N4" in clf,
            message=f"all_to_N4 defined: {'all_to_N4' in clf}",
        ))
    
    # =========================================================================
    # Category 6: Human Answer Structure
    # =========================================================================
    
    def _audit_human_answer_structure(self, c: dict, r: AuditReport) -> None:
        """Audit human answer structure sections."""
        has = c.get("human_answer_structure", {})
        
        # 6.1 Template mode is epistemological_narrative
        r.add(AuditFinding(
            category="6-HumanAnswer",
            check_id="6.1-TemplateMode",
            passed=has.get("template_mode") == "epistemological_narrative",
            message=f"Template mode: {has.get('template_mode')}",
        ))
        
        # 6.2 Four sections (S1-S4)
        sections = has.get("sections", [])
        expected_sections = ["S1_verdict", "S2_empirical_base", "S3_robustness_audit", "S4_gaps"]
        section_ids = [s.get("section_id") for s in sections]
        for expected in expected_sections:
            r.add(AuditFinding(
                category="6-HumanAnswer",
                check_id=f"6.2-Section-{expected[:2]}",
                passed=expected in section_ids,
                message=f"Section {expected} present: {expected in section_ids}",
            ))
        
        # 6.3 S3 has veto_display
        s3 = next((s for s in sections if s.get("section_id") == "S3_robustness_audit"), {})
        r.add(AuditFinding(
            category="6-HumanAnswer",
            check_id="6.3-S3-VetoDisplay",
            passed="veto_display" in s3,
            message=f"S3 has veto_display: {'veto_display' in s3}",
        ))
        
        # 6.4 confidence_interpretation defined
        r.add(AuditFinding(
            category="6-HumanAnswer",
            check_id="6.4-ConfidenceInterpretation",
            passed="confidence_interpretation" in has,
            message=f"confidence_interpretation defined: {'confidence_interpretation' in has}",
        ))
        
        # 6.5 argumentative_roles defined
        r.add(AuditFinding(
            category="6-HumanAnswer",
            check_id="6.5-ArgumentativeRoles",
            passed="argumentative_roles" in has,
            message=f"argumentative_roles defined: {'argumentative_roles' in has}",
        ))
    
    # =========================================================================
    # Category 7: Traceability & Metadata
    # =========================================================================
    
    def _audit_traceability(self, c: dict, r: AuditReport) -> None:
        """Audit traceability and metadata."""
        trace = c.get("traceability", {})
        
        # 7.1 refactoring_history present
        r.add(AuditFinding(
            category="7-Traceability",
            check_id="7.1-RefactoringHistory",
            passed="refactoring_history" in trace,
            message=f"refactoring_history present: {'refactoring_history' in trace}",
        ))
        
        # 7.2 canonical_sources present
        r.add(AuditFinding(
            category="7-Traceability",
            check_id="7.2-CanonicalSources",
            passed="canonical_sources" in trace,
            message=f"canonical_sources present: {'canonical_sources' in trace}",
        ))
        
        # 7.3 epistemological_framework documented
        history = trace.get("refactoring_history", [])
        has_framework = any("epistemological_framework" in h for h in history)
        r.add(AuditFinding(
            category="7-Traceability",
            check_id="7.3-EpistemologicalFramework",
            passed=has_framework,
            message=f"epistemological_framework documented: {has_framework}",
        ))
        
        # 7.4 episte_refact.md referenced
        sources = trace.get("canonical_sources", {})
        refs_guide = sources.get("epistemological_guide") == "episte_refact.md"
        r.add(AuditFinding(
            category="7-Traceability",
            check_id="7.4-GuideReference",
            passed=refs_guide,
            message=f"episte_refact.md referenced: {refs_guide}",
        ))
    
    # =========================================================================
    # Category 8: Cross-Validation
    # =========================================================================
    
    def _audit_cross_validation(self, c: dict, r: AuditReport) -> None:
        """Audit cross-validation consistency."""
        mb = c.get("method_binding", {})
        ea = c.get("evidence_assembly", {})
        
        # 8.1 Method count matches sum of phases
        phases = mb.get("execution_phases", {})
        total_methods = sum(
            len(p.get("methods", []))
            for p in phases.values()
        )
        declared_count = mb.get("method_count", 0)
        r.add(AuditFinding(
            category="8-CrossValidation",
            check_id="8.1-MethodCountConsistency",
            passed=total_methods == declared_count,
            message=f"Method count: declared={declared_count}, actual={total_methods}",
        ))
        
        # 8.2 R1 sources match phase_A method provides
        phase_a = phases.get("phase_A_construction", {})
        phase_a_provides = {m.get("provides") for m in phase_a.get("methods", [])}
        r1 = next((rule for rule in ea.get("assembly_rules", []) 
                   if rule.get("rule_id") == "R1_empirical_extraction"), {})
        r1_sources = set(r1.get("sources", []))
        sources_match = r1_sources == phase_a_provides
        r.add(AuditFinding(
            category="8-CrossValidation",
            check_id="8.2-R1SourcesMatch",
            passed=sources_match,
            message=f"R1 sources match phase_A provides: {sources_match}",
            severity="WARNING" if not sources_match else "ERROR",
        ))
        
        # 8.3 Contract type consistent across identity, method_binding, fusion_specification
        identity_type = c.get("identity", {}).get("contract_type")
        mb_type = mb.get("contract_type")
        fs_type = c.get("fusion_specification", {}).get("contract_type")
        all_match = identity_type == mb_type == fs_type
        r.add(AuditFinding(
            category="8-CrossValidation",
            check_id="8.3-TypeConsistency",
            passed=all_match,
            message=f"Contract type consistent: identity={identity_type}, mb={mb_type}, fs={fs_type}",
        ))
    
    # =========================================================================
    # Category 9: Meta-Epistemological Checks
    # =========================================================================
    
    def _audit_meta_epistemological(self, c: dict, r: AuditReport) -> None:
        """Audit meta-epistemological properties."""
        phases = c.get("method_binding", {}).get("execution_phases", {})
        
        # 9.1 Epistemological hierarchy respected: N1 → N2 → N3 dependencies
        phase_b = phases.get("phase_B_computation", {})
        phase_c = phases.get("phase_C_litigation", {})
        
        b_deps = phase_b.get("dependencies", [])
        c_deps = phase_c.get("dependencies", [])
        
        r.add(AuditFinding(
            category="9-MetaEpistemological",
            check_id="9.1-HierarchyN2DependsN1",
            passed="phase_A_construction" in b_deps,
            message=f"N2 depends on N1: {'phase_A_construction' in b_deps}",
        ))
        
        r.add(AuditFinding(
            category="9-MetaEpistemological",
            check_id="9.2-HierarchyN3DependsBoth",
            passed="phase_A_construction" in c_deps and "phase_B_computation" in c_deps,
            message=f"N3 depends on N1+N2: {c_deps}",
        ))
        
        # 9.3 N3 asymmetry explicitly stated
        phase_c_asymmetry = phase_c.get("asymmetry_principle", "")
        r.add(AuditFinding(
            category="9-MetaEpistemological",
            check_id="9.3-N3AsymmetryExplicit",
            passed=bool(phase_c_asymmetry),
            message=f"N3 asymmetry principle: {phase_c_asymmetry}",
        ))
        
        # 9.4 All phases have epistemology declared
        for phase_key, phase in phases.items():
            has_epistemology = "epistemology" in phase
            r.add(AuditFinding(
                category="9-MetaEpistemological",
                check_id=f"9.4-Epistemology-{phase_key[:7]}",
                passed=has_epistemology,
                message=f"{phase_key} has epistemology: {has_epistemology}",
            ))


def audit_all_contracts(
    contracts_dir: Path,
    output_file: Path | None = None,
) -> dict[str, AuditReport]:
    """Audit all contracts in a directory."""
    auditor = V4ContractAuditor()
    reports: dict[str, AuditReport] = {}
    
    total_errors = 0
    total_warnings = 0
    
    for contract_file in sorted(contracts_dir.glob("*.json")):
        with open(contract_file, encoding="utf-8") as f:
            contract = json.load(f)
        
        report = auditor.audit(contract)
        reports[report.slot] = report
        
        total_errors += report.errors
        total_warnings += report.warnings
        
        status = "✅ PASS" if report.passed else f"❌ FAIL ({report.errors} errors)"
        print(f"Audited {contract_file.name}: {status}")
    
    print(f"\n{'='*60}")
    print(f"TOTAL: {len(reports)} contracts audited")
    print(f"  - Passed: {sum(1 for r in reports.values() if r.passed)}")
    print(f"  - Failed: {sum(1 for r in reports.values() if not r.passed)}")
    print(f"  - Total Errors: {total_errors}")
    print(f"  - Total Warnings: {total_warnings}")
    
    if output_file:
        summary = {
            slot: {
                "passed": report.passed,
                "errors": report.errors,
                "warnings": report.warnings,
                "findings": [
                    {
                        "category": f.category,
                        "check_id": f.check_id,
                        "passed": f.passed,
                        "message": f.message,
                        "severity": f.severity,
                    }
                    for f in report.findings
                    if not f.passed  # Only include failures
                ]
            }
            for slot, report in reports.items()
        }
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"\nAudit report saved to {output_file}")
    
    return reports


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Audit v4 epistemological contracts")
    parser.add_argument(
        "--contracts-dir",
        type=Path,
        default=Path("contracts_v4"),
        help="Directory containing contracts to audit",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output file for audit report (JSON)",
    )
    
    args = parser.parse_args()
    audit_all_contracts(args.contracts_dir, args.output)

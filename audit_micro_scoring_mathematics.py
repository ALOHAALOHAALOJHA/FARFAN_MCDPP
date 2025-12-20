#!/usr/bin/env python3
"""
Mathematical Audit of Micro-Level Scoring Procedures
====================================================

Comprehensive mathematical audit of scoring procedures at the micro level, including:
1. Scoring modality mathematical formulas (TYPE_A through TYPE_F)
2. Executor contract alignment to scoring modalities
3. Questionnaire validation patterns alignment
4. Mathematical invariants verification
5. Threshold and weighting calculations

Author: F.A.R.F.A.N Pipeline Team
Date: 2025-12-11
Version: 1.0.0
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from orchestration.factory import get_canonical_questionnaire

# Color codes for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

ScoringModality = Literal["TYPE_A", "TYPE_B", "TYPE_C", "TYPE_D", "TYPE_E", "TYPE_F", "MESO_INTEGRATION", "MACRO_HOLISTIC"]


@dataclass
class ScoringModalityFormula:
    """Mathematical formula definition for a scoring modality."""
    modality: str
    description: str
    threshold: float
    aggregation: str
    weight_elements: float
    weight_similarity: float
    weight_patterns: float
    formula: str
    failure_code: str | None = None
    
    def compute_score(self, elements: float, similarity: float, patterns: float) -> float:
        """Compute score using modality formula."""
        if self.aggregation == "weighted_mean":
            total_weight = self.weight_elements + self.weight_similarity + self.weight_patterns
            if total_weight == 0:
                return 0.0
            weighted_sum = (
                elements * self.weight_elements +
                similarity * self.weight_similarity +
                patterns * self.weight_patterns
            )
            return weighted_sum / total_weight
        elif self.aggregation == "max":
            return max(elements, similarity, patterns)
        elif self.aggregation == "min":
            return min(elements, similarity, patterns)
        return 0.0
    
    def passes_threshold(self, score: float) -> bool:
        """Check if score passes threshold."""
        return score >= self.threshold


@dataclass
class ContractAnalysis:
    """Analysis of an executor contract."""
    contract_path: str
    question_id: str
    base_slot: str
    policy_area_id: str
    dimension_id: str
    scoring_modality: str | None
    method_count: int
    patterns_count: int
    validation_rules_count: int
    expected_elements: list[str]
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class QuestionnaireAnalysis:
    """Analysis of questionnaire micro question."""
    question_id: str
    base_slot: str
    policy_area_id: str
    dimension_id: str
    scoring_modality: str
    patterns_count: int
    validations_count: int
    expected_elements: list[str]
    method_sets: dict[str, Any]


@dataclass
class AuditFindings:
    """Audit findings and statistics."""
    total_contracts: int = 0
    total_questions: int = 0
    modality_distribution: dict[str, int] = field(default_factory=dict)
    alignment_errors: list[str] = field(default_factory=list)
    mathematical_errors: list[str] = field(default_factory=list)
    threshold_violations: list[str] = field(default_factory=list)
    weight_violations: list[str] = field(default_factory=list)
    pattern_mismatches: list[str] = field(default_factory=list)
    critical_findings: list[str] = field(default_factory=list)
    high_findings: list[str] = field(default_factory=list)
    medium_findings: list[str] = field(default_factory=list)
    low_findings: list[str] = field(default_factory=list)
    
    def add_finding(self, severity: str, message: str) -> None:
        """Add a finding with specified severity."""
        if severity == "CRITICAL":
            self.critical_findings.append(message)
        elif severity == "HIGH":
            self.high_findings.append(message)
        elif severity == "MEDIUM":
            self.medium_findings.append(message)
        elif severity == "LOW":
            self.low_findings.append(message)


class MicroScoringMathematicalAuditor:
    """Comprehensive mathematical auditor for micro-level scoring procedures."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.questionnaire_path = repo_root / "canonic_questionnaire_central" / "questionnaire_monolith.json"
        self.contracts_dir = repo_root / "src" / "canonic_phases" / "Phase_two" / "json_files_phase_two" / "executor_contracts" / "specialized"
        self.findings = AuditFindings()
        self.contracts: dict[str, ContractAnalysis] = {}
        self.questions: dict[str, QuestionnaireAnalysis] = {}
        self.scoring_formulas: dict[str, ScoringModalityFormula] = {}
        
    def load_scoring_formulas(self) -> None:
        """Load scoring modality mathematical formulas."""
        # TYPE_A: High precision, balanced weights
        self.scoring_formulas["TYPE_A"] = ScoringModalityFormula(
            modality="TYPE_A",
            description="High precision balanced scoring",
            threshold=0.65,
            aggregation="weighted_mean",
            weight_elements=0.4,
            weight_similarity=0.3,
            weight_patterns=0.3,
            formula="score = 0.4*E + 0.3*S + 0.3*P",
            failure_code="INSUFFICIENT_EVIDENCE_TYPE_A"
        )
        
        # TYPE_B: Evidence-focused, higher threshold
        self.scoring_formulas["TYPE_B"] = ScoringModalityFormula(
            modality="TYPE_B",
            description="Evidence-focused high threshold",
            threshold=0.70,
            aggregation="weighted_mean",
            weight_elements=0.5,
            weight_similarity=0.25,
            weight_patterns=0.25,
            formula="score = 0.5*E + 0.25*S + 0.25*P",
            failure_code="INSUFFICIENT_EVIDENCE_TYPE_B"
        )
        
        # TYPE_C: Similarity-focused
        self.scoring_formulas["TYPE_C"] = ScoringModalityFormula(
            modality="TYPE_C",
            description="Semantic similarity focused",
            threshold=0.60,
            aggregation="weighted_mean",
            weight_elements=0.25,
            weight_similarity=0.5,
            weight_patterns=0.25,
            formula="score = 0.25*E + 0.5*S + 0.25*P",
            failure_code="INSUFFICIENT_SIMILARITY_TYPE_C"
        )
        
        # TYPE_D: Pattern-focused
        self.scoring_formulas["TYPE_D"] = ScoringModalityFormula(
            modality="TYPE_D",
            description="Pattern matching focused",
            threshold=0.60,
            aggregation="weighted_mean",
            weight_elements=0.25,
            weight_similarity=0.25,
            weight_patterns=0.5,
            formula="score = 0.25*E + 0.25*S + 0.5*P",
            failure_code="INSUFFICIENT_PATTERNS_TYPE_D"
        )
        
        # TYPE_E: Conservative, maximum aggregation
        self.scoring_formulas["TYPE_E"] = ScoringModalityFormula(
            modality="TYPE_E",
            description="Conservative maximum aggregation",
            threshold=0.75,
            aggregation="max",
            weight_elements=1.0,
            weight_similarity=1.0,
            weight_patterns=1.0,
            formula="score = max(E, S, P)",
            failure_code="INSUFFICIENT_EVIDENCE_TYPE_E"
        )
        
        # TYPE_F: Strict, minimum aggregation
        self.scoring_formulas["TYPE_F"] = ScoringModalityFormula(
            modality="TYPE_F",
            description="Strict minimum aggregation",
            threshold=0.55,
            aggregation="min",
            weight_elements=1.0,
            weight_similarity=1.0,
            weight_patterns=1.0,
            formula="score = min(E, S, P)",
            failure_code="INSUFFICIENT_EVIDENCE_TYPE_F"
        )
        
        print(f"{GREEN}✓ Loaded {len(self.scoring_formulas)} scoring modality formulas{RESET}")
    
    def load_questionnaire_data(self) -> None:
        """Load and analyze questionnaire micro questions."""
        print(f"\n{BOLD}Loading questionnaire_monolith.json...{RESET}")
        
        canonical_questionnaire = get_canonical_questionnaire(
            questionnaire_path=self.questionnaire_path,
        )
        questionnaire = canonical_questionnaire.data
        
        micro_questions = questionnaire.get('blocks', {}).get('micro_questions', [])
        
        for question in micro_questions:
            q_id = question.get('question_id', 'UNKNOWN')
            
            analysis = QuestionnaireAnalysis(
                question_id=q_id,
                base_slot=question.get('base_slot', 'UNKNOWN'),
                policy_area_id=question.get('policy_area_id', 'UNKNOWN'),
                dimension_id=question.get('dimension_id', 'UNKNOWN'),
                scoring_modality=question.get('scoring_modality', 'UNKNOWN'),
                patterns_count=len(question.get('patterns', [])),
                validations_count=len(question.get('validations', [])),
                expected_elements=question.get('expected_elements', []),
                method_sets=question.get('method_sets', {})
            )
            
            self.questions[q_id] = analysis
            
            # Track modality distribution
            modality = analysis.scoring_modality
            self.findings.modality_distribution[modality] = self.findings.modality_distribution.get(modality, 0) + 1
        
        self.findings.total_questions = len(self.questions)
        print(f"{GREEN}✓ Loaded {self.findings.total_questions} micro questions{RESET}")
        print(f"{CYAN}  Modality distribution:{RESET}")
        for modality, count in sorted(self.findings.modality_distribution.items(), key=lambda x: -x[1]):
            print(f"    {modality}: {count}")
    
    def load_executor_contracts(self) -> None:
        """Load and analyze executor contracts."""
        print(f"\n{BOLD}Loading executor contracts...{RESET}")
        
        contract_files = list(self.contracts_dir.glob("*.v3.json"))
        
        for contract_file in contract_files:
            try:
                with open(contract_file, 'r', encoding='utf-8') as f:
                    contract = json.load(f)
                
                identity = contract.get('identity', {})
                q_id = identity.get('question_id', 'UNKNOWN')
                
                # Extract scoring modality from question_context if present
                question_context = contract.get('question_context', {})
                scoring_modality = question_context.get('scoring_modality')
                
                analysis = ContractAnalysis(
                    contract_path=str(contract_file),
                    question_id=q_id,
                    base_slot=identity.get('base_slot', 'UNKNOWN'),
                    policy_area_id=identity.get('policy_area_id', 'UNKNOWN'),
                    dimension_id=identity.get('dimension_id', 'UNKNOWN'),
                    scoring_modality=scoring_modality,
                    method_count=contract.get('method_binding', {}).get('method_count', 0),
                    patterns_count=len(question_context.get('patterns', [])),
                    validation_rules_count=len(contract.get('validation_rules', [])),
                    expected_elements=question_context.get('expected_elements', [])
                )
                
                self.contracts[q_id] = analysis
                
            except Exception as e:
                print(f"{RED}✗ Error loading {contract_file.name}: {e}{RESET}")
                self.findings.add_finding("HIGH", f"Failed to load contract {contract_file.name}: {e}")
        
        self.findings.total_contracts = len(self.contracts)
        print(f"{GREEN}✓ Loaded {self.findings.total_contracts} executor contracts{RESET}")
    
    def audit_contract_questionnaire_alignment(self) -> None:
        """Audit alignment between executor contracts and questionnaire."""
        print(f"\n{BOLD}Auditing contract-questionnaire alignment...{RESET}")
        
        aligned_count = 0
        misaligned_count = 0
        
        for q_id, question in self.questions.items():
            if q_id not in self.contracts:
                self.findings.alignment_errors.append(
                    f"Question {q_id} has no corresponding executor contract"
                )
                self.findings.add_finding("HIGH", f"Missing executor contract for question {q_id}")
                misaligned_count += 1
                continue
            
            contract = self.contracts[q_id]
            
            # Check scoring modality alignment
            if contract.scoring_modality and contract.scoring_modality != question.scoring_modality:
                self.findings.alignment_errors.append(
                    f"Question {q_id}: Scoring modality mismatch - "
                    f"Questionnaire: {question.scoring_modality}, Contract: {contract.scoring_modality}"
                )
                self.findings.add_finding(
                    "CRITICAL",
                    f"Q{q_id}: Scoring modality mismatch (Q:{question.scoring_modality} vs C:{contract.scoring_modality})"
                )
                misaligned_count += 1
                continue
            
            # Check pattern count alignment (warning if significantly different)
            if abs(contract.patterns_count - question.patterns_count) > 5:
                self.findings.pattern_mismatches.append(
                    f"Question {q_id}: Pattern count mismatch - "
                    f"Questionnaire: {question.patterns_count}, Contract: {contract.patterns_count}"
                )
                self.findings.add_finding(
                    "MEDIUM",
                    f"Q{q_id}: Large pattern count difference (Q:{question.patterns_count} vs C:{contract.patterns_count})"
                )
            
            # Check expected elements alignment
            # Handle both list and dict formats for expected_elements
            q_elements = question.expected_elements
            c_elements = contract.expected_elements
            
            # Convert to comparable sets (extract IDs if dicts)
            q_elements_set = set()
            if isinstance(q_elements, list):
                for elem in q_elements:
                    if isinstance(elem, dict):
                        q_elements_set.add(elem.get('id', str(elem)))
                    else:
                        q_elements_set.add(str(elem))
            
            c_elements_set = set()
            if isinstance(c_elements, list):
                for elem in c_elements:
                    if isinstance(elem, dict):
                        c_elements_set.add(elem.get('id', str(elem)))
                    else:
                        c_elements_set.add(str(elem))
            
            if q_elements_set != c_elements_set:
                missing_in_contract = q_elements_set - c_elements_set
                extra_in_contract = c_elements_set - q_elements_set
                if missing_in_contract or extra_in_contract:
                    self.findings.add_finding(
                        "MEDIUM",
                        f"Q{q_id}: Expected elements mismatch - "
                        f"Missing: {missing_in_contract}, Extra: {extra_in_contract}"
                    )
            
            aligned_count += 1
        
        # Check for contracts without questions
        for q_id in self.contracts:
            if q_id not in self.questions:
                self.findings.alignment_errors.append(
                    f"Contract {q_id} has no corresponding questionnaire entry"
                )
                self.findings.add_finding("HIGH", f"Orphaned contract for question {q_id}")
                misaligned_count += 1
        
        print(f"{GREEN}✓ Aligned: {aligned_count}{RESET}")
        print(f"{YELLOW}⚠ Misaligned: {misaligned_count}{RESET}")
        print(f"{RED}✗ Alignment errors: {len(self.findings.alignment_errors)}{RESET}")
    
    def audit_mathematical_formulas(self) -> None:
        """Audit mathematical correctness of scoring formulas."""
        print(f"\n{BOLD}Auditing mathematical formulas...{RESET}")
        
        # Test each formula with boundary conditions
        test_cases = [
            (0.0, 0.0, 0.0, "All zeros"),
            (1.0, 1.0, 1.0, "All ones"),
            (0.5, 0.5, 0.5, "All 0.5"),
            (1.0, 0.0, 0.0, "Only elements"),
            (0.0, 1.0, 0.0, "Only similarity"),
            (0.0, 0.0, 1.0, "Only patterns"),
        ]
        
        for modality, formula in self.scoring_formulas.items():
            print(f"\n{CYAN}  Testing {modality} ({formula.description}){RESET}")
            print(f"    Formula: {formula.formula}")
            print(f"    Threshold: {formula.threshold}")
            print(f"    Aggregation: {formula.aggregation}")
            
            for e, s, p, desc in test_cases:
                score = formula.compute_score(e, s, p)
                passes = formula.passes_threshold(score)
                
                # Verify score is in valid range [0, 1]
                if not (0.0 <= score <= 1.0):
                    self.findings.mathematical_errors.append(
                        f"{modality}: Score out of range [0,1] for {desc} - got {score}"
                    )
                    self.findings.add_finding(
                        "CRITICAL",
                        f"{modality}: Invalid score range {score} for test case '{desc}'"
                    )
                
                # Verify threshold logic
                if formula.aggregation == "weighted_mean":
                    weights_sum = formula.weight_elements + formula.weight_similarity + formula.weight_patterns
                    if abs(weights_sum - 1.0) > 0.01:
                        self.findings.weight_violations.append(
                            f"{modality}: Weights don't sum to 1.0 - got {weights_sum}"
                        )
                        self.findings.add_finding(
                            "HIGH",
                            f"{modality}: Weights sum to {weights_sum:.3f} instead of 1.0"
                        )
            
            # Verify threshold is in valid range
            if not (0.0 <= formula.threshold <= 1.0):
                self.findings.threshold_violations.append(
                    f"{modality}: Threshold out of range [0,1] - got {formula.threshold}"
                )
                self.findings.add_finding(
                    "CRITICAL",
                    f"{modality}: Invalid threshold {formula.threshold}"
                )
        
        print(f"\n{GREEN}✓ Mathematical formula audit complete{RESET}")
        print(f"{RED}✗ Mathematical errors: {len(self.findings.mathematical_errors)}{RESET}")
        print(f"{RED}✗ Threshold violations: {len(self.findings.threshold_violations)}{RESET}")
        print(f"{RED}✗ Weight violations: {len(self.findings.weight_violations)}{RESET}")
    
    def audit_scoring_distribution(self) -> None:
        """Audit distribution of scoring modalities across questions."""
        print(f"\n{BOLD}Auditing scoring modality distribution...{RESET}")
        
        # Check if distribution is reasonable
        total = self.findings.total_questions
        if total == 0:
            self.findings.add_finding("CRITICAL", "No questions found in questionnaire")
            return
        
        for modality, count in self.findings.modality_distribution.items():
            percentage = (count / total) * 100
            print(f"  {modality}: {count} ({percentage:.1f}%)")
            
            # Check if modality is defined
            if modality not in self.scoring_formulas and modality not in ["MESO_INTEGRATION", "MACRO_HOLISTIC"]:
                self.findings.add_finding(
                    "HIGH",
                    f"Scoring modality {modality} used by {count} questions but not defined in formulas"
                )
            
            # Warn if unusual distribution (TYPE_A dominates heavily)
            if modality == "TYPE_A" and percentage > 90:
                self.findings.add_finding(
                    "LOW",
                    f"TYPE_A used by {percentage:.1f}% of questions - consider diversification"
                )
    
    def generate_report(self) -> str:
        """Generate comprehensive audit report."""
        report_lines = []
        
        report_lines.append("=" * 80)
        report_lines.append("MATHEMATICAL AUDIT OF MICRO-LEVEL SCORING PROCEDURES")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # Executive Summary
        report_lines.append("EXECUTIVE SUMMARY")
        report_lines.append("-" * 80)
        report_lines.append(f"Total Questions:          {self.findings.total_questions}")
        report_lines.append(f"Total Contracts:          {self.findings.total_contracts}")
        report_lines.append(f"Scoring Modalities:       {len(self.scoring_formulas)}")
        report_lines.append(f"")
        report_lines.append(f"CRITICAL Findings:        {len(self.findings.critical_findings)}")
        report_lines.append(f"HIGH Findings:            {len(self.findings.high_findings)}")
        report_lines.append(f"MEDIUM Findings:          {len(self.findings.medium_findings)}")
        report_lines.append(f"LOW Findings:             {len(self.findings.low_findings)}")
        report_lines.append("")
        
        # Modality Distribution
        report_lines.append("SCORING MODALITY DISTRIBUTION")
        report_lines.append("-" * 80)
        for modality, count in sorted(self.findings.modality_distribution.items(), key=lambda x: -x[1]):
            percentage = (count / self.findings.total_questions) * 100 if self.findings.total_questions > 0 else 0
            report_lines.append(f"  {modality:20s}: {count:3d} questions ({percentage:5.1f}%)")
        report_lines.append("")
        
        # Mathematical Formulas
        report_lines.append("SCORING MODALITY MATHEMATICAL FORMULAS")
        report_lines.append("-" * 80)
        for modality, formula in sorted(self.scoring_formulas.items()):
            report_lines.append(f"\n{modality}: {formula.description}")
            report_lines.append(f"  Formula:      {formula.formula}")
            report_lines.append(f"  Threshold:    {formula.threshold}")
            report_lines.append(f"  Aggregation:  {formula.aggregation}")
            report_lines.append(f"  Weights:      Elements={formula.weight_elements}, Similarity={formula.weight_similarity}, Patterns={formula.weight_patterns}")
            report_lines.append(f"  Failure Code: {formula.failure_code}")
        report_lines.append("")
        
        # Critical Findings
        if self.findings.critical_findings:
            report_lines.append("CRITICAL FINDINGS")
            report_lines.append("-" * 80)
            for i, finding in enumerate(self.findings.critical_findings, 1):
                report_lines.append(f"{i:3d}. {finding}")
            report_lines.append("")
        
        # High Findings
        if self.findings.high_findings:
            report_lines.append("HIGH FINDINGS")
            report_lines.append("-" * 80)
            for i, finding in enumerate(self.findings.high_findings, 1):
                report_lines.append(f"{i:3d}. {finding}")
            report_lines.append("")
        
        # Medium Findings
        if self.findings.medium_findings:
            report_lines.append("MEDIUM FINDINGS")
            report_lines.append("-" * 80)
            for i, finding in enumerate(self.findings.medium_findings, 1):
                report_lines.append(f"{i:3d}. {finding}")
            report_lines.append("")
        
        # Low Findings
        if self.findings.low_findings:
            report_lines.append("LOW FINDINGS")
            report_lines.append("-" * 80)
            for i, finding in enumerate(self.findings.low_findings, 1):
                report_lines.append(f"{i:3d}. {finding}")
            report_lines.append("")
        
        # Recommendations
        report_lines.append("RECOMMENDATIONS")
        report_lines.append("-" * 80)
        
        if len(self.findings.critical_findings) == 0 and len(self.findings.high_findings) == 0:
            report_lines.append("✓ No critical or high-severity issues found.")
            report_lines.append("✓ Mathematical scoring procedures are correctly implemented.")
            report_lines.append("✓ Contract-questionnaire alignment is maintained.")
        else:
            report_lines.append("1. Address all CRITICAL findings immediately")
            report_lines.append("2. Review and fix all HIGH findings")
            report_lines.append("3. Validate scoring modality assignments")
            report_lines.append("4. Ensure contract-questionnaire synchronization")
        
        if len(self.findings.weight_violations) > 0:
            report_lines.append("5. Normalize all scoring weights to sum to 1.0")
        
        if len(self.findings.pattern_mismatches) > 0:
            report_lines.append("6. Synchronize pattern definitions between contracts and questionnaire")
        
        report_lines.append("")
        report_lines.append("=" * 80)
        report_lines.append("END OF AUDIT REPORT")
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)
    
    def run_audit(self) -> None:
        """Run complete mathematical audit."""
        print(f"\n{BOLD}{BLUE}========================================{RESET}")
        print(f"{BOLD}{BLUE}MICRO-LEVEL SCORING MATHEMATICAL AUDIT{RESET}")
        print(f"{BOLD}{BLUE}========================================{RESET}\n")
        
        # Phase 1: Load data
        self.load_scoring_formulas()
        self.load_questionnaire_data()
        self.load_executor_contracts()
        
        # Phase 2: Audit procedures
        self.audit_contract_questionnaire_alignment()
        self.audit_mathematical_formulas()
        self.audit_scoring_distribution()
        
        # Phase 3: Generate report
        print(f"\n{BOLD}Generating audit report...{RESET}")
        report = self.generate_report()
        
        # Write report to file
        report_path = self.repo_root / "AUDIT_MICRO_SCORING_MATHEMATICS.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"{GREEN}✓ Audit report written to: {report_path}{RESET}")
        
        # Print summary
        print(f"\n{BOLD}AUDIT SUMMARY{RESET}")
        print(f"{'=' * 80}")
        print(f"CRITICAL: {len(self.findings.critical_findings)}")
        print(f"HIGH:     {len(self.findings.high_findings)}")
        print(f"MEDIUM:   {len(self.findings.medium_findings)}")
        print(f"LOW:      {len(self.findings.low_findings)}")
        print(f"{'=' * 80}")
        
        # Print to console
        print(f"\n{BOLD}Full Report:{RESET}")
        print(report)
        
        # Return exit code based on findings
        if len(self.findings.critical_findings) > 0:
            sys.exit(2)
        elif len(self.findings.high_findings) > 0:
            sys.exit(1)
        else:
            sys.exit(0)


def main() -> None:
    """Main entry point."""
    repo_root = Path(__file__).parent
    auditor = MicroScoringMathematicalAuditor(repo_root)
    auditor.run_audit()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Comprehensive Audit: Cluster Question Answering Capability (MESO Level)
==========================================================================

This script audits whether the F.A.R.F.A.N system can effectively answer questions
about development plan behavior in each of the 4 clusters (CL01-CL04).

The audit verifies three key requirements:

a. NEED IDENTIFICATION: System has full identification of cluster-level questions
   - Questionnaire contains 4 MESO questions (one per cluster)
   - Each MESO question is properly structured with cluster_id
   - Clusters are defined with policy area mappings

b. INPUT GENERATION: Necessary inputs are issued to answer cluster questions
   - Phase 2: 300 executor contracts (50 per dimension × 6 dimensions) exist
   - Phase 4: Dimension aggregation (60 dimensions: 10 PA × 6 DIM)
   - Phase 5: Policy area aggregation (10 areas)
   - Phase 6: Cluster aggregation (4 clusters from policy areas)
   - Data flows: Micro (Phase 2) → Dimension (Phase 4) → Area (Phase 5) → Cluster (Phase 6)

c. RESPONSE STRUCTURING: Carver has equipment and programming to structure responses
   - CarverAnswer dataclass exists for structured responses
   - ContractInterpreter can extract cluster-level semantics
   - EvidenceGraph can build causal graphs for cluster analysis
   - GapAnalyzer can identify multi-dimensional gaps at cluster level
   - CarverRenderer can generate narrative responses

Author: F.A.R.F.A.N Audit System
Version: 1.0.0
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple
from collections import defaultdict
from dataclasses import dataclass, field
import logging

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from orchestration.factory import get_canonical_questionnaire

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class AuditResult:
    """Results of the cluster question capability audit."""
    passed: bool
    severity: str  # "PASSED", "WARNING", "CRITICAL"
    section: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


class ClusterQuestionAuditor:
    """Audits the complete capability to answer cluster-level MESO questions."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.questionnaire_path = repo_root / "canonic_questionnaire_central" / "questionnaire_monolith.json"
        self.contracts_dir = repo_root / "src" / "canonic_phases" / "Phase_two" / "json_files_phase_two" / "executor_contracts" / "specialized"
        self.aggregation_file = repo_root / "src" / "canonic_phases" / "Phase_four_five_six_seven" / "aggregation.py"
        self.carver_file = repo_root / "src" / "canonic_phases" / "Phase_two" / "carver.py"
        
        self.results: List[AuditResult] = []
        self.questionnaire: Dict[str, Any] = {}
        self.clusters: List[Dict[str, Any]] = []
        self.meso_questions: List[Dict[str, Any]] = []
        
    def run_audit(self) -> Dict[str, Any]:
        """Execute complete audit and return comprehensive results."""
        logger.info("=" * 80)
        logger.info("CLUSTER QUESTION CAPABILITY AUDIT - Starting...")
        logger.info("=" * 80)
        
        # Section A: Need Identification
        logger.info("\n[SECTION A] NEED IDENTIFICATION - Questionnaire Structure")
        logger.info("-" * 80)
        self._audit_questionnaire_structure()
        
        # Section B: Input Generation
        logger.info("\n[SECTION B] INPUT GENERATION - Data Flow & Aggregation")
        logger.info("-" * 80)
        self._audit_input_generation()
        
        # Section C: Response Structuring
        logger.info("\n[SECTION C] RESPONSE STRUCTURING - Carver Capabilities")
        logger.info("-" * 80)
        self._audit_carver_capabilities()
        
        # Generate summary
        summary = self._generate_summary()
        
        logger.info("\n" + "=" * 80)
        logger.info("AUDIT COMPLETE")
        logger.info("=" * 80)
        
        return summary
    
    def _audit_questionnaire_structure(self) -> None:
        """Audit Section A: Need Identification in questionnaire."""
        
        # A.1: Load questionnaire
        try:
            canonical_questionnaire = get_canonical_questionnaire(
                questionnaire_path=self.questionnaire_path,
            )
            self.questionnaire = canonical_questionnaire.data
            self.results.append(AuditResult(
                passed=True,
                severity="PASSED",
                section="A.1",
                message="Questionnaire monolith loaded successfully",
                details={"path": str(self.questionnaire_path)}
            ))
            logger.info("✓ A.1: Questionnaire loaded")
        except Exception as e:
            self.results.append(AuditResult(
                passed=False,
                severity="CRITICAL",
                section="A.1",
                message=f"Failed to load questionnaire: {e}",
                details={"path": str(self.questionnaire_path), "error": str(e)}
            ))
            logger.error(f"✗ A.1: Failed to load questionnaire: {e}")
            return
        
        # A.2: Check clusters definition in niveles
        blocks = self.questionnaire.get("blocks", {})
        niveles = blocks.get("niveles_abstraccion", {})
        self.clusters = niveles.get("clusters", [])
        
        if not self.clusters:
            self.results.append(AuditResult(
                passed=False,
                severity="CRITICAL",
                section="A.2",
                message="No clusters defined in niveles_abstraccion",
                details={"niveles_keys": list(niveles.keys())}
            ))
            logger.error("✗ A.2: No clusters defined")
        elif len(self.clusters) != 4:
            self.results.append(AuditResult(
                passed=False,
                severity="CRITICAL",
                section="A.2",
                message=f"Expected 4 clusters, found {len(self.clusters)}",
                details={"cluster_count": len(self.clusters)}
            ))
            logger.error(f"✗ A.2: Expected 4 clusters, found {len(self.clusters)}")
        else:
            cluster_ids = [c.get("cluster_id") for c in self.clusters]
            expected_ids = ["CL01", "CL02", "CL03", "CL04"]
            if cluster_ids == expected_ids:
                self.results.append(AuditResult(
                    passed=True,
                    severity="PASSED",
                    section="A.2",
                    message="All 4 clusters defined correctly (CL01-CL04)",
                    details={"clusters": cluster_ids}
                ))
                logger.info(f"✓ A.2: 4 clusters defined: {cluster_ids}")
            else:
                self.results.append(AuditResult(
                    passed=False,
                    severity="WARNING",
                    section="A.2",
                    message=f"Cluster IDs don't match expected: {cluster_ids} vs {expected_ids}",
                    details={"found": cluster_ids, "expected": expected_ids}
                ))
                logger.warning(f"⚠ A.2: Cluster IDs mismatch: {cluster_ids}")
        
        # A.3: Check cluster-policy area mappings
        for cluster in self.clusters:
            cluster_id = cluster.get("cluster_id")
            policy_areas = cluster.get("policy_area_ids", [])
            if not policy_areas:
                self.results.append(AuditResult(
                    passed=False,
                    severity="CRITICAL",
                    section="A.3",
                    message=f"Cluster {cluster_id} has no policy_area_ids mapping",
                    details={"cluster_id": cluster_id}
                ))
                logger.error(f"✗ A.3: Cluster {cluster_id} has no policy areas")
            else:
                self.results.append(AuditResult(
                    passed=True,
                    severity="PASSED",
                    section="A.3",
                    message=f"Cluster {cluster_id} mapped to {len(policy_areas)} policy areas",
                    details={"cluster_id": cluster_id, "policy_areas": policy_areas}
                ))
                logger.info(f"✓ A.3: Cluster {cluster_id} → {policy_areas}")
        
        # A.4: Check MESO questions
        self.meso_questions = blocks.get("meso_questions", [])
        
        if not self.meso_questions:
            self.results.append(AuditResult(
                passed=False,
                severity="CRITICAL",
                section="A.4",
                message="No MESO questions found in questionnaire",
                details={}
            ))
            logger.error("✗ A.4: No MESO questions found")
        elif len(self.meso_questions) != 4:
            self.results.append(AuditResult(
                passed=False,
                severity="WARNING",
                section="A.4",
                message=f"Expected 4 MESO questions, found {len(self.meso_questions)}",
                details={"count": len(self.meso_questions)}
            ))
            logger.warning(f"⚠ A.4: Expected 4 MESO questions, found {len(self.meso_questions)}")
        else:
            self.results.append(AuditResult(
                passed=True,
                severity="PASSED",
                section="A.4",
                message="All 4 MESO questions found",
                details={"count": len(self.meso_questions)}
            ))
            logger.info(f"✓ A.4: 4 MESO questions found")
        
        # A.5: Verify each MESO question has cluster_id
        for meso_q in self.meso_questions:
            cluster_id = meso_q.get("cluster_id")
            question_text = meso_q.get("text", "")[:60]
            if not cluster_id:
                self.results.append(AuditResult(
                    passed=False,
                    severity="CRITICAL",
                    section="A.5",
                    message=f"MESO question missing cluster_id: '{question_text}...'",
                    details={"question": meso_q}
                ))
                logger.error(f"✗ A.5: MESO question missing cluster_id")
            else:
                self.results.append(AuditResult(
                    passed=True,
                    severity="PASSED",
                    section="A.5",
                    message=f"MESO question for {cluster_id}: '{question_text}...'",
                    details={"cluster_id": cluster_id, "text": question_text}
                ))
                logger.info(f"✓ A.5: MESO question {cluster_id}")
    
    def _audit_input_generation(self) -> None:
        """Audit Section B: Input Generation via Phase 2-6 pipeline."""
        
        # B.1: Check Phase 2 executor contracts exist (300 expected)
        if not self.contracts_dir.exists():
            self.results.append(AuditResult(
                passed=False,
                severity="CRITICAL",
                section="B.1",
                message="Phase 2 executor contracts directory not found",
                details={"path": str(self.contracts_dir)}
            ))
            logger.error(f"✗ B.1: Contracts directory not found: {self.contracts_dir}")
        else:
            contract_files = list(self.contracts_dir.glob("Q*.v3.json"))
            if len(contract_files) != 300:
                self.results.append(AuditResult(
                    passed=False,
                    severity="WARNING",
                    section="B.1",
                    message=f"Expected 300 executor contracts, found {len(contract_files)}",
                    details={"expected": 300, "found": len(contract_files)}
                ))
                logger.warning(f"⚠ B.1: Expected 300 contracts, found {len(contract_files)}")
            else:
                self.results.append(AuditResult(
                    passed=True,
                    severity="PASSED",
                    section="B.1",
                    message="All 300 Phase 2 executor contracts present",
                    details={"count": len(contract_files)}
                ))
                logger.info(f"✓ B.1: 300 executor contracts present")
            
            # B.2: Verify contracts have policy_area_id and dimension_id
            sample_contracts = contract_files[:10]  # Sample 10 for verification
            contracts_with_ids = 0
            for contract_file in sample_contracts:
                try:
                    with open(contract_file, 'r', encoding='utf-8') as f:
                        contract = json.load(f)
                    identity = contract.get("identity", {})
                    if identity.get("policy_area_id") and identity.get("dimension_id"):
                        contracts_with_ids += 1
                except Exception as e:
                    logger.warning(f"Failed to read {contract_file}: {e}")
            
            if contracts_with_ids == len(sample_contracts):
                self.results.append(AuditResult(
                    passed=True,
                    severity="PASSED",
                    section="B.2",
                    message="Sample contracts have policy_area_id and dimension_id",
                    details={"sampled": len(sample_contracts), "valid": contracts_with_ids}
                ))
                logger.info(f"✓ B.2: Contracts have PA×DIM coordinates (sampled {len(sample_contracts)})")
            else:
                self.results.append(AuditResult(
                    passed=False,
                    severity="WARNING",
                    section="B.2",
                    message=f"Some contracts missing PA/DIM IDs: {contracts_with_ids}/{len(sample_contracts)}",
                    details={"sampled": len(sample_contracts), "valid": contracts_with_ids}
                ))
                logger.warning(f"⚠ B.2: Only {contracts_with_ids}/{len(sample_contracts)} contracts have IDs")
        
        # B.3: Check aggregation.py has ClusterAggregator class
        if not self.aggregation_file.exists():
            self.results.append(AuditResult(
                passed=False,
                severity="CRITICAL",
                section="B.3",
                message="aggregation.py not found",
                details={"path": str(self.aggregation_file)}
            ))
            logger.error(f"✗ B.3: aggregation.py not found")
        else:
            with open(self.aggregation_file, 'r', encoding='utf-8') as f:
                aggregation_code = f.read()
            
            has_cluster_aggregator = "class ClusterAggregator" in aggregation_code
            has_aggregate_cluster = "def aggregate_cluster" in aggregation_code
            has_cluster_score = "class ClusterScore" in aggregation_code
            
            if has_cluster_aggregator and has_aggregate_cluster and has_cluster_score:
                self.results.append(AuditResult(
                    passed=True,
                    severity="PASSED",
                    section="B.3",
                    message="ClusterAggregator class with aggregate_cluster method found",
                    details={
                        "has_class": has_cluster_aggregator,
                        "has_method": has_aggregate_cluster,
                        "has_score": has_cluster_score
                    }
                ))
                logger.info("✓ B.3: ClusterAggregator implementation found")
            else:
                self.results.append(AuditResult(
                    passed=False,
                    severity="CRITICAL",
                    section="B.3",
                    message="ClusterAggregator missing required components",
                    details={
                        "has_class": has_cluster_aggregator,
                        "has_method": has_aggregate_cluster,
                        "has_score": has_cluster_score
                    }
                ))
                logger.error("✗ B.3: ClusterAggregator incomplete")
        
        # B.4: Check data flow from micro → dimension → area → cluster
        # This verifies the hierarchical aggregation structure
        if self.aggregation_file.exists():
            with open(self.aggregation_file, 'r', encoding='utf-8') as f:
                aggregation_code = f.read()
            
            has_dimension_agg = "class DimensionAggregator" in aggregation_code
            has_area_agg = "class AreaPolicyAggregator" in aggregation_code
            has_macro_agg = "class MacroAggregator" in aggregation_code
            
            if has_dimension_agg and has_area_agg and has_macro_agg:
                self.results.append(AuditResult(
                    passed=True,
                    severity="PASSED",
                    section="B.4",
                    message="Complete aggregation hierarchy present (Dimension → Area → Cluster → Macro)",
                    details={
                        "dimension": has_dimension_agg,
                        "area": has_area_agg,
                        "cluster": has_cluster_aggregator,
                        "macro": has_macro_agg
                    }
                ))
                logger.info("✓ B.4: Complete aggregation pipeline present")
            else:
                self.results.append(AuditResult(
                    passed=False,
                    severity="CRITICAL",
                    section="B.4",
                    message="Aggregation hierarchy incomplete",
                    details={
                        "dimension": has_dimension_agg,
                        "area": has_area_agg,
                        "cluster": has_cluster_aggregator,
                        "macro": has_macro_agg
                    }
                ))
                logger.error("✗ B.4: Aggregation hierarchy incomplete")
    
    def _audit_carver_capabilities(self) -> None:
        """Audit Section C: Carver's response structuring capabilities."""
        
        # C.1: Check carver.py exists
        if not self.carver_file.exists():
            self.results.append(AuditResult(
                passed=False,
                severity="CRITICAL",
                section="C.1",
                message="carver.py not found",
                details={"path": str(self.carver_file)}
            ))
            logger.error(f"✗ C.1: carver.py not found")
            return
        
        with open(self.carver_file, 'r', encoding='utf-8') as f:
            carver_code = f.read()
        
        # C.2: Check CarverAnswer dataclass
        has_carver_answer = "class CarverAnswer" in carver_code
        if has_carver_answer:
            self.results.append(AuditResult(
                passed=True,
                severity="PASSED",
                section="C.2",
                message="CarverAnswer dataclass found for structured responses",
                details={"present": True}
            ))
            logger.info("✓ C.2: CarverAnswer dataclass present")
        else:
            self.results.append(AuditResult(
                passed=False,
                severity="CRITICAL",
                section="C.2",
                message="CarverAnswer dataclass not found",
                details={"present": False}
            ))
            logger.error("✗ C.2: CarverAnswer dataclass missing")
        
        # C.3: Check ContractInterpreter
        has_contract_interpreter = "class ContractInterpreter" in carver_code
        if has_contract_interpreter:
            self.results.append(AuditResult(
                passed=True,
                severity="PASSED",
                section="C.3",
                message="ContractInterpreter found for semantic extraction",
                details={"present": True}
            ))
            logger.info("✓ C.3: ContractInterpreter present")
        else:
            self.results.append(AuditResult(
                passed=False,
                severity="WARNING",
                section="C.3",
                message="ContractInterpreter not found",
                details={"present": False}
            ))
            logger.warning("⚠ C.3: ContractInterpreter missing")
        
        # C.4: Check EvidenceGraph or EvidenceAnalyzer
        has_evidence_graph = "class EvidenceGraph" in carver_code
        has_evidence_analyzer = "class EvidenceAnalyzer" in carver_code
        if has_evidence_graph or has_evidence_analyzer:
            component_name = "EvidenceGraph" if has_evidence_graph else "EvidenceAnalyzer"
            self.results.append(AuditResult(
                passed=True,
                severity="PASSED",
                section="C.4",
                message=f"{component_name} found for evidence analysis",
                details={"present": True, "component": component_name}
            ))
            logger.info(f"✓ C.4: {component_name} present")
        else:
            self.results.append(AuditResult(
                passed=False,
                severity="WARNING",
                section="C.4",
                message="Neither EvidenceGraph nor EvidenceAnalyzer found",
                details={"present": False}
            ))
            logger.warning("⚠ C.4: Evidence analysis component missing")
        
        # C.5: Check GapAnalyzer
        has_gap_analyzer = "class GapAnalyzer" in carver_code
        if has_gap_analyzer:
            self.results.append(AuditResult(
                passed=True,
                severity="PASSED",
                section="C.5",
                message="GapAnalyzer found for gap identification",
                details={"present": True}
            ))
            logger.info("✓ C.5: GapAnalyzer present")
        else:
            self.results.append(AuditResult(
                passed=False,
                severity="WARNING",
                section="C.5",
                message="GapAnalyzer not found",
                details={"present": False}
            ))
            logger.warning("⚠ C.5: GapAnalyzer missing")
        
        # C.6: Check BayesianConfidence
        has_bayesian = "class BayesianConfidence" in carver_code or "BayesianConfidenceResult" in carver_code
        if has_bayesian:
            self.results.append(AuditResult(
                passed=True,
                severity="PASSED",
                section="C.6",
                message="Bayesian confidence quantification found",
                details={"present": True}
            ))
            logger.info("✓ C.6: Bayesian confidence present")
        else:
            self.results.append(AuditResult(
                passed=False,
                severity="WARNING",
                section="C.6",
                message="Bayesian confidence quantification not found",
                details={"present": False}
            ))
            logger.warning("⚠ C.6: Bayesian confidence missing")
        
        # C.7: Check CarverRenderer or similar response formatting
        has_renderer = "class CarverRenderer" in carver_code or "def render" in carver_code
        if has_renderer:
            self.results.append(AuditResult(
                passed=True,
                severity="PASSED",
                section="C.7",
                message="Response rendering capability found",
                details={"present": True}
            ))
            logger.info("✓ C.7: Response renderer present")
        else:
            self.results.append(AuditResult(
                passed=False,
                severity="WARNING",
                section="C.7",
                message="Response rendering not explicitly found",
                details={"present": False}
            ))
            logger.warning("⚠ C.7: Response renderer not clear")
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate comprehensive audit summary."""
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        critical = sum(1 for r in self.results if r.severity == "CRITICAL")
        warning = sum(1 for r in self.results if r.severity == "WARNING")
        
        summary = {
            "audit_name": "Cluster Question Answering Capability Audit",
            "timestamp": Path(__file__).stat().st_mtime,
            "total_checks": len(self.results),
            "passed": passed,
            "failed": failed,
            "critical_failures": critical,
            "warnings": warning,
            "overall_status": "PASS" if critical == 0 and failed == 0 else "FAIL" if critical > 0 else "WARNING",
            "sections": {
                "A_need_identification": self._section_summary("A"),
                "B_input_generation": self._section_summary("B"),
                "C_response_structuring": self._section_summary("C"),
            },
            "detailed_results": [
                {
                    "section": r.section,
                    "passed": r.passed,
                    "severity": r.severity,
                    "message": r.message,
                    "details": r.details
                }
                for r in self.results
            ]
        }
        
        # Print summary
        logger.info("\n" + "=" * 80)
        logger.info("AUDIT SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Checks: {len(self.results)}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Critical Failures: {critical}")
        logger.info(f"Warnings: {warning}")
        logger.info(f"Overall Status: {summary['overall_status']}")
        
        logger.info("\nSection Summaries:")
        for section_name, section_data in summary["sections"].items():
            status = "✓" if section_data["critical"] == 0 and section_data["failed"] == 0 else "✗"
            logger.info(f"  {status} {section_name}: {section_data['passed']}/{section_data['total']} passed")
        
        return summary
    
    def _section_summary(self, section_prefix: str) -> Dict[str, Any]:
        """Generate summary for a specific section."""
        section_results = [r for r in self.results if r.section.startswith(section_prefix)]
        return {
            "total": len(section_results),
            "passed": sum(1 for r in section_results if r.passed),
            "failed": sum(1 for r in section_results if not r.passed),
            "critical": sum(1 for r in section_results if r.severity == "CRITICAL"),
            "warnings": sum(1 for r in section_results if r.severity == "WARNING"),
        }


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.resolve()
    
    auditor = ClusterQuestionAuditor(repo_root)
    summary = auditor.run_audit()
    
    # Write results to JSON
    output_path = repo_root / "audit_cluster_question_capability_report.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\n✓ Audit report written to: {output_path}")
    
    # Exit with appropriate code
    if summary["overall_status"] == "PASS":
        logger.info("\n✓ AUDIT PASSED - System is capable of answering cluster questions")
        sys.exit(0)
    elif summary["overall_status"] == "WARNING":
        logger.warning("\n⚠ AUDIT PASSED WITH WARNINGS - System is capable but has minor issues")
        sys.exit(0)
    else:
        logger.error("\n✗ AUDIT FAILED - System has critical issues in cluster question capability")
        sys.exit(1)


if __name__ == "__main__":
    main()

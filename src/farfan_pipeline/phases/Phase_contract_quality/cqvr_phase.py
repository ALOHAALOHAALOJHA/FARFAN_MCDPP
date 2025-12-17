"""
Contract Quality Phase - CQVR Integration

This module implements Phase 11 (Contract Quality) of the F.A.R.F.A.N pipeline.
It validates executor contracts using the CQVR v2.0 rubric and produces
quality assessment reports.

Phase Characteristics:
- Phase ID: 11
- Mode: sync (post-pipeline validation)
- Input: Executor contracts from Phase 2
- Output: Quality assessment with decisions (PRODUCCION/PARCHEAR/REFORMULAR)
- Ignition: After Phase 10 (export) completes
- Node Interactions: Reads from Phase 2 contract storage, writes to reporting
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .cqvr_evaluator_core import CQVREvaluator, CQVRDecision


@dataclass
class ContractQualityResult:
    """Result of contract quality validation phase"""
    
    phase_id: int = 11
    phase_name: str = "Contract Quality Validation"
    timestamp: str = ""
    contracts_evaluated: int = 0
    average_score: float = 0.0
    production_ready: int = 0
    need_patches: int = 0
    need_reformulation: int = 0
    contract_decisions: List[Dict[str, Any]] = None
    summary_report_path: str = ""
    
    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if self.contract_decisions is None:
            self.contract_decisions = []
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ContractQualityPhase:
    """
    Phase 11: Contract Quality Validation
    
    Validates executor contracts using CQVR (Contract Quality Validation and
    Remediation) rubric. Produces quality assessments and triage decisions.
    
    Phase Contract:
    ---------------
    INPUT:
        - contracts_dir: Path to executor contracts (from Phase 2)
        - evaluation_config: CQVR configuration parameters
        
    OUTPUT:
        - ContractQualityResult with:
            * Per-contract evaluations
            * Aggregate statistics
            * Quality distribution (PRODUCCION/PARCHEAR/REFORMULAR)
            * Recommendations for remediation
    
    IGNITION POINT:
        - Triggered after Phase 10 (export) completes successfully
        - Can also run standalone for contract auditing
        
    NODE INTERACTIONS:
        - READS: Phase 2 executor contracts from contract storage
        - WRITES: Quality reports to reports/contract_quality/
        - NOTIFIES: Orchestrator of quality gate status
    
    MATHEMATICAL BASIS:
        - See README.md Section 2: Mathematical Foundation
        - Scoring based on convex combinations and threshold logic
        - Decision matrix implements production readiness criteria
    """
    
    def __init__(self, contracts_dir: Path, output_dir: Path) -> None:
        """
        Initialize Contract Quality Phase.
        
        Args:
            contracts_dir: Directory containing executor contracts
            output_dir: Directory for quality reports
        """
        self.contracts_dir = contracts_dir
        self.output_dir = output_dir
        self.evaluator = CQVREvaluator()
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def execute(
        self,
        contract_range: Tuple[int, int] = (1, 300),
        config: Dict[str, Any] | None = None
    ) -> ContractQualityResult:
        """
        Execute contract quality validation phase.
        
        Args:
            contract_range: Tuple of (start_q, end_q) for contract evaluation
            config: Optional configuration parameters
            
        Returns:
            ContractQualityResult with evaluation outcomes
        """
        start_q, end_q = contract_range
        
        # Evaluate contracts
        results = self.evaluator.evaluate_batch(
            self.contracts_dir,
            start_q,
            end_q
        )
        
        # Calculate summary statistics
        summary = self._calculate_summary(results)
        
        # Generate reports
        report_path = self._generate_phase_report(results, summary)
        
        # Build result
        result = ContractQualityResult(
            contracts_evaluated=summary["total_evaluated"],
            average_score=summary["average_score"],
            production_ready=summary["production_ready"],
            need_patches=summary["need_patches"],
            need_reformulation=summary["need_reformulation"],
            contract_decisions=[
                {
                    "contract_id": cid,
                    "decision": decision.decision,
                    "score": decision.score.total_score,
                    "blockers_count": len(decision.blockers),
                }
                for cid, decision, _ in results
            ],
            summary_report_path=str(report_path),
        )
        
        return result
    
    def _calculate_summary(
        self,
        results: List[Tuple[str, CQVRDecision, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Calculate summary statistics from results"""
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
    
    def _generate_phase_report(
        self,
        results: List[Tuple[str, CQVRDecision, Dict[str, Any]]],
        summary: Dict[str, Any]
    ) -> Path:
        """Generate phase execution report"""
        report_path = self.output_dir / "phase_11_contract_quality_report.json"
        
        report = {
            "phase_id": 11,
            "phase_name": "Contract Quality Validation",
            "timestamp": datetime.now().isoformat(),
            "evaluator": "CQVR Evaluator v2.0",
            "rubric": "CQVR v2.0 (100 points)",
            "summary": summary,
            "contracts": [
                {
                    "contract_id": cid,
                    "decision": decision.to_dict(),
                }
                for cid, decision, _ in results
            ],
        }
        
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report_path
    
    def validate_input(self, context: Dict[str, Any]) -> bool:
        """
        Validate phase input from pipeline context.
        
        Args:
            context: Pipeline execution context
            
        Returns:
            True if input is valid
        """
        # Check if contracts directory exists and has contracts
        if not self.contracts_dir.exists():
            return False
        
        contracts = list(self.contracts_dir.glob("Q*.v3.json"))
        return len(contracts) > 0
    
    def get_phase_contract(self) -> Dict[str, Any]:
        """
        Get phase contract specification.
        
        Returns:
            Dict describing phase contract
        """
        return {
            "phase_id": 11,
            "phase_name": "Contract Quality Validation",
            "phase_mode": "sync",
            "input_specification": {
                "required": [
                    {
                        "name": "contracts_dir",
                        "type": "Path",
                        "description": "Directory containing executor contracts from Phase 2",
                    }
                ],
                "optional": [
                    {
                        "name": "contract_range",
                        "type": "Tuple[int, int]",
                        "description": "Range of contracts to evaluate (start_q, end_q)",
                        "default": "(1, 300)",
                    },
                    {
                        "name": "config",
                        "type": "Dict[str, Any]",
                        "description": "CQVR configuration parameters",
                        "default": "None",
                    }
                ],
            },
            "output_specification": {
                "type": "ContractQualityResult",
                "fields": [
                    "contracts_evaluated",
                    "average_score",
                    "production_ready",
                    "need_patches",
                    "need_reformulation",
                    "contract_decisions",
                    "summary_report_path",
                ],
            },
            "ignition_point": {
                "trigger": "After Phase 10 (Export) completes",
                "condition": "success=true in Phase 10",
                "mode": "post-pipeline validation",
            },
            "node_interactions": {
                "reads_from": [
                    {
                        "phase": "Phase 2",
                        "artifact": "executor_contracts",
                        "location": "src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized/",
                    }
                ],
                "writes_to": [
                    {
                        "artifact": "quality_reports",
                        "location": "reports/contract_quality/",
                        "format": "JSON",
                    }
                ],
                "notifies": [
                    {
                        "target": "Orchestrator",
                        "event": "quality_gate_status",
                        "payload": "ContractQualityResult",
                    }
                ],
            },
            "mathematical_basis": "See README.md Section 2",
            "quality_gates": {
                "production_threshold": 80.0,
                "tier1_threshold": 35.0,
                "decision_matrix": {
                    "PRODUCCION": "Tier 1 ≥ 45, Total ≥ 80, 0 blockers",
                    "PARCHEAR": "Tier 1 ≥ 35, Total ≥ 70, ≤ 2 blockers",
                    "REFORMULAR": "Otherwise"
                }
            },
        }

#!/usr/bin/env python3
"""
Audit Tool: Macro-Level Development Plan Divergence Analysis
=============================================================

Audits whether the F.A.R.F.A.N system can effectively answer questions at the macro
framework level about divergence between development plans and the PA×DIM matrix.

This audit validates 4 critical capabilities:
a. System identification of macro-level needs (divergence analysis capability)
b. System emits necessary inputs for macro question answering
c. Response structure exists for macro-level questions  
d. Carver component is equipped with code for macro-level synthesis

Author: F.A.R.F.A.N Pipeline
Version: 1.0.0
"""

from __future__ import annotations

import inspect
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from orchestration.factory import get_canonical_questionnaire

# Type definitions
PolicyArea = str  # PA01-PA10
Dimension = str  # DIM01-DIM06


class AuditSeverity(Enum):
    """Severity levels for audit findings."""
    CRITICAL = "CRITICAL"  # Blocks macro-level functionality
    HIGH = "HIGH"  # Significantly impairs capability
    MEDIUM = "MEDIUM"  # Degrades quality but functional
    LOW = "LOW"  # Minor issue, doesn't block functionality
    INFO = "INFO"  # Informational, no issue


class CapabilityStatus(Enum):
    """Status of a capability check."""
    PRESENT = "PRESENT"  # Capability fully implemented
    PARTIAL = "PARTIAL"  # Capability partially implemented
    MISSING = "MISSING"  # Capability not found
    NOT_APPLICABLE = "NOT_APPLICABLE"  # Not relevant for this component


@dataclass
class AuditFinding:
    """Represents a single audit finding."""
    capability: str
    component: str
    severity: AuditSeverity
    status: CapabilityStatus
    description: str
    evidence: List[str] = field(default_factory=list)
    recommendation: Optional[str] = None
    code_references: List[str] = field(default_factory=list)


@dataclass
class ComponentAudit:
    """Audit results for a specific component."""
    component_name: str
    component_path: str
    exists: bool
    findings: List[AuditFinding] = field(default_factory=list)
    capabilities: Dict[str, CapabilityStatus] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MacroLevelAuditReport:
    """Complete audit report for macro-level capabilities."""
    timestamp: datetime
    
    # Component audits
    orchestrator_audit: Optional[ComponentAudit] = None
    carver_audit: Optional[ComponentAudit] = None
    phase_three_audit: Optional[ComponentAudit] = None
    questionnaire_audit: Optional[ComponentAudit] = None
    types_audit: Optional[ComponentAudit] = None
    
    # PA×DIM matrix analysis
    pa_dim_matrix_audit: Optional[Dict[str, Any]] = None
    
    # Overall findings
    all_findings: List[AuditFinding] = field(default_factory=list)
    critical_findings: List[AuditFinding] = field(default_factory=list)
    
    # Summary metrics
    total_capabilities_checked: int = 0
    capabilities_present: int = 0
    capabilities_partial: int = 0
    capabilities_missing: int = 0
    
    # Overall status
    macro_level_ready: bool = False
    overall_score: float = 0.0  # 0-1, percentage of capabilities present
    
    def compute_summary(self):
        """Compute summary metrics from findings."""
        self.all_findings = []
        for audit in [self.orchestrator_audit, self.carver_audit, self.phase_three_audit, 
                      self.questionnaire_audit, self.types_audit]:
            if audit:
                self.all_findings.extend(audit.findings)
        
        self.critical_findings = [
            f for f in self.all_findings 
            if f.severity == AuditSeverity.CRITICAL
        ]
        
        # Count capabilities
        status_counts = {}
        for audit in [self.orchestrator_audit, self.carver_audit, self.phase_three_audit]:
            if audit:
                for cap, status in audit.capabilities.items():
                    status_counts[status] = status_counts.get(status, 0) + 1
        
        self.total_capabilities_checked = sum(status_counts.values())
        self.capabilities_present = status_counts.get(CapabilityStatus.PRESENT, 0)
        self.capabilities_partial = status_counts.get(CapabilityStatus.PARTIAL, 0)
        self.capabilities_missing = status_counts.get(CapabilityStatus.MISSING, 0)
        
        if self.total_capabilities_checked > 0:
            self.overall_score = (
                self.capabilities_present + 0.5 * self.capabilities_partial
            ) / self.total_capabilities_checked
        
        self.macro_level_ready = (
            len(self.critical_findings) == 0 and 
            self.overall_score >= 0.75
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "summary": {
                "macro_level_ready": self.macro_level_ready,
                "overall_score": round(self.overall_score, 3),
                "total_capabilities_checked": self.total_capabilities_checked,
                "capabilities_present": self.capabilities_present,
                "capabilities_partial": self.capabilities_partial,
                "capabilities_missing": self.capabilities_missing,
                "critical_findings_count": len(self.critical_findings),
            },
            "components": {
                "orchestrator": self._component_to_dict(self.orchestrator_audit),
                "carver": self._component_to_dict(self.carver_audit),
                "phase_three": self._component_to_dict(self.phase_three_audit),
                "questionnaire": self._component_to_dict(self.questionnaire_audit),
                "types": self._component_to_dict(self.types_audit),
            },
            "pa_dim_matrix_audit": self.pa_dim_matrix_audit,
            "critical_findings": [self._finding_to_dict(f) for f in self.critical_findings],
            "all_findings": [self._finding_to_dict(f) for f in self.all_findings],
        }
    
    def _component_to_dict(self, audit: Optional[ComponentAudit]) -> Optional[Dict]:
        if not audit:
            return None
        return {
            "component_name": audit.component_name,
            "exists": audit.exists,
            "capabilities": {k: v.value for k, v in audit.capabilities.items()},
            "findings_count": len(audit.findings),
            "metadata": audit.metadata,
        }
    
    def _finding_to_dict(self, finding: AuditFinding) -> Dict:
        return {
            "capability": finding.capability,
            "component": finding.component,
            "severity": finding.severity.value,
            "status": finding.status.value,
            "description": finding.description,
            "evidence": finding.evidence,
            "recommendation": finding.recommendation,
            "code_references": finding.code_references,
        }


class MacroLevelAuditor:
    """
    Main auditor for macro-level development plan divergence analysis capabilities.
    """
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.src_root = repo_root / "src"
        self.report = MacroLevelAuditReport(timestamp=datetime.now())
    
    def run_full_audit(self) -> MacroLevelAuditReport:
        """Run complete macro-level audit."""
        print("=" * 80)
        print("MACRO-LEVEL DEVELOPMENT PLAN DIVERGENCE AUDIT")
        print("=" * 80)
        print()
        
        # Audit all components
        print("1. Auditing Orchestrator...")
        self.report.orchestrator_audit = self.audit_orchestrator()
        print()
        
        print("2. Auditing Carver...")
        self.report.carver_audit = self.audit_carver()
        print()
        
        print("3. Auditing Phase Three (Scoring/Aggregation)...")
        self.report.phase_three_audit = self.audit_phase_three()
        print()
        
        print("4. Auditing Questionnaire Structure...")
        self.report.questionnaire_audit = self.audit_questionnaire()
        print()
        
        print("5. Auditing Type System...")
        self.report.types_audit = self.audit_types()
        print()
        
        print("6. Auditing PA×DIM Matrix Coverage...")
        self.report.pa_dim_matrix_audit = self.audit_pa_dim_matrix()
        print()
        
        # Compute summary
        self.report.compute_summary()
        
        # Print summary
        self.print_summary()
        
        return self.report
    
    def audit_orchestrator(self) -> ComponentAudit:
        """Audit orchestrator for macro-level execution capability."""
        orchestrator_path = self.src_root / "orchestration" / "orchestrator.py"
        
        audit = ComponentAudit(
            component_name="Orchestrator",
            component_path=str(orchestrator_path),
            exists=orchestrator_path.exists()
        )
        
        if not audit.exists:
            audit.findings.append(AuditFinding(
                capability="orchestrator_existence",
                component="Orchestrator",
                severity=AuditSeverity.CRITICAL,
                status=CapabilityStatus.MISSING,
                description="Orchestrator file not found",
                recommendation="Create orchestrator.py with macro-level execution"
            ))
            return audit
        
        # Read source
        source = orchestrator_path.read_text()
        
        # Check for macro question handling
        has_macro_eval = "_evaluate_macro" in source or "macro_question" in source
        audit.capabilities["macro_evaluation"] = (
            CapabilityStatus.PRESENT if has_macro_eval else CapabilityStatus.MISSING
        )
        
        if has_macro_eval:
            audit.findings.append(AuditFinding(
                capability="macro_evaluation",
                component="Orchestrator",
                severity=AuditSeverity.INFO,
                status=CapabilityStatus.PRESENT,
                description="Orchestrator has macro evaluation capability",
                evidence=["_evaluate_macro method found" if "_evaluate_macro" in source else "macro_question reference found"]
            ))
        else:
            audit.findings.append(AuditFinding(
                capability="macro_evaluation",
                component="Orchestrator",
                severity=AuditSeverity.HIGH,
                status=CapabilityStatus.MISSING,
                description="Orchestrator lacks macro evaluation method",
                recommendation="Implement _evaluate_macro method for holistic assessment"
            ))
        
        # Check for PA×DIM awareness
        has_policy_areas = "PA01" in source or "policy_area" in source
        has_dimensions = "DIM01" in source or "dimension" in source
        has_pa_dim = has_policy_areas and has_dimensions
        audit.capabilities["pa_dim_awareness"] = (
            CapabilityStatus.PRESENT if has_pa_dim else CapabilityStatus.MISSING
        )
        
        if has_pa_dim:
            audit.findings.append(AuditFinding(
                capability="pa_dim_awareness",
                component="Orchestrator",
                severity=AuditSeverity.INFO,
                status=CapabilityStatus.PRESENT,
                description="Orchestrator is PA×DIM aware",
                evidence=["Policy area and dimension references found"]
            ))
        else:
            audit.findings.append(AuditFinding(
                capability="pa_dim_awareness",
                component="Orchestrator",
                severity=AuditSeverity.MEDIUM,
                status=CapabilityStatus.MISSING,
                description="Orchestrator lacks PA×DIM awareness",
                recommendation="Add policy area and dimension tracking"
            ))
        
        # Check for macro result aggregation
        has_aggregation = "MacroEvaluation" in source or "macro_result" in source
        audit.capabilities["macro_aggregation"] = (
            CapabilityStatus.PRESENT if has_aggregation else CapabilityStatus.MISSING
        )
        
        if has_aggregation:
            audit.findings.append(AuditFinding(
                capability="macro_aggregation",
                component="Orchestrator",
                severity=AuditSeverity.INFO,
                status=CapabilityStatus.PRESENT,
                description="Orchestrator can aggregate macro results",
                evidence=["MacroEvaluation or macro_result found"]
            ))
        else:
            audit.findings.append(AuditFinding(
                capability="macro_aggregation",
                component="Orchestrator",
                severity=AuditSeverity.HIGH,
                status=CapabilityStatus.MISSING,
                description="Orchestrator cannot aggregate macro results",
                recommendation="Implement macro result aggregation from meso questions"
            ))
        
        return audit
    
    def audit_carver(self) -> ComponentAudit:
        """Audit Carver for macro-level synthesis capability."""
        carver_path = self.src_root / "canonic_phases" / "Phase_two" / "carver.py"
        
        audit = ComponentAudit(
            component_name="Carver",
            component_path=str(carver_path),
            exists=carver_path.exists()
        )
        
        if not audit.exists:
            audit.findings.append(AuditFinding(
                capability="carver_existence",
                component="Carver",
                severity=AuditSeverity.CRITICAL,
                status=CapabilityStatus.MISSING,
                description="Carver file not found",
                recommendation="Create carver.py for answer synthesis"
            ))
            return audit
        
        # Read source
        source = carver_path.read_text()
        
        # Check for dimension support
        has_dimensions = "Dimension" in source and ("D1_INSUMOS" in source or "DIM01" in source)
        audit.capabilities["dimension_support"] = (
            CapabilityStatus.PRESENT if has_dimensions else CapabilityStatus.MISSING
        )
        
        if has_dimensions:
            audit.findings.append(AuditFinding(
                capability="dimension_support",
                component="Carver",
                severity=AuditSeverity.INFO,
                status=CapabilityStatus.PRESENT,
                description="Carver supports 6 dimensions (D1-D6)",
                evidence=["Dimension enum found with D1_INSUMOS or DIM01"]
            ))
        else:
            audit.findings.append(AuditFinding(
                capability="dimension_support",
                component="Carver",
                severity=AuditSeverity.CRITICAL,
                status=CapabilityStatus.MISSING,
                description="Carver lacks dimension support",
                recommendation="Add Dimension enum with DIM01-DIM06"
            ))
        
        # Check for gap analysis
        has_gap_analysis = "GapAnalyzer" in source or "gap" in source.lower()
        audit.capabilities["gap_analysis"] = (
            CapabilityStatus.PRESENT if has_gap_analysis else CapabilityStatus.MISSING
        )
        
        if has_gap_analysis:
            audit.findings.append(AuditFinding(
                capability="gap_analysis",
                component="Carver",
                severity=AuditSeverity.INFO,
                status=CapabilityStatus.PRESENT,
                description="Carver can identify gaps in evidence",
                evidence=["GapAnalyzer or gap references found"]
            ))
        else:
            audit.findings.append(AuditFinding(
                capability="gap_analysis",
                component="Carver",
                severity=AuditSeverity.HIGH,
                status=CapabilityStatus.MISSING,
                description="Carver cannot identify gaps",
                recommendation="Implement GapAnalyzer for divergence identification"
            ))
        
        # Check for divergence/coverage analysis
        has_divergence = "divergen" in source.lower() or "coverage" in source.lower()
        audit.capabilities["divergence_analysis"] = (
            CapabilityStatus.PRESENT if has_divergence else CapabilityStatus.MISSING
        )
        
        if has_divergence:
            audit.findings.append(AuditFinding(
                capability="divergence_analysis",
                component="Carver",
                severity=AuditSeverity.INFO,
                status=CapabilityStatus.PRESENT,
                description="Carver can analyze divergence/coverage",
                evidence=["Divergence or coverage references found"]
            ))
        else:
            audit.findings.append(AuditFinding(
                capability="divergence_analysis",
                component="Carver",
                severity=AuditSeverity.HIGH,
                status=CapabilityStatus.MISSING,
                description="Carver lacks divergence analysis",
                recommendation="Add divergence calculation between plan and PA×DIM matrix"
            ))
        
        # Check for macro-level synthesis
        has_macro_synthesis = "MacroQuestion" in source or "holistic" in source.lower()
        audit.capabilities["macro_synthesis"] = (
            CapabilityStatus.PRESENT if has_macro_synthesis else CapabilityStatus.PARTIAL
        )
        
        if has_macro_synthesis:
            audit.findings.append(AuditFinding(
                capability="macro_synthesis",
                component="Carver",
                severity=AuditSeverity.INFO,
                status=CapabilityStatus.PRESENT,
                description="Carver supports macro-level synthesis",
                evidence=["MacroQuestion or holistic assessment references found"]
            ))
        else:
            audit.findings.append(AuditFinding(
                capability="macro_synthesis",
                component="Carver",
                severity=AuditSeverity.MEDIUM,
                status=CapabilityStatus.PARTIAL,
                description="Carver may not fully support macro synthesis",
                recommendation="Extend Carver to handle macro-level holistic assessment"
            ))
        
        return audit
    
    def audit_phase_three(self) -> ComponentAudit:
        """Audit Phase Three for scoring and aggregation."""
        phase_three_path = self.src_root / "canonic_phases" / "Phase_three"
        
        audit = ComponentAudit(
            component_name="Phase Three",
            component_path=str(phase_three_path),
            exists=phase_three_path.exists()
        )
        
        if not audit.exists:
            audit.findings.append(AuditFinding(
                capability="phase_three_existence",
                component="Phase Three",
                severity=AuditSeverity.MEDIUM,
                status=CapabilityStatus.MISSING,
                description="Phase Three directory not found",
                recommendation="Phase Three exists but may be minimal - check implementation"
            ))
            return audit
        
        # Check for scoring module
        scoring_path = phase_three_path / "scoring.py"
        has_scoring = scoring_path.exists()
        audit.capabilities["scoring_module"] = (
            CapabilityStatus.PRESENT if has_scoring else CapabilityStatus.MISSING
        )
        
        if has_scoring:
            source = scoring_path.read_text()
            audit.findings.append(AuditFinding(
                capability="scoring_module",
                component="Phase Three",
                severity=AuditSeverity.INFO,
                status=CapabilityStatus.PRESENT,
                description="Phase Three has scoring module",
                evidence=[f"scoring.py exists at {scoring_path}"]
            ))
            
            # Check for macro scoring
            has_macro_scoring = "macro" in source.lower() or "holistic" in source.lower()
            if has_macro_scoring:
                audit.metadata["macro_scoring"] = True
        else:
            audit.findings.append(AuditFinding(
                capability="scoring_module",
                component="Phase Three",
                severity=AuditSeverity.MEDIUM,
                status=CapabilityStatus.MISSING,
                description="Phase Three lacks dedicated scoring",
                recommendation="Implement macro-level scoring aggregation"
            ))
        
        return audit
    
    def audit_questionnaire(self) -> ComponentAudit:
        """Audit questionnaire structure for macro question definition."""
        questionnaire_path = self.repo_root / "canonic_questionnaire_central" / "questionnaire_monolith.json"
        
        audit = ComponentAudit(
            component_name="Questionnaire",
            component_path=str(questionnaire_path),
            exists=questionnaire_path.exists()
        )
        
        if not audit.exists:
            audit.findings.append(AuditFinding(
                capability="questionnaire_existence",
                component="Questionnaire",
                severity=AuditSeverity.CRITICAL,
                status=CapabilityStatus.MISSING,
                description="Questionnaire monolith not found",
                recommendation="Create questionnaire_monolith.json with macro question"
            ))
            return audit
        
        # Load and analyze
        try:
            canonical_questionnaire = get_canonical_questionnaire(
                questionnaire_path=questionnaire_path,
            )
            questionnaire = canonical_questionnaire.data
        except Exception as e:
            audit.findings.append(AuditFinding(
                capability="questionnaire_parseable",
                component="Questionnaire",
                severity=AuditSeverity.CRITICAL,
                status=CapabilityStatus.MISSING,
                description=f"Questionnaire load failed: {str(e)}",
                recommendation="Fix questionnaire_monolith.json"
            ))
            return audit
        
        # Check for macro question
        blocks = questionnaire.get("blocks", {})
        macro_question = blocks.get("macro_question", {})
        
        has_macro_q = bool(macro_question)
        audit.capabilities["macro_question_defined"] = (
            CapabilityStatus.PRESENT if has_macro_q else CapabilityStatus.MISSING
        )
        
        if has_macro_q:
            audit.findings.append(AuditFinding(
                capability="macro_question_defined",
                component="Questionnaire",
                severity=AuditSeverity.INFO,
                status=CapabilityStatus.PRESENT,
                description="Macro question is defined in questionnaire",
                evidence=[
                    f"Question ID: {macro_question.get('question_id', 'N/A')}",
                    f"Text: {macro_question.get('text', 'N/A')[:100]}..."
                ]
            ))
            
            audit.metadata["macro_question"] = {
                "question_id": macro_question.get("question_id"),
                "type": macro_question.get("type"),
                "aggregation_method": macro_question.get("aggregation_method"),
                "scoring_modality": macro_question.get("scoring_modality"),
            }
            
            # Check aggregation method
            agg_method = macro_question.get("aggregation_method")
            if agg_method == "holistic_assessment":
                audit.findings.append(AuditFinding(
                    capability="holistic_aggregation",
                    component="Questionnaire",
                    severity=AuditSeverity.INFO,
                    status=CapabilityStatus.PRESENT,
                    description="Macro question uses holistic assessment",
                    evidence=[f"aggregation_method: {agg_method}"]
                ))
            else:
                audit.findings.append(AuditFinding(
                    capability="holistic_aggregation",
                    component="Questionnaire",
                    severity=AuditSeverity.MEDIUM,
                    status=CapabilityStatus.PARTIAL,
                    description=f"Macro question uses {agg_method}, not holistic",
                    recommendation="Consider holistic_assessment for macro evaluation"
                ))
        else:
            audit.findings.append(AuditFinding(
                capability="macro_question_defined",
                component="Questionnaire",
                severity=AuditSeverity.CRITICAL,
                status=CapabilityStatus.MISSING,
                description="No macro question defined in questionnaire",
                recommendation="Add macro_question to blocks with holistic assessment"
            ))
        
        return audit
    
    def audit_types(self) -> ComponentAudit:
        """Audit type system for macro-level data structures."""
        types_path = self.src_root / "farfan_pipeline" / "core" / "types.py"
        
        audit = ComponentAudit(
            component_name="Types",
            component_path=str(types_path),
            exists=types_path.exists()
        )
        
        if not audit.exists:
            audit.findings.append(AuditFinding(
                capability="types_existence",
                component="Types",
                severity=AuditSeverity.CRITICAL,
                status=CapabilityStatus.MISSING,
                description="Types file not found",
                recommendation="Create types.py with macro-level data structures"
            ))
            return audit
        
        # Read source
        source = types_path.read_text()
        
        # Check for MacroQuestionResult
        has_macro_result = "MacroQuestionResult" in source
        audit.capabilities["macro_result_type"] = (
            CapabilityStatus.PRESENT if has_macro_result else CapabilityStatus.MISSING
        )
        
        if has_macro_result:
            audit.findings.append(AuditFinding(
                capability="macro_result_type",
                component="Types",
                severity=AuditSeverity.INFO,
                status=CapabilityStatus.PRESENT,
                description="MacroQuestionResult type is defined",
                evidence=["MacroQuestionResult class found"]
            ))
        else:
            audit.findings.append(AuditFinding(
                capability="macro_result_type",
                component="Types",
                severity=AuditSeverity.HIGH,
                status=CapabilityStatus.MISSING,
                description="MacroQuestionResult type is missing",
                recommendation="Define MacroQuestionResult dataclass"
            ))
        
        # Check for PA×DIM coverage matrix
        has_coverage_matrix = "coverage_matrix" in source
        audit.capabilities["coverage_matrix_type"] = (
            CapabilityStatus.PRESENT if has_coverage_matrix else CapabilityStatus.MISSING
        )
        
        if has_coverage_matrix:
            audit.findings.append(AuditFinding(
                capability="coverage_matrix_type",
                component="Types",
                severity=AuditSeverity.INFO,
                status=CapabilityStatus.PRESENT,
                description="Coverage matrix type is defined",
                evidence=["coverage_matrix field found"]
            ))
        else:
            audit.findings.append(AuditFinding(
                capability="coverage_matrix_type",
                component="Types",
                severity=AuditSeverity.MEDIUM,
                status=CapabilityStatus.MISSING,
                description="Coverage matrix type not explicitly defined",
                recommendation="Add coverage_matrix field for PA×DIM tracking"
            ))
        
        # Check for PolicyArea enum
        has_policy_area = "PolicyArea" in source and "PA01" in source
        audit.capabilities["policy_area_enum"] = (
            CapabilityStatus.PRESENT if has_policy_area else CapabilityStatus.MISSING
        )
        
        if has_policy_area:
            audit.findings.append(AuditFinding(
                capability="policy_area_enum",
                component="Types",
                severity=AuditSeverity.INFO,
                status=CapabilityStatus.PRESENT,
                description="PolicyArea enum (PA01-PA10) is defined",
                evidence=["PolicyArea enum found"]
            ))
        
        # Check for DimensionCausal enum
        has_dimension = "DimensionCausal" in source and "DIM01" in source
        audit.capabilities["dimension_enum"] = (
            CapabilityStatus.PRESENT if has_dimension else CapabilityStatus.MISSING
        )
        
        if has_dimension:
            audit.findings.append(AuditFinding(
                capability="dimension_enum",
                component="Types",
                severity=AuditSeverity.INFO,
                status=CapabilityStatus.PRESENT,
                description="DimensionCausal enum (DIM01-DIM06) is defined",
                evidence=["DimensionCausal enum found"]
            ))
        
        return audit
    
    def audit_pa_dim_matrix(self) -> Dict[str, Any]:
        """Audit PA×DIM matrix coverage capability."""
        result = {
            "capability": "pa_dim_matrix_coverage",
            "description": "Ability to track and analyze PA×DIM matrix (10×6 = 60 cells)",
            "findings": []
        }
        
        # Expected matrix: 10 PA × 6 DIM = 60 cells
        policy_areas = [f"PA{i:02d}" for i in range(1, 11)]
        dimensions = [f"DIM{i:02d}" for i in range(1, 7)]
        
        result["expected_cells"] = 60
        result["policy_areas"] = policy_areas
        result["dimensions"] = dimensions
        
        # Check if PA×DIM matrix is tracked in types
        types_path = self.src_root / "farfan_pipeline" / "core" / "types.py"
        if types_path.exists():
            source = types_path.read_text()
            
            # Check for 60 chunks invariant
            has_60_chunks = "60 chunks" in source.lower() or "10 PA × 6 DIM" in source or "10 PA x 6 DIM" in source
            result["has_60_chunks_invariant"] = has_60_chunks
            
            if has_60_chunks:
                result["findings"].append({
                    "status": "PRESENT",
                    "description": "60 chunks (PA×DIM) invariant documented",
                    "evidence": "Found reference to 60 chunks or 10×6 matrix"
                })
            else:
                result["findings"].append({
                    "status": "MISSING",
                    "severity": "MEDIUM",
                    "description": "60 chunks invariant not documented",
                    "recommendation": "Document PA×DIM matrix invariant"
                })
            
            # Check for coverage matrix tracking
            has_coverage_tracking = "coverage_matrix" in source
            result["has_coverage_tracking"] = has_coverage_tracking
            
            if has_coverage_tracking:
                result["findings"].append({
                    "status": "PRESENT",
                    "description": "Coverage matrix tracking capability found",
                    "evidence": "coverage_matrix field exists"
                })
            else:
                result["findings"].append({
                    "status": "MISSING",
                    "severity": "HIGH",
                    "description": "No coverage matrix tracking",
                    "recommendation": "Add coverage_matrix field for PA×DIM tracking"
                })
        
        # Check for divergence analysis methods
        carver_path = self.src_root / "canonic_phases" / "Phase_two" / "carver.py"
        if carver_path.exists():
            source = carver_path.read_text()
            
            has_gap_analysis = "GapAnalyzer" in source
            result["has_gap_analysis"] = has_gap_analysis
            
            if has_gap_analysis:
                result["findings"].append({
                    "status": "PRESENT",
                    "description": "Gap analysis capability found in Carver",
                    "evidence": "GapAnalyzer class exists"
                })
        
        return result
    
    def print_summary(self):
        """Print audit summary."""
        print("=" * 80)
        print("AUDIT SUMMARY")
        print("=" * 80)
        print()
        print(f"Timestamp: {self.report.timestamp.isoformat()}")
        print(f"Macro-Level Ready: {'✓ YES' if self.report.macro_level_ready else '✗ NO'}")
        print(f"Overall Score: {self.report.overall_score:.1%}")
        print()
        print(f"Total Capabilities Checked: {self.report.total_capabilities_checked}")
        print(f"  Present: {self.report.capabilities_present} ({self.report.capabilities_present/self.report.total_capabilities_checked*100:.0f}%)")
        print(f"  Partial: {self.report.capabilities_partial}")
        print(f"  Missing: {self.report.capabilities_missing}")
        print()
        print(f"Critical Findings: {len(self.report.critical_findings)}")
        if self.report.critical_findings:
            print("\nCRITICAL ISSUES:")
            for finding in self.report.critical_findings:
                print(f"  • [{finding.component}] {finding.description}")
                if finding.recommendation:
                    print(f"    → {finding.recommendation}")
        print()
        print("=" * 80)


def main():
    """Run the macro-level divergence audit."""
    repo_root = Path(__file__).parent
    
    auditor = MacroLevelAuditor(repo_root)
    report = auditor.run_full_audit()
    
    # Save report to JSON
    output_path = repo_root / "audit_macro_level_divergence_report.json"
    with open(output_path, "w") as f:
        json.dump(report.to_dict(), f, indent=2)
    
    print(f"\nFull report saved to: {output_path}")
    
    # Exit with appropriate code
    exit_code = 0 if report.macro_level_ready else 1
    return exit_code


if __name__ == "__main__":
    exit(main())

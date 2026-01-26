# phase8_32_00_transformation_pipeline.py - 8-Step Transformation Pipeline
"""
Module: src.farfan_pipeline.phases.Phase_08.phase8_32_00_transformation_pipeline
Purpose: Orchestrates the complete 8-step transformation from FARFAN diagnostics to PDM recommendations
Owner: phase8_enhanced
Stage: 32 (Pipeline Orchestrator)
Order: 00
Type: ORCHESTRATOR
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2026-01-26

═══════════════════════════════════════════════════════════════════════════════════
    🔄 TRANSFORMATION PIPELINE - FARFAN to PDM Orchestrator 🔄
═══════════════════════════════════════════════════════════════════════════════════

TRANSFORMATION PIPELINE (8 STEPS):
    Step 1: Data Synthesis & Problem Tree Construction
    Step 2: Objective Formulation (Objetivo General + Específicos)
    Step 3: Capacity Assessment & Binding Constraint Identification
    Step 4: Instrument Selection Matched to Capacity
    Step 5: Product & Activity Specification
    Step 6: Resource Allocation & Timeline Specification
    Step 7: Narrative Generation (Lenguaje Claro)
    Step 8: Quality Verification

ORCHESTRATION FLOW:
    FARFAN Diagnostic Data
        ↓ (Step 1)
    Problem Tree
        ↓ (Step 2)
    Objectives (General + Específicos)
        ↓ (Step 3)
    Capacity Profile + Binding Constraints
        ↓ (Step 4)
    Instrument Mixes (by Objective)
        ↓ (Step 5)
    Value Chain Structure (Products + Activities)
        ↓ (Step 6)
    Budget + Timeline + Legal Compliance
        ↓ (Step 7)
    Prose Recommendation
        ↓ (Step 8)
    Quality-Verified PDM Recommendation

KEY FEATURES:
    1. End-to-end orchestration of all transformation steps
    2. Dependency management between steps
    3. Error handling and validation at each step
    4. Full traceability from FARFAN question to final recommendation
    5. Quality gates with automated feedback loops

INTEGRATION:
    - Coordinates phase8_27 (capacity framework)
    - Coordinates phase8_28 (instruments)
    - Coordinates phase8_29 (value chain)
    - Coordinates phase8_30 (legal framework)
    - Coordinates phase8_31 (narrative generation)
    - Feeds dimensional recommendation engine (phase8_26)

Author: F.A.R.F.A.N Architecture Team
Python: 3.10+
═══════════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 8
__stage__ = 32
__order__ = 0
__author__ = "F.A.R.F.A.N Architecture Team"
__created__ = "2026-01-26"
__modified__ = "2026-01-26"
__criticality__ = "CRITICAL"
__execution_pattern__ = "On-Demand"
__codename__ = "TRANSFORMATION-PIPELINE"

# =============================================================================
# IMPORTS
# =============================================================================

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .phase8_27_00_policy_capacity_framework import (
    PolicyCapacityFramework,
    ComprehensiveCapacityProfile,
    CapacityDimension,
)
from .phase8_28_00_howlett_instruments import (
    InstrumentSelectionEngine,
    InstrumentMix,
)
from .phase8_29_00_value_chain_integration import (
    build_value_chain_from_farfan,
    ValueChainStructure,
    ValueChainValidator,
)
from .phase8_30_00_colombian_legal_framework import (
    ColombianLegalFrameworkEngine,
    MunicipalCategory,
    PDMCompliance,
)
from .phase8_31_00_narrative_generation import (
    NarrativeGenerator,
    ProseRecommendation,
)

logger = logging.getLogger(__name__)

# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    "TransformationPipeline",
    "PipelineResult",
    "StepResult",
    "transform_farfan_to_pdm",
]

# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass
class StepResult:
    """Result of a single pipeline step"""
    step_number: int
    step_name: str
    success: bool
    output: Any
    errors: list[str]
    warnings: list[str]
    duration_seconds: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineResult:
    """Complete pipeline execution result"""
    municipality_id: str
    policy_area: str
    dimension: str
    
    # Step results
    steps: list[StepResult]
    
    # Final outputs
    capacity_profile: ComprehensiveCapacityProfile | None
    value_chain: ValueChainStructure | None
    prose_recommendation: ProseRecommendation | None
    pdm_compliance: PDMCompliance | None
    
    # Overall status
    success: bool
    quality_score: float  # 0.0-100.0
    total_duration_seconds: float
    
    # Traceability
    farfan_questions: list[str]
    evidence_used: list[str]
    legal_frameworks: list[str]
    
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# TRANSFORMATION PIPELINE
# =============================================================================


class TransformationPipeline:
    """
    Orchestrates the complete 8-step transformation pipeline.
    
    Transforms FARFAN diagnostic data into PDM-ready, capacity-calibrated,
    legally-compliant, prose recommendations.
    """
    
    def __init__(self):
        """Initialize transformation pipeline with all components"""
        self.capacity_framework = PolicyCapacityFramework()
        self.instrument_engine = InstrumentSelectionEngine()
        self.legal_engine = ColombianLegalFrameworkEngine()
        self.narrative_generator = NarrativeGenerator()
        
        logger.info("Transformation Pipeline initialized")
    
    def transform(
        self,
        municipality_id: str,
        municipality_category: MunicipalCategory,
        policy_area: str,
        dimension: str,
        farfan_diagnostic: dict[str, Any],
        capacity_evidence: dict[CapacityDimension, list[str]]
    ) -> PipelineResult:
        """
        Execute complete transformation pipeline.
        
        Args:
            municipality_id: Municipality identifier
            municipality_category: Municipal category (1-6)
            policy_area: Policy area (PA01-PA10)
            dimension: Dimension (DIM01-DIM06)
            farfan_diagnostic: FARFAN diagnostic data with scores and evidence
            capacity_evidence: Evidence for 9-dimensional capacity assessment
            
        Returns:
            PipelineResult with complete transformation outputs
        """
        start_time = datetime.now(timezone.utc)
        steps = []
        
        # Step 1: Data Synthesis & Problem Tree
        step1 = self._step1_data_synthesis(farfan_diagnostic, policy_area)
        steps.append(step1)
        if not step1.success:
            return self._create_failed_result(municipality_id, policy_area, dimension, steps, start_time)
        
        problem_tree = step1.output
        
        # Step 2: Objective Formulation
        step2 = self._step2_objective_formulation(problem_tree, policy_area)
        steps.append(step2)
        if not step2.success:
            return self._create_failed_result(municipality_id, policy_area, dimension, steps, start_time)
        
        objectives = step2.output
        
        # Step 3: Capacity Assessment
        step3 = self._step3_capacity_assessment(
            municipality_id, municipality_category.value, capacity_evidence
        )
        steps.append(step3)
        if not step3.success:
            return self._create_failed_result(municipality_id, policy_area, dimension, steps, start_time)
        
        capacity_profile = step3.output
        
        # Step 4: Instrument Selection
        step4 = self._step4_instrument_selection(
            objectives, capacity_profile, municipality_category.value, policy_area, dimension
        )
        steps.append(step4)
        if not step4.success:
            return self._create_failed_result(municipality_id, policy_area, dimension, steps, start_time)
        
        instrument_mixes = step4.output
        
        # Step 5: Product & Activity Specification
        step5 = self._step5_product_activity_specification(
            municipality_id, policy_area, dimension, farfan_diagnostic, instrument_mixes
        )
        steps.append(step5)
        if not step5.success:
            return self._create_failed_result(municipality_id, policy_area, dimension, steps, start_time)
        
        value_chain = step5.output
        
        # Step 6: Resource Allocation & Timeline
        step6 = self._step6_resource_timeline(
            value_chain, instrument_mixes, municipality_category, policy_area
        )
        steps.append(step6)
        if not step6.success:
            return self._create_failed_result(municipality_id, policy_area, dimension, steps, start_time)
        
        pdm_compliance = step6.output
        
        # Step 7: Narrative Generation
        step7 = self._step7_narrative_generation(
            value_chain, instrument_mixes, capacity_profile, municipality_category
        )
        steps.append(step7)
        if not step7.success:
            return self._create_failed_result(municipality_id, policy_area, dimension, steps, start_time)
        
        prose_recommendation = step7.output
        
        # Step 8: Quality Verification
        step8 = self._step8_quality_verification(
            prose_recommendation, value_chain, pdm_compliance
        )
        steps.append(step8)
        
        quality_score = step8.output if step8.success else 0.0
        
        # Calculate total duration
        end_time = datetime.now(timezone.utc)
        total_duration = (end_time - start_time).total_seconds()
        
        # Collect traceability info
        farfan_questions = farfan_diagnostic.get("questions", [])
        evidence_used = farfan_diagnostic.get("evidence", [])
        legal_frameworks = self.legal_engine.get_legal_obligations(policy_area)
        legal_framework_names = [lf.law_number for lf in legal_frameworks]
        
        return PipelineResult(
            municipality_id=municipality_id,
            policy_area=policy_area,
            dimension=dimension,
            steps=steps,
            capacity_profile=capacity_profile,
            value_chain=value_chain,
            prose_recommendation=prose_recommendation,
            pdm_compliance=pdm_compliance,
            success=all(step.success for step in steps),
            quality_score=quality_score,
            total_duration_seconds=total_duration,
            farfan_questions=farfan_questions,
            evidence_used=evidence_used,
            legal_frameworks=legal_framework_names,
            metadata={
                "pipeline_version": __version__,
                "municipality_category": municipality_category.value,
                "timestamp": end_time.isoformat()
            }
        )
    
    def _step1_data_synthesis(
        self,
        farfan_diagnostic: dict[str, Any],
        policy_area: str
    ) -> StepResult:
        """Step 1: Data synthesis and problem tree construction"""
        start = datetime.now(timezone.utc)
        
        try:
            from .phase8_29_00_value_chain_integration import _construct_problem_tree
            
            problem_tree = _construct_problem_tree(farfan_diagnostic, policy_area)
            
            duration = (datetime.now(timezone.utc) - start).total_seconds()
            
            return StepResult(
                step_number=1,
                step_name="Data Synthesis & Problem Tree",
                success=True,
                output=problem_tree,
                errors=[],
                warnings=[],
                duration_seconds=duration
            )
            
        except Exception as e:
            logger.error(f"Step 1 failed: {e}")
            duration = (datetime.now(timezone.utc) - start).total_seconds()
            
            return StepResult(
                step_number=1,
                step_name="Data Synthesis & Problem Tree",
                success=False,
                output=None,
                errors=[str(e)],
                warnings=[],
                duration_seconds=duration
            )
    
    def _step2_objective_formulation(
        self,
        problem_tree: Any,
        policy_area: str
    ) -> StepResult:
        """Step 2: Objective formulation"""
        start = datetime.now(timezone.utc)
        
        try:
            from .phase8_29_00_value_chain_integration import (
                _formulate_objetivo_general,
                _formulate_objetivos_especificos
            )
            
            objetivo_general = _formulate_objetivo_general(problem_tree, policy_area)
            objetivos_especificos = _formulate_objetivos_especificos(
                problem_tree, objetivo_general
            )
            
            duration = (datetime.now(timezone.utc) - start).total_seconds()
            
            return StepResult(
                step_number=2,
                step_name="Objective Formulation",
                success=True,
                output={
                    "general": objetivo_general,
                    "especificos": objetivos_especificos
                },
                errors=[],
                warnings=[],
                duration_seconds=duration
            )
            
        except Exception as e:
            logger.error(f"Step 2 failed: {e}")
            duration = (datetime.now(timezone.utc) - start).total_seconds()
            
            return StepResult(
                step_number=2,
                step_name="Objective Formulation",
                success=False,
                output=None,
                errors=[str(e)],
                warnings=[],
                duration_seconds=duration
            )
    
    def _step3_capacity_assessment(
        self,
        municipality_id: str,
        municipality_category: int,
        capacity_evidence: dict[CapacityDimension, list[str]]
    ) -> StepResult:
        """Step 3: Capacity assessment and binding constraint identification"""
        start = datetime.now(timezone.utc)
        
        try:
            capacity_profile = self.capacity_framework.create_comprehensive_profile(
                municipality_id=municipality_id,
                municipality_category=municipality_category,
                assessments=capacity_evidence
            )
            
            duration = (datetime.now(timezone.utc) - start).total_seconds()
            
            warnings = []
            if capacity_profile.binding_constraints:
                warnings.append(
                    f"Found {len(capacity_profile.binding_constraints)} binding constraints"
                )
            
            return StepResult(
                step_number=3,
                step_name="Capacity Assessment",
                success=True,
                output=capacity_profile,
                errors=[],
                warnings=warnings,
                duration_seconds=duration
            )
            
        except Exception as e:
            logger.error(f"Step 3 failed: {e}")
            duration = (datetime.now(timezone.utc) - start).total_seconds()
            
            return StepResult(
                step_number=3,
                step_name="Capacity Assessment",
                success=False,
                output=None,
                errors=[str(e)],
                warnings=[],
                duration_seconds=duration
            )
    
    def _step4_instrument_selection(
        self,
        objectives: dict[str, Any],
        capacity_profile: ComprehensiveCapacityProfile,
        municipality_category: int,
        policy_area: str,
        dimension: str
    ) -> StepResult:
        """Step 4: Instrument selection matched to capacity"""
        start = datetime.now(timezone.utc)
        
        try:
            instrument_mixes = {}
            
            for obj_esp in objectives["especificos"]:
                instrument_mix = self.instrument_engine.select_instrument_mix(
                    objective=obj_esp.text,
                    problem=obj_esp.cause_addressed,
                    capacity_profile=capacity_profile,
                    municipality_category=municipality_category,
                    policy_area=policy_area,
                    dimension=dimension
                )
                instrument_mixes[obj_esp.text] = instrument_mix
            
            duration = (datetime.now(timezone.utc) - start).total_seconds()
            
            return StepResult(
                step_number=4,
                step_name="Instrument Selection",
                success=True,
                output=instrument_mixes,
                errors=[],
                warnings=[],
                duration_seconds=duration
            )
            
        except Exception as e:
            logger.error(f"Step 4 failed: {e}")
            duration = (datetime.now(timezone.utc) - start).total_seconds()
            
            return StepResult(
                step_number=4,
                step_name="Instrument Selection",
                success=False,
                output=None,
                errors=[str(e)],
                warnings=[],
                duration_seconds=duration
            )
    
    def _step5_product_activity_specification(
        self,
        municipality_id: str,
        policy_area: str,
        dimension: str,
        farfan_diagnostic: dict[str, Any],
        instrument_mixes: dict[str, InstrumentMix]
    ) -> StepResult:
        """Step 5: Product and activity specification"""
        start = datetime.now(timezone.utc)
        
        try:
            value_chain = build_value_chain_from_farfan(
                municipality_id=municipality_id,
                policy_area=policy_area,
                dimension=dimension,
                farfan_diagnostic=farfan_diagnostic,
                instrument_mixes=instrument_mixes
            )
            
            duration = (datetime.now(timezone.utc) - start).total_seconds()
            
            warnings = []
            if not value_chain.is_valid:
                warnings.append(f"Value chain validation issues: {value_chain.validation_report}")
            
            return StepResult(
                step_number=5,
                step_name="Product & Activity Specification",
                success=True,
                output=value_chain,
                errors=[],
                warnings=warnings,
                duration_seconds=duration
            )
            
        except Exception as e:
            logger.error(f"Step 5 failed: {e}")
            duration = (datetime.now(timezone.utc) - start).total_seconds()
            
            return StepResult(
                step_number=5,
                step_name="Product & Activity Specification",
                success=False,
                output=None,
                errors=[str(e)],
                warnings=[],
                duration_seconds=duration
            )
    
    def _step6_resource_timeline(
        self,
        value_chain: ValueChainStructure,
        instrument_mixes: dict[str, InstrumentMix],
        municipality_category: MunicipalCategory,
        policy_area: str
    ) -> StepResult:
        """Step 6: Resource allocation and timeline specification"""
        start = datetime.now(timezone.utc)
        
        try:
            # Validate PDM compliance
            pdm_compliance = self.legal_engine.validate_pdm_compliance(
                value_chain=value_chain,
                municipality_category=municipality_category,
                policy_area=policy_area
            )
            
            duration = (datetime.now(timezone.utc) - start).total_seconds()
            
            warnings = []
            if not pdm_compliance.legal_compliance:
                warnings.append("Legal compliance issues found")
            if not pdm_compliance.financing_feasibility:
                warnings.append("Financing feasibility concerns")
            
            return StepResult(
                step_number=6,
                step_name="Resource Allocation & Timeline",
                success=True,
                output=pdm_compliance,
                errors=[],
                warnings=warnings,
                duration_seconds=duration
            )
            
        except Exception as e:
            logger.error(f"Step 6 failed: {e}")
            duration = (datetime.now(timezone.utc) - start).total_seconds()
            
            return StepResult(
                step_number=6,
                step_name="Resource Allocation & Timeline",
                success=False,
                output=None,
                errors=[str(e)],
                warnings=[],
                duration_seconds=duration
            )
    
    def _step7_narrative_generation(
        self,
        value_chain: ValueChainStructure,
        instrument_mixes: dict[str, InstrumentMix],
        capacity_profile: ComprehensiveCapacityProfile,
        municipality_category: MunicipalCategory
    ) -> StepResult:
        """Step 7: Narrative generation with Lenguaje Claro"""
        start = datetime.now(timezone.utc)
        
        try:
            prose_recommendation = self.narrative_generator.generate_prose_recommendation(
                value_chain=value_chain,
                instrument_mixes=instrument_mixes,
                capacity_profile=capacity_profile,
                municipality_category=municipality_category
            )
            
            duration = (datetime.now(timezone.utc) - start).total_seconds()
            
            warnings = []
            if prose_recommendation.carver_compliance_score < 70:
                warnings.append(
                    f"Low Carver compliance score: {prose_recommendation.carver_compliance_score}"
                )
            
            return StepResult(
                step_number=7,
                step_name="Narrative Generation",
                success=True,
                output=prose_recommendation,
                errors=[],
                warnings=warnings,
                duration_seconds=duration
            )
            
        except Exception as e:
            logger.error(f"Step 7 failed: {e}")
            duration = (datetime.now(timezone.utc) - start).total_seconds()
            
            return StepResult(
                step_number=7,
                step_name="Narrative Generation",
                success=False,
                output=None,
                errors=[str(e)],
                warnings=[],
                duration_seconds=duration
            )
    
    def _step8_quality_verification(
        self,
        prose_recommendation: ProseRecommendation,
        value_chain: ValueChainStructure,
        pdm_compliance: PDMCompliance
    ) -> StepResult:
        """Step 8: Quality verification"""
        start = datetime.now(timezone.utc)
        
        try:
            # Calculate quality score (0-100)
            quality_components = {
                "carver_compliance": prose_recommendation.carver_compliance_score,
                "value_chain_valid": 100.0 if value_chain.is_valid else 0.0,
                "legal_compliance": 100.0 if pdm_compliance.legal_compliance else 0.0,
                "financing_feasible": 100.0 if pdm_compliance.financing_feasibility else 0.0,
            }
            
            # Weighted average
            quality_score = (
                quality_components["carver_compliance"] * 0.4 +
                quality_components["value_chain_valid"] * 0.3 +
                quality_components["legal_compliance"] * 0.2 +
                quality_components["financing_feasible"] * 0.1
            )
            
            duration = (datetime.now(timezone.utc) - start).total_seconds()
            
            return StepResult(
                step_number=8,
                step_name="Quality Verification",
                success=True,
                output=quality_score,
                errors=[],
                warnings=[],
                duration_seconds=duration,
                metadata=quality_components
            )
            
        except Exception as e:
            logger.error(f"Step 8 failed: {e}")
            duration = (datetime.now(timezone.utc) - start).total_seconds()
            
            return StepResult(
                step_number=8,
                step_name="Quality Verification",
                success=False,
                output=0.0,
                errors=[str(e)],
                warnings=[],
                duration_seconds=duration
            )
    
    def _create_failed_result(
        self,
        municipality_id: str,
        policy_area: str,
        dimension: str,
        steps: list[StepResult],
        start_time: datetime
    ) -> PipelineResult:
        """Create a failed pipeline result"""
        end_time = datetime.now(timezone.utc)
        total_duration = (end_time - start_time).total_seconds()
        
        return PipelineResult(
            municipality_id=municipality_id,
            policy_area=policy_area,
            dimension=dimension,
            steps=steps,
            capacity_profile=None,
            value_chain=None,
            prose_recommendation=None,
            pdm_compliance=None,
            success=False,
            quality_score=0.0,
            total_duration_seconds=total_duration,
            farfan_questions=[],
            evidence_used=[],
            legal_frameworks=[],
            metadata={
                "failure_reason": f"Pipeline failed at step {len(steps)}",
                "timestamp": end_time.isoformat()
            }
        )


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================


def transform_farfan_to_pdm(
    municipality_id: str,
    municipality_category: MunicipalCategory,
    policy_area: str,
    dimension: str,
    farfan_diagnostic: dict[str, Any],
    capacity_evidence: dict[CapacityDimension, list[str]]
) -> PipelineResult:
    """
    Convenience function to execute complete transformation pipeline.
    
    Args:
        municipality_id: Municipality identifier
        municipality_category: Municipal category
        policy_area: Policy area (PA01-PA10)
        dimension: Dimension (DIM01-DIM06)
        farfan_diagnostic: FARFAN diagnostic data
        capacity_evidence: Capacity assessment evidence
        
    Returns:
        PipelineResult with complete transformation
    """
    pipeline = TransformationPipeline()
    return pipeline.transform(
        municipality_id=municipality_id,
        municipality_category=municipality_category,
        policy_area=policy_area,
        dimension=dimension,
        farfan_diagnostic=farfan_diagnostic,
        capacity_evidence=capacity_evidence
    )

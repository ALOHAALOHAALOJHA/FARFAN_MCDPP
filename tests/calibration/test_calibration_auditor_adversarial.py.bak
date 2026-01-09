"""
ADVERSARIAL TESTS FOR CALIBRATION AUDITOR
=========================================
Tests N3-AUD veto and drift detection for calibration manifest.
"""
import pytest
from datetime import datetime, timezone, timedelta
from src.farfan_pipeline.infrastructure.calibration.calibration_manifest import (
    CalibrationManifest, ManifestBuilder, CalibrationDecision
)
from src.farfan_pipeline.infrastructure.calibration.calibration_core import (
    CalibrationLayer, CalibrationPhase, CalibrationParameter,
    ClosedInterval, EvidenceReference
)
from src.farfan_pipeline.infrastructure.calibration.calibration_auditor import (
    CalibrationAuditor, AuditResult
)
from src.farfan_pipeline.infrastructure.calibration.unit_of_analysis import (
    UnitOfAnalysis, MunicipalityCategory, FiscalContext
)

def create_dummy_manifest(contract_type, ingestion_prior, phase2_prior, phase2_veto, decisions=None):
    uoa = UnitOfAnalysis(
        municipality_code="05001",
        municipality_name="Medellín",
        department_code="05",
        population=2500000,
        total_budget_cop=1000000000,
        category=MunicipalityCategory.CATEGORIA_ESPECIAL,
        sgp_percentage=20.0,
        own_revenue_percentage=80.0,
        fiscal_context=FiscalContext.HIGH_CAPACITY,
        plan_period_start=2024,
        plan_period_end=2027,
        policy_area_codes=frozenset(["PA01"])
    )
    
    now = datetime.now(timezone.utc)
    future = now + timedelta(days=90)
    
    def create_layer(phase, prior, veto):
        params = [
            CalibrationParameter(
                name="prior_strength", value=prior, unit="dimensionless",
                bounds=ClosedInterval(0.0, 10.0), rationale="Test",
                evidence=EvidenceReference("docs/README.md", "a"*40, "desc"),
                calibrated_at=now, expires_at=future
            ),
            CalibrationParameter(
                name="veto_threshold", value=veto, unit="dimensionless",
                bounds=ClosedInterval(0.0, 1.0), rationale="Test",
                evidence=EvidenceReference("docs/README.md", "a"*40, "desc"),
                calibrated_at=now, expires_at=future
            ),
            CalibrationParameter(
                name="chunk_size", value=2000.0, unit="tokens",
                bounds=ClosedInterval(100.0, 10000.0), rationale="Test",
                evidence=EvidenceReference("docs/README.md", "a"*40, "desc"),
                calibrated_at=now, expires_at=future
            ),
            CalibrationParameter(
                name="extraction_coverage_target", value=0.85, unit="fraction",
                bounds=ClosedInterval(0.0, 1.0), rationale="Test",
                evidence=EvidenceReference("docs/README.md", "a"*40, "desc"),
                calibrated_at=now, expires_at=future
            )
        ]
        return CalibrationLayer(
            unit_of_analysis_id="DANE-05001",
            phase=phase,
            contract_type_code=contract_type,
            parameters=tuple(params),
            created_at=now
        )

    ing_layer = create_layer(CalibrationPhase.INGESTION, ingestion_prior, 0.05)
    ph2_layer = create_layer(CalibrationPhase.PHASE_2_COMPUTATION, phase2_prior, phase2_veto)
    
    builder = ManifestBuilder("TEST-CONTRACT", uoa)
    builder.with_contract_type(contract_type)
    builder.with_ingestion_layer(ing_layer)
    builder.with_phase2_layer(ph2_layer)
    
    if decisions:
        for d in decisions:
            builder.add_decision(d)
            
    return builder.build()

def test_prior_strength_out_of_bounds_triggers_veto() -> None:
    # Construct a manifest with invalid prior strength (0.05 < 0.1 min)
    # Note: Layer bounds are [0.0, 10.0], so 0.05 passes layer validation
    # but fails Auditor specification [0.1, 10.0]
    manifest = create_dummy_manifest(
        contract_type="TYPE_A",
        ingestion_prior=0.05,
        phase2_prior=0.05,
        phase2_veto=0.05
    )
    auditor = CalibrationAuditor()
    audit_result = auditor.audit(manifest)
    assert not audit_result.passed
    assert audit_result.veto_triggered
    assert any("prior strength" in v.message.lower() for v in audit_result.violations)

def test_veto_threshold_mismatch_triggers_veto() -> None:
    # Use a veto_threshold outside of spec for TYPE_A (Standard: 0.03-0.07)
    # 0.99 is invalid
    manifest = create_dummy_manifest(
        contract_type="TYPE_A",
        ingestion_prior=1.0,
        phase2_prior=1.0,
        phase2_veto=0.99
    )
    auditor = CalibrationAuditor()
    audit_result = auditor.audit(manifest)
    assert not audit_result.passed
    assert audit_result.veto_triggered
    assert any("veto threshold" in v.message.lower() for v in audit_result.violations)

def test_fusion_strategy_uses_prohibited_operation_triggers_veto() -> None:
    # TYPE_A prohibits "weighted_mean"
    decision = CalibrationDecision(
        decision_id="dec1",
        parameter_name="weighted_mean",
        chosen_value=1.0,
        alternative_values=(0.5, 2.0),
        rationale="Prohibited fuse for TYPE_A",
        source_evidence="src/farfan_pipeline/methods/test.py",
        decision_timestamp=datetime.now(timezone.utc),
    )
    
    manifest = create_dummy_manifest(
        contract_type="TYPE_A",
        ingestion_prior=1.0,
        phase2_prior=1.0,
        phase2_veto=0.05,
        decisions=[decision]
    )
    
    auditor = CalibrationAuditor()
    audit_result = auditor.audit(manifest)
    assert not audit_result.passed
    assert audit_result.veto_triggered
    assert any("prohibited operation" in v.message.lower() for v in audit_result.violations)

def test_drift_detection_flags_severe_coverage_drift() -> None:
    auditor = CalibrationAuditor()
    manifest = create_dummy_manifest(
        contract_type="TYPE_A",
        ingestion_prior=1.0,
        phase2_prior=1.0,
        phase2_veto=0.05
    )
    
    # 10% coverage vs expected 0.95 -> 0.85 deviation -> FATAL
    runtime_observations = [{"covered": False}]*9 + [{"covered": True}]*1 
    
    report = auditor.audit_drift(
        manifest=manifest,
        runtime_observations=runtime_observations,
        expected_coverage=0.95,
        expected_credible_width=None,
    )
    assert report.drift_detected
    assert any(di.severity == "FATAL" for di in report.indicators)

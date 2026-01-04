from datetime import datetime, timezone, timedelta
from src.farfan_pipeline.infrastructure.calibration.calibration_manifest import (
    ManifestBuilder,
    CalibrationDecision,
    CalibrationManifest
)
from src.farfan_pipeline.infrastructure.calibration.calibration_core import (
    CalibrationLayer,
    CalibrationPhase,
    CalibrationParameter,
    ClosedInterval,
    EvidenceReference
)
from src.farfan_pipeline.infrastructure.calibration.unit_of_analysis import (
    UnitOfAnalysis,
    MunicipalityCategory,
    FiscalContext
)

def create_dummy_layer(phase, uoa_id):
    now = datetime.now(timezone.utc)
    future = now + timedelta(days=90)
    
    param = CalibrationParameter(
        name="prior_strength",
        value=0.5,
        unit="dimensionless",
        bounds=ClosedInterval(0.0, 1.0),
        rationale="Default",
        evidence=EvidenceReference("docs/README.md", "a" * 40, "desc"),
        calibrated_at=now,
        expires_at=future
    )
    # We need to include all required params to pass validation if we were strict,
    # but here we just need a layer object. However, CalibrationLayer validates required params.
    # REQUIRED_PARAMETER_NAMES: prior_strength, veto_threshold, chunk_size, extraction_coverage_target
    
    params = [
        CalibrationParameter(
            name=name,
            value=val,
            unit="dimensionless",
            bounds=ClosedInterval(0.0, 10000.0),
            rationale="Default",
            evidence=EvidenceReference("docs/README.md", "a" * 40, "desc"),
            calibrated_at=now,
            expires_at=future
        )
        for name, val in [
            ("prior_strength", 0.5),
            ("veto_threshold", 0.3),
            ("chunk_size", 2000.0),
            ("extraction_coverage_target", 0.85)
        ]
    ]

    return CalibrationLayer(
        unit_of_analysis_id=uoa_id,
        phase=phase,
        contract_type_code="PDT",
        parameters=tuple(params),
        created_at=now
    )

def test_manifest_builder():
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
    
    ingestion_layer = create_dummy_layer(CalibrationPhase.INGESTION, "DANE-05001")
    phase2_layer = create_dummy_layer(CalibrationPhase.PHASE_2_COMPUTATION, "DANE-05001")
    
    builder = ManifestBuilder("CONTRACT-123", uoa)
    builder.with_contract_type("PDT")
    builder.with_ingestion_layer(ingestion_layer)
    builder.with_phase2_layer(phase2_layer)
    
    decision = CalibrationDecision(
        decision_id="DEC-001",
        parameter_name="prior_strength",
        chosen_value=0.6,
        alternative_values=(0.4, 0.5),
        rationale="Higher confidence needed",
        source_evidence="Expert review",
        decision_timestamp=datetime.now(timezone.utc)
    )
    builder.add_decision(decision)
    
    manifest = builder.build()
    
    assert isinstance(manifest, CalibrationManifest)
    assert manifest.contract_id == "CONTRACT-123"
    assert len(manifest.decisions) == 1
    assert manifest.compute_hash() is not None

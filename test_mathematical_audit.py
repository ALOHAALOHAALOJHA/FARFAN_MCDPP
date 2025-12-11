"""
Tests para el auditor matemático de scoring macro

Verifica que el auditor ejecuta correctamente y produce reportes válidos.
"""

import json
import os
import pytest
from audit_mathematical_scoring_macro import (
    MacroScoringMathematicalAuditor,
    MathematicalCheck,
    AuditReport,
)


def test_auditor_initialization():
    """Test que el auditor se inicializa correctamente"""
    auditor = MacroScoringMathematicalAuditor()
    assert auditor.report.total_checks == 0
    assert auditor.report.passed_checks == 0
    assert auditor.report.failed_checks == 0


def test_weighted_average_audit():
    """Test auditoría de weighted average"""
    auditor = MacroScoringMathematicalAuditor()
    checks = auditor.audit_weighted_average()
    
    assert len(checks) > 0
    assert all(isinstance(check, MathematicalCheck) for check in checks)
    assert any(check.check_id == "WA-001" for check in checks)
    assert any(check.procedure_name == "weighted_average" for check in checks)


def test_choquet_integral_audit():
    """Test auditoría de Choquet integral"""
    auditor = MacroScoringMathematicalAuditor()
    checks = auditor.audit_choquet_integral()
    
    assert len(checks) > 0
    assert any(check.check_id == "CI-001" for check in checks)
    assert any(check.check_id == "CI-002" for check in checks)
    assert any("choquet" in check.procedure_name.lower() for check in checks)


def test_coherence_audit():
    """Test auditoría de cálculo de coherence"""
    auditor = MacroScoringMathematicalAuditor()
    checks = auditor.audit_coherence_calculation()
    
    assert len(checks) > 0
    assert any(check.check_id == "COH-001" for check in checks)
    assert any("variance" in check.procedure_name.lower() or "coherence" in check.procedure_name.lower() for check in checks)


def test_penalty_factor_audit():
    """Test auditoría de penalty factor"""
    auditor = MacroScoringMathematicalAuditor()
    checks = auditor.audit_penalty_factor()
    
    assert len(checks) > 0
    assert any(check.check_id == "PF-001" for check in checks)
    assert any("penalty" in check.procedure_name.lower() for check in checks)


def test_threshold_application_audit():
    """Test auditoría de aplicación de umbrales"""
    auditor = MacroScoringMathematicalAuditor()
    checks = auditor.audit_threshold_application()
    
    assert len(checks) > 0
    assert any(check.check_id == "TH-001" for check in checks)
    assert any("threshold" in check.procedure_name.lower() for check in checks)


def test_weight_normalization_audit():
    """Test auditoría de normalización de pesos"""
    auditor = MacroScoringMathematicalAuditor()
    checks = auditor.audit_weight_normalization()
    
    assert len(checks) > 0
    assert any(check.check_id == "WN-001" for check in checks)
    assert any("normalization" in check.procedure_name.lower() for check in checks)


def test_score_normalization_audit():
    """Test auditoría de normalización de scores"""
    auditor = MacroScoringMathematicalAuditor()
    checks = auditor.audit_score_normalization()
    
    assert len(checks) > 0
    assert any(check.check_id == "SN-001" for check in checks)


def test_complete_audit_execution():
    """Test ejecución completa de auditoría"""
    auditor = MacroScoringMathematicalAuditor()
    report = auditor.run_complete_audit()
    
    # Verificar estructura del reporte
    assert isinstance(report, AuditReport)
    assert report.total_checks > 0
    assert report.total_checks == report.passed_checks + report.failed_checks
    assert len(report.all_checks) == report.total_checks
    
    # Verificar que todos los checks están clasificados
    total_issues = (
        len(report.critical_issues) +
        len(report.high_issues) +
        len(report.medium_issues) +
        len(report.low_issues)
    )
    assert total_issues == report.failed_checks


def test_report_generation(tmp_path):
    """Test generación de reportes"""
    auditor = MacroScoringMathematicalAuditor()
    auditor.run_complete_audit()
    
    # Generar reporte Markdown
    md_path = tmp_path / "test_report.md"
    auditor.generate_detailed_report(str(md_path))
    assert md_path.exists()
    assert md_path.stat().st_size > 0
    
    # Verificar contenido básico
    content = md_path.read_text(encoding="utf-8")
    assert "Auditoría Matemática" in content
    assert "Resumen Ejecutivo" in content
    assert "Weighted Average" in content
    
    # Generar reporte JSON
    json_path = tmp_path / "test_report.json"
    auditor.generate_json_report(str(json_path))
    assert json_path.exists()
    
    # Verificar estructura JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert "summary" in data
    assert "checks" in data
    assert data["summary"]["total_checks"] > 0
    assert isinstance(data["checks"], list)


def test_all_checks_have_required_fields():
    """Test que todos los checks tienen los campos requeridos"""
    auditor = MacroScoringMathematicalAuditor()
    report = auditor.run_complete_audit()
    
    for check in report.all_checks:
        assert check.check_id
        assert check.procedure_name
        assert check.description
        assert check.severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        assert isinstance(check.passed, bool)
        assert isinstance(check.details, dict)
        assert check.recommendation


def test_severity_levels_present():
    """Test que hay checks de todas las severidades"""
    auditor = MacroScoringMathematicalAuditor()
    report = auditor.run_complete_audit()
    
    severities = {check.severity for check in report.all_checks}
    
    # Debe haber checks de severidad CRITICAL y HIGH al menos
    assert "CRITICAL" in severities
    assert "HIGH" in severities


def test_mathematical_formulas_documented():
    """Test que todas las fórmulas matemáticas están documentadas"""
    auditor = MacroScoringMathematicalAuditor()
    report = auditor.run_complete_audit()
    
    # Verificar que checks críticos tienen fórmulas documentadas
    critical_checks = [c for c in report.all_checks if c.severity == "CRITICAL"]
    
    for check in critical_checks:
        # Checks críticos deben tener al menos uno de estos campos
        has_formula = (
            "formula" in check.details or
            "implementation" in check.details or
            "validation" in check.details
        )
        assert has_formula, f"Check {check.check_id} missing formula documentation"


def test_audit_produces_expected_check_count():
    """Test que la auditoría produce el número esperado de verificaciones"""
    auditor = MacroScoringMathematicalAuditor()
    report = auditor.run_complete_audit()
    
    # Debe haber al menos 20 verificaciones (ajustar según implementación real)
    assert report.total_checks >= 20
    
    # Verificar cobertura mínima por área
    check_ids = {check.check_id for check in report.all_checks}
    
    # Weighted Average
    assert any(cid.startswith("WA-") for cid in check_ids)
    
    # Choquet Integral
    assert any(cid.startswith("CI-") for cid in check_ids)
    
    # Coherence
    assert any(cid.startswith("COH-") for cid in check_ids)
    
    # Penalty Factor
    assert any(cid.startswith("PF-") for cid in check_ids)
    
    # Thresholds
    assert any(cid.startswith("TH-") for cid in check_ids)
    
    # Weight Normalization
    assert any(cid.startswith("WN-") for cid in check_ids)
    
    # Score Normalization
    assert any(cid.startswith("SN-") for cid in check_ids)


def test_no_duplicate_check_ids():
    """Test que no hay check_ids duplicados"""
    auditor = MacroScoringMathematicalAuditor()
    report = auditor.run_complete_audit()
    
    check_ids = [check.check_id for check in report.all_checks]
    assert len(check_ids) == len(set(check_ids)), "Duplicate check_ids found"


def test_report_summary_consistency():
    """Test consistencia en el resumen del reporte"""
    auditor = MacroScoringMathematicalAuditor()
    report = auditor.run_complete_audit()
    
    # La suma de passed + failed debe igualar total
    assert report.passed_checks + report.failed_checks == report.total_checks
    
    # La suma de issues por severidad debe igualar failed_checks
    total_issues = (
        len(report.critical_issues) +
        len(report.high_issues) +
        len(report.medium_issues) +
        len(report.low_issues)
    )
    assert total_issues == report.failed_checks


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

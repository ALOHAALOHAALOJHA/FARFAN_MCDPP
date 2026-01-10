"""Lightweight validation tests for report generation
These tests validate the structure and implementation without requiring
full dependency installation.
"""

import sys
from pathlib import Path

# Add src to path
def test_no_stub_in_report_generator():
    """Verify report_generator has no stub responses."""
    code = Path("src/farfan_pipeline/phases/Phase_nine/report_generator.py").read_text()
    
    # Should not have stub status
    assert 'status": "stub"' not in code, "report_generator contains stub response"
    assert '"stub"' not in code.lower() or "# stub" in code.lower(), "Unexpected stub in report_generator"
    
    print("✓ report_generator has no stub responses")


def test_required_functions_present():
    """Verify all required functions are present."""
    code = Path("src/farfan_pipeline/phases/Phase_nine/report_generator.py").read_text()
    
    required_functions = [
        "generate_markdown_report",
        "generate_html_report",
        "generate_pdf_report",
        "generate_charts",
        "compute_file_sha256",
        "ReportGenerator",
    ]
    
    for func in required_functions:
        assert f"def {func}" in code or f"class {func}" in code, f"Missing {func}"
        print(f"✓ Found: {func}")


def test_orchestrator_phase9_not_stub():
    """Verify Phase 9 in orchestrator is not stub."""
    code = Path("src/farfan_pipeline/orchestration/orchestrator.py").read_text()
    
    # Find Phase 9 method
    phase9_start = code.find("def _assemble_report(")
    assert phase9_start > 0, "Phase 9 method not found"
    
    phase9_end = code.find("def _format_and_export", phase9_start)
    phase9_code = code[phase9_start:phase9_end]
    
    # Should not have stub warning
    assert "logger.warning" not in phase9_code or "stub" not in phase9_code, "Phase 9 still has stub warning"
    assert '"stub"' not in phase9_code, "Phase 9 returns stub status"
    
    # Should use ReportAssembler
    assert "ReportAssembler" in phase9_code, "Phase 9 does not use ReportAssembler"
    assert "assemble_report" in phase9_code, "Phase 9 does not call assemble_report"
    
    print("✓ Phase 9 has real implementation")


def test_orchestrator_phase10_not_stub():
    """Verify Phase 10 in orchestrator is not stub."""
    code = Path("src/farfan_pipeline/orchestration/orchestrator.py").read_text()
    
    # Find Phase 10 method
    phase10_start = code.find("async def _format_and_export(")
    assert phase10_start > 0, "Phase 10 method not found"
    
    # Get Phase 10 code (until next method or end)
    next_method = code.find("\n    def ", phase10_start + 50)
    if next_method == -1:
        next_method = code.find("\n    async def ", phase10_start + 50)
    phase10_end = next_method if next_method > 0 else len(code)
    phase10_code = code[phase10_start:phase10_end]
    
    # Should not have stub warning
    assert not ("logger.warning" in phase10_code and "stub" in phase10_code), "Phase 10 still has stub warning"
    assert '"stub"' not in phase10_code, "Phase 10 returns stub status"
    
    # Should use ReportGenerator
    assert "ReportGenerator" in phase10_code, "Phase 10 does not use ReportGenerator"
    assert "generate_all" in phase10_code, "Phase 10 does not call generate_all"
    
    # Should generate multiple formats
    assert "generate_pdf=True" in phase10_code, "Phase 10 does not generate PDF"
    assert "generate_html=True" in phase10_code, "Phase 10 does not generate HTML"
    assert "generate_markdown=True" in phase10_code, "Phase 10 does not generate Markdown"
    
    print("✓ Phase 10 has real implementation with all formats")


def test_html_template_exists():
    """Verify HTML template exists and has required structure."""
    template_path = Path("src/farfan_pipeline/phases/Phase_nine/templates/report.html.j2")
    assert template_path.exists(), "HTML template not found"
    
    template_content = template_path.read_text()
    
    # Check for required sections
    required = [
        "<!DOCTYPE html>",
        "<title>Reporte de Análisis de Política",
        "Resumen Ejecutivo",
        "Recomendaciones Estratégicas",
        "Análisis Meso",
        "Análisis Micro",
        "Trazabilidad",
        "{{ metadata.plan_name }}",
        "{% if macro_summary %}",
        "<style>",
    ]
    
    for item in required:
        assert item in template_content, f"Template missing: {item}"
    
    # Check template size (should be substantial)
    assert len(template_content) > 5000, "Template too small"
    
    print(f"✓ HTML template valid ({len(template_content)} bytes)")


def test_requirements_updated():
    """Verify requirements.txt includes new dependencies."""
    requirements = Path("requirements.txt").read_text().lower()
    
    required_packages = [
        "weasyprint",
        "jinja2",
        "markdown",
        "matplotlib",
        "pillow",
    ]
    
    for package in required_packages:
        assert package in requirements, f"Missing package: {package}"
        print(f"✓ Found: {package}")


def test_config_includes_artifacts_dir():
    """Verify orchestrator config includes artifacts_dir."""
    code = Path("src/farfan_pipeline/orchestration/orchestrator.py").read_text()
    
    # Find _load_configuration method
    config_start = code.find("def _load_configuration(")
    assert config_start > 0, "_load_configuration not found"
    
    config_end = code.find("def _ingest_document(", config_start)
    config_code = code[config_start:config_end]
    
    # Should set artifacts_dir
    assert "artifacts_dir" in config_code, "Config does not include artifacts_dir"
    assert "plan_name" in config_code, "Config does not include plan_name"
    
    print("✓ Config includes artifacts_dir and plan_name")


if __name__ == "__main__":
    print("=" * 70)
    print("Report Generation Validation Tests")
    print("=" * 70)
    
    tests = [
        test_no_stub_in_report_generator,
        test_required_functions_present,
        test_orchestrator_phase9_not_stub,
        test_orchestrator_phase10_not_stub,
        test_html_template_exists,
        test_requirements_updated,
        test_config_includes_artifacts_dir,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        print(f"\n[{test.__name__}]")
        try:
            test()
            passed += 1
            print(f"✅ PASSED")
        except AssertionError as e:
            failed += 1
            print(f"❌ FAILED: {e}")
        except Exception as e:
            failed += 1
            print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    sys.exit(0 if failed == 0 else 1)

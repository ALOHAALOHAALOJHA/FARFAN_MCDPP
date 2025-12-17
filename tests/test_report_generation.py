"""Tests for Report Generation (Phases 9-10)
=============================================

Tests for real report generation replacing stub implementations.

Test Coverage:
- Unit: Template rendering and formatting
- Unit: Markdown generation
- Integration: Full pipeline PDF generation
- Regression: No stub responses
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Mark as updated test
pytestmark = pytest.mark.updated


class TestReportGenerator:
    """Unit tests for ReportGenerator module."""
    
    def test_markdown_generation(self, tmp_path):
        """Test structured Markdown report generation."""
        from farfan_pipeline.phases.Phase_nine.report_assembly import (
            AnalysisReport,
            ReportMetadata,
            QuestionAnalysis,
            MesoCluster,
            MacroSummary,
            Recommendation,
        )
        from farfan_pipeline.phases.Phase_nine.report_generator import (
            generate_markdown_report,
        )
        
        # Create test report
        metadata = ReportMetadata(
            report_id="test-001",
            monolith_version="1.0",
            monolith_hash="a" * 64,
            plan_name="test_plan",
            total_questions=10,
            questions_analyzed=10,
        )
        
        micro_analyses = [
            QuestionAnalysis(
                question_id=f"Q{i:03d}",
                question_global=i,
                base_slot=f"slot{i}",
                score=0.8,
                patterns_applied=[f"pattern{j}" for j in range(3)],
                human_answer=f"Esta es una respuesta de prueba Carver-style para la pregunta Q{i:03d}. La evidencia muestra resultados claros. Los datos confirman la tendencia.",
                metadata={"dimension": "DIM1", "policy_area": "PA1"},
            )
            for i in range(1, 11)
        ]
        
        meso_cluster = MesoCluster(
            cluster_id="CL01",
            raw_meso_score=0.8,
            adjusted_score=0.75,
            dispersion_penalty=0.05,
            peer_penalty=0.0,
            total_penalty=0.05,
            micro_scores=[0.8, 0.75, 0.82],
        )
        
        macro_summary = MacroSummary(
            overall_posterior=0.75,
            adjusted_score=0.7,
            coverage_penalty=0.05,
            dispersion_penalty=0.0,
            contradiction_penalty=0.0,
            total_penalty=0.05,
            contradiction_count=0,
            recommendations=[
                Recommendation(
                    type="RISK",
                    severity="HIGH",
                    description="Test recommendation",
                    source="macro"
                )
            ],
        )
        
        report = AnalysisReport(
            metadata=metadata,
            micro_analyses=micro_analyses,
            meso_clusters={"CL01": meso_cluster},
            macro_summary=macro_summary,
        )
        
        # Generate Markdown
        markdown = generate_markdown_report(report)
        
        # Assertions
        assert "# Reporte de Análisis de Política: test_plan" in markdown
        assert "test-001" in markdown
        assert "Resumen Ejecutivo" in markdown
        assert "70.00%" in markdown  # adjusted_score * 100
        assert "Recomendaciones Estratégicas" in markdown
        assert "Test recommendation" in markdown
        assert "Análisis Meso: Clústeres" in markdown
        assert "CL01" in markdown
        assert "Análisis Micro: Preguntas" in markdown
        assert "Q001" in markdown
        assert len(markdown) > 1000  # Should be substantial
    
    def test_html_template_rendering(self, tmp_path):
        """Test HTML report generation using Jinja2 templates."""
        from farfan_pipeline.phases.Phase_nine.report_assembly import (
            AnalysisReport,
            ReportMetadata,
            QuestionAnalysis,
        )
        from farfan_pipeline.phases.Phase_nine.report_generator import (
            generate_html_report,
        )
        
        # Create minimal report
        metadata = ReportMetadata(
            report_id="test-html",
            monolith_version="1.0",
            monolith_hash="b" * 64,
            plan_name="html_test",
            total_questions=5,
            questions_analyzed=5,
        )
        
        micro_analyses = [
            QuestionAnalysis(
                question_id="Q001",
                question_global=1,
                base_slot="slot1",
                score=0.9,
            )
        ]
        
        report = AnalysisReport(
            metadata=metadata,
            micro_analyses=micro_analyses,
        )
        
        # Generate HTML
        html = generate_html_report(report)
        
        # Assertions
        assert "<!DOCTYPE html>" in html
        assert "test-html" in html
        assert "html_test" in html
        assert "Q001" in html
        assert "0.9" in html or "0.9000" in html
        assert len(html) > 5000  # Template should be substantial
    
    @pytest.mark.skipif(
        True,  # Skip by default as WeasyPrint has system dependencies
        reason="WeasyPrint requires system libraries (cairo, pango)"
    )
    def test_pdf_generation(self, tmp_path):
        """Test PDF generation from HTML content."""
        from farfan_pipeline.phases.Phase_nine.report_generator import (
            generate_pdf_report,
        )
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Test PDF</title></head>
        <body><h1>Test Report</h1><p>This is a test.</p></body>
        </html>
        """
        
        pdf_path = tmp_path / "test_report.pdf"
        
        # Generate PDF
        generate_pdf_report(html_content, pdf_path)
        
        # Assertions
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 100  # PDF should have content
        assert pdf_path.suffix == ".pdf"
    
    def test_chart_generation(self, tmp_path):
        """Test chart generation for score distributions."""
        from farfan_pipeline.phases.Phase_nine.report_assembly import (
            AnalysisReport,
            ReportMetadata,
            QuestionAnalysis,
            MesoCluster,
        )
        from farfan_pipeline.phases.Phase_nine.report_generator import (
            generate_charts,
        )
        
        # Create report with data for charts
        metadata = ReportMetadata(
            report_id="test-charts",
            monolith_version="1.0",
            monolith_hash="c" * 64,
            plan_name="chart_test",
            total_questions=20,
            questions_analyzed=20,
        )
        
        # Create micro analyses with varying scores
        micro_analyses = [
            QuestionAnalysis(
                question_id=f"Q{i:03d}",
                question_global=i,
                base_slot=f"slot{i}",
                score=0.5 + (i * 0.02),  # Varying scores
            )
            for i in range(1, 21)
        ]
        
        # Create meso clusters
        meso_clusters = {
            f"CL{i:02d}": MesoCluster(
                cluster_id=f"CL{i:02d}",
                raw_meso_score=0.6 + (i * 0.05),
                adjusted_score=0.55 + (i * 0.05),
                dispersion_penalty=0.05,
                peer_penalty=0.0,
                total_penalty=0.05,
                micro_scores=[0.6] * 5,
            )
            for i in range(1, 5)
        }
        
        report = AnalysisReport(
            metadata=metadata,
            micro_analyses=micro_analyses,
            meso_clusters=meso_clusters,
        )
        
        # Generate charts
        chart_paths = generate_charts(report, tmp_path, "chart_test")
        
        # Assertions
        assert len(chart_paths) >= 1  # At least score distribution
        for chart_path in chart_paths:
            assert chart_path.exists()
            assert chart_path.suffix == ".png"
            assert chart_path.stat().st_size > 1000  # Should have content
    
    def test_manifest_generation(self, tmp_path):
        """Test manifest generation with SHA256 hashes."""
        from farfan_pipeline.phases.Phase_nine.report_assembly import (
            AnalysisReport,
            ReportMetadata,
            QuestionAnalysis,
        )
        from farfan_pipeline.phases.Phase_nine.report_generator import (
            ReportGenerator,
        )
        
        # Create minimal report
        metadata = ReportMetadata(
            report_id="test-manifest",
            monolith_version="1.0",
            monolith_hash="d" * 64,
            plan_name="manifest_test",
            total_questions=1,
            questions_analyzed=1,
        )
        
        micro_analyses = [
            QuestionAnalysis(
                question_id="Q001",
                question_global=1,
                base_slot="slot1",
                score=0.8,
            )
        ]
        
        report = AnalysisReport(
            metadata=metadata,
            micro_analyses=micro_analyses,
            report_digest="e" * 64,
        )
        
        # Generate reports
        generator = ReportGenerator(
            output_dir=tmp_path,
            plan_name="manifest_test",
            enable_charts=False,
        )
        
        artifacts = generator.generate_all(
            report=report,
            generate_pdf=False,  # Skip PDF for speed
            generate_html=True,
            generate_markdown=True,
        )
        
        # Check manifest exists
        assert "manifest" in artifacts
        manifest_path = artifacts["manifest"]
        assert manifest_path.exists()
        
        # Load and validate manifest
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        assert "generated_at" in manifest
        assert "plan_name" in manifest
        assert manifest["plan_name"] == "manifest_test"
        assert "report_id" in manifest
        assert manifest["report_id"] == "test-manifest"
        assert "artifacts" in manifest
        
        # Check artifact entries have SHA256
        for artifact_type, artifact_info in manifest["artifacts"].items():
            if artifact_type != "manifest":
                assert "sha256" in artifact_info
                assert len(artifact_info["sha256"]) == 64
                assert "size_bytes" in artifact_info
                assert artifact_info["size_bytes"] > 0


class TestOrchestratorIntegration:
    """Integration tests for orchestrator Phases 9-10."""
    
    def test_phase9_no_stub_response(self):
        """Regression test: Phase 9 should not return stub response."""
        from farfan_pipeline.phases.Phase_nine.report_assembly import (
            ReportMetadata,
            QuestionAnalysis,
            AnalysisReport,
        )
        
        # Create mock orchestrator context
        class MockOrchestrator:
            def __init__(self):
                self._context = {
                    "micro_results": {},
                    "scored_results": [],
                    "dimension_scores": [],
                    "policy_area_scores": [],
                    "cluster_scores": [],
                    "macro_result": None,
                }
        
        orchestrator = MockOrchestrator()
        
        # Mock config
        config = {
            "monolith": {
                "version": "1.0",
                "blocks": {
                    "micro_questions": [
                        {
                            "question_id": "Q001",
                            "question_global": 1,
                            "base_slot": "slot1",
                        }
                    ]
                }
            },
            "plan_name": "test_plan",
        }
        
        recommendations = {"status": "test"}
        
        # Import the actual method (we'll need to refactor to make it testable)
        # For now, we verify the logic doesn't return stub
        from farfan_pipeline.phases.Phase_nine.report_assembly import (
            ReportAssembler,
        )
        
        # Create provider
        class QuestionnaireProvider:
            def get_data(self):
                return config["monolith"]
            
            def get_patterns_by_question(self, question_id):
                return []
        
        provider = QuestionnaireProvider()
        assembler = ReportAssembler(
            questionnaire_provider=provider,
            orchestrator=orchestrator,
        )
        
        execution_results = {
            "questions": {},
            "scored_results": [],
            "dimension_scores": [],
            "policy_area_scores": [],
            "meso_clusters": [],
            "macro_summary": None,
        }
        
        # Assemble report
        report = assembler.assemble_report(
            plan_name="test_plan",
            execution_results=execution_results,
        )
        
        # Assertions: should NOT be stub
        assert isinstance(report, AnalysisReport)
        assert report.metadata.plan_name == "test_plan"
        assert report.report_digest is not None
        assert len(report.report_digest) == 64
    
    def test_phase10_artifact_generation(self, tmp_path):
        """Test Phase 10 generates all expected artifacts."""
        from farfan_pipeline.phases.Phase_nine.report_assembly import (
            AnalysisReport,
            ReportMetadata,
            QuestionAnalysis,
        )
        from farfan_pipeline.phases.Phase_nine.report_generator import (
            ReportGenerator,
        )
        
        # Create report
        metadata = ReportMetadata(
            report_id="phase10-test",
            monolith_version="1.0",
            monolith_hash="f" * 64,
            plan_name="phase10_test",
            total_questions=3,
            questions_analyzed=3,
        )
        
        micro_analyses = [
            QuestionAnalysis(
                question_id=f"Q{i:03d}",
                question_global=i,
                base_slot=f"slot{i}",
                score=0.7 + (i * 0.1),
            )
            for i in range(1, 4)
        ]
        
        report = AnalysisReport(
            metadata=metadata,
            micro_analyses=micro_analyses,
        )
        
        # Generate all artifacts
        generator = ReportGenerator(
            output_dir=tmp_path,
            plan_name="phase10_test",
            enable_charts=True,
        )
        
        artifacts = generator.generate_all(
            report=report,
            generate_pdf=False,  # Skip PDF for CI
            generate_html=True,
            generate_markdown=True,
        )
        
        # Verify expected artifacts
        assert "markdown" in artifacts
        assert "html" in artifacts
        assert "manifest" in artifacts
        
        # Verify files exist and have content
        markdown_path = artifacts["markdown"]
        assert markdown_path.exists()
        assert markdown_path.stat().st_size > 500
        
        html_path = artifacts["html"]
        assert html_path.exists()
        assert html_path.stat().st_size > 3000
        
        manifest_path = artifacts["manifest"]
        assert manifest_path.exists()
        
        # Verify manifest structure
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        assert manifest["plan_name"] == "phase10_test"
        assert "markdown" in manifest["artifacts"]
        assert "html" in manifest["artifacts"]
        
        # Verify SHA256 hashes present
        for artifact_type in ["markdown", "html"]:
            artifact_info = manifest["artifacts"][artifact_type]
            assert "sha256" in artifact_info
            assert len(artifact_info["sha256"]) == 64
            assert "size_bytes" in artifact_info


class TestReportQuality:
    """Tests for report quality and completeness."""
    
    def test_report_page_count_estimate(self, tmp_path):
        """Test that report has sufficient content for ~20 pages."""
        from farfan_pipeline.phases.Phase_nine.report_assembly import (
            AnalysisReport,
            ReportMetadata,
            QuestionAnalysis,
            MesoCluster,
            MacroSummary,
            Recommendation,
        )
        from farfan_pipeline.phases.Phase_nine.report_generator import (
            generate_markdown_report,
            generate_html_report,
        )
        
        # Create comprehensive report with realistic data
        metadata = ReportMetadata(
            report_id="quality-test",
            monolith_version="1.0",
            monolith_hash="g" * 64,
            plan_name="quality_test",
            total_questions=300,
            questions_analyzed=300,
        )
        
        # Generate 300 micro analyses
        micro_analyses = [
            QuestionAnalysis(
                question_id=f"Q{i:03d}",
                question_global=i,
                base_slot=f"slot{i}",
                score=0.5 + ((i % 50) * 0.01),
                patterns_applied=[f"pattern{j}" for j in range(5)],
                metadata={
                    "dimension": f"DIM{(i % 6) + 1}",
                    "policy_area": f"PA{(i % 10) + 1}",
                },
            )
            for i in range(1, 301)
        ]
        
        # Generate meso clusters
        meso_clusters = {
            f"CL{i:02d}": MesoCluster(
                cluster_id=f"CL{i:02d}",
                raw_meso_score=0.6 + (i * 0.01),
                adjusted_score=0.55 + (i * 0.01),
                dispersion_penalty=0.05,
                peer_penalty=0.02,
                total_penalty=0.07,
                micro_scores=[0.6 + (j * 0.01) for j in range(75)],
            )
            for i in range(1, 5)
        }
        
        # Generate macro summary with recommendations
        recommendations = [
            Recommendation(
                type="RISK",
                severity="CRITICAL",
                description=f"Critical risk {i}: Immediate action required to address policy gap in dimension X.",
                source="macro"
            )
            for i in range(1, 6)
        ] + [
            Recommendation(
                type="OPPORTUNITY",
                severity="HIGH",
                description=f"Opportunity {i}: Leverage existing framework to enhance policy area Y.",
                source="macro"
            )
            for i in range(1, 6)
        ]
        
        macro_summary = MacroSummary(
            overall_posterior=0.72,
            adjusted_score=0.68,
            coverage_penalty=0.04,
            dispersion_penalty=0.02,
            contradiction_penalty=0.01,
            total_penalty=0.07,
            contradiction_count=3,
            recommendations=recommendations,
        )
        
        report = AnalysisReport(
            metadata=metadata,
            micro_analyses=micro_analyses,
            meso_clusters=meso_clusters,
            macro_summary=macro_summary,
            report_digest="h" * 64,
            evidence_chain_hash="i" * 64,
        )
        
        # Generate Markdown
        markdown = generate_markdown_report(report)
        
        # Estimate pages: ~3000 chars per page (conservative)
        estimated_pages = len(markdown) / 3000
        
        assert estimated_pages >= 15, f"Report too short: {estimated_pages:.1f} pages estimated"
        assert len(markdown) > 40000, "Markdown should be substantial (>40KB)"
        
        # Generate HTML
        html = generate_html_report(report)
        
        # HTML should be even larger with styling
        assert len(html) > 50000, "HTML should be substantial (>50KB)"
        
        # Verify key sections present
        assert "Resumen Ejecutivo" in markdown
        assert "Recomendaciones Estratégicas" in markdown
        assert "Análisis Meso" in markdown
        assert "Análisis Micro" in markdown
        assert "Trazabilidad" in markdown


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "updated"])

"""Report Generator Module - Production Grade
==============================================

Generates comprehensive policy analysis reports in Markdown, HTML, and PDF formats.
Replaces stub implementations in Phases 9-10 with real report generation.

Key Features:
- Structured Markdown generation
- HTML rendering via Jinja2 templates
- PDF export via WeasyPrint (deterministic)
- Chart generation for score distributions
- Complete provenance tracking
- SHA256 manifest generation

Author: F.A.R.F.A.N Pipeline Team
Version: 1.0.0
Python: 3.12+
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from farfan_pipeline.phases.Phase_nine.report_assembly import AnalysisReport

logger = logging.getLogger(__name__)

__all__ = [
    "ReportGenerator",
    "generate_markdown_report",
    "generate_html_report",
    "generate_pdf_report",
    "generate_charts",
    "compute_file_sha256",
]


class ReportGenerationError(Exception):
    """Exception raised during report generation."""
    pass


class ReportGenerator:
    """Generates comprehensive policy analysis reports in multiple formats.
    
    Produces:
    - Structured Markdown reports
    - HTML reports with styling
    - PDF reports via WeasyPrint
    - Score distribution charts
    - Manifest with SHA256 hashes
    
    Attributes:
        output_dir: Directory for report artifacts
        plan_name: Name of development plan
        enable_charts: Enable chart generation
    """
    
    def __init__(
        self,
        output_dir: Path | str,
        plan_name: str = "plan1",
        enable_charts: bool = True,
    ) -> None:
        """Initialize report generator.
        
        Args:
            output_dir: Directory for output artifacts
            plan_name: Development plan name
            enable_charts: Enable chart generation
        """
        self.output_dir = Path(output_dir)
        self.plan_name = plan_name
        self.enable_charts = enable_charts
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(
            f"ReportGenerator initialized: output_dir={self.output_dir}, "
            f"plan_name={plan_name}, charts={enable_charts}"
        )
    
    def generate_all(
        self,
        report: AnalysisReport,
        generate_pdf: bool = True,
        generate_html: bool = True,
        generate_markdown: bool = True,
    ) -> dict[str, Path]:
        """Generate all report formats.
        
        Args:
            report: AnalysisReport to render
            generate_pdf: Generate PDF output
            generate_html: Generate HTML output
            generate_markdown: Generate Markdown output
            
        Returns:
            Dictionary mapping format to output path
            
        Raises:
            ReportGenerationError: If generation fails
        """
        artifacts: dict[str, Path] = {}
        
        try:
            # Generate Markdown
            if generate_markdown:
                markdown_path = self.output_dir / f"{self.plan_name}_report.md"
                markdown_content = generate_markdown_report(report)
                markdown_path.write_text(markdown_content, encoding="utf-8")
                artifacts["markdown"] = markdown_path
                logger.info(f"Generated Markdown report: {markdown_path}")
            
            # Generate charts if enabled
            chart_paths = []
            if self.enable_charts:
                chart_paths = generate_charts(
                    report,
                    output_dir=self.output_dir,
                    plan_name=self.plan_name
                )
                logger.info(f"Generated {len(chart_paths)} charts")
            
            # Generate HTML
            if generate_html:
                html_path = self.output_dir / f"{self.plan_name}_report.html"
                html_content = generate_html_report(
                    report,
                    chart_paths=chart_paths
                )
                html_path.write_text(html_content, encoding="utf-8")
                artifacts["html"] = html_path
                logger.info(f"Generated HTML report: {html_path}")
            
            # Generate PDF from HTML
            if generate_pdf:
                if not generate_html:
                    # Need HTML as intermediate
                    html_content = generate_html_report(
                        report,
                        chart_paths=chart_paths
                    )
                else:
                    html_content = html_path.read_text(encoding="utf-8")
                
                pdf_path = self.output_dir / f"{self.plan_name}_report.pdf"
                generate_pdf_report(html_content, pdf_path)
                artifacts["pdf"] = pdf_path
                logger.info(f"Generated PDF report: {pdf_path}")
            
            # Generate manifest with SHA256 hashes
            manifest_path = self.output_dir / f"{self.plan_name}_manifest.json"
            manifest = self._generate_manifest(artifacts, report)
            manifest_path.write_text(
                json.dumps(manifest, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            artifacts["manifest"] = manifest_path
            logger.info(f"Generated manifest: {manifest_path}")
            
            return artifacts
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}", exc_info=True)
            raise ReportGenerationError(
                f"Failed to generate reports: {e}"
            ) from e
    
    def _generate_manifest(
        self,
        artifacts: dict[str, Path],
        report: AnalysisReport
    ) -> dict[str, Any]:
        """Generate manifest with artifact metadata and hashes.
        
        Args:
            artifacts: Dictionary of generated artifacts
            report: AnalysisReport for metadata
            
        Returns:
            Manifest dictionary
        """
        manifest: dict[str, Any] = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "plan_name": self.plan_name,
            "report_id": report.metadata.report_id,
            "artifacts": {},
        }
        
        for artifact_type, path in artifacts.items():
            if path.exists():
                manifest["artifacts"][artifact_type] = {
                    "path": str(path.relative_to(self.output_dir)),
                    "size_bytes": path.stat().st_size,
                    "sha256": compute_file_sha256(path),
                }
        
        # Add report digest
        if report.report_digest:
            manifest["report_digest"] = report.report_digest
        
        # Add evidence chain hash
        if report.evidence_chain_hash:
            manifest["evidence_chain_hash"] = report.evidence_chain_hash
        
        return manifest


def generate_markdown_report(report: AnalysisReport) -> str:
    """Generate structured Markdown report.
    
    Args:
        report: AnalysisReport to render
        
    Returns:
        Markdown content as string
    """
    lines = [
        f"# Reporte de Análisis de Política: {report.metadata.plan_name}\n",
        "\n## Información del Reporte\n",
        f"- **ID de Reporte:** `{report.metadata.report_id}`\n",
        f"- **Generado:** {report.metadata.generated_at}\n",
        f"- **Versión de Cuestionario:** {report.metadata.monolith_version}\n",
        f"- **Hash de Cuestionario:** `{report.metadata.monolith_hash[:16]}...`\n",
        f"- **Preguntas Totales:** {report.metadata.total_questions}\n",
        f"- **Preguntas Analizadas:** {report.metadata.questions_analyzed}\n",
        "\n---\n",
    ]
    
    # Executive Summary
    lines.append("\n## Resumen Ejecutivo\n")
    if report.macro_summary:
        score_pct = report.macro_summary.adjusted_score * 100
        lines.extend([
            f"\n### Evaluación General\n",
            f"**Puntuación Global:** {score_pct:.2f}%\n",
            f"\n#### Métricas Clave\n",
            f"- Posterior Global: {report.macro_summary.overall_posterior:.4f}\n",
            f"- Puntuación Ajustada: {report.macro_summary.adjusted_score:.4f}\n",
            f"- Contradicciones Detectadas: {report.macro_summary.contradiction_count}\n",
            f"\n#### Penalizaciones\n",
            f"- Cobertura: {report.macro_summary.coverage_penalty:.4f}\n",
            f"- Dispersión: {report.macro_summary.dispersion_penalty:.4f}\n",
            f"- Contradicciones: {report.macro_summary.contradiction_penalty:.4f}\n",
            f"- Total: {report.macro_summary.total_penalty:.4f}\n",
        ])
    else:
        lines.append("*Resumen macro no disponible.*\n")
    
    # Recommendations
    if report.macro_summary and report.macro_summary.recommendations:
        lines.append("\n## Recomendaciones Estratégicas\n")
        for i, rec in enumerate(report.macro_summary.recommendations, 1):
            icon = "🔴" if rec.severity == "CRITICAL" else "🟠" if rec.severity == "HIGH" else "🟡" if rec.severity == "MEDIUM" else "🔵"
            lines.extend([
                f"\n### {i}. {icon} {rec.type} ({rec.severity})\n",
                f"{rec.description}\n",
                f"\n*Fuente: {rec.source}*\n",
            ])
    
    # Meso Clusters
    if report.meso_clusters:
        lines.append("\n---\n")
        lines.append("\n## Análisis Meso: Clústeres\n")
        lines.append(f"\nSe identificaron {len(report.meso_clusters)} clústeres.\n")
        lines.append("\n| Clúster ID | Puntuación Raw | Puntuación Ajustada | Penalización Total | # Puntuaciones Micro |\n")
        lines.append("|------------|----------------|---------------------|--------------------|-----------------------|\n")
        
        for cluster_id, cluster in sorted(report.meso_clusters.items()):
            lines.append(
                f"| {cluster_id} | {cluster.raw_meso_score:.4f} | "
                f"{cluster.adjusted_score:.4f} | {cluster.total_penalty:.4f} | "
                f"{len(cluster.micro_scores)} |\n"
            )
    
    # Micro Analysis Summary
    lines.append("\n---\n")
    lines.append("\n## Análisis Micro: Preguntas\n")
    lines.append(f"\nTotal de preguntas analizadas: {len(report.micro_analyses)}\n")
    
    # Detailed answers section - show first 10 with human answers
    lines.append("\n### Respuestas Detalladas (Primeras 10 Preguntas)\n")
    
    for i, analysis in enumerate(report.micro_analyses[:10], 1):
        dimension = analysis.metadata.get("dimension", "N/A") if analysis.metadata else "N/A"
        policy_area = analysis.metadata.get("policy_area", "N/A") if analysis.metadata else "N/A"
        score_str = f"{analysis.score:.4f}" if analysis.score is not None else "N/A"
        
        lines.append(f"\n#### {i}. {analysis.question_id} - {analysis.base_slot}\n")
        lines.append(f"**Dimensión:** {dimension} | **Área de Política:** {policy_area} | **Puntuación:** {score_str}\n")
        
        # Include human answer if available
        if analysis.human_answer:
            lines.append(f"\n**Respuesta:**\n\n{analysis.human_answer}\n")
        else:
            lines.append(f"\n*Respuesta no disponible*\n")
        
        # Show patterns if any
        if analysis.patterns_applied:
            lines.append(f"\n**Patrones aplicados:** {len(analysis.patterns_applied)}\n")
    
    # Show summary table for remaining questions
    if len(report.micro_analyses) > 10:
        lines.append(f"\n### Resumen Adicional ({len(report.micro_analyses) - 10} Preguntas)\n")
        lines.append("\n| ID | # Global | Dimensión | Área | Puntuación | Patrones |\n")
        lines.append("|----|----------|-----------|------|------------|----------|\n")
        
        for analysis in report.micro_analyses[10:30]:  # Show next 20 in table
            dimension = analysis.metadata.get("dimension", "N/A") if analysis.metadata else "N/A"
            policy_area = analysis.metadata.get("policy_area", "N/A") if analysis.metadata else "N/A"
            score_str = f"{analysis.score:.4f}" if analysis.score is not None else "N/A"
            pattern_count = len(analysis.patterns_applied)
            
            lines.append(
                f"| {analysis.question_id} | {analysis.question_global} | "
                f"{dimension} | {policy_area} | {score_str} | {pattern_count} |\n"
            )
    
        if len(report.micro_analyses) > 30:
            lines.append(f"\n*... y {len(report.micro_analyses) - 30} preguntas más*\n")
    
    # Provenance
    lines.append("\n---\n")
    lines.append("\n## Trazabilidad y Verificación\n")
    if report.report_digest:
        lines.append(f"\n- **Digest del Reporte:** `{report.report_digest}`\n")
    if report.evidence_chain_hash:
        lines.append(f"- **Hash de Cadena de Evidencia:** `{report.evidence_chain_hash}`\n")
    lines.append(f"- **Hash de Cuestionario:** `{report.metadata.monolith_hash}`\n")
    
    lines.append("\n---\n")
    lines.append("\n*Generado por F.A.R.F.A.N - Framework for Advanced Retrieval and Forensic Analysis of Administrative Narratives*\n")
    
    return "".join(lines)


def generate_html_report(
    report: AnalysisReport,
    chart_paths: list[Path] | None = None
) -> str:
    """Generate HTML report using Jinja2 template.
    
    Args:
        report: AnalysisReport to render
        chart_paths: Optional paths to chart images
        
    Returns:
        HTML content as string
    """
    try:
        from jinja2 import Environment, FileSystemLoader, select_autoescape
    except ImportError as e:
        raise ReportGenerationError(
            "Jinja2 not installed. Run: pip install jinja2"
        ) from e
    
    # Get template directory
    template_dir = Path(__file__).parent / "templates"
    
    if not template_dir.exists():
        raise ReportGenerationError(
            f"Template directory not found: {template_dir}"
        )
    
    # Setup Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(['html', 'xml'])
    )
    
    # Load template
    template = env.get_template("report.html.j2")
    
    # Prepare context
    context = {
        "metadata": {
            "report_id": report.metadata.report_id,
            "generated_at": report.metadata.generated_at,
            "plan_name": report.metadata.plan_name,
            "monolith_version": report.metadata.monolith_version,
            "monolith_hash": report.metadata.monolith_hash,
            "total_questions": report.metadata.total_questions,
            "questions_analyzed": report.metadata.questions_analyzed,
            "correlation_id": report.metadata.correlation_id,
        },
        "micro_analyses": [
            {
                "question_id": a.question_id,
                "question_global": a.question_global,
                "base_slot": a.base_slot,
                "score": a.score,
                "patterns_applied": a.patterns_applied,
                "human_answer": a.human_answer,
                "metadata": a.metadata or {},
            }
            for a in report.micro_analyses
        ],
        "meso_clusters": {
            k: {
                "cluster_id": v.cluster_id,
                "raw_meso_score": v.raw_meso_score,
                "adjusted_score": v.adjusted_score,
                "dispersion_penalty": v.dispersion_penalty,
                "peer_penalty": v.peer_penalty,
                "total_penalty": v.total_penalty,
                "micro_scores": v.micro_scores,
            }
            for k, v in report.meso_clusters.items()
        } if report.meso_clusters else {},
        "macro_summary": {
            "overall_posterior": report.macro_summary.overall_posterior,
            "adjusted_score": report.macro_summary.adjusted_score,
            "coverage_penalty": report.macro_summary.coverage_penalty,
            "dispersion_penalty": report.macro_summary.dispersion_penalty,
            "contradiction_penalty": report.macro_summary.contradiction_penalty,
            "total_penalty": report.macro_summary.total_penalty,
            "contradiction_count": report.macro_summary.contradiction_count,
            "recommendations": [
                {
                    "type": r.type,
                    "severity": r.severity,
                    "description": r.description,
                    "source": r.source,
                }
                for r in report.macro_summary.recommendations
            ],
        } if report.macro_summary else None,
        "report_digest": report.report_digest,
        "evidence_chain_hash": report.evidence_chain_hash,
        "charts": chart_paths or [],
    }
    
    # Render template
    html_content = template.render(**context)
    
    return html_content


def generate_pdf_report(html_content: str, output_path: Path) -> None:
    """Generate PDF from HTML content using WeasyPrint.
    
    Args:
        html_content: HTML content to render
        output_path: Path for output PDF
        
    Raises:
        ReportGenerationError: If PDF generation fails
    """
    try:
        from weasyprint import HTML, CSS
    except ImportError as e:
        raise ReportGenerationError(
            "WeasyPrint not installed. Run: pip install weasyprint"
        ) from e
    
    try:
        # Create PDF from HTML
        html_doc = HTML(string=html_content)
        html_doc.write_pdf(str(output_path))
        
        logger.info(f"PDF generated: {output_path} ({output_path.stat().st_size} bytes)")
        
    except Exception as e:
        logger.error(f"PDF generation failed: {e}", exc_info=True)
        raise ReportGenerationError(
            f"Failed to generate PDF: {e}"
        ) from e


def generate_charts(
    report: AnalysisReport,
    output_dir: Path,
    plan_name: str = "plan1"
) -> list[Path]:
    """Generate charts for report visualization.
    
    Args:
        report: AnalysisReport to visualize
        output_dir: Directory for chart output
        plan_name: Plan name for filenames
        
    Returns:
        List of generated chart paths
    """
    try:
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError as e:
        logger.warning(f"Matplotlib not available for charts: {e}")
        return []
    
    chart_paths = []
    
    try:
        # Chart 1: Score Distribution
        if report.micro_analyses:
            scores = [a.score for a in report.micro_analyses if a.score is not None]
            
            if scores:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.hist(scores, bins=20, edgecolor='black', alpha=0.7)
                ax.set_xlabel('Puntuación', fontsize=12)
                ax.set_ylabel('Frecuencia', fontsize=12)
                ax.set_title('Distribución de Puntuaciones Micro', fontsize=14, fontweight='bold')
                ax.grid(True, alpha=0.3)
                
                chart_path = output_dir / f"{plan_name}_score_distribution.png"
                fig.savefig(chart_path, dpi=150, bbox_inches='tight')
                plt.close(fig)
                
                chart_paths.append(chart_path)
                logger.info(f"Generated score distribution chart: {chart_path}")
        
        # Chart 2: Meso Cluster Comparison
        if report.meso_clusters:
            cluster_ids = list(report.meso_clusters.keys())
            adjusted_scores = [c.adjusted_score for c in report.meso_clusters.values()]
            
            fig, ax = plt.subplots(figsize=(12, 6))
            bars = ax.bar(range(len(cluster_ids)), adjusted_scores, edgecolor='black', alpha=0.7)
            
            # Color bars based on score
            for i, score in enumerate(adjusted_scores):
                if score >= 0.75:
                    bars[i].set_color('#28a745')  # Green
                elif score >= 0.5:
                    bars[i].set_color('#ffc107')  # Yellow
                else:
                    bars[i].set_color('#dc3545')  # Red
            
            ax.set_xticks(range(len(cluster_ids)))
            ax.set_xticklabels(cluster_ids, rotation=45, ha='right')
            ax.set_xlabel('Clúster ID', fontsize=12)
            ax.set_ylabel('Puntuación Ajustada', fontsize=12)
            ax.set_title('Comparación de Clústeres Meso', fontsize=14, fontweight='bold')
            ax.set_ylim(0, 1.0)
            ax.grid(True, alpha=0.3, axis='y')
            
            chart_path = output_dir / f"{plan_name}_cluster_comparison.png"
            fig.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            chart_paths.append(chart_path)
            logger.info(f"Generated cluster comparison chart: {chart_path}")
        
    except Exception as e:
        logger.error(f"Chart generation failed: {e}", exc_info=True)
    
    return chart_paths


def compute_file_sha256(file_path: Path) -> str:
    """Compute SHA256 hash of file.
    
    Args:
        file_path: Path to file
        
    Returns:
        Hexadecimal SHA256 digest
    """
    sha256_hash = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256_hash.update(chunk)
    
    return sha256_hash.hexdigest()

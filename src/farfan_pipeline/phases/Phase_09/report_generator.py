"""
Report Generator Module - Production Grade with AtroZ Aesthetic
===================================================================

Generates comprehensive policy analysis reports in Markdown, HTML, and PDF formats
with full AtroZ dark cyberpunk visual styling including animations, neural effects,
and visceral design elements.

Author: F.A.R.F.A.N Pipeline Team
Version: 3.0.0 (AtroZ Visceral Aesthetic)
Python: 3.12+
"""

from __future__ import annotations

import base64
import hashlib
import html
import json
import logging
import math
import random

from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from farfan_pipeline.phases.Phase_09.report_assembly import AnalysisReport

logger = logging.getLogger(__name__)

html_escape = html.escape

__all__ = [
    "ReportGenerator",
    "compute_file_sha256",
    "format_digest_atroz",
    "generate_charts",
    "generate_html_report",
    "generate_markdown_report",
    "generate_pdf_report",
    "AtrozVisualizer",
]


class ReportGenerationError(Exception):
    """Exception raised during report generation with AtroZ aesthetic."""
    pass


class AtrozVisualizer:
    """Manages AtroZ visual effects and animations for reports."""
    
    # AtroZ color palette
    COLORS = {
        'red_900': '#3A0E0E',
        'red_700': '#7A0F0F',
        'red_500': '#C41E3A',
        'blood': '#8B0000',
        'blue_900': '#04101A',
        'blue_700': '#102F56',
        'blue_electric': '#00D4FF',
        'green_900': '#0B231B',
        'green_300': '#BFEFCB',
        'green_toxic': '#39FF14',
        'copper_700': '#7B3F1D',
        'copper_500': '#B2642E',
        'copper_oxide': '#17A589',
        'ink': '#E5E7EB',
        'bg': '#0A0A0A',
        'membrane': 'rgba(122, 15, 15, 0.1)'
    }
    
    @staticmethod
    def generate_neural_background() -> str:
        """Generate SVG neural network background."""
        svg = f"""
        <svg width="100%" height="100%" style="position: absolute; top: 0; left: 0; pointer-events: none; opacity: 0.05;">
            <defs>
                <linearGradient id="neuralGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:{AtrozVisualizer.COLORS['red_700']};stop-opacity:0.1" />
                    <stop offset="50%" style="stop-color:{AtrozVisualizer.COLORS['blue_electric']};stop-opacity:0.05" />
                    <stop offset="100%" style="stop-color:{AtrozVisualizer.COLORS['green_toxic']};stop-opacity:0.1" />
                </linearGradient>
                <filter id="glow">
                    <feGaussianBlur stdDeviation="2" result="blur" />
                    <feMerge>
                        <feMergeNode in="blur" />
                        <feMergeNode in="SourceGraphic" />
                    </feMerge>
                </filter>
            </defs>
        """
        
        # Generate random neural network lines
        for _ in range(50):
            x1 = random.randint(0, 100)
            y1 = random.randint(0, 100)
            x2 = random.randint(0, 100)
            y2 = random.randint(0, 100)
            stroke_width = random.uniform(0.2, 0.5)
            opacity = random.uniform(0.02, 0.08)
            
            svg += f'''
            <line x1="{x1}%" y1="{y1}%" x2="{x2}%" y2="{y2}%" 
                  stroke="url(#neuralGradient)" stroke-width="{stroke_width}" 
                  opacity="{opacity}" />
            '''
        
        svg += "</svg>"
        return svg
    
    @staticmethod
    def generate_particle_system() -> str:
        """Generate CSS particle system animation."""
        return """
        <style>
            .particle-container {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: 1;
                overflow: hidden;
            }
            
            .particle {
                position: absolute;
                width: 1px;
                height: 1px;
                background: var(--atroz-blue-electric);
                border-radius: 50%;
                animation: particleFloat 15s infinite linear;
                opacity: 0.3;
            }
            
            @keyframes particleFloat {
                0% {
                    transform: translateY(100vh) translateX(0);
                    opacity: 0;
                }
                10% {
                    opacity: 0.3;
                }
                90% {
                    opacity: 0.3;
                }
                100% {
                    transform: translateY(-100px) translateX(100px);
                    opacity: 0;
                }
            }
            
            .neural-pulse {
                position: absolute;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: 2;
            }
            
            .pulse-line {
                position: absolute;
                height: 1px;
                background: linear-gradient(90deg, transparent, var(--atroz-green-toxic), transparent);
                opacity: 0;
                animation: pulseFlow 3s infinite;
            }
            
            @keyframes pulseFlow {
                0% {
                    transform: translateX(-100%);
                    opacity: 0;
                }
                50% {
                    opacity: 0.5;
                }
                100% {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }
        </style>
        """
    
    @staticmethod
    def generate_hexagon_pattern() -> str:
        """Generate hexagon mesh pattern."""
        return f"""
        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 0; opacity: 0.02;">
            <svg width="100%" height="100%">
                <defs>
                    <pattern id="hexagons" width="50" height="43.4" patternUnits="userSpaceOnUse" patternTransform="scale(2)">
                        <path d="M25 0L50 14.5V43.5L25 58L0 43.5V14.5L25 0Z" 
                              fill="none" 
                              stroke="{AtrozVisualizer.COLORS['copper_500']}" 
                              stroke-width="0.5" />
                    </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#hexagons)" />
            </svg>
        </div>
        """
    
    @staticmethod
    def generate_glitch_effect() -> str:
        """Generate CSS glitch effect."""
        return """
        <style>
            .glitch-container {
                position: relative;
                display: inline-block;
            }
            
            .glitch-text {
                position: relative;
                animation: glitch 5s infinite;
            }
            
            .glitch-text::before,
            .glitch-text::after {
                content: attr(data-text);
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
            }
            
            .glitch-text::before {
                left: 2px;
                text-shadow: -2px 0 var(--atroz-red-500);
                clip: rect(44px, 450px, 56px, 0);
                animation: glitch-anim 5s infinite linear alternate-reverse;
            }
            
            .glitch-text::after {
                left: -2px;
                text-shadow: -2px 0 var(--atroz-blue-electric);
                clip: rect(44px, 450px, 56px, 0);
                animation: glitch-anim2 5s infinite linear alternate-reverse;
            }
            
            @keyframes glitch {
                0%, 12%, 15%, 52%, 55%, 100% { transform: translateX(0) skew(0deg); }
                13% { transform: translateX(-10px) skew(-10deg); }
                14% { transform: translateX(10px) skew(10deg); }
                53% { transform: translateX(5px) skew(5deg); }
                54% { transform: translateX(-5px) skew(-5deg); }
            }
            
            @keyframes glitch-anim {
                0% { clip: rect(20px, 9999px, 25px, 0); }
                5% { clip: rect(30px, 9999px, 40px, 0); }
                10% { clip: rect(45px, 9999px, 50px, 0); }
                15% { clip: rect(60px, 9999px, 70px, 0); }
                20% { clip: rect(75px, 9999px, 85px, 0); }
                25% { clip: rect(90px, 9999px, 100px, 0); }
                30% { clip: rect(105px, 9999px, 115px, 0); }
                35% { clip: rect(120px, 9999px, 130px, 0); }
                40% { clip: rect(135px, 9999px, 145px, 0); }
                45% { clip: rect(150px, 9999px, 160px, 0); }
                50% { clip: rect(165px, 9999px, 175px, 0); }
                55% { clip: rect(180px, 9999px, 190px, 0); }
                60% { clip: rect(195px, 9999px, 205px, 0); }
                65% { clip: rect(210px, 9999px, 220px, 0); }
                70% { clip: rect(225px, 9999px, 235px, 0); }
                75% { clip: rect(240px, 9999px, 250px, 0); }
                80% { clip: rect(255px, 9999px, 265px, 0); }
                85% { clip: rect(270px, 9999px, 280px, 0); }
                90% { clip: rect(285px, 9999px, 295px, 0); }
                95% { clip: rect(300px, 9999px, 310px, 0); }
                100% { clip: rect(315px, 9999px, 325px, 0); }
            }
            
            @keyframes glitch-anim2 {
                0% { clip: rect(315px, 9999px, 325px, 0); }
                5% { clip: rect(300px, 9999px, 310px, 0); }
                10% { clip: rect(285px, 9999px, 295px, 0); }
                15% { clip: rect(270px, 9999px, 280px, 0); }
                20% { clip: rect(255px, 9999px, 265px, 0); }
                25% { clip: rect(240px, 9999px, 250px, 0); }
                30% { clip: rect(225px, 9999px, 235px, 0); }
                35% { clip: rect(210px, 9999px, 220px, 0); }
                40% { clip: rect(195px, 9999px, 205px, 0); }
                45% { clip: rect(180px, 9999px, 190px, 0); }
                50% { clip: rect(165px, 9999px, 175px, 0); }
                55% { clip: rect(150px, 9999px, 160px, 0); }
                60% { clip: rect(135px, 9999px, 145px, 0); }
                65% { clip: rect(120px, 9999px, 130px, 0); }
                70% { clip: rect(105px, 9999px, 115px, 0); }
                75% { clip: rect(90px, 9999px, 100px, 0); }
                80% { clip: rect(75px, 9999px, 85px, 0); }
                85% { clip: rect(60px, 9999px, 70px, 0); }
                90% { clip: rect(45px, 9999px, 50px, 0); }
                95% { clip: rect(30px, 9999px, 40px, 0); }
                100% { clip: rect(20px, 9999px, 25px, 0); }
            }
        </style>
        """
    
    @staticmethod
    def generate_radar_chart(scores: list[float], labels: list[str]) -> str:
        """Generate animated radar chart with AtroZ styling."""
        if not scores or not labels:
            return ""
        
        # Normalize scores to 0-100
        normalized_scores = [s * 100 for s in scores]
        
        svg = f'''
        <div class="radar-container" style="width: 400px; height: 400px; margin: 0 auto; position: relative;">
            <svg viewBox="0 0 400 400" style="width: 100%; height: 100%;">
                <defs>
                    <linearGradient id="radarGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:{AtrozVisualizer.COLORS['green_toxic']};stop-opacity:0.6" />
                        <stop offset="100%" style="stop-color:{AtrozVisualizer.COLORS['copper_oxide']};stop-opacity:0.3" />
                    </linearGradient>
                    <filter id="radarGlow">
                        <feGaussianBlur stdDeviation="2" result="coloredBlur" />
                        <feMerge>
                            <feMergeNode in="coloredBlur" />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                </defs>
        '''
        
        # Draw radar circles
        for i in range(1, 6):
            radius = 40 * i
            svg += f'''
                <circle cx="200" cy="200" r="{radius}" 
                        fill="none" 
                        stroke="{AtrozVisualizer.COLORS['copper_500']}" 
                        stroke-width="0.5" 
                        opacity="0.2" />
            '''
        
        # Draw axes
        n_points = len(labels)
        for i in range(n_points):
            angle = (2 * math.pi * i) / n_points
            x = 200 + 200 * math.sin(angle)
            y = 200 - 200 * math.cos(angle)
            
            svg += f'''
                <line x1="200" y1="200" x2="{x}" y2="{y}" 
                      stroke="{AtrozVisualizer.COLORS['blue_electric']}" 
                      stroke-width="0.5" 
                      opacity="0.3" />
            '''
            
            # Label
            label_x = 200 + 220 * math.sin(angle)
            label_y = 200 - 220 * math.cos(angle)
            text_anchor = "middle"
            
            svg += f'''
                <text x="{label_x}" y="{label_y}" 
                      text-anchor="{text_anchor}"
                      fill="{AtrozVisualizer.COLORS['ink']}" 
                      font-size="10" 
                      font-family="'JetBrains Mono', monospace"
                      opacity="0.7">{labels[i]}</text>
            '''
        
        # Draw data polygon
        points = []
        for i in range(n_points):
            score = normalized_scores[i]
            radius = 200 * (score / 100)
            angle = (2 * math.pi * i) / n_points
            x = 200 + radius * math.sin(angle)
            y = 200 - radius * math.cos(angle)
            points.append(f"{x},{y}")
        
        points_str = " ".join(points)
        
        svg += f'''
                <polygon points="{points_str}" 
                        fill="url(#radarGradient)" 
                        stroke="{AtrozVisualizer.COLORS['green_toxic']}" 
                        stroke-width="2" 
                        opacity="0.7"
                        filter="url(#radarGlow)">
                    <animate attributeName="opacity" 
                             values="0.5;0.8;0.5" 
                             dur="3s" 
                             repeatCount="indefinite" />
                </polygon>
        '''
        
        svg += '''
            </svg>
        </div>
        '''
        
        return svg


class ReportGenerator:
    """Generates comprehensive policy analysis reports in multiple formats with AtroZ aesthetic."""

    def __init__(
        self,
        output_dir: Path | str,
        plan_name: str = "plan1",
        enable_charts: bool = True,
        enable_animations: bool = True,
    ) -> None:
        """Initialize report generator with AtroZ aesthetic."""
        self.output_dir = Path(output_dir)
        self.plan_name = plan_name
        self.enable_charts = enable_charts
        self.enable_animations = enable_animations
        self.visualizer = AtrozVisualizer()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"AtroZ ReportGenerator initialized: {self.output_dir}")

    def generate_all(
        self,
        report: AnalysisReport,
        generate_pdf: bool = True,
        generate_html: bool = True,
        generate_markdown: bool = True,
        template_name: str = "report_enhanced.html.j2",
    ) -> dict[str, Path]:
        """Generate all report formats with enhanced template (default: report_enhanced.html.j2)."""
        artifacts: dict[str, Path] = {}

        try:
            if generate_markdown:
                markdown_path = self.output_dir / f"{self.plan_name}_report.md"
                markdown_content = generate_markdown_report(report)
                markdown_path.write_text(markdown_content, encoding="utf-8")
                artifacts["markdown"] = markdown_path
                logger.info(f"Generated AtroZ Markdown: {markdown_path}")

            chart_paths = []
            if self.enable_charts:
                chart_paths = generate_charts(report, self.output_dir, self.plan_name)
                logger.info(f"Generated {len(chart_paths)} AtroZ charts")

            if generate_html:
                html_path = self.output_dir / f"{self.plan_name}_report.html"
                html_content = generate_html_report(
                    report, 
                    chart_paths, 
                    template_name,
                    enable_animations=self.enable_animations
                )
                html_path.write_text(html_content, encoding="utf-8")
                artifacts["html"] = html_path
                logger.info(f"Generated AtroZ HTML: {html_path}")
            
            if generate_pdf:
                if not generate_html:
                    html_content = generate_html_report(
                        report, 
                        chart_paths, 
                        template_name,
                        enable_animations=self.enable_animations
                    )
                else:
                    html_content = html_path.read_text(encoding="utf-8")

                pdf_path = self.output_dir / f"{self.plan_name}_report.pdf"
                generate_pdf_report(html_content, pdf_path)
                artifacts["pdf"] = pdf_path
                logger.info(f"Generated AtroZ PDF: {pdf_path}")

            manifest_path = self.output_dir / f"{self.plan_name}_manifest.json"
            manifest = self._generate_manifest(artifacts, report)
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            artifacts["manifest"] = manifest_path
            logger.info(f"Generated AtroZ manifest: {manifest_path}")

            return artifacts

        except Exception as e:
            logger.error(f"AtroZ report generation failed: {e}", exc_info=True)
            raise ReportGenerationError(f"Failed to generate AtroZ reports: {e}") from e

    def _generate_manifest(self, artifacts: dict[str, Path], report: AnalysisReport) -> dict[str, Any]:
        """Generate manifest with AtroZ artifact metadata."""
        manifest: dict[str, Any] = {
            "generated_at": datetime.now(UTC).isoformat(),
            "plan_name": self.plan_name,
            "report_id": report.metadata.report_id,
            "aesthetic": "atroz_visceral",
            "version": "3.0.0",
            "artifacts": {},
        }

        for artifact_type, path in artifacts.items():
            if path.exists():
                manifest["artifacts"][artifact_type] = {
                    "path": str(path.relative_to(self.output_dir)),
                    "size_bytes": path.stat().st_size,
                    "sha256": compute_file_sha256(path),
                    "mimetype": self._get_mimetype(path),
                }

        if report.report_digest:
            manifest["report_digest"] = report.report_digest
        if report.evidence_chain_hash:
            manifest["evidence_chain_hash"] = report.evidence_chain_hash

        return manifest

    def _get_mimetype(self, path: Path) -> str:
        """Get MIME type based on file extension."""
        ext = path.suffix.lower()
        mime_types = {
            '.html': 'text/html',
            '.pdf': 'application/pdf',
            '.md': 'text/markdown',
            '.json': 'application/json',
            '.png': 'image/png',
            '.svg': 'image/svg+xml',
        }
        return mime_types.get(ext, 'application/octet-stream')


def generate_markdown_report(report: AnalysisReport) -> str:
    """Generate structured Markdown report with AtroZ styling hints."""
    lines = [
        f"# ⚡ F.A.R.F.A.N · Reporte de Análisis Neural\n\n",
        f"## {report.metadata.plan_name}\n\n",
        "```atroz\n",
        f"REPORTE ID: {report.metadata.report_id}\n",
        f"GENERADO: {report.metadata.generated_at}\n",
        f"VERSION: {report.metadata.monolith_version}\n",
        f"HASH: {report.metadata.monolith_hash[:16]}...\n",
        "```\n\n",
        "---\n\n",
    ]

    if report.macro_summary:
        score_pct = report.macro_summary.adjusted_score * 100
        score_color = "🟢" if score_pct >= 70 else "🟡" if score_pct >= 50 else "🔴"
        
        lines.extend([
            "## ⚡ RESUMEN EJECUTIVO\n\n",
            f"### PUNTUACIÓN GLOBAL: **{score_pct:.2f}%** {score_color}\n\n",
            "### MÉTRICAS NEURALES\n\n",
            f"- **Posterior Global:** `{report.macro_summary.overall_posterior:.4f}`\n",
            f"- **Puntuación Ajustada:** `{report.macro_summary.adjusted_score:.4f}`\n",
            f"- **Contradicciones Detectadas:** `{report.macro_summary.contradiction_count}`\n",
            f"- **Confianza del Modelo:** `{report.macro_summary.model_confidence if hasattr(report.macro_summary, 'model_confidence') else 'N/A'}`\n\n",
        ])

    if report.macro_summary and report.macro_summary.recommendations:
        lines.append("## 🎯 RECOMENDACIONES ESTRATÉGICAS\n\n")
        for i, rec in enumerate(report.macro_summary.recommendations, 1):
            severity_icon = "🔥" if rec.severity.lower() == "alta" else "⚡" if rec.severity.lower() == "media" else "💡"
            lines.extend([
                f"### {severity_icon} {i}. **{rec.type}** · `{rec.severity}`\n\n",
                f"> {rec.description}\n\n",
                f"*`{rec.source}`*\n\n",
            ])

    if report.meso_clusters:
        lines.append("## 🌀 ANÁLISIS MESO · CLÚSTERES\n\n")
        lines.append(f"**Clústeres Identificados:** `{len(report.meso_clusters)}`\n\n")
        
        for cluster_id, cluster in report.meso_clusters.items():
            cluster_score = cluster.adjusted_score * 100
            lines.extend([
                f"### 🟣 {cluster_id}\n",
                f"- **Score:** `{cluster_score:.1f}%`\n",
                f"- **Indicadores:** `{len(cluster.indicators)}`\n",
                f"- **Trend:** `{'+' if cluster.trend > 0 else '-' if cluster.trend < 0 else '='}`\n\n",
            ])

    lines.append(f"## 🔬 ANÁLISIS MICRO · PREGUNTAS\n\n")
    lines.append(f"**Total Analizadas:** `{len(report.micro_analyses)}`\n\n")
    
    # Show top and bottom performing questions
    sorted_questions = sorted(report.micro_analyses, key=lambda x: x.score or 0, reverse=True)
    
    lines.append("**TOP PERFORMERS:**\n\n")
    for i, q in enumerate(sorted_questions[:5]):
        if q.score:
            lines.append(f"{i+1}. **Q{q.question_id}:** `{q.score*100:.1f}%` - {q.category}\n")
    
    lines.append("\n**AREAS CRÍTICAS:**\n\n")
    for i, q in enumerate(sorted_questions[-5:][::-1]):
        if q.score:
            lines.append(f"{i+1}. **Q{q.question_id}:** `{q.score*100:.1f}%` - {q.category}\n")

    lines.append("\n---\n")
    lines.append("`⚡ GENERADO POR SISTEMA F.A.R.F.A.N · ANÁLISIS NEURAL`\n")

    return "".join(lines)


def generate_html_report(
    report: AnalysisReport,
    chart_paths: list[Path] | None = None,
    template_name: str = "report.html.j2",
    enable_animations: bool = True,
) -> str:
    """Generate HTML report with enhanced template (aligned with generate_all default)."""
    visualizer = AtrozVisualizer()
    
    try:
        from jinja2 import Environment, FileSystemLoader, select_autoescape
    except ImportError:
        return _generate_atroz_html(report, chart_paths, visualizer, enable_animations)

    template_dir = Path(__file__).resolve().parent / "templates"
    if not template_dir.exists():
        return _generate_atroz_html(report, chart_paths, visualizer, enable_animations)

    env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=select_autoescape(["html"]))
    template = env.get_template(template_name)
    
    context = {
        "metadata": report.metadata.__dict__,
        "micro_analyses": [a.__dict__ for a in report.micro_analyses],
        "meso_clusters": {k: v.__dict__ for k, v in report.meso_clusters.items()} if report.meso_clusters else {},
        "macro_summary": report.macro_summary.__dict__ if report.macro_summary else None,
        "report_digest": report.report_digest,
        "evidence_chain_hash": report.evidence_chain_hash,
        "charts": chart_paths or [],
        "atroz_colors": AtrozVisualizer.COLORS,
        "enable_animations": enable_animations,
    }

    return template.render(**context)


def _generate_atroz_html(
    report: AnalysisReport,
    chart_paths: list[Path] | None,
    visualizer: AtrozVisualizer,
    enable_animations: bool = True
) -> str:
    """Generate inline HTML with full AtroZ visceral aesthetic (fallback mode with XSS protection)."""
    
    # Escape all user-controllable metadata fields for XSS protection
    safe_plan_name = html_escape(report.metadata.plan_name)
    safe_report_id = html_escape(report.metadata.report_id)
    safe_generated_at = html_escape(str(report.metadata.generated_at))
    safe_monolith_version = html_escape(report.metadata.monolith_version)
    safe_monolith_hash = html_escape(report.metadata.monolith_hash)
    
    # Prepare data
    score_pct = report.macro_summary.adjusted_score * 100 if report.macro_summary else 0
    total_questions = report.metadata.total_questions
    analyzed_questions = report.metadata.questions_analyzed
    clusters_count = len(report.meso_clusters) if report.meso_clusters else 0
    contradictions = report.macro_summary.contradiction_count if report.macro_summary else 0
    
    # Calculate cluster scores for radar chart
    if report.meso_clusters:
        cluster_labels = list(report.meso_clusters.keys())
        cluster_scores = [c.adjusted_score for c in report.meso_clusters.values()]
        radar_chart = visualizer.generate_radar_chart(cluster_scores, cluster_labels)
    else:
        radar_chart = ""
    
    # Base64 encode chart images
    chart_images = ""
    if chart_paths:
        for i, chart_path in enumerate(chart_paths[:2]):  # Limit to first 2 charts
            if chart_path.exists():
                with open(chart_path, "rb") as f:
                    chart_data = base64.b64encode(f.read()).decode('utf-8')
                    chart_images += f'''
                    <div class="chart-card">
                        <img src="data:image/png;base64,{chart_data}" 
                             alt="Chart {i+1}" 
                             class="atroz-chart" />
                    </div>
                    '''
    
    # Animation scripts
    animations = visualizer.generate_particle_system() + visualizer.generate_glitch_effect() if enable_animations else ""
    
    # Pre-generate recommendations HTML to avoid complex f-string nesting
    recommendations_html = ""
    if report.macro_summary and report.macro_summary.recommendations:
        recs = report.macro_summary.recommendations[:6]
        rec_cards = []
        for rec in recs:
            severity = html_escape(rec.severity)
            rec_type = html_escape(rec.type)
            description = html_escape(rec.description)
            source = html_escape(rec.source)
            
            card = f'''
                <div class="rec-card">
                    <div class="rec-severity">{severity}</div>
                    <div style="font-size: 14px; font-weight: 700; margin-bottom: 10px;">{rec_type}</div>
                    <div style="font-size: 12px; opacity: 0.9;">{description}</div>
                    <div style="font-size: 10px; opacity: 0.5; margin-top: 10px;">{source}</div>
                </div>
            '''
            rec_cards.append(card)
            
        recommendations_html = f'''
        <div class="section">
            <div class="section-title">🎯 RECOMENDACIONES</div>
            <div class="recommendation-grid">
                {"".join(rec_cards)}
            </div>
        </div>
        '''
    
    # Pre-calculate animations script to avoid complex nesting
    animations_js_html = ""
    if enable_animations:
        animations_js_html = '''
    <script>
        // Generate particles
        document.addEventListener('DOMContentLoaded', function() {
            const container = document.createElement('div');
            container.className = 'particle-container';
            document.body.appendChild(container);
            
            for (let i = 0; i < 50; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.left = Math.random() * 100 + 'vw';
                particle.style.animationDelay = Math.random() * 15 + 's';
                container.appendChild(particle);
            }
            
            // Generate pulse lines
            const pulseContainer = document.createElement('div');
            pulseContainer.className = 'neural-pulse';
            document.body.appendChild(pulseContainer);
            
            for (let i = 0; i < 5; i++) {
                const pulseLine = document.createElement('div');
                pulseLine.className = 'pulse-line';
                pulseLine.style.top = Math.random() * 100 + 'vh';
                pulseLine.style.width = Math.random() * 200 + 100 + 'px';
                pulseLine.style.animationDelay = Math.random() * 3 + 's';
                pulseContainer.appendChild(pulseLine);
            }
        });
    </script>
    '''

    return f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ F.A.R.F.A.N · {safe_plan_name}</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@200;400;700&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --atroz-red-900: #3A0E0E;
            --atroz-red-700: #7A0F0F;
            --atroz-red-500: #C41E3A;
            --atroz-blood: #8B0000;
            --atroz-blue-900: #04101A;
            --atroz-blue-700: #102F56;
            --atroz-blue-electric: #00D4FF;
            --atroz-green-900: #0B231B;
            --atroz-green-300: #BFEFCB;
            --atroz-green-toxic: #39FF14;
            --atroz-copper-700: #7B3F1D;
            --atroz-copper-500: #B2642E;
            --atroz-copper-oxide: #17A589;
            --ink: #E5E7EB;
            --bg: #0A0A0A;
            --membrane: rgba(122, 15, 15, 0.1);
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            background: var(--bg);
            color: var(--ink);
            font-family: 'JetBrains Mono', monospace;
            overflow-x: hidden;
            position: relative;
        }}
        
        body::before {{
            content: '';
            position: fixed;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: 
                radial-gradient(circle at 20% 50%, var(--membrane) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(16, 47, 86, 0.05) 0%, transparent 50%),
                radial-gradient(circle at 40% 20%, rgba(11, 35, 27, 0.05) 0%, transparent 50%);
            animation: organicPulse 15s ease-in-out infinite;
            pointer-events: none;
            z-index: -1;
        }}
        
        @keyframes organicPulse {{
            0%, 100% {{ transform: rotate(0deg) scale(1); opacity: 0.7; }}
            25% {{ transform: rotate(90deg) scale(1.1); opacity: 0.8; }}
            50% {{ transform: rotate(180deg) scale(0.95); opacity: 0.6; }}
            75% {{ transform: rotate(270deg) scale(1.05); opacity: 0.9; }}
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            position: relative;
            z-index: 10;
        }}
        
        .header {{
            background: linear-gradient(180deg, rgba(4,16,26,0.9) 0%, transparent 100%);
            backdrop-filter: blur(20px);
            padding: 60px 40px;
            position: relative;
            border-bottom: 1px solid transparent;
            background-image: linear-gradient(90deg, transparent, var(--atroz-copper-500), transparent);
            background-position: 0% 100%;
            background-repeat: no-repeat;
            background-size: 100% 1px;
            animation: scanline 3s linear infinite;
        }}
        
        @keyframes scanline {{
            0% {{ background-position: -100% 100%; }}
            100% {{ background-position: 200% 100%; }}
        }}
        
        .logo {{
            font-size: 48px;
            font-weight: 200;
            letter-spacing: 12px;
            background: linear-gradient(90deg, var(--ink), var(--atroz-green-toxic));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            position: relative;
        }}
        
        .logo::before {{
            content: 'F.A.R.F.A.N';
            position: absolute;
            left: 0;
            top: 0;
            color: var(--atroz-red-700);
            animation: glitch 5s infinite;
            z-index: -1;
            opacity: 0.8;
        }}
        
        .subtitle {{
            font-size: 14px;
            letter-spacing: 4px;
            opacity: 0.7;
            text-transform: uppercase;
            margin-bottom: 20px;
        }}
        
        .report-id {{
            font-size: 10px;
            letter-spacing: 2px;
            opacity: 0.5;
            background: rgba(0,0,0,0.5);
            padding: 5px 10px;
            display: inline-block;
            border: 1px solid var(--atroz-copper-700);
        }}
        
        .score-hero {{
            text-align: center;
            padding: 80px 40px;
            background: linear-gradient(135deg, rgba(122,15,15,0.3), rgba(16,47,86,0.3));
            border: 1px solid var(--atroz-copper-500);
            margin: 40px;
            position: relative;
            overflow: hidden;
        }}
        
        .score-hero::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, var(--membrane), transparent);
            animation: organicMove 10s ease-in-out infinite;
            pointer-events: none;
        }}
        
        @keyframes organicMove {{
            0%, 100% {{ transform: translate(0, 0); }}
            50% {{ transform: translate(20px, 20px); }}
        }}
        
        .score-value {{
            font-size: 120px;
            font-weight: 700;
            color: var(--atroz-green-toxic);
            text-shadow: 0 0 40px var(--atroz-green-toxic);
            position: relative;
            z-index: 2;
            animation: pulse 2s ease-in-out infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ text-shadow: 0 0 40px var(--atroz-green-toxic); }}
            50% {{ text-shadow: 0 0 60px var(--atroz-green-toxic); }}
        }}
        
        .score-label {{
            font-size: 16px;
            letter-spacing: 6px;
            text-transform: uppercase;
            margin-top: 20px;
            opacity: 0.8;
            position: relative;
            z-index: 2;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 30px;
            margin: 60px 40px;
        }}
        
        .metric-card {{
            background: rgba(4,16,26,0.6);
            border: 1px solid var(--atroz-copper-700);
            padding: 30px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
        }}
        
        .metric-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, var(--atroz-copper-oxide), transparent);
            transition: left 0.5s;
        }}
        
        .metric-card:hover::before {{
            left: 100%;
        }}
        
        .metric-card:hover {{
            border-color: var(--atroz-blue-electric);
            box-shadow: 0 0 40px rgba(0,212,255,0.3);
            transform: translateY(-5px);
        }}
        
        .metric-label {{
            font-size: 11px;
            color: var(--atroz-copper-500);
            letter-spacing: 3px;
            text-transform: uppercase;
            margin-bottom: 15px;
            position: relative;
            z-index: 2;
        }}
        
        .metric-value {{
            font-size: 48px;
            font-weight: 700;
            color: var(--atroz-blue-electric);
            text-shadow: 0 0 20px var(--atroz-blue-electric);
            position: relative;
            z-index: 2;
        }}
        
        .section {{
            margin: 80px 40px;
            padding: 40px;
            background: rgba(4,16,26,0.8);
            border: 1px solid var(--atroz-copper-700);
            backdrop-filter: blur(10px);
        }}
        
        .section-title {{
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 30px;
            letter-spacing: 4px;
            text-transform: uppercase;
            background: linear-gradient(90deg, var(--atroz-blue-electric), var(--atroz-green-toxic));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            position: relative;
        }}
        
        .section-title::after {{
            content: '';
            position: absolute;
            bottom: -10px;
            left: 0;
            width: 100px;
            height: 1px;
            background: linear-gradient(90deg, var(--atroz-blue-electric), transparent);
        }}
        
        .chart-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-top: 40px;
        }}
        
        .chart-card {{
            background: rgba(0,0,0,0.5);
            border: 1px solid rgba(178,100,46,0.2);
            padding: 20px;
            transition: all 0.3s;
        }}
        
        .chart-card:hover {{
            border-color: var(--atroz-green-toxic);
            box-shadow: 0 0 30px rgba(57,255,20,0.2);
        }}
        
        .atroz-chart {{
            width: 100%;
            height: auto;
            filter: brightness(1.1) contrast(1.1);
        }}
        
        .recommendation-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        
        .rec-card {{
            background: linear-gradient(135deg, var(--atroz-red-900), var(--atroz-blue-900));
            border-left: 3px solid var(--atroz-blood);
            padding: 20px;
            transition: all 0.3s;
            position: relative;
            overflow: hidden;
        }}
        
        .rec-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 3px;
            height: 100%;
            background: var(--atroz-green-toxic);
            opacity: 0;
            transition: opacity 0.3s;
        }}
        
        .rec-card:hover::before {{
            opacity: 0.5;
        }}
        
        .rec-card:hover {{
            transform: translateX(10px);
            box-shadow: -10px 0 30px rgba(139,0,0,0.3);
        }}
        
        .rec-severity {{
            position: absolute;
            top: 10px;
            right: 10px;
            font-size: 10px;
            color: var(--atroz-copper-500);
            letter-spacing: 1px;
            text-transform: uppercase;
            padding: 2px 8px;
            border: 1px solid var(--atroz-copper-500);
        }}
        
        .footer {{
            background: linear-gradient(180deg, transparent, rgba(4,16,26,0.9));
            border-top: 1px solid var(--atroz-copper-700);
            padding: 40px;
            text-align: center;
            margin-top: 80px;
            backdrop-filter: blur(10px);
        }}
        
        .footer-logo {{
            font-size: 24px;
            letter-spacing: 8px;
            background: linear-gradient(90deg, var(--ink), var(--atroz-green-toxic));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        
        .footer-subtitle {{
            font-size: 10px;
            opacity: 0.5;
            letter-spacing: 2px;
            text-transform: uppercase;
        }}
        
        .metadata {{
            font-size: 9px;
            opacity: 0.3;
            margin-top: 20px;
            letter-spacing: 1px;
        }}
        
        @media (max-width: 768px) {{
            .header {{ padding: 30px 20px; }}
            .logo {{ font-size: 32px; letter-spacing: 8px; }}
            .score-value {{ font-size: 80px; }}
            .section {{ margin: 40px 20px; padding: 20px; }}
            .metrics-grid {{ margin: 40px 20px; }}
            .chart-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
    
    {animations}
</head>
<body>
    {visualizer.generate_hexagon_pattern() if enable_animations else ""}
    
    <div class="container">
        <header class="header">
            <div class="logo glitch-text" data-text="F.A.R.F.A.N">F.A.R.F.A.N</div>
            <div class="subtitle">Neural Policy Analysis System</div>
            <div style="margin-top: 20px; font-size: 18px; opacity: 0.8;">
                {safe_plan_name}
            </div>
            <div class="report-id">REPORT ID: {safe_report_id}</div>
        </header>
        
        <div class="score-hero">
            <div class="score-value">{score_pct:.1f}%</div>
            <div class="score-label">PUNTUACIÓN GLOBAL</div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Preguntas</div>
                <div class="metric-value">{total_questions}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Analizadas</div>
                <div class="metric-value">{analyzed_questions}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Clusters</div>
                <div class="metric-value">{clusters_count}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Contradicciones</div>
                <div class="metric-value">{contradictions}</div>
            </div>
        </div>
        
        {radar_chart if radar_chart else ""}
        
        <div class="section">
            <div class="section-title">⚡ VISUALIZACIONES</div>
            <div class="chart-grid">
                {chart_images if chart_images else '<div style="opacity: 0.5; text-align: center;">No hay visualizaciones disponibles</div>'}
            </div>
        </div>
        
        {recommendations_html}
        
        <div class="footer">
            <div class="footer-logo">F.A.R.F.A.N</div>
            <div class="footer-subtitle">
                Framework for Advanced Retrieval and Forensic Analysis
            </div>
            <div class="metadata">
                Generado el {safe_generated_at} | 
                Versión {safe_monolith_version} | 
                Hash: {safe_monolith_hash[:12]}...
            </div>
        </div>
    </div>
    
    {animations_js_html}
</body>
</html>'''


def generate_pdf_report(html_content: str, output_path: Path) -> None:
    """Generate PDF from HTML with AtroZ styling."""
    try:
        from weasyprint import HTML
    except ImportError as e:
        raise ReportGenerationError("WeasyPrint not installed") from e

    try:
        # Configure WeasyPrint for AtroZ styling
        HTML(string=html_content).write_pdf(
            str(output_path),
            stylesheets=None,  # Styles are inline
            presentational_hints=True
        )
        logger.info(f"AtroZ PDF generated: {output_path}")
    except Exception as e:
        raise ReportGenerationError(f"Failed to generate AtroZ PDF: {e}") from e


def generate_charts(report: AnalysisReport, output_dir: Path, plan_name: str = "plan1") -> list[Path]:
    """Generate charts with full AtroZ cyberpunk styling."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        logger.warning("Matplotlib not available for AtroZ charts")
        return []

    chart_paths = []
    colors = AtrozVisualizer.COLORS
    
    try:
        # SCORE DISTRIBUTION CHART - Enhanced
        if report.micro_analyses:
            scores = [a.score for a in report.micro_analyses if a.score is not None]
            if scores:
                fig, ax = plt.subplots(figsize=(14, 8), facecolor=colors['bg'])
                ax.set_facecolor(colors['bg'])
                
                # Create gradient histogram
                n, bins, patches = ax.hist(
                    scores, 
                    bins=30, 
                    edgecolor=colors['green_toxic'], 
                    linewidth=2,
                    alpha=0.7,
                    density=True
                )
                
                # Gradient coloring based on score
                norm = plt.Normalize(min(scores), max(scores))
                cmap = plt.cm.colors.LinearSegmentedColormap.from_list(
                    "atroz", 
                    [colors['blood'], colors['copper_oxide'], colors['green_toxic']]
                )
                
                for i, patch in enumerate(patches):
                    patch.set_facecolor(cmap(norm(bins[i])))
                    patch.set_edgecolor(colors['blue_electric'])
                    patch.set_linewidth(1)
                    patch.set_alpha(0.8)
                
                # Add glow effect
                for spine in ax.spines.values():
                    spine.set_edgecolor(colors['copper_500'])
                    spine.set_linewidth(1)
                
                ax.set_xlabel("PUNTUACIÓN", 
                             fontsize=12, 
                             color=colors['ink'], 
                             family='monospace',
                             fontweight='bold',
                             labelpad=15)
                ax.set_ylabel("DENSIDAD", 
                             fontsize=12, 
                             color=colors['ink'], 
                             family='monospace',
                             fontweight='bold',
                             labelpad=15)
                ax.set_title("DISTRIBUCIÓN NEURAL DE SCORES", 
                            fontsize=16, 
                            color=colors['green_toxic'], 
                            family='monospace',
                            fontweight='bold',
                            pad=20)
                
                ax.tick_params(colors=colors['ink'], labelsize=10)
                ax.grid(True, alpha=0.15, color=colors['blue_electric'], linestyle='--', linewidth=0.5)
                
                # Add custom legend
                ax.legend(['Distribución Neural'], 
                         loc='upper right',
                         frameon=True,
                         facecolor=colors['blue_900'],
                         edgecolor=colors['copper_500'],
                         fontsize=10,
                         labelcolor=colors['ink'])
                
                chart_path = output_dir / f"{plan_name}_score_distribution_atroz.png"
                fig.savefig(chart_path, 
                           dpi=200, 
                           bbox_inches='tight', 
                           facecolor=colors['bg'],
                           edgecolor='none',
                           transparent=False)
                plt.close(fig)
                chart_paths.append(chart_path)

        # CLUSTER COMPARISON CHART - Enhanced 3D effect
        if report.meso_clusters:
            cluster_ids = list(report.meso_clusters.keys())
            scores = [c.adjusted_score * 100 for c in report.meso_clusters.values()]
            
            fig, ax = plt.subplots(figsize=(16, 9), facecolor=colors['bg'])
            ax.set_facecolor(colors['bg'])
            
            # Create 3D-like bars with gradient
            x_pos = np.arange(len(cluster_ids))
            bar_width = 0.7
            
            # Create gradient for bars
            gradient = np.linspace(0, 1, len(cluster_ids))
            cmap = plt.cm.colors.LinearSegmentedColormap.from_list(
                "atroz_bars", 
                [colors['blood'], colors['copper_oxide'], colors['green_toxic']]
            )
            
            bars = ax.bar(x_pos, scores, width=bar_width, 
                         edgecolor=colors['blue_electric'], 
                         linewidth=2,
                         alpha=0.9)
            
            # Apply gradient and add glow effect
            for i, (bar, score) in enumerate(zip(bars, scores)):
                bar_color = cmap(gradient[i])
                bar.set_facecolor(bar_color)
                
                # Add inner glow
                bar.set_edgecolor(colors['ink'])
                bar.set_linewidth(1)
                
                # Add value labels with glow
                ax.text(bar.get_x() + bar.get_width()/2, 
                       bar.get_height() + 1,
                       f'{score:.1f}%',
                       ha='center', 
                       va='bottom',
                       color=colors['green_toxic'],
                       fontsize=9,
                       fontweight='bold',
                       family='monospace')
            
            # Style axes
            ax.set_xticks(x_pos)
            ax.set_xticklabels(cluster_ids, 
                              rotation=45, 
                              ha="right", 
                              color=colors['ink'], 
                              family='monospace',
                              fontsize=10,
                              fontweight='bold')
            
            ax.set_ylabel("SCORE %", 
                         fontsize=12, 
                         color=colors['ink'], 
                         family='monospace',
                         fontweight='bold',
                         labelpad=15)
            
            ax.set_title("ANÁLISIS DE CLÚSTERES MESO", 
                        fontsize=18, 
                        color=colors['blue_electric'], 
                        family='monospace',
                        fontweight='bold',
                        pad=25)
            
            ax.tick_params(colors=colors['ink'], labelsize=10)
            ax.grid(True, alpha=0.2, color=colors['copper_500'], linestyle=':', linewidth=0.8, axis='y')
            
            # Add score range indicators
            ax.axhline(y=70, color=colors['green_toxic'], linestyle='--', alpha=0.3, linewidth=1)
            ax.axhline(y=50, color=colors['copper_oxide'], linestyle='--', alpha=0.3, linewidth=1)
            ax.axhline(y=30, color=colors['blood'], linestyle='--', alpha=0.3, linewidth=1)
            
            chart_path = output_dir / f"{plan_name}_cluster_comparison_atroz.png"
            fig.savefig(chart_path, 
                       dpi=200, 
                       bbox_inches='tight', 
                       facecolor=colors['bg'],
                       edgecolor='none')
            plt.close(fig)
            chart_paths.append(chart_path)

        # RADAR CHART for clusters with actual multi-dimensional metrics
        if report.meso_clusters and len(report.meso_clusters) >= 3:
            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True), facecolor=colors['bg'])
            ax.set_facecolor(colors['bg'])

            # Define metric dimensions for the radar chart
            categories = ['Raw Score', 'Adjusted Score', 'Dispersion', 'Peer Quality', 'Overall Quality']
            N = len(categories)

            # Extract top 3 clusters with their actual metrics
            cluster_items = list(report.meso_clusters.items())[:3]

            # Build multi-dimensional data for each cluster
            values = []
            for cluster_id, cluster in cluster_items:
                # Extract actual metrics from the cluster
                cluster_metrics = [
                    cluster.raw_meso_score,  # Raw Score
                    cluster.adjusted_score,  # Adjusted Score
                    1.0 - cluster.dispersion_penalty,  # Dispersion (inverted - higher is better)
                    1.0 - cluster.peer_penalty,  # Peer Quality (inverted - higher is better)
                    1.0 - cluster.total_penalty,  # Overall Quality (inverted - higher is better)
                ]
                values.append(cluster_metrics)
            values = np.array(values)

            # Setup angles for radar chart
            angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
            angles += angles[:1]

            # Plot each cluster with its actual metrics
            cluster_colors = ['#00ff88', '#ff8800', '#0088ff']
            for i in range(min(3, len(cluster_items))):
                vals = values[i].tolist()
                vals += vals[:1]
                
                ax.plot(angles, vals, linewidth=2, linestyle='solid', 
                       color=[colors['green_toxic'], colors['blue_electric'], colors['copper_oxide']][i],
                       alpha=0.8)
                ax.fill(angles, vals, alpha=0.1, 
                       color=[colors['green_toxic'], colors['blue_electric'], colors['copper_oxide']][i])
            
            # Set category labels
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, color=colors['ink'], family='monospace', fontsize=9)
            
            # Style
            ax.set_yticklabels([])
            ax.grid(color=colors['copper_500'], alpha=0.3, linestyle='--', linewidth=0.5)
            ax.spines['polar'].set_color(colors['copper_700'])
            
            ax.set_title("RADAR DE CLÚSTERES", 
                        color=colors['green_toxic'], 
                        family='monospace',
                        fontsize=14,
                        fontweight='bold',
                        pad=20)
            
            chart_path = output_dir / f"{plan_name}_cluster_radar_atroz.png"
            fig.savefig(chart_path, 
                       dpi=200, 
                       bbox_inches='tight', 
                       facecolor=colors['bg'],
                       transparent=False)
            plt.close(fig)
            chart_paths.append(chart_path)

    except Exception as e:
        logger.error(f"AtroZ chart generation failed: {e}", exc_info=True)

    return chart_paths


def compute_file_sha256(file_path: Path) -> str:
    """Compute SHA256 hash of file (returns standard 64-char hex digest)."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256_hash.update(chunk)
    
    # Return standard hex digest for compatibility
    return sha256_hash.hexdigest()


def format_digest_atroz(digest: str) -> str:
    """Format SHA256 digest with AtroZ aesthetic (for display only)."""
    if len(digest) >= 32:
        return f"atroz:{digest[:16]}...{digest[-16:]}"
    return digest

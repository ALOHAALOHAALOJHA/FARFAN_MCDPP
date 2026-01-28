#!/usr/bin/env python3
"""
Generador de reportes comprehensivos de calidad de código.
Analiza métricas y genera reportes en HTML.
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class QualityReportGenerator:
    """Genera reportes detallados de calidad de código"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.report_data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': {},
            'issues': [],
            'recommendations': []
        }
    
    def run_metrics(self) -> Dict:
        """Recolecta métricas del código"""
        metrics = {}
        
        # Contar archivos
        py_files = list(self.project_root.rglob('*.py'))
        metrics['total_python_files'] = len(py_files)
        
        # Contar líneas de código
        total_lines = 0
        for py_file in py_files:
            if any(skip in str(py_file) for skip in ['.venv', 'venv', '__pycache__']):
                continue
            try:
                with open(py_file, 'r') as f:
                    total_lines += len(f.readlines())
            except:
                pass
        metrics['total_lines_of_code'] = total_lines
        
        # Ejecutar radon para métricas de complejidad
        try:
            result = subprocess.run(
                ['radon', 'cc', '.', '-j'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                complexity_data = json.loads(result.stdout)
                metrics['cyclomatic_complexity'] = self._calculate_average_complexity(complexity_data)
        except:
            pass
        
        # Métricas de mantenibilidad con radon
        try:
            result = subprocess.run(
                ['radon', 'mi', '.', '-j'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                mi_data = json.loads(result.stdout)
                metrics['maintainability_index'] = self._calculate_average_mi(mi_data)
        except:
            pass
        
        return metrics
    
    def _calculate_average_complexity(self, data: Dict) -> float:
        """Calcula complejidad ciclomática promedio"""
        total = 0
        count = 0
        for file_data in data.values():
            for func in file_data:
                total += func.get('complexity', 0)
                count += 1
        return round(total / count, 2) if count > 0 else 0
    
    def _calculate_average_mi(self, data: Dict) -> float:
        """Calcula índice de mantenibilidad promedio"""
        total = 0
        count = 0
        for file_path, mi_score in data.items():
            if isinstance(mi_score, dict) and 'mi' in mi_score:
                total += mi_score['mi']
                count += 1
        return round(total / count, 2) if count > 0 else 0
    
    def generate_html_report(self) -> str:
        """Genera reporte HTML"""
        metrics = self.run_metrics()
        
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Reporte de Calidad de Código - {datetime.now().strftime('%Y-%m-%d')}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                }}
                h1 {{
                    color: #333;
                    border-bottom: 3px solid #667eea;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #555;
                    margin-top: 30px;
                }}
                .metrics-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }}
                .metric-card {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 4px solid #667eea;
                }}
                .metric-value {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #667eea;
                }}
                .metric-label {{
                    color: #666;
                    margin-top: 5px;
                }}
                .good {{ color: #28a745; }}
                .warning {{ color: #ffc107; }}
                .error {{ color: #dc3545; }}
                .recommendations {{
                    background: #e8f4fd;
                    border-left: 4px solid #0066cc;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                ul {{
                    line-height: 1.8;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 Reporte de Calidad de Código - F.A.R.F.A.N</h1>
                <p>Generado: {self.report_data['timestamp']}</p>
                
                <h2>📈 Métricas del Proyecto</h2>
                <div class="metrics-grid">
                    {self._generate_metrics_cards(metrics)}
                </div>
                
                <h2>✅ Recomendaciones</h2>
                <div class="recommendations">
                    <ul>
                        <li>✓ Habilitar pre-commit hooks para todos los desarrolladores</li>
                        <li>✓ Configurar pipeline de integración continua</li>
                        <li>✓ Realizar revisiones de código enfocadas en complejidad</li>
                        <li>✓ Mantener cobertura de tests por encima del 80%</li>
                        <li>✓ Documentar funciones complejas (complejidad > 10)</li>
                        <li>✓ Refactorizar módulos con índice de mantenibilidad < 20</li>
                    </ul>
                </div>
                
                <h2>🎯 Objetivos de Calidad</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value good">< 10</div>
                        <div class="metric-label">Complejidad Ciclomática Target</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value good">> 20</div>
                        <div class="metric-label">Índice Mantenibilidad Target</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value good">> 80%</div>
                        <div class="metric-label">Cobertura de Tests Target</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value good">0</div>
                        <div class="metric-label">Vulnerabilidades Críticas</div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Guardar reporte
        report_path = self.project_root / 'quality_report.html'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(report_path)
    
    def _generate_metrics_cards(self, metrics: Dict) -> str:
        """Genera HTML para las tarjetas de métricas"""
        html = ""
        
        for key, value in metrics.items():
            label = key.replace('_', ' ').title()
            html += f'''
            <div class="metric-card">
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
            </div>
            '''
        
        return html
    
    def run(self):
        """Ejecuta generación de reporte"""
        self.report_data['metrics'] = self.run_metrics()
        report_path = self.generate_html_report()
        print(f"✓ Reporte generado: {report_path}")
        return self.report_data


if __name__ == '__main__':
    generator = QualityReportGenerator()
    generator.run()

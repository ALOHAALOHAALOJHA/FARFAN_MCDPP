#!/usr/bin/env python3
"""
Generate comprehensive code quality reports
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class QualityReportGenerator:
    """Generates detailed code quality reports"""
    
    def __init__(self):
        self.project_root = Path.cwd().parent
        self.report_data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': {},
            'issues': [],
            'recommendations': []
        }
    
    def run_metrics(self) -> Dict:
        """Collect code metrics"""
        metrics = {}
        
        # Count files
        py_files = list(self.project_root.rglob('*.py'))
        metrics['total_python_files'] = len(py_files)
        
        # Count lines of code
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
        
        # Run radon for complexity metrics
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
        
        return metrics
    
    def _calculate_average_complexity(self, data: Dict) -> float:
        """Calculate average cyclomatic complexity"""
        total = 0
        count = 0
        for file_data in data.values():
            for func in file_data:
                total += func.get('complexity', 0)
                count += 1
        return total / count if count > 0 else 0
    
    def generate_html_report(self) -> str:
        """Generate HTML report"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Code Quality Report - {datetime.now().strftime('%Y-%m-%d')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .metric {{ background: #f0f0f0; padding: 10px; margin: 10px 0; }}
                .good {{ color: green; }}
                .warning {{ color: orange; }}
                .error {{ color: red; }}
            </style>
        </head>
        <body>
            <h1>Code Quality Report</h1>
            <p>Generated: {self.report_data['timestamp']}</p>
            
            <h2>Metrics</h2>
            <div class="metrics">
                {self._generate_metrics_html()}
            </div>
            
            <h2>Recommendations</h2>
            <ul>
                <li>Enable pre-commit hooks for all developers</li>
                <li>Set up continuous integration pipeline</li>
                <li>Regular code reviews focusing on complexity</li>
                <li>Maintain test coverage above 80%</li>
            </ul>
        </body>
        </html>
        """
        
        # Save report
        report_path = self.project_root / 'quality_report.html'
        with open(report_path, 'w') as f:
            f.write(html)
        
        return str(report_path)
    
    def _generate_metrics_html(self) -> str:
        """Generate HTML for metrics section"""
        metrics = self.run_metrics()
        html = ""
        for key, value in metrics.items():
            html += f'<div class="metric">{key}: <strong>{value}</strong></div>'
        return html
    
    def run(self):
        """Run report generation"""
        self.report_data['metrics'] = self.run_metrics()
        report_path = self.generate_html_report()
        print(f"Report generated: {report_path}")
        return self.report_data


if __name__ == '__main__':
    generator = QualityReportGenerator()
    generator.run()

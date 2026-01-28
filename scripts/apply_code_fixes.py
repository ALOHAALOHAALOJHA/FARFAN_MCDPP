#!/usr/bin/env python3
"""
Script de automatización para aplicar fixes de calidad de código.
Resuelve automáticamente problemas identificados en el audit.
"""

import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CodeFixAutomation:
    """Automatiza la corrección de problemas de calidad de código"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.stats = {
            'files_processed': 0,
            'fixes_applied': 0,
            'errors': []
        }
    
    def run_black(self) -> Tuple[bool, str]:
        """Aplica formateo Black a todos los archivos Python"""
        logger.info("Ejecutando Black formatter...")
        try:
            result = subprocess.run(
                ['black', '--line-length=100', '.'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info("✓ Formateo Black completado")
                return True, result.stdout
            else:
                logger.error(f"Black falló: {result.stderr}")
                return False, result.stderr
        except Exception as e:
            logger.error(f"Error ejecutando Black: {e}")
            return False, str(e)
    
    def run_isort(self) -> Tuple[bool, str]:
        """Corrige ordenamiento de imports"""
        logger.info("Ejecutando isort...")
        try:
            result = subprocess.run(
                ['isort', '--profile=black', '--line-length=100', '.'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info("✓ Ordenamiento de imports completado")
                return True, result.stdout
            else:
                logger.error(f"isort falló: {result.stderr}")
                return False, result.stderr
        except Exception as e:
            logger.error(f"Error ejecutando isort: {e}")
            return False, str(e)
    
    def run_autoflake(self) -> Tuple[bool, str]:
        """Elimina imports y variables no usadas"""
        logger.info("Ejecutando autoflake...")
        try:
            result = subprocess.run(
                [
                    'autoflake',
                    '--remove-all-unused-imports',
                    '--remove-unused-variables',
                    '--in-place',
                    '--recursive',
                    '.'
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info("✓ Eliminación de código no usado completada")
                return True, result.stdout
            else:
                logger.error(f"autoflake falló: {result.stderr}")
                return False, result.stderr
        except Exception as e:
            logger.error(f"Error ejecutando autoflake: {e}")
            return False, str(e)
    
    def run_pyupgrade(self) -> Tuple[bool, str]:
        """Actualiza sintaxis de Python a versiones modernas"""
        logger.info("Ejecutando pyupgrade...")
        try:
            # Buscar todos los archivos Python
            python_files = list(self.project_root.rglob('*.py'))
            
            for py_file in python_files:
                if any(skip in str(py_file) for skip in ['.venv', 'venv', '__pycache__']):
                    continue
                    
                result = subprocess.run(
                    ['pyupgrade', '--py312-plus', str(py_file)],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.stats['files_processed'] += 1
            
            logger.info(f"✓ Actualización de sintaxis completada para {self.stats['files_processed']} archivos")
            return True, f"Procesados {self.stats['files_processed']} archivos"
        except Exception as e:
            logger.error(f"Error ejecutando pyupgrade: {e}")
            return False, str(e)
    
    def run_ruff_fix(self) -> Tuple[bool, str]:
        """Aplica fixes automáticos con Ruff"""
        logger.info("Ejecutando Ruff fixes...")
        try:
            result = subprocess.run(
                ['ruff', 'check', '--fix', '.'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            logger.info("✓ Ruff fixes aplicados")
            return True, result.stdout
        except Exception as e:
            logger.error(f"Error ejecutando Ruff: {e}")
            return False, str(e)
    
    def fix_line_lengths(self) -> None:
        """Corrige problemas de longitud de línea en archivos Python"""
        logger.info("Corrigiendo longitud de líneas...")
        
        for py_file in self.project_root.rglob('*.py'):
            if any(skip in str(py_file) for skip in ['.venv', 'venv', '__pycache__']):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                modified = False
                new_lines = []
                
                for line in lines:
                    if len(line) > 100 and not line.strip().startswith('#'):
                        # Intentar romper líneas largas inteligentemente
                        if ',' in line:
                            # Romper en comas
                            parts = line.split(',')
                            if len(parts) > 1:
                                indent = len(line) - len(line.lstrip())
                                new_line = parts[0] + ',\n'
                                for part in parts[1:-1]:
                                    new_line += ' ' * (indent + 4) + part.strip() + ',\n'
                                new_line += ' ' * (indent + 4) + parts[-1].strip()
                                new_lines.append(new_line)
                                modified = True
                                continue
                    new_lines.append(line)
                
                if modified:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.writelines(new_lines)
                    self.stats['fixes_applied'] += 1
                    
            except Exception as e:
                logger.error(f"Error procesando {py_file}: {e}")
                self.stats['errors'].append(str(py_file))
    
    def install_pre_commit(self) -> None:
        """Instala y configura pre-commit hooks"""
        logger.info("Instalando pre-commit hooks...")
        try:
            subprocess.run(['pip', 'install', 'pre-commit'], check=True)
            subprocess.run(['pre-commit', 'install'], cwd=self.project_root, check=True)
            logger.info("✓ Pre-commit hooks instalados")
        except Exception as e:
            logger.error(f"Error instalando pre-commit: {e}")
    
    def generate_report(self) -> Dict:
        """Genera reporte de fixes aplicados"""
        report = {
            'timestamp': str(Path.cwd()),
            'stats': self.stats,
            'tools_run': [
                'black', 'isort', 'autoflake', 'pyupgrade', 'ruff'
            ]
        }
        
        # Guardar reporte
        report_path = self.project_root / 'code_fixes_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Reporte guardado en {report_path}")
        return report
    
    def apply_all_fixes(self) -> None:
        """Aplica todos los fixes automáticos en secuencia"""
        logger.info("=" * 60)
        logger.info("Iniciando fixes automáticos de código...")
        logger.info("=" * 60)
        
        # Instalar dependencias primero
        logger.info("Instalando herramientas requeridas...")
        tools = ['black', 'isort', 'autoflake', 'pyupgrade', 'flake8', 'mypy', 'ruff']
        for tool in tools:
            subprocess.run(['pip', 'install', tool], capture_output=True)
        
        # Aplicar fixes en orden
        steps = [
            ("Eliminando código no usado", self.run_autoflake),
            ("Actualizando sintaxis", self.run_pyupgrade),
            ("Ordenando imports", self.run_isort),
            ("Formateando código", self.run_black),
            ("Aplicando fixes de Ruff", self.run_ruff_fix),
        ]
        
        for step_name, step_func in steps:
            logger.info(f"\n{step_name}...")
            success, output = step_func()
            if not success:
                logger.warning(f"Paso '{step_name}' tuvo problemas pero continuando...")
        
        # Fixes adicionales
        self.fix_line_lengths()
        
        # Configurar pre-commit para el futuro
        self.install_pre_commit()
        
        # Generar reporte
        report = self.generate_report()
        
        logger.info("\n" + "=" * 60)
        logger.info("RESUMEN:")
        logger.info(f"Archivos procesados: {self.stats['files_processed']}")
        logger.info(f"Fixes aplicados: {self.stats['fixes_applied']}")
        logger.info(f"Errores encontrados: {len(self.stats['errors'])}")
        logger.info("=" * 60)
        
        return report


def main():
    """Función principal de ejecución"""
    automation = CodeFixAutomation()
    automation.apply_all_fixes()
    
    # Ejecutar validación final
    logger.info("\nEjecutando validación final...")
    result = subprocess.run(
        ['flake8', '--count', '--statistics', '--max-line-length=100'],
        cwd=automation.project_root,
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        remaining_issues = len(result.stdout.strip().split('\n'))
        logger.info(f"Problemas restantes después de automatización: {remaining_issues}")
    else:
        logger.info("✓ ¡Todos los fixes automáticos aplicados exitosamente!")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

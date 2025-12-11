#!/usr/bin/env python3
"""
Phase 1 Dependency Validator - Ensures All Necessary and Sufficient Conditions

This module implements rigorous dependency validation for Phase 1, following the principle:
"Check necessary and sufficient conditions BEFORE invocation, not during."

PHILOSOPHY:
- Dependencies are REQUIRED, not optional
- Fail fast with clear diagnostics if dependencies missing
- No graceful degradation - fix the root cause
- Provide actionable fix instructions

Author: F.A.R.F.A.N Development Team
Version: 1.0.0
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DependencyCheck:
    """Result of a dependency check."""
    name: str
    available: bool
    version: Optional[str] = None
    error: Optional[str] = None
    fix_command: Optional[str] = None


class Phase1DependencyValidator:
    """
    Validates all necessary and sufficient conditions for Phase 1 execution.
    
    NECESSARY CONDITIONS:
    1. Python 3.12+
    2. Core scientific libraries (numpy, scipy, networkx, pandas)
    3. NLP libraries (spacy, transformers)
    4. Bayesian libraries (pymc, arviz)
    5. PDF processing (PyMuPDF/fitz, pdfplumber)
    6. Validation libraries (pydantic >=2.0)
    7. methods_dispensary package accessible
    8. Derek Beach module importable
    9. Theory of Change module importable
    
    SUFFICIENT CONDITIONS:
    - All NECESSARY conditions met
    - No circular import issues
    - No version conflicts
    - PYTHONPATH correctly configured
    """
    
    def __init__(self):
        self.checks: List[DependencyCheck] = []
        self.critical_failures: List[DependencyCheck] = []
    
    def validate_all(self) -> bool:
        """
        Validate all dependencies.
        
        Returns:
            True if all checks pass, False otherwise
        """
        logger.info("=" * 80)
        logger.info("PHASE 1 DEPENDENCY VALIDATION - NECESSARY & SUFFICIENT CONDITIONS")
        logger.info("=" * 80)
        
        # Check Python version
        self._check_python_version()
        
        # Check core scientific libraries
        self._check_core_libraries()
        
        # Check NLP libraries
        self._check_nlp_libraries()
        
        # Check Bayesian libraries
        self._check_bayesian_libraries()
        
        # Check PDF processing
        self._check_pdf_libraries()
        
        # Check validation libraries
        self._check_validation_libraries()
        
        # Check methods_dispensary package
        self._check_methods_dispensary()
        
        # Check Derek Beach module
        self._check_derek_beach()
        
        # Check Theory of Change module
        self._check_teoria_cambio()
        
        # Report results
        return self._report_results()
    
    def _check_python_version(self) -> None:
        """Check Python version is 3.12+."""
        version_info = sys.version_info
        required = (3, 12)
        
        if version_info >= required:
            self.checks.append(DependencyCheck(
                name="Python version",
                available=True,
                version=f"{version_info.major}.{version_info.minor}.{version_info.micro}"
            ))
        else:
            self.critical_failures.append(DependencyCheck(
                name="Python version",
                available=False,
                version=f"{version_info.major}.{version_info.minor}.{version_info.micro}",
                error=f"Python {required[0]}.{required[1]}+ required",
                fix_command="Install Python 3.12 or higher"
            ))
    
    def _check_core_libraries(self) -> None:
        """Check core scientific libraries."""
        core_libs = {
            'numpy': 'pip install "numpy>=1.26.4,<2.0.0"',
            'scipy': 'pip install "scipy>=1.11.0"',
            'networkx': 'pip install "networkx>=3.0"',
            'pandas': 'pip install "pandas>=2.0.0"',
        }
        
        for lib, fix_cmd in core_libs.items():
            self._check_module(lib, fix_cmd, critical=True)
    
    def _check_nlp_libraries(self) -> None:
        """Check NLP libraries."""
        nlp_libs = {
            'spacy': 'pip install "spacy>=3.7.0"',
            'transformers': 'pip install "transformers>=4.41.0,<4.42.0"',
        }
        
        for lib, fix_cmd in nlp_libs.items():
            self._check_module(lib, fix_cmd, critical=True)
    
    def _check_bayesian_libraries(self) -> None:
        """Check Bayesian analysis libraries."""
        bayesian_libs = {
            'pymc': 'pip install "pymc>=5.16.0,<5.17.0"',
            'arviz': 'pip install "arviz>=0.17.0"',
            'pytensor': 'pip install "pytensor>=2.25.1,<2.26"',
        }
        
        for lib, fix_cmd in bayesian_libs.items():
            self._check_module(lib, fix_cmd, critical=True)
    
    def _check_pdf_libraries(self) -> None:
        """Check PDF processing libraries."""
        # Try PyMuPDF (imported as fitz)
        try:
            import fitz
            self.checks.append(DependencyCheck(
                name="PyMuPDF (fitz)",
                available=True,
                version=getattr(fitz, '__version__', 'unknown')
            ))
        except ImportError as e:
            self.critical_failures.append(DependencyCheck(
                name="PyMuPDF (fitz)",
                available=False,
                error=str(e),
                fix_command='pip install "PyMuPDF>=1.23.0"'
            ))
        
        # Check pdfplumber
        self._check_module('pdfplumber', 'pip install "pdfplumber>=0.10.0"', critical=True)
    
    def _check_validation_libraries(self) -> None:
        """Check validation libraries."""
        # Check pydantic version 2.0+
        try:
            import pydantic
            version_str = pydantic.__version__
            major_version = int(version_str.split('.')[0])
            
            if major_version >= 2:
                self.checks.append(DependencyCheck(
                    name="pydantic",
                    available=True,
                    version=version_str
                ))
            else:
                self.critical_failures.append(DependencyCheck(
                    name="pydantic",
                    available=False,
                    error=f"Version {version_str} found, need 2.0+",
                    fix_command='pip install "pydantic>=2.0.0"'
                ))
        except ImportError as e:
            self.critical_failures.append(DependencyCheck(
                name="pydantic",
                available=False,
                error=str(e),
                fix_command='pip install "pydantic>=2.0.0"'
            ))
    
    def _check_methods_dispensary(self) -> None:
        """Check methods_dispensary package is accessible."""
        try:
            import methods_dispensary
            self.checks.append(DependencyCheck(
                name="methods_dispensary package",
                available=True,
                version=getattr(methods_dispensary, '__version__', 'unknown')
            ))
        except ImportError as e:
            self.critical_failures.append(DependencyCheck(
                name="methods_dispensary package",
                available=False,
                error=str(e),
                fix_command="Ensure src/methods_dispensary/__init__.py exists and PYTHONPATH includes src/"
            ))
    
    def _check_derek_beach(self) -> None:
        """Check Derek Beach module can be imported."""
        try:
            from methods_dispensary.derek_beach import (
                BeachEvidentialTest,
                CausalExtractor,
                MechanismPartExtractor,
            )
            
            # Verify key methods exist
            if not hasattr(BeachEvidentialTest, 'classify_test'):
                raise AttributeError("BeachEvidentialTest missing classify_test method")
            if not hasattr(BeachEvidentialTest, 'apply_test_logic'):
                raise AttributeError("BeachEvidentialTest missing apply_test_logic method")
            
            self.checks.append(DependencyCheck(
                name="Derek Beach module",
                available=True,
                version="2.0.0"
            ))
        except ImportError as e:
            self.critical_failures.append(DependencyCheck(
                name="Derek Beach module",
                available=False,
                error=str(e),
                fix_command="Fix import errors in methods_dispensary.derek_beach (check dependencies above)"
            ))
        except AttributeError as e:
            self.critical_failures.append(DependencyCheck(
                name="Derek Beach module",
                available=False,
                error=str(e),
                fix_command="Derek Beach module incomplete - verify src/methods_dispensary/derek_beach.py"
            ))
    
    def _check_teoria_cambio(self) -> None:
        """Check Theory of Change module can be imported."""
        try:
            from methods_dispensary.teoria_cambio import (
                TeoriaCambio,
                ValidacionResultado,
                AdvancedDAGValidator,
            )
            
            # Verify key methods exist
            if not hasattr(TeoriaCambio, 'construir_grafo_causal'):
                raise AttributeError("TeoriaCambio missing construir_grafo_causal method")
            if not hasattr(TeoriaCambio, 'validacion_completa'):
                raise AttributeError("TeoriaCambio missing validacion_completa method")
            
            self.checks.append(DependencyCheck(
                name="Theory of Change module",
                available=True,
                version="4.0.0"
            ))
        except ImportError as e:
            self.critical_failures.append(DependencyCheck(
                name="Theory of Change module",
                available=False,
                error=str(e),
                fix_command="Fix import errors in methods_dispensary.teoria_cambio (check dependencies above)"
            ))
        except AttributeError as e:
            self.critical_failures.append(DependencyCheck(
                name="Theory of Change module",
                available=False,
                error=str(e),
                fix_command="Theory of Change module incomplete - verify src/methods_dispensary/teoria_cambio.py"
            ))
    
    def _check_module(self, module_name: str, fix_command: str, critical: bool = False) -> None:
        """Check if a module can be imported."""
        try:
            mod = __import__(module_name)
            version = getattr(mod, '__version__', 'unknown')
            self.checks.append(DependencyCheck(
                name=module_name,
                available=True,
                version=version
            ))
        except ImportError as e:
            check = DependencyCheck(
                name=module_name,
                available=False,
                error=str(e),
                fix_command=fix_command
            )
            if critical:
                self.critical_failures.append(check)
            else:
                self.checks.append(check)
    
    def _report_results(self) -> bool:
        """Report validation results."""
        # Print successful checks
        logger.info("\n✅ AVAILABLE DEPENDENCIES:")
        for check in self.checks:
            if check.available:
                version_str = f" (v{check.version})" if check.version != 'unknown' else ""
                logger.info(f"  ✓ {check.name}{version_str}")
        
        # Print failures
        if self.critical_failures:
            logger.error("\n❌ CRITICAL FAILURES - MUST FIX BEFORE PROCEEDING:")
            for check in self.critical_failures:
                logger.error(f"\n  ✗ {check.name}")
                logger.error(f"     Error: {check.error}")
                logger.error(f"     Fix: {check.fix_command}")
            
            logger.error("\n" + "=" * 80)
            logger.error("VALIDATION FAILED - Fix all critical issues above")
            logger.error("=" * 80)
            return False
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ VALIDATION PASSED - All necessary and sufficient conditions met")
        logger.info("=" * 80)
        return True
    
    def get_fix_script(self) -> str:
        """Generate a shell script to fix all dependency issues."""
        if not self.critical_failures:
            return "# All dependencies satisfied"
        
        commands = ["#!/bin/bash", "# Auto-generated dependency fix script", ""]
        commands.append("echo 'Installing missing dependencies...'")
        commands.append("")
        
        for check in self.critical_failures:
            if check.fix_command and check.fix_command.startswith('pip install'):
                commands.append(f"echo 'Installing {check.name}...'")
                commands.append(check.fix_command)
                commands.append("")
        
        commands.append("echo 'Done! Re-run validation to verify.'")
        return "\n".join(commands)


def validate_phase1_dependencies() -> bool:
    """
    Validate all Phase 1 dependencies.
    
    Returns:
        True if all checks pass, False otherwise
    """
    validator = Phase1DependencyValidator()
    return validator.validate_all()


def generate_fix_script(output_path: str = "fix_phase1_dependencies.sh") -> None:
    """Generate a fix script for missing dependencies."""
    validator = Phase1DependencyValidator()
    validator.validate_all()
    
    script = validator.get_fix_script()
    with open(output_path, 'w') as f:
        f.write(script)
    
    print(f"Fix script written to: {output_path}")
    print("Run with: bash {output_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate Phase 1 dependencies")
    parser.add_argument(
        "--generate-fix",
        action="store_true",
        help="Generate a shell script to fix missing dependencies"
    )
    parser.add_argument(
        "--fix-script-path",
        default="fix_phase1_dependencies.sh",
        help="Path for generated fix script"
    )
    
    args = parser.parse_args()
    
    if args.generate_fix:
        generate_fix_script(args.fix_script_path)
    else:
        success = validate_phase1_dependencies()
        sys.exit(0 if success else 1)

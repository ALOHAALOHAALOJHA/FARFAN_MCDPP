#!/usr/bin/env python3
"""
Phase 1 Pre-Import Validator - Check Before Import

Validates all dependencies BEFORE attempting to import derek_beach or teoria_cambio.
This prevents the "ERROR: Dependencia faltante" exit that happens during import.

NECESSARY CONDITIONS (checked in order):
1. Python standard library modules
2. Core scientific libraries (numpy, scipy, networkx, pandas)
3. NLP libraries (spacy)
4. Bayesian libraries (pymc, arviz, pytensor)
5. PDF libraries (PyMuPDF/fitz)
6. Validation libraries (pydantic >=2.0, yaml)
7. Fuzzy matching (fuzzywuzzy, python-Levenshtein)
8. Graph visualization (pydot)
9. farfan_pipeline modules (core.parameters, core.types, core.calibration)

SUFFICIENT CONDITION:
All NECESSARY conditions above are met.

Author: F.A.R.F.A.N Development Team
Version: 1.0.0
"""

import sys
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)


class PreImportValidator:
    """Validates dependencies before attempting imports that may sys.exit()."""
    
    def __init__(self):
        self.missing_deps: List[Tuple[str, str]] = []
        self.available_deps: List[str] = []
    
    def validate_all(self) -> bool:
        """
        Validate all dependencies needed for derek_beach and teoria_cambio.
        
        Returns:
            True if all dependencies available, False otherwise
        """
        # Core scientific
        self._check('numpy', 'pip install "numpy>=1.26.4,<2.0.0"')
        self._check('scipy', 'pip install "scipy>=1.11.0"')
        self._check('networkx', 'pip install "networkx>=3.0"')
        self._check('pandas', 'pip install "pandas>=2.0.0"')
        
        # NLP
        self._check('spacy', 'pip install "spacy>=3.7.0"')
        
        # Bayesian
        self._check('pymc', 'pip install "pymc>=5.16.0,<5.17.0"')
        self._check('arviz', 'pip install "arviz>=0.17.0"')
        self._check('pytensor', 'pip install "pytensor>=2.25.1,<2.26"')
        
        # PDF processing
        try:
            import fitz  # PyMuPDF
            self.available_deps.append('PyMuPDF (fitz)')
        except ImportError:
            self.missing_deps.append(('PyMuPDF (fitz)', 'pip install "PyMuPDF>=1.23.0"'))
        
        # Validation and data
        self._check_pydantic()
        self._check('yaml', 'pip install "PyYAML>=6.0"', import_name='yaml')
        
        # Fuzzy matching
        self._check('fuzzywuzzy', 'pip install "fuzzywuzzy>=0.18.0"')
        # python-Levenshtein is optional speedup for fuzzywuzzy
        
        # Graph visualization
        self._check('pydot', 'pip install "pydot>=1.4.0"')
        
        # farfan_pipeline core modules
        self._check_farfan_modules()
        
        return len(self.missing_deps) == 0
    
    def _check(self, module_name: str, fix_cmd: str, import_name: Optional[str] = None) -> None:
        """Check if module can be imported."""
        try:
            __import__(import_name or module_name)
            self.available_deps.append(module_name)
        except ImportError:
            self.missing_deps.append((module_name, fix_cmd))
    
    def _check_pydantic(self) -> None:
        """Check pydantic version 2.0+."""
        try:
            import pydantic
            version_str = pydantic.__version__
            major_version = int(version_str.split('.')[0])
            
            if major_version >= 2:
                self.available_deps.append(f'pydantic (v{version_str})')
            else:
                self.missing_deps.append((
                    f'pydantic (need 2.0+, found {version_str})',
                    'pip install "pydantic>=2.0.0" --upgrade'
                ))
        except ImportError:
            self.missing_deps.append(('pydantic', 'pip install "pydantic>=2.0.0"'))
    
    def _check_farfan_modules(self) -> None:
        """Check farfan_pipeline core modules."""
        farfan_modules = [
            ('farfan_pipeline.core.parameters', 'Ensure farfan-pipeline is installed: pip install -e .'),
            ('farfan_pipeline.core.types', 'Ensure farfan-pipeline is installed: pip install -e .'),
            ('farfan_pipeline.core.calibration.decorators', 'Ensure farfan-pipeline is installed: pip install -e .'),
        ]
        
        for module_name, fix_cmd in farfan_modules:
            try:
                __import__(module_name)
                self.available_deps.append(module_name)
            except ImportError:
                self.missing_deps.append((module_name, fix_cmd))
    
    def report(self) -> None:
        """Print validation report."""
        if self.available_deps:
            logger.info("✅ Available dependencies:")
            for dep in self.available_deps:
                logger.info(f"  ✓ {dep}")
        
        if self.missing_deps:
            logger.error("\n❌ MISSING DEPENDENCIES:")
            for dep_name, fix_cmd in self.missing_deps:
                logger.error(f"  ✗ {dep_name}")
                logger.error(f"     Fix: {fix_cmd}")
            logger.error("\nFix all missing dependencies before importing derek_beach or teoria_cambio")
    
    def get_fix_commands(self) -> List[str]:
        """Get list of fix commands."""
        commands = []
        for _, fix_cmd in self.missing_deps:
            if fix_cmd.startswith('pip install'):
                commands.append(fix_cmd)
        return list(set(commands))  # Deduplicate


def validate_derek_beach_dependencies() -> bool:
    """
    Validate dependencies for derek_beach module.
    
    Returns:
        True if all dependencies available, False otherwise
    
    Usage:
        from canonic_phases.Phase_one.phase1_pre_import_validator import validate_derek_beach_dependencies
        
        if validate_derek_beach_dependencies():
            from methods_dispensary.derek_beach import BeachEvidentialTest
        else:
            logger.error("Cannot import derek_beach - missing dependencies")
    """
    validator = PreImportValidator()
    success = validator.validate_all()
    
    if not success:
        validator.report()
    
    return success


def get_missing_dependencies() -> List[Tuple[str, str]]:
    """
    Get list of missing dependencies.
    
    Returns:
        List of (dependency_name, fix_command) tuples
    """
    validator = PreImportValidator()
    validator.validate_all()
    return validator.missing_deps


if __name__ == "__main__":
    validator = PreImportValidator()
    success = validator.validate_all()
    
    print("=" * 80)
    print("PHASE 1 PRE-IMPORT DEPENDENCY VALIDATION")
    print("=" * 80)
    
    if success:
        print("\n✅ ALL DEPENDENCIES AVAILABLE")
        print("Safe to import derek_beach and teoria_cambio modules")
    else:
        print("\n❌ MISSING DEPENDENCIES")
        validator.report()
        
        print("\n" + "=" * 80)
        print("FIX COMMANDS:")
        print("=" * 80)
        for cmd in validator.get_fix_commands():
            print(cmd)
    
    sys.exit(0 if success else 1)

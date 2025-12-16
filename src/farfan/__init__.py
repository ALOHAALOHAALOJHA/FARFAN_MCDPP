"""
F.A.R.F.A.N: Framework for Analytical Research on Formulation and Assessment of Norms
======================================================================================

A mechanistic policy pipeline for analyzing 170 Colombian municipal development plans.

**Usage**:
    >>> from farfan.core.orchestration import Engine
    >>> engine = Engine()
    >>> result = engine.run()

**Version**: 2.0.0 (Major Architectural Restructure)
"""

from farfan.__version__ import __version__

__all__ = [
    '__version__',
    'core',
    'phases',
    'analysis',
    'infrastructure',
    'dashboard',
    'processing',
    'utils',
]

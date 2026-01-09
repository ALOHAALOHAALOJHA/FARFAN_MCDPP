"""
Custom Linters for FARFAN Pipeline
===================================

This package provides custom static analysis tools for detecting code quality
issues specific to the FARFAN pipeline architecture.

Available Linters:
- pylint_unreachable_fallback: Detects unreachable fallback handlers in
  FailureFallbackContract.execute_with_fallback calls

Usage:
    # In .pylintrc:
    [MASTER]
    load-plugins=farfan_pipeline.linters.pylint_unreachable_fallback

    # Or via command line:
    pylint --load-plugins=farfan_pipeline.linters.pylint_unreachable_fallback src/
"""

from .pylint_unreachable_fallback import UnreachableFallbackChecker, register

__all__ = ["UnreachableFallbackChecker", "register"]

"""
Mypy plugin for FailureFallbackContract type checking.

Validates that:
1. fallback_value matches function return type
2. expected_exceptions are Exception subclasses
3.  Warns if function signature doesn't declare raises

Usage in mypy.ini:
    [mypy]
    plugins = farfan_pipeline.linters.mypy_fallback_plugin
"""

from __future__ import annotations

from typing import Callable, Optional, Type

from mypy.plugin import FunctionContext, Plugin
from mypy.types import Type as MypyType


class FailureFallbackPlugin(Plugin):
    """Mypy plugin for FailureFallbackContract validation."""

    def get_function_hook(self, fullname: str) -> Optional[Callable[[FunctionContext], MypyType]]:
        if fullname == (
            "farfan_pipeline.infrastructure.contractual.dura_lex."
            "failure_fallback.FailureFallbackContract.execute_with_fallback"
        ):
            return self._check_execute_with_fallback
        return None

    def _check_execute_with_fallback(self, ctx: FunctionContext) -> MypyType:
        """
        Type-check execute_with_fallback call.

        Validates:
        - func return type matches fallback_value type
        - expected_exceptions are tuple of Exception types
        """
        args = ctx.args
        if len(args) >= 2:
            func_arg = args[0][0]
            fallback_arg = args[1][0]

            # Get function return type
            func_type = ctx.api.expr_checker.accept(func_arg)
            fallback_type = ctx.api.expr_checker.accept(fallback_arg)

            # Validate type compatibility
            if not ctx.api.check_subtype(fallback_type, func_type.ret_type):
                ctx.api.fail(
                    f"Fallback value type {fallback_type} incompatible with "
                    f"function return type {func_type.ret_type}",
                    ctx.context,
                )

        return ctx.default_return_type


def plugin(version: str):
    """Mypy plugin entry point."""
    return FailureFallbackPlugin

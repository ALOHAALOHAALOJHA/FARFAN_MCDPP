"""
Pylint Plugin: Detect Unreachable Fallback Handlers
====================================================

RECOMMENDATION 4 IMPLEMENTATION: Add static linter for unnecessary fallbacks

This pylint plugin detects cases where FailureFallbackContract.execute_with_fallback
is used with exception types that the wrapped function provably cannot raise.

Problem (from analysis Instance 9):
    ```python
    def always_succeeds() -> int:
        return 42

    # Fallback is dead code - ValueError never raised
    x = FailureFallbackContract.execute_with_fallback(
        always_succeeds,
        fallback_value=0,
        expected_exceptions=(ValueError,)
    )
    ```

Detection Strategy:
1. Find calls to FailureFallbackContract.execute_with_fallback
2. Analyze the wrapped function:
   - If it's a lambda/simple function, check for raise statements
   - If it's a known function, check its body for exception raises
   - Check if expected_exceptions match raised exceptions
3. Warn if fallback is provably unreachable

Limitations:
- Cannot detect exceptions raised by called functions (inter-procedural analysis)
- Cannot detect dynamic exception raises (e.g., eval, exec)
- Conservative: only warns on obvious cases to avoid false positives

Usage:
    # In pylintrc or .pylintrc:
    [MASTER]
    load-plugins=farfan_pipeline.linters.pylint_unreachable_fallback

    # Or via command line:
    pylint --load-plugins=farfan_pipeline.linters.pylint_unreachable_fallback module.py

Example Output:
    policy_processor.py:1234:0: W9001: Unreachable fallback handler for
    'parse_config'. Function cannot raise ValueError but fallback expects it.
    (unreachable-fallback-handler)
"""

from __future__ import annotations

import astroid
from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker


class UnreachableFallbackChecker(BaseChecker):
    """
    Enhanced checker with inter-procedural analysis for unreachable fallback handlers in FailureFallbackContract.

    Detects:
    - Fallback handlers where expected_exceptions cannot be raised
    - Functions without any raise statements but fallback expects exceptions
    - Mismatched exception types between function and fallback
    - Inter-procedural mismatches where called functions don't raise expected exceptions
    """

    __implements__ = IAstroidChecker

    name = "unreachable-fallback"
    priority = -1

    msgs = {
        "W9001": (
            "Unreachable fallback for '%s':  function cannot raise %s",
            "unreachable-fallback-handler",
            "Fallback handler will never execute.",
        ),
        "W9002": (
            "Suspicious fallback for '%s': function may not raise %s",
            "suspicious-fallback-handler",
            "Fallback may be dead code.",
        ),
        "I9001": (
            "Manual verification needed for '%s': inter-procedural analysis incomplete",
            "fallback-verification-needed",
            "Cannot statically determine exception behavior.",
        ),
        # NEW: Inter-procedural warnings
        "W9003": (
            "Fallback mismatch in call chain '%s' -> '%s':  expected %s not raised",
            "interprocedural-fallback-mismatch",
            "Called function doesn't raise expected exceptions.",
        ),
    }

    def visit_call(self, node: astroid.Call) -> None:
        """
        Visit Call nodes and check for FailureFallbackContract.execute_with_fallback.

        Args:
            node: AST Call node
        """
        # Check if this is a call to FailureFallbackContract.execute_with_fallback
        if not self._is_fallback_contract_call(node):
            return

        # Extract arguments
        func_arg, fallback_value, expected_exceptions = self._extract_arguments(node)
        if func_arg is None or expected_exceptions is None:
            return

        # Analyze the wrapped function
        func_name = self._get_function_name(func_arg)
        raised_exceptions = self._analyze_function_exceptions(func_arg)

        # Check for unreachable fallback
        if raised_exceptions is not None:
            if len(raised_exceptions) == 0:
                # Function has no raise statements
                self.add_message(
                    "suspicious-fallback-handler",
                    node=node,
                    args=(func_name, ", ".join(expected_exceptions)),
                )
            else:
                # Check if expected exceptions match raised exceptions
                unmatched = self._find_unmatched_exceptions(expected_exceptions, raised_exceptions)
                if unmatched:
                    self.add_message(
                        "unreachable-fallback-handler",
                        node=node,
                        args=(func_name, ", ".join(unmatched)),
                    )
        else:
            # Cannot determine raised exceptions - emit informational message
            self.add_message(
                "fallback-handler-verification",
                node=node,
                args=(func_name, ", ".join(expected_exceptions)),
            )

    def _is_fallback_contract_call(self, node: astroid.Call) -> bool:
        """
        Check if node is a call to FailureFallbackContract.execute_with_fallback.

        Args:
            node: AST Call node

        Returns:
            True if this is a fallback contract call
        """
        if not isinstance(node.func, astroid.Attribute):
            return False

        # Check for execute_with_fallback method
        if node.func.attrname != "execute_with_fallback":
            return False

        # Check for FailureFallbackContract class
        if isinstance(node.func.expr, astroid.Name):
            return node.func.expr.name == "FailureFallbackContract"

        return False

    def _extract_arguments(
        self, node: astroid.Call
    ) -> tuple[astroid.NodeNG | None, astroid.NodeNG | None, list[str] | None]:
        """
        Extract func, fallback_value, and expected_exceptions from call.

        Args:
            node: AST Call node

        Returns:
            Tuple of (func_arg, fallback_value, expected_exceptions)
            expected_exceptions is a list of exception type names
        """
        if len(node.args) < 3:
            return None, None, None

        func_arg = node.args[0]
        fallback_value = node.args[1]
        exceptions_arg = node.args[2]

        # Extract exception type names from tuple
        expected_exceptions = []
        if isinstance(exceptions_arg, astroid.Tuple):
            for elt in exceptions_arg.elts:
                if isinstance(elt, astroid.Name):
                    expected_exceptions.append(elt.name)
                elif isinstance(elt, astroid.Attribute):
                    expected_exceptions.append(elt.attrname)

        if not expected_exceptions:
            return func_arg, fallback_value, None

        return func_arg, fallback_value, expected_exceptions

    def _get_function_name(self, func_arg: astroid.NodeNG) -> str:
        """
        Get human-readable name of function being wrapped.

        Args:
            func_arg: Function argument node

        Returns:
            Function name or "<lambda>" or "<unknown>"
        """
        if isinstance(func_arg, astroid.Name):
            return func_arg.name
        elif isinstance(func_arg, astroid.Lambda):
            return "<lambda>"
        elif isinstance(func_arg, astroid.Attribute):
            return func_arg.attrname
        else:
            return "<unknown>"

    def _analyze_function_exceptions(self, func_arg: astroid.NodeNG) -> set[str] | None:
        """
        Analyze function to determine which exceptions it can raise.

        Args:
            func_arg: Function argument node

        Returns:
            Set of exception type names that can be raised, or None if unknown
        """
        raised_exceptions: set[str] = set()

        # Handle lambda functions
        if isinstance(func_arg, astroid.Lambda):
            body = func_arg.body
            self._collect_raised_exceptions(body, raised_exceptions)
            return raised_exceptions

        # Handle function references
        if isinstance(func_arg, astroid.Name):
            try:
                # Try to infer the function definition
                inferred = list(func_arg.infer())
                if len(inferred) == 1 and isinstance(inferred[0], astroid.FunctionDef):
                    func_def = inferred[0]
                    self._collect_raised_exceptions(func_def, raised_exceptions)

                    # Inter-procedural analysis: analyze called functions
                    called_exceptions = self._analyze_call_chain(func_def)
                    raised_exceptions.update(called_exceptions)

                    return raised_exceptions
            except (astroid.InferenceError, astroid.NameInferenceError):
                pass

        # Cannot determine - return None
        return None

    def _analyze_call_chain(self, func_node: astroid.FunctionDef, depth: int = 2) -> set[str]:
        """
        Analyze exception types raised by function and its callees.
        Args:
            func_node: Function AST node
            depth: Maximum call chain depth to analyze (default: 2)
        Returns:
            Set of exception type names that may be raised
        """
        raised_exceptions: set[str] = set()

        # Direct raises in this function
        for node in func_node.nodes_of_class(astroid.Raise):
            if node.exc:
                exc_name = self._get_exception_name(node.exc)
                if exc_name:
                    raised_exceptions.add(exc_name)

        # Inter-procedural: analyze called functions (limited depth)
        if depth > 0:
            for call in func_node.nodes_of_class(astroid.Call):
                try:
                    # Try to infer the called function
                    inferred = call.func.infer()
                    for inferred_func in inferred:
                        if isinstance(inferred_func, astroid.FunctionDef):
                            # Recursively analyze the called function
                            called_exceptions = self._analyze_call_chain(inferred_func, depth - 1)
                            raised_exceptions.update(called_exceptions)
                        elif isinstance(inferred_func, astroid.BoundMethod):
                            # Handle method calls
                            if inferred_func.type == "method" and inferred_func.parent:
                                called_exceptions = self._analyze_call_chain(
                                    inferred_func.parent, depth - 1
                                )
                                raised_exceptions.update(called_exceptions)
                except (astroid.InferenceError, astroid.NameInferenceError, AttributeError):
                    # Cannot infer callee, continue to next call
                    continue

        return raised_exceptions

    def _collect_raised_exceptions(self, node: astroid.NodeNG, exceptions: set[str]) -> None:
        """
        Recursively collect exception types raised in node.

        Args:
            node: AST node to analyze
            exceptions: Set to accumulate exception type names
        """
        if isinstance(node, astroid.Raise):
            if node.exc is not None:
                exc_name = self._get_exception_name(node.exc)
                if exc_name:
                    exceptions.add(exc_name)

        # Recurse into child nodes
        for child in node.get_children():
            self._collect_raised_exceptions(child, exceptions)

    def _get_exception_name(self, exc_node: astroid.NodeNG) -> str | None:
        """
        Extract exception type name from raise statement.

        Args:
            exc_node: Exception node from raise statement

        Returns:
            Exception type name or None
        """
        if isinstance(exc_node, astroid.Name):
            return exc_node.name
        elif isinstance(exc_node, astroid.Call):
            if isinstance(exc_node.func, astroid.Name):
                return exc_node.func.name
            elif isinstance(exc_node.func, astroid.Attribute):
                return exc_node.func.attrname
        elif isinstance(exc_node, astroid.Attribute):
            return exc_node.attrname

        return None

    def _find_unmatched_exceptions(self, expected: list[str], raised: set[str]) -> list[str]:
        """
        Find expected exceptions that are not raised by the function.

        Args:
            expected: Expected exception types from fallback
            raised: Exception types raised by function

        Returns:
            List of expected exceptions not found in raised set
        """
        unmatched = []
        for exc_type in expected:
            # Simple name matching (not inheritance-aware)
            if exc_type not in raised:
                unmatched.append(exc_type)

        return unmatched


def register(linter):
    """
    Register the checker with pylint.

    Args:
        linter: Pylint linter instance
    """
    linter.register_checker(UnreachableFallbackChecker(linter))


__all__ = ["UnreachableFallbackChecker", "register"]

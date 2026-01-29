"""Tests for mypy plugin for FailureFallbackContract."""

import pytest
from unittest.mock import Mock, MagicMock

from farfan_pipeline.linters.mypy_fallback_plugin import FailureFallbackPlugin


class TestMypyFallbackPlugin:
    """Test mypy plugin for FailureFallbackContract type checking."""

    def test_plugin_creation(self):
        """Test that the plugin can be instantiated."""
        plugin = FailureFallbackPlugin()
        assert plugin is not None

    def test_get_function_hook_target(self):
        """Test that the plugin hooks into the correct function."""
        plugin = FailureFallbackPlugin()

        # Test the target function
        target_name = (
            "farfan_pipeline.infrastructure.contractual.dura_lex."
            "failure_fallback.FailureFallbackContract.execute_with_fallback"
        )

        hook = plugin.get_function_hook(target_name)
        assert hook is not None
        assert callable(hook)

    def test_get_function_hook_other_functions(self):
        """Test that the plugin doesn't hook into other functions."""
        plugin = FailureFallbackPlugin()

        # Test a different function
        hook = plugin.get_function_hook("some.other.function")
        assert hook is None

    def test_check_execute_with_fallback_method_exists(self):
        """Test that the checking method exists."""
        plugin = FailureFallbackPlugin()

        target_name = (
            "farfan_pipeline.infrastructure.contractual.dura_lex."
            "failure_fallback.FailureFallbackContract.execute_with_fallback"
        )

        hook = plugin.get_function_hook(target_name)
        assert hook == plugin._check_execute_with_fallback

    def test_plugin_entry_point(self):
        """Test the plugin entry point function."""
        from farfan_pipeline.linters.mypy_fallback_plugin import plugin as plugin_entry

        # This should return a plugin instance
        mypy_plugin = plugin_entry("1.0.0")
        assert isinstance(mypy_plugin, FailureFallbackPlugin)

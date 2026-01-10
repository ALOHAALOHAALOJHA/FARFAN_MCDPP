# tests/test_pylint_interprocedural.py
import astroid
from pylint.testutils import CheckerTestCase
from farfan_pipeline.linters.pylint_unreachable_fallback import UnreachableFallbackChecker


class TestPylintInterprocedural:
    """Test inter-procedural analysis in pylint plugin."""
    
    def test_interprocedural_analysis_method(self):
        """Test the new interprocedural analysis method."""
        checker = UnreachableFallbackChecker(None)
        
        # Create a simple function that raises an exception
        func_code = """
def raising_function():
    raise ValueError("test error")
"""
        func_node = astroid.extract_node(func_code)
        
        # Test the interprocedural analysis
        exceptions = checker._analyze_call_chain(func_node)
        assert "ValueError" in exceptions
    
    def test_interprocedural_analysis_with_calls(self):
        """Test interprocedural analysis when function calls another function."""
        checker = UnreachableFallbackChecker(None)
        
        # Create a function that calls another function which raises
        func_code = """
def calling_function():
    called_function()

def called_function():
    raise TypeError("another error")
"""
        module_node = astroid.parse(func_code)
        calling_func = module_node.body[0]  # calling_function
        
        # Test the interprocedural analysis
        exceptions = checker._analyze_call_chain(calling_func)
        # The called function raises TypeError, so it should be in the set
        assert "TypeError" in exceptions
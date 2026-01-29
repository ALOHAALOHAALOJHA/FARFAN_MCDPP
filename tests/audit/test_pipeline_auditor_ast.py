"""
Unit tests for AST Analyzers module.

Tests the refactored AST analysis components:
- FunctionAnalyzer
- ExceptionAnalyzer  
- ImportAnalyzer
- CompositeASTVisitor
- Integration with PipelineAuditor
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ast_analyzers import (
    AnalysisResult,
    CompositeASTVisitor,
    ExceptionAnalyzer,
    FunctionAnalyzer,
    ImportAnalyzer,
    analyze_ast,
)


# ============================================================================
# Test Fixtures
# ============================================================================

@dataclass
class MockAuditIssue:
    """Mock AuditIssue for testing."""
    severity: str
    category: str
    file_path: str
    line_number: Optional[int]
    description: str
    recommendation: str
    code_snippet: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)


def create_mock_issue(**kwargs: object) -> MockAuditIssue:
    """Factory for creating mock issues."""
    return MockAuditIssue(**kwargs)  # type: ignore[arg-type]


def mock_get_snippet(content: str, line_num: int) -> str:
    """Mock snippet getter."""
    lines = content.split('\n')
    if 0 < line_num <= len(lines):
        return lines[line_num - 1]
    return ""


class MockAuditor:
    """Mock PipelineAuditor for testing."""
    
    def __init__(self) -> None:
        self.report = MagicMock()
        self.report.issues = []
        self.import_graph: Dict[str, set] = {}
        self.function_complexity: Dict[str, int] = {}
    
    def _get_code_snippet(self, content: str, line_num: int) -> str:
        return mock_get_snippet(content, line_num)


# ============================================================================
# FunctionAnalyzer Tests
# ============================================================================

class TestFunctionAnalyzer:
    """Test suite for FunctionAnalyzer class."""
    
    def test_high_complexity_detected(self) -> None:
        """Test that high complexity functions are detected."""
        code = '''
def complex_function(a, b, c):
    if a:
        if b:
            if c:
                for i in range(10):
                    while True:
                        if a and b:
                            if c or d:
                                try:
                                    pass
                                except:
                                    pass
                                finally:
                                    pass
    return None
'''
        tree = ast.parse(code)
        func_node = tree.body[0]
        
        analyzer = FunctionAnalyzer(create_issue=create_mock_issue)
        issues = analyzer.analyze(func_node, "/test/file.py")  # type: ignore[arg-type]
        
        assert len(issues) >= 1
        assert issues[0].category == "COMPLEXITY"
        assert issues[0].severity in ("MEDIUM", "HIGH")
    
    def test_too_many_parameters_detected(self) -> None:
        """Test that functions with too many parameters are detected."""
        code = '''
def many_params(a, b, c, d, e, f, g):
    pass
'''
        tree = ast.parse(code)
        func_node = tree.body[0]
        
        analyzer = FunctionAnalyzer(create_issue=create_mock_issue)
        issues = analyzer.analyze(func_node, "/test/file.py")  # type: ignore[arg-type]
        
        assert len(issues) == 1
        assert issues[0].category == "CODE_SMELL"
        assert "7 parameters" in issues[0].description
    
    def test_normal_function_no_issues(self) -> None:
        """Test that simple functions produce no issues."""
        code = '''
def simple_function(a, b):
    return a + b
'''
        tree = ast.parse(code)
        func_node = tree.body[0]
        
        analyzer = FunctionAnalyzer(create_issue=create_mock_issue)
        issues = analyzer.analyze(func_node, "/test/file.py")  # type: ignore[arg-type]
        
        assert len(issues) == 0
    
    def test_cyclomatic_complexity_calculation(self) -> None:
        """Test accurate cyclomatic complexity calculation."""
        # Simple function: complexity = 1
        simple = ast.parse("def f(): pass").body[0]
        assert FunctionAnalyzer._calculate_cyclomatic_complexity(simple) == 1
        
        # Function with if: complexity = 2
        with_if = ast.parse("def f():\n if x: pass").body[0]
        assert FunctionAnalyzer._calculate_cyclomatic_complexity(with_if) == 2
        
        # Function with for: complexity = 2
        with_for = ast.parse("def f():\n for i in x: pass").body[0]
        assert FunctionAnalyzer._calculate_cyclomatic_complexity(with_for) == 2
        
        # Function with boolean and: complexity = 2
        with_and = ast.parse("def f():\n if x and y: pass").body[0]
        assert FunctionAnalyzer._calculate_cyclomatic_complexity(with_and) == 3


# ============================================================================
# ExceptionAnalyzer Tests
# ============================================================================

class TestExceptionAnalyzer:
    """Test suite for ExceptionAnalyzer class."""
    
    def test_bare_except_with_pass_detected(self) -> None:
        """Test that bare except with pass is detected."""
        code = '''
try:
    x = 1
except:
    pass
'''
        tree = ast.parse(code)
        try_node = tree.body[0]
        
        analyzer = ExceptionAnalyzer(
            create_issue=create_mock_issue,
            get_snippet=mock_get_snippet
        )
        issues = analyzer.analyze(try_node, "/test/file.py", code)  # type: ignore[arg-type]
        
        assert len(issues) == 1
        assert issues[0].category == "SILENCED_ERROR"
        assert issues[0].severity == "HIGH"
    
    def test_exception_with_pass_detected(self) -> None:
        """Test that Exception with pass is detected."""
        code = '''
try:
    x = 1
except Exception:
    pass
'''
        tree = ast.parse(code)
        try_node = tree.body[0]
        
        analyzer = ExceptionAnalyzer(
            create_issue=create_mock_issue,
            get_snippet=mock_get_snippet
        )
        issues = analyzer.analyze(try_node, "/test/file.py", code)  # type: ignore[arg-type]
        
        assert len(issues) == 1
        assert issues[0].category == "SILENCED_ERROR"
    
    def test_proper_exception_handling_no_issue(self) -> None:
        """Test that proper exception handling produces no issues."""
        code = '''
try:
    x = 1
except ValueError as e:
    print(e)
'''
        tree = ast.parse(code)
        try_node = tree.body[0]
        
        analyzer = ExceptionAnalyzer(
            create_issue=create_mock_issue,
            get_snippet=mock_get_snippet
        )
        issues = analyzer.analyze(try_node, "/test/file.py", code)  # type: ignore[arg-type]
        
        assert len(issues) == 0
    
    def test_exception_with_logging_no_issue(self) -> None:
        """Test that Exception with logging produces no issues."""
        code = '''
try:
    x = 1
except Exception as e:
    logger.error(e)
'''
        tree = ast.parse(code)
        try_node = tree.body[0]
        
        analyzer = ExceptionAnalyzer(
            create_issue=create_mock_issue,
            get_snippet=mock_get_snippet
        )
        issues = analyzer.analyze(try_node, "/test/file.py", code)  # type: ignore[arg-type]
        
        assert len(issues) == 0


# ============================================================================
# ImportAnalyzer Tests
# ============================================================================

class TestImportAnalyzer:
    """Test suite for ImportAnalyzer class."""
    
    def test_import_statement_tracked(self) -> None:
        """Test that import statements are tracked."""
        code = "import os, sys, json"
        tree = ast.parse(code)
        import_node = tree.body[0]
        
        analyzer = ImportAnalyzer()
        imports = analyzer.analyze_import(import_node)  # type: ignore[arg-type]
        
        assert imports == {"os", "sys", "json"}
    
    def test_from_import_tracked(self) -> None:
        """Test that from-import statements are tracked."""
        code = "from pathlib import Path"
        tree = ast.parse(code)
        import_node = tree.body[0]
        
        analyzer = ImportAnalyzer()
        imports = analyzer.analyze_from_import(import_node)  # type: ignore[arg-type]
        
        assert imports == {"pathlib"}
    
    def test_relative_import_empty(self) -> None:
        """Test that relative imports without module return empty set."""
        code = "from . import something"
        tree = ast.parse(code)
        import_node = tree.body[0]
        
        analyzer = ImportAnalyzer()
        imports = analyzer.analyze_from_import(import_node)  # type: ignore[arg-type]
        
        assert imports == set()


# ============================================================================
# AnalysisResult Tests
# ============================================================================

class TestAnalysisResult:
    """Test suite for AnalysisResult dataclass."""
    
    def test_merge_combines_results(self) -> None:
        """Test that merge combines two results correctly."""
        result1 = AnalysisResult(
            issues=[MagicMock()],
            imports={"os", "sys"},
            function_complexity={"func1": 5}
        )
        result2 = AnalysisResult(
            issues=[MagicMock()],
            imports={"json"},
            function_complexity={"func2": 10}
        )
        
        result1.merge(result2)
        
        assert len(result1.issues) == 2
        assert result1.imports == {"os", "sys", "json"}
        assert result1.function_complexity == {"func1": 5, "func2": 10}


# ============================================================================
# Integration Tests
# ============================================================================

class TestAnalyzeAstIntegration:
    """Integration tests for the full analysis pipeline."""
    
    def test_full_analysis_produces_correct_issues(self) -> None:
        """Test that full analysis detects expected issues."""
        code = '''
def problematic_function(a, b, c, d, e, f, g):
    try:
        x = 1
    except:
        pass
    return a + b
'''
        tree = ast.parse(code)
        auditor = MockAuditor()
        
        with patch('ast_analyzers.AuditIssue', MockAuditIssue):
            result = analyze_ast(
                auditor,  # type: ignore[arg-type]
                tree, 
                Path("/test/file.py"),
                code
            )
        
        # Should detect too many parameters
        param_issues = [i for i in result.issues if i.category == "CODE_SMELL"]
        assert len(param_issues) >= 1
        
        # Should detect silenced exception
        exception_issues = [i for i in result.issues if i.category == "SILENCED_ERROR"]
        assert len(exception_issues) >= 1
    
    def test_imports_tracked_correctly(self) -> None:
        """Test that imports are correctly tracked."""
        code = '''
import os
import sys
from pathlib import Path
from typing import List
'''
        tree = ast.parse(code)
        auditor = MockAuditor()
        
        with patch('ast_analyzers.AuditIssue', MockAuditIssue):
            result = analyze_ast(
                auditor,  # type: ignore[arg-type]
                tree, 
                Path("/test/file.py"),
                code
            )
        
        assert "os" in result.imports
        assert "sys" in result.imports
        assert "pathlib" in result.imports
        assert "typing" in result.imports
    
    def test_no_regression_complex_file(self) -> None:
        """Test that complex files are analyzed without errors."""
        code = '''
import ast
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Example:
    value: int

class Processor:
    def process(self, items: List[Example]) -> Optional[Example]:
        if not items:
            return None
        for item in items:
            if item.value > 10:
                try:
                    return self._transform(item)
                except ValueError as e:
                    print(f"Error: {e}")
        return items[0]
    
    def _transform(self, item: Example) -> Example:
        return Example(item.value * 2)
'''
        tree = ast.parse(code)
        auditor = MockAuditor()
        
        with patch('ast_analyzers.AuditIssue', MockAuditIssue):
            # Should not raise any exceptions
            result = analyze_ast(
                auditor,  # type: ignore[arg-type]
                tree, 
                Path("/test/file.py"),
                code
            )
        
        # Should have tracked imports
        assert len(result.imports) > 0
        
        # Should have recorded function complexities
        assert "process" in result.function_complexity
        assert "_transform" in result.function_complexity


# ============================================================================
# Complexity Verification
# ============================================================================

class TestComplexityReduction:
    """Verify that the refactoring achieved complexity goals."""
    
    def test_function_analyzer_complexity_below_threshold(self) -> None:
        """Verify FunctionAnalyzer methods have low complexity."""
        import ast_analyzers
        
        source = Path(ast_analyzers.__file__).read_text()
        tree = ast.parse(source)
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity = FunctionAnalyzer._calculate_cyclomatic_complexity(node)
                # Each method should have complexity < 8
                assert complexity < 8, (
                    f"Method {node.name} has complexity {complexity}, exceeds target of 8"
                )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

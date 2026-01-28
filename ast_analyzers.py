"""
AST Analyzers Module for Pipeline Audit Script.

Provides specialized analyzer classes for Abstract Syntax Tree analysis,
extracted from the original monolithic _analyze_ast function.

This module reduces cyclomatic complexity by separating concerns into:
- FunctionAnalyzer: Function definition analysis
- ExceptionAnalyzer: Exception handling pattern analysis
- ImportAnalyzer: Import tracking
- CompositeASTVisitor: Main visitor coordinating all analyzers
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Set, Tuple

if TYPE_CHECKING:
    from pipeline_audit_script import AuditIssue, PipelineAuditor


@dataclass
class AnalysisResult:
    """Structured result from AST analysis."""
    
    issues: List[AuditIssue] = field(default_factory=list)
    imports: Set[str] = field(default_factory=set)
    function_complexity: Dict[str, int] = field(default_factory=dict)
    
    def merge(self, other: AnalysisResult) -> None:
        """Merge another result into this one."""
        self.issues.extend(other.issues)
        self.imports.update(other.imports)
        self.function_complexity.update(other.function_complexity)


class FunctionAnalyzer:
    """Analyze function definitions for complexity and code smells.
    
    Responsibilities:
    - Calculate cyclomatic complexity
    - Check parameter count
    - Track function line ranges
    """
    
    COMPLEXITY_THRESHOLD_MEDIUM = 10
    COMPLEXITY_THRESHOLD_HIGH = 15
    MAX_PARAMETERS = 5
    
    def __init__(self, create_issue: Callable[..., AuditIssue]) -> None:
        """Initialize with issue factory function."""
        self._create_issue = create_issue
        self.function_lines: Dict[str, Tuple[int, Optional[int]]] = {}
    
    def analyze(
        self, 
        node: ast.FunctionDef, 
        file_path: str
    ) -> List[AuditIssue]:
        """Analyze a function definition node."""
        issues: List[AuditIssue] = []
        
        # Track function line range
        self.function_lines[node.name] = (node.lineno, node.end_lineno)
        
        # Check complexity
        issues.extend(self._check_complexity(node, file_path))
        
        # Check parameters
        issues.extend(self._check_parameters(node, file_path))
        
        return issues
    
    def _check_complexity(
        self, 
        node: ast.FunctionDef, 
        file_path: str
    ) -> List[AuditIssue]:
        """Check function cyclomatic complexity."""
        complexity = self._calculate_cyclomatic_complexity(node)
        
        if complexity <= self.COMPLEXITY_THRESHOLD_MEDIUM:
            return []
        
        severity = (
            "MEDIUM" if complexity < self.COMPLEXITY_THRESHOLD_HIGH else "HIGH"
        )
        
        return [self._create_issue(
            severity=severity,
            category="COMPLEXITY",
            file_path=file_path,
            line_number=node.lineno,
            description=f"Function '{node.name}' has high cyclomatic complexity: {complexity}",
            recommendation="Consider refactoring to reduce complexity",
            metrics={"complexity": complexity}
        )]
    
    def _check_parameters(
        self, 
        node: ast.FunctionDef, 
        file_path: str
    ) -> List[AuditIssue]:
        """Check for too many function parameters."""
        param_count = len(node.args.args)
        
        if param_count <= self.MAX_PARAMETERS:
            return []
        
        return [self._create_issue(
            severity="LOW",
            category="CODE_SMELL",
            file_path=file_path,
            line_number=node.lineno,
            description=f"Function '{node.name}' has {param_count} parameters",
            recommendation="Consider using configuration objects or reducing parameters"
        )]
    
    @staticmethod
    def _calculate_cyclomatic_complexity(node: ast.AST) -> int:
        """Calculate cyclomatic complexity for an AST node."""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.With):
                complexity += 1
            elif isinstance(child, ast.Assert):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity


class ExceptionAnalyzer:
    """Analyze exception handling patterns for code quality issues.
    
    Detects:
    - Bare except clauses
    - Overly broad exception handlers
    - Silenced exceptions (pass statement in handler)
    """
    
    BROAD_EXCEPTIONS = frozenset({'Exception', 'BaseException'})
    
    def __init__(
        self, 
        create_issue: Callable[..., AuditIssue],
        get_snippet: Callable[[str, int], str]
    ) -> None:
        """Initialize with issue factory and snippet getter."""
        self._create_issue = create_issue
        self._get_snippet = get_snippet
    
    def analyze(
        self, 
        node: ast.Try, 
        file_path: str, 
        content: str
    ) -> List[AuditIssue]:
        """Analyze a try block for exception handling issues."""
        issues: List[AuditIssue] = []
        
        for handler in node.handlers:
            if self._is_silenced_exception(handler):
                issues.append(self._create_silenced_exception_issue(
                    handler, file_path, content
                ))
        
        return issues
    
    def _is_silenced_exception(self, handler: ast.ExceptHandler) -> bool:
        """Check if exception handler silences the exception."""
        # Check for bare except or broad exception type
        is_broad = (
            handler.type is None or
            (isinstance(handler.type, ast.Name) and 
             handler.type.id in self.BROAD_EXCEPTIONS)
        )
        
        # Check for pass-only body
        is_pass_only = (
            len(handler.body) == 1 and 
            isinstance(handler.body[0], ast.Pass)
        )
        
        return is_broad and is_pass_only
    
    def _create_silenced_exception_issue(
        self, 
        handler: ast.ExceptHandler, 
        file_path: str, 
        content: str
    ) -> AuditIssue:
        """Create an issue for silenced exception."""
        return self._create_issue(
            severity="HIGH",
            category="SILENCED_ERROR",
            file_path=file_path,
            line_number=handler.lineno,
            description="Silenced exception with pass statement",
            recommendation="Log exceptions or handle them appropriately",
            code_snippet=self._get_snippet(content, handler.lineno)
        )


class ImportAnalyzer:
    """Track imports for dependency analysis.
    
    Handles both:
    - import statements
    - from ... import statements
    """
    
    def analyze_import(self, node: ast.Import) -> Set[str]:
        """Analyze an import statement."""
        return {alias.name for alias in node.names}
    
    def analyze_from_import(self, node: ast.ImportFrom) -> Set[str]:
        """Analyze a from-import statement."""
        if node.module:
            return {node.module}
        return set()


class CompositeASTVisitor(ast.NodeVisitor):
    """Composite AST visitor coordinating specialized analyzers.
    
    This class serves as the orchestrator, delegating specific
    analysis tasks to specialized analyzer classes.
    """
    
    def __init__(
        self, 
        auditor: PipelineAuditor, 
        file_path: Path, 
        content: str
    ) -> None:
        """Initialize the composite visitor with all analyzers."""
        self.auditor = auditor
        self.file_path = file_path
        self.content = content
        
        # Initialize specialized analyzers
        self._function_analyzer = FunctionAnalyzer(
            create_issue=self._create_issue
        )
        self._exception_analyzer = ExceptionAnalyzer(
            create_issue=self._create_issue,
            get_snippet=self.auditor._get_code_snippet
        )
        self._import_analyzer = ImportAnalyzer()
        
        # Collected results
        self.result = AnalysisResult()
    
    def _create_issue(self, **kwargs: object) -> AuditIssue:
        """Factory method to create AuditIssue instances."""
        from pipeline_audit_script import AuditIssue
        return AuditIssue(**kwargs)  # type: ignore[arg-type]
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Delegate function analysis to FunctionAnalyzer."""
        issues = self._function_analyzer.analyze(node, str(self.file_path))
        self.result.issues.extend(issues)
        
        # Store complexity for reporting
        complexity = FunctionAnalyzer._calculate_cyclomatic_complexity(node)
        self.result.function_complexity[node.name] = complexity
        
        self.generic_visit(node)
    
    # Also handle async functions
    visit_AsyncFunctionDef = visit_FunctionDef
    
    def visit_Try(self, node: ast.Try) -> None:
        """Delegate exception analysis to ExceptionAnalyzer."""
        issues = self._exception_analyzer.analyze(
            node, str(self.file_path), self.content
        )
        self.result.issues.extend(issues)
        self.generic_visit(node)
    
    def visit_Import(self, node: ast.Import) -> None:
        """Delegate import tracking to ImportAnalyzer."""
        imports = self._import_analyzer.analyze_import(node)
        self.result.imports.update(imports)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Delegate from-import tracking to ImportAnalyzer."""
        imports = self._import_analyzer.analyze_from_import(node)
        self.result.imports.update(imports)
        self.generic_visit(node)


def analyze_ast(
    auditor: PipelineAuditor,
    tree: ast.AST, 
    file_path: Path, 
    content: str
) -> AnalysisResult:
    """
    Analyze an Abstract Syntax Tree using specialized analyzers.
    
    This function replaces the monolithic _analyze_ast method,
    providing the same functionality with reduced complexity.
    
    Args:
        auditor: The PipelineAuditor instance for reporting
        tree: The parsed AST to analyze
        file_path: Path to the source file
        content: Raw source file content
        
    Returns:
        AnalysisResult containing issues, imports, and complexity data
    """
    visitor = CompositeASTVisitor(auditor, file_path, content)
    visitor.visit(tree)
    return visitor.result

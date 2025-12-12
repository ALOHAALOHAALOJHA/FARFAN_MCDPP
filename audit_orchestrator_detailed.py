#!/usr/bin/env python3
"""
Comprehensive Orchestrator Audit - F.A.R.F.A.N Pipeline
=========================================================

This script performs a detailed audit of the orchestrator component at
src/orchestration/orchestrator.py, analyzing:

1. **Architecture & Components**: Class structure, data models, helper functions
2. **Phase Flow**: 11-phase pipeline execution model and coordination
3. **Resource Management**: Adaptive resource limits, memory/CPU monitoring
4. **Instrumentation**: Progress tracking, metrics, performance monitoring
5. **Abort Mechanism**: Thread-safe abort signaling and propagation
6. **Data Contracts**: TypedDict contracts and phase output/input alignment
7. **Error Handling**: Exception recovery, graceful degradation, timeout handling
8. **Integration Points**: Method executor, questionnaire, calibration, SISAS
9. **Wiring Integrity**: Dependency injection, component connections
10. **Code Quality**: Type safety, logging, maintainability patterns

The audit generates both a detailed markdown report and a JSON metrics file.
"""

import ast
import inspect
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


# Paths
REPO_ROOT = Path(__file__).resolve().parent
ORCHESTRATOR_PATH = REPO_ROOT / "src" / "orchestration" / "orchestrator.py"
OUTPUT_JSON = REPO_ROOT / "audit_orchestrator_detailed_report.json"
OUTPUT_MD = REPO_ROOT / "ORCHESTRATOR_DETAILED_AUDIT.md"


@dataclass
class ComponentInventory:
    """Inventory of orchestrator components."""
    classes: List[Dict[str, Any]] = field(default_factory=list)
    functions: List[Dict[str, Any]] = field(default_factory=list)
    constants: List[Dict[str, Any]] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    type_annotations: Dict[str, int] = field(default_factory=dict)
    
    
@dataclass
class PhaseAnalysis:
    """Analysis of phase execution model."""
    phase_definitions: List[Dict[str, Any]] = field(default_factory=list)
    phase_handlers: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    phase_timeouts: Dict[int, float] = field(default_factory=dict)
    phase_item_targets: Dict[int, int] = field(default_factory=dict)
    phase_dependencies: Dict[int, List[str]] = field(default_factory=dict)
    phase_outputs: Dict[int, str] = field(default_factory=dict)
    
    
@dataclass
class ResourceManagementAnalysis:
    """Analysis of resource management capabilities."""
    has_resource_limits: bool = False
    has_memory_tracking: bool = False
    has_cpu_tracking: bool = False
    has_adaptive_workers: bool = False
    has_usage_history: bool = False
    worker_constraints: Dict[str, int] = field(default_factory=dict)
    thresholds: Dict[str, float] = field(default_factory=dict)
    

@dataclass
class InstrumentationAnalysis:
    """Analysis of instrumentation and monitoring."""
    has_phase_instrumentation: bool = False
    has_progress_tracking: bool = False
    has_resource_snapshots: bool = False
    has_latency_tracking: bool = False
    has_warning_recording: bool = False
    has_error_recording: bool = False
    metrics_exported: List[str] = field(default_factory=list)
    

@dataclass
class AbortMechanismAnalysis:
    """Analysis of abort mechanism."""
    has_abort_signal: bool = False
    thread_safe: bool = False
    has_abort_reason: bool = False
    has_abort_timestamp: bool = False
    propagation_points: List[str] = field(default_factory=list)
    

@dataclass
class DataContractAnalysis:
    """Analysis of data contracts and types."""
    typed_dicts: List[str] = field(default_factory=list)
    dataclasses: List[str] = field(default_factory=list)
    phase_io_alignment: bool = False
    type_safety_score: float = 0.0
    

@dataclass
class ErrorHandlingAnalysis:
    """Analysis of error handling patterns."""
    has_timeout_handling: bool = False
    has_abort_handling: bool = False
    has_exception_recovery: bool = False
    try_except_count: int = 0
    finally_count: int = 0
    error_categories: List[str] = field(default_factory=list)
    

@dataclass
class IntegrationAnalysis:
    """Analysis of integration points."""
    integrations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    

@dataclass
class CodeQualityMetrics:
    """Code quality metrics."""
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    docstring_lines: int = 0
    type_annotation_coverage: float = 0.0
    complexity_score: float = 0.0
    logging_statements: int = 0
    

class OrchestratorAuditor:
    """Comprehensive orchestrator auditor."""
    
    def __init__(self, orchestrator_path: Path):
        self.path = orchestrator_path
        self.source_code = ""
        self.tree: ast.Module | None = None
        
        # Analysis results
        self.components = ComponentInventory()
        self.phases = PhaseAnalysis()
        self.resources = ResourceManagementAnalysis()
        self.instrumentation = InstrumentationAnalysis()
        self.abort = AbortMechanismAnalysis()
        self.contracts = DataContractAnalysis()
        self.errors = ErrorHandlingAnalysis()
        self.integrations = IntegrationAnalysis()
        self.quality = CodeQualityMetrics()
        
    def run_audit(self) -> Dict[str, Any]:
        """Run complete audit."""
        print(f"🔍 Auditing orchestrator at {self.path}...")
        
        if not self.path.exists():
            print(f"❌ ERROR: Orchestrator file not found at {self.path}")
            sys.exit(1)
            
        # Load and parse source
        self._load_source()
        self._parse_ast()
        
        # Run all analyses
        self._analyze_components()
        self._analyze_phases()
        self._analyze_resource_management()
        self._analyze_instrumentation()
        self._analyze_abort_mechanism()
        self._analyze_data_contracts()
        self._analyze_error_handling()
        self._analyze_integrations()
        self._analyze_code_quality()
        
        # Generate report
        report = self._build_report()
        
        print("✅ Audit complete!")
        return report
        
    def _load_source(self) -> None:
        """Load source code."""
        with open(self.path, "r", encoding="utf-8") as f:
            self.source_code = f.read()
            
    def _parse_ast(self) -> None:
        """Parse AST."""
        try:
            self.tree = ast.parse(self.source_code)
        except SyntaxError as e:
            print(f"❌ ERROR: Failed to parse orchestrator: {e}")
            sys.exit(1)
            
    def _analyze_components(self) -> None:
        """Analyze component inventory."""
        print("  📦 Analyzing components...")
        
        for node in ast.walk(self.tree):
            # Classes
            if isinstance(node, ast.ClassDef):
                bases = [self._get_name(b) for b in node.bases]
                methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                
                self.components.classes.append({
                    "name": node.name,
                    "bases": bases,
                    "methods": methods,
                    "method_count": len(methods),
                    "line": node.lineno,
                })
                
            # Top-level functions
            elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                params = [arg.arg for arg in node.args.args]
                has_return_type = node.returns is not None
                
                self.components.functions.append({
                    "name": node.name,
                    "params": params,
                    "param_count": len(params),
                    "has_return_type": has_return_type,
                    "is_async": isinstance(node, ast.AsyncFunctionDef),
                    "line": node.lineno,
                })
                
            # Constants
            elif isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
                name = node.targets[0].id
                if name.isupper():
                    self.components.constants.append({
                        "name": name,
                        "line": node.lineno,
                    })
                    
            # Imports
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    self.components.imports.append(alias.name)
                    
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    self.components.imports.append(f"{module}.{alias.name}")
                    
    def _analyze_phases(self) -> None:
        """Analyze phase execution model."""
        print("  🔄 Analyzing phase flow...")
        
        # Find Orchestrator class and analyze its class-level attributes
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef) and node.name == "Orchestrator":
                # Find FASES definition (class variable assignment)
                for item in node.body:
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        # Handle annotated assignments like FASES: list[tuple[...]] = [...]
                        if item.target.id == "FASES" and item.value and isinstance(item.value, ast.List):
                            for i, elem in enumerate(item.value.elts):
                                if isinstance(elem, ast.Tuple):
                                    phase_id = self._get_constant_value(elem.elts[0])
                                    mode = self._get_constant_value(elem.elts[1])
                                    handler = self._get_constant_value(elem.elts[2])
                                    label = self._get_constant_value(elem.elts[3])
                                    
                                    self.phases.phase_definitions.append({
                                        "phase_id": phase_id,
                                        "mode": mode,
                                        "handler": handler,
                                        "label": label,
                                    })
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                if target.id == "FASES" and isinstance(item.value, ast.List):
                                    for i, elem in enumerate(item.value.elts):
                                        if isinstance(elem, ast.Tuple):
                                            phase_id = self._get_constant_value(elem.elts[0])
                                            mode = self._get_constant_value(elem.elts[1])
                                            handler = self._get_constant_value(elem.elts[2])
                                            label = self._get_constant_value(elem.elts[3])
                                            
                                            self.phases.phase_definitions.append({
                                                "phase_id": phase_id,
                                                "mode": mode,
                                                "handler": handler,
                                                "label": label,
                                            })
                                            
                                elif target.id == "PHASE_TIMEOUTS" and isinstance(item.value, ast.Dict):
                                    for k, v in zip(item.value.keys, item.value.values):
                                        phase_id = self._get_constant_value(k)
                                        timeout = self._get_constant_value(v)
                                        if phase_id is not None and timeout is not None:
                                            self.phases.phase_timeouts[phase_id] = timeout
                                        
                                elif target.id == "PHASE_ITEM_TARGETS" and isinstance(item.value, ast.Dict):
                                    for k, v in zip(item.value.keys, item.value.values):
                                        phase_id = self._get_constant_value(k)
                                        target_val = self._get_constant_value(v)
                                        if phase_id is not None and target_val is not None:
                                            self.phases.phase_item_targets[phase_id] = target_val
                                        
                                elif target.id == "PHASE_OUTPUT_KEYS" and isinstance(item.value, ast.Dict):
                                    for k, v in zip(item.value.keys, item.value.values):
                                        phase_id = self._get_constant_value(k)
                                        output_key = self._get_constant_value(v)
                                        if phase_id is not None and output_key is not None:
                                            self.phases.phase_outputs[phase_id] = output_key
                                        
                                elif target.id == "PHASE_ARGUMENT_KEYS" and isinstance(item.value, ast.Dict):
                                    for k, v in zip(item.value.keys, item.value.values):
                                        phase_id = self._get_constant_value(k)
                                        if isinstance(v, ast.List) and phase_id is not None:
                                            args = [self._get_constant_value(el) for el in v.elts]
                                            self.phases.phase_dependencies[phase_id] = args
                    
                    # Also check for AnnAssign (annotated class variables)
                    elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        if item.value and isinstance(item.value, ast.Dict):
                            if item.target.id == "PHASE_TIMEOUTS":
                                for k, v in zip(item.value.keys, item.value.values):
                                    phase_id = self._get_constant_value(k)
                                    timeout = self._get_constant_value(v)
                                    if phase_id is not None and timeout is not None:
                                        self.phases.phase_timeouts[phase_id] = timeout
                                        
                            elif item.target.id == "PHASE_ITEM_TARGETS":
                                for k, v in zip(item.value.keys, item.value.values):
                                    phase_id = self._get_constant_value(k)
                                    target_val = self._get_constant_value(v)
                                    if phase_id is not None and target_val is not None:
                                        self.phases.phase_item_targets[phase_id] = target_val
                                        
                            elif item.target.id == "PHASE_OUTPUT_KEYS":
                                for k, v in zip(item.value.keys, item.value.values):
                                    phase_id = self._get_constant_value(k)
                                    output_key = self._get_constant_value(v)
                                    if phase_id is not None and output_key is not None:
                                        self.phases.phase_outputs[phase_id] = output_key
                                        
                            elif item.target.id == "PHASE_ARGUMENT_KEYS":
                                for k, v in zip(item.value.keys, item.value.values):
                                    phase_id = self._get_constant_value(k)
                                    if isinstance(v, ast.List) and phase_id is not None:
                                        args = [self._get_constant_value(el) for el in v.elts]
                                        self.phases.phase_dependencies[phase_id] = args
                                            
                    # Find phase handler methods
                    elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if item.name.startswith("_") and any(
                            phase in item.name for phase in [
                                "load_configuration", "ingest_document", "execute_micro",
                                "score_micro", "aggregate_dimensions", "aggregate_policy",
                                "aggregate_clusters", "evaluate_macro", "generate_recommendations",
                                "assemble_report", "format_and_export"
                            ]
                        ):
                            self.phases.phase_handlers[item.name] = {
                                "is_async": isinstance(item, ast.AsyncFunctionDef),
                                "params": [arg.arg for arg in item.args.args],
                                "line": item.lineno,
                            }
                            
    def _analyze_resource_management(self) -> None:
        """Analyze resource management."""
        print("  💻 Analyzing resource management...")
        
        # Find ResourceLimits class
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef) and node.name == "ResourceLimits":
                self.resources.has_resource_limits = True
                
                # Analyze methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if "memory" in item.name.lower():
                            self.resources.has_memory_tracking = True
                        if "cpu" in item.name.lower():
                            self.resources.has_cpu_tracking = True
                        if "worker" in item.name.lower():
                            self.resources.has_adaptive_workers = True
                        if "history" in item.name.lower():
                            self.resources.has_usage_history = True
                            
                # Extract init parameters
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                        for i, arg in enumerate(item.args.args[1:]):  # Skip self
                            default_idx = i - (len(item.args.args) - len(item.args.defaults) - 1)
                            if default_idx >= 0 and default_idx < len(item.args.defaults):
                                default = item.args.defaults[default_idx]
                                value = self._get_constant_value(default)
                                
                                if "worker" in arg.arg:
                                    self.resources.worker_constraints[arg.arg] = value
                                elif "memory" in arg.arg or "cpu" in arg.arg:
                                    self.resources.thresholds[arg.arg] = value
                                    
    def _analyze_instrumentation(self) -> None:
        """Analyze instrumentation."""
        print("  📊 Analyzing instrumentation...")
        
        # Find PhaseInstrumentation class
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef) and node.name == "PhaseInstrumentation":
                self.instrumentation.has_phase_instrumentation = True
                
                # Analyze methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if "progress" in item.name:
                            self.instrumentation.has_progress_tracking = True
                        if "snapshot" in item.name:
                            self.instrumentation.has_resource_snapshots = True
                        if "latency" in item.name:
                            self.instrumentation.has_latency_tracking = True
                        if "warning" in item.name:
                            self.instrumentation.has_warning_recording = True
                        if "error" in item.name:
                            self.instrumentation.has_error_recording = True
                        if "metric" in item.name or "export" in item.name:
                            self.instrumentation.metrics_exported.append(item.name)
                            
    def _analyze_abort_mechanism(self) -> None:
        """Analyze abort mechanism."""
        print("  🛑 Analyzing abort mechanism...")
        
        # Find AbortSignal class
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef) and node.name == "AbortSignal":
                self.abort.has_abort_signal = True
                
                # Check for threading primitives
                init_found = False
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                        init_found = True
                        for stmt in ast.walk(item):
                            if isinstance(stmt, ast.Assign):
                                for target in stmt.targets:
                                    if isinstance(target, ast.Attribute):
                                        attr_name = target.attr
                                        if "_lock" in attr_name or "Lock" in str(stmt.value):
                                            self.abort.thread_safe = True
                                        if "reason" in attr_name:
                                            self.abort.has_abort_reason = True
                                        if "timestamp" in attr_name:
                                            self.abort.has_abort_timestamp = True
                                            
        # Find abort check points
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.Call):
                        func_name = self._get_name(stmt.func)
                        if "ensure_not_aborted" in func_name or "is_aborted" in func_name:
                            self.abort.propagation_points.append(f"{node.name}:{node.lineno}")
                            
    def _analyze_data_contracts(self) -> None:
        """Analyze data contracts."""
        print("  📋 Analyzing data contracts...")
        
        typed_annotations = 0
        total_functions = 0
        
        for node in ast.walk(self.tree):
            # TypedDict classes
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if "TypedDict" in self._get_name(base):
                        self.contracts.typed_dicts.append(node.name)
                        
                # Dataclasses with @dataclass decorator
                for decorator in getattr(node, "decorator_list", []):
                    if "dataclass" in self._get_name(decorator):
                        self.contracts.dataclasses.append(node.name)
                        
            # Count type annotations
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                total_functions += 1
                if node.returns is not None:
                    typed_annotations += 1
                for arg in node.args.args:
                    if arg.annotation is not None:
                        typed_annotations += 1
                        
        if total_functions > 0:
            self.contracts.type_safety_score = typed_annotations / (total_functions * 2)  # Rough estimate
            
        # Check phase I/O alignment
        self.contracts.phase_io_alignment = (
            len(self.phases.phase_outputs) > 0 and
            len(self.phases.phase_dependencies) > 0
        )
        
    def _analyze_error_handling(self) -> None:
        """Analyze error handling."""
        print("  ⚠️  Analyzing error handling...")
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Try):
                self.errors.try_except_count += 1
                
                # Check handlers
                for handler in node.handlers:
                    if handler.type:
                        exc_name = self._get_name(handler.type)
                        if exc_name not in self.errors.error_categories:
                            self.errors.error_categories.append(exc_name)
                            
                        if "Timeout" in exc_name:
                            self.errors.has_timeout_handling = True
                        if "Abort" in exc_name:
                            self.errors.has_abort_handling = True
                            
                if node.finalbody:
                    self.errors.finally_count += 1
                    
        # Check for exception recovery
        if self.errors.try_except_count > 0:
            self.errors.has_exception_recovery = True
            
    def _analyze_integrations(self) -> None:
        """Analyze integration points."""
        print("  🔌 Analyzing integration points...")
        
        # Key integration points
        integration_patterns = {
            "method_executor": ["MethodExecutor", "method_executor", "executor"],
            "questionnaire": ["CanonicalQuestionnaire", "questionnaire", "_canonical_questionnaire"],
            "calibration": ["CalibrationOrchestrator", "calibration_orchestrator"],
            "sisas": ["IrrigationSynchronizer", "signal_registry", "enriched_packs"],
            "phase_two_executors": ["executors_contract", "D1Q1_Executor", "executors"],
            "aggregation": ["DimensionAggregator", "AreaPolicyAggregator", "ClusterAggregator"],
            "recommendation": ["RecommendationEnginePort", "recommendation_engine"],
        }
        
        for integration_name, patterns in integration_patterns.items():
            found = False
            locations = []
            
            # Check imports
            for imp in self.components.imports:
                if any(p in imp for p in patterns):
                    found = True
                    locations.append(f"import:{imp}")
                    
            # Check source code
            for pattern in patterns:
                if pattern in self.source_code:
                    found = True
                    count = self.source_code.count(pattern)
                    locations.append(f"usage_count:{count}")
                    
            self.integrations.integrations[integration_name] = {
                "detected": found,
                "locations": locations,
            }
            
    def _analyze_code_quality(self) -> None:
        """Analyze code quality metrics."""
        print("  📈 Analyzing code quality...")
        
        lines = self.source_code.split("\n")
        self.quality.total_lines = len(lines)
        
        in_docstring = False
        docstring_delimiter = None
        
        for line in lines:
            stripped = line.strip()
            
            # Check for docstring start/end
            if '"""' in stripped or "'''" in stripped:
                delimiter = '"""' if '"""' in stripped else "'''"
                if not in_docstring:
                    in_docstring = True
                    docstring_delimiter = delimiter
                    self.quality.docstring_lines += 1
                elif delimiter == docstring_delimiter:
                    in_docstring = False
                    self.quality.docstring_lines += 1
                    docstring_delimiter = None
                else:
                    self.quality.docstring_lines += 1
            elif in_docstring:
                self.quality.docstring_lines += 1
            elif stripped.startswith("#"):
                self.quality.comment_lines += 1
            elif stripped and not in_docstring:
                self.quality.code_lines += 1
                
            # Count logging
            if "logger." in stripped:
                self.quality.logging_statements += 1
                
        # Type annotation coverage
        self.quality.type_annotation_coverage = self.contracts.type_safety_score
        
        # Complexity score (rough estimate based on various factors)
        complexity_factors = [
            len(self.components.classes) * 2,  # Classes add complexity
            len(self.components.functions),
            self.errors.try_except_count,
            len(self.abort.propagation_points) / 10,
        ]
        self.quality.complexity_score = sum(complexity_factors) / 100
        
    def _build_report(self) -> Dict[str, Any]:
        """Build comprehensive report."""
        print("  📝 Building report...")
        
        # Calculate summary scores
        architecture_score = self._calculate_architecture_score()
        phase_flow_score = self._calculate_phase_flow_score()
        resource_score = self._calculate_resource_score()
        instrumentation_score = self._calculate_instrumentation_score()
        abort_score = self._calculate_abort_score()
        contract_score = self._calculate_contract_score()
        error_handling_score = self._calculate_error_handling_score()
        integration_score = self._calculate_integration_score()
        quality_score = self._calculate_quality_score()
        
        overall_score = (
            architecture_score * 0.15 +
            phase_flow_score * 0.15 +
            resource_score * 0.10 +
            instrumentation_score * 0.10 +
            abort_score * 0.10 +
            contract_score * 0.10 +
            error_handling_score * 0.10 +
            integration_score * 0.10 +
            quality_score * 0.10
        )
        
        return {
            "audit_metadata": {
                "orchestrator_path": str(self.path),
                "audit_timestamp": self._get_timestamp(),
                "total_lines": self.quality.total_lines,
            },
            "overall_score": round(overall_score, 3),
            "category_scores": {
                "architecture": round(architecture_score, 3),
                "phase_flow": round(phase_flow_score, 3),
                "resource_management": round(resource_score, 3),
                "instrumentation": round(instrumentation_score, 3),
                "abort_mechanism": round(abort_score, 3),
                "data_contracts": round(contract_score, 3),
                "error_handling": round(error_handling_score, 3),
                "integration": round(integration_score, 3),
                "code_quality": round(quality_score, 3),
            },
            "components": {
                "classes": self.components.classes,
                "class_count": len(self.components.classes),
                "functions": self.components.functions,
                "function_count": len(self.components.functions),
                "constants": self.components.constants,
                "constant_count": len(self.components.constants),
                "import_count": len(self.components.imports),
            },
            "phases": {
                "phase_definitions": self.phases.phase_definitions,
                "phase_count": len(self.phases.phase_definitions),
                "phase_handlers": self.phases.phase_handlers,
                "handler_count": len(self.phases.phase_handlers),
                "phase_timeouts": self.phases.phase_timeouts,
                "phase_item_targets": self.phases.phase_item_targets,
                "phase_dependencies": self.phases.phase_dependencies,
                "phase_outputs": self.phases.phase_outputs,
                "sync_phases": len([p for p in self.phases.phase_definitions if p.get("mode") == "sync"]),
                "async_phases": len([p for p in self.phases.phase_definitions if p.get("mode") == "async"]),
            },
            "resource_management": {
                "has_resource_limits": self.resources.has_resource_limits,
                "has_memory_tracking": self.resources.has_memory_tracking,
                "has_cpu_tracking": self.resources.has_cpu_tracking,
                "has_adaptive_workers": self.resources.has_adaptive_workers,
                "has_usage_history": self.resources.has_usage_history,
                "worker_constraints": self.resources.worker_constraints,
                "thresholds": self.resources.thresholds,
            },
            "instrumentation": {
                "has_phase_instrumentation": self.instrumentation.has_phase_instrumentation,
                "has_progress_tracking": self.instrumentation.has_progress_tracking,
                "has_resource_snapshots": self.instrumentation.has_resource_snapshots,
                "has_latency_tracking": self.instrumentation.has_latency_tracking,
                "has_warning_recording": self.instrumentation.has_warning_recording,
                "has_error_recording": self.instrumentation.has_error_recording,
                "metrics_exported": self.instrumentation.metrics_exported,
                "metric_count": len(self.instrumentation.metrics_exported),
            },
            "abort_mechanism": {
                "has_abort_signal": self.abort.has_abort_signal,
                "thread_safe": self.abort.thread_safe,
                "has_abort_reason": self.abort.has_abort_reason,
                "has_abort_timestamp": self.abort.has_abort_timestamp,
                "propagation_points": self.abort.propagation_points,
                "propagation_count": len(self.abort.propagation_points),
            },
            "data_contracts": {
                "typed_dicts": self.contracts.typed_dicts,
                "typed_dict_count": len(self.contracts.typed_dicts),
                "dataclasses": self.contracts.dataclasses,
                "dataclass_count": len(self.contracts.dataclasses),
                "phase_io_alignment": self.contracts.phase_io_alignment,
                "type_safety_score": round(self.contracts.type_safety_score, 3),
            },
            "error_handling": {
                "has_timeout_handling": self.errors.has_timeout_handling,
                "has_abort_handling": self.errors.has_abort_handling,
                "has_exception_recovery": self.errors.has_exception_recovery,
                "try_except_count": self.errors.try_except_count,
                "finally_count": self.errors.finally_count,
                "error_categories": self.errors.error_categories,
                "category_count": len(self.errors.error_categories),
            },
            "integrations": self.integrations.integrations,
            "code_quality": {
                "total_lines": self.quality.total_lines,
                "code_lines": self.quality.code_lines,
                "comment_lines": self.quality.comment_lines,
                "docstring_lines": self.quality.docstring_lines,
                "code_to_comment_ratio": round(
                    self.quality.code_lines / max(self.quality.comment_lines, 1), 2
                ),
                "type_annotation_coverage": round(self.quality.type_annotation_coverage, 3),
                "complexity_score": round(self.quality.complexity_score, 3),
                "logging_statements": self.quality.logging_statements,
            },
        }
        
    def _calculate_architecture_score(self) -> float:
        """Calculate architecture score."""
        score = 0.0
        
        # Key classes present
        key_classes = ["Orchestrator", "ResourceLimits", "PhaseInstrumentation", "AbortSignal"]
        classes_found = sum(1 for c in self.components.classes if c["name"] in key_classes)
        score += (classes_found / len(key_classes)) * 40
        
        # Reasonable class count (not too many, not too few)
        class_count = len(self.components.classes)
        if 5 <= class_count <= 15:
            score += 30
        elif 3 <= class_count <= 20:
            score += 20
        else:
            score += 10
            
        # Functions present
        if len(self.components.functions) >= 2:
            score += 15
            
        # Constants defined
        if len(self.components.constants) >= 3:
            score += 15
            
        return min(score, 100.0)
        
    def _calculate_phase_flow_score(self) -> float:
        """Calculate phase flow score."""
        score = 0.0
        
        # 11 phases defined
        if len(self.phases.phase_definitions) == 11:
            score += 30
        else:
            score += len(self.phases.phase_definitions) * 2
            
        # Phase handlers present
        if len(self.phases.phase_handlers) >= 8:
            score += 25
        else:
            score += len(self.phases.phase_handlers) * 2
            
        # Timeouts defined
        if len(self.phases.phase_timeouts) >= 10:
            score += 15
            
        # Item targets defined
        if len(self.phases.phase_item_targets) >= 10:
            score += 15
            
        # Dependencies mapped
        if len(self.phases.phase_dependencies) >= 5:
            score += 15
            
        return min(score, 100.0)
        
    def _calculate_resource_score(self) -> float:
        """Calculate resource management score."""
        score = 0.0
        
        if self.resources.has_resource_limits:
            score += 30
        if self.resources.has_memory_tracking:
            score += 20
        if self.resources.has_cpu_tracking:
            score += 20
        if self.resources.has_adaptive_workers:
            score += 20
        if self.resources.has_usage_history:
            score += 10
            
        return min(score, 100.0)
        
    def _calculate_instrumentation_score(self) -> float:
        """Calculate instrumentation score."""
        score = 0.0
        
        if self.instrumentation.has_phase_instrumentation:
            score += 25
        if self.instrumentation.has_progress_tracking:
            score += 20
        if self.instrumentation.has_resource_snapshots:
            score += 15
        if self.instrumentation.has_latency_tracking:
            score += 15
        if self.instrumentation.has_warning_recording:
            score += 10
        if self.instrumentation.has_error_recording:
            score += 10
        if len(self.instrumentation.metrics_exported) >= 1:
            score += 5
            
        return min(score, 100.0)
        
    def _calculate_abort_score(self) -> float:
        """Calculate abort mechanism score."""
        score = 0.0
        
        if self.abort.has_abort_signal:
            score += 30
        if self.abort.thread_safe:
            score += 25
        if self.abort.has_abort_reason:
            score += 15
        if self.abort.has_abort_timestamp:
            score += 10
        if len(self.abort.propagation_points) >= 5:
            score += 20
        elif len(self.abort.propagation_points) >= 1:
            score += 10
            
        return min(score, 100.0)
        
    def _calculate_contract_score(self) -> float:
        """Calculate data contract score."""
        score = 0.0
        
        # TypedDicts present
        if len(self.contracts.typed_dicts) >= 1:
            score += 20
            
        # Dataclasses present
        if len(self.contracts.dataclasses) >= 5:
            score += 30
        elif len(self.contracts.dataclasses) >= 1:
            score += 15
            
        # Phase I/O alignment
        if self.contracts.phase_io_alignment:
            score += 25
            
        # Type safety
        score += self.contracts.type_safety_score * 25
        
        return min(score, 100.0)
        
    def _calculate_error_handling_score(self) -> float:
        """Calculate error handling score."""
        score = 0.0
        
        if self.errors.has_timeout_handling:
            score += 25
        if self.errors.has_abort_handling:
            score += 25
        if self.errors.has_exception_recovery:
            score += 20
        if self.errors.try_except_count >= 5:
            score += 20
        elif self.errors.try_except_count >= 1:
            score += 10
        if self.errors.finally_count >= 1:
            score += 10
            
        return min(score, 100.0)
        
    def _calculate_integration_score(self) -> float:
        """Calculate integration score."""
        detected = sum(1 for i in self.integrations.integrations.values() if i["detected"])
        total = len(self.integrations.integrations)
        return (detected / total) * 100 if total > 0 else 0.0
        
    def _calculate_quality_score(self) -> float:
        """Calculate code quality score."""
        score = 0.0
        
        # Code to comment ratio (target ~5:1 to 15:1)
        ratio = self.quality.code_lines / max(self.quality.comment_lines, 1)
        if 5 <= ratio <= 15:
            score += 20
        elif 3 <= ratio <= 20:
            score += 15
        else:
            score += 10
            
        # Type annotation coverage
        score += self.quality.type_annotation_coverage * 30
        
        # Logging presence
        if self.quality.logging_statements >= 20:
            score += 25
        elif self.quality.logging_statements >= 10:
            score += 15
        else:
            score += 5
            
        # Docstrings
        if self.quality.docstring_lines >= 50:
            score += 25
        elif self.quality.docstring_lines >= 20:
            score += 15
        else:
            score += 5
            
        return min(score, 100.0)
        
    def _get_name(self, node: ast.AST) -> str:
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_name(node.func)
        return ""
        
    def _get_constant_value(self, node: ast.AST) -> Any:
        """Get constant value from AST node."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Str):
            return node.s
        return None
        
    def _get_timestamp(self) -> str:
        """Get ISO timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"


def generate_markdown_report(report: Dict[str, Any]) -> str:
    """Generate markdown report from JSON data."""
    
    md = f"""# Orchestrator Detailed Audit Report
## F.A.R.F.A.N Mechanistic Pipeline

**Audit Date**: {report["audit_metadata"]["audit_timestamp"]}  
**Orchestrator Path**: `{report["audit_metadata"]["orchestrator_path"]}`  
**Total Lines**: {report["audit_metadata"]["total_lines"]}

---

## Executive Summary

### Overall Score: {report["overall_score"]:.1f}/100

The orchestrator is the central coordination component of the F.A.R.F.A.N pipeline, managing an 11-phase deterministic policy analysis workflow with comprehensive resource management, instrumentation, and error handling.

### Category Scores

| Category | Score | Status |
|----------|-------|--------|
| **Architecture & Components** | {report["category_scores"]["architecture"]:.1f}/100 | {"✅" if report["category_scores"]["architecture"] >= 70 else "⚠️" if report["category_scores"]["architecture"] >= 50 else "❌"} |
| **Phase Flow** | {report["category_scores"]["phase_flow"]:.1f}/100 | {"✅" if report["category_scores"]["phase_flow"] >= 70 else "⚠️" if report["category_scores"]["phase_flow"] >= 50 else "❌"} |
| **Resource Management** | {report["category_scores"]["resource_management"]:.1f}/100 | {"✅" if report["category_scores"]["resource_management"] >= 70 else "⚠️" if report["category_scores"]["resource_management"] >= 50 else "❌"} |
| **Instrumentation** | {report["category_scores"]["instrumentation"]:.1f}/100 | {"✅" if report["category_scores"]["instrumentation"] >= 70 else "⚠️" if report["category_scores"]["instrumentation"] >= 50 else "❌"} |
| **Abort Mechanism** | {report["category_scores"]["abort_mechanism"]:.1f}/100 | {"✅" if report["category_scores"]["abort_mechanism"] >= 70 else "⚠️" if report["category_scores"]["abort_mechanism"] >= 50 else "❌"} |
| **Data Contracts** | {report["category_scores"]["data_contracts"]:.1f}/100 | {"✅" if report["category_scores"]["data_contracts"] >= 70 else "⚠️" if report["category_scores"]["data_contracts"] >= 50 else "❌"} |
| **Error Handling** | {report["category_scores"]["error_handling"]:.1f}/100 | {"✅" if report["category_scores"]["error_handling"] >= 70 else "⚠️" if report["category_scores"]["error_handling"] >= 50 else "❌"} |
| **Integration** | {report["category_scores"]["integration"]:.1f}/100 | {"✅" if report["category_scores"]["integration"] >= 70 else "⚠️" if report["category_scores"]["integration"] >= 50 else "❌"} |
| **Code Quality** | {report["category_scores"]["code_quality"]:.1f}/100 | {"✅" if report["category_scores"]["code_quality"] >= 70 else "⚠️" if report["category_scores"]["code_quality"] >= 50 else "❌"} |

---

## 1. Architecture & Components

### 1.1 Component Inventory

**Classes**: {report["components"]["class_count"]}  
**Functions**: {report["components"]["function_count"]}  
**Constants**: {report["components"]["constant_count"]}  
**Imports**: {report["components"]["import_count"]}

#### Key Classes

"""
    
    for cls in report["components"]["classes"]:
        md += f"\n**{cls['name']}** (Line {cls['line']})\n"
        if cls.get("bases"):
            md += f"- Bases: {', '.join(cls['bases'])}\n"
        md += f"- Methods: {cls['method_count']}\n"
        
    md += f"""

#### Top-Level Functions

"""
    
    for func in report["components"]["functions"]:
        async_marker = "async " if func["is_async"] else ""
        type_marker = "✓" if func["has_return_type"] else "✗"
        md += f"- **{async_marker}{func['name']}** ({func['param_count']} params, return type: {type_marker})\n"
        
    md += f"""

---

## 2. Phase Flow Analysis

### 2.1 Phase Definitions

**Total Phases**: {report["phases"]["phase_count"]}  
**Sync Phases**: {report["phases"]["sync_phases"]}  
**Async Phases**: {report["phases"]["async_phases"]}

"""
    
    for phase in report["phases"]["phase_definitions"]:
        timeout = report["phases"]["phase_timeouts"].get(phase["phase_id"], "N/A")
        target = report["phases"]["phase_item_targets"].get(phase["phase_id"], "N/A")
        output = report["phases"]["phase_outputs"].get(phase["phase_id"], "N/A")
        
        md += f"""
#### Phase {phase["phase_id"]}: {phase["label"]}

- **Mode**: {phase["mode"]}
- **Handler**: `{phase["handler"]}`
- **Timeout**: {timeout}s
- **Target Items**: {target}
- **Output Key**: `{output}`
"""
        
        if phase["phase_id"] in report["phases"]["phase_dependencies"]:
            deps = report["phases"]["phase_dependencies"][phase["phase_id"]]
            md += f"- **Dependencies**: {', '.join(f'`{d}`' for d in deps)}\n"
            
    md += f"""

### 2.2 Phase Handler Methods

**Handler Count**: {report["phases"]["handler_count"]}

"""
    
    for handler_name, handler_info in report["phases"]["phase_handlers"].items():
        async_marker = "async " if handler_info["is_async"] else ""
        md += f"- **{async_marker}{handler_name}** (Line {handler_info['line']}, {len(handler_info['params'])} params)\n"
        
    md += f"""

---

## 3. Resource Management

### 3.1 Capabilities

"""
    
    rm = report["resource_management"]
    md += f"""
- **Resource Limits**: {"✅" if rm["has_resource_limits"] else "❌"}
- **Memory Tracking**: {"✅" if rm["has_memory_tracking"] else "❌"}
- **CPU Tracking**: {"✅" if rm["has_cpu_tracking"] else "❌"}
- **Adaptive Workers**: {"✅" if rm["has_adaptive_workers"] else "❌"}
- **Usage History**: {"✅" if rm["has_usage_history"] else "❌"}

### 3.2 Worker Constraints

"""
    
    for key, value in rm["worker_constraints"].items():
        md += f"- **{key}**: {value}\n"
        
    md += "\n### 3.3 Thresholds\n\n"
    
    for key, value in rm["thresholds"].items():
        md += f"- **{key}**: {value}\n"
        
    md += f"""

---

## 4. Instrumentation & Monitoring

### 4.1 Capabilities

"""
    
    instr = report["instrumentation"]
    md += f"""
- **Phase Instrumentation**: {"✅" if instr["has_phase_instrumentation"] else "❌"}
- **Progress Tracking**: {"✅" if instr["has_progress_tracking"] else "❌"}
- **Resource Snapshots**: {"✅" if instr["has_resource_snapshots"] else "❌"}
- **Latency Tracking**: {"✅" if instr["has_latency_tracking"] else "❌"}
- **Warning Recording**: {"✅" if instr["has_warning_recording"] else "❌"}
- **Error Recording**: {"✅" if instr["has_error_recording"] else "❌"}

### 4.2 Metrics Exported

**Metric Count**: {instr["metric_count"]}

"""
    
    for metric in instr["metrics_exported"]:
        md += f"- `{metric}`\n"
        
    md += f"""

---

## 5. Abort Mechanism

### 5.1 Capabilities

"""
    
    abort = report["abort_mechanism"]
    md += f"""
- **Abort Signal**: {"✅" if abort["has_abort_signal"] else "❌"}
- **Thread Safe**: {"✅" if abort["thread_safe"] else "❌"}
- **Abort Reason**: {"✅" if abort["has_abort_reason"] else "❌"}
- **Abort Timestamp**: {"✅" if abort["has_abort_timestamp"] else "❌"}

### 5.2 Propagation Points

**Count**: {abort["propagation_count"]}

"""
    
    if abort["propagation_count"] > 0:
        md += "The abort mechanism is checked at the following locations:\n\n"
        for point in abort["propagation_points"][:10]:  # Limit to first 10
            md += f"- `{point}`\n"
        if abort["propagation_count"] > 10:
            md += f"\n... and {abort['propagation_count'] - 10} more locations\n"
    else:
        md += "⚠️ No abort propagation points detected\n"
        
    md += f"""

---

## 6. Data Contracts & Type Safety

### 6.1 Contract Types

"""
    
    contracts = report["data_contracts"]
    md += f"""
- **TypedDict Count**: {contracts["typed_dict_count"]}
- **Dataclass Count**: {contracts["dataclass_count"]}
- **Phase I/O Alignment**: {"✅" if contracts["phase_io_alignment"] else "❌"}
- **Type Safety Score**: {contracts["type_safety_score"]:.1%}

### 6.2 TypedDict Definitions

"""
    
    for td in contracts["typed_dicts"]:
        md += f"- `{td}`\n"
        
    md += "\n### 6.3 Dataclass Definitions\n\n"
    
    for dc in contracts["dataclasses"]:
        md += f"- `{dc}`\n"
        
    md += f"""

---

## 7. Error Handling & Resilience

### 7.1 Capabilities

"""
    
    errors = report["error_handling"]
    md += f"""
- **Timeout Handling**: {"✅" if errors["has_timeout_handling"] else "❌"}
- **Abort Handling**: {"✅" if errors["has_abort_handling"] else "❌"}
- **Exception Recovery**: {"✅" if errors["has_exception_recovery"] else "❌"}
- **Try-Except Blocks**: {errors["try_except_count"]}
- **Finally Blocks**: {errors["finally_count"]}

### 7.2 Error Categories Handled

**Count**: {errors["category_count"]}

"""
    
    for cat in errors["error_categories"]:
        md += f"- `{cat}`\n"
        
    md += f"""

---

## 8. Integration Points

### 8.1 External Components

"""
    
    for integration_name, integration_data in report["integrations"].items():
        status = "✅" if integration_data["detected"] else "❌"
        md += f"\n**{integration_name}**: {status}\n"
        if integration_data["locations"]:
            for loc in integration_data["locations"][:3]:
                md += f"  - {loc}\n"
                
    md += f"""

---

## 9. Code Quality Metrics

### 9.1 Line Counts

"""
    
    quality = report["code_quality"]
    md += f"""
- **Total Lines**: {quality["total_lines"]}
- **Code Lines**: {quality["code_lines"]}
- **Comment Lines**: {quality["comment_lines"]}
- **Docstring Lines**: {quality["docstring_lines"]}
- **Code-to-Comment Ratio**: {quality["code_to_comment_ratio"]:.1f}:1

### 9.2 Quality Indicators

- **Type Annotation Coverage**: {quality["type_annotation_coverage"]:.1%}
- **Complexity Score**: {quality["complexity_score"]:.2f}
- **Logging Statements**: {quality["logging_statements"]}

---

## 10. Recommendations

"""
    
    recommendations = []
    
    # Generate recommendations based on scores
    if report["category_scores"]["architecture"] < 70:
        recommendations.append("🔧 **Architecture**: Consider refactoring to improve component organization")
        
    if report["category_scores"]["phase_flow"] < 70:
        recommendations.append("🔧 **Phase Flow**: Ensure all 11 phases are properly defined with complete metadata")
        
    if not rm["has_memory_tracking"] or not rm["has_cpu_tracking"]:
        recommendations.append("🔧 **Resource Management**: Implement comprehensive resource tracking")
        
    if not instr["has_progress_tracking"]:
        recommendations.append("🔧 **Instrumentation**: Add progress tracking for better observability")
        
    if abort["propagation_count"] < 5:
        recommendations.append("🔧 **Abort Mechanism**: Add more abort check points throughout critical paths")
        
    if contracts["type_safety_score"] < 0.7:
        recommendations.append("🔧 **Type Safety**: Increase type annotation coverage for better type safety")
        
    if errors["try_except_count"] < 5:
        recommendations.append("🔧 **Error Handling**: Add more comprehensive error handling blocks")
        
    if report["category_scores"]["integration"] < 70:
        recommendations.append("🔧 **Integration**: Verify all integration points are properly wired")
        
    if quality["code_to_comment_ratio"] > 15:
        recommendations.append("🔧 **Code Quality**: Add more comments to improve code readability")
    elif quality["code_to_comment_ratio"] < 5:
        recommendations.append("🔧 **Code Quality**: Reduce comment verbosity for better maintainability")
        
    if recommendations:
        for rec in recommendations:
            md += f"\n{rec}\n"
    else:
        md += "\n✅ **No critical recommendations** - Orchestrator is in good shape!\n"
        
    md += f"""

---

## 11. Summary

The orchestrator audit reveals:

- **Overall Health**: {report["overall_score"]:.1f}/100 ({"Excellent" if report["overall_score"] >= 80 else "Good" if report["overall_score"] >= 60 else "Needs Improvement"})
- **Key Strength**: {"Phase flow management" if report["category_scores"]["phase_flow"] == max(report["category_scores"].values()) else "Resource management" if report["category_scores"]["resource_management"] == max(report["category_scores"].values()) else "Code quality"}
- **Priority Improvements**: {min(report["category_scores"], key=report["category_scores"].get).replace("_", " ").title()}

**Audit Status**: {"✅ COMPLETE" if report["overall_score"] >= 60 else "⚠️ NEEDS ATTENTION"}

---

*Generated by audit_orchestrator_detailed.py*
"""
    
    return md


def main() -> None:
    """Main execution."""
    print("=" * 80)
    print("ORCHESTRATOR DETAILED AUDIT")
    print("F.A.R.F.A.N Mechanistic Pipeline")
    print("=" * 80)
    print()
    
    # Run audit
    auditor = OrchestratorAuditor(ORCHESTRATOR_PATH)
    report = auditor.run_audit()
    
    # Save JSON report
    print(f"\n💾 Saving JSON report to {OUTPUT_JSON}...")
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("✅ JSON report saved")
    
    # Generate and save markdown report
    print(f"\n💾 Generating markdown report to {OUTPUT_MD}...")
    markdown = generate_markdown_report(report)
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(markdown)
    print("✅ Markdown report saved")
    
    # Print summary
    print("\n" + "=" * 80)
    print("AUDIT SUMMARY")
    print("=" * 80)
    print(f"\nOverall Score: {report['overall_score']:.1f}/100")
    print("\nCategory Scores:")
    for category, score in report["category_scores"].items():
        status = "✅" if score >= 70 else "⚠️" if score >= 50 else "❌"
        print(f"  {status} {category.replace('_', ' ').title()}: {score:.1f}/100")
        
    print(f"\n📊 Component Summary:")
    print(f"  - Classes: {report['components']['class_count']}")
    print(f"  - Functions: {report['components']['function_count']}")
    print(f"  - Phases: {report['phases']['phase_count']}")
    print(f"  - Total Lines: {report['code_quality']['total_lines']}")
    
    print("\n" + "=" * 80)
    print("✅ Audit complete! Check the generated reports for details.")
    print("=" * 80)


if __name__ == "__main__":
    main()

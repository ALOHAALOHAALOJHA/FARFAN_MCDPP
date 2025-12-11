"""
Comprehensive System Audit for Calibration and Parametrization Implementation.

This tool conducts exhaustive verification of the COHORT_2024 calibration system by:
1. Scanning COHORT_2024 production files to verify actual implementation
2. Generating canonical method inventory with calibration status
3. Generating parametrized method inventory 
4. Creating calibration completeness matrix (which methods have which layers)
5. Producing verification report identifying gaps
6. Scanning for hardcoded calibration parameters using AST analysis
7. Generating compliance report with file:line citations
"""

import ast
import json
import logging
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Tuple
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MethodCalibrationStatus:
    """Calibration status for a single method."""
    method_id: str
    has_intrinsic_score: bool
    intrinsic_score: Optional[float]
    calibration_status: str
    layers_claimed: Set[str] = field(default_factory=set)
    layers_computed: Dict[str, bool] = field(default_factory=dict)
    layer_evidence: Dict[str, List[str]] = field(default_factory=dict)
    layer_assignment: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class LayerEvaluatorStatus:
    """Status of a layer evaluator implementation."""
    layer_name: str
    layer_symbol: str
    file_path: str
    exists: bool
    has_compute_method: bool
    compute_method_name: Optional[str] = None
    is_stub: bool = False
    evidence: List[str] = field(default_factory=list)
    implementation_details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParameterViolation:
    """Hardcoded parameter violation."""
    file_path: str
    line_number: int
    parameter_name: str
    parameter_value: Any
    context: str
    violation_type: str
    severity: str


@dataclass
class AuditResult:
    """Complete audit results."""
    timestamp: str
    canonical_method_inventory: List[Dict[str, Any]]
    parametrized_method_inventory: List[Dict[str, Any]]
    calibration_completeness_matrix: Dict[str, Dict[str, bool]]
    layer_evaluator_status: List[Dict[str, Any]]
    missing_evaluators: List[str]
    incomplete_configurations: List[Dict[str, Any]]
    stub_implementations: List[Dict[str, Any]]
    parameter_violations: List[Dict[str, Any]]
    compliance_summary: Dict[str, Any]
    verification_report: Dict[str, Any]


class ComprehensiveCalibrationAuditor:
    """Conducts comprehensive audit of calibration implementation."""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.calibration_dir = self.base_path / "src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration"
        self.parametrization_dir = self.base_path / "src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/parametrization"
        
        self.intrinsic_json_path = self.calibration_dir / "COHORT_2024_intrinsic_calibration.json"
        self.canonical_inventory_path = self.calibration_dir / "COHORT_2024_canonical_method_inventory.json"
        self.layer_requirements_path = self.calibration_dir / "COHORT_2024_layer_requirements.json"
        self.method_compatibility_path = self.calibration_dir / "COHORT_2024_method_compatibility.json"
        self.executor_config_path = self.parametrization_dir / "COHORT_2024_executor_config.json"
        
        self.layer_definitions = {
            "@b": {"name": "Base Layer", "file": "COHORT_2024_intrinsic_scoring.py", "compute_method": "compute_base_layer"},
            "@chain": {"name": "Chain Layer", "file": "COHORT_2024_chain_layer.py", "compute_method": "evaluate_chain_score"},
            "@q": {"name": "Question Layer", "file": "COHORT_2024_question_layer.py", "compute_method": "evaluate_question_score"},
            "@d": {"name": "Dimension Layer", "file": "COHORT_2024_dimension_layer.py", "compute_method": "evaluate_dimension_score"},
            "@p": {"name": "Policy Layer", "file": "COHORT_2024_policy_layer.py", "compute_method": "evaluate_policy_score"},
            "@C": {"name": "Congruence Layer", "file": "COHORT_2024_congruence_layer.py", "compute_method": "evaluate_congruence"},
            "@u": {"name": "Unit Layer", "file": "COHORT_2024_unit_layer.py", "compute_method": "evaluate_unit_score"},
            "@m": {"name": "Meta Layer", "file": "COHORT_2024_meta_layer.py", "compute_method": "evaluate_meta_score"}
        }
        
        self.methods_data: Dict[str, MethodCalibrationStatus] = {}
        self.layer_evaluators: Dict[str, LayerEvaluatorStatus] = {}
        self.parameter_violations: List[ParameterViolation] = []
    
    def load_intrinsic_calibration(self) -> Dict[str, Any]:
        """Load intrinsic calibration data."""
        logger.info(f"Loading intrinsic calibration from {self.intrinsic_json_path}")
        
        if not self.intrinsic_json_path.exists():
            logger.error(f"Intrinsic calibration file not found: {self.intrinsic_json_path}")
            return {}
        
        with open(self.intrinsic_json_path, 'r') as f:
            return json.load(f)
    
    def load_canonical_inventory(self) -> Dict[str, Any]:
        """Load canonical method inventory."""
        logger.info(f"Loading canonical inventory from {self.canonical_inventory_path}")
        
        if not self.canonical_inventory_path.exists():
            logger.warning(f"Canonical inventory not found: {self.canonical_inventory_path}")
            return {}
        
        with open(self.canonical_inventory_path, 'r') as f:
            return json.load(f)
    
    def scan_layer_evaluator(self, layer_symbol: str, layer_def: Dict[str, str]) -> LayerEvaluatorStatus:
        """Scan a layer evaluator file to verify implementation."""
        file_path = self.calibration_dir / layer_def["file"]
        
        status = LayerEvaluatorStatus(
            layer_name=layer_def["name"],
            layer_symbol=layer_symbol,
            file_path=str(file_path),
            exists=file_path.exists(),
            has_compute_method=False
        )
        
        if not status.exists:
            logger.warning(f"Layer evaluator file not found: {file_path}")
            return status
        
        try:
            content = file_path.read_text()
            tree = ast.parse(content)
            
            compute_methods_found = []
            classes_found = []
            functions_found = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes_found.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    functions_found.append(node.name)
                    
                    if layer_def["compute_method"] in node.name or "evaluate" in node.name or "compute" in node.name:
                        compute_methods_found.append(node.name)
                        
                        body_lines = ast.unparse(node).split('\n')
                        is_stub = self._is_stub_implementation(body_lines)
                        
                        status.has_compute_method = True
                        status.compute_method_name = node.name
                        status.is_stub = is_stub
                        status.evidence.append(f"Found compute method: {node.name} at line {node.lineno}")
                        
                        if is_stub:
                            status.evidence.append(f"WARNING: {node.name} appears to be a stub implementation")
            
            status.implementation_details = {
                "classes": classes_found,
                "functions": functions_found,
                "compute_methods": compute_methods_found,
                "total_lines": len(content.split('\n')),
                "has_docstring": content.find('"""') != -1
            }
            
            if not status.has_compute_method:
                status.evidence.append(f"WARNING: No compute method found matching pattern: {layer_def['compute_method']}")
        
        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")
            status.evidence.append(f"ERROR: Failed to parse file: {str(e)}")
        
        return status
    
    def _is_stub_implementation(self, body_lines: List[str]) -> bool:
        """Check if a method is a stub implementation."""
        body_text = '\n'.join(body_lines)
        
        stub_indicators = [
            "raise NotImplementedError",
            "pass",
            "return 0.5",
            "return None",
            "TODO",
            "STUB",
            "PLACEHOLDER"
        ]
        
        return any(indicator in body_text for indicator in stub_indicators)
    
    def verify_layer_implementations(self) -> None:
        """Verify all 8 layer evaluators are properly implemented."""
        logger.info("Verifying layer evaluator implementations...")
        
        for layer_symbol, layer_def in self.layer_definitions.items():
            status = self.scan_layer_evaluator(layer_symbol, layer_def)
            self.layer_evaluators[layer_symbol] = status
            
            if not status.exists:
                logger.error(f"MISSING: {layer_symbol} evaluator file not found")
            elif not status.has_compute_method:
                logger.error(f"INCOMPLETE: {layer_symbol} evaluator missing compute method")
            elif status.is_stub:
                logger.warning(f"STUB: {layer_symbol} evaluator has stub implementation")
            else:
                logger.info(f"OK: {layer_symbol} evaluator properly implemented")
    
    def build_canonical_method_inventory(self) -> List[Dict[str, Any]]:
        """Build canonical inventory of all methods with calibration status."""
        logger.info("Building canonical method inventory...")
        
        intrinsic_data = self.load_intrinsic_calibration()
        inventory = []
        
        for method_id, method_data in intrinsic_data.items():
            if method_id.startswith("_"):
                continue
            
            status = MethodCalibrationStatus(
                method_id=method_id,
                has_intrinsic_score=method_data.get("calibration_status") == "computed",
                intrinsic_score=method_data.get("intrinsic_score"),
                calibration_status=method_data.get("calibration_status", "unknown"),
                layer_assignment=method_data.get("layer", "unknown")
            )
            
            self.methods_data[method_id] = status
            
            inventory.append({
                "method_id": method_id,
                "has_intrinsic_score": status.has_intrinsic_score,
                "intrinsic_score": status.intrinsic_score,
                "calibration_status": status.calibration_status,
                "layer_assignment": status.layer_assignment,
                "b_theory": method_data.get("b_theory_computation", {}).get("final_score"),
                "b_impl": method_data.get("b_impl_computation", {}).get("final_score"),
                "b_deploy": method_data.get("b_deploy_computation", {}).get("final_score"),
                "layers_required": self._get_required_layers_for_role(status.layer_assignment)
            })
        
        logger.info(f"Built inventory with {len(inventory)} methods")
        return sorted(inventory, key=lambda x: x["method_id"])
    
    def _get_required_layers_for_role(self, role: str) -> List[str]:
        """Determine required layers based on role."""
        role_layer_map = {
            "INGEST_PDM": ["@b", "@chain", "@u", "@m"],
            "STRUCTURE": ["@b", "@chain", "@u", "@m"],
            "EXTRACT": ["@b", "@chain", "@u", "@m"],
            "SCORE_Q": ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"],
            "AGGREGATE": ["@b", "@chain", "@d", "@p", "@C", "@m"],
            "REPORT": ["@b", "@chain", "@C", "@m"],
            "META_TOOL": ["@b", "@chain", "@m"],
            "TRANSFORM": ["@b", "@chain", "@m"],
            "unknown": ["@b"]
        }
        
        return role_layer_map.get(role, ["@b"])
    
    def build_parametrized_method_inventory(self) -> List[Dict[str, Any]]:
        """Build inventory of methods with parametrization status."""
        logger.info("Building parametrized method inventory...")
        
        inventory = []
        
        if self.executor_config_path.exists():
            with open(self.executor_config_path, 'r') as f:
                executor_config = json.load(f)
            
            for executor_id, config in executor_config.items():
                if executor_id.startswith("_"):
                    continue
                
                inventory.append({
                    "executor_id": executor_id,
                    "has_config": True,
                    "parameters_externalized": bool(config),
                    "parameter_count": len(config) if isinstance(config, dict) else 0,
                    "parameters": list(config.keys()) if isinstance(config, dict) else []
                })
        
        logger.info(f"Built parametrization inventory with {len(inventory)} executors")
        return sorted(inventory, key=lambda x: x["executor_id"])
    
    def build_calibration_completeness_matrix(self) -> Dict[str, Dict[str, bool]]:
        """Build matrix showing which methods have which layers computed."""
        logger.info("Building calibration completeness matrix...")
        
        matrix = {}
        
        for method_id, status in self.methods_data.items():
            method_matrix = {
                "@b": status.has_intrinsic_score,
                "@chain": False,
                "@q": False,
                "@d": False,
                "@p": False,
                "@C": False,
                "@u": False,
                "@m": False
            }
            
            matrix[method_id] = method_matrix
        
        logger.info(f"Built completeness matrix for {len(matrix)} methods")
        return matrix
    
    def scan_hardcoded_parameters(self) -> List[ParameterViolation]:
        """Scan Python source files for hardcoded calibration parameters using AST."""
        logger.info("Scanning for hardcoded calibration parameters...")
        
        violations = []
        
        src_dir = self.base_path / "src"
        if not src_dir.exists():
            logger.warning(f"Source directory not found: {src_dir}")
            return violations
        
        for py_file in src_dir.rglob("*.py"):
            if "venv" in str(py_file) or ".venv" in str(py_file):
                continue
            
            try:
                content = py_file.read_text()
                tree = ast.parse(content)
                
                violations.extend(self._scan_ast_for_parameters(py_file, tree, content))
            
            except Exception as e:
                logger.debug(f"Could not parse {py_file}: {e}")
        
        logger.info(f"Found {len(violations)} potential parameter violations")
        return violations
    
    def _scan_ast_for_parameters(self, file_path: Path, tree: ast.AST, content: str) -> List[ParameterViolation]:
        """Scan AST for hardcoded parameters."""
        violations = []
        lines = content.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id.lower()
                        
                        if any(keyword in var_name for keyword in [
                            "threshold", "weight", "alpha", "beta", "gamma", 
                            "scale", "factor", "coeff", "param", "calibration"
                        ]):
                            if isinstance(node.value, ast.Constant):
                                if isinstance(node.value.value, (int, float)):
                                    context = lines[node.lineno - 1] if node.lineno <= len(lines) else ""
                                    
                                    violations.append(ParameterViolation(
                                        file_path=str(file_path.relative_to(self.base_path)),
                                        line_number=node.lineno,
                                        parameter_name=target.id,
                                        parameter_value=node.value.value,
                                        context=context.strip(),
                                        violation_type="hardcoded_numeric",
                                        severity="medium"
                                    ))
        
        return violations
    
    def generate_verification_report(self) -> Dict[str, Any]:
        """Generate comprehensive verification report identifying gaps."""
        logger.info("Generating verification report...")
        
        missing_evaluators = []
        incomplete_configurations = []
        stub_implementations = []
        
        for layer_symbol, evaluator_status in self.layer_evaluators.items():
            if not evaluator_status.exists:
                missing_evaluators.append({
                    "layer": layer_symbol,
                    "name": evaluator_status.layer_name,
                    "expected_file": evaluator_status.file_path,
                    "issue": "File does not exist"
                })
            elif not evaluator_status.has_compute_method:
                incomplete_configurations.append({
                    "layer": layer_symbol,
                    "name": evaluator_status.layer_name,
                    "file": evaluator_status.file_path,
                    "issue": "Missing compute method",
                    "details": evaluator_status.implementation_details
                })
            elif evaluator_status.is_stub:
                stub_implementations.append({
                    "layer": layer_symbol,
                    "name": evaluator_status.layer_name,
                    "file": evaluator_status.file_path,
                    "compute_method": evaluator_status.compute_method_name,
                    "issue": "Stub implementation without production logic",
                    "evidence": evaluator_status.evidence
                })
        
        total_methods = len(self.methods_data)
        methods_with_intrinsic = sum(1 for m in self.methods_data.values() if m.has_intrinsic_score)
        
        report = {
            "audit_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_methods": total_methods,
                "methods_with_intrinsic_calibration": methods_with_intrinsic,
                "methods_without_calibration": total_methods - methods_with_intrinsic,
                "total_layers": len(self.layer_definitions),
                "layers_implemented": sum(1 for e in self.layer_evaluators.values() if e.exists and e.has_compute_method and not e.is_stub),
                "layers_missing": len(missing_evaluators),
                "layers_incomplete": len(incomplete_configurations),
                "layers_stub": len(stub_implementations),
                "hardcoded_parameters_found": len(self.parameter_violations)
            },
            "missing_evaluators": missing_evaluators,
            "incomplete_configurations": incomplete_configurations,
            "stub_implementations": stub_implementations,
            "layer_status_detail": {
                layer: {
                    "exists": status.exists,
                    "has_compute_method": status.has_compute_method,
                    "is_stub": status.is_stub,
                    "file": status.file_path,
                    "evidence": status.evidence
                }
                for layer, status in self.layer_evaluators.items()
            },
            "critical_gaps": []
        }
        
        if missing_evaluators:
            report["critical_gaps"].append({
                "category": "Missing Layer Evaluators",
                "severity": "critical",
                "count": len(missing_evaluators),
                "details": missing_evaluators
            })
        
        if stub_implementations:
            report["critical_gaps"].append({
                "category": "Stub Implementations",
                "severity": "high",
                "count": len(stub_implementations),
                "details": stub_implementations
            })
        
        if incomplete_configurations:
            report["critical_gaps"].append({
                "category": "Incomplete Configurations",
                "severity": "high",
                "count": len(incomplete_configurations),
                "details": incomplete_configurations
            })
        
        return report
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance report with file:line citations."""
        logger.info("Generating compliance report...")
        
        violations_by_file = {}
        for violation in self.parameter_violations:
            if violation.file_path not in violations_by_file:
                violations_by_file[violation.file_path] = []
            violations_by_file[violation.file_path].append(asdict(violation))
        
        report = {
            "audit_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_violations": len(self.parameter_violations),
                "files_with_violations": len(violations_by_file),
                "severity_breakdown": {
                    "critical": sum(1 for v in self.parameter_violations if v.severity == "critical"),
                    "high": sum(1 for v in self.parameter_violations if v.severity == "high"),
                    "medium": sum(1 for v in self.parameter_violations if v.severity == "medium"),
                    "low": sum(1 for v in self.parameter_violations if v.severity == "low")
                }
            },
            "violations_by_file": violations_by_file,
            "all_violations": [asdict(v) for v in self.parameter_violations],
            "migration_status": {
                "files_fully_migrated": 0,
                "files_partially_migrated": len(violations_by_file),
                "files_not_migrated": 0
            }
        }
        
        return report
    
    def run_comprehensive_audit(self) -> AuditResult:
        """Run complete comprehensive audit."""
        logger.info("=" * 80)
        logger.info("COMPREHENSIVE CALIBRATION SYSTEM AUDIT")
        logger.info("=" * 80)
        
        self.verify_layer_implementations()
        
        canonical_inventory = self.build_canonical_method_inventory()
        
        parametrized_inventory = self.build_parametrized_method_inventory()
        
        completeness_matrix = self.build_calibration_completeness_matrix()
        
        verification_report = self.generate_verification_report()
        
        self.parameter_violations = self.scan_hardcoded_parameters()
        
        compliance_report = self.generate_compliance_report()
        
        missing_evaluators = [
            evaluator.layer_symbol 
            for evaluator in self.layer_evaluators.values() 
            if not evaluator.exists
        ]
        
        incomplete_configurations = [
            {
                "layer": evaluator.layer_symbol,
                "issue": "Missing compute method"
            }
            for evaluator in self.layer_evaluators.values()
            if evaluator.exists and not evaluator.has_compute_method
        ]
        
        stub_implementations = [
            {
                "layer": evaluator.layer_symbol,
                "file": evaluator.file_path,
                "method": evaluator.compute_method_name
            }
            for evaluator in self.layer_evaluators.values()
            if evaluator.exists and evaluator.has_compute_method and evaluator.is_stub
        ]
        
        result = AuditResult(
            timestamp=datetime.now().isoformat(),
            canonical_method_inventory=canonical_inventory,
            parametrized_method_inventory=parametrized_inventory,
            calibration_completeness_matrix=completeness_matrix,
            layer_evaluator_status=[asdict(e) for e in self.layer_evaluators.values()],
            missing_evaluators=missing_evaluators,
            incomplete_configurations=incomplete_configurations,
            stub_implementations=stub_implementations,
            parameter_violations=[asdict(v) for v in self.parameter_violations],
            compliance_summary=compliance_report,
            verification_report=verification_report
        )
        
        logger.info("=" * 80)
        logger.info("AUDIT COMPLETE")
        logger.info("=" * 80)
        
        return result
    
    def save_audit_results(self, result: AuditResult, output_dir: str = "artifacts/audit_reports") -> None:
        """Save audit results to files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        with open(output_path / f"canonical_method_inventory_{timestamp}.json", 'w') as f:
            json.dump(result.canonical_method_inventory, f, indent=2)
        
        with open(output_path / f"parametrized_method_inventory_{timestamp}.json", 'w') as f:
            json.dump(result.parametrized_method_inventory, f, indent=2)
        
        with open(output_path / f"calibration_completeness_matrix_{timestamp}.json", 'w') as f:
            json.dump(result.calibration_completeness_matrix, f, indent=2)
        
        with open(output_path / f"verification_report_{timestamp}.json", 'w') as f:
            json.dump(result.verification_report, f, indent=2)
        
        with open(output_path / f"compliance_report_{timestamp}.json", 'w') as f:
            json.dump(result.compliance_summary, f, indent=2)
        
        with open(output_path / f"complete_audit_{timestamp}.json", 'w') as f:
            json.dump(asdict(result), f, indent=2, default=lambda x: list(x) if isinstance(x, set) else str(x))
        
        logger.info(f"Audit results saved to {output_path}")


def main():
    """Main entry point."""
    auditor = ComprehensiveCalibrationAuditor()
    
    result = auditor.run_comprehensive_audit()
    
    auditor.save_audit_results(result)
    
    print("\n" + "=" * 80)
    print("AUDIT SUMMARY")
    print("=" * 80)
    print(f"Total Methods: {len(result.canonical_method_inventory)}")
    print(f"Methods with Intrinsic Calibration: {result.verification_report['summary']['methods_with_intrinsic_calibration']}")
    print(f"Layers Fully Implemented: {result.verification_report['summary']['layers_implemented']}/{result.verification_report['summary']['total_layers']}")
    print(f"Missing Evaluators: {len(result.missing_evaluators)}")
    print(f"Stub Implementations: {len(result.stub_implementations)}")
    print(f"Hardcoded Parameter Violations: {len(result.parameter_violations)}")
    print("=" * 80)
    
    if result.missing_evaluators:
        print("\n🔴 MISSING EVALUATORS:")
        for layer in result.missing_evaluators:
            print(f"  - {layer}")
    
    if result.stub_implementations:
        print("\n⚠️  STUB IMPLEMENTATIONS:")
        for stub in result.stub_implementations:
            print(f"  - {stub['layer']}: {stub['file']}")
    
    if result.parameter_violations:
        print(f"\n⚠️  PARAMETER VIOLATIONS: {len(result.parameter_violations)} found")
        print("   See compliance_report for details")
    
    print(f"\n✅ Complete audit results saved to artifacts/audit_reports/")
    print("=" * 80)


if __name__ == "__main__":
    main()
